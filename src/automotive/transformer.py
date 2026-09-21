"""
Data Transformation Module
===========================
Creates derived features from the cleaned automotive DataFrame.

Public API:
    transform_dataset(df)  →  DataFrame with new feature columns
"""

from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger(__name__)

CURRENT_YEAR = 2024

# ---------------------------------------------------------------------------
# Category bin definitions
# ---------------------------------------------------------------------------

PRICE_BINS   = [0, 20_000, 35_000, 55_000, 100_000, float("inf")]
PRICE_LABELS = ["Budget", "Economy", "Mid-Range", "Premium", "Luxury"]

MILEAGE_BINS   = [0, 10, 15, 20, 25, float("inf")]
MILEAGE_LABELS = ["Very Low", "Low", "Moderate", "High", "Very High"]

SERVICE_BINS   = [0, 500, 1_000, 2_500, 5_000, float("inf")]
SERVICE_LABELS = ["Minimal", "Low", "Moderate", "High", "Very High"]


# ---------------------------------------------------------------------------
# Individual transformations
# ---------------------------------------------------------------------------

def add_vehicle_age(df: pd.DataFrame) -> pd.DataFrame:
    """Add *vehicle_age* column (years since manufacture)."""
    df = df.copy()
    df["vehicle_age"] = (CURRENT_YEAR - df["vehicle_year"].astype(int)).clip(lower=0)
    return df


def add_total_sales_value(df: pd.DataFrame) -> pd.DataFrame:
    """Add *total_sales_value* = vehicle_price × units_sold."""
    df = df.copy()
    price = pd.to_numeric(df["vehicle_price"], errors="coerce").fillna(0)
    sold  = pd.to_numeric(df["units_sold"],    errors="coerce").fillna(0)
    df["total_sales_value"] = (price * sold).round(2)
    return df


def add_price_category(df: pd.DataFrame) -> pd.DataFrame:
    """Add *price_category* (Budget / Economy / Mid-Range / Premium / Luxury)."""
    df = df.copy()
    price = pd.to_numeric(df["vehicle_price"], errors="coerce")
    df["price_category"] = pd.cut(
        price,
        bins=PRICE_BINS,
        labels=PRICE_LABELS,
        right=False,
    ).astype(str)
    df["price_category"] = df["price_category"].replace("nan", "Unknown")
    return df


def add_mileage_category(df: pd.DataFrame) -> pd.DataFrame:
    """Add *mileage_category* based on fuel efficiency (km/L)."""
    df = df.copy()
    mileage = pd.to_numeric(df["mileage_kmpl"], errors="coerce")
    df["mileage_category"] = pd.cut(
        mileage,
        bins=MILEAGE_BINS,
        labels=MILEAGE_LABELS,
        right=False,
    ).astype(str)
    df["mileage_category"] = df["mileage_category"].replace("nan", "Unknown")
    return df


def add_service_cost_category(df: pd.DataFrame) -> pd.DataFrame:
    """Add *service_cost_category* from annual service cost."""
    df = df.copy()
    sc = pd.to_numeric(df["service_cost"], errors="coerce")
    df["service_cost_category"] = pd.cut(
        sc,
        bins=SERVICE_BINS,
        labels=SERVICE_LABELS,
        right=False,
    ).astype(str)
    df["service_cost_category"] = df["service_cost_category"].replace("nan", "Unknown")
    return df


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def transform_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all transformations to *df* and return the enriched DataFrame.

    Args:
        df: Cleaned automotive DataFrame.

    Returns:
        New DataFrame with derived feature columns appended.
    """
    log.info("Running transformations on %d rows…", len(df))

    pipeline = [
        add_vehicle_age,
        add_total_sales_value,
        add_price_category,
        add_mileage_category,
        add_service_cost_category,
    ]
    result = df.copy()
    for step in pipeline:
        result = step(result)
        log.debug("Applied: %s", step.__name__)

    new_cols = [
        "vehicle_age", "total_sales_value",
        "price_category", "mileage_category", "service_cost_category",
    ]
    log.info("Transformation complete. New columns: %s", new_cols)
    return result
