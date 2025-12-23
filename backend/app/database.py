"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


def get_engine_config(database_url: str):
    """Get engine configuration based on database URL"""
    if database_url.startswith("sqlite"):
        # SQLite-specific settings
        return {
            "connect_args": {"check_same_thread": False}
        }
    elif database_url.startswith("postgresql"):
        # PostgreSQL-specific settings
        return {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,  # Verify connections before use
        }
    else:
        return {}


# =============================================================================
# Primary Database (Finexus App - users, analyses, datasets)
# =============================================================================

engine = create_engine(
    settings.DATABASE_URL,
    **get_engine_config(settings.DATABASE_URL)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session for Finexus app database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# DATA Database (Read-only - economic, treasury, financial/market data)
# =============================================================================

data_engine = None
DataSessionLocal = None
DataBase = declarative_base()

if settings.DATA_DATABASE_URL:
    # Use configurable pool settings for high-concurrency queries (BEA 50 states, etc.)
    data_engine = create_engine(
        settings.DATA_DATABASE_URL,
        pool_size=settings.DATA_DB_POOL_SIZE,
        max_overflow=settings.DATA_DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=settings.DATA_DB_POOL_RECYCLE,
    )
    DataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=data_engine)


def get_data_db():
    """Get database session for DATA database (read-only)"""
    if DataSessionLocal is None:
        raise RuntimeError("DATA_DATABASE_URL not configured")
    db = DataSessionLocal()
    try:
        yield db
    finally:
        db.close()