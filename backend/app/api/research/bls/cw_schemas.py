"""
Pydantic schemas for CW (Consumer Price Index - Urban Wage Earners and Clerical Workers) Survey Explorer

CW survey is identical in structure to CU but covers a different population:
- CU: All Urban Consumers (about 93% of U.S. population)
- CW: Urban Wage Earners and Clerical Workers (about 29% of U.S. population)

CW is used for:
- Social Security COLA adjustments
- Federal civil service retirees
- Military retirees
- Food stamp program benefits

Dimensions: Area + Item (same as CU)
"""
from typing import List, Optional
from pydantic import BaseModel


# ==================== Dimension Models ====================

class CWAreaItem(BaseModel):
    """CW Area dimension item"""
    area_code: str
    area_name: str
    display_level: int
    selectable: bool
    sort_sequence: int

    class Config:
        from_attributes = True


class CWItemItem(BaseModel):
    """CW Item dimension item"""
    item_code: str
    item_name: str
    display_level: int
    selectable: bool
    sort_sequence: int

    class Config:
        from_attributes = True


class CWDimensions(BaseModel):
    """Available dimensions for CW survey"""
    areas: List[CWAreaItem]
    items: List[CWItemItem]
    total_series: int
    data_range: Optional[str] = None


# ==================== Series Models ====================

class CWSeriesInfo(BaseModel):
    """CW Series metadata with dimensions"""
    series_id: str
    series_title: str
    area_code: str
    area_name: str
    item_code: str
    item_name: str
    seasonal_code: str
    periodicity_code: Optional[str] = None
    base_period: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class CWSeriesListResponse(BaseModel):
    """Response for CW series list with filters"""
    survey_code: str = "CW"
    total: int
    limit: int
    offset: int
    series: List[CWSeriesInfo]


# ==================== Data Models ====================

class CWDataPoint(BaseModel):
    """A single CW time series observation"""
    year: int
    period: str
    period_name: str  # "January 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class CWSeriesData(BaseModel):
    """Time series data for a single CW series"""
    series_id: str
    series_title: str
    area_name: str
    item_name: str
    data_points: List[CWDataPoint]


class CWDataResponse(BaseModel):
    """Response for CW series data request"""
    survey_code: str = "CW"
    series: List[CWSeriesData]


# ==================== Analytics Models ====================

class InflationMetric(BaseModel):
    """Inflation rate metrics for a single series"""
    series_id: str
    item_code: str
    item_name: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None  # "January 2024"
    month_over_month: Optional[float] = None  # % change
    year_over_year: Optional[float] = None  # % change


class CWOverviewResponse(BaseModel):
    """Overview dashboard data for CPI-W"""
    survey_code: str = "CW"
    headline_cpi: Optional[InflationMetric] = None  # All items (SA0)
    core_cpi: Optional[InflationMetric] = None  # All items less food and energy (SA0L1E)
    food_beverages: Optional[InflationMetric] = None  # SAF
    housing: Optional[InflationMetric] = None  # SAH
    apparel: Optional[InflationMetric] = None  # SAA
    transportation: Optional[InflationMetric] = None  # SAT
    medical_care: Optional[InflationMetric] = None  # SAM
    recreation: Optional[InflationMetric] = None  # SAR
    education_communication: Optional[InflationMetric] = None  # SAE
    other_goods_services: Optional[InflationMetric] = None  # SAG
    energy: Optional[InflationMetric] = None  # SA0E
    last_updated: Optional[str] = None


class CategoryMetric(BaseModel):
    """Metrics for a major CPI-W category"""
    category_code: str
    category_name: str
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    year_over_year: Optional[float] = None
    weight: Optional[float] = None  # Relative importance


class CWCategoryAnalysisResponse(BaseModel):
    """Category analysis with aggregated trends"""
    survey_code: str = "CW"
    area_code: str
    area_name: str
    categories: List[CategoryMetric]


class AreaComparisonMetric(BaseModel):
    """Comparison metric for a single area"""
    area_code: str
    area_name: str
    area_type: Optional[str] = None  # 'national', 'region', 'metro', 'size_class'
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    year_over_year: Optional[float] = None


class CWAreaComparisonResponse(BaseModel):
    """Compare same item across different areas"""
    survey_code: str = "CW"
    item_code: str
    item_name: str
    areas: List[AreaComparisonMetric]


# ==================== Timeline Models ====================

class TimelineDataPoint(BaseModel):
    """A single point in the timeline with inflation metrics"""
    year: int
    period: str  # "M01", "M02", etc.
    period_name: str  # "Jan 2024"
    date: str  # "2024-01" for charts
    headline_value: Optional[float] = None
    headline_yoy: Optional[float] = None
    headline_mom: Optional[float] = None
    core_value: Optional[float] = None
    core_yoy: Optional[float] = None
    core_mom: Optional[float] = None


class CWOverviewTimelineResponse(BaseModel):
    """Timeline data for overview dashboard"""
    survey_code: str = "CW"
    area_code: str
    area_name: str
    timeline: List[TimelineDataPoint]


class CategoryTimelineData(BaseModel):
    """Timeline data for a single category"""
    category_code: str
    category_name: str
    series_id: str
    data: List[dict]  # [{date, value, yoy, mom}, ...]


class CWCategoryTimelineResponse(BaseModel):
    """Timeline data for category analysis"""
    survey_code: str = "CW"
    area_code: str
    area_name: str
    categories: List[CategoryTimelineData]


class AreaTimelineData(BaseModel):
    """Timeline data for a single area"""
    area_code: str
    area_name: str
    series_id: str
    data: List[dict]  # [{date, value, yoy, mom}, ...]


class CWAreaTimelineResponse(BaseModel):
    """Timeline data for area comparison"""
    survey_code: str = "CW"
    item_code: str
    item_name: str
    areas: List[AreaTimelineData]


# ==================== Top Movers ====================

class CWTopMover(BaseModel):
    """Item with significant index change"""
    series_id: str
    item_code: str
    item_name: str
    area_name: Optional[str] = None
    latest_value: Optional[float] = None
    change: Optional[float] = None  # Index point change
    pct_change: Optional[float] = None  # % change
    direction: str  # 'up' or 'down'


class CWTopMoversResponse(BaseModel):
    """Top CPI-W movers"""
    survey_code: str = "CW"
    period: str  # 'mom' or 'yoy'
    latest_date: Optional[str] = None
    gainers: List[CWTopMover]
    losers: List[CWTopMover]
