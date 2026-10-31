# TPC-DS on Vertica - 20261031-0054_sf1_vertica_smoke

## Power run (99 queries, sequential)

| Iteration | Total time | Server time | Queries OK | Geomean (queries OK in all iterations) |
|---:|---:|---:|---:|---:|
| 1 | 23.2 s | 20.4 s | 99/99 | 0.143 s |
| best of each query | 23.2 s | | 99/99 | 0.143 s (all queries) |

Memory spills to disk (all iterations): none

Largest memory acquired by one query: 18.2 GiB (query 1)

Total time = wall clock measured by the client around each query (includes connecting and fetching the result). Server time = execution time recorded by Vertica itself (see `server_times.csv`).

## Data generation and load

| Step | Value |
|---|---:|
| dsdgen (22 parallel) | 20.4 s, 1.23 GB flat files |
| COPY, 4 tables in parallel | 4.9 s |
| primary keys and indexes | 0.0 s |
| analyze_statistics | 2.2 s |
| Vertica storage | 0.37 GB (compression 3.4x) |

<details><summary>Rows, load time and size per table</summary>

| Table | Rows | Load time | Flat files | Stored | Compression |
|---|---:|---:|---:|---:|---:|
| store_sales | 2,880,404 | 3.5 s | 0.39 GB | 0.16 GB | 2.4x |
| catalog_sales | 1,441,548 | 2.3 s | 0.29 GB | 0.09 GB | 3.1x |
| web_sales | 719,384 | 1.3 s | 0.15 GB | 0.05 GB | 2.7x |
| inventory | 11,745,000 | 4.9 s | 0.22 GB | 0.03 GB | 8.5x |
| store_returns | 287,514 | 0.4 s | 0.03 GB | 0.01 GB | 2.4x |
| catalog_returns | 144,067 | 0.2 s | 0.02 GB | 0.01 GB | 3.0x |
| web_returns | 71,763 | 0.1 s | 0.01 GB | 0.00 GB | 2.9x |
| customer | 100,000 | 0.1 s | 0.01 GB | 0.00 GB | 3.3x |
| customer_demographics | 1,920,800 | 1.5 s | 0.08 GB | 0.00 GB | 225.1x |
| customer_address | 50,000 | 0.1 s | 0.01 GB | 0.00 GB | 5.4x |
| item | 18,000 | 0.1 s | 0.01 GB | 0.00 GB | 3.2x |
| date_dim | 73,049 | 0.1 s | 0.01 GB | 0.00 GB | 20.5x |
| time_dim | 86,400 | 0.1 s | 0.01 GB | 0.00 GB | 83.1x |
| promotion | 300 | 0.0 s | 0.00 GB | 0.00 GB | 4.0x |
| household_demographics | 7,200 | 0.0 s | 0.00 GB | 0.00 GB | 151.9x |
| catalog_page | 11,718 | 0.0 s | 0.00 GB | 0.00 GB | 4.0x |
| web_page | 60 | 0.0 s | 0.00 GB | 0.00 GB | 4.7x |
| call_center | 6 | 0.0 s | 0.00 GB | 0.00 GB | 0.9x |
| store | 12 | 0.0 s | 0.00 GB | 0.00 GB | 1.6x |
| warehouse | 5 | 0.0 s | 0.00 GB | 0.00 GB | 0.9x |
| web_site | 30 | 0.0 s | 0.00 GB | 0.00 GB | 2.6x |
| reason | 35 | 0.0 s | 0.00 GB | 0.00 GB | 2.2x |
| ship_mode | 20 | 0.0 s | 0.00 GB | 0.00 GB | 1.3x |
| income_band | 20 | 0.0 s | 0.00 GB | 0.00 GB | 4.2x |

</details>

## Environment

| | |
|---|---|
| Date | 2026-10-30 22:54 UTC |
| Machine | Dell Inc. Precision 3591 (laptop) |
| CPU | Intel(R) Core(TM) Ultra 7 165H - 1 socket(s), 16 cores, 22 threads, max 5000 MHz, L3 24 MiB (1 instance) |
| Memory | 61.0 GiB RAM, 8.0 GiB swap |
| Storage (database data) | 953.9G NVMe SSD (BC901 NVMe SK hynix 1024GB), ext4 |
| OS | Ubuntu 26.04.1 LTS, kernel 7.0.0-34-generic |
| Power | governor=performance, energy_perf_pref=default, platform_profile=performance, on AC=1 |
| Database | Vertica |
| Version | 26.3.0-2 |
| Deployment | Enterprise mode, 1 node(s) |
| License | 1TB raw data limit, perpetual |
| Resource pool | benchmark pool tpcds_pool: memorysize=65%, maxmemorysize=none, plannedconcurrency=2, executionparallelism=AUTO |
| Projections | 37 projections (24 super-projections), PROJECTIONS=designed |

## Benchmark settings

| | |
|---|---|
| Scale factor | 1 |
| Toolkit | tpcds-kit @ 5a3a817, queries generated with -QUALIFY Y (fixed spec parameters) |
| Iterations | 1, query timeout 3600s |
| dsdgen jobs / load jobs | 22 / 4 tables at a time |

## Per-query times (seconds)

| Query | Iter 1 | Best | Rows |
|---:|---:|---:|---:|
| 1 | 0.077 | 0.077 | 100 |
| 2 | 0.136 | 0.136 | 2513 |
| 3 | 0.052 | 0.052 | 38 |
| 4 | 2.502 | 2.502 | 8 |
| 5 | 0.388 | 0.388 | 100 |
| 6 | 0.095 | 0.095 | 41 |
| 7 | 0.114 | 0.114 | 100 |
| 8 | 0.099 | 0.099 | 0 |
| 9 | 0.077 | 0.077 | 1 |
| 10 | 0.120 | 0.120 | 2 |
| 11 | 1.360 | 1.360 | 88 |
| 12 | 0.079 | 0.079 | 100 |
| 13 | 0.292 | 0.292 | 1 |
| 14 | 1.085 | 1.085 | 200 |
| 15 | 0.089 | 0.089 | 100 |
| 16 | 0.273 | 0.273 | 1 |
| 17 | 0.170 | 0.170 | 1 |
| 18 | 0.237 | 0.237 | 100 |
| 19 | 0.085 | 0.085 | 100 |
| 20 | 0.064 | 0.064 | 100 |
| 21 | 0.089 | 0.089 | 100 |
| 22 | 1.281 | 1.281 | 100 |
| 23 | 1.234 | 1.234 | 1 |
| 24 | 0.293 | 0.293 | 0 |
| 25 | 0.124 | 0.124 | 0 |
| 26 | 0.102 | 0.102 | 100 |
| 27 | 0.096 | 0.096 | 100 |
| 28 | 0.174 | 0.174 | 1 |
| 29 | 0.114 | 0.114 | 0 |
| 30 | 0.067 | 0.067 | 92 |
| 31 | 0.417 | 0.417 | 51 |
| 32 | 0.059 | 0.059 | 1 |
| 33 | 0.155 | 0.155 | 100 |
| 34 | 0.090 | 0.090 | 451 |
| 35 | 0.158 | 0.158 | 100 |
| 36 | 0.135 | 0.135 | 100 |
| 37 | 0.051 | 0.051 | 0 |
| 38 | 0.279 | 0.279 | 1 |
| 39 | 0.862 | 0.862 | 153 |
| 40 | 0.079 | 0.079 | 100 |
| 41 | 0.050 | 0.050 | 0 |
| 42 | 0.033 | 0.033 | 10 |
| 43 | 0.118 | 0.118 | 6 |
| 44 | 0.098 | 0.098 | 10 |
| 45 | 0.077 | 0.077 | 16 |
| 46 | 0.150 | 0.150 | 100 |
| 47 | 0.440 | 0.440 | 100 |
| 48 | 0.304 | 0.304 | 1 |
| 49 | 0.155 | 0.155 | 31 |
| 50 | 0.098 | 0.098 | 6 |
| 51 | 0.301 | 0.301 | 100 |
| 52 | 0.033 | 0.033 | 100 |
| 53 | 0.064 | 0.064 | 14 |
| 54 | 0.179 | 0.179 | 0 |
| 55 | 0.035 | 0.035 | 69 |
| 56 | 0.117 | 0.117 | 78 |
| 57 | 0.263 | 0.263 | 100 |
| 58 | 0.103 | 0.103 | 0 |
| 59 | 0.228 | 0.228 | 100 |
| 60 | 0.154 | 0.154 | 100 |
| 61 | 0.065 | 0.065 | 1 |
| 62 | 0.115 | 0.115 | 100 |
| 63 | 0.079 | 0.079 | 44 |
| 64 | 0.407 | 0.407 | 10 |
| 65 | 0.156 | 0.156 | 100 |
| 66 | 0.268 | 0.268 | 5 |
| 67 | 0.545 | 0.545 | 100 |
| 68 | 0.138 | 0.138 | 100 |
| 69 | 0.104 | 0.104 | 100 |
| 70 | 0.136 | 0.136 | 3 |
| 71 | 0.124 | 0.124 | 1102 |
| 72 | 0.320 | 0.320 | 100 |
| 73 | 0.081 | 0.081 | 9 |
| 74 | 0.395 | 0.395 | 90 |
| 75 | 0.423 | 0.423 | 100 |
| 76 | 0.112 | 0.112 | 100 |
| 77 | 0.118 | 0.118 | 44 |
| 78 | 0.611 | 0.611 | 100 |
| 79 | 0.102 | 0.102 | 100 |
| 80 | 0.261 | 0.261 | 100 |
| 81 | 0.075 | 0.075 | 96 |
| 82 | 0.041 | 0.041 | 1 |
| 83 | 0.074 | 0.074 | 4 |
| 84 | 0.050 | 0.050 | 22 |
| 85 | 0.166 | 0.166 | 3 |
| 86 | 0.092 | 0.092 | 100 |
| 87 | 0.279 | 0.279 | 1 |
| 88 | 0.190 | 0.190 | 1 |
| 89 | 0.090 | 0.090 | 100 |
| 90 | 0.038 | 0.038 | 1 |
| 91 | 0.048 | 0.048 | 4 |
| 92 | 0.034 | 0.034 | 1 |
| 93 | 0.071 | 0.071 | 100 |
| 94 | 0.152 | 0.152 | 1 |
| 95 | 0.496 | 0.496 | 1 |
| 96 | 0.048 | 0.048 | 1 |
| 97 | 0.284 | 0.284 | 1 |
| 98 | 0.073 | 0.073 | 2486 |
| 99 | 0.096 | 0.096 | 90 |
