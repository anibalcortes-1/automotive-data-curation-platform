"""
Tests for src/automotive/loader.py
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.automotive.loader import (
    load_csv, load_excel, load_dataset,
    load_uploaded_file, standardize_column_names,
)


class TestLoadCsv:
    """Tests for load_csv()."""

    def test_load_valid_csv(self, tmp_path: Path, raw_df: pd.DataFrame) -> None:
        f = tmp_path / "test.csv"
        raw_df.to_csv(f, index=False)
        df = load_csv(f)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(raw_df)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_csv(tmp_path / "nonexistent.csv")

    def test_wrong_extension_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("data")
        with pytest.raises(ValueError, match="Unsupported file extension"):
            load_csv(f)

    def test_empty_csv_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.csv"
        f.write_text("")
        with pytest.raises(ValueError):
            load_csv(f)

    def test_columns_preserved(self, tmp_path: Path, raw_df: pd.DataFrame) -> None:
        f = tmp_path / "test.csv"
        raw_df.to_csv(f, index=False)
        df = load_csv(f)
        assert set(df.columns) == set(raw_df.columns)


class TestLoadExcel:
    """Tests for load_excel()."""

    def test_load_valid_excel(self, tmp_path: Path, raw_df: pd.DataFrame) -> None:
        f = tmp_path / "test.xlsx"
        raw_df.to_excel(f, index=False)
        df = load_excel(f)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(raw_df)

    def test_missing_excel_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_excel(tmp_path / "no.xlsx")

    def test_wrong_extension_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "test.csv"
        f.write_text("a,b\n1,2")
        with pytest.raises(ValueError, match="Unsupported file extension"):
            load_excel(f)


class TestLoadDataset:
    """Tests for load_dataset()."""

    def test_auto_detects_csv(self, tmp_path: Path, raw_df: pd.DataFrame) -> None:
        f = tmp_path / "data.csv"
        raw_df.to_csv(f, index=False)
        df = load_dataset(f)
        assert isinstance(df, pd.DataFrame)

    def test_auto_detects_excel(self, tmp_path: Path, raw_df: pd.DataFrame) -> None:
        f = tmp_path / "data.xlsx"
        raw_df.to_excel(f, index=False)
        df = load_dataset(f)
        assert isinstance(df, pd.DataFrame)

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        f.write_text("{}")
        with pytest.raises(ValueError, match="Cannot determine format"):
            load_dataset(f)

    def test_string_path_accepted(self, tmp_path: Path, raw_df: pd.DataFrame) -> None:
        f = tmp_path / "data.csv"
        raw_df.to_csv(f, index=False)
        df = load_dataset(str(f))
        assert len(df) > 0


class TestLoadUploadedFile:
    """Tests for in-memory file uploads and column standardization."""

    def test_load_uploaded_csv(self, raw_df: pd.DataFrame) -> None:
        buf = io.BytesIO(raw_df.to_csv(index=False).encode("utf-8"))
        buf.name = "custom_vehicles.csv"
        df = load_uploaded_file(buf)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(raw_df)

    def test_load_uploaded_excel(self, raw_df: pd.DataFrame) -> None:
        buf = io.BytesIO()
        raw_df.to_excel(buf, index=False)
        buf.seek(0)
        buf.name = "custom_fleet.xlsx"
        df = load_uploaded_file(buf)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(raw_df)

    def test_standardize_column_aliases(self) -> None:
        raw_custom = pd.DataFrame({
            "Make": ["Honda", "Ford"],
            "Model": ["Civic", "F-150"],
            "Year": [2021, 2022],
            "Price": [24000, 45000],
            "Mileage": [16.5, 9.8],
        })
        std = standardize_column_names(raw_custom)
        assert "manufacturer" in std.columns
        assert "model" in std.columns
        assert "vehicle_year" in std.columns
        assert "vehicle_price" in std.columns
        assert "mileage_kmpl" in std.columns

    def test_unsupported_uploaded_format_raises(self) -> None:
        buf = io.BytesIO(b"some content")
        buf.name = "unsupported.pdf"
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_uploaded_file(buf)
