--
-- Database Designer (DBD): projection design for the TPC-DS queries.
--
-- Generic: run it on the system that will run the benchmark. DBD then creates
-- projections that fit that system - its node count (segmentation), K-safety
-- (buddy projections) and Vertica version (encodings, syntax) - so no saved
-- projection DDL has to be adapted by hand.
--
-- Prerequisite: a sample of the target scale factor is loaded into :schema and
-- has statistics (analyze_statistics). See TUNING.md, section 1.
--
-- Usage (all values in single quotes except schema):
--   vsql -v schema=tpcds_sample \
--        -v tables="'tpcds_sample.*'" \
--        -v design_type="'comprehensive'" \
--        -v workload="'/path/workload.sql'" \
--        -v design_out="'/path/design.sql'" \
--        -v deploy_out="'/path/deploy.sql'" \
--        -f sql/dbd_design.sql
--
--   tables      tables to design: 'schema.*' or a comma-separated list 'schema.t1,schema.t2'
--   design_type 'comprehensive' = design all projections of the tables;
--               'incremental' = only projections to add to the existing ones
--   workload    file with the 99 queries, one statement per query, ending with ';'
--   design_out  output: CREATE PROJECTION statements of the design
--   deploy_out  output: the statements DBD would run to deploy it (not used here)
--   The output files are written by the Vertica server process, so the database
--   administrator user must be able to write to their directory.
--
-- Result: design_out holds the projection DDL. Run it on the empty tables of the
-- benchmark schema (with the sample schema name replaced), then load the data.
--

-- remove a design left over from an earlier attempt (error if none: ignored)
\set ON_ERROR_STOP off
select designer_drop_design('tpcds_design');
\set ON_ERROR_STOP on

-- DBD resolves the unqualified table names of the queries with the search path
set search_path to :schema, public;

select designer_create_design('tpcds_design');

select designer_set_design_type('tpcds_design', :design_type);

-- query = fastest queries; other values: 'load' (fastest load), 'balanced'
select designer_set_optimization_objective('tpcds_design', 'query');

-- optional: K-safety of the design (default: the K-safety of the database)
-- select designer_set_design_ksafety('tpcds_design', 1);

select designer_add_design_tables('tpcds_design', :tables);

-- the workload; true = the queries are optimized, not only accepted
select designer_add_design_queries('tpcds_design', :workload, true);

-- create the design (arguments after the file names: analyze correlations,
-- deploy, drop the design workspace, continue after an error).
-- deploy = false: only write the DDL; it is applied to the empty tables later.
select designer_run_populate_design_and_deploy('tpcds_design', :design_out, :deploy_out,
                                               true, false, false, false);

-- the design runs in the background: wait until it has finished.
-- With deploy = false this call reports "deployment did not start" - expected.
\set ON_ERROR_STOP off
select designer_wait_for_design('tpcds_design');

-- progress and errors of the design
select event_time, design_phase, phase_step
from v_monitor.design_status
where design_name = 'tpcds_design'
order by event_time desc
limit 5;

select designer_drop_design('tpcds_design');
