"""
Price Calculator Service

Computes derived price-based features from prices_daily:
- 52-week high/low
- Returns (1D, 1W, 1M, 3M, 6M, YTD, 1Y)
- Volatility metrics
- Price vs moving averages
"""

from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, text
from datetime import date, timedelta
from decimal import Decimal
import math

from ...data_models import PriceDaily, PriceDailyBulk


def safe_float(value) -> float | None:
    """Convert to float, returning None for None, NaN, or Infinity values."""
    if value is None:
        return None
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


class PriceCalculator:
    """
    Service for computing price-based features.

    Uses prices_daily table to calculate:
    - 52-week high/low and % from high/low
    - Returns over various periods
    - Technical indicators (future)
    """

    # Trading days approximation for each period
    TRADING_DAYS = {
        "1d": 1,
        "1w": 5,
        "1m": 21,
        "3m": 63,
        "6m": 126,
        "1y": 252,
        "52w": 252,
    }

    def __init__(self, db: Session):
        self.db = db
        self._latest_price_date = None

    @property
    def latest_price_date(self) -> date:
        """Get the most recent date with price data."""
        if self._latest_price_date is None:
            # Try PriceDaily first, fallback to PriceDailyBulk
            result = self.db.query(func.max(PriceDaily.date)).scalar()
            if result is None:
                result = self.db.query(func.max(PriceDailyBulk.date)).scalar()
            self._latest_price_date = result
        return self._latest_price_date

    def get_52_week_stats(self, symbol: str) -> Dict[str, Any]:
        """
        Get 52-week high/low and current position for a symbol.

        Returns:
            {
                "high_52w": float,
                "low_52w": float,
                "high_52w_date": date,
                "low_52w_date": date,
                "pct_from_high": float,  # negative when below high
                "pct_from_low": float,   # positive when above low
            }
        """
        if not self.latest_price_date:
            return {}

        # Calculate date 252 trading days ago (approximately 1 year)
        lookback_date = self.latest_price_date - timedelta(days=365)

        # Query for 52-week high and low
        stats = self.db.query(
            func.max(PriceDaily.adj_high).label("high_52w"),
            func.min(PriceDaily.adj_low).label("low_52w"),
        ).filter(
            PriceDaily.symbol == symbol,
            PriceDaily.date >= lookback_date,
            PriceDaily.date <= self.latest_price_date,
        ).first()

        if not stats or stats.high_52w is None:
            return {}

        # Get current price
        current = self.db.query(PriceDaily.adj_close).filter(
            PriceDaily.symbol == symbol,
            PriceDaily.date == self.latest_price_date,
        ).scalar()

        if current is None:
            # Try to get most recent price for this symbol
            current_row = self.db.query(PriceDaily.adj_close).filter(
                PriceDaily.symbol == symbol,
            ).order_by(desc(PriceDaily.date)).first()
            current = current_row[0] if current_row else None

        if current is None:
            return {
                "high_52w": safe_float(stats.high_52w),
                "low_52w": safe_float(stats.low_52w),
            }

        high = float(stats.high_52w)
        low = float(stats.low_52w)
        price = float(current)

        return {
            "high_52w": safe_float(high),
            "low_52w": safe_float(low),
            "pct_from_high": safe_float((price - high) / high * 100) if high > 0 else None,
            "pct_from_low": safe_float((price - low) / low * 100) if low > 0 else None,
        }

    def get_returns(self, symbol: str) -> Dict[str, float]:
        """
        Calculate returns over various periods for a symbol.

        Returns:
            {
                "return_1d": float,   # 1-day return %
                "return_1w": float,   # 1-week return %
                "return_1m": float,   # 1-month return %
                "return_3m": float,   # 3-month return %
                "return_6m": float,   # 6-month return %
                "return_ytd": float,  # Year-to-date return %
                "return_1y": float,   # 1-year return %
            }
        """
        if not self.latest_price_date:
            return {}

        # Get all prices for this symbol in the last year
        lookback_date = self.latest_price_date - timedelta(days=400)  # Extra buffer

        prices = self.db.query(
            PriceDaily.date,
            PriceDaily.adj_close
        ).filter(
            PriceDaily.symbol == symbol,
            PriceDaily.date >= lookback_date,
        ).order_by(desc(PriceDaily.date)).all()

        if not prices or len(prices) < 2:
            return {}

        # Convert to list of (date, price) sorted by date descending
        price_list = [(p.date, float(p.adj_close)) for p in prices if p.adj_close]

        if not price_list:
            return {}

        current_date, current_price = price_list[0]

        returns = {}

        # Calculate returns for each period
        periods = [
            ("return_1d", 1),
            ("return_1w", 5),
            ("return_1m", 21),
            ("return_3m", 63),
            ("return_6m", 126),
            ("return_1y", 252),
        ]

        for return_name, days_back in periods:
            if len(price_list) > days_back:
                past_date, past_price = price_list[days_back]
                if past_price > 0:
                    returns[return_name] = safe_float((current_price - past_price) / past_price * 100)

        # YTD return - from Jan 1 of current year
        year_start = date(current_date.year, 1, 1)
        ytd_price = None
        for p_date, p_price in price_list:
            if p_date <= year_start:
                ytd_price = p_price
                break

        if ytd_price and ytd_price > 0:
            returns["return_ytd"] = safe_float((current_price - ytd_price) / ytd_price * 100)

        return returns

    def get_price_features_batch(
        self,
        symbols: List[str],
        include_52w: bool = True,
        include_returns: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get price-based features for multiple symbols efficiently.

        This is a batch operation that minimizes database queries.

        Returns:
            {
                "AAPL": {"high_52w": 200, "return_1m": 5.2, ...},
                "MSFT": {"high_52w": 450, "return_1m": 3.1, ...},
                ...
            }
        """
        if not self.latest_price_date or not symbols:
            return {}

        results = {s: {} for s in symbols}

        if include_52w:
            self._batch_52w_stats(symbols, results)

        if include_returns:
            self._batch_returns(symbols, results)

        return results

    def _batch_52w_stats(self, symbols: List[str], results: Dict[str, Dict]):
        """Batch calculate 52-week stats for multiple symbols."""
        lookback_date = self.latest_price_date - timedelta(days=365)

        # Get 52-week high/low for all symbols in one query
        stats = self.db.query(
            PriceDaily.symbol,
            func.max(PriceDaily.adj_high).label("high_52w"),
            func.min(PriceDaily.adj_low).label("low_52w"),
        ).filter(
            PriceDaily.symbol.in_(symbols),
            PriceDaily.date >= lookback_date,
            PriceDaily.date <= self.latest_price_date,
        ).group_by(PriceDaily.symbol).all()

        # Get latest prices for all symbols
        latest_prices = self.db.query(
            PriceDaily.symbol,
            PriceDaily.adj_close
        ).filter(
            PriceDaily.symbol.in_(symbols),
            PriceDaily.date == self.latest_price_date,
        ).all()

        price_map = {p.symbol: float(p.adj_close) for p in latest_prices if p.adj_close}

        for stat in stats:
            symbol = stat.symbol
            if symbol not in results:
                continue

            high = safe_float(stat.high_52w)
            low = safe_float(stat.low_52w)
            price = price_map.get(symbol)

            results[symbol]["high_52w"] = high
            results[symbol]["low_52w"] = low

            if price and high and high > 0:
                results[symbol]["pct_from_high"] = safe_float((price - high) / high * 100)
            if price and low and low > 0:
                results[symbol]["pct_from_low"] = safe_float((price - low) / low * 100)

    def _batch_returns(self, symbols: List[str], results: Dict[str, Dict]):
        """Batch calculate returns for multiple symbols."""
        lookback_date = self.latest_price_date - timedelta(days=400)

        # Get relevant date lookbacks
        target_dates = {}
        for days_back in [1, 5, 21, 63, 126, 252]:
            target_date = self.latest_price_date - timedelta(days=int(days_back * 1.5))
            target_dates[days_back] = target_date

        # Get all prices in the lookback period
        prices = self.db.query(
            PriceDaily.symbol,
            PriceDaily.date,
            PriceDaily.adj_close
        ).filter(
            PriceDaily.symbol.in_(symbols),
            PriceDaily.date >= lookback_date,
        ).order_by(
            PriceDaily.symbol,
            desc(PriceDaily.date)
        ).all()

        # Organize prices by symbol
        symbol_prices = {}
        for p in prices:
            if p.symbol not in symbol_prices:
                symbol_prices[p.symbol] = []
            if p.adj_close:
                symbol_prices[p.symbol].append((p.date, float(p.adj_close)))

        # Calculate returns for each symbol
        periods = [
            ("return_1d", 1),
            ("return_1w", 5),
            ("return_1m", 21),
            ("return_3m", 63),
            ("return_6m", 126),
            ("return_1y", 252),
        ]

        for symbol, price_list in symbol_prices.items():
            if symbol not in results or len(price_list) < 2:
                continue

            current_price = price_list[0][1]

            for return_name, days_back in periods:
                if len(price_list) > days_back:
                    past_price = price_list[days_back][1]
                    if past_price > 0:
                        results[symbol][return_name] = safe_float(
                            (current_price - past_price) / past_price * 100
                        )


def compute_relative_volume(volume: float, avg_volume: float) -> Optional[float]:
    """Compute relative volume (current volume / average volume)."""
    if avg_volume and avg_volume > 0:
        return safe_float(volume / avg_volume)
    return None


def compute_price_target_upside(
    current_price: float,
    target_price: float
) -> Optional[float]:
    """Compute upside to price target as percentage."""
    if current_price and current_price > 0 and target_price:
        return safe_float((target_price - current_price) / current_price * 100)
    return None
