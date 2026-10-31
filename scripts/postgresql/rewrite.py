#!/usr/bin/env python3
"""Adjust a dsqgen-generated TPC-DS query so PostgreSQL accepts it.

Usage: rewrite.py < query.sql > query_postgresql.sql

Rewrites (semantics-preserving, see README "Query changes"):
  1. "<date> + 30 days"  ->  "<date> + 30"           (date + integer adds days)
  2. an output column alias used inside an ORDER BY expression is replaced by the
     expression it names (queries 36, 70, 86: "case when lochierarchy = 0 ...");
     PostgreSQL resolves aliases in ORDER BY only as a whole sort key
  3. integer / integer is divided as a decimal, as Vertica does (queries 21, 34, 73,
     78, 83: ratios); PostgreSQL would truncate it to an integer and compute other
     answers, so the numerator is cast to numeric
  4. "(select count(*) as item_cnt ... correlated ...) > 0"  ->  "exists (select * ...)"
     (query 41): the same text Vertica runs, so both products answer identical SQL
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlrewrite import correlated_count_to_exists, days_to_integer, decimal_division, inline_order_by_alias  # noqa: E402

# integer columns / aliases that the 99 queries divide by another integer
INTEGER_NUMERATORS = ("inv_after", "household_demographics.hd_dep_count", "ss_qty",
                      "sr_item_qty", "cr_item_qty", "wr_item_qty")


def rewrite(sql):
    sql = days_to_integer(sql)
    sql = inline_order_by_alias(sql, "lochierarchy")
    sql = decimal_division(sql, INTEGER_NUMERATORS)
    sql = correlated_count_to_exists(sql)
    return sql


if __name__ == "__main__":
    sys.stdout.write(rewrite(sys.stdin.read()))
