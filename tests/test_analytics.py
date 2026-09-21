"""
Tests for src/automotive/analytics.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.automotive.analytics import (
    compute_overall_kpis,
    compute_manufacturer_analytics,
    compute_vehicle_analytics,
    compute_fuel_analytics,
    compute_time_analytics,
    compute_relationship_analytics,
    compute_service_analytics,
    run_all_analytics,
)


class TestOverallKpis:
    def test_returns_dict(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        assert isinstance(kpis, dict)

    def test_required_keys(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        for key in ("total_vehicles", "total_units_sold", "total_sales_value",
                    "avg_price", "avg_mileage", "avg_service_cost"):
            assert key in kpis

    def test_total_vehicles_matches_len(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        assert kpis["total_vehicles"] == len(transformed_df)

    def test_total_units_sold_positive(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        assert kpis["total_units_sold"] > 0

    def test_total_sales_value_positive(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        assert kpis["total_sales_value"] > 0

    def test_avg_price_reasonable(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        assert 1_000 < kpis["avg_price"] < 500_000

    def test_total_sales_matches_manual(self, transformed_df: pd.DataFrame) -> None:
        kpis = compute_overall_kpis(transformed_df)
        manual = int(pd.to_numeric(transformed_df["units_sold"], errors="coerce").sum())
        assert kpis["total_units_sold"] == manual


class TestManufacturerAnalytics:
    def test_returns_dict_of_dataframes(self, transformed_df: pd.DataFrame) -> None:
        result = compute_manufacturer_analytics(transformed_df)
        assert isinstance(result, dict)
        for key in ("sales_by_manufacturer", "revenue_by_manufacturer",
                    "avg_price_by_manufacturer", "avg_service_by_manufacturer"):
            assert key in result
            assert isinstance(result[key], pd.DataFrame)

    def test_sales_sorted_descending(self, transformed_df: pd.DataFrame) -> None:
        result = compute_manufacturer_analytics(transformed_df)
        sales = result["sales_by_manufacturer"]["total_units_sold"].tolist()
        assert sales == sorted(sales, reverse=True)

    def test_all_manufacturers_present(self, transformed_df: pd.DataFrame) -> None:
        result = compute_manufacturer_analytics(transformed_df)
        mfr_in_data  = set(transformed_df["manufacturer"].dropna().unique())
        mfr_in_result = set(result["sales_by_manufacturer"]["manufacturer"])
        assert mfr_in_data == mfr_in_result


class TestVehicleAnalytics:
    def test_returns_dict(self, transformed_df: pd.DataFrame) -> None:
        result = compute_vehicle_analytics(transformed_df)
        assert isinstance(result, dict)

    def test_required_keys(self, transformed_df: pd.DataFrame) -> None:
        result = compute_vehicle_analytics(transformed_df)
        for key in ("sales_by_model", "vehicle_type_dist", "price_stats",
                    "mileage_stats", "age_distribution"):
            assert key in result

    def test_sales_by_model_is_df(self, transformed_df: pd.DataFrame) -> None:
        result = compute_vehicle_analytics(transformed_df)
        assert isinstance(result["sales_by_model"], pd.DataFrame)


class TestFuelAnalytics:
    def test_returns_dict_of_dfs(self, transformed_df: pd.DataFrame) -> None:
        result = compute_fuel_analytics(transformed_df)
        for key in ("fuel_type_distribution", "sales_by_fuel", "avg_price_by_fuel"):
            assert isinstance(result[key], pd.DataFrame)

    def test_all_fuel_types_present(self, transformed_df: pd.DataFrame) -> None:
        result = compute_fuel_analytics(transformed_df)
        fuel_in_data   = set(transformed_df["fuel_type"].dropna().unique())
        fuel_in_result = set(result["fuel_type_distribution"]["fuel_type"])
        assert fuel_in_data == fuel_in_result


class TestTimeAnalytics:
    def test_returns_dict_of_dfs(self, transformed_df: pd.DataFrame) -> None:
        result = compute_time_analytics(transformed_df)
        for key in ("production_by_year", "sales_by_year", "avg_price_by_year"):
            assert isinstance(result[key], pd.DataFrame)

    def test_sorted_by_year(self, transformed_df: pd.DataFrame) -> None:
        result = compute_time_analytics(transformed_df)
        years = result["sales_by_year"]["vehicle_year"].tolist()
        assert years == sorted(years)


class TestRelationshipAnalytics:
    def test_returns_dict(self, transformed_df: pd.DataFrame) -> None:
        result = compute_relationship_analytics(transformed_df)
        assert "relationship_sample" in result
        assert "correlation_matrix" in result

    def test_correlation_matrix_square(self, transformed_df: pd.DataFrame) -> None:
        result = compute_relationship_analytics(transformed_df)
        corr = result["correlation_matrix"]
        assert corr.shape[0] == corr.shape[1]

    def test_diagonal_all_ones(self, transformed_df: pd.DataFrame) -> None:
        result = compute_relationship_analytics(transformed_df)
        corr = result["correlation_matrix"]
        import numpy as np
        diag = np.diag(corr.values)
        assert all(abs(v - 1.0) < 1e-9 for v in diag)


class TestServiceAnalytics:
    def test_returns_dict(self, transformed_df: pd.DataFrame) -> None:
        result = compute_service_analytics(transformed_df)
        assert isinstance(result, dict)

    def test_required_keys(self, transformed_df: pd.DataFrame) -> None:
        result = compute_service_analytics(transformed_df)
        for key in ("overall_avg_service_cost", "service_by_manufacturer",
                    "service_by_vehicle_type", "age_vs_service_cost"):
            assert key in result

    def test_avg_service_cost_positive(self, transformed_df: pd.DataFrame) -> None:
        result = compute_service_analytics(transformed_df)
        assert result["overall_avg_service_cost"] > 0


class TestRunAllAnalytics:
    def test_returns_all_sections(self, transformed_df: pd.DataFrame) -> None:
        result = run_all_analytics(transformed_df)
        for key in ("overall", "manufacturer", "vehicle", "fuel", "time",
                    "relationships", "service"):
            assert key in result

    def test_overall_kpis_match(self, transformed_df: pd.DataFrame) -> None:
        result = run_all_analytics(transformed_df)
        assert result["overall"]["total_vehicles"] == len(transformed_df)
