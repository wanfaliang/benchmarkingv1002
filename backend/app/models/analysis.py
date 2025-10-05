"""Analysis database model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Analysis(Base):
    __tablename__ = "analyses"
    
    analysis_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=True)
    companies = Column(JSON, nullable=False)  # List of tickers
    years_back = Column(Integer, default=10)
    status = Column(String, default="created")  # created, collection, analysis, complete, failed
    phase = Column(String, nullable=True)  # A, B
    progress = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_log = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    sections = relationship("Section", back_populates="analysis", cascade="all, delete-orphan")