#!/usr/bin/env bash
# Save Vertica's monitoring data of one power run into its results folder.
#
# Usage: scripts/vertica/save_monitoring.sh results/<run-id>
#
# Vertica keeps v_monitor.query_requests, query_events etc. only for a limited
# time (older rows are dropped as new ones arrive), so the rows of the run are
# copied right after it (the run step calls this script) and every number of the
# report is computed from the saved files:
#   sessions.csv            iteration,query,session_id of every query of the run
#   query_requests.csv      statements of the run: duration, memory, success
#   query_events.csv        optimizer/execution events (spills, missing statistics, ...)
#   projection_storage.csv  size of every projection of the schema
#   server_times.csv        per query: server time (sum of its statements), memory
#   spills.csv              spill / memory-limit events, total per type
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

RESULT_DIR=${1:?usage: $0 results/<run-id>}
S="$RESULT_DIR/sessions.csv"
[[ -s "$S" ]] || die "no $S"

ids=$(tail -n +2 "$S" | cut -d, -f3 | sed "s/.*/'&'/" | paste -sd,)
tmp=$(mktemp -d)
# free-text column as a quoted CSV field on one line (at most 20000 characters)
q() { echo "'\"' || replace(replace(coalesce($1, '')::varchar(20000), '\"', '\"\"'), chr(10), ' ') || '\"'"; }

# prefix each row (session_id first) with iteration,query from sessions.csv
with_query() {
    awk -F, 'NR == FNR { if (FNR > 1) key[$3] = $1 "," $2; next }
             { sid = $1; sub(/^[^,]*,/, ""); if (sid in key) print key[sid] "," $0 }' "$S" -
}

vsql -A -t -q -F, -c "select session_id, statement_id, request_type, start_timestamp, end_timestamp,
        request_duration_ms, memory_acquired_mb, success, error_count
    from v_monitor.query_requests
    where session_id in ($ids) and request not ilike '%current_session%'
    order by start_timestamp" > "$tmp/requests" || die "cannot read v_monitor.query_requests"
{ echo "iteration,query,statement_id,request_type,start_timestamp,end_timestamp,duration_ms,memory_acquired_mb,success,error_count"
  with_query < "$tmp/requests"; } > "$RESULT_DIR/query_requests.csv"

vsql -A -t -q -F, -c "select session_id, statement_id, event_timestamp, event_category, event_type,
        operator_name, path_id, event_severity,
        $(q event_description), $(q event_details), $(q suggested_action)
    from v_monitor.query_events
    where session_id in ($ids)
    order by event_timestamp" > "$tmp/events" || die "cannot read v_monitor.query_events"
{ echo "iteration,query,statement_id,event_timestamp,event_category,event_type,operator_name,path_id,event_severity,event_description,event_details,suggested_action"
  with_query < "$tmp/events"; } > "$RESULT_DIR/query_events.csv"

{ echo "projection_name,anchor_table_name,row_count,used_bytes,ros_count"
  vsql -A -t -q -F, -c "select projection_name, anchor_table_name, sum(row_count), sum(used_bytes), sum(ros_count)
      from v_monitor.projection_storage where anchor_table_schema = '$SCHEMA'
      group by 1, 2 order by 4 desc" || true; } > "$RESULT_DIR/projection_storage.csv"

# derived from the saved files
{ echo "iteration,query,server_seconds,memory_mb"
  awk -F, 'NR > 1 && $4 == "QUERY" { k = $1 "," $2; ms[k] += $7; if ($8 > mb[k]) mb[k] = $8 }
           END { for (k in ms) printf "%s,%.3f,%.0f\n", k, ms[k] / 1000, mb[k] }' \
      "$RESULT_DIR/query_requests.csv" | sort -t, -k1,1n -k2,2; } > "$RESULT_DIR/server_times.csv"
{ echo "event_type,count"
  awk -F, 'NR > 1 && ($6 ~ /SPILL/ || $6 == "MEMORY LIMIT HIT") { n[$6]++ }
           END { for (t in n) print t "," n[t] }' "$RESULT_DIR/query_events.csv" | sort; } > "$RESULT_DIR/spills.csv"

rm -rf "$tmp"
log "monitoring data saved in $RESULT_DIR ($(( $(wc -l < "$RESULT_DIR/query_requests.csv") - 1 )) statements," \
    "$(( $(wc -l < "$RESULT_DIR/query_events.csv") - 1 )) events)"
