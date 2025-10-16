"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import EmailStr

from ..database import get_db
from ..schemas.user import UserCreate, UserResponse, UserLogin
from ..schemas.auth import Token, GoogleTokenRequest
from ..services.auth_service import register_user, authenticate_user, authenticate_google_user
from ..core.deps import get_current_user
from ..models.user import User
from ..services.google_oauth_service import verify_google_token
from ..config import settings
from ..services.auth_service import verify_email_token, resend_verification_email

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

# NEW: Google OAuth endpoints
@router.post("/google/verify", response_model=Token)
async def verify_google(
    token_request: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Verify Google ID token and authenticate user (for frontend Google One Tap)
    
    This endpoint:
    1. Verifies the Google ID token
    2. Extracts user information
    3. Creates user if doesn't exist or links to existing account
    4. Returns JWT token for your app
    """
    # Verify the Google token
    google_user_info = await verify_google_token(token_request.id_token)
    
    # Authenticate or create user and get JWT token
    token = authenticate_google_user(db, google_user_info)
    
    return token


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth flow (redirect method)
    
    Redirects user to Google's consent screen.
    User will be redirected back to /auth/google/callback after consent.
    """
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline"
    )
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback (redirect method)
    
    This endpoint:
    1. Receives authorization code from Google
    2. Exchanges it for tokens
    3. Verifies the ID token
    4. Creates/links user account
    5. Redirects to frontend with JWT token
    """
    import httpx
    
    try:
        # Exchange authorization code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                    'grant_type': 'authorization_code'
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail="Failed to exchange code for token"
                )
            
            tokens = token_response.json()
            id_token = tokens['id_token']
        
        # Verify token and get user info
        google_user_info = await verify_google_token(id_token)
        
        # Authenticate or create user and get JWT token
        token = authenticate_google_user(db, google_user_info)
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/google/callback?token={token.access_token}"
        )
        
    except Exception as e:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={str(e)}"
        )

@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address using token from email"""
    user = verify_email_token(db, token)
    return {
        "message": "Email verified successfully!",
        "email": user.email
    }


@router.post("/resend-verification")
def resend_verification(email: EmailStr, db: Session = Depends(get_db)):
    """Resend verification email"""
    return resend_verification_email(db, email)