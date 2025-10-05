"""Dependencies for FastAPI routes"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user from JWT token"""
    if not token:
        print("Missing or malformed Authorization header")  # Debug
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    print(f"Received token (prefix): {token[:50]}...")  # Debug (safe now)
    print(f"Received token: {token[:50]}...")  # Debug
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    print(f"Decoded payload: {payload}")  # Debug
    
    if payload is None:
        print("Token decode failed")  # Debug
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    print(f"User ID from token: {user_id}")  # Debug
    
    if user_id is None:
        print("No user_id in token")  # Debug
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    print(f"User found in DB: {user}")  # Debug
    
    if user is None:
        print("User not found in database")  # Debug
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user