"""
Data Loader Module
==================
Provides functions to load CSV and Excel files into Pandas DataFrames
with comprehensive validation, error handling, and intelligent column mapping.

Public API:
    load_csv(path)                — load a CSV file
    load_excel(path)              — load an Excel file
    load_dataset(path)            — auto-detect format and load
    load_uploaded_file(file_obj)  — load an in-memory uploaded file (CSV / Excel)
    standardize_column_names(df)  — intelligently map automotive column aliases
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

SUPPORTED_CSV_EXTENSIONS   = {".csv", ".tsv"}
SUPPORTED_EXCEL_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}
ALL_SUPPORTED_EXTENSIONS   = SUPPORTED_CSV_EXTENSIONS | SUPPORTED_EXCEL_EXTENSIONS

# Common column name aliases mapped to standard schema
COLUMN_ALIASES: dict[str, str] = {
    # VIN / Vehicle ID
    "vin": "vehicle_id",
    "vehicle_identification_number": "vehicle_id",
    "vin_number": "vehicle_id",
    "chassis_number": "vehicle_id",
    "id": "vehicle_id",
    "vehicle_id": "vehicle_id",
    # Manufacturer / Make
    "manufacturer": "manufacturer",
    "make": "manufacturer",
    "brand": "manufacturer",
    "company": "manufacturer",
    "oem": "manufacturer",
    # Model
    "model": "model",
    "vehicle_model": "model",
    "car_model": "model",
    # Year
    "vehicle_year": "vehicle_year",
    "year": "vehicle_year",
    "model_year": "vehicle_year",
    "manufacturing_year": "vehicle_year",
    "prod_year": "vehicle_year",
    # Vehicle Type / Body
    "vehicle_type": "vehicle_type",
    "body_type": "vehicle_type",
    "type": "vehicle_type",
    "category": "vehicle_type",
    "segment": "vehicle_type",
    # Fuel Type
    "fuel_type": "fuel_type",
    "fuel": "fuel_type",
    "fueltype": "fuel_type",
    # Transmission
    "transmission": "transmission",
    "gearbox": "transmission",
    "trans": "transmission",
    "gear": "transmission",
    # Engine CC
    "engine_cc": "engine_cc",
    "engine_size": "engine_cc",
    "engine_displacement": "engine_cc",
    "displacement": "engine_cc",
    "cc": "engine_cc",
    "engine": "engine_cc",
    # Price
    "price": "vehicle_price",
    "price_usd": "vehicle_price",
    "selling_price": "vehicle_price",
    "cost": "vehicle_price",
    "msrp": "vehicle_price",
    "vehicle_price": "vehicle_price",
    # Mileage
    "mileage": "mileage_kmpl",
    "mileage_kmpl": "mileage_kmpl",
    "fuel_economy": "mileage_kmpl",
    "efficiency": "mileage_kmpl",
    "kmpl": "mileage_kmpl",
    # Units Sold
    "units_sold": "units_sold",
    "sales_count": "units_sold",
    "quantity": "units_sold",
    "sales_volume": "units_sold",
    "volume": "units_sold",
    "sold": "units_sold",
    # Service Cost
    "annual_service_cost": "service_cost",
    "service_cost": "service_cost",
    "maintenance_cost": "service_cost",
    "annual_maintenance_cost": "service_cost",
    "repair_cost": "service_cost",
    # Manufacturing Region
    "manufacturing_region": "manufacturing_region",
    "region": "manufacturing_region",
    "country": "manufacturing_region",
    "origin": "manufacturing_region",
}


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Intelligently map common column names/aliases to the standard schema."""
    rename_map: dict[str, str] = {}
    for col in df.columns:
        norm_col = str(col).strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")
        if norm_col in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[norm_col]

    if rename_map:
        log.info("Mapped columns: %s", rename_map)
        return df.rename(columns=rename_map)
    return df


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_path(path: Path) -> None:
    """Raise ValueError if *path* does not exist or is not a file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")


def _validate_extension(path: Path, allowed: set[str]) -> None:
    """Raise ValueError if *path* extension is not in *allowed*."""
    ext = path.suffix.lower()
    if ext not in allowed:
        raise ValueError(
            f"Unsupported file extension '{ext}'. Expected one of: {sorted(allowed)}"
        )


def _check_not_empty(df: pd.DataFrame, source: Any) -> None:
    """Raise ValueError if *df* has no rows."""
    if df.empty:
        raise ValueError(f"File is empty (0 rows): {source}")


# ---------------------------------------------------------------------------
# Public loaders
# ---------------------------------------------------------------------------

def load_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    """Load a CSV or TSV file into a DataFrame."""
    path = Path(path)
    _validate_path(path)
    _validate_extension(path, SUPPORTED_CSV_EXTENSIONS)

    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    kwargs.setdefault("sep", sep)
    kwargs.setdefault("encoding", "utf-8")
    kwargs.setdefault("low_memory", False)

    log.info("Loading CSV: %s", path)
    try:
        df = pd.read_csv(path, **kwargs)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"File is empty or has no parseable data: {path}") from exc
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV file '{path}': {exc}") from exc

    _check_not_empty(df, path)
    df = standardize_column_names(df)
    log.info("Loaded %d rows × %d columns from '%s'.", *df.shape, path.name)
    return df


def load_excel(path: str | Path, sheet_name: str | int = 0, **kwargs) -> pd.DataFrame:
    """Load an Excel file into a DataFrame."""
    path = Path(path)
    _validate_path(path)
    _validate_extension(path, SUPPORTED_EXCEL_EXTENSIONS)

    log.info("Loading Excel: %s (sheet=%s)", path, sheet_name)
    try:
        df = pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    except Exception as exc:
        raise ValueError(f"Failed to parse Excel file '{path}': {exc}") from exc

    _check_not_empty(df, path)
    df = standardize_column_names(df)
    log.info("Loaded %d rows × %d columns from '%s'.", *df.shape, path.name)
    return df


def load_dataset(path: str | Path, **kwargs) -> pd.DataFrame:
    """Auto-detect file format and load the dataset."""
    path = Path(path)
    ext = path.suffix.lower()

    if ext in SUPPORTED_CSV_EXTENSIONS:
        return load_csv(path, **kwargs)
    if ext in SUPPORTED_EXCEL_EXTENSIONS:
        return load_excel(path, **kwargs)

    raise ValueError(
        f"Cannot determine format for extension '{ext}'. "
        f"Supported: {sorted(ALL_SUPPORTED_EXTENSIONS)}"
    )


def load_uploaded_file(uploaded_file: Any, **kwargs) -> pd.DataFrame:
    """Load a dataset from an in-memory uploaded file object (Streamlit UploadedFile, BytesIO).

    Args:
        uploaded_file: An uploaded file object with ``.name`` and readable content.
        **kwargs: Extra arguments forwarded to ``pd.read_csv`` or ``pd.read_excel``.

    Returns:
        Standardized DataFrame.
    """
    filename = getattr(uploaded_file, "name", "uploaded_data.csv")
    ext = Path(filename).suffix.lower()

    if ext in SUPPORTED_CSV_EXTENSIONS or ext == "":
        # Default to CSV
        try:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, low_memory=False, **kwargs)
        except Exception as exc:
            raise ValueError(f"Failed to parse uploaded CSV file '{filename}': {exc}") from exc
    elif ext in SUPPORTED_EXCEL_EXTENSIONS:
        try:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file, **kwargs)
        except Exception as exc:
            raise ValueError(f"Failed to parse uploaded Excel file '{filename}': {exc}") from exc
    else:
        raise ValueError(
            f"Unsupported file format '{ext}' for uploaded file '{filename}'. "
            f"Expected CSV (.csv, .tsv) or Excel (.xlsx, .xls)."
        )

    _check_not_empty(df, filename)
    df = standardize_column_names(df)
    log.info("Loaded %d rows × %d columns from uploaded file '%s'.", *df.shape, filename)
    return df
