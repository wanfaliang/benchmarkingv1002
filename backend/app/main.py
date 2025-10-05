"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, tickers, analyses
from .config import settings

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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tickers.router)
app.include_router(analyses.router)

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