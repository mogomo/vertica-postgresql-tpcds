# PostgreSQL: client helpers and the db_* hooks used by the shared steps (the hook
# list is at the top of scripts/vertica/common.sh). Sourced by scripts/common.sh
# when PRODUCT=postgresql.
#
# The benchmark tables live in schema $SCHEMA of database $PG_DB. The server
# settings come from sql/postgresql/$PG_CONF.conf (installed by install.sh); the
# load builds the primary keys and the indexes of sql/postgresql/indexes.sql
# after the data is in (PG_INDEXES=yes), then VACUUM (FREEZE, ANALYZE) sets the
# hint bits and the visibility map and collects the optimizer statistics, so the
# first query run does not rewrite the freshly loaded pages.

PRODUCT_NAME=PostgreSQL
PRODUCT_STEPS="schema gen load queries run"
PSQL=${PSQL:-psql}

PSQL_ARGS=(-X -v ON_ERROR_STOP=1 -U "$PG_USER" -p "$PG_PORT" -d "$PG_DB")
[[ -n "$PG_HOST" ]] && PSQL_ARGS+=(-h "$PG_HOST")
pg() { "$PSQL" "${PSQL_ARGS[@]}" "$@"; }

# single value from a query
pg_value() { pg -A -t -q -c "$1"; }

# --- load ---------------------------------------------------------------------

db_check_loaded() {
    local rows
    rows=$(pg_value "select count(*) from $SCHEMA.store_sales" 2>/dev/null) \
        || die "no data in schema $SCHEMA, run: ./tpcds.sh load"
    (( rows > 0 )) || die "store_sales is empty, run: ./tpcds.sh load"
}

# One COPY per flat file, up to $PG_COPY_STREAMS of them at a time (a COPY is one
# process; the server runs concurrent COPYs into the same table in parallel).
# The flat files are read as they are (dsdgen -TERMINATE N: no delimiter at the end
# of the line). CSV format with a quote character that never occurs in the data:
# no quoting or backslash escapes, an empty field is NULL.
# Prints the number of rows loaded (sum of the COPY command tags).
db_copy_table() {
    local t=$1 f running=0 tmp
    shift
    tmp=$(mktemp -d)
    for f in "$@"; do
        pg -c "copy $SCHEMA.$t from stdin with (format csv, delimiter '|', null '', quote e'\\x01')" \
            < "$f" > "$tmp/$(basename "$f").out" &
        if (( ++running >= PG_COPY_STREAMS )); then wait -n || { rm -rf "$tmp"; return 1; }; (( running-- )); fi
    done
    while (( running > 0 )); do wait -n || { rm -rf "$tmp"; return 1; }; (( running-- )); done
    awk '$1 == "COPY" { s += $2 } END { printf "%d\n", s }' "$tmp"/*.out
    rm -rf "$tmp"
}

# Primary keys of the TPC-DS specification (from the toolkit DDL, kept aside by the
# schema step in $STATE_DIR/primary_keys.sql) and the secondary indexes of
# sql/postgresql/indexes.sql. Built after the load (much faster than maintaining
# them row by row); maintenance_work_mem and parallel workers come from the server
# settings. One statement after the other: each one uses parallel workers itself.
db_build_indexes() {
    [[ "$PG_INDEXES" == yes ]] || { log "PG_INDEXES=$PG_INDEXES: no primary keys, no indexes"; return 0; }
    [[ -f "$STATE_DIR/primary_keys.sql" ]] || die "no $STATE_DIR/primary_keys.sql, run: ./tpcds.sh schema"
    { echo "set search_path to $SCHEMA;"
      cat "$STATE_DIR/primary_keys.sql"
      grep -v '^--' "$REPO_DIR/sql/postgresql/indexes.sql"; } | pg -q
}

db_collect_statistics() {
    local t
    for t in "${TABLES[@]}"; do echo "vacuum (freeze, analyze) $SCHEMA.$t;"; done | pg -q
}

# checkpoint, so the written pages and the WAL do not compete with the first run
db_wait_background() { pg -q -c "checkpoint"; }

db_stored_bytes() {   # table,total bytes (heap + TOAST + free space/visibility maps + indexes),index bytes
    pg -A -t -q -F, -c "select c.relname, pg_total_relation_size(c.oid), pg_indexes_size(c.oid)
        from pg_class c join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = '$SCHEMA' and c.relkind = 'r'"
}

# --- power run ----------------------------------------------------------------

DB_QUERY_CMD=("$PSQL" "${PSQL_ARGS[@]}" -q -A -t)

db_run_begin() {
    pg_value "select 1" >/dev/null || die "PostgreSQL is not reachable (scripts/postgresql/install.sh, systemctl start postgresql)"
    RUN_START=$(date "+%F %T")
    log "$(pg_value 'select version()' | cut -d, -f1), settings: sql/postgresql/$PG_CONF.conf"
}

# Every query runs in its own session named <run id>_<iteration>_<query>
# (application name, shown in the server log and in pg_stat_activity); the name is
# the tag of the query. The time limit of the query is enforced by run_queries.sh
# (it ends the session with db_cancel_query); statement_timeout, a little longer,
# is only a safety net on the server side. $RUN_ID, $it, $q and $limit are the
# current values of run_queries.sh.
db_query_input() {
    local name="${RUN_ID}_${it}_${q#query}"
    echo "$name" > "$2"
    echo "set application_name = '$name';"
    echo "set statement_timeout = '$(( ${limit%.*} + 10 ))s';"
    echo "set search_path to $SCHEMA, public;"
    cat "$1"
}

db_cancel_query() {
    [[ -s "$1" ]] || return 0
    pg -q -c "select pg_terminate_backend(pid) from pg_stat_activity where application_name = '$(head -1 "$1")'" \
        >/dev/null 2>&1 || true
}

# The server log (jsonlog, every statement with its duration, every temporary file
# = spill to disk) of the run window is saved in the results folder, together with
# the settings and the size of every table and index:
#   server_log.csv     iteration,query,kind,value (kind: duration_ms or temp_file_bytes)
#   server_times.csv   per query: server time (sum of its statements)
#   spills.csv         temporary files written by the queries (count, bytes)
#   settings.csv       all settings that differ from the built-in defaults
#   relation_sizes.csv size of every table and index of the schema
db_save_run() {
    local result_dir=$1 logdir
    logdir=$(pg_value "select current_setting('log_directory')")
    find "$logdir" -name '*.json' -newermt "$RUN_START" -exec cat {} + \
        | python3 "$PRODUCT_DIR/parse_log.py" "$result_dir" "$RUN_ID" \
        || log "could not read the server log in $logdir"
    { echo "name,setting,unit,source"
      pg -A -t -q -F, -c "select name, '\"' || replace(setting, '\"', '\"\"') || '\"', coalesce(unit, ''), source
          from pg_settings where source not in ('default', 'override', 'client', 'session')
              and name not in ('TimeZone', 'log_timezone') order by 1"; } > "$result_dir/settings.csv"
    { echo "relation,kind,table,bytes"
      pg -A -t -q -F, -c "select c.relname, case c.relkind when 'r' then 'table' else 'index' end,
              coalesce(t.relname, c.relname), pg_relation_size(c.oid)
                + case when c.relkind = 'r' then coalesce(pg_total_relation_size(c.reltoastrelid), 0) else 0 end
          from pg_class c join pg_namespace n on n.oid = c.relnamespace
          left join pg_index i on i.indexrelid = c.oid left join pg_class t on t.oid = i.indrelid
          where n.nspname = '$SCHEMA' and c.relkind in ('r', 'i') order by 4 desc"; } > "$result_dir/relation_sizes.csv"
}

db_run_end() { :; }

# --- environment --------------------------------------------------------------

db_data_path() { pg_value "select current_setting('data_directory')" 2>/dev/null; }

db_env_rows() {
    local q version settings idx
    q() { pg_value "$1" 2>/dev/null | head -1 || true; }
    version=$(q "select current_setting('server_version')")
    settings=$(q "select string_agg(name || '=' || current_setting(name), ', ' order by name) from pg_settings
                  where name in ('shared_buffers', 'work_mem', 'hash_mem_multiplier', 'effective_cache_size',
                                 'max_parallel_workers_per_gather', 'max_parallel_workers', 'jit',
                                 'random_page_cost', 'default_statistics_target')")
    idx=$(q "select count(*) || ' indexes (' || sum(case when indisprimary then 1 else 0 end) || ' primary keys)'
             from pg_index i join pg_class c on c.oid = i.indexrelid join pg_namespace n on n.oid = c.relnamespace
             where n.nspname = '$SCHEMA'")
    cat <<EOF
| Database | $PRODUCT_NAME |
| Version | $version |
| Deployment | single server, row store (heap tables) |
| Server settings | sql/postgresql/$PG_CONF.conf: $settings |
| Indexes | ${idx:-n/a}, PG_INDEXES=$PG_INDEXES |
EOF
}
