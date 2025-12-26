"""
FRED Leading Economic Index & Recession Indicators Explorer API

Provides endpoints for analyzing:
- USSLIND: Conference Board Leading Economic Index
- USREC: NBER-based Recession Indicator
- RECPROUSM156N: Smoothed U.S. Recession Probabilities
- Related leading indicators
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

router = APIRouter(prefix="/api/research/fred/leading", tags=["FRED Leading Index"])

# Leading Index and Recession series definitions
LEADING_SERIES = {
    "USSLIND": {
        "name": "Leading Index",
        "description": "Leading Index for the United States",
        "frequency": "Monthly",
        "unit": "Percent",
        "category": "leading",
    },
    "USREC": {
        "name": "Recession Indicator",
        "description": "NBER based Recession Indicators for the United States",
        "frequency": "Monthly",
        "unit": "Binary (1=Recession, 0=Expansion)",
        "category": "recession",
    },
    "RECPROUSM156N": {
        "name": "Recession Probability",
        "description": "Smoothed U.S. Recession Probabilities",
        "frequency": "Monthly",
        "unit": "Percent",
        "category": "recession",
    },
    "USSLIND": {
        "name": "Leading Index",
        "description": "Conference Board Leading Index",
        "frequency": "Monthly",
        "unit": "Percent Change",
        "category": "leading",
    },
}

# Additional leading indicators for comprehensive view
ADDITIONAL_INDICATORS = {
    "T10Y3M": {
        "name": "10Y-3M Spread",
        "description": "10-Year Treasury Minus 3-Month Treasury",
        "category": "spread",
    },
    "T10Y2Y": {
        "name": "10Y-2Y Spread",
        "description": "10-Year Treasury Minus 2-Year Treasury",
        "category": "spread",
    },
}


def get_series_history(
    db: Session,
    series_id: str,
    months_back: int = 120,
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


def get_latest_value(
    db: Session,
    series_id: str,
    prefer_alfred: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get the most recent value for a series."""
    if prefer_alfred:
        obs = db.query(FredObservationRealtime).filter(
            FredObservationRealtime.series_id == series_id
        ).order_by(desc(FredObservationRealtime.date)).first()

        if obs:
            return {"date": obs.date.isoformat(), "value": obs.value}

    obs = db.query(FredObservationLatest).filter(
        FredObservationLatest.series_id == series_id
    ).order_by(desc(FredObservationLatest.date)).first()

    if obs:
        return {"date": obs.date.isoformat(), "value": obs.value}

    return None


def find_recession_periods(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify recession periods from USREC binary indicator.
    Returns list of recession periods with start/end dates and duration.
    """
    if not history:
        return []

    recessions = []
    in_recession = False
    start_date = None

    for obs in history:
        if obs["value"] == 1 and not in_recession:
            # Start of recession
            in_recession = True
            start_date = obs["date"]
        elif obs["value"] == 0 and in_recession:
            # End of recession
            in_recession = False
            if start_date:
                start = date.fromisoformat(start_date)
                end = date.fromisoformat(obs["date"])
                duration_months = (end.year - start.year) * 12 + (end.month - start.month)
                recessions.append({
                    "start_date": start_date,
                    "end_date": obs["date"],
                    "duration_months": duration_months,
                })

    # Handle ongoing recession
    if in_recession and start_date:
        start = date.fromisoformat(start_date)
        end = date.today()
        duration_months = (end.year - start.year) * 12 + (end.month - start.month)
        recessions.append({
            "start_date": start_date,
            "end_date": None,
            "duration_months": duration_months,
            "ongoing": True,
        })

    return recessions


def get_recession_risk_level(probability: float) -> str:
    """Classify recession risk based on probability."""
    if probability >= 50:
        return "high"
    elif probability >= 30:
        return "elevated"
    elif probability >= 15:
        return "moderate"
    else:
        return "low"


@router.get("/overview")
async def get_leading_overview(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview of leading economic indicators and recession status.

    Returns current leading index, recession probability, and NBER indicator.
    """
    # Get latest values
    leading = get_latest_value(db, "USSLIND")
    usrec = get_latest_value(db, "USREC")
    rec_prob = get_latest_value(db, "RECPROUSM156N")

    # Get leading index history for trend analysis
    leading_history = get_series_history(db, "USSLIND", months_back=24)

    # Calculate trend
    trend = None
    consecutive_declines = 0
    if len(leading_history) >= 6:
        recent = leading_history[-6:]
        declines = sum(1 for i in range(1, len(recent)) if recent[i]["value"] < recent[i-1]["value"])
        if declines >= 4:
            trend = "deteriorating"
            consecutive_declines = declines
        elif declines <= 1:
            trend = "improving"
        else:
            trend = "mixed"

    # Get recession periods
    usrec_full = get_series_history(db, "USREC", months_back=600)  # 50 years
    recession_periods = find_recession_periods(usrec_full)

    # Current recession status
    in_recession = usrec and usrec.get("value") == 1

    # Risk level from probability
    risk_level = None
    if rec_prob and rec_prob.get("value") is not None:
        risk_level = get_recession_risk_level(rec_prob["value"])

    # Get metadata
    leading_meta = db.query(FredSeries).filter(FredSeries.series_id == "USSLIND").first()

    return {
        "as_of": datetime.now().isoformat(),
        "leading_index": {
            "value": leading.get("value") if leading else None,
            "date": leading.get("date") if leading else None,
            "trend": trend,
            "consecutive_declines": consecutive_declines if trend == "deteriorating" else None,
        },
        "recession_status": {
            "in_recession": in_recession,
            "nber_indicator": usrec.get("value") if usrec else None,
            "date": usrec.get("date") if usrec else None,
        },
        "recession_probability": {
            "value": rec_prob.get("value") if rec_prob else None,
            "date": rec_prob.get("date") if rec_prob else None,
            "risk_level": risk_level,
        },
        "recent_recessions": recession_periods[-5:] if recession_periods else [],
        "recession_stats": {
            "total_recessions": len(recession_periods),
            "avg_duration_months": round(sum(r["duration_months"] for r in recession_periods) / len(recession_periods), 1) if recession_periods else None,
        },
        "series_info": {
            "last_updated": leading_meta.last_updated.isoformat() if leading_meta and leading_meta.last_updated else None,
        }
    }


@router.get("/timeline")
async def get_leading_timeline(
    months_back: int = Query(120, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical timeline for leading index and recession indicators.
    """
    leading_history = get_series_history(db, "USSLIND", months_back=months_back)
    usrec_history = get_series_history(db, "USREC", months_back=months_back)
    recprob_history = get_series_history(db, "RECPROUSM156N", months_back=months_back)

    # Build unified timeline
    all_dates = set()
    for series in [leading_history, usrec_history, recprob_history]:
        for obs in series:
            all_dates.add(obs["date"])

    leading_lookup = {obs["date"]: obs["value"] for obs in leading_history}
    usrec_lookup = {obs["date"]: obs["value"] for obs in usrec_history}
    recprob_lookup = {obs["date"]: obs["value"] for obs in recprob_history}

    timeline = []
    for dt in sorted(all_dates):
        timeline.append({
            "date": dt,
            "leading_index": leading_lookup.get(dt),
            "recession": usrec_lookup.get(dt),
            "recession_probability": recprob_lookup.get(dt),
        })

    return {
        "months_back": months_back,
        "data_points": len(timeline),
        "timeline": timeline,
    }


@router.get("/recessions")
async def get_recession_history(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed history of all U.S. recessions from NBER data.
    """
    usrec_history = get_series_history(db, "USREC", months_back=1200)  # 100 years
    recession_periods = find_recession_periods(usrec_history)

    # Add context to each recession
    for i, rec in enumerate(recession_periods):
        # Calculate time since previous recession
        if i > 0:
            prev_end = date.fromisoformat(recession_periods[i-1]["end_date"])
            current_start = date.fromisoformat(rec["start_date"])
            gap_months = (current_start.year - prev_end.year) * 12 + (current_start.month - prev_end.month)
            rec["months_since_previous"] = gap_months

    # Summary statistics
    durations = [r["duration_months"] for r in recession_periods]
    gaps = [r.get("months_since_previous") for r in recession_periods if r.get("months_since_previous")]

    stats = {
        "total_recessions": len(recession_periods),
        "avg_duration_months": round(sum(durations) / len(durations), 1) if durations else None,
        "min_duration_months": min(durations) if durations else None,
        "max_duration_months": max(durations) if durations else None,
        "avg_expansion_months": round(sum(gaps) / len(gaps), 1) if gaps else None,
    }

    return {
        "recessions": list(reversed(recession_periods)),
        "statistics": stats,
    }


@router.get("/signals")
async def get_recession_signals(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current recession warning signals from multiple indicators.

    Combines leading index trend, yield curve, and probability model.
    """
    # Get latest values
    leading = get_latest_value(db, "USSLIND")
    rec_prob = get_latest_value(db, "RECPROUSM156N")
    spread_10y3m = get_latest_value(db, "T10Y3M")
    spread_10y2y = get_latest_value(db, "T10Y2Y")

    # Leading index analysis (6 consecutive declines is warning)
    leading_history = get_series_history(db, "USSLIND", months_back=12)
    leading_signal = "neutral"
    leading_declines = 0
    if len(leading_history) >= 6:
        for i in range(len(leading_history) - 1, max(len(leading_history) - 7, 0), -1):
            if leading_history[i]["value"] < leading_history[i-1]["value"]:
                leading_declines += 1
            else:
                break
        if leading_declines >= 6:
            leading_signal = "warning"
        elif leading_declines >= 3:
            leading_signal = "caution"

    # Yield curve analysis (inversion is warning)
    curve_signal = "neutral"
    if spread_10y3m and spread_10y3m.get("value") is not None:
        if spread_10y3m["value"] < 0:
            curve_signal = "inverted"
        elif spread_10y3m["value"] < 0.5:
            curve_signal = "flattening"

    # Probability model
    prob_signal = "low"
    if rec_prob and rec_prob.get("value") is not None:
        prob_signal = get_recession_risk_level(rec_prob["value"])

    # Overall assessment
    warning_count = sum([
        1 if leading_signal == "warning" else 0,
        1 if curve_signal == "inverted" else 0,
        1 if prob_signal in ["high", "elevated"] else 0,
    ])

    if warning_count >= 2:
        overall = "elevated_risk"
    elif warning_count >= 1:
        overall = "caution"
    else:
        overall = "normal"

    return {
        "as_of": datetime.now().isoformat(),
        "signals": {
            "leading_index": {
                "signal": leading_signal,
                "consecutive_declines": leading_declines,
                "value": leading.get("value") if leading else None,
            },
            "yield_curve": {
                "signal": curve_signal,
                "spread_10y3m": spread_10y3m.get("value") if spread_10y3m else None,
                "spread_10y2y": spread_10y2y.get("value") if spread_10y2y else None,
            },
            "probability_model": {
                "signal": prob_signal,
                "probability": rec_prob.get("value") if rec_prob else None,
            },
        },
        "overall_assessment": overall,
        "warning_count": warning_count,
    }


@router.get("/series/{series_id}")
async def get_series_detail(
    series_id: str,
    months_back: int = Query(120, ge=1, le=600, description="Months of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed data for a specific leading/recession series."""
    series_id_upper = series_id.upper()

    all_series = {**LEADING_SERIES, **ADDITIONAL_INDICATORS}
    if series_id_upper not in all_series:
        return {"error": f"Unknown series: {series_id}. Valid: {list(all_series.keys())}"}

    info = all_series[series_id_upper]

    # Get series metadata
    series_meta = db.query(FredSeries).filter(
        FredSeries.series_id == series_id_upper
    ).first()

    # Get latest value
    latest = get_latest_value(db, series_id_upper)

    # Get history
    history = get_series_history(db, series_id_upper, months_back=months_back)

    # Calculate statistics
    values = [obs["value"] for obs in history if obs["value"] is not None]
    stats = {}
    if values:
        stats = {
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 2),
            "current": latest.get("value") if latest else None,
        }

    return {
        "series_id": series_id_upper,
        "name": info["name"],
        "description": info["description"],
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
