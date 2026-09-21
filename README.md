# Automotive Data Analytics & Curation Platform

A production-quality web application for automotive dataset curation, validation, cleaning, feature transformation, interactive analytics, and reporting. Built with Python, Streamlit, and Plotly.

---

## Features

| Capability | Description |
|---|---|
| **Custom Dataset Upload** | Drag-and-drop uncleaned CSV / Excel datasets with automated schema healing and column aliasing |
| **Data Validation** | 9-point automated quality checks with column-level anomaly reports |
| **Data Cleaning** | 14-step cleansing pipeline (deduplication, normalization, range enforcement, outlier resolution) |
| **Data Transformation** | Feature engineering: vehicle age, total sales volume, and categorization bins |
| **Analytics Engine** | 7 analytical domains covering fleet KPIs, manufacturer share, vehicle specs, and maintenance risk |
| **Visualizations** | 16 interactive Plotly charts styled with dark theme aesthetics |
| **Export & Reporting** | One-click cleaned CSV and Excel downloads, plus downloadable text analytics reports |
| **Database Support** | SQLite persistent storage via SQLAlchemy with optional Google Firebase Firestore connectivity |
| **Testing** | 91 comprehensive Pytest unit tests |

---

## Project Structure

```
automotive-data-platform/
├── app.py                          # Streamlit application entry point (7 interactive pages)
├── requirements.txt                # Pinned production dependencies
├── pyproject.toml                  # Tooling and pytest configuration
│
├── .streamlit/
│   └── config.toml                 # Streamlit server and dark theme configuration
│
├── data/
│   ├── raw/                        # Uploaded raw files
│   ├── processed/                  # Output cleaned datasets (CSV / Excel)
│   └── sample/                     # Built-in synthetic dataset (automotive_raw.csv)
│
├── src/automotive/
│   ├── loader.py                   # CSV/Excel & in-memory file loader with column aliasing
│   ├── validator.py                # 9-point data quality validation
│   ├── cleaner.py                  # 14-step cleaning pipeline with schema healing
│   ├── transformer.py              # Feature engineering and derived metrics
│   ├── analytics.py                # 7 domain analytical computations
│   ├── visualizations.py           # Plotly interactive chart builders
│   ├── reporting.py                # Summary and audit report generator
│   └── database.py                 # SQLite + SQLAlchemy ORM & optional Firebase adapter
│
├── dashboard/
│   ├── components.py               # KPI cards, SVG icons, glassmorphic loading popups, export buttons
│   └── charts.py                   # Cached chart rendering wrappers
│
├── scripts/
│   ├── generate_sample_data.py     # Synthetic data generator
│   ├── run_pipeline.py             # CLI batch pipeline execution
│   └── verify_runtime.py           # End-to-end verification script
│
├── tests/
│   ├── conftest.py                 # Pytest fixtures and generators
│   ├── test_loader.py              # File loader and upload tests
│   ├── test_validator.py           # Validation checks tests
│   ├── test_cleaner.py             # Cleansing operations tests
│   ├── test_transformer.py         # Feature engineering tests
│   └── test_analytics.py           # Analytics and KPI tests
│
└── reports/
    └── generated/                  # Generated audit text reports
```

---



## License

MIT License.
