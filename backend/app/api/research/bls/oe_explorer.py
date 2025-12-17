"""
OE (Occupational Employment and Wage Statistics) Explorer API

Provides endpoints for exploring OEWS data including:
- National, State, and Metro area employment/wage estimates
- ~800 occupations (SOC classification)
- 450+ industries (NAICS classification at national level)
- Wage distributions (10th, 25th, median, 75th, 90th percentiles)
- Location quotients and employment concentration

Data is annual, updated each March.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import (
    OEAreaType, OEDataType, OEIndustry, OEOccupation, OESector, OEArea, OESeries, OEData
)
from .oe_schemas import (
    OEDimensions, OEAreaTypeItem, OEAreaItem, OEIndustryItem, OESectorItem,
    OEOccupationItem, OEDataTypeItem,
    OESeriesInfo, OESeriesListResponse,
    OEDataPoint, OESeriesData, OEDataResponse,
    OEMajorGroupSummary, OEOverviewResponse, OEOverviewTimelinePoint, OEOverviewTimelineResponse,
    OEOccupationMetric, OEOccupationAnalysisResponse, OEOccupationTimelinePoint, OEOccupationTimelineResponse,
    OEAreaMetric, OEAreaAnalysisResponse, OEAreaTimelinePoint, OEAreaTimelineResponse,
    OEIndustryMetric, OEIndustryAnalysisResponse, OEIndustryTimelinePoint, OEIndustryTimelineResponse,
    OEStateMetric, OEStateComparisonResponse, OEStateTimelinePoint, OEStateTimelineResponse,
    OEWageDistribution, OEWageDistributionResponse,
    OETopOccupation, OETopRankingsResponse,
    OETopMover, OETopMoversResponse,
    OEOccupationWageProfile, OEOccupationProfileResponse
)

router = APIRouter(prefix="/api/research/bls/oe", tags=["BLS OE Research"])


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


def get_period_name(period: str) -> str:
    """Convert period code to display name"""
    # OE uses A01 for annual data
    if period == 'A01':
        return 'Annual'
    return period


# Major occupation group codes (2-digit SOC)
MAJOR_OCCUPATION_GROUPS = [
    '110000', '130000', '150000', '170000', '190000', '210000', '230000',
    '250000', '270000', '290000', '310000', '330000', '350000', '370000',
    '390000', '410000', '430000', '450000', '470000', '490000', '510000', '530000'
]


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=OEDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering OE data"""
    # Area types
    area_types = db.execute(
        select(OEAreaType).order_by(OEAreaType.areatype_code)
    ).scalars().all()

    # States - identify by area_code pattern (state codes end in '00000' with 7 chars)
    # This is MUCH faster than querying the 2M+ series table
    states = db.execute(
        select(OEArea.area_code, OEArea.area_name)
        .where(
            and_(
                OEArea.area_code.like('%00000'),
                func.length(OEArea.area_code) == 7,
                OEArea.area_code != '0000000'  # Exclude national
            )
        )
        .order_by(OEArea.area_name)
    ).all()

    # Major occupation groups (display_level <= 1)
    occupations = db.execute(
        select(OEOccupation)
        .where(OEOccupation.display_level <= 1)
        .order_by(OEOccupation.sort_sequence)
    ).scalars().all()

    # Sectors
    sectors = db.execute(
        select(OESector).order_by(OESector.sector_code)
    ).scalars().all()

    # Data types
    data_types = db.execute(
        select(OEDataType).order_by(OEDataType.datatype_code)
    ).scalars().all()

    return OEDimensions(
        area_types=[OEAreaTypeItem(
            areatype_code=at.areatype_code,
            areatype_name=at.areatype_name
        ) for at in area_types],
        states=[OEAreaItem(
            state_code=s.area_code[:2],  # First 2 chars are state FIPS code
            area_code=s.area_code,
            areatype_code='S',
            area_name=s.area_name
        ) for s in states],
        occupations=[OEOccupationItem(
            occupation_code=o.occupation_code,
            occupation_name=o.occupation_name,
            occupation_description=o.occupation_description,
            display_level=o.display_level,
            selectable=o.selectable == 'T'
        ) for o in occupations],
        sectors=[OESectorItem(
            sector_code=s.sector_code,
            sector_name=s.sector_name
        ) for s in sectors],
        data_types=[OEDataTypeItem(
            datatype_code=dt.datatype_code,
            datatype_name=dt.datatype_name
        ) for dt in data_types]
    )


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================

@router.get("/series", response_model=OESeriesListResponse)
async def get_series(
    occupation_code: Optional[str] = Query(None, description="Filter by occupation code"),
    area_code: Optional[str] = Query(None, description="Filter by area code"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    areatype_code: Optional[str] = Query(None, description="Filter by area type (N/S/M)"),
    industry_code: Optional[str] = Query(None, description="Filter by industry code"),
    datatype_code: Optional[str] = Query(None, description="Filter by data type"),
    search: Optional[str] = Query(None, description="Search series title"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Get list of OE series with optional filters"""
    # Build query
    query = select(OESeries)

    if occupation_code:
        query = query.where(OESeries.occupation_code == occupation_code)
    if area_code:
        query = query.where(OESeries.area_code == area_code)
    if state_code:
        query = query.where(OESeries.state_code == state_code)
    if areatype_code:
        query = query.where(OESeries.areatype_code == areatype_code)
    if industry_code:
        query = query.where(OESeries.industry_code == industry_code)
    if datatype_code:
        query = query.where(OESeries.datatype_code == datatype_code)
    if search:
        query = query.where(OESeries.series_title.ilike(f'%{search}%'))

    # Get total count - skip expensive count if no filters (we know it's ~2M)
    has_filters = any([occupation_code, area_code, state_code, areatype_code, industry_code, datatype_code, search])
    if has_filters:
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar()
    else:
        # Estimate for unfiltered query (avoid counting 2M+ rows)
        total = 2000000  # Approximate

    # Get paginated results
    query = query.order_by(OESeries.series_id).limit(limit).offset(offset)
    series_list = db.execute(query).scalars().all()

    # Get dimension names
    occupation_codes = list(set(s.occupation_code for s in series_list if s.occupation_code))
    area_codes = list(set(s.area_code for s in series_list if s.area_code))
    industry_codes = list(set(s.industry_code for s in series_list if s.industry_code))
    datatype_codes = list(set(s.datatype_code for s in series_list if s.datatype_code))
    areatype_codes = list(set(s.areatype_code for s in series_list if s.areatype_code))
    sector_codes = list(set(s.sector_code for s in series_list if s.sector_code))

    occupation_names = {}
    area_names = {}
    industry_names = {}
    datatype_names = {}
    areatype_names = {}
    sector_names = {}

    if occupation_codes:
        occs = db.execute(
            select(OEOccupation.occupation_code, OEOccupation.occupation_name)
            .where(OEOccupation.occupation_code.in_(occupation_codes))
        ).all()
        occupation_names = {o.occupation_code: o.occupation_name for o in occs}

    if area_codes:
        areas = db.execute(
            select(OEArea.area_code, OEArea.area_name)
            .where(OEArea.area_code.in_(area_codes))
        ).all()
        area_names = {a.area_code: a.area_name for a in areas}

    if industry_codes:
        inds = db.execute(
            select(OEIndustry.industry_code, OEIndustry.industry_name)
            .where(OEIndustry.industry_code.in_(industry_codes))
        ).all()
        industry_names = {i.industry_code: i.industry_name for i in inds}

    if datatype_codes:
        dts = db.execute(
            select(OEDataType.datatype_code, OEDataType.datatype_name)
            .where(OEDataType.datatype_code.in_(datatype_codes))
        ).all()
        datatype_names = {d.datatype_code: d.datatype_name for d in dts}

    if areatype_codes:
        ats = db.execute(
            select(OEAreaType.areatype_code, OEAreaType.areatype_name)
            .where(OEAreaType.areatype_code.in_(areatype_codes))
        ).all()
        areatype_names = {a.areatype_code: a.areatype_name for a in ats}

    if sector_codes:
        secs = db.execute(
            select(OESector.sector_code, OESector.sector_name)
            .where(OESector.sector_code.in_(sector_codes))
        ).all()
        sector_names = {s.sector_code: s.sector_name for s in secs}

    return OESeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=[OESeriesInfo(
            series_id=s.series_id,
            seasonal=s.seasonal,
            areatype_code=s.areatype_code,
            areatype_name=areatype_names.get(s.areatype_code),
            state_code=s.state_code,
            area_code=s.area_code,
            area_name=area_names.get(s.area_code),
            sector_code=s.sector_code,
            sector_name=sector_names.get(s.sector_code),
            industry_code=s.industry_code,
            industry_name=industry_names.get(s.industry_code),
            occupation_code=s.occupation_code,
            occupation_name=occupation_names.get(s.occupation_code),
            datatype_code=s.datatype_code,
            datatype_name=datatype_names.get(s.datatype_code),
            series_title=s.series_title,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period
        ) for s in series_list]
    )


@router.get("/series/{series_id}/data", response_model=OEDataResponse)
async def get_series_data(
    series_id: str,
    years: int = Query(10, description="Number of years to retrieve"),
    db: Session = Depends(get_data_db)
):
    """Get time series data for a specific OE series"""
    # Get series info
    series = db.execute(
        select(OESeries).where(OESeries.series_id == series_id)
    ).scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    # Get dimension names
    occupation_name = None
    area_name = None
    industry_name = None
    datatype_name = None

    if series.occupation_code:
        occ = db.execute(
            select(OEOccupation.occupation_name)
            .where(OEOccupation.occupation_code == series.occupation_code)
        ).scalar_one_or_none()
        occupation_name = occ

    if series.area_code:
        area = db.execute(
            select(OEArea.area_name)
            .where(OEArea.area_code == series.area_code)
        ).scalar_one_or_none()
        area_name = area

    if series.industry_code:
        ind = db.execute(
            select(OEIndustry.industry_name)
            .where(OEIndustry.industry_code == series.industry_code)
        ).scalar_one_or_none()
        industry_name = ind

    if series.datatype_code:
        dt = db.execute(
            select(OEDataType.datatype_name)
            .where(OEDataType.datatype_code == series.datatype_code)
        ).scalar_one_or_none()
        datatype_name = dt

    # Get data points
    query = select(OEData).where(OEData.series_id == series_id)
    if years > 0:
        # Get latest year
        latest_year = db.execute(
            select(func.max(OEData.year)).where(OEData.series_id == series_id)
        ).scalar()
        if latest_year:
            query = query.where(OEData.year >= latest_year - years)

    query = query.order_by(OEData.year.asc(), OEData.period.asc())
    data_points = db.execute(query).scalars().all()

    return OEDataResponse(
        series=[OESeriesData(
            series_id=series_id,
            occupation_name=occupation_name,
            area_name=area_name,
            industry_name=industry_name,
            datatype_name=datatype_name,
            data_points=[OEDataPoint(
                year=dp.year,
                period=dp.period,
                period_name=str(dp.year),
                value=decimal_to_float(dp.value),
                footnote_codes=dp.footnote_codes
            ) for dp in data_points]
        )]
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=OEOverviewResponse)
async def get_overview(
    area_code: str = Query("0000000", description="Area code (0000000=National)"),
    db: Session = Depends(get_data_db)
):
    """Get overview of employment and wages by major occupation groups"""
    # Get area name
    area_name = "National"
    if area_code != "0000000":
        area = db.execute(
            select(OEArea.area_name).where(OEArea.area_code == area_code)
        ).scalar_one_or_none()
        if area:
            area_name = area

    # Get latest year and previous year
    latest_year = db.execute(select(func.max(OEData.year))).scalar()
    prev_year = latest_year - 1 if latest_year else None

    # All occupation codes to query (000000 for total + major groups)
    all_occ_codes = ['000000'] + MAJOR_OCCUPATION_GROUPS

    # Batch query: Get all series for these occupations in one query
    series_query = db.execute(
        select(
            OESeries.series_id,
            OESeries.occupation_code,
            OESeries.datatype_code
        )
        .where(and_(
            OESeries.occupation_code.in_(all_occ_codes),
            OESeries.area_code == area_code,
            OESeries.industry_code == '000000',
            OESeries.datatype_code.in_(['01', '03', '04', '13'])  # emp, hourly, annual_mean, annual_median
        ))
    ).all()

    # Build series lookup: {(occ_code, datatype_code): series_id}
    series_map = {(s.occupation_code, s.datatype_code): s.series_id for s in series_query}

    # Get all series IDs
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get data values for both current and previous year
    data_query = db.execute(
        select(OEData.series_id, OEData.year, OEData.value)
        .where(and_(
            OEData.series_id.in_(all_series_ids),
            OEData.year.in_([latest_year, prev_year])
        ))
    ).all()

    # Build data lookup: {(series_id, year): value}
    data_map = {(d.series_id, d.year): decimal_to_float(d.value) for d in data_query}

    # Batch query: Get occupation names
    occ_query = db.execute(
        select(OEOccupation.occupation_code, OEOccupation.occupation_name)
        .where(OEOccupation.occupation_code.in_(all_occ_codes))
    ).all()
    occ_names = {o.occupation_code: o.occupation_name for o in occ_query}

    # Helper to get value for a specific year
    def get_value(occ_code: str, datatype_code: str, year: int) -> Optional[float]:
        series_id = series_map.get((occ_code, datatype_code))
        return data_map.get((series_id, year)) if series_id else None

    # Extract totals
    total_employment = get_value('000000', '01', latest_year)
    mean_annual_wage = get_value('000000', '04', latest_year)
    median_annual_wage = get_value('000000', '13', latest_year)

    # Build major groups
    major_groups = []
    for occ_code in MAJOR_OCCUPATION_GROUPS:
        occ_name = occ_names.get(occ_code)
        if not occ_name:
            continue

        employment = get_value(occ_code, '01', latest_year)
        annual_mean = get_value(occ_code, '04', latest_year)
        hourly_mean = get_value(occ_code, '03', latest_year)

        # Previous year values for YoY calculation
        prev_employment = get_value(occ_code, '01', prev_year)
        prev_annual_mean = get_value(occ_code, '04', prev_year)

        emp_pct = None
        if employment and total_employment and total_employment > 0:
            emp_pct = round((employment / total_employment) * 100, 2)

        # Calculate YoY employment change
        yoy_emp_change = None
        if employment and prev_employment and prev_employment > 0:
            yoy_emp_change = round(((employment - prev_employment) / prev_employment) * 100, 2)

        # Calculate YoY wage change
        yoy_wage_change = None
        if annual_mean and prev_annual_mean and prev_annual_mean > 0:
            yoy_wage_change = round(((annual_mean - prev_annual_mean) / prev_annual_mean) * 100, 2)

        major_groups.append(OEMajorGroupSummary(
            occupation_code=occ_code,
            occupation_name=occ_name,
            employment=employment,
            annual_mean=annual_mean,
            hourly_mean=hourly_mean,
            employment_pct_of_total=emp_pct,
            yoy_employment_change=yoy_emp_change,
            yoy_wage_change=yoy_wage_change
        ))

    return OEOverviewResponse(
        area_code=area_code,
        area_name=area_name,
        total_employment=total_employment,
        mean_annual_wage=mean_annual_wage,
        median_annual_wage=median_annual_wage,
        latest_year=latest_year,
        major_groups=sorted(major_groups, key=lambda x: x.employment or 0, reverse=True)
    )


@router.get("/overview/timeline", response_model=OEOverviewTimelineResponse)
async def get_overview_timeline(
    area_code: str = Query("0000000", description="Area code"),
    datatype: str = Query("employment", description="employment or annual_mean"),
    years: int = Query(10, description="Number of years"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for major occupation groups"""
    datatype_code = '01' if datatype == 'employment' else '04'

    # Get latest year
    latest_year = db.execute(select(func.max(OEData.year))).scalar()
    start_year = latest_year - years if years > 0 else 2000
    years_list = list(range(start_year, latest_year + 1))

    # Batch query 1: Get occupation names
    occ_query = db.execute(
        select(OEOccupation.occupation_code, OEOccupation.occupation_name)
        .where(OEOccupation.occupation_code.in_(MAJOR_OCCUPATION_GROUPS))
    ).all()
    group_names = {o.occupation_code: o.occupation_name for o in occ_query}

    # Batch query 2: Get all series for major groups
    series_query = db.execute(
        select(OESeries.series_id, OESeries.occupation_code)
        .where(and_(
            OESeries.occupation_code.in_(MAJOR_OCCUPATION_GROUPS),
            OESeries.area_code == area_code,
            OESeries.industry_code == '000000',
            OESeries.datatype_code == datatype_code
        ))
    ).all()
    series_map = {s.occupation_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query 3: Get all data for these series across all years
    data_query = db.execute(
        select(OEData.series_id, OEData.year, OEData.value)
        .where(and_(
            OEData.series_id.in_(all_series_ids),
            OEData.year >= start_year,
            OEData.year <= latest_year
        ))
    ).all() if all_series_ids else []

    # Build data lookup: {(series_id, year): value}
    data_map = {(d.series_id, d.year): decimal_to_float(d.value) for d in data_query}

    # Build timeline
    timeline = []
    for year in years_list:
        point = OEOverviewTimelinePoint(year=year, major_groups={})
        for occ_code in MAJOR_OCCUPATION_GROUPS:
            series_id = series_map.get(occ_code)
            if series_id:
                point.major_groups[occ_code] = data_map.get((series_id, year))
            else:
                point.major_groups[occ_code] = None
        timeline.append(point)

    return OEOverviewTimelineResponse(
        datatype=datatype,
        timeline=timeline,
        group_names=group_names
    )


# ============================================================================
# OCCUPATION ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/occupations", response_model=OEOccupationAnalysisResponse)
async def get_occupations(
    area_code: str = Query("0000000", description="Area code"),
    industry_code: str = Query("000000", description="Industry code"),
    major_group: Optional[str] = Query(None, description="Filter by major group (e.g., 11 for Management)"),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Get occupation-level employment and wage analysis"""
    # Get area name
    area_name = "National"
    if area_code != "0000000":
        area = db.execute(
            select(OEArea.area_name).where(OEArea.area_code == area_code)
        ).scalar_one_or_none()
        if area:
            area_name = area

    # Get industry name
    industry_name = "All Industries"
    if industry_code != "000000":
        ind = db.execute(
            select(OEIndustry.industry_name).where(OEIndustry.industry_code == industry_code)
        ).scalar_one_or_none()
        if ind:
            industry_name = ind

    # Get latest year
    latest_year = db.execute(select(func.max(OEData.year))).scalar()

    # Build occupation query
    occ_query = select(OEOccupation).where(OEOccupation.selectable == 'T')
    if major_group:
        occ_query = occ_query.where(OEOccupation.occupation_code.like(f'{major_group}%'))
    occ_query = occ_query.order_by(OEOccupation.sort_sequence).limit(limit).offset(offset)
    occupations = db.execute(occ_query).scalars().all()

    # Get total count
    count_base = select(func.count()).select_from(OEOccupation).where(OEOccupation.selectable == 'T')
    if major_group:
        count_base = count_base.where(OEOccupation.occupation_code.like(f'{major_group}%'))
    total_count = db.execute(count_base).scalar()

    if not occupations:
        return OEOccupationAnalysisResponse(
            area_code=area_code, area_name=area_name,
            industry_code=industry_code, industry_name=industry_name,
            occupations=[], total_count=0, latest_year=latest_year
        )

    # Get occupation codes
    occ_codes = [o.occupation_code for o in occupations]

    # Batch query: Get all series for these occupations in one query
    datatype_codes = ['01', '03', '04', '08', '13', '16', '17']
    series_query = db.execute(
        select(OESeries.series_id, OESeries.occupation_code, OESeries.datatype_code)
        .where(and_(
            OESeries.occupation_code.in_(occ_codes),
            OESeries.area_code == area_code,
            OESeries.industry_code == industry_code,
            OESeries.datatype_code.in_(datatype_codes)
        ))
    ).all()

    # Build series lookup
    series_map = {(s.occupation_code, s.datatype_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data values
    data_query = db.execute(
        select(OEData.series_id, OEData.value)
        .where(and_(
            OEData.series_id.in_(all_series_ids),
            OEData.year == latest_year
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Helper to get value
    def get_value(occ_code: str, dt_code: str) -> Optional[float]:
        series_id = series_map.get((occ_code, dt_code))
        return data_map.get(series_id) if series_id else None

    # Build results
    results = []
    for occ in occupations:
        employment = get_value(occ.occupation_code, '01')
        if employment is None:
            continue

        results.append(OEOccupationMetric(
            occupation_code=occ.occupation_code,
            occupation_name=occ.occupation_name,
            display_level=occ.display_level,
            employment=employment,
            employment_per_1000=get_value(occ.occupation_code, '16'),
            location_quotient=get_value(occ.occupation_code, '17'),
            hourly_mean=get_value(occ.occupation_code, '03'),
            hourly_median=get_value(occ.occupation_code, '08'),
            annual_mean=get_value(occ.occupation_code, '04'),
            annual_median=get_value(occ.occupation_code, '13'),
            yoy_employment_pct=None,  # Only 2024 data available
            yoy_wage_pct=None,
            latest_year=latest_year
        ))

    return OEOccupationAnalysisResponse(
        area_code=area_code,
        area_name=area_name,
        industry_code=industry_code,
        industry_name=industry_name,
        occupations=results,
        total_count=total_count,
        latest_year=latest_year
    )


@router.get("/occupations/timeline", response_model=OEOccupationTimelineResponse)
async def get_occupations_timeline(
    area_code: str = Query("0000000"),
    industry_code: str = Query("000000"),
    datatype: str = Query("employment", description="employment, annual_mean, hourly_mean"),
    occupation_codes: Optional[str] = Query(None, description="Comma-separated occupation codes"),
    years: int = Query(10),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for occupation comparison"""
    datatype_map = {
        'employment': '01',
        'annual_mean': '04',
        'hourly_mean': '03',
        'annual_median': '13'
    }
    datatype_code = datatype_map.get(datatype, '01')

    latest_year = db.execute(select(func.max(OEData.year))).scalar()
    start_year = latest_year - years if years > 0 else 2000
    years_list = list(range(start_year, latest_year + 1))

    # Parse occupation codes
    occ_codes = occupation_codes.split(',') if occupation_codes else MAJOR_OCCUPATION_GROUPS[:5]

    # Batch query 1: Get occupation names
    occ_query = db.execute(
        select(OEOccupation.occupation_code, OEOccupation.occupation_name)
        .where(OEOccupation.occupation_code.in_(occ_codes))
    ).all()
    occupation_names = {o.occupation_code: o.occupation_name for o in occ_query}

    # Batch query 2: Get all series for these occupations
    series_query = db.execute(
        select(OESeries.series_id, OESeries.occupation_code)
        .where(and_(
            OESeries.occupation_code.in_(occ_codes),
            OESeries.area_code == area_code,
            OESeries.industry_code == industry_code,
            OESeries.datatype_code == datatype_code
        ))
    ).all()
    series_map = {s.occupation_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query 3: Get all data for these series across all years
    data_query = db.execute(
        select(OEData.series_id, OEData.year, OEData.value)
        .where(and_(
            OEData.series_id.in_(all_series_ids),
            OEData.year >= start_year,
            OEData.year <= latest_year
        ))
    ).all() if all_series_ids else []

    # Build data lookup: {(series_id, year): value}
    data_map = {(d.series_id, d.year): decimal_to_float(d.value) for d in data_query}

    # Build timeline
    timeline = []
    for year in years_list:
        point = OEOccupationTimelinePoint(year=year, occupations={})
        for occ_code in occ_codes:
            series_id = series_map.get(occ_code)
            if series_id:
                point.occupations[occ_code] = data_map.get((series_id, year))
            else:
                point.occupations[occ_code] = None
        timeline.append(point)

    return OEOccupationTimelineResponse(
        datatype=datatype,
        timeline=timeline,
        occupation_names=occupation_names
    )


# ============================================================================
# STATE COMPARISON ENDPOINTS
# ============================================================================

@router.get("/states", response_model=OEStateComparisonResponse)
async def get_states(
    occupation_code: str = Query("000000", description="Occupation code"),
    db: Session = Depends(get_data_db)
):
    """Get state-level comparison for an occupation"""
    # Get occupation name
    occupation_name = "All Occupations"
    if occupation_code != "000000":
        occ = db.execute(
            select(OEOccupation.occupation_name)
            .where(OEOccupation.occupation_code == occupation_code)
        ).scalar_one_or_none()
        if occ:
            occupation_name = occ

    # Get latest year
    latest_year = db.execute(select(func.max(OEData.year))).scalar()

    # Get state areas (join series with area to get areatype filter and state_code)
    states = db.execute(
        select(OESeries.state_code, OEArea.area_code, OEArea.area_name)
        .join(OEArea, OESeries.area_code == OEArea.area_code)
        .where(OESeries.areatype_code == 'S')
        .distinct()
        .order_by(OEArea.area_name)
    ).all()

    results = []
    for state in states:
        # Get employment
        emp_series = db.execute(
            select(OESeries.series_id)
            .where(and_(
                OESeries.occupation_code == occupation_code,
                OESeries.area_code == state.area_code,
                OESeries.industry_code == '000000',
                OESeries.datatype_code == '01'
            ))
        ).scalar_one_or_none()

        employment = None
        if emp_series:
            emp = db.execute(
                select(OEData.value)
                .where(and_(OEData.series_id == emp_series, OEData.year == latest_year))
            ).scalar_one_or_none()
            employment = decimal_to_float(emp)

        # Get other metrics
        annual_mean = None
        hourly_mean = None
        emp_per_1000 = None
        location_quotient = None

        for dt_code, attr in [('04', 'annual_mean'), ('03', 'hourly_mean'),
                               ('16', 'emp_per_1000'), ('17', 'location_quotient')]:
            series_id = db.execute(
                select(OESeries.series_id)
                .where(and_(
                    OESeries.occupation_code == occupation_code,
                    OESeries.area_code == state.area_code,
                    OESeries.industry_code == '000000',
                    OESeries.datatype_code == dt_code
                ))
            ).scalar_one_or_none()

            if series_id:
                value = db.execute(
                    select(OEData.value)
                    .where(and_(OEData.series_id == series_id, OEData.year == latest_year))
                ).scalar_one_or_none()
                if attr == 'annual_mean':
                    annual_mean = decimal_to_float(value)
                elif attr == 'hourly_mean':
                    hourly_mean = decimal_to_float(value)
                elif attr == 'emp_per_1000':
                    emp_per_1000 = decimal_to_float(value)
                elif attr == 'location_quotient':
                    location_quotient = decimal_to_float(value)

        results.append(OEStateMetric(
            state_code=state.state_code,
            state_name=state.area_name,
            employment=employment,
            employment_per_1000=emp_per_1000,
            location_quotient=location_quotient,
            hourly_mean=hourly_mean,
            annual_mean=annual_mean,
            latest_year=latest_year
        ))

    return OEStateComparisonResponse(
        occupation_code=occupation_code,
        occupation_name=occupation_name,
        states=results,
        latest_year=latest_year
    )


@router.get("/states/timeline", response_model=OEStateTimelineResponse)
async def get_states_timeline(
    occupation_code: str = Query("000000"),
    datatype: str = Query("annual_mean", description="employment, annual_mean, hourly_mean"),
    state_codes: Optional[str] = Query(None, description="Comma-separated state codes"),
    years: int = Query(10),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for state comparison"""
    datatype_map = {'employment': '01', 'annual_mean': '04', 'hourly_mean': '03'}
    datatype_code = datatype_map.get(datatype, '04')

    # Get occupation name
    occupation_name = "All Occupations"
    if occupation_code != "000000":
        occ = db.execute(
            select(OEOccupation.occupation_name)
            .where(OEOccupation.occupation_code == occupation_code)
        ).scalar_one_or_none()
        if occ:
            occupation_name = occ

    latest_year = db.execute(select(func.max(OEData.year))).scalar()
    start_year = latest_year - years if years > 0 else 2000
    years_list = list(range(start_year, latest_year + 1))

    # Get states - use area table directly for efficiency
    if state_codes:
        codes = state_codes.split(',')
        # State area codes are 7 chars ending in '00000', first 2 chars are state FIPS
        states = db.execute(
            select(OEArea.area_code, OEArea.area_name)
            .where(and_(
                OEArea.area_code.like('%00000'),
                func.length(OEArea.area_code) == 7,
                func.substr(OEArea.area_code, 1, 2).in_(codes)
            ))
        ).all()
    else:
        # Default: first 10 states by code
        states = db.execute(
            select(OEArea.area_code, OEArea.area_name)
            .where(and_(
                OEArea.area_code.like('%00000'),
                func.length(OEArea.area_code) == 7,
                OEArea.area_code != '0000000'
            ))
            .order_by(OEArea.area_code)
            .limit(10)
        ).all()

    state_names = {s.area_code[:2]: s.area_name for s in states}
    area_codes = [s.area_code for s in states]

    # Batch query: Get all series for these areas
    series_query = db.execute(
        select(OESeries.series_id, OESeries.area_code)
        .where(and_(
            OESeries.occupation_code == occupation_code,
            OESeries.area_code.in_(area_codes),
            OESeries.industry_code == '000000',
            OESeries.datatype_code == datatype_code
        ))
    ).all()
    series_map = {s.area_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data for these series across all years
    data_query = db.execute(
        select(OEData.series_id, OEData.year, OEData.value)
        .where(and_(
            OEData.series_id.in_(all_series_ids),
            OEData.year >= start_year,
            OEData.year <= latest_year
        ))
    ).all() if all_series_ids else []

    # Build data lookup: {(series_id, year): value}
    data_map = {(d.series_id, d.year): decimal_to_float(d.value) for d in data_query}

    # Build timeline
    timeline = []
    for year in years_list:
        point = OEStateTimelinePoint(year=year, states={})
        for state in states:
            state_code = state.area_code[:2]
            series_id = series_map.get(state.area_code)
            if series_id:
                point.states[state_code] = data_map.get((series_id, year))
            else:
                point.states[state_code] = None
        timeline.append(point)

    return OEStateTimelineResponse(
        occupation_code=occupation_code,
        occupation_name=occupation_name,
        datatype=datatype,
        timeline=timeline,
        state_names=state_names
    )


# ============================================================================
# INDUSTRY ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/industries", response_model=OEIndustryAnalysisResponse)
async def get_industries(
    occupation_code: str = Query("000000", description="Occupation code"),
    sector_code: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_data_db)
):
    """Get industry-level analysis for an occupation (national level only)"""
    # Get occupation name
    occupation_name = "All Occupations"
    if occupation_code != "000000":
        occ = db.execute(
            select(OEOccupation.occupation_name)
            .where(OEOccupation.occupation_code == occupation_code)
        ).scalar_one_or_none()
        if occ:
            occupation_name = occ

    latest_year = db.execute(select(func.max(OEData.year))).scalar()

    # Get industries - filter by selectable='T' and order by sort_sequence
    ind_query = select(OEIndustry).where(OEIndustry.selectable == 'T')
    if sector_code:
        ind_query = ind_query.where(OEIndustry.industry_code.like(f'{sector_code[:2]}%'))
    ind_query = ind_query.order_by(OEIndustry.sort_sequence).limit(limit * 2)  # Get more to filter
    industries = db.execute(ind_query).scalars().all()

    results = []
    for ind in industries:
        # Get employment (national level only)
        emp_series = db.execute(
            select(OESeries.series_id)
            .where(and_(
                OESeries.occupation_code == occupation_code,
                OESeries.area_code == '0000000',
                OESeries.industry_code == ind.industry_code,
                OESeries.datatype_code == '01'
            ))
        ).scalar_one_or_none()

        employment = None
        if emp_series:
            emp = db.execute(
                select(OEData.value)
                .where(and_(OEData.series_id == emp_series, OEData.year == latest_year))
            ).scalar_one_or_none()
            employment = decimal_to_float(emp)

        if employment is None:
            continue

        # Get wages
        annual_mean = None
        annual_median = None
        hourly_mean = None

        for dt_code, attr in [('04', 'annual_mean'), ('13', 'annual_median'), ('03', 'hourly_mean')]:
            series_id = db.execute(
                select(OESeries.series_id)
                .where(and_(
                    OESeries.occupation_code == occupation_code,
                    OESeries.area_code == '0000000',
                    OESeries.industry_code == ind.industry_code,
                    OESeries.datatype_code == dt_code
                ))
            ).scalar_one_or_none()

            if series_id:
                value = db.execute(
                    select(OEData.value)
                    .where(and_(OEData.series_id == series_id, OEData.year == latest_year))
                ).scalar_one_or_none()
                if attr == 'annual_mean':
                    annual_mean = decimal_to_float(value)
                elif attr == 'annual_median':
                    annual_median = decimal_to_float(value)
                elif attr == 'hourly_mean':
                    hourly_mean = decimal_to_float(value)

        results.append(OEIndustryMetric(
            industry_code=ind.industry_code,
            industry_name=ind.industry_name,
            display_level=ind.display_level,
            employment=employment,
            hourly_mean=hourly_mean,
            annual_mean=annual_mean,
            annual_median=annual_median,
            latest_year=latest_year
        ))

        # Stop if we have enough results
        if len(results) >= limit:
            break

    return OEIndustryAnalysisResponse(
        occupation_code=occupation_code,
        occupation_name=occupation_name,
        industries=results,
        total_count=len(results),
        latest_year=latest_year
    )


@router.get("/industries/timeline", response_model=OEIndustryTimelineResponse)
async def get_industries_timeline(
    occupation_code: str = Query("000000"),
    datatype: str = Query("annual_mean"),
    industry_codes: Optional[str] = Query(None, description="Comma-separated industry codes"),
    years: int = Query(10),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for industry comparison"""
    datatype_map = {'employment': '01', 'annual_mean': '04', 'hourly_mean': '03'}
    datatype_code = datatype_map.get(datatype, '04')

    occupation_name = "All Occupations"
    if occupation_code != "000000":
        occ = db.execute(
            select(OEOccupation.occupation_name)
            .where(OEOccupation.occupation_code == occupation_code)
        ).scalar_one_or_none()
        if occ:
            occupation_name = occ

    latest_year = db.execute(select(func.max(OEData.year))).scalar()
    start_year = latest_year - years if years > 0 else 2000
    years_list = list(range(start_year, latest_year + 1))

    # Parse industry codes
    if industry_codes:
        ind_codes = industry_codes.split(',')
    else:
        ind_codes = ['000000', '000001']

    # Batch query 1: Get industry names
    ind_query = db.execute(
        select(OEIndustry.industry_code, OEIndustry.industry_name)
        .where(OEIndustry.industry_code.in_(ind_codes))
    ).all()
    industry_names = {i.industry_code: i.industry_name for i in ind_query}

    # Batch query 2: Get all series for these industries
    series_query = db.execute(
        select(OESeries.series_id, OESeries.industry_code)
        .where(and_(
            OESeries.occupation_code == occupation_code,
            OESeries.area_code == '0000000',
            OESeries.industry_code.in_(ind_codes),
            OESeries.datatype_code == datatype_code
        ))
    ).all()
    series_map = {s.industry_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query 3: Get all data for these series across all years
    data_query = db.execute(
        select(OEData.series_id, OEData.year, OEData.value)
        .where(and_(
            OEData.series_id.in_(all_series_ids),
            OEData.year >= start_year,
            OEData.year <= latest_year
        ))
    ).all() if all_series_ids else []

    # Build data lookup: {(series_id, year): value}
    data_map = {(d.series_id, d.year): decimal_to_float(d.value) for d in data_query}

    # Build timeline
    timeline = []
    for year in years_list:
        point = OEIndustryTimelinePoint(year=year, industries={})
        for ind_code in ind_codes:
            series_id = series_map.get(ind_code)
            if series_id:
                point.industries[ind_code] = data_map.get((series_id, year))
            else:
                point.industries[ind_code] = None
        timeline.append(point)

    return OEIndustryTimelineResponse(
        occupation_code=occupation_code,
        occupation_name=occupation_name,
        datatype=datatype,
        timeline=timeline,
        industry_names=industry_names
    )


# ============================================================================
# TOP RANKINGS ENDPOINTS
# ============================================================================

@router.get("/top-rankings", response_model=OETopRankingsResponse)
async def get_top_rankings(
    area_code: str = Query("0000000", description="Area code"),
    ranking_type: str = Query("highest_paying", description="highest_paying, most_employed, highest_lq"),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_data_db)
):
    """Get top-ranked occupations by various metrics"""
    area_name = "National"
    if area_code != "0000000":
        area = db.execute(
            select(OEArea.area_name).where(OEArea.area_code == area_code)
        ).scalar_one_or_none()
        if area:
            area_name = area

    latest_year = db.execute(select(func.max(OEData.year))).scalar()

    datatype_map = {
        'highest_paying': '04',
        'most_employed': '01',
        'highest_lq': '17'
    }
    datatype_code = datatype_map.get(ranking_type, '04')

    # Single optimized query: join series, data, and occupations
    ranked_query = db.execute(
        select(
            OESeries.occupation_code,
            OEOccupation.occupation_name,
            OEData.value
        )
        .join(OEData, and_(
            OEData.series_id == OESeries.series_id,
            OEData.year == latest_year
        ))
        .join(OEOccupation, OESeries.occupation_code == OEOccupation.occupation_code)
        .where(and_(
            OESeries.area_code == area_code,
            OESeries.industry_code == '000000',
            OESeries.datatype_code == datatype_code,
            OESeries.occupation_code != '000000',
            OEData.value.isnot(None)
        ))
        .order_by(OEData.value.desc())
        .limit(limit)
    ).all()

    ranked = [{
        'occupation_code': r.occupation_code,
        'occupation_name': r.occupation_name,
        'value': decimal_to_float(r.value)
    } for r in ranked_query]

    return OETopRankingsResponse(
        area_code=area_code,
        area_name=area_name,
        ranking_type=ranking_type,
        occupations=[OETopOccupation(
            occupation_code=r['occupation_code'],
            occupation_name=r['occupation_name'],
            value=r['value'],
            rank=i + 1
        ) for i, r in enumerate(ranked[:limit])],
        latest_year=latest_year
    )


# ============================================================================
# TOP MOVERS ENDPOINT
# ============================================================================

@router.get("/top-movers", response_model=OETopMoversResponse)
async def get_top_movers(
    area_code: str = Query("0000000", description="Area code"),
    metric: str = Query("annual_mean", description="employment or annual_mean"),
    limit: int = Query(10, le=25),
    db: Session = Depends(get_data_db)
):
    """Get occupations with largest year-over-year changes"""
    area_name = "National"
    if area_code != "0000000":
        area = db.execute(
            select(OEArea.area_name).where(OEArea.area_code == area_code)
        ).scalar_one_or_none()
        if area:
            area_name = area

    datatype_code = '01' if metric == 'employment' else '04'

    # Get latest year efficiently (max is faster than distinct)
    latest_year = db.execute(select(func.max(OEData.year))).scalar()
    if not latest_year:
        return OETopMoversResponse(
            area_code=area_code, area_name=area_name, metric=metric,
            gainers=[], losers=[], latest_year=None
        )
    prev_year = latest_year - 1

    # Check if previous year data exists (quick check with limit 1)
    has_prev_year = db.execute(
        select(OEData.year).where(OEData.year == prev_year).limit(1)
    ).scalar_one_or_none()

    if not has_prev_year:
        # Not enough years for YoY comparison
        return OETopMoversResponse(
            area_code=area_code,
            area_name=area_name,
            metric=metric,
            gainers=[],
            losers=[],
            latest_year=latest_year
        )

    # Batch query: Get series with occupation names
    series_query = db.execute(
        select(OESeries.series_id, OESeries.occupation_code, OEOccupation.occupation_name)
        .join(OEOccupation, OESeries.occupation_code == OEOccupation.occupation_code)
        .where(and_(
            OESeries.area_code == area_code,
            OESeries.industry_code == '000000',
            OESeries.datatype_code == datatype_code,
            OESeries.occupation_code != '000000'
        ))
    ).all()

    if not series_query:
        return OETopMoversResponse(
            area_code=area_code, area_name=area_name, metric=metric,
            gainers=[], losers=[], latest_year=latest_year
        )

    series_ids = [s.series_id for s in series_query]
    series_info = {s.series_id: (s.occupation_code, s.occupation_name) for s in series_query}

    # Batch query: Get current and previous year data
    data_query = db.execute(
        select(OEData.series_id, OEData.year, OEData.value)
        .where(and_(
            OEData.series_id.in_(series_ids),
            OEData.year.in_([latest_year, prev_year])
        ))
    ).all()

    # Build data lookup: {series_id: {year: value}}
    data_map = {}
    for d in data_query:
        if d.series_id not in data_map:
            data_map[d.series_id] = {}
        data_map[d.series_id][d.year] = decimal_to_float(d.value)

    # Calculate changes
    changes = []
    for series_id, (occ_code, occ_name) in series_info.items():
        series_data = data_map.get(series_id, {})
        curr_val = series_data.get(latest_year)
        prev_val = series_data.get(prev_year)

        if curr_val and prev_val and prev_val > 0:
            change = curr_val - prev_val
            change_pct = ((curr_val - prev_val) / prev_val) * 100
            changes.append({
                'occupation_code': occ_code,
                'occupation_name': occ_name,
                'value': curr_val,
                'prev_value': prev_val,
                'change': change,
                'change_pct': change_pct
            })

    # Sort by change_pct
    gainers = sorted([c for c in changes if c['change_pct'] > 0],
                     key=lambda x: x['change_pct'], reverse=True)[:limit]
    losers = sorted([c for c in changes if c['change_pct'] < 0],
                    key=lambda x: x['change_pct'])[:limit]

    return OETopMoversResponse(
        area_code=area_code,
        area_name=area_name,
        metric=metric,
        gainers=[OETopMover(
            occupation_code=g['occupation_code'],
            occupation_name=g['occupation_name'],
            value=g['value'],
            prev_value=g['prev_value'],
            change=g['change'],
            change_pct=round(g['change_pct'], 2),
            latest_year=latest_year
        ) for g in gainers],
        losers=[OETopMover(
            occupation_code=l['occupation_code'],
            occupation_name=l['occupation_name'],
            value=l['value'],
            prev_value=l['prev_value'],
            change=l['change'],
            change_pct=round(l['change_pct'], 2),
            latest_year=latest_year
        ) for l in losers],
        latest_year=latest_year
    )


# ============================================================================
# WAGE DISTRIBUTION ENDPOINT
# ============================================================================

@router.get("/wage-distribution", response_model=OEWageDistributionResponse)
async def get_wage_distribution(
    occupation_code: str = Query(..., description="Occupation code"),
    area_code: str = Query("0000000", description="Area code"),
    db: Session = Depends(get_data_db)
):
    """Get complete wage distribution for an occupation in an area"""
    # Get names
    occupation_name = db.execute(
        select(OEOccupation.occupation_name)
        .where(OEOccupation.occupation_code == occupation_code)
    ).scalar_one_or_none() or occupation_code

    area_name = "National"
    if area_code != "0000000":
        area = db.execute(
            select(OEArea.area_name).where(OEArea.area_code == area_code)
        ).scalar_one_or_none()
        if area:
            area_name = area

    latest_year = db.execute(select(func.max(OEData.year))).scalar()

    # Get all wage data types
    wage_data = {}
    datatype_map = {
        '03': 'hourly_mean', '06': 'hourly_10th', '07': 'hourly_25th',
        '08': 'hourly_median', '09': 'hourly_75th', '10': 'hourly_90th',
        '04': 'annual_mean', '11': 'annual_10th', '12': 'annual_25th',
        '13': 'annual_median', '14': 'annual_75th', '15': 'annual_90th'
    }

    for dt_code, field in datatype_map.items():
        series_id = db.execute(
            select(OESeries.series_id)
            .where(and_(
                OESeries.occupation_code == occupation_code,
                OESeries.area_code == area_code,
                OESeries.industry_code == '000000',
                OESeries.datatype_code == dt_code
            ))
        ).scalar_one_or_none()

        if series_id:
            value = db.execute(
                select(OEData.value)
                .where(and_(OEData.series_id == series_id, OEData.year == latest_year))
            ).scalar_one_or_none()
            wage_data[field] = decimal_to_float(value)
        else:
            wage_data[field] = None

    return OEWageDistributionResponse(
        distributions=[OEWageDistribution(
            occupation_code=occupation_code,
            occupation_name=occupation_name,
            area_code=area_code,
            area_name=area_name,
            latest_year=latest_year,
            **wage_data
        )]
    )


# ============================================================================
# OCCUPATION PROFILE ENDPOINT
# ============================================================================

@router.get("/occupation-profile", response_model=OEOccupationProfileResponse)
async def get_occupation_profile(
    occupation_code: str = Query(..., description="Occupation code"),
    area_code: str = Query("0000000", description="Area code"),
    industry_code: str = Query("000000", description="Industry code"),
    db: Session = Depends(get_data_db)
):
    """Get complete profile for an occupation including all metrics"""
    # Get occupation info
    occ = db.execute(
        select(OEOccupation)
        .where(OEOccupation.occupation_code == occupation_code)
    ).scalar_one_or_none()

    if not occ:
        raise HTTPException(status_code=404, detail=f"Occupation {occupation_code} not found")

    # Get area and industry names
    area_name = "National"
    if area_code != "0000000":
        area = db.execute(
            select(OEArea.area_name).where(OEArea.area_code == area_code)
        ).scalar_one_or_none()
        if area:
            area_name = area

    industry_name = "All Industries"
    if industry_code != "000000":
        ind = db.execute(
            select(OEIndustry.industry_name).where(OEIndustry.industry_code == industry_code)
        ).scalar_one_or_none()
        if ind:
            industry_name = ind

    latest_year = db.execute(select(func.max(OEData.year))).scalar()

    # Get all data types
    profile_data = {}
    datatype_map = {
        '01': 'employment', '02': 'employment_rse',
        '03': 'hourly_mean', '04': 'annual_mean', '05': 'wage_rse',
        '06': 'hourly_10th', '07': 'hourly_25th', '08': 'hourly_median',
        '09': 'hourly_75th', '10': 'hourly_90th',
        '11': 'annual_10th', '12': 'annual_25th', '13': 'annual_median',
        '14': 'annual_75th', '15': 'annual_90th',
        '16': 'employment_per_1000', '17': 'location_quotient'
    }

    for dt_code, field in datatype_map.items():
        series_id = db.execute(
            select(OESeries.series_id)
            .where(and_(
                OESeries.occupation_code == occupation_code,
                OESeries.area_code == area_code,
                OESeries.industry_code == industry_code,
                OESeries.datatype_code == dt_code
            ))
        ).scalar_one_or_none()

        if series_id:
            value = db.execute(
                select(OEData.value)
                .where(and_(OEData.series_id == series_id, OEData.year == latest_year))
            ).scalar_one_or_none()
            profile_data[field] = decimal_to_float(value)
        else:
            profile_data[field] = None

    return OEOccupationProfileResponse(
        occupation=OEOccupationWageProfile(
            occupation_code=occupation_code,
            occupation_name=occ.occupation_name,
            occupation_description=occ.occupation_description,
            area_code=area_code,
            area_name=area_name,
            industry_code=industry_code,
            industry_name=industry_name,
            latest_year=latest_year,
            **profile_data
        )
    )
