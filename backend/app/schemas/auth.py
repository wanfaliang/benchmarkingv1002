"""Authentication schemas"""
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: str


# NEW: Google OAuth schemas
class GoogleTokenRequest(BaseModel):
    """Request schema for Google ID token verification"""
    id_token: str


class GoogleUserInfo(BaseModel):
    """User info extracted from Google token"""
    google_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None