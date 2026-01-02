"""Flagship screen templates API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
import time

from ...database import get_data_db
from ...schemas.stocks import (
    ScreenTemplate, ScreenFilter, UniverseFilter, SortOrder, FilterOperator,
    ScreenResponse, StockResult
)
from ...services.stocks import ScreenerService

router = APIRouter(prefix="/templates", tags=["templates"])


# =============================================================================
# Flagship Screen Templates (12 templates from docs/Stocks.md)
# =============================================================================

SCREEN_TEMPLATES: List[ScreenTemplate] = [
    # Template 1: Deep Value - Much looser filters to find more stocks
    ScreenTemplate(
        template_key="deep_value",
        name="Deep Value",
        description="Find stocks trading at significant discounts. Low P/E ratio.",
        category="value",
        filters=[
            ScreenFilter(feature="pe_ratio_ttm", operator=FilterOperator.GT, value=0),
            ScreenFilter(feature="pe_ratio_ttm", operator=FilterOperator.LT, value=50),
        ],
        universe=UniverseFilter(min_market_cap=100_000_000, exclude_etfs=False),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "pe_ratio_ttm", "pb_ratio"],
        sort_by="pe_ratio_ttm",
        sort_order=SortOrder.ASC
    ),

    # Template 2: Quality Compounders (positive ROE only)
    ScreenTemplate(
        template_key="quality_compounders",
        name="Quality Compounders",
        description="High-quality businesses with strong returns on equity and good margins.",
        category="quality",
        filters=[
            ScreenFilter(feature="roe", operator=FilterOperator.GT, value=0.10),
            ScreenFilter(feature="roe", operator=FilterOperator.LT, value=1.0),
        ],
        universe=UniverseFilter(min_market_cap=500_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "roe", "gross_margin", "net_profit_margin"],
        sort_by="roe",
        sort_order=SortOrder.DESC
    ),

    # Template 3: GARP (Growth at Reasonable Price)
    ScreenTemplate(
        template_key="garp",
        name="GARP",
        description="Growth stocks that aren't overvalued. Reasonable P/E with good ROE.",
        category="growth",
        filters=[
            ScreenFilter(feature="pe_ratio_ttm", operator=FilterOperator.GT, value=0),
            ScreenFilter(feature="pe_ratio_ttm", operator=FilterOperator.LT, value=30),
        ],
        universe=UniverseFilter(min_market_cap=300_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "pe_ratio_ttm", "roe"],
        sort_by="pe_ratio_ttm",
        sort_order=SortOrder.ASC
    ),

    # Template 4: Dividend Income (loosened yield threshold)
    ScreenTemplate(
        template_key="dividend_income",
        name="Dividend Income",
        description="High-quality dividend payers with sustainable yields.",
        category="income",
        filters=[
            ScreenFilter(feature="dividend_yield", operator=FilterOperator.GT, value=0.01),
            ScreenFilter(feature="dividend_yield", operator=FilterOperator.LT, value=0.15),
        ],
        universe=UniverseFilter(min_market_cap=500_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "dividend_yield", "payout_ratio"],
        sort_by="dividend_yield",
        sort_order=SortOrder.DESC
    ),

    # Template 5: High Beta Momentum
    ScreenTemplate(
        template_key="momentum_leaders",
        name="High Beta Momentum",
        description="Stocks with high beta - more volatile, potential momentum plays.",
        category="momentum",
        filters=[
            ScreenFilter(feature="beta", operator=FilterOperator.GT, value=1.2),
        ],
        universe=UniverseFilter(min_market_cap=1_000_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "price_change_pct", "market_cap", "beta"],
        sort_by="beta",
        sort_order=SortOrder.DESC
    ),

    # Template 6: Value with Quality (low P/E + positive ROE)
    ScreenTemplate(
        template_key="value_quality",
        name="Value with Quality",
        description="Cheap stocks with proven profitability. Low valuations, positive returns.",
        category="value",
        filters=[
            ScreenFilter(feature="pe_ratio_ttm", operator=FilterOperator.LT, value=20),
            ScreenFilter(feature="pe_ratio_ttm", operator=FilterOperator.GT, value=0),
        ],
        universe=UniverseFilter(min_market_cap=500_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "price_change_pct", "market_cap", "pe_ratio_ttm"],
        sort_by="pe_ratio_ttm",
        sort_order=SortOrder.ASC
    ),

    # Template 7: Small Cap Opportunities
    ScreenTemplate(
        template_key="small_cap_growth",
        name="Small Cap Opportunities",
        description="Smaller companies with positive profitability.",
        category="growth",
        filters=[
            ScreenFilter(feature="roe", operator=FilterOperator.GT, value=0.05),
        ],
        universe=UniverseFilter(min_market_cap=300_000_000, max_market_cap=2_000_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "roe", "gross_margin"],
        sort_by="roe",
        sort_order=SortOrder.DESC
    ),

    # Template 8: Low Volatility (defensive)
    ScreenTemplate(
        template_key="low_vol_dividend",
        name="Low Volatility",
        description="Defensive stocks with lower market sensitivity. Beta below 1.",
        category="defensive",
        filters=[
            ScreenFilter(feature="beta", operator=FilterOperator.LT, value=0.9),
            ScreenFilter(feature="beta", operator=FilterOperator.GT, value=0),
        ],
        universe=UniverseFilter(min_market_cap=1_000_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "beta", "dividend_yield"],
        sort_by="beta",
        sort_order=SortOrder.ASC
    ),

    # Template 9: High Dividend Yield
    ScreenTemplate(
        template_key="high_yield",
        name="High Dividend Yield",
        description="Stocks with above-average dividend yields.",
        category="income",
        filters=[
            ScreenFilter(feature="dividend_yield", operator=FilterOperator.GT, value=0.04),
        ],
        universe=UniverseFilter(min_market_cap=500_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "dividend_yield", "payout_ratio"],
        sort_by="dividend_yield",
        sort_order=SortOrder.DESC
    ),

    # Template 10: Large Cap Leaders
    ScreenTemplate(
        template_key="large_cap_leaders",
        name="Large Cap Leaders",
        description="Large, established companies with strong fundamentals.",
        category="quality",
        filters=[
            ScreenFilter(feature="roe", operator=FilterOperator.GT, value=0.10),
        ],
        universe=UniverseFilter(min_market_cap=50_000_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "roe", "pe_ratio_ttm"],
        sort_by="market_cap",
        sort_order=SortOrder.DESC
    ),

    # Template 11: Undervalued by P/B
    ScreenTemplate(
        template_key="low_pb",
        name="Low Price-to-Book",
        description="Stocks trading below book value. Potential value traps or hidden gems.",
        category="value",
        filters=[
            ScreenFilter(feature="pb_ratio", operator=FilterOperator.LT, value=1.0),
            ScreenFilter(feature="pb_ratio", operator=FilterOperator.GT, value=0),
        ],
        universe=UniverseFilter(min_market_cap=500_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "pb_ratio", "pe_ratio_ttm"],
        sort_by="pb_ratio",
        sort_order=SortOrder.ASC
    ),

    # Template 12: Profitable & Growing
    ScreenTemplate(
        template_key="profitable_growth",
        name="Profitable Growth",
        description="Companies with solid margins and good returns on capital.",
        category="growth",
        filters=[
            ScreenFilter(feature="net_profit_margin", operator=FilterOperator.GT, value=0.08),
            ScreenFilter(feature="roe", operator=FilterOperator.GT, value=0.10),
        ],
        universe=UniverseFilter(min_market_cap=1_000_000_000),
        default_columns=["symbol", "company_name", "sector", "price", "market_cap", "net_profit_margin", "roe", "gross_margin"],
        sort_by="net_profit_margin",
        sort_order=SortOrder.DESC
    ),
]


# Create lookup dictionary
TEMPLATES_BY_KEY = {t.template_key: t for t in SCREEN_TEMPLATES}


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/", response_model=List[ScreenTemplate])
def list_templates(category: str = None):
    """
    Get all flagship screen templates.

    Optionally filter by category (value, growth, income, momentum, etc.)
    """
    if category:
        return [t for t in SCREEN_TEMPLATES if t.category == category]
    return SCREEN_TEMPLATES


@router.get("/categories")
def list_template_categories():
    """Get all template categories with counts"""
    categories = {}
    for t in SCREEN_TEMPLATES:
        if t.category not in categories:
            categories[t.category] = []
        categories[t.category].append(t.template_key)

    return {
        "total_templates": len(SCREEN_TEMPLATES),
        "categories": [
            {"category": cat, "count": len(keys), "templates": keys}
            for cat, keys in sorted(categories.items())
        ]
    }


@router.get("/{template_key}", response_model=ScreenTemplate)
def get_template(template_key: str):
    """Get a specific template by key"""
    template = TEMPLATES_BY_KEY.get(template_key)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_key}' not found"
        )
    return template


@router.post("/{template_key}/run", response_model=ScreenResponse)
def run_template(
    template_key: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    include_count: bool = Query(False, description="Include total count (slower)"),
    sort_by: str = Query(None, description="Override sort column (default: template's sort_by)"),
    sort_order: str = Query(None, description="Override sort order: 'asc' or 'desc' (default: template's sort_order)"),
    data_db: Session = Depends(get_data_db)
):
    """
    Run a flagship template and return results.

    This is a public endpoint - no authentication required.
    Useful for quick exploration of template results.

    Set include_count=true to get exact total_count (adds ~10s to query time).
    Use sort_by and sort_order to override the template's default sorting.
    """
    template = TEMPLATES_BY_KEY.get(template_key)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_key}' not found"
        )

    start_time = time.time()

    # Use the ScreenerService to run the template
    screener = ScreenerService(data_db)

    # Use override sort parameters if provided, otherwise use template defaults
    effective_sort_by = sort_by if sort_by else template.sort_by
    effective_sort_order = SortOrder(sort_order) if sort_order else template.sort_order

    results, total_count = screener.run_screen(
        filters=template.filters,
        universe=template.universe,
        columns=template.default_columns,
        sort_by=effective_sort_by,
        sort_order=effective_sort_order,
        limit=limit,
        offset=offset,
        skip_count=not include_count,  # Skip count by default for faster response
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Convert results to StockResult objects
    stock_results = [StockResult(**r) for r in results]

    return ScreenResponse(
        total_count=total_count,
        returned_count=len(stock_results),
        offset=offset,
        limit=limit,
        results=stock_results,
        execution_time_ms=execution_time_ms
    )
