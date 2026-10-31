# Shared settings and helpers. Sourced by every step script.
#
# The database product is chosen with PRODUCT (vertica, postgresql). Everything
# about the toolkit, the flat files and the queries is shared; what differs per
# product (client, DDL, load statement, monitoring) lives in scripts/<product>/,
# whose common.sh is sourced at the end of this file and defines the db_* hooks
# used by the shared steps (see scripts/vertica/common.sh for the list).

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export REPO_DIR

if [[ -f "$REPO_DIR/config.env" ]]; then
    # shellcheck disable=SC1091
    source "$REPO_DIR/config.env"
else
    # shellcheck disable=SC1091
    source "$REPO_DIR/config.env.example"
fi
PRODUCT_DIR="$REPO_DIR/scripts/$PRODUCT"
[[ -f "$PRODUCT_DIR/common.sh" ]] || { echo "unknown PRODUCT '$PRODUCT' (no $PRODUCT_DIR/common.sh)" >&2; exit 1; }

# Pinned version of the TPC-DS toolkit sources (dsdgen / dsqgen)
KIT_REPO=${KIT_REPO:-https://github.com/gregrahn/tpcds-kit.git}
KIT_COMMIT=${KIT_COMMIT:-5a3a81796992b725c2a8b216767e142609966752}
KIT_DIR="$WORK_DIR/tpcds-kit"
TOOLS_PREFIX="$WORK_DIR/local"          # parser tools built here when missing
QUERY_DIR="$WORK_DIR/queries/$PRODUCT/sf$SCALE"           # the 99 queries in the product's dialect
STATE_DIR="${STATE_DIR_OVERRIDE:-$WORK_DIR/state/$PRODUCT/sf$SCALE}"   # generate/load statistics
export PATH="$TOOLS_PREFIX/bin:$PATH"

# The 24 TPC-DS tables, largest first (so they start loading first)
TABLES=(store_sales catalog_sales web_sales inventory store_returns catalog_returns
        web_returns customer customer_demographics customer_address item date_dim
        time_dim promotion household_demographics catalog_page web_page call_center
        store warehouse web_site reason ship_mode income_band)

log()  { printf '%s  %s\n' "$(date '+%F %T')" "$*" >&2; }
die()  { log "ERROR: $*"; exit 1; }
now()  { date +%s.%N; }
elapsed() { awk -v a="$1" -v b="$2" 'BEGIN { printf "%.3f", b - a }'; }

# all flat files of one table in $DATA_DIR (dsdgen writes t.dat or t_<child>_<n>.dat)
files_of() {
    local t=$1 f
    shopt -s nullglob
    for f in "$DATA_DIR/$t.dat" "$DATA_DIR/${t}"_[0-9]*_[0-9]*.dat; do
        [[ -f "$f" ]] && echo "$f"
    done
    shopt -u nullglob
}

# table DDL of the toolkit (tools/tpcds.sql) without dbgen_version (generator
# metadata, not part of the benchmark); products adapt the types from here
toolkit_ddl() {
    local ddl="$KIT_DIR/tools/tpcds.sql"
    [[ -f "$ddl" ]] || die "toolkit not found, run: ./tpcds.sh build"
    awk '/^create table dbgen_version/ { skip = 1 } !skip { print } skip && /^\);/ { skip = 0 }' "$ddl"
}

# Design sample of scale factor $SCALE, used by the Vertica steps "design" and "check":
# chunk 1 of N of dsdgen's parallel output, N chosen so that store_sales has about
# $DESIGN_SAMPLE_ROWS rows, plus the customer tables in full (they are split across
# the chunks otherwise). Writes the flat files into directory $1, prints N.
make_sample() {
    local dir=$1 chunks t dsdgen="$KIT_DIR/tools/dsdgen" rows=${DESIGN_SAMPLE_ROWS:-10000000}
    [[ -x "$dsdgen" ]] || die "dsdgen not built yet, run: ./tpcds.sh build"
    chunks=$(awk -v s="$SCALE" -v r="$rows" 'BEGIN { n = int(s * 2880404 / r + 0.5); print (n < 1 ? 1 : n) }')
    mkdir -p "$dir"
    rm -f "$dir"/*.dat
    (
        cd "$KIT_DIR/tools"   # dsdgen reads tpcds.idx from its working directory
        if (( chunks > 1 )); then
            "$dsdgen" -SCALE "$SCALE" -DIR "$dir" -TERMINATE N -FORCE Y -QUIET Y -PARALLEL "$chunks" -CHILD 1
            for t in customer customer_address customer_demographics; do
                rm -f "$dir/${t}"_1_*.dat
                "$dsdgen" -SCALE "$SCALE" -DIR "$dir" -TERMINATE N -FORCE Y -QUIET Y -TABLE "$t"
            done
        else
            "$dsdgen" -SCALE "$SCALE" -DIR "$dir" -TERMINATE N -FORCE Y -QUIET Y
        fi
    ) >&2
    rm -f "$dir"/dbgen_version*.dat
    echo "$chunks"
}

need() {
    local c
    for c in "$@"; do
        command -v "$c" >/dev/null 2>&1 || die "'$c' is required but not installed"
    done
}

# shellcheck disable=SC1090
source "$PRODUCT_DIR/common.sh"
