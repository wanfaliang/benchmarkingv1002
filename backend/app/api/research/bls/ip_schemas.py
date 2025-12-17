"""
Pydantic schemas for IP (Industry Productivity) Explorer

IP Survey provides annual measures of labor productivity, unit labor costs, and related series
for U.S. industries. The data covers:
- 21 sectors (Agriculture, Mining, Manufacturing, etc.)
- 800+ industries (NAICS classification at various levels)
- 38 measures (Labor productivity, Output, Hours worked, Employment, etc.)
- Index values (2017=100) and annual percent changes

Series ID Format: IPUBN211___L000000000
  - IP = survey abbreviation
  - U = seasonal code (always U for unadjusted, annual data)
  - B = sector_code (1 char)
  - N211___ = industry_code (7 chars)
  - L00 = measure_code (3 chars)
  - 0 = duration_code (1 char: 0=Index, 1=% change)
  - 000000 = area_code (always 000000 for U.S. total)

Data available annually from 1987-present, updated throughout the year.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class IPSectorItem(BaseModel):
    """IP Sector dimension item"""
    sector_code: str
    sector_text: str

    class Config:
        from_attributes = True


class IPIndustryItem(BaseModel):
    """IP Industry dimension item"""
    industry_code: str
    naics_code: Optional[str] = None
    industry_text: str
    display_level: Optional[int] = None
    selectable: Optional[bool] = None

    class Config:
        from_attributes = True


class IPMeasureItem(BaseModel):
    """IP Measure dimension item"""
    measure_code: str
    measure_text: str
    display_level: Optional[int] = None
    selectable: Optional[bool] = None

    class Config:
        from_attributes = True


class IPDurationItem(BaseModel):
    """IP Duration dimension item (Index vs % change)"""
    duration_code: str
    duration_text: str

    class Config:
        from_attributes = True


class IPTypeItem(BaseModel):
    """IP Type dimension item (Index, Percent, Currency, etc.)"""
    type_code: str
    type_text: str

    class Config:
        from_attributes = True


class IPAreaItem(BaseModel):
    """IP Area dimension item (geographic areas)"""
    area_code: str
    area_text: str

    class Config:
        from_attributes = True


class IPDimensions(BaseModel):
    """Available dimensions for IP survey"""
    sectors: List[IPSectorItem]
    industries: List[IPIndustryItem]
    measures: List[IPMeasureItem]
    durations: List[IPDurationItem]
    types: List[IPTypeItem]
    areas: List[IPAreaItem]


# ==================== Series Models ====================

class IPSeriesInfo(BaseModel):
    """IP Series metadata with dimensions"""
    series_id: str
    seasonal: Optional[str] = None
    sector_code: Optional[str] = None
    sector_text: Optional[str] = None
    industry_code: Optional[str] = None
    industry_text: Optional[str] = None
    naics_code: Optional[str] = None
    measure_code: Optional[str] = None
    measure_text: Optional[str] = None
    duration_code: Optional[str] = None
    duration_text: Optional[str] = None
    type_code: Optional[str] = None
    type_text: Optional[str] = None
    area_code: Optional[str] = None
    area_text: Optional[str] = None
    base_year: Optional[str] = None
    series_title: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class IPSeriesListResponse(BaseModel):
    """Response for IP series list with filters"""
    survey_code: str = "IP"
    total: int
    limit: int
    offset: int
    series: List[IPSeriesInfo]


# ==================== Data Models ====================

class IPDataPoint(BaseModel):
    """A single IP time series observation"""
    year: int
    period: str
    period_name: str
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class IPSeriesData(BaseModel):
    """IP Series with its time series data"""
    series_id: str
    series_info: IPSeriesInfo
    data: List[IPDataPoint]


class IPDataResponse(BaseModel):
    """Response for IP data query"""
    survey_code: str = "IP"
    series: List[IPSeriesData]


# ==================== Overview Models ====================

class IPSectorSummary(BaseModel):
    """Summary metrics for a sector"""
    sector_code: str
    sector_text: str
    labor_productivity: Optional[float] = None
    labor_productivity_change: Optional[float] = None
    output: Optional[float] = None
    output_change: Optional[float] = None
    hours: Optional[float] = None
    hours_change: Optional[float] = None
    employment: Optional[float] = None
    employment_change: Optional[float] = None
    unit_labor_costs: Optional[float] = None
    ulc_change: Optional[float] = None
    industry_count: int = 0


class IPOverviewResponse(BaseModel):
    """Overview of IP data with key metrics by sector"""
    survey_code: str = "IP"
    year: int
    sectors: List[IPSectorSummary]


class IPOverviewTimelinePoint(BaseModel):
    """Timeline point for overview data"""
    year: int
    period: str
    period_name: str
    sectors: Dict[str, Optional[float]]  # sector_code -> value


class IPOverviewTimelineResponse(BaseModel):
    """Timeline data for overview"""
    survey_code: str = "IP"
    measure_code: str
    measure_text: str
    timeline: List[IPOverviewTimelinePoint]
    sector_names: Dict[str, str]


# ==================== Sector Analysis Models ====================

class IPIndustryMetric(BaseModel):
    """Metrics for an industry within a sector"""
    industry_code: str
    industry_text: str
    naics_code: Optional[str] = None
    display_level: Optional[int] = None
    labor_productivity: Optional[float] = None
    labor_productivity_change: Optional[float] = None
    output: Optional[float] = None
    output_change: Optional[float] = None
    hours: Optional[float] = None
    hours_change: Optional[float] = None
    employment: Optional[float] = None
    employment_change: Optional[float] = None


class IPSectorAnalysisResponse(BaseModel):
    """Detailed analysis for a specific sector"""
    survey_code: str = "IP"
    sector_code: str
    sector_text: str
    year: int
    industries: List[IPIndustryMetric]


class IPSectorTimelinePoint(BaseModel):
    """Timeline point for sector data"""
    year: int
    period: str
    period_name: str
    industries: Dict[str, Optional[float]]  # industry_code -> value


class IPSectorTimelineResponse(BaseModel):
    """Timeline data for sector analysis"""
    survey_code: str = "IP"
    sector_code: str
    sector_text: str
    measure_code: str
    measure_text: str
    timeline: List[IPSectorTimelinePoint]
    industry_names: Dict[str, str]


# ==================== Industry Comparison Models ====================

class IPMeasureValue(BaseModel):
    """Value for a specific measure"""
    measure_code: str
    measure_text: str
    value: Optional[float] = None
    change: Optional[float] = None


class IPIndustryAnalysisResponse(BaseModel):
    """Detailed analysis for a specific industry"""
    survey_code: str = "IP"
    industry_code: str
    industry_text: str
    naics_code: Optional[str] = None
    sector_code: str
    sector_text: str
    year: int
    measures: List[IPMeasureValue]


class IPIndustryTimelinePoint(BaseModel):
    """Timeline point for industry data"""
    year: int
    period: str
    period_name: str
    measures: Dict[str, Optional[float]]  # measure_code -> value


class IPIndustryTimelineResponse(BaseModel):
    """Timeline data for industry analysis"""
    survey_code: str = "IP"
    industry_code: str
    industry_text: str
    timeline: List[IPIndustryTimelinePoint]
    measure_names: Dict[str, str]


# ==================== Measure Comparison Models ====================

class IPIndustryMeasureMetric(BaseModel):
    """Measure value for an industry"""
    industry_code: str
    industry_text: str
    naics_code: Optional[str] = None
    value: Optional[float] = None
    change: Optional[float] = None


class IPMeasureComparisonResponse(BaseModel):
    """Compare a measure across industries"""
    survey_code: str = "IP"
    measure_code: str
    measure_text: str
    year: int
    industries: List[IPIndustryMeasureMetric]


class IPMeasureTimelinePoint(BaseModel):
    """Timeline point for measure comparison"""
    year: int
    period: str
    period_name: str
    industries: Dict[str, Optional[float]]  # industry_code -> value


class IPMeasureTimelineResponse(BaseModel):
    """Timeline data for measure comparison"""
    survey_code: str = "IP"
    measure_code: str
    measure_text: str
    timeline: List[IPMeasureTimelinePoint]
    industry_names: Dict[str, str]


# ==================== Top Rankings Models ====================

class IPTopIndustry(BaseModel):
    """Industry ranking entry"""
    rank: int
    industry_code: str
    industry_text: str
    naics_code: Optional[str] = None
    sector_code: str
    sector_text: str
    value: Optional[float] = None
    change: Optional[float] = None


class IPTopRankingsResponse(BaseModel):
    """Top/Bottom industries by measure"""
    survey_code: str = "IP"
    measure_code: str
    measure_text: str
    ranking_type: str  # 'highest', 'lowest', 'fastest_growing', 'fastest_declining'
    year: int
    industries: List[IPTopIndustry]


# ==================== Productivity vs Costs Models ====================

class IPProductivityVsCostsMetric(BaseModel):
    """Productivity vs Costs comparison for an industry"""
    industry_code: str
    industry_text: str
    naics_code: Optional[str] = None
    labor_productivity: Optional[float] = None
    productivity_change: Optional[float] = None
    unit_labor_costs: Optional[float] = None
    ulc_change: Optional[float] = None
    output: Optional[float] = None
    output_change: Optional[float] = None
    compensation: Optional[float] = None
    compensation_change: Optional[float] = None


class IPProductivityVsCostsResponse(BaseModel):
    """Productivity vs Unit Labor Costs comparison"""
    survey_code: str = "IP"
    sector_code: Optional[str] = None
    sector_text: Optional[str] = None
    year: int
    industries: List[IPProductivityVsCostsMetric]


class IPProductivityVsCostsTimelinePoint(BaseModel):
    """Timeline point for productivity vs costs"""
    year: int
    period: str
    period_name: str
    labor_productivity: Optional[float] = None
    unit_labor_costs: Optional[float] = None
    output: Optional[float] = None
    compensation: Optional[float] = None


class IPProductivityVsCostsTimelineResponse(BaseModel):
    """Timeline for productivity vs costs"""
    survey_code: str = "IP"
    industry_code: str
    industry_text: str
    timeline: List[IPProductivityVsCostsTimelinePoint]
