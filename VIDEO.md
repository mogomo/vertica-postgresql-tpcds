# Video: Vertica and PostgreSQL on the same analytic workload

An animated video of about 6 minutes (manim, Rocket Software colours and logo) that tells the
story of [BLOG.md](BLOG.md). The project is in [video/](video/README.md). This file holds
the narration (the words to be recorded), the environment sheet shown on screen, and
every number that appears in the video with its source.

## Narration

Recording: read at a calm pace (about 140 words per minute); each `[SCENE NN — Title]`
block is one chapter of the video. The `ANCHOR:` line is the first sentence of the block
as spoken; the video aligns its chapters to these sentences in the recording. Save the
recording as `video/assets/narration.mp3`.

```
[SCENE 00 — Cold open]
ANCHOR: Couldn't we just run our reports on PostgreSQL?
Couldn't we just run our reports on PostgreSQL? Every analytics team hears that
question sooner or later. PostgreSQL is an excellent database. It is everywhere, and it
costs nothing to start with. So instead of arguing, we measured it.

[SCENE 01 — The test]
ANCHOR: One laptop, two databases, the same data.
One laptop, two databases, the same data. Vertica twenty-six point three, and
PostgreSQL eighteen point six, the current release. The workload is derived from
TPC-DS, the industry's decision-support benchmark: twenty-four tables of a retailer that
sells through stores, a catalog and the web, and ninety-nine analytic queries. We ran it
at twelve gigabytes of raw data, and again at a hundred and two gigabytes. Each product
ran the ninety-nine queries three times, and the best run counts.

[SCENE 02 — Making it fair]
ANCHOR: A comparison is only worth something if the loser cannot claim it was rigged.
A comparison is only worth something if the loser cannot claim it was rigged. So both
products got the same memory budget, about forty gigabytes, and all twenty-two CPU
threads. Each was tuned the way its own documentation recommends. Vertica: projections
designed by its Database Designer. PostgreSQL: settings for analytics, primary keys,
indexes on the fact tables, and a full vacuum and analyze. No materialized views, no
caches, no hints, no hand-tuned queries. We compared the answers of all ninety-nine
queries, row by row. That check caught something: five queries divide one integer by
another. Vertica returns a decimal, PostgreSQL truncates. Unchanged, PostgreSQL would
have answered a different question. And to keep the test finite, every PostgreSQL query
got a time limit: at least one minute, and five times what Vertica needed. A query over
its limit counts with its limit, so PostgreSQL's totals are minimums.

[SCENE 03 — Storage]
ANCHOR: Start with the data itself.
Start with the data itself. Twelve gigabytes of raw text become four point one
gigabytes in Vertica, and twenty-two in PostgreSQL. At a hundred and two gigabytes, it is
thirty-nine against a hundred and forty-seven. Look at one table. Inventory holds
four hundred million rows of four integers. PostgreSQL stores every row with a header
that is larger than the row's own values, and needs another index on top. Vertica
stores each column sorted, and run-length encoding turns long runs of the same value
into a single entry. Eight gigabytes of text become less than one.

[SCENE 04 — Twelve gigabytes]
ANCHOR: Now the queries, at twelve gigabytes.
Now the queries, at twelve gigabytes. Vertica ran all ninety-nine in ninety-four
seconds. PostgreSQL needed at least eight hundred and thirty-seven, and eight queries did
not finish within their limit. But look at the queries one by one. On seven of them,
PostgreSQL was as fast as Vertica, or faster. Twenty-one were within a factor of two. The
typical query took about five times as long.

[SCENE 05 — Where PostgreSQL wins]
ANCHOR: Where does PostgreSQL win?
Where does PostgreSQL win? On selective lookups. Query five reports two weeks of sales.
PostgreSQL walks the index on the date key and reads exactly those two weeks. That is
what indexes are made for, and a fair test has to show it.

[SCENE 06 — Where it breaks]
ANCHOR: And where does it break?
And where does it break? Query one asks for customers whose returns are twenty percent
above their store's average. That average is a correlated subquery. PostgreSQL computes
it again for every single row, scanning the whole intermediate result each time. The work
grows with the square of the data. Vertica turns the same subquery into a join, with one
average per store, computed once. A quarter of a second, against more than ten minutes.
Four queries follow this pattern.

[SCENE 07 — A hundred gigabytes]
ANCHOR: Then we multiplied the data by ten.
Then we multiplied the data by ten. Vertica's time grew seven times, to six hundred and
sixty-four seconds. PostgreSQL finished only forty-three of the ninety-nine queries within
their limits. The reason is memory. Vertica's thirty-nine gigabytes nearly fit into the
laptop's memory. PostgreSQL's hundred and forty-seven do not. Its scans go to disk, and
its joins spill fifty-five gigabytes of intermediate results per run. The typical gap
grows from five times to twenty-one.

[SCENE 08 — What a time limit hides]
ANCHOR: A word about those time limits.
A word about those time limits. A query that was stopped was not measured. More than ten
minutes means at least ten minutes, and nobody knows how much more. Take the worst query
that did finish: query thirty, at twelve gigabytes. Five hundred and eighty seconds on
PostgreSQL, a sixth of a second on Vertica. Three thousand seven hundred times as long.
From one gigabyte to twelve, its time grew ninety-three times, for ten times the data:
the square, just as its plan predicts. At a hundred gigabytes, that points to about
fifteen hours. So we gave it thirty minutes. It did not finish. Every PostgreSQL total
marked at least is a floor, not an estimate.

[SCENE 09 — What it means]
ANCHOR: So, can you run your reports on PostgreSQL?
So, can you run your reports on PostgreSQL? For tens of gigabytes and simple, selective
queries, it can be good enough. For analytic SQL as it is really written, with
subqueries, period-over-period comparisons and joins across the fact tables, Vertica is
faster by orders of magnitude. And the gap grows with your data, because compression
keeps Vertica's working set in memory.

[SCENE 10 — Repeat it yourself]
ANCHOR: One machine, one workload, one query stream.
One machine, one workload, one query stream. Vertica ran as a single node; it is built
to scale out across a cluster, and on more nodes or stronger hardware it would likely do
better still. Transactions and many concurrent users were not part of this test. This is
not an official TPC-DS result. Every script, setting and timing is published, as is, so
you can run it yourself. Vertica, from Rocket Software.
```

About 870 words: about 6 minutes at 140 words per minute, plus the opening and closing logo.

## Environment sheet (shown in scene 01)

| | |
|---|---|
| Machine | Dell Precision 3591 laptop |
| CPU | Intel Core Ultra 7 165H, 16 cores, 22 threads |
| Memory | 64 GB |
| Disk | 1 TB NVMe SSD |
| OS | Ubuntu 26.04 LTS |
| Vertica | 26.3.0, 1 node, Database Designer projections, resource pool 65% of RAM |
| PostgreSQL | 18.6, tuned settings, primary keys + 12 indexes, VACUUM (FREEZE, ANALYZE) |
| Workload | derived from TPC-DS: 24 tables, 99 queries; 12 GB and 102 GB of raw data; best of 3 runs |

## Numbers on screen and their source

| Scene | Number | Source |
|---|---|---|
| 01 | 24 tables, 99 queries, 12.0 GB and 102.5 GB raw data | `generate.info` of the SF10 / SF100 runs |
| 02 | 40 GB, 22 threads; limit = max(60 s, 5 x Vertica) | README "Rules of the comparison", `budgets.csv` |
| 02 | 5 queries with integer division (21, 34, 73, 78, 83) | README "Query changes", `analysis/answers/` |
| 03 | 12.0 -> 4.1 GB (Vertica) / 22.2 GB (PostgreSQL); 102.5 -> 39.2 / 147.5 GB | COMPARISON.md |
| 03 | inventory SF100: 399 M rows, 8.2 GB text, 0.69 GB Vertica, 17.7 GB table + 12.6 GB key PostgreSQL | `load.csv`, `relation_sizes.csv` of the SF100 runs |
| 04 | 94 s vs ≥ 837 s; 8 not finished; 7 faster or equal, 21 within 2x, median 5.1x | COMPARISON.md, RESULTS.md |
| 05 | query 5: 1.53 s vs 3.63 s (SF10), 24.9 s vs 35.0 s (SF100) | COMPARISON.md |
| 06 | query 1: 0.24 s vs > 600 s; the same pattern in queries 1, 6, 30, 81 | RESULTS.md, analysis/README.md |
| 07 | 664 s (x7.1); 43 / 99 finished; 39.2 vs 147.5 GB vs 61 GiB RAM; 55.2 GB temp files per run; median 20.9x | COMPARISON.md, RESULTS.md |
| 08 | query 30: 0.16 s vs 579.6 s at SF10 (x3,668, the largest ratio of a query that finished); SF1 6.2 s -> SF10 579.6 s (x93; Vertica x2.4); SF100 estimate ~15 h; SF100 run with a 30-minute limit: not finished | RESULTS.md "What the time limits mean", `results/*_rerun-600s`, `results/*_q30-1800s` |

## Production

See [video/README.md](video/README.md): draft render without narration (timing estimated
from the words), final render after the recording is in place.
