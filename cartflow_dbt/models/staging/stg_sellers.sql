SELECT
    seller_id,
    seller_name,
    seller_city,
    seller_state
FROM {{ source('bronze', 'sellers') }}