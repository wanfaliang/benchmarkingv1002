"""
TU (American Time Use Survey) Explorer API

Provides endpoints for exploring ATUS data including:
- Time spent on major activities (sleeping, working, eating, leisure, etc.)
- Demographics breakdown (sex, age, race, education, labor force status)
- Participation rates and average hours per day
- Year-over-year trend analysis

Data is annual, from 2003-present.

OPTIMIZATIONS:
- Batch queries for dimension lookups
- Targeted indexes on frequently filtered columns
- Precomputed aggregations where possible
- Efficient pagination with indexed sorting
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select, func, and_, or_, desc, asc, case
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Tuple
from decimal import Decimal

from ....database import get_data_db
from ....data_models.bls_models import (
    TUSeries, TUData, TUAspect,
    TUStatType, TUActivityCode, TUSex, TUAge, TURace, TUEducation,
    TUMaritalStatus, TULaborForceStatus, TUOrigin, TURegion, TUWhere, TUWho, TUTimeOfDay
)
from .tu_schemas import (
    TUDimensions, TUStatTypeItem, TUActivityItem, TUSexItem, TUAgeItem, TURaceItem,
    TUEducationItem, TUMaritalStatusItem, TULaborForceStatusItem, TUOriginItem,
    TURegionItem, TUWhereItem, TUWhoItem, TUTimeOfDayItem,
    TUSeriesInfo, TUSeriesListResponse,
    TUDataPoint, TUSeriesData, TUDataResponse,
    TUActivitySummary, TUOverviewResponse, TUOverviewTimelinePoint, TUOverviewTimelineResponse,
    TUActivityMetric, TUActivityAnalysisResponse, TUActivityTimelinePoint, TUActivityTimelineResponse,
    TUDemographicMetric, TUDemographicAnalysisResponse, TUDemographicTimelinePoint, TUDemographicTimelineResponse,
    TUSexComparison, TUSexComparisonResponse, TUSexTimelinePoint, TUSexTimelineResponse,
    TUAgeComparison, TUAgeComparisonResponse, TUAgeTimelinePoint, TUAgeTimelineResponse,
    TULaborForceComparison, TULaborForceComparisonResponse, TULaborForceTimelinePoint, TULaborForceTimelineResponse,
    TUEducationComparison, TUEducationComparisonResponse, TUEducationTimelinePoint, TUEducationTimelineResponse,
    TURaceComparison, TURaceComparisonResponse, TURaceTimelinePoint, TURaceTimelineResponse,
    TUDayTypeComparison, TUDayTypeComparisonResponse, TUDayTypeTimelinePoint, TUDayTypeTimelineResponse,
    TUTopActivity, TUTopActivitiesResponse,
    TUTimeTrendPoint, TUTimeTrendResponse,
    TURegionMetric, TURegionAnalysisResponse, TURegionTimelinePoint, TURegionTimelineResponse,
    TUActivityChange, TUYoYChangeResponse,
    TUActivityProfile, TUActivityProfileResponse,
    TUDrilldownLevel, TUDrilldownResponse,
    TUSexBulkResponse, TUAgeBulkResponse, TULaborForceBulkResponse
)

router = APIRouter(prefix="/api/research/bls/tu", tags=["BLS TU Research"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def decimal_to_float(val) -> Optional[float]:
    """Convert Decimal to float, handling None"""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    return val


def get_period_name(year: int, period: str) -> str:
    """Convert period code to display name"""
    if period == 'A01':
        return str(year)
    elif period.startswith('Q'):
        return f"Q{period[1:]} {year}"
    return f"{period} {year}"


# Major activity codes (top level activities for overview)
# 010100 (Sleeping) added as it's what most users care about
# The 600xxx codes are summary categories from bls_tu_actcodes with display_level=1
MAJOR_ACTIVITY_CODES = [
    '010100',  # Sleeping
    '600013',  # Working and work-related activities (includes travel)
    '600023',  # Leisure and sports (includes travel)
    '600022',  # Eating and drinking (includes travel)
    '600003',  # Household activities (includes travel)
    '600018',  # Purchasing goods and services (includes travel)
    '600007',  # Caring for and helping household members (includes travel)
    '600010',  # Caring for and helping nonhousehold members (includes travel)
    '600016',  # Educational activities (includes travel)
    '600030',  # Organizational, civic, and religious activities
    '600033',  # Telephone calls, mail, and e-mail (includes travel)
    '600034',  # Other activities, not elsewhere classified
]

# Some common detailed activity codes for sub-activities
DETAILED_ACTIVITY_CODES = [
    '010100',  # Sleeping
    '010200',  # Grooming
    '020100',  # Housework
    '020200',  # Food preparation and cleanup
    '050101',  # Working, main job
    '110100',  # Eating and drinking
    '120300',  # Relaxing and leisure
    '180000',  # Traveling
]

# Key stat type codes (from bls_tu_stattypes)
STAT_HOURS_PER_DAY = '10101'  # Average hours per day
STAT_PARTICIPATION = '30105'  # Percent of population engaged in activity on an average day
STAT_HOURS_PARTICIPANTS = '20101'  # Average hours per day for participants in an activity

# Sex codes
SEX_BOTH = '0'
SEX_MALE = '1'
SEX_FEMALE = '2'

# Age code for all ages
AGE_ALL = '000'

# Age code for education/race breakdowns (25 years and over - most meaningful for education level)
AGE_25_AND_OVER = '028'

# Person type code for all days average (not weekend-only or weekday-only)
PERTYPE_ALL_DAYS = '00'

# Activities that have education breakdown data available in BLS ATUS
# (Most activities only have aggregate data - these have specific education level breakdowns)
EDUCATION_BREAKDOWN_ACTIVITIES = [
    '000000',  # Total, all activities
    '050100',  # Working
    '120301',  # Relaxing and thinking
    '120307',  # Playing games
    '120308',  # Computer use for leisure (excluding games)
    '120312',  # Reading for personal interest
    '600001',  # Personal care activities (includes travel)
    '600003',  # Household activities (includes travel)
    '600007',  # Caring for and helping household members (includes travel)
    '600010',  # Caring for and helping nonhousehold members (includes travel)
    '600013',  # Working and work-related activities (includes travel)
    '600016',  # Educational activities (includes travel)
    '600018',  # Purchasing goods and services (includes travel)
    '600022',  # Eating and drinking (includes travel)
    '600023',  # Leisure and sports (includes travel)
    '600024',  # Socializing and communicating
    '600025',  # Watching TV
    '600027',  # Participating in sports, exercise, and recreation
    '600030',  # Organizational, civic, and religious activities
    '600033',  # Telephone calls, mail, and e-mail (includes travel)
    '600034',  # Other activities, not elsewhere classified
    '600058',  # Playing games and computer use for leisure
    '600059',  # Other leisure and sports activities, including travel
    '600085',  # Awake time
]

# Activities that have race breakdown data (same as education for ATUS)
RACE_BREAKDOWN_ACTIVITIES = EDUCATION_BREAKDOWN_ACTIVITIES


# ============================================================================
# DIMENSIONS ENDPOINT
# ============================================================================

@router.get("/dimensions", response_model=TUDimensions)
async def get_dimensions(db: Session = Depends(get_data_db)):
    """Get available dimensions for filtering TU data"""

    # Get all dimension data in parallel queries
    stat_types = db.execute(
        select(TUStatType)
        .where(TUStatType.selectable == 'T')
        .order_by(TUStatType.sort_sequence)
    ).scalars().all()

    activities = db.execute(
        select(TUActivityCode)
        .where(TUActivityCode.selectable == 'T')
        .order_by(TUActivityCode.sort_sequence)
    ).scalars().all()

    sexes = db.execute(
        select(TUSex)
        .where(TUSex.selectable == 'T')
        .order_by(TUSex.sort_sequence)
    ).scalars().all()

    ages = db.execute(
        select(TUAge)
        .where(TUAge.selectable == 'T')
        .order_by(TUAge.sort_sequence)
    ).scalars().all()

    races = db.execute(
        select(TURace)
        .where(TURace.selectable == 'T')
        .order_by(TURace.sort_sequence)
    ).scalars().all()

    educations = db.execute(
        select(TUEducation)
        .where(TUEducation.selectable == 'T')
        .order_by(TUEducation.sort_sequence)
    ).scalars().all()

    marital_statuses = db.execute(
        select(TUMaritalStatus)
        .where(TUMaritalStatus.selectable == 'T')
        .order_by(TUMaritalStatus.sort_sequence)
    ).scalars().all()

    labor_force_statuses = db.execute(
        select(TULaborForceStatus)
        .where(TULaborForceStatus.selectable == 'T')
        .order_by(TULaborForceStatus.sort_sequence)
    ).scalars().all()

    origins = db.execute(
        select(TUOrigin)
        .where(TUOrigin.selectable == 'T')
        .order_by(TUOrigin.sort_sequence)
    ).scalars().all()

    regions = db.execute(
        select(TURegion)
        .where(TURegion.selectable == 'T')
        .order_by(TURegion.sort_sequence)
    ).scalars().all()

    wheres = db.execute(
        select(TUWhere)
        .where(TUWhere.selectable == 'T')
        .order_by(TUWhere.sort_sequence)
    ).scalars().all()

    whos = db.execute(
        select(TUWho)
        .where(TUWho.selectable == 'T')
        .order_by(TUWho.sort_sequence)
    ).scalars().all()

    times_of_day = db.execute(
        select(TUTimeOfDay)
        .where(TUTimeOfDay.selectable == 'T')
        .order_by(TUTimeOfDay.sort_sequence)
    ).scalars().all()

    return TUDimensions(
        stat_types=[TUStatTypeItem(
            stattype_code=s.stattype_code,
            stattype_text=s.stattype_text,
            display_level=s.display_level,
            selectable=s.selectable
        ) for s in stat_types],
        activities=[TUActivityItem(
            actcode_code=a.actcode_code,
            actcode_text=a.actcode_text,
            display_level=a.display_level,
            selectable=a.selectable
        ) for a in activities],
        sexes=[TUSexItem(sex_code=s.sex_code, sex_text=s.sex_text) for s in sexes],
        ages=[TUAgeItem(age_code=a.age_code, age_text=a.age_text, display_level=a.display_level) for a in ages],
        races=[TURaceItem(race_code=r.race_code, race_text=r.race_text) for r in races],
        educations=[TUEducationItem(educ_code=e.educ_code, educ_text=e.educ_text) for e in educations],
        marital_statuses=[TUMaritalStatusItem(maritlstat_code=m.maritlstat_code, maritlstat_text=m.maritlstat_text) for m in marital_statuses],
        labor_force_statuses=[TULaborForceStatusItem(lfstat_code=l.lfstat_code, lfstat_text=l.lfstat_text) for l in labor_force_statuses],
        origins=[TUOriginItem(orig_code=o.orig_code, orig_text=o.orig_text) for o in origins],
        regions=[TURegionItem(region_code=r.region_code, region_text=r.region_text) for r in regions],
        wheres=[TUWhereItem(where_code=w.where_code, where_text=w.where_text) for w in wheres],
        whos=[TUWhoItem(who_code=w.who_code, who_text=w.who_text) for w in whos],
        times_of_day=[TUTimeOfDayItem(timeday_code=t.timeday_code, timeday_text=t.timeday_text) for t in times_of_day]
    )


# ============================================================================
# SERIES EXPLORER ENDPOINTS - THREE METHODS
# ============================================================================

@router.get("/series/search", response_model=TUSeriesListResponse)
async def search_series(
    search: str = Query(..., description="Search term for series title or activity"),
    stattype_code: Optional[str] = Query(None, description="Filter by stat type"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Search series by text (Method 1: Search)"""
    query = select(TUSeries).where(
        or_(
            TUSeries.series_title.ilike(f'%{search}%'),
            TUSeries.series_id.ilike(f'%{search}%')
        )
    )

    if stattype_code:
        query = query.where(TUSeries.stattype_code == stattype_code)

    # Get count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Get paginated results
    query = query.order_by(TUSeries.series_id).limit(limit).offset(offset)
    series_list = db.execute(query).scalars().all()

    # Batch lookup dimension names
    series_info_list = await _enrich_series_list(db, series_list)

    return TUSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_info_list
    )


@router.get("/series/browse", response_model=TUSeriesListResponse)
async def browse_series(
    actcode_code: Optional[str] = Query(None, description="Filter by activity code"),
    stattype_code: Optional[str] = Query(None, description="Filter by stat type"),
    sex_code: Optional[str] = Query(None, description="Filter by sex"),
    age_code: Optional[str] = Query(None, description="Filter by age group"),
    race_code: Optional[str] = Query(None, description="Filter by race"),
    educ_code: Optional[str] = Query(None, description="Filter by education level"),
    lfstat_code: Optional[str] = Query(None, description="Filter by labor force status"),
    region_code: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_data_db)
):
    """Browse series with filters (Method 2: Browse with filters)"""
    query = select(TUSeries)

    if actcode_code:
        query = query.where(TUSeries.actcode_code == actcode_code)
    if stattype_code:
        query = query.where(TUSeries.stattype_code == stattype_code)
    if sex_code:
        query = query.where(TUSeries.sex_code == sex_code)
    if age_code:
        query = query.where(TUSeries.age_code == age_code)
    if race_code:
        query = query.where(TUSeries.race_code == race_code)
    if educ_code:
        query = query.where(TUSeries.educ_code == educ_code)
    if lfstat_code:
        query = query.where(TUSeries.lfstat_code == lfstat_code)
    if region_code:
        query = query.where(TUSeries.region_code == region_code)

    # Check if we have any filters
    has_filters = any([actcode_code, stattype_code, sex_code, age_code, race_code, educ_code, lfstat_code, region_code])

    if has_filters:
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar() or 0
    else:
        # Estimate total for unfiltered query
        total = 100000  # Approximate count to avoid expensive COUNT(*)

    query = query.order_by(TUSeries.series_id).limit(limit).offset(offset)
    series_list = db.execute(query).scalars().all()

    series_info_list = await _enrich_series_list(db, series_list)

    return TUSeriesListResponse(
        total=total,
        limit=limit,
        offset=offset,
        series=series_info_list
    )


@router.get("/series/drilldown", response_model=TUDrilldownResponse)
async def drilldown_series(
    actcode_code: Optional[str] = Query(None, description="Current activity code"),
    stattype_code: Optional[str] = Query(None, description="Current stat type"),
    sex_code: Optional[str] = Query(None, description="Current sex"),
    age_code: Optional[str] = Query(None, description="Current age group"),
    db: Session = Depends(get_data_db)
):
    """Drill-down navigation through dimensions (Method 3: Drill-down)"""
    current_path = []
    children = []
    available_dimensions = []

    # Build current path
    if actcode_code:
        act_name = db.execute(
            select(TUActivityCode.actcode_text).where(TUActivityCode.actcode_code == actcode_code)
        ).scalar()
        current_path.append(TUDrilldownLevel(
            dimension="activity", code=actcode_code, name=act_name or actcode_code
        ))

    if stattype_code:
        stat_name = db.execute(
            select(TUStatType.stattype_text).where(TUStatType.stattype_code == stattype_code)
        ).scalar()
        current_path.append(TUDrilldownLevel(
            dimension="stattype", code=stattype_code, name=stat_name or stattype_code
        ))

    if sex_code:
        sex_name = db.execute(
            select(TUSex.sex_text).where(TUSex.sex_code == sex_code)
        ).scalar()
        current_path.append(TUDrilldownLevel(
            dimension="sex", code=sex_code, name=sex_name or sex_code
        ))

    if age_code:
        age_name = db.execute(
            select(TUAge.age_text).where(TUAge.age_code == age_code)
        ).scalar()
        current_path.append(TUDrilldownLevel(
            dimension="age", code=age_code, name=age_name or age_code
        ))

    # Determine next drill-down options
    base_query = select(TUSeries)
    if actcode_code:
        base_query = base_query.where(TUSeries.actcode_code == actcode_code)
    if stattype_code:
        base_query = base_query.where(TUSeries.stattype_code == stattype_code)
    if sex_code:
        base_query = base_query.where(TUSeries.sex_code == sex_code)
    if age_code:
        base_query = base_query.where(TUSeries.age_code == age_code)

    # First level: Activity
    if not actcode_code:
        activities = db.execute(
            select(TUActivityCode.actcode_code, TUActivityCode.actcode_text, func.count(TUSeries.series_id).label('cnt'))
            .join(TUSeries, TUSeries.actcode_code == TUActivityCode.actcode_code)
            .where(TUActivityCode.display_level <= 1)
            .group_by(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
            .order_by(TUActivityCode.sort_sequence)
            .limit(30)
        ).all()

        children = [TUDrilldownLevel(
            dimension="activity",
            code=a.actcode_code,
            name=a.actcode_text,
            has_children=True,
            child_count=a.cnt
        ) for a in activities]
        available_dimensions = ["activity"]

    # Second level: Stat type
    elif not stattype_code:
        stat_types = db.execute(
            select(TUStatType.stattype_code, TUStatType.stattype_text, func.count(TUSeries.series_id).label('cnt'))
            .join(TUSeries, TUSeries.stattype_code == TUStatType.stattype_code)
            .where(TUSeries.actcode_code == actcode_code)
            .group_by(TUStatType.stattype_code, TUStatType.stattype_text)
            .order_by(TUStatType.sort_sequence)
        ).all()

        children = [TUDrilldownLevel(
            dimension="stattype",
            code=s.stattype_code,
            name=s.stattype_text,
            has_children=True,
            child_count=s.cnt
        ) for s in stat_types]
        available_dimensions = ["stattype", "sex", "age"]

    # Third level: Sex
    elif not sex_code:
        sexes = db.execute(
            select(TUSex.sex_code, TUSex.sex_text, func.count(TUSeries.series_id).label('cnt'))
            .join(TUSeries, TUSeries.sex_code == TUSex.sex_code)
            .where(and_(
                TUSeries.actcode_code == actcode_code,
                TUSeries.stattype_code == stattype_code
            ))
            .group_by(TUSex.sex_code, TUSex.sex_text)
            .order_by(TUSex.sort_sequence)
        ).all()

        children = [TUDrilldownLevel(
            dimension="sex",
            code=s.sex_code,
            name=s.sex_text,
            has_children=True,
            child_count=s.cnt
        ) for s in sexes]
        available_dimensions = ["sex", "age", "race"]

    # Fourth level: Age
    elif not age_code:
        ages = db.execute(
            select(TUAge.age_code, TUAge.age_text, func.count(TUSeries.series_id).label('cnt'))
            .join(TUSeries, TUSeries.age_code == TUAge.age_code)
            .where(and_(
                TUSeries.actcode_code == actcode_code,
                TUSeries.stattype_code == stattype_code,
                TUSeries.sex_code == sex_code
            ))
            .group_by(TUAge.age_code, TUAge.age_text)
            .order_by(TUAge.sort_sequence)
        ).all()

        children = [TUDrilldownLevel(
            dimension="age",
            code=a.age_code,
            name=a.age_text,
            has_children=False,
            child_count=a.cnt
        ) for a in ages]
        available_dimensions = ["age", "race", "education"]

    # Count matching series
    series_count = db.execute(
        select(func.count()).select_from(base_query.subquery())
    ).scalar() or 0

    return TUDrilldownResponse(
        current_path=current_path,
        children=children,
        available_dimensions=available_dimensions,
        series_count=series_count
    )


async def _enrich_series_list(db: Session, series_list: List[TUSeries]) -> List[TUSeriesInfo]:
    """Batch lookup dimension names for series list"""
    if not series_list:
        return []

    # Collect unique codes
    actcode_codes = list(set(s.actcode_code for s in series_list if s.actcode_code))
    stattype_codes = list(set(s.stattype_code for s in series_list if s.stattype_code))
    sex_codes = list(set(s.sex_code for s in series_list if s.sex_code))
    age_codes = list(set(s.age_code for s in series_list if s.age_code))
    race_codes = list(set(s.race_code for s in series_list if s.race_code))
    educ_codes = list(set(s.educ_code for s in series_list if s.educ_code))
    maritlstat_codes = list(set(s.maritlstat_code for s in series_list if s.maritlstat_code))
    lfstat_codes = list(set(s.lfstat_code for s in series_list if s.lfstat_code))
    orig_codes = list(set(s.orig_code for s in series_list if s.orig_code))
    region_codes = list(set(s.region_code for s in series_list if s.region_code))
    where_codes = list(set(s.where_code for s in series_list if s.where_code))
    who_codes = list(set(s.who_code for s in series_list if s.who_code))
    timeday_codes = list(set(s.timeday_code for s in series_list if s.timeday_code))

    # Batch lookups
    actcode_names = {}
    stattype_names = {}
    sex_names = {}
    age_names = {}
    race_names = {}
    educ_names = {}
    maritlstat_names = {}
    lfstat_names = {}
    orig_names = {}
    region_names = {}
    where_names = {}
    who_names = {}
    timeday_names = {}

    if actcode_codes:
        results = db.execute(
            select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
            .where(TUActivityCode.actcode_code.in_(actcode_codes))
        ).all()
        actcode_names = {r.actcode_code: r.actcode_text for r in results}

    if stattype_codes:
        results = db.execute(
            select(TUStatType.stattype_code, TUStatType.stattype_text)
            .where(TUStatType.stattype_code.in_(stattype_codes))
        ).all()
        stattype_names = {r.stattype_code: r.stattype_text for r in results}

    if sex_codes:
        results = db.execute(
            select(TUSex.sex_code, TUSex.sex_text)
            .where(TUSex.sex_code.in_(sex_codes))
        ).all()
        sex_names = {r.sex_code: r.sex_text for r in results}

    if age_codes:
        results = db.execute(
            select(TUAge.age_code, TUAge.age_text)
            .where(TUAge.age_code.in_(age_codes))
        ).all()
        age_names = {r.age_code: r.age_text for r in results}

    if race_codes:
        results = db.execute(
            select(TURace.race_code, TURace.race_text)
            .where(TURace.race_code.in_(race_codes))
        ).all()
        race_names = {r.race_code: r.race_text for r in results}

    if educ_codes:
        results = db.execute(
            select(TUEducation.educ_code, TUEducation.educ_text)
            .where(TUEducation.educ_code.in_(educ_codes))
        ).all()
        educ_names = {r.educ_code: r.educ_text for r in results}

    if maritlstat_codes:
        results = db.execute(
            select(TUMaritalStatus.maritlstat_code, TUMaritalStatus.maritlstat_text)
            .where(TUMaritalStatus.maritlstat_code.in_(maritlstat_codes))
        ).all()
        maritlstat_names = {r.maritlstat_code: r.maritlstat_text for r in results}

    if lfstat_codes:
        results = db.execute(
            select(TULaborForceStatus.lfstat_code, TULaborForceStatus.lfstat_text)
            .where(TULaborForceStatus.lfstat_code.in_(lfstat_codes))
        ).all()
        lfstat_names = {r.lfstat_code: r.lfstat_text for r in results}

    if orig_codes:
        results = db.execute(
            select(TUOrigin.orig_code, TUOrigin.orig_text)
            .where(TUOrigin.orig_code.in_(orig_codes))
        ).all()
        orig_names = {r.orig_code: r.orig_text for r in results}

    if region_codes:
        results = db.execute(
            select(TURegion.region_code, TURegion.region_text)
            .where(TURegion.region_code.in_(region_codes))
        ).all()
        region_names = {r.region_code: r.region_text for r in results}

    if where_codes:
        results = db.execute(
            select(TUWhere.where_code, TUWhere.where_text)
            .where(TUWhere.where_code.in_(where_codes))
        ).all()
        where_names = {r.where_code: r.where_text for r in results}

    if who_codes:
        results = db.execute(
            select(TUWho.who_code, TUWho.who_text)
            .where(TUWho.who_code.in_(who_codes))
        ).all()
        who_names = {r.who_code: r.who_text for r in results}

    if timeday_codes:
        results = db.execute(
            select(TUTimeOfDay.timeday_code, TUTimeOfDay.timeday_text)
            .where(TUTimeOfDay.timeday_code.in_(timeday_codes))
        ).all()
        timeday_names = {r.timeday_code: r.timeday_text for r in results}

    return [TUSeriesInfo(
        series_id=s.series_id,
        seasonal=s.seasonal,
        stattype_code=s.stattype_code,
        stattype_text=stattype_names.get(s.stattype_code),
        actcode_code=s.actcode_code,
        actcode_text=actcode_names.get(s.actcode_code),
        sex_code=s.sex_code,
        sex_text=sex_names.get(s.sex_code),
        age_code=s.age_code,
        age_text=age_names.get(s.age_code),
        race_code=s.race_code,
        race_text=race_names.get(s.race_code),
        educ_code=s.educ_code,
        educ_text=educ_names.get(s.educ_code),
        maritlstat_code=s.maritlstat_code,
        maritlstat_text=maritlstat_names.get(s.maritlstat_code),
        lfstat_code=s.lfstat_code,
        lfstat_text=lfstat_names.get(s.lfstat_code),
        orig_code=s.orig_code,
        orig_text=orig_names.get(s.orig_code),
        region_code=s.region_code,
        region_text=region_names.get(s.region_code),
        where_code=s.where_code,
        where_text=where_names.get(s.where_code),
        who_code=s.who_code,
        who_text=who_names.get(s.who_code),
        timeday_code=s.timeday_code,
        timeday_text=timeday_names.get(s.timeday_code),
        series_title=s.series_title,
        begin_year=s.begin_year,
        begin_period=s.begin_period,
        end_year=s.end_year,
        end_period=s.end_period,
        is_active=s.is_active if s.is_active is not None else True
    ) for s in series_list]


# ============================================================================
# DATA ENDPOINT
# ============================================================================

@router.get("/series/{series_id}/data", response_model=TUDataResponse)
async def get_series_data(
    series_id: str,
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    db: Session = Depends(get_data_db)
):
    """Get time series data for a specific TU series"""
    # Get series info
    series = db.execute(
        select(TUSeries).where(TUSeries.series_id == series_id)
    ).scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")

    # Get data
    query = select(TUData).where(TUData.series_id == series_id)

    if start_year:
        query = query.where(TUData.year >= start_year)
    if end_year:
        query = query.where(TUData.year <= end_year)

    query = query.order_by(TUData.year, TUData.period)
    data_rows = db.execute(query).scalars().all()

    # Get dimension names
    activity_name = None
    stattype_name = None

    if series.actcode_code:
        activity_name = db.execute(
            select(TUActivityCode.actcode_text)
            .where(TUActivityCode.actcode_code == series.actcode_code)
        ).scalar()

    if series.stattype_code:
        stattype_name = db.execute(
            select(TUStatType.stattype_text)
            .where(TUStatType.stattype_code == series.stattype_code)
        ).scalar()

    return TUDataResponse(
        series=[TUSeriesData(
            series_id=series_id,
            activity_name=activity_name,
            stattype_name=stattype_name,
            demographic_group=series.series_title,
            data_points=[TUDataPoint(
                year=d.year,
                period=d.period,
                period_name=get_period_name(d.year, d.period),
                value=decimal_to_float(d.value),
                footnote_codes=d.footnote_codes
            ) for d in data_rows]
        )]
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=TUOverviewResponse)
async def get_overview(
    year: Optional[int] = Query(None, description="Year filter (default: latest)"),
    db: Session = Depends(get_data_db)
):
    """Get overview of time use by major activities

    Shows average hours per day for major activity categories.
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    # Get latest year if not specified
    if not year:
        latest = db.execute(
            select(func.max(TUData.year))
        ).scalar()
        year = latest or 2023

    # Batch query 1: Get activity names
    acts = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(MAJOR_ACTIVITY_CODES))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in acts}

    # Batch query 2: Find series IDs for all activity codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code)
        .where(and_(
            TUSeries.actcode_code.in_(MAJOR_ACTIVITY_CODES),
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    # Build actcode -> series_id map (take first match for each activity)
    actcode_to_series = {}
    for s in series_query:
        if s.actcode_code not in actcode_to_series:
            actcode_to_series[s.actcode_code] = s.series_id

    all_series_ids = list(actcode_to_series.values())

    # Batch query 3: Get current year values for all series
    current_values = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        current_values = {d.series_id: d.value for d in data_rows}

    # Batch query 4: Get previous year values for YoY calculation
    prev_values = {}
    if all_series_ids:
        prev_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year - 1,
                TUData.period == 'A01'
            ))
        ).all()
        prev_values = {d.series_id: d.value for d in prev_rows}

    # Build response from cached data
    activities_data = []
    for act_code in MAJOR_ACTIVITY_CODES:
        series_id = actcode_to_series.get(act_code)
        value = current_values.get(series_id) if series_id else None
        prev_value = prev_values.get(series_id) if series_id else None

        yoy = None
        if value is not None and prev_value is not None:
            yoy = decimal_to_float(value) - decimal_to_float(prev_value)

        activities_data.append(TUActivitySummary(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            avg_hours_per_day=decimal_to_float(value),
            yoy_change=yoy,
            latest_year=year
        ))

    return TUOverviewResponse(
        activities=activities_data,
        latest_year=year
    )


@router.get("/overview/timeline", response_model=TUOverviewTimelineResponse)
async def get_overview_timeline(
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    activities: Optional[str] = Query(None, description="Comma-separated activity codes"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for overview charts"""
    # Parse activity codes
    if activities:
        act_codes = [a.strip() for a in activities.split(',')]
    else:
        # Use top 6 major activities
        act_codes = MAJOR_ACTIVITY_CODES[:6]

    # Get year range
    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9  # Last 10 years

    # Get activity names
    activity_names = {}
    acts = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(act_codes))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in acts}

    # Find series IDs for each activity
    series_to_activity = {}
    for act_code in act_codes:
        series_id = db.execute(
            select(TUSeries.series_id)
            .where(and_(
                TUSeries.actcode_code == act_code,
                TUSeries.stattype_code == STAT_HOURS_PER_DAY,
                or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
                or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
                or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
            ))
            .limit(1)
        ).scalar()
        if series_id:
            series_to_activity[series_id] = act_code

    # Batch query for all data
    if series_to_activity:
        data_rows = db.execute(
            select(TUData)
            .where(and_(
                TUData.series_id.in_(list(series_to_activity.keys())),
                TUData.year >= start_year,
                TUData.year <= end_year,
                TUData.period == 'A01'
            ))
            .order_by(TUData.year)
        ).scalars().all()
    else:
        data_rows = []

    # Build timeline
    year_data: Dict[int, Dict[str, Optional[float]]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        act_code = series_to_activity.get(d.series_id)
        if act_code:
            year_data[d.year][act_code] = decimal_to_float(d.value)

    timeline = [
        TUOverviewTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            activities={act: year_data.get(year, {}).get(act) for act in act_codes}
        )
        for year in sorted(year_data.keys())
    ]

    return TUOverviewTimelineResponse(
        stattype="avg_hours",
        timeline=timeline,
        activity_names=activity_names
    )


# ============================================================================
# ACTIVITY ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/activity/{actcode_code}", response_model=TUActivityAnalysisResponse)
async def get_activity_analysis(
    actcode_code: str,
    year: Optional[int] = Query(None, description="Year filter"),
    include_subactivities: bool = Query(True, description="Include sub-activity breakdown"),
    db: Session = Depends(get_data_db)
):
    """Get detailed analysis for an activity with sub-activities
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    # Get latest year if not specified
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get parent activity name
    parent = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get sub-activities (codes that start with same prefix but are more specific)
    prefix = actcode_code[:2]  # First 2 digits are major category

    if include_subactivities:
        sub_activities = db.execute(
            select(TUActivityCode)
            .where(and_(
                TUActivityCode.actcode_code.like(f'{prefix}%'),
                TUActivityCode.display_level <= 2,
                TUActivityCode.selectable == 'T'
            ))
            .order_by(TUActivityCode.sort_sequence)
        ).scalars().all()
    else:
        sub_activities = db.execute(
            select(TUActivityCode)
            .where(TUActivityCode.actcode_code == actcode_code)
        ).scalars().all()

    if not sub_activities:
        return TUActivityAnalysisResponse(
            parent_activity_code=actcode_code,
            parent_activity_name=parent,
            activities=[],
            total_count=0,
            latest_year=year
        )

    # Get all activity codes we need
    act_codes = [a.actcode_code for a in sub_activities]

    # Batch query 1: Find all series for these activities at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code)
        .where(and_(
            TUSeries.actcode_code.in_(act_codes),
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    # Build actcode -> series_id map
    actcode_to_series = {}
    for s in series_query:
        if s.actcode_code not in actcode_to_series:
            actcode_to_series[s.actcode_code] = s.series_id

    all_series_ids = list(actcode_to_series.values())

    # Batch query 2: Get current year values
    current_values = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        current_values = {d.series_id: d.value for d in data_rows}

    # Batch query 3: Get previous year values
    prev_values = {}
    if all_series_ids:
        prev_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year - 1,
                TUData.period == 'A01'
            ))
        ).all()
        prev_values = {d.series_id: d.value for d in prev_rows}

    # Build response from cached data
    activities_data = []
    for act in sub_activities:
        series_id = actcode_to_series.get(act.actcode_code)
        value = current_values.get(series_id) if series_id else None
        prev_value = prev_values.get(series_id) if series_id else None

        yoy = None
        if value is not None and prev_value is not None:
            yoy = decimal_to_float(value) - decimal_to_float(prev_value)

        activities_data.append(TUActivityMetric(
            actcode_code=act.actcode_code,
            actcode_text=act.actcode_text,
            display_level=act.display_level,
            avg_hours_per_day=decimal_to_float(value),
            yoy_change_hours=yoy,
            latest_year=year
        ))

    return TUActivityAnalysisResponse(
        parent_activity_code=actcode_code,
        parent_activity_name=parent,
        activities=activities_data,
        total_count=len(activities_data),
        latest_year=year
    )


@router.get("/activity/{actcode_code}/timeline", response_model=TUActivityTimelineResponse)
async def get_activity_timeline(
    actcode_code: str,
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type: avg_hours, participation"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data for an activity"""
    # Map stattype to code
    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION
    elif stattype == "avg_hours_participants":
        stattype_code = STAT_HOURS_PARTICIPANTS

    # Get year range
    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Find series
    series_id = db.execute(
        select(TUSeries.series_id)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
        .limit(1)
    ).scalar()

    if not series_id:
        raise HTTPException(status_code=404, detail=f"No data found for activity {actcode_code}")

    # Get data
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id == series_id,
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    timeline = [
        TUActivityTimelinePoint(
            year=d.year,
            period=d.period,
            period_name=str(d.year),
            activities={actcode_code: decimal_to_float(d.value)}
        )
        for d in data_rows
    ]

    return TUActivityTimelineResponse(
        stattype=stattype,
        timeline=timeline,
        activity_names={actcode_code: activity_name or actcode_code}
    )


# ============================================================================
# DEMOGRAPHICS ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/demographics/sex", response_model=TUSexComparisonResponse)
async def get_sex_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use between sexes for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get sex categories
    sexes = db.execute(
        select(TUSex)
        .where(TUSex.selectable == 'T')
        .order_by(TUSex.sort_sequence)
    ).scalars().all()

    sex_codes = [s.sex_code for s in sexes]

    # Batch query 1: Find all series for these sex codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.sex_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.sex_code.in_(sex_codes),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    sex_to_series = {}
    for s in series_query:
        if s.sex_code not in sex_to_series:
            sex_to_series[s.sex_code] = s.series_id

    all_series_ids = list(sex_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    comparisons = []
    for sex in sexes:
        series_id = sex_to_series.get(sex.sex_code)
        value = values_map.get(series_id) if series_id else None

        comparisons.append(TUSexComparison(
            sex_code=sex.sex_code,
            sex_text=sex.sex_text,
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TUSexComparisonResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        comparisons=comparisons,
        latest_year=year
    )


@router.get("/demographics/sex/bulk", response_model=TUSexBulkResponse)
async def get_sex_comparison_bulk(
    actcode_codes: str = Query(..., description="Comma-separated activity codes"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Get sex comparison data for multiple activities in a single request.
    OPTIMIZED: Fetches all data in batch queries instead of multiple HTTP requests.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    act_codes = [c.strip() for c in actcode_codes.split(',') if c.strip()]

    # Batch query 1: Get all activity names
    act_names = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(act_codes))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in act_names}

    # Batch query 2: Get sex categories
    sexes = db.execute(
        select(TUSex)
        .where(TUSex.selectable == 'T')
        .order_by(TUSex.sort_sequence)
    ).scalars().all()
    sex_codes = [s.sex_code for s in sexes]

    # Batch query 3: Find ALL series for ALL activities and sex codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code, TUSeries.sex_code)
        .where(and_(
            TUSeries.actcode_code.in_(act_codes),
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.sex_code.in_(sex_codes),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    # Build (actcode, sex_code) -> series_id map
    series_map = {}
    all_series_ids = []
    for s in series_query:
        key = (s.actcode_code, s.sex_code)
        if key not in series_map:
            series_map[key] = s.series_id
            all_series_ids.append(s.series_id)

    # Batch query 4: Get values for ALL series at once
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response for each activity
    activities_data = {}
    for act_code in act_codes:
        comparisons = []
        for sex in sexes:
            series_id = series_map.get((act_code, sex.sex_code))
            value = values_map.get(series_id) if series_id else None
            comparisons.append(TUSexComparison(
                sex_code=sex.sex_code,
                sex_text=sex.sex_text,
                avg_hours_per_day=decimal_to_float(value)
            ))
        activities_data[act_code] = TUSexComparisonResponse(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            comparisons=comparisons,
            latest_year=year
        )

    return TUSexBulkResponse(
        latest_year=year,
        activities=activities_data
    )


@router.get("/demographics/sex/timeline", response_model=TUSexTimelineResponse)
async def get_sex_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing sexes"""
    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Find series for male and female
    male_series = db.execute(
        select(TUSeries.series_id)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.sex_code == SEX_MALE,  # Male
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
        .limit(1)
    ).scalar()

    female_series = db.execute(
        select(TUSeries.series_id)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.sex_code == SEX_FEMALE,  # Female
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
        .limit(1)
    ).scalar()

    # Get data
    series_ids = [s for s in [male_series, female_series] if s]
    if not series_ids:
        raise HTTPException(status_code=404, detail="No data found")

    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(series_ids),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        if d.series_id == male_series:
            year_data[d.year]['male'] = decimal_to_float(d.value)
        elif d.series_id == female_series:
            year_data[d.year]['female'] = decimal_to_float(d.value)

    timeline = [
        TUSexTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            male=year_data.get(year, {}).get('male'),
            female=year_data.get(year, {}).get('female')
        )
        for year in sorted(year_data.keys())
    ]

    return TUSexTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline
    )


@router.get("/demographics/age", response_model=TUAgeComparisonResponse)
async def get_age_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use across age groups for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get age groups
    ages = db.execute(
        select(TUAge)
        .where(and_(TUAge.selectable == 'T', TUAge.display_level <= 1))
        .order_by(TUAge.sort_sequence)
    ).scalars().all()

    age_codes = [a.age_code for a in ages]

    # Batch query 1: Find all series for these age codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.age_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.age_code.in_(age_codes),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    age_to_series = {}
    for s in series_query:
        if s.age_code not in age_to_series:
            age_to_series[s.age_code] = s.series_id

    all_series_ids = list(age_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    comparisons = []
    for age in ages:
        series_id = age_to_series.get(age.age_code)
        value = values_map.get(series_id) if series_id else None

        comparisons.append(TUAgeComparison(
            age_code=age.age_code,
            age_text=age.age_text,
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TUAgeComparisonResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        comparisons=comparisons,
        latest_year=year
    )


@router.get("/demographics/age/timeline", response_model=TUAgeTimelineResponse)
async def get_age_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    age_codes: str = Query(..., description="Comma-separated age codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing age groups"""
    age_list = [a.strip() for a in age_codes.split(',')]

    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get age names
    age_names = {}
    ages = db.execute(
        select(TUAge.age_code, TUAge.age_text)
        .where(TUAge.age_code.in_(age_list))
    ).all()
    age_names = {a.age_code: a.age_text for a in ages}

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query: Find all series for these age codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.age_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.age_code.in_(age_list),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    series_to_age = {}
    for s in series_query:
        if s.age_code not in series_to_age:
            series_to_age[s.series_id] = s.age_code

    if not series_to_age:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(list(series_to_age.keys())),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        age_code = series_to_age.get(d.series_id)
        if age_code:
            year_data[d.year][age_code] = decimal_to_float(d.value)

    timeline = [
        TUAgeTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            ages={age: year_data.get(year, {}).get(age) for age in age_list}
        )
        for year in sorted(year_data.keys())
    ]

    return TUAgeTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline,
        age_names=age_names
    )


@router.get("/demographics/age/bulk", response_model=TUAgeBulkResponse)
async def get_age_comparison_bulk(
    actcode_codes: str = Query(..., description="Comma-separated activity codes"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Get age comparison data for multiple activities in a single request.
    OPTIMIZED: Fetches all data in batch queries instead of multiple HTTP requests.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    act_codes = [c.strip() for c in actcode_codes.split(',') if c.strip()]

    # Batch query 1: Get all activity names
    act_names = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(act_codes))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in act_names}

    # Batch query 2: Get age groups
    ages = db.execute(
        select(TUAge)
        .where(and_(TUAge.selectable == 'T', TUAge.display_level <= 1))
        .order_by(TUAge.sort_sequence)
    ).scalars().all()
    age_codes = [a.age_code for a in ages]

    # Batch query 3: Find ALL series for ALL activities and age codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code, TUSeries.age_code)
        .where(and_(
            TUSeries.actcode_code.in_(act_codes),
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.age_code.in_(age_codes),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    # Build (actcode, age_code) -> series_id map
    series_map = {}
    all_series_ids = []
    for s in series_query:
        key = (s.actcode_code, s.age_code)
        if key not in series_map:
            series_map[key] = s.series_id
            all_series_ids.append(s.series_id)

    # Batch query 4: Get values for ALL series at once
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response for each activity
    activities_data = {}
    for act_code in act_codes:
        comparisons = []
        for age in ages:
            series_id = series_map.get((act_code, age.age_code))
            value = values_map.get(series_id) if series_id else None
            comparisons.append(TUAgeComparison(
                age_code=age.age_code,
                age_text=age.age_text,
                avg_hours_per_day=decimal_to_float(value)
            ))
        activities_data[act_code] = TUAgeComparisonResponse(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            comparisons=comparisons,
            latest_year=year
        )

    return TUAgeBulkResponse(
        latest_year=year,
        age_groups=[TUAgeItem(age_code=a.age_code, age_text=a.age_text) for a in ages],
        activities=activities_data
    )


@router.get("/demographics/labor-force", response_model=TULaborForceComparisonResponse)
async def get_labor_force_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use by labor force status for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get labor force statuses
    statuses = db.execute(
        select(TULaborForceStatus)
        .where(TULaborForceStatus.selectable == 'T')
        .order_by(TULaborForceStatus.sort_sequence)
    ).scalars().all()

    lfstat_codes = [s.lfstat_code for s in statuses]

    # Batch query 1: Find all series for these labor force codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.lfstat_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.lfstat_code.in_(lfstat_codes),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    lfstat_to_series = {}
    for s in series_query:
        if s.lfstat_code not in lfstat_to_series:
            lfstat_to_series[s.lfstat_code] = s.series_id

    all_series_ids = list(lfstat_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    comparisons = []
    for status in statuses:
        series_id = lfstat_to_series.get(status.lfstat_code)
        value = values_map.get(series_id) if series_id else None

        comparisons.append(TULaborForceComparison(
            lfstat_code=status.lfstat_code,
            lfstat_text=status.lfstat_text,
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TULaborForceComparisonResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        comparisons=comparisons,
        latest_year=year
    )


@router.get("/demographics/labor-force/timeline", response_model=TULaborForceTimelineResponse)
async def get_labor_force_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    lfstat_codes: str = Query(..., description="Comma-separated labor force status codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing labor force statuses"""
    lfstat_list = [lf.strip() for lf in lfstat_codes.split(',')]

    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get labor force status names
    lfstat_names = {}
    statuses = db.execute(
        select(TULaborForceStatus.lfstat_code, TULaborForceStatus.lfstat_text)
        .where(TULaborForceStatus.lfstat_code.in_(lfstat_list))
    ).all()
    lfstat_names = {s.lfstat_code: s.lfstat_text for s in statuses}

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query: Find all series for these labor force status codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.lfstat_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.lfstat_code.in_(lfstat_list),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    series_to_lfstat = {}
    for s in series_query:
        if s.lfstat_code not in series_to_lfstat:
            series_to_lfstat[s.series_id] = s.lfstat_code

    if not series_to_lfstat:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(list(series_to_lfstat.keys())),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        lfstat_code = series_to_lfstat.get(d.series_id)
        if lfstat_code:
            year_data[d.year][lfstat_code] = decimal_to_float(d.value)

    timeline = [
        TULaborForceTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            statuses={lf: year_data.get(year, {}).get(lf) for lf in lfstat_list}
        )
        for year in sorted(year_data.keys())
    ]

    return TULaborForceTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline,
        status_names=lfstat_names
    )


@router.get("/demographics/labor-force/bulk", response_model=TULaborForceBulkResponse)
async def get_labor_force_comparison_bulk(
    actcode_codes: str = Query(..., description="Comma-separated activity codes"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Get labor force comparison data for multiple activities in a single request.
    OPTIMIZED: Fetches all data in batch queries instead of multiple HTTP requests.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    act_codes = [c.strip() for c in actcode_codes.split(',') if c.strip()]

    # Batch query 1: Get all activity names
    act_names = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(act_codes))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in act_names}

    # Batch query 2: Get labor force statuses
    statuses = db.execute(
        select(TULaborForceStatus)
        .where(TULaborForceStatus.selectable == 'T')
        .order_by(TULaborForceStatus.sort_sequence)
    ).scalars().all()
    lfstat_codes = [s.lfstat_code for s in statuses]

    # Batch query 3: Find ALL series for ALL activities and labor force codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code, TUSeries.lfstat_code)
        .where(and_(
            TUSeries.actcode_code.in_(act_codes),
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.lfstat_code.in_(lfstat_codes),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    # Build (actcode, lfstat_code) -> series_id map
    series_map = {}
    all_series_ids = []
    for s in series_query:
        key = (s.actcode_code, s.lfstat_code)
        if key not in series_map:
            series_map[key] = s.series_id
            all_series_ids.append(s.series_id)

    # Batch query 4: Get values for ALL series at once
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response for each activity
    activities_data = {}
    for act_code in act_codes:
        comparisons = []
        for status in statuses:
            series_id = series_map.get((act_code, status.lfstat_code))
            value = values_map.get(series_id) if series_id else None
            comparisons.append(TULaborForceComparison(
                lfstat_code=status.lfstat_code,
                lfstat_text=status.lfstat_text,
                avg_hours_per_day=decimal_to_float(value)
            ))
        activities_data[act_code] = TULaborForceComparisonResponse(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            comparisons=comparisons,
            latest_year=year
        )

    return TULaborForceBulkResponse(
        latest_year=year,
        labor_force_statuses=[TULaborForceStatusItem(lfstat_code=s.lfstat_code, lfstat_text=s.lfstat_text) for s in statuses],
        activities=activities_data
    )


# ============================================================================
# EDUCATION COMPARISON ENDPOINTS
# ============================================================================

@router.get("/demographics/education", response_model=TUEducationComparisonResponse)
async def get_education_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use by education level for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get education levels
    educations = db.execute(
        select(TUEducation)
        .where(TUEducation.selectable == 'T')
        .order_by(TUEducation.sort_sequence)
    ).scalars().all()

    educ_codes = [e.educ_code for e in educations]

    # Education data has different age filters:
    # - educ_code='00' (All education) uses age_code='000' (All ages)
    # - Specific education levels use age_code='028' (25 years and over)

    educ_to_series = {}

    # Query 1: Get "All education levels" (educ_code='00') with age_code='000'
    if '00' in educ_codes:
        all_educ_series = db.execute(
            select(TUSeries.series_id)
            .where(and_(
                TUSeries.actcode_code == actcode_code,
                TUSeries.stattype_code == STAT_HOURS_PER_DAY,
                TUSeries.educ_code == '00',
                TUSeries.age_code == AGE_ALL,
                or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
            ))
            .limit(1)
        ).scalar()
        if all_educ_series:
            educ_to_series['00'] = all_educ_series

    # Query 2: Get specific education levels with age_code='028' (25 years and over)
    specific_educ_codes = [e for e in educ_codes if e != '00']
    if specific_educ_codes:
        series_query = db.execute(
            select(TUSeries.series_id, TUSeries.educ_code)
            .where(and_(
                TUSeries.actcode_code == actcode_code,
                TUSeries.stattype_code == STAT_HOURS_PER_DAY,
                TUSeries.educ_code.in_(specific_educ_codes),
                TUSeries.age_code == AGE_25_AND_OVER,
                or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
            ))
        ).all()
        for s in series_query:
            if s.educ_code not in educ_to_series:
                educ_to_series[s.educ_code] = s.series_id

    all_series_ids = list(educ_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    comparisons = []
    for educ in educations:
        series_id = educ_to_series.get(educ.educ_code)
        value = values_map.get(series_id) if series_id else None

        comparisons.append(TUEducationComparison(
            educ_code=educ.educ_code,
            educ_text=educ.educ_text,
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TUEducationComparisonResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        comparisons=comparisons,
        latest_year=year
    )


@router.get("/demographics/education/timeline", response_model=TUEducationTimelineResponse)
async def get_education_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    educ_codes: str = Query(..., description="Comma-separated education codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing education levels"""
    educ_list = [e.strip() for e in educ_codes.split(',')]

    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get education names
    education_names = {}
    educs = db.execute(
        select(TUEducation.educ_code, TUEducation.educ_text)
        .where(TUEducation.educ_code.in_(educ_list))
    ).all()
    education_names = {e.educ_code: e.educ_text for e in educs}

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query: Find series for education levels
    # Education data has different age filters:
    # - educ_code='00' (All education) uses age_code='000' (All ages)
    # - Specific education levels use age_code='028' (25 years and over)
    # Split into two groups for batch querying
    educ_all = [e for e in educ_list if e == '00']
    educ_specific = [e for e in educ_list if e != '00']

    series_to_educ = {}

    # Batch query for "All education" (age_code='000')
    if educ_all:
        series_query = db.execute(
            select(TUSeries.series_id, TUSeries.educ_code)
            .where(and_(
                TUSeries.actcode_code == actcode_code,
                TUSeries.stattype_code == stattype_code,
                TUSeries.educ_code.in_(educ_all),
                TUSeries.age_code == AGE_ALL,
                or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
            ))
        ).all()
        for s in series_query:
            if s.educ_code not in [series_to_educ.get(sid) for sid in series_to_educ]:
                series_to_educ[s.series_id] = s.educ_code

    # Batch query for specific education levels (age_code='028')
    if educ_specific:
        series_query = db.execute(
            select(TUSeries.series_id, TUSeries.educ_code)
            .where(and_(
                TUSeries.actcode_code == actcode_code,
                TUSeries.stattype_code == stattype_code,
                TUSeries.educ_code.in_(educ_specific),
                TUSeries.age_code == AGE_25_AND_OVER,
                or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
            ))
        ).all()
        for s in series_query:
            if s.educ_code not in [series_to_educ.get(sid) for sid in series_to_educ]:
                series_to_educ[s.series_id] = s.educ_code

    if not series_to_educ:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(list(series_to_educ.keys())),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        educ_code = series_to_educ.get(d.series_id)
        if educ_code:
            year_data[d.year][educ_code] = decimal_to_float(d.value)

    timeline = [
        TUEducationTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            educations={educ: year_data.get(year, {}).get(educ) for educ in educ_list}
        )
        for year in sorted(year_data.keys())
    ]

    return TUEducationTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline,
        education_names=education_names
    )


# ============================================================================
# RACE COMPARISON ENDPOINTS
# ============================================================================

@router.get("/demographics/race", response_model=TURaceComparisonResponse)
async def get_race_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use by race for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get races
    races = db.execute(
        select(TURace)
        .where(TURace.selectable == 'T')
        .order_by(TURace.sort_sequence)
    ).scalars().all()

    race_codes = [r.race_code for r in races]

    # Batch query 1: Find all series for these race codes at once
    # Note: Don't filter by sex_code - race breakdown already implies aggregation across sexes
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.race_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.race_code.in_(race_codes),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    race_to_series = {}
    for s in series_query:
        if s.race_code not in race_to_series:
            race_to_series[s.race_code] = s.series_id

    all_series_ids = list(race_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    comparisons = []
    for race in races:
        series_id = race_to_series.get(race.race_code)
        value = values_map.get(series_id) if series_id else None

        comparisons.append(TURaceComparison(
            race_code=race.race_code,
            race_text=race.race_text,
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TURaceComparisonResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        comparisons=comparisons,
        latest_year=year
    )


@router.get("/demographics/race/timeline", response_model=TURaceTimelineResponse)
async def get_race_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    race_codes: str = Query(..., description="Comma-separated race codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing races"""
    race_list = [r.strip() for r in race_codes.split(',')]

    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get race names
    race_names = {}
    races_data = db.execute(
        select(TURace.race_code, TURace.race_text)
        .where(TURace.race_code.in_(race_list))
    ).all()
    race_names = {r.race_code: r.race_text for r in races_data}

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query: Find all series for these race codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.race_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.race_code.in_(race_list),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    series_to_race = {}
    for s in series_query:
        if s.race_code not in series_to_race:
            series_to_race[s.series_id] = s.race_code

    if not series_to_race:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(list(series_to_race.keys())),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        race_code = series_to_race.get(d.series_id)
        if race_code:
            year_data[d.year][race_code] = decimal_to_float(d.value)

    timeline = [
        TURaceTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            races={race: year_data.get(year, {}).get(race) for race in race_list}
        )
        for year in sorted(year_data.keys())
    ]

    return TURaceTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline,
        race_names=race_names
    )


# ============================================================================
# DAY TYPE COMPARISON ENDPOINTS
# ============================================================================

# Day type codes (pertype_code) - based on actual BLS ATUS data
# 00 = All days, 16 = Weekends and holidays, 19 = Nonholiday weekdays
PERTYPE_WEEKDAY = '19'  # Nonholiday weekdays (most data available)
PERTYPE_WEEKEND = '16'  # Weekends and holidays
DAY_TYPE_CODES = [PERTYPE_ALL_DAYS, PERTYPE_WEEKDAY, PERTYPE_WEEKEND]
DAY_TYPE_NAMES = {
    PERTYPE_ALL_DAYS: 'All Days',
    PERTYPE_WEEKDAY: 'Weekday',
    PERTYPE_WEEKEND: 'Weekend/Holiday'
}


@router.get("/demographics/day-type", response_model=TUDayTypeComparisonResponse)
async def get_day_type_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use by day type (weekday vs weekend) for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query 1: Find all series for these day type codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.pertype_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.pertype_code.in_(DAY_TYPE_CODES),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
        ))
    ).all()

    pertype_to_series = {}
    for s in series_query:
        if s.pertype_code not in pertype_to_series:
            pertype_to_series[s.pertype_code] = s.series_id

    all_series_ids = list(pertype_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    comparisons = []
    for pertype_code in DAY_TYPE_CODES:
        series_id = pertype_to_series.get(pertype_code)
        value = values_map.get(series_id) if series_id else None

        comparisons.append(TUDayTypeComparison(
            pertype_code=pertype_code,
            pertype_text=DAY_TYPE_NAMES.get(pertype_code, pertype_code),
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TUDayTypeComparisonResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        comparisons=comparisons,
        latest_year=year
    )


@router.get("/demographics/day-type/timeline", response_model=TUDayTypeTimelineResponse)
async def get_day_type_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    pertype_codes: str = Query(..., description="Comma-separated day type codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing day types (weekday vs weekend)"""
    pertype_list = [p.strip() for p in pertype_codes.split(',')]

    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query: Find all series for these day type codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.pertype_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.pertype_code.in_(pertype_list),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
        ))
    ).all()

    series_to_pertype = {}
    for s in series_query:
        if s.pertype_code not in series_to_pertype:
            series_to_pertype[s.series_id] = s.pertype_code

    if not series_to_pertype:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(list(series_to_pertype.keys())),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        pertype_code = series_to_pertype.get(d.series_id)
        if pertype_code:
            year_data[d.year][pertype_code] = decimal_to_float(d.value)

    timeline = [
        TUDayTypeTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            day_types={pertype: year_data.get(year, {}).get(pertype) for pertype in pertype_list}
        )
        for year in sorted(year_data.keys())
    ]

    return TUDayTypeTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline,
        day_type_names={p: DAY_TYPE_NAMES.get(p, p) for p in pertype_list}
    )


# ============================================================================
# TOP ACTIVITIES ENDPOINT
# ============================================================================

@router.get("/top-activities", response_model=TUTopActivitiesResponse)
async def get_top_activities(
    ranking_type: str = Query("most_time", description="Ranking type: most_time, highest_participation"),
    limit: int = Query(10, le=20),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Get top activities by time spent or participation
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    stattype_code = STAT_HOURS_PER_DAY if ranking_type == "most_time" else STAT_PARTICIPATION

    # Batch query 1: Get activity names
    acts = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(MAJOR_ACTIVITY_CODES))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in acts}

    # Batch query 2: Find all series for major activities at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code)
        .where(and_(
            TUSeries.actcode_code.in_(MAJOR_ACTIVITY_CODES),
            TUSeries.stattype_code == stattype_code,
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    actcode_to_series = {}
    for s in series_query:
        if s.actcode_code not in actcode_to_series:
            actcode_to_series[s.actcode_code] = s.series_id

    all_series_ids = list(actcode_to_series.values())

    # Batch query 3: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build activities with values from cached data
    activities_with_values = []
    for act_code in MAJOR_ACTIVITY_CODES:
        series_id = actcode_to_series.get(act_code)
        if series_id:
            value = values_map.get(series_id)
            if value:
                activities_with_values.append((act_code, decimal_to_float(value)))

    # Sort by value descending
    activities_with_values.sort(key=lambda x: x[1] or 0, reverse=True)

    # Build response
    top_activities = [
        TUTopActivity(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            avg_hours_per_day=value if ranking_type == "most_time" else None,
            participation_rate=value if ranking_type == "highest_participation" else None,
            rank=idx + 1
        )
        for idx, (act_code, value) in enumerate(activities_with_values[:limit])
    ]

    return TUTopActivitiesResponse(
        ranking_type=ranking_type,
        activities=top_activities,
        latest_year=year
    )


# ============================================================================
# YEAR-OVER-YEAR CHANGES ENDPOINT
# ============================================================================

@router.get("/yoy-changes", response_model=TUYoYChangeResponse)
async def get_yoy_changes(
    stattype: str = Query("avg_hours", description="Stat type"),
    limit: int = Query(5, le=10),
    year: Optional[int] = Query(None, description="Year to compare"),
    db: Session = Depends(get_data_db)
):
    """Get year-over-year changes for activities
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    stattype_code = STAT_HOURS_PER_DAY if stattype == "avg_hours" else STAT_PARTICIPATION

    # Batch query 1: Get activity names
    acts = db.execute(
        select(TUActivityCode.actcode_code, TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code.in_(MAJOR_ACTIVITY_CODES))
    ).all()
    activity_names = {a.actcode_code: a.actcode_text for a in acts}

    # Batch query 2: Find all series for major activities at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.actcode_code)
        .where(and_(
            TUSeries.actcode_code.in_(MAJOR_ACTIVITY_CODES),
            TUSeries.stattype_code == stattype_code,
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    actcode_to_series = {}
    for s in series_query:
        if s.actcode_code not in actcode_to_series:
            actcode_to_series[s.actcode_code] = s.series_id

    all_series_ids = list(actcode_to_series.values())

    # Batch query 3: Get current year values
    current_values = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        current_values = {d.series_id: d.value for d in data_rows}

    # Batch query 4: Get previous year values
    prev_values = {}
    if all_series_ids:
        prev_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year - 1,
                TUData.period == 'A01'
            ))
        ).all()
        prev_values = {d.series_id: d.value for d in prev_rows}

    # Build changes from cached data
    changes = []
    for act_code in MAJOR_ACTIVITY_CODES:
        series_id = actcode_to_series.get(act_code)
        if series_id:
            current = current_values.get(series_id)
            prev = prev_values.get(series_id)

            if current and prev:
                curr_val = decimal_to_float(current)
                prev_val = decimal_to_float(prev)
                change = curr_val - prev_val
                pct = (change / prev_val * 100) if prev_val else None
                changes.append((act_code, curr_val, prev_val, change, pct))

    # Sort by change
    changes.sort(key=lambda x: x[3] or 0, reverse=True)

    gainers = [
        TUActivityChange(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            current_value=curr_val,
            prev_value=prev_val,
            change=change,
            change_pct=pct
        )
        for act_code, curr_val, prev_val, change, pct in changes[:limit]
        if change and change > 0
    ]

    losers = [
        TUActivityChange(
            actcode_code=act_code,
            actcode_text=activity_names.get(act_code, act_code),
            current_value=curr_val,
            prev_value=prev_val,
            change=change,
            change_pct=pct
        )
        for act_code, curr_val, prev_val, change, pct in reversed(changes[-limit:])
        if change and change < 0
    ]

    return TUYoYChangeResponse(
        stattype=stattype,
        latest_year=year,
        prev_year=year - 1,
        gainers=gainers,
        losers=losers
    )


# ============================================================================
# REGION ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/regions", response_model=TURegionAnalysisResponse)
async def get_region_comparison(
    actcode_code: str = Query(..., description="Activity code"),
    year: Optional[int] = Query(None, description="Year filter"),
    db: Session = Depends(get_data_db)
):
    """Compare time use across regions for an activity
    OPTIMIZED: Uses batch queries instead of N+1 pattern.
    """
    if not year:
        year = db.execute(select(func.max(TUData.year))).scalar() or 2023

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Get regions
    regions = db.execute(
        select(TURegion)
        .where(TURegion.selectable == 'T')
        .order_by(TURegion.sort_sequence)
    ).scalars().all()

    region_codes = [r.region_code for r in regions]

    # Batch query 1: Find all series for these region codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.region_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == STAT_HOURS_PER_DAY,
            TUSeries.region_code.in_(region_codes),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    region_to_series = {}
    for s in series_query:
        if s.region_code not in region_to_series:
            region_to_series[s.region_code] = s.series_id

    all_series_ids = list(region_to_series.values())

    # Batch query 2: Get values for all series
    values_map = {}
    if all_series_ids:
        data_rows = db.execute(
            select(TUData.series_id, TUData.value)
            .where(and_(
                TUData.series_id.in_(all_series_ids),
                TUData.year == year,
                TUData.period == 'A01'
            ))
        ).all()
        values_map = {d.series_id: d.value for d in data_rows}

    # Build response from cached data
    region_metrics = []
    for region in regions:
        series_id = region_to_series.get(region.region_code)
        value = values_map.get(series_id) if series_id else None

        region_metrics.append(TURegionMetric(
            region_code=region.region_code,
            region_text=region.region_text,
            avg_hours_per_day=decimal_to_float(value)
        ))

    return TURegionAnalysisResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        regions=region_metrics,
        latest_year=year
    )


@router.get("/regions/timeline", response_model=TURegionTimelineResponse)
async def get_region_timeline(
    actcode_code: str = Query(..., description="Activity code"),
    region_codes: str = Query(..., description="Comma-separated region codes"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year"),
    stattype: str = Query("avg_hours", description="Stat type"),
    db: Session = Depends(get_data_db)
):
    """Get timeline data comparing regions"""
    region_list = [r.strip() for r in region_codes.split(',')]

    stattype_code = STAT_HOURS_PER_DAY
    if stattype == "participation":
        stattype_code = STAT_PARTICIPATION

    if not end_year:
        end_year = db.execute(select(func.max(TUData.year))).scalar() or 2023
    if not start_year:
        start_year = end_year - 9

    # Get region names
    region_names = {}
    regions = db.execute(
        select(TURegion.region_code, TURegion.region_text)
        .where(TURegion.region_code.in_(region_list))
    ).all()
    region_names = {r.region_code: r.region_text for r in regions}

    # Get activity name
    activity_name = db.execute(
        select(TUActivityCode.actcode_text)
        .where(TUActivityCode.actcode_code == actcode_code)
    ).scalar()

    # Batch query: Find all series for these region codes at once
    series_query = db.execute(
        select(TUSeries.series_id, TUSeries.region_code)
        .where(and_(
            TUSeries.actcode_code == actcode_code,
            TUSeries.stattype_code == stattype_code,
            TUSeries.region_code.in_(region_list),
            or_(TUSeries.sex_code == SEX_BOTH, TUSeries.sex_code.is_(None)),
            or_(TUSeries.age_code == AGE_ALL, TUSeries.age_code.is_(None)),
            or_(TUSeries.pertype_code == PERTYPE_ALL_DAYS, TUSeries.pertype_code.is_(None)),
        ))
    ).all()

    series_to_region = {}
    for s in series_query:
        if s.region_code not in series_to_region:
            series_to_region[s.series_id] = s.region_code

    if not series_to_region:
        raise HTTPException(status_code=404, detail="No data found")

    # Batch query
    data_rows = db.execute(
        select(TUData)
        .where(and_(
            TUData.series_id.in_(list(series_to_region.keys())),
            TUData.year >= start_year,
            TUData.year <= end_year,
            TUData.period == 'A01'
        ))
        .order_by(TUData.year)
    ).scalars().all()

    # Build timeline
    year_data: Dict[int, Dict[str, float]] = {}
    for d in data_rows:
        if d.year not in year_data:
            year_data[d.year] = {}
        region_code = series_to_region.get(d.series_id)
        if region_code:
            year_data[d.year][region_code] = decimal_to_float(d.value)

    timeline = [
        TURegionTimelinePoint(
            year=year,
            period='A01',
            period_name=str(year),
            regions={reg: year_data.get(year, {}).get(reg) for reg in region_list}
        )
        for year in sorted(year_data.keys())
    ]

    return TURegionTimelineResponse(
        actcode_code=actcode_code,
        actcode_text=activity_name,
        stattype=stattype,
        timeline=timeline,
        region_names=region_names
    )
