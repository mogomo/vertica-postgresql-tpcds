#!/usr/bin/env bash
# Step "queries": generate the 99 TPC-DS queries with dsqgen in the product's dialect
# (sql/<product>/dialect.tpl), then apply the product's syntax adjustments
# (scripts/<product>/rewrite.py, when present).
#
# -QUALIFY Y uses the fixed qualification parameters of the specification, so
# every run (and every product) executes exactly the same SQL.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

DSQGEN="$KIT_DIR/tools/dsqgen"
[[ -x "$DSQGEN" ]] || die "dsqgen not built yet, run: ./tpcds.sh build"
[[ -f "$KIT_DIR/query_templates/$PRODUCT.tpl" ]] || die "no dialect $PRODUCT.tpl in the toolkit, run: ./tpcds.sh build"
REWRITE="$PRODUCT_DIR/rewrite.py"

mkdir -p "$QUERY_DIR"
rm -f "$QUERY_DIR"/query*.sql
tmp=$(mktemp -d)
adjusted=()
cd "$KIT_DIR/tools"   # dsqgen reads tpcds.idx from its working directory
for (( q = 1; q <= 99; q++ )); do
    "$DSQGEN" -DIRECTORY ../query_templates -TEMPLATE "query$q.tpl" -DIALECT "$PRODUCT" \
        -QUALIFY Y -SCALE "$SCALE" -OUTPUT_DIR "$tmp" -QUIET Y >"$tmp/dsqgen.log" 2>&1 \
        || { cat "$tmp/dsqgen.log" >&2; die "dsqgen failed for query $q"; }
    out=$(printf '%s/query%02d.sql' "$QUERY_DIR" "$q")
    if [[ -f "$REWRITE" ]]; then
        python3 "$REWRITE" < "$tmp/query_0.sql" > "$out"
        cmp -s "$tmp/query_0.sql" "$out" || adjusted+=("$q")
    else
        cp "$tmp/query_0.sql" "$out"
    fi
    rm -f "$tmp/query_0.sql"
done
rm -rf "$tmp"
[[ -f "$REWRITE" ]] && log "syntax adjusted for $PRODUCT_NAME: queries ${adjusted[*]:-none}"
log "generated $(ls "$QUERY_DIR"/query*.sql | wc -l) queries in $QUERY_DIR"
