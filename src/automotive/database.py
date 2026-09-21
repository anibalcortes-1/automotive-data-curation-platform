"""
Database Module — SQLite + SQLAlchemy
=====================================
Manages persistent storage for the Automotive Data Platform.

Tables:
    vehicles        — cleaned vehicle records
    data_quality    — quality-report snapshots
    analytics_runs  — analytics metadata
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text,
    create_engine, inspect, text,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ORM Base & Models
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class VehicleRecord(Base):
    """Cleaned vehicle record."""

    __tablename__ = "vehicles"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id           = Column(String(20), unique=True, nullable=False, index=True)
    manufacturer         = Column(String(100))
    model                = Column(String(100))
    vehicle_year         = Column(Integer)
    vehicle_type         = Column(String(50))
    fuel_type            = Column(String(50))
    transmission         = Column(String(50))
    engine_cc            = Column(Integer)
    mileage_kmpl         = Column(Float)
    vehicle_price        = Column(Float)
    units_sold           = Column(Integer)
    service_cost         = Column(Float)
    manufacturing_region = Column(String(100))
    vehicle_age          = Column(Integer)
    total_sales_value    = Column(Float)
    service_cost_category = Column(String(50))
    mileage_category     = Column(String(50))
    price_category       = Column(String(50))
    created_at           = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DataQualityRun(Base):
    """Snapshot of a data-quality report."""

    __tablename__ = "data_quality"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    run_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_rows = Column(Integer)
    missing    = Column(Integer)
    duplicates = Column(Integer)
    invalid    = Column(Integer)
    report_json = Column(Text)


class AnalyticsRun(Base):
    """Record of an analytics execution."""

    __tablename__ = "analytics_runs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    run_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dataset     = Column(String(200))
    n_records   = Column(Integer)
    summary_json = Column(Text)


# ---------------------------------------------------------------------------
# Database manager
# ---------------------------------------------------------------------------

class DatabaseManager:
    """Manages SQLite database lifecycle for the platform."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            project_root = Path(__file__).resolve().parents[3]
            db_path = project_root / "automotive_platform.db"
        self.db_path = Path(db_path)
        self._engine = None
        self._Session = None

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def engine(self):
        """Return (and lazily create) the SQLAlchemy engine."""
        if self._engine is None:
            url = f"sqlite:///{self.db_path}"
            self._engine = create_engine(url, echo=False, future=True)
            Base.metadata.create_all(self._engine)
            log.info("Database connected: %s", self.db_path)
        return self._engine

    def session(self) -> Session:
        """Return a new session bound to this database."""
        if self._Session is None:
            self._Session = sessionmaker(bind=self.engine())
        return self._Session()

    def ensure_tables(self) -> None:
        """Create all tables if they do not exist."""
        Base.metadata.create_all(self.engine())

    def table_exists(self, table_name: str) -> bool:
        """Check whether a table exists."""
        inspector = inspect(self.engine())
        return table_name in inspector.get_table_names()

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def upsert_vehicles(self, df: pd.DataFrame) -> int:
        """Upsert vehicle records from a DataFrame. Returns rows inserted."""
        with self.session() as sess:
            count = 0
            for _, row in df.iterrows():
                existing = sess.query(VehicleRecord).filter_by(
                    vehicle_id=row.get("vehicle_id")
                ).first()
                if existing:
                    for col, val in row.items():
                        if hasattr(existing, col):
                            setattr(existing, col, val)
                else:
                    record_data = {
                        k: v for k, v in row.items()
                        if hasattr(VehicleRecord, k)
                    }
                    sess.add(VehicleRecord(**record_data))
                    count += 1
            sess.commit()
            log.info("Upserted %d vehicle records.", count)
            return count

    def save_quality_run(
        self,
        total_rows: int,
        missing: int,
        duplicates: int,
        invalid: int,
        report: dict[str, Any],
    ) -> None:
        """Save a data-quality run snapshot."""
        with self.session() as sess:
            sess.add(DataQualityRun(
                total_rows=total_rows,
                missing=missing,
                duplicates=duplicates,
                invalid=invalid,
                report_json=json.dumps(report, default=str),
            ))
            sess.commit()

    def save_analytics_run(self, dataset: str, n_records: int, summary: dict[str, Any]) -> None:
        """Save an analytics run record."""
        with self.session() as sess:
            sess.add(AnalyticsRun(
                dataset=dataset,
                n_records=n_records,
                summary_json=json.dumps(summary, default=str),
            ))
            sess.commit()

    def load_vehicles(self) -> pd.DataFrame:
        """Load all vehicle records into a DataFrame."""
        with self.engine().connect() as conn:
            if not self.table_exists("vehicles"):
                return pd.DataFrame()
            result = conn.execute(text("SELECT * FROM vehicles"))
            rows = result.fetchall()
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame(rows, columns=result.keys())

    def row_count(self, table: str) -> int:
        """Return the row count for a table."""
        if not self.table_exists(table):
            return 0
        with self.engine().connect() as conn:
            return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
