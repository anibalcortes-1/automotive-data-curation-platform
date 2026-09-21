"""
Reporting Module
=================
Generates text and HTML reports from analytics results.

Public API:
    generate_report(df, validation_result, cleaning_result, analytics)  →  str
    save_report(content, output_path)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _hr(char: str = "─", width: int = 70) -> str:
    return char * width


def _section(title: str) -> str:
    return f"\n{_hr('═')}\n  {title.upper()}\n{_hr('═')}\n"


def _subsection(title: str) -> str:
    return f"\n{_hr('─')}\n  {title}\n{_hr('─')}\n"


def generate_report(
    df: pd.DataFrame,
    validation_result: Any | None = None,
    cleaning_result: Any | None = None,
    analytics: dict[str, Any] | None = None,
) -> str:
    """Generate a full text report of the dataset and analytics.

    Args:
        df:                Transformed DataFrame.
        validation_result: ValidationResult object (optional).
        cleaning_result:   CleaningResult object (optional).
        analytics:         Dict from run_all_analytics() (optional).

    Returns:
        Multi-line string report.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append("AUTOMOTIVE DATA ANALYTICS PLATFORM")
    lines.append(f"Report Generated: {now}")
    lines.append("NOTE: Dataset is ENTIRELY SYNTHETIC — for development only.")

    # ── Dataset Overview ────────────────────────────────────────────────────
    lines.append(_section("Dataset Overview"))
    lines.append(f"  Rows:    {len(df):,}")
    lines.append(f"  Columns: {len(df.columns)}")
    lines.append(f"  Columns: {', '.join(df.columns.tolist())}")

    # ── Data Quality ────────────────────────────────────────────────────────
    if validation_result is not None:
        lines.append(_section("Data Quality Summary"))
        vr = validation_result
        lines.append(f"  Total rows:        {vr.total_rows:,}")
        lines.append(f"  Duplicate rows:    {vr.duplicate_count:,}")
        lines.append(f"  Missing cells:     {vr.total_missing:,}")
        lines.append(f"  Invalid records:   {vr.total_invalid:,}")
        lines.append(f"    Invalid years:   {vr.invalid_years}")
        lines.append(f"    Invalid prices:  {vr.invalid_prices}")
        lines.append(f"    Invalid mileage: {vr.invalid_mileage}")
        lines.append(f"    Invalid sales:   {vr.invalid_sales}")
        lines.append(f"    Invalid engine:  {vr.invalid_engine}")
        lines.append(f"    Invalid fuel:    {vr.invalid_fuel}")
        lines.append(f"    Invalid trans:   {vr.invalid_trans}")

    # ── Cleaning Summary ────────────────────────────────────────────────────
    if cleaning_result is not None:
        lines.append(_section("Cleaning Summary"))
        cr = cleaning_result
        lines.append(f"  Original records:   {cr.original_records:,}")
        lines.append(f"  Duplicates removed: {cr.duplicates_removed:,}")
        lines.append(f"  Missing filled:     {cr.missing_filled:,}")
        lines.append(f"  Invalid corrected:  {cr.invalid_corrected:,}")
        lines.append(f"  Final records:      {cr.final_records:,}")
        lines.append("")
        lines.append("  Change Log:")
        for entry in cr.changes_log[:30]:
            lines.append(f"    • {entry}")

    # ── KPI Summary ─────────────────────────────────────────────────────────
    if analytics and "overall" in analytics:
        lines.append(_section("Key Performance Indicators"))
        kpi = analytics["overall"]
        lines.append(f"  Total Vehicles:       {kpi['total_vehicles']:,}")
        lines.append(f"  Total Units Sold:     {kpi['total_units_sold']:,}")
        lines.append(f"  Total Revenue:        ${kpi['total_sales_value']:,.2f}")
        lines.append(f"  Avg Vehicle Price:    ${kpi['avg_price']:,.2f}")
        lines.append(f"  Avg Mileage (km/L):   {kpi['avg_mileage']:.2f}")
        lines.append(f"  Avg Service Cost:     ${kpi['avg_service_cost']:,.2f}")

    # ── Manufacturer Analytics ──────────────────────────────────────────────
    if analytics and "manufacturer" in analytics:
        lines.append(_section("Manufacturer Analytics"))
        mfr = analytics["manufacturer"]

        lines.append(_subsection("Top 10 by Units Sold"))
        df_sales = mfr["sales_by_manufacturer"].head(10)
        for _, row in df_sales.iterrows():
            lines.append(f"  {row['manufacturer']:<20} {row['total_units_sold']:>10,} units")

        lines.append(_subsection("Top 10 by Revenue"))
        df_rev = mfr["revenue_by_manufacturer"].head(10)
        for _, row in df_rev.iterrows():
            lines.append(f"  {row['manufacturer']:<20} ${row['total_revenue']:>15,.2f}")

    # ── Fuel Type Analytics ─────────────────────────────────────────────────
    if analytics and "fuel" in analytics:
        lines.append(_section("Fuel Type Analytics"))
        fuel = analytics["fuel"]
        df_fuel = fuel["fuel_type_distribution"]
        for _, row in df_fuel.iterrows():
            lines.append(f"  {row['fuel_type']:<12} {row['vehicle_count']:>6,} vehicles")

    # ── Time Analytics ──────────────────────────────────────────────────────
    if analytics and "time" in analytics:
        lines.append(_section("Year-wise Analytics"))
        time_data = analytics["time"]
        df_yr = time_data["sales_by_year"].tail(10)
        for _, row in df_yr.iterrows():
            lines.append(
                f"  {int(row['vehicle_year'])}: {row['total_units_sold']:>8,} units sold"
            )

    # ── Key Observations ────────────────────────────────────────────────────
    lines.append(_section("Key Observations"))
    if analytics:
        overall = analytics.get("overall", {})
        lines.append(f"  • The dataset contains {overall.get('total_vehicles', 0):,} vehicle records.")
        lines.append(f"  • Total sales revenue: ${overall.get('total_sales_value', 0):,.0f}.")
        lines.append(f"  • Average vehicle price: ${overall.get('avg_price', 0):,.2f}.")
        lines.append(f"  • Average fuel efficiency: {overall.get('avg_mileage', 0):.2f} km/L.")
        lines.append(f"  • Average annual service cost: ${overall.get('avg_service_cost', 0):,.2f}.")

    lines.append("\n" + _hr("═"))
    lines.append("END OF REPORT")
    lines.append(_hr("═"))
    return "\n".join(lines)


def save_report(content: str, output_path: Path | str) -> Path:
    """Save *content* to *output_path*.

    Args:
        content:     Report text.
        output_path: File path to write.

    Returns:
        Resolved path to the saved file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    log.info("Report saved to: %s", path)
    return path
