"""
SU (Chained CPI - All Urban Consumers) Survey Explorer API

Endpoints for exploring Chained Consumer Price Index data.
The C-CPI-U uses a Tornqvist formula to account for consumer substitution.

Key Features:
- Only U.S. city average data (no regional breakdown)
- 29 expenditure categories in hierarchical structure
- Base period: December 1999 = 100
- Monthly data from December 1999 to present
- Not seasonally adjusted
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, select
from typing import Optional, List
from decimal import Decimal

from ....database import get_data_db
from ....api.auth import get_current_user
from .su_schemas import (
    SUDimensions, SUAreaItem, SUItemItem,
    SUSeriesInfo, SUSeriesListResponse,
    SUDataPoint, SUSeriesData, SUDataResponse,
    SUCategoryMetric, SUOverviewResponse, SUOverviewTimelinePoint, SUOverviewTimelineResponse,
    SUSubcategoryMetric, SUCategoryAnalysisResponse, SUCategoryTimelinePoint, SUCategoryTimelineResponse,
    SUComparisonMetric, SUComparisonResponse, SUComparisonTimelinePoint, SUComparisonTimelineResponse,
    SUTopMover, SUTopMoversResponse,
    SUInflationPoint, SUInflationResponse,
    SUYoYComparisonPoint, SUYoYComparisonResponse
)
from ....data_models.bls_models import SUArea, SUItem, SUSeries, SUData, BLSPeriod

router = APIRouter(
    prefix="/api/research/bls/su",
    tags=["BLS SU - Chained CPI (All Urban Consumers)"]
)

# Key item codes for overview
KEY_ITEMS = {
    'SA0': 'All items',
    'SA0L1E': 'All items less food and energy',
    'SAF': 'Food and beverages',
    'SA0E': 'Energy',
    'SAH': 'Housing',
    'SAT': 'Transportation',
    'SAM': 'Medical care',
}

# Period mapping
PERIOD_NAMES = {
    'M01': 'January', 'M02': 'February', 'M03': 'March', 'M04': 'April',
    'M05': 'May', 'M06': 'June', 'M07': 'July', 'M08': 'August',
    'M09': 'September', 'M10': 'October', 'M11': 'November', 'M12': 'December',
    'M13': 'Annual Average'
}


def decimal_to_float(val) -> Optional[float]:
    """Convert Decimal to float safely"""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    return float(val)


def get_period_name(year: int, period: str) -> str:
    """Get human-readable period name"""
    month_name = PERIOD_NAMES.get(period, period)
    return f"{month_name} {year}"


def build_series_id(item_code: str, area_code: str = '0000') -> str:
    """Build SU series ID from components"""
    return f"SUUR{area_code}{item_code}"


# ==================== Dimensions ====================

@router.get("/dimensions", response_model=SUDimensions)
async def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get available dimensions for SU survey filtering"""

    # Get areas (only U.S. city average for SU)
    areas = db.execute(
        select(SUArea).order_by(SUArea.area_code)
    ).scalars().all()

    area_items = [
        SUAreaItem(
            area_code=a.area_code,
            area_name=a.area_name,
            display_level=a.display_level,
            selectable=a.selectable
        )
        for a in areas
    ]

    # Get items with hierarchy
    items = db.execute(
        select(SUItem).order_by(SUItem.sort_sequence, SUItem.item_code)
    ).scalars().all()

    item_items = [
        SUItemItem(
            item_code=i.item_code,
            item_name=i.item_name,
            display_level=i.display_level,
            selectable=i.selectable,
            sort_sequence=i.sort_sequence
        )
        for i in items
    ]

    return SUDimensions(areas=area_items, items=item_items)


# ==================== Series ====================

@router.get("/series", response_model=SUSeriesListResponse)
async def get_series(
    item_code: Optional[str] = Query(None, description="Filter by item code"),
    search: Optional[str] = Query(None, description="Search series title/item name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get SU series with optional filters"""

    # Build query
    query = select(SUSeries).where(SUSeries.is_active == True)

    if item_code:
        query = query.where(SUSeries.item_code == item_code)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(SUSeries.series_title.ilike(search_pattern))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Get series with pagination
    query = query.order_by(SUSeries.series_id).offset(offset).limit(limit)
    series_list = db.execute(query).scalars().all()

    # Get item names for response
    item_codes = list(set(s.item_code for s in series_list if s.item_code))
    item_map = {}
    if item_codes:
        items = db.execute(
            select(SUItem).where(SUItem.item_code.in_(item_codes))
        ).scalars().all()
        item_map = {i.item_code: i.item_name for i in items}

    # Get area names
    area_codes = list(set(s.area_code for s in series_list if s.area_code))
    area_map = {}
    if area_codes:
        areas = db.execute(
            select(SUArea).where(SUArea.area_code.in_(area_codes))
        ).scalars().all()
        area_map = {a.area_code: a.area_name for a in areas}

    series_info = [
        SUSeriesInfo(
            series_id=s.series_id,
            area_code=s.area_code,
            area_name=area_map.get(s.area_code),
            item_code=s.item_code,
            item_name=item_map.get(s.item_code),
            seasonal_code=s.seasonal_code,
            periodicity_code=s.periodicity_code,
            base_code=s.base_code,
            base_period=s.base_period,
            series_title=s.series_title,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active
        )
        for s in series_list
    ]

    return SUSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_info
    )


@router.get("/series/{series_id}", response_model=SUSeriesInfo)
async def get_series_by_id(
    series_id: str,
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get a specific series by ID"""

    series = db.execute(
        select(SUSeries).where(SUSeries.series_id == series_id)
    ).scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    # Get item name
    item = db.execute(
        select(SUItem).where(SUItem.item_code == series.item_code)
    ).scalar_one_or_none()

    # Get area name
    area = db.execute(
        select(SUArea).where(SUArea.area_code == series.area_code)
    ).scalar_one_or_none()

    return SUSeriesInfo(
        series_id=series.series_id,
        area_code=series.area_code,
        area_name=area.area_name if area else None,
        item_code=series.item_code,
        item_name=item.item_name if item else None,
        seasonal_code=series.seasonal_code,
        periodicity_code=series.periodicity_code,
        base_code=series.base_code,
        base_period=series.base_period,
        series_title=series.series_title,
        begin_year=series.begin_year,
        begin_period=series.begin_period,
        end_year=series.end_year,
        end_period=series.end_period,
        is_active=series.is_active
    )


# ==================== Data ====================

@router.get("/data", response_model=SUDataResponse)
async def get_data(
    series_ids: str = Query(..., description="Comma-separated series IDs"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get time series data for specified series"""

    series_id_list = [s.strip() for s in series_ids.split(',') if s.strip()]

    if not series_id_list:
        raise HTTPException(status_code=400, detail="At least one series ID required")

    if len(series_id_list) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 series IDs allowed")

    # Build data query
    query = select(SUData).where(SUData.series_id.in_(series_id_list))

    if start_year:
        query = query.where(SUData.year >= start_year)
    if end_year:
        query = query.where(SUData.year <= end_year)

    query = query.order_by(SUData.series_id, SUData.year, SUData.period)
    data_rows = db.execute(query).scalars().all()

    # Get series metadata
    series_list = db.execute(
        select(SUSeries).where(SUSeries.series_id.in_(series_id_list))
    ).scalars().all()

    # Get item/area maps
    item_codes = list(set(s.item_code for s in series_list if s.item_code))
    area_codes = list(set(s.area_code for s in series_list if s.area_code))

    item_map = {}
    if item_codes:
        items = db.execute(select(SUItem).where(SUItem.item_code.in_(item_codes))).scalars().all()
        item_map = {i.item_code: i.item_name for i in items}

    area_map = {}
    if area_codes:
        areas = db.execute(select(SUArea).where(SUArea.area_code.in_(area_codes))).scalars().all()
        area_map = {a.area_code: a.area_name for a in areas}

    series_map = {s.series_id: s for s in series_list}

    # Group data by series
    data_by_series = {}
    for d in data_rows:
        if d.series_id not in data_by_series:
            data_by_series[d.series_id] = []
        data_by_series[d.series_id].append(d)

    result = []
    for sid in series_id_list:
        s = series_map.get(sid)
        if not s:
            continue

        series_info = SUSeriesInfo(
            series_id=s.series_id,
            area_code=s.area_code,
            area_name=area_map.get(s.area_code),
            item_code=s.item_code,
            item_name=item_map.get(s.item_code),
            seasonal_code=s.seasonal_code,
            periodicity_code=s.periodicity_code,
            base_code=s.base_code,
            base_period=s.base_period,
            series_title=s.series_title,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active
        )

        data_points = [
            SUDataPoint(
                year=d.year,
                period=d.period,
                period_name=get_period_name(d.year, d.period),
                value=decimal_to_float(d.value),
                footnote_codes=d.footnote_codes
            )
            for d in data_by_series.get(sid, [])
        ]

        result.append(SUSeriesData(
            series_id=sid,
            series_info=series_info,
            data=data_points
        ))

    return SUDataResponse(series=result)


# ==================== Overview ====================

@router.get("/overview", response_model=SUOverviewResponse)
async def get_overview(
    year: Optional[int] = Query(None, description="Year (default: latest)"),
    period: Optional[str] = Query(None, description="Period (default: latest)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get overview of Chained CPI with key metrics"""

    # Determine year/period
    if not year or not period:
        latest = db.execute(
            select(SUData.year, SUData.period)
            .where(SUData.period != 'M13')
            .order_by(desc(SUData.year), desc(SUData.period))
            .limit(1)
        ).first()
        if latest:
            year = year or latest.year
            period = period or latest.period
        else:
            year = year or 2024
            period = period or 'M01'

    period_name = get_period_name(year, period)

    # Get all items
    items = db.execute(
        select(SUItem).order_by(SUItem.sort_sequence, SUItem.item_code)
    ).scalars().all()

    item_map = {i.item_code: i for i in items}

    # Get all series
    series_list = db.execute(
        select(SUSeries).where(SUSeries.is_active == True)
    ).scalars().all()

    series_map = {s.item_code: s for s in series_list}

    # Batch query: Get current period data for all series
    series_ids = [s.series_id for s in series_list]
    current_data = db.execute(
        select(SUData)
        .where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year,
            SUData.period == period
        ))
    ).scalars().all()
    current_map = {d.series_id: d for d in current_data}

    # Batch query: Get previous month data
    prev_year, prev_period = year, period
    period_num = int(period[1:]) if period.startswith('M') else 1
    if period_num == 1:
        prev_year = year - 1
        prev_period = 'M12'
    else:
        prev_period = f"M{period_num - 1:02d}"

    prev_month_data = db.execute(
        select(SUData)
        .where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == prev_year,
            SUData.period == prev_period
        ))
    ).scalars().all()
    prev_month_map = {d.series_id: d for d in prev_month_data}

    # Batch query: Get same period last year data
    prev_year_data = db.execute(
        select(SUData)
        .where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year - 1,
            SUData.period == period
        ))
    ).scalars().all()
    prev_year_map = {d.series_id: d for d in prev_year_data}

    def build_metric(item_code: str) -> Optional[SUCategoryMetric]:
        item = item_map.get(item_code)
        series = series_map.get(item_code)
        if not item or not series:
            return None

        current = current_map.get(series.series_id)
        prev_month = prev_month_map.get(series.series_id)
        prev_year_val = prev_year_map.get(series.series_id)

        latest_value = decimal_to_float(current.value) if current else None

        mom_pct = None
        if current and prev_month and current.value and prev_month.value:
            pv = float(prev_month.value)
            cv = float(current.value)
            if pv != 0:
                mom_pct = round((cv - pv) / pv * 100, 2)

        yoy_pct = None
        if current and prev_year_val and current.value and prev_year_val.value:
            pv = float(prev_year_val.value)
            cv = float(current.value)
            if pv != 0:
                yoy_pct = round((cv - pv) / pv * 100, 2)

        return SUCategoryMetric(
            item_code=item_code,
            item_name=item.item_name,
            display_level=item.display_level,
            series_id=series.series_id,
            latest_value=latest_value,
            latest_date=period_name,
            month_over_month=round(float(current.value) - float(prev_month.value), 3) if current and prev_month and current.value and prev_month.value else None,
            month_over_month_pct=mom_pct,
            year_over_year=round(float(current.value) - float(prev_year_val.value), 3) if current and prev_year_val and current.value and prev_year_val.value else None,
            year_over_year_pct=yoy_pct
        )

    # Build all category metrics
    categories = []
    for item in items:
        metric = build_metric(item.item_code)
        if metric:
            categories.append(metric)

    return SUOverviewResponse(
        year=year,
        period=period,
        period_name=period_name,
        all_items=build_metric('SA0'),
        core_items=build_metric('SA0L1E'),
        food=build_metric('SAF'),
        energy=build_metric('SA0E'),
        housing=build_metric('SAH'),
        transportation=build_metric('SAT'),
        medical_care=build_metric('SAM'),
        categories=categories
    )


@router.get("/overview/timeline", response_model=SUOverviewTimelineResponse)
async def get_overview_timeline(
    item_codes: Optional[str] = Query(None, description="Comma-separated item codes (default: key items)"),
    start_year: Optional[int] = Query(None, description="Start year"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for overview - multiple items over time"""

    # Determine items to track
    if item_codes:
        codes = [c.strip() for c in item_codes.split(',')]
    else:
        codes = list(KEY_ITEMS.keys())

    # Get end year
    end_year = db.execute(select(func.max(SUData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    # Get items
    items = db.execute(
        select(SUItem).where(SUItem.item_code.in_(codes))
    ).scalars().all()
    item_names = {i.item_code: i.item_name for i in items}

    # Get series for items
    series_list = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code.in_(codes),
            SUSeries.is_active == True
        ))
    ).scalars().all()

    series_map = {s.item_code: s.series_id for s in series_list}
    series_ids = list(series_map.values())

    # Batch query all data
    data_rows = db.execute(
        select(SUData)
        .where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year >= start_year,
            SUData.year <= end_year,
            SUData.period != 'M13'
        ))
        .order_by(SUData.year, SUData.period)
    ).scalars().all()

    # Organize by year/period
    timeline_data = {}
    for d in data_rows:
        key = (d.year, d.period)
        if key not in timeline_data:
            timeline_data[key] = {}
        # Find item_code from series_id
        for item_code, sid in series_map.items():
            if sid == d.series_id:
                timeline_data[key][item_code] = decimal_to_float(d.value)
                break

    timeline = [
        SUOverviewTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            items=values
        )
        for (year, period), values in sorted(timeline_data.items())
    ]

    return SUOverviewTimelineResponse(
        timeline=timeline,
        item_names=item_names
    )


# ==================== Category Analysis ====================

@router.get("/category/{item_code}", response_model=SUCategoryAnalysisResponse)
async def get_category_analysis(
    item_code: str,
    year: Optional[int] = Query(None, description="Year (default: latest)"),
    period: Optional[str] = Query(None, description="Period (default: latest)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get detailed analysis for a category and its subcategories"""

    # Get the main item
    main_item = db.execute(
        select(SUItem).where(SUItem.item_code == item_code)
    ).scalar_one_or_none()

    if not main_item:
        raise HTTPException(status_code=404, detail=f"Item {item_code} not found")

    # Determine year/period
    if not year or not period:
        latest = db.execute(
            select(SUData.year, SUData.period)
            .where(SUData.period != 'M13')
            .order_by(desc(SUData.year), desc(SUData.period))
            .limit(1)
        ).first()
        if latest:
            year = year or latest.year
            period = period or latest.period
        else:
            year = year or 2024
            period = period or 'M01'

    period_name = get_period_name(year, period)

    # Get all items to find subcategories
    all_items = db.execute(
        select(SUItem).order_by(SUItem.sort_sequence)
    ).scalars().all()

    # Find subcategories (items that come after this one with higher display_level until next same-level item)
    main_level = main_item.display_level or 0
    main_seq = main_item.sort_sequence or 0

    subcategory_codes = []
    found_main = False
    for item in all_items:
        if item.item_code == item_code:
            found_main = True
            continue
        if found_main:
            item_level = item.display_level or 0
            if item_level <= main_level:
                break  # Reached next same-level or higher item
            if item_level == main_level + 1:
                subcategory_codes.append(item.item_code)

    # Include main item
    all_codes = [item_code] + subcategory_codes

    item_map = {i.item_code: i for i in all_items if i.item_code in all_codes}

    # Get series
    series_list = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code.in_(all_codes),
            SUSeries.is_active == True
        ))
    ).scalars().all()

    series_map = {s.item_code: s for s in series_list}
    series_ids = [s.series_id for s in series_list]

    # Batch query current data
    current_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year,
            SUData.period == period
        ))
    ).scalars().all()
    current_map = {d.series_id: d for d in current_data}

    # Previous month
    prev_year, prev_period = year, period
    period_num = int(period[1:]) if period.startswith('M') else 1
    if period_num == 1:
        prev_year = year - 1
        prev_period = 'M12'
    else:
        prev_period = f"M{period_num - 1:02d}"

    prev_month_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == prev_year,
            SUData.period == prev_period
        ))
    ).scalars().all()
    prev_month_map = {d.series_id: d for d in prev_month_data}

    # Same period last year
    prev_year_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year - 1,
            SUData.period == period
        ))
    ).scalars().all()
    prev_year_map = {d.series_id: d for d in prev_year_data}

    def calc_pct(current_val, prev_val):
        if current_val is None or prev_val is None:
            return None
        cv = float(current_val)
        pv = float(prev_val)
        if pv == 0:
            return None
        return round((cv - pv) / pv * 100, 2)

    # Build main metric
    main_series = series_map.get(item_code)
    main_metric = None
    if main_series:
        current = current_map.get(main_series.series_id)
        prev_month = prev_month_map.get(main_series.series_id)
        prev_yr = prev_year_map.get(main_series.series_id)

        main_metric = SUCategoryMetric(
            item_code=item_code,
            item_name=main_item.item_name,
            display_level=main_item.display_level,
            series_id=main_series.series_id,
            latest_value=decimal_to_float(current.value) if current else None,
            latest_date=period_name,
            month_over_month=round(float(current.value) - float(prev_month.value), 3) if current and prev_month and current.value and prev_month.value else None,
            month_over_month_pct=calc_pct(current.value if current else None, prev_month.value if prev_month else None),
            year_over_year=round(float(current.value) - float(prev_yr.value), 3) if current and prev_yr and current.value and prev_yr.value else None,
            year_over_year_pct=calc_pct(current.value if current else None, prev_yr.value if prev_yr else None)
        )

    # Build subcategory metrics
    subcategories = []
    for code in subcategory_codes:
        item = item_map.get(code)
        series = series_map.get(code)
        if not item or not series:
            continue

        current = current_map.get(series.series_id)
        prev_month = prev_month_map.get(series.series_id)
        prev_yr = prev_year_map.get(series.series_id)

        subcategories.append(SUSubcategoryMetric(
            item_code=code,
            item_name=item.item_name,
            display_level=item.display_level,
            series_id=series.series_id,
            latest_value=decimal_to_float(current.value) if current else None,
            latest_date=period_name,
            month_over_month_pct=calc_pct(current.value if current else None, prev_month.value if prev_month else None),
            year_over_year_pct=calc_pct(current.value if current else None, prev_yr.value if prev_yr else None)
        ))

    return SUCategoryAnalysisResponse(
        item_code=item_code,
        item_name=main_item.item_name,
        year=year,
        period=period,
        period_name=period_name,
        main_metric=main_metric,
        subcategories=subcategories
    )


@router.get("/category/{item_code}/timeline", response_model=SUCategoryTimelineResponse)
async def get_category_timeline(
    item_code: str,
    start_year: Optional[int] = Query(None, description="Start year"),
    include_subcategories: bool = Query(True, description="Include subcategories"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for a category"""

    main_item = db.execute(
        select(SUItem).where(SUItem.item_code == item_code)
    ).scalar_one_or_none()

    if not main_item:
        raise HTTPException(status_code=404, detail=f"Item {item_code} not found")

    end_year = db.execute(select(func.max(SUData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    # Get all items
    all_items = db.execute(
        select(SUItem).order_by(SUItem.sort_sequence)
    ).scalars().all()

    # Find subcategories
    codes = [item_code]
    if include_subcategories:
        main_level = main_item.display_level or 0
        found_main = False
        for item in all_items:
            if item.item_code == item_code:
                found_main = True
                continue
            if found_main:
                item_level = item.display_level or 0
                if item_level <= main_level:
                    break
                if item_level == main_level + 1:
                    codes.append(item.item_code)

    item_names = {i.item_code: i.item_name for i in all_items if i.item_code in codes}

    # Get series
    series_list = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code.in_(codes),
            SUSeries.is_active == True
        ))
    ).scalars().all()

    series_map = {s.item_code: s.series_id for s in series_list}
    series_ids = list(series_map.values())

    # Query data
    data_rows = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year >= start_year,
            SUData.year <= end_year,
            SUData.period != 'M13'
        ))
        .order_by(SUData.year, SUData.period)
    ).scalars().all()

    # Organize
    timeline_data = {}
    for d in data_rows:
        key = (d.year, d.period)
        if key not in timeline_data:
            timeline_data[key] = {}
        for ic, sid in series_map.items():
            if sid == d.series_id:
                timeline_data[key][ic] = decimal_to_float(d.value)
                break

    timeline = [
        SUCategoryTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            items=values
        )
        for (year, period), values in sorted(timeline_data.items())
    ]

    return SUCategoryTimelineResponse(
        item_code=item_code,
        item_name=main_item.item_name,
        timeline=timeline,
        item_names=item_names
    )


# ==================== Comparison ====================

@router.get("/comparison", response_model=SUComparisonResponse)
async def get_comparison(
    item_codes: str = Query(..., description="Comma-separated item codes"),
    year: Optional[int] = Query(None, description="Year (default: latest)"),
    period: Optional[str] = Query(None, description="Period (default: latest)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Compare multiple items at a point in time"""

    codes = [c.strip() for c in item_codes.split(',') if c.strip()]

    if not codes:
        raise HTTPException(status_code=400, detail="At least one item code required")

    if len(codes) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 item codes allowed")

    # Determine year/period
    if not year or not period:
        latest = db.execute(
            select(SUData.year, SUData.period)
            .where(SUData.period != 'M13')
            .order_by(desc(SUData.year), desc(SUData.period))
            .limit(1)
        ).first()
        if latest:
            year = year or latest.year
            period = period or latest.period
        else:
            year = year or 2024
            period = period or 'M01'

    period_name = get_period_name(year, period)

    # Get items
    items = db.execute(
        select(SUItem).where(SUItem.item_code.in_(codes))
    ).scalars().all()
    item_map = {i.item_code: i for i in items}

    # Get series
    series_list = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code.in_(codes),
            SUSeries.is_active == True
        ))
    ).scalars().all()
    series_map = {s.item_code: s for s in series_list}
    series_ids = [s.series_id for s in series_list]

    # Current data
    current_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year,
            SUData.period == period
        ))
    ).scalars().all()
    current_map = {d.series_id: d for d in current_data}

    # Previous year data
    prev_year_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year - 1,
            SUData.period == period
        ))
    ).scalars().all()
    prev_year_map = {d.series_id: d for d in prev_year_data}

    items_result = []
    for code in codes:
        item = item_map.get(code)
        series = series_map.get(code)
        if not item or not series:
            continue

        current = current_map.get(series.series_id)
        prev_yr = prev_year_map.get(series.series_id)

        yoy_pct = None
        if current and prev_yr and current.value and prev_yr.value:
            pv = float(prev_yr.value)
            cv = float(current.value)
            if pv != 0:
                yoy_pct = round((cv - pv) / pv * 100, 2)

        items_result.append(SUComparisonMetric(
            item_code=code,
            item_name=item.item_name,
            series_id=series.series_id,
            value=decimal_to_float(current.value) if current else None,
            year_over_year_pct=yoy_pct
        ))

    return SUComparisonResponse(
        year=year,
        period=period,
        period_name=period_name,
        items=items_result
    )


@router.get("/comparison/timeline", response_model=SUComparisonTimelineResponse)
async def get_comparison_timeline(
    item_codes: str = Query(..., description="Comma-separated item codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for comparing multiple items"""

    codes = [c.strip() for c in item_codes.split(',') if c.strip()]

    if not codes:
        raise HTTPException(status_code=400, detail="At least one item code required")

    if len(codes) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 item codes for timeline")

    end_year = db.execute(select(func.max(SUData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    # Get items
    items = db.execute(
        select(SUItem).where(SUItem.item_code.in_(codes))
    ).scalars().all()
    item_names = {i.item_code: i.item_name for i in items}

    # Get series
    series_list = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code.in_(codes),
            SUSeries.is_active == True
        ))
    ).scalars().all()
    series_map = {s.item_code: s.series_id for s in series_list}
    series_ids = list(series_map.values())

    # Query data
    data_rows = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year >= start_year,
            SUData.year <= end_year,
            SUData.period != 'M13'
        ))
        .order_by(SUData.year, SUData.period)
    ).scalars().all()

    # Organize
    timeline_data = {}
    for d in data_rows:
        key = (d.year, d.period)
        if key not in timeline_data:
            timeline_data[key] = {}
        for ic, sid in series_map.items():
            if sid == d.series_id:
                timeline_data[key][ic] = decimal_to_float(d.value)
                break

    timeline = [
        SUComparisonTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            items=values
        )
        for (year, period), values in sorted(timeline_data.items())
    ]

    return SUComparisonTimelineResponse(
        item_codes=codes,
        timeline=timeline,
        item_names=item_names
    )


# ==================== Top Movers ====================

@router.get("/top-movers", response_model=SUTopMoversResponse)
async def get_top_movers(
    change_type: str = Query('year_over_year', description="'month_over_month' or 'year_over_year'"),
    direction: str = Query('highest', description="'highest' or 'lowest'"),
    limit: int = Query(10, ge=1, le=29),
    year: Optional[int] = Query(None, description="Year (default: latest)"),
    period: Optional[str] = Query(None, description="Period (default: latest)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get top/bottom movers by price change"""

    if change_type not in ('month_over_month', 'year_over_year'):
        raise HTTPException(status_code=400, detail="change_type must be 'month_over_month' or 'year_over_year'")
    if direction not in ('highest', 'lowest'):
        raise HTTPException(status_code=400, detail="direction must be 'highest' or 'lowest'")

    # Determine year/period
    if not year or not period:
        latest = db.execute(
            select(SUData.year, SUData.period)
            .where(SUData.period != 'M13')
            .order_by(desc(SUData.year), desc(SUData.period))
            .limit(1)
        ).first()
        if latest:
            year = year or latest.year
            period = period or latest.period
        else:
            year = year or 2024
            period = period or 'M01'

    period_name = get_period_name(year, period)

    # Get all items and series
    items = db.execute(select(SUItem)).scalars().all()
    item_map = {i.item_code: i for i in items}

    series_list = db.execute(
        select(SUSeries).where(SUSeries.is_active == True)
    ).scalars().all()
    series_map = {s.item_code: s for s in series_list}
    series_ids = [s.series_id for s in series_list]

    # Current data
    current_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == year,
            SUData.period == period
        ))
    ).scalars().all()
    current_map = {d.series_id: d for d in current_data}

    # Comparison period
    if change_type == 'month_over_month':
        period_num = int(period[1:]) if period.startswith('M') else 1
        if period_num == 1:
            comp_year = year - 1
            comp_period = 'M12'
        else:
            comp_year = year
            comp_period = f"M{period_num - 1:02d}"
    else:  # year_over_year
        comp_year = year - 1
        comp_period = period

    comp_data = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year == comp_year,
            SUData.period == comp_period
        ))
    ).scalars().all()
    comp_map = {d.series_id: d for d in comp_data}

    # Calculate changes
    changes = []
    for s in series_list:
        current = current_map.get(s.series_id)
        comp = comp_map.get(s.series_id)

        if not current or not comp or not current.value or not comp.value:
            continue

        cv = float(current.value)
        pv = float(comp.value)
        if pv == 0:
            continue

        pct = (cv - pv) / pv * 100

        item = item_map.get(s.item_code)
        if item:
            changes.append({
                'item_code': s.item_code,
                'item_name': item.item_name,
                'series_id': s.series_id,
                'latest_value': cv,
                'change_pct': pct
            })

    # Sort
    changes.sort(key=lambda x: x['change_pct'], reverse=(direction == 'highest'))

    movers = [
        SUTopMover(
            rank=i + 1,
            item_code=c['item_code'],
            item_name=c['item_name'],
            series_id=c['series_id'],
            latest_value=round(c['latest_value'], 3),
            change_pct=round(c['change_pct'], 2)
        )
        for i, c in enumerate(changes[:limit])
    ]

    return SUTopMoversResponse(
        year=year,
        period=period,
        period_name=period_name,
        change_type=change_type,
        direction=direction,
        movers=movers
    )


# ==================== Inflation Analysis ====================

@router.get("/inflation/{item_code}", response_model=SUInflationResponse)
async def get_inflation_analysis(
    item_code: str,
    start_year: Optional[int] = Query(None, description="Start year"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get inflation analysis for an item - index, MoM%, and YoY% over time"""

    item = db.execute(
        select(SUItem).where(SUItem.item_code == item_code)
    ).scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_code} not found")

    series = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code == item_code,
            SUSeries.is_active == True
        ))
    ).scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail=f"No series found for item {item_code}")

    end_year = db.execute(select(func.max(SUData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 9

    # Get all data for the series
    data_rows = db.execute(
        select(SUData).where(and_(
            SUData.series_id == series.series_id,
            SUData.year >= start_year - 1,  # Need previous year for YoY
            SUData.year <= end_year,
            SUData.period != 'M13'
        ))
        .order_by(SUData.year, SUData.period)
    ).scalars().all()

    # Build lookup
    data_map = {}
    for d in data_rows:
        data_map[(d.year, d.period)] = decimal_to_float(d.value)

    # Calculate metrics
    result_data = []
    for d in data_rows:
        if d.year < start_year:
            continue

        cv = decimal_to_float(d.value)

        # MoM
        period_num = int(d.period[1:]) if d.period.startswith('M') else 1
        if period_num == 1:
            prev_key = (d.year - 1, 'M12')
        else:
            prev_key = (d.year, f"M{period_num - 1:02d}")

        pv_mom = data_map.get(prev_key)
        mom_pct = None
        if cv and pv_mom and pv_mom != 0:
            mom_pct = round((cv - pv_mom) / pv_mom * 100, 2)

        # YoY
        yoy_key = (d.year - 1, d.period)
        pv_yoy = data_map.get(yoy_key)
        yoy_pct = None
        if cv and pv_yoy and pv_yoy != 0:
            yoy_pct = round((cv - pv_yoy) / pv_yoy * 100, 2)

        result_data.append(SUInflationPoint(
            year=d.year,
            period=d.period,
            period_name=get_period_name(d.year, d.period),
            index_value=cv,
            month_over_month_pct=mom_pct,
            year_over_year_pct=yoy_pct
        ))

    return SUInflationResponse(
        item_code=item_code,
        item_name=item.item_name,
        base_period=series.base_period or "December 1999=100",
        data=result_data
    )


# ==================== YoY Comparison ====================

@router.get("/yoy-comparison", response_model=SUYoYComparisonResponse)
async def get_yoy_comparison(
    item_codes: Optional[str] = Query(None, description="Comma-separated item codes (default: key items)"),
    start_year: Optional[int] = Query(None, description="Start year"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get year-over-year inflation comparison for multiple items"""

    if item_codes:
        codes = [c.strip() for c in item_codes.split(',')]
    else:
        codes = list(KEY_ITEMS.keys())

    end_year = db.execute(select(func.max(SUData.year))).scalar() or 2024
    if not start_year:
        start_year = end_year - 4

    # Get items
    items = db.execute(
        select(SUItem).where(SUItem.item_code.in_(codes))
    ).scalars().all()
    item_names = {i.item_code: i.item_name for i in items}

    # Get series
    series_list = db.execute(
        select(SUSeries).where(and_(
            SUSeries.item_code.in_(codes),
            SUSeries.is_active == True
        ))
    ).scalars().all()
    series_map = {s.item_code: s.series_id for s in series_list}
    series_ids = list(series_map.values())

    # Get data including previous year for YoY calculation
    data_rows = db.execute(
        select(SUData).where(and_(
            SUData.series_id.in_(series_ids),
            SUData.year >= start_year - 1,
            SUData.year <= end_year,
            SUData.period != 'M13'
        ))
        .order_by(SUData.year, SUData.period)
    ).scalars().all()

    # Build lookup
    data_map = {}
    for d in data_rows:
        for ic, sid in series_map.items():
            if sid == d.series_id:
                data_map[(ic, d.year, d.period)] = decimal_to_float(d.value)
                break

    # Calculate YoY for each period
    timeline_data = {}
    periods_seen = set()
    for d in data_rows:
        if d.year < start_year:
            continue

        key = (d.year, d.period)
        if key not in timeline_data:
            timeline_data[key] = {}
            periods_seen.add(key)

        for ic, sid in series_map.items():
            if sid != d.series_id:
                continue

            cv = data_map.get((ic, d.year, d.period))
            pv = data_map.get((ic, d.year - 1, d.period))

            if cv and pv and pv != 0:
                timeline_data[key][ic] = round((cv - pv) / pv * 100, 2)
            else:
                timeline_data[key][ic] = None

    timeline = [
        SUYoYComparisonPoint(
            year=year,
            period=period,
            period_name=get_period_name(year, period),
            items=values
        )
        for (year, period), values in sorted(timeline_data.items())
    ]

    return SUYoYComparisonResponse(
        timeline=timeline,
        item_names=item_names
    )
