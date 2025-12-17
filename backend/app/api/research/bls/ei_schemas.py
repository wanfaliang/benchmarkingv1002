"""
Pydantic schemas for EI (Import/Export Price Indexes) Explorer

International Price Index tracks merchandise import and export price indexes
based on several classification systems and selected import and export services indexes.

Index Types (index_code):
- IR: BEA End Use Import Price Indexes
- IQ: BEA End Use Export Price Indexes
- IZ: NAICS Import Price Indexes
- IY: NAICS Export Price Indexes
- IP: Harmonized System Import Price Indexes
- ID: Harmonized System Export Price Indexes
- CO: Locality of Origin Price Indexes (Import by Country/Region)
- CD: Locality of Destination Price Indexes (Export by Country/Region)
- CT: Terms of Trade Indexes
- IV: Services Import Price Indexes
- IH: Services Export Price Indexes
- IC: Services Inbound Price Indexes
- IS: Services Outbound Price Indexes

Series ID Format: EIUCOCANMANU
  - EI = survey abbreviation
  - U = seasonal (S=adjusted, U=unadjusted)
  - CO = index_code
  - CANMANU = series_name (country/category code)

Data Range: 1980-present, updated monthly
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# ==================== Dimension Models ====================

class EIIndexItem(BaseModel):
    """EI Index type dimension item"""
    index_code: str  # 'IR', 'IQ', 'CO', 'CD', etc.
    index_name: str
    category: Optional[str] = None  # 'import', 'export', 'services', 'trade'

    class Config:
        from_attributes = True


class EICountryItem(BaseModel):
    """Country/Region extracted from series"""
    country_code: str  # Extracted from series_name
    country_name: str
    index_code: str  # 'CO' for import origin, 'CD' for export destination
    series_count: int = 0

    class Config:
        from_attributes = True


class EIDimensions(BaseModel):
    """Available dimensions for EI survey"""
    indexes: List[EIIndexItem]
    import_indexes: List[EIIndexItem]  # IR, IZ, IP, IV, IC
    export_indexes: List[EIIndexItem]  # IQ, IY, ID, IH, IS
    origin_countries: List[EICountryItem]  # CO index countries
    destination_countries: List[EICountryItem]  # CD index countries
    available_years: List[int]
    available_periods: List[str]


# ==================== Series Models ====================

class EISeriesInfo(BaseModel):
    """EI Series metadata"""
    series_id: str
    seasonal_code: Optional[str] = None
    index_code: Optional[str] = None
    index_name: Optional[str] = None
    series_name: Optional[str] = None
    base_period: Optional[str] = None
    series_title: Optional[str] = None
    footnote_codes: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True
    # Derived fields
    country_region: Optional[str] = None  # Extracted country/region for CO/CD
    industry_category: Optional[str] = None  # Extracted industry for CO/CD

    class Config:
        from_attributes = True


class EISeriesListResponse(BaseModel):
    """Response for EI series list"""
    survey_code: str = "EI"
    total: int
    limit: int
    offset: int
    series: List[EISeriesInfo]


# ==================== Data Models ====================

class EIDataPoint(BaseModel):
    """A single EI time series observation"""
    year: int
    period: str  # 'M01'-'M12', 'M13' (annual)
    period_name: str
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class EISeriesData(BaseModel):
    """Time series data for a single EI series"""
    series_id: str
    series_info: EISeriesInfo
    data_points: List[EIDataPoint]


class EIDataResponse(BaseModel):
    """Response for EI series data queries"""
    survey_code: str = "EI"
    series_count: int
    total_observations: int
    series: List[EISeriesData]


# ==================== Overview Models ====================

class EIOverviewMetric(BaseModel):
    """Overview metric for import/export indexes"""
    metric_name: str
    series_id: str
    index_code: str
    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    mom_change: Optional[float] = None  # Month-over-month
    yoy_change: Optional[float] = None  # Year-over-year
    yoy_pct_change: Optional[float] = None


class EIOverviewResponse(BaseModel):
    """Overview of import/export price indexes"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    # All imports/exports
    all_imports: Optional[EIOverviewMetric] = None
    all_exports: Optional[EIOverviewMetric] = None
    imports_ex_fuel: Optional[EIOverviewMetric] = None
    exports_ex_fuel: Optional[EIOverviewMetric] = None
    terms_of_trade: Optional[EIOverviewMetric] = None
    # Key metrics list
    import_metrics: List[EIOverviewMetric]
    export_metrics: List[EIOverviewMetric]
    available_years: List[int]
    available_periods: List[str]


class EIOverviewTimelinePoint(BaseModel):
    """Timeline data point for overview"""
    year: int
    period: str
    period_name: str
    all_imports: Optional[float] = None
    all_exports: Optional[float] = None
    imports_ex_fuel: Optional[float] = None
    exports_ex_fuel: Optional[float] = None
    terms_of_trade: Optional[float] = None


class EIOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "EI"
    data: List[EIOverviewTimelinePoint]


# ==================== Country/Region Comparison Models ====================

class EICountryComparisonItem(BaseModel):
    """Single country in comparison"""
    country_code: str
    country_name: str
    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None
    yoy_pct_change: Optional[float] = None


class EICountryComparisonResponse(BaseModel):
    """Country comparison data"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    direction: str  # 'import' (CO) or 'export' (CD)
    industry_filter: Optional[str] = None  # 'All Industries', 'Manufacturing', etc.
    countries: List[EICountryComparisonItem]


class EICountryTimelinePoint(BaseModel):
    """Timeline point for country comparison"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]  # country_code -> value


class EICountryTimelineResponse(BaseModel):
    """Country comparison timeline"""
    survey_code: str = "EI"
    direction: str
    industry_filter: Optional[str] = None
    countries: List[EICountryItem]
    data: List[EICountryTimelinePoint]


# ==================== Trade Flow Models (Special Graph) ====================

class EITradeFlowItem(BaseModel):
    """Trade flow data item for Sankey/flow chart"""
    country_code: str
    country_name: str
    direction: str  # 'import' or 'export'
    value: Optional[float] = None
    change: Optional[float] = None
    pct_of_total: Optional[float] = None


class EITradeFlowResponse(BaseModel):
    """Trade flow data for visualization"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    base_country: str = "United States"
    imports: List[EITradeFlowItem]
    exports: List[EITradeFlowItem]
    # Summary
    total_import_index: Optional[float] = None
    total_export_index: Optional[float] = None
    terms_of_trade: Optional[float] = None


class EITradeBalanceItem(BaseModel):
    """Trade balance (price index difference) by country"""
    country_code: str
    country_name: str
    import_index: Optional[float] = None
    export_index: Optional[float] = None
    price_differential: Optional[float] = None  # export - import index


class EITradeBalanceResponse(BaseModel):
    """Trade balance comparison"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    countries: List[EITradeBalanceItem]


class EITradeBalanceTimelinePoint(BaseModel):
    """Timeline point for trade balance"""
    year: int
    period: str
    period_name: str
    import_index: Optional[float] = None
    export_index: Optional[float] = None
    differential: Optional[float] = None


class EITradeBalanceTimelineResponse(BaseModel):
    """Trade balance timeline for a country"""
    survey_code: str = "EI"
    country_code: str
    country_name: str
    data: List[EITradeBalanceTimelinePoint]


# ==================== Index Category Comparison Models ====================

class EIIndexCategoryItem(BaseModel):
    """Index category comparison item"""
    series_id: str
    series_name: str
    index_code: str
    current_value: Optional[float] = None
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None


class EIIndexCategoryResponse(BaseModel):
    """Index category comparison (BEA, NAICS, Harmonized)"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    direction: str  # 'import' or 'export'
    classification: str  # 'BEA', 'NAICS', 'Harmonized'
    categories: List[EIIndexCategoryItem]


class EIIndexCategoryTimelinePoint(BaseModel):
    """Timeline point for index category"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]  # series_id -> value


class EIIndexCategoryTimelineResponse(BaseModel):
    """Index category timeline"""
    survey_code: str = "EI"
    direction: str
    classification: str
    series: List[EISeriesInfo]
    data: List[EIIndexCategoryTimelinePoint]


# ==================== Services Trade Models ====================

class EIServicesItem(BaseModel):
    """Services trade item"""
    series_id: str
    series_name: str
    direction: str  # 'import', 'export', 'inbound', 'outbound'
    current_value: Optional[float] = None
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None


class EIServicesResponse(BaseModel):
    """Services trade data"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    import_services: List[EIServicesItem]
    export_services: List[EIServicesItem]
    inbound_services: List[EIServicesItem]
    outbound_services: List[EIServicesItem]


class EIServicesTimelinePoint(BaseModel):
    """Timeline point for services"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]  # series_id -> value


class EIServicesTimelineResponse(BaseModel):
    """Services timeline data"""
    survey_code: str = "EI"
    series: List[EISeriesInfo]
    data: List[EIServicesTimelinePoint]


# ==================== Terms of Trade Models ====================

class EITermsOfTradeItem(BaseModel):
    """Terms of trade item"""
    series_id: str
    series_name: str
    current_value: Optional[float] = None
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None


class EITermsOfTradeResponse(BaseModel):
    """Terms of trade data"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    terms: List[EITermsOfTradeItem]


class EITermsOfTradeTimelinePoint(BaseModel):
    """Timeline point for terms of trade"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]


class EITermsOfTradeTimelineResponse(BaseModel):
    """Terms of trade timeline"""
    survey_code: str = "EI"
    series: List[EISeriesInfo]
    data: List[EITermsOfTradeTimelinePoint]


# ==================== Historical Trends Models ====================

class EITrendPoint(BaseModel):
    """A single trend data point"""
    year: int
    period: str
    period_name: str
    value: Optional[float] = None
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None
    yoy_pct_change: Optional[float] = None


class EITrendResponse(BaseModel):
    """Historical trend data"""
    survey_code: str = "EI"
    series_id: str
    series_info: EISeriesInfo
    data: List[EITrendPoint]


# ==================== Top Movers Models ====================

class EITopMoverItem(BaseModel):
    """Top mover item"""
    series_id: str
    series_name: str
    index_code: str
    country_region: Optional[str] = None
    current_value: Optional[float] = None
    change: Optional[float] = None
    pct_change: Optional[float] = None


class EITopMoversResponse(BaseModel):
    """Top movers response"""
    survey_code: str = "EI"
    year: int
    period: str
    period_name: str
    direction: str  # 'import', 'export', or 'all'
    metric: str  # 'mom_change', 'yoy_change'
    top_gainers: List[EITopMoverItem]
    top_losers: List[EITopMoverItem]
