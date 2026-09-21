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

## Quick Start (Local)

### 1. Set Up Virtual Environment

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# macOS / Linux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Tests

```bash
pytest -v
```

### 3. Launch Application

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## Deployment Guide (GitHub to Streamlit Community Cloud)

Streamlit Community Cloud provides 100% free hosting directly integrated with your GitHub repository.

### Step 1: Create a GitHub Repository
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `automotive-data-platform`).
3. Keep it **Public** (required for free Streamlit Cloud deployment).
4. Do not initialize with README or .gitignore (they are already created).
5. Click **Create repository**.

### Step 2: Push Local Code to GitHub
Open your terminal in the `automotive-data-platform` directory:

```powershell
# Initialize git and stage files
git add .

# Create initial commit
git commit -m "Production release: Automotive Data Curation & Analytics Platform"

# Rename branch to main
git branch -M main

# Link to your GitHub repo (replace with your actual GitHub URL)
git remote add origin https://github.com/<your-username>/automotive-data-platform.git

# Push to GitHub
git push -u origin main
```

### Step 3: Deploy on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **New app**.
3. Select your repository: `<your-username>/automotive-data-platform`.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Click **Deploy!**.

Within 1-2 minutes, your live web application URL will be active (e.g., `https://<your-app-name>.streamlit.app`).

---

## Optional: Google Firebase Integration

The platform includes an optional Firebase Firestore adapter in `src/automotive/database.py`. It operates using local SQLite by default, and automatically activates Firebase if credentials are provided.

To enable Firebase on Streamlit Community Cloud:
1. In your Google Firebase Console, create a project and enable **Cloud Firestore**.
2. Go to **Project Settings > Service accounts** and click **Generate new private key**.
3. In Streamlit Cloud dashboard, go to **App settings > Secrets** and paste your configuration:
```toml
FIREBASE_CONFIG = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
"""
```

---

## License

MIT License.
