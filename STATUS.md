# Project status

Handoff notes for the next working session. Host address, credentials and local paths
are kept outside the repository in `config.env` (git-ignored) - read it together with
this file.

## Where we are (2026-10-30, 23:30 - read this first)

**State:** project defined and approved, nothing built or run yet. This folder holds
only this file, `.gitignore` and the local `config.env`. The GitHub repository does
not exist yet (the owner creates it; see "Repository" below).

**The task:** run the TPC-DS benchmark on the same Ubuntu laptop with Vertica 26.3 and
with PostgreSQL, compare the two side by side (query times, load, storage and
compression), publish everything needed to repeat both runs in this repository, write a
detailed technical blog (LinkedIn, Vertica customers) and build a 5-10 minute video
(manim + screenshots, Rocket brand). Only Vertica and PostgreSQL: no other product or
technology is mentioned anywhere in this repository, the blog or the video.

**Approval:** the owner approved the whole chain in one go on 2026-10-30 (toolkit build,
data generation SF1/SF10/SF100, loads, all power runs for both products). No further
question is needed before a heavy run. The host is reserved for this benchmark; nothing
else runs there and its lid is closed.

### Decisions (all defaults accepted by the owner, exceptions marked *)

1. Vertica 26.3.0-2 (already installed on the host) is rerun in the same session as
   PostgreSQL; the older Vertica 26.2 numbers are not used. Both products at SF10 and
   SF100, SF1 for smoke tests and answer verification. Power run only (single stream,
   99 queries, 3 iterations, best iteration counts), same hardware, same data files,
   same query seed, about 40 GB memory budget and 22 threads for both.
2. Vertica setup as in the earlier runs: OS tuning (governor performance, swappiness,
   lid), projections designed by the Database Designer on a sample before the load,
   dedicated resource pool for the query session, statistics, monitoring rows saved to
   the results folder at run time. Benchmark schemas live inside the existing database
   `VDB`; only those schemas are dropped afterwards.
3. *PostgreSQL 18, latest minor, from the PostgreSQL community apt repository (PGDG),
   data directory on `/data`. Version 19 is considered too new for "what the industry
   runs".
4. PostgreSQL tuned setup: shared_buffers / work_mem / effective_cache_size sized for the
   same ~40 GB budget, parallel workers for 22 threads, JIT on, primary keys and indexes
   on the fact tables' join and date columns, ANALYZE with a raised statistics target.
   All settings in a config file in the repo. A second PostgreSQL run with stock
   settings and no indexes is the "defaults" column (SF10 at least).
5. *Per-query timeout for PostgreSQL (owner's rule, 2026-10-30):
   `timeout = min(5 minutes, max(60 seconds, 5 x Vertica best time of the same query at
   the same scale))`. Vertica runs first at each scale so the budgets exist. A query that
   times out in iteration 1 is skipped in iterations 2 and 3 and reported as "did not
   finish within its budget" with the budget shown. Worst case about 8 hours per
   PostgreSQL iteration at SF100.
6. *Storage and compression are compared side by side: flat-file size, Vertica
   compressed size (projection storage), PostgreSQL table size with and without indexes
   (and TOAST), compression ratio = flat files / database size. Load time and load
   throughput too.
7. *Host data: nothing that belongs to the owner's other projects is deleted. Keep the
   dynamic-schema-load data (`/data/dsload` and its schemas in `VDB`), the `/data/vdb`
   storage location, the 26.2 upgrade backup and the folders in the admin user's home.
   Disk is sufficient (183 GB free on root, 691 GB on `/data`). Flat files go to `/data`
   and are kept until both products are loaded at that scale, then deleted to free disk.
8. Repository: new, private, name `vertica-postgresql-tpcds`, created on GitHub by the
   owner; this folder is its local clone-to-be (`git init` done, identity set to the
   owner's GitHub noreply identity, branch `main`). Contents: scripts, SQL, results,
   README, RESULTS, COMPARISON, charts, BLOG.md, VIDEO.md, `video/` (manim project).
9. Blog: BLOG.md in the repo, technical and detailed, for Vertica customers, to be
   published on LinkedIn later; charts and infographics where they help; no author name
   or title.
10. *Video: 5-10 minutes, manim scenes plus screenshots, Rocket Software colours and
    logo as in the owner's previous videos. **Everything including the manim code goes
    into `video/` inside the repo.** Reuse the previous project's `style.py` (palette:
    primary #990099 for shapes, secondary #D257FC for type on black, deep #4500A4,
    violet #751ECA, blue #503EFF, grey text #B8B8C4), `logo.py`, logo and font assets and
    its agent instructions (path in `config.env`). VIDEO.md holds the narration script
    (spoken words), the environment sheet and the numbers shown on screen.
11. Material from the owner's earlier Vertica benchmark repository (path in `config.env`)
    may be reused freely: pipeline (`tpcds.sh`, `scripts/common.sh`, `scripts/vertica/`,
    `sql/vertica/` incl. designed projections, `tune_os.sh`, `report.py`, `charts.py`,
    `collect_env.sh`, `generate_*`, `load_data.sh`, `run_queries.sh`). Strip every
    reference to other products from what is copied. The old repository itself stays
    untouched.
12. Do nothing on the Mac or on the host that this benchmark does not need.

### Host state found on 2026-10-30

- Dell Precision 3591 laptop, Intel Core Ultra 7 165H (6P+8E+2LPE, 22 threads), 64 GB
  RAM (61 GiB usable), 1 TB NVMe: root 232 GB, `/data` 705 GB (ext4). Ubuntu 26.04.1
  LTS, kernel 7.0.0-34. Swap file 8 GB (unused).
- Vertica 26.3.0-2 (deb), Community Edition licence (1 TB), database `VDB` DOWN,
  catalog in the admin home, storage location `/data/vdb` (6 GB, other project), data
  collector retention 5 days (original policy saved in `~/dc_policy`).
- PostgreSQL not installed; Ubuntu archive offers 18.6, PGDG reachable. Python 3.14,
  no psycopg. gcc/make/rsync present, flex/bison not (build step compiles them into
  `work/local` as before).
- CPU governor is `powersave` (the `vertica-cpu-performance` unit does not hold across
  reboots; set it before every run and check it in the run chain).
- `vertica_agent`, `verticad`, unattended-upgrades and 14 update/maintenance timers are
  disabled, snap refresh held (undo list in `~/disabled_for_benchmark.txt` on the host).
  Leave them disabled during the benchmark; the owner decides afterwards.
- The desktop user had a session open (Chrome); the owner says nothing else will run.

### Plan (chain)

1. Build the new repo skeleton from the old pipeline: `tpcds.sh`, `scripts/common.sh`
   with the `db_*` hooks, `scripts/vertica/` (copied), `scripts/postgresql/`
   (new: install.sh via PGDG, server config, schema.sh with DDL from the TPC-DS
   templates, load via `COPY ... FROM PROGRAM` stripping dsdgen's trailing delimiter,
   indexes + ANALYZE, run with `statement_timeout` per query from the Vertica budgets,
   save pg_stat / relation sizes / settings at run time), `sql/postgresql/` (dialect
   template and rewrite rules for the 99 queries), `report.py` / `charts.py` for two
   products, `collect_env.sh`.
2. On the host: tune_os, start `VDB`, build toolkit, generate SF1, smoke test Vertica
   and PostgreSQL at SF1, verify the 99 answers between the two products.
3. SF10: generate, Vertica (design on sample -> schema with projections -> load ->
   3 iterations), PostgreSQL tuned (load -> indexes -> ANALYZE -> 3 iterations with
   budgets), PostgreSQL defaults run.
4. SF100: same order; PostgreSQL first iteration, then iterations 2-3 with the skip
   rule. Delete flat files afterwards.
5. Results folders (`results/<date>_sf<N>_<product>_<label>/` with metrics.csv,
   timings.csv, load.csv, environment.md, summary.md), RESULTS.md, COMPARISON.md,
   charts, README (how to repeat), BLOG.md, VIDEO.md, `video/` manim project, rendered
   video.
6. Privacy grep (addresses, host names, user names, tool attribution, temperatures) before
   every commit; commit commands handed to the owner in the chat.

## Repository

The owner creates `vertica-postgresql-tpcds` (private) on GitHub, then:

```
cd <this folder>
git remote add origin git@github.com:mogomo/vertica-postgresql-tpcds.git
```

Commits and pushes are done by the owner with commands prepared in the chat.

## Rules agreed with the owner

- Every heavy run needs the owner's approval: given once for this whole chain
  (2026-10-30). A new chain (e.g. reruns after a change) needs a new approval.
- The owner runs all git commits and pushes; prepare the exact commands in the chat.
  Commit messages carry no tool attribution and no co-author line.
- Nothing in the repository, the blog or the video mentions how the work was produced or
  any product other than Vertica and PostgreSQL.
- No private data (addresses, host names, user names, passwords) and no temperatures or
  thermal throttling remarks in repository files.
- Communicate in the chat, short and concrete; handoff notes in this file.
- Monitoring data from system tables is saved to the results folder at run time; reports
  are computed from the saved files only.
- The host is used only for this benchmark; the owner's other project data on the host
  is kept.

## Log

- 2026-10-30: project defined; host access verified (Vertica 26.3.0-2 installed by the
  owner on 2026-10-17, PostgreSQL absent); all decisions above agreed with the owner;
  approval for the whole chain given; this folder created. Next: step 1 of the plan.
