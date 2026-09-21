"""
Data Cleaning Module
====================
Implements a multi-step cleaning pipeline for raw automotive data.
Never modifies the raw dataset — always works on a copy.

Public API:
    clean_dataset(df, output_path=None)  →  CleaningResult
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain constants
# ---------------------------------------------------------------------------

VALID_FUEL_TYPES    = {"Petrol", "Diesel", "Electric", "Hybrid", "CNG", "LPG"}
VALID_TRANSMISSIONS = {"Automatic", "Manual", "CVT", "DCT", "AMT"}
VALID_VEHICLE_TYPES = {"Sedan", "SUV", "Truck", "Hatchback", "Coupe",
                       "Convertible", "Van", "Wagon"}

FUEL_ALIASES: dict[str, str] = {
    "Gas":        "Petrol",
    "Petrol/Gas": "Petrol",
    "Elec":       "Electric",
    "N/A":        "Unknown",
}

TRANSMISSION_ALIASES: dict[str, str] = {
    "Auto": "Automatic",
    "Man":  "Manual",
    "Seq":  "Automatic",
}

MIN_YEAR     = 1980
MAX_YEAR     = 2025
MIN_PRICE    = 1_000
MAX_PRICE    = 500_000
MIN_MILEAGE  = 0.5
MAX_MILEAGE  = 50.0
MIN_ENGINE   = 0
MAX_ENGINE   = 9_000
DEFAULT_YEAR = 2020


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CleaningResult:
    """Summary of all cleaning operations performed."""

    original_records:     int = 0
    duplicates_removed:   int = 0
    missing_filled:       int = 0
    invalid_corrected:    int = 0
    rows_dropped:         int = 0
    final_records:        int = 0
    changes_log:          list[str] = field(default_factory=list)
    cleaned_df:           pd.DataFrame = field(default_factory=pd.DataFrame)

    def summary(self) -> dict[str, Any]:
        return {
            "original_records":   self.original_records,
            "duplicates_removed": self.duplicates_removed,
            "missing_filled":     self.missing_filled,
            "invalid_corrected":  self.invalid_corrected,
            "rows_dropped":       self.rows_dropped,
            "final_records":      self.final_records,
        }


# ---------------------------------------------------------------------------
# Cleaning pipeline
# ---------------------------------------------------------------------------

def clean_dataset(
    df: pd.DataFrame,
    output_path: Path | str | None = None,
) -> CleaningResult:
    """Run the complete cleaning pipeline on *df*.

    Args:
        df:          Raw automotive DataFrame (not modified in place).
        output_path: If provided, save cleaned CSV to this path.

    Returns:
        CleaningResult with cleaned DataFrame and change summary.
    """
    result = CleaningResult(original_records=len(df))
    work   = df.copy()
    log_  = result.changes_log

    # ── Step 0: Ensure essential schema columns exist ─────────────────────
    defaults = {
        "vehicle_id": lambda n: [f"V-{i+1:05d}" for i in range(n)],
        "manufacturer": "Unknown",
        "model": "Standard",
        "vehicle_year": DEFAULT_YEAR,
        "vehicle_type": "Sedan",
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "engine_cc": 1800,
        "mileage_kmpl": 15.0,
        "vehicle_price": 25000.0,
        "units_sold": 100,
        "service_cost": 650.0,
        "manufacturing_region": "Global",
    }
    for col, default_val in defaults.items():
        if col not in work.columns:
            if callable(default_val):
                work[col] = default_val(len(work))
            else:
                work[col] = default_val
            log_.append(f"Injected missing column '{col}' with standard defaults.")

    # ── Step 1: Remove exact duplicates ────────────────────────────────────
    before = len(work)
    work = work.drop_duplicates()
    removed = before - len(work)
    result.duplicates_removed = removed
    if removed:
        log_.append(f"Removed {removed} exact duplicate rows.")

    # ── Step 2: Trim whitespace from string columns ─────────────────────────
    str_cols = work.select_dtypes(include=["object", "str"]).columns
    for col in str_cols:
        before_vals = work[col].copy()
        work[col] = work[col].str.strip()
        changed = (work[col] != before_vals).sum()
        if changed:
            log_.append(f"Trimmed whitespace in '{col}' ({changed} cells).")

    # ── Step 3: Standardise manufacturer names ─────────────────────────────
    if "manufacturer" in work.columns:
        work["manufacturer"] = work["manufacturer"].str.title()

    # ── Step 4: Standardise model names ────────────────────────────────────
    if "model" in work.columns:
        work["model"] = work["model"].str.strip()

    # ── Step 5: Standardise fuel_type ──────────────────────────────────────
    if "fuel_type" in work.columns:
        n_fixed = 0
        def _fix_fuel(val):
            nonlocal n_fixed
            if pd.isna(val):
                return val
            normed = val.strip().title()
            if normed in VALID_FUEL_TYPES:
                return normed
            alias = FUEL_ALIASES.get(normed)
            if alias:
                n_fixed += 1
                return alias
            return normed

        work["fuel_type"] = work["fuel_type"].apply(_fix_fuel)
        if n_fixed:
            log_.append(f"Standardised {n_fixed} fuel_type aliases.")
        result.invalid_corrected += n_fixed

        # Replace entirely invalid values with NaN
        invalid_mask = ~work["fuel_type"].isin(VALID_FUEL_TYPES) & work["fuel_type"].notna()
        n_invalid = invalid_mask.sum()
        if n_invalid:
            work.loc[invalid_mask, "fuel_type"] = np.nan
            log_.append(f"Set {n_invalid} invalid fuel_type values to NaN.")
            result.invalid_corrected += int(n_invalid)

    # ── Step 6: Standardise transmission ───────────────────────────────────
    if "transmission" in work.columns:
        n_fixed = 0
        def _fix_trans(val):
            nonlocal n_fixed
            if pd.isna(val):
                return val
            normed = val.strip().title()
            if normed in VALID_TRANSMISSIONS:
                return normed
            alias = TRANSMISSION_ALIASES.get(normed)
            if alias:
                n_fixed += 1
                return alias
            return normed

        work["transmission"] = work["transmission"].apply(_fix_trans)
        if n_fixed:
            log_.append(f"Standardised {n_fixed} transmission aliases.")
        result.invalid_corrected += n_fixed

        invalid_mask = ~work["transmission"].isin(VALID_TRANSMISSIONS) & work["transmission"].notna()
        n_invalid = invalid_mask.sum()
        if n_invalid:
            work.loc[invalid_mask, "transmission"] = np.nan
            log_.append(f"Set {n_invalid} invalid transmission values to NaN.")
            result.invalid_corrected += int(n_invalid)

    # ── Step 7: Handle invalid vehicle_year ────────────────────────────────
    if "vehicle_year" in work.columns:
        work["vehicle_year"] = pd.to_numeric(work["vehicle_year"], errors="coerce")
        bad_mask = work["vehicle_year"].notna() & (
            (work["vehicle_year"] < MIN_YEAR) | (work["vehicle_year"] > MAX_YEAR)
        )
        n_bad = int(bad_mask.sum())
        if n_bad:
            work.loc[bad_mask, "vehicle_year"] = np.nan
            log_.append(f"Nullified {n_bad} invalid vehicle_year values.")
            result.invalid_corrected += n_bad

        # Fill NaN years with median
        median_year = work["vehicle_year"].median()
        if pd.isna(median_year):
            median_year = DEFAULT_YEAR
        n_null = work["vehicle_year"].isna().sum()
        work["vehicle_year"] = work["vehicle_year"].fillna(int(median_year))
        work["vehicle_year"] = work["vehicle_year"].astype(int)
        if n_null:
            log_.append(f"Filled {n_null} missing vehicle_year with median ({int(median_year)}).")
            result.missing_filled += int(n_null)

    # ── Step 8: Handle invalid vehicle_price ───────────────────────────────
    if "vehicle_price" in work.columns:
        work["vehicle_price"] = pd.to_numeric(work["vehicle_price"], errors="coerce")
        bad_mask = work["vehicle_price"].notna() & (
            (work["vehicle_price"] < MIN_PRICE) | (work["vehicle_price"] > MAX_PRICE)
        )
        n_bad = int(bad_mask.sum())
        if n_bad:
            work.loc[bad_mask, "vehicle_price"] = np.nan
            log_.append(f"Nullified {n_bad} invalid vehicle_price values (<{MIN_PRICE} or >{MAX_PRICE}).")
            result.invalid_corrected += n_bad

        median_price = work["vehicle_price"].median()
        n_null = work["vehicle_price"].isna().sum()
        if n_null and pd.notna(median_price):
            work["vehicle_price"] = work["vehicle_price"].fillna(median_price)
            log_.append(f"Filled {n_null} missing vehicle_price with median ({median_price:.2f}).")
            result.missing_filled += int(n_null)

    # ── Step 9: Handle invalid mileage_kmpl ────────────────────────────────
    if "mileage_kmpl" in work.columns:
        work["mileage_kmpl"] = pd.to_numeric(work["mileage_kmpl"], errors="coerce")
        bad_mask = work["mileage_kmpl"].notna() & (
            (work["mileage_kmpl"] < MIN_MILEAGE) | (work["mileage_kmpl"] > MAX_MILEAGE)
        )
        n_bad = int(bad_mask.sum())
        if n_bad:
            work.loc[bad_mask, "mileage_kmpl"] = np.nan
            log_.append(f"Nullified {n_bad} invalid mileage_kmpl values.")
            result.invalid_corrected += n_bad

        median_mileage = work["mileage_kmpl"].median()
        n_null = work["mileage_kmpl"].isna().sum()
        if n_null and pd.notna(median_mileage):
            work["mileage_kmpl"] = work["mileage_kmpl"].fillna(round(median_mileage, 2))
            log_.append(f"Filled {n_null} missing mileage_kmpl with median ({median_mileage:.2f}).")
            result.missing_filled += int(n_null)

    # ── Step 10: Handle invalid units_sold ─────────────────────────────────
    if "units_sold" in work.columns:
        work["units_sold"] = pd.to_numeric(work["units_sold"], errors="coerce")
        neg_mask = work["units_sold"].notna() & (work["units_sold"] < 0)
        n_neg = int(neg_mask.sum())
        if n_neg:
            work.loc[neg_mask, "units_sold"] = work.loc[neg_mask, "units_sold"].abs()
            log_.append(f"Converted {n_neg} negative units_sold to absolute values.")
            result.invalid_corrected += n_neg

        median_sales = work["units_sold"].median()
        n_null = work["units_sold"].isna().sum()
        if n_null and pd.notna(median_sales):
            work["units_sold"] = work["units_sold"].fillna(int(median_sales))
            log_.append(f"Filled {n_null} missing units_sold with median ({int(median_sales)}).")
            result.missing_filled += int(n_null)
        work["units_sold"] = work["units_sold"].astype("Int64")

    # ── Step 11: Handle invalid engine_cc ──────────────────────────────────
    if "engine_cc" in work.columns:
        work["engine_cc"] = pd.to_numeric(work["engine_cc"], errors="coerce")
        # Negative or absurdly large
        bad_mask = work["engine_cc"].notna() & (
            (work["engine_cc"] < MIN_ENGINE) | (work["engine_cc"] > MAX_ENGINE)
        )
        n_bad = int(bad_mask.sum())
        if n_bad:
            work.loc[bad_mask, "engine_cc"] = np.nan
            log_.append(f"Nullified {n_bad} invalid engine_cc values.")
            result.invalid_corrected += n_bad

        median_engine = work["engine_cc"].median()
        n_null = work["engine_cc"].isna().sum()
        if n_null and pd.notna(median_engine):
            work["engine_cc"] = work["engine_cc"].fillna(int(median_engine))
            log_.append(f"Filled {n_null} missing engine_cc with median ({int(median_engine)}).")
            result.missing_filled += int(n_null)
        work["engine_cc"] = work["engine_cc"].astype("Int64")

    # ── Step 12: Handle missing service_cost ───────────────────────────────
    if "service_cost" in work.columns:
        work["service_cost"] = pd.to_numeric(work["service_cost"], errors="coerce")
        median_sc = work["service_cost"].median()
        n_null = work["service_cost"].isna().sum()
        if n_null and pd.notna(median_sc):
            work["service_cost"] = work["service_cost"].fillna(round(median_sc, 2))
            log_.append(f"Filled {n_null} missing service_cost with median ({median_sc:.2f}).")
            result.missing_filled += int(n_null)

    # ── Step 13: Handle missing categorical columns ─────────────────────────
    cat_modes = {
        "manufacturer":        "Toyota",
        "vehicle_type":        "Sedan",
        "fuel_type":           "Petrol",
        "transmission":        "Automatic",
        "manufacturing_region": "North America",
    }
    for col, fallback in cat_modes.items():
        if col in work.columns:
            n_null = work[col].isna().sum()
            if n_null:
                mode = work[col].mode()
                fill_val = mode.iloc[0] if len(mode) else fallback
                work[col] = work[col].fillna(fill_val)
                log_.append(f"Filled {n_null} missing '{col}' with mode ('{fill_val}').")
                result.missing_filled += int(n_null)

    # ── Step 14: Ensure model is not null ──────────────────────────────────
    if "model" in work.columns:
        n_null = work["model"].isna().sum()
        if n_null:
            work["model"] = work["model"].fillna("Unknown")
            log_.append(f"Filled {n_null} missing model with 'Unknown'.")
            result.missing_filled += int(n_null)

    result.final_records = len(work)
    result.rows_dropped   = result.original_records - result.final_records - result.duplicates_removed
    result.cleaned_df     = work.reset_index(drop=True)

    # ── Save to disk ────────────────────────────────────────────────────────
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.cleaned_df.to_csv(output_path, index=False)
        log.info("Cleaned dataset saved to: %s", output_path)

    log.info(
        "Cleaning complete — original: %d, final: %d, duplicates removed: %d, "
        "missing filled: %d, invalid corrected: %d",
        result.original_records, result.final_records, result.duplicates_removed,
        result.missing_filled, result.invalid_corrected,
    )
    return result
