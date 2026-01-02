"""
Stock Screener Service

Provides screening functionality against the DATA database.
Queries multiple tables and applies filters dynamically.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, and_, or_, case, text
from sqlalchemy.sql import label
from decimal import Decimal

from ...data_models import (
    NasdaqScreenerProfile,
    CompanyProfileBulk,
    RatiosTTMBulk,
    KeyMetricsTTMBulk,
    PriceTargetSummaryBulk,
    InstitutionalOwnership,
    InsiderStatistics,
)
from ...schemas.stocks import (
    ScreenRequest,
    ScreenFilter,
    UniverseFilter,
    FilterOperator,
    SortOrder,
    StockResult,
)
from .feature_registry import FEATURE_REGISTRY, get_feature

import logging
import math


def safe_float(value) -> float | None:
    """Convert to float, returning None for None, NaN, or Infinity values."""
    if value is None:
        return None
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None

logger = logging.getLogger(__name__)


# =============================================================================
# Table Mapping
# =============================================================================

# Map source_table names to actual SQLAlchemy models
TABLE_MAP = {
    "nasdaq_screener_profiles": NasdaqScreenerProfile,
    "company_profile_bulk": CompanyProfileBulk,
    "ratios_ttm_bulk": RatiosTTMBulk,
    "key_metrics_ttm_bulk": KeyMetricsTTMBulk,
    "price_target_summary_bulk": PriceTargetSummaryBulk,
    "institutional_ownership": InstitutionalOwnership,
    "insider_statistics": InsiderStatistics,
}

# Tables that need special handling (time-series with latest record needed)
TIME_SERIES_TABLES = {
    "nasdaq_screener_profiles": "snapshot_date",
    "institutional_ownership": "date",
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_latest_snapshot_date(db: Session) -> Any:
    """Get the most recent snapshot date from NasdaqScreenerProfile."""
    result = db.query(func.max(NasdaqScreenerProfile.snapshot_date)).scalar()
    return result


def get_latest_ownership_date(db: Session) -> Any:
    """Get the most recent date from InstitutionalOwnership."""
    result = db.query(func.max(InstitutionalOwnership.date)).scalar()
    return result


def get_latest_insider_period(db: Session) -> Tuple[int, int]:
    """Get the most recent year/quarter from InsiderStatistics."""
    result = db.query(
        InsiderStatistics.year,
        InsiderStatistics.quarter
    ).order_by(
        desc(InsiderStatistics.year),
        desc(InsiderStatistics.quarter)
    ).first()

    if result:
        return result.year, result.quarter
    return None, None


def get_column_from_model(model, column_name: str):
    """Get a column attribute from a SQLAlchemy model."""
    if hasattr(model, column_name):
        return getattr(model, column_name)
    return None


def build_filter_condition(model, column_name: str, operator: FilterOperator, value: Any):
    """Build a SQLAlchemy filter condition based on operator."""
    column = get_column_from_model(model, column_name)
    if column is None:
        return None

    if operator == FilterOperator.EQ:
        return column == value
    elif operator == FilterOperator.NE:
        return column != value
    elif operator == FilterOperator.GT:
        return column > value
    elif operator == FilterOperator.GTE:
        return column >= value
    elif operator == FilterOperator.LT:
        return column < value
    elif operator == FilterOperator.LTE:
        return column <= value
    elif operator == FilterOperator.IN:
        if isinstance(value, list):
            return column.in_(value)
        return column.in_([value])
    elif operator == FilterOperator.NOT_IN:
        if isinstance(value, list):
            return ~column.in_(value)
        return ~column.in_([value])
    elif operator == FilterOperator.BETWEEN:
        if isinstance(value, list) and len(value) == 2:
            return and_(column >= value[0], column <= value[1])
        return None
    elif operator == FilterOperator.IS_NULL:
        return column.is_(None)
    elif operator == FilterOperator.IS_NOT_NULL:
        return column.isnot(None)
    elif operator == FilterOperator.CONTAINS:
        return column.ilike(f"%{value}%")
    elif operator == FilterOperator.STARTS_WITH:
        return column.ilike(f"{value}%")
    elif operator == FilterOperator.ENDS_WITH:
        return column.ilike(f"%{value}")

    return None


# =============================================================================
# Main Screener Service
# =============================================================================

class ScreenerService:
    """Service for running stock screens against the DATA database."""

    def __init__(self, db: Session):
        self.db = db
        self._latest_snapshot_date = None
        self._latest_ownership_date = None
        self._latest_insider_year = None
        self._latest_insider_quarter = None

    @property
    def latest_snapshot_date(self):
        if self._latest_snapshot_date is None:
            self._latest_snapshot_date = get_latest_snapshot_date(self.db)
        return self._latest_snapshot_date

    @property
    def latest_ownership_date(self):
        if self._latest_ownership_date is None:
            self._latest_ownership_date = get_latest_ownership_date(self.db)
        return self._latest_ownership_date

    @property
    def latest_insider_period(self):
        if self._latest_insider_year is None:
            self._latest_insider_year, self._latest_insider_quarter = get_latest_insider_period(self.db)
        return self._latest_insider_year, self._latest_insider_quarter

    def get_universe_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the stock universe.

        Returns total count, sector breakdown, and market cap distribution.
        """
        if not self.latest_snapshot_date:
            return {
                "total_stocks": 0,
                "sectors": [],
                "exchanges": [],
                "market_cap_distribution": {},
                "data_as_of": None,
            }

        # Base query - latest snapshot
        base_query = self.db.query(NasdaqScreenerProfile).filter(
            NasdaqScreenerProfile.snapshot_date == self.latest_snapshot_date
        )

        # Total count
        total_stocks = base_query.count()

        # Sector breakdown
        sector_counts = self.db.query(
            NasdaqScreenerProfile.sector,
            func.count(NasdaqScreenerProfile.symbol).label("count")
        ).filter(
            NasdaqScreenerProfile.snapshot_date == self.latest_snapshot_date,
            NasdaqScreenerProfile.sector.isnot(None),
            NasdaqScreenerProfile.sector != ""
        ).group_by(
            NasdaqScreenerProfile.sector
        ).order_by(
            desc("count")
        ).all()

        sectors = [
            {"sector": s.sector, "count": s.count}
            for s in sector_counts
        ]

        # Exchange breakdown (from CompanyProfileBulk)
        exchange_counts = self.db.query(
            CompanyProfileBulk.exchange,
            func.count(CompanyProfileBulk.symbol).label("count")
        ).filter(
            CompanyProfileBulk.exchange.isnot(None),
            CompanyProfileBulk.is_actively_trading == True
        ).group_by(
            CompanyProfileBulk.exchange
        ).order_by(
            desc("count")
        ).all()

        exchanges = [
            {"exchange": e.exchange, "count": e.count}
            for e in exchange_counts
        ]

        # Market cap distribution
        market_cap_dist = self._get_market_cap_distribution()

        return {
            "total_stocks": total_stocks,
            "sectors": sectors,
            "exchanges": exchanges,
            "market_cap_distribution": market_cap_dist,
            "data_as_of": str(self.latest_snapshot_date) if self.latest_snapshot_date else None,
        }

    def _get_market_cap_distribution(self) -> Dict[str, int]:
        """Get market cap distribution by category."""
        if not self.latest_snapshot_date:
            return {}

        # Define market cap ranges
        ranges = [
            ("mega_cap", 200_000_000_000, None),       # > $200B
            ("large_cap", 10_000_000_000, 200_000_000_000),  # $10B - $200B
            ("mid_cap", 2_000_000_000, 10_000_000_000),      # $2B - $10B
            ("small_cap", 300_000_000, 2_000_000_000),       # $300M - $2B
            ("micro_cap", 50_000_000, 300_000_000),          # $50M - $300M
            ("nano_cap", 0, 50_000_000),                     # < $50M
        ]

        result = {}
        for name, min_cap, max_cap in ranges:
            query = self.db.query(func.count(NasdaqScreenerProfile.symbol)).filter(
                NasdaqScreenerProfile.snapshot_date == self.latest_snapshot_date,
                NasdaqScreenerProfile.market_cap.isnot(None)
            )

            if min_cap is not None:
                query = query.filter(NasdaqScreenerProfile.market_cap >= min_cap)
            if max_cap is not None:
                query = query.filter(NasdaqScreenerProfile.market_cap < max_cap)

            result[name] = query.scalar() or 0

        return result

    def get_sectors(self) -> List[Dict[str, Any]]:
        """Get all sectors with stock counts."""
        if not self.latest_snapshot_date:
            return []

        sectors = self.db.query(
            NasdaqScreenerProfile.sector,
            func.count(NasdaqScreenerProfile.symbol).label("count")
        ).filter(
            NasdaqScreenerProfile.snapshot_date == self.latest_snapshot_date,
            NasdaqScreenerProfile.sector.isnot(None),
            NasdaqScreenerProfile.sector != ""
        ).group_by(
            NasdaqScreenerProfile.sector
        ).order_by(
            NasdaqScreenerProfile.sector
        ).all()

        return [{"sector": s.sector, "count": s.count} for s in sectors]

    def get_industries(self, sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all industries, optionally filtered by sector."""
        if not self.latest_snapshot_date:
            return []

        query = self.db.query(
            NasdaqScreenerProfile.industry,
            NasdaqScreenerProfile.sector,
            func.count(NasdaqScreenerProfile.symbol).label("count")
        ).filter(
            NasdaqScreenerProfile.snapshot_date == self.latest_snapshot_date,
            NasdaqScreenerProfile.industry.isnot(None),
            NasdaqScreenerProfile.industry != ""
        )

        if sector:
            query = query.filter(NasdaqScreenerProfile.sector == sector)

        industries = query.group_by(
            NasdaqScreenerProfile.industry,
            NasdaqScreenerProfile.sector
        ).order_by(
            NasdaqScreenerProfile.industry
        ).all()

        return [
            {"industry": i.industry, "sector": i.sector, "count": i.count}
            for i in industries
        ]

    def run_screen(
        self,
        filters: Optional[List[ScreenFilter]] = None,
        universe: Optional[UniverseFilter] = None,
        columns: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: SortOrder = SortOrder.DESC,
        limit: int = 100,
        offset: int = 0,
        skip_count: bool = False,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Run a stock screen with the specified filters.

        Returns (results, total_count).

        Args:
            skip_count: If True, skip the expensive COUNT query and return -1 for total_count.
                       Useful for initial page loads where exact count isn't needed.
        """
        if not self.latest_snapshot_date:
            return [], 0

        # Determine which tables we need based on filters and columns
        required_tables = self._get_required_tables(filters, columns, sort_by)

        # Add company_profile_bulk if universe filters require it
        if universe:
            if universe.exclude_etfs or universe.exclude_adrs or universe.exchanges:
                required_tables.add("company_profile_bulk")

        # Tables that have filters applied should use INNER JOIN for better performance
        filter_tables = self._get_filter_tables(filters)

        # Build the query with necessary joins
        query = self._build_base_query(required_tables, filter_tables)

        # Apply universe filters
        query = self._apply_universe_filters(query, universe)

        # Apply screen filters
        query = self._apply_screen_filters(query, filters, required_tables)

        # Get total count before pagination (skip if not needed for performance)
        if skip_count:
            total_count = -1  # Indicates count was skipped
        else:
            # Use a simpler count query
            count_query = query.with_entities(func.count(NasdaqScreenerProfile.symbol.distinct()))
            total_count = count_query.scalar() or 0

        # Apply sorting
        query = self._apply_sorting(query, sort_by, sort_order, required_tables)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute and format results
        results = self._execute_and_format(query, columns, required_tables)

        # If we skipped count but got fewer results than limit, we know the total
        if skip_count and len(results) < limit:
            total_count = offset + len(results)

        return results, total_count

    def _get_filter_tables(self, filters: Optional[List[ScreenFilter]]) -> set:
        """Get tables that have filters applied (candidates for INNER JOIN)."""
        filter_tables = set()
        if filters:
            for f in filters:
                feature = get_feature(f.feature)
                if feature:
                    filter_tables.add(feature["source_table"])
        return filter_tables

    def _get_required_tables(
        self,
        filters: Optional[List[ScreenFilter]],
        columns: Optional[List[str]],
        sort_by: Optional[str]
    ) -> set:
        """Determine which tables are needed for this query."""
        required = {"nasdaq_screener_profiles"}  # Always need base table

        # Add tables from filters
        if filters:
            for f in filters:
                feature = get_feature(f.feature)
                if feature:
                    required.add(feature["source_table"])

        # Add tables from columns
        if columns:
            for col in columns:
                feature = get_feature(col)
                if feature:
                    required.add(feature["source_table"])

        # Add table from sort_by
        if sort_by:
            feature = get_feature(sort_by)
            if feature:
                required.add(feature["source_table"])

        return required

    def _build_base_query(self, required_tables: set, filter_tables: set = None):
        """Build base query with necessary joins.

        Args:
            required_tables: All tables needed for the query
            filter_tables: Tables that have filters applied (use INNER JOIN for these)
        """
        if filter_tables is None:
            filter_tables = set()

        # Start with NasdaqScreenerProfile (latest snapshot only)
        query = self.db.query(NasdaqScreenerProfile).filter(
            NasdaqScreenerProfile.snapshot_date == self.latest_snapshot_date
        )

        # Join other tables as needed
        # Use INNER JOIN for tables with filters (faster, and NULL values would fail filter anyway)
        # Use OUTER JOIN for tables only needed for display columns

        if "company_profile_bulk" in required_tables:
            if "company_profile_bulk" in filter_tables:
                query = query.join(
                    CompanyProfileBulk,
                    NasdaqScreenerProfile.symbol == CompanyProfileBulk.symbol
                )
            else:
                query = query.outerjoin(
                    CompanyProfileBulk,
                    NasdaqScreenerProfile.symbol == CompanyProfileBulk.symbol
                )

        if "ratios_ttm_bulk" in required_tables:
            if "ratios_ttm_bulk" in filter_tables:
                query = query.join(
                    RatiosTTMBulk,
                    NasdaqScreenerProfile.symbol == RatiosTTMBulk.symbol
                )
            else:
                query = query.outerjoin(
                    RatiosTTMBulk,
                    NasdaqScreenerProfile.symbol == RatiosTTMBulk.symbol
                )

        if "key_metrics_ttm_bulk" in required_tables:
            if "key_metrics_ttm_bulk" in filter_tables:
                query = query.join(
                    KeyMetricsTTMBulk,
                    NasdaqScreenerProfile.symbol == KeyMetricsTTMBulk.symbol
                )
            else:
                query = query.outerjoin(
                    KeyMetricsTTMBulk,
                    NasdaqScreenerProfile.symbol == KeyMetricsTTMBulk.symbol
                )

        if "price_target_summary_bulk" in required_tables:
            if "price_target_summary_bulk" in filter_tables:
                query = query.join(
                    PriceTargetSummaryBulk,
                    NasdaqScreenerProfile.symbol == PriceTargetSummaryBulk.symbol
                )
            else:
                query = query.outerjoin(
                    PriceTargetSummaryBulk,
                    NasdaqScreenerProfile.symbol == PriceTargetSummaryBulk.symbol
                )

        if "institutional_ownership" in required_tables:
            # Join latest ownership data
            if self.latest_ownership_date:
                join_condition = and_(
                    NasdaqScreenerProfile.symbol == InstitutionalOwnership.symbol,
                    InstitutionalOwnership.date == self.latest_ownership_date
                )
                if "institutional_ownership" in filter_tables:
                    query = query.join(InstitutionalOwnership, join_condition)
                else:
                    query = query.outerjoin(InstitutionalOwnership, join_condition)

        if "insider_statistics" in required_tables:
            # Join latest insider data
            year, quarter = self.latest_insider_period
            if year and quarter:
                join_condition = and_(
                    NasdaqScreenerProfile.symbol == InsiderStatistics.symbol,
                    InsiderStatistics.year == year,
                    InsiderStatistics.quarter == quarter
                )
                if "insider_statistics" in filter_tables:
                    query = query.join(InsiderStatistics, join_condition)
                else:
                    query = query.outerjoin(InsiderStatistics, join_condition)

        return query

    def _apply_universe_filters(self, query, universe: Optional[UniverseFilter]):
        """Apply universe-level filters (market cap, sector, etc.)."""
        if not universe:
            return query

        if universe.min_market_cap is not None:
            query = query.filter(NasdaqScreenerProfile.market_cap >= universe.min_market_cap)

        if universe.max_market_cap is not None:
            query = query.filter(NasdaqScreenerProfile.market_cap <= universe.max_market_cap)

        if universe.sectors:
            query = query.filter(NasdaqScreenerProfile.sector.in_(universe.sectors))

        if universe.industries:
            query = query.filter(NasdaqScreenerProfile.industry.in_(universe.industries))

        if universe.countries:
            query = query.filter(NasdaqScreenerProfile.country.in_(universe.countries))

        if universe.exchanges:
            query = query.filter(CompanyProfileBulk.exchange.in_(universe.exchanges))

        if universe.min_volume is not None:
            query = query.filter(NasdaqScreenerProfile.volume >= universe.min_volume)

        if universe.exclude_etfs:
            query = query.filter(
                or_(
                    CompanyProfileBulk.is_etf == False,
                    CompanyProfileBulk.is_etf.is_(None)
                )
            )

        if universe.exclude_adrs:
            query = query.filter(
                or_(
                    CompanyProfileBulk.is_adr == False,
                    CompanyProfileBulk.is_adr.is_(None)
                )
            )

        return query

    def _apply_screen_filters(
        self,
        query,
        filters: Optional[List[ScreenFilter]],
        required_tables: set
    ):
        """Apply screening filters."""
        if not filters:
            return query

        for f in filters:
            feature = get_feature(f.feature)
            if not feature:
                logger.warning(f"Unknown feature: {f.feature}")
                continue

            table_name = feature["source_table"]
            column_name = feature["source_column"]
            model = TABLE_MAP.get(table_name)

            if not model:
                logger.warning(f"Unknown table: {table_name}")
                continue

            condition = build_filter_condition(model, column_name, f.operator, f.value)
            if condition is not None:
                query = query.filter(condition)

        return query

    def _apply_sorting(
        self,
        query,
        sort_by: Optional[str],
        sort_order: SortOrder,
        required_tables: set
    ):
        """Apply sorting to query."""
        if not sort_by:
            # Default sort by market cap descending
            return query.order_by(desc(NasdaqScreenerProfile.market_cap))

        feature = get_feature(sort_by)
        if not feature:
            return query.order_by(desc(NasdaqScreenerProfile.market_cap))

        table_name = feature["source_table"]
        column_name = feature["source_column"]
        model = TABLE_MAP.get(table_name)

        if not model:
            return query.order_by(desc(NasdaqScreenerProfile.market_cap))

        column = get_column_from_model(model, column_name)
        if column is None:
            return query.order_by(desc(NasdaqScreenerProfile.market_cap))

        # Apply sort order
        if sort_order == SortOrder.ASC:
            query = query.order_by(asc(column).nullslast())
        else:
            query = query.order_by(desc(column).nullslast())

        return query

    def _execute_and_format(
        self,
        query,
        columns: Optional[List[str]],
        required_tables: set
    ) -> List[Dict[str, Any]]:
        """Execute query and format results."""
        # Define which columns to select based on required tables
        select_columns = [
            NasdaqScreenerProfile.symbol,
            NasdaqScreenerProfile.name,
            NasdaqScreenerProfile.sector,
            NasdaqScreenerProfile.industry,
            NasdaqScreenerProfile.country,
            NasdaqScreenerProfile.last_sale,
            NasdaqScreenerProfile.net_change,
            NasdaqScreenerProfile.percent_change,
            NasdaqScreenerProfile.market_cap,
            NasdaqScreenerProfile.volume,
        ]

        if "company_profile_bulk" in required_tables:
            select_columns.extend([
                CompanyProfileBulk.beta,
                CompanyProfileBulk.exchange,
                CompanyProfileBulk.average_volume,
                CompanyProfileBulk.last_dividend,
            ])

        if "ratios_ttm_bulk" in required_tables:
            select_columns.extend([
                RatiosTTMBulk.price_to_earnings_ratio_ttm,
                RatiosTTMBulk.price_to_book_ratio_ttm,
                RatiosTTMBulk.dividend_yield_ttm,
                RatiosTTMBulk.gross_profit_margin_ttm,
                RatiosTTMBulk.net_profit_margin_ttm,
                RatiosTTMBulk.debt_to_equity_ratio_ttm,
                RatiosTTMBulk.current_ratio_ttm,
            ])

        if "key_metrics_ttm_bulk" in required_tables:
            select_columns.extend([
                KeyMetricsTTMBulk.return_on_equity_ttm,
                KeyMetricsTTMBulk.return_on_invested_capital_ttm,
                KeyMetricsTTMBulk.ev_to_ebitda_ttm,
                KeyMetricsTTMBulk.earnings_yield_ttm,
                KeyMetricsTTMBulk.free_cash_flow_yield_ttm,
            ])

        # Update query to select specific columns
        query = query.with_entities(*select_columns)

        # Execute query
        rows = query.all()

        # Format results - use dict to deduplicate by symbol
        results_dict = {}
        for row in rows:
            # Skip if we already have this symbol (deduplication)
            if row.symbol in results_dict:
                continue
            result = {
                "symbol": row.symbol,
                "company_name": row.name,
                "sector": row.sector,
                "industry": row.industry,
                "country": row.country,
                "price": safe_float(row.last_sale),
                "price_change": safe_float(row.net_change),
                "price_change_pct": safe_float(row.percent_change),
                "market_cap": row.market_cap,
                "volume": row.volume,
            }

            # Add optional fields if available
            if hasattr(row, "beta"):
                result["beta"] = safe_float(row.beta)
            if hasattr(row, "exchange"):
                result["exchange"] = row.exchange
            if hasattr(row, "average_volume"):
                result["avg_volume"] = row.average_volume
            if hasattr(row, "price_to_earnings_ratio_ttm"):
                result["pe_ratio_ttm"] = safe_float(row.price_to_earnings_ratio_ttm)
            if hasattr(row, "price_to_book_ratio_ttm"):
                result["pb_ratio"] = safe_float(row.price_to_book_ratio_ttm)
            if hasattr(row, "dividend_yield_ttm"):
                result["dividend_yield"] = safe_float(row.dividend_yield_ttm)
            if hasattr(row, "return_on_equity_ttm"):
                result["roe"] = safe_float(row.return_on_equity_ttm)
            if hasattr(row, "return_on_invested_capital_ttm"):
                result["roic"] = safe_float(row.return_on_invested_capital_ttm)
            if hasattr(row, "ev_to_ebitda_ttm"):
                result["ev_to_ebitda"] = safe_float(row.ev_to_ebitda_ttm)
            if hasattr(row, "earnings_yield_ttm"):
                result["earnings_yield"] = safe_float(row.earnings_yield_ttm)
            if hasattr(row, "gross_profit_margin_ttm"):
                result["gross_margin"] = safe_float(row.gross_profit_margin_ttm)
            if hasattr(row, "net_profit_margin_ttm"):
                result["net_profit_margin"] = safe_float(row.net_profit_margin_ttm)
            if hasattr(row, "debt_to_equity_ratio_ttm"):
                result["debt_to_equity"] = safe_float(row.debt_to_equity_ratio_ttm)
            if hasattr(row, "current_ratio_ttm"):
                result["current_ratio"] = safe_float(row.current_ratio_ttm)
            if hasattr(row, "free_cash_flow_yield_ttm"):
                result["fcf_yield"] = safe_float(row.free_cash_flow_yield_ttm)

            results_dict[row.symbol] = result

        return list(results_dict.values())
