#!/usr/bin/env python3
"""Step "budgets": time limit per query for another product, from a Vertica run.

Usage: budgets.py results/<vertica-run> > budgets.csv

limit = max(60 s, 5 x the best time of the query in that run), the rule of this
benchmark: every query gets at least a minute, and five times what Vertica needed
on the same machine, data and scale factor. Output: CSV query,seconds (all 99).
The run step reads the file with QUERY_BUDGETS=budgets.csv.
"""
import csv
import sys
from pathlib import Path

FLOOR, FACTOR = 60.0, 5.0


def main(folder):
    best = {}
    for r in csv.DictReader(open(Path(folder) / "timings.csv")):
        if r["status"] == "ok":
            q, s = r["query"], float(r["seconds"])
            best[q] = min(best.get(q, s), s)
    missing = [f"{q:02d}" for q in range(1, 100) if f"{q:02d}" not in best]
    if missing:
        sys.exit(f"no successful time for queries {' '.join(missing)} in {folder}")
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["query", "seconds"])
    for q in sorted(best):
        w.writerow([q, f"{max(FLOOR, FACTOR * best[q]):.3f}"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
