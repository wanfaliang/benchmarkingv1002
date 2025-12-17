"""
SM (State and Metro Area Employment) Survey Explorer API

Endpoints for exploring State and Area Employment, Hours, and Earnings data.
Covers all 50 states, DC, Puerto Rico, Virgin Islands, and ~450 metropolitan areas.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from ....database import get_data_db
from ....api.auth import get_current_user
from .sm_schemas import (
    SMDimensions, SMStateItem, SMAreaItem, SMSupersectorItem, SMDataTypeItem,
    SMSeriesInfo, SMSeriesListResponse,
    SMDataPoint, SMSeriesData, SMDataResponse,
    SMSupersectorSummary, SMOverviewResponse, SMOverviewTimelinePoint, SMOverviewTimelineResponse,
    SMStateMetric, SMStateAnalysisResponse, SMStateTimelinePoint, SMStateTimelineResponse,
    SMMetroMetric, SMMetroAnalysisResponse, SMMetroTimelinePoint, SMMetroTimelineResponse,
    SMSupersectorMetric, SMSupersectorAnalysisResponse, SMSupersectorTimelinePoint, SMSupersectorTimelineResponse,
    SMIndustryMetric, SMIndustryAnalysisResponse, SMIndustryTimelinePoint, SMIndustryTimelineResponse,
    SMTopMover, SMTopMoversResponse
)
from ....data_models.bls_models import (
    SMState, SMArea, SMSupersector, SMIndustry, SMSeries, SMData, BLSPeriod
)

router = APIRouter(
    prefix="/api/research/bls/sm",
    tags=["BLS SM - State & Metro Employment"]
)

# Data type codes and their descriptions
DATA_TYPE_MAP = {
    "01": "All Employees (Thousands)",
    "02": "Avg Weekly Hours",
    "03": "Avg Hourly Earnings ($)",
    "06": "Production Employees (Thousands)",
    "07": "Production Avg Weekly Hours",
    "08": "Production Avg Hourly Earnings ($)",
    "11": "Avg Weekly Earnings ($)",
    "26": "All Employees 3-mo Avg Change",
    "30": "Production Avg Weekly Earnings ($)",
}


def _get_period_name(year: int, period: str, db: Session) -> str:
    """Get human-readable period name"""
    period_info = db.query(BLSPeriod).filter(BLSPeriod.period_code == period).first()
    if period_info:
        return f"{period_info.period_name} {year}"

    # Fallback
    month_map = {
        'M01': 'January', 'M02': 'February', 'M03': 'March', 'M04': 'April',
        'M05': 'May', 'M06': 'June', 'M07': 'July', 'M08': 'August',
        'M09': 'September', 'M10': 'October', 'M11': 'November', 'M12': 'December',
        'M13': 'Annual Average'
    }
    return f"{month_map.get(period, period)} {year}"


def _calculate_employment_metrics(series_id: str, db: Session):
    """Calculate employment metrics for a series"""
    data = db.query(SMData).filter(
        SMData.series_id == series_id,
        SMData.period != 'M13'  # Exclude annual averages
    ).order_by(desc(SMData.year), desc(SMData.period)).limit(14).all()

    if not data:
        return None

    latest = data[0]
    prev_month = data[1] if len(data) > 1 else None
    prev_year = None

    # Find same month last year
    for d in data:
        if d.year == latest.year - 1 and d.period == latest.period:
            prev_year = d
            break

    latest_value = float(latest.value) if latest.value else None

    mom_change = None
    mom_pct = None
    if prev_month and prev_month.value and latest_value:
        prev_val = float(prev_month.value)
        mom_change = latest_value - prev_val
        mom_pct = (mom_change / prev_val) * 100 if prev_val != 0 else None

    yoy_change = None
    yoy_pct = None
    if prev_year and prev_year.value and latest_value:
        prev_val = float(prev_year.value)
        yoy_change = latest_value - prev_val
        yoy_pct = (yoy_change / prev_val) * 100 if prev_val != 0 else None

    return {
        "latest_value": latest_value,
        "latest_date": _get_period_name(latest.year, latest.period, db),
        "latest_year": latest.year,
        "latest_period": latest.period,
        "mom_change": round(mom_change, 1) if mom_change is not None else None,
        "mom_pct": round(mom_pct, 2) if mom_pct is not None else None,
        "yoy_change": round(yoy_change, 1) if yoy_change is not None else None,
        "yoy_pct": round(yoy_pct, 2) if yoy_pct is not None else None
    }


# ==================== Dimensions ====================

@router.get("/dimensions", response_model=SMDimensions)
def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get available dimensions for SM survey filtering"""

    # Get all states
    states = db.query(SMState).order_by(SMState.state_name).all()
    state_items = [SMStateItem(state_code=s.state_code, state_name=s.state_name) for s in states]

    # Get all areas (limit to a reasonable number for dropdown)
    areas = db.query(SMArea).order_by(SMArea.area_name).limit(500).all()
    area_items = [SMAreaItem(area_code=a.area_code, area_name=a.area_name) for a in areas]

    # Get all supersectors
    supersectors = db.query(SMSupersector).order_by(SMSupersector.supersector_code).all()
    supersector_items = [SMSupersectorItem(supersector_code=s.supersector_code, supersector_name=s.supersector_name) for s in supersectors]

    # Create data type items from map
    data_type_items = [SMDataTypeItem(data_type_code=k, data_type_name=v) for k, v in DATA_TYPE_MAP.items()]

    return SMDimensions(
        states=state_items,
        areas=area_items,
        supersectors=supersector_items,
        data_types=data_type_items
    )


# ==================== Series ====================

@router.get("/series", response_model=SMSeriesListResponse)
def get_series(
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    area_code: Optional[str] = Query(None, description="Filter by area code (e.g., '00000' for statewide)"),
    supersector_code: Optional[str] = Query(None, description="Filter by supersector code"),
    industry_code: Optional[str] = Query(None, description="Filter by industry code"),
    data_type_code: Optional[str] = Query(None, description="Filter by data type (01=employment, 03=earnings, etc.)"),
    seasonal_code: Optional[str] = Query(None, description="S=Seasonally Adjusted, U=Not Adjusted"),
    active_only: bool = Query(True, description="Only return active series"),
    search: Optional[str] = Query(None, description="Search in industry name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """List SM series with optional filters and search"""

    query = db.query(SMSeries)

    # Apply filters
    if state_code:
        query = query.filter(SMSeries.state_code == state_code)

    if area_code:
        query = query.filter(SMSeries.area_code == area_code)

    if supersector_code:
        query = query.filter(SMSeries.supersector_code == supersector_code)

    if industry_code:
        query = query.filter(SMSeries.industry_code == industry_code)

    if data_type_code:
        query = query.filter(SMSeries.data_type_code == data_type_code)

    if seasonal_code:
        query = query.filter(SMSeries.seasonal_code == seasonal_code)

    if active_only:
        query = query.filter(SMSeries.is_active == True)

    if search:
        # Join with industry table to search by name
        matching_industries = db.query(SMIndustry.industry_code).filter(
            SMIndustry.industry_name.ilike(f"%{search}%")
        ).all()
        matching_codes = [i[0] for i in matching_industries]
        if matching_codes:
            query = query.filter(SMSeries.industry_code.in_(matching_codes))
        else:
            query = query.filter(False)  # No matches

    total = query.count()

    series = query.order_by(SMSeries.state_code, SMSeries.area_code, SMSeries.supersector_code).offset(offset).limit(limit).all()

    # Get names for display
    state_names = {s.state_code: s.state_name for s in db.query(SMState).all()}
    area_names = {a.area_code: a.area_name for a in db.query(SMArea).all()}
    supersector_names = {s.supersector_code: s.supersector_name for s in db.query(SMSupersector).all()}
    industry_codes = list(set(s.industry_code for s in series if s.industry_code))
    industry_names = {}
    if industry_codes:
        industries = db.query(SMIndustry).filter(SMIndustry.industry_code.in_(industry_codes)).all()
        industry_names = {i.industry_code: i.industry_name for i in industries}

    series_list = [
        SMSeriesInfo(
            series_id=s.series_id,
            state_code=s.state_code,
            state_name=state_names.get(s.state_code),
            area_code=s.area_code,
            area_name=area_names.get(s.area_code),
            supersector_code=s.supersector_code,
            supersector_name=supersector_names.get(s.supersector_code),
            industry_code=s.industry_code,
            industry_name=industry_names.get(s.industry_code),
            data_type_code=s.data_type_code,
            data_type_name=DATA_TYPE_MAP.get(s.data_type_code),
            seasonal_code=s.seasonal_code,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active
        )
        for s in series
    ]

    return SMSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_list
    )


@router.get("/series/{series_id}/data", response_model=SMDataResponse)
def get_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    include_annual: bool = Query(False, description="Include annual averages (M13)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get time series data for a specific SM series"""

    series = db.query(SMSeries).filter(SMSeries.series_id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    query = db.query(SMData).filter(SMData.series_id == series_id)

    if not include_annual:
        query = query.filter(SMData.period != 'M13')

    if start_year:
        query = query.filter(SMData.year >= start_year)

    if end_year:
        query = query.filter(SMData.year <= end_year)

    data = query.order_by(SMData.year, SMData.period).all()

    # Get names
    state_name = None
    if series.state_code:
        state = db.query(SMState).filter(SMState.state_code == series.state_code).first()
        if state:
            state_name = state.state_name

    area_name = None
    if series.area_code:
        area = db.query(SMArea).filter(SMArea.area_code == series.area_code).first()
        if area:
            area_name = area.area_name

    supersector_name = None
    if series.supersector_code:
        supersector = db.query(SMSupersector).filter(SMSupersector.supersector_code == series.supersector_code).first()
        if supersector:
            supersector_name = supersector.supersector_name

    industry_name = None
    if series.industry_code:
        industry = db.query(SMIndustry).filter(SMIndustry.industry_code == series.industry_code).first()
        if industry:
            industry_name = industry.industry_name

    data_points = [
        SMDataPoint(
            year=d.year,
            period=d.period,
            period_name=_get_period_name(d.year, d.period, db),
            value=float(d.value) if d.value else None,
            footnote_codes=d.footnote_codes
        )
        for d in data
    ]

    return SMDataResponse(
        series=[SMSeriesData(
            series_id=series.series_id,
            state_name=state_name,
            area_name=area_name,
            supersector_name=supersector_name,
            industry_name=industry_name,
            data_type_name=DATA_TYPE_MAP.get(series.data_type_code),
            data_points=data_points
        )]
    )


# ==================== Overview ====================

@router.get("/overview", response_model=SMOverviewResponse)
def get_overview(
    state_code: str = Query(..., description="State code (e.g., '36' for New York)"),
    area_code: str = Query("00000", description="Area code ('00000' for statewide)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get employment overview by supersector for a state/area

    Shows Total Nonfarm and major supersector breakdown.
    """

    # Get state and area names
    state = db.query(SMState).filter(SMState.state_code == state_code).first()
    if not state:
        raise HTTPException(status_code=404, detail=f"State {state_code} not found")

    area = db.query(SMArea).filter(SMArea.area_code == area_code).first()
    area_name = area.area_name if area else "Unknown"

    # Get all supersectors
    supersectors = db.query(SMSupersector).order_by(SMSupersector.supersector_code).all()

    summaries = []
    last_updated = None

    for ss in supersectors:
        # Find employment series (data_type_code = '01') for this supersector
        series = db.query(SMSeries).filter(
            SMSeries.state_code == state_code,
            SMSeries.area_code == area_code,
            SMSeries.supersector_code == ss.supersector_code,
            SMSeries.data_type_code == '01',  # All employees
            SMSeries.is_active == True
        ).first()

        if not series:
            # Try seasonally adjusted first, then unadjusted
            series = db.query(SMSeries).filter(
                SMSeries.state_code == state_code,
                SMSeries.area_code == area_code,
                SMSeries.supersector_code == ss.supersector_code,
                SMSeries.data_type_code == '01',
                SMSeries.seasonal_code == 'S'
            ).first()

            if not series:
                series = db.query(SMSeries).filter(
                    SMSeries.state_code == state_code,
                    SMSeries.area_code == area_code,
                    SMSeries.supersector_code == ss.supersector_code,
                    SMSeries.data_type_code == '01',
                    SMSeries.seasonal_code == 'U'
                ).first()

        if not series:
            continue

        metrics = _calculate_employment_metrics(series.series_id, db)
        if not metrics:
            continue

        summaries.append(SMSupersectorSummary(
            supersector_code=ss.supersector_code,
            supersector_name=ss.supersector_name,
            series_id=series.series_id,
            employment=metrics["latest_value"],
            latest_date=metrics["latest_date"],
            mom_change=metrics["mom_change"],
            mom_pct=metrics["mom_pct"],
            yoy_change=metrics["yoy_change"],
            yoy_pct=metrics["yoy_pct"]
        ))

        if not last_updated:
            last_updated = metrics["latest_date"]

    return SMOverviewResponse(
        state_code=state_code,
        state_name=state.state_name,
        area_code=area_code,
        area_name=area_name,
        supersectors=summaries,
        last_updated=last_updated
    )


@router.get("/overview/timeline", response_model=SMOverviewTimelineResponse)
def get_overview_timeline(
    state_code: str = Query(..., description="State code"),
    area_code: str = Query("00000", description="Area code"),
    months_back: int = Query(24, ge=1, le=9999, description="Number of months to look back"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for supersector employment"""

    # Get state and area names
    state = db.query(SMState).filter(SMState.state_code == state_code).first()
    area = db.query(SMArea).filter(SMArea.area_code == area_code).first()

    # Get supersectors and their series
    supersectors = db.query(SMSupersector).order_by(SMSupersector.supersector_code).all()

    supersector_series = {}
    supersector_names = {}

    for ss in supersectors:
        series = db.query(SMSeries).filter(
            SMSeries.state_code == state_code,
            SMSeries.area_code == area_code,
            SMSeries.supersector_code == ss.supersector_code,
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if series:
            supersector_series[ss.supersector_code] = series.series_id
            supersector_names[ss.supersector_code] = ss.supersector_name

    if not supersector_series:
        return SMOverviewTimelineResponse(
            state_name=state.state_name if state else None,
            area_name=area.area_name if area else None,
            timeline=[],
            supersector_names={}
        )

    # Get latest data point
    first_series_id = next(iter(supersector_series.values()))
    latest = db.query(SMData).filter(
        SMData.series_id == first_series_id,
        SMData.period != 'M13'
    ).order_by(desc(SMData.year), desc(SMData.period)).first()

    if not latest:
        return SMOverviewTimelineResponse(
            state_name=state.state_name if state else None,
            area_name=area.area_name if area else None,
            timeline=[],
            supersector_names=supersector_names
        )

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    if months_back >= 9999:
        start_year = 1939
        start_period_num = 1
    else:
        months_to_subtract = months_back
        while months_to_subtract > 0:
            if start_period_num > months_to_subtract:
                start_period_num -= months_to_subtract
                months_to_subtract = 0
            else:
                months_to_subtract -= start_period_num
                start_year -= 1
                start_period_num = 12

    start_period = f"M{start_period_num:02d}"

    # Get data for all supersectors
    all_series_ids = list(supersector_series.values())

    data = db.query(SMData).filter(
        SMData.series_id.in_(all_series_ids),
        SMData.period != 'M13',
        ((SMData.year > start_year) |
         ((SMData.year == start_year) & (SMData.period >= start_period)))
    ).order_by(SMData.year, SMData.period).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {}

        for ss_code, series_id in supersector_series.items():
            if d.series_id == series_id:
                period_data[key][ss_code] = float(d.value) if d.value else None

    # Build timeline
    timeline = []
    for (year, period) in sorted(period_data.keys()):
        timeline.append(SMOverviewTimelinePoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            supersectors=period_data[(year, period)]
        ))

    return SMOverviewTimelineResponse(
        state_name=state.state_name if state else None,
        area_name=area.area_name if area else None,
        timeline=timeline,
        supersector_names=supersector_names
    )


# ==================== State Analysis ====================

@router.get("/states", response_model=SMStateAnalysisResponse)
def get_states_analysis(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get Total Nonfarm employment data for all states"""

    states = db.query(SMState).filter(
        SMState.state_code != '00',  # Exclude "All States"
        SMState.state_code != '99'   # Exclude "All MSAs"
    ).order_by(SMState.state_name).all()

    state_metrics = []
    last_updated = None

    for state in states:
        # Find Total Nonfarm (supersector_code='00') statewide (area_code='00000') employment series
        series = db.query(SMSeries).filter(
            SMSeries.state_code == state.state_code,
            SMSeries.area_code == '00000',
            SMSeries.supersector_code == '00',
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if not series:
            # Try seasonally adjusted
            series = db.query(SMSeries).filter(
                SMSeries.state_code == state.state_code,
                SMSeries.area_code == '00000',
                SMSeries.supersector_code == '00',
                SMSeries.data_type_code == '01',
                SMSeries.seasonal_code == 'S'
            ).first()

        if not series:
            continue

        metrics = _calculate_employment_metrics(series.series_id, db)
        if not metrics:
            continue

        state_metrics.append(SMStateMetric(
            state_code=state.state_code,
            state_name=state.state_name,
            series_id=series.series_id,
            employment=metrics["latest_value"],
            latest_date=metrics["latest_date"],
            month_over_month=metrics["mom_change"],
            month_over_month_pct=metrics["mom_pct"],
            year_over_year=metrics["yoy_change"],
            year_over_year_pct=metrics["yoy_pct"]
        ))

        if not last_updated:
            last_updated = metrics["latest_date"]

    # Sort by employment descending
    state_metrics.sort(key=lambda x: x.employment if x.employment else 0, reverse=True)

    # Get rankings
    highest = [m.state_name for m in state_metrics[:5]]
    by_growth = sorted(state_metrics, key=lambda x: x.year_over_year_pct if x.year_over_year_pct else 0, reverse=True)
    highest_growth = [m.state_name for m in by_growth[:5]]

    return SMStateAnalysisResponse(
        states=state_metrics,
        rankings={"highest_employment": highest, "highest_growth": highest_growth},
        last_updated=last_updated
    )


@router.get("/states/timeline", response_model=SMStateTimelineResponse)
def get_states_timeline(
    months_back: int = Query(24, ge=1, le=9999),
    state_codes: Optional[str] = Query(None, description="Comma-separated state codes"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for state Total Nonfarm employment"""

    # Determine which states to include
    if state_codes:
        codes = [code.strip() for code in state_codes.split(',')]
        states = db.query(SMState).filter(SMState.state_code.in_(codes)).all()
    else:
        states = db.query(SMState).filter(
            SMState.state_code != '00',
            SMState.state_code != '99'
        ).all()

    # Get series for each state
    state_series = {}
    state_names = {}

    for state in states:
        series = db.query(SMSeries).filter(
            SMSeries.state_code == state.state_code,
            SMSeries.area_code == '00000',
            SMSeries.supersector_code == '00',
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if series:
            state_series[state.state_code] = series.series_id
            state_names[state.state_code] = state.state_name

    if not state_series:
        return SMStateTimelineResponse(timeline=[], state_names={})

    # Get latest data point
    first_series_id = next(iter(state_series.values()))
    latest = db.query(SMData).filter(
        SMData.series_id == first_series_id,
        SMData.period != 'M13'
    ).order_by(desc(SMData.year), desc(SMData.period)).first()

    if not latest:
        return SMStateTimelineResponse(timeline=[], state_names=state_names)

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    if months_back >= 9999:
        start_year = 1939
        start_period_num = 1
    else:
        months_to_subtract = months_back
        while months_to_subtract > 0:
            if start_period_num > months_to_subtract:
                start_period_num -= months_to_subtract
                months_to_subtract = 0
            else:
                months_to_subtract -= start_period_num
                start_year -= 1
                start_period_num = 12

    start_period = f"M{start_period_num:02d}"

    # Get data for all states
    all_series_ids = list(state_series.values())

    data = db.query(SMData).filter(
        SMData.series_id.in_(all_series_ids),
        SMData.period != 'M13',
        ((SMData.year > start_year) |
         ((SMData.year == start_year) & (SMData.period >= start_period)))
    ).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {}

        for sc, series_id in state_series.items():
            if d.series_id == series_id:
                period_data[key][sc] = float(d.value) if d.value else None

    # Build timeline
    timeline = []
    for (year, period) in sorted(period_data.keys()):
        timeline.append(SMStateTimelinePoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            states=period_data[(year, period)]
        ))

    return SMStateTimelineResponse(
        timeline=timeline,
        state_names=state_names
    )


# ==================== Metro Analysis ====================

@router.get("/metros", response_model=SMMetroAnalysisResponse)
def get_metros_analysis(
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get Total Nonfarm employment data for metropolitan areas"""

    # Get areas that are not statewide
    areas = db.query(SMArea).filter(
        SMArea.area_code != '00000',
        SMArea.area_code != '99999'
    ).order_by(SMArea.area_name).all()

    metro_metrics = []
    last_updated = None

    for area in areas:
        # Find Total Nonfarm employment series for this area
        query = db.query(SMSeries).filter(
            SMSeries.area_code == area.area_code,
            SMSeries.supersector_code == '00',
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        )

        if state_code:
            query = query.filter(SMSeries.state_code == state_code)

        series = query.first()

        if not series:
            continue

        metrics = _calculate_employment_metrics(series.series_id, db)
        if not metrics:
            continue

        state = db.query(SMState).filter(SMState.state_code == series.state_code).first()

        metro_metrics.append(SMMetroMetric(
            state_code=series.state_code,
            state_name=state.state_name if state else None,
            area_code=area.area_code,
            area_name=area.area_name,
            series_id=series.series_id,
            employment=metrics["latest_value"],
            latest_date=metrics["latest_date"],
            month_over_month=metrics["mom_change"],
            month_over_month_pct=metrics["mom_pct"],
            year_over_year=metrics["yoy_change"],
            year_over_year_pct=metrics["yoy_pct"]
        ))

        if not last_updated:
            last_updated = metrics["latest_date"]

        if len(metro_metrics) >= limit:
            break

    # Sort by employment descending
    metro_metrics.sort(key=lambda x: x.employment if x.employment else 0, reverse=True)

    return SMMetroAnalysisResponse(
        metros=metro_metrics[:limit],
        total_count=len(metro_metrics),
        last_updated=last_updated
    )


@router.get("/metros/timeline", response_model=SMMetroTimelineResponse)
def get_metros_timeline(
    months_back: int = Query(24, ge=1, le=9999),
    area_codes: Optional[str] = Query(None, description="Comma-separated area codes"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for metro Total Nonfarm employment"""

    # Determine which metros to include
    if area_codes:
        codes = [code.strip() for code in area_codes.split(',')]
        areas = db.query(SMArea).filter(SMArea.area_code.in_(codes)).all()
    else:
        areas = db.query(SMArea).filter(
            SMArea.area_code != '00000',
            SMArea.area_code != '99999'
        ).order_by(SMArea.area_name).limit(limit).all()

    # Get series for each metro
    metro_series = {}
    metro_names = {}

    for area in areas:
        series = db.query(SMSeries).filter(
            SMSeries.area_code == area.area_code,
            SMSeries.supersector_code == '00',
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if series:
            metro_series[area.area_code] = series.series_id
            metro_names[area.area_code] = area.area_name

    if not metro_series:
        return SMMetroTimelineResponse(timeline=[], metro_names={})

    # Get latest data point
    first_series_id = next(iter(metro_series.values()))
    latest = db.query(SMData).filter(
        SMData.series_id == first_series_id,
        SMData.period != 'M13'
    ).order_by(desc(SMData.year), desc(SMData.period)).first()

    if not latest:
        return SMMetroTimelineResponse(timeline=[], metro_names=metro_names)

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    if months_back >= 9999:
        start_year = 1990
        start_period_num = 1
    else:
        months_to_subtract = months_back
        while months_to_subtract > 0:
            if start_period_num > months_to_subtract:
                start_period_num -= months_to_subtract
                months_to_subtract = 0
            else:
                months_to_subtract -= start_period_num
                start_year -= 1
                start_period_num = 12

    start_period = f"M{start_period_num:02d}"

    # Get data for all metros
    all_series_ids = list(metro_series.values())

    data = db.query(SMData).filter(
        SMData.series_id.in_(all_series_ids),
        SMData.period != 'M13',
        ((SMData.year > start_year) |
         ((SMData.year == start_year) & (SMData.period >= start_period)))
    ).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {}

        for ac, series_id in metro_series.items():
            if d.series_id == series_id:
                period_data[key][ac] = float(d.value) if d.value else None

    # Build timeline
    timeline = []
    for (year, period) in sorted(period_data.keys()):
        timeline.append(SMMetroTimelinePoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            metros=period_data[(year, period)]
        ))

    return SMMetroTimelineResponse(
        timeline=timeline,
        metro_names=metro_names
    )


# ==================== Supersector Analysis ====================

@router.get("/supersectors", response_model=SMSupersectorAnalysisResponse)
def get_supersectors_analysis(
    state_code: str = Query(..., description="State code"),
    area_code: str = Query("00000", description="Area code"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get employment breakdown by supersector for a state/area"""

    state = db.query(SMState).filter(SMState.state_code == state_code).first()
    if not state:
        raise HTTPException(status_code=404, detail=f"State {state_code} not found")

    area = db.query(SMArea).filter(SMArea.area_code == area_code).first()

    supersectors = db.query(SMSupersector).order_by(SMSupersector.supersector_code).all()

    supersector_metrics = []
    last_updated = None

    for ss in supersectors:
        series = db.query(SMSeries).filter(
            SMSeries.state_code == state_code,
            SMSeries.area_code == area_code,
            SMSeries.supersector_code == ss.supersector_code,
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if not series:
            continue

        metrics = _calculate_employment_metrics(series.series_id, db)
        if not metrics:
            continue

        supersector_metrics.append(SMSupersectorMetric(
            supersector_code=ss.supersector_code,
            supersector_name=ss.supersector_name,
            series_id=series.series_id,
            employment=metrics["latest_value"],
            latest_date=metrics["latest_date"],
            month_over_month=metrics["mom_change"],
            month_over_month_pct=metrics["mom_pct"],
            year_over_year=metrics["yoy_change"],
            year_over_year_pct=metrics["yoy_pct"]
        ))

        if not last_updated:
            last_updated = metrics["latest_date"]

    return SMSupersectorAnalysisResponse(
        state_code=state_code,
        state_name=state.state_name,
        area_code=area_code,
        area_name=area.area_name if area else None,
        supersectors=supersector_metrics,
        last_updated=last_updated
    )


@router.get("/supersectors/timeline", response_model=SMSupersectorTimelineResponse)
def get_supersectors_timeline(
    state_code: str = Query(..., description="State code"),
    area_code: str = Query("00000", description="Area code"),
    supersector_codes: str = Query(..., description="Comma-separated supersector codes"),
    months_back: int = Query(24, ge=1, le=9999),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for supersector comparison"""

    state = db.query(SMState).filter(SMState.state_code == state_code).first()
    area = db.query(SMArea).filter(SMArea.area_code == area_code).first()

    codes = [c.strip() for c in supersector_codes.split(',')]

    # Get series for each supersector
    supersector_series = {}
    supersector_names = {}

    for code in codes:
        ss = db.query(SMSupersector).filter(SMSupersector.supersector_code == code).first()
        if not ss:
            continue

        series = db.query(SMSeries).filter(
            SMSeries.state_code == state_code,
            SMSeries.area_code == area_code,
            SMSeries.supersector_code == code,
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if series:
            supersector_series[code] = series.series_id
            supersector_names[code] = ss.supersector_name

    if not supersector_series:
        return SMSupersectorTimelineResponse(
            state_name=state.state_name if state else None,
            area_name=area.area_name if area else None,
            timeline=[],
            supersector_names={}
        )

    # Get latest data point
    first_series_id = next(iter(supersector_series.values()))
    latest = db.query(SMData).filter(
        SMData.series_id == first_series_id,
        SMData.period != 'M13'
    ).order_by(desc(SMData.year), desc(SMData.period)).first()

    if not latest:
        return SMSupersectorTimelineResponse(
            state_name=state.state_name if state else None,
            area_name=area.area_name if area else None,
            timeline=[],
            supersector_names=supersector_names
        )

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    if months_back >= 9999:
        start_year = 1939
        start_period_num = 1
    else:
        months_to_subtract = months_back
        while months_to_subtract > 0:
            if start_period_num > months_to_subtract:
                start_period_num -= months_to_subtract
                months_to_subtract = 0
            else:
                months_to_subtract -= start_period_num
                start_year -= 1
                start_period_num = 12

    start_period = f"M{start_period_num:02d}"

    # Get data
    all_series_ids = list(supersector_series.values())

    data = db.query(SMData).filter(
        SMData.series_id.in_(all_series_ids),
        SMData.period != 'M13',
        ((SMData.year > start_year) |
         ((SMData.year == start_year) & (SMData.period >= start_period)))
    ).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {}

        for code, series_id in supersector_series.items():
            if d.series_id == series_id:
                period_data[key][code] = float(d.value) if d.value else None

    # Build timeline
    timeline = []
    for (year, period) in sorted(period_data.keys()):
        timeline.append(SMSupersectorTimelinePoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            supersectors=period_data[(year, period)]
        ))

    return SMSupersectorTimelineResponse(
        state_name=state.state_name if state else None,
        area_name=area.area_name if area else None,
        timeline=timeline,
        supersector_names=supersector_names
    )


# ==================== Industry Analysis ====================

@router.get("/industries", response_model=SMIndustryAnalysisResponse)
def get_industries_analysis(
    state_code: str = Query(..., description="State code"),
    area_code: str = Query("00000", description="Area code"),
    supersector_code: Optional[str] = Query(None, description="Filter by supersector"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get employment breakdown by industry for a state/area"""

    state = db.query(SMState).filter(SMState.state_code == state_code).first()
    if not state:
        raise HTTPException(status_code=404, detail=f"State {state_code} not found")

    area = db.query(SMArea).filter(SMArea.area_code == area_code).first()

    # Build query for series
    query = db.query(SMSeries).filter(
        SMSeries.state_code == state_code,
        SMSeries.area_code == area_code,
        SMSeries.data_type_code == '01',
        SMSeries.is_active == True
    )

    if supersector_code:
        query = query.filter(SMSeries.supersector_code == supersector_code)

    series_list = query.limit(limit * 2).all()  # Get extra in case some have no data

    # Get industry names
    industry_codes = list(set(s.industry_code for s in series_list if s.industry_code))
    industries = db.query(SMIndustry).filter(SMIndustry.industry_code.in_(industry_codes)).all()
    industry_names = {i.industry_code: i.industry_name for i in industries}

    # Get supersector names
    supersector_codes = list(set(s.supersector_code for s in series_list if s.supersector_code))
    supersectors = db.query(SMSupersector).filter(SMSupersector.supersector_code.in_(supersector_codes)).all()
    supersector_names = {s.supersector_code: s.supersector_name for s in supersectors}

    industry_metrics = []
    last_updated = None

    for series in series_list:
        if len(industry_metrics) >= limit:
            break

        metrics = _calculate_employment_metrics(series.series_id, db)
        if not metrics:
            continue

        industry_metrics.append(SMIndustryMetric(
            industry_code=series.industry_code,
            industry_name=industry_names.get(series.industry_code, "Unknown"),
            supersector_code=series.supersector_code,
            supersector_name=supersector_names.get(series.supersector_code),
            series_id=series.series_id,
            employment=metrics["latest_value"],
            latest_date=metrics["latest_date"],
            month_over_month=metrics["mom_change"],
            month_over_month_pct=metrics["mom_pct"],
            year_over_year=metrics["yoy_change"],
            year_over_year_pct=metrics["yoy_pct"]
        ))

        if not last_updated:
            last_updated = metrics["latest_date"]

    # Sort by employment descending
    industry_metrics.sort(key=lambda x: x.employment if x.employment else 0, reverse=True)

    return SMIndustryAnalysisResponse(
        state_code=state_code,
        state_name=state.state_name,
        area_code=area_code,
        area_name=area.area_name if area else None,
        industries=industry_metrics,
        total_count=len(industry_metrics),
        last_updated=last_updated
    )


@router.get("/industries/timeline", response_model=SMIndustryTimelineResponse)
def get_industries_timeline(
    state_code: str = Query(..., description="State code"),
    area_code: str = Query("00000", description="Area code"),
    industry_codes: str = Query(..., description="Comma-separated industry codes"),
    months_back: int = Query(24, ge=1, le=9999),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for industry comparison"""

    state = db.query(SMState).filter(SMState.state_code == state_code).first()
    area = db.query(SMArea).filter(SMArea.area_code == area_code).first()

    codes = [c.strip() for c in industry_codes.split(',')]

    # Get series for each industry
    industry_series = {}
    industry_names = {}

    for code in codes:
        ind = db.query(SMIndustry).filter(SMIndustry.industry_code == code).first()
        if not ind:
            continue

        series = db.query(SMSeries).filter(
            SMSeries.state_code == state_code,
            SMSeries.area_code == area_code,
            SMSeries.industry_code == code,
            SMSeries.data_type_code == '01',
            SMSeries.is_active == True
        ).first()

        if series:
            industry_series[code] = series.series_id
            industry_names[code] = ind.industry_name

    if not industry_series:
        return SMIndustryTimelineResponse(
            state_name=state.state_name if state else None,
            area_name=area.area_name if area else None,
            timeline=[],
            industry_names={}
        )

    # Get latest data point
    first_series_id = next(iter(industry_series.values()))
    latest = db.query(SMData).filter(
        SMData.series_id == first_series_id,
        SMData.period != 'M13'
    ).order_by(desc(SMData.year), desc(SMData.period)).first()

    if not latest:
        return SMIndustryTimelineResponse(
            state_name=state.state_name if state else None,
            area_name=area.area_name if area else None,
            timeline=[],
            industry_names=industry_names
        )

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    if months_back >= 9999:
        start_year = 1990
        start_period_num = 1
    else:
        months_to_subtract = months_back
        while months_to_subtract > 0:
            if start_period_num > months_to_subtract:
                start_period_num -= months_to_subtract
                months_to_subtract = 0
            else:
                months_to_subtract -= start_period_num
                start_year -= 1
                start_period_num = 12

    start_period = f"M{start_period_num:02d}"

    # Get data
    all_series_ids = list(industry_series.values())

    data = db.query(SMData).filter(
        SMData.series_id.in_(all_series_ids),
        SMData.period != 'M13',
        ((SMData.year > start_year) |
         ((SMData.year == start_year) & (SMData.period >= start_period)))
    ).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {}

        for code, series_id in industry_series.items():
            if d.series_id == series_id:
                period_data[key][code] = float(d.value) if d.value else None

    # Build timeline
    timeline = []
    for (year, period) in sorted(period_data.keys()):
        timeline.append(SMIndustryTimelinePoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            industries=period_data[(year, period)]
        ))

    return SMIndustryTimelineResponse(
        state_name=state.state_name if state else None,
        area_name=area.area_name if area else None,
        timeline=timeline,
        industry_names=industry_names
    )


# ==================== Top Movers ====================

@router.get("/top-movers", response_model=SMTopMoversResponse)
def get_top_movers(
    period: str = Query("yoy", description="mom or yoy"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get states/metros with biggest employment changes"""

    # Get statewide Total Nonfarm series
    series_list = db.query(SMSeries).filter(
        SMSeries.area_code == '00000',
        SMSeries.supersector_code == '00',
        SMSeries.data_type_code == '01',
        SMSeries.is_active == True
    ).limit(100).all()

    movers = []
    last_updated = None

    state_names = {s.state_code: s.state_name for s in db.query(SMState).all()}

    for series in series_list:
        metrics = _calculate_employment_metrics(series.series_id, db)
        if not metrics:
            continue

        change = metrics["yoy_change"] if period == "yoy" else metrics["mom_change"]
        change_pct = metrics["yoy_pct"] if period == "yoy" else metrics["mom_pct"]

        if change_pct is None:
            continue

        movers.append(SMTopMover(
            series_id=series.series_id,
            state_code=series.state_code,
            state_name=state_names.get(series.state_code, "Unknown"),
            area_code=series.area_code,
            area_name="Statewide",
            employment=metrics["latest_value"],
            latest_date=metrics["latest_date"],
            change=change,
            change_pct=change_pct
        ))

        if not last_updated:
            last_updated = metrics["latest_date"]

    # Sort by change percent
    movers.sort(key=lambda x: x.change_pct or 0, reverse=True)
    gainers = movers[:limit]

    movers.sort(key=lambda x: x.change_pct or 0)
    losers = movers[:limit]

    return SMTopMoversResponse(
        period=period,
        gainers=gainers,
        losers=losers,
        last_updated=last_updated
    )
