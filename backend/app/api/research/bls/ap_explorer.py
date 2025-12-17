"""
AP (Average Price) Survey Explorer API

Endpoints for exploring Average Price data for household fuel, motor fuel, and food items.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List

from ....database import get_data_db
from ....api.auth import get_current_user
from .ap_schemas import (
    APDimensions, APAreaItem, APItemInfo,
    APSeriesInfo, APSeriesListResponse,
    APDataPoint, APSeriesData, APDataResponse,
    APPriceMetric, APCategoryOverview, APOverviewResponse,
    APAreaMetric, APAreaComparisonResponse,
    APItemMetric, APItemsAnalysisResponse,
    APTopMover, APTopMoversResponse,
    APTimelinePoint, APItemTimelineResponse
)
from ....data_models.bls_models import (
    APItem, APSeries, APData, BLSArea, BLSPeriod
)

router = APIRouter(
    prefix="/api/research/bls/ap",
    tags=["BLS AP - Average Price"]
)


# Category classification based on item codes
def _get_category(item_code: str) -> str:
    """Determine category from item code"""
    if not item_code:
        return "Other"

    # Gasoline items start with 74
    if item_code.startswith('74'):
        return "Gasoline"

    # Household fuels - electricity, gas, fuel oil
    if item_code.startswith('72'):  # Electricity
        return "Household Fuels"
    if item_code.startswith('71'):  # Natural gas / fuel oil
        return "Household Fuels"

    # Food items (70xxxx range typically)
    if item_code.startswith('70'):
        return "Food"

    return "Other"


def _get_area_type(area_code: str) -> str:
    """Determine area type from area code"""
    if not area_code:
        return "unknown"

    if area_code == "0000":
        return "national"
    if area_code.startswith("0") and len(area_code) == 4:
        return "region"
    if area_code.startswith("S") and area_code[1:3].isdigit():
        return "metro"
    if area_code.startswith(("A", "B", "C", "D", "N")):
        return "size_class"

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
        'M13': 'Annual Average'
    }
    return f"{month_map.get(period, period)} {year}"


def _calculate_price_metrics(series_id: str, item_code: str, item_name: str,
                             area_code: str, area_name: str, unit: str,
                             db: Session) -> Optional[APPriceMetric]:
    """Calculate price metrics for a series"""
    data = db.query(APData).filter(
        APData.series_id == series_id,
        APData.period != 'M13'
    ).order_by(desc(APData.year), desc(APData.period)).limit(14).all()

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

    latest_price = float(latest.value) if latest.value else None
    prev_month_price = float(prev_month.value) if prev_month and prev_month.value else None
    prev_year_price = float(prev_year.value) if prev_year and prev_year.value else None

    mom_change = None
    mom_pct = None
    yoy_change = None
    yoy_pct = None

    if latest_price and prev_month_price:
        mom_change = round(latest_price - prev_month_price, 3)
        mom_pct = round((mom_change / prev_month_price) * 100, 2) if prev_month_price != 0 else None

    if latest_price and prev_year_price:
        yoy_change = round(latest_price - prev_year_price, 3)
        yoy_pct = round((yoy_change / prev_year_price) * 100, 2) if prev_year_price != 0 else None

    return APPriceMetric(
        series_id=series_id,
        item_code=item_code,
        item_name=item_name,
        area_code=area_code,
        area_name=area_name,
        unit=unit,
        latest_date=_get_period_name(latest.year, latest.period, db),
        latest_price=latest_price,
        prev_month_price=prev_month_price,
        prev_year_price=prev_year_price,
        mom_change=mom_change,
        mom_pct=mom_pct,
        yoy_change=yoy_change,
        yoy_pct=yoy_pct
    )


# =============================================================================
# DIMENSIONS ENDPOINT
# =============================================================================

@router.get("/dimensions", response_model=APDimensions)
async def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get available dimensions for AP data filtering"""

    # Get areas used in AP
    areas_query = db.query(
        BLSArea.area_code,
        BLSArea.area_name
    ).join(
        APSeries, APSeries.area_code == BLSArea.area_code
    ).distinct().order_by(BLSArea.area_code).all()

    areas = [
        APAreaItem(
            area_code=a.area_code,
            area_name=a.area_name,
            area_type=_get_area_type(a.area_code)
        )
        for a in areas_query
    ]

    # Get items
    items_query = db.query(APItem).order_by(APItem.item_code).all()
    items = [
        APItemInfo(
            item_code=i.item_code,
            item_name=i.item_name,
            category=i.category or _get_category(i.item_code),
            unit=i.unit
        )
        for i in items_query
    ]

    # Get unique categories
    categories = list(set(i.category for i in items if i.category))
    categories.sort()

    # Total series count
    total_series = db.query(func.count(APSeries.series_id)).scalar() or 0

    # Data range
    min_year = db.query(func.min(APData.year)).scalar()
    max_year = db.query(func.max(APData.year)).scalar()
    data_range = f"{min_year}-{max_year}" if min_year and max_year else None

    return APDimensions(
        areas=areas,
        items=items,
        categories=categories,
        total_series=total_series,
        data_range=data_range
    )


# =============================================================================
# SERIES ENDPOINTS
# =============================================================================

@router.get("/series", response_model=APSeriesListResponse)
async def get_series(
    area_code: Optional[str] = Query(None, description="Filter by area code"),
    item_code: Optional[str] = Query(None, description="Filter by item code"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search series title"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get list of AP series with optional filters"""

    query = db.query(
        APSeries,
        BLSArea.area_name,
        APItem.item_name,
        APItem.category,
        APItem.unit
    ).outerjoin(
        BLSArea, APSeries.area_code == BLSArea.area_code
    ).outerjoin(
        APItem, APSeries.item_code == APItem.item_code
    )

    if area_code:
        query = query.filter(APSeries.area_code == area_code)

    if item_code:
        query = query.filter(APSeries.item_code == item_code)

    if category:
        query = query.filter(APItem.category == category)

    if search:
        query = query.filter(APSeries.series_title.ilike(f"%{search}%"))

    total = query.count()

    results = query.order_by(APSeries.series_id).offset(offset).limit(limit).all()

    series = [
        APSeriesInfo(
            series_id=r.APSeries.series_id,
            series_title=r.APSeries.series_title,
            area_code=r.APSeries.area_code,
            area_name=r.area_name,
            item_code=r.APSeries.item_code,
            item_name=r.item_name,
            category=r.category or _get_category(r.APSeries.item_code),
            unit=r.unit,
            seasonal_code=r.APSeries.seasonal_code,
            begin_year=r.APSeries.begin_year,
            end_year=r.APSeries.end_year,
            is_active=r.APSeries.is_active
        )
        for r in results
    ]

    return APSeriesListResponse(
        series=series,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/series/{series_id}/data", response_model=APSeriesData)
async def get_series_data(
    series_id: str,
    months: int = Query(60, ge=1, le=600, description="Number of months of data"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get data for a specific series"""

    series = db.query(
        APSeries,
        BLSArea.area_name,
        APItem.item_name,
        APItem.unit
    ).outerjoin(
        BLSArea, APSeries.area_code == BLSArea.area_code
    ).outerjoin(
        APItem, APSeries.item_code == APItem.item_code
    ).filter(
        APSeries.series_id == series_id
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    data = db.query(APData).filter(
        APData.series_id == series_id,
        APData.period != 'M13'
    ).order_by(desc(APData.year), desc(APData.period)).limit(months).all()

    data_points = [
        APDataPoint(
            year=d.year,
            period=d.period,
            period_name=_get_period_name(d.year, d.period, db),
            value=float(d.value) if d.value else None,
            footnote_codes=d.footnote_codes
        )
        for d in reversed(data)
    ]

    return APSeriesData(
        series_id=series_id,
        series_title=series.APSeries.series_title,
        area_name=series.area_name,
        item_name=series.item_name,
        unit=series.unit,
        data=data_points
    )


# =============================================================================
# OVERVIEW ENDPOINT
# =============================================================================

# Key items for featured prices (national, not seasonally adjusted)
FEATURED_ITEMS = {
    "gasoline_regular": {"item_code": "74714", "name": "Gasoline, unleaded regular"},
    "gasoline_premium": {"item_code": "74716", "name": "Gasoline, unleaded premium"},
    "electricity": {"item_code": "72610", "name": "Electricity per KWH"},
    "natural_gas": {"item_code": "71311", "name": "Utility (piped) gas per therm"},
    "eggs": {"item_code": "708111", "name": "Eggs, grade A, large"},
    "milk": {"item_code": "709112", "name": "Milk, fresh, whole"},
    "bread": {"item_code": "702111", "name": "Bread, white, pan"},
    "ground_beef": {"item_code": "703112", "name": "Ground beef, 100% beef"},
    "chicken": {"item_code": "706111", "name": "Chicken, fresh, whole"},
    "bacon": {"item_code": "704111", "name": "Bacon, sliced"},
    "butter": {"item_code": "710111", "name": "Butter, salted"},
    "coffee": {"item_code": "717311", "name": "Coffee, ground roast"},
}


@router.get("/overview", response_model=APOverviewResponse)
async def get_overview(
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get overview of AP data with featured prices and category summaries"""

    # Get latest date
    latest = db.query(APData.year, APData.period).filter(
        APData.period != 'M13'
    ).order_by(desc(APData.year), desc(APData.period)).first()

    latest_date = _get_period_name(latest.year, latest.period, db) if latest else None

    # Total counts
    total_items = db.query(func.count(APItem.item_code)).scalar() or 0
    total_series = db.query(func.count(APSeries.series_id)).scalar() or 0

    # Featured prices (national averages)
    featured_prices = []
    for key, info in FEATURED_ITEMS.items():
        # Find national series for this item
        series = db.query(
            APSeries,
            APItem.item_name,
            APItem.unit
        ).outerjoin(
            APItem, APSeries.item_code == APItem.item_code
        ).filter(
            APSeries.item_code == info["item_code"],
            APSeries.area_code == "0000"  # U.S. city average
        ).first()

        if series:
            metric = _calculate_price_metrics(
                series.APSeries.series_id,
                info["item_code"],
                series.item_name or info["name"],
                "0000",
                "U.S. city average",
                series.unit,
                db
            )
            if metric and metric.latest_price:
                featured_prices.append(metric)

    # Category summaries
    categories = []
    for cat in ["Gasoline", "Household Fuels", "Food"]:
        # Count items and series in category
        cat_items = db.query(APItem).filter(APItem.category == cat).all()
        item_count = len(cat_items)

        series_count = db.query(func.count(APSeries.series_id)).join(
            APItem, APSeries.item_code == APItem.item_code
        ).filter(APItem.category == cat).scalar() or 0

        # Top items by YoY change in this category (national)
        top_items = []
        for item in cat_items[:5]:  # Limit to first 5 items
            series = db.query(
                APSeries,
                APItem.item_name,
                APItem.unit
            ).outerjoin(
                APItem, APSeries.item_code == APItem.item_code
            ).filter(
                APSeries.item_code == item.item_code,
                APSeries.area_code == "0000"
            ).first()

            if series:
                metric = _calculate_price_metrics(
                    series.APSeries.series_id,
                    item.item_code,
                    series.item_name or item.item_name,
                    "0000",
                    "U.S. city average",
                    series.unit,
                    db
                )
                if metric and metric.latest_price:
                    top_items.append(metric)

        # Sort by absolute YoY change
        top_items.sort(key=lambda x: abs(x.yoy_pct or 0), reverse=True)

        categories.append(APCategoryOverview(
            category=cat,
            item_count=item_count,
            series_count=series_count,
            top_items=top_items[:5]
        ))

    return APOverviewResponse(
        latest_date=latest_date,
        total_items=total_items,
        total_series=total_series,
        categories=categories,
        featured_prices=featured_prices
    )


# =============================================================================
# AREA COMPARISON
# =============================================================================

@router.get("/areas/compare", response_model=APAreaComparisonResponse)
async def compare_areas(
    item_code: str = Query(..., description="Item code to compare"),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Compare prices for an item across different areas"""

    item = db.query(APItem).filter(APItem.item_code == item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Get all series for this item
    series_list = db.query(
        APSeries,
        BLSArea.area_name
    ).outerjoin(
        BLSArea, APSeries.area_code == BLSArea.area_code
    ).filter(
        APSeries.item_code == item_code
    ).all()

    latest_date = None
    areas = []

    for s in series_list:
        # Get latest data
        data = db.query(APData).filter(
            APData.series_id == s.APSeries.series_id,
            APData.period != 'M13'
        ).order_by(desc(APData.year), desc(APData.period)).limit(14).all()

        if not data:
            continue

        latest = data[0]
        if not latest_date:
            latest_date = _get_period_name(latest.year, latest.period, db)

        prev_month = data[1] if len(data) > 1 else None
        prev_year = None
        for d in data:
            if d.year == latest.year - 1 and d.period == latest.period:
                prev_year = d
                break

        latest_price = float(latest.value) if latest.value else None
        mom_pct = None
        yoy_pct = None

        if latest_price and prev_month and prev_month.value:
            prev_val = float(prev_month.value)
            if prev_val != 0:
                mom_pct = round(((latest_price - prev_val) / prev_val) * 100, 2)

        if latest_price and prev_year and prev_year.value:
            prev_val = float(prev_year.value)
            if prev_val != 0:
                yoy_pct = round(((latest_price - prev_val) / prev_val) * 100, 2)

        areas.append(APAreaMetric(
            area_code=s.APSeries.area_code,
            area_name=s.area_name or s.APSeries.area_code,
            area_type=_get_area_type(s.APSeries.area_code),
            item_code=item_code,
            item_name=item.item_name,
            unit=item.unit,
            latest_price=latest_price,
            mom_pct=mom_pct,
            yoy_pct=yoy_pct
        ))

    # Sort by area code
    areas.sort(key=lambda x: x.area_code)

    return APAreaComparisonResponse(
        item_code=item_code,
        item_name=item.item_name,
        unit=item.unit,
        latest_date=latest_date,
        areas=areas
    )


# =============================================================================
# ITEMS ANALYSIS
# =============================================================================

@router.get("/items/analysis", response_model=APItemsAnalysisResponse)
async def get_items_analysis(
    category: str = Query(..., description="Category: Food, Gasoline, Household Fuels"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get price analysis for items in a category"""

    # Get items in category
    items = db.query(APItem).filter(
        APItem.category == category
    ).order_by(APItem.item_code).limit(limit).all()

    latest_date = None
    item_metrics = []

    for item in items:
        # Get national series
        series = db.query(APSeries).filter(
            APSeries.item_code == item.item_code,
            APSeries.area_code == "0000"
        ).first()

        if not series:
            continue

        # Get data
        data = db.query(APData).filter(
            APData.series_id == series.series_id,
            APData.period != 'M13'
        ).order_by(desc(APData.year), desc(APData.period)).limit(14).all()

        if not data:
            continue

        latest = data[0]
        if not latest_date:
            latest_date = _get_period_name(latest.year, latest.period, db)

        prev_month = data[1] if len(data) > 1 else None
        prev_year = None
        for d in data:
            if d.year == latest.year - 1 and d.period == latest.period:
                prev_year = d
                break

        latest_price = float(latest.value) if latest.value else None
        prev_month_price = float(prev_month.value) if prev_month and prev_month.value else None
        prev_year_price = float(prev_year.value) if prev_year and prev_year.value else None

        mom_change = None
        mom_pct = None
        yoy_change = None
        yoy_pct = None

        if latest_price and prev_month_price:
            mom_change = round(latest_price - prev_month_price, 3)
            mom_pct = round((mom_change / prev_month_price) * 100, 2) if prev_month_price != 0 else None

        if latest_price and prev_year_price:
            yoy_change = round(latest_price - prev_year_price, 3)
            yoy_pct = round((yoy_change / prev_year_price) * 100, 2) if prev_year_price != 0 else None

        # Get 52-week high/low
        year_data = db.query(APData).filter(
            APData.series_id == series.series_id,
            APData.period != 'M13'
        ).order_by(desc(APData.year), desc(APData.period)).limit(12).all()

        prices = [float(d.value) for d in year_data if d.value]
        price_52w_high = max(prices) if prices else None
        price_52w_low = min(prices) if prices else None

        item_metrics.append(APItemMetric(
            item_code=item.item_code,
            item_name=item.item_name,
            category=category,
            unit=item.unit,
            series_id=series.series_id,
            latest_date=latest_date,
            latest_price=latest_price,
            mom_change=mom_change,
            mom_pct=mom_pct,
            yoy_change=yoy_change,
            yoy_pct=yoy_pct,
            price_52w_high=price_52w_high,
            price_52w_low=price_52w_low
        ))

    return APItemsAnalysisResponse(
        category=category,
        latest_date=latest_date,
        items=item_metrics
    )


# =============================================================================
# TOP MOVERS
# =============================================================================

@router.get("/top-movers", response_model=APTopMoversResponse)
async def get_top_movers(
    period: str = Query("mom", description="Period: 'mom' or 'yoy'"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get items with largest price changes"""

    # Get national series
    query = db.query(
        APSeries,
        APItem.item_name,
        APItem.category,
        APItem.unit
    ).join(
        APItem, APSeries.item_code == APItem.item_code
    ).filter(
        APSeries.area_code == "0000"  # National only
    )

    if category:
        query = query.filter(APItem.category == category)

    series_list = query.all()

    latest_date = None
    all_movers = []

    for s in series_list:
        data = db.query(APData).filter(
            APData.series_id == s.APSeries.series_id,
            APData.period != 'M13'
        ).order_by(desc(APData.year), desc(APData.period)).limit(14).all()

        if len(data) < 2:
            continue

        latest = data[0]
        if not latest_date:
            latest_date = _get_period_name(latest.year, latest.period, db)

        latest_price = float(latest.value) if latest.value else None
        if not latest_price:
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

        prev_price = float(prev.value)
        if prev_price == 0:
            continue

        change = latest_price - prev_price
        pct_change = round((change / prev_price) * 100, 2)

        all_movers.append(APTopMover(
            series_id=s.APSeries.series_id,
            item_code=s.APSeries.item_code,
            item_name=s.item_name,
            category=s.category,
            unit=s.unit,
            area_name="U.S. city average",
            latest_price=latest_price,
            change=round(change, 3),
            pct_change=pct_change,
            direction="up" if pct_change > 0 else "down"
        ))

    # Sort and split into gainers/losers
    all_movers.sort(key=lambda x: x.pct_change, reverse=True)
    gainers = [m for m in all_movers if m.pct_change > 0][:limit]
    losers = [m for m in all_movers if m.pct_change < 0]
    losers.sort(key=lambda x: x.pct_change)
    losers = losers[:limit]

    return APTopMoversResponse(
        period=period,
        latest_date=latest_date,
        gainers=gainers,
        losers=losers
    )


# =============================================================================
# TIMELINE DATA
# =============================================================================

@router.get("/items/{item_code}/timeline", response_model=APItemTimelineResponse)
async def get_item_timeline(
    item_code: str,
    area_code: str = Query("0000", description="Area code (default: national)"),
    months: int = Query(60, ge=1, le=600),
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    """Get price timeline for an item"""

    item = db.query(APItem).filter(APItem.item_code == item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    series = db.query(APSeries).filter(
        APSeries.item_code == item_code,
        APSeries.area_code == area_code
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found for this item/area")

    area = db.query(BLSArea).filter(BLSArea.area_code == area_code).first()
    area_name = area.area_name if area else area_code

    data = db.query(APData).filter(
        APData.series_id == series.series_id,
        APData.period != 'M13'
    ).order_by(desc(APData.year), desc(APData.period)).limit(months).all()

    timeline = [
        APTimelinePoint(
            date=f"{d.year}-{d.period[1:]}",  # "2024-01"
            year=d.year,
            period=d.period,
            value=float(d.value) if d.value else None
        )
        for d in reversed(data)
    ]

    return APItemTimelineResponse(
        item_code=item_code,
        item_name=item.item_name,
        unit=item.unit,
        area_name=area_name,
        timeline=timeline
    )
