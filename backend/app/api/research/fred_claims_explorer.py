"""
FRED Claims Explorer API - Unemployment Insurance Claims data.

Provides endpoints for analyzing Initial Claims (ICSA) and Continued Claims (CCSA)
from FRED, with historical trends and week-over-week changes.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from backend.app.database import get_data_db
from backend.app.data_models import (
    FredSeries, FredObservationLatest, FredObservationRealtime
)
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.core.cache import cached, DataCategory

router = APIRouter(prefix="/api/research/fred/claims", tags=["FRED Claims"])

# Unemployment Insurance Claims series
CLAIMS_SERIES = {
    "ICSA": {
        "name": "Initial Claims",
        "description": "Initial Claims, Seasonally Adjusted",
        "frequency": "Weekly",
        "unit": "Number",
    },
    "CCSA": {
        "name": "Continued Claims",
        "description": "Continued Claims (Insured Unemployment), Seasonally Adjusted",
        "frequency": "Weekly",
        "unit": "Number",
    },
    "ICNSA": {
        "name": "Initial Claims (NSA)",
        "description": "Initial Claims, Not Seasonally Adjusted",
        "frequency": "Weekly",
        "unit": "Number",
    },
    "IC4WSA": {
        "name": "4-Week MA",
        "description": "4-Week Moving Average of Initial Claims, Seasonally Adjusted",
        "frequency": "Weekly",
        "unit": "Number",
    },
    "IURSA": {
        "name": "Insured Unemployment Rate",
        "description": "Insured Unemployment Rate, Seasonally Adjusted",
        "frequency": "Weekly",
        "unit": "Percent",
    },
    "IURNSA": {
        "name": "IUR (NSA)",
        "description": "Insured Unemployment Rate, Not Seasonally Adjusted",
        "frequency": "Weekly",
        "unit": "Percent",
    },
}

# State abbreviations for state-level claims data
STATE_CODES = [
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL",
    "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA",
    "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE",
    "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR",
    "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VI", "VT", "WA",
    "WI", "WV", "WY",
]

STATE_NAMES = {
    "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DC": "District of Columbia",
    "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "IA": "Iowa", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts",
    "MD": "Maryland", "ME": "Maine", "MI": "Michigan", "MN": "Minnesota",
    "MO": "Missouri", "MS": "Mississippi", "MT": "Montana", "NC": "North Carolina",
    "ND": "North Dakota", "NE": "Nebraska", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NV": "Nevada", "NY": "New York", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "PR": "Puerto Rico",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VA": "Virginia", "VI": "Virgin Islands",
    "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin", "WV": "West Virginia",
    "WY": "Wyoming",
}


def get_series_history(
    db: Session,
    series_id: str,
    weeks_back: int = 52,
    prefer_alfred: bool = True,
) -> List[Dict[str, Any]]:
    """
    Get historical observations for a series.
    """
    start_date = date.today() - timedelta(weeks=weeks_back)

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
    """
    Get latest value with week-over-week and year-over-year changes.
    """
    # Get recent observations (need at least 53 weeks for YoY)
    history = get_series_history(db, series_id, weeks_back=60, prefer_alfred=prefer_alfred)

    if not history:
        return None

    latest = history[-1]
    latest_value = latest["value"]
    latest_date = latest["date"]

    # Week-over-week change (previous week)
    wow_change = None
    wow_pct = None
    prior_value = None
    if len(history) >= 2:
        prior_value = history[-2]["value"]
        if prior_value and prior_value != 0:
            wow_change = latest_value - prior_value
            wow_pct = round((wow_change / prior_value) * 100, 2)

    # Year-over-year change (52 weeks ago)
    yoy_change = None
    yoy_pct = None
    year_ago_value = None
    if len(history) >= 52:
        # Find observation closest to 52 weeks ago
        target_date = date.fromisoformat(latest_date) - timedelta(weeks=52)
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
        "wow_change": wow_change,
        "wow_pct": wow_pct,
        "year_ago_value": year_ago_value,
        "yoy_change": yoy_change,
        "yoy_pct": yoy_pct,
    }


@router.get("/overview")
@cached("fred:claims:overview", category=DataCategory.CLAIMS_WEEKLY)
async def get_claims_overview(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview of unemployment claims data.

    Returns latest values for ICSA and CCSA with week-over-week and year-over-year changes.
    """
    overview = {}

    for series_id, info in CLAIMS_SERIES.items():
        data = get_latest_with_changes(db, series_id)
        if data:
            overview[series_id.lower()] = {
                "series_id": series_id,
                "name": info["name"],
                "description": info["description"],
                **data,
            }

    # Calculate ICSA/CCSA ratio if both available
    ratio = None
    if overview.get("icsa") and overview.get("ccsa"):
        icsa_val = overview["icsa"]["value"]
        ccsa_val = overview["ccsa"]["value"]
        if ccsa_val and ccsa_val != 0:
            ratio = round(icsa_val / ccsa_val, 4)

    return {
        "as_of": datetime.now().isoformat(),
        "claims": overview,
        "icsa_ccsa_ratio": ratio,
    }


@router.get("/overview/timeline")
async def get_claims_timeline(
    weeks_back: int = Query(104, ge=4, le=2600, description="Number of weeks of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical timeline for claims data.

    Returns weekly data for ICSA, CCSA, and 4-week MA.
    """
    timeline_data = {}

    for series_id in ["ICSA", "CCSA", "IC4WSA"]:
        history = get_series_history(db, series_id, weeks_back=weeks_back)
        timeline_data[series_id.lower()] = history

    # Build unified timeline with all series
    all_dates = set()
    for series_data in timeline_data.values():
        for obs in series_data:
            all_dates.add(obs["date"])

    # Create lookup dicts
    lookups = {
        key: {obs["date"]: obs["value"] for obs in data}
        for key, data in timeline_data.items()
    }

    # Build combined timeline
    timeline = []
    for dt in sorted(all_dates):
        timeline.append({
            "date": dt,
            "icsa": lookups.get("icsa", {}).get(dt),
            "ccsa": lookups.get("ccsa", {}).get(dt),
            "ic4wsa": lookups.get("ic4wsa", {}).get(dt),
        })

    return {
        "weeks_back": weeks_back,
        "timeline": timeline,
    }


@router.get("/series/{series_id}")
async def get_claims_series(
    series_id: str,
    weeks_back: int = Query(104, ge=4, le=2600, description="Number of weeks of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed data for a specific claims series.
    """
    series_id_upper = series_id.upper()

    if series_id_upper not in CLAIMS_SERIES:
        return {"error": f"Unknown series: {series_id}. Valid series: {list(CLAIMS_SERIES.keys())}"}

    info = CLAIMS_SERIES[series_id_upper]

    # Get series metadata from database
    series_meta = db.query(FredSeries).filter(
        FredSeries.series_id == series_id_upper
    ).first()

    # Get latest with changes
    latest = get_latest_with_changes(db, series_id_upper)

    # Get history
    history = get_series_history(db, series_id_upper, weeks_back=weeks_back)

    # Calculate statistics
    values = [obs["value"] for obs in history if obs["value"] is not None]
    stats = {}
    if values:
        stats = {
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 0),
            "current_vs_avg_pct": round(((latest["value"] - (sum(values) / len(values))) / (sum(values) / len(values))) * 100, 2) if latest else None,
        }

    return {
        "series_id": series_id_upper,
        "name": info["name"],
        "description": info["description"],
        "frequency": info["frequency"],
        "unit": info["unit"],
        "title": series_meta.title if series_meta else None,
        "notes": series_meta.notes if series_meta else None,
        "observation_start": series_meta.observation_start.isoformat() if series_meta and series_meta.observation_start else None,
        "observation_end": series_meta.observation_end.isoformat() if series_meta and series_meta.observation_end else None,
        "last_updated": series_meta.last_updated.isoformat() if series_meta and series_meta.last_updated else None,
        "latest": latest,
        "statistics": stats,
        "history": history,
    }


@router.get("/compare")
async def compare_claims_periods(
    weeks_back: int = Query(520, ge=4, le=2600, description="Number of weeks to compare"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare current claims levels with historical periods.

    Useful for understanding where we are relative to historical norms.
    """
    # Get ICSA history
    history = get_series_history(db, "ICSA", weeks_back=520)  # 10 years

    if not history:
        return {"error": "No data available"}

    values = [obs["value"] for obs in history if obs["value"] is not None]

    if not values:
        return {"error": "No valid values"}

    current = values[-1]

    # Calculate percentiles
    sorted_values = sorted(values)
    current_percentile = sum(1 for v in sorted_values if v <= current) / len(sorted_values) * 100

    # Find notable thresholds
    periods = {
        "current": {
            "value": current,
            "date": history[-1]["date"],
            "percentile": round(current_percentile, 1),
        },
        "statistics": {
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 0),
            "median": sorted_values[len(sorted_values) // 2],
            "p25": sorted_values[len(sorted_values) // 4],
            "p75": sorted_values[3 * len(sorted_values) // 4],
        },
        "recent_range": {
            "weeks": weeks_back,
            "min": min(values[-weeks_back:]) if len(values) >= weeks_back else min(values),
            "max": max(values[-weeks_back:]) if len(values) >= weeks_back else max(values),
            "avg": round(sum(values[-weeks_back:]) / min(weeks_back, len(values)), 0),
        },
    }

    return periods


@router.get("/states/overview")
async def get_states_overview(
    weeks_back: int = Query(52, ge=1, le=520, description="Number of weeks of history for period comparison"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unemployment claims data for all states with period comparison.

    Returns initial claims with WoW and period changes for each state.
    Uses batch queries for efficiency.
    """
    # Build all series IDs - only ICLAIMS exists for states (no CCLAIMS series)
    iclaims_ids = [f"{sc}ICLAIMS" for sc in STATE_CODES]

    # Calculate date range for the period
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks_back + 2)  # Extra buffer for WoW

    # Get observations for all state series in ONE query
    all_obs = db.query(FredObservationLatest).filter(
        FredObservationLatest.series_id.in_(iclaims_ids),
        FredObservationLatest.date >= start_date
    ).order_by(
        FredObservationLatest.series_id,
        desc(FredObservationLatest.date)
    ).all()

    # Group observations by series_id
    series_obs: dict = defaultdict(list)
    for obs in all_obs:
        series_obs[obs.series_id].append(obs)

    # Build state data
    states_data = []
    for state_code in STATE_CODES:
        iclaims_id = f"{state_code}ICLAIMS"
        obs_list = series_obs.get(iclaims_id, [])

        if not obs_list:
            continue

        latest = obs_list[0]
        prior = obs_list[1] if len(obs_list) > 1 else None

        # WoW change
        wow_change = None
        wow_pct = None
        if prior and prior.value and prior.value != 0:
            wow_change = latest.value - prior.value
            wow_pct = round((wow_change / prior.value) * 100, 2)

        # Period start value (closest to weeks_back ago)
        period_start_date = end_date - timedelta(weeks=weeks_back)
        period_start_value = None
        period_change = None
        period_pct = None

        for obs in reversed(obs_list):
            if obs.date <= period_start_date:
                period_start_value = obs.value
                break

        if period_start_value and period_start_value != 0:
            period_change = latest.value - period_start_value
            period_pct = round((period_change / period_start_value) * 100, 2)

        state_entry = {
            "state_code": state_code,
            "state_name": STATE_NAMES.get(state_code, state_code),
            "iclaims": {
                "value": latest.value,
                "date": latest.date.isoformat(),
                "prior_value": prior.value if prior else None,
                "wow_change": wow_change,
                "wow_pct": wow_pct,
                "period_start_value": period_start_value,
                "period_change": period_change,
                "period_pct": period_pct,
            },
        }
        states_data.append(state_entry)

    # Sort by initial claims value (descending)
    states_data.sort(
        key=lambda x: x.get("iclaims", {}).get("value", 0) or 0,
        reverse=True
    )

    return {
        "as_of": datetime.now().isoformat(),
        "weeks_back": weeks_back,
        "states_count": len(states_data),
        "states": states_data,
    }


@router.get("/states/{state_code}")
async def get_state_claims(
    state_code: str,
    weeks_back: int = Query(104, ge=4, le=2600, description="Number of weeks of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed claims data for a specific state.
    """
    state_code_upper = state_code.upper()

    if state_code_upper not in STATE_CODES:
        return {"error": f"Unknown state: {state_code}. Valid codes: {STATE_CODES}"}

    iclaims_id = f"{state_code_upper}ICLAIMS"
    cclaims_id = f"{state_code_upper}CCLAIMS"

    # Get latest with changes
    iclaims_latest = get_latest_with_changes(db, iclaims_id)
    cclaims_latest = get_latest_with_changes(db, cclaims_id)

    # Get history
    iclaims_history = get_series_history(db, iclaims_id, weeks_back=weeks_back)
    cclaims_history = get_series_history(db, cclaims_id, weeks_back=weeks_back)

    # Calculate statistics for initial claims
    iclaims_stats = {}
    if iclaims_history:
        values = [obs["value"] for obs in iclaims_history if obs["value"] is not None]
        if values:
            iclaims_stats = {
                "min": min(values),
                "max": max(values),
                "avg": round(sum(values) / len(values), 0),
            }

    # Build unified timeline
    all_dates = set()
    for obs in iclaims_history:
        all_dates.add(obs["date"])
    for obs in cclaims_history:
        all_dates.add(obs["date"])

    iclaims_lookup = {obs["date"]: obs["value"] for obs in iclaims_history}
    cclaims_lookup = {obs["date"]: obs["value"] for obs in cclaims_history}

    timeline = []
    for dt in sorted(all_dates):
        timeline.append({
            "date": dt,
            "iclaims": iclaims_lookup.get(dt),
            "cclaims": cclaims_lookup.get(dt),
        })

    return {
        "state_code": state_code_upper,
        "state_name": STATE_NAMES.get(state_code_upper, state_code_upper),
        "iclaims": {
            "series_id": iclaims_id,
            "latest": iclaims_latest,
            "statistics": iclaims_stats,
        },
        "cclaims": {
            "series_id": cclaims_id,
            "latest": cclaims_latest,
        },
        "timeline": timeline,
    }


@router.get("/states/rankings/{metric}")
async def get_state_rankings(
    metric: str,
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get state rankings by a specific metric.

    Metrics: iclaims, cclaims, wow_change, wow_pct
    """
    valid_metrics = ["iclaims", "cclaims", "wow_change", "wow_pct"]
    if metric.lower() not in valid_metrics:
        return {"error": f"Invalid metric. Valid options: {valid_metrics}"}

    states_data = []

    for state_code in STATE_CODES:
        iclaims_id = f"{state_code}ICLAIMS"
        cclaims_id = f"{state_code}CCLAIMS"

        iclaims_data = get_latest_with_changes(db, iclaims_id)
        cclaims_data = get_latest_with_changes(db, cclaims_id)

        if metric.lower() == "iclaims" and iclaims_data:
            states_data.append({
                "state_code": state_code,
                "state_name": STATE_NAMES.get(state_code, state_code),
                "value": iclaims_data.get("value"),
                "date": iclaims_data.get("date"),
            })
        elif metric.lower() == "cclaims" and cclaims_data:
            states_data.append({
                "state_code": state_code,
                "state_name": STATE_NAMES.get(state_code, state_code),
                "value": cclaims_data.get("value"),
                "date": cclaims_data.get("date"),
            })
        elif metric.lower() == "wow_change" and iclaims_data:
            states_data.append({
                "state_code": state_code,
                "state_name": STATE_NAMES.get(state_code, state_code),
                "value": iclaims_data.get("wow_change"),
                "date": iclaims_data.get("date"),
            })
        elif metric.lower() == "wow_pct" and iclaims_data:
            states_data.append({
                "state_code": state_code,
                "state_name": STATE_NAMES.get(state_code, state_code),
                "value": iclaims_data.get("wow_pct"),
                "date": iclaims_data.get("date"),
            })

    # Filter out None values and sort
    states_data = [s for s in states_data if s.get("value") is not None]
    states_data.sort(key=lambda x: x["value"], reverse=True)

    return {
        "metric": metric,
        "as_of": datetime.now().isoformat(),
        "rankings": states_data,
    }
