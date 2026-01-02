"""Stock Screener schemas for API requests/responses"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class FilterOperator(str, Enum):
    """Supported filter operators"""
    EQ = "="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class FeatureCategory(str, Enum):
    """Feature categories for organization"""
    IDENTITY = "identity"
    PRICE = "price"
    RETURNS = "returns"
    VOLUME = "volume"
    MARKET_CAP = "market_cap"
    RISK = "risk"
    TECHNICAL = "technical"
    VALUATION = "valuation"
    PROFITABILITY = "profitability"
    LEVERAGE = "leverage"
    DIVIDEND = "dividend"
    PER_SHARE = "per_share"
    FINANCIAL = "financial"
    OWNERSHIP = "ownership"
    INSIDER = "insider"
    ANALYST = "analyst"


# =============================================================================
# Filter Schemas
# =============================================================================

class ScreenFilter(BaseModel):
    """Single filter criterion"""
    feature: str  # Feature key from registry, e.g., "pe_ratio_ttm"
    operator: FilterOperator
    value: Any  # Single value, list for IN, [min, max] for BETWEEN


class UniverseFilter(BaseModel):
    """Universe/base filtering constraints"""
    min_market_cap: Optional[float] = None  # Minimum market cap in dollars
    max_market_cap: Optional[float] = None
    sectors: Optional[List[str]] = None  # Include only these sectors
    industries: Optional[List[str]] = None
    exchanges: Optional[List[str]] = None  # NYSE, NASDAQ, etc.
    countries: Optional[List[str]] = None
    exclude_etfs: bool = True
    exclude_adrs: bool = False
    min_price: Optional[float] = None  # Minimum stock price
    min_volume: Optional[int] = None  # Minimum average volume


# =============================================================================
# Screen Request/Response Schemas
# =============================================================================

class ScreenRequest(BaseModel):
    """Request to run a stock screen"""
    universe: Optional[UniverseFilter] = None
    filters: List[ScreenFilter] = []
    columns: Optional[List[str]] = None  # Features to include in response
    sort_by: Optional[str] = "market_cap"
    sort_order: SortOrder = SortOrder.DESC
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class StockResult(BaseModel):
    """Single stock in screen results"""
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None

    # Price fields
    price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_pct: Optional[float] = None

    # Market data
    market_cap: Optional[int] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    exchange: Optional[str] = None

    # Risk
    beta: Optional[float] = None

    # Valuation ratios
    pe_ratio_ttm: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    earnings_yield: Optional[float] = None
    fcf_yield: Optional[float] = None

    # Profitability
    roe: Optional[float] = None
    roic: Optional[float] = None
    gross_margin: Optional[float] = None
    net_profit_margin: Optional[float] = None

    # Leverage
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None

    # Dividend
    dividend_yield: Optional[float] = None

    # Dynamic fields for additional columns
    data: Dict[str, Any] = {}  # Additional feature values

    class Config:
        extra = "allow"  # Allow extra fields from database


class ScreenResponse(BaseModel):
    """Response from running a screen"""
    total_count: int  # Total stocks matching filters
    returned_count: int  # Number returned in this page
    offset: int
    limit: int
    results: List[StockResult]
    execution_time_ms: int


# =============================================================================
# Saved Screen Schemas
# =============================================================================

class SavedScreenCreate(BaseModel):
    """Create a new saved screen"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    filters: List[ScreenFilter] = []
    universe: Optional[UniverseFilter] = None
    columns: Optional[List[str]] = None
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.DESC


class SavedScreenUpdate(BaseModel):
    """Update an existing saved screen"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    filters: Optional[List[ScreenFilter]] = None
    universe: Optional[UniverseFilter] = None
    columns: Optional[List[str]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[SortOrder] = None


class SavedScreenResponse(BaseModel):
    """Saved screen response"""
    screen_id: str
    user_id: str
    name: str
    description: Optional[str]
    filters: List[Dict[str, Any]]
    universe: Optional[Dict[str, Any]]
    columns: Optional[List[str]]
    sort_by: Optional[str]
    sort_order: str
    is_template: bool
    template_key: Optional[str]
    last_run_at: Optional[datetime]
    run_count: int
    last_result_count: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedScreenSummary(BaseModel):
    """Summary for listing saved screens"""
    screen_id: str
    name: str
    description: Optional[str]
    filter_count: int
    is_template: bool
    template_key: Optional[str]
    last_run_at: Optional[datetime]
    run_count: int
    last_result_count: Optional[int]

    class Config:
        from_attributes = True


# =============================================================================
# Template Schemas
# =============================================================================

class ScreenTemplate(BaseModel):
    """Flagship screen template"""
    template_key: str
    name: str
    description: str
    category: str  # "value", "growth", "income", "momentum", etc.
    filters: List[ScreenFilter]
    universe: Optional[UniverseFilter] = None
    default_columns: List[str]
    sort_by: str
    sort_order: SortOrder = SortOrder.DESC


# =============================================================================
# Feature Registry Schemas
# =============================================================================

class FeatureInfo(BaseModel):
    """Metadata about a single feature"""
    key: str  # Unique identifier, e.g., "pe_ratio_ttm"
    name: str  # Display name, e.g., "P/E Ratio (TTM)"
    category: FeatureCategory
    description: Optional[str] = None
    source_table: str  # e.g., "ratios_ttm_bulk"
    source_column: str  # Actual column name in table
    data_type: Literal["number", "string", "boolean", "date"]
    unit: Optional[str] = None  # e.g., "ratio", "percent", "dollars"
    is_computed: bool = False  # True if needs calculation
    lower_is_better: Optional[bool] = None  # For sorting/ranking guidance
    null_handling: Literal["exclude", "include", "fill_zero", "fill_median"] = "exclude"


class FeatureListResponse(BaseModel):
    """Response with all available features"""
    total_count: int
    features: List[FeatureInfo]
    categories: List[str]


# =============================================================================
# Universe Metadata Schemas
# =============================================================================

class UniverseStats(BaseModel):
    """Statistics about the current stock universe"""
    total_stocks: int
    sectors: List[Dict[str, Any]]  # [{name: "Technology", count: 500}, ...]
    exchanges: List[Dict[str, Any]]
    market_cap_distribution: Dict[str, int]  # {"mega": 50, "large": 200, ...}


class SectorInfo(BaseModel):
    """Sector information"""
    name: str
    stock_count: int
    industries: List[str]
