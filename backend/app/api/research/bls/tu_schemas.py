"""
Pydantic schemas for TU (American Time Use Survey) Explorer

ATUS provides time use data showing how people divide their time among activities:
- Average hours per day spent in various activities
- Participation rates (percent who engaged in activity)
- Number of persons

Key Dimensions:
- Activity: Major activities (sleeping, working, leisure, eating, etc.)
- Demographics: Sex, Age, Race, Education, Marital Status, Labor Force Status
- Context: Where (home, work), Who (alone, with family), Time of Day
- Geographic: Region

Stat Types:
- Average hours per day
- Percent participated
- Average hours per day for participants
- Number of persons

Data available annually from 2003-present, with some quarterly breakdowns.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel


# ==================== Dimension Models ====================

class TUStatTypeItem(BaseModel):
    """TU Statistic type dimension item"""
    stattype_code: str
    stattype_text: str
    display_level: Optional[int] = None
    selectable: Optional[str] = None

    class Config:
        from_attributes = True


class TUActivityItem(BaseModel):
    """TU Activity code dimension item"""
    actcode_code: str
    actcode_text: str
    display_level: Optional[int] = None
    selectable: Optional[str] = None

    class Config:
        from_attributes = True


class TUSexItem(BaseModel):
    """TU Sex dimension item"""
    sex_code: str
    sex_text: str

    class Config:
        from_attributes = True


class TUAgeItem(BaseModel):
    """TU Age group dimension item"""
    age_code: str
    age_text: str
    display_level: Optional[int] = None

    class Config:
        from_attributes = True


class TURaceItem(BaseModel):
    """TU Race dimension item"""
    race_code: str
    race_text: str

    class Config:
        from_attributes = True


class TUEducationItem(BaseModel):
    """TU Education level dimension item"""
    educ_code: str
    educ_text: str

    class Config:
        from_attributes = True


class TUMaritalStatusItem(BaseModel):
    """TU Marital status dimension item"""
    maritlstat_code: str
    maritlstat_text: str

    class Config:
        from_attributes = True


class TULaborForceStatusItem(BaseModel):
    """TU Labor force status dimension item"""
    lfstat_code: str
    lfstat_text: str

    class Config:
        from_attributes = True


class TUOriginItem(BaseModel):
    """TU Hispanic/Latino origin dimension item"""
    orig_code: str
    orig_text: str

    class Config:
        from_attributes = True


class TURegionItem(BaseModel):
    """TU Region dimension item"""
    region_code: str
    region_text: str

    class Config:
        from_attributes = True


class TUWhereItem(BaseModel):
    """TU Where activity took place dimension item"""
    where_code: str
    where_text: str

    class Config:
        from_attributes = True


class TUWhoItem(BaseModel):
    """TU Who was present dimension item"""
    who_code: str
    who_text: str

    class Config:
        from_attributes = True


class TUTimeOfDayItem(BaseModel):
    """TU Time of day dimension item"""
    timeday_code: str
    timeday_text: str

    class Config:
        from_attributes = True


class TUDimensions(BaseModel):
    """Available dimensions for TU survey"""
    stat_types: List[TUStatTypeItem]
    activities: List[TUActivityItem]
    sexes: List[TUSexItem]
    ages: List[TUAgeItem]
    races: List[TURaceItem]
    educations: List[TUEducationItem]
    marital_statuses: List[TUMaritalStatusItem]
    labor_force_statuses: List[TULaborForceStatusItem]
    origins: List[TUOriginItem]
    regions: List[TURegionItem]
    wheres: List[TUWhereItem]
    whos: List[TUWhoItem]
    times_of_day: List[TUTimeOfDayItem]


# ==================== Series Models ====================

class TUSeriesInfo(BaseModel):
    """TU Series metadata with dimensions"""
    series_id: str
    seasonal: Optional[str] = None
    stattype_code: Optional[str] = None
    stattype_text: Optional[str] = None
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    sex_code: Optional[str] = None
    sex_text: Optional[str] = None
    age_code: Optional[str] = None
    age_text: Optional[str] = None
    race_code: Optional[str] = None
    race_text: Optional[str] = None
    educ_code: Optional[str] = None
    educ_text: Optional[str] = None
    maritlstat_code: Optional[str] = None
    maritlstat_text: Optional[str] = None
    lfstat_code: Optional[str] = None
    lfstat_text: Optional[str] = None
    orig_code: Optional[str] = None
    orig_text: Optional[str] = None
    region_code: Optional[str] = None
    region_text: Optional[str] = None
    where_code: Optional[str] = None
    where_text: Optional[str] = None
    who_code: Optional[str] = None
    who_text: Optional[str] = None
    timeday_code: Optional[str] = None
    timeday_text: Optional[str] = None
    series_title: Optional[str] = None
    begin_year: Optional[int] = None
    begin_period: Optional[str] = None
    end_year: Optional[int] = None
    end_period: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class TUSeriesListResponse(BaseModel):
    """Response for TU series list with filters"""
    survey_code: str = "TU"
    total: int
    limit: int
    offset: int
    series: List[TUSeriesInfo]


# ==================== Data Models ====================

class TUDataPoint(BaseModel):
    """A single TU time series observation"""
    year: int
    period: str
    period_name: str  # "2024", "Q1 2024", etc.
    value: Optional[float] = None
    footnote_codes: Optional[str] = None

    class Config:
        from_attributes = True


class TUSeriesData(BaseModel):
    """Time series data for a single TU series"""
    series_id: str
    activity_name: Optional[str] = None
    stattype_name: Optional[str] = None
    demographic_group: Optional[str] = None  # Combined description
    data_points: List[TUDataPoint]


class TUDataResponse(BaseModel):
    """Response for TU series data request"""
    survey_code: str = "TU"
    series: List[TUSeriesData]


# ==================== Overview Models ====================

class TUActivitySummary(BaseModel):
    """Summary for a major activity category"""
    actcode_code: str
    actcode_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None
    yoy_change: Optional[float] = None
    latest_year: Optional[int] = None


class TUOverviewResponse(BaseModel):
    """Overview of time use by major activities

    Shows average hours per day and participation rates for major activity categories
    (Personal care, Eating, Household activities, Work, Leisure, etc.)
    """
    survey_code: str = "TU"
    description: str = "American Time Use Survey"
    activities: List[TUActivitySummary]
    total_persons: Optional[float] = None
    latest_year: Optional[int] = None


class TUOverviewTimelinePoint(BaseModel):
    """Single point in overview timeline"""
    year: int
    period: str
    period_name: str
    activities: Dict[str, Optional[float]]  # actcode_code -> value


class TUOverviewTimelineResponse(BaseModel):
    """Timeline data for overview charts"""
    survey_code: str = "TU"
    stattype: str  # "avg_hours" or "participation"
    timeline: List[TUOverviewTimelinePoint]
    activity_names: Dict[str, str]  # actcode_code -> name


# ==================== Activity Analysis Models ====================

class TUActivityMetric(BaseModel):
    """Detailed metrics for an activity"""
    actcode_code: str
    actcode_text: str
    display_level: Optional[int] = None
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None
    yoy_change_hours: Optional[float] = None
    yoy_change_participation: Optional[float] = None
    latest_year: Optional[int] = None


class TUActivityAnalysisResponse(BaseModel):
    """Analysis of activity breakdown (with sub-activities)"""
    survey_code: str = "TU"
    parent_activity_code: Optional[str] = None
    parent_activity_name: Optional[str] = None
    demographic_filter: Optional[str] = None
    activities: List[TUActivityMetric]
    total_count: int
    latest_year: Optional[int] = None


class TUActivityTimelinePoint(BaseModel):
    """Single point in activity timeline"""
    year: int
    period: str
    period_name: str
    activities: Dict[str, Optional[float]]  # actcode_code -> value


class TUActivityTimelineResponse(BaseModel):
    """Timeline data for activity comparison charts"""
    survey_code: str = "TU"
    stattype: str  # "avg_hours", "participation", "avg_hours_participants"
    timeline: List[TUActivityTimelinePoint]
    activity_names: Dict[str, str]


# ==================== Demographics Analysis Models ====================

class TUDemographicMetric(BaseModel):
    """Metrics for a demographic group"""
    group_code: str
    group_name: str
    demographic_type: str  # "sex", "age", "race", etc.
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None
    yoy_change: Optional[float] = None
    latest_year: Optional[int] = None


class TUDemographicAnalysisResponse(BaseModel):
    """Compare time use across demographic groups for an activity"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    demographic_type: str  # "sex", "age", "race", "education", "labor_force", "marital"
    groups: List[TUDemographicMetric]
    latest_year: Optional[int] = None


class TUDemographicTimelinePoint(BaseModel):
    """Single point in demographic timeline"""
    year: int
    period: str
    period_name: str
    groups: Dict[str, Optional[float]]  # group_code -> value


class TUDemographicTimelineResponse(BaseModel):
    """Timeline data for demographic comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    demographic_type: str
    stattype: str
    timeline: List[TUDemographicTimelinePoint]
    group_names: Dict[str, str]


# ==================== Sex Comparison Models ====================

class TUSexComparison(BaseModel):
    """Time use comparison by sex"""
    sex_code: str
    sex_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


class TUSexComparisonResponse(BaseModel):
    """Compare activity time use between sexes"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    comparisons: List[TUSexComparison]
    latest_year: Optional[int] = None


class TUSexTimelinePoint(BaseModel):
    """Single point in sex comparison timeline"""
    year: int
    period: str
    period_name: str
    male: Optional[float] = None
    female: Optional[float] = None


class TUSexTimelineResponse(BaseModel):
    """Timeline data for sex comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TUSexTimelinePoint]


# ==================== Age Comparison Models ====================

class TUAgeComparison(BaseModel):
    """Time use comparison by age group"""
    age_code: str
    age_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


class TUAgeComparisonResponse(BaseModel):
    """Compare activity time use across age groups"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    comparisons: List[TUAgeComparison]
    latest_year: Optional[int] = None


class TUAgeTimelinePoint(BaseModel):
    """Single point in age comparison timeline"""
    year: int
    period: str
    period_name: str
    ages: Dict[str, Optional[float]]  # age_code -> value


class TUAgeTimelineResponse(BaseModel):
    """Timeline data for age comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TUAgeTimelinePoint]
    age_names: Dict[str, str]


# ==================== Labor Force Comparison Models ====================

class TULaborForceComparison(BaseModel):
    """Time use comparison by labor force status"""
    lfstat_code: str
    lfstat_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


class TULaborForceComparisonResponse(BaseModel):
    """Compare activity time use by labor force status"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    comparisons: List[TULaborForceComparison]
    latest_year: Optional[int] = None


class TULaborForceTimelinePoint(BaseModel):
    """Single point in labor force comparison timeline"""
    year: int
    period: str
    period_name: str
    statuses: Dict[str, Optional[float]]  # lfstat_code -> value


class TULaborForceTimelineResponse(BaseModel):
    """Timeline data for labor force comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TULaborForceTimelinePoint]
    status_names: Dict[str, str]


# ==================== Bulk Response Models ====================

class TUSexBulkResponse(BaseModel):
    """Bulk sex comparison data for multiple activities"""
    survey_code: str = "TU"
    latest_year: Optional[int] = None
    activities: Dict[str, TUSexComparisonResponse]  # actcode_code -> comparison data


class TUAgeBulkResponse(BaseModel):
    """Bulk age comparison data for multiple activities"""
    survey_code: str = "TU"
    latest_year: Optional[int] = None
    age_groups: List[TUAgeItem]  # List of age group definitions
    activities: Dict[str, TUAgeComparisonResponse]  # actcode_code -> comparison data


class TULaborForceBulkResponse(BaseModel):
    """Bulk labor force comparison data for multiple activities"""
    survey_code: str = "TU"
    latest_year: Optional[int] = None
    labor_force_statuses: List[TULaborForceStatusItem]  # List of status definitions
    activities: Dict[str, TULaborForceComparisonResponse]  # actcode_code -> comparison data


# ==================== Education Comparison Models ====================

class TUEducationComparison(BaseModel):
    """Time use comparison by education level"""
    educ_code: str
    educ_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


class TUEducationComparisonResponse(BaseModel):
    """Compare activity time use across education levels"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    comparisons: List[TUEducationComparison]
    latest_year: Optional[int] = None


class TUEducationTimelinePoint(BaseModel):
    """Single point in education comparison timeline"""
    year: int
    period: str
    period_name: str
    educations: Dict[str, Optional[float]]  # educ_code -> value


class TUEducationTimelineResponse(BaseModel):
    """Timeline data for education comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TUEducationTimelinePoint]
    education_names: Dict[str, str]


# ==================== Race Comparison Models ====================

class TURaceComparison(BaseModel):
    """Time use comparison by race"""
    race_code: str
    race_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


class TURaceComparisonResponse(BaseModel):
    """Compare activity time use across race groups"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    comparisons: List[TURaceComparison]
    latest_year: Optional[int] = None


class TURaceTimelinePoint(BaseModel):
    """Single point in race comparison timeline"""
    year: int
    period: str
    period_name: str
    races: Dict[str, Optional[float]]  # race_code -> value


class TURaceTimelineResponse(BaseModel):
    """Timeline data for race comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TURaceTimelinePoint]
    race_names: Dict[str, str]


# ==================== Day Type Comparison Models ====================

class TUDayTypeComparison(BaseModel):
    """Time use comparison by day type"""
    pertype_code: str
    pertype_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


class TUDayTypeComparisonResponse(BaseModel):
    """Compare activity time use by day type (weekday vs weekend)"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    comparisons: List[TUDayTypeComparison]
    latest_year: Optional[int] = None


class TUDayTypeTimelinePoint(BaseModel):
    """Single point in day type comparison timeline"""
    year: int
    period: str
    period_name: str
    day_types: Dict[str, Optional[float]]  # pertype_code -> value


class TUDayTypeTimelineResponse(BaseModel):
    """Timeline data for day type comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TUDayTypeTimelinePoint]
    day_type_names: Dict[str, str]


# ==================== Legacy Day Type Analysis Models ====================

class TUDayTypeMetric(BaseModel):
    """Time use by day type (weekday vs weekend) - Legacy"""
    day_type: str  # "weekday", "weekend", "all_days"
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None


# ==================== Where/Who Context Models ====================

class TUWhereMetric(BaseModel):
    """Time use by location"""
    where_code: str
    where_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None


class TUWhereAnalysisResponse(BaseModel):
    """Analyze where activities take place"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    locations: List[TUWhereMetric]
    latest_year: Optional[int] = None


class TUWhoMetric(BaseModel):
    """Time use by who was present"""
    who_code: str
    who_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None


class TUWhoAnalysisResponse(BaseModel):
    """Analyze who was present during activities"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    companions: List[TUWhoMetric]
    latest_year: Optional[int] = None


# ==================== Top Activities Models ====================

class TUTopActivity(BaseModel):
    """A top activity by time spent"""
    actcode_code: str
    actcode_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    rank: int


class TUTopActivitiesResponse(BaseModel):
    """Top activities by time spent for a demographic"""
    survey_code: str = "TU"
    demographic_filter: Optional[str] = None
    ranking_type: str  # "most_time", "highest_participation"
    activities: List[TUTopActivity]
    latest_year: Optional[int] = None


# ==================== Time Trends Models ====================

class TUTimeTrendPoint(BaseModel):
    """Single point in a time trend"""
    year: int
    period: str
    period_name: str
    value: Optional[float] = None
    yoy_change: Optional[float] = None


class TUTimeTrendResponse(BaseModel):
    """Time trend data for an activity"""
    survey_code: str = "TU"
    actcode_code: str
    actcode_text: str
    stattype: str  # "avg_hours", "participation"
    demographic_filter: Optional[str] = None
    timeline: List[TUTimeTrendPoint]


# ==================== Region Analysis Models ====================

class TURegionMetric(BaseModel):
    """Time use metrics by region"""
    region_code: str
    region_text: str
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None


class TURegionAnalysisResponse(BaseModel):
    """Compare time use across regions"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    regions: List[TURegionMetric]
    latest_year: Optional[int] = None


class TURegionTimelinePoint(BaseModel):
    """Single point in region comparison timeline"""
    year: int
    period: str
    period_name: str
    regions: Dict[str, Optional[float]]  # region_code -> value


class TURegionTimelineResponse(BaseModel):
    """Timeline data for region comparison"""
    survey_code: str = "TU"
    actcode_code: Optional[str] = None
    actcode_text: Optional[str] = None
    stattype: str
    timeline: List[TURegionTimelinePoint]
    region_names: Dict[str, str]


# ==================== Year-over-Year Change Models ====================

class TUActivityChange(BaseModel):
    """Year-over-year change for an activity"""
    actcode_code: str
    actcode_text: str
    current_value: Optional[float] = None
    prev_value: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None


class TUYoYChangeResponse(BaseModel):
    """Year-over-year changes for activities"""
    survey_code: str = "TU"
    stattype: str  # "avg_hours", "participation"
    latest_year: int
    prev_year: int
    gainers: List[TUActivityChange]
    losers: List[TUActivityChange]


# ==================== Profile Models ====================

class TUActivityProfile(BaseModel):
    """Complete profile for an activity"""
    actcode_code: str
    actcode_text: str
    # Overall metrics
    avg_hours_per_day: Optional[float] = None
    participation_rate: Optional[float] = None
    avg_hours_participants: Optional[float] = None
    number_of_persons: Optional[float] = None
    # By sex
    male_hours: Optional[float] = None
    female_hours: Optional[float] = None
    # Year-over-year
    yoy_change_hours: Optional[float] = None
    yoy_change_participation: Optional[float] = None
    latest_year: Optional[int] = None


class TUActivityProfileResponse(BaseModel):
    """Full activity profile response"""
    survey_code: str = "TU"
    profile: TUActivityProfile


# ==================== Drill-down Series Explorer Models ====================

class TUDrilldownLevel(BaseModel):
    """A level in the drill-down hierarchy"""
    dimension: str  # "activity", "stattype", "sex", "age", etc.
    code: str
    name: str
    has_children: bool = False
    child_count: int = 0


class TUDrilldownResponse(BaseModel):
    """Response for drill-down navigation"""
    survey_code: str = "TU"
    current_path: List[TUDrilldownLevel]
    children: List[TUDrilldownLevel]
    available_dimensions: List[str]
    series_count: int
