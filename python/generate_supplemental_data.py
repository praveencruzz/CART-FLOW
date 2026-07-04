"""
Supplemental synthetic data generator
======================================
The base dataset (Instacart-style baskets) has NO price, seller, payment,
review, or calendar-date information. This script synthesizes those, fully
consistent with the real data, so the revenue / CLV / AOV / star-schema phases
(6-9) become possible.

Everything is keyed to the REAL ids from the cleaned dataset:
  * product_pricing  -> real product_id
  * order_payments   -> real order_id, and payment_value sums to the order total
  * order_reviews    -> real order_id
  * order_dates      -> real order_id, weekday-consistent with order_dow and
                        hour-consistent with order_hour_of_day

Output (written to data/raw/ as additional source files):
  sellers.csv           seller_id, seller_name, seller_city, seller_state
  product_pricing.csv   product_id, unit_price, seller_id
  order_items_qty.csv   order_id, product_id, quantity      (line grain)
  order_payments.csv    order_id, payment_sequential, payment_type,
                        payment_installments, payment_value
  order_reviews.csv     review_id, order_id, review_score,
                        review_creation_date, review_answer_timestamp
  order_dates.csv       order_id, order_purchase_timestamp

Deterministic: fixed seeds + id-based arithmetic -> re-running reproduces the
exact same data.

Usage:
    python python/generate_supplemental_data.py
"""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned" / "ecommerce_cleaned.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

SEED = 42
N_SELLERS = 60
CHUNK_SIZE = 250_000

# Calendar window for synthesized order dates (2 years -> clean monthly buckets).
# 2023-01-01 is a Sunday; order_dow is added on top so weekday stays consistent.
BASE_DATE = date(2023, 1, 1)
NUM_WEEKS = 104

# Per-department unit-price ranges (USD) — plausible grocery/marketplace prices.
DEPARTMENT_PRICE_RANGES: dict[str, tuple[float, float]] = {
    "frozen": (3.0, 9.0),
    "other": (2.0, 8.0),
    "bakery": (2.0, 7.0),
    "produce": (1.0, 6.0),
    "alcohol": (8.0, 40.0),
    "international": (3.0, 12.0),
    "beverages": (1.0, 10.0),
    "pets": (4.0, 25.0),
    "dry goods pasta": (1.0, 6.0),
    "bulk": (3.0, 15.0),
    "personal care": (3.0, 20.0),
    "meat seafood": (5.0, 25.0),
    "pantry": (2.0, 10.0),
    "breakfast": (2.0, 9.0),
    "canned goods": (1.0, 5.0),
    "dairy eggs": (2.0, 8.0),
    "household": (3.0, 18.0),
    "babies": (4.0, 25.0),
    "snacks": (1.0, 8.0),
    "deli": (3.0, 15.0),
    "missing": (1.0, 10.0),
}
DEFAULT_PRICE_RANGE = (2.0, 12.0)

# Reference lists for seller generation.
CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"),
    ("Houston", "TX"), ("Phoenix", "AZ"), ("Philadelphia", "PA"),
    ("San Antonio", "TX"), ("San Diego", "CA"), ("Dallas", "TX"),
    ("Austin", "TX"), ("Seattle", "WA"), ("Denver", "CO"),
    ("Boston", "MA"), ("Atlanta", "GA"), ("Miami", "FL"),
    ("Portland", "OR"), ("Nashville", "TN"), ("Columbus", "OH"),
    ("Minneapolis", "MN"), ("Charlotte", "NC"),
]
SELLER_ADJ = ["Prime", "Fresh", "Global", "Metro", "Sunrise", "Peak", "Urban",
              "Golden", "Blue", "Green", "Rapid", "Elite", "Nova", "Coastal",
              "Summit", "Harbor", "Maple", "Cedar", "Silver", "Union"]
SELLER_NOUN = ["Supply Co.", "Trading", "Wholesale", "Distributors", "Market",
               "Foods", "Mercantile", "Goods", "Provisions", "Traders"]

PAYMENT_TYPES = ["credit_card", "debit_card", "wallet", "voucher", "bank_transfer"]
PAYMENT_TYPE_WEIGHTS = [55, 20, 15, 6, 4]
INSTALLMENT_CHOICES = [1, 2, 3, 4, 5, 6, 10, 12]
INSTALLMENT_WEIGHTS = [40, 15, 12, 10, 8, 6, 5, 4]

QTY_CHOICES = [1, 2, 3, 4, 5, 6, 8]
QTY_WEIGHTS = [45, 25, 13, 7, 4, 3, 3]

REVIEW_PROBABILITY = 0.72
REVIEW_SCORE_CHOICES = [1, 2, 3, 4, 5]
REVIEW_SCORE_WEIGHTS = [10, 8, 12, 25, 45]


# --------------------------------------------------------------------------- #
# Sellers + product pricing (small, deterministic dimensions)
# --------------------------------------------------------------------------- #
def build_sellers() -> list[dict]:
    rng = random.Random(SEED)
    sellers = []
    for sid in range(1, N_SELLERS + 1):
        city, state = rng.choice(CITIES)
        name = f"{rng.choice(SELLER_ADJ)} {rng.choice(SELLER_NOUN)}"
        sellers.append(
            {"seller_id": sid, "seller_name": name,
             "seller_city": city, "seller_state": state}
        )
    return sellers


def build_pricing(products: pd.DataFrame) -> pd.DataFrame:
    """products: distinct product_id + department. Deterministic price/seller."""
    rows = []
    for r in products.itertuples(index=False):
        # Per-product RNG keyed on product_id -> stable across runs.
        pr = random.Random(SEED * 1000 + int(r.product_id))
        lo, hi = DEPARTMENT_PRICE_RANGES.get(r.department, DEFAULT_PRICE_RANGE)
        # Charm pricing: whole/half dollar minus a cent (e.g. 4.99, 7.49).
        price = round(pr.uniform(lo, hi) * 2) / 2 - 0.01
        price = max(0.49, round(price, 2))
        seller_id = pr.randint(1, N_SELLERS)
        rows.append({"product_id": int(r.product_id),
                     "unit_price": price, "seller_id": seller_id})
    return pd.DataFrame(rows).sort_values("product_id")


# --------------------------------------------------------------------------- #
# Order dates (deterministic, weekday/hour-consistent with the real data)
# --------------------------------------------------------------------------- #
def order_timestamp(order_id: int, order_dow: int, order_hour: int) -> datetime:
    week = (order_id * 2654435761) % NUM_WEEKS          # deterministic mix
    d = BASE_DATE + timedelta(days=7 * week + int(order_dow))
    minute = (order_id * 60) % 60
    second = (order_id * 13) % 60
    return datetime(d.year, d.month, d.day, int(order_hour), minute, second)


# --------------------------------------------------------------------------- #
# Payments (split so payment_value sums to the true order total)
# --------------------------------------------------------------------------- #
def build_payments(order_id: int, total: float, rng: random.Random) -> list[dict]:
    total = round(total, 2)
    # ~12% of orders split across two payment rows.
    n_rows = 2 if rng.random() < 0.12 and total > 5 else 1
    rows = []
    if n_rows == 1:
        splits = [total]
    else:
        frac = rng.uniform(0.3, 0.7)
        first = round(total * frac, 2)
        splits = [first, round(total - first, 2)]

    for seq, value in enumerate(splits, start=1):
        ptype = rng.choices(PAYMENT_TYPES, weights=PAYMENT_TYPE_WEIGHTS)[0]
        if ptype == "credit_card":
            inst = rng.choices(INSTALLMENT_CHOICES, weights=INSTALLMENT_WEIGHTS)[0]
        else:
            inst = 1
        rows.append({
            "order_id": order_id,
            "payment_sequential": seq,
            "payment_type": ptype,
            "payment_installments": inst,
            "payment_value": value,
        })
    return rows


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            f"{CLEAN_PATH} not found — run python/ingest.py (Phase 4) first."
        )
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1. Sellers + pricing -------------------------------------------- #
    print("Building sellers + product pricing ...")
    sellers = build_sellers()
    pd.DataFrame(sellers).to_csv(RAW_DIR / "sellers.csv", index=False)

    products = (
        pd.read_csv(CLEAN_PATH, usecols=["product_id", "department"])
        .drop_duplicates("product_id")
    )
    pricing = build_pricing(products)
    pricing.to_csv(RAW_DIR / "product_pricing.csv", index=False)
    price_map = dict(zip(pricing.product_id, pricing.unit_price))
    print(f"  {len(sellers)} sellers, {len(pricing)} priced products")

    # --- 2. Line quantities + per-order totals (streamed) ---------------- #
    print("Assigning line quantities + computing order totals ...")
    rng = random.Random(SEED)
    order_totals: dict[int, float] = {}

    qty_path = RAW_DIR / "order_items_qty.csv"
    with open(qty_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "product_id", "quantity"])
        reader = pd.read_csv(
            CLEAN_PATH, usecols=["order_id", "product_id"], chunksize=CHUNK_SIZE
        )
        for chunk in reader:
            for oid, pid in zip(chunk.order_id.to_numpy(), chunk.product_id.to_numpy()):
                qty = rng.choices(QTY_CHOICES, weights=QTY_WEIGHTS)[0]
                w.writerow([int(oid), int(pid), qty])
                order_totals[int(oid)] = round(
                    order_totals.get(int(oid), 0.0) + qty * price_map.get(int(pid), 0.0), 2
                )
    print(f"  {len(order_totals):,} order totals computed")

    # --- 3. Order-level attributes --------------------------------------- #
    orders = (
        pd.read_csv(
            CLEAN_PATH,
            usecols=["order_id", "order_dow", "order_hour_of_day"],
        )
        .drop_duplicates("order_id")
        .sort_values("order_id")
    )

    # --- 4. Dates + payments + reviews ----------------------------------- #
    print("Generating dates, payments and reviews ...")
    dates_f = open(RAW_DIR / "order_dates.csv", "w", newline="")
    pay_f = open(RAW_DIR / "order_payments.csv", "w", newline="")
    rev_f = open(RAW_DIR / "order_reviews.csv", "w", newline="")
    dw, pw, rw = csv.writer(dates_f), csv.writer(pay_f), csv.writer(rev_f)
    dw.writerow(["order_id", "order_purchase_timestamp"])
    pw.writerow(["order_id", "payment_sequential", "payment_type",
                 "payment_installments", "payment_value"])
    rw.writerow(["review_id", "order_id", "review_score",
                 "review_creation_date", "review_answer_timestamp"])

    n_pay = n_rev = 0
    for r in orders.itertuples(index=False):
        oid = int(r.order_id)
        dow = 0 if pd.isna(r.order_dow) else int(r.order_dow)
        hod = 12 if pd.isna(r.order_hour_of_day) else int(r.order_hour_of_day)

        ts = order_timestamp(oid, dow, hod)
        dw.writerow([oid, ts.strftime("%Y-%m-%d %H:%M:%S")])

        for row in build_payments(oid, order_totals.get(oid, 0.0), rng):
            pw.writerow([row["order_id"], row["payment_sequential"],
                         row["payment_type"], row["payment_installments"],
                         row["payment_value"]])
            n_pay += 1

        if rng.random() < REVIEW_PROBABILITY:
            score = rng.choices(REVIEW_SCORE_CHOICES, weights=REVIEW_SCORE_WEIGHTS)[0]
            created = ts + timedelta(days=rng.randint(1, 10))
            answered = created + timedelta(days=rng.randint(0, 5))
            rw.writerow([f"rev_{oid}", oid, score,
                         created.strftime("%Y-%m-%d %H:%M:%S"),
                         answered.strftime("%Y-%m-%d %H:%M:%S")])
            n_rev += 1

    for fh in (dates_f, pay_f, rev_f):
        fh.close()

    # --- Summary --------------------------------------------------------- #
    tot_vals = list(order_totals.values())
    avg_order = round(sum(tot_vals) / len(tot_vals), 2) if tot_vals else 0
    print("\n=== SUPPLEMENTAL DATA GENERATED ===")
    print(f"  sellers.csv          : {len(sellers)} rows")
    print(f"  product_pricing.csv  : {len(pricing)} rows")
    print(f"  order_items_qty.csv  : {sum(1 for _ in open(qty_path)) - 1:,} rows")
    print(f"  order_dates.csv      : {len(orders):,} rows")
    print(f"  order_payments.csv   : {n_pay:,} rows")
    print(f"  order_reviews.csv    : {n_rev:,} rows ({REVIEW_PROBABILITY:.0%} of orders)")
    print(f"  avg order value      : ${avg_order}")
    print(f"\n  All files written to : {RAW_DIR}")


if __name__ == "__main__":
    main()
