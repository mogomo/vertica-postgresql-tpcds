-- Secondary indexes for the TPC-DS tables in PostgreSQL, built after the load
-- (scripts/postgresql/common.sh, db_build_indexes) next to the primary keys of the
-- specification (every table; for the fact tables item + ticket/order number).
--
-- Chosen from the schema by one general rule, not per query: every fact table gets
-- a B-tree index on its date key (the queries restrict the facts by a date range
-- through date_dim) and on its customer key (the second most common join and
-- filter path). inventory is covered by its primary key (date, item, warehouse).
-- The schema is set by the caller (search_path).
create index on store_sales (ss_sold_date_sk);
create index on store_sales (ss_customer_sk);
create index on store_returns (sr_returned_date_sk);
create index on store_returns (sr_customer_sk);
create index on catalog_sales (cs_sold_date_sk);
create index on catalog_sales (cs_bill_customer_sk);
create index on catalog_returns (cr_returned_date_sk);
create index on catalog_returns (cr_returning_customer_sk);
create index on web_sales (ws_sold_date_sk);
create index on web_sales (ws_bill_customer_sk);
create index on web_returns (wr_returned_date_sk);
create index on web_returns (wr_returning_customer_sk);
