#!/usr/bin/env bash
# TPC-DS benchmark - single entry point. PRODUCT selects the database (vertica, postgresql).
#
#   ./tpcds.sh all              build + the product's steps (Vertica: design, schema, gen,
#                               load, queries, run; PostgreSQL: schema, gen, load, queries, run)
#   ./tpcds.sh <step> [...]     run individual steps in the given order
#
# Steps (shared):
#   build     download and compile the TPC-DS toolkit (dsdgen, dsqgen)
#   gen       generate the flat files for scale factor $SCALE
#   load      bulk load the flat files, build indexes (PostgreSQL), collect statistics
#   queries   generate the 99 queries in the product's dialect
#   run       power run, writes results/<date>_sf<scale>_<product>_<label>/
#   budgets   per-query time limits from a Vertica run:  ./tpcds.sh budgets results/<vertica-run>
#   verify    compare the answers of two runs:  ./tpcds.sh verify results/<run-a> results/<run-b>
#   amend     replace queries of a power run by a later run of them:  ./tpcds.sh amend results/<run> results/<rerun> "<reason>"
#   env       print the environment description
#   report    rebuild summary.md and metrics.csv of a results folder:  ./tpcds.sh report results/<run>
#   compare   side-by-side table of several results folders -> COMPARISON.md:  ./tpcds.sh compare results/<a> results/<b> ...
# Steps of the product (scripts/<product>/<step>.sh):
#   schema    drop and re-create schema $SCHEMA
#   design    (Vertica) projection design for $SCALE from a ~10M-row sample
#             -> sql/vertica/projections/sf<N>_<nodes>node.sql (skipped when the file exists)
#   check     (Vertica) test the design on the sample: failing queries, unused projections,
#             query events, further DBD proposals, storage and disk space estimate
#
# Settings come from config.env (see config.env.example); any of them can be
# given on the command line too:  PRODUCT=postgresql SCALE=10 ./tpcds.sh all
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
S=scripts

usage() { sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
[[ $# -gt 0 ]] || usage 1
case "$1" in
    -h|--help|help) usage ;;
    report)  [[ $# -eq 2 ]] || usage 1; exec python3 $S/report.py "$2" ;;
    compare) [[ $# -ge 2 ]] || usage 1; shift; exec python3 $S/compare.py "$@" ;;
    budgets) [[ $# -eq 2 ]] || usage 1; exec python3 $S/budgets.py "$2" ;;
    verify)  [[ $# -ge 3 ]] || usage 1; shift; exec python3 $S/verify_answers.py "$@" ;;
    amend)   [[ $# -eq 4 ]] || usage 1; shift; exec python3 $S/amend.py "$@" ;;
esac

# shellcheck disable=SC1091
source $S/common.sh      # settings, PRODUCT_DIR and PRODUCT_STEPS of the product

steps=("$@")
[[ "$1" == all ]] && read -ra steps <<< "build $PRODUCT_STEPS"
for step in "${steps[@]}"; do
    case "$step" in
        build)   $S/build_toolkit.sh ;;
        gen)     $S/generate_data.sh ;;
        load)    $S/load_data.sh ;;
        queries) $S/generate_queries.sh ;;
        run)     $S/run_queries.sh ;;
        env)     $S/collect_env.sh ;;
        *)  if [[ -x "$PRODUCT_DIR/$step.sh" ]]; then
                "$PRODUCT_DIR/$step.sh"
            else
                echo "unknown step for $PRODUCT: $step" >&2; usage 1
            fi ;;
    esac
done
