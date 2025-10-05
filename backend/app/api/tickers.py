"""Ticker validation API endpoints"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..services.ticker_service import ticker_service
from ..core.deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/tickers", tags=["tickers"])

class TickerValidateRequest(BaseModel):
    ticker: str

@router.post("/validate")
def validate_ticker(
    request: TickerValidateRequest,
    current_user: User = Depends(get_current_user)
):
    """Validate a stock ticker"""
    return ticker_service.validate_ticker(request.ticker)