"""
Synthetic Automotive Dataset Generator
=======================================
Generates realistic synthetic automotive data for development and testing.
This dataset is ENTIRELY SYNTHETIC — it does NOT represent real vehicles,
sales figures, or market data.

Usage:
    python scripts/generate_sample_data.py
"""

from __future__ import annotations

import logging
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so src/ imports work
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SEED = 42
RNG = np.random.default_rng(SEED)
random.seed(SEED)

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------
MANUFACTURERS = [
    "Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz",
    "Hyundai", "Volkswagen", "Nissan", "Chevrolet", "Kia",
    "Audi", "Subaru", "Mazda", "Jeep", "Ram",
    "Tesla", "Lexus", "Volvo", "Porsche", "Land Rover",
]

MODELS: dict[str, list[str]] = {
    "Toyota":       ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma", "Prius"],
    "Honda":        ["Civic", "Accord", "CR-V", "Pilot", "HR-V", "Ridgeline"],
    "Ford":         ["F-150", "Mustang", "Explorer", "Escape", "Edge", "Bronco"],
    "BMW":          ["3 Series", "5 Series", "X3", "X5", "7 Series", "M3"],
    "Mercedes-Benz":["C-Class", "E-Class", "GLE", "GLC", "S-Class", "AMG GT"],
    "Hyundai":      ["Tucson", "Santa Fe", "Elantra", "Sonata", "Kona", "Palisade"],
    "Volkswagen":   ["Golf", "Passat", "Tiguan", "Atlas", "Jetta", "ID.4"],
    "Nissan":       ["Altima", "Rogue", "Sentra", "Pathfinder", "Murano", "Frontier"],
    "Chevrolet":    ["Silverado", "Equinox", "Malibu", "Tahoe", "Colorado", "Blazer"],
    "Kia":          ["Sportage", "Sorento", "Forte", "Telluride", "Soul", "Carnival"],
    "Audi":         ["A4", "A6", "Q5", "Q7", "A3", "e-tron"],
    "Subaru":       ["Outback", "Forester", "Impreza", "Crosstrek", "Legacy", "WRX"],
    "Mazda":        ["Mazda3", "Mazda6", "CX-5", "CX-9", "MX-5 Miata", "CX-30"],
    "Jeep":         ["Wrangler", "Grand Cherokee", "Cherokee", "Compass", "Renegade", "Gladiator"],
    "Ram":          ["1500", "2500", "3500", "ProMaster", "Dakota"],
    "Tesla":        ["Model 3", "Model S", "Model X", "Model Y", "Cybertruck"],
    "Lexus":        ["RX", "NX", "ES", "GX", "IS", "LS"],
    "Volvo":        ["XC90", "XC60", "S60", "V60", "XC40", "C40"],
    "Porsche":      ["Cayenne", "Macan", "911", "Panamera", "Taycan", "Boxster"],
    "Land Rover":   ["Defender", "Discovery", "Range Rover", "Evoque", "Freelander"],
}

VEHICLE_TYPES = ["Sedan", "SUV", "Truck", "Hatchback", "Coupe", "Convertible", "Van", "Wagon"]
FUEL_TYPES    = ["Petrol", "Diesel", "Electric", "Hybrid", "CNG", "LPG"]
TRANSMISSIONS = ["Automatic", "Manual", "CVT", "DCT", "AMT"]
REGIONS       = [
    "North America", "Europe", "Asia Pacific", "South Asia",
    "Middle East", "Latin America", "Africa",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _manufacturer_vehicle_type(manufacturer: str) -> str:
    """Assign a biased vehicle type for realism."""
    bias: dict[str, list[str]] = {
        "Tesla":        ["Sedan", "SUV"],
        "Porsche":      ["Coupe", "SUV", "Convertible"],
        "Land Rover":   ["SUV"],
        "Ram":          ["Truck", "Van"],
        "Jeep":         ["SUV"],
        "Ford":         ["Truck", "SUV", "Sedan"],
        "Chevrolet":    ["Truck", "SUV", "Sedan"],
    }
    types = bias.get(manufacturer, VEHICLE_TYPES)
    return random.choice(types)


def _base_price(manufacturer: str, vehicle_type: str, fuel_type: str) -> float:
    """Generate a realistic base price (USD)."""
    luxury = {"BMW", "Mercedes-Benz", "Audi", "Lexus", "Porsche", "Land Rover", "Tesla", "Volvo"}
    base = 45_000 if manufacturer in luxury else 25_000
    type_mult = {"Truck": 1.15, "SUV": 1.10, "Van": 1.05, "Sedan": 1.0,
                 "Hatchback": 0.90, "Coupe": 1.05, "Convertible": 1.12, "Wagon": 1.02}
    fuel_mult = {"Electric": 1.25, "Hybrid": 1.10, "Diesel": 1.05,
                 "Petrol": 1.0, "CNG": 0.95, "LPG": 0.93}
    noise = RNG.normal(1.0, 0.12)
    return round(base * type_mult.get(vehicle_type, 1.0) * fuel_mult.get(fuel_type, 1.0) * noise, 2)


def _mileage(fuel_type: str) -> float:
    """Generate fuel efficiency (km/L) appropriate to fuel type."""
    ranges = {
        "Petrol":   (8, 20), "Diesel":   (10, 25),
        "Electric": (5,  15), "Hybrid":   (15, 35),
        "CNG":      (12, 22), "LPG":      (9, 18),
    }
    lo, hi = ranges.get(fuel_type, (8, 20))
    return round(float(RNG.uniform(lo, hi)), 2)


def _engine_cc(fuel_type: str, vehicle_type: str) -> int:
    """Generate engine displacement in cc."""
    if fuel_type == "Electric":
        return 0
    base_map = {"Truck": (2500, 6200), "SUV": (1500, 5000), "Van": (1800, 3500)}
    lo, hi = base_map.get(vehicle_type, (1000, 3500))
    return int(RNG.integers(lo, hi))


def _service_cost(vehicle_price: float, vehicle_age: int) -> float:
    """Annual service cost correlated with age and price."""
    base = vehicle_price * 0.03
    age_factor = 1 + 0.05 * vehicle_age
    noise = RNG.normal(1.0, 0.15)
    return round(max(200, base * age_factor * noise), 2)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_dataset(n_records: int = 5000) -> pd.DataFrame:
    """Generate a synthetic automotive dataset with realistic quality issues.

    Args:
        n_records: Number of records to generate.

    Returns:
        DataFrame with intentional data-quality problems.
    """
    log.info("Generating %d synthetic automotive records (seed=%d)…", n_records, SEED)

    records = []
    current_year = 2024

    for i in range(n_records):
        manufacturer = random.choice(MANUFACTURERS)
        model        = random.choice(MODELS[manufacturer])
        vehicle_year = int(RNG.integers(2005, current_year + 1))
        vehicle_type = _manufacturer_vehicle_type(manufacturer)
        fuel_type    = random.choice(FUEL_TYPES)
        transmission = random.choice(TRANSMISSIONS)
        engine_cc    = _engine_cc(fuel_type, vehicle_type)
        mileage      = _mileage(fuel_type)
        price        = _base_price(manufacturer, vehicle_type, fuel_type)
        units_sold   = int(RNG.integers(1, 5001))
        vehicle_age  = current_year - vehicle_year
        service_cost = _service_cost(price, vehicle_age)
        region       = random.choice(REGIONS)

        records.append({
            "vehicle_id":         f"VH{i + 1:05d}",
            "manufacturer":       manufacturer,
            "model":              model,
            "vehicle_year":       vehicle_year,
            "vehicle_type":       vehicle_type,
            "fuel_type":          fuel_type,
            "transmission":       transmission,
            "engine_cc":          engine_cc,
            "mileage_kmpl":       mileage,
            "vehicle_price":      price,
            "units_sold":         units_sold,
            "service_cost":       service_cost,
            "manufacturing_region": region,
        })

    df = pd.DataFrame(records)

    # -----------------------------------------------------------------------
    # Inject realistic data-quality problems
    # -----------------------------------------------------------------------
    log.info("Injecting data-quality issues…")

    n = len(df)
    idx = df.index.tolist()

    # 1. Missing values (random NaN injection across several columns)
    missing_cols = ["mileage_kmpl", "engine_cc", "service_cost", "transmission", "fuel_type"]
    for col in missing_cols:
        missing_idx = RNG.choice(idx, size=int(n * 0.04), replace=False)
        df.loc[missing_idx, col] = np.nan

    missing_price_idx = RNG.choice(idx, size=int(n * 0.02), replace=False)
    df.loc[missing_price_idx, "vehicle_price"] = np.nan

    missing_mfr_idx = RNG.choice(idx, size=int(n * 0.01), replace=False)
    df.loc[missing_mfr_idx, "manufacturer"] = np.nan

    # 2. Duplicate rows (inject ~80 duplicates)
    dup_src = RNG.choice(idx, size=80, replace=False)
    dup_rows = df.loc[dup_src].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 3. Leading/trailing whitespace
    ws_idx = RNG.choice(df.index.tolist(), size=150, replace=False)
    df.loc[ws_idx, "manufacturer"] = df.loc[ws_idx, "manufacturer"].apply(
        lambda v: f"  {v}  " if isinstance(v, str) else v
    )
    df.loc[ws_idx, "fuel_type"] = df.loc[ws_idx, "fuel_type"].apply(
        lambda v: f" {v} " if isinstance(v, str) else v
    )

    # 4. Inconsistent capitalisation
    cap_idx = RNG.choice(df.index.tolist(), size=120, replace=False)
    df.loc[cap_idx, "manufacturer"] = df.loc[cap_idx, "manufacturer"].apply(
        lambda v: v.upper() if isinstance(v, str) else v
    )
    df.loc[cap_idx, "fuel_type"] = df.loc[cap_idx, "fuel_type"].apply(
        lambda v: v.lower() if isinstance(v, str) else v
    )

    # 5. Invalid categorical values
    bad_fuel_idx   = RNG.choice(df.index.tolist(), size=30, replace=False)
    bad_trans_idx  = RNG.choice(df.index.tolist(), size=25, replace=False)
    df.loc[bad_fuel_idx,  "fuel_type"]    = RNG.choice(["Gas", "Elec", "Petrol/Gas", "N/A", "Unknown"], size=30)
    df.loc[bad_trans_idx, "transmission"] = RNG.choice(["Auto", "Man", "Seq", "Unknown"], size=25)

    # 6. Invalid numeric values (negative prices, mileage, units)
    neg_price_idx = RNG.choice(df.index.tolist(), size=20, replace=False)
    df.loc[neg_price_idx, "vehicle_price"] = -1 * abs(df.loc[neg_price_idx, "vehicle_price"])

    neg_mileage_idx = RNG.choice(df.index.tolist(), size=15, replace=False)
    df.loc[neg_mileage_idx, "mileage_kmpl"] = -1 * abs(df.loc[neg_mileage_idx, "mileage_kmpl"])

    neg_sales_idx = RNG.choice(df.index.tolist(), size=10, replace=False)
    df.loc[neg_sales_idx, "units_sold"] = -1 * abs(df.loc[neg_sales_idx, "units_sold"])

    # 7. Invalid years (future or implausibly old)
    bad_year_idx = RNG.choice(df.index.tolist(), size=25, replace=False)
    df.loc[bad_year_idx, "vehicle_year"] = RNG.choice(
        [1890, 1950, 2030, 2040, 2099], size=25
    )

    # 8. Extreme engine_cc outliers
    big_eng_idx = RNG.choice(df.index.tolist(), size=15, replace=False)
    df.loc[big_eng_idx, "engine_cc"] = RNG.choice([0, -500, 99999], size=15)

    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    log.info("Dataset generated: %d rows × %d columns", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Generate and save the synthetic dataset."""
    output_path = PROJECT_ROOT / "data" / "sample" / "automotive_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_dataset(n_records=5000)

    df.to_csv(output_path, index=False)
    log.info("Dataset saved to: %s", output_path)
    log.info("Shape: %d rows × %d columns", *df.shape)
    log.info("\nColumn dtypes:\n%s", df.dtypes.to_string())
    log.info("\nMissing values per column:\n%s", df.isnull().sum().to_string())


if __name__ == "__main__":
    main()
