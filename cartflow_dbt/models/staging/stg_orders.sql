

SELECT
    order_id,
    order_purchase_timestamp
FROM {{ source('bronze', 'order_dates') }}

