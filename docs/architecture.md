# Architecture

## Pipeline flow (medallion)

```
                 ┌─────────────────────────────────────────────────────────────┐
                 │                      SOURCE (Phase 3)                         │
                 │   ecommerce_consumer_behaviour.csv  (~2.02M rows, ~120 MB)    │
                 └───────────────────────────┬─────────────────────────────────┘
                                             │
                     Phase 4 — Python (pandas, chunked)
                     • schema validation   • type coercion
                     • missing-value handling   • range checks
                     • data-quality report
                                             │
                                             ▼
                 ┌─────────────────────────────────────────────────────────────┐
                 │              CLEANED  (data/cleaned/)  — "Silver-in"          │
                 │   ecommerce_cleaned.csv  +  data_quality_report.json          │
                 └───────────────────────────┬─────────────────────────────────┘
                                             │
                     Phase 5 — PySpark (local[*])
                     • de-duplicate   • enforce types
                     • drop invalid records
                     • normalise flat table → modelled datasets
                                             │
                                             ▼
                 ┌─────────────────────────────────────────────────────────────┐
                 │            PROCESSED (data/processed/)  — "Silver"            │
                 │   order_items · orders · dim_products ·                       │
                 │   dim_departments · dim_users     (Parquet)                   │
                 └───────────────────────────┬─────────────────────────────────┘
                                             │
                     Phase 6–7 (next)  → Snowflake Bronze/Silver + star schema
                     Phase 8 (next)    → dbt staging/intermediate/mart (Gold)
                     Phase 9 (next)    → SQL analytics
                     Phase 10 (next)   → BI dashboard
```

## Target star schema (Phase 7 — planned)

The Phase 5 datasets map directly onto a star schema:

- **Fact:** `fact_order_items` ← `order_items` (grain: order × product)
- **Dimensions:** `dim_products`, `dim_departments`, `dim_users`,
  and a `dim_date`/`dim_time` built from `order_dow` + `order_hour_of_day`.

> Revenue-based facts (`fact_payments`) require price/payment data not present in
> the current dataset — see [../data/README.md](../data/README.md).
