# Data

The actual data files are **git-ignored** (the raw CSV is ~120 MB — over GitHub's
100 MB limit). This file documents the schema so the pipeline is reproducible.

## Raw dataset

`data/raw/ecommerce_consumer_behaviour.csv` — an Instacart-style online-grocery
basket dataset. **Grain: one row per product within an order.** ~2.02M rows.

| column                  | type   | notes                                             |
|-------------------------|--------|---------------------------------------------------|
| order_id                | int    | order identifier                                  |
| user_id                 | int    | customer identifier                               |
| order_number            | int    | the n-th order placed by this user (1 = first)    |
| order_dow               | int    | day of week the order was placed (0–6)            |
| order_hour_of_day       | int    | hour of day (0–23)                                |
| days_since_prior_order  | float  | NULL for a user's first order (~124k rows)        |
| product_id              | int    | product identifier                                |
| add_to_cart_order       | int    | sequence the item was added to the cart           |
| reordered               | int    | 1 if the user has ordered this product before     |
| department_id           | int    | department identifier                             |
| department              | string | department name (e.g. `dairy eggs`, `pantry`)     |
| product_name            | string | product / sub-category name                       |

## Layers (medallion)

- `data/raw/`       — source CSV as delivered (Phase 3).
- `data/cleaned/`   — Phase 4 output: validated, type-coerced single CSV + `data_quality_report.json`.
- `data/processed/` — Phase 5 output: modelled Parquet datasets (`order_items`, `orders`, `dim_products`, `dim_departments`, `dim_users`).

## Supplemental synthetic data (unblocks revenue analytics)

The base dataset has **no price, payment, seller, review, or calendar-date**
columns, so revenue / CLV / AOV / `fact_payments` / `dim_seller` were originally
impossible. `python/generate_supplemental_data.py` synthesizes them, fully
consistent with the real ids. Regenerate any time with:

```bash
python python/generate_supplemental_data.py
```

| file                  | grain                    | columns                                                                        |
|-----------------------|--------------------------|--------------------------------------------------------------------------------|
| `sellers.csv`         | seller                   | seller_id, seller_name, seller_city, seller_state                              |
| `product_pricing.csv` | product                  | product_id, unit_price, seller_id                                              |
| `order_items_qty.csv` | order × product (line)   | order_id, product_id, quantity                                                 |
| `order_payments.csv`  | payment (1+ per order)   | order_id, payment_sequential, payment_type, payment_installments, payment_value |
| `order_reviews.csv`   | review (~72% of orders)  | review_id, order_id, review_score, review_creation_date, review_answer_timestamp |
| `order_dates.csv`     | order                    | order_id, order_purchase_timestamp                                             |

**Consistency guarantees (verified):**
- `payment_value` per order sums **exactly** to line revenue `Σ(quantity × unit_price)` (0 mismatches / 200k orders).
- Every synthetic `order_id` / `product_id` exists in the real data (no orphans).
- `order_purchase_timestamp` weekday matches the real `order_dow`, hour matches `order_hour_of_day`; bounded to **2023-01-01 → 2024-12-28** for clean monthly buckets.
- Prices use per-department ranges (charm pricing, e.g. `4.99`); deterministic (seeded) so re-runs reproduce identical data.

> These files are **synthetic** and git-ignored (regenerate via the script). Swap
> in the real [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
> later if you want genuine payments/sellers/reviews.

All analytics in the Phase 9 plan are now possible: **Monthly Revenue, Top
Products, Best Customers, Customer Lifetime Value, Average Order Value, Sales by
Category, Top Sellers** — plus reorder-rate, basket-size, and order-timing.
