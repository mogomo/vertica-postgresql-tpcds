# Query plan analysis (SF10)

`postgresql_plans_sf10/qNN.plan` and `vertica_plans_sf10/qNN.plan` hold the plans
(`EXPLAIN`, no execution) of the queries that show the two ends of the comparison, taken
on the SF10 schemas with the benchmark settings after the power runs. They explain the
per-query results in [COMPARISON.md](../COMPARISON.md).

## Where PostgreSQL is as fast as Vertica or faster: selective index lookups

| Query | Vertica | PostgreSQL | Plan |
|---:|---:|---:|---|
| 5 | 3.63 s (SF100: 35.0 s) | 1.53 s (SF100: 24.9 s) | a 14-day date window: bitmap / index scans on the date indexes of store_sales, store_returns, catalog_sales, catalog_returns read only those days |
| 24 | 1.82 s (SF100: 11.9 s) | 0.18 s (SF100: 12.8 s) | from the customers of a few stores through the customer index of store_sales to the primary key of store_returns (index-only scan) |
| 3, 37, 84 | 0.09 - 0.16 s | 0.08 - 0.15 s | small result sets found through indexes |

A B-tree index reads the few rows a query needs and nothing else. Vertica answers these
queries from projections sorted for the workload as a whole, which for these particular
filters still means scanning (compressed) columns.

## Where PostgreSQL falls far behind: correlated subqueries and repeated CTEs

| Query | Vertica SF10 | PostgreSQL SF10 | Plan |
|---:|---:|---:|---|
| 1 | 0.24 s | > 600 s | `ctr_total_return > (select avg(...) from customer_total_return where ctr_store_sk = ...)`: a SubPlan that scans the whole CTE again for every row of the CTE |
| 30, 81 | 0.16 s, 0.20 s | 580 s, 388 s | the same pattern per state |
| 6 | 0.15 s | > 600 s | `i_current_price > 1.2 * (select avg(i_current_price) ... where j.i_category = i.i_category)`: a SubPlan per row |
| 41 | 0.05 s | 18.8 s | `(select count(*) ... where i_manufact = i1.i_manufact) > 0`: a SubPlan per row (see below) |
| 4, 11, 74 | 8.3 s, 4.2 s, 1.6 s | > 600 s | the `year_total` CTE is referenced six (4) or four times: it is computed over all fact rows and then joined to itself through nested loops |

Vertica's plans of the same queries contain only hash and merge joins: query 1 has
three hash joins, one merge join and two group-bys, query 4 eleven hash joins, queries
6 and 41 hash and merge joins - no subquery is executed per row. The correlated
subqueries become joins with an aggregate per correlation key, computed once. The
PostgreSQL planner keeps them as per-row SubPlans, so their cost grows with the square
of the rows involved.

## Query 41: the same meaning, two texts

Vertica does not accept the correlated `count(*)` subquery of query 41, so it runs the
equivalent `exists (select * ...)` form (see README, "Query changes"). PostgreSQL accepts
the original text and was measured with it. Run once with Vertica's text, after the power
runs:

| | Vertica (EXISTS text) | PostgreSQL, original text (power run) | PostgreSQL, EXISTS text (single run) |
|---|---:|---:|---:|
| SF10 | 0.05 s | 18.8 s | 0.03 s |
| SF100 | 0.11 s | > 60 s (time limit) | 0.06 s |

With the `EXISTS` text PostgreSQL plans a hash semi-join instead of a SubPlan per row.
The difference in query 41 is therefore one of query text, not of the engines.

## Answer check reports

`answers/` holds the output of `./tpcds.sh verify` (row-by-row comparison of the query
results, iteration 1 of each run):

- `answers_sf1_before_division_fix.md`: SF1, the first PostgreSQL run; queries 21, 34,
  73, 78 and 83 differ because PostgreSQL truncated integer division;
- `answers_sf1_division_fix.md`: SF1, those five queries with the cast: identical
  (the other queries show as missing: only the five were run);
- `answers_sf10.md`: SF10 power runs; differences only for the 8 queries PostgreSQL did
  not finish within 60 s, NULL position under `LIMIT` (77, 93) and NaN vs NULL (17).
