#!/usr/bin/env bash
# Step "schema" (Vertica): (re)create the TPC-DS schema. Drops $SCHEMA with CASCADE first.
#
# The table DDL comes from the toolkit (tools/tpcds.sql). With PROJECTIONS=designed
# the projections of sql/vertica/projections/sf<SCALE>_<nodes>node.sql (Database Designer on a sample,
# see step "design") are created on the still empty tables, so the load writes the
# data straight into them. With PROJECTIONS=default Vertica creates a default
# super-projection for each table on the first load.
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

log "dropping and creating schema $SCHEMA"
{
    echo "drop schema if exists $SCHEMA cascade;"
    echo "create schema $SCHEMA;"
    echo "set search_path to $SCHEMA;"
    toolkit_ddl
} | vsql -q

n=$(vsql_value "select count(*) from v_catalog.tables where table_schema = '$SCHEMA'")
[[ "$n" == "${#TABLES[@]}" ]] || die "expected ${#TABLES[@]} tables in $SCHEMA, found $n"


if [[ "$PROJECTIONS" == designed ]]; then
    DESIGN_FILE=$(design_file)
    design_is_current || die "no design for SF$SCALE for this node count and Vertica version" \
        "($(basename "$DESIGN_FILE")); run: ./tpcds.sh design  (or PROJECTIONS=default)"
    sed "s/@SCHEMA@/$SCHEMA/g" "$DESIGN_FILE" | vsql -q
    p=$(vsql_value "select count(*) from v_catalog.projections where projection_schema = '$SCHEMA'")
    log "schema $SCHEMA created with $n tables and $p projections from $(basename "$DESIGN_FILE")"
else
    log "schema $SCHEMA created with $n tables (default projections are created by the load)"
fi
