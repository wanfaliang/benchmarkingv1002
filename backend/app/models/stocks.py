"""Stock Screener database models - saved screens and templates"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class SavedScreen(Base):
    """User-saved stock screens"""
    __tablename__ = "saved_screens"

    screen_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    # Screen metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Screen configuration (JSON)
    # Structure: {
    #   "universe": {"min_market_cap": 1000000000, "sectors": [...], ...},
    #   "filters": [{"feature": "pe_ratio_ttm", "operator": "<", "value": 20}, ...],
    #   "columns": ["symbol", "company_name", "pe_ratio_ttm", ...],
    #   "sort_by": "market_cap",
    #   "sort_order": "desc"
    # }
    filters = Column(JSON, nullable=False, default=list)
    universe = Column(JSON, nullable=True)  # Universe constraints
    columns = Column(JSON, nullable=True)  # Selected display columns
    sort_by = Column(String(100), nullable=True)
    sort_order = Column(String(10), default="desc")  # "asc" or "desc"

    # Template flag - if True, this is a system template (not user-owned)
    is_template = Column(Boolean, default=False)
    template_key = Column(String(50), nullable=True, unique=True)  # e.g., "deep_value", "garp"

    # Usage tracking
    last_run_at = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    last_result_count = Column(Integer, nullable=True)  # How many stocks matched last time

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_screens")


class ScreenRun(Base):
    """History of screen executions"""
    __tablename__ = "screen_runs"

    run_id = Column(String, primary_key=True, default=generate_uuid)
    screen_id = Column(String, ForeignKey("saved_screens.screen_id"), nullable=True)  # Null for ad-hoc screens
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    # Snapshot of filters used (in case screen was modified)
    filters_snapshot = Column(JSON, nullable=False)
    universe_snapshot = Column(JSON, nullable=True)

    # Results
    result_count = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)

    # Timestamp
    run_at = Column(DateTime, default=datetime.utcnow)
