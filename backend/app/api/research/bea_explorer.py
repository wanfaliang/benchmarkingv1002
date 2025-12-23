"""
BEA Data Explorer API Endpoints

Endpoints for exploring NIPA, Regional, GDP by Industry, ITA, and Fixed Assets data.
Adapted from DATA project for Finexus Research module.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from backend.app.database import get_data_db
# Authentication removed - BEA research data is public/internal
from backend.app.data_models.bea_models import (
    NIPATable, NIPASeries, NIPAData,
    RegionalTable, RegionalLineCode, RegionalGeoFips, RegionalData,
    GDPByIndustryTable, GDPByIndustryIndustry, GDPByIndustryData,
    ITAIndicator, ITAArea, ITAData,
    FixedAssetsTable, FixedAssetsSeries, FixedAssetsData,
)

router = APIRouter(prefix="/api/research/bea", tags=["BEA Explorer"])


# ============================================================================
# PYDANTIC RESPONSE MODELS
# ============================================================================

class NIPATableResponse(BaseModel):
    table_name: str
    table_description: str
    has_annual: bool
    has_quarterly: bool
    has_monthly: bool
    first_year: Optional[int]
    last_year: Optional[int]
    series_count: int
    is_active: bool

class NIPASeriesResponse(BaseModel):
    series_code: str
    table_name: str
    line_number: int
    line_description: str
    metric_name: Optional[str]
    cl_unit: Optional[str]
    unit_mult: Optional[int]
    data_points_count: int

class NIPATimeSeriesResponse(BaseModel):
    series_code: str
    line_description: str
    metric_name: Optional[str]
    unit: Optional[str]
    unit_mult: Optional[int]
    data: List[Dict[str, Any]]

class RegionalTableResponse(BaseModel):
    table_name: str
    table_description: str
    geo_scope: Optional[str]
    first_year: Optional[int]
    last_year: Optional[int]
    line_codes_count: int
    is_active: bool

class RegionalLineCodeResponse(BaseModel):
    table_name: str
    line_code: int
    line_description: str
    cl_unit: Optional[str]
    unit_mult: Optional[int]

class RegionalGeoResponse(BaseModel):
    geo_fips: str
    geo_name: str
    geo_type: Optional[str]
    parent_fips: Optional[str]

class RegionalTimeSeriesResponse(BaseModel):
    table_name: str
    line_code: int
    line_description: str
    geo_fips: str
    geo_name: str
    unit: Optional[str]
    unit_mult: Optional[int]
    data: List[Dict[str, Any]]


class RegionalBatchTimeSeriesResponse(BaseModel):
    table_name: str
    line_code: int
    line_description: str
    unit: Optional[str]
    unit_mult: Optional[int]
    series: List[Dict[str, Any]]  # List of {geo_fips, geo_name, data: [...]}

class GDPByIndustryTableResponse(BaseModel):
    table_id: int
    table_description: str
    has_annual: bool
    has_quarterly: bool
    first_annual_year: Optional[int]
    last_annual_year: Optional[int]
    first_quarterly_year: Optional[int]
    last_quarterly_year: Optional[int]
    is_active: bool

class GDPByIndustryIndustryResponse(BaseModel):
    industry_code: str
    industry_description: str
    parent_code: Optional[str]
    industry_level: Optional[int]

class GDPByIndustryTimeSeriesResponse(BaseModel):
    table_id: int
    table_description: str
    industry_code: str
    industry_description: str
    frequency: str
    unit: Optional[str]
    unit_mult: Optional[int]
    data: List[Dict[str, Any]]

class ITAIndicatorResponse(BaseModel):
    indicator_code: str
    indicator_description: str
    is_active: bool

class ITAAreaResponse(BaseModel):
    area_code: str
    area_name: str
    area_type: Optional[str]
    is_active: bool

class ITATimeSeriesResponse(BaseModel):
    indicator_code: str
    indicator_description: str
    area_code: str
    area_name: str
    frequency: str
    unit: Optional[str]
    unit_mult: Optional[int]
    data: List[Dict[str, Any]]

class FixedAssetsTableResponse(BaseModel):
    table_name: str
    table_description: str
    first_year: Optional[int]
    last_year: Optional[int]
    series_count: int
    is_active: bool

class FixedAssetsSeriesResponse(BaseModel):
    series_code: str
    table_name: str
    line_number: int
    line_description: str
    metric_name: Optional[str]
    cl_unit: Optional[str]
    unit_mult: Optional[int]
    data_points_count: int

class FixedAssetsTimeSeriesResponse(BaseModel):
    series_code: str
    line_description: str
    metric_name: Optional[str]
    unit: Optional[str]
    unit_mult: Optional[int]
    data: List[Dict[str, Any]]


# ============================================================================
# NIPA EXPLORER ENDPOINTS
# ============================================================================

@router.get("/nipa/tables", response_model=List[NIPATableResponse])
async def get_nipa_tables(
    active_only: bool = True,
    db: Session = Depends(get_data_db)):
    """Get list of NIPA tables"""
    query = db.query(NIPATable)
    if active_only:
        query = query.filter(NIPATable.is_active == True)
    tables = query.order_by(NIPATable.table_name).all()

    series_counts = dict(
        db.query(NIPASeries.table_name, func.count(NIPASeries.series_code))
        .group_by(NIPASeries.table_name).all()
    )

    return [
        NIPATableResponse(
            table_name=t.table_name,
            table_description=t.table_description,
            has_annual=t.has_annual or False,
            has_quarterly=t.has_quarterly or False,
            has_monthly=t.has_monthly or False,
            first_year=t.first_year,
            last_year=t.last_year,
            series_count=series_counts.get(t.table_name, 0),
            is_active=t.is_active or False,
        )
        for t in tables
    ]


@router.get("/nipa/tables/{table_name}", response_model=NIPATableResponse)
async def get_nipa_table(
    table_name: str,
    db: Session = Depends(get_data_db)):
    """Get details of a specific NIPA table"""
    table = db.query(NIPATable).filter(
        NIPATable.table_name == table_name.upper()
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail=f"Table {table_name} not found")

    series_count = db.query(func.count(NIPASeries.series_code)).filter(
        NIPASeries.table_name == table_name.upper()
    ).scalar() or 0

    return NIPATableResponse(
        table_name=table.table_name,
        table_description=table.table_description,
        has_annual=table.has_annual or False,
        has_quarterly=table.has_quarterly or False,
        has_monthly=table.has_monthly or False,
        first_year=table.first_year,
        last_year=table.last_year,
        series_count=series_count,
        is_active=table.is_active or False,
    )


@router.get("/nipa/tables/{table_name}/series", response_model=List[NIPASeriesResponse])
async def get_nipa_table_series(
    table_name: str,
    db: Session = Depends(get_data_db)):
    """Get all series for a NIPA table"""
    series_list = db.query(NIPASeries).filter(
        NIPASeries.table_name == table_name.upper()
    ).order_by(NIPASeries.line_number).all()

    if not series_list:
        return []

    data_counts = dict(
        db.query(NIPAData.series_code, func.count(NIPAData.time_period))
        .filter(NIPAData.series_code.in_([s.series_code for s in series_list]))
        .group_by(NIPAData.series_code).all()
    )

    return [
        NIPASeriesResponse(
            series_code=s.series_code,
            table_name=s.table_name,
            line_number=s.line_number,
            line_description=s.line_description,
            metric_name=s.metric_name,
            cl_unit=s.cl_unit,
            unit_mult=s.unit_mult,
            data_points_count=data_counts.get(s.series_code, 0),
        )
        for s in series_list
    ]


@router.get("/nipa/series/{series_code}/data", response_model=NIPATimeSeriesResponse)
async def get_nipa_series_data(
    series_code: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    frequency: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get time series data for a NIPA series"""
    series = db.query(NIPASeries).filter(
        NIPASeries.series_code == series_code
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_code} not found")

    query = db.query(NIPAData).filter(NIPAData.series_code == series_code)

    if start_year:
        query = query.filter(NIPAData.time_period >= str(start_year))
    if end_year:
        query = query.filter(NIPAData.time_period <= str(end_year + 1))

    data_points = query.order_by(NIPAData.time_period).all()

    # Filter by frequency if specified
    if frequency:
        freq = frequency.upper()
        if freq == 'A':
            data_points = [d for d in data_points if len(d.time_period) == 4]
        elif freq == 'Q':
            data_points = [d for d in data_points if 'Q' in d.time_period]
        elif freq == 'M':
            data_points = [d for d in data_points if 'M' in d.time_period]

    return NIPATimeSeriesResponse(
        series_code=series_code,
        line_description=series.line_description,
        metric_name=series.metric_name,
        unit=series.cl_unit,
        unit_mult=series.unit_mult,
        data=[
            {
                "time_period": d.time_period,
                "value": float(d.value) if d.value else None,
                "note_ref": d.note_ref,
            }
            for d in data_points
        ]
    )


@router.get("/nipa/headline")
async def get_nipa_headline(db: Session = Depends(get_data_db)):
    """
    Get headline GDP data for Research portal dashboard.
    Returns current GDP growth, prior quarter, components contribution, and trend.
    """
    # Real GDP percent change - Table T10101, line 1
    # Find the GDP growth series
    gdp_series = db.query(NIPASeries).filter(
        NIPASeries.table_name == 'T10101',
        NIPASeries.line_number == 1
    ).first()

    if not gdp_series:
        # Try alternative table name
        gdp_series = db.query(NIPASeries).filter(
            NIPASeries.line_description.ilike('%Gross domestic product%'),
            NIPASeries.table_name.like('T101%')
        ).first()

    # Get quarterly GDP data (last 8 quarters)
    gdp_data = []
    if gdp_series:
        quarterly_data = db.query(NIPAData).filter(
            NIPAData.series_code == gdp_series.series_code,
            NIPAData.time_period.like('%Q%')
        ).order_by(desc(NIPAData.time_period)).limit(8).all()
        gdp_data = list(reversed(quarterly_data))

    # Get GDP components contributions - Table T10102
    component_series = {
        'consumption': {'table': 'T10102', 'line': 2, 'name': 'Consumption'},
        'investment': {'table': 'T10102', 'line': 7, 'name': 'Investment'},
        'government': {'table': 'T10102', 'line': 22, 'name': 'Government'},
        'net_exports': {'table': 'T10102', 'line': 14, 'name': 'Net Exports'},
    }

    components = []
    for key, config in component_series.items():
        series = db.query(NIPASeries).filter(
            NIPASeries.table_name == config['table'],
            NIPASeries.line_number == config['line']
        ).first()

        if series:
            latest = db.query(NIPAData).filter(
                NIPAData.series_code == series.series_code,
                NIPAData.time_period.like('%Q%')
            ).order_by(desc(NIPAData.time_period)).first()

            if latest and latest.value is not None:
                components.append({
                    'name': config['name'],
                    'contribution': float(latest.value),
                    'series_code': series.series_code,
                })

    # Calculate max contribution for percentage display
    max_contrib = max([abs(c['contribution']) for c in components], default=1)
    for c in components:
        c['pct'] = int((c['contribution'] / max_contrib) * 100) if max_contrib else 0

    # Build trend data
    trend = []
    for d in gdp_data:
        period = d.time_period
        # Convert 2024Q3 to Q3 24 format
        if 'Q' in period:
            year = period[:4]
            quarter = period[4:]
            short_year = year[2:]
            trend.append({
                'q': f"{quarter} {short_year}",
                'period': period,
                'value': float(d.value) if d.value else None,
            })

    # Current and prior values
    current_value = None
    prior_value = None
    current_period = None

    if len(gdp_data) >= 1:
        current_value = float(gdp_data[-1].value) if gdp_data[-1].value else None
        current_period = gdp_data[-1].time_period
    if len(gdp_data) >= 2:
        prior_value = float(gdp_data[-2].value) if gdp_data[-2].value else None

    return {
        "current": {
            "value": current_value,
            "prior": prior_value,
            "period": current_period,
            "unit": "% SAAR",
        },
        "components": components,
        "trend": trend,
        "series_code": gdp_series.series_code if gdp_series else None,
    }


# ============================================================================
# REGIONAL EXPLORER ENDPOINTS
# ============================================================================

@router.get("/regional/tables", response_model=List[RegionalTableResponse])
async def get_regional_tables(
    active_only: bool = True,
    db: Session = Depends(get_data_db)):
    """Get list of Regional tables"""
    query = db.query(RegionalTable)
    if active_only:
        query = query.filter(RegionalTable.is_active == True)
    tables = query.order_by(RegionalTable.table_name).all()

    line_counts = dict(
        db.query(RegionalLineCode.table_name, func.count(RegionalLineCode.line_code))
        .group_by(RegionalLineCode.table_name).all()
    )

    return [
        RegionalTableResponse(
            table_name=t.table_name,
            table_description=t.table_description,
            geo_scope=t.geo_scope,
            first_year=t.first_year,
            last_year=t.last_year,
            line_codes_count=line_counts.get(t.table_name, 0),
            is_active=t.is_active or False,
        )
        for t in tables
    ]


@router.get("/regional/tables/{table_name}/linecodes", response_model=List[RegionalLineCodeResponse])
async def get_regional_table_linecodes(
    table_name: str,
    db: Session = Depends(get_data_db)):
    """Get all line codes for a Regional table"""
    line_codes = db.query(RegionalLineCode).filter(
        RegionalLineCode.table_name == table_name.upper()
    ).order_by(RegionalLineCode.line_code).all()

    if not line_codes:
        raise HTTPException(status_code=404, detail=f"No line codes found for table {table_name}")

    return [
        RegionalLineCodeResponse(
            table_name=lc.table_name,
            line_code=lc.line_code,
            line_description=lc.line_description,
            cl_unit=lc.cl_unit,
            unit_mult=lc.unit_mult,
        )
        for lc in line_codes
    ]


@router.get("/regional/geographies", response_model=List[RegionalGeoResponse])
async def get_regional_geographies(
    geo_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_data_db)):
    """Get list of geographic areas"""
    query = db.query(RegionalGeoFips)
    if geo_type:
        query = query.filter(RegionalGeoFips.geo_type == geo_type)
    if search:
        query = query.filter(RegionalGeoFips.geo_name.ilike(f"%{search}%"))
    geos = query.order_by(RegionalGeoFips.geo_name).limit(limit).all()

    return [
        RegionalGeoResponse(
            geo_fips=g.geo_fips,
            geo_name=g.geo_name,
            geo_type=g.geo_type,
            parent_fips=g.parent_fips,
        )
        for g in geos
    ]


@router.get("/regional/data", response_model=RegionalTimeSeriesResponse)
async def get_regional_data(
    table_name: str,
    line_code: int,
    geo_fips: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """Get time series data for a Regional table/line/geography combination"""
    line_info = db.query(RegionalLineCode).filter(
        RegionalLineCode.table_name == table_name.upper(),
        RegionalLineCode.line_code == line_code
    ).first()

    if not line_info:
        raise HTTPException(status_code=404, detail=f"Line code {line_code} not found for table {table_name}")

    geo_info = db.query(RegionalGeoFips).filter(RegionalGeoFips.geo_fips == geo_fips).first()
    if not geo_info:
        raise HTTPException(status_code=404, detail=f"Geography {geo_fips} not found")

    query = db.query(RegionalData).filter(
        RegionalData.table_name == table_name.upper(),
        RegionalData.line_code == line_code,
        RegionalData.geo_fips == geo_fips
    )

    if start_year:
        query = query.filter(RegionalData.time_period >= str(start_year))
    if end_year:
        query = query.filter(RegionalData.time_period <= str(end_year))

    data_points = query.order_by(RegionalData.time_period).all()

    unit_mult = None
    cl_unit = None
    for d in data_points:
        if unit_mult is None and d.unit_mult is not None:
            unit_mult = d.unit_mult
        if cl_unit is None and d.cl_unit is not None:
            cl_unit = d.cl_unit
        if unit_mult is not None and cl_unit is not None:
            break

    return RegionalTimeSeriesResponse(
        table_name=table_name.upper(),
        line_code=line_code,
        line_description=line_info.line_description,
        geo_fips=geo_fips,
        geo_name=geo_info.geo_name,
        unit=cl_unit or line_info.cl_unit,
        unit_mult=unit_mult if unit_mult is not None else line_info.unit_mult,
        data=[
            {
                "time_period": d.time_period,
                "value": float(d.value) if d.value else None,
                "note_ref": d.note_ref,
            }
            for d in data_points
        ]
    )


@router.get("/regional/data/batch", response_model=RegionalBatchTimeSeriesResponse)
async def get_regional_data_batch(
    table_name: str,
    line_code: int,
    geo_fips_list: str = Query(..., description="Comma-separated list of geo_fips codes"),
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """
    Get time series data for multiple geographies in a single query.
    This is much more efficient than making 50 separate API calls.

    Example: /regional/data/batch?table_name=SAGDP1&line_code=1&geo_fips_list=01000,02000,04000
    """
    geo_fips_codes = [f.strip() for f in geo_fips_list.split(',') if f.strip()]

    if not geo_fips_codes:
        raise HTTPException(status_code=400, detail="geo_fips_list cannot be empty")

    if len(geo_fips_codes) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 geographies per request")

    # Get line code info
    line_info = db.query(RegionalLineCode).filter(
        RegionalLineCode.table_name == table_name.upper(),
        RegionalLineCode.line_code == line_code
    ).first()

    if not line_info:
        raise HTTPException(status_code=404, detail=f"Line code {line_code} not found for table {table_name}")

    # Get geo names
    geos = db.query(RegionalGeoFips).filter(RegionalGeoFips.geo_fips.in_(geo_fips_codes)).all()
    geo_names = {g.geo_fips: g.geo_name for g in geos}

    # Query all data in ONE query using IN clause
    query = db.query(RegionalData).filter(
        RegionalData.table_name == table_name.upper(),
        RegionalData.line_code == line_code,
        RegionalData.geo_fips.in_(geo_fips_codes)
    )

    if start_year:
        query = query.filter(RegionalData.time_period >= str(start_year))
    if end_year:
        query = query.filter(RegionalData.time_period <= str(end_year))

    data_points = query.order_by(RegionalData.geo_fips, RegionalData.time_period).all()

    # Group by geo_fips
    from collections import defaultdict
    grouped_data: Dict[str, List] = defaultdict(list)
    unit_mult = None
    cl_unit = None

    for d in data_points:
        grouped_data[d.geo_fips].append({
            "time_period": d.time_period,
            "value": float(d.value) if d.value else None,
        })
        if unit_mult is None and d.unit_mult is not None:
            unit_mult = d.unit_mult
        if cl_unit is None and d.cl_unit is not None:
            cl_unit = d.cl_unit

    # Build response
    series = []
    for geo_fips in geo_fips_codes:
        if geo_fips in grouped_data:
            series.append({
                "geo_fips": geo_fips,
                "geo_name": geo_names.get(geo_fips, geo_fips),
                "data": grouped_data[geo_fips],
            })

    return RegionalBatchTimeSeriesResponse(
        table_name=table_name.upper(),
        line_code=line_code,
        line_description=line_info.line_description,
        unit=cl_unit or line_info.cl_unit,
        unit_mult=unit_mult if unit_mult is not None else line_info.unit_mult,
        series=series,
    )


@router.get("/regional/snapshot")
async def get_regional_snapshot(
    table_name: str = "SAGDP1",
    line_code: int = 1,
    geo_type: str = "State",
    year: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get snapshot of data for all geographies of a type (for treemap/heatmap)"""
    geos = db.query(RegionalGeoFips).filter(RegionalGeoFips.geo_type == geo_type).all()
    if not geos:
        return {"data": [], "table_name": table_name, "line_code": line_code}

    geo_fips_list = [g.geo_fips for g in geos]
    geo_names = {g.geo_fips: g.geo_name for g in geos}

    if year:
        target_year = year
    else:
        target_year = db.query(func.max(RegionalData.time_period)).filter(
            RegionalData.table_name == table_name.upper(),
            RegionalData.line_code == line_code,
            RegionalData.geo_fips.in_(geo_fips_list)
        ).scalar()

    if not target_year:
        return {"data": [], "table_name": table_name, "line_code": line_code, "year": None}

    data_points = db.query(RegionalData).filter(
        RegionalData.table_name == table_name.upper(),
        RegionalData.line_code == line_code,
        RegionalData.geo_fips.in_(geo_fips_list),
        RegionalData.time_period == target_year
    ).all()

    line_info = db.query(RegionalLineCode).filter(
        RegionalLineCode.table_name == table_name.upper(),
        RegionalLineCode.line_code == line_code
    ).first()

    unit_mult = None
    cl_unit = None
    result = []
    for d in data_points:
        if d.value is not None:
            result.append({
                "geo_fips": d.geo_fips,
                "geo_name": geo_names.get(d.geo_fips, d.geo_fips),
                "value": float(d.value),
            })
            if unit_mult is None and d.unit_mult is not None:
                unit_mult = d.unit_mult
            if cl_unit is None and d.cl_unit is not None:
                cl_unit = d.cl_unit

    result.sort(key=lambda x: x["value"], reverse=True)

    return {
        "data": result,
        "table_name": table_name.upper(),
        "line_code": line_code,
        "line_description": line_info.line_description if line_info else None,
        "unit": cl_unit or (line_info.cl_unit if line_info else None),
        "unit_mult": unit_mult if unit_mult is not None else (line_info.unit_mult if line_info else None),
        "year": target_year,
    }


# ============================================================================
# GDP BY INDUSTRY EXPLORER ENDPOINTS
# ============================================================================

@router.get("/gdpbyindustry/tables", response_model=List[GDPByIndustryTableResponse])
async def get_gdpbyindustry_tables(
    active_only: bool = True,
    db: Session = Depends(get_data_db)):
    """Get list of GDP by Industry tables"""
    query = db.query(GDPByIndustryTable)
    if active_only:
        query = query.filter(GDPByIndustryTable.is_active == True)
    tables = query.order_by(GDPByIndustryTable.table_id).all()

    return [
        GDPByIndustryTableResponse(
            table_id=t.table_id,
            table_description=t.table_description,
            has_annual=t.has_annual or False,
            has_quarterly=t.has_quarterly or False,
            first_annual_year=t.first_annual_year,
            last_annual_year=t.last_annual_year,
            first_quarterly_year=t.first_quarterly_year,
            last_quarterly_year=t.last_quarterly_year,
            is_active=t.is_active or False,
        )
        for t in tables
    ]


@router.get("/gdpbyindustry/industries", response_model=List[GDPByIndustryIndustryResponse])
async def get_gdpbyindustry_industries(
    active_only: bool = True,
    level: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """Get list of industries for GDP by Industry data"""
    query = db.query(GDPByIndustryIndustry)
    if active_only:
        query = query.filter(GDPByIndustryIndustry.is_active == True)
    if level is not None:
        query = query.filter(GDPByIndustryIndustry.industry_level == level)
    industries = query.order_by(GDPByIndustryIndustry.industry_code).all()

    # Get better descriptions from data table
    industry_codes = [i.industry_code for i in industries]
    generic_descriptions = {'Value added', 'Compensation of employees', 'Gross operating surplus',
                           'Taxes on production and imports less subsidies'}

    descriptions_query = db.query(
        GDPByIndustryData.industry_code,
        GDPByIndustryData.industry_description
    ).filter(
        GDPByIndustryData.industry_code.in_(industry_codes),
        GDPByIndustryData.row_type == 'total',
        GDPByIndustryData.industry_description.isnot(None)
    ).distinct().all()

    desc_map = {}
    for code, desc in descriptions_query:
        if desc:
            is_generic = desc in generic_descriptions
            if code not in desc_map:
                desc_map[code] = {'desc': desc, 'is_generic': is_generic}
            elif desc_map[code]['is_generic'] and not is_generic:
                desc_map[code] = {'desc': desc, 'is_generic': is_generic}
    desc_map = {k: v['desc'] for k, v in desc_map.items()}

    return [
        GDPByIndustryIndustryResponse(
            industry_code=i.industry_code,
            industry_description=desc_map.get(i.industry_code) or i.industry_description or i.industry_code,
            parent_code=i.parent_code,
            industry_level=i.industry_level,
        )
        for i in industries
    ]


@router.get("/gdpbyindustry/data", response_model=GDPByIndustryTimeSeriesResponse)
async def get_gdpbyindustry_data(
    table_id: int,
    industry_code: str,
    frequency: str = "A",
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """Get time series data for a GDP by Industry table/industry combination"""
    table_info = db.query(GDPByIndustryTable).filter(GDPByIndustryTable.table_id == table_id).first()
    if not table_info:
        raise HTTPException(status_code=404, detail=f"Table {table_id} not found")

    industry_info = db.query(GDPByIndustryIndustry).filter(
        GDPByIndustryIndustry.industry_code == industry_code
    ).first()
    if not industry_info:
        raise HTTPException(status_code=404, detail=f"Industry {industry_code} not found")

    query = db.query(GDPByIndustryData).filter(
        GDPByIndustryData.table_id == table_id,
        GDPByIndustryData.industry_code == industry_code,
        GDPByIndustryData.frequency == frequency.upper()
    )

    if start_year:
        query = query.filter(GDPByIndustryData.time_period >= str(start_year))
    if end_year:
        query = query.filter(GDPByIndustryData.time_period <= str(end_year + 1))

    data_points = query.order_by(GDPByIndustryData.time_period).all()

    unit_mult = None
    cl_unit = None
    for d in data_points:
        if unit_mult is None and d.unit_mult is not None:
            unit_mult = d.unit_mult
        if cl_unit is None and d.cl_unit is not None:
            cl_unit = d.cl_unit
        if unit_mult is not None and cl_unit is not None:
            break

    return GDPByIndustryTimeSeriesResponse(
        table_id=table_id,
        table_description=table_info.table_description,
        industry_code=industry_code,
        industry_description=industry_info.industry_description or industry_code,
        frequency=frequency.upper(),
        unit=cl_unit,
        unit_mult=unit_mult,
        data=[
            {
                "time_period": d.time_period,
                "value": float(d.value) if d.value else None,
                "row_type": d.row_type,
                "note_ref": d.note_ref,
            }
            for d in data_points
        ]
    )


@router.get("/gdpbyindustry/snapshot")
async def get_gdpbyindustry_snapshot(
    table_id: int = 1,
    frequency: str = "A",
    year: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get snapshot of data for all industries (for treemap/charts)"""
    if year:
        target_period = year
    else:
        target_period = db.query(func.max(GDPByIndustryData.time_period)).filter(
            GDPByIndustryData.table_id == table_id,
            GDPByIndustryData.frequency == frequency.upper()
        ).scalar()

    if not target_period:
        return {"data": [], "table_id": table_id, "period": None}

    data_points = db.query(GDPByIndustryData).filter(
        GDPByIndustryData.table_id == table_id,
        GDPByIndustryData.frequency == frequency.upper(),
        GDPByIndustryData.time_period == target_period,
        GDPByIndustryData.row_type == 'total'
    ).all()

    industry_codes = [d.industry_code for d in data_points]
    industries = db.query(GDPByIndustryIndustry).filter(
        GDPByIndustryIndustry.industry_code.in_(industry_codes)
    ).all()
    industry_map = {i.industry_code: i for i in industries}

    table_info = db.query(GDPByIndustryTable).filter(GDPByIndustryTable.table_id == table_id).first()

    unit_mult = None
    cl_unit = None
    result = []
    for d in data_points:
        if d.value is not None:
            industry = industry_map.get(d.industry_code)
            result.append({
                "industry_code": d.industry_code,
                "industry_description": d.industry_description or (industry.industry_description if industry else d.industry_code),
                "value": float(d.value),
                "parent_code": industry.parent_code if industry else None,
                "industry_level": industry.industry_level if industry else None,
            })
            if unit_mult is None and d.unit_mult is not None:
                unit_mult = d.unit_mult
            if cl_unit is None and d.cl_unit is not None:
                cl_unit = d.cl_unit

    result.sort(key=lambda x: x["value"], reverse=True)

    return {
        "data": result,
        "table_id": table_id,
        "table_description": table_info.table_description if table_info else None,
        "frequency": frequency.upper(),
        "period": target_period,
        "unit": cl_unit,
        "unit_mult": unit_mult,
    }


# ============================================================================
# ITA (INTERNATIONAL TRADE) EXPLORER ENDPOINTS
# ============================================================================

@router.get("/ita/indicators", response_model=List[ITAIndicatorResponse])
async def get_ita_indicators(
    active_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get list of ITA indicators"""
    query = db.query(ITAIndicator)
    if active_only:
        query = query.filter(ITAIndicator.is_active == True)
    if search:
        query = query.filter(
            ITAIndicator.indicator_description.ilike(f'%{search}%') |
            ITAIndicator.indicator_code.ilike(f'%{search}%')
        )
    indicators = query.order_by(ITAIndicator.indicator_code).all()

    return [
        ITAIndicatorResponse(
            indicator_code=i.indicator_code,
            indicator_description=i.indicator_description or i.indicator_code,
            is_active=i.is_active,
        )
        for i in indicators
    ]


@router.get("/ita/areas", response_model=List[ITAAreaResponse])
async def get_ita_areas(
    active_only: bool = True,
    area_type: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get list of ITA areas/countries"""
    query = db.query(ITAArea)
    if active_only:
        query = query.filter(ITAArea.is_active == True)
    if area_type:
        query = query.filter(ITAArea.area_type == area_type)
    areas = query.order_by(ITAArea.area_name).all()

    return [
        ITAAreaResponse(
            area_code=a.area_code,
            area_name=a.area_name,
            area_type=a.area_type,
            is_active=a.is_active,
        )
        for a in areas
    ]


@router.get("/ita/data", response_model=ITATimeSeriesResponse)
async def get_ita_data(
    indicator_code: str,
    area_code: str = "AllCountries",
    frequency: str = "A",
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """Get ITA time series data for a specific indicator and area"""
    indicator = db.query(ITAIndicator).filter(ITAIndicator.indicator_code == indicator_code).first()
    if not indicator:
        raise HTTPException(status_code=404, detail=f"Indicator '{indicator_code}' not found")

    area = db.query(ITAArea).filter(ITAArea.area_code == area_code).first()
    if not area:
        raise HTTPException(status_code=404, detail=f"Area '{area_code}' not found")

    query = db.query(ITAData).filter(
        ITAData.indicator_code == indicator_code,
        ITAData.area_code == area_code,
        ITAData.frequency == frequency.upper()
    )

    if start_year:
        query = query.filter(ITAData.time_period >= str(start_year))
    if end_year:
        query = query.filter(ITAData.time_period <= f"{end_year}Q4" if frequency != "A" else str(end_year))

    data_points = query.order_by(ITAData.time_period).all()

    if not data_points:
        raise HTTPException(status_code=404, detail=f"No data found for indicator '{indicator_code}' and area '{area_code}'")

    first_point = data_points[0]

    return ITATimeSeriesResponse(
        indicator_code=indicator_code,
        indicator_description=indicator.indicator_description or indicator_code,
        area_code=area_code,
        area_name=area.area_name,
        frequency=frequency.upper(),
        unit=first_point.cl_unit,
        unit_mult=first_point.unit_mult,
        data=[
            {
                "time_period": d.time_period,
                "value": float(d.value) if d.value is not None else None,
                "note_ref": d.note_ref,
            }
            for d in data_points
        ]
    )


@router.get("/ita/headline")
async def get_ita_headline(
    frequency: str = "A",
    db: Session = Depends(get_data_db)):
    """Get headline ITA metrics (key balance indicators)"""
    headline_indicators = ['BalGds', 'BalServ', 'BalGdsServ', 'BalCurrAcct', 'BalPrimInc', 'BalSecInc']

    results = []
    for ind_code in headline_indicators:
        indicator = db.query(ITAIndicator).filter(ITAIndicator.indicator_code == ind_code).first()
        if not indicator:
            continue

        latest_data = db.query(ITAData).filter(
            ITAData.indicator_code == ind_code,
            ITAData.area_code == 'AllCountries',
            ITAData.frequency == frequency.upper()
        ).order_by(desc(ITAData.time_period)).first()

        if latest_data:
            results.append({
                "indicator_code": ind_code,
                "indicator_description": indicator.indicator_description,
                "value": float(latest_data.value) if latest_data.value is not None else None,
                "time_period": latest_data.time_period,
                "unit": latest_data.cl_unit,
                "unit_mult": latest_data.unit_mult,
            })

    return {"data": results, "frequency": frequency.upper()}


@router.get("/ita/snapshot")
async def get_ita_snapshot(
    indicator_code: str = "BalGds",
    frequency: str = "A",
    year: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get snapshot of data for an indicator across trading partners"""
    indicator = db.query(ITAIndicator).filter(ITAIndicator.indicator_code == indicator_code).first()
    if not indicator:
        raise HTTPException(status_code=404, detail=f"Indicator '{indicator_code}' not found")

    if year:
        target_period = year
    else:
        target_period = db.query(func.max(ITAData.time_period)).filter(
            ITAData.indicator_code == indicator_code,
            ITAData.frequency == frequency.upper()
        ).scalar()

    if not target_period:
        return {"data": [], "indicator_code": indicator_code, "period": None}

    data_points = db.query(ITAData).filter(
        ITAData.indicator_code == indicator_code,
        ITAData.frequency == frequency.upper(),
        ITAData.time_period == target_period,
        ITAData.area_code != 'AllCountries'
    ).all()

    area_codes = [d.area_code for d in data_points]
    areas = db.query(ITAArea).filter(ITAArea.area_code.in_(area_codes)).all()
    area_map = {a.area_code: a for a in areas}

    unit_mult = None
    cl_unit = None
    result = []
    for d in data_points:
        if d.value is not None:
            area = area_map.get(d.area_code)
            result.append({
                "area_code": d.area_code,
                "area_name": area.area_name if area else d.area_code,
                "area_type": area.area_type if area else None,
                "value": float(d.value),
            })
            if unit_mult is None and d.unit_mult is not None:
                unit_mult = d.unit_mult
            if cl_unit is None and d.cl_unit is not None:
                cl_unit = d.cl_unit

    result.sort(key=lambda x: abs(x["value"]), reverse=True)

    return {
        "data": result,
        "indicator_code": indicator_code,
        "indicator_description": indicator.indicator_description,
        "frequency": frequency.upper(),
        "period": target_period,
        "unit": cl_unit,
        "unit_mult": unit_mult,
    }


# ============================================================================
# FIXED ASSETS EXPLORER ENDPOINTS
# ============================================================================

@router.get("/fixedassets/tables", response_model=List[FixedAssetsTableResponse])
async def get_fixedassets_tables(
    active_only: bool = True,
    db: Session = Depends(get_data_db)):
    """Get list of Fixed Assets tables"""
    query = db.query(FixedAssetsTable)
    if active_only:
        query = query.filter(FixedAssetsTable.is_active == True)
    tables = query.order_by(FixedAssetsTable.table_name).all()

    series_counts = dict(
        db.query(FixedAssetsSeries.table_name, func.count(FixedAssetsSeries.series_code))
        .group_by(FixedAssetsSeries.table_name).all()
    )

    return [
        FixedAssetsTableResponse(
            table_name=t.table_name,
            table_description=t.table_description,
            first_year=t.first_year,
            last_year=t.last_year,
            series_count=series_counts.get(t.table_name, 0),
            is_active=t.is_active or False,
        )
        for t in tables
    ]


@router.get("/fixedassets/tables/{table_name}/series", response_model=List[FixedAssetsSeriesResponse])
async def get_fixedassets_table_series(
    table_name: str,
    db: Session = Depends(get_data_db)):
    """Get all series for a Fixed Assets table"""
    series_list = db.query(FixedAssetsSeries).filter(
        FixedAssetsSeries.table_name == table_name
    ).order_by(FixedAssetsSeries.line_number).all()

    if not series_list:
        raise HTTPException(status_code=404, detail=f"No series found for table {table_name}")

    data_counts = dict(
        db.query(FixedAssetsData.series_code, func.count(FixedAssetsData.time_period))
        .filter(FixedAssetsData.series_code.in_([s.series_code for s in series_list]))
        .group_by(FixedAssetsData.series_code).all()
    )

    return [
        FixedAssetsSeriesResponse(
            series_code=s.series_code,
            table_name=s.table_name,
            line_number=s.line_number,
            line_description=s.line_description,
            metric_name=s.metric_name,
            cl_unit=s.cl_unit,
            unit_mult=s.unit_mult,
            data_points_count=data_counts.get(s.series_code, 0),
        )
        for s in series_list
    ]


@router.get("/fixedassets/series/{series_code}/data", response_model=FixedAssetsTimeSeriesResponse)
async def get_fixedassets_series_data(
    series_code: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """Get time series data for a Fixed Assets series"""
    series = db.query(FixedAssetsSeries).filter(FixedAssetsSeries.series_code == series_code).first()
    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_code} not found")

    query = db.query(FixedAssetsData).filter(FixedAssetsData.series_code == series_code)
    if start_year:
        query = query.filter(FixedAssetsData.time_period >= str(start_year))
    if end_year:
        query = query.filter(FixedAssetsData.time_period <= str(end_year))

    data_points = query.order_by(FixedAssetsData.time_period).all()

    return FixedAssetsTimeSeriesResponse(
        series_code=series.series_code,
        line_description=series.line_description,
        metric_name=series.metric_name,
        unit=series.cl_unit,
        unit_mult=series.unit_mult,
        data=[
            {
                "time_period": d.time_period,
                "value": float(d.value) if d.value is not None else None,
                "note_ref": d.note_ref,
            }
            for d in data_points
        ]
    )


@router.get("/fixedassets/headline")
async def get_fixedassets_headline(
    db: Session = Depends(get_data_db)):
    """Get headline Fixed Assets metrics"""
    headline_series = [
        {'table': 'FAAt101', 'line': 1, 'name': 'Private Fixed Assets'},
        {'table': 'FAAt101', 'line': 3, 'name': 'Equipment'},
        {'table': 'FAAt101', 'line': 4, 'name': 'Structures'},
        {'table': 'FAAt101', 'line': 8, 'name': 'Residential'},
        {'table': 'FAAt101', 'line': 5, 'name': 'IP Products'},
        {'table': 'FAAt201', 'line': 1, 'name': 'Government Assets'},
    ]

    results = []
    for item in headline_series:
        series = db.query(FixedAssetsSeries).filter(
            FixedAssetsSeries.table_name == item['table'],
            FixedAssetsSeries.line_number == item['line']
        ).first()

        if not series:
            continue

        latest_data = db.query(FixedAssetsData).filter(
            FixedAssetsData.series_code == series.series_code
        ).order_by(desc(FixedAssetsData.time_period)).first()

        if latest_data:
            results.append({
                "series_code": series.series_code,
                "name": item['name'],
                "line_description": series.line_description,
                "value": float(latest_data.value) if latest_data.value is not None else None,
                "time_period": latest_data.time_period,
                "unit": series.cl_unit,
                "unit_mult": series.unit_mult,
            })

    return {"data": results}


@router.get("/fixedassets/snapshot")
async def get_fixedassets_snapshot(
    table_name: str = "FAAt101",
    year: Optional[str] = None,
    db: Session = Depends(get_data_db)):
    """Get snapshot of Fixed Assets data for a table's key series"""
    table = db.query(FixedAssetsTable).filter(FixedAssetsTable.table_name == table_name).first()
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    series_list = db.query(FixedAssetsSeries).filter(
        FixedAssetsSeries.table_name == table_name
    ).order_by(FixedAssetsSeries.line_number).all()

    if not series_list:
        return {"data": [], "table_name": table_name, "period": None}

    if year:
        target_period = year
    else:
        target_period = db.query(func.max(FixedAssetsData.time_period)).filter(
            FixedAssetsData.series_code.in_([s.series_code for s in series_list])
        ).scalar()

    if not target_period:
        return {"data": [], "table_name": table_name, "period": None}

    data_points = db.query(FixedAssetsData).filter(
        FixedAssetsData.series_code.in_([s.series_code for s in series_list]),
        FixedAssetsData.time_period == target_period
    ).all()

    data_map = {d.series_code: d for d in data_points}
    unit = series_list[0].cl_unit if series_list else None
    unit_mult = series_list[0].unit_mult if series_list else None

    result = []
    for s in series_list:
        data = data_map.get(s.series_code)
        if data and data.value is not None:
            result.append({
                "series_code": s.series_code,
                "line_number": s.line_number,
                "line_description": s.line_description,
                "value": float(data.value),
            })

    return {
        "data": result,
        "table_name": table_name,
        "table_description": table.table_description,
        "period": target_period,
        "unit": unit,
        "unit_mult": unit_mult,
    }


# ============================================================================
# BATCH ENDPOINTS FOR IMPROVED PERFORMANCE
# ============================================================================

@router.get("/fixedassets/data/batch")
async def get_fixedassets_data_batch(
    series_codes: str = Query(..., description="Comma-separated list of series codes"),
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """
    Get time series data for multiple Fixed Assets series in a single query.
    Much more efficient than making separate API calls for each series.

    Example: /fixedassets/data/batch?series_codes=FAAt101-A-1,FAAt101-A-2,FAAt101-A-3
    """
    codes = [c.strip() for c in series_codes.split(',') if c.strip()]

    if not codes:
        raise HTTPException(status_code=400, detail="series_codes cannot be empty")
    if len(codes) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 series per request")

    # Get series info
    series_list = db.query(FixedAssetsSeries).filter(
        FixedAssetsSeries.series_code.in_(codes)
    ).all()
    series_info = {s.series_code: s for s in series_list}

    # Query all data in ONE query
    query = db.query(FixedAssetsData).filter(FixedAssetsData.series_code.in_(codes))
    if start_year:
        query = query.filter(FixedAssetsData.time_period >= str(start_year))
    if end_year:
        query = query.filter(FixedAssetsData.time_period <= str(end_year))

    data_points = query.order_by(FixedAssetsData.series_code, FixedAssetsData.time_period).all()

    # Group by series_code
    from collections import defaultdict
    grouped_data: Dict[str, List] = defaultdict(list)

    for d in data_points:
        grouped_data[d.series_code].append({
            "time_period": d.time_period,
            "value": float(d.value) if d.value else None,
        })

    # Build response
    result = []
    for code in codes:
        if code in grouped_data:
            info = series_info.get(code)
            result.append({
                "series_code": code,
                "line_number": info.line_number if info else None,
                "line_description": info.line_description if info else None,
                "unit": info.cl_unit if info else None,
                "unit_mult": info.unit_mult if info else None,
                "data": grouped_data[code],
            })

    return {"series": result}


@router.get("/nipa/data/batch")
async def get_nipa_data_batch(
    series_codes: str = Query(..., description="Comma-separated list of series codes"),
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """
    Get time series data for multiple NIPA series in a single query.

    Example: /nipa/data/batch?series_codes=A191RL,A191RC,DPCERL
    """
    codes = [c.strip() for c in series_codes.split(',') if c.strip()]

    if not codes:
        raise HTTPException(status_code=400, detail="series_codes cannot be empty")
    if len(codes) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 series per request")

    # Get series info
    series_list = db.query(NIPASeries).filter(NIPASeries.series_code.in_(codes)).all()
    series_info = {s.series_code: s for s in series_list}

    # Query all data in ONE query
    query = db.query(NIPAData).filter(NIPAData.series_code.in_(codes))
    if start_year:
        query = query.filter(func.substr(NIPAData.time_period, 1, 4) >= str(start_year))
    if end_year:
        query = query.filter(func.substr(NIPAData.time_period, 1, 4) <= str(end_year))

    data_points = query.order_by(NIPAData.series_code, NIPAData.time_period).all()

    # Group by series_code
    from collections import defaultdict
    grouped_data: Dict[str, List] = defaultdict(list)

    for d in data_points:
        grouped_data[d.series_code].append({
            "time_period": d.time_period,
            "value": float(d.value) if d.value else None,
        })

    # Build response
    result = []
    for code in codes:
        if code in grouped_data:
            info = series_info.get(code)
            result.append({
                "series_code": code,
                "line_number": info.line_number if info else None,
                "line_description": info.line_description if info else None,
                "table_name": info.table_name if info else None,
                "unit": info.cl_unit if info else None,
                "unit_mult": info.unit_mult if info else None,
                "data": grouped_data[code],
            })

    return {"series": result}


@router.get("/gdpbyindustry/data/batch")
async def get_gdpbyindustry_data_batch(
    table_id: int,
    industry_codes: str = Query(..., description="Comma-separated list of industry codes"),
    year_type: str = "A",
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """
    Get time series data for multiple industries in a single query.

    Example: /gdpbyindustry/data/batch?table_id=1&industry_codes=1,11,21,22&year_type=A
    """
    codes = [c.strip() for c in industry_codes.split(',') if c.strip()]

    if not codes:
        raise HTTPException(status_code=400, detail="industry_codes cannot be empty")
    if len(codes) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 industries per request")

    # Get industry info
    industries = db.query(GDPByIndustryIndustry).filter(
        GDPByIndustryIndustry.industry_code.in_(codes)
    ).all()
    industry_info = {i.industry_code: i for i in industries}

    # Query all data in ONE query
    query = db.query(GDPByIndustryData).filter(
        GDPByIndustryData.table_id == table_id,
        GDPByIndustryData.industry_code.in_(codes),
        GDPByIndustryData.year_type == year_type.upper()
    )
    if start_year:
        query = query.filter(GDPByIndustryData.time_period >= str(start_year))
    if end_year:
        query = query.filter(GDPByIndustryData.time_period <= str(end_year))

    data_points = query.order_by(GDPByIndustryData.industry_code, GDPByIndustryData.time_period).all()

    # Group by industry_code
    from collections import defaultdict
    grouped_data: Dict[str, List] = defaultdict(list)
    unit = None
    unit_mult = None

    for d in data_points:
        grouped_data[d.industry_code].append({
            "time_period": d.time_period,
            "value": float(d.value) if d.value else None,
        })
        if unit is None and d.cl_unit:
            unit = d.cl_unit
        if unit_mult is None and d.unit_mult is not None:
            unit_mult = d.unit_mult

    # Build response
    result = []
    for code in codes:
        if code in grouped_data:
            info = industry_info.get(code)
            result.append({
                "industry_code": code,
                "industry_description": info.industry_description if info else None,
                "data": grouped_data[code],
            })

    return {
        "table_id": table_id,
        "year_type": year_type.upper(),
        "unit": unit,
        "unit_mult": unit_mult,
        "series": result,
    }


@router.get("/ita/data/batch")
async def get_ita_data_batch(
    indicator: str,
    area_codes: str = Query(..., description="Comma-separated list of area codes"),
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_data_db)):
    """
    Get time series data for multiple areas/countries in a single query.

    Example: /ita/data/batch?indicator=BalGds&area_codes=AllCountries,Canada,Mexico,China
    """
    codes = [c.strip() for c in area_codes.split(',') if c.strip()]

    if not codes:
        raise HTTPException(status_code=400, detail="area_codes cannot be empty")
    if len(codes) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 areas per request")

    # Get indicator info
    indicator_info = db.query(ITAIndicator).filter(ITAIndicator.indicator == indicator).first()

    # Get area info
    areas = db.query(ITAArea).filter(ITAArea.area_or_country == indicator).all()
    # Actually we need to get all areas
    all_areas = db.query(ITAArea).all()
    area_info = {a.area_or_country: a for a in all_areas}

    # Query all data in ONE query
    query = db.query(ITAData).filter(
        ITAData.indicator == indicator,
        ITAData.area_or_country.in_(codes)
    )
    if start_year:
        query = query.filter(func.substr(ITAData.time_period, 1, 4) >= str(start_year))
    if end_year:
        query = query.filter(func.substr(ITAData.time_period, 1, 4) <= str(end_year))

    data_points = query.order_by(ITAData.area_or_country, ITAData.time_period).all()

    # Group by area
    from collections import defaultdict
    grouped_data: Dict[str, List] = defaultdict(list)
    unit = None
    unit_mult = None

    for d in data_points:
        grouped_data[d.area_or_country].append({
            "time_period": d.time_period,
            "value": float(d.value) if d.value else None,
        })
        if unit is None and d.cl_unit:
            unit = d.cl_unit
        if unit_mult is None and d.unit_mult is not None:
            unit_mult = d.unit_mult

    # Build response
    result = []
    for code in codes:
        if code in grouped_data:
            info = area_info.get(code)
            result.append({
                "area_or_country": code,
                "area_description": info.area_description if info else code,
                "data": grouped_data[code],
            })

    return {
        "indicator": indicator,
        "indicator_description": indicator_info.indicator_description if indicator_info else None,
        "unit": unit,
        "unit_mult": unit_mult,
        "series": result,
    }
