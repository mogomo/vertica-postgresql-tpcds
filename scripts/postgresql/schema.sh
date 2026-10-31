#!/usr/bin/env bash
# Step "schema" (PostgreSQL): (re)create schema $SCHEMA in database $PG_DB with the 24
# TPC-DS tables. Drops $SCHEMA with CASCADE first.
#
# The table DDL comes from the toolkit (tools/tpcds.sql); PostgreSQL accepts its types
# as they are. The primary key clauses are taken out and kept in
# $STATE_DIR/primary_keys.sql: the load adds them after the data is in (one index
# build instead of row-by-row maintenance), together with sql/postgresql/indexes.sql.
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

mkdir -p "$STATE_DIR"
log "dropping and creating schema $SCHEMA in database $PG_DB"
toolkit_ddl | python3 -c '
import re, sys
ddl, pks = sys.stdin.read(), []
def take(m):
    table = re.findall(r"create table (\w+)", ddl[:m.start()], re.I)[-1]
    pks.append(f"alter table {table} add primary key ({m.group(1)});")
    return ""
ddl = re.sub(r",\s*\n\s*primary key\s*\(([^)]*)\)", take, ddl, flags=re.I)   # constraint after the last column
open(sys.argv[1], "w").write("\n".join(pks) + "\n")
sys.stdout.write(ddl)' "$STATE_DIR/primary_keys.sql" > "$STATE_DIR/tables.sql"
{
    echo "drop schema if exists $SCHEMA cascade;"
    echo "create schema $SCHEMA;"
    echo "set search_path to $SCHEMA;"
    cat "$STATE_DIR/tables.sql"
} | pg -q

n=$(pg_value "select count(*) from information_schema.tables where table_schema = '$SCHEMA'")
[[ "$n" == "${#TABLES[@]}" ]] || die "expected ${#TABLES[@]} tables in $SCHEMA, found $n"
log "schema $SCHEMA created with $n tables ($(grep -c . "$STATE_DIR/primary_keys.sql") primary keys added after the load)"
