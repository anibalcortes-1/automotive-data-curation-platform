"""
Visualizations Module
======================
Builds Plotly figures and Matplotlib/Seaborn charts for the platform.
All chart functions return Plotly Figure objects (for Streamlit compatibility).

Public API:
    chart_sales_by_manufacturer(df)
    chart_sales_by_year(df)
    chart_fuel_distribution(df)
    chart_vehicle_type_distribution(df)
    chart_avg_price_by_manufacturer(df)
    chart_price_vs_mileage(df)
    chart_price_distribution(df)
    chart_mileage_distribution(df)
    chart_vehicle_age_distribution(df)
    chart_engine_cc_distribution(df)
    chart_service_cost_by_manufacturer(df)
    chart_service_cost_by_type(df)
    chart_age_vs_service_cost(df)
    chart_correlation_heatmap(df)
    chart_revenue_by_manufacturer(df)
    chart_sales_trend(df)
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

PALETTE = px.colors.qualitative.Vivid
TEMPLATE = "plotly_dark"


def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent layout to a figure."""
    fig.update_layout(
        template=TEMPLATE,
        title=dict(text=title, x=0.5, font=dict(size=16)),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", y=-0.2),
        height=420,
    )
    return fig


# ---------------------------------------------------------------------------
# Sales / Revenue
# ---------------------------------------------------------------------------

def chart_sales_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    """Bar chart — units sold per manufacturer (top 15)."""
    data = (
        df.groupby("manufacturer", observed=True)["units_sold"]
        .sum()
        .reset_index()
        .sort_values("units_sold", ascending=False)
        .head(15)
    )
    fig = px.bar(
        data, x="manufacturer", y="units_sold",
        color="units_sold", color_continuous_scale="Teal",
        labels={"manufacturer": "Manufacturer", "units_sold": "Units Sold"},
    )
    return _base_layout(fig, "Units Sold by Manufacturer")


def chart_revenue_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar — revenue per manufacturer (top 15)."""
    data = (
        df.groupby("manufacturer", observed=True)["total_sales_value"]
        .sum()
        .reset_index()
        .rename(columns={"total_sales_value": "revenue"})
        .sort_values("revenue", ascending=True)
        .tail(15)
    )
    fig = px.bar(
        data, x="revenue", y="manufacturer",
        orientation="h",
        color="revenue", color_continuous_scale="Sunset",
        labels={"manufacturer": "Manufacturer", "revenue": "Revenue (USD)"},
    )
    return _base_layout(fig, "Revenue by Manufacturer (Top 15)")


def chart_sales_by_year(df: pd.DataFrame) -> go.Figure:
    """Line chart — units sold by model year."""
    data = (
        df.groupby("vehicle_year", observed=True)["units_sold"]
        .sum()
        .reset_index()
        .sort_values("vehicle_year")
    )
    fig = px.line(
        data, x="vehicle_year", y="units_sold",
        markers=True,
        labels={"vehicle_year": "Model Year", "units_sold": "Units Sold"},
        color_discrete_sequence=["#00D4FF"],
    )
    fig.update_traces(line=dict(width=2.5))
    return _base_layout(fig, "Units Sold by Model Year")


def chart_sales_trend(df: pd.DataFrame) -> go.Figure:
    """Area chart — sales trend by year with avg price overlay."""
    by_year = (
        df.groupby("vehicle_year", observed=True)
        .agg(units_sold=("units_sold", "sum"), avg_price=("vehicle_price", "mean"))
        .reset_index()
        .sort_values("vehicle_year")
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=by_year["vehicle_year"], y=by_year["units_sold"],
        fill="tozeroy", name="Units Sold",
        line=dict(color="#00D4FF", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=by_year["vehicle_year"], y=by_year["avg_price"],
        name="Avg Price (USD)", yaxis="y2",
        line=dict(color="#FF6B6B", width=2, dash="dash"),
    ))
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right", title="Avg Price (USD)"),
        yaxis=dict(title="Units Sold"),
        xaxis=dict(title="Model Year"),
    )
    return _base_layout(fig, "Sales Trend & Average Price by Year")


# ---------------------------------------------------------------------------
# Distributions
# ---------------------------------------------------------------------------

def chart_fuel_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart — fuel type distribution."""
    data = df["fuel_type"].value_counts().reset_index()
    data.columns = ["fuel_type", "count"]
    fig = px.pie(
        data, names="fuel_type", values="count",
        hole=0.45, color_discrete_sequence=PALETTE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _base_layout(fig, "Fuel Type Distribution")


def chart_vehicle_type_distribution(df: pd.DataFrame) -> go.Figure:
    """Bar chart — vehicle type counts."""
    data = df["vehicle_type"].value_counts().reset_index()
    data.columns = ["vehicle_type", "count"]
    fig = px.bar(
        data, x="vehicle_type", y="count",
        color="vehicle_type", color_discrete_sequence=PALETTE,
        labels={"vehicle_type": "Vehicle Type", "count": "Count"},
    )
    fig.update_layout(showlegend=False)
    return _base_layout(fig, "Vehicle Type Distribution")


def chart_price_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram — vehicle price distribution."""
    prices = pd.to_numeric(df["vehicle_price"], errors="coerce").dropna()
    fig = px.histogram(
        prices, nbins=50,
        color_discrete_sequence=["#7C3AED"],
        labels={"value": "Vehicle Price (USD)", "count": "Count"},
    )
    return _base_layout(fig, "Vehicle Price Distribution")


def chart_mileage_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram — mileage (km/L) distribution."""
    mileage = pd.to_numeric(df["mileage_kmpl"], errors="coerce").dropna()
    fig = px.histogram(
        mileage, nbins=40,
        color_discrete_sequence=["#10B981"],
        labels={"value": "Mileage (km/L)", "count": "Count"},
    )
    return _base_layout(fig, "Mileage Distribution (km/L)")


def chart_vehicle_age_distribution(df: pd.DataFrame) -> go.Figure:
    """Bar chart — vehicle age distribution."""
    if "vehicle_age" not in df.columns:
        return go.Figure()
    data = df["vehicle_age"].value_counts().sort_index().reset_index()
    data.columns = ["vehicle_age", "count"]
    fig = px.bar(
        data, x="vehicle_age", y="count",
        color="count", color_continuous_scale="Blues",
        labels={"vehicle_age": "Vehicle Age (years)", "count": "Count"},
    )
    return _base_layout(fig, "Vehicle Age Distribution")


def chart_engine_cc_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram — engine displacement distribution."""
    engine = pd.to_numeric(df["engine_cc"], errors="coerce")
    engine = engine[engine > 0].dropna()
    fig = px.histogram(
        engine, nbins=40,
        color_discrete_sequence=["#F59E0B"],
        labels={"value": "Engine Displacement (cc)", "count": "Count"},
    )
    return _base_layout(fig, "Engine Displacement Distribution")


# ---------------------------------------------------------------------------
# Price analytics
# ---------------------------------------------------------------------------

def chart_avg_price_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar — average price per manufacturer."""
    data = (
        df.groupby("manufacturer", observed=True)["vehicle_price"]
        .mean()
        .reset_index()
        .rename(columns={"vehicle_price": "avg_price"})
        .sort_values("avg_price", ascending=True)
    )
    fig = px.bar(
        data, x="avg_price", y="manufacturer",
        orientation="h",
        color="avg_price", color_continuous_scale="Purples",
        labels={"manufacturer": "Manufacturer", "avg_price": "Avg Price (USD)"},
    )
    return _base_layout(fig, "Average Vehicle Price by Manufacturer")


def chart_price_vs_mileage(df: pd.DataFrame) -> go.Figure:
    """Scatter — vehicle price vs mileage coloured by fuel type."""
    sample = df[["vehicle_price", "mileage_kmpl", "fuel_type", "manufacturer"]].dropna()
    sample = sample.sample(min(1500, len(sample)), random_state=42)
    fig = px.scatter(
        sample,
        x="mileage_kmpl", y="vehicle_price",
        color="fuel_type", hover_data=["manufacturer"],
        color_discrete_sequence=PALETTE,
        labels={"mileage_kmpl": "Mileage (km/L)", "vehicle_price": "Price (USD)"},
        opacity=0.65,
    )
    return _base_layout(fig, "Vehicle Price vs Mileage")


# ---------------------------------------------------------------------------
# Service analytics
# ---------------------------------------------------------------------------

def chart_service_cost_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar — avg service cost per manufacturer."""
    data = (
        df.groupby("manufacturer", observed=True)["service_cost"]
        .mean()
        .reset_index()
        .rename(columns={"service_cost": "avg_service_cost"})
        .sort_values("avg_service_cost", ascending=True)
    )
    fig = px.bar(
        data, x="avg_service_cost", y="manufacturer",
        orientation="h",
        color="avg_service_cost", color_continuous_scale="Reds",
        labels={"manufacturer": "Manufacturer", "avg_service_cost": "Avg Service Cost (USD)"},
    )
    return _base_layout(fig, "Average Service Cost by Manufacturer")


def chart_service_cost_by_type(df: pd.DataFrame) -> go.Figure:
    """Bar chart — avg service cost per vehicle type."""
    data = (
        df.groupby("vehicle_type", observed=True)["service_cost"]
        .mean()
        .reset_index()
        .rename(columns={"service_cost": "avg_service_cost"})
        .sort_values("avg_service_cost", ascending=False)
    )
    fig = px.bar(
        data, x="vehicle_type", y="avg_service_cost",
        color="vehicle_type", color_discrete_sequence=PALETTE,
        labels={"vehicle_type": "Vehicle Type", "avg_service_cost": "Avg Service Cost (USD)"},
    )
    fig.update_layout(showlegend=False)
    return _base_layout(fig, "Average Service Cost by Vehicle Type")


def chart_age_vs_service_cost(df: pd.DataFrame) -> go.Figure:
    """Scatter — vehicle age vs service cost."""
    if "vehicle_age" not in df.columns:
        return go.Figure()
    sample = df[["vehicle_age", "service_cost", "manufacturer"]].dropna()
    sample = sample.sample(min(1000, len(sample)), random_state=42)
    fig = px.scatter(
        sample,
        x="vehicle_age", y="service_cost",
        color="vehicle_age", color_continuous_scale="Oranges",
        hover_data=["manufacturer"],
        labels={"vehicle_age": "Vehicle Age (years)", "service_cost": "Service Cost (USD)"},
        opacity=0.65,
        trendline="ols",
    )
    return _base_layout(fig, "Vehicle Age vs Service Cost")


# ---------------------------------------------------------------------------
# Correlation
# ---------------------------------------------------------------------------

def chart_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap — correlation matrix of numeric columns."""
    num_cols = ["vehicle_price", "mileage_kmpl", "vehicle_age",
                "service_cost", "engine_cc", "units_sold"]
    available = [c for c in num_cols if c in df.columns]
    corr = df[available].corr(numeric_only=True).round(2)

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        aspect="auto",
    )
    return _base_layout(fig, "Correlation Heatmap")
