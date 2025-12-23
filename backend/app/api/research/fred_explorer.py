"""
FRED Explorer API - Treasury Yield Curve and related data.

Provides endpoints for analyzing Treasury yield curve data from FRED/ALFRED.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_data_db
from backend.app.data_models import (
    FredSeries, FredObservationLatest, FredObservationRealtime
)
from backend.app.core.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/research/fred", tags=["FRED Research"])

# Treasury yield curve series (nominal yields)
YIELD_CURVE_SERIES = {
    "1M": "DGS1MO",
    "3M": "DGS3MO",
    "6M": "DGS6MO",
    "1Y": "DGS1",
    "2Y": "DGS2",
    "3Y": "DGS3",
    "5Y": "DGS5",
    "7Y": "DGS7",
    "10Y": "DGS10",
    "20Y": "DGS20",
    "30Y": "DGS30",
}

# TIPS real yields
TIPS_SERIES = {
    "5Y": "DFII5",
    "7Y": "DFII7",
    "10Y": "DFII10",
    "20Y": "DFII20",
    "30Y": "DFII30",
}

# Breakeven inflation rates
BREAKEVEN_SERIES = {
    "5Y": "T5YIE",
    "10Y": "T10YIE",
}


def get_latest_values(
    db: Session,
    series_ids: List[str],
    prefer_alfred: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """
    Get the most recent values for a list of series.
    Returns dict mapping series_id to {date, value, source}.
    """
    results = {}

    for series_id in series_ids:
        # Try ALFRED first (get the most recent observation)
        if prefer_alfred:
            alfred_obs = db.query(FredObservationRealtime).filter(
                FredObservationRealtime.series_id == series_id
            ).order_by(
                desc(FredObservationRealtime.date)
            ).first()

            if alfred_obs:
                results[series_id] = {
                    "date": alfred_obs.date.isoformat() if alfred_obs.date else None,
                    "value": alfred_obs.value,
                    "source": "alfred",
                }
                continue

        # Fall back to Latest
        latest_obs = db.query(FredObservationLatest).filter(
            FredObservationLatest.series_id == series_id
        ).order_by(
            desc(FredObservationLatest.date)
        ).first()

        if latest_obs:
            results[series_id] = {
                "date": latest_obs.date.isoformat() if latest_obs.date else None,
                "value": latest_obs.value,
                "source": "latest",
            }
        else:
            results[series_id] = None

    return results


def get_historical_values(
    db: Session,
    series_id: str,
    as_of_date: date,
    prefer_alfred: bool = True,
) -> Optional[float]:
    """
    Get the value of a series as of a specific date.
    """
    if prefer_alfred:
        obs = db.query(FredObservationRealtime).filter(
            FredObservationRealtime.series_id == series_id,
            FredObservationRealtime.date <= as_of_date,
        ).order_by(
            desc(FredObservationRealtime.date)
        ).first()

        if obs:
            return obs.value

    # Fall back to Latest
    obs = db.query(FredObservationLatest).filter(
        FredObservationLatest.series_id == series_id,
        FredObservationLatest.date <= as_of_date,
    ).order_by(
        desc(FredObservationLatest.date)
    ).first()

    return obs.value if obs else None


@router.get("/yield-curve")
async def get_yield_curve(
    as_of_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, defaults to latest"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the Treasury yield curve data.

    Returns current yields for all maturities, plus daily/weekly/monthly changes.
    """
    today = date.today()

    # Parse as_of_date if provided
    if as_of_date:
        try:
            target_date = datetime.strptime(as_of_date, "%Y-%m-%d").date()
        except ValueError:
            target_date = today
    else:
        target_date = today

    # Calculate comparison dates
    day_ago = target_date - timedelta(days=1)
    week_ago = target_date - timedelta(days=7)
    month_ago = target_date - timedelta(days=30)

    # Get yield curve data
    curve_data = []
    series_ids = list(YIELD_CURVE_SERIES.values())

    # Get latest values
    latest_values = get_latest_values(db, series_ids)

    # Track the actual data date
    data_date = None

    for tenor, series_id in YIELD_CURVE_SERIES.items():
        current = latest_values.get(series_id)

        if current and current.get("value") is not None:
            current_value = current["value"]
            current_date = current["date"]

            if data_date is None and current_date:
                data_date = current_date

            # Get historical values for changes
            day_ago_val = get_historical_values(db, series_id, day_ago)
            week_ago_val = get_historical_values(db, series_id, week_ago)
            month_ago_val = get_historical_values(db, series_id, month_ago)

            # Calculate changes in basis points (1 bp = 0.01%)
            daily_change = round((current_value - day_ago_val) * 100, 1) if day_ago_val else None
            weekly_change = round((current_value - week_ago_val) * 100, 1) if week_ago_val else None
            monthly_change = round((current_value - month_ago_val) * 100, 1) if month_ago_val else None

            curve_data.append({
                "tenor": tenor,
                "series_id": series_id,
                "yield": round(current_value, 3),
                "date": current_date,
                "source": current["source"],
                "daily_change_bps": daily_change,
                "weekly_change_bps": weekly_change,
                "monthly_change_bps": monthly_change,
            })
        else:
            curve_data.append({
                "tenor": tenor,
                "series_id": series_id,
                "yield": None,
                "date": None,
                "source": None,
                "daily_change_bps": None,
                "weekly_change_bps": None,
                "monthly_change_bps": None,
            })

    # Calculate spreads
    spreads = {}
    yields_by_tenor = {d["tenor"]: d["yield"] for d in curve_data if d["yield"] is not None}

    if "2Y" in yields_by_tenor and "10Y" in yields_by_tenor:
        spreads["2s10s"] = round((yields_by_tenor["10Y"] - yields_by_tenor["2Y"]) * 100, 1)
    if "2Y" in yields_by_tenor and "30Y" in yields_by_tenor:
        spreads["2s30s"] = round((yields_by_tenor["30Y"] - yields_by_tenor["2Y"]) * 100, 1)
    if "5Y" in yields_by_tenor and "30Y" in yields_by_tenor:
        spreads["5s30s"] = round((yields_by_tenor["30Y"] - yields_by_tenor["5Y"]) * 100, 1)
    if "3M" in yields_by_tenor and "10Y" in yields_by_tenor:
        spreads["3m10y"] = round((yields_by_tenor["10Y"] - yields_by_tenor["3M"]) * 100, 1)

    # Get TIPS real yields
    tips_data = []
    tips_values = get_latest_values(db, list(TIPS_SERIES.values()))

    for tenor, series_id in TIPS_SERIES.items():
        val = tips_values.get(series_id)
        if val and val.get("value") is not None:
            tips_data.append({
                "tenor": tenor,
                "series_id": series_id,
                "real_yield": round(val["value"], 3),
                "date": val["date"],
            })

    # Get breakeven inflation
    breakeven_data = []
    breakeven_values = get_latest_values(db, list(BREAKEVEN_SERIES.values()))

    for tenor, series_id in BREAKEVEN_SERIES.items():
        val = breakeven_values.get(series_id)
        if val and val.get("value") is not None:
            breakeven_data.append({
                "tenor": tenor,
                "series_id": series_id,
                "breakeven": round(val["value"], 3),
                "date": val["date"],
            })

    return {
        "as_of_date": data_date or target_date.isoformat(),
        "curve": curve_data,
        "spreads": spreads,
        "tips_real_yields": tips_data,
        "breakeven_inflation": breakeven_data,
    }


@router.get("/yield-curve/history")
async def get_yield_curve_history(
    tenor: str = Query("10Y", description="Tenor to get history for"),
    days: int = Query(365, ge=1, le=3650, description="Number of days of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical yield data for a specific tenor.
    """
    series_id = YIELD_CURVE_SERIES.get(tenor)
    if not series_id:
        return {"error": f"Invalid tenor: {tenor}"}

    start_date = date.today() - timedelta(days=days)

    # Try ALFRED first
    obs = db.query(FredObservationRealtime).filter(
        FredObservationRealtime.series_id == series_id,
        FredObservationRealtime.date >= start_date,
    ).order_by(FredObservationRealtime.date).all()

    source = "alfred"

    if not obs:
        # Fall back to Latest
        obs = db.query(FredObservationLatest).filter(
            FredObservationLatest.series_id == series_id,
            FredObservationLatest.date >= start_date,
        ).order_by(FredObservationLatest.date).all()
        source = "latest"

    return {
        "tenor": tenor,
        "series_id": series_id,
        "source": source,
        "data": [
            {"date": o.date.isoformat(), "value": o.value}
            for o in obs
        ],
    }


@router.get("/yield-curve/spread-history")
async def get_spread_history(
    spread: str = Query("2s10s", description="Spread to get history for (2s10s, 2s30s, 5s30s, 3m10y)"),
    days: int = Query(365, ge=1, le=3650, description="Number of days of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical spread data, calculated from underlying yields.
    """
    spread_configs = {
        "2s10s": ("DGS2", "DGS10"),
        "2s30s": ("DGS2", "DGS30"),
        "5s30s": ("DGS5", "DGS30"),
        "3m10y": ("DGS3MO", "DGS10"),
    }

    if spread not in spread_configs:
        return {"error": f"Invalid spread: {spread}"}

    short_series, long_series = spread_configs[spread]
    start_date = date.today() - timedelta(days=days)

    # Get data for both series
    def get_series_data(series_id: str):
        obs = db.query(FredObservationRealtime).filter(
            FredObservationRealtime.series_id == series_id,
            FredObservationRealtime.date >= start_date,
        ).order_by(FredObservationRealtime.date).all()

        if not obs:
            obs = db.query(FredObservationLatest).filter(
                FredObservationLatest.series_id == series_id,
                FredObservationLatest.date >= start_date,
            ).order_by(FredObservationLatest.date).all()

        return {o.date: o.value for o in obs}

    short_data = get_series_data(short_series)
    long_data = get_series_data(long_series)

    # Calculate spread for dates where both exist
    spread_data = []
    for dt in sorted(set(short_data.keys()) & set(long_data.keys())):
        spread_value = round((long_data[dt] - short_data[dt]) * 100, 1)  # in bps
        spread_data.append({
            "date": dt.isoformat(),
            "value": spread_value,
        })

    return {
        "spread": spread,
        "short_tenor": short_series,
        "long_tenor": long_series,
        "unit": "bps",
        "data": spread_data,
    }
