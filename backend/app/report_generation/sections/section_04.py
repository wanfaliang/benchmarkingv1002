"""Section 4: Profitability & Returns Analysis"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import json

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_section_divider,
    build_data_table,
    build_plotly_chart,
    build_info_box,
    build_stat_grid,
    format_percentage,
    format_number,
    format_currency,
    build_enhanced_table,
    build_summary_card,
    build_badge,
    build_heatmap_table,
    build_score_badge,
    build_colored_cell
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 4: Profitability & Returns Analysis
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # 1. Extract data from collector
    companies = collector.companies
    df = collector.get_all_financial_data()
    
    try:
        prices_df = collector.get_prices_daily()
    except:
        prices_df = pd.DataFrame()
    
    try:
        institutional_df = collector.get_institutional_ownership()
    except:
        institutional_df = pd.DataFrame()
    
    try:
        insider_df = collector.get_insider_trading_latest()
    except:
        insider_df = pd.DataFrame()
    
    try:
        economic_df = collector.get_economic()
    except:
        economic_df = pd.DataFrame()
    
    # 2. Build all subsections
    section_4a_html = _build_section_4a_dupont_analysis(df, companies, institutional_df)
    section_4b_html = _build_section_4b_operational_efficiency(df, companies)
    section_4c_html = _build_section_4c_multidimensional_returns(df, companies, prices_df, institutional_df)
    section_4d_html = _build_section_4d_economic_value_added(df, companies, economic_df)
    section_4e_html = _build_section_4e_visualization_suite(df, companies, institutional_df)
    section_4f_html = _build_section_4f_strategic_insights(df, companies, institutional_df, insider_df)
    
    # 3. Define custom CSS for collapsible sections
    collapsible_css = """
    <style>
        .collapsible-section {
            margin: 30px 0;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
            background: var(--card-bg);
            box-shadow: var(--shadow-sm);
        }
        
        .collapsible-header {
            background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
            color: white;
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: var(--transition-fast);
        }
        
        .collapsible-header:hover {
            opacity: 0.9;
        }
        
        .collapsible-header h3 {
            margin: 0;
            font-size: 1.3rem;
            font-weight: 700;
            color: white;
        }
        
        .collapsible-toggle {
            font-size: 1.5rem;
            font-weight: bold;
            transition: transform 0.3s ease;
        }
        
        .collapsible-content {
            padding: 25px;
            display: none;
        }
        
        .collapsible-content.active {
            display: block;
            animation: slideDown 0.3s ease;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
    """
    
    # 4. Define JavaScript for collapsible functionality
    collapsible_js = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize all collapsible sections
            const headers = document.querySelectorAll('.collapsible-header');
            
            headers.forEach(header => {
                header.addEventListener('click', function() {
                    const content = this.nextElementSibling;
                    const toggle = this.querySelector('.collapsible-toggle');
                    
                    // Toggle active state
                    content.classList.toggle('active');
                    
                    // Rotate toggle icon
                    if (content.classList.contains('active')) {
                        toggle.style.transform = 'rotate(180deg)';
                    } else {
                        toggle.style.transform = 'rotate(0deg)';
                    }
                });
            });
            
            // Open first section by default
            if (headers.length > 0) {
                headers[0].click();
            }
        });
    </script>
    """
    
    # 5. Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        <!-- Section Introduction -->
        <div class="info-box info">
            <h3>Section Overview</h3>
            <p>
                This section provides comprehensive profitability and returns analysis across multiple dimensions:
                DuPont decomposition with institutional weighting, operational efficiency metrics, 
                multi-dimensional return analysis, Economic Value Added (EVA) assessment, and strategic insights.
            </p>
            <p><strong>Analysis Coverage:</strong> {len(companies)} companies • {len(df)} financial data points • 
            {len(institutional_df)} institutional records • {len(insider_df)} insider transactions</p>
        </div>
        
        {section_4a_html}
        {build_section_divider() if section_4a_html else ""}
        
        {section_4b_html}
        {build_section_divider() if section_4b_html else ""}
        
        {section_4c_html}
        {build_section_divider() if section_4c_html else ""}
        
        {section_4d_html}
        {build_section_divider() if section_4d_html else ""}
        
        {section_4e_html}
        {build_section_divider() if section_4e_html else ""}
        
        {section_4f_html}
    </div>
    
    {collapsible_css}
    {collapsible_js}
    """
    
    return generate_section_wrapper(4, "Profitability & Returns Analysis", content)


# =============================================================================
# SUBSECTION 4A: DUPONT ANALYSIS WITH INSTITUTIONAL WEIGHTING
# =============================================================================

def _build_section_4a_dupont_analysis(df: pd.DataFrame, companies: Dict[str, str], 
                                     institutional_df: pd.DataFrame) -> str:
    """Build Section 4A: DuPont Analysis with Institutional Weighting"""
    
    if df.empty:
        return ""
    
    # Generate DuPont analysis
    dupont_analysis = _calculate_dupont_analysis(df, companies, institutional_df)
    
    # Generate profitability trends
    profitability_trends = _calculate_profitability_trends(df, companies)
    
    # Build DuPont analysis subsection
    dupont_html = _build_dupont_decomposition_subsection(dupont_analysis, companies)
    
    # Build profitability trends subsection
    trends_html = _build_profitability_trends_subsection(profitability_trends, companies)
    
    # Build charts
    dupont_charts_html = _build_dupont_charts(dupont_analysis, profitability_trends, df, companies)
    
    content = f"""
    <div class="collapsible-section">
        <div class="collapsible-header">
            <h3>4A. DuPont Analysis & Institutional-Weighted Profitability</h3>
            <span class="collapsible-toggle">▼</span>
        </div>
        <div class="collapsible-content">
            <div class="info-box info">
                <p>
                    Enhanced DuPont analysis decomposes Return on Equity (ROE) into three key components:
                    Net Profit Margin, Asset Turnover, and Equity Multiplier. This analysis incorporates
                    institutional ownership data to provide weighted profitability assessments.
                </p>
            </div>
            
            {dupont_html}
            
            {trends_html}
            
            {dupont_charts_html}
        </div>
    </div>
    """
    
    return content


def _calculate_dupont_analysis(df: pd.DataFrame, companies: Dict[str, str], 
                               institutional_df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate institutional-weighted DuPont analysis for all companies"""
    
    dupont_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Standard DuPont components
        net_margin = latest.get('netProfitMargin', 0)
        asset_turnover = latest.get('assetTurnover', 0)
        equity_multiplier = latest.get('financialLeverageRatio', 1)
        
        # Calculate ROE components
        metrics['net_margin'] = net_margin
        metrics['asset_turnover'] = asset_turnover
        metrics['equity_multiplier'] = equity_multiplier
        metrics['calculated_roe'] = net_margin * asset_turnover * equity_multiplier
        metrics['reported_roe'] = latest.get('returnOnEquity', 0)
        
        # Institutional weighting factors
        if not institutional_df.empty:
            inst_data = institutional_df[institutional_df['Company'] == company_name]
            if not inst_data.empty:
                latest_inst = inst_data.iloc[-1]
                ownership_pct = latest_inst.get('ownershipPercent', 0)
                investor_count = latest_inst.get('investorsHolding', 0)
                
                # Calculate institutional quality adjustment
                ownership_weight = min(ownership_pct / 100, 1.0) if ownership_pct > 0 else 0.3
                diversification_factor = min(np.log1p(investor_count) / 5, 1.0) if investor_count > 0 else 0.5
                
                metrics['institutional_ownership'] = ownership_pct
                metrics['investor_count'] = investor_count
                metrics['institutional_weight'] = (ownership_weight + diversification_factor) / 2
            else:
                metrics['institutional_ownership'] = 0
                metrics['investor_count'] = 0
                metrics['institutional_weight'] = 0.3
        else:
            metrics['institutional_ownership'] = 0
            metrics['investor_count'] = 0
            metrics['institutional_weight'] = 0.3
        
        # Institutional-weighted ROE
        base_quality = 0.8 + (metrics['institutional_weight'] * 0.4)
        metrics['weighted_roe'] = metrics['calculated_roe'] * base_quality
        
        # DuPont variance analysis
        metrics['dupont_variance'] = abs(metrics['calculated_roe'] - metrics['reported_roe'])
        
        # Quality assessment
        if metrics['dupont_variance'] < 0.5 and metrics['institutional_weight'] > 0.6:
            metrics['dupont_quality'] = 'Excellent'
        elif metrics['dupont_variance'] < 1.0 and metrics['institutional_weight'] > 0.4:
            metrics['dupont_quality'] = 'Good'
        elif metrics['dupont_variance'] < 2.0:
            metrics['dupont_quality'] = 'Fair'
        else:
            metrics['dupont_quality'] = 'Poor'
        
        # Component efficiency scores (0-10 scale)
        metrics['margin_efficiency'] = min(10, max(0, net_margin * 2))
        metrics['asset_efficiency'] = min(10, max(0, asset_turnover * 5))
        metrics['leverage_efficiency'] = min(10, max(0, 10 - abs(equity_multiplier - 2)))
        
        dupont_analysis[company_name] = metrics
    
    return dupont_analysis


def _calculate_profitability_trends(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate profitability trends with regime detection"""
    
    profitability_trends = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 3:
            continue
        
        metrics = {}
        
        # Basic profitability metrics
        roe_series = company_data['returnOnEquity'].dropna()
        roa_series = company_data['returnOnAssets'].dropna()
        net_margin_series = company_data['netProfitMargin'].dropna()
        
        if len(roe_series) >= 3:
            # 3-year average ROE
            metrics['avg_roe_3y'] = roe_series.tail(3).mean()
            metrics['roe_volatility'] = roe_series.std()
            
            # Regime detection (simplified change point analysis)
            roe_values = roe_series.values
            if len(roe_values) >= 5:
                window_size = min(3, len(roe_values) // 2)
                rolling_means = pd.Series(roe_values).rolling(window_size).mean().dropna()
                
                if len(rolling_means) >= 2:
                    recent_mean = rolling_means.iloc[-1]
                    historical_mean = rolling_means.iloc[:-window_size].mean()
                    
                    if recent_mean > historical_mean * 1.2:
                        metrics['current_regime'] = 'High Performance'
                        metrics['regime_years'] = window_size
                    elif recent_mean < historical_mean * 0.8:
                        metrics['current_regime'] = 'Underperformance'
                        metrics['regime_years'] = window_size
                    else:
                        metrics['current_regime'] = 'Stable Performance'
                        metrics['regime_years'] = len(roe_values)
                else:
                    metrics['current_regime'] = 'Insufficient Data'
                    metrics['regime_years'] = len(roe_values)
            else:
                metrics['current_regime'] = 'Limited History'
                metrics['regime_years'] = len(roe_values)
        else:
            metrics['avg_roe_3y'] = 0
            metrics['roe_volatility'] = 0
            metrics['current_regime'] = 'Insufficient Data'
            metrics['regime_years'] = 0
        
        # Margin stability analysis
        if len(net_margin_series) >= 3:
            margin_cv = net_margin_series.std() / (abs(net_margin_series.mean()) + 0.001)
            metrics['margin_stability'] = max(0, min(10, 10 - margin_cv * 5))
        else:
            metrics['margin_stability'] = 5
        
        # Profitability score (composite)
        roe_score = min(10, max(0, metrics['avg_roe_3y'] / 2))
        stability_score = 10 - min(10, metrics['roe_volatility'])
        margin_score = metrics['margin_stability']
        
        metrics['profitability_score'] = (roe_score * 0.5 + stability_score * 0.3 + margin_score * 0.2)
        
        # Trend direction
        if len(roe_series) >= 2:
            recent_roe = roe_series.iloc[-1]
            previous_roe = roe_series.iloc[-2]
            
            if recent_roe > previous_roe * 1.1:
                metrics['trend_direction'] = 'Improving'
            elif recent_roe < previous_roe * 0.9:
                metrics['trend_direction'] = 'Declining'
            else:
                metrics['trend_direction'] = 'Stable'
        else:
            metrics['trend_direction'] = 'Unknown'
        
        # Quality rating
        if metrics['profitability_score'] >= 8:
            metrics['quality_rating'] = 'Excellent'
        elif metrics['profitability_score'] >= 6:
            metrics['quality_rating'] = 'Good'
        elif metrics['profitability_score'] >= 4:
            metrics['quality_rating'] = 'Fair'
        else:
            metrics['quality_rating'] = 'Poor'
        
        # Risk level assessment
        if metrics['roe_volatility'] < 3 and metrics['margin_stability'] > 7:
            metrics['risk_level'] = 'Low'
        elif metrics['roe_volatility'] < 6 and metrics['margin_stability'] > 5:
            metrics['risk_level'] = 'Medium'
        else:
            metrics['risk_level'] = 'High'
        
        profitability_trends[company_name] = metrics
    
    return profitability_trends


def _build_dupont_decomposition_subsection(dupont_analysis: Dict[str, Dict], 
                                          companies: Dict[str, str]) -> str:
    """Build DuPont decomposition table and summary"""
    
    if not dupont_analysis:
        return '<div class="info-box warning"><p>Insufficient data for DuPont analysis.</p></div>'
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in dupont_analysis.items():
        efficiency_score = (metrics['margin_efficiency'] + metrics['asset_efficiency'] + 
                          metrics['leverage_efficiency']) / 3
        
        table_data.append({
            'Company': company_name,
            'Net Margin (%)': f"{metrics['net_margin']:.2f}",
            'Asset TO': f"{metrics['asset_turnover']:.2f}",
            'Equity Mult': f"{metrics['equity_multiplier']:.2f}",
            'Inst. Own. (%)': f"{metrics['institutional_ownership']:.1f}",
            'Investor Count': int(metrics['investor_count']),
            'Calculated ROE (%)': f"{metrics['calculated_roe']:.2f}",
            'Weighted ROE (%)': f"{metrics['weighted_roe']:.2f}",
            'Quality Rating': metrics['dupont_quality'],
            'Efficiency Score': f"{efficiency_score:.1f}/10"
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Determine quality color coding
    quality_color_map = {
        'Excellent': 'excellent',
        'Good': 'good',
        'Fair': 'fair',
        'Poor': 'poor'
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="dupont-analysis-table",
        color_columns={'Quality Rating': lambda x: quality_color_map.get(x, 'neutral')},
        badge_columns=['Quality Rating']
    )
    
    # Generate summary
    avg_net_margin = np.mean([m['net_margin'] for m in dupont_analysis.values()])
    avg_asset_turnover = np.mean([m['asset_turnover'] for m in dupont_analysis.values()])
    avg_institutional_weight = np.mean([m['institutional_weight'] for m in dupont_analysis.values()])
    high_quality_companies = sum(1 for m in dupont_analysis.values() if m['dupont_quality'] in ['Excellent', 'Good'])
    
    summary = f"""
    <div class="info-box success">
        <h4>DuPont Analysis Summary</h4>
        <ul>
            <li><strong>Portfolio Net Margin:</strong> {avg_net_margin:.2f}% average, reflecting pricing power and cost management</li>
            <li><strong>Asset Turnover:</strong> {avg_asset_turnover:.2f}x average, indicating operational efficiency levels</li>
            <li><strong>Institutional Validation:</strong> {avg_institutional_weight*100:.0f}% average institutional confidence weighting</li>
            <li><strong>Quality Distribution:</strong> {high_quality_companies}/{len(dupont_analysis)} companies ({(high_quality_companies/len(dupont_analysis)*100):.0f}%) rated as high-quality DuPont profiles</li>
        </ul>
    </div>
    """
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>Institutional-Enhanced DuPont Decomposition</h4>
        {table_html}
        {summary}
    </div>
    """


def _build_profitability_trends_subsection(profitability_trends: Dict[str, Dict], 
                                          companies: Dict[str, str]) -> str:
    """Build profitability trends and regime analysis table"""
    
    if not profitability_trends:
        return '<div class="info-box warning"><p>Insufficient data for profitability trends analysis.</p></div>'
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in profitability_trends.items():
        table_data.append({
            'Company': company_name,
            '3Y Avg ROE (%)': f"{metrics['avg_roe_3y']:.1f}",
            'ROE Volatility': f"{metrics['roe_volatility']:.1f}",
            'Current Regime': metrics['current_regime'],
            'Regime Years': metrics['regime_years'],
            'Margin Stability': f"{metrics['margin_stability']:.1f}/10",
            'Profitability Score': f"{metrics['profitability_score']:.1f}/10",
            'Trend Direction': metrics['trend_direction'],
            'Quality Rating': metrics['quality_rating'],
            'Risk Level': metrics['risk_level']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Define color/badge mappings
    quality_color_map = {
        'Excellent': 'excellent',
        'Good': 'good',
        'Fair': 'fair',
        'Poor': 'poor'
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="profitability-trends-table",
        color_columns={'Quality Rating': lambda x: quality_color_map.get(x, 'neutral')},
        badge_columns=['Current Regime', 'Trend Direction', 'Risk Level']
    )
    
    # Generate summary
    avg_prof_score = np.mean([m['profitability_score'] for m in profitability_trends.values()])
    high_performers = sum(1 for m in profitability_trends.values() if m['current_regime'] == 'High Performance')
    improving_trends = sum(1 for m in profitability_trends.values() if m['trend_direction'] == 'Improving')
    low_risk = sum(1 for m in profitability_trends.values() if m['risk_level'] == 'Low')
    
    summary = f"""
    <div class="info-box info">
        <h4>Profitability Regime Analysis Summary</h4>
        <ul>
            <li><strong>Portfolio Profitability Score:</strong> {avg_prof_score:.1f}/10 indicating {'excellent' if avg_prof_score >= 8 else 'good' if avg_prof_score >= 6 else 'fair'} overall quality</li>
            <li><strong>Performance Regimes:</strong> {high_performers}/{len(profitability_trends)} companies in high-performance regimes</li>
            <li><strong>Trend Momentum:</strong> {improving_trends}/{len(profitability_trends)} companies showing improving profitability trends</li>
            <li><strong>Risk Profile:</strong> {low_risk}/{len(profitability_trends)} companies classified as low-risk</li>
        </ul>
    </div>
    """
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>Profitability Regime Analysis & Trend Statistics</h4>
        {table_html}
        {summary}
    </div>
    """


def _build_dupont_charts(dupont_analysis: Dict[str, Dict], profitability_trends: Dict[str, Dict],
                        df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build standalone Plotly charts for DuPont analysis"""
    
    if not dupont_analysis:
        return ""
    
    companies_list = list(dupont_analysis.keys())
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    charts_html = '<h4 style="margin-top: 40px;">DuPont Analysis Visualizations</h4>'
    
    # Chart 1: Net Margin Comparison
    net_margins = [dupont_analysis[c]['net_margin'] for c in companies_list]
    
    fig1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': net_margins,
            'marker': {'color': colors[:len(companies_list)]},
            'text': [f"{val:.2f}%" for val in net_margins],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Net Margin: %{y:.2f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Net Profit Margin Analysis', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Net Margin (%)'},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig1_data, div_id="dupont-net-margin-chart", height=450)
    
    # Chart 2: Asset Turnover Comparison
    asset_turnovers = [dupont_analysis[c]['asset_turnover'] for c in companies_list]
    
    fig2_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': asset_turnovers,
            'marker': {'color': colors[:len(companies_list)]},
            'text': [f"{val:.2f}x" for val in asset_turnovers],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Asset Turnover: %{y:.2f}x<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Asset Turnover Efficiency', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Asset Turnover (x)'},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig2_data, div_id="dupont-asset-turnover-chart", height=450)
    
    # Chart 3: Equity Multiplier (Leverage)
    equity_multipliers = [dupont_analysis[c]['equity_multiplier'] for c in companies_list]
    
    fig3_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': equity_multipliers,
            'marker': {'color': colors[:len(companies_list)]},
            'text': [f"{val:.2f}x" for val in equity_multipliers],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Equity Multiplier: %{y:.2f}x<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Financial Leverage Analysis', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Equity Multiplier (x)'},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig3_data, div_id="dupont-equity-multiplier-chart", height=450)
    
    # Chart 4: Calculated ROE vs Weighted ROE
    calculated_roes = [dupont_analysis[c]['calculated_roe'] for c in companies_list]
    weighted_roes = [dupont_analysis[c]['weighted_roe'] for c in companies_list]
    
    fig4_data = {
        'data': [
            {
                'type': 'bar',
                'x': companies_list,
                'y': calculated_roes,
                'name': 'Calculated ROE',
                'marker': {'color': 'lightblue'},
                'hovertemplate': '<b>%{x}</b><br>Calculated ROE: %{y:.2f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'x': companies_list,
                'y': weighted_roes,
                'name': 'Weighted ROE',
                'marker': {'color': 'lightcoral'},
                'hovertemplate': '<b>%{x}</b><br>Weighted ROE: %{y:.2f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'DuPont ROE: Calculated vs Institutional-Weighted', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'ROE (%)'},
            'barmode': 'group',
            'showlegend': True,
            'legend': {'x': 0.7, 'y': 1.0}
        }
    }
    
    charts_html += build_plotly_chart(fig4_data, div_id="dupont-roe-comparison-chart", height=450)
    
    # Chart 5: ROE Evolution Over Time (if profitability trends available)
    if profitability_trends:
        roe_evolution_html = _build_roe_evolution_chart(df, companies)
        charts_html += roe_evolution_html
    
    # Chart 6: Profitability Score Comparison (if profitability trends available)
    if profitability_trends:
        prof_scores = [profitability_trends[c]['profitability_score'] for c in companies_list if c in profitability_trends]
        prof_companies = [c for c in companies_list if c in profitability_trends]
        
        fig6_data = {
            'data': [{
                'type': 'bar',
                'x': prof_companies,
                'y': prof_scores,
                'marker': {'color': colors[:len(prof_companies)]},
                'text': [f"{val:.1f}" for val in prof_scores],
                'textposition': 'outside',
                'hovertemplate': '<b>%{x}</b><br>Profitability Score: %{y:.1f}/10<extra></extra>'
            }],
            'layout': {
                'title': {'text': 'Profitability Quality Assessment', 'font': {'size': 18, 'weight': 'bold'}},
                'xaxis': {'title': 'Companies'},
                'yaxis': {'title': 'Profitability Score (0-10)', 'range': [0, 10]},
                'showlegend': False,
                'shapes': [{
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(prof_companies) - 0.5,
                    'y0': 5,
                    'y1': 5,
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                }],
                'annotations': [{
                    'x': len(prof_companies) - 0.5,
                    'y': 5,
                    'text': 'Benchmark',
                    'showarrow': False,
                    'xanchor': 'left',
                    'font': {'color': 'red'}
                }]
            }
        }
        
        charts_html += build_plotly_chart(fig6_data, div_id="profitability-score-chart", height=450)
    
    return charts_html


def _build_roe_evolution_chart(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build ROE evolution over time chart"""
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    traces = []
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) >= 2:
            years = company_data['Year'].tolist()
            roe_values = company_data['returnOnEquity'].tolist()
            
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years,
                'y': roe_values,
                'name': company_name,
                'line': {'color': colors[i % len(colors)], 'width': 3},
                'marker': {'size': 8},
                'hovertemplate': '<b>' + company_name + '</b><br>Year: %{x}<br>ROE: %{y:.2f}%<extra></extra>'
            })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'ROE Evolution & Trends', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Year'},
            'yaxis': {'title': 'Return on Equity (%)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'x': 1.05, 'y': 1.0}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roe-evolution-chart", height=500)


# =============================================================================
# SUBSECTION 4B: OPERATIONAL EFFICIENCY (STUB)
# =============================================================================

"""
Section 4 - Phase 2: Subsections 4B & 4C Implementation

This file contains the implementation for:
- 4B: Operational Efficiency & Asset Utilization Analysis
- 4C: Multi-Dimensional Return Analysis & Risk Assessment

Replace the stub functions in section_04.py with these implementations.
"""




# =============================================================================
# SUBSECTION 4B: OPERATIONAL EFFICIENCY & ASSET UTILIZATION ANALYSIS
# =============================================================================

def _build_section_4b_operational_efficiency(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build Section 4B: Operational Efficiency & Asset Utilization Analysis"""
    
    if df.empty:
        return ""
    
    # Calculate efficiency analysis
    efficiency_analysis = _calculate_operational_efficiency(df, companies)
    
    if not efficiency_analysis:
        return ""
    
    # Build efficiency metrics table
    efficiency_table_html = _build_efficiency_metrics_table(efficiency_analysis)
    
    # Build efficiency charts
    efficiency_charts_html = _build_efficiency_charts(efficiency_analysis, companies)
    
    content = f"""
    <div class="collapsible-section">
        <div class="collapsible-header">
            <h3>4B. Operational Efficiency & Asset Utilization Analysis</h3>
            <span class="collapsible-toggle">▼</span>
        </div>
        <div class="collapsible-content">
            <div class="info-box info">
                <p>
                    Operational efficiency analysis evaluates how effectively companies utilize their assets
                    to generate revenue. This includes asset turnover ratios, working capital management,
                    and cash conversion cycle metrics.
                </p>
            </div>
            
            {efficiency_table_html}
            
            {efficiency_charts_html}
        </div>
    </div>
    """
    
    return content


def _calculate_operational_efficiency(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate operational efficiency metrics for all companies"""
    
    efficiency_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core turnover ratios
        metrics['asset_turnover'] = latest.get('assetTurnover', 0)
        metrics['receivables_turnover'] = latest.get('receivablesTurnover', 0)
        metrics['inventory_turnover'] = latest.get('inventoryTurnover', 0)
        metrics['fixed_asset_turnover'] = latest.get('fixedAssetTurnover', 0)
        
        # Days calculations
        metrics['days_sales_outstanding'] = 365 / metrics['receivables_turnover'] if metrics['receivables_turnover'] > 0 else 0
        metrics['days_inventory_outstanding'] = 365 / metrics['inventory_turnover'] if metrics['inventory_turnover'] > 0 else 0
        
        # Working capital efficiency
        current_assets = latest.get('totalCurrentAssets', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        revenue = latest.get('revenue', 1)
        
        working_capital = current_assets - current_liabilities
        wc_turnover = revenue / working_capital if working_capital > 0 else 0
        
        # Working capital efficiency score (0-10)
        if wc_turnover > 10:
            metrics['working_capital_efficiency'] = 10
        elif wc_turnover > 5:
            metrics['working_capital_efficiency'] = 8
        elif wc_turnover > 2:
            metrics['working_capital_efficiency'] = 6
        elif wc_turnover > 1:
            metrics['working_capital_efficiency'] = 4
        else:
            metrics['working_capital_efficiency'] = 2
        
        # Overall efficiency score
        efficiency_components = [
            min(10, metrics['asset_turnover'] * 5),
            min(10, metrics['receivables_turnover'] / 2),
            min(10, metrics['inventory_turnover'] / 2),
            metrics['working_capital_efficiency']
        ]
        
        metrics['efficiency_score'] = np.mean([comp for comp in efficiency_components if comp > 0])
        
        # Efficiency trend analysis
        if len(company_data) >= 3:
            recent_turnover = company_data['assetTurnover'].tail(3).mean()
            earlier_turnover = company_data['assetTurnover'].head(3).mean()
            
            if pd.notna(recent_turnover) and pd.notna(earlier_turnover):
                if recent_turnover > earlier_turnover * 1.1:
                    metrics['efficiency_trend'] = 'Improving'
                elif recent_turnover < earlier_turnover * 0.9:
                    metrics['efficiency_trend'] = 'Declining'
                else:
                    metrics['efficiency_trend'] = 'Stable'
            else:
                metrics['efficiency_trend'] = 'Limited Data'
        else:
            metrics['efficiency_trend'] = 'Limited Data'
        
        efficiency_analysis[company_name] = metrics
    
    # Calculate efficiency rankings
    efficiency_scores = [(name, metrics['efficiency_score']) for name, metrics in efficiency_analysis.items()]
    efficiency_scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (company_name, _) in enumerate(efficiency_scores):
        efficiency_analysis[company_name]['efficiency_rank'] = rank + 1
    
    return efficiency_analysis


def _build_efficiency_metrics_table(efficiency_analysis: Dict[str, Dict]) -> str:
    """Build operational efficiency metrics table"""
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in efficiency_analysis.items():
        table_data.append({
            'Company': company_name,
            'Asset Turnover': f"{metrics['asset_turnover']:.2f}x",
            'Receivables TO': f"{metrics['receivables_turnover']:.1f}x",
            'Inventory TO': f"{metrics['inventory_turnover']:.1f}x",
            'Fixed Asset TO': f"{metrics['fixed_asset_turnover']:.2f}x",
            'DSO (Days)': f"{metrics['days_sales_outstanding']:.0f}",
            'DIO (Days)': f"{metrics['days_inventory_outstanding']:.0f}",
            'WC Efficiency': f"{metrics['working_capital_efficiency']:.1f}/10",
            'Efficiency Score': f"{metrics['efficiency_score']:.1f}/10",
            'Efficiency Rank': f"{metrics['efficiency_rank']}/{len(efficiency_analysis)}",
            'Trend': metrics['efficiency_trend']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Color/badge mappings
    trend_color_map = {
        'Improving': 'excellent',
        'Stable': 'good',
        'Declining': 'poor',
        'Limited Data': 'neutral'
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="operational-efficiency-table",
        color_columns={'Trend': lambda x: trend_color_map.get(x, 'neutral')},
        badge_columns=['Trend']
    )
    
    # Generate summary
    avg_efficiency_score = np.mean([m['efficiency_score'] for m in efficiency_analysis.values()])
    high_efficiency = sum(1 for m in efficiency_analysis.values() if m['efficiency_score'] >= 7)
    improving = sum(1 for m in efficiency_analysis.values() if m['efficiency_trend'] == 'Improving')
    
    summary = f"""
    <div class="info-box success">
        <h4>Operational Efficiency Summary</h4>
        <ul>
            <li><strong>Portfolio Efficiency Score:</strong> {avg_efficiency_score:.1f}/10 indicating {'excellent' if avg_efficiency_score >= 8 else 'good' if avg_efficiency_score >= 6 else 'moderate'} operational efficiency</li>
            <li><strong>High-Efficiency Companies:</strong> {high_efficiency}/{len(efficiency_analysis)} companies achieving excellence ratings (7+)</li>
            <li><strong>Efficiency Momentum:</strong> {improving}/{len(efficiency_analysis)} companies showing improving efficiency trends</li>
            <li><strong>Working Capital Management:</strong> {sum(1 for m in efficiency_analysis.values() if m['working_capital_efficiency'] >= 8)}/{len(efficiency_analysis)} companies with excellent WC efficiency</li>
        </ul>
    </div>
    """
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>Advanced Efficiency Metrics & Turnover Analysis</h4>
        {table_html}
        {summary}
    </div>
    """


def _build_efficiency_charts(efficiency_analysis: Dict[str, Dict], companies: Dict[str, str]) -> str:
    """Build operational efficiency visualization charts"""
    
    companies_list = list(efficiency_analysis.keys())
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    charts_html = '<h4 style="margin-top: 40px;">Operational Efficiency Visualizations</h4>'
    
    # Chart 1: Asset Turnover Comparison
    asset_turnovers = [efficiency_analysis[c]['asset_turnover'] for c in companies_list]
    
    fig1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': asset_turnovers,
            'marker': {'color': colors[:len(companies_list)]},
            'text': [f"{val:.2f}x" for val in asset_turnovers],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Asset Turnover: %{y:.2f}x<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Asset Turnover Efficiency', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Asset Turnover (x)'},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig1_data, div_id="asset-turnover-chart", height=450)
    
    # Chart 2: Working Capital Efficiency vs Overall Efficiency Scatter
    wc_efficiency = [efficiency_analysis[c]['working_capital_efficiency'] for c in companies_list]
    overall_efficiency = [efficiency_analysis[c]['efficiency_score'] for c in companies_list]
    
    fig2_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': wc_efficiency,
            'y': overall_efficiency,
            'text': companies_list,
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors[:len(companies_list)],
                'line': {'color': 'black', 'width': 1}
            },
            'hovertemplate': '<b>%{text}</b><br>WC Efficiency: %{x:.1f}/10<br>Overall Efficiency: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Efficiency Correlation Matrix', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Working Capital Efficiency (0-10)', 'range': [0, 11]},
            'yaxis': {'title': 'Overall Efficiency Score (0-10)', 'range': [0, 11]},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig2_data, div_id="efficiency-correlation-chart", height=450)
    
    # Chart 3: Days Metrics Comparison (DSO vs DIO)
    dso_values = [efficiency_analysis[c]['days_sales_outstanding'] for c in companies_list]
    dio_values = [efficiency_analysis[c]['days_inventory_outstanding'] for c in companies_list]
    
    fig3_data = {
        'data': [
            {
                'type': 'bar',
                'x': companies_list,
                'y': dso_values,
                'name': 'DSO (Days)',
                'marker': {'color': 'lightblue'},
                'hovertemplate': '<b>%{x}</b><br>DSO: %{y:.0f} days<extra></extra>'
            },
            {
                'type': 'bar',
                'x': companies_list,
                'y': dio_values,
                'name': 'DIO (Days)',
                'marker': {'color': 'lightgreen'},
                'hovertemplate': '<b>%{x}</b><br>DIO: %{y:.0f} days<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Working Capital Cycle Components', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Days'},
            'barmode': 'group',
            'showlegend': True
        }
    }
    
    charts_html += build_plotly_chart(fig3_data, div_id="days-metrics-chart", height=450)
    
    # Chart 4: Efficiency Score Rankings (Horizontal Bar)
    sorted_data = sorted(efficiency_analysis.items(), key=lambda x: x[1]['efficiency_rank'])
    sorted_companies = [item[0] for item in sorted_data]
    sorted_scores = [item[1]['efficiency_score'] for item in sorted_data]
    sorted_ranks = [item[1]['efficiency_rank'] for item in sorted_data]
    
    fig4_data = {
        'data': [{
            'type': 'bar',
            'orientation': 'h',
            'x': sorted_scores,
            'y': [f"{c} (#{r})" for c, r in zip(sorted_companies, sorted_ranks)],
            'marker': {'color': colors[:len(sorted_companies)]},
            'text': [f"{val:.1f}" for val in sorted_scores],
            'textposition': 'outside',
            'hovertemplate': '<b>%{y}</b><br>Efficiency Score: %{x:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Efficiency Score Rankings', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Efficiency Score (0-10)', 'range': [0, 11]},
            'yaxis': {'title': 'Companies (with Rank)'},
            'showlegend': False,
            'height': max(400, len(sorted_companies) * 40)
        }
    }
    
    charts_html += build_plotly_chart(fig4_data, div_id="efficiency-rankings-chart", height=max(450, len(sorted_companies) * 40))
    
    return charts_html


# =============================================================================
# SUBSECTION 4C: MULTI-DIMENSIONAL RETURN ANALYSIS & RISK ASSESSMENT
# =============================================================================

def _build_section_4c_multidimensional_returns(df: pd.DataFrame, companies: Dict[str, str],
                                               prices_df: pd.DataFrame, 
                                               institutional_df: pd.DataFrame) -> str:
    """Build Section 4C: Multi-Dimensional Return Analysis & Risk Assessment"""
    
    if df.empty:
        return ""
    
    # Calculate return analysis
    return_analysis = _calculate_multidimensional_returns(df, companies, prices_df, institutional_df)
    
    if not return_analysis:
        return ""
    
    # Build return metrics table
    return_table_html = _build_return_metrics_table(return_analysis)
    
    # Build return charts
    return_charts_html = _build_return_charts(return_analysis, companies)
    
    content = f"""
    <div class="collapsible-section">
        <div class="collapsible-header">
            <h3>4C. Multi-Dimensional Return Analysis & Risk Assessment</h3>
            <span class="collapsible-toggle">▼</span>
        </div>
        <div class="collapsible-content">
            <div class="info-box info">
                <p>
                    Multi-dimensional return analysis evaluates profitability from multiple perspectives:
                    Return on Equity (ROE), Return on Assets (ROA), Return on Invested Capital (ROIC),
                    and Return on Capital Employed (ROCE). This analysis includes risk adjustment and
                    consistency metrics.
                </p>
            </div>
            
            {return_table_html}
            
            {return_charts_html}
        </div>
    </div>
    """
    
    return content


def _calculate_multidimensional_returns(df: pd.DataFrame, companies: Dict[str, str],
                                       prices_df: pd.DataFrame, 
                                       institutional_df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate multi-dimensional return metrics with risk adjustment"""
    
    return_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core return metrics
        metrics['roe'] = latest.get('returnOnEquity', 0)
        metrics['roa'] = latest.get('returnOnAssets', 0)
        metrics['roic'] = latest.get('returnOnInvestedCapital', 0)
        metrics['roce'] = latest.get('returnOnCapitalEmployed', 0)
        
        # Return volatility analysis
        if len(company_data) >= 3:
            roe_series = company_data['returnOnEquity'].dropna()
            if len(roe_series) >= 3:
                metrics['return_volatility'] = roe_series.std()
                
                # Return consistency (inverse of coefficient of variation)
                mean_roe = roe_series.mean()
                if mean_roe > 0:
                    cv = metrics['return_volatility'] / mean_roe
                    metrics['return_consistency'] = max(0, min(10, 10 - cv * 2))
                else:
                    metrics['return_consistency'] = 0
            else:
                metrics['return_volatility'] = 0
                metrics['return_consistency'] = 5
        else:
            metrics['return_volatility'] = 0
            metrics['return_consistency'] = 5
        
        # Risk-adjusted return calculation
        risk_free_rate = 3.0  # Assumption
        if metrics['return_volatility'] > 0:
            sharpe_like_ratio = (metrics['roe'] - risk_free_rate) / metrics['return_volatility']
            metrics['risk_adjusted_roe'] = metrics['roe'] * (1 + sharpe_like_ratio / 10)
        else:
            metrics['risk_adjusted_roe'] = metrics['roe']
        
        # Return quality score
        quality_components = [
            min(10, max(0, metrics['roe'] / 2)),
            min(10, max(0, metrics['roa'] / 1.5)),
            min(10, max(0, metrics['roic'] / 2)),
            metrics['return_consistency']
        ]
        
        metrics['return_quality'] = np.mean([comp for comp in quality_components if comp > 0])
        
        # Return rating
        if metrics['return_quality'] >= 8:
            metrics['return_rating'] = 'Superior'
        elif metrics['return_quality'] >= 6:
            metrics['return_rating'] = 'Above Average'
        elif metrics['return_quality'] >= 4:
            metrics['return_rating'] = 'Average'
        else:
            metrics['return_rating'] = 'Below Average'
        
        # Return outlook based on trends
        if len(company_data) >= 2:
            current_roe = company_data['returnOnEquity'].iloc[-1]
            previous_roe = company_data['returnOnEquity'].iloc[-2]
            
            if pd.notna(current_roe) and pd.notna(previous_roe):
                if current_roe > previous_roe * 1.1:
                    metrics['return_outlook'] = 'Positive'
                elif current_roe < previous_roe * 0.9:
                    metrics['return_outlook'] = 'Negative'
                else:
                    metrics['return_outlook'] = 'Stable'
            else:
                metrics['return_outlook'] = 'Uncertain'
        else:
            metrics['return_outlook'] = 'Limited Data'
        
        return_analysis[company_name] = metrics
    
    # Calculate percentile rankings
    if return_analysis:
        return_quality_scores = [metrics['return_quality'] for metrics in return_analysis.values()]
        
        for company_name, metrics in return_analysis.items():
            percentile = (sum(1 for score in return_quality_scores if score < metrics['return_quality']) / len(return_quality_scores)) * 100
            metrics['percentile_rank'] = percentile
    
    return return_analysis


def _build_return_metrics_table(return_analysis: Dict[str, Dict]) -> str:
    """Build multi-dimensional return metrics table"""
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in return_analysis.items():
        table_data.append({
            'Company': company_name,
            'ROE (%)': f"{metrics['roe']:.1f}",
            'ROA (%)': f"{metrics['roa']:.1f}",
            'ROIC (%)': f"{metrics['roic']:.1f}",
            'ROCE (%)': f"{metrics['roce']:.1f}",
            'Risk-Adj ROE': f"{metrics['risk_adjusted_roe']:.1f}",
            'Return Quality': f"{metrics['return_quality']:.1f}/10",
            'Volatility': f"{metrics['return_volatility']:.1f}",
            'Consistency': f"{metrics['return_consistency']:.1f}/10",
            'Percentile Rank': f"{metrics['percentile_rank']:.0f}th",
            'Rating': metrics['return_rating'],
            'Outlook': metrics['return_outlook']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Color/badge mappings
    rating_color_map = {
        'Superior': 'excellent',
        'Above Average': 'good',
        'Average': 'fair',
        'Below Average': 'poor'
    }
    
    outlook_color_map = {
        'Positive': 'excellent',
        'Stable': 'good',
        'Negative': 'poor',
        'Uncertain': 'neutral',
        'Limited Data': 'neutral'
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="return-analysis-table",
        color_columns={
            'Rating': lambda x: rating_color_map.get(x, 'neutral'),
            'Outlook': lambda x: outlook_color_map.get(x, 'neutral')
        },
        badge_columns=['Rating', 'Outlook']
    )
    
    # Generate summary
    avg_roe = np.mean([m['roe'] for m in return_analysis.values()])
    avg_return_quality = np.mean([m['return_quality'] for m in return_analysis.values()])
    superior_returns = sum(1 for m in return_analysis.values() if m['return_rating'] == 'Superior')
    positive_outlook = sum(1 for m in return_analysis.values() if m['return_outlook'] == 'Positive')
    
    summary = f"""
    <div class="info-box success">
        <h4>Multi-Dimensional Return Analysis Summary</h4>
        <ul>
            <li><strong>Portfolio Return Profile:</strong> {avg_roe:.1f}% average ROE with {avg_return_quality:.1f}/10 return quality score</li>
            <li><strong>Superior Performance:</strong> {superior_returns}/{len(return_analysis)} companies achieving superior return ratings</li>
            <li><strong>Return Outlook:</strong> {positive_outlook}/{len(return_analysis)} companies with positive return momentum</li>
            <li><strong>Risk-Adjusted Performance:</strong> {'Strong' if avg_return_quality >= 7 else 'Moderate' if avg_return_quality >= 5 else 'Weak'} portfolio-wide risk-adjusted returns</li>
        </ul>
    </div>
    """
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>Return Metrics & Risk-Adjusted Performance</h4>
        {table_html}
        {summary}
    </div>
    """


def _build_return_charts(return_analysis: Dict[str, Dict], companies: Dict[str, str]) -> str:
    """Build multi-dimensional return visualization charts"""
    
    companies_list = list(return_analysis.keys())
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    charts_html = '<h4 style="margin-top: 40px;">Multi-Dimensional Returns Visualizations</h4>'
    
    # Chart 1: Return Metrics Heatmap
    return_metrics = ['roe', 'roa', 'roic', 'roce']
    heatmap_data = []
    
    for company in companies_list:
        row_data = []
        for metric in return_metrics:
            row_data.append(return_analysis[company].get(metric, 0))
        heatmap_data.append(row_data)
    
    # Create heatmap using Plotly
    fig1_data = {
        'data': [{
            'type': 'heatmap',
            'z': heatmap_data,
            'x': ['ROE', 'ROA', 'ROIC', 'ROCE'],
            'y': companies_list,
            'colorscale': 'RdYlGn',
            'zmid': 10,
            'text': [[f"{val:.1f}%" for val in row] for row in heatmap_data],
            'texttemplate': '%{text}',
            'textfont': {'size': 10},
            'hovertemplate': '<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Multi-Dimensional Return Metrics Heatmap', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Return Metrics', 'side': 'top'},
            'yaxis': {'title': 'Companies'},
            'height': max(400, len(companies_list) * 40)
        }
    }
    
    charts_html += build_plotly_chart(fig1_data, div_id="return-metrics-heatmap", height=max(450, len(companies_list) * 40))
    
    # Chart 2: Return Quality vs Return Level Scatter
    return_quality = [return_analysis[c]['return_quality'] for c in companies_list]
    roe_values = [return_analysis[c]['roe'] for c in companies_list]
    
    fig2_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': return_quality,
            'y': roe_values,
            'text': companies_list,
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors[:len(companies_list)],
                'line': {'color': 'black', 'width': 1}
            },
            'hovertemplate': '<b>%{text}</b><br>Return Quality: %{x:.1f}/10<br>ROE: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Return Quality vs Return Level', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Return Quality Score (0-10)', 'range': [0, 11]},
            'yaxis': {'title': 'ROE (%)'},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig2_data, div_id="return-quality-scatter", height=450)
    
    # Chart 3: Risk-Adjusted Returns Comparison
    risk_adj_roe = [return_analysis[c]['risk_adjusted_roe'] for c in companies_list]
    
    fig3_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': risk_adj_roe,
            'marker': {'color': colors[:len(companies_list)]},
            'text': [f"{val:.1f}%" for val in risk_adj_roe],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Risk-Adjusted ROE: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Risk-Adjusted Return Performance', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Risk-Adjusted ROE (%)'},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig3_data, div_id="risk-adjusted-roe-chart", height=450)
    
    # Chart 4: Return Volatility vs Consistency Scatter
    return_volatility = [return_analysis[c]['return_volatility'] for c in companies_list]
    return_consistency = [return_analysis[c]['return_consistency'] for c in companies_list]
    
    fig4_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': return_volatility,
            'y': return_consistency,
            'text': companies_list,
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors[:len(companies_list)],
                'line': {'color': 'black', 'width': 1}
            },
            'hovertemplate': '<b>%{text}</b><br>Volatility: %{x:.1f}<br>Consistency: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Return Volatility vs Consistency', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Return Volatility'},
            'yaxis': {'title': 'Return Consistency (0-10)', 'range': [0, 11]},
            'showlegend': False
        }
    }
    
    charts_html += build_plotly_chart(fig4_data, div_id="volatility-consistency-scatter", height=450)
    
    return charts_html


"""
Section 4 - Phase 3: Subsection 4D Implementation

This file contains the implementation for:
- 4D: Economic Value Added & Value Creation Analysis

Replace the stub function in section_04.py with this implementation.
"""



# =============================================================================
# SUBSECTION 4D: ECONOMIC VALUE ADDED & VALUE CREATION ANALYSIS
# =============================================================================

def _build_section_4d_economic_value_added(df: pd.DataFrame, companies: Dict[str, str],
                                          economic_df: pd.DataFrame) -> str:
    """Build Section 4D: Economic Value Added & Value Creation Analysis"""
    
    if df.empty:
        return ""
    
    # Calculate EVA analysis
    eva_analysis = _calculate_economic_value_added(df, companies, economic_df)
    
    if not eva_analysis:
        return ""
    
    # Build EVA metrics table
    eva_table_html = _build_eva_metrics_table(eva_analysis)
    
    # Build EVA charts
    eva_charts_html = _build_eva_charts(eva_analysis, companies)
    
    content = f"""
    <div class="collapsible-section">
        <div class="collapsible-header">
            <h3>4D. Economic Value Added & Value Creation Analysis</h3>
            <span class="collapsible-toggle">▼</span>
        </div>
        <div class="collapsible-content">
            <div class="info-box info">
                <p>
                    Economic Value Added (EVA) measures true economic profit by comparing Return on Invested Capital (ROIC)
                    to the Weighted Average Cost of Capital (WACC). Positive EVA indicates value creation, while negative
                    EVA suggests value destruction. This analysis provides insights into capital allocation effectiveness
                    and long-term value generation capability.
                </p>
            </div>
            
            {eva_table_html}
            
            {eva_charts_html}
        </div>
    </div>
    """
    
    return content


def _calculate_economic_value_added(df: pd.DataFrame, companies: Dict[str, str],
                                   economic_df: pd.DataFrame) -> Dict[str, Dict]:
    """Calculate Economic Value Added and value creation metrics"""
    
    eva_analysis = {}
    
    # Risk-free rate estimation (from economic data if available)
    risk_free_rate = 4.0  # Default assumption
    if not economic_df.empty and 'Treasury_10Y' in economic_df.columns:
        latest_treasury = economic_df['Treasury_10Y'].dropna().iloc[-1] if len(economic_df['Treasury_10Y'].dropna()) > 0 else 4.0
        risk_free_rate = latest_treasury
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # NOPAT calculation (Net Operating Profit After Tax)
        ebit = latest.get('ebit', latest.get('operatingIncome', 0))
        tax_rate = 0.25  # Assumption, could be calculated from data
        nopat = ebit * (1 - tax_rate)
        metrics['nopat'] = nopat
        
        # Invested Capital calculation
        total_assets = latest.get('totalAssets', 0)
        cash = latest.get('cashAndCashEquivalents', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        invested_capital = total_assets - cash - current_liabilities
        metrics['invested_capital'] = max(invested_capital, total_assets * 0.5)  # Minimum threshold
        
        # WACC calculation (simplified)
        debt_to_equity = latest.get('debtToEquityRatio', 0.3)
        
        # Estimate cost of equity (CAPM-like approach)
        beta = 1.2  # Default assumption
        market_risk_premium = 6.0  # Market risk premium assumption
        cost_of_equity = risk_free_rate + beta * market_risk_premium
        
        # Cost of debt
        interest_expense = latest.get('interestExpense', 0)
        total_debt = latest.get('totalDebt', 0)
        cost_of_debt = (interest_expense / total_debt * 100) if total_debt > 0 else 5.0
        
        # WACC calculation
        if debt_to_equity > 0:
            weight_debt = debt_to_equity / (1 + debt_to_equity)
            weight_equity = 1 / (1 + debt_to_equity)
            wacc = (weight_equity * cost_of_equity + weight_debt * cost_of_debt * (1 - tax_rate))
        else:
            wacc = cost_of_equity
        
        metrics['wacc'] = wacc
        
        # EVA calculation
        eva = nopat - (wacc / 100 * metrics['invested_capital'])
        metrics['eva'] = eva
        
        # EVA margin
        revenue = latest.get('revenue', 1)
        metrics['eva_margin'] = (eva / revenue) * 100 if revenue > 0 else 0
        
        # ROIC calculation
        roic = (nopat / metrics['invested_capital']) * 100 if metrics['invested_capital'] > 0 else 0
        metrics['roic'] = roic
        
        # ROIC vs WACC spread
        metrics['roic_wacc_spread'] = roic - wacc
        
        # Value creation assessment
        if eva > 0:
            if metrics['roic_wacc_spread'] > 5:
                metrics['value_creation'] = 'Excellent'
            elif metrics['roic_wacc_spread'] > 2:
                metrics['value_creation'] = 'Good'
            else:
                metrics['value_creation'] = 'Marginal'
        else:
            if eva > -metrics['invested_capital'] * 0.02:  # Within 2% of invested capital
                metrics['value_creation'] = 'Break-even'
            else:
                metrics['value_creation'] = 'Destroying'
        
        # EVA sustainability assessment
        if len(company_data) >= 3:
            # Check for consistent profitability
            recent_margins = company_data['netProfitMargin'].tail(3).dropna()
            recent_roe = company_data['returnOnEquity'].tail(3).dropna()
            
            if len(recent_margins) >= 3 and len(recent_roe) >= 3:
                margin_stability = recent_margins.std()
                roe_stability = recent_roe.std()
                
                avg_stability = (10 - min(10, margin_stability)) + (10 - min(10, roe_stability))
                sustainability_score = avg_stability / 2
                
                if sustainability_score >= 8:
                    metrics['sustainability_rating'] = 'Highly Sustainable'
                elif sustainability_score >= 6:
                    metrics['sustainability_rating'] = 'Sustainable'
                elif sustainability_score >= 4:
                    metrics['sustainability_rating'] = 'Moderate'
                else:
                    metrics['sustainability_rating'] = 'Unsustainable'
            else:
                metrics['sustainability_rating'] = 'Unknown'
        else:
            metrics['sustainability_rating'] = 'Unknown'
        
        eva_analysis[company_name] = metrics
    
    # Calculate EVA rankings
    eva_values = [(name, metrics['eva']) for name, metrics in eva_analysis.items()]
    eva_values.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (company_name, _) in enumerate(eva_values):
        eva_analysis[company_name]['eva_rank'] = rank + 1
    
    return eva_analysis


def _build_eva_metrics_table(eva_analysis: Dict[str, Dict]) -> str:
    """Build EVA metrics table with comprehensive value creation assessment"""
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in eva_analysis.items():
        table_data.append({
            'Company': company_name,
            'NOPAT ($M)': f"${metrics['nopat']/1000000:.0f}",
            'Invested Cap ($M)': f"${metrics['invested_capital']/1000000:.0f}",
            'WACC (%)': f"{metrics['wacc']:.1f}",
            'EVA ($M)': f"${metrics['eva']/1000000:.0f}",
            'EVA Margin (%)': f"{metrics['eva_margin']:.2f}",
            'ROIC vs WACC': f"{metrics['roic_wacc_spread']:.1f}pp",
            'Value Creation': metrics['value_creation'],
            'Sustainability': metrics['sustainability_rating'],
            'EVA Rank': f"{metrics['eva_rank']}/{len(eva_analysis)}"
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Color/badge mappings
    value_creation_color_map = {
        'Excellent': 'excellent',
        'Good': 'good',
        'Marginal': 'fair',
        'Break-even': 'neutral',
        'Destroying': 'poor'
    }
    
    sustainability_color_map = {
        'Highly Sustainable': 'excellent',
        'Sustainable': 'good',
        'Moderate': 'fair',
        'Unsustainable': 'poor',
        'Unknown': 'neutral'
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="eva-analysis-table",
        color_columns={
            'Value Creation': lambda x: value_creation_color_map.get(x, 'neutral'),
            'Sustainability': lambda x: sustainability_color_map.get(x, 'neutral')
        },
        badge_columns=['Value Creation', 'Sustainability']
    )
    
    # Generate summary
    total_eva = sum(m['eva'] for m in eva_analysis.values())
    avg_roic_wacc_spread = np.mean([m['roic_wacc_spread'] for m in eva_analysis.values()])
    value_creators = sum(1 for m in eva_analysis.values() if m['eva'] > 0)
    excellent_creators = sum(1 for m in eva_analysis.values() if m['value_creation'] == 'Excellent')
    sustainable_creators = sum(1 for m in eva_analysis.values() if m['sustainability_rating'] in ['Highly Sustainable', 'Sustainable'])
    
    summary = f"""
    <div class="info-box {'success' if total_eva > 0 else 'warning'}">
        <h4>Economic Value Added Summary</h4>
        <ul>
            <li><strong>Portfolio EVA Performance:</strong> ${total_eva/1000000:.0f}M total economic value {'created' if total_eva > 0 else 'destroyed'}</li>
            <li><strong>ROIC-WACC Spread:</strong> {avg_roic_wacc_spread:.1f}pp average spread indicating {'strong' if avg_roic_wacc_spread > 3 else 'adequate' if avg_roic_wacc_spread > 0 else 'poor'} value creation</li>
            <li><strong>Value Creator Distribution:</strong> {value_creators}/{len(eva_analysis)} companies ({(value_creators/len(eva_analysis)*100):.0f}%) generating positive economic value</li>
            <li><strong>Excellence in Value Creation:</strong> {excellent_creators}/{len(eva_analysis)} companies achieving excellent ratings</li>
            <li><strong>Sustainability Profile:</strong> {sustainable_creators}/{len(eva_analysis)} companies with sustainable value creation characteristics</li>
        </ul>
    </div>
    """
    
    return f"""
    <div style="margin: 30px 0;">
        <h4>EVA Calculation & Value Creation Assessment</h4>
        {table_html}
        {summary}
    </div>
    """


def _build_eva_charts(eva_analysis: Dict[str, Dict], companies: Dict[str, str]) -> str:
    """Build Economic Value Added visualization charts"""
    
    companies_list = list(eva_analysis.keys())
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    charts_html = '<h4 style="margin-top: 40px;">Economic Value Added Visualizations</h4>'
    
    # Chart 1: EVA Values Comparison (with color coding for positive/negative)
    eva_values = [eva_analysis[c]['eva']/1000000 for c in companies_list]  # Convert to millions
    
    # Color bars based on positive/negative EVA
    bar_colors = ['green' if eva > 0 else 'red' for eva in eva_values]
    
    fig1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': eva_values,
            'marker': {'color': bar_colors},
            'text': [f"${val:.0f}M" for val in eva_values],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>EVA: $%{y:.0f}M<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Economic Value Added Analysis', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'EVA ($M)'},
            'showlegend': False,
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies_list) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2}
            }]
        }
    }
    
    charts_html += build_plotly_chart(fig1_data, div_id="eva-values-chart", height=450)
    
    # Chart 2: ROIC vs WACC Comparison
    roic_values = [eva_analysis[c]['roic'] for c in companies_list]
    wacc_values = [eva_analysis[c]['wacc'] for c in companies_list]
    
    fig2_data = {
        'data': [
            {
                'type': 'bar',
                'x': companies_list,
                'y': roic_values,
                'name': 'ROIC (%)',
                'marker': {'color': 'lightblue'},
                'hovertemplate': '<b>%{x}</b><br>ROIC: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'x': companies_list,
                'y': wacc_values,
                'name': 'WACC (%)',
                'marker': {'color': 'lightcoral'},
                'hovertemplate': '<b>%{x}</b><br>WACC: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'ROIC vs WACC Comparison', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Rate (%)'},
            'barmode': 'group',
            'showlegend': True,
            'legend': {'x': 0.7, 'y': 1.0}
        }
    }
    
    charts_html += build_plotly_chart(fig2_data, div_id="roic-wacc-comparison-chart", height=450)
    
    # Chart 3: EVA Margin vs ROIC-WACC Spread Scatter
    eva_margins = [eva_analysis[c]['eva_margin'] for c in companies_list]
    roic_wacc_spreads = [eva_analysis[c]['roic_wacc_spread'] for c in companies_list]
    
    fig3_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': roic_wacc_spreads,
            'y': eva_margins,
            'text': companies_list,
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors[:len(companies_list)],
                'line': {'color': 'black', 'width': 1}
            },
            'hovertemplate': '<b>%{text}</b><br>ROIC-WACC Spread: %{x:.1f}pp<br>EVA Margin: %{y:.2f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Value Creation Efficiency Matrix', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'ROIC-WACC Spread (pp)', 'zeroline': True},
            'yaxis': {'title': 'EVA Margin (%)', 'zeroline': True},
            'showlegend': False,
            'shapes': [
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': 0,
                    'y0': min(eva_margins) - 1,
                    'y1': max(eva_margins) + 1,
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': min(roic_wacc_spreads) - 1,
                    'x1': max(roic_wacc_spreads) + 1,
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                }
            ]
        }
    }
    
    charts_html += build_plotly_chart(fig3_data, div_id="eva-efficiency-matrix", height=450)
    
    # Chart 4: Value Creation Distribution (Pie Chart)
    value_creation_categories = {}
    for company in companies_list:
        category = eva_analysis[company]['value_creation']
        value_creation_categories[category] = value_creation_categories.get(category, 0) + 1
    
    if value_creation_categories:
        categories = list(value_creation_categories.keys())
        counts = list(value_creation_categories.values())
        
        # Custom colors for value creation categories
        category_colors_map = {
            'Excellent': 'darkgreen',
            'Good': 'green',
            'Marginal': 'orange',
            'Break-even': 'yellow',
            'Destroying': 'red'
        }
        pie_colors = [category_colors_map.get(cat, 'gray') for cat in categories]
        
        fig4_data = {
            'data': [{
                'type': 'pie',
                'labels': categories,
                'values': counts,
                'marker': {'colors': pie_colors},
                'textinfo': 'label+percent',
                'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            }],
            'layout': {
                'title': {'text': 'Value Creation Distribution', 'font': {'size': 18, 'weight': 'bold'}},
                'showlegend': True
            }
        }
        
        charts_html += build_plotly_chart(fig4_data, div_id="value-creation-distribution", height=450)
    
    # Chart 5: ROIC-WACC Spread Waterfall
    sorted_data = sorted(eva_analysis.items(), key=lambda x: x[1]['roic_wacc_spread'], reverse=True)
    sorted_companies = [item[0] for item in sorted_data]
    sorted_spreads = [item[1]['roic_wacc_spread'] for item in sorted_data]
    
    # Color code bars based on positive/negative spread
    spread_colors = ['green' if spread > 0 else 'red' for spread in sorted_spreads]
    
    fig5_data = {
        'data': [{
            'type': 'bar',
            'x': sorted_companies,
            'y': sorted_spreads,
            'marker': {'color': spread_colors},
            'text': [f"{val:.1f}pp" for val in sorted_spreads],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>ROIC-WACC Spread: %{y:.1f}pp<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'ROIC-WACC Spread Rankings', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies (Ranked by Spread)'},
            'yaxis': {'title': 'ROIC-WACC Spread (pp)'},
            'showlegend': False,
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(sorted_companies) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2, 'dash': 'dash'}
            }]
        }
    }
    
    charts_html += build_plotly_chart(fig5_data, div_id="roic-wacc-spread-rankings", height=450)
    
    # Chart 6: EVA vs Invested Capital Bubble Chart
    eva_millions = [eva_analysis[c]['eva']/1000000 for c in companies_list]
    invested_cap_millions = [eva_analysis[c]['invested_capital']/1000000 for c in companies_list]
    roic_sizes = [abs(eva_analysis[c]['roic']) * 2 for c in companies_list]  # Size based on ROIC
    
    fig6_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': invested_cap_millions,
            'y': eva_millions,
            'text': companies_list,
            'textposition': 'top center',
            'marker': {
                'size': roic_sizes,
                'color': colors[:len(companies_list)],
                'line': {'color': 'black', 'width': 1},
                'sizemode': 'diameter'
            },
            'hovertemplate': '<b>%{text}</b><br>Invested Capital: $%{x:.0f}M<br>EVA: $%{y:.0f}M<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'EVA vs Invested Capital (Bubble size = ROIC)', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Invested Capital ($M)'},
            'yaxis': {'title': 'EVA ($M)', 'zeroline': True},
            'showlegend': False,
            'shapes': [{
                'type': 'line',
                'x0': 0,
                'x1': max(invested_cap_millions) * 1.1,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
            }]
        }
    }
    
    charts_html += build_plotly_chart(fig6_data, div_id="eva-invested-capital-bubble", height=500)
    
    return charts_html


"""
Section 4 - Phase 4: Subsections 4E & 4F Implementation

This file contains the implementation for:
- 4E: Comprehensive Visualization Suite
- 4F: Profitability Analysis Summary & Strategic Insights (with enhanced presentation)

Replace the stub functions in section_04.py with these implementations.
"""


# =============================================================================
# SUBSECTION 4E: COMPREHENSIVE VISUALIZATION SUITE
# =============================================================================

def _build_section_4e_visualization_suite(df: pd.DataFrame, companies: Dict[str, str],
                                         institutional_df: pd.DataFrame) -> str:
    """Build Section 4E: Comprehensive Visualization Suite"""
    
    if df.empty:
        return ""
    
    # Get all previously calculated analyses
    dupont_analysis = _calculate_dupont_analysis(df, companies, institutional_df)
    profitability_trends = _calculate_profitability_trends(df, companies)
    efficiency_analysis = _calculate_operational_efficiency(df, companies)
    return_analysis = _calculate_multidimensional_returns(df, companies, pd.DataFrame(), institutional_df)
    
    try:
        economic_df = pd.DataFrame()  # Placeholder
        eva_analysis = _calculate_economic_value_added(df, companies, economic_df)
    except:
        eva_analysis = {}
    
    # Build comprehensive dashboard charts
    dashboard_charts_html = _build_comprehensive_dashboard(
        dupont_analysis, profitability_trends, efficiency_analysis, 
        return_analysis, eva_analysis, df, companies
    )
    
    content = f"""
    <div class="collapsible-section">
        <div class="collapsible-header">
            <h3>4E. Comprehensive Visualization Suite</h3>
            <span class="collapsible-toggle">▼</span>
        </div>
        <div class="collapsible-content">
            <div class="info-box info">
                <p>
                    This comprehensive visualization suite synthesizes insights from all profitability dimensions:
                    DuPont decomposition, operational efficiency, multi-dimensional returns, and EVA analysis.
                    The integrated dashboard provides a holistic view of portfolio performance.
                </p>
            </div>
            
            {dashboard_charts_html}
        </div>
    </div>
    """
    
    return content


def _build_comprehensive_dashboard(dupont_analysis: Dict, profitability_trends: Dict,
                                   efficiency_analysis: Dict, return_analysis: Dict,
                                   eva_analysis: Dict, df: pd.DataFrame, 
                                   companies: Dict[str, str]) -> str:
    """Build comprehensive performance dashboard with integrated visualizations"""
    
    companies_list = list(companies.keys())
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    charts_html = '<h4 style="margin-top: 40px;">Integrated Performance Dashboard</h4>'
    
    # Chart 1: Portfolio Performance Radar Chart
    if dupont_analysis and return_analysis and efficiency_analysis:
        # Select top 4 companies for readability
        top_companies = list(companies_list)[:min(4, len(companies_list))]
        
        metrics = ['ROE', 'Efficiency', 'Quality', 'Margin']
        
        radar_traces = []
        for i, company in enumerate(top_companies):
            if company in dupont_analysis and company in return_analysis and company in efficiency_analysis:
                values = [
                    dupont_analysis[company]['calculated_roe'] / 20 * 10,  # Normalize to 0-10
                    efficiency_analysis[company]['efficiency_score'],
                    return_analysis[company]['return_quality'],
                    dupont_analysis[company].get('margin_efficiency', 5)
                ]
                
                # Close the radar by repeating first value
                values_closed = values + [values[0]]
                metrics_closed = metrics + [metrics[0]]
                
                radar_traces.append({
                    'type': 'scatterpolar',
                    'r': values_closed,
                    'theta': metrics_closed,
                    'fill': 'toself',
                    'name': company,
                    'line': {'color': colors[i % len(colors)]},
                    'marker': {'size': 8}
                })
        
        fig1_data = {
            'data': radar_traces,
            'layout': {
                'polar': {
                    'radialaxis': {
                        'visible': True,
                        'range': [0, 10]
                    }
                },
                'title': {'text': 'Portfolio Performance Profile Comparison', 'font': {'size': 18, 'weight': 'bold'}},
                'showlegend': True
            }
        }
        
        charts_html += build_plotly_chart(fig1_data, div_id="portfolio-radar-chart", height=500)
    
    # Chart 2: Profitability Components Stacked Analysis
    if dupont_analysis:
        net_margins = [dupont_analysis[c]['net_margin'] for c in companies_list if c in dupont_analysis]
        asset_turnovers = [dupont_analysis[c]['asset_turnover'] for c in companies_list if c in dupont_analysis]
        display_companies = [c for c in companies_list if c in dupont_analysis]
        
        # Normalize for stacking visualization
        max_margin = max(net_margins) if net_margins else 1
        max_turnover = max(asset_turnovers) if asset_turnovers else 1
        
        norm_margins = [m / max_margin * 10 for m in net_margins]
        norm_turnovers = [t / max_turnover * 10 for t in asset_turnovers]
        
        fig2_data = {
            'data': [
                {
                    'type': 'bar',
                    'x': display_companies,
                    'y': norm_margins,
                    'name': 'Net Margin (Normalized)',
                    'marker': {'color': 'lightblue'},
                    'hovertemplate': '<b>%{x}</b><br>Net Margin Score: %{y:.1f}/10<extra></extra>'
                },
                {
                    'type': 'bar',
                    'x': display_companies,
                    'y': norm_turnovers,
                    'name': 'Asset Turnover (Normalized)',
                    'marker': {'color': 'lightgreen'},
                    'hovertemplate': '<b>%{x}</b><br>Turnover Score: %{y:.1f}/10<extra></extra>'
                }
            ],
            'layout': {
                'title': {'text': 'Profitability Component Breakdown', 'font': {'size': 18, 'weight': 'bold'}},
                'xaxis': {'title': 'Companies'},
                'yaxis': {'title': 'Normalized Component Score (0-10)'},
                'barmode': 'stack',
                'showlegend': True
            }
        }
        
        charts_html += build_plotly_chart(fig2_data, div_id="profitability-components-chart", height=450)
    
    # Chart 3: Risk-Return Efficiency Matrix
    if return_analysis and eva_analysis:
        return_quality = [return_analysis[c]['return_quality'] for c in companies_list if c in return_analysis and c in eva_analysis]
        eva_scores = [eva_analysis[c]['eva'] / 1000000 for c in companies_list if c in return_analysis and c in eva_analysis]
        matrix_companies = [c for c in companies_list if c in return_analysis and c in eva_analysis]
        
        scatter_colors = ['green' if eva > 0 else 'red' for eva in eva_scores]
        
        fig3_data = {
            'data': [{
                'type': 'scatter',
                'mode': 'markers+text',
                'x': return_quality,
                'y': [abs(eva) for eva in eva_scores],
                'text': matrix_companies,
                'textposition': 'top center',
                'marker': {
                    'size': 15,
                    'color': scatter_colors,
                    'line': {'color': 'black', 'width': 1}
                },
                'hovertemplate': '<b>%{text}</b><br>Return Quality: %{x:.1f}/10<br>|EVA|: $%{y:.0f}M<extra></extra>'
            }],
            'layout': {
                'title': {'text': 'Risk-Value Creation Matrix', 'font': {'size': 18, 'weight': 'bold'}},
                'xaxis': {'title': 'Return Quality (0-10)', 'range': [0, 11]},
                'yaxis': {'title': '|EVA| ($M)'},
                'showlegend': False,
                'annotations': [
                    {
                        'x': 2,
                        'y': max([abs(e) for e in eva_scores]) * 0.9 if eva_scores else 10,
                        'text': 'Low Quality<br>Value Destroyers',
                        'showarrow': False,
                        'font': {'color': 'red', 'size': 10}
                    },
                    {
                        'x': 8,
                        'y': max([abs(e) for e in eva_scores]) * 0.9 if eva_scores else 10,
                        'text': 'High Quality<br>Value Creators',
                        'showarrow': False,
                        'font': {'color': 'green', 'size': 10}
                    }
                ]
            }
        }
        
        charts_html += build_plotly_chart(fig3_data, div_id="risk-value-matrix-chart", height=450)
    
    # Chart 4: Portfolio Score Summary (Multi-metric Bar)
    if dupont_analysis and return_analysis and eva_analysis:
        avg_roe = np.mean([dupont_analysis[c]['calculated_roe'] for c in dupont_analysis.keys()])
        avg_quality = np.mean([return_analysis[c]['return_quality'] for c in return_analysis.keys()])
        total_eva = sum([eva_analysis[c]['eva'] for c in eva_analysis.keys()]) / 1000000
        avg_efficiency = np.mean([efficiency_analysis[c]['efficiency_score'] for c in efficiency_analysis.keys()]) if efficiency_analysis else 0
        
        portfolio_scores = [
            avg_roe / 2,  # Normalize to 0-10
            avg_quality,
            (total_eva + 100) / 20 if total_eva > -100 else 0,  # Normalize
            avg_efficiency
        ]
        score_labels = ['ROE<br>Performance', 'Return<br>Quality', 'Value<br>Creation', 'Operational<br>Efficiency']
        score_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        fig4_data = {
            'data': [{
                'type': 'bar',
                'x': score_labels,
                'y': portfolio_scores,
                'marker': {'color': score_colors},
                'text': [f"{val:.1f}" for val in portfolio_scores],
                'textposition': 'outside',
                'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}/10<extra></extra>'
            }],
            'layout': {
                'title': {'text': 'Portfolio Aggregate Metrics', 'font': {'size': 18, 'weight': 'bold'}},
                'xaxis': {'title': ''},
                'yaxis': {'title': 'Portfolio Score', 'range': [0, 12]},
                'showlegend': False
            }
        }
        
        charts_html += build_plotly_chart(fig4_data, div_id="portfolio-scores-chart", height=450)
    
    # Chart 5: Time Series ROE Trends (if historical data available)
    roe_history_html = _build_roe_trends_consolidated(df, companies)
    charts_html += roe_history_html
    
    return charts_html


def _build_roe_trends_consolidated(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build consolidated ROE trends over time for all companies"""
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#ff7675']
    
    traces = []
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) >= 2:
            years = company_data['Year'].tolist()
            roe_values = company_data['returnOnEquity'].tolist()
            
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': years,
                'y': roe_values,
                'name': company_name,
                'line': {'color': colors[i % len(colors)], 'width': 3},
                'marker': {'size': 8},
                'hovertemplate': '<b>' + company_name + '</b><br>Year: %{x}<br>ROE: %{y:.2f}%<extra></extra>'
            })
    
    if not traces:
        return ""
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Historical ROE Trends - Portfolio View', 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': 'Year'},
            'yaxis': {'title': 'Return on Equity (%)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'x': 1.05, 'y': 1.0}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roe-trends-consolidated", height=500)


# =============================================================================
# SUBSECTION 4F: STRATEGIC INSIGHTS WITH ENHANCED PRESENTATION
# =============================================================================

def _build_section_4f_strategic_insights(df: pd.DataFrame, companies: Dict[str, str],
                                        institutional_df: pd.DataFrame,
                                        insider_df: pd.DataFrame) -> str:
    """Build Section 4F: Profitability Analysis Summary & Strategic Insights"""
    
    if df.empty:
        return ""
    
    # Get all analyses
    dupont_analysis = _calculate_dupont_analysis(df, companies, institutional_df)
    profitability_trends = _calculate_profitability_trends(df, companies)
    efficiency_analysis = _calculate_operational_efficiency(df, companies)
    return_analysis = _calculate_multidimensional_returns(df, companies, pd.DataFrame(), institutional_df)
    
    try:
        economic_df = pd.DataFrame()
        eva_analysis = _calculate_economic_value_added(df, companies, economic_df)
    except:
        eva_analysis = {}
    
    # Generate insights with enhanced presentation
    insights_html = _build_enhanced_strategic_insights(
        dupont_analysis, profitability_trends, efficiency_analysis,
        return_analysis, eva_analysis, companies, institutional_df, insider_df
    )
    
    content = f"""
    <div class="collapsible-section">
        <div class="collapsible-header">
            <h3>4F. Profitability Analysis Summary & Strategic Insights</h3>
            <span class="collapsible-toggle">▼</span>
        </div>
        <div class="collapsible-content">
            {insights_html}
        </div>
    </div>
    """
    
    return content


def _build_enhanced_strategic_insights(dupont_analysis: Dict, profitability_trends: Dict,
                                       efficiency_analysis: Dict, return_analysis: Dict,
                                       eva_analysis: Dict, companies: Dict,
                                       institutional_df: pd.DataFrame,
                                       insider_df: pd.DataFrame) -> str:
    """Build strategic insights with enhanced visual presentation using cards and highlights"""
    
    total_companies = len(companies)
    
    # Calculate portfolio metrics
    if dupont_analysis:
        avg_calculated_roe = np.mean([m['calculated_roe'] for m in dupont_analysis.values()])
        high_quality_dupont = sum(1 for m in dupont_analysis.values() if m['dupont_quality'] in ['Excellent', 'Good'])
        avg_institutional_weight = np.mean([m['institutional_weight'] for m in dupont_analysis.values()])
    else:
        avg_calculated_roe = 10
        high_quality_dupont = 0
        avg_institutional_weight = 0.5
    
    if return_analysis:
        avg_return_quality = np.mean([m['return_quality'] for m in return_analysis.values()])
        superior_returns = sum(1 for m in return_analysis.values() if m['return_rating'] == 'Superior')
        consistent_performers = sum(1 for m in return_analysis.values() if m['return_consistency'] >= 7)
    else:
        avg_return_quality = 5
        superior_returns = 0
        consistent_performers = 0
    
    if eva_analysis:
        total_eva = sum(m['eva'] for m in eva_analysis.values())
        value_creators = sum(1 for m in eva_analysis.values() if m['eva'] > 0)
        excellent_creators = sum(1 for m in eva_analysis.values() if m['value_creation'] == 'Excellent')
        avg_roic_wacc_spread = np.mean([m['roic_wacc_spread'] for m in eva_analysis.values()])
    else:
        total_eva = 0
        value_creators = 0
        excellent_creators = 0
        avg_roic_wacc_spread = 0
    
    if efficiency_analysis:
        avg_efficiency_score = np.mean([m['efficiency_score'] for m in efficiency_analysis.values()])
        high_efficiency_companies = sum(1 for m in efficiency_analysis.values() if m['efficiency_score'] >= 7)
        improving_efficiency = sum(1 for m in efficiency_analysis.values() if m['efficiency_trend'] == 'Improving')
    else:
        avg_efficiency_score = 5
        high_efficiency_companies = 0
        improving_efficiency = 0
    
    # Build the enhanced presentation
    html = '<div style="margin: 20px 0;">'
    
    # Executive Summary Cards
    html += '<h3 style="margin-bottom: 20px; color: var(--text-primary);">📊 Executive Summary</h3>'
    
    summary_cards = [
        {
            "label": "Portfolio ROE",
            "value": f"{avg_calculated_roe:.1f}%",
            "description": f"{'Strong' if avg_calculated_roe > 15 else 'Solid' if avg_calculated_roe > 10 else 'Moderate'} profitability",
            "type": "success" if avg_calculated_roe > 12 else "info"
        },
        {
            "label": "Return Quality",
            "value": f"{avg_return_quality:.1f}/10",
            "description": f"{superior_returns}/{total_companies} superior performers",
            "type": "success" if avg_return_quality >= 7 else "info"
        },
        {
            "label": "Total EVA",
            "value": f"${total_eva/1000000:.0f}M",
            "description": f"{'Value creation' if total_eva > 0 else 'Value destruction'}",
            "type": "success" if total_eva > 0 else "warning"
        },
        {
            "label": "Efficiency Score",
            "value": f"{avg_efficiency_score:.1f}/10",
            "description": f"{high_efficiency_companies}/{total_companies} high efficiency",
            "type": "success" if avg_efficiency_score >= 7 else "info"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    # Section 1: Profitability Foundation
    html += build_section_divider()
    html += '<h3 style="margin: 30px 0 20px 0; color: var(--text-primary);">💎 Profitability Foundation</h3>'
    
    profitability_metrics = [
        {"label": "DuPont Quality", "value": f"{high_quality_dupont}/{total_companies}"},
        {"label": "Institutional Confidence", "value": f"{avg_institutional_weight*100:.0f}%"},
        {"label": "Consistent Performers", "value": f"{consistent_performers}/{total_companies}"}
    ]
    
    foundation_card = build_summary_card(
        "Foundation Strength Assessment",
        profitability_metrics,
        "success" if high_quality_dupont >= total_companies * 0.6 else "info"
    )
    html += foundation_card
    
    # Key insights
    html += f"""
    <div class="info-box info" style="margin: 20px 0;">
        <h4>🎯 Key Insights</h4>
        <ul style="margin: 10px 0; line-height: 1.8;">
            <li><strong>Profitability Quality:</strong> {high_quality_dupont}/{total_companies} companies demonstrate high-quality DuPont profiles with strong institutional validation</li>
            <li><strong>Performance Sustainability:</strong> {'Strong' if high_quality_dupont >= total_companies * 0.6 and superior_returns >= total_companies * 0.4 else 'Moderate'} foundation with {avg_institutional_weight*100:.0f}% institutional backing</li>
            <li><strong>Strategic Position:</strong> Portfolio positioned for {'sustained excellence' if avg_calculated_roe > 15 and avg_return_quality >= 7 else 'continued growth' if avg_calculated_roe > 10 else 'performance improvement'}</li>
        </ul>
    </div>
    """
    
    # Section 2: Return Excellence
    html += build_section_divider()
    html += '<h3 style="margin: 30px 0 20px 0; color: var(--text-primary);">🏆 Return Excellence</h3>'
    
    return_metrics = [
        {"label": "Superior Performers", "value": f"{superior_returns}/{total_companies}"},
        {"label": "Avg Return Quality", "value": f"{avg_return_quality:.1f}/10"},
        {"label": "Consistency Leaders", "value": f"{consistent_performers}/{total_companies}"}
    ]
    
    return_card = build_summary_card(
        "Multi-Dimensional Return Profile",
        return_metrics,
        "success" if superior_returns >= total_companies * 0.4 else "info"
    )
    html += return_card
    
    html += f"""
    <div class="info-box {'success' if avg_return_quality >= 7 else 'info'}" style="margin: 20px 0;">
        <h4>📈 Return Dynamics</h4>
        <ul style="margin: 10px 0; line-height: 1.8;">
            <li><strong>Performance Distribution:</strong> {superior_returns}/{total_companies} companies achieve superior ratings with {avg_return_quality:.1f}/10 portfolio quality</li>
            <li><strong>Risk-Adjusted Returns:</strong> {'Strong' if avg_return_quality >= 7 else 'Moderate'} risk-adjusted performance across multiple dimensions</li>
            <li><strong>Momentum:</strong> {'Positive trajectory' if superior_returns >= total_companies * 0.4 else 'Mixed signals'} with {consistent_performers} companies showing high consistency</li>
        </ul>
    </div>
    """
    
    # Section 3: Value Creation
    html += build_section_divider()
    html += '<h3 style="margin: 30px 0 20px 0; color: var(--text-primary);">💰 Economic Value Creation</h3>'
    
    value_metrics = [
        {"label": "Total EVA", "value": f"${total_eva/1000000:.0f}M"},
        {"label": "Value Creators", "value": f"{value_creators}/{total_companies}"},
        {"label": "ROIC-WACC Spread", "value": f"{avg_roic_wacc_spread:.1f}pp"}
    ]
    
    value_card = build_summary_card(
        "Capital Allocation Effectiveness",
        value_metrics,
        "success" if total_eva > 0 and value_creators >= total_companies * 0.5 else "warning"
    )
    html += value_card
    
    html += f"""
    <div class="info-box {'success' if total_eva > 0 else 'warning'}" style="margin: 20px 0;">
        <h4>💡 Value Creation Insights</h4>
        <ul style="margin: 10px 0; line-height: 1.8;">
            <li><strong>Economic Profit:</strong> ${total_eva/1000000:.0f}M portfolio EVA with {value_creators}/{total_companies} companies generating positive value</li>
            <li><strong>Capital Efficiency:</strong> {avg_roic_wacc_spread:.1f}pp average spread indicates {'strong' if avg_roic_wacc_spread > 3 else 'adequate' if avg_roic_wacc_spread > 0 else 'challenged'} returns above cost of capital</li>
            <li><strong>Excellence:</strong> {excellent_creators}/{total_companies} companies achieve excellent value creation ratings</li>
        </ul>
    </div>
    """
    
    # Section 4: Operational Excellence
    html += build_section_divider()
    html += '<h3 style="margin: 30px 0 20px 0; color: var(--text-primary);">⚙️ Operational Excellence</h3>'
    
    efficiency_metrics = [
        {"label": "Portfolio Efficiency", "value": f"{avg_efficiency_score:.1f}/10"},
        {"label": "High Performers", "value": f"{high_efficiency_companies}/{total_companies}"},
        {"label": "Improving Trends", "value": f"{improving_efficiency}/{total_companies}"}
    ]
    
    efficiency_card = build_summary_card(
        "Operational Performance Overview",
        efficiency_metrics,
        "success" if avg_efficiency_score >= 7 else "info"
    )
    html += efficiency_card
    
    html += f"""
    <div class="info-box {'success' if avg_efficiency_score >= 7 else 'info'}" style="margin: 20px 0;">
        <h4>🔧 Efficiency Dynamics</h4>
        <ul style="margin: 10px 0; line-height: 1.8;">
            <li><strong>Operational Quality:</strong> {avg_efficiency_score:.1f}/10 portfolio score with {high_efficiency_companies}/{total_companies} companies achieving excellence</li>
            <li><strong>Asset Utilization:</strong> {'Optimized' if high_efficiency_companies >= total_companies * 0.6 else 'Standard'} asset turnover and working capital management</li>
            <li><strong>Trajectory:</strong> {improving_efficiency}/{total_companies} companies showing improving efficiency trends</li>
        </ul>
    </div>
    """
    
    # Section 5: Strategic Recommendations
    html += build_section_divider()
    html += '<h3 style="margin: 30px 0 20px 0; color: var(--text-primary);">🎯 Strategic Recommendations</h3>'
    
    # Immediate priorities
    html += """
    <div class="info-box warning" style="margin: 20px 0;">
        <h4>🚀 Immediate Priorities (0-6 months)</h4>
        <ul style="margin: 10px 0; line-height: 1.8;">
    """
    
    if superior_returns >= total_companies * 0.3 and excellent_creators >= total_companies * 0.3:
        html += "<li><strong>Portfolio Optimization:</strong> Increase allocation to superior performers and excellent value creators</li>"
    else:
        html += "<li><strong>Performance Enhancement:</strong> Focus capital on return quality improvement initiatives</li>"
    
    if avg_institutional_weight > 0.6:
        html += "<li><strong>Institutional Relations:</strong> Maintain and expand institutional relationships for stability</li>"
    else:
        html += "<li><strong>Investor Engagement:</strong> Enhance institutional engagement and transparency</li>"
    
    if avg_efficiency_score >= 7:
        html += "<li><strong>Best Practice Scaling:</strong> Scale operational excellence across portfolio</li>"
    else:
        html += "<li><strong>Efficiency Programs:</strong> Implement targeted operational improvement initiatives</li>"
    
    html += """
        </ul>
    </div>
    """
    
    # Medium-term strategy
    html += """
    <div class="info-box info" style="margin: 20px 0;">
        <h4>📅 Medium-Term Strategy (6-18 months)</h4>
        <ul style="margin: 10px 0; line-height: 1.8;">
    """
    
    if superior_returns >= total_companies * 0.4 and consistent_performers >= total_companies * 0.5:
        html += "<li><strong>Excellence Sustainment:</strong> Maintain superior performance while enhancing consistency</li>"
    else:
        html += "<li><strong>Quality Enhancement:</strong> Develop comprehensive return quality improvement framework</li>"
    
    if excellent_creators >= total_companies * 0.4:
        html += "<li><strong>Value Expansion:</strong> Scale excellent value creators through strategic capital reallocation</li>"
    else:
        html += "<li><strong>Capability Development:</strong> Build value creation capabilities and ROIC improvement programs</li>"
    
    html += """
        </ul>
    </div>
    """
    
    # Performance targets
    target_metrics = [
        {"label": "Target Return Quality", "value": f"{min(10, avg_return_quality + 1.5):.1f}/10"},
        {"label": "Target EVA Growth", "value": f"+{max(0, total_eva/1000000 * 0.5):.0f}M"},
        {"label": "Target Superior Performers", "value": f"{min(total_companies, superior_returns + max(1, (total_companies - superior_returns) // 2))}/{total_companies}"}
    ]
    
    target_card = build_summary_card(
        "24-Month Performance Targets",
        target_metrics,
        "info"
    )
    html += target_card
    
    html += '</div>'
    
    return html
