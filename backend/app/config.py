"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./financial_analysis.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    FMP_API_KEY: Optional[str] = None
    FRED_API_KEY: Optional[str] = None
    
    # File Storage
    DATA_DIR: str = "./data"
    
    # Application
    DEBUG: bool = True
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()