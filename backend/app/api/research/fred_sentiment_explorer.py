"""
FRED Consumer Sentiment Explorer API

Provides endpoints for analyzing consumer sentiment data:
- UMCSENT: University of Michigan Consumer Sentiment Index
- UMCSENT1: Consumer Sentiment - Current Conditions
- UMCSENT5: Consumer Sentiment - Expectations
- MICH: University of Michigan Inflation Expectations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from backend.app.database import get_data_db
from backend.app.data_models import (
    FredSeries, FredObservationLatest, FredObservationRealtime
)
from backend.app.core.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/research/fred/sentiment", tags=["FRED Consumer Sentiment"])

# Consumer Sentiment series definitions
SENTIMENT_SERIES = {
    "UMCSENT": {
        "name": "Consumer Sentiment",
        "description": "University of Michigan: Consumer Sentiment Index",
        "frequency": "Monthly",
        "unit": "Index 1966:Q1=100",
        "category": "headline",
    },
    "UMCSENT1": {
        "name": "Current Conditions",
        "description": "University of Michigan: Consumer Sentiment - Current Conditions",
        "frequency": "Monthly",
        "unit": "Index 1966:Q1=100",
        "category": "component",
    },
    "UMCSENT5": {
        "name": "Expectations",
        "description": "University of Michigan: Consumer Sentiment - Expectations",
        "frequency": "Monthly",
        "unit": "Index 1966:Q1=100",
        "category": "component",
    },
    "MICH": {
        "name": "Inflation Expectations",
        "description": "University of Michigan: Inflation Expectation (1 Year)",
        "frequency": "Monthly",
        "unit": "Percent",
        "category": "inflation",
    },
}

# Historical context thresholds
SENTIMENT_THRESHOLDS = {
    "very_pessimistic": 60,
    "pessimistic": 75,
    "neutral": 90,
    "optimistic": 100,
    # Above 100 = very_optimistic
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

    # Fall back to Latest
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

    # Month-over-month change
    mom_change = None
    mom_pct = None
    prior_value = None
    if len(history) >= 2:
        prior_value = history[-2]["value"]
        if prior_value and prior_value != 0:
            mom_change = latest_value - prior_value
            mom_pct = round((mom_change / prior_value) * 100, 2)

    # Year-over-year change
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


def get_sentiment_level(value: float) -> str:
    """Classify sentiment level based on index value."""
    if value < SENTIMENT_THRESHOLDS["very_pessimistic"]:
        return "very_pessimistic"
    elif value < SENTIMENT_THRESHOLDS["pessimistic"]:
        return "pessimistic"
    elif value < SENTIMENT_THRESHOLDS["neutral"]:
        return "neutral"
    elif value < SENTIMENT_THRESHOLDS["optimistic"]:
        return "optimistic"
    else:
        return "very_optimistic"


@router.get("/overview")
async def get_sentiment_overview(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview of consumer sentiment data.

    Returns headline sentiment index with components and inflation expectations.
    """
    # Get latest values for all series
    results = {}
    for series_id, info in SENTIMENT_SERIES.items():
        data = get_latest_with_changes(db, series_id)
        if data:
            results[series_id.lower()] = {
                "series_id": series_id,
                "name": info["name"],
                "category": info["category"],
                **data,
            }

    # Get headline sentiment details
    headline = results.get("umcsent", {})
    sentiment_level = None
    if headline.get("value"):
        sentiment_level = get_sentiment_level(headline["value"])

    # Get series metadata
    headline_meta = db.query(FredSeries).filter(FredSeries.series_id == "UMCSENT").first()

    # Get long-term statistics from full history
    full_history = get_series_history(db, "UMCSENT", months_back=600)  # 50 years
    values = [obs["value"] for obs in full_history if obs["value"] is not None]

    stats = {}
    if values:
        sorted_vals = sorted(values)
        current_val = headline.get("value", 0)
        percentile = sum(1 for v in sorted_vals if v <= current_val) / len(sorted_vals) * 100

        stats = {
            "all_time_min": min(values),
            "all_time_max": max(values),
            "all_time_avg": round(sum(values) / len(values), 1),
            "current_percentile": round(percentile, 1),
            "observation_count": len(values),
        }

    return {
        "as_of": datetime.now().isoformat(),
        "headline": {
            **headline,
            "sentiment_level": sentiment_level,
        },
        "components": {
            "current_conditions": results.get("umcsent1"),
            "expectations": results.get("umcsent5"),
        },
        "inflation_expectations": results.get("mich"),
        "historical_stats": stats,
        "series_info": {
            "last_updated": headline_meta.last_updated.isoformat() if headline_meta and headline_meta.last_updated else None,
            "observation_start": headline_meta.observation_start.isoformat() if headline_meta and headline_meta.observation_start else None,
        }
    }


@router.get("/timeline")
async def get_sentiment_timeline(
    months_back: int = Query(60, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical timeline for consumer sentiment.

    Returns monthly data for headline index and components.
    """
    # Get history for all main series
    umcsent_history = get_series_history(db, "UMCSENT", months_back=months_back)
    umcsent1_history = get_series_history(db, "UMCSENT1", months_back=months_back)
    umcsent5_history = get_series_history(db, "UMCSENT5", months_back=months_back)
    mich_history = get_series_history(db, "MICH", months_back=months_back)

    # Build unified timeline
    all_dates = set()
    for series in [umcsent_history, umcsent1_history, umcsent5_history, mich_history]:
        for obs in series:
            all_dates.add(obs["date"])

    umcsent_lookup = {obs["date"]: obs["value"] for obs in umcsent_history}
    umcsent1_lookup = {obs["date"]: obs["value"] for obs in umcsent1_history}
    umcsent5_lookup = {obs["date"]: obs["value"] for obs in umcsent5_history}
    mich_lookup = {obs["date"]: obs["value"] for obs in mich_history}

    timeline = []
    for dt in sorted(all_dates):
        timeline.append({
            "date": dt,
            "sentiment": umcsent_lookup.get(dt),
            "current_conditions": umcsent1_lookup.get(dt),
            "expectations": umcsent5_lookup.get(dt),
            "inflation_expectations": mich_lookup.get(dt),
        })

    return {
        "months_back": months_back,
        "data_points": len(timeline),
        "timeline": timeline,
    }


@router.get("/compare-periods")
async def compare_periods(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare current sentiment to notable historical periods.

    Provides context by comparing to recessions, expansions, and crisis periods.
    """
    # Get full history
    full_history = get_series_history(db, "UMCSENT", months_back=600)

    if not full_history:
        return {"error": "No data available"}

    values = [obs["value"] for obs in full_history if obs["value"] is not None]
    current = values[-1] if values else None

    # Calculate key statistics
    sorted_values = sorted(values)
    percentiles = {
        "p10": sorted_values[len(sorted_values) // 10],
        "p25": sorted_values[len(sorted_values) // 4],
        "p50": sorted_values[len(sorted_values) // 2],
        "p75": sorted_values[3 * len(sorted_values) // 4],
        "p90": sorted_values[9 * len(sorted_values) // 10],
    }

    # Find notable extremes
    min_idx = values.index(min(values))
    max_idx = values.index(max(values))

    notable_points = {
        "all_time_low": {
            "value": min(values),
            "date": full_history[min_idx]["date"],
        },
        "all_time_high": {
            "value": max(values),
            "date": full_history[max_idx]["date"],
        },
    }

    # Calculate averages by decade
    by_decade = {}
    for obs in full_history:
        if obs["value"] is not None:
            year = int(obs["date"][:4])
            decade = f"{(year // 10) * 10}s"
            if decade not in by_decade:
                by_decade[decade] = []
            by_decade[decade].append(obs["value"])

    decade_averages = {
        decade: round(sum(vals) / len(vals), 1)
        for decade, vals in by_decade.items()
    }

    return {
        "current": {
            "value": current,
            "date": full_history[-1]["date"] if full_history else None,
            "percentile": round(sum(1 for v in sorted_values if v <= current) / len(sorted_values) * 100, 1) if current else None,
        },
        "percentiles": percentiles,
        "notable_points": notable_points,
        "decade_averages": decade_averages,
        "thresholds": SENTIMENT_THRESHOLDS,
    }


@router.get("/series/{series_id}")
async def get_series_detail(
    series_id: str,
    months_back: int = Query(60, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed data for a specific sentiment series."""
    series_id_upper = series_id.upper()

    if series_id_upper not in SENTIMENT_SERIES:
        return {"error": f"Unknown series: {series_id}. Valid: {list(SENTIMENT_SERIES.keys())}"}

    info = SENTIMENT_SERIES[series_id_upper]

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
        "frequency": info["frequency"],
        "unit": info["unit"],
        "category": info["category"],
        "title": series_meta.title if series_meta else None,
        "notes": series_meta.notes if series_meta else None,
        "observation_start": series_meta.observation_start.isoformat() if series_meta and series_meta.observation_start else None,
        "observation_end": series_meta.observation_end.isoformat() if series_meta and series_meta.observation_end else None,
        "last_updated": series_meta.last_updated.isoformat() if series_meta and series_meta.last_updated else None,
        "latest": latest,
        "statistics": stats,
        "history": history,
    }


@router.get("/correlation")
async def get_correlation_analysis(
    months_back: int = Query(120, ge=12, le=600, description="Months for correlation analysis"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze correlation between current conditions and expectations components.

    Shows how consumer assessment of present vs future diverges or converges.
    """
    current_history = get_series_history(db, "UMCSENT1", months_back=months_back)
    expect_history = get_series_history(db, "UMCSENT5", months_back=months_back)

    current_lookup = {obs["date"]: obs["value"] for obs in current_history}
    expect_lookup = {obs["date"]: obs["value"] for obs in expect_history}

    # Find common dates
    common_dates = set(current_lookup.keys()) & set(expect_lookup.keys())

    analysis = []
    for dt in sorted(common_dates):
        current_val = current_lookup[dt]
        expect_val = expect_lookup[dt]
        if current_val and expect_val:
            gap = current_val - expect_val
            analysis.append({
                "date": dt,
                "current_conditions": current_val,
                "expectations": expect_val,
                "gap": round(gap, 1),  # Positive = more optimistic about present
            })

    # Calculate gap statistics
    gaps = [a["gap"] for a in analysis]
    gap_stats = {}
    if gaps:
        gap_stats = {
            "current_gap": gaps[-1] if gaps else None,
            "avg_gap": round(sum(gaps) / len(gaps), 1),
            "max_gap": max(gaps),
            "min_gap": min(gaps),
        }

    return {
        "months_back": months_back,
        "data_points": len(analysis),
        "gap_stats": gap_stats,
        "analysis": analysis,
    }
