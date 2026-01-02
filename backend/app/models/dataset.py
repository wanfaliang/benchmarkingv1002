"""
Dataset Module - Database Schema & SQLAlchemy Models
File: backend/app/models/dataset.py
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
import uuid


# ============================================================================
# ASSOCIATION TABLES (Many-to-Many relationships)
# ============================================================================

# Dataset sharing - which users have access to which datasets
dataset_shares = Table(
    'dataset_shares',
    Base.metadata,
    Column('dataset_id', String, ForeignKey('datasets.dataset_id', ondelete='CASCADE')),
    Column('shared_with_user_id', String, ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('permission', String, default='view'),  # view, edit, admin
    Column('shared_at', DateTime, default=datetime.utcnow),
    Column('shared_by_user_id', String, ForeignKey('users.user_id'))
)


# ============================================================================
# MAIN DATASET TABLE
# ============================================================================

class Dataset(Base):
    """
    Dataset represents a collection of financial data that can be explored flexibly.
    Unlike Analysis (which generates fixed reports), Dataset focuses on data access.
    """
    __tablename__ = "datasets"
    
    # Identity
    dataset_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    # Configuration
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    companies = Column(JSON, nullable=False)  # [{"ticker": "AAPL", "name": "Apple Inc"}, ...]
    years_back = Column(Integer, default=10)
    
    # Collection settings
    include_analyst = Column(Boolean, default=True)
    include_institutional = Column(Boolean, default=True)
    
    # Status tracking
    status = Column(String, default="created")  # created, collecting, ready, failed
    progress = Column(Integer, default=0)  # 0-100
    error_log = Column(Text, nullable=True)
    
    # Metadata
    data_size_mb = Column(Integer, nullable=True)  # Size of pickled data
    row_count = Column(Integer, nullable=True)  # Total rows in financial data
    
    # Sharing & visibility
    visibility = Column(String, default="private")  # private, shared, public
    share_token = Column(String, nullable=True, unique=True)  # For public sharing links
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    collected_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="datasets", foreign_keys=[user_id])
    shared_with = relationship(
        "User",
        secondary=dataset_shares,
        backref="shared_datasets",
        foreign_keys=[dataset_shares.c.dataset_id, dataset_shares.c.shared_with_user_id]
    )
    dashboards = relationship("Dashboard", back_populates="dataset", cascade="all, delete-orphan")
    saved_queries = relationship("SavedQuery", back_populates="dataset", cascade="all, delete-orphan")


# ============================================================================
# DASHBOARD TABLE (User's custom views)
# ============================================================================

class Dashboard(Base):
    """
    Dashboard represents a saved layout of charts, tables, and filters.
    Users can create multiple dashboards from the same dataset.
    """
    __tablename__ = "dashboards"
    
    dashboard_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.dataset_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    # Dashboard configuration
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    layout = Column(JSON, nullable=False)  # React-grid-layout configuration
    
    # Layout stores:
    # {
    #   "components": [
    #     {
    #       "id": "chart-1",
    #       "type": "line_chart",
    #       "config": {
    #         "dataSource": "financial",
    #         "xAxis": "Year",
    #         "yAxis": "revenue",
    #         "companies": ["AAPL", "MSFT"]
    #       },
    #       "position": {"x": 0, "y": 0, "w": 6, "h": 4}
    #     },
    #     {
    #       "id": "table-1",
    #       "type": "data_table",
    #       "config": {...},
    #       "position": {"x": 6, "y": 0, "w": 6, "h": 4}
    #     }
    #   ]
    # }
    
    # Metadata
    is_default = Column(Boolean, default=False)  # Default dashboard for this dataset
    is_template = Column(Boolean, default=False)  # Can be cloned by other users
    view_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="dashboards")
    user = relationship("User", back_populates="dashboards")


# ============================================================================
# SAVED QUERY TABLE (Reusable filters/queries)
# ============================================================================

class SavedQuery(Base):
    """
    SavedQuery stores frequently used query configurations.
    Users can save complex filters and reuse them.
    """
    __tablename__ = "saved_queries"
    
    query_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.dataset_id', ondelete='CASCADE'), nullable=True)
    user_id = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    # Query configuration
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    data_source = Column(String, nullable=False)  # financial, prices_daily, etc.
    query_config = Column(JSON, nullable=False)  # Complete DataQuery object
    
    # Example query_config:
    # {
    #   "filters": [
    #     {"field": "revenue", "operator": "gt", "value": 1000000000},
    #     {"field": "returnOnEquity", "operator": "gte", "value": 0.15}
    #   ],
    #   "columns": ["Company", "Symbol", "revenue", "netIncome"],
    #   "sort_by": "revenue",
    #   "sort_order": "desc"
    # }
    
    # Metadata
    is_public = Column(Boolean, default=False)  # Can other users see this query?
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="saved_queries", foreign_keys=[dataset_id])
    user = relationship("User", back_populates="saved_queries")


# ============================================================================
# SHARE LOG TABLE (Audit trail for sharing)
# ============================================================================

class DatasetShareLog(Base):
    """
    Log of all sharing activities for audit and analytics
    """
    __tablename__ = "dataset_share_logs"
    
    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.dataset_id', ondelete='CASCADE'))
    
    # Who did what
    shared_by_user_id = Column(String, ForeignKey('users.user_id', ondelete='SET NULL'))
    shared_with_user_id = Column(String, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    action = Column(String, nullable=False)  # shared, unshared, permission_changed, accessed
    
    # Share details
    permission = Column(String, nullable=True)  # view, edit, admin
    share_method = Column(String, nullable=True)  # email, link, social_media
    platform = Column(String, nullable=True)  # twitter, linkedin, etc (for social sharing)
    
    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# EXPORT LOG TABLE (Track data exports)
# ============================================================================

class DatasetExportLog(Base):
    """
    Track when users export data (for compliance and usage analytics)
    """
    __tablename__ = "dataset_export_logs"
    
    export_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.dataset_id', ondelete='CASCADE'))
    user_id = Column(String, ForeignKey('users.user_id', ondelete='CASCADE'))
    
    # Export details
    data_source = Column(String, nullable=False)  # financial, prices_daily, etc.
    format = Column(String, nullable=False)  # csv, excel, json, parquet
    row_count = Column(Integer, nullable=True)
    file_size_mb = Column(Integer, nullable=True)
    
    # Query used
    query_config = Column(JSON, nullable=True)  # What filters were applied
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)