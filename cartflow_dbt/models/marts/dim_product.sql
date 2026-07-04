SELECT DISTINCT
    product_id,
    product_name,
    unit_price,
    seller_id

FROM {{ ref('int_orders') }}