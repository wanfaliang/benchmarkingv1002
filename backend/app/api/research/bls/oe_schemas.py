"""
Pydantic schemas for OE (Occupational Employment and Wage Statistics) Explorer

OEWS provides employment and wage estimates for ~800 occupations by:
- Geographic area (National, State, Metropolitan/Nonmetropolitan)
- Industry (450+ NAICS-based industries at national level)
- Occupation (SOC-based classification)

Data Types Available:
- 01: Employment
- 02: Employment percent relative standard error
- 03: Hourly mean wage
- 04: Annual mean wage
- 05: Wage percent relative standard error
- 06-10: Hourly percentile wages (10th, 25th, 50th, 75th, 90th)
- 11-15: Annual percentile wages (10th, 25th, 50th, 75th, 90th)
- 16: Employment per 1,000 jobs
- 17: Location Quotient

Series ID Format: OEUM000040000000000000001
  - OE = survey abbreviation
  - U = seasonal code (always U for unadjusted)
  - M = areatype_code (N=National, S=State, M=Metro/Nonmetro)
  - 0000400 = area_code (7 digits)
  - 000000 = industry_code (6 digits)
  - 000000 = occupation_code (6 digits)
  - 01 = datatype_code (2 digits)

Data available annually, updated in March.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class OEAreaTypeItem(BaseModel):
    """OE Area type dimension item"""
    areatype_code: str  # 'N', 'S', 'M'
    areatype_name: str

    class Config:
        from_attributes = True


class OEAreaItem(BaseModel):
    """OE Area dimension item (geographic areas)"""
    state_code: str
    area_code: str
    areatype_code: str
    area_name: str

    class Config:
        from_attributes = True


class OEIndustryItem(BaseModel):
    """OE Industry dimension item"""
    industry_code: str
    industry_name: str
    display_level: Optional[int] = None
    selectable: Optional[bool] = None

    class Config:
        from_attributes = True


class OESectorItem(BaseModel):
    """OE Sector dimension item"""
    sector_code: str
    sector_name: str

    class Config:
        from_attributes = True


class OEOccupationItem(BaseModel):
    """OE Occupation dimension item (SOC codes)"""
    occupation_code: str
    occupation_name: str
    occupation_description: Optional[str] = None
    display_level: Optional[int] = None
    selectable: Optional[bool] = None

    class Config:
        from_attributes = True


class OEDataTypeItem(BaseModel):
    """OE Data type dimension item"""
    datatype_code: str
    datatype_name: str

    class Config:
        from_attributes = True


class OEDimensions(BaseModel):
    """Available dimensions for OE survey"""
    area_types: List[OEAreaTypeItem]
    states: List[OEAreaItem]  # State-level areas
    occupations: List[OEOccupationItem]
    sectors: List[OESectorItem]
    data_types: List[OEDataTypeItem]


# ==================== Series Models ====================

class OESeriesInfo(BaseModel):
    """OE Series metadata with dimensions"""
    series_id: str
    seasonal: Optional[str] = None
    areatype_code: Optional[str] = None
    areatype_name: Optional[str] = None
    state_code: Optional[str] = None
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    sector_code: Optional[str] = None
    sector_name: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    datatype_code: Optional[str] = None
    datatype_name: Optional[str] = None
    series_title: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class OESeriesListResponse(BaseModel):
    """Response for OE series list with filters"""
    survey_code: str = "OE"
    total: int
    limit: int
    offset: int
    series: List[OESeriesInfo]


# ==================== Data Models ====================

class OEDataPoint(BaseModel):
    """A single OE time series observation"""
    year: int
    period: str
    period_name: str  # "2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class OESeriesData(BaseModel):
    """Time series data for a single OE series"""
    series_id: str
    occupation_name: Optional[str] = None
    area_name: Optional[str] = None
    industry_name: Optional[str] = None
    datatype_name: Optional[str] = None
    data_points: List[OEDataPoint]


class OEDataResponse(BaseModel):
    """Response for OE series data request"""
    survey_code: str = "OE"
    series: List[OESeriesData]


# ==================== Occupation Profile Models ====================

class OEOccupationWageProfile(BaseModel):
    """Complete wage profile for an occupation in an area"""
    occupation_code: str
    occupation_name: str
    occupation_description: Optional[str] = None
    area_code: str
    area_name: str
    industry_code: str
    industry_name: str
    latest_year: Optional[int] = None
    # Employment
    employment: Optional[float] = None
    employment_rse: Optional[float] = None
    employment_per_1000: Optional[float] = None
    location_quotient: Optional[float] = None
    # Hourly wages
    hourly_mean: Optional[float] = None
    hourly_10th: Optional[float] = None
    hourly_25th: Optional[float] = None
    hourly_median: Optional[float] = None
    hourly_75th: Optional[float] = None
    hourly_90th: Optional[float] = None
    # Annual wages
    annual_mean: Optional[float] = None
    annual_10th: Optional[float] = None
    annual_25th: Optional[float] = None
    annual_median: Optional[float] = None
    annual_75th: Optional[float] = None
    annual_90th: Optional[float] = None
    wage_rse: Optional[float] = None


class OEOccupationProfileResponse(BaseModel):
    """Full occupation profile response"""
    survey_code: str = "OE"
    occupation: OEOccupationWageProfile


# ==================== Overview/Dashboard Models ====================

class OEMajorGroupSummary(BaseModel):
    """Summary for a major occupation group"""
    occupation_code: str
    occupation_name: str
    employment: Optional[float] = None
    annual_mean: Optional[float] = None
    hourly_mean: Optional[float] = None
    employment_pct_of_total: Optional[float] = None
    yoy_employment_change: Optional[float] = None
    yoy_wage_change: Optional[float] = None


class OEOverviewResponse(BaseModel):
    """National overview by major occupation groups

    Shows employment and wage summary for top-level SOC groups
    (Management, Business, Computer, Healthcare, etc.)
    """
    survey_code: str = "OE"
    description: str = "Occupational Employment and Wage Statistics"
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    total_employment: Optional[float] = None
    mean_annual_wage: Optional[float] = None
    median_annual_wage: Optional[float] = None
    latest_year: Optional[int] = None
    major_groups: List[OEMajorGroupSummary]


class OEOverviewTimelinePoint(BaseModel):
    """Single point in overview timeline"""
    year: int
    major_groups: Dict[str, Optional[float]]  # occupation_code -> value


class OEOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "OE"
    datatype: str  # "employment" or "annual_mean"
    timeline: List[OEOverviewTimelinePoint]
    group_names: Dict[str, str]  # occupation_code -> name


# ==================== Occupation Analysis Models ====================

class OEOccupationMetric(BaseModel):
    """Metrics for a single occupation"""
    occupation_code: str
    occupation_name: str
    display_level: Optional[int] = None
    employment: Optional[float] = None
    employment_per_1000: Optional[float] = None
    location_quotient: Optional[float] = None
    hourly_mean: Optional[float] = None
    hourly_median: Optional[float] = None
    annual_mean: Optional[float] = None
    annual_median: Optional[float] = None
    yoy_employment_pct: Optional[float] = None
    yoy_wage_pct: Optional[float] = None
    latest_year: Optional[int] = None


class OEOccupationAnalysisResponse(BaseModel):
    """Occupation-level analysis"""
    survey_code: str = "OE"
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    occupations: List[OEOccupationMetric]
    total_count: int
    latest_year: Optional[int] = None


class OEOccupationTimelinePoint(BaseModel):
    """Single point in occupation timeline"""
    year: int
    occupations: Dict[str, Optional[float]]  # occupation_code -> value


class OEOccupationTimelineResponse(BaseModel):
    """Timeline data for occupation comparison charts"""
    survey_code: str = "OE"
    datatype: str  # "employment", "annual_mean", etc.
    timeline: List[OEOccupationTimelinePoint]
    occupation_names: Dict[str, str]  # occupation_code -> name


# ==================== Geographic Analysis Models ====================

class OEAreaMetric(BaseModel):
    """Metrics for a geographic area"""
    state_code: str
    area_code: str
    area_name: str
    areatype_code: str
    employment: Optional[float] = None
    employment_per_1000: Optional[float] = None
    location_quotient: Optional[float] = None
    hourly_mean: Optional[float] = None
    annual_mean: Optional[float] = None
    annual_median: Optional[float] = None
    latest_year: Optional[int] = None


class OEAreaAnalysisResponse(BaseModel):
    """Geographic analysis for an occupation"""
    survey_code: str = "OE"
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    areas: List[OEAreaMetric]
    total_count: int
    latest_year: Optional[int] = None


class OEAreaTimelinePoint(BaseModel):
    """Single point in area timeline"""
    year: int
    areas: Dict[str, Optional[float]]  # area_code -> value


class OEAreaTimelineResponse(BaseModel):
    """Timeline data for area comparison charts"""
    survey_code: str = "OE"
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    datatype: str
    timeline: List[OEAreaTimelinePoint]
    area_names: Dict[str, str]  # area_code -> name


# ==================== Industry Analysis Models ====================

class OEIndustryMetric(BaseModel):
    """Metrics for an industry"""
    industry_code: str
    industry_name: str
    sector_code: Optional[str] = None
    sector_name: Optional[str] = None
    display_level: Optional[int] = None
    employment: Optional[float] = None
    employment_per_1000: Optional[float] = None
    location_quotient: Optional[float] = None
    hourly_mean: Optional[float] = None
    annual_mean: Optional[float] = None
    annual_median: Optional[float] = None
    yoy_employment_pct: Optional[float] = None
    yoy_wage_pct: Optional[float] = None
    latest_year: Optional[int] = None


class OEIndustryAnalysisResponse(BaseModel):
    """Industry-level analysis for an occupation"""
    survey_code: str = "OE"
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    industries: List[OEIndustryMetric]
    total_count: int
    latest_year: Optional[int] = None


class OEIndustryTimelinePoint(BaseModel):
    """Single point in industry timeline"""
    year: int
    industries: Dict[str, Optional[float]]  # industry_code -> value


class OEIndustryTimelineResponse(BaseModel):
    """Timeline data for industry comparison charts"""
    survey_code: str = "OE"
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    datatype: str
    timeline: List[OEIndustryTimelinePoint]
    industry_names: Dict[str, str]  # industry_code -> name


# ==================== Wage Distribution Models ====================

class OEWageDistribution(BaseModel):
    """Wage distribution for an occupation/area combination"""
    occupation_code: str
    occupation_name: str
    area_code: str
    area_name: str
    latest_year: Optional[int] = None
    # Hourly distribution
    hourly_10th: Optional[float] = None
    hourly_25th: Optional[float] = None
    hourly_median: Optional[float] = None
    hourly_75th: Optional[float] = None
    hourly_90th: Optional[float] = None
    hourly_mean: Optional[float] = None
    # Annual distribution
    annual_10th: Optional[float] = None
    annual_25th: Optional[float] = None
    annual_median: Optional[float] = None
    annual_75th: Optional[float] = None
    annual_90th: Optional[float] = None
    annual_mean: Optional[float] = None


class OEWageDistributionResponse(BaseModel):
    """Response for wage distribution request"""
    survey_code: str = "OE"
    distributions: List[OEWageDistribution]


# ==================== Top Rankings Models ====================

class OETopOccupation(BaseModel):
    """An occupation in a top-ranked list"""
    occupation_code: str
    occupation_name: str
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    value: Optional[float] = None
    rank: int


class OETopRankingsResponse(BaseModel):
    """Top occupations by various metrics"""
    survey_code: str = "OE"
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    ranking_type: str  # "highest_paying", "most_employed", "fastest_growing", etc.
    occupations: List[OETopOccupation]
    latest_year: Optional[int] = None


# ==================== State Comparison Models ====================

class OEStateMetric(BaseModel):
    """Metrics for a state"""
    state_code: str
    state_name: str
    employment: Optional[float] = None
    employment_per_1000: Optional[float] = None
    location_quotient: Optional[float] = None
    hourly_mean: Optional[float] = None
    annual_mean: Optional[float] = None
    latest_year: Optional[int] = None


class OEStateComparisonResponse(BaseModel):
    """State-level comparison for an occupation"""
    survey_code: str = "OE"
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    states: List[OEStateMetric]
    latest_year: Optional[int] = None


class OEStateTimelinePoint(BaseModel):
    """Single point in state timeline"""
    year: int
    states: Dict[str, Optional[float]]  # state_code -> value


class OEStateTimelineResponse(BaseModel):
    """Timeline data for state comparison charts"""
    survey_code: str = "OE"
    occupation_code: Optional[str] = None
    occupation_name: Optional[str] = None
    datatype: str
    timeline: List[OEStateTimelinePoint]
    state_names: Dict[str, str]  # state_code -> name


# ==================== Top Movers Models ====================

class OETopMover(BaseModel):
    """An occupation with significant change"""
    occupation_code: str
    occupation_name: str
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    value: Optional[float] = None
    prev_value: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    latest_year: Optional[int] = None


class OETopMoversResponse(BaseModel):
    """Top movers (gainers and losers) in employment or wages"""
    survey_code: str = "OE"
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    metric: str  # "employment" or "annual_mean"
    gainers: List[OETopMover]
    losers: List[OETopMover]
    latest_year: Optional[int] = None
