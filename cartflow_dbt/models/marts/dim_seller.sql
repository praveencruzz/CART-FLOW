SELECT

    seller_id,
    seller_name,
    seller_city,
    seller_state

FROM {{ ref('stg_sellers') }}