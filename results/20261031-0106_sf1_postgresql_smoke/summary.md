# TPC-DS on PostgreSQL - 20261031-0106_sf1_postgresql_smoke

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | ≥ 1109.7 s | 506.0 s | 97/99 | 0.288 s |
| best of each query | ≥ 1109.7 s | | 97/99 | ≥ 0.331 s (all queries) |

Did not finish within the time limit (counted with the limit, so the totals marked ≥ are lower bounds): q4 (300 s), q11 (300 s)

Memory spills to disk (all iterations): TEMPORARY FILE 1 (0.15 GB)

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
| Date | 2026-10-30 23:25 UTC |
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
| Iterations | 1, query timeout 300s |
| dsdgen jobs / load jobs | 22 / 4 tables at a time (PostgreSQL: up to 6 files per table) |

## Per-query times (seconds)

| Query | Iter 1 | Best | Rows |
|---:|---:|---:|---:|
| 1 | 89.401 | 89.401 | 100 |
| 2 | 0.220 | 0.220 | 2513 |
| 3 | 0.048 | 0.048 | 38 |
| 4 | TIMEOUT (limit 300) | > 300 | 0 |
| 5 | 0.157 | 0.157 | 100 |
| 6 | 47.668 | 47.668 | 41 |
| 7 | 0.400 | 0.400 | 100 |
| 8 | 0.105 | 0.105 | 0 |
| 9 | 1.431 | 1.431 | 1 |
| 10 | 0.458 | 0.458 | 2 |
| 11 | TIMEOUT (limit 300) | > 300 | 0 |
| 12 | 0.073 | 0.073 | 100 |
| 13 | 0.157 | 0.157 | 1 |
| 14 | 12.819 | 12.819 | 200 |
| 15 | 0.118 | 0.118 | 100 |
| 16 | 1.195 | 1.195 | 1 |
| 17 | 0.172 | 0.172 | 1 |
| 18 | 0.226 | 0.226 | 100 |
| 19 | 0.144 | 0.144 | 100 |
| 20 | 0.066 | 0.066 | 100 |
| 21 | 0.135 | 0.135 | 100 |
| 22 | 2.596 | 2.596 | 100 |
| 23 | 3.462 | 3.462 | 1 |
| 24 | 0.073 | 0.073 | 0 |
| 25 | 0.233 | 0.233 | 0 |
| 26 | 0.201 | 0.201 | 100 |
| 27 | 0.399 | 0.399 | 100 |
| 28 | 0.494 | 0.494 | 1 |
| 29 | 0.203 | 0.203 | 0 |
| 30 | 6.249 | 6.249 | 92 |
| 31 | 4.358 | 4.358 | 51 |
| 32 | 0.066 | 0.066 | 1 |
| 33 | 0.120 | 0.120 | 100 |
| 34 | 0.090 | 0.090 | 347 |
| 35 | 0.763 | 0.763 | 100 |
| 36 | 0.403 | 0.403 | 100 |
| 37 | 0.052 | 0.052 | 0 |
| 38 | 0.604 | 0.604 | 1 |
| 39 | 2.079 | 2.079 | 153 |
| 40 | 0.082 | 0.082 | 100 |
| 41 | 0.687 | 0.687 | 0 |
| 42 | 0.144 | 0.144 | 10 |
| 43 | 0.169 | 0.169 | 6 |
| 44 | 0.378 | 0.378 | 10 |
| 45 | 0.095 | 0.095 | 16 |
| 46 | 0.207 | 0.207 | 100 |
| 47 | 1.426 | 1.426 | 100 |
| 48 | 0.230 | 0.230 | 1 |
| 49 | 0.097 | 0.097 | 31 |
| 50 | 0.063 | 0.063 | 6 |
| 51 | 0.619 | 0.619 | 100 |
| 52 | 0.156 | 0.156 | 100 |
| 53 | 0.115 | 0.115 | 14 |
| 54 | 0.072 | 0.072 | 0 |
| 55 | 0.074 | 0.074 | 69 |
| 56 | 0.141 | 0.141 | 78 |
| 57 | 0.860 | 0.860 | 100 |
| 58 | 0.085 | 0.085 | 0 |
| 59 | 0.343 | 0.343 | 100 |
| 60 | 0.292 | 0.292 | 100 |
| 61 | 0.060 | 0.060 | 1 |
| 62 | 0.100 | 0.100 | 100 |
| 63 | 0.099 | 0.099 | 44 |
| 64 | 0.207 | 0.207 | 10 |
| 65 | 0.321 | 0.321 | 100 |
| 66 | 0.134 | 0.134 | 5 |
| 67 | 2.738 | 2.738 | 100 |
| 68 | 0.102 | 0.102 | 100 |
| 69 | 0.080 | 0.080 | 100 |
| 70 | 0.346 | 0.346 | 3 |
| 71 | 0.156 | 0.156 | 1102 |
| 72 | 0.193 | 0.193 | 100 |
| 73 | 0.067 | 0.067 | 5 |
| 74 | 293.791 | 293.791 | 90 |
| 75 | 0.520 | 0.520 | 100 |
| 76 | 0.176 | 0.176 | 100 |
| 77 | 0.102 | 0.102 | 44 |
| 78 | 2.190 | 2.190 | 100 |
| 79 | 0.142 | 0.142 | 100 |
| 80 | 0.194 | 0.194 | 100 |
| 81 | 4.892 | 4.892 | 96 |
| 82 | 0.047 | 0.047 | 1 |
| 83 | 0.066 | 0.066 | 4 |
| 84 | 0.058 | 0.058 | 22 |
| 85 | 0.075 | 0.075 | 3 |
| 86 | 0.164 | 0.164 | 100 |
| 87 | 0.612 | 0.612 | 1 |
| 88 | 1.728 | 1.728 | 1 |
| 89 | 0.187 | 0.187 | 100 |
| 90 | 0.091 | 0.091 | 1 |
| 91 | 0.055 | 0.055 | 4 |
| 92 | 0.052 | 0.052 | 1 |
| 93 | 0.068 | 0.068 | 100 |
| 94 | 0.080 | 0.080 | 1 |
| 95 | 15.243 | 15.243 | 1 |
| 96 | 0.094 | 0.094 | 1 |
| 97 | 0.416 | 0.416 | 1 |
| 98 | 0.086 | 0.086 | 2486 |
| 99 | 0.124 | 0.124 | 90 |
