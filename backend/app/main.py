"""FastAPI application entry point"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .api import auth, tickers, analyses, websocket
from .config import settings

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
    debug=settings.DEBUG
)

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
app.include_router(websocket.router)  # ← Add this line

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