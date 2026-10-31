# TPC-DS on PostgreSQL - 20261031-0145_sf10_postgresql_tuned

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | ≥ 860.9 s | 376.9 s | 91/99 | 1.480 s |
| 2 | ≥ 837.5 s | 353.9 s | 91/99 | 1.293 s |
| 3 | ≥ 837.1 s | 353.5 s | 91/99 | 1.320 s |
| best of each query | ≥ 828.1 s | | 91/99 | ≥ 1.710 s (all queries) |

Did not finish within the time limit (counted with the limit, so the totals marked ≥ are lower bounds): q1 (60 s), q4 (60 s), q6 (60 s), q11 (60 s), q14 (60 s), q30 (60 s), q74 (60 s), q81 (60 s)

Amended: queries 41 from a later run, see [amended.md](amended.md).

Memory spills to disk (all iterations): TEMPORARY FILE 54 (29.85 GB)

Total time = wall clock measured by the client around each query (includes connecting and fetching the result). Server time = execution time recorded by PostgreSQL itself (see `server_times.csv`).

## Data generation and load

| Step | Value |
|---|---:|
| dsdgen (22 parallel) | 56.0 s, 12.00 GB flat files |
| COPY, 4 tables in parallel | 30.4 s |
| primary keys and indexes | 63.2 s |
| VACUUM (FREEZE, ANALYZE) | 97.5 s |
| PostgreSQL storage | 22.23 GB (compression 0.5x) |
| of which indexes | 6.33 GB; data without indexes 15.90 GB (compression 0.8x) |

<details><summary>Rows, load time and size per table</summary>

| Table | Rows | Load time | Flat files | Stored | Compression |
|---|---:|---:|---:|---:|---:|
| store_sales | 28,800,991 | 24.2 s | 3.97 GB | 5.29 GB | 0.8x |
| catalog_sales | 14,401,261 | 18.7 s | 3.02 GB | 3.60 GB | 0.8x |
| web_sales | 7,197,566 | 30.3 s | 1.50 GB | 1.81 GB | 0.8x |
| inventory | 133,110,000 | 22.1 s | 2.63 GB | 10.09 GB | 0.3x |
| store_returns | 2,875,432 | 2.4 s | 0.34 GB | 0.51 GB | 0.7x |
| catalog_returns | 1,439,749 | 1.3 s | 0.22 GB | 0.30 GB | 0.7x |
| web_returns | 719,217 | 1.8 s | 0.10 GB | 0.14 GB | 0.7x |
| customer | 500,000 | 1.4 s | 0.07 GB | 0.13 GB | 0.5x |
| customer_demographics | 1,920,800 | 0.7 s | 0.08 GB | 0.22 GB | 0.4x |
| customer_address | 250,000 | 0.4 s | 0.03 GB | 0.05 GB | 0.5x |
| item | 102,000 | 0.4 s | 0.03 GB | 0.06 GB | 0.5x |
| date_dim | 73,049 | 0.2 s | 0.01 GB | 0.01 GB | 0.8x |
| time_dim | 86,400 | 0.1 s | 0.01 GB | 0.01 GB | 0.4x |
| promotion | 500 | 0.1 s | 0.00 GB | 0.00 GB | 0.4x |
| household_demographics | 7,200 | 0.0 s | 0.00 GB | 0.00 GB | 0.2x |
| catalog_page | 12,000 | 0.0 s | 0.00 GB | 0.00 GB | 0.7x |
| web_page | 200 | 0.0 s | 0.00 GB | 0.00 GB | 0.2x |
| call_center | 24 | 0.0 s | 0.00 GB | 0.00 GB | 0.1x |
| store | 102 | 0.0 s | 0.00 GB | 0.00 GB | 0.3x |
| warehouse | 10 | 0.1 s | 0.00 GB | 0.00 GB | 0.0x |
| web_site | 42 | 0.0 s | 0.00 GB | 0.00 GB | 0.1x |
| reason | 45 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |
| ship_mode | 20 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |
| income_band | 20 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |

</details>

## Environment

| | |
|---|---|
| Date | 2026-10-31 00:12 UTC |
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
| Scale factor | 10 |
| Toolkit | tpcds-kit @ 5a3a817, queries generated with -QUALIFY Y (fixed spec parameters) |
| Iterations | 3, time limit per query from budgets.csv (max(60 s, 5 x Vertica best time)); a query over its limit is not run again |
| dsdgen jobs / load jobs | 22 / 4 tables at a time (PostgreSQL: up to 6 files per table) |

## Per-query times (seconds)

| Query | Iter 1 | Iter 2 | Iter 3 | Best | Rows |
|---:|---:|---:|---:|---:|---:|
| 1 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 2 | 1.488 | 1.310 | 1.296 | 1.296 | 2513 |
| 3 | 0.078 | 0.083 | 0.095 | 0.078 | 100 |
| 4 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 5 | 1.530 | 1.656 | 1.710 | 1.530 | 100 |
| 6 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 7 | 1.879 | 0.335 | 0.334 | 0.334 | 100 |
| 8 | 1.637 | 0.672 | 0.683 | 0.672 | 8 |
| 9 | 4.674 | 4.183 | 4.392 | 4.183 | 1 |
| 10 | 7.660 | 7.525 | 7.624 | 7.525 | 100 |
| 11 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 12 | 0.215 | 0.210 | 0.221 | 0.210 | 100 |
| 13 | 1.061 | 1.089 | 1.288 | 1.061 | 1 |
| 14 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 15 | 7.662 | 1.774 | 1.830 | 1.774 | 100 |
| 16 | 1.622 | 1.477 | 1.515 | 1.477 | 1 |
| 17 | 2.051 | 2.136 | 2.251 | 2.051 | 3 |
| 18 | 0.494 | 0.445 | 0.460 | 0.445 | 100 |
| 19 | 0.478 | 0.532 | 0.537 | 0.478 | 100 |
| 20 | 0.363 | 0.411 | 0.425 | 0.363 | 100 |
| 21 | 3.527 | 2.085 | 2.112 | 2.085 | 100 |
| 22 | 27.659 | 28.284 | 28.138 | 27.659 | 100 |
| 23 | 44.203 | 39.158 | 39.076 | 39.076 | 2 |
| 24 | 0.194 | 0.188 | 0.182 | 0.182 | 1 |
| 25 | 3.172 | 3.012 | 2.883 | 2.883 | 4 |
| 26 | 6.318 | 0.295 | 0.299 | 0.295 | 100 |
| 27 | 3.874 | 3.764 | 3.982 | 3.764 | 100 |
| 28 | 3.293 | 3.426 | 3.584 | 3.293 | 1 |
| 29 | 2.038 | 2.457 | 2.051 | 2.038 | 3 |
| 30 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 31 | 16.251 | 16.977 | 16.733 | 16.251 | 288 |
| 32 | 0.283 | 0.277 | 0.304 | 0.277 | 1 |
| 33 | 0.916 | 0.915 | 0.929 | 0.915 | 100 |
| 34 | 0.697 | 0.727 | 0.742 | 0.697 | 4569 |
| 35 | 5.729 | 6.003 | 6.095 | 5.729 | 100 |
| 36 | 3.615 | 3.643 | 3.670 | 3.615 | 100 |
| 37 | 0.254 | 0.090 | 0.100 | 0.090 | 3 |
| 38 | 6.590 | 6.581 | 6.934 | 6.581 | 1 |
| 39 | 28.061 | 28.982 | 28.908 | 28.061 | 1715 |
| 40 | 0.497 | 0.449 | 0.496 | 0.449 | 100 |
| 41 | 0.114 | 0.066 | 0.071 | 0.066 | 42 |
| 42 | 0.434 | 0.459 | 0.601 | 0.434 | 11 |
| 43 | 1.244 | 1.185 | 1.214 | 1.185 | 17 |
| 44 | 0.732 | 0.795 | 0.801 | 0.732 | 0 |
| 45 | 3.709 | 3.568 | 3.444 | 3.444 | 36 |
| 46 | 1.747 | 1.821 | 1.834 | 1.747 | 100 |
| 47 | 13.079 | 13.139 | 14.620 | 13.079 | 100 |
| 48 | 1.893 | 1.993 | 2.026 | 1.893 | 1 |
| 49 | 0.787 | 0.382 | 0.387 | 0.382 | 45 |
| 50 | 0.358 | 0.373 | 0.537 | 0.358 | 51 |
| 51 | 6.244 | 6.311 | 6.444 | 6.244 | 100 |
| 52 | 0.434 | 0.454 | 0.478 | 0.434 | 100 |
| 53 | 0.687 | 0.741 | 0.780 | 0.687 | 100 |
| 54 | 0.362 | 0.253 | 0.248 | 0.248 | 0 |
| 55 | 0.302 | 0.311 | 0.325 | 0.302 | 100 |
| 56 | 1.271 | 1.083 | 1.111 | 1.083 | 100 |
| 57 | 7.092 | 7.504 | 7.121 | 7.092 | 100 |
| 58 | 0.279 | 0.276 | 0.285 | 0.276 | 5 |
| 59 | 2.366 | 2.398 | 2.513 | 2.366 | 100 |
| 60 | 3.995 | 4.169 | 4.106 | 3.995 | 100 |
| 61 | 0.130 | 0.139 | 0.145 | 0.130 | 1 |
| 62 | 0.493 | 0.513 | 0.516 | 0.493 | 100 |
| 63 | 0.682 | 0.731 | 0.779 | 0.682 | 100 |
| 64 | 1.696 | 1.735 | 1.735 | 1.696 | 20 |
| 65 | 6.847 | 7.225 | 6.769 | 6.769 | 100 |
| 66 | 1.122 | 1.165 | 1.125 | 1.122 | 10 |
| 67 | 34.521 | 34.458 | 34.774 | 34.458 | 100 |
| 68 | 0.437 | 0.451 | 0.460 | 0.437 | 100 |
| 69 | 4.867 | 1.410 | 1.417 | 1.410 | 100 |
| 70 | 3.469 | 3.420 | 3.599 | 3.420 | 8 |
| 71 | 0.905 | 0.925 | 0.937 | 0.905 | 10477 |
| 72 | 3.774 | 1.895 | 1.886 | 1.886 | 100 |
| 73 | 0.328 | 0.301 | 0.333 | 0.301 | 43 |
| 74 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 75 | 7.540 | 8.228 | 6.940 | 6.940 | 100 |
| 76 | 16.659 | 15.811 | 15.065 | 15.065 | 100 |
| 77 | 0.792 | 0.795 | 0.793 | 0.792 | 100 |
| 78 | 8.503 | 8.318 | 8.302 | 8.302 | 100 |
| 79 | 1.286 | 1.198 | 1.113 | 1.113 | 100 |
| 80 | 1.896 | 1.984 | 1.829 | 1.829 | 100 |
| 81 | TIMEOUT (limit 60) | SKIPPED (limit 60) | SKIPPED (limit 60) | > 60 | 0 |
| 82 | 0.359 | 0.158 | 0.148 | 0.148 | 10 |
| 83 | 0.214 | 0.224 | 0.228 | 0.214 | 100 |
| 84 | 0.155 | 0.163 | 0.146 | 0.146 | 100 |
| 85 | 0.396 | 0.316 | 0.317 | 0.316 | 14 |
| 86 | 1.404 | 1.450 | 1.471 | 1.404 | 100 |
| 87 | 6.649 | 6.835 | 6.742 | 6.649 | 1 |
| 88 | 3.748 | 4.130 | 4.055 | 3.748 | 1 |
| 89 | 1.522 | 1.629 | 1.652 | 1.522 | 100 |
| 90 | 0.404 | 0.417 | 0.418 | 0.404 | 1 |
| 91 | 0.169 | 0.163 | 0.251 | 0.163 | 13 |
| 92 | 0.209 | 0.191 | 0.192 | 0.191 | 1 |
| 93 | 0.274 | 0.277 | 0.276 | 0.274 | 100 |
| 94 | 3.726 | 3.716 | 3.656 | 3.656 | 1 |
| 95 | 20.827 | 20.915 | 20.892 | 20.827 | 1 |
| 96 | 0.606 | 0.683 | 0.652 | 0.606 | 1 |
| 97 | 4.949 | 5.408 | 4.962 | 4.949 | 1 |
| 98 | 0.725 | 0.732 | 0.755 | 0.725 | 15070 |
| 99 | 0.952 | 0.950 | 0.935 | 0.935 | 100 |
