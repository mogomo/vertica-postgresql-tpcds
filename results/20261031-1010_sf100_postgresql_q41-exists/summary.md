# TPC-DS on PostgreSQL - 20261031-1010_sf100_postgresql_q41-exists

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | 0.1 s | 0.1 s | 1/1 | 0.144 s |
| 2 | 0.1 s | 0.1 s | 1/1 | 0.098 s |
| 3 | 0.1 s | 0.1 s | 1/1 | 0.089 s |
| best of each query | 0.1 s | | 1/1 | 0.089 s (all queries) |

Memory spills to disk (all iterations): none

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
| Date | 2026-10-31 08:10 UTC |
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
| Iterations | 3, time limit per query from budgets.csv (max(60 s, 5 x Vertica best time)); a query over its limit is not run again, queries: 41 |
| dsdgen jobs / load jobs | 22 / 4 tables at a time (PostgreSQL: up to 6 files per table) |

## Per-query times (seconds)

| Query | Iter 1 | Iter 2 | Iter 3 | Best | Rows |
|---:|---:|---:|---:|---:|---:|
| 41 | 0.144 | 0.098 | 0.089 | 0.089 | 100 |
