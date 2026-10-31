# TPC-DS on PostgreSQL - 20261031-1009_sf10_postgresql_q41-exists

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | 0.1 s | 0.1 s | 1/1 | 0.114 s |
| 2 | 0.1 s | 0.0 s | 1/1 | 0.066 s |
| 3 | 0.1 s | 0.0 s | 1/1 | 0.071 s |
| best of each query | 0.1 s | | 1/1 | 0.066 s (all queries) |

Memory spills to disk (all iterations): none

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
| Date | 2026-10-31 08:09 UTC |
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
| Iterations | 3, time limit per query from budgets.csv (max(60 s, 5 x Vertica best time)); a query over its limit is not run again, queries: 41 |
| dsdgen jobs / load jobs | 22 / 4 tables at a time (PostgreSQL: up to 6 files per table) |

## Per-query times (seconds)

| Query | Iter 1 | Iter 2 | Iter 3 | Best | Rows |
|---:|---:|---:|---:|---:|---:|
| 41 | 0.114 | 0.066 | 0.071 | 0.066 | 42 |
