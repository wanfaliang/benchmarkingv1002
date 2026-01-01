"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database - set in .env file
    # PostgreSQL: postgresql://user:password@localhost:5432/finexus_app
    # SQLite (dev): sqlite:///./financial_analysis.db
    DATABASE_URL: str

    # DATA project database (read-only access for Research module)
    # Contains: economic (BEA, BLS), treasury, financial/market data
    DATA_DATABASE_URL: Optional[str] = None

    # DATA database connection pool settings (for high-concurrency queries like BEA 50 states)
    DATA_DB_POOL_SIZE: int = 20
    DATA_DB_MAX_OVERFLOW: int = 10
    DATA_DB_POOL_RECYCLE: int = 3600

    FRONTEND_URL: str = "http://localhost:3000"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DOCS_PASSWORD: str
    
    # API Keys
    FMP_API_KEY: Optional[str] = None
    FRED_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    
    # File Storage
    DATA_DIR: str = "./data"
    
    # Application
    DEBUG: bool = True
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    RESEND_API_KEY: str
    FROM_EMAIL: str = "onboarding@resend.dev"  # Default Resend test email

    # Redis Configuration
    REDIS_URL: Optional[str] = None  # Full URL overrides host/port/db
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_PREFIX: str = "finexus"

    # Cache webhook (for DATA project to trigger cache clear)
    CACHE_WEBHOOK_SECRET: str = "change-me-in-production"

    # Cache TTLs (seconds) - session-based caching
    CACHE_TTL_BLS: int = 900          # 15 min - session scope
    CACHE_TTL_TREASURY: int = 900     # 15 min - session scope
    CACHE_TTL_CLAIMS: int = 900       # 15 min - session scope
    CACHE_TTL_FRED: int = 900         # 15 min - session scope
    CACHE_TTL_AUTH: int = 1800        # 30 min - user auth
    CACHE_TTL_DEFAULT: int = 900      # 15 min - fallback

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()