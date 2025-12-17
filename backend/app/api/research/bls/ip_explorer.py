"""
IP (Industry Productivity) Explorer API

Provides endpoints for exploring Industry Productivity data including:
- 21 economic sectors (Agriculture, Mining, Manufacturing, etc.)
- 800+ industries (NAICS classification)
- Labor productivity, unit labor costs, output, hours, employment
- Index values (2017=100) and annual percent changes

Data is annual, updated throughout the year.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import (
    IPSector, IPIndustry, IPMeasure, IPDuration, IPType, IPArea, IPSeries, IPData
)
from .ip_schemas import (
    IPDimensions, IPSectorItem, IPIndustryItem, IPMeasureItem, IPDurationItem, IPTypeItem, IPAreaItem,
    IPSeriesInfo, IPSeriesListResponse,
    IPDataPoint, IPSeriesData, IPDataResponse,
    IPSectorSummary, IPOverviewResponse, IPOverviewTimelinePoint, IPOverviewTimelineResponse,
    IPIndustryMetric, IPSectorAnalysisResponse, IPSectorTimelinePoint, IPSectorTimelineResponse,
    IPMeasureValue, IPIndustryAnalysisResponse, IPIndustryTimelinePoint, IPIndustryTimelineResponse,
    IPIndustryMeasureMetric, IPMeasureComparisonResponse, IPMeasureTimelinePoint, IPMeasureTimelineResponse,
    IPTopIndustry, IPTopRankingsResponse,
    IPProductivityVsCostsMetric, IPProductivityVsCostsResponse,
    IPProductivityVsCostsTimelinePoint, IPProductivityVsCostsTimelineResponse
)

router = APIRouter(prefix="/api/research/bls/ip", tags=["BLS IP Research"])


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


def get_period_name(period: str, year: int) -> str:
    """Convert period code to display name"""
    if period == 'A01':
        return str(year)
    return f"{year} {period}"


# Key measure codes
MEASURE_LABOR_PRODUCTIVITY = 'L00'  # Labor productivity index
MEASURE_OUTPUT = 'T01'  # Real sectoral output index
MEASURE_HOURS = 'L01'  # Hours worked index
MEASURE_EMPLOYMENT = 'W01'  # Employment index
MEASURE_UNIT_LABOR_COSTS = 'U10'  # Unit labor costs index
MEASURE_COMPENSATION = 'U11'  # Labor compensation index
MEASURE_OUTPUT_PER_WORKER = 'W00'  # Output per worker index

# Key measures for analysis
KEY_MEASURES = [
    MEASURE_LABOR_PRODUCTIVITY,
    MEASURE_OUTPUT,
    MEASURE_HOURS,
    MEASURE_EMPLOYMENT,
    MEASURE_UNIT_LABOR_COSTS,
    MEASURE_COMPENSATION
]

# Duration codes
DURATION_INDEX = '0'  # Index value
DURATION_PERCENT_CHANGE = '1'  # Annual percent change


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=IPDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering IP data"""
    # Sectors
    sectors = db.execute(
        select(IPSector).order_by(IPSector.sector_code)
    ).scalars().all()

    # Industries - only selectable ones at reasonable display level
    industries = db.execute(
        select(IPIndustry)
        .where(IPIndustry.selectable == 'T')
        .order_by(IPIndustry.sort_sequence)
    ).scalars().all()

    # Measures
    measures = db.execute(
        select(IPMeasure)
        .where(IPMeasure.selectable == 'T')
        .order_by(IPMeasure.sort_sequence)
    ).scalars().all()

    # Durations
    durations = db.execute(
        select(IPDuration).order_by(IPDuration.duration_code)
    ).scalars().all()

    # Types
    types = db.execute(
        select(IPType).order_by(IPType.type_code)
    ).scalars().all()

    # Areas
    areas = db.execute(
        select(IPArea)
        .where(IPArea.selectable == 'T')
        .order_by(IPArea.sort_sequence)
    ).scalars().all()

    return IPDimensions(
        sectors=[IPSectorItem(sector_code=s.sector_code, sector_text=s.sector_text) for s in sectors],
        industries=[IPIndustryItem(
            industry_code=i.industry_code,
            naics_code=i.naics_code,
            industry_text=i.industry_text,
            display_level=i.display_level,
            selectable=i.selectable == 'T'
        ) for i in industries],
        measures=[IPMeasureItem(
            measure_code=m.measure_code,
            measure_text=m.measure_text,
            display_level=m.display_level,
            selectable=m.selectable == 'T'
        ) for m in measures],
        durations=[IPDurationItem(duration_code=d.duration_code, duration_text=d.duration_text) for d in durations],
        types=[IPTypeItem(type_code=t.type_code, type_text=t.type_text) for t in types],
        areas=[IPAreaItem(area_code=a.area_code, area_text=a.area_text) for a in areas]
    )


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================

@router.get("/series", response_model=IPSeriesListResponse)
async def get_series(
    sector_code: Optional[str] = Query(None, description="Sector code filter"),
    industry_code: Optional[str] = Query(None, description="Industry code filter"),
    measure_code: Optional[str] = Query(None, description="Measure code filter"),
    duration_code: Optional[str] = Query(None, description="Duration code filter (0=Index, 1=% change)"),
    search: Optional[str] = Query(None, description="Search in series title"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db)
):
    """Get list of IP series with optional filters"""
    # Build base query with joins for dimension names
    query = (
        select(
            IPSeries,
            IPSector.sector_text,
            IPIndustry.industry_text,
            IPIndustry.naics_code,
            IPMeasure.measure_text,
            IPDuration.duration_text,
            IPType.type_text,
            IPArea.area_text
        )
        .outerjoin(IPSector, IPSeries.sector_code == IPSector.sector_code)
        .outerjoin(IPIndustry, IPSeries.industry_code == IPIndustry.industry_code)
        .outerjoin(IPMeasure, IPSeries.measure_code == IPMeasure.measure_code)
        .outerjoin(IPDuration, IPSeries.duration_code == IPDuration.duration_code)
        .outerjoin(IPType, IPSeries.type_code == IPType.type_code)
        .outerjoin(IPArea, IPSeries.area_code == IPArea.area_code)
        .where(IPSeries.is_active == True)
    )

    # Apply filters
    if sector_code:
        query = query.where(IPSeries.sector_code == sector_code)
    if industry_code:
        query = query.where(IPSeries.industry_code == industry_code)
    if measure_code:
        query = query.where(IPSeries.measure_code == measure_code)
    if duration_code:
        query = query.where(IPSeries.duration_code == duration_code)
    if search:
        query = query.where(IPSeries.series_title.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    total = db.execute(count_query).scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(IPSeries.series_id).offset(offset).limit(limit)

    results = db.execute(query).all()

    series_list = []
    for row in results:
        s = row[0]
        series_list.append(IPSeriesInfo(
            series_id=s.series_id,
            seasonal=s.seasonal,
            sector_code=s.sector_code,
            sector_text=row[1],
            industry_code=s.industry_code,
            industry_text=row[2],
            naics_code=row[3],
            measure_code=s.measure_code,
            measure_text=row[4],
            duration_code=s.duration_code,
            duration_text=row[5],
            type_code=s.type_code,
            type_text=row[6],
            area_code=s.area_code,
            area_text=row[7],
            base_year=s.base_year,
            series_title=s.series_title,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active
        ))

    return IPSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_list
    )


@router.get("/series/{series_id}/data", response_model=IPDataResponse)
async def get_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    db: Session = Depends(get_data_db)
):
    """Get time series data for a specific IP series"""
    # Get series info with joins
    series_query = (
        select(
            IPSeries,
            IPSector.sector_text,
            IPIndustry.industry_text,
            IPIndustry.naics_code,
            IPMeasure.measure_text,
            IPDuration.duration_text,
            IPType.type_text,
            IPArea.area_text
        )
        .outerjoin(IPSector, IPSeries.sector_code == IPSector.sector_code)
        .outerjoin(IPIndustry, IPSeries.industry_code == IPIndustry.industry_code)
        .outerjoin(IPMeasure, IPSeries.measure_code == IPMeasure.measure_code)
        .outerjoin(IPDuration, IPSeries.duration_code == IPDuration.duration_code)
        .outerjoin(IPType, IPSeries.type_code == IPType.type_code)
        .outerjoin(IPArea, IPSeries.area_code == IPArea.area_code)
        .where(IPSeries.series_id == series_id)
    )

    result = db.execute(series_query).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    s = result[0]
    series_info = IPSeriesInfo(
        series_id=s.series_id,
        seasonal=s.seasonal,
        sector_code=s.sector_code,
        sector_text=result[1],
        industry_code=s.industry_code,
        industry_text=result[2],
        naics_code=result[3],
        measure_code=s.measure_code,
        measure_text=result[4],
        duration_code=s.duration_code,
        duration_text=result[5],
        type_code=s.type_code,
        type_text=result[6],
        area_code=s.area_code,
        area_text=result[7],
        base_year=s.base_year,
        series_title=s.series_title,
        begin_year=s.begin_year,
        begin_period=s.begin_period,
        end_year=s.end_year,
        end_period=s.end_period,
        is_active=s.is_active
    )

    # Get data points
    data_query = select(IPData).where(IPData.series_id == series_id)
    if start_year:
        data_query = data_query.where(IPData.year >= start_year)
    if end_year:
        data_query = data_query.where(IPData.year <= end_year)
    data_query = data_query.order_by(IPData.year, IPData.period)

    data_rows = db.execute(data_query).scalars().all()

    data_points = [
        IPDataPoint(
            year=d.year,
            period=d.period,
            period_name=get_period_name(d.period, d.year),
            value=decimal_to_float(d.value),
            footnote_codes=d.footnote_codes
        )
        for d in data_rows
    ]

    return IPDataResponse(
        series=[IPSeriesData(
            series_id=series_id,
            series_info=series_info,
            data=data_points
        )]
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=IPOverviewResponse)
async def get_overview(
    year: Optional[int] = Query(None, description="Year for overview (defaults to latest)"),
    db: Session = Depends(get_data_db)
):
    """Get overview of IP data with key metrics by sector"""
    # Get latest year if not specified
    if not year:
        year = db.execute(select(func.max(IPData.year))).scalar() or 2024

    # Get all sectors
    sectors = db.execute(
        select(IPSector).order_by(IPSector.sector_code)
    ).scalars().all()

    sector_summaries = []

    # Batch query: Get all series for key measures and index duration at U.S. Total level
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.sector_code, IPSeries.measure_code, IPSeries.industry_code)
        .where(and_(
            IPSeries.measure_code.in_(KEY_MEASURES),
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.area_code == '000000',  # U.S. Total only
            IPSeries.is_active == True
        ))
    ).all()

    # For each sector+measure, find the most aggregated industry (MIN industry_code)
    # Build mapping: (sector, measure) -> (industry_code, series_id)
    sector_measure_best = {}
    for s in series_query:
        key = (s.sector_code, s.measure_code)
        if key not in sector_measure_best or s.industry_code < sector_measure_best[key][0]:
            sector_measure_best[key] = (s.industry_code, s.series_id)

    # Build mapping: (sector, measure) -> series_id
    series_map = {k: v[1] for k, v in sector_measure_best.items()}

    # Get all series IDs for batch data query
    all_series_ids = list(set(s.series_id for s in series_query))

    # Batch query for data values
    if all_series_ids:
        data_query = db.execute(
            select(IPData.series_id, IPData.value)
            .where(and_(
                IPData.series_id.in_(all_series_ids),
                IPData.year == year,
                IPData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_query}
    else:
        values_map = {}

    # Also get percent changes
    change_series_query = db.execute(
        select(IPSeries.series_id, IPSeries.sector_code, IPSeries.measure_code, IPSeries.industry_code)
        .where(and_(
            IPSeries.measure_code.in_(KEY_MEASURES),
            IPSeries.duration_code == DURATION_PERCENT_CHANGE,
            IPSeries.area_code == '000000',  # U.S. Total only
            IPSeries.is_active == True
        ))
    ).all()

    # For each sector+measure, find the most aggregated industry
    change_sector_measure_best = {}
    for s in change_series_query:
        key = (s.sector_code, s.measure_code)
        if key not in change_sector_measure_best or s.industry_code < change_sector_measure_best[key][0]:
            change_sector_measure_best[key] = (s.industry_code, s.series_id)

    change_series_map = {k: v[1] for k, v in change_sector_measure_best.items()}

    all_change_series_ids = list(set(s.series_id for s in change_series_query))

    if all_change_series_ids:
        change_data_query = db.execute(
            select(IPData.series_id, IPData.value)
            .where(and_(
                IPData.series_id.in_(all_change_series_ids),
                IPData.year == year,
                IPData.period == 'A01'
            ))
        ).all()
        change_values_map = {d.series_id: d.value for d in change_data_query}
    else:
        change_values_map = {}

    # Count industries per sector
    sector_industry_count = {}
    count_query = db.execute(
        select(IPSeries.sector_code, func.count(func.distinct(IPSeries.industry_code)).label('count'))
        .where(IPSeries.is_active == True)
        .group_by(IPSeries.sector_code)
    ).all()
    for row in count_query:
        sector_industry_count[row.sector_code] = row.count

    for sector in sectors:
        def get_value(measure_code: str) -> Optional[float]:
            key = (sector.sector_code, measure_code)
            series_id = series_map.get(key)
            if series_id:
                val = values_map.get(series_id)
                if val is not None:
                    return decimal_to_float(val)
            return None

        def get_change(measure_code: str) -> Optional[float]:
            key = (sector.sector_code, measure_code)
            series_id = change_series_map.get(key)
            if series_id:
                val = change_values_map.get(series_id)
                if val is not None:
                    return decimal_to_float(val)
            return None

        sector_summaries.append(IPSectorSummary(
            sector_code=sector.sector_code,
            sector_text=sector.sector_text,
            labor_productivity=get_value(MEASURE_LABOR_PRODUCTIVITY),
            labor_productivity_change=get_change(MEASURE_LABOR_PRODUCTIVITY),
            output=get_value(MEASURE_OUTPUT),
            output_change=get_change(MEASURE_OUTPUT),
            hours=get_value(MEASURE_HOURS),
            hours_change=get_change(MEASURE_HOURS),
            employment=get_value(MEASURE_EMPLOYMENT),
            employment_change=get_change(MEASURE_EMPLOYMENT),
            unit_labor_costs=get_value(MEASURE_UNIT_LABOR_COSTS),
            ulc_change=get_change(MEASURE_UNIT_LABOR_COSTS),
            industry_count=sector_industry_count.get(sector.sector_code, 0)
        ))

    return IPOverviewResponse(
        year=year,
        sectors=sector_summaries
    )


@router.get("/overview/timeline", response_model=IPOverviewTimelineResponse)
async def get_overview_timeline(
    measure_code: str = Query(MEASURE_LABOR_PRODUCTIVITY, description="Measure to track"),
    duration_code: str = Query(DURATION_INDEX, description="Duration code (0=Index, 1=% change)"),
    start_year: Optional[int] = Query(None, description="Start year"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for overview - measure by sector over time"""
    end_year = db.execute(select(func.max(IPData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    # Get measure name
    measure = db.execute(
        select(IPMeasure).where(IPMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure.measure_text if measure else measure_code

    # Get sectors
    sectors = db.execute(
        select(IPSector).order_by(IPSector.sector_code)
    ).scalars().all()

    sector_names = {s.sector_code: s.sector_text for s in sectors}

    # Batch query: Find series for the specific measure at U.S. Total level
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.sector_code, IPSeries.industry_code)
        .where(and_(
            IPSeries.measure_code == measure_code,
            IPSeries.duration_code == duration_code,
            IPSeries.area_code == '000000',  # U.S. Total only
            IPSeries.is_active == True
        ))
    ).all()

    # For each sector, find the most aggregated industry (MIN industry_code)
    sector_to_series = {}
    sector_best_industry = {}
    for s in series_query:
        if s.sector_code not in sector_best_industry or s.industry_code < sector_best_industry[s.sector_code]:
            sector_best_industry[s.sector_code] = s.industry_code
            sector_to_series[s.sector_code] = s.series_id

    if not sector_to_series:
        # Return empty timeline instead of error
        return IPOverviewTimelineResponse(
            measure_code=measure_code,
            measure_text=measure_text,
            timeline=[],
            sector_names=sector_names
        )

    # Batch query for data
    all_series_ids = list(sector_to_series.values())
    data_rows = db.execute(
        select(IPData)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year >= start_year,
            IPData.year <= end_year,
            IPData.period == 'A01'
        ))
        .order_by(IPData.year)
    ).scalars().all()

    # Reverse mapping
    series_to_sector = {v: k for k, v in sector_to_series.items()}

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        sector_code = series_to_sector.get(d.series_id)
        if sector_code:
            year_data[d.year][sector_code] = decimal_to_float(d.value)

    timeline = [
        IPOverviewTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            sectors={sec: year_data.get(year, {}).get(sec) for sec in sector_names.keys()}
        )
        for year in sorted(year_data.keys())
    ]

    return IPOverviewTimelineResponse(
        measure_code=measure_code,
        measure_text=measure_text,
        timeline=timeline,
        sector_names=sector_names
    )


# ============================================================================
# SECTOR ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/sectors/{sector_code}", response_model=IPSectorAnalysisResponse)
async def get_sector_analysis(
    sector_code: str,
    year: Optional[int] = Query(None, description="Year for analysis"),
    display_level: int = Query(2, description="Industry hierarchy level (1-5)"),
    db: Session = Depends(get_data_db)
):
    """Get detailed analysis for a specific sector with industry breakdown"""
    if not year:
        year = db.execute(select(func.max(IPData.year))).scalar() or 2024

    # Get sector info
    sector = db.execute(
        select(IPSector).where(IPSector.sector_code == sector_code)
    ).scalar_one_or_none()

    if not sector:
        raise HTTPException(status_code=404, detail=f"Sector {sector_code} not found")

    # Get industries for this sector
    industries = db.execute(
        select(IPIndustry)
        .where(and_(
            IPIndustry.selectable == 'T',
            IPIndustry.display_level <= display_level
        ))
        .order_by(IPIndustry.sort_sequence)
    ).scalars().all()

    # Filter to industries in this sector by checking series
    sector_industries = []
    industry_codes = [i.industry_code for i in industries]

    # Batch query: Find series for these industries in this sector
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.industry_code, IPSeries.measure_code)
        .where(and_(
            IPSeries.sector_code == sector_code,
            IPSeries.industry_code.in_(industry_codes),
            IPSeries.measure_code.in_(KEY_MEASURES),
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.is_active == True
        ))
    ).all()

    # Build mapping
    series_map = {}
    valid_industry_codes = set()
    for s in series_query:
        key = (s.industry_code, s.measure_code)
        series_map[key] = s.series_id
        valid_industry_codes.add(s.industry_code)

    # Get data values
    all_series_ids = list(set(s.series_id for s in series_query))
    data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    values_map = {d.series_id: d.value for d in data_query}

    # Get percent changes
    change_series_query = db.execute(
        select(IPSeries.series_id, IPSeries.industry_code, IPSeries.measure_code)
        .where(and_(
            IPSeries.sector_code == sector_code,
            IPSeries.industry_code.in_(industry_codes),
            IPSeries.measure_code.in_(KEY_MEASURES),
            IPSeries.duration_code == DURATION_PERCENT_CHANGE,
            IPSeries.is_active == True
        ))
    ).all()

    change_series_map = {}
    for s in change_series_query:
        key = (s.industry_code, s.measure_code)
        change_series_map[key] = s.series_id

    all_change_ids = list(set(s.series_id for s in change_series_query))
    change_data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_change_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    change_values_map = {d.series_id: d.value for d in change_data_query}

    # Build industry metrics
    industry_metrics = []
    for ind in industries:
        if ind.industry_code not in valid_industry_codes:
            continue

        def get_val(measure_code: str) -> Optional[float]:
            key = (ind.industry_code, measure_code)
            series_id = series_map.get(key)
            if series_id:
                return decimal_to_float(values_map.get(series_id))
            return None

        def get_change(measure_code: str) -> Optional[float]:
            key = (ind.industry_code, measure_code)
            series_id = change_series_map.get(key)
            if series_id:
                return decimal_to_float(change_values_map.get(series_id))
            return None

        industry_metrics.append(IPIndustryMetric(
            industry_code=ind.industry_code,
            industry_text=ind.industry_text,
            naics_code=ind.naics_code,
            display_level=ind.display_level,
            labor_productivity=get_val(MEASURE_LABOR_PRODUCTIVITY),
            labor_productivity_change=get_change(MEASURE_LABOR_PRODUCTIVITY),
            output=get_val(MEASURE_OUTPUT),
            output_change=get_change(MEASURE_OUTPUT),
            hours=get_val(MEASURE_HOURS),
            hours_change=get_change(MEASURE_HOURS),
            employment=get_val(MEASURE_EMPLOYMENT),
            employment_change=get_change(MEASURE_EMPLOYMENT)
        ))

    return IPSectorAnalysisResponse(
        sector_code=sector_code,
        sector_text=sector.sector_text,
        year=year,
        industries=industry_metrics
    )


@router.get("/sectors/{sector_code}/timeline", response_model=IPSectorTimelineResponse)
async def get_sector_timeline(
    sector_code: str,
    measure_code: str = Query(MEASURE_LABOR_PRODUCTIVITY, description="Measure to track"),
    industry_codes: str = Query(..., description="Comma-separated industry codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for industries within a sector"""
    if not end_year:
        end_year = db.execute(select(func.max(IPData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    industry_list = [i.strip() for i in industry_codes.split(',')]

    # Get sector info
    sector = db.execute(
        select(IPSector).where(IPSector.sector_code == sector_code)
    ).scalar_one_or_none()
    sector_text = sector.sector_text if sector else sector_code

    # Get measure info
    measure = db.execute(
        select(IPMeasure).where(IPMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure.measure_text if measure else measure_code

    # Get industry names
    industries = db.execute(
        select(IPIndustry.industry_code, IPIndustry.industry_text)
        .where(IPIndustry.industry_code.in_(industry_list))
    ).all()
    industry_names = {i.industry_code: i.industry_text for i in industries}

    # Batch query: Find series for these industries
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.industry_code)
        .where(and_(
            IPSeries.sector_code == sector_code,
            IPSeries.industry_code.in_(industry_list),
            IPSeries.measure_code == measure_code,
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.is_active == True
        ))
    ).all()

    series_to_industry = {}
    for s in series_query:
        if s.industry_code not in series_to_industry:
            series_to_industry[s.series_id] = s.industry_code

    if not series_to_industry:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query for data
    all_series_ids = list(series_to_industry.keys())
    data_rows = db.execute(
        select(IPData)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year >= start_year,
            IPData.year <= end_year,
            IPData.period == 'A01'
        ))
        .order_by(IPData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        industry_code = series_to_industry.get(d.series_id)
        if industry_code:
            year_data[d.year][industry_code] = decimal_to_float(d.value)

    timeline = [
        IPSectorTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            industries={ind: year_data.get(year, {}).get(ind) for ind in industry_list}
        )
        for year in sorted(year_data.keys())
    ]

    return IPSectorTimelineResponse(
        sector_code=sector_code,
        sector_text=sector_text,
        measure_code=measure_code,
        measure_text=measure_text,
        timeline=timeline,
        industry_names=industry_names
    )


# ============================================================================
# INDUSTRY ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/industries/{industry_code}", response_model=IPIndustryAnalysisResponse)
async def get_industry_analysis(
    industry_code: str,
    year: Optional[int] = Query(None, description="Year for analysis"),
    db: Session = Depends(get_data_db)
):
    """Get detailed analysis for a specific industry with all measures"""
    if not year:
        year = db.execute(select(func.max(IPData.year))).scalar() or 2024

    # Get industry info
    industry = db.execute(
        select(IPIndustry).where(IPIndustry.industry_code == industry_code)
    ).scalar_one_or_none()

    if not industry:
        raise HTTPException(status_code=404, detail=f"Industry {industry_code} not found")

    # Get sector info from series
    sector_query = db.execute(
        select(IPSeries.sector_code)
        .where(IPSeries.industry_code == industry_code)
        .limit(1)
    ).scalar()

    sector = db.execute(
        select(IPSector).where(IPSector.sector_code == sector_query)
    ).scalar_one_or_none() if sector_query else None

    # Get all measures
    measures = db.execute(
        select(IPMeasure)
        .where(IPMeasure.selectable == 'T')
        .order_by(IPMeasure.sort_sequence)
    ).scalars().all()

    # Batch query: Get series for all measures
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.measure_code)
        .where(and_(
            IPSeries.industry_code == industry_code,
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.is_active == True
        ))
    ).all()

    series_map = {s.measure_code: s.series_id for s in series_query}

    # Get data values
    all_series_ids = list(set(s.series_id for s in series_query))
    data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    values_map = {d.series_id: d.value for d in data_query}

    # Get percent changes
    change_series_query = db.execute(
        select(IPSeries.series_id, IPSeries.measure_code)
        .where(and_(
            IPSeries.industry_code == industry_code,
            IPSeries.duration_code == DURATION_PERCENT_CHANGE,
            IPSeries.is_active == True
        ))
    ).all()

    change_series_map = {s.measure_code: s.series_id for s in change_series_query}

    all_change_ids = list(set(s.series_id for s in change_series_query))
    change_data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_change_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    change_values_map = {d.series_id: d.value for d in change_data_query}

    # Build measure values
    measure_values = []
    for m in measures:
        series_id = series_map.get(m.measure_code)
        change_series_id = change_series_map.get(m.measure_code)

        value = decimal_to_float(values_map.get(series_id)) if series_id else None
        change = decimal_to_float(change_values_map.get(change_series_id)) if change_series_id else None

        if value is not None or change is not None:
            measure_values.append(IPMeasureValue(
                measure_code=m.measure_code,
                measure_text=m.measure_text,
                value=value,
                change=change
            ))

    return IPIndustryAnalysisResponse(
        industry_code=industry_code,
        industry_text=industry.industry_text,
        naics_code=industry.naics_code,
        sector_code=sector.sector_code if sector else None,
        sector_text=sector.sector_text if sector else None,
        year=year,
        measures=measure_values
    )


@router.get("/industries/{industry_code}/timeline", response_model=IPIndustryTimelineResponse)
async def get_industry_timeline(
    industry_code: str,
    measure_codes: str = Query(..., description="Comma-separated measure codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for multiple measures of an industry"""
    if not end_year:
        end_year = db.execute(select(func.max(IPData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    measure_list = [m.strip() for m in measure_codes.split(',')]

    # Get industry info
    industry = db.execute(
        select(IPIndustry).where(IPIndustry.industry_code == industry_code)
    ).scalar_one_or_none()
    industry_text = industry.industry_text if industry else industry_code

    # Get measure names
    measures = db.execute(
        select(IPMeasure.measure_code, IPMeasure.measure_text)
        .where(IPMeasure.measure_code.in_(measure_list))
    ).all()
    measure_names = {m.measure_code: m.measure_text for m in measures}

    # Batch query: Find series for these measures
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.measure_code)
        .where(and_(
            IPSeries.industry_code == industry_code,
            IPSeries.measure_code.in_(measure_list),
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.is_active == True
        ))
    ).all()

    series_to_measure = {}
    for s in series_query:
        if s.measure_code not in series_to_measure:
            series_to_measure[s.series_id] = s.measure_code

    if not series_to_measure:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query for data
    all_series_ids = list(series_to_measure.keys())
    data_rows = db.execute(
        select(IPData)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year >= start_year,
            IPData.year <= end_year,
            IPData.period == 'A01'
        ))
        .order_by(IPData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        measure_code = series_to_measure.get(d.series_id)
        if measure_code:
            year_data[d.year][measure_code] = decimal_to_float(d.value)

    timeline = [
        IPIndustryTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            measures={m: year_data.get(year, {}).get(m) for m in measure_list}
        )
        for year in sorted(year_data.keys())
    ]

    return IPIndustryTimelineResponse(
        industry_code=industry_code,
        industry_text=industry_text,
        timeline=timeline,
        measure_names=measure_names
    )


# ============================================================================
# MEASURE COMPARISON ENDPOINTS
# ============================================================================

@router.get("/measures/{measure_code}", response_model=IPMeasureComparisonResponse)
async def get_measure_comparison(
    measure_code: str,
    sector_code: Optional[str] = Query(None, description="Filter by sector"),
    display_level: int = Query(2, description="Industry hierarchy level"),
    year: Optional[int] = Query(None, description="Year for comparison"),
    limit: int = Query(50, description="Maximum industries to return"),
    db: Session = Depends(get_data_db)
):
    """Compare a measure across industries"""
    if not year:
        year = db.execute(select(func.max(IPData.year))).scalar() or 2024

    # Get measure info
    measure = db.execute(
        select(IPMeasure).where(IPMeasure.measure_code == measure_code)
    ).scalar_one_or_none()

    if not measure:
        raise HTTPException(status_code=404, detail=f"Measure {measure_code} not found")

    # Get industries
    ind_query = select(IPIndustry).where(and_(
        IPIndustry.selectable == 'T',
        IPIndustry.display_level <= display_level
    )).order_by(IPIndustry.sort_sequence)

    industries = db.execute(ind_query).scalars().all()
    industry_codes = [i.industry_code for i in industries]

    # Batch query: Find series
    series_base_query = select(IPSeries.series_id, IPSeries.industry_code).where(and_(
        IPSeries.industry_code.in_(industry_codes),
        IPSeries.measure_code == measure_code,
        IPSeries.duration_code == DURATION_INDEX,
        IPSeries.is_active == True
    ))
    if sector_code:
        series_base_query = series_base_query.where(IPSeries.sector_code == sector_code)

    series_query = db.execute(series_base_query).all()

    series_map = {}
    for s in series_query:
        if s.industry_code not in series_map:
            series_map[s.industry_code] = s.series_id

    # Get data values
    all_series_ids = list(series_map.values())
    data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    values_map = {d.series_id: d.value for d in data_query}

    # Get percent changes
    change_series_base_query = select(IPSeries.series_id, IPSeries.industry_code).where(and_(
        IPSeries.industry_code.in_(industry_codes),
        IPSeries.measure_code == measure_code,
        IPSeries.duration_code == DURATION_PERCENT_CHANGE,
        IPSeries.is_active == True
    ))
    if sector_code:
        change_series_base_query = change_series_base_query.where(IPSeries.sector_code == sector_code)

    change_series_query = db.execute(change_series_base_query).all()

    change_series_map = {}
    for s in change_series_query:
        if s.industry_code not in change_series_map:
            change_series_map[s.industry_code] = s.series_id

    all_change_ids = list(change_series_map.values())
    change_data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_change_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    change_values_map = {d.series_id: d.value for d in change_data_query}

    # Build results
    industry_metrics = []
    for ind in industries:
        series_id = series_map.get(ind.industry_code)
        if not series_id:
            continue

        value = decimal_to_float(values_map.get(series_id))
        change_series_id = change_series_map.get(ind.industry_code)
        change = decimal_to_float(change_values_map.get(change_series_id)) if change_series_id else None

        if value is not None:
            industry_metrics.append(IPIndustryMeasureMetric(
                industry_code=ind.industry_code,
                industry_text=ind.industry_text,
                naics_code=ind.naics_code,
                value=value,
                change=change
            ))

    # Sort by value descending and limit
    industry_metrics.sort(key=lambda x: x.value if x.value else 0, reverse=True)
    industry_metrics = industry_metrics[:limit]

    return IPMeasureComparisonResponse(
        measure_code=measure_code,
        measure_text=measure.measure_text,
        year=year,
        industries=industry_metrics
    )


@router.get("/measures/{measure_code}/timeline", response_model=IPMeasureTimelineResponse)
async def get_measure_timeline(
    measure_code: str,
    industry_codes: str = Query(..., description="Comma-separated industry codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for a measure across industries"""
    if not end_year:
        end_year = db.execute(select(func.max(IPData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    industry_list = [i.strip() for i in industry_codes.split(',')]

    # Get measure info
    measure = db.execute(
        select(IPMeasure).where(IPMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure.measure_text if measure else measure_code

    # Get industry names
    industries = db.execute(
        select(IPIndustry.industry_code, IPIndustry.industry_text)
        .where(IPIndustry.industry_code.in_(industry_list))
    ).all()
    industry_names = {i.industry_code: i.industry_text for i in industries}

    # Batch query: Find series
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.industry_code)
        .where(and_(
            IPSeries.industry_code.in_(industry_list),
            IPSeries.measure_code == measure_code,
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.is_active == True
        ))
    ).all()

    series_to_industry = {}
    for s in series_query:
        if s.industry_code not in series_to_industry:
            series_to_industry[s.series_id] = s.industry_code

    if not series_to_industry:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query for data
    all_series_ids = list(series_to_industry.keys())
    data_rows = db.execute(
        select(IPData)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year >= start_year,
            IPData.year <= end_year,
            IPData.period == 'A01'
        ))
        .order_by(IPData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        industry_code = series_to_industry.get(d.series_id)
        if industry_code:
            year_data[d.year][industry_code] = decimal_to_float(d.value)

    timeline = [
        IPMeasureTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            industries={ind: year_data.get(year, {}).get(ind) for ind in industry_list}
        )
        for year in sorted(year_data.keys())
    ]

    return IPMeasureTimelineResponse(
        measure_code=measure_code,
        measure_text=measure_text,
        timeline=timeline,
        industry_names=industry_names
    )


# ============================================================================
# TOP RANKINGS ENDPOINTS
# ============================================================================

@router.get("/top-rankings", response_model=IPTopRankingsResponse)
async def get_top_rankings(
    ranking_type: str = Query("highest", description="'highest', 'lowest', 'fastest_growing', 'fastest_declining'"),
    measure_code: str = Query(MEASURE_LABOR_PRODUCTIVITY, description="Measure to rank by"),
    sector_code: Optional[str] = Query(None, description="Filter by sector"),
    year: Optional[int] = Query(None, description="Year for ranking"),
    limit: int = Query(20, description="Number of results"),
    db: Session = Depends(get_data_db)
):
    """Get top/bottom industries by measure"""
    if not year:
        year = db.execute(select(func.max(IPData.year))).scalar() or 2024

    # Get measure info
    measure = db.execute(
        select(IPMeasure).where(IPMeasure.measure_code == measure_code)
    ).scalar_one_or_none()
    measure_text = measure.measure_text if measure else measure_code

    # Determine which duration to use for ranking
    if ranking_type in ['fastest_growing', 'fastest_declining']:
        ranking_duration = DURATION_PERCENT_CHANGE
    else:
        ranking_duration = DURATION_INDEX

    # Get industries
    industries = db.execute(
        select(IPIndustry)
        .where(IPIndustry.selectable == 'T')
        .order_by(IPIndustry.sort_sequence)
    ).scalars().all()
    industry_map = {i.industry_code: i for i in industries}
    industry_codes = list(industry_map.keys())

    # Batch query: Find series for ranking
    series_base_query = select(IPSeries.series_id, IPSeries.industry_code, IPSeries.sector_code).where(and_(
        IPSeries.industry_code.in_(industry_codes),
        IPSeries.measure_code == measure_code,
        IPSeries.duration_code == ranking_duration,
        IPSeries.is_active == True
    ))
    if sector_code:
        series_base_query = series_base_query.where(IPSeries.sector_code == sector_code)

    series_query = db.execute(series_base_query).all()

    series_map = {}
    sector_map = {}
    for s in series_query:
        if s.industry_code not in series_map:
            series_map[s.industry_code] = s.series_id
            sector_map[s.industry_code] = s.sector_code

    # Also get percent change series for YoY display (when ranking by index)
    change_series_map = {}
    if ranking_duration == DURATION_INDEX:
        change_series_query = db.execute(
            select(IPSeries.series_id, IPSeries.industry_code)
            .where(and_(
                IPSeries.industry_code.in_(industry_codes),
                IPSeries.measure_code == measure_code,
                IPSeries.duration_code == DURATION_PERCENT_CHANGE,
                IPSeries.is_active == True
            ))
        ).all()
        for s in change_series_query:
            if s.industry_code not in change_series_map:
                change_series_map[s.industry_code] = s.series_id

    # Get data values for ranking
    all_series_ids = list(series_map.values())
    if all_series_ids:
        data_query = db.execute(
            select(IPData.series_id, IPData.value)
            .where(and_(
                IPData.series_id.in_(all_series_ids),
                IPData.year == year,
                IPData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_query}
    else:
        values_map = {}

    # Get YoY change values (if ranking by index)
    change_values_map = {}
    if change_series_map:
        change_series_ids = list(change_series_map.values())
        change_data_query = db.execute(
            select(IPData.series_id, IPData.value)
            .where(and_(
                IPData.series_id.in_(change_series_ids),
                IPData.year == year,
                IPData.period == 'A01'
            ))
        ).all()
        change_values_map = {d.series_id: d.value for d in change_data_query}

    # Reverse map
    series_to_industry = {v: k for k, v in series_map.items()}

    # Get all sectors in one query
    sector_query = db.execute(select(IPSector)).scalars().all()
    sector_name_map = {s.sector_code: s.sector_text for s in sector_query}

    # Build results
    results = []
    for industry_code, series_id in series_map.items():
        value = values_map.get(series_id)
        if value is None:
            continue
        industry = industry_map.get(industry_code)
        if not industry:
            continue

        # Get YoY change
        change_value = None
        if ranking_duration == DURATION_PERCENT_CHANGE:
            change_value = decimal_to_float(value)  # The value IS the change
        elif change_series_map.get(industry_code):
            change_series_id = change_series_map[industry_code]
            change_val = change_values_map.get(change_series_id)
            if change_val is not None:
                change_value = decimal_to_float(change_val)

        results.append({
            'industry_code': industry_code,
            'industry_text': industry.industry_text,
            'naics_code': industry.naics_code,
            'sector_code': sector_map.get(industry_code),
            'sector_text': sector_name_map.get(sector_map.get(industry_code)),
            'value': decimal_to_float(value),
            'change': change_value
        })

    # Sort based on ranking type
    if ranking_type in ['highest', 'fastest_growing']:
        results.sort(key=lambda x: x['value'] if x['value'] else float('-inf'), reverse=True)
    else:
        results.sort(key=lambda x: x['value'] if x['value'] else float('inf'))

    # Take top N
    results = results[:limit]

    # Build response
    top_industries = []
    for i, r in enumerate(results, 1):
        top_industries.append(IPTopIndustry(
            rank=i,
            industry_code=r['industry_code'],
            industry_text=r['industry_text'],
            naics_code=r['naics_code'],
            sector_code=r['sector_code'],
            sector_text=r['sector_text'],
            value=r['value'],
            change=r['change']
        ))

    return IPTopRankingsResponse(
        measure_code=measure_code,
        measure_text=measure_text,
        ranking_type=ranking_type,
        year=year,
        industries=top_industries
    )


# ============================================================================
# PRODUCTIVITY VS COSTS ENDPOINTS
# ============================================================================

@router.get("/productivity-vs-costs", response_model=IPProductivityVsCostsResponse)
async def get_productivity_vs_costs(
    sector_code: Optional[str] = Query(None, description="Filter by sector"),
    display_level: int = Query(2, description="Industry hierarchy level"),
    year: Optional[int] = Query(None, description="Year for comparison"),
    limit: int = Query(50, description="Maximum industries to return"),
    db: Session = Depends(get_data_db)
):
    """Compare productivity vs unit labor costs across industries"""
    if not year:
        year = db.execute(select(func.max(IPData.year))).scalar() or 2024

    sector_text = None
    if sector_code:
        sector = db.execute(
            select(IPSector).where(IPSector.sector_code == sector_code)
        ).scalar_one_or_none()
        sector_text = sector.sector_text if sector else None

    # Get industries
    ind_query = select(IPIndustry).where(and_(
        IPIndustry.selectable == 'T',
        IPIndustry.display_level <= display_level
    )).order_by(IPIndustry.sort_sequence)

    industries = db.execute(ind_query).scalars().all()
    industry_codes = [i.industry_code for i in industries]
    industry_map = {i.industry_code: i for i in industries}

    measures_needed = [MEASURE_LABOR_PRODUCTIVITY, MEASURE_UNIT_LABOR_COSTS, MEASURE_OUTPUT, MEASURE_COMPENSATION]

    # Batch query: Find series for index values
    series_base_query = select(IPSeries.series_id, IPSeries.industry_code, IPSeries.measure_code).where(and_(
        IPSeries.industry_code.in_(industry_codes),
        IPSeries.measure_code.in_(measures_needed),
        IPSeries.duration_code == DURATION_INDEX,
        IPSeries.is_active == True
    ))
    if sector_code:
        series_base_query = series_base_query.where(IPSeries.sector_code == sector_code)

    series_query = db.execute(series_base_query).all()

    series_map = {}  # (industry, measure) -> series_id
    for s in series_query:
        key = (s.industry_code, s.measure_code)
        if key not in series_map:
            series_map[key] = s.series_id

    # Get data values
    all_series_ids = list(set(series_map.values()))
    data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    values_map = {d.series_id: d.value for d in data_query}

    # Get percent changes
    change_series_base_query = select(IPSeries.series_id, IPSeries.industry_code, IPSeries.measure_code).where(and_(
        IPSeries.industry_code.in_(industry_codes),
        IPSeries.measure_code.in_(measures_needed),
        IPSeries.duration_code == DURATION_PERCENT_CHANGE,
        IPSeries.is_active == True
    ))
    if sector_code:
        change_series_base_query = change_series_base_query.where(IPSeries.sector_code == sector_code)

    change_series_query = db.execute(change_series_base_query).all()

    change_series_map = {}
    for s in change_series_query:
        key = (s.industry_code, s.measure_code)
        if key not in change_series_map:
            change_series_map[key] = s.series_id

    all_change_ids = list(set(change_series_map.values()))
    change_data_query = db.execute(
        select(IPData.series_id, IPData.value)
        .where(and_(
            IPData.series_id.in_(all_change_ids),
            IPData.year == year,
            IPData.period == 'A01'
        ))
    ).all()
    change_values_map = {d.series_id: d.value for d in change_data_query}

    # Build results
    metrics = []
    for ind_code in set(s[0] for s in series_map.keys()):
        industry = industry_map.get(ind_code)
        if not industry:
            continue

        def get_val(measure: str) -> Optional[float]:
            key = (ind_code, measure)
            series_id = series_map.get(key)
            if series_id:
                return decimal_to_float(values_map.get(series_id))
            return None

        def get_change(measure: str) -> Optional[float]:
            key = (ind_code, measure)
            series_id = change_series_map.get(key)
            if series_id:
                return decimal_to_float(change_values_map.get(series_id))
            return None

        lp = get_val(MEASURE_LABOR_PRODUCTIVITY)
        ulc = get_val(MEASURE_UNIT_LABOR_COSTS)

        if lp is not None or ulc is not None:
            metrics.append(IPProductivityVsCostsMetric(
                industry_code=ind_code,
                industry_text=industry.industry_text,
                naics_code=industry.naics_code,
                labor_productivity=lp,
                productivity_change=get_change(MEASURE_LABOR_PRODUCTIVITY),
                unit_labor_costs=ulc,
                ulc_change=get_change(MEASURE_UNIT_LABOR_COSTS),
                output=get_val(MEASURE_OUTPUT),
                output_change=get_change(MEASURE_OUTPUT),
                compensation=get_val(MEASURE_COMPENSATION),
                compensation_change=get_change(MEASURE_COMPENSATION)
            ))

    # Sort by productivity descending
    metrics.sort(key=lambda x: x.labor_productivity if x.labor_productivity else 0, reverse=True)
    metrics = metrics[:limit]

    return IPProductivityVsCostsResponse(
        sector_code=sector_code,
        sector_text=sector_text,
        year=year,
        industries=metrics
    )


@router.get("/productivity-vs-costs/timeline", response_model=IPProductivityVsCostsTimelineResponse)
async def get_productivity_vs_costs_timeline(
    industry_code: str = Query(..., description="Industry code"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    db: Session = Depends(get_data_db)
):
    """Get timeline for productivity vs costs for an industry"""
    if not end_year:
        end_year = db.execute(select(func.max(IPData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    # Get industry info
    industry = db.execute(
        select(IPIndustry).where(IPIndustry.industry_code == industry_code)
    ).scalar_one_or_none()
    industry_text = industry.industry_text if industry else industry_code

    measures_needed = [MEASURE_LABOR_PRODUCTIVITY, MEASURE_UNIT_LABOR_COSTS, MEASURE_OUTPUT, MEASURE_COMPENSATION]

    # Batch query: Find series
    series_query = db.execute(
        select(IPSeries.series_id, IPSeries.measure_code)
        .where(and_(
            IPSeries.industry_code == industry_code,
            IPSeries.measure_code.in_(measures_needed),
            IPSeries.duration_code == DURATION_INDEX,
            IPSeries.is_active == True
        ))
    ).all()

    series_to_measure = {}
    for s in series_query:
        if s.measure_code not in series_to_measure:
            series_to_measure[s.series_id] = s.measure_code

    if not series_to_measure:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query for data
    all_series_ids = list(series_to_measure.keys())
    data_rows = db.execute(
        select(IPData)
        .where(and_(
            IPData.series_id.in_(all_series_ids),
            IPData.year >= start_year,
            IPData.year <= end_year,
            IPData.period == 'A01'
        ))
        .order_by(IPData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        measure_code = series_to_measure.get(d.series_id)
        if measure_code:
            year_data[d.year][measure_code] = decimal_to_float(d.value)

    timeline = [
        IPProductivityVsCostsTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            labor_productivity=year_data.get(year, {}).get(MEASURE_LABOR_PRODUCTIVITY),
            unit_labor_costs=year_data.get(year, {}).get(MEASURE_UNIT_LABOR_COSTS),
            output=year_data.get(year, {}).get(MEASURE_OUTPUT),
            compensation=year_data.get(year, {}).get(MEASURE_COMPENSATION)
        )
        for year in sorted(year_data.keys())
    ]

    return IPProductivityVsCostsTimelineResponse(
        industry_code=industry_code,
        industry_text=industry_text,
        timeline=timeline
    )
