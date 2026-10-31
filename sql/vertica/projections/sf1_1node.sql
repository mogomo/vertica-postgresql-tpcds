-- TPC-DS projections for Vertica, scale factor 1.
-- Database Designer (comprehensive design, optimized for the 99 queries) on a sample:
-- chunk 1 of 1 of the SF1 data plus the full customer tables; Vertica Analytic Database v26.3.0-2.
-- Nodes: 1
-- Not designed (default projection): store.
-- Created by scripts/vertica/design.sh with sql/vertica/dbd_design.sql; used by the schema step.
-- @SCHEMA@ = target schema. Valid for the node count and Vertica version above only.

CREATE PROJECTION @SCHEMA@.customer_address_DBD_1_rep /*+createtype(D)*/
(
 ca_address_sk ENCODING DELTARANGE_COMP, 
 ca_address_id ENCODING ZSTD_FAST_COMP, 
 ca_street_number ENCODING ZSTD_FAST_COMP, 
 ca_street_name ENCODING ZSTD_FAST_COMP, 
 ca_street_type ENCODING ZSTD_FAST_COMP, 
 ca_suite_number ENCODING ZSTD_FAST_COMP, 
 ca_city ENCODING ZSTD_FAST_COMP, 
 ca_county ENCODING ZSTD_FAST_COMP, 
 ca_state ENCODING RLE, 
 ca_zip ENCODING ZSTD_FAST_COMP, 
 ca_country ENCODING RLE, 
 ca_gmt_offset ENCODING RLE, 
 ca_location_type ENCODING RLE
)
AS
 SELECT ca_address_sk, 
        ca_address_id, 
        ca_street_number, 
        ca_street_name, 
        ca_street_type, 
        ca_suite_number, 
        ca_city, 
        ca_county, 
        ca_state, 
        ca_zip, 
        ca_country, 
        ca_gmt_offset, 
        ca_location_type
 FROM @SCHEMA@.customer_address 
 ORDER BY ca_gmt_offset,
          ca_state,
          ca_country,
          ca_location_type,
          ca_address_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.customer_address_DBD_2_rep /*+createtype(D)*/
(
 ca_address_sk ENCODING DELTARANGE_COMP, 
 ca_zip ENCODING RLE
)
AS
 SELECT ca_address_sk, 
        ca_zip
 FROM @SCHEMA@.customer_address 
 ORDER BY ca_zip,
          ca_address_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.customer_demographics_DBD_3_rep /*+createtype(D)*/
(
 cd_demo_sk ENCODING COMMONDELTA_COMP, 
 cd_gender ENCODING RLE, 
 cd_marital_status ENCODING RLE, 
 cd_education_status ENCODING RLE, 
 cd_purchase_estimate ENCODING RLE, 
 cd_credit_rating ENCODING RLE, 
 cd_dep_count ENCODING RLE, 
 cd_dep_employed_count ENCODING RLE, 
 cd_dep_college_count ENCODING COMMONDELTA_COMP
)
AS
 SELECT cd_demo_sk, 
        cd_gender, 
        cd_marital_status, 
        cd_education_status, 
        cd_purchase_estimate, 
        cd_credit_rating, 
        cd_dep_count, 
        cd_dep_employed_count, 
        cd_dep_college_count
 FROM @SCHEMA@.customer_demographics 
 ORDER BY cd_gender,
          cd_marital_status,
          cd_education_status,
          cd_purchase_estimate,
          cd_credit_rating,
          cd_dep_count,
          cd_dep_employed_count,
          cd_dep_college_count
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.date_dim_DBD_4_rep /*+createtype(D)*/
(
 d_date_sk ENCODING RLE, 
 d_date_id ENCODING ZSTD_FAST_COMP, 
 d_date ENCODING COMMONDELTA_COMP, 
 d_month_seq ENCODING COMMONDELTA_COMP, 
 d_week_seq ENCODING COMMONDELTA_COMP, 
 d_quarter_seq ENCODING COMMONDELTA_COMP, 
 d_year ENCODING RLE, 
 d_dow ENCODING COMMONDELTA_COMP, 
 d_moy ENCODING RLE, 
 d_dom ENCODING COMMONDELTA_COMP, 
 d_qoy ENCODING RLE, 
 d_fy_year ENCODING COMMONDELTA_COMP, 
 d_fy_quarter_seq ENCODING COMMONDELTA_COMP, 
 d_fy_week_seq ENCODING COMMONDELTA_COMP, 
 d_day_name ENCODING ZSTD_FAST_COMP, 
 d_quarter_name ENCODING ZSTD_FAST_COMP, 
 d_holiday ENCODING RLE, 
 d_weekend ENCODING RLE, 
 d_following_holiday ENCODING RLE, 
 d_first_dom ENCODING COMMONDELTA_COMP, 
 d_last_dom ENCODING COMMONDELTA_COMP, 
 d_same_day_ly ENCODING COMMONDELTA_COMP, 
 d_same_day_lq ENCODING COMMONDELTA_COMP, 
 d_current_day ENCODING RLE, 
 d_current_week ENCODING RLE, 
 d_current_month ENCODING AUTO, 
 d_current_quarter ENCODING AUTO, 
 d_current_year ENCODING AUTO
)
AS
 SELECT d_date_sk, 
        d_date_id, 
        d_date, 
        d_month_seq, 
        d_week_seq, 
        d_quarter_seq, 
        d_year, 
        d_dow, 
        d_moy, 
        d_dom, 
        d_qoy, 
        d_fy_year, 
        d_fy_quarter_seq, 
        d_fy_week_seq, 
        d_day_name, 
        d_quarter_name, 
        d_holiday, 
        d_weekend, 
        d_following_holiday, 
        d_first_dom, 
        d_last_dom, 
        d_same_day_ly, 
        d_same_day_lq, 
        d_current_day, 
        d_current_week, 
        d_current_month, 
        d_current_quarter, 
        d_current_year
 FROM @SCHEMA@.date_dim 
 ORDER BY d_year,
          d_moy,
          d_qoy,
          d_current_day,
          d_current_week,
          d_holiday,
          d_weekend,
          d_following_holiday,
          d_date_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.date_dim_DBD_5_rep /*+createtype(D)*/
(
 d_date_sk ENCODING COMMONDELTA_COMP, 
 d_year ENCODING COMMONDELTA_COMP, 
 d_moy ENCODING RLE
)
AS
 SELECT d_date_sk, 
        d_year, 
        d_moy
 FROM @SCHEMA@.date_dim 
 ORDER BY d_moy,
          d_date_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.date_dim_DBD_6_rep /*+createtype(D)*/
(
 d_date_sk ENCODING COMMONDELTA_COMP, 
 d_date ENCODING COMMONDELTA_COMP
)
AS
 SELECT d_date_sk, 
        d_date
 FROM @SCHEMA@.date_dim 
 ORDER BY d_date_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.warehouse_DBD_7_rep /*+createtype(D)*/
(
 w_warehouse_sk ENCODING AUTO, 
 w_warehouse_id ENCODING AUTO, 
 w_warehouse_name ENCODING ZSTD_FAST_COMP, 
 w_warehouse_sq_ft ENCODING AUTO, 
 w_street_number ENCODING AUTO, 
 w_street_name ENCODING AUTO, 
 w_street_type ENCODING AUTO, 
 w_suite_number ENCODING AUTO, 
 w_city ENCODING AUTO, 
 w_county ENCODING AUTO, 
 w_state ENCODING AUTO, 
 w_zip ENCODING AUTO, 
 w_country ENCODING AUTO, 
 w_gmt_offset ENCODING AUTO
)
AS
 SELECT w_warehouse_sk, 
        w_warehouse_id, 
        w_warehouse_name, 
        w_warehouse_sq_ft, 
        w_street_number, 
        w_street_name, 
        w_street_type, 
        w_suite_number, 
        w_city, 
        w_county, 
        w_state, 
        w_zip, 
        w_country, 
        w_gmt_offset
 FROM @SCHEMA@.warehouse 
 ORDER BY w_warehouse_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.ship_mode_DBD_8_rep /*+createtype(D)*/
(
 sm_ship_mode_sk ENCODING AUTO, 
 sm_ship_mode_id ENCODING AUTO, 
 sm_type ENCODING AUTO, 
 sm_code ENCODING ZSTD_FAST_COMP, 
 sm_carrier ENCODING ZSTD_FAST_COMP, 
 sm_contract ENCODING ZSTD_FAST_COMP
)
AS
 SELECT sm_ship_mode_sk, 
        sm_ship_mode_id, 
        sm_type, 
        sm_code, 
        sm_carrier, 
        sm_contract
 FROM @SCHEMA@.ship_mode 
 ORDER BY sm_carrier
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.time_dim_DBD_9_rep /*+createtype(D)*/
(
 t_time_sk ENCODING COMMONDELTA_COMP, 
 t_time_id ENCODING ZSTD_FAST_COMP, 
 t_time ENCODING COMMONDELTA_COMP, 
 t_hour ENCODING RLE, 
 t_minute ENCODING RLE, 
 t_second ENCODING COMMONDELTA_COMP, 
 t_am_pm ENCODING RLE, 
 t_shift ENCODING RLE, 
 t_sub_shift ENCODING AUTO, 
 t_meal_time ENCODING RLE
)
AS
 SELECT t_time_sk, 
        t_time_id, 
        t_time, 
        t_hour, 
        t_minute, 
        t_second, 
        t_am_pm, 
        t_shift, 
        t_sub_shift, 
        t_meal_time
 FROM @SCHEMA@.time_dim 
 ORDER BY t_hour,
          t_minute,
          t_meal_time,
          t_am_pm,
          t_shift,
          t_time_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.reason_DBD_10_rep /*+createtype(D)*/
(
 r_reason_sk ENCODING AUTO, 
 r_reason_id ENCODING ZSTD_FAST_COMP, 
 r_reason_desc ENCODING ZSTD_FAST_COMP
)
AS
 SELECT r_reason_sk, 
        r_reason_id, 
        r_reason_desc
 FROM @SCHEMA@.reason 
 ORDER BY r_reason_desc,
          r_reason_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.income_band_DBD_11_rep /*+createtype(D)*/
(
 ib_income_band_sk ENCODING COMMONDELTA_COMP, 
 ib_lower_bound ENCODING COMMONDELTA_COMP, 
 ib_upper_bound ENCODING COMMONDELTA_COMP
)
AS
 SELECT ib_income_band_sk, 
        ib_lower_bound, 
        ib_upper_bound
 FROM @SCHEMA@.income_band 
 ORDER BY ib_upper_bound
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.item_DBD_12_rep /*+createtype(D)*/
(
 i_item_sk ENCODING DELTAVAL, 
 i_item_id ENCODING ZSTD_FAST_COMP, 
 i_rec_start_date ENCODING BLOCKDICT_COMP, 
 i_rec_end_date ENCODING BLOCKDICT_COMP, 
 i_item_desc ENCODING ZSTD_FAST_COMP, 
 i_current_price ENCODING DELTARANGE_COMP, 
 i_wholesale_cost ENCODING DELTARANGE_COMP, 
 i_brand_id ENCODING ZSTD_FAST_COMP, 
 i_brand ENCODING ZSTD_FAST_COMP, 
 i_class_id ENCODING COMMONDELTA_COMP, 
 i_class ENCODING RLE, 
 i_category_id ENCODING RLE, 
 i_category ENCODING RLE, 
 i_manufact_id ENCODING DELTAVAL, 
 i_manufact ENCODING ZSTD_FAST_COMP, 
 i_size ENCODING ZSTD_FAST_COMP, 
 i_formulation ENCODING ZSTD_FAST_COMP, 
 i_color ENCODING ZSTD_FAST_COMP, 
 i_units ENCODING ZSTD_FAST_COMP, 
 i_container ENCODING ZSTD_FAST_COMP, 
 i_manager_id ENCODING DELTAVAL, 
 i_product_name ENCODING ZSTD_FAST_COMP
)
AS
 SELECT i_item_sk, 
        i_item_id, 
        i_rec_start_date, 
        i_rec_end_date, 
        i_item_desc, 
        i_current_price, 
        i_wholesale_cost, 
        i_brand_id, 
        i_brand, 
        i_class_id, 
        i_class, 
        i_category_id, 
        i_category, 
        i_manufact_id, 
        i_manufact, 
        i_size, 
        i_formulation, 
        i_color, 
        i_units, 
        i_container, 
        i_manager_id, 
        i_product_name
 FROM @SCHEMA@.item 
 ORDER BY i_category,
          i_class,
          i_current_price,
          i_item_id,
          i_item_desc
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.item_DBD_13_rep /*+createtype(D)*/
(
 i_item_sk ENCODING DELTAVAL, 
 i_brand_id ENCODING ZSTD_FAST_COMP, 
 i_brand ENCODING ZSTD_FAST_COMP, 
 i_category_id ENCODING COMMONDELTA_COMP, 
 i_category ENCODING ZSTD_FAST_COMP, 
 i_manufact_id ENCODING DELTAVAL, 
 i_manager_id ENCODING RLE
)
AS
 SELECT i_item_sk, 
        i_brand_id, 
        i_brand, 
        i_category_id, 
        i_category, 
        i_manufact_id, 
        i_manager_id
 FROM @SCHEMA@.item 
 ORDER BY i_manager_id,
          i_brand,
          i_brand_id,
          i_manufact_id
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.call_center_DBD_14_rep /*+createtype(D)*/
(
 cc_call_center_sk ENCODING RLE, 
 cc_call_center_id ENCODING RLE, 
 cc_rec_start_date ENCODING RLE, 
 cc_rec_end_date ENCODING RLE, 
 cc_closed_date_sk ENCODING RLE, 
 cc_open_date_sk ENCODING RLE, 
 cc_name ENCODING RLE, 
 cc_class ENCODING RLE, 
 cc_employees ENCODING RLE, 
 cc_sq_ft ENCODING RLE, 
 cc_hours ENCODING RLE, 
 cc_manager ENCODING RLE, 
 cc_mkt_id ENCODING RLE, 
 cc_mkt_class ENCODING RLE, 
 cc_mkt_desc ENCODING RLE, 
 cc_market_manager ENCODING RLE, 
 cc_division ENCODING RLE, 
 cc_division_name ENCODING RLE, 
 cc_company ENCODING RLE, 
 cc_company_name ENCODING RLE, 
 cc_street_number ENCODING RLE, 
 cc_street_name ENCODING RLE, 
 cc_street_type ENCODING RLE, 
 cc_suite_number ENCODING RLE, 
 cc_city ENCODING RLE, 
 cc_county ENCODING RLE, 
 cc_state ENCODING RLE, 
 cc_zip ENCODING RLE, 
 cc_country ENCODING RLE, 
 cc_gmt_offset ENCODING RLE, 
 cc_tax_percentage ENCODING AUTO
)
AS
 SELECT cc_call_center_sk, 
        cc_call_center_id, 
        cc_rec_start_date, 
        cc_rec_end_date, 
        cc_closed_date_sk, 
        cc_open_date_sk, 
        cc_name, 
        cc_class, 
        cc_employees, 
        cc_sq_ft, 
        cc_hours, 
        cc_manager, 
        cc_mkt_id, 
        cc_mkt_class, 
        cc_mkt_desc, 
        cc_market_manager, 
        cc_division, 
        cc_division_name, 
        cc_company, 
        cc_company_name, 
        cc_street_number, 
        cc_street_name, 
        cc_street_type, 
        cc_suite_number, 
        cc_city, 
        cc_county, 
        cc_state, 
        cc_zip, 
        cc_country, 
        cc_gmt_offset, 
        cc_tax_percentage
 FROM @SCHEMA@.call_center 
 ORDER BY cc_county,
          cc_closed_date_sk,
          cc_hours,
          cc_city,
          cc_state,
          cc_zip,
          cc_country,
          cc_gmt_offset,
          cc_call_center_sk,
          cc_call_center_id,
          cc_rec_start_date,
          cc_rec_end_date,
          cc_open_date_sk,
          cc_name,
          cc_class,
          cc_employees,
          cc_sq_ft,
          cc_manager,
          cc_mkt_id,
          cc_mkt_class,
          cc_mkt_desc,
          cc_market_manager,
          cc_division,
          cc_division_name,
          cc_company,
          cc_company_name,
          cc_street_number,
          cc_street_name,
          cc_street_type,
          cc_suite_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.customer_DBD_15_rep /*+createtype(D)*/
(
 c_customer_sk ENCODING COMMONDELTA_COMP, 
 c_customer_id ENCODING ZSTD_FAST_COMP, 
 c_current_cdemo_sk ENCODING DELTAVAL, 
 c_current_hdemo_sk ENCODING DELTAVAL, 
 c_current_addr_sk ENCODING DELTAVAL, 
 c_first_shipto_date_sk ENCODING DELTAVAL, 
 c_first_sales_date_sk ENCODING DELTAVAL, 
 c_salutation ENCODING ZSTD_FAST_COMP, 
 c_first_name ENCODING ZSTD_FAST_COMP, 
 c_last_name ENCODING ZSTD_FAST_COMP, 
 c_preferred_cust_flag ENCODING ZSTD_FAST_COMP, 
 c_birth_day ENCODING DELTAVAL, 
 c_birth_month ENCODING BLOCKDICT_COMP, 
 c_birth_year ENCODING BLOCKDICT_COMP, 
 c_birth_country ENCODING ZSTD_FAST_COMP, 
 c_login ENCODING AUTO, 
 c_email_address ENCODING ZSTD_FAST_COMP, 
 c_last_review_date_sk ENCODING DELTAVAL
)
AS
 SELECT c_customer_sk, 
        c_customer_id, 
        c_current_cdemo_sk, 
        c_current_hdemo_sk, 
        c_current_addr_sk, 
        c_first_shipto_date_sk, 
        c_first_sales_date_sk, 
        c_salutation, 
        c_first_name, 
        c_last_name, 
        c_preferred_cust_flag, 
        c_birth_day, 
        c_birth_month, 
        c_birth_year, 
        c_birth_country, 
        c_login, 
        c_email_address, 
        c_last_review_date_sk
 FROM @SCHEMA@.customer 
 ORDER BY c_customer_sk,
          c_current_addr_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.customer_DBD_16_rep /*+createtype(D)*/
(
 c_current_addr_sk ENCODING COMMONDELTA_COMP, 
 c_preferred_cust_flag ENCODING RLE
)
AS
 SELECT c_current_addr_sk, 
        c_preferred_cust_flag
 FROM @SCHEMA@.customer 
 ORDER BY c_preferred_cust_flag,
          c_current_addr_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.web_site_DBD_36_seg_tpcds_design_b0 /*+basename(web_site_DBD_36_seg),createtype(D)*/
(
 web_site_sk ENCODING COMMONDELTA_COMP, 
 web_site_id ENCODING ZSTD_FAST_COMP, 
 web_rec_start_date ENCODING COMMONDELTA_COMP, 
 web_rec_end_date ENCODING BLOCKDICT_COMP, 
 web_name ENCODING AUTO, 
 web_open_date_sk ENCODING COMMONDELTA_COMP, 
 web_close_date_sk ENCODING DELTAVAL, 
 web_class ENCODING AUTO, 
 web_manager ENCODING ZSTD_FAST_COMP, 
 web_mkt_id ENCODING COMMONDELTA_COMP, 
 web_mkt_class ENCODING ZSTD_FAST_COMP, 
 web_mkt_desc ENCODING ZSTD_FAST_COMP, 
 web_market_manager ENCODING ZSTD_FAST_COMP, 
 web_company_id ENCODING COMMONDELTA_COMP, 
 web_company_name ENCODING ZSTD_FAST_COMP, 
 web_street_number ENCODING ZSTD_FAST_COMP, 
 web_street_name ENCODING ZSTD_FAST_COMP, 
 web_street_type ENCODING ZSTD_FAST_COMP, 
 web_suite_number ENCODING AUTO, 
 web_city ENCODING AUTO, 
 web_county ENCODING AUTO, 
 web_state ENCODING AUTO, 
 web_zip ENCODING AUTO, 
 web_country ENCODING AUTO, 
 web_gmt_offset ENCODING COMMONDELTA_COMP, 
 web_tax_percentage ENCODING AUTO
)
AS
 SELECT web_site_sk, 
        web_site_id, 
        web_rec_start_date, 
        web_rec_end_date, 
        web_name, 
        web_open_date_sk, 
        web_close_date_sk, 
        web_class, 
        web_manager, 
        web_mkt_id, 
        web_mkt_class, 
        web_mkt_desc, 
        web_market_manager, 
        web_company_id, 
        web_company_name, 
        web_street_number, 
        web_street_name, 
        web_street_type, 
        web_suite_number, 
        web_city, 
        web_county, 
        web_state, 
        web_zip, 
        web_country, 
        web_gmt_offset, 
        web_tax_percentage
 FROM @SCHEMA@.web_site 
 ORDER BY web_site_sk
SEGMENTED BY HASH (web_site_sk) ALL NODES OFFSET 0;

CREATE PROJECTION @SCHEMA@.store_returns_DBD_17_rep /*+createtype(D)*/
(
 sr_returned_date_sk ENCODING DELTAVAL, 
 sr_return_time_sk ENCODING DELTAVAL, 
 sr_item_sk ENCODING DELTAVAL, 
 sr_customer_sk ENCODING RLE, 
 sr_cdemo_sk ENCODING DELTAVAL, 
 sr_hdemo_sk ENCODING DELTAVAL, 
 sr_addr_sk ENCODING DELTAVAL, 
 sr_store_sk ENCODING BLOCKDICT_COMP, 
 sr_reason_sk ENCODING BLOCKDICT_COMP, 
 sr_ticket_number ENCODING DELTARANGE_COMP, 
 sr_return_quantity ENCODING BLOCKDICT_COMP, 
 sr_return_amt ENCODING DELTARANGE_COMP, 
 sr_return_tax ENCODING DELTARANGE_COMP, 
 sr_return_amt_inc_tax ENCODING DELTARANGE_COMP, 
 sr_fee ENCODING DELTAVAL, 
 sr_return_ship_cost ENCODING DELTARANGE_COMP, 
 sr_refunded_cash ENCODING DELTARANGE_COMP, 
 sr_reversed_charge ENCODING DELTARANGE_COMP, 
 sr_store_credit ENCODING DELTARANGE_COMP, 
 sr_net_loss ENCODING DELTAVAL
)
AS
 SELECT sr_returned_date_sk, 
        sr_return_time_sk, 
        sr_item_sk, 
        sr_customer_sk, 
        sr_cdemo_sk, 
        sr_hdemo_sk, 
        sr_addr_sk, 
        sr_store_sk, 
        sr_reason_sk, 
        sr_ticket_number, 
        sr_return_quantity, 
        sr_return_amt, 
        sr_return_tax, 
        sr_return_amt_inc_tax, 
        sr_fee, 
        sr_return_ship_cost, 
        sr_refunded_cash, 
        sr_reversed_charge, 
        sr_store_credit, 
        sr_net_loss
 FROM @SCHEMA@.store_returns 
 ORDER BY sr_customer_sk,
          sr_store_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.store_returns_DBD_18_rep /*+createtype(D)*/
(
 sr_returned_date_sk ENCODING RLE, 
 sr_store_sk ENCODING RLE, 
 sr_return_amt ENCODING DELTARANGE_COMP, 
 sr_net_loss ENCODING DELTARANGE_COMP
)
AS
 SELECT sr_returned_date_sk, 
        sr_store_sk, 
        sr_return_amt, 
        sr_net_loss
 FROM @SCHEMA@.store_returns 
 ORDER BY sr_store_sk,
          sr_returned_date_sk,
          sr_return_amt
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.store_returns_DBD_19_rep /*+createtype(D)*/
(
 sr_item_sk ENCODING DELTARANGE_COMP, 
 sr_reason_sk ENCODING RLE, 
 sr_ticket_number ENCODING DELTAVAL, 
 sr_return_quantity ENCODING RLE
)
AS
 SELECT sr_item_sk, 
        sr_reason_sk, 
        sr_ticket_number, 
        sr_return_quantity
 FROM @SCHEMA@.store_returns 
 ORDER BY sr_reason_sk,
          sr_return_quantity,
          sr_item_sk,
          sr_ticket_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.household_demographics_DBD_20_rep /*+createtype(D)*/
(
 hd_demo_sk ENCODING COMMONDELTA_COMP, 
 hd_income_band_sk ENCODING COMMONDELTA_COMP, 
 hd_buy_potential ENCODING RLE, 
 hd_dep_count ENCODING RLE, 
 hd_vehicle_count ENCODING RLE
)
AS
 SELECT hd_demo_sk, 
        hd_income_band_sk, 
        hd_buy_potential, 
        hd_dep_count, 
        hd_vehicle_count
 FROM @SCHEMA@.household_demographics 
 ORDER BY hd_dep_count,
          hd_buy_potential,
          hd_vehicle_count,
          hd_demo_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.web_page_DBD_21_rep /*+createtype(D)*/
(
 wp_web_page_sk ENCODING COMMONDELTA_COMP, 
 wp_web_page_id ENCODING ZSTD_FAST_COMP, 
 wp_rec_start_date ENCODING COMMONDELTA_COMP, 
 wp_rec_end_date ENCODING ZSTD_FAST_COMP, 
 wp_creation_date_sk ENCODING DELTAVAL, 
 wp_access_date_sk ENCODING AUTO, 
 wp_autogen_flag ENCODING AUTO, 
 wp_customer_sk ENCODING ZSTD_FAST_COMP, 
 wp_url ENCODING AUTO, 
 wp_type ENCODING ZSTD_FAST_COMP, 
 wp_char_count ENCODING AUTO, 
 wp_link_count ENCODING AUTO, 
 wp_image_count ENCODING DELTAVAL, 
 wp_max_ad_count ENCODING COMMONDELTA_COMP
)
AS
 SELECT wp_web_page_sk, 
        wp_web_page_id, 
        wp_rec_start_date, 
        wp_rec_end_date, 
        wp_creation_date_sk, 
        wp_access_date_sk, 
        wp_autogen_flag, 
        wp_customer_sk, 
        wp_url, 
        wp_type, 
        wp_char_count, 
        wp_link_count, 
        wp_image_count, 
        wp_max_ad_count
 FROM @SCHEMA@.web_page 
 ORDER BY wp_web_page_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.promotion_DBD_22_rep /*+createtype(D)*/
(
 p_promo_sk ENCODING COMMONDELTA_COMP, 
 p_promo_id ENCODING ZSTD_FAST_COMP, 
 p_start_date_sk ENCODING DELTAVAL, 
 p_end_date_sk ENCODING DELTAVAL, 
 p_item_sk ENCODING DELTAVAL, 
 p_cost ENCODING RLE, 
 p_response_target ENCODING RLE, 
 p_promo_name ENCODING ZSTD_FAST_COMP, 
 p_channel_dmail ENCODING RLE, 
 p_channel_email ENCODING RLE, 
 p_channel_catalog ENCODING RLE, 
 p_channel_tv ENCODING RLE, 
 p_channel_radio ENCODING AUTO, 
 p_channel_press ENCODING AUTO, 
 p_channel_event ENCODING RLE, 
 p_channel_demo ENCODING AUTO, 
 p_channel_details ENCODING ZSTD_FAST_COMP, 
 p_purpose ENCODING AUTO, 
 p_discount_active ENCODING AUTO
)
AS
 SELECT p_promo_sk, 
        p_promo_id, 
        p_start_date_sk, 
        p_end_date_sk, 
        p_item_sk, 
        p_cost, 
        p_response_target, 
        p_promo_name, 
        p_channel_dmail, 
        p_channel_email, 
        p_channel_catalog, 
        p_channel_tv, 
        p_channel_radio, 
        p_channel_press, 
        p_channel_event, 
        p_channel_demo, 
        p_channel_details, 
        p_purpose, 
        p_discount_active
 FROM @SCHEMA@.promotion 
 ORDER BY p_channel_tv,
          p_channel_email,
          p_channel_dmail,
          p_channel_event,
          p_cost,
          p_response_target,
          p_channel_catalog,
          p_promo_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.catalog_page_DBD_35_seg_tpcds_design_b0 /*+basename(catalog_page_DBD_35_seg),createtype(D)*/
(
 cp_catalog_page_sk ENCODING COMMONDELTA_COMP, 
 cp_catalog_page_id ENCODING ZSTD_FAST_COMP, 
 cp_start_date_sk ENCODING RLE, 
 cp_end_date_sk ENCODING RLE, 
 cp_department ENCODING ZSTD_FAST_COMP, 
 cp_catalog_number ENCODING RLE, 
 cp_catalog_page_number ENCODING ZSTD_FAST_COMP, 
 cp_description ENCODING ZSTD_FAST_COMP, 
 cp_type ENCODING ZSTD_FAST_COMP
)
AS
 SELECT cp_catalog_page_sk, 
        cp_catalog_page_id, 
        cp_start_date_sk, 
        cp_end_date_sk, 
        cp_department, 
        cp_catalog_number, 
        cp_catalog_page_number, 
        cp_description, 
        cp_type
 FROM @SCHEMA@.catalog_page 
 ORDER BY cp_catalog_page_sk
SEGMENTED BY HASH (cp_catalog_page_sk) ALL NODES OFFSET 0;

CREATE PROJECTION @SCHEMA@.inventory_DBD_23_rep /*+createtype(D)*/
(
 inv_date_sk ENCODING RLE, 
 inv_item_sk ENCODING DELTARANGE_COMP, 
 inv_warehouse_sk ENCODING RLE, 
 inv_quantity_on_hand ENCODING RLE
)
AS
 SELECT inv_date_sk, 
        inv_item_sk, 
        inv_warehouse_sk, 
        inv_quantity_on_hand
 FROM @SCHEMA@.inventory 
 ORDER BY inv_date_sk,
          inv_quantity_on_hand,
          inv_warehouse_sk,
          inv_item_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.catalog_returns_DBD_24_rep /*+createtype(D)*/
(
 cr_returned_date_sk ENCODING RLE, 
 cr_returned_time_sk ENCODING DELTAVAL, 
 cr_item_sk ENCODING DELTARANGE_COMP, 
 cr_refunded_customer_sk ENCODING DELTAVAL, 
 cr_refunded_cdemo_sk ENCODING DELTAVAL, 
 cr_refunded_hdemo_sk ENCODING DELTAVAL, 
 cr_refunded_addr_sk ENCODING DELTAVAL, 
 cr_returning_customer_sk ENCODING DELTAVAL, 
 cr_returning_cdemo_sk ENCODING DELTAVAL, 
 cr_returning_hdemo_sk ENCODING DELTAVAL, 
 cr_returning_addr_sk ENCODING DELTAVAL, 
 cr_call_center_sk ENCODING RLE, 
 cr_catalog_page_sk ENCODING DELTAVAL, 
 cr_ship_mode_sk ENCODING BLOCKDICT_COMP, 
 cr_warehouse_sk ENCODING RLE, 
 cr_reason_sk ENCODING BLOCKDICT_COMP, 
 cr_order_number ENCODING DELTARANGE_COMP, 
 cr_return_quantity ENCODING BLOCKDICT_COMP, 
 cr_return_amount ENCODING DELTARANGE_COMP, 
 cr_return_tax ENCODING DELTARANGE_COMP, 
 cr_return_amt_inc_tax ENCODING DELTARANGE_COMP, 
 cr_fee ENCODING DELTAVAL, 
 cr_return_ship_cost ENCODING DELTARANGE_COMP, 
 cr_refunded_cash ENCODING DELTARANGE_COMP, 
 cr_reversed_charge ENCODING DELTARANGE_COMP, 
 cr_store_credit ENCODING DELTARANGE_COMP, 
 cr_net_loss ENCODING DELTARANGE_COMP
)
AS
 SELECT cr_returned_date_sk, 
        cr_returned_time_sk, 
        cr_item_sk, 
        cr_refunded_customer_sk, 
        cr_refunded_cdemo_sk, 
        cr_refunded_hdemo_sk, 
        cr_refunded_addr_sk, 
        cr_returning_customer_sk, 
        cr_returning_cdemo_sk, 
        cr_returning_hdemo_sk, 
        cr_returning_addr_sk, 
        cr_call_center_sk, 
        cr_catalog_page_sk, 
        cr_ship_mode_sk, 
        cr_warehouse_sk, 
        cr_reason_sk, 
        cr_order_number, 
        cr_return_quantity, 
        cr_return_amount, 
        cr_return_tax, 
        cr_return_amt_inc_tax, 
        cr_fee, 
        cr_return_ship_cost, 
        cr_refunded_cash, 
        cr_reversed_charge, 
        cr_store_credit, 
        cr_net_loss
 FROM @SCHEMA@.catalog_returns 
 ORDER BY cr_call_center_sk,
          cr_returned_date_sk,
          cr_warehouse_sk,
          cr_item_sk,
          cr_order_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.web_returns_DBD_25_rep /*+createtype(D)*/
(
 wr_returned_date_sk ENCODING DELTAVAL, 
 wr_returned_time_sk ENCODING DELTAVAL, 
 wr_item_sk ENCODING DELTARANGE_COMP, 
 wr_refunded_customer_sk ENCODING DELTAVAL, 
 wr_refunded_cdemo_sk ENCODING DELTAVAL, 
 wr_refunded_hdemo_sk ENCODING DELTAVAL, 
 wr_refunded_addr_sk ENCODING DELTAVAL, 
 wr_returning_customer_sk ENCODING DELTAVAL, 
 wr_returning_cdemo_sk ENCODING DELTAVAL, 
 wr_returning_hdemo_sk ENCODING DELTAVAL, 
 wr_returning_addr_sk ENCODING DELTAVAL, 
 wr_web_page_sk ENCODING RLE, 
 wr_reason_sk ENCODING RLE, 
 wr_order_number ENCODING DELTAVAL, 
 wr_return_quantity ENCODING BLOCKDICT_COMP, 
 wr_return_amt ENCODING DELTARANGE_COMP, 
 wr_return_tax ENCODING DELTARANGE_COMP, 
 wr_return_amt_inc_tax ENCODING DELTARANGE_COMP, 
 wr_fee ENCODING DELTAVAL, 
 wr_return_ship_cost ENCODING DELTARANGE_COMP, 
 wr_refunded_cash ENCODING DELTARANGE_COMP, 
 wr_reversed_charge ENCODING DELTARANGE_COMP, 
 wr_account_credit ENCODING DELTARANGE_COMP, 
 wr_net_loss ENCODING DELTARANGE_COMP
)
AS
 SELECT wr_returned_date_sk, 
        wr_returned_time_sk, 
        wr_item_sk, 
        wr_refunded_customer_sk, 
        wr_refunded_cdemo_sk, 
        wr_refunded_hdemo_sk, 
        wr_refunded_addr_sk, 
        wr_returning_customer_sk, 
        wr_returning_cdemo_sk, 
        wr_returning_hdemo_sk, 
        wr_returning_addr_sk, 
        wr_web_page_sk, 
        wr_reason_sk, 
        wr_order_number, 
        wr_return_quantity, 
        wr_return_amt, 
        wr_return_tax, 
        wr_return_amt_inc_tax, 
        wr_fee, 
        wr_return_ship_cost, 
        wr_refunded_cash, 
        wr_reversed_charge, 
        wr_account_credit, 
        wr_net_loss
 FROM @SCHEMA@.web_returns 
 ORDER BY wr_web_page_sk,
          wr_reason_sk,
          wr_item_sk,
          wr_order_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.web_sales_DBD_26_rep /*+createtype(D)*/
(
 ws_sold_date_sk ENCODING DELTAVAL, 
 ws_sold_time_sk ENCODING DELTAVAL, 
 ws_ship_date_sk ENCODING DELTAVAL, 
 ws_item_sk ENCODING DELTARANGE_COMP, 
 ws_bill_customer_sk ENCODING DELTAVAL, 
 ws_bill_cdemo_sk ENCODING DELTAVAL, 
 ws_bill_hdemo_sk ENCODING DELTAVAL, 
 ws_bill_addr_sk ENCODING DELTAVAL, 
 ws_ship_customer_sk ENCODING DELTAVAL, 
 ws_ship_cdemo_sk ENCODING DELTAVAL, 
 ws_ship_hdemo_sk ENCODING DELTAVAL, 
 ws_ship_addr_sk ENCODING DELTAVAL, 
 ws_web_page_sk ENCODING RLE, 
 ws_web_site_sk ENCODING BLOCKDICT_COMP, 
 ws_ship_mode_sk ENCODING BLOCKDICT_COMP, 
 ws_warehouse_sk ENCODING RLE, 
 ws_promo_sk ENCODING DELTAVAL, 
 ws_order_number ENCODING DELTAVAL, 
 ws_quantity ENCODING RLE, 
 ws_wholesale_cost ENCODING DELTAVAL, 
 ws_list_price ENCODING DELTAVAL, 
 ws_sales_price ENCODING DELTAVAL, 
 ws_ext_discount_amt ENCODING DELTAVAL, 
 ws_ext_sales_price ENCODING DELTAVAL, 
 ws_ext_wholesale_cost ENCODING DELTAVAL, 
 ws_ext_list_price ENCODING DELTAVAL, 
 ws_ext_tax ENCODING DELTARANGE_COMP, 
 ws_coupon_amt ENCODING DELTARANGE_COMP, 
 ws_ext_ship_cost ENCODING DELTAVAL, 
 ws_net_paid ENCODING DELTARANGE_COMP, 
 ws_net_paid_inc_tax ENCODING DELTARANGE_COMP, 
 ws_net_paid_inc_ship ENCODING DELTAVAL, 
 ws_net_paid_inc_ship_tax ENCODING DELTAVAL, 
 ws_net_profit ENCODING DELTAVAL
)
AS
 SELECT ws_sold_date_sk, 
        ws_sold_time_sk, 
        ws_ship_date_sk, 
        ws_item_sk, 
        ws_bill_customer_sk, 
        ws_bill_cdemo_sk, 
        ws_bill_hdemo_sk, 
        ws_bill_addr_sk, 
        ws_ship_customer_sk, 
        ws_ship_cdemo_sk, 
        ws_ship_hdemo_sk, 
        ws_ship_addr_sk, 
        ws_web_page_sk, 
        ws_web_site_sk, 
        ws_ship_mode_sk, 
        ws_warehouse_sk, 
        ws_promo_sk, 
        ws_order_number, 
        ws_quantity, 
        ws_wholesale_cost, 
        ws_list_price, 
        ws_sales_price, 
        ws_ext_discount_amt, 
        ws_ext_sales_price, 
        ws_ext_wholesale_cost, 
        ws_ext_list_price, 
        ws_ext_tax, 
        ws_coupon_amt, 
        ws_ext_ship_cost, 
        ws_net_paid, 
        ws_net_paid_inc_tax, 
        ws_net_paid_inc_ship, 
        ws_net_paid_inc_ship_tax, 
        ws_net_profit
 FROM @SCHEMA@.web_sales 
 ORDER BY ws_quantity,
          ws_web_page_sk,
          ws_warehouse_sk,
          ws_item_sk,
          ws_order_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.web_sales_DBD_27_rep /*+createtype(D)*/
(
 ws_sold_date_sk ENCODING RLE, 
 ws_sold_time_sk ENCODING DELTAVAL, 
 ws_ship_hdemo_sk ENCODING DELTAVAL, 
 ws_web_page_sk ENCODING RLE, 
 ws_ext_sales_price ENCODING DELTARANGE_COMP, 
 ws_net_profit ENCODING DELTARANGE_COMP
)
AS
 SELECT ws_sold_date_sk, 
        ws_sold_time_sk, 
        ws_ship_hdemo_sk, 
        ws_web_page_sk, 
        ws_ext_sales_price, 
        ws_net_profit
 FROM @SCHEMA@.web_sales 
 ORDER BY ws_web_page_sk,
          ws_sold_date_sk,
          ws_ext_sales_price
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.web_sales_DBD_28_rep /*+createtype(D)*/
(
 ws_sold_date_sk ENCODING RLE, 
 ws_item_sk ENCODING GCDDELTA, 
 ws_ext_discount_amt ENCODING DELTARANGE_COMP
)
AS
 SELECT ws_sold_date_sk, 
        ws_item_sk, 
        ws_ext_discount_amt
 FROM @SCHEMA@.web_sales 
 ORDER BY ws_sold_date_sk,
          ws_ext_discount_amt
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.catalog_sales_DBD_29_rep /*+createtype(D)*/
(
 cs_sold_date_sk ENCODING DELTAVAL, 
 cs_sold_time_sk ENCODING DELTAVAL, 
 cs_ship_date_sk ENCODING DELTAVAL, 
 cs_bill_customer_sk ENCODING DELTAVAL, 
 cs_bill_cdemo_sk ENCODING DELTAVAL, 
 cs_bill_hdemo_sk ENCODING DELTAVAL, 
 cs_bill_addr_sk ENCODING DELTAVAL, 
 cs_ship_customer_sk ENCODING DELTAVAL, 
 cs_ship_cdemo_sk ENCODING DELTAVAL, 
 cs_ship_hdemo_sk ENCODING DELTAVAL, 
 cs_ship_addr_sk ENCODING DELTAVAL, 
 cs_call_center_sk ENCODING RLE, 
 cs_catalog_page_sk ENCODING DELTARANGE_COMP, 
 cs_ship_mode_sk ENCODING BLOCKDICT_COMP, 
 cs_warehouse_sk ENCODING RLE, 
 cs_item_sk ENCODING RLE, 
 cs_promo_sk ENCODING DELTAVAL, 
 cs_order_number ENCODING DELTARANGE_COMP, 
 cs_quantity ENCODING DELTAVAL, 
 cs_wholesale_cost ENCODING DELTAVAL, 
 cs_list_price ENCODING DELTAVAL, 
 cs_sales_price ENCODING DELTAVAL, 
 cs_ext_discount_amt ENCODING DELTARANGE_COMP, 
 cs_ext_sales_price ENCODING DELTARANGE_COMP, 
 cs_ext_wholesale_cost ENCODING DELTAVAL, 
 cs_ext_list_price ENCODING DELTAVAL, 
 cs_ext_tax ENCODING DELTARANGE_COMP, 
 cs_coupon_amt ENCODING DELTARANGE_COMP, 
 cs_ext_ship_cost ENCODING DELTARANGE_COMP, 
 cs_net_paid ENCODING DELTARANGE_COMP, 
 cs_net_paid_inc_tax ENCODING DELTARANGE_COMP, 
 cs_net_paid_inc_ship ENCODING DELTARANGE_COMP, 
 cs_net_paid_inc_ship_tax ENCODING DELTARANGE_COMP, 
 cs_net_profit ENCODING DELTARANGE_COMP
)
AS
 SELECT cs_sold_date_sk, 
        cs_sold_time_sk, 
        cs_ship_date_sk, 
        cs_bill_customer_sk, 
        cs_bill_cdemo_sk, 
        cs_bill_hdemo_sk, 
        cs_bill_addr_sk, 
        cs_ship_customer_sk, 
        cs_ship_cdemo_sk, 
        cs_ship_hdemo_sk, 
        cs_ship_addr_sk, 
        cs_call_center_sk, 
        cs_catalog_page_sk, 
        cs_ship_mode_sk, 
        cs_warehouse_sk, 
        cs_item_sk, 
        cs_promo_sk, 
        cs_order_number, 
        cs_quantity, 
        cs_wholesale_cost, 
        cs_list_price, 
        cs_sales_price, 
        cs_ext_discount_amt, 
        cs_ext_sales_price, 
        cs_ext_wholesale_cost, 
        cs_ext_list_price, 
        cs_ext_tax, 
        cs_coupon_amt, 
        cs_ext_ship_cost, 
        cs_net_paid, 
        cs_net_paid_inc_tax, 
        cs_net_paid_inc_ship, 
        cs_net_paid_inc_ship_tax, 
        cs_net_profit
 FROM @SCHEMA@.catalog_sales 
 ORDER BY cs_item_sk,
          cs_warehouse_sk,
          cs_call_center_sk,
          cs_order_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.catalog_sales_DBD_30_rep /*+createtype(D)*/
(
 cs_sold_date_sk ENCODING COMMONDELTA_COMP, 
 cs_ship_date_sk ENCODING COMMONDELTA_COMP, 
 cs_call_center_sk ENCODING RLE, 
 cs_ship_mode_sk ENCODING RLE, 
 cs_warehouse_sk ENCODING RLE
)
AS
 SELECT cs_sold_date_sk, 
        cs_ship_date_sk, 
        cs_call_center_sk, 
        cs_ship_mode_sk, 
        cs_warehouse_sk
 FROM @SCHEMA@.catalog_sales 
 ORDER BY cs_warehouse_sk,
          cs_ship_mode_sk,
          cs_call_center_sk,
          cs_sold_date_sk,
          cs_ship_date_sk
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.store_sales_DBD_31_rep /*+createtype(D)*/
(
 ss_sold_date_sk ENCODING RLE, 
 ss_sold_time_sk ENCODING DELTAVAL, 
 ss_item_sk ENCODING DELTAVAL, 
 ss_customer_sk ENCODING DELTAVAL, 
 ss_cdemo_sk ENCODING DELTAVAL, 
 ss_hdemo_sk ENCODING DELTAVAL, 
 ss_addr_sk ENCODING DELTAVAL, 
 ss_store_sk ENCODING RLE, 
 ss_promo_sk ENCODING DELTAVAL, 
 ss_ticket_number ENCODING DELTAVAL, 
 ss_quantity ENCODING RLE, 
 ss_wholesale_cost ENCODING DELTAVAL, 
 ss_list_price ENCODING DELTAVAL, 
 ss_sales_price ENCODING DELTAVAL, 
 ss_ext_discount_amt ENCODING DELTARANGE_COMP, 
 ss_ext_sales_price ENCODING DELTAVAL, 
 ss_ext_wholesale_cost ENCODING DELTAVAL, 
 ss_ext_list_price ENCODING DELTAVAL, 
 ss_ext_tax ENCODING ZSTD_FAST_COMP, 
 ss_coupon_amt ENCODING DELTARANGE_COMP, 
 ss_net_paid ENCODING DELTAVAL, 
 ss_net_paid_inc_tax ENCODING DELTAVAL, 
 ss_net_profit ENCODING DELTAVAL
)
AS
 SELECT ss_sold_date_sk, 
        ss_sold_time_sk, 
        ss_item_sk, 
        ss_customer_sk, 
        ss_cdemo_sk, 
        ss_hdemo_sk, 
        ss_addr_sk, 
        ss_store_sk, 
        ss_promo_sk, 
        ss_ticket_number, 
        ss_quantity, 
        ss_wholesale_cost, 
        ss_list_price, 
        ss_sales_price, 
        ss_ext_discount_amt, 
        ss_ext_sales_price, 
        ss_ext_wholesale_cost, 
        ss_ext_list_price, 
        ss_ext_tax, 
        ss_coupon_amt, 
        ss_net_paid, 
        ss_net_paid_inc_tax, 
        ss_net_profit
 FROM @SCHEMA@.store_sales 
 ORDER BY ss_store_sk,
          ss_quantity,
          ss_sold_date_sk,
          ss_item_sk,
          ss_ticket_number
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.store_sales_DBD_32_rep /*+createtype(D)*/
(
 ss_sold_date_sk ENCODING RLE, 
 ss_item_sk ENCODING GCDDELTA, 
 ss_ext_sales_price ENCODING DELTARANGE_COMP
)
AS
 SELECT ss_sold_date_sk, 
        ss_item_sk, 
        ss_ext_sales_price
 FROM @SCHEMA@.store_sales 
 ORDER BY ss_sold_date_sk,
          ss_ext_sales_price
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.store_sales_DBD_33_rep /*+createtype(D)*/
(
 ss_item_sk ENCODING RLE, 
 ss_hdemo_sk ENCODING DELTAVAL, 
 ss_store_sk ENCODING RLE, 
 ss_net_profit ENCODING DELTARANGE_COMP
)
AS
 SELECT ss_item_sk, 
        ss_hdemo_sk, 
        ss_store_sk, 
        ss_net_profit
 FROM @SCHEMA@.store_sales 
 ORDER BY ss_store_sk,
          ss_item_sk,
          ss_net_profit
UNSEGMENTED ALL NODES;

CREATE PROJECTION @SCHEMA@.store_sales_DBD_34_rep /*+createtype(D)*/
(
 ss_item_sk ENCODING RLE, 
 ss_customer_sk ENCODING DELTAVAL, 
 ss_ticket_number ENCODING DELTARANGE_COMP, 
 ss_quantity ENCODING DELTAVAL, 
 ss_sales_price ENCODING DELTAVAL
)
AS
 SELECT ss_item_sk, 
        ss_customer_sk, 
        ss_ticket_number, 
        ss_quantity, 
        ss_sales_price
 FROM @SCHEMA@.store_sales 
 ORDER BY ss_item_sk,
          ss_ticket_number
UNSEGMENTED ALL NODES;



