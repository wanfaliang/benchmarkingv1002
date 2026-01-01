"""
FRED Fed Funds Rate Explorer API

Provides endpoints for analyzing Federal Reserve interest rate policy:
- DFEDTARL: Fed Funds Target Rate Lower Limit
- DFEDTARU: Fed Funds Target Rate Upper Limit
- DFF: Effective Federal Funds Rate (daily)
- FEDFUNDS: Effective Federal Funds Rate (monthly average)

Release: H.15 Selected Interest Rates (Release ID: 18)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from backend.app.database import get_data_db
from backend.app.data_models import (
    FredSeries, FredObservationLatest, FredObservationRealtime,
    FredSeriesRelease, FredRelease
)
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.core.cache import cached, DataCategory

router = APIRouter(prefix="/api/research/fred/fedfunds", tags=["FRED Fed Funds"])

# H.15 Selected Interest Rates Release ID
H15_RELEASE_ID = 18

# Fed Funds Rate series definitions
FED_FUNDS_SERIES = {
    "DFEDTARL": {
        "name": "Target Rate Lower",
        "description": "Federal Funds Target Rate - Lower Limit",
        "frequency": "Daily",
        "unit": "Percent",
        "category": "target",
    },
    "DFEDTARU": {
        "name": "Target Rate Upper",
        "description": "Federal Funds Target Rate - Upper Limit",
        "frequency": "Daily",
        "unit": "Percent",
        "category": "target",
    },
    "DFF": {
        "name": "Effective Rate (Daily)",
        "description": "Effective Federal Funds Rate (Daily)",
        "frequency": "Daily",
        "unit": "Percent",
        "category": "effective",
    },
    "FEDFUNDS": {
        "name": "Effective Rate (Monthly)",
        "description": "Effective Federal Funds Rate (Monthly Average)",
        "frequency": "Monthly",
        "unit": "Percent",
        "category": "effective",
    },
}

# Related H.15 series categories for sibling exploration
H15_SIBLING_CATEGORIES = {
    "fed_funds": {
        "name": "Federal Funds Rates",
        "series": ["DFEDTARL", "DFEDTARU", "DFF", "FEDFUNDS"],
    },
    "prime_rates": {
        "name": "Prime & Discount Rates",
        "series": ["DPRIME", "DPCREDIT"],  # Bank Prime Loan, Primary Credit
    },
    "treasury_bills": {
        "name": "Treasury Bills",
        "series": ["DTB4WK", "DTB3", "DTB6", "DTB1YR"],  # 4-week, 3mo, 6mo, 1yr
    },
    "treasury_notes": {
        "name": "Treasury Notes/Bonds",
        "series": ["DGS2", "DGS5", "DGS10", "DGS30"],  # 2yr, 5yr, 10yr, 30yr
    },
    "commercial_paper": {
        "name": "Commercial Paper",
        "series": ["DCPN3M", "DCPF3M"],  # Nonfinancial, Financial 3-month
    },
}


def get_series_history(
    db: Session,
    series_id: str,
    days_back: int = 365,
    prefer_alfred: bool = True,
    max_rows: int = None,
) -> List[Dict[str, Any]]:
    """Get historical observations for a series.

    Args:
        max_rows: If set, limit query to this many rows (for performance)
    """
    start_date = date.today() - timedelta(days=days_back)

    if prefer_alfred:
        query = db.query(FredObservationRealtime).filter(
            FredObservationRealtime.series_id == series_id,
            FredObservationRealtime.date >= start_date,
        ).order_by(FredObservationRealtime.date)

        if max_rows:
            query = query.limit(max_rows)

        obs = query.all()

        if obs:
            return [
                {"date": o.date.isoformat(), "value": o.value}
                for o in obs if o.value is not None
            ]

    # Fall back to Latest
    query = db.query(FredObservationLatest).filter(
        FredObservationLatest.series_id == series_id,
        FredObservationLatest.date >= start_date,
    ).order_by(FredObservationLatest.date)

    if max_rows:
        query = query.limit(max_rows)

    obs = query.all()

    return [
        {"date": o.date.isoformat(), "value": o.value}
        for o in obs if o.value is not None
    ]


def get_multiple_series_history_batch(
    db: Session,
    series_ids: List[str],
    days_back: int = 365,
    prefer_alfred: bool = True,
    sample_every_n: int = 1,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch multiple series in a SINGLE database query for better performance.

    Args:
        series_ids: List of series IDs to fetch
        days_back: Number of days of history
        prefer_alfred: Whether to prefer realtime (ALFRED) data
        sample_every_n: Sample every Nth row (1 = all rows, 2 = every other row, etc.)

    Returns:
        Dictionary mapping series_id -> list of observations
    """
    start_date = date.today() - timedelta(days=days_back)
    result = {sid: [] for sid in series_ids}

    if prefer_alfred:
        # Single query for all series using IN clause
        query = db.query(FredObservationRealtime).filter(
            FredObservationRealtime.series_id.in_(series_ids),
            FredObservationRealtime.date >= start_date,
        ).order_by(
            FredObservationRealtime.series_id,
            FredObservationRealtime.date
        )

        obs_list = query.all()

        if obs_list:
            # Group by series_id and apply sampling
            for series_id in series_ids:
                series_obs = [o for o in obs_list if o.series_id == series_id and o.value is not None]
                if sample_every_n > 1:
                    # Sample every Nth observation
                    series_obs = series_obs[::sample_every_n]
                    # Always include last point
                    all_series_obs = [o for o in obs_list if o.series_id == series_id and o.value is not None]
                    if all_series_obs and (not series_obs or series_obs[-1] != all_series_obs[-1]):
                        series_obs.append(all_series_obs[-1])
                result[series_id] = [
                    {"date": o.date.isoformat(), "value": o.value}
                    for o in series_obs
                ]

            # Check if we got data for all series
            if all(result[sid] for sid in series_ids):
                return result

    # Fall back to Latest for any missing series
    missing_series = [sid for sid in series_ids if not result[sid]]
    if missing_series:
        query = db.query(FredObservationLatest).filter(
            FredObservationLatest.series_id.in_(missing_series),
            FredObservationLatest.date >= start_date,
        ).order_by(
            FredObservationLatest.series_id,
            FredObservationLatest.date
        )

        obs_list = query.all()

        for series_id in missing_series:
            series_obs = [o for o in obs_list if o.series_id == series_id and o.value is not None]
            if sample_every_n > 1:
                all_series_obs = series_obs.copy()
                series_obs = series_obs[::sample_every_n]
                if all_series_obs and (not series_obs or series_obs[-1] != all_series_obs[-1]):
                    series_obs.append(all_series_obs[-1])
            result[series_id] = [
                {"date": o.date.isoformat(), "value": o.value}
                for o in series_obs
            ]

    return result


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
            return {
                "date": obs.date.isoformat(),
                "value": obs.value,
                "source": "alfred"
            }

    obs = db.query(FredObservationLatest).filter(
        FredObservationLatest.series_id == series_id
    ).order_by(desc(FredObservationLatest.date)).first()

    if obs:
        return {
            "date": obs.date.isoformat(),
            "value": obs.value,
            "source": "latest"
        }

    return None


def find_rate_changes(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find all dates where the rate changed.
    Returns list of changes with date, old_rate, new_rate, and change amount.
    """
    if not history or len(history) < 2:
        return []

    changes = []
    prev_value = history[0]["value"]

    for obs in history[1:]:
        if obs["value"] != prev_value:
            change = obs["value"] - prev_value
            changes.append({
                "date": obs["date"],
                "old_rate": prev_value,
                "new_rate": obs["value"],
                "change_bps": round(change * 100, 0),  # Convert to basis points
                "direction": "hike" if change > 0 else "cut",
            })
            prev_value = obs["value"]

    return changes


@router.get("/overview")
@cached("fred:fedfunds:overview", category=DataCategory.FRED_SERIES)
async def get_fedfunds_overview(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview of Federal Funds Rate data.

    Returns current target range (lower/upper), effective rate,
    and recent rate change history.
    """
    # Get latest values for key series
    lower = get_latest_value(db, "DFEDTARL")
    upper = get_latest_value(db, "DFEDTARU")
    effective = get_latest_value(db, "DFF")

    # Calculate target range midpoint
    midpoint = None
    if lower and upper and lower.get("value") is not None and upper.get("value") is not None:
        midpoint = round((lower["value"] + upper["value"]) / 2, 3)

    # Get rate change history from upper limit (5 years is enough for recent policy cycles)
    upper_history = get_series_history(db, "DFEDTARU", days_back=365 * 5)
    rate_changes = find_rate_changes(upper_history)

    # Get last 10 rate changes
    recent_changes = list(reversed(rate_changes[-10:])) if rate_changes else []

    # Calculate stats
    if rate_changes:
        last_change = rate_changes[-1] if rate_changes else None
        hikes_count = sum(1 for c in rate_changes if c["direction"] == "hike")
        cuts_count = sum(1 for c in rate_changes if c["direction"] == "cut")
    else:
        last_change = None
        hikes_count = 0
        cuts_count = 0

    # Get series metadata
    upper_meta = db.query(FredSeries).filter(FredSeries.series_id == "DFEDTARU").first()

    return {
        "as_of": datetime.now().isoformat(),
        "current": {
            "lower_limit": lower.get("value") if lower else None,
            "upper_limit": upper.get("value") if upper else None,
            "midpoint": midpoint,
            "effective_rate": effective.get("value") if effective else None,
            "date": upper.get("date") if upper else (lower.get("date") if lower else None),
        },
        "target_range_display": f"{lower.get('value', 0):.2f}% - {upper.get('value', 0):.2f}%" if lower and upper else None,
        "last_change": last_change,
        "recent_changes": recent_changes,
        "change_stats": {
            "total_changes": len(rate_changes),
            "hikes": hikes_count,
            "cuts": cuts_count,
        },
        "series_info": {
            "last_updated": upper_meta.last_updated.isoformat() if upper_meta and upper_meta.last_updated else None,
            "observation_start": upper_meta.observation_start.isoformat() if upper_meta and upper_meta.observation_start else None,
        }
    }


def sample_timeline(timeline: List[Dict[str, Any]], max_points: int = 500) -> List[Dict[str, Any]]:
    """Sample timeline data to reduce payload size while preserving shape."""
    if len(timeline) <= max_points:
        return timeline

    # Calculate step size to get approximately max_points
    step = len(timeline) / max_points
    sampled = []
    last_idx = -1

    for i in range(max_points):
        idx = int(i * step)
        if idx != last_idx and idx < len(timeline):
            sampled.append(timeline[idx])
            last_idx = idx

    # Always include the last point
    if timeline and (not sampled or sampled[-1] != timeline[-1]):
        sampled.append(timeline[-1])

    return sampled


def build_unified_timeline(
    lower_history: List[Dict[str, Any]],
    upper_history: List[Dict[str, Any]],
    effective_history: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build unified timeline from three series histories."""
    all_dates = set()
    for obs in lower_history:
        all_dates.add(obs["date"])
    for obs in upper_history:
        all_dates.add(obs["date"])
    for obs in effective_history:
        all_dates.add(obs["date"])

    lower_lookup = {obs["date"]: obs["value"] for obs in lower_history}
    upper_lookup = {obs["date"]: obs["value"] for obs in upper_history}
    effective_lookup = {obs["date"]: obs["value"] for obs in effective_history}

    timeline = []
    for dt in sorted(all_dates):
        lower_val = lower_lookup.get(dt)
        upper_val = upper_lookup.get(dt)
        timeline.append({
            "date": dt,
            "lower": lower_val,
            "upper": upper_val,
            "midpoint": round((lower_val + upper_val) / 2, 3) if lower_val is not None and upper_val is not None else None,
            "effective": effective_lookup.get(dt),
        })

    return timeline


def build_comparison_data(
    lower_history: List[Dict[str, Any]],
    upper_history: List[Dict[str, Any]],
    effective_history: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Build comparison data and tracking stats from three series histories."""
    lower_lookup = {obs["date"]: obs["value"] for obs in lower_history}
    upper_lookup = {obs["date"]: obs["value"] for obs in upper_history}
    effective_lookup = {obs["date"]: obs["value"] for obs in effective_history}

    common_dates = set(lower_lookup.keys()) & set(upper_lookup.keys()) & set(effective_lookup.keys())

    comparison = []
    deviations = []

    for dt in sorted(common_dates):
        lower_val = lower_lookup[dt]
        upper_val = upper_lookup[dt]
        effective_val = effective_lookup[dt]
        midpoint = (lower_val + upper_val) / 2
        deviation = effective_val - midpoint

        comparison.append({
            "date": dt,
            "target_lower": lower_val,
            "target_upper": upper_val,
            "target_midpoint": round(midpoint, 3),
            "effective": effective_val,
            "deviation_bps": round(deviation * 100, 1),
        })
        deviations.append(abs(deviation))

    tracking_stats = {}
    if deviations:
        tracking_stats = {
            "avg_deviation_bps": round(sum(deviations) / len(deviations) * 100, 2),
            "max_deviation_bps": round(max(deviations) * 100, 2),
            "within_5bps_pct": round(sum(1 for d in deviations if d <= 0.05) / len(deviations) * 100, 1),
        }

    return comparison, tracking_stats


@router.get("/timeline")
@cached("fred:fedfunds:timeline", category=DataCategory.FRED_SERIES, param_keys=["years_back"])
async def get_fedfunds_timeline(
    years_back: int = Query(5, ge=1, le=50, description="Years of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical timeline for Fed Funds rates.

    Returns sampled data for chart display (max ~500 points).
    Uses optimized batch query to fetch all 3 series in one DB call.
    """
    days_back = years_back * 365

    # OPTIMIZED: Single DB query for all 3 series
    batch_data = get_multiple_series_history_batch(
        db,
        ["DFEDTARL", "DFEDTARU", "DFF"],
        days_back=days_back,
    )

    lower_history = batch_data["DFEDTARL"]
    upper_history = batch_data["DFEDTARU"]
    effective_history = batch_data["DFF"]

    # Build unified timeline
    timeline = build_unified_timeline(lower_history, upper_history, effective_history)

    # Sample for chart display
    sampled_timeline = sample_timeline(timeline, max_points=500)

    return {
        "years_back": years_back,
        "data_points": len(sampled_timeline),
        "total_points": len(timeline),
        "timeline": sampled_timeline,
    }


@router.get("/changes")
@cached("fred:fedfunds:changes", category=DataCategory.FRED_SERIES, param_keys=["years_back"])
async def get_rate_changes(
    years_back: int = Query(5, ge=1, le=50, description="Years of history for changes"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all Fed Funds rate changes (FOMC decisions).

    Returns chronological list of rate changes with direction and magnitude.
    """
    days_back = years_back * 365

    # Get upper limit history (best for tracking changes)
    upper_history = get_series_history(db, "DFEDTARU", days_back=days_back)
    rate_changes = find_rate_changes(upper_history)

    # Reverse to show most recent first
    rate_changes_reversed = list(reversed(rate_changes))

    # Calculate cumulative change
    cumulative = 0
    for change in rate_changes:
        cumulative += change["change_bps"]
        change["cumulative_bps"] = cumulative

    # Summary stats by year
    by_year = {}
    for change in rate_changes:
        year = change["date"][:4]
        if year not in by_year:
            by_year[year] = {"hikes": 0, "cuts": 0, "net_bps": 0}
        if change["direction"] == "hike":
            by_year[year]["hikes"] += 1
        else:
            by_year[year]["cuts"] += 1
        by_year[year]["net_bps"] += change["change_bps"]

    return {
        "years_back": years_back,
        "total_changes": len(rate_changes),
        "changes": rate_changes_reversed,
        "by_year": by_year,
    }


@router.get("/series/{series_id}")
@cached("fred:fedfunds:series", category=DataCategory.FRED_SERIES, param_keys=["series_id", "days_back"])
async def get_series_detail(
    series_id: str,
    days_back: int = Query(365, ge=1, le=18250, description="Days of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed data for a specific Fed Funds series.
    """
    series_id_upper = series_id.upper()

    if series_id_upper not in FED_FUNDS_SERIES:
        return {"error": f"Unknown series: {series_id}. Valid: {list(FED_FUNDS_SERIES.keys())}"}

    info = FED_FUNDS_SERIES[series_id_upper]

    # Get series metadata
    series_meta = db.query(FredSeries).filter(
        FredSeries.series_id == series_id_upper
    ).first()

    # Get latest value
    latest = get_latest_value(db, series_id_upper)

    # Get history
    history = get_series_history(db, series_id_upper, days_back=days_back)

    # Calculate statistics
    values = [obs["value"] for obs in history if obs["value"] is not None]
    stats = {}
    if values:
        stats = {
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 3),
            "current": latest.get("value") if latest else None,
        }

    # Sample history for chart display
    sampled_history = sample_timeline(history, max_points=500)

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
        "history": sampled_history,
        "total_points": len(history),
    }


@router.get("/compare-effective")
@cached("fred:fedfunds:compare", category=DataCategory.FRED_SERIES, param_keys=["days_back"])
async def compare_effective_to_target(
    days_back: int = Query(365, ge=1, le=3650, description="Days of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare effective rate to target range.

    Shows how closely the effective rate tracks the target midpoint.
    Uses optimized batch query to fetch all 3 series in one DB call.
    """
    # OPTIMIZED: Single DB query for all 3 series
    batch_data = get_multiple_series_history_batch(
        db,
        ["DFEDTARL", "DFEDTARU", "DFF"],
        days_back=days_back,
    )

    lower_history = batch_data["DFEDTARL"]
    upper_history = batch_data["DFEDTARU"]
    effective_history = batch_data["DFF"]

    # Build comparison data using shared function
    comparison, tracking_stats = build_comparison_data(lower_history, upper_history, effective_history)

    # Sample for chart display
    sampled_comparison = sample_timeline(comparison, max_points=500)

    return {
        "days_back": days_back,
        "data_points": len(sampled_comparison),
        "total_points": len(comparison),
        "tracking_stats": tracking_stats,
        "comparison": sampled_comparison,
    }


@router.get("/chart-data")
@cached("fred:fedfunds:chart-data", category=DataCategory.FRED_SERIES, param_keys=["years_back"])
async def get_combined_chart_data(
    years_back: int = Query(5, ge=1, le=50, description="Years of history"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    OPTIMIZED: Get all chart data (timeline + comparison + changes) in ONE request.

    This endpoint replaces the need to call /timeline, /compare-effective, and /changes
    separately. Instead of 6-9 separate DB queries, this makes just 1 query.

    Returns:
        - timeline: Rate history for the timeline chart
        - comparison: Effective vs target comparison data
        - changes: FOMC rate decisions
    """
    days_back = years_back * 365

    # SINGLE DB query for all 3 series
    batch_data = get_multiple_series_history_batch(
        db,
        ["DFEDTARL", "DFEDTARU", "DFF"],
        days_back=days_back,
    )

    lower_history = batch_data["DFEDTARL"]
    upper_history = batch_data["DFEDTARU"]
    effective_history = batch_data["DFF"]

    # Build timeline (for Rate History chart)
    timeline = build_unified_timeline(lower_history, upper_history, effective_history)
    sampled_timeline = sample_timeline(timeline, max_points=500)

    # Build comparison (for Effective vs Target chart)
    comparison, tracking_stats = build_comparison_data(lower_history, upper_history, effective_history)
    sampled_comparison = sample_timeline(comparison, max_points=500)

    # Calculate rate changes (for FOMC Decisions table)
    rate_changes = find_rate_changes(upper_history)
    rate_changes_reversed = list(reversed(rate_changes))

    # Summary stats by year
    by_year = {}
    cumulative = 0
    for change in rate_changes:
        cumulative += change["change_bps"]
        change["cumulative_bps"] = cumulative
        year = change["date"][:4]
        if year not in by_year:
            by_year[year] = {"hikes": 0, "cuts": 0, "net_bps": 0}
        if change["direction"] == "hike":
            by_year[year]["hikes"] += 1
        else:
            by_year[year]["cuts"] += 1
        by_year[year]["net_bps"] += change["change_bps"]

    return {
        "years_back": years_back,
        "timeline": {
            "data_points": len(sampled_timeline),
            "total_points": len(timeline),
            "data": sampled_timeline,
        },
        "comparison": {
            "data_points": len(sampled_comparison),
            "total_points": len(comparison),
            "tracking_stats": tracking_stats,
            "data": sampled_comparison,
        },
        "changes": {
            "total_changes": len(rate_changes),
            "data": rate_changes_reversed,
            "by_year": by_year,
        },
    }


@router.get("/sibling-series")
@cached("fred:fedfunds:siblings", category=DataCategory.METADATA)
async def get_sibling_series(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sibling series from H.15 Selected Interest Rates release.

    Returns related interest rate series organized by category.
    """
    result = {}

    for category_key, category_info in H15_SIBLING_CATEGORIES.items():
        series_list = []

        for series_id in category_info["series"]:
            # Get series metadata
            series_meta = db.query(FredSeries).filter(
                FredSeries.series_id == series_id
            ).first()

            # Get latest value
            latest = get_latest_value(db, series_id)

            if series_meta or latest:
                series_list.append({
                    "series_id": series_id,
                    "title": series_meta.title if series_meta else FED_FUNDS_SERIES.get(series_id, {}).get("description", series_id),
                    "frequency": series_meta.frequency_short if series_meta else FED_FUNDS_SERIES.get(series_id, {}).get("frequency"),
                    "units": series_meta.units_short if series_meta else "Percent",
                    "latest_value": latest.get("value") if latest else None,
                    "latest_date": latest.get("date") if latest else None,
                    "observation_start": series_meta.observation_start.isoformat() if series_meta and series_meta.observation_start else None,
                    "observation_end": series_meta.observation_end.isoformat() if series_meta and series_meta.observation_end else None,
                    "available": latest is not None,
                })

        result[category_key] = {
            "name": category_info["name"],
            "series": series_list,
        }

    # Get release info
    release = db.query(FredRelease).filter(FredRelease.release_id == H15_RELEASE_ID).first()

    return {
        "release": {
            "id": H15_RELEASE_ID,
            "name": release.name if release else "H.15 Selected Interest Rates",
            "link": release.link if release else "https://www.federalreserve.gov/releases/h15/",
            "notes": release.notes if release else None,
        },
        "categories": result,
    }


@router.get("/historical-table")
@cached("fred:fedfunds:table", category=DataCategory.FRED_SERIES, param_keys=["years_back", "frequency", "limit"])
async def get_historical_table(
    years_back: int = Query(5, ge=0, le=100, description="Years of history (0 = all)"),
    frequency: str = Query("monthly", description="monthly or daily"),
    limit: int = Query(500, ge=1, le=5000, description="Max rows to return"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical data in table format.

    Returns data formatted for tabular display with all series as columns.
    Supports monthly aggregation for cleaner table display.
    """
    # Calculate days back (0 = all available)
    if years_back == 0:
        days_back = 365 * 100  # ~100 years max
    else:
        days_back = years_back * 365

    # Get histories for all series
    lower_history = get_series_history(db, "DFEDTARL", days_back=days_back)
    upper_history = get_series_history(db, "DFEDTARU", days_back=days_back)
    effective_daily = get_series_history(db, "DFF", days_back=days_back)
    effective_monthly = get_series_history(db, "FEDFUNDS", days_back=days_back)

    if frequency == "monthly":
        # Use monthly effective rate, aggregate target rates by month-end
        monthly_lookup = {obs["date"]: obs["value"] for obs in effective_monthly}

        # Aggregate target rates by month (use last value of each month)
        lower_by_month: Dict[str, float] = {}
        upper_by_month: Dict[str, float] = {}

        for obs in lower_history:
            month_key = obs["date"][:7]  # YYYY-MM
            lower_by_month[month_key] = obs["value"]

        for obs in upper_history:
            month_key = obs["date"][:7]
            upper_by_month[month_key] = obs["value"]

        # Build table data
        all_months = set(monthly_lookup.keys())
        for dt in lower_history:
            all_months.add(dt["date"][:7] + "-01")

        table_data = []
        for month_date in sorted(all_months, reverse=True):
            month_key = month_date[:7]
            lower_val = lower_by_month.get(month_key)
            upper_val = upper_by_month.get(month_key)
            effective_val = monthly_lookup.get(month_date)

            if lower_val is not None or upper_val is not None or effective_val is not None:
                midpoint = round((lower_val + upper_val) / 2, 3) if lower_val and upper_val else None
                table_data.append({
                    "date": month_date,
                    "period": month_key,
                    "target_lower": lower_val,
                    "target_upper": upper_val,
                    "target_midpoint": midpoint,
                    "target_range": f"{lower_val:.2f}-{upper_val:.2f}" if lower_val and upper_val else None,
                    "effective_rate": effective_val,
                })

    else:
        # Daily data
        lower_lookup = {obs["date"]: obs["value"] for obs in lower_history}
        upper_lookup = {obs["date"]: obs["value"] for obs in upper_history}
        effective_lookup = {obs["date"]: obs["value"] for obs in effective_daily}

        all_dates = set(lower_lookup.keys()) | set(upper_lookup.keys()) | set(effective_lookup.keys())

        table_data = []
        for dt in sorted(all_dates, reverse=True):
            lower_val = lower_lookup.get(dt)
            upper_val = upper_lookup.get(dt)
            effective_val = effective_lookup.get(dt)
            midpoint = round((lower_val + upper_val) / 2, 3) if lower_val and upper_val else None

            table_data.append({
                "date": dt,
                "target_lower": lower_val,
                "target_upper": upper_val,
                "target_midpoint": midpoint,
                "target_range": f"{lower_val:.2f}-{upper_val:.2f}" if lower_val and upper_val else None,
                "effective_rate": effective_val,
            })

    # Apply limit
    total_points = len(table_data)
    limited_data = table_data[:limit]

    return {
        "years_back": years_back if years_back > 0 else "all",
        "frequency": frequency,
        "data_points": len(limited_data),
        "total_points": total_points,
        "data": limited_data,
    }


@router.get("/about")
@cached("fred:fedfunds:about", category=DataCategory.METADATA)
async def get_about_info(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive information about Fed Funds Rate data.

    Returns educational content, series definitions, and data sources.
    """
    # Get series metadata for each Fed Funds series
    series_details = []
    for series_id, info in FED_FUNDS_SERIES.items():
        series_meta = db.query(FredSeries).filter(
            FredSeries.series_id == series_id
        ).first()

        latest = get_latest_value(db, series_id)

        series_details.append({
            "series_id": series_id,
            "name": info["name"],
            "description": info["description"],
            "frequency": info["frequency"],
            "category": info["category"],
            "title": series_meta.title if series_meta else None,
            "notes": series_meta.notes if series_meta else None,
            "observation_start": series_meta.observation_start.isoformat() if series_meta and series_meta.observation_start else None,
            "observation_end": series_meta.observation_end.isoformat() if series_meta and series_meta.observation_end else None,
            "last_updated": series_meta.last_updated.isoformat() if series_meta and series_meta.last_updated else None,
            "latest_value": latest.get("value") if latest else None,
            "latest_date": latest.get("date") if latest else None,
        })

    return {
        "title": "Federal Funds Rate",
        "subtitle": "Federal Reserve Interest Rate Policy",
        "description": """
The federal funds rate is the interest rate at which depository institutions (banks and credit unions)
lend reserve balances to other depository institutions overnight, on an uncollateralized basis.
The Federal Open Market Committee (FOMC) sets a target range for this rate as one of its primary
tools for implementing monetary policy.
        """.strip(),
        "key_concepts": [
            {
                "term": "Target Range",
                "definition": "The range set by the FOMC within which the fed funds rate should trade. Since December 2008, the Fed has set a target range rather than a single target rate."
            },
            {
                "term": "Effective Federal Funds Rate",
                "definition": "The volume-weighted median rate at which banks actually transact overnight loans. This is calculated daily by the Federal Reserve Bank of New York."
            },
            {
                "term": "FOMC Meeting",
                "definition": "The Federal Open Market Committee meets 8 times per year to review economic conditions and set monetary policy, including the target fed funds rate."
            },
            {
                "term": "Basis Points (bps)",
                "definition": "One basis point equals 0.01%. Rate changes are typically measured in basis points. A 25 bps increase means the rate went up by 0.25%."
            },
        ],
        "data_source": {
            "name": "Federal Reserve Economic Data (FRED)",
            "provider": "Federal Reserve Bank of St. Louis",
            "release": "H.15 Selected Interest Rates",
            "release_id": H15_RELEASE_ID,
            "url": "https://fred.stlouisfed.org/",
        },
        "series": series_details,
        "related_concepts": [
            "Monetary Policy",
            "Open Market Operations",
            "Quantitative Easing",
            "Inflation Targeting",
            "Bank Reserves",
        ],
    }
