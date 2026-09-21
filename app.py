"""
Automotive Data Analytics Platform — Main Streamlit Application
===============================================================
Run with:
    streamlit run app.py

Pages:
    1. Dashboard        — KPI cards + 6 overview charts
    2. Data Explorer    — Browse, search, filter, download data
    3. Data Quality     — Validation and cleaning statistics
    4. Sales Analytics  — Manufacturer/model/year sales analysis
    5. Vehicle Analytics — Price/mileage/age/engine distributions
    6. Service Analytics — Service cost breakdowns
    7. Report Generator — Generate and download full reports
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — ensure src/ is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Configure logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Streamlit page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Automotive Analytics Platform",
    page_icon=":material/directions_car:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Imports (after path setup)
# ---------------------------------------------------------------------------
from src.automotive.loader import load_dataset, load_uploaded_file
from src.automotive.validator import validate_dataset, ValidationResult
from src.automotive.cleaner import clean_dataset, CleaningResult
from src.automotive.transformer import transform_dataset
from src.automotive.analytics import run_all_analytics
from src.automotive.reporting import generate_report
from dashboard.components import (
    build_sidebar_filters, apply_filters, section_header,
    kpi_row, download_csv_button, download_excel_button, download_text_button,
    active_dataset_banner, show_loading_overlay, hide_loading_overlay, icon, icon_label,
)
from dashboard import charts as ch

# ---------------------------------------------------------------------------
# CSS — dark premium aesthetic, icon-button polish
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
.stSidebar { background: #0c0c1a !important; }
.stSidebar [data-testid="stSidebarContent"] { padding-top: 1rem; }

/* ── Nav radio — pill style ── */
.stRadio > div { gap: 4px; }
.stRadio label {
    border-radius: 8px;
    padding: 8px 12px !important;
    transition: background 0.15s ease;
}
.stRadio label:hover { background: rgba(126,179,255,0.08); }
[data-baseweb="radio"] input:checked ~ div { color: #7EB3FF !important; }

/* ── Native st.metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    border: 1px solid #3f3f5f;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #7EB3FF !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    color: #9090b0 !important;
}

/* ── Headings ── */
h1 { color: #7EB3FF; }
h2 { color: #a0c4ff; }
h3 { color: #c0d8ff; }

/* ── Primary buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #3a3af0, #7c3aed);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    padding: 0.45rem 1.1rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #5a5af0, #9c5aed);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(124,58,237,0.35);
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #0f766e, #059669);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    transition: transform 0.15s ease;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #14b8a6, #10b981);
    transform: translateY(-1px);
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    border: 1px solid #3f3f5f;
    border-radius: 8px;
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-weight: 500;
    color: #7878a0;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #7EB3FF;
    border-bottom-color: #7EB3FF !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #2a2a40;
}

/* ── Spinner override (show on pipeline stages) ── */
[data-testid="stSpinner"] > div {
    border-top-color: #7EB3FF !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data pipeline (cached at session level)
# ---------------------------------------------------------------------------

SAMPLE_PATH   = PROJECT_ROOT / "data" / "sample" / "automotive_raw.csv"
CLEANED_PATH  = PROJECT_ROOT / "data" / "processed" / "automotive_cleaned.csv"


@st.cache_data(show_spinner="Loading dataset…")
def load_raw_data(path: str) -> pd.DataFrame:
    return load_dataset(path)


@st.cache_data(show_spinner="Validating dataset…")
def run_validation(df: pd.DataFrame) -> ValidationResult:
    return validate_dataset(df)


@st.cache_data(show_spinner="Cleaning dataset…")
def run_cleaning(df: pd.DataFrame, output_path: str) -> CleaningResult:
    return clean_dataset(df, output_path=output_path)


@st.cache_data(show_spinner="Running transformations…")
def run_transformation(df: pd.DataFrame) -> pd.DataFrame:
    return transform_dataset(df)


@st.cache_data(show_spinner="Computing analytics…")
def run_analytics(df: pd.DataFrame) -> dict:
    return run_all_analytics(df)


def ensure_sample_data() -> bool:
    """Generate sample data if it doesn't exist. Returns True if available."""
    if SAMPLE_PATH.exists():
        return True
    st.warning("Sample dataset not found. Generating default sample...")
    st.code("python scripts/generate_sample_data.py", language="bash")
    with st.status("Generating sample automotive dataset…", expanded=True) as status:
        try:
            st.write("Initializing schema and generating 5,000 vehicle records…")
            from scripts.generate_sample_data import generate_dataset
            df = generate_dataset(5000)
            SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(SAMPLE_PATH, index=False)
            status.update(label="Sample dataset generated successfully.", state="complete", expanded=False)
            st.success("Sample dataset generated successfully.")
            return True
        except Exception as exc:
            status.update(label="Generation failed", state="error", expanded=True)
            st.error(f"Failed to auto-generate dataset: {exc}")
            return False


# ---------------------------------------------------------------------------
# Session state initialisation  — with loading overlay
# ---------------------------------------------------------------------------

def initialise_pipeline() -> bool:
    """Run full pipeline and store results in session state."""
    if "pipeline_done" in st.session_state:
        return True

    if not ensure_sample_data():
        return False

    loader_ph = st.empty()
    show_loading_overlay(
        message="Initialising Analytics Pipeline",
        sub="Loading · Validating · Cleaning · Transforming · Computing…",
        placeholder=loader_ph,
    )

    try:
        raw_df = load_raw_data(str(SAMPLE_PATH))
        st.session_state["raw_df"] = raw_df

        validation = run_validation(raw_df)
        st.session_state["validation"] = validation

        cleaning = run_cleaning(raw_df, str(CLEANED_PATH))
        st.session_state["cleaning"] = cleaning
        st.session_state["cleaned_df"] = cleaning.cleaned_df

        transformed = run_transformation(cleaning.cleaned_df)
        st.session_state["transformed_df"] = transformed

        analytics = run_analytics(transformed)
        st.session_state["analytics"] = analytics

        st.session_state["pipeline_done"] = True
        st.session_state["dataset_name"] = "Sample Fleet Dataset"
        st.session_state["active_filename"] = "Sample Fleet Dataset"

        hide_loading_overlay(placeholder=loader_ph)
        st.rerun()
        return True

    except Exception as exc:
        hide_loading_overlay(placeholder=loader_ph)
        st.error(f"Pipeline error: {exc}")
        log.exception("Pipeline failed")
        return False


# ---------------------------------------------------------------------------
# Data Source Picker & Custom File Uploader
# ---------------------------------------------------------------------------

def render_dataset_source_selector() -> None:
    """Render dataset source picker (sample vs custom upload) in sidebar."""
    with st.sidebar:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0 2px;">'
            f'{icon("database", "#7EB3FF", 16)}'
            f'<span style="font-weight:600;font-size:0.9rem;color:#7EB3FF;">Data Source</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        source_mode = st.radio(
            "Select Data Source",
            ["Sample Fleet Dataset", "Upload Custom Dataset"],
            key="selected_source_mode",
            label_visibility="collapsed",
            format_func=lambda x: f":material/database:  {x}" if "Sample" in x else f":material/upload_file:  {x}",
        )

        if source_mode == "Upload Custom Dataset":
            uploaded_file = st.file_uploader(
                "Upload uncleaned CSV/Excel",
                type=["csv", "tsv", "xlsx", "xls"],
                key="custom_file_uploader",
                help="Upload any raw automotive dataset to validate, clean, transform, and analyze dynamically.",
            )
            if uploaded_file is not None:
                if st.session_state.get("active_filename") != uploaded_file.name:
                    loader_ph = st.empty()
                    show_loading_overlay(
                        message="Curating Uploaded Dataset",
                        sub=f"Analyzing {uploaded_file.name} · Cleansing anomalies · Engineering features…",
                        placeholder=loader_ph,
                    )
                    try:
                        raw_df = load_uploaded_file(uploaded_file)
                        validation = run_validation(raw_df)
                        cleaning = run_cleaning(
                            raw_df,
                            str(PROJECT_ROOT / "data" / "processed" / f"custom_cleaned_{uploaded_file.name}.csv"),
                        )
                        transformed = run_transformation(cleaning.cleaned_df)
                        analytics = run_analytics(transformed)

                        st.session_state["raw_df"] = raw_df
                        st.session_state["validation"] = validation
                        st.session_state["cleaning"] = cleaning
                        st.session_state["cleaned_df"] = cleaning.cleaned_df
                        st.session_state["transformed_df"] = transformed
                        st.session_state["analytics"] = analytics
                        st.session_state["dataset_name"] = uploaded_file.name
                        st.session_state["active_filename"] = uploaded_file.name
                        st.session_state["pipeline_done"] = True

                        hide_loading_overlay(placeholder=loader_ph)
                        st.rerun()
                    except Exception as exc:
                        hide_loading_overlay(placeholder=loader_ph)
                        st.error(f"Error curating dataset '{uploaded_file.name}': {exc}")
                        log.exception("Custom curation failed")
        else:
            if st.session_state.get("active_filename") != "Sample Fleet Dataset":
                for k in ["raw_df", "validation", "cleaning", "cleaned_df", "transformed_df", "analytics", "pipeline_done", "dataset_name", "active_filename"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        st.divider()


# ---------------------------------------------------------------------------
# Navigation — icon-based sidebar, no emojis
# ---------------------------------------------------------------------------

_NAV_ITEMS: list[dict] = [
    {"label": "Dashboard",        "icon": "layout-dashboard", "mat": ":material/dashboard:"},
    {"label": "Data Explorer",    "icon": "table",            "mat": ":material/table_chart:"},
    {"label": "Data Quality",     "icon": "shield-check",     "mat": ":material/verified_user:"},
    {"label": "Sales Analytics",  "icon": "trending-up",      "mat": ":material/trending_up:"},
    {"label": "Vehicle Analytics","icon": "car",              "mat": ":material/directions_car:"},
    {"label": "Service Analytics","icon": "wrench",           "mat": ":material/build:"},
    {"label": "Report Generator", "icon": "file-text",        "mat": ":material/description:"},
]

PAGES = [item["label"] for item in _NAV_ITEMS]

_NAV_CSS = """
<style>
.stRadio label {
    border-radius: 8px;
    padding: 8px 12px !important;
    transition: background 0.15s ease;
}
.stRadio label:hover { background: rgba(126,179,255,0.08); }
</style>
"""

_SIDEBAR_HEADER_CSS = """
<style>
.ag-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 4px 12px;
    border-bottom: 1px solid #2a2a40;
    margin-bottom: 10px;
}
.ag-brand-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #3a3af0, #7c3aed);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
}
.ag-brand-name {
    font-size: 1rem;
    font-weight: 700;
    color: #c0d8ff;
    line-height: 1.1;
}
.ag-brand-version {
    font-size: 0.7rem;
    color: #4a4a70;
    margin-top: 1px;
}
</style>
"""


def sidebar_navigation() -> str:
    """Render icon-based sidebar navigation, return selected page label."""
    with st.sidebar:
        # Brand header
        st.markdown(_SIDEBAR_HEADER_CSS, unsafe_allow_html=True)
        car_svg = icon("car", "#c0d8ff", 22)
        brand_html = (
            f'<div class="ag-sidebar-brand">'
            f'<div class="ag-brand-icon">{car_svg}</div>'
            f'<div>'
            f'<div class="ag-brand-name">Auto Analytics</div>'
            f'<div class="ag-brand-version">v1.0  ·  Synthetic Dataset</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(brand_html, unsafe_allow_html=True)

        st.markdown(_NAV_CSS, unsafe_allow_html=True)

        def _format_nav(lbl: str) -> str:
            item = next((x for x in _NAV_ITEMS if x["label"] == lbl), None)
            if item:
                return f"{item['mat']}  {item['label']}"
            return lbl

        page = st.radio(
            "Navigation",
            PAGES,
            label_visibility="collapsed",
            format_func=_format_nav,
        )

        st.divider()

        # Active page info
        active_item = next((x for x in _NAV_ITEMS if x["label"] == page), _NAV_ITEMS[0])
        svg = icon(active_item["icon"], "#7EB3FF", 14)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;color:#5a5a80;font-size:0.78rem;">'
            f'{svg}<span>{page}</span></div>',
            unsafe_allow_html=True,
        )

    return page


# ---------------------------------------------------------------------------
# Page 1 — Dashboard
# ---------------------------------------------------------------------------

def page_dashboard(df: pd.DataFrame, filters: dict, analytics: dict) -> None:
    section_header("Dashboard", "Fleet-wide KPI overview and interactive charts", "layout-dashboard")

    kpis = analytics["overall"]
    kpi_row([
        {"icon": "car",     "label": "Total Vehicles",   "value": f"{kpis['total_vehicles']:,}"},
        {"icon": "package", "label": "Total Units Sold", "value": f"{kpis['total_units_sold']:,}"},
        {"icon": "dollar",  "label": "Total Revenue",    "value": f"${kpis['total_sales_value']/1e9:.2f}B"},
    ], cols=3)

    kpi_row([
        {"icon": "tag",    "label": "Avg Vehicle Price", "value": f"${kpis['avg_price']:,.0f}"},
        {"icon": "fuel",   "label": "Avg Mileage",       "value": f"{kpis['avg_mileage']:.1f} km/L"},
        {"icon": "wrench", "label": "Avg Service Cost",  "value": f"${kpis['avg_service_cost']:,.0f}"},
    ], cols=3)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ch.cached_sales_by_manufacturer(df), use_container_width=True)
    with col2:
        st.plotly_chart(ch.cached_sales_by_year(df), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(ch.cached_fuel_distribution(df), use_container_width=True)
    with col4:
        st.plotly_chart(ch.cached_vehicle_type_distribution(df), use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(ch.cached_avg_price_by_manufacturer(df), use_container_width=True)
    with col6:
        st.plotly_chart(ch.cached_price_vs_mileage(df), use_container_width=True)

    st.info(f"Showing **{len(df):,}** records. Use the sidebar filters to drill down.")


# ---------------------------------------------------------------------------
# Page 2 — Data Explorer
# ---------------------------------------------------------------------------

def page_data_explorer(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame, filters: dict) -> None:
    section_header("Data Explorer", "Browse, search, filter, and download the dataset", "table")

    tab_raw, tab_clean, tab_stats = st.tabs(["Raw Data", "Cleaned Data", "Statistics"])

    def _render_table(df: pd.DataFrame, key_prefix: str) -> None:
        search = st.text_input(
            "Search records", key=f"{key_prefix}_search",
            placeholder="Type to filter any column…",
        )
        if search:
            mask = df.astype(str).apply(
                lambda s: s.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df = df[mask]

        cols = st.multiselect(
            "Select columns to display",
            df.columns.tolist(),
            default=df.columns.tolist(),
            key=f"{key_prefix}_cols",
        )
        if cols:
            df = df[cols]

        st.dataframe(df, use_container_width=True, height=480)
        st.caption(f"{len(df):,} rows × {len(df.columns)} columns")
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            download_csv_button(df, f"automotive_{key_prefix}.csv", f"Export {key_prefix.title()} (CSV)")
        with btn_c2:
            download_excel_button(df, f"automotive_{key_prefix}.xlsx", f"Export {key_prefix.title()} (Excel)")

    with tab_raw:
        _render_table(raw_df, "raw")

    with tab_clean:
        _render_table(cleaned_df, "cleaned")

    with tab_stats:
        st.subheader("Descriptive Statistics")
        num_cols = cleaned_df.select_dtypes(include="number")
        st.dataframe(num_cols.describe().round(3), use_container_width=True)

        st.subheader("Categorical Columns")
        for col in cleaned_df.select_dtypes(include=["object", "str"]).columns:
            with st.expander(col):
                vc = cleaned_df[col].value_counts().reset_index()
                vc.columns = [col, "Count"]
                st.dataframe(vc, use_container_width=True)


# ---------------------------------------------------------------------------
# Page 3 — Data Quality
# ---------------------------------------------------------------------------

def page_data_quality(validation: ValidationResult, cleaning: CleaningResult) -> None:
    section_header("Data Quality", "Validation findings, cleaning statistics, and quality report", "shield-check")

    tab_val, tab_clean, tab_report = st.tabs(["Validation", "Cleaning", "Column Report"])

    with tab_val:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows",      f"{validation.total_rows:,}")
        col2.metric("Duplicates",      f"{validation.duplicate_count:,}")
        col3.metric("Missing Cells",   f"{validation.total_missing:,}")
        col4.metric("Invalid Records", f"{validation.total_invalid:,}")

        st.divider()
        st.subheader("Validation Breakdown")
        breakdown = {
            "Invalid Years":          validation.invalid_years,
            "Invalid Prices":         validation.invalid_prices,
            "Invalid Mileage":        validation.invalid_mileage,
            "Invalid Sales":          validation.invalid_sales,
            "Invalid Engine CC":      validation.invalid_engine,
            "Invalid Fuel Types":     validation.invalid_fuel,
            "Invalid Transmissions":  validation.invalid_trans,
        }
        bdf = pd.DataFrame(list(breakdown.items()), columns=["Issue", "Count"])
        st.dataframe(bdf, use_container_width=True)

        import plotly.express as px
        bdf_plot = bdf[bdf["Count"] > 0]
        if not bdf_plot.empty:
            fig = px.bar(
                bdf_plot, x="Count", y="Issue", orientation="h",
                color="Count", color_continuous_scale="Reds",
                template="plotly_dark",
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    with tab_clean:
        s = cleaning.summary()
        col1, col2, col3 = st.columns(3)
        col1.metric("Original Records",   f"{s['original_records']:,}")
        col2.metric("Duplicates Removed", f"{s['duplicates_removed']:,}")
        col3.metric("Final Records",      f"{s['final_records']:,}")

        col4, col5 = st.columns(2)
        col4.metric("Missing Values Filled",    f"{s['missing_filled']:,}")
        col5.metric("Invalid Values Corrected", f"{s['invalid_corrected']:,}")

        st.divider()
        with st.expander("Cleaning Change Log"):
            for entry in cleaning.changes_log:
                st.markdown(f"- {entry}")

    with tab_report:
        col_report = validation.column_report_df()
        st.dataframe(col_report, use_container_width=True)
        download_csv_button(col_report, "data_quality_report.csv", "Download Quality Report")


# ---------------------------------------------------------------------------
# Page 4 — Sales Analytics
# ---------------------------------------------------------------------------

def page_sales_analytics(df: pd.DataFrame, analytics: dict) -> None:
    section_header("Sales Analytics", "Manufacturer, model, year and fuel-type sales analysis", "trending-up")

    mfr  = analytics["manufacturer"]
    fuel = analytics["fuel"]
    time = analytics["time"]

    tab_mfr, tab_model, tab_year, tab_fuel = st.tabs([
        "By Manufacturer", "By Model", "By Year", "By Fuel Type"
    ])

    with tab_mfr:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Units Sold")
            st.dataframe(mfr["sales_by_manufacturer"], use_container_width=True)
            download_csv_button(mfr["sales_by_manufacturer"], "sales_by_mfr.csv")
        with col2:
            st.subheader("Revenue")
            revenue_df = mfr["revenue_by_manufacturer"].copy()
            revenue_df["total_revenue"] = revenue_df["total_revenue"].map("${:,.2f}".format)
            st.dataframe(revenue_df, use_container_width=True)

        st.plotly_chart(ch.cached_revenue_by_manufacturer(df), use_container_width=True)
        st.plotly_chart(ch.cached_sales_by_manufacturer(df), use_container_width=True)

    with tab_model:
        vehicle_ana = analytics["vehicle"]
        st.subheader("Top 30 Models by Units Sold")
        st.dataframe(vehicle_ana["sales_by_model"], use_container_width=True)
        download_csv_button(vehicle_ana["sales_by_model"], "sales_by_model.csv")

        import plotly.express as px
        top20 = vehicle_ana["sales_by_model"].head(20)
        fig = px.bar(
            top20, x="total_units_sold", y="model",
            orientation="h", color="total_units_sold",
            color_continuous_scale="Blues", template="plotly_dark",
            labels={"model": "Model", "total_units_sold": "Units Sold"},
        )
        fig.update_layout(height=600, title="Top 20 Models by Units Sold")
        st.plotly_chart(fig, use_container_width=True)

    with tab_year:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_sales_by_year(df), use_container_width=True)
        with col2:
            st.plotly_chart(ch.cached_sales_trend(df), use_container_width=True)

        st.subheader("Year-wise Sales Table")
        yr_df = time["sales_by_year"].copy()
        st.dataframe(yr_df, use_container_width=True)
        download_csv_button(yr_df, "sales_by_year.csv")

    with tab_fuel:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_fuel_distribution(df), use_container_width=True)
        with col2:
            st.dataframe(fuel["sales_by_fuel"], use_container_width=True)
            download_csv_button(fuel["sales_by_fuel"], "sales_by_fuel.csv")

        st.subheader("Average Price by Fuel Type")
        st.dataframe(fuel["avg_price_by_fuel"], use_container_width=True)


# ---------------------------------------------------------------------------
# Page 5 — Vehicle Analytics
# ---------------------------------------------------------------------------

def page_vehicle_analytics(df: pd.DataFrame, analytics: dict) -> None:
    section_header("Vehicle Analytics", "Price, mileage, age, engine and type distributions", "gauge")

    vehicle = analytics["vehicle"]
    rel     = analytics["relationships"]

    tab_price, tab_mileage, tab_age, tab_engine, tab_type, tab_corr = st.tabs([
        "Price", "Mileage", "Age", "Engine", "Type & Fuel", "Correlations"
    ])

    with tab_price:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_price_distribution(df), use_container_width=True)
        with col2:
            st.plotly_chart(ch.cached_avg_price_by_manufacturer(df), use_container_width=True)
        st.subheader("Price Statistics")
        st.dataframe(
            vehicle["price_stats"].to_frame("Price (USD)"),
            use_container_width=True,
        )

    with tab_mileage:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_mileage_distribution(df), use_container_width=True)
        with col2:
            st.plotly_chart(ch.cached_price_vs_mileage(df), use_container_width=True)
        st.subheader("Mileage Statistics")
        st.dataframe(
            vehicle["mileage_stats"].to_frame("Mileage (km/L)"),
            use_container_width=True,
        )

    with tab_age:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_vehicle_age_distribution(df), use_container_width=True)
        with col2:
            st.dataframe(vehicle["age_distribution"], use_container_width=True)

    with tab_engine:
        st.plotly_chart(ch.cached_engine_cc_distribution(df), use_container_width=True)
        import plotly.express as px
        if "engine_cc" in df.columns:
            box_fig = px.box(
                df[df["engine_cc"] > 0], x="vehicle_type", y="engine_cc",
                color="vehicle_type", color_discrete_sequence=px.colors.qualitative.Vivid,
                template="plotly_dark",
                labels={"vehicle_type": "Vehicle Type", "engine_cc": "Engine CC"},
            )
            box_fig.update_layout(
                title="Engine Size by Vehicle Type",
                showlegend=False, height=420,
            )
            st.plotly_chart(box_fig, use_container_width=True)

    with tab_type:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_vehicle_type_distribution(df), use_container_width=True)
        with col2:
            st.plotly_chart(ch.cached_fuel_distribution(df), use_container_width=True)
        st.dataframe(vehicle["vehicle_type_dist"], use_container_width=True)

    with tab_corr:
        st.subheader("Correlation Matrix")
        st.plotly_chart(ch.cached_correlation_heatmap(df), use_container_width=True)
        st.subheader("Correlation Values")
        st.dataframe(rel["correlation_matrix"], use_container_width=True)


# ---------------------------------------------------------------------------
# Page 6 — Service Analytics
# ---------------------------------------------------------------------------

def page_service_analytics(df: pd.DataFrame, analytics: dict) -> None:
    section_header("Service Analytics", "Annual service cost analysis and breakdowns", "wrench")

    service = analytics["service"]

    st.metric("Overall Avg Service Cost (USD)", f"${service['overall_avg_service_cost']:,.2f}")
    st.divider()

    tab_mfr, tab_type, tab_age, tab_cat = st.tabs([
        "By Manufacturer", "By Vehicle Type", "Age vs Cost", "Cost Categories"
    ])

    with tab_mfr:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_service_cost_by_manufacturer(df), use_container_width=True)
        with col2:
            st.dataframe(service["service_by_manufacturer"], use_container_width=True)
            download_csv_button(service["service_by_manufacturer"], "service_by_mfr.csv")

    with tab_type:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(ch.cached_service_cost_by_type(df), use_container_width=True)
        with col2:
            st.dataframe(service["service_by_vehicle_type"], use_container_width=True)

    with tab_age:
        st.plotly_chart(ch.cached_age_vs_service_cost(df), use_container_width=True)
        st.info("Trend line shows the positive correlation between vehicle age and service cost.")

    with tab_cat:
        cat_df = service["service_category_dist"]
        if not cat_df.empty:
            import plotly.express as px
            fig = px.pie(
                cat_df, names="service_cost_category", values="count",
                hole=0.4, color_discrete_sequence=px.colors.qualitative.Vivid,
                template="plotly_dark",
                title="Service Cost Category Distribution",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(cat_df, use_container_width=True)


# ---------------------------------------------------------------------------
# Page 7 — Report Generator
# ---------------------------------------------------------------------------

def page_report_generator(
    transformed_df: pd.DataFrame,
    validation: ValidationResult,
    cleaning: CleaningResult,
    analytics: dict,
) -> None:
    section_header("Report Generator", "Generate and download a comprehensive analytics report", "file-text")

    st.info(
        "Click **Generate Report** to compile a full report including dataset overview, "
        "data quality summary, cleaning statistics, KPIs, and analytics findings."
    )

    if st.button("Generate Report", icon=":material/play_arrow:", use_container_width=False):
        with st.status("Compiling Comprehensive Analytics Report…", expanded=True) as status:
            st.write("Aggregating fleet KPIs and baseline parameters…")
            time.sleep(0.25)
            st.write("Compiling data quality, validation, and cleansing audit…")
            time.sleep(0.25)
            content = generate_report(
                df=transformed_df,
                validation_result=validation,
                cleaning_result=cleaning,
                analytics=analytics,
            )
            st.write("Synthesizing strategic recommendations and export package…")
            time.sleep(0.2)
            st.session_state["report_content"] = content
            status.update(label="Analytics Report Ready for Download", state="complete", expanded=False)
        st.success("Report generated successfully.")

    if "report_content" in st.session_state:
        content = st.session_state["report_content"]
        st.subheader("Report Preview")
        st.code(content[:3000] + ("\n… (truncated for preview)" if len(content) > 3000 else ""))
        download_text_button(content, "automotive_analytics_report.txt")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main application entry point."""
    ok = initialise_pipeline()
    if not ok:
        st.stop()

    page = sidebar_navigation()
    render_dataset_source_selector()

    raw_df         = st.session_state["raw_df"]
    cleaned_df     = st.session_state["cleaned_df"]
    transformed_df = st.session_state["transformed_df"]
    analytics      = st.session_state["analytics"]
    validation     = st.session_state["validation"]
    cleaning       = st.session_state["cleaning"]
    dataset_name   = st.session_state.get("dataset_name", "Sample Fleet Dataset")

    # Render active dataset banner with quick CSV/Excel export buttons
    active_dataset_banner(
        source_name=dataset_name,
        raw_count=len(raw_df),
        cleaned_count=len(cleaned_df),
        cleaned_df=cleaned_df,
    )

    filters     = build_sidebar_filters(transformed_df)
    filtered_df = apply_filters(transformed_df, filters)

    if len(filtered_df) == 0:
        st.warning("No records match the current filters. Try adjusting your selection.")
        st.stop()

    has_filters = any([
        filters["manufacturers"], filters["models"], filters["fuel_types"],
        filters["vehicle_types"], filters["transmissions"],
    ])
    yr_range = filters["year_range"]
    yr_full  = (
        int(transformed_df["vehicle_year"].min()),
        int(transformed_df["vehicle_year"].max()),
    )
    has_year_filter = yr_range != yr_full

    if has_filters or has_year_filter:
        analytics_view = run_all_analytics(filtered_df)
    else:
        analytics_view = analytics

    # Route to page
    if page == PAGES[0]:
        page_dashboard(filtered_df, filters, analytics_view)
    elif page == PAGES[1]:
        page_data_explorer(raw_df, cleaned_df, filters)
    elif page == PAGES[2]:
        page_data_quality(validation, cleaning)
    elif page == PAGES[3]:
        page_sales_analytics(filtered_df, analytics_view)
    elif page == PAGES[4]:
        page_vehicle_analytics(filtered_df, analytics_view)
    elif page == PAGES[5]:
        page_service_analytics(filtered_df, analytics_view)
    elif page == PAGES[6]:
        page_report_generator(transformed_df, validation, cleaning, analytics)


if __name__ == "__main__":
    main()
