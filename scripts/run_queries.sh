#!/usr/bin/env bash
# Step "run": power run - the 99 queries one after another, $ITERATIONS times.
#
# Creates results/<date>_sf<scale>_<product>_<label>/ with timings.csv, lets the
# product save its monitoring data (db_save_run), collects the environment
# description and writes the summary and metrics for that folder.
#
# Time limit per query: QUERY_TIMEOUT seconds, or the query's own limit from the
# CSV file QUERY_BUDGETS (query,seconds; see scripts/budgets.py). A query that runs
# out of time is recorded as "timeout" and is not run again in the later iterations
# ("skipped", recorded with its limit as time). QUERIES="04 14" runs only those queries.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

compgen -G "$QUERY_DIR/query*.sql" >/dev/null || die "no queries, run: ./tpcds.sh queries"
db_check_loaded
db_run_begin

RUN_ID="$(date +%Y%m%d-%H%M)_sf${SCALE}_${PRODUCT}_${RUN_LABEL}"
RESULT_DIR="${RESULTS_DIR:-$REPO_DIR/results}/$RUN_ID"
OUT_DIR="$WORK_DIR/output/$RUN_ID"      # query result sets, not kept in git
mkdir -p "$RESULT_DIR" "$OUT_DIR"
CSV="$RESULT_DIR/timings.csv"
echo "iteration,query,seconds,status,rows" > "$CSV"
TAGS="$OUT_DIR/tags.csv"                # iteration,query,<id written by the client> (no header)
: > "$TAGS"

declare -A BUDGET
if [[ -n "$QUERY_BUDGETS" ]]; then
    [[ -f "$QUERY_BUDGETS" ]] || die "budget file $QUERY_BUDGETS not found"
    while IFS=, read -r q secs; do
        secs=${secs%$'\r'}
        [[ "$q" =~ ^[0-9]+$ ]] && BUDGET[$(printf '%02d' "$((10#$q))")]=$secs
    done < "$QUERY_BUDGETS"
    cp "$QUERY_BUDGETS" "$RESULT_DIR/budgets.csv"
    log "time limit per query from $QUERY_BUDGETS (${#BUDGET[@]} queries)"
fi
limit_of() { echo "${BUDGET[$1]:-$QUERY_TIMEOUT}"; }
# every limit must be a plain number of seconds, or the watchdog below could not run
for secs in "$QUERY_TIMEOUT" "${BUDGET[@]}"; do
    [[ "$secs" =~ ^[0-9]+(\.[0-9]+)?$ ]] || die "time limit '$secs' is not a number of seconds"
done

files=()
for f in "$QUERY_DIR"/query*.sql; do
    q=$(basename "$f" .sql); q=${q#query}
    [[ -z "$QUERIES" || " $QUERIES " == *" $q "* ]] && files+=("$f")
done
(( ${#files[@]} > 0 )) || die "no query matches QUERIES='$QUERIES'"

# Run the client on one query with a time limit; prints ok, error or timeout.
# Deliberately not the timeout(1) command: the one of Ubuntu 26.04 (Rust coreutils)
# polls its child every 100 ms, which added up to 0.1 s to every measured query time.
run_query() {   # $1 query file, $2 tag file, $3 stdout, $4 stderr, $5 limit (seconds)
    local pid wd rc
    db_query_input "$1" "$2" | "${DB_QUERY_CMD[@]}" >"$3" 2>"$4" &
    pid=$!                                  # the client (last command of the pipeline)
    ( sleep "$5" && touch "$3.timeout" && kill "$pid" ) 2>/dev/null &
    wd=$!
    wait "$pid" && rc=0 || rc=$?
    pkill -P "$wd" 2>/dev/null; kill "$wd" 2>/dev/null; wait "$wd" 2>/dev/null || true
    if [[ -e "$3.timeout" ]]; then rm -f "$3.timeout"; db_cancel_query "$2"; echo timeout
    elif (( rc == 0 )); then echo ok
    else echo error
    fi
}

declare -A TIMED_OUT
log "power run: ${#files[@]} queries x $ITERATIONS iterations on $SCHEMA (SF$SCALE, $PRODUCT_NAME) -> results/$RUN_ID"
for (( it = 1; it <= ITERATIONS; it++ )); do
    mkdir -p "$OUT_DIR/iter$it"
    it_t0=$(now); failed=0
    for f in "${files[@]}"; do
        q=$(basename "$f" .sql)
        out="$OUT_DIR/iter$it/$q.out"; err="$OUT_DIR/iter$it/$q.err"; tag="$OUT_DIR/iter$it/$q.tag"
        limit=$(limit_of "${q#query}")
        if [[ -n "${TIMED_OUT[$q]:-}" ]]; then
            echo "$it,${q#query},$limit,skipped,0" >> "$CSV"
            failed=$((failed + 1))
            continue
        fi
        : > "$tag"
        t0=$(now)
        status=$(run_query "$f" "$tag" "$out" "$err" "$limit")
        t1=$(now)
        [[ $status == ok ]] || failed=$((failed + 1))
        [[ $status == timeout ]] && TIMED_OUT[$q]=1
        secs=$(elapsed "$t0" "$t1")
        n=$(grep -c '' "$out" || true)
        echo "$it,${q#query},$secs,$status,$n" >> "$CSV"
        [[ -s "$tag" ]] && echo "$it,${q#query},$(head -1 "$tag")" >> "$TAGS"
        [[ $status == ok ]] || log "iteration $it $q: $status (limit ${limit}s) $(head -c 300 "$err")"
    done
    log "iteration $it done in $(elapsed "$it_t0" "$(now)")s, $failed not ok"
done

db_save_run "$RESULT_DIR" "$TAGS"
"$REPO_DIR/scripts/collect_env.sh" > "$RESULT_DIR/environment.md"
db_run_end   # after the environment is collected, so it records the settings used by the run
cp "$STATE_DIR"/*.{csv,info} "$RESULT_DIR/" 2>/dev/null || true
python3 "$REPO_DIR/scripts/report.py" "$RESULT_DIR"
log "results written to $RESULT_DIR"
