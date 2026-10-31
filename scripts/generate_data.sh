#!/usr/bin/env bash
# Step "gen": generate the flat files with dsdgen, $JOBS chunks in parallel.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

DSDGEN="$KIT_DIR/tools/dsdgen"
[[ -x "$DSDGEN" ]] || die "dsdgen not built yet, run: ./tpcds.sh build"

mkdir -p "$DATA_DIR"
need_gb=$(awk -v s="$SCALE" 'BEGIN { printf "%d", s * 1.1 + 1 }')
free_gb=$(df -P -BG "$DATA_DIR" | awk 'NR == 2 { sub("G", "", $4); print $4 }')
(( free_gb >= need_gb )) || die "need ~${need_gb} GB free in $DATA_DIR, only ${free_gb} GB available"

rm -f "$DATA_DIR"/*.dat
log "generating SF$SCALE into $DATA_DIR with $JOBS parallel chunks"
t0=$(now)
# dsdgen reads tpcds.idx from its working directory
cd "$KIT_DIR/tools"
common_args=(-SCALE "$SCALE" -DIR "$DATA_DIR" -TERMINATE N -FORCE Y -QUIET Y)
if (( JOBS > 1 )); then
    pids=()
    for (( child = 1; child <= JOBS; child++ )); do
        "$DSDGEN" "${common_args[@]}" -PARALLEL "$JOBS" -CHILD "$child" &
        pids+=($!)
    done
    for p in "${pids[@]}"; do wait "$p" || die "dsdgen child failed"; done
else
    "$DSDGEN" "${common_args[@]}"
fi
t1=$(now)

rm -f "$DATA_DIR"/dbgen_version*.dat
size=$(du -sb "$DATA_DIR" | cut -f1)
secs=$(elapsed "$t0" "$t1")
log "generated $(awk -v b="$size" 'BEGIN { printf "%.2f GB", b / 1e9 }') in ${secs}s"
printf 'scale=%s\njobs=%s\nseconds=%s\nbytes=%s\n' "$SCALE" "$JOBS" "$secs" "$size" > "$DATA_DIR/generate.info"
