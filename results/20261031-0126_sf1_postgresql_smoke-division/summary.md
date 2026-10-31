# TPC-DS on PostgreSQL - 20261031-0126_sf1_postgresql_smoke-division

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | 2.6 s | 2.4 s | 5/5 | 0.159 s |
| best of each query | 2.6 s | | 5/5 | 0.159 s (all queries) |

Memory spills to disk (all iterations): none

Total time = wall clock measured by the client around each query (includes connecting and fetching the result). Server time = execution time recorded by PostgreSQL itself (see `server_times.csv`).

## Data generation and load

| Step | Value |
|---|---:|
| dsdgen (22 parallel) | 20.4 s, 1.23 GB flat files |
| COPY, 4 tables in parallel | 4.4 s |
| primary keys and indexes | 4.6 s |
| VACUUM (FREEZE, ANALYZE) | 12.8 s |
| PostgreSQL storage | 2.36 GB (compression 0.5x) |
| of which indexes | 0.63 GB; data without indexes 1.73 GB (compression 0.7x) |

<details><summary>Rows, load time and size per table</summary>

| Table | Rows | Load time | Flat files | Stored | Compression |
|---|---:|---:|---:|---:|---:|
| store_sales | 2,880,404 | 4.3 s | 0.39 GB | 0.53 GB | 0.7x |
| catalog_sales | 1,441,548 | 3.1 s | 0.29 GB | 0.36 GB | 0.8x |
| web_sales | 719,384 | 1.7 s | 0.15 GB | 0.18 GB | 0.8x |
| inventory | 11,745,000 | 0.9 s | 0.22 GB | 0.89 GB | 0.3x |
| store_returns | 287,514 | 0.4 s | 0.03 GB | 0.05 GB | 0.6x |
| catalog_returns | 144,067 | 0.3 s | 0.02 GB | 0.03 GB | 0.7x |
| web_returns | 71,763 | 0.2 s | 0.01 GB | 0.01 GB | 0.7x |
| customer | 100,000 | 0.2 s | 0.01 GB | 0.03 GB | 0.5x |
| customer_demographics | 1,920,800 | 0.5 s | 0.08 GB | 0.22 GB | 0.4x |
| customer_address | 50,000 | 0.1 s | 0.01 GB | 0.01 GB | 0.5x |
| item | 18,000 | 0.2 s | 0.01 GB | 0.01 GB | 0.5x |
| date_dim | 73,049 | 0.1 s | 0.01 GB | 0.01 GB | 0.8x |
| time_dim | 86,400 | 0.1 s | 0.01 GB | 0.01 GB | 0.4x |
| promotion | 300 | 0.1 s | 0.00 GB | 0.00 GB | 0.3x |
| household_demographics | 7,200 | 0.1 s | 0.00 GB | 0.00 GB | 0.2x |
| catalog_page | 11,718 | 0.0 s | 0.00 GB | 0.00 GB | 0.7x |
| web_page | 60 | 0.0 s | 0.00 GB | 0.00 GB | 0.1x |
| call_center | 6 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |
| store | 12 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |
| warehouse | 5 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |
| web_site | 30 | 0.1 s | 0.00 GB | 0.00 GB | 0.1x |
| reason | 35 | 0.1 s | 0.00 GB | 0.00 GB | 0.0x |
| ship_mode | 20 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |
| income_band | 20 | 0.0 s | 0.00 GB | 0.00 GB | 0.0x |

</details>

## Environment

| | |
|---|---|
| Date | 2026-10-30 23:26 UTC |
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
| Scale factor | 1 |
| Toolkit | tpcds-kit @ 5a3a817, queries generated with -QUALIFY Y (fixed spec parameters) |
| Iterations | 1, query timeout 300s, queries: 21 34 73 78 83 |
| dsdgen jobs / load jobs | 22 / 4 tables at a time (PostgreSQL: up to 6 files per table) |

## Per-query times (seconds)

| Query | Iter 1 | Best | Rows |
|---:|---:|---:|---:|
| 21 | 0.104 | 0.104 | 100 |
| 34 | 0.097 | 0.097 | 451 |
| 73 | 0.063 | 0.063 | 9 |
| 78 | 2.247 | 2.247 | 100 |
| 83 | 0.071 | 0.071 | 4 |
