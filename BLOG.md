# Vertica and PostgreSQL on the same analytic workload: 99 queries, one laptop, measured

"Couldn't we just run our reports on PostgreSQL?" Every analytics team hears this
question sooner or later. PostgreSQL is an excellent database, it is everywhere, and it
costs nothing to start with. So instead of arguing, I measured it: the same
decision-support workload, the same data, the same machine, once with Vertica and once
with PostgreSQL, each set up the way its documentation recommends. This article explains
how the test was made fair, what came out, and why the two products behave so
differently. Every script, setting and raw timing is published, so you can repeat the
test yourself.

## The short version

| | Vertica 26.3 | PostgreSQL 18.6 |
|---|---:|---:|
| **12 GB of raw data (scale factor 10)** | | |
| 99 queries, best of 3 runs | **94 s** | **≥ 856 s** |
| Queries finished within their time limit | 99 | 91 |
| Data on disk | **4.1 GB** | **22.2 GB** |
| **102 GB of raw data (scale factor 100)** | | |
| 99 queries, best of 3 runs | **664 s** | **≥ 5,842 s** |
| Queries finished within their time limit | 99 | 42 |
| Data on disk | **39.2 GB** | **147.5 GB** |

"≥" means "at least": PostgreSQL queries that ran over their time limit were stopped and
counted with the limit, so the real figures are higher.

Three findings stand out:

1. **At 12 GB, PostgreSQL holds its own on simple, selective queries** - it was as fast
   as Vertica or faster on 7 of the 99 queries, and within a factor of two on 20. The
   median query took about 5 times as long.
2. **A specific class of queries breaks it.** Correlated subqueries and large repeated
   sub-results take Vertica a fraction of a second and PostgreSQL minutes - or longer
   than we were willing to wait.
3. **At 102 GB, storage decides.** Vertica keeps the data in 39 GB, which nearly fits in
   the laptop's 64 GB of memory. PostgreSQL needs 147 GB, reads from disk, spills 55 GB
   of intermediate results per run, and finishes only 42 of the 99 queries within their
   limits. Its median gap grows from 5x to 24x.

## The test setup

- **Machine:** a Dell Precision 3591 laptop with an Intel Core Ultra 7 165H (16 cores,
  22 threads), 64 GB of RAM and a 1 TB NVMe SSD, running Ubuntu 26.04 LTS. OS settings
  for an analytic database (performance CPU governor, disk readahead, low swappiness)
  applied for both products.
- **Vertica 26.3.0** Community Edition, one node.
- **PostgreSQL 18.6**, the current major release, from the PostgreSQL community package
  repository. (Version 19 was left out on purpose: the comparison should reflect what
  runs in production today.)
- **Data and queries:** generated with the TPC-DS toolkit: 24 tables (7 fact tables and
  17 dimensions of a retailer selling through stores, a catalog and the web) and its 99
  queries with the fixed parameters of the specification. Scale factor 10 (12 GB of raw
  data, 29 million rows in the largest fact table) and scale factor 100 (102 GB,
  288 million rows).
- **Procedure:** a power run: the 99 queries one after another in one session, three
  times; the best of the three runs counts. Only one database runs at a time, and the
  OS file cache is emptied before each product starts.

## Making it fair

A comparison is only worth reading if the loser could not reasonably claim it was set up
to lose. These were the rules:

1. **Same hardware, same budget.** Each product gets about 40 GB of memory and all 22
   CPU threads. Vertica: a resource pool of 65% of RAM for the query session.
   PostgreSQL: 10 GB of shared buffers, 256 MB of work memory per sort or hash
   operation, the rest as file cache, and parallel query with up to 16 workers per
   query.
2. **Each product tuned the way its documentation recommends - and no further.**
   Vertica: its Database Designer creates the physical design (projections) for the 99
   queries on a sample of the data, before the load; statistics afterwards. PostgreSQL:
   settings for an analytic workload on SSD (planner cost settings, I/O concurrency,
   JIT, a statistics target ten times the default), the primary keys of the TPC-DS
   schema, B-tree indexes on the date and customer keys of every fact table, and
   `VACUUM (FREEZE, ANALYZE)` after the load. Core PostgreSQL, no extensions.
3. **No shortcuts for either.** No materialized views or pre-aggregated projections, no
   result caches, no per-query hints, no hand-optimized queries. The queries were changed
   only where a product would not accept the syntax or would compute a different answer;
   every change is listed in the repository.
4. **Same answers.** The results of the 99 queries were compared row by row between the
   two products. They match, apart from documented differences such as where NULLs land
   in an `ORDER BY ... LIMIT`.
5. **Time limits, stated openly.** Each PostgreSQL query gets `max(60 s, 5 x Vertica's
   best time for that query)`: at least a minute, and five times what Vertica needed. A
   query over its limit is stopped and counted *with its limit*, so every PostgreSQL
   total that contains one is a lower bound. At scale factor 10 every query that hit its
   limit was run again with 10 minutes, to show how far off it was.

One detail from rule 4 is worth telling, because it is exactly the kind of thing that
silently breaks comparisons. Five TPC-DS queries compute ratios of two integer columns,
e.g. `hd_dep_count / hd_vehicle_count > 1.2`. Vertica divides integers as decimals;
PostgreSQL truncates integer division. Run unchanged, PostgreSQL would have returned
different rows - and been timed on a different question. The answer check caught it,
and PostgreSQL got a cast that restores the intended ratio.

## Load and storage

| | Vertica SF10 | PostgreSQL SF10 | Vertica SF100 | PostgreSQL SF100 |
|---|---:|---:|---:|---:|
| Raw data (flat files) | 12.0 GB | 12.0 GB | 102.5 GB | 102.5 GB |
| Bulk load (COPY) | 33 s | 30 s | 388 s | 499 s |
| Primary keys and indexes | - | 63 s | - | 1,099 s |
| Statistics | 3.5 s | 98 s | 11 s | 1,845 s |
| **Size on disk** | **4.1 GB** | **22.2 GB** | **39.2 GB** | **147.5 GB** |
| of which indexes | - | 6.3 GB | - | 33.1 GB |

The raw load speed is similar. The work around it is not: PostgreSQL then builds its
keys and indexes and runs `VACUUM (FREEZE, ANALYZE)` - at 102 GB that is 49 minutes on
top of an 8-minute load. Vertica writes its sorted, compressed projections during the
load and collects statistics in seconds.

The size difference is the more important one. Vertica stores the data at 2.6-3x
compression - including the extra projections its Database Designer added for the
queries. PostgreSQL stores it *larger* than the raw text, before any index. The
`inventory` table shows why: at scale factor 100 it holds 399 million rows of four
integers (date, item, warehouse, quantity), 8.2 GB as text. PostgreSQL needs a 17.7 GB
table - every row carries a header of about 24 bytes plus a 4-byte pointer, more than
its four values - and a 12.6 GB primary key index. Vertica stores it in **0.7 GB**:
sorted by date, item and warehouse, those columns compress to almost nothing with
run-length encoding.

Size matters beyond the disk bill. Every query that scans a table reads its stored size,
and whether the working set fits in memory decides whether a query runs at memory speed
or at disk speed. More on that below.

## The 99 queries at scale factor 10

Vertica ran all 99 queries in 94 s. PostgreSQL needed at least 856 s; 8 queries did not
finish within their 60-second limit.

Across the 91 queries both finished, the ratio PostgreSQL / Vertica:

| | Queries |
|---|---:|
| PostgreSQL as fast or faster | 7 |
| within 2x | 20 |
| within 5x | 43 |
| within 10x | 69 |
| 10x or more | 22 |

**Where PostgreSQL wins: selective index lookups.** Query 5 reports sales and returns
for a 14-day window. PostgreSQL's plan goes through the B-tree indexes on the date keys
and reads only those 14 days: 1.5 s against Vertica's 3.6 s - and it stays ahead at
scale factor 100 (24.9 s against 35.0 s). Query 24 starts from the customers of a few
stores and follows two indexes; PostgreSQL answers in 0.18 s, Vertica in 1.8 s. This is
what indexes are made for, and a fair comparison has to show it.

**Where it breaks: correlated subqueries and repeated sub-results.** These are the
queries that did not finish within a minute, rerun with a 10-minute limit:

| Query | What it asks | Vertica | PostgreSQL |
|---:|---|---:|---:|
| 1 | customers whose returns are 20% above their store's average | 0.24 s | > 10 min |
| 6 | states with many purchases of items priced 20% above their category's average | 0.15 s | > 10 min |
| 30 | customers whose web returns are 20% above their state's average | 0.16 s | 580 s |
| 81 | the same for catalog returns | 0.20 s | 388 s |
| 4, 11, 74 | customers whose spending grew faster in one channel than in another, year over year | 1.6 - 8.3 s | > 10 min |
| 14 | items sold in all three channels, by channel | 6.7 s | 121 s |

The query plans show why ([analysis](analysis/README.md)). In query 1,
"above their store's average" is a correlated subquery:
`ctr_total_return > (select avg(...) ... where ctr2.ctr_store_sk = ctr1.ctr_store_sk)`.
PostgreSQL executes it as a *SubPlan*: for every row of the outer result it scans the
whole intermediate result again to compute that store's average - the work grows with
the square of the rows. Vertica's optimizer turns the same subquery into a join with
one pre-computed average per store; its plan contains nothing but hash and merge joins,
and the query takes a quarter of a second. Queries 6, 30, 41 and 81 follow the same
pattern. Queries 4, 11 and 74 build a large per-customer, per-year summary and join it
to itself several times; PostgreSQL does that with nested loops, Vertica with hash joins.

How large the effect of the query text alone can be shows in query 41. Vertica does not
accept its correlated `count(*) > 0` subquery, so - as the rules allow - it runs the
equivalent `EXISTS` form. PostgreSQL accepts and ran the original text: 18.8 s, against
0.05 s for Vertica. Given the `EXISTS` text, PostgreSQL plans a semi-join and answers in
0.03 s. So in query 41 the difference comes from the query text, not the engine - and
it is listed as such in the results.

## The 99 queries at scale factor 100

At ten times the data, Vertica's total time grew 7.1 times - from 94 s to 664 s.
PostgreSQL finished only 42 of the 99 queries within their limits (60 s for most,
up to 333 s for the queries Vertica itself needed more than 12 s for). On the 42 queries
it finished at both scale factors its time grew 14.6 times, Vertica's 6.6 times.

| Queries both finished, PostgreSQL / Vertica | SF10 (91) | SF100 (42) |
|---|---:|---:|
| PostgreSQL as fast or faster | 7 | 1 |
| within 2x | 20 | 3 |
| within 10x | 69 | 14 |
| median | 5.1x | 24.3x |

The reason is memory. At scale factor 10 both data sets fit into RAM. At scale factor
100, Vertica's 39 GB still nearly fits into the 61 GiB the laptop can use; PostgreSQL's
147 GB does not, so its scans read from disk, and its hash joins and sorts wrote 55 GB of
temporary files per run. A side effect showed in the timings themselves: eight
PostgreSQL queries that took 23-51 s in the first run went over 60 s in the second,
because the previous queries had pushed different tables out of the file cache. Vertica's
three runs differed by less than 0.2%.

## Why the difference

The measurements line up with the architecture of the two products:

- **Column storage and compression.** An analytic query typically touches a handful of
  the 20-30 columns of a fact table. Vertica reads only those columns, encoded
  (run-length, delta, dictionary) and compressed. PostgreSQL stores whole rows, so a scan
  reads every column of every row it visits - and the rows are larger than the raw data.
- **Sorted projections.** Vertica stores each table sorted, and where its Database
  Designer sees a benefit, more than once with different sort orders. Range filters,
  merge joins and group-bys on those columns become cheap.
- **A query optimizer for analytic SQL.** Correlated subqueries become joins; large
  intermediate results are joined with hash joins across all cores. PostgreSQL's planner
  is excellent for the queries it was built around - transactions and selective lookups -
  and leaves some analytic query shapes as per-row loops.
- **Indexes help where they help.** They made PostgreSQL competitive on selective
  queries. They also cost 33 GB of disk and 18 minutes of load time at scale factor 100,
  and do little for queries that aggregate large parts of a fact table.

## What this means if you run Vertica

- For reporting on tens of gigabytes with simple, selective queries, PostgreSQL can be
  good enough - this test shows where.
- Analytic SQL as it is actually written - subqueries against aggregates, period-over-
  period comparisons, many joins over the fact tables - is where Vertica's optimizer and
  execution engine pay off, by two to three orders of magnitude on individual queries.
- The gap widens with data size. Compression keeps Vertica's working set in memory far
  longer; at 100 GB on the same laptop, PostgreSQL ran out of memory to cache its data
  and could not finish most of the workload in five times Vertica's time.
- The less obvious costs add up too: nearly four times the disk space, and nearly an hour of
  index builds and vacuuming after every 100 GB load.

## Limitations

- One workload (decision support), one machine, one node per product, one query stream.
  Transactions, many concurrent users and continuous data changes were not measured -
  that is where PostgreSQL is strong.
- General best-practice tuning for both, not expert tuning per query. A PostgreSQL
  specialist could make individual queries faster, for example by rewriting the
  correlated subqueries by hand - as the query 41 example shows. The test deliberately
  ran the queries as written.
- Queries that hit their time limit are counted with the limit, so the PostgreSQL totals
  are lower bounds.
- This is not an official TPC-DS result (see below).

## Repeat it yourself

Everything is in the repository: installing PostgreSQL, generating the data, the Vertica
physical design, both loads, the power runs with time limits, the answer check, the query
plans, and the raw timings and monitoring data of every run. One command per scale
factor runs both products end to end, and every step has a time limit.

---

*This is not an official TPC-DS benchmark result. The workload is derived from TPC-DS
(the TPC-DS toolkit generates the data and the queries), but the TPC run rules -
throughput test, data maintenance, auditing, pricing - were not followed, and the
numbers cannot be compared with published TPC-DS results. TPC-DS is a trademark of the
Transaction Processing Performance Council.*
