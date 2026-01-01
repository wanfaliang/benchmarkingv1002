"""FastAPI application entry point"""
from fastapi import FastAPI, HTTPException, Request,status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import secrets
from .api import auth, tickers, analyses, websocket, datasets
from .api.research import treasury as treasury_research
from .api.research import fred_explorer as fred_research
from .api.research import fred_claims_explorer as fred_claims_research
from .api.research import fred_fedfunds_explorer as fred_fedfunds_research
from .api.research import fred_sentiment_explorer as fred_sentiment_research
from .api.research import fred_leading_explorer as fred_leading_research
from .api.research import fred_housing_explorer as fred_housing_research
from .api.research.bls import cu_explorer as cu_research
from .api.research.bls import ln_explorer as ln_research
from .api.research.bls import la_explorer as la_research
from .api.research.bls import ce_explorer as ce_research
from .api.research.bls import pc_explorer as pc_research
from .api.research.bls import wp_explorer as wp_research
from .api.research.bls import ap_explorer as ap_research
from .api.research.bls import cw_explorer as cw_research
from .api.research.bls import sm_explorer as sm_research
from .api.research.bls import jt_explorer as jt_research
from .api.research.bls import oe_explorer as oe_research
from .api.research.bls import ec_explorer as ec_research
from .api.research.bls import pr_explorer as pr_research
from .api.research.bls import tu_explorer as tu_research
from .api.research.bls import ip_explorer as ip_research
from .api.research.bls import su_explorer as su_research
from .api.research.bls import bd_explorer as bd_research
from .api.research.bls import ei_explorer as ei_research
from .api.research import portal_api as portal_research
from .api.research import market_indices as market_research
from .api.research import economic_calendar as calendar_research
from .api.research import bea_explorer as bea_research
from .api.research import fred_calendar as fred_calendar_research
from .api.research.market_indices import start_polling, get_market_status
from .config import settings
from .core.cache.client import get_redis_client, get_cache_stats

import logging
import sys
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(sys.stdout)  # Also print to console
    ]
)


logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Financial Analysis Platform",
    description="Web-based financial analysis and reporting platform",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url=None, redoc_url=None
)
security = HTTPBasic()
DOCS_USERNAME = "admin"
DOCS_PASSWORD = settings.DOCS_PASSWORD

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://finexus.net","https://www.finexus.net",
        "https://api.finexus.net","http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tickers.router)
app.include_router(analyses.router)
app.include_router(websocket.router)
app.include_router(datasets.router)

# Research module routers (DATA database)
app.include_router(treasury_research.router)
app.include_router(fred_research.router)
app.include_router(fred_claims_research.router)
app.include_router(fred_fedfunds_research.router)
app.include_router(fred_sentiment_research.router)
app.include_router(fred_leading_research.router)
app.include_router(fred_housing_research.router)
app.include_router(cu_research.router)
app.include_router(ln_research.router)
app.include_router(la_research.router)
app.include_router(ce_research.router)
app.include_router(pc_research.router)
app.include_router(wp_research.router)
app.include_router(ap_research.router)
app.include_router(cw_research.router)
app.include_router(sm_research.router)
app.include_router(jt_research.router)
app.include_router(oe_research.router)
app.include_router(ec_research.router)
app.include_router(pr_research.router)
app.include_router(tu_research.router)
app.include_router(ip_research.router)
app.include_router(su_research.router)
app.include_router(bd_research.router)
app.include_router(ei_research.router)

# Research Portal API
app.include_router(portal_research.router)

# Market Indices API
app.include_router(market_research.router)

# Economic Calendar API
app.include_router(calendar_research.router)

# BEA (Bureau of Economic Analysis) API
app.include_router(bea_research.router)

# FRED Calendar API
app.include_router(fred_calendar_research.router)

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Compares the provided credentials with the secure ones.
    """
    correct_username = secrets.compare_digest(credentials.username, DOCS_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, DOCS_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    """
    Serves the protected Swagger UI.
    """
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title + " - Swagger UI")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Financial Analysis Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/health/cache")
def cache_health_check():
    """Cache health check endpoint - returns Redis connection status and stats"""
    stats = get_cache_stats()
    return {
        "cache": stats,
        "config": {
            "enabled": settings.CACHE_ENABLED,
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
        }
    }


@app.delete("/cache", tags=["Admin"])
def clear_data_cache(username: str = Depends(get_current_username)):
    """Clear all data cache (keeps auth cache intact). Admin only."""
    client = get_redis_client()
    if not client:
        raise HTTPException(status_code=503, detail="Cache not available")

    prefix = settings.CACHE_PREFIX
    auth_prefix = f"{prefix}:auth:"

    deleted = 0
    for key in client.scan_iter(f"{prefix}:*"):
        key_str = key if isinstance(key, str) else key.decode()
        if not key_str.startswith(auth_prefix):
            client.delete(key)
            deleted += 1

    return {"deleted": deleted}


@app.delete("/cache/webhook", tags=["Webhook"])
def cache_webhook(
    source: str = None,
    x_webhook_key: str = None
):
    """
    Webhook for DATA project to clear cache after data updates.

    - source: Optional, e.g. "bls", "fred", "treasury" to clear specific cache
    - x_webhook_key: Secret key (pass as query param or header)
    """
    # Check secret key
    if x_webhook_key != settings.CACHE_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook key")

    client = get_redis_client()
    if not client:
        raise HTTPException(status_code=503, detail="Cache not available")

    prefix = settings.CACHE_PREFIX
    auth_prefix = f"{prefix}:auth:"

    # Determine pattern based on source
    if source:
        search_pattern = f"{prefix}:{source}:*"
    else:
        search_pattern = f"{prefix}:*"

    deleted = 0
    for key in client.scan_iter(search_pattern):
        key_str = key if isinstance(key, str) else key.decode()
        if not key_str.startswith(auth_prefix):
            client.delete(key)
            deleted += 1

    return {"deleted": deleted, "source": source or "all"}


# Debug endpoint to verify WebSocket route is registered
@app.get("/debug/routes")
def list_routes():
    """List all registered routes (including WebSocket)"""
    routes = []
    for route in app.routes:
        route_info = {
            "path": route.path,
            "name": route.name,
        }
        # Check if it's a WebSocket route
        if hasattr(route, 'methods'):
            route_info["methods"] = list(route.methods)
        elif 'websocket' in route.path.lower() or route.path.startswith('/api/ws'):
            route_info["type"] = "WebSocket"
        
        routes.append(route_info)
    return {
        "total_routes": len(routes),
        "routes": routes
    }

FAVICON_PATH = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "favicon.ico"

@app.get("/favicon.ico")
def favicon():
    if FAVICON_PATH and FAVICON_PATH.exists():
        return FileResponse(FAVICON_PATH, media_type="image/x-icon")
    # (Optional) return 204 to silence logs if the file isn't there yet
    # return Response(status_code=204)
    raise HTTPException(status_code=404, detail="favicon not found")

@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
  return JSONResponse(status_code=500, content={"detail":"Internal Server Error"})


# Startup event to initialize yfinance polling for real-time market data
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize Redis cache connection
    try:
        redis = get_redis_client()
        if redis:
            logger.info("Redis cache connected successfully")
        else:
            logger.warning("Redis cache not available - running without cache")
    except Exception as e:
        logger.warning(f"Redis cache initialization failed: {e}")

    # Start yfinance polling for real-time index prices
    try:
        market_status = get_market_status()
        logger.info(f"Market status: {market_status}")

        await start_polling()
        logger.info("yfinance polling started for real-time index prices")
    except Exception as e:
        logger.error(f"Failed to start yfinance polling: {e}")