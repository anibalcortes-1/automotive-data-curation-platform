"""
Tests for src/automotive/cleaner.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.automotive.cleaner import clean_dataset, CleaningResult


class TestCleanDataset:
    """Tests for clean_dataset()."""

    def test_returns_cleaning_result(self, dirty_df: pd.DataFrame) -> None:
        result = clean_dataset(dirty_df)
        assert isinstance(result, CleaningResult)

    def test_does_not_modify_input(self, dirty_df: pd.DataFrame) -> None:
        original_len = len(dirty_df)
        _ = clean_dataset(dirty_df)
        assert len(dirty_df) == original_len, "Input DataFrame was modified."

    def test_removes_duplicates(self, raw_df: pd.DataFrame) -> None:
        # Build a DataFrame with guaranteed exact duplicates (no whitespace or other mutations)
        df_with_dups = pd.concat([raw_df, raw_df.iloc[:5]], ignore_index=True)
        assert df_with_dups.duplicated().sum() == 5, "Fixture setup: expected 5 duplicates"
        result = clean_dataset(df_with_dups)
        assert result.duplicates_removed >= 5, "Expected at least 5 duplicates removed."
        assert result.cleaned_df.duplicated().sum() == 0

    def test_trims_whitespace(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "manufacturer"] = "  Toyota  "
        df.loc[1, "fuel_type"]    = " Petrol "
        result = clean_dataset(df)
        cdf = result.cleaned_df
        assert cdf.loc[0, "manufacturer"] == "Toyota"
        assert cdf.loc[1, "fuel_type"] == "Petrol"

    def test_standardises_manufacturer_case(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "manufacturer"] = "TOYOTA"
        result = clean_dataset(df)
        assert result.cleaned_df.loc[0, "manufacturer"] == "Toyota"

    def test_standardises_fuel_type_aliases(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "fuel_type"] = "Gas"
        result = clean_dataset(df)
        assert result.cleaned_df.loc[0, "fuel_type"] == "Petrol"

    def test_standardises_transmission_aliases(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "transmission"] = "Auto"
        result = clean_dataset(df)
        assert result.cleaned_df.loc[0, "transmission"] == "Automatic"

    def test_nullifies_invalid_years(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "vehicle_year"] = 1800
        df.loc[1, "vehicle_year"] = 2099
        result = clean_dataset(df)
        # Should be replaced with median, not left as 1800/2099
        assert result.cleaned_df.loc[0, "vehicle_year"] != 1800
        assert result.cleaned_df.loc[1, "vehicle_year"] != 2099

    def test_handles_negative_price(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "vehicle_price"] = -25000
        result = clean_dataset(df)
        assert result.cleaned_df.loc[0, "vehicle_price"] > 0

    def test_handles_negative_mileage(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "mileage_kmpl"] = -15.0
        result = clean_dataset(df)
        assert result.cleaned_df.loc[0, "mileage_kmpl"] > 0

    def test_handles_negative_units_sold(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "units_sold"] = -500
        result = clean_dataset(df)
        assert result.cleaned_df.loc[0, "units_sold"] > 0

    def test_fills_missing_numeric(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "mileage_kmpl"]  = np.nan
        df.loc[1, "vehicle_price"] = np.nan
        df.loc[2, "service_cost"]  = np.nan
        result = clean_dataset(df)
        cdf = result.cleaned_df
        assert not cdf["mileage_kmpl"].isna().any()
        assert not cdf["vehicle_price"].isna().any()
        assert not cdf["service_cost"].isna().any()

    def test_fills_missing_categorical(self, raw_df: pd.DataFrame) -> None:
        df = raw_df.copy()
        df.loc[0, "fuel_type"]    = np.nan
        df.loc[1, "transmission"] = np.nan
        result = clean_dataset(df)
        cdf = result.cleaned_df
        assert not cdf["fuel_type"].isna().any()
        assert not cdf["transmission"].isna().any()

    def test_final_records_positive(self, dirty_df: pd.DataFrame) -> None:
        result = clean_dataset(dirty_df)
        assert result.final_records > 0

    def test_changes_log_not_empty(self, dirty_df: pd.DataFrame) -> None:
        result = clean_dataset(dirty_df)
        assert len(result.changes_log) > 0

    def test_saves_csv(self, dirty_df: pd.DataFrame, tmp_path: Path) -> None:
        output = tmp_path / "cleaned.csv"
        result = clean_dataset(dirty_df, output_path=output)
        assert output.exists()
        saved = pd.read_csv(output)
        assert len(saved) == result.final_records

    def test_summary_dict_keys(self, dirty_df: pd.DataFrame) -> None:
        result = clean_dataset(dirty_df)
        s = result.summary()
        expected_keys = {
            "original_records", "duplicates_removed", "missing_filled",
            "invalid_corrected", "rows_dropped", "final_records",
        }
        assert expected_keys.issubset(s.keys())
