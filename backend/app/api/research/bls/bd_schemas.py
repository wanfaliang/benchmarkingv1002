"""
Pydantic schemas for BD (Business Employment Dynamics) Explorer

Business Employment Dynamics (BED) tracks changes in employment at the establishment level,
revealing the dynamics underlying net changes in employment.

Key Concepts:
- Job Flows: Gains (Openings + Expansions) vs Losses (Closings + Contractions)
- Establishment Births/Deaths: New/ceased business establishments
- Data available as Levels (thousands) or Rates (percentage)

Data Classes (dataclass_code):
- 01: Gross Job Gains (sum of 02+03)
- 02: Expansions (existing establishments hiring)
- 03: Openings (new establishments or reopenings)
- 04: Gross Job Losses (sum of 05+06)
- 05: Contractions (existing establishments reducing staff)
- 06: Closings (establishments closing or going out of business)
- 07: Establishment Births (new establishments)
- 08: Establishment Deaths (ceased establishments)

Data Elements (dataelement_code):
- 1: Employment
- 2: Number of Establishments

Size Classes (sizeclass_code):
- 00: All size classes (industry/state data)
- 01-09: Firm size classes (1-4 emp, 5-9 emp, ... 1000+ emp)
- 10-28+: Employment change size (1 job, 2 jobs, ... 100+ jobs)

Series ID Format: BDS0000006000200090110004LQ5
  - BD = survey abbreviation
  - S = seasonal (S=adjusted, U=unadjusted)
  - 00000 = msa_code (national = 00000)
  - 06 = state_code (FIPS, 00=US total)
  - 000 = county_code
  - 200090 = industry_code
  - 1 = unitanalysis_code (1=Establishment)
  - 1 = dataelement_code (1=Employment, 2=Establishments)
  - 00 = sizeclass_code
  - 04 = dataclass_code
  - L = ratelevel_code (L=Level, R=Rate)
  - Q = periodicity_code (Q=Quarterly, A=Annual)
  - 5 = ownership_code (5=Private)

Data Range: 1992-present, updated quarterly (6 months lag)
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# ==================== Dimension Models ====================

class BDStateItem(BaseModel):
    """BD State dimension item"""
    state_code: str  # '00', '01', '06', etc.
    state_name: str

    class Config:
        from_attributes = True


class BDIndustryItem(BaseModel):
    """BD Industry dimension item"""
    industry_code: str  # '000000', '100000', '200090', etc.
    industry_name: str
    display_level: Optional[int] = None
    selectable: Optional[str] = None
    sort_sequence: Optional[int] = None

    class Config:
        from_attributes = True


class BDDataClassItem(BaseModel):
    """BD Data class dimension item (Job Gains, Losses, Births, Deaths)"""
    dataclass_code: str  # '01'-'08'
    dataclass_name: str
    display_level: Optional[int] = None
    selectable: Optional[str] = None
    sort_sequence: Optional[int] = None

    class Config:
        from_attributes = True


class BDDataElementItem(BaseModel):
    """BD Data element dimension item"""
    dataelement_code: str  # '1', '2'
    dataelement_name: str  # 'Employment', 'Number of Establishments'

    class Config:
        from_attributes = True


class BDSizeClassItem(BaseModel):
    """BD Size class dimension item"""
    sizeclass_code: str  # '00', '01'-'09', '10'-'28', '31'-'33'
    sizeclass_name: str

    class Config:
        from_attributes = True


class BDRateLevelItem(BaseModel):
    """BD Rate/Level dimension item"""
    ratelevel_code: str  # 'L', 'R'
    ratelevel_name: str  # 'Level', 'Rate'

    class Config:
        from_attributes = True


class BDOwnershipItem(BaseModel):
    """BD Ownership dimension item"""
    ownership_code: str  # '5' = Private Sector
    ownership_name: str

    class Config:
        from_attributes = True


class BDDimensions(BaseModel):
    """Available dimensions for BD survey"""
    states: List[BDStateItem]
    industries: List[BDIndustryItem]
    dataclasses: List[BDDataClassItem]
    dataelements: List[BDDataElementItem]
    sizeclasses: List[BDSizeClassItem]
    ratelevels: List[BDRateLevelItem]
    # Derived for convenience
    firm_sizeclasses: List[BDSizeClassItem]  # 00-09
    empchange_sizeclasses: List[BDSizeClassItem]  # 10+


# ==================== Series Models ====================

class BDSeriesInfo(BaseModel):
    """BD Series metadata with dimensions"""
    series_id: str
    seasonal_code: Optional[str] = None
    msa_code: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    county_code: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    unitanalysis_code: Optional[str] = None
    dataelement_code: Optional[str] = None
    dataelement_name: Optional[str] = None
    sizeclass_code: Optional[str] = None
    sizeclass_name: Optional[str] = None
    dataclass_code: Optional[str] = None
    dataclass_name: Optional[str] = None
    ratelevel_code: Optional[str] = None
    ratelevel_name: Optional[str] = None
    periodicity_code: Optional[str] = None
    ownership_code: Optional[str] = None
    series_title: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class BDSeriesListResponse(BaseModel):
    """Response for BD series list with filters"""
    survey_code: str = "BD"
    total: int
    limit: int
    offset: int
    series: List[BDSeriesInfo]


# ==================== Data Models ====================

class BDDataPoint(BaseModel):
    """A single BD time series observation"""
    year: int
    period: str  # 'Q01'-'Q04' or 'A01'
    period_name: str
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class BDSeriesData(BaseModel):
    """Time series data for a single BD series"""
    series_id: str
    series_info: BDSeriesInfo
    data_points: List[BDDataPoint]


class BDDataResponse(BaseModel):
    """Response for BD series data queries"""
    survey_code: str = "BD"
    series_count: int
    total_observations: int
    series: List[BDSeriesData]


# ==================== Overview Models ====================

class BDOverviewMetric(BaseModel):
    """A single overview metric (e.g., Gross Job Gains)"""
    dataclass_code: str
    dataclass_name: str
    level_value: Optional[float] = None
    rate_value: Optional[float] = None
    level_change: Optional[float] = None  # vs previous quarter
    rate_change: Optional[float] = None
    level_yoy_change: Optional[float] = None  # vs same quarter last year
    rate_yoy_change: Optional[float] = None


class BDOverviewResponse(BaseModel):
    """Overview of BD data for a specific period"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    metrics: List[BDOverviewMetric]
    available_years: List[int]
    available_periods: List[str]


class BDOverviewTimelinePoint(BaseModel):
    """Timeline data point for overview chart"""
    year: int
    period: str
    period_name: str
    gross_gains_level: Optional[float] = None
    gross_losses_level: Optional[float] = None
    net_change: Optional[float] = None
    gross_gains_rate: Optional[float] = None
    gross_losses_rate: Optional[float] = None


class BDOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "BD"
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    data: List[BDOverviewTimelinePoint]


# ==================== State Comparison Models ====================

class BDStateComparisonItem(BaseModel):
    """Single state in state comparison"""
    state_code: str
    state_name: str
    gross_gains_level: Optional[float] = None
    gross_losses_level: Optional[float] = None
    net_change: Optional[float] = None
    gross_gains_rate: Optional[float] = None
    gross_losses_rate: Optional[float] = None
    expansions_level: Optional[float] = None
    contractions_level: Optional[float] = None
    openings_level: Optional[float] = None
    closings_level: Optional[float] = None
    births_level: Optional[float] = None
    deaths_level: Optional[float] = None


class BDStateComparisonResponse(BaseModel):
    """State comparison data"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    dataelement_code: str
    dataelement_name: str
    states: List[BDStateComparisonItem]


class BDStateTimelinePoint(BaseModel):
    """Timeline point for state comparison"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]  # state_code -> value


class BDStateTimelineResponse(BaseModel):
    """State comparison timeline"""
    survey_code: str = "BD"
    dataclass_code: str
    dataclass_name: str
    ratelevel_code: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    states: List[BDStateItem]
    data: List[BDStateTimelinePoint]


# ==================== Industry Comparison Models ====================

class BDIndustryComparisonItem(BaseModel):
    """Single industry in industry comparison"""
    industry_code: str
    industry_name: str
    display_level: Optional[int] = None
    gross_gains_level: Optional[float] = None
    gross_losses_level: Optional[float] = None
    net_change: Optional[float] = None
    gross_gains_rate: Optional[float] = None
    gross_losses_rate: Optional[float] = None


class BDIndustryComparisonResponse(BaseModel):
    """Industry comparison data"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    state_code: str
    state_name: str
    seasonal_code: str
    dataelement_code: str
    dataelement_name: str
    industries: List[BDIndustryComparisonItem]


class BDIndustryTimelinePoint(BaseModel):
    """Timeline point for industry comparison"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]  # industry_code -> value


class BDIndustryTimelineResponse(BaseModel):
    """Industry comparison timeline"""
    survey_code: str = "BD"
    dataclass_code: str
    dataclass_name: str
    ratelevel_code: str
    state_code: str
    state_name: str
    seasonal_code: str
    industries: List[BDIndustryItem]
    data: List[BDIndustryTimelinePoint]


# ==================== Job Flow Components Models ====================

class BDJobFlowComponents(BaseModel):
    """Job flow component breakdown"""
    # Gains
    gross_gains: Optional[float] = None
    expansions: Optional[float] = None
    openings: Optional[float] = None
    # Losses
    gross_losses: Optional[float] = None
    contractions: Optional[float] = None
    closings: Optional[float] = None
    # Net
    net_change: Optional[float] = None
    # Births/Deaths (subset of openings/closings)
    births: Optional[float] = None
    deaths: Optional[float] = None


class BDJobFlowResponse(BaseModel):
    """Job flow component analysis"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    ratelevel_code: str
    ratelevel_name: str
    dataelement_code: str
    dataelement_name: str
    components: BDJobFlowComponents


class BDJobFlowTimelinePoint(BaseModel):
    """Timeline point for job flow analysis"""
    year: int
    period: str
    period_name: str
    gross_gains: Optional[float] = None
    expansions: Optional[float] = None
    openings: Optional[float] = None
    gross_losses: Optional[float] = None
    contractions: Optional[float] = None
    closings: Optional[float] = None
    net_change: Optional[float] = None


class BDJobFlowTimelineResponse(BaseModel):
    """Job flow timeline data"""
    survey_code: str = "BD"
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    ratelevel_code: str
    dataelement_code: str
    data: List[BDJobFlowTimelinePoint]


# ==================== Size Class Analysis Models ====================

class BDSizeClassDataItem(BaseModel):
    """Size class data item"""
    sizeclass_code: str
    sizeclass_name: str
    gross_gains: Optional[float] = None
    gross_losses: Optional[float] = None
    net_change: Optional[float] = None


class BDSizeClassResponse(BaseModel):
    """Size class analysis response"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    seasonal_code: str
    ratelevel_code: str
    ratelevel_name: str
    dataelement_code: str
    dataelement_name: str
    sizeclass_type: str  # 'firm' or 'empchange'
    data: List[BDSizeClassDataItem]


class BDSizeClassTimelinePoint(BaseModel):
    """Size class timeline point"""
    year: int
    period: str
    period_name: str
    values: Dict[str, Optional[float]]  # sizeclass_code -> value


class BDSizeClassTimelineResponse(BaseModel):
    """Size class timeline response"""
    survey_code: str = "BD"
    dataclass_code: str
    dataclass_name: str
    ratelevel_code: str
    sizeclass_type: str
    seasonal_code: str
    sizeclasses: List[BDSizeClassItem]
    data: List[BDSizeClassTimelinePoint]


# ==================== Establishment Births/Deaths Models ====================

class BDBirthsDeathsData(BaseModel):
    """Establishment births and deaths data"""
    births: Optional[float] = None
    deaths: Optional[float] = None
    net: Optional[float] = None
    birth_rate: Optional[float] = None
    death_rate: Optional[float] = None


class BDBirthsDeathsResponse(BaseModel):
    """Establishment births/deaths analysis"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    employment: BDBirthsDeathsData
    establishments: BDBirthsDeathsData


class BDBirthsDeathsTimelinePoint(BaseModel):
    """Births/deaths timeline point"""
    year: int
    period: str
    period_name: str
    births_emp: Optional[float] = None
    deaths_emp: Optional[float] = None
    births_est: Optional[float] = None
    deaths_est: Optional[float] = None
    net_emp: Optional[float] = None
    net_est: Optional[float] = None


class BDBirthsDeathsTimelineResponse(BaseModel):
    """Births/deaths timeline"""
    survey_code: str = "BD"
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    seasonal_code: str
    ratelevel_code: str
    data: List[BDBirthsDeathsTimelinePoint]


# ==================== Top Movers Models ====================

class BDTopMoverItem(BaseModel):
    """Top mover item (state or industry)"""
    code: str
    name: str
    value: Optional[float] = None
    change: Optional[float] = None
    pct_change: Optional[float] = None


class BDTopMoversResponse(BaseModel):
    """Top movers response"""
    survey_code: str = "BD"
    year: int
    period: str
    period_name: str
    metric: str  # 'gross_gains', 'gross_losses', 'net_change', etc.
    ratelevel_code: str
    dataelement_code: str
    comparison_type: str  # 'state' or 'industry'
    top_gainers: List[BDTopMoverItem]
    top_losers: List[BDTopMoverItem]


# ==================== Historical Trends Models ====================

class BDTrendPoint(BaseModel):
    """A single trend data point"""
    year: int
    period: str
    period_name: str
    value: Optional[float] = None
    yoy_change: Optional[float] = None
    yoy_pct_change: Optional[float] = None


class BDTrendResponse(BaseModel):
    """Historical trend data"""
    survey_code: str = "BD"
    state_code: str
    state_name: str
    industry_code: str
    industry_name: str
    dataclass_code: str
    dataclass_name: str
    ratelevel_code: str
    ratelevel_name: str
    dataelement_code: str
    dataelement_name: str
    seasonal_code: str
    data: List[BDTrendPoint]
