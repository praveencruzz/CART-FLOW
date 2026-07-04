SELECT
    product_id,
    unit_price,
    seller_id
FROM {{ source('bronze', 'product_pricing') }}