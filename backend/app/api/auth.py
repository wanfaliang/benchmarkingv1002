"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import UserCreate, UserResponse, UserLogin
from ..schemas.auth import Token
from ..services.auth_service import register_user, authenticate_user
from ..core.deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return register_user(db, user_data)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    return authenticate_user(db, form_data.username, form_data.password)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user