# Vertica: client helpers and the db_* hooks used by the shared steps.
# Sourced by scripts/common.sh when PRODUCT=vertica.
#
# Hooks every product must define:
#   PRODUCT_NAME, PRODUCT_STEPS      display name; steps of "./tpcds.sh all" after "build"
#   db_check_loaded                  die unless $SCHEMA holds the data (before a run)
#   db_copy_table <table> <files..>  bulk load one table, print the number of rows loaded
#   db_build_indexes                 after the load: indexes / constraints (if the product uses any)
#   db_collect_statistics            optimizer statistics for all tables
#   db_wait_background               wait for background work started by the load
#   db_stored_bytes                  print "table,bytes[,index_bytes]" for every table (size on disk;
#                                    bytes includes index_bytes)
#   db_run_begin                     before the power run (resource settings)
#   DB_QUERY_CMD (array)             client command: SQL on stdin, result rows on stdout
#   db_query_input <sql> <tagfile>   print the client's stdin for one query; the client
#                                    may write an id of the query into <tagfile>
#   db_cancel_query <tagfile>        stop the server side of a query whose time limit is over
#   db_save_run <results> <tags.csv> right after the run: save what the report needs
#                                    (tags.csv: iteration,query,tag written by the client)
#   db_run_end                       after the environment was recorded (release resources)
#   db_data_path                     directory that holds the database's data
#   db_env_rows                      Markdown table rows "| Setting | Value |" for the report

PRODUCT_NAME=Vertica
PRODUCT_STEPS="design schema gen load queries run"

# vsql with the configured connection; extra arguments are passed through
VSQL_ARGS=(-X -v ON_ERROR_STOP=1 -U "$DB_USER" -p "$DB_PORT")
[[ -n "$DB_HOST" ]]     && VSQL_ARGS+=(-h "$DB_HOST")
[[ -n "$DB_NAME" ]]     && VSQL_ARGS+=(-d "$DB_NAME")
[[ -n "$DB_PASSWORD" ]] && VSQL_ARGS+=(-w "$DB_PASSWORD")
vsql() { "$VSQL" "${VSQL_ARGS[@]}" "$@"; }

# single value from a query
vsql_value() { vsql -A -t -q -c "$1"; }

# Projection design for this scale factor and cluster size. A design only fits the
# node count it was made on: on one node Database Designer replicates every table
# (UNSEGMENTED ALL NODES), on a cluster it segments the large tables across nodes.
design_file() {
    echo "$REPO_DIR/sql/vertica/projections/sf${SCALE}_$(vsql_value "select count(*) from v_catalog.nodes")node.sql"
}

# true when the design file exists and was made with the running Vertica version
# (encodings and syntax of the projection DDL can differ between versions)
design_is_current() {
    local f; f=$(design_file)
    [[ -f "$f" ]] && grep -qF -- "$(vsql_value 'select version()')" "$f"
}

# --- load ---------------------------------------------------------------------

db_check_loaded() {
    local rows
    rows=$(vsql_value "select count(*) from $SCHEMA.store_sales" 2>/dev/null) \
        || die "no data in schema $SCHEMA, run: ./tpcds.sh load"
    (( rows > 0 )) || die "store_sales is empty, run: ./tpcds.sh load"
}

db_copy_table() {   # server-side COPY of all files of the table; prints the rows loaded
    local t=$1 files
    shift
    files=$(printf "'%s'," "$@"); files=${files%,}
    vsql -A -t -q -c "copy $SCHEMA.$t from $files delimiter '|' null '' abort on error"
}

# projections are written by the load itself
db_build_indexes() { :; }

db_collect_statistics() {
    local t
    for t in "${TABLES[@]}"; do echo "select analyze_statistics('$SCHEMA.$t');"; done | vsql -q -A -t >/dev/null
}

# The Tuple Mover merges the containers of a fresh load in the background; queries
# run during that work are slower, so wait until it has finished (max 1 hour).
db_wait_background() {
    local i busy
    for (( i = 0; i < 360; i++ )); do
        busy=$(vsql_value "select count(*) from v_monitor.tuple_mover_operations where is_executing")
        [[ "$busy" == 0 ]] && break
        (( i == 0 )) && log "waiting for the Tuple Mover (mergeout) to finish"
        sleep 10
    done
}

db_stored_bytes() {   # all projections of each table
    vsql -A -t -q -F, -c "select anchor_table_name, sum(used_bytes) from v_monitor.projection_storage
        where anchor_table_schema = '$SCHEMA' group by 1"
}

# --- power run ----------------------------------------------------------------

DB_QUERY_CMD=("$VSQL" "${VSQL_ARGS[@]}" -q -A -t)
SESSION_SETUP="set search_path to $SCHEMA, public;"

# optional dedicated resource pool (see POOL_CONCURRENCY in config.env.example)
db_run_begin() {
    [[ -n "$POOL_CONCURRENCY" ]] || return 0
    local exists
    exists=$(vsql_value "select count(*) from v_catalog.resource_pools where name = '$POOL_NAME'")
    [[ "$exists" == 0 ]] && vsql -q -c "create resource pool $POOL_NAME"
    vsql -q -c "alter resource pool $POOL_NAME memorysize '$POOL_MEMORY' maxmemorysize none
                plannedconcurrency $POOL_CONCURRENCY maxconcurrency none"
    SESSION_SETUP+=" set session resource_pool = $POOL_NAME;"
    log "using resource pool $POOL_NAME: memorysize $POOL_MEMORY, plannedconcurrency $POOL_CONCURRENCY"
}

# the session id written to the tag file links the query to its statements in
# v_monitor.query_requests
db_query_input() {
    printf '\\o %s\nselect session_id from v_monitor.current_session;\n\\o\n' "$2"
    echo "$SESSION_SETUP"
    cat "$1"
}

db_cancel_query() {
    [[ -s "$1" ]] && vsql -q -c "select close_session('$(head -1 "$1")')" >/dev/null 2>&1 || true
}

# Vertica's monitoring tables keep rows only for a limited time: save the run's rows
# (statements, events, projection sizes) in the results folder now; server times,
# memory and spills are computed from these files
db_save_run() {
    local result_dir=$1 tags=$2
    [[ -s "$tags" ]] || return 0
    { echo "iteration,query,session_id"; cat "$tags"; } > "$result_dir/sessions.csv"
    "$PRODUCT_DIR/save_monitoring.sh" "$result_dir" || log "could not save the monitoring data"
}

# give the memory of the benchmark pool back while the database is idle
db_run_end() {
    [[ -n "$POOL_CONCURRENCY" ]] || return 0
    vsql -q -c "alter resource pool $POOL_NAME memorysize '0%'" || true
}

# --- environment --------------------------------------------------------------

db_data_path() {
    vsql_value "select location_path from v_catalog.storage_locations where location_usage like '%DATA%' limit 1" 2>/dev/null | head -1
}

db_env_rows() {
    local q version nodes eon license pool projections
    q() { vsql_value "$1" 2>/dev/null | head -1 || true; }
    version=$(q "select version()")
    nodes=$(q "select count(*) from v_catalog.nodes")
    eon=$(q "select case when count(*) > 0 then 'Eon' else 'Enterprise' end from v_catalog.storage_locations where sharing_type = 'COMMUNAL'")
    license=$(q "select size || ' raw data limit, ' || lower(end_date) from v_catalog.licenses order by start_date desc limit 1")
    pool="general: "$(q "select 'memorysize=' || coalesce(nullif(memorysize, ''), '-') || ', maxmemorysize=' || maxmemorysize || ', plannedconcurrency=' || plannedconcurrency || ', executionparallelism=' || executionparallelism from v_catalog.resource_pools where name = 'general'")
    if [[ -n "$POOL_CONCURRENCY" ]]; then
        pool="benchmark pool $POOL_NAME: "$(q "select 'memorysize=' || memorysize || ', maxmemorysize=' || coalesce(nullif(maxmemorysize, ''), 'none') || ', plannedconcurrency=' || plannedconcurrency || ', executionparallelism=' || executionparallelism from v_catalog.resource_pools where name = '$POOL_NAME'")
    fi
    projections=$(q "select count(*) || ' projections (' || sum(case when is_super_projection then 1 else 0 end) || ' super-projections)' from v_catalog.projections where projection_schema = '$SCHEMA'")
    cat <<EOF
| Database | $PRODUCT_NAME |
| Version | ${version#Vertica Analytic Database v} |
| Deployment | $eon mode, $nodes node(s) |
| License | ${license:-n/a} |
| Resource pool | $pool |
| Projections | ${projections:-n/a}, PROJECTIONS=$PROJECTIONS |
EOF
}
