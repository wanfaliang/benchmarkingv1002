"""
JT (Job Openings and Labor Turnover Survey - JOLTS) Explorer API

JOLTS provides national estimates of rates and levels for:
- Job openings, Hires, Total separations, Quits, Layoffs and discharges

Data available from December 2000 to present, monthly.
Geographic coverage: Total US, 4 regions (Northeast, Midwest, South, West), and individual states
Industry coverage: Total nonfarm + major supersectors/sectors
Size class breakdown available for total nonfarm
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List, Dict

from ....database import get_data_db
from ....api.auth import get_current_user
from ....core.cache import cached, DataCategory
from .jt_schemas import (
    JTDimensions, JTIndustryItem, JTStateItem, JTDataElementItem,
    JTSizeClassItem, JTRateLevelItem,
    JTSeriesInfo, JTSeriesListResponse,
    JTDataPoint, JTSeriesData, JTDataResponse,
    JTMetric, JTOverviewResponse, JTOverviewTimelinePoint, JTOverviewTimelineResponse,
    JTIndustryMetric, JTIndustryAnalysisResponse,
    JTIndustryTimelinePoint, JTIndustryTimelineResponse,
    JTRegionMetric, JTRegionAnalysisResponse,
    JTRegionTimelinePoint, JTRegionTimelineResponse,
    JTSizeClassMetric, JTSizeClassAnalysisResponse,
    JTSizeClassTimelinePoint, JTSizeClassTimelineResponse,
    JTTopMover, JTTopMoversResponse
)
from ....data_models.bls_models import (
    JTIndustry, JTState, JTDataElement, JTSizeClass, JTRateLevel,
    JTSeries, JTData, BLSPeriod
)

router = APIRouter(
    prefix="/api/research/bls/jt",
    tags=["BLS JT - JOLTS (Job Openings and Labor Turnover)"]
)


# Data element codes
DATA_ELEMENTS = {
    'JO': 'Job openings',
    'HI': 'Hires',
    'TS': 'Total separations',
    'QU': 'Quits',
    'LD': 'Layoffs and discharges',
    'OS': 'Other separations',
    'UO': 'Unemployed persons per job opening ratio',
}

# Region codes
REGIONS = {'NE': 'Northeast', 'MW': 'Midwest', 'SO': 'South', 'WE': 'West'}


def _get_period_name(year: int, period: str, db: Session) -> str:
    """Get human-readable period name"""
    period_info = db.query(BLSPeriod).filter(BLSPeriod.period_code == period).first()
    if period_info:
        return f"{period_info.period_name} {year}"

    month_map = {
        'M01': 'January', 'M02': 'February', 'M03': 'March', 'M04': 'April',
        'M05': 'May', 'M06': 'June', 'M07': 'July', 'M08': 'August',
        'M09': 'September', 'M10': 'October', 'M11': 'November', 'M12': 'December',
        'M13': 'Annual Average'
    }
    return f"{month_map.get(period, period)} {year}"


def _calculate_jolts_metric(
    db: Session,
    industry_code: str,
    state_code: str,
    dataelement_code: str,
    ratelevel_code: str,
    seasonal: str = 'S'
) -> Optional[JTMetric]:
    """Calculate JOLTS metrics for a specific series combination"""

    # Find the series
    series = db.query(JTSeries).filter(
        JTSeries.industry_code == industry_code,
        JTSeries.state_code == state_code,
        JTSeries.dataelement_code == dataelement_code,
        JTSeries.ratelevel_code == ratelevel_code,
        JTSeries.seasonal == seasonal,
        JTSeries.area_code == '00000',
        JTSeries.sizeclass_code == '00'
    ).first()

    if not series:
        return None

    # Get recent data (14 months)
    data = db.query(JTData).filter(
        JTData.series_id == series.series_id,
        JTData.period.like('M%'),
        JTData.period != 'M13'
    ).order_by(desc(JTData.year), desc(JTData.period)).limit(14).all()

    if not data:
        return None

    latest = data[0]
    prev_month = data[1] if len(data) > 1 else None

    # Find same month last year
    prev_year = None
    for d in data:
        if d.year == latest.year - 1 and d.period == latest.period:
            prev_year = d
            break

    latest_value = float(latest.value) if latest.value else None
    mom = None
    mom_pct = None
    yoy = None
    yoy_pct = None

    if latest_value is not None and prev_month and prev_month.value:
        prev_val = float(prev_month.value)
        mom = round(latest_value - prev_val, 1)
        if prev_val != 0:
            mom_pct = round(((latest_value - prev_val) / prev_val) * 100, 2)

    if latest_value is not None and prev_year and prev_year.value:
        prev_val = float(prev_year.value)
        yoy = round(latest_value - prev_val, 1)
        if prev_val != 0:
            yoy_pct = round(((latest_value - prev_val) / prev_val) * 100, 2)

    element = db.query(JTDataElement).filter(JTDataElement.dataelement_code == dataelement_code).first()

    return JTMetric(
        series_id=series.series_id,
        dataelement_code=dataelement_code,
        dataelement_name=element.dataelement_text if element else dataelement_code,
        ratelevel_code=ratelevel_code,
        value=latest_value,
        latest_date=_get_period_name(latest.year, latest.period, db),
        month_over_month=mom,
        month_over_month_pct=mom_pct,
        year_over_year=yoy,
        year_over_year_pct=yoy_pct
    )


# =============================================================================
# DIMENSIONS ENDPOINT
# =============================================================================

@router.get("/dimensions", response_model=JTDimensions)
async def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get available dimensions for JT (JOLTS) data filtering"""

    # Get industries
    industries = db.query(JTIndustry).order_by(JTIndustry.sort_sequence).all()
    industry_items = [
        JTIndustryItem(
            industry_code=i.industry_code,
            industry_name=i.industry_text,
            display_level=i.display_level,
            selectable=i.selectable == 'T'
        )
        for i in industries
    ]

    # Get states/regions
    states = db.query(JTState).order_by(JTState.sort_sequence).all()
    state_items = [
        JTStateItem(
            state_code=s.state_code,
            state_name=s.state_text,
            display_level=s.display_level,
            selectable=s.selectable == 'T'
        )
        for s in states
    ]

    # Get data elements
    elements = db.query(JTDataElement).order_by(JTDataElement.sort_sequence).all()
    element_items = [
        JTDataElementItem(
            dataelement_code=e.dataelement_code,
            dataelement_name=e.dataelement_text,
            display_level=e.display_level
        )
        for e in elements
    ]

    # Get size classes
    sizes = db.query(JTSizeClass).order_by(JTSizeClass.sort_sequence).all()
    size_items = [
        JTSizeClassItem(
            sizeclass_code=s.sizeclass_code,
            sizeclass_name=s.sizeclass_text
        )
        for s in sizes
    ]

    # Get rate/level
    ratelevels = db.query(JTRateLevel).order_by(JTRateLevel.sort_sequence).all()
    ratelevel_items = [
        JTRateLevelItem(
            ratelevel_code=r.ratelevel_code,
            ratelevel_name=r.ratelevel_text
        )
        for r in ratelevels
    ]

    return JTDimensions(
        industries=industry_items,
        states=state_items,
        data_elements=element_items,
        size_classes=size_items,
        rate_levels=ratelevel_items
    )


# =============================================================================
# SERIES ENDPOINTS
# =============================================================================

@router.get("/series", response_model=JTSeriesListResponse)
async def get_series(
    industry_code: Optional[str] = Query(None, description="Filter by industry"),
    state_code: Optional[str] = Query(None, description="Filter by state/region"),
    dataelement_code: Optional[str] = Query(None, description="Filter by data element (JO/HI/TS/QU/LD)"),
    ratelevel_code: Optional[str] = Query(None, description="Filter by rate/level (R/L)"),
    sizeclass_code: Optional[str] = Query(None, description="Filter by size class"),
    seasonal: Optional[str] = Query(None, description="Filter by seasonal (S/U)"),
    search: Optional[str] = Query(None, description="Search by industry or state name"),
    active_only: bool = Query(True, description="Only active series"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get JT (JOLTS) series list with optional filters"""

    query = db.query(
        JTSeries,
        JTIndustry.industry_text,
        JTState.state_text,
        JTDataElement.dataelement_text,
        JTSizeClass.sizeclass_text,
        JTRateLevel.ratelevel_text
    ).outerjoin(
        JTIndustry, JTSeries.industry_code == JTIndustry.industry_code
    ).outerjoin(
        JTState, JTSeries.state_code == JTState.state_code
    ).outerjoin(
        JTDataElement, JTSeries.dataelement_code == JTDataElement.dataelement_code
    ).outerjoin(
        JTSizeClass, JTSeries.sizeclass_code == JTSizeClass.sizeclass_code
    ).outerjoin(
        JTRateLevel, JTSeries.ratelevel_code == JTRateLevel.ratelevel_code
    )

    if industry_code:
        query = query.filter(JTSeries.industry_code == industry_code)
    if state_code:
        query = query.filter(JTSeries.state_code == state_code)
    if dataelement_code:
        query = query.filter(JTSeries.dataelement_code == dataelement_code)
    if ratelevel_code:
        query = query.filter(JTSeries.ratelevel_code == ratelevel_code)
    if sizeclass_code:
        query = query.filter(JTSeries.sizeclass_code == sizeclass_code)
    if seasonal:
        query = query.filter(JTSeries.seasonal == seasonal)
    if search:
        query = query.filter(
            or_(
                JTIndustry.industry_text.ilike(f"%{search}%"),
                JTState.state_text.ilike(f"%{search}%")
            )
        )
    if active_only:
        query = query.filter(JTSeries.is_active == True)

    total = query.count()
    results = query.order_by(JTSeries.series_id).offset(offset).limit(limit).all()

    series = [
        JTSeriesInfo(
            series_id=r.JTSeries.series_id,
            industry_code=r.JTSeries.industry_code,
            industry_name=r.industry_text,
            state_code=r.JTSeries.state_code,
            state_name=r.state_text,
            area_code=r.JTSeries.area_code,
            sizeclass_code=r.JTSeries.sizeclass_code,
            sizeclass_name=r.sizeclass_text,
            dataelement_code=r.JTSeries.dataelement_code,
            dataelement_name=r.dataelement_text,
            ratelevel_code=r.JTSeries.ratelevel_code,
            ratelevel_name=r.ratelevel_text,
            seasonal_code=r.JTSeries.seasonal,
            begin_year=r.JTSeries.begin_year,
            begin_period=r.JTSeries.begin_period,
            end_year=r.JTSeries.end_year,
            end_period=r.JTSeries.end_period,
            is_active=r.JTSeries.is_active if r.JTSeries.is_active is not None else True
        )
        for r in results
    ]

    return JTSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series
    )


@router.get("/series/{series_id}/data", response_model=JTDataResponse)
async def get_series_data(
    series_id: str,
    months: int = Query(60, ge=1, le=600, description="Number of months of data"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get time series data for a specific JT (JOLTS) series"""

    series = db.query(
        JTSeries,
        JTIndustry.industry_text,
        JTState.state_text,
        JTDataElement.dataelement_text,
        JTRateLevel.ratelevel_text
    ).outerjoin(
        JTIndustry, JTSeries.industry_code == JTIndustry.industry_code
    ).outerjoin(
        JTState, JTSeries.state_code == JTState.state_code
    ).outerjoin(
        JTDataElement, JTSeries.dataelement_code == JTDataElement.dataelement_code
    ).outerjoin(
        JTRateLevel, JTSeries.ratelevel_code == JTRateLevel.ratelevel_code
    ).filter(
        JTSeries.series_id == series_id
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    data = db.query(JTData).filter(
        JTData.series_id == series_id,
        JTData.period.like('M%'),
        JTData.period != 'M13'
    ).order_by(desc(JTData.year), desc(JTData.period)).limit(months).all()

    data_points = [
        JTDataPoint(
            year=d.year,
            period=d.period,
            period_name=_get_period_name(d.year, d.period, db),
            value=float(d.value) if d.value else None,
            footnote_codes=d.footnote_codes
        )
        for d in reversed(data)
    ]

    return JTDataResponse(
        series=[JTSeriesData(
            series_id=series_id,
            industry_name=series.industry_text,
            state_name=series.state_text,
            dataelement_name=series.dataelement_text,
            ratelevel_name=series.ratelevel_text,
            data_points=data_points
        )]
    )


# =============================================================================
# OVERVIEW ENDPOINT
# =============================================================================

@router.get("/overview", response_model=JTOverviewResponse)
@cached("bls:jt:overview", category=DataCategory.BLS_MONTHLY, param_keys=["industry_code", "state_code"])
async def get_overview(
    industry_code: str = Query("000000", description="Industry code (default: Total nonfarm)"),
    state_code: str = Query("00", description="State/region code (default: Total US)"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get JOLTS overview with all key metrics (rates and levels)"""

    industry = db.query(JTIndustry).filter(JTIndustry.industry_code == industry_code).first()
    state = db.query(JTState).filter(JTState.state_code == state_code).first()

    # Get all metrics
    response = JTOverviewResponse(
        industry_code=industry_code,
        industry_name=industry.industry_text if industry else None,
        state_code=state_code,
        state_name=state.state_text if state else None,
        job_openings_rate=_calculate_jolts_metric(db, industry_code, state_code, 'JO', 'R'),
        hires_rate=_calculate_jolts_metric(db, industry_code, state_code, 'HI', 'R'),
        total_separations_rate=_calculate_jolts_metric(db, industry_code, state_code, 'TS', 'R'),
        quits_rate=_calculate_jolts_metric(db, industry_code, state_code, 'QU', 'R'),
        layoffs_rate=_calculate_jolts_metric(db, industry_code, state_code, 'LD', 'R'),
        job_openings_level=_calculate_jolts_metric(db, industry_code, state_code, 'JO', 'L'),
        hires_level=_calculate_jolts_metric(db, industry_code, state_code, 'HI', 'L'),
        total_separations_level=_calculate_jolts_metric(db, industry_code, state_code, 'TS', 'L'),
        quits_level=_calculate_jolts_metric(db, industry_code, state_code, 'QU', 'L'),
        layoffs_level=_calculate_jolts_metric(db, industry_code, state_code, 'LD', 'L'),
        unemployed_per_opening=_calculate_jolts_metric(db, industry_code, state_code, 'UO', 'R')
    )

    # Get last updated from any available metric
    for metric in [response.job_openings_rate, response.hires_rate, response.quits_rate]:
        if metric and metric.latest_date:
            response.last_updated = metric.latest_date
            break

    return response


@router.get("/overview/timeline", response_model=JTOverviewTimelineResponse)
async def get_overview_timeline(
    industry_code: str = Query("000000", description="Industry code"),
    state_code: str = Query("00", description="State/region code"),
    months: int = Query(60, ge=12, le=300, description="Number of months"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get timeline data for JOLTS overview charts"""

    industry = db.query(JTIndustry).filter(JTIndustry.industry_code == industry_code).first()
    state = db.query(JTState).filter(JTState.state_code == state_code).first()

    # Build series mapping
    series_map: Dict[str, str] = {}  # key -> series_id
    for elem in ['JO', 'HI', 'TS', 'QU', 'LD']:
        for rl in ['R', 'L']:
            key = f"{elem}_{rl}"
            series = db.query(JTSeries).filter(
                JTSeries.industry_code == industry_code,
                JTSeries.state_code == state_code,
                JTSeries.dataelement_code == elem,
                JTSeries.ratelevel_code == rl,
                JTSeries.seasonal == 'S',
                JTSeries.area_code == '00000',
                JTSeries.sizeclass_code == '00'
            ).first()
            if series:
                series_map[key] = series.series_id

    if not series_map:
        return JTOverviewTimelineResponse(
            industry_name=industry.industry_text if industry else None,
            state_name=state.state_text if state else None,
            timeline=[]
        )

    # Get data for all series
    all_data: Dict[str, Dict[str, float]] = {}  # {year-period: {key: value}}

    for key, series_id in series_map.items():
        data = db.query(JTData).filter(
            JTData.series_id == series_id,
            JTData.period.like('M%'),
            JTData.period != 'M13'
        ).order_by(desc(JTData.year), desc(JTData.period)).limit(months).all()

        for d in data:
            period_key = f"{d.year}-{d.period}"
            if period_key not in all_data:
                all_data[period_key] = {'year': d.year, 'period': d.period}
            if d.value is not None:
                all_data[period_key][key] = float(d.value)

    # Convert to timeline
    timeline = []
    for period_key in sorted(all_data.keys()):
        d = all_data[period_key]
        timeline.append(JTOverviewTimelinePoint(
            year=d['year'],
            period=d['period'],
            period_name=_get_period_name(d['year'], d['period'], db),
            job_openings_rate=d.get('JO_R'),
            hires_rate=d.get('HI_R'),
            total_separations_rate=d.get('TS_R'),
            quits_rate=d.get('QU_R'),
            layoffs_rate=d.get('LD_R'),
            job_openings_level=d.get('JO_L'),
            hires_level=d.get('HI_L'),
            total_separations_level=d.get('TS_L'),
            quits_level=d.get('QU_L'),
            layoffs_level=d.get('LD_L')
        ))

    return JTOverviewTimelineResponse(
        industry_name=industry.industry_text if industry else None,
        state_name=state.state_text if state else None,
        timeline=timeline
    )


# =============================================================================
# INDUSTRY ANALYSIS ENDPOINTS
# =============================================================================

@router.get("/industries", response_model=JTIndustryAnalysisResponse)
async def get_industry_analysis(
    state_code: str = Query("00", description="State/region code"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get JOLTS metrics by industry for a given state/region"""

    state = db.query(JTState).filter(JTState.state_code == state_code).first()
    industries = db.query(JTIndustry).order_by(JTIndustry.sort_sequence).all()

    result = []
    last_updated = None

    for ind in industries:
        # Get key metrics for this industry
        jo_rate = _calculate_jolts_metric(db, ind.industry_code, state_code, 'JO', 'R')
        hi_rate = _calculate_jolts_metric(db, ind.industry_code, state_code, 'HI', 'R')
        qu_rate = _calculate_jolts_metric(db, ind.industry_code, state_code, 'QU', 'R')
        ld_rate = _calculate_jolts_metric(db, ind.industry_code, state_code, 'LD', 'R')
        ts_rate = _calculate_jolts_metric(db, ind.industry_code, state_code, 'TS', 'R')
        jo_level = _calculate_jolts_metric(db, ind.industry_code, state_code, 'JO', 'L')

        if jo_rate or hi_rate or jo_level:
            if jo_rate and jo_rate.latest_date:
                last_updated = jo_rate.latest_date

            result.append(JTIndustryMetric(
                industry_code=ind.industry_code,
                industry_name=ind.industry_text,
                display_level=ind.display_level,
                job_openings_rate=jo_rate.value if jo_rate else None,
                hires_rate=hi_rate.value if hi_rate else None,
                quits_rate=qu_rate.value if qu_rate else None,
                layoffs_rate=ld_rate.value if ld_rate else None,
                total_separations_rate=ts_rate.value if ts_rate else None,
                job_openings_level=jo_level.value if jo_level else None,
                job_openings_yoy_pct=jo_rate.year_over_year_pct if jo_rate else None,
                hires_yoy_pct=hi_rate.year_over_year_pct if hi_rate else None,
                quits_yoy_pct=qu_rate.year_over_year_pct if qu_rate else None,
                latest_date=jo_rate.latest_date if jo_rate else None
            ))

    return JTIndustryAnalysisResponse(
        state_code=state_code,
        state_name=state.state_text if state else None,
        industries=result,
        last_updated=last_updated
    )


@router.get("/industries/timeline", response_model=JTIndustryTimelineResponse)
async def get_industry_timeline(
    dataelement_code: str = Query("JO", description="Data element (JO/HI/TS/QU/LD)"),
    ratelevel_code: str = Query("R", description="Rate (R) or Level (L)"),
    state_code: str = Query("00", description="State/region code"),
    months: int = Query(60, ge=12, le=300),
    industry_codes: Optional[str] = Query(None, description="Comma-separated industry codes"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get timeline data for industry comparison"""

    element = db.query(JTDataElement).filter(JTDataElement.dataelement_code == dataelement_code).first()

    # Default industries if not specified
    if industry_codes:
        codes = [c.strip() for c in industry_codes.split(',')]
    else:
        codes = ['000000', '100000', '300000', '540099', '620000', '720000']

    # Get series for each industry
    series_map: Dict[str, str] = {}
    industry_names: Dict[str, str] = {}

    for code in codes:
        series = db.query(JTSeries, JTIndustry.industry_text).outerjoin(
            JTIndustry, JTSeries.industry_code == JTIndustry.industry_code
        ).filter(
            JTSeries.industry_code == code,
            JTSeries.state_code == state_code,
            JTSeries.dataelement_code == dataelement_code,
            JTSeries.ratelevel_code == ratelevel_code,
            JTSeries.seasonal == 'S',
            JTSeries.area_code == '00000',
            JTSeries.sizeclass_code == '00'
        ).first()

        if series:
            series_map[code] = series.JTSeries.series_id
            industry_names[code] = series.industry_text or code

    # Get data
    all_data: Dict[str, Dict[str, float]] = {}

    for code, series_id in series_map.items():
        data = db.query(JTData).filter(
            JTData.series_id == series_id,
            JTData.period.like('M%'),
            JTData.period != 'M13'
        ).order_by(desc(JTData.year), desc(JTData.period)).limit(months).all()

        for d in data:
            period_key = f"{d.year}-{d.period}"
            if period_key not in all_data:
                all_data[period_key] = {'year': d.year, 'period': d.period}
            if d.value is not None:
                all_data[period_key][code] = float(d.value)

    timeline = []
    for period_key in sorted(all_data.keys()):
        d = all_data[period_key]
        industries_dict = {code: d.get(code) for code in codes}
        timeline.append(JTIndustryTimelinePoint(
            year=d['year'],
            period=d['period'],
            period_name=_get_period_name(d['year'], d['period'], db),
            industries=industries_dict
        ))

    return JTIndustryTimelineResponse(
        dataelement_code=dataelement_code,
        dataelement_name=element.dataelement_text if element else dataelement_code,
        ratelevel_code=ratelevel_code,
        timeline=timeline,
        industry_names=industry_names
    )


# =============================================================================
# REGIONAL ANALYSIS ENDPOINTS
# =============================================================================

@router.get("/regions", response_model=JTRegionAnalysisResponse)
async def get_region_analysis(
    industry_code: str = Query("000000", description="Industry code"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get JOLTS metrics by region/state"""

    industry = db.query(JTIndustry).filter(JTIndustry.industry_code == industry_code).first()
    states = db.query(JTState).order_by(JTState.sort_sequence).all()

    result = []
    last_updated = None

    for state in states:
        jo_rate = _calculate_jolts_metric(db, industry_code, state.state_code, 'JO', 'R')
        hi_rate = _calculate_jolts_metric(db, industry_code, state.state_code, 'HI', 'R')
        qu_rate = _calculate_jolts_metric(db, industry_code, state.state_code, 'QU', 'R')
        ld_rate = _calculate_jolts_metric(db, industry_code, state.state_code, 'LD', 'R')
        ts_rate = _calculate_jolts_metric(db, industry_code, state.state_code, 'TS', 'R')
        jo_level = _calculate_jolts_metric(db, industry_code, state.state_code, 'JO', 'L')

        if jo_rate or hi_rate:
            if jo_rate and jo_rate.latest_date:
                last_updated = jo_rate.latest_date

            result.append(JTRegionMetric(
                state_code=state.state_code,
                state_name=state.state_text,
                is_region=state.state_code in REGIONS,
                job_openings_rate=jo_rate.value if jo_rate else None,
                hires_rate=hi_rate.value if hi_rate else None,
                quits_rate=qu_rate.value if qu_rate else None,
                layoffs_rate=ld_rate.value if ld_rate else None,
                total_separations_rate=ts_rate.value if ts_rate else None,
                job_openings_level=jo_level.value if jo_level else None,
                job_openings_yoy_pct=jo_rate.year_over_year_pct if jo_rate else None,
                latest_date=jo_rate.latest_date if jo_rate else None
            ))

    return JTRegionAnalysisResponse(
        industry_code=industry_code,
        industry_name=industry.industry_text if industry else None,
        regions=result,
        last_updated=last_updated
    )


@router.get("/regions/timeline", response_model=JTRegionTimelineResponse)
async def get_region_timeline(
    dataelement_code: str = Query("JO", description="Data element"),
    ratelevel_code: str = Query("R", description="Rate or Level"),
    industry_code: str = Query("000000", description="Industry code"),
    months: int = Query(60, ge=12, le=300),
    state_codes: Optional[str] = Query(None, description="Comma-separated state/region codes"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get timeline data for region comparison"""

    element = db.query(JTDataElement).filter(JTDataElement.dataelement_code == dataelement_code).first()

    # Default to regions + total US
    if state_codes:
        codes = [c.strip() for c in state_codes.split(',')]
    else:
        codes = ['00', 'NE', 'MW', 'SO', 'WE']

    series_map: Dict[str, str] = {}
    region_names: Dict[str, str] = {}

    for code in codes:
        series = db.query(JTSeries, JTState.state_text).outerjoin(
            JTState, JTSeries.state_code == JTState.state_code
        ).filter(
            JTSeries.industry_code == industry_code,
            JTSeries.state_code == code,
            JTSeries.dataelement_code == dataelement_code,
            JTSeries.ratelevel_code == ratelevel_code,
            JTSeries.seasonal == 'S',
            JTSeries.area_code == '00000',
            JTSeries.sizeclass_code == '00'
        ).first()

        if series:
            series_map[code] = series.JTSeries.series_id
            region_names[code] = series.state_text or code

    all_data: Dict[str, Dict[str, float]] = {}

    for code, series_id in series_map.items():
        data = db.query(JTData).filter(
            JTData.series_id == series_id,
            JTData.period.like('M%'),
            JTData.period != 'M13'
        ).order_by(desc(JTData.year), desc(JTData.period)).limit(months).all()

        for d in data:
            period_key = f"{d.year}-{d.period}"
            if period_key not in all_data:
                all_data[period_key] = {'year': d.year, 'period': d.period}
            if d.value is not None:
                all_data[period_key][code] = float(d.value)

    timeline = []
    for period_key in sorted(all_data.keys()):
        d = all_data[period_key]
        regions_dict = {code: d.get(code) for code in codes}
        timeline.append(JTRegionTimelinePoint(
            year=d['year'],
            period=d['period'],
            period_name=_get_period_name(d['year'], d['period'], db),
            regions=regions_dict
        ))

    return JTRegionTimelineResponse(
        dataelement_code=dataelement_code,
        dataelement_name=element.dataelement_text if element else dataelement_code,
        ratelevel_code=ratelevel_code,
        timeline=timeline,
        region_names=region_names
    )


# =============================================================================
# SIZE CLASS ANALYSIS ENDPOINTS
# =============================================================================

@router.get("/sizeclasses", response_model=JTSizeClassAnalysisResponse)
async def get_sizeclass_analysis(
    industry_code: str = Query("000000", description="Industry code (only Total nonfarm has size class data)"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get JOLTS metrics by establishment size class"""

    industry = db.query(JTIndustry).filter(JTIndustry.industry_code == industry_code).first()
    sizes = db.query(JTSizeClass).order_by(JTSizeClass.sort_sequence).all()

    result = []
    last_updated = None

    for size in sizes:
        # Size class data only available for Total nonfarm (000000) and Total US (00)
        series = db.query(JTSeries).filter(
            JTSeries.industry_code == '000000',
            JTSeries.state_code == '00',
            JTSeries.sizeclass_code == size.sizeclass_code,
            JTSeries.dataelement_code == 'JO',
            JTSeries.ratelevel_code == 'R',
            JTSeries.seasonal == 'S',
            JTSeries.area_code == '00000'
        ).first()

        if not series:
            continue

        # Get data
        data = db.query(JTData).filter(
            JTData.series_id == series.series_id,
            JTData.period.like('M%'),
            JTData.period != 'M13'
        ).order_by(desc(JTData.year), desc(JTData.period)).limit(1).first()

        if data:
            if not last_updated:
                last_updated = _get_period_name(data.year, data.period, db)

            # Get other metrics for this size class
            metrics = {}
            for elem in ['JO', 'HI', 'QU', 'LD', 'TS']:
                s = db.query(JTSeries).filter(
                    JTSeries.industry_code == '000000',
                    JTSeries.state_code == '00',
                    JTSeries.sizeclass_code == size.sizeclass_code,
                    JTSeries.dataelement_code == elem,
                    JTSeries.ratelevel_code == 'R',
                    JTSeries.seasonal == 'S',
                    JTSeries.area_code == '00000'
                ).first()

                if s:
                    d = db.query(JTData).filter(
                        JTData.series_id == s.series_id,
                        JTData.period.like('M%'),
                        JTData.period != 'M13'
                    ).order_by(desc(JTData.year), desc(JTData.period)).limit(1).first()

                    if d and d.value:
                        metrics[elem] = float(d.value)

            result.append(JTSizeClassMetric(
                sizeclass_code=size.sizeclass_code,
                sizeclass_name=size.sizeclass_text,
                job_openings_rate=metrics.get('JO'),
                hires_rate=metrics.get('HI'),
                quits_rate=metrics.get('QU'),
                layoffs_rate=metrics.get('LD'),
                total_separations_rate=metrics.get('TS'),
                latest_date=last_updated
            ))

    return JTSizeClassAnalysisResponse(
        industry_code=industry_code,
        industry_name=industry.industry_text if industry else None,
        size_classes=result,
        last_updated=last_updated
    )


@router.get("/sizeclasses/timeline", response_model=JTSizeClassTimelineResponse)
async def get_sizeclass_timeline(
    dataelement_code: str = Query("JO", description="Data element"),
    ratelevel_code: str = Query("R", description="Rate or Level"),
    months: int = Query(60, ge=12, le=300),
    sizeclass_codes: Optional[str] = Query(None, description="Comma-separated size class codes"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get timeline data for size class comparison"""

    element = db.query(JTDataElement).filter(JTDataElement.dataelement_code == dataelement_code).first()

    if sizeclass_codes:
        codes = [c.strip() for c in sizeclass_codes.split(',')]
    else:
        codes = ['00', '01', '02', '03', '04', '05', '06']

    series_map: Dict[str, str] = {}
    sizeclass_names: Dict[str, str] = {}

    for code in codes:
        series = db.query(JTSeries, JTSizeClass.sizeclass_text).outerjoin(
            JTSizeClass, JTSeries.sizeclass_code == JTSizeClass.sizeclass_code
        ).filter(
            JTSeries.industry_code == '000000',
            JTSeries.state_code == '00',
            JTSeries.sizeclass_code == code,
            JTSeries.dataelement_code == dataelement_code,
            JTSeries.ratelevel_code == ratelevel_code,
            JTSeries.seasonal == 'S',
            JTSeries.area_code == '00000'
        ).first()

        if series:
            series_map[code] = series.JTSeries.series_id
            sizeclass_names[code] = series.sizeclass_text or code

    all_data: Dict[str, Dict[str, float]] = {}

    for code, series_id in series_map.items():
        data = db.query(JTData).filter(
            JTData.series_id == series_id,
            JTData.period.like('M%'),
            JTData.period != 'M13'
        ).order_by(desc(JTData.year), desc(JTData.period)).limit(months).all()

        for d in data:
            period_key = f"{d.year}-{d.period}"
            if period_key not in all_data:
                all_data[period_key] = {'year': d.year, 'period': d.period}
            if d.value is not None:
                all_data[period_key][code] = float(d.value)

    timeline = []
    for period_key in sorted(all_data.keys()):
        d = all_data[period_key]
        size_dict = {code: d.get(code) for code in codes}
        timeline.append(JTSizeClassTimelinePoint(
            year=d['year'],
            period=d['period'],
            period_name=_get_period_name(d['year'], d['period'], db),
            size_classes=size_dict
        ))

    return JTSizeClassTimelineResponse(
        dataelement_code=dataelement_code,
        dataelement_name=element.dataelement_text if element else dataelement_code,
        ratelevel_code=ratelevel_code,
        timeline=timeline,
        sizeclass_names=sizeclass_names
    )


# =============================================================================
# TOP MOVERS ENDPOINT
# =============================================================================

@router.get("/top-movers", response_model=JTTopMoversResponse)
async def get_top_movers(
    dataelement_code: str = Query("JO", description="Data element"),
    period: str = Query("yoy", description="Period: 'mom' or 'yoy'"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get industries with largest JOLTS changes"""

    element = db.query(JTDataElement).filter(JTDataElement.dataelement_code == dataelement_code).first()
    industries = db.query(JTIndustry).filter(JTIndustry.selectable == 'T').all()

    movers = []

    for ind in industries:
        metric = _calculate_jolts_metric(db, ind.industry_code, '00', dataelement_code, 'R')

        if metric:
            change = metric.month_over_month if period == 'mom' else metric.year_over_year
            change_pct = metric.month_over_month_pct if period == 'mom' else metric.year_over_year_pct

            if change_pct is not None:
                movers.append(JTTopMover(
                    series_id=metric.series_id,
                    industry_code=ind.industry_code,
                    industry_name=ind.industry_text,
                    dataelement_code=dataelement_code,
                    dataelement_name=element.dataelement_text if element else dataelement_code,
                    value=metric.value,
                    latest_date=metric.latest_date,
                    change=change,
                    change_pct=change_pct
                ))

    # Sort by change percentage
    gainers = sorted([m for m in movers if m.change_pct and m.change_pct > 0],
                    key=lambda x: x.change_pct or 0, reverse=True)[:limit]
    losers = sorted([m for m in movers if m.change_pct and m.change_pct < 0],
                   key=lambda x: x.change_pct or 0)[:limit]

    last_updated = gainers[0].latest_date if gainers else (losers[0].latest_date if losers else None)

    return JTTopMoversResponse(
        dataelement_code=dataelement_code,
        dataelement_name=element.dataelement_text if element else dataelement_code,
        period=period,
        gainers=gainers,
        losers=losers,
        last_updated=last_updated
    )
