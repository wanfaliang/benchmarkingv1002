"""
FRED / ALFRED Models for Finexus Research Module

Models for accessing FRED economic data from the DATA database.
Used primarily for Treasury yield curve data.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Float, Text,
    ForeignKey, Index, UniqueConstraint
)

from ..database import DataBase as Base


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

    source_id = Column(Integer, nullable=True, index=True)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)


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
