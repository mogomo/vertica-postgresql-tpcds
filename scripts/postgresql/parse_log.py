#!/usr/bin/env python3
"""Extract the statements of one power run from PostgreSQL's server log (jsonlog).

Usage: cat <log files> | parse_log.py results/<run-id> <run-id>

The queries of the run carry the application name <run-id>_<iteration>_<query>
(scripts/postgresql/common.sh). With log_min_duration_statement = 0 every statement
is logged with its duration, with log_temp_files = 0 every temporary file (a sort,
hash or aggregation that spilled to disk) with its size; parallel workers log under
the application name of their leader. Writes into the results folder:
  server_log.csv    iteration,query,kind,value   (kind: duration_ms, temp_file_bytes)
  server_times.csv  iteration,query,server_seconds,memory_mb (sum of the statements;
                    the session settings at the start are not counted)
  spills.csv        event_type,count,bytes  (temporary files of all iterations)
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

DURATION = re.compile(r"^duration: ([0-9.]+) ms\s+statement: (.*)", re.S)
TEMP = re.compile(r"^temporary file: path \"[^\"]*\", size (\d+)")


def main(folder, run_id):
    folder = Path(folder)
    prefix = run_id + "_"
    rows, server, temp_n, temp_b = [], defaultdict(float), 0, 0
    for line in sys.stdin:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        app = e.get("application_name") or ""
        if not app.startswith(prefix):
            continue
        it, q = app[len(prefix):].split("_", 1)
        msg = e.get("message") or ""
        m = DURATION.match(msg)
        if m:
            if m.group(2).lstrip().lower().startswith("set "):
                continue
            rows.append((int(it), q, "duration_ms", m.group(1)))
            server[(int(it), q)] += float(m.group(1)) / 1000
            continue
        m = TEMP.match(msg)
        if m:
            rows.append((int(it), q, "temp_file_bytes", m.group(1)))
            temp_n += 1
            temp_b += int(m.group(1))
    rows.sort(key=lambda r: (r[0], r[1]))
    with open(folder / "server_log.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["iteration", "query", "kind", "value"])
        w.writerows(rows)
    with open(folder / "server_times.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["iteration", "query", "server_seconds", "memory_mb"])
        for (it, q), s in sorted(server.items()):
            w.writerow([it, q, f"{s:.3f}", ""])
    with open(folder / "spills.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["event_type", "count", "bytes"])
        if temp_n:
            w.writerow(["TEMPORARY FILE", temp_n, temp_b])
    print(f"server log: {len(server)} queries, {temp_n} temporary files", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
