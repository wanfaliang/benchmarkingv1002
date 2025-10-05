"""User schemas for API requests/responses"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str

class UserResponse(UserBase):
    """Schema for user response (no password)"""
    user_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str