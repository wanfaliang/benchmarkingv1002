"""
Section 8: Macroeconomic Environment Analysis
Phase 1: Scaffolding + Subsections 8A (Economic Indicators) and 8B (Interest Rates)
"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import json

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_data_table,
    build_plotly_chart,
    build_section_divider,
    build_info_box,
    format_percentage,
    format_number,
    build_enhanced_table,
    build_badge,
    build_colored_cell
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 8: Macroeconomic Environment Analysis
    
    Comprehensive macro analysis including:
    - Economic indicators snapshot and trends
    - Interest rate environment and yield curve analysis
    - Inflation dynamics and monetary policy assessment
    - Growth and employment indicators
    - Market conditions and risk indicators
    - Sector-specific macro correlations
    - Professional visualization suite
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    try:
        # Extract data from collector
        companies = collector.companies
        df = collector.get_all_financial_data()
        
        # Get macroeconomic data
        try:
            economic_df = collector.get_economic()
        except:
            economic_df = pd.DataFrame()
        
        # Get profiles for context
        try:
            profiles = collector.get_profiles()
        except:
            profiles = pd.DataFrame()
        
        # Build all subsections
        section_8a_html = _build_section_8a_economic_indicators(economic_df, companies, collector.years)
        section_8b_html = _build_section_8b_interest_rates(economic_df, companies)
        section_8c_html = _build_section_8c_inflation_dynamics(economic_df, companies)
        section_8d_html = _build_section_8d_growth_employment(economic_df, companies)
        section_8e_html = _build_section_8e_market_risk(economic_df, companies)
        section_8f_html = _build_section_8f_visualizations(economic_df, companies)
        section_8g_html = _build_section_8g_sector_correlations(economic_df, df, companies)
        section_8h_html = _build_section_8h_strategic_framework(economic_df, df, companies)
        
        # Combine all subsections
        content = f"""
        <div class="section-content-wrapper">
            <!-- Enhanced header with data scope -->
            <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border);">
                <p style="font-size: 1.1rem; line-height: 1.8; color: var(--text-secondary); margin: 0;">
                    <strong>Comprehensive Macroeconomic Environment Assessment</strong> • {len(companies)} companies • {collector.years} years analysis period<br>
                    Multi-dimensional macro-financial correlation analysis • Federal Reserve Economic Data (FRED) integration<br>
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} • Data Source: FRED + Financial Modeling Prep
                </p>
            </div>
            
            {section_8a_html}
            {build_section_divider() if section_8b_html else ""}
            {section_8b_html}
            {build_section_divider() if section_8c_html else ""}
            {section_8c_html}
            {build_section_divider() if section_8d_html else ""}
            {section_8d_html}
            {build_section_divider() if section_8e_html else ""}
            {section_8e_html}
            {build_section_divider() if section_8f_html else ""}
            {section_8f_html}
            {build_section_divider() if section_8g_html else ""}
            {section_8g_html}
            {build_section_divider() if section_8h_html else ""}
            {section_8h_html}
        </div>
        
        <style>
            .subsection-container {{
                margin: 40px 0;
                background: var(--card-bg);
                border-radius: 16px;
                border: 1px solid var(--card-border);
                box-shadow: var(--shadow-sm);
                overflow: hidden;
            }}
            
            .subsection-header {{
                background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
                padding: 20px 25px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: var(--transition-fast);
            }}
            
            .subsection-header:hover {{
                opacity: 0.95;
                transform: translateX(3px);
            }}
            
            .subsection-title {{
                color: white;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0;
            }}
            
            .subsection-toggle {{
                color: white;
                font-size: 1.5rem;
                font-weight: bold;
                transition: transform 0.3s ease;
            }}
            
            .subsection-toggle.collapsed {{
                transform: rotate(-90deg);
            }}
            
            .subsection-content {{
                padding: 30px;
                display: block;
            }}
            
            .subsection-content.collapsed {{
                display: none;
            }}
            
            .metric-highlight {{
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                padding: 15px 20px;
                border-radius: 12px;
                border-left: 4px solid var(--primary-gradient-start);
                margin: 15px 0;
            }}
            
            .chart-container {{
                margin: 25px 0;
                padding: 20px;
                background: var(--card-bg);
                border-radius: 12px;
                border: 1px solid var(--card-border);
                box-shadow: var(--shadow-sm);
            }}
            
            .chart-title {{
                font-size: 1.2rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid var(--primary-gradient-start);
            }}
        </style>
        
        <script>
            // Collapsible subsection functionality
            document.addEventListener('DOMContentLoaded', function() {{
                const headers = document.querySelectorAll('.subsection-header');
                
                headers.forEach(header => {{
                    header.addEventListener('click', function() {{
                        const content = this.nextElementSibling;
                        const toggle = this.querySelector('.subsection-toggle');
                        
                        content.classList.toggle('collapsed');
                        toggle.classList.toggle('collapsed');
                    }});
                }});
            }});
        </script>
        """
        
        return generate_section_wrapper(8, "Macroeconomic Environment Analysis", content)
        
    except Exception as e:
        error_content = f"""
        <div class="error-container">
            <h3>Error Generating Section 8</h3>
            <p>An error occurred while generating the macroeconomic environment analysis:</p>
            <pre>{str(e)}</pre>
        </div>
        """
        return generate_section_wrapper(8, "Macroeconomic Environment Analysis - Error", error_content)


# =============================================================================
# SUBSECTION 8A: ECONOMIC INDICATORS SNAPSHOT & HISTORICAL TRENDS
# =============================================================================

def _build_section_8a_economic_indicators(economic_df: pd.DataFrame, companies: Dict[str, str], years_coverage: int) -> str:
    """Build subsection 8A: Economic Indicators Snapshot & Historical Trends"""
    
    if economic_df.empty:
        return _build_collapsible_subsection(
            "8A",
            "Economic Indicators Snapshot & Historical Trends",
            "<p>Economic data unavailable for comprehensive analysis.</p>"
        )
    
    # Analyze economic indicators
    analysis = _analyze_economic_indicators(economic_df, years_coverage)
    
    if not analysis:
        return _build_collapsible_subsection(
            "8A",
            "Economic Indicators Snapshot & Historical Trends",
            "<p>Insufficient economic data for analysis.</p>"
        )
    
    # Build content sections
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Comprehensive Economic Indicators Overview</h4>
            <p>Analysis of key macroeconomic indicators including growth metrics, inflation measures, 
            employment trends, and interest rate environment. These indicators provide critical context 
            for portfolio positioning and economic cycle assessment.</p>
        </div>
    """)
    
    # Economic Indicators Snapshot Table
    if 'snapshot' in analysis and analysis['snapshot']:
        snapshot_df = _create_snapshot_dataframe(analysis['snapshot'])
        
        content_parts.append('<div class="metric-highlight">')
        content_parts.append('<h4>Economic Indicators Snapshot</h4>')
        content_parts.append(build_data_table(snapshot_df, table_id="economic-snapshot-table", page_length=15))
        content_parts.append('</div>')
    
    # Economic Regime Assessment
    if 'economic_regime' in analysis:
        regime = analysis['economic_regime']
        regime_badge = _get_regime_badge(regime['regime'])
        
        regime_html = f"""
        <div class="info-box info">
            <h4>Economic Regime Classification</h4>
            <p><strong>Current Regime:</strong> {regime_badge} {regime['regime']}</p>
            <p><strong>Description:</strong> {regime['description']}</p>
            <ul>
                <li><strong>GDP Trend:</strong> {regime['gdp_trend']:.1f}% indicating {'robust' if regime['gdp_trend'] > 2.5 else 'moderate' if regime['gdp_trend'] > 1.5 else 'weak'} economic expansion</li>
                <li><strong>Inflation Trend:</strong> {regime['inflation_trend']:.1f}% {'above' if regime['inflation_trend'] > 2.5 else 'near' if regime['inflation_trend'] > 1.5 else 'below'} Federal Reserve target range</li>
            </ul>
        </div>
        """
        content_parts.append(regime_html)
    
    # Economic Trends Summary
    trends_summary = _generate_economic_trends_summary(analysis, len(companies))
    content_parts.append(f'<div class="info-box default">{trends_summary}</div>')
    
    # Create time series charts
    charts_html = _create_economic_indicators_charts(economic_df, analysis)
    content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8A",
        "Economic Indicators Snapshot & Historical Trends",
        combined_content
    )


def _analyze_economic_indicators(economic_df: pd.DataFrame, years_coverage: int) -> Dict[str, Any]:
    """Analyze comprehensive economic indicators"""
    
    analysis = {}
    
    # Key economic indicators to analyze
    key_indicators = {
        'Real_GDP': 'Real GDP Growth',
        'CPI_All_Items': 'Consumer Price Index',
        'Core_CPI': 'Core CPI',
        'Unemployment_Rate': 'Unemployment Rate',
        'Treasury_10Y': '10-Year Treasury',
        'Treasury_3M': '3-Month Treasury',
        'Industrial_Production': 'Industrial Production',
        'S&P_500_Index': 'S&P 500 Index',
        'VIX_Index': 'VIX Volatility Index'
    }
    
    snapshot = {}
    
    for indicator, label in key_indicators.items():
        if indicator in economic_df.columns:
            series = economic_df[indicator].dropna()
            
            if len(series) >= 2:
                current = series.iloc[-1]
                previous = series.iloc[-2]
                three_year_avg = series.tail(3).mean() if len(series) >= 3 else current
                
                # Calculate trends and changes
                yoy_change = current - previous
                volatility = series.std() if len(series) >= 3 else 0
                
                # Trend classification
                if len(series) >= 3:
                    recent_trend = series.tail(3).values
                    if np.all(np.diff(recent_trend) > 0):
                        trend = 'Rising'
                    elif np.all(np.diff(recent_trend) < 0):
                        trend = 'Falling'
                    else:
                        trend = 'Mixed'
                else:
                    trend = 'Stable'
                
                # Economic significance assessment
                if indicator in ['CPI_All_Items', 'Core_CPI']:
                    significance = 'High' if abs(yoy_change) > 0.5 else 'Moderate' if abs(yoy_change) > 0.2 else 'Low'
                elif indicator in ['Unemployment_Rate']:
                    significance = 'High' if abs(yoy_change) > 1.0 else 'Moderate' if abs(yoy_change) > 0.5 else 'Low'
                elif indicator in ['Treasury_10Y', 'Treasury_3M']:
                    significance = 'High' if abs(yoy_change) > 1.0 else 'Moderate' if abs(yoy_change) > 0.5 else 'Low'
                else:
                    significance = 'Moderate'
                
                snapshot[label] = {
                    'current_value': current,
                    'yoy_change': yoy_change,
                    'three_year_avg': three_year_avg,
                    'volatility': volatility,
                    'trend': trend,
                    'significance': significance
                }
    
    analysis['snapshot'] = snapshot
    
    # Calculate economic regime assessment
    if 'Real_GDP' in economic_df.columns and 'CPI_All_Items' in economic_df.columns:
        gdp_series = economic_df['Real_GDP'].dropna()
        cpi_series = economic_df['CPI_All_Items'].dropna()
        
        if len(gdp_series) >= 3 and len(cpi_series) >= 3:
            recent_gdp = gdp_series.tail(3).mean()
            recent_cpi = cpi_series.tail(3).mean()
            
            # Economic regime classification
            if recent_gdp > 2.5 and recent_cpi < 3.0:
                regime = 'Goldilocks'
                regime_desc = 'Strong growth with controlled inflation'
            elif recent_gdp > 2.5 and recent_cpi >= 3.0:
                regime = 'Overheating'
                regime_desc = 'Strong growth with elevated inflation'
            elif recent_gdp <= 2.5 and recent_cpi < 3.0:
                regime = 'Slow Growth'
                regime_desc = 'Moderate growth with low inflation'
            else:
                regime = 'Stagflation Risk'
                regime_desc = 'Slow growth with elevated inflation'
            
            analysis['economic_regime'] = {
                'regime': regime,
                'description': regime_desc,
                'gdp_trend': recent_gdp,
                'inflation_trend': recent_cpi
            }
    
    return analysis


def _create_snapshot_dataframe(snapshot: Dict) -> pd.DataFrame:
    """Create DataFrame from snapshot data for table display"""
    
    rows = []
    for indicator, data in snapshot.items():
        # Format values based on indicator type
        if 'Rate' in indicator or 'Treasury' in indicator or 'CPI' in indicator:
            current_val = f"{data['current_value']:.2f}%"
            yoy_val = f"{data['yoy_change']:+.2f}pp"
            avg_val = f"{data['three_year_avg']:.2f}%"
        elif 'Index' in indicator:
            current_val = f"{data['current_value']:,.0f}"
            yoy_val = f"{data['yoy_change']:+,.0f}"
            avg_val = f"{data['three_year_avg']:,.0f}"
        else:
            current_val = f"{data['current_value']:.1f}"
            yoy_val = f"{data['yoy_change']:+.1f}"
            avg_val = f"{data['three_year_avg']:.1f}"
        
        rows.append({
            'Economic Indicator': indicator,
            'Current Value': current_val,
            'YoY Change': yoy_val,
            '3Y Average': avg_val,
            'Trend': data['trend'],
            'Significance': data['significance']
        })
    
    return pd.DataFrame(rows)


def _generate_economic_trends_summary(analysis: Dict, num_companies: int) -> str:
    """Generate economic trends analysis summary"""
    
    snapshot = analysis.get('snapshot', {})
    regime = analysis.get('economic_regime', {})
    
    if not snapshot:
        return "<p>Economic data insufficient for trend analysis.</p>"
    
    # Count indicators by trend and significance
    rising_indicators = sum(1 for data in snapshot.values() if data['trend'] == 'Rising')
    falling_indicators = sum(1 for data in snapshot.values() if data['trend'] == 'Falling')
    high_significance = sum(1 for data in snapshot.values() if data['significance'] == 'High')
    total_indicators = len(snapshot)
    
    # Economic momentum assessment
    if rising_indicators > falling_indicators:
        momentum = 'Positive'
    elif falling_indicators > rising_indicators:
        momentum = 'Negative'
    else:
        momentum = 'Mixed'
    
    return f"""
        <h4>Economic Environment & Trend Analysis</h4>
        <ul>
            <li><strong>Macroeconomic Momentum:</strong> {momentum} directional bias with {rising_indicators}/{total_indicators} indicators rising and {falling_indicators}/{total_indicators} indicators declining</li>
            <li><strong>Indicator Significance:</strong> {high_significance}/{total_indicators} indicators showing high significance changes requiring strategic attention</li>
            <li><strong>Portfolio Companies:</strong> Analysis based on {num_companies} companies with varying macroeconomic sensitivities</li>
            <li><strong>Investment Environment:</strong> {'Favorable' if momentum == 'Positive' and regime.get('regime') == 'Goldilocks' else 'Cautious' if momentum == 'Negative' or regime.get('regime') == 'Stagflation Risk' else 'Selective'} conditions for portfolio positioning</li>
        </ul>
    """


def _create_economic_indicators_charts(economic_df: pd.DataFrame, analysis: Dict) -> str:
    """Create economic indicators time series charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Economic Indicators Historical Trends</h4>'
    
    if 'Year' not in economic_df.columns:
        return charts_html + "<p>Year data not available for time series charts.</p>"
    
    years = economic_df['Year'].tolist()
    
    # Chart 1: GDP and Industrial Production
    if 'Real_GDP' in economic_df.columns:
        gdp_data = economic_df['Real_GDP'].tolist()
        
        traces = [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': years[:len(gdp_data)],
            'y': gdp_data,
            'name': 'Real GDP Growth',
            'line': {'color': '#1f77b4', 'width': 3},
            'marker': {'size': 8}
        }]
        
        if 'Industrial_Production' in economic_df.columns:
            indpro_data = economic_df['Industrial_Production'].tolist()
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(indpro_data)],
                'y': indpro_data,
                'name': 'Industrial Production',
                'line': {'color': '#ff7f0e', 'width': 3},
                'marker': {'size': 8}
            })
        
        fig_data = {
            'data': traces,
            'layout': {
                'title': 'Economic Growth Indicators',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Growth Rate (%)'},
                'hovermode': 'x unified',
                'shapes': [{
                    'type': 'line',
                    'x0': years[0],
                    'x1': years[-1],
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'black', 'dash': 'dash', 'width': 1}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-gdp-indpro", height=400)
    
    # Chart 2: Inflation Indicators
    if 'CPI_All_Items' in economic_df.columns:
        cpi_data = economic_df['CPI_All_Items'].tolist()
        
        traces = [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': years[:len(cpi_data)],
            'y': cpi_data,
            'name': 'CPI (Headline)',
            'line': {'color': '#2ca02c', 'width': 3},
            'marker': {'size': 8}
        }]
        
        if 'Core_CPI' in economic_df.columns:
            core_cpi_data = economic_df['Core_CPI'].tolist()
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(core_cpi_data)],
                'y': core_cpi_data,
                'name': 'Core CPI',
                'line': {'color': '#d62728', 'width': 3},
                'marker': {'size': 8}
            })
        
        fig_data = {
            'data': traces,
            'layout': {
                'title': 'Inflation Dynamics',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Inflation Rate (%)'},
                'hovermode': 'x unified',
                'shapes': [{
                    'type': 'line',
                    'x0': years[0],
                    'x1': years[-1],
                    'y0': 2.0,
                    'y1': 2.0,
                    'line': {'color': 'red', 'dash': 'dash', 'width': 2}
                }],
                'annotations': [{
                    'x': years[-1],
                    'y': 2.0,
                    'text': 'Fed Target',
                    'showarrow': False,
                    'xanchor': 'left',
                    'font': {'color': 'red'}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-inflation", height=400)
    
    # Chart 3: Labor Market
    if 'Unemployment_Rate' in economic_df.columns:
        unemployment_data = economic_df['Unemployment_Rate'].tolist()
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(unemployment_data)],
                'y': unemployment_data,
                'name': 'Unemployment Rate',
                'line': {'color': '#9467bd', 'width': 3},
                'marker': {'size': 8},
                'fill': 'tozeroy',
                'fillcolor': 'rgba(148, 103, 189, 0.2)'
            }],
            'layout': {
                'title': 'Labor Market Conditions',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Unemployment Rate (%)'},
                'hovermode': 'x unified'
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-unemployment", height=400)
    
    # Chart 4: Interest Rates
    if 'Treasury_10Y' in economic_df.columns:
        ten_year_data = economic_df['Treasury_10Y'].tolist()
        
        traces = [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': years[:len(ten_year_data)],
            'y': ten_year_data,
            'name': '10-Year Treasury',
            'line': {'color': '#8c564b', 'width': 3},
            'marker': {'size': 8}
        }]
        
        if 'Treasury_3M' in economic_df.columns:
            three_month_data = economic_df['Treasury_3M'].tolist()
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(three_month_data)],
                'y': three_month_data,
                'name': '3-Month Treasury',
                'line': {'color': '#e377c2', 'width': 3},
                'marker': {'size': 8}
            })
        
        fig_data = {
            'data': traces,
            'layout': {
                'title': 'Interest Rate Environment',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Interest Rate (%)'},
                'hovermode': 'x unified'
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-interest-rates", height=400)
    
    return charts_html


# =============================================================================
# SUBSECTION 8B: INTEREST RATE ENVIRONMENT & YIELD CURVE DYNAMICS
# =============================================================================

def _build_section_8b_interest_rates(economic_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8B: Interest Rate Environment & Yield Curve Dynamics"""
    
    if economic_df.empty:
        return _build_collapsible_subsection(
            "8B",
            "Interest Rate Environment & Yield Curve Dynamics",
            "<p>Economic data unavailable for interest rate analysis.</p>"
        )
    
    # Analyze interest rate environment
    analysis = _analyze_interest_rate_environment(economic_df)
    
    if not analysis:
        return _build_collapsible_subsection(
            "8B",
            "Interest Rate Environment & Yield Curve Dynamics",
            "<p>Interest rate data unavailable for yield curve analysis.</p>"
        )
    
    # Build content sections
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Treasury Yield Curve & Monetary Policy Assessment</h4>
            <p>Analysis of the interest rate environment including yield curve shape, monetary policy stance, 
            and implications for portfolio companies. The yield curve provides critical signals about 
            economic expectations and credit conditions.</p>
        </div>
    """)
    
    # Current Yield Curve Table
    if 'current_curve' in analysis and analysis['current_curve']:
        curve_df = _create_yield_curve_dataframe(analysis['current_curve'])
        
        content_parts.append('<div class="metric-highlight">')
        content_parts.append('<h4>Current Treasury Yield Curve</h4>')
        content_parts.append(build_data_table(curve_df, table_id="yield-curve-table", page_length=-1))
        content_parts.append('</div>')
    
    # Yield Curve Analysis Table
    if any(key in analysis for key in ['yield_curve', 'monetary_policy', 'rate_trends']):
        analysis_df = _create_yield_curve_analysis_dataframe(analysis)
        
        content_parts.append('<div class="metric-highlight">')
        content_parts.append('<h4>Yield Curve & Monetary Policy Analysis</h4>')
        content_parts.append(build_data_table(analysis_df, table_id="yield-analysis-table", page_length=-1))
        content_parts.append('</div>')
    
    # Yield Curve Assessment
    if 'yield_curve' in analysis:
        yc = analysis['yield_curve']
        shape_badge = _get_yield_curve_badge(yc['shape'])
        
        yc_html = f"""
        <div class="info-box {'success' if yc['shape'] in ['Steep', 'Normal'] else 'warning' if yc['shape'] == 'Flat' else 'danger'}">
            <h4>Yield Curve Configuration</h4>
            <p><strong>Curve Shape:</strong> {shape_badge} {yc['shape']}</p>
            <p><strong>10Y-3M Spread:</strong> {yc['spread_10y_3m']:+.2f} percentage points</p>
            <p><strong>Interpretation:</strong> {yc['interpretation']}</p>
        </div>
        """
        content_parts.append(yc_html)
    
    # Monetary Policy Assessment
    if 'monetary_policy' in analysis:
        mp = analysis['monetary_policy']
        policy_badge = _get_policy_stance_badge(mp['stance'])
        
        mp_html = f"""
        <div class="info-box info">
            <h4>Monetary Policy Stance</h4>
            <p><strong>Policy Stance:</strong> {policy_badge} {mp['stance']}</p>
            <p><strong>Short-term Rate:</strong> {mp['current_rate']:.2f}%</p>
            <p><strong>Recent Change:</strong> {mp['rate_change']:+.2f} percentage points</p>
            <p><strong>Description:</strong> {mp['description']}</p>
        </div>
        """
        content_parts.append(mp_html)
    
    # Interest Rate Summary
    summary = _generate_yield_curve_summary(analysis, len(companies))
    content_parts.append(f'<div class="info-box default">{summary}</div>')
    
    # Create yield curve charts
    charts_html = _create_interest_rate_charts(economic_df, analysis)
    content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8B",
        "Interest Rate Environment & Yield Curve Dynamics",
        combined_content
    )


def _analyze_interest_rate_environment(economic_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze interest rate environment and yield curve dynamics"""
    
    analysis = {}
    
    # Treasury rates across the curve
    treasury_rates = {
        'Treasury_3M': '3-Month',
        'Treasury_6M': '6-Month',
        'Treasury_1Y': '1-Year',
        'Treasury_2Y': '2-Year',
        'Treasury_5Y': '5-Year',
        'Treasury_10Y': '10-Year',
        'Treasury_30Y': '30-Year'
    }
    
    # Current yield curve
    current_curve = {}
    for rate_col, label in treasury_rates.items():
        if rate_col in economic_df.columns:
            series = economic_df[rate_col].dropna()
            if len(series) > 0:
                current_curve[label] = series.iloc[-1]
    
    analysis['current_curve'] = current_curve
    
    # Yield curve analysis
    if 'Treasury_10Y' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        ten_year = economic_df['Treasury_10Y'].dropna()
        three_month = economic_df['Treasury_3M'].dropna()
        
        if len(ten_year) > 0 and len(three_month) > 0:
            # Calculate spreads
            current_spread = ten_year.iloc[-1] - three_month.iloc[-1]
            
            # Yield curve shape assessment
            if current_spread > 1.5:
                curve_shape = 'Steep'
                curve_interpretation = 'Normal yield curve suggesting growth expectations'
            elif current_spread > 0.5:
                curve_shape = 'Normal'
                curve_interpretation = 'Moderately upward sloping yield curve'
            elif current_spread > -0.5:
                curve_shape = 'Flat'
                curve_interpretation = 'Flat yield curve indicating uncertainty'
            else:
                curve_shape = 'Inverted'
                curve_interpretation = 'Inverted yield curve signaling recession risk'
            
            analysis['yield_curve'] = {
                'spread_10y_3m': current_spread,
                'shape': curve_shape,
                'interpretation': curve_interpretation
            }
            
            # Interest rate trend analysis
            if len(ten_year) >= 4:
                recent_10y_trend = ten_year.tail(4).values
                trend_direction = 'Rising' if recent_10y_trend[-1] > recent_10y_trend[0] else 'Falling'
                trend_magnitude = abs(recent_10y_trend[-1] - recent_10y_trend[0])
                
                analysis['rate_trends'] = {
                    'direction': trend_direction,
                    'magnitude': trend_magnitude,
                    'assessment': 'Significant' if trend_magnitude > 0.5 else 'Moderate' if trend_magnitude > 0.25 else 'Minimal'
                }
    
    # Federal funds rate analysis (using 3M Treasury as proxy)
    if 'Treasury_3M' in economic_df.columns:
        fed_proxy = economic_df['Treasury_3M'].dropna()
        if len(fed_proxy) >= 2:
            current_rate = fed_proxy.iloc[-1]
            previous_rate = fed_proxy.iloc[-2]
            
            # Monetary policy stance assessment
            if current_rate > 4.0:
                policy_stance = 'Restrictive'
                policy_desc = 'Tight monetary policy constraining economic activity'
            elif current_rate > 2.0:
                policy_stance = 'Neutral'
                policy_desc = 'Balanced monetary policy stance'
            else:
                policy_stance = 'Accommodative'
                policy_desc = 'Supportive monetary policy stimulating growth'
            
            analysis['monetary_policy'] = {
                'current_rate': current_rate,
                'rate_change': current_rate - previous_rate,
                'stance': policy_stance,
                'description': policy_desc
            }
    
    return analysis


def _create_yield_curve_dataframe(current_curve: Dict) -> pd.DataFrame:
    """Create DataFrame for current yield curve display"""
    
    maturities = list(current_curve.keys())
    rates = [f"{rate:.2f}%" for rate in current_curve.values()]
    
    return pd.DataFrame({
        'Maturity': maturities,
        'Yield': rates
    })


def _create_yield_curve_analysis_dataframe(analysis: Dict) -> pd.DataFrame:
    """Create DataFrame for yield curve analysis"""
    
    rows = []
    
    if 'yield_curve' in analysis:
        yc = analysis['yield_curve']
        rows.append({
            'Component': 'Yield Curve Shape',
            'Current Assessment': f"{yc['shape']} ({yc['spread_10y_3m']:+.2f}pp spread)",
            'Investment Implication': yc['interpretation']
        })
    
    if 'monetary_policy' in analysis:
        mp = analysis['monetary_policy']
        rows.append({
            'Component': 'Monetary Policy Stance',
            'Current Assessment': f"{mp['stance']} ({mp['current_rate']:.2f}%)",
            'Investment Implication': mp['description']
        })
    
    if 'rate_trends' in analysis:
        rt = analysis['rate_trends']
        rows.append({
            'Component': 'Interest Rate Trend',
            'Current Assessment': f"{rt['direction']} ({rt['assessment']} magnitude)",
            'Investment Implication': f"{'Rising rate pressure' if rt['direction'] == 'Rising' else 'Declining rate support'} for portfolio valuations"
        })
    
    return pd.DataFrame(rows)


def _generate_yield_curve_summary(analysis: Dict, num_companies: int) -> str:
    """Generate yield curve and interest rate environment summary"""
    
    curve = analysis.get('yield_curve', {})
    monetary = analysis.get('monetary_policy', {})
    trends = analysis.get('rate_trends', {})
    
    rate_environment = "Standard"
    if monetary.get('current_rate', 0) > 4.5:
        rate_environment = "Highly Restrictive"
    elif monetary.get('current_rate', 0) > 3.0:
        rate_environment = "Restrictive"
    elif monetary.get('current_rate', 0) < 1.0:
        rate_environment = "Highly Accommodative"
    elif monetary.get('current_rate', 0) < 2.0:
        rate_environment = "Accommodative"
    
    return f"""
        <h4>Interest Rate Environment & Yield Curve Assessment</h4>
        <ul>
            <li><strong>Overall Rate Environment:</strong> {rate_environment} monetary policy stance with {monetary.get('current_rate', 0):.2f}% short-term rates</li>
            <li><strong>Yield Curve Configuration:</strong> {curve.get('shape', 'Unknown')} yield curve with {curve.get('spread_10y_3m', 0):+.2f} percentage point 10Y-3M spread</li>
            <li><strong>Rate Trend Dynamics:</strong> {trends.get('direction', 'Stable')} interest rate trajectory with {trends.get('assessment', 'minimal')} magnitude changes</li>
            <li><strong>Portfolio Implications:</strong> {'Defensive positioning recommended' if rate_environment in ['Highly Restrictive', 'Restrictive'] and trends.get('direction') == 'Rising' else 'Opportunistic growth positioning' if rate_environment in ['Accommodative', 'Highly Accommodative'] else 'Balanced approach'} for {num_companies} portfolio companies</li>
            <li><strong>Duration Risk:</strong> {'High' if trends.get('direction') == 'Rising' and trends.get('magnitude', 0) > 0.5 else 'Moderate' if trends.get('direction') == 'Rising' else 'Low'} sensitivity to interest rate changes</li>
        </ul>
    """


def _create_interest_rate_charts(economic_df: pd.DataFrame, analysis: Dict) -> str:
    """Create interest rate and yield curve charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Interest Rate Environment Visualization</h4>'
    
    if 'Year' not in economic_df.columns:
        return charts_html + "<p>Year data not available for time series charts.</p>"
    
    years = economic_df['Year'].tolist()
    
    # Chart 1: Current Yield Curve
    if 'current_curve' in analysis and analysis['current_curve']:
        maturities = list(analysis['current_curve'].keys())
        rates = list(analysis['current_curve'].values())
        
        # Convert maturities to numeric for proper ordering
        maturity_map = {'3-Month': 0.25, '6-Month': 0.5, '1-Year': 1, '2-Year': 2,
                       '5-Year': 5, '10-Year': 10, '30-Year': 30}
        numeric_maturities = [maturity_map.get(m, 0) for m in maturities]
        
        # Sort by maturity
        sorted_data = sorted(zip(numeric_maturities, maturities, rates))
        sorted_numeric, sorted_labels, sorted_rates = zip(*sorted_data)
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': list(sorted_labels),
                'y': list(sorted_rates),
                'name': 'Current Yield Curve',
                'line': {'color': '#1f77b4', 'width': 4},
                'marker': {'size': 10, 'color': '#1f77b4'}
            }],
            'layout': {
                'title': 'Current Treasury Yield Curve',
                'xaxis': {'title': 'Maturity'},
                'yaxis': {'title': 'Yield (%)'},
                'hovermode': 'closest'
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-current-yield-curve", height=400)
    
    # Chart 2: Yield Spread Evolution (10Y-3M)
    if 'Treasury_10Y' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        ten_year = economic_df['Treasury_10Y'].tolist()
        three_month = economic_df['Treasury_3M'].tolist()
        
        min_len = min(len(ten_year), len(three_month), len(years))
        spread = [ten_year[i] - three_month[i] for i in range(min_len)]
        years_spread = years[:min_len]
        
        # Create areas for positive and negative spreads
        positive_spread = [s if s >= 0 else 0 for s in spread]
        negative_spread = [s if s < 0 else 0 for s in spread]
        
        fig_data = {
            'data': [
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_spread,
                    'y': positive_spread,
                    'name': 'Normal Curve',
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(46, 160, 44, 0.3)',
                    'line': {'color': 'rgba(46, 160, 44, 0)', 'width': 0},
                    'showlegend': True
                },
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_spread,
                    'y': negative_spread,
                    'name': 'Inverted Curve',
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(214, 39, 40, 0.3)',
                    'line': {'color': 'rgba(214, 39, 40, 0)', 'width': 0},
                    'showlegend': True
                },
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_spread,
                    'y': spread,
                    'name': '10Y-3M Spread',
                    'line': {'color': '#1f77b4', 'width': 3},
                    'showlegend': True
                }
            ],
            'layout': {
                'title': 'Yield Curve Spread Evolution (10Y-3M)',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Spread (percentage points)'},
                'hovermode': 'x unified',
                'shapes': [{
                    'type': 'line',
                    'x0': years_spread[0],
                    'x1': years_spread[-1],
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'black', 'width': 2}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-yield-spread", height=400)
    
    # Chart 3: Interest Rate Levels Over Time
    if 'Treasury_10Y' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        ten_year_data = economic_df['Treasury_10Y'].tolist()
        three_month_data = economic_df['Treasury_3M'].tolist()
        
        fig_data = {
            'data': [
                {
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'x': years[:len(ten_year_data)],
                    'y': ten_year_data,
                    'name': '10-Year Treasury',
                    'line': {'color': '#ff7f0e', 'width': 3},
                    'marker': {'size': 6}
                },
                {
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'x': years[:len(three_month_data)],
                    'y': three_month_data,
                    'name': '3-Month Treasury',
                    'line': {'color': '#2ca02c', 'width': 3},
                    'marker': {'size': 6}
                }
            ],
            'layout': {
                'title': 'Interest Rate Level Trends',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Interest Rate (%)'},
                'hovermode': 'x unified'
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-rate-levels", height=400)
    
    # Chart 4: Rate Volatility
    if 'Treasury_10Y' in economic_df.columns:
        rate_series = pd.Series(economic_df['Treasury_10Y'].tolist())
        if len(rate_series) >= 3:
            rolling_vol = rate_series.rolling(window=3).std().tolist()
            years_vol = years[:len(rolling_vol)]
            
            fig_data = {
                'data': [{
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_vol,
                    'y': rolling_vol,
                    'name': '10Y Rate Volatility',
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(148, 103, 189, 0.3)',
                    'line': {'color': '#9467bd', 'width': 3}
                }],
                'layout': {
                    'title': 'Interest Rate Volatility (3-Year Rolling)',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Rate Volatility'},
                    'hovermode': 'x unified'
                }
            }
            
            charts_html += build_plotly_chart(fig_data, div_id="chart-rate-volatility", height=400)
    
    return charts_html



# =============================================================================
# SUBSECTION 8C: INFLATION DYNAMICS & MONETARY POLICY IMPACT
# =============================================================================

def _build_section_8c_inflation_dynamics(economic_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8C: Inflation Dynamics & Monetary Policy Impact"""
    
    if economic_df.empty:
        return _build_collapsible_subsection(
            "8C",
            "Inflation Dynamics & Monetary Policy Impact",
            "<p>Economic data unavailable for inflation analysis.</p>"
        )
    
    # Analyze inflation dynamics
    analysis = _analyze_inflation_dynamics(economic_df)
    
    if not analysis or not analysis.get('metrics'):
        return _build_collapsible_subsection(
            "8C",
            "Inflation Dynamics & Monetary Policy Impact",
            "<p>Inflation data unavailable for comprehensive analysis.</p>"
        )
    
    # Build content sections
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Price Stability & Inflationary Environment Analysis</h4>
            <p>Comprehensive analysis of inflation measures including consumer prices, core inflation, 
            producer prices, and PCE index. Assessment of price pressures, monetary policy implications, 
            and inflation regime classification for portfolio positioning.</p>
        </div>
    """)
    
    # Inflation Metrics Table
    if 'metrics' in analysis:
        metrics_df = _create_inflation_metrics_dataframe(analysis['metrics'])
        
        content_parts.append('<div class="metric-highlight">')
        content_parts.append('<h4>Inflation Indicators Analysis</h4>')
        content_parts.append(build_data_table(metrics_df, table_id="inflation-metrics-table", page_length=10))
        content_parts.append('</div>')
    
    # Inflation Regime Assessment
    if 'inflation_regime' in analysis:
        regime = analysis['inflation_regime']
        regime_badge = _get_inflation_regime_badge(regime['regime'])
        
        regime_html = f"""
        <div class="info-box {'danger' if regime['regime'] == 'High Inflation' else 'warning' if regime['regime'] == 'Elevated Inflation' else 'success' if regime['regime'] == 'Target Range' else 'info'}">
            <h4>Inflation Regime Classification</h4>
            <p><strong>Current Regime:</strong> {regime_badge} {regime['regime']}</p>
            <p><strong>Description:</strong> {regime['description']}</p>
            <ul>
                <li><strong>Headline CPI:</strong> {regime['headline_cpi']:.2f}% {'above' if regime['headline_cpi'] > 3.0 else 'near' if regime['headline_cpi'] > 2.0 else 'below'} Federal Reserve tolerance range</li>
                <li><strong>Core CPI:</strong> {regime['core_cpi']:.2f}% showing {'persistent' if regime['core_cpi'] > 2.5 else 'moderate' if regime['core_cpi'] > 2.0 else 'subdued'} underlying price pressures</li>
                <li><strong>Inflation Breadth:</strong> {regime['breadth']} - {regime['breadth_description']}</li>
            </ul>
        </div>
        """
        content_parts.append(regime_html)
    
    # Inflation Summary
    inflation_summary = _generate_inflation_summary(analysis, len(companies))
    content_parts.append(f'<div class="info-box default">{inflation_summary}</div>')
    
    # Create inflation charts
    charts_html = _create_inflation_dynamics_charts(economic_df, analysis)
    content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8C",
        "Inflation Dynamics & Monetary Policy Impact",
        combined_content
    )


def _analyze_inflation_dynamics(economic_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze inflation dynamics and price pressures"""
    
    analysis = {}
    
    # Inflation indicators
    inflation_indicators = {
        'CPI_All_Items': 'Consumer Price Index (Headline)',
        'Core_CPI': 'Core CPI (Ex Food & Energy)',
        'PCE_Price_Index': 'PCE Price Index',
        'Producer_Price_Index': 'Producer Price Index'
    }
    
    metrics = {}
    
    for indicator, label in inflation_indicators.items():
        if indicator in economic_df.columns:
            series = economic_df[indicator].dropna()
            
            if len(series) >= 3:
                current_level = series.iloc[-1]
                previous_level = series.iloc[-2]
                three_year_avg = series.tail(3).mean()
                volatility = series.std()
                
                yoy_change = current_level - previous_level
                
                # Policy implication assessment
                if 'CPI' in indicator or 'PCE' in indicator:
                    if current_level > 3.0:
                        policy_implication = 'Above Target - Restrictive Policy'
                    elif current_level > 2.0:
                        policy_implication = 'Near Target - Neutral Policy'
                    else:
                        policy_implication = 'Below Target - Accommodative Policy'
                else:  # Producer prices
                    if current_level > 4.0:
                        policy_implication = 'High Input Cost Pressure'
                    elif current_level > 2.0:
                        policy_implication = 'Moderate Input Costs'
                    else:
                        policy_implication = 'Low Input Cost Pressure'
                
                metrics[label] = {
                    'current_level': current_level,
                    'yoy_change': yoy_change,
                    'three_year_avg': three_year_avg,
                    'volatility': volatility,
                    'policy_implication': policy_implication
                }
    
    analysis['metrics'] = metrics
    
    # Inflation regime assessment
    if 'CPI_All_Items' in economic_df.columns and 'Core_CPI' in economic_df.columns:
        headline_cpi = economic_df['CPI_All_Items'].dropna()
        core_cpi = economic_df['Core_CPI'].dropna()
        
        if len(headline_cpi) >= 3 and len(core_cpi) >= 3:
            current_headline = headline_cpi.iloc[-1]
            current_core = core_cpi.iloc[-1]
            
            # Inflation regime classification
            if current_headline > 4.0 and current_core > 3.0:
                regime = 'High Inflation'
                regime_desc = 'Broad-based price pressures requiring aggressive policy response'
            elif current_headline > 3.0 or current_core > 2.5:
                regime = 'Elevated Inflation'
                regime_desc = 'Above-target inflation with policy tightening implications'
            elif current_headline > 2.0 and current_core > 1.5:
                regime = 'Target Range'
                regime_desc = 'Inflation near Federal Reserve target range'
            else:
                regime = 'Low Inflation'
                regime_desc = 'Below-target inflation with policy accommodation potential'
            
            # Calculate inflation breadth
            breadth_measure = abs(current_headline - current_core)
            if breadth_measure > 1.0:
                breadth = 'Volatile'
                breadth_desc = 'Significant divergence between headline and core inflation'
            elif breadth_measure > 0.5:
                breadth = 'Moderate'
                breadth_desc = 'Some divergence between headline and core measures'
            else:
                breadth = 'Aligned'
                breadth_desc = 'Headline and core inflation moving in tandem'
            
            analysis['inflation_regime'] = {
                'regime': regime,
                'description': regime_desc,
                'headline_cpi': current_headline,
                'core_cpi': current_core,
                'breadth': breadth,
                'breadth_description': breadth_desc
            }
    
    return analysis


def _create_inflation_metrics_dataframe(metrics: Dict) -> pd.DataFrame:
    """Create DataFrame from inflation metrics for table display"""
    
    rows = []
    for indicator, data in metrics.items():
        rows.append({
            'Indicator': indicator,
            'Current Level': f"{data['current_level']:.2f}%",
            '1Y Change': f"{data['yoy_change']:+.2f}pp",
            '3Y Average': f"{data['three_year_avg']:.2f}%",
            'Volatility': f"{data['volatility']:.2f}",
            'Policy Implication': data['policy_implication']
        })
    
    return pd.DataFrame(rows)


def _generate_inflation_summary(analysis: Dict, num_companies: int) -> str:
    """Generate inflation dynamics summary"""
    
    metrics = analysis.get('metrics', {})
    regime = analysis.get('inflation_regime', {})
    
    if not metrics:
        return "<p>Inflation data insufficient for comprehensive analysis.</p>"
    
    # Calculate average inflation level - only consumer price measures
    inflation_levels = []
    for indicator_name, data in metrics.items():
        if 'CPI' in indicator_name or 'PCE' in indicator_name:
            inflation_levels.append(data['current_level'])
    
    avg_inflation = np.mean(inflation_levels) if inflation_levels else 0
    
    above_target = sum(1 for m in metrics.values() if m['current_level'] > 2.5)
    total_indicators = len(metrics)
    
    return f"""
        <h4>Inflation Dynamics & Price Pressure Assessment</h4>
        <ul>
            <li><strong>Overall Inflation Level:</strong> {avg_inflation:.2f}% average across key indicators with {above_target}/{total_indicators} measures above target range</li>
            <li><strong>Price Pressure Intensity:</strong> {'High' if avg_inflation > 3.5 else 'Moderate' if avg_inflation > 2.5 else 'Low'} inflation environment affecting operating cost structures</li>
            <li><strong>Policy Response Implications:</strong> {'Restrictive monetary policy likely' if avg_inflation > 3.0 else 'Neutral policy stance expected' if avg_inflation > 2.0 else 'Accommodative policy potential'} based on current inflation trajectory</li>
            <li><strong>Portfolio Companies:</strong> {num_companies} companies face {'elevated' if avg_inflation > 3.0 else 'moderate' if avg_inflation > 2.0 else 'contained'} input cost pressures</li>
            <li><strong>Pricing Power Assessment:</strong> {'Strong' if avg_inflation > 3.0 else 'Moderate' if avg_inflation > 2.0 else 'Limited'} pricing power environment for portfolio companies</li>
        </ul>
    """


def _create_inflation_dynamics_charts(economic_df: pd.DataFrame, analysis: Dict) -> str:
    """Create inflation dynamics visualization charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Inflation Dynamics Visualization</h4>'
    
    if 'Year' not in economic_df.columns:
        return charts_html + "<p>Year data not available for time series charts.</p>"
    
    years = economic_df['Year'].tolist()
    
    # Chart 1: Inflation Time Series
    if 'CPI_All_Items' in economic_df.columns:
        cpi_data = economic_df['CPI_All_Items'].tolist()
        
        traces = [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': years[:len(cpi_data)],
            'y': cpi_data,
            'name': 'CPI (Headline)',
            'line': {'color': '#2ca02c', 'width': 3},
            'marker': {'size': 8}
        }]
        
        if 'Core_CPI' in economic_df.columns:
            core_cpi_data = economic_df['Core_CPI'].tolist()
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(core_cpi_data)],
                'y': core_cpi_data,
                'name': 'Core CPI',
                'line': {'color': '#d62728', 'width': 3},
                'marker': {'size': 8}
            })
        
        if 'PCE_Price_Index' in economic_df.columns:
            pce_data = economic_df['PCE_Price_Index'].tolist()
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(pce_data)],
                'y': pce_data,
                'name': 'PCE Price Index',
                'line': {'color': '#1f77b4', 'width': 2},
                'marker': {'size': 6}
            })
        
        # Add Fed target line
        fig_data = {
            'data': traces,
            'layout': {
                'title': 'Inflation Measures Evolution',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Inflation Rate (%)'},
                'hovermode': 'x unified',
                'shapes': [
                    {
                        'type': 'line',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 2.0,
                        'y1': 2.0,
                        'line': {'color': 'red', 'dash': 'dash', 'width': 2}
                    },
                    {
                        'type': 'rect',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 1.5,
                        'y1': 2.5,
                        'fillcolor': 'rgba(46, 160, 44, 0.1)',
                        'line': {'width': 0},
                        'layer': 'below'
                    }
                ],
                'annotations': [{
                    'x': years[-1],
                    'y': 2.0,
                    'text': 'Fed Target (2%)',
                    'showarrow': False,
                    'xanchor': 'left',
                    'font': {'color': 'red', 'size': 10}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-inflation-evolution", height=400)
    
    # Chart 2: Inflation vs Producer Prices Scatter
    if 'CPI_All_Items' in economic_df.columns and 'Producer_Price_Index' in economic_df.columns:
        cpi = economic_df['CPI_All_Items'].dropna()
        ppi = economic_df['Producer_Price_Index'].dropna()
        
        min_len = min(len(cpi), len(ppi))
        cpi_aligned = cpi.iloc[:min_len].tolist()
        ppi_aligned = ppi.iloc[:min_len].tolist()
        years_aligned = years[:min_len]
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'mode': 'markers',
                'x': ppi_aligned,
                'y': cpi_aligned,
                'text': [f'Year: {y}' for y in years_aligned],
                'marker': {
                    'size': 10,
                    'color': list(range(len(years_aligned))),
                    'colorscale': 'Viridis',
                    'showscale': True,
                    'colorbar': {'title': 'Time Progression'}
                },
                'hovertemplate': '<b>%{text}</b><br>PPI: %{x:.2f}%<br>CPI: %{y:.2f}%<extra></extra>'
            }],
            'layout': {
                'title': 'Producer vs Consumer Price Relationship',
                'xaxis': {'title': 'Producer Price Index (%)'},
                'yaxis': {'title': 'Consumer Price Index (%)'},
                'hovermode': 'closest'
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-inflation-scatter", height=400)
    
    # Chart 3: Inflation Volatility
    if 'CPI_All_Items' in economic_df.columns:
        cpi_series = pd.Series(economic_df['CPI_All_Items'].tolist())
        if len(cpi_series) >= 3:
            rolling_vol = cpi_series.rolling(window=3).std().tolist()
            years_vol = years[:len(rolling_vol)]
            
            vol_data = [v for v in rolling_vol if not pd.isna(v)]
            high_vol_threshold = np.quantile(vol_data, 0.75) if vol_data else 1
            
            fig_data = {
                'data': [{
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_vol,
                    'y': rolling_vol,
                    'name': 'CPI Volatility',
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(148, 103, 189, 0.3)',
                    'line': {'color': '#9467bd', 'width': 3}
                }],
                'layout': {
                    'title': 'Inflation Volatility Analysis (3-Year Rolling)',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Inflation Volatility'},
                    'hovermode': 'x unified',
                    'shapes': [{
                        'type': 'line',
                        'x0': years_vol[0],
                        'x1': years_vol[-1],
                        'y0': high_vol_threshold,
                        'y1': high_vol_threshold,
                        'line': {'color': 'red', 'dash': 'dash', 'width': 1}
                    }],
                    'annotations': [{
                        'x': years_vol[-1],
                        'y': high_vol_threshold,
                        'text': 'High Volatility Threshold',
                        'showarrow': False,
                        'xanchor': 'left',
                        'font': {'color': 'red', 'size': 9}
                    }]
                }
            }
            
            charts_html += build_plotly_chart(fig_data, div_id="chart-inflation-volatility", height=400)
    
    # Chart 4: Current Inflation Indicators Bar Chart
    if 'metrics' in analysis and analysis['metrics']:
        indicators = list(analysis['metrics'].keys())
        values = [analysis['metrics'][ind]['current_level'] for ind in indicators]
        
        colors = []
        for value in values:
            if value > 3.0:
                colors.append('#d62728')
            elif value > 2.0:
                colors.append('#ff7f0e')
            else:
                colors.append('#2ca02c')
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': values,
                'y': indicators,
                'orientation': 'h',
                'marker': {'color': colors},
                'text': [f'{v:.1f}%' for v in values],
                'textposition': 'auto',
                'hovertemplate': '<b>%{y}</b><br>%{x:.2f}%<extra></extra>'
            }],
            'layout': {
                'title': 'Current Inflation Indicators',
                'xaxis': {'title': 'Inflation Rate (%)'},
                'yaxis': {'title': ''},
                'hovermode': 'closest',
                'shapes': [{
                    'type': 'line',
                    'x0': 2.0,
                    'x1': 2.0,
                    'y0': -0.5,
                    'y1': len(indicators) - 0.5,
                    'line': {'color': 'blue', 'dash': 'dash', 'width': 2}
                }],
                'annotations': [{
                    'x': 2.0,
                    'y': len(indicators) - 0.5,
                    'text': 'Fed Target',
                    'showarrow': False,
                    'yanchor': 'bottom',
                    'font': {'color': 'blue'}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-current-inflation", height=400)
    
    return charts_html


# =============================================================================
# SUBSECTION 8D: ECONOMIC GROWTH & LABOR MARKET ASSESSMENT
# =============================================================================

def _build_section_8d_growth_employment(economic_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8D: Economic Growth & Labor Market Assessment"""
    
    if economic_df.empty:
        return _build_collapsible_subsection(
            "8D",
            "Economic Growth & Labor Market Assessment",
            "<p>Economic data unavailable for growth and employment analysis.</p>"
        )
    
    analysis = _analyze_growth_employment(economic_df)
    
    if not analysis or not analysis.get('indicators'):
        return _build_collapsible_subsection(
            "8D",
            "Economic Growth & Labor Market Assessment",
            "<p>Growth and employment data unavailable for analysis.</p>"
        )
    
    content_parts = []
    
    content_parts.append("""
        <div class="info-section">
            <h4>GDP Growth, Industrial Production & Employment Dynamics</h4>
            <p>Comprehensive analysis of economic growth momentum, industrial activity, labor market conditions, 
            and business cycle positioning. Assessment of growth trajectory implications for portfolio companies 
            and investment strategy.</p>
        </div>
    """)
    
    if 'indicators' in analysis:
        indicators_df = _create_growth_indicators_dataframe(analysis['indicators'])
        
        content_parts.append('<div class="metric-highlight">')
        content_parts.append('<h4>Growth & Employment Indicators Analysis</h4>')
        content_parts.append(build_data_table(indicators_df, table_id="growth-indicators-table", page_length=10))
        content_parts.append('</div>')
    
    if 'economic_momentum' in analysis:
        momentum = analysis['economic_momentum']
        momentum_badge = _get_momentum_badge(momentum['momentum'])
        
        momentum_html = f"""
        <div class="info-box {'success' if momentum['momentum'] == 'Strong' else 'warning' if momentum['momentum'] == 'Weak' else 'danger' if momentum['momentum'] == 'Contractionary' else 'info'}">
            <h4>Economic Growth Momentum</h4>
            <p><strong>Growth Phase:</strong> {momentum_badge} {momentum['momentum']}</p>
            <p><strong>Description:</strong> {momentum['description']}</p>
            <ul>
                <li><strong>GDP Trajectory:</strong> {momentum['gdp_trend']:.1f}% trend indicating {'robust' if momentum['gdp_trend'] > 3.0 else 'moderate' if momentum['gdp_trend'] > 2.0 else 'weak'} economic fundamentals</li>
                <li><strong>Industrial Activity:</strong> {momentum['industrial_trend']:.1f}% production trend showing {'strong' if momentum['industrial_trend'] > 2.0 else 'moderate' if momentum['industrial_trend'] > 0 else 'weak'} manufacturing momentum</li>
            </ul>
        </div>
        """
        content_parts.append(momentum_html)
    
    growth_summary = _generate_growth_employment_summary(analysis, len(companies))
    content_parts.append(f'<div class="info-box default">{growth_summary}</div>')
    
    charts_html = _create_growth_employment_charts(economic_df, analysis)
    content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8D",
        "Economic Growth & Labor Market Assessment",
        combined_content
    )


def _analyze_growth_employment(economic_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze economic growth and employment indicators"""
    
    analysis = {}
    indicators = {}
    
    growth_employment_indicators = {
        'Real_GDP': ('GDP Growth', '%', 'Economic expansion momentum'),
        'Industrial_Production': ('Industrial Production', 'Index', 'Manufacturing sector strength'),
        'Unemployment_Rate': ('Unemployment Rate', '%', 'Labor market conditions'),
        'Nonfarm_Payrolls': ('Employment Growth', 'Thousands', 'Job creation trends'),
        'Labor_Force_Participation': ('Labor Participation', '%', 'Workforce engagement'),
        'Initial_Jobless_Claims': ('Jobless Claims', 'Thousands', 'Employment stability')
    }
    
    for indicator, (label, unit, description) in growth_employment_indicators.items():
        if indicator in economic_df.columns:
            series = economic_df[indicator].dropna()
            
            if len(series) >= 2:
                current = series.iloc[-1]
                previous = series.iloc[-2]
                yoy_change = current - previous
                
                if unit == '%':
                    latest_value = f"{current:.1f}%"
                    yoy_change_str = f"{yoy_change:+.1f}pp"
                elif unit == 'Index':
                    latest_value = f"{current:.1f}"
                    yoy_change_str = f"{yoy_change:+.1f}"
                else:
                    latest_value = f"{current:,.0f}K"
                    yoy_change_str = f"{yoy_change:+,.0f}K"
                
                if len(series) >= 3:
                    recent_trend = series.tail(3).values
                    if np.all(np.diff(recent_trend) > 0):
                        trend_direction = 'Improving'
                    elif np.all(np.diff(recent_trend) < 0):
                        trend_direction = 'Weakening'
                    else:
                        trend_direction = 'Mixed'
                else:
                    trend_direction = 'Stable'
                
                if indicator == 'Real_GDP':
                    if current > 3.0:
                        cycle_phase = 'Expansion'
                    elif current > 1.0:
                        cycle_phase = 'Moderate Growth'
                    elif current > -1.0:
                        cycle_phase = 'Slow Growth'
                    else:
                        cycle_phase = 'Contraction'
                elif indicator == 'Unemployment_Rate':
                    if current < 4.0:
                        cycle_phase = 'Full Employment'
                    elif current < 6.0:
                        cycle_phase = 'Healthy Labor Market'
                    elif current < 8.0:
                        cycle_phase = 'Weakening Employment'
                    else:
                        cycle_phase = 'High Unemployment'
                else:
                    cycle_phase = 'Stable'
                
                sector_impact = 'General Economic Impact'
                
                if trend_direction == 'Improving' and cycle_phase in ['Expansion', 'Full Employment', 'Healthy Labor Market']:
                    investment_implication = 'Supportive for Growth'
                elif trend_direction == 'Weakening' or cycle_phase in ['Contraction', 'High Unemployment']:
                    investment_implication = 'Defensive Positioning'
                else:
                    investment_implication = 'Neutral Environment'
                
                indicators[label] = {
                    'latest_value': latest_value,
                    'yoy_change': yoy_change_str,
                    'trend_direction': trend_direction,
                    'cycle_phase': cycle_phase,
                    'sector_impact': sector_impact,
                    'investment_implication': investment_implication,
                    'description': description
                }
    
    analysis['indicators'] = indicators
    
    if 'Real_GDP' in economic_df.columns and 'Industrial_Production' in economic_df.columns:
        gdp_series = economic_df['Real_GDP'].dropna()
        indpro_series = economic_df['Industrial_Production'].dropna()
        
        if len(gdp_series) >= 3 and len(indpro_series) >= 3:
            recent_gdp = gdp_series.tail(3).mean()
            recent_indpro = indpro_series.tail(3).mean()
            
            if recent_gdp > 3.0 and recent_indpro > 2.0:
                momentum = 'Strong'
                momentum_desc = 'Robust economic expansion across sectors'
            elif recent_gdp > 2.0 and recent_indpro > 0:
                momentum = 'Moderate'
                momentum_desc = 'Steady economic growth with mixed sectoral performance'
            elif recent_gdp > 0 and recent_indpro > -2.0:
                momentum = 'Weak'
                momentum_desc = 'Sluggish economic growth with limited momentum'
            else:
                momentum = 'Contractionary'
                momentum_desc = 'Economic contraction requiring policy response'
            
            analysis['economic_momentum'] = {
                'momentum': momentum,
                'description': momentum_desc,
                'gdp_trend': recent_gdp,
                'industrial_trend': recent_indpro
            }
    
    return analysis


def _create_growth_indicators_dataframe(indicators: Dict) -> pd.DataFrame:
    """Create DataFrame from growth indicators for table display"""
    
    rows = []
    for indicator, data in indicators.items():
        rows.append({
            'Indicator': indicator,
            'Latest Value': data['latest_value'],
            'YoY Change': data['yoy_change'],
            'Trend Direction': data['trend_direction'],
            'Business Cycle Phase': data['cycle_phase'],
            'Sector Impact': data['sector_impact'],
            'Investment Implication': data['investment_implication']
        })
    
    return pd.DataFrame(rows)


def _generate_growth_employment_summary(analysis: Dict, num_companies: int) -> str:
    """Generate growth and employment analysis summary"""
    
    indicators = analysis.get('indicators', {})
    momentum = analysis.get('economic_momentum', {})
    
    if not indicators:
        return "<p>Growth and employment data insufficient for analysis.</p>"
    
    improving_indicators = sum(1 for data in indicators.values() if data['trend_direction'] == 'Improving')
    weakening_indicators = sum(1 for data in indicators.values() if data['trend_direction'] == 'Weakening')
    total_indicators = len(indicators)
    
    supportive_indicators = sum(1 for data in indicators.values() if 'Supportive' in data['investment_implication'])
    
    return f"""
        <h4>Economic Growth & Employment Assessment</h4>
        <ul>
            <li><strong>Growth Indicator Trends:</strong> {improving_indicators}/{total_indicators} indicators improving vs {weakening_indicators}/{total_indicators} weakening</li>
            <li><strong>Investment Environment:</strong> {supportive_indicators}/{total_indicators} indicators providing supportive investment conditions</li>
            <li><strong>Labor Market Dynamics:</strong> {'Strong' if any('Full Employment' in data['cycle_phase'] for data in indicators.values()) else 'Stable' if any('Healthy' in data['cycle_phase'] for data in indicators.values()) else 'Challenging'} employment environment</li>
            <li><strong>Portfolio Companies:</strong> {num_companies} companies {'benefit from robust growth momentum' if momentum.get('momentum') == 'Strong' else 'face mixed economic conditions' if momentum.get('momentum') == 'Moderate' else 'require defensive positioning' if momentum.get('momentum') in ['Weak', 'Contractionary'] else 'operate in standard environment'}</li>
            <li><strong>Business Cycle Positioning:</strong> {'Late Cycle' if momentum.get('momentum') == 'Strong' and any('Full Employment' in data['cycle_phase'] for data in indicators.values()) else 'Mid Cycle' if momentum.get('momentum') in ['Strong', 'Moderate'] else 'Early Cycle'} economic positioning</li>
        </ul>
    """


def _create_growth_employment_charts(economic_df: pd.DataFrame, analysis: Dict) -> str:
    """Create growth and employment visualization charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Growth & Employment Indicators Visualization</h4>'
    
    if 'Year' not in economic_df.columns:
        return charts_html + "<p>Year data not available for time series charts.</p>"
    
    years = economic_df['Year'].tolist()
    
    # Chart 1: GDP Growth Bar Chart
    if 'Real_GDP' in economic_df.columns:
        gdp_data = economic_df['Real_GDP'].tolist()
        
        colors = []
        for value in gdp_data:
            if pd.notna(value):
                if value > 3.0:
                    colors.append('#2ca02c')
                elif value > 1.0:
                    colors.append('#8bc34a')
                elif value > -1.0:
                    colors.append('#ff9800')
                else:
                    colors.append('#f44336')
            else:
                colors.append('#999999')
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': years[:len(gdp_data)],
                'y': gdp_data,
                'marker': {'color': colors},
                'text': [f'{v:.1f}%' if pd.notna(v) else 'N/A' for v in gdp_data],
                'textposition': 'outside',
                'hovertemplate': '<b>%{x}</b><br>GDP Growth: %{y:.2f}%<extra></extra>'
            }],
            'layout': {
                'title': 'Economic Growth Performance (Real GDP)',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'GDP Growth (%)'},
                'hovermode': 'x unified',
                'shapes': [
                    {
                        'type': 'line',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 0,
                        'y1': 0,
                        'line': {'color': 'black', 'width': 1}
                    },
                    {
                        'type': 'line',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 2.0,
                        'y1': 2.0,
                        'line': {'color': 'blue', 'dash': 'dash', 'width': 1}
                    }
                ],
                'annotations': [{
                    'x': years[-1],
                    'y': 2.0,
                    'text': 'Trend Growth',
                    'showarrow': False,
                    'xanchor': 'left',
                    'font': {'color': 'blue', 'size': 9}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-gdp-bars", height=400)
    
    # Chart 2: Unemployment
    if 'Unemployment_Rate' in economic_df.columns:
        unemployment_data = economic_df['Unemployment_Rate'].tolist()
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(unemployment_data)],
                'y': unemployment_data,
                'name': 'Unemployment Rate',
                'fill': 'tozeroy',
                'fillcolor': 'rgba(148, 103, 189, 0.2)',
                'line': {'color': '#9467bd', 'width': 3},
                'marker': {'size': 8}
            }],
            'layout': {
                'title': 'Labor Market Conditions',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Unemployment Rate (%)'},
                'hovermode': 'x unified',
                'shapes': [{
                    'type': 'line',
                    'x0': years[0],
                    'x1': years[-1],
                    'y0': 5.0,
                    'y1': 5.0,
                    'line': {'color': 'orange', 'dash': 'dash', 'width': 1}
                }],
                'annotations': [{
                    'x': years[-1],
                    'y': 5.0,
                    'text': 'Natural Rate (~5%)',
                    'showarrow': False,
                    'xanchor': 'left',
                    'font': {'color': 'orange', 'size': 9}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="new-chart-unemployment", height=400)
    
    # Chart 3: Industrial Production
    if 'Industrial_Production' in economic_df.columns:
        indpro_data = economic_df['Industrial_Production'].tolist()
        
        traces = [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': years[:len(indpro_data)],
            'y': indpro_data,
            'name': 'Industrial Production',
            'line': {'color': '#ff7f0e', 'width': 3},
            'marker': {'size': 6}
        }]
        
        layout = {
            'title': 'Manufacturing Sector Indicators',
            'xaxis': {'title': 'Year'},
            'yaxis': {'title': 'Industrial Production Growth (%)'},
            'hovermode': 'x unified',
            'shapes': [{
                'type': 'line',
                'x0': years[0],
                'x1': years[-1],
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'dash': 'dash', 'width': 1}
            }]
        }
        
        if 'Capacity_Utilization' in economic_df.columns:
            cap_util_data = economic_df['Capacity_Utilization'].tolist()
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years[:len(cap_util_data)],
                'y': cap_util_data,
                'name': 'Capacity Utilization',
                'yaxis': 'y2',
                'line': {'color': '#2ca02c', 'width': 3},
                'marker': {'size': 6}
            })
            layout['yaxis2'] = {
                'title': 'Capacity Utilization (%)',
                'overlaying': 'y',
                'side': 'right'
            }
        
        fig_data = {'data': traces, 'layout': layout}
        charts_html += build_plotly_chart(fig_data, div_id="chart-indpro-caputil", height=400)
    
    # Chart 4: Status Heatmap
    if 'indicators' in analysis and analysis['indicators']:
        indicators_list = list(analysis['indicators'].keys())
        
        if len(indicators_list) > 0:
            trend_scores = []
            cycle_scores = []
            
            for indicator in indicators_list:
                data = analysis['indicators'][indicator]
                
                trend = data['trend_direction']
                trend_score = 1 if trend == 'Improving' else -1 if trend == 'Weakening' else 0
                trend_scores.append(trend_score)
                
                cycle = data['cycle_phase']
                if any(word in cycle for word in ['Expansion', 'Full Employment', 'Healthy']):
                    cycle_score = 1
                elif any(word in cycle for word in ['Contraction', 'High Unemployment', 'Weakening']):
                    cycle_score = -1
                else:
                    cycle_score = 0
                cycle_scores.append(cycle_score)
            
            # Truncate indicator names for display
            display_labels = []
            for ind in indicators_list:
                if len(ind) > 20:
                    display_labels.append(ind[:17] + '...')
                else:
                    display_labels.append(ind)
            
            fig_data = {
                'data': [{
                    'type': 'heatmap',
                    'z': [trend_scores, cycle_scores],
                    'x': display_labels,
                    'y': ['Trend Direction', 'Business Cycle'],
                    'colorscale': [
                        [0, '#d62728'],
                        [0.5, '#ffffe0'],
                        [1, '#2ca02c']
                    ],
                    'zmid': 0,
                    'zmin': -1,
                    'zmax': 1,
                    'showscale': True,
                    'colorbar': {
                        'title': 'Status',
                        'tickvals': [-1, 0, 1],
                        'ticktext': ['Negative', 'Neutral', 'Positive']
                    },
                    'hovertemplate': '<b>%{y}</b><br>%{x}<br>Score: %{z}<extra></extra>'
                }],
                'layout': {
                    'title': 'Economic Indicators Status Matrix',
                    'xaxis': {
                        'tickangle': -45,
                        'tickfont': {'size': 10}
                    },
                    'yaxis': {
                        'side': 'left',
                        'tickfont': {'size': 11}
                    },
                    'margin': {'l': 100, 'r': 50, 't': 50, 'b': 100},
                    'height': 350
                }
            }
            
            charts_html += build_plotly_chart(fig_data, div_id="chart-status-heatmap", height=350)
        else:
            charts_html += "<p><em>Insufficient indicators for status heatmap visualization.</em></p>"
    else:
        charts_html += "<p><em>No indicator data available for status matrix.</em></p>"
    
    return charts_html


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _get_inflation_regime_badge(regime: str) -> str:
    """Get badge emoji for inflation regime"""
    badge_map = {
        'High Inflation': '🔴',
        'Elevated Inflation': '🟡',
        'Target Range': '🟢',
        'Low Inflation': '🔵'
    }
    return badge_map.get(regime, '⚪')


def _get_momentum_badge(momentum: str) -> str:
    """Get badge emoji for economic momentum"""
    badge_map = {
        'Strong': '🟢',
        'Moderate': '🔵',
        'Weak': '🟡',
        'Contractionary': '🔴'
    }
    return badge_map.get(momentum, '⚪')



# =============================================================================
# SUBSECTION 8E: FINANCIAL MARKET CONDITIONS & RISK ASSESSMENT
# =============================================================================

def _build_section_8e_market_risk(economic_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8E: Financial Market Conditions & Risk Assessment"""
    
    if economic_df.empty:
        return _build_collapsible_subsection(
            "8E",
            "Financial Market Conditions & Risk Assessment",
            "<p>Economic data unavailable for market risk analysis.</p>"
        )
    
    # Analyze market risk conditions
    analysis = _analyze_market_risk_conditions(economic_df)
    
    if not analysis:
        return _build_collapsible_subsection(
            "8E",
            "Financial Market Conditions & Risk Assessment",
            "<p>Market risk data unavailable for comprehensive assessment.</p>"
        )
    
    # Build content sections
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Market Risk Indicators & Volatility Analysis</h4>
            <p>Comprehensive assessment of financial market conditions including volatility measures, 
            credit spreads, liquidity conditions, term structure risk, and economic uncertainty indicators. 
            Analysis of market stress levels and risk environment implications for portfolio positioning.</p>
        </div>
    """)
    
    # Market Risk Assessment Table
    risk_table_df = _create_market_risk_table(analysis)
    
    content_parts.append('<div class="metric-highlight">')
    content_parts.append('<h4>Market Risk Assessment</h4>')
    content_parts.append(build_data_table(risk_table_df, table_id="market-risk-table", page_length=-1))
    content_parts.append('</div>')
    
    # Overall Risk Assessment
    overall_risk = _assess_overall_risk(analysis)
    risk_badge = _get_risk_level_badge(overall_risk['level'])
    
    risk_html = f"""
    <div class="info-box {overall_risk['box_type']}">
        <h4>Overall Market Risk Environment</h4>
        <p><strong>Risk Level:</strong> {risk_badge} {overall_risk['level']}</p>
        <p><strong>Assessment:</strong> {overall_risk['assessment']}</p>
        <ul>
            <li><strong>High Risk Signals:</strong> {overall_risk['high_risk_count']}/{overall_risk['total_indicators']} indicators showing elevated risk</li>
            <li><strong>Portfolio Implication:</strong> {overall_risk['implication']}</li>
        </ul>
    </div>
    """
    content_parts.append(risk_html)
    
    # Market Risk Summary
    risk_summary = _generate_market_risk_summary(analysis, len(companies))
    content_parts.append(f'<div class="info-box default">{risk_summary}</div>')
    
    # Create market risk charts
    charts_html = _create_market_risk_charts(economic_df, analysis)
    content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8E",
        "Financial Market Conditions & Risk Assessment",
        combined_content
    )


def _analyze_market_risk_conditions(economic_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze market conditions and risk indicators"""
    
    analysis = {}
    
    # Market volatility analysis (VIX)
    if 'VIX_Index' in economic_df.columns:
        vix_series = economic_df['VIX_Index'].dropna()
        if len(vix_series) > 0:
            current_vix = vix_series.iloc[-1]
            
            if current_vix > 30:
                vol_level = f"{current_vix:.1f} (High)"
                vol_assessment = 'Elevated Fear'
                vol_implication = 'Risk-off sentiment, defensive positioning'
            elif current_vix > 20:
                vol_level = f"{current_vix:.1f} (Moderate)"
                vol_assessment = 'Normal Volatility'
                vol_implication = 'Standard risk environment'
            else:
                vol_level = f"{current_vix:.1f} (Low)"
                vol_assessment = 'Low Fear'
                vol_implication = 'Risk-on sentiment, growth opportunities'
            
            analysis['volatility'] = vol_level
            analysis['vol_assessment'] = vol_assessment
            analysis['vol_implication'] = vol_implication
    
    # Credit spread analysis (using treasury spreads as proxy)
    if 'Treasury_10Y' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        ten_year = economic_df['Treasury_10Y'].dropna()
        three_month = economic_df['Treasury_3M'].dropna()
        
        if len(ten_year) > 0 and len(three_month) > 0:
            spread = ten_year.iloc[-1] - three_month.iloc[-1]
            
            if spread < 0:
                spread_level = f"{spread:.2f}pp (Inverted)"
                credit_assessment = 'Recession Risk'
                credit_implication = 'Credit quality concerns, defensive positioning'
            elif spread < 0.5:
                spread_level = f"{spread:.2f}pp (Flat)"
                credit_assessment = 'Tight Spreads'
                credit_implication = 'Limited credit risk premium'
            elif spread < 2.0:
                spread_level = f"{spread:.2f}pp (Normal)"
                credit_assessment = 'Healthy Spreads'
                credit_implication = 'Normal credit conditions'
            else:
                spread_level = f"{spread:.2f}pp (Wide)"
                credit_assessment = 'Wide Spreads'
                credit_implication = 'Credit stress indicators'
            
            analysis['credit_spreads'] = spread_level
            analysis['credit_assessment'] = credit_assessment
            analysis['credit_implication'] = credit_implication
    
    # Liquidity conditions (M2 growth and rates)
    if 'M2_Money_Supply' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        m2_series = economic_df['M2_Money_Supply'].dropna()
        rates_series = economic_df['Treasury_3M'].dropna()
        
        if len(m2_series) >= 2 and len(rates_series) > 0:
            m2_growth = ((m2_series.iloc[-1] / m2_series.iloc[-2]) - 1) * 100 if len(m2_series) >= 2 else 0
            current_rate = rates_series.iloc[-1]
            
            if m2_growth > 5 and current_rate < 2:
                liquidity_level = "Abundant"
                liquidity_assessment = 'High Liquidity'
                liquidity_implication = 'Strong liquidity supporting risk assets'
            elif m2_growth > 2 and current_rate < 4:
                liquidity_level = "Adequate"
                liquidity_assessment = 'Normal Liquidity'
                liquidity_implication = 'Standard liquidity conditions'
            else:
                liquidity_level = "Tight"
                liquidity_assessment = 'Constrained Liquidity'
                liquidity_implication = 'Limited liquidity pressuring risk assets'
            
            analysis['liquidity'] = liquidity_level
            analysis['liquidity_assessment'] = liquidity_assessment
            analysis['liquidity_implication'] = liquidity_implication
    
    # Term structure risk
    if 'Treasury_30Y' in economic_df.columns and 'Treasury_2Y' in economic_df.columns:
        long_term = economic_df['Treasury_30Y'].dropna()
        short_term = economic_df['Treasury_2Y'].dropna()
        
        if len(long_term) > 0 and len(short_term) > 0:
            term_spread = long_term.iloc[-1] - short_term.iloc[-1]
            
            if term_spread > 2.0:
                term_level = f"{term_spread:.2f}pp (Steep)"
                term_assessment = 'Low Term Risk'
                term_implication = 'Normal term structure expectations'
            elif term_spread > 0.5:
                term_level = f"{term_spread:.2f}pp (Normal)"
                term_assessment = 'Moderate Term Risk'
                term_implication = 'Standard term structure risk'
            else:
                term_level = f"{term_spread:.2f}pp (Flat/Inverted)"
                term_assessment = 'High Term Risk'
                term_implication = 'Distorted term structure signaling stress'
            
            analysis['term_risk'] = term_level
            analysis['term_assessment'] = term_assessment
            analysis['term_implication'] = term_implication
    
    # Economic uncertainty assessment
    uncertainty_indicators = 0
    uncertainty_signals = 0
    
    # Check VIX
    if 'volatility' in analysis:
        uncertainty_indicators += 1
        vix_val = float(analysis['volatility'].split()[0])
        if vix_val > 25:
            uncertainty_signals += 1
    
    # Check yield curve
    if 'credit_spreads' in analysis:
        uncertainty_indicators += 1
        if 'Inverted' in analysis['credit_spreads']:
            uncertainty_signals += 1
    
    if uncertainty_indicators > 0:
        uncertainty_ratio = uncertainty_signals / uncertainty_indicators
        
        if uncertainty_ratio > 0.6:
            uncertainty_level = "High"
            uncertainty_assessment = 'Elevated Uncertainty'
            uncertainty_implication = 'Risk management and hedging strategies warranted'
        elif uncertainty_ratio > 0.3:
            uncertainty_level = "Moderate"
            uncertainty_assessment = 'Standard Uncertainty'
            uncertainty_implication = 'Normal risk monitoring required'
        else:
            uncertainty_level = "Low"
            uncertainty_assessment = 'Low Uncertainty'
            uncertainty_implication = 'Favorable risk environment for growth strategies'
        
        analysis['uncertainty'] = uncertainty_level
        analysis['uncertainty_assessment'] = uncertainty_assessment
        analysis['uncertainty_implication'] = uncertainty_implication
    
    return analysis


def _create_market_risk_table(analysis: Dict) -> pd.DataFrame:
    """Create market risk assessment table"""
    
    rows = []
    
    risk_categories = [
        ('Market Volatility', 'volatility', 'vol_assessment', 'vol_implication'),
        ('Credit Spreads', 'credit_spreads', 'credit_assessment', 'credit_implication'),
        ('Liquidity Conditions', 'liquidity', 'liquidity_assessment', 'liquidity_implication'),
        ('Term Structure Risk', 'term_risk', 'term_assessment', 'term_implication'),
        ('Economic Uncertainty', 'uncertainty', 'uncertainty_assessment', 'uncertainty_implication')
    ]
    
    for category, level_key, assessment_key, implication_key in risk_categories:
        if level_key in analysis:
            rows.append({
                'Risk Category': category,
                'Current Level': analysis.get(level_key, 'N/A'),
                'Assessment': analysis.get(assessment_key, 'N/A'),
                'Portfolio Implication': analysis.get(implication_key, 'N/A')
            })
    
    return pd.DataFrame(rows)


def _assess_overall_risk(analysis: Dict) -> Dict[str, Any]:
    """Assess overall market risk level"""
    
    high_risk_signals = 0
    total_risk_indicators = 0
    
    risk_components = ['vol_assessment', 'credit_assessment', 'liquidity_assessment', 
                      'term_assessment', 'uncertainty_assessment']
    
    for component in risk_components:
        if component in analysis:
            total_risk_indicators += 1
            if any(word in analysis[component] for word in ['High', 'Elevated', 'Constrained', 'Recession']):
                high_risk_signals += 1
    
    if total_risk_indicators == 0:
        return {
            'level': 'Unknown',
            'assessment': 'Insufficient data for risk assessment',
            'implication': 'Standard risk monitoring recommended',
            'high_risk_count': 0,
            'total_indicators': 0,
            'box_type': 'info'
        }
    
    risk_ratio = high_risk_signals / total_risk_indicators
    
    if risk_ratio > 0.6:
        level = "High"
        assessment = "Multiple elevated risk indicators requiring defensive positioning"
        implication = "Implement comprehensive risk management and hedging strategies"
        box_type = "danger"
    elif risk_ratio > 0.3:
        level = "Moderate"
        assessment = "Mixed risk environment with selective elevated indicators"
        implication = "Maintain standard risk monitoring with selective hedging"
        box_type = "warning"
    else:
        level = "Low"
        assessment = "Favorable risk environment supporting growth strategies"
        implication = "Focus on growth opportunities with normal risk controls"
        box_type = "success"
    
    return {
        'level': level,
        'assessment': assessment,
        'implication': implication,
        'high_risk_count': high_risk_signals,
        'total_indicators': total_risk_indicators,
        'box_type': box_type
    }


def _generate_market_risk_summary(analysis: Dict, num_companies: int) -> str:
    """Generate market risk and conditions summary"""
    
    if not analysis:
        return "<p>Market risk data insufficient for comprehensive assessment.</p>"
    
    overall_risk = _assess_overall_risk(analysis)
    
    return f"""
        <h4>Financial Market Risk & Conditions Assessment</h4>
        <ul>
            <li><strong>Overall Risk Environment:</strong> {overall_risk['level']} market risk profile with {overall_risk['high_risk_count']}/{overall_risk['total_indicators']} elevated risk indicators</li>
            <li><strong>Market Volatility:</strong> {analysis.get('vol_assessment', 'Unknown')} with {analysis.get('vol_implication', 'standard market conditions')}</li>
            <li><strong>Credit Conditions:</strong> {analysis.get('credit_assessment', 'Unknown')} indicating {analysis.get('credit_implication', 'normal credit environment')}</li>
            <li><strong>Liquidity Environment:</strong> {analysis.get('liquidity_assessment', 'Unknown')} with {analysis.get('liquidity_implication', 'standard liquidity conditions')}</li>
            <li><strong>Portfolio Companies:</strong> {num_companies} companies exposed to {'heightened' if overall_risk['level'] == 'High' else 'moderate' if overall_risk['level'] == 'Moderate' else 'standard'} market risk environment</li>
            <li><strong>Risk Management Priority:</strong> {'High' if overall_risk['level'] == 'High' else 'Moderate' if overall_risk['level'] == 'Moderate' else 'Standard'} risk monitoring and mitigation strategies recommended</li>
        </ul>
    """


def _create_market_risk_charts(economic_df: pd.DataFrame, analysis: Dict) -> str:
    """Create market risk assessment charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Market Risk Environment Visualization</h4>'
    
    if 'Year' not in economic_df.columns:
        return charts_html + "<p>Year data not available for time series charts.</p>"
    
    years = economic_df['Year'].tolist()
    
    # Chart 1: VIX Volatility Index
    if 'VIX_Index' in economic_df.columns:
        vix_data = economic_df['VIX_Index'].tolist()
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'mode': 'lines',
                'x': years[:len(vix_data)],
                'y': vix_data,
                'name': 'VIX Index',
                'fill': 'tozeroy',
                'fillcolor': 'rgba(102, 126, 234, 0.3)',
                'line': {'color': '#667eea', 'width': 3}
            }],
            'layout': {
                'title': 'Market Volatility (VIX Index)',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'VIX Index'},
                'hovermode': 'x unified',
                'shapes': [
                    {
                        'type': 'line',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 20,
                        'y1': 20,
                        'line': {'color': 'green', 'dash': 'dash', 'width': 1}
                    },
                    {
                        'type': 'line',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 30,
                        'y1': 30,
                        'line': {'color': 'orange', 'dash': 'dash', 'width': 1}
                    },
                    {
                        'type': 'rect',
                        'x0': years[0],
                        'x1': years[-1],
                        'y0': 30,
                        'y1': max(vix_data) if vix_data else 50,
                        'fillcolor': 'rgba(255, 0, 0, 0.1)',
                        'line': {'width': 0},
                        'layer': 'below'
                    }
                ],
                'annotations': [
                    {
                        'x': years[-1],
                        'y': 20,
                        'text': 'Low Risk (20)',
                        'showarrow': False,
                        'xanchor': 'left',
                        'font': {'color': 'green', 'size': 9}
                    },
                    {
                        'x': years[-1],
                        'y': 30,
                        'text': 'High Risk (30)',
                        'showarrow': False,
                        'xanchor': 'left',
                        'font': {'color': 'orange', 'size': 9}
                    }
                ]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-vix", height=400)
    
    # Chart 2: Yield Curve Spread (credit risk proxy)
    if 'Treasury_10Y' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        ten_year = economic_df['Treasury_10Y'].tolist()
        three_month = economic_df['Treasury_3M'].tolist()
        
        min_len = min(len(ten_year), len(three_month), len(years))
        spread = [ten_year[i] - three_month[i] for i in range(min_len)]
        years_spread = years[:min_len]
        
        positive_spread = [s if s >= 0 else 0 for s in spread]
        negative_spread = [s if s < 0 else 0 for s in spread]
        
        fig_data = {
            'data': [
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_spread,
                    'y': positive_spread,
                    'name': 'Normal Curve',
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(46, 160, 44, 0.3)',
                    'line': {'color': 'rgba(46, 160, 44, 0)', 'width': 0},
                    'showlegend': True
                },
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_spread,
                    'y': negative_spread,
                    'name': 'Inverted Curve',
                    'fill': 'tozeroy',
                    'fillcolor': 'rgba(214, 39, 40, 0.3)',
                    'line': {'color': 'rgba(214, 39, 40, 0)', 'width': 0},
                    'showlegend': True
                },
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years_spread,
                    'y': spread,
                    'name': '10Y-3M Spread',
                    'line': {'color': '#1f77b4', 'width': 3}
                }
            ],
            'layout': {
                'title': 'Yield Curve Health (Credit Risk Proxy)',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Yield Spread (pp)'},
                'hovermode': 'x unified',
                'shapes': [{
                    'type': 'line',
                    'x0': years_spread[0],
                    'x1': years_spread[-1],
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'black', 'width': 2}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-credit-spread", height=400)
    
    # Chart 3: Economic Stress Indicators Bar Chart
    stress_indicators = []
    stress_values = []
    stress_colors = []
    
    if 'VIX_Index' in economic_df.columns and len(economic_df['VIX_Index'].dropna()) > 0:
        current_vix = economic_df['VIX_Index'].dropna().iloc[-1]
        stress_indicators.append('Market Volatility')
        stress_val = min(current_vix / 50 * 100, 100)
        stress_values.append(stress_val)
        stress_colors.append('#ef4444' if stress_val > 70 else '#ff9800' if stress_val > 40 else '#2ca02c')
    
    if 'Unemployment_Rate' in economic_df.columns and len(economic_df['Unemployment_Rate'].dropna()) > 0:
        current_unemployment = economic_df['Unemployment_Rate'].dropna().iloc[-1]
        stress_indicators.append('Labor Market Stress')
        stress_val = min(current_unemployment / 10 * 100, 100)
        stress_values.append(stress_val)
        stress_colors.append('#ef4444' if stress_val > 70 else '#ff9800' if stress_val > 40 else '#2ca02c')
    
    if 'Treasury_10Y' in economic_df.columns and 'Treasury_3M' in economic_df.columns:
        ten_y = economic_df['Treasury_10Y'].dropna()
        three_m = economic_df['Treasury_3M'].dropna()
        if len(ten_y) > 0 and len(three_m) > 0:
            spread = ten_y.iloc[-1] - three_m.iloc[-1]
            stress_indicators.append('Yield Curve Stress')
            stress_val = max(0, min((2 - spread) / 2 * 100, 100))
            stress_values.append(stress_val)
            stress_colors.append('#ef4444' if stress_val > 70 else '#ff9800' if stress_val > 40 else '#2ca02c')
    
    if stress_indicators:
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': stress_values,
                'y': stress_indicators,
                'orientation': 'h',
                'marker': {'color': stress_colors},
                'text': [f'{v:.0f}' for v in stress_values],
                'textposition': 'auto',
                'hovertemplate': '<b>%{y}</b><br>Stress Level: %{x:.1f}<extra></extra>'
            }],
            'layout': {
                'title': 'Current Economic Stress Indicators',
                'xaxis': {'title': 'Stress Level (0-100)', 'range': [0, 100]},
                'yaxis': {'title': ''},
                'hovermode': 'closest',
                'shapes': [{
                    'type': 'line',
                    'x0': 50,
                    'x1': 50,
                    'y0': -0.5,
                    'y1': len(stress_indicators) - 0.5,
                    'line': {'color': 'blue', 'dash': 'dash', 'width': 2}
                }],
                'annotations': [{
                    'x': 50,
                    'y': len(stress_indicators) - 0.5,
                    'text': 'Neutral (50)',
                    'showarrow': False,
                    'yanchor': 'bottom',
                    'font': {'color': 'blue'}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-stress-indicators", height=400)
    
    # Chart 4: Comprehensive Risk Assessment
    if analysis:
        risk_categories = []
        risk_scores = []
        risk_colors = []
        
        risk_mapping = {
            'vol_assessment': ('Market\nVolatility', ['High', 'Elevated'], ['Low']),
            'credit_assessment': ('Credit\nConditions', ['Recession', 'Tight'], ['Healthy']),
            'liquidity_assessment': ('Liquidity\nStress', ['Constrained'], ['High']),
            'term_assessment': ('Term\nStructure', ['High', 'Distorted'], ['Low']),
            'uncertainty_assessment': ('Economic\nUncertainty', ['Elevated', 'High'], ['Low'])
        }
        
        for key, (label, high_words, low_words) in risk_mapping.items():
            if key in analysis:
                assessment = analysis[key]
                if any(word in assessment for word in high_words):
                    score = 80
                    color = '#ef4444'
                elif any(word in assessment for word in low_words):
                    score = 20
                    color = '#2ca02c'
                else:
                    score = 50
                    color = '#ff9800'
                
                risk_categories.append(label)
                risk_scores.append(score)
                risk_colors.append(color)
        
        if risk_categories:
            fig_data = {
                'data': [{
                    'type': 'bar',
                    'x': risk_categories,
                    'y': risk_scores,
                    'marker': {'color': risk_colors},
                    'text': [f'{s:.0f}' for s in risk_scores],
                    'textposition': 'outside',
                    'hovertemplate': '<b>%{x}</b><br>Risk Level: %{y:.0f}<extra></extra>'
                }],
                'layout': {
                    'title': 'Comprehensive Risk Assessment',
                    'xaxis': {'title': ''},
                    'yaxis': {'title': 'Risk Level (0-100)', 'range': [0, 105]},
                    'hovermode': 'closest',
                    'shapes': [{
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(risk_categories) - 0.5,
                        'y0': 50,
                        'y1': 50,
                        'line': {'color': 'blue', 'dash': 'dash', 'width': 2}
                    }],
                    'annotations': [{
                        'x': 0,
                        'y': 50,
                        'text': 'Neutral Risk',
                        'showarrow': False,
                        'xanchor': 'left',
                        'yanchor': 'bottom',
                        'font': {'color': 'blue'}
                    }]
                }
            }
            
            charts_html += build_plotly_chart(fig_data, div_id="chart-risk-assessment", height=400)
    
    return charts_html


# =============================================================================
# SUBSECTION 8F: COMPREHENSIVE MACROECONOMIC VISUALIZATION SUITE
# =============================================================================

def _build_section_8f_visualizations(economic_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8F: Comprehensive Macroeconomic Visualization Suite"""
    
    if economic_df.empty:
        return _build_collapsible_subsection(
            "8F",
            "Comprehensive Macroeconomic Visualization Suite",
            "<p>Economic data unavailable for additional visualizations.</p>"
        )
    
    # Build content sections
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Additional Macroeconomic Analysis & Correlation Insights</h4>
            <p>Supplementary visualizations providing cross-indicator relationships, economic interdependencies, 
            and normalized trend analysis across multiple macroeconomic metrics. Enhanced perspective on 
            economic environment through correlation matrices and comparative time series analysis.</p>
        </div>
    """)
    
    # Create additional visualization charts
    charts_html = _create_additional_macro_charts(economic_df)
    content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8F",
        "Comprehensive Macroeconomic Visualization Suite",
        combined_content
    )


def _create_additional_macro_charts(economic_df: pd.DataFrame) -> str:
    """Create additional macroeconomic visualization charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Additional Macroeconomic Visualizations</h4>'
    
    if 'Year' not in economic_df.columns:
        return charts_html + "<p>Year data not available for visualization charts.</p>"
    
    years = economic_df['Year'].tolist()
    
    # Chart 1: Macroeconomic Correlation Heatmap
    key_indicators = ['Real_GDP', 'CPI_All_Items', 'Unemployment_Rate', 'Treasury_10Y', 
                     'Treasury_3M', 'Industrial_Production', 'S&P_500_Index', 'VIX_Index']
    
    available_indicators = [ind for ind in key_indicators if ind in economic_df.columns]
    
    if len(available_indicators) >= 3:
        correlation_data = economic_df[available_indicators].corr()
        
        # Create correlation matrix values
        z_values = correlation_data.values.tolist()
        labels = [ind.replace('_', ' ') for ind in available_indicators]
        
        fig_data = {
            'data': [{
                'type': 'heatmap',
                'z': z_values,
                'x': labels,
                'y': labels,
                'colorscale': 'RdBu',
                'zmid': 0,
                'zmin': -1,
                'zmax': 1,
                'showscale': True,
                'colorbar': {'title': 'Correlation'},
                'text': [[f'{val:.2f}' for val in row] for row in z_values],
                'texttemplate': '%{text}',
                'textfont': {'size': 10},
                'hovertemplate': '<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
            }],
            'layout': {
                'title': 'Macroeconomic Indicators Correlation Matrix',
                'xaxis': {
                    'tickangle': -45,
                    'side': 'bottom',
                    'tickfont': {'size': 10}
                },
                'yaxis': {
                    'tickfont': {'size': 10}
                },
                'margin': {'l': 120, 'r': 50, 't': 60, 'b': 120}
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id="chart-correlation-matrix", height=500)
    
    # Chart 2: Normalized Economic Indicators Trends
    if len(available_indicators[:6]) >= 3:
        normalized_data = {}
        
        for indicator in available_indicators[:6]:
            series = economic_df[indicator].dropna()
            if len(series) > 1:
                min_val = series.min()
                max_val = series.max()
                if max_val > min_val:
                    normalized = (series - min_val) / (max_val - min_val) * 100
                    normalized_data[indicator] = normalized.tolist()
        
        if normalized_data:
            traces = []
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            for i, (indicator, data) in enumerate(normalized_data.items()):
                traces.append({
                    'type': 'scatter',
                    'mode': 'lines',
                    'x': years[:len(data)],
                    'y': data,
                    'name': indicator.replace('_', ' '),
                    'line': {'color': colors[i % len(colors)], 'width': 2}
                })
            
            fig_data = {
                'data': traces,
                'layout': {
                    'title': 'Normalized Economic Indicators Trends',
                    'xaxis': {'title': 'Year'},
                    'yaxis': {'title': 'Normalized Index (0-100)'},
                    'hovermode': 'x unified',
                    'legend': {
                        'orientation': 'v',
                        'yanchor': 'top',
                        'y': 1,
                        'xanchor': 'left',
                        'x': 1.02
                    }
                }
            }
            
            charts_html += build_plotly_chart(fig_data, div_id="chart-normalized-trends", height=500)
    
    return charts_html


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _get_risk_level_badge(level: str) -> str:
    """Get badge emoji for risk level"""
    badge_map = {
        'High': '🔴',
        'Moderate': '🟡',
        'Low': '🟢',
        'Unknown': '⚪'
    }
    return badge_map.get(level, '⚪')



# =============================================================================
# SUBSECTION 8G: SECTOR-SPECIFIC MACROECONOMIC CORRELATIONS
# =============================================================================

def _build_section_8g_sector_correlations(economic_df: pd.DataFrame, df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8G: Sector-Specific Macroeconomic Correlations"""
    
    if economic_df.empty or df.empty:
        return _build_collapsible_subsection(
            "8G",
            "Sector-Specific Macroeconomic Correlations",
            "<p>Insufficient data for sector-macro correlation analysis.</p>"
        )
    
    # Analyze sector-macro correlations
    analysis = _analyze_sector_macro_correlations(economic_df, df, companies)
    
    if not analysis:
        return _build_collapsible_subsection(
            "8G",
            "Sector-Specific Macroeconomic Correlations",
            "<p>Unable to compute sector-macro correlations with available data.</p>"
        )
    
    # Build content sections
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Industry-Macro Relationships & Investment Implications</h4>
            <p>Statistical analysis of portfolio revenue growth correlations with key macroeconomic indicators. 
            Assessment of sector-specific economic sensitivities, cyclical relationships, and strategic 
            implications for portfolio positioning across varying macroeconomic environments.</p>
        </div>
    """)
    
    # Sector-Macro Correlation Table
    if analysis:
        correlation_df = _create_sector_macro_correlation_table(analysis)
        
        content_parts.append('<div class="metric-highlight">')
        content_parts.append('<h4>Sector-Macroeconomic Correlation Analysis</h4>')
        content_parts.append(build_data_table(correlation_df, table_id="sector-macro-table", page_length=10))
        content_parts.append('</div>')
    
    # Sector-Macro Summary
    macro_summary = _generate_sector_macro_summary(analysis, len(companies))
    content_parts.append(f'<div class="info-box default">{macro_summary}</div>')
    
    # Create correlation visualization
    if analysis:
        charts_html = _create_sector_macro_charts(analysis)
        content_parts.append(charts_html)
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8G",
        "Sector-Specific Macroeconomic Correlations",
        combined_content
    )


def _analyze_sector_macro_correlations(economic_df: pd.DataFrame, financial_df: pd.DataFrame, 
                                      companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze sector-specific macroeconomic correlations"""
    
    correlations = {}
    
    # Get portfolio revenue growth for correlation analysis
    portfolio_revenue_growth = []
    economic_years = []
    
    # Calculate portfolio-level revenue growth by year
    for year in sorted(economic_df['Year'].unique()) if 'Year' in economic_df.columns else []:
        year_data = financial_df[financial_df['Year'] == year]
        if not year_data.empty and 'revenue_YoY' in year_data.columns:
            valid_growth = year_data['revenue_YoY'].dropna()
            if len(valid_growth) > 0:
                portfolio_growth = valid_growth.mean()
                portfolio_revenue_growth.append(portfolio_growth)
                economic_years.append(year)
    
    if len(portfolio_revenue_growth) < 3:
        return {}
    
    # Key macro indicators for correlation analysis
    macro_indicators = {
        'Real_GDP': 'GDP Growth',
        'Industrial_Production': 'Industrial Production',
        'Unemployment_Rate': 'Unemployment Rate',
        'CPI_All_Items': 'Inflation (CPI)',
        'Treasury_10Y': '10-Year Treasury',
        'S&P_500_Index': 'S&P 500 Index'
    }
    
    for indicator, label in macro_indicators.items():
        if indicator in economic_df.columns:
            # Align macro data with portfolio years
            macro_values = []
            for year in economic_years:
                year_macro = economic_df[economic_df['Year'] == year][indicator]
                if not year_macro.empty:
                    macro_values.append(year_macro.iloc[0])
            
            if len(macro_values) == len(portfolio_revenue_growth) and len(macro_values) >= 3:
                # Calculate correlation
                correlation = np.corrcoef(portfolio_revenue_growth, macro_values)[0, 1]
                
                # Statistical significance (simplified t-test)
                n = len(macro_values)
                if abs(correlation) < 0.99:
                    t_stat = correlation * np.sqrt((n-2)/(1-correlation**2))
                else:
                    t_stat = 999
                
                if abs(t_stat) > 2.5:
                    significance = 'Significant'
                elif abs(t_stat) > 1.5:
                    significance = 'Moderate'
                else:
                    significance = 'Weak'
                
                # Impact direction
                if correlation > 0.3:
                    impact_direction = 'Positive'
                elif correlation < -0.3:
                    impact_direction = 'Negative'
                else:
                    impact_direction = 'Neutral'
                
                # Sensitivity assessment
                if abs(correlation) > 0.7:
                    sensitivity = 'High'
                elif abs(correlation) > 0.4:
                    sensitivity = 'Moderate'
                else:
                    sensitivity = 'Low'
                
                # Strategic implication
                if abs(correlation) > 0.6 and significance == 'Significant':
                    implication = 'Key driver requiring active monitoring'
                elif abs(correlation) > 0.4:
                    implication = 'Material factor for portfolio performance'
                else:
                    implication = 'Minor influence on portfolio dynamics'
                
                correlations[label] = {
                    'correlation': correlation,
                    'significance': significance,
                    'impact_direction': impact_direction,
                    'sensitivity': sensitivity,
                    'implication': implication
                }
    
    return correlations


def _create_sector_macro_correlation_table(analysis: Dict) -> pd.DataFrame:
    """Create sector-macro correlation table"""
    
    rows = []
    for driver, data in analysis.items():
        rows.append({
            'Economic Driver': driver,
            'Correlation': f"{data['correlation']:.3f}",
            'Significance': data['significance'],
            'Impact Direction': data['impact_direction'],
            'Sector Sensitivity': data['sensitivity'],
            'Strategic Implication': data['implication']
        })
    
    return pd.DataFrame(rows)


def _generate_sector_macro_summary(analysis: Dict, num_companies: int) -> str:
    """Generate sector-macro correlation summary"""
    
    if not analysis:
        return "<p>Insufficient data for sector-macro correlation analysis.</p>"
    
    # Count significant correlations
    significant_correlations = sum(1 for data in analysis.values() if data['significance'] == 'Significant')
    high_sensitivity = sum(1 for data in analysis.values() if data['sensitivity'] == 'High')
    total_indicators = len(analysis)
    
    # Find strongest correlations
    correlations_list = [(driver, data['correlation']) for driver, data in analysis.items()]
    correlations_list.sort(key=lambda x: abs(x[1]), reverse=True)
    
    strongest_driver = correlations_list[0][0] if correlations_list else 'N/A'
    strongest_corr = correlations_list[0][1] if correlations_list else 0
    
    return f"""
        <h4>Sector-Specific Macroeconomic Correlation Analysis</h4>
        <ul>
            <li><strong>Correlation Strength:</strong> {significant_correlations}/{total_indicators} indicators showing significant correlations with portfolio revenue growth</li>
            <li><strong>Economic Sensitivity:</strong> {high_sensitivity}/{total_indicators} indicators demonstrating high sensitivity to portfolio performance</li>
            <li><strong>Strongest Relationship:</strong> {strongest_driver} with {strongest_corr:+.3f} correlation coefficient</li>
            <li><strong>Portfolio Companies:</strong> {num_companies} companies {'highly' if significant_correlations >= total_indicators * 0.5 else 'moderately' if significant_correlations >= total_indicators * 0.3 else 'minimally'} correlated with macroeconomic factors</li>
            <li><strong>Diversification Assessment:</strong> {'Limited' if high_sensitivity >= total_indicators * 0.6 else 'Moderate' if high_sensitivity >= total_indicators * 0.4 else 'Strong'} macro diversification from economic exposures</li>
            <li><strong>Monitoring Priority:</strong> {'Comprehensive macro tracking essential' if significant_correlations >= total_indicators * 0.5 else 'Selective macro monitoring sufficient'} for portfolio management</li>
        </ul>
    """


def _create_sector_macro_charts(analysis: Dict) -> str:
    """Create sector-macro correlation visualization charts"""
    
    charts_html = '<h4 style="margin-top: 30px;">Sector-Macro Correlation Visualization</h4>'
    
    if not analysis:
        return charts_html + "<p>No correlation data available for visualization.</p>"
    
    # Chart 1: Correlation Coefficients Bar Chart
    drivers = list(analysis.keys())
    correlations = [analysis[d]['correlation'] for d in drivers]
    
    colors = []
    for corr in correlations:
        if abs(corr) > 0.7:
            colors.append('#2ca02c' if corr > 0 else '#d62728')
        elif abs(corr) > 0.4:
            colors.append('#8bc34a' if corr > 0 else '#ff7043')
        else:
            colors.append('#9e9e9e')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': drivers,
            'y': correlations,
            'marker': {'color': colors},
            'text': [f'{c:+.3f}' for c in correlations],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Correlation: %{y:.3f}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Revenue Growth vs Economic Indicators',
            'xaxis': {'title': 'Economic Indicator', 'tickangle': -45},
            'yaxis': {'title': 'Correlation Coefficient', 'range': [-1, 1]},
            'hovermode': 'closest',
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(drivers) - 0.5,
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'black', 'width': 2}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(drivers) - 0.5,
                    'y0': 0.5,
                    'y1': 0.5,
                    'line': {'color': 'green', 'dash': 'dash', 'width': 1}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(drivers) - 0.5,
                    'y0': -0.5,
                    'y1': -0.5,
                    'line': {'color': 'red', 'dash': 'dash', 'width': 1}
                }
            ]
        }
    }
    
    charts_html += build_plotly_chart(fig_data, div_id="chart-correlations", height=400)
    
    # Chart 2: Sensitivity Bubble Chart
    sensitivities = [analysis[d]['sensitivity'] for d in drivers]
    significances = [analysis[d]['significance'] for d in drivers]
    
    # Convert to numeric for plotting
    sensitivity_values = []
    significance_values = []
    
    for sens, sig in zip(sensitivities, significances):
        if sens == 'High':
            sensitivity_values.append(3)
        elif sens == 'Moderate':
            sensitivity_values.append(2)
        else:
            sensitivity_values.append(1)
        
        if sig == 'Significant':
            significance_values.append(3)
        elif sig == 'Moderate':
            significance_values.append(2)
        else:
            significance_values.append(1)
    
    # Bubble sizes based on absolute correlation
    sizes = [abs(c) * 50 for c in correlations]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': sensitivity_values,
            'y': significance_values,
            'marker': {
                'size': sizes,
                'color': correlations,
                'colorscale': 'RdBu',
                'showscale': True,
                'colorbar': {'title': 'Correlation'},
                'line': {'color': 'white', 'width': 2}
            },
            'text': drivers,
            'textposition': 'top center',
            'textfont': {'size': 10},
            'hovertemplate': '<b>%{text}</b><br>Sensitivity: %{x}<br>Significance: %{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Correlation Sensitivity & Significance Matrix',
            'xaxis': {
                'title': 'Sensitivity',
                'tickvals': [1, 2, 3],
                'ticktext': ['Low', 'Moderate', 'High'],
                'range': [0.5, 3.5]
            },
            'yaxis': {
                'title': 'Statistical Significance',
                'tickvals': [1, 2, 3],
                'ticktext': ['Weak', 'Moderate', 'Significant'],
                'range': [0.5, 3.5]
            },
            'hovermode': 'closest'
        }
    }
    
    charts_html += build_plotly_chart(fig_data, div_id="chart-sensitivity-matrix", height=450)
    
    return charts_html


# =============================================================================
# SUBSECTION 8H: STRATEGIC FRAMEWORK WITH ENHANCED VISUAL DESIGN
# =============================================================================

def _build_section_8h_strategic_framework(economic_df: pd.DataFrame, df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 8H: Macroeconomic Assessment Summary & Strategic Framework"""
    
    # Generate comprehensive insights from all previous analyses
    insights = _generate_comprehensive_macro_insights(economic_df, df, companies)
    
    # Build enhanced visual content
    content_parts = []
    
    # Introduction
    content_parts.append("""
        <div class="info-section">
            <h4>Comprehensive Macroeconomic Assessment & Strategic Investment Framework</h4>
            <p>Synthesized strategic insights integrating economic environment, monetary policy, growth dynamics, 
            market risk, and sector-specific correlations. Actionable framework for portfolio positioning across 
            multiple time horizons with prioritized strategic recommendations.</p>
        </div>
    """)
    
    # Executive Dashboard Cards
    content_parts.append(_build_executive_dashboard(insights))
    
    # Strategic Framework Tabs
    content_parts.append(_build_strategic_tabs(insights))
    
    # Priority Action Cards
    content_parts.append(_build_priority_actions(insights))
    
    # Key Metrics Scorecard
    content_parts.append(_build_metrics_scorecard(insights))
    
    combined_content = '\n'.join(content_parts)
    
    return _build_collapsible_subsection(
        "8H",
        "Macroeconomic Assessment Summary & Strategic Framework",
        combined_content
    )


def _generate_comprehensive_macro_insights(economic_df: pd.DataFrame, df: pd.DataFrame, 
                                          companies: Dict[str, str]) -> Dict[str, Any]:
    """Generate comprehensive macroeconomic insights"""
    
    insights = {
        'num_companies': len(companies),
        'economic_regime': 'Mixed',
        'growth_momentum': 'Moderate',
        'inflation_regime': 'Target Range',
        'risk_level': 'Moderate',
        'policy_stance': 'Neutral',
        'immediate_actions': [],
        'medium_term_actions': [],
        'long_term_actions': []
    }
    
    # Analyze current economic regime
    if not economic_df.empty and 'Real_GDP' in economic_df.columns and 'CPI_All_Items' in economic_df.columns:
        gdp_series = economic_df['Real_GDP'].dropna()
        cpi_series = economic_df['CPI_All_Items'].dropna()
        
        if len(gdp_series) >= 3 and len(cpi_series) >= 3:
            recent_gdp = gdp_series.tail(3).mean()
            recent_cpi = cpi_series.tail(3).mean()
            
            if recent_gdp > 2.5 and recent_cpi < 3.0:
                insights['economic_regime'] = 'Goldilocks'
            elif recent_gdp > 2.5 and recent_cpi >= 3.0:
                insights['economic_regime'] = 'Overheating'
            elif recent_gdp <= 2.5 and recent_cpi < 3.0:
                insights['economic_regime'] = 'Slow Growth'
            else:
                insights['economic_regime'] = 'Stagflation Risk'
    
    # Growth momentum
    if not economic_df.empty and 'Real_GDP' in economic_df.columns:
        gdp_series = economic_df['Real_GDP'].dropna()
        if len(gdp_series) >= 3:
            recent_gdp = gdp_series.tail(3).mean()
            if recent_gdp > 3.0:
                insights['growth_momentum'] = 'Strong'
            elif recent_gdp > 2.0:
                insights['growth_momentum'] = 'Moderate'
            elif recent_gdp > 0:
                insights['growth_momentum'] = 'Weak'
            else:
                insights['growth_momentum'] = 'Contractionary'
    
    # Inflation regime
    if not economic_df.empty and 'CPI_All_Items' in economic_df.columns:
        cpi_series = economic_df['CPI_All_Items'].dropna()
        if len(cpi_series) >= 3:
            recent_cpi = cpi_series.tail(3).mean()
            if recent_cpi > 4.0:
                insights['inflation_regime'] = 'High Inflation'
            elif recent_cpi > 3.0:
                insights['inflation_regime'] = 'Elevated Inflation'
            elif recent_cpi > 2.0:
                insights['inflation_regime'] = 'Target Range'
            else:
                insights['inflation_regime'] = 'Low Inflation'
    
    # Risk level (simplified)
    if not economic_df.empty and 'VIX_Index' in economic_df.columns:
        vix_series = economic_df['VIX_Index'].dropna()
        if len(vix_series) > 0:
            current_vix = vix_series.iloc[-1]
            if current_vix > 30:
                insights['risk_level'] = 'High'
            elif current_vix > 20:
                insights['risk_level'] = 'Moderate'
            else:
                insights['risk_level'] = 'Low'
    
    # Policy stance
    if not economic_df.empty and 'Treasury_3M' in economic_df.columns:
        rates = economic_df['Treasury_3M'].dropna()
        if len(rates) > 0:
            current_rate = rates.iloc[-1]
            if current_rate > 4.0:
                insights['policy_stance'] = 'Restrictive'
            elif current_rate > 2.0:
                insights['policy_stance'] = 'Neutral'
            else:
                insights['policy_stance'] = 'Accommodative'
    
    # Generate strategic actions based on conditions
    insights['immediate_actions'] = _generate_immediate_actions(insights)
    insights['medium_term_actions'] = _generate_medium_term_actions(insights)
    insights['long_term_actions'] = _generate_long_term_actions(insights)
    
    return insights


def _generate_immediate_actions(insights: Dict) -> List[Dict[str, str]]:
    """Generate immediate strategic actions (0-6 months)"""
    
    actions = []
    
    # Based on economic regime
    if insights['economic_regime'] == 'Stagflation Risk':
        actions.append({
            'title': 'Defensive Positioning',
            'description': 'Shift toward defensive sectors and quality companies',
            'priority': 'High',
            'icon': '🛡️'
        })
    elif insights['economic_regime'] == 'Goldilocks':
        actions.append({
            'title': 'Growth Acceleration',
            'description': 'Capitalize on favorable environment with growth investments',
            'priority': 'High',
            'icon': '🚀'
        })
    
    # Based on risk level
    if insights['risk_level'] == 'High':
        actions.append({
            'title': 'Risk Management',
            'description': 'Implement hedging strategies and reduce leverage',
            'priority': 'High',
            'icon': '⚠️'
        })
    
    # Based on inflation
    if insights['inflation_regime'] in ['High Inflation', 'Elevated Inflation']:
        actions.append({
            'title': 'Inflation Protection',
            'description': 'Focus on companies with pricing power',
            'priority': 'Medium',
            'icon': '💰'
        })
    
    # Default action
    if not actions:
        actions.append({
            'title': 'Balanced Approach',
            'description': 'Maintain diversified portfolio with standard risk controls',
            'priority': 'Medium',
            'icon': '⚖️'
        })
    
    return actions


def _generate_medium_term_actions(insights: Dict) -> List[Dict[str, str]]:
    """Generate medium-term strategic actions (6-18 months)"""
    
    actions = []
    
    if insights['growth_momentum'] == 'Weak':
        actions.append({
            'title': 'Sector Rotation',
            'description': 'Rotate toward defensive and counter-cyclical sectors',
            'priority': 'Medium',
            'icon': '🔄'
        })
    
    if insights['policy_stance'] == 'Restrictive':
        actions.append({
            'title': 'Rate Sensitivity Management',
            'description': 'Reduce exposure to rate-sensitive sectors',
            'priority': 'Medium',
            'icon': '📊'
        })
    
    actions.append({
        'title': 'Portfolio Rebalancing',
        'description': 'Adjust allocations based on economic cycle positioning',
        'priority': 'Low',
        'icon': '⚙️'
    })
    
    return actions


def _generate_long_term_actions(insights: Dict) -> List[Dict[str, str]]:
    """Generate long-term strategic actions (18+ months)"""
    
    return [
        {
            'title': 'Structural Positioning',
            'description': 'Align portfolio with long-term economic trends',
            'priority': 'Medium',
            'icon': '🎯'
        },
        {
            'title': 'Risk Framework Enhancement',
            'description': 'Build resilience for various economic scenarios',
            'priority': 'Low',
            'icon': '🏗️'
        },
        {
            'title': 'Monitoring & Adaptation',
            'description': 'Continuous assessment and strategy refinement',
            'priority': 'Low',
            'icon': '🔍'
        }
    ]


def _build_executive_dashboard(insights: Dict) -> str:
    """Build executive dashboard with key metrics cards"""
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>📊 Executive Macro Dashboard</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Economic Regime</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{insights['economic_regime']}</div>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Growth Momentum</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{insights['growth_momentum']}</div>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Inflation Regime</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{insights['inflation_regime']}</div>
            </div>
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Market Risk</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{insights['risk_level']}</div>
            </div>
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Policy Stance</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{insights['policy_stance']}</div>
            </div>
            <div style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Portfolio Companies</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{insights['num_companies']}</div>
            </div>
        </div>
    </div>
    """


def _build_strategic_tabs(insights: Dict) -> str:
    """Build tabbed strategic sections"""
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>🎯 Strategic Investment Framework</h4>
        <div class="tabs-container">
            <div class="tabs-header">
                <button class="tab-button active" onclick="switchTab(event, 'immediate')">Immediate (0-6M)</button>
                <button class="tab-button" onclick="switchTab(event, 'medium')">Medium-Term (6-18M)</button>
                <button class="tab-button" onclick="switchTab(event, 'longterm')">Long-Term (18M+)</button>
            </div>
            
            <div id="immediate" class="tab-content active">
                <h5>Immediate Priorities (0-6 Months)</h5>
                {_build_action_cards(insights['immediate_actions'])}
            </div>
            
            <div id="medium" class="tab-content">
                <h5>Medium-Term Strategy (6-18 Months)</h5>
                {_build_action_cards(insights['medium_term_actions'])}
            </div>
            
            <div id="longterm" class="tab-content">
                <h5>Long-Term Positioning (18+ Months)</h5>
                {_build_action_cards(insights['long_term_actions'])}
            </div>
        </div>
    </div>
    
    <style>
        .tabs-container {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--shadow-sm);
        }}
        
        .tabs-header {{
            display: flex;
            gap: 10px;
            border-bottom: 2px solid var(--card-border);
            margin-bottom: 20px;
        }}
        
        .tab-button {{
            background: transparent;
            border: none;
            padding: 12px 24px;
            cursor: pointer;
            font-weight: 600;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }}
        
        .tab-button:hover {{
            color: var(--text-primary);
        }}
        
        .tab-button.active {{
            color: var(--primary-gradient-start);
            border-bottom-color: var(--primary-gradient-start);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    
    <script>
        function switchTab(event, tabId) {{
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active from all buttons
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
    """


def _build_action_cards(actions: List[Dict[str, str]]) -> str:
    """Build action cards with color coding"""
    
    cards_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 20px 0;">'
    
    for action in actions:
        priority = action['priority']
        
        if priority == 'High':
            border_color = '#ef4444'
            bg_color = 'rgba(239, 68, 68, 0.1)'
        elif priority == 'Medium':
            border_color = '#f59e0b'
            bg_color = 'rgba(245, 158, 11, 0.1)'
        else:
            border_color = '#10b981'
            bg_color = 'rgba(16, 185, 129, 0.1)'
        
        cards_html += f"""
        <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 1.8rem;">{action['icon']}</span>
                <div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary);">{action['title']}</div>
                    <div style="font-size: 0.85rem; color: {border_color}; font-weight: 600;">Priority: {priority}</div>
                </div>
            </div>
            <p style="color: var(--text-secondary); margin: 0; line-height: 1.6;">{action['description']}</p>
        </div>
        """
    
    cards_html += '</div>'
    return cards_html


def _build_priority_actions(insights: Dict) -> str:
    """Build priority action summary"""
    
    all_actions = insights['immediate_actions'] + insights['medium_term_actions']
    high_priority = [a for a in all_actions if a['priority'] == 'High']
    
    return f"""
    <div class="info-box danger" style="margin: 30px 0;">
        <h4>⚡ High Priority Actions</h4>
        <p><strong>Immediate Attention Required:</strong> {len(high_priority)} high-priority strategic actions identified</p>
        <ul>
            {''.join([f"<li><strong>{a['icon']} {a['title']}:</strong> {a['description']}</li>" for a in high_priority])}
        </ul>
    </div>
    """


def _build_metrics_scorecard(insights: Dict) -> str:
    """Build key metrics scorecard"""
    
    # Determine scores based on regimes
    scores = {
        'Economic Environment': _get_regime_score(insights['economic_regime']),
        'Growth Outlook': _get_growth_score(insights['growth_momentum']),
        'Inflation Pressure': _get_inflation_score(insights['inflation_regime']),
        'Market Risk': _get_risk_score(insights['risk_level']),
        'Policy Support': _get_policy_score(insights['policy_stance'])
    }
    
    avg_score = sum(scores.values()) / len(scores)
    
    scorecard_html = f"""
    <div style="margin: 30px 0;">
        <h4>📈 Macroeconomic Environment Scorecard</h4>
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; box-shadow: var(--shadow-sm);">
            <div style="display: grid; grid-template-columns: 2fr 1fr 3fr; gap: 15px; align-items: center; margin-bottom: 15px;">
                <div style="font-weight: 700; color: var(--text-primary);">Category</div>
                <div style="font-weight: 700; color: var(--text-primary); text-align: center;">Score</div>
                <div style="font-weight: 700; color: var(--text-primary);">Assessment</div>
            </div>
    """
    
    for category, score in scores.items():
        bar_color = '#2ca02c' if score >= 7 else '#f59e0b' if score >= 4 else '#ef4444'
        assessment = 'Favorable' if score >= 7 else 'Neutral' if score >= 4 else 'Challenging'
        
        scorecard_html += f"""
        <div style="display: grid; grid-template-columns: 2fr 1fr 3fr; gap: 15px; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--card-border);">
            <div style="color: var(--text-primary);">{category}</div>
            <div style="text-align: center; font-weight: 700; font-size: 1.2rem; color: {bar_color};">{score}/10</div>
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 1; background: rgba(0,0,0,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="width: {score*10}%; background: {bar_color}; height: 100%; transition: width 0.5s ease;"></div>
                    </div>
                    <span style="color: {bar_color}; font-weight: 600; font-size: 0.9rem;">{assessment}</span>
                </div>
            </div>
        </div>
        """
    
    overall_color = '#2ca02c' if avg_score >= 7 else '#f59e0b' if avg_score >= 4 else '#ef4444'
    overall_assessment = 'Strong' if avg_score >= 7 else 'Mixed' if avg_score >= 4 else 'Weak'
    
    scorecard_html += f"""
        <div style="margin-top: 20px; padding: 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 1.2rem; color: var(--text-primary);">Overall Macro Environment</span>
                <div style="text-align: right;">
                    <div style="font-size: 2rem; font-weight: 900; color: {overall_color};">{avg_score:.1f}/10</div>
                    <div style="color: {overall_color}; font-weight: 600;">{overall_assessment}</div>
                </div>
            </div>
        </div>
    </div>
    </div>
    """
    
    return scorecard_html


def _get_regime_score(regime: str) -> int:
    """Get score for economic regime"""
    scores = {'Goldilocks': 9, 'Slow Growth': 6, 'Overheating': 5, 'Stagflation Risk': 3, 'Mixed': 5}
    return scores.get(regime, 5)


def _get_growth_score(momentum: str) -> int:
    """Get score for growth momentum"""
    scores = {'Strong': 9, 'Moderate': 6, 'Weak': 4, 'Contractionary': 2}
    return scores.get(momentum, 5)


def _get_inflation_score(regime: str) -> int:
    """Get score for inflation regime"""
    scores = {'Target Range': 8, 'Low Inflation': 6, 'Elevated Inflation': 4, 'High Inflation': 2}
    return scores.get(regime, 5)


def _get_risk_score(level: str) -> int:
    """Get score for risk level (inverted - lower risk = higher score)"""
    scores = {'Low': 9, 'Moderate': 6, 'High': 3}
    return scores.get(level, 5)


def _get_policy_score(stance: str) -> int:
    """Get score for policy stance"""
    scores = {'Accommodative': 8, 'Neutral': 6, 'Restrictive': 4}
    return scores.get(stance, 5)



# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _build_collapsible_subsection(subsection_id: str, title: str, content: str) -> str:
    """Build a collapsible subsection container"""
    
    return f"""
    <div class="subsection-container">
        <div class="subsection-header">
            <h3 class="subsection-title">{subsection_id}. {title}</h3>
            <span class="subsection-toggle">▼</span>
        </div>
        <div class="subsection-content">
            {content}
        </div>
    </div>
    """


def _get_regime_badge(regime: str) -> str:
    """Get badge HTML for economic regime"""
    
    badge_map = {
        'Goldilocks': ('success', '🟢'),
        'Overheating': ('warning', '🟡'),
        'Slow Growth': ('info', '🔵'),
        'Stagflation Risk': ('danger', '🔴')
    }
    
    badge_type, emoji = badge_map.get(regime, ('default', '⚪'))
    return f'{emoji}'


def _get_yield_curve_badge(shape: str) -> str:
    """Get badge HTML for yield curve shape"""
    
    badge_map = {
        'Steep': ('success', '📈'),
        'Normal': ('info', '➡️'),
        'Flat': ('warning', '➖'),
        'Inverted': ('danger', '📉')
    }
    
    badge_type, emoji = badge_map.get(shape, ('default', '⚪'))
    return f'{emoji}'


def _get_policy_stance_badge(stance: str) -> str:
    """Get badge HTML for monetary policy stance"""
    
    badge_map = {
        'Restrictive': ('danger', '🔴'),
        'Neutral': ('info', '🔵'),
        'Accommodative': ('success', '🟢')
    }
    
    badge_type, emoji = badge_map.get(stance, ('default', '⚪'))
    return f'{emoji}'