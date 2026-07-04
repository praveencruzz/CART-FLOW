SELECT DISTINCT

    CAST(order_purchase_timestamp AS DATE) AS order_date,

    YEAR(order_purchase_timestamp) AS order_year,

    MONTH(order_purchase_timestamp) AS order_month,

    MONTHNAME(order_purchase_timestamp) AS month_name,

    DAYOFWEEK(order_purchase_timestamp) AS day_of_week

FROM {{ ref('stg_orders') }}