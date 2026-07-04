show warehouses;
use warehouse warehouse_snow;
use DATABASE CARTFLOW_DB;
create SCHEMA BRONZE;
-- =====================================================
-- 1. ECOMMERCE_CONSUMER_BEHAVIOUR
-- =====================================================

CREATE OR REPLACE TABLE ECOMMERCE_CONSUMER_BEHAVIOUR
(
    ORDER_ID NUMBER,
    USER_ID NUMBER,
    ORDER_NUMBER NUMBER,
    ORDER_DOW NUMBER,
    ORDER_HOUR_OF_DAY NUMBER,
    DAYS_SINCE_PRIOR_ORDER FLOAT,
    PRODUCT_ID NUMBER,
    ADD_TO_CART_ORDER NUMBER,
    REORDERED NUMBER,
    DEPARTMENT_ID NUMBER,
    DEPARTMENT STRING,
    PRODUCT_NAME STRING
);

-- =====================================================
-- 2. ORDER_DATES
-- =====================================================

CREATE OR REPLACE TABLE ORDER_DATES
(
    ORDER_ID NUMBER,
    ORDER_PURCHASE_TIMESTAMP TIMESTAMP
);

-- =====================================================
-- 3. ORDER_ITEMS_QTY
-- =====================================================

CREATE OR REPLACE TABLE ORDER_ITEMS_QTY
(
    ORDER_ID NUMBER,
    PRODUCT_ID NUMBER,
    QUANTITY NUMBER
);

-- =====================================================
-- 4. ORDER_PAYMENTS
-- =====================================================

CREATE OR REPLACE TABLE ORDER_PAYMENTS
(
    ORDER_ID NUMBER,
    PAYMENT_SEQUENTIAL NUMBER,
    PAYMENT_TYPE STRING,
    PAYMENT_INSTALLMENTS NUMBER,
    PAYMENT_VALUE NUMBER(10,2)
);

-- =====================================================
-- 5. ORDER_REVIEWS
-- =====================================================

CREATE OR REPLACE TABLE ORDER_REVIEWS
(
    REVIEW_ID STRING,
    ORDER_ID NUMBER,
    REVIEW_SCORE NUMBER,
    REVIEW_CREATION_DATE TIMESTAMP,
    REVIEW_ANSWER_TIMESTAMP TIMESTAMP
);

-- =====================================================
-- 6. PRODUCT_PRICING
-- =====================================================

CREATE OR REPLACE TABLE PRODUCT_PRICING
(
    PRODUCT_ID NUMBER,
    UNIT_PRICE NUMBER(10,2),
    SELLER_ID NUMBER
);

-- =====================================================
-- 7. SELLERS
-- =====================================================

CREATE OR REPLACE TABLE SELLERS
(
    SELLER_ID NUMBER,
    SELLER_NAME STRING,
    SELLER_CITY STRING,
    SELLER_STATE STRING
);

-- =====================================================
-- Verify Tables
-- =====================================================

SHOW TABLES IN SCHEMA BRONZE;