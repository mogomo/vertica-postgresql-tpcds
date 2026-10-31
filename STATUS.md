# Project status

Handoff notes for the next working session. Host address, credentials and local paths
are kept outside the repository in `config.env` (git-ignored) - read it together with
this file.

## Where we are (2026-10-31, 11:00 - read this first)

**State:** benchmark complete. First full commit pushed by the owner (c1bd94e). After it,
on the owner's request and approval (2026-10-31): query 41 now runs with identical text on
both products (PostgreSQL rewrite gets the same `EXISTS` form; rerun 3 iterations at SF10
and SF100, merged into the PostgreSQL power runs with `./tpcds.sh amend`, originals kept
as `timings_original.csv`); query 30 run once at SF100 with a 30-minute limit to show what
the time limits hide; README / RESULTS / BLOG / VIDEO.md / analysis / video scenes
updated (time-limit section, single-node caveat, "as is" disclaimer, MIT license
section; silent draft re-rendered, 405.7 s, `video/media/videos/film/480p15/Film.mp4`). Committed and pushed by the owner (7d3407b).
Repo still private.

| | Vertica SF10 | PostgreSQL SF10 | Vertica SF100 | PostgreSQL SF100 |
|---|---:|---:|---:|---:|
| best iteration | 94.4 s | >= 837.1 s (8 over 60 s) | 663.8 s | >= 5782.0 s (56 over limit) |
| finished within limit | 99 | 91 | 99 | 43 |
| median ratio (finished) | | 5.1x | | 20.9x |
| COPY / indexes / statistics | 33 / - / 3.5 s | 30 / 63 / 98 s | 388 / - / 11 s | 499 / 1099 / 1845 s |
| size (flat 12.0 / 102.5 GB) | 4.07 GB | 22.2 GB | 39.2 GB | 147.5 GB |

Time-limit argument (owner's request): worst ratio of a finished query = q30 SF10,
579.6 s vs 0.158 s = 3,668x (60 s limit had shown "> 380x"); measured growth SF1 -> SF10
93x (6.25 -> 579.6 s; Vertica 2.4x), quadratic per the SubPlan in the plan; SF100 plan
unchanged (analysis/postgresql_plans_sf100/q30.plan); extrapolation ~54,000 s = ~15 h
at SF100 (Vertica 0.78 s); 30-minute run at SF100: stopped at 1800 s, not finished (> 2,300x; the power-run limit had shown > 77x).

Host state: VDB holds schemas tpcds_sf1, tpcds_sf10, tpcds_sf100 (+ the owner's other
project, kept); PostgreSQL 18 cluster (stopped, start.conf manual) holds the same three
schemas in database tpcds (~193 GB incl. WAL on /data); flat files: SF1 and SF10 still in
/data/tpcds/data (SF100 deleted). Both databases stopped. tune_os settings applied
(not persisted). Host scripts of the last runs: /data/tpcds/q41_q30.sh (+ .log);
pre-change PostgreSQL queries kept in /data/tpcds/queries/postgresql/sf{10,100}_before_q41.
Cleanup (drop schemas, remove PostgreSQL, delete /data/tpcds, re-enable the services in
~/disabled_for_benchmark.txt) waits for the owner's decision.

**Next (owner):** record the narration
(VIDEO.md, now 11 chapters s00-s10, ~870 words) as `video/assets/narration.mp3`, then in
video/: `python timeline.py && manim -qh --fps 60 --disable_caching film.py Film`; decide
host cleanup; making the repo public needs the owner's approval of the results.

**How the pieces fit (for a new session):** `scripts/run_comparison.sh` = one scale
factor end to end; `./tpcds.sh <step>` single steps (`amend` = replace queries of a power
run by a later run). Reports: `python3 scripts/compare.py results/20261031-0132_sf10_vertica_tuned
results/20261031-0145_sf10_postgresql_tuned results/20261031-0335_sf100_vertica_tuned
results/20261031-0506_sf100_postgresql_tuned -o COMPARISON.md`. Host: rsync `scripts sql
tpcds.sh` to `~/vertica-postgresql-tpcds/` (never config.env), run there, rsync new results
folders back (pulling an existing folder overwrites local edits). Video numbers come from
`video/kit.py` (RUNS / RERUNS -> results folders); draft render `manim -ql film.py Film` in
video/ with the venv in config.env (MANIM_SRC/.venv); macOS has no `timeout`.

**The task:** run the TPC-DS benchmark on the same Ubuntu laptop with Vertica 26.3 and
with PostgreSQL, compare the two side by side (query times, load, storage and
compression), publish everything needed to repeat both runs in this repository, write a
detailed technical blog (LinkedIn, Vertica customers) and build a 5-10 minute video
(manim + screenshots, Rocket brand). Only Vertica and PostgreSQL: no other product or
technology is mentioned anywhere in this repository, the blog or the video.

**Approval:** the owner approved the whole chain in one go on 2026-10-30 (toolkit build,
data generation SF1/SF10/SF100, loads, all power runs for both products); on 2026-10-31
the q41 rerun with identical text and one 30-minute run of a single query. All of it is
done: any further run needs a new approval. The host is reserved for this benchmark;
nothing else runs there and its lid is closed.

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
   All settings in a config file in the repo. *No "stock defaults" PostgreSQL run
   (dropped by the owner on 2026-10-31: tuned against tuned only). Queries: syntax-only
   edits for PostgreSQL (same meaning, every edit listed in the repo), no hand tuning; no
   materialized views / aggregate projections / result caches / hints for either product.
5. *Per-query timeout for PostgreSQL (owner's rule, final 2026-10-31):
   `timeout = max(60 seconds, 5 x Vertica best time of the same query at the same scale)`
   (no 5-minute cap). Vertica best = best of its 3 iterations, client-side wall clock; for
   multi-part queries the budget covers the whole query file. Vertica runs first at each
   scale so the budgets exist. A query that times out in iteration 1 is skipped in
   iterations 2 and 3 and reported as "did not finish within its budget" with the budget
   shown; totals that include timeouts are lower bounds (">= X s"). Worst case with the
   26.2 timings: 1.6 h per iteration at SF10, 2.1 h at SF100.
   *At SF10 only: every query that timed out is rerun once, alone, with a 10-minute limit
   (no total cap) and reported with its real time or "> 10 min".
   *(2026-10-31, after the runs) To show what the limits hide: take the worst ratio of a
   query that finished (q30 SF10, 3,668x), explain from measured facts why stopped queries
   can be far worse or never end, and prove it with one query given 30 minutes (q30 at
   SF100). Documented in README / RESULTS / BLOG / VIDEO "What the time limits mean/hide".
   *(2026-10-31) q41: both products run the identical `EXISTS` text; PostgreSQL's q41 rows
   come from a rerun merged with `./tpcds.sh amend`.
6. *Storage and compression are compared side by side: flat-file size, Vertica
   compressed size (projection storage), PostgreSQL table size with and without indexes
   (and TOAST), compression ratio = flat files / database size. Load time and load
   throughput too.
7. *Host data: nothing that belongs to the owner's other projects is deleted. Keep the
   dynamic-schema-load data (`/data/dsload` and its schemas in `VDB`), the `/data/vdb`
   storage location, the 26.2 upgrade backup and the folders in the admin user's home.
   Disk is sufficient (183 GB free on root, 691 GB on `/data`). Flat files go to `/data`
   and are kept until both products are loaded at that scale, then deleted to free disk.
8. Repository: `vertica-postgresql-tpcds`, created private on GitHub by the owner on
   2026-10-31; this folder is its local clone-to-be (`git init` done, identity set to the
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
   budgets), SF10 rerun of timed-out queries with a 10-minute limit.
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

- README must keep: MIT license (LICENSE + section), the "provided as is, no
  responsibility" disclaimer, the single-node caveat (Vertica would probably do better on
  a cluster or stronger hardware), the TPC fair-use disclaimer, and the meaning of the
  time limits. README, RESULTS, COMPARISON, BLOG, VIDEO.md and the video scenes must show
  the same, latest numbers.

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

- 2026-10-31 (afternoon): blog prepared for LinkedIn: repository URL added (intro, analysis
  link, "Repeat it yourself"); the 5 tables and 6 charts rendered as PNG in `work/linkedin/`
  (git-ignored; LinkedIn articles take neither Markdown tables nor SVG). Publishing waits
  for the repository to go public (owner's approval).

- 2026-10-31 (late morning): owner committed the full work (c1bd94e) and approved: q41
  rerun with identical text for both products; a 30-minute limit for one query to prove
  the time-limit point; final doc pass (MIT, as-is disclaimer, single node, time limits).
  Done: PostgreSQL rewrite gets `correlated_count_to_exists`; q41 rerun SF10/SF100 (0.066 /
  0.089 s, Vertica 0.054 / 0.109 s) merged into the power runs; q30 SF100 30-minute run;
  scripts/amend.py + `./tpcds.sh amend`; COMPARISON regenerated; docs and video updated
  (new chapter s08_limits, s08/s09 renamed to s09_meaning/s10_close). Commit pending.

- 2026-10-31: owner said "start the benchmark now". Final decisions: timeout
  max(60 s, 5 x Vertica best) without cap; defaults run dropped; SF10 rerun of timed-out
  queries with a 10-minute limit; syntax-only query edits. Blog must carry the TPC
  fair-use disclaimer (derived from TPC-DS, not an official result), a limitations
  section and per-query results.

- 2026-10-31: GitHub repository created (private); first commit with STATUS.md and
  .gitignore pushed by the owner. Work starts only when the owner says
  "start the benchmark".
- 2026-10-30: project defined; host access verified (Vertica 26.3.0-2 installed by the
  owner on 2026-10-17, PostgreSQL absent); all decisions above agreed with the owner;
  approval for the whole chain given; this folder created. Next: step 1 of the plan.
