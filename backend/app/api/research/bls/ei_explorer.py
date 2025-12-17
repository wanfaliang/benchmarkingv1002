"""
EI (Import/Export Price Indexes) Explorer API

Provides endpoints for exploring international price index data including:
- Import/Export price indexes by BEA, NAICS, Harmonized System classifications
- Country/Region comparison (Locality of Origin/Destination)
- Services trade indexes
- Terms of Trade
- Trade flow visualizations

Data is monthly, updated monthly.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, or_, desc, asc, case, text
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import EIIndex, EISeries, EIData
from .ei_schemas import (
    EIDimensions, EIIndexItem, EICountryItem,
    EISeriesInfo, EISeriesListResponse,
    EIDataPoint, EISeriesData, EIDataResponse,
    EIOverviewMetric, EIOverviewResponse, EIOverviewTimelinePoint, EIOverviewTimelineResponse,
    EICountryComparisonItem, EICountryComparisonResponse, EICountryTimelinePoint, EICountryTimelineResponse,
    EITradeFlowItem, EITradeFlowResponse, EITradeBalanceItem, EITradeBalanceResponse,
    EITradeBalanceTimelinePoint, EITradeBalanceTimelineResponse,
    EIIndexCategoryItem, EIIndexCategoryResponse, EIIndexCategoryTimelinePoint, EIIndexCategoryTimelineResponse,
    EIServicesItem, EIServicesResponse, EIServicesTimelinePoint, EIServicesTimelineResponse,
    EITermsOfTradeItem, EITermsOfTradeResponse, EITermsOfTradeTimelinePoint, EITermsOfTradeTimelineResponse,
    EITrendPoint, EITrendResponse,
    EITopMoverItem, EITopMoversResponse
)

router = APIRouter(prefix="/api/research/bls/ei", tags=["BLS EI Research"])


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
        'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
        'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
        'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
        'M13': 'Annual', 'Q01': 'Q1', 'Q02': 'Q2', 'Q03': 'Q3',
        'Q04': 'Q4', 'Q05': 'Annual'
    }
    name = period_map.get(period, period)
    if year:
        return f"{year} {name}"
    return name


def extract_country_from_series(series_name: str) -> tuple:
    """Extract country/region and industry from series name"""
    if '-' in series_name:
        parts = series_name.split('-', 1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else None
    return series_name, None


# Index code categorization
IMPORT_INDEXES = ['IR', 'IZ', 'IP', 'IV', 'IC', 'CO']  # CO = import by origin
EXPORT_INDEXES = ['IQ', 'IY', 'ID', 'IH', 'IS', 'CD']  # CD = export by destination
SERVICES_INDEXES = ['IV', 'IH', 'IC', 'IS']
COUNTRY_INDEXES = ['CO', 'CD']

# Key series IDs for overview
KEY_IMPORT_SERIES = 'EIUIR'  # All imports
KEY_EXPORT_SERIES = 'EIUIQ'  # All exports
KEY_IMPORT_EX_FUEL = 'EIUIREXFUELS'  # Imports ex fuel
KEY_EXPORT_EX_FUEL = 'EIUIQEXFUELS'  # Exports ex fuel


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=EIDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering EI data"""
    # Get all indexes
    indexes = db.execute(
        select(EIIndex).order_by(EIIndex.index_code)
    ).scalars().all()

    index_items = []
    import_items = []
    export_items = []

    for idx in indexes:
        category = 'import' if idx.index_code in IMPORT_INDEXES else 'export' if idx.index_code in EXPORT_INDEXES else 'trade'
        item = EIIndexItem(
            index_code=idx.index_code,
            index_name=idx.index_name,
            category=category
        )
        index_items.append(item)
        if idx.index_code in IMPORT_INDEXES:
            import_items.append(item)
        elif idx.index_code in EXPORT_INDEXES:
            export_items.append(item)

    # Get countries for CO (import origin)
    origin_result = db.execute(text("""
        SELECT
            CASE
                WHEN series_name LIKE '%-%' THEN SPLIT_PART(series_name, '-', 1)
                ELSE series_name
            END as country,
            COUNT(*) as cnt
        FROM bls_ei_series
        WHERE index_code = 'CO'
        GROUP BY country
        ORDER BY country
    """)).fetchall()

    origin_countries = [
        EICountryItem(
            country_code=row[0].replace(' ', '').upper()[:10],
            country_name=row[0],
            index_code='CO',
            series_count=row[1]
        )
        for row in origin_result
    ]

    # Get countries for CD (export destination)
    dest_result = db.execute(text("""
        SELECT
            CASE
                WHEN series_name LIKE '%-%' THEN SPLIT_PART(series_name, '-', 1)
                ELSE series_name
            END as country,
            COUNT(*) as cnt
        FROM bls_ei_series
        WHERE index_code = 'CD'
        GROUP BY country
        ORDER BY country
    """)).fetchall()

    dest_countries = [
        EICountryItem(
            country_code=row[0].replace(' ', '').upper()[:10],
            country_name=row[0],
            index_code='CD',
            series_count=row[1]
        )
        for row in dest_result
    ]

    # Get available years
    years_result = db.execute(text("""
        SELECT DISTINCT year FROM bls_ei_data ORDER BY year DESC
    """)).fetchall()
    available_years = [row[0] for row in years_result]

    # Get available periods
    periods_result = db.execute(text("""
        SELECT DISTINCT period FROM bls_ei_data ORDER BY period
    """)).fetchall()
    available_periods = [row[0] for row in periods_result]

    return EIDimensions(
        indexes=index_items,
        import_indexes=import_items,
        export_indexes=export_items,
        origin_countries=origin_countries,
        destination_countries=dest_countries,
        available_years=available_years,
        available_periods=available_periods
    )


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================

@router.get("/series", response_model=EISeriesListResponse)
async def get_series(
    index_code: Optional[str] = Query(None, description="Filter by index code (IR, IQ, CO, CD, etc.)"),
    search: Optional[str] = Query(None, description="Search in series name/title"),
    country: Optional[str] = Query(None, description="Filter by country/region name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_data_db)
):
    """Get list of EI series with filters"""
    query = select(EISeries, EIIndex.index_name).join(
        EIIndex, EISeries.index_code == EIIndex.index_code, isouter=True
    )

    conditions = []
    if index_code:
        conditions.append(EISeries.index_code == index_code)
    if search:
        search_pattern = f"%{search}%"
        conditions.append(or_(
            EISeries.series_name.ilike(search_pattern),
            EISeries.series_title.ilike(search_pattern)
        ))
    if country:
        country_pattern = f"{country}%"
        conditions.append(EISeries.series_name.ilike(country_pattern))

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(EISeries)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = db.execute(count_query).scalar()

    # Get series with pagination
    query = query.order_by(EISeries.index_code, EISeries.series_name).limit(limit).offset(offset)
    results = db.execute(query).fetchall()

    series = []
    for row in results:
        s = row[0]
        country, industry = extract_country_from_series(s.series_name or '')
        series.append(EISeriesInfo(
            series_id=s.series_id,
            seasonal_code=s.seasonal_code,
            index_code=s.index_code,
            index_name=row[1],
            series_name=s.series_name,
            base_period=s.base_period,
            series_title=s.series_title,
            footnote_codes=s.footnote_codes,
            begin_year=s.begin_year,
            begin_period=s.begin_period,
            end_year=s.end_year,
            end_period=s.end_period,
            is_active=s.is_active,
            country_region=country,
            industry_category=industry
        ))

    return EISeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series
    )


@router.get("/series/{series_id}", response_model=EISeriesInfo)
async def get_series_by_id(series_id: str, db: Session = Depends(get_data_db)):
    """Get a specific series by ID"""
    result = db.execute(
        select(EISeries, EIIndex.index_name).join(
            EIIndex, EISeries.index_code == EIIndex.index_code, isouter=True
        ).where(EISeries.series_id == series_id)
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    s = result[0]
    country, industry = extract_country_from_series(s.series_name or '')
    return EISeriesInfo(
        series_id=s.series_id,
        seasonal_code=s.seasonal_code,
        index_code=s.index_code,
        index_name=result[1],
        series_name=s.series_name,
        base_period=s.base_period,
        series_title=s.series_title,
        footnote_codes=s.footnote_codes,
        begin_year=s.begin_year,
        begin_period=s.begin_period,
        end_year=s.end_year,
        end_period=s.end_period,
        is_active=s.is_active,
        country_region=country,
        industry_category=industry
    )


# ============================================================================
# DATA ENDPOINTS
# ============================================================================

@router.get("/data", response_model=EIDataResponse)
async def get_data(
    series_ids: str = Query(..., description="Comma-separated series IDs"),
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get time series data for multiple series"""
    ids = [s.strip() for s in series_ids.split(',')]

    # Get series info
    series_query = select(EISeries, EIIndex.index_name).join(
        EIIndex, EISeries.index_code == EIIndex.index_code, isouter=True
    ).where(EISeries.series_id.in_(ids))
    series_results = db.execute(series_query).fetchall()
    series_map = {}
    for row in series_results:
        s = row[0]
        country, industry = extract_country_from_series(s.series_name or '')
        series_map[s.series_id] = EISeriesInfo(
            series_id=s.series_id,
            seasonal_code=s.seasonal_code,
            index_code=s.index_code,
            index_name=row[1],
            series_name=s.series_name,
            base_period=s.base_period,
            series_title=s.series_title,
            begin_year=s.begin_year,
            end_year=s.end_year,
            country_region=country,
            industry_category=industry
        )

    # Get data
    data_query = select(EIData).where(EIData.series_id.in_(ids))
    if start_year:
        data_query = data_query.where(EIData.year >= start_year)
    if end_year:
        data_query = data_query.where(EIData.year <= end_year)
    data_query = data_query.order_by(EIData.series_id, EIData.year, EIData.period)
    data_results = db.execute(data_query).scalars().all()

    # Group by series
    series_data: Dict[str, List[EIDataPoint]] = {sid: [] for sid in ids}
    for d in data_results:
        if d.series_id in series_data:
            series_data[d.series_id].append(EIDataPoint(
                year=d.year,
                period=d.period,
                period_name=get_period_name(d.period, d.year),
                value=decimal_to_float(d.value),
                footnote_codes=d.footnote_codes
            ))

    result_series = []
    total_obs = 0
    for sid in ids:
        if sid in series_map:
            points = series_data.get(sid, [])
            total_obs += len(points)
            result_series.append(EISeriesData(
                series_id=sid,
                series_info=series_map[sid],
                data_points=points
            ))

    return EIDataResponse(
        series_count=len(result_series),
        total_observations=total_obs,
        series=result_series
    )


# ============================================================================
# OVERVIEW ENDPOINTS
# ============================================================================

@router.get("/overview", response_model=EIOverviewResponse)
async def get_overview(
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get overview of import/export price indexes"""
    # Get latest period if not specified
    if not year or not period:
        latest = db.execute(text("""
            SELECT year, period FROM bls_ei_data
            WHERE period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 1
        """)).fetchone()
        if latest:
            year = latest[0]
            period = latest[1]

    # Get previous period for comparison
    prev_result = db.execute(text("""
        SELECT year, period FROM bls_ei_data
        WHERE (year < :year OR (year = :year AND period < :period))
        AND period != 'M13'
        ORDER BY year DESC, period DESC LIMIT 1
    """), {"year": year, "period": period}).fetchone()
    prev_year, prev_period = prev_result if prev_result else (None, None)

    # Get year-ago period
    yoy_year = year - 1

    def get_metric(series_id: str, metric_name: str) -> EIOverviewMetric:
        """Get metric data for a series"""
        # Current value
        current = db.execute(text("""
            SELECT d.value, s.index_code FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE d.series_id = :sid AND d.year = :year AND d.period = :period
        """), {"sid": series_id, "year": year, "period": period}).fetchone()

        # Previous value
        previous = None
        if prev_year and prev_period:
            prev_row = db.execute(text("""
                SELECT value FROM bls_ei_data
                WHERE series_id = :sid AND year = :year AND period = :period
            """), {"sid": series_id, "year": prev_year, "period": prev_period}).fetchone()
            previous = decimal_to_float(prev_row[0]) if prev_row else None

        # YoY value
        yoy_row = db.execute(text("""
            SELECT value FROM bls_ei_data
            WHERE series_id = :sid AND year = :year AND period = :period
        """), {"sid": series_id, "year": yoy_year, "period": period}).fetchone()
        yoy_value = decimal_to_float(yoy_row[0]) if yoy_row else None

        current_val = decimal_to_float(current[0]) if current else None
        index_code = current[1] if current else None

        mom_change = None
        yoy_change = None
        yoy_pct = None

        if current_val is not None and previous is not None:
            mom_change = current_val - previous
        if current_val is not None and yoy_value is not None:
            yoy_change = current_val - yoy_value
            if yoy_value != 0:
                yoy_pct = ((current_val - yoy_value) / yoy_value) * 100

        return EIOverviewMetric(
            metric_name=metric_name,
            series_id=series_id,
            index_code=index_code or '',
            current_value=current_val,
            previous_value=previous,
            mom_change=mom_change,
            yoy_change=yoy_change,
            yoy_pct_change=yoy_pct
        )

    # Get key metrics
    all_imports = get_metric(KEY_IMPORT_SERIES, "All Imports")
    all_exports = get_metric(KEY_EXPORT_SERIES, "All Exports")
    imports_ex_fuel = get_metric(KEY_IMPORT_EX_FUEL, "Imports ex Fuel")
    exports_ex_fuel = get_metric(KEY_EXPORT_EX_FUEL, "Exports ex Fuel")

    # Terms of trade
    terms = None
    terms_series = db.execute(text("""
        SELECT series_id FROM bls_ei_series WHERE index_code = 'CT' LIMIT 1
    """)).fetchone()
    if terms_series:
        terms = get_metric(terms_series[0], "Terms of Trade")

    # Get available years and periods
    years_result = db.execute(text("SELECT DISTINCT year FROM bls_ei_data ORDER BY year DESC")).fetchall()
    periods_result = db.execute(text("""
        SELECT DISTINCT period FROM bls_ei_data WHERE period != 'M13' ORDER BY period
    """)).fetchall()

    return EIOverviewResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        all_imports=all_imports,
        all_exports=all_exports,
        imports_ex_fuel=imports_ex_fuel,
        exports_ex_fuel=exports_ex_fuel,
        terms_of_trade=terms,
        import_metrics=[all_imports, imports_ex_fuel] if all_imports.current_value else [],
        export_metrics=[all_exports, exports_ex_fuel] if all_exports.current_value else [],
        available_years=[row[0] for row in years_result],
        available_periods=[row[0] for row in periods_result]
    )


@router.get("/overview/timeline", response_model=EIOverviewTimelineResponse)
async def get_overview_timeline(
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for overview chart"""
    conditions = "WHERE d.period != 'M13'"
    if start_year:
        conditions += f" AND d.year >= {start_year}"

    # Get data for key series
    result = db.execute(text(f"""
        SELECT d.series_id, d.year, d.period, d.value
        FROM bls_ei_data d
        {conditions}
        AND d.series_id IN ('{KEY_IMPORT_SERIES}', '{KEY_EXPORT_SERIES}',
                           '{KEY_IMPORT_EX_FUEL}', '{KEY_EXPORT_EX_FUEL}')
        ORDER BY d.year, d.period
    """)).fetchall()

    # Pivot data
    timeline_map: Dict[str, Dict[str, Optional[float]]] = {}
    for row in result:
        key = f"{row[1]}-{row[2]}"
        if key not in timeline_map:
            timeline_map[key] = {
                'year': row[1], 'period': row[2],
                'all_imports': None, 'all_exports': None,
                'imports_ex_fuel': None, 'exports_ex_fuel': None
            }
        val = decimal_to_float(row[3])
        if row[0] == KEY_IMPORT_SERIES:
            timeline_map[key]['all_imports'] = val
        elif row[0] == KEY_EXPORT_SERIES:
            timeline_map[key]['all_exports'] = val
        elif row[0] == KEY_IMPORT_EX_FUEL:
            timeline_map[key]['imports_ex_fuel'] = val
        elif row[0] == KEY_EXPORT_EX_FUEL:
            timeline_map[key]['exports_ex_fuel'] = val

    # Get terms of trade if available
    terms_series = db.execute(text("""
        SELECT series_id FROM bls_ei_series WHERE index_code = 'CT' LIMIT 1
    """)).fetchone()
    if terms_series:
        # Convert WHERE to AND for additional conditions
        terms_conditions = conditions.replace('d.', '').replace('WHERE', 'AND')
        terms_result = db.execute(text(f"""
            SELECT year, period, value FROM bls_ei_data
            WHERE series_id = :sid {terms_conditions}
            ORDER BY year, period
        """), {"sid": terms_series[0]}).fetchall()
        for row in terms_result:
            key = f"{row[0]}-{row[1]}"
            if key in timeline_map:
                timeline_map[key]['terms_of_trade'] = decimal_to_float(row[2])

    data = [
        EIOverviewTimelinePoint(
            year=v['year'],
            period=v['period'],
            period_name=get_period_name(v['period'], v['year']),
            all_imports=v.get('all_imports'),
            all_exports=v.get('all_exports'),
            imports_ex_fuel=v.get('imports_ex_fuel'),
            exports_ex_fuel=v.get('exports_ex_fuel'),
            terms_of_trade=v.get('terms_of_trade')
        )
        for v in sorted(timeline_map.values(), key=lambda x: (x['year'], x['period']))
    ]

    return EIOverviewTimelineResponse(data=data)


# ============================================================================
# COUNTRY COMPARISON ENDPOINTS
# ============================================================================

@router.get("/countries/comparison", response_model=EICountryComparisonResponse)
async def get_country_comparison(
    direction: str = Query("import", description="'import' (CO) or 'export' (CD)"),
    industry: Optional[str] = Query("All Industries", description="Industry filter"),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Compare price indexes across countries/regions"""
    index_code = 'CO' if direction == 'import' else 'CD'

    # Get latest period if not specified
    if not year or not period:
        latest = db.execute(text("""
            SELECT d.year, d.period FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx AND d.period != 'M13'
            ORDER BY d.year DESC, d.period DESC LIMIT 1
        """), {"idx": index_code}).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    # Build industry filter
    industry_filter = ""
    if industry and industry != "All Industries":
        industry_filter = f"AND s.series_name LIKE '%-{industry}%'"
    else:
        industry_filter = "AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')"

    # Get current data
    query = text(f"""
        SELECT
            SPLIT_PART(s.series_name, '-', 1) as country,
            d.value,
            s.series_id
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx
        AND d.year = :year AND d.period = :period
        {industry_filter}
        ORDER BY country
    """)
    current_data = db.execute(query, {"idx": index_code, "year": year, "period": period}).fetchall()

    # Get previous month data
    prev_result = db.execute(text("""
        SELECT year, period FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx
        AND (d.year < :year OR (d.year = :year AND d.period < :period))
        AND d.period != 'M13'
        ORDER BY d.year DESC, d.period DESC LIMIT 1
    """), {"idx": index_code, "year": year, "period": period}).fetchone()

    prev_map = {}
    if prev_result:
        prev_data = db.execute(text(f"""
            SELECT
                SPLIT_PART(s.series_name, '-', 1) as country,
                d.value
            FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx
            AND d.year = :year AND d.period = :period
            {industry_filter}
        """), {"idx": index_code, "year": prev_result[0], "period": prev_result[1]}).fetchall()
        prev_map = {row[0]: decimal_to_float(row[1]) for row in prev_data}

    # Get YoY data
    yoy_map = {}
    yoy_data = db.execute(text(f"""
        SELECT
            SPLIT_PART(s.series_name, '-', 1) as country,
            d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx
        AND d.year = :year AND d.period = :period
        {industry_filter}
    """), {"idx": index_code, "year": year - 1, "period": period}).fetchall()
    yoy_map = {row[0]: decimal_to_float(row[1]) for row in yoy_data}

    countries = []
    for row in current_data:
        country = row[0]
        current_val = decimal_to_float(row[1])
        prev_val = prev_map.get(country)
        yoy_val = yoy_map.get(country)

        mom_change = None
        yoy_change = None
        yoy_pct = None

        if current_val is not None and prev_val is not None:
            mom_change = current_val - prev_val
        if current_val is not None and yoy_val is not None:
            yoy_change = current_val - yoy_val
            if yoy_val != 0:
                yoy_pct = ((current_val - yoy_val) / yoy_val) * 100

        countries.append(EICountryComparisonItem(
            country_code=country.replace(' ', '').upper()[:10],
            country_name=country,
            current_value=current_val,
            previous_value=prev_val,
            mom_change=mom_change,
            yoy_change=yoy_change,
            yoy_pct_change=yoy_pct
        ))

    return EICountryComparisonResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        direction=direction,
        industry_filter=industry,
        countries=countries
    )


@router.get("/countries/timeline", response_model=EICountryTimelineResponse)
async def get_country_timeline(
    country_codes: str = Query(..., description="Comma-separated country names"),
    direction: str = Query("import", description="'import' (CO) or 'export' (CD)"),
    industry: Optional[str] = Query("All Industries"),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for country comparison"""
    countries = [c.strip() for c in country_codes.split(',')]
    index_code = 'CO' if direction == 'import' else 'CD'

    # Build industry filter
    industry_filter = ""
    if industry and industry != "All Industries":
        industry_filter = f"AND s.series_name LIKE '%-{industry}%'"
    else:
        industry_filter = "AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')"

    # Build country filter
    country_conditions = " OR ".join([f"s.series_name LIKE '{c}-%'" for c in countries])

    year_filter = f"AND d.year >= {start_year}" if start_year else ""

    query = text(f"""
        SELECT
            SPLIT_PART(s.series_name, '-', 1) as country,
            d.year, d.period, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx
        AND ({country_conditions})
        AND d.period != 'M13'
        {industry_filter}
        {year_filter}
        ORDER BY d.year, d.period, country
    """)
    results = db.execute(query, {"idx": index_code}).fetchall()

    # Pivot data
    timeline_map: Dict[str, Dict[str, Optional[float]]] = {}
    for row in results:
        key = f"{row[1]}-{row[2]}"
        if key not in timeline_map:
            timeline_map[key] = {'year': row[1], 'period': row[2], 'values': {}}
        timeline_map[key]['values'][row[0]] = decimal_to_float(row[3])

    data = [
        EICountryTimelinePoint(
            year=v['year'],
            period=v['period'],
            period_name=get_period_name(v['period'], v['year']),
            values=v['values']
        )
        for v in sorted(timeline_map.values(), key=lambda x: (x['year'], x['period']))
    ]

    country_items = [
        EICountryItem(
            country_code=c.replace(' ', '').upper()[:10],
            country_name=c,
            index_code=index_code
        )
        for c in countries
    ]

    return EICountryTimelineResponse(
        direction=direction,
        industry_filter=industry,
        countries=country_items,
        data=data
    )


# ============================================================================
# TRADE FLOW ENDPOINTS (Special Graph)
# ============================================================================

@router.get("/trade-flow", response_model=EITradeFlowResponse)
async def get_trade_flow(
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get trade flow data for visualization (imports and exports by country)"""
    # Get latest period if not specified
    if not year or not period:
        latest = db.execute(text("""
            SELECT year, period FROM bls_ei_data
            WHERE period != 'M13' ORDER BY year DESC, period DESC LIMIT 1
        """)).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    # Get import data (CO - Locality of Origin)
    import_query = text("""
        SELECT
            SPLIT_PART(s.series_name, '-', 1) as country,
            d.value,
            s.series_id
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CO'
        AND d.year = :year AND d.period = :period
        AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')
        ORDER BY d.value DESC
    """)
    import_data = db.execute(import_query, {"year": year, "period": period}).fetchall()

    # Get export data (CD - Locality of Destination)
    export_query = text("""
        SELECT
            SPLIT_PART(s.series_name, '-', 1) as country,
            d.value,
            s.series_id
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CD'
        AND d.year = :year AND d.period = :period
        AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')
        ORDER BY d.value DESC
    """)
    export_data = db.execute(export_query, {"year": year, "period": period}).fetchall()

    # Get YoY data for changes
    import_yoy = {}
    export_yoy = {}
    yoy_year = year - 1

    import_yoy_data = db.execute(text("""
        SELECT SPLIT_PART(s.series_name, '-', 1) as country, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CO' AND d.year = :year AND d.period = :period
        AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')
    """), {"year": yoy_year, "period": period}).fetchall()
    import_yoy = {row[0]: decimal_to_float(row[1]) for row in import_yoy_data}

    export_yoy_data = db.execute(text("""
        SELECT SPLIT_PART(s.series_name, '-', 1) as country, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CD' AND d.year = :year AND d.period = :period
        AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')
    """), {"year": yoy_year, "period": period}).fetchall()
    export_yoy = {row[0]: decimal_to_float(row[1]) for row in export_yoy_data}

    imports = []
    total_import = 0
    for row in import_data:
        val = decimal_to_float(row[1])
        if val:
            total_import += val
        yoy_val = import_yoy.get(row[0])
        change = (val - yoy_val) if val and yoy_val else None
        imports.append(EITradeFlowItem(
            country_code=row[0].replace(' ', '').upper()[:10],
            country_name=row[0],
            direction='import',
            value=val,
            change=change
        ))

    exports = []
    total_export = 0
    for row in export_data:
        val = decimal_to_float(row[1])
        if val:
            total_export += val
        yoy_val = export_yoy.get(row[0])
        change = (val - yoy_val) if val and yoy_val else None
        exports.append(EITradeFlowItem(
            country_code=row[0].replace(' ', '').upper()[:10],
            country_name=row[0],
            direction='export',
            value=val,
            change=change
        ))

    # Calculate percentage of total
    for item in imports:
        if item.value and total_import > 0:
            item.pct_of_total = (item.value / total_import) * 100
    for item in exports:
        if item.value and total_export > 0:
            item.pct_of_total = (item.value / total_export) * 100

    # Get overall indexes
    total_import_idx = db.execute(text("""
        SELECT value FROM bls_ei_data WHERE series_id = :sid AND year = :year AND period = :period
    """), {"sid": KEY_IMPORT_SERIES, "year": year, "period": period}).fetchone()

    total_export_idx = db.execute(text("""
        SELECT value FROM bls_ei_data WHERE series_id = :sid AND year = :year AND period = :period
    """), {"sid": KEY_EXPORT_SERIES, "year": year, "period": period}).fetchone()

    # Terms of trade
    terms_series = db.execute(text("""
        SELECT series_id FROM bls_ei_series WHERE index_code = 'CT' LIMIT 1
    """)).fetchone()
    terms_val = None
    if terms_series:
        terms_result = db.execute(text("""
            SELECT value FROM bls_ei_data WHERE series_id = :sid AND year = :year AND period = :period
        """), {"sid": terms_series[0], "year": year, "period": period}).fetchone()
        terms_val = decimal_to_float(terms_result[0]) if terms_result else None

    return EITradeFlowResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        imports=imports,
        exports=exports,
        total_import_index=decimal_to_float(total_import_idx[0]) if total_import_idx else None,
        total_export_index=decimal_to_float(total_export_idx[0]) if total_export_idx else None,
        terms_of_trade=terms_val
    )


@router.get("/trade-balance", response_model=EITradeBalanceResponse)
async def get_trade_balance(
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get trade balance (price differential) by country"""
    # Get latest period
    if not year or not period:
        latest = db.execute(text("""
            SELECT year, period FROM bls_ei_data
            WHERE period != 'M13' ORDER BY year DESC, period DESC LIMIT 1
        """)).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    # Get import data by country
    import_data = db.execute(text("""
        SELECT SPLIT_PART(s.series_name, '-', 1) as country, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CO' AND d.year = :year AND d.period = :period
        AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')
    """), {"year": year, "period": period}).fetchall()
    import_map = {row[0]: decimal_to_float(row[1]) for row in import_data}

    # Get export data by country
    export_data = db.execute(text("""
        SELECT SPLIT_PART(s.series_name, '-', 1) as country, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CD' AND d.year = :year AND d.period = :period
        AND (s.series_name LIKE '%-All Industries%' OR s.series_name LIKE '%Tot%')
    """), {"year": year, "period": period}).fetchall()
    export_map = {row[0]: decimal_to_float(row[1]) for row in export_data}

    # Combine for countries that have both
    all_countries = set(import_map.keys()) | set(export_map.keys())
    countries = []
    for country in sorted(all_countries):
        imp = import_map.get(country)
        exp = export_map.get(country)
        diff = None
        if imp is not None and exp is not None:
            diff = exp - imp

        countries.append(EITradeBalanceItem(
            country_code=country.replace(' ', '').upper()[:10],
            country_name=country,
            import_index=imp,
            export_index=exp,
            price_differential=diff
        ))

    return EITradeBalanceResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        countries=countries
    )


@router.get("/trade-balance/timeline", response_model=EITradeBalanceTimelineResponse)
async def get_trade_balance_timeline(
    country: str = Query(..., description="Country name"),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get trade balance timeline for a specific country"""
    year_filter = f"AND d.year >= {start_year}" if start_year else ""

    # Get import data
    import_query = text(f"""
        SELECT d.year, d.period, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CO'
        AND s.series_name LIKE :country
        AND d.period != 'M13'
        {year_filter}
        ORDER BY d.year, d.period
    """)
    import_data = db.execute(import_query, {"country": f"{country}-%All Industries%"}).fetchall()
    if not import_data:
        import_data = db.execute(import_query, {"country": f"{country}%Tot%"}).fetchall()

    import_map = {f"{r[0]}-{r[1]}": decimal_to_float(r[2]) for r in import_data}

    # Get export data
    export_query = text(f"""
        SELECT d.year, d.period, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CD'
        AND s.series_name LIKE :country
        AND d.period != 'M13'
        {year_filter}
        ORDER BY d.year, d.period
    """)
    export_data = db.execute(export_query, {"country": f"{country}-%All Industries%"}).fetchall()
    if not export_data:
        export_data = db.execute(export_query, {"country": f"{country}%Tot%"}).fetchall()

    export_map = {f"{r[0]}-{r[1]}": decimal_to_float(r[2]) for r in export_data}

    # Combine
    all_periods = set(import_map.keys()) | set(export_map.keys())
    data = []
    for key in sorted(all_periods):
        parts = key.split('-')
        year, period = int(parts[0]), parts[1]
        imp = import_map.get(key)
        exp = export_map.get(key)
        diff = (exp - imp) if imp is not None and exp is not None else None

        data.append(EITradeBalanceTimelinePoint(
            year=year,
            period=period,
            period_name=get_period_name(period, year),
            import_index=imp,
            export_index=exp,
            differential=diff
        ))

    return EITradeBalanceTimelineResponse(
        country_code=country.replace(' ', '').upper()[:10],
        country_name=country,
        data=data
    )


# ============================================================================
# INDEX CATEGORY ENDPOINTS
# ============================================================================

@router.get("/categories", response_model=EIIndexCategoryResponse)
async def get_index_categories(
    direction: str = Query("import", description="'import' or 'export'"),
    classification: str = Query("BEA", description="'BEA', 'NAICS', or 'Harmonized'"),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get index categories by classification system"""
    # Map classification to index codes
    index_map = {
        ('import', 'BEA'): 'IR',
        ('export', 'BEA'): 'IQ',
        ('import', 'NAICS'): 'IZ',
        ('export', 'NAICS'): 'IY',
        ('import', 'Harmonized'): 'IP',
        ('export', 'Harmonized'): 'ID',
    }
    index_code = index_map.get((direction, classification), 'IR')

    # Get latest period
    if not year or not period:
        latest = db.execute(text("""
            SELECT d.year, d.period FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx AND d.period != 'M13'
            ORDER BY d.year DESC, d.period DESC LIMIT 1
        """), {"idx": index_code}).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    # Get current data
    current_data = db.execute(text("""
        SELECT s.series_id, s.series_name, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx AND d.year = :year AND d.period = :period
        ORDER BY s.series_name
    """), {"idx": index_code, "year": year, "period": period}).fetchall()

    # Get previous month
    prev_result = db.execute(text("""
        SELECT d.year, d.period FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx
        AND (d.year < :year OR (d.year = :year AND d.period < :period))
        AND d.period != 'M13'
        ORDER BY d.year DESC, d.period DESC LIMIT 1
    """), {"idx": index_code, "year": year, "period": period}).fetchone()

    prev_map = {}
    if prev_result:
        prev_data = db.execute(text("""
            SELECT s.series_id, d.value
            FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx AND d.year = :year AND d.period = :period
        """), {"idx": index_code, "year": prev_result[0], "period": prev_result[1]}).fetchall()
        prev_map = {row[0]: decimal_to_float(row[1]) for row in prev_data}

    # Get YoY
    yoy_data = db.execute(text("""
        SELECT s.series_id, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = :idx AND d.year = :year AND d.period = :period
    """), {"idx": index_code, "year": year - 1, "period": period}).fetchall()
    yoy_map = {row[0]: decimal_to_float(row[1]) for row in yoy_data}

    categories = []
    for row in current_data:
        current_val = decimal_to_float(row[2])
        prev_val = prev_map.get(row[0])
        yoy_val = yoy_map.get(row[0])

        mom_change = (current_val - prev_val) if current_val and prev_val else None
        yoy_change = (current_val - yoy_val) if current_val and yoy_val else None

        categories.append(EIIndexCategoryItem(
            series_id=row[0],
            series_name=row[1],
            index_code=index_code,
            current_value=current_val,
            mom_change=mom_change,
            yoy_change=yoy_change
        ))

    return EIIndexCategoryResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        direction=direction,
        classification=classification,
        categories=categories
    )


@router.get("/categories/timeline", response_model=EIIndexCategoryTimelineResponse)
async def get_index_category_timeline(
    series_ids: str = Query(..., description="Comma-separated series IDs"),
    direction: str = Query("import"),
    classification: str = Query("BEA"),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get timeline for index categories"""
    ids = [s.strip() for s in series_ids.split(',')]
    year_filter = f"AND d.year >= {start_year}" if start_year else ""

    # Get series info
    series_info = db.execute(
        select(EISeries).where(EISeries.series_id.in_(ids))
    ).scalars().all()
    series_list = [
        EISeriesInfo(
            series_id=s.series_id,
            series_name=s.series_name,
            index_code=s.index_code,
            base_period=s.base_period
        )
        for s in series_info
    ]

    # Get data
    placeholders = ','.join([f"'{sid}'" for sid in ids])
    result = db.execute(text(f"""
        SELECT series_id, year, period, value
        FROM bls_ei_data
        WHERE series_id IN ({placeholders})
        AND period != 'M13'
        {year_filter}
        ORDER BY year, period
    """)).fetchall()

    # Pivot
    timeline_map: Dict[str, Dict[str, Optional[float]]] = {}
    for row in result:
        key = f"{row[1]}-{row[2]}"
        if key not in timeline_map:
            timeline_map[key] = {'year': row[1], 'period': row[2], 'values': {}}
        timeline_map[key]['values'][row[0]] = decimal_to_float(row[3])

    data = [
        EIIndexCategoryTimelinePoint(
            year=v['year'],
            period=v['period'],
            period_name=get_period_name(v['period'], v['year']),
            values=v['values']
        )
        for v in sorted(timeline_map.values(), key=lambda x: (x['year'], x['period']))
    ]

    return EIIndexCategoryTimelineResponse(
        direction=direction,
        classification=classification,
        series=series_list,
        data=data
    )


# ============================================================================
# SERVICES ENDPOINTS
# ============================================================================

@router.get("/services", response_model=EIServicesResponse)
async def get_services(
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get services trade indexes"""
    # Get latest period
    if not year or not period:
        latest = db.execute(text("""
            SELECT d.year, d.period FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code IN ('IV', 'IH', 'IC', 'IS') AND d.period != 'M13'
            ORDER BY d.year DESC, d.period DESC LIMIT 1
        """)).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    def get_services_by_code(idx_code: str, direction: str) -> List[EIServicesItem]:
        data = db.execute(text("""
            SELECT s.series_id, s.series_name, d.value
            FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx AND d.year = :year AND d.period = :period
            ORDER BY s.series_name
        """), {"idx": idx_code, "year": year, "period": period}).fetchall()

        prev_result = db.execute(text("""
            SELECT d.year, d.period FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx
            AND (d.year < :year OR (d.year = :year AND d.period < :period))
            AND d.period != 'M13'
            ORDER BY d.year DESC, d.period DESC LIMIT 1
        """), {"idx": idx_code, "year": year, "period": period}).fetchone()

        prev_map = {}
        if prev_result:
            prev_data = db.execute(text("""
                SELECT s.series_id, d.value FROM bls_ei_data d
                JOIN bls_ei_series s ON d.series_id = s.series_id
                WHERE s.index_code = :idx AND d.year = :year AND d.period = :period
            """), {"idx": idx_code, "year": prev_result[0], "period": prev_result[1]}).fetchall()
            prev_map = {row[0]: decimal_to_float(row[1]) for row in prev_data}

        yoy_data = db.execute(text("""
            SELECT s.series_id, d.value FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = :idx AND d.year = :year AND d.period = :period
        """), {"idx": idx_code, "year": year - 1, "period": period}).fetchall()
        yoy_map = {row[0]: decimal_to_float(row[1]) for row in yoy_data}

        items = []
        for row in data:
            current_val = decimal_to_float(row[2])
            prev_val = prev_map.get(row[0])
            yoy_val = yoy_map.get(row[0])

            items.append(EIServicesItem(
                series_id=row[0],
                series_name=row[1],
                direction=direction,
                current_value=current_val,
                mom_change=(current_val - prev_val) if current_val and prev_val else None,
                yoy_change=(current_val - yoy_val) if current_val and yoy_val else None
            ))
        return items

    return EIServicesResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        import_services=get_services_by_code('IV', 'import'),
        export_services=get_services_by_code('IH', 'export'),
        inbound_services=get_services_by_code('IC', 'inbound'),
        outbound_services=get_services_by_code('IS', 'outbound')
    )


# ============================================================================
# TERMS OF TRADE ENDPOINTS
# ============================================================================

@router.get("/terms-of-trade", response_model=EITermsOfTradeResponse)
async def get_terms_of_trade(
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get terms of trade indexes"""
    if not year or not period:
        latest = db.execute(text("""
            SELECT d.year, d.period FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = 'CT' AND d.period != 'M13'
            ORDER BY d.year DESC, d.period DESC LIMIT 1
        """)).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    data = db.execute(text("""
        SELECT s.series_id, s.series_name, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CT' AND d.year = :year AND d.period = :period
        ORDER BY s.series_name
    """), {"year": year, "period": period}).fetchall()

    prev_result = db.execute(text("""
        SELECT d.year, d.period FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CT'
        AND (d.year < :year OR (d.year = :year AND d.period < :period))
        AND d.period != 'M13'
        ORDER BY d.year DESC, d.period DESC LIMIT 1
    """), {"year": year, "period": period}).fetchone()

    prev_map = {}
    if prev_result:
        prev_data = db.execute(text("""
            SELECT s.series_id, d.value FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code = 'CT' AND d.year = :year AND d.period = :period
        """), {"year": prev_result[0], "period": prev_result[1]}).fetchall()
        prev_map = {row[0]: decimal_to_float(row[1]) for row in prev_data}

    yoy_data = db.execute(text("""
        SELECT s.series_id, d.value FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CT' AND d.year = :year AND d.period = :period
    """), {"year": year - 1, "period": period}).fetchall()
    yoy_map = {row[0]: decimal_to_float(row[1]) for row in yoy_data}

    terms = []
    for row in data:
        current_val = decimal_to_float(row[2])
        prev_val = prev_map.get(row[0])
        yoy_val = yoy_map.get(row[0])

        terms.append(EITermsOfTradeItem(
            series_id=row[0],
            series_name=row[1],
            current_value=current_val,
            mom_change=(current_val - prev_val) if current_val and prev_val else None,
            yoy_change=(current_val - yoy_val) if current_val and yoy_val else None
        ))

    return EITermsOfTradeResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        terms=terms
    )


@router.get("/terms-of-trade/timeline", response_model=EITermsOfTradeTimelineResponse)
async def get_terms_of_trade_timeline(
    series_ids: Optional[str] = Query(None, description="Comma-separated series IDs"),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get terms of trade timeline"""
    year_filter = f"AND d.year >= {start_year}" if start_year else ""

    if series_ids:
        ids = [s.strip() for s in series_ids.split(',')]
        placeholders = ','.join([f"'{sid}'" for sid in ids])
        series_filter = f"AND s.series_id IN ({placeholders})"
    else:
        series_filter = ""

    # Get series info
    series_query = text(f"""
        SELECT s.series_id, s.series_name, s.base_period
        FROM bls_ei_series s
        WHERE s.index_code = 'CT' {series_filter.replace('s.', '')}
        ORDER BY s.series_name
    """)
    series_info = db.execute(series_query).fetchall()
    series_list = [
        EISeriesInfo(
            series_id=row[0],
            series_name=row[1],
            index_code='CT',
            base_period=row[2]
        )
        for row in series_info
    ]

    if not series_list:
        return EITermsOfTradeTimelineResponse(series=[], data=[])

    ids = [s.series_id for s in series_list]
    placeholders = ','.join([f"'{sid}'" for sid in ids])

    result = db.execute(text(f"""
        SELECT d.series_id, d.year, d.period, d.value
        FROM bls_ei_data d
        JOIN bls_ei_series s ON d.series_id = s.series_id
        WHERE s.index_code = 'CT'
        AND d.series_id IN ({placeholders})
        AND d.period != 'M13'
        {year_filter}
        ORDER BY d.year, d.period
    """)).fetchall()

    timeline_map: Dict[str, Dict[str, Optional[float]]] = {}
    for row in result:
        key = f"{row[1]}-{row[2]}"
        if key not in timeline_map:
            timeline_map[key] = {'year': row[1], 'period': row[2], 'values': {}}
        timeline_map[key]['values'][row[0]] = decimal_to_float(row[3])

    data = [
        EITermsOfTradeTimelinePoint(
            year=v['year'],
            period=v['period'],
            period_name=get_period_name(v['period'], v['year']),
            values=v['values']
        )
        for v in sorted(timeline_map.values(), key=lambda x: (x['year'], x['period']))
    ]

    return EITermsOfTradeTimelineResponse(series=series_list, data=data)


# ============================================================================
# TREND ENDPOINT
# ============================================================================

@router.get("/trend", response_model=EITrendResponse)
async def get_trend(
    series_id: str = Query(...),
    start_year: Optional[int] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get historical trend for a series"""
    # Get series info
    series_result = db.execute(
        select(EISeries, EIIndex.index_name).join(
            EIIndex, EISeries.index_code == EIIndex.index_code, isouter=True
        ).where(EISeries.series_id == series_id)
    ).fetchone()

    if not series_result:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    s = series_result[0]
    country, industry = extract_country_from_series(s.series_name or '')
    series_info = EISeriesInfo(
        series_id=s.series_id,
        seasonal_code=s.seasonal_code,
        index_code=s.index_code,
        index_name=series_result[1],
        series_name=s.series_name,
        base_period=s.base_period,
        series_title=s.series_title,
        begin_year=s.begin_year,
        end_year=s.end_year,
        country_region=country,
        industry_category=industry
    )

    # Get data
    year_filter = f"AND year >= {start_year}" if start_year else ""
    data_result = db.execute(text(f"""
        SELECT year, period, value
        FROM bls_ei_data
        WHERE series_id = :sid AND period != 'M13'
        {year_filter}
        ORDER BY year, period
    """), {"sid": series_id}).fetchall()

    # Calculate changes
    data = []
    prev_val = None
    for i, row in enumerate(data_result):
        current_val = decimal_to_float(row[2])

        mom_change = None
        if prev_val is not None and current_val is not None:
            mom_change = current_val - prev_val

        # Find YoY
        yoy_change = None
        yoy_pct = None
        year_ago_idx = i - 12  # Monthly data
        if year_ago_idx >= 0:
            yoy_val = decimal_to_float(data_result[year_ago_idx][2])
            if yoy_val is not None and current_val is not None:
                yoy_change = current_val - yoy_val
                if yoy_val != 0:
                    yoy_pct = ((current_val - yoy_val) / yoy_val) * 100

        data.append(EITrendPoint(
            year=row[0],
            period=row[1],
            period_name=get_period_name(row[1], row[0]),
            value=current_val,
            mom_change=mom_change,
            yoy_change=yoy_change,
            yoy_pct_change=yoy_pct
        ))

        prev_val = current_val

    return EITrendResponse(
        series_id=series_id,
        series_info=series_info,
        data=data
    )


# ============================================================================
# TOP MOVERS ENDPOINT
# ============================================================================

@router.get("/top-movers", response_model=EITopMoversResponse)
async def get_top_movers(
    direction: str = Query("all", description="'import', 'export', or 'all'"),
    metric: str = Query("yoy_change", description="'mom_change' or 'yoy_change'"),
    limit: int = Query(10),
    year: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_data_db)
):
    """Get top movers by price change"""
    if not year or not period:
        latest = db.execute(text("""
            SELECT year, period FROM bls_ei_data
            WHERE period != 'M13' ORDER BY year DESC, period DESC LIMIT 1
        """)).fetchone()
        if latest:
            year, period = latest[0], latest[1]

    # Determine index codes to search
    if direction == 'import':
        index_codes = "('IR', 'IZ', 'IP', 'CO')"
    elif direction == 'export':
        index_codes = "('IQ', 'IY', 'ID', 'CD')"
    else:
        index_codes = "('IR', 'IQ', 'IZ', 'IY', 'IP', 'ID', 'CO', 'CD')"

    # Get comparison period
    if metric == 'mom_change':
        comp_result = db.execute(text("""
            SELECT year, period FROM bls_ei_data
            WHERE (year < :year OR (year = :year AND period < :period))
            AND period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 1
        """), {"year": year, "period": period}).fetchone()
    else:  # yoy_change
        comp_result = (year - 1, period)

    comp_year, comp_period = comp_result if isinstance(comp_result, tuple) else (comp_result[0], comp_result[1]) if comp_result else (None, None)

    if not comp_year or not comp_period:
        return EITopMoversResponse(
            year=year, period=period, period_name=get_period_name(period, year),
            direction=direction, metric=metric, top_gainers=[], top_losers=[]
        )

    # Query for changes
    query = text(f"""
        WITH current_data AS (
            SELECT s.series_id, s.series_name, s.index_code, d.value as current_value
            FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code IN {index_codes}
            AND d.year = :year AND d.period = :period
        ),
        comparison_data AS (
            SELECT s.series_id, d.value as comp_value
            FROM bls_ei_data d
            JOIN bls_ei_series s ON d.series_id = s.series_id
            WHERE s.index_code IN {index_codes}
            AND d.year = :comp_year AND d.period = :comp_period
        )
        SELECT
            c.series_id, c.series_name, c.index_code, c.current_value,
            c.current_value - p.comp_value as change,
            CASE WHEN p.comp_value != 0
                THEN ((c.current_value - p.comp_value) / p.comp_value) * 100
                ELSE NULL END as pct_change
        FROM current_data c
        JOIN comparison_data p ON c.series_id = p.series_id
        WHERE c.current_value IS NOT NULL AND p.comp_value IS NOT NULL
        ORDER BY change DESC
    """)

    results = db.execute(query, {
        "year": year, "period": period,
        "comp_year": comp_year, "comp_period": comp_period
    }).fetchall()

    all_items = []
    for row in results:
        country, _ = extract_country_from_series(row[1] or '')
        all_items.append(EITopMoverItem(
            series_id=row[0],
            series_name=row[1],
            index_code=row[2],
            country_region=country if row[2] in ['CO', 'CD'] else None,
            current_value=decimal_to_float(row[3]),
            change=decimal_to_float(row[4]),
            pct_change=decimal_to_float(row[5])
        ))

    # Sort and get top gainers/losers
    gainers = [item for item in all_items if item.change and item.change > 0]
    losers = [item for item in all_items if item.change and item.change < 0]

    gainers.sort(key=lambda x: x.change or 0, reverse=True)
    losers.sort(key=lambda x: x.change or 0)

    return EITopMoversResponse(
        year=year,
        period=period,
        period_name=get_period_name(period, year),
        direction=direction,
        metric=metric,
        top_gainers=gainers[:limit],
        top_losers=losers[:limit]
    )
