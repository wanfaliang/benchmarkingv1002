"""Stocks API package - Stock Screener endpoints"""
from fastapi import APIRouter
from .router import router as stocks_router
from .features import router as features_router
from .templates import router as templates_router
from .computed import router as computed_router
from .screens import router as screens_router

# Main router that combines all sub-routers
router = APIRouter(prefix="/api/stocks", tags=["stocks"])

# Include sub-routers
router.include_router(features_router)
router.include_router(templates_router)
router.include_router(computed_router)
router.include_router(screens_router)
router.include_router(stocks_router)

__all__ = ["router"]
