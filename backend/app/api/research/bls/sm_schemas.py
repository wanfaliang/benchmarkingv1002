"""
Pydantic schemas for SM (State and Metro Area Employment) Survey Explorer

SM survey dimensions: State + Area (MSA) + Supersector + Industry + Data Type
Measures employment (thousands), average weekly hours, and average hourly/weekly earnings
for all 50 states, DC, Puerto Rico, Virgin Islands, and ~450 metropolitan areas.

Series ID Format: SMU01266207072200001
  - SM = survey abbreviation
  - U = seasonal code (S=Seasonally Adjusted, U=Unadjusted)
  - 01 = state_code (2 digits, FIPS)
  - 26620 = area_code (5 digits, '00000'=Statewide)
  - 70 = supersector_code (2 digits)
  - 70722000 = industry_code (8 digits NAICS)
  - 01 = data_type_code (2 digits)
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class SMStateItem(BaseModel):
    """SM State dimension item"""
    state_code: str
    state_name: str

    class Config:
        from_attributes = True


class SMAreaItem(BaseModel):
    """SM Area dimension item (MSA/Metro areas)"""
    area_code: str
    area_name: str

    class Config:
        from_attributes = True


class SMSupersectorItem(BaseModel):
    """SM Supersector dimension item"""
    supersector_code: str
    supersector_name: str

    class Config:
        from_attributes = True


class SMIndustryItem(BaseModel):
    """SM Industry dimension item (NAICS-based)"""
    industry_code: str
    industry_name: str
    supersector: Optional[str] = None  # Derived from first 2 digits

    class Config:
        from_attributes = True


class SMDataTypeItem(BaseModel):
    """SM Data type dimension item"""
    data_type_code: str
    data_type_name: str

    class Config:
        from_attributes = True


class SMDimensions(BaseModel):
    """Available dimensions for SM survey"""
    states: List[SMStateItem]
    areas: List[SMAreaItem]
    supersectors: List[SMSupersectorItem]
    data_types: List[SMDataTypeItem]


# ==================== Series Models ====================

class SMSeriesInfo(BaseModel):
    """SM Series metadata with dimensions"""
    series_id: str
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    supersector_code: Optional[str] = None
    supersector_name: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    data_type_code: Optional[str] = None
    data_type_name: Optional[str] = None
    seasonal_code: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class SMSeriesListResponse(BaseModel):
    """Response for SM series list with filters"""
    survey_code: str = "SM"
    total: int
    limit: int
    offset: int
    series: List[SMSeriesInfo]


# ==================== Data Models ====================

class SMDataPoint(BaseModel):
    """A single SM time series observation"""
    year: int
    period: str
    period_name: str  # "January 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class SMSeriesData(BaseModel):
    """Time series data for a single SM series"""
    series_id: str
    state_name: Optional[str] = None
    area_name: Optional[str] = None
    supersector_name: Optional[str] = None
    industry_name: Optional[str] = None
    data_type_name: Optional[str] = None
    data_points: List[SMDataPoint]


class SMDataResponse(BaseModel):
    """Response for SM series data request"""
    survey_code: str = "SM"
    series: List[SMSeriesData]


# ==================== Overview/Analytics Models ====================

class SMEmploymentMetric(BaseModel):
    """Employment metric for a geographic area"""
    series_id: str
    area_code: str
    area_name: str
    area_type: str  # "State", "Metro", "Statewide"
    employment: Optional[float] = None  # All employees (thousands)
    avg_weekly_hours: Optional[float] = None
    avg_hourly_earnings: Optional[float] = None
    avg_weekly_earnings: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None  # Employment change
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SMSupersectorSummary(BaseModel):
    """Employment summary for a supersector"""
    supersector_code: str
    supersector_name: str
    series_id: str
    employment: Optional[float] = None
    latest_date: Optional[str] = None
    mom_change: Optional[float] = None
    mom_pct: Optional[float] = None
    yoy_change: Optional[float] = None
    yoy_pct: Optional[float] = None


class SMOverviewResponse(BaseModel):
    """Overview of State & Metro Employment by major supersectors

    Shows Total Nonfarm employment breakdown for a selected state/area.
    """
    survey_code: str = "SM"
    description: str = "State and Metro Area Employment Statistics"
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    supersectors: List[SMSupersectorSummary]
    last_updated: Optional[str] = None


class SMOverviewTimelinePoint(BaseModel):
    """Single point in overview timeline - shows employment by supersector"""
    year: int
    period: str
    period_name: str
    supersectors: Dict[str, Optional[float]]  # supersector_code -> employment


class SMOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "SM"
    state_name: Optional[str] = None
    area_name: Optional[str] = None
    timeline: List[SMOverviewTimelinePoint]
    supersector_names: Dict[str, str]  # supersector_code -> name


# ==================== State Analysis Models ====================

class SMStateMetric(BaseModel):
    """Employment metric for a state"""
    state_code: str
    state_name: str
    series_id: str
    employment: Optional[float] = None  # Total Nonfarm (thousands)
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SMStateAnalysisResponse(BaseModel):
    """State-level employment analysis"""
    survey_code: str = "SM"
    states: List[SMStateMetric]
    rankings: Dict[str, List[str]]  # "highest_employment", "highest_growth"
    last_updated: Optional[str] = None


class SMStateTimelinePoint(BaseModel):
    """Single point in state timeline"""
    year: int
    period: str
    period_name: str
    states: Dict[str, Optional[float]]  # state_code -> employment


class SMStateTimelineResponse(BaseModel):
    """Timeline data for state comparison charts"""
    survey_code: str = "SM"
    timeline: List[SMStateTimelinePoint]
    state_names: Dict[str, str]  # state_code -> name


# ==================== Metro Analysis Models ====================

class SMMetroMetric(BaseModel):
    """Employment metric for a metropolitan area"""
    state_code: str
    state_name: str
    area_code: str
    area_name: str
    series_id: str
    employment: Optional[float] = None  # Total Nonfarm (thousands)
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SMMetroAnalysisResponse(BaseModel):
    """Metro-level employment analysis"""
    survey_code: str = "SM"
    metros: List[SMMetroMetric]
    total_count: int
    last_updated: Optional[str] = None


class SMMetroTimelinePoint(BaseModel):
    """Single point in metro timeline"""
    year: int
    period: str
    period_name: str
    metros: Dict[str, Optional[float]]  # area_code -> employment


class SMMetroTimelineResponse(BaseModel):
    """Timeline data for metro comparison charts"""
    survey_code: str = "SM"
    timeline: List[SMMetroTimelinePoint]
    metro_names: Dict[str, str]  # area_code -> name


# ==================== Supersector Analysis Models ====================

class SMSupersectorMetric(BaseModel):
    """Employment metric for a supersector within a state/area"""
    supersector_code: str
    supersector_name: str
    series_id: str
    employment: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SMSupersectorAnalysisResponse(BaseModel):
    """Supersector-level employment analysis for a state/area"""
    survey_code: str = "SM"
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    supersectors: List[SMSupersectorMetric]
    last_updated: Optional[str] = None


class SMSupersectorTimelinePoint(BaseModel):
    """Single point in supersector timeline"""
    year: int
    period: str
    period_name: str
    supersectors: Dict[str, Optional[float]]  # supersector_code -> employment


class SMSupersectorTimelineResponse(BaseModel):
    """Timeline data for supersector comparison charts"""
    survey_code: str = "SM"
    state_name: Optional[str] = None
    area_name: Optional[str] = None
    timeline: List[SMSupersectorTimelinePoint]
    supersector_names: Dict[str, str]  # supersector_code -> name


# ==================== Industry Analysis Models ====================

class SMIndustryMetric(BaseModel):
    """Employment metric for an industry within a state/area"""
    industry_code: str
    industry_name: str
    supersector_code: Optional[str] = None
    supersector_name: Optional[str] = None
    series_id: str
    employment: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class SMIndustryAnalysisResponse(BaseModel):
    """Industry-level employment analysis for a state/area"""
    survey_code: str = "SM"
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    industries: List[SMIndustryMetric]
    total_count: int
    last_updated: Optional[str] = None


class SMIndustryTimelinePoint(BaseModel):
    """Single point in industry timeline"""
    year: int
    period: str
    period_name: str
    industries: Dict[str, Optional[float]]  # industry_code -> employment


class SMIndustryTimelineResponse(BaseModel):
    """Timeline data for industry comparison charts"""
    survey_code: str = "SM"
    state_name: Optional[str] = None
    area_name: Optional[str] = None
    timeline: List[SMIndustryTimelinePoint]
    industry_names: Dict[str, str]  # industry_code -> name


# ==================== Top Movers Models ====================

class SMTopMover(BaseModel):
    """A top mover (biggest employment change)"""
    series_id: str
    state_code: str
    state_name: str
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    supersector_code: Optional[str] = None
    supersector_name: Optional[str] = None
    employment: Optional[float] = None
    latest_date: Optional[str] = None
    change: Optional[float] = None  # Absolute change (thousands)
    change_pct: Optional[float] = None  # Percent change


class SMTopMoversResponse(BaseModel):
    """Top movers (gainers and losers)"""
    survey_code: str = "SM"
    period: str  # "mom" or "yoy"
    gainers: List[SMTopMover]
    losers: List[SMTopMover]
    last_updated: Optional[str] = None
