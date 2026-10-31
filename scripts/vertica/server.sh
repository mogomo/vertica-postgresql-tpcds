#!/usr/bin/env bash
# Start / stop the Vertica database $DB_NAME (run as the database administrator).
#
#   scripts/vertica/server.sh start|stop|status
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

ADMINTOOLS=${ADMINTOOLS:-/opt/vertica/bin/admintools}
pw=(); [[ -n "$DB_PASSWORD" ]] && pw=(-p "$DB_PASSWORD")
case "${1:-status}" in
    start)  vsql_value "select 1" >/dev/null 2>&1 && exit 0
            "$ADMINTOOLS" -t start_db -d "$DB_NAME" "${pw[@]}" >&2 ;;
    stop)   vsql_value "select 1" >/dev/null 2>&1 || exit 0
            "$ADMINTOOLS" -t stop_db -d "$DB_NAME" "${pw[@]}" >&2 ;;
    status) "$ADMINTOOLS" -t view_cluster -d "$DB_NAME" 2>/dev/null | tail -n +3 ;;
    *)      sed -n '2,4p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
