"""
LA (Local Area Unemployment Statistics) Survey Explorer API Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database import get_data_db
from ....api.auth import get_current_user
from .la_schemas import (
    LADimensions, LAAreaItem, LAMeasureItem,
    LASeriesListResponse, LASeriesInfo,
    LADataResponse, LASeriesData, LADataPoint,
    LAOverviewResponse, UnemploymentMetric,
    LAStateAnalysisResponse, LAMetroAnalysisResponse,
    LAOverviewTimelineResponse, OverviewTimelinePoint,
    LAStateTimelineResponse, StateTimelinePoint,
    LAMetroTimelineResponse, MetroTimelinePoint
)
from ....data_models.bls_models import (
    LAArea, LAMeasure, LASeries, LAData, BLSPeriod,
    LNData  # For national unemployment from LN survey
)

router = APIRouter(prefix="/api/research/bls/la", tags=["LA Explorer"])


@router.get("/dimensions", response_model=LADimensions)
def get_la_dimensions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get all available dimensions for LA survey (areas and measures)"""

    # Get all areas
    areas = db.query(LAArea).order_by(LAArea.area_text).all()
    area_items = [
        LAAreaItem(
            area_code=a.area_code,
            area_name=a.area_text,
            area_type=a.area_type_code
        )
        for a in areas
    ]

    # Get all measures
    measures = db.query(LAMeasure).order_by(LAMeasure.measure_code).all()
    measure_items = [
        LAMeasureItem(
            measure_code=m.measure_code,
            measure_name=m.measure_text
        )
        for m in measures
    ]

    return LADimensions(areas=area_items, measures=measure_items)


@router.get("/series", response_model=LASeriesListResponse)
def get_la_series(
    area_code: Optional[str] = Query(None, description="Filter by area code"),
    measure_code: Optional[str] = Query(None, description="Filter by measure code"),
    seasonal_code: Optional[str] = Query(None, description="Filter by seasonal adjustment (S/U)"),
    active_only: bool = Query(True, description="Only return active series"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get LA series list with optional filters"""

    # Build query with joins
    query = db.query(
        LASeries,
        LAArea.area_text,
        LAMeasure.measure_text
    ).join(
        LAArea, LASeries.area_code == LAArea.area_code
    ).join(
        LAMeasure, LASeries.measure_code == LAMeasure.measure_code
    )

    # Apply filters
    if area_code:
        query = query.filter(LASeries.area_code == area_code)
    if measure_code:
        query = query.filter(LASeries.measure_code == measure_code)
    if seasonal_code:
        query = query.filter(LASeries.seasonal_code == seasonal_code)
    if active_only:
        query = query.filter(LASeries.is_active == True)

    # Get total count
    total = query.count()

    # Apply pagination
    results = query.order_by(LASeries.series_id).offset(offset).limit(limit).all()

    # Build response
    series_list = [
        LASeriesInfo(
            series_id=s.series_id,
            series_title=s.series_title,
            area_code=s.area_code,
            area_name=area_name,
            measure_code=s.measure_code,
            measure_name=measure_name,
            seasonal_code=s.seasonal_code,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active
        )
        for s, area_name, measure_name in results
    ]

    return LASeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_list
    )


@router.get("/series/{series_id}/data", response_model=LADataResponse)
def get_la_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None, description="Filter data from this year"),
    end_year: Optional[int] = Query(None, description="Filter data up to this year"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get time series data for a specific LA series"""

    # Get series metadata
    series = db.query(
        LASeries,
        LAArea.area_text,
        LAMeasure.measure_text
    ).join(
        LAArea, LASeries.area_code == LAArea.area_code
    ).join(
        LAMeasure, LASeries.measure_code == LAMeasure.measure_code
    ).filter(
        LASeries.series_id == series_id
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    s, area_name, measure_name = series

    # Get data points
    data_query = db.query(LAData).filter(LAData.series_id == series_id)

    if start_year:
        data_query = data_query.filter(LAData.year >= start_year)
    if end_year:
        data_query = data_query.filter(LAData.year <= end_year)

    data_points = data_query.order_by(LAData.year, LAData.period).all()

    # Get period names for formatting
    period_map = {p.period_code: p.period_name for p in db.query(BLSPeriod).all()}

    # Build data points with period names
    formatted_points = []
    for dp in data_points:
        period_name = period_map.get(dp.period, dp.period)
        if period_name and dp.year:
            period_display = f"{period_name} {dp.year}"
        else:
            period_display = f"{dp.period} {dp.year}"

        formatted_points.append(
            LADataPoint(
                year=dp.year,
                period=dp.period,
                period_name=period_display,
                value=float(dp.value) if dp.value is not None else None,
                footnote_codes=dp.footnote_codes
            )
        )

    series_data = LASeriesData(
        series_id=s.series_id,
        series_title=s.series_title,
        area_name=area_name,
        measure_name=measure_name,
        data_points=formatted_points
    )

    return LADataResponse(series=[series_data])


# ==================== Explorer Endpoints ====================

@router.get("/overview", response_model=LAOverviewResponse)
def get_overview(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get unemployment overview using official national data from LN survey"""

    # Use LN survey series for official national unemployment data (seasonally adjusted)
    # LNS14000000 = Unemployment rate
    # LNS13000000 = Unemployment level (thousands)
    # LNS12000000 = Employment level (thousands)
    # LNS11000000 = Labor force level (thousands)

    headline_series_id = "LNS14000000"  # Unemployment rate (SA)
    unemp_level_series_id = "LNS13000000"  # Unemployment level (SA)
    emp_level_series_id = "LNS12000000"  # Employment level (SA)
    labor_force_series_id = "LNS11000000"  # Labor force level (SA)

    # Get latest unemployment rate
    latest_rate = db.query(LNData).filter(
        LNData.series_id == headline_series_id
    ).order_by(LNData.year.desc(), LNData.period.desc()).first()

    if not latest_rate:
        raise HTTPException(status_code=404, detail="No national unemployment data found")

    # Get other measures for the same period
    unemp_level = db.query(LNData).filter(
        LNData.series_id == unemp_level_series_id,
        LNData.year == latest_rate.year,
        LNData.period == latest_rate.period
    ).first()

    emp_level = db.query(LNData).filter(
        LNData.series_id == emp_level_series_id,
        LNData.year == latest_rate.year,
        LNData.period == latest_rate.period
    ).first()

    labor_force = db.query(LNData).filter(
        LNData.series_id == labor_force_series_id,
        LNData.year == latest_rate.year,
        LNData.period == latest_rate.period
    ).first()

    # Calculate M/M change
    mom_change = None
    if latest_rate.period.startswith('M'):
        month_num = int(latest_rate.period[1:])
        if month_num > 1:
            prev_period = f"M{month_num-1:02d}"
            prev_year = latest_rate.year
        else:
            prev_period = "M12"
            prev_year = latest_rate.year - 1

        prev_data = db.query(LNData).filter(
            LNData.series_id == headline_series_id,
            LNData.year == prev_year,
            LNData.period == prev_period
        ).first()

        if prev_data and prev_data.value and latest_rate.value:
            mom_change = float(latest_rate.value) - float(prev_data.value)

    # Calculate Y/Y change
    yoy_change = None
    yoy_data = db.query(LNData).filter(
        LNData.series_id == headline_series_id,
        LNData.year == latest_rate.year - 1,
        LNData.period == latest_rate.period
    ).first()

    if yoy_data and yoy_data.value and latest_rate.value:
        yoy_change = float(latest_rate.value) - float(yoy_data.value)

    latest_date = f"{latest_rate.year}-{latest_rate.period}"

    national_metric = UnemploymentMetric(
        series_id=headline_series_id,
        area_code="US_NATIONAL",
        area_name="United States",
        area_type="National",
        unemployment_rate=float(latest_rate.value) if latest_rate.value else None,
        unemployment_level=float(unemp_level.value) if unemp_level and unemp_level.value else None,
        employment_level=float(emp_level.value) if emp_level and emp_level.value else None,
        labor_force=float(labor_force.value) if labor_force and labor_force.value else None,
        latest_date=latest_date,
        month_over_month=round(mom_change, 1) if mom_change is not None else None,
        year_over_year=round(yoy_change, 1) if yoy_change is not None else None
    )

    return LAOverviewResponse(
        national_unemployment=national_metric,
        last_updated=latest_date
    )


@router.get("/overview/timeline", response_model=LAOverviewTimelineResponse)
def get_overview_timeline(
    months_back: int = Query(24, ge=1, le=9999, description="Number of months to retrieve"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for national unemployment using official LN survey data"""

    # Use LN survey series for official national unemployment data (seasonally adjusted)
    headline_series_id = "LNS14000000"  # Unemployment rate (SA)
    unemp_level_series_id = "LNS13000000"  # Unemployment level (SA)
    labor_force_series_id = "LNS11000000"  # Labor force level (SA)

    # Get latest data point to determine time range
    latest = db.query(LNData).filter(
        LNData.series_id == headline_series_id
    ).order_by(LNData.year.desc(), LNData.period.desc()).first()

    if not latest:
        return LAOverviewTimelineResponse(
            area_name="United States",
            timeline=[]
        )

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    # Handle "All Time" (9999 months = effectively all data)
    if months_back >= 9999:
        start_year = 1948  # LN data goes back to 1948
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

    # Get unemployment rate data
    rate_data = db.query(LNData).filter(
        LNData.series_id == headline_series_id,
        ((LNData.year > start_year) |
         ((LNData.year == start_year) & (LNData.period >= start_period)))
    ).order_by(LNData.year, LNData.period).all()

    # Get unemployment level data
    unemp_level_data = db.query(LNData).filter(
        LNData.series_id == unemp_level_series_id,
        ((LNData.year > start_year) |
         ((LNData.year == start_year) & (LNData.period >= start_period)))
    ).all()
    unemp_level_map = {(d.year, d.period): float(d.value) for d in unemp_level_data if d.value is not None}

    # Get labor force data
    labor_force_data = db.query(LNData).filter(
        LNData.series_id == labor_force_series_id,
        ((LNData.year > start_year) |
         ((LNData.year == start_year) & (LNData.period >= start_period)))
    ).all()
    labor_force_map = {(d.year, d.period): float(d.value) for d in labor_force_data if d.value is not None}

    # Get period names
    period_map = {p.period_code: p.period_name for p in db.query(BLSPeriod).all()}

    # Build timeline
    timeline = []
    for d in rate_data:
        if d.value is not None:
            period_name = period_map.get(d.period, d.period)
            point = OverviewTimelinePoint(
                year=d.year,
                period=d.period,
                period_name=f"{period_name} {d.year}",
                unemployment_rate=float(d.value),
                unemployment_level=unemp_level_map.get((d.year, d.period)),
                labor_force=labor_force_map.get((d.year, d.period))
            )
            timeline.append(point)

    return LAOverviewTimelineResponse(
        area_name="United States",
        timeline=timeline
    )


@router.get("/states", response_model=LAStateAnalysisResponse)
def get_states_analysis(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get unemployment data for all states (latest snapshot)"""

    # Get all state area codes (area_type_code = 'A')
    states = db.query(LAArea).filter(LAArea.area_type_code == 'A').all()

    state_metrics = []

    for state in states:
        # Get unemployment rate series for this state
        series = db.query(LASeries).filter(
            LASeries.area_code == state.area_code,
            LASeries.measure_code == '03',
            LASeries.seasonal_code == 'S'
        ).first()

        if not series:
            series = db.query(LASeries).filter(
                LASeries.area_code == state.area_code,
                LASeries.measure_code == '03',
                LASeries.seasonal_code == 'U'
            ).first()

        if not series:
            continue

        # Get latest data point
        latest = db.query(LAData).filter(
            LAData.series_id == series.series_id
        ).order_by(LAData.year.desc(), LAData.period.desc()).first()

        if not latest:
            continue

        # Get other measures for this state
        other_series = db.query(LASeries).filter(
            LASeries.area_code == state.area_code,
            LASeries.measure_code.in_(['04', '05', '06']),
            LASeries.seasonal_code == series.seasonal_code
        ).all()

        other_measures = {}
        for os in other_series:
            data = db.query(LAData).filter(
                LAData.series_id == os.series_id,
                LAData.year == latest.year,
                LAData.period == latest.period
            ).first()
            if data:
                other_measures[os.measure_code] = float(data.value) if data.value else None

        # Calculate M/M and Y/Y changes
        mom_change = None
        yoy_change = None

        if latest.period.startswith('M'):
            month_num = int(latest.period[1:])
            if month_num > 1:
                prev_period = f"M{month_num-1:02d}"
                prev_year = latest.year
            else:
                prev_period = "M12"
                prev_year = latest.year - 1

            prev_data = db.query(LAData).filter(
                LAData.series_id == series.series_id,
                LAData.year == prev_year,
                LAData.period == prev_period
            ).first()

            if prev_data and prev_data.value and latest.value:
                mom_change = float(latest.value) - float(prev_data.value)

        # Y/Y change
        yoy_data = db.query(LAData).filter(
            LAData.series_id == series.series_id,
            LAData.year == latest.year - 1,
            LAData.period == latest.period
        ).first()

        if yoy_data and yoy_data.value and latest.value:
            yoy_change = float(latest.value) - float(yoy_data.value)

        metric = UnemploymentMetric(
            series_id=series.series_id,
            area_code=state.area_code,
            area_name=state.area_text,
            area_type="State",
            unemployment_rate=float(latest.value) if latest.value else None,
            unemployment_level=other_measures.get('04'),
            employment_level=other_measures.get('05'),
            labor_force=other_measures.get('06'),
            latest_date=f"{latest.year}-{latest.period}",
            month_over_month=mom_change,
            year_over_year=yoy_change
        )
        state_metrics.append(metric)

    # Sort by unemployment rate descending
    state_metrics.sort(key=lambda x: x.unemployment_rate if x.unemployment_rate else 0, reverse=True)

    # Get top 5 highest and lowest
    highest = [m.area_name for m in state_metrics[:5]]
    lowest = [m.area_name for m in state_metrics[-5:]]

    return LAStateAnalysisResponse(
        states=state_metrics,
        rankings={"highest": highest, "lowest": lowest}
    )


@router.get("/states/timeline", response_model=LAStateTimelineResponse)
def get_states_timeline(
    months_back: int = Query(24, ge=1, le=9999),
    state_codes: Optional[str] = Query(None, description="Comma-separated list of state area codes"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for state unemployment rates"""

    # Determine which states to include
    if state_codes:
        area_codes = [code.strip() for code in state_codes.split(',')]
        states = db.query(LAArea).filter(
            LAArea.area_code.in_(area_codes),
            LAArea.area_type_code == 'A'
        ).all()
    else:
        states = db.query(LAArea).filter(LAArea.area_type_code == 'A').all()

    # Get series for all states
    state_series = {}
    state_names = {}

    for state in states:
        series = db.query(LASeries).filter(
            LASeries.area_code == state.area_code,
            LASeries.measure_code == '03',
            LASeries.seasonal_code == 'S'
        ).first()

        if not series:
            series = db.query(LASeries).filter(
                LASeries.area_code == state.area_code,
                LASeries.measure_code == '03',
                LASeries.seasonal_code == 'U'
            ).first()

        if series:
            state_series[state.area_code] = series.series_id
            state_names[state.area_code] = state.area_text

    if not state_series:
        raise HTTPException(status_code=404, detail="No state series found")

    # Get latest data point to determine time range
    first_series_id = next(iter(state_series.values()))
    latest = db.query(LAData).filter(
        LAData.series_id == first_series_id
    ).order_by(LAData.year.desc(), LAData.period.desc()).first()

    if not latest:
        raise HTTPException(status_code=404, detail="No data found")

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    # Handle "All Time" (9999 months = effectively all data)
    if months_back >= 9999:
        start_year = 1976  # BLS LA data typically starts around here
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
    timeline_data = {}
    for area_code, series_id in state_series.items():
        data = db.query(LAData).filter(
            LAData.series_id == series_id,
            ((LAData.year > start_year) |
             ((LAData.year == start_year) & (LAData.period >= start_period)))
        ).order_by(LAData.year, LAData.period).all()

        for d in data:
            key = (d.year, d.period)
            if key not in timeline_data:
                timeline_data[key] = {}
            timeline_data[key][area_code] = float(d.value) if d.value else None

    # Get period names
    period_map = {p.period_code: p.period_name for p in db.query(BLSPeriod).all()}

    # Build timeline
    timeline = []
    for (year, period) in sorted(timeline_data.keys()):
        period_name = period_map.get(period, period)
        point = StateTimelinePoint(
            year=year,
            period=period,
            period_name=f"{period_name} {year}",
            states=timeline_data[(year, period)]
        )
        timeline.append(point)

    return LAStateTimelineResponse(
        timeline=timeline,
        state_names=state_names
    )


@router.get("/metros", response_model=LAMetroAnalysisResponse)
def get_metros_analysis(
    limit: int = Query(100, ge=1, le=500, description="Number of metro areas to return"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get unemployment data for metropolitan areas (latest snapshot)"""

    # Get metro areas (area_type_code = 'B')
    metros = db.query(LAArea).filter(
        LAArea.area_type_code == 'B'
    ).order_by(LAArea.area_text).limit(limit * 2).all()

    metro_metrics = []

    for metro in metros:
        # Get unemployment rate series (not seasonally adjusted - most metros don't have SA)
        series = db.query(LASeries).filter(
            LASeries.area_code == metro.area_code,
            LASeries.measure_code == '03',
            LASeries.seasonal_code == 'U'
        ).first()

        if not series:
            continue

        # Get latest data point
        latest = db.query(LAData).filter(
            LAData.series_id == series.series_id
        ).order_by(LAData.year.desc(), LAData.period.desc()).first()

        if not latest:
            continue

        # Get other measures
        other_series = db.query(LASeries).filter(
            LASeries.area_code == metro.area_code,
            LASeries.measure_code.in_(['04', '05', '06']),
            LASeries.seasonal_code == 'U'
        ).all()

        other_measures = {}
        for os in other_series:
            data = db.query(LAData).filter(
                LAData.series_id == os.series_id,
                LAData.year == latest.year,
                LAData.period == latest.period
            ).first()
            if data:
                other_measures[os.measure_code] = float(data.value) if data.value else None

        # Calculate M/M and Y/Y changes
        mom_change = None
        yoy_change = None

        if latest.period.startswith('M'):
            month_num = int(latest.period[1:])
            if month_num > 1:
                prev_period = f"M{month_num-1:02d}"
                prev_year = latest.year
            else:
                prev_period = "M12"
                prev_year = latest.year - 1

            prev_data = db.query(LAData).filter(
                LAData.series_id == series.series_id,
                LAData.year == prev_year,
                LAData.period == prev_period
            ).first()

            if prev_data and prev_data.value and latest.value:
                mom_change = float(latest.value) - float(prev_data.value)

        yoy_data = db.query(LAData).filter(
            LAData.series_id == series.series_id,
            LAData.year == latest.year - 1,
            LAData.period == latest.period
        ).first()

        if yoy_data and yoy_data.value and latest.value:
            yoy_change = float(latest.value) - float(yoy_data.value)

        metric = UnemploymentMetric(
            series_id=series.series_id,
            area_code=metro.area_code,
            area_name=metro.area_text,
            area_type="Metro",
            unemployment_rate=float(latest.value) if latest.value else None,
            unemployment_level=other_measures.get('04'),
            employment_level=other_measures.get('05'),
            labor_force=other_measures.get('06'),
            latest_date=f"{latest.year}-{latest.period}",
            month_over_month=mom_change,
            year_over_year=yoy_change
        )
        metro_metrics.append(metric)

    # Sort by labor force (larger metros first) and limit
    metro_metrics.sort(key=lambda x: x.labor_force if x.labor_force else 0, reverse=True)
    metro_metrics = metro_metrics[:limit]

    return LAMetroAnalysisResponse(
        metros=metro_metrics,
        total_count=len(metro_metrics)
    )


@router.get("/metros/timeline", response_model=LAMetroTimelineResponse)
def get_metros_timeline(
    months_back: int = Query(24, ge=1, le=9999),
    metro_codes: Optional[str] = Query(None, description="Comma-separated list of metro area codes"),
    limit: int = Query(10, ge=1, le=500, description="Number of metros if metro_codes not specified"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for metro area unemployment rates"""

    # Determine which metros to include
    if metro_codes:
        area_codes = [code.strip() for code in metro_codes.split(',')]
        metros = db.query(LAArea).filter(
            LAArea.area_code.in_(area_codes),
            LAArea.area_type_code == 'B'
        ).all()
    else:
        metros = db.query(LAArea).filter(
            LAArea.area_type_code == 'B'
        ).order_by(LAArea.area_text).limit(limit).all()

    # Get series for selected metros
    metro_series = {}
    metro_names = {}

    for metro in metros:
        series = db.query(LASeries).filter(
            LASeries.area_code == metro.area_code,
            LASeries.measure_code == '03',
            LASeries.seasonal_code == 'U'
        ).first()

        if series:
            metro_series[metro.area_code] = series.series_id
            metro_names[metro.area_code] = metro.area_text

    if not metro_series:
        raise HTTPException(status_code=404, detail="No metro series found")

    # Get latest data point to determine time range
    first_series_id = next(iter(metro_series.values()))
    latest = db.query(LAData).filter(
        LAData.series_id == first_series_id
    ).order_by(LAData.year.desc(), LAData.period.desc()).first()

    if not latest:
        raise HTTPException(status_code=404, detail="No data found")

    # Calculate start date
    start_year = latest.year
    start_period_num = int(latest.period[1:])

    # Handle "All Time" (9999 months = effectively all data)
    if months_back >= 9999:
        start_year = 1976  # BLS LA data typically starts around here
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
    timeline_data = {}
    for area_code, series_id in metro_series.items():
        data = db.query(LAData).filter(
            LAData.series_id == series_id,
            ((LAData.year > start_year) |
             ((LAData.year == start_year) & (LAData.period >= start_period)))
        ).order_by(LAData.year, LAData.period).all()

        for d in data:
            key = (d.year, d.period)
            if key not in timeline_data:
                timeline_data[key] = {}
            timeline_data[key][area_code] = float(d.value) if d.value else None

    # Get period names
    period_map = {p.period_code: p.period_name for p in db.query(BLSPeriod).all()}

    # Build timeline
    timeline = []
    for (year, period) in sorted(timeline_data.keys()):
        period_name = period_map.get(period, period)
        point = MetroTimelinePoint(
            year=year,
            period=period,
            period_name=f"{period_name} {year}",
            metros=timeline_data[(year, period)]
        )
        timeline.append(point)

    return LAMetroTimelineResponse(
        timeline=timeline,
        metro_names=metro_names
    )
