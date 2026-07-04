SELECT
    o.order_id,
    o.order_purchase_timestamp,

    c.user_id,
    c.department_id,
    c.department,
    c.product_name,

    oi.product_id,
    oi.quantity,

    pr.unit_price,
    pr.seller_id,

    pay.payment_type,
    pay.payment_value,

    r.review_score

FROM {{ ref('stg_orders') }} o

LEFT JOIN {{ ref('stg_order_items') }} oi
    ON o.order_id = oi.order_id

LEFT JOIN {{ ref('stg_customers') }} c
    ON o.order_id = c.order_id
   AND oi.product_id = c.product_id

LEFT JOIN {{ ref('stg_products') }} pr
    ON oi.product_id = pr.product_id

LEFT JOIN {{ ref('stg_payments') }} pay
    ON o.order_id = pay.order_id

LEFT JOIN {{ ref('stg_reviews') }} r
    ON o.order_id = r.order_id