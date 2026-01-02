"""
Feature Registry for Stock Screener

Maps feature keys to their source tables, columns, and metadata.
This is the single source of truth for all screening features.

Categories:
- identity: Symbol, name, sector, industry, etc.
- price: Current price, price change
- valuation: P/E, P/B, EV/EBITDA, etc.
- profitability: ROE, ROA, margins, etc.
- leverage: Debt ratios, current ratio, etc.
- dividend: Yield, payout ratio, etc.
- per_share: EPS, book value per share, etc.
- financial: Revenue, net income, etc.
- ownership: Institutional ownership
- insider: Insider trading activity
- analyst: Price targets, estimates
- volume: Volume, average volume
- market_cap: Market cap, enterprise value
- risk: Beta
"""

from typing import Dict, List, Optional, Any


# =============================================================================
# Feature Registry - All 97 Ready Features
# =============================================================================

FEATURE_REGISTRY: Dict[str, Dict[str, Any]] = {

    # =========================================================================
    # Category: Identity & Classification (12 features)
    # =========================================================================

    "symbol": {
        "name": "Symbol",
        "category": "identity",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "symbol",
        "data_type": "string",
        "description": "Stock ticker symbol",
    },
    "company_name": {
        "name": "Company Name",
        "category": "identity",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "name",
        "data_type": "string",
        "description": "Company name",
    },
    "sector": {
        "name": "Sector",
        "category": "identity",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "sector",
        "data_type": "string",
        "description": "GICS sector classification",
    },
    "industry": {
        "name": "Industry",
        "category": "identity",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "industry",
        "data_type": "string",
        "description": "Industry classification",
    },
    "country": {
        "name": "Country",
        "category": "identity",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "country",
        "data_type": "string",
        "description": "Country of incorporation",
    },
    "exchange": {
        "name": "Exchange",
        "category": "identity",
        "source_table": "company_profile_bulk",
        "source_column": "exchange",
        "data_type": "string",
        "description": "Stock exchange (NYSE, NASDAQ, etc.)",
    },
    "ipo_year": {
        "name": "IPO Year",
        "category": "identity",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "ipo_year",
        "data_type": "number",
        "description": "Year of initial public offering",
    },
    "is_etf": {
        "name": "Is ETF",
        "category": "identity",
        "source_table": "company_profile_bulk",
        "source_column": "is_etf",
        "data_type": "boolean",
        "description": "Whether the security is an ETF",
    },
    "is_adr": {
        "name": "Is ADR",
        "category": "identity",
        "source_table": "company_profile_bulk",
        "source_column": "is_adr",
        "data_type": "boolean",
        "description": "Whether the security is an ADR",
    },
    "is_fund": {
        "name": "Is Fund",
        "category": "identity",
        "source_table": "company_profile_bulk",
        "source_column": "is_fund",
        "data_type": "boolean",
        "description": "Whether the security is a fund",
    },
    "is_actively_trading": {
        "name": "Is Actively Trading",
        "category": "identity",
        "source_table": "company_profile_bulk",
        "source_column": "is_actively_trading",
        "data_type": "boolean",
        "description": "Whether the stock is actively trading",
    },
    "peers": {
        "name": "Peer Group",
        "category": "identity",
        "source_table": "peers_bulk",
        "source_column": "peers_list",
        "data_type": "string",
        "description": "Comma-separated list of peer symbols",
    },

    # =========================================================================
    # Category: Price (3 ready features)
    # =========================================================================

    "price": {
        "name": "Price",
        "category": "price",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "last_sale",
        "data_type": "number",
        "unit": "dollars",
        "description": "Last sale price",
    },
    "price_change": {
        "name": "Price Change ($)",
        "category": "price",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "net_change",
        "data_type": "number",
        "unit": "dollars",
        "description": "Net price change in dollars",
    },
    "price_change_pct": {
        "name": "Price Change (%)",
        "category": "price",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "percent_change",
        "data_type": "number",
        "unit": "percent",
        "description": "Percent price change",
    },

    # =========================================================================
    # Category: Volume & Liquidity (2 ready features)
    # =========================================================================

    "volume": {
        "name": "Volume",
        "category": "volume",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "volume",
        "data_type": "number",
        "description": "Trading volume",
    },
    "avg_volume": {
        "name": "Average Volume",
        "category": "volume",
        "source_table": "company_profile_bulk",
        "source_column": "average_volume",
        "data_type": "number",
        "description": "Average daily trading volume",
    },

    # =========================================================================
    # Category: Market Cap & Size (3 ready features)
    # =========================================================================

    "market_cap": {
        "name": "Market Cap",
        "category": "market_cap",
        "source_table": "nasdaq_screener_profiles",
        "source_column": "market_cap",
        "data_type": "number",
        "unit": "dollars",
        "description": "Market capitalization",
    },
    "enterprise_value": {
        "name": "Enterprise Value",
        "category": "market_cap",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "enterprise_value_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Enterprise value (market cap + debt - cash)",
    },
    "shares_outstanding": {
        "name": "Shares Outstanding",
        "category": "market_cap",
        "source_table": "enterprise_values",
        "source_column": "number_of_shares",
        "data_type": "number",
        "description": "Total shares outstanding",
    },

    # =========================================================================
    # Category: Risk & Volatility (1 ready feature)
    # =========================================================================

    "beta": {
        "name": "Beta",
        "category": "risk",
        "source_table": "company_profile_bulk",
        "source_column": "beta",
        "data_type": "number",
        "description": "Beta coefficient (market sensitivity)",
    },

    # =========================================================================
    # Category: Valuation Ratios (14 features)
    # =========================================================================

    "pe_ratio_ttm": {
        "name": "P/E Ratio (TTM)",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_earnings_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price to earnings ratio (trailing twelve months)",
        "lower_is_better": True,
    },
    "forward_pe": {
        "name": "Forward P/E",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "forward_price_to_earnings_growth_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Forward price to earnings ratio",
        "lower_is_better": True,
    },
    "peg_ratio": {
        "name": "PEG Ratio",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_earnings_growth_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price/earnings to growth ratio",
        "lower_is_better": True,
    },
    "pb_ratio": {
        "name": "P/B Ratio",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_book_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price to book ratio",
        "lower_is_better": True,
    },
    "ps_ratio": {
        "name": "P/S Ratio",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_sales_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price to sales ratio",
        "lower_is_better": True,
    },
    "price_to_fcf": {
        "name": "P/FCF Ratio",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_free_cash_flow_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price to free cash flow ratio",
        "lower_is_better": True,
    },
    "price_to_ocf": {
        "name": "P/OCF Ratio",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_operating_cash_flow_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price to operating cash flow ratio",
        "lower_is_better": True,
    },
    "ev_to_ebitda": {
        "name": "EV/EBITDA",
        "category": "valuation",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "ev_to_ebitda_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Enterprise value to EBITDA",
        "lower_is_better": True,
    },
    "ev_to_sales": {
        "name": "EV/Sales",
        "category": "valuation",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "ev_to_sales_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Enterprise value to sales",
        "lower_is_better": True,
    },
    "ev_to_fcf": {
        "name": "EV/FCF",
        "category": "valuation",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "ev_to_free_cash_flow_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Enterprise value to free cash flow",
        "lower_is_better": True,
    },
    "earnings_yield": {
        "name": "Earnings Yield",
        "category": "valuation",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "earnings_yield_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Earnings yield (inverse of P/E)",
        "lower_is_better": False,
    },
    "fcf_yield": {
        "name": "FCF Yield",
        "category": "valuation",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "free_cash_flow_yield_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Free cash flow yield",
        "lower_is_better": False,
    },
    "price_to_fair_value": {
        "name": "Price to Fair Value",
        "category": "valuation",
        "source_table": "ratios_ttm_bulk",
        "source_column": "price_to_fair_value_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Price relative to estimated fair value",
        "lower_is_better": True,
    },
    "graham_number": {
        "name": "Graham Number",
        "category": "valuation",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "graham_number_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Benjamin Graham's intrinsic value estimate",
    },

    # =========================================================================
    # Category: Profitability Ratios (10 features)
    # =========================================================================

    "gross_margin": {
        "name": "Gross Margin",
        "category": "profitability",
        "source_table": "ratios_ttm_bulk",
        "source_column": "gross_profit_margin_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Gross profit margin",
        "lower_is_better": False,
    },
    "operating_margin": {
        "name": "Operating Margin",
        "category": "profitability",
        "source_table": "ratios_ttm_bulk",
        "source_column": "operating_profit_margin_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Operating profit margin",
        "lower_is_better": False,
    },
    "ebit_margin": {
        "name": "EBIT Margin",
        "category": "profitability",
        "source_table": "ratios_ttm_bulk",
        "source_column": "ebit_margin_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "EBIT margin",
        "lower_is_better": False,
    },
    "ebitda_margin": {
        "name": "EBITDA Margin",
        "category": "profitability",
        "source_table": "ratios_ttm_bulk",
        "source_column": "ebitda_margin_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "EBITDA margin",
        "lower_is_better": False,
    },
    "net_profit_margin": {
        "name": "Net Profit Margin",
        "category": "profitability",
        "source_table": "ratios_ttm_bulk",
        "source_column": "net_profit_margin_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Net profit margin",
        "lower_is_better": False,
    },
    "roe": {
        "name": "Return on Equity",
        "category": "profitability",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "return_on_equity_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Return on equity",
        "lower_is_better": False,
    },
    "roa": {
        "name": "Return on Assets",
        "category": "profitability",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "return_on_assets_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Return on assets",
        "lower_is_better": False,
    },
    "roic": {
        "name": "Return on Invested Capital",
        "category": "profitability",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "return_on_invested_capital_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Return on invested capital",
        "lower_is_better": False,
    },
    "roce": {
        "name": "Return on Capital Employed",
        "category": "profitability",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "return_on_capital_employed_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Return on capital employed",
        "lower_is_better": False,
    },
    "asset_turnover": {
        "name": "Asset Turnover",
        "category": "profitability",
        "source_table": "ratios_ttm_bulk",
        "source_column": "asset_turnover_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Asset turnover ratio",
        "lower_is_better": False,
    },

    # =========================================================================
    # Category: Leverage & Financial Health (9 features)
    # =========================================================================

    "debt_to_equity": {
        "name": "Debt to Equity",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "debt_to_equity_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Total debt to equity ratio",
        "lower_is_better": True,
    },
    "debt_to_assets": {
        "name": "Debt to Assets",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "debt_to_assets_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Total debt to assets ratio",
        "lower_is_better": True,
    },
    "debt_to_capital": {
        "name": "Debt to Capital",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "debt_to_capital_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Total debt to capital ratio",
        "lower_is_better": True,
    },
    "net_debt_to_ebitda": {
        "name": "Net Debt to EBITDA",
        "category": "leverage",
        "source_table": "key_metrics_ttm_bulk",
        "source_column": "net_debt_to_ebitda_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Net debt to EBITDA ratio",
        "lower_is_better": True,
    },
    "current_ratio": {
        "name": "Current Ratio",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "current_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Current assets to current liabilities",
        "lower_is_better": False,
    },
    "quick_ratio": {
        "name": "Quick Ratio",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "quick_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Quick assets to current liabilities",
        "lower_is_better": False,
    },
    "cash_ratio": {
        "name": "Cash Ratio",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "cash_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Cash to current liabilities",
        "lower_is_better": False,
    },
    "interest_coverage": {
        "name": "Interest Coverage",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "interest_coverage_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "EBIT to interest expense",
        "lower_is_better": False,
    },
    "financial_leverage": {
        "name": "Financial Leverage",
        "category": "leverage",
        "source_table": "ratios_ttm_bulk",
        "source_column": "financial_leverage_ratio_ttm",
        "data_type": "number",
        "unit": "ratio",
        "description": "Assets to equity ratio",
        "lower_is_better": True,
    },

    # =========================================================================
    # Category: Dividend Features (4 features)
    # =========================================================================

    "dividend_yield": {
        "name": "Dividend Yield",
        "category": "dividend",
        "source_table": "ratios_ttm_bulk",
        "source_column": "dividend_yield_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Annual dividend yield",
        "lower_is_better": False,
    },
    "dividend_per_share": {
        "name": "Dividend Per Share",
        "category": "dividend",
        "source_table": "ratios_ttm_bulk",
        "source_column": "dividend_per_share_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Annual dividend per share",
    },
    "payout_ratio": {
        "name": "Payout Ratio",
        "category": "dividend",
        "source_table": "ratios_ttm_bulk",
        "source_column": "dividend_payout_ratio_ttm",
        "data_type": "number",
        "unit": "percent",
        "description": "Dividend payout ratio",
    },
    "last_dividend": {
        "name": "Last Dividend",
        "category": "dividend",
        "source_table": "company_profile_bulk",
        "source_column": "last_dividend",
        "data_type": "number",
        "unit": "dollars",
        "description": "Most recent dividend payment",
    },

    # =========================================================================
    # Category: Per Share Metrics (6 features)
    # =========================================================================

    "eps_diluted": {
        "name": "EPS (Diluted)",
        "category": "per_share",
        "source_table": "income_statements",
        "source_column": "eps_diluted",
        "data_type": "number",
        "unit": "dollars",
        "description": "Diluted earnings per share",
    },
    "revenue_per_share": {
        "name": "Revenue Per Share",
        "category": "per_share",
        "source_table": "ratios_ttm_bulk",
        "source_column": "revenue_per_share_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Revenue per share",
    },
    "book_value_per_share": {
        "name": "Book Value Per Share",
        "category": "per_share",
        "source_table": "ratios_ttm_bulk",
        "source_column": "book_value_per_share_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Book value per share",
    },
    "cash_per_share": {
        "name": "Cash Per Share",
        "category": "per_share",
        "source_table": "ratios_ttm_bulk",
        "source_column": "cash_per_share_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Cash per share",
    },
    "fcf_per_share": {
        "name": "FCF Per Share",
        "category": "per_share",
        "source_table": "ratios_ttm_bulk",
        "source_column": "free_cash_flow_per_share_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Free cash flow per share",
    },
    "tangible_book_value_per_share": {
        "name": "Tangible Book Value Per Share",
        "category": "per_share",
        "source_table": "ratios_ttm_bulk",
        "source_column": "tangible_book_value_per_share_ttm",
        "data_type": "number",
        "unit": "dollars",
        "description": "Tangible book value per share",
    },

    # =========================================================================
    # Category: Financial Statement Items (13 features)
    # =========================================================================

    "revenue": {
        "name": "Revenue",
        "category": "financial",
        "source_table": "income_statements",
        "source_column": "revenue",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total revenue",
    },
    "gross_profit": {
        "name": "Gross Profit",
        "category": "financial",
        "source_table": "income_statements",
        "source_column": "gross_profit",
        "data_type": "number",
        "unit": "dollars",
        "description": "Gross profit",
    },
    "operating_income": {
        "name": "Operating Income",
        "category": "financial",
        "source_table": "income_statements",
        "source_column": "operating_income",
        "data_type": "number",
        "unit": "dollars",
        "description": "Operating income",
    },
    "ebitda": {
        "name": "EBITDA",
        "category": "financial",
        "source_table": "income_statements",
        "source_column": "ebitda",
        "data_type": "number",
        "unit": "dollars",
        "description": "Earnings before interest, taxes, depreciation, and amortization",
    },
    "net_income": {
        "name": "Net Income",
        "category": "financial",
        "source_table": "income_statements",
        "source_column": "net_income",
        "data_type": "number",
        "unit": "dollars",
        "description": "Net income",
    },
    "total_assets": {
        "name": "Total Assets",
        "category": "financial",
        "source_table": "balance_sheets",
        "source_column": "total_assets",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total assets",
    },
    "total_liabilities": {
        "name": "Total Liabilities",
        "category": "financial",
        "source_table": "balance_sheets",
        "source_column": "total_liabilities",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total liabilities",
    },
    "total_equity": {
        "name": "Total Equity",
        "category": "financial",
        "source_table": "balance_sheets",
        "source_column": "total_stockholders_equity",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total stockholders equity",
    },
    "total_debt": {
        "name": "Total Debt",
        "category": "financial",
        "source_table": "balance_sheets",
        "source_column": "total_debt",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total debt",
    },
    "cash_and_equivalents": {
        "name": "Cash & Equivalents",
        "category": "financial",
        "source_table": "balance_sheets",
        "source_column": "cash_and_cash_equivalents",
        "data_type": "number",
        "unit": "dollars",
        "description": "Cash and cash equivalents",
    },
    "operating_cash_flow": {
        "name": "Operating Cash Flow",
        "category": "financial",
        "source_table": "cash_flows",
        "source_column": "operating_cash_flow",
        "data_type": "number",
        "unit": "dollars",
        "description": "Cash flow from operations",
    },
    "free_cash_flow": {
        "name": "Free Cash Flow",
        "category": "financial",
        "source_table": "cash_flows",
        "source_column": "free_cash_flow",
        "data_type": "number",
        "unit": "dollars",
        "description": "Free cash flow",
    },
    "capex": {
        "name": "Capital Expenditures",
        "category": "financial",
        "source_table": "cash_flows",
        "source_column": "capital_expenditure",
        "data_type": "number",
        "unit": "dollars",
        "description": "Capital expenditures",
    },

    # =========================================================================
    # Category: Ownership Features (8 features)
    # =========================================================================

    "institutional_ownership_pct": {
        "name": "Institutional Ownership %",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "ownership_percent",
        "data_type": "number",
        "unit": "percent",
        "description": "Percentage owned by institutions",
    },
    "institutional_ownership_change": {
        "name": "Institutional Ownership Change",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "ownership_percent_change",
        "data_type": "number",
        "unit": "percent",
        "description": "Change in institutional ownership",
    },
    "institutional_holders_count": {
        "name": "# Institutional Holders",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "investors_holding",
        "data_type": "number",
        "description": "Number of institutional holders",
    },
    "new_positions": {
        "name": "New Positions",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "new_positions",
        "data_type": "number",
        "description": "Number of new institutional positions",
    },
    "increased_positions": {
        "name": "Increased Positions",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "increased_positions",
        "data_type": "number",
        "description": "Number of increased positions",
    },
    "closed_positions": {
        "name": "Closed Positions",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "closed_positions",
        "data_type": "number",
        "description": "Number of closed positions",
    },
    "reduced_positions": {
        "name": "Reduced Positions",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "reduced_positions",
        "data_type": "number",
        "description": "Number of reduced positions",
    },
    "put_call_ratio": {
        "name": "Put/Call Ratio",
        "category": "ownership",
        "source_table": "institutional_ownership",
        "source_column": "put_call_ratio",
        "data_type": "number",
        "unit": "ratio",
        "description": "Institutional put/call ratio",
    },

    # =========================================================================
    # Category: Insider Trading Features (6 features)
    # =========================================================================

    "insider_buy_sell_ratio": {
        "name": "Insider Buy/Sell Ratio",
        "category": "insider",
        "source_table": "insider_statistics",
        "source_column": "acquired_disposed_ratio",
        "data_type": "number",
        "unit": "ratio",
        "description": "Ratio of insider buys to sells",
        "lower_is_better": False,
    },
    "insider_total_purchases": {
        "name": "Total Insider Purchases ($)",
        "category": "insider",
        "source_table": "insider_statistics",
        "source_column": "total_purchases",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total value of insider purchases",
    },
    "insider_total_sales": {
        "name": "Total Insider Sales ($)",
        "category": "insider",
        "source_table": "insider_statistics",
        "source_column": "total_sales",
        "data_type": "number",
        "unit": "dollars",
        "description": "Total value of insider sales",
    },
    "insider_buy_transactions": {
        "name": "# Buy Transactions",
        "category": "insider",
        "source_table": "insider_statistics",
        "source_column": "acquired_transactions",
        "data_type": "number",
        "description": "Number of insider buy transactions",
    },
    "insider_sell_transactions": {
        "name": "# Sell Transactions",
        "category": "insider",
        "source_table": "insider_statistics",
        "source_column": "disposed_transactions",
        "data_type": "number",
        "description": "Number of insider sell transactions",
    },
    "insider_shares_transacted": {
        "name": "Insider Shares Transacted",
        "category": "insider",
        "source_table": "insider_statistics",
        "source_column": "total_shares_transacted",
        "data_type": "number",
        "description": "Total shares transacted by insiders",
    },

    # =========================================================================
    # Category: Analyst Features (6 features)
    # =========================================================================

    "price_target_high": {
        "name": "Price Target High",
        "category": "analyst",
        "source_table": "price_target_summary_bulk",
        "source_column": "last_month_avg_price_target",
        "data_type": "number",
        "unit": "dollars",
        "description": "Highest analyst price target",
    },
    "analyst_count_month": {
        "name": "# Analysts (Month)",
        "category": "analyst",
        "source_table": "price_target_summary_bulk",
        "source_column": "last_month_count",
        "data_type": "number",
        "description": "Number of analysts with targets this month",
    },
    "analyst_count_quarter": {
        "name": "# Analysts (Quarter)",
        "category": "analyst",
        "source_table": "price_target_summary_bulk",
        "source_column": "last_quarter_count",
        "data_type": "number",
        "description": "Number of analysts with targets this quarter",
    },
    "analyst_count_year": {
        "name": "# Analysts (Year)",
        "category": "analyst",
        "source_table": "price_target_summary_bulk",
        "source_column": "last_year_count",
        "data_type": "number",
        "description": "Number of analysts with targets this year",
    },
    "eps_estimate_avg": {
        "name": "EPS Estimate (Avg)",
        "category": "analyst",
        "source_table": "analyst_estimates",
        "source_column": "eps_avg",
        "data_type": "number",
        "unit": "dollars",
        "description": "Average analyst EPS estimate",
    },
    "revenue_estimate_avg": {
        "name": "Revenue Estimate (Avg)",
        "category": "analyst",
        "source_table": "analyst_estimates",
        "source_column": "revenue_avg",
        "data_type": "number",
        "unit": "dollars",
        "description": "Average analyst revenue estimate",
    },

    # =========================================================================
    # Category: Computed - 52 Week Stats (4 features)
    # =========================================================================

    "high_52w": {
        "name": "52-Week High",
        "category": "price_computed",
        "data_type": "number",
        "unit": "dollars",
        "description": "52-week high price",
        "computed": True,
        "source_table": "prices_daily",
    },
    "low_52w": {
        "name": "52-Week Low",
        "category": "price_computed",
        "data_type": "number",
        "unit": "dollars",
        "description": "52-week low price",
        "computed": True,
        "source_table": "prices_daily",
    },
    "pct_from_high": {
        "name": "% From 52-Week High",
        "category": "price_computed",
        "data_type": "number",
        "unit": "percent",
        "description": "Percentage below 52-week high (negative values)",
        "computed": True,
        "source_table": "prices_daily",
        "lower_is_better": False,
    },
    "pct_from_low": {
        "name": "% From 52-Week Low",
        "category": "price_computed",
        "data_type": "number",
        "unit": "percent",
        "description": "Percentage above 52-week low",
        "computed": True,
        "source_table": "prices_daily",
        "lower_is_better": False,
    },

    # =========================================================================
    # Category: Computed - Returns (7 features)
    # =========================================================================

    "return_1d": {
        "name": "1-Day Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "1-day price return",
        "computed": True,
        "source_table": "prices_daily",
    },
    "return_1w": {
        "name": "1-Week Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "1-week (5 trading days) return",
        "computed": True,
        "source_table": "prices_daily",
    },
    "return_1m": {
        "name": "1-Month Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "1-month (~21 trading days) return",
        "computed": True,
        "source_table": "prices_daily",
    },
    "return_3m": {
        "name": "3-Month Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "3-month (~63 trading days) return",
        "computed": True,
        "source_table": "prices_daily",
    },
    "return_6m": {
        "name": "6-Month Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "6-month (~126 trading days) return",
        "computed": True,
        "source_table": "prices_daily",
    },
    "return_ytd": {
        "name": "YTD Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "Year-to-date return",
        "computed": True,
        "source_table": "prices_daily",
    },
    "return_1y": {
        "name": "1-Year Return",
        "category": "returns",
        "data_type": "number",
        "unit": "percent",
        "description": "1-year (~252 trading days) return",
        "computed": True,
        "source_table": "prices_daily",
    },

    # =========================================================================
    # Category: Computed - Derived Metrics (2 features)
    # =========================================================================

    "relative_volume": {
        "name": "Relative Volume",
        "category": "volume",
        "data_type": "number",
        "unit": "ratio",
        "description": "Today's volume / average volume",
        "computed": True,
        "inline_compute": True,  # Can be computed inline in SQL
    },
    "price_target_upside": {
        "name": "Price Target Upside %",
        "category": "analyst",
        "data_type": "number",
        "unit": "percent",
        "description": "Upside to analyst price target",
        "computed": True,
        "inline_compute": True,  # Can be computed inline in SQL
    },
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_feature(key: str) -> Optional[Dict[str, Any]]:
    """Get feature metadata by key"""
    return FEATURE_REGISTRY.get(key)


def get_features_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all features in a category"""
    return [
        {"key": k, **v}
        for k, v in FEATURE_REGISTRY.items()
        if v.get("category") == category
    ]


def get_all_categories() -> List[str]:
    """Get list of all unique categories"""
    return list(set(f.get("category") for f in FEATURE_REGISTRY.values()))


def get_features_by_source_table(table_name: str) -> List[Dict[str, Any]]:
    """Get all features from a specific source table"""
    return [
        {"key": k, **v}
        for k, v in FEATURE_REGISTRY.items()
        if v.get("source_table") == table_name
    ]


def get_feature_count() -> int:
    """Get total number of features in registry"""
    return len(FEATURE_REGISTRY)
