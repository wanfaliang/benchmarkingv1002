"""Section 16: Benchmark Relative Analysis"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_card,
    build_stat_grid,
    build_info_box,
    build_section_divider,
    build_data_table,
    build_plotly_chart,
    build_enhanced_table,
    format_currency,
    format_percentage,
    format_number,
    build_badge,
    build_colored_cell
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 16: Benchmark Relative Analysis
    
    Comprehensive S&P 500 relative analysis with:
    - Dynamic beta and correlation analysis
    - Relative performance intelligence
    - Market regime analysis
    - Enhanced technical analysis
    - Risk management insights
    - Portfolio construction guidance
    """
    
    try:
        companies = collector.companies
        
        # Get price data
        daily_prices = collector.get_prices_daily()
        monthly_prices = collector.get_prices_monthly()
        
        # Extract S&P 500 data
        sp500_daily = daily_prices[daily_prices["symbol"] == "^GSPC"].copy()
        sp500_monthly = monthly_prices[monthly_prices["symbol"] == "^GSPC"].copy()
        
        if sp500_daily.empty:
            sp500_daily = _simulate_benchmark_data(daily_prices)
            sp500_monthly = _simulate_benchmark_data(monthly_prices)
        
        # Build all subsections
        section_16a_html = _build_section_16a_beta_analysis(
            daily_prices, sp500_daily, companies
        )
        
        section_16b_html = _build_section_16b_performance_analysis(
            daily_prices, monthly_prices, sp500_daily, sp500_monthly, companies
        )
        
        section_16c_html = _build_section_16c_regime_analysis(
            daily_prices, sp500_daily, companies
        )
        
        section_16d_html = _build_section_16d_technical_analysis(
            daily_prices, sp500_daily, companies
        )
        
        section_16e_html = _build_section_16e_risk_management(
            daily_prices, sp500_daily, companies
        )
        
        section_16f_html = _build_section_16f_portfolio_insights(
            daily_prices, sp500_daily, companies
        )
        
        section_16g_html = _build_section_16g_dashboard(
            daily_prices, sp500_daily, companies
        )
        
        section_16h_html = _build_section_16h_strategic_framework(
            daily_prices, sp500_daily, companies
        )
        
        # Combine all subsections
        content = f"""
        <div class="section-content-wrapper">
            {section_16a_html}
            {build_section_divider() if section_16b_html else ""}
            {section_16b_html}
            {build_section_divider() if section_16c_html else ""}
            {section_16c_html}
            {build_section_divider() if section_16d_html else ""}
            {section_16d_html}
            {build_section_divider() if section_16e_html else ""}
            {section_16e_html}
            {build_section_divider() if section_16f_html else ""}
            {section_16f_html}
            {build_section_divider() if section_16g_html else ""}
            {section_16g_html}
            {build_section_divider() if section_16h_html else ""}
            {section_16h_html}
        </div>
        """
        
        return generate_section_wrapper(16, "Benchmark Relative Analysis", content)
        
    except Exception as e:
        error_content = f"""
        <div class="section-content-wrapper">
            {build_info_box(f"<p>Error generating Section 16: {str(e)}</p>", "danger", "Generation Error")}
        </div>
        """
        return generate_section_wrapper(16, "Benchmark Relative Analysis", error_content)


# =============================================================================
# SECTION 16A: BETA AND CORRELATION ANALYSIS
# =============================================================================

def _build_section_16a_beta_analysis(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                     companies: Dict[str, str]) -> str:
    """Build Section 16A: Enhanced Beta and Correlation Analysis"""
    
    # Calculate beta metrics
    beta_analysis = _calculate_enhanced_beta_metrics(daily_prices, sp500_daily, companies)
    
    if not beta_analysis:
        return build_info_box("<p>Insufficient data for beta analysis.</p>", "warning", "16A. Beta Analysis")
    
    # Create collapsible section
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16a')">
            <h2>16A. Enhanced Beta and Correlation Analysis</h2>
            <span class="toggle-icon" id="section16a-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16a-content">
    """
    
    # Overview cards
    avg_beta = np.mean([a['current_beta'] for a in beta_analysis.values()])
    avg_correlation = np.mean([a['correlation_full'] for a in beta_analysis.values()])
    high_beta_count = sum(1 for a in beta_analysis.values() if a['current_beta'] > 1.2)
    defensive_count = sum(1 for a in beta_analysis.values() if a['down_beta'] < a['up_beta'])
    
    cards = [
        {
            "label": "Portfolio Average Beta",
            "value": f"{avg_beta:.2f}",
            "description": f"{'Above' if avg_beta > 1.0 else 'Below'} market sensitivity",
            "type": "info" if 0.8 <= avg_beta <= 1.2 else "warning"
        },
        {
            "label": "Average Correlation",
            "value": f"{avg_correlation:.2f}",
            "description": f"{'High' if avg_correlation > 0.7 else 'Moderate'} market correlation",
            "type": "default"
        },
        {
            "label": "High Beta Positions",
            "value": f"{high_beta_count}/{len(beta_analysis)}",
            "description": "Companies with beta > 1.2",
            "type": "warning" if high_beta_count > len(beta_analysis) * 0.6 else "success"
        },
        {
            "label": "Defensive Characteristics",
            "value": f"{defensive_count}/{len(beta_analysis)}",
            "description": "Lower downside vs upside beta",
            "type": "success"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Beta comparison table
    html += "<h3>Beta Metrics by Company</h3>"
    beta_df = _create_beta_dataframe(beta_analysis)
    html += build_data_table(beta_df, "beta-table-16a", sortable=True)
    
    # Chart 1: Current Beta Comparison
    html += _create_beta_comparison_chart(beta_analysis)
    
    # Chart 2: Up vs Down Beta (Asymmetric Beta)
    html += _create_asymmetric_beta_chart(beta_analysis)
    
    # Chart 3: Beta vs Correlation Scatter
    html += _create_beta_correlation_scatter(beta_analysis)
    
    # Chart 4: Beta Stability Metrics
    html += _create_beta_stability_chart(beta_analysis)
    
    # Summary insights
    insights = _generate_beta_insights(beta_analysis, avg_beta, avg_correlation, high_beta_count, defensive_count)
    html += build_info_box(insights, "info", "Beta Analysis Insights")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _calculate_enhanced_beta_metrics(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                     companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate comprehensive beta metrics across multiple timeframes"""
    
    beta_analysis = {}
    
    # Calculate S&P 500 returns
    sp500_returns = sp500_daily.set_index('date')['close'].pct_change().dropna()
    
    for company_name, ticker in companies.items():
        company_prices = daily_prices[daily_prices['Symbol'] == ticker].copy()
        
        if len(company_prices) < 60:
            continue
        
        company_returns = company_prices.set_index('date')['close'].pct_change().dropna()
        
        # Align returns
        aligned_data = pd.DataFrame({
            'company': company_returns,
            'market': sp500_returns
        }).dropna()
        
        if len(aligned_data) < 60:
            continue
        
        # Calculate betas for different periods
        betas = {}
        
        for window, label in [(60, '60-day'), (120, '120-day'), (252, '252-day')]:
            if len(aligned_data) >= window:
                rolling_cov = aligned_data['company'].rolling(window).cov(aligned_data['market'])
                rolling_var = aligned_data['market'].rolling(window).var()
                rolling_beta = rolling_cov / rolling_var
                
                betas[label] = {
                    'current': rolling_beta.iloc[-1] if not rolling_beta.empty else 1.0,
                    'mean': rolling_beta.mean(),
                    'std': rolling_beta.std(),
                    'min': rolling_beta.min(),
                    'max': rolling_beta.max()
                }
        
        # Calculate correlation metrics
        correlation_60d = aligned_data.tail(60)['company'].corr(aligned_data.tail(60)['market']) if len(aligned_data) >= 60 else 0
        correlation_full = aligned_data['company'].corr(aligned_data['market'])
        
        # Up/down market betas
        up_market = aligned_data[aligned_data['market'] > 0]
        down_market = aligned_data[aligned_data['market'] < 0]
        
        up_beta = _calculate_simple_beta(up_market) if len(up_market) > 20 else 1.0
        down_beta = _calculate_simple_beta(down_market) if len(down_market) > 20 else 1.0
        
        # Beta stability metrics (raw, not scored)
        if '252-day' in betas:
            beta_std = betas['252-day']['std']
            beta_mean = betas['252-day']['mean']
            beta_cv = beta_std / abs(beta_mean) if beta_mean != 0 else 0
            beta_range = betas['252-day']['max'] - betas['252-day']['min']
        else:
            beta_std = 0
            beta_cv = 0
            beta_range = 0
        
        beta_analysis[company_name] = {
            'betas': betas,
            'current_beta': betas.get('252-day', betas.get('120-day', betas.get('60-day', {})))['current'] if betas else 1.0,
            'correlation_60d': correlation_60d,
            'correlation_full': correlation_full,
            'up_beta': up_beta,
            'down_beta': down_beta,
            'beta_std': beta_std,
            'beta_cv': beta_cv,
            'beta_range': beta_range,
            'beta_trend': 'Increasing' if len(betas) > 0 and list(betas.values())[0]['current'] > list(betas.values())[-1]['mean'] else 'Decreasing'
        }
    
    return beta_analysis


def _calculate_simple_beta(aligned_data: pd.DataFrame) -> float:
    """Calculate simple beta from aligned returns data"""
    if aligned_data.empty or len(aligned_data) < 2:
        return 1.0
    
    try:
        cov = aligned_data['company'].cov(aligned_data['market'])
        var = aligned_data['market'].var()
        return cov / var if var > 0 else 1.0
    except:
        return 1.0


def _create_beta_dataframe(beta_analysis: Dict) -> pd.DataFrame:
    """Create DataFrame for beta table"""
    
    rows = []
    for company_name, analysis in beta_analysis.items():
        row = {
            'Company': company_name,
            'Current Beta': f"{analysis['current_beta']:.3f}",
            'Up Beta': f"{analysis['up_beta']:.3f}",
            'Down Beta': f"{analysis['down_beta']:.3f}",
            'Correlation': f"{analysis['correlation_full']:.3f}",
            'Beta Std Dev': f"{analysis['beta_std']:.3f}",
            'Beta CV': f"{analysis['beta_cv']:.2%}",
            'Beta Range': f"{analysis['beta_range']:.3f}",
            'Trend': analysis['beta_trend']
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_beta_comparison_chart(beta_analysis: Dict) -> str:
    """Create beta comparison bar chart"""
    
    companies = list(beta_analysis.keys())
    betas = [analysis['current_beta'] for analysis in beta_analysis.values()]
    
    # Color based on beta level
    colors = ['#ef4444' if b > 1.2 else '#10b981' if b < 0.8 else '#3b82f6' for b in betas]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': betas,
            'marker': {'color': colors},
            'text': [f'{b:.2f}' for b in betas],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Beta: %{y:.3f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Current Beta vs S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Beta'},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 1.0,
                'y1': 1.0,
                'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
            }],
            'annotations': [{
                'x': len(companies) - 1,
                'y': 1.0,
                'text': 'Market Beta = 1.0',
                'showarrow': False,
                'yshift': 10,
                'font': {'color': 'red'}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, "beta-comparison-chart", 500)


def _create_asymmetric_beta_chart(beta_analysis: Dict) -> str:
    """Create up vs down beta comparison chart"""
    
    companies = list(beta_analysis.keys())
    up_betas = [analysis['up_beta'] for analysis in beta_analysis.values()]
    down_betas = [analysis['down_beta'] for analysis in beta_analysis.values()]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Up Market Beta',
                'x': companies,
                'y': up_betas,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Up Beta: %{y:.3f}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Down Market Beta',
                'x': companies,
                'y': down_betas,
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{x}</b><br>Down Beta: %{y:.3f}<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Asymmetric Beta Analysis: Up vs Down Markets', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Beta'},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, "asymmetric-beta-chart", 500)


def _create_beta_correlation_scatter(beta_analysis: Dict) -> str:
    """Create beta vs correlation scatter plot"""
    
    companies = list(beta_analysis.keys())
    betas = [analysis['current_beta'] for analysis in beta_analysis.values()]
    correlations = [analysis['correlation_full'] for analysis in beta_analysis.values()]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': betas,
            'y': correlations,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': betas,
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Beta'}
            },
            'hovertemplate': '<b>%{text}</b><br>Beta: %{x:.3f}<br>Correlation: %{y:.3f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Beta vs Correlation with S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Beta', 'zeroline': False},
            'yaxis': {'title': 'Correlation', 'zeroline': False},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, "beta-correlation-scatter", 500)


def _create_beta_stability_chart(beta_analysis: Dict) -> str:
    """Create beta stability metrics chart"""
    
    companies = list(beta_analysis.keys())
    beta_stds = [analysis['beta_std'] for analysis in beta_analysis.values()]
    beta_cvs = [analysis['beta_cv'] * 100 for analysis in beta_analysis.values()]  # Convert to percentage
    beta_ranges = [analysis['beta_range'] for analysis in beta_analysis.values()]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Std Dev',
                'x': companies,
                'y': beta_stds,
                'marker': {'color': '#3b82f6'},
                'yaxis': 'y',
                'hovertemplate': '<b>%{x}</b><br>Std Dev: %{y:.3f}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Coefficient of Variation (%)',
                'x': companies,
                'y': beta_cvs,
                'marker': {'color': '#f59e0b'},
                'yaxis': 'y2',
                'hovertemplate': '<b>%{x}</b><br>CV: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Beta Stability Metrics', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Std Dev', 'side': 'left'},
            'yaxis2': {'title': 'Coefficient of Variation (%)', 'side': 'right', 'overlaying': 'y'},
            'barmode': 'group',
            'hovermode': 'x unified',
            'legend': {'x': 0.01, 'y': 0.99}
        }
    }
    
    return build_plotly_chart(fig_data, "beta-stability-chart", 500)


def _generate_beta_insights(beta_analysis: Dict, avg_beta: float, avg_correlation: float,
                            high_beta_count: int, defensive_count: int) -> str:
    """Generate beta analysis insights"""
    
    total = len(beta_analysis)
    
    positioning = "aggressive" if avg_beta > 1.1 else "defensive" if avg_beta < 0.9 else "market-neutral"
    correlation_level = "high" if avg_correlation > 0.7 else "moderate" if avg_correlation > 0.5 else "low"
    
    insights = f"""
    <h4>Key Beta Insights:</h4>
    <ul>
        <li><strong>Portfolio Positioning:</strong> With an average beta of {avg_beta:.2f}, the portfolio exhibits 
        {positioning} characteristics relative to the S&P 500.</li>
        
        <li><strong>Market Sensitivity:</strong> Average correlation of {avg_correlation:.2f} indicates {correlation_level} 
        market sensitivity, {'suggesting limited diversification benefits' if correlation_level == 'high' else 'providing meaningful diversification potential'}.</li>
        
        <li><strong>Growth Exposure:</strong> {high_beta_count}/{total} companies have beta > 1.2, 
        {'concentrating' if high_beta_count > total * 0.5 else 'providing balanced'} growth exposure.</li>
        
        <li><strong>Downside Protection:</strong> {defensive_count}/{total} companies exhibit asymmetric beta profiles 
        (lower downside beta), {'offering strong' if defensive_count > total * 0.5 else 'providing moderate'} defensive characteristics.</li>
        
        <li><strong>Stability Assessment:</strong> Review the Coefficient of Variation (CV) - lower values indicate more stable beta relationships. 
        Companies with CV < 20% demonstrate consistent market sensitivity.</li>
    </ul>
    """
    
    return insights


# =============================================================================
# SECTION 16B: RELATIVE PERFORMANCE ANALYSIS
# =============================================================================

def _build_section_16b_performance_analysis(daily_prices: pd.DataFrame, monthly_prices: pd.DataFrame,
                                           sp500_daily: pd.DataFrame, sp500_monthly: pd.DataFrame,
                                           companies: Dict[str, str]) -> str:
    """Build Section 16B: Relative Performance Intelligence"""
    
    # Calculate performance metrics
    performance_analysis = _calculate_performance_metrics(
        daily_prices, monthly_prices, sp500_daily, sp500_monthly, companies
    )
    
    if not performance_analysis:
        return build_info_box("<p>Insufficient data for performance analysis.</p>", "warning", "16B. Performance Analysis")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16b')">
            <h2>16B. Relative Performance Intelligence</h2>
            <span class="toggle-icon" id="section16b-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16b-content">
    """
    
    # Overview cards
    avg_alpha = np.mean([a['alpha'] for a in performance_analysis.values()]) * 100
    positive_alpha = sum(1 for a in performance_analysis.values() if a['alpha'] > 0)
    avg_info_ratio = np.mean([a['information_ratio'] for a in performance_analysis.values()])
    avg_tracking_error = np.mean([a['tracking_error'] for a in performance_analysis.values()]) * 100
    
    cards = [
        {
            "label": "Average Alpha",
            "value": f"{avg_alpha:+.1f}%",
            "description": "Excess return vs S&P 500",
            "type": "success" if avg_alpha > 0 else "danger"
        },
        {
            "label": "Positive Alpha Count",
            "value": f"{positive_alpha}/{len(performance_analysis)}",
            "description": "Companies outperforming",
            "type": "success" if positive_alpha > len(performance_analysis) * 0.5 else "warning"
        },
        {
            "label": "Avg Information Ratio",
            "value": f"{avg_info_ratio:.2f}",
            "description": "Risk-adjusted outperformance",
            "type": "success" if avg_info_ratio > 0.5 else "info" if avg_info_ratio > 0 else "danger"
        },
        {
            "label": "Avg Tracking Error",
            "value": f"{avg_tracking_error:.1f}%",
            "description": "Active positioning level",
            "type": "info"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Performance table
    html += "<h3>Performance Metrics by Company</h3>"
    perf_df = _create_performance_dataframe(performance_analysis)
    html += build_enhanced_table(
        perf_df, 
        "performance-table-16b",
        color_columns={
            'Performance Tier': lambda x: 'excellent' if x == 'Top Tier' else 'good' if x == 'Above Average' else 'fair'
        },
        sortable=True
    )
    
    # Chart 1: Alpha Generation
    html += _create_alpha_chart(performance_analysis)
    
    # Chart 2: Information Ratio vs Tracking Error
    html += _create_info_ratio_scatter(performance_analysis)
    
    # Chart 3: Period Performance Comparison
    html += _create_period_performance_chart(performance_analysis)
    
    # Chart 4: Relative Strength
    html += _create_relative_strength_chart(performance_analysis)
    
    # Summary insights
    insights = _generate_performance_insights(performance_analysis, avg_alpha, positive_alpha, avg_info_ratio)
    html += build_info_box(insights, "info", "Performance Analysis Insights")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _calculate_performance_metrics(daily_prices: pd.DataFrame, monthly_prices: pd.DataFrame,
                                   sp500_daily: pd.DataFrame, sp500_monthly: pd.DataFrame,
                                   companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate relative performance metrics vs S&P 500"""
    
    performance_analysis = {}
    
    # Calculate S&P 500 performance metrics
    sp500_returns_daily = sp500_daily.set_index('date')['close'].pct_change().dropna()
    sp500_returns_monthly = sp500_monthly.set_index('date')['close'].pct_change().dropna()
    
    sp500_annual_return = (1 + sp500_returns_monthly).prod() ** (12 / len(sp500_returns_monthly)) - 1 if len(sp500_returns_monthly) > 0 else 0
    sp500_volatility = sp500_returns_daily.std() * np.sqrt(252)
    
    for company_name, ticker in companies.items():
        company_daily = daily_prices[daily_prices['Symbol'] == ticker].copy()
        company_monthly = monthly_prices[monthly_prices['Symbol'] == ticker].copy()
        
        if len(company_daily) < 60:
            continue
        
        # Calculate returns
        company_returns_daily = company_daily.set_index('date')['close'].pct_change().dropna()
        company_returns_monthly = company_monthly.set_index('date')['close'].pct_change().dropna()
        
        # Annual return
        company_annual_return = (1 + company_returns_monthly).prod() ** (12 / len(company_returns_monthly)) - 1 if len(company_returns_monthly) > 0 else 0
        
        # Alpha calculation
        alpha = company_annual_return - sp500_annual_return
        
        # Tracking error
        aligned_returns = pd.DataFrame({
            'company': company_returns_daily,
            'market': sp500_returns_daily
        }).dropna()
        
        if not aligned_returns.empty:
            tracking_error = (aligned_returns['company'] - aligned_returns['market']).std() * np.sqrt(252)
            information_ratio = alpha / tracking_error if tracking_error > 0 else 0
        else:
            tracking_error = 0
            information_ratio = 0
        
        # Relative strength
        if len(company_daily) > 0 and len(sp500_daily) > 0:
            company_total_return = (company_daily['close'].iloc[-1] / company_daily['close'].iloc[0]) - 1
            sp500_total_return = (sp500_daily['close'].iloc[-1] / sp500_daily['close'].iloc[0]) - 1
            relative_strength = ((1 + company_total_return) / (1 + sp500_total_return)) - 1
        else:
            relative_strength = 0
        
        # Performance periods
        periods = {}
        for days, label in [(20, '1M'), (60, '3M'), (252, '1Y')]:
            if len(company_daily) >= days and len(sp500_daily) >= days:
                company_period_return = (company_daily['close'].iloc[-1] / company_daily['close'].iloc[-days]) - 1
                sp500_period_return = (sp500_daily['close'].iloc[-1] / sp500_daily['close'].iloc[-days]) - 1
                periods[label] = {
                    'company_return': company_period_return,
                    'sp500_return': sp500_period_return,
                    'excess_return': company_period_return - sp500_period_return
                }
        
        performance_analysis[company_name] = {
            'annual_return': company_annual_return,
            'sp500_annual_return': sp500_annual_return,
            'alpha': alpha,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'relative_strength': relative_strength,
            'period_performance': periods
        }
    
    # Calculate performance tiers using percentiles
    all_alphas = [a['alpha'] for a in performance_analysis.values()]
    all_irs = [a['information_ratio'] for a in performance_analysis.values()]
    all_rs = [a['relative_strength'] for a in performance_analysis.values()]
    
    for company_name, analysis in performance_analysis.items():
        alpha_pct = stats.percentileofscore(all_alphas, analysis['alpha'])
        ir_pct = stats.percentileofscore(all_irs, analysis['information_ratio'])
        rs_pct = stats.percentileofscore(all_rs, analysis['relative_strength'])
        
        # Weighted score (IR most important)
        weighted_score = alpha_pct * 0.3 + ir_pct * 0.5 + rs_pct * 0.2
        
        if weighted_score >= 66:
            analysis['performance_tier'] = 'Top Tier'
        elif weighted_score >= 33:
            analysis['performance_tier'] = 'Above Average'
        else:
            analysis['performance_tier'] = 'Below Average'
    
    return performance_analysis


def _create_performance_dataframe(performance_analysis: Dict) -> pd.DataFrame:
    """Create DataFrame for performance table"""
    
    rows = []
    for company_name, analysis in performance_analysis.items():
        row = {
            'Company': company_name,
            'Annual Return': f"{analysis['annual_return']*100:.1f}%",
            'S&P 500 Return': f"{analysis['sp500_annual_return']*100:.1f}%",
            'Alpha': f"{analysis['alpha']*100:+.1f}%",
            'Tracking Error': f"{analysis['tracking_error']*100:.1f}%",
            'Information Ratio': f"{analysis['information_ratio']:.2f}",
            'Relative Strength': f"{analysis['relative_strength']*100:+.1f}%",
            'Performance Tier': analysis['performance_tier']
        }
        
        # Add period performance if available
        if '1Y' in analysis['period_performance']:
            row['1Y Excess'] = f"{analysis['period_performance']['1Y']['excess_return']*100:+.1f}%"
        
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_alpha_chart(performance_analysis: Dict) -> str:
    """Create alpha generation bar chart"""
    
    companies = list(performance_analysis.keys())
    alphas = [analysis['alpha'] * 100 for analysis in performance_analysis.values()]
    
    colors = ['#10b981' if a > 0 else '#ef4444' for a in alphas]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': alphas,
            'marker': {'color': colors},
            'text': [f'{a:+.1f}%' for a in alphas],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Alpha: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Alpha Generation vs S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Alpha (%)', 'zeroline': True, 'zerolinewidth': 2, 'zerolinecolor': 'black'},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, "alpha-chart", 500)


def _create_info_ratio_scatter(performance_analysis: Dict) -> str:
    """Create information ratio vs tracking error scatter plot"""
    
    companies = list(performance_analysis.keys())
    tracking_errors = [analysis['tracking_error'] * 100 for analysis in performance_analysis.values()]
    info_ratios = [analysis['information_ratio'] for analysis in performance_analysis.values()]
    alphas = [analysis['alpha'] * 100 for analysis in performance_analysis.values()]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': tracking_errors,
            'y': info_ratios,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': alphas,
                'colorscale': [[0, '#ef4444'], [0.5, '#f59e0b'], [1, '#10b981']],
                'showscale': True,
                'colorbar': {'title': 'Alpha (%)'}
            },
            'hovertemplate': '<b>%{text}</b><br>Tracking Error: %{x:.1f}%<br>Info Ratio: %{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Risk-Adjusted Outperformance: Information Ratio vs Tracking Error', 
                     'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Tracking Error (%)', 'zeroline': False},
            'yaxis': {'title': 'Information Ratio', 'zeroline': True, 'zerolinewidth': 1},
            'shapes': [
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': max(tracking_errors) * 1.1,
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'black', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': max(tracking_errors) * 1.1,
                    'y0': 0.5,
                    'y1': 0.5,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {
                    'x': max(tracking_errors) * 0.9,
                    'y': 0.5,
                    'text': 'Good IR (0.5)',
                    'showarrow': False,
                    'yshift': 10,
                    'font': {'color': 'green', 'size': 10}
                }
            ],
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, "info-ratio-scatter", 500)


def _create_period_performance_chart(performance_analysis: Dict) -> str:
    """Create period performance comparison chart"""
    
    companies = list(performance_analysis.keys())
    periods = ['1M', '3M', '1Y']
    
    traces = []
    colors_map = {'1M': '#3b82f6', '3M': '#8b5cf6', '1Y': '#ec4899'}
    
    for period in periods:
        excess_returns = []
        for company_name in companies:
            if period in performance_analysis[company_name]['period_performance']:
                excess_returns.append(
                    performance_analysis[company_name]['period_performance'][period]['excess_return'] * 100
                )
            else:
                excess_returns.append(0)
        
        traces.append({
            'type': 'bar',
            'name': f'{period} Excess Return',
            'x': companies,
            'y': excess_returns,
            'marker': {'color': colors_map[period]},
            'hovertemplate': f'<b>%{{x}}</b><br>{period} Excess: %{{y:+.1f}}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Period Excess Returns vs S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Excess Return (%)', 'zeroline': True, 'zerolinewidth': 2},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, "period-performance-chart", 500)


def _create_relative_strength_chart(performance_analysis: Dict) -> str:
    """Create relative strength bar chart"""
    
    companies = list(performance_analysis.keys())
    rel_strengths = [analysis['relative_strength'] * 100 for analysis in performance_analysis.values()]
    
    colors = [
        '#10b981' if rs > 5 else '#ef4444' if rs < -5 else '#f59e0b'
        for rs in rel_strengths
    ]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': rel_strengths,
            'marker': {'color': colors},
            'text': [f'{rs:+.1f}%' for rs in rel_strengths],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Relative Strength: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Cumulative Relative Strength vs S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Relative Strength (%)', 'zeroline': True, 'zerolinewidth': 2},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, "relative-strength-chart", 500)


def _generate_performance_insights(performance_analysis: Dict, avg_alpha: float,
                                   positive_alpha: int, avg_info_ratio: float) -> str:
    """Generate performance analysis insights"""
    
    total = len(performance_analysis)
    
    insights = f"""
    <h4>Key Performance Insights:</h4>
    <ul>
        <li><strong>Alpha Generation:</strong> Portfolio generates {avg_alpha:+.1f}% average alpha with 
        {positive_alpha}/{total} companies outperforming the S&P 500, indicating 
        {'strong' if positive_alpha > total * 0.6 else 'mixed'} stock selection.</li>
        
        <li><strong>Risk-Adjusted Performance:</strong> Average information ratio of {avg_info_ratio:.2f} suggests 
        {'excellent' if avg_info_ratio > 0.5 else 'good' if avg_info_ratio > 0.3 else 'moderate' if avg_info_ratio > 0 else 'poor'} 
        risk-adjusted outperformance.</li>
        
        <li><strong>Consistency:</strong> Companies in the "Top Tier" demonstrate both positive alpha and high information ratios, 
        representing the best risk-adjusted performers in the portfolio.</li>
        
        <li><strong>Active Management Value:</strong> 
        {'High tracking errors with positive information ratios validate active management approach' if avg_info_ratio > 0.3 
         else 'Consider whether tracking error is justified by alpha generation'}.</li>
    </ul>
    
    <h4>Interpretation Guide:</h4>
    <ul>
        <li><strong>Alpha > 5%:</strong> Significant outperformance</li>
        <li><strong>Information Ratio > 0.5:</strong> Strong risk-adjusted returns</li>
        <li><strong>Relative Strength > 10%:</strong> Substantially outperforming market</li>
    </ul>
    """
    
    return insights


# =============================================================================
# SECTION 16C-16H: STUBBED SUBSECTIONS
# =============================================================================

"""
Section 16 - Step 2: Subsections 16C and 16D
Replace the stubbed functions in section_16.py with these implementations
"""

# =============================================================================
# SECTION 16C: MARKET REGIME ANALYSIS
# =============================================================================

def _build_section_16c_regime_analysis(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                      companies: Dict[str, str]) -> str:
    """Build Section 16C: Market Regime Analysis"""
    
    # Calculate regime metrics
    regime_analysis = _calculate_regime_metrics(daily_prices, sp500_daily, companies)
    
    if not regime_analysis:
        return build_info_box("<p>Insufficient data for regime analysis.</p>", "warning", "16C. Regime Analysis")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16c')">
            <h2>16C. Market Regime Analysis</h2>
            <span class="toggle-icon" id="section16c-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16c-content">
    """
    
    # Overview cards - Display actual defensive metrics instead of scores
    avg_downside_capture = np.mean([a['defensive_metrics']['downside_capture_ratio'] 
                                    for a in regime_analysis.values()])
    avg_bear_alpha = np.mean([a['defensive_metrics']['bear_market_alpha'] 
                              for a in regime_analysis.values()]) * 100
    low_stress_dd_count = sum(1 for a in regime_analysis.values() 
                              if a['defensive_metrics']['stress_max_drawdown'] > -0.20)
    
    cards = [
        {
            "label": "Avg Downside Capture",
            "value": f"{avg_downside_capture:.2f}",
            "description": "Lower is better (defensive)",
            "type": "success" if avg_downside_capture < 0.9 else "warning"
        },
        {
            "label": "Avg Bear Market Alpha",
            "value": f"{avg_bear_alpha:+.1f}%",
            "description": "Performance in bear markets",
            "type": "success" if avg_bear_alpha > -5 else "warning"
        },
        {
            "label": "Low Stress Drawdown",
            "value": f"{low_stress_dd_count}/{len(regime_analysis)}",
            "description": "Max DD > -20% in stress",
            "type": "success" if low_stress_dd_count > len(regime_analysis) * 0.5 else "info"
        },
        {
            "label": "Regime Count",
            "value": "4",
            "description": "Market regimes analyzed",
            "type": "info"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Defensive metrics table
    html += "<h3>Defensive Characteristics by Company</h3>"
    defensive_df = _create_defensive_metrics_dataframe(regime_analysis)
    html += build_data_table(defensive_df, "defensive-table-16c", sortable=True)
    
    # Regime performance table
    html += "<h3>Performance Across Market Regimes</h3>"
    regime_perf_df = _create_regime_performance_dataframe(regime_analysis)
    html += build_data_table(regime_perf_df, "regime-perf-table-16c", sortable=True)
    
    # Chart 1: Regime Performance Heatmap
    html += _create_regime_heatmap(regime_analysis)
    
    # Chart 2: Downside Capture Ratio
    html += _create_downside_capture_chart(regime_analysis)
    
    # Chart 3: Stress vs Normal Performance
    html += _create_stress_normal_comparison_chart(regime_analysis)
    
    # Chart 4: Maximum Drawdowns in Stress Periods
    html += _create_stress_drawdown_chart(regime_analysis)
    
    # Chart 5: Bear Market Performance
    html += _create_bear_market_performance_chart(regime_analysis)
    
    # Summary insights
    insights = _generate_regime_insights(regime_analysis, avg_downside_capture, avg_bear_alpha)
    html += build_info_box(insights, "info", "Regime Analysis Insights")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _calculate_regime_metrics(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                              companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate performance across market regimes"""
    
    regime_analysis = {}
    
    # Calculate S&P 500 metrics for regime identification
    sp500_returns = sp500_daily.set_index('date')['close'].pct_change().dropna()
    
    # Define market regimes based on volatility
    rolling_vol = sp500_returns.rolling(20).std() * np.sqrt(252)
    vol_median = rolling_vol.median()
    
    # Trend identification
    sp500_sma_50 = sp500_daily.set_index('date')['close'].rolling(50).mean()
    sp500_close = sp500_daily.set_index('date')['close']
    
    # Create regime labels
    regimes = pd.Series(index=sp500_returns.index, dtype=str)
    
    for date in sp500_returns.index:
        if date in rolling_vol.index and date in sp500_sma_50.index:
            vol = rolling_vol.loc[date]
            price = sp500_close.loc[date] if date in sp500_close.index else np.nan
            sma_50 = sp500_sma_50.loc[date]
            
            if pd.notna(vol) and pd.notna(price) and pd.notna(sma_50):
                if vol < vol_median:
                    if price > sma_50:
                        regimes.loc[date] = 'Low Vol Bull'
                    else:
                        regimes.loc[date] = 'Low Vol Bear'
                else:
                    if price > sma_50:
                        regimes.loc[date] = 'High Vol Bull'
                    else:
                        regimes.loc[date] = 'High Vol Bear'
    
    # Calculate S&P 500 regime performance for reference
    sp500_regime_perf = {}
    for regime in ['Low Vol Bull', 'Low Vol Bear', 'High Vol Bull', 'High Vol Bear']:
        regime_returns = sp500_returns[regimes == regime]
        if len(regime_returns) > 0:
            sp500_regime_perf[regime] = regime_returns.mean() * 252
    
    # Analyze company performance in each regime
    for company_name, ticker in companies.items():
        company_prices = daily_prices[daily_prices['Symbol'] == ticker].copy()
        
        if len(company_prices) < 60:
            continue
        
        company_returns = company_prices.set_index('date')['close'].pct_change().dropna()
        
        # Align with regimes
        aligned_data = pd.DataFrame({
            'returns': company_returns,
            'regime': regimes
        }).dropna()
        
        if aligned_data.empty:
            continue
        
        # Calculate regime-specific metrics
        regime_metrics = {}
        
        for regime in ['Low Vol Bull', 'Low Vol Bear', 'High Vol Bull', 'High Vol Bear']:
            regime_data = aligned_data[aligned_data['regime'] == regime]
            
            if len(regime_data) > 0:
                regime_metrics[regime] = {
                    'avg_return': regime_data['returns'].mean() * 252,
                    'volatility': regime_data['returns'].std() * np.sqrt(252),
                    'sharpe': (regime_data['returns'].mean() * 252) / (regime_data['returns'].std() * np.sqrt(252)) if regime_data['returns'].std() > 0 else 0,
                    'observations': len(regime_data),
                    'hit_rate': (regime_data['returns'] > 0).mean()
                }
        
        # Stress periods analysis (market down 10%+ over 20 days)
        drawdown_threshold = -0.10
        stress_periods = sp500_returns.rolling(20).sum() < drawdown_threshold
        
        stress_returns = company_returns[stress_periods[company_returns.index]].dropna()
        normal_returns = company_returns[~stress_periods[company_returns.index]].dropna()
        
        # Calculate up/down market betas for downside capture
        sp500_aligned = pd.DataFrame({
            'company': company_returns,
            'market': sp500_returns
        }).dropna()
        
        up_market = sp500_aligned[sp500_aligned['market'] > 0]
        down_market = sp500_aligned[sp500_aligned['market'] < 0]
        
        up_beta = _calculate_simple_beta(up_market) if len(up_market) > 20 else 1.0
        down_beta = _calculate_simple_beta(down_market) if len(down_market) > 20 else 1.0
        
        # Defensive metrics (raw, not scored)
        downside_capture_ratio = down_beta / up_beta if up_beta != 0 else 1.0
        
        # Bear market alpha
        bear_regimes = ['Low Vol Bear', 'High Vol Bear']
        bear_returns = []
        sp500_bear_returns = []
        for regime in bear_regimes:
            if regime in regime_metrics:
                bear_returns.append(regime_metrics[regime]['avg_return'])
            if regime in sp500_regime_perf:
                sp500_bear_returns.append(sp500_regime_perf[regime])
        
        bear_market_alpha = (np.mean(bear_returns) - np.mean(sp500_bear_returns)) if bear_returns and sp500_bear_returns else 0
        
        regime_analysis[company_name] = {
            'regime_performance': regime_metrics,
            'stress_performance': {
                'avg_return': stress_returns.mean() * 252 if len(stress_returns) > 0 else 0,
                'volatility': stress_returns.std() * np.sqrt(252) if len(stress_returns) > 0 else 0,
                'max_drawdown': stress_returns.min() if len(stress_returns) > 0 else 0,
                'observations': len(stress_returns)
            },
            'normal_performance': {
                'avg_return': normal_returns.mean() * 252 if len(normal_returns) > 0 else 0,
                'volatility': normal_returns.std() * np.sqrt(252) if len(normal_returns) > 0 else 0,
                'observations': len(normal_returns)
            },
            'defensive_metrics': {
                'downside_capture_ratio': downside_capture_ratio,
                'bear_market_alpha': bear_market_alpha,
                'stress_max_drawdown': stress_returns.min() if len(stress_returns) > 0 else 0,
                'stress_avg_return': stress_returns.mean() * 252 if len(stress_returns) > 0 else 0
            }
        }
    
    return regime_analysis


def _create_defensive_metrics_dataframe(regime_analysis: Dict) -> pd.DataFrame:
    """Create DataFrame for defensive metrics table"""
    
    rows = []
    for company_name, analysis in regime_analysis.items():
        dm = analysis['defensive_metrics']
        row = {
            'Company': company_name,
            'Downside Capture': f"{dm['downside_capture_ratio']:.3f}",
            'Bear Market Alpha': f"{dm['bear_market_alpha']*100:+.1f}%",
            'Stress Max DD': f"{dm['stress_max_drawdown']*100:.1f}%",
            'Stress Avg Return': f"{dm['stress_avg_return']:.1f}%",
            'Interpretation': 'Defensive' if dm['downside_capture_ratio'] < 0.9 else 'Moderate' if dm['downside_capture_ratio'] < 1.1 else 'Aggressive'
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_regime_performance_dataframe(regime_analysis: Dict) -> pd.DataFrame:
    """Create DataFrame for regime performance table"""
    
    rows = []
    for company_name, analysis in regime_analysis.items():
        row = {'Company': company_name}
        
        for regime in ['Low Vol Bull', 'Low Vol Bear', 'High Vol Bull', 'High Vol Bear']:
            if regime in analysis['regime_performance']:
                row[regime] = f"{analysis['regime_performance'][regime]['avg_return']*100:.1f}%"
            else:
                row[regime] = "N/A"
        
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_regime_heatmap(regime_analysis: Dict) -> str:
    """Create regime performance heatmap"""
    
    companies = list(regime_analysis.keys())
    regime_types = ['Low Vol Bull', 'Low Vol Bear', 'High Vol Bull', 'High Vol Bear']
    
    # Build z-matrix for heatmap
    z_data = []
    for company in companies:
        company_perf = []
        for regime in regime_types:
            if regime in regime_analysis[company]['regime_performance']:
                company_perf.append(regime_analysis[company]['regime_performance'][regime]['avg_return'] * 100)
            else:
                company_perf.append(0)
        z_data.append(company_perf)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': z_data,
            'x': regime_types,
            'y': companies,
            'colorscale': 'RdYlGn',
            'zmid': 0,
            'colorbar': {'title': 'Return (%)'},
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Return: %{z:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Performance Across Market Regimes', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Market Regime', 'side': 'bottom'},
            'yaxis': {'title': 'Company'},
            'height': max(400, len(companies) * 30)
        }
    }
    
    return build_plotly_chart(fig_data, "regime-heatmap", max(400, len(companies) * 30))


def _create_downside_capture_chart(regime_analysis: Dict) -> str:
    """Create downside capture ratio chart"""
    
    companies = list(regime_analysis.keys())
    downside_captures = [analysis['defensive_metrics']['downside_capture_ratio'] 
                        for analysis in regime_analysis.values()]
    
    colors = ['#10b981' if dc < 0.9 else '#f59e0b' if dc < 1.1 else '#ef4444' for dc in downside_captures]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': downside_captures,
            'marker': {'color': colors},
            'text': [f'{dc:.2f}' for dc in downside_captures],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Downside Capture: %{y:.3f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Downside Capture Ratio (Down Beta / Up Beta)', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Downside Capture Ratio'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 1.0,
                    'y1': 1.0,
                    'line': {'color': 'black', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 0.9,
                    'y1': 0.9,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dot'}
                }
            ],
            'annotations': [
                {
                    'x': len(companies) - 1,
                    'y': 1.0,
                    'text': 'Market (1.0)',
                    'showarrow': False,
                    'yshift': 10
                },
                {
                    'x': len(companies) - 1,
                    'y': 0.9,
                    'text': 'Defensive (<0.9)',
                    'showarrow': False,
                    'yshift': -15,
                    'font': {'color': 'green'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "downside-capture-chart", 500)


def _create_stress_normal_comparison_chart(regime_analysis: Dict) -> str:
    """Create stress vs normal performance comparison"""
    
    companies = list(regime_analysis.keys())
    stress_returns = [analysis['stress_performance']['avg_return'] 
                     for analysis in regime_analysis.values()]
    normal_returns = [analysis['normal_performance']['avg_return'] 
                     for analysis in regime_analysis.values()]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Normal Markets',
                'x': companies,
                'y': normal_returns,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Normal: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Stress Periods',
                'x': companies,
                'y': stress_returns,
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{x}</b><br>Stress: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Performance: Normal vs Stress Periods', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Annualized Return (%)', 'zeroline': True},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, "stress-normal-chart", 500)


def _create_stress_drawdown_chart(regime_analysis: Dict) -> str:
    """Create stress period maximum drawdown chart"""
    
    companies = list(regime_analysis.keys())
    max_drawdowns = [analysis['stress_performance']['max_drawdown'] * 100 
                    for analysis in regime_analysis.values()]
    
    colors = ['#10b981' if dd > -10 else '#f59e0b' if dd > -20 else '#ef4444' for dd in max_drawdowns]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': max_drawdowns,
            'marker': {'color': colors},
            'text': [f'{dd:.1f}%' for dd in max_drawdowns],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Max DD: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Maximum Drawdown in Stress Periods', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Maximum Drawdown (%)'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': -10,
                    'y1': -10,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': -20,
                    'y1': -20,
                    'line': {'color': 'orange', 'width': 1, 'dash': 'dash'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "stress-drawdown-chart", 500)


def _create_bear_market_performance_chart(regime_analysis: Dict) -> str:
    """Create bear market performance chart"""
    
    companies = list(regime_analysis.keys())
    bear_alphas = [analysis['defensive_metrics']['bear_market_alpha'] * 100 
                  for analysis in regime_analysis.values()]
    
    colors = ['#10b981' if ba > 0 else '#ef4444' for ba in bear_alphas]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': bear_alphas,
            'marker': {'color': colors},
            'text': [f'{ba:+.1f}%' for ba in bear_alphas],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Bear Alpha: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Bear Market Alpha vs S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Alpha in Bear Markets (%)', 'zeroline': True, 'zerolinewidth': 2},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, "bear-market-alpha-chart", 500)


def _generate_regime_insights(regime_analysis: Dict, avg_downside_capture: float,
                              avg_bear_alpha: float) -> str:
    """Generate regime analysis insights"""
    
    total = len(regime_analysis)
    
    insights = f"""
    <h4>Key Regime Insights:</h4>
    <ul>
        <li><strong>Downside Protection:</strong> Average downside capture of {avg_downside_capture:.2f} indicates the portfolio 
        {'provides strong downside protection' if avg_downside_capture < 0.9 
         else 'has moderate downside characteristics' if avg_downside_capture < 1.1 
         else 'amplifies downside moves'} relative to the S&P 500.</li>
        
        <li><strong>Bear Market Performance:</strong> Average bear market alpha of {avg_bear_alpha:+.1f}% shows 
        {'significant outperformance' if avg_bear_alpha > 5 
         else 'relative resilience' if avg_bear_alpha > 0 
         else 'underperformance'} during bearish conditions.</li>
        
        <li><strong>Stress Resilience:</strong> Companies with downside capture < 0.9 demonstrate defensive characteristics, 
        protecting capital during market downturns.</li>
        
        <li><strong>Regime Adaptability:</strong> Review the heatmap to identify which companies perform best in specific 
        market regimes for tactical allocation opportunities.</li>
    </ul>
    
    <h4>Interpretation Guide:</h4>
    <ul>
        <li><strong>Downside Capture < 0.9:</strong> Defensive - loses less in down markets</li>
        <li><strong>Downside Capture ≈ 1.0:</strong> Market-like downside exposure</li>
        <li><strong>Downside Capture > 1.1:</strong> Aggressive - amplifies downside moves</li>
        <li><strong>Positive Bear Alpha:</strong> Outperforms in bear markets (rare and valuable)</li>
    </ul>
    """
    
    return insights


# =============================================================================
# SECTION 16D: TECHNICAL ANALYSIS
# =============================================================================

def _build_section_16d_technical_analysis(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                         companies: Dict[str, str]) -> str:
    """Build Section 16D: Enhanced Technical Analysis"""
    
    # Calculate technical metrics
    technical_analysis = _calculate_technical_metrics(daily_prices, sp500_daily, companies)
    
    if not technical_analysis:
        return build_info_box("<p>Insufficient data for technical analysis.</p>", "warning", "16D. Technical Analysis")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16d')">
            <h2>16D. Enhanced Technical Analysis</h2>
            <span class="toggle-icon" id="section16d-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16d-content">
    """
    
    # Overview cards
    bullish_count = sum(1 for a in technical_analysis.values() 
                       if a['composite_signal']['overall_signal'] == 'Bullish')
    avg_rel_momentum = np.mean([a['momentum']['relative_momentum'] 
                                for a in technical_analysis.values()]) * 100
    strong_trend_count = sum(1 for a in technical_analysis.values() 
                            if a['trend']['trend_strength'] == 'Strong')
    
    cards = [
        {
            "label": "Bullish Signals",
            "value": f"{bullish_count}/{len(technical_analysis)}",
            "description": "Companies with bullish setup",
            "type": "success" if bullish_count > len(technical_analysis) * 0.5 else "warning"
        },
        {
            "label": "Avg Relative Momentum",
            "value": f"{avg_rel_momentum:+.1f}%",
            "description": "vs S&P 500",
            "type": "success" if avg_rel_momentum > 0 else "danger"
        },
        {
            "label": "Strong Trends",
            "value": f"{strong_trend_count}/{len(technical_analysis)}",
            "description": "Companies in strong trend",
            "type": "info"
        },
        {
            "label": "Signals Analyzed",
            "value": "4",
            "description": "RSI, Momentum, Trend, Volume",
            "type": "default"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Technical signals dashboard table
    html += "<h3>Technical Strength Dashboard</h3>"
    tech_dashboard_df = _create_technical_dashboard_dataframe(technical_analysis)
    html += build_enhanced_table(
        tech_dashboard_df,
        "tech-dashboard-16d",
        badge_columns=['RSI Signal', 'Momentum Signal', 'Trend Signal', 'Overall Signal'],
        sortable=True
    )
    
    # Detailed metrics table
    html += "<h3>Detailed Technical Metrics</h3>"
    tech_metrics_df = _create_technical_metrics_dataframe(technical_analysis)
    html += build_data_table(tech_metrics_df, "tech-metrics-16d", sortable=True)
    
    # Chart 1: Relative RSI
    html += _create_relative_rsi_chart(technical_analysis)
    
    # Chart 2: Relative Momentum
    html += _create_relative_momentum_chart(technical_analysis)
    
    # Chart 3: Price vs Moving Averages
    html += _create_price_ma_chart(technical_analysis)
    
    # Chart 4: Technical Signal Distribution
    html += _create_technical_distribution_chart(technical_analysis)
    
    # Chart 5: Composite Technical Strength
    html += _create_composite_strength_chart(technical_analysis)
    
    # Summary insights
    insights = _generate_technical_insights(technical_analysis, bullish_count, avg_rel_momentum)
    html += build_info_box(insights, "info", "Technical Analysis Insights")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _calculate_technical_metrics(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                 companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate technical indicators relative to S&P 500"""
    
    technical_analysis = {}
    
    # Calculate S&P 500 technicals
    sp500_rsi = _calculate_rsi(sp500_daily['close'].values)
    sp500_momentum_20d = (sp500_daily['close'].iloc[-1] / sp500_daily['close'].iloc[-20] - 1) if len(sp500_daily) > 20 else 0
    
    for company_name, ticker in companies.items():
        company_prices = daily_prices[daily_prices['Symbol'] == ticker].copy()
        
        if len(company_prices) < 60:
            continue
        
        # Calculate technical indicators
        company_rsi = _calculate_rsi(company_prices['close'].values)
        company_momentum_20d = (company_prices['close'].iloc[-1] / company_prices['close'].iloc[-20] - 1) if len(company_prices) > 20 else 0
        
        # Relative metrics
        relative_rsi = company_rsi - sp500_rsi
        relative_momentum = company_momentum_20d - sp500_momentum_20d
        
        # Moving averages
        sma_20 = company_prices['close'].rolling(20).mean().iloc[-1] if len(company_prices) >= 20 else company_prices['close'].mean()
        sma_50 = company_prices['close'].rolling(50).mean().iloc[-1] if len(company_prices) >= 50 else company_prices['close'].mean()
        sma_200 = company_prices['close'].rolling(200).mean().iloc[-1] if len(company_prices) >= 200 else company_prices['close'].mean()
        
        current_price = company_prices['close'].iloc[-1]
        
        # Trend analysis
        price_vs_sma20 = (current_price / sma_20 - 1) * 100
        price_vs_sma50 = (current_price / sma_50 - 1) * 100
        price_vs_sma200 = (current_price / sma_200 - 1) * 100
        
        trend_alignment = 0
        if current_price > sma_20: trend_alignment += 1
        if current_price > sma_50: trend_alignment += 1
        if current_price > sma_200: trend_alignment += 1
        if sma_20 > sma_50: trend_alignment += 1
        if sma_50 > sma_200: trend_alignment += 1
        
        trend_strength = 'Strong' if trend_alignment >= 4 else 'Moderate' if trend_alignment >= 2 else 'Weak'
        
        # Volume analysis
        if 'volume' in company_prices.columns:
            avg_volume = company_prices['volume'].rolling(20).mean().iloc[-1]
            recent_volume = company_prices['volume'].iloc[-5:].mean()
            volume_surge = (recent_volume / avg_volume - 1) if avg_volume > 0 else 0
        else:
            volume_surge = 0
        
        # Individual signals
        rsi_signal = _classify_rsi_signal(relative_rsi)
        momentum_signal = _classify_momentum_signal(relative_momentum)
        trend_signal = _classify_trend_signal(trend_alignment)
        volume_signal = _classify_volume_signal(volume_surge)
        
        # Composite technical score using Z-scores
        all_rel_rsi = []
        all_rel_momentum = []
        all_trend_align = []
        
        # We'll calculate z-scores after gathering all data
        technical_analysis[company_name] = {
            'rsi': {
                'absolute': company_rsi,
                'relative': relative_rsi,
                'signal': rsi_signal
            },
            'momentum': {
                'absolute': company_momentum_20d,
                'relative_momentum': relative_momentum,
                'signal': momentum_signal
            },
            'trend': {
                'price_vs_sma20': price_vs_sma20,
                'price_vs_sma50': price_vs_sma50,
                'price_vs_sma200': price_vs_sma200,
                'alignment_score': trend_alignment,
                'trend_strength': trend_strength,
                'signal': trend_signal
            },
            'volume': {
                'surge': volume_surge,
                'signal': volume_signal
            }
        }
    
    # Calculate composite signals with z-scores
    rel_rsi_values = [a['rsi']['relative'] for a in technical_analysis.values()]
    rel_momentum_values = [a['momentum']['relative_momentum'] for a in technical_analysis.values()]
    trend_scores = [a['trend']['alignment_score'] for a in technical_analysis.values()]
    
    mean_rsi = np.mean(rel_rsi_values)
    std_rsi = np.std(rel_rsi_values) if len(rel_rsi_values) > 1 else 1
    mean_momentum = np.mean(rel_momentum_values)
    std_momentum = np.std(rel_momentum_values) if len(rel_momentum_values) > 1 else 1
    mean_trend = np.mean(trend_scores)
    std_trend = np.std(trend_scores) if len(trend_scores) > 1 else 1
    
    for company_name, analysis in technical_analysis.items():
        # Calculate z-scores
        rsi_z = (analysis['rsi']['relative'] - mean_rsi) / std_rsi if std_rsi > 0 else 0
        momentum_z = (analysis['momentum']['relative_momentum'] - mean_momentum) / std_momentum if std_momentum > 0 else 0
        trend_z = (analysis['trend']['alignment_score'] - mean_trend) / std_trend if std_trend > 0 else 0
        
        # Weighted composite (momentum most important)
        composite_z = rsi_z * 0.25 + momentum_z * 0.5 + trend_z * 0.25
        
        # Convert to 0-10 scale
        from scipy.stats import norm
        composite_score = norm.cdf(composite_z) * 10
        
        # Overall signal
        if composite_score >= 6.5:
            overall_signal = 'Bullish'
        elif composite_score >= 3.5:
            overall_signal = 'Neutral'
        else:
            overall_signal = 'Bearish'
        
        analysis['composite_signal'] = {
            'score': composite_score,
            'overall_signal': overall_signal,
            'rsi_z': rsi_z,
            'momentum_z': momentum_z,
            'trend_z': trend_z
        }
    
    return technical_analysis


def _calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def _classify_rsi_signal(relative_rsi: float) -> str:
    """Classify RSI signal"""
    if relative_rsi > 15:
        return "Strong Overbought vs SPX"
    elif relative_rsi > 5:
        return "Overbought vs SPX"
    elif relative_rsi > -5:
        return "Neutral"
    elif relative_rsi > -15:
        return "Oversold vs SPX"
    else:
        return "Strong Oversold vs SPX"


def _classify_momentum_signal(relative_momentum: float) -> str:
    """Classify momentum signal"""
    if relative_momentum > 0.10:
        return "Strong Positive"
    elif relative_momentum > 0.03:
        return "Positive"
    elif relative_momentum > -0.03:
        return "Neutral"
    elif relative_momentum > -0.10:
        return "Negative"
    else:
        return "Strong Negative"


def _classify_trend_signal(alignment_score: int) -> str:
    """Classify trend signal"""
    if alignment_score >= 4:
        return "Strong Uptrend"
    elif alignment_score >= 3:
        return "Uptrend"
    elif alignment_score >= 2:
        return "Mixed"
    else:
        return "Downtrend"


def _classify_volume_signal(volume_surge: float) -> str:
    """Classify volume signal"""
    if volume_surge > 0.5:
        return "High Surge"
    elif volume_surge > 0.2:
        return "Moderate Surge"
    elif volume_surge > -0.2:
        return "Normal"
    else:
        return "Low Volume"


def _create_technical_dashboard_dataframe(technical_analysis: Dict) -> pd.DataFrame:
    """Create technical signals dashboard DataFrame"""
    
    rows = []
    for company_name, analysis in technical_analysis.items():
        row = {
            'Company': company_name,
            'RSI Signal': analysis['rsi']['signal'],
            'Momentum Signal': analysis['momentum']['signal'],
            'Trend Signal': analysis['trend']['signal'],
            'Volume Signal': analysis['volume']['signal'],
            'Overall Signal': analysis['composite_signal']['overall_signal'],
            'Tech Score': f"{analysis['composite_signal']['score']:.1f}/10"
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_technical_metrics_dataframe(technical_analysis: Dict) -> pd.DataFrame:
    """Create detailed technical metrics DataFrame"""
    
    rows = []
    for company_name, analysis in technical_analysis.items():
        row = {
            'Company': company_name,
            'RSI': f"{analysis['rsi']['absolute']:.1f}",
            'Relative RSI': f"{analysis['rsi']['relative']:+.1f}",
            '20D Momentum': f"{analysis['momentum']['absolute']*100:.1f}%",
            'Rel Momentum': f"{analysis['momentum']['relative_momentum']*100:+.1f}%",
            'vs SMA20': f"{analysis['trend']['price_vs_sma20']:+.1f}%",
            'vs SMA50': f"{analysis['trend']['price_vs_sma50']:+.1f}%",
            'Trend Score': f"{analysis['trend']['alignment_score']}/5"
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_relative_rsi_chart(technical_analysis: Dict) -> str:
    """Create relative RSI chart"""
    
    companies = list(technical_analysis.keys())
    rel_rsis = [analysis['rsi']['relative'] for analysis in technical_analysis.values()]
    
    colors = ['#10b981' if rsi > 10 else '#ef4444' if rsi < -10 else '#f59e0b' for rsi in rel_rsis]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': rel_rsis,
            'marker': {'color': colors},
            'text': [f'{rsi:+.1f}' for rsi in rel_rsis],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Relative RSI: %{y:+.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'RSI Relative to S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Relative RSI', 'zeroline': True, 'zerolinewidth': 2},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 10,
                    'y1': 10,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': -10,
                    'y1': -10,
                    'line': {'color': 'red', 'width': 1, 'dash': 'dash'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "relative-rsi-chart", 500)


def _create_relative_momentum_chart(technical_analysis: Dict) -> str:
    """Create relative momentum chart"""
    
    companies = list(technical_analysis.keys())
    rel_momentums = [analysis['momentum']['relative_momentum'] * 100 
                    for analysis in technical_analysis.values()]
    
    colors = ['#10b981' if m > 5 else '#ef4444' if m < -5 else '#f59e0b' for m in rel_momentums]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': rel_momentums,
            'marker': {'color': colors},
            'text': [f'{m:+.1f}%' for m in rel_momentums],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Relative Momentum: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': '20-Day Momentum vs S&P 500', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Relative Momentum (%)', 'zeroline': True, 'zerolinewidth': 2}
        }
    }
    
    return build_plotly_chart(fig_data, "relative-momentum-chart", 500)


def _create_price_ma_chart(technical_analysis: Dict) -> str:
    """Create price vs moving averages chart"""
    
    companies = list(technical_analysis.keys())
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'vs SMA20',
                'x': companies,
                'y': [analysis['trend']['price_vs_sma20'] for analysis in technical_analysis.values()],
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>vs SMA20: %{y:+.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'vs SMA50',
                'x': companies,
                'y': [analysis['trend']['price_vs_sma50'] for analysis in technical_analysis.values()],
                'marker': {'color': '#8b5cf6'},
                'hovertemplate': '<b>%{x}</b><br>vs SMA50: %{y:+.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'vs SMA200',
                'x': companies,
                'y': [analysis['trend']['price_vs_sma200'] for analysis in technical_analysis.values()],
                'marker': {'color': '#ec4899'},
                'hovertemplate': '<b>%{x}</b><br>vs SMA200: %{y:+.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Price Position vs Moving Averages', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Price vs MA (%)', 'zeroline': True},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, "price-ma-chart", 500)


def _create_technical_distribution_chart(technical_analysis: Dict) -> str:
    """Create technical signal distribution pie chart"""
    
    signals = [analysis['composite_signal']['overall_signal'] for analysis in technical_analysis.values()]
    signal_counts = {
        'Bullish': signals.count('Bullish'),
        'Neutral': signals.count('Neutral'),
        'Bearish': signals.count('Bearish')
    }
    
    # Remove zero counts
    signal_counts = {k: v for k, v in signal_counts.items() if v > 0}
    
    colors_map = {'Bullish': '#10b981', 'Neutral': '#f59e0b', 'Bearish': '#ef4444'}
    colors = [colors_map[k] for k in signal_counts.keys()]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': list(signal_counts.keys()),
            'values': list(signal_counts.values()),
            'marker': {'colors': colors},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Technical Signal Distribution', 'font': {'size': 16, 'weight': 'bold'}}
        }
    }
    
    return build_plotly_chart(fig_data, "tech-distribution-chart", 400)


def _create_composite_strength_chart(technical_analysis: Dict) -> str:
    """Create composite technical strength chart"""
    
    companies = list(technical_analysis.keys())
    scores = [analysis['composite_signal']['score'] for analysis in technical_analysis.values()]
    
    colors = ['#10b981' if s >= 6.5 else '#ef4444' if s < 3.5 else '#f59e0b' for s in scores]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': scores,
            'marker': {'color': colors},
            'text': [f'{s:.1f}' for s in scores],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Tech Score: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Composite Technical Strength Score', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Technical Score (0-10)', 'range': [0, 11]},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 6.5,
                    'y1': 6.5,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 3.5,
                    'y1': 3.5,
                    'line': {'color': 'red', 'width': 1, 'dash': 'dash'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "composite-strength-chart", 500)


def _generate_technical_insights(technical_analysis: Dict, bullish_count: int,
                                avg_rel_momentum: float) -> str:
    """Generate technical analysis insights"""
    
    total = len(technical_analysis)
    
    insights = f"""
    <h4>Key Technical Insights:</h4>
    <ul>
        <li><strong>Technical Setup:</strong> {bullish_count}/{total} companies showing bullish technical signals, 
        suggesting {'strong' if bullish_count > total * 0.6 else 'moderate' if bullish_count > total * 0.3 else 'weak'} 
        technical momentum across the portfolio.</li>
        
        <li><strong>Relative Momentum:</strong> Average relative momentum of {avg_rel_momentum:+.1f}% indicates the portfolio is 
        {'outperforming' if avg_rel_momentum > 0 else 'underperforming'} the S&P 500 on a momentum basis.</li>
        
        <li><strong>Composite Scoring:</strong> Technical scores use Z-score normalization with weighted factors (Momentum 50%, 
        RSI 25%, Trend 25%) to provide relative strength rankings within the portfolio.</li>
        
        <li><strong>Signal Alignment:</strong> Companies with all signals aligned (bullish RSI, positive momentum, strong trend) 
        represent the strongest technical setups for potential outperformance.</li>
    </ul>
    
    <h4>Interpretation Guide:</h4>
    <ul>
        <li><strong>Relative RSI > +10:</strong> Overbought vs market (potential reversal)</li>
        <li><strong>Relative Momentum > +5%:</strong> Strong outperformance momentum</li>
        <li><strong>Price > All MAs + Aligned:</strong> Strong uptrend confirmation</li>
        <li><strong>Tech Score > 6.5:</strong> Bullish technical setup</li>
    </ul>
    """
    
    return insights


"""
Section 16 - Step 3: Subsections 16E and 16F
Replace the stubbed functions in section_16.py with these implementations
"""

# =============================================================================
# SECTION 16E: RISK MANAGEMENT
# =============================================================================

def _build_section_16e_risk_management(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                      companies: Dict[str, str]) -> str:
    """Build Section 16E: Improved Risk Management"""
    
    # Need beta analysis for risk decomposition
    beta_analysis = _calculate_enhanced_beta_metrics(daily_prices, sp500_daily, companies)
    
    if not beta_analysis:
        return build_info_box("<p>Insufficient data for risk analysis.</p>", "warning", "16E. Risk Management")
    
    # Calculate risk metrics
    risk_analysis = _calculate_risk_metrics(daily_prices, sp500_daily, companies, beta_analysis)
    
    if not risk_analysis:
        return build_info_box("<p>Insufficient data for risk analysis.</p>", "warning", "16E. Risk Management")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16e')">
            <h2>16E. Improved Risk Management</h2>
            <span class="toggle-icon" id="section16e-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16e-content">
    """
    
    # Overview cards
    avg_total_risk = np.mean([a['total_risk'] for a in risk_analysis.values()]) * 100
    avg_systematic_pct = np.mean([a['systematic_pct'] for a in risk_analysis.values()]) * 100
    avg_max_dd = np.mean([a['max_drawdown'] for a in risk_analysis.values()]) * 100
    high_idio_count = sum(1 for a in risk_analysis.values() if a['idiosyncratic_pct'] > 0.5)
    
    cards = [
        {
            "label": "Avg Total Risk",
            "value": f"{avg_total_risk:.1f}%",
            "description": "Annualized volatility",
            "type": "info"
        },
        {
            "label": "Avg Systematic Risk",
            "value": f"{avg_systematic_pct:.0f}%",
            "description": "% of total risk from market",
            "type": "warning" if avg_systematic_pct > 70 else "success"
        },
        {
            "label": "Avg Max Drawdown",
            "value": f"{avg_max_dd:.1f}%",
            "description": "Peak to trough decline",
            "type": "danger" if avg_max_dd < -30 else "warning" if avg_max_dd < -20 else "success"
        },
        {
            "label": "High Diversification",
            "value": f"{high_idio_count}/{len(risk_analysis)}",
            "description": "Idiosyncratic risk > 50%",
            "type": "success"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Risk Profile Matrix
    html += "<h3>Risk Profile Matrix</h3>"
    risk_profile_df = _create_risk_profile_dataframe(risk_analysis)
    html += build_enhanced_table(
        risk_profile_df,
        "risk-profile-16e",
        color_columns={
            'Risk Level': lambda x: 'excellent' if 'Low' in x else 'fair' if 'Moderate' in x else 'poor'
        },
        sortable=True
    )
    
    # Risk decomposition table
    html += "<h3>Risk Decomposition Analysis</h3>"
    risk_decomp_df = _create_risk_decomposition_dataframe(risk_analysis)
    html += build_data_table(risk_decomp_df, "risk-decomp-16e", sortable=True)
    
    # Chart 1: Risk Decomposition Stacked Bar
    html += _create_risk_decomposition_chart(risk_analysis)
    
    # Chart 2: Systematic Risk Percentage
    html += _create_systematic_risk_pct_chart(risk_analysis)
    
    # Chart 3: Total Risk vs Downside Risk Scatter
    html += _create_total_vs_downside_risk_scatter(risk_analysis)
    
    # Chart 4: Maximum Drawdown Analysis
    html += _create_max_drawdown_chart(risk_analysis)
    
    # Chart 5: Risk-Adjusted Return (Sharpe/Sortino)
    html += _create_risk_adjusted_return_chart(risk_analysis)
    
    # Chart 6: Recovery Time Analysis
    html += _create_recovery_time_chart(risk_analysis)
    
    # Summary insights
    insights = _generate_risk_insights(risk_analysis, avg_systematic_pct, high_idio_count)
    html += build_info_box(insights, "info", "Risk Management Insights")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _calculate_risk_metrics(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                            companies: Dict[str, str], beta_analysis: Dict) -> Dict[str, Dict]:
    """Calculate systematic vs idiosyncratic risk components"""
    
    risk_analysis = {}
    
    # Calculate market variance
    sp500_returns = sp500_daily.set_index('date')['close'].pct_change().dropna()
    market_variance = sp500_returns.var()
    market_volatility = sp500_returns.std() * np.sqrt(252)
    
    for company_name, ticker in companies.items():
        if company_name not in beta_analysis:
            continue
        
        company_prices = daily_prices[daily_prices['Symbol'] == ticker].copy()
        
        if len(company_prices) < 60:
            continue
        
        company_returns = company_prices.set_index('date')['close'].pct_change().dropna()
        
        # Get beta
        beta = beta_analysis[company_name]['current_beta']
        
        # Total variance and volatility
        total_variance = company_returns.var()
        total_volatility = company_returns.std() * np.sqrt(252)
        
        # Systematic risk (beta^2 * market_variance)
        systematic_variance = (beta ** 2) * market_variance
        systematic_volatility = np.sqrt(systematic_variance) * np.sqrt(252)
        
        # Idiosyncratic risk
        idiosyncratic_variance = max(0, total_variance - systematic_variance)
        idiosyncratic_volatility = np.sqrt(idiosyncratic_variance) * np.sqrt(252)
        
        # Risk decomposition percentages
        systematic_pct = systematic_variance / total_variance if total_variance > 0 else 0
        idiosyncratic_pct = 1 - systematic_pct
        
        # Downside risk metrics
        downside_returns = company_returns[company_returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + company_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Recovery analysis
        recovery_days = None
        if max_drawdown < 0:
            drawdown_start = drawdown.idxmin()
            recovery_mask = (drawdown.index > drawdown_start) & (drawdown > -0.01)
            if recovery_mask.any():
                recovery_date = drawdown[recovery_mask].index[0]
                recovery_days = (recovery_date - drawdown_start).days
        
        # Risk-adjusted returns
        mean_return = company_returns.mean() * 252
        sharpe_ratio = mean_return / total_volatility if total_volatility > 0 else 0
        sortino_ratio = mean_return / downside_deviation if downside_deviation > 0 else 0
        
        # Downside beta (already calculated in beta_analysis)
        down_beta = beta_analysis[company_name].get('down_beta', beta)
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(company_returns, 5) * np.sqrt(252)
        
        # Risk level classification
        risk_level = _classify_risk_level(systematic_pct, max_drawdown, total_volatility)
        
        risk_analysis[company_name] = {
            'total_risk': total_volatility,
            'systematic_risk': systematic_volatility,
            'idiosyncratic_risk': idiosyncratic_volatility,
            'systematic_pct': systematic_pct,
            'idiosyncratic_pct': idiosyncratic_pct,
            'downside_deviation': downside_deviation,
            'max_drawdown': max_drawdown,
            'recovery_days': recovery_days,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'down_beta': down_beta,
            'var_95': var_95,
            'risk_level': risk_level
        }
    
    return risk_analysis


def _classify_risk_level(systematic_pct: float, max_dd: float, total_vol: float) -> str:
    """Classify risk level based on multiple factors"""
    risk_score = 0
    
    # Lower systematic risk is better for diversification
    if systematic_pct < 0.5: risk_score += 2
    elif systematic_pct < 0.7: risk_score += 1
    
    # Drawdown assessment
    if max_dd > -0.2: risk_score += 2
    elif max_dd > -0.3: risk_score += 1
    
    # Volatility assessment (relative to market ~15-20%)
    if total_vol < 0.20: risk_score += 2
    elif total_vol < 0.30: risk_score += 1
    
    if risk_score >= 5: return "Low Risk"
    elif risk_score >= 3: return "Moderate Risk"
    else: return "High Risk"


def _create_risk_profile_dataframe(risk_analysis: Dict) -> pd.DataFrame:
    """Create risk profile matrix DataFrame"""
    
    rows = []
    for company_name, analysis in risk_analysis.items():
        row = {
            'Company': company_name,
            'Total Risk': f"{analysis['total_risk']*100:.1f}%",
            'Systematic %': f"{analysis['systematic_pct']*100:.0f}%",
            'Idiosyncratic %': f"{analysis['idiosyncratic_pct']*100:.0f}%",
            'Downside Dev': f"{analysis['downside_deviation']*100:.1f}%",
            'Max Drawdown': f"{analysis['max_drawdown']*100:.1f}%",
            'Recovery Days': str(analysis['recovery_days']) if analysis['recovery_days'] else 'N/A',
            'Sharpe Ratio': f"{analysis['sharpe_ratio']:.2f}",
            'Sortino Ratio': f"{analysis['sortino_ratio']:.2f}",
            'Risk Level': analysis['risk_level']
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_risk_decomposition_dataframe(risk_analysis: Dict) -> pd.DataFrame:
    """Create risk decomposition DataFrame"""
    
    rows = []
    for company_name, analysis in risk_analysis.items():
        row = {
            'Company': company_name,
            'Systematic Risk': f"{analysis['systematic_risk']*100:.1f}%",
            'Idiosyncratic Risk': f"{analysis['idiosyncratic_risk']*100:.1f}%",
            'Total Risk': f"{analysis['total_risk']*100:.1f}%",
            'Downside Beta': f"{analysis['down_beta']:.3f}",
            'VaR (95%)': f"{analysis['var_95']*100:.1f}%"
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_risk_decomposition_chart(risk_analysis: Dict) -> str:
    """Create risk decomposition stacked bar chart"""
    
    companies = list(risk_analysis.keys())
    systematic_risks = [analysis['systematic_risk'] * 100 for analysis in risk_analysis.values()]
    idiosyncratic_risks = [analysis['idiosyncratic_risk'] * 100 for analysis in risk_analysis.values()]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Systematic Risk',
                'x': companies,
                'y': systematic_risks,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Systematic: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Idiosyncratic Risk',
                'x': companies,
                'y': idiosyncratic_risks,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Idiosyncratic: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Risk Decomposition: Systematic vs Idiosyncratic', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Volatility (%)'},
            'barmode': 'stack',
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, "risk-decomposition-chart", 500)


def _create_systematic_risk_pct_chart(risk_analysis: Dict) -> str:
    """Create systematic risk percentage chart"""
    
    companies = list(risk_analysis.keys())
    systematic_pcts = [analysis['systematic_pct'] * 100 for analysis in risk_analysis.values()]
    
    colors = ['#ef4444' if pct > 70 else '#f59e0b' if pct > 50 else '#10b981' for pct in systematic_pcts]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': systematic_pcts,
            'marker': {'color': colors},
            'text': [f'{pct:.0f}%' for pct in systematic_pcts],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Systematic: %{y:.0f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Systematic Risk as % of Total Risk', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Systematic Risk (%)', 'range': [0, 110]},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 50,
                    'y1': 50,
                    'line': {'color': 'green', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 70,
                    'y1': 70,
                    'line': {'color': 'orange', 'width': 1, 'dash': 'dot'}
                }
            ],
            'annotations': [
                {
                    'x': len(companies) - 1,
                    'y': 50,
                    'text': 'Well Diversified (50%)',
                    'showarrow': False,
                    'yshift': 10,
                    'font': {'color': 'green', 'size': 10}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "systematic-risk-pct-chart", 500)


def _create_total_vs_downside_risk_scatter(risk_analysis: Dict) -> str:
    """Create total risk vs downside risk scatter plot"""
    
    companies = list(risk_analysis.keys())
    total_risks = [analysis['total_risk'] * 100 for analysis in risk_analysis.values()]
    downside_devs = [analysis['downside_deviation'] * 100 for analysis in risk_analysis.values()]
    systematic_pcts = [analysis['systematic_pct'] * 100 for analysis in risk_analysis.values()]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': total_risks,
            'y': downside_devs,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': systematic_pcts,
                'colorscale': [[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']],
                'showscale': True,
                'colorbar': {'title': 'Systematic %'}
            },
            'hovertemplate': '<b>%{text}</b><br>Total Risk: %{x:.1f}%<br>Downside: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Total Risk vs Downside Risk', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Total Risk (%)', 'zeroline': False},
            'yaxis': {'title': 'Downside Deviation (%)', 'zeroline': False},
            'shapes': [{
                'type': 'line',
                'x0': 0,
                'y0': 0,
                'x1': max(total_risks) * 1.1,
                'y1': max(total_risks) * 1.1,
                'line': {'color': 'gray', 'width': 1, 'dash': 'dash'}
            }],
            'annotations': [{
                'x': max(total_risks) * 0.9,
                'y': max(total_risks) * 0.9,
                'text': 'Equal Risk Line',
                'showarrow': False,
                'font': {'color': 'gray', 'size': 10}
            }],
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, "total-downside-scatter", 500)


def _create_max_drawdown_chart(risk_analysis: Dict) -> str:
    """Create maximum drawdown chart"""
    
    companies = list(risk_analysis.keys())
    max_drawdowns = [analysis['max_drawdown'] * 100 for analysis in risk_analysis.values()]
    
    colors = ['#10b981' if dd > -15 else '#f59e0b' if dd > -25 else '#ef4444' for dd in max_drawdowns]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': max_drawdowns,
            'marker': {'color': colors},
            'text': [f'{dd:.1f}%' for dd in max_drawdowns],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Max DD: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Maximum Drawdown Analysis', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Maximum Drawdown (%)'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': -15,
                    'y1': -15,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': -25,
                    'y1': -25,
                    'line': {'color': 'orange', 'width': 1, 'dash': 'dash'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "max-drawdown-chart", 500)


def _create_risk_adjusted_return_chart(risk_analysis: Dict) -> str:
    """Create risk-adjusted return (Sharpe and Sortino) chart"""
    
    companies = list(risk_analysis.keys())
    sharpe_ratios = [analysis['sharpe_ratio'] for analysis in risk_analysis.values()]
    sortino_ratios = [analysis['sortino_ratio'] for analysis in risk_analysis.values()]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Sharpe Ratio',
                'x': companies,
                'y': sharpe_ratios,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Sharpe: %{y:.2f}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Sortino Ratio',
                'x': companies,
                'y': sortino_ratios,
                'marker': {'color': '#8b5cf6'},
                'hovertemplate': '<b>%{x}</b><br>Sortino: %{y:.2f}<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Risk-Adjusted Returns: Sharpe vs Sortino', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Ratio', 'zeroline': True},
            'barmode': 'group',
            'hovermode': 'x unified',
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 1.0,
                'y1': 1.0,
                'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, "risk-adjusted-return-chart", 500)


def _create_recovery_time_chart(risk_analysis: Dict) -> str:
    """Create recovery time analysis chart"""
    
    companies = list(risk_analysis.keys())
    recovery_days = []
    
    for analysis in risk_analysis.values():
        if analysis['recovery_days'] is not None:
            recovery_days.append(analysis['recovery_days'])
        else:
            recovery_days.append(0)
    
    # Filter out companies with no recovery data for coloring
    colors = ['#10b981' if days > 0 and days < 60 else '#f59e0b' if days >= 60 and days < 120 else '#ef4444' if days >= 120 else '#94a3b8' for days in recovery_days]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': recovery_days,
            'marker': {'color': colors},
            'text': [f'{d}d' if d > 0 else 'N/A' for d in recovery_days],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Recovery: %{y} days<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Recovery Time from Maximum Drawdown', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Days to Recovery'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 60,
                    'y1': 60,
                    'line': {'color': 'green', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 120,
                    'y1': 120,
                    'line': {'color': 'orange', 'width': 1, 'dash': 'dash'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, "recovery-time-chart", 500)


def _generate_risk_insights(risk_analysis: Dict, avg_systematic_pct: float,
                           high_idio_count: int) -> str:
    """Generate risk management insights"""
    
    total = len(risk_analysis)
    
    insights = f"""
    <h4>Key Risk Management Insights:</h4>
    <ul>
        <li><strong>Diversification Potential:</strong> {avg_systematic_pct:.0f}% average systematic risk indicates 
        {'limited' if avg_systematic_pct > 70 else 'moderate' if avg_systematic_pct > 50 else 'strong'} diversification benefits. 
        {high_idio_count}/{total} companies have majority idiosyncratic risk (>50%).</li>
        
        <li><strong>Risk Decomposition:</strong> Companies with high idiosyncratic risk percentages offer better diversification 
        as their returns are driven more by company-specific factors than market movements.</li>
        
        <li><strong>Downside Protection:</strong> Companies where downside deviation is significantly lower than total risk 
        demonstrate asymmetric risk profiles - less downside volatility.</li>
        
        <li><strong>Recovery Capability:</strong> Shorter recovery times indicate resilience. Companies recovering in <60 days 
        show strong rebound characteristics.</li>
        
        <li><strong>Risk-Adjusted Performance:</strong> Sortino ratios focus on downside risk. Higher Sortino vs Sharpe suggests 
        positive return distribution skew.</li>
    </ul>
    
    <h4>Risk Profile Interpretation:</h4>
    <ul>
        <li><strong>Systematic Risk < 50%:</strong> Well-diversified, company-specific drivers</li>
        <li><strong>Systematic Risk > 70%:</strong> High market sensitivity, limited diversification</li>
        <li><strong>Sharpe Ratio > 1.0:</strong> Excellent risk-adjusted returns</li>
        <li><strong>Max Drawdown < -25%:</strong> High risk, review position sizing</li>
    </ul>
    """
    
    return insights


# =============================================================================
# SECTION 16F: PORTFOLIO CONSTRUCTION INSIGHTS
# =============================================================================

def _build_section_16f_portfolio_insights(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                         companies: Dict[str, str]) -> str:
    """Build Section 16F: Portfolio Construction Insights"""
    
    # Gather all required analyses
    beta_analysis = _calculate_enhanced_beta_metrics(daily_prices, sp500_daily, companies)
    risk_analysis = _calculate_risk_metrics(daily_prices, sp500_daily, companies, beta_analysis) if beta_analysis else {}
    performance_analysis = _calculate_performance_metrics(
        daily_prices, daily_prices, sp500_daily, sp500_daily, companies
    )
    
    if not beta_analysis or not risk_analysis or not performance_analysis:
        return build_info_box("<p>Insufficient data for portfolio insights.</p>", "warning", "16F. Portfolio Insights")
    
    # Calculate portfolio insights
    portfolio_insights = _calculate_portfolio_insights(
        beta_analysis, performance_analysis, risk_analysis, companies
    )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16f')">
            <h2>16F. Portfolio Construction Insights</h2>
            <span class="toggle-icon" id="section16f-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16f-content">
    """
    
    # Overview cards
    high_diversification = sum(1 for i in portfolio_insights.values() 
                               if i['diversification_benefit'] == 'High')
    overweight_signals = sum(1 for i in portfolio_insights.values() 
                            if i['timing_signal'] == 'Overweight')
    defensive_roles = sum(1 for i in portfolio_insights.values() 
                         if i['portfolio_role'] == 'Defensive')
    alpha_generators = sum(1 for i in portfolio_insights.values() 
                          if i['portfolio_role'] == 'Alpha Generator')
    
    cards = [
        {
            "label": "High Diversification",
            "value": f"{high_diversification}/{len(portfolio_insights)}",
            "description": "Strong diversification benefit",
            "type": "success"
        },
        {
            "label": "Overweight Signals",
            "value": f"{overweight_signals}/{len(portfolio_insights)}",
            "description": "Timing favors increase",
            "type": "info"
        },
        {
            "label": "Defensive Positions",
            "value": f"{defensive_roles}/{len(portfolio_insights)}",
            "description": "Portfolio stabilizers",
            "type": "success"
        },
        {
            "label": "Alpha Generators",
            "value": f"{alpha_generators}/{len(portfolio_insights)}",
            "description": "Consistent outperformers",
            "type": "warning"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Portfolio construction recommendations table
    html += "<h3>Portfolio Construction Recommendations</h3>"
    portfolio_df = _create_portfolio_recommendations_dataframe(portfolio_insights)
    html += build_enhanced_table(
        portfolio_df,
        "portfolio-recommendations-16f",
        badge_columns=['Diversification Benefit', 'Timing Signal', 'Portfolio Role', 'Allocation Recommendation'],
        sortable=True
    )
    
    # Chart 1: Diversification Benefit Distribution
    html += _create_diversification_benefit_chart(portfolio_insights)
    
    # Chart 2: Portfolio Role Allocation
    html += _create_portfolio_role_chart(portfolio_insights)
    
    # Chart 3: Timing Signals Dashboard
    html += _create_timing_signals_chart(portfolio_insights)
    
    # Chart 4: Allocation Recommendations
    html += _create_allocation_recommendations_chart(portfolio_insights)
    
    # Chart 5: Risk-Return Positioning
    html += _create_risk_return_positioning_chart(portfolio_insights, risk_analysis, performance_analysis)
    
    # Summary insights
    insights = _generate_portfolio_insights_summary(
        portfolio_insights, high_diversification, overweight_signals, 
        defensive_roles, alpha_generators
    )
    html += build_info_box(insights, "info", "Portfolio Construction Insights")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _calculate_portfolio_insights(beta_analysis: Dict, performance_analysis: Dict,
                                  risk_analysis: Dict, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate portfolio construction insights"""
    
    portfolio_insights = {}
    
    for company_name in companies.keys():
        if company_name not in beta_analysis:
            continue
        
        insights = {
            'diversification_benefit': 'Moderate',
            'timing_signal': 'Neutral',
            'hedging_effectiveness': 'Low',
            'portfolio_role': 'Core',
            'allocation_recommendation': 'Market Weight'
        }
        
        # Diversification benefit based on idiosyncratic risk
        if company_name in risk_analysis:
            idio_pct = risk_analysis[company_name]['idiosyncratic_pct']
            if idio_pct > 0.6:
                insights['diversification_benefit'] = 'High'
            elif idio_pct > 0.4:
                insights['diversification_benefit'] = 'Moderate'
            else:
                insights['diversification_benefit'] = 'Low'
        
        # Timing signal based on relative momentum and alpha
        if company_name in performance_analysis:
            rel_strength = performance_analysis[company_name].get('relative_strength', 0)
            alpha = performance_analysis[company_name].get('alpha', 0)
            
            if rel_strength > 0.1 or alpha > 0.05:
                insights['timing_signal'] = 'Overweight'
            elif rel_strength < -0.1 or alpha < -0.05:
                insights['timing_signal'] = 'Underweight'
            else:
                insights['timing_signal'] = 'Neutral'
        
        # Hedging effectiveness based on beta
        beta = beta_analysis[company_name]['current_beta']
        if beta < -0.3:
            insights['hedging_effectiveness'] = 'High'
        elif beta < 0.3:
            insights['hedging_effectiveness'] = 'Moderate'
        else:
            insights['hedging_effectiveness'] = 'Low'
        
        # Portfolio role determination
        down_beta = beta_analysis[company_name].get('down_beta', beta)
        up_beta = beta_analysis[company_name].get('up_beta', beta)
        
        if down_beta < up_beta * 0.8:
            insights['portfolio_role'] = 'Defensive'
        elif company_name in performance_analysis and performance_analysis[company_name].get('alpha', 0) > 0.05:
            insights['portfolio_role'] = 'Alpha Generator'
        elif beta > 1.2:
            insights['portfolio_role'] = 'Growth'
        else:
            insights['portfolio_role'] = 'Core'
        
        # Allocation recommendation
        recommendation_score = 0
        
        if insights['diversification_benefit'] == 'High':
            recommendation_score += 2
        elif insights['diversification_benefit'] == 'Moderate':
            recommendation_score += 1
        
        if insights['timing_signal'] == 'Overweight':
            recommendation_score += 2
        elif insights['timing_signal'] == 'Underweight':
            recommendation_score -= 2
        
        if insights['portfolio_role'] in ['Alpha Generator', 'Defensive']:
            recommendation_score += 1
        
        if recommendation_score >= 3:
            insights['allocation_recommendation'] = 'Overweight'
        elif recommendation_score <= -1:
            insights['allocation_recommendation'] = 'Underweight'
        else:
            insights['allocation_recommendation'] = 'Market Weight'
        
        portfolio_insights[company_name] = insights
    
    return portfolio_insights


def _create_portfolio_recommendations_dataframe(portfolio_insights: Dict) -> pd.DataFrame:
    """Create portfolio recommendations DataFrame"""
    
    rows = []
    for company_name, insights in portfolio_insights.items():
        row = {
            'Company': company_name,
            'Diversification Benefit': insights['diversification_benefit'],
            'Timing Signal': insights['timing_signal'],
            'Hedging Effectiveness': insights['hedging_effectiveness'],
            'Portfolio Role': insights['portfolio_role'],
            'Allocation Recommendation': insights['allocation_recommendation']
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def _create_diversification_benefit_chart(portfolio_insights: Dict) -> str:
    """Create diversification benefit distribution chart"""
    
    benefits = [insights['diversification_benefit'] for insights in portfolio_insights.values()]
    benefit_counts = {
        'High': benefits.count('High'),
        'Moderate': benefits.count('Moderate'),
        'Low': benefits.count('Low')
    }
    
    benefit_counts = {k: v for k, v in benefit_counts.items() if v > 0}
    
    colors = {'High': '#10b981', 'Moderate': '#f59e0b', 'Low': '#ef4444'}
    pie_colors = [colors[k] for k in benefit_counts.keys()]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': list(benefit_counts.keys()),
            'values': list(benefit_counts.values()),
            'marker': {'colors': pie_colors},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Diversification Benefit Distribution', 'font': {'size': 16, 'weight': 'bold'}}
        }
    }
    
    return build_plotly_chart(fig_data, "diversification-benefit-chart", 400)


def _create_portfolio_role_chart(portfolio_insights: Dict) -> str:
    """Create portfolio role distribution chart"""
    
    roles = [insights['portfolio_role'] for insights in portfolio_insights.values()]
    role_counts = {}
    for role in ['Defensive', 'Alpha Generator', 'Growth', 'Core']:
        count = roles.count(role)
        if count > 0:
            role_counts[role] = count
    
    colors = {
        'Defensive': '#10b981',
        'Alpha Generator': '#8b5cf6',
        'Growth': '#ef4444',
        'Core': '#3b82f6'
    }
    pie_colors = [colors[k] for k in role_counts.keys()]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': list(role_counts.keys()),
            'values': list(role_counts.values()),
            'marker': {'colors': pie_colors},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Portfolio Role Distribution', 'font': {'size': 16, 'weight': 'bold'}}
        }
    }
    
    return build_plotly_chart(fig_data, "portfolio-role-chart", 400)


def _create_timing_signals_chart(portfolio_insights: Dict) -> str:
    """Create timing signals chart"""
    
    companies = list(portfolio_insights.keys())
    
    # Create numeric values for signals
    signal_values = []
    colors = []
    for insights in portfolio_insights.values():
        if insights['timing_signal'] == 'Overweight':
            signal_values.append(1)
            colors.append('#10b981')
        elif insights['timing_signal'] == 'Underweight':
            signal_values.append(-1)
            colors.append('#ef4444')
        else:
            signal_values.append(0)
            colors.append('#f59e0b')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': signal_values,
            'marker': {'color': colors},
            'text': [portfolio_insights[c]['timing_signal'] for c in companies],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Signal: %{text}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Market Timing Signals', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {
                'title': 'Signal',
                'tickvals': [-1, 0, 1],
                'ticktext': ['Underweight', 'Neutral', 'Overweight'],
                'zeroline': True,
                'zerolinewidth': 2
            }
        }
    }
    
    return build_plotly_chart(fig_data, "timing-signals-chart", 500)


def _create_allocation_recommendations_chart(portfolio_insights: Dict) -> str:
    """Create allocation recommendations chart"""
    
    companies = list(portfolio_insights.keys())
    
    # Create numeric values for recommendations
    rec_values = []
    colors = []
    for insights in portfolio_insights.values():
        if insights['allocation_recommendation'] == 'Overweight':
            rec_values.append(1.5)
            colors.append('#10b981')
        elif insights['allocation_recommendation'] == 'Underweight':
            rec_values.append(0.5)
            colors.append('#ef4444')
        else:
            rec_values.append(1.0)
            colors.append('#3b82f6')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': rec_values,
            'marker': {'color': colors},
            'text': [portfolio_insights[c]['allocation_recommendation'] for c in companies],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Recommendation: %{text}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Allocation Recommendations', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {
                'title': 'Relative Weight',
                'tickvals': [0.5, 1.0, 1.5],
                'ticktext': ['Underweight', 'Market Weight', 'Overweight']
            },
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 1.0,
                'y1': 1.0,
                'line': {'color': 'black', 'width': 2, 'dash': 'dash'}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, "allocation-recommendations-chart", 500)


def _create_risk_return_positioning_chart(portfolio_insights: Dict, risk_analysis: Dict,
                                          performance_analysis: Dict) -> str:
    """Create risk-return positioning scatter chart"""
    
    companies = list(portfolio_insights.keys())
    
    risks = []
    returns = []
    roles = []
    
    for company in companies:
        if company in risk_analysis and company in performance_analysis:
            risks.append(risk_analysis[company]['total_risk'] * 100)
            returns.append(performance_analysis[company]['alpha'] * 100)
            roles.append(portfolio_insights[company]['portfolio_role'])
    
    # Create traces for each role
    role_colors = {
        'Defensive': '#10b981',
        'Alpha Generator': '#8b5cf6',
        'Growth': '#ef4444',
        'Core': '#3b82f6'
    }
    
    traces = []
    for role, color in role_colors.items():
        role_companies = [c for c in companies if portfolio_insights[c]['portfolio_role'] == role]
        if not role_companies:
            continue
        
        role_risks = [risk_analysis[c]['total_risk'] * 100 for c in role_companies if c in risk_analysis]
        role_returns = [performance_analysis[c]['alpha'] * 100 for c in role_companies if c in performance_analysis]
        role_labels = [c[:10] for c in role_companies]
        
        traces.append({
            'type': 'scatter',
            'mode': 'markers+text',
            'name': role,
            'x': role_risks,
            'y': role_returns,
            'text': role_labels,
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': color
            },
            'hovertemplate': '<b>%{text}</b><br>Risk: %{x:.1f}%<br>Alpha: %{y:+.1f}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Risk-Return Positioning by Portfolio Role', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Total Risk (%)', 'zeroline': False},
            'yaxis': {'title': 'Alpha (%)', 'zeroline': True, 'zerolinewidth': 2},
            'hovermode': 'closest',
            'showlegend': True
        }
    }
    
    return build_plotly_chart(fig_data, "risk-return-positioning-chart", 500)


def _generate_portfolio_insights_summary(portfolio_insights: Dict, high_diversification: int,
                                        overweight_signals: int, defensive_roles: int,
                                        alpha_generators: int) -> str:
    """Generate portfolio construction insights summary"""
    
    total = len(portfolio_insights)
    
    insights = f"""
    <h4>Key Portfolio Construction Insights:</h4>
    <ul>
        <li><strong>Diversification Profile:</strong> {high_diversification}/{total} companies offer high diversification benefits 
        through significant idiosyncratic risk components, enabling effective portfolio risk reduction.</li>
        
        <li><strong>Timing Opportunities:</strong> {overweight_signals}/{total} companies show positive timing signals, 
        suggesting {'attractive' if overweight_signals > total * 0.4 else 'selective'} tactical overweight opportunities.</li>
        
        <li><strong>Portfolio Balance:</strong> Portfolio includes {defensive_roles} defensive positions, {alpha_generators} 
        alpha generators, providing a {'well-balanced' if defensive_roles + alpha_generators > total * 0.4 else 'growth-oriented'} 
        risk-return profile.</li>
        
        <li><strong>Role-Based Allocation:</strong> Each company's portfolio role reflects its unique characteristics:
            <ul>
                <li><strong>Defensive:</strong> Lower downside beta, suitable for stability</li>
                <li><strong>Alpha Generator:</strong> Consistent positive alpha, focus positions</li>
                <li><strong>Growth:</strong> High beta, market amplification</li>
                <li><strong>Core:</strong> Market-like exposure, foundational holdings</li>
            </ul>
        </li>
    </ul>
    
    <h4>Implementation Framework:</h4>
    <ul>
        <li><strong>Overweight Positions:</strong> Concentrate in companies with high diversification + positive timing signals</li>
        <li><strong>Market Weight:</strong> Maintain exposure to well-diversified core holdings</li>
        <li><strong>Underweight:</strong> Reduce positions with low diversification + negative timing signals</li>
        <li><strong>Defensive Allocation:</strong> Increase defensive positions during market uncertainty</li>
    </ul>
    """
    
    return insights


"""
Section 16 - Step 4: Subsections 16G and 16H (Final)
Replace the stubbed functions in section_16.py with these implementations
"""

# =============================================================================
# SECTION 16G: COMPREHENSIVE DASHBOARD
# =============================================================================

def _build_section_16g_dashboard(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                companies: Dict[str, str]) -> str:
    """Build Section 16G: Comprehensive Multi-Dimensional Dashboard"""
    
    # Gather all analyses
    beta_analysis = _calculate_enhanced_beta_metrics(daily_prices, sp500_daily, companies)
    
    if not beta_analysis:
        return build_info_box("<p>Insufficient data for dashboard.</p>", "warning", "16G. Dashboard")
    
    monthly_prices = daily_prices  # Simplified for dashboard
    sp500_monthly = sp500_daily
    
    performance_analysis = _calculate_performance_metrics(
        daily_prices, monthly_prices, sp500_daily, sp500_monthly, companies
    )
    risk_analysis = _calculate_risk_metrics(daily_prices, sp500_daily, companies, beta_analysis)
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16g')">
            <h2>16G. Comprehensive Benchmark Intelligence Dashboard</h2>
            <span class="toggle-icon" id="section16g-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16g-content">
    """
    
    # Multi-Dimensional Portfolio Metrics
    html += "<h3>Multi-Dimensional Portfolio View</h3>"
    
    # Performance Metrics
    html += "<h4>Performance Metrics</h4>"
    perf_cards = _create_performance_metrics_cards(performance_analysis, sp500_daily)
    html += build_stat_grid(perf_cards)
    
    # Risk Metrics
    html += "<h4>Risk Metrics</h4>"
    risk_cards = _create_risk_metrics_cards(risk_analysis, sp500_daily)
    html += build_stat_grid(risk_cards)
    
    # Efficiency Metrics
    html += "<h4>Efficiency Metrics</h4>"
    efficiency_cards = _create_efficiency_metrics_cards(performance_analysis, risk_analysis)
    html += build_stat_grid(efficiency_cards)
    
    # Positioning Metrics
    html += "<h4>Positioning Metrics</h4>"
    positioning_cards = _create_positioning_metrics_cards(beta_analysis, performance_analysis)
    html += build_stat_grid(positioning_cards)
    
    # Chart 1: 4-Quadrant Risk-Alpha Positioning
    html += "<h3>Portfolio Positioning Analysis</h3>"
    html += _create_risk_alpha_quadrant_chart(beta_analysis, performance_analysis, risk_analysis)
    
    # Chart 2: Performance Attribution
    html += _create_performance_attribution_chart(beta_analysis, performance_analysis)
    
    # Chart 3: Multi-Factor Dashboard
    html += _create_multifactor_dashboard_chart(
        beta_analysis, performance_analysis, risk_analysis, companies
    )
    
    # Portfolio-Level Summary Table
    html += "<h3>Portfolio-Level Statistics Summary</h3>"
    portfolio_summary_df = _create_portfolio_summary_dataframe(
        beta_analysis, performance_analysis, risk_analysis, sp500_daily
    )
    html += build_data_table(portfolio_summary_df, "portfolio-summary-16g", sortable=False)
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_performance_metrics_cards(performance_analysis: Dict, sp500_daily: pd.DataFrame) -> List[Dict]:
    """Create performance metrics cards"""
    
    if not performance_analysis:
        return []
    
    # Calculate portfolio-level metrics
    avg_alpha = np.mean([a['alpha'] for a in performance_analysis.values()])
    total_return = np.mean([a['annual_return'] for a in performance_analysis.values()])
    sp500_return = performance_analysis[list(performance_analysis.keys())[0]]['sp500_annual_return']
    positive_alpha_pct = sum(1 for a in performance_analysis.values() if a['alpha'] > 0) / len(performance_analysis)
    
    cards = [
        {
            "label": "Portfolio Return",
            "value": f"{total_return*100:.1f}%",
            "description": "Average annual return",
            "type": "info"
        },
        {
            "label": "S&P 500 Return",
            "value": f"{sp500_return*100:.1f}%",
            "description": "Benchmark return",
            "type": "default"
        },
        {
            "label": "Portfolio Alpha",
            "value": f"{avg_alpha*100:+.1f}%",
            "description": "Excess vs benchmark",
            "type": "success" if avg_alpha > 0 else "danger"
        },
        {
            "label": "Outperformance Rate",
            "value": f"{positive_alpha_pct*100:.0f}%",
            "description": "% positions beating SPX",
            "type": "success" if positive_alpha_pct > 0.5 else "warning"
        }
    ]
    
    return cards


def _create_risk_metrics_cards(risk_analysis: Dict, sp500_daily: pd.DataFrame) -> List[Dict]:
    """Create risk metrics cards"""
    
    if not risk_analysis:
        return []
    
    # Calculate portfolio-level risk metrics
    avg_total_risk = np.mean([a['total_risk'] for a in risk_analysis.values()])
    sp500_returns = sp500_daily['close'].pct_change().dropna()
    market_risk = sp500_returns.std() * np.sqrt(252)
    avg_max_dd = np.mean([a['max_drawdown'] for a in risk_analysis.values()])
    avg_downside_dev = np.mean([a['downside_deviation'] for a in risk_analysis.values()])
    
    cards = [
        {
            "label": "Portfolio Risk",
            "value": f"{avg_total_risk*100:.1f}%",
            "description": "Average volatility",
            "type": "info"
        },
        {
            "label": "Market Risk",
            "value": f"{market_risk*100:.1f}%",
            "description": "S&P 500 volatility",
            "type": "default"
        },
        {
            "label": "Avg Max Drawdown",
            "value": f"{avg_max_dd*100:.1f}%",
            "description": "Peak to trough",
            "type": "warning" if avg_max_dd < -0.20 else "success"
        },
        {
            "label": "Downside Deviation",
            "value": f"{avg_downside_dev*100:.1f}%",
            "description": "Downside volatility",
            "type": "info"
        }
    ]
    
    return cards


def _create_efficiency_metrics_cards(performance_analysis: Dict, risk_analysis: Dict) -> List[Dict]:
    """Create efficiency metrics cards"""
    
    if not performance_analysis or not risk_analysis:
        return []
    
    # Calculate efficiency metrics
    avg_sharpe = np.mean([risk_analysis[c]['sharpe_ratio'] 
                         for c in performance_analysis.keys() if c in risk_analysis])
    avg_sortino = np.mean([risk_analysis[c]['sortino_ratio'] 
                          for c in performance_analysis.keys() if c in risk_analysis])
    avg_info_ratio = np.mean([a['information_ratio'] for a in performance_analysis.values()])
    
    # Calculate up/down capture (approximate)
    up_capture = 1.0  # Placeholder
    down_capture = 1.0  # Placeholder
    
    cards = [
        {
            "label": "Sharpe Ratio",
            "value": f"{avg_sharpe:.2f}",
            "description": "Return per unit risk",
            "type": "success" if avg_sharpe > 1.0 else "info"
        },
        {
            "label": "Sortino Ratio",
            "value": f"{avg_sortino:.2f}",
            "description": "Return per downside risk",
            "type": "success" if avg_sortino > 1.0 else "info"
        },
        {
            "label": "Information Ratio",
            "value": f"{avg_info_ratio:.2f}",
            "description": "Alpha per tracking error",
            "type": "success" if avg_info_ratio > 0.5 else "info"
        },
        {
            "label": "Win Rate",
            "value": f"{sum(1 for a in performance_analysis.values() if a['alpha'] > 0) / len(performance_analysis) * 100:.0f}%",
            "description": "Positions with positive alpha",
            "type": "success"
        }
    ]
    
    return cards


def _create_positioning_metrics_cards(beta_analysis: Dict, performance_analysis: Dict) -> List[Dict]:
    """Create positioning metrics cards"""
    
    if not beta_analysis:
        return []
    
    # Calculate positioning metrics
    avg_beta = np.mean([a['current_beta'] for a in beta_analysis.values()])
    avg_correlation = np.mean([a['correlation_full'] for a in beta_analysis.values()])
    avg_tracking_error = np.mean([a['tracking_error'] for a in performance_analysis.values()]) if performance_analysis else 0
    
    cards = [
        {
            "label": "Portfolio Beta",
            "value": f"{avg_beta:.2f}",
            "description": "Market sensitivity",
            "type": "info" if 0.8 <= avg_beta <= 1.2 else "warning"
        },
        {
            "label": "Correlation to SPX",
            "value": f"{avg_correlation:.2f}",
            "description": "Market relationship",
            "type": "info"
        },
        {
            "label": "Tracking Error",
            "value": f"{avg_tracking_error*100:.1f}%",
            "description": "Active risk",
            "type": "info"
        },
        {
            "label": "Active Positions",
            "value": f"{len(beta_analysis)}",
            "description": "Companies analyzed",
            "type": "default"
        }
    ]
    
    return cards


def _create_risk_alpha_quadrant_chart(beta_analysis: Dict, performance_analysis: Dict,
                                      risk_analysis: Dict) -> str:
    """Create 4-quadrant risk-alpha positioning chart"""
    
    companies = list(beta_analysis.keys())
    
    risks = []
    alphas = []
    labels = []
    colors = []
    
    for company in companies:
        if company in risk_analysis and company in performance_analysis:
            risks.append(risk_analysis[company]['total_risk'] * 100)
            alphas.append(performance_analysis[company]['alpha'] * 100)
            labels.append(company[:10])
            
            # Color by quadrant
            risk = risk_analysis[company]['total_risk'] * 100
            alpha = performance_analysis[company]['alpha'] * 100
            avg_risk = np.mean([r['total_risk'] * 100 for r in risk_analysis.values()])
            
            if alpha > 0 and risk < avg_risk:
                colors.append('#10b981')  # Efficient outperformers (green)
            elif alpha > 0 and risk >= avg_risk:
                colors.append('#8b5cf6')  # Alpha generators (purple)
            elif alpha <= 0 and risk < avg_risk:
                colors.append('#3b82f6')  # Defensive (blue)
            else:
                colors.append('#ef4444')  # Aggressive underperformers (red)
    
    if not risks or not alphas:
        return ""
    
    avg_risk = np.mean(risks)
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': risks,
            'y': alphas,
            'text': labels,
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Risk: %{x:.1f}%<br>Alpha: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Portfolio Positioning: Risk vs Alpha Quadrant Analysis', 
                     'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Total Risk (%)', 'zeroline': False},
            'yaxis': {'title': 'Alpha (%)', 'zeroline': True, 'zerolinewidth': 2},
            'shapes': [
                {
                    'type': 'line',
                    'x0': avg_risk,
                    'x1': avg_risk,
                    'y0': min(alphas) * 1.2,
                    'y1': max(alphas) * 1.2,
                    'line': {'color': 'gray', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': min(risks) * 0.8,
                    'x1': max(risks) * 1.2,
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'gray', 'width': 2, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {
                    'x': max(risks) * 1.1,
                    'y': max(alphas) * 1.1,
                    'text': 'Alpha Generators<br>(High Risk/High Return)',
                    'showarrow': False,
                    'font': {'size': 10, 'color': '#8b5cf6'}
                },
                {
                    'x': min(risks) * 0.9,
                    'y': max(alphas) * 1.1,
                    'text': 'Efficient<br>Outperformers',
                    'showarrow': False,
                    'font': {'size': 10, 'color': '#10b981'}
                },
                {
                    'x': min(risks) * 0.9,
                    'y': min(alphas) * 1.1,
                    'text': 'Defensive<br>Positions',
                    'showarrow': False,
                    'font': {'size': 10, 'color': '#3b82f6'}
                },
                {
                    'x': max(risks) * 1.1,
                    'y': min(alphas) * 1.1,
                    'text': 'Aggressive<br>Underperformers',
                    'showarrow': False,
                    'font': {'size': 10, 'color': '#ef4444'}
                }
            ],
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, "risk-alpha-quadrant", 600)


def _create_performance_attribution_chart(beta_analysis: Dict, performance_analysis: Dict) -> str:
    """Create performance attribution chart"""
    
    companies = list(beta_analysis.keys())
    
    if not performance_analysis:
        return ""
    
    # Calculate components
    betas = [beta_analysis[c]['current_beta'] for c in companies]
    alphas = [performance_analysis[c]['alpha'] * 100 for c in companies if c in performance_analysis]
    
    # Market return contribution (beta * market return)
    sp500_return = performance_analysis[companies[0]]['sp500_annual_return'] * 100 if companies and companies[0] in performance_analysis else 0
    market_contrib = [b * sp500_return for b in betas[:len(alphas)]]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Market Contribution',
                'x': companies[:len(alphas)],
                'y': market_contrib,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Market: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Alpha (Stock Selection)',
                'x': companies[:len(alphas)],
                'y': alphas,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Alpha: %{y:+.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Performance Attribution: Market vs Alpha', 
                     'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Return Contribution (%)', 'zeroline': True},
            'barmode': 'relative',
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, "performance-attribution", 500)


def _create_multifactor_dashboard_chart(beta_analysis: Dict, performance_analysis: Dict,
                                        risk_analysis: Dict, companies: Dict[str, str]) -> str:
    """Create multi-factor radar/spider chart for portfolio overview"""
    
    if not all([beta_analysis, performance_analysis, risk_analysis]):
        return ""
    
    # Calculate normalized scores for each factor (0-10 scale)
    companies_list = list(beta_analysis.keys())
    
    # Collect metrics
    metrics = {
        'Beta Alignment': [],
        'Alpha Generation': [],
        'Risk Efficiency': [],
        'Diversification': [],
        'Momentum': []
    }
    
    for company in companies_list:
        # Beta alignment (closer to 1.0 is better, scale to 0-10)
        beta_score = 10 - min(10, abs(beta_analysis[company]['current_beta'] - 1.0) * 10)
        metrics['Beta Alignment'].append(beta_score)
        
        # Alpha generation (scale alpha to 0-10)
        if company in performance_analysis:
            alpha = performance_analysis[company]['alpha']
            alpha_score = min(10, max(0, (alpha * 100 + 5)))
            metrics['Alpha Generation'].append(alpha_score)
        else:
            metrics['Alpha Generation'].append(5)
        
        # Risk efficiency (Sharpe ratio scaled)
        if company in risk_analysis:
            sharpe = risk_analysis[company]['sharpe_ratio']
            risk_score = min(10, max(0, sharpe * 2.5 + 5))
            metrics['Risk Efficiency'].append(risk_score)
        else:
            metrics['Risk Efficiency'].append(5)
        
        # Diversification (idiosyncratic % scaled)
        if company in risk_analysis:
            idio_pct = risk_analysis[company]['idiosyncratic_pct']
            div_score = idio_pct * 10
            metrics['Diversification'].append(div_score)
        else:
            metrics['Diversification'].append(5)
        
        # Momentum (relative strength scaled)
        if company in performance_analysis:
            rel_strength = performance_analysis[company].get('relative_strength', 0)
            momentum_score = min(10, max(0, (rel_strength * 100 + 5)))
            metrics['Momentum'].append(momentum_score)
        else:
            metrics['Momentum'].append(5)
    
    # Calculate portfolio averages
    avg_scores = {k: np.mean(v) for k, v in metrics.items()}
    
    # Create radar chart
    categories = list(avg_scores.keys())
    values = list(avg_scores.values())
    values.append(values[0])  # Close the radar
    categories_closed = categories + [categories[0]]
    
    fig_data = {
        'data': [{
            'type': 'scatterpolar',
            'r': values,
            'theta': categories_closed,
            'fill': 'toself',
            'fillcolor': 'rgba(102, 126, 234, 0.3)',
            'line': {'color': '#667eea', 'width': 3},
            'marker': {'size': 8, 'color': '#667eea'},
            'hovertemplate': '<b>%{theta}</b><br>Score: %{r:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Portfolio Multi-Factor Profile', 'font': {'size': 16, 'weight': 'bold'}},
            'polar': {
                'radialaxis': {
                    'visible': True,
                    'range': [0, 10],
                    'tickmode': 'linear',
                    'tick0': 0,
                    'dtick': 2
                }
            },
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, "multifactor-dashboard", 500)


def _create_portfolio_summary_dataframe(beta_analysis: Dict, performance_analysis: Dict,
                                        risk_analysis: Dict, sp500_daily: pd.DataFrame) -> pd.DataFrame:
    """Create portfolio-level summary statistics DataFrame"""
    
    # Calculate S&P 500 metrics
    sp500_returns = sp500_daily['close'].pct_change().dropna()
    sp500_vol = sp500_returns.std() * np.sqrt(252)
    sp500_return = sp500_returns.mean() * 252
    
    # Portfolio metrics
    data = {
        'Metric Category': [],
        'Metric': [],
        'Portfolio': [],
        'S&P 500': [],
        'Difference': []
    }
    
    # Performance metrics
    if performance_analysis:
        avg_return = np.mean([a['annual_return'] for a in performance_analysis.values()])
        avg_alpha = np.mean([a['alpha'] for a in performance_analysis.values()])
        
        data['Metric Category'].extend(['Performance', 'Performance'])
        data['Metric'].extend(['Annual Return', 'Alpha'])
        data['Portfolio'].extend([f"{avg_return*100:.1f}%", f"{avg_alpha*100:+.1f}%"])
        data['S&P 500'].extend([f"{sp500_return*100:.1f}%", "0.0%"])
        data['Difference'].extend([f"{(avg_return - sp500_return)*100:+.1f}%", f"{avg_alpha*100:+.1f}%"])
    
    # Risk metrics
    if risk_analysis:
        avg_vol = np.mean([a['total_risk'] for a in risk_analysis.values()])
        avg_max_dd = np.mean([a['max_drawdown'] for a in risk_analysis.values()])
        
        data['Metric Category'].extend(['Risk', 'Risk'])
        data['Metric'].extend(['Volatility', 'Max Drawdown'])
        data['Portfolio'].extend([f"{avg_vol*100:.1f}%", f"{avg_max_dd*100:.1f}%"])
        data['S&P 500'].extend([f"{sp500_vol*100:.1f}%", "N/A"])
        data['Difference'].extend([f"{(avg_vol - sp500_vol)*100:+.1f}%", "N/A"])
    
    # Efficiency metrics
    if risk_analysis and performance_analysis:
        avg_sharpe = np.mean([risk_analysis[c]['sharpe_ratio'] 
                             for c in performance_analysis.keys() if c in risk_analysis])
        avg_info_ratio = np.mean([a['information_ratio'] for a in performance_analysis.values()])
        
        data['Metric Category'].extend(['Efficiency', 'Efficiency'])
        data['Metric'].extend(['Sharpe Ratio', 'Information Ratio'])
        data['Portfolio'].extend([f"{avg_sharpe:.2f}", f"{avg_info_ratio:.2f}"])
        data['S&P 500'].extend(["N/A", "N/A"])
        data['Difference'].extend(["N/A", "N/A"])
    
    # Positioning metrics
    if beta_analysis:
        avg_beta = np.mean([a['current_beta'] for a in beta_analysis.values()])
        avg_corr = np.mean([a['correlation_full'] for a in beta_analysis.values()])
        
        data['Metric Category'].extend(['Positioning', 'Positioning'])
        data['Metric'].extend(['Beta', 'Correlation'])
        data['Portfolio'].extend([f"{avg_beta:.2f}", f"{avg_corr:.2f}"])
        data['S&P 500'].extend(["1.00", "1.00"])
        data['Difference'].extend([f"{avg_beta - 1.0:+.2f}", f"{avg_corr - 1.0:+.2f}"])
    
    return pd.DataFrame(data)


# =============================================================================
# SECTION 16H: STRATEGIC FRAMEWORK (NEW FORMAT)
# =============================================================================

def _build_section_16h_strategic_framework(daily_prices: pd.DataFrame, sp500_daily: pd.DataFrame,
                                          companies: Dict[str, str]) -> str:
    """Build Section 16H: Strategic Benchmark Intelligence Framework (New Format)"""
    
    # Gather all analyses
    beta_analysis = _calculate_enhanced_beta_metrics(daily_prices, sp500_daily, companies)
    
    if not beta_analysis:
        return build_info_box("<p>Insufficient data for strategic framework.</p>", "warning", "16H. Strategic Framework")
    
    monthly_prices = daily_prices
    sp500_monthly = sp500_daily
    
    performance_analysis = _calculate_performance_metrics(
        daily_prices, monthly_prices, sp500_daily, sp500_monthly, companies
    )
    risk_analysis = _calculate_risk_metrics(daily_prices, sp500_daily, companies, beta_analysis)
    regime_analysis = _calculate_regime_metrics(daily_prices, sp500_daily, companies)
    portfolio_insights = _calculate_portfolio_insights(
        beta_analysis, performance_analysis, risk_analysis, companies
    )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section16h')">
            <h2>16H. Strategic Benchmark Intelligence Framework</h2>
            <span class="toggle-icon" id="section16h-icon">▼</span>
        </div>
        <div class="subsection-content" id="section16h-content">
    """
    
    # 16H.1: Portfolio Positioning Summary
    html += _build_16h1_positioning_summary(
        beta_analysis, performance_analysis, risk_analysis
    )
    
    # 16H.2: Factor Analysis Dashboard
    html += _build_16h2_factor_analysis(
        beta_analysis, performance_analysis, risk_analysis, regime_analysis
    )
    
    # 16H.3: Strategic Opportunities
    html += _build_16h3_strategic_opportunities(
        portfolio_insights, performance_analysis, risk_analysis
    )
    
    # 16H.4: Portfolio Optimization Scenarios
    html += _build_16h4_optimization_scenarios(
        beta_analysis, performance_analysis, risk_analysis
    )
    
    html += """
        </div>
    </div>
    """
    
    return html


def _build_16h1_positioning_summary(beta_analysis: Dict, performance_analysis: Dict,
                                    risk_analysis: Dict) -> str:
    """Build 16H.1: Portfolio Positioning Summary with stat cards"""
    
    html = "<h3>16H.1 Portfolio Positioning Summary</h3>"
    
    # Calculate key metrics
    avg_beta = np.mean([a['current_beta'] for a in beta_analysis.values()])
    avg_alpha = np.mean([a['alpha'] for a in performance_analysis.values()]) * 100 if performance_analysis else 0
    avg_sharpe = np.mean([a['sharpe_ratio'] for a in risk_analysis.values()]) if risk_analysis else 0
    avg_systematic = np.mean([a['systematic_pct'] for a in risk_analysis.values()]) * 100 if risk_analysis else 50
    
    # Determine positioning
    beta_position = "Aggressive" if avg_beta > 1.15 else "Defensive" if avg_beta < 0.85 else "Neutral"
    alpha_position = "Strong" if avg_alpha > 3 else "Moderate" if avg_alpha > 0 else "Weak"
    risk_position = "Efficient" if avg_sharpe > 0.8 else "Balanced" if avg_sharpe > 0.4 else "Inefficient"
    diversification = "High" if avg_systematic < 60 else "Moderate" if avg_systematic < 75 else "Low"
    
    cards = [
        {
            "label": "Market Positioning",
            "value": beta_position,
            "description": f"Beta: {avg_beta:.2f}",
            "type": "info" if beta_position == "Neutral" else "warning"
        },
        {
            "label": "Alpha Generation",
            "value": alpha_position,
            "description": f"Average: {avg_alpha:+.1f}%",
            "type": "success" if alpha_position == "Strong" else "info"
        },
        {
            "label": "Risk Efficiency",
            "value": risk_position,
            "description": f"Sharpe: {avg_sharpe:.2f}",
            "type": "success" if risk_position == "Efficient" else "warning"
        },
        {
            "label": "Diversification",
            "value": diversification,
            "description": f"Systematic: {avg_systematic:.0f}%",
            "type": "success" if diversification == "High" else "info"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # Directional indicators
    beta_trend = "↑" if avg_beta > 1.0 else "↓" if avg_beta < 1.0 else "→"
    alpha_trend = "↑" if avg_alpha > 0 else "↓"
    
    insight_text = f"""
    <p><strong>Current Positioning:</strong> Portfolio exhibits <strong>{beta_position.lower()}</strong> market positioning 
    with a beta of {avg_beta:.2f} {beta_trend}, generating <strong>{alpha_position.lower()}</strong> alpha at {avg_alpha:+.1f}% {alpha_trend}. 
    Risk-adjusted returns are <strong>{risk_position.lower()}</strong> with a Sharpe ratio of {avg_sharpe:.2f}, 
    and diversification is <strong>{diversification.lower()}</strong> with {avg_systematic:.0f}% systematic risk.</p>
    """
    
    html += build_info_box(insight_text, "info", "Current Position Assessment")
    
    return html


def _build_16h2_factor_analysis(beta_analysis: Dict, performance_analysis: Dict,
                                risk_analysis: Dict, regime_analysis: Dict) -> str:
    """Build 16H.2: Factor Analysis Dashboard with multi-column cards"""
    
    html = "<h3>16H.2 Factor Analysis Dashboard</h3>"
    
    # Beta Exposure Profile
    html += """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
    """
    
    # Card 1: Beta Exposure
    high_beta = sum(1 for a in beta_analysis.values() if a['current_beta'] > 1.2)
    low_beta = sum(1 for a in beta_analysis.values() if a['current_beta'] < 0.8)
    neutral_beta = len(beta_analysis) - high_beta - low_beta
    
    beta_card = f"""
    <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #3b82f6; box-shadow: var(--shadow-sm);">
        <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">📊 Beta Exposure Profile</h4>
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                <span>High Beta (>1.2):</span>
                <strong style="color: #ef4444;">{high_beta} positions</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                <span>Neutral Beta (0.8-1.2):</span>
                <strong style="color: #3b82f6;">{neutral_beta} positions</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                <span>Low Beta (<0.8):</span>
                <strong style="color: #10b981;">{low_beta} positions</strong>
            </div>
        </div>
        <p style="margin-top: 15px; font-size: 0.9rem; color: var(--text-secondary);">
            Portfolio is {'growth-tilted' if high_beta > neutral_beta else 'defensively-positioned' if low_beta > neutral_beta else 'balanced'} 
            with respect to market sensitivity.
        </p>
    </div>
    """
    html += beta_card
    
    # Card 2: Alpha Sources
    if performance_analysis:
        positive_alpha = sum(1 for a in performance_analysis.values() if a['alpha'] > 0)
        strong_alpha = sum(1 for a in performance_analysis.values() if a['alpha'] > 0.05)
        
        alpha_card = f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #10b981; box-shadow: var(--shadow-sm);">
            <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">💎 Alpha Generation Sources</h4>
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Positive Alpha:</span>
                    <strong style="color: #10b981;">{positive_alpha}/{len(performance_analysis)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Strong Alpha (>5%):</span>
                    <strong style="color: #8b5cf6;">{strong_alpha}/{len(performance_analysis)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Success Rate:</span>
                    <strong style="color: #3b82f6;">{positive_alpha/len(performance_analysis)*100:.0f}%</strong>
                </div>
            </div>
            <p style="margin-top: 15px; font-size: 0.9rem; color: var(--text-secondary);">
                {'Excellent' if positive_alpha > len(performance_analysis) * 0.6 else 'Good' if positive_alpha > len(performance_analysis) * 0.4 else 'Moderate'} 
                stock selection with {strong_alpha} strong performers.
            </p>
        </div>
        """
        html += alpha_card
    
    # Card 3: Risk Decomposition
    if risk_analysis:
        high_idio = sum(1 for a in risk_analysis.values() if a['idiosyncratic_pct'] > 0.5)
        avg_systematic = np.mean([a['systematic_pct'] for a in risk_analysis.values()]) * 100
        
        risk_card = f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #f59e0b; box-shadow: var(--shadow-sm);">
            <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">🛡️ Risk Decomposition</h4>
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Avg Systematic Risk:</span>
                    <strong style="color: #ef4444;">{avg_systematic:.0f}%</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>High Diversification:</span>
                    <strong style="color: #10b981;">{high_idio}/{len(risk_analysis)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Diversification Benefit:</span>
                    <strong style="color: #3b82f6;">{'High' if avg_systematic < 60 else 'Moderate' if avg_systematic < 75 else 'Low'}</strong>
                </div>
            </div>
            <p style="margin-top: 15px; font-size: 0.9rem; color: var(--text-secondary);">
                Portfolio offers {'strong' if avg_systematic < 60 else 'moderate' if avg_systematic < 75 else 'limited'} 
                diversification with {100-avg_systematic:.0f}% idiosyncratic risk.
            </p>
        </div>
        """
        html += risk_card
    
    # Card 4: Defensive Characteristics
    if regime_analysis:
        avg_downside_capture = np.mean([a['defensive_metrics']['downside_capture_ratio'] 
                                       for a in regime_analysis.values()])
        defensive_count = sum(1 for a in regime_analysis.values() 
                             if a['defensive_metrics']['downside_capture_ratio'] < 0.9)
        
        defensive_card = f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #8b5cf6; box-shadow: var(--shadow-sm);">
            <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">🛡️ Defensive Characteristics</h4>
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Avg Downside Capture:</span>
                    <strong style="color: {'#10b981' if avg_downside_capture < 0.9 else '#f59e0b'};">{avg_downside_capture:.2f}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Defensive Positions:</span>
                    <strong style="color: #10b981;">{defensive_count}/{len(regime_analysis)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span>Downside Protection:</span>
                    <strong style="color: #3b82f6;">{'Strong' if avg_downside_capture < 0.9 else 'Moderate' if avg_downside_capture < 1.1 else 'Weak'}</strong>
                </div>
            </div>
            <p style="margin-top: 15px; font-size: 0.9rem; color: var(--text-secondary);">
                Portfolio {'provides strong' if avg_downside_capture < 0.9 else 'has moderate' if avg_downside_capture < 1.1 else 'lacks'} 
                downside protection vs market.
            </p>
        </div>
        """
        html += defensive_card
    
    html += "</div>"
    
    return html


def _build_16h3_strategic_opportunities(portfolio_insights: Dict, performance_analysis: Dict,
                                       risk_analysis: Dict) -> str:
    """Build 16H.3: Strategic Opportunities with action cards"""
    
    html = "<h3>16H.3 Strategic Opportunities & Action Items</h3>"
    
    # Identify opportunities
    opportunities = []
    
    # Rebalancing opportunities
    overweight_candidates = [c for c, i in portfolio_insights.items() 
                            if i['allocation_recommendation'] == 'Overweight']
    underweight_candidates = [c for c, i in portfolio_insights.items() 
                             if i['allocation_recommendation'] == 'Underweight']
    
    if overweight_candidates:
        opportunities.append({
            'title': '📈 Rebalancing Opportunities',
            'priority': 'High',
            'action': f"Consider increasing allocation to {len(overweight_candidates)} positions",
            'positions': ', '.join(overweight_candidates[:3]) + ('...' if len(overweight_candidates) > 3 else ''),
            'rationale': 'Strong diversification benefits + positive timing signals',
            'color': '#10b981'
        })
    
    # Alpha concentration opportunities
    if performance_analysis:
        top_alpha_generators = sorted(
            [(c, a['alpha']) for c, a in performance_analysis.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_alpha_generators and top_alpha_generators[0][1] > 0.05:
            opportunities.append({
                'title': '💎 Alpha Concentration',
                'priority': 'Medium',
                'action': f"Concentrate positions in top alpha generators",
                'positions': ', '.join([c for c, _ in top_alpha_generators]),
                'rationale': f'Consistent outperformance with alpha > 5%',
                'color': '#8b5cf6'
            })
    
    # Risk reduction opportunities
    if risk_analysis:
        high_risk_positions = [c for c, r in risk_analysis.items() 
                              if r['max_drawdown'] < -0.30]
        
        if high_risk_positions:
            opportunities.append({
                'title': '🛡️ Risk Reduction',
                'priority': 'High',
                'action': f"Review {len(high_risk_positions)} high-risk positions",
                'positions': ', '.join(high_risk_positions[:3]) + ('...' if len(high_risk_positions) > 3 else ''),
                'rationale': 'Maximum drawdown > 30%, consider hedging or position sizing',
                'color': '#ef4444'
            })
    
    # Defensive positioning
    defensive_positions = [c for c, i in portfolio_insights.items() 
                          if i['portfolio_role'] == 'Defensive']
    
    if defensive_positions and len(defensive_positions) < len(portfolio_insights) * 0.3:
        opportunities.append({
            'title': '🔰 Defensive Enhancement',
            'priority': 'Medium',
            'action': f"Add defensive exposure ({len(defensive_positions)}/{len(portfolio_insights)} currently)",
            'positions': 'Consider increasing allocation to existing defensive positions',
            'rationale': 'Portfolio could benefit from additional downside protection',
            'color': '#3b82f6'
        })
    
    # Render opportunity cards
    html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin: 20px 0;">'
    
    for opp in opportunities:
        priority_colors = {'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'}
        priority_color = priority_colors.get(opp['priority'], '#3b82f6')
        
        card = f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; 
                    border-left: 4px solid {opp['color']}; box-shadow: var(--shadow-md);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0; color: var(--text-primary);">{opp['title']}</h4>
                <span style="background: {priority_color}; color: white; padding: 4px 12px; 
                           border-radius: 12px; font-size: 0.85rem; font-weight: 600;">
                    {opp['priority']} Priority
                </span>
            </div>
            <div style="margin: 15px 0;">
                <p style="margin: 8px 0; font-weight: 600; color: var(--text-primary);">
                    <strong>Action:</strong> {opp['action']}
                </p>
                <p style="margin: 8px 0; font-size: 0.9rem; color: var(--text-secondary);">
                    <strong>Positions:</strong> {opp['positions']}
                </p>
                <p style="margin: 8px 0; font-size: 0.9rem; color: var(--text-secondary);">
                    <strong>Rationale:</strong> {opp['rationale']}
                </p>
            </div>
        </div>
        """
        html += card
    
    html += '</div>'
    
    return html


def _build_16h4_optimization_scenarios(beta_analysis: Dict, performance_analysis: Dict,
                                      risk_analysis: Dict) -> str:
    """Build 16H.4: Portfolio Optimization Scenarios"""
    
    html = "<h3>16H.4 Portfolio Optimization Scenarios</h3>"
    
    # Current portfolio metrics
    current_beta = np.mean([a['current_beta'] for a in beta_analysis.values()])
    current_alpha = np.mean([a['alpha'] for a in performance_analysis.values()]) if performance_analysis else 0
    current_risk = np.mean([a['total_risk'] for a in risk_analysis.values()]) if risk_analysis else 0
    
    # Define scenarios
    scenarios = [
        {
            'name': 'Reduce Beta by 0.1',
            'change': 'Beta',
            'delta': -0.1,
            'impact': {
                'Beta': f"{current_beta:.2f} → {current_beta - 0.1:.2f}",
                'Expected Alpha Impact': f"{current_alpha*100:.1f}% → {current_alpha*100:.1f}%",
                'Expected Risk': f"{current_risk*100:.1f}% → {(current_risk * 0.95)*100:.1f}%"
            },
            'recommendation': 'Shift allocation toward lower-beta positions for defensive positioning'
        },
        {
            'name': 'Increase Alpha Focus',
            'change': 'Concentration',
            'delta': 0,
            'impact': {
                'Top 3 Weight': '15% → 25%',
                'Expected Alpha': f"{current_alpha*100:.1f}% → {(current_alpha * 1.3)*100:.1f}%",
                'Concentration Risk': 'Moderate → High'
            },
            'recommendation': 'Concentrate in top alpha generators, accept higher concentration risk'
        },
        {
            'name': 'Increase Diversification',
            'change': 'Risk Reduction',
            'delta': 0,
            'impact': {
                'Idiosyncratic Risk': 'Current level → +10%',
                'Total Risk': f"{current_risk*100:.1f}% → {(current_risk * 0.90)*100:.1f}%",
                'Risk-Adjusted Return': 'Improved'
            },
            'recommendation': 'Add positions with high idiosyncratic risk for better diversification'
        }
    ]
    
    # Render scenario cards
    html += '<div style="margin: 20px 0;">'
    
    for scenario in scenarios:
        card = f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; 
                    margin: 15px 0; border-left: 4px solid #667eea; box-shadow: var(--shadow-sm);">
            <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">
                💡 Scenario: {scenario['name']}
            </h4>
            <div style="background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">Expected Impact:</h5>
        """
        
        for metric, value in scenario['impact'].items():
            card += f"""
                <div style="display: flex; justify-content: space-between; margin: 8px 0; padding: 5px 0;">
                    <span style="color: var(--text-secondary);">{metric}:</span>
                    <strong style="color: var(--text-primary);">{value}</strong>
                </div>
            """
        
        card += f"""
            </div>
            <div style="margin-top: 15px; padding: 12px; background: rgba(16, 185, 129, 0.1); 
                       border-radius: 8px; border-left: 3px solid #10b981;">
                <strong style="color: var(--text-primary);">Recommendation:</strong>
                <p style="margin: 5px 0 0 0; color: var(--text-secondary);">{scenario['recommendation']}</p>
            </div>
        </div>
        """
        html += card
    
    html += '</div>'
    
    # Add summary insight
    summary = f"""
    <p><strong>Optimization Summary:</strong> Current portfolio positioning with {current_beta:.2f} beta 
    and {current_alpha*100:.1f}% alpha provides a baseline for tactical adjustments. Consider the scenarios above 
    based on market outlook and risk tolerance. Each scenario involves trade-offs between risk, return, and 
    concentration that should align with investment objectives.</p>
    """
    
    html += build_info_box(summary, "info", "Portfolio Optimization Guidance")
    
    return html


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _simulate_benchmark_data(price_data: pd.DataFrame) -> pd.DataFrame:
    """Simulate S&P 500 data if not available"""
    if price_data.empty:
        return pd.DataFrame()
    
    dates = price_data['date'].unique()
    benchmark_data = []
    
    for date in dates:
        day_data = price_data[price_data['date'] == date]
        if not day_data.empty:
            benchmark_data.append({
                'date': date,
                'symbol': '^GSPC',
                'close': day_data['close'].mean(),
                'open': day_data['open'].mean() if 'open' in day_data.columns else day_data['close'].mean(),
                'high': day_data['high'].mean() if 'high' in day_data.columns else day_data['close'].mean(),
                'low': day_data['low'].mean() if 'low' in day_data.columns else day_data['close'].mean(),
                'volume': day_data['volume'].sum() if 'volume' in day_data.columns else 1000000
            })
    
    return pd.DataFrame(benchmark_data)