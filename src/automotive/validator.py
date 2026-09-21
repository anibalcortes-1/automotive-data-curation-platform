"""
Data Validation Module
======================
Validates a raw automotive DataFrame and produces a structured quality report.

Public API:
    validate_dataset(df)  — run all validation checks, return ValidationResult
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain constants
# ---------------------------------------------------------------------------

VALID_FUEL_TYPES    = {"Petrol", "Diesel", "Electric", "Hybrid", "CNG", "LPG"}
VALID_TRANSMISSIONS = {"Automatic", "Manual", "CVT", "DCT", "AMT"}
VALID_VEHICLE_TYPES = {"Sedan", "SUV", "Truck", "Hatchback", "Coupe",
                       "Convertible", "Van", "Wagon"}
MIN_YEAR = 1980
MAX_YEAR = 2025
MIN_PRICE = 0.0
MIN_MILEAGE = 0.0
MIN_ENGINE_CC = 0
MAX_ENGINE_CC = 10_000
EXPECTED_COLUMNS = [
    "vehicle_id", "manufacturer", "model", "vehicle_year", "vehicle_type",
    "fuel_type", "transmission", "engine_cc", "mileage_kmpl", "vehicle_price",
    "units_sold", "service_cost", "manufacturing_region",
]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ColumnReport:
    """Quality metrics for a single column."""

    column:             str
    dtype:              str
    row_count:          int
    missing_count:      int
    missing_pct:        float
    unique_count:       int
    issues:             list[str] = field(default_factory=list)
    validation_status:  str = "OK"

    def to_dict(self) -> dict[str, Any]:
        return {
            "Column":            self.column,
            "Data Type":         self.dtype,
            "Row Count":         self.row_count,
            "Missing Count":     self.missing_count,
            "Missing %":         round(self.missing_pct, 2),
            "Unique Count":      self.unique_count,
            "Issues":            "; ".join(self.issues) if self.issues else "None",
            "Validation Status": self.validation_status,
        }


@dataclass
class ValidationResult:
    """Full validation output for a DataFrame."""

    total_rows:        int
    total_columns:     int
    duplicate_count:   int
    total_missing:     int
    column_reports:    list[ColumnReport]
    invalid_years:     int = 0
    invalid_prices:    int = 0
    invalid_mileage:   int = 0
    invalid_sales:     int = 0
    invalid_engine:    int = 0
    invalid_fuel:      int = 0
    invalid_trans:     int = 0
    missing_columns:   list[str] = field(default_factory=list)

    @property
    def total_invalid(self) -> int:
        return (
            self.invalid_years + self.invalid_prices + self.invalid_mileage
            + self.invalid_sales + self.invalid_engine
            + self.invalid_fuel + self.invalid_trans
        )

    def summary_dict(self) -> dict[str, Any]:
        return {
            "total_rows":      self.total_rows,
            "total_columns":   self.total_columns,
            "duplicate_count": self.duplicate_count,
            "total_missing":   self.total_missing,
            "total_invalid":   self.total_invalid,
            "invalid_years":   self.invalid_years,
            "invalid_prices":  self.invalid_prices,
            "invalid_mileage": self.invalid_mileage,
            "invalid_sales":   self.invalid_sales,
            "invalid_engine":  self.invalid_engine,
            "invalid_fuel":    self.invalid_fuel,
            "invalid_trans":   self.invalid_trans,
            "missing_columns": self.missing_columns,
        }

    def column_report_df(self) -> pd.DataFrame:
        """Return column-level quality report as a DataFrame."""
        return pd.DataFrame([r.to_dict() for r in self.column_reports])


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

def validate_dataset(df: pd.DataFrame) -> ValidationResult:
    """Run comprehensive data validation on *df*.

    Args:
        df: Raw automotive DataFrame.

    Returns:
        ValidationResult with column-level metrics and aggregate stats.
    """
    log.info("Running data validation on %d rows…", len(df))

    n = len(df)

    # ── Missing columns ────────────────────────────────────────────────────
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        log.warning("Missing expected columns: %s", missing_cols)

    # ── Duplicates ────────────────────────────────────────────────────────
    dup_count = int(df.duplicated().sum())

    # ── Per-column reports ─────────────────────────────────────────────────
    col_reports: list[ColumnReport] = []
    for col in df.columns:
        series     = df[col]
        miss_cnt   = int(series.isna().sum())
        miss_pct   = (miss_cnt / n * 100) if n else 0.0
        unique_cnt = int(series.nunique(dropna=True))
        issues: list[str] = []

        if miss_cnt > 0:
            issues.append(f"{miss_cnt} missing values")

        status = "WARNING" if issues else "OK"
        col_reports.append(ColumnReport(
            column=col,
            dtype=str(series.dtype),
            row_count=n,
            missing_count=miss_cnt,
            missing_pct=miss_pct,
            unique_count=unique_cnt,
            issues=issues,
            validation_status=status,
        ))

    # ── Domain-specific checks ─────────────────────────────────────────────
    def _count_invalid(series: pd.Series, mask: pd.Series) -> int:
        return int(mask.sum())

    invalid_years  = 0
    invalid_prices = 0
    invalid_mileage = 0
    invalid_sales  = 0
    invalid_engine = 0
    invalid_fuel   = 0
    invalid_trans  = 0

    if "vehicle_year" in df.columns:
        yr = pd.to_numeric(df["vehicle_year"], errors="coerce")
        mask = yr.notna() & ((yr < MIN_YEAR) | (yr > MAX_YEAR))
        invalid_years = int(mask.sum())

    if "vehicle_price" in df.columns:
        pr = pd.to_numeric(df["vehicle_price"], errors="coerce")
        invalid_prices = int((pr.notna() & (pr < MIN_PRICE)).sum())

    if "mileage_kmpl" in df.columns:
        ml = pd.to_numeric(df["mileage_kmpl"], errors="coerce")
        invalid_mileage = int((ml.notna() & (ml < MIN_MILEAGE)).sum())

    if "units_sold" in df.columns:
        us = pd.to_numeric(df["units_sold"], errors="coerce")
        invalid_sales = int((us.notna() & (us < 0)).sum())

    if "engine_cc" in df.columns:
        ec = pd.to_numeric(df["engine_cc"], errors="coerce")
        invalid_engine = int((ec.notna() & ((ec < MIN_ENGINE_CC) | (ec > MAX_ENGINE_CC))).sum())

    if "fuel_type" in df.columns:
        normed = df["fuel_type"].dropna().str.strip().str.title()
        invalid_fuel = int((~normed.isin(VALID_FUEL_TYPES)).sum())

    if "transmission" in df.columns:
        normed = df["transmission"].dropna().str.strip().str.title()
        invalid_trans = int((~normed.isin(VALID_TRANSMISSIONS)).sum())

    total_missing = int(df.isna().sum().sum())

    result = ValidationResult(
        total_rows=n,
        total_columns=len(df.columns),
        duplicate_count=dup_count,
        total_missing=total_missing,
        column_reports=col_reports,
        invalid_years=invalid_years,
        invalid_prices=invalid_prices,
        invalid_mileage=invalid_mileage,
        invalid_sales=invalid_sales,
        invalid_engine=invalid_engine,
        invalid_fuel=invalid_fuel,
        invalid_trans=invalid_trans,
        missing_columns=missing_cols,
    )

    log.info(
        "Validation complete — duplicates: %d, missing cells: %d, invalid records: %d",
        dup_count, total_missing, result.total_invalid,
    )
    return result
