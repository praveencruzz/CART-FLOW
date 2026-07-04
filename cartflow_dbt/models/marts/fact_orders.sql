SELECT
    order_id,
    user_id,
    product_id,
    seller_id,

    CAST(order_purchase_timestamp AS DATE) AS order_date,
    order_purchase_timestamp,

    department,
    quantity,
    unit_price,

    payment_type,
    payment_value,

    review_score

FROM {{ ref('int_orders') }}