#!/usr/bin/env bash
# Both products at one scale factor, in the order of this benchmark:
#
#   SCALE=10 scripts/run_comparison.sh
#
#  1. OS settings (tune_os.sh apply), flat files of SF$SCALE (unless already there)
#  2. Vertica: start, empty the OS page cache, projection design on a sample,
#     schema with the designed projections, load, queries, power run; stop
#  3. PostgreSQL: start, empty the OS page cache, schema, load (primary keys,
#     indexes, VACUUM ANALYZE), queries, time limits from the Vertica run
#     (budgets.py), power run; queries that did not finish within their limit are
#     run once more with RERUN_LIMIT seconds (empty = no rerun); stop
# Only one database runs at a time. Schema of both products: tpcds_sf$SCALE.
# DELETE_DATA=yes removes the flat files after the PostgreSQL load.
# START_AT=postgresql-run continues an interrupted chain at the PostgreSQL power run
# (data loaded, the Vertica run of the same scale factor done).
# Needs sudo (OS settings, page cache, PostgreSQL service).
#
# Nothing runs without a time limit: every query has one (Vertica: QUERY_TIMEOUT,
# PostgreSQL: its budget, then RERUN_LIMIT), and every step below has one, generous
# for the scale factor (step_limit); a step over its limit stops the chain.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

RERUN_LIMIT=${RERUN_LIMIT:-}
START_AT=${START_AT:-begin}
DELETE_DATA=${DELETE_DATA:-no}
export SCALE SCHEMA="tpcds_sf$SCALE"
T="$REPO_DIR/tpcds.sh"
RESULTS="${RESULTS_DIR:-$REPO_DIR/results}"

export QUERY_TIMEOUT=${QUERY_TIMEOUT:-900}    # Vertica queries (the slowest took ~70 s at SF100)

drop_cache() { sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null; }
# step <seconds> <command...>: run with a time limit, stop the chain when it fails or runs over
step() {
    local secs=$1 rc=0; shift
    timeout -k 60 "$secs" "$@" || rc=$?
    (( rc == 124 || rc == 137 )) && die "step over its time limit of ${secs}s: $*"
    (( rc == 0 )) || die "step failed (exit $rc): $*"
}
S=$SCALE
latest_run() { ls -d "$RESULTS"/*_sf"${SCALE}_$1_$2" 2>/dev/null | tail -1; }

step 120 sudo "$REPO_DIR/scripts/tune_os.sh" apply >&2
grep -qv performance /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor && die "CPU governor is not performance"

if [[ "$START_AT" == begin ]]; then
    [[ -x "$KIT_DIR/tools/dsdgen" ]] || step 1800 "$T" build
    [[ -f "$DATA_DIR/generate.info" ]] || step $(( 900 + 30 * S )) env PRODUCT=vertica "$T" gen

    log "=== Vertica SF$SCALE"
    timeout 300 env PRODUCT=postgresql "$REPO_DIR/scripts/postgresql/server.sh" stop 2>/dev/null || true
    step 900 env PRODUCT=vertica "$REPO_DIR/scripts/vertica/server.sh" start
    drop_cache
    step 7200 env PRODUCT=vertica "$T" design
    step $(( 1800 + 60 * S )) env PRODUCT=vertica "$T" schema load
    step 900 env PRODUCT=vertica "$T" queries
    drop_cache
    # 99 queries x ITERATIONS: ~12 s per iteration at SF1 scale (687 s at SF100 with 26.2), cap ~5x
    step $(( 3600 + 30 * S * ITERATIONS )) env PRODUCT=vertica "$T" run
    VRUN=$(latest_run vertica "$RUN_LABEL")
    [[ -n "$VRUN" ]] || die "no Vertica results folder for SF$SCALE"
    step 900 env PRODUCT=vertica "$REPO_DIR/scripts/vertica/server.sh" stop

    log "=== PostgreSQL SF$SCALE (time limits from $(basename "$VRUN"))"
    step 300 env PRODUCT=postgresql "$REPO_DIR/scripts/postgresql/server.sh" start
    drop_cache
    step 600 env PRODUCT=postgresql "$T" schema
    step $(( 1800 + 180 * S )) env PRODUCT=postgresql "$T" load     # COPY, primary keys, indexes, VACUUM (FREEZE, ANALYZE)
    step 900 env PRODUCT=postgresql "$T" queries
    [[ "$DELETE_DATA" == yes ]] && { log "removing the flat files in $DATA_DIR"; rm -rf "$DATA_DIR"; }
elif [[ "$START_AT" == postgresql-run ]]; then
    VRUN=$(latest_run vertica "$RUN_LABEL")
    [[ -n "$VRUN" ]] || die "no Vertica results folder for SF$SCALE"
    log "=== continuing at the PostgreSQL run of SF$SCALE (time limits from $(basename "$VRUN"))"
    timeout 900 env PRODUCT=vertica "$REPO_DIR/scripts/vertica/server.sh" stop || true
    step 300 env PRODUCT=postgresql "$REPO_DIR/scripts/postgresql/server.sh" start
else
    die "START_AT must be begin or postgresql-run"
fi
mkdir -p "$WORK_DIR/state"
BUDGETS="$WORK_DIR/state/budgets_sf$SCALE.csv"
python3 "$REPO_DIR/scripts/budgets.py" "$VRUN" > "$BUDGETS"
drop_cache
# the sum of all limits x iterations bounds the run (queries over their limit are skipped later)
limit=$(awk -F, -v it="$ITERATIONS" 'NR > 1 { s += $2 + 5 } END { printf "%d", s * it + 1800 }' "$BUDGETS")
log "PostgreSQL run: at most ${limit}s ($(( limit / 60 )) min)"
step "$limit" env PRODUCT=postgresql QUERY_BUDGETS="$BUDGETS" "$T" run
PRUN=$(latest_run postgresql "$RUN_LABEL")

if [[ -n "$RERUN_LIMIT" && -n "$PRUN" ]]; then
    late=$(awk -F, '$4 == "timeout" { printf "%s ", $2 }' "$PRUN/timings.csv")
    if [[ -n "$late" ]]; then
        log "rerun of the queries over their limit with ${RERUN_LIMIT}s each: $late"
        n=$(wc -w <<< "$late")
        step $(( n * (RERUN_LIMIT + 15) + 900 )) env PRODUCT=postgresql QUERIES="$late" ITERATIONS=1 \
            QUERY_TIMEOUT="$RERUN_LIMIT" QUERY_BUDGETS= RUN_LABEL="rerun-${RERUN_LIMIT}s" "$T" run
    fi
fi
step 300 env PRODUCT=postgresql "$REPO_DIR/scripts/postgresql/server.sh" stop
log "=== SF$SCALE done: $(basename "$VRUN") ${PRUN:+and $(basename "$PRUN")}"
