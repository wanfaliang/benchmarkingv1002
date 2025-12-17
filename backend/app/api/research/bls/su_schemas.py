"""
Pydantic schemas for SU (Chained CPI - All Urban Consumers) Explorer

SU Survey provides Chained Consumer Price Index data using a Tornqvist formula
that accounts for consumer substitution. Key characteristics:
- U.S. city average only (area code 0000)
- 29 item categories in hierarchical structure
- Index base: December 1999 = 100
- Monthly data from December 1999 to present
- Not seasonally adjusted

Series ID Format: SUUR0000SA0
  - SU = survey abbreviation
  - U = seasonal code (U = unadjusted)
  - R = periodicity code (R = regular monthly)
  - 0000 = area code (U.S. city average)
  - SA0 = item code (All items)

Data available monthly from December 1999-present.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class SUAreaItem(BaseModel):
    """SU Area dimension item"""
    area_code: str
    area_name: str
    display_level: Optional[int] = None
    selectable: Optional[str] = None

    class Config:
        from_attributes = True


class SUItemItem(BaseModel):
    """SU Item dimension item (expenditure category)"""
    item_code: str
    item_name: str
    display_level: Optional[int] = None
    selectable: Optional[str] = None
    sort_sequence: Optional[int] = None

    class Config:
        from_attributes = True


class SUDimensions(BaseModel):
    """Available dimensions for SU survey"""
    areas: List[SUAreaItem]
    items: List[SUItemItem]


# ==================== Series Models ====================

class SUSeriesInfo(BaseModel):
    """SU Series metadata with dimensions"""
    series_id: str
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    seasonal_code: Optional[str] = None
    periodicity_code: Optional[str] = None
    base_code: Optional[str] = None
    base_period: Optional[str] = None
    series_title: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class SUSeriesListResponse(BaseModel):
    """Response for SU series list with filters"""
    survey_code: str = "SU"
    total: int
    limit: int
    offset: int
    series: List[SUSeriesInfo]


# ==================== Data Models ====================

class SUDataPoint(BaseModel):
    """A single SU time series observation"""
    year: int
    period: str
    period_name: str
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class SUSeriesData(BaseModel):
    """SU Series with its time series data"""
    series_id: str
    series_info: SUSeriesInfo
    data: List[SUDataPoint]


class SUDataResponse(BaseModel):
    """Response for SU data query"""
    survey_code: str = "SU"
    series: List[SUSeriesData]


# ==================== Overview Models ====================

class SUCategoryMetric(BaseModel):
    """Metrics for a single expenditure category"""
    item_code: str
    item_name: str
    display_level: Optional[int] = None
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SUOverviewResponse(BaseModel):
    """Overview of C-CPI-U with key metrics"""
    survey_code: str = "SU"
    year: int
    period: str
    period_name: str
    all_items: Optional[SUCategoryMetric] = None
    core_items: Optional[SUCategoryMetric] = None  # All items less food and energy
    food: Optional[SUCategoryMetric] = None
    energy: Optional[SUCategoryMetric] = None
    housing: Optional[SUCategoryMetric] = None
    transportation: Optional[SUCategoryMetric] = None
    medical_care: Optional[SUCategoryMetric] = None
    categories: List[SUCategoryMetric]


class SUOverviewTimelinePoint(BaseModel):
    """Timeline point for overview data"""
    year: int
    period: str
    period_name: str
    items: Dict[str, Optional[float]]  # item_code -> value


class SUOverviewTimelineResponse(BaseModel):
    """Timeline data for overview"""
    survey_code: str = "SU"
    timeline: List[SUOverviewTimelinePoint]
    item_names: Dict[str, str]  # item_code -> item_name


# ==================== Category Analysis Models ====================

class SUSubcategoryMetric(BaseModel):
    """Metrics for a subcategory"""
    item_code: str
    item_name: str
    display_level: Optional[int] = None
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month_pct: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SUCategoryAnalysisResponse(BaseModel):
    """Detailed analysis for a category and its subcategories"""
    survey_code: str = "SU"
    item_code: str
    item_name: str
    year: int
    period: str
    period_name: str
    main_metric: Optional[SUCategoryMetric] = None
    subcategories: List[SUSubcategoryMetric]


class SUCategoryTimelinePoint(BaseModel):
    """Timeline point for category analysis"""
    year: int
    period: str
    period_name: str
    items: Dict[str, Optional[float]]  # item_code -> value


class SUCategoryTimelineResponse(BaseModel):
    """Timeline data for category analysis"""
    survey_code: str = "SU"
    item_code: str
    item_name: str
    timeline: List[SUCategoryTimelinePoint]
    item_names: Dict[str, str]


# ==================== Comparison Models ====================

class SUComparisonMetric(BaseModel):
    """Metric for comparing items"""
    item_code: str
    item_name: str
    series_id: str
    value: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SUComparisonResponse(BaseModel):
    """Compare multiple items at a point in time"""
    survey_code: str = "SU"
    year: int
    period: str
    period_name: str
    items: List[SUComparisonMetric]


class SUComparisonTimelinePoint(BaseModel):
    """Timeline point for comparison"""
    year: int
    period: str
    period_name: str
    items: Dict[str, Optional[float]]  # item_code -> value


class SUComparisonTimelineResponse(BaseModel):
    """Timeline data for comparison"""
    survey_code: str = "SU"
    item_codes: List[str]
    timeline: List[SUComparisonTimelinePoint]
    item_names: Dict[str, str]


# ==================== Top Movers Models ====================

class SUTopMover(BaseModel):
    """Item with largest change"""
    rank: int
    item_code: str
    item_name: str
    series_id: str
    latest_value: Optional[float] = None
    change_pct: Optional[float] = None


class SUTopMoversResponse(BaseModel):
    """Top/Bottom movers by change"""
    survey_code: str = "SU"
    year: int
    period: str
    period_name: str
    change_type: str  # 'month_over_month' or 'year_over_year'
    direction: str  # 'highest' or 'lowest'
    movers: List[SUTopMover]


# ==================== Inflation Analysis Models ====================

class SUInflationPoint(BaseModel):
    """Point in inflation time series"""
    year: int
    period: str
    period_name: str
    index_value: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SUInflationResponse(BaseModel):
    """Inflation analysis for an item"""
    survey_code: str = "SU"
    item_code: str
    item_name: str
    base_period: str
    data: List[SUInflationPoint]


# ==================== YoY Comparison Models ====================

class SUYoYComparisonPoint(BaseModel):
    """Year-over-year comparison for a specific month"""
    year: int
    period: str
    period_name: str
    items: Dict[str, Optional[float]]  # item_code -> YoY% change


class SUYoYComparisonResponse(BaseModel):
    """Year-over-year comparison timeline"""
    survey_code: str = "SU"
    timeline: List[SUYoYComparisonPoint]
    item_names: Dict[str, str]
