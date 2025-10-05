"""Section database model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Section(Base):
    __tablename__ = "sections"
    
    section_id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("analyses.analysis_id"), nullable=False)
    section_number = Column(Integer, nullable=False)
    section_name = Column(String, nullable=False)
    status = Column(String, default="queued")  # queued, processing, complete, failed, skipped
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    html_path = Column(String, nullable=True)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="sections")