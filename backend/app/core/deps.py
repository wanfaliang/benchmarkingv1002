"""Dependencies for FastAPI routes"""
import json
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from .security import decode_access_token
from .cache.client import get_redis_client
from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _get_cached_user(user_id: str) -> dict | None:
    """Get user from Redis cache."""
    client = get_redis_client()
    if not client:
        return None
    try:
        data = client.get(f"{settings.CACHE_PREFIX}:auth:user:{user_id}")
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


def _cache_user(user_id: str, user_data: dict) -> None:
    """Cache user data in Redis."""
    client = get_redis_client()
    if not client:
        return
    try:
        key = f"{settings.CACHE_PREFIX}:auth:user:{user_id}"
        client.setex(key, settings.CACHE_TTL_AUTH, json.dumps(user_data))
    except Exception:
        pass  # Fail silently


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user from JWT token (with Redis caching)"""
    if not token:
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token (CPU only, no DB/cache)
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Try cache first
    cached_data = _get_cached_user(user_id)
    if cached_data:
        from datetime import datetime
        # Reconstruct User object from cached data
        user = User(
            user_id=cached_data["user_id"],
            email=cached_data["email"],
            full_name=cached_data.get("full_name"),
            is_active=cached_data["is_active"],
            email_verified=cached_data.get("email_verified", False),
            created_at=datetime.fromisoformat(cached_data["created_at"]) if cached_data.get("created_at") else datetime.utcnow(),
        )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user

    # Cache miss - query database
    user = db.query(User).filter(User.user_id == user_id).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Cache for next time
    _cache_user(user_id, {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })

    return user