SELECT

    order_id,
    payment_type,
    payment_installments,
    payment_value

FROM {{ ref('stg_payments') }}