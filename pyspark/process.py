"""
Phase 5 - PySpark Processing
============================
Takes the cleaned CSV from Phase 4 and turns it into modelled, analytics-ready
datasets written as Parquet. This is the "Silver" layer that feeds the
Snowflake Bronze/Silver load (Phase 6) and the star schema (Phase 7).

Steps
-----
1. Read the cleaned CSV with an explicit schema (no type guessing).
2. Enforce / convert data types.
3. Remove duplicate rows.
4. Drop invalid records (bad keys, out-of-range values).
5. Split the flat basket table into normalised, star-schema-ready datasets:
       order_items      (grain: one row per product per order  -> future fact)
       orders           (grain: one row per order)
       dim_products     (product_id, product_name, department_id)
       dim_departments  (department_id, department)
       dim_users        (user_id + per-user order stats)

Usage:
    python pyspark/process.py
"""

from __future__ import annotations

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned" / "ecommerce_cleaned.csv"
OUT_DIR = PROJECT_ROOT / "data" / "processed"

# Explicit schema for the cleaned file -> no inference, deterministic types.
CLEAN_SCHEMA = StructType(
    [
        StructField("order_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("order_number", IntegerType(), True),
        StructField("order_dow", IntegerType(), True),
        StructField("order_hour_of_day", IntegerType(), True),
        StructField("days_since_prior_order", DoubleType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("add_to_cart_order", IntegerType(), True),
        StructField("reordered", IntegerType(), True),
        StructField("department_id", IntegerType(), True),
        StructField("department", StringType(), True),
        StructField("product_name", StringType(), True),
    ]
)


def build_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("ecommerce-phase5-processing")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )


def write_parquet(df, name: str) -> None:
    path = str(OUT_DIR / name)
    df.coalesce(1).write.mode("overwrite").parquet(path)
    print(f"  wrote {name:<16} -> {path}")


def main() -> None:
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    print(f"Reading cleaned data from: {CLEAN_PATH}\n")
    df = spark.read.csv(str(CLEAN_PATH), header=True, schema=CLEAN_SCHEMA)

    raw_count = df.count()

    # --- 2/3/4: enforce validity, then de-duplicate ----------------------- #
    df = (
        df.dropna(subset=["order_id", "user_id", "product_id"])
        .filter(F.col("order_dow").between(0, 6) | F.col("order_dow").isNull())
        .filter(
            F.col("order_hour_of_day").between(0, 23)
            | F.col("order_hour_of_day").isNull()
        )
        .filter(F.col("reordered").isin(0, 1) | F.col("reordered").isNull())
        .dropDuplicates()
    )
    clean_count = df.count()
    df.cache()

    print(f"Rows in  : {raw_count:,}")
    print(f"Rows out : {clean_count:,}  (removed {raw_count - clean_count:,})\n")

    # --- 5: build normalised, star-schema-ready datasets ------------------ #
    print("Building modelled datasets:")

    # order_items -> future fact table (grain: one line = one cart position).
    # NOTE: product_id is aisle-level here (only 134 distinct values), so the
    # same product_id can legitimately appear on several lines of one order.
    # The true line grain is (order_id, add_to_cart_order); de-duping on
    # product_id would merge distinct lines and LOSE real order items.
    order_items = df.select(
        "order_id",
        "user_id",
        "product_id",
        "department_id",
        "add_to_cart_order",
        "reordered",
    ).dropDuplicates(["order_id", "add_to_cart_order"])
    write_parquet(order_items, "order_items")

    # orders -> one row per order (order-level attributes)
    orders = df.select(
        "order_id",
        "user_id",
        "order_number",
        "order_dow",
        "order_hour_of_day",
        "days_since_prior_order",
    ).dropDuplicates(["order_id"])
    write_parquet(orders, "orders")

    # dim_products
    dim_products = df.select(
        "product_id", "product_name", "department_id"
    ).dropDuplicates(["product_id"])
    write_parquet(dim_products, "dim_products")

    # dim_departments
    dim_departments = df.select("department_id", "department").dropDuplicates(
        ["department_id"]
    )
    write_parquet(dim_departments, "dim_departments")

    # dim_users -> user + basic behavioural aggregates
    dim_users = orders.groupBy("user_id").agg(
        F.countDistinct("order_id").alias("total_orders"),
        F.avg("days_since_prior_order").alias("avg_days_between_orders"),
        F.max("order_number").alias("max_order_number"),
    )
    write_parquet(dim_users, "dim_users")

    # --- Summary ---------------------------------------------------------- #
    print("\n=== ROW COUNTS ===")
    for name, d in [
        ("order_items", order_items),
        ("orders", orders),
        ("dim_products", dim_products),
        ("dim_departments", dim_departments),
        ("dim_users", dim_users),
    ]:
        print(f"  {name:<16}: {d.count():>10,}")

    spark.stop()
    print("\nPhase 5 complete.")


if __name__ == "__main__":
    main()
