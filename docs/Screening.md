# Building the brand new module for Finexus, Screening
    We are going to create a new module for this project.
    The goal is to create comprehensive equity screening based on the financial, economic, market data we have collected and we continuously collect throught the supporting project, the DATA project.

# Introducing DATA Project
    The DATA Project is the core data collection project which estabishes models, builds collectors, runs scripts and jobs, implements management with Admin UI.
## DATA Prjoct's location and 
    It is in D:\finexus-data-collector
## Major Models of the DATA Project
    
    The data models are in src/database
1.  bea_models.py, all the data models for BEA datasets
    bea_tracking_models.py, models for tracking BEA collection runs.
2.  bls_models.py, all the data models for BLS Surveys
    bls_tracking_models.py, models for tracking BLS data collection runs.
3.  models_fred.py, models for FRED data.
    fred_tracking_models.py, models for tracking FRED data collection runs.
4.  models.py, models for financial, market, and economic snapshot(mini version of FRED) and related tracking models.
5.  treasury_models.py, models related to treasury auctions and auction results.

# Module Screening of this project
    As mentioned above, we will create schema, endpoints, frontends for Module Screening, which should be accessed through the navigation in the header

## DATA Access
    This project can only read the data from DATA Project
    the code file backend\app\database.py list two database connection:

  1. Primary Database (Finexus App) - get_db()
    - For users, analyses, datasets
    - Uses settings.DATABASE_URL
  2. DATA Database (Read-only) - get_data_db()
    - For economic, treasury, financial/market data
    - Uses settings.DATA_DATABASE_URL
    - This is where BLS, BEA, Treasury, and FRED data lives
  3. The .env file contains both 
     DATABASE_URL, which is the database url for database of this project, namely users, analyses, datasets, sections, etc.
     DATA_DATABASE_URL, which is the database url for the database of DATA Project, in case we need to retrieve meta data for building pages and real data to get insights.

## Ideas for Building Phase one of Module Screening. See below.

Let’s be concrete and systematic, and **tie every feature to the tables we already have**.

Below is a **Finexus-grade feature taxonomy** for the **Stock Screening Module**, organized by **feature type → what it measures → exact data source(s)** → how it’s used in screening.

---

## 1️⃣ Universe & Identity Features (who is even eligible?)

**Purpose:** define *what stocks exist* and basic constraints.

### Features

* `symbol`
* `company_name`
* `exchange`
* `country`
* `sector`
* `industry`
* `market_cap`
* `avg_volume`
* `price`
* `snapshot_date`

### Sources

* `nasdaq_screener_profiles` (primary)
* `companies` (static identity)
* `prices_daily` (price sanity check)

### Screening use

* Market-cap buckets (large / mid / small)
* Sector/industry filtering
* Liquidity safety (min volume, min price)
* Regional screens (US only, etc.)

---

## 2️⃣ Valuation Features (what do you pay?)

**Purpose:** identify cheap vs expensive stocks.

### Core features (TTM unless noted)

* `pe_ratio_ttm`
* `ev_to_ebitda_ttm`
* `ev_to_sales_ttm`
* `price_to_book_ratio`
* `price_to_sales_ratio_ttm`
* `free_cash_flow_yield_ttm`
* `earnings_yield_ttm`
* `market_cap / enterprise_value`

### Sources

* `ratios_ttm_bulk`
* `key_metrics_ttm_bulk`
* `enterprise_values`

### Screening use

* Absolute value screens
* Sector-relative cheapness (z-score within sector)
* Composite “Value Score”

---

## 3️⃣ Profitability & Quality Features (is the business good?)

**Purpose:** avoid value traps; find durable businesses.

### Features

* `gross_margin_ttm`
* `operating_margin_ttm`
* `net_margin_ttm`
* `return_on_equity_ttm`
* `return_on_assets_ttm`
* `return_on_invested_capital_ttm`
* `asset_turnover_ttm`
* `free_cash_flow_margin_ttm`

### Sources

* `ratios_ttm_bulk`
* `key_metrics_ttm_bulk`

### Screening use

* Quality filters (min ROE / ROIC)
* Quality ranking
* Defensive vs cyclical classification

---

## 4️⃣ Growth Features (is it improving?)

**Purpose:** distinguish compounders from stagnation.

### Features

* `revenue_growth_yoy`
* `revenue_cagr_3y`
* `eps_growth_yoy`
* `eps_cagr_3y`
* `free_cash_flow_growth`
* `ebitda_growth`

### Sources

* `financial_ratios`
* `key_metrics`
* (computed across periods)

### Screening use

* Growth stock screens
* GARP (growth at reasonable price)
* Momentum confirmation

---

## 5️⃣ Financial Strength & Risk Features (can it survive?)

**Purpose:** downside protection.

### Features

* `debt_to_equity`
* `net_debt_to_ebitda`
* `interest_coverage`
* `current_ratio`
* `quick_ratio`
* `cash_ratio`
* `altman_z_score` (derived)

### Sources

* `ratios_ttm_bulk`
* `balance_sheets`

### Screening use

* Bankruptcy risk filters
* Rate-sensitivity screens
* Macro regime conditioning

---

## 6️⃣ Momentum & Price Behavior (what is the market doing?)

**Purpose:** align with market trend and risk.

### Features

* `return_1m`
* `return_3m`
* `return_6m`
* `return_12m`
* `momentum_12m_1m`
* `volatility_30d`
* `volatility_90d`
* `max_drawdown_1y`
* `beta` (optional)

### Sources

* `prices_daily`
* `prices_monthly`

### Screening use

* Trend-following screens
* Avoiding falling knives
* Momentum-value hybrids

---

## 7️⃣ Liquidity & Tradability Features (can you trade it?)

**Purpose:** practical execution.

### Features

* `average_daily_volume`
* `dollar_volume`
* `turnover_ratio`
* `shares_outstanding`
* `float_shares`

### Sources

* `nasdaq_screener_profiles`
* `key_metrics_ttm_bulk`

### Screening use

* Institutional vs retail screens
* Slippage avoidance
* Position sizing constraints

---

## 8️⃣ Shareholder Return Features (how are owners rewarded?)

**Purpose:** income & capital discipline.

### Features

* `dividend_yield`
* `payout_ratio`
* `dividend_growth_rate`
* `share_buyback_yield`
* `total_shareholder_yield`

### Sources

* `key_metrics_ttm_bulk`
* `ratios_ttm_bulk`

### Screening use

* Income screens
* Capital discipline screens
* Defensive portfolios

---

## 9️⃣ Sentiment & Positioning (what do others think?)

**Purpose:** secondary signal / confirmation.

### Features

* `analyst_rating_consensus`
* `price_target_upside`
* `insider_buy_sell_ratio`
* `institutional_ownership_pct`
* `institutional_ownership_change`

### Sources

* `price_target_summary_bulk`
* `insider_trading`
* `institutional_ownership`

### Screening use

* Confirmation filters
* Contrarian setups
* Event-driven screens

---

## 🔟 Macro-Conditioned Features (Finexus differentiator)

**Purpose:** context-aware screening.

### Macro features (regimes)

* Inflation regime (CPI / PCE trend)
* Growth regime (GDP / IP)
* Labor stress (jobless claims, unemployment)
* Rates regime (2s10s, real rates)
* Volatility regime (macro proxies)

### Sources

* `models_fred.py` (latest + realtime)
* `treasury_daily_rates`
* `bls_models.py`
* `bea_models.py`

### Usage

* Conditional factor weighting
* Screen presets by regime
* “Why this screen works *now*” explanation

---

## 11️⃣ Composite & Derived Features (what users actually pick)

These are **not raw columns** but what makes the screener powerful:

* `value_score` = weighted z-score of valuation metrics
* `quality_score`
* `growth_score`
* `momentum_score`
* `defensive_score`
* `overall_rank`

Computed:

* within sector
* within universe
* or regime-conditional

---

## 12️⃣ Feature usage summary (what screens are possible immediately?)

| Screen Type     | Supported Now?                        |
| --------------- | ------------------------------------- |
| Value           | ✅                                     |
| Quality         | ✅                                     |
| Growth          | ✅                                     |
| Momentum        | ✅                                     |
| Dividend        | ✅                                     |
| GARP            | ✅                                     |
| Defensive       | ✅                                     |
| Sector-relative | ✅                                     |
| Regime-aware    | ✅                                     |
| PIT research    | ⚠️ (needs feature layer, data exists) |

---

## Final takeaway

You already have **institutional-level raw data**.
The screening module is about:

> **selecting, standardizing, and composing features — not collecting more data**

If you want, next I can:

* design the **exact feature dictionary** (names, units, null handling)
* define **feature availability flags** (live vs PIT)
* or propose **10 flagship Finexus screen templates** (Value, Quality, Recession-proof, Rate-cut winners, etc.)

Just tell me which one you want to lock in first.
