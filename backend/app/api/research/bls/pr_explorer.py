"""
PR (Major Sector Productivity and Costs) Explorer API

Provides endpoints for exploring productivity and cost measures for major economic sectors:
- Business Sector
- Nonfarm Business Sector
- Nonfinancial Corporations
- Manufacturing (Total, Durable Goods, Nondurable Goods)

Key measures:
- Labor productivity (output per hour)
- Unit labor costs
- Hourly compensation
- Real hourly compensation
- Output
- Hours worked

Data is quarterly and annual, from 1947-present.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import (
    PRSector, PRClass, PRMeasure, PRDuration, PRSeries, PRData
)
from .pr_schemas import (
    PRDimensions, PRSectorItem, PRClassItem, PRMeasureItem, PRDurationItem,
    PRSeriesInfo, PRSeriesListResponse,
    PRDataPoint, PRSeriesData, PRDataResponse,
    PRSectorMetrics, PROverviewResponse, PROverviewTimelinePoint, PROverviewTimelineResponse,
    PRMeasureMetric, PRSectorAnalysisResponse, PRMeasureTimelinePoint, PRMeasureTimelineResponse,
    PRSectorMeasureValue, PRMeasureComparisonResponse, PRMeasureComparisonTimelinePoint, PRMeasureComparisonTimelineResponse,
    PRClassMeasureValue, PRClassComparisonResponse, PRClassTimelinePoint, PRClassTimelineResponse,
    PRProductivityVsCosts, PRProductivityVsCostsResponse, PRProductivityVsCostsTimelinePoint, PRProductivityVsCostsTimelineResponse,
    PRManufacturingMetric, PRManufacturingComparisonResponse, PRManufacturingTimelinePoint, PRManufacturingTimelineResponse
)

router = APIRouter(prefix="/api/research/bls/pr", tags=["BLS PR Research"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def decimal_to_float(val) -> Optional[float]:
    """Convert Decimal to float, handling None"""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    return val


def get_period_name(year: int, period: str) -> str:
    """Convert period code to display name"""
    period_map = {
        'Q01': f'Q1 {year}',
        'Q02': f'Q2 {year}',
        'Q03': f'Q3 {year}',
        'Q04': f'Q4 {year}',
        'Q05': f'Annual {year}'
    }
    return period_map.get(period, f'{period} {year}')


# Key measure codes for productivity analysis
PRODUCTIVITY_MEASURES = {
    '01': 'Labor productivity',
    '02': 'Output',
    '03': 'Hours',
    '04': 'Hourly compensation',
    '07': 'Unit labor costs',
    '08': 'Unit nonlabor payments',
    '10': 'Real hourly compensation'
}

# Manufacturing sector codes
MANUFACTURING_SECTORS = ['3000', '3100', '3200']


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=PRDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering PR data"""
    # Get sectors
    sectors = db.execute(
        select(PRSector).order_by(PRSector.sort_sequence)
    ).scalars().all()

    # Get classes
    classes = db.execute(
        select(PRClass).order_by(PRClass.sort_sequence)
    ).scalars().all()

    # Get measures
    measures = db.execute(
        select(PRMeasure).order_by(PRMeasure.sort_sequence)
    ).scalars().all()

    # Get durations
    durations = db.execute(
        select(PRDuration).order_by(PRDuration.sort_sequence)
    ).scalars().all()

    return PRDimensions(
        sectors=[PRSectorItem(
            sector_code=s.sector_code,
            sector_name=s.sector_name
        ) for s in sectors],
        classes=[PRClassItem(
            class_code=c.class_code,
            class_text=c.class_text
        ) for c in classes],
        measures=[PRMeasureItem(
            measure_code=m.measure_code,
            measure_text=m.measure_text
        ) for m in measures],
        durations=[PRDurationItem(
            duration_code=d.duration_code,
            duration_text=d.duration_text
        ) for d in durations]
    )


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================

@router.get("/series", response_model=PRSeriesListResponse)
async def get_series(
    sector_code: Optional[str] = Query(None, description="Filter by sector code"),
    class_code: Optional[str] = Query(None, description="Filter by class code"),
    measure_code: Optional[str] = Query(None, description="Filter by measure code"),
    duration_code: Optional[str] = Query(None, description="Filter by duration code"),
    seasonal: Optional[str] = Query(None, description="Filter by seasonal adjustment"),
    search: Optional[str] = Query(None, description="Search in dimension names"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Get list of PR series with optional filters"""
    # Build query
    query = select(PRSeries)

    if sector_code:
        query = query.where(PRSeries.sector_code == sector_code)
    if class_code:
        query = query.where(PRSeries.class_code == class_code)
    if measure_code:
        query = query.where(PRSeries.measure_code == measure_code)
    if duration_code:
        query = query.where(PRSeries.duration_code == duration_code)
    if seasonal:
        query = query.where(PRSeries.seasonal == seasonal)

    # Get total count
    has_filters = any([sector_code, class_code, measure_code, duration_code, seasonal, search])
    if has_filters:
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar()
    else:
        total = db.execute(select(func.count()).select_from(PRSeries)).scalar()

    # Get paginated results
    query = query.order_by(PRSeries.series_id).limit(limit).offset(offset)
    series_list = db.execute(query).scalars().all()

    # Batch query: Get dimension names for all results
    sector_codes = list(set(s.sector_code for s in series_list if s.sector_code))
    class_codes = list(set(s.class_code for s in series_list if s.class_code))
    measure_codes = list(set(s.measure_code for s in series_list if s.measure_code))
    duration_codes = list(set(s.duration_code for s in series_list if s.duration_code))

    sector_names = {}
    class_names = {}
    measure_names = {}
    duration_names = {}

    if sector_codes:
        secs = db.execute(
            select(PRSector.sector_code, PRSector.sector_name)
            .where(PRSector.sector_code.in_(sector_codes))
        ).all()
        sector_names = {s.sector_code: s.sector_name for s in secs}

    if class_codes:
        cls = db.execute(
            select(PRClass.class_code, PRClass.class_text)
            .where(PRClass.class_code.in_(class_codes))
        ).all()
        class_names = {c.class_code: c.class_text for c in cls}

    if measure_codes:
        meas = db.execute(
            select(PRMeasure.measure_code, PRMeasure.measure_text)
            .where(PRMeasure.measure_code.in_(measure_codes))
        ).all()
        measure_names = {m.measure_code: m.measure_text for m in meas}

    if duration_codes:
        durs = db.execute(
            select(PRDuration.duration_code, PRDuration.duration_text)
            .where(PRDuration.duration_code.in_(duration_codes))
        ).all()
        duration_names = {d.duration_code: d.duration_text for d in durs}

    return PRSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=[PRSeriesInfo(
            series_id=s.series_id,
            seasonal=s.seasonal,
            sector_code=s.sector_code,
            sector_name=sector_names.get(s.sector_code),
            class_code=s.class_code,
            class_text=class_names.get(s.class_code),
            measure_code=s.measure_code,
            measure_text=measure_names.get(s.measure_code),
            duration_code=s.duration_code,
            duration_text=duration_names.get(s.duration_code),
            base_year=s.base_year,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active if s.is_active is not None else True
        ) for s in series_list]
    )


@router.get("/series/{series_id}/data", response_model=PRDataResponse)
async def get_series_data(
    series_id: str,
    years: int = Query(0, description="Number of years to retrieve (0=all)"),
    period_type: str = Query("quarterly", description="quarterly, annual, or all"),
    db: Session = Depends(get_data_db)
):
    """Get time series data for a specific PR series"""
    # Get series info
    series = db.execute(
        select(PRSeries).where(PRSeries.series_id == series_id)
    ).scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    # Get dimension names (batch query)
    sector_name = None
    class_text = None
    measure_text = None
    duration_text = None

    if series.sector_code:
        sec = db.execute(
            select(PRSector.sector_name)
            .where(PRSector.sector_code == series.sector_code)
        ).scalar_one_or_none()
        sector_name = sec

    if series.class_code:
        cls = db.execute(
            select(PRClass.class_text)
            .where(PRClass.class_code == series.class_code)
        ).scalar_one_or_none()
        class_text = cls

    if series.measure_code:
        meas = db.execute(
            select(PRMeasure.measure_text)
            .where(PRMeasure.measure_code == series.measure_code)
        ).scalar_one_or_none()
        measure_text = meas

    if series.duration_code:
        dur = db.execute(
            select(PRDuration.duration_text)
            .where(PRDuration.duration_code == series.duration_code)
        ).scalar_one_or_none()
        duration_text = dur

    # Build data query
    query = select(PRData).where(PRData.series_id == series_id)

    if years > 0:
        # Get latest year
        latest_year = db.execute(
            select(func.max(PRData.year)).where(PRData.series_id == series_id)
        ).scalar()
        if latest_year:
            query = query.where(PRData.year >= latest_year - years)

    # Filter by period type
    if period_type == 'quarterly':
        query = query.where(PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']))
    elif period_type == 'annual':
        query = query.where(PRData.period == 'Q05')

    query = query.order_by(PRData.year.asc(), PRData.period.asc())
    data_points = db.execute(query).scalars().all()

    return PRDataResponse(
        series=[PRSeriesData(
            series_id=series_id,
            sector_name=sector_name,
            class_text=class_text,
            measure_text=measure_text,
            duration_text=duration_text,
            data_points=[PRDataPoint(
                year=dp.year,
                period=dp.period,
                period_name=get_period_name(dp.year, dp.period),
                value=decimal_to_float(dp.value),
                footnote_codes=dp.footnote_codes
            ) for dp in data_points]
        )]
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=PROverviewResponse)
async def get_overview(
    class_code: str = Query("6", description="Class code (5=All persons, 6=Employees)"),
    period_type: str = Query("quarterly", description="quarterly or annual"),
    db: Session = Depends(get_data_db)
):
    """Get overview of productivity metrics across all sectors"""
    # Get latest data points
    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    # Get latest year/period
    latest = db.execute(
        select(PRData.year, PRData.period)
        .where(period_filter)
        .order_by(PRData.year.desc(), PRData.period.desc())
        .limit(1)
    ).first()

    if not latest:
        return PROverviewResponse(sectors=[], latest_year=None, latest_period=None)

    latest_year, latest_period = latest

    # Get all sectors
    sectors = db.execute(
        select(PRSector).order_by(PRSector.sort_sequence)
    ).scalars().all()

    sector_codes = [s.sector_code for s in sectors]
    sector_names = {s.sector_code: s.sector_name for s in sectors}

    # Correct PR measure codes:
    # Labor productivity=09, Unit labor costs=11, Output=05 (or 21 for Manufacturing), Hours=03, Compensation=10
    key_measures = ['09', '11', '05', '03', '10', '21']  # Include 21 (Real sectoral output) for Manufacturing
    # Duration codes: 1=% change YoY, 2=% change prev quarter, 3=Index
    duration_codes = ['1', '3']

    # Nonfinancial Corporations (8800) only has class_code '3', not '6'
    # So we query for both the requested class and '3' as fallback
    class_codes_to_query = [class_code]
    if class_code != '3':
        class_codes_to_query.append('3')

    # Batch query: Get all series for these combinations
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code, PRSeries.class_code, PRSeries.measure_code, PRSeries.duration_code)
        .where(and_(
            PRSeries.sector_code.in_(sector_codes),
            PRSeries.class_code.in_(class_codes_to_query),
            PRSeries.measure_code.in_(key_measures),
            PRSeries.duration_code.in_(duration_codes),
            PRSeries.seasonal == 'S'
        ))
    ).all()

    # Build series lookup: {(sector_code, measure_code, duration_code): series_id}
    # Prioritize the requested class_code over fallback class '3'
    series_map = {}
    for s in series_query:
        key = (s.sector_code, s.measure_code, s.duration_code)
        # Only set if not already set, or if this is the requested class_code (preferred)
        if key not in series_map or s.class_code == class_code:
            series_map[key] = s.series_id
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get data values for latest period
    data_query = db.execute(
        select(PRData.series_id, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year == latest_year,
            PRData.period == latest_period
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Helper to get value with fallback for Manufacturing output
    def get_value(sector_code: str, measure_code: str, duration_code: str) -> Optional[float]:
        series_id = series_map.get((sector_code, measure_code, duration_code))
        if series_id:
            return data_map.get(series_id)
        # Manufacturing sectors use measure 21 (Real sectoral output) instead of 05 (Value-added output)
        if measure_code == '05' and sector_code in ['3000', '3100', '3200']:
            series_id = series_map.get((sector_code, '21', duration_code))
            return data_map.get(series_id) if series_id else None
        return None

    # Build sector metrics (using correct PR measure codes)
    results = []
    for sector_code in sector_codes:
        results.append(PRSectorMetrics(
            sector_code=sector_code,
            sector_name=sector_names.get(sector_code),
            labor_productivity_index=get_value(sector_code, '09', '3'),
            labor_productivity_change=get_value(sector_code, '09', '1'),
            unit_labor_costs_index=get_value(sector_code, '11', '3'),
            unit_labor_costs_change=get_value(sector_code, '11', '1'),
            output_index=get_value(sector_code, '05', '3'),
            output_change=get_value(sector_code, '05', '1'),
            hours_index=get_value(sector_code, '03', '3'),
            hours_change=get_value(sector_code, '03', '1'),
            compensation_index=get_value(sector_code, '10', '3'),
            compensation_change=get_value(sector_code, '10', '1'),
            latest_year=latest_year,
            latest_period=latest_period
        ))

    return PROverviewResponse(
        sectors=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/overview/timeline", response_model=PROverviewTimelineResponse)
async def get_overview_timeline(
    measure: str = Query("labor_productivity", description="labor_productivity, unit_labor_costs, output, compensation"),
    duration: str = Query("index", description="index or pct_change"),
    class_code: str = Query("6", description="Class code"),
    period_type: str = Query("quarterly", description="quarterly or annual"),
    years: int = Query(0, description="Number of years (0=all)"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for overview charts"""
    # Correct PR measure codes (same for all sectors)
    measure_map = {
        'labor_productivity': '09',
        'unit_labor_costs': '11',
        'output': '05',
        'hours': '03',
        'compensation': '10'
    }
    measure_code = measure_map.get(measure, '09')
    duration_code = '3' if duration == 'index' else '1'

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    # Get latest year and calculate start year
    latest_year = db.execute(select(func.max(PRData.year))).scalar()
    start_year = latest_year - years if years > 0 else 1947

    # Get all sectors
    sectors = db.execute(select(PRSector).order_by(PRSector.sort_sequence)).scalars().all()
    sector_codes = [s.sector_code for s in sectors]
    sector_names = {s.sector_code: s.sector_name for s in sectors}

    # Nonfinancial Corporations (8800) only has class_code '3', not '6'
    class_codes_to_query = [class_code]
    if class_code != '3':
        class_codes_to_query.append('3')

    # Batch query: Get all series for these sectors
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code, PRSeries.class_code)
        .where(and_(
            PRSeries.sector_code.in_(sector_codes),
            PRSeries.class_code.in_(class_codes_to_query),
            PRSeries.measure_code == measure_code,
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    # Prioritize requested class_code over fallback
    series_map = {}
    for s in series_query:
        if s.sector_code not in series_map or s.class_code == class_code:
            series_map[s.sector_code] = s.series_id
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data for these series
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year >= start_year,
            period_filter
        ))
        .order_by(PRData.year.asc(), PRData.period.asc())
    ).all() if all_series_ids else []

    # Build data lookup: {(series_id, year, period): value}
    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}

    # Get unique year/period combinations
    year_periods = sorted(set((d.year, d.period) for d in data_query))

    # Build timeline
    timeline = []
    for year, period in year_periods:
        point = PROverviewTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            sectors={}
        )
        for sector_code in sector_codes:
            series_id = series_map.get(sector_code)
            if series_id:
                point.sectors[sector_code] = data_map.get((series_id, year, period))
            else:
                point.sectors[sector_code] = None
        timeline.append(point)

    return PROverviewTimelineResponse(
        measure=measure,
        duration=duration,
        timeline=timeline,
        sector_names=sector_names
    )


# ============================================================================
# SECTOR ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/sectors/{sector_code}", response_model=PRSectorAnalysisResponse)
async def get_sector_analysis(
    sector_code: str,
    class_code: str = Query("6", description="Class code"),
    period_type: str = Query("quarterly", description="quarterly or annual"),
    db: Session = Depends(get_data_db)
):
    """Get detailed analysis for a specific sector"""
    # Get sector info
    sector = db.execute(
        select(PRSector).where(PRSector.sector_code == sector_code)
    ).scalar_one_or_none()

    if not sector:
        raise HTTPException(status_code=404, detail=f"Sector {sector_code} not found")

    # Get class text
    class_text = None
    cls = db.execute(
        select(PRClass.class_text).where(PRClass.class_code == class_code)
    ).scalar_one_or_none()
    class_text = cls

    # Get latest period
    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    latest = db.execute(
        select(PRData.year, PRData.period)
        .where(period_filter)
        .order_by(PRData.year.desc(), PRData.period.desc())
        .limit(1)
    ).first()

    if not latest:
        return PRSectorAnalysisResponse(
            sector_code=sector_code, sector_name=sector.sector_name,
            class_code=class_code, class_text=class_text,
            measures=[], latest_year=None, latest_period=None
        )

    latest_year, latest_period = latest

    # Get all measures
    measures = db.execute(
        select(PRMeasure).order_by(PRMeasure.sort_sequence)
    ).scalars().all()

    measure_codes = [m.measure_code for m in measures]
    measure_names = {m.measure_code: m.measure_text for m in measures}

    # Duration codes: 1=YoY, 2=QoQ, 3=Index
    duration_codes = ['1', '2', '3']

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.measure_code, PRSeries.duration_code)
        .where(and_(
            PRSeries.sector_code == sector_code,
            PRSeries.class_code == class_code,
            PRSeries.measure_code.in_(measure_codes),
            PRSeries.duration_code.in_(duration_codes),
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {(s.measure_code, s.duration_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get data values
    data_query = db.execute(
        select(PRData.series_id, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year == latest_year,
            PRData.period == latest_period
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Helper
    def get_value(measure_code: str, duration_code: str) -> Optional[float]:
        series_id = series_map.get((measure_code, duration_code))
        return data_map.get(series_id) if series_id else None

    # Build measure metrics
    results = []
    for measure_code in measure_codes:
        measure_text = measure_names.get(measure_code)
        index_val = get_value(measure_code, '3')
        yoy_change = get_value(measure_code, '1')
        qoq_change = get_value(measure_code, '2')

        # Only include if we have at least some data
        if index_val is not None or yoy_change is not None or qoq_change is not None:
            results.append(PRMeasureMetric(
                measure_code=measure_code,
                measure_text=measure_text,
                index_value=index_val,
                yoy_change=yoy_change,
                qoq_change=qoq_change,
                latest_year=latest_year,
                latest_period=latest_period
            ))

    return PRSectorAnalysisResponse(
        sector_code=sector_code,
        sector_name=sector.sector_name,
        class_code=class_code,
        class_text=class_text,
        measures=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/sectors/{sector_code}/timeline", response_model=PRMeasureTimelineResponse)
async def get_sector_timeline(
    sector_code: str,
    duration: str = Query("index", description="index, yoy, or qoq"),
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    measure_codes: Optional[str] = Query(None, description="Comma-separated measure codes"),
    years: int = Query(0, description="Number of years (0=all)"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for measure comparison within a sector"""
    # Get sector name
    sector = db.execute(
        select(PRSector.sector_name).where(PRSector.sector_code == sector_code)
    ).scalar_one_or_none()
    sector_name = sector or sector_code

    duration_map = {'index': '3', 'yoy': '1', 'qoq': '2'}
    duration_code = duration_map.get(duration, '3')

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    latest_year = db.execute(select(func.max(PRData.year))).scalar()
    start_year = latest_year - years if years > 0 else 1947

    # Parse measure codes
    if measure_codes:
        meas_codes = measure_codes.split(',')
    else:
        meas_codes = ['01', '02', '03', '04', '07']  # Default key measures

    # Get measure names
    meas_query = db.execute(
        select(PRMeasure.measure_code, PRMeasure.measure_text)
        .where(PRMeasure.measure_code.in_(meas_codes))
    ).all()
    measure_names = {m.measure_code: m.measure_text for m in meas_query}

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.measure_code)
        .where(and_(
            PRSeries.sector_code == sector_code,
            PRSeries.class_code == class_code,
            PRSeries.measure_code.in_(meas_codes),
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {s.measure_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year >= start_year,
            period_filter
        ))
        .order_by(PRData.year.asc(), PRData.period.asc())
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}
    year_periods = sorted(set((d.year, d.period) for d in data_query))

    # Build timeline
    timeline = []
    for year, period in year_periods:
        point = PRMeasureTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            measures={}
        )
        for meas_code in meas_codes:
            series_id = series_map.get(meas_code)
            if series_id:
                point.measures[meas_code] = data_map.get((series_id, year, period))
            else:
                point.measures[meas_code] = None
        timeline.append(point)

    return PRMeasureTimelineResponse(
        sector_code=sector_code,
        sector_name=sector_name,
        duration=duration,
        timeline=timeline,
        measure_names=measure_names
    )


# ============================================================================
# MEASURE COMPARISON ENDPOINTS
# ============================================================================

@router.get("/measures/{measure_code}", response_model=PRMeasureComparisonResponse)
async def get_measure_comparison(
    measure_code: str,
    duration_code: str = Query("3", description="Duration code (1=YoY, 2=QoQ, 3=Index)"),
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    db: Session = Depends(get_data_db)
):
    """Compare a measure across all sectors"""
    # Get measure info
    measure = db.execute(
        select(PRMeasure).where(PRMeasure.measure_code == measure_code)
    ).scalar_one_or_none()

    if not measure:
        raise HTTPException(status_code=404, detail=f"Measure {measure_code} not found")

    # Get duration text
    duration_text = db.execute(
        select(PRDuration.duration_text).where(PRDuration.duration_code == duration_code)
    ).scalar_one_or_none() or duration_code

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    # Get latest period
    latest = db.execute(
        select(PRData.year, PRData.period)
        .where(period_filter)
        .order_by(PRData.year.desc(), PRData.period.desc())
        .limit(1)
    ).first()

    if not latest:
        return PRMeasureComparisonResponse(
            measure_code=measure_code, measure_text=measure.measure_text,
            duration_code=duration_code, duration_text=duration_text,
            sectors=[], latest_year=None, latest_period=None
        )

    latest_year, latest_period = latest
    prev_year = latest_year - 1

    # Get all sectors
    sectors = db.execute(select(PRSector).order_by(PRSector.sort_sequence)).scalars().all()
    sector_codes = [s.sector_code for s in sectors]
    sector_names = {s.sector_code: s.sector_name for s in sectors}

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code)
        .where(and_(
            PRSeries.sector_code.in_(sector_codes),
            PRSeries.class_code == class_code,
            PRSeries.measure_code == measure_code,
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {s.sector_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get current and previous year data
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year.in_([latest_year, prev_year]),
            PRData.period == latest_period
        ))
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year): decimal_to_float(d.value) for d in data_query}

    # Build results
    results = []
    for sector_code in sector_codes:
        series_id = series_map.get(sector_code)
        value = data_map.get((series_id, latest_year)) if series_id else None
        prev_value = data_map.get((series_id, prev_year)) if series_id else None

        yoy_change = None
        if value is not None and prev_value is not None and prev_value != 0:
            yoy_change = round(((value - prev_value) / abs(prev_value)) * 100, 2)

        results.append(PRSectorMeasureValue(
            sector_code=sector_code,
            sector_name=sector_names.get(sector_code),
            value=value,
            yoy_change=yoy_change
        ))

    return PRMeasureComparisonResponse(
        measure_code=measure_code,
        measure_text=measure.measure_text,
        duration_code=duration_code,
        duration_text=duration_text,
        sectors=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/measures/{measure_code}/timeline", response_model=PRMeasureComparisonTimelineResponse)
async def get_measure_comparison_timeline(
    measure_code: str,
    duration_code: str = Query("3"),
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    sector_codes: Optional[str] = Query(None, description="Comma-separated sector codes"),
    years: int = Query(0, description="Number of years (0=all)"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for comparing a measure across sectors"""
    # Get measure info
    measure = db.execute(
        select(PRMeasure.measure_text).where(PRMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure or measure_code

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    latest_year = db.execute(select(func.max(PRData.year))).scalar()
    start_year = latest_year - years if years > 0 else 1947

    # Parse sector codes
    if sector_codes:
        sec_codes = sector_codes.split(',')
    else:
        # Default: all sectors
        sectors = db.execute(select(PRSector.sector_code)).scalars().all()
        sec_codes = sectors

    # Get sector names
    sec_query = db.execute(
        select(PRSector.sector_code, PRSector.sector_name)
        .where(PRSector.sector_code.in_(sec_codes))
    ).all()
    sector_names = {s.sector_code: s.sector_name for s in sec_query}

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code)
        .where(and_(
            PRSeries.sector_code.in_(sec_codes),
            PRSeries.class_code == class_code,
            PRSeries.measure_code == measure_code,
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {s.sector_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year >= start_year,
            period_filter
        ))
        .order_by(PRData.year.asc(), PRData.period.asc())
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}
    year_periods = sorted(set((d.year, d.period) for d in data_query))

    # Build timeline
    timeline = []
    for year, period in year_periods:
        point = PRMeasureComparisonTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            sectors={}
        )
        for sec_code in sec_codes:
            series_id = series_map.get(sec_code)
            if series_id:
                point.sectors[sec_code] = data_map.get((series_id, year, period))
            else:
                point.sectors[sec_code] = None
        timeline.append(point)

    return PRMeasureComparisonTimelineResponse(
        measure_code=measure_code,
        measure_text=measure_text,
        timeline=timeline,
        sector_names=sector_names
    )


# ============================================================================
# CLASS COMPARISON ENDPOINTS
# ============================================================================

@router.get("/classes/compare", response_model=PRClassComparisonResponse)
async def get_class_comparison(
    sector_code: str = Query("8500", description="Sector code"),
    measure_code: str = Query("01", description="Measure code"),
    period_type: str = Query("quarterly"),
    db: Session = Depends(get_data_db)
):
    """Compare measures between worker classes for a sector"""
    # Get sector and measure info
    sector = db.execute(
        select(PRSector.sector_name).where(PRSector.sector_code == sector_code)
    ).scalar_one_or_none()
    sector_name = sector or sector_code

    measure = db.execute(
        select(PRMeasure.measure_text).where(PRMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure or measure_code

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    # Get latest period
    latest = db.execute(
        select(PRData.year, PRData.period)
        .where(period_filter)
        .order_by(PRData.year.desc(), PRData.period.desc())
        .limit(1)
    ).first()

    if not latest:
        return PRClassComparisonResponse(
            sector_code=sector_code, sector_name=sector_name,
            measure_code=measure_code, measure_text=measure_text,
            classes=[], latest_year=None, latest_period=None
        )

    latest_year, latest_period = latest

    # Get all classes
    classes = db.execute(select(PRClass).order_by(PRClass.sort_sequence)).scalars().all()
    class_codes = [c.class_code for c in classes]
    class_names = {c.class_code: c.class_text for c in classes}

    # Duration codes
    duration_codes = ['1', '2', '3']

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.class_code, PRSeries.duration_code)
        .where(and_(
            PRSeries.sector_code == sector_code,
            PRSeries.class_code.in_(class_codes),
            PRSeries.measure_code == measure_code,
            PRSeries.duration_code.in_(duration_codes),
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {(s.class_code, s.duration_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get data values
    data_query = db.execute(
        select(PRData.series_id, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year == latest_year,
            PRData.period == latest_period
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Build results
    results = []
    for class_code in class_codes:
        index_series = series_map.get((class_code, '3'))
        yoy_series = series_map.get((class_code, '1'))
        qoq_series = series_map.get((class_code, '2'))

        results.append(PRClassMeasureValue(
            class_code=class_code,
            class_text=class_names.get(class_code),
            index_value=data_map.get(index_series) if index_series else None,
            yoy_change=data_map.get(yoy_series) if yoy_series else None,
            qoq_change=data_map.get(qoq_series) if qoq_series else None
        ))

    return PRClassComparisonResponse(
        sector_code=sector_code,
        sector_name=sector_name,
        measure_code=measure_code,
        measure_text=measure_text,
        classes=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/classes/timeline", response_model=PRClassTimelineResponse)
async def get_class_timeline(
    sector_code: str = Query("8500"),
    measure_code: str = Query("01"),
    duration_code: str = Query("3"),
    period_type: str = Query("quarterly"),
    years: int = Query(0, description="Number of years (0=all)"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for comparing classes"""
    # Get sector and measure names
    sector = db.execute(
        select(PRSector.sector_name).where(PRSector.sector_code == sector_code)
    ).scalar_one_or_none()
    sector_name = sector or sector_code

    measure = db.execute(
        select(PRMeasure.measure_text).where(PRMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure or measure_code

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    latest_year = db.execute(select(func.max(PRData.year))).scalar()
    start_year = latest_year - years if years > 0 else 1947

    # Get all classes
    classes = db.execute(select(PRClass).order_by(PRClass.sort_sequence)).scalars().all()
    class_codes = [c.class_code for c in classes]
    class_names = {c.class_code: c.class_text for c in classes}

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.class_code)
        .where(and_(
            PRSeries.sector_code == sector_code,
            PRSeries.class_code.in_(class_codes),
            PRSeries.measure_code == measure_code,
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {s.class_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year >= start_year,
            period_filter
        ))
        .order_by(PRData.year.asc(), PRData.period.asc())
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}
    year_periods = sorted(set((d.year, d.period) for d in data_query))

    # Build timeline
    timeline = []
    for year, period in year_periods:
        point = PRClassTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            classes={}
        )
        for class_code in class_codes:
            series_id = series_map.get(class_code)
            if series_id:
                point.classes[class_code] = data_map.get((series_id, year, period))
            else:
                point.classes[class_code] = None
        timeline.append(point)

    return PRClassTimelineResponse(
        sector_code=sector_code,
        sector_name=sector_name,
        measure_code=measure_code,
        measure_text=measure_text,
        timeline=timeline,
        class_names=class_names
    )


# ============================================================================
# PRODUCTIVITY VS COSTS ENDPOINTS
# ============================================================================

@router.get("/productivity-vs-costs", response_model=PRProductivityVsCostsResponse)
async def get_productivity_vs_costs(
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    db: Session = Depends(get_data_db)
):
    """Get productivity vs costs analysis for all sectors"""
    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    # Get latest period
    latest = db.execute(
        select(PRData.year, PRData.period)
        .where(period_filter)
        .order_by(PRData.year.desc(), PRData.period.desc())
        .limit(1)
    ).first()

    if not latest:
        return PRProductivityVsCostsResponse(analysis=[], latest_year=None, latest_period=None)

    latest_year, latest_period = latest

    # Get all sectors
    sectors = db.execute(select(PRSector).order_by(PRSector.sort_sequence)).scalars().all()
    sector_codes = [s.sector_code for s in sectors]
    sector_names = {s.sector_code: s.sector_name for s in sectors}

    # Key measures: 01=productivity, 07=unit labor costs, 04=hourly compensation, 10=real compensation
    measures = ['01', '04', '07', '10']
    # Duration codes: 1=YoY, 3=Index
    durations = ['1', '3']

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code, PRSeries.measure_code, PRSeries.duration_code)
        .where(and_(
            PRSeries.sector_code.in_(sector_codes),
            PRSeries.class_code == class_code,
            PRSeries.measure_code.in_(measures),
            PRSeries.duration_code.in_(durations),
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {(s.sector_code, s.measure_code, s.duration_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get data values
    data_query = db.execute(
        select(PRData.series_id, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year == latest_year,
            PRData.period == latest_period
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Helper
    def get_value(sector_code: str, measure_code: str, duration_code: str) -> Optional[float]:
        series_id = series_map.get((sector_code, measure_code, duration_code))
        return data_map.get(series_id) if series_id else None

    # Build results
    results = []
    for sector_code in sector_codes:
        results.append(PRProductivityVsCosts(
            sector_code=sector_code,
            sector_name=sector_names.get(sector_code),
            productivity_index=get_value(sector_code, '01', '3'),
            productivity_change=get_value(sector_code, '01', '1'),
            unit_labor_costs_index=get_value(sector_code, '07', '3'),
            unit_labor_costs_change=get_value(sector_code, '07', '1'),
            hourly_compensation_index=get_value(sector_code, '04', '3'),
            hourly_compensation_change=get_value(sector_code, '04', '1'),
            real_compensation_index=get_value(sector_code, '10', '3'),
            real_compensation_change=get_value(sector_code, '10', '1')
        ))

    return PRProductivityVsCostsResponse(
        analysis=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/productivity-vs-costs/timeline", response_model=PRProductivityVsCostsTimelineResponse)
async def get_productivity_vs_costs_timeline(
    sector_code: str = Query("8500"),
    duration: str = Query("index", description="index or pct_change"),
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    years: int = Query(0, description="Number of years (0=all)"),
    db: Session = Depends(get_data_db)
):
    """Get timeline for productivity vs costs comparison"""
    # Get sector name
    sector = db.execute(
        select(PRSector.sector_name).where(PRSector.sector_code == sector_code)
    ).scalar_one_or_none()
    sector_name = sector or sector_code

    duration_code = '3' if duration == 'index' else '1'
    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    latest_year = db.execute(select(func.max(PRData.year))).scalar()
    start_year = latest_year - years if years > 0 else 1947

    # Key measures
    measures = ['01', '04', '07']

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.measure_code)
        .where(and_(
            PRSeries.sector_code == sector_code,
            PRSeries.class_code == class_code,
            PRSeries.measure_code.in_(measures),
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {s.measure_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year >= start_year,
            period_filter
        ))
        .order_by(PRData.year.asc(), PRData.period.asc())
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}
    year_periods = sorted(set((d.year, d.period) for d in data_query))

    # Build timeline
    timeline = []
    for year, period in year_periods:
        productivity_sid = series_map.get('01')
        ulc_sid = series_map.get('07')
        comp_sid = series_map.get('04')

        timeline.append(PRProductivityVsCostsTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            productivity=data_map.get((productivity_sid, year, period)) if productivity_sid else None,
            unit_labor_costs=data_map.get((ulc_sid, year, period)) if ulc_sid else None,
            hourly_compensation=data_map.get((comp_sid, year, period)) if comp_sid else None
        ))

    return PRProductivityVsCostsTimelineResponse(
        sector_code=sector_code,
        sector_name=sector_name,
        duration=duration,
        timeline=timeline
    )


# ============================================================================
# MANUFACTURING COMPARISON ENDPOINTS
# ============================================================================

@router.get("/manufacturing", response_model=PRManufacturingComparisonResponse)
async def get_manufacturing_comparison(
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    db: Session = Depends(get_data_db)
):
    """Compare manufacturing subsectors (total, durable, nondurable)"""
    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    # Get latest period
    latest = db.execute(
        select(PRData.year, PRData.period)
        .where(period_filter)
        .order_by(PRData.year.desc(), PRData.period.desc())
        .limit(1)
    ).first()

    if not latest:
        return PRManufacturingComparisonResponse(manufacturing_sectors=[], latest_year=None, latest_period=None)

    latest_year, latest_period = latest

    # Get manufacturing sectors
    sectors = db.execute(
        select(PRSector)
        .where(PRSector.sector_code.in_(MANUFACTURING_SECTORS))
        .order_by(PRSector.sort_sequence)
    ).scalars().all()

    sector_codes = [s.sector_code for s in sectors]
    sector_names = {s.sector_code: s.sector_name for s in sectors}

    # Key measures: 01=productivity, 07=unit labor costs, 02=output
    measures = ['01', '02', '07']
    durations = ['1', '3']

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code, PRSeries.measure_code, PRSeries.duration_code)
        .where(and_(
            PRSeries.sector_code.in_(sector_codes),
            PRSeries.class_code == class_code,
            PRSeries.measure_code.in_(measures),
            PRSeries.duration_code.in_(durations),
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {(s.sector_code, s.measure_code, s.duration_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get data values
    data_query = db.execute(
        select(PRData.series_id, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year == latest_year,
            PRData.period == latest_period
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Helper
    def get_value(sector_code: str, measure_code: str, duration_code: str) -> Optional[float]:
        series_id = series_map.get((sector_code, measure_code, duration_code))
        return data_map.get(series_id) if series_id else None

    # Build results
    results = []
    for sector_code in sector_codes:
        results.append(PRManufacturingMetric(
            sector_code=sector_code,
            sector_name=sector_names.get(sector_code),
            productivity_index=get_value(sector_code, '01', '3'),
            productivity_change=get_value(sector_code, '01', '1'),
            unit_labor_costs_index=get_value(sector_code, '07', '3'),
            unit_labor_costs_change=get_value(sector_code, '07', '1'),
            output_index=get_value(sector_code, '02', '3'),
            output_change=get_value(sector_code, '02', '1')
        ))

    return PRManufacturingComparisonResponse(
        manufacturing_sectors=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/manufacturing/timeline", response_model=PRManufacturingTimelineResponse)
async def get_manufacturing_timeline(
    measure: str = Query("productivity", description="productivity, unit_labor_costs, output"),
    duration: str = Query("index", description="index or pct_change"),
    class_code: str = Query("6"),
    period_type: str = Query("quarterly"),
    years: int = Query(0, description="Number of years (0=all)"),
    db: Session = Depends(get_data_db)
):
    """Get timeline for manufacturing subsector comparison"""
    measure_map = {'productivity': '01', 'unit_labor_costs': '07', 'output': '02'}
    measure_code = measure_map.get(measure, '01')
    duration_code = '3' if duration == 'index' else '1'

    period_filter = PRData.period.in_(['Q01', 'Q02', 'Q03', 'Q04']) if period_type == 'quarterly' else PRData.period == 'Q05'

    latest_year = db.execute(select(func.max(PRData.year))).scalar()
    start_year = latest_year - years if years > 0 else 1947

    # Get manufacturing sectors
    sectors = db.execute(
        select(PRSector)
        .where(PRSector.sector_code.in_(MANUFACTURING_SECTORS))
        .order_by(PRSector.sort_sequence)
    ).scalars().all()

    sector_codes = [s.sector_code for s in sectors]
    sector_names = {s.sector_code: s.sector_name for s in sectors}

    # Batch query: Get all series
    series_query = db.execute(
        select(PRSeries.series_id, PRSeries.sector_code)
        .where(and_(
            PRSeries.sector_code.in_(sector_codes),
            PRSeries.class_code == class_code,
            PRSeries.measure_code == measure_code,
            PRSeries.duration_code == duration_code,
            PRSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {s.sector_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(PRData.series_id, PRData.year, PRData.period, PRData.value)
        .where(and_(
            PRData.series_id.in_(all_series_ids),
            PRData.year >= start_year,
            period_filter
        ))
        .order_by(PRData.year.asc(), PRData.period.asc())
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}
    year_periods = sorted(set((d.year, d.period) for d in data_query))

    # Build timeline
    timeline = []
    for year, period in year_periods:
        point = PRManufacturingTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            sectors={}
        )
        for sector_code in sector_codes:
            series_id = series_map.get(sector_code)
            if series_id:
                point.sectors[sector_code] = data_map.get((series_id, year, period))
            else:
                point.sectors[sector_code] = None
        timeline.append(point)

    return PRManufacturingTimelineResponse(
        measure=measure,
        timeline=timeline,
        sector_names=sector_names
    )
