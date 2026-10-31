# TPC-DS on PostgreSQL - 20261031-0506_sf100_postgresql_tuned

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | ≥ 5782.0 s | 863.3 s | 43/99 | 8.900 s |
| 2 | ≥ 6011.7 s | 616.0 s | 35/99 | 8.938 s |
| 3 | ≥ 6097.0 s | 521.8 s | 32/99 | 8.842 s |
| best of each query | ≥ 5581.1 s | | 43/99 | ≥ 29.929 s (all queries) |

Did not finish within the time limit (counted with the limit, so the totals marked ≥ are lower bounds): q1 (60 s), q4 (333 s), q6 (60 s), q8 (60 s), q10 (60 s), q11 (162 s), q13 (60 s), q14 (296 s), q15 (60 s), q16 (60 s), q17 (60 s), q19 (60 s), q21 (60 s), q22 (81 s), q23 (273 s), q25 (60 s), q27 (60 s), q29 (60 s), q30 (60 s), q33 (60 s), q35 (60 s), q36 (60 s), q38 (60 s), q39 (81 s), q40 (60 s), q43 (60 s), q45 (60 s), q46 (60 s), q47 (60 s), q48 (60 s), q51 (60 s), q56 (60 s), q57 (60 s), q60 (60 s), q64 (60 s), q65 (60 s), q66 (60 s), q67 (235 s), q69 (60 s), q70 (60 s), q71 (60 s), q72 (60 s), q74 (60 s), q75 (136 s), q76 (60 s), q77 (60 s), q78 (329 s), q79 (60 s), q80 (60 s), q81 (60 s), q86 (60 s), q87 (60 s), q89 (60 s), q94 (60 s), q95 (204 s), q97 (83 s)

Amended: queries 41 from a later run, see [amended.md](amended.md).

Memory spills to disk (all iterations): TEMPORARY FILE 228 (165.64 GB)

Total time = wall clock measured by the client around each query (includes connecting and fetching the result). Server time = execution time recorded by PostgreSQL itself (see `server_times.csv`).

## Data generation and load

| Step | Value |
|---|---:|
| dsdgen (22 parallel) | 229.5 s, 102.46 GB flat files |
| COPY, 4 tables in parallel | 499.1 s |
| primary keys and indexes | 1098.6 s |
| VACUUM (FREEZE, ANALYZE) | 1845.0 s |
| PostgreSQL storage | 147.51 GB (compression 0.7x) |
| of which indexes | 33.06 GB; data without indexes 114.45 GB (compression 0.9x) |

<details><summary>Rows, load time and size per table</summary>

| Table | Rows | Load time | Flat files | Stored | Compression |
|---|---:|---:|---:|---:|---:|
| store_sales | 287,997,024 | 481.2 s | 40.67 GB | 52.88 GB | 0.8x |
| catalog_sales | 143,997,065 | 399.8 s | 30.87 GB | 35.87 GB | 0.9x |
| web_sales | 72,001,237 | 228.6 s | 15.39 GB | 18.04 GB | 0.9x |
| inventory | 399,330,000 | 182.9 s | 8.23 GB | 30.28 GB | 0.3x |
| store_returns | 28,795,080 | 78.8 s | 3.46 GB | 5.03 GB | 0.7x |
| catalog_returns | 14,404,374 | 60.4 s | 2.26 GB | 2.93 GB | 0.8x |
| web_returns | 7,197,670 | 20.8 s | 1.05 GB | 1.40 GB | 0.7x |
| customer | 2,000,000 | 3.1 s | 0.27 GB | 0.50 GB | 0.5x |
| customer_demographics | 1,920,800 | 1.4 s | 0.08 GB | 0.22 GB | 0.4x |
| customer_address | 1,000,000 | 1.9 s | 0.11 GB | 0.20 GB | 0.5x |
| item | 204,000 | 2.3 s | 0.06 GB | 0.12 GB | 0.5x |
| date_dim | 73,049 | 0.4 s | 0.01 GB | 0.01 GB | 0.8x |
| time_dim | 86,400 | 0.2 s | 0.01 GB | 0.01 GB | 0.4x |
| promotion | 1,000 | 0.2 s | 0.00 GB | 0.00 GB | 0.4x |
| household_demographics | 7,200 | 0.2 s | 0.00 GB | 0.00 GB | 0.2x |
| catalog_page | 20,400 | 0.2 s | 0.00 GB | 0.00 GB | 0.7x |
| web_page | 2,040 | 0.1 s | 0.00 GB | 0.00 GB | 0.4x |
| call_center | 30 | 0.1 s | 0.00 GB | 0.00 GB | 0.1x |
| store | 402 | 0.1 s | 0.00 GB | 0.00 GB | 0.5x |
| warehouse | 15 | 0.1 s | 0.00 GB | 0.00 GB | 0.0x |
| web_site | 24 | 0.1 s | 0.00 GB | 0.00 GB | 0.1x |
| reason | 55 | 0.1 s | 0.00 GB | 0.00 GB | 0.0x |
| ship_mode | 20 | 0.1 s | 0.00 GB | 0.00 GB | 0.0x |
| income_band | 20 | 0.1 s | 0.00 GB | 0.00 GB | 0.0x |

</details>

## Environment

| | |
|---|---|
| Date | 2026-10-31 05:14 UTC |
| Machine | Dell Inc. Precision 3591 (laptop) |
| CPU | Intel(R) Core(TM) Ultra 7 165H - 1 socket(s), 16 cores, 22 threads, max 5000 MHz, L3 24 MiB (1 instance) |
| Memory | 61.0 GiB RAM, 8.0 GiB swap |
| Storage (database data) | 953.9G NVMe SSD (BC901 NVMe SK hynix 1024GB), ext4 |
| OS | Ubuntu 26.04.1 LTS, kernel 7.0.0-34-generic |
| Power | governor=performance, energy_perf_pref=default, platform_profile=performance, on AC=1 |
| Database | PostgreSQL |
| Version | 18.6 (Ubuntu 18.6-1.pgdg26.04+2) |
| Deployment | single server, row store (heap tables) |
| Server settings | sql/postgresql/tuned.conf: default_statistics_target=1000, effective_cache_size=40GB, hash_mem_multiplier=2, jit=on, max_parallel_workers=22, max_parallel_workers_per_gather=16, random_page_cost=1.1, shared_buffers=10GB, work_mem=256MB |
| Indexes | 36 indexes (24 primary keys), PG_INDEXES=yes |

## Benchmark settings

| | |
|---|---|
| Scale factor | 100 |
| Toolkit | tpcds-kit @ 5a3a817, queries generated with -QUALIFY Y (fixed spec parameters) |
| Iterations | 3, time limit per query from budgets.csv (max(60 s, 5 x Vertica best time)); a query over its limit is not run again |
| dsdgen jobs / load jobs | 22 / 4 tables at a time (PostgreSQL: up to 6 files per table) |

## Per-query times (seconds)

| Query | Iter 1 | Iter 2 | Iter 3 | Best | Rows |
|---:|---:|---:|---:|---:|---:|
| 1 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 2 | 18.208 | 18.717 | 18.711 | 18.208 | 2513 |
| 3 | 11.954 | 4.649 | 5.418 | 4.649 | 100 |
| 4 | TIMEOUT (limit 333) | SKIPPED (limit 333) | SKIPPED (limit 333) | > 333 | 0 |
| 5 | 60.191 | 24.890 | 57.114 | 24.890 | 100 |
| 6 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 7 | 32.179 | 24.316 | 23.856 | 23.856 | 100 |
| 8 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 9 | 50.830 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 50.830 | 0 |
| 10 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 11 | TIMEOUT (limit 162) | SKIPPED (limit 162) | SKIPPED (limit 162) | > 162 | 0 |
| 12 | 12.832 | 36.023 | 10.736 | 10.736 | 100 |
| 13 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 14 | TIMEOUT (limit 296) | SKIPPED (limit 296) | SKIPPED (limit 296) | > 296 | 0 |
| 15 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 16 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 17 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 18 | 4.882 | 35.661 | 34.215 | 4.882 | 100 |
| 19 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 20 | 2.304 | 32.732 | 27.000 | 2.304 | 100 |
| 21 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 22 | TIMEOUT (limit 81) | SKIPPED (limit 81) | SKIPPED (limit 81) | > 81 | 0 |
| 23 | TIMEOUT (limit 273) | SKIPPED (limit 273) | SKIPPED (limit 273) | > 273 | 0 |
| 24 | 23.962 | 12.925 | 12.806 | 12.806 | 14 |
| 25 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 26 | 23.055 | 14.517 | 15.093 | 14.517 | 100 |
| 27 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 28 | 27.309 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 27.309 | 0 |
| 29 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 30 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 31 | 27.575 | 33.536 | 29.771 | 27.575 | 275 |
| 32 | 57.257 | 24.085 | TIMEOUT (limit 60) | 24.085 | 0 |
| 33 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 34 | 30.631 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 30.631 | 0 |
| 35 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 36 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 37 | 2.016 | 1.530 | 1.216 | 1.216 | 5 |
| 38 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 39 | TIMEOUT (limit 81) | SKIPPED (limit 81) | SKIPPED (limit 81) | > 81 | 0 |
| 40 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 41 | 0.144 | 0.098 | 0.089 | 0.089 | 100 |
| 42 | 18.368 | 36.005 | TIMEOUT (limit 60) | 18.368 | 0 |
| 43 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 44 | 13.586 | 20.018 | 22.950 | 13.586 | 10 |
| 45 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 46 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 47 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 48 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 49 | 14.923 | 14.410 | 14.000 | 14.000 | 100 |
| 50 | 40.927 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 40.927 | 0 |
| 51 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 52 | 13.229 | 47.503 | 52.115 | 13.229 | 100 |
| 53 | 13.055 | 52.228 | TIMEOUT (limit 60) | 13.055 | 0 |
| 54 | 46.260 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 46.260 | 0 |
| 55 | 39.918 | 31.971 | 15.448 | 15.448 | 100 |
| 56 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 57 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 58 | 8.316 | 32.566 | 35.408 | 8.316 | 100 |
| 59 | 13.051 | 13.970 | 14.692 | 13.051 | 100 |
| 60 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 61 | 1.105 | 1.090 | 1.104 | 1.090 | 1 |
| 62 | 8.705 | 5.984 | 6.011 | 5.984 | 100 |
| 63 | 23.104 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 23.104 | 0 |
| 64 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 65 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 66 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 67 | TIMEOUT (limit 235) | SKIPPED (limit 235) | SKIPPED (limit 235) | > 235 | 0 |
| 68 | 45.376 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 45.376 | 0 |
| 69 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 70 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 71 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 72 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 73 | 39.146 | 6.830 | 39.389 | 6.830 | 170 |
| 74 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 75 | TIMEOUT (limit 136) | SKIPPED (limit 136) | SKIPPED (limit 136) | > 136 | 0 |
| 76 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 77 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 78 | TIMEOUT (limit 329) | SKIPPED (limit 329) | SKIPPED (limit 329) | > 329 | 0 |
| 79 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 80 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 81 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 82 | 3.347 | 4.169 | 3.300 | 3.300 | 18 |
| 83 | 10.879 | 19.288 | 19.212 | 10.879 | 100 |
| 84 | 1.458 | 1.682 | 1.720 | 1.458 | 100 |
| 85 | 8.607 | 6.482 | 5.294 | 5.294 | 50 |
| 86 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 87 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 88 | 34.166 | TIMEOUT (limit 60) | SKIPPED (limit 60) | 34.166 | 0 |
| 89 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 90 | 7.831 | 5.046 | 4.797 | 4.797 | 1 |
| 91 | 1.500 | 0.627 | 0.530 | 0.530 | 30 |
| 92 | 19.662 | 2.818 | 2.649 | 2.649 | 1 |
| 93 | 13.462 | 14.770 | 12.169 | 12.169 | 100 |
| 94 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 95 | TIMEOUT (limit 204) | SKIPPED (limit 204) | SKIPPED (limit 204) | > 204 | 0 |
| 96 | 19.239 | 15.244 | 15.362 | 15.244 | 1 |
| 97 | TIMEOUT (limit 83) | SKIPPED (limit 83) | SKIPPED (limit 83) | > 83 | 0 |
| 98 | 4.699 | 5.415 | 5.983 | 4.699 | 30573 |
| 99 | 15.899 | 15.585 | 14.951 | 14.951 | 100 |
