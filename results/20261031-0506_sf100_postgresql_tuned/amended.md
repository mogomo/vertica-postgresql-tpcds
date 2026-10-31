# Amended: queries 41

Query 41 runs on both products with the same text: the equivalent `exists (select * ...)` form that Vertica needs (README, "Query changes"). The power run had given PostgreSQL the original `count(*) > 0` text; query 41 was run again with the identical text, 3 iterations, same time limit.

The rows of these queries come from run `20261031-1010_sf100_postgresql_q41-exists` (same database, same settings, same time limits); the original rows of this run are kept in `timings_original.csv` and `server_times_original.csv`.

| Iteration | Query | Original | Amended |
|---:|---:|---:|---:|
| 1 | 41 | 60.051 s timeout | 0.144 s ok |
| 2 | 41 | 60.000 s skipped | 0.098 s ok |
| 3 | 41 | 60.000 s skipped | 0.089 s ok |
