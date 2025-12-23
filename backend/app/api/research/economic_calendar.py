"""
Economic Calendar API - Upcoming and recent economic events.

Provides endpoints for economic data releases calendar from the DATA database.
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.app.database import get_data_db
from backend.app.data_models import EconomicCalendar
from backend.app.core.deps import get_current_user
from backend.app.models.user import User

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research/calendar", tags=["Economic Calendar"])

# Map impact levels to numeric importance (for frontend display)
IMPACT_TO_IMPORTANCE = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
    None: 1,
}

# Map country to source name (for display)
COUNTRY_TO_SOURCE = {
    "US": "US",
    "EU": "EU",
    "UK": "UK",
    "JP": "Japan",
    "CN": "China",
    "CA": "Canada",
    "AU": "Australia",
    "DE": "Germany",
    "FR": "France",
}


def format_event_time(dt: datetime) -> str:
    """Format datetime to time string like '8:30 AM'."""
    if not dt:
        return ""
    # Use %#I on Windows, %-I on Unix for non-padded hour
    try:
        return dt.strftime("%#I:%M %p")  # Windows
    except ValueError:
        return dt.strftime("%-I:%M %p")  # Unix


def format_event_date(dt: datetime) -> str:
    """Format datetime to date string like 'Dec 11'."""
    if not dt:
        return ""
    try:
        return dt.strftime("%b %#d")  # Windows
    except ValueError:
        return dt.strftime("%b %-d")  # Unix


@router.get("/debug")
async def debug_calendar(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check what data exists in the table."""
    from sqlalchemy import func

    total = db.query(func.count(EconomicCalendar.event)).scalar()

    # Get date range
    min_date = db.query(func.min(EconomicCalendar.date)).scalar()
    max_date = db.query(func.max(EconomicCalendar.date)).scalar()

    # Get sample events
    sample = db.query(EconomicCalendar).order_by(EconomicCalendar.date.desc()).limit(5).all()

    return {
        "total_events": total,
        "min_date": min_date.isoformat() if min_date else None,
        "max_date": max_date.isoformat() if max_date else None,
        "current_time": datetime.now().isoformat(),
        "sample_events": [
            {"date": e.date.isoformat() if e.date else None, "event": e.event, "country": e.country}
            for e in sample
        ]
    }


@router.get("/upcoming")
async def get_upcoming_events(
    days: int = Query(14, ge=1, le=90, description="Number of days to look ahead"),
    country: Optional[str] = Query(None, description="Filter by country code (e.g., 'US')"),
    impact: Optional[str] = Query(None, description="Filter by impact level ('High', 'Medium', 'Low')"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of events to return"),
    include_recent: bool = Query(True, description="Include recent events if no upcoming found"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get upcoming economic events.

    Returns events scheduled for the next N days, sorted by date/time.
    If no upcoming events and include_recent=True, returns most recent events instead.
    """
    now = datetime.now()
    end_date = now + timedelta(days=days)

    # Build query for upcoming events
    query = db.query(EconomicCalendar).filter(
        EconomicCalendar.date >= now,
        EconomicCalendar.date <= end_date,
    )

    if country:
        query = query.filter(EconomicCalendar.country == country.upper())

    if impact:
        query = query.filter(EconomicCalendar.impact == impact)

    # Order by date and get results
    events = query.order_by(EconomicCalendar.date).limit(limit).all()

    # If no upcoming events and include_recent is True, get recent events instead
    source = "upcoming"
    if not events and include_recent:
        start_date = now - timedelta(days=30)
        query = db.query(EconomicCalendar).filter(
            EconomicCalendar.date >= start_date,
            EconomicCalendar.date < now,
        )
        if country:
            query = query.filter(EconomicCalendar.country == country.upper())
        if impact:
            query = query.filter(EconomicCalendar.impact == impact)
        events = query.order_by(EconomicCalendar.date.desc()).limit(limit).all()
        source = "recent"

    return {
        "as_of": now.isoformat(),
        "days_ahead": days,
        "count": len(events),
        "data_source": source,  # "upcoming" or "recent"
        "events": [
            {
                "date": format_event_date(e.date),
                "time": format_event_time(e.date),
                "datetime": e.date.isoformat() if e.date else None,
                "name": e.event,
                "country": e.country,
                "source": COUNTRY_TO_SOURCE.get(e.country, e.country),
                "currency": e.currency,
                "previous": float(e.previous) if e.previous else None,
                "estimate": float(e.estimate) if e.estimate else None,
                "actual": float(e.actual) if e.actual else None,
                "change": float(e.change) if e.change else None,
                "change_pct": float(e.change_percentage) if e.change_percentage else None,
                "impact": e.impact,
                "importance": IMPACT_TO_IMPORTANCE.get(e.impact, 1),
                "unit": e.unit,
            }
            for e in events
        ],
    }


@router.get("/recent")
async def get_recent_events(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    impact: Optional[str] = Query(None, description="Filter by impact level"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent economic events (already released).

    Returns events from the past N days with actual values.
    """
    now = datetime.now()
    start_date = now - timedelta(days=days)

    query = db.query(EconomicCalendar).filter(
        EconomicCalendar.date >= start_date,
        EconomicCalendar.date < now,
    )

    if country:
        query = query.filter(EconomicCalendar.country == country.upper())

    if impact:
        query = query.filter(EconomicCalendar.impact == impact)

    events = query.order_by(EconomicCalendar.date.desc()).limit(limit).all()

    return {
        "as_of": now.isoformat(),
        "days_back": days,
        "count": len(events),
        "events": [
            {
                "date": format_event_date(e.date),
                "time": format_event_time(e.date),
                "datetime": e.date.isoformat() if e.date else None,
                "name": e.event,
                "country": e.country,
                "source": COUNTRY_TO_SOURCE.get(e.country, e.country),
                "currency": e.currency,
                "previous": float(e.previous) if e.previous else None,
                "estimate": float(e.estimate) if e.estimate else None,
                "actual": float(e.actual) if e.actual else None,
                "change": float(e.change) if e.change else None,
                "change_pct": float(e.change_percentage) if e.change_percentage else None,
                "impact": e.impact,
                "importance": IMPACT_TO_IMPORTANCE.get(e.impact, 1),
                "unit": e.unit,
                "surprise": (
                    float(e.actual) - float(e.estimate)
                    if e.actual is not None and e.estimate is not None
                    else None
                ),
            }
            for e in events
        ],
    }


@router.get("/week")
async def get_this_week_events(
    country: Optional[str] = Query("US", description="Filter by country code"),
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get economic events for the current week (Mon-Fri).

    This is optimized for the Research portal calendar widget.
    """
    now = datetime.now()

    # Get start of week (Monday) and end of week (Friday EOD)
    days_since_monday = now.weekday()
    start_of_week = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = (start_of_week + timedelta(days=6)).replace(hour=23, minute=59, second=59)

    query = db.query(EconomicCalendar).filter(
        EconomicCalendar.date >= start_of_week,
        EconomicCalendar.date <= end_of_week,
    )

    if country:
        query = query.filter(EconomicCalendar.country == country.upper())

    events = query.order_by(EconomicCalendar.date).all()

    # Group by day for easier display
    events_by_day = {}
    for e in events:
        day_key = e.date.strftime("%Y-%m-%d")
        if day_key not in events_by_day:
            events_by_day[day_key] = []
        events_by_day[day_key].append({
            "time": format_event_time(e.date),
            "name": e.event,
            "impact": e.impact,
            "importance": IMPACT_TO_IMPORTANCE.get(e.impact, 1),
            "previous": float(e.previous) if e.previous else None,
            "estimate": float(e.estimate) if e.estimate else None,
            "actual": float(e.actual) if e.actual else None,
        })

    return {
        "week_start": start_of_week.strftime("%Y-%m-%d"),
        "week_end": end_of_week.strftime("%Y-%m-%d"),
        "country": country,
        "total_events": len(events),
        "events_by_day": events_by_day,
        "events": [
            {
                "date": format_event_date(e.date),
                "time": format_event_time(e.date),
                "datetime": e.date.isoformat() if e.date else None,
                "name": e.event,
                "country": e.country,
                "source": COUNTRY_TO_SOURCE.get(e.country, e.country),
                "impact": e.impact,
                "importance": IMPACT_TO_IMPORTANCE.get(e.impact, 1),
                "previous": float(e.previous) if e.previous else None,
                "estimate": float(e.estimate) if e.estimate else None,
                "actual": float(e.actual) if e.actual else None,
            }
            for e in events
        ],
    }
