"""
EC (Employment Cost Index) Explorer API

Provides endpoints for exploring ECI data including:
- Index levels for total compensation, wages/salaries, and benefits
- 3-month and 12-month percent changes
- Worker group breakdowns (occupation and industry combinations)
- Ownership comparisons (Civilian, Private, State/Local govt)

Data is quarterly, from 1980-2005 (legacy survey).
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import (
    ECCompensation, ECGroup, ECOwnership, ECPeriodicity, ECSeries, ECData
)
from .ec_schemas import (
    ECDimensions, ECDimensionItem,
    ECSeriesInfo, ECSeriesListResponse,
    ECDataPoint, ECSeriesData, ECDataResponse,
    ECCostMetric, ECOverviewResponse,
    ECTimelinePoint, ECTimelineResponse,
    ECGroupMetric, ECGroupAnalysisResponse,
    ECGroupTimelinePoint, ECGroupTimelineResponse,
    ECOwnershipMetric, ECOwnershipComparisonResponse,
    ECOwnershipTimelinePoint, ECOwnershipTimelineResponse
)

router = APIRouter(prefix="/api/research/bls/ec", tags=["BLS EC Research"])


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
    period_map = {
        'Q01': '1st Quarter',
        'Q02': '2nd Quarter',
        'Q03': '3rd Quarter',
        'Q04': '4th Quarter',
        'Q05': 'Annual Average'
    }
    return period_map.get(period, period)


# Major worker groups for overview (key occupation/industry groups)
MAJOR_GROUPS = ['000', '110', '120', '130', '200', '210', '240']


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=ECDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering EC data"""
    # Compensation types
    compensations = db.execute(
        select(ECCompensation).order_by(ECCompensation.comp_code)
    ).scalars().all()

    # Worker groups
    groups = db.execute(
        select(ECGroup).order_by(ECGroup.group_code)
    ).scalars().all()

    # Ownership types
    ownerships = db.execute(
        select(ECOwnership).order_by(ECOwnership.ownership_code)
    ).scalars().all()

    # Periodicity types
    periodicities = db.execute(
        select(ECPeriodicity).order_by(ECPeriodicity.periodicity_code)
    ).scalars().all()

    return ECDimensions(
        compensations=[ECDimensionItem(
            code=c.comp_code,
            name=c.comp_text
        ) for c in compensations],
        groups=[ECDimensionItem(
            code=g.group_code,
            name=g.group_name
        ) for g in groups],
        ownerships=[ECDimensionItem(
            code=o.ownership_code,
            name=o.ownership_name
        ) for o in ownerships],
        periodicities=[ECDimensionItem(
            code=p.periodicity_code,
            name=p.periodicity_text
        ) for p in periodicities]
    )


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================

@router.get("/series", response_model=ECSeriesListResponse)
async def get_series(
    comp_code: Optional[str] = Query(None, description="Filter by compensation type"),
    group_code: Optional[str] = Query(None, description="Filter by worker group"),
    ownership_code: Optional[str] = Query(None, description="Filter by ownership type"),
    periodicity_code: Optional[str] = Query(None, description="Filter by periodicity (I/Q/A)"),
    seasonal: Optional[str] = Query(None, description="Filter by seasonal adjustment (S/U)"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Get list of EC series with optional filters"""
    query = select(ECSeries)

    if comp_code:
        query = query.where(ECSeries.comp_code == comp_code)
    if group_code:
        query = query.where(ECSeries.group_code == group_code)
    if ownership_code:
        query = query.where(ECSeries.ownership_code == ownership_code)
    if periodicity_code:
        query = query.where(ECSeries.periodicity_code == periodicity_code)
    if seasonal:
        query = query.where(ECSeries.seasonal == seasonal)

    # Get total count
    has_filters = any([comp_code, group_code, ownership_code, periodicity_code, seasonal])
    if has_filters:
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar()
    else:
        total = db.execute(select(func.count()).select_from(ECSeries)).scalar()

    # Get paginated results
    query = query.order_by(ECSeries.series_id).limit(limit).offset(offset)
    series_list = db.execute(query).scalars().all()

    # Get dimension names in batch
    comp_codes = list(set(s.comp_code for s in series_list if s.comp_code))
    group_codes = list(set(s.group_code for s in series_list if s.group_code))
    ownership_codes = list(set(s.ownership_code for s in series_list if s.ownership_code))
    periodicity_codes = list(set(s.periodicity_code for s in series_list if s.periodicity_code))

    comp_names = {}
    if comp_codes:
        comps = db.execute(
            select(ECCompensation.comp_code, ECCompensation.comp_text)
            .where(ECCompensation.comp_code.in_(comp_codes))
        ).all()
        comp_names = {c.comp_code: c.comp_text for c in comps}

    group_names = {}
    if group_codes:
        groups = db.execute(
            select(ECGroup.group_code, ECGroup.group_name)
            .where(ECGroup.group_code.in_(group_codes))
        ).all()
        group_names = {g.group_code: g.group_name for g in groups}

    ownership_names = {}
    if ownership_codes:
        owners = db.execute(
            select(ECOwnership.ownership_code, ECOwnership.ownership_name)
            .where(ECOwnership.ownership_code.in_(ownership_codes))
        ).all()
        ownership_names = {o.ownership_code: o.ownership_name for o in owners}

    periodicity_names = {}
    if periodicity_codes:
        periods = db.execute(
            select(ECPeriodicity.periodicity_code, ECPeriodicity.periodicity_text)
            .where(ECPeriodicity.periodicity_code.in_(periodicity_codes))
        ).all()
        periodicity_names = {p.periodicity_code: p.periodicity_text for p in periods}

    return ECSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=[ECSeriesInfo(
            series_id=s.series_id,
            comp_code=s.comp_code,
            comp_name=comp_names.get(s.comp_code),
            group_code=s.group_code,
            group_name=group_names.get(s.group_code),
            ownership_code=s.ownership_code,
            ownership_name=ownership_names.get(s.ownership_code),
            periodicity_code=s.periodicity_code,
            periodicity_name=periodicity_names.get(s.periodicity_code),
            seasonal=s.seasonal,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active if s.is_active is not None else True
        ) for s in series_list]
    )


@router.get("/series/{series_id}/data", response_model=ECDataResponse)
async def get_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get time series data for a specific series"""
    # Verify series exists
    series = db.execute(
        select(ECSeries).where(ECSeries.series_id == series_id)
    ).scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    # Get data
    query = select(ECData).where(ECData.series_id == series_id)
    if start_year:
        query = query.where(ECData.year >= start_year)
    if end_year:
        query = query.where(ECData.year <= end_year)
    query = query.order_by(ECData.year, ECData.period)

    data_points = db.execute(query).scalars().all()

    # Build series title
    comp_name = db.execute(
        select(ECCompensation.comp_text)
        .where(ECCompensation.comp_code == series.comp_code)
    ).scalar_one_or_none() or series.comp_code

    group_name = db.execute(
        select(ECGroup.group_name)
        .where(ECGroup.group_code == series.group_code)
    ).scalar_one_or_none() or series.group_code

    ownership_name = db.execute(
        select(ECOwnership.ownership_name)
        .where(ECOwnership.ownership_code == series.ownership_code)
    ).scalar_one_or_none() or series.ownership_code

    series_title = f"{comp_name} - {group_name} ({ownership_name})"

    return ECDataResponse(
        series=[ECSeriesData(
            series_id=series_id,
            series_title=series_title,
            data_points=[ECDataPoint(
                year=d.year,
                period=d.period,
                period_name=get_period_name(d.period),
                value=decimal_to_float(d.value),
                footnote_codes=d.footnote_codes
            ) for d in data_points]
        )]
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=ECOverviewResponse)
async def get_overview(
    ownership_code: str = Query("2", description="Ownership type (1=Civilian, 2=Private, 3=State/local)"),
    db: Session = Depends(get_data_db)
):
    """Get overview dashboard with headline ECI metrics for a given ownership type"""
    # Batch query 1: Get dimension names
    ownership_name = db.execute(
        select(ECOwnership.ownership_name)
        .where(ECOwnership.ownership_code == ownership_code)
    ).scalar_one_or_none() or "Private industry"

    comp_names = {c.comp_code: c.comp_text for c in db.execute(
        select(ECCompensation.comp_code, ECCompensation.comp_text)
    ).all()}

    periodicity_names = {p.periodicity_code: p.periodicity_text for p in db.execute(
        select(ECPeriodicity.periodicity_code, ECPeriodicity.periodicity_text)
    ).all()}

    # Batch query 2: Get all relevant series (9 combinations: 3 comp types × 3 periodicities)
    series_query = db.execute(
        select(ECSeries.series_id, ECSeries.comp_code, ECSeries.periodicity_code)
        .where(and_(
            ECSeries.group_code == '000',  # All workers
            ECSeries.ownership_code == ownership_code,
            ECSeries.seasonal == 'S'
        ))
    ).all()

    # Build series map: {(comp_code, periodicity_code): series_id}
    series_map = {(s.comp_code, s.periodicity_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    if not all_series_ids:
        return ECOverviewResponse(
            ownership=ownership_code,
            ownership_name=ownership_name,
            data_range="No data available"
        )

    # Batch query 3: Get latest data point per series (using window function approach)
    # Get latest year/period for the data range
    latest_data = db.execute(
        select(ECData.year, ECData.period)
        .where(ECData.series_id.in_(all_series_ids))
        .order_by(desc(ECData.year), desc(ECData.period))
        .limit(1)
    ).first()

    if not latest_data:
        return ECOverviewResponse(
            ownership=ownership_code,
            ownership_name=ownership_name,
            data_range="No data available"
        )

    latest_year, latest_period = latest_data

    # Get earliest for data range
    earliest_data = db.execute(
        select(ECData.year, ECData.period)
        .where(ECData.series_id.in_(all_series_ids))
        .order_by(ECData.year, ECData.period)
        .limit(1)
    ).first()

    data_range = f"Q{earliest_data.period[-1]} {earliest_data.year} - Q{latest_period[-1]} {latest_year}" if earliest_data else None

    # Batch query 4: Get latest values for all series
    latest_values = db.execute(
        select(ECData.series_id, ECData.value, ECData.year, ECData.period)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year == latest_year,
            ECData.period == latest_period
        ))
    ).all()
    latest_map = {d.series_id: {'value': d.value, 'year': d.year, 'period': d.period} for d in latest_values}

    # Batch query 5: Get previous year values for YoY calculation
    prev_year_values = db.execute(
        select(ECData.series_id, ECData.value)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year == latest_year - 1,
            ECData.period == latest_period
        ))
    ).all()
    prev_map = {d.series_id: d.value for d in prev_year_values}

    # Helper function to build metric from cached data
    def build_metric(comp_code: str, periodicity_code: str) -> Optional[ECCostMetric]:
        series_id = series_map.get((comp_code, periodicity_code))
        if not series_id or series_id not in latest_map:
            return None

        latest = latest_map[series_id]
        prev_val = prev_map.get(series_id)

        yoy_change = None
        if latest['value'] is not None and prev_val is not None:
            if periodicity_code == 'I':  # Index - calculate percent change
                yoy_change = round((float(latest['value']) - float(prev_val)) / float(prev_val) * 100, 2)
            else:  # Already percent change - calculate difference
                yoy_change = round(float(latest['value']) - float(prev_val), 2)

        comp_name = comp_names.get(comp_code, comp_code)
        periodicity_name = periodicity_names.get(periodicity_code, periodicity_code)

        return ECCostMetric(
            series_id=series_id,
            name=f"{comp_name} - All Workers",
            comp_type=comp_name,
            periodicity_type=periodicity_name,
            latest_value=decimal_to_float(latest['value']),
            latest_year=latest['year'],
            latest_period=latest['period'],
            previous_value=decimal_to_float(prev_val),
            yoy_change=yoy_change
        )

    return ECOverviewResponse(
        ownership=ownership_code,
        ownership_name=ownership_name,
        # Index values
        total_compensation_index=build_metric('1', 'I'),
        wages_salaries_index=build_metric('2', 'I'),
        benefits_index=build_metric('3', 'I'),
        # Quarterly percent changes
        total_compensation_quarterly=build_metric('1', 'Q'),
        wages_salaries_quarterly=build_metric('2', 'Q'),
        benefits_quarterly=build_metric('3', 'Q'),
        # Annual percent changes
        total_compensation_annual=build_metric('1', 'A'),
        wages_salaries_annual=build_metric('2', 'A'),
        benefits_annual=build_metric('3', 'A'),
        data_range=data_range
    )


# ============================================================================
# TIMELINE ENDPOINTS
# ============================================================================

@router.get("/timeline", response_model=ECTimelineResponse)
async def get_timeline(
    ownership_code: str = Query("2", description="Ownership type"),
    periodicity_code: str = Query("I", description="I=Index, Q=3-month %, A=12-month %"),
    years: int = Query(10, description="Number of years"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for all compensation types"""
    # Get ownership name
    ownership_name = db.execute(
        select(ECOwnership.ownership_name)
        .where(ECOwnership.ownership_code == ownership_code)
    ).scalar_one_or_none() or ownership_code

    periodicity_name = db.execute(
        select(ECPeriodicity.periodicity_text)
        .where(ECPeriodicity.periodicity_code == periodicity_code)
    ).scalar_one_or_none() or periodicity_code

    # Get latest year
    latest_year = db.execute(select(func.max(ECData.year))).scalar()
    start_year = latest_year - years if latest_year and years > 0 else 1980

    # Batch query: Get all series for this ownership/periodicity
    series_query = db.execute(
        select(ECSeries.series_id, ECSeries.comp_code)
        .where(and_(
            ECSeries.group_code == '000',  # All workers
            ECSeries.ownership_code == ownership_code,
            ECSeries.periodicity_code == periodicity_code,
            ECSeries.seasonal == 'S'
        ))
    ).all()
    series_map = {s.comp_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(ECData.series_id, ECData.year, ECData.period, ECData.value)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year >= start_year,
            ECData.period != 'Q05'  # Exclude annual averages for timeline
        ))
        .order_by(ECData.year, ECData.period)
    ).all() if all_series_ids else []

    # Build data lookup: {(series_id, year, period): value}
    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}

    # Get unique year/period combinations
    periods_set = set((d.year, d.period) for d in data_query)
    periods_sorted = sorted(periods_set, key=lambda x: (x[0], x[1]))

    # Build timeline
    timeline = []
    for year, period in periods_sorted:
        timeline.append(ECTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(period),
            total_compensation=data_map.get((series_map.get('1'), year, period)),
            wages_salaries=data_map.get((series_map.get('2'), year, period)),
            benefits=data_map.get((series_map.get('3'), year, period))
        ))

    return ECTimelineResponse(
        ownership=ownership_code,
        ownership_name=ownership_name,
        periodicity=periodicity_name,
        timeline=timeline
    )


# ============================================================================
# GROUP ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/groups", response_model=ECGroupAnalysisResponse)
async def get_groups(
    ownership_code: str = Query("2", description="Ownership type"),
    comp_code: str = Query("1", description="Compensation type (1/2/3)"),
    db: Session = Depends(get_data_db)
):
    """Get analysis by worker group"""
    # Get ownership and compensation names
    ownership_name = db.execute(
        select(ECOwnership.ownership_name)
        .where(ECOwnership.ownership_code == ownership_code)
    ).scalar_one_or_none() or ownership_code

    comp_name = db.execute(
        select(ECCompensation.comp_text)
        .where(ECCompensation.comp_code == comp_code)
    ).scalar_one_or_none() or comp_code

    # Get latest year
    latest_year = db.execute(select(func.max(ECData.year))).scalar()

    # Get all groups
    groups = db.execute(
        select(ECGroup).order_by(ECGroup.group_code)
    ).scalars().all()

    # Batch query: Get all series for this ownership/comp type
    series_query = db.execute(
        select(ECSeries.series_id, ECSeries.group_code, ECSeries.periodicity_code)
        .where(and_(
            ECSeries.ownership_code == ownership_code,
            ECSeries.comp_code == comp_code,
            ECSeries.seasonal == 'S'
        ))
    ).all()

    # Build series maps: {(group_code, periodicity): series_id}
    series_map = {(s.group_code, s.periodicity_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get latest data for all series
    data_query = db.execute(
        select(ECData.series_id, ECData.value)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year == latest_year,
            ECData.period == 'Q04'  # Last quarter
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: decimal_to_float(d.value) for d in data_query}

    # Build results
    results = []
    for g in groups:
        index_series = series_map.get((g.group_code, 'I'))
        quarterly_series = series_map.get((g.group_code, 'Q'))
        annual_series = series_map.get((g.group_code, 'A'))

        # Only include groups that have data
        index_val = data_map.get(index_series) if index_series else None
        if index_val is not None:
            results.append(ECGroupMetric(
                group_code=g.group_code,
                group_name=g.group_name,
                index_value=index_val,
                quarterly_change=data_map.get(quarterly_series) if quarterly_series else None,
                annual_change=data_map.get(annual_series) if annual_series else None,
                latest_year=latest_year,
                latest_period='Q04'
            ))

    return ECGroupAnalysisResponse(
        ownership=ownership_code,
        ownership_name=ownership_name,
        comp_type=comp_name,
        groups=results,
        latest_year=latest_year
    )


@router.get("/groups/timeline", response_model=ECGroupTimelineResponse)
async def get_groups_timeline(
    ownership_code: str = Query("2"),
    comp_code: str = Query("1"),
    periodicity_code: str = Query("I"),
    group_codes: Optional[str] = Query(None, description="Comma-separated group codes"),
    years: int = Query(10),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for group comparison"""
    ownership_name = db.execute(
        select(ECOwnership.ownership_name)
        .where(ECOwnership.ownership_code == ownership_code)
    ).scalar_one_or_none() or ownership_code

    periodicity_name = db.execute(
        select(ECPeriodicity.periodicity_text)
        .where(ECPeriodicity.periodicity_code == periodicity_code)
    ).scalar_one_or_none() or periodicity_code

    comp_name = db.execute(
        select(ECCompensation.comp_text)
        .where(ECCompensation.comp_code == comp_code)
    ).scalar_one_or_none() or comp_code

    # Parse group codes
    codes = group_codes.split(',') if group_codes else MAJOR_GROUPS

    # Get latest year
    latest_year = db.execute(select(func.max(ECData.year))).scalar()
    start_year = latest_year - years if latest_year and years > 0 else 1980

    # Batch query 1: Get group names
    group_query = db.execute(
        select(ECGroup.group_code, ECGroup.group_name)
        .where(ECGroup.group_code.in_(codes))
    ).all()
    group_names = {g.group_code: g.group_name for g in group_query}

    # Batch query 2: Get all series
    series_query = db.execute(
        select(ECSeries.series_id, ECSeries.group_code)
        .where(and_(
            ECSeries.group_code.in_(codes),
            ECSeries.ownership_code == ownership_code,
            ECSeries.comp_code == comp_code,
            ECSeries.periodicity_code == periodicity_code,
            ECSeries.seasonal == 'S'
        ))
    ).all()
    series_map = {s.group_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query 3: Get all data
    data_query = db.execute(
        select(ECData.series_id, ECData.year, ECData.period, ECData.value)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year >= start_year,
            ECData.period != 'Q05'
        ))
        .order_by(ECData.year, ECData.period)
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}

    # Get unique year/period combinations
    periods_set = set((d.year, d.period) for d in data_query)
    periods_sorted = sorted(periods_set, key=lambda x: (x[0], x[1]))

    # Build timeline
    timeline = []
    for year, period in periods_sorted:
        point = ECGroupTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(period),
            groups={}
        )
        for code in codes:
            series_id = series_map.get(code)
            if series_id:
                point.groups[code] = data_map.get((series_id, year, period))
            else:
                point.groups[code] = None
        timeline.append(point)

    return ECGroupTimelineResponse(
        ownership=ownership_code,
        periodicity=periodicity_name,
        comp_type=comp_name,
        timeline=timeline,
        group_names=group_names
    )


# ============================================================================
# OWNERSHIP COMPARISON ENDPOINTS
# ============================================================================

@router.get("/ownership-comparison", response_model=ECOwnershipComparisonResponse)
async def get_ownership_comparison(
    comp_code: str = Query("1", description="Compensation type"),
    group_code: str = Query("000", description="Worker group"),
    db: Session = Depends(get_data_db)
):
    """Compare across ownership types for a given compensation/group"""
    comp_name = db.execute(
        select(ECCompensation.comp_text)
        .where(ECCompensation.comp_code == comp_code)
    ).scalar_one_or_none() or comp_code

    group_name = db.execute(
        select(ECGroup.group_name)
        .where(ECGroup.group_code == group_code)
    ).scalar_one_or_none() or group_code

    # Get latest year
    latest_year = db.execute(select(func.max(ECData.year))).scalar()

    # Get all ownership types
    ownerships = db.execute(
        select(ECOwnership).order_by(ECOwnership.ownership_code)
    ).scalars().all()

    # Batch query: Get all series
    series_query = db.execute(
        select(ECSeries.series_id, ECSeries.ownership_code, ECSeries.periodicity_code)
        .where(and_(
            ECSeries.comp_code == comp_code,
            ECSeries.group_code == group_code,
            ECSeries.seasonal == 'S'
        ))
    ).all()

    series_map = {(s.ownership_code, s.periodicity_code): s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get latest data
    data_query = db.execute(
        select(ECData.series_id, ECData.value, ECData.period)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year == latest_year,
            ECData.period == 'Q04'
        ))
    ).all() if all_series_ids else []

    data_map = {d.series_id: (decimal_to_float(d.value), d.period) for d in data_query}

    results = []
    latest_period = None
    for o in ownerships:
        index_series = series_map.get((o.ownership_code, 'I'))
        quarterly_series = series_map.get((o.ownership_code, 'Q'))
        annual_series = series_map.get((o.ownership_code, 'A'))

        index_val = data_map.get(index_series, (None, None))[0] if index_series else None
        if index_val is not None:
            if not latest_period and index_series in data_map:
                latest_period = data_map[index_series][1]

            results.append(ECOwnershipMetric(
                ownership_code=o.ownership_code,
                ownership_name=o.ownership_name,
                index_value=index_val,
                quarterly_change=data_map.get(quarterly_series, (None, None))[0] if quarterly_series else None,
                annual_change=data_map.get(annual_series, (None, None))[0] if annual_series else None
            ))

    return ECOwnershipComparisonResponse(
        comp_type=comp_name,
        group_name=group_name,
        ownerships=results,
        latest_year=latest_year,
        latest_period=latest_period
    )


@router.get("/ownership-comparison/timeline", response_model=ECOwnershipTimelineResponse)
async def get_ownership_timeline(
    comp_code: str = Query("1"),
    periodicity_code: str = Query("I"),
    years: int = Query(10),
    db: Session = Depends(get_data_db)
):
    """Get timeline comparing across ownership types"""
    comp_name = db.execute(
        select(ECCompensation.comp_text)
        .where(ECCompensation.comp_code == comp_code)
    ).scalar_one_or_none() or comp_code

    periodicity_name = db.execute(
        select(ECPeriodicity.periodicity_text)
        .where(ECPeriodicity.periodicity_code == periodicity_code)
    ).scalar_one_or_none() or periodicity_code

    # Get all ownerships
    ownerships = db.execute(
        select(ECOwnership).order_by(ECOwnership.ownership_code)
    ).scalars().all()
    ownership_names = {o.ownership_code: o.ownership_name for o in ownerships}
    ownership_codes = [o.ownership_code for o in ownerships]

    # Get latest year
    latest_year = db.execute(select(func.max(ECData.year))).scalar()
    start_year = latest_year - years if latest_year and years > 0 else 1980

    # Batch query: Get all series
    series_query = db.execute(
        select(ECSeries.series_id, ECSeries.ownership_code)
        .where(and_(
            ECSeries.comp_code == comp_code,
            ECSeries.group_code == '000',  # All workers
            ECSeries.periodicity_code == periodicity_code,
            ECSeries.seasonal == 'S'
        ))
    ).all()
    series_map = {s.ownership_code: s.series_id for s in series_query}
    all_series_ids = [s.series_id for s in series_query]

    # Batch query: Get all data
    data_query = db.execute(
        select(ECData.series_id, ECData.year, ECData.period, ECData.value)
        .where(and_(
            ECData.series_id.in_(all_series_ids),
            ECData.year >= start_year,
            ECData.period != 'Q05'
        ))
        .order_by(ECData.year, ECData.period)
    ).all() if all_series_ids else []

    data_map = {(d.series_id, d.year, d.period): decimal_to_float(d.value) for d in data_query}

    # Get unique year/period combinations
    periods_set = set((d.year, d.period) for d in data_query)
    periods_sorted = sorted(periods_set, key=lambda x: (x[0], x[1]))

    # Build timeline
    timeline = []
    for year, period in periods_sorted:
        point = ECOwnershipTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(period),
            ownerships={}
        )
        for code in ownership_codes:
            series_id = series_map.get(code)
            if series_id:
                point.ownerships[code] = data_map.get((series_id, year, period))
            else:
                point.ownerships[code] = None
        timeline.append(point)

    return ECOwnershipTimelineResponse(
        comp_type=comp_name,
        periodicity=periodicity_name,
        timeline=timeline,
        ownership_names=ownership_names
    )
