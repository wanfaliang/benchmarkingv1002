# Module: Stocks

> **Status:** Planning Phase
> **Last Updated:** 2024-12-31
> **Replaces:** Screening.md (renamed for broader scope)

## Overview

The **Stocks** module is a comprehensive equity research and screening platform for Finexus. It provides institutional-grade stock analysis tools powered by the DATA project's extensive financial, market, and economic datasets.

### Module Capabilities

| Feature | Description | Phase |
|---------|-------------|-------|
| **Stock Screener** | Filter stocks by 100+ criteria | 1 |
| **Stock Detail** | Deep-dive into individual stocks | 2 |
| **Watchlists** | Save and track stock lists | 2 |
| **Comparisons** | Side-by-side stock comparison | 3 |
| **Alerts** | Price and metric-based alerts | Future |

---

## Data Access

This module reads data from the **DATA Project** database (read-only access).

### Database Connections

| Connection | Function | Database |
|------------|----------|----------|
| `get_db()` | Primary Finexus DB | Users, saved screens, watchlists |
| `get_data_db()` | DATA Project DB (read-only) | All stock/financial/economic data |

### DATA Project Location

- **Path:** `D:\finexus-data-collector`
- **Financial and Market Models:** `src/database/models.py`
- **BEA Models:** `src/databse/bea_models.py`
- **BLS Models:** `src/database/bls_models.py`
- **FRED Models:** `src/database/models_fred.py`
- **Treasury Models:** `src/database/treasury_models.py`
---

# Part 1: Stock Screener

## 1.1 Feature Categories

The screener supports **136 features** across 17 categories:
- **97 Ready** (direct from database)
- **32 Computed** (calculated from price history)
- **7 Missing** (requires new data collection)

---

## Category 1: Identity & Classification (12 features)

Base universe filtering - who is eligible for screening.

| Feature | Status | Source Table | Column |
|---------|--------|--------------|--------|
| Symbol | Ready | `nasdaq_screener_profiles` | `symbol` |
| Company Name | Ready | `nasdaq_screener_profiles` | `name` |
| Sector | Ready | `nasdaq_screener_profiles` | `sector` |
| Industry | Ready | `nasdaq_screener_profiles` | `industry` |
| Country | Ready | `nasdaq_screener_profiles` | `country` |
| Exchange | Ready | `company_profile_bulk` | `exchange` |
| IPO Year | Ready | `nasdaq_screener_profiles` | `ipo_year` |
| Is ETF | Ready | `company_profile_bulk` | `is_etf` |
| Is ADR | Ready | `company_profile_bulk` | `is_adr` |
| Is Fund | Ready | `company_profile_bulk` | `is_fund` |
| Is Actively Trading | Ready | `company_profile_bulk` | `is_actively_trading` |
| Peer Group | Ready | `peers_bulk` | `peers_list` |

### Screening Use Cases
- Filter by sector/industry
- US-only or international stocks
- Exclude ETFs, ADRs, funds
- Find peers of a specific stock

---

## Category 2: Price Features (11 features)

Current price and historical price levels.

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| Price (Last Sale) | Ready | `nasdaq_screener_profiles` | `last_sale` |
| Price Change ($) | Ready | `nasdaq_screener_profiles` | `net_change` |
| Price Change (%) | Ready | `nasdaq_screener_profiles` | `percent_change` |
| 52-Week Range | Ready | `company_profile_bulk` | `range` (text) |
| 52-Week High | Computed | `prices_daily` | MAX(adj_high) 252 days |
| 52-Week Low | Computed | `prices_daily` | MIN(adj_low) 252 days |
| % From 52-Week High | Computed | Derived | (price - high) / high |
| % From 52-Week Low | Computed | Derived | (price - low) / low |
| All-Time High | Computed | `prices_daily` | MAX(adj_high) all-time |
| All-Time High Date | Computed | `prices_daily` | Date of ATH |
| % From ATH | Computed | Derived | (price - ATH) / ATH |

### Screening Use Cases
- Stocks near 52-week highs (momentum)
- Stocks near 52-week lows (value/contrarian)
- Stocks at all-time highs (breakout)

---

## Category 3: Return/Performance Features (9 features)

Historical price returns over various periods.

| Feature | Status | Source | Calculation |
|---------|--------|--------|-------------|
| 1-Day Return | Computed | `prices_daily` | Close-to-close |
| 1-Week Return | Computed | `prices_daily` | 5 trading days |
| 1-Month Return | Computed | `prices_monthly` | 1 month ago |
| 3-Month Return | Computed | `prices_monthly` | 3 months ago |
| 6-Month Return | Computed | `prices_monthly` | 6 months ago |
| YTD Return | Computed | `prices_daily` | From Jan 1 |
| 1-Year Return | Computed | `prices_monthly` | 12 months ago |
| 3-Year Return | Computed | `prices_monthly` | 36 months ago |
| 5-Year Return | Computed | `prices_monthly` | 60 months ago |

### Screening Use Cases
- Momentum screens (top 6M/12M returns)
- Mean reversion (worst 1M performers)
- Long-term compounders

---

## Category 4: Volume & Liquidity Features (5 features)

Trading activity and liquidity metrics.

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| Volume (Today) | Ready | `nasdaq_screener_profiles` | `volume` |
| Average Volume | Ready | `company_profile_bulk` | `average_volume` |
| Relative Volume | Computed | Derived | volume / avg_volume |
| Dollar Volume | Computed | Derived | price * volume |
| Avg Dollar Volume | Computed | Derived | price * avg_volume |

### Screening Use Cases
- Minimum liquidity filters
- Unusual volume detection
- Institutional-size position capability

---

## Category 5: Market Cap & Size Features (5 features)

Company size metrics.

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| Market Cap | Ready | `nasdaq_screener_profiles` | `market_cap` |
| Market Cap Category | Computed | Derived | Mega/Large/Mid/Small/Micro |
| Enterprise Value | Ready | `key_metrics_ttm_bulk` | `enterprise_value_ttm` |
| Shares Outstanding | Ready | `enterprise_values` | `number_of_shares` |
| Float Shares | Missing | - | Need data collection |

### Market Cap Categories
| Category | Range |
|----------|-------|
| Mega Cap | > $200B |
| Large Cap | $10B - $200B |
| Mid Cap | $2B - $10B |
| Small Cap | $300M - $2B |
| Micro Cap | $50M - $300M |
| Nano Cap | < $50M |

---

## Category 6: Risk & Volatility Features (4 features)

Risk metrics and price volatility.

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| Beta | Ready | `company_profile_bulk` | `beta` |
| Volatility (30-day) | Computed | `prices_daily` | Std dev of returns |
| Volatility (90-day) | Computed | `prices_daily` | Std dev of returns |
| Max Drawdown (1Y) | Computed | `prices_daily` | Peak-to-trough |

### Screening Use Cases
- Low-beta defensive screens
- High-volatility trading opportunities
- Drawdown risk filters

---

## Category 7: Technical Indicators (7 features)

Price-based technical analysis indicators.

| Feature | Status | Source | Calculation |
|---------|--------|--------|-------------|
| RSI (14-day) | Computed | `prices_daily` | Standard RSI |
| SMA 20 | Computed | `prices_daily` | 20-day average |
| SMA 50 | Computed | `prices_daily` | 50-day average |
| SMA 200 | Computed | `prices_daily` | 200-day average |
| Price vs SMA 50 | Computed | Derived | price / SMA50 |
| Price vs SMA 200 | Computed | Derived | price / SMA200 |
| Golden Cross | Computed | Derived | SMA50 > SMA200 |

### Screening Use Cases
- Oversold stocks (RSI < 30)
- Overbought stocks (RSI > 70)
- Trend confirmation (above 200 SMA)
- Golden/Death cross signals

---

## Category 8: Valuation Ratios (14 features)

Price multiples and valuation metrics.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| P/E Ratio (TTM) | Ready | `ratios_ttm_bulk` | `price_to_earnings_ratio_ttm` |
| Forward P/E | Ready | `ratios_ttm_bulk` | `forward_price_to_earnings_growth_ratio_ttm` |
| PEG Ratio | Ready | `ratios_ttm_bulk` | `price_to_earnings_growth_ratio_ttm` |
| P/B Ratio | Ready | `ratios_ttm_bulk` | `price_to_book_ratio_ttm` |
| P/S Ratio | Ready | `ratios_ttm_bulk` | `price_to_sales_ratio_ttm` |
| P/FCF Ratio | Ready | `ratios_ttm_bulk` | `price_to_free_cash_flow_ratio_ttm` |
| P/OCF Ratio | Ready | `ratios_ttm_bulk` | `price_to_operating_cash_flow_ratio_ttm` |
| EV/EBITDA | Ready | `key_metrics_ttm_bulk` | `ev_to_ebitda_ttm` |
| EV/Sales | Ready | `key_metrics_ttm_bulk` | `ev_to_sales_ttm` |
| EV/FCF | Ready | `key_metrics_ttm_bulk` | `ev_to_free_cash_flow_ttm` |
| Earnings Yield | Ready | `key_metrics_ttm_bulk` | `earnings_yield_ttm` |
| FCF Yield | Ready | `key_metrics_ttm_bulk` | `free_cash_flow_yield_ttm` |
| Price to Fair Value | Ready | `ratios_ttm_bulk` | `price_to_fair_value_ttm` |
| Graham Number | Ready | `key_metrics_ttm_bulk` | `graham_number_ttm` |

### Screening Use Cases
- Deep value (low P/E, P/B)
- High FCF yield
- GARP (reasonable PEG)
- Cheap vs fair value

---

## Category 9: Profitability Ratios (10 features)

Margins and returns on capital.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| Gross Margin | Ready | `ratios_ttm_bulk` | `gross_profit_margin_ttm` |
| Operating Margin | Ready | `ratios_ttm_bulk` | `operating_profit_margin_ttm` |
| EBIT Margin | Ready | `ratios_ttm_bulk` | `ebit_margin_ttm` |
| EBITDA Margin | Ready | `ratios_ttm_bulk` | `ebitda_margin_ttm` |
| Net Profit Margin | Ready | `ratios_ttm_bulk` | `net_profit_margin_ttm` |
| ROE | Ready | `key_metrics_ttm_bulk` | `return_on_equity_ttm` |
| ROA | Ready | `key_metrics_ttm_bulk` | `return_on_assets_ttm` |
| ROIC | Ready | `key_metrics_ttm_bulk` | `return_on_invested_capital_ttm` |
| ROCE | Ready | `key_metrics_ttm_bulk` | `return_on_capital_employed_ttm` |
| Asset Turnover | Ready | `ratios_ttm_bulk` | `asset_turnover_ttm` |

### Screening Use Cases
- Quality screens (high ROE, ROIC)
- Margin expansion candidates
- Capital-efficient businesses

---

## Category 10: Leverage & Financial Health (9 features)

Debt levels and liquidity ratios.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| Debt/Equity | Ready | `ratios_ttm_bulk` | `debt_to_equity_ratio_ttm` |
| Debt/Assets | Ready | `ratios_ttm_bulk` | `debt_to_assets_ratio_ttm` |
| Debt/Capital | Ready | `ratios_ttm_bulk` | `debt_to_capital_ratio_ttm` |
| Net Debt/EBITDA | Ready | `key_metrics_ttm_bulk` | `net_debt_to_ebitda_ttm` |
| Current Ratio | Ready | `ratios_ttm_bulk` | `current_ratio_ttm` |
| Quick Ratio | Ready | `ratios_ttm_bulk` | `quick_ratio_ttm` |
| Cash Ratio | Ready | `ratios_ttm_bulk` | `cash_ratio_ttm` |
| Interest Coverage | Ready | `ratios_ttm_bulk` | `interest_coverage_ratio_ttm` |
| Financial Leverage | Ready | `ratios_ttm_bulk` | `financial_leverage_ratio_ttm` |

### Screening Use Cases
- Low-debt screens
- Bankruptcy risk avoidance
- Rate sensitivity screening

---

## Category 11: Dividend Features (4 features)

Dividend income metrics.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| Dividend Yield | Ready | `ratios_ttm_bulk` | `dividend_yield_ttm` |
| Dividend Per Share | Ready | `ratios_ttm_bulk` | `dividend_per_share_ttm` |
| Payout Ratio | Ready | `ratios_ttm_bulk` | `dividend_payout_ratio_ttm` |
| Last Dividend | Ready | `company_profile_bulk` | `last_dividend` |

### Screening Use Cases
- High-yield income screens
- Sustainable dividend (low payout)
- Dividend growth candidates

---

## Category 12: Per Share Metrics (6 features)

Fundamental values per share.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| EPS (Diluted) | Ready | `income_statements` | `eps_diluted` |
| Revenue Per Share | Ready | `ratios_ttm_bulk` | `revenue_per_share_ttm` |
| Book Value/Share | Ready | `ratios_ttm_bulk` | `book_value_per_share_ttm` |
| Cash Per Share | Ready | `ratios_ttm_bulk` | `cash_per_share_ttm` |
| FCF Per Share | Ready | `ratios_ttm_bulk` | `free_cash_flow_per_share_ttm` |
| Tangible BV/Share | Ready | `ratios_ttm_bulk` | `tangible_book_value_per_share_ttm` |

---

## Category 13: Financial Statement Items (13 features)

Key line items from financial statements.

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| Revenue | Ready | `income_statements` | Latest FY |
| Gross Profit | Ready | `income_statements` | Latest FY |
| Operating Income | Ready | `income_statements` | Latest FY |
| EBITDA | Ready | `income_statements` | Latest FY |
| Net Income | Ready | `income_statements` | Latest FY |
| Total Assets | Ready | `balance_sheets` | Latest |
| Total Liabilities | Ready | `balance_sheets` | Latest |
| Total Equity | Ready | `balance_sheets` | Latest |
| Total Debt | Ready | `balance_sheets` | Latest |
| Cash & Equivalents | Ready | `balance_sheets` | Latest |
| Operating Cash Flow | Ready | `cash_flows` | Latest FY |
| Free Cash Flow | Ready | `cash_flows` | Latest FY |
| CapEx | Ready | `cash_flows` | Latest FY |

---

## Category 14: Ownership Features (8 features)

Institutional ownership data.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| Institutional Ownership % | Ready | `institutional_ownership` | `ownership_percent` |
| Ownership Change % | Ready | `institutional_ownership` | `ownership_percent_change` |
| # Institutional Holders | Ready | `institutional_ownership` | `investors_holding` |
| New Positions | Ready | `institutional_ownership` | `new_positions` |
| Increased Positions | Ready | `institutional_ownership` | `increased_positions` |
| Closed Positions | Ready | `institutional_ownership` | `closed_positions` |
| Reduced Positions | Ready | `institutional_ownership` | `reduced_positions` |
| Put/Call Ratio | Ready | `institutional_ownership` | `put_call_ratio` |

### Screening Use Cases
- Institutional accumulation
- Under-owned opportunities
- Smart money tracking

---

## Category 15: Insider Trading Features (6 features)

Corporate insider activity.

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| Buy/Sell Ratio | Ready | `insider_statistics` | `acquired_disposed_ratio` |
| Total Purchases ($) | Ready | `insider_statistics` | `total_purchases` |
| Total Sales ($) | Ready | `insider_statistics` | `total_sales` |
| # Buy Transactions | Ready | `insider_statistics` | `acquired_transactions` |
| # Sell Transactions | Ready | `insider_statistics` | `disposed_transactions` |
| Recent Trades | Ready | `insider_trading` | Individual records |

### Screening Use Cases
- Insider buying signals
- Cluster buys detection
- Management confidence

---

## Category 16: Analyst Features (7 features)

Analyst estimates and price targets.

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| Price Target High | Ready | `price_targets` | `target_high` |
| Price Target Low | Ready | `price_targets` | `target_low` |
| Price Target Consensus | Ready | `price_targets` | `target_consensus` |
| Price Target Upside % | Computed | Derived | (target - price) / price |
| # Analysts (Month) | Ready | `price_target_summary_bulk` | `last_month_count` |
| EPS Estimate | Ready | `analyst_estimates` | `eps_avg` |
| Analyst Rating | Missing | - | Need Buy/Hold/Sell data |

### Screening Use Cases
- High upside to target
- Earnings surprise candidates
- Under-covered stocks

---

## Category 17: Short Interest Features (5 features)

Short selling data. **All features require new data collection.**

| Feature | Status | Notes |
|---------|--------|-------|
| Short Interest | Missing | Shares sold short |
| Short % of Float | Missing | Short / Float |
| Short % of Outstanding | Missing | Short / Outstanding |
| Days to Cover | Missing | Short / Avg Volume |
| Short Interest Change | Missing | Period-over-period change |

### Future Use Cases
- Short squeeze candidates
- Crowded shorts
- Bearish sentiment

---

# Part 2: Flagship Screens

Pre-built screening strategies using combinations of features above.

## Screen 1: Deep Value

**Philosophy:** Find stocks trading at significant discounts to intrinsic value.

| Criteria | Operator | Value |
|----------|----------|-------|
| P/E Ratio | < | 15 |
| P/B Ratio | < | 1.5 |
| EV/EBITDA | < | 8 |
| Earnings Yield | > | 8% |
| Debt/Equity | < | 1.0 |
| Market Cap | > | $500M |

---

## Screen 2: Quality Compounders

**Philosophy:** High-quality businesses with durable competitive advantages.

| Criteria | Operator | Value |
|----------|----------|-------|
| ROE | > | 15% |
| ROIC | > | 12% |
| Gross Margin | > | 40% |
| Net Profit Margin | > | 10% |
| Debt/Equity | < | 0.5 |
| 5-Year Revenue CAGR | > | 5% |

---

## Screen 3: GARP (Growth at Reasonable Price)

**Philosophy:** Growth stocks that aren't overvalued.

| Criteria | Operator | Value |
|----------|----------|-------|
| Revenue Growth (YoY) | > | 15% |
| EPS Growth (YoY) | > | 15% |
| PEG Ratio | < | 1.5 |
| P/E Ratio | < | 30 |
| ROE | > | 12% |

---

## Screen 4: Dividend Aristocrats Clone

**Philosophy:** High-quality dividend payers with sustainable yields.

| Criteria | Operator | Value |
|----------|----------|-------|
| Dividend Yield | > | 2% |
| Dividend Yield | < | 8% |
| Payout Ratio | < | 70% |
| Debt/Equity | < | 1.0 |
| FCF Yield | > | 4% |
| Market Cap | > | $2B |

---

## Screen 5: Momentum Leaders

**Philosophy:** Stocks with strong price momentum.

| Criteria | Operator | Value |
|----------|----------|-------|
| 6-Month Return | > | 20% |
| 12-Month Return | > | 30% |
| % From 52-Week High | > | -10% |
| Relative Volume | > | 1.0 |
| Price vs SMA 200 | > | 1.0 |
| Market Cap | > | $1B |

---

## Screen 6: Fallen Angels

**Philosophy:** Quality stocks that have sold off significantly.

| Criteria | Operator | Value |
|----------|----------|-------|
| % From 52-Week High | < | -30% |
| ROE | > | 10% |
| Current Ratio | > | 1.5 |
| Interest Coverage | > | 3 |
| Institutional Ownership | > | 20% |

---

## Screen 7: Small Cap Growth

**Philosophy:** Fast-growing smaller companies.

| Criteria | Operator | Value |
|----------|----------|-------|
| Market Cap | > | $300M |
| Market Cap | < | $2B |
| Revenue Growth (YoY) | > | 20% |
| Gross Margin | > | 35% |
| ROE | > | 10% |

---

## Screen 8: Low Volatility Dividend

**Philosophy:** Defensive, income-generating stocks.

| Criteria | Operator | Value |
|----------|----------|-------|
| Beta | < | 0.8 |
| Dividend Yield | > | 2.5% |
| Payout Ratio | < | 60% |
| Debt/Equity | < | 0.8 |
| Volatility (90-day) | < | 25% |

---

## Screen 9: Insider Buying

**Philosophy:** Follow corporate insider purchases.

| Criteria | Operator | Value |
|----------|----------|-------|
| Buy/Sell Ratio | > | 2.0 |
| # Buy Transactions (Qtr) | > | 3 |
| Total Purchases ($) | > | $100,000 |
| Market Cap | > | $500M |

---

## Screen 10: Analyst Upgrade Candidates

**Philosophy:** Stocks with significant upside to price targets.

| Criteria | Operator | Value |
|----------|----------|-------|
| Price Target Upside % | > | 30% |
| # Analysts | > | 5 |
| ROE | > | 10% |
| Debt/Equity | < | 1.0 |

---

## Screen 11: Recession Resistant

**Philosophy:** Defensive stocks for economic downturns.

| Criteria | Operator | Value |
|----------|----------|-------|
| Sector | IN | Consumer Staples, Healthcare, Utilities |
| Beta | < | 0.8 |
| Dividend Yield | > | 2% |
| Current Ratio | > | 1.5 |
| Debt/Equity | < | 0.7 |
| FCF Yield | > | 5% |

---

## Screen 12: Rate Cut Beneficiaries

**Philosophy:** Stocks that benefit from falling interest rates.

| Criteria | Operator | Value |
|----------|----------|-------|
| Sector | IN | Real Estate, Utilities, Financials |
| Dividend Yield | > | 3% |
| Net Debt/EBITDA | > | 2 |
| P/E Ratio | < | 20 |

---

# Part 3: Module Architecture

## Backend Structure

```
backend/app/
├── api/
│   └── stocks/
│       ├── __init__.py
│       ├── router.py           # Main router mounting all sub-routers
│       ├── screener.py         # Stock screener endpoints
│       ├── features.py         # Feature metadata/dictionary
│       ├── templates.py        # Flagship screen templates
│       ├── detail.py           # Individual stock detail (Phase 2)
│       └── watchlists.py       # Watchlist management (Phase 2)
├── schemas/
│   └── stocks.py               # Pydantic schemas
├── services/
│   └── stocks/
│       ├── __init__.py
│       ├── screener_service.py # Core screening logic
│       ├── feature_engine.py   # Feature computation
│       ├── price_calculator.py # Returns, technicals, 52wk
│       └── universe.py         # Universe/base filtering
└── models/
    └── stocks.py               # Saved screens, watchlists
```

## Frontend Structure

```
frontend/src/pages/
└── stocks/
    ├── StocksPortal.tsx        # Main landing page
    ├── Screener.tsx            # Stock screener page
    ├── ScreenBuilder.tsx       # Build custom screens
    ├── ScreenResults.tsx       # Display results
    ├── Templates.tsx           # Flagship templates
    ├── StockDetail.tsx         # Individual stock (Phase 2)
    ├── Watchlists.tsx          # Watchlist management (Phase 2)
    └── components/
        ├── CriteriaBuilder.tsx
        ├── FeatureSelector.tsx
        ├── UniverseFilter.tsx
        ├── ResultsTable.tsx
        └── StockCard.tsx
```

## Navigation

Add to main navigation under "Stocks":
- `/stocks` - Portal (Template-First Landing)
- `/stocks/screener` - Stock Screener
- `/stocks/screener/new` - Build New Screen
- `/stocks/templates` - Flagship Templates
- `/stocks/watchlists` - Watchlists (Phase 2)
- `/stocks/:symbol` - Stock Detail (Phase 2)

## Front Page Design (Template-First Portal)

```
┌─────────────────────────────────────────────────────────────┐
│  STOCKS                                        [New Screen] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Flagship Screens                                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Deep     │ │Quality  │ │GARP     │ │Dividend │  → more   │
│  │Value    │ │Compound │ │         │ │Income   │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                             │
│  📁 My Saved Screens                                        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Tech Value Plays          Last run: 2 days ago         ││
│  │ Small Cap Momentum        Last run: 1 week ago         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Rationale:** Guided experience for common investors - flagship templates are prominently featured while custom screening remains accessible.

---

# Part 4: Implementation Phases

## Phase 1: Core Screener (MVP)

**Goal:** Working screener with ready features and basic UI.

### Part 1A: Foundation (Backend Setup)
- [ ] Database models for saved screens (`backend/app/models/stocks.py`)
- [ ] Pydantic schemas (`backend/app/schemas/stocks.py`)
- [ ] Feature registry dictionary (all 97 ready features)
- [ ] Basic router structure (`backend/app/api/stocks/`)

### Part 1B: Core Screener API
- [ ] Universe endpoint (`GET /api/stocks/universe`)
- [ ] Screening endpoint (`POST /api/stocks/screen`)
- [ ] Join logic (nasdaq_screener_profiles + ratios_ttm_bulk + key_metrics_ttm_bulk)
- [ ] Pagination and sorting

### Part 1C: Frontend MVP
- [ ] Basic Screener page with filter builder
- [ ] Results table component
- [ ] API integration testing

### Part 1D: Computed Features
- [ ] 52-week high/low from `prices_daily`
- [ ] Returns (1M, 3M, 6M, 1Y) from `prices_monthly`
- [ ] Relative volume
- [ ] Price target upside %

### Part 1E: Templates & Persistence
- [ ] 12 flagship screen templates
- [ ] Save/load custom screens
- [ ] Template selector UI

---

## Phase 2: Enhanced Features

**Goal:** Add computed features and stock detail pages.

### Computed Features
- [ ] All return periods
- [ ] RSI, SMAs, Golden Cross
- [ ] Volatility metrics
- [ ] Max drawdown

### New Features
- [ ] Stock detail page
- [ ] Watchlist management
- [ ] Export to CSV

---

## Phase 3: Advanced

**Goal:** Comparisons, alerts, and macro-conditioning.

- [ ] Side-by-side stock comparison
- [ ] Sector-relative z-scores
- [ ] Composite scores (Value, Quality, Growth, Momentum)
- [ ] Macro regime conditioning
- [ ] Price/metric alerts

---

## Phase 4: Data Expansion

**Goal:** Add missing data sources.

- [ ] Short interest data collection
- [ ] Float shares
- [ ] Analyst ratings (Buy/Hold/Sell)
- [ ] Historical estimates for surprise calculation

---

## Phase 5: Factor Analytics

**Goal:** Statistical models for stock-macro relationships.

- [ ] Factor sensitivity calculations
- [ ] Rolling correlations
- [ ] Regime detection
- [ ] Factor decomposition

---

# Part 5: Macro/Economic Features

## Category 18: Macro & Economic Indicators

The Finexus differentiator: regime-aware screening using economic data.

### 18.1 FRED Economic Indicators

| Feature | Status | Source | Series Examples |
|---------|--------|--------|-----------------|
| Fed Funds Rate | Ready | `fred_observation_latest` | FEDFUNDS, DFF |
| 10-Year Treasury Yield | Ready | `fred_observation_latest` | DGS10 |
| 2-Year Treasury Yield | Ready | `fred_observation_latest` | DGS2 |
| 2s10s Spread | Computed | Derived | DGS10 - DGS2 |
| CPI (All Items) | Ready | `fred_observation_latest` | CPIAUCSL |
| Core CPI | Ready | `fred_observation_latest` | CPILFESL |
| PCE Inflation | Ready | `fred_observation_latest` | PCEPI |
| Core PCE | Ready | `fred_observation_latest` | PCEPILFE |
| Real GDP | Ready | `fred_observation_latest` | GDPC1 |
| GDP Growth (QoQ) | Computed | Derived | Period change |
| Industrial Production | Ready | `fred_observation_latest` | INDPRO |
| Unemployment Rate | Ready | `fred_observation_latest` | UNRATE |
| Initial Jobless Claims | Ready | `fred_observation_latest` | ICSA |
| Continuing Claims | Ready | `fred_observation_latest` | CCSA |
| ISM Manufacturing | Ready | `fred_observation_latest` | MANEMP, ISM |
| Consumer Sentiment | Ready | `fred_observation_latest` | UMCSENT |
| VIX | Ready | `fred_observation_latest` | VIXCLS |
| Credit Spreads | Ready | `fred_observation_latest` | BAMLH0A0HYM2 |
| M2 Money Supply | Ready | `fred_observation_latest` | M2SL |
| Leading Economic Index | Ready | `fred_observation_latest` | USSLIND |
| Housing Starts | Ready | `fred_observation_latest` | HOUST |

**Source Tables:**
- `fred_series` - Series metadata
- `fred_observation_latest` - Latest values
- `fred_observation_realtime` - ALFRED revision history (for PIT analysis)

---

### 18.2 BLS Labor & Price Data

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| CPI Index Level | Ready | `bls_cu_data` | CUSR0000SA0 |
| CPI YoY % Change | Computed | Derived | 12-month change |
| CPI MoM % Change | Computed | Derived | 1-month change |
| Core CPI | Ready | `bls_cu_data` | CUSR0000SA0L1E |
| Employment (Nonfarm) | Ready | `bls_ce_data` | CES0000000001 |
| Employment Change | Computed | Derived | Monthly change |
| Unemployment Rate | Ready | `bls_la_data` | LASST... series |
| Average Hourly Earnings | Ready | `bls_ce_data` | CES0500000003 |
| PPI (All Commodities) | Ready | `bls_pc_data` | Producer prices |
| Average Prices (Gas, Food) | Ready | `bls_ap_data` | Consumer prices |

**Source Tables:**
- `bls_cu_series` / `bls_cu_data` - CPI data
- `bls_ce_series` / `bls_ce_data` - Employment data
- `bls_la_series` / `bls_la_data` - Unemployment by area
- `bls_ap_series` / `bls_ap_data` - Average consumer prices

---

### 18.3 BEA GDP & Income Data

| Feature | Status | Source | Notes |
|---------|--------|--------|-------|
| GDP (Current $) | Ready | `bea_nipa_data` | Table T10101 |
| GDP (Real/Chained $) | Ready | `bea_nipa_data` | Table T10106 |
| GDP Components | Ready | `bea_nipa_data` | Consumption, Investment, Gov, Net Exports |
| Personal Income | Ready | `bea_personal_income_summary` | National & State |
| Per Capita Income | Ready | `bea_personal_income_summary` | By geography |
| State GDP | Ready | `bea_regional_data` | SAGDP tables |
| GDP by Industry | Ready | `bea_gdpbyindustry_data` | Sector breakdown |
| Trade Balance | Ready | `bea_ita_data` | International transactions |

**Source Tables:**
- `bea_nipa_data` - National accounts
- `bea_regional_data` - State/regional data
- `bea_gdp_summary` - Quick GDP access
- `bea_gdpbyindustry_data` - Industry breakdown
- `bea_ita_data` - Trade/international

---

### 18.4 Treasury Yield & Auction Data

| Feature | Status | Source | Column |
|---------|--------|--------|--------|
| 1M Treasury Yield | Ready | `treasury_daily_rates` | `yield_1m` |
| 3M Treasury Yield | Ready | `treasury_daily_rates` | `yield_3m` |
| 6M Treasury Yield | Ready | `treasury_daily_rates` | `yield_6m` |
| 1Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_1y` |
| 2Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_2y` |
| 5Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_5y` |
| 7Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_7y` |
| 10Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_10y` |
| 20Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_20y` |
| 30Y Treasury Yield | Ready | `treasury_daily_rates` | `yield_30y` |
| 2s10s Spread | Ready | `treasury_daily_rates` | `spread_2s10s` |
| 5s30s Spread | Ready | `treasury_daily_rates` | `spread_5s30s` |
| 5Y Real Yield (TIPS) | Ready | `treasury_daily_rates` | `real_yield_5y` |
| 10Y Real Yield (TIPS) | Ready | `treasury_daily_rates` | `real_yield_10y` |
| 5Y Breakeven Inflation | Ready | `treasury_daily_rates` | `breakeven_5y` |
| 10Y Breakeven Inflation | Ready | `treasury_daily_rates` | `breakeven_10y` |
| Auction Bid-to-Cover | Ready | `treasury_auctions` | `bid_to_cover_ratio` |
| Auction Tail (bps) | Ready | `treasury_auctions` | `tail_bps` |

**Source Tables:**
- `treasury_daily_rates` - Daily yield curve
- `treasury_auctions` - Auction results
- `treasury_auction_reactions` - Market reactions

---

### 18.5 Derived Regime Indicators

| Regime | Definition | Indicators Used |
|--------|------------|-----------------|
| **Inflation Regime** | Rising/Falling/Stable | CPI YoY, Core PCE, Breakeven inflation |
| **Growth Regime** | Expansion/Contraction/Slowdown | GDP QoQ, Industrial Production, LEI |
| **Labor Regime** | Tight/Loose/Transitioning | Unemployment, Claims, Wage growth |
| **Rates Regime** | Hiking/Cutting/Pausing | Fed Funds, 2Y yield, Yield curve shape |
| **Credit Regime** | Risk-On/Risk-Off | Credit spreads, VIX, HY spreads |
| **Volatility Regime** | Low/Normal/High | VIX level, VIX percentile |

---

# Part 6: Statistical Models & Factor Analysis

## 6.1 Overview

Build quantitative models to understand relationships between stock returns and economic factors. This enables:

1. **Factor Sensitivity Analysis** - How does AAPL react to CPI surprises?
2. **Correlation Analysis** - Which stocks are most correlated with interest rates?
3. **Regime-Based Selection** - Which stocks outperform when inflation is rising?
4. **Risk Decomposition** - What % of volatility is explained by macro factors?

---

## 6.2 Core Statistical Metrics

### Stock-Factor Correlations

| Metric | Description | Calculation |
|--------|-------------|-------------|
| `corr_10y_yield` | Correlation with 10Y Treasury | Rolling 60-day correlation |
| `corr_2s10s_spread` | Correlation with yield curve | Rolling correlation |
| `corr_cpi` | Correlation with CPI changes | Monthly correlation |
| `corr_vix` | Correlation with VIX | Rolling 30-day correlation |
| `corr_dxy` | Correlation with Dollar Index | Rolling correlation |
| `corr_oil` | Correlation with crude oil | Rolling correlation |
| `corr_spx` | Correlation with S&P 500 | Rolling 60-day (market beta proxy) |

### Factor Sensitivities (Betas)

| Metric | Description | Regression Model |
|--------|-------------|------------------|
| `beta_market` | Market beta | R_stock = α + β_mkt × R_SPX |
| `beta_rates` | Interest rate sensitivity | R_stock = α + β_rates × Δ10Y |
| `beta_inflation` | Inflation sensitivity | R_stock = α + β_inf × ΔCPI |
| `beta_growth` | GDP sensitivity | R_stock = α + β_gdp × ΔGDP |
| `beta_credit` | Credit spread sensitivity | R_stock = α + β_credit × ΔHY_spread |
| `beta_volatility` | Volatility sensitivity | R_stock = α + β_vix × ΔVIX |

### Multi-Factor Model

```
R_stock = α + β₁(R_mkt) + β₂(Δ10Y) + β₃(ΔCPI) + β₄(ΔVIX) + ε

Where:
- α = Stock-specific alpha (unexplained return)
- β₁ = Market beta
- β₂ = Rate sensitivity
- β₃ = Inflation sensitivity
- β₄ = Volatility sensitivity
- ε = Residual/idiosyncratic risk
```

---

## 6.3 Regime-Conditional Analysis

### Performance by Regime

For each stock, calculate average returns during different regimes:

| Regime State | Stocks Outperform | Stocks Underperform |
|--------------|-------------------|---------------------|
| Rising Inflation | Commodities, Energy, TIPS-linked | Growth, Long-duration |
| Falling Inflation | Growth, Tech, Long-duration | Commodities |
| Rising Rates | Financials, Value | REITs, Utilities, Growth |
| Falling Rates | REITs, Utilities, Growth | Banks |
| High VIX | Defensive, Low-beta, Quality | Cyclicals, High-beta |
| Low VIX | Cyclicals, High-beta | Defensive |
| Yield Curve Steepening | Banks, Financials | - |
| Yield Curve Inversion | Defensive, Quality | Cyclicals, Financials |

### Regime-Conditional Screening

Screen criteria can be conditioned on current regime:

```python
# Example: Adjust value screen based on rate regime
if regime.rates == "CUTTING":
    # Favor rate-sensitive value
    screen.add_filter("beta_rates", ">", 0.5)
    screen.add_filter("dividend_yield", ">", 3.0)
elif regime.rates == "HIKING":
    # Favor low-duration value
    screen.add_filter("beta_rates", "<", 0.2)
    screen.add_filter("debt_to_equity", "<", 0.5)
```

---

## 6.4 Data Requirements

### For Factor Analysis

| Data | Source | Frequency | Lookback |
|------|--------|-----------|----------|
| Stock returns | `prices_daily` | Daily | 3-5 years |
| Treasury yields | `treasury_daily_rates` | Daily | 3-5 years |
| CPI | `bls_cu_data` | Monthly | 3-5 years |
| GDP | `bea_nipa_data` | Quarterly | 3-5 years |
| VIX | `fred_observation_latest` | Daily | 3-5 years |
| Credit spreads | `fred_observation_latest` | Daily | 3-5 years |

### Computed Tables (New)

| Table | Description | Update Frequency |
|-------|-------------|------------------|
| `stock_factor_betas` | Pre-computed factor sensitivities per stock | Weekly |
| `stock_correlations` | Rolling correlations with factors | Daily |
| `regime_indicators` | Current regime state | Daily |
| `stock_regime_returns` | Historical returns by regime | Weekly |

---

## 6.5 Implementation Approach

### Backend Services

```
backend/app/services/stocks/
├── factor_engine.py        # Compute factor betas and correlations
├── regime_detector.py      # Identify current economic regime
├── correlation_service.py  # Rolling correlation calculations
└── risk_decomposition.py   # Variance attribution
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stocks/{symbol}/factors` | Factor betas and correlations for a stock |
| `GET /api/stocks/{symbol}/regime-returns` | Historical returns by regime |
| `GET /api/regime/current` | Current economic regime state |
| `GET /api/screener/regime-adjusted` | Screening with regime conditioning |

### Frontend Components

| Component | Description |
|-----------|-------------|
| `FactorExposureChart.tsx` | Bar chart of factor betas |
| `CorrelationHeatmap.tsx` | Correlation matrix visualization |
| `RegimeIndicator.tsx` | Current regime state display |
| `RegimePerformance.tsx` | Returns by regime table |

---

## 6.6 Flagship Factor Screens

### Screen 13: Rate-Sensitive Value

**Use Case:** Benefit from rate cuts.

| Criteria | Operator | Value |
|----------|----------|-------|
| `beta_rates` | > | 0.5 |
| P/E Ratio | < | 18 |
| Dividend Yield | > | 2.5% |
| Debt/Equity | < | 1.0 |

### Screen 14: Inflation Hedges

**Use Case:** Protect against rising inflation.

| Criteria | Operator | Value |
|----------|----------|-------|
| `beta_inflation` | > | 0.3 |
| Sector | IN | Energy, Materials, Real Estate |
| ROE | > | 10% |

### Screen 15: Low Macro Sensitivity

**Use Case:** Stocks with low macro exposure (idiosyncratic).

| Criteria | Operator | Value |
|----------|----------|-------|
| `beta_rates` | BETWEEN | -0.2 AND 0.2 |
| `beta_inflation` | BETWEEN | -0.2 AND 0.2 |
| `corr_spx` | < | 0.5 |
| Market Cap | > | $1B |

### Screen 16: Regime Momentum

**Use Case:** Stocks performing well in current regime.

| Criteria | Operator | Value |
|----------|----------|-------|
| `regime_return_current` | > | Top 20% |
| 3-Month Return | > | 0 |
| Relative Volume | > | 1.0 |

---

# Appendix A: Feature Summary

| Category | Ready | Computed | Missing | Total |
|----------|-------|----------|---------|-------|
| Identity & Classification | 12 | 0 | 0 | 12 |
| Price | 3 | 8 | 0 | 11 |
| Returns | 0 | 9 | 0 | 9 |
| Volume & Liquidity | 2 | 3 | 0 | 5 |
| Market Cap & Size | 3 | 1 | 1 | 5 |
| Risk & Volatility | 1 | 3 | 0 | 4 |
| Technical Indicators | 0 | 7 | 0 | 7 |
| Valuation Ratios | 14 | 0 | 0 | 14 |
| Profitability Ratios | 10 | 0 | 0 | 10 |
| Leverage & Health | 9 | 0 | 0 | 9 |
| Dividend | 4 | 0 | 0 | 4 |
| Per Share Metrics | 6 | 0 | 0 | 6 |
| Financial Statements | 13 | 0 | 0 | 13 |
| Ownership | 8 | 0 | 0 | 8 |
| Insider Trading | 6 | 0 | 0 | 6 |
| Analyst | 6 | 1 | 1 | 8 |
| Short Interest | 0 | 0 | 5 | 5 |
| **Macro/Economic** | **55** | **10** | **0** | **65** |
| **Factor Sensitivities** | **0** | **13** | **0** | **13** |
| **TOTAL** | **152** | **55** | **7** | **214** |

---

# Appendix B: Key Data Models Reference

## Primary Tables for Screening

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `nasdaq_screener_profiles` | Universe base | symbol, sector, industry, market_cap |
| `company_profile_bulk` | Company details | exchange, beta, avg_volume |
| `ratios_ttm_bulk` | Valuation/Profit ratios | All TTM ratios |
| `key_metrics_ttm_bulk` | Key metrics | ROE, ROIC, EV metrics |
| `prices_daily` | Daily prices | adj_close, volume |
| `prices_monthly` | Monthly prices | For return calculations |
| `institutional_ownership` | Ownership data | ownership_percent |
| `insider_statistics` | Insider activity | buy/sell ratio |
| `price_target_summary_bulk` | Analyst targets | price targets |

---

# Appendix C: Economic Data Models Reference

## FRED Models (`models_fred.py`)

| Model | Table | Purpose |
|-------|-------|---------|
| `FredSource` | `fred_source` | Data sources (BLS, Census, etc.) |
| `FredRelease` | `fred_release` | Release schedules |
| `FredReleaseDate` | `fred_release_date` | Release calendar |
| `FredCategory` | `fred_category` | Hierarchical categories |
| `FredTag` | `fred_tag` | Series tags |
| `FredSeries` | `fred_series` | Series metadata (title, units, frequency) |
| `FredObservationLatest` | `fred_observation_latest` | Latest snapshot values |
| `FredObservationRealtime` | `fred_observation_realtime` | ALFRED revision history |

## BLS Models (`bls_models.py`)

| Model | Table | Purpose |
|-------|-------|---------|
| `BLSSurvey` | `bls_surveys` | Survey catalog (CPI, CES, LA, etc.) |
| `BLSArea` | `bls_areas` | Geographic areas |
| `CUSeries` / `CUData` | `bls_cu_series` / `bls_cu_data` | Consumer Price Index |
| `CESeries` / `CEData` | `bls_ce_series` / `bls_ce_data` | Current Employment Statistics |
| `LASeries` / `LAData` | `bls_la_series` / `bls_la_data` | Local Area Unemployment |
| `APSeries` / `APData` | `bls_ap_series` / `bls_ap_data` | Average Prices |

## BEA Models (`bea_models.py`)

| Model | Table | Purpose |
|-------|-------|---------|
| `BEADataset` | `bea_datasets` | Dataset catalog |
| `NIPATable` / `NIPASeries` / `NIPAData` | `bea_nipa_*` | National Income & Product Accounts |
| `RegionalTable` / `RegionalData` | `bea_regional_*` | State/regional economic data |
| `RegionalGeoFips` | `bea_regional_geo_fips` | FIPS code reference |
| `GDPSummary` | `bea_gdp_summary` | Quick GDP access |
| `PersonalIncomeSummary` | `bea_personal_income_summary` | Income summaries |
| `GDPByIndustryData` | `bea_gdpbyindustry_data` | GDP by industry sector |
| `ITAData` | `bea_ita_data` | International transactions |
| `FixedAssetsData` | `bea_fixedassets_data` | Fixed asset accounts |

## Treasury Models (`treasury_models.py`)

| Model | Table | Purpose |
|-------|-------|---------|
| `TreasurySecurityType` | `treasury_security_types` | Security type reference |
| `TreasuryAuction` | `treasury_auctions` | Auction results |
| `TreasuryAuctionReaction` | `treasury_auction_reactions` | Market reactions |
| `TreasuryUpcomingAuction` | `treasury_upcoming_auctions` | Auction calendar |
| `TreasuryDailyRate` | `treasury_daily_rates` | Daily yield curve |
| `TreasuryAuctionSchedule` | `treasury_auction_schedule` | Regular schedule |

---

# Appendix D: Flagship Screens Summary

| # | Screen Name | Strategy | Key Metrics |
|---|-------------|----------|-------------|
| 1 | Deep Value | Low multiples, positive earnings | P/E, P/B, EV/EBITDA |
| 2 | Quality Compounders | High returns, durable margins | ROE, ROIC, Gross Margin |
| 3 | GARP | Growth at reasonable price | PEG, Revenue Growth, P/E |
| 4 | Dividend Aristocrats Clone | Sustainable high yield | Div Yield, Payout Ratio, FCF |
| 5 | Momentum Leaders | Strong price momentum | 6M/12M Returns, RSI |
| 6 | Fallen Angels | Quality stocks sold off | % from 52wk High, ROE |
| 7 | Small Cap Growth | Fast-growing small caps | Market Cap, Revenue Growth |
| 8 | Low Volatility Dividend | Defensive income | Beta, Div Yield, Volatility |
| 9 | Insider Buying | Follow insider purchases | Buy/Sell Ratio, Transactions |
| 10 | Analyst Upgrade Candidates | High upside to targets | Price Target Upside % |
| 11 | Recession Resistant | Defensive for downturns | Sector, Beta, FCF Yield |
| 12 | Rate Cut Beneficiaries | Benefit from lower rates | Sector, Div Yield |
| 13 | Rate-Sensitive Value | High rate beta value | beta_rates, P/E, Div Yield |
| 14 | Inflation Hedges | Protect against inflation | beta_inflation, Sector |
| 15 | Low Macro Sensitivity | Idiosyncratic stocks | Low factor betas |
| 16 | Regime Momentum | Outperformers in current regime | Regime returns |

---

*Document maintained by Finexus development team.*
*Last updated: 2024-12-31*
