#!/usr/bin/env python3
"""Step "amend": replace some queries of a power run by a later run of those queries.

Usage: amend.py results/<power-run> results/<rerun> "<reason>"

Used when a query text changed after the power run (query 41: the EXISTS text that
Vertica runs, given to PostgreSQL too). The rows of the rerun's queries replace the
rows of the same query and iteration in timings.csv and server_times.csv of the power
run; the power run's original files are kept as timings_original.csv and
server_times_original.csv, and amended.md records what was replaced, from which run
and why. summary.md and metrics.csv are rebuilt (report.py). Running it again starts
from the original files.
"""
import csv
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    with open(path) as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(path, fields, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def amend(run, rerun, name):
    """Replace the rows of file `name` in `run` by those of `rerun`; returns the replaced queries."""
    if not (run / name).exists() or not (rerun / name).exists():
        return set()
    original = run / name.replace(".csv", "_original.csv")
    if not original.exists():
        shutil.copy(run / name, original)
    fields, rows = read(original)
    _, new = read(rerun / name)
    queries = {r["query"] for r in new}
    by = {(r["iteration"], r["query"]): r for r in new}
    out = [by.get((r["iteration"], r["query"]), r) for r in rows
           if r["query"] not in queries or (r["iteration"], r["query"]) in by]
    have = {(r["iteration"], r["query"]) for r in out}
    out += [r for k, r in by.items() if k not in have]      # e.g. no server time for a query that was stopped
    out.sort(key=lambda r: (int(r["iteration"]), r["query"]))
    write(run / name, fields, out)
    return queries


def main(run, rerun, reason):
    run, rerun = Path(run), Path(rerun)
    queries = amend(run, rerun, "timings.csv")
    if not queries:
        sys.exit(f"no timings.csv in {run} or {rerun}")
    amend(run, rerun, "server_times.csv")
    _, before = read(run / "timings_original.csv")
    _, after = read(run / "timings.csv")
    lines = [f"# Amended: queries {', '.join(str(int(q)) for q in sorted(queries))}", "",
             reason, "",
             f"The rows of these queries come from run `{rerun.name}` (same database, same "
             "settings, same time limits); the original rows of this run are kept in "
             "`timings_original.csv` and `server_times_original.csv`.", "",
             "| Iteration | Query | Original | Amended |", "|---:|---:|---:|---:|"]
    old = {(r["iteration"], r["query"]): r for r in before}
    for r in after:
        if r["query"] in queries:
            o = old.get((r["iteration"], r["query"]), {})
            lines.append(f"| {r['iteration']} | {int(r['query'])} | {o.get('seconds', '-')} s {o.get('status', '')} "
                         f"| {r['seconds']} s {r['status']} |")
    (run / "amended.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {run / 'amended.md'}")
    subprocess.run([sys.executable, str(HERE / "report.py"), str(run)], check=True)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
