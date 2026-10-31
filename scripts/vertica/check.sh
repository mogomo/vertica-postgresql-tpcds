#!/usr/bin/env bash
# Step "check" (Vertica): test the projection design of scale factor $SCALE on the design
# sample before the big load. Loads the sample (see make_sample in common.sh) into
# schema ${SCHEMA}_check with the designed projections, runs the 99 queries
# $CHECK_ITERATIONS times with the benchmark's resource pool settings and reports:
#  - queries that fail,
#  - projections no query read (they only cost load time and disk),
#  - optimizer and execution events of the queries (missing statistics, spills, ...),
#  - projections Database Designer would still add (incremental design on the same
#    sample); when there are any, they are created and the queries run again, so
#    the report shows what they change per query,
#  - the Vertica storage of the design, extrapolated to the full scale factor, and
#    the disk space left at the fullest point of "schema gen load".
# Report: work/state/check_sf<SCALE>/check.md. The sample holds 1/N of the fact
# tables, so timings and spills are not those of the full scale factor; query plans
# and the choice of projections mostly are.
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

DESIGN_FILE=$(design_file)
design_is_current || die "no design for SF$SCALE for this node count and Vertica version" \
    "($(basename "$DESIGN_FILE")); run: ./tpcds.sh design"

CHECK_ITERATIONS=${CHECK_ITERATIONS:-2}
CHECK_SCHEMA="${SCHEMA}_check"
WORK="$WORK_DIR/state/check_sf$SCALE"
SAMPLE_DIR="$WORK_DIR/data/sample_sf$SCALE"
REPORT="$WORK/check.md"
# tables that dsdgen splits across the chunks (all others are complete in the sample)
FACT_TABLES="store_sales store_returns catalog_sales catalog_returns web_sales web_returns inventory"
facts=$(printf "'%s'," $FACT_TABLES); facts=${facts%,}
rm -rf "$WORK"
mkdir -p "$WORK"
chmod 755 "$WORK"   # Database Designer (server process) writes its output here

log "check of $(basename "$DESIGN_FILE"): sample for SF$SCALE into schema $CHECK_SCHEMA"
chunks=$(make_sample "$SAMPLE_DIR")
check_env=(SCHEMA="$CHECK_SCHEMA" PROJECTIONS=designed KEEP_DATA=no DATA_DIR="$SAMPLE_DIR"
           WORK_DIR="$WORK_DIR" STATE_DIR_OVERRIDE="$WORK/load")
env "${check_env[@]}" "$PRODUCT_DIR/schema.sh"
env "${check_env[@]}" "$REPO_DIR/scripts/load_data.sh"
rm -rf "$SAMPLE_DIR"
"$REPO_DIR/scripts/generate_queries.sh"

run_queries() {   # $1 = label; prints "<results folder>|<start>|<end>" (database time)
    local t0 t1
    t0=$(vsql_value "select statement_timestamp()")
    env "${check_env[@]}" ITERATIONS="$CHECK_ITERATIONS" RUN_LABEL="$1" RESULTS_DIR="$WORK/results" \
        "$REPO_DIR/scripts/run_queries.sh" >&2
    t1=$(vsql_value "select statement_timestamp()")
    echo "$(ls -d "$WORK"/results/*_"$1" | tail -1)|$t0|$t1"
}
IFS='|' read -r run_dir t0 t1 <<< "$(run_queries check)"
window="between '$t0' and '$t1'"

log "incremental Database Designer run on $CHECK_SCHEMA"
tables=$(printf "$CHECK_SCHEMA.%s\n" "${TABLES[@]}" | paste -sd, -)
cat "$QUERY_DIR"/query*.sql | grep -v '^--' > "$WORK/workload.sql"
vsql -A -t -f "$REPO_DIR/sql/vertica/dbd_design.sql" -v schema="$CHECK_SCHEMA" -v tables="'$tables'" \
     -v design_type="'incremental'" \
     -v workload="'$WORK/workload.sql'" -v design_out="'$WORK/incremental.sql'" \
     -v deploy_out="'$WORK/incremental_deploy.sql'" >"$WORK/dbd.log" 2>&1 || true

# the design output lists the existing projections too: keep only the new ones
vsql_value "select projection_name from v_catalog.projections where projection_schema = '$CHECK_SCHEMA'" \
    > "$WORK/existing.txt"
python3 - "$WORK/incremental.sql" "$WORK/existing.txt" "$WORK/incremental_new.sql" <<'EOF'
import re, sys
ddl, existing, out = sys.argv[1:]
known = set(open(existing).read().split())
try:
    stmts = [s.strip() for s in open(ddl).read().split(";") if s.strip()]
except FileNotFoundError:
    stmts = []
new = [s for s in stmts if re.match(r"CREATE PROJECTION\s+\S+\.(\w+)", s, re.I)
       and re.match(r"CREATE PROJECTION\s+\S+\.(\w+)", s, re.I).group(1) not in known]
open(out, "w").write("".join(s + ";\n\n" for s in new))
EOF
n_new=$(grep -ci '^create projection' "$WORK/incremental_new.sql" || true)

if (( n_new > 0 )); then
    log "Database Designer proposes $n_new more projections: creating them and running the queries again"
    vsql -q -f "$WORK/incremental_new.sql"
    new_tables=$(grep -iE '^ *from ' "$WORK/incremental_new.sql" | awk '{ print $2 }' | sort -u | paste -sd, -)
    vsql -q -A -t -c "select refresh('$new_tables')" > "$WORK/refresh.log"
    for t in ${new_tables//,/ }; do echo "select analyze_statistics('$t');"; done | vsql -q -A -t >/dev/null
    IFS='|' read -r run_dir2 t2 t3 <<< "$(run_queries check_incr)"
fi

# --- report ------------------------------------------------------------------
md_table() {   # query -> markdown table ("none" when it returns no rows)
    vsql -A -P footer=off -F $'\t' -c "$1" \
        | awk -F'\t' '{ gsub(/\|/, "/"); line = "|"; for (i = 1; i <= NF; i++) line = line " " $i " |"; print line }
                      NR == 1 { line = "|"; for (i = 1; i <= NF; i++) line = line " --- |"; print line }
                      END { if (NR < 2) print "\nnone" }'
}
usage_query() {   # $1 = time window, $2 = extra condition
    echo "select anchor_table_name as table_name, projection_name,
            count(distinct session_id) // $CHECK_ITERATIONS as queries
        from v_monitor.projection_usage
        where anchor_table_schema = '$CHECK_SCHEMA' and io_type = 'input' and query_start_timestamp $1 ${2:-}
        group by 1, 2 order by 1, 2"
}
storage_query() {   # $1 = condition on projection_name
    echo "select anchor_table_name as table_name, count(distinct projection_id) as projections,
            (sum(used_bytes) / 1e9)::numeric(10,3) as sample_gb,
            (sum(used_bytes * (case when anchor_table_name in ($facts) then $chunks else 1 end)) / 1e9)::numeric(10,2) as est_sf${SCALE}_gb
        from v_monitor.projection_storage where anchor_table_schema = '$CHECK_SCHEMA' and $1
        group by 1 order by 4 desc, 1"
}
new_names=$(grep -ioE '^create projection +[^ ]+' "$WORK/incremental_new.sql" 2>/dev/null \
            | awk -v q="'" '{ split($3, a, "."); printf "%s%s%s%s", (n++ ? "," : ""), q, a[2], q }')
new_names=${new_names:-"''"}

{
    echo "# Design check: $(basename "$DESIGN_FILE")"
    echo
    echo "Sample: chunk 1 of $chunks of SF$SCALE (+ full customer tables), schema $CHECK_SCHEMA;" \
         "queries run $CHECK_ITERATIONS times (best time counts); resource pool:" \
         "$([[ -n "$POOL_CONCURRENCY" ]] && echo "plannedconcurrency $POOL_CONCURRENCY, memorysize $POOL_MEMORY" || echo general)."
    echo
    echo "## Queries"
    echo
    awk -F, 'NR > 1 { if ($4 != "ok") bad = bad " " $1 ":" $2 "(" $4 ")"; else ok++; n++ }
             END { printf "%d of %d query runs OK.%s\n", ok, n, bad ? " Failed:" bad : "" }' "$run_dir/timings.csv"
    echo
    echo "## Projections not read by any query"
    echo
    md_table "select p.anchor_table_name as table_name, p.projection_name
        from v_catalog.projections p
        where p.projection_schema = '$CHECK_SCHEMA' and p.projection_name not in ($new_names) and not exists (
            select 1 from v_monitor.projection_usage u
            where u.projection_id = p.projection_id and u.io_type = 'input'
              and u.query_start_timestamp $window)
        order by 1, 2"
    echo
    echo "## Queries per projection"
    echo
    md_table "$(usage_query "$window")"
    echo
    echo "## Query events"
    echo
    echo "Events of the queries, query numbers in brackets. Watch for NO HISTOGRAM (statistics"
    echo "missing), *SPILL* / MEMORY LIMIT HIT (memory), RESEGMENTED / BROADCAST (data movement)."
    echo
    vsql -A -t -F $'\t' -c "select session_id, event_type, event_description
        from v_monitor.query_events where event_timestamp $window" \
    | awk -F'\t' -v OFS='\t' 'NR == FNR { split($0, a, ","); q[a[3]] = a[2]; next }
            ($1 in q) { k = $2 "\t" $3; n[k]++; if (index(l[k], " " q[$1]) == 0) l[k] = l[k] " " q[$1] }
            END { print "event_type", "description", "count", "queries"
                  for (k in n) print k, n[k], "[" substr(l[k], 2) "]" }' \
        "$run_dir/sessions.csv" - \
    | awk -F'\t' '{ gsub(/\|/, "/"); line = "|"; for (i = 1; i <= NF; i++) line = line " " $i " |"; print line }
                  NR == 1 { print "| --- | --- | --- | --- |" }'
    echo
    echo "## Incremental Database Designer run"
    echo
    grep -E 'accepted queries|limit' "$WORK/dbd.log" | sed 's/^ */    /'
    echo
    if (( n_new > 0 )); then
        echo "Database Designer proposes $n_new more projection(s) ($WORK/incremental_new.sql)."
        echo "They were created on the sample and the queries run again:"
        echo
        md_table "$(storage_query "projection_name in ($new_names)")"
        echo
        echo "Queries that read the new projections:"
        echo
        md_table "$(usage_query "between '$t2' and '$t3'" "and projection_name in ($new_names)")"
        echo
        python3 - "$run_dir/timings.csv" "$run_dir2/timings.csv" <<'EOF'
import csv, sys
def best(path):
    b = {}
    for r in csv.DictReader(open(path)):
        if r["status"] == "ok":
            b[r["query"]] = min(b.get(r["query"], 1e9), float(r["seconds"]))
    return b
a, b = best(sys.argv[1]), best(sys.argv[2])
qs = sorted(set(a) & set(b))
ta, tb = sum(a[q] for q in qs), sum(b[q] for q in qs)
print(f"Sum of the best times of {len(qs)} queries: {ta:.1f} s without, {tb:.1f} s with the new projections"
      f" ({(tb - ta) / ta * 100:+.1f}%).")
print()
print("Queries that changed by more than 10% and 0.1 s:")
print()
print("| query | without (s) | with (s) | change |")
print("| --- | ---: | ---: | ---: |")
for q in qs:
    if abs(b[q] - a[q]) > 0.1 and abs(b[q] - a[q]) > 0.1 * a[q]:
        print(f"| {q} | {a[q]:.2f} | {b[q]:.2f} | {(b[q] - a[q]) / a[q] * 100:+.0f}% |")
EOF
    else
        echo "No further projections proposed."
    fi
    echo
    echo "## Storage and disk space for SF$SCALE"
    echo
    echo "Designed projections. Fact tables ($FACT_TABLES) extrapolated x$chunks, other tables as loaded."
    echo
    md_table "$(storage_query "projection_name not in ($new_names)")"
    echo
    est=$(vsql_value "select sum(used_bytes * (case when anchor_table_name in ($facts) then $chunks else 1 end))
        from v_monitor.projection_storage
        where anchor_table_schema = '$CHECK_SCHEMA' and projection_name not in ($new_names)")
    old=$(vsql_value "select coalesce(sum(used_bytes), 0) from v_monitor.projection_storage where anchor_table_schema = '$SCHEMA'")
    flat=$(awk -F= '$1 == "bytes" { print $2 }' "$STATE_DIR/generate.info" 2>/dev/null || true)
    flat=${flat:-$(awk -v s="$SCALE" 'BEGIN { printf "%d", s * 1.025e9 }')}
    free=$(df -P -B1 "$WORK_DIR" | awk 'NR == 2 { print $4 }')
    awk -v e="$est" -v o="$old" -v f="$flat" -v d="$free" -v s="$SCHEMA" 'BEGIN {
        g = 1e9
        printf "| | GB |\n| --- | ---: |\n"
        printf "| free now | %.0f |\n", d / g
        printf "| freed by the schema step (current %s) | %.0f |\n", s, o / g
        printf "| flat files | %.0f |\n", f / g
        printf "| estimated Vertica storage of the design | %.0f |\n", e / g
        printf "| free after gen (schema step first) | %.0f |\n", (d + o - f) / g
        printf "| free during load, worst case (all files + all storage) | %.0f |\n", (d + o - f - e) / g
        printf "| free after load (KEEP_DATA=no) | %.0f |\n", (d + o - e) / g
    }'
    echo
    echo "GB = 10^9 bytes. Queries spill to the TEMP location on the same disk; keep a margin for that and for mergeout."
} > "$REPORT"

vsql -q -c "drop schema $CHECK_SCHEMA cascade"
log "check done: $REPORT"
cat "$REPORT"
