from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from fastapi import HTTPException, status
import uuid

from ..models.user import User
from ..schemas.user import UserCreate
from ..schemas.auth import Token
from ..core.security import verify_password, get_password_hash, create_access_token
from ..config import settings
from .email_service import generate_verification_token, send_verification_email, send_welcome_email

def register_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user and send verification email"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification token
    token, expires = generate_verification_token()
    
    # Create new user (not verified)
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        auth_provider="local",
        email_verified=False,  # NEW: Not verified yet
        verification_token=token,
        verification_token_expires=expires
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    send_verification_email(user.email, token, user.full_name)
    
    return user


def authenticate_user(db: Session, email: str, password: str) -> Token:
    """Authenticate user and return JWT token"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
        
    # Verify password
    if not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # NEW: Check if email is verified (optional - you can allow unverified login)
    # Uncomment this if you want to require verification before login:
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in."
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


def authenticate_google_user(db: Session, google_user_info: dict) -> Token:
    """Authenticate or create user from Google OAuth"""
    google_id = google_user_info['google_id']
    email = google_user_info['email']
    
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if not user:
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Link Google account
            user.google_id = google_id
            user.auth_provider = "google"
            user.avatar_url = google_user_info.get('avatar_url')
            user.email_verified = True  # Google accounts are pre-verified
        else:
            # Create new user
            user = User(
                user_id=str(uuid.uuid4()),
                email=email,
                full_name=google_user_info['name'],
                google_id=google_id,
                auth_provider="google",
                avatar_url=google_user_info.get('avatar_url'),
                password_hash=None,
                email_verified=True  # Google accounts are pre-verified
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


def verify_email_token(db: Session, token: str) -> User:
    """Verify email using token"""
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token,please request a new one or check the latest email sent to you."
        )
    
    # Check if token expired
    if user.verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one."
        )
    
    # Mark email as verified
    user.email_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    
    db.commit()
    db.refresh(user)
    
    # Send welcome email
    send_welcome_email(user.email, user.full_name)
    
    return user


def resend_verification_email(db: Session, email: str):
    """Resend verification email"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new token
    token, expires = generate_verification_token()
    user.verification_token = token
    user.verification_token_expires = expires
    
    db.commit()
    
    # Send email
    send_verification_email(user.email, token, user.full_name)
    
    return {"message": "Verification email sent"}