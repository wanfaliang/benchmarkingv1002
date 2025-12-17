"""
WP (Producer Price Index - Commodities/Final Demand) Survey Explorer API

Endpoints for exploring Producer Price Index data by commodity group and item.
This survey contains the HEADLINE PPI numbers reported in press releases (Final Demand).

Key sections:
- Final Demand (FD): Headline PPI numbers
- Intermediate Demand (ID): Production stage price indexes
- Traditional commodity groups (01-15)
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List

from ....database import get_data_db
from ....api.auth import get_current_user
from .wp_schemas import (
    WPDimensions, WPGroupItem, WPItemInfo,
    WPSeriesInfo, WPSeriesListResponse,
    WPDataPoint, WPSeriesData, WPDataResponse,
    WPHeadlinePPI, WPFinalDemandOverview, WPOverviewTimelinePoint, WPOverviewTimelineResponse,
    WPGroupMetric, WPGroupAnalysisResponse, WPGroupTimelinePoint, WPGroupTimelineResponse,
    WPItemMetric, WPItemAnalysisResponse, WPItemTimelinePoint, WPItemTimelineResponse,
    WPIntermediateDemandStage, WPIntermediateDemandResponse,
    WPTopMover, WPTopMoversResponse
)
from ....data_models.bls_models import (
    WPGroup, WPItem, WPSeries, WPData, BLSPeriod
)

router = APIRouter(
    prefix="/api/research/bls/wp",
    tags=["BLS WP - Producer Price Index (Commodities/Final Demand)"]
)

# Final Demand series IDs - these are the headline PPI numbers
# Format: WPS + seasonal (S/U) + group + item
FINAL_DEMAND_SERIES = {
    "final_demand": {
        "series_id": "WPSFD4",  # Final Demand - Total
        "name": "Final Demand",
        "description": "PPI for Final Demand (Headline)"
    },
    "final_demand_goods": {
        "series_id": "WPSFD41",  # Final Demand - Goods
        "name": "Final Demand - Goods",
        "description": "PPI for Final Demand Goods"
    },
    "final_demand_services": {
        "series_id": "WPSFD42",  # Final Demand - Services
        "name": "Final Demand - Services",
        "description": "PPI for Final Demand Services"
    },
    "final_demand_construction": {
        "series_id": "WPSFD43",  # Final Demand - Construction
        "name": "Final Demand - Construction",
        "description": "PPI for Final Demand Construction"
    },
    "final_demand_core": {
        "series_id": "WPSFD49116",  # Final Demand less foods, energy, trade services
        "name": "Final Demand - Core (ex Food, Energy, Trade)",
        "description": "PPI Core - excluding food, energy, and trade services"
    },
    "final_demand_ex_food_energy": {
        "series_id": "WPSFD49104",  # Final Demand less foods and energy
        "name": "Final Demand - ex Food & Energy",
        "description": "PPI excluding food and energy"
    },
}

# Intermediate Demand stages
INTERMEDIATE_DEMAND_STAGES = {
    "stage4_processed": {
        "series_id": "WPUID54",
        "name": "Stage 4 - Processed Goods",
        "stage": "stage4"
    },
    "stage3_processed": {
        "series_id": "WPUID53",
        "name": "Stage 3 - Processed Goods",
        "stage": "stage3"
    },
    "stage2_processed": {
        "series_id": "WPUID52",
        "name": "Stage 2 - Processed Goods",
        "stage": "stage2"
    },
    "stage1_unprocessed": {
        "series_id": "WPUID51",
        "name": "Stage 1 - Unprocessed Goods",
        "stage": "stage1"
    },
}


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


def _calculate_ppi_metrics(series_id: str, name: str, db: Session) -> Optional[WPHeadlinePPI]:
    """Calculate PPI metrics for a series"""
    data = db.query(WPData).filter(
        WPData.series_id == series_id,
        WPData.period != 'M13'
    ).order_by(desc(WPData.year), desc(WPData.period)).limit(14).all()

    if not data:
        return None

    latest = data[0]
    prev_month = data[1] if len(data) > 1 else None
    prev_year = None

    for d in data:
        if d.year == latest.year - 1 and d.period == latest.period:
            prev_year = d
            break

    latest_value = float(latest.value) if latest.value else None

    mom_pct = None
    if prev_month and prev_month.value and latest_value:
        prev_val = float(prev_month.value)
        if prev_val != 0:
            mom_pct = ((latest_value - prev_val) / prev_val) * 100

    yoy_pct = None
    if prev_year and prev_year.value and latest_value:
        prev_val = float(prev_year.value)
        if prev_val != 0:
            yoy_pct = ((latest_value - prev_val) / prev_val) * 100

    return WPHeadlinePPI(
        series_id=series_id,
        name=name,
        latest_date=_get_period_name(latest.year, latest.period, db),
        mom_pct=round(mom_pct, 2) if mom_pct is not None else None,
        yoy_pct=round(yoy_pct, 2) if yoy_pct is not None else None,
        index_value=latest_value
    )


def _is_final_demand_group(group_code: str) -> bool:
    """Check if group code is part of Final Demand-Intermediate Demand system"""
    fd_prefixes = ['FD', 'ID', 'FG', 'FS', 'FC']  # Final Demand, Intermediate Demand, etc.
    return any(group_code.upper().startswith(p) for p in fd_prefixes)


# ==================== Dimensions ====================

@router.get("/dimensions", response_model=WPDimensions)
def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get available dimensions for WP survey filtering"""

    groups = db.query(WPGroup).order_by(WPGroup.group_code).all()

    all_groups = []
    fd_groups = []
    commodity_groups = []

    for g in groups:
        is_fd = _is_final_demand_group(g.group_code)
        item = WPGroupItem(
            group_code=g.group_code,
            group_name=g.group_name,
            is_final_demand=is_fd
        )
        all_groups.append(item)
        if is_fd:
            fd_groups.append(item)
        else:
            commodity_groups.append(item)

    # Get distinct base years
    base_dates = db.query(WPSeries.base_date).distinct().all()
    base_years_set = set()
    for (bd,) in base_dates:
        if bd and len(bd) >= 4:
            try:
                year = int(bd[:4])
                base_years_set.add(year)
            except ValueError:
                pass

    # Get distinct start years
    start_years_result = db.query(WPSeries.begin_year).distinct().filter(
        WPSeries.begin_year.isnot(None)
    ).all()
    start_years = sorted([y for (y,) in start_years_result if y])

    return WPDimensions(
        groups=all_groups,
        final_demand_groups=fd_groups,
        commodity_groups=commodity_groups,
        base_years=sorted(base_years_set),
        start_years=start_years
    )


# ==================== Series ====================

@router.get("/series", response_model=WPSeriesListResponse)
def get_series(
    group_code: Optional[str] = Query(None, description="Filter by exact group code"),
    item_code: Optional[str] = Query(None, description="Filter by item code (requires group_code)"),
    seasonal_code: Optional[str] = Query(None, description="S=Seasonally Adjusted, U=Not Adjusted"),
    final_demand_only: bool = Query(False, description="Only show Final Demand series"),
    commodity_only: bool = Query(False, description="Only show traditional commodity series"),
    base_year: Optional[int] = Query(None, description="Filter by base year"),
    min_start_year: Optional[int] = Query(None, description="Series with data from this year or earlier"),
    active_only: bool = Query(True, description="Only return active series"),
    search: Optional[str] = Query(None, description="Search in series title, group name, or item name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """List WP series with optional filters and search"""

    if search:
        matching_groups = db.query(WPGroup.group_code).filter(
            WPGroup.group_name.ilike(f"%{search}%")
        ).all()
        matching_group_codes = [g[0] for g in matching_groups]

        matching_items = db.query(WPItem.group_code, WPItem.item_code).filter(
            WPItem.item_name.ilike(f"%{search}%")
        ).all()

        search_conditions = [WPSeries.series_title.ilike(f"%{search}%")]

        if matching_group_codes:
            search_conditions.append(WPSeries.group_code.in_(matching_group_codes))

        if matching_items:
            item_conditions = []
            for grp_code, itm_code in matching_items:
                item_conditions.append(
                    and_(WPSeries.group_code == grp_code, WPSeries.item_code == itm_code)
                )
            if item_conditions:
                search_conditions.append(or_(*item_conditions))

        query = db.query(WPSeries).filter(or_(*search_conditions))
    else:
        query = db.query(WPSeries)

    if group_code:
        query = query.filter(WPSeries.group_code == group_code)

    if item_code and group_code:
        query = query.filter(WPSeries.item_code == item_code)

    if seasonal_code:
        query = query.filter(WPSeries.seasonal_code == seasonal_code)

    if final_demand_only:
        fd_prefixes = ['FD', 'ID', 'FG', 'FS', 'FC']
        fd_conditions = [WPSeries.group_code.like(f"{p}%") for p in fd_prefixes]
        query = query.filter(or_(*fd_conditions))

    if commodity_only:
        fd_prefixes = ['FD', 'ID', 'FG', 'FS', 'FC']
        for p in fd_prefixes:
            query = query.filter(~WPSeries.group_code.like(f"{p}%"))

    if base_year:
        query = query.filter(WPSeries.base_date.like(f"{base_year}%"))

    if min_start_year:
        query = query.filter(WPSeries.begin_year <= min_start_year)

    if active_only:
        query = query.filter(WPSeries.is_active == True)

    total = query.count()

    series = query.order_by(WPSeries.group_code, WPSeries.item_code).offset(offset).limit(limit).all()

    # Get group names
    group_codes = list(set(s.group_code for s in series if s.group_code))
    group_names = {}
    if group_codes:
        groups = db.query(WPGroup).filter(WPGroup.group_code.in_(group_codes)).all()
        group_names = {g.group_code: g.group_name for g in groups}

    # Get item names
    item_keys = [(s.group_code, s.item_code) for s in series if s.item_code]
    item_names = {}
    if item_keys:
        items = db.query(WPItem).filter(WPItem.group_code.in_(group_codes)).all()
        item_names = {(i.group_code, i.item_code): i.item_name for i in items}

    series_list = [
        WPSeriesInfo(
            series_id=s.series_id,
            series_title=s.series_title,
            group_code=s.group_code,
            group_name=group_names.get(s.group_code),
            item_code=s.item_code,
            item_name=item_names.get((s.group_code, s.item_code)),
            seasonal_code=s.seasonal_code,
            base_date=s.base_date,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active
        )
        for s in series
    ]

    return WPSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_list
    )


@router.get("/series/{series_id}/data", response_model=WPDataResponse)
def get_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get time series data for a specific WP series"""

    series = db.query(WPSeries).filter(WPSeries.series_id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    query = db.query(WPData).filter(WPData.series_id == series_id)

    if start_year:
        query = query.filter(WPData.year >= start_year)
    if end_year:
        query = query.filter(WPData.year <= end_year)

    data = query.order_by(WPData.year, WPData.period).all()

    group_name = ""
    if series.group_code:
        group = db.query(WPGroup).filter(WPGroup.group_code == series.group_code).first()
        if group:
            group_name = group.group_name

    item_name = None
    if series.item_code:
        item = db.query(WPItem).filter(
            WPItem.group_code == series.group_code,
            WPItem.item_code == series.item_code
        ).first()
        if item:
            item_name = item.item_name

    data_points = [
        WPDataPoint(
            year=d.year,
            period=d.period,
            period_name=_get_period_name(d.year, d.period, db),
            value=float(d.value) if d.value else None,
            footnote_codes=d.footnote_codes
        )
        for d in data
    ]

    return WPDataResponse(
        series=[WPSeriesData(
            series_id=series.series_id,
            series_title=series.series_title,
            group_name=group_name,
            item_name=item_name,
            base_date=series.base_date,
            data_points=data_points
        )]
    )


# ==================== Items for a Group ====================

@router.get("/groups/{group_code}/items")
def get_items_for_group(
    group_code: str,
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get all items for a specific group"""

    group = db.query(WPGroup).filter(WPGroup.group_code == group_code).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_code} not found")

    items = db.query(WPItem).filter(
        WPItem.group_code == group_code
    ).order_by(WPItem.item_code).all()

    return {
        "group_code": group_code,
        "group_name": group.group_name,
        "items": [
            WPItemInfo(
                group_code=i.group_code,
                item_code=i.item_code,
                item_name=i.item_name
            )
            for i in items
        ]
    }


# ==================== Final Demand Overview (Headline PPI) ====================

@router.get("/overview", response_model=WPFinalDemandOverview)
def get_overview(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get Final Demand PPI overview - HEADLINE NUMBERS

    This returns the PPI numbers reported in BLS press releases:
    - Final Demand (total) - THE headline number
    - Final Demand Goods
    - Final Demand Services
    - Core PPI (ex food, energy, trade)
    """

    # Calculate headline (total Final Demand)
    headline_info = FINAL_DEMAND_SERIES["final_demand"]
    headline = _calculate_ppi_metrics(headline_info["series_id"], headline_info["name"], db)

    if not headline:
        # Try alternative series ID patterns
        alt_series = db.query(WPSeries).filter(
            WPSeries.series_title.ilike("%final demand%"),
            WPSeries.seasonal_code == 'S'
        ).first()
        if alt_series:
            headline = _calculate_ppi_metrics(alt_series.series_id, "Final Demand", db)

    if not headline:
        headline = WPHeadlinePPI(
            series_id="WPSFD4",
            name="Final Demand",
            latest_date=None,
            mom_pct=None,
            yoy_pct=None,
            index_value=None
        )

    # Calculate component metrics
    components = []
    for key in ["final_demand_goods", "final_demand_services", "final_demand_construction",
                "final_demand_ex_food_energy", "final_demand_core"]:
        info = FINAL_DEMAND_SERIES.get(key)
        if info:
            metric = _calculate_ppi_metrics(info["series_id"], info["name"], db)
            if metric:
                components.append(metric)

    # Get last updated from headline
    last_updated = headline.latest_date if headline else None

    return WPFinalDemandOverview(
        headline=headline,
        components=components,
        last_updated=last_updated
    )


@router.get("/overview/timeline", response_model=WPOverviewTimelineResponse)
def get_overview_timeline(
    months_back: int = Query(24, ge=6, le=120, description="Number of months to retrieve"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for Final Demand overview charts (MoM % changes)"""

    categories = {
        "fd_total": FINAL_DEMAND_SERIES["final_demand"],
        "fd_goods": FINAL_DEMAND_SERIES["final_demand_goods"],
        "fd_services": FINAL_DEMAND_SERIES["final_demand_services"],
        "fd_core": FINAL_DEMAND_SERIES["final_demand_core"],
    }

    category_names = {
        "fd_total": "Final Demand",
        "fd_goods": "Goods",
        "fd_services": "Services",
        "fd_core": "Core (ex Food/Energy/Trade)"
    }

    # Get data for each category
    all_data = {}
    for cat_key, info in categories.items():
        data = db.query(WPData).filter(
            WPData.series_id == info["series_id"],
            WPData.period != 'M13'
        ).order_by(desc(WPData.year), desc(WPData.period)).limit(months_back + 1).all()
        all_data[cat_key] = {(d.year, d.period): float(d.value) if d.value else None for d in data}

    # Build timeline with MoM % changes
    timeline = []
    periods_processed = set()

    for cat_key, info in categories.items():
        data = db.query(WPData).filter(
            WPData.series_id == info["series_id"],
            WPData.period != 'M13'
        ).order_by(WPData.year, WPData.period).all()

        for d in data[-months_back:]:
            key = (d.year, d.period)
            if key not in periods_processed:
                periods_processed.add(key)

    sorted_periods = sorted(periods_processed)

    for i, (year, period) in enumerate(sorted_periods):
        categories_mom = {}

        for cat_key in categories.keys():
            current_val = all_data[cat_key].get((year, period))

            # Find previous month
            prev_val = None
            if i > 0:
                prev_year, prev_period = sorted_periods[i - 1]
                prev_val = all_data[cat_key].get((prev_year, prev_period))

            if current_val and prev_val and prev_val != 0:
                mom_pct = ((current_val - prev_val) / prev_val) * 100
                categories_mom[cat_key] = round(mom_pct, 2)
            else:
                categories_mom[cat_key] = None

        timeline.append(WPOverviewTimelinePoint(
            year=year,
            period=period,
            period_name=_get_period_name(year, period, db),
            categories=categories_mom
        ))

    return WPOverviewTimelineResponse(
        timeline=timeline,
        category_names=category_names
    )


# ==================== Intermediate Demand ====================

@router.get("/intermediate-demand", response_model=WPIntermediateDemandResponse)
def get_intermediate_demand(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get Intermediate Demand breakdown by production stages

    Shows price indexes at different stages of production:
    - Stage 4: Most processed goods
    - Stage 3: Intermediate processed
    - Stage 2: Early processed
    - Stage 1: Unprocessed/raw materials
    """

    stages = []
    for key, info in INTERMEDIATE_DEMAND_STAGES.items():
        data = db.query(WPData).filter(
            WPData.series_id == info["series_id"],
            WPData.period != 'M13'
        ).order_by(desc(WPData.year), desc(WPData.period)).limit(14).all()

        if not data:
            continue

        latest = data[0]
        prev_month = data[1] if len(data) > 1 else None
        prev_year = None

        for d in data:
            if d.year == latest.year - 1 and d.period == latest.period:
                prev_year = d
                break

        latest_value = float(latest.value) if latest.value else None

        mom_pct = None
        if prev_month and prev_month.value and latest_value:
            prev_val = float(prev_month.value)
            if prev_val != 0:
                mom_pct = ((latest_value - prev_val) / prev_val) * 100

        yoy_pct = None
        if prev_year and prev_year.value and latest_value:
            prev_val = float(prev_year.value)
            if prev_val != 0:
                yoy_pct = ((latest_value - prev_val) / prev_val) * 100

        stages.append(WPIntermediateDemandStage(
            stage=info["stage"],
            stage_name=info["name"],
            series_id=info["series_id"],
            latest_date=_get_period_name(latest.year, latest.period, db),
            mom_pct=round(mom_pct, 2) if mom_pct is not None else None,
            yoy_pct=round(yoy_pct, 2) if yoy_pct is not None else None,
            index_value=latest_value
        ))

    last_updated = stages[0].latest_date if stages else None

    return WPIntermediateDemandResponse(
        stages=stages,
        last_updated=last_updated
    )


# ==================== Group Analysis ====================

@router.get("/groups/analysis", response_model=WPGroupAnalysisResponse)
def get_group_analysis(
    commodity_only: bool = Query(False, description="Only traditional commodity groups"),
    final_demand_only: bool = Query(False, description="Only FD-ID groups"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get PPI analysis by commodity group"""

    groups_query = db.query(WPGroup).order_by(WPGroup.group_code)

    if commodity_only:
        fd_prefixes = ['FD', 'ID', 'FG', 'FS', 'FC']
        for p in fd_prefixes:
            groups_query = groups_query.filter(~WPGroup.group_code.like(f"{p}%"))

    if final_demand_only:
        fd_prefixes = ['FD', 'ID', 'FG', 'FS', 'FC']
        fd_conditions = [WPGroup.group_code.like(f"{p}%") for p in fd_prefixes]
        groups_query = groups_query.filter(or_(*fd_conditions))

    groups = groups_query.limit(limit).all()

    group_metrics = []
    for group in groups:
        # Find primary series for this group (usually seasonal adjusted, no item code)
        series = db.query(WPSeries).filter(
            WPSeries.group_code == group.group_code,
            WPSeries.seasonal_code == 'S',
            WPSeries.is_active == True
        ).order_by(WPSeries.item_code).first()

        if not series:
            series = db.query(WPSeries).filter(
                WPSeries.group_code == group.group_code,
                WPSeries.is_active == True
            ).first()

        if not series:
            continue

        metric = _calculate_ppi_metrics(series.series_id, group.group_name, db)
        if metric:
            group_metrics.append(WPGroupMetric(
                group_code=group.group_code,
                group_name=group.group_name,
                series_id=series.series_id,
                latest_value=metric.index_value,
                latest_date=metric.latest_date,
                mom_pct=metric.mom_pct,
                yoy_pct=metric.yoy_pct
            ))

    last_updated = group_metrics[0].latest_date if group_metrics else None

    return WPGroupAnalysisResponse(
        groups=group_metrics,
        last_updated=last_updated
    )


@router.get("/groups/timeline", response_model=WPGroupTimelineResponse)
def get_group_timeline(
    group_codes: str = Query(..., description="Comma-separated group codes"),
    months_back: int = Query(24, ge=6, le=120),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for comparing multiple groups"""

    codes = [c.strip() for c in group_codes.split(',')][:6]

    group_series = {}
    group_names = {}

    for code in codes:
        group = db.query(WPGroup).filter(WPGroup.group_code == code).first()
        if not group:
            continue

        series = db.query(WPSeries).filter(
            WPSeries.group_code == code,
            WPSeries.seasonal_code == 'S',
            WPSeries.is_active == True
        ).first()

        if series:
            group_series[code] = series.series_id
            group_names[code] = group.group_name

    if not group_series:
        raise HTTPException(status_code=404, detail="No valid groups found")

    # Get data
    period_data = {}
    for code, series_id in group_series.items():
        data = db.query(WPData).filter(
            WPData.series_id == series_id,
            WPData.period != 'M13'
        ).order_by(desc(WPData.year), desc(WPData.period)).limit(months_back).all()

        for d in data:
            key = (d.year, d.period)
            if key not in period_data:
                period_data[key] = {'year': d.year, 'period': d.period, 'groups': {}}
            period_data[key]['groups'][code] = float(d.value) if d.value else None

    timeline = []
    for key in sorted(period_data.keys()):
        pd = period_data[key]
        timeline.append(WPGroupTimelinePoint(
            year=pd['year'],
            period=pd['period'],
            period_name=_get_period_name(pd['year'], pd['period'], db),
            groups=pd['groups']
        ))

    return WPGroupTimelineResponse(
        timeline=timeline,
        group_names=group_names
    )


# ==================== Item Analysis ====================

@router.get("/groups/{group_code}/analysis", response_model=WPItemAnalysisResponse)
def get_item_analysis(
    group_code: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get item-level PPI analysis for a specific group"""

    group = db.query(WPGroup).filter(WPGroup.group_code == group_code).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_code} not found")

    # Get series with item codes
    series_list = db.query(WPSeries).filter(
        WPSeries.group_code == group_code,
        WPSeries.item_code.isnot(None),
        WPSeries.is_active == True
    ).order_by(WPSeries.item_code).limit(limit).all()

    # Get item names
    items = db.query(WPItem).filter(WPItem.group_code == group_code).all()
    item_names = {i.item_code: i.item_name for i in items}

    item_metrics = []
    for series in series_list:
        metric = _calculate_ppi_metrics(series.series_id, series.series_title, db)
        if metric:
            item_metrics.append(WPItemMetric(
                group_code=group_code,
                group_name=group.group_name,
                item_code=series.item_code,
                item_name=item_names.get(series.item_code, series.series_title),
                series_id=series.series_id,
                latest_value=metric.index_value,
                latest_date=metric.latest_date,
                mom_pct=metric.mom_pct,
                yoy_pct=metric.yoy_pct
            ))

    return WPItemAnalysisResponse(
        group_code=group_code,
        group_name=group.group_name,
        items=item_metrics,
        total_count=len(item_metrics),
        last_updated=item_metrics[0].latest_date if item_metrics else None
    )


# ==================== Top Movers ====================

@router.get("/top-movers", response_model=WPTopMoversResponse)
def get_top_movers(
    period: str = Query("mom", description="'mom' for month-over-month, 'yoy' for year-over-year"),
    limit: int = Query(10, ge=1, le=25),
    commodity_only: bool = Query(True, description="Only traditional commodities (exclude FD-ID)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get top price movers (gainers and losers)"""

    query = db.query(WPSeries).filter(
        WPSeries.is_active == True,
        WPSeries.seasonal_code == 'S'
    )

    if commodity_only:
        fd_prefixes = ['FD', 'ID', 'FG', 'FS', 'FC']
        for p in fd_prefixes:
            query = query.filter(~WPSeries.group_code.like(f"{p}%"))

    series_list = query.limit(200).all()

    # Calculate metrics
    all_metrics = []
    for series in series_list:
        metric = _calculate_ppi_metrics(series.series_id, series.series_title, db)
        if metric:
            change_pct = metric.mom_pct if period == 'mom' else metric.yoy_pct
            if change_pct is not None:
                all_metrics.append({
                    'series': series,
                    'metric': metric,
                    'change_pct': change_pct
                })

    # Sort and get top movers
    sorted_metrics = sorted(all_metrics, key=lambda x: x['change_pct'], reverse=True)

    gainers = []
    for m in sorted_metrics[:limit]:
        s = m['series']
        group = db.query(WPGroup).filter(WPGroup.group_code == s.group_code).first()
        item = None
        if s.item_code:
            item = db.query(WPItem).filter(
                WPItem.group_code == s.group_code,
                WPItem.item_code == s.item_code
            ).first()

        gainers.append(WPTopMover(
            series_id=s.series_id,
            group_code=s.group_code,
            group_name=group.group_name if group else s.group_code,
            item_code=s.item_code,
            item_name=item.item_name if item else None,
            latest_value=m['metric'].index_value,
            latest_date=m['metric'].latest_date,
            change_pct=m['change_pct']
        ))

    losers = []
    for m in sorted_metrics[-limit:]:
        s = m['series']
        group = db.query(WPGroup).filter(WPGroup.group_code == s.group_code).first()
        item = None
        if s.item_code:
            item = db.query(WPItem).filter(
                WPItem.group_code == s.group_code,
                WPItem.item_code == s.item_code
            ).first()

        losers.append(WPTopMover(
            series_id=s.series_id,
            group_code=s.group_code,
            group_name=group.group_name if group else s.group_code,
            item_code=s.item_code,
            item_name=item.item_name if item else None,
            latest_value=m['metric'].index_value,
            latest_date=m['metric'].latest_date,
            change_pct=m['change_pct']
        ))

    losers.reverse()

    return WPTopMoversResponse(
        period=period,
        gainers=gainers,
        losers=losers,
        last_updated=gainers[0].latest_date if gainers else None
    )
