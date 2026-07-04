
DESC TABLE GOLD.FACT_ORDERS;

DESC TABLE GOLD.DIM_PRODUCT;
DESC TABLE GOLD.DIM_SELLER;
DESC TABLE GOLD.FACT_PAYMENTS;


SELECT *
FROM GOLD.DIM_PRODUCT
LIMIT 10;

SELECT *
FROM GOLD.DIM_CUSTOMER
LIMIT 10;

SELECT *
FROM GOLD.DIM_SELLER
LIMIT 10;

SELECT *
FROM GOLD.DIM_DATE
LIMIT 10;

SELECT *
FROM GOLD.FACT_PAYMENTS
LIMIT 10;


-- =====================================================
-- File: 08_analytics.sql
-- Purpose: Business Analytics Queries
-- =====================================================

USE WAREHOUSE WAREHOUSE_SNOW;
USE DATABASE CARTFLOW_DB;
USE SCHEMA GOLD;

-- =====================================================
-- 1. Monthly Revenue
-- =====================================================

SELECT
    ORDER_YEAR,
    ORDER_MONTH,
    SUM(QUANTITY * UNIT_PRICE) AS MONTHLY_REVENUE
FROM FACT_ORDERS
GROUP BY ORDER_YEAR, ORDER_MONTH
ORDER BY ORDER_YEAR, ORDER_MONTH;

-- =====================================================
-- 2. Top 10 Products
-- =====================================================

SELECT
    P.PRODUCT_NAME,
    SUM(F.QUANTITY) AS TOTAL_QUANTITY
FROM FACT_ORDERS F
JOIN DIM_PRODUCT P
ON F.PRODUCT_ID = P.PRODUCT_ID
GROUP BY P.PRODUCT_NAME
ORDER BY TOTAL_QUANTITY DESC
LIMIT 10;

-- =====================================================
-- 3. Best Customers
-- =====================================================

SELECT
    USER_ID,
    COUNT(DISTINCT ORDER_ID) AS TOTAL_ORDERS
FROM FACT_ORDERS
GROUP BY USER_ID
ORDER BY TOTAL_ORDERS DESC
LIMIT 10;

-- =====================================================
-- 4. Customer Lifetime Value (CLV)
-- =====================================================

SELECT
    USER_ID,
    SUM(QUANTITY * UNIT_PRICE) AS CUSTOMER_LIFETIME_VALUE
FROM FACT_ORDERS
GROUP BY USER_ID
ORDER BY CUSTOMER_LIFETIME_VALUE DESC;

-- =====================================================
-- 5. Sales by Department
-- =====================================================

SELECT
    P.DEPARTMENT,
    SUM(F.QUANTITY * F.UNIT_PRICE) AS TOTAL_SALES
FROM FACT_ORDERS F
JOIN DIM_PRODUCT P
ON F.PRODUCT_ID = P.PRODUCT_ID
GROUP BY P.DEPARTMENT
ORDER BY TOTAL_SALES DESC;

-- =====================================================
-- 6. Average Review Score
-- =====================================================

SELECT
    AVG(REVIEW_SCORE) AS AVERAGE_REVIEW_SCORE
FROM FACT_PAYMENTS;

-- =====================================================
-- 7. Payment Method Analysis
-- =====================================================

SELECT
    PAYMENT_TYPE,
    COUNT(*) AS TOTAL_PAYMENTS,
    SUM(PAYMENT_VALUE) AS TOTAL_AMOUNT
FROM FACT_PAYMENTS
GROUP BY PAYMENT_TYPE
ORDER BY TOTAL_AMOUNT DESC;

-- =====================================================
-- 8. Top Sellers
-- =====================================================

SELECT
    S.SELLER_NAME,
    SUM(F.QUANTITY * F.UNIT_PRICE) AS TOTAL_REVENUE
FROM FACT_ORDERS F
JOIN DIM_SELLER S
ON F.SELLER_ID = S.SELLER_ID
GROUP BY S.SELLER_NAME
ORDER BY TOTAL_REVENUE DESC
LIMIT 10;

-- =====================================================
-- 9. Monthly Order Trend
-- =====================================================

SELECT
    ORDER_YEAR,
    ORDER_MONTH,
    COUNT(DISTINCT ORDER_ID) AS TOTAL_ORDERS
FROM FACT_ORDERS
GROUP BY ORDER_YEAR, ORDER_MONTH
ORDER BY ORDER_YEAR, ORDER_MONTH;

-- =====================================================
-- 10. Average Order Value (AOV)
-- =====================================================

SELECT
    AVG(ORDER_TOTAL) AS AVERAGE_ORDER_VALUE
FROM (
    SELECT
        ORDER_ID,
        SUM(QUANTITY * UNIT_PRICE) AS ORDER_TOTAL
    FROM FACT_ORDERS
    GROUP BY ORDER_ID
);