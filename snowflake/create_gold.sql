-- =====================================================
-- File: 07_create_gold.sql
-- Purpose: Create Gold Layer (Star Schema)
-- =====================================================

USE WAREHOUSE WAREHOUSE_SNOW;
USE DATABASE CARTFLOW_DB;
USE SCHEMA GOLD;

-- =====================================================
-- DIM_CUSTOMER
-- =====================================================

CREATE OR REPLACE TABLE DIM_CUSTOMER AS
SELECT DISTINCT
    USER_ID,
    MAX(ORDER_NUMBER) AS TOTAL_ORDERS
FROM SILVER.CUSTOMER_ORDERS
GROUP BY USER_ID;

-- =====================================================
-- DIM_PRODUCT
-- =====================================================

CREATE OR REPLACE TABLE DIM_PRODUCT AS
SELECT DISTINCT
    PRODUCT_ID,
    PRODUCT_NAME,
    DEPARTMENT_ID,
    DEPARTMENT
FROM SILVER.CUSTOMER_ORDERS;

-- =====================================================
-- DIM_DATE
-- =====================================================

CREATE OR REPLACE TABLE DIM_DATE AS
SELECT DISTINCT
    ORDER_PURCHASE_TIMESTAMP,
    ORDER_YEAR,
    ORDER_MONTH,
    ORDER_DAY
FROM SILVER.ORDER_DATES;

-- =====================================================
-- DIM_SELLER
-- =====================================================

CREATE OR REPLACE TABLE DIM_SELLER AS
SELECT DISTINCT
    SELLER_ID,
    SELLER_NAME,
    SELLER_CITY,
    SELLER_STATE
FROM SILVER.SELLERS;

-- =====================================================
-- FACT_ORDERS
-- =====================================================

CREATE OR REPLACE TABLE FACT_ORDERS AS
SELECT
    c.ORDER_ID,
    c.USER_ID,
    c.PRODUCT_ID,
    i.QUANTITY,
    p.UNIT_PRICE,
    pr.SELLER_ID,
    d.ORDER_PURCHASE_TIMESTAMP,
    d.ORDER_YEAR,
    d.ORDER_MONTH,
    d.ORDER_DAY,
    c.REORDERED
FROM SILVER.CUSTOMER_ORDERS c
LEFT JOIN SILVER.ORDER_ITEMS i
ON c.ORDER_ID = i.ORDER_ID
AND c.PRODUCT_ID = i.PRODUCT_ID
LEFT JOIN SILVER.PRODUCT_PRICING p
ON c.PRODUCT_ID = p.PRODUCT_ID
LEFT JOIN SILVER.ORDER_DATES d
ON c.ORDER_ID = d.ORDER_ID
LEFT JOIN SILVER.PRODUCT_PRICING pr
ON c.PRODUCT_ID = pr.PRODUCT_ID;

-- =====================================================
-- FACT_PAYMENTS
-- =====================================================

CREATE OR REPLACE TABLE FACT_PAYMENTS AS
SELECT
    p.ORDER_ID,
    p.PAYMENT_TYPE,
    p.PAYMENT_INSTALLMENTS,
    p.PAYMENT_VALUE,
    r.REVIEW_SCORE
FROM SILVER.PAYMENTS p
LEFT JOIN SILVER.REVIEWS r
ON p.ORDER_ID = r.ORDER_ID;


SHOW TABLES IN SCHEMA GOLD;


--- TO CHECK
SELECT * FROM GOLD.DIM_CUSTOMER LIMIT 10;

SELECT * FROM GOLD.DIM_PRODUCT LIMIT 10;

SELECT * FROM GOLD.FACT_ORDERS LIMIT 10;

SELECT * FROM GOLD.FACT_PAYMENTS LIMIT 10;