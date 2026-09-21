"""
Pytest fixtures shared across all test modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Fixture: minimal valid automotive DataFrame
# ---------------------------------------------------------------------------

@pytest.fixture()
def raw_df() -> pd.DataFrame:
    """A small clean automotive DataFrame."""
    return pd.DataFrame({
        "vehicle_id":         [f"VH{i:05d}" for i in range(1, 21)],
        "manufacturer":       ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz",
                               "Hyundai", "Volkswagen", "Nissan", "Chevrolet", "Kia",
                               "Audi", "Subaru", "Mazda", "Jeep", "Ram",
                               "Tesla", "Lexus", "Volvo", "Porsche", "Land Rover"],
        "model":              ["Camry", "Civic", "F-150", "X3", "C-Class",
                               "Tucson", "Golf", "Altima", "Silverado", "Sportage",
                               "A4", "Outback", "CX-5", "Wrangler", "1500",
                               "Model 3", "RX", "XC90", "Cayenne", "Defender"],
        "vehicle_year":       [2020, 2019, 2021, 2018, 2022,
                               2020, 2017, 2023, 2016, 2021,
                               2019, 2022, 2020, 2018, 2023,
                               2021, 2019, 2020, 2022, 2023],
        "vehicle_type":       ["Sedan", "Sedan", "Truck", "SUV", "Sedan",
                               "SUV", "Hatchback", "Sedan", "Truck", "SUV",
                               "Sedan", "Wagon", "SUV", "SUV", "Truck",
                               "Sedan", "SUV", "SUV", "SUV", "SUV"],
        "fuel_type":          ["Petrol", "Petrol", "Petrol", "Diesel", "Diesel",
                               "Hybrid", "Petrol", "Petrol", "Petrol", "Hybrid",
                               "Diesel", "Petrol", "Petrol", "Petrol", "Diesel",
                               "Electric", "Hybrid", "Diesel", "Petrol", "Diesel"],
        "transmission":       ["Automatic"] * 20,
        "engine_cc":          [2000, 1500, 3500, 2000, 1800,
                               2000, 1400, 2500, 5300, 2000,
                               2000, 2500, 2500, 3600, 5700,
                               0, 3500, 2000, 3000, 2000],
        "mileage_kmpl":       [15.0, 17.0, 10.0, 12.0, 11.0,
                               14.0, 16.0, 13.0, 9.0, 15.0,
                               12.0, 13.0, 14.0, 11.0, 9.0,
                               6.5, 14.0, 12.0, 11.0, 10.0],
        "vehicle_price":      [25000, 22000, 40000, 55000, 48000,
                               28000, 24000, 26000, 52000, 30000,
                               45000, 32000, 33000, 38000, 45000,
                               55000, 55000, 58000, 120000, 90000],
        "units_sold":         [1200, 1500, 2000, 800, 600,
                               1100, 900, 1000, 2500, 1300,
                               700, 800, 950, 1600, 1800,
                               500, 600, 400, 200, 300],
        "service_cost":       [800, 700, 1200, 1500, 1300,
                               900, 750, 850, 1400, 950,
                               1300, 900, 1000, 1100, 1300,
                               500, 1200, 1100, 2500, 2200],
        "manufacturing_region": ["Asia Pacific"] * 10 + ["Europe"] * 5 + ["North America"] * 5,
    })


@pytest.fixture()
def dirty_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame with injected data-quality problems."""
    df = raw_df.copy()

    # Duplicates
    df = pd.concat([df, df.iloc[:3]], ignore_index=True)

    # Missing values
    df.loc[0, "mileage_kmpl"]  = np.nan
    df.loc[1, "vehicle_price"] = np.nan
    df.loc[2, "transmission"]  = np.nan
    df.loc[3, "fuel_type"]     = np.nan

    # Whitespace
    df.loc[4, "manufacturer"] = "  Toyota  "
    df.loc[5, "fuel_type"]    = " Petrol "

    # Bad capitalisation
    df.loc[6, "manufacturer"] = "HONDA"
    df.loc[7, "fuel_type"]    = "petrol"

    # Invalid categorical
    df.loc[8,  "fuel_type"]    = "Gas"
    df.loc[9,  "transmission"] = "Auto"

    # Negative values
    df.loc[10, "vehicle_price"] = -25000
    df.loc[11, "mileage_kmpl"]  = -15.0
    df.loc[12, "units_sold"]    = -500

    # Invalid year
    df.loc[13, "vehicle_year"]  = 1890
    df.loc[14, "vehicle_year"]  = 2099

    return df


@pytest.fixture()
def cleaned_df(dirty_df: pd.DataFrame) -> pd.DataFrame:
    """Run the cleaning pipeline and return the cleaned DataFrame."""
    from src.automotive.cleaner import clean_dataset
    result = clean_dataset(dirty_df)
    return result.cleaned_df


@pytest.fixture()
def transformed_df(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to cleaned data."""
    from src.automotive.transformer import transform_dataset
    return transform_dataset(cleaned_df)
