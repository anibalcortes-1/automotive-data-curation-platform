"""
Automated Data Pipeline Script
================================
Runs the complete automotive data pipeline end-to-end:

    1. Generate sample dataset
    2. Load dataset
    3. Validate dataset
    4. Clean dataset
    5. Transform dataset
    6. Run analytics
    7. Generate and save report

Usage:
    python scripts/run_pipeline.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("pipeline")


def run_pipeline() -> None:
    """Execute the full automotive data pipeline."""

    # ── Step 1: Generate sample dataset ─────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 1: Generating synthetic dataset…")
    from scripts.generate_sample_data import generate_dataset

    sample_path = PROJECT_ROOT / "data" / "sample" / "automotive_raw.csv"
    sample_path.parent.mkdir(parents=True, exist_ok=True)

    raw_df = generate_dataset(n_records=5000)
    raw_df.to_csv(sample_path, index=False)
    log.info("Dataset saved: %s (%d rows)", sample_path, len(raw_df))

    # ── Step 2: Load dataset ─────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 2: Loading dataset…")
    from src.automotive.loader import load_dataset

    df = load_dataset(sample_path)
    log.info("Loaded: %d rows × %d columns", *df.shape)

    # ── Step 3: Validate ─────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 3: Validating dataset…")
    from src.automotive.validator import validate_dataset

    validation = validate_dataset(df)
    log.info(
        "Validation — duplicates: %d, missing: %d, invalid: %d",
        validation.duplicate_count,
        validation.total_missing,
        validation.total_invalid,
    )

    # ── Step 4: Clean ─────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 4: Cleaning dataset…")
    from src.automotive.cleaner import clean_dataset

    cleaned_path = PROJECT_ROOT / "data" / "processed" / "automotive_cleaned.csv"
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)

    cleaning = clean_dataset(df, output_path=cleaned_path)
    log.info(
        "Cleaning — original: %d, duplicates removed: %d, final: %d",
        cleaning.original_records,
        cleaning.duplicates_removed,
        cleaning.final_records,
    )

    # ── Step 5: Transform ─────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 5: Transforming dataset…")
    from src.automotive.transformer import transform_dataset

    transformed = transform_dataset(cleaning.cleaned_df)
    log.info("Transformed: %d rows × %d columns", *transformed.shape)

    # ── Step 6: Analytics ─────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 6: Running analytics…")
    from src.automotive.analytics import run_all_analytics

    analytics = run_all_analytics(transformed)
    kpis = analytics["overall"]
    log.info("KPIs:")
    log.info("  Total vehicles:    %d",   kpis["total_vehicles"])
    log.info("  Total units sold:  %d",   kpis["total_units_sold"])
    log.info("  Total revenue:     $%.2f", kpis["total_sales_value"])
    log.info("  Avg price:         $%.2f", kpis["avg_price"])
    log.info("  Avg mileage:       %.2f km/L", kpis["avg_mileage"])
    log.info("  Avg service cost:  $%.2f", kpis["avg_service_cost"])

    # ── Step 7: Report ─────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("STEP 7: Generating report…")
    from src.automotive.reporting import generate_report, save_report

    report = generate_report(
        df=transformed,
        validation_result=validation,
        cleaning_result=cleaning,
        analytics=analytics,
    )
    report_path = PROJECT_ROOT / "reports" / "generated" / "automotive_report.txt"
    save_report(report, report_path)
    log.info("Report saved: %s", report_path)

    log.info("=" * 60)
    log.info("[SUCCESS] PIPELINE COMPLETE")
    log.info("  Raw data:     %s", sample_path)
    log.info("  Cleaned data: %s", cleaned_path)
    log.info("  Report:       %s", report_path)


if __name__ == "__main__":
    run_pipeline()
