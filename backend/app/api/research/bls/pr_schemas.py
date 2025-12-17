"""
Pydantic schemas for PR (Major Sector Productivity and Costs) Explorer

PR Survey provides productivity and cost measures for major economic sectors:
- Business Sector
- Nonfarm Business Sector
- Nonfinancial Corporations
- Manufacturing (Total, Durable Goods, Nondurable Goods)

Dimensions:
- Sector: 6 major sectors (Business, Nonfarm Business, Nonfinancial Corp, Manufacturing variants)
- Class: 2 worker types (All persons, Employees)
- Measure: 23 metrics (Labor productivity, Unit labor costs, Compensation, Output, Hours, etc.)
- Duration: 3 types (Percent change YoY, Percent change prev quarter, Index 2017=100)

Series ID Format: PRS30006011
  - PR = survey abbreviation
  - S = seasonal adjustment (S=seasonally adjusted)
  - 3000 = sector_code (4 digits)
  - 6 = class_code (1 digit)
  - 01 = measure_code (2 digits)
  - 1 = duration_code (1 digit)

Data available quarterly and annually from 1947-present.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class PRSectorItem(BaseModel):
    """PR Sector dimension item"""
    sector_code: str
    sector_name: str

    class Config:
        from_attributes = True


class PRClassItem(BaseModel):
    """PR Worker class dimension item"""
    class_code: str
    class_text: str

    class Config:
        from_attributes = True


class PRMeasureItem(BaseModel):
    """PR Measure dimension item"""
    measure_code: str
    measure_text: str

    class Config:
        from_attributes = True


class PRDurationItem(BaseModel):
    """PR Duration dimension item"""
    duration_code: str
    duration_text: str

    class Config:
        from_attributes = True


class PRDimensions(BaseModel):
    """Available dimensions for PR survey"""
    sectors: List[PRSectorItem]
    classes: List[PRClassItem]
    measures: List[PRMeasureItem]
    durations: List[PRDurationItem]


# ==================== Series Models ====================

class PRSeriesInfo(BaseModel):
    """PR Series metadata with dimensions"""
    series_id: str
    seasonal: Optional[str] = None
    sector_code: Optional[str] = None
    sector_name: Optional[str] = None
    class_code: Optional[str] = None
    class_text: Optional[str] = None
    measure_code: Optional[str] = None
    measure_text: Optional[str] = None
    duration_code: Optional[str] = None
    duration_text: Optional[str] = None
    base_year: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class PRSeriesListResponse(BaseModel):
    """Response for PR series list with filters"""
    survey_code: str = "PR"
    total: int
    limit: int
    offset: int
    series: List[PRSeriesInfo]


# ==================== Data Models ====================

class PRDataPoint(BaseModel):
    """A single PR time series observation"""
    year: int
    period: str
    period_name: str  # "Q1 2024", "Annual 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class PRSeriesData(BaseModel):
    """Time series data for a single PR series"""
    series_id: str
    sector_name: Optional[str] = None
    class_text: Optional[str] = None
    measure_text: Optional[str] = None
    duration_text: Optional[str] = None
    data_points: List[PRDataPoint]


class PRDataResponse(BaseModel):
    """Response for PR series data request"""
    survey_code: str = "PR"
    series: List[PRSeriesData]


# ==================== Overview Models ====================

class PRSectorMetrics(BaseModel):
    """Key productivity metrics for a sector"""
    sector_code: str
    sector_name: str
    labor_productivity_index: Optional[float] = None
    labor_productivity_change: Optional[float] = None
    unit_labor_costs_index: Optional[float] = None
    unit_labor_costs_change: Optional[float] = None
    output_index: Optional[float] = None
    output_change: Optional[float] = None
    hours_index: Optional[float] = None
    hours_change: Optional[float] = None
    compensation_index: Optional[float] = None
    compensation_change: Optional[float] = None
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PROverviewResponse(BaseModel):
    """Overview of all sectors with key metrics"""
    survey_code: str = "PR"
    description: str = "Major Sector Productivity and Costs"
    sectors: List[PRSectorMetrics]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PROverviewTimelinePoint(BaseModel):
    """Single point in overview timeline"""
    year: int
    period: str
    period_name: str
    sectors: Dict[str, Optional[float]]  # sector_code -> value


class PROverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "PR"
    measure: str  # "labor_productivity", "unit_labor_costs", etc.
    duration: str  # "index" or "pct_change"
    timeline: List[PROverviewTimelinePoint]
    sector_names: Dict[str, str]  # sector_code -> name


# ==================== Sector Analysis Models ====================

class PRMeasureMetric(BaseModel):
    """Single measure metric for a sector"""
    measure_code: str
    measure_text: str
    index_value: Optional[float] = None
    yoy_change: Optional[float] = None
    qoq_change: Optional[float] = None
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PRSectorAnalysisResponse(BaseModel):
    """Detailed analysis for a specific sector"""
    survey_code: str = "PR"
    sector_code: str
    sector_name: str
    class_code: Optional[str] = None
    class_text: Optional[str] = None
    measures: List[PRMeasureMetric]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PRMeasureTimelinePoint(BaseModel):
    """Single point in measure timeline"""
    year: int
    period: str
    period_name: str
    measures: Dict[str, Optional[float]]  # measure_code -> value


class PRMeasureTimelineResponse(BaseModel):
    """Timeline data for measure comparison"""
    survey_code: str = "PR"
    sector_code: str
    sector_name: str
    duration: str  # "index", "yoy", or "qoq"
    timeline: List[PRMeasureTimelinePoint]
    measure_names: Dict[str, str]  # measure_code -> name


# ==================== Measure Comparison Models ====================

class PRSectorMeasureValue(BaseModel):
    """A single measure value for a sector"""
    sector_code: str
    sector_name: str
    value: Optional[float] = None
    yoy_change: Optional[float] = None


class PRMeasureComparisonResponse(BaseModel):
    """Compare a measure across all sectors"""
    survey_code: str = "PR"
    measure_code: str
    measure_text: str
    duration_code: str
    duration_text: str
    sectors: List[PRSectorMeasureValue]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PRMeasureComparisonTimelinePoint(BaseModel):
    """Single point in measure comparison timeline"""
    year: int
    period: str
    period_name: str
    sectors: Dict[str, Optional[float]]  # sector_code -> value


class PRMeasureComparisonTimelineResponse(BaseModel):
    """Timeline data for comparing a measure across sectors"""
    survey_code: str = "PR"
    measure_code: str
    measure_text: str
    timeline: List[PRMeasureComparisonTimelinePoint]
    sector_names: Dict[str, str]


# ==================== Class Comparison Models ====================

class PRClassMeasureValue(BaseModel):
    """A measure value for a class (employees vs all workers)"""
    class_code: str
    class_text: str
    index_value: Optional[float] = None
    yoy_change: Optional[float] = None
    qoq_change: Optional[float] = None


class PRClassComparisonResponse(BaseModel):
    """Compare measures between worker classes for a sector"""
    survey_code: str = "PR"
    sector_code: str
    sector_name: str
    measure_code: str
    measure_text: str
    classes: List[PRClassMeasureValue]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PRClassTimelinePoint(BaseModel):
    """Single point in class comparison timeline"""
    year: int
    period: str
    period_name: str
    classes: Dict[str, Optional[float]]  # class_code -> value


class PRClassTimelineResponse(BaseModel):
    """Timeline data for comparing classes"""
    survey_code: str = "PR"
    sector_code: str
    sector_name: str
    measure_code: str
    measure_text: str
    timeline: List[PRClassTimelinePoint]
    class_names: Dict[str, str]


# ==================== Productivity vs Costs Analysis ====================

class PRProductivityVsCosts(BaseModel):
    """Productivity and cost metrics for a sector"""
    sector_code: str
    sector_name: str
    productivity_index: Optional[float] = None
    productivity_change: Optional[float] = None
    unit_labor_costs_index: Optional[float] = None
    unit_labor_costs_change: Optional[float] = None
    hourly_compensation_index: Optional[float] = None
    hourly_compensation_change: Optional[float] = None
    real_compensation_index: Optional[float] = None
    real_compensation_change: Optional[float] = None


class PRProductivityVsCostsResponse(BaseModel):
    """Productivity vs costs analysis"""
    survey_code: str = "PR"
    analysis: List[PRProductivityVsCosts]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PRProductivityVsCostsTimelinePoint(BaseModel):
    """Single point for productivity vs costs timeline"""
    year: int
    period: str
    period_name: str
    productivity: Optional[float] = None
    unit_labor_costs: Optional[float] = None
    hourly_compensation: Optional[float] = None


class PRProductivityVsCostsTimelineResponse(BaseModel):
    """Timeline data for productivity vs costs"""
    survey_code: str = "PR"
    sector_code: str
    sector_name: str
    duration: str  # "index" or "pct_change"
    timeline: List[PRProductivityVsCostsTimelinePoint]


# ==================== Manufacturing Comparison Models ====================

class PRManufacturingMetric(BaseModel):
    """Metrics for manufacturing subsectors"""
    sector_code: str
    sector_name: str
    productivity_index: Optional[float] = None
    productivity_change: Optional[float] = None
    unit_labor_costs_index: Optional[float] = None
    unit_labor_costs_change: Optional[float] = None
    output_index: Optional[float] = None
    output_change: Optional[float] = None


class PRManufacturingComparisonResponse(BaseModel):
    """Compare manufacturing subsectors (total, durable, nondurable)"""
    survey_code: str = "PR"
    manufacturing_sectors: List[PRManufacturingMetric]
    latest_year: Optional[int] = None
    latest_period: Optional[str] = None


class PRManufacturingTimelinePoint(BaseModel):
    """Single point in manufacturing timeline"""
    year: int
    period: str
    period_name: str
    sectors: Dict[str, Optional[float]]  # sector_code -> value


class PRManufacturingTimelineResponse(BaseModel):
    """Timeline data for manufacturing comparison"""
    survey_code: str = "PR"
    measure: str  # "productivity", "unit_labor_costs", "output"
    timeline: List[PRManufacturingTimelinePoint]
    sector_names: Dict[str, str]
