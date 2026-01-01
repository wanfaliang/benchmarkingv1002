
# Macro Impact Lab Modual or Research Modual – Portal-Level Design (Q2 Architecture)  
**Finexus Documentation – Markdown Version**  
**Version: 1.0**

---

# Table of Contents
1. [Overview](#overview)  
2. [Portal Sections](#portal-sections)  
3. [BLS Portal Section](#bls-portal-section)  
4. [BEA Portal Section](#bea-portal-section)  
5. [Treasury Portal Section](#treasury-portal-section)  
6. [FRED Portal Section](#fred-portal-section)  
7. [Markets & Indices Portal Section](#markets--indices-portal-section)  
8. [Options Market Flows Portal Section (Placeholder)](#options-market-flows-portal-section-placeholder)  
9. [Census & Other Sources Portal Section (Placeholder)](#census--other-sources-portal-section-placeholder)  
10. [Next Steps](#next-steps)

---

# Overview
The **Macro Impact Lab** or  **Research** is the central module inside Finexus for analyzing interactions between **macroeconomic data** and **financial markets**.

The Lab portal provides:
- High‑level economic dashboards  
- Data-source-based sections (BLS, BEA, Treasury, FRED, etc.)  
- Quick entries into deep dataset explorers (Q3 level)  
- Preconfigured "Quick Studies"  
- Extensible architecture for future datasets

This document defines the **Portal-Level (Q2) design**, not the deep analytical explorers.

---

# Portal Sections

The Macro Impact Lab portal consists of:

1. Overview  
2. **BLS** – Labor, Wages, Inflation  
3. **BEA** – GDP, Income, Trade, Capital, Industry, Regions  
4. **Treasury** – Yield Curve, Auctions, Rates  
5. **FRED** – Curated financial & macro indicators  
6. **Markets & Indices** – Cross-asset market dashboards  
7. **Options Market Flows** – Gamma & hedging (placeholder)  
8. **Census & Others** – Structural and demographic data (placeholder)

Each portal section follows the structure:
- (1) Header  
- (2) Snapshot Cards  
- (3) Calendar / Update Feed  4
- (4) Latest Releases  
- (5) Category Browser  
- (6) Quick Studies  

---

# BLS Portal Section
## (1) Header
**Title:** BLS – U.S. Labor, Wages & Prices Overview  
Covers CES, LN, LAUS, JOLTS, OE, EC, CPI, PR, regional labor datasets.

Metadata examples:
- Last updated  
- Surveys tracked (~20+)  
- Data coverage: national, regional, industry  

## (2) Snapshot Cards
- **Labor Market:** unemployment rate, payrolls, job openings vs unemployed  
- **Wages:** hourly earnings, ECI, OE wage data  
- **Inflation:** CPI headline/core  
- **Regional:** mini-map of state unemployment  

## (3) Release Calendar
Upcoming: CPI, Nonfarm Payrolls, Unemployment Rate, JOLTS, ECI, Productivity  

## (4) Latest Releases
Recent releases with actual vs previous, plus signal tags.

## (5) Survey Category Browser
Cards for:
- Employment (CES)  
- Unemployment (LN/LA/SM)  
- Wages (OE/EC)  
- JOLTS  
- CPI / AP  
- Productivity (PR)  
- Regional Labor  

## (6) Quick Studies
- Labor Tightness vs SPX  
- Wage Growth vs Margins  
- CPI Surprise vs SPX  
- Quits Rate vs Small Caps  

---

# BEA Portal Section
## (1) Header
**Title:** BEA – Growth, Income, Trade & Capital Overview  
Includes NIPA, Personal Income & Outlays, Industry Accounts, Regional Accounts, ITA, Fixed Assets.

## (2) Snapshot Cards
- **GDP Growth:** YoY, QoQ SAAR, contributions  
- **Demand Composition:** C/I/G/NX shares  
- **Income & Savings:** DPI, savings rate  
- **Regional & Industry:** state GDP, leading industries  

## (3) Release Calendar
GDP estimates, personal income/outlays, industry accounts, regional accounts, ITA, fixed assets.

## (4) Latest Releases
Rows with period, headline numbers, classification tags.

## (5) Dataset Browser
Cards:
- NIPA  
- Personal Income  
- GDP by Industry  
- Regional  
- ITA  
- Fixed Assets  

## (6) Quick Studies
- GDP Regimes vs SPX  
- Consumption vs Consumer Sectors  
- Industry Growth vs Sector Performance  
- Regional Growth vs Cyclicals  

---

# Treasury Portal Section
## (1) Header
**Title:** U.S. Treasury – Yield Curve & Auctions Overview**

## (2) Snapshot Cards
- **Yield Curve:** mini chart + spreads  
- **Curve Dynamics:** 1M changes  
- **Auction Snapshot:** tails, BTC, strength indicators  
- **Rates vs Risk Assets:** 10Y vs SPX correlations  

## (3) Auction Calendar
All upcoming coupon auctions.

## (4) Latest Auctions
Show yield, tail, BTC, and market reaction.

## (5) Category Browser
- Yield Curve & Spreads  
- Auctions & WI Metrics  
- Auction Impact Studies  
- Mortgage vs Treasuries  
- Term Premium Models (future)  

## (6) Quick Studies
- Auction Impact Study  
- Curve Inversion vs Equities  
- Rates Shock Analysis  

---

# FRED Portal Section
## (1) Header
**Title:** FRED – Financial & Economic Metrics Watch**

## (2) Snapshot Cards
- Financial Conditions Index  
- Credit Spreads  
- Money & Liquidity  
- Housing Indicators  

## (3) Watchlist Calendar / Update Feed
Upcoming scheduled updates for curated indicators.

## (4) Latest Changes / Alerts
Largest moves in curated series.

## (5) Category Browser
- Financial Conditions & Stress  
- Credit & Spreads  
- Money & Liquidity  
- Housing & Construction  
- Global & FX  
- User Watchlists  

## (6) Quick Studies
- FCI vs SPX  
- Credit Spreads vs HY ETFs  
- M2 vs Asset Prices  
- Housing vs Homebuilders  

---

# Markets & Indices Portal Section
## (1) Header
**Title:** Markets & Indices – Global Risk Overview**

## (2) Snapshot Cards
- Equity Performance (SPX, NDX, RUT)  
- Volatility & Risk (VIX, RV)  
- USD Strength (DXY)  
- Breadth & Liquidity Metrics  

## (3) Market Event Overview
Light summary: macro events, earnings cycles.

## (4) Regimes & Risk Summary
- Equity regime  
- Vol regime  
- Credit regime  

## (5) Category Browser
- Global Indices  
- Sectors & Factors  
- Volatility  
- FX & Dollar  
- Breadth & Liquidity  

## (6) Quick Studies
- Market Regime Study  
- Sector Rotation Map  
- Volatility & Drawdown Study  
- Breadth Thrust Study  

---

# Options Market Flows Portal Section (Placeholder)
## (1) Header
Options Market Flows – Gamma, Hedging, Positioning

## (2) Snapshot Cards
Placeholders for:
- SPX Gamma  
- QQQ Gamma  
- IWM Gamma  
- 0DTE Activity  

## (3) Expiration Calendar
Placeholder for opex schedules.

## (4) Latest Flows
Future integration.

## (5) Category Browser
Planned explorers (index gamma, ETF gamma, dealer flow).

## (6) Quick Studies
Planned templates.

---

# Census & Other Sources Portal Section (Placeholder)
## (1) Header
Census & Other Data – Structural & Demographic Insights

## (2) Snapshot Cards
Planned: population, housing, retail.

## (3) Release Calendar
Placeholder.

## (4) Latest Releases
Placeholder.

## (5) Dataset Browser
Planned categories.

## (6) Quick Studies
Planned integrations.

---

# Next Steps
1. Add this `.md` file to:
   ```
   /docs/macro_impact_lab/macro_impact_lab_portal.md
   ```
2. Define backend API contracts for portal snapshot data.
3. Begin Q3 Dataset Explorer designs.
4. Produce architecture diagrams and component trees.

