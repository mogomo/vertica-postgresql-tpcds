# Amended: queries 41

Query 41 runs on both products with the same text: the equivalent `exists (select * ...)` form that Vertica needs (README, "Query changes"). The power run had given PostgreSQL the original `count(*) > 0` text; query 41 was run again with the identical text, 3 iterations, same time limit.

The rows of these queries come from run `20261031-1009_sf10_postgresql_q41-exists` (same database, same settings, same time limits); the original rows of this run are kept in `timings_original.csv` and `server_times_original.csv`.

| Iteration | Query | Original | Amended |
|---:|---:|---:|---:|
| 1 | 41 | 20.548 s ok | 0.114 s ok |
| 2 | 41 | 19.135 s ok | 0.066 s ok |
| 3 | 41 | 18.766 s ok | 0.071 s ok |
