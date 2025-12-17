"""
Pydantic schemas for WP (Producer Price Index - Commodities) Survey Explorer

WP survey dimensions: Group + Item
Contains both traditional commodity groupings AND Final Demand-Intermediate Demand (FD-ID)
which provides the headline PPI numbers reported in press releases.

Key Groups:
- Traditional: 01-15 commodity groups
- FD-ID: Final Demand (headline PPI), Intermediate Demand stages
"""
from typing import List, Optional
from pydantic import BaseModel


# ==================== Dimension Models ====================

class WPGroupItem(BaseModel):
    """WP Group dimension item"""
    group_code: str
    group_name: str
    is_final_demand: bool = False  # True for FD-ID groups (headline PPI)

    class Config:
        from_attributes = True


class WPItemInfo(BaseModel):
    """WP Item dimension item"""
    group_code: str
    item_code: str
    item_name: str

    class Config:
        from_attributes = True


class WPDimensions(BaseModel):
    """Available dimensions for WP survey"""
    groups: List[WPGroupItem]
    final_demand_groups: List[WPGroupItem]  # FD-ID groups only (for headline section)
    commodity_groups: List[WPGroupItem]  # Traditional commodity groups
    base_years: List[int]
    start_years: List[int]


# ==================== Series Models ====================

class WPSeriesInfo(BaseModel):
    """WP Series metadata with dimensions"""
    series_id: str
    series_title: str
    group_code: str
    group_name: Optional[str] = None
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    seasonal_code: Optional[str] = None
    base_date: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class WPSeriesListResponse(BaseModel):
    """Response for WP series list with filters"""
    survey_code: str = "WP"
    total: int
    limit: int
    offset: int
    series: List[WPSeriesInfo]


# ==================== Data Models ====================

class WPDataPoint(BaseModel):
    """A single WP time series observation"""
    year: int
    period: str
    period_name: str  # "January 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class WPSeriesData(BaseModel):
    """Time series data for a single WP series"""
    series_id: str
    series_title: str
    group_name: str
    item_name: Optional[str] = None
    base_date: Optional[str] = None
    data_points: List[WPDataPoint]


class WPDataResponse(BaseModel):
    """Response for WP series data request"""
    survey_code: str = "WP"
    series: List[WPSeriesData]


# ==================== Final Demand Overview (Headline PPI) ====================

class WPHeadlinePPI(BaseModel):
    """Headline PPI metrics - the numbers reported in press releases

    Final Demand PPI is the primary measure of producer price inflation.
    """
    series_id: str
    name: str  # "Final Demand", "Final Demand Goods", "Final Demand Services", etc.
    latest_date: Optional[str] = None
    # Primary metrics - percent changes (headline numbers)
    mom_pct: Optional[float] = None  # Month-over-month % change (THE headline number)
    yoy_pct: Optional[float] = None  # Year-over-year % change
    # Secondary - index value
    index_value: Optional[float] = None


class WPFinalDemandOverview(BaseModel):
    """Final Demand PPI overview - headline numbers

    This is what BLS reports in monthly press releases:
    - Final Demand (total)
    - Final Demand Goods
    - Final Demand Services
    - Final Demand excluding foods, energy, and trade services (core)
    """
    survey_code: str = "WP"
    description: str = "Producer Price Index - Final Demand (Headline PPI)"
    headline: WPHeadlinePPI  # Total Final Demand
    components: List[WPHeadlinePPI]  # Goods, Services, Core, etc.
    last_updated: Optional[str] = None


class WPOverviewTimelinePoint(BaseModel):
    """Single point in overview timeline - shows MoM % changes"""
    year: int
    period: str
    period_name: str
    categories: dict  # category_key -> mom_pct


class WPOverviewTimelineResponse(BaseModel):
    """Timeline data for Final Demand overview charts"""
    survey_code: str = "WP"
    timeline: List[WPOverviewTimelinePoint]
    category_names: dict  # category_key -> name


# ==================== Commodity Group Analysis ====================

class WPGroupMetric(BaseModel):
    """PPI metric for a commodity group"""
    group_code: str
    group_name: str
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    mom_pct: Optional[float] = None
    yoy_pct: Optional[float] = None


class WPGroupAnalysisResponse(BaseModel):
    """Group-level PPI analysis"""
    survey_code: str = "WP"
    groups: List[WPGroupMetric]
    last_updated: Optional[str] = None


class WPGroupTimelinePoint(BaseModel):
    """Single point in group timeline"""
    year: int
    period: str
    period_name: str
    groups: dict  # group_code -> value


class WPGroupTimelineResponse(BaseModel):
    """Timeline data for group comparison charts"""
    survey_code: str = "WP"
    timeline: List[WPGroupTimelinePoint]
    group_names: dict


# ==================== Item Analysis ====================

class WPItemMetric(BaseModel):
    """PPI metric for an item within a group"""
    group_code: str
    group_name: str
    item_code: str
    item_name: str
    series_id: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    mom_pct: Optional[float] = None
    yoy_pct: Optional[float] = None


class WPItemAnalysisResponse(BaseModel):
    """Item-level PPI analysis for a group"""
    survey_code: str = "WP"
    group_code: str
    group_name: str
    items: List[WPItemMetric]
    total_count: int
    last_updated: Optional[str] = None


class WPItemTimelinePoint(BaseModel):
    """Single point in item timeline"""
    year: int
    period: str
    period_name: str
    items: dict  # item_code -> value


class WPItemTimelineResponse(BaseModel):
    """Timeline data for item comparison charts"""
    survey_code: str = "WP"
    group_code: str
    group_name: str
    timeline: List[WPItemTimelinePoint]
    item_names: dict


# ==================== Intermediate Demand Analysis ====================

class WPIntermediateDemandStage(BaseModel):
    """Intermediate Demand stage metrics

    The production flow stages:
    - Stage 4: Processed goods for intermediate demand
    - Stage 3: Processed goods for intermediate demand
    - Stage 2: Processed goods for intermediate demand
    - Stage 1: Unprocessed goods for intermediate demand
    """
    stage: str  # "stage1", "stage2", etc.
    stage_name: str
    series_id: str
    latest_date: Optional[str] = None
    mom_pct: Optional[float] = None
    yoy_pct: Optional[float] = None
    index_value: Optional[float] = None


class WPIntermediateDemandResponse(BaseModel):
    """Intermediate Demand breakdown by production stages"""
    survey_code: str = "WP"
    description: str = "Producer Price Index - Intermediate Demand by Production Stage"
    stages: List[WPIntermediateDemandStage]
    last_updated: Optional[str] = None


# ==================== Top Movers ====================

class WPTopMover(BaseModel):
    """A top mover (biggest price change)"""
    series_id: str
    group_code: str
    group_name: str
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None


class WPTopMoversResponse(BaseModel):
    """Top movers (gainers and losers)"""
    survey_code: str = "WP"
    period: str  # "mom" or "yoy"
    gainers: List[WPTopMover]
    losers: List[WPTopMover]
    last_updated: Optional[str] = None
