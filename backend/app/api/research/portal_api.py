"""
Research Portal API - Comprehensive Data Endpoints

Provides rich, detailed data for the Research portal including:
- BLS: Employment by industry, CPI breakdowns, regional data, labor indicators
- Treasury: Yield curves, auction details, spread analysis
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text, desc
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime, date

from ...database import get_data_db
from ...data_models.treasury_models import TreasuryDailyRate, TreasuryAuction, TreasuryUpcomingAuction
from ...core.cache import cached, DataCategory
print("[PORTAL_API] Cache module imported successfully")  # Debug

router = APIRouter(prefix="/api/research/portal", tags=["Research Portal"])


# ============================================================================
# HELPERS
# ============================================================================

def decimal_to_float(val) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    return val


def get_period_name(period: str) -> str:
    period_map = {
        'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
        'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
        'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
        'M13': 'Annual', 'Q01': 'Q1', 'Q02': 'Q2', 'Q03': 'Q3', 'Q04': 'Q4'
    }
    return period_map.get(period, period)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class IndustryEmployment(BaseModel):
    """Employment data by industry"""
    industry_code: str
    industry_name: str
    employment: Optional[float] = None
    employment_change: Optional[float] = None
    employment_change_pct: Optional[float] = None
    avg_hourly_earnings: Optional[float] = None
    avg_weekly_hours: Optional[float] = None
    period: Optional[str] = None
    year: Optional[int] = None


class CPICategory(BaseModel):
    """CPI data by category"""
    item_code: str
    item_name: str
    index_value: Optional[float] = None
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None
    weight: Optional[float] = None
    period: Optional[str] = None
    year: Optional[int] = None


class RegionalUnemployment(BaseModel):
    """Unemployment by state/region"""
    area_code: str
    area_name: str
    unemployment_rate: Optional[float] = None
    labor_force: Optional[float] = None
    employed: Optional[float] = None
    unemployed: Optional[float] = None
    rate_change: Optional[float] = None
    period: Optional[str] = None
    year: Optional[int] = None


class LaborIndicator(BaseModel):
    """Key labor market indicator"""
    id: str
    name: str
    value: Optional[float] = None
    formatted_value: Optional[str] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    period: Optional[str] = None
    year: Optional[int] = None
    source: Optional[str] = None
    frequency: Optional[str] = None


class TrendPoint(BaseModel):
    """A point in a time series"""
    date: str
    value: float
    period: Optional[str] = None
    year: Optional[int] = None


class SurveyInfo(BaseModel):
    """Survey/dataset information"""
    id: str
    code: str
    name: str
    description: str
    path: str
    category: str
    series_count: Optional[int] = None
    latest_period: Optional[str] = None
    latest_year: Optional[int] = None
    update_frequency: Optional[str] = None


class QuickStudy(BaseModel):
    """Quick study template"""
    id: str
    title: str
    description: str
    available: bool = False


class BLSPortalData(BaseModel):
    """Comprehensive BLS portal data"""
    # Summary indicators
    labor_indicators: List[LaborIndicator]
    # Employment by industry
    employment_by_industry: List[IndustryEmployment]
    # CPI breakdown
    cpi_categories: List[CPICategory]
    # Regional unemployment
    regional_unemployment: List[RegionalUnemployment]
    # Historical trends
    unemployment_trend: List[TrendPoint]
    cpi_trend: List[TrendPoint]
    payrolls_trend: List[TrendPoint]
    # Survey browser
    surveys: List[SurveyInfo]
    # Quick studies
    quick_studies: List[QuickStudy]
    # Meta
    last_updated: Optional[str] = None


class YieldCurvePoint(BaseModel):
    """A point on the yield curve"""
    maturity: str
    maturity_months: int
    yield_value: Optional[float] = None
    change_1d: Optional[float] = None
    change_1w: Optional[float] = None
    change_1m: Optional[float] = None


class AuctionResult(BaseModel):
    """Treasury auction result"""
    security_type: str
    security_term: str
    auction_date: str
    issue_date: Optional[str] = None
    maturity_date: Optional[str] = None
    high_yield: Optional[float] = None
    high_price: Optional[float] = None
    bid_to_cover: Optional[float] = None
    primary_dealer_pct: Optional[float] = None
    direct_bidder_pct: Optional[float] = None
    indirect_bidder_pct: Optional[float] = None
    total_accepted: Optional[float] = None
    total_tendered: Optional[float] = None
    tail: Optional[float] = None
    cusip: Optional[str] = None


class SpreadData(BaseModel):
    """Yield spread data"""
    name: str
    spread_bps: Optional[float] = None
    change_1d: Optional[float] = None
    change_1w: Optional[float] = None


class UpcomingAuctionData(BaseModel):
    """Upcoming Treasury auction"""
    security_type: str
    security_term: str
    announcement_date: Optional[str] = None
    auction_date: str
    issue_date: Optional[str] = None
    offering_amount: Optional[float] = None


class TreasuryPortalData(BaseModel):
    """Comprehensive Treasury portal data"""
    yield_curve: List[YieldCurvePoint]
    yield_trend_10y: List[TrendPoint]
    yield_trend_2y: List[TrendPoint]
    spreads: List[SpreadData]
    recent_auctions: List[AuctionResult]
    upcoming_auctions: List[UpcomingAuctionData]
    quick_studies: List[QuickStudy]
    last_updated: Optional[str] = None


# ============================================================================
# BLS COMPREHENSIVE ENDPOINT
# ============================================================================

@router.get("/bls/comprehensive", response_model=BLSPortalData)
@cached("portal:bls:comprehensive", category=DataCategory.BLS_MONTHLY)
async def get_bls_comprehensive(db: Session = Depends(get_data_db)):
    """Get comprehensive BLS portal data (cached for 24h)"""
    print("[BLS_COMPREHENSIVE] Function called - DB queries starting...")  # Debug

    labor_indicators = []

    # --- LABOR INDICATORS ---

    # 1. Unemployment Rate
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_ln_data
                WHERE series_id = 'LNS14000000' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            previous AS (
                SELECT value FROM bls_ln_data
                WHERE series_id = 'LNS14000000' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1 OFFSET 1
            )
            SELECT c.value, c.year, c.period, p.value as prev
            FROM current c, previous p
        """)).fetchone()
        if result:
            change = decimal_to_float(result[0]) - decimal_to_float(result[3]) if result[3] else None
            labor_indicators.append(LaborIndicator(
                id="unemployment_rate", name="Unemployment Rate",
                value=decimal_to_float(result[0]), formatted_value=f"{result[0]}%",
                change=round(change, 2) if change else None,
                period=get_period_name(result[2]), year=result[1],
                source="LN", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 2. Labor Force Participation Rate
    try:
        result = db.execute(text("""
            SELECT value, year, period FROM bls_ln_data
            WHERE series_id = 'LNS11300000' AND period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 1
        """)).fetchone()
        if result:
            labor_indicators.append(LaborIndicator(
                id="lfpr", name="Labor Force Participation Rate",
                value=decimal_to_float(result[0]), formatted_value=f"{result[0]}%",
                period=get_period_name(result[2]), year=result[1],
                source="LN", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 3. Total Nonfarm Payrolls
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_ce_data
                WHERE series_id = 'CES0000000001' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            previous AS (
                SELECT value FROM bls_ce_data
                WHERE series_id = 'CES0000000001' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1 OFFSET 1
            )
            SELECT c.value, c.year, c.period, p.value as prev
            FROM current c, previous p
        """)).fetchone()
        if result:
            change = decimal_to_float(result[0]) - decimal_to_float(result[3]) if result[3] else None
            labor_indicators.append(LaborIndicator(
                id="nonfarm_payrolls", name="Total Nonfarm Payrolls",
                value=decimal_to_float(result[0]), formatted_value=f"{result[0]/1000:.1f}M",
                change=round(change, 0) if change else None,
                period=get_period_name(result[2]), year=result[1],
                source="CE", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 4. Job Openings
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_jt_data
                WHERE series_id = 'JTS000000000000000JOL' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            previous AS (
                SELECT value FROM bls_jt_data
                WHERE series_id = 'JTS000000000000000JOL' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1 OFFSET 1
            )
            SELECT c.value, c.year, c.period, p.value as prev
            FROM current c, previous p
        """)).fetchone()
        if result:
            change = decimal_to_float(result[0]) - decimal_to_float(result[3]) if result[3] else None
            labor_indicators.append(LaborIndicator(
                id="job_openings", name="Job Openings (JOLTS)",
                value=decimal_to_float(result[0]), formatted_value=f"{result[0]/1000:.1f}M",
                change=round(change, 0) if change else None,
                period=get_period_name(result[2]), year=result[1],
                source="JT", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 5. Quits Rate
    try:
        result = db.execute(text("""
            SELECT value, year, period FROM bls_jt_data
            WHERE series_id = 'JTS000000000000000QUR' AND period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 1
        """)).fetchone()
        if result:
            labor_indicators.append(LaborIndicator(
                id="quits_rate", name="Quits Rate",
                value=decimal_to_float(result[0]), formatted_value=f"{result[0]}%",
                period=get_period_name(result[2]), year=result[1],
                source="JT", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 6. Average Hourly Earnings
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_ce_data
                WHERE series_id = 'CES0500000003' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            year_ago AS (
                SELECT value FROM bls_ce_data
                WHERE series_id = 'CES0500000003'
                AND (year, period) = (
                    SELECT year - 1, period FROM bls_ce_data
                    WHERE series_id = 'CES0500000003' AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1
                )
            )
            SELECT c.value, c.year, c.period, y.value as year_ago
            FROM current c LEFT JOIN year_ago y ON true
        """)).fetchone()
        if result:
            yoy = round(((decimal_to_float(result[0]) - decimal_to_float(result[3])) / decimal_to_float(result[3])) * 100, 1) if result[3] else None
            labor_indicators.append(LaborIndicator(
                id="avg_hourly_earnings", name="Avg Hourly Earnings (YoY)",
                value=decimal_to_float(result[0]), formatted_value=f"${result[0]:.2f}",
                change_pct=yoy,
                period=get_period_name(result[2]), year=result[1],
                source="CE", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 7. CPI All Items YoY
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_cu_data
                WHERE series_id = 'CUSR0000SA0' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            year_ago AS (
                SELECT value FROM bls_cu_data d
                WHERE series_id = 'CUSR0000SA0'
                AND year = (SELECT year - 1 FROM current)
                AND period = (SELECT period FROM current)
            )
            SELECT c.value, c.year, c.period, y.value as year_ago
            FROM current c, year_ago y
        """)).fetchone()
        if result and result[3]:
            yoy = round(((decimal_to_float(result[0]) - decimal_to_float(result[3])) / decimal_to_float(result[3])) * 100, 1)
            labor_indicators.append(LaborIndicator(
                id="cpi_yoy", name="CPI All Items (YoY)",
                value=yoy, formatted_value=f"{yoy}%",
                period=get_period_name(result[2]), year=result[1],
                source="CU", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 8. CPI Core YoY
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_cu_data
                WHERE series_id = 'CUSR0000SA0L1E' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            year_ago AS (
                SELECT value FROM bls_cu_data
                WHERE series_id = 'CUSR0000SA0L1E'
                AND year = (SELECT year - 1 FROM current)
                AND period = (SELECT period FROM current)
            )
            SELECT c.value, c.year, c.period, y.value as year_ago
            FROM current c, year_ago y
        """)).fetchone()
        if result and result[3]:
            yoy = round(((decimal_to_float(result[0]) - decimal_to_float(result[3])) / decimal_to_float(result[3])) * 100, 1)
            labor_indicators.append(LaborIndicator(
                id="cpi_core_yoy", name="CPI Core (YoY)",
                value=yoy, formatted_value=f"{yoy}%",
                period=get_period_name(result[2]), year=result[1],
                source="CU", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 9. PPI Final Demand YoY
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_wp_data
                WHERE series_id = 'WPSFD4' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            year_ago AS (
                SELECT value FROM bls_wp_data
                WHERE series_id = 'WPSFD4'
                AND year = (SELECT year - 1 FROM current)
                AND period = (SELECT period FROM current)
            )
            SELECT c.value, c.year, c.period, y.value as year_ago
            FROM current c, year_ago y
        """)).fetchone()
        if result and result[3]:
            yoy = round(((decimal_to_float(result[0]) - decimal_to_float(result[3])) / decimal_to_float(result[3])) * 100, 1)
            labor_indicators.append(LaborIndicator(
                id="ppi_yoy", name="PPI Final Demand (YoY)",
                value=yoy, formatted_value=f"{yoy}%",
                period=get_period_name(result[2]), year=result[1],
                source="WP", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # 10. Import Price Index YoY
    try:
        result = db.execute(text("""
            WITH current AS (
                SELECT value, year, period FROM bls_ei_data
                WHERE series_id = 'EIUIR' AND period != 'M13'
                ORDER BY year DESC, period DESC LIMIT 1
            ),
            year_ago AS (
                SELECT value FROM bls_ei_data
                WHERE series_id = 'EIUIR'
                AND year = (SELECT year - 1 FROM current)
                AND period = (SELECT period FROM current)
            )
            SELECT c.value, c.year, c.period, y.value as year_ago
            FROM current c, year_ago y
        """)).fetchone()
        if result and result[3]:
            yoy = round(((decimal_to_float(result[0]) - decimal_to_float(result[3])) / decimal_to_float(result[3])) * 100, 1)
            labor_indicators.append(LaborIndicator(
                id="import_prices_yoy", name="Import Prices (YoY)",
                value=yoy, formatted_value=f"{yoy}%",
                period=get_period_name(result[2]), year=result[1],
                source="EI", frequency="Monthly"
            ))
    except Exception as e:
        print(f"Error: {e}")

    # --- EMPLOYMENT BY INDUSTRY (Top supersectors) ---
    employment_by_industry = []
    supersectors = [
        ("CES0500000001", "CES0500000003", "CES0500000002", "Total Private"),
        ("CES1000000001", "CES1000000003", "CES1000000002", "Mining and Logging"),
        ("CES2000000001", "CES2000000003", "CES2000000002", "Construction"),
        ("CES3000000001", "CES3000000003", "CES3000000002", "Manufacturing"),
        ("CES4000000001", "CES4000000003", "CES4000000002", "Trade, Transportation, Utilities"),
        ("CES5000000001", "CES5000000003", "CES5000000002", "Information"),
        ("CES5500000001", "CES5500000003", "CES5500000002", "Financial Activities"),
        ("CES6000000001", "CES6000000003", "CES6000000002", "Professional & Business Services"),
        ("CES6500000001", "CES6500000003", "CES6500000002", "Education & Health Services"),
        ("CES7000000001", "CES7000000003", "CES7000000002", "Leisure & Hospitality"),
        ("CES8000000001", "CES8000000003", "CES8000000002", "Other Services"),
        ("CES9000000001", "CES9000000003", "CES9000000002", "Government"),
    ]

    for emp_id, earnings_id, hours_id, name in supersectors:
        try:
            result = db.execute(text("""
                WITH current AS (
                    SELECT value, year, period FROM bls_ce_data
                    WHERE series_id = :emp_id AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1
                ),
                previous AS (
                    SELECT value FROM bls_ce_data
                    WHERE series_id = :emp_id AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1 OFFSET 1
                ),
                earnings AS (
                    SELECT value FROM bls_ce_data
                    WHERE series_id = :earnings_id AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1
                ),
                hours AS (
                    SELECT value FROM bls_ce_data
                    WHERE series_id = :hours_id AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1
                )
                SELECT c.value, c.year, c.period, p.value, e.value, h.value
                FROM current c
                LEFT JOIN previous p ON true
                LEFT JOIN earnings e ON true
                LEFT JOIN hours h ON true
            """), {"emp_id": emp_id, "earnings_id": earnings_id, "hours_id": hours_id}).fetchone()

            if result and result[0]:
                change = decimal_to_float(result[0]) - decimal_to_float(result[3]) if result[3] else None
                change_pct = round((change / decimal_to_float(result[3])) * 100, 2) if change and result[3] else None
                employment_by_industry.append(IndustryEmployment(
                    industry_code=emp_id[:6],
                    industry_name=name,
                    employment=decimal_to_float(result[0]),
                    employment_change=round(change, 1) if change else None,
                    employment_change_pct=change_pct,
                    avg_hourly_earnings=decimal_to_float(result[4]),
                    avg_weekly_hours=decimal_to_float(result[5]),
                    period=get_period_name(result[2]),
                    year=result[1]
                ))
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    # --- CPI CATEGORIES ---
    cpi_categories = []
    cpi_items = [
        ("CUSR0000SA0", "All Items"),
        ("CUSR0000SA0L1E", "All Items Less Food and Energy"),
        ("CUSR0000SAF1", "Food"),
        ("CUSR0000SAH1", "Shelter"),
        ("CUSR0000SETA01", "New Vehicles"),
        ("CUSR0000SETA02", "Used Cars and Trucks"),
        ("CUSR0000SAM", "Medical Care"),
        ("CUSR0000SAA", "Apparel"),
        ("CUSR0000SETB01", "Gasoline"),
        ("CUSR0000SEHF01", "Electricity"),
        ("CUSR0000SEHF02", "Utility Gas Service"),
        ("CUSR0000SAE1", "Education"),
    ]

    for series_id, name in cpi_items:
        try:
            result = db.execute(text("""
                WITH current AS (
                    SELECT value, year, period FROM bls_cu_data
                    WHERE series_id = :sid AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1
                ),
                previous AS (
                    SELECT value FROM bls_cu_data
                    WHERE series_id = :sid AND period != 'M13'
                    ORDER BY year DESC, period DESC LIMIT 1 OFFSET 1
                ),
                year_ago AS (
                    SELECT value FROM bls_cu_data
                    WHERE series_id = :sid
                    AND year = (SELECT year - 1 FROM current)
                    AND period = (SELECT period FROM current)
                )
                SELECT c.value, c.year, c.period, p.value, y.value
                FROM current c
                LEFT JOIN previous p ON true
                LEFT JOIN year_ago y ON true
            """), {"sid": series_id}).fetchone()

            if result and result[0]:
                mom = round(((decimal_to_float(result[0]) - decimal_to_float(result[3])) / decimal_to_float(result[3])) * 100, 2) if result[3] else None
                yoy = round(((decimal_to_float(result[0]) - decimal_to_float(result[4])) / decimal_to_float(result[4])) * 100, 1) if result[4] else None
                cpi_categories.append(CPICategory(
                    item_code=series_id,
                    item_name=name,
                    index_value=decimal_to_float(result[0]),
                    mom_change=mom,
                    yoy_change=yoy,
                    period=get_period_name(result[2]),
                    year=result[1]
                ))
        except Exception as e:
            print(f"Error fetching CPI {name}: {e}")

    # --- REGIONAL UNEMPLOYMENT (Top 20 states) ---
    regional_unemployment = []
    try:
        result = db.execute(text("""
            WITH latest AS (
                SELECT DISTINCT ON (series_id) series_id, value, year, period
                FROM bls_la_data
                WHERE series_id LIKE 'LASST%03' AND period != 'M13'
                ORDER BY series_id, year DESC, period DESC
            ),
            previous AS (
                SELECT DISTINCT ON (series_id) series_id, value
                FROM bls_la_data
                WHERE series_id LIKE 'LASST%03' AND period != 'M13'
                  AND (year, period) < (SELECT year, period FROM latest LIMIT 1)
                ORDER BY series_id, year DESC, period DESC
            )
            SELECT l.series_id, l.value, l.year, l.period,
                   COALESCE(p.value, l.value) as prev_value
            FROM latest l
            LEFT JOIN previous p ON l.series_id = p.series_id
            ORDER BY l.value DESC
            LIMIT 25
        """)).fetchall()

        state_codes = {
            'ST0100000000000': 'Alabama', 'ST0200000000000': 'Alaska', 'ST0400000000000': 'Arizona',
            'ST0500000000000': 'Arkansas', 'ST0600000000000': 'California', 'ST0800000000000': 'Colorado',
            'ST0900000000000': 'Connecticut', 'ST1000000000000': 'Delaware', 'ST1100000000000': 'DC',
            'ST1200000000000': 'Florida', 'ST1300000000000': 'Georgia', 'ST1500000000000': 'Hawaii',
            'ST1600000000000': 'Idaho', 'ST1700000000000': 'Illinois', 'ST1800000000000': 'Indiana',
            'ST1900000000000': 'Iowa', 'ST2000000000000': 'Kansas', 'ST2100000000000': 'Kentucky',
            'ST2200000000000': 'Louisiana', 'ST2300000000000': 'Maine', 'ST2400000000000': 'Maryland',
            'ST2500000000000': 'Massachusetts', 'ST2600000000000': 'Michigan', 'ST2700000000000': 'Minnesota',
            'ST2800000000000': 'Mississippi', 'ST2900000000000': 'Missouri', 'ST3000000000000': 'Montana',
            'ST3100000000000': 'Nebraska', 'ST3200000000000': 'Nevada', 'ST3300000000000': 'New Hampshire',
            'ST3400000000000': 'New Jersey', 'ST3500000000000': 'New Mexico', 'ST3600000000000': 'New York',
            'ST3700000000000': 'North Carolina', 'ST3800000000000': 'North Dakota', 'ST3900000000000': 'Ohio',
            'ST4000000000000': 'Oklahoma', 'ST4100000000000': 'Oregon', 'ST4200000000000': 'Pennsylvania',
            'ST4400000000000': 'Rhode Island', 'ST4500000000000': 'South Carolina', 'ST4600000000000': 'South Dakota',
            'ST4700000000000': 'Tennessee', 'ST4800000000000': 'Texas', 'ST4900000000000': 'Utah',
            'ST5000000000000': 'Vermont', 'ST5100000000000': 'Virginia', 'ST5300000000000': 'Washington',
            'ST5400000000000': 'West Virginia', 'ST5500000000000': 'Wisconsin', 'ST5600000000000': 'Wyoming',
        }

        for row in result:
            series_id = row[0]
            # Extract state code from series_id (LASST0100000000003 -> ST0100000000000)
            state_key = series_id[3:18]
            state_name = state_codes.get(state_key, series_id[3:5])
            change = decimal_to_float(row[1]) - decimal_to_float(row[4]) if row[4] else None
            regional_unemployment.append(RegionalUnemployment(
                area_code=series_id,
                area_name=state_name,
                unemployment_rate=decimal_to_float(row[1]),
                rate_change=round(change, 2) if change else None,
                period=get_period_name(row[3]),
                year=row[2]
            ))
    except Exception as e:
        print(f"Error fetching regional: {e}")

    # --- TRENDS ---
    unemployment_trend = []
    try:
        result = db.execute(text("""
            SELECT year, period, value FROM bls_ln_data
            WHERE series_id = 'LNS14000000' AND period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 36
        """)).fetchall()
        for row in reversed(result):
            unemployment_trend.append(TrendPoint(
                date=f"{row[0]}-{row[1][1:]}",
                value=decimal_to_float(row[2]),
                period=get_period_name(row[1]),
                year=row[0]
            ))
    except Exception as e:
        print(f"Error: {e}")

    cpi_trend = []
    try:
        result = db.execute(text("""
            SELECT year, period, value FROM bls_cu_data
            WHERE series_id = 'CUSR0000SA0' AND period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 36
        """)).fetchall()
        for row in reversed(result):
            cpi_trend.append(TrendPoint(
                date=f"{row[0]}-{row[1][1:]}",
                value=decimal_to_float(row[2]),
                period=get_period_name(row[1]),
                year=row[0]
            ))
    except Exception as e:
        print(f"Error: {e}")

    payrolls_trend = []
    try:
        result = db.execute(text("""
            SELECT year, period, value FROM bls_ce_data
            WHERE series_id = 'CES0000000001' AND period != 'M13'
            ORDER BY year DESC, period DESC LIMIT 36
        """)).fetchall()
        for row in reversed(result):
            payrolls_trend.append(TrendPoint(
                date=f"{row[0]}-{row[1][1:]}",
                value=decimal_to_float(row[2]),
                period=get_period_name(row[1]),
                year=row[0]
            ))
    except Exception as e:
        print(f"Error: {e}")

    # --- SURVEYS ---
    surveys = [
        SurveyInfo(id="cu", code="CU", name="Consumer Price Index", description="Urban consumer inflation by item and area", path="/research/bls/cu", category="Price Indexes", update_frequency="Monthly"),
        SurveyInfo(id="cw", code="CW", name="CPI-W", description="CPI for Urban Wage Earners", path="/research/bls/cw", category="Price Indexes", update_frequency="Monthly"),
        SurveyInfo(id="su", code="SU", name="Chained CPI", description="C-CPI-U with substitution effects", path="/research/bls/su", category="Price Indexes", update_frequency="Monthly"),
        SurveyInfo(id="ap", code="AP", name="Average Prices", description="Retail prices for specific items", path="/research/bls/ap", category="Price Indexes", update_frequency="Monthly"),
        SurveyInfo(id="wp", code="WP", name="PPI - Commodities", description="Producer prices including Final Demand", path="/research/bls/wp", category="Price Indexes", update_frequency="Monthly"),
        SurveyInfo(id="pc", code="PC", name="PPI - Industry", description="Producer prices by NAICS industry", path="/research/bls/pc", category="Price Indexes", update_frequency="Monthly"),
        SurveyInfo(id="ce", code="CE", name="Employment Situation", description="Employment, hours, earnings by industry", path="/research/bls/ce", category="Employment", update_frequency="Monthly"),
        SurveyInfo(id="la", code="LA", name="Local Area Unemployment", description="State and metro unemployment rates", path="/research/bls/la", category="Employment", update_frequency="Monthly"),
        SurveyInfo(id="sm", code="SM", name="State & Metro Employment", description="Employment by state and metro", path="/research/bls/sm", category="Employment", update_frequency="Monthly"),
        SurveyInfo(id="jt", code="JT", name="JOLTS", description="Job openings, hires, separations", path="/research/bls/jt", category="Employment", update_frequency="Monthly"),
        SurveyInfo(id="oe", code="OE", name="Occupational Employment", description="Employment and wages by occupation", path="/research/bls/oe", category="Employment", update_frequency="Annual"),
        SurveyInfo(id="bd", code="BD", name="Business Employment Dynamics", description="Job gains/losses, establishment births/deaths", path="/research/bls/bd", category="Employment", update_frequency="Quarterly"),
        SurveyInfo(id="ln", code="LN", name="Labor Force Statistics", description="Unemployment, participation by demographics", path="/research/bls/ln", category="Labor Force", update_frequency="Monthly"),
        SurveyInfo(id="ec", code="EC", name="Employment Cost Index", description="Compensation cost trends", path="/research/bls/ec", category="Labor Force", update_frequency="Quarterly"),
        SurveyInfo(id="pr", code="PR", name="Productivity", description="Labor productivity and unit labor costs", path="/research/bls/pr", category="Productivity", update_frequency="Quarterly"),
        SurveyInfo(id="ip", code="IP", name="Industry Productivity", description="Productivity by major industry", path="/research/bls/ip", category="Productivity", update_frequency="Annual"),
        SurveyInfo(id="ei", code="EI", name="Import/Export Prices", description="International trade price indexes", path="/research/bls/ei", category="International", update_frequency="Monthly"),
        SurveyInfo(id="tu", code="TU", name="Time Use Survey", description="How Americans spend their time", path="/research/bls/tu", category="Other", update_frequency="Annual"),
    ]

    # --- QUICK STUDIES ---
    quick_studies = [
        QuickStudy(id="labor_tightness", title="Labor Tightness vs SPX", description="Job openings/unemployed ratio against equity performance"),
        QuickStudy(id="wage_margins", title="Wage Growth vs Margins", description="Wage growth trends vs corporate profit margins"),
        QuickStudy(id="cpi_surprise", title="CPI Surprise Analysis", description="Market reaction to CPI beats/misses"),
        QuickStudy(id="phillips_curve", title="Phillips Curve", description="Unemployment vs inflation relationship"),
    ]

    return BLSPortalData(
        labor_indicators=labor_indicators,
        employment_by_industry=employment_by_industry,
        cpi_categories=cpi_categories,
        regional_unemployment=regional_unemployment,
        unemployment_trend=unemployment_trend,
        cpi_trend=cpi_trend,
        payrolls_trend=payrolls_trend,
        surveys=surveys,
        quick_studies=quick_studies,
        last_updated=datetime.now().isoformat()
    )


# ============================================================================
# TREASURY COMPREHENSIVE ENDPOINT
# ============================================================================

@router.get("/treasury/comprehensive", response_model=TreasuryPortalData)
@cached("portal:treasury:comprehensive", category=DataCategory.TREASURY_YIELDS)
async def get_treasury_comprehensive(db: Session = Depends(get_data_db)):
    """Get comprehensive Treasury portal data (cached for 4h)"""

    # --- YIELD CURVE ---
    yield_curve = []
    maturities = [
        ("1-Month", 1, "yield_1m"), ("3-Month", 3, "yield_3m"), ("6-Month", 6, "yield_6m"),
        ("1-Year", 12, "yield_1y"), ("2-Year", 24, "yield_2y"), ("3-Year", 36, "yield_3y"),
        ("5-Year", 60, "yield_5y"), ("7-Year", 84, "yield_7y"), ("10-Year", 120, "yield_10y"),
        ("20-Year", 240, "yield_20y"), ("30-Year", 360, "yield_30y")
    ]

    try:
        # Get the latest 30 days of data for change calculations using ORM
        rates = db.query(TreasuryDailyRate).order_by(
            desc(TreasuryDailyRate.rate_date)
        ).limit(30).all()

        if rates:
            latest = rates[0]
            day_ago = rates[1] if len(rates) > 1 else None
            week_ago = rates[5] if len(rates) > 5 else None
            month_ago = rates[22] if len(rates) > 22 else None

            for term, months, attr_name in maturities:
                current_val = decimal_to_float(getattr(latest, attr_name, None))
                if current_val is not None:
                    # Calculate changes in basis points
                    change_1d = None
                    change_1w = None
                    change_1m = None

                    if day_ago:
                        day_val = decimal_to_float(getattr(day_ago, attr_name, None))
                        if day_val is not None:
                            change_1d = round((current_val - day_val) * 100, 1)

                    if week_ago:
                        week_val = decimal_to_float(getattr(week_ago, attr_name, None))
                        if week_val is not None:
                            change_1w = round((current_val - week_val) * 100, 1)

                    if month_ago:
                        month_val = decimal_to_float(getattr(month_ago, attr_name, None))
                        if month_val is not None:
                            change_1m = round((current_val - month_val) * 100, 1)

                    yield_curve.append(YieldCurvePoint(
                        maturity=term,
                        maturity_months=months,
                        yield_value=current_val,
                        change_1d=change_1d,
                        change_1w=change_1w,
                        change_1m=change_1m,
                    ))
    except Exception as e:
        print(f"Error fetching yield curve: {e}")

    # --- YIELD TRENDS ---
    yield_trend_10y = []
    yield_trend_2y = []
    try:
        # Get 90 days of rate data using ORM
        trend_rates = db.query(TreasuryDailyRate).order_by(
            desc(TreasuryDailyRate.rate_date)
        ).limit(90).all()

        for rate in reversed(trend_rates):
            if rate.yield_10y is not None:
                yield_trend_10y.append(TrendPoint(
                    date=str(rate.rate_date),
                    value=decimal_to_float(rate.yield_10y)
                ))
            if rate.yield_2y is not None:
                yield_trend_2y.append(TrendPoint(
                    date=str(rate.rate_date),
                    value=decimal_to_float(rate.yield_2y)
                ))
    except Exception as e:
        print(f"Error fetching yield trends: {e}")

    # --- SPREADS ---
    spreads = []
    try:
        # Get latest rate for spread calculations using ORM
        latest_rate = db.query(TreasuryDailyRate).order_by(
            desc(TreasuryDailyRate.rate_date)
        ).first()

        if latest_rate:
            y2 = decimal_to_float(latest_rate.yield_2y)
            y3m = decimal_to_float(latest_rate.yield_3m)
            y10 = decimal_to_float(latest_rate.yield_10y)
            y30 = decimal_to_float(latest_rate.yield_30y)
            spread_2s10s = decimal_to_float(latest_rate.spread_2s10s)

            # Use pre-calculated spread if available, otherwise calculate
            if spread_2s10s is not None:
                spreads.append(SpreadData(name="2s10s Spread", spread_bps=round(spread_2s10s * 100, 1)))
            elif y10 is not None and y2 is not None:
                spreads.append(SpreadData(name="2s10s Spread", spread_bps=round((y10 - y2) * 100, 1)))

            if y10 is not None and y3m is not None:
                spreads.append(SpreadData(name="3m10y Spread", spread_bps=round((y10 - y3m) * 100, 1)))

            if y30 is not None and y10 is not None:
                spreads.append(SpreadData(name="10s30s Spread", spread_bps=round((y30 - y10) * 100, 1)))
    except Exception as e:
        print(f"Error fetching spreads: {e}")

    # --- RECENT AUCTIONS ---
    recent_auctions = []
    try:
        # Get recent auctions using ORM
        auctions = db.query(TreasuryAuction).filter(
            TreasuryAuction.high_yield.isnot(None)
        ).order_by(
            desc(TreasuryAuction.auction_date)
        ).limit(15).all()

        for auction in auctions:
            total_accepted = decimal_to_float(auction.total_accepted) or 1
            recent_auctions.append(AuctionResult(
                security_type=auction.security_type or "Note",
                security_term=auction.security_term,
                auction_date=str(auction.auction_date),
                issue_date=str(auction.issue_date) if auction.issue_date else None,
                maturity_date=str(auction.maturity_date) if auction.maturity_date else None,
                high_yield=decimal_to_float(auction.high_yield),
                bid_to_cover=decimal_to_float(auction.bid_to_cover_ratio),
                primary_dealer_pct=round((decimal_to_float(auction.primary_dealer_accepted) or 0) / total_accepted * 100, 1) if total_accepted > 0 else None,
                direct_bidder_pct=round((decimal_to_float(auction.direct_bidder_accepted) or 0) / total_accepted * 100, 1) if total_accepted > 0 else None,
                indirect_bidder_pct=round((decimal_to_float(auction.indirect_bidder_accepted) or 0) / total_accepted * 100, 1) if total_accepted > 0 else None,
                total_accepted=decimal_to_float(auction.total_accepted),
                total_tendered=decimal_to_float(auction.total_tendered),
                cusip=auction.cusip,
            ))
    except Exception as e:
        print(f"Error fetching auctions: {e}")

    # --- UPCOMING AUCTIONS ---
    upcoming_auctions = []
    try:
        # Get upcoming auctions using ORM
        upcoming = db.query(TreasuryUpcomingAuction).filter(
            TreasuryUpcomingAuction.auction_date >= date.today()
        ).order_by(
            TreasuryUpcomingAuction.auction_date
        ).limit(20).all()

        for auction in upcoming:
            upcoming_auctions.append(UpcomingAuctionData(
                security_type=auction.security_type or "Note",
                security_term=auction.security_term,
                announcement_date=str(auction.announcement_date) if auction.announcement_date else None,
                auction_date=str(auction.auction_date),
                issue_date=str(auction.issue_date) if auction.issue_date else None,
                offering_amount=decimal_to_float(auction.offering_amount),
            ))
    except Exception as e:
        print(f"Error fetching upcoming auctions: {e}")

    # --- QUICK STUDIES ---
    quick_studies = [
        QuickStudy(id="auction_impact", title="Auction Impact Study", description="Market reaction to auction results"),
        QuickStudy(id="curve_inversion", title="Curve Inversion Analysis", description="Yield curve inversions and recessions"),
        QuickStudy(id="rates_equities", title="Rates vs Equities", description="Rate changes and equity performance"),
    ]

    return TreasuryPortalData(
        yield_curve=yield_curve,
        yield_trend_10y=yield_trend_10y,
        yield_trend_2y=yield_trend_2y,
        spreads=spreads,
        recent_auctions=recent_auctions,
        upcoming_auctions=upcoming_auctions,
        quick_studies=quick_studies,
        last_updated=datetime.now().isoformat()
    )


# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@router.get("/bls/snapshot")
@cached("portal:bls:comprehensive", category=DataCategory.BLS_MONTHLY)
async def get_bls_snapshot(db: Session = Depends(get_data_db)):
    """Legacy endpoint - same cache as comprehensive"""
    # Note: shares cache key with /bls/comprehensive
    return await get_bls_comprehensive.__wrapped__(db)  # Call original function


@router.get("/treasury/snapshot")
@cached("portal:treasury:comprehensive", category=DataCategory.TREASURY_YIELDS)
async def get_treasury_snapshot(db: Session = Depends(get_data_db)):
    """Legacy endpoint - same cache as comprehensive"""
    return await get_treasury_comprehensive.__wrapped__(db)
