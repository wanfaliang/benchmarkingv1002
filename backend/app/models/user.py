"""User database model"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


from ..database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Changed to nullable=True
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # NEW: Google OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    auth_provider = Column(String, default="local")  # "local" or "google"
    avatar_url = Column(String, nullable=True)
    
    # NEW: Email verification fields
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Relationship
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    # Add these relationships:
    datasets = relationship("Dataset", back_populates="owner", foreign_keys="Dataset.user_id")
    dashboards = relationship("Dashboard", back_populates="user")
    saved_queries = relationship("SavedQuery", back_populates="user")
    saved_screens = relationship("SavedScreen", back_populates="user", cascade="all, delete-orphan")