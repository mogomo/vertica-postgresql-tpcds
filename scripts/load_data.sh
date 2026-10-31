#!/usr/bin/env bash
# Step "load": bulk load the flat files ($LOAD_JOBS tables at a time, db_copy_table
# of the product), check the row counts against the files, build the product's
# indexes (db_build_indexes; PostgreSQL only), then collect optimizer statistics.
# load.csv records per table: rows, load time, flat file bytes and bytes stored in
# the database (index_bytes: the part of it that is indexes), so the compression
# can be compared per table.
# KEEP_DATA=no deletes the files of each table as soon as it is loaded and its row
# count matches, so flat files and database storage never both hold the whole data set.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

mkdir -p "$STATE_DIR"
LOAD_CSV="$STATE_DIR/load.csv"

load_table() {   # prints: table,rows,seconds,status,file_rows,file_bytes
    local t=$1 files t0 t1 rows file_rows file_bytes
    mapfile -t files < <(files_of "$t")
    (( ${#files[@]} > 0 )) || { echo "$t,0,0,missing,0,0"; return 1; }
    file_bytes=$(stat -c %s "${files[@]}" | awk '{ s += $1 } END { printf "%d", s }')
    t0=$(now)
    rows=$(db_copy_table "$t" "${files[@]}") || { echo "$t,0,0,error,0,$file_bytes"; return 1; }
    t1=$(now)
    file_rows=$(cat "${files[@]}" | wc -l)
    echo "$t,$rows,$(elapsed "$t0" "$t1"),ok,$file_rows,$file_bytes"
    [[ "$KEEP_DATA" == no && "$rows" == "$file_rows" ]] && rm -f "${files[@]}"
    return 0
}

[[ -n "$(files_of store_sales)" ]] || die "no data in $DATA_DIR, run: ./tpcds.sh gen"

log "loading SF$SCALE from $DATA_DIR into $SCHEMA ($LOAD_JOBS tables at a time)"
tmp=$(mktemp -d)
t0=$(now)
running=0
for t in "${TABLES[@]}"; do
    load_table "$t" > "$tmp/$t.csv" &
    if (( ++running >= LOAD_JOBS )); then wait -n || true; (( running-- )); fi
done
wait || true
t1=$(now)
load_secs=$(elapsed "$t0" "$t1")

log "building indexes"
t5=$(now)
db_build_indexes
index_secs=$(elapsed "$t5" "$(now)")

log "collecting statistics"
t2=$(now)
db_collect_statistics
t3=$(now)
stats_secs=$(elapsed "$t2" "$t3")

t4=$(now)
db_wait_background
settle_secs=$(elapsed "$t4" "$(now)")

# row counts: load result vs lines in the files; bytes: flat files vs database storage
db_stored_bytes > "$tmp/stored.csv" || true
echo "table,rows,seconds,status,file_rows,file_bytes,stored_bytes,index_bytes" > "$LOAD_CSV"
failed=0
for t in "${TABLES[@]}"; do
    IFS=, read -r _ rows secs status file_rows file_bytes < "$tmp/$t.csv"
    if [[ "$status" != ok || "$rows" != "$file_rows" ]]; then
        failed=1; log "$t: status=$status rows=$rows, file rows=$file_rows"
    fi
    stored=; index=
    IFS=, read -r stored index < <(awk -F, -v t="$t" '$1 == t { print $2 "," $3 }' "$tmp/stored.csv") || true
    echo "$t,$rows,$secs,$status,$file_rows,$file_bytes,${stored:-0},${index:-0}" >> "$LOAD_CSV"
done
bytes=$(awk -F, 'NR > 1 { s += $7 } END { printf "%d", s }' "$LOAD_CSV")
index_bytes=$(awk -F, 'NR > 1 { s += $8 } END { printf "%d", s }' "$LOAD_CSV")
rm -rf "$tmp"
(( failed == 0 )) || die "load failed, see $LOAD_CSV and the errors above"

printf 'scale=%s\nload_seconds=%s\nindex_seconds=%s\nstats_seconds=%s\nsettle_seconds=%s\nload_jobs=%s\nstorage_bytes=%s\nindex_bytes=%s\n' \
    "$SCALE" "$load_secs" "$index_secs" "$stats_secs" "$settle_secs" "$LOAD_JOBS" "$bytes" "$index_bytes" > "$STATE_DIR/load.info"
[[ -f "$DATA_DIR/generate.info" ]] && cp "$DATA_DIR/generate.info" "$STATE_DIR/"
log "loaded all tables in ${load_secs}s, indexes in ${index_secs}s, statistics in ${stats_secs}s," \
    "$(awk -v b="$bytes" 'BEGIN { printf "%.2f GB", b / 1e9 }') in $PRODUCT_NAME storage"

[[ "$KEEP_DATA" == no ]] && log "KEEP_DATA=no: flat files in $DATA_DIR removed after the load of each table"
exit 0
