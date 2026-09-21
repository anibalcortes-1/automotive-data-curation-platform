"""
Dashboard Charts
=================
Thin wrappers over src/automotive/visualizations.py for use in the dashboard.
Provides caching and Streamlit chart rendering helpers.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.automotive import visualizations as viz


@st.cache_data(show_spinner=False)
def cached_sales_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    return viz.chart_sales_by_manufacturer(df)


@st.cache_data(show_spinner=False)
def cached_revenue_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    return viz.chart_revenue_by_manufacturer(df)


@st.cache_data(show_spinner=False)
def cached_sales_by_year(df: pd.DataFrame) -> go.Figure:
    return viz.chart_sales_by_year(df)


@st.cache_data(show_spinner=False)
def cached_sales_trend(df: pd.DataFrame) -> go.Figure:
    return viz.chart_sales_trend(df)


@st.cache_data(show_spinner=False)
def cached_fuel_distribution(df: pd.DataFrame) -> go.Figure:
    return viz.chart_fuel_distribution(df)


@st.cache_data(show_spinner=False)
def cached_vehicle_type_distribution(df: pd.DataFrame) -> go.Figure:
    return viz.chart_vehicle_type_distribution(df)


@st.cache_data(show_spinner=False)
def cached_avg_price_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    return viz.chart_avg_price_by_manufacturer(df)


@st.cache_data(show_spinner=False)
def cached_price_vs_mileage(df: pd.DataFrame) -> go.Figure:
    return viz.chart_price_vs_mileage(df)


@st.cache_data(show_spinner=False)
def cached_price_distribution(df: pd.DataFrame) -> go.Figure:
    return viz.chart_price_distribution(df)


@st.cache_data(show_spinner=False)
def cached_mileage_distribution(df: pd.DataFrame) -> go.Figure:
    return viz.chart_mileage_distribution(df)


@st.cache_data(show_spinner=False)
def cached_vehicle_age_distribution(df: pd.DataFrame) -> go.Figure:
    return viz.chart_vehicle_age_distribution(df)


@st.cache_data(show_spinner=False)
def cached_engine_cc_distribution(df: pd.DataFrame) -> go.Figure:
    return viz.chart_engine_cc_distribution(df)


@st.cache_data(show_spinner=False)
def cached_service_cost_by_manufacturer(df: pd.DataFrame) -> go.Figure:
    return viz.chart_service_cost_by_manufacturer(df)


@st.cache_data(show_spinner=False)
def cached_service_cost_by_type(df: pd.DataFrame) -> go.Figure:
    return viz.chart_service_cost_by_type(df)


@st.cache_data(show_spinner=False)
def cached_age_vs_service_cost(df: pd.DataFrame) -> go.Figure:
    return viz.chart_age_vs_service_cost(df)


@st.cache_data(show_spinner=False)
def cached_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    return viz.chart_correlation_heatmap(df)
