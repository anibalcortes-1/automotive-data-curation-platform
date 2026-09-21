"""
Analytics Module
=================
Computes all automotive analytics from the transformed DataFrame.
All calculations derive from actual data — nothing is hardcoded.

Public API:
    compute_overall_kpis(df)
    compute_manufacturer_analytics(df)
    compute_vehicle_analytics(df)
    compute_fuel_analytics(df)
    compute_time_analytics(df)
    compute_relationship_analytics(df)
    compute_service_analytics(df)
    run_all_analytics(df)   →  dict
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _numeric(df: pd.DataFrame, col: str) -> pd.Series:
    """Return *col* as a numeric Series, coercing errors to NaN."""
    return pd.to_numeric(df[col], errors="coerce")


# ---------------------------------------------------------------------------
# Overall KPIs
# ---------------------------------------------------------------------------

def compute_overall_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Compute fleet-wide summary KPIs.

    Returns:
        Dict with keys: total_vehicles, total_units_sold, total_sales_value,
        avg_price, avg_mileage, avg_service_cost.
    """
    return {
        "total_vehicles":    len(df),
        "total_units_sold":  int(_numeric(df, "units_sold").sum()),
        "total_sales_value": round(float(_numeric(df, "total_sales_value").sum()), 2),
        "avg_price":         round(float(_numeric(df, "vehicle_price").mean()), 2),
        "avg_mileage":       round(float(_numeric(df, "mileage_kmpl").mean()), 2),
        "avg_service_cost":  round(float(_numeric(df, "service_cost").mean()), 2),
    }


# ---------------------------------------------------------------------------
# Manufacturer analytics
# ---------------------------------------------------------------------------

def compute_manufacturer_analytics(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compute per-manufacturer summaries.

    Returns:
        Dict with DataFrames: sales_by_manufacturer, revenue_by_manufacturer,
        avg_price_by_manufacturer, avg_service_by_manufacturer.
    """
    g = df.groupby("manufacturer", observed=True)

    sales = (
        g["units_sold"].sum()
        .reset_index()
        .rename(columns={"units_sold": "total_units_sold"})
        .sort_values("total_units_sold", ascending=False)
    )

    revenue = (
        g["total_sales_value"].sum()
        .reset_index()
        .rename(columns={"total_sales_value": "total_revenue"})
        .sort_values("total_revenue", ascending=False)
    )

    avg_price = (
        g["vehicle_price"].mean()
        .reset_index()
        .rename(columns={"vehicle_price": "avg_price"})
        .sort_values("avg_price", ascending=False)
    )
    avg_price["avg_price"] = avg_price["avg_price"].round(2)

    avg_service = (
        g["service_cost"].mean()
        .reset_index()
        .rename(columns={"service_cost": "avg_service_cost"})
        .sort_values("avg_service_cost", ascending=False)
    )
    avg_service["avg_service_cost"] = avg_service["avg_service_cost"].round(2)

    return {
        "sales_by_manufacturer":       sales,
        "revenue_by_manufacturer":     revenue,
        "avg_price_by_manufacturer":   avg_price,
        "avg_service_by_manufacturer": avg_service,
    }


# ---------------------------------------------------------------------------
# Vehicle analytics
# ---------------------------------------------------------------------------

def compute_vehicle_analytics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute model-level and distribution analytics.

    Returns:
        Dict with DataFrames and descriptive stats.
    """
    sales_by_model = (
        df.groupby("model", observed=True)["units_sold"]
        .sum()
        .reset_index()
        .rename(columns={"units_sold": "total_units_sold"})
        .sort_values("total_units_sold", ascending=False)
        .head(30)
    )

    vehicle_type_dist = (
        df["vehicle_type"].value_counts().reset_index()
    )
    vehicle_type_dist.columns = ["vehicle_type", "count"]

    price_stats = _numeric(df, "vehicle_price").describe().round(2)
    mileage_stats = _numeric(df, "mileage_kmpl").describe().round(2)
    age_dist = df["vehicle_age"].value_counts().sort_index().reset_index()
    age_dist.columns = ["vehicle_age", "count"]

    return {
        "sales_by_model":     sales_by_model,
        "vehicle_type_dist":  vehicle_type_dist,
        "price_stats":        price_stats,
        "mileage_stats":      mileage_stats,
        "age_distribution":   age_dist,
    }


# ---------------------------------------------------------------------------
# Fuel analytics
# ---------------------------------------------------------------------------

def compute_fuel_analytics(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compute fuel-type breakdown analytics."""
    g = df.groupby("fuel_type", observed=True)

    fuel_dist = (
        df["fuel_type"].value_counts()
        .reset_index()
        .rename(columns={"count": "vehicle_count"})
    )

    sales_by_fuel = (
        g["units_sold"].sum()
        .reset_index()
        .rename(columns={"units_sold": "total_units_sold"})
        .sort_values("total_units_sold", ascending=False)
    )

    avg_price_by_fuel = (
        g["vehicle_price"].mean()
        .reset_index()
        .rename(columns={"vehicle_price": "avg_price"})
        .sort_values("avg_price", ascending=False)
    )
    avg_price_by_fuel["avg_price"] = avg_price_by_fuel["avg_price"].round(2)

    return {
        "fuel_type_distribution": fuel_dist,
        "sales_by_fuel":          sales_by_fuel,
        "avg_price_by_fuel":      avg_price_by_fuel,
    }


# ---------------------------------------------------------------------------
# Time analytics
# ---------------------------------------------------------------------------

def compute_time_analytics(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compute year-wise production and sales trends."""
    g = df.groupby("vehicle_year", observed=True)

    production_by_year = (
        g.size()
        .reset_index(name="vehicle_count")
        .sort_values("vehicle_year")
    )

    sales_by_year = (
        g["units_sold"].sum()
        .reset_index()
        .rename(columns={"units_sold": "total_units_sold"})
        .sort_values("vehicle_year")
    )

    avg_price_by_year = (
        g["vehicle_price"].mean()
        .reset_index()
        .rename(columns={"vehicle_price": "avg_price"})
        .sort_values("vehicle_year")
    )
    avg_price_by_year["avg_price"] = avg_price_by_year["avg_price"].round(2)

    return {
        "production_by_year": production_by_year,
        "sales_by_year":      sales_by_year,
        "avg_price_by_year":  avg_price_by_year,
    }


# ---------------------------------------------------------------------------
# Relationship analytics
# ---------------------------------------------------------------------------

def compute_relationship_analytics(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compute pairwise relationship data for scatter/correlation charts."""
    cols = ["vehicle_price", "mileage_kmpl", "vehicle_age",
            "service_cost", "engine_cc", "units_sold"]
    sample_df = df[cols].dropna().sample(min(1000, len(df)), random_state=42)

    corr = df[cols].corr(numeric_only=True).round(3)

    return {
        "relationship_sample": sample_df.reset_index(drop=True),
        "correlation_matrix":  corr,
    }


# ---------------------------------------------------------------------------
# Service analytics
# ---------------------------------------------------------------------------

def compute_service_analytics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute service-cost analytics."""
    overall_avg = round(float(_numeric(df, "service_cost").mean()), 2)

    by_manufacturer = (
        df.groupby("manufacturer", observed=True)["service_cost"]
        .mean()
        .reset_index()
        .rename(columns={"service_cost": "avg_service_cost"})
        .sort_values("avg_service_cost", ascending=False)
    )
    by_manufacturer["avg_service_cost"] = by_manufacturer["avg_service_cost"].round(2)

    by_type = (
        df.groupby("vehicle_type", observed=True)["service_cost"]
        .mean()
        .reset_index()
        .rename(columns={"service_cost": "avg_service_cost"})
        .sort_values("avg_service_cost", ascending=False)
    )
    by_type["avg_service_cost"] = by_type["avg_service_cost"].round(2)

    if "service_cost_category" in df.columns:
        category_dist = (
            df["service_cost_category"].value_counts()
            .reset_index()
            .rename(columns={"count": "vehicle_count"})
        )
    else:
        category_dist = pd.DataFrame()

    # Age vs service cost sample
    age_vs_sc = (
        df[["vehicle_age", "service_cost"]].dropna()
        .sample(min(800, len(df)), random_state=42)
        .reset_index(drop=True)
    )

    return {
        "overall_avg_service_cost": overall_avg,
        "service_by_manufacturer":  by_manufacturer,
        "service_by_vehicle_type":  by_type,
        "service_category_dist":    category_dist,
        "age_vs_service_cost":      age_vs_sc,
    }


# ---------------------------------------------------------------------------
# All analytics
# ---------------------------------------------------------------------------

def run_all_analytics(df: pd.DataFrame) -> dict[str, Any]:
    """Run every analytics function and return a consolidated dict.

    Args:
        df: Transformed automotive DataFrame.

    Returns:
        Dict with all analytics results.
    """
    log.info("Running all analytics on %d records…", len(df))
    result = {
        "overall":        compute_overall_kpis(df),
        "manufacturer":   compute_manufacturer_analytics(df),
        "vehicle":        compute_vehicle_analytics(df),
        "fuel":           compute_fuel_analytics(df),
        "time":           compute_time_analytics(df),
        "relationships":  compute_relationship_analytics(df),
        "service":        compute_service_analytics(df),
    }
    log.info("Analytics complete.")
    return result
