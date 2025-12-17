"""
BD (Business Employment Dynamics) Explorer API

Provides endpoints for exploring BED data including:
- Job flows: Gross gains, gross losses, expansions, contractions, openings, closings
- Establishment births and deaths
- State and industry comparisons
- Size class analysis (firm size, employment change)
- Historical trends

Data is quarterly, updated ~6 months after quarter end.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, or_, desc, asc, case
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import (
    BDState, BDIndustry, BDDataClass, BDDataElement, BDSizeClass,
    BDRateLevel, BDUnitAnalysis, BDOwnership, BDSeries, BDData
)
from .bd_schemas import (
    BDDimensions, BDStateItem, BDIndustryItem, BDDataClassItem,
    BDDataElementItem, BDSizeClassItem, BDRateLevelItem, BDOwnershipItem,
    BDSeriesInfo, BDSeriesListResponse,
    BDDataPoint, BDSeriesData, BDDataResponse,
    BDOverviewMetric, BDOverviewResponse, BDOverviewTimelinePoint, BDOverviewTimelineResponse,
    BDStateComparisonItem, BDStateComparisonResponse, BDStateTimelinePoint, BDStateTimelineResponse,
    BDIndustryComparisonItem, BDIndustryComparisonResponse, BDIndustryTimelinePoint, BDIndustryTimelineResponse,
    BDJobFlowComponents, BDJobFlowResponse, BDJobFlowTimelinePoint, BDJobFlowTimelineResponse,
    BDSizeClassDataItem, BDSizeClassResponse, BDSizeClassTimelinePoint, BDSizeClassTimelineResponse,
    BDBirthsDeathsData, BDBirthsDeathsResponse, BDBirthsDeathsTimelinePoint, BDBirthsDeathsTimelineResponse,
    BDTopMoverItem, BDTopMoversResponse,
    BDTrendPoint, BDTrendResponse
)

router = APIRouter(prefix="/api/research/bls/bd", tags=["BLS BD Research"])


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


def get_period_name(period: str, year: int = None) -> str:
    """Convert period code to display name"""
    period_map = {
        'Q01': 'Q1', 'Q02': 'Q2', 'Q03': 'Q3', 'Q04': 'Q4',
        'A01': 'Annual'
    }
    name = period_map.get(period, period)
    if year:
        return f"{year} {name}"
    return name


# Data class codes for quick reference
DATACLASS_GROSS_GAINS = '01'
DATACLASS_EXPANSIONS = '02'
DATACLASS_OPENINGS = '03'
DATACLASS_GROSS_LOSSES = '04'
DATACLASS_CONTRACTIONS = '05'
DATACLASS_CLOSINGS = '06'
DATACLASS_BIRTHS = '07'
DATACLASS_DEATHS = '08'

# All job flow data classes
JOB_FLOW_DATACLASSES = ['01', '02', '03', '04', '05', '06']
ALL_DATACLASSES = ['01', '02', '03', '04', '05', '06', '07', '08']


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=BDDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering BD data"""
    # States
    states = db.execute(
        select(BDState).order_by(
            case((BDState.state_code == '00', 0), else_=1),
            BDState.state_name
        )
    ).scalars().all()

    # Industries
    industries = db.execute(
        select(BDIndustry).order_by(BDIndustry.sort_sequence)
    ).scalars().all()

    # Data classes
    dataclasses = db.execute(
        select(BDDataClass).order_by(BDDataClass.sort_sequence)
    ).scalars().all()

    # Data elements
    dataelements = db.execute(
        select(BDDataElement).order_by(BDDataElement.dataelement_code)
    ).scalars().all()

    # Size classes
    sizeclasses = db.execute(
        select(BDSizeClass).order_by(BDSizeClass.sizeclass_code)
    ).scalars().all()

    # Rate levels
    ratelevels = db.execute(
        select(BDRateLevel).order_by(BDRateLevel.ratelevel_code)
    ).scalars().all()

    # Separate firm vs employment change size classes
    firm_sizeclasses = [s for s in sizeclasses if s.sizeclass_code in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']]
    empchange_sizeclasses = [s for s in sizeclasses if s.sizeclass_code not in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']]

    return BDDimensions(
        states=[BDStateItem(state_code=s.state_code, state_name=s.state_name) for s in states],
        industries=[BDIndustryItem(
            industry_code=i.industry_code,
            industry_name=i.industry_name,
            display_level=i.display_level,
            selectable=i.selectable,
            sort_sequence=i.sort_sequence
        ) for i in industries],
        dataclasses=[BDDataClassItem(
            dataclass_code=d.dataclass_code,
            dataclass_name=d.dataclass_name,
            display_level=d.display_level,
            selectable=d.selectable,
            sort_sequence=d.sort_sequence
        ) for d in dataclasses],
        dataelements=[BDDataElementItem(
            dataelement_code=e.dataelement_code,
            dataelement_name=e.dataelement_name
        ) for e in dataelements],
        sizeclasses=[BDSizeClassItem(
            sizeclass_code=s.sizeclass_code,
            sizeclass_name=s.sizeclass_name
        ) for s in sizeclasses],
        ratelevels=[BDRateLevelItem(
            ratelevel_code=r.ratelevel_code,
            ratelevel_name=r.ratelevel_name
        ) for r in ratelevels],
        firm_sizeclasses=[BDSizeClassItem(
            sizeclass_code=s.sizeclass_code,
            sizeclass_name=s.sizeclass_name
        ) for s in firm_sizeclasses],
        empchange_sizeclasses=[BDSizeClassItem(
            sizeclass_code=s.sizeclass_code,
            sizeclass_name=s.sizeclass_name
        ) for s in empchange_sizeclasses]
    )


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================

@router.get("/series", response_model=BDSeriesListResponse)
async def get_series(
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    industry_code: Optional[str] = Query(None, description="Filter by industry code"),
    dataclass_code: Optional[str] = Query(None, description="Filter by data class"),
    dataelement_code: Optional[str] = Query(None, description="Filter by data element (1=Employment, 2=Establishments)"),
    sizeclass_code: Optional[str] = Query(None, description="Filter by size class"),
    ratelevel_code: Optional[str] = Query(None, description="Filter by rate/level (L or R)"),
    seasonal_code: Optional[str] = Query(None, description="Filter by seasonal adjustment (S or U)"),
    periodicity_code: Optional[str] = Query(None, description="Filter by periodicity (Q or A)"),
    search: Optional[str] = Query(None, description="Search in series title"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Get list of BD series with optional filters"""
    # Base query with joins
    query = select(
        BDSeries,
        BDState.state_name,
        BDIndustry.industry_name,
        BDDataClass.dataclass_name,
        BDDataElement.dataelement_name,
        BDSizeClass.sizeclass_name,
        BDRateLevel.ratelevel_name
    ).outerjoin(
        BDState, BDSeries.state_code == BDState.state_code
    ).outerjoin(
        BDIndustry, BDSeries.industry_code == BDIndustry.industry_code
    ).outerjoin(
        BDDataClass, BDSeries.dataclass_code == BDDataClass.dataclass_code
    ).outerjoin(
        BDDataElement, BDSeries.dataelement_code == BDDataElement.dataelement_code
    ).outerjoin(
        BDSizeClass, BDSeries.sizeclass_code == BDSizeClass.sizeclass_code
    ).outerjoin(
        BDRateLevel, BDSeries.ratelevel_code == BDRateLevel.ratelevel_code
    )

    # Apply filters
    filters = []
    if state_code:
        filters.append(BDSeries.state_code == state_code)
    if industry_code:
        filters.append(BDSeries.industry_code == industry_code)
    if dataclass_code:
        filters.append(BDSeries.dataclass_code == dataclass_code)
    if dataelement_code:
        filters.append(BDSeries.dataelement_code == dataelement_code)
    if sizeclass_code:
        filters.append(BDSeries.sizeclass_code == sizeclass_code)
    if ratelevel_code:
        filters.append(BDSeries.ratelevel_code == ratelevel_code)
    if seasonal_code:
        filters.append(BDSeries.seasonal_code == seasonal_code)
    if periodicity_code:
        filters.append(BDSeries.periodicity_code == periodicity_code)
    if search:
        filters.append(BDSeries.series_title.ilike(f'%{search}%'))

    if filters:
        query = query.where(and_(*filters))

    # Count total
    count_query = select(func.count()).select_from(BDSeries)
    if filters:
        count_query = count_query.where(and_(*filters))
    total = db.execute(count_query).scalar()

    # Execute with pagination
    query = query.order_by(BDSeries.series_id).limit(limit).offset(offset)
    results = db.execute(query).all()

    series_list = []
    for row in results:
        s = row[0]
        series_list.append(BDSeriesInfo(
            series_id=s.series_id,
            seasonal_code=s.seasonal_code,
            msa_code=s.msa_code,
            state_code=s.state_code,
            state_name=row[1],
            county_code=s.county_code,
            industry_code=s.industry_code,
            industry_name=row[2],
            unitanalysis_code=s.unitanalysis_code,
            dataelement_code=s.dataelement_code,
            dataelement_name=row[4],
            sizeclass_code=s.sizeclass_code,
            sizeclass_name=row[5],
            dataclass_code=s.dataclass_code,
            dataclass_name=row[3],
            ratelevel_code=s.ratelevel_code,
            ratelevel_name=row[6],
            periodicity_code=s.periodicity_code,
            ownership_code=s.ownership_code,
            series_title=s.series_title,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active if s.is_active is not None else True
        ))

    return BDSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_list
    )


@router.get("/series/{series_id}", response_model=BDSeriesInfo)
async def get_series_detail(
    series_id: str,
    db: Session = Depends(get_data_db)
):
    """Get detailed information for a specific series"""
    result = db.execute(
        select(
            BDSeries,
            BDState.state_name,
            BDIndustry.industry_name,
            BDDataClass.dataclass_name,
            BDDataElement.dataelement_name,
            BDSizeClass.sizeclass_name,
            BDRateLevel.ratelevel_name
        ).outerjoin(
            BDState, BDSeries.state_code == BDState.state_code
        ).outerjoin(
            BDIndustry, BDSeries.industry_code == BDIndustry.industry_code
        ).outerjoin(
            BDDataClass, BDSeries.dataclass_code == BDDataClass.dataclass_code
        ).outerjoin(
            BDDataElement, BDSeries.dataelement_code == BDDataElement.dataelement_code
        ).outerjoin(
            BDSizeClass, BDSeries.sizeclass_code == BDSizeClass.sizeclass_code
        ).outerjoin(
            BDRateLevel, BDSeries.ratelevel_code == BDRateLevel.ratelevel_code
        ).where(BDSeries.series_id == series_id)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Series not found")

    s = result[0]
    return BDSeriesInfo(
        series_id=s.series_id,
        seasonal_code=s.seasonal_code,
        msa_code=s.msa_code,
        state_code=s.state_code,
        state_name=result[1],
        county_code=s.county_code,
        industry_code=s.industry_code,
        industry_name=result[2],
        unitanalysis_code=s.unitanalysis_code,
        dataelement_code=s.dataelement_code,
        dataelement_name=result[4],
        sizeclass_code=s.sizeclass_code,
        sizeclass_name=result[5],
        dataclass_code=s.dataclass_code,
        dataclass_name=result[3],
        ratelevel_code=s.ratelevel_code,
        ratelevel_name=result[6],
        periodicity_code=s.periodicity_code,
        ownership_code=s.ownership_code,
        series_title=s.series_title,
        begin_year=s.begin_year,
        begin_period=s.begin_period,
        end_year=s.end_year,
        end_period=s.end_period,
        is_active=s.is_active if s.is_active is not None else True
    )


@router.get("/data", response_model=BDDataResponse)
async def get_data(
    series_ids: str = Query(..., description="Comma-separated series IDs"),
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get time series data for one or more series"""
    ids = [s.strip() for s in series_ids.split(',') if s.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="No series IDs provided")
    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 series at a time")

    # Batch fetch series info
    series_results = db.execute(
        select(
            BDSeries,
            BDState.state_name,
            BDIndustry.industry_name,
            BDDataClass.dataclass_name,
            BDDataElement.dataelement_name,
            BDSizeClass.sizeclass_name,
            BDRateLevel.ratelevel_name
        ).outerjoin(
            BDState, BDSeries.state_code == BDState.state_code
        ).outerjoin(
            BDIndustry, BDSeries.industry_code == BDIndustry.industry_code
        ).outerjoin(
            BDDataClass, BDSeries.dataclass_code == BDDataClass.dataclass_code
        ).outerjoin(
            BDDataElement, BDSeries.dataelement_code == BDDataElement.dataelement_code
        ).outerjoin(
            BDSizeClass, BDSeries.sizeclass_code == BDSizeClass.sizeclass_code
        ).outerjoin(
            BDRateLevel, BDSeries.ratelevel_code == BDRateLevel.ratelevel_code
        ).where(BDSeries.series_id.in_(ids))
    ).all()

    series_info_map = {}
    for row in series_results:
        s = row[0]
        series_info_map[s.series_id] = BDSeriesInfo(
            series_id=s.series_id,
            seasonal_code=s.seasonal_code,
            state_code=s.state_code,
            state_name=row[1],
            industry_code=s.industry_code,
            industry_name=row[2],
            dataelement_code=s.dataelement_code,
            dataelement_name=row[4],
            sizeclass_code=s.sizeclass_code,
            sizeclass_name=row[5],
            dataclass_code=s.dataclass_code,
            dataclass_name=row[3],
            ratelevel_code=s.ratelevel_code,
            ratelevel_name=row[6],
            periodicity_code=s.periodicity_code,
            series_title=s.series_title,
            begin_year=s.begin_year,
            end_year=s.end_year
        )

    # Batch fetch data
    data_query = select(BDData).where(BDData.series_id.in_(ids))
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    if end_year:
        data_query = data_query.where(BDData.year <= end_year)
    data_query = data_query.order_by(BDData.series_id, BDData.year, BDData.period)

    data_results = db.execute(data_query).scalars().all()

    # Group by series
    data_by_series: Dict[str, List[BDDataPoint]] = {sid: [] for sid in ids}
    for d in data_results:
        if d.series_id in data_by_series:
            data_by_series[d.series_id].append(BDDataPoint(
                year=d.year,
                period=d.period,
                period_name=get_period_name(d.period, d.year),
                value=decimal_to_float(d.value),
                footnote_codes=d.footnote_codes
            ))

    # Build response
    series_data = []
    total_obs = 0
    for sid in ids:
        if sid in series_info_map:
            points = data_by_series.get(sid, [])
            total_obs += len(points)
            series_data.append(BDSeriesData(
                series_id=sid,
                series_info=series_info_map[sid],
                data_points=points
            ))

    return BDDataResponse(
        series_count=len(series_data),
        total_observations=total_obs,
        series=series_data
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=BDOverviewResponse)
async def get_overview(
    state_code: str = Query('00', description="State code (00 for US)"),
    industry_code: str = Query('000000', description="Industry code"),
    seasonal_code: str = Query('S', description="S=Seasonally adjusted, U=Unadjusted"),
    year: Optional[int] = Query(None, description="Year (defaults to latest)"),
    period: Optional[str] = Query(None, description="Period Q01-Q04 (defaults to latest)"),
    db: Session = Depends(get_data_db)
):
    """Get overview of BD metrics for a specific state/industry/period"""
    # Get state and industry names
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()

    state_name = state.state_name if state else 'Unknown'
    industry_name = industry.industry_name if industry else 'Unknown'

    # Find latest available period if not specified
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.state_code == state_code,
                    BDSeries.industry_code == industry_code,
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code == '00',
                    BDSeries.dataelement_code == '1'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year = latest[0]
            period = latest[1]
        else:
            raise HTTPException(status_code=404, detail="No data available for this selection")

    # Get available years/periods
    available = db.execute(
        select(BDData.year, BDData.period)
        .join(BDSeries, BDData.series_id == BDSeries.series_id)
        .where(
            and_(
                BDSeries.state_code == state_code,
                BDSeries.industry_code == industry_code,
                BDSeries.seasonal_code == seasonal_code,
                BDSeries.periodicity_code == 'Q',
                BDSeries.sizeclass_code == '00',
                BDSeries.dataelement_code == '1',
                BDSeries.dataclass_code == '01'
            )
        )
        .distinct()
        .order_by(desc(BDData.year), desc(BDData.period))
    ).all()

    available_years = sorted(set(a[0] for a in available), reverse=True)
    available_periods = sorted(set(a[1] for a in available))

    # Batch query for all data classes (both Level and Rate)
    # Employment (dataelement_code = '1'), sizeclass = '00'
    series_query = select(BDSeries.series_id, BDSeries.dataclass_code, BDSeries.ratelevel_code).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == '1',
            BDSeries.dataclass_code.in_(ALL_DATACLASSES)
        )
    )
    series_results = db.execute(series_query).all()

    series_ids = [r[0] for r in series_results]
    series_map = {r[0]: (r[1], r[2]) for r in series_results}  # series_id -> (dataclass, ratelevel)

    # Get current period data
    current_data = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    # Get previous quarter data
    prev_year, prev_period = year, period
    if period == 'Q01':
        prev_year, prev_period = year - 1, 'Q04'
    elif period == 'Q02':
        prev_period = 'Q01'
    elif period == 'Q03':
        prev_period = 'Q02'
    elif period == 'Q04':
        prev_period = 'Q03'

    prev_data = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == prev_year,
                BDData.period == prev_period
            )
        )
    ).all()

    # Get same quarter last year
    yoy_data = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year - 1,
                BDData.period == period
            )
        )
    ).all()

    # Organize data by dataclass and ratelevel
    current_map = {d[0]: decimal_to_float(d[1]) for d in current_data}
    prev_map = {d[0]: decimal_to_float(d[1]) for d in prev_data}
    yoy_map = {d[0]: decimal_to_float(d[1]) for d in yoy_data}

    # Build metrics
    dataclass_names = {d.dataclass_code: d.dataclass_name for d in db.execute(select(BDDataClass)).scalars().all()}

    metrics_data = {}  # dataclass_code -> {level, rate, level_prev, rate_prev, ...}
    for sid, (dc, rl) in series_map.items():
        if dc not in metrics_data:
            metrics_data[dc] = {}
        if rl == 'L':
            metrics_data[dc]['level'] = current_map.get(sid)
            metrics_data[dc]['level_prev'] = prev_map.get(sid)
            metrics_data[dc]['level_yoy'] = yoy_map.get(sid)
        else:
            metrics_data[dc]['rate'] = current_map.get(sid)
            metrics_data[dc]['rate_prev'] = prev_map.get(sid)
            metrics_data[dc]['rate_yoy'] = yoy_map.get(sid)

    metrics = []
    for dc in ALL_DATACLASSES:
        if dc in metrics_data:
            m = metrics_data[dc]
            level_val = m.get('level')
            rate_val = m.get('rate')
            level_prev = m.get('level_prev')
            rate_prev = m.get('rate_prev')
            level_yoy = m.get('level_yoy')
            rate_yoy = m.get('rate_yoy')

            metrics.append(BDOverviewMetric(
                dataclass_code=dc,
                dataclass_name=dataclass_names.get(dc, dc),
                level_value=level_val,
                rate_value=rate_val,
                level_change=level_val - level_prev if level_val and level_prev else None,
                rate_change=rate_val - rate_prev if rate_val and rate_prev else None,
                level_yoy_change=level_val - level_yoy if level_val and level_yoy else None,
                rate_yoy_change=rate_val - rate_yoy if rate_val and rate_yoy else None
            ))

    return BDOverviewResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        state_code=state_code,
        state_name=state_name,
        industry_code=industry_code,
        industry_name=industry_name,
        seasonal_code=seasonal_code,
        metrics=metrics,
        available_years=available_years,
        available_periods=available_periods
    )


@router.get("/overview/timeline", response_model=BDOverviewTimelineResponse)
async def get_overview_timeline(
    state_code: str = Query('00', description="State code"),
    industry_code: str = Query('000000', description="Industry code"),
    seasonal_code: str = Query('S'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for overview charts (Gross Gains vs Losses)"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()

    # Get series for gross gains (01) and gross losses (04) - both Level
    series_query = select(BDSeries.series_id, BDSeries.dataclass_code).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == '1',
            BDSeries.ratelevel_code == 'L',
            BDSeries.dataclass_code.in_(['01', '04'])
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: r[1] for r in series_results}
    series_ids = list(series_map.keys())

    # Also get rates
    rate_series_query = select(BDSeries.series_id, BDSeries.dataclass_code).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == '1',
            BDSeries.ratelevel_code == 'R',
            BDSeries.dataclass_code.in_(['01', '04'])
        )
    )
    rate_results = db.execute(rate_series_query).all()
    rate_map = {r[0]: r[1] for r in rate_results}
    rate_ids = list(rate_map.keys())

    # Query data
    data_query = select(BDData.series_id, BDData.year, BDData.period, BDData.value).where(
        BDData.series_id.in_(series_ids + rate_ids)
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Organize by period
    timeline_data = {}
    for sid, yr, per, val in data_results:
        key = (yr, per)
        if key not in timeline_data:
            timeline_data[key] = {}
        dc = series_map.get(sid) or rate_map.get(sid)
        is_rate = sid in rate_map
        if dc == '01':
            if is_rate:
                timeline_data[key]['gains_rate'] = decimal_to_float(val)
            else:
                timeline_data[key]['gains_level'] = decimal_to_float(val)
        elif dc == '04':
            if is_rate:
                timeline_data[key]['losses_rate'] = decimal_to_float(val)
            else:
                timeline_data[key]['losses_level'] = decimal_to_float(val)

    # Build timeline
    timeline = []
    for (yr, per) in sorted(timeline_data.keys()):
        d = timeline_data[(yr, per)]
        gains = d.get('gains_level')
        losses = d.get('losses_level')
        timeline.append(BDOverviewTimelinePoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            gross_gains_level=gains,
            gross_losses_level=losses,
            net_change=gains - losses if gains and losses else None,
            gross_gains_rate=d.get('gains_rate'),
            gross_losses_rate=d.get('losses_rate')
        ))

    return BDOverviewTimelineResponse(
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        data=timeline
    )


# ============================================================================
# STATE COMPARISON ENDPOINT
# ============================================================================

@router.get("/states/comparison", response_model=BDStateComparisonResponse)
async def get_state_comparison(
    industry_code: str = Query('000000'),
    seasonal_code: str = Query('S'),
    dataelement_code: str = Query('1', description="1=Employment, 2=Establishments"),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Compare job dynamics across all states"""
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()
    dataelement = db.execute(select(BDDataElement).where(BDDataElement.dataelement_code == dataelement_code)).scalar()

    # Find latest period if not specified
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.industry_code == industry_code,
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code == '00',
                    BDSeries.dataelement_code == dataelement_code,
                    BDSeries.dataclass_code == '01'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year, period = latest[0], latest[1]
        else:
            raise HTTPException(status_code=404, detail="No data available")

    # Get all states
    states = db.execute(select(BDState).order_by(BDState.state_name)).scalars().all()
    state_map = {s.state_code: s.state_name for s in states}

    # Get series for all states, all data classes, Level only
    series_query = select(
        BDSeries.series_id, BDSeries.state_code, BDSeries.dataclass_code
    ).where(
        and_(
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == dataelement_code,
            BDSeries.ratelevel_code == 'L',
            BDSeries.dataclass_code.in_(ALL_DATACLASSES)
        )
    )
    series_results = db.execute(series_query).all()

    series_ids = [r[0] for r in series_results]
    series_map = {r[0]: (r[1], r[2]) for r in series_results}  # series_id -> (state, dataclass)

    # Get data
    data_results = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    # Organize by state
    state_data = {}
    for sid, val in data_results:
        state_code, dc = series_map.get(sid, (None, None))
        if not state_code:
            continue
        if state_code not in state_data:
            state_data[state_code] = {}
        state_data[state_code][dc] = decimal_to_float(val)

    # Build response
    state_items = []
    for sc, sn in state_map.items():
        if sc in state_data:
            d = state_data[sc]
            gains = d.get('01')
            losses = d.get('04')
            state_items.append(BDStateComparisonItem(
                state_code=sc,
                state_name=sn,
                gross_gains_level=gains,
                gross_losses_level=losses,
                net_change=gains - losses if gains and losses else None,
                expansions_level=d.get('02'),
                contractions_level=d.get('05'),
                openings_level=d.get('03'),
                closings_level=d.get('06'),
                births_level=d.get('07'),
                deaths_level=d.get('08')
            ))

    # Sort by gross gains descending
    state_items.sort(key=lambda x: x.gross_gains_level or 0, reverse=True)

    return BDStateComparisonResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        dataelement_code=dataelement_code,
        dataelement_name=dataelement.dataelement_name if dataelement else 'Employment',
        states=state_items
    )


@router.get("/states/timeline", response_model=BDStateTimelineResponse)
async def get_state_timeline(
    state_codes: str = Query(..., description="Comma-separated state codes"),
    industry_code: str = Query('000000'),
    dataclass_code: str = Query('01', description="Data class (01=Gross Gains, 04=Gross Losses, etc.)"),
    ratelevel_code: str = Query('L'),
    seasonal_code: str = Query('S'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for comparing multiple states"""
    codes = [c.strip() for c in state_codes.split(',') if c.strip()]
    if not codes or len(codes) > 10:
        raise HTTPException(status_code=400, detail="Provide 1-10 state codes")

    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()
    dataclass = db.execute(select(BDDataClass).where(BDDataClass.dataclass_code == dataclass_code)).scalar()
    states = db.execute(select(BDState).where(BDState.state_code.in_(codes))).scalars().all()
    state_map = {s.state_code: s.state_name for s in states}

    # Get series
    series_query = select(BDSeries.series_id, BDSeries.state_code).where(
        and_(
            BDSeries.state_code.in_(codes),
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == '1',
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code == dataclass_code
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: r[1] for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_query = select(BDData.series_id, BDData.year, BDData.period, BDData.value).where(
        BDData.series_id.in_(series_ids)
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Organize by period
    timeline_data = {}
    for sid, yr, per, val in data_results:
        key = (yr, per)
        if key not in timeline_data:
            timeline_data[key] = {}
        state_code = series_map.get(sid)
        if state_code:
            timeline_data[key][state_code] = decimal_to_float(val)

    timeline = []
    for (yr, per) in sorted(timeline_data.keys()):
        timeline.append(BDStateTimelinePoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            values=timeline_data[(yr, per)]
        ))

    return BDStateTimelineResponse(
        dataclass_code=dataclass_code,
        dataclass_name=dataclass.dataclass_name if dataclass else dataclass_code,
        ratelevel_code=ratelevel_code,
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        states=[BDStateItem(state_code=sc, state_name=state_map.get(sc, sc)) for sc in codes if sc in state_map],
        data=timeline
    )


# ============================================================================
# INDUSTRY COMPARISON ENDPOINT
# ============================================================================

@router.get("/industries/comparison", response_model=BDIndustryComparisonResponse)
async def get_industry_comparison(
    state_code: str = Query('00'),
    seasonal_code: str = Query('S'),
    dataelement_code: str = Query('1'),
    display_level: Optional[int] = Query(None, description="Filter by industry display level"),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Compare job dynamics across industries"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    dataelement = db.execute(select(BDDataElement).where(BDDataElement.dataelement_code == dataelement_code)).scalar()

    # Get industries
    ind_query = select(BDIndustry).order_by(BDIndustry.sort_sequence)
    if display_level is not None:
        ind_query = ind_query.where(BDIndustry.display_level == display_level)
    industries = db.execute(ind_query).scalars().all()
    industry_map = {i.industry_code: (i.industry_name, i.display_level) for i in industries}

    # Find latest period
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.state_code == state_code,
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code == '00',
                    BDSeries.dataelement_code == dataelement_code,
                    BDSeries.dataclass_code == '01'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year, period = latest[0], latest[1]
        else:
            raise HTTPException(status_code=404, detail="No data available")

    # Get series for all industries
    series_query = select(
        BDSeries.series_id, BDSeries.industry_code, BDSeries.dataclass_code
    ).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == dataelement_code,
            BDSeries.ratelevel_code == 'L',
            BDSeries.dataclass_code.in_(['01', '04'])
        )
    )
    if display_level is not None:
        series_query = series_query.where(BDSeries.industry_code.in_(list(industry_map.keys())))

    series_results = db.execute(series_query).all()
    series_ids = [r[0] for r in series_results]
    series_map = {r[0]: (r[1], r[2]) for r in series_results}

    # Get data
    data_results = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    # Organize by industry
    industry_data = {}
    for sid, val in data_results:
        ind_code, dc = series_map.get(sid, (None, None))
        if not ind_code:
            continue
        if ind_code not in industry_data:
            industry_data[ind_code] = {}
        industry_data[ind_code][dc] = decimal_to_float(val)

    # Build response
    items = []
    for ic, (iname, dlevel) in industry_map.items():
        if ic in industry_data:
            d = industry_data[ic]
            gains = d.get('01')
            losses = d.get('04')
            items.append(BDIndustryComparisonItem(
                industry_code=ic,
                industry_name=iname,
                display_level=dlevel,
                gross_gains_level=gains,
                gross_losses_level=losses,
                net_change=gains - losses if gains and losses else None
            ))

    items.sort(key=lambda x: x.gross_gains_level or 0, reverse=True)

    return BDIndustryComparisonResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        seasonal_code=seasonal_code,
        dataelement_code=dataelement_code,
        dataelement_name=dataelement.dataelement_name if dataelement else 'Employment',
        industries=items
    )


@router.get("/industries/timeline", response_model=BDIndustryTimelineResponse)
async def get_industry_timeline(
    industry_codes: str = Query(..., description="Comma-separated industry codes"),
    state_code: str = Query('00'),
    dataclass_code: str = Query('01'),
    ratelevel_code: str = Query('L'),
    seasonal_code: str = Query('S'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for comparing multiple industries"""
    codes = [c.strip() for c in industry_codes.split(',') if c.strip()]
    if not codes or len(codes) > 10:
        raise HTTPException(status_code=400, detail="Provide 1-10 industry codes")

    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    dataclass = db.execute(select(BDDataClass).where(BDDataClass.dataclass_code == dataclass_code)).scalar()
    industries = db.execute(select(BDIndustry).where(BDIndustry.industry_code.in_(codes))).scalars().all()
    industry_map = {i.industry_code: i.industry_name for i in industries}

    # Get series
    series_query = select(BDSeries.series_id, BDSeries.industry_code).where(
        and_(
            BDSeries.industry_code.in_(codes),
            BDSeries.state_code == state_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == '1',
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code == dataclass_code
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: r[1] for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_query = select(BDData.series_id, BDData.year, BDData.period, BDData.value).where(
        BDData.series_id.in_(series_ids)
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Organize by period
    timeline_data = {}
    for sid, yr, per, val in data_results:
        key = (yr, per)
        if key not in timeline_data:
            timeline_data[key] = {}
        ind_code = series_map.get(sid)
        if ind_code:
            timeline_data[key][ind_code] = decimal_to_float(val)

    timeline = []
    for (yr, per) in sorted(timeline_data.keys()):
        timeline.append(BDIndustryTimelinePoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            values=timeline_data[(yr, per)]
        ))

    return BDIndustryTimelineResponse(
        dataclass_code=dataclass_code,
        dataclass_name=dataclass.dataclass_name if dataclass else dataclass_code,
        ratelevel_code=ratelevel_code,
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        seasonal_code=seasonal_code,
        industries=[BDIndustryItem(
            industry_code=ic,
            industry_name=industry_map.get(ic, ic)
        ) for ic in codes if ic in industry_map],
        data=timeline
    )


# ============================================================================
# JOB FLOW COMPONENTS ENDPOINT
# ============================================================================

@router.get("/job-flow", response_model=BDJobFlowResponse)
async def get_job_flow(
    state_code: str = Query('00'),
    industry_code: str = Query('000000'),
    seasonal_code: str = Query('S'),
    ratelevel_code: str = Query('L'),
    dataelement_code: str = Query('1'),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get job flow component breakdown for a specific period"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()
    ratelevel = db.execute(select(BDRateLevel).where(BDRateLevel.ratelevel_code == ratelevel_code)).scalar()
    dataelement = db.execute(select(BDDataElement).where(BDDataElement.dataelement_code == dataelement_code)).scalar()

    # Find latest period
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.state_code == state_code,
                    BDSeries.industry_code == industry_code,
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code == '00',
                    BDSeries.dataelement_code == dataelement_code,
                    BDSeries.ratelevel_code == ratelevel_code,
                    BDSeries.dataclass_code == '01'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year, period = latest[0], latest[1]
        else:
            raise HTTPException(status_code=404, detail="No data available")

    # Get all data class series
    series_query = select(BDSeries.series_id, BDSeries.dataclass_code).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == dataelement_code,
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code.in_(ALL_DATACLASSES)
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: r[1] for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_results = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    values = {}
    for sid, val in data_results:
        dc = series_map.get(sid)
        if dc:
            values[dc] = decimal_to_float(val)

    gains = values.get('01')
    losses = values.get('04')

    return BDJobFlowResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        ratelevel_code=ratelevel_code,
        ratelevel_name=ratelevel.ratelevel_name if ratelevel else ratelevel_code,
        dataelement_code=dataelement_code,
        dataelement_name=dataelement.dataelement_name if dataelement else 'Employment',
        components=BDJobFlowComponents(
            gross_gains=gains,
            expansions=values.get('02'),
            openings=values.get('03'),
            gross_losses=losses,
            contractions=values.get('05'),
            closings=values.get('06'),
            net_change=gains - losses if gains and losses else None,
            births=values.get('07'),
            deaths=values.get('08')
        )
    )


@router.get("/job-flow/timeline", response_model=BDJobFlowTimelineResponse)
async def get_job_flow_timeline(
    state_code: str = Query('00'),
    industry_code: str = Query('000000'),
    seasonal_code: str = Query('S'),
    ratelevel_code: str = Query('L'),
    dataelement_code: str = Query('1'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get job flow timeline with all components"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()

    # Get series for all job flow data classes
    series_query = select(BDSeries.series_id, BDSeries.dataclass_code).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataelement_code == dataelement_code,
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code.in_(JOB_FLOW_DATACLASSES)
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: r[1] for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_query = select(BDData.series_id, BDData.year, BDData.period, BDData.value).where(
        BDData.series_id.in_(series_ids)
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Organize by period
    timeline_data = {}
    for sid, yr, per, val in data_results:
        key = (yr, per)
        if key not in timeline_data:
            timeline_data[key] = {}
        dc = series_map.get(sid)
        if dc:
            timeline_data[key][dc] = decimal_to_float(val)

    timeline = []
    for (yr, per) in sorted(timeline_data.keys()):
        d = timeline_data[(yr, per)]
        gains = d.get('01')
        losses = d.get('04')
        timeline.append(BDJobFlowTimelinePoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            gross_gains=gains,
            expansions=d.get('02'),
            openings=d.get('03'),
            gross_losses=losses,
            contractions=d.get('05'),
            closings=d.get('06'),
            net_change=gains - losses if gains and losses else None
        ))

    return BDJobFlowTimelineResponse(
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        ratelevel_code=ratelevel_code,
        dataelement_code=dataelement_code,
        data=timeline
    )


# ============================================================================
# SIZE CLASS ANALYSIS ENDPOINT
# ============================================================================

@router.get("/size-class", response_model=BDSizeClassResponse)
async def get_size_class_analysis(
    sizeclass_type: str = Query('firm', description="'firm' (01-09) or 'empchange' (10+)"),
    seasonal_code: str = Query('S'),
    ratelevel_code: str = Query('L'),
    dataelement_code: str = Query('1'),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get job dynamics by size class (firm size or employment change size)"""
    ratelevel = db.execute(select(BDRateLevel).where(BDRateLevel.ratelevel_code == ratelevel_code)).scalar()
    dataelement = db.execute(select(BDDataElement).where(BDDataElement.dataelement_code == dataelement_code)).scalar()

    # Determine size class codes to use
    if sizeclass_type == 'firm':
        size_codes = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    else:
        # Employment change sizes
        size_codes = [f'{i:02d}' for i in range(10, 29)] + ['31', '32', '33']

    # Get size classes
    sizeclasses = db.execute(
        select(BDSizeClass).where(BDSizeClass.sizeclass_code.in_(size_codes))
    ).scalars().all()
    sizeclass_map = {s.sizeclass_code: s.sizeclass_name for s in sizeclasses}

    # Find latest period
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.state_code == '00',
                    BDSeries.industry_code == '000000',
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code.in_(size_codes),
                    BDSeries.dataelement_code == dataelement_code,
                    BDSeries.ratelevel_code == ratelevel_code,
                    BDSeries.dataclass_code == '01'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year, period = latest[0], latest[1]
        else:
            raise HTTPException(status_code=404, detail="No size class data available")

    # Get series
    series_query = select(BDSeries.series_id, BDSeries.sizeclass_code, BDSeries.dataclass_code).where(
        and_(
            BDSeries.state_code == '00',
            BDSeries.industry_code == '000000',
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code.in_(size_codes),
            BDSeries.dataelement_code == dataelement_code,
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code.in_(['01', '04'])
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: (r[1], r[2]) for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_results = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    # Organize by size class
    size_data = {}
    for sid, val in data_results:
        sc, dc = series_map.get(sid, (None, None))
        if not sc:
            continue
        if sc not in size_data:
            size_data[sc] = {}
        size_data[sc][dc] = decimal_to_float(val)

    # Build response
    items = []
    for sc in size_codes:
        if sc in size_data and sc in sizeclass_map:
            d = size_data[sc]
            gains = d.get('01')
            losses = d.get('04')
            items.append(BDSizeClassDataItem(
                sizeclass_code=sc,
                sizeclass_name=sizeclass_map[sc],
                gross_gains=gains,
                gross_losses=losses,
                net_change=gains - losses if gains and losses else None
            ))

    return BDSizeClassResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        seasonal_code=seasonal_code,
        ratelevel_code=ratelevel_code,
        ratelevel_name=ratelevel.ratelevel_name if ratelevel else ratelevel_code,
        dataelement_code=dataelement_code,
        dataelement_name=dataelement.dataelement_name if dataelement else 'Employment',
        sizeclass_type=sizeclass_type,
        data=items
    )


@router.get("/size-class/timeline", response_model=BDSizeClassTimelineResponse)
async def get_size_class_timeline(
    sizeclass_codes: str = Query(..., description="Comma-separated size class codes"),
    dataclass_code: str = Query('01'),
    ratelevel_code: str = Query('L'),
    seasonal_code: str = Query('S'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline for comparing size classes"""
    codes = [c.strip() for c in sizeclass_codes.split(',') if c.strip()]
    if not codes or len(codes) > 10:
        raise HTTPException(status_code=400, detail="Provide 1-10 size class codes")

    dataclass = db.execute(select(BDDataClass).where(BDDataClass.dataclass_code == dataclass_code)).scalar()
    sizeclasses = db.execute(select(BDSizeClass).where(BDSizeClass.sizeclass_code.in_(codes))).scalars().all()
    sizeclass_map = {s.sizeclass_code: s.sizeclass_name for s in sizeclasses}

    # Determine type
    sizeclass_type = 'firm' if all(c in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09'] for c in codes) else 'empchange'

    # Get series
    series_query = select(BDSeries.series_id, BDSeries.sizeclass_code).where(
        and_(
            BDSeries.state_code == '00',
            BDSeries.industry_code == '000000',
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code.in_(codes),
            BDSeries.dataelement_code == '1',
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code == dataclass_code
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: r[1] for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_query = select(BDData.series_id, BDData.year, BDData.period, BDData.value).where(
        BDData.series_id.in_(series_ids)
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Organize by period
    timeline_data = {}
    for sid, yr, per, val in data_results:
        key = (yr, per)
        if key not in timeline_data:
            timeline_data[key] = {}
        sc = series_map.get(sid)
        if sc:
            timeline_data[key][sc] = decimal_to_float(val)

    timeline = []
    for (yr, per) in sorted(timeline_data.keys()):
        timeline.append(BDSizeClassTimelinePoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            values=timeline_data[(yr, per)]
        ))

    return BDSizeClassTimelineResponse(
        dataclass_code=dataclass_code,
        dataclass_name=dataclass.dataclass_name if dataclass else dataclass_code,
        ratelevel_code=ratelevel_code,
        sizeclass_type=sizeclass_type,
        seasonal_code=seasonal_code,
        sizeclasses=[BDSizeClassItem(
            sizeclass_code=sc,
            sizeclass_name=sizeclass_map.get(sc, sc)
        ) for sc in codes if sc in sizeclass_map],
        data=timeline
    )


# ============================================================================
# BIRTHS/DEATHS ENDPOINT
# ============================================================================

@router.get("/births-deaths", response_model=BDBirthsDeathsResponse)
async def get_births_deaths(
    state_code: str = Query('00'),
    industry_code: str = Query('000000'),
    seasonal_code: str = Query('S'),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get establishment births and deaths data"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()

    # Find latest period
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.state_code == state_code,
                    BDSeries.industry_code == industry_code,
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code == '00',
                    BDSeries.dataclass_code == '07'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year, period = latest[0], latest[1]
        else:
            raise HTTPException(status_code=404, detail="No births/deaths data available")

    # Get series for births (07) and deaths (08) - both elements and both rate/level
    series_query = select(
        BDSeries.series_id, BDSeries.dataclass_code,
        BDSeries.dataelement_code, BDSeries.ratelevel_code
    ).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.dataclass_code.in_(['07', '08'])
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: (r[1], r[2], r[3]) for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_results = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    # Organize
    values = {}  # (dataclass, dataelement, ratelevel) -> value
    for sid, val in data_results:
        key = series_map.get(sid)
        if key:
            values[key] = decimal_to_float(val)

    # Employment data
    emp_births = values.get(('07', '1', 'L'))
    emp_deaths = values.get(('08', '1', 'L'))
    emp_birth_rate = values.get(('07', '1', 'R'))
    emp_death_rate = values.get(('08', '1', 'R'))

    # Establishment data
    est_births = values.get(('07', '2', 'L'))
    est_deaths = values.get(('08', '2', 'L'))
    est_birth_rate = values.get(('07', '2', 'R'))
    est_death_rate = values.get(('08', '2', 'R'))

    return BDBirthsDeathsResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        employment=BDBirthsDeathsData(
            births=emp_births,
            deaths=emp_deaths,
            net=emp_births - emp_deaths if emp_births and emp_deaths else None,
            birth_rate=emp_birth_rate,
            death_rate=emp_death_rate
        ),
        establishments=BDBirthsDeathsData(
            births=est_births,
            deaths=est_deaths,
            net=est_births - est_deaths if est_births and est_deaths else None,
            birth_rate=est_birth_rate,
            death_rate=est_death_rate
        )
    )


@router.get("/births-deaths/timeline", response_model=BDBirthsDeathsTimelineResponse)
async def get_births_deaths_timeline(
    state_code: str = Query('00'),
    industry_code: str = Query('000000'),
    seasonal_code: str = Query('S'),
    ratelevel_code: str = Query('L'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get births/deaths timeline"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()

    # Get series for births and deaths - both elements
    series_query = select(
        BDSeries.series_id, BDSeries.dataclass_code, BDSeries.dataelement_code
    ).where(
        and_(
            BDSeries.state_code == state_code,
            BDSeries.industry_code == industry_code,
            BDSeries.seasonal_code == seasonal_code,
            BDSeries.periodicity_code == 'Q',
            BDSeries.sizeclass_code == '00',
            BDSeries.ratelevel_code == ratelevel_code,
            BDSeries.dataclass_code.in_(['07', '08'])
        )
    )
    series_results = db.execute(series_query).all()
    series_map = {r[0]: (r[1], r[2]) for r in series_results}
    series_ids = list(series_map.keys())

    # Get data
    data_query = select(BDData.series_id, BDData.year, BDData.period, BDData.value).where(
        BDData.series_id.in_(series_ids)
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Organize by period
    timeline_data = {}
    for sid, yr, per, val in data_results:
        key = (yr, per)
        if key not in timeline_data:
            timeline_data[key] = {}
        dc, de = series_map.get(sid, (None, None))
        if dc == '07' and de == '1':
            timeline_data[key]['births_emp'] = decimal_to_float(val)
        elif dc == '08' and de == '1':
            timeline_data[key]['deaths_emp'] = decimal_to_float(val)
        elif dc == '07' and de == '2':
            timeline_data[key]['births_est'] = decimal_to_float(val)
        elif dc == '08' and de == '2':
            timeline_data[key]['deaths_est'] = decimal_to_float(val)

    timeline = []
    for (yr, per) in sorted(timeline_data.keys()):
        d = timeline_data[(yr, per)]
        births_emp = d.get('births_emp')
        deaths_emp = d.get('deaths_emp')
        births_est = d.get('births_est')
        deaths_est = d.get('deaths_est')
        timeline.append(BDBirthsDeathsTimelinePoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            births_emp=births_emp,
            deaths_emp=deaths_emp,
            births_est=births_est,
            deaths_est=deaths_est,
            net_emp=births_emp - deaths_emp if births_emp and deaths_emp else None,
            net_est=births_est - deaths_est if births_est and deaths_est else None
        ))

    return BDBirthsDeathsTimelineResponse(
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        seasonal_code=seasonal_code,
        ratelevel_code=ratelevel_code,
        data=timeline
    )


# ============================================================================
# TOP MOVERS ENDPOINT
# ============================================================================

@router.get("/top-movers", response_model=BDTopMoversResponse)
async def get_top_movers(
    comparison_type: str = Query('state', description="'state' or 'industry'"),
    metric: str = Query('net_change', description="'gross_gains', 'gross_losses', 'net_change'"),
    ratelevel_code: str = Query('L'),
    dataelement_code: str = Query('1'),
    seasonal_code: str = Query('S'),
    limit: int = Query(10, le=20),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get top gainers and losers by state or industry"""
    # Find latest period
    if not year or not period:
        latest = db.execute(
            select(BDData.year, BDData.period)
            .join(BDSeries, BDData.series_id == BDSeries.series_id)
            .where(
                and_(
                    BDSeries.seasonal_code == seasonal_code,
                    BDSeries.periodicity_code == 'Q',
                    BDSeries.sizeclass_code == '00',
                    BDSeries.dataelement_code == dataelement_code,
                    BDSeries.ratelevel_code == ratelevel_code,
                    BDSeries.dataclass_code == '01'
                )
            )
            .order_by(desc(BDData.year), desc(BDData.period))
            .limit(1)
        ).first()
        if latest:
            year, period = latest[0], latest[1]
        else:
            raise HTTPException(status_code=404, detail="No data available")

    if comparison_type == 'state':
        # Get state comparison data
        states = db.execute(select(BDState)).scalars().all()
        name_map = {s.state_code: s.state_name for s in states}

        # Get series
        series_query = select(
            BDSeries.series_id, BDSeries.state_code, BDSeries.dataclass_code
        ).where(
            and_(
                BDSeries.industry_code == '000000',
                BDSeries.seasonal_code == seasonal_code,
                BDSeries.periodicity_code == 'Q',
                BDSeries.sizeclass_code == '00',
                BDSeries.dataelement_code == dataelement_code,
                BDSeries.ratelevel_code == ratelevel_code,
                BDSeries.dataclass_code.in_(['01', '04']),
                BDSeries.state_code != '00'  # Exclude US total
            )
        )
        series_results = db.execute(series_query).all()
        series_map = {r[0]: (r[1], r[2]) for r in series_results}
        code_field = 'state_code'
    else:
        # Get industry comparison data
        industries = db.execute(
            select(BDIndustry).where(BDIndustry.display_level <= 2)
        ).scalars().all()
        name_map = {i.industry_code: i.industry_name for i in industries}

        # Get series
        series_query = select(
            BDSeries.series_id, BDSeries.industry_code, BDSeries.dataclass_code
        ).where(
            and_(
                BDSeries.state_code == '00',
                BDSeries.seasonal_code == seasonal_code,
                BDSeries.periodicity_code == 'Q',
                BDSeries.sizeclass_code == '00',
                BDSeries.dataelement_code == dataelement_code,
                BDSeries.ratelevel_code == ratelevel_code,
                BDSeries.dataclass_code.in_(['01', '04']),
                BDSeries.industry_code.in_(list(name_map.keys()))
            )
        )
        series_results = db.execute(series_query).all()
        series_map = {r[0]: (r[1], r[2]) for r in series_results}
        code_field = 'industry_code'

    series_ids = list(series_map.keys())

    # Get current and previous quarter data
    data_results = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == year,
                BDData.period == period
            )
        )
    ).all()

    # Get previous quarter
    prev_year, prev_period = year, period
    if period == 'Q01':
        prev_year, prev_period = year - 1, 'Q04'
    elif period == 'Q02':
        prev_period = 'Q01'
    elif period == 'Q03':
        prev_period = 'Q02'
    elif period == 'Q04':
        prev_period = 'Q03'

    prev_data = db.execute(
        select(BDData.series_id, BDData.value)
        .where(
            and_(
                BDData.series_id.in_(series_ids),
                BDData.year == prev_year,
                BDData.period == prev_period
            )
        )
    ).all()

    # Organize data
    current_map = {d[0]: decimal_to_float(d[1]) for d in data_results}
    prev_map = {d[0]: decimal_to_float(d[1]) for d in prev_data}

    entity_data = {}  # code -> {gains, losses, prev_gains, prev_losses}
    for sid, (code, dc) in series_map.items():
        if code not in entity_data:
            entity_data[code] = {}
        if dc == '01':
            entity_data[code]['gains'] = current_map.get(sid)
            entity_data[code]['prev_gains'] = prev_map.get(sid)
        else:
            entity_data[code]['losses'] = current_map.get(sid)
            entity_data[code]['prev_losses'] = prev_map.get(sid)

    # Calculate metric and changes
    items = []
    for code, d in entity_data.items():
        gains = d.get('gains')
        losses = d.get('losses')
        prev_gains = d.get('prev_gains')
        prev_losses = d.get('prev_losses')

        if metric == 'gross_gains':
            value = gains
            prev_value = prev_gains
        elif metric == 'gross_losses':
            value = losses
            prev_value = prev_losses
        else:  # net_change
            value = gains - losses if gains and losses else None
            prev_value = prev_gains - prev_losses if prev_gains and prev_losses else None

        if value is not None:
            change = value - prev_value if prev_value else None
            pct_change = (change / abs(prev_value) * 100) if change and prev_value and prev_value != 0 else None
            items.append(BDTopMoverItem(
                code=code,
                name=name_map.get(code, code),
                value=value,
                change=change,
                pct_change=pct_change
            ))

    # Sort
    items.sort(key=lambda x: x.value or 0, reverse=True)
    top_gainers = items[:limit]

    items.sort(key=lambda x: x.value or 0)
    top_losers = items[:limit]

    return BDTopMoversResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        metric=metric,
        ratelevel_code=ratelevel_code,
        dataelement_code=dataelement_code,
        comparison_type=comparison_type,
        top_gainers=top_gainers,
        top_losers=top_losers
    )


# ============================================================================
# TREND ENDPOINT
# ============================================================================

@router.get("/trend", response_model=BDTrendResponse)
async def get_trend(
    state_code: str = Query('00'),
    industry_code: str = Query('000000'),
    dataclass_code: str = Query('01'),
    ratelevel_code: str = Query('L'),
    dataelement_code: str = Query('1'),
    seasonal_code: str = Query('S'),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get historical trend for a specific metric"""
    state = db.execute(select(BDState).where(BDState.state_code == state_code)).scalar()
    industry = db.execute(select(BDIndustry).where(BDIndustry.industry_code == industry_code)).scalar()
    dataclass = db.execute(select(BDDataClass).where(BDDataClass.dataclass_code == dataclass_code)).scalar()
    ratelevel = db.execute(select(BDRateLevel).where(BDRateLevel.ratelevel_code == ratelevel_code)).scalar()
    dataelement = db.execute(select(BDDataElement).where(BDDataElement.dataelement_code == dataelement_code)).scalar()

    # Get series
    series = db.execute(
        select(BDSeries.series_id).where(
            and_(
                BDSeries.state_code == state_code,
                BDSeries.industry_code == industry_code,
                BDSeries.seasonal_code == seasonal_code,
                BDSeries.periodicity_code == 'Q',
                BDSeries.sizeclass_code == '00',
                BDSeries.dataelement_code == dataelement_code,
                BDSeries.ratelevel_code == ratelevel_code,
                BDSeries.dataclass_code == dataclass_code
            )
        )
    ).scalar()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    # Get data
    data_query = select(BDData.year, BDData.period, BDData.value).where(
        BDData.series_id == series
    )
    if start_year:
        data_query = data_query.where(BDData.year >= start_year)
    data_query = data_query.order_by(BDData.year, BDData.period)

    data_results = db.execute(data_query).all()

    # Calculate YoY changes
    data_map = {(d[0], d[1]): decimal_to_float(d[2]) for d in data_results}

    trend = []
    for yr, per, val in data_results:
        value = decimal_to_float(val)
        yoy_value = data_map.get((yr - 1, per))
        yoy_change = value - yoy_value if value and yoy_value else None
        yoy_pct = (yoy_change / abs(yoy_value) * 100) if yoy_change and yoy_value and yoy_value != 0 else None

        trend.append(BDTrendPoint(
            year=yr,
            period=per,
            period_name=get_period_name(per, yr),
            value=value,
            yoy_change=yoy_change,
            yoy_pct_change=yoy_pct
        ))

    return BDTrendResponse(
        state_code=state_code,
        state_name=state.state_name if state else 'Unknown',
        industry_code=industry_code,
        industry_name=industry.industry_name if industry else 'Unknown',
        dataclass_code=dataclass_code,
        dataclass_name=dataclass.dataclass_name if dataclass else dataclass_code,
        ratelevel_code=ratelevel_code,
        ratelevel_name=ratelevel.ratelevel_name if ratelevel else ratelevel_code,
        dataelement_code=dataelement_code,
        dataelement_name=dataelement.dataelement_name if dataelement else 'Employment',
        seasonal_code=seasonal_code,
        data=trend
    )
