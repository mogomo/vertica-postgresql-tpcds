"""
captions.py - the caption band: one chip per chapter, captions at spoken phrases.

Numbers come from ../results through kit.py; a caption starts where its phrase is spoken
(None: at the start of the chapter).
"""

from __future__ import annotations

import statistics

import kit
import timeline as TL

CHIPS = {"s01": "THE TEST", "s02": "MAKING IT FAIR", "s03": "STORAGE", "s04": "12 GB",
         "s05": "WHERE POSTGRESQL WINS", "s06": "WHERE IT BREAKS", "s07": "102 GB",
         "s08": "WHAT A TIME LIMIT HIDES", "s09": "WHAT IT MEANS", "s10": "REPEAT IT YOURSELF"}


def _gb(product, sf):
    return float(kit.metrics(product, sf)["stored_bytes"]) / 1e9


def _power(product, sf):
    return float(kit.metrics(product, sf)["power_best_iteration_seconds"])


def _items():
    raw10 = float(kit.metrics("vertica", 10)["raw_data_bytes"]) / 1e9
    raw100 = float(kit.metrics("vertica", 100)["raw_data_bytes"]) / 1e9
    nf10 = int(kit.metrics("postgresql", 10)["queries_not_finished"])
    nf100 = int(kit.metrics("postgresql", 100)["queries_not_finished"])
    r10, r100 = kit.ratios(10), kit.ratios(100)
    return [
        ("s01", None, "Vertica 26.3 and PostgreSQL 18.6 on the same machine, from the same data"),
        ("s01", "The workload is derived", "Workload derived from TPC-DS: 24 tables, 99 analytic queries"),
        ("s01", "We ran it at twelve", f"{raw10:.0f} GB and {raw100:.0f} GB of raw data  ·  3 runs, the best counts"),
        ("s02", None, "The same memory budget (about 40 GB) and all 22 CPU threads for each"),
        ("s02", "Each was tuned", "Each tuned the way its own documentation recommends"),
        ("s02", "No materialized views", "No materialized views, no caches, no hints, no hand-tuned queries"),
        ("s02", "We compared the answers", "The answers of all 99 queries compared row by row"),
        ("s02", "And to keep the test finite", "Time limit per PostgreSQL query: at least 60 s, and 5 x Vertica's time"),
        ("s03", None, f"{raw10:.0f} GB raw: {_gb('vertica', 10):.1f} GB in Vertica, "
                      f"{_gb('postgresql', 10):.1f} GB in PostgreSQL"),
        ("s03", "At a hundred and two", f"{raw100:.0f} GB raw: {_gb('vertica', 100):.1f} GB in Vertica, "
                                        f"{_gb('postgresql', 100):.1f} GB in PostgreSQL"),
        ("s03", "Look at one table", "inventory at 102 GB: 399 million rows of four integers"),
        ("s03", "Vertica stores each column sorted", "Sorted columns and run-length encoding: 8.2 GB of text in 0.7 GB"),
        ("s04", None, f"All 99 queries: Vertica {_power('vertica', 10):.0f} s, "
                      f"PostgreSQL at least {_power('postgresql', 10):.0f} s ({nf10} stopped at their limit)"),
        ("s04", "But look at the queries", f"{sum(r <= 1 for r in r10)} queries as fast or faster on PostgreSQL  ·  "
                                           f"{sum(r <= 2 for r in r10)} within 2x"),
        ("s04", "The typical query", f"The median query: {statistics.median(r10):.1f}x as long on PostgreSQL"),
        ("s05", None, "Query 5: sales and returns of a 14-day window"),
        ("s05", "walks the index", "A B-tree index on the date key reads only those 14 days"),
        ("s06", None, "Query 1: customers whose returns are 20% above their store's average"),
        ("s06", "PostgreSQL computes it again", "PostgreSQL runs the subquery again for every row"),
        ("s06", "Vertica turns the same subquery", "Vertica: one join, one average per store, computed once"),
        ("s06", "Four queries follow", "The same pattern: queries 1, 6, 30 and 81"),
        ("s07", None, f"Vertica: {_power('vertica', 10):.0f} s -> {_power('vertica', 100):.0f} s for 10x the data"),
        ("s07", "PostgreSQL finished only", f"PostgreSQL: {99 - nf100} of 99 queries finished within their limits"),
        ("s07", "The reason is memory", f"{_gb('vertica', 100):.1f} GB against {_gb('postgresql', 100):.1f} GB, "
                                        "with 61 GiB of memory"),
        ("s07", "The typical gap grows", f"The median gap: {statistics.median(r10):.1f}x at 12 GB, "
                                         f"{statistics.median(r100):.1f}x at 102 GB"),
        ("s08", None, "A stopped query counts with its limit: every such total is a floor"),
        ("s08", "Take the worst query", "Query 30 at 12 GB: 579.6 s against 0.158 s, 3,668x"),
        ("s08", "From one gigabyte", "1 GB -> 12 GB: 93x the time for 10x the data"),
        ("s08", "So we gave it thirty minutes", "Query 30 at 102 GB, with 30 minutes: not finished"),
        ("s09", None, "Tens of gigabytes, selective queries: PostgreSQL can be good enough"),
        ("s09", "For analytic SQL", "Analytic SQL as it is written: Vertica, faster by orders of magnitude"),
        ("s09", "And the gap grows", "The gap grows with the data: compression keeps Vertica in memory"),
        ("s10", None, "One machine, one workload, one query stream"),
        ("s10", "Vertica ran as a single node", "Vertica on one node: it is built to scale out across a cluster"),
        ("s10", "This is not an official", "Derived from TPC-DS: not an official TPC-DS result"),
        ("s10", "Every script", "Every script, setting and timing is published, as is"),
    ]


def band_items() -> list[tuple[float, str, str]]:
    order = list(CHIPS)
    out = []
    for cid, phrase, text in _items():
        sc = TL.chapter(cid)
        t = sc["start"] - 0.2 if phrase is None else TL.cue_in(sc, phrase) - 0.15
        out.append((t, f"{order.index(cid) + 1}  ·  {CHIPS[cid]}", text))
    return sorted(out)
