"""
Market Indices API - Real-time and historical index prices.

Provides endpoints for major market indices (S&P 500, NASDAQ, DJIA, Russell 2000).
- Primary: yfinance polling for real-time prices (when market is open)
- Fallback: PriceDailyBulk table for last trading day's adjusted close
- WebSocket: Push updates to connected clients
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc
import asyncio
import json
import logging

from backend.app.database import get_data_db
from backend.app.data_models import PriceDailyBulk
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research/market", tags=["Market Indices"])

# Major indices - symbols for both database and yfinance
MARKET_INDICES = {
    "^GSPC": {"name": "S&P 500"},
    "^IXIC": {"name": "Nasdaq"},
    "^DJI": {"name": "DJIA"},
    "^RUT": {"name": "Russell 2000"},
}

# Cache for real-time prices (updated by yfinance polling)
_realtime_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamp: Optional[datetime] = None

# Connected WebSocket clients
_connected_clients: Set[WebSocket] = set()
_polling_task: Optional[asyncio.Task] = None


def get_recent_prices_from_db(
    db: Session,
    symbols: List[str],
    days_back: int = 7
) -> Dict[str, Dict[str, Any]]:
    """
    Get most recent prices from PriceDailyBulk for given symbols.
    """
    results = {}
    start_date = date.today() - timedelta(days=days_back)

    for symbol in symbols:
        # Get most recent price data
        price = db.query(PriceDailyBulk).filter(
            PriceDailyBulk.symbol == symbol,
            PriceDailyBulk.date >= start_date,
        ).order_by(desc(PriceDailyBulk.date)).first()

        if price:
            # Get previous day's close for change calculation
            prev_price = db.query(PriceDailyBulk).filter(
                PriceDailyBulk.symbol == symbol,
                PriceDailyBulk.date < price.date,
            ).order_by(desc(PriceDailyBulk.date)).first()

            current_close = float(price.adj_close) if price.adj_close else float(price.close) if price.close else None
            prev_close = None
            if prev_price:
                prev_close = float(prev_price.adj_close) if prev_price.adj_close else float(prev_price.close) if prev_price.close else None

            # Calculate change
            change = None
            change_pct = None
            if current_close and prev_close:
                change = current_close - prev_close
                change_pct = (change / prev_close) * 100

            results[symbol] = {
                "date": price.date.isoformat(),
                "price": current_close,
                "prev_close": prev_close,
                "change": round(change, 2) if change else None,
                "change_pct": round(change_pct, 2) if change_pct else None,
                "volume": price.volume,
                "source": "eod",
            }
        else:
            results[symbol] = None

    return results


def get_historical_prices(
    db: Session,
    symbol: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """Get historical price data for sparkline chart."""
    start_date = date.today() - timedelta(days=days)

    prices = db.query(PriceDailyBulk).filter(
        PriceDailyBulk.symbol == symbol,
        PriceDailyBulk.date >= start_date,
    ).order_by(PriceDailyBulk.date).all()

    return [
        {
            "date": p.date.isoformat(),
            "value": float(p.adj_close) if p.adj_close else float(p.close) if p.close else None,
        }
        for p in prices
        if p.adj_close or p.close
    ]


def get_market_status() -> str:
    """Determine if US market is open."""
    try:
        from zoneinfo import ZoneInfo
        eastern = ZoneInfo('America/New_York')
        now = datetime.now(eastern)

        if now.weekday() >= 5:
            return "closed"

        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        if market_open <= now <= market_close:
            return "open"
        elif now < market_open:
            return "pre-market"
        else:
            return "after-hours"
    except Exception:
        return "unknown"


@router.get("/indices")
async def get_market_indices(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current prices for major market indices.
    Returns S&P 500, Nasdaq, DJIA, and Russell 2000.
    """
    symbols = list(MARKET_INDICES.keys())

    # Check real-time cache first
    use_realtime = False
    if _cache_timestamp and (datetime.now() - _cache_timestamp).seconds < 60:
        use_realtime = True

    # Get prices from database as fallback
    db_prices = get_recent_prices_from_db(db, symbols)

    indices = []
    for symbol in symbols:
        info = MARKET_INDICES[symbol]

        # Try real-time cache first - but only if it has actual price data
        rt = _realtime_cache.get(symbol, {})
        if use_realtime and rt.get("price") is not None:
            price_data = {
                "price": rt.get("price"),
                "change": rt.get("change"),
                "change_pct": rt.get("change_pct"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "realtime",
            }
        else:
            # Fall back to database
            price_data = db_prices.get(symbol)

        # Get sparkline data
        sparkline = get_historical_prices(db, symbol, days=10)
        sparkline_values = [p["value"] for p in sparkline[-6:]] if sparkline else []

        if price_data:
            indices.append({
                "symbol": symbol,
                "name": info["name"],
                "price": price_data.get("price"),
                "change": price_data.get("change"),
                "change_pct": price_data.get("change_pct"),
                "date": price_data.get("date"),
                "sparkline": sparkline_values,
                "source": price_data.get("source", "eod"),
                "is_realtime": price_data.get("source") == "realtime",
            })
        else:
            indices.append({
                "symbol": symbol,
                "name": info["name"],
                "price": None,
                "change": None,
                "change_pct": None,
                "date": None,
                "sparkline": [],
                "source": None,
                "is_realtime": False,
            })

    return {
        "as_of": datetime.now().isoformat(),
        "market_status": get_market_status(),
        "indices": indices,
    }


@router.get("/indices/{symbol}/history")
async def get_index_history(
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for a specific index."""
    if symbol not in MARKET_INDICES:
        return {"error": f"Unknown symbol: {symbol}"}

    history = get_historical_prices(db, symbol, days)
    return {
        "symbol": symbol,
        "name": MARKET_INDICES[symbol]["name"],
        "data": history,
    }


# ============================================================================
# YFINANCE POLLING + WEBSOCKET PUSH
# ============================================================================

def fetch_realtime_prices() -> Dict[str, Dict[str, Any]]:
    """Fetch real-time prices from yfinance."""
    import yfinance as yf

    results = {}
    symbols = list(MARKET_INDICES.keys())

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            price = info.get("regularMarketPrice") or info.get("currentPrice")
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
            change = info.get("regularMarketChange")
            change_pct = info.get("regularMarketChangePercent")

            if price is not None:
                results[symbol] = {
                    "price": round(price, 2),
                    "prev_close": round(prev_close, 2) if prev_close else None,
                    "change": round(change, 2) if change else None,
                    "change_pct": round(change_pct, 2) if change_pct else None,
                    "source": "realtime",
                }
        except Exception as e:
            logger.error(f"Failed to fetch {symbol} from yfinance: {e}")

    return results


async def broadcast_to_clients(data: Dict[str, Any]):
    """Send data to all connected WebSocket clients."""
    if not _connected_clients:
        return

    message = json.dumps(data)
    disconnected = set()

    for client in _connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected.add(client)

    # Remove disconnected clients
    for client in disconnected:
        _connected_clients.discard(client)


async def polling_loop():
    """Background task to poll yfinance and push updates."""
    global _realtime_cache, _cache_timestamp

    logger.info("Starting yfinance polling loop (every 10 seconds)")

    while True:
        try:
            # Only poll during market hours
            market_status = get_market_status()
            if market_status == "open":
                # Fetch prices in a thread to avoid blocking
                loop = asyncio.get_event_loop()
                prices = await loop.run_in_executor(None, fetch_realtime_prices)

                if prices:
                    _realtime_cache.update(prices)
                    _cache_timestamp = datetime.now()

                    # Broadcast to connected clients
                    await broadcast_to_clients({
                        "type": "indices_update",
                        "data": prices,
                        "timestamp": _cache_timestamp.isoformat(),
                        "market_status": market_status,
                    })
                    logger.debug(f"Broadcasted prices to {len(_connected_clients)} clients")

            await asyncio.sleep(10)  # Poll every 10 seconds
        except Exception as e:
            logger.error(f"Polling loop error: {e}")
            await asyncio.sleep(10)


@router.websocket("/ws/indices")
async def websocket_indices(websocket: WebSocket):
    """WebSocket endpoint for real-time index prices."""
    await websocket.accept()
    _connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(_connected_clients)}")

    try:
        # Send current cache immediately on connect
        if _realtime_cache:
            await websocket.send_text(json.dumps({
                "type": "indices_update",
                "data": _realtime_cache,
                "timestamp": _cache_timestamp.isoformat() if _cache_timestamp else None,
                "market_status": get_market_status(),
            }))

        # Keep connection alive
        while True:
            try:
                # Wait for any message (ping/pong or close)
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # Send ping to keep alive
                await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        pass
    finally:
        _connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(_connected_clients)}")


async def start_polling():
    """Start the yfinance polling background task."""
    global _polling_task

    if _polling_task is None or _polling_task.done():
        _polling_task = asyncio.create_task(polling_loop())
        logger.info("yfinance polling task started")


async def stop_polling():
    """Stop the polling background task."""
    global _polling_task

    if _polling_task and not _polling_task.done():
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass
        logger.info("yfinance polling task stopped")
