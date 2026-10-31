#!/usr/bin/env bash
# Step "design" (Vertica): run Database Designer (sql/vertica/dbd_design.sql) on a small sample of
# scale factor $SCALE on THIS system and save the resulting projection DDL as
# sql/vertica/projections/sf<SCALE>_<nodes>node.sql. The "schema" step creates these
# projections on the empty tables, so the load writes the data straight into them
# (no redesign and no refresh of the full data set later). Because DBD runs on the
# target system, the design fits its node count, K-safety and Vertica version.
# A saved design is reused only when it was made for the same node count and
# Vertica version (FORCE_DESIGN=yes to redo it anyway).
#
# The sample is a slice of the real data of the target scale factor:
#  - chunk 1 of N of dsdgen's parallel output, N chosen so that store_sales has
#    about $DESIGN_SAMPLE_ROWS rows. It contains 1/N of the fact tables and the
#    complete small dimensions (store, item, warehouse, date_dim, ...), so the
#    column cardinalities match the target scale factor;
#  - the customer tables in full (they are split across the chunks otherwise).
# A smaller scale factor is NOT a good sample: some dimensions grow with the
# scale factor (12 stores at SF1, 402 at SF100) and Database Designer then picks
# different sort orders for the fact tables.
source "$(dirname "${BASH_SOURCE[0]}")/../common.sh"

DESIGN_FILE=$(design_file)
if design_is_current && [[ "${FORCE_DESIGN:-no}" != yes ]]; then
    log "design $(basename "$DESIGN_FILE") exists for this node count and Vertica version, skipping" \
        "(FORCE_DESIGN=yes to redo)"
    exit 0
fi

# Tables left out of the design (they keep Vertica's default projection). Needed
# at SF1: Database Designer 26.2 stops with "Internal DBDesigner Error (12) isRleF"
# on the 12-row store table.
DESIGN_EXCLUDE=${DESIGN_EXCLUDE:-$( (( SCALE <= 1 )) && echo store || true)}
SAMPLE_SCHEMA="${SCHEMA}_sample"
DESIGN=tpcds_design     # name used in sql/vertica/dbd_design.sql
WORK="$WORK_DIR/state/design_sf$SCALE"
SAMPLE_DIR="$WORK_DIR/data/sample_sf$SCALE"
mkdir -p "$WORK"
chmod 755 "$WORK"   # Database Designer (server process) writes its output here

log "sample for SF$SCALE (+ full customer tables) into schema $SAMPLE_SCHEMA"
chunks=$(make_sample "$SAMPLE_DIR")
log "sample = chunk 1 of $chunks"

sample_env=(SCHEMA="$SAMPLE_SCHEMA" PROJECTIONS=default KEEP_DATA=no DATA_DIR="$SAMPLE_DIR"
            WORK_DIR="$WORK_DIR" STATE_DIR_OVERRIDE="$WORK/load")
env "${sample_env[@]}" "$PRODUCT_DIR/schema.sh"
env "${sample_env[@]}" "$REPO_DIR/scripts/load_data.sh"
"$REPO_DIR/scripts/generate_queries.sh"      # the workload: the 99 queries of this scale factor

cat "$QUERY_DIR"/query*.sql | grep -v '^--' > "$WORK/workload.sql"
rm -f "$WORK/design.sql" "$WORK/deploy.sql"

log "running Database Designer on $SAMPLE_SCHEMA${DESIGN_EXCLUDE:+ (without: $DESIGN_EXCLUDE)}"
tables=$(for t in "${TABLES[@]}"; do
             [[ " $DESIGN_EXCLUDE " == *" $t "* ]] || printf '%s.%s\n' "$SAMPLE_SCHEMA" "$t"
         done | paste -sd, -)
t0=$(now)
vsql -A -t -f "$REPO_DIR/sql/vertica/dbd_design.sql" -v schema="$SAMPLE_SCHEMA" -v tables="'$tables'" \
     -v design_type="'comprehensive'" \
     -v workload="'$WORK/workload.sql'" -v design_out="'$WORK/design.sql'" \
     -v deploy_out="'$WORK/deploy.sql'" >"$WORK/dbd.log" 2>&1 || true
t1=$(now)
if [[ ! -s "$WORK/design.sql" ]]; then
    tail -5 "$WORK/dbd.log" >&2
    die "Database Designer produced no design, see $WORK/dbd.log (a table can be left out with DESIGN_EXCLUDE)"
fi

mkdir -p "$(dirname "$DESIGN_FILE")"
{
    echo "-- TPC-DS projections for Vertica, scale factor $SCALE."
    echo "-- Database Designer (comprehensive design, optimized for the 99 queries) on a sample:"
    echo "-- chunk 1 of $chunks of the SF$SCALE data plus the full customer tables; $(vsql_value 'select version()')."
    echo "-- Nodes: $(vsql_value 'select count(*) from v_catalog.nodes')"
    [[ -n "$DESIGN_EXCLUDE" ]] && echo "-- Not designed (default projection): $DESIGN_EXCLUDE."
    echo "-- Created by scripts/vertica/design.sh with sql/vertica/dbd_design.sql; used by the schema step."
    echo "-- @SCHEMA@ = target schema. Valid for the node count and Vertica version above only."
    echo
    sed -e "s/\b$SAMPLE_SCHEMA\./@SCHEMA@./g" -e "s/_$DESIGN\b//g" "$WORK/design.sql"
} > "$DESIGN_FILE"

vsql -q -c "drop schema $SAMPLE_SCHEMA cascade"
rm -rf "$SAMPLE_DIR"
n=$(grep -ci '^create projection' "$DESIGN_FILE")
log "design ready in $(elapsed "$t0" "$t1")s: $n projections -> sql/vertica/projections/$(basename "$DESIGN_FILE")"
