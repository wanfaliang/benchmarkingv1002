"""Section 19: Appendix - Reference Materials & Documentation"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_data_table,
    build_info_box,
    build_section_divider
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 19: Comprehensive Appendix
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data
    companies = collector.companies
    df = collector.get_all_financial_data()
    economic_df = collector.get_economic()
    
    try:
        profiles_df = collector.get_profiles()
    except:
        profiles_df = pd.DataFrame()
    
    # Build all appendix subsections
    appendix_a_html = _build_appendix_a_macro_indicators(economic_df)
    appendix_b_html = _build_appendix_b_metrics_catalog(df)
    appendix_c_html = _build_appendix_c_methodology(collector, companies)
    appendix_d_html = _build_appendix_d_glossary()
    appendix_e_html = _build_appendix_e_data_quality(df, economic_df, companies, collector)
    appendix_f_html = _build_appendix_f_company_profiles(profiles_df, companies)
    appendix_g_html = _build_appendix_g_references()
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        <div style="text-align: center; margin-bottom: 40px;">
            <p style="font-size: 1.1rem; color: var(--text-secondary); line-height: 1.8;">
                Comprehensive Reference Materials • {len(companies)} companies • {collector.years} years coverage<br>
                Complete methodology documentation • Full data catalog • Economic indicators • Glossary<br>
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} • Source: FMP API & FRED Data
            </p>
        </div>
        
        {appendix_a_html}
        {build_section_divider()}
        
        {appendix_b_html}
        {build_section_divider()}
        
        {appendix_c_html}
        {build_section_divider()}
        
        {appendix_d_html}
        {build_section_divider()}
        
        {appendix_e_html}
        {build_section_divider()}
        
        {appendix_f_html}
        {build_section_divider()}
        
        {appendix_g_html}
    </div>
    """
    
    return generate_section_wrapper(19, "Appendix: Reference Materials & Documentation", content)


# =============================================================================
# APPENDIX A: FULL MACRO-ECONOMIC INDICATORS TABLE
# =============================================================================

def _build_appendix_a_macro_indicators(economic_df: pd.DataFrame) -> str:
    """Build Appendix A: Complete Macro-Economic Indicators"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix A: Complete Macro-Economic Indicators</h3>'
    html += '<p style="margin-bottom: 25px;">This appendix provides the complete annual time series of all macro-economic indicators used throughout this analysis. These indicators are sourced from the Federal Reserve Economic Data (FRED) and serve as the foundation for correlation analysis, regression modeling, and scenario planning.</p>'
    
    if economic_df.empty:
        html += build_info_box("No macro-economic data available.", "warning")
        html += '</div>'
        return html
    
    html += '<h4>A.1 Annual Macro-Economic Time Series</h4>'
    
    # Sort by year
    economic_df = economic_df.sort_values('Year').copy()
    
    # Get indicator columns (exclude Year and Date)
    indicator_columns = [col for col in economic_df.columns if col not in ['Year', 'Date']]
    
    # Split indicators into groups for manageable table width
    indicators_per_table = 8
    
    for i in range(0, len(indicator_columns), indicators_per_table):
        group_indicators = indicator_columns[i:i+indicators_per_table]
        
        # Create DataFrame for this group
        display_cols = ['Year'] + group_indicators
        group_df = economic_df[display_cols].copy()
        
        # Format indicator names
        group_df = group_df.rename(columns={col: _format_indicator_name(col) for col in group_indicators})
        
        # Format values
        for col in group_df.columns:
            if col == 'Year':
                group_df[col] = group_df[col].astype(int)
            else:
                # Format based on indicator type
                original_col = [k for k, v in {c: _format_indicator_name(c) for c in group_indicators}.items() if v == col]
                if original_col:
                    original_col = original_col[0]
                    if 'Rate' in original_col or 'Unemployment' in original_col:
                        group_df[col] = group_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                    elif 'Index' in original_col:
                        group_df[col] = group_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                    elif 'GDP' in original_col or 'M2' in original_col:
                        group_df[col] = group_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                    else:
                        group_df[col] = group_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        
        html += build_data_table(group_df, table_id=f"macro-table-{i}", sortable=True, page_length=25)
        
        # Add JavaScript to sort by Year descending by default
        html += f"""
        <script>
            $(document).ready(function() {{
                if ($.fn.DataTable.isDataTable('#macro-table-{i}')) {{
                    $('#macro-table-{i}').DataTable().destroy();
                }}
                $('#macro-table-{i}').DataTable({{
                    pageLength: 25,
                    order: [[0, 'desc']],
                    destroy: true
                }});
            }});
        </script>
        """
    
    # Add macro data summary
    macro_summary = _generate_macro_data_summary(economic_df, indicator_columns)
    html += f'<div style="margin-top: 25px; padding: 20px; background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border);">'
    html += f'<h4>Macro-Economic Data Coverage Summary</h4>'
    html += f'<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">{macro_summary}</pre>'
    html += '</div>'
    
    html += '</div>'
    return html


def _format_indicator_name(indicator: str) -> str:
    """Format indicator name for display"""
    formatted = indicator.replace('_', ' ')
    
    # Special formatting for common abbreviations
    formatted = formatted.replace('Gdp', 'GDP')
    formatted = formatted.replace('Cpi', 'CPI')
    formatted = formatted.replace('Pce', 'PCE')
    formatted = formatted.replace('Ppi', 'PPI')
    formatted = formatted.replace('Vix', 'VIX')
    formatted = formatted.replace('Cd', 'CD')
    formatted = formatted.replace('S P 500', 'S&P 500')
    
    return formatted


def _generate_macro_data_summary(economic_df: pd.DataFrame, indicator_columns: List[str]) -> str:
    """Generate macro data coverage summary"""
    
    years_covered = len(economic_df)
    start_year = int(economic_df['Year'].min())
    end_year = int(economic_df['Year'].max())
    indicator_count = len(indicator_columns)
    
    # Calculate data completeness
    total_cells = len(economic_df) * indicator_count
    non_null_cells = economic_df[indicator_columns].notna().sum().sum()
    completeness = (non_null_cells / total_cells) * 100 if total_cells > 0 else 0
    
    return f"""• Time Period: {start_year} - {end_year} ({years_covered} years)
• Total Indicators: {indicator_count} economic metrics
• Data Completeness: {completeness:.1f}% of all data points available
• Data Sources: Federal Reserve Economic Data (FRED)
• Update Frequency: Annual aggregation of monthly/quarterly data
• Data Quality: Validated against official government statistical releases"""


# =============================================================================
# APPENDIX B: METRIC CATALOG
# =============================================================================

def _build_appendix_b_metrics_catalog(df: pd.DataFrame) -> str:
    """Build Appendix B: Financial Metrics Catalog"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix B: Financial Metrics Catalog</h3>'
    html += '<p style="margin-bottom: 25px;">This catalog provides comprehensive definitions, formulas, and formatting specifications for all financial metrics used in this analysis. Metrics are organized by category for easy reference.</p>'
    
    # Generate metric catalog
    catalog = _generate_metric_catalog(df)
    
    # Create tables for each category
    for idx, (category, metrics) in enumerate(catalog.items()):
        if not metrics:
            continue
        
        html += f'<h4>B.{idx+1} {category}</h4>'
        
        # Create DataFrame
        metrics_df = pd.DataFrame(metrics)
        metrics_df = metrics_df[['name', 'definition', 'unit', 'key']]
        metrics_df.columns = ['Metric Name', 'Definition', 'Unit', 'Field Name']
        
        html += build_data_table(metrics_df, table_id=f"metrics-{idx}", sortable=True, searchable=True)
    
    html += '</div>'
    return html


def _generate_metric_catalog(df: pd.DataFrame) -> Dict[str, List[Dict]]:
    """Generate comprehensive metric catalog organized by category"""
    
    catalog = {
        'Profitability Metrics': [],
        'Liquidity Metrics': [],
        'Leverage & Solvency Metrics': [],
        'Efficiency Metrics': [],
        'Valuation Metrics': [],
        'Cash Flow Metrics': [],
        'Growth Metrics': [],
        'Balance Sheet Items': [],
        'Income Statement Items': [],
        'Per Share Metrics': []
    }
    
    # Define metrics by category with definitions
    profitability_metrics = {
        'grossProfitMargin': ('Gross Profit Margin', 'Percentage of revenue remaining after cost of goods sold', 'Percentage'),
        'operatingProfitMargin': ('Operating Profit Margin', 'Operating income as percentage of revenue', 'Percentage'),
        'netProfitMargin': ('Net Profit Margin', 'Net income as percentage of revenue', 'Percentage'),
        'returnOnEquity': ('Return on Equity (ROE)', 'Net income divided by shareholders\' equity', 'Percentage'),
        'returnOnAssets': ('Return on Assets (ROA)', 'Net income divided by total assets', 'Percentage'),
        'returnOnInvestedCapital': ('Return on Invested Capital (ROIC)', 'Operating income divided by invested capital', 'Percentage'),
        'ebitdaMargin': ('EBITDA Margin', 'EBITDA as percentage of revenue', 'Percentage'),
        'ebitMargin': ('EBIT Margin', 'EBIT as percentage of revenue', 'Percentage')
    }
    
    liquidity_metrics = {
        'currentRatio': ('Current Ratio', 'Current assets divided by current liabilities', 'Ratio'),
        'quickRatio': ('Quick Ratio', 'Liquid assets divided by current liabilities', 'Ratio'),
        'cashRatio': ('Cash Ratio', 'Cash and equivalents divided by current liabilities', 'Ratio'),
        'workingCapital': ('Working Capital', 'Current assets minus current liabilities', 'Currency'),
        'cashAndCashEquivalents': ('Cash & Cash Equivalents', 'Most liquid assets', 'Currency')
    }
    
    leverage_metrics = {
        'debtToEquityRatio': ('Debt-to-Equity Ratio', 'Total debt divided by shareholders\' equity', 'Ratio'),
        'debtToAssetsRatio': ('Debt-to-Assets Ratio', 'Total debt divided by total assets', 'Ratio'),
        'interestCoverageRatio': ('Interest Coverage Ratio', 'EBIT divided by interest expense', 'Times'),
        'financialLeverageRatio': ('Financial Leverage', 'Total assets divided by shareholders\' equity', 'Ratio'),
        'netDebtToEBITDA': ('Net Debt to EBITDA', 'Net debt divided by EBITDA', 'Times')
    }
    
    efficiency_metrics = {
        'assetTurnover': ('Asset Turnover', 'Revenue divided by average total assets', 'Times'),
        'inventoryTurnover': ('Inventory Turnover', 'Cost of goods sold divided by average inventory', 'Times'),
        'receivablesTurnover': ('Receivables Turnover', 'Revenue divided by average receivables', 'Times'),
        'payablesTurnover': ('Payables Turnover', 'Cost of goods sold divided by average payables', 'Times'),
        'daysOfSalesOutstanding': ('Days Sales Outstanding (DSO)', 'Average collection period for receivables', 'Days'),
        'daysOfInventoryOutstanding': ('Days Inventory Outstanding (DIO)', 'Average holding period for inventory', 'Days'),
        'cashConversionCycle': ('Cash Conversion Cycle', 'DSO + DIO - DPO', 'Days')
    }
    
    valuation_metrics = {
        'priceToEarningsRatio': ('Price-to-Earnings (P/E)', 'Stock price divided by earnings per share', 'Ratio'),
        'priceToBookRatio': ('Price-to-Book (P/B)', 'Stock price divided by book value per share', 'Ratio'),
        'priceToSalesRatio': ('Price-to-Sales (P/S)', 'Market cap divided by revenue', 'Ratio'),
        'enterpriseValueMultiple': ('EV/EBITDA', 'Enterprise value divided by EBITDA', 'Multiple'),
        'evToSales': ('EV/Sales', 'Enterprise value divided by revenue', 'Multiple'),
        'marketCap': ('Market Capitalization', 'Stock price times shares outstanding', 'Currency'),
        'enterpriseValue': ('Enterprise Value', 'Market cap plus net debt', 'Currency')
    }
    
    # Add metrics to catalog
    for metric_dict, category in [
        (profitability_metrics, 'Profitability Metrics'),
        (liquidity_metrics, 'Liquidity Metrics'),
        (leverage_metrics, 'Leverage & Solvency Metrics'),
        (efficiency_metrics, 'Efficiency Metrics'),
        (valuation_metrics, 'Valuation Metrics')
    ]:
        for metric_key, (display_name, definition, unit) in metric_dict.items():
            if metric_key in df.columns:
                catalog[category].append({
                    'key': metric_key,
                    'name': display_name,
                    'definition': definition,
                    'unit': unit
                })
    
    return catalog


# =============================================================================
# APPENDIX C: METHODOLOGY DOCUMENTATION
# =============================================================================

def _build_appendix_c_methodology(collector, companies: Dict) -> str:
    """Build Appendix C: Methodology & Technical Documentation"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix C: Methodology & Technical Documentation</h3>'
    html += '<p style="margin-bottom: 25px;">This section documents the complete methodology used throughout this analysis, including data collection procedures, calculation methods, statistical techniques, and analytical frameworks.</p>'
    
    # C.1 Data Collection
    html += '<h4>C.1 Data Collection & Sources</h4>'
    html += _document_data_collection_methodology(collector, companies)
    
    # C.2 Financial Calculations
    html += '<h4>C.2 Financial Calculations & Transformations</h4>'
    html += _document_financial_calculations()
    
    # C.3 Statistical Methods
    html += '<h4>C.3 Statistical Analysis Methods</h4>'
    html += _document_statistical_methods()
    
    # C.4 Regime Detection
    html += '<h4>C.4 Regime Detection & Change-Point Analysis</h4>'
    html += _document_regime_detection_methodology()
    
    # C.5 Scenario Modeling
    html += '<h4>C.5 Scenario Modeling & Forecasting</h4>'
    html += _document_scenario_modeling_methodology()
    
    # C.6 Risk Assessment
    html += '<h4>C.6 Risk Assessment & Scoring Methods</h4>'
    html += _document_risk_assessment_methodology()
    
    # C.7 Valuation
    html += '<h4>C.7 Valuation Methodologies</h4>'
    html += _document_valuation_methodologies()
    
    html += '</div>'
    return html


def _document_data_collection_methodology(collector, companies: Dict) -> str:
    """Document data collection methodology"""
    
    methodology_text = f"""
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Data Collection Framework:

Primary Data Source: Financial Modeling Prep (FMP) API
• API Version: Latest stable release
• Companies Analyzed: {len(companies)} companies
• Historical Coverage: {collector.years} years of annual financial data
• Data Types: Financial statements, ratios, market prices, analyst estimates, institutional ownership

Data Collection Procedure:
1. Company Financial Statements: Income statements, balance sheets, and cash flow statements collected via FMP 
   /income-statement, /balance-sheet-statement, and /cash-flow-statement endpoints
2. Financial Ratios: Comprehensive ratio analysis via /ratios endpoint
3. Key Metrics: Additional performance metrics via /key-metrics endpoint
4. Market Data: Daily and monthly price data via /historical-price-full endpoint
5. Institutional Data: Ownership and insider trading via /institutional-holder and /insider-trading endpoints
6. Economic Data: Macro indicators from Federal Reserve Economic Data (FRED)

Data Quality Controls:
• Automated validation of data completeness
• Cross-verification between multiple data sources
• Outlier detection and flagging
• Currency and unit standardization
• Date alignment and temporal consistency checks

Data Processing Pipeline:
1. Raw data extraction via API calls with retry logic
2. Data normalization and standardization
3. Missing value handling and interpolation where appropriate
4. Derived metric calculation (growth rates, ratios)
5. Data consolidation into unified analytical dataset

Update Frequency: Analysis reflects data as of {datetime.now().strftime('%Y-%m-%d')}
</pre>
"""
    return methodology_text


def _document_financial_calculations() -> str:
    """Document financial calculation methods"""
    
    calculations_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Financial Calculation Methodology:

Growth Rate Calculations:
• Year-over-Year Growth: ((Current Year - Prior Year) / Prior Year) × 100
• Compound Annual Growth Rate (CAGR): ((Ending Value / Beginning Value)^(1/n) - 1) × 100
• Applied to: Revenue, net income, cash flows, assets, and other key metrics

Margin Calculations:
• Gross Margin: (Gross Profit / Revenue) × 100
• Operating Margin: (Operating Income / Revenue) × 100
• Net Margin: (Net Income / Revenue) × 100
• EBITDA Margin: (EBITDA / Revenue) × 100

Return Metrics:
• ROE: (Net Income / Average Shareholders' Equity) × 100
• ROA: (Net Income / Average Total Assets) × 100
• ROIC: (Operating Income × (1 - Tax Rate)) / Invested Capital × 100

Liquidity Ratios:
• Current Ratio: Current Assets / Current Liabilities
• Quick Ratio: (Current Assets - Inventory) / Current Liabilities
• Cash Ratio: Cash and Cash Equivalents / Current Liabilities

Leverage Ratios:
• Debt-to-Equity: Total Debt / Total Shareholders' Equity
• Debt-to-Assets: Total Debt / Total Assets
• Interest Coverage: EBIT / Interest Expense

Efficiency Ratios:
• Asset Turnover: Revenue / Average Total Assets
• Inventory Turnover: Cost of Goods Sold / Average Inventory
• Receivables Turnover: Revenue / Average Accounts Receivable

Per Share Calculations:
• Earnings Per Share (EPS): Net Income / Weighted Average Shares Outstanding
• Book Value Per Share: Total Equity / Shares Outstanding
• Free Cash Flow Per Share: Free Cash Flow / Shares Outstanding

Data Precedence for Conflicting Fields:
Income Statement > Cash Flow Statement > Balance Sheet > Key Metrics > Ratios
(Later sources overwrite earlier sources for overlapping fields)
</pre>
"""
    return calculations_text


def _document_statistical_methods() -> str:
    """Document statistical analysis methods"""
    
    statistical_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Statistical Analysis Methodology:

Correlation Analysis:
• Method: Pearson correlation coefficient
• Formula: r = Σ((x - x̄)(y - ȳ)) / √(Σ(x - x̄)² × Σ(y - ȳ)²)
• Interpretation: r > 0.7 (strong positive), 0.3-0.7 (moderate), < 0.3 (weak)
• Statistical Significance: p-value < 0.05 for significance testing
• Applied to: Revenue growth vs. macro-economic indicators

Regression Analysis:
• Method: Ordinary Least Squares (OLS) regression
• Model: y = β₀ + β₁x₁ + ... + βₙxₙ + ε
• Software: statsmodels Python library
• Diagnostics: R², Adjusted R², t-statistics, p-values, residual analysis
• Validation: Cross-validation and out-of-sample testing where applicable

Descriptive Statistics:
• Central Tendency: Mean, median, mode
• Dispersion: Standard deviation, variance, range, interquartile range
• Distribution: Skewness, kurtosis, normality tests
• Time Series: Moving averages, trends, seasonality analysis

Change-Point Detection:
• Method: Statistical breakpoint analysis
• Tests: t-test for mean changes, F-test for variance changes
• Threshold: p-value < 0.10 for regime detection
• Minimum Segment Length: 3 years
• Maximum Regimes: 3 per company

Hypothesis Testing:
• Significance Level: α = 0.05 (95% confidence)
• Tests Used: t-tests, F-tests, chi-square tests
• Multiple Comparison Correction: Bonferroni correction when applicable

Risk Metrics:
• Volatility: Standard deviation of returns
• Beta: Covariance with market / Variance of market
• Sharpe Ratio: (Return - Risk-free rate) / Standard deviation
• Maximum Drawdown: Largest peak-to-trough decline

Quality Control:
• Outlier Detection: Values > 3 standard deviations flagged
• Data Validation: Range checks and logical consistency tests
• Sensitivity Analysis: Testing robustness of results to assumptions
</pre>
"""
    return statistical_text


def _document_regime_detection_methodology() -> str:
    """Document regime detection methodology"""
    
    regime_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Regime Detection & Change-Point Analysis:

Methodological Framework:
• Objective: Identify distinct performance regimes in company revenue growth
• Approach: Statistical change-point detection using variance and mean shifts
• Minimum Data Requirement: 8 years of historical data
• Minimum Segment Length: 3 years per regime
• Maximum Regimes: 3 per company (avoiding over-segmentation)

Detection Algorithm:
1. Revenue Growth Calculation: Year-over-year percentage changes
2. Window-Based Analysis: Rolling comparison windows of minimum 3 years
3. Statistical Testing:
   - t-test for mean differences between segments (p < 0.10)
   - F-test for variance changes (F-ratio > 2 or < 0.5)
4. Change-Point Identification: Periods where both tests indicate structural break
5. Regime Consolidation: Merging adjacent similar regimes

Regime Characterization:
• Average Growth: Mean revenue growth rate within regime period
• Volatility: Standard deviation of growth within regime
• Duration: Number of years in regime
• Trend Direction: Improving vs. declining performance
• Stability Score: 10 - volatility (normalized scale)

Performance Metrics per Regime:
• Revenue growth (mean, volatility)
• Profitability margins (gross, operating, net)
• Return metrics (ROE, ROA)
• Leverage ratios
• Cash flow generation

Quality Scoring:
Components: Revenue growth, margins, ROE, stability
Scale: 0-10 with classifications (High Performance > 7, Standard 5-7, Underperformance < 5)

Validation:
• Historical consistency checks
• Economic event correlation
• Management change analysis
• Industry cycle verification

Limitations:
• Requires sufficient historical data (minimum 8 years)
• Sensitive to outlier years
• May not capture within-year regime changes
• Assumes discrete regime structure rather than continuous evolution
</pre>
"""
    return regime_text


def _document_scenario_modeling_methodology() -> str:
    """Document scenario modeling methodology"""
    
    scenario_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Scenario Modeling & Forecasting Framework:

Three-Scenario Architecture:

1. Soft Landing Scenario:
   • Description: Gradual economic slowdown with controlled inflation
   • Assumptions: GDP -1.0%, CPI -1.5%, Unemployment +0.5pp, 10Y Treasury -50bp
   • Market Impact: S&P 500 -5%, moderate equity volatility
   • Revenue Impact: Model-based projection using established correlations

2. Re-acceleration Scenario:
   • Description: Economic growth rebound with moderate inflation
   • Assumptions: GDP +2.0%, CPI +1.0%, Unemployment -0.3pp, 10Y Treasury +50bp
   • Market Impact: S&P 500 +10%, increased economic activity
   • Revenue Impact: Positive correlation with growth indicators

3. Economic Shock Scenario:
   • Description: Severe contraction with deflationary pressures
   • Assumptions: GDP -3.0%, CPI -2.0%, Unemployment +2.0pp, 10Y Treasury -150bp
   • Market Impact: S&P 500 -25%, risk-off environment
   • Revenue Impact: Severe downside using stress-test parameters

Forecasting Methodology:

Baseline Forecast:
• Method: 3-year rolling average of recent revenue growth
• Adjustment: Outlier removal and trend analysis
• Validation: Comparison with analyst estimates where available

Scenario Impact Calculation:
1. Primary Indicator Identification: Best-correlated macro variable from Section 9
2. Sensitivity Calibration: Slope coefficient from univariate regression
3. Impact Translation: Macro change × sensitivity = revenue growth impact
4. Forecast Adjustment: Baseline ± scenario impact = scenario-specific forecast

Model Quality Assessment:
• Confidence Level: Based on regression R² (higher R² = higher confidence)
• Quality Classification: High (R² > 0.4), Moderate (0.2-0.4), Low (< 0.2)
• Sensitivity Range: Difference between best and worst scenario outcomes

Uncertainty Quantification:
• Confidence Intervals: ±1.96 × standard error for 95% confidence
• Historical Volatility Integration: Past variability informs forecast bands
• Regime Stability Factor: More stable regimes → tighter confidence intervals
• Model Uncertainty: Incorporated from regression diagnostics

Risk-Return Analysis:
• Upside Potential: Re-acceleration forecast - baseline forecast
• Downside Risk: Baseline forecast - shock scenario forecast
• Profile Classification: Favorable (upside > 1.5× downside), Balanced, Defensive

Forecast Horizon: 1-2 years forward-looking

Validation & Testing:
• Back-testing against historical scenarios
• Comparison with realized outcomes where available
• Sensitivity analysis to assumption changes
• Expert judgment overlay for extreme scenarios

Limitations:
• Linear extrapolation may not capture non-linear effects
• Past correlations may not persist in future
• Scenario assumptions represent point estimates, not distributions
• Company-specific factors may override macro trends
</pre>
"""
    return scenario_text


def _document_risk_assessment_methodology() -> str:
    """Document risk assessment methodology"""
    
    risk_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Risk Assessment & Scoring Framework:

Risk Categories & Metrics:

1. Financial Risk:
   • Leverage Risk: High debt-to-equity (> 2.0) or interest coverage (< 2.0)
   • Liquidity Risk: Current ratio < 1.5 or declining cash position
   • Profitability Risk: Negative margins or declining ROE
   • Cash Flow Risk: Negative FCF for 2+ consecutive years

2. Operational Risk:
   • Revenue Volatility: Standard deviation of growth rates
   • Margin Compression: Year-over-year margin decline > 150bp
   • Efficiency Decline: Deteriorating turnover ratios
   • Working Capital Stress: Increasing cash conversion cycle

3. Market Risk:
   • Valuation Risk: Extreme multiples vs. peers
   • Price Volatility: Historical stock price standard deviation
   • Beta Risk: Market sensitivity > 1.5
   • Liquidity Risk: Low trading volume or high bid-ask spreads

4. Forecast Uncertainty:
   • Model Uncertainty: Low R² in regression models
   • Scenario Dispersion: Wide range between scenarios
   • Regime Instability: Frequent regime changes
   • Historical Volatility: High revenue growth variability

Risk Scoring Methodology:

Component Scores (0-10 scale):
• 0-3: Low Risk (Green)
• 4-6: Moderate Risk (Yellow)
• 7-8: High Risk (Orange)
• 9-10: Very High Risk (Red)

Composite Risk Score Calculation:
1. Weighted average of component scores
2. Adjustments for industry-specific factors
3. Overlay for company-specific events
4. Final score classification

Alert Triggers:
• Negative FCF streak ≥ 2 years
• Interest coverage < 2×
• Debt-to-equity ratio increase > 50bp year-over-year
• Margin compression > 150bp year-over-year
• Cash drawdown > 20% year-over-year

Risk Mitigation Considerations:
• Diversification benefits
• Industry cycle positioning
• Management quality factors
• Competitive moat strength
• Balance sheet flexibility

Limitations:
• Backward-looking data may not reflect future risks
• Industry-specific risks may require adjustment
• Qualitative factors not fully captured
• Correlation breakdown in crisis scenarios
</pre>
"""
    return risk_text


def _document_valuation_methodologies() -> str:
    """Document valuation methodologies"""
    
    valuation_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Valuation Methodologies:

Multiple-Based Valuation:

1. Price-to-Earnings (P/E) Ratio:
   • Formula: Stock Price / Earnings Per Share
   • Interpretation: Lower P/E suggests undervaluation (relative to peers/history)
   • Limitations: Sensitive to earnings quality and accounting methods
   • Adjustments: Exclude non-recurring items for normalized P/E

2. Price-to-Book (P/B) Ratio:
   • Formula: Stock Price / Book Value Per Share
   • Interpretation: P/B < 1 suggests trading below net asset value
   • Limitations: Less relevant for asset-light businesses
   • Adjustments: Tangible book value for asset quality

3. Enterprise Value to EBITDA (EV/EBITDA):
   • Formula: (Market Cap + Net Debt) / EBITDA
   • Interpretation: Capital structure-neutral comparison
   • Limitations: Ignores CapEx intensity differences
   • Adjustments: Normalize for one-time items

4. EV/Sales:
   • Formula: Enterprise Value / Revenue
   • Interpretation: Useful for pre-profit or low-margin companies
   • Limitations: Ignores profitability differences
   • Adjustments: Consider growth rates and margin trajectories

Relative Valuation:
• Peer Comparison: Valuation ladders showing company position vs. peers
• Sector Medians: Reference points for over/undervaluation assessment
• Historical Context: Current multiples vs. company's own history
• Growth Adjustment: PEG ratio (P/E / growth rate) for growth companies

Valuation Buckets:
• Classification: Quintiles or custom ranges based on multiple distribution
• Labels: Value, Fair Value, Growth, Premium
• Portfolio Context: Concentration in each bucket

Analyst Consensus:
• Price Targets: Mean, median, high, low from analyst coverage
• Target Convergence: Dispersion as measure of uncertainty
• Recommendation Distribution: Buy/Hold/Sell consensus
• Revision Trends: Direction of recent estimate changes

Fair Value Estimation:
• DCF Framework: Discounted cash flow where sufficient data available
• Multiples Application: Peer median multiple × company metric
• Scenario-Weighted: Probability-weighted scenario outcomes
• Range Estimation: Conservative to optimistic value range

Limitations & Considerations:
• Multiples reflect market sentiment, not intrinsic value
• Peer selection subjectivity
• Cyclical adjustments needed for EV/EBITDA
• Growth expectations embedded in multiples
• Market inefficiencies may persist
• Qualitative factors not captured
</pre>
"""
    return valuation_text


# =============================================================================
# APPENDIX D: COMPREHENSIVE GLOSSARY
# =============================================================================

def _build_appendix_d_glossary() -> str:
    """Build Appendix D: Financial & Economic Terms Glossary"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix D: Financial & Economic Terms Glossary</h3>'
    html += '<p style="margin-bottom: 25px;">This glossary provides clear, concise definitions of all financial, economic, and statistical terms used throughout this analysis. Terms are organized alphabetically for easy reference.</p>'
    
    # Generate comprehensive glossary
    glossary_terms = _generate_comprehensive_glossary()
    
    # Sort terms alphabetically
    sorted_terms = sorted(glossary_terms.items())
    
    # Group by first letter
    current_letter = ''
    terms_list = []
    
    for term, definition in sorted_terms:
        first_letter = term[0].upper()
        
        # Start new section for new letter
        if first_letter != current_letter:
            if terms_list:
                # Output previous section
                terms_df = pd.DataFrame(terms_list, columns=['Term', 'Definition'])
                html += f'<h4>Terms Starting with "{current_letter}"</h4>'
                html += build_data_table(terms_df, table_id=f"glossary-{current_letter}", sortable=False, searchable=True)
                terms_list = []
            current_letter = first_letter
        
        terms_list.append([term, definition])
    
    # Output last section
    if terms_list:
        terms_df = pd.DataFrame(terms_list, columns=['Term', 'Definition'])
        html += f'<h4>Terms Starting with "{current_letter}"</h4>'
        html += build_data_table(terms_df, table_id=f"glossary-{current_letter}", sortable=False, searchable=True)
    
    html += '</div>'
    return html


def _generate_comprehensive_glossary() -> Dict[str, str]:
    """Generate comprehensive glossary of terms"""
    
    glossary = {
        # Financial Statement Terms
        'EBITDA': 'Earnings Before Interest, Taxes, Depreciation, and Amortization - a measure of operating profitability that excludes non-cash expenses and financing costs',
        'EBIT': 'Earnings Before Interest and Taxes - operating profit before financing costs and tax effects',
        'Free Cash Flow': 'Operating cash flow minus capital expenditures - cash available for distribution to investors',
        'Operating Cash Flow': 'Cash generated from core business operations, excluding investing and financing activities',
        'Working Capital': 'Current assets minus current liabilities - measure of short-term financial health',
        'Net Debt': 'Total debt minus cash and cash equivalents - net financial obligations',
        'Gross Profit': 'Revenue minus cost of goods sold - profit before operating expenses',
        'Operating Income': 'Gross profit minus operating expenses - profit from core operations',
        'Net Income': 'Bottom-line profit after all expenses, interest, and taxes',
        
        # Ratio Terms
        'Current Ratio': 'Current assets divided by current liabilities - measure of short-term liquidity',
        'Quick Ratio': 'Liquid assets divided by current liabilities - more conservative liquidity measure',
        'Debt-to-Equity': 'Total debt divided by shareholders\' equity - measure of financial leverage',
        'Interest Coverage': 'EBIT divided by interest expense - ability to service debt',
        'Asset Turnover': 'Revenue divided by average assets - efficiency in asset utilization',
        'ROE': 'Return on Equity - net income divided by shareholders\' equity, expressed as percentage',
        'ROA': 'Return on Assets - net income divided by total assets, expressed as percentage',
        'ROIC': 'Return on Invested Capital - operating return on capital employed in business',
        
        # Valuation Terms
        'P/E Ratio': 'Price-to-Earnings ratio - stock price divided by earnings per share',
        'P/B Ratio': 'Price-to-Book ratio - market value relative to book value',
        'EV/EBITDA': 'Enterprise Value to EBITDA multiple - common valuation metric',
        'Market Capitalization': 'Total market value of company\'s outstanding shares',
        'Enterprise Value': 'Market cap plus net debt - total value of business',
        'PEG Ratio': 'P/E ratio divided by growth rate - growth-adjusted valuation',
        
        # Statistical Terms
        'Correlation': 'Statistical measure of the relationship between two variables, ranging from -1 to +1',
        'R-squared': 'Coefficient of determination - proportion of variance explained by regression model',
        'p-value': 'Probability of observing results if null hypothesis is true - measures statistical significance',
        't-statistic': 'Test statistic for hypothesis testing - ratio of coefficient to standard error',
        'Standard Deviation': 'Measure of dispersion from the mean - indicates variability',
        'Beta': 'Measure of systematic risk - sensitivity to market movements',
        'Regression': 'Statistical method for modeling relationships between variables',
        'CAGR': 'Compound Annual Growth Rate - geometric average growth rate over time period',
        
        # Economic Terms
        'GDP': 'Gross Domestic Product - total value of goods and services produced in economy',
        'CPI': 'Consumer Price Index - measure of inflation based on consumer goods basket',
        'Federal Funds Rate': 'Interest rate at which banks lend to each other overnight',
        'Yield Curve': 'Graph of interest rates across different maturity periods',
        'Monetary Policy': 'Central bank actions to manage money supply and interest rates',
        'Fiscal Policy': 'Government spending and taxation policies',
        'Treasury Yield': 'Return on US government bonds - risk-free rate benchmark',
        'VIX Index': 'Volatility Index - market expectation of 30-day volatility',
        
        # Analysis Terms
        'Regime': 'Distinct period characterized by specific performance patterns',
        'Change-Point': 'Statistical point where structural break in data occurs',
        'Scenario Analysis': 'Evaluation of different potential future outcomes',
        'Sensitivity Analysis': 'Assessment of how changes in inputs affect outputs',
        'Backtesting': 'Testing model performance on historical data',
        'Forecast Horizon': 'Time period for which predictions are made',
        'Confidence Interval': 'Range within which true value likely falls with specified probability',
        
        # Risk Terms
        'Downside Risk': 'Probability and magnitude of potential losses',
        'Maximum Drawdown': 'Largest peak-to-trough decline in value',
        'Sharpe Ratio': 'Risk-adjusted return - excess return per unit of volatility',
        'Value at Risk': 'Maximum expected loss over specified time period at given confidence level',
        'Systematic Risk': 'Market-wide risk that cannot be diversified away',
        'Idiosyncratic Risk': 'Company-specific risk that can be diversified',
        
        # Other Financial Terms
        'Diluted EPS': 'Earnings per share assuming conversion of all dilutive securities',
        'Book Value': 'Net asset value - total assets minus liabilities',
        'Tangible Book Value': 'Book value minus intangible assets and goodwill',
        'Cash Conversion Cycle': 'Time between cash outflows and inflows in operations',
        'Days Sales Outstanding': 'Average collection period for receivables',
        'Inventory Turnover': 'Number of times inventory sold and replaced per period',
        'Accruals': 'Difference between net income and operating cash flow',
        'Capitalization': 'Total amount of capital invested in business (debt + equity)'
    }
    
    return glossary


# =============================================================================
# APPENDIX E: DATA QUALITY
# =============================================================================

def _build_appendix_e_data_quality(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                    companies: Dict, collector) -> str:
    """Build Appendix E: Data Quality & Coverage Assessment"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix E: Data Quality & Coverage Assessment</h3>'
    html += '<p style="margin-bottom: 25px;">This section documents data availability, quality metrics, and coverage limitations for the analyzed companies and time periods.</p>'
    
    # E.1 Financial Data Coverage
    html += '<h4>E.1 Financial Data Coverage</h4>'
    
    coverage_data = []
    for company_name, ticker in companies.items():
        company_data = df[df['Company'] == company_name]
        
        if not company_data.empty:
            years_available = len(company_data)
            latest_year = int(company_data['Year'].max())
            earliest_year = int(company_data['Year'].min())
            
            # Calculate completeness
            total_fields = len(company_data.columns)
            non_null_count = company_data.notna().sum().sum()
            total_cells = len(company_data) * total_fields
            completeness = (non_null_count / total_cells * 100) if total_cells > 0 else 0
            
            # Quality score
            if completeness >= 90:
                quality = "Excellent"
            elif completeness >= 75:
                quality = "Good"
            elif completeness >= 60:
                quality = "Fair"
            else:
                quality = "Limited"
            
            coverage_data.append({
                'Company': company_name,
                'Years Available': years_available,
                'Data Completeness': f"{completeness:.1f}%",
                'Latest Year': latest_year,
                'Earliest Year': earliest_year,
                'Quality Score': quality
            })
    
    if coverage_data:
        coverage_df = pd.DataFrame(coverage_data)
        html += build_data_table(coverage_df, table_id="coverage-table", sortable=True)
    
    # E.2 Economic Data Coverage
    html += '<h4>E.2 Economic Data Coverage</h4>'
    
    if not economic_df.empty:
        indicator_count = len(economic_df.columns) - 2
        total_cells = len(economic_df) * indicator_count
        non_null_cells = economic_df.drop(columns=['Year', 'Date']).notna().sum().sum()
        econ_completeness = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
        
        econ_text = f"""
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Economic Data Quality Assessment:

• Time Period: {int(economic_df['Year'].min())} - {int(economic_df['Year'].max())}
• Total Years: {len(economic_df)}
• Indicators: {indicator_count}
• Source: Federal Reserve Economic Data (FRED)
• Update Frequency: Annual aggregation
• Data Completeness: {econ_completeness:.1f}%

Key Economic Indicators Coverage:
• GDP & Real GDP: Complete coverage
• Inflation Metrics (CPI, PCE): Complete coverage
• Labor Market (Unemployment, Payrolls): Complete coverage
• Interest Rates (Fed Funds, Treasury Curve): Complete coverage
• Market Indices (S&P 500, VIX): Complete coverage
• Housing Market Indicators: Complete coverage

Data Quality: High - sourced from official government statistical releases
</pre>
"""
        html += econ_text
    
    # E.3 Data Limitations & Disclaimers
    html += '<h4>E.3 Data Limitations & Disclaimers</h4>'
    
    limitations_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Data Quality Limitations & Disclaimers:

1. Historical Data Availability:
   • Coverage varies by company based on public trading history
   • Newer companies have limited historical comparisons
   • M&A activity may create data discontinuities

2. Data Accuracy:
   • Data sourced from third-party providers (FMP API)
   • Financial statements reflect company filings but may contain restatements
   • Economic data reflects official releases but subject to revisions

3. Temporal Considerations:
   • Analysis based on annual data - intra-year variations not captured
   • Latest data reflects most recent filings (may be several months old)
   • Economic indicators subject to periodic government revisions

4. Comparability Issues:
   • Accounting standards may differ (GAAP vs. IFRS)
   • Industry-specific metrics may limit cross-sector comparisons
   • One-time events and non-recurring items may distort trends

5. Forward-Looking Limitations:
   • Past performance does not guarantee future results
   • Projections based on historical correlations that may not persist
   • Scenario analysis represents illustrative cases, not predictions

6. Data Completeness:
   • Some fields may be unavailable for certain companies or periods
   • Institutional ownership data limited to recent quarters
   • Insider trading data reflects reported transactions only

7. Market Data:
   • Stock prices reflect market valuations subject to various influences
   • Volatility measures based on historical patterns
   • Trading volumes and liquidity metrics are time-sensitive

Recommended Use:
This analysis provides comprehensive financial intelligence for informed decision-making but should be 
supplemented with:
• Current news and company developments
• Management commentary and guidance
• Industry research and competitive analysis
• Professional financial advice for investment decisions
</pre>
"""
    html += limitations_text
    
    html += '</div>'
    return html


# =============================================================================
# APPENDIX F: COMPANY PROFILES
# =============================================================================

def _build_appendix_f_company_profiles(profiles_df: pd.DataFrame, companies: Dict) -> str:
    """Build Appendix F: Company Profiles & Industry Classification"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix F: Company Profiles & Industry Classification</h3>'
    html += '<p style="margin-bottom: 25px;">Complete company profiles including sector classifications, industry groups, exchange listings, and key identifiers.</p>'
    
    html += '<h4>F.1 Company Identification & Classification</h4>'
    
    if not profiles_df.empty:
        profile_data = []
        for company_name, ticker in companies.items():
            profile = profiles_df[profiles_df['Symbol'] == ticker]
            if not profile.empty:
                p = profile.iloc[0]
                employees = p.get('fullTimeEmployees', None)
                if pd.notna(employees) and str(employees) != 'None':
                    try:
                        employees_str = f"{int(employees):,}"
                    except:
                        employees_str = "N/A"
                else:
                    employees_str = "N/A"
                
                profile_data.append({
                    'Company': company_name,
                    'Ticker': ticker,
                    'Sector': str(p.get('sector', 'N/A')),
                    'Industry': str(p.get('industry', 'N/A')),
                    'Exchange': str(p.get('exchange', 'N/A')),
                    'Country': str(p.get('country', 'N/A')),
                    'Employees': employees_str
                })
            else:
                profile_data.append({
                    'Company': company_name,
                    'Ticker': ticker,
                    'Sector': 'N/A',
                    'Industry': 'N/A',
                    'Exchange': 'N/A',
                    'Country': 'N/A',
                    'Employees': 'N/A'
                })
        
        if profile_data:
            profile_df = pd.DataFrame(profile_data)
            html += build_data_table(profile_df, table_id="profiles-table", sortable=True)
    else:
        html += build_info_box("Company profile data not available.", "warning")
    
    html += '</div>'
    return html


# =============================================================================
# APPENDIX G: REFERENCES & DATA SOURCES
# =============================================================================

def _build_appendix_g_references() -> str:
    """Build Appendix G: References & Data Sources"""
    
    html = '<div class="info-section">'
    html += '<h3>Appendix G: References & Data Sources</h3>'
    
    # G.1 Data Sources
    html += '<h4>G.1 Data Sources</h4>'
    
    sources_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Primary Data Sources:

1. Financial Modeling Prep (FMP)
   • Website: https://financialmodelingprep.com
   • Type: Financial data API provider
   • Coverage: US and international public companies
   • Data Types: Financial statements, ratios, market data, institutional ownership
   • Update Frequency: Real-time to daily updates
   • Data Quality: Sourced from SEC filings and official company reports

2. Federal Reserve Economic Data (FRED)
   • Website: https://fred.stlouisfed.org
   • Provider: Federal Reserve Bank of St. Louis
   • Coverage: Comprehensive US economic indicators
   • Data Types: GDP, inflation, employment, interest rates, market indices
   • Update Frequency: Various (monthly, quarterly, annual)
   • Data Quality: Official government and central bank statistics

3. U.S. Securities and Exchange Commission (SEC)
   • Website: https://www.sec.gov
   • Type: Regulatory filings database (EDGAR)
   • Coverage: All US public companies
   • Data Types: 10-K, 10-Q, 8-K filings, insider transactions (Form 4)
   • Reliability: Primary source for regulatory disclosures
</pre>
"""
    html += sources_text
    
    # G.2 Analytical Frameworks
    html += '<h4>G.2 Analytical Frameworks</h4>'
    
    frameworks_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Analytical Frameworks & Methodologies:

1. DuPont Analysis
   • Developer: DuPont Corporation (1920s)
   • Application: ROE decomposition into profitability, efficiency, leverage
   • Formula: ROE = Net Margin × Asset Turnover × Equity Multiplier
   • Reference: Standard financial analysis textbook methodology

2. Graham & Dodd Value Investing
   • Authors: Benjamin Graham and David Dodd
   • Publication: "Security Analysis" (1934)
   • Application: Fundamental analysis and intrinsic value estimation
   • Key Concepts: Margin of safety, Mr. Market, book value analysis

3. Modern Portfolio Theory
   • Developer: Harry Markowitz
   • Publication: "Portfolio Selection" (1952)
   • Application: Risk-return optimization, diversification
   • Key Metrics: Beta, correlation, Sharpe ratio

4. Regression Analysis
   • Statistical Method: Ordinary Least Squares (OLS)
   • Software: statsmodels Python library
   • Application: Correlation analysis, predictive modeling
   • Reference: Standard econometric methodology

5. Change-Point Detection
   • Statistical Method: Variance and mean shift testing
   • Application: Regime identification in time series
   • Tests: t-test, F-test for structural breaks
   • Reference: Time series analysis literature
</pre>
"""
    html += frameworks_text
    
    # G.3 Software & Tools
    html += '<h4>G.3 Software & Tools</h4>'
    
    tools_text = """
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Software & Tools Used:

Programming Language:
• Python 3.x

Key Libraries:
• pandas: Data manipulation and analysis
• numpy: Numerical computing
• scipy: Scientific computing and statistics
• statsmodels: Statistical modeling and hypothesis testing
• plotly: Interactive data visualization
• Custom FinancialDataCollection class for API integration

Data Processing:
• Automated data validation and quality control
• Derived metric calculation engine
• Multi-source data integration

Analysis Infrastructure:
• Modular section-based analysis framework
• Automated report generation pipeline
• Web-based interactive visualization

Quality Assurance:
• Data validation checks at multiple stages
• Statistical significance testing
• Outlier detection and handling
• Cross-verification between data sources
</pre>
"""
    html += tools_text
    
    # G.4 Disclaimers
    html += '<h4>G.4 Disclaimers</h4>'
    
    disclaimer_text = f"""
<pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
Important Disclaimers:

1. Not Investment Advice:
   This analysis is provided for informational purposes only and does not constitute investment advice, 
   recommendation, or solicitation to buy or sell any securities. Readers should consult with qualified 
   financial advisors before making investment decisions.

2. Forward-Looking Statements:
   This report contains forward-looking statements, projections, and scenarios that involve risks and 
   uncertainties. Actual results may differ materially from those projected. Past performance is not 
   indicative of future results.

3. Data Accuracy:
   While efforts have been made to ensure data accuracy, the analysis relies on third-party data sources. 
   No warranty is made regarding the accuracy, completeness, or timeliness of the information provided.

4. Model Limitations:
   Statistical models are simplifications of complex realities. Model results should be interpreted within 
   the context of their assumptions and limitations. Models may not capture all relevant factors.

5. Market Risks:
   Investment in securities involves substantial risk of loss. Market conditions can change rapidly and 
   unpredictably. Diversification does not guarantee profits or protect against losses.

6. Professional Advice:
   This analysis does not replace the need for professional financial, tax, or legal advice. Readers 
   should seek appropriate professional guidance for their specific circumstances.

7. Intellectual Property:
   This report is provided for the recipient's internal use only. Redistribution or reproduction without 
   permission is prohibited. Data providers retain rights to their underlying data.

8. Regulatory Compliance:
   Users are responsible for ensuring their use of this analysis complies with applicable laws and 
   regulations in their jurisdiction.

Date of Analysis: {datetime.now().strftime('%Y-%m-%d')}

This appendix and the associated analysis represent a comprehensive financial intelligence framework 
designed to support informed decision-making through rigorous quantitative analysis and professional-grade 
methodologies.
</pre>
"""
    html += disclaimer_text
    
    html += '</div>'
    return html