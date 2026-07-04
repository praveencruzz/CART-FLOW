"""
Phase 4 - Python Ingestion
==========================
Reads the raw e-commerce CSV, validates its schema, coerces data types,
handles missing values, and writes a cleaned CSV plus a data-quality report.

The raw file is ~2M rows / ~120 MB, so it is processed in chunks to keep
memory usage flat.

Usage:
    python python/ingest.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "ecommerce_consumer_behaviour.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned" / "ecommerce_cleaned.csv"
REPORT_PATH = PROJECT_ROOT / "data" / "cleaned" / "data_quality_report.json"

CHUNK_SIZE = 250_000

# Expected schema: column -> pandas dtype used for coercion.
# Integer columns are read as nullable Int64 so bad values become <NA>
# instead of silently crashing the parser.
SCHEMA: dict[str, str] = {
    "order_id": "Int64",
    "user_id": "Int64",
    "order_number": "Int64",
    "order_dow": "Int64",
    "order_hour_of_day": "Int64",
    "days_since_prior_order": "float64",  # legitimately null on a user's 1st order
    "product_id": "Int64",
    "add_to_cart_order": "Int64",
    "reordered": "Int64",
    "department_id": "Int64",
    "department": "string",
    "product_name": "string",
}

# Rows missing any of these keys are unusable and get dropped.
CRITICAL_KEYS = ["order_id", "user_id", "product_id"]

# Valid ranges used for sanity checks.
RANGE_CHECKS = {
    "order_dow": (0, 6),
    "order_hour_of_day": (0, 23),
    "reordered": (0, 1),
}


def new_report() -> dict:
    return {
        "raw_rows": 0,
        "clean_rows": 0,
        "dropped_missing_keys": 0,
        "nulls_before": {c: 0 for c in SCHEMA},
        "range_violations": {c: 0 for c in RANGE_CHECKS},
        "days_since_prior_nulls": 0,
    }


def clean_chunk(chunk: pd.DataFrame, report: dict) -> pd.DataFrame:
    """Validate, coerce and clean a single chunk; mutate the report in place."""
    report["raw_rows"] += len(chunk)

    # Normalise column names (strip stray whitespace from the header).
    chunk.columns = [c.strip() for c in chunk.columns]

    # Coerce dtypes. errors="coerce" turns un-parseable values into <NA>/NaN.
    for col, dtype in SCHEMA.items():
        if dtype in ("Int64", "float64"):
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce").astype(dtype)
        else:  # string
            chunk[col] = chunk[col].astype("string").str.strip()

    # Count nulls (post-coercion) for the report.
    for col in SCHEMA:
        report["nulls_before"][col] += int(chunk[col].isna().sum())

    # --- Handle missing values -------------------------------------------- #
    # 1. Drop rows missing any critical key.
    before = len(chunk)
    chunk = chunk.dropna(subset=CRITICAL_KEYS)
    report["dropped_missing_keys"] += before - len(chunk)

    # 2. days_since_prior_order is NULL for a user's first order -> keep as-is,
    #    just record how many so the pattern is documented.
    report["days_since_prior_nulls"] += int(chunk["days_since_prior_order"].isna().sum())

    # 3. Categorical text: fill blanks with 'unknown', normalise to lowercase.
    for col in ("department", "product_name"):
        chunk[col] = chunk[col].fillna("unknown").str.lower()

    # --- Range / validity checks ------------------------------------------ #
    for col, (lo, hi) in RANGE_CHECKS.items():
        bad = ~chunk[col].between(lo, hi)
        report["range_violations"][col] += int(bad.sum())
        # Blank out clearly invalid values rather than dropping the whole row.
        chunk.loc[bad, col] = pd.NA

    report["clean_rows"] += len(chunk)
    return chunk


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}")

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = new_report()

    print(f"Reading   : {RAW_PATH}")
    print(f"Writing   : {CLEAN_PATH}")
    print(f"Chunk size: {CHUNK_SIZE:,} rows\n")

    reader = pd.read_csv(RAW_PATH, dtype="string", chunksize=CHUNK_SIZE)
    wrote_header = False

    for i, chunk in enumerate(reader, start=1):
        # Validate schema on the first chunk.
        if not wrote_header:
            missing = set(SCHEMA) - {c.strip() for c in chunk.columns}
            if missing:
                raise ValueError(f"Missing expected columns: {sorted(missing)}")

        cleaned = clean_chunk(chunk, report)
        cleaned.to_csv(
            CLEAN_PATH,
            mode="w" if not wrote_header else "a",
            header=not wrote_header,
            index=False,
        )
        wrote_header = True
        print(f"  chunk {i:>3}: {report['raw_rows']:>10,} rows read")

    # --- Write + print the data-quality report ---------------------------- #
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print("\n=== DATA QUALITY REPORT ===")
    print(f"Raw rows              : {report['raw_rows']:,}")
    print(f"Clean rows            : {report['clean_rows']:,}")
    print(f"Dropped (missing keys): {report['dropped_missing_keys']:,}")
    print(f"days_since_prior nulls: {report['days_since_prior_nulls']:,} (expected: first orders)")
    print(f"Range violations      : {report['range_violations']}")
    print(f"\nReport written to     : {REPORT_PATH}")


if __name__ == "__main__":
    main()
