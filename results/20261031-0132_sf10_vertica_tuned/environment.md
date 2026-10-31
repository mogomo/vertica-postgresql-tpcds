## Environment

| | |
|---|---|
| Date | 2026-10-30 23:37 UTC |
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
| Projections | 46 projections (24 super-projections), PROJECTIONS=designed |

## Benchmark settings

| | |
|---|---|
| Scale factor | 10 |
| Toolkit | tpcds-kit @ 5a3a817, queries generated with -QUALIFY Y (fixed spec parameters) |
| Iterations | 3, query timeout 3600s |
| dsdgen jobs / load jobs | 22 / 4 tables at a time |
