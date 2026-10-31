# TPC-DS: Vertica vs PostgreSQL on the same machine

The TPC-DS decision-support workload (24 tables, 99 queries) run with **Vertica 26.3**
and **PostgreSQL 18** on the same laptop, from the same flat files, with the same
queries and the same procedure, at scale factors 10 and 100 (~10 GB and ~100 GB of
raw data). Everything needed to repeat both runs is in this repository.

Results: [Results](#results) below, the side-by-side tables in
[COMPARISON.md](COMPARISON.md), every run in its own folder under `results/`.

## Rules of the comparison

The goal is a comparison a sceptical reader can accept, so both products get the
same conditions and their usual best-practice setup, and nothing else:

- **Same everything:** one machine (64 GB RAM, 22 CPU threads, NVMe SSD), the same
  OS settings, the same flat files, the same 99 queries (`dsqgen -QUALIFY Y`), a
  memory budget of about 40 GB and all 22 threads for each product. Only one database
  runs at a time; the OS page cache is emptied before each product's load and run.
- **Each product set up the way its documentation recommends:**
  - Vertica: projections designed by the Database Designer for the 99 queries (on a
    sample, before the load), a resource pool for the query session (65% of RAM,
    planned concurrency 2), optimizer statistics.
  - PostgreSQL: server settings sized for the machine (shared buffers, work memory,
    parallel query on all threads, JIT, SSD cost settings,
    [sql/postgresql/tuned.conf](sql/postgresql/tuned.conf)), the primary keys of the
    TPC-DS specification on every table, B-tree indexes on the date and customer keys
    of the fact tables ([sql/postgresql/indexes.sql](sql/postgresql/indexes.sql)),
    `VACUUM (FREEZE, ANALYZE)` with a raised statistics target. Core PostgreSQL, no
    extensions.
- **Not used by either:** precomputed results (materialized views, aggregate
  projections), result caches, per-query hints or settings, hand-rewritten queries.
  The queries get syntax-only changes, listed in [Query changes](#query-changes).
- **Same answers:** at scale factor 1 the results of the 99 queries were compared row
  by row between the two products (see [Answer check](#answer-check)).
- **Time limits, stated openly:** to keep the runs finite, a PostgreSQL query gets
  `max(60 s, 5 x Vertica's best time for the same query at the same scale factor)`.
  A query over its limit is stopped, reported as *did not finish* with its limit,
  and not run again in the later iterations; every total that contains such a query
  is a lower bound (shown as `≥`). At SF10 every query that did not finish was run
  once more with a 10-minute limit, to give it a real number where possible.

## Results

Dell Precision 3591 laptop (Intel Core Ultra 7 165H, 22 threads, 64 GB RAM, NVMe SSD),
Ubuntu 26.04, Vertica 26.3.0 (one node) and PostgreSQL 18.6, 2026-10-31. Details,
per-query analysis and all results folders: [RESULTS.md](RESULTS.md).

| | Vertica SF10 | PostgreSQL SF10 | Vertica SF100 | PostgreSQL SF100 |
|---|---:|---:|---:|---:|
| 99 queries, best of 3 iterations | **94 s** | **≥ 856 s** | **664 s** | **≥ 5,842 s** |
| Queries finished within their limit | 99 | 91 | 99 | 42 |
| Geometric mean of the best time per query | 0.32 s | ≥ 1.81 s | 1.36 s | ≥ 31.96 s |
| Size in the database (flat files 12.0 / 102.5 GB) | **4.1 GB** | **22.2 GB** (6.3 GB indexes) | **39.2 GB** | **147.5 GB** (33.1 GB indexes) |
| Load: COPY / indexes / statistics | 33 s / - / 3.5 s | 30 s / 63 s / 98 s | 388 s / - / 11 s | 499 s / 1,099 s / 1,845 s |

`≥`: lower bound - PostgreSQL queries over their time limit are counted with the limit.
At SF10, three of the eight queries that did not finish within 60 s finished with a
10-minute limit (121 s, 388 s, 580 s); five needed more than 10 minutes. PostgreSQL was as
fast as or faster than Vertica on 7 queries at SF10 and 1 at SF100 (selective index
lookups); the largest gaps are correlated subqueries, which PostgreSQL runs once per row
([analysis/](analysis/README.md)).

![Power run](charts/power_run.svg)
![Storage](charts/storage.svg)

## How to repeat

Requirements: Ubuntu (tested on 26.04) on one machine, Vertica installed with a
database (tested with 26.3 Community Edition, single node), `sudo`, `gcc`, `make`,
`git`, `curl`, `python3`. Run as the Vertica database administrator.

```bash
git clone <this repository> vertica-postgresql-tpcds && cd vertica-postgresql-tpcds
cp config.env.example config.env        # connection, paths (WORK_DIR for the data), PG_DATA_DIR
scripts/postgresql/install.sh           # PostgreSQL 18 from the PostgreSQL apt repository
SCALE=1 ITERATIONS=1 RUN_LABEL=smoke scripts/run_comparison.sh     # a few minutes per product
SCALE=10 RERUN_LIMIT=600 scripts/run_comparison.sh
SCALE=100 DELETE_DATA=yes scripts/run_comparison.sh
./tpcds.sh compare results/<vertica-sf10> results/<postgresql-sf10> results/<vertica-sf100> results/<postgresql-sf100>
```

`scripts/run_comparison.sh` runs one scale factor end to end: OS settings
(`scripts/tune_os.sh`), data generation, then Vertica (projection design on a
sample, schema, load, queries, power run) and then PostgreSQL (schema, load with
primary keys, indexes and VACUUM ANALYZE, queries, time limits from the Vertica run,
power run, optional rerun). The other database is stopped while one is measured.
Every step has a time limit, so the chain cannot hang.

The single steps are available through `./tpcds.sh` (`PRODUCT=vertica|postgresql`):

| Step | What it does |
|---|---|
| `build` | download and compile the TPC-DS toolkit (dsdgen, dsqgen) |
| `gen` | generate the flat files of scale factor `SCALE` |
| `design` | (Vertica) Database Designer on a sample of the scale factor -> `sql/vertica/projections/` |
| `schema` | drop and re-create the schema with the 24 tables (Vertica: with the designed projections) |
| `load` | bulk load, (PostgreSQL) primary keys and indexes, statistics; sizes per table |
| `queries` | the 99 queries in the product's dialect |
| `run` | power run: 99 queries x `ITERATIONS`, results folder with timings, monitoring data, environment, summary |
| `budgets` | per-query time limits from a Vertica results folder |
| `verify` | compare the answers of two runs |
| `report`, `compare` | rebuild a summary; side-by-side table and charts of several runs |

Main settings (`config.env.example` has all of them):

| Setting | Default | Meaning |
|---|---|---|
| `SCALE` | 1 | TPC-DS scale factor |
| `ITERATIONS` | 3 | power run iterations; the best iteration is reported |
| `POOL_CONCURRENCY`, `POOL_MEMORY` | 2, 65% | Vertica resource pool of the query session |
| `PG_CONF` | tuned | `sql/postgresql/<PG_CONF>.conf` is installed as the server settings |
| `PG_INDEXES` | yes | primary keys and `sql/postgresql/indexes.sql` after the load |
| `PG_COPY_STREAMS` | 6 | flat files of one table loaded concurrently into PostgreSQL |
| `QUERY_BUDGETS` | - | CSV `query,seconds`: time limit per query (written by `budgets`) |
| `QUERY_TIMEOUT` | 3600 (chain: 900 for Vertica) | time limit per query without a budget file |
| `RERUN_LIMIT` | - | chain: rerun the queries over their limit once with this limit |

## Query changes

The queries are generated by the TPC `dsqgen` tool with the qualification parameters,
so both products run the same SQL. Each product then gets only the changes it needs to
accept the queries and compute the same answers.

Vertica (`scripts/vertica/rewrite.py`):

| Change | Queries | Reason |
|---|---|---|
| `date + 30 days` -> `date + 30` | 5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98 | Vertica adds days with `date + integer` |
| alias added to derived tables (`from (select ...) dt1`) | 2, 14, 23, 49 | Vertica requires an alias for a subquery in `FROM` |
| `(select count(*) ... correlated) > 0` -> `exists (select * ...)` | 41 | correlated subquery with `COUNT` is not supported; `EXISTS` is equivalent |

PostgreSQL (`scripts/postgresql/rewrite.py`):

| Change | Queries | Reason |
|---|---|---|
| `date + 30 days` -> `date + 30` | 5, 12, 16, 20, 21, 32, 37, 40, 77, 80, 82, 92, 94, 95, 98 | PostgreSQL adds days with `date + integer` |
| `case when lochierarchy = 0 ...` in `ORDER BY` -> the expression the alias names | 36, 70, 86 | PostgreSQL accepts an output alias in `ORDER BY` only as a whole sort key |
| `a / b` with two integers -> `cast(a as numeric) / b` | 21, 34, 73, 78, 83 | the queries compute ratios (e.g. `hd_dep_count / hd_vehicle_count > 1.2`); Vertica divides integers as decimals, PostgreSQL would truncate and return other rows |

Only a dialect template per product (`sql/<product>/dialect.tpl`, row limit as
`LIMIT n`) is added to the toolkit.

## Answer check

At scale factor 1 both products ran the 99 queries and `./tpcds.sh verify` compared
the result rows (text without CHAR padding, numbers with a tolerance of 0.01):

- 90 queries return identical rows in identical order;
- 4 return the same rows in another order (ties in `ORDER BY`);
- 2 (14, 93) differ only in which rows reach the `LIMIT`: the products place NULLs
  differently in the sort order (Vertica first, PostgreSQL last for ascending order);
- 1 (17): the standard deviation of a single value is NaN in Vertica and NULL in
  PostgreSQL (both "undefined"); all other columns are equal;
- 2 (4, 11) did not finish in PostgreSQL within the 5 minutes given at SF1, so their
  answers could not be compared there.

The check was repeated on the SF10 power runs with the same outcome (reports in
[analysis/answers/](analysis/answers/)).

## What is measured

- **Power run:** the 99 queries one after another in one session, in query number
  order, three times. Times are measured by the client (wall clock around `vsql` /
  `psql`, including fetching the result); the server's own time is saved as well
  (Vertica `v_monitor.query_requests`, PostgreSQL server log). Iteration 1 runs right
  after the load with an empty OS page cache.
- **Load:** data generation, `COPY`, PostgreSQL primary keys and indexes, statistics,
  each timed on its own.
- **Storage:** flat-file size, size in the database (Vertica: all projections;
  PostgreSQL: tables incl. TOAST and maps, indexes shown separately) and the
  compression ratio flat files / database size.
- **Spills:** Vertica spill events, PostgreSQL temporary files.
- Monitoring data is copied into the results folder at run time; all reports are
  computed from these files only.

## Disclaimer

This is not an official TPC-DS benchmark result. The workload is derived from TPC-DS:
the TPC-DS toolkit is used to generate the data and the queries, but the run rules of
the TPC (throughput test, data maintenance, auditing, pricing) are not followed, so
the numbers cannot be compared with published TPC-DS results. TPC-DS is a trademark of
the Transaction Processing Performance Council. The toolkit is downloaded from its own
repository under its own license and is not part of this repository.

The results describe one workload on one machine with one node per product; other
workloads (transactions, many concurrent users, data updates) and other hardware can
give different results.

## Repository layout

```
tpcds.sh                  entry point (PRODUCT selects scripts/<product>/)
config.env.example        settings (copy to config.env)
scripts/                  shared steps: toolkit build, data generation, load and run loops, query
                          generation, time limits, answer check, environment, report, compare, OS tuning,
                          run_comparison.sh (one scale factor, both products)
scripts/vertica/          Vertica: client hooks, server start/stop, schema, projection design and check,
                          monitoring data, query rewrite
scripts/postgresql/       PostgreSQL: install, server start/stop, client hooks, schema, server log parser,
                          query rewrite
sql/vertica/              dsqgen dialect, Database Designer statements, projection designs per scale factor
sql/postgresql/           dsqgen dialect, server settings (tuned.conf), secondary indexes
results/                  one folder per run (timings, monitoring data, environment, summary, metrics)
analysis/                 query plans of both products for the extreme queries, answer check reports
charts/                   comparison charts (SVG, written by ./tpcds.sh compare)
RESULTS.md, COMPARISON.md results and analysis; side-by-side tables of all runs
BLOG.md                   article about the comparison
VIDEO.md, video/          narration script and the animated video (manim)
```
