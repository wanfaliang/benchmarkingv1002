# Computed Features Implementation Guide

> **Target Project:** DATA Project (`D:\finexus-data-collector`)
> **Purpose:** Pre-compute stock features daily for fast screening
> **Schedule:** Daily after market close (~6 PM ET)
> **Estimated Runtime:** ~1-2 minutes for ~10,000 symbols

---

## 0. Tables Involved

### Input Tables (Read From)

| Table | Purpose | Columns Used |
|-------|---------|--------------|
| `prices_daily` | All price/volume data | `symbol`, `date`, `open`, `adj_close`, `adj_high`, `adj_low`, `volume` |
| `price_target_summary_bulk` | Analyst price targets (optional) | `symbol`, `last_month_avg_price_target` |

### Output Table (Write To)

| Table | Purpose |
|-------|---------|
| `stock_computed_features` | New table - stores all 47 computed features |

> **Note:** If `price_target_summary_bulk` doesn't exist or is named differently, comment out `_compute_analyst_data()` - those 2 features will be NULL.

---

## 1. Database Table

Create table `stock_computed_features` in the DATA database.

### Schema

```sql
CREATE TABLE stock_computed_features (
    -- Primary key
    symbol VARCHAR(20) PRIMARY KEY,

    -- Computation metadata
    compute_date DATE NOT NULL,
    price_date DATE NOT NULL,
    current_price NUMERIC(20, 4),

    -- =========================================================================
    -- 52-WEEK STATS
    -- =========================================================================
    high_52w NUMERIC(20, 4),
    low_52w NUMERIC(20, 4),
    high_52w_date DATE,
    low_52w_date DATE,
    pct_from_high NUMERIC(10, 4),         -- % below 52-week high (negative)
    pct_from_low NUMERIC(10, 4),          -- % above 52-week low (positive)
    range_position_52w NUMERIC(10, 4),    -- Position in 52w range (0-100%)
    days_since_high_52w INTEGER,          -- Trading days since 52w high
    days_since_low_52w INTEGER,           -- Trading days since 52w low

    -- =========================================================================
    -- RETURNS (as percentages, e.g., 5.25 = 5.25%)
    -- =========================================================================
    return_1d NUMERIC(10, 4),
    return_1w NUMERIC(10, 4),
    return_1m NUMERIC(10, 4),
    return_3m NUMERIC(10, 4),
    return_6m NUMERIC(10, 4),
    return_ytd NUMERIC(10, 4),
    return_1y NUMERIC(10, 4),

    -- =========================================================================
    -- MOVING AVERAGES
    -- =========================================================================
    sma_20 NUMERIC(20, 4),
    sma_50 NUMERIC(20, 4),
    sma_200 NUMERIC(20, 4),
    ema_12 NUMERIC(20, 4),
    ema_26 NUMERIC(20, 4),

    -- Price vs SMA ratios (as percentage, 105 = 5% above SMA)
    price_vs_sma20 NUMERIC(10, 4),
    price_vs_sma50 NUMERIC(10, 4),
    price_vs_sma200 NUMERIC(10, 4),

    -- Trend signals (boolean as integer: 1=true, 0=false)
    above_sma20 SMALLINT,
    above_sma50 SMALLINT,
    above_sma200 SMALLINT,
    golden_cross SMALLINT,                -- SMA50 > SMA200
    death_cross SMALLINT,                 -- SMA50 < SMA200

    -- =========================================================================
    -- MOMENTUM INDICATORS
    -- =========================================================================
    rsi_14 NUMERIC(10, 4),                -- 14-day RSI (0-100)
    roc_10 NUMERIC(10, 4),                -- 10-day Rate of Change %
    roc_20 NUMERIC(10, 4),                -- 20-day Rate of Change %

    -- MACD
    macd_line NUMERIC(10, 4),             -- EMA12 - EMA26
    macd_signal NUMERIC(10, 4),           -- 9-day EMA of MACD line
    macd_histogram NUMERIC(10, 4),        -- MACD - Signal

    -- =========================================================================
    -- VOLATILITY METRICS
    -- =========================================================================
    volatility_20d NUMERIC(10, 4),        -- 20-day annualized volatility %
    volatility_60d NUMERIC(10, 4),        -- 60-day annualized volatility %
    atr_14 NUMERIC(20, 4),                -- 14-day Average True Range
    atr_14_pct NUMERIC(10, 4),            -- ATR as % of price

    -- Drawdown
    max_drawdown_ytd NUMERIC(10, 4),      -- Max drawdown % YTD
    max_drawdown_1y NUMERIC(10, 4),       -- Max drawdown % 1 year

    -- =========================================================================
    -- VOLUME METRICS
    -- =========================================================================
    avg_volume_20d NUMERIC(20, 2),
    avg_volume_50d NUMERIC(20, 2),
    relative_volume NUMERIC(10, 4),       -- Today's volume / 20-day avg
    avg_dollar_volume_20d NUMERIC(20, 2), -- Price * Volume average
    volume_trend NUMERIC(10, 4),          -- 5d avg / 20d avg ratio

    -- =========================================================================
    -- PRICE ACTION
    -- =========================================================================
    gap_pct NUMERIC(10, 4),               -- Today open vs yesterday close %
    consecutive_up_days INTEGER,          -- Streak of positive days (negative for down)

    -- =========================================================================
    -- ANALYST / PRICE TARGET
    -- =========================================================================
    price_target_consensus NUMERIC(20, 4),
    price_target_upside NUMERIC(10, 4),

    -- =========================================================================
    -- METADATA
    -- =========================================================================
    updated_at TIMESTAMP NOT NULL
);

-- Indexes for common queries
CREATE INDEX ix_scf_compute_date ON stock_computed_features(compute_date);
CREATE INDEX ix_scf_rsi ON stock_computed_features(rsi_14);
CREATE INDEX ix_scf_volatility ON stock_computed_features(volatility_20d);
CREATE INDEX ix_scf_return_1m ON stock_computed_features(return_1m);
```

### SQLAlchemy Model

Add to `src/database/models.py`:

```python
from sqlalchemy import Column, String, Date, DateTime, Numeric, Integer, SmallInteger

class StockComputedFeatures(Base):
    """Pre-computed stock features, updated daily."""
    __tablename__ = 'stock_computed_features'

    symbol = Column(String(20), primary_key=True)
    compute_date = Column(Date, nullable=False, index=True)
    price_date = Column(Date, nullable=False)
    current_price = Column(Numeric(20, 4))

    # 52-Week Stats
    high_52w = Column(Numeric(20, 4))
    low_52w = Column(Numeric(20, 4))
    high_52w_date = Column(Date)
    low_52w_date = Column(Date)
    pct_from_high = Column(Numeric(10, 4))
    pct_from_low = Column(Numeric(10, 4))
    range_position_52w = Column(Numeric(10, 4))
    days_since_high_52w = Column(Integer)
    days_since_low_52w = Column(Integer)

    # Returns
    return_1d = Column(Numeric(10, 4))
    return_1w = Column(Numeric(10, 4))
    return_1m = Column(Numeric(10, 4))
    return_3m = Column(Numeric(10, 4))
    return_6m = Column(Numeric(10, 4))
    return_ytd = Column(Numeric(10, 4))
    return_1y = Column(Numeric(10, 4))

    # Moving Averages
    sma_20 = Column(Numeric(20, 4))
    sma_50 = Column(Numeric(20, 4))
    sma_200 = Column(Numeric(20, 4))
    ema_12 = Column(Numeric(20, 4))
    ema_26 = Column(Numeric(20, 4))
    price_vs_sma20 = Column(Numeric(10, 4))
    price_vs_sma50 = Column(Numeric(10, 4))
    price_vs_sma200 = Column(Numeric(10, 4))
    above_sma20 = Column(SmallInt)
    above_sma50 = Column(SmallInt)
    above_sma200 = Column(SmallInt)
    golden_cross = Column(SmallInt)
    death_cross = Column(SmallInt)

    # Momentum
    rsi_14 = Column(Numeric(10, 4))
    roc_10 = Column(Numeric(10, 4))
    roc_20 = Column(Numeric(10, 4))
    macd_line = Column(Numeric(10, 4))
    macd_signal = Column(Numeric(10, 4))
    macd_histogram = Column(Numeric(10, 4))

    # Volatility
    volatility_20d = Column(Numeric(10, 4))
    volatility_60d = Column(Numeric(10, 4))
    atr_14 = Column(Numeric(20, 4))
    atr_14_pct = Column(Numeric(10, 4))
    max_drawdown_ytd = Column(Numeric(10, 4))
    max_drawdown_1y = Column(Numeric(10, 4))

    # Volume
    avg_volume_20d = Column(Numeric(20, 2))
    avg_volume_50d = Column(Numeric(20, 2))
    relative_volume = Column(Numeric(10, 4))
    avg_dollar_volume_20d = Column(Numeric(20, 2))
    volume_trend = Column(Numeric(10, 4))

    # Price Action
    gap_pct = Column(Numeric(10, 4))
    consecutive_up_days = Column(Integer)

    # Analyst
    price_target_consensus = Column(Numeric(20, 4))
    price_target_upside = Column(Numeric(10, 4))

    updated_at = Column(DateTime, nullable=False)
```

---

## 2. Compute Service

Create `src/services/computed_features_service.py`:

```python
"""
Computed Features Service

Computes 40+ derived stock features from prices_daily.
Run daily after market close.

Features computed:
- 52-week stats (high, low, position, days since)
- Returns (1d, 1w, 1m, 3m, 6m, YTD, 1y)
- Moving averages (SMA 20/50/200, EMA 12/26)
- Trend signals (above SMA, golden/death cross)
- Momentum (RSI, ROC, MACD)
- Volatility (20d, 60d, ATR, max drawdown)
- Volume metrics (averages, relative volume, trend)
- Price action (gap, consecutive days)
"""

import math
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database.models import (
    PriceDaily,
    PriceTargetSummaryBulk,
    StockComputedFeatures,
)


class ComputedFeaturesService:
    """Compute and store derived stock features."""

    # Trading days per period
    TRADING_DAYS = {
        "1d": 1, "1w": 5, "1m": 21, "3m": 63,
        "6m": 126, "1y": 252, "52w": 252
    }

    def __init__(self, db: Session):
        self.db = db

    def compute_all(self, batch_size: int = 500) -> int:
        """
        Compute features for all symbols with price data.
        Processes in batches to manage memory.
        Returns count of symbols processed.
        """
        latest_date = self.db.query(func.max(PriceDaily.date)).scalar()
        if not latest_date:
            return 0

        symbols = [s[0] for s in self.db.query(PriceDaily.symbol).filter(
            PriceDaily.date == latest_date
        ).distinct().all()]

        count = 0
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            for symbol in batch:
                try:
                    self._compute_symbol(symbol, latest_date)
                    count += 1
                except Exception as e:
                    print(f"Error computing {symbol}: {e}")

            self.db.commit()
            print(f"Processed {min(i + batch_size, len(symbols))}/{len(symbols)} symbols")

        return count

    def _compute_symbol(self, symbol: str, latest_date: date):
        """Compute all features for a single symbol."""

        # Get price history (last 400 days for buffer)
        lookback = latest_date - timedelta(days=400)
        rows = self.db.query(
            PriceDaily.date,
            PriceDaily.open,
            PriceDaily.adj_close,
            PriceDaily.adj_high,
            PriceDaily.adj_low,
            PriceDaily.volume
        ).filter(
            PriceDaily.symbol == symbol,
            PriceDaily.date >= lookback
        ).order_by(PriceDaily.date.desc()).all()

        if len(rows) < 20:
            return

        # Convert to lists (most recent first)
        dates = [r.date for r in rows]
        opens = [float(r.open) if r.open else None for r in rows]
        closes = [float(r.adj_close) if r.adj_close else None for r in rows]
        highs = [float(r.adj_high) if r.adj_high else None for r in rows]
        lows = [float(r.adj_low) if r.adj_low else None for r in rows]
        volumes = [float(r.volume) if r.volume else 0 for r in rows]

        if closes[0] is None:
            return

        current_price = closes[0]

        # Build feature dict
        features = {
            "symbol": symbol,
            "compute_date": date.today(),
            "price_date": latest_date,
            "current_price": current_price,
        }

        # Compute all feature groups
        features.update(self._compute_52_week_stats(closes, highs, lows, dates, current_price))
        features.update(self._compute_returns(closes, dates, current_price, latest_date))
        features.update(self._compute_moving_averages(closes, current_price))
        features.update(self._compute_momentum(closes))
        features.update(self._compute_volatility(closes, highs, lows, current_price, dates, latest_date))
        features.update(self._compute_volume_metrics(closes, volumes, current_price))
        features.update(self._compute_price_action(opens, closes))
        features.update(self._compute_analyst_data(symbol, current_price))

        features["updated_at"] = datetime.utcnow()

        # Upsert
        self._upsert_features(features)

    # =========================================================================
    # 52-WEEK STATS
    # =========================================================================
    def _compute_52_week_stats(
        self, closes: List, highs: List, lows: List, dates: List, current_price: float
    ) -> Dict:
        high_52w, low_52w = None, None
        high_52w_date, low_52w_date = None, None
        high_52w_idx, low_52w_idx = 0, 0

        for i, (h, l, d) in enumerate(zip(highs[:252], lows[:252], dates[:252])):
            if h is not None:
                if high_52w is None or h > high_52w:
                    high_52w = h
                    high_52w_date = d
                    high_52w_idx = i
            if l is not None:
                if low_52w is None or l < low_52w:
                    low_52w = l
                    low_52w_date = d
                    low_52w_idx = i

        pct_from_high = ((current_price - high_52w) / high_52w * 100) if high_52w else None
        pct_from_low = ((current_price - low_52w) / low_52w * 100) if low_52w else None

        # Range position: 0 = at low, 100 = at high
        range_position = None
        if high_52w and low_52w and high_52w != low_52w:
            range_position = (current_price - low_52w) / (high_52w - low_52w) * 100

        return {
            "high_52w": high_52w,
            "low_52w": low_52w,
            "high_52w_date": high_52w_date,
            "low_52w_date": low_52w_date,
            "pct_from_high": pct_from_high,
            "pct_from_low": pct_from_low,
            "range_position_52w": range_position,
            "days_since_high_52w": high_52w_idx,
            "days_since_low_52w": low_52w_idx,
        }

    # =========================================================================
    # RETURNS
    # =========================================================================
    def _compute_returns(
        self, closes: List, dates: List, current_price: float, latest_date: date
    ) -> Dict:
        def calc_return(days: int) -> Optional[float]:
            if len(closes) > days and closes[days]:
                return (current_price - closes[days]) / closes[days] * 100
            return None

        # YTD
        year_start = date(latest_date.year, 1, 1)
        return_ytd = None
        for i, d in enumerate(dates):
            if d <= year_start and closes[i]:
                return_ytd = (current_price - closes[i]) / closes[i] * 100
                break

        return {
            "return_1d": calc_return(1),
            "return_1w": calc_return(5),
            "return_1m": calc_return(21),
            "return_3m": calc_return(63),
            "return_6m": calc_return(126),
            "return_1y": calc_return(252),
            "return_ytd": return_ytd,
        }

    # =========================================================================
    # MOVING AVERAGES
    # =========================================================================
    def _compute_moving_averages(self, closes: List, current_price: float) -> Dict:
        def sma(n: int) -> Optional[float]:
            valid = [c for c in closes[:n] if c is not None]
            return sum(valid) / len(valid) if len(valid) == n else None

        def ema(n: int) -> Optional[float]:
            valid = [c for c in closes[:n*2] if c is not None]  # Need more data for EMA
            if len(valid) < n:
                return None
            # Reverse to chronological order for EMA calculation
            valid = list(reversed(valid[:n*2]))
            multiplier = 2 / (n + 1)
            ema_val = sum(valid[:n]) / n  # Start with SMA
            for price in valid[n:]:
                ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
            return ema_val

        sma_20 = sma(20)
        sma_50 = sma(50)
        sma_200 = sma(200)
        ema_12 = ema(12)
        ema_26 = ema(26)

        return {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "ema_12": ema_12,
            "ema_26": ema_26,
            "price_vs_sma20": (current_price / sma_20 * 100) if sma_20 else None,
            "price_vs_sma50": (current_price / sma_50 * 100) if sma_50 else None,
            "price_vs_sma200": (current_price / sma_200 * 100) if sma_200 else None,
            "above_sma20": 1 if sma_20 and current_price > sma_20 else 0,
            "above_sma50": 1 if sma_50 and current_price > sma_50 else 0,
            "above_sma200": 1 if sma_200 and current_price > sma_200 else 0,
            "golden_cross": 1 if sma_50 and sma_200 and sma_50 > sma_200 else 0,
            "death_cross": 1 if sma_50 and sma_200 and sma_50 < sma_200 else 0,
        }

    # =========================================================================
    # MOMENTUM INDICATORS
    # =========================================================================
    def _compute_momentum(self, closes: List) -> Dict:
        # RSI 14
        rsi = self._calculate_rsi(closes, 14)

        # Rate of Change
        roc_10 = None
        roc_20 = None
        if len(closes) > 10 and closes[10]:
            roc_10 = (closes[0] - closes[10]) / closes[10] * 100
        if len(closes) > 20 and closes[20]:
            roc_20 = (closes[0] - closes[20]) / closes[20] * 100

        # MACD
        macd_line, macd_signal, macd_histogram = self._calculate_macd(closes)

        return {
            "rsi_14": rsi,
            "roc_10": roc_10,
            "roc_20": roc_20,
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "macd_histogram": macd_histogram,
        }

    def _calculate_rsi(self, closes: List, period: int = 14) -> Optional[float]:
        if len(closes) < period + 1:
            return None

        gains, losses = [], []
        for i in range(period):
            if closes[i] is None or closes[i + 1] is None:
                return None
            change = closes[i] - closes[i + 1]  # Most recent first
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, closes: List) -> tuple:
        """Calculate MACD line, signal, and histogram."""
        valid = [c for c in closes if c is not None]
        if len(valid) < 35:  # Need at least 26 + 9 for signal
            return None, None, None

        # Reverse for chronological calculation
        prices = list(reversed(valid[:60]))

        def ema_series(data: List, period: int) -> List:
            if len(data) < period:
                return []
            multiplier = 2 / (period + 1)
            ema_values = [sum(data[:period]) / period]
            for price in data[period:]:
                ema_values.append((price * multiplier) + (ema_values[-1] * (1 - multiplier)))
            return ema_values

        ema12 = ema_series(prices, 12)
        ema26 = ema_series(prices, 26)

        if not ema12 or not ema26:
            return None, None, None

        # Align lengths
        min_len = min(len(ema12), len(ema26))
        macd_values = [ema12[-(min_len - i)] - ema26[-(min_len - i)] for i in range(min_len)]

        if len(macd_values) < 9:
            return macd_values[-1] if macd_values else None, None, None

        signal_values = ema_series(macd_values, 9)

        macd_line = macd_values[-1]
        macd_signal = signal_values[-1] if signal_values else None
        macd_histogram = (macd_line - macd_signal) if macd_signal else None

        return macd_line, macd_signal, macd_histogram

    # =========================================================================
    # VOLATILITY
    # =========================================================================
    def _compute_volatility(
        self, closes: List, highs: List, lows: List, current_price: float,
        dates: List, latest_date: date
    ) -> Dict:
        # Historical volatility (annualized)
        vol_20 = self._calculate_volatility(closes, 20)
        vol_60 = self._calculate_volatility(closes, 60)

        # ATR 14
        atr = self._calculate_atr(highs, lows, closes, 14)
        atr_pct = (atr / current_price * 100) if atr and current_price else None

        # Max drawdown
        dd_ytd = self._calculate_max_drawdown(closes, dates, latest_date, ytd_only=True)
        dd_1y = self._calculate_max_drawdown(closes, dates, latest_date, ytd_only=False)

        return {
            "volatility_20d": vol_20,
            "volatility_60d": vol_60,
            "atr_14": atr,
            "atr_14_pct": atr_pct,
            "max_drawdown_ytd": dd_ytd,
            "max_drawdown_1y": dd_1y,
        }

    def _calculate_volatility(self, closes: List, period: int) -> Optional[float]:
        valid = [c for c in closes[:period + 1] if c is not None]
        if len(valid) < period + 1:
            return None

        returns = []
        for i in range(period):
            if valid[i + 1] != 0:
                returns.append(math.log(valid[i] / valid[i + 1]))

        if len(returns) < period:
            return None

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        daily_vol = math.sqrt(variance)

        # Annualize (252 trading days)
        return daily_vol * math.sqrt(252) * 100

    def _calculate_atr(self, highs: List, lows: List, closes: List, period: int) -> Optional[float]:
        if len(closes) < period + 1:
            return None

        true_ranges = []
        for i in range(period):
            if highs[i] is None or lows[i] is None or closes[i + 1] is None:
                continue
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i + 1]),
                abs(lows[i] - closes[i + 1])
            )
            true_ranges.append(tr)

        return sum(true_ranges) / len(true_ranges) if true_ranges else None

    def _calculate_max_drawdown(
        self, closes: List, dates: List, latest_date: date, ytd_only: bool
    ) -> Optional[float]:
        # Determine range
        if ytd_only:
            year_start = date(latest_date.year, 1, 1)
            valid_closes = []
            for c, d in zip(closes, dates):
                if d >= year_start and c is not None:
                    valid_closes.append(c)
        else:
            valid_closes = [c for c in closes[:252] if c is not None]

        if len(valid_closes) < 2:
            return None

        # Reverse to chronological order
        prices = list(reversed(valid_closes))

        peak = prices[0]
        max_dd = 0
        for price in prices:
            if price > peak:
                peak = price
            dd = (peak - price) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return -max_dd  # Negative to indicate loss

    # =========================================================================
    # VOLUME METRICS
    # =========================================================================
    def _compute_volume_metrics(
        self, closes: List, volumes: List, current_price: float
    ) -> Dict:
        vol_20 = [v for v in volumes[:20] if v > 0]
        vol_50 = [v for v in volumes[:50] if v > 0]
        vol_5 = [v for v in volumes[:5] if v > 0]

        avg_20 = sum(vol_20) / len(vol_20) if vol_20 else None
        avg_50 = sum(vol_50) / len(vol_50) if vol_50 else None
        avg_5 = sum(vol_5) / len(vol_5) if vol_5 else None

        current_vol = volumes[0] if volumes else 0
        relative_vol = (current_vol / avg_20) if avg_20 and avg_20 > 0 else None

        # Dollar volume
        dollar_vol_data = [(c * v) for c, v in zip(closes[:20], volumes[:20]) if c and v]
        avg_dollar_vol = sum(dollar_vol_data) / len(dollar_vol_data) if dollar_vol_data else None

        # Volume trend: 5d avg / 20d avg
        vol_trend = (avg_5 / avg_20) if avg_5 and avg_20 and avg_20 > 0 else None

        return {
            "avg_volume_20d": avg_20,
            "avg_volume_50d": avg_50,
            "relative_volume": relative_vol,
            "avg_dollar_volume_20d": avg_dollar_vol,
            "volume_trend": vol_trend,
        }

    # =========================================================================
    # PRICE ACTION
    # =========================================================================
    def _compute_price_action(self, opens: List, closes: List) -> Dict:
        # Gap %
        gap_pct = None
        if len(opens) > 0 and len(closes) > 1 and opens[0] and closes[1]:
            gap_pct = (opens[0] - closes[1]) / closes[1] * 100

        # Consecutive up/down days
        consecutive = 0
        if len(closes) > 1:
            direction = 1 if closes[0] > closes[1] else -1
            consecutive = direction
            for i in range(1, min(len(closes) - 1, 20)):
                if closes[i] is None or closes[i + 1] is None:
                    break
                if direction == 1 and closes[i] > closes[i + 1]:
                    consecutive += 1
                elif direction == -1 and closes[i] < closes[i + 1]:
                    consecutive -= 1
                else:
                    break

        return {
            "gap_pct": gap_pct,
            "consecutive_up_days": consecutive,
        }

    # =========================================================================
    # ANALYST DATA
    # =========================================================================
    def _compute_analyst_data(self, symbol: str, current_price: float) -> Dict:
        target = self.db.query(PriceTargetSummaryBulk).filter(
            PriceTargetSummaryBulk.symbol == symbol
        ).first()

        consensus = None
        upside = None
        if target and target.last_month_avg_price_target:
            consensus = float(target.last_month_avg_price_target)
            upside = (consensus - current_price) / current_price * 100

        return {
            "price_target_consensus": consensus,
            "price_target_upside": upside,
        }

    # =========================================================================
    # DATABASE OPERATIONS
    # =========================================================================
    def _upsert_features(self, features: Dict):
        """Insert or update features for a symbol."""
        existing = self.db.query(StockComputedFeatures).filter(
            StockComputedFeatures.symbol == features["symbol"]
        ).first()

        if existing:
            for key, value in features.items():
                setattr(existing, key, value)
        else:
            record = StockComputedFeatures(**features)
            self.db.add(record)
```

---

## 3. Daily Job Script

Create `src/jobs/compute_features_job.py`:

```python
"""
Daily job to compute stock features.
Run after EOD price updates complete.

Usage:
    python -m src.jobs.compute_features_job
"""

import logging
import time
from datetime import datetime

from ..database.session import SessionLocal
from ..services.computed_features_service import ComputedFeaturesService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    start_time = time.time()
    logger.info("Starting computed features job")

    db = SessionLocal()
    try:
        service = ComputedFeaturesService(db)
        count = service.compute_all(batch_size=500)

        elapsed = time.time() - start_time
        logger.info(f"Computed features for {count} symbols in {elapsed:.1f}s")
        logger.info(f"Average: {elapsed/count*1000:.1f}ms per symbol" if count > 0 else "")

    except Exception as e:
        logger.error(f"Job failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

### Schedule with Task Scheduler / Cron

**Windows Task Scheduler:**
- Run after EOD price collection (e.g., 6:30 PM ET)
- Command: `python -m src.jobs.compute_features_job`

**Linux Cron:**
```cron
30 18 * * 1-5 cd /path/to/data-project && python -m src.jobs.compute_features_job
```

---

## 4. Feature Summary

| Category | Count | Features |
|----------|-------|----------|
| **52-Week Stats** | 9 | high_52w, low_52w, dates, pct_from_high/low, range_position, days_since |
| **Returns** | 7 | 1d, 1w, 1m, 3m, 6m, YTD, 1y |
| **Moving Averages** | 10 | SMA 20/50/200, EMA 12/26, price_vs_sma, above_sma, golden/death cross |
| **Momentum** | 6 | RSI 14, ROC 10/20, MACD line/signal/histogram |
| **Volatility** | 6 | vol 20d/60d, ATR 14, ATR %, max drawdown YTD/1Y |
| **Volume** | 5 | avg 20d/50d, relative, dollar volume, trend |
| **Price Action** | 2 | gap %, consecutive days |
| **Analyst** | 2 | price target, upside % |
| **Total** | **47** | |

---

## 5. Finexus Integration

After the table is populated in DATA project, update Finexus to use it.

### Add Model to data_models

In `backend/app/data_models/models.py`, copy the SQLAlchemy model above.

### Update Feature Registry

In `backend/app/services/stocks/feature_registry.py`, add all computed features:

```python
# 52-Week Stats
"high_52w": {"name": "52-Week High", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},
"low_52w": {"name": "52-Week Low", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},
"pct_from_high": {"name": "% From 52W High", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},
"pct_from_low": {"name": "% From 52W Low", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},
"range_position_52w": {"name": "52W Range Position", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},
"days_since_high_52w": {"name": "Days Since 52W High", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},
"days_since_low_52w": {"name": "Days Since 52W Low", "category": "price_computed", "source_table": "stock_computed_features", "data_type": "number"},

# Moving Averages
"sma_20": {"name": "SMA 20", "category": "technicals", "source_table": "stock_computed_features", "data_type": "number"},
"sma_50": {"name": "SMA 50", "category": "technicals", "source_table": "stock_computed_features", "data_type": "number"},
"sma_200": {"name": "SMA 200", "category": "technicals", "source_table": "stock_computed_features", "data_type": "number"},
"price_vs_sma50": {"name": "Price/SMA50 %", "category": "technicals", "source_table": "stock_computed_features", "data_type": "number"},
"price_vs_sma200": {"name": "Price/SMA200 %", "category": "technicals", "source_table": "stock_computed_features", "data_type": "number"},
"above_sma50": {"name": "Above SMA50", "category": "technicals", "source_table": "stock_computed_features", "data_type": "boolean"},
"above_sma200": {"name": "Above SMA200", "category": "technicals", "source_table": "stock_computed_features", "data_type": "boolean"},
"golden_cross": {"name": "Golden Cross", "category": "technicals", "source_table": "stock_computed_features", "data_type": "boolean"},

# Momentum
"rsi_14": {"name": "RSI (14)", "category": "momentum", "source_table": "stock_computed_features", "data_type": "number"},
"macd_line": {"name": "MACD", "category": "momentum", "source_table": "stock_computed_features", "data_type": "number"},
"macd_histogram": {"name": "MACD Histogram", "category": "momentum", "source_table": "stock_computed_features", "data_type": "number"},

# Volatility
"volatility_20d": {"name": "Volatility 20D", "category": "risk", "source_table": "stock_computed_features", "data_type": "number"},
"volatility_60d": {"name": "Volatility 60D", "category": "risk", "source_table": "stock_computed_features", "data_type": "number"},
"atr_14_pct": {"name": "ATR %", "category": "risk", "source_table": "stock_computed_features", "data_type": "number"},
"max_drawdown_1y": {"name": "Max Drawdown 1Y", "category": "risk", "source_table": "stock_computed_features", "data_type": "number"},

# Volume
"relative_volume": {"name": "Relative Volume", "category": "volume", "source_table": "stock_computed_features", "data_type": "number"},
"avg_dollar_volume_20d": {"name": "Avg $ Volume 20D", "category": "volume", "source_table": "stock_computed_features", "data_type": "number"},
"volume_trend": {"name": "Volume Trend", "category": "volume", "source_table": "stock_computed_features", "data_type": "number"},
```

### Update Screener Service

In `screener_service.py`, add the table join:

```python
from ..data_models import StockComputedFeatures

# In _build_base_query:
if "stock_computed_features" in required_tables:
    query = query.outerjoin(
        StockComputedFeatures,
        NasdaqScreenerProfile.symbol == StockComputedFeatures.symbol
    )
```

---

## 6. Summary Checklist

- [ ] Create `stock_computed_features` table in DATA database
- [ ] Add SQLAlchemy model to DATA project
- [ ] Create compute service with all 47 features
- [ ] Create daily job script
- [ ] Test locally with a few symbols
- [ ] Schedule job to run after EOD price updates
- [ ] Run full job and verify data
- [ ] Add model to Finexus data_models
- [ ] Update Finexus feature registry
- [ ] Update Finexus screener service with join
- [ ] Add features to Screener.tsx UI
- [ ] Test screening with computed features
