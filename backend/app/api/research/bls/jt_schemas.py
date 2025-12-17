"""
Pydantic schemas for JT (Job Openings and Labor Turnover Survey - JOLTS) Explorer

JOLTS provides national estimates of rates and levels for:
- Job openings (JO)
- Hires (HI)
- Total separations (TS)
- Quits (QU)
- Layoffs and discharges (LD)
- Other separations (OS)
- Unemployed persons per job opening ratio (UO)

Series ID Format: JTS000000000000000JOR
  - JT = survey abbreviation
  - S = seasonal code (S=Seasonally Adjusted, U=Unadjusted)
  - 000000 = industry_code (6 digits)
  - 00 = state_code (2 digits, includes regions NE/MW/SO/WE)
  - 00000 = area_code (5 digits, currently only '00000' = All areas)
  - 00 = sizeclass_code (2 digits)
  - JO = dataelement_code (2 chars)
  - R = ratelevel_code (R=Rate, L=Level in thousands)

Data available from December 2000 to present, monthly.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class JTIndustryItem(BaseModel):
    """JT Industry dimension item"""
    industry_code: str
    industry_name: str
    display_level: Optional[int] = None
    selectable: Optional[bool] = None

    class Config:
        from_attributes = True


class JTStateItem(BaseModel):
    """JT State/Region dimension item"""
    state_code: str
    state_name: str
    display_level: Optional[int] = None
    selectable: Optional[bool] = None

    class Config:
        from_attributes = True


class JTDataElementItem(BaseModel):
    """JT Data element dimension item"""
    dataelement_code: str
    dataelement_name: str
    display_level: Optional[int] = None

    class Config:
        from_attributes = True


class JTSizeClassItem(BaseModel):
    """JT Size class dimension item"""
    sizeclass_code: str
    sizeclass_name: str

    class Config:
        from_attributes = True


class JTRateLevelItem(BaseModel):
    """JT Rate/Level dimension item"""
    ratelevel_code: str
    ratelevel_name: str

    class Config:
        from_attributes = True


class JTDimensions(BaseModel):
    """Available dimensions for JT survey"""
    industries: List[JTIndustryItem]
    states: List[JTStateItem]
    data_elements: List[JTDataElementItem]
    size_classes: List[JTSizeClassItem]
    rate_levels: List[JTRateLevelItem]


# ==================== Series Models ====================

class JTSeriesInfo(BaseModel):
    """JT Series metadata with dimensions"""
    series_id: str
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    area_code: Optional[str] = None
    sizeclass_code: Optional[str] = None
    sizeclass_name: Optional[str] = None
    dataelement_code: Optional[str] = None
    dataelement_name: Optional[str] = None
    ratelevel_code: Optional[str] = None
    ratelevel_name: Optional[str] = None
    seasonal_code: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class JTSeriesListResponse(BaseModel):
    """Response for JT series list with filters"""
    survey_code: str = "JT"
    total: int
    limit: int
    offset: int
    series: List[JTSeriesInfo]


# ==================== Data Models ====================

class JTDataPoint(BaseModel):
    """A single JT time series observation"""
    year: int
    period: str
    period_name: str  # "January 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class JTSeriesData(BaseModel):
    """Time series data for a single JT series"""
    series_id: str
    industry_name: Optional[str] = None
    state_name: Optional[str] = None
    dataelement_name: Optional[str] = None
    ratelevel_name: Optional[str] = None
    data_points: List[JTDataPoint]


class JTDataResponse(BaseModel):
    """Response for JT series data request"""
    survey_code: str = "JT"
    series: List[JTSeriesData]


# ==================== Overview/Dashboard Models ====================

class JTMetric(BaseModel):
    """A single JOLTS metric (rate or level)"""
    series_id: str
    dataelement_code: str
    dataelement_name: str
    ratelevel_code: str
    value: Optional[float] = None
    latest_date: Optional[str] = None
    month_over_month: Optional[float] = None
    month_over_month_pct: Optional[float] = None
    year_over_year: Optional[float] = None
    year_over_year_pct: Optional[float] = None


class JTOverviewResponse(BaseModel):
    """Overview dashboard showing all JOLTS metrics for Total Nonfarm

    Shows job openings, hires, quits, layoffs, total separations
    for the selected industry (default: Total Nonfarm)
    """
    survey_code: str = "JT"
    description: str = "Job Openings and Labor Turnover Survey"
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    # Rate metrics (%)
    job_openings_rate: Optional[JTMetric] = None
    hires_rate: Optional[JTMetric] = None
    total_separations_rate: Optional[JTMetric] = None
    quits_rate: Optional[JTMetric] = None
    layoffs_rate: Optional[JTMetric] = None
    # Level metrics (thousands)
    job_openings_level: Optional[JTMetric] = None
    hires_level: Optional[JTMetric] = None
    total_separations_level: Optional[JTMetric] = None
    quits_level: Optional[JTMetric] = None
    layoffs_level: Optional[JTMetric] = None
    # Ratio
    unemployed_per_opening: Optional[JTMetric] = None
    last_updated: Optional[str] = None


class JTOverviewTimelinePoint(BaseModel):
    """Single point in overview timeline"""
    year: int
    period: str
    period_name: str
    job_openings_rate: Optional[float] = None
    hires_rate: Optional[float] = None
    total_separations_rate: Optional[float] = None
    quits_rate: Optional[float] = None
    layoffs_rate: Optional[float] = None
    job_openings_level: Optional[float] = None
    hires_level: Optional[float] = None
    total_separations_level: Optional[float] = None
    quits_level: Optional[float] = None
    layoffs_level: Optional[float] = None


class JTOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "JT"
    industry_name: Optional[str] = None
    state_name: Optional[str] = None
    timeline: List[JTOverviewTimelinePoint]


# ==================== Industry Analysis Models ====================

class JTIndustryMetric(BaseModel):
    """JOLTS metrics for a single industry"""
    industry_code: str
    industry_name: str
    display_level: Optional[int] = None
    # Latest rates
    job_openings_rate: Optional[float] = None
    hires_rate: Optional[float] = None
    quits_rate: Optional[float] = None
    layoffs_rate: Optional[float] = None
    total_separations_rate: Optional[float] = None
    # Latest levels (thousands)
    job_openings_level: Optional[float] = None
    hires_level: Optional[float] = None
    quits_level: Optional[float] = None
    layoffs_level: Optional[float] = None
    total_separations_level: Optional[float] = None
    # Changes
    job_openings_yoy_pct: Optional[float] = None
    hires_yoy_pct: Optional[float] = None
    quits_yoy_pct: Optional[float] = None
    latest_date: Optional[str] = None


class JTIndustryAnalysisResponse(BaseModel):
    """Industry-level JOLTS analysis"""
    survey_code: str = "JT"
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    industries: List[JTIndustryMetric]
    last_updated: Optional[str] = None


class JTIndustryTimelinePoint(BaseModel):
    """Single point in industry timeline"""
    year: int
    period: str
    period_name: str
    industries: Dict[str, Optional[float]]  # industry_code -> value


class JTIndustryTimelineResponse(BaseModel):
    """Timeline data for industry comparison charts"""
    survey_code: str = "JT"
    dataelement_code: str
    dataelement_name: str
    ratelevel_code: str
    timeline: List[JTIndustryTimelinePoint]
    industry_names: Dict[str, str]  # industry_code -> name


# ==================== Regional Analysis Models ====================

class JTRegionMetric(BaseModel):
    """JOLTS metrics for a state/region"""
    state_code: str
    state_name: str
    is_region: bool = False  # True for NE, MW, SO, WE
    job_openings_rate: Optional[float] = None
    hires_rate: Optional[float] = None
    quits_rate: Optional[float] = None
    layoffs_rate: Optional[float] = None
    total_separations_rate: Optional[float] = None
    job_openings_level: Optional[float] = None
    job_openings_yoy_pct: Optional[float] = None
    latest_date: Optional[str] = None


class JTRegionAnalysisResponse(BaseModel):
    """Regional JOLTS analysis"""
    survey_code: str = "JT"
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    regions: List[JTRegionMetric]
    last_updated: Optional[str] = None


class JTRegionTimelinePoint(BaseModel):
    """Single point in region timeline"""
    year: int
    period: str
    period_name: str
    regions: Dict[str, Optional[float]]  # state_code -> value


class JTRegionTimelineResponse(BaseModel):
    """Timeline data for region comparison charts"""
    survey_code: str = "JT"
    dataelement_code: str
    dataelement_name: str
    ratelevel_code: str
    timeline: List[JTRegionTimelinePoint]
    region_names: Dict[str, str]  # state_code -> name


# ==================== Size Class Analysis Models ====================

class JTSizeClassMetric(BaseModel):
    """JOLTS metrics by establishment size"""
    sizeclass_code: str
    sizeclass_name: str
    job_openings_rate: Optional[float] = None
    hires_rate: Optional[float] = None
    quits_rate: Optional[float] = None
    layoffs_rate: Optional[float] = None
    total_separations_rate: Optional[float] = None
    job_openings_level: Optional[float] = None
    latest_date: Optional[str] = None


class JTSizeClassAnalysisResponse(BaseModel):
    """Size class JOLTS analysis"""
    survey_code: str = "JT"
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    size_classes: List[JTSizeClassMetric]
    last_updated: Optional[str] = None


class JTSizeClassTimelinePoint(BaseModel):
    """Single point in size class timeline"""
    year: int
    period: str
    period_name: str
    size_classes: Dict[str, Optional[float]]  # sizeclass_code -> value


class JTSizeClassTimelineResponse(BaseModel):
    """Timeline data for size class comparison charts"""
    survey_code: str = "JT"
    dataelement_code: str
    dataelement_name: str
    ratelevel_code: str
    timeline: List[JTSizeClassTimelinePoint]
    sizeclass_names: Dict[str, str]  # sizeclass_code -> name


# ==================== Top Movers Models ====================

class JTTopMover(BaseModel):
    """An industry with significant JOLTS change"""
    series_id: str
    industry_code: str
    industry_name: str
    dataelement_code: str
    dataelement_name: str
    value: Optional[float] = None
    latest_date: Optional[str] = None
    change: Optional[float] = None  # Absolute change
    change_pct: Optional[float] = None  # Percent change


class JTTopMoversResponse(BaseModel):
    """Top movers (gainers and losers) in job openings, hires, etc."""
    survey_code: str = "JT"
    dataelement_code: str
    dataelement_name: str
    period: str  # "mom" or "yoy"
    gainers: List[JTTopMover]
    losers: List[JTTopMover]
    last_updated: Optional[str] = None
