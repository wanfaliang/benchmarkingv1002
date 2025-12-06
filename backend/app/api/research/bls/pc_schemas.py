"""
Pydantic schemas for PC (Producer Price Index - Industry) Survey Explorer

PC survey dimensions: Industry (NAICS) + Product
Measures price movements for net output of producers organized by NAICS.
"""
from typing import List, Optional
from pydantic import BaseModel


# ==================== Dimension Models ====================

class PCIndustryItem(BaseModel):
    """PC Industry dimension item (NAICS-based)"""
    industry_code: str
    industry_name: str
    sector: Optional[str] = None  # Derived from first 2-3 digits of NAICS

    class Config:
        from_attributes = True


class PCProductItem(BaseModel):
    """PC Product dimension item"""
    industry_code: str
    product_code: str
    product_name: str

    class Config:
        from_attributes = True


class PCDimensions(BaseModel):
    """Available dimensions for PC survey"""
    industries: List[PCIndustryItem]
    sectors: List[dict]  # Aggregated sector list for filtering
    base_years: List[int]  # Available base years (e.g., [1982, 1986, 2005, ...])
    start_years: List[int]  # Available data start years for filtering


# ==================== Series Models ====================

class PCSeriesInfo(BaseModel):
    """PC Series metadata with dimensions"""
    series_id: str
    series_title: str
    industry_code: str
    industry_name: Optional[str] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    seasonal_code: Optional[str] = None
    base_date: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class PCSeriesListResponse(BaseModel):
    """Response for PC series list with filters"""
    survey_code: str = "PC"
    total: int
    limit: int
    offset: int
    series: List[PCSeriesInfo]


# ==================== Data Models ====================

class PCDataPoint(BaseModel):
    """A single PC time series observation"""
    year: int
    period: str
    period_name: str  # "January 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class PCSeriesData(BaseModel):
    """Time series data for a single PC series"""
    series_id: str
    series_title: str
    industry_name: str
    product_name: Optional[str] = None
    base_date: Optional[str] = None
    data_points: List[PCDataPoint]


class PCDataResponse(BaseModel):
    """Response for PC series data request"""
    survey_code: str = "PC"
    series: List[PCSeriesData]


# ==================== Overview/Analytics Models ====================

class PCPriceMetric(BaseModel):
    """Internal helper for price metric calculations"""
    series_id: str
    name: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class PCSectorSummary(BaseModel):
    """PPI summary for a NAICS sector - emphasizes % changes"""
    sector_code: str
    sector_name: str
    series_id: str
    latest_date: Optional[str] = None  # "October 2024"
    # Primary metrics - percent changes (what users care about)
    mom_pct: Optional[float] = None  # Month-over-month % change
    yoy_pct: Optional[float] = None  # Year-over-year % change
    # Secondary - index value (for reference only)
    index_value: Optional[float] = None


class PCOverviewResponse(BaseModel):
    """Overview of Industry PPI by major NAICS sectors

    Note: PC survey measures producer prices by NAICS industry classification.
    For Final Demand PPI (headline numbers), see the WP survey.
    """
    survey_code: str = "PC"
    description: str = "Producer Price Index by NAICS Industry"
    sectors: List[PCSectorSummary]
    last_updated: Optional[str] = None


class PCOverviewTimelinePoint(BaseModel):
    """Single point in overview timeline - shows MoM % changes for charting"""
    year: int
    period: str
    period_name: str
    sectors: dict  # sector_code -> mom_pct (percent change for that month)


class PCOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts - shows % changes over time"""
    survey_code: str = "PC"
    timeline: List[PCOverviewTimelinePoint]
    sector_names: dict  # sector_code -> name


# ==================== Sector Analysis Models ====================

class PCSectorMetric(BaseModel):
    """PPI metric for a sector (NAICS 2-3 digit)"""
    sector_code: str
    sector_name: str
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class PCSectorAnalysisResponse(BaseModel):
    """Sector-level PPI analysis"""
    survey_code: str = "PC"
    sectors: List[PCSectorMetric]
    last_updated: Optional[str] = None


class PCSectorTimelinePoint(BaseModel):
    """Single point in sector timeline"""
    year: int
    period: str
    period_name: str
    sectors: dict  # sector_code -> value


class PCSectorTimelineResponse(BaseModel):
    """Timeline data for sector comparison charts"""
    survey_code: str = "PC"
    timeline: List[PCSectorTimelinePoint]
    sector_names: dict  # sector_code -> name


# ==================== Industry Analysis Models ====================

class PCIndustryMetric(BaseModel):
    """PPI metric for an industry"""
    industry_code: str
    industry_name: str
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class PCIndustryAnalysisResponse(BaseModel):
    """Industry-level PPI analysis"""
    survey_code: str = "PC"
    industries: List[PCIndustryMetric]
    total_count: int
    last_updated: Optional[str] = None


class PCIndustryTimelinePoint(BaseModel):
    """Single point in industry timeline"""
    year: int
    period: str
    period_name: str
    industries: dict  # industry_code -> value


class PCIndustryTimelineResponse(BaseModel):
    """Timeline data for industry comparison charts"""
    survey_code: str = "PC"
    timeline: List[PCIndustryTimelinePoint]
    industry_names: dict  # industry_code -> name


# ==================== Product Analysis Models ====================

class PCProductMetric(BaseModel):
    """PPI metric for a product within an industry"""
    industry_code: str
    industry_name: str
    product_code: str
    product_name: str
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class PCProductAnalysisResponse(BaseModel):
    """Product-level PPI analysis for an industry"""
    survey_code: str = "PC"
    industry_code: str
    industry_name: str
    products: List[PCProductMetric]
    total_count: int
    last_updated: Optional[str] = None


class PCProductTimelinePoint(BaseModel):
    """Single point in product timeline"""
    year: int
    period: str
    period_name: str
    products: dict  # product_code -> value


class PCProductTimelineResponse(BaseModel):
    """Timeline data for product comparison charts"""
    survey_code: str = "PC"
    industry_code: str
    industry_name: str
    timeline: List[PCProductTimelinePoint]
    product_names: dict  # product_code -> name


# ==================== Top Movers Models ====================

class PCTopMover(BaseModel):
    """A top mover (biggest price change)"""
    series_id: str
    industry_code: str
    industry_name: str
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    change: Optional[float] = None  # Absolute change
    change_pct: Optional[float] = None  # Percent change


class PCTopMoversResponse(BaseModel):
    """Top movers (gainers and losers)"""
    survey_code: str = "PC"
    period: str  # "mom" or "yoy"
    gainers: List[PCTopMover]
    losers: List[PCTopMover]
    last_updated: Optional[str] = None
