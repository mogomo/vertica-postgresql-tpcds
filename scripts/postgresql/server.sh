#!/usr/bin/env bash
# Start / stop the PostgreSQL benchmark cluster (needs sudo).
#
#   scripts/postgresql/server.sh start|stop|status
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

unit="postgresql@$PG_VERSION-main"
case "${1:-status}" in
    start)  sudo systemctl start "$unit"
            for (( i = 0; i < 60; i++ )); do pg_value "select 1" >/dev/null 2>&1 && break; sleep 1; done
            pg_value "select 1" >/dev/null || die "$unit did not come up" ;;
    stop)   sudo systemctl stop "$unit" ;;
    status) systemctl is-active "$unit" || true ;;
    *)      sed -n '2,4p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
