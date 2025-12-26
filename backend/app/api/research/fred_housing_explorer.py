"""
FRED Housing Market Explorer API

Provides endpoints for analyzing housing market data:
- HOUST: Housing Starts Total
- HOUST1F: Single Family Housing Starts
- HOUST5F: 5+ Units Housing Starts
- PERMIT: Building Permits Total
- PERMIT1: Single Family Building Permits
- Related mortgage rates and regional data
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

router = APIRouter(prefix="/api/research/fred/housing", tags=["FRED Housing"])

# Housing series definitions
HOUSING_SERIES = {
    # Housing Starts
    "HOUST": {
        "name": "Housing Starts",
        "description": "Total Housing Starts",
        "frequency": "Monthly",
        "unit": "Thousands of Units (SAAR)",
        "category": "starts",
    },
    "HOUST1F": {
        "name": "Single Family Starts",
        "description": "Privately Owned Housing Starts: 1-Unit Structures",
        "frequency": "Monthly",
        "unit": "Thousands of Units (SAAR)",
        "category": "starts",
    },
    "HOUST5F": {
        "name": "5+ Unit Starts",
        "description": "Privately Owned Housing Starts: 5+ Unit Structures",
        "frequency": "Monthly",
        "unit": "Thousands of Units (SAAR)",
        "category": "starts",
    },
    # Building Permits
    "PERMIT": {
        "name": "Building Permits",
        "description": "Total New Private Housing Units Authorized",
        "frequency": "Monthly",
        "unit": "Thousands of Units (SAAR)",
        "category": "permits",
    },
    "PERMIT1": {
        "name": "Single Family Permits",
        "description": "New Private Housing Units Authorized: 1-Unit Structures",
        "frequency": "Monthly",
        "unit": "Thousands of Units (SAAR)",
        "category": "permits",
    },
    # Completions
    "COMPUTSA": {
        "name": "Housing Completions",
        "description": "Total Housing Completions",
        "frequency": "Monthly",
        "unit": "Thousands of Units (SAAR)",
        "category": "completions",
    },
    # Under Construction
    "UNDCONTSA": {
        "name": "Under Construction",
        "description": "Total Housing Units Under Construction",
        "frequency": "Monthly",
        "unit": "Thousands of Units",
        "category": "construction",
    },
}

# Mortgage rate series for context
MORTGAGE_SERIES = {
    "MORTGAGE30US": {
        "name": "30-Year Fixed",
        "description": "30-Year Fixed Rate Mortgage Average",
        "frequency": "Weekly",
        "unit": "Percent",
    },
    "MORTGAGE15US": {
        "name": "15-Year Fixed",
        "description": "15-Year Fixed Rate Mortgage Average",
        "frequency": "Weekly",
        "unit": "Percent",
    },
}

# Regional housing starts
REGIONAL_SERIES = {
    "HOUSTNE": "Northeast",
    "HOUSTMW": "Midwest",
    "HOUSTS": "South",
    "HOUSTW": "West",
}


def get_series_history(
    db: Session,
    series_id: str,
    months_back: int = 60,
    prefer_alfred: bool = True,
) -> List[Dict[str, Any]]:
    """Get historical observations for a series."""
    start_date = date.today() - timedelta(days=months_back * 30)

    if prefer_alfred:
        obs = db.query(FredObservationRealtime).filter(
            FredObservationRealtime.series_id == series_id,
            FredObservationRealtime.date >= start_date,
        ).order_by(FredObservationRealtime.date).all()

        if obs:
            return [
                {"date": o.date.isoformat(), "value": o.value}
                for o in obs if o.value is not None
            ]

    obs = db.query(FredObservationLatest).filter(
        FredObservationLatest.series_id == series_id,
        FredObservationLatest.date >= start_date,
    ).order_by(FredObservationLatest.date).all()

    return [
        {"date": o.date.isoformat(), "value": o.value}
        for o in obs if o.value is not None
    ]


def get_latest_with_changes(
    db: Session,
    series_id: str,
    prefer_alfred: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get latest value with month-over-month and year-over-year changes."""
    history = get_series_history(db, series_id, months_back=24, prefer_alfred=prefer_alfred)

    if not history:
        return None

    latest = history[-1]
    latest_value = latest["value"]
    latest_date = latest["date"]

    # MoM change
    mom_change = None
    mom_pct = None
    prior_value = None
    if len(history) >= 2:
        prior_value = history[-2]["value"]
        if prior_value and prior_value != 0:
            mom_change = latest_value - prior_value
            mom_pct = round((mom_change / prior_value) * 100, 2)

    # YoY change
    yoy_change = None
    yoy_pct = None
    year_ago_value = None
    if len(history) >= 12:
        target_date = date.fromisoformat(latest_date) - timedelta(days=365)
        for obs in reversed(history[:-1]):
            obs_date = date.fromisoformat(obs["date"])
            if obs_date <= target_date:
                year_ago_value = obs["value"]
                break

        if year_ago_value and year_ago_value != 0:
            yoy_change = latest_value - year_ago_value
            yoy_pct = round((yoy_change / year_ago_value) * 100, 2)

    return {
        "value": latest_value,
        "date": latest_date,
        "prior_value": prior_value,
        "mom_change": mom_change,
        "mom_pct": mom_pct,
        "year_ago_value": year_ago_value,
        "yoy_change": yoy_change,
        "yoy_pct": yoy_pct,
    }


def classify_housing_level(value: float, metric: str) -> str:
    """Classify housing activity level based on historical norms."""
    # These thresholds are based on historical averages
    thresholds = {
        "starts": {"low": 1000, "normal": 1300, "high": 1600},
        "permits": {"low": 1000, "normal": 1300, "high": 1600},
    }

    t = thresholds.get(metric, thresholds["starts"])

    if value < t["low"]:
        return "weak"
    elif value < t["normal"]:
        return "below_average"
    elif value < t["high"]:
        return "normal"
    else:
        return "strong"


@router.get("/overview")
async def get_housing_overview(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview of housing market data.

    Returns housing starts, permits, and mortgage rates with trends.
    """
    # Get latest values for main series
    starts = get_latest_with_changes(db, "HOUST")
    starts_1f = get_latest_with_changes(db, "HOUST1F")
    starts_5f = get_latest_with_changes(db, "HOUST5F")
    permits = get_latest_with_changes(db, "PERMIT")
    permits_1f = get_latest_with_changes(db, "PERMIT1")
    completions = get_latest_with_changes(db, "COMPUTSA")
    under_construction = get_latest_with_changes(db, "UNDCONTSA")

    # Get mortgage rates
    mortgage_30 = get_latest_with_changes(db, "MORTGAGE30US")
    mortgage_15 = get_latest_with_changes(db, "MORTGAGE15US")

    # Get regional data
    regional = {}
    for series_id, region_name in REGIONAL_SERIES.items():
        data = get_latest_with_changes(db, series_id)
        if data:
            regional[region_name.lower()] = {
                "series_id": series_id,
                "name": region_name,
                **data,
            }

    # Calculate single family share
    sf_share = None
    if starts and starts_1f and starts.get("value") and starts_1f.get("value"):
        sf_share = round((starts_1f["value"] / starts["value"]) * 100, 1)

    # Activity level assessment
    activity_level = None
    if starts and starts.get("value"):
        activity_level = classify_housing_level(starts["value"], "starts")

    # Get metadata
    houst_meta = db.query(FredSeries).filter(FredSeries.series_id == "HOUST").first()

    return {
        "as_of": datetime.now().isoformat(),
        "housing_starts": {
            "total": starts,
            "single_family": starts_1f,
            "multi_family": starts_5f,
            "single_family_share": sf_share,
            "activity_level": activity_level,
        },
        "building_permits": {
            "total": permits,
            "single_family": permits_1f,
        },
        "pipeline": {
            "completions": completions,
            "under_construction": under_construction,
        },
        "mortgage_rates": {
            "rate_30y": mortgage_30,
            "rate_15y": mortgage_15,
            "spread": round(mortgage_30["value"] - mortgage_15["value"], 2) if mortgage_30 and mortgage_15 and mortgage_30.get("value") and mortgage_15.get("value") else None,
        },
        "regional": regional,
        "series_info": {
            "last_updated": houst_meta.last_updated.isoformat() if houst_meta and houst_meta.last_updated else None,
        }
    }


@router.get("/timeline")
async def get_housing_timeline(
    months_back: int = Query(60, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical timeline for housing starts and permits.
    """
    starts_history = get_series_history(db, "HOUST", months_back=months_back)
    permits_history = get_series_history(db, "PERMIT", months_back=months_back)
    starts_1f_history = get_series_history(db, "HOUST1F", months_back=months_back)
    starts_5f_history = get_series_history(db, "HOUST5F", months_back=months_back)

    # Build unified timeline
    all_dates = set()
    for series in [starts_history, permits_history, starts_1f_history, starts_5f_history]:
        for obs in series:
            all_dates.add(obs["date"])

    starts_lookup = {obs["date"]: obs["value"] for obs in starts_history}
    permits_lookup = {obs["date"]: obs["value"] for obs in permits_history}
    starts_1f_lookup = {obs["date"]: obs["value"] for obs in starts_1f_history}
    starts_5f_lookup = {obs["date"]: obs["value"] for obs in starts_5f_history}

    timeline = []
    for dt in sorted(all_dates):
        timeline.append({
            "date": dt,
            "starts": starts_lookup.get(dt),
            "permits": permits_lookup.get(dt),
            "starts_1f": starts_1f_lookup.get(dt),
            "starts_5f": starts_5f_lookup.get(dt),
        })

    return {
        "months_back": months_back,
        "data_points": len(timeline),
        "timeline": timeline,
    }


@router.get("/mortgage-rates")
async def get_mortgage_rates(
    months_back: int = Query(60, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical mortgage rate data.
    """
    rate_30_history = get_series_history(db, "MORTGAGE30US", months_back=months_back)
    rate_15_history = get_series_history(db, "MORTGAGE15US", months_back=months_back)

    rate_30_lookup = {obs["date"]: obs["value"] for obs in rate_30_history}
    rate_15_lookup = {obs["date"]: obs["value"] for obs in rate_15_history}

    all_dates = set(rate_30_lookup.keys()) | set(rate_15_lookup.keys())

    timeline = []
    for dt in sorted(all_dates):
        r30 = rate_30_lookup.get(dt)
        r15 = rate_15_lookup.get(dt)
        timeline.append({
            "date": dt,
            "rate_30y": r30,
            "rate_15y": r15,
            "spread": round(r30 - r15, 2) if r30 and r15 else None,
        })

    # Calculate stats
    values_30 = [obs["value"] for obs in rate_30_history if obs["value"]]
    stats = {}
    if values_30:
        stats = {
            "current": values_30[-1] if values_30 else None,
            "avg": round(sum(values_30) / len(values_30), 2),
            "min": min(values_30),
            "max": max(values_30),
        }

    return {
        "months_back": months_back,
        "data_points": len(timeline),
        "statistics": stats,
        "timeline": timeline,
    }


@router.get("/regional")
async def get_regional_breakdown(
    months_back: int = Query(60, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get regional housing starts breakdown.
    """
    regional_data = {}

    for series_id, region_name in REGIONAL_SERIES.items():
        history = get_series_history(db, series_id, months_back=months_back)
        latest = get_latest_with_changes(db, series_id)

        regional_data[region_name.lower()] = {
            "series_id": series_id,
            "name": region_name,
            "latest": latest,
            "history": history,
        }

    # Calculate regional shares
    shares = {}
    total = 0
    for region, data in regional_data.items():
        if data["latest"] and data["latest"].get("value"):
            total += data["latest"]["value"]

    if total > 0:
        for region, data in regional_data.items():
            if data["latest"] and data["latest"].get("value"):
                shares[region] = round((data["latest"]["value"] / total) * 100, 1)

    return {
        "months_back": months_back,
        "regional_shares": shares,
        "regions": regional_data,
    }


@router.get("/compare-starts-permits")
async def compare_starts_permits(
    months_back: int = Query(120, ge=12, le=600, description="Months for comparison"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare housing starts to permits.

    Permits typically lead starts by 1-2 months as a forward indicator.
    """
    starts_history = get_series_history(db, "HOUST", months_back=months_back)
    permits_history = get_series_history(db, "PERMIT", months_back=months_back)

    starts_lookup = {obs["date"]: obs["value"] for obs in starts_history}
    permits_lookup = {obs["date"]: obs["value"] for obs in permits_history}

    common_dates = set(starts_lookup.keys()) & set(permits_lookup.keys())

    comparison = []
    gaps = []

    for dt in sorted(common_dates):
        starts_val = starts_lookup[dt]
        permits_val = permits_lookup[dt]
        gap = permits_val - starts_val

        comparison.append({
            "date": dt,
            "starts": starts_val,
            "permits": permits_val,
            "gap": round(gap, 1),
            "ratio": round(permits_val / starts_val, 3) if starts_val > 0 else None,
        })
        gaps.append(gap)

    # Stats
    gap_stats = {}
    if gaps:
        gap_stats = {
            "current_gap": gaps[-1] if gaps else None,
            "avg_gap": round(sum(gaps) / len(gaps), 1),
            "positive_gap_indicates": "permits exceeding starts (building backlog)",
        }

    return {
        "months_back": months_back,
        "data_points": len(comparison),
        "gap_stats": gap_stats,
        "comparison": comparison,
    }


@router.get("/series/{series_id}")
async def get_series_detail(
    series_id: str,
    months_back: int = Query(60, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed data for a specific housing series."""
    series_id_upper = series_id.upper()

    all_series = {**HOUSING_SERIES, **MORTGAGE_SERIES}
    if series_id_upper not in all_series:
        return {"error": f"Unknown series: {series_id}. Valid: {list(all_series.keys())}"}

    info = all_series[series_id_upper]

    # Get series metadata
    series_meta = db.query(FredSeries).filter(
        FredSeries.series_id == series_id_upper
    ).first()

    # Get latest with changes
    latest = get_latest_with_changes(db, series_id_upper)

    # Get history
    history = get_series_history(db, series_id_upper, months_back=months_back)

    # Calculate statistics
    values = [obs["value"] for obs in history if obs["value"] is not None]
    stats = {}
    if values:
        stats = {
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 1),
            "current": latest.get("value") if latest else None,
        }

    return {
        "series_id": series_id_upper,
        "name": info["name"],
        "description": info["description"],
        "frequency": info.get("frequency"),
        "unit": info.get("unit"),
        "category": info.get("category"),
        "title": series_meta.title if series_meta else None,
        "notes": series_meta.notes if series_meta else None,
        "observation_start": series_meta.observation_start.isoformat() if series_meta and series_meta.observation_start else None,
        "observation_end": series_meta.observation_end.isoformat() if series_meta and series_meta.observation_end else None,
        "last_updated": series_meta.last_updated.isoformat() if series_meta and series_meta.last_updated else None,
        "latest": latest,
        "statistics": stats,
        "history": history,
    }
