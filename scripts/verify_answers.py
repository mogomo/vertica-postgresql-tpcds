#!/usr/bin/env python3
"""Step "verify": compare the answers (result rows) of the 99 queries of two runs.

Usage: verify_answers.py results/<run-a> results/<run-b> [-o answers.md]

Reads the result sets of iteration 1 of both runs from $WORK_DIR/output/<run>/iter1/
(default work/output; the run step writes them there, they are not kept in git).
Values are compared field by field: text without trailing blanks (CHAR padding),
numbers with a tolerance of 0.01 or 1e-6 relative (one product may print an average
with more digits than the other). Per query the result is
  same           same rows in the same order
  same rows      same rows, other order (ties in ORDER BY or a different position
                 of NULLs in the sort order)
  different      n rows only in a, m rows only in b (shown in the report)
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def out_dir(run):
    work = Path(os.environ.get("WORK_DIR", REPO / "work"))
    return work / "output" / Path(run).name / "iter1"


def norm(field):
    f = field.rstrip()
    try:
        return ("n", float(f))
    except ValueError:
        return ("s", f)


def same_value(a, b):
    if a[0] == "n" and b[0] == "n":
        return abs(a[1] - b[1]) <= max(0.01, 1e-6 * max(abs(a[1]), abs(b[1])))
    return a == b


def same_row(a, b):
    return len(a) == len(b) and all(same_value(x, y) for x, y in zip(a, b))


def key(row):   # sort key: numbers rounded so rows within the tolerance sort together
    return tuple((t, round(v, 1) if t == "n" else v) for t, v in row)


def read(path):
    if not path.exists():
        return None
    return [tuple(norm(f) for f in line.rstrip("\n").split("|")) for line in open(path, errors="replace")]


def compare(a, b):
    if a is None or b is None:
        return "missing", []
    if len(a) == len(b) and all(same_row(x, y) for x, y in zip(a, b)):
        return "same", []
    rest_b, only_a = list(b), []
    for row in a:
        for i, other in enumerate(rest_b):
            if same_row(row, other):
                del rest_b[i]
                break
        else:
            only_a.append(row)
    if not only_a and not rest_b:
        return "same rows", []
    return f"different ({len(only_a)} rows only in a, {len(rest_b)} only in b)", (only_a, rest_b)


def show(row):
    return "|".join(f"{v:g}" if t == "n" else v for t, v in row)


def main(argv):
    out = None
    if "-o" in argv:
        i = argv.index("-o")
        out = Path(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) != 2:
        sys.exit(__doc__)
    da, db = out_dir(argv[0]), out_dir(argv[1])
    lines = [f"# Answers: {Path(argv[0]).name} (a) vs {Path(argv[1]).name} (b)", "",
             "| Query | Rows a | Rows b | Result |", "|---:|---:|---:|---|"]
    details, counts = [], {}
    for q in range(1, 100):
        name = f"query{q:02d}.out"
        a, b = read(da / name), read(db / name)
        status, diff = compare(a, b)
        counts[status.split(" (")[0]] = counts.get(status.split(" (")[0], 0) + 1
        lines.append(f"| {q} | {len(a) if a is not None else '-'} | {len(b) if b is not None else '-'} | {status} |")
        if diff:
            details += [f"## Query {q}", "", "Only in a (first 5):", "```"] + [show(r) for r in diff[0][:5]] + \
                       ["```", "Only in b (first 5):", "```"] + [show(r) for r in diff[1][:5]] + ["```", ""]
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    lines[1:1] = ["", summary]
    text = "\n".join(lines + [""] + details)
    if out:
        out.write_text(text)
    print(text if not out else f"{summary}\nwrote {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
