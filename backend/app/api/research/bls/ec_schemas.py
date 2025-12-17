"""
EC Explorer Pydantic Schemas
Employment Cost Index (ECI) - Quarterly measure of change in labor costs
Legacy survey with data from 1980-2005
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class ECDimensionItem(BaseModel):
    """Generic dimension item"""
    code: str
    name: str


class ECDimensions(BaseModel):
    """All available EC dimensions for filtering"""
    compensations: List[ECDimensionItem]  # Total compensation, Wages, Benefits
    groups: List[ECDimensionItem]  # Worker groups (occupation/industry)
    ownerships: List[ECDimensionItem]  # Civilian, Private, State/Local govt
    periodicities: List[ECDimensionItem]  # Index, 3-month %, 12-month %


# ==================== Series Models ====================

class ECSeriesInfo(BaseModel):
    """EC Series metadata"""
    series_id: str
    comp_code: Optional[str] = None
    comp_name: Optional[str] = None
    group_code: Optional[str] = None
    group_name: Optional[str] = None
    ownership_code: Optional[str] = None
    ownership_name: Optional[str] = None
    periodicity_code: Optional[str] = None
    periodicity_name: Optional[str] = None
    seasonal: str  # S = Seasonally adjusted, U = Unadjusted

    # Time range
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None

    is_active: bool = True

    class Config:
        from_attributes = True


class ECSeriesListResponse(BaseModel):
    """Response for series list endpoint"""
    survey_code: str = "EC"
    total: int
    limit: int
    offset: int
    series: List[ECSeriesInfo]


# ==================== Data Models ====================

class ECDataPoint(BaseModel):
    """Single data observation"""
    year: int
    period: str
    period_name: str
    value: Optional[float] = None
    footnote_codes: Optional[str] = None


class ECSeriesData(BaseModel):
    """Time series data for a single series"""
    series_id: str
    series_title: str
    data_points: List[ECDataPoint]


class ECDataResponse(BaseModel):
    """Response for series data endpoint"""
    survey_code: str = "EC"
    series: List[ECSeriesData]


# ==================== Overview Models ====================

class ECCostMetric(BaseModel):
    """Employment cost metric"""
    series_id: str
    name: str  # Descriptive name
    comp_type: str  # compensation type name
    periodicity_type: str  # Index, 3-month change, 12-month change
    latest_value: Optional[float] = None
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None
    previous_value: Optional[float] = None
    yoy_change: Optional[float] = None  # Year-over-year change


class ECOverviewResponse(BaseModel):
    """Overview dashboard with headline ECI metrics"""
    survey_code: str = "EC"
    ownership: str
    ownership_name: str

    # Headline index values
    total_compensation_index: Optional[ECCostMetric] = None
    wages_salaries_index: Optional[ECCostMetric] = None
    benefits_index: Optional[ECCostMetric] = None

    # Recent percent changes
    total_compensation_quarterly: Optional[ECCostMetric] = None
    wages_salaries_quarterly: Optional[ECCostMetric] = None
    benefits_quarterly: Optional[ECCostMetric] = None

    total_compensation_annual: Optional[ECCostMetric] = None
    wages_salaries_annual: Optional[ECCostMetric] = None
    benefits_annual: Optional[ECCostMetric] = None

    data_range: Optional[str] = None  # e.g., "Q1 1980 - Q4 2005"


# ==================== Timeline Models ====================

class ECTimelinePoint(BaseModel):
    """Timeline point for EC index"""
    year: int
    period: str
    period_name: str
    total_compensation: Optional[float] = None
    wages_salaries: Optional[float] = None
    benefits: Optional[float] = None


class ECTimelineResponse(BaseModel):
    """Timeline data for EC indices"""
    survey_code: str = "EC"
    ownership: str
    ownership_name: str
    periodicity: str  # Index, quarterly change, annual change
    timeline: List[ECTimelinePoint]


# ==================== Group Analysis Models ====================

class ECGroupMetric(BaseModel):
    """Cost metric for a worker group"""
    group_code: str
    group_name: str
    index_value: Optional[float] = None
    quarterly_change: Optional[float] = None
    annual_change: Optional[float] = None
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class ECGroupAnalysisResponse(BaseModel):
    """Analysis by worker group"""
    survey_code: str = "EC"
    ownership: str
    ownership_name: str
    comp_type: str  # Total compensation, Wages, Benefits
    groups: List[ECGroupMetric]
    latest_year: Optional[int] = None


class ECGroupTimelinePoint(BaseModel):
    """Timeline point for group comparison"""
    year: int
    period: str
    period_name: str
    groups: Dict[str, Optional[float]]  # group_code -> value


class ECGroupTimelineResponse(BaseModel):
    """Timeline data for group comparison"""
    survey_code: str = "EC"
    ownership: str
    periodicity: str
    comp_type: str
    timeline: List[ECGroupTimelinePoint]
    group_names: Dict[str, str]  # group_code -> group_name


# ==================== Ownership Comparison Models ====================

class ECOwnershipMetric(BaseModel):
    """Metric comparing across ownership types"""
    ownership_code: str
    ownership_name: str
    index_value: Optional[float] = None
    quarterly_change: Optional[float] = None
    annual_change: Optional[float] = None


class ECOwnershipComparisonResponse(BaseModel):
    """Comparison across ownership types"""
    survey_code: str = "EC"
    comp_type: str
    group_name: str
    ownerships: List[ECOwnershipMetric]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class ECOwnershipTimelinePoint(BaseModel):
    """Timeline point for ownership comparison"""
    year: int
    period: str
    period_name: str
    ownerships: Dict[str, Optional[float]]  # ownership_code -> value


class ECOwnershipTimelineResponse(BaseModel):
    """Timeline data for ownership comparison"""
    survey_code: str = "EC"
    comp_type: str
    periodicity: str
    timeline: List[ECOwnershipTimelinePoint]
    ownership_names: Dict[str, str]
