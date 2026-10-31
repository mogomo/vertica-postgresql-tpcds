#!/usr/bin/env python3
"""Adjust a dsqgen-generated TPC-DS query so Vertica accepts it.

Usage: rewrite.py < query.sql > query_vertica.sql

Rewrites (all semantics-preserving, see README "Query changes"):
  1. "<date> + 30 days"  ->  "<date> + 30"           (date + integer adds days)
  2. derived table without an alias gets one:       "from (select ...)"  ->  "from (select ...) dt1"
  3. "(select count(*) as item_cnt ... correlated ...) > 0"  ->  "exists (select * ...)"   (query 41)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlrewrite import add_derived_table_aliases, correlated_count_to_exists, days_to_integer  # noqa: E402


def rewrite(sql):
    sql = days_to_integer(sql)
    sql = add_derived_table_aliases(sql)
    sql = correlated_count_to_exists(sql)
    return sql


if __name__ == "__main__":
    sys.stdout.write(rewrite(sys.stdin.read()))
