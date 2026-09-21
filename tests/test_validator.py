"""
Tests for src/automotive/validator.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.automotive.validator import validate_dataset, ValidationResult


class TestValidateDataset:
    """Tests for validate_dataset()."""

    def test_returns_validation_result(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        assert isinstance(result, ValidationResult)

    def test_total_rows_correct(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        assert result.total_rows == len(raw_df)

    def test_no_duplicates_in_clean_data(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        assert result.duplicate_count == 0

    def test_detects_duplicates(self, raw_df: pd.DataFrame) -> None:
        df_with_dups = pd.concat([raw_df, raw_df.iloc[:5]], ignore_index=True)
        result = validate_dataset(df_with_dups)
        assert result.duplicate_count >= 5

    def test_detects_missing_values(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "mileage_kmpl"] = np.nan
        df.loc[1, "vehicle_price"] = np.nan
        result = validate_dataset(df)
        assert result.total_missing >= 2

    def test_detects_invalid_years(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "vehicle_year"] = 1800
        df.loc[1, "vehicle_year"] = 2099
        result = validate_dataset(df)
        assert result.invalid_years >= 2

    def test_detects_negative_prices(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "vehicle_price"] = -5000
        result = validate_dataset(df)
        assert result.invalid_prices >= 1

    def test_detects_negative_mileage(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "mileage_kmpl"] = -10.0
        result = validate_dataset(df)
        assert result.invalid_mileage >= 1

    def test_detects_negative_sales(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "units_sold"] = -100
        result = validate_dataset(df)
        assert result.invalid_sales >= 1

    def test_detects_invalid_fuel_type(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "fuel_type"] = "Gas"
        df.loc[1, "fuel_type"] = "Unknown"
        result = validate_dataset(df)
        assert result.invalid_fuel >= 2

    def test_detects_invalid_transmission(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "transmission"] = "Auto"
        result = validate_dataset(df)
        assert result.invalid_trans >= 1

    def test_column_report_has_all_columns(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        col_names = [r.column for r in result.column_reports]
        for col in raw_df.columns:
            assert col in col_names

    def test_column_report_df_shape(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        df = result.column_report_df()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(raw_df.columns)

    def test_zero_missing_in_clean_data(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        assert result.total_missing == 0

    def test_total_invalid_property(self, raw_df: pd.DataFrame) -> None:
        result = validate_dataset(raw_df)
        expected = (
            result.invalid_years + result.invalid_prices + result.invalid_mileage
            + result.invalid_sales + result.invalid_engine
            + result.invalid_fuel + result.invalid_trans
        )
        assert result.total_invalid == expected
