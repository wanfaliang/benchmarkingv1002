"""
PC (Producer Price Index - Industry) Survey Explorer API

Endpoints for exploring Producer Price Index data by NAICS industry and product.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List

from ....database import get_data_db
from ....api.auth import get_current_user
from .pc_schemas import (
    PCDimensions, PCIndustryItem, PCProductItem,
    PCSeriesInfo, PCSeriesListResponse,
    PCDataPoint, PCSeriesData, PCDataResponse,
    PCPriceMetric, PCSectorSummary, PCOverviewResponse, PCOverviewTimelinePoint, PCOverviewTimelineResponse,
    PCSectorMetric, PCSectorAnalysisResponse, PCSectorTimelinePoint, PCSectorTimelineResponse,
    PCIndustryMetric, PCIndustryAnalysisResponse, PCIndustryTimelinePoint, PCIndustryTimelineResponse,
    PCProductMetric, PCProductAnalysisResponse, PCProductTimelinePoint, PCProductTimelineResponse,
    PCTopMover, PCTopMoversResponse
)
from ....data_models.bls_models import (
    PCIndustry, PCProduct, PCSeries, PCData, BLSPeriod
)

router = APIRouter(
    prefix="/api/research/bls/pc",
    tags=["BLS PC - Producer Price Index (Industry)"]
)

# NAICS sector mapping (2-digit codes)
# Manufacturing (31-33), Retail (44-45), Transportation (48-49) have multiple subsector codes
NAICS_SECTORS = {
    "11": "Agriculture, Forestry, Fishing & Hunting",
    "21": "Mining, Quarrying & Oil/Gas Extraction",
    "22": "Utilities",
    "23": "Construction",
    "31": "Manufacturing - Food, Beverage, Textile, Apparel",
    "32": "Manufacturing - Wood, Paper, Petroleum, Chemical, Plastics",
    "33": "Manufacturing - Metals, Machinery, Electronics, Transport Equip",
    "42": "Wholesale Trade",
    "44": "Retail Trade - Motor Vehicles, Furniture, Electronics, Building",
    "45": "Retail Trade - Food, Health, Gasoline, Clothing, General Merch",
    "48": "Transportation - Air, Rail, Water, Truck, Transit, Pipeline",
    "49": "Transportation - Postal, Courier, Warehousing",
    "51": "Information",
    "52": "Finance and Insurance",
    "53": "Real Estate and Rental/Leasing",
    "54": "Professional, Scientific & Technical Services",
    "55": "Management of Companies",
    "56": "Administrative & Support Services",
    "61": "Educational Services",
    "62": "Health Care and Social Assistance",
    "71": "Arts, Entertainment & Recreation",
    "72": "Accommodation and Food Services",
    "81": "Other Services (except Public Admin)",
}


def _get_sector_from_industry_code(industry_code: str) -> tuple:
    """Extract sector code and name from NAICS industry code"""
    if not industry_code or len(industry_code) < 2:
        return None, None

    sector_code = industry_code[:2]
    sector_name = NAICS_SECTORS.get(sector_code, f"Sector {sector_code}")
    return sector_code, sector_name


def _get_period_name(year: int, period: str, db: Session) -> str:
    """Get human-readable period name"""
    period_info = db.query(BLSPeriod).filter(BLSPeriod.period_code == period).first()
    if period_info:
        return f"{period_info.period_name} {year}"

    # Fallback
    month_map = {
        'M01': 'January', 'M02': 'February', 'M03': 'March', 'M04': 'April',
        'M05': 'May', 'M06': 'June', 'M07': 'July', 'M08': 'August',
        'M09': 'September', 'M10': 'October', 'M11': 'November', 'M12': 'December',
        'M13': 'Annual Average'
    }
    return f"{month_map.get(period, period)} {year}"


def _calculate_ppi_metrics(series_id: str, name: str, db: Session) -> Optional[PCPriceMetric]:
    """Calculate PPI metrics for a series"""
    data = db.query(PCData).filter(
        PCData.series_id == series_id,
        PCData.period != 'M13'  # Exclude annual averages
    ).order_by(desc(PCData.year), desc(PCData.period)).limit(14).all()

    if not data:
        return None

    latest = data[0]
    prev_month = data[1] if len(data) > 1 else None
    prev_year = None

    # Find same month last year
    for d in data:
        if d.year == latest.year - 1 and d.period == latest.period:
            prev_year = d
            break

    latest_value = float(latest.value) if latest.value else None

    mom_change = None
    mom_pct = None
    if prev_month and prev_month.value and latest_value:
        prev_val = float(prev_month.value)
        mom_change = latest_value - prev_val
        mom_pct = (mom_change / prev_val) * 100 if prev_val != 0 else None

    yoy_change = None
    yoy_pct = None
    if prev_year and prev_year.value and latest_value:
        prev_val = float(prev_year.value)
        yoy_change = latest_value - prev_val
        yoy_pct = (yoy_change / prev_val) * 100 if prev_val != 0 else None

    return PCPriceMetric(
        series_id=series_id,
        name=name,
        latest_value=latest_value,
        latest_date=_get_period_name(latest.year, latest.period, db),
        month_over_month=round(mom_change, 3) if mom_change else None,
        month_over_month_pct=round(mom_pct, 2) if mom_pct else None,
        year_over_year=round(yoy_change, 3) if yoy_change else None,
        year_over_year_pct=round(yoy_pct, 2) if yoy_pct else None
    )


# ==================== Dimensions ====================

@router.get("/dimensions", response_model=PCDimensions)
def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get available dimensions for PC survey filtering"""

    # Get all industries
    industries = db.query(PCIndustry).order_by(PCIndustry.industry_code).all()

    industry_items = []
    sectors_set = {}

    for ind in industries:
        sector_code, sector_name = _get_sector_from_industry_code(ind.industry_code)
        industry_items.append(PCIndustryItem(
            industry_code=ind.industry_code,
            industry_name=ind.industry_name,
            sector=sector_code
        ))
        if sector_code and sector_code not in sectors_set:
            sectors_set[sector_code] = sector_name

    sectors = [{"code": k, "name": v} for k, v in sorted(sectors_set.items())]

    # Get distinct base years from series
    base_dates = db.query(PCSeries.base_date).distinct().all()
    base_years_set = set()
    for (bd,) in base_dates:
        if bd and len(bd) >= 4:
            try:
                year = int(bd[:4])
                base_years_set.add(year)
            except ValueError:
                pass
    base_years = sorted(base_years_set)

    # Get distinct start years from series
    start_years_result = db.query(PCSeries.begin_year).distinct().filter(
        PCSeries.begin_year.isnot(None)
    ).all()
    start_years = sorted([y for (y,) in start_years_result if y])

    return PCDimensions(
        industries=industry_items,
        sectors=sectors,
        base_years=base_years,
        start_years=start_years
    )


# ==================== Series ====================

@router.get("/series", response_model=PCSeriesListResponse)
def get_series(
    industry_code: Optional[str] = Query(None, description="Filter by exact industry code"),
    product_code: Optional[str] = Query(None, description="Filter by product code (requires industry_code)"),
    sector_code: Optional[str] = Query(None, description="Filter by sector (first 2 digits of NAICS)"),
    seasonal_code: Optional[str] = Query(None, description="S=Seasonally Adjusted, U=Not Adjusted"),
    base_date: Optional[str] = Query(None, description="Filter by base date (e.g., '198212', '200506')"),
    base_year: Optional[int] = Query(None, description="Filter by base year (e.g., 1982, 2005)"),
    min_start_year: Optional[int] = Query(None, description="Series must have data starting from this year or earlier"),
    active_only: bool = Query(True, description="Only return active series"),
    search: Optional[str] = Query(None, description="Search in series title, industry name, or product name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """List PC series with optional filters and search

    Supports three modes:
    1. Search: Use 'search' param to find series by keyword across title, industry, product
    2. Hierarchical: Use sector_code → industry_code → product_code for drill-down
    3. Browse: Use limit/offset for pagination through all series

    Additional filters:
    - base_date: Exact base period (e.g., '198212')
    - base_year: Filter by base year (matches any base_date starting with that year)
    - min_start_year: Series with data available from this year or earlier
    """

    # If searching, we need to join with industry and product tables
    if search:
        # Get matching industry codes
        matching_industries = db.query(PCIndustry.industry_code).filter(
            PCIndustry.industry_name.ilike(f"%{search}%")
        ).all()
        matching_industry_codes = [i[0] for i in matching_industries]

        # Get matching product codes
        matching_products = db.query(PCProduct.industry_code, PCProduct.product_code).filter(
            PCProduct.product_name.ilike(f"%{search}%")
        ).all()

        # Build query with OR conditions
        from sqlalchemy import or_
        search_conditions = [PCSeries.series_title.ilike(f"%{search}%")]

        if matching_industry_codes:
            search_conditions.append(PCSeries.industry_code.in_(matching_industry_codes))

        if matching_products:
            # Match industry_code + product_code pairs
            product_conditions = []
            for ind_code, prod_code in matching_products:
                product_conditions.append(
                    and_(PCSeries.industry_code == ind_code, PCSeries.product_code == prod_code)
                )
            if product_conditions:
                search_conditions.append(or_(*product_conditions))

        query = db.query(PCSeries).filter(or_(*search_conditions))
    else:
        query = db.query(PCSeries)

    # Apply filters
    if industry_code:
        query = query.filter(PCSeries.industry_code == industry_code)

    if product_code and industry_code:
        query = query.filter(PCSeries.product_code == product_code)

    if sector_code:
        query = query.filter(PCSeries.industry_code.like(f"{sector_code}%"))

    if seasonal_code:
        query = query.filter(PCSeries.seasonal_code == seasonal_code)

    if base_date:
        query = query.filter(PCSeries.base_date == base_date)

    if base_year:
        # Match base_date starting with the year (e.g., 1982 matches '198201', '198212', etc.)
        query = query.filter(PCSeries.base_date.like(f"{base_year}%"))

    if min_start_year:
        # Series must have data starting from this year or earlier
        query = query.filter(PCSeries.begin_year <= min_start_year)

    if active_only:
        query = query.filter(PCSeries.is_active == True)

    total = query.count()

    series = query.order_by(PCSeries.industry_code, PCSeries.product_code).offset(offset).limit(limit).all()

    # Get industry names
    industry_codes = list(set(s.industry_code for s in series if s.industry_code))
    industry_names = {}
    if industry_codes:
        industries = db.query(PCIndustry).filter(PCIndustry.industry_code.in_(industry_codes)).all()
        industry_names = {i.industry_code: i.industry_name for i in industries}

    # Get product names for the specific series we're returning
    product_keys = [(s.industry_code, s.product_code) for s in series if s.product_code]
    product_names = {}
    if product_keys:
        # Only fetch products for the industries we have
        products = db.query(PCProduct).filter(
            PCProduct.industry_code.in_(industry_codes)
        ).all()
        product_names = {(p.industry_code, p.product_code): p.product_name for p in products}

    series_list = [
        PCSeriesInfo(
            series_id=s.series_id,
            series_title=s.series_title,
            industry_code=s.industry_code,
            industry_name=industry_names.get(s.industry_code),
            product_code=s.product_code,
            product_name=product_names.get((s.industry_code, s.product_code)),
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

    return PCSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_list
    )


@router.get("/series/{series_id}/data", response_model=PCDataResponse)
def get_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    include_annual: bool = Query(False, description="Include annual averages (M13)"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get time series data for a specific PC series"""

    series = db.query(PCSeries).filter(PCSeries.series_id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    query = db.query(PCData).filter(PCData.series_id == series_id)

    if not include_annual:
        query = query.filter(PCData.period != 'M13')

    if start_year:
        query = query.filter(PCData.year >= start_year)

    if end_year:
        query = query.filter(PCData.year <= end_year)

    data = query.order_by(PCData.year, PCData.period).all()

    # Get industry and product names
    industry_name = "Unknown"
    if series.industry_code:
        industry = db.query(PCIndustry).filter(PCIndustry.industry_code == series.industry_code).first()
        if industry:
            industry_name = industry.industry_name

    product_name = None
    if series.product_code:
        product = db.query(PCProduct).filter(
            PCProduct.industry_code == series.industry_code,
            PCProduct.product_code == series.product_code
        ).first()
        if product:
            product_name = product.product_name

    data_points = [
        PCDataPoint(
            year=d.year,
            period=d.period,
            period_name=_get_period_name(d.year, d.period, db),
            value=float(d.value) if d.value else None,
            footnote_codes=d.footnote_codes
        )
        for d in data
    ]

    return PCDataResponse(
        series=[PCSeriesData(
            series_id=series.series_id,
            series_title=series.series_title,
            industry_name=industry_name,
            product_name=product_name,
            base_date=series.base_date,
            data_points=data_points
        )]
    )


# ==================== Overview ====================

@router.get("/overview", response_model=PCOverviewResponse)
def get_overview(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get PPI overview by major NAICS sectors

    Shows key sectors with their MoM% and YoY% price changes.
    This is Industry PPI (PC survey), not Final Demand PPI (WP survey).
    """

    # Get all industries and group by sector
    industries = db.query(PCIndustry).all()

    # Find one representative industry per sector (first one alphabetically)
    sector_industries = {}
    for ind in industries:
        sector_code, sector_name = _get_sector_from_industry_code(ind.industry_code)
        if sector_code and sector_code not in sector_industries:
            sector_industries[sector_code] = (ind.industry_code, sector_name)

    sectors = []
    last_updated = None

    for sector_code in sorted(sector_industries.keys()):
        industry_code, sector_name = sector_industries[sector_code]

        # Find an active series for this industry
        series = db.query(PCSeries).filter(
            PCSeries.industry_code == industry_code,
            PCSeries.is_active == True
        ).first()

        if not series:
            continue

        metric = _calculate_ppi_metrics(series.series_id, sector_name, db)
        if metric:
            sectors.append(PCSectorSummary(
                sector_code=sector_code,
                sector_name=sector_name,
                series_id=series.series_id,
                latest_date=metric.latest_date,
                mom_pct=metric.month_over_month_pct,
                yoy_pct=metric.year_over_year_pct,
                index_value=metric.latest_value
            ))
            if not last_updated:
                last_updated = metric.latest_date

    return PCOverviewResponse(
        sectors=sectors,
        last_updated=last_updated
    )


@router.get("/overview/timeline", response_model=PCOverviewTimelineResponse)
def get_overview_timeline(
    months_back: int = Query(24, ge=1, le=240, description="Number of months to look back"),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for overview charts - shows MoM % changes over time"""

    # Get all industries and find one per sector
    industries = db.query(PCIndustry).all()

    sector_industries = {}
    for ind in industries:
        sector_code, sector_name = _get_sector_from_industry_code(ind.industry_code)
        if sector_code and sector_code not in sector_industries:
            sector_industries[sector_code] = (ind.industry_code, sector_name)

    # Find series for each sector
    sector_series = {}
    sector_names = {}

    for sector_code, (industry_code, sector_name) in sector_industries.items():
        series = db.query(PCSeries).filter(
            PCSeries.industry_code == industry_code,
            PCSeries.is_active == True
        ).first()
        if series:
            sector_series[sector_code] = series.series_id
            sector_names[sector_code] = sector_name

    if not sector_series:
        return PCOverviewTimelineResponse(timeline=[], sector_names={})

    # Get data for all series
    all_series_ids = list(sector_series.values())

    data = db.query(PCData).filter(
        PCData.series_id.in_(all_series_ids),
        PCData.period != 'M13'
    ).order_by(desc(PCData.year), desc(PCData.period)).all()

    # Group by period and series
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {
                'year': d.year,
                'period': d.period,
                'period_name': _get_period_name(d.year, d.period, db),
                'values': {}
            }

        for sector_code, series_id in sector_series.items():
            if d.series_id == series_id:
                period_data[key]['values'][sector_code] = float(d.value) if d.value else None

    # Sort periods
    sorted_periods = sorted(period_data.keys(), reverse=True)[:months_back + 1]  # +1 for calculating first MoM
    sorted_periods.reverse()

    # Calculate MoM % changes for each period
    timeline = []
    for i, key in enumerate(sorted_periods):
        if i == 0:
            continue  # Skip first period (no prior month to compare)

        pd = period_data[key]
        prev_key = sorted_periods[i - 1]
        prev_pd = period_data.get(prev_key, {}).get('values', {})

        sectors_mom = {}
        for sector_code in sector_series.keys():
            current_val = pd['values'].get(sector_code)
            prev_val = prev_pd.get(sector_code)
            if current_val and prev_val and prev_val != 0:
                mom_pct = ((current_val - prev_val) / prev_val) * 100
                sectors_mom[sector_code] = round(mom_pct, 2)
            else:
                sectors_mom[sector_code] = None

        timeline.append(PCOverviewTimelinePoint(
            year=pd['year'],
            period=pd['period'],
            period_name=pd['period_name'],
            sectors=sectors_mom
        ))

    return PCOverviewTimelineResponse(
        timeline=timeline,
        sector_names=sector_names
    )


# ==================== Sector Analysis ====================

@router.get("/sectors", response_model=PCSectorAnalysisResponse)
def get_sectors(
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get PPI analysis by NAICS sector"""

    # Find one representative series per sector
    industries = db.query(PCIndustry).all()

    sector_industries = {}
    for ind in industries:
        sector_code, sector_name = _get_sector_from_industry_code(ind.industry_code)
        if sector_code and sector_code not in sector_industries:
            sector_industries[sector_code] = (ind.industry_code, sector_name)

    sectors = []
    last_updated = None

    for sector_code, (industry_code, sector_name) in sorted(sector_industries.items()):
        # Find an active series for this industry
        series = db.query(PCSeries).filter(
            PCSeries.industry_code == industry_code,
            PCSeries.is_active == True
        ).first()

        if not series:
            continue

        metric = _calculate_ppi_metrics(series.series_id, sector_name, db)
        if metric:
            sectors.append(PCSectorMetric(
                sector_code=sector_code,
                sector_name=sector_name,
                series_id=series.series_id,
                latest_value=metric.latest_value,
                latest_date=metric.latest_date,
                month_over_month=metric.month_over_month,
                month_over_month_pct=metric.month_over_month_pct,
                year_over_year=metric.year_over_year,
                year_over_year_pct=metric.year_over_year_pct
            ))
            if not last_updated:
                last_updated = metric.latest_date

    return PCSectorAnalysisResponse(
        sectors=sectors,
        last_updated=last_updated
    )


@router.get("/sectors/timeline", response_model=PCSectorTimelineResponse)
def get_sectors_timeline(
    sector_codes: str = Query(..., description="Comma-separated sector codes"),
    months_back: int = Query(24, ge=1, le=240),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for sector comparison"""

    codes = [c.strip() for c in sector_codes.split(",")]

    # Find series for each sector
    sector_series = {}
    sector_names = {}

    for code in codes:
        # Find first industry in this sector
        industry = db.query(PCIndustry).filter(
            PCIndustry.industry_code.like(f"{code}%")
        ).first()

        if not industry:
            continue

        series = db.query(PCSeries).filter(
            PCSeries.industry_code == industry.industry_code,
            PCSeries.is_active == True
        ).first()

        if series:
            sector_series[code] = series.series_id
            sector_names[code] = NAICS_SECTORS.get(code, f"Sector {code}")

    if not sector_series:
        return PCSectorTimelineResponse(timeline=[], sector_names={})

    # Get data
    all_series_ids = list(sector_series.values())

    data = db.query(PCData).filter(
        PCData.series_id.in_(all_series_ids),
        PCData.period != 'M13'
    ).order_by(desc(PCData.year), desc(PCData.period)).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {
                'year': d.year,
                'period': d.period,
                'period_name': _get_period_name(d.year, d.period, db),
                'sectors': {}
            }

        for code, series_id in sector_series.items():
            if d.series_id == series_id:
                period_data[key]['sectors'][code] = float(d.value) if d.value else None

    sorted_periods = sorted(period_data.keys(), reverse=True)[:months_back]
    sorted_periods.reverse()

    timeline = [
        PCSectorTimelinePoint(
            year=period_data[key]['year'],
            period=period_data[key]['period'],
            period_name=period_data[key]['period_name'],
            sectors=period_data[key]['sectors']
        )
        for key in sorted_periods
    ]

    return PCSectorTimelineResponse(
        timeline=timeline,
        sector_names=sector_names
    )


# ==================== Industry Analysis ====================

@router.get("/industries", response_model=PCIndustryAnalysisResponse)
def get_industries(
    sector_code: Optional[str] = Query(None, description="Filter by sector code"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get PPI analysis by industry"""

    query = db.query(PCIndustry)

    if sector_code:
        query = query.filter(PCIndustry.industry_code.like(f"{sector_code}%"))

    industries = query.order_by(PCIndustry.industry_code).limit(limit).all()
    total_count = query.count()

    industry_metrics = []
    last_updated = None

    for ind in industries:
        # Find an active series for this industry
        series = db.query(PCSeries).filter(
            PCSeries.industry_code == ind.industry_code,
            PCSeries.is_active == True
        ).first()

        if not series:
            continue

        metric = _calculate_ppi_metrics(series.series_id, ind.industry_name, db)
        if metric:
            industry_metrics.append(PCIndustryMetric(
                industry_code=ind.industry_code,
                industry_name=ind.industry_name,
                series_id=series.series_id,
                latest_value=metric.latest_value,
                latest_date=metric.latest_date,
                month_over_month=metric.month_over_month,
                month_over_month_pct=metric.month_over_month_pct,
                year_over_year=metric.year_over_year,
                year_over_year_pct=metric.year_over_year_pct
            ))
            if not last_updated:
                last_updated = metric.latest_date

    return PCIndustryAnalysisResponse(
        industries=industry_metrics,
        total_count=total_count,
        last_updated=last_updated
    )


@router.get("/industries/timeline", response_model=PCIndustryTimelineResponse)
def get_industries_timeline(
    industry_codes: str = Query(..., description="Comma-separated industry codes"),
    months_back: int = Query(24, ge=1, le=240),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for industry comparison"""

    codes = [c.strip() for c in industry_codes.split(",")]

    # Find series for each industry
    industry_series = {}
    industry_names = {}

    for code in codes:
        industry = db.query(PCIndustry).filter(PCIndustry.industry_code == code).first()
        if not industry:
            continue

        series = db.query(PCSeries).filter(
            PCSeries.industry_code == code,
            PCSeries.is_active == True
        ).first()

        if series:
            industry_series[code] = series.series_id
            industry_names[code] = industry.industry_name

    if not industry_series:
        return PCIndustryTimelineResponse(timeline=[], industry_names={})

    # Get data
    all_series_ids = list(industry_series.values())

    data = db.query(PCData).filter(
        PCData.series_id.in_(all_series_ids),
        PCData.period != 'M13'
    ).order_by(desc(PCData.year), desc(PCData.period)).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {
                'year': d.year,
                'period': d.period,
                'period_name': _get_period_name(d.year, d.period, db),
                'industries': {}
            }

        for code, series_id in industry_series.items():
            if d.series_id == series_id:
                period_data[key]['industries'][code] = float(d.value) if d.value else None

    sorted_periods = sorted(period_data.keys(), reverse=True)[:months_back]
    sorted_periods.reverse()

    timeline = [
        PCIndustryTimelinePoint(
            year=period_data[key]['year'],
            period=period_data[key]['period'],
            period_name=period_data[key]['period_name'],
            industries=period_data[key]['industries']
        )
        for key in sorted_periods
    ]

    return PCIndustryTimelineResponse(
        timeline=timeline,
        industry_names=industry_names
    )


# ==================== Product Analysis ====================

@router.get("/products/{industry_code}", response_model=PCProductAnalysisResponse)
def get_products(
    industry_code: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get PPI analysis for products within an industry"""

    industry = db.query(PCIndustry).filter(PCIndustry.industry_code == industry_code).first()
    if not industry:
        raise HTTPException(status_code=404, detail=f"Industry {industry_code} not found")

    products = db.query(PCProduct).filter(
        PCProduct.industry_code == industry_code
    ).order_by(PCProduct.product_code).limit(limit).all()

    total_count = db.query(PCProduct).filter(PCProduct.industry_code == industry_code).count()

    product_metrics = []
    last_updated = None

    for prod in products:
        # Find series for this product
        series = db.query(PCSeries).filter(
            PCSeries.industry_code == industry_code,
            PCSeries.product_code == prod.product_code,
            PCSeries.is_active == True
        ).first()

        if not series:
            continue

        metric = _calculate_ppi_metrics(series.series_id, prod.product_name, db)
        if metric:
            product_metrics.append(PCProductMetric(
                industry_code=industry_code,
                industry_name=industry.industry_name,
                product_code=prod.product_code,
                product_name=prod.product_name,
                series_id=series.series_id,
                latest_value=metric.latest_value,
                latest_date=metric.latest_date,
                month_over_month=metric.month_over_month,
                month_over_month_pct=metric.month_over_month_pct,
                year_over_year=metric.year_over_year,
                year_over_year_pct=metric.year_over_year_pct
            ))
            if not last_updated:
                last_updated = metric.latest_date

    return PCProductAnalysisResponse(
        industry_code=industry_code,
        industry_name=industry.industry_name,
        products=product_metrics,
        total_count=total_count,
        last_updated=last_updated
    )


@router.get("/products/{industry_code}/timeline", response_model=PCProductTimelineResponse)
def get_products_timeline(
    industry_code: str,
    product_codes: str = Query(..., description="Comma-separated product codes"),
    months_back: int = Query(24, ge=1, le=240),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get timeline data for product comparison within an industry"""

    industry = db.query(PCIndustry).filter(PCIndustry.industry_code == industry_code).first()
    if not industry:
        raise HTTPException(status_code=404, detail=f"Industry {industry_code} not found")

    codes = [c.strip() for c in product_codes.split(",")]

    # Find series for each product
    product_series = {}
    product_names = {}

    for code in codes:
        product = db.query(PCProduct).filter(
            PCProduct.industry_code == industry_code,
            PCProduct.product_code == code
        ).first()

        if not product:
            continue

        series = db.query(PCSeries).filter(
            PCSeries.industry_code == industry_code,
            PCSeries.product_code == code,
            PCSeries.is_active == True
        ).first()

        if series:
            product_series[code] = series.series_id
            product_names[code] = product.product_name

    if not product_series:
        return PCProductTimelineResponse(
            industry_code=industry_code,
            industry_name=industry.industry_name,
            timeline=[],
            product_names={}
        )

    # Get data
    all_series_ids = list(product_series.values())

    data = db.query(PCData).filter(
        PCData.series_id.in_(all_series_ids),
        PCData.period != 'M13'
    ).order_by(desc(PCData.year), desc(PCData.period)).all()

    # Group by period
    period_data = {}
    for d in data:
        key = (d.year, d.period)
        if key not in period_data:
            period_data[key] = {
                'year': d.year,
                'period': d.period,
                'period_name': _get_period_name(d.year, d.period, db),
                'products': {}
            }

        for code, series_id in product_series.items():
            if d.series_id == series_id:
                period_data[key]['products'][code] = float(d.value) if d.value else None

    sorted_periods = sorted(period_data.keys(), reverse=True)[:months_back]
    sorted_periods.reverse()

    timeline = [
        PCProductTimelinePoint(
            year=period_data[key]['year'],
            period=period_data[key]['period'],
            period_name=period_data[key]['period_name'],
            products=period_data[key]['products']
        )
        for key in sorted_periods
    ]

    return PCProductTimelineResponse(
        industry_code=industry_code,
        industry_name=industry.industry_name,
        timeline=timeline,
        product_names=product_names
    )


# ==================== Top Movers ====================

@router.get("/top-movers", response_model=PCTopMoversResponse)
def get_top_movers(
    period: str = Query("yoy", description="mom or yoy"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_data_db),
    current_user=Depends(get_current_user)
):
    """Get top price gainers and losers"""

    # Get active series with recent data
    series_list = db.query(PCSeries).filter(
        PCSeries.is_active == True
    ).limit(500).all()

    movers = []
    last_updated = None

    for series in series_list:
        metric = _calculate_ppi_metrics(series.series_id, "", db)
        if not metric:
            continue

        change_pct = metric.year_over_year_pct if period == "yoy" else metric.month_over_month_pct
        change = metric.year_over_year if period == "yoy" else metric.month_over_month

        if change_pct is None:
            continue

        industry = db.query(PCIndustry).filter(PCIndustry.industry_code == series.industry_code).first()
        product = None
        if series.product_code:
            product = db.query(PCProduct).filter(
                PCProduct.industry_code == series.industry_code,
                PCProduct.product_code == series.product_code
            ).first()

        movers.append(PCTopMover(
            series_id=series.series_id,
            industry_code=series.industry_code,
            industry_name=industry.industry_name if industry else "Unknown",
            product_code=series.product_code,
            product_name=product.product_name if product else None,
            latest_value=metric.latest_value,
            latest_date=metric.latest_date,
            change=change,
            change_pct=change_pct
        ))

        if not last_updated:
            last_updated = metric.latest_date

    # Sort by change percent
    movers.sort(key=lambda x: x.change_pct or 0, reverse=True)
    gainers = movers[:limit]

    movers.sort(key=lambda x: x.change_pct or 0)
    losers = movers[:limit]

    return PCTopMoversResponse(
        period=period,
        gainers=gainers,
        losers=losers,
        last_updated=last_updated
    )
