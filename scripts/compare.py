#!/usr/bin/env python3
"""Step "compare": side-by-side table of several results folders -> COMPARISON.md.

Usage: compare.py results/<run-a> results/<run-b> ... [-o COMPARISON.md]

Reads metrics.csv and timings.csv of every folder (written by report.py). The
columns are the runs, named after their product and scale factor; the key
metrics come first, then the best time of every query in each run. Bar charts
(SVG) go to charts/ next to the output file. Standard library only.

A query that did not finish within its time limit counts with its limit; totals
that contain one are lower bounds, shown as ">= x", and the query as "> limit".
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402

KEY_METRICS = [                # metric, label, format
    ("product_version", "Version", "{}"),
    ("deployment", "Deployment", "{}"),
    ("scale_factor", "Scale factor", "{}"),
    ("raw_data_bytes", "Flat files", "gb"),
    ("stored_bytes", "Stored in the database (all copies / indexes)", "gb"),
    ("compression_ratio", "Compression (raw / stored)", "{}x"),
    ("stored_bytes_without_indexes", "Stored without indexes", "gb"),
    ("compression_ratio_without_indexes", "Compression without indexes", "{}x"),
    ("load_seconds", "Load time (COPY)", "s1"),
    ("load_throughput", "Load throughput", "{} MB/s"),
    ("index_seconds", "Primary keys and indexes", "s1"),
    ("stats_seconds", "Statistics", "s1"),
    ("queries_ok_all_iterations", "Queries OK in all iterations", "{}/99"),
    ("queries_not_finished", "Queries not finished within the limit", "{}"),
    ("power_best_iteration_seconds", "Power run, best iteration", "{} s"),
    ("power_sum_best_per_query_seconds", "Sum of the best time of each query", "{} s"),
    ("geomean_best_per_query_seconds", "Geometric mean of the best times", "{} s"),
    ("queries_under_1s_best", "Queries under 1 s", "{}"),
    ("max_query_memory_acquired_mb", "Largest memory of one query", "mb"),
    ("spill_events_per_iteration", "Spills per iteration (Vertica events / PostgreSQL temporary files)", "{}"),
    ("spill_bytes_per_iteration", "Temporary file bytes per iteration", "gb"),
    ("iterations", "Iterations", "{}"),
]


LOWER_BOUND = {   # metric -> flag metric that marks it as a lower bound
    "power_best_iteration_seconds": "power_best_iteration_is_lower_bound",
    "power_sum_best_per_query_seconds": "best_per_query_is_lower_bound",
    "geomean_best_per_query_seconds": "best_per_query_is_lower_bound",
}


def fmt(value, f):
    if value in (None, ""):
        return "-"
    if f == "gb":
        return f"{int(value) / 1e9:.1f} GB"
    if f == "s1":
        return "-" if float(value) < 0.05 else f"{float(value):.1f} s"
    if f == "mb":
        return f"{float(value) / 1024:.1f} GiB"
    return f.format(value)


def read_metrics(folder):
    return {r["metric"]: r["value"] for r in csv.DictReader(open(folder / "metrics.csv"))}


def best_times(folder):
    best = {}
    for r in csv.DictReader(open(folder / "timings.csv")):
        if r["status"] == "ok":
            q, s = r["query"], float(r["seconds"])
            best[q] = min(best.get(q, s), s)
    return best


def unfinished(m):
    """query -> time limit of the queries that never finished in time (from metrics.csv)."""
    return {q: float(v) for q, v in (x.split(":") for x in m.get("queries_not_finished_list", "").split())}


def cell(m, key, f):
    flag = LOWER_BOUND.get(key)
    return ("≥ " if flag and m.get(flag) == "yes" else "") + fmt(m.get(key), f)


CHARTS = [   # metric, title, unit, file
    ("power_best_iteration_seconds", "Power run, 99 queries, best of 3 iterations", "s", "power_run"),
    ("geomean_best_per_query_seconds", "Geometric mean of the best time per query (all 99)", "s", "geomean"),
    ("load_seconds", "Bulk load of the flat files", "s", "load"),
    ("stored_bytes", "Size in the database (Vertica: all projections; PostgreSQL: tables + indexes)", "GB", "storage"),
]


def write_charts(runs, folder):
    """Grouped columns per scale factor (products as series) and, per scale factor,
    the queries with the largest best time in the first product. Returns Markdown lines."""
    folder.mkdir(parents=True, exist_ok=True)
    products, scales = [], []
    for _, m, _ in runs:
        p, sf = m.get("product", "?"), m.get("scale_factor", "?")
        products.append(p) if p not in products else None
        scales.append(sf) if sf not in scales else None
    scales.sort(key=lambda x: float(x) if x.replace(".", "").isdigit() else 0)
    by = {(m.get("product"), m.get("scale_factor")): (m, b) for _, m, b in runs}
    lines = []
    for key, title, unit, name in CHARTS:
        values = [[(float(by[(p, sf)][0][key]) / (1e9 if unit == "GB" else 1)
                    if (p, sf) in by and by[(p, sf)][0].get(key) else None) for sf in scales] for p in products]
        if not any(v is not None for row in values for v in row):
            continue
        flag = LOWER_BOUND.get(key)
        lower = [[bool(flag and (p, sf) in by and by[(p, sf)][0].get(flag) == "yes") for sf in scales] for p in products]
        charts.grouped_columns(title, unit, [f"SF{sf}" for sf in scales], products, values,
                               folder / f"{name}.svg",
                               "Same machine, flat files, queries and procedure; lower is better"
                               + ("; ≥ = lower bound (queries stopped at their time limit)" if any(map(any, lower)) else ""),
                               lower=lower)
        lines.append(f"![{title}]({folder.name}/{name}.svg)")
    for sf in scales:
        # best time, or the time limit of a query that did not finish (a lower bound)
        cols = [(p, {**unfinished(by[(p, sf)][0]), **by[(p, sf)][1]}) for p in products if (p, sf) in by]
        if len(cols) < 2:
            continue
        top = sorted(cols[0][1].items(), key=lambda kv: -kv[1])[:20]
        items = [str(int(q)) for q, _ in top]
        values = [[b.get(q) for q, _ in top] for _, b in cols]
        lower = [[q in unfinished(by[(p, sf)][0]) for q, _ in top] for p, _ in cols]
        charts.grouped_bars_h(f"SF{sf}: the 20 slowest queries of {cols[0][0]}, best time", "s", items,
                              [p for p, _ in cols], values, folder / f"sf{sf}_queries.svg",
                              "Best of the iterations, client wall clock per query; > = stopped at its time limit; lower is better",
                              lower=lower)
        lines.append(f"![SF{sf} slowest queries]({folder.name}/sf{sf}_queries.svg)")
    return lines


def main(argv):
    out_path = Path("COMPARISON.md")
    if "-o" in argv:
        i = argv.index("-o")
        out_path = Path(argv[i + 1])
        del argv[i:i + 2]
    folders = [Path(a) for a in argv]
    if len(folders) < 2:
        sys.exit(__doc__)
    runs = [(f, read_metrics(f), best_times(f)) for f in folders]
    names = [f"{m.get('product', '?')} SF{m.get('scale_factor', '?')}" for _, m, _ in runs]

    out = ["# TPC-DS comparison", "",
           "Same toolkit, data, queries (`dsqgen -QUALIFY Y`), procedure and machine for every "
           "column; the settings of each run are in its results folder. Generated by "
           "`./tpcds.sh compare`; the analysis is in RESULTS.md. A query that did not finish "
           "within its time limit counts with its limit: totals marked ≥ are lower bounds, "
           "such a query shows as > limit.", "",
           "| | " + " | ".join(names) + " |", "|---|" + "---:|" * len(runs)]
    for key, label, f in KEY_METRICS:
        out.append(f"| {label} | " + " | ".join(cell(m, key, f) for _, m, _ in runs) + " |")
    out.append("| Results folder | " + " | ".join(f"[{f.name}]({f.as_posix()}/summary.md)" for f, _, _ in runs) + " |")

    settings = sorted({k for _, m, _ in runs for k in m if k.startswith("setting_")})
    if settings:
        out += ["", "## Settings", "", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(runs)]
        for k in settings:
            label = k[len("setting_"):].replace("_", " ")
            out.append(f"| {label} | " + " | ".join(m.get(k, "-") for _, m, _ in runs) + " |")

    hw = [("machine", "Machine"), ("cpu", "CPU"), ("memory", "Memory"), ("storage", "Storage"), ("os", "OS")]
    out += ["", "## Hardware", "", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(runs)]
    for k, label in hw:
        out.append(f"| {label} | " + " | ".join(m.get(k, "-") for _, m, _ in runs) + " |")

    out += ["", "## Charts", ""] + write_charts(runs, out_path.parent / "charts")

    queries = sorted({q for _, _, b in runs for q in b})
    out += ["", "## Best time per query (seconds)", "",
            "| Query | " + " | ".join(names) + " |", "|---:|" + "---:|" * len(runs)]
    for q in queries:
        cells = [f"{b[q]:.3f}" if q in b else (f"> {unfinished(m)[q]:.0f}" if q in unfinished(m) else "FAILED")
                 for _, m, b in runs]
        out.append(f"| {int(q)} | " + " | ".join(cells) + " |")
    out.append("")
    out_path.write_text("\n".join(out))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
