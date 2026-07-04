USE WAREHOUSE WAREHOUSE_SNOW;
USE DATABASE CARTFLOW_DB;
USE SCHEMA SILVER;

-- =====================================================
-- CUSTOMER ORDERS
-- =====================================================

CREATE OR REPLACE TABLE CUSTOMER_ORDERS AS
SELECT DISTINCT
    ORDER_ID,
    USER_ID,
    ORDER_NUMBER,
    ORDER_DOW,
    ORDER_HOUR_OF_DAY,
    DAYS_SINCE_PRIOR_ORDER,
    PRODUCT_ID,
    ADD_TO_CART_ORDER,
    REORDERED,
    DEPARTMENT_ID,
    DEPARTMENT,
    PRODUCT_NAME
FROM BRONZE.ECOMMERCE_CONSUMER_BEHAVIOUR;

-- =====================================================
-- ORDER DATES
-- =====================================================

CREATE OR REPLACE TABLE ORDER_DATES AS
SELECT
    ORDER_ID,
    ORDER_PURCHASE_TIMESTAMP,
    YEAR(ORDER_PURCHASE_TIMESTAMP) AS ORDER_YEAR,
    MONTH(ORDER_PURCHASE_TIMESTAMP) AS ORDER_MONTH,
    DAY(ORDER_PURCHASE_TIMESTAMP) AS ORDER_DAY
FROM BRONZE.ORDER_DATES;

-- =====================================================
-- ORDER ITEMS
-- =====================================================

CREATE OR REPLACE TABLE ORDER_ITEMS AS
SELECT *
FROM BRONZE.ORDER_ITEMS_QTY;

-- =====================================================
-- PAYMENTS
-- =====================================================

CREATE OR REPLACE TABLE PAYMENTS AS
SELECT *
FROM BRONZE.ORDER_PAYMENTS;

-- =====================================================
-- REVIEWS
-- =====================================================

CREATE OR REPLACE TABLE REVIEWS AS
SELECT *
FROM BRONZE.ORDER_REVIEWS;

-- =====================================================
-- PRODUCT PRICING
-- =====================================================

CREATE OR REPLACE TABLE PRODUCT_PRICING AS
SELECT *
FROM BRONZE.PRODUCT_PRICING;

-- =====================================================
-- SELLERS
-- =====================================================

CREATE OR REPLACE TABLE SELLERS AS
SELECT *
FROM BRONZE.SELLERS;

SHOW TABLES IN SCHEMA SILVER;

---TO CHECK
SELECT * FROM SILVER.CUSTOMER_ORDERS LIMIT 10;

SELECT * FROM SILVER.ORDER_DATES LIMIT 10;

SELECT * FROM SILVER.PAYMENTS LIMIT 10;