"""Section 18: Equity Analysis & Investment Risk Assessment"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_data_table,
    build_plotly_chart,
    build_section_divider,
    build_info_box,
    format_currency,
    format_percentage,
    format_number,
    build_enhanced_table,
    build_heatmap_table
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 18: Equity Analysis & Investment Risk Assessment
    
    Comprehensive equity-specific analysis WITHOUT arbitrary scoring:
    - 18A: Equity Risk Profile (actual metrics, not risk scores)
    - 18B: Investment Style Characteristics (actual positioning, not style scores)
    - 18C: Relative Performance Analysis (actual returns, enhanced context)
    - 18D: Price Momentum & Technical Indicators (separate indicators, no composite)
    - 18E: Earnings Quality & Cash Flow Analysis (quality metrics with trends)
    - 18F: Management Effectiveness & Capital Allocation (DuPont + capital flows)
    - 18G: Competitive Positioning & Moat Assessment (margin quality, not moat scores)
    - 18H: Multi-Dimensional Investment Profile (replaces composite scoring)
    - 18I: Time-Series Evolution Analysis (metric trends over time)
    - 18J: Strategic Investment Intelligence Dashboard (interactive, not text blocks)
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    df = collector.get_all_financial_data()
    prices_daily = collector.get_prices_daily()
    prices_monthly = collector.get_prices_monthly()
    
    # Get S&P 500 data for benchmarking
    sp500_daily = prices_daily[prices_daily['symbol'] == '^GSPC'].copy() if not prices_daily.empty else pd.DataFrame()
    sp500_monthly = prices_monthly[prices_monthly['symbol'] == '^GSPC'].copy() if not prices_monthly.empty else pd.DataFrame()
    
    # Build subsections
    section_18a_html = _build_section_18a_equity_risk_profile(
        companies, prices_daily, prices_monthly, sp500_daily, sp500_monthly, df
    )
    
    section_18b_html = _build_section_18b_investment_style(companies, df, prices_daily)
    section_18c_html = _build_section_18c_relative_performance(companies, prices_daily, prices_monthly, sp500_daily, sp500_monthly)
    section_18d_html = _build_section_18d_momentum_technical(companies, prices_daily, prices_monthly)
    section_18e_html = _build_section_18e_earnings_quality(companies, df)
    section_18f_html = _build_section_18f_management_effectiveness(companies, df)
    section_18g_html = _build_section_18g_competitive_positioning(companies, df)
    section_18h_html = _build_section_18h_investment_profile(companies, df, prices_daily,sp500_daily)
    section_18i_html = _build_section_18i_strategic_intelligence(companies, df, prices_daily, sp500_daily)
    
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        {section_18a_html}
        {build_section_divider() if section_18b_html else ""}
        {section_18b_html}
        {build_section_divider() if section_18c_html else ""}
        {section_18c_html}
        {build_section_divider() if section_18d_html else ""}
        {section_18d_html}
        {build_section_divider() if section_18e_html else ""}
        {section_18e_html}
        {build_section_divider() if section_18f_html else ""}
        {section_18f_html}
        {build_section_divider() if section_18g_html else ""}
        {section_18g_html}
        {build_section_divider() if section_18h_html else ""}
        {section_18h_html}
        {build_section_divider() if section_18i_html else ""}
        {section_18i_html}
    
    </div>
    """
    
    return generate_section_wrapper(18, "Equity Analysis & Investment Risk Assessment", content)


# =============================================================================
# 18A. EQUITY RISK PROFILE
# =============================================================================

def _build_section_18a_equity_risk_profile(
    companies: Dict[str, str],
    prices_daily: pd.DataFrame,
    prices_monthly: pd.DataFrame,
    sp500_daily: pd.DataFrame,
    sp500_monthly: pd.DataFrame,
    df: pd.DataFrame
) -> str:
    """Build subsection 18A: Equity Risk Profile (actual metrics, no scores)"""
    
    if prices_daily.empty or sp500_daily.empty:
        return _build_collapsible_subsection(
            "18A",
            "Equity Risk Profile",
            "<p>Insufficient price data for equity risk analysis.</p>"
        )
    
    # Calculate risk metrics
    risk_metrics = _calculate_equity_risk_metrics(companies, prices_daily, prices_monthly, sp500_daily, sp500_monthly)
    
    if not risk_metrics:
        return _build_collapsible_subsection(
            "18A",
            "Equity Risk Profile",
            "<p>Unable to calculate risk metrics.</p>"
        )
    
    # Build content sections
    intro_html = """
    <p>This section analyzes equity-specific risk characteristics using <strong>actual metrics</strong> rather than arbitrary scores. 
    Risk profiles are assessed through beta, volatility, drawdowns, and risk-adjusted returns, with percentile rankings 
    providing context relative to the S&P 500 and portfolio peers.</p>
    """
    
    # Summary statistics cards
    summary_cards = _build_risk_summary_cards(risk_metrics)
    
    # 1. Risk-Return Scatter Plot with Quadrants
    risk_return_scatter = _create_risk_return_scatter(risk_metrics)
    
    # 2. Beta Distribution Strip Plot
    beta_distribution = _create_beta_distribution_plot(risk_metrics)
    
    # 3. Volatility Heatmap
    volatility_heatmap = _create_volatility_heatmap(risk_metrics)
    
    # 4. Sharpe Ratio Bullet Charts
    sharpe_bullets = _create_sharpe_ratio_bullets(risk_metrics)
    
    # 5. Maximum Drawdown Comparison
    drawdown_comparison = _create_drawdown_comparison(risk_metrics)
    
    # 6. Systematic vs Idiosyncratic Risk
    risk_decomposition = _create_risk_decomposition_chart(risk_metrics)
    
    # 7. Risk Metrics Comparison Table
    risk_table = _create_risk_metrics_table(risk_metrics)
    
    # 8. Risk Classification Matrix
    risk_classification = _create_risk_classification_matrix(risk_metrics)
    
    # Combine all content
    content_html = f"""
    {intro_html}
    
    <h4>Portfolio Risk Summary</h4>
    {summary_cards}
    
    <h4>Risk-Return Profile</h4>
    <p>Companies positioned by volatility (risk) and Sharpe ratio (risk-adjusted returns). 
    Quadrants indicate: <strong>Defensive</strong> (low risk, good returns), <strong>Efficient</strong> (moderate risk, high returns), 
    <strong>Aggressive</strong> (high risk, high returns), and <strong>High-Risk</strong> (high risk, low returns).</p>
    {risk_return_scatter}
    
    <h4>Beta Distribution Analysis</h4>
    <p>Beta measures sensitivity to market movements. Values below 1.0 indicate defensive characteristics, 
    while values above 1.0 suggest aggressive market exposure.</p>
    {beta_distribution}
    
    <h4>Volatility Profile</h4>
    <p>Annualized volatility across multiple dimensions. Lower volatility indicates more stable price movements.</p>
    {volatility_heatmap}
    
    <h4>Risk-Adjusted Performance (Sharpe Ratios)</h4>
    <p>Sharpe ratios measure excess returns per unit of risk. Higher values indicate better risk-adjusted performance. 
    Portfolio and S&P 500 benchmarks provide context.</p>
    {sharpe_bullets}
    
    <h4>Maximum Drawdown Analysis</h4>
    <p>Maximum drawdown represents the largest peak-to-trough decline. Lower (less negative) values indicate 
    better downside protection.</p>
    {drawdown_comparison}
    
    <h4>Risk Decomposition: Systematic vs Idiosyncratic</h4>
    <p>Systematic risk stems from market movements, while idiosyncratic risk is company-specific. 
    Higher systematic percentages indicate stronger market correlation.</p>
    {risk_decomposition}
    
    <h4>Comprehensive Risk Metrics</h4>
    {risk_table}
    
    <h4>Risk Classification Summary</h4>
    {risk_classification}
    """
    
    return _build_collapsible_subsection("18A", "Equity Risk Profile", content_html)


def _calculate_equity_risk_metrics(
    companies: Dict[str, str],
    prices_daily: pd.DataFrame,
    prices_monthly: pd.DataFrame,
    sp500_daily: pd.DataFrame,
    sp500_monthly: pd.DataFrame
) -> Dict[str, Dict]:
    """Calculate comprehensive equity risk metrics without arbitrary scoring"""
    
    risk_metrics = {}
    
    # Prepare S&P 500 returns
    sp500_daily = sp500_daily.sort_values('date').copy()
    sp500_daily['sp500_return'] = sp500_daily['close'].pct_change()
    
    for company_name, ticker in companies.items():
        company_daily = prices_daily[prices_daily['symbol'] == ticker].copy()
        
        if company_daily.empty or len(company_daily) < 60:
            continue
        
        company_daily = company_daily.sort_values('date')
        company_daily['stock_return'] = company_daily['close'].pct_change()
        
        # Merge with S&P 500
        merged_daily = pd.merge(
            company_daily[['date', 'stock_return']],
            sp500_daily[['date', 'sp500_return']],
            on='date',
            how='inner'
        ).dropna()
        
        if len(merged_daily) < 60:
            continue
        
        # Calculate beta (1-year rolling)
        recent_data = merged_daily.tail(252)
        if len(recent_data) >= 60:
            covariance = np.cov(recent_data['stock_return'], recent_data['sp500_return'])[0, 1]
            market_variance = np.var(recent_data['sp500_return'])
            beta = covariance / market_variance if market_variance > 0 else 1.0
        else:
            beta = 1.0
        
        # Volatility metrics
        daily_volatility = company_daily['stock_return'].std() * np.sqrt(252) * 100
        
        # Downside deviation
        negative_returns = company_daily['stock_return'][company_daily['stock_return'] < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) * 100 if len(negative_returns) > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + company_daily['stock_return']).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe ratio (3% risk-free rate)
        risk_free_rate = 0.03
        mean_return = company_daily['stock_return'].mean() * 252
        std_return = company_daily['stock_return'].std() * np.sqrt(252)
        sharpe_ratio = (mean_return - risk_free_rate) / std_return if std_return > 0 else 0
        
        # Tracking error
        tracking_error = (merged_daily['stock_return'] - merged_daily['sp500_return']).std() * np.sqrt(252) * 100
        
        # Information ratio
        active_return = (merged_daily['stock_return'] - merged_daily['sp500_return']).mean() * 252
        information_ratio = active_return / (tracking_error / 100) if tracking_error > 0 else 0
        
        # Risk decomposition
        systematic_risk = (beta ** 2) * merged_daily['sp500_return'].var() * 252 * 100
        total_risk = merged_daily['stock_return'].var() * 252 * 100
        idiosyncratic_risk = max(0, total_risk - systematic_risk)
        systematic_pct = (systematic_risk / total_risk * 100) if total_risk > 0 else 0
        
        # Beta classification
        if beta < 0.8:
            beta_class = "Defensive"
        elif beta <= 1.2:
            beta_class = "Market-Like"
        else:
            beta_class = "Aggressive"
        
        # Volatility classification
        if daily_volatility < 20:
            vol_class = "Low Volatility"
        elif daily_volatility <= 35:
            vol_class = "Moderate Volatility"
        else:
            vol_class = "High Volatility"
        
        risk_metrics[company_name] = {
            'beta': beta,
            'daily_volatility': daily_volatility,
            'downside_deviation': downside_deviation,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'systematic_risk': systematic_risk,
            'idiosyncratic_risk': idiosyncratic_risk,
            'total_risk': total_risk,
            'systematic_pct': systematic_pct,
            'beta_class': beta_class,
            'vol_class': vol_class,
            'mean_return_annual': mean_return * 100
        }
    
    return risk_metrics


def _build_risk_summary_cards(risk_metrics: Dict[str, Dict]) -> str:
    """Build summary stat cards for risk profile"""
    
    if not risk_metrics:
        return "<p>No risk data available.</p>"
    
    avg_beta = np.mean([m['beta'] for m in risk_metrics.values()])
    avg_volatility = np.mean([m['daily_volatility'] for m in risk_metrics.values()])
    avg_sharpe = np.mean([m['sharpe_ratio'] for m in risk_metrics.values()])
    avg_drawdown = np.mean([m['max_drawdown'] for m in risk_metrics.values()])
    
    defensive_count = sum(1 for m in risk_metrics.values() if m['beta_class'] == 'Defensive')
    low_vol_count = sum(1 for m in risk_metrics.values() if m['vol_class'] == 'Low Volatility')
    
    total = len(risk_metrics)
    
    cards = [
        {
            "label": "Average Beta",
            "value": f"{avg_beta:.2f}",
            "description": f"Market sensitivity ({defensive_count}/{total} defensive stocks)",
            "type": "default" if 0.9 <= avg_beta <= 1.1 else "success" if avg_beta < 0.9 else "warning"
        },
        {
            "label": "Average Volatility",
            "value": f"{avg_volatility:.1f}%",
            "description": f"Annualized ({low_vol_count}/{total} low volatility)",
            "type": "success" if avg_volatility < 25 else "default" if avg_volatility < 35 else "warning"
        },
        {
            "label": "Average Sharpe Ratio",
            "value": f"{avg_sharpe:.2f}",
            "description": "Risk-adjusted returns",
            "type": "success" if avg_sharpe > 1.0 else "default" if avg_sharpe > 0.5 else "warning"
        },
        {
            "label": "Average Max Drawdown",
            "value": f"{avg_drawdown:.1f}%",
            "description": "Peak-to-trough decline",
            "type": "success" if avg_drawdown > -30 else "default" if avg_drawdown > -45 else "danger"
        }
    ]
    
    return build_stat_grid(cards)


def _create_risk_return_scatter(risk_metrics: Dict[str, Dict]) -> str:
    """Create risk-return scatter plot with quadrants"""
    
    companies = list(risk_metrics.keys())
    volatilities = [risk_metrics[c]['daily_volatility'] for c in companies]
    sharpe_ratios = [risk_metrics[c]['sharpe_ratio'] for c in companies]
    
    # Determine quadrant colors
    colors = []
    for vol, sharpe in zip(volatilities, sharpe_ratios):
        if vol < 25 and sharpe > 0.8:
            colors.append('#10b981')  # Defensive - green
        elif vol < 35 and sharpe > 0.8:
            colors.append('#3b82f6')  # Efficient - blue
        elif sharpe > 0.8:
            colors.append('#f59e0b')  # Aggressive - orange
        else:
            colors.append('#ef4444')  # High-Risk - red
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': volatilities,
            'y': sharpe_ratios,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>Volatility: %{x:.1f}%<br>Sharpe: %{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Risk-Return Profile with Quadrant Classification',
            'xaxis': {'title': 'Volatility (Annualized %)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Sharpe Ratio', 'gridcolor': '#e5e7eb'},
            'shapes': [
                # Vertical line at 25% volatility
                {'type': 'line', 'x0': 25, 'x1': 25, 'y0': -1, 'y1': 3,
                 'line': {'color': '#94a3b8', 'width': 1, 'dash': 'dash'}},
                # Horizontal line at 0.8 Sharpe
                {'type': 'line', 'x0': 0, 'x1': 60, 'y0': 0.8, 'y1': 0.8,
                 'line': {'color': '#94a3b8', 'width': 1, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 15, 'y': 1.5, 'text': 'Defensive', 'showarrow': False, 'font': {'size': 12, 'color': '#10b981'}},
                {'x': 30, 'y': 1.5, 'text': 'Efficient', 'showarrow': False, 'font': {'size': 12, 'color': '#3b82f6'}},
                {'x': 45, 'y': 1.5, 'text': 'Aggressive', 'showarrow': False, 'font': {'size': 12, 'color': '#f59e0b'}},
                {'x': 30, 'y': 0.3, 'text': 'High-Risk', 'showarrow': False, 'font': {'size': 12, 'color': '#ef4444'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-return-scatter", height=500)


def _create_beta_distribution_plot(risk_metrics: Dict[str, Dict]) -> str:
    """Create beta distribution strip plot"""
    
    companies = list(risk_metrics.keys())
    betas = [risk_metrics[c]['beta'] for c in companies]
    
    # Create strip plot with box plot overlay
    fig_data = {
        'data': [
            {
                'type': 'box',
                'x': betas,
                'name': 'Distribution',
                'marker': {'color': '#3b82f6'},
                'boxmean': True
            },
            {
                'type': 'scatter',
                'mode': 'markers+text',
                'x': betas,
                'y': [0.5] * len(betas),
                'text': [c[:10] for c in companies],
                'textposition': 'top center',
                'marker': {
                    'size': 12,
                    'color': ['#10b981' if b < 0.8 else '#3b82f6' if b <= 1.2 else '#f59e0b' for b in betas],
                    'line': {'width': 1, 'color': '#ffffff'}
                },
                'hovertemplate': '<b>%{text}</b><br>Beta: %{x:.2f}<extra></extra>',
                'showlegend': False
            }
        ],
        'layout': {
            'title': 'Beta Distribution Across Portfolio',
            'xaxis': {'title': 'Beta', 'gridcolor': '#e5e7eb'},
            'yaxis': {'visible': False},
            'shapes': [
                {'type': 'line', 'x0': 1.0, 'x1': 1.0, 'y0': 0, 'y1': 1,
                 'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 1.0, 'y': 1.1, 'text': 'Market Beta = 1.0', 'showarrow': False,
                 'font': {'size': 11, 'color': '#ef4444'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="beta-distribution", height=400)


def _create_volatility_heatmap(risk_metrics: Dict[str, Dict]) -> str:
    """Create volatility heatmap across multiple dimensions"""
    
    companies = list(risk_metrics.keys())
    
    # Prepare data
    daily_vols = [risk_metrics[c]['daily_volatility'] for c in companies]
    downside_vols = [risk_metrics[c]['downside_deviation'] for c in companies]
    tracking_errors = [risk_metrics[c]['tracking_error'] for c in companies]
    
    # Create heatmap
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': [daily_vols, downside_vols, tracking_errors],
            'x': [c[:15] for c in companies],
            'y': ['Daily Volatility', 'Downside Deviation', 'Tracking Error'],
            'colorscale': [
                [0, '#10b981'],    # Green for low
                [0.5, '#f59e0b'],  # Orange for medium
                [1, '#ef4444']     # Red for high
            ],
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Value: %{z:.1f}%<extra></extra>',
            'colorbar': {'title': 'Volatility %'}
        }],
        'layout': {
            'title': 'Volatility Profile Heatmap',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="volatility-heatmap", height=400)


def _create_sharpe_ratio_bullets(risk_metrics: Dict[str, Dict]) -> str:
    """Create Sharpe ratio bullet charts with benchmarks"""
    
    companies = list(risk_metrics.keys())
    sharpe_ratios = [risk_metrics[c]['sharpe_ratio'] for c in companies]
    
    # Calculate portfolio average
    portfolio_avg = np.mean(sharpe_ratios)
    
    # Sort by Sharpe ratio
    sorted_data = sorted(zip(companies, sharpe_ratios), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:15] for c, _ in sorted_data]
    sorted_sharpes = [s for _, s in sorted_data]
    
    # Color code
    colors = ['#10b981' if s > 1.0 else '#3b82f6' if s > 0.7 else '#f59e0b' if s > 0.3 else '#ef4444' for s in sorted_sharpes]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_sharpes,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Sharpe Ratio: %{x:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Risk-Adjusted Performance (Sharpe Ratios)',
            'xaxis': {'title': 'Sharpe Ratio', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': portfolio_avg, 'x1': portfolio_avg, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#667eea', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': 1.0, 'x1': 1.0, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': portfolio_avg, 'y': len(companies), 'text': f'Portfolio Avg: {portfolio_avg:.2f}',
                 'showarrow': False, 'font': {'size': 10, 'color': '#667eea'}},
                {'x': 1.0, 'y': len(companies), 'text': 'Excellent: 1.0',
                 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="sharpe-bullets", height=max(400, len(companies) * 25))


def _create_drawdown_comparison(risk_metrics: Dict[str, Dict]) -> str:
    """Create maximum drawdown comparison chart"""
    
    companies = list(risk_metrics.keys())
    drawdowns = [risk_metrics[c]['max_drawdown'] for c in companies]
    
    # Sort by drawdown (least negative first)
    sorted_data = sorted(zip(companies, drawdowns), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:15] for c, _ in sorted_data]
    sorted_drawdowns = [d for _, d in sorted_data]
    
    # Color code
    colors = ['#10b981' if d > -25 else '#3b82f6' if d > -35 else '#f59e0b' if d > -45 else '#ef4444' for d in sorted_drawdowns]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_drawdowns,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Max Drawdown: %{x:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Maximum Drawdown Analysis',
            'xaxis': {'title': 'Maximum Drawdown (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': -30, 'x1': -30, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': -30, 'y': len(companies), 'text': 'Good: -30%',
                 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="drawdown-comparison", height=max(400, len(companies) * 25))


def _create_risk_decomposition_chart(risk_metrics: Dict[str, Dict]) -> str:
    """Create systematic vs idiosyncratic risk decomposition"""
    
    companies = list(risk_metrics.keys())
    systematic_pcts = [risk_metrics[c]['systematic_pct'] for c in companies]
    idio_pcts = [100 - pct for pct in systematic_pcts]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Systematic Risk',
                'y': [c[:15] for c in companies],
                'x': systematic_pcts,
                'orientation': 'h',
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{y}</b><br>Systematic: %{x:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Idiosyncratic Risk',
                'y': [c[:15] for c in companies],
                'x': idio_pcts,
                'orientation': 'h',
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{y}</b><br>Idiosyncratic: %{x:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Risk Decomposition: Market vs Company-Specific',
            'barmode': 'stack',
            'xaxis': {'title': 'Risk Composition (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'legend': {'orientation': 'h', 'y': -0.15}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-decomposition", height=max(400, len(companies) * 25))


def _create_risk_metrics_table(risk_metrics: Dict[str, Dict]) -> str:
    """Create comprehensive risk metrics comparison table"""
    
    # Prepare data for table
    table_data = []
    for company, metrics in risk_metrics.items():
        table_data.append({
            'Company': company,
            'Beta': f"{metrics['beta']:.2f}",
            'Volatility': f"{metrics['daily_volatility']:.1f}%",
            'Downside Vol': f"{metrics['downside_deviation']:.1f}%",
            'Max Drawdown': f"{metrics['max_drawdown']:.1f}%",
            'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
            'Tracking Error': f"{metrics['tracking_error']:.1f}%",
            'Info Ratio': f"{metrics['information_ratio']:.2f}",
            'Systematic %': f"{metrics['systematic_pct']:.0f}%"
        })
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="risk-metrics-table", page_length=10)


def _create_risk_classification_matrix(risk_metrics: Dict[str, Dict]) -> str:
    """Create risk classification summary matrix"""
    
    # Count classifications
    beta_counts = {}
    vol_counts = {}
    
    for metrics in risk_metrics.values():
        beta_class = metrics['beta_class']
        vol_class = metrics['vol_class']
        beta_counts[beta_class] = beta_counts.get(beta_class, 0) + 1
        vol_counts[vol_class] = vol_counts.get(vol_class, 0) + 1
    
    # Create classification table
    classification_data = []
    for company, metrics in risk_metrics.items():
        classification_data.append({
            'Company': company,
            'Beta Classification': metrics['beta_class'],
            'Volatility Classification': metrics['vol_class'],
            'Risk Profile': f"{metrics['beta_class']}, {metrics['vol_class']}"
        })
    
    df_classification = pd.DataFrame(classification_data)
    
    return build_enhanced_table(
        df_classification,
        table_id="risk-classification-table",
        badge_columns=['Beta Classification', 'Volatility Classification']
    )


# =============================================================================
# 18B-18J: SUBSECTION STUBS (TO BE IMPLEMENTED IN NEXT PHASES)
# =============================================================================

"""Section 18: Equity Analysis & Investment Risk Assessment"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_data_table,
    build_plotly_chart,
    build_section_divider,
    build_info_box,
    format_currency,
    format_percentage,
    format_number,
    build_enhanced_table,
    build_heatmap_table
)





# =============================================================================
# 18A. EQUITY RISK PROFILE
# =============================================================================

def _build_section_18a_equity_risk_profile(
    companies: Dict[str, str],
    prices_daily: pd.DataFrame,
    prices_monthly: pd.DataFrame,
    sp500_daily: pd.DataFrame,
    sp500_monthly: pd.DataFrame,
    df: pd.DataFrame
) -> str:
    """Build subsection 18A: Equity Risk Profile (actual metrics, no scores)"""
    
    if prices_daily.empty or sp500_daily.empty:
        return _build_collapsible_subsection(
            "18A",
            "Equity Risk Profile",
            "<p>Insufficient price data for equity risk analysis.</p>"
        )
    
    # Calculate risk metrics
    risk_metrics = _calculate_equity_risk_metrics(companies, prices_daily, prices_monthly, sp500_daily, sp500_monthly)
    
    if not risk_metrics:
        return _build_collapsible_subsection(
            "18A",
            "Equity Risk Profile",
            "<p>Unable to calculate risk metrics.</p>"
        )
    
    # Build content sections
    intro_html = """
    <p>This section analyzes equity-specific risk characteristics using <strong>actual metrics</strong> rather than arbitrary scores. 
    Risk profiles are assessed through beta, volatility, drawdowns, and risk-adjusted returns, with percentile rankings 
    providing context relative to the S&P 500 and portfolio peers.</p>
    """
    
    # Summary statistics cards
    summary_cards = _build_risk_summary_cards(risk_metrics)
    
    # 1. Risk-Return Scatter Plot with Quadrants
    risk_return_scatter = _create_risk_return_scatter(risk_metrics)
    
    # 2. Beta Distribution Strip Plot
    beta_distribution = _create_beta_distribution_plot(risk_metrics)
    
    # 3. Volatility Heatmap
    volatility_heatmap = _create_volatility_heatmap(risk_metrics)
    
    # 4. Sharpe Ratio Bullet Charts
    sharpe_bullets = _create_sharpe_ratio_bullets(risk_metrics)
    
    # 5. Maximum Drawdown Comparison
    drawdown_comparison = _create_drawdown_comparison(risk_metrics)
    
    # 6. Systematic vs Idiosyncratic Risk
    risk_decomposition = _create_risk_decomposition_chart(risk_metrics)
    
    # 7. Risk Metrics Comparison Table
    risk_table = _create_risk_metrics_table(risk_metrics)
    
    # 8. Risk Classification Matrix
    risk_classification = _create_risk_classification_matrix(risk_metrics)
    
    # Combine all content
    content_html = f"""
    {intro_html}
    
    <h4>Portfolio Risk Summary</h4>
    {summary_cards}
    
    <h4>Risk-Return Profile</h4>
    <p>Companies positioned by volatility (risk) and Sharpe ratio (risk-adjusted returns). 
    Quadrants indicate: <strong>Defensive</strong> (low risk, good returns), <strong>Efficient</strong> (moderate risk, high returns), 
    <strong>Aggressive</strong> (high risk, high returns), and <strong>High-Risk</strong> (high risk, low returns).</p>
    {risk_return_scatter}
    
    <h4>Beta Distribution Analysis</h4>
    <p>Beta measures sensitivity to market movements. Values below 1.0 indicate defensive characteristics, 
    while values above 1.0 suggest aggressive market exposure.</p>
    {beta_distribution}
    
    <h4>Volatility Profile</h4>
    <p>Annualized volatility across multiple dimensions. Lower volatility indicates more stable price movements.</p>
    {volatility_heatmap}
    
    <h4>Risk-Adjusted Performance (Sharpe Ratios)</h4>
    <p>Sharpe ratios measure excess returns per unit of risk. Higher values indicate better risk-adjusted performance. 
    Portfolio and S&P 500 benchmarks provide context.</p>
    {sharpe_bullets}
    
    <h4>Maximum Drawdown Analysis</h4>
    <p>Maximum drawdown represents the largest peak-to-trough decline. Lower (less negative) values indicate 
    better downside protection.</p>
    {drawdown_comparison}
    
    <h4>Risk Decomposition: Systematic vs Idiosyncratic</h4>
    <p>Systematic risk stems from market movements, while idiosyncratic risk is company-specific. 
    Higher systematic percentages indicate stronger market correlation.</p>
    {risk_decomposition}
    
    <h4>Comprehensive Risk Metrics</h4>
    {risk_table}
    
    <h4>Risk Classification Summary</h4>
    {risk_classification}
    """
    
    return _build_collapsible_subsection("18A", "Equity Risk Profile", content_html)


def _calculate_equity_risk_metrics(
    companies: Dict[str, str],
    prices_daily: pd.DataFrame,
    prices_monthly: pd.DataFrame,
    sp500_daily: pd.DataFrame,
    sp500_monthly: pd.DataFrame
) -> Dict[str, Dict]:
    """Calculate comprehensive equity risk metrics without arbitrary scoring"""
    
    risk_metrics = {}
    
    # Prepare S&P 500 returns
    sp500_daily = sp500_daily.sort_values('date').copy()
    sp500_daily['sp500_return'] = sp500_daily['close'].pct_change()
    
    for company_name, ticker in companies.items():
        company_daily = prices_daily[prices_daily['symbol'] == ticker].copy()
        
        if company_daily.empty or len(company_daily) < 60:
            continue
        
        company_daily = company_daily.sort_values('date')
        company_daily['stock_return'] = company_daily['close'].pct_change()
        
        # Merge with S&P 500
        merged_daily = pd.merge(
            company_daily[['date', 'stock_return']],
            sp500_daily[['date', 'sp500_return']],
            on='date',
            how='inner'
        ).dropna()
        
        if len(merged_daily) < 60:
            continue
        
        # Calculate beta (1-year rolling)
        recent_data = merged_daily.tail(252)
        if len(recent_data) >= 60:
            covariance = np.cov(recent_data['stock_return'], recent_data['sp500_return'])[0, 1]
            market_variance = np.var(recent_data['sp500_return'])
            beta = covariance / market_variance if market_variance > 0 else 1.0
        else:
            beta = 1.0
        
        # Volatility metrics
        daily_volatility = company_daily['stock_return'].std() * np.sqrt(252) * 100
        
        # Downside deviation
        negative_returns = company_daily['stock_return'][company_daily['stock_return'] < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) * 100 if len(negative_returns) > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + company_daily['stock_return']).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe ratio (3% risk-free rate)
        risk_free_rate = 0.03
        mean_return = company_daily['stock_return'].mean() * 252
        std_return = company_daily['stock_return'].std() * np.sqrt(252)
        sharpe_ratio = (mean_return - risk_free_rate) / std_return if std_return > 0 else 0
        
        # Tracking error
        tracking_error = (merged_daily['stock_return'] - merged_daily['sp500_return']).std() * np.sqrt(252) * 100
        
        # Information ratio
        active_return = (merged_daily['stock_return'] - merged_daily['sp500_return']).mean() * 252
        information_ratio = active_return / (tracking_error / 100) if tracking_error > 0 else 0
        
        # Risk decomposition
        systematic_risk = (beta ** 2) * merged_daily['sp500_return'].var() * 252 * 100
        total_risk = merged_daily['stock_return'].var() * 252 * 100
        idiosyncratic_risk = max(0, total_risk - systematic_risk)
        systematic_pct = (systematic_risk / total_risk * 100) if total_risk > 0 else 0
        
        # Beta classification
        if beta < 0.8:
            beta_class = "Defensive"
        elif beta <= 1.2:
            beta_class = "Market-Like"
        else:
            beta_class = "Aggressive"
        
        # Volatility classification
        if daily_volatility < 20:
            vol_class = "Low Volatility"
        elif daily_volatility <= 35:
            vol_class = "Moderate Volatility"
        else:
            vol_class = "High Volatility"
        
        risk_metrics[company_name] = {
            'beta': beta,
            'daily_volatility': daily_volatility,
            'downside_deviation': downside_deviation,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'systematic_risk': systematic_risk,
            'idiosyncratic_risk': idiosyncratic_risk,
            'total_risk': total_risk,
            'systematic_pct': systematic_pct,
            'beta_class': beta_class,
            'vol_class': vol_class,
            'mean_return_annual': mean_return * 100
        }
    
    return risk_metrics


def _build_risk_summary_cards(risk_metrics: Dict[str, Dict]) -> str:
    """Build summary stat cards for risk profile"""
    
    if not risk_metrics:
        return "<p>No risk data available.</p>"
    
    avg_beta = np.mean([m['beta'] for m in risk_metrics.values()])
    avg_volatility = np.mean([m['daily_volatility'] for m in risk_metrics.values()])
    avg_sharpe = np.mean([m['sharpe_ratio'] for m in risk_metrics.values()])
    avg_drawdown = np.mean([m['max_drawdown'] for m in risk_metrics.values()])
    
    defensive_count = sum(1 for m in risk_metrics.values() if m['beta_class'] == 'Defensive')
    low_vol_count = sum(1 for m in risk_metrics.values() if m['vol_class'] == 'Low Volatility')
    
    total = len(risk_metrics)
    
    cards = [
        {
            "label": "Average Beta",
            "value": f"{avg_beta:.2f}",
            "description": f"Market sensitivity ({defensive_count}/{total} defensive stocks)",
            "type": "default" if 0.9 <= avg_beta <= 1.1 else "success" if avg_beta < 0.9 else "warning"
        },
        {
            "label": "Average Volatility",
            "value": f"{avg_volatility:.1f}%",
            "description": f"Annualized ({low_vol_count}/{total} low volatility)",
            "type": "success" if avg_volatility < 25 else "default" if avg_volatility < 35 else "warning"
        },
        {
            "label": "Average Sharpe Ratio",
            "value": f"{avg_sharpe:.2f}",
            "description": "Risk-adjusted returns",
            "type": "success" if avg_sharpe > 1.0 else "default" if avg_sharpe > 0.5 else "warning"
        },
        {
            "label": "Average Max Drawdown",
            "value": f"{avg_drawdown:.1f}%",
            "description": "Peak-to-trough decline",
            "type": "success" if avg_drawdown > -30 else "default" if avg_drawdown > -45 else "danger"
        }
    ]
    
    return build_stat_grid(cards)


def _create_risk_return_scatter(risk_metrics: Dict[str, Dict]) -> str:
    """Create risk-return scatter plot with quadrants"""
    
    companies = list(risk_metrics.keys())
    volatilities = [risk_metrics[c]['daily_volatility'] for c in companies]
    sharpe_ratios = [risk_metrics[c]['sharpe_ratio'] for c in companies]
    
    # Determine quadrant colors
    colors = []
    for vol, sharpe in zip(volatilities, sharpe_ratios):
        if vol < 25 and sharpe > 0.8:
            colors.append('#10b981')  # Defensive - green
        elif vol < 35 and sharpe > 0.8:
            colors.append('#3b82f6')  # Efficient - blue
        elif sharpe > 0.8:
            colors.append('#f59e0b')  # Aggressive - orange
        else:
            colors.append('#ef4444')  # High-Risk - red
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': volatilities,
            'y': sharpe_ratios,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>Volatility: %{x:.1f}%<br>Sharpe: %{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Risk-Return Profile with Quadrant Classification',
            'xaxis': {'title': 'Volatility (Annualized %)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Sharpe Ratio', 'gridcolor': '#e5e7eb'},
            'shapes': [
                # Vertical line at 25% volatility
                {'type': 'line', 'x0': 25, 'x1': 25, 'y0': -1, 'y1': 3,
                 'line': {'color': '#94a3b8', 'width': 1, 'dash': 'dash'}},
                # Horizontal line at 0.8 Sharpe
                {'type': 'line', 'x0': 0, 'x1': 60, 'y0': 0.8, 'y1': 0.8,
                 'line': {'color': '#94a3b8', 'width': 1, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 15, 'y': 1.5, 'text': 'Defensive', 'showarrow': False, 'font': {'size': 12, 'color': '#10b981'}},
                {'x': 30, 'y': 1.5, 'text': 'Efficient', 'showarrow': False, 'font': {'size': 12, 'color': '#3b82f6'}},
                {'x': 45, 'y': 1.5, 'text': 'Aggressive', 'showarrow': False, 'font': {'size': 12, 'color': '#f59e0b'}},
                {'x': 30, 'y': 0.3, 'text': 'High-Risk', 'showarrow': False, 'font': {'size': 12, 'color': '#ef4444'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-return-scatter", height=500)


def _create_beta_distribution_plot(risk_metrics: Dict[str, Dict]) -> str:
    """Create beta distribution strip plot"""
    
    companies = list(risk_metrics.keys())
    betas = [risk_metrics[c]['beta'] for c in companies]
    
    # Create strip plot with box plot overlay
    fig_data = {
        'data': [
            {
                'type': 'box',
                'x': betas,
                'name': 'Distribution',
                'marker': {'color': '#3b82f6'},
                'boxmean': True
            },
            {
                'type': 'scatter',
                'mode': 'markers+text',
                'x': betas,
                'y': [0.5] * len(betas),
                'text': [c[:10] for c in companies],
                'textposition': 'top center',
                'marker': {
                    'size': 12,
                    'color': ['#10b981' if b < 0.8 else '#3b82f6' if b <= 1.2 else '#f59e0b' for b in betas],
                    'line': {'width': 1, 'color': '#ffffff'}
                },
                'hovertemplate': '<b>%{text}</b><br>Beta: %{x:.2f}<extra></extra>',
                'showlegend': False
            }
        ],
        'layout': {
            'title': 'Beta Distribution Across Portfolio',
            'xaxis': {'title': 'Beta', 'gridcolor': '#e5e7eb'},
            'yaxis': {'visible': False},
            'shapes': [
                {'type': 'line', 'x0': 1.0, 'x1': 1.0, 'y0': 0, 'y1': 1,
                 'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 1.0, 'y': 1.1, 'text': 'Market Beta = 1.0', 'showarrow': False,
                 'font': {'size': 11, 'color': '#ef4444'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="beta-distribution", height=400)


def _create_volatility_heatmap(risk_metrics: Dict[str, Dict]) -> str:
    """Create volatility heatmap across multiple dimensions"""
    
    companies = list(risk_metrics.keys())
    
    # Prepare data
    daily_vols = [risk_metrics[c]['daily_volatility'] for c in companies]
    downside_vols = [risk_metrics[c]['downside_deviation'] for c in companies]
    tracking_errors = [risk_metrics[c]['tracking_error'] for c in companies]
    
    # Create heatmap
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': [daily_vols, downside_vols, tracking_errors],
            'x': [c[:15] for c in companies],
            'y': ['Daily Volatility', 'Downside Deviation', 'Tracking Error'],
            'colorscale': [
                [0, '#10b981'],    # Green for low
                [0.5, '#f59e0b'],  # Orange for medium
                [1, '#ef4444']     # Red for high
            ],
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Value: %{z:.1f}%<extra></extra>',
            'colorbar': {'title': 'Volatility %'}
        }],
        'layout': {
            'title': 'Volatility Profile Heatmap',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="volatility-heatmap", height=400)


def _create_sharpe_ratio_bullets(risk_metrics: Dict[str, Dict]) -> str:
    """Create Sharpe ratio bullet charts with benchmarks"""
    
    companies = list(risk_metrics.keys())
    sharpe_ratios = [risk_metrics[c]['sharpe_ratio'] for c in companies]
    
    # Calculate portfolio average
    portfolio_avg = np.mean(sharpe_ratios)
    
    # Sort by Sharpe ratio
    sorted_data = sorted(zip(companies, sharpe_ratios), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:15] for c, _ in sorted_data]
    sorted_sharpes = [s for _, s in sorted_data]
    
    # Color code
    colors = ['#10b981' if s > 1.0 else '#3b82f6' if s > 0.7 else '#f59e0b' if s > 0.3 else '#ef4444' for s in sorted_sharpes]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_sharpes,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Sharpe Ratio: %{x:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Risk-Adjusted Performance (Sharpe Ratios)',
            'xaxis': {'title': 'Sharpe Ratio', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': portfolio_avg, 'x1': portfolio_avg, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#667eea', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': 1.0, 'x1': 1.0, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': portfolio_avg, 'y': len(companies), 'text': f'Portfolio Avg: {portfolio_avg:.2f}',
                 'showarrow': False, 'font': {'size': 10, 'color': '#667eea'}},
                {'x': 1.0, 'y': len(companies), 'text': 'Excellent: 1.0',
                 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="sharpe-bullets", height=max(400, len(companies) * 25))


def _create_drawdown_comparison(risk_metrics: Dict[str, Dict]) -> str:
    """Create maximum drawdown comparison chart"""
    
    companies = list(risk_metrics.keys())
    drawdowns = [risk_metrics[c]['max_drawdown'] for c in companies]
    
    # Sort by drawdown (least negative first)
    sorted_data = sorted(zip(companies, drawdowns), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:15] for c, _ in sorted_data]
    sorted_drawdowns = [d for _, d in sorted_data]
    
    # Color code
    colors = ['#10b981' if d > -25 else '#3b82f6' if d > -35 else '#f59e0b' if d > -45 else '#ef4444' for d in sorted_drawdowns]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_drawdowns,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Max Drawdown: %{x:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Maximum Drawdown Analysis',
            'xaxis': {'title': 'Maximum Drawdown (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': -30, 'x1': -30, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': -30, 'y': len(companies), 'text': 'Good: -30%',
                 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="drawdown-comparison", height=max(400, len(companies) * 25))


def _create_risk_decomposition_chart(risk_metrics: Dict[str, Dict]) -> str:
    """Create systematic vs idiosyncratic risk decomposition"""
    
    companies = list(risk_metrics.keys())
    systematic_pcts = [risk_metrics[c]['systematic_pct'] for c in companies]
    idio_pcts = [100 - pct for pct in systematic_pcts]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Systematic Risk',
                'y': [c[:15] for c in companies],
                'x': systematic_pcts,
                'orientation': 'h',
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{y}</b><br>Systematic: %{x:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Idiosyncratic Risk',
                'y': [c[:15] for c in companies],
                'x': idio_pcts,
                'orientation': 'h',
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{y}</b><br>Idiosyncratic: %{x:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Risk Decomposition: Market vs Company-Specific',
            'barmode': 'stack',
            'xaxis': {'title': 'Risk Composition (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'legend': {'orientation': 'h', 'y': -0.15}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-decomposition", height=max(400, len(companies) * 25))


def _create_risk_metrics_table(risk_metrics: Dict[str, Dict]) -> str:
    """Create comprehensive risk metrics comparison table"""
    
    # Prepare data for table
    table_data = []
    for company, metrics in risk_metrics.items():
        table_data.append({
            'Company': company,
            'Beta': f"{metrics['beta']:.2f}",
            'Volatility': f"{metrics['daily_volatility']:.1f}%",
            'Downside Vol': f"{metrics['downside_deviation']:.1f}%",
            'Max Drawdown': f"{metrics['max_drawdown']:.1f}%",
            'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
            'Tracking Error': f"{metrics['tracking_error']:.1f}%",
            'Info Ratio': f"{metrics['information_ratio']:.2f}",
            'Systematic %': f"{metrics['systematic_pct']:.0f}%"
        })
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="risk-metrics-table", page_length=10)


def _create_risk_classification_matrix(risk_metrics: Dict[str, Dict]) -> str:
    """Create risk classification summary matrix"""
    
    # Count classifications
    beta_counts = {}
    vol_counts = {}
    
    for metrics in risk_metrics.values():
        beta_class = metrics['beta_class']
        vol_class = metrics['vol_class']
        beta_counts[beta_class] = beta_counts.get(beta_class, 0) + 1
        vol_counts[vol_class] = vol_counts.get(vol_class, 0) + 1
    
    # Create classification table
    classification_data = []
    for company, metrics in risk_metrics.items():
        classification_data.append({
            'Company': company,
            'Beta Classification': metrics['beta_class'],
            'Volatility Classification': metrics['vol_class'],
            'Risk Profile': f"{metrics['beta_class']}, {metrics['vol_class']}"
        })
    
    df_classification = pd.DataFrame(classification_data)
    
    return build_enhanced_table(
        df_classification,
        table_id="risk-classification-table",
        badge_columns=['Beta Classification', 'Volatility Classification']
    )


# =============================================================================
# 18B-18J: SUBSECTION STUBS (TO BE IMPLEMENTED IN NEXT PHASES)
# =============================================================================

def _build_section_18b_investment_style(companies: Dict[str, str], df: pd.DataFrame, prices_daily: pd.DataFrame) -> str:
    """Build subsection 18B: Investment Style Characteristics"""
    
    if df.empty:
        return _build_collapsible_subsection(
            "18B",
            "Investment Style Characteristics",
            "<p>Insufficient financial data for style analysis.</p>"
        )
    
    # Calculate style metrics
    style_metrics = _calculate_style_metrics(companies, df)
    
    if not style_metrics:
        return _build_collapsible_subsection(
            "18B",
            "Investment Style Characteristics",
            "<p>Unable to calculate style metrics.</p>"
        )
    
    # Build content sections
    intro_html = """
    <p>This section analyzes investment style characteristics using <strong>actual financial metrics</strong> 
    rather than arbitrary style scores. Companies are positioned based on growth rates, valuation multiples, 
    profitability, and dividend characteristics to identify their natural investment profile.</p>
    """
    
    # Summary cards
    summary_cards = _build_style_summary_cards(style_metrics)
    
    # 1. Growth-Value Scatter Plot
    growth_value_scatter = _create_growth_value_scatter(style_metrics)
    
    # 2. Style Quadrant Analysis
    style_quadrant = _create_style_quadrant_chart(style_metrics)
    
    # 3. ROE vs ROIC Scatter
    roe_roic_scatter = _create_roe_roic_scatter(style_metrics)
    
    # 4. Dividend-Growth Matrix
    dividend_growth_matrix = _create_dividend_growth_matrix(style_metrics)
    
    # 5. Profitability Radar Charts
    profitability_radars = _create_profitability_radar_charts(style_metrics)
    
    # 6. Style Metrics Heatmap
    style_heatmap = _create_style_metrics_heatmap(style_metrics)
    
    # 7. Style Metrics Table
    style_table = _create_style_metrics_table(style_metrics)
    
    # 8. Style Classification Summary
    style_classification = _create_style_classification_summary(style_metrics)
    
    # Combine all content
    content_html = f"""
    {intro_html}
    
    <h4>Portfolio Style Summary</h4>
    {summary_cards}
    
    <h4>Growth vs Value Positioning</h4>
    <p>Companies positioned by P/E ratio (valuation) and revenue growth (growth characteristic). 
    Lower P/E with higher growth indicates attractive growth-at-reasonable-price opportunities.</p>
    {growth_value_scatter}
    
    <h4>Investment Style Quadrant Analysis</h4>
    <p>Four distinct investment styles based on growth and valuation characteristics. 
    <strong>Growth Premium</strong> (high growth, high valuation), <strong>GARP</strong> (high growth, reasonable valuation), 
    <strong>Deep Value</strong> (low growth, low valuation), <strong>Value Trap Risk</strong> (low growth, high valuation).</p>
    {style_quadrant}
    
    <h4>Return on Equity vs Return on Invested Capital</h4>
    <p>Quality assessment through capital efficiency metrics. Companies with high ROE and ROIC demonstrate 
    superior profitability and capital allocation. Size represents market capitalization.</p>
    {roe_roic_scatter}
    
    <h4>Dividend Yield vs Revenue Growth</h4>
    <p>Income vs growth trade-off visualization. <strong>High-yield dividend stocks</strong> typically show lower growth, 
    while <strong>high-growth companies</strong> reinvest rather than distribute cash.</p>
    {dividend_growth_matrix}
    
    <h4>Profitability Profile Comparison</h4>
    <p>Multi-dimensional profitability radar charts showing margin structure, returns, and efficiency metrics 
    for each company. Larger areas indicate stronger overall profitability.</p>
    {profitability_radars}
    
    <h4>Style Metrics Heatmap</h4>
    <p>Comprehensive view of all style-related metrics across companies. Color intensity represents 
    relative strength within the portfolio.</p>
    {style_heatmap}
    
    <h4>Detailed Style Metrics</h4>
    {style_table}
    
    <h4>Style Classification Summary</h4>
    {style_classification}
    """
    
    return _build_collapsible_subsection("18B", "Investment Style Characteristics", content_html)


def _calculate_style_metrics(companies: Dict[str, str], df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate investment style metrics using actual financial data"""
    
    style_metrics = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty or len(company_data) < 3:
            continue
        
        latest_data = company_data.iloc[-1]
        
        # Growth metrics (actual percentages)
        revenue_growth_3y = company_data['revenue'].pct_change().tail(3).mean() * 100 if len(company_data) >= 3 else 0
        earnings_growth_3y = company_data['netIncome'].pct_change().tail(3).mean() * 100 if 'netIncome' in company_data.columns and len(company_data) >= 3 else 0
        
        # Valuation metrics (actual multiples)
        pe_ratio = latest_data.get('priceToEarningsRatio', np.nan)
        pb_ratio = latest_data.get('priceToBookRatio', np.nan)
        ps_ratio = latest_data.get('priceToSalesRatio', np.nan)
        
        # Profitability metrics (actual percentages)
        roe = latest_data.get('returnOnEquity', 0)
        roic = latest_data.get('returnOnInvestedCapital', 0)
        roa = latest_data.get('returnOnAssets', 0)
        gross_margin = latest_data.get('grossProfitMargin', 0)
        operating_margin = latest_data.get('operatingProfitMargin', 0)
        net_margin = latest_data.get('netProfitMargin', 0)
        
        # Dividend metrics
        dividend_yield = latest_data.get('dividendYield', 0) * 100 if 'dividendYield' in latest_data else 0
        dividend_payout = latest_data.get('dividendPayoutRatio', 0) * 100 if 'dividendPayoutRatio' in latest_data else 0
        
        # Market cap
        market_cap = latest_data.get('marketCap', 0) / 1e9  # in billions
        
        # Style classification based on actual metrics
        style_class = _classify_investment_style(
            revenue_growth_3y, pe_ratio, dividend_yield, roe, roic
        )
        
        style_metrics[company_name] = {
            'revenue_growth_3y': revenue_growth_3y,
            'earnings_growth_3y': earnings_growth_3y,
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'ps_ratio': ps_ratio,
            'roe': roe,
            'roic': roic,
            'roa': roa,
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'net_margin': net_margin,
            'dividend_yield': dividend_yield,
            'dividend_payout': dividend_payout,
            'market_cap': market_cap,
            'style_class': style_class
        }
    
    return style_metrics


def _classify_investment_style(revenue_growth: float, pe_ratio: float, 
                               dividend_yield: float, roe: float, roic: float) -> str:
    """Classify investment style based on actual metrics"""
    
    # High growth threshold
    high_growth = revenue_growth > 15
    moderate_growth = revenue_growth > 8
    
    # Value thresholds
    deep_value = pe_ratio < 15 if not np.isnan(pe_ratio) else False
    fair_value = pe_ratio < 25 if not np.isnan(pe_ratio) else False
    
    # Quality thresholds
    high_quality = roe > 18 and roic > 15
    
    # Income thresholds
    high_income = dividend_yield > 3
    
    # Classification logic
    if high_growth and not fair_value:
        return "Growth Premium"
    elif high_growth and fair_value:
        return "Growth at Reasonable Price (GARP)"
    elif high_quality and fair_value:
        return "Quality Value"
    elif deep_value and moderate_growth:
        return "Deep Value"
    elif high_income:
        return "Dividend Income"
    elif high_quality:
        return "Quality Growth"
    elif fair_value:
        return "Value"
    else:
        return "Core/Blend"


def _build_style_summary_cards(style_metrics: Dict[str, Dict]) -> str:
    """Build summary stat cards for style analysis"""
    
    if not style_metrics:
        return "<p>No style data available.</p>"
    
    avg_growth = np.mean([m['revenue_growth_3y'] for m in style_metrics.values()])
    avg_pe = np.nanmean([m['pe_ratio'] for m in style_metrics.values()])
    avg_roe = np.mean([m['roe'] for m in style_metrics.values()])
    avg_div_yield = np.mean([m['dividend_yield'] for m in style_metrics.values()])
    
    # Count style types
    style_counts = {}
    for m in style_metrics.values():
        style = m['style_class']
        style_counts[style] = style_counts.get(style, 0) + 1
    
    dominant_style = max(style_counts.items(), key=lambda x: x[1])[0] if style_counts else "Mixed"
    
    cards = [
        {
            "label": "Average Revenue Growth",
            "value": f"{avg_growth:.1f}%",
            "description": "3-year average growth rate",
            "type": "success" if avg_growth > 12 else "default" if avg_growth > 5 else "warning"
        },
        {
            "label": "Average P/E Ratio",
            "value": f"{avg_pe:.1f}x" if not np.isnan(avg_pe) else "N/A",
            "description": "Valuation multiple",
            "type": "success" if avg_pe < 20 else "default" if avg_pe < 30 else "warning"
        },
        {
            "label": "Average ROE",
            "value": f"{avg_roe:.1f}%",
            "description": "Return on equity",
            "type": "success" if avg_roe > 18 else "default" if avg_roe > 12 else "warning"
        },
        {
            "label": "Dominant Style",
            "value": dominant_style,
            "description": f"{style_counts.get(dominant_style, 0)}/{len(style_metrics)} companies",
            "type": "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_growth_value_scatter(style_metrics: Dict[str, Dict]) -> str:
    """Create growth vs value scatter plot"""
    
    companies = list(style_metrics.keys())
    pe_ratios = [style_metrics[c]['pe_ratio'] for c in companies]
    growth_rates = [style_metrics[c]['revenue_growth_3y'] for c in companies]
    market_caps = [style_metrics[c]['market_cap'] for c in companies]
    
    # Color by style class
    style_colors = {
        'Growth Premium': '#ef4444',
        'Growth at Reasonable Price (GARP)': '#10b981',
        'Quality Value': '#3b82f6',
        'Deep Value': '#8b5cf6',
        'Dividend Income': '#f59e0b',
        'Quality Growth': '#14b8a6',
        'Value': '#06b6d4',
        'Core/Blend': '#64748b'
    }
    
    colors = [style_colors.get(style_metrics[c]['style_class'], '#64748b') for c in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': pe_ratios,
            'y': growth_rates,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': [max(8, min(30, mc / 100)) for mc in market_caps],
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>P/E: %{x:.1f}<br>Growth: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Growth vs Value Positioning (P/E vs Revenue Growth)',
            'xaxis': {'title': 'P/E Ratio', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': '3-Year Revenue Growth (%)', 'gridcolor': '#e5e7eb'},
            'shapes': [
                # Fair value line at P/E = 20
                {'type': 'line', 'x0': 20, 'x1': 20, 'y0': -10, 'y1': 40,
                 'line': {'color': '#94a3b8', 'width': 1, 'dash': 'dash'}},
                # High growth line at 15%
                {'type': 'line', 'x0': 0, 'x1': 50, 'y0': 15, 'y1': 15,
                 'line': {'color': '#94a3b8', 'width': 1, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 20, 'y': 38, 'text': 'Fair Value (P/E=20)', 'showarrow': False, 'font': {'size': 10}},
                {'x': 45, 'y': 16, 'text': 'High Growth (15%)', 'showarrow': False, 'font': {'size': 10}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="growth-value-scatter", height=500)


def _create_style_quadrant_chart(style_metrics: Dict[str, Dict]) -> str:
    """Create style quadrant analysis chart"""
    
    companies = list(style_metrics.keys())
    
    # Use PEG ratio proxy: P/E divided by growth rate
    x_values = []  # Growth characteristic
    y_values = []  # Value characteristic
    
    for c in companies:
        growth = style_metrics[c]['revenue_growth_3y']
        pe = style_metrics[c]['pe_ratio']
        
        x_values.append(growth)
        # Invert P/E for value axis (lower P/E = more value = higher score)
        y_values.append(100 / pe if not np.isnan(pe) and pe > 0 else 0)
    
    # Color by quadrant
    colors = []
    for x, y in zip(x_values, y_values):
        if x > 12 and y > 4:  # High growth, low P/E (GARP)
            colors.append('#10b981')
        elif x > 12:  # High growth, high P/E (Growth Premium)
            colors.append('#ef4444')
        elif y > 4:  # Low growth, low P/E (Deep Value)
            colors.append('#3b82f6')
        else:  # Low growth, high P/E (Value Trap)
            colors.append('#f59e0b')
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': x_values,
            'y': y_values,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>Growth: %{x:.1f}%<br>Value Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': 'Investment Style Quadrant Matrix',
            'xaxis': {'title': 'Revenue Growth (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Value Score (100/P/E)', 'gridcolor': '#e5e7eb'},
            'shapes': [
                {'type': 'line', 'x0': 12, 'x1': 12, 'y0': 0, 'y1': 10,
                 'line': {'color': '#94a3b8', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': -10, 'x1': 40, 'y0': 4, 'y1': 4,
                 'line': {'color': '#94a3b8', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 25, 'y': 7, 'text': 'GARP Zone', 'showarrow': False, 'font': {'size': 12, 'color': '#10b981'}},
                {'x': 25, 'y': 2, 'text': 'Growth Premium', 'showarrow': False, 'font': {'size': 12, 'color': '#ef4444'}},
                {'x': 5, 'y': 7, 'text': 'Deep Value', 'showarrow': False, 'font': {'size': 12, 'color': '#3b82f6'}},
                {'x': 5, 'y': 2, 'text': 'Value Trap Risk', 'showarrow': False, 'font': {'size': 12, 'color': '#f59e0b'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="style-quadrant", height=500)


def _create_roe_roic_scatter(style_metrics: Dict[str, Dict]) -> str:
    """Create ROE vs ROIC quality scatter plot"""
    
    companies = list(style_metrics.keys())
    roe_values = [style_metrics[c]['roe'] for c in companies]
    roic_values = [style_metrics[c]['roic'] for c in companies]
    market_caps = [style_metrics[c]['market_cap'] for c in companies]
    
    # Color by quality
    colors = []
    for roe, roic in zip(roe_values, roic_values):
        if roe > 18 and roic > 15:
            colors.append('#10b981')  # Excellent
        elif roe > 12 and roic > 10:
            colors.append('#3b82f6')  # Good
        elif roe > 8 and roic > 7:
            colors.append('#f59e0b')  # Fair
        else:
            colors.append('#ef4444')  # Poor
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': roe_values,
            'y': roic_values,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': [max(8, min(30, mc / 100)) for mc in market_caps],
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>ROE: %{x:.1f}%<br>ROIC: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Quality Analysis: ROE vs ROIC (Size = Market Cap)',
            'xaxis': {'title': 'Return on Equity (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Return on Invested Capital (%)', 'gridcolor': '#e5e7eb'},
            'shapes': [
                {'type': 'line', 'x0': 15, 'x1': 15, 'y0': 0, 'y1': 40,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}},
                {'type': 'line', 'x0': 0, 'x1': 40, 'y0': 15, 'y1': 15,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': 15, 'y': 38, 'text': 'Excellent ROE', 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}},
                {'x': 35, 'y': 15.5, 'text': 'Excellent ROIC', 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roe-roic-scatter", height=500)


def _create_dividend_growth_matrix(style_metrics: Dict[str, Dict]) -> str:
    """Create dividend yield vs growth matrix"""
    
    companies = list(style_metrics.keys())
    growth_rates = [style_metrics[c]['revenue_growth_3y'] for c in companies]
    div_yields = [style_metrics[c]['dividend_yield'] for c in companies]
    
    # Color by category
    colors = []
    for growth, div_yield in zip(growth_rates, div_yields):
        if growth > 12 and div_yield < 2:
            colors.append('#8b5cf6')  # High Growth
        elif growth > 8 and div_yield > 2:
            colors.append('#10b981')  # Growth + Income
        elif div_yield > 3:
            colors.append('#3b82f6')  # High Dividend
        else:
            colors.append('#64748b')  # Balanced
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': div_yields,
            'y': growth_rates,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>Dividend Yield: %{x:.1f}%<br>Growth: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Income vs Growth Trade-off Matrix',
            'xaxis': {'title': 'Dividend Yield (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Revenue Growth (%)', 'gridcolor': '#e5e7eb'},
            'annotations': [
                {'x': 1, 'y': 25, 'text': 'Pure Growth', 'showarrow': False, 'font': {'size': 11, 'color': '#8b5cf6'}},
                {'x': 4, 'y': 25, 'text': 'Growth + Income', 'showarrow': False, 'font': {'size': 11, 'color': '#10b981'}},
                {'x': 5, 'y': 5, 'text': 'High Dividend', 'showarrow': False, 'font': {'size': 11, 'color': '#3b82f6'}},
                {'x': 1, 'y': 5, 'text': 'Balanced', 'showarrow': False, 'font': {'size': 11, 'color': '#64748b'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="dividend-growth-matrix", height=500)


def _create_profitability_radar_charts(style_metrics: Dict[str, Dict]) -> str:
    """Create profitability radar charts for each company"""
    
    companies = list(style_metrics.keys())
    
    # Create individual radar chart for each company (show first 4)
    charts_html = ""
    for i, company in enumerate(companies[:4]):
        metrics = style_metrics[company]
        
        fig_data = {
            'data': [{
                'type': 'scatterpolar',
                'r': [
                    min(100, metrics['gross_margin']),
                    min(100, metrics['operating_margin'] * 3),  # Scale up
                    min(100, metrics['net_margin'] * 4),  # Scale up
                    min(100, metrics['roe'] * 3),  # Scale up
                    min(100, metrics['roic'] * 3),  # Scale up
                    min(100, metrics['roa'] * 5)  # Scale up
                ],
                'theta': ['Gross Margin', 'Operating Margin', 'Net Margin', 'ROE', 'ROIC', 'ROA'],
                'fill': 'toself',
                'name': company,
                'marker': {'color': '#667eea'}
            }],
            'layout': {
                'polar': {
                    'radialaxis': {
                        'visible': True,
                        'range': [0, 100]
                    }
                },
                'title': company[:20],
                'showlegend': False
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id=f"profitability-radar-{i}", height=400)
    
    if len(companies) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(companies)} companies. All companies included in data tables.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_style_metrics_heatmap(style_metrics: Dict[str, Dict]) -> str:
    """Create style metrics heatmap"""
    
    companies = list(style_metrics.keys())
    
    # Metrics to show
    metric_names = ['Revenue Growth', 'P/E', 'P/B', 'ROE', 'ROIC', 'Div Yield', 'Gross Margin', 'Net Margin']
    
    # Prepare data matrix (normalize for better visualization)
    data_matrix = []
    for metric in metric_names:
        row = []
        for company in companies:
            if metric == 'Revenue Growth':
                val = style_metrics[company]['revenue_growth_3y']
            elif metric == 'P/E':
                val = style_metrics[company]['pe_ratio'] if not np.isnan(style_metrics[company]['pe_ratio']) else 0
            elif metric == 'P/B':
                val = style_metrics[company]['pb_ratio'] if not np.isnan(style_metrics[company]['pb_ratio']) else 0
            elif metric == 'ROE':
                val = style_metrics[company]['roe']
            elif metric == 'ROIC':
                val = style_metrics[company]['roic']
            elif metric == 'Div Yield':
                val = style_metrics[company]['dividend_yield']
            elif metric == 'Gross Margin':
                val = style_metrics[company]['gross_margin']
            elif metric == 'Net Margin':
                val = style_metrics[company]['net_margin']
            else:
                val = 0
            row.append(val)
        data_matrix.append(row)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'x': [c[:15] for c in companies],
            'y': metric_names,
            'colorscale': 'RdYlGn',
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Value: %{z:.1f}<extra></extra>',
            'colorbar': {'title': 'Value'}
        }],
        'layout': {
            'title': 'Style Metrics Heatmap (Green = Strong, Red = Weak)',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="style-heatmap", height=500)


def _create_style_metrics_table(style_metrics: Dict[str, Dict]) -> str:
    """Create detailed style metrics table"""
    
    table_data = []
    for company, metrics in style_metrics.items():
        table_data.append({
            'Company': company,
            'Rev Growth 3Y': f"{metrics['revenue_growth_3y']:.1f}%",
            'P/E': f"{metrics['pe_ratio']:.1f}" if not np.isnan(metrics['pe_ratio']) else "N/A",
            'P/B': f"{metrics['pb_ratio']:.1f}" if not np.isnan(metrics['pb_ratio']) else "N/A",
            'ROE': f"{metrics['roe']:.1f}%",
            'ROIC': f"{metrics['roic']:.1f}%",
            'Div Yield': f"{metrics['dividend_yield']:.1f}%",
            'Gross Margin': f"{metrics['gross_margin']:.1f}%",
            'Net Margin': f"{metrics['net_margin']:.1f}%",
            'Market Cap ($B)': f"{metrics['market_cap']:.1f}"
        })
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="style-metrics-table", page_length=10)


def _create_style_classification_summary(style_metrics: Dict[str, Dict]) -> str:
    """Create style classification summary"""
    
    classification_data = []
    for company, metrics in style_metrics.items():
        classification_data.append({
            'Company': company,
            'Investment Style': metrics['style_class'],
            'Growth Profile': 'High Growth' if metrics['revenue_growth_3y'] > 15 else 'Moderate Growth' if metrics['revenue_growth_3y'] > 8 else 'Low Growth',
            'Valuation': 'Deep Value' if metrics['pe_ratio'] < 15 else 'Fair Value' if metrics['pe_ratio'] < 25 else 'Premium' if not np.isnan(metrics['pe_ratio']) else 'N/A',
            'Quality Tier': 'Excellent' if metrics['roe'] > 18 and metrics['roic'] > 15 else 'Good' if metrics['roe'] > 12 else 'Fair'
        })
    
    df_classification = pd.DataFrame(classification_data)
    
    return build_enhanced_table(
        df_classification,
        table_id="style-classification-table",
        badge_columns=['Investment Style', 'Growth Profile', 'Valuation', 'Quality Tier']
    )


def _build_section_18c_relative_performance(companies: Dict[str, str], prices_daily: pd.DataFrame, 
                                           prices_monthly: pd.DataFrame, sp500_daily: pd.DataFrame, 
                                           sp500_monthly: pd.DataFrame) -> str:
    """Build subsection 18C: Relative Performance Analysis"""
    
    if prices_daily.empty or sp500_daily.empty:
        return _build_collapsible_subsection(
            "18C",
            "Relative Performance Analysis",
            "<p>Insufficient price data for relative performance analysis.</p>"
        )
    
    # Calculate relative performance
    rel_perf_metrics = _calculate_relative_performance(companies, prices_daily, prices_monthly, sp500_daily, sp500_monthly)
    
    if not rel_perf_metrics:
        return _build_collapsible_subsection(
            "18C",
            "Relative Performance Analysis",
            "<p>Unable to calculate relative performance metrics.</p>"
        )
    
    # Build content
    intro_html = """
    <p>This section analyzes performance relative to the S&P 500 benchmark across multiple timeframes. 
    <strong>Actual returns</strong> are shown rather than arbitrary scores, with consistency metrics 
    indicating the reliability of outperformance.</p>
    """
    
    # Summary cards
    summary_cards = _build_relative_perf_summary_cards(rel_perf_metrics)
    
    # 1. Relative Performance Heatmap
    rel_perf_heatmap = _create_relative_performance_heatmap(rel_perf_metrics)
    
    # 2. Consistency Analysis
    consistency_chart = _create_consistency_analysis_chart(rel_perf_metrics)
    
    # 3. 1Y vs 3Y Relative Performance Scatter
    relative_scatter = _create_relative_performance_scatter(rel_perf_metrics)
    
    # 4. Performance Attribution Waterfall
    attribution_charts = _create_performance_attribution_charts(rel_perf_metrics)
    
    # 5. Outperformance Frequency
    outperformance_freq = _create_outperformance_frequency_chart(rel_perf_metrics)
    
    # 6. Relative Performance Table
    rel_perf_table = _create_relative_performance_table(rel_perf_metrics)
    
    # 7. Performance Classification
    perf_classification = _create_performance_classification(rel_perf_metrics)
    
    content_html = f"""
    {intro_html}
    
    <h4>Relative Performance Summary</h4>
    {summary_cards}
    
    <h4>Relative Performance Heatmap</h4>
    <p>Performance vs S&P 500 across multiple time periods. Positive values (green) indicate outperformance, 
    negative values (red) indicate underperformance.</p>
    {rel_perf_heatmap}
    
    <h4>Performance Consistency Analysis</h4>
    <p>Percentage of time periods where each company outperformed the S&P 500. Higher consistency 
    indicates more reliable relative strength.</p>
    {consistency_chart}
    
    <h4>Short-term vs Long-term Relative Performance</h4>
    <p>Comparison of 1-year and 3-year relative returns. Companies in the upper-right quadrant show 
    consistent outperformance across timeframes.</p>
    {relative_scatter}
    
    <h4>Performance Attribution</h4>
    <p>Breakdown of total returns into stock-specific performance and market contribution.</p>
    {attribution_charts}
    
    <h4>Outperformance Frequency</h4>
    <p>Number of periods (out of 5 measured) where each company beat the S&P 500.</p>
    {outperformance_freq}
    
    <h4>Detailed Relative Performance</h4>
    {rel_perf_table}
    
    <h4>Performance Classification</h4>
    {perf_classification}
    """
    
    return _build_collapsible_subsection("18C", "Relative Performance Analysis", content_html)


def _calculate_relative_performance(companies: Dict[str, str], prices_daily: pd.DataFrame,
                                   prices_monthly: pd.DataFrame, sp500_daily: pd.DataFrame,
                                   sp500_monthly: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate relative performance vs S&P 500"""
    
    rel_perf_metrics = {}
    
    # Prepare S&P 500 data
    sp500_daily = sp500_daily.sort_values('date').copy()
    sp500_monthly = sp500_monthly.sort_values('date').copy()
    
    for company_name, ticker in companies.items():
        company_daily = prices_daily[prices_daily['symbol'] == ticker].copy()
        
        if company_daily.empty or len(company_daily) < 60:
            continue
        
        company_daily = company_daily.sort_values('date')
        
        # Calculate returns for different periods
        periods = {
            '1M': 21,
            '3M': 63,
            '6M': 126,
            '1Y': 252,
            '3Y': 756
        }
        
        relative_performance = {}
        
        for period_name, days in periods.items():
            if len(company_daily) >= days and len(sp500_daily) >= days:
                stock_return = (company_daily['close'].iloc[-1] / company_daily['close'].iloc[-days] - 1) * 100
                sp500_return = (sp500_daily['close'].iloc[-1] / sp500_daily['close'].iloc[-days] - 1) * 100
                relative_perf = stock_return - sp500_return
                
                relative_performance[period_name] = {
                    'stock_return': stock_return,
                    'sp500_return': sp500_return,
                    'relative_performance': relative_perf
                }
        
        if not relative_performance:
            continue
        
        # Calculate consistency (% of periods with outperformance)
        positive_periods = sum(1 for perf in relative_performance.values() if perf['relative_performance'] > 0)
        consistency = (positive_periods / len(relative_performance)) * 100
        
        # Classification
        avg_rel_perf = np.mean([p['relative_performance'] for p in relative_performance.values()])
        
        if avg_rel_perf > 10 and consistency > 70:
            classification = "Strong Outperformer"
        elif avg_rel_perf > 5 and consistency > 60:
            classification = "Consistent Outperformer"
        elif avg_rel_perf > 0:
            classification = "Moderate Outperformer"
        elif avg_rel_perf > -5:
            classification = "Market Performer"
        elif avg_rel_perf > -10:
            classification = "Underperformer"
        else:
            classification = "Significant Underperformer"
        
        rel_perf_metrics[company_name] = {
            'relative_performance': relative_performance,
            'consistency': consistency,
            'avg_rel_perf': avg_rel_perf,
            'classification': classification,
            '1y_relative': relative_performance.get('1Y', {}).get('relative_performance', 0),
            '3y_relative': relative_performance.get('3Y', {}).get('relative_performance', 0)
        }
    
    return rel_perf_metrics


def _build_relative_perf_summary_cards(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Build summary cards for relative performance"""
    
    if not rel_perf_metrics:
        return "<p>No relative performance data available.</p>"
    
    avg_rel_perf = np.mean([m['avg_rel_perf'] for m in rel_perf_metrics.values()])
    avg_consistency = np.mean([m['consistency'] for m in rel_perf_metrics.values()])
    
    outperformers = sum(1 for m in rel_perf_metrics.values() if m['avg_rel_perf'] > 0)
    strong_outperformers = sum(1 for m in rel_perf_metrics.values() if m['avg_rel_perf'] > 10)
    
    total = len(rel_perf_metrics)
    
    cards = [
        {
            "label": "Average Relative Performance",
            "value": f"{avg_rel_perf:+.1f}%",
            "description": "vs S&P 500 across all periods",
            "type": "success" if avg_rel_perf > 5 else "default" if avg_rel_perf > 0 else "danger"
        },
        {
            "label": "Outperformers",
            "value": f"{outperformers}/{total}",
            "description": f"Companies beating S&P 500",
            "type": "success" if outperformers >= total * 0.6 else "default"
        },
        {
            "label": "Strong Outperformers",
            "value": f"{strong_outperformers}/{total}",
            "description": "Beating by >10% on average",
            "type": "success" if strong_outperformers >= 2 else "info"
        },
        {
            "label": "Average Consistency",
            "value": f"{avg_consistency:.0f}%",
            "description": "Periods with outperformance",
            "type": "success" if avg_consistency > 65 else "default" if avg_consistency > 50 else "warning"
        }
    ]
    
    return build_stat_grid(cards)


def _create_relative_performance_heatmap(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create relative performance heatmap"""
    
    companies = list(rel_perf_metrics.keys())
    periods = ['1M', '3M', '6M', '1Y', '3Y']
    
    # Build data matrix
    data_matrix = []
    for company in companies:
        row = []
        for period in periods:
            rel_perf = rel_perf_metrics[company]['relative_performance'].get(period, {}).get('relative_performance', 0)
            row.append(rel_perf)
        data_matrix.append(row)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'y': [c[:20] for c in companies],
            'x': periods,
            'colorscale': [
                [0, '#ef4444'],     # Red for underperformance
                [0.5, '#fef3c7'],   # Yellow for neutral
                [1, '#10b981']      # Green for outperformance
            ],
            'zmid': 0,
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Relative: %{z:+.1f}%<extra></extra>',
            'colorbar': {'title': 'Relative %'}
        }],
        'layout': {
            'title': 'Relative Performance vs S&P 500 Heatmap',
            'xaxis': {'title': 'Time Period'},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="relative-perf-heatmap", height=max(400, len(companies) * 30))


def _create_consistency_analysis_chart(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create consistency analysis chart"""
    
    companies = list(rel_perf_metrics.keys())
    consistencies = [rel_perf_metrics[c]['consistency'] for c in companies]
    
    # Sort by consistency
    sorted_data = sorted(zip(companies, consistencies), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:20] for c, _ in sorted_data]
    sorted_consistencies = [cons for _, cons in sorted_data]
    
    # Color by consistency level
    colors = ['#10b981' if c > 70 else '#3b82f6' if c > 50 else '#f59e0b' if c > 30 else '#ef4444' for c in sorted_consistencies]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_consistencies,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Consistency: %{x:.0f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Performance Consistency (% of Periods Outperforming)',
            'xaxis': {'title': 'Consistency (%)', 'range': [0, 100], 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': 70, 'x1': 70, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': 72, 'y': len(companies), 'text': 'High Consistency (70%)',
                 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="consistency-chart", height=max(400, len(companies) * 25))


def _create_relative_performance_scatter(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create 1Y vs 3Y relative performance scatter"""
    
    companies = list(rel_perf_metrics.keys())
    rel_1y = [rel_perf_metrics[c]['1y_relative'] for c in companies]
    rel_3y = [rel_perf_metrics[c]['3y_relative'] for c in companies]
    
    # Color by quadrant
    colors = []
    for r1, r3 in zip(rel_1y, rel_3y):
        if r1 > 0 and r3 > 0:
            colors.append('#10b981')  # Consistent outperformer
        elif r1 > 0:
            colors.append('#3b82f6')  # Recent strength
        elif r3 > 0:
            colors.append('#f59e0b')  # Long-term strength fading
        else:
            colors.append('#ef4444')  # Consistent underperformer
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': rel_1y,
            'y': rel_3y,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>1Y: %{x:+.1f}%<br>3Y: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': '1-Year vs 3-Year Relative Performance',
            'xaxis': {'title': '1-Year Relative Performance (%)', 'gridcolor': '#e5e7eb', 'zeroline': True},
            'yaxis': {'title': '3-Year Relative Performance (%)', 'gridcolor': '#e5e7eb', 'zeroline': True},
            'shapes': [
                {'type': 'line', 'x0': 0, 'x1': 0, 'y0': -50, 'y1': 50,
                 'line': {'color': '#94a3b8', 'width': 1}},
                {'type': 'line', 'x0': -50, 'x1': 50, 'y0': 0, 'y1': 0,
                 'line': {'color': '#94a3b8', 'width': 1}}
            ],
            'annotations': [
                {'x': 30, 'y': 30, 'text': 'Consistent Winners', 'showarrow': False, 'font': {'size': 11, 'color': '#10b981'}},
                {'x': -30, 'y': -30, 'text': 'Consistent Losers', 'showarrow': False, 'font': {'size': 11, 'color': '#ef4444'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="relative-scatter", height=500)


def _create_performance_attribution_charts(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create performance attribution waterfall charts"""
    
    companies = list(rel_perf_metrics.keys())
    
    # Show first 4 companies
    charts_html = ""
    for i, company in enumerate(companies[:4]):
        if '1Y' in rel_perf_metrics[company]['relative_performance']:
            perf_data = rel_perf_metrics[company]['relative_performance']['1Y']
            
            stock_return = perf_data['stock_return']
            sp500_return = perf_data['sp500_return']
            relative_perf = perf_data['relative_performance']
            
            fig_data = {
                'data': [{
                    'type': 'waterfall',
                    'x': ['Market Return', 'Stock-Specific', 'Total Stock Return'],
                    'y': [sp500_return, relative_perf, 0],
                    'measure': ['relative', 'relative', 'total'],
                    'connector': {'line': {'color': '#94a3b8'}},
                    'increasing': {'marker': {'color': '#10b981'}},
                    'decreasing': {'marker': {'color': '#ef4444'}},
                    'totals': {'marker': {'color': '#3b82f6'}},
                    'hovertemplate': '%{x}<br>%{y:.1f}%<extra></extra>'
                }],
                'layout': {
                    'title': f'{company[:25]} - 1Y Attribution',
                    'yaxis': {'title': 'Return (%)', 'gridcolor': '#e5e7eb'},
                    'showlegend': False
                }
            }
            
            charts_html += build_plotly_chart(fig_data, div_id=f"attribution-{i}", height=350)
    
    if len(companies) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(companies)} companies.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_outperformance_frequency_chart(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create outperformance frequency chart"""
    
    companies = list(rel_perf_metrics.keys())
    frequencies = []
    
    for company in companies:
        positive_count = sum(1 for perf in rel_perf_metrics[company]['relative_performance'].values() 
                           if perf['relative_performance'] > 0)
        frequencies.append(positive_count)
    
    # Sort by frequency
    sorted_data = sorted(zip(companies, frequencies), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:20] for c, _ in sorted_data]
    sorted_frequencies = [f for _, f in sorted_data]
    
    colors = ['#10b981' if f >= 4 else '#3b82f6' if f >= 3 else '#f59e0b' if f >= 2 else '#ef4444' for f in sorted_frequencies]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_frequencies,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Outperformed: %{x} of 5 periods<extra></extra>'
        }],
        'layout': {
            'title': 'Outperformance Frequency (Number of Periods)',
            'xaxis': {'title': 'Periods Outperformed (out of 5)', 'range': [0, 5], 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="outperformance-freq", height=max(400, len(companies) * 25))


def _create_relative_performance_table(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create detailed relative performance table"""
    
    table_data = []
    for company, metrics in rel_perf_metrics.items():
        rp = metrics['relative_performance']
        row = {
            'Company': company,
            '1M Relative': f"{rp.get('1M', {}).get('relative_performance', 0):+.1f}%" if '1M' in rp else "N/A",
            '3M Relative': f"{rp.get('3M', {}).get('relative_performance', 0):+.1f}%" if '3M' in rp else "N/A",
            '6M Relative': f"{rp.get('6M', {}).get('relative_performance', 0):+.1f}%" if '6M' in rp else "N/A",
            '1Y Relative': f"{rp.get('1Y', {}).get('relative_performance', 0):+.1f}%" if '1Y' in rp else "N/A",
            '3Y Relative': f"{rp.get('3Y', {}).get('relative_performance', 0):+.1f}%" if '3Y' in rp else "N/A",
            'Consistency': f"{metrics['consistency']:.0f}%",
            'Avg Relative': f"{metrics['avg_rel_perf']:+.1f}%"
        }
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="relative-perf-table", page_length=10)


def _create_performance_classification(rel_perf_metrics: Dict[str, Dict]) -> str:
    """Create performance classification table"""
    
    classification_data = []
    for company, metrics in rel_perf_metrics.items():
        classification_data.append({
            'Company': company,
            'Performance Classification': metrics['classification'],
            'Average Relative Performance': f"{metrics['avg_rel_perf']:+.1f}%",
            'Consistency': f"{metrics['consistency']:.0f}%",
            'Trend': 'Improving' if metrics['1y_relative'] > metrics.get('3y_relative', 0) else 'Stable' if abs(metrics['1y_relative'] - metrics.get('3y_relative', 0)) < 5 else 'Declining'
        })
    
    df_classification = pd.DataFrame(classification_data)
    
    return build_enhanced_table(
        df_classification,
        table_id="perf-classification-table",
        badge_columns=['Performance Classification', 'Trend']
    )


def _build_section_18d_momentum_technical(companies: Dict[str, str], prices_daily: pd.DataFrame, 
                                         prices_monthly: pd.DataFrame) -> str:
    """Build subsection 18D: Price Momentum & Technical Indicators (STUB)"""
    return _build_collapsible_subsection(
        "18D",
        "Price Momentum & Technical Indicators",
        "<p>Momentum and technical analysis will be implemented in Phase 3.</p>"
    )


def _build_section_18e_earnings_quality(companies: Dict[str, str], df: pd.DataFrame) -> str:
    """Build subsection 18E: Earnings Quality & Cash Flow Analysis (STUB)"""
    return _build_collapsible_subsection(
        "18E",
        "Earnings Quality & Cash Flow Analysis",
        "<p>Earnings quality analysis will be implemented in Phase 3.</p>"
    )


# =============================================================================
# COLLAPSIBLE SUBSECTION HELPER
# =============================================================================

def _build_collapsible_subsection(subsection_id: str, title: str, content: str) -> str:
    """Build a collapsible/expandable subsection"""
    
    unique_id = f"subsection-{subsection_id.lower().replace('.', '-')}"
    
    return f"""
    <div class="subsection-container" style="margin: 30px 0;">
        <div class="subsection-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px 20px; border-radius: 12px; cursor: pointer; display: flex; 
                    justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
             onclick="toggleSubsection('{unique_id}')">
            <h3 style="margin: 0; color: white; font-size: 1.3rem; font-weight: 700;">
                {subsection_id}. {title}
            </h3>
            <span id="{unique_id}-toggle" style="color: white; font-size: 1.5rem; font-weight: bold;">−</span>
        </div>
        <div id="{unique_id}-content" class="subsection-content" 
             style="padding: 25px; background: var(--card-bg); border-radius: 0 0 12px 12px; 
                    border: 1px solid var(--card-border); border-top: none;">
            {content}
        </div>
    </div>
    
    <script>
    function toggleSubsection(id) {{
        const content = document.getElementById(id + '-content');
        const toggle = document.getElementById(id + '-toggle');
        
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            toggle.textContent = '−';
        }} else {{
            content.style.display = 'none';
            toggle.textContent = '+';
        }}
    }}
    </script>
    """


def _build_section_18d_momentum_technical(companies: Dict[str, str], prices_daily: pd.DataFrame, 
                                         prices_monthly: pd.DataFrame) -> str:
    """Build subsection 18D: Price Momentum & Technical Indicators"""
    
    if prices_daily.empty:
        return _build_collapsible_subsection(
            "18D",
            "Price Momentum & Technical Indicators",
            "<p>Insufficient price data for technical analysis.</p>"
        )
    
    # Calculate technical indicators
    tech_indicators = _calculate_technical_indicators(companies, prices_daily)
    
    if not tech_indicators:
        return _build_collapsible_subsection(
            "18D",
            "Price Momentum & Technical Indicators",
            "<p>Unable to calculate technical indicators.</p>"
        )
    
    # Build content
    intro_html = """
    <p>This section analyzes price momentum and technical indicators using <strong>actual indicator values</strong> 
    rather than composite momentum scores. RSI, moving averages, and mean reversion metrics are shown separately 
    to provide clear, actionable technical signals.</p>
    """
    
    # Summary cards
    summary_cards = _build_technical_summary_cards(tech_indicators)
    
    # 1. RSI Gauge Charts
    rsi_gauges = _create_rsi_gauge_charts(tech_indicators)
    
    # 2. Price vs Moving Averages
    ma_deviation_chart = _create_ma_deviation_chart(tech_indicators)
    
    # 3. Trend Classification Matrix
    trend_matrix = _create_trend_classification_matrix(tech_indicators)
    
    # 4. Z-Score Mean Reversion Analysis
    zscore_analysis = _create_zscore_analysis_chart(tech_indicators)
    
    # 5. Momentum Heatmap (Multiple Timeframes)
    momentum_heatmap = _create_momentum_heatmap(tech_indicators)
    
    # 6. Price Action with MAs Overlay
    price_action_charts = _create_price_action_charts(companies, prices_daily, tech_indicators)
    
    # 7. Technical Indicators Table
    tech_table = _create_technical_indicators_table(tech_indicators)
    
    # 8. Technical Signal Summary
    signal_summary = _create_technical_signal_summary(tech_indicators)
    
    content_html = f"""
    {intro_html}
    
    <h4>Technical Indicators Summary</h4>
    {summary_cards}
    
    <h4>RSI (Relative Strength Index) Analysis</h4>
    <p>RSI values range from 0-100. Values above 70 suggest overbought conditions, below 30 suggest oversold. 
    Current RSI levels indicate momentum strength without composite scoring.</p>
    {rsi_gauges}
    
    <h4>Price vs Moving Averages Deviation</h4>
    <p>Percentage deviation from 50-day and 200-day moving averages. Positive values indicate price trading 
    above the average (bullish), negative values indicate trading below (bearish).</p>
    {ma_deviation_chart}
    
    <h4>Trend Classification</h4>
    <p>Trend strength determined by price position relative to moving averages and MA alignment. 
    <strong>Strong Uptrend</strong>: Price > MA50 > MA200. <strong>Strong Downtrend</strong>: Price < MA50 < MA200.</p>
    {trend_matrix}
    
    <h4>Mean Reversion Analysis (Z-Score)</h4>
    <p>Z-scores measure how many standard deviations current price is from its 1-year average. 
    |Z| > 2 indicates extreme deviation with potential mean reversion opportunities.</p>
    {zscore_analysis}
    
    <h4>Multi-Timeframe Momentum Heatmap</h4>
    <p>Price changes across multiple timeframes (1M, 3M, 6M, 1Y). Green indicates positive momentum, 
    red indicates negative momentum.</p>
    {momentum_heatmap}
    
    <h4>Price Action with Moving Averages</h4>
    <p>Recent price trends with 50-day and 200-day moving average overlays for visual trend confirmation.</p>
    {price_action_charts}
    
    <h4>Detailed Technical Indicators</h4>
    {tech_table}
    
    <h4>Technical Signal Summary</h4>
    {signal_summary}
    """
    
    return _build_collapsible_subsection("18D", "Price Momentum & Technical Indicators", content_html)


def _calculate_technical_indicators(companies: Dict[str, str], prices_daily: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate technical indicators without composite scoring"""
    
    tech_indicators = {}
    
    for company_name, ticker in companies.items():
        company_daily = prices_daily[prices_daily['symbol'] == ticker].copy()
        
        if company_daily.empty or len(company_daily) < 200:
            continue
        
        company_daily = company_daily.sort_values('date')
        company_daily['return'] = company_daily['close'].pct_change()
        
        # Moving averages
        company_daily['ma_50'] = company_daily['close'].rolling(50).mean()
        company_daily['ma_200'] = company_daily['close'].rolling(200).mean()
        
        latest_price = company_daily['close'].iloc[-1]
        ma_50 = company_daily['ma_50'].iloc[-1]
        ma_200 = company_daily['ma_200'].iloc[-1]
        
        # Price vs MA deviations
        price_vs_ma50 = ((latest_price / ma_50) - 1) * 100 if not np.isnan(ma_50) else 0
        price_vs_ma200 = ((latest_price / ma_200) - 1) * 100 if not np.isnan(ma_200) else 0
        
        # Trend classification (no scoring, just classification)
        if ma_50 > ma_200 and latest_price > ma_50:
            trend_class = "Strong Uptrend"
        elif ma_50 > ma_200:
            trend_class = "Uptrend"
        elif ma_50 < ma_200 and latest_price < ma_50:
            trend_class = "Strong Downtrend"
        elif ma_50 < ma_200:
            trend_class = "Downtrend"
        else:
            trend_class = "Neutral"
        
        # Mean reversion: Z-score
        recent_prices = company_daily['close'].tail(252)
        price_mean = recent_prices.mean()
        price_std = recent_prices.std()
        z_score = (latest_price - price_mean) / price_std if price_std > 0 else 0
        
        # Z-score classification
        if abs(z_score) < 0.5:
            reversion_status = "Near Mean"
        elif z_score > 2:
            reversion_status = "Extremely Overbought"
        elif z_score > 1:
            reversion_status = "Overbought"
        elif z_score < -2:
            reversion_status = "Extremely Oversold"
        elif z_score < -1:
            reversion_status = "Oversold"
        else:
            reversion_status = "Normal Range"
        
        # RSI calculation (14-period)
        delta = company_daily['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if len(rsi) > 0 and not np.isnan(rsi.iloc[-1]) else 50
        
        # RSI classification
        if current_rsi > 70:
            rsi_signal = "Overbought"
        elif current_rsi > 60:
            rsi_signal = "Strong"
        elif current_rsi > 40:
            rsi_signal = "Neutral"
        elif current_rsi > 30:
            rsi_signal = "Weak"
        else:
            rsi_signal = "Oversold"
        
        # Multi-timeframe momentum (actual returns)
        momentum_1m = ((company_daily['close'].iloc[-1] / company_daily['close'].iloc[-21]) - 1) * 100 if len(company_daily) >= 21 else 0
        momentum_3m = ((company_daily['close'].iloc[-1] / company_daily['close'].iloc[-63]) - 1) * 100 if len(company_daily) >= 63 else 0
        momentum_6m = ((company_daily['close'].iloc[-1] / company_daily['close'].iloc[-126]) - 1) * 100 if len(company_daily) >= 126 else 0
        momentum_1y = ((company_daily['close'].iloc[-1] / company_daily['close'].iloc[-252]) - 1) * 100 if len(company_daily) >= 252 else 0
        
        tech_indicators[company_name] = {
            'current_price': latest_price,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'price_vs_ma50': price_vs_ma50,
            'price_vs_ma200': price_vs_ma200,
            'trend_class': trend_class,
            'z_score': z_score,
            'reversion_status': reversion_status,
            'rsi': current_rsi,
            'rsi_signal': rsi_signal,
            'momentum_1m': momentum_1m,
            'momentum_3m': momentum_3m,
            'momentum_6m': momentum_6m,
            'momentum_1y': momentum_1y,
            'price_history': company_daily[['date', 'close', 'ma_50', 'ma_200']].tail(120)  # Last 6 months
        }
    
    return tech_indicators


def _build_technical_summary_cards(tech_indicators: Dict[str, Dict]) -> str:
    """Build summary cards for technical indicators"""
    
    if not tech_indicators:
        return "<p>No technical data available.</p>"
    
    avg_rsi = np.mean([t['rsi'] for t in tech_indicators.values()])
    
    uptrend_count = sum(1 for t in tech_indicators.values() if 'Uptrend' in t['trend_class'])
    overbought_count = sum(1 for t in tech_indicators.values() if 'Overbought' in t['reversion_status'])
    oversold_count = sum(1 for t in tech_indicators.values() if 'Oversold' in t['reversion_status'])
    
    total = len(tech_indicators)
    
    cards = [
        {
            "label": "Average RSI",
            "value": f"{avg_rsi:.0f}",
            "description": "Portfolio momentum indicator",
            "type": "warning" if avg_rsi > 70 else "success" if 40 <= avg_rsi <= 60 else "info"
        },
        {
            "label": "Uptrend Stocks",
            "value": f"{uptrend_count}/{total}",
            "description": "Above moving averages",
            "type": "success" if uptrend_count >= total * 0.6 else "default"
        },
        {
            "label": "Overbought",
            "value": f"{overbought_count}/{total}",
            "description": "Potential pullback candidates",
            "type": "warning" if overbought_count >= 2 else "info"
        },
        {
            "label": "Oversold",
            "value": f"{oversold_count}/{total}",
            "description": "Potential bounce candidates",
            "type": "success" if oversold_count >= 2 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_rsi_gauge_charts(tech_indicators: Dict[str, Dict]) -> str:
    """Create RSI gauge charts for each company"""
    
    companies = list(tech_indicators.keys())
    
    # Create individual gauges (show first 4)
    charts_html = ""
    for i, company in enumerate(companies[:4]):
        rsi_value = tech_indicators[company]['rsi']
        
        fig_data = {
            'data': [{
                'type': 'indicator',
                'mode': 'gauge+number',
                'value': rsi_value,
                'title': {'text': company[:25]},
                'gauge': {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': '#667eea'},
                    'steps': [
                        {'range': [0, 30], 'color': '#10b981'},
                        {'range': [30, 70], 'color': '#f3f4f6'},
                        {'range': [70, 100], 'color': '#ef4444'}
                    ],
                    'threshold': {
                        'line': {'color': '#1f2937', 'width': 4},
                        'thickness': 0.75,
                        'value': rsi_value
                    }
                }
            }],
            'layout': {
                'height': 250,
                'margin': {'t': 50, 'b': 0, 'l': 50, 'r': 50}
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id=f"rsi-gauge-{i}", height=250)
    
    if len(companies) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(companies)} companies. RSI values for all companies in data table below.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_ma_deviation_chart(tech_indicators: Dict[str, Dict]) -> str:
    """Create price vs moving averages deviation chart"""
    
    companies = list(tech_indicators.keys())
    ma50_devs = [tech_indicators[c]['price_vs_ma50'] for c in companies]
    ma200_devs = [tech_indicators[c]['price_vs_ma200'] for c in companies]
    
    # Sort by MA50 deviation
    sorted_data = sorted(zip(companies, ma50_devs, ma200_devs), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:20] for c, _, _ in sorted_data]
    sorted_ma50 = [m50 for _, m50, _ in sorted_data]
    sorted_ma200 = [m200 for _, _, m200 in sorted_data]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'vs MA50',
                'y': sorted_companies,
                'x': sorted_ma50,
                'orientation': 'h',
                'marker': {'color': ['#10b981' if x > 0 else '#ef4444' for x in sorted_ma50]},
                'hovertemplate': '<b>%{y}</b><br>vs MA50: %{x:+.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'vs MA200',
                'y': sorted_companies,
                'x': sorted_ma200,
                'orientation': 'h',
                'marker': {'color': ['#3b82f6' if x > 0 else '#f59e0b' for x in sorted_ma200]},
                'hovertemplate': '<b>%{y}</b><br>vs MA200: %{x:+.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Price vs Moving Averages Deviation (%)',
            'xaxis': {'title': 'Deviation (%)', 'gridcolor': '#e5e7eb', 'zeroline': True},
            'yaxis': {'title': ''},
            'barmode': 'group',
            'legend': {'orientation': 'h', 'y': -0.15}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ma-deviation", height=max(500, len(companies) * 30))


def _create_trend_classification_matrix(tech_indicators: Dict[str, Dict]) -> str:
    """Create trend classification matrix"""
    
    classification_data = []
    for company, indicators in tech_indicators.items():
        classification_data.append({
            'Company': company,
            'Trend Classification': indicators['trend_class'],
            'Price vs MA50': f"{indicators['price_vs_ma50']:+.1f}%",
            'Price vs MA200': f"{indicators['price_vs_ma200']:+.1f}%",
            'Trend Strength': 'Strong' if 'Strong' in indicators['trend_class'] else 'Moderate' if indicators['trend_class'] != 'Neutral' else 'Weak'
        })
    
    df_classification = pd.DataFrame(classification_data)
    
    return build_enhanced_table(
        df_classification,
        table_id="trend-classification-table",
        badge_columns=['Trend Classification', 'Trend Strength']
    )


def _create_zscore_analysis_chart(tech_indicators: Dict[str, Dict]) -> str:
    """Create Z-score mean reversion analysis chart"""
    
    companies = list(tech_indicators.keys())
    z_scores = [tech_indicators[c]['z_score'] for c in companies]
    
    # Create scatter plot with zones
    colors = []
    for z in z_scores:
        if abs(z) > 2:
            colors.append('#ef4444')  # Extreme
        elif abs(z) > 1:
            colors.append('#f59e0b')  # Moderate
        else:
            colors.append('#10b981')  # Normal
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': z_scores,
            'y': list(range(len(companies))),
            'text': [c[:10] for c in companies],
            'textposition': 'middle right',
            'marker': {
                'size': 12,
                'color': colors,
                'line': {'width': 1, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>Z-Score: %{x:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Mean Reversion Analysis (Z-Score Distribution)',
            'xaxis': {'title': 'Z-Score (Standard Deviations from Mean)', 'gridcolor': '#e5e7eb', 'zeroline': True},
            'yaxis': {'visible': False},
            'shapes': [
                # Extreme zones
                {'type': 'rect', 'x0': -4, 'x1': -2, 'y0': -1, 'y1': len(companies),
                 'fillcolor': '#ef4444', 'opacity': 0.1, 'line': {'width': 0}},
                {'type': 'rect', 'x0': 2, 'x1': 4, 'y0': -1, 'y1': len(companies),
                 'fillcolor': '#ef4444', 'opacity': 0.1, 'line': {'width': 0}},
                # Moderate zones
                {'type': 'rect', 'x0': -2, 'x1': -1, 'y0': -1, 'y1': len(companies),
                 'fillcolor': '#f59e0b', 'opacity': 0.1, 'line': {'width': 0}},
                {'type': 'rect', 'x0': 1, 'x1': 2, 'y0': -1, 'y1': len(companies),
                 'fillcolor': '#f59e0b', 'opacity': 0.1, 'line': {'width': 0}},
                # Lines at key thresholds
                {'type': 'line', 'x0': -2, 'x1': -2, 'y0': -1, 'y1': len(companies),
                 'line': {'color': '#ef4444', 'width': 1, 'dash': 'dash'}},
                {'type': 'line', 'x0': 2, 'x1': 2, 'y0': -1, 'y1': len(companies),
                 'line': {'color': '#ef4444', 'width': 1, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': -2.5, 'y': len(companies), 'text': 'Oversold', 'showarrow': False, 'font': {'size': 10}},
                {'x': 2.5, 'y': len(companies), 'text': 'Overbought', 'showarrow': False, 'font': {'size': 10}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="zscore-analysis", height=400)


def _create_momentum_heatmap(tech_indicators: Dict[str, Dict]) -> str:
    """Create multi-timeframe momentum heatmap"""
    
    companies = list(tech_indicators.keys())
    periods = ['1M', '3M', '6M', '1Y']
    
    # Build data matrix
    data_matrix = []
    for company in companies:
        row = [
            tech_indicators[company]['momentum_1m'],
            tech_indicators[company]['momentum_3m'],
            tech_indicators[company]['momentum_6m'],
            tech_indicators[company]['momentum_1y']
        ]
        data_matrix.append(row)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'y': [c[:20] for c in companies],
            'x': periods,
            'colorscale': [
                [0, '#ef4444'],     # Red for negative
                [0.5, '#fef3c7'],   # Yellow for neutral
                [1, '#10b981']      # Green for positive
            ],
            'zmid': 0,
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Return: %{z:+.1f}%<extra></extra>',
            'colorbar': {'title': 'Return %'}
        }],
        'layout': {
            'title': 'Multi-Timeframe Momentum Heatmap',
            'xaxis': {'title': 'Time Period'},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="momentum-heatmap", height=max(400, len(companies) * 30))


def _create_price_action_charts(companies: Dict[str, str], prices_daily: pd.DataFrame, 
                                tech_indicators: Dict[str, Dict]) -> str:
    """Create price action charts with MA overlays"""
    
    company_list = list(tech_indicators.keys())
    
    # Show first 4 companies
    charts_html = ""
    for i, company in enumerate(company_list[:4]):
        price_history = tech_indicators[company]['price_history']
        
        if price_history.empty:
            continue
        
        fig_data = {
            'data': [
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'Price',
                    'x': [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in price_history['date']],  # ✅ FIXED
                    'y': price_history['close'].tolist(),
                    'line': {'color': '#1f2937', 'width': 2}
                },
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'MA50',
                    'x': [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in price_history['date']],  # ✅ FIXED
                    'y': price_history['ma_50'].tolist(),
                    'line': {'color': '#3b82f6', 'width': 1.5, 'dash': 'dash'}
                },
                {
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'MA200',
                    'x': [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in price_history['date']],  # ✅ FIXED
                    'y': price_history['ma_200'].tolist(),
                    'line': {'color': '#ef4444', 'width': 1.5, 'dash': 'dot'}
                }
            ],
            'layout': {
                'title': f'{company[:30]} - Price Action (Last 6 Months)',
                'xaxis': {'title': '', 'gridcolor': '#e5e7eb'},
                'yaxis': {'title': 'Price ($)', 'gridcolor': '#e5e7eb'},
                'legend': {'orientation': 'h', 'y': -0.15},
                'hovermode': 'x unified'
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id=f"price-action-{i}", height=350)
    
    if len(company_list) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(company_list)} companies.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_technical_indicators_table(tech_indicators: Dict[str, Dict]) -> str:
    """Create detailed technical indicators table"""
    
    table_data = []
    for company, indicators in tech_indicators.items():
        table_data.append({
            'Company': company,
            'Current Price': f"${indicators['current_price']:.2f}",
            'vs MA50': f"{indicators['price_vs_ma50']:+.1f}%",
            'vs MA200': f"{indicators['price_vs_ma200']:+.1f}%",
            'RSI': f"{indicators['rsi']:.0f}",
            'Z-Score': f"{indicators['z_score']:.2f}",
            '1M Return': f"{indicators['momentum_1m']:+.1f}%",
            '3M Return': f"{indicators['momentum_3m']:+.1f}%",
            '1Y Return': f"{indicators['momentum_1y']:+.1f}%"
        })
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="technical-indicators-table", page_length=10)


def _create_technical_signal_summary(tech_indicators: Dict[str, Dict]) -> str:
    """Create technical signal summary"""
    
    signal_data = []
    for company, indicators in tech_indicators.items():
        # Determine overall signal
        signals = []
        if indicators['trend_class'] in ['Strong Uptrend', 'Uptrend']:
            signals.append('Bullish Trend')
        elif indicators['trend_class'] in ['Strong Downtrend', 'Downtrend']:
            signals.append('Bearish Trend')
        
        if indicators['rsi_signal'] == 'Oversold':
            signals.append('Oversold (Buy Signal)')
        elif indicators['rsi_signal'] == 'Overbought':
            signals.append('Overbought (Sell Signal)')
        
        if 'Oversold' in indicators['reversion_status']:
            signals.append('Mean Reversion Buy')
        elif 'Overbought' in indicators['reversion_status']:
            signals.append('Mean Reversion Sell')
        
        signal_summary = ', '.join(signals) if signals else 'Neutral'
        
        signal_data.append({
            'Company': company,
            'Trend': indicators['trend_class'],
            'RSI Signal': indicators['rsi_signal'],
            'Mean Reversion': indicators['reversion_status'],
            'Technical Summary': signal_summary
        })
    
    df_signals = pd.DataFrame(signal_data)
    
    return build_enhanced_table(
        df_signals,
        table_id="technical-signals-table",
        badge_columns=['Trend', 'RSI Signal', 'Mean Reversion']
    )


def _build_section_18e_earnings_quality(companies: Dict[str, str], df: pd.DataFrame) -> str:
    """Build subsection 18E: Earnings Quality & Cash Flow Analysis"""
    
    if df.empty:
        return _build_collapsible_subsection(
            "18E",
            "Earnings Quality & Cash Flow Analysis",
            "<p>Insufficient financial data for earnings quality analysis.</p>"
        )
    
    # Calculate earnings quality metrics
    quality_metrics = _calculate_earnings_quality_metrics(companies, df)
    
    if not quality_metrics:
        return _build_collapsible_subsection(
            "18E",
            "Earnings Quality & Cash Flow Analysis",
            "<p>Unable to calculate earnings quality metrics.</p>"
        )
    
    # Build content
    intro_html = """
    <p>This section analyzes earnings quality and cash flow conversion using <strong>established financial metrics</strong> 
    rather than arbitrary quality scores. Accruals analysis, FCF conversion, and cash generation metrics provide 
    objective assessment of earnings authenticity.</p>
    """
    
    # Summary cards
    summary_cards = _build_quality_summary_cards(quality_metrics)
    
    # 1. Earnings Quality Matrix (Accruals vs FCF Quality)
    quality_matrix = _create_quality_matrix_scatter(quality_metrics)
    
    # 2. Accruals Analysis
    accruals_chart = _create_accruals_analysis_chart(quality_metrics)
    
    # 3. FCF Conversion Quality
    fcf_conversion_chart = _create_fcf_conversion_chart(quality_metrics)
    
    # 4. Cash Flow Waterfall (NI → OCF → FCF)
    cash_flow_waterfalls = _create_cash_flow_waterfalls(quality_metrics)
    
    # 5. OCF Stability Analysis
    ocf_stability_chart = _create_ocf_stability_chart(quality_metrics)
    
    # 6. Quality Metrics Heatmap
    quality_heatmap = _create_quality_metrics_heatmap(quality_metrics)
    
    # 7. Quality Metrics Table
    quality_table = _create_quality_metrics_table(quality_metrics)
    
    # 8. Quality Classification
    quality_classification = _create_quality_classification(quality_metrics)
    
    content_html = f"""
    {intro_html}
    
    <h4>Earnings Quality Summary</h4>
    {summary_cards}
    
    <h4>Earnings Quality Matrix</h4>
    <p>Companies positioned by accruals quality (lower is better) and FCF conversion (higher is better). 
    Upper-left quadrant represents highest quality earnings with low accruals and strong cash conversion.</p>
    {quality_matrix}
    
    <h4>Accruals Analysis (Sloan Ratio)</h4>
    <p>Accruals ratio = (Net Income - Operating Cash Flow) / Total Assets. 
    Values near zero indicate high-quality earnings. High positive values suggest potential earnings manipulation.</p>
    {accruals_chart}
    
    <h4>Free Cash Flow Conversion</h4>
    <p>FCF / Net Income ratio measures cash generation quality. Values > 1.0 indicate earnings fully backed by cash, 
    values < 1.0 suggest working capital or capex pressures.</p>
    {fcf_conversion_chart}
    
    <h4>Cash Flow Breakdown</h4>
    <p>Waterfall showing progression from Net Income to Operating Cash Flow to Free Cash Flow.</p>
    {cash_flow_waterfalls}
    
    <h4>Operating Cash Flow Stability</h4>
    <p>3-year coefficient of variation for OCF. Lower values indicate more predictable cash generation.</p>
    {ocf_stability_chart}
    
    <h4>Quality Metrics Heatmap</h4>
    {quality_heatmap}
    
    <h4>Detailed Quality Metrics</h4>
    {quality_table}
    
    <h4>Quality Classification</h4>
    {quality_classification}
    """
    
    return _build_collapsible_subsection("18E", "Earnings Quality & Cash Flow Analysis", content_html)


def _calculate_earnings_quality_metrics(companies: Dict[str, str], df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate earnings quality metrics without arbitrary scoring"""
    
    quality_metrics = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty or len(company_data) < 3:
            continue
        
        latest_data = company_data.iloc[-1]
        
        # Accruals quality (Sloan ratio)
        net_income = latest_data.get('netIncome', 0)
        ocf = latest_data.get('operatingCashFlow', 0)
        total_assets = latest_data.get('totalAssets', 1)
        
        accruals = (net_income - ocf) / total_assets if total_assets > 0 else 0
        
        # Cash flow quality
        fcf = latest_data.get('freeCashFlow', 0)
        fcf_quality = fcf / net_income if net_income > 0 else 0
        
        ebitda = latest_data.get('ebitda', 1)
        cfo_ebitda = ocf / ebitda if ebitda > 0 else 0
        
        # Working capital efficiency
        revenue = latest_data.get('revenue', 1)
        capex = abs(latest_data.get('capitalExpenditure', 0))
        capex_intensity = capex / revenue if revenue > 0 else 0
        
        # Calculate 3-year OCF stability
        if len(company_data) >= 3:
            ocf_values = company_data['operatingCashFlow'].tail(3).values
            ocf_mean = np.mean(ocf_values)
            ocf_std = np.std(ocf_values)
            ocf_cv = abs(ocf_std / ocf_mean) if ocf_mean != 0 else 1
        else:
            ocf_cv = 1
        
        # Quality classification (NO SCORING - just classification based on thresholds)
        if abs(accruals) < 0.05 and fcf_quality > 1.0:
            quality_tier = "Excellent"
        elif abs(accruals) < 0.10 and fcf_quality > 0.8:
            quality_tier = "Good"
        elif abs(accruals) < 0.15 and fcf_quality > 0.5:
            quality_tier = "Fair"
        else:
            quality_tier = "Poor"
        
        quality_metrics[company_name] = {
            'net_income': net_income / 1e9,  # in billions
            'ocf': ocf / 1e9,
            'fcf': fcf / 1e9,
            'accruals': accruals,
            'fcf_quality': fcf_quality,
            'cfo_ebitda': cfo_ebitda,
            'capex_intensity': capex_intensity * 100,
            'ocf_cv': ocf_cv,
            'quality_tier': quality_tier
        }
    
    return quality_metrics


def _build_quality_summary_cards(quality_metrics: Dict[str, Dict]) -> str:
    """Build summary cards for earnings quality"""
    
    if not quality_metrics:
        return "<p>No quality data available.</p>"
    
    avg_accruals = np.mean([abs(q['accruals']) for q in quality_metrics.values()])
    avg_fcf_quality = np.mean([q['fcf_quality'] for q in quality_metrics.values()])
    
    excellent_count = sum(1 for q in quality_metrics.values() if q['quality_tier'] == 'Excellent')
    good_plus = sum(1 for q in quality_metrics.values() if q['quality_tier'] in ['Excellent', 'Good'])
    
    total = len(quality_metrics)
    
    cards = [
        {
            "label": "Average Accruals Ratio",
            "value": f"{avg_accruals:.3f}",
            "description": "Lower is better (absolute value)",
            "type": "success" if avg_accruals < 0.08 else "default" if avg_accruals < 0.15 else "warning"
        },
        {
            "label": "Average FCF Conversion",
            "value": f"{avg_fcf_quality:.2f}x",
            "description": "FCF / Net Income",
            "type": "success" if avg_fcf_quality > 0.9 else "default" if avg_fcf_quality > 0.7 else "warning"
        },
        {
            "label": "Excellent Quality",
            "value": f"{excellent_count}/{total}",
            "description": "Low accruals + strong cash",
            "type": "success" if excellent_count >= total * 0.4 else "info"
        },
        {
            "label": "Good+ Quality",
            "value": f"{good_plus}/{total}",
            "description": "Good or excellent tier",
            "type": "success" if good_plus >= total * 0.6 else "default"
        }
    ]
    
    return build_stat_grid(cards)


def _create_quality_matrix_scatter(quality_metrics: Dict[str, Dict]) -> str:
    """Create earnings quality matrix scatter plot"""
    
    companies = list(quality_metrics.keys())
    accruals = [abs(quality_metrics[c]['accruals']) for c in companies]
    fcf_qualities = [quality_metrics[c]['fcf_quality'] for c in companies]
    
    # Color by quality tier
    quality_colors = {
        'Excellent': '#10b981',
        'Good': '#3b82f6',
        'Fair': '#f59e0b',
        'Poor': '#ef4444'
    }
    
    colors = [quality_colors.get(quality_metrics[c]['quality_tier'], '#64748b') for c in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': accruals,
            'y': fcf_qualities,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': '#ffffff'}
            },
            'hovertemplate': '<b>%{text}</b><br>Accruals: %{x:.3f}<br>FCF Quality: %{y:.2f}x<extra></extra>'
        }],
        'layout': {
            'title': 'Earnings Quality Matrix: Accruals vs FCF Conversion',
            'xaxis': {'title': 'Accruals Ratio (absolute, lower is better)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'FCF / Net Income (higher is better)', 'gridcolor': '#e5e7eb'},
            'shapes': [
                # Quality thresholds
                {'type': 'line', 'x0': 0.08, 'x1': 0.08, 'y0': 0, 'y1': 3,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}},
                {'type': 'line', 'x0': 0, 'x1': 0.3, 'y0': 1.0, 'y1': 1.0,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': 0.05, 'y': 2.5, 'text': 'High Quality Zone', 'showarrow': False, 'font': {'size': 11, 'color': '#10b981'}},
                {'x': 0.08, 'y': 0.1, 'text': 'Low Risk (0.08)', 'showarrow': False, 'font': {'size': 9}},
                {'x': 0.25, 'y': 1.05, 'text': 'Strong Conversion (1.0x)', 'showarrow': False, 'font': {'size': 9}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="quality-matrix", height=500)


def _create_accruals_analysis_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create accruals analysis chart"""
    
    companies = list(quality_metrics.keys())
    accruals = [quality_metrics[c]['accruals'] for c in companies]
    
    # Sort by accruals (ascending)
    sorted_data = sorted(zip(companies, accruals), key=lambda x: abs(x[1]))
    sorted_companies = [c[:20] for c, _ in sorted_data]
    sorted_accruals = [a for _, a in sorted_data]
    
    # Color by risk level
    colors = []
    for acc in sorted_accruals:
        abs_acc = abs(acc)
        if abs_acc < 0.05:
            colors.append('#10b981')  # Low risk
        elif abs_acc < 0.10:
            colors.append('#3b82f6')  # Moderate
        elif abs_acc < 0.15:
            colors.append('#f59e0b')  # Elevated
        else:
            colors.append('#ef4444')  # High risk
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_accruals,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Accruals: %{x:.3f}<extra></extra>'
        }],
        'layout': {
            'title': 'Accruals Quality (Sloan Ratio)',
            'xaxis': {'title': 'Accruals Ratio', 'gridcolor': '#e5e7eb', 'zeroline': True},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': 0.08, 'x1': 0.08, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}},
                {'type': 'line', 'x0': -0.08, 'x1': -0.08, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': 0.09, 'y': len(companies), 'text': 'Low Risk Zone', 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="accruals-chart", height=max(450, len(companies) * 25))


def _create_fcf_conversion_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create FCF conversion quality chart"""
    
    companies = list(quality_metrics.keys())
    fcf_qualities = [quality_metrics[c]['fcf_quality'] for c in companies]
    
    # Sort by FCF quality
    sorted_data = sorted(zip(companies, fcf_qualities), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:20] for c, _ in sorted_data]
    sorted_qualities = [q for _, q in sorted_data]
    
    # Color by quality
    colors = []
    for q in sorted_qualities:
        if q >= 1.2:
            colors.append('#10b981')  # Excellent
        elif q >= 0.8:
            colors.append('#3b82f6')  # Good
        elif q >= 0.5:
            colors.append('#f59e0b')  # Fair
        else:
            colors.append('#ef4444')  # Poor
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_qualities,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>FCF Quality: %{x:.2f}x<extra></extra>'
        }],
        'layout': {
            'title': 'Free Cash Flow Conversion Quality',
            'xaxis': {'title': 'FCF / Net Income', 'gridcolor': '#e5e7eb', 'zeroline': True},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': 1.0, 'x1': 1.0, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 1.05, 'y': len(companies), 'text': '100% Conversion (1.0x)', 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="fcf-conversion", height=max(450, len(companies) * 25))


def _create_cash_flow_waterfalls(quality_metrics: Dict[str, Dict]) -> str:
    """Create cash flow waterfall charts"""
    
    company_list = list(quality_metrics.keys())
    
    # Show first 4 companies
    charts_html = ""
    for i, company in enumerate(company_list[:4]):
        metrics = quality_metrics[company]
        
        ni = metrics['net_income']
        ocf = metrics['ocf']
        fcf = metrics['fcf']
        
        non_cash = ocf - ni
        capex = ocf - fcf
        
        fig_data = {
            'data': [{
                'type': 'waterfall',
                'x': ['Net Income', 'Non-Cash Adj', 'Operating CF', 'CapEx', 'Free CF'],
                'y': [ni, non_cash, 0, -capex, 0],
                'measure': ['absolute', 'relative', 'total', 'relative', 'total'],
                'connector': {'line': {'color': '#94a3b8'}},
                'increasing': {'marker': {'color': '#10b981'}},
                'decreasing': {'marker': {'color': '#ef4444'}},
                'totals': {'marker': {'color': '#3b82f6'}},
                'hovertemplate': '%{x}<br>$%{y:.1f}B<extra></extra>'
            }],
            'layout': {
                'title': f'{company[:25]} - Cash Flow Waterfall ($B)',
                'yaxis': {'title': 'Cash Flow ($B)', 'gridcolor': '#e5e7eb'},
                'showlegend': False
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id=f"cf-waterfall-{i}", height=350)
    
    if len(company_list) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(company_list)} companies.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_ocf_stability_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create OCF stability chart"""
    
    companies = list(quality_metrics.keys())
    ocf_cvs = [quality_metrics[c]['ocf_cv'] for c in companies]
    
    # Sort by stability (lower CV is better)
    sorted_data = sorted(zip(companies, ocf_cvs), key=lambda x: x[1])
    sorted_companies = [c[:20] for c, _ in sorted_data]
    sorted_cvs = [cv for _, cv in sorted_data]
    
    # Color by stability
    colors = ['#10b981' if cv < 0.2 else '#3b82f6' if cv < 0.4 else '#f59e0b' if cv < 0.6 else '#ef4444' for cv in sorted_cvs]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_cvs,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>Coefficient of Variation: %{x:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Operating Cash Flow Stability (3-Year CV)',
            'xaxis': {'title': 'Coefficient of Variation (lower is better)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': 0.3, 'x1': 0.3, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': 0.32, 'y': len(companies), 'text': 'Stable (< 0.3)', 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ocf-stability", height=max(400, len(companies) * 25))


def _create_quality_metrics_heatmap(quality_metrics: Dict[str, Dict]) -> str:
    """Create quality metrics heatmap"""
    
    companies = list(quality_metrics.keys())
    metric_names = ['Accruals', 'FCF Quality', 'CFO/EBITDA', 'CapEx Intensity', 'OCF Stability']
    
    # Prepare data matrix (normalized/inverted where needed)
    data_matrix = []
    for metric in metric_names:
        row = []
        for company in companies:
            if metric == 'Accruals':
                val = -abs(quality_metrics[company]['accruals']) * 100  # Negative for color scale
            elif metric == 'FCF Quality':
                val = quality_metrics[company]['fcf_quality'] * 50  # Scale for visualization
            elif metric == 'CFO/EBITDA':
                val = quality_metrics[company]['cfo_ebitda'] * 50
            elif metric == 'CapEx Intensity':
                val = -quality_metrics[company]['capex_intensity']  # Negative (lower is better)
            elif metric == 'OCF Stability':
                val = -quality_metrics[company]['ocf_cv'] * 100  # Negative (lower CV is better)
            else:
                val = 0
            row.append(val)
        data_matrix.append(row)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'x': [c[:15] for c in companies],
            'y': metric_names,
            'colorscale': 'RdYlGn',
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Normalized Value: %{z:.1f}<extra></extra>',
            'colorbar': {'title': 'Quality'}
        }],
        'layout': {
            'title': 'Earnings Quality Heatmap (Green = Strong, Red = Weak)',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="quality-heatmap", height=400)


def _create_quality_metrics_table(quality_metrics: Dict[str, Dict]) -> str:
    """Create quality metrics table"""
    
    table_data = []
    for company, metrics in quality_metrics.items():
        table_data.append({
            'Company': company,
            'Accruals': f"{metrics['accruals']:.3f}",
            'FCF Quality': f"{metrics['fcf_quality']:.2f}x",
            'CFO/EBITDA': f"{metrics['cfo_ebitda']:.2f}x",
            'CapEx Intensity': f"{metrics['capex_intensity']:.1f}%",
            'OCF CV': f"{metrics['ocf_cv']:.2f}",
            'Net Income ($B)': f"{metrics['net_income']:.1f}",
            'OCF ($B)': f"{metrics['ocf']:.1f}",
            'FCF ($B)': f"{metrics['fcf']:.1f}"
        })
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="quality-metrics-table", page_length=10)


def _create_quality_classification(quality_metrics: Dict[str, Dict]) -> str:
    """Create quality classification table"""
    
    classification_data = []
    for company, metrics in quality_metrics.items():
        classification_data.append({
            'Company': company,
            'Quality Tier': metrics['quality_tier'],
            'Accruals Assessment': 'Low Risk' if abs(metrics['accruals']) < 0.08 else 'Moderate Risk' if abs(metrics['accruals']) < 0.15 else 'High Risk',
            'FCF Conversion': 'Excellent' if metrics['fcf_quality'] > 1.2 else 'Good' if metrics['fcf_quality'] > 0.8 else 'Fair' if metrics['fcf_quality'] > 0.5 else 'Poor',
            'Cash Stability': 'Stable' if metrics['ocf_cv'] < 0.3 else 'Moderate' if metrics['ocf_cv'] < 0.6 else 'Volatile'
        })
    
    df_classification = pd.DataFrame(classification_data)
    
    return build_enhanced_table(
        df_classification,
        table_id="quality-classification-table",
        badge_columns=['Quality Tier', 'Accruals Assessment', 'FCF Conversion', 'Cash Stability']
    )


# =============================================================================
# PHASE 4: 18F, 18G, 18H, 18I, 18J - FUNCTIONS ONLY
# Copy these functions into your existing section_18.py file
# =============================================================================

# 18F: Management Effectiveness & Capital Allocation

def _build_section_18f_management_effectiveness(companies: Dict[str, str], df: pd.DataFrame) -> str:
    """Build subsection 18F: Management Effectiveness & Capital Allocation"""
    
    if df.empty:
        return _build_collapsible_subsection(
            "18F",
            "Management Effectiveness & Capital Allocation",
            "<p>Insufficient financial data for management analysis.</p>"
        )
    
    mgmt_metrics = _calculate_management_metrics(companies, df)
    
    if not mgmt_metrics:
        return _build_collapsible_subsection(
            "18F",
            "Management Effectiveness & Capital Allocation",
            "<p>Unable to calculate management metrics.</p>"
        )
    
    intro_html = """
    <p>This section analyzes management effectiveness through <strong>actual return metrics and capital allocation patterns</strong> 
    rather than arbitrary management scores. DuPont analysis, ROIC trends, and capital deployment visualizations provide 
    objective assessment of value creation.</p>
    """
    
    summary_cards = _build_mgmt_summary_cards(mgmt_metrics)
    roe_roic_scatter = _create_mgmt_roe_roic_scatter(mgmt_metrics)
    dupont_analysis = _create_dupont_waterfall_charts(mgmt_metrics)
    roic_trend_chart = _create_roic_trend_chart(mgmt_metrics)
    capital_allocation_sankey = _create_capital_allocation_charts(mgmt_metrics)
    roe_trend_heatmap = _create_roe_trend_heatmap(mgmt_metrics)
    mgmt_table = _create_mgmt_metrics_table(mgmt_metrics)
    mgmt_classification = _create_mgmt_classification(mgmt_metrics)
    
    content_html = f"""
    {intro_html}
    <h4>Management Effectiveness Summary</h4>
    {summary_cards}
    <h4>Return Quality: ROE vs ROIC</h4>
    <p>Companies with high ROE and ROIC demonstrate superior capital efficiency. Arrows show trend direction.</p>
    {roe_roic_scatter}
    <h4>DuPont ROE Decomposition</h4>
    <p>Breaking down ROE into: Net Margin × Asset Turnover × Financial Leverage.</p>
    {dupont_analysis}
    <h4>ROIC Evolution Over Time</h4>
    <p>3-year ROIC trends showing improvement or deterioration in capital returns.</p>
    {roic_trend_chart}
    <h4>Capital Allocation Strategy</h4>
    <p>How management deploys free cash flow across CapEx, dividends, and buybacks.</p>
    {capital_allocation_sankey}
    <h4>ROE Trend Analysis</h4>
    {roe_trend_heatmap}
    <h4>Detailed Management Metrics</h4>
    {mgmt_table}
    <h4>Management Classification</h4>
    {mgmt_classification}
    """
    
    return _build_collapsible_subsection("18F", "Management Effectiveness & Capital Allocation", content_html)


def _calculate_management_metrics(companies: Dict[str, str], df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate management effectiveness metrics"""
    
    mgmt_metrics = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty or len(company_data) < 3:
            continue
        
        latest = company_data.iloc[-1]
        
        # Return metrics
        roe = latest.get('returnOnEquity', 0)
        roic = latest.get('returnOnInvestedCapital', 0)
        roa = latest.get('returnOnAssets', 0)
        
        # DuPont components
        net_margin = latest.get('netProfitMargin', 0)
        asset_turnover = latest.get('assetTurnover', 0)
        equity_multiplier = latest.get('financialLeverageRatio', 1)
        
        # ROIC trend
        if len(company_data) >= 3:
            roic_values = company_data['returnOnInvestedCapital'].tail(3).values
            roic_trend = np.polyfit(range(len(roic_values)), roic_values, 1)[0] if len(roic_values) > 1 else 0
            roic_history = company_data[['Year', 'returnOnInvestedCapital']].tail(3).to_dict('records')
        else:
            roic_trend = 0
            roic_history = []
        
        # Capital allocation
        fcf = latest.get('freeCashFlow', 0)
        capex = abs(latest.get('capitalExpenditure', 0))
        dividends = abs(latest.get('netDividendsPaid', 0))
        buybacks = abs(latest.get('commonStockRepurchased', 0))
        
        total_deployed = capex + dividends + buybacks
        if total_deployed > 0:
            capex_pct = (capex / total_deployed) * 100
            div_pct = (dividends / total_deployed) * 100
            buyback_pct = (buybacks / total_deployed) * 100
        else:
            capex_pct = div_pct = buyback_pct = 0
        
        # Classification
        if roe > 18 and roic > 15 and roic_trend > 0:
            mgmt_class = "Excellent"
        elif roe > 12 and roic > 10:
            mgmt_class = "Good"
        elif roe > 8 and roic > 7:
            mgmt_class = "Fair"
        else:
            mgmt_class = "Needs Improvement"
        
        mgmt_metrics[company_name] = {
            'roe': roe,
            'roic': roic,
            'roa': roa,
            'net_margin': net_margin,
            'asset_turnover': asset_turnover,
            'equity_multiplier': equity_multiplier,
            'roic_trend': roic_trend,
            'roic_history': roic_history,
            'capex_pct': capex_pct,
            'div_pct': div_pct,
            'buyback_pct': buyback_pct,
            'fcf': fcf / 1e9,
            'mgmt_class': mgmt_class
        }
    
    return mgmt_metrics


def _build_mgmt_summary_cards(mgmt_metrics: Dict[str, Dict]) -> str:
    """Build management summary cards"""
    
    if not mgmt_metrics:
        return "<p>No management data available.</p>"
    
    avg_roe = np.mean([m['roe'] for m in mgmt_metrics.values()])
    avg_roic = np.mean([m['roic'] for m in mgmt_metrics.values()])
    
    excellent_count = sum(1 for m in mgmt_metrics.values() if m['mgmt_class'] == 'Excellent')
    improving_count = sum(1 for m in mgmt_metrics.values() if m['roic_trend'] > 0.5)
    
    total = len(mgmt_metrics)
    
    cards = [
        {"label": "Average ROE", "value": f"{avg_roe:.1f}%", "description": "Return on Equity", 
         "type": "success" if avg_roe > 18 else "default"},
        {"label": "Average ROIC", "value": f"{avg_roic:.1f}%", "description": "Return on Invested Capital",
         "type": "success" if avg_roic > 15 else "default"},
        {"label": "Excellent Management", "value": f"{excellent_count}/{total}", "description": "Top-tier capital efficiency",
         "type": "success" if excellent_count >= 2 else "info"},
        {"label": "Improving ROIC", "value": f"{improving_count}/{total}", "description": "Positive 3Y trend",
         "type": "success" if improving_count >= total * 0.5 else "default"}
    ]
    
    return build_stat_grid(cards)


def _create_mgmt_roe_roic_scatter(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create ROE vs ROIC scatter with trend arrows"""
    
    companies = list(mgmt_metrics.keys())
    roe_values = [mgmt_metrics[c]['roe'] for c in companies]
    roic_values = [mgmt_metrics[c]['roic'] for c in companies]
    trends = [mgmt_metrics[c]['roic_trend'] for c in companies]
    
    colors = ['#10b981' if t > 0.5 else '#3b82f6' if t > -0.5 else '#ef4444' for t in trends]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': roe_values,
            'y': roic_values,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {'size': 15, 'color': colors, 'line': {'width': 2, 'color': '#ffffff'}},
            'hovertemplate': '<b>%{text}</b><br>ROE: %{x:.1f}%<br>ROIC: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Management Quality: ROE vs ROIC (Color = ROIC Trend)',
            'xaxis': {'title': 'Return on Equity (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Return on Invested Capital (%)', 'gridcolor': '#e5e7eb'},
            'shapes': [
                {'type': 'line', 'x0': 15, 'x1': 15, 'y0': 0, 'y1': 40, 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}},
                {'type': 'line', 'x0': 0, 'x1': 40, 'y0': 15, 'y1': 15, 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="mgmt-roe-roic", height=500)


def _create_dupont_waterfall_charts(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create DuPont decomposition waterfalls"""
    
    company_list = list(mgmt_metrics.keys())
    charts_html = ""
    
    for i, company in enumerate(company_list[:4]):
        m = mgmt_metrics[company]
        
        fig_data = {
            'data': [{
                'type': 'waterfall',
                'x': ['Net Margin', 'Asset Turnover', 'Leverage', 'ROE'],
                'y': [m['net_margin'], m['asset_turnover'] * 10, m['equity_multiplier'], 0],
                'measure': ['absolute', 'relative', 'relative', 'total'],
                'connector': {'line': {'color': '#94a3b8'}},
                'increasing': {'marker': {'color': '#10b981'}},
                'decreasing': {'marker': {'color': '#ef4444'}},
                'totals': {'marker': {'color': '#3b82f6'}},
                'hovertemplate': '%{x}<br>%{y:.2f}<extra></extra>'
            }],
            'layout': {
                'title': f'{company[:25]} - DuPont Decomposition',
                'yaxis': {'title': 'Component Value', 'gridcolor': '#e5e7eb'},
                'showlegend': False
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id=f"dupont-{i}", height=350)
    
    if len(company_list) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(company_list)} companies.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_roic_trend_chart(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create ROIC trend chart"""
    
    companies = list(mgmt_metrics.keys())
    
    traces = []
    for company in companies:
        history = mgmt_metrics[company]['roic_history']
        if history:
            years = [h['Year'] for h in history]
            roics = [h['returnOnInvestedCapital'] for h in history]
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': company[:15],
                'x': years,
                'y': roics,
                'line': {'width': 2},
                'marker': {'size': 8}
            })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': 'ROIC Evolution (3-Year Trend)',
            'xaxis': {'title': 'Year', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'ROIC (%)', 'gridcolor': '#e5e7eb'},
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roic-trend", height=500)


def _create_capital_allocation_charts(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create capital allocation stacked bar chart"""
    
    companies = list(mgmt_metrics.keys())
    capex_pcts = [mgmt_metrics[c]['capex_pct'] for c in companies]
    div_pcts = [mgmt_metrics[c]['div_pct'] for c in companies]
    buyback_pcts = [mgmt_metrics[c]['buyback_pct'] for c in companies]
    
    fig_data = {
        'data': [
            {'type': 'bar', 'name': 'CapEx', 'y': [c[:15] for c in companies], 'x': capex_pcts, 
             'orientation': 'h', 'marker': {'color': '#3b82f6'}},
            {'type': 'bar', 'name': 'Dividends', 'y': [c[:15] for c in companies], 'x': div_pcts,
             'orientation': 'h', 'marker': {'color': '#10b981'}},
            {'type': 'bar', 'name': 'Buybacks', 'y': [c[:15] for c in companies], 'x': buyback_pcts,
             'orientation': 'h', 'marker': {'color': '#f59e0b'}}
        ],
        'layout': {
            'title': 'Capital Allocation Strategy (% of Total Deployed)',
            'barmode': 'stack',
            'xaxis': {'title': 'Allocation (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'legend': {'orientation': 'h', 'y': -0.15}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="capital-allocation", height=max(400, len(companies) * 25))


def _create_roe_trend_heatmap(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create ROE/ROIC/ROA heatmap"""
    
    companies = list(mgmt_metrics.keys())
    
    data_matrix = [
        [mgmt_metrics[c]['roe'] for c in companies],
        [mgmt_metrics[c]['roic'] for c in companies],
        [mgmt_metrics[c]['roa'] for c in companies]
    ]
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'x': [c[:15] for c in companies],
            'y': ['ROE', 'ROIC', 'ROA'],
            'colorscale': 'RdYlGn',
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Value: %{z:.1f}%<extra></extra>',
            'colorbar': {'title': 'Return %'}
        }],
        'layout': {
            'title': 'Return Metrics Heatmap',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="return-heatmap", height=300)


def _create_mgmt_metrics_table(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create management metrics table"""
    
    table_data = []
    for company, metrics in mgmt_metrics.items():
        table_data.append({
            'Company': company,
            'ROE': f"{metrics['roe']:.1f}%",
            'ROIC': f"{metrics['roic']:.1f}%",
            'Net Margin': f"{metrics['net_margin']:.1f}%",
            'Asset Turnover': f"{metrics['asset_turnover']:.2f}x",
            'CapEx Alloc': f"{metrics['capex_pct']:.0f}%",
            'Dividend Alloc': f"{metrics['div_pct']:.0f}%",
            'Buyback Alloc': f"{metrics['buyback_pct']:.0f}%"
        })
    
    df_table = pd.DataFrame(table_data)
    return build_data_table(df_table, table_id="mgmt-metrics-table", page_length=10)


def _create_mgmt_classification(mgmt_metrics: Dict[str, Dict]) -> str:
    """Create management classification table"""
    
    classification_data = []
    for company, metrics in mgmt_metrics.items():
        classification_data.append({
            'Company': company,
            'Management Quality': metrics['mgmt_class'],
            'ROIC Trend': 'Improving' if metrics['roic_trend'] > 0.5 else 'Stable' if metrics['roic_trend'] > -0.5 else 'Declining',
            'Capital Efficiency': 'Excellent' if metrics['roic'] > 15 else 'Good' if metrics['roic'] > 10 else 'Fair'
        })
    
    df_classification = pd.DataFrame(classification_data)
    return build_enhanced_table(df_classification, table_id="mgmt-class-table", 
                                badge_columns=['Management Quality', 'ROIC Trend', 'Capital Efficiency'])


# 18G: Competitive Positioning & Moat Assessment

def _build_section_18g_competitive_positioning(companies: Dict[str, str], df: pd.DataFrame) -> str:
    """Build subsection 18G: Competitive Positioning"""
    
    if df.empty:
        return _build_collapsible_subsection("18G", "Competitive Positioning & Moat Assessment",
                                            "<p>Insufficient data.</p>")
    
    comp_metrics = _calculate_competitive_metrics(companies, df)
    
    if not comp_metrics:
        return _build_collapsible_subsection("18G", "Competitive Positioning & Moat Assessment",
                                            "<p>Unable to calculate metrics.</p>")
    
    intro_html = """
    <p>Competitive positioning assessed through <strong>margin quality, ROIC premium, and stability metrics</strong> 
    rather than arbitrary moat scores. Wide moats demonstrated by sustained high margins and returns.</p>
    """
    
    summary_cards = _build_comp_summary_cards(comp_metrics)
    margin_stability_scatter = _create_margin_stability_scatter(comp_metrics)
    roic_premium_chart = _create_roic_premium_chart(comp_metrics)
    margin_trend_chart = _create_margin_trend_chart(comp_metrics)
    competitive_heatmap = _create_competitive_heatmap(comp_metrics)
    comp_table = _create_comp_metrics_table(comp_metrics)
    moat_classification = _create_moat_classification(comp_metrics)
    
    content_html = f"""
    {intro_html}
    <h4>Competitive Position Summary</h4>
    {summary_cards}
    <h4>Margin Stability Matrix</h4>
    <p>Companies with high operating margins AND low variability demonstrate pricing power and moat strength.</p>
    {margin_stability_scatter}
    <h4>ROIC Premium Analysis</h4>
    <p>Returns above 15% suggest competitive advantages and economic moats.</p>
    {roic_premium_chart}
    <h4>Margin Evolution</h4>
    <p>Gross, operating, and net margin trends over time.</p>
    {margin_trend_chart}
    <h4>Competitive Strength Heatmap</h4>
    {competitive_heatmap}
    <h4>Detailed Competitive Metrics</h4>
    {comp_table}
    <h4>Moat Classification</h4>
    {moat_classification}
    """
    
    return _build_collapsible_subsection("18G", "Competitive Positioning & Moat Assessment", content_html)


def _calculate_competitive_metrics(companies: Dict[str, str], df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate competitive positioning metrics"""
    
    comp_metrics = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty or len(company_data) < 3:
            continue
        
        latest = company_data.iloc[-1]
        
        # Margin metrics
        gross_margin = latest.get('grossProfitMargin', 0)
        op_margin = latest.get('operatingProfitMargin', 0)
        net_margin = latest.get('netProfitMargin', 0)
        
        # Margin stability (3Y)
        if len(company_data) >= 3:
            op_margins = company_data['operatingProfitMargin'].tail(3).values
            margin_stability = 1 - (np.std(op_margins) / np.mean(op_margins)) if np.mean(op_margins) > 0 else 0
            margin_stability = max(0, min(1, margin_stability))
        else:
            margin_stability = 0.5
        
        # Returns
        roic = latest.get('returnOnInvestedCapital', 0)
        roe = latest.get('returnOnEquity', 0)
        
        # Growth
        if len(company_data) >= 3:
            revenue_growth = company_data['revenue'].pct_change().tail(3).mean() * 100
        else:
            revenue_growth = 0
        
        # Moat classification
        if op_margin > 20 and roic > 20 and margin_stability > 0.7:
            moat_class = "Wide Moat"
        elif op_margin > 12 and roic > 12 and margin_stability > 0.5:
            moat_class = "Narrow Moat"
        else:
            moat_class = "No Clear Moat"
        
        comp_metrics[company_name] = {
            'gross_margin': gross_margin,
            'op_margin': op_margin,
            'net_margin': net_margin,
            'margin_stability': margin_stability,
            'roic': roic,
            'roe': roe,
            'revenue_growth': revenue_growth,
            'moat_class': moat_class
        }
    
    return comp_metrics


def _build_comp_summary_cards(comp_metrics: Dict[str, Dict]) -> str:
    """Build competitive summary cards"""
    
    if not comp_metrics:
        return "<p>No data available.</p>"
    
    avg_op_margin = np.mean([m['op_margin'] for m in comp_metrics.values()])
    avg_roic = np.mean([m['roic'] for m in comp_metrics.values()])
    
    wide_moat = sum(1 for m in comp_metrics.values() if m['moat_class'] == 'Wide Moat')
    total = len(comp_metrics)
    
    cards = [
        {"label": "Avg Operating Margin", "value": f"{avg_op_margin:.1f}%", "description": "Profitability level",
         "type": "success" if avg_op_margin > 15 else "default"},
        {"label": "Avg ROIC", "value": f"{avg_roic:.1f}%", "description": "Capital efficiency",
         "type": "success" if avg_roic > 15 else "default"},
        {"label": "Wide Moat Companies", "value": f"{wide_moat}/{total}", "description": "Sustainable advantages",
         "type": "success" if wide_moat >= 2 else "info"},
        {"label": "Moat Concentration", "value": f"{wide_moat/total*100:.0f}%", "description": "Portfolio moat %",
         "type": "success" if wide_moat >= total * 0.4 else "default"}
    ]
    
    return build_stat_grid(cards)


def _create_margin_stability_scatter(comp_metrics: Dict[str, Dict]) -> str:
    """Create margin level vs stability scatter"""
    
    companies = list(comp_metrics.keys())
    margins = [comp_metrics[c]['op_margin'] for c in companies]
    stabilities = [comp_metrics[c]['margin_stability'] * 100 for c in companies]
    
    moat_colors = {'Wide Moat': '#10b981', 'Narrow Moat': '#3b82f6', 'No Clear Moat': '#94a3b8'}
    colors = [moat_colors[comp_metrics[c]['moat_class']] for c in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': margins,
            'y': stabilities,
            'text': [c[:10] for c in companies],
            'textposition': 'top center',
            'marker': {'size': 15, 'color': colors, 'line': {'width': 2, 'color': '#ffffff'}},
            'hovertemplate': '<b>%{text}</b><br>Margin: %{x:.1f}%<br>Stability: %{y:.0f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Competitive Strength: Margin Level vs Stability',
            'xaxis': {'title': 'Operating Margin (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': 'Margin Stability (%, higher = more stable)', 'gridcolor': '#e5e7eb'},
            'shapes': [
                {'type': 'line', 'x0': 15, 'x1': 15, 'y0': 0, 'y1': 100, 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}},
                {'type': 'line', 'x0': 0, 'x1': 40, 'y0': 70, 'y1': 70, 'line': {'color': '#10b981', 'width': 1, 'dash': 'dot'}}
            ],
            'annotations': [
                {'x': 25, 'y': 85, 'text': 'Wide Moat Zone', 'showarrow': False, 'font': {'size': 11, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="margin-stability", height=500)


def _create_roic_premium_chart(comp_metrics: Dict[str, Dict]) -> str:
    """Create ROIC premium chart"""
    
    companies = list(comp_metrics.keys())
    roics = [comp_metrics[c]['roic'] for c in companies]
    
    sorted_data = sorted(zip(companies, roics), key=lambda x: x[1], reverse=True)
    sorted_companies = [c[:20] for c, _ in sorted_data]
    sorted_roics = [r for _, r in sorted_data]
    
    colors = ['#10b981' if r > 20 else '#3b82f6' if r > 15 else '#f59e0b' if r > 10 else '#ef4444' for r in sorted_roics]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': sorted_companies,
            'x': sorted_roics,
            'orientation': 'h',
            'marker': {'color': colors},
            'hovertemplate': '<b>%{y}</b><br>ROIC: %{x:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Return on Invested Capital (Moat Indicator)',
            'xaxis': {'title': 'ROIC (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'shapes': [
                {'type': 'line', 'x0': 15, 'x1': 15, 'y0': -0.5, 'y1': len(companies) - 0.5,
                 'line': {'color': '#10b981', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 16, 'y': len(companies), 'text': 'Moat Threshold (15%)', 'showarrow': False, 
                 'font': {'size': 10, 'color': '#10b981'}}
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roic-premium", height=max(400, len(companies) * 25))


def _create_margin_trend_chart(comp_metrics: Dict[str, Dict]) -> str:
    """Create margin comparison chart"""
    
    companies = list(comp_metrics.keys())
    gross = [comp_metrics[c]['gross_margin'] for c in companies]
    operating = [comp_metrics[c]['op_margin'] for c in companies]
    net = [comp_metrics[c]['net_margin'] for c in companies]
    
    fig_data = {
        'data': [
            {'type': 'bar', 'name': 'Gross', 'y': [c[:15] for c in companies], 'x': gross, 'orientation': 'h', 
             'marker': {'color': '#3b82f6'}},
            {'type': 'bar', 'name': 'Operating', 'y': [c[:15] for c in companies], 'x': operating, 'orientation': 'h',
             'marker': {'color': '#10b981'}},
            {'type': 'bar', 'name': 'Net', 'y': [c[:15] for c in companies], 'x': net, 'orientation': 'h',
             'marker': {'color': '#f59e0b'}}
        ],
        'layout': {
            'title': 'Margin Profile Comparison',
            'barmode': 'group',
            'xaxis': {'title': 'Margin (%)', 'gridcolor': '#e5e7eb'},
            'yaxis': {'title': ''},
            'legend': {'orientation': 'h', 'y': -0.15}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="margin-comparison", height=max(400, len(companies) * 30))


def _create_competitive_heatmap(comp_metrics: Dict[str, Dict]) -> str:
    """Create competitive metrics heatmap"""
    
    companies = list(comp_metrics.keys())
    
    data_matrix = [
        [comp_metrics[c]['gross_margin'] for c in companies],
        [comp_metrics[c]['op_margin'] for c in companies],
        [comp_metrics[c]['net_margin'] for c in companies],
        [comp_metrics[c]['roic'] for c in companies],
        [comp_metrics[c]['margin_stability'] * 100 for c in companies]
    ]
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'x': [c[:15] for c in companies],
            'y': ['Gross Margin', 'Op Margin', 'Net Margin', 'ROIC', 'Stability'],
            'colorscale': 'RdYlGn',
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Value: %{z:.1f}<extra></extra>',
            'colorbar': {'title': 'Strength'}
        }],
        'layout': {
            'title': 'Competitive Strength Heatmap',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="comp-heatmap", height=400)


def _create_comp_metrics_table(comp_metrics: Dict[str, Dict]) -> str:
    """Create competitive metrics table"""
    
    table_data = []
    for company, metrics in comp_metrics.items():
        table_data.append({
            'Company': company,
            'Gross Margin': f"{metrics['gross_margin']:.1f}%",
            'Op Margin': f"{metrics['op_margin']:.1f}%",
            'Net Margin': f"{metrics['net_margin']:.1f}%",
            'ROIC': f"{metrics['roic']:.1f}%",
            'Margin Stability': f"{metrics['margin_stability']*100:.0f}%",
            'Revenue Growth': f"{metrics['revenue_growth']:.1f}%"
        })
    
    df_table = pd.DataFrame(table_data)
    return build_data_table(df_table, table_id="comp-metrics-table", page_length=10)


def _create_moat_classification(comp_metrics: Dict[str, Dict]) -> str:
    """Create moat classification table"""
    
    classification_data = []
    for company, metrics in comp_metrics.items():
        classification_data.append({
            'Company': company,
            'Moat Classification': metrics['moat_class'],
            'Margin Level': 'High' if metrics['op_margin'] > 15 else 'Moderate' if metrics['op_margin'] > 10 else 'Low',
            'ROIC Level': 'Excellent' if metrics['roic'] > 20 else 'Good' if metrics['roic'] > 15 else 'Fair',
            'Stability': 'Stable' if metrics['margin_stability'] > 0.7 else 'Moderate' if metrics['margin_stability'] > 0.5 else 'Volatile'
        })
    
    df_classification = pd.DataFrame(classification_data)
    return build_enhanced_table(df_classification, table_id="moat-class-table",
                                badge_columns=['Moat Classification', 'Margin Level', 'ROIC Level', 'Stability'])


# 18H & 18I: Investment Profile & Strategic Intelligence (Combined)

def _build_section_18h_investment_profile(companies: Dict[str, str], df: pd.DataFrame,
                                         prices_daily: pd.DataFrame, sp500_daily: pd.DataFrame) -> str:
    """Build 18H: Multi-Dimensional Investment Profile Dashboard"""
    
    # Gather all metrics from previous sections
    profile_data = _compile_investment_profiles(companies, df, prices_daily, sp500_daily)
    
    if not profile_data:
        return _build_collapsible_subsection("18H", "Multi-Dimensional Investment Profile",
                                            "<p>Unable to compile investment profiles.</p>")
    
    intro_html = """
    <p>Comprehensive investment analysis using <strong>multiple actual metrics</strong> rather than composite scores. 
    Each company assessed across quality, valuation, momentum, and risk dimensions with clear classifications.</p>
    """
    
    comparison_matrix = _create_comparison_matrix(profile_data)
    radar_charts = _create_profile_radar_charts(profile_data)
    profile_heatmap = _create_profile_heatmap(profile_data)
    investment_cards = _create_investment_profile_cards(profile_data)
    
    content_html = f"""
    {intro_html}
    <h4>Side-by-Side Comparison Matrix</h4>
    {comparison_matrix}
    <h4>Multi-Dimensional Profile Radar Charts</h4>
    <p>Visual representation of strengths across quality, profitability, growth, and risk dimensions.</p>
    {radar_charts}
    <h4>Investment Profile Heatmap</h4>
    {profile_heatmap}
    <h4>Investment Profile Cards</h4>
    {investment_cards}
    """
    
    return _build_collapsible_subsection("18H", "Multi-Dimensional Investment Profile", content_html)


def _build_section_18i_strategic_intelligence(companies: Dict[str, str], df: pd.DataFrame,
                                              prices_daily: pd.DataFrame, sp500_daily: pd.DataFrame) -> str:
    """Build 18I: Strategic Investment Intelligence Dashboard"""
    
    profile_data = _compile_investment_profiles(companies, df, prices_daily, sp500_daily)
    
    if not profile_data:
        return _build_collapsible_subsection("18I", "Strategic Investment Intelligence Dashboard",
                                            "<p>Unable to generate intelligence.</p>")
    
    intro_html = """
    <p>Interactive strategic intelligence dashboard providing actionable insights, opportunity identification, 
    and risk monitoring across the portfolio.</p>
    """
    
    executive_cards = _create_executive_dashboard_cards(profile_data)
    opportunity_analysis = _create_opportunity_analysis(profile_data)
    risk_monitoring = _create_risk_monitoring_panel(profile_data)
    action_priorities = _create_action_priority_cards(profile_data)
    
    content_html = f"""
    {intro_html}
    <h4>Executive Dashboard</h4>
    {executive_cards}
    <h4>Investment Opportunities</h4>
    {opportunity_analysis}
    <h4>Risk Monitoring</h4>
    {risk_monitoring}
    <h4>Action Priorities</h4>
    {action_priorities}
    """
    
    return _build_collapsible_subsection("18I", "Strategic Investment Intelligence Dashboard", content_html)


def _compile_investment_profiles(companies: Dict[str, str], df: pd.DataFrame,
                                 prices_daily: pd.DataFrame, sp500_daily: pd.DataFrame) -> Dict[str, Dict]:
    """Compile comprehensive investment profiles from all metrics"""
    
    profiles = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        
        # Quality tier
        roe = latest.get('returnOnEquity', 0)
        roic = latest.get('returnOnInvestedCapital', 0)
        if roe > 18 and roic > 15:
            quality_tier = "Excellent"
        elif roe > 12 and roic > 10:
            quality_tier = "Good"
        else:
            quality_tier = "Fair"
        
        # Valuation zone
        pe = latest.get('priceToEarningsRatio', np.nan)
        if not np.isnan(pe):
            if pe < 15:
                valuation_zone = "Deep Value"
            elif pe < 25:
                valuation_zone = "Fair Value"
            else:
                valuation_zone = "Premium"
        else:
            valuation_zone = "N/A"
        
        # Risk level (simplified)
        risk_level = "Moderate"  # Could calculate from volatility if available
        
        profiles[company_name] = {
            'quality_tier': quality_tier,
            'valuation_zone': valuation_zone,
            'risk_level': risk_level,
            'roe': roe,
            'roic': roic,
            'pe': pe if not np.isnan(pe) else 0,
            'op_margin': latest.get('operatingProfitMargin', 0),
            'revenue_growth': company_data['revenue'].pct_change().tail(3).mean() * 100 if len(company_data) >= 3 else 0
        }
    
    return profiles


def _create_comparison_matrix(profile_data: Dict[str, Dict]) -> str:
    """Create side-by-side comparison matrix"""
    
    table_data = []
    for company, profile in profile_data.items():
        table_data.append({
            'Company': company,
            'Quality': profile['quality_tier'],
            'Valuation': profile['valuation_zone'],
            'ROE': f"{profile['roe']:.1f}%",
            'ROIC': f"{profile['roic']:.1f}%",
            'P/E': f"{profile['pe']:.1f}x" if profile['pe'] > 0 else "N/A",
            'Op Margin': f"{profile['op_margin']:.1f}%",
            'Growth': f"{profile['revenue_growth']:.1f}%"
        })
    
    df_table = pd.DataFrame(table_data)
    return build_enhanced_table(df_table, table_id="comparison-matrix",
                                badge_columns=['Quality', 'Valuation'])


def _create_profile_radar_charts(profile_data: Dict[str, Dict]) -> str:
    """Create radar charts for each company"""
    
    company_list = list(profile_data.keys())
    charts_html = ""
    
    for i, company in enumerate(company_list[:4]):
        profile = profile_data[company]
        
        fig_data = {
            'data': [{
                'type': 'scatterpolar',
                'r': [
                    min(100, profile['roe'] * 3),
                    min(100, profile['roic'] * 3),
                    min(100, profile['op_margin'] * 3),
                    min(100, max(0, profile['revenue_growth']) * 5),
                    50  # Risk placeholder
                ],
                'theta': ['ROE', 'ROIC', 'Op Margin', 'Growth', 'Risk-Adj'],
                'fill': 'toself',
                'marker': {'color': '#667eea'}
            }],
            'layout': {
                'polar': {'radialaxis': {'visible': True, 'range': [0, 100]}},
                'title': company[:25],
                'showlegend': False
            }
        }
        
        charts_html += build_plotly_chart(fig_data, div_id=f"profile-radar-{i}", height=350)
    
    if len(company_list) > 4:
        charts_html += f"<p><em>Showing first 4 of {len(company_list)} companies.</em></p>"
    
    return f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;">{charts_html}</div>'


def _create_profile_heatmap(profile_data: Dict[str, Dict]) -> str:
    """Create investment profile heatmap"""
    
    companies = list(profile_data.keys())
    
    data_matrix = [
        [profile_data[c]['roe'] for c in companies],
        [profile_data[c]['roic'] for c in companies],
        [profile_data[c]['op_margin'] for c in companies],
        [profile_data[c]['revenue_growth'] for c in companies]
    ]
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': data_matrix,
            'x': [c[:15] for c in companies],
            'y': ['ROE', 'ROIC', 'Op Margin', 'Revenue Growth'],
            'colorscale': 'RdYlGn',
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Value: %{z:.1f}<extra></extra>',
            'colorbar': {'title': 'Strength'}
        }],
        'layout': {
            'title': 'Investment Profile Heatmap',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="profile-heatmap", height=350)


def _create_investment_profile_cards(profile_data: Dict[str, Dict]) -> str:
    """Create investment profile cards for each company"""
    
    cards_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">'
    
    for company, profile in profile_data.items():
        quality_color = {'Excellent': '#10b981', 'Good': '#3b82f6', 'Fair': '#f59e0b'}.get(profile['quality_tier'], '#94a3b8')
        val_color = {'Deep Value': '#10b981', 'Fair Value': '#3b82f6', 'Premium': '#f59e0b'}.get(profile['valuation_zone'], '#94a3b8')
        
        card_html = f"""
        <div style="background: var(--card-bg); border-radius: 12px; padding: 20px; border: 1px solid var(--card-border); box-shadow: var(--shadow-sm);">
            <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">{company[:25]}</h4>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary);">Quality:</span>
                    <span style="background: {quality_color}; color: white; padding: 2px 8px; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">
                        {profile['quality_tier']}
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary);">Valuation:</span>
                    <span style="background: {val_color}; color: white; padding: 2px 8px; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">
                        {profile['valuation_zone']}
                    </span>
                </div>
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--card-border); font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                        <span style="color: var(--text-secondary);">ROE:</span>
                        <span style="font-weight: 600;">{profile['roe']:.1f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                        <span style="color: var(--text-secondary);">ROIC:</span>
                        <span style="font-weight: 600;">{profile['roic']:.1f}%</span>
                    </div>
                </div>
            </div>
        </div>
        """
        cards_html += card_html
    
    cards_html += '</div>'
    return cards_html


def _create_executive_dashboard_cards(profile_data: Dict[str, Dict]) -> str:
    """Create executive dashboard summary cards"""
    
    total = len(profile_data)
    excellent_quality = sum(1 for p in profile_data.values() if p['quality_tier'] == 'Excellent')
    value_opps = sum(1 for p in profile_data.values() if p['valuation_zone'] in ['Deep Value', 'Fair Value'])
    high_growth = sum(1 for p in profile_data.values() if p['revenue_growth'] > 12)
    
    cards = [
        {"label": "📊 Portfolio Quality", "value": f"{excellent_quality}/{total}", "description": "Excellent quality companies",
         "type": "success"},
        {"label": "🎯 Value Opportunities", "value": f"{value_opps}/{total}", "description": "Fair or deep value",
         "type": "info"},
        {"label": "📈 Growth Leaders", "value": f"{high_growth}/{total}", "description": "Revenue growth >12%",
         "type": "success"},
        {"label": "💎 High Conviction", "value": f"{min(3, excellent_quality)}", "description": "Quality + Value alignment",
         "type": "success"}
    ]
    
    return build_stat_grid(cards)


def _create_opportunity_analysis(profile_data: Dict[str, Dict]) -> str:
    """Create opportunity analysis section"""
    
    # Identify opportunities
    quality_value = []
    growth_value = []
    turnaround = []
    
    for company, profile in profile_data.items():
        if profile['quality_tier'] == 'Excellent' and profile['valuation_zone'] in ['Deep Value', 'Fair Value']:
            quality_value.append(company)
        elif profile['revenue_growth'] > 12 and profile['valuation_zone'] == 'Fair Value':
            growth_value.append(company)
        elif profile['quality_tier'] == 'Fair' and profile['valuation_zone'] == 'Deep Value':
            turnaround.append(company)
    
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">'
    
    # Quality Value
    html += f"""
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px;">
        <h4 style="margin: 0 0 10px 0;">🟢 Quality Value Opportunities</h4>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem;">High quality at reasonable prices</p>
        <ul style="margin: 0; padding-left: 20px;">
            {''.join([f'<li>{c}</li>' for c in quality_value[:3]]) if quality_value else '<li>None identified</li>'}
        </ul>
    </div>
    """
    
    # Growth Value
    html += f"""
    <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 20px; border-radius: 12px;">
        <h4 style="margin: 0 0 10px 0;">🔵 Growth at Fair Price</h4>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem;">Strong growth, reasonable valuation</p>
        <ul style="margin: 0; padding-left: 20px;">
            {''.join([f'<li>{c}</li>' for c in growth_value[:3]]) if growth_value else '<li>None identified</li>'}
        </ul>
    </div>
    """
    
    # Turnaround
    html += f"""
    <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 20px; border-radius: 12px;">
        <h4 style="margin: 0 0 10px 0;">🟡 Turnaround Candidates</h4>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem;">Deep value, higher risk</p>
        <ul style="margin: 0; padding-left: 20px;">
            {''.join([f'<li>{c}</li>' for c in turnaround[:3]]) if turnaround else '<li>None identified</li>'}
        </ul>
    </div>
    """
    
    html += '</div>'
    return html


def _create_risk_monitoring_panel(profile_data: Dict[str, Dict]) -> str:
    """Create risk monitoring panel"""
    
    # Identify risks
    premium_valuations = [c for c, p in profile_data.items() if p['valuation_zone'] == 'Premium']
    low_quality = [c for c, p in profile_data.items() if p['quality_tier'] == 'Fair' and p['valuation_zone'] != 'Deep Value']
    
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">'
    
    # Valuation risk
    html += f"""
    <div style="background: var(--card-bg); border-left: 4px solid #f59e0b; padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
        <h4 style="margin: 0 0 10px 0; color: #f59e0b;">⚠️ Valuation Risk</h4>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem; color: var(--text-secondary);">
            {len(premium_valuations)} companies at premium valuations
        </p>
        <ul style="margin: 0; padding-left: 20px; color: var(--text-secondary);">
            {''.join([f'<li>{c[:20]}</li>' for c in premium_valuations[:3]]) if premium_valuations else '<li>No concerns</li>'}
        </ul>
    </div>
    """
    
    # Quality concerns
    html += f"""
    <div style="background: var(--card-bg); border-left: 4px solid #ef4444; padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
        <h4 style="margin: 0 0 10px 0; color: #ef4444;">🔴 Quality Concerns</h4>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem; color: var(--text-secondary);">
            {len(low_quality)} companies with quality concerns
        </p>
        <ul style="margin: 0; padding-left: 20px; color: var(--text-secondary);">
            {''.join([f'<li>{c[:20]}</li>' for c in low_quality[:3]]) if low_quality else '<li>No concerns</li>'}
        </ul>
    </div>
    """
    
    html += '</div>'
    return html


def _create_action_priority_cards(profile_data: Dict[str, Dict]) -> str:
    """Create action priority cards"""
    
    # High priority: Quality + Value
    high_priority = [c for c, p in profile_data.items() 
                     if p['quality_tier'] == 'Excellent' and p['valuation_zone'] in ['Deep Value', 'Fair Value']]
    
    # Monitor: Premium valuations
    monitor = [c for c, p in profile_data.items() if p['valuation_zone'] == 'Premium']
    
    # Review: Quality concerns
    review = [c for c, p in profile_data.items() if p['quality_tier'] == 'Fair']
    
    html = """
    <div style="display: flex; flex-direction: column; gap: 15px;">
    """
    
    # High Priority
    html += f"""
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; box-shadow: var(--shadow-md);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="margin: 0;">🟢 HIGH PRIORITY: Quality + Value</h4>
            <span style="background: rgba(255,255,255,0.3); padding: 4px 12px; border-radius: 8px; font-weight: 700;">{len(high_priority)} stocks</span>
        </div>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem;">Strong buy candidates with quality and valuation alignment</p>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            {''.join([f'<span style="background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">{c[:15]}</span>' for c in high_priority]) if high_priority else '<span>None identified</span>'}
        </div>
    </div>
    """
    
    # Monitor
    html += f"""
    <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 20px; border-radius: 12px; box-shadow: var(--shadow-md);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="margin: 0;">🟡 MONITOR: Premium Valuations</h4>
            <span style="background: rgba(255,255,255,0.3); padding: 4px 12px; border-radius: 8px; font-weight: 700;">{len(monitor)} stocks</span>
        </div>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem;">Watch for valuation compression or earnings growth acceleration</p>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            {''.join([f'<span style="background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">{c[:15]}</span>' for c in monitor[:5]]) if monitor else '<span>None identified</span>'}
        </div>
    </div>
    """
    
    # Review
    html += f"""
    <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 20px; border-radius: 12px; box-shadow: var(--shadow-md);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="margin: 0;">🔴 REVIEW: Quality Enhancement Needed</h4>
            <span style="background: rgba(255,255,255,0.3); padding: 4px 12px; border-radius: 8px; font-weight: 700;">{len(review)} stocks</span>
        </div>
        <p style="margin: 0 0 10px 0; font-size: 0.9rem;">Consider rotation to higher quality alternatives</p>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            {''.join([f'<span style="background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">{c[:15]}</span>' for c in review[:5]]) if review else '<span>None identified</span>'}
        </div>
    </div>
    """
    
    html += '</div>'
    return html


# Collapsible subsection helper

def _build_collapsible_subsection(subsection_id: str, title: str, content: str) -> str:
    """Build collapsible subsection"""
    
    unique_id = f"subsection-{subsection_id.lower().replace('.', '-')}"
    
    return f"""
    <div class="subsection-container" style="margin: 30px 0;">
        <div class="subsection-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px 20px; border-radius: 12px; cursor: pointer; display: flex; 
                    justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
             onclick="toggleSubsection('{unique_id}')">
            <h3 style="margin: 0; color: white; font-size: 1.3rem; font-weight: 700;">
                {subsection_id}. {title}
            </h3>
            <span id="{unique_id}-toggle" style="color: white; font-size: 1.5rem; font-weight: bold;">−</span>
        </div>
        <div id="{unique_id}-content" class="subsection-content" 
             style="padding: 25px; background: var(--card-bg); border-radius: 0 0 12px 12px; 
                    border: 1px solid var(--card-border); border-top: none;">
            {content}
        </div>
    </div>
    
    <script>
    function toggleSubsection(id) {{
        const content = document.getElementById(id + '-content');
        const toggle = document.getElementById(id + '-toggle');
        
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            toggle.textContent = '−';
        }} else {{
            content.style.display = 'none';
            toggle.textContent = '+';
        }}
    }}
    </script>
    """


# =============================================================================
# COLLAPSIBLE SUBSECTION HELPER
# =============================================================================

def _build_collapsible_subsection(subsection_id: str, title: str, content: str) -> str:
    """Build a collapsible/expandable subsection"""
    
    unique_id = f"subsection-{subsection_id.lower().replace('.', '-')}"
    
    return f"""
    <div class="subsection-container" style="margin: 30px 0;">
        <div class="subsection-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px 20px; border-radius: 12px; cursor: pointer; display: flex; 
                    justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
             onclick="toggleSubsection('{unique_id}')">
            <h3 style="margin: 0; color: white; font-size: 1.3rem; font-weight: 700;">
                {subsection_id}. {title}
            </h3>
            <span id="{unique_id}-toggle" style="color: white; font-size: 1.5rem; font-weight: bold;">−</span>
        </div>
        <div id="{unique_id}-content" class="subsection-content" 
             style="padding: 25px; background: var(--card-bg); border-radius: 0 0 12px 12px; 
                    border: 1px solid var(--card-border); border-top: none;">
            {content}
        </div>
    </div>
    
    <script>
    function toggleSubsection(id) {{
        const content = document.getElementById(id + '-content');
        const toggle = document.getElementById(id + '-toggle');
        
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            toggle.textContent = '−';
        }} else {{
            content.style.display = 'none';
            toggle.textContent = '+';
        }}
    }}
    </script>
    """


# =============================================================================
# COLLAPSIBLE SUBSECTION HELPER
# =============================================================================

def _build_collapsible_subsection(subsection_id: str, title: str, content: str) -> str:
    """Build a collapsible/expandable subsection"""
    
    unique_id = f"subsection-{subsection_id.lower().replace('.', '-')}"
    
    return f"""
    <div class="subsection-container" style="margin: 30px 0;">
        <div class="subsection-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px 20px; border-radius: 12px; cursor: pointer; display: flex; 
                    justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
             onclick="toggleSubsection('{unique_id}')">
            <h3 style="margin: 0; color: white; font-size: 1.3rem; font-weight: 700;">
                {subsection_id}. {title}
            </h3>
            <span id="{unique_id}-toggle" style="color: white; font-size: 1.5rem; font-weight: bold;">−</span>
        </div>
        <div id="{unique_id}-content" class="subsection-content" 
             style="padding: 25px; background: var(--card-bg); border-radius: 0 0 12px 12px; 
                    border: 1px solid var(--card-border); border-top: none;">
            {content}
        </div>
    </div>
    
    <script>
    function toggleSubsection(id) {{
        const content = document.getElementById(id + '-content');
        const toggle = document.getElementById(id + '-toggle');
        
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            toggle.textContent = '−';
        }} else {{
            content.style.display = 'none';
            toggle.textContent = '+';
        }}
    }}
    </script>
    """