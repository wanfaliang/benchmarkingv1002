from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import HTTPException, status
import uuid

from ..models.user import User
from ..schemas.user import UserCreate
from ..schemas.auth import Token
from ..core.security import verify_password, get_password_hash, create_access_token
from ..config import settings

def register_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        auth_provider="local"  # NEW: Set auth provider
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

def authenticate_user(db: Session, email: str, password: str) -> Token:
    """Authenticate user and return JWT token"""
    # Get user
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


# NEW: Google OAuth authentication function
def authenticate_google_user(db: Session, google_user_info: dict) -> Token:
    """Authenticate or create user from Google OAuth and return JWT token"""
    google_id = google_user_info['google_id']
    email = google_user_info['email']
    
    # Try to find user by google_id first
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if not user:
        # Try to find by email (account linking)
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Link Google account to existing user
            user.google_id = google_id
            user.auth_provider = "google"
            user.avatar_url = google_user_info.get('avatar_url')
        else:
            # Create new user
            user = User(
                user_id=str(uuid.uuid4()),
                email=email,
                full_name=google_user_info['name'],
                google_id=google_id,
                auth_provider="google",
                avatar_url=google_user_info.get('avatar_url'),
                password_hash=None  # No password for OAuth users
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
    
    # Create JWT token (same as regular login)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")
