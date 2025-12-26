"""
FRED Release Calendar API - Economic data release schedule from FRED.

Provides endpoints for viewing upcoming and historical release dates
for FRED economic data series (CPI, Employment, GDP, etc.).
"""
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from calendar import monthrange
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_data_db
from backend.app.data_models import (
    FredRelease, FredReleaseDate, FredSeries, FredSeriesRelease, FredObservationLatest
)
from backend.app.core.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/research/fred-calendar", tags=["FRED Calendar"])


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_releases_query(db: Session, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Get all releases within a date range.
    Returns list of dicts with release_id, release_name, release_date, series_count.
    """
    results = db.query(
        FredReleaseDate.release_id,
        FredRelease.name.label("release_name"),
        FredReleaseDate.release_date,
        FredRelease.series_count,
    ).join(
        FredRelease, FredReleaseDate.release_id == FredRelease.release_id
    ).filter(
        FredReleaseDate.release_date >= start_date,
        FredReleaseDate.release_date <= end_date,
    ).order_by(
        FredReleaseDate.release_date,
        FredRelease.name,
    ).all()

    return [
        {
            "release_id": r.release_id,
            "release_name": r.release_name,
            "release_date": r.release_date.isoformat() if r.release_date else None,
            "series_count": r.series_count or 0,
        }
        for r in results
    ]


def group_by_date(releases: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group releases by date for calendar display."""
    by_date = {}
    for r in releases:
        d = r["release_date"]
        if d not in by_date:
            by_date[d] = []
        by_date[d].append(r)
    return by_date


# -----------------------------------------------------------------------------
# Calendar Endpoints
# -----------------------------------------------------------------------------

@router.get("/stats")
async def get_calendar_stats(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar statistics."""
    today = date.today()

    # Total release dates
    total = db.query(func.count(FredReleaseDate.release_id)).scalar() or 0

    # Future dates
    future = db.query(func.count(FredReleaseDate.release_id)).filter(
        FredReleaseDate.release_date > today
    ).scalar() or 0

    # Earliest and latest dates
    min_date = db.query(func.min(FredReleaseDate.release_date)).scalar()
    max_date = db.query(func.max(FredReleaseDate.release_date)).scalar()

    # Total unique releases
    total_releases = db.query(func.count(FredRelease.release_id)).scalar() or 0

    return {
        "total_dates": total,
        "future_dates": future,
        "historical_dates": total - future,
        "total_releases": total_releases,
        "earliest_date": min_date.isoformat() if min_date else None,
        "latest_date": max_date.isoformat() if max_date else None,
    }


@router.get("/upcoming")
async def get_upcoming_releases(
    days: int = Query(7, ge=1, le=90, description="Number of days to look ahead"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get upcoming releases for the next N days.
    """
    today = date.today()
    end_date = today + timedelta(days=days)

    releases = get_releases_query(db, today, end_date)

    return {
        "days": days,
        "start_date": today.isoformat(),
        "end_date": end_date.isoformat(),
        "count": len(releases),
        "releases": releases,
    }


@router.get("/month/{year}/{month}")
async def get_releases_by_month(
    year: int,
    month: int,
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all releases for a specific month.
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    if year < 1900 or year > 2100:
        raise HTTPException(status_code=400, detail="Year must be between 1900 and 2100")

    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)

    releases = get_releases_query(db, start_date, end_date)

    return {
        "year": year,
        "month": month,
        "total_releases": len(releases),
        "releases_by_date": group_by_date(releases),
        "releases": releases,
    }


@router.get("/range")
async def get_releases_by_range(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get releases within a date range.
    """
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    releases = get_releases_query(db, start_date, end_date)

    return {
        "start": start,
        "end": end,
        "total_releases": len(releases),
        "releases_by_date": group_by_date(releases),
        "releases": releases,
    }


@router.get("/today")
async def get_todays_releases(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get releases scheduled for today."""
    today = date.today()
    releases = get_releases_query(db, today, today)

    return {
        "date": today.isoformat(),
        "count": len(releases),
        "releases": releases,
    }


@router.get("/week")
async def get_this_weeks_releases(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get releases for the current week (Mon-Sun)."""
    today = date.today()
    # Get Monday of current week
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    releases = get_releases_query(db, monday, sunday)

    return {
        "week_start": monday.isoformat(),
        "week_end": sunday.isoformat(),
        "total_releases": len(releases),
        "releases_by_date": group_by_date(releases),
        "releases": releases,
    }


@router.get("/releases")
async def get_all_releases(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all available releases with their info."""
    releases = db.query(
        FredRelease.release_id,
        FredRelease.name,
        FredRelease.link,
        FredRelease.press_release,
        FredRelease.series_count,
    ).order_by(FredRelease.name).all()

    return {
        "count": len(releases),
        "releases": [
            {
                "release_id": r.release_id,
                "name": r.name,
                "link": r.link,
                "press_release": r.press_release,
                "series_count": r.series_count or 0,
            }
            for r in releases
        ],
    }


@router.get("/release/{release_id}/dates")
async def get_release_dates(
    release_id: int,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of dates to return"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical and upcoming dates for a specific release."""
    # Get release info
    release = db.query(FredRelease).filter(
        FredRelease.release_id == release_id
    ).first()

    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    today = date.today()

    # Get past dates (most recent first)
    past_dates = db.query(FredReleaseDate.release_date).filter(
        FredReleaseDate.release_id == release_id,
        FredReleaseDate.release_date < today,
    ).order_by(FredReleaseDate.release_date.desc()).limit(limit).all()

    # Get future dates
    future_dates = db.query(FredReleaseDate.release_date).filter(
        FredReleaseDate.release_id == release_id,
        FredReleaseDate.release_date >= today,
    ).order_by(FredReleaseDate.release_date).limit(limit).all()

    return {
        "release_id": release_id,
        "name": release.name,
        "link": release.link,
        "press_release": release.press_release,
        "series_count": release.series_count or 0,
        "past_dates": [d.release_date.isoformat() for d in reversed(past_dates)],
        "future_dates": [d.release_date.isoformat() for d in future_dates],
    }


@router.get("/release/{release_id}/series")
async def get_release_series(
    release_id: int,
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=250, description="Maximum number of series to return"),
    search: str = Query(None, description="Search filter for series ID or title"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get all series belonging to a specific release."""
    # Get release info
    release = db.query(FredRelease).filter(
        FredRelease.release_id == release_id
    ).first()

    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    # Build query for series in this release
    query = db.query(FredSeries).join(
        FredSeriesRelease,
        FredSeries.series_id == FredSeriesRelease.series_id
    ).filter(
        FredSeriesRelease.release_id == release_id
    )

    # Apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (FredSeries.series_id.ilike(search_pattern)) |
            (FredSeries.title.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Get paginated results
    series_list = query.order_by(
        FredSeries.popularity.desc().nullslast(),
        FredSeries.series_id
    ).offset(offset).limit(limit).all()

    # Get observation counts ONLY for the paginated series (fast!)
    series_ids = [s.series_id for s in series_list]
    obs_counts = {}
    if series_ids:
        obs_query = db.query(
            FredObservationLatest.series_id,
            func.count(FredObservationLatest.date).label('count')
        ).filter(
            FredObservationLatest.series_id.in_(series_ids)
        ).group_by(FredObservationLatest.series_id).all()
        obs_counts = {r.series_id: r.count for r in obs_query}

    return {
        "release_id": release_id,
        "release_name": release.name,
        "total": total,
        "offset": offset,
        "limit": limit,
        "series": [
            {
                "series_id": s.series_id,
                "title": s.title,
                "units": s.units,
                "units_short": s.units_short,
                "frequency": s.frequency,
                "frequency_short": s.frequency_short,
                "seasonal_adjustment": s.seasonal_adjustment,
                "seasonal_adjustment_short": s.seasonal_adjustment_short,
                "observation_start": s.observation_start.isoformat() if s.observation_start else None,
                "observation_end": s.observation_end.isoformat() if s.observation_end else None,
                "last_updated": s.last_updated.isoformat() if s.last_updated else None,
                "popularity": s.popularity,
                "observations_count": obs_counts.get(s.series_id, 0),
            }
            for s in series_list
        ],
    }


@router.get("/series/{series_id}")
async def get_series_detail(
    series_id: str,
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific series."""
    # Get series info
    series = db.query(FredSeries).filter(
        FredSeries.series_id == series_id
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    # Get observation count
    obs_count = db.query(func.count(FredObservationLatest.date)).filter(
        FredObservationLatest.series_id == series_id
    ).scalar() or 0

    # Get releases this series belongs to
    releases = db.query(
        FredRelease.release_id,
        FredRelease.name
    ).join(
        FredSeriesRelease,
        FredRelease.release_id == FredSeriesRelease.release_id
    ).filter(
        FredSeriesRelease.series_id == series_id
    ).all()

    return {
        "series_id": series.series_id,
        "title": series.title,
        "units": series.units,
        "units_short": series.units_short,
        "frequency": series.frequency,
        "frequency_short": series.frequency_short,
        "seasonal_adjustment": series.seasonal_adjustment,
        "seasonal_adjustment_short": series.seasonal_adjustment_short,
        "observation_start": series.observation_start.isoformat() if series.observation_start else None,
        "observation_end": series.observation_end.isoformat() if series.observation_end else None,
        "last_updated": series.last_updated.isoformat() if series.last_updated else None,
        "popularity": series.popularity,
        "notes": series.notes,
        "observations_count": obs_count,
        "releases": [
            {"release_id": r.release_id, "name": r.name}
            for r in releases
        ],
    }


@router.get("/series/{series_id}/observations")
async def get_series_observations(
    series_id: str,
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(5000, ge=1, le=10000, description="Maximum observations to return"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Get observation data for a series."""
    # Get series info
    series = db.query(FredSeries).filter(
        FredSeries.series_id == series_id
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    # Build query
    query = db.query(
        FredObservationLatest.date,
        FredObservationLatest.value
    ).filter(
        FredObservationLatest.series_id == series_id
    )

    # Apply date filters
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(FredObservationLatest.date >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(FredObservationLatest.date <= end)
        except ValueError:
            pass

    # Get observations ordered by date
    observations = query.order_by(FredObservationLatest.date).limit(limit).all()

    return {
        "series_id": series_id,
        "title": series.title,
        "units": series.units,
        "units_short": series.units_short,
        "frequency": series.frequency,
        "total": len(observations),
        "observations": [
            {
                "date": o.date.isoformat() if o.date else None,
                "value": o.value,
            }
            for o in observations
        ],
    }
