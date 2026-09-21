"""
Tests for src/automotive/transformer.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.automotive.transformer import (
    transform_dataset,
    add_vehicle_age,
    add_total_sales_value,
    add_price_category,
    add_mileage_category,
    add_service_cost_category,
    CURRENT_YEAR,
)


class TestAddVehicleAge:
    def test_age_calculated_correctly(self, cleaned_df: pd.DataFrame) -> None:
        df = add_vehicle_age(cleaned_df)
        assert "vehicle_age" in df.columns
        expected = CURRENT_YEAR - cleaned_df["vehicle_year"]
        pd.testing.assert_series_equal(
            df["vehicle_age"].reset_index(drop=True),
            expected.clip(lower=0).reset_index(drop=True),
            check_names=False,
        )

    def test_age_non_negative(self, cleaned_df: pd.DataFrame) -> None:
        df = add_vehicle_age(cleaned_df)
        assert (df["vehicle_age"] >= 0).all()

    def test_does_not_modify_input(self, cleaned_df: pd.DataFrame) -> None:
        original = cleaned_df.columns.tolist()
        _ = add_vehicle_age(cleaned_df)
        assert cleaned_df.columns.tolist() == original


class TestAddTotalSalesValue:
    def test_sales_value_calculated(self, cleaned_df: pd.DataFrame) -> None:
        df = add_total_sales_value(cleaned_df)
        assert "total_sales_value" in df.columns

    def test_sales_value_equals_price_times_sold(self, cleaned_df: pd.DataFrame) -> None:
        df = add_total_sales_value(cleaned_df)
        price = pd.to_numeric(cleaned_df["vehicle_price"], errors="coerce").fillna(0)
        sold  = pd.to_numeric(cleaned_df["units_sold"],    errors="coerce").fillna(0)
        expected = (price * sold).round(2)
        pd.testing.assert_series_equal(
            df["total_sales_value"].reset_index(drop=True),
            expected.reset_index(drop=True),
            check_names=False,
        )

    def test_sales_value_non_negative(self, cleaned_df: pd.DataFrame) -> None:
        df = add_total_sales_value(cleaned_df)
        assert (df["total_sales_value"] >= 0).all()


class TestAddPriceCategory:
    def test_column_created(self, cleaned_df: pd.DataFrame) -> None:
        df = add_price_category(cleaned_df)
        assert "price_category" in df.columns

    def test_valid_categories(self, cleaned_df: pd.DataFrame) -> None:
        df = add_price_category(cleaned_df)
        valid = {"Budget", "Economy", "Mid-Range", "Premium", "Luxury", "Unknown"}
        assert set(df["price_category"].unique()).issubset(valid)

    def test_luxury_for_high_price(self, cleaned_df: pd.DataFrame) -> None:
        df = cleaned_df.copy()
        df.loc[0, "vehicle_price"] = 200_000
        result = add_price_category(df)
        assert result.loc[0, "price_category"] == "Luxury"

    def test_budget_for_low_price(self, cleaned_df: pd.DataFrame) -> None:
        df = cleaned_df.copy()
        df.loc[0, "vehicle_price"] = 5_000
        result = add_price_category(df)
        assert result.loc[0, "price_category"] == "Budget"


class TestAddMileageCategory:
    def test_column_created(self, cleaned_df: pd.DataFrame) -> None:
        df = add_mileage_category(cleaned_df)
        assert "mileage_category" in df.columns

    def test_valid_categories(self, cleaned_df: pd.DataFrame) -> None:
        df = add_mileage_category(cleaned_df)
        valid = {"Very Low", "Low", "Moderate", "High", "Very High", "Unknown"}
        assert set(df["mileage_category"].unique()).issubset(valid)


class TestAddServiceCostCategory:
    def test_column_created(self, cleaned_df: pd.DataFrame) -> None:
        df = add_service_cost_category(cleaned_df)
        assert "service_cost_category" in df.columns

    def test_valid_categories(self, cleaned_df: pd.DataFrame) -> None:
        df = add_service_cost_category(cleaned_df)
        valid = {"Minimal", "Low", "Moderate", "High", "Very High", "Unknown"}
        assert set(df["service_cost_category"].unique()).issubset(valid)


class TestTransformDataset:
    def test_all_new_columns_present(self, cleaned_df: pd.DataFrame) -> None:
        df = transform_dataset(cleaned_df)
        expected_new = [
            "vehicle_age", "total_sales_value",
            "price_category", "mileage_category", "service_cost_category",
        ]
        for col in expected_new:
            assert col in df.columns, f"Missing column: {col}"

    def test_original_columns_preserved(self, cleaned_df: pd.DataFrame) -> None:
        df = transform_dataset(cleaned_df)
        for col in cleaned_df.columns:
            assert col in df.columns

    def test_row_count_unchanged(self, cleaned_df: pd.DataFrame) -> None:
        df = transform_dataset(cleaned_df)
        assert len(df) == len(cleaned_df)

    def test_does_not_modify_input(self, cleaned_df: pd.DataFrame) -> None:
        original_cols = cleaned_df.columns.tolist()
        _ = transform_dataset(cleaned_df)
        assert cleaned_df.columns.tolist() == original_cols
