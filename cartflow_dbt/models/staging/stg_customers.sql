SELECT DISTINCT
    order_id,
    user_id,
    department_id,
    department,
    product_id,
    product_name
FROM {{ source('bronze', 'ecommerce_consumer_behaviour') }}