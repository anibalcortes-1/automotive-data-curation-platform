"""Quick runtime verification script."""
import sys
sys.path.insert(0, ".")

from src.automotive.loader import load_csv, load_excel, load_dataset
from src.automotive.validator import validate_dataset
from src.automotive.cleaner import clean_dataset
from src.automotive.transformer import transform_dataset
from src.automotive.analytics import run_all_analytics
from src.automotive.visualizations import chart_sales_by_manufacturer
from src.automotive.reporting import generate_report
from src.automotive.database import DatabaseManager
from dashboard.components import kpi_row, apply_filters
from pathlib import Path

# Test with actual generated data
df_raw = load_dataset(Path("data/sample/automotive_raw.csv"))
print(f"Raw:         {df_raw.shape}")

validation = validate_dataset(df_raw)
print(f"Validation:  dups={validation.duplicate_count}, missing={validation.total_missing}, invalid={validation.total_invalid}")

cleaning = clean_dataset(df_raw)
print(f"Cleaned:     {cleaning.cleaned_df.shape}")

transformed = transform_dataset(cleaning.cleaned_df)
print(f"Transformed: {transformed.shape}")

analytics = run_all_analytics(transformed)
kpis = analytics["overall"]
print(f"KPIs:        vehicles={kpis['total_vehicles']}, revenue=${kpis['total_sales_value']:,.0f}")

fig = chart_sales_by_manufacturer(transformed)
print(f"Chart:       {type(fig).__name__} created OK")

report = generate_report(transformed)
print(f"Report:      {len(report)} chars")

db = DatabaseManager()
db.ensure_tables()
print(f"Database:    tables created OK at {db.db_path}")

print()
print("ALL RUNTIME CHECKS PASSED")
