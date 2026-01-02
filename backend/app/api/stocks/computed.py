"""
Computed Features API endpoints

Provides endpoints for price-based computed features:
- 52-week high/low
- Returns (1D, 1W, 1M, 3M, 6M, YTD, 1Y)
- Relative volume
- Price target upside
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from ...database import get_data_db
from ...services.stocks import PriceCalculator

router = APIRouter(prefix="/computed", tags=["computed"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ComputedFeaturesRequest(BaseModel):
    """Request for computed features for multiple symbols"""
    symbols: List[str]
    include_52w: bool = True
    include_returns: bool = True


class ComputedFeaturesResponse(BaseModel):
    """Response with computed features by symbol"""
    data: Dict[str, Dict[str, Any]]
    symbols_requested: int
    symbols_found: int


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/{symbol}")
def get_computed_features(
    symbol: str,
    data_db: Session = Depends(get_data_db)
):
    """
    Get all computed features for a single symbol.

    Returns 52-week stats and returns.
    """
    calculator = PriceCalculator(data_db)

    result = {
        "symbol": symbol.upper(),
    }

    # Get 52-week stats
    stats_52w = calculator.get_52_week_stats(symbol.upper())
    result.update(stats_52w)

    # Get returns
    returns = calculator.get_returns(symbol.upper())
    result.update(returns)

    return result


@router.post("/batch", response_model=ComputedFeaturesResponse)
def get_computed_features_batch(
    request: ComputedFeaturesRequest,
    data_db: Session = Depends(get_data_db)
):
    """
    Get computed features for multiple symbols in one request.

    This is optimized for batch operations and is used by the screener
    to enrich results with computed features.
    """
    if not request.symbols:
        return ComputedFeaturesResponse(
            data={},
            symbols_requested=0,
            symbols_found=0
        )

    # Normalize symbols to uppercase
    symbols = [s.upper() for s in request.symbols]

    calculator = PriceCalculator(data_db)

    # Get features for all symbols
    data = calculator.get_price_features_batch(
        symbols=symbols,
        include_52w=request.include_52w,
        include_returns=request.include_returns
    )

    return ComputedFeaturesResponse(
        data=data,
        symbols_requested=len(symbols),
        symbols_found=len([s for s in data if data[s]])  # Count non-empty results
    )


@router.get("/{symbol}/52week")
def get_52_week_stats(
    symbol: str,
    data_db: Session = Depends(get_data_db)
):
    """Get 52-week high/low statistics for a symbol."""
    calculator = PriceCalculator(data_db)
    stats = calculator.get_52_week_stats(symbol.upper())

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for symbol '{symbol}'"
        )

    return {
        "symbol": symbol.upper(),
        **stats
    }


@router.get("/{symbol}/returns")
def get_returns(
    symbol: str,
    data_db: Session = Depends(get_data_db)
):
    """Get historical returns for a symbol across various periods."""
    calculator = PriceCalculator(data_db)
    returns = calculator.get_returns(symbol.upper())

    if not returns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for symbol '{symbol}'"
        )

    return {
        "symbol": symbol.upper(),
        **returns
    }
