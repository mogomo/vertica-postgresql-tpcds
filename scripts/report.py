#!/usr/bin/env python3
"""Step "report": write summary.md and metrics.csv for one results folder.

Usage: report.py results/<run-id>

Reads timings.csv, environment.md and (when present) budgets.csv, server_times.csv,
spills.csv, query_events.csv, load.csv, load.info and generate.info from the
folder - never the database, whose monitoring tables are not kept for long.

A query that did not finish within its time limit (status timeout, or skipped in
the later iterations) counts with its limit: every total that contains one is a
lower bound and is shown as ">= x".

Also writes metrics.csv (metric,value,unit): the key numbers of the run under
product-neutral names, so runs of other database products on the same TPC-DS
workload can be put side by side. Standard library only.
"""
import csv
import math
import statistics
import sys
from pathlib import Path


def read_info(path):
    info = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                info[k.strip()] = v.strip()
    return info


def gb(b):
    return f"{int(b) / 1e9:.2f} GB"


def geomean(values):
    values = [max(v, 0.001) for v in values]
    return math.exp(sum(math.log(v) for v in values) / len(values)) if values else 0.0


def read_env(path):
    """Rows of the environment table in environment.md: {label: value}."""
    env = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith("## Benchmark settings"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and cells[0] and not cells[0].startswith("-"):
                env[cells[0]] = cells[1]
    return env


def write_metrics(folder, m):
    with open(folder / "metrics.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["metric", "value", "unit"])
        for name, value, unit in m:
            if value is not None and value != "":
                w.writerow([name, value, unit])


def main(folder):
    folder = Path(folder)
    rows = list(csv.DictReader(open(folder / "timings.csv")))
    iterations = sorted({int(r["iteration"]) for r in rows})
    queries = sorted({r["query"] for r in rows})
    by = {(int(r["iteration"]), r["query"]): r for r in rows}
    server, memory = {}, {}
    if (folder / "server_times.csv").exists():
        for r in csv.DictReader(open(folder / "server_times.csv")):
            server[(int(r["iteration"]), r["query"])] = float(r["server_seconds"])
            if r.get("memory_mb"):
                memory[(int(r["iteration"]), r["query"])] = float(r["memory_mb"])

    env = folder / "environment.md"
    envd = read_env(env)
    product = envd.get("Database") or "Vertica"      # older folders: only a "Vertica" row
    out = [f"# TPC-DS on {product} - {folder.name}", ""]
    limits = {}
    if (folder / "budgets.csv").exists():
        limits = {r["query"]: float(r["seconds"]) for r in csv.DictReader(open(folder / "budgets.csv"))}

    # --- headline -------------------------------------------------------------
    ok_all = [q for q in queries if all(by.get((i, q), {}).get("status") == "ok" for i in iterations)]
    unfinished = {}      # query -> its limit, for queries that never finished in time
    for q in queries:
        rs = [by[(i, q)] for i in iterations if (i, q) in by]
        if rs and not any(r["status"] == "ok" for r in rs) and any(r["status"] in ("timeout", "skipped") for r in rs):
            unfinished[q] = limits.get(q) or max(float(r["seconds"]) for r in rs)
    per_iter = []
    for i in iterations:
        rs = [by[(i, q)] for q in queries if (i, q) in by]
        ok = [float(r["seconds"]) for r in rs if r["status"] == "ok"]
        srv = sum(server.get((i, q), 0.0) for q in queries)
        lower = any(r["status"] in ("timeout", "skipped") for r in rs)
        per_iter.append((i, sum(float(r["seconds"]) for r in rs), srv, len(ok), len(rs),
                         geomean([float(by[(i, q)]["seconds"]) for q in ok_all]), lower))
    best = {q: min(float(by[(i, q)]["seconds"]) for i in iterations if by.get((i, q), {}).get("status") == "ok")
            for q in queries if any(by.get((i, q), {}).get("status") == "ok" for i in iterations)}
    # every query: best time, or its limit when it never finished (lower bound)
    best_or_limit = {**{q: v for q, v in unfinished.items()}, **best}
    ge = "≥ " if unfinished else ""

    out += ["## Power run (99 queries, sequential)", "",
            "| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |",
            "|---:|---:|---:|---:|---:|"]
    for i, total, srv, n_ok, n, gm, lower in per_iter:
        srv_txt = f"{srv:.1f} s" if server else "-"
        out.append(f"| {i} | {'≥ ' if lower else ''}{total:.1f} s | {srv_txt} | {n_ok}/{n} | {gm:.3f} s |")
    if best_or_limit:
        out.append(f"| best of each query | {ge}{sum(best_or_limit.values()):.1f} s | | {len(best)}/{len(queries)} "
                   f"| {ge}{geomean(list(best_or_limit.values())):.3f} s (all queries) |")
    if unfinished:
        txt = ", ".join(f"q{int(q)} ({v:.0f} s)" for q, v in sorted(unfinished.items()))
        out += ["", f"Did not finish within the time limit (counted with the limit, so the totals marked ≥ "
                    f"are lower bounds): {txt}"]
    spill_events = None
    spills = folder / "spills.csv"
    if spills.exists():
        ev = list(csv.DictReader(open(spills)))
        spill_events = sum(int(r["count"]) for r in ev)
        txt = ", ".join(f"{r['event_type']} {r['count']}" + (f" ({gb(r['bytes'])})" if r.get("bytes") else "")
                        for r in ev) or "none"
        out += ["", f"Memory spills to disk (all iterations): {txt}"]
    events = folder / "query_events.csv"
    if events.exists():
        per_q = {}
        for r in csv.DictReader(open(events)):
            if "SPILL" in r["event_type"] or r["event_type"] == "MEMORY LIMIT HIT":
                per_q[r["query"]] = per_q.get(r["query"], 0) + 1
        if per_q:
            txt = ", ".join(f"q{q} {n}" for q, n in sorted(per_q.items(), key=lambda kv: (-kv[1], kv[0])))
            out += ["", f"Spill events per query (all iterations): {txt}"]
    peak = max(memory.items(), key=lambda kv: kv[1]) if memory else None
    if peak:
        out += ["", f"Largest memory acquired by one query: {peak[1] / 1024:.1f} GiB (query {int(peak[0][1])})"]
    out += ["", "Total time = wall clock measured by the client around each query (includes "
            "connecting and fetching the result). Server time = execution time recorded by "
            f"{product} itself (see `server_times.csv`).", ""]

    # --- data generation / load ------------------------------------------------
    gen = read_info(folder / "generate.info")
    load = read_info(folder / "load.info")
    if gen or load:
        out += ["## Data generation and load", ""]
        src = load.get("from") or gen.get("from")
        if src:                    # run step only, on data loaded by an earlier run
            out += [f"Same database as run `{src}` (not reloaded); its generation and load:", ""]
        out += ["| Step | Value |", "|---|---:|"]
        if gen:
            out.append(f"| dsdgen ({gen.get('jobs')} parallel) | {float(gen['seconds']):.1f} s, {gb(gen['bytes'])} flat files |")
        if load:
            stats = {"Vertica": "analyze_statistics", "PostgreSQL": "VACUUM (FREEZE, ANALYZE)"}.get(product, "statistics")
            out.append(f"| COPY, {load.get('load_jobs')} tables in parallel | {float(load['load_seconds']):.1f} s |")
            if float(load.get("index_seconds") or 0) > 0:
                out.append(f"| primary keys and indexes | {float(load['index_seconds']):.1f} s |")
            out.append(f"| {stats} | {float(load['stats_seconds']):.1f} s |")
            idx = int(load.get("index_bytes") or 0)
            stored = int(load["storage_bytes"])
            ratio = f" (compression {int(gen['bytes']) / max(stored, 1):.1f}x)" if gen else ""
            out.append(f"| {product} storage | {gb(stored)}{ratio} |")
            if idx:
                ratio = f" (compression {int(gen['bytes']) / max(stored - idx, 1):.1f}x)" if gen else ""
                out.append(f"| of which indexes | {gb(idx)}; data without indexes {gb(stored - idx)}{ratio} |")
        out.append("")
    lrows = list(csv.DictReader(open(folder / "load.csv"))) if (folder / "load.csv").exists() else []
    if lrows:
        sizes = bool(lrows[0].get("stored_bytes"))
        if sizes:
            has_files = any(int(r.get("file_bytes") or 0) for r in lrows)
            out += ["<details><summary>Rows, load time and size per table</summary>", "",
                    "| Table | Rows | Load time | Flat files | Stored | Compression |",
                    "|---|---:|---:|---:|---:|---:|"]
            for r in lrows:
                fb, sb = int(r.get("file_bytes") or 0), int(r["stored_bytes"])
                ftxt = gb(fb) if has_files else "-"
                ratio = f"{fb / sb:.1f}x" if fb and sb else "-"
                out.append(f"| {r['table']} | {int(r['rows']):,} | {float(r['seconds']):.1f} s "
                           f"| {ftxt} | {gb(sb)} | {ratio} |")
        else:
            out += ["<details><summary>Rows and load time per table</summary>", "",
                    "| Table | Rows | Load time |", "|---|---:|---:|"]
            for r in lrows:
                out.append(f"| {r['table']} | {int(r['rows']):,} | {float(r['seconds']):.1f} s |")
        out += ["", "</details>", ""]

    # --- environment -----------------------------------------------------------
    if env.exists():
        out += [env.read_text().rstrip(), ""]

    # --- per query -----------------------------------------------------------------
    head = "| Query | " + " | ".join(f"Iter {i}" for i in iterations) + " | Best | Rows |"
    out += ["## Per-query times (seconds)", "", head,
            "|---:|" + "---:|" * (len(iterations) + 2)]
    for q in queries:
        cells = []
        for i in iterations:
            r = by.get((i, q))
            if r is None:
                cells.append("")
            elif r["status"] == "ok":
                cells.append(f"{float(r['seconds']):.3f}")
            elif r["status"] in ("timeout", "skipped"):
                cells.append(f"{r['status'].upper()} (limit {limits.get(q) or float(r['seconds']):.0f})")
            else:
                cells.append(r["status"].upper())
        b = f"{best[q]:.3f}" if q in best else (f"> {unfinished[q]:.0f}" if q in unfinished else "-")
        n = by.get((iterations[-1], q), {}).get("rows", "")
        out.append(f"| {int(q)} | " + " | ".join(cells) + f" | {b} | {n} |")
    out.append("")

    (folder / "summary.md").write_text("\n".join(out))
    print(f"wrote {folder / 'summary.md'}")

    # --- metrics.csv: product-neutral key numbers ---------------------------------
    if "Database" in envd:
        version, deployment = envd.get("Version", ""), envd.get("Deployment", "")
    else:                          # older folders: "| Vertica | <version>, <mode>, <nodes> |"
        old = envd.get("Vertica", "")
        version = old.split(",")[0].split()[-1].lstrip("v") if old else ""
        deployment = ", ".join(x.strip() for x in old.split(",")[1:]) if old else ""
    bi = min(per_iter, key=lambda p: p[1]) if per_iter else None
    idx_b = int(load.get("index_bytes") or 0) if load else 0
    raw = int(gen["bytes"]) if gen else None
    stored = int(load["storage_bytes"]) if load.get("storage_bytes") else None
    rows_total = sum(int(r["rows"]) for r in lrows) if lrows else None
    load_s = float(load["load_seconds"]) if load else None
    scale = gen.get("scale") or load.get("scale")
    m = [
        ("product", product, ""),
        ("product_version", version, ""),
        ("deployment", deployment, ""),
        ("scale_factor", scale, ""),
        ("tables", len(lrows) or None, ""),
        ("total_rows", rows_total, "rows"),
        ("raw_data_bytes", raw, "bytes"),
        ("stored_bytes", stored, "bytes"),
        ("compression_ratio", f"{raw / stored:.2f}" if raw and stored else None, "raw/stored"),
        ("index_bytes", idx_b if load else None, "bytes"),
        ("stored_bytes_without_indexes", stored - idx_b if stored else None, "bytes"),
        ("compression_ratio_without_indexes", f"{raw / (stored - idx_b):.2f}" if raw and stored else None, "raw/stored"),
        ("datagen_seconds", gen.get("seconds"), "s"),
        ("load_seconds", load.get("load_seconds"), "s"),
        ("load_parallel_tables", load.get("load_jobs"), ""),
        ("load_throughput", f"{raw / load_s / 1e6:.1f}" if raw and load_s else None, "MB/s raw"),
        ("load_rows_per_second", f"{rows_total / load_s:.0f}" if rows_total and load_s else None, "rows/s"),
        ("index_seconds", load.get("index_seconds"), "s"),
        ("stats_seconds", load.get("stats_seconds"), "s"),
        ("iterations", len(iterations), ""),
        ("queries", len(queries), ""),
        ("queries_ok_all_iterations", len(ok_all), ""),
        ("queries_not_finished", len(unfinished), "queries"),
        ("queries_not_finished_list", " ".join(f"{q}:{v:.0f}" for q, v in sorted(unfinished.items())), "query:limit_s"),
    ]
    for i, total, srv, n_ok, n, gm, lower in per_iter:
        m.append((f"power_iteration_{i}_seconds", f"{total:.1f}", "s"))
    if bi:
        m += [("power_best_iteration_seconds", f"{bi[1]:.1f}", "s"),
              ("power_best_iteration_is_lower_bound", "yes" if bi[6] else "no", ""),
              ("power_best_iteration_server_seconds", f"{bi[2]:.1f}" if server else None, "s"),
              ("geomean_best_iteration_seconds", f"{bi[5]:.3f}", "s")]
    if best_or_limit:
        m += [("power_sum_best_per_query_seconds", f"{sum(best_or_limit.values()):.1f}", "s"),
              ("geomean_best_per_query_seconds", f"{geomean(list(best_or_limit.values())):.3f}", "s"),
              ("best_per_query_is_lower_bound", "yes" if unfinished else "no", ""),
              ("queries_under_1s_best", sum(v < 1 for v in best.values()), "queries")]
    if peak:
        m.append(("max_query_memory_acquired_mb", f"{peak[1]:.0f}", "MB"))
    spill_bytes = sum(int(r.get("bytes") or 0) for r in csv.DictReader(open(spills))) if spills.exists() else 0
    if spill_bytes:
        m.append(("spill_bytes_per_iteration", f"{spill_bytes / len(iterations):.0f}", "bytes"))
    if spill_events is not None:
        m.append(("spill_events_per_iteration", f"{spill_events / len(iterations):.0f}", "events"))
    m += [("machine", envd.get("Machine"), ""), ("cpu", envd.get("CPU"), ""),
          ("memory", envd.get("Memory"), ""),
          ("storage", envd.get("Storage (database data)") or envd.get("Storage (Vertica data)"), ""),
          ("os", envd.get("OS"), "")]
    # the product's own settings (rows after "Deployment" / "License" in the environment
    # table, e.g. Vertica's resource pool and projections, PostgreSQL's server settings)
    shared = {"Date", "Machine", "CPU", "Memory", "Storage (database data)", "Storage (Vertica data)",
              "OS", "Power", "Database", "Version", "Deployment", "Vertica", "License"}
    m += [("setting_" + k.lower().replace(" ", "_"), v, "") for k, v in envd.items() if k not in shared]
    write_metrics(folder, m)
    print(f"wrote {folder / 'metrics.csv'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
