"""
AP (Average Price) Survey Pydantic Schemas

Average consumer prices for household fuel, motor fuel, and food items.
Three main categories:
- HouseholdFuels: Electricity, natural gas, fuel oil
- Gasoline: Regular, midgrade, premium gasoline
- Food: ~100 food categories (meat, dairy, produce, etc.)

Data characteristics:
- Prices stored to 3 decimal places
- Monthly data only (no annual averages)
- Areas: U.S. city average, 23 urban areas, 4 regions, etc.
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


# =============================================================================
# DIMENSIONS
# =============================================================================

class APAreaItem(BaseModel):
    """Area/geography for AP survey"""
    area_code: str
    area_name: str
    area_type: Optional[str] = None  # 'national', 'region', 'division', 'metro', 'size_class'


class APItemInfo(BaseModel):
    """Item (product) in AP survey"""
    item_code: str
    item_name: str
    category: Optional[str] = None  # 'Food', 'Fuel', 'Gasoline'
    unit: Optional[str] = None  # 'per lb.', 'per gallon', etc.


class APDimensions(BaseModel):
    """Available dimensions for filtering AP data"""
    areas: List[APAreaItem]
    items: List[APItemInfo]
    categories: List[str]  # ['Food', 'Gasoline', 'Household Fuels']
    total_series: int
    data_range: Optional[str] = None


# =============================================================================
# SERIES
# =============================================================================

class APSeriesInfo(BaseModel):
    """Basic series information"""
    series_id: str
    series_title: str
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    seasonal_code: Optional[str] = None
    begin_year: Optional[int] = None
    end_year: Optional[int] = None
    is_active: Optional[bool] = True


class APSeriesListResponse(BaseModel):
    """Paginated series list"""
    series: List[APSeriesInfo]
    total: int
    limit: int
    offset: int


# =============================================================================
# DATA POINTS
# =============================================================================

class APDataPoint(BaseModel):
    """Single data observation"""
    year: int
    period: str
    period_name: Optional[str] = None
    value: Optional[float] = None
    footnote_codes: Optional[str] = None


class APSeriesData(BaseModel):
    """Series with its data points"""
    series_id: str
    series_title: str
    area_name: Optional[str] = None
    item_name: Optional[str] = None
    unit: Optional[str] = None
    data: List[APDataPoint]


class APDataResponse(BaseModel):
    """Response for data queries"""
    series: List[APSeriesData]


# =============================================================================
# PRICE METRICS
# =============================================================================

class APPriceMetric(BaseModel):
    """Price metric for an item"""
    series_id: str
    item_code: str
    item_name: str
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    unit: Optional[str] = None
    latest_date: Optional[str] = None
    latest_price: Optional[float] = None
    prev_month_price: Optional[float] = None
    prev_year_price: Optional[float] = None
    mom_change: Optional[float] = None  # Month-over-month $ change
    mom_pct: Optional[float] = None  # Month-over-month % change
    yoy_change: Optional[float] = None  # Year-over-year $ change
    yoy_pct: Optional[float] = None  # Year-over-year % change


# =============================================================================
# CATEGORY OVERVIEW
# =============================================================================

class APCategoryOverview(BaseModel):
    """Overview of a category (Food, Gasoline, Household Fuels)"""
    category: str
    item_count: int
    series_count: int
    top_items: List[APPriceMetric]  # Top items by price change


class APOverviewResponse(BaseModel):
    """Overall AP survey overview"""
    latest_date: Optional[str] = None
    total_items: int
    total_series: int
    categories: List[APCategoryOverview]
    featured_prices: List[APPriceMetric]  # Key items like gasoline, bread, eggs


# =============================================================================
# AREA ANALYSIS
# =============================================================================

class APAreaMetric(BaseModel):
    """Price metrics for a specific area"""
    area_code: str
    area_name: str
    area_type: Optional[str] = None
    item_code: str
    item_name: str
    unit: Optional[str] = None
    latest_price: Optional[float] = None
    mom_pct: Optional[float] = None
    yoy_pct: Optional[float] = None


class APAreaComparisonResponse(BaseModel):
    """Compare prices across areas for an item"""
    item_code: str
    item_name: str
    unit: Optional[str] = None
    latest_date: Optional[str] = None
    areas: List[APAreaMetric]


# =============================================================================
# ITEM ANALYSIS
# =============================================================================

class APItemMetric(BaseModel):
    """Detailed metrics for an item"""
    item_code: str
    item_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    series_id: str  # National series
    latest_date: Optional[str] = None
    latest_price: Optional[float] = None
    mom_change: Optional[float] = None
    mom_pct: Optional[float] = None
    yoy_change: Optional[float] = None
    yoy_pct: Optional[float] = None
    price_52w_high: Optional[float] = None
    price_52w_low: Optional[float] = None


class APItemsAnalysisResponse(BaseModel):
    """Analysis of items in a category"""
    category: str
    latest_date: Optional[str] = None
    items: List[APItemMetric]


# =============================================================================
# TOP MOVERS
# =============================================================================

class APTopMover(BaseModel):
    """Item with significant price change"""
    series_id: str
    item_code: str
    item_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    area_name: Optional[str] = None
    latest_price: Optional[float] = None
    change: Optional[float] = None
    pct_change: Optional[float] = None
    direction: str  # 'up' or 'down'


class APTopMoversResponse(BaseModel):
    """Top price movers"""
    period: str  # 'mom' or 'yoy'
    latest_date: Optional[str] = None
    gainers: List[APTopMover]
    losers: List[APTopMover]


# =============================================================================
# TIMELINE DATA
# =============================================================================

class APTimelinePoint(BaseModel):
    """Point in time series for charts"""
    date: str  # "YYYY-MM"
    year: int
    period: str
    value: Optional[float] = None


class APItemTimelineResponse(BaseModel):
    """Timeline data for an item"""
    item_code: str
    item_name: str
    unit: Optional[str] = None
    area_name: Optional[str] = None
    timeline: List[APTimelinePoint]
