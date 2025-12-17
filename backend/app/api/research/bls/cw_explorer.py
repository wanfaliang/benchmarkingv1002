"""
CW (Consumer Price Index - Urban Wage Earners and Clerical Workers) Survey Explorer API

CPI-W is used for:
- Social Security COLA adjustments (using Q3 average)
- Federal civil service retirees
- Military retirees
- Food stamp program benefits

Structure identical to CU but covers ~29% of U.S. population (wage earners/clerical workers)
vs CU which covers ~93% (all urban consumers).
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List

from ....database import get_data_db
from ....api.auth import get_current_user
from .cw_schemas import (
    CWDimensions, CWAreaItem, CWItemItem,
    CWSeriesInfo, CWSeriesListResponse,
    CWDataPoint, CWSeriesData, CWDataResponse,
    InflationMetric, CWOverviewResponse,
    CategoryMetric, CWCategoryAnalysisResponse,
    AreaComparisonMetric, CWAreaComparisonResponse,
    TimelineDataPoint, CWOverviewTimelineResponse,
    CategoryTimelineData, CWCategoryTimelineResponse,
    AreaTimelineData, CWAreaTimelineResponse,
    CWTopMover, CWTopMoversResponse
)
from ....data_models.bls_models import (
    CWArea, CWItem, CWSeries, CWData, BLSPeriod
)

router = APIRouter(
    prefix="/api/research/bls/cw",
    tags=["BLS CW - CPI for Urban Wage Earners"]
)


# Major CPI categories (8 expenditure categories)
MAJOR_CATEGORIES = {
    'SAF': 'Food and beverages',
    'SAH': 'Housing',
    'SAA': 'Apparel',
    'SAT': 'Transportation',
    'SAM': 'Medical care',
    'SAR': 'Recreation',
    'SAE': 'Education and communication',
    'SAG': 'Other goods and services',
}

# Key aggregate indexes
KEY_INDEXES = {
    'SA0': 'All items',
    'SA0L1E': 'All items less food and energy',
    'SA0E': 'Energy',
    'SAC': 'Commodities',
    'SAS': 'Services',
}


def _get_area_type(area_code: str) -> str:
    """Determine area type from area code"""
    if not area_code:
        return "unknown"
    if area_code == "0000":
        return "national"
    if area_code.startswith("0") and len(area_code) == 4:
        return "region"
    if area_code.startswith("S") and len(area_code) == 4:
        if area_code[1:].isdigit():
            return "size_class"
        return "metro"
    if area_code.startswith(("A", "D", "N", "X")):
        return "metro" if area_code.startswith("A") else "size_class"
    return "other"


def _get_period_name(year: int, period: str, db: Session) -> str:
    """Get human-readable period name"""
    period_info = db.query(BLSPeriod).filter(BLSPeriod.period_code == period).first()
    if period_info:
        return f"{period_info.period_name} {year}"

    month_map = {
        'M01': 'January', 'M02': 'February', 'M03': 'March', 'M04': 'April',
        'M05': 'May', 'M06': 'June', 'M07': 'July', 'M08': 'August',
        'M09': 'September', 'M10': 'October', 'M11': 'November', 'M12': 'December',
        'M13': 'Annual Average', 'S01': 'First Half', 'S02': 'Second Half', 'S03': 'Annual'
    }
    return f"{month_map.get(period, period)} {year}"


def _calculate_inflation_metric(series_id: str, item_code: str, item_name: str, db: Session) -> Optional[InflationMetric]:
    """Calculate inflation metrics for a series"""
    # Get recent data (14 months to ensure YoY comparison)
    data = db.query(CWData).filter(
        CWData.series_id == series_id,
        CWData.period.like('M%'),
        CWData.period != 'M13'
    ).order_by(desc(CWData.year), desc(CWData.period)).limit(14).all()

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
    yoy = None

    if latest_value and prev_month and prev_month.value:
        prev_val = float(prev_month.value)
        if prev_val != 0:
            mom = round(((latest_value - prev_val) / prev_val) * 100, 2)

    if latest_value and prev_year and prev_year.value:
        prev_val = float(prev_year.value)
        if prev_val != 0:
            yoy = round(((latest_value - prev_val) / prev_val) * 100, 2)

    return InflationMetric(
        series_id=series_id,
        item_code=item_code,
        item_name=item_name,
        latest_value=latest_value,
        latest_date=_get_period_name(latest.year, latest.period, db),
        month_over_month=mom,
        year_over_year=yoy
    )


# =============================================================================
# DIMENSIONS ENDPOINT
# =============================================================================

@router.get("/dimensions", response_model=CWDimensions)
async def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get available dimensions for CW data filtering"""

    # Get all areas
    areas = db.query(CWArea).order_by(CWArea.sort_sequence).all()
    area_items = [
        CWAreaItem(
            area_code=a.area_code,
            area_name=a.area_name,
            display_level=a.display_level or 0,
            selectable=a.selectable == 'T',
            sort_sequence=a.sort_sequence or 0
        )
        for a in areas
    ]

    # Get all items
    items = db.query(CWItem).order_by(CWItem.sort_sequence).all()
    item_items = [
        CWItemItem(
            item_code=i.item_code,
            item_name=i.item_name,
            display_level=i.display_level or 0,
            selectable=i.selectable == 'T',
            sort_sequence=i.sort_sequence or 0
        )
        for i in items
    ]

    # Total series and date range
    total_series = db.query(func.count(CWSeries.series_id)).scalar() or 0
    min_year = db.query(func.min(CWData.year)).scalar()
    max_year = db.query(func.max(CWData.year)).scalar()
    data_range = f"{min_year}-{max_year}" if min_year and max_year else None

    return CWDimensions(
        areas=area_items,
        items=item_items,
        total_series=total_series,
        data_range=data_range
    )


# =============================================================================
# SERIES ENDPOINTS
# =============================================================================

@router.get("/series", response_model=CWSeriesListResponse)
async def get_series(
    area_code: Optional[str] = Query(None, description="Filter by area code"),
    item_code: Optional[str] = Query(None, description="Filter by item code"),
    seasonal_code: Optional[str] = Query(None, description="Filter by seasonal (S/U)"),
    search: Optional[str] = Query(None, description="Search series title"),
    active_only: bool = Query(True, description="Only active series"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get CW series list with optional filters"""

    query = db.query(
        CWSeries,
        CWArea.area_name,
        CWItem.item_name
    ).outerjoin(
        CWArea, CWSeries.area_code == CWArea.area_code
    ).outerjoin(
        CWItem, CWSeries.item_code == CWItem.item_code
    )

    if area_code:
        query = query.filter(CWSeries.area_code == area_code)
    if item_code:
        query = query.filter(CWSeries.item_code == item_code)
    if seasonal_code:
        query = query.filter(CWSeries.seasonal_code == seasonal_code)
    if search:
        query = query.filter(CWSeries.series_title.ilike(f"%{search}%"))
    if active_only:
        query = query.filter(CWSeries.is_active == True)

    total = query.count()
    results = query.order_by(CWSeries.series_id).offset(offset).limit(limit).all()

    series = [
        CWSeriesInfo(
            series_id=r.CWSeries.series_id,
            series_title=r.CWSeries.series_title,
            area_code=r.CWSeries.area_code or '',
            area_name=r.area_name or '',
            item_code=r.CWSeries.item_code or '',
            item_name=r.item_name or '',
            seasonal_code=r.CWSeries.seasonal_code or 'U',
            periodicity_code=r.CWSeries.periodicity_code,
            base_period=r.CWSeries.base_period,
            begin_year=r.CWSeries.begin_year,
            begin_period=r.CWSeries.begin_period,
            end_year=r.CWSeries.end_year,
            end_period=r.CWSeries.end_period,
            is_active=r.CWSeries.is_active if r.CWSeries.is_active is not None else True
        )
        for r in results
    ]

    return CWSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series
    )


@router.get("/series/{series_id}/data", response_model=CWDataResponse)
async def get_series_data(
    series_id: str,
    months: int = Query(60, ge=1, le=600, description="Number of months of data"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get time series data for a specific CW series"""

    series = db.query(
        CWSeries,
        CWArea.area_name,
        CWItem.item_name
    ).outerjoin(
        CWArea, CWSeries.area_code == CWArea.area_code
    ).outerjoin(
        CWItem, CWSeries.item_code == CWItem.item_code
    ).filter(
        CWSeries.series_id == series_id
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    data = db.query(CWData).filter(
        CWData.series_id == series_id,
        CWData.period.like('M%'),
        CWData.period != 'M13'
    ).order_by(desc(CWData.year), desc(CWData.period)).limit(months).all()

    data_points = [
        CWDataPoint(
            year=d.year,
            period=d.period,
            period_name=_get_period_name(d.year, d.period, db),
            value=float(d.value) if d.value else None,
            footnote_codes=d.footnote_codes
        )
        for d in reversed(data)
    ]

    return CWDataResponse(
        series=[CWSeriesData(
            series_id=series_id,
            series_title=series.CWSeries.series_title,
            area_name=series.area_name or '',
            item_name=series.item_name or '',
            data_points=data_points
        )]
    )


# =============================================================================
# OVERVIEW ENDPOINT
# =============================================================================

@router.get("/overview", response_model=CWOverviewResponse)
async def get_overview(
    area_code: str = Query("0000", description="Area code (default: U.S. city average)"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get CPI-W overview with key inflation metrics"""

    # Helper to find series and calculate metric
    def get_metric(item_code: str, item_name: str) -> Optional[InflationMetric]:
        series = db.query(CWSeries).filter(
            CWSeries.area_code == area_code,
            CWSeries.item_code == item_code,
            CWSeries.seasonal_code == 'U'  # Not seasonally adjusted for official figures
        ).first()

        if not series:
            # Try seasonally adjusted
            series = db.query(CWSeries).filter(
                CWSeries.area_code == area_code,
                CWSeries.item_code == item_code,
                CWSeries.seasonal_code == 'S'
            ).first()

        if series:
            return _calculate_inflation_metric(series.series_id, item_code, item_name, db)
        return None

    # Get latest date
    latest = db.query(CWData.year, CWData.period).filter(
        CWData.period.like('M%'),
        CWData.period != 'M13'
    ).order_by(desc(CWData.year), desc(CWData.period)).first()

    last_updated = _get_period_name(latest.year, latest.period, db) if latest else None

    return CWOverviewResponse(
        headline_cpi=get_metric('SA0', 'All items'),
        core_cpi=get_metric('SA0L1E', 'All items less food and energy'),
        food_beverages=get_metric('SAF', 'Food and beverages'),
        housing=get_metric('SAH', 'Housing'),
        apparel=get_metric('SAA', 'Apparel'),
        transportation=get_metric('SAT', 'Transportation'),
        medical_care=get_metric('SAM', 'Medical care'),
        recreation=get_metric('SAR', 'Recreation'),
        education_communication=get_metric('SAE', 'Education and communication'),
        other_goods_services=get_metric('SAG', 'Other goods and services'),
        energy=get_metric('SA0E', 'Energy'),
        last_updated=last_updated
    )


# =============================================================================
# OVERVIEW TIMELINE
# =============================================================================

@router.get("/overview/timeline", response_model=CWOverviewTimelineResponse)
async def get_overview_timeline(
    area_code: str = Query("0000", description="Area code"),
    months_back: int = Query(24, ge=0, le=600, description="Months of history (0 = all)"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get timeline data for headline and core CPI-W"""

    area = db.query(CWArea).filter(CWArea.area_code == area_code).first()
    area_name = area.area_name if area else area_code

    # Find headline and core series
    headline_series = db.query(CWSeries).filter(
        CWSeries.area_code == area_code,
        CWSeries.item_code == 'SA0',
        CWSeries.seasonal_code == 'U'
    ).first()

    core_series = db.query(CWSeries).filter(
        CWSeries.area_code == area_code,
        CWSeries.item_code == 'SA0L1E',
        CWSeries.seasonal_code == 'U'
    ).first()

    # Get data for both series (0 means all data)
    headline_data = {}
    core_data = {}
    fetch_limit = None if months_back == 0 else months_back + 12

    if headline_series:
        query = db.query(CWData).filter(
            CWData.series_id == headline_series.series_id,
            CWData.period.like('M%'),
            CWData.period != 'M13'
        ).order_by(desc(CWData.year), desc(CWData.period))
        data = query.all() if fetch_limit is None else query.limit(fetch_limit).all()

        for d in data:
            key = f"{d.year}-{d.period}"
            headline_data[key] = float(d.value) if d.value else None

    if core_series:
        query = db.query(CWData).filter(
            CWData.series_id == core_series.series_id,
            CWData.period.like('M%'),
            CWData.period != 'M13'
        ).order_by(desc(CWData.year), desc(CWData.period))
        data = query.all() if fetch_limit is None else query.limit(fetch_limit).all()

        for d in data:
            key = f"{d.year}-{d.period}"
            core_data[key] = float(d.value) if d.value else None

    # Build timeline
    timeline = []
    all_keys = sorted(set(headline_data.keys()) | set(core_data.keys()), reverse=True)
    if months_back > 0:
        all_keys = all_keys[:months_back]

    for key in reversed(all_keys):
        year, period = key.split('-')
        year = int(year)

        headline_val = headline_data.get(key)
        core_val = core_data.get(key)

        # Calculate YoY
        prev_year_key = f"{year - 1}-{period}"
        headline_yoy = None
        core_yoy = None

        if headline_val and prev_year_key in headline_data and headline_data[prev_year_key]:
            prev_val = headline_data[prev_year_key]
            headline_yoy = round(((headline_val - prev_val) / prev_val) * 100, 2)

        if core_val and prev_year_key in core_data and core_data[prev_year_key]:
            prev_val = core_data[prev_year_key]
            core_yoy = round(((core_val - prev_val) / prev_val) * 100, 2)

        timeline.append(TimelineDataPoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            date=f"{year}-{period[1:]}",
            headline_value=headline_val,
            headline_yoy=headline_yoy,
            headline_mom=None,  # Can calculate if needed
            core_value=core_val,
            core_yoy=core_yoy,
            core_mom=None
        ))

    return CWOverviewTimelineResponse(
        area_code=area_code,
        area_name=area_name,
        timeline=timeline
    )


# =============================================================================
# CATEGORY ANALYSIS
# =============================================================================

@router.get("/categories", response_model=CWCategoryAnalysisResponse)
async def get_category_analysis(
    area_code: str = Query("0000", description="Area code"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get analysis of major CPI-W expenditure categories"""

    area = db.query(CWArea).filter(CWArea.area_code == area_code).first()
    area_name = area.area_name if area else area_code

    categories = []

    for item_code, item_name in MAJOR_CATEGORIES.items():
        series = db.query(CWSeries).filter(
            CWSeries.area_code == area_code,
            CWSeries.item_code == item_code,
            CWSeries.seasonal_code == 'U'
        ).first()

        if not series:
            continue

        metric = _calculate_inflation_metric(series.series_id, item_code, item_name, db)
        if metric:
            categories.append(CategoryMetric(
                category_code=item_code,
                category_name=item_name,
                series_id=series.series_id,
                latest_value=metric.latest_value,
                latest_date=metric.latest_date,
                month_over_month=metric.month_over_month,
                year_over_year=metric.year_over_year,
                weight=None
            ))

    return CWCategoryAnalysisResponse(
        area_code=area_code,
        area_name=area_name,
        categories=categories
    )


# =============================================================================
# CATEGORY TIMELINE
# =============================================================================

@router.get("/categories/timeline", response_model=CWCategoryTimelineResponse)
async def get_category_timeline(
    area_code: str = Query("0000", description="Area code"),
    months_back: int = Query(24, ge=0, le=600, description="Months of history (0 = all)"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get timeline data for all major categories"""

    area = db.query(CWArea).filter(CWArea.area_code == area_code).first()
    area_name = area.area_name if area else area_code

    categories = []
    fetch_limit = None if months_back == 0 else months_back + 12

    for item_code, item_name in MAJOR_CATEGORIES.items():
        series = db.query(CWSeries).filter(
            CWSeries.area_code == area_code,
            CWSeries.item_code == item_code,
            CWSeries.seasonal_code == 'U'
        ).first()

        if not series:
            continue

        query = db.query(CWData).filter(
            CWData.series_id == series.series_id,
            CWData.period.like('M%'),
            CWData.period != 'M13'
        ).order_by(desc(CWData.year), desc(CWData.period))
        data = query.all() if fetch_limit is None else query.limit(fetch_limit).all()

        # Build lookup for YoY calculation
        data_lookup = {f"{d.year}-{d.period}": float(d.value) if d.value else None for d in data}

        timeline_data = []
        data_slice = list(reversed(data)) if months_back == 0 else list(reversed(data))[:months_back]
        for d in data_slice:
            val = float(d.value) if d.value else None
            prev_key = f"{d.year - 1}-{d.period}"
            yoy = None
            if val and prev_key in data_lookup and data_lookup[prev_key]:
                yoy = round(((val - data_lookup[prev_key]) / data_lookup[prev_key]) * 100, 2)

            timeline_data.append({
                'date': f"{d.year}-{d.period[1:]}",
                'value': val,
                'yoy': yoy
            })

        categories.append(CategoryTimelineData(
            category_code=item_code,
            category_name=item_name,
            series_id=series.series_id,
            data=timeline_data
        ))

    return CWCategoryTimelineResponse(
        area_code=area_code,
        area_name=area_name,
        categories=categories
    )


# =============================================================================
# AREA COMPARISON
# =============================================================================

@router.get("/areas/compare", response_model=CWAreaComparisonResponse)
async def compare_areas(
    item_code: str = Query("SA0", description="Item code to compare"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Compare CPI-W for an item across all areas"""

    item = db.query(CWItem).filter(CWItem.item_code == item_code).first()
    item_name = item.item_name if item else item_code

    # Get all series for this item
    series_list = db.query(
        CWSeries,
        CWArea.area_name
    ).outerjoin(
        CWArea, CWSeries.area_code == CWArea.area_code
    ).filter(
        CWSeries.item_code == item_code,
        CWSeries.seasonal_code == 'U'
    ).all()

    areas = []
    for s in series_list:
        metric = _calculate_inflation_metric(s.CWSeries.series_id, item_code, item_name, db)
        if metric:
            areas.append(AreaComparisonMetric(
                area_code=s.CWSeries.area_code,
                area_name=s.area_name or s.CWSeries.area_code,
                area_type=_get_area_type(s.CWSeries.area_code),
                series_id=s.CWSeries.series_id,
                latest_value=metric.latest_value,
                latest_date=metric.latest_date,
                month_over_month=metric.month_over_month,
                year_over_year=metric.year_over_year
            ))

    # Sort by area code
    areas.sort(key=lambda x: x.area_code)

    return CWAreaComparisonResponse(
        item_code=item_code,
        item_name=item_name,
        areas=areas
    )


# =============================================================================
# TOP MOVERS
# =============================================================================

@router.get("/top-movers", response_model=CWTopMoversResponse)
async def get_top_movers(
    period: str = Query("yoy", description="Period: 'mom' or 'yoy'"),
    area_code: str = Query("0000", description="Area code"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get items with largest CPI-W changes"""

    # Get all series for this area (major items only - display_level 0 or 1)
    series_list = db.query(
        CWSeries,
        CWItem.item_name,
        CWItem.display_level
    ).join(
        CWItem, CWSeries.item_code == CWItem.item_code
    ).filter(
        CWSeries.area_code == area_code,
        CWSeries.seasonal_code == 'U',
        CWItem.display_level.in_([0, 1])
    ).all()

    latest_date = None
    all_movers = []

    for s in series_list:
        data = db.query(CWData).filter(
            CWData.series_id == s.CWSeries.series_id,
            CWData.period.like('M%'),
            CWData.period != 'M13'
        ).order_by(desc(CWData.year), desc(CWData.period)).limit(14).all()

        if len(data) < 2:
            continue

        latest = data[0]
        if not latest_date:
            latest_date = _get_period_name(latest.year, latest.period, db)

        latest_value = float(latest.value) if latest.value else None
        if not latest_value:
            continue

        if period == "mom":
            prev = data[1]
        else:  # yoy
            prev = None
            for d in data:
                if d.year == latest.year - 1 and d.period == latest.period:
                    prev = d
                    break

        if not prev or not prev.value:
            continue

        prev_value = float(prev.value)
        if prev_value == 0:
            continue

        change = latest_value - prev_value
        pct_change = round(((latest_value - prev_value) / prev_value) * 100, 2)

        all_movers.append(CWTopMover(
            series_id=s.CWSeries.series_id,
            item_code=s.CWSeries.item_code,
            item_name=s.item_name,
            area_name="U.S. city average" if area_code == "0000" else None,
            latest_value=latest_value,
            change=round(change, 3),
            pct_change=pct_change,
            direction="up" if pct_change > 0 else "down"
        ))

    # Sort and split
    all_movers.sort(key=lambda x: x.pct_change, reverse=True)
    gainers = [m for m in all_movers if m.pct_change > 0][:limit]
    losers = [m for m in all_movers if m.pct_change < 0]
    losers.sort(key=lambda x: x.pct_change)
    losers = losers[:limit]

    return CWTopMoversResponse(
        period=period,
        latest_date=latest_date,
        gainers=gainers,
        losers=losers
    )
