SELECT
    order_id,
    product_id,
    quantity
FROM {{ source('bronze', 'order_items_qty') }}