"""
FRED / ALFRED Models for Finexus Research Module

Models for accessing FRED economic data from the DATA database.
Includes metadata, observations, releases, and calendar data.

Note: This is a subset of the full DATA project models, focused on
what's needed for the Research module features.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Float, Boolean, Text,
    ForeignKey, Index, UniqueConstraint
)

from ..database import DataBase as Base


# ----------------------------
# FRED Metadata
# ----------------------------

class FredSource(Base):
    """FRED data source (e.g., Bureau of Labor Statistics)"""
    __tablename__ = "fred_source"

    source_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    link = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)


class FredRelease(Base):
    """FRED release (e.g., Employment Situation, GDP)"""
    __tablename__ = "fred_release"

    release_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    link = Column(String(512), nullable=True)
    press_release = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    series_count = Column(Integer, nullable=True, default=0)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)


class FredReleaseDate(Base):
    """Calendar backbone: date-level release schedule"""
    __tablename__ = "fred_release_date"

    release_id = Column(Integer, ForeignKey("fred_release.release_id"), primary_key=True)
    release_date = Column(Date, primary_key=True)

    __table_args__ = (
        Index("ix_fred_release_date_date", "release_date"),
    )


class FredCategory(Base):
    """FRED category for organizing series"""
    __tablename__ = "fred_category"

    category_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, nullable=True, index=True)
    notes = Column(Text, nullable=True)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)


class FredSeries(Base):
    """FRED series metadata"""
    __tablename__ = "fred_series"

    series_id = Column(String(64), primary_key=True)

    title = Column(String(512), nullable=True, index=True)
    units = Column(String(255), nullable=True)
    units_short = Column(String(64), nullable=True)
    frequency = Column(String(64), nullable=True)
    frequency_short = Column(String(32), nullable=True)
    seasonal_adjustment = Column(String(64), nullable=True)
    seasonal_adjustment_short = Column(String(32), nullable=True)

    observation_start = Column(Date, nullable=True)
    observation_end = Column(Date, nullable=True)
    last_updated = Column(DateTime, nullable=True, index=True)

    notes = Column(Text, nullable=True)
    popularity = Column(Integer, nullable=True)

    source_id = Column(Integer, ForeignKey("fred_source.source_id"), nullable=True, index=True)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)


# ----------------------------
# Series Mapping Tables
# ----------------------------

class FredSeriesRelease(Base):
    """Mapping between series and releases"""
    __tablename__ = "fred_series_release"

    series_id = Column(String(64), ForeignKey("fred_series.series_id"), primary_key=True)
    release_id = Column(Integer, ForeignKey("fred_release.release_id"), primary_key=True)

    __table_args__ = (Index("ix_fred_series_release_release", "release_id"),)


class FredSeriesCategory(Base):
    """Mapping between series and categories"""
    __tablename__ = "fred_series_category"

    series_id = Column(String(64), ForeignKey("fred_series.series_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("fred_category.category_id"), primary_key=True)

    __table_args__ = (Index("ix_fred_series_category_category", "category_id"),)


class FredObservationLatest(Base):
    """Latest FRED observation values"""
    __tablename__ = "fred_observation_latest"

    series_id = Column(String(64), ForeignKey("fred_series.series_id"), primary_key=True)
    date = Column(Date, primary_key=True)

    value = Column(Float, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_fred_latest_series_date", "series_id", "date"),
        Index("ix_fred_latest_date", "date"),
    )


class FredObservationRealtime(Base):
    """
    ALFRED revision-aware observation:
    - date: observation period
    - realtime_start/realtime_end: interval where this value was current in ALFRED
    """
    __tablename__ = "fred_observation_realtime"

    series_id = Column(String(64), ForeignKey("fred_series.series_id"), primary_key=True)
    date = Column(Date, primary_key=True)
    realtime_start = Column(Date, primary_key=True)
    realtime_end = Column(Date, primary_key=True)

    value = Column(Float, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_fred_rt_series_date", "series_id", "date"),
        Index("ix_fred_rt_start_end", "realtime_start", "realtime_end"),
        Index("ix_fred_rt_series_start_end", "series_id", "realtime_start", "realtime_end"),
    )
