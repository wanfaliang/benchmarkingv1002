"""Section 3: Financial Overview & Historical Analysis"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_data_table,
    build_info_box,
    build_section_divider,
    build_plotly_chart,
    format_currency,
    format_percentage,
    format_number
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 3: Financial Overview & Historical Analysis
    
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
        
        # Get prices and enterprise values (optional)
        try:
            prices_df = collector.get_prices_daily()
        except:
            prices_df = pd.DataFrame()
        
        try:
            enterprise_values_df = collector.get_enterprise_values()
        except:
            enterprise_values_df = pd.DataFrame()
        
        # Generate comprehensive financial history
        financial_history = _generate_comprehensive_financial_history(df, companies, collector.years)
        
        # Calculate advanced growth metrics
        growth_metrics = _calculate_advanced_growth_metrics(df, companies)
        
        # Build all subsections
        section_3a_html = _build_section_3a_financial_history(
            financial_history, growth_metrics, companies, df
        )
        
        # Stub remaining sections (will be implemented in later phases)
        section_3b_html = _build_section_3b_visualization_suite(df,companies,financial_history,growth_metrics)
        section_3c_html = _build_section_3c_working_capital(df,companies)
        section_3d_html = _build_section_3d_capital_allocation(df,companies)
        section_3e_html = _build_section_3e_financial_quality(df,companies,financial_history)
        section_3f_html = _build_section_3f_summary_insights(df,companies,financial_history,growth_metrics)
        
        # Combine all subsections
        content = f'''
        <div class="section-content-wrapper">
            <!-- Section Header with Key Stats -->
            <div class="info-section">
                <h3>Financial Overview Summary</h3>
                {_build_overview_stats(df, companies)}
            </div>
            
            {build_section_divider()}
            
            <!-- 3A: Core Financial History (Collapsible) -->
            {_make_subsection_collapsible("3a", "3A. Core Financial History & Growth Analysis", section_3a_html, default_open=True)}
            
            <!-- 3B: Comprehensive Visualization Suite (Collapsible) -->
            {_make_subsection_collapsible("3b", "3B. Comprehensive Financial Visualization Suite", section_3b_html, default_open=True)}
            
            <!-- 3C: Working Capital Management (Collapsible) -->
            {_make_subsection_collapsible("3c", "3C. Working Capital Management & Operational Efficiency", section_3c_html, default_open=True)}
            
            <!-- 3D: Capital Allocation & Return Analysis (Collapsible) -->
            {_make_subsection_collapsible("3d", "3D. Capital Allocation & Return Analysis", section_3d_html, default_open=True)}
            
            <!-- 3E: Financial Quality & Earnings Analysis (Collapsible) -->
            {_make_subsection_collapsible("3e", "3E. Financial Quality & Earnings Analysis", section_3e_html, default_open=True)}
            
            <!-- 3F: Financial Overview Summary & Strategic Insights (Collapsible) -->
            {_make_subsection_collapsible("3f", "3F. Financial Overview Summary & Strategic Insights", section_3f_html, default_open=True)}
        </div>
        '''
        
        return generate_section_wrapper(3, "Financial Overview & Historical Analysis", content)
        
    except Exception as e:
        error_content = f"""
        <div class="info-box danger">
            <h4>Error Generating Section 3</h4>
            <p>An error occurred while generating the financial overview: {str(e)}</p>
        </div>
        """
        return generate_section_wrapper(3, "Financial Overview & Historical Analysis", error_content)

def _make_subsection_collapsible(subsection_id: str, title: str, content: str, default_open: bool = True) -> str:
    """
    Make a subsection collapsible/expandable
    
    Args:
        subsection_id: Unique ID for the subsection (e.g., "3a", "3b", "3c")
        title: Display title (e.g., "3A. Core Financial History")
        content: HTML content to be made collapsible
        default_open: Whether section is open by default
    
    Returns:
        HTML string with collapsible wrapper
    """
    
    display_style = "block" if default_open else "none"
    button_icon = "▼" if default_open else "▶"
    
    return f"""
    <div style="margin: 30px 0;">
        <div class="subsection-header" 
             style="display: flex; align-items: center; justify-content: space-between; 
                    background: linear-gradient(135deg, #667eea, #764ba2); 
                    padding: 15px 25px; border-radius: 12px; cursor: pointer;
                    box-shadow: var(--shadow-md); transition: all 0.3s ease;"
             onclick="toggleSubsection('subsection_{subsection_id}')"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-lg)';"
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='var(--shadow-md)';">
            <h3 style="margin: 0; color: white; font-size: 1.4rem; font-weight: 700;">{title}</h3>
            <span id="subsection_{subsection_id}_toggle" 
                  style="color: white; font-size: 1.5rem; font-weight: bold; 
                         transition: transform 0.3s ease; min-width: 30px; text-align: center;">
                {button_icon}
            </span>
        </div>
        <div id="subsection_{subsection_id}_content" 
             style="display: {display_style}; margin-top: 0; overflow: hidden;
                    transition: all 0.3s ease;">
            {content}
        </div>
    </div>
    
    <script>
        function toggleSubsection(subsectionId) {{
            const content = document.getElementById(subsectionId + '_content');
            const toggle = document.getElementById(subsectionId + '_toggle');
            
            if (content.style.display === 'none' || content.style.display === '') {{
                content.style.display = 'block';
                toggle.textContent = '▼';
                // Smooth expand animation
                content.style.animation = 'slideDown 0.3s ease';
            }} else {{
                content.style.display = 'none';
                toggle.textContent = '▶';
            }}
        }}
    </script>
    
    <style>
        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>
    """
# =============================================================================
# OVERVIEW STATS
# =============================================================================

def _build_overview_stats(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build overview statistics cards"""
    
    total_companies = len(companies)
    
    # Calculate portfolio-level metrics
    latest_data = df.groupby('Company', group_keys=False).apply(
        lambda x: x.sort_values('Year').iloc[-1], 
        include_groups=False
    )
    
    total_revenue = latest_data['revenue'].sum() if 'revenue' in latest_data.columns else 0
    avg_revenue_growth = latest_data['revenue_YoY'].mean() if 'revenue_YoY' in latest_data.columns else 0
    avg_net_margin = latest_data['netProfitMargin'].mean() * 100 if 'netProfitMargin' in latest_data.columns else 0
    total_fcf = latest_data['freeCashFlow'].sum() if 'freeCashFlow' in latest_data.columns else 0
    
    # Build stat cards
    cards = [
        {
            "label": "Total Companies",
            "value": str(total_companies),
            "description": "Portfolio Coverage",
            "type": "info"
        },
        {
            "label": "Combined Revenue",
            "value": format_currency(total_revenue, millions=True),
            "description": "Latest Fiscal Year",
            "type": "default"
        },
        {
            "label": "Avg Revenue Growth",
            "value": format_percentage(avg_revenue_growth / 100, decimals=1, include_sign=True),
            "description": "Year-over-Year",
            "type": "success" if avg_revenue_growth > 5 else "warning"
        },
        {
            "label": "Avg Net Margin",
            "value": f"{avg_net_margin:.1f}%",
            "description": "Profitability Indicator",
            "type": "success" if avg_net_margin > 15 else "info"
        },
        {
            "label": "Combined Free Cash Flow",
            "value": format_currency(total_fcf, millions=True),
            "description": "Latest Fiscal Year",
            "type": "success" if total_fcf > 0 else "danger"
        }
    ]
    
    return build_stat_grid(cards)


# =============================================================================
# SUBSECTION 3A: CORE FINANCIAL HISTORY & GROWTH ANALYSIS
# =============================================================================

def _build_section_3a_financial_history(
    financial_history: Dict[str, pd.DataFrame],
    growth_metrics: Dict[str, Dict],
    companies: Dict[str, str],
    df: pd.DataFrame
) -> str:
    """Build subsection 3A: Core Financial History"""
    
    html = '<div class="info-section">'
    html += '<h3>3A. Core Financial History & Growth Analysis</h3>'
    
    # 3A.1: Financial History Tables (per company)
    html += '<h4>Multi-Year Financial Performance</h4>'
    
    for company_name, history_df in financial_history.items():
        if history_df.empty:
            continue
        
        html += f'<h5 style="margin-top: 30px;">{company_name} - Financial History</h5>'
        
        # Prepare display DataFrame
        display_df = _prepare_financial_history_display(history_df)
        
        # Build table
        html += build_data_table(
            display_df,
            table_id=f"financial_history_{company_name.replace(' ', '_')}",
            sortable=True,
            page_length=10
        )
    
    # Financial trend analysis
    trend_analysis = _analyze_financial_trends(financial_history, companies)
    html += build_info_box(
        f"<p>{trend_analysis}</p>",
        box_type="info",
        title="Financial Trend Analysis"
    )
    
    html += '<h4 style="margin-top: 40px;">Growth Quality & Sustainability Analysis</h4>'
    
    # 3A.2: Growth Metrics Table
    if growth_metrics:
        growth_df = _prepare_growth_metrics_display(growth_metrics)
        html += build_data_table(
            growth_df,
            table_id="growth_quality_metrics",
            sortable=True,
            page_length=-1
        )
        
        # Growth analysis summary
        growth_summary = _generate_growth_analysis_summary(growth_metrics)
        html += build_info_box(
            f"<p>{growth_summary}</p>",
            box_type="success",
            title="Growth Quality Assessment"
        )
    else:
        html += build_info_box(
            "<p>Insufficient data for advanced growth metrics analysis.</p>",
            box_type="warning"
        )
    
    html += '</div>'
    
    return html


# =============================================================================
# SUBSECTION BUILDERS (To be implemented in later phases)
# =============================================================================

"""
Section 3B: Comprehensive Financial Visualization Suite
Complete implementation with all 24 charts

INSTRUCTIONS:
1. Copy this entire code
2. In your section_03.py, find the function: _build_section_3b_visualization_suite()
3. Replace that stub function with the implementation below
4. Copy all the helper functions to the bottom of your section_03.py file
"""


def _build_section_3b_visualization_suite(
    df: pd.DataFrame,
    companies: Dict[str, str],
    financial_history: Dict[str, pd.DataFrame],
    growth_metrics: Dict[str, Dict]
) -> str:
    """Build Section 3B: Comprehensive Financial Visualization Suite (24 Charts)"""
    
    html = '<div class="info-section">'
    html += '<h3>3B. Comprehensive Financial Visualization Suite</h3>'
    
    # Chart Set 1: Revenue Growth Analysis (4 charts)
    html += '<h4 style="margin-top: 30px;">Revenue Growth Analysis</h4>'
    html += _build_revenue_growth_charts(df, companies, financial_history, growth_metrics)
    
    # Chart Set 2: Profitability & Margin Evolution (4 charts)
    html += '<h4 style="margin-top: 40px;">Profitability & Margin Evolution</h4>'
    html += _build_profitability_charts(df, companies, financial_history)
    
    # Chart Set 3: Cash Flow Engine Analysis (4 charts)
    html += '<h4 style="margin-top: 40px;">Cash Flow Engine Analysis</h4>'
    html += _build_cash_flow_charts(df, companies, financial_history)
    
    # Chart Set 4: Balance Sheet Evolution (4 charts)
    html += '<h4 style="margin-top: 40px;">Balance Sheet Evolution</h4>'
    html += _build_balance_sheet_charts(df, companies, financial_history)
    
    # Chart Set 5: Advanced Financial Metrics (4 charts)
    html += '<h4 style="margin-top: 40px;">Advanced Financial Metrics</h4>'
    html += _build_advanced_metrics_charts(df, companies, financial_history)
    
    # Chart Set 6: Cross-Company Comparative Analysis (4 charts)
    html += '<h4 style="margin-top: 40px;">Cross-Company Comparative Analysis</h4>'
    html += _build_comparative_charts(df, companies, financial_history)
    
    html += '</div>'
    
    return html


# =============================================================================
# CHART SET 1: REVENUE GROWTH ANALYSIS (4 CHARTS)
# =============================================================================

def _build_revenue_growth_charts(
    df: pd.DataFrame,
    companies: Dict[str, str],
    financial_history: Dict[str, pd.DataFrame],
    growth_metrics: Dict[str, Dict]
) -> str:
    """Build 4 revenue growth analysis charts"""
    
    html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
    
    # Chart 1: Revenue Trends Over Time
    html += _create_revenue_trends_chart(df, companies, colors)
    
    # Chart 2: Revenue Growth Rates YoY
    html += _create_revenue_growth_rates_chart(df, companies, colors)
    
    # Chart 3: Growth Quality Scatter
    if growth_metrics:
        html += _create_growth_quality_scatter(growth_metrics, colors)
    
    # Chart 4: Growth Quality Scores
    if growth_metrics:
        html += _create_growth_quality_scores_chart(growth_metrics, colors)
    
    return html


def _create_revenue_trends_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 1: Revenue trends over time"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2 or 'revenue' not in company_data.columns:
            continue
        
        years = company_data['Year'].tolist()
        revenue = (company_data['revenue'] / 1_000_000).tolist()
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': company_name,
            'x': years,
            'y': revenue,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>Revenue: $%{{y:.1f}}M<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Revenue Trends Over Time', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Revenue ($M)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="revenue_trends_chart", height=500)


def _create_revenue_growth_rates_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 2: Revenue growth rates YoY"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2 or 'revenue' not in company_data.columns:
            continue
        
        years = company_data['Year'].iloc[1:].tolist()
        revenues = company_data['revenue'].values
        growth_rates = [((revenues[j] - revenues[j-1]) / revenues[j-1] * 100) for j in range(1, len(revenues))]
        
        traces.append({
            'type': 'bar',
            'name': company_name,
            'x': years,
            'y': growth_rates,
            'marker': {'color': colors[i % len(colors)]},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>Growth: %{{y:.1f}}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Revenue Growth Rates (Year-over-Year)', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Growth Rate (%)', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(0,0,0,0.3)', 'zerolinewidth': 2},
            'barmode': 'group',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="revenue_growth_rates_chart", height=500)


def _create_growth_quality_scatter(growth_metrics: Dict[str, Dict], colors: List[str]) -> str:
    """Chart 3: Growth quality scatter"""
    
    companies_list = list(growth_metrics.keys())
    growth_1y = [growth_metrics[c]['revenue_growth_1y'] for c in companies_list]
    growth_3y = [growth_metrics[c]['revenue_cagr_3y'] for c in companies_list]
    stability = [growth_metrics[c]['growth_stability'] for c in companies_list]
    bubble_sizes = [s * 5 for s in stability]
    
    traces = []
    for i, company in enumerate(companies_list):
        traces.append({
            'type': 'scatter',
            'mode': 'markers',
            'name': company,
            'x': [growth_1y[i]],
            'y': [growth_3y[i]],
            'marker': {'size': bubble_sizes[i], 'color': colors[i % len(colors)], 'line': {'color': 'white', 'width': 2}},
            'hovertemplate': f'<b>{company}</b><br>1Y Growth: %{{x:.1f}}%<br>3Y CAGR: %{{y:.1f}}%<br>Stability: {stability[i]:.1f}/10<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Growth Consistency Analysis<br><sub>Bubble Size = Growth Stability Score</sub>', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': '1-Year Revenue Growth (%)', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(239, 68, 68, 0.5)', 'zerolinewidth': 2},
            'yaxis': {'title': '3-Year CAGR (%)', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(239, 68, 68, 0.5)', 'zerolinewidth': 2},
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="growth_quality_scatter_chart", height=500)


def _create_growth_quality_scores_chart(growth_metrics: Dict[str, Dict], colors: List[str]) -> str:
    """Chart 4: Growth quality scores"""
    
    companies_list = list(growth_metrics.keys())
    quality_scores = [growth_metrics[c]['growth_quality_score'] for c in companies_list]
    
    bar_colors = []
    for score in quality_scores:
        if score >= 8:
            bar_colors.append('#10b981')
        elif score >= 6:
            bar_colors.append('#3b82f6')
        elif score >= 4:
            bar_colors.append('#f59e0b')
        else:
            bar_colors.append('#ef4444')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': quality_scores,
            'marker': {'color': bar_colors, 'line': {'color': 'white', 'width': 2}},
            'text': [f'{score:.1f}' for score in quality_scores],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Quality Score: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Growth Quality Assessment', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Quality Score (out of 10)', 'gridcolor': 'rgba(0,0,0,0.1)', 'range': [0, 11]},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies_list) - 0.5,
                'y0': 5,
                'y1': 5,
                'line': {'color': 'rgba(239, 68, 68, 0.5)', 'width': 2, 'dash': 'dash'}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="growth_quality_scores_chart", height=500)


# =============================================================================
# CHART SET 2: PROFITABILITY & MARGIN EVOLUTION (4 CHARTS)
# =============================================================================

def _build_profitability_charts(df: pd.DataFrame, companies: Dict[str, str], financial_history: Dict[str, pd.DataFrame]) -> str:
    """Build 4 profitability and margin analysis charts"""
    
    html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
    
    html += _create_net_margin_trends_chart(df, companies, colors)
    html += _create_margin_comparison_chart(df, companies)
    html += _create_roe_trends_chart(df, companies, colors)
    html += _create_profitability_matrix_chart(df, companies, colors)
    
    return html


def _create_net_margin_trends_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 5: Net profit margin trends"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2 or 'netProfitMargin' not in company_data.columns:
            continue
        
        years = company_data['Year'].tolist()
        net_margin = (company_data['netProfitMargin'] * 100).tolist()
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': company_name,
            'x': years,
            'y': net_margin,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>Net Margin: %{{y:.1f}}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Net Profit Margin Evolution', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Net Profit Margin (%)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="net_margin_trends_chart", height=500)


def _create_margin_comparison_chart(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Chart 6: Latest year margin comparison"""
    
    companies_list = list(companies.keys())
    latest_gross = []
    latest_operating = []
    latest_net = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            latest_gross.append(latest.get('grossProfitMargin', 0) * 100)
            latest_operating.append(latest.get('operatingProfitMargin', 0) * 100)
            latest_net.append(latest.get('netProfitMargin', 0) * 100)
        else:
            latest_gross.append(0)
            latest_operating.append(0)
            latest_net.append(0)
    
    fig_data = {
        'data': [
            {'type': 'bar', 'name': 'Gross Margin', 'x': companies_list, 'y': latest_gross, 'marker': {'color': '#60a5fa'}, 'hovertemplate': '<b>%{x}</b><br>Gross Margin: %{y:.1f}%<extra></extra>'},
            {'type': 'bar', 'name': 'Operating Margin', 'x': companies_list, 'y': latest_operating, 'marker': {'color': '#34d399'}, 'hovertemplate': '<b>%{x}</b><br>Operating Margin: %{y:.1f}%<extra></extra>'},
            {'type': 'bar', 'name': 'Net Margin', 'x': companies_list, 'y': latest_net, 'marker': {'color': '#f87171'}, 'hovertemplate': '<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'}
        ],
        'layout': {
            'title': {'text': 'Latest Year Margin Comparison', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Margin (%)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'barmode': 'group',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="margin_comparison_chart", height=500)


def _create_roe_trends_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 7: ROE trends"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        years = company_data['Year'].tolist()
        roe_values = []
        
        for _, row in company_data.iterrows():
            net_income = row.get('netIncome', 0)
            stockholders_equity = row.get('totalStockholdersEquity', 1)
            roe = (net_income / stockholders_equity) * 100 if stockholders_equity > 0 else 0
            roe_values.append(roe)
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': company_name,
            'x': years,
            'y': roe_values,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>ROE: %{{y:.1f}}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Return on Equity Trends', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Return on Equity (%)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roe_trends_chart", height=500)


def _create_profitability_matrix_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 8: Profitability efficiency scatter"""
    
    companies_list = list(companies.keys())
    latest_roe = []
    latest_roa = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            net_income = latest.get('netIncome', 0)
            total_assets = latest.get('totalAssets', 1)
            stockholders_equity = latest.get('totalStockholdersEquity', 1)
            
            roe = (net_income / stockholders_equity) * 100 if stockholders_equity > 0 else 0
            roa = (net_income / total_assets) * 100 if total_assets > 0 else 0
            
            latest_roe.append(roe)
            latest_roa.append(roa)
        else:
            latest_roe.append(0)
            latest_roa.append(0)
    
    traces = []
    for i, company in enumerate(companies_list):
        traces.append({
            'type': 'scatter',
            'mode': 'markers',
            'name': company,
            'x': [latest_roa[i]],
            'y': [latest_roe[i]],
            'marker': {'size': 20, 'color': colors[i % len(colors)], 'line': {'color': 'white', 'width': 2}},
            'hovertemplate': f'<b>{company}</b><br>ROA: %{{x:.1f}}%<br>ROE: %{{y:.1f}}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Profitability Efficiency Matrix', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Return on Assets (%)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Return on Equity (%)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="profitability_matrix_chart", height=500)


# =============================================================================
# CHART SET 3: CASH FLOW ENGINE ANALYSIS (4 CHARTS)
# =============================================================================

def _build_cash_flow_charts(df: pd.DataFrame, companies: Dict[str, str], financial_history: Dict[str, pd.DataFrame]) -> str:
    """Build 4 cash flow engine analysis charts"""
    
    html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
    
    html += _create_ocf_vs_netincome_chart(df, companies, colors)
    html += _create_fcf_trends_chart(df, companies, colors)
    html += _create_capex_chart(df, companies, colors)
    html += _create_cash_conversion_matrix_chart(df, companies, colors)
    
    return html


def _create_ocf_vs_netincome_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 9: OCF vs Net Income"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        years = company_data['Year'].tolist()
        ocf = (company_data['operatingCashFlow'] / 1_000_000).tolist()
        net_income = (company_data['netIncome'] / 1_000_000).tolist()
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': f'{company_name} OCF',
            'x': years,
            'y': ocf,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8, 'symbol': 'circle'},
            'hovertemplate': f'<b>{company_name} OCF</b><br>Year: %{{x}}<br>OCF: $%{{y:.1f}}M<extra></extra>'
        })
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': f'{company_name} Net Income',
            'x': years,
            'y': net_income,
            'line': {'color': colors[i % len(colors)], 'width': 3, 'dash': 'dash'},
            'marker': {'size': 8, 'symbol': 'square'},
            'hovertemplate': f'<b>{company_name} Net Income</b><br>Year: %{{x}}<br>Net Income: $%{{y:.1f}}M<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Operating Cash Flow vs Net Income', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Amount ($M)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'v', 'x': 1.02, 'y': 1}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ocf_vs_netincome_chart", height=500)


def _create_fcf_trends_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 10: Free cash flow trends"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2 or 'freeCashFlow' not in company_data.columns:
            continue
        
        years = company_data['Year'].tolist()
        fcf = (company_data['freeCashFlow'] / 1_000_000).tolist()
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': company_name,
            'x': years,
            'y': fcf,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>FCF: $%{{y:.1f}}M<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Free Cash Flow Trends', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Free Cash Flow ($M)', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(239, 68, 68, 0.5)', 'zerolinewidth': 2},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="fcf_trends_chart", height=500)


def _create_capex_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 11: Capital expenditure"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2 or 'capitalExpenditure' not in company_data.columns:
            continue
        
        years = company_data['Year'].tolist()
        capex = (company_data['capitalExpenditure'].abs() / 1_000_000).tolist()
        
        traces.append({
            'type': 'bar',
            'name': company_name,
            'x': years,
            'y': capex,
            'marker': {'color': colors[i % len(colors)]},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>CapEx: $%{{y:.1f}}M<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Capital Expenditure Trends', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Capital Expenditure ($M)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'barmode': 'group',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="capex_chart", height=500)


def _create_cash_conversion_matrix_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 12: Cash conversion quality matrix"""
    
    companies_list = list(companies.keys())
    ocf_ni_ratios = []
    fcf_margins = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            
            ocf = latest.get('operatingCashFlow', 0)
            net_income = latest.get('netIncome', 1)
            fcf = latest.get('freeCashFlow', 0)
            revenue = latest.get('revenue', 1)
            
            ocf_ni_ratio = ocf / net_income if net_income > 0 else 0
            fcf_margin = (fcf / revenue) * 100 if revenue > 0 else 0
            
            ocf_ni_ratios.append(ocf_ni_ratio)
            fcf_margins.append(fcf_margin)
        else:
            ocf_ni_ratios.append(0)
            fcf_margins.append(0)
    
    traces = []
    for i, company in enumerate(companies_list):
        traces.append({
            'type': 'scatter',
            'mode': 'markers',
            'name': company,
            'x': [ocf_ni_ratios[i]],
            'y': [fcf_margins[i]],
            'marker': {'size': 20, 'color': colors[i % len(colors)], 'line': {'color': 'white', 'width': 2}},
            'hovertemplate': f'<b>{company}</b><br>OCF/NI Ratio: %{{x:.2f}}<br>FCF Margin: %{{y:.1f}}%<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Cash Conversion Quality Matrix', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'OCF/Net Income Ratio', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(239, 68, 68, 0.5)', 'zerolinewidth': 2},
            'yaxis': {'title': 'FCF Margin (%)', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(239, 68, 68, 0.5)', 'zerolinewidth': 2},
            'shapes': [{'type': 'line', 'x0': 1, 'x1': 1, 'y0': -100, 'y1': 100, 'line': {'color': 'rgba(59, 130, 246, 0.3)', 'width': 2, 'dash': 'dash'}}],
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="cash_conversion_matrix_chart", height=500)


# =============================================================================
# CHART SET 4: BALANCE SHEET EVOLUTION (4 CHARTS)
# =============================================================================

def _build_balance_sheet_charts(df: pd.DataFrame, companies: Dict[str, str], financial_history: Dict[str, pd.DataFrame]) -> str:
    """Build 4 balance sheet evolution charts"""
    
    html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
    
    html += _create_assets_equity_chart(df, companies, colors)
    html += _create_debt_equity_trends_chart(df, companies, colors)
    html += _create_asset_composition_chart(df, companies)
    html += _create_leverage_matrix_chart(df, companies, colors)
    
    return html


def _create_assets_equity_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 13: Asset and equity growth"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        years = company_data['Year'].tolist()
        assets = (company_data['totalAssets'] / 1_000_000).tolist()
        equity = (company_data['totalStockholdersEquity'] / 1_000_000).tolist()
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': f'{company_name} Assets',
            'x': years,
            'y': assets,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8, 'symbol': 'circle'},
            'hovertemplate': f'<b>{company_name} Assets</b><br>Year: %{{x}}<br>Assets: $%{{y:.1f}}M<extra></extra>'
        })
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': f'{company_name} Equity',
            'x': years,
            'y': equity,
            'line': {'color': colors[i % len(colors)], 'width': 3, 'dash': 'dash'},
            'marker': {'size': 8, 'symbol': 'square'},
            'hovertemplate': f'<b>{company_name} Equity</b><br>Year: %{{x}}<br>Equity: $%{{y:.1f}}M<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Balance Sheet Growth: Assets & Equity', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Amount ($M)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'v', 'x': 1.02, 'y': 1}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="assets_equity_chart", height=500)


def _create_debt_equity_trends_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 14: Debt-to-equity trends"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        years = company_data['Year'].tolist()
        de_ratios = []
        
        for _, row in company_data.iterrows():
            total_debt = row.get('totalDebt', 0)
            equity = row.get('totalStockholdersEquity', 1)
            de_ratio = total_debt / equity if equity > 0 else 0
            de_ratios.append(de_ratio)
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': company_name,
            'x': years,
            'y': de_ratios,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>D/E Ratio: %{{y:.2f}}x<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Capital Structure: Leverage Trends', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Debt-to-Equity Ratio', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="debt_equity_trends_chart", height=500)


def _create_asset_composition_chart(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Chart 15: Asset composition (latest year)"""
    
    companies_list = list(companies.keys())
    current_assets = []
    fixed_assets = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            
            curr_assets = latest.get('totalCurrentAssets', 0) / 1_000_000
            total_assets = latest.get('totalAssets', 1) / 1_000_000
            fix_assets = max(0, total_assets - curr_assets)
            
            current_assets.append(curr_assets)
            fixed_assets.append(fix_assets)
        else:
            current_assets.append(0)
            fixed_assets.append(0)
    
    fig_data = {
        'data': [
            {'type': 'bar', 'name': 'Current Assets', 'x': companies_list, 'y': current_assets, 'marker': {'color': '#60a5fa'}, 'hovertemplate': '<b>%{x}</b><br>Current Assets: $%{y:.1f}M<extra></extra>'},
            {'type': 'bar', 'name': 'Fixed Assets', 'x': companies_list, 'y': fixed_assets, 'marker': {'color': '#f87171'}, 'hovertemplate': '<b>%{x}</b><br>Fixed Assets: $%{y:.1f}M<extra></extra>'}
        ],
        'layout': {
            'title': {'text': 'Asset Composition (Latest Year)', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Assets ($M)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'barmode': 'stack',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="asset_composition_chart", height=500)


def _create_leverage_matrix_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 16: Financial leverage analysis"""
    
    companies_list = list(companies.keys())
    debt_ratios = []
    equity_multipliers = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            
            total_debt = latest.get('totalDebt', 0)
            equity = latest.get('totalStockholdersEquity', 1)
            assets = latest.get('totalAssets', 1)
            
            debt_ratio = (total_debt / assets) * 100 if assets > 0 else 0
            equity_mult = assets / equity if equity > 0 else 1
            
            debt_ratios.append(debt_ratio)
            equity_multipliers.append(equity_mult)
        else:
            debt_ratios.append(0)
            equity_multipliers.append(1)
    
    traces = []
    for i, company in enumerate(companies_list):
        traces.append({
            'type': 'scatter',
            'mode': 'markers',
            'name': company,
            'x': [debt_ratios[i]],
            'y': [equity_multipliers[i]],
            'marker': {'size': 20, 'color': colors[i % len(colors)], 'line': {'color': 'white', 'width': 2}},
            'hovertemplate': f'<b>{company}</b><br>Debt Ratio: %{{x:.1f}}%<br>Equity Multiplier: %{{y:.2f}}x<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Financial Leverage Analysis', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Debt Ratio (%)', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Equity Multiplier', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="leverage_matrix_chart", height=500)


# =============================================================================
# CHART SET 5: ADVANCED FINANCIAL METRICS (4 CHARTS)
# =============================================================================

def _build_advanced_metrics_charts(df: pd.DataFrame, companies: Dict[str, str], financial_history: Dict[str, pd.DataFrame]) -> str:
    """Build 4 advanced financial metrics charts"""
    
    html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
    
    html += _create_liquidity_ratios_chart(df, companies)
    html += _create_asset_turnover_chart(df, companies, colors)
    html += _create_interest_coverage_chart(df, companies, colors)
    html += _create_financial_health_heatmap(df, companies)
    
    return html


def _create_liquidity_ratios_chart(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Chart 17: Liquidity ratios comparison"""
    
    companies_list = list(companies.keys())
    current_ratios = []
    quick_ratios = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            current_ratios.append(latest.get('currentRatio', 0))
            quick_ratios.append(latest.get('quickRatio', 0))
        else:
            current_ratios.append(0)
            quick_ratios.append(0)
    
    fig_data = {
        'data': [
            {'type': 'bar', 'name': 'Current Ratio', 'x': companies_list, 'y': current_ratios, 'marker': {'color': '#60a5fa'}, 'hovertemplate': '<b>%{x}</b><br>Current Ratio: %{y:.2f}x<extra></extra>'},
            {'type': 'bar', 'name': 'Quick Ratio', 'x': companies_list, 'y': quick_ratios, 'marker': {'color': '#34d399'}, 'hovertemplate': '<b>%{x}</b><br>Quick Ratio: %{y:.2f}x<extra></extra>'}
        ],
        'layout': {
            'title': {'text': 'Liquidity Ratios Comparison', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Ratio', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'barmode': 'group',
            'shapes': [{'type': 'line', 'x0': -0.5, 'x1': len(companies_list) - 0.5, 'y0': 1, 'y1': 1, 'line': {'color': 'rgba(239, 68, 68, 0.5)', 'width': 2, 'dash': 'dash'}}],
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="liquidity_ratios_chart", height=500)


def _create_asset_turnover_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 18: Asset turnover efficiency trends"""
    
    traces = []
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        years = company_data['Year'].tolist()
        turnover_ratios = []
        
        for _, row in company_data.iterrows():
            revenue = row.get('revenue', 0)
            assets = row.get('totalAssets', 1)
            turnover = revenue / assets if assets > 0 else 0
            turnover_ratios.append(turnover)
        
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': company_name,
            'x': years,
            'y': turnover_ratios,
            'line': {'color': colors[i % len(colors)], 'width': 3},
            'marker': {'size': 8},
            'hovertemplate': f'<b>{company_name}</b><br>Year: %{{x}}<br>Asset Turnover: %{{y:.2f}}x<extra></extra>'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Asset Turnover Efficiency Trends', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Asset Turnover Ratio', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="asset_turnover_chart", height=500)


def _create_interest_coverage_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 19: Interest coverage ratios"""
    
    companies_list = list(companies.keys())
    interest_coverage = []
    bar_colors = []
    
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            coverage = min(latest.get('interestCoverageRatio', 0), 50)  # Cap at 50 for viz
            interest_coverage.append(coverage)
            
            # Color based on safety
            if coverage >= 5:
                bar_colors.append('#10b981')
            elif coverage >= 2.5:
                bar_colors.append('#3b82f6')
            elif coverage >= 1.5:
                bar_colors.append('#f59e0b')
            else:
                bar_colors.append('#ef4444')
        else:
            interest_coverage.append(0)
            bar_colors.append('#94a3b8')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': interest_coverage,
            'marker': {'color': bar_colors, 'line': {'color': 'white', 'width': 2}},
            'text': [f'{ic:.1f}' for ic in interest_coverage],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Interest Coverage: %{y:.1f}x<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Interest Coverage Analysis', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Interest Coverage Ratio', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'shapes': [{'type': 'line', 'x0': -0.5, 'x1': len(companies_list) - 0.5, 'y0': 2.5, 'y1': 2.5, 'line': {'color': 'rgba(239, 68, 68, 0.5)', 'width': 2, 'dash': 'dash'}}]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="interest_coverage_chart", height=500)


def _create_financial_health_heatmap(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Chart 20: Financial health heatmap"""
    
    import plotly.graph_objects as go
    
    companies_list = list(companies.keys())
    metric_names = ['Current Ratio', 'ROE (%)', 'ROA (%)', 'Asset Turnover', 'Interest Cov.']
    
    # Collect metrics
    metrics_data = []
    for company_name in companies_list:
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            
            current_ratio = latest.get('currentRatio', 1)
            net_income = latest.get('netIncome', 0)
            equity = latest.get('totalStockholdersEquity', 1)
            assets = latest.get('totalAssets', 1)
            revenue = latest.get('revenue', 0)
            interest_cov = min(latest.get('interestCoverageRatio', 0), 20)
            
            roe = (net_income / equity) * 100 if equity > 0 else 0
            roa = (net_income / assets) * 100 if assets > 0 else 0
            asset_turn = revenue / assets if assets > 0 else 0
            
            metrics_data.append([current_ratio, roe, roa, asset_turn, interest_cov])
        else:
            metrics_data.append([0, 0, 0, 0, 0])
    
    # Normalize for heatmap (z-score)
    metrics_array = np.array(metrics_data)
    normalized_data = []
    for col_idx in range(metrics_array.shape[1]):
        col = metrics_array[:, col_idx]
        mean = np.mean(col)
        std = np.std(col)
        if std > 0:
            normalized_col = (col - mean) / std
        else:
            normalized_col = col - mean
        normalized_data.append(normalized_col)
    
    normalized_data = np.array(normalized_data).T
    
    # Create heatmap
    fig_dict = {
        'data': [{
            'type': 'heatmap',
            'z': normalized_data.tolist(),
            'x': metric_names,
            'y': companies_list,
            'colorscale': 'RdYlGn',
            'zmid': 0,
            'text': [[f'{metrics_data[i][j]:.1f}' for j in range(len(metric_names))] for i in range(len(companies_list))],
            'texttemplate': '%{text}',
            'textfont': {'size': 10},
            'hovertemplate': '<b>%{y}</b><br>%{x}: %{text}<br>Z-score: %{z:.2f}<extra></extra>',
            'colorbar': {'title': 'Z-Score'}
        }],
        'layout': {
            'title': {'text': 'Financial Health Matrix', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Financial Metrics', 'side': 'bottom'},
            'yaxis': {'title': 'Companies'},
            'height': 500
        }
    }
    
    return build_plotly_chart(fig_dict, div_id="financial_health_heatmap", height=500)


# =============================================================================
# CHART SET 6: CROSS-COMPANY COMPARATIVE ANALYSIS (4 CHARTS)
# =============================================================================

def _build_comparative_charts(df: pd.DataFrame, companies: Dict[str, str], financial_history: Dict[str, pd.DataFrame]) -> str:
    """Build 4 cross-company comparative charts"""
    
    html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
    
    html += _create_revenue_comparison_chart(df, companies, colors)
    html += _create_net_margin_comparison_chart(df, companies, colors)
    html += _create_roe_comparison_chart(df, companies, colors)
    html += _create_fcf_comparison_chart(df, companies, colors)
    
    return html


def _create_revenue_comparison_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 21: Latest year revenue comparison"""
    
    companies_list = list(companies.keys())
    revenues = []
    bar_colors = []
    
    for i, company_name in enumerate(companies_list):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            revenues.append(latest.get('revenue', 0) / 1_000_000)
            bar_colors.append(colors[i % len(colors)])
        else:
            revenues.append(0)
            bar_colors.append('#94a3b8')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': revenues,
            'marker': {'color': bar_colors, 'line': {'color': 'white', 'width': 2}},
            'text': [f'${r:.0f}M' for r in revenues],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Revenue: $%{y:.0f}M<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Latest Year Revenue Comparison', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Revenue ($M)', 'gridcolor': 'rgba(0,0,0,0.1)'}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="revenue_comparison_chart", height=500)


def _create_net_margin_comparison_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 22: Net profit margin comparison"""
    
    companies_list = list(companies.keys())
    net_margins = []
    bar_colors = []
    
    for i, company_name in enumerate(companies_list):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            margin = latest.get('netProfitMargin', 0) * 100
            net_margins.append(margin)
            
            if margin >= 20:
                bar_colors.append('#10b981')
            elif margin >= 10:
                bar_colors.append('#3b82f6')
            elif margin >= 5:
                bar_colors.append('#f59e0b')
            else:
                bar_colors.append('#ef4444')
        else:
            net_margins.append(0)
            bar_colors.append('#94a3b8')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': net_margins,
            'marker': {'color': bar_colors, 'line': {'color': 'white', 'width': 2}},
            'text': [f'{m:.1f}%' for m in net_margins],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Net Profit Margin Comparison', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Net Margin (%)', 'gridcolor': 'rgba(0,0,0,0.1)'}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="net_margin_comparison_chart", height=500)


def _create_roe_comparison_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 23: Return on equity comparison"""
    
    companies_list = list(companies.keys())
    roes = []
    bar_colors = []
    
    for i, company_name in enumerate(companies_list):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            net_income = latest.get('netIncome', 0)
            equity = latest.get('totalStockholdersEquity', 1)
            roe = (net_income / equity) * 100 if equity > 0 else 0
            roes.append(roe)
            
            if roe >= 15:
                bar_colors.append('#10b981')
            elif roe >= 10:
                bar_colors.append('#3b82f6')
            elif roe >= 5:
                bar_colors.append('#f59e0b')
            else:
                bar_colors.append('#ef4444')
        else:
            roes.append(0)
            bar_colors.append('#94a3b8')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': roes,
            'marker': {'color': bar_colors, 'line': {'color': 'white', 'width': 2}},
            'text': [f'{r:.1f}%' for r in roes],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>ROE: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Return on Equity Comparison', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'ROE (%)', 'gridcolor': 'rgba(0,0,0,0.1)'}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="roe_comparison_chart", height=500)


def _create_fcf_comparison_chart(df: pd.DataFrame, companies: Dict[str, str], colors: List[str]) -> str:
    """Chart 24: Free cash flow comparison"""
    
    companies_list = list(companies.keys())
    fcfs = []
    bar_colors = []
    
    for i, company_name in enumerate(companies_list):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        if not company_data.empty:
            latest = company_data.iloc[-1]
            fcf = latest.get('freeCashFlow', 0) / 1_000_000
            fcfs.append(fcf)
            
            if fcf >= 0:
                bar_colors.append(colors[i % len(colors)])
            else:
                bar_colors.append('#ef4444')
        else:
            fcfs.append(0)
            bar_colors.append('#94a3b8')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': fcfs,
            'marker': {'color': bar_colors, 'line': {'color': 'white', 'width': 2}},
            'text': [f'${f:.0f}M' for f in fcfs],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>FCF: $%{y:.0f}M<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Free Cash Flow Comparison', 'font': {'size': 18, 'color': '#1e293b'}},
            'xaxis': {'title': 'Company', 'gridcolor': 'rgba(0,0,0,0.1)'},
            'yaxis': {'title': 'Free Cash Flow ($M)', 'gridcolor': 'rgba(0,0,0,0.1)', 'zeroline': True, 'zerolinecolor': 'rgba(0,0,0,0.5)', 'zerolinewidth': 2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="fcf_comparison_chart", height=500)


"""
Section 3C: Working Capital Management & Operational Efficiency
Section 3D: Capital Allocation & Return Analysis

INSTRUCTIONS:
1. Copy this entire code
2. In your section_03.py, find these two stub functions:
   - _build_section_3c_working_capital()
   - _build_section_3d_capital_allocation()
3. Replace both stub functions with the implementations below
4. Copy all the helper functions to your section_03.py file
"""


def _build_section_3c_working_capital(df: pd.DataFrame,companies: Dict[str, str]) -> str:
    """Build Section 3C: Working Capital Management & Operational Efficiency"""
    
    html = '<div class="info-section">'
    html += '<h3>3C. Working Capital Management & Operational Efficiency</h3>'
    html += '<h4>Working Capital Dynamics</h4>'
    
    # Working capital analysis
    wc_analysis = _analyze_working_capital_efficiency(df, companies)
    
    if wc_analysis:
        # Create working capital table
        wc_df = _prepare_working_capital_display(wc_analysis)
        html += build_data_table(
            wc_df,
            table_id="working_capital_table",
            sortable=True,
            page_length=-1
        )
        
        # Working capital analysis summary
        wc_summary = _generate_working_capital_summary(wc_analysis)
        html += build_info_box(
            f"<p>{wc_summary}</p>",
            box_type="info",
            title="Working Capital Management Assessment"
        )
    else:
        html += build_info_box(
            "<p>Insufficient data for working capital analysis.</p>",
            box_type="warning"
        )
    
    html += '</div>'
    
    return html


def _build_section_3d_capital_allocation(df: pd.DataFrame,companies: Dict[str, str]) -> str:
    """Build Section 3D: Capital Allocation & Return Analysis"""
    
    html = '<div class="info-section">'
    html += '<h3>3D. Capital Allocation & Return Analysis</h3>'
    html += '<h4>Return on Invested Capital & Capital Efficiency</h4>'
    
    # Capital efficiency analysis
    capital_efficiency = _analyze_capital_efficiency(df, companies)
    
    if capital_efficiency:
        # Create capital efficiency table
        cap_df = _prepare_capital_efficiency_display(capital_efficiency)
        html += build_data_table(
            cap_df,
            table_id="capital_efficiency_table",
            sortable=True,
            page_length=-1
        )
        
        # Capital allocation analysis summary
        capital_summary = _generate_capital_allocation_summary(capital_efficiency)
        html += build_info_box(
            f"<p>{capital_summary}</p>",
            box_type="success",
            title="Capital Allocation & Efficiency Assessment"
        )
    else:
        html += build_info_box(
            "<p>Insufficient data for capital efficiency analysis.</p>",
            box_type="warning"
        )
    
    html += '</div>'
    
    return html


# =============================================================================
# SECTION 3C HELPER FUNCTIONS: WORKING CAPITAL ANALYSIS
# =============================================================================

def _analyze_working_capital_efficiency(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze working capital efficiency metrics"""
    
    wc_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Working capital calculation
        current_assets = latest.get('totalCurrentAssets', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        working_capital = current_assets - current_liabilities
        
        metrics['working_capital'] = working_capital
        
        # Working capital as % of revenue
        revenue = latest.get('revenue', 1)
        if revenue > 0:
            metrics['wc_revenue_ratio'] = (working_capital / revenue) * 100
        else:
            metrics['wc_revenue_ratio'] = 0
        
        # Days calculations
        receivables = latest.get('netReceivables', 0)
        inventory = latest.get('inventory', 0)
        payables = latest.get('accountPayables', 0)
        
        # Days Sales Outstanding (DSO)
        if revenue > 0 and receivables > 0:
            metrics['days_sales_outstanding'] = (receivables / revenue) * 365
        else:
            metrics['days_sales_outstanding'] = 0
        
        # Days Inventory Outstanding (DIO)
        cost_of_revenue = latest.get('costOfRevenue', revenue * 0.7)
        if cost_of_revenue > 0 and inventory > 0:
            metrics['days_inventory_outstanding'] = (inventory / cost_of_revenue) * 365
        else:
            metrics['days_inventory_outstanding'] = 0
        
        # Days Payable Outstanding (DPO)
        if cost_of_revenue > 0 and payables > 0:
            metrics['days_payable_outstanding'] = (payables / cost_of_revenue) * 365
        else:
            metrics['days_payable_outstanding'] = 0
        
        # Cash conversion cycle
        metrics['cash_conversion_cycle'] = (metrics['days_sales_outstanding'] + 
                                          metrics['days_inventory_outstanding'] - 
                                          metrics['days_payable_outstanding'])
        
        # Efficiency score (0-10, lower cash cycle = higher score)
        if metrics['cash_conversion_cycle'] < 0:
            metrics['efficiency_score'] = 10
        elif metrics['cash_conversion_cycle'] < 30:
            metrics['efficiency_score'] = 9
        elif metrics['cash_conversion_cycle'] < 60:
            metrics['efficiency_score'] = 8
        elif metrics['cash_conversion_cycle'] < 90:
            metrics['efficiency_score'] = 6
        elif metrics['cash_conversion_cycle'] < 120:
            metrics['efficiency_score'] = 4
        else:
            metrics['efficiency_score'] = 2
        
        wc_analysis[company_name] = metrics
    
    return wc_analysis


def _prepare_working_capital_display(wc_analysis: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare working capital DataFrame for display"""
    
    rows = []
    
    for company_name, metrics in wc_analysis.items():
        rows.append({
            'Company': company_name,
            'Working Capital': f"${metrics['working_capital']/1000:,.0f}K",
            'WC/Revenue %': f"{metrics['wc_revenue_ratio']:.1f}%",
            'DSO (Days)': f"{metrics['days_sales_outstanding']:.0f}",
            'DIO (Days)': f"{metrics['days_inventory_outstanding']:.0f}",
            'DPO (Days)': f"{metrics['days_payable_outstanding']:.0f}",
            'Cash Cycle': f"{metrics['cash_conversion_cycle']:.0f}",
            'WC Efficiency Score': f"{metrics['efficiency_score']:.1f}/10"
        })
    
    return pd.DataFrame(rows)


def _generate_working_capital_summary(wc_analysis: Dict[str, Dict]) -> str:
    """Generate working capital analysis summary"""
    
    if not wc_analysis:
        return "Insufficient data for working capital analysis."
    
    # Calculate portfolio metrics
    avg_cash_cycle = np.mean([m['cash_conversion_cycle'] for m in wc_analysis.values()])
    avg_efficiency = np.mean([m['efficiency_score'] for m in wc_analysis.values()])
    
    efficient_companies = sum(1 for m in wc_analysis.values() if m['efficiency_score'] >= 7)
    total_companies = len(wc_analysis)
    
    return f"""<strong>Working Capital Management Assessment:</strong><br>
• Portfolio Cash Conversion Cycle: {avg_cash_cycle:.0f} days average, indicating {'excellent' if avg_cash_cycle < 30 else 'good' if avg_cash_cycle < 60 else 'moderate' if avg_cash_cycle < 90 else 'poor'} working capital efficiency<br>
• Efficiency Distribution: {efficient_companies}/{total_companies} companies ({(efficient_companies/total_companies)*100:.0f}%) rated as highly efficient (7+ score)<br>
• Portfolio Efficiency Score: {avg_efficiency:.1f}/10<br><br>

<strong>Key Insights:</strong><br>
• Cash Conversion Performance: {'Strong cash generation' if avg_cash_cycle < 60 else 'Adequate cash management' if avg_cash_cycle < 90 else 'Working capital optimization needed'}<br>
• Operational Excellence: {'Portfolio demonstrates efficient working capital management' if efficient_companies >= total_companies * 0.6 else 'Mixed working capital performance across portfolio' if efficient_companies >= total_companies * 0.3 else 'Significant working capital improvement opportunities'}<br>
• Strategic Priority: {'Maintain efficient working capital practices' if avg_efficiency >= 7 else 'Focus on reducing cash conversion cycle' if avg_cash_cycle > 90 else 'Optimize receivables and inventory management'} for enhanced cash flow generation"""


# =============================================================================
# SECTION 3D HELPER FUNCTIONS: CAPITAL ALLOCATION ANALYSIS
# =============================================================================

def _analyze_capital_efficiency(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze capital allocation and efficiency metrics"""
    
    capital_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Return on Invested Capital (ROIC)
        nopat = latest.get('ebit', 0) * 0.75  # Approximate NOPAT (EBIT * (1-tax rate))
        invested_capital = latest.get('totalAssets', 0) - latest.get('cashAndCashEquivalents', 0)
        
        if invested_capital > 0:
            metrics['roic'] = (nopat / invested_capital) * 100
        else:
            metrics['roic'] = 0
        
        # Return on Capital Employed (ROCE)
        ebit = latest.get('ebit', 0)
        capital_employed = latest.get('totalAssets', 0) - latest.get('totalCurrentLiabilities', 0)
        
        if capital_employed > 0:
            metrics['roce'] = (ebit / capital_employed) * 100
        else:
            metrics['roce'] = 0
        
        # Asset turnover
        revenue = latest.get('revenue', 0)
        total_assets = latest.get('totalAssets', 1)
        metrics['asset_turnover'] = revenue / total_assets
        
        # Capital intensity
        capex = latest.get('capitalExpenditure', 0)
        if revenue > 0:
            metrics['capital_intensity'] = (abs(capex) / revenue) * 100
            metrics['capex_revenue_ratio'] = (abs(capex) / revenue) * 100
        else:
            metrics['capital_intensity'] = 0
            metrics['capex_revenue_ratio'] = 0
        
        # CapEx to Depreciation ratio
        depreciation = latest.get('depreciationAndAmortization', 1)
        metrics['capex_depreciation_ratio'] = abs(capex) / depreciation if depreciation > 0 else 0
        
        # WACC estimate (simplified)
        debt_ratio = latest.get('debtToEquityRatio', 0.3)
        if debt_ratio > 0:
            # Simplified WACC estimate
            risk_free_rate = 0.04
            equity_risk_premium = 0.06
            cost_of_debt = 0.05
            tax_rate = 0.25
            
            weight_debt = debt_ratio / (1 + debt_ratio)
            weight_equity = 1 / (1 + debt_ratio)
            
            metrics['wacc_estimate'] = (weight_equity * (risk_free_rate + equity_risk_premium) + 
                                       weight_debt * cost_of_debt * (1 - tax_rate)) * 100
        else:
            metrics['wacc_estimate'] = 8.0
        
        # Value creation (ROIC vs WACC)
        if metrics['roic'] > metrics['wacc_estimate']:
            metrics['value_creation'] = 'Creating Value'
        elif metrics['roic'] > metrics['wacc_estimate'] * 0.8:
            metrics['value_creation'] = 'Adequate Returns'
        else:
            metrics['value_creation'] = 'Destroying Value'
        
        capital_analysis[company_name] = metrics
    
    # Calculate efficiency rankings
    roic_values = [(name, metrics['roic']) for name, metrics in capital_analysis.items()]
    roic_values.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (company_name, _) in enumerate(roic_values):
        capital_analysis[company_name]['efficiency_rank'] = rank + 1
    
    return capital_analysis


def _prepare_capital_efficiency_display(capital_efficiency: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare capital efficiency DataFrame for display"""
    
    rows = []
    
    for company_name, metrics in capital_efficiency.items():
        rows.append({
            'Company': company_name,
            'ROIC %': f"{metrics['roic']:.1f}%",
            'ROCE %': f"{metrics['roce']:.1f}%",
            'Asset Turnover': f"{metrics['asset_turnover']:.2f}x",
            'Capital Intensity': f"{metrics['capital_intensity']:.1f}%",
            'CapEx/Revenue %': f"{metrics['capex_revenue_ratio']:.1f}%",
            'CapEx/Depreciation': f"{metrics['capex_depreciation_ratio']:.1f}x",
            'WACC Estimate %': f"{metrics['wacc_estimate']:.1f}%",
            'Value Creation': metrics['value_creation'],
            'Efficiency Rank': f"{metrics['efficiency_rank']}/{len(capital_efficiency)}"
        })
    
    return pd.DataFrame(rows)


def _generate_capital_allocation_summary(capital_efficiency: Dict[str, Dict]) -> str:
    """Generate capital allocation analysis summary"""
    
    if not capital_efficiency:
        return "Insufficient data for capital efficiency analysis."
    
    # Portfolio metrics
    avg_roic = np.mean([m['roic'] for m in capital_efficiency.values()])
    avg_wacc = np.mean([m['wacc_estimate'] for m in capital_efficiency.values()])
    
    value_creators = sum(1 for m in capital_efficiency.values() if m['value_creation'] == 'Creating Value')
    total_companies = len(capital_efficiency)
    
    return f"""<strong>Capital Allocation & Efficiency Assessment:</strong><br>
• Portfolio ROIC Performance: {avg_roic:.1f}% average return on invested capital<br>
• Cost of Capital: {avg_wacc:.1f}% estimated weighted average cost of capital<br>
• Value Creation: {value_creators}/{total_companies} companies ({(value_creators/total_companies)*100:.0f}%) generating returns above cost of capital<br><br>

<strong>Economic Value Analysis:</strong><br>
• ROIC-WACC Spread: {avg_roic - avg_wacc:.1f} percentage points {'(positive value creation)' if avg_roic > avg_wacc else '(neutral)' if avg_roic > avg_wacc * 0.9 else '(value destruction)'}<br>
• Capital Deployment Effectiveness: {'Excellent' if value_creators >= total_companies * 0.7 else 'Good' if value_creators >= total_companies * 0.5 else 'Needs Improvement' if value_creators >= total_companies * 0.3 else 'Poor'} capital allocation discipline<br>
• Return Profile: {'High-return portfolio' if avg_roic > 15 else 'Market-rate returns' if avg_roic > 10 else 'Below-market returns'} relative to expectations<br><br>

<strong>Strategic Implications:</strong><br>
• Investment Strategy: {'Accelerate capital deployment' if avg_roic > 15 and value_creators >= total_companies * 0.6 else 'Maintain current allocation' if avg_roic > 10 else 'Restructure capital allocation'} based on return profile<br>
• Portfolio Optimization: {'Focus on scaling high-ROIC businesses' if value_creators >= total_companies * 0.5 else 'Improve returns on invested capital' if avg_roic < 12 else 'Mixed optimization approach required'}<br>
• Shareholder Value: {'Strong value creation trajectory' if avg_roic > avg_wacc + 3 else 'Adequate value preservation' if avg_roic > avg_wacc else 'Value enhancement required'} based on economic profit generation"""


"""
Section 3E: Financial Quality & Earnings Analysis
Section 3F: Financial Overview Summary & Strategic Insights

INSTRUCTIONS:
1. Copy this entire code
2. In your section_03.py, find these two stub functions:
   - _build_section_3e_financial_quality()
   - _build_section_3f_summary_insights()
3. Replace both stub functions with the implementations below
4. Copy all the helper functions to your section_03.py file
"""


def _build_section_3e_financial_quality(
    df: pd.DataFrame,
    companies: Dict[str, str],
    financial_history: Dict[str, pd.DataFrame]
) -> str:
    """Build Section 3E: Financial Quality & Earnings Analysis"""
    
    html = '<div class="info-section">'
    html += '<h3>3E. Financial Quality & Earnings Analysis</h3>'
    html += '<h4>Earnings Quality & Cash Flow Assessment</h4>'
    
    # Earnings quality analysis
    earnings_quality = _analyze_earnings_quality(df, companies)
    
    if earnings_quality:
        # Create earnings quality table
        eq_df = _prepare_earnings_quality_display(earnings_quality)
        html += build_data_table(
            eq_df,
            table_id="earnings_quality_table",
            sortable=True,
            page_length=-1
        )
        
        # Financial quality summary
        quality_summary = _generate_financial_quality_summary(earnings_quality)
        html += build_info_box(
            f"<p>{quality_summary}</p>",
            box_type="info",
            title="Financial Quality & Risk Assessment"
        )
    else:
        html += build_info_box(
            "<p>Insufficient data for earnings quality analysis.</p>",
            box_type="warning"
        )
    
    html += '</div>'
    
    return html


"""
Section 3F: Financial Overview Summary & Strategic Insights
IMPROVED VERSION - Visual, scannable presentation with cards and metrics

INSTRUCTIONS:
Replace your existing _build_section_3f_summary_insights() function with this one.
"""


def _build_section_3f_summary_insights(
    df: pd.DataFrame,
    companies: Dict[str, str],
    financial_history: Dict[str, pd.DataFrame],
    growth_metrics: Dict[str, Dict]
) -> str:
    """Build Section 3F: Financial Overview Summary & Strategic Insights (Improved Visual Version)"""
    
    html = '<div class="info-section">'
    html += '<h3>3F. Financial Overview Summary & Strategic Insights</h3>'
    
    # Get all analysis components
    working_capital_analysis = _analyze_working_capital_efficiency(df, companies)
    capital_efficiency = _analyze_capital_efficiency(df, companies)
    earnings_quality = _analyze_earnings_quality(df, companies)
    
    # Calculate key metrics for cards
    total_companies = len(companies)
    
    if earnings_quality:
        avg_quality = np.mean([m['quality_score'] for m in earnings_quality.values()])
        high_quality_count = sum(1 for m in earnings_quality.values() if m['quality_score'] >= 7)
    else:
        avg_quality = 5
        high_quality_count = 0
    
    if capital_efficiency:
        avg_roic = np.mean([m['roic'] for m in capital_efficiency.values()])
        value_creators = sum(1 for m in capital_efficiency.values() if m['value_creation'] == 'Creating Value')
    else:
        avg_roic = 10
        value_creators = 0
    
    if growth_metrics:
        avg_growth = np.mean([m['revenue_growth_1y'] for m in growth_metrics.values()])
        sustainable_growers = sum(1 for m in growth_metrics.values() if m['sustainability_rating'] in ['Excellent', 'Good'])
    else:
        avg_growth = 5
        sustainable_growers = 0
    
    if working_capital_analysis:
        avg_wc_efficiency = np.mean([m['efficiency_score'] for m in working_capital_analysis.values()])
    else:
        avg_wc_efficiency = 5
    
    # BUILD SUMMARY KPI CARDS
    html += '<h4>Portfolio Performance Scorecard</h4>'
    
    cards = [
        {
            "label": "Financial Quality",
            "value": f"{avg_quality:.1f}/10",
            "description": f"{high_quality_count}/{total_companies} high-quality companies",
            "type": "success" if avg_quality >= 7 else "info" if avg_quality >= 5 else "warning"
        },
        {
            "label": "Capital Efficiency (ROIC)",
            "value": f"{avg_roic:.1f}%",
            "description": f"{value_creators}/{total_companies} creating value",
            "type": "success" if avg_roic > 15 else "info" if avg_roic > 10 else "warning"
        },
        {
            "label": "Revenue Growth",
            "value": f"{avg_growth:+.1f}%",
            "description": f"{sustainable_growers}/{total_companies} sustainable growers",
            "type": "success" if avg_growth > 8 else "info" if avg_growth > 3 else "warning"
        },
        {
            "label": "Working Capital Efficiency",
            "value": f"{avg_wc_efficiency:.1f}/10",
            "description": f"{'Excellent' if avg_wc_efficiency >= 7 else 'Good' if avg_wc_efficiency >= 5 else 'Fair'} cash management",
            "type": "success" if avg_wc_efficiency >= 7 else "info"
        }
    ]
    
    html += build_stat_grid(cards)
    
    # PORTFOLIO HEALTH RATING
    html += '<h4 style="margin-top: 40px;">Overall Portfolio Health Rating</h4>'
    overall_score = (avg_quality * 0.3 + (avg_roic / 20 * 10) * 0.3 + 
                    (min(avg_growth + 10, 20) / 20 * 10) * 0.2 + avg_wc_efficiency * 0.2)
    
    if overall_score >= 8:
        rating = "Excellent"
        rating_type = "success"
        rating_emoji = "🟢"
    elif overall_score >= 6:
        rating = "Good"
        rating_type = "info"
        rating_emoji = "🔵"
    elif overall_score >= 4:
        rating = "Fair"
        rating_type = "warning"
        rating_emoji = "🟡"
    else:
        rating = "Needs Improvement"
        rating_type = "danger"
        rating_emoji = "🔴"
    
    html += f"""
    <div style="text-align: center; margin: 20px 0;">
        <div style="font-size: 3rem;">{rating_emoji}</div>
        <div style="font-size: 2rem; font-weight: bold; margin: 10px 0; 
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {rating}
        </div>
        <div style="font-size: 1.2rem; color: var(--text-secondary);">
            Portfolio Health Score: {overall_score:.1f}/10
        </div>
    </div>
    """
    
    # STRENGTH ASSESSMENT - Compact Cards
    html += '<h4 style="margin-top: 40px;">Portfolio Financial Strength</h4>'
    
    html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">'
    
    # Financial Foundation Card
    html += f"""
    <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid #10b981; box-shadow: var(--shadow-sm);">
        <h5 style="margin: 0 0 15px 0; color: #10b981;">💪 Financial Foundation</h5>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li><strong>{avg_quality:.1f}/10</strong> quality score</li>
            <li><strong>{high_quality_count}/{total_companies}</strong> high-quality companies</li>
            <li><strong>{'Strong' if high_quality_count >= total_companies * 0.6 else 'Moderate' if high_quality_count >= total_companies * 0.4 else 'Weak'}</strong> foundation</li>
        </ul>
    </div>
    """
    
    # Value Creation Card
    html += f"""
    <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6; box-shadow: var(--shadow-sm);">
        <h5 style="margin: 0 0 15px 0; color: #3b82f6;">💎 Value Creation</h5>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li><strong>{avg_roic:.1f}%</strong> average ROIC</li>
            <li><strong>{value_creators}/{total_companies}</strong> value creators</li>
            <li><strong>{'Excellent' if value_creators >= total_companies * 0.6 else 'Good' if value_creators >= total_companies * 0.4 else 'Needs Work'}</strong> capital deployment</li>
        </ul>
    </div>
    """
    
    # Growth Momentum Card
    html += f"""
    <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b; box-shadow: var(--shadow-sm);">
        <h5 style="margin: 0 0 15px 0; color: #f59e0b;">🚀 Growth Momentum</h5>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li><strong>{avg_growth:+.1f}%</strong> average growth</li>
            <li><strong>{sustainable_growers}/{total_companies}</strong> sustainable growers</li>
            <li><strong>{'Strong' if avg_growth > 8 else 'Moderate' if avg_growth > 3 else 'Weak'}</strong> momentum</li>
        </ul>
    </div>
    """
    
    html += '</div>'
    
    # GROWTH & PROFITABILITY - Progress Bars
    html += '<h4 style="margin-top: 40px;">Growth & Profitability Performance</h4>'
    
    # Revenue Growth Progress
    growth_target = 10
    growth_percentage = min(100, (avg_growth / growth_target * 100))
    html += f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 600;">Revenue Growth vs Target</span>
            <span style="font-weight: 600; color: {'#10b981' if avg_growth >= growth_target else '#3b82f6' if avg_growth >= growth_target * 0.7 else '#f59e0b'};">
                {avg_growth:.1f}% / {growth_target}%
            </span>
        </div>
        <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
            <div style="width: {growth_percentage}%; background: linear-gradient(90deg, #667eea, #764ba2); 
                       height: 100%; border-radius: 10px; transition: width 0.8s ease;"></div>
        </div>
    </div>
    """
    
    # ROIC Progress
    roic_target = 15
    roic_percentage = min(100, (avg_roic / roic_target * 100))
    html += f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 600;">ROIC vs Target</span>
            <span style="font-weight: 600; color: {'#10b981' if avg_roic >= roic_target else '#3b82f6' if avg_roic >= roic_target * 0.7 else '#f59e0b'};">
                {avg_roic:.1f}% / {roic_target}%
            </span>
        </div>
        <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
            <div style="width: {roic_percentage}%; background: linear-gradient(90deg, #10b981, #059669); 
                       height: 100%; border-radius: 10px; transition: width 0.8s ease;"></div>
        </div>
    </div>
    """
    
    # Quality Score Progress
    quality_target = 8
    quality_percentage = (avg_quality / quality_target * 100)
    html += f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 600;">Financial Quality vs Target</span>
            <span style="font-weight: 600; color: {'#10b981' if avg_quality >= quality_target else '#3b82f6' if avg_quality >= quality_target * 0.7 else '#f59e0b'};">
                {avg_quality:.1f} / {quality_target}
            </span>
        </div>
        <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
            <div style="width: {quality_percentage}%; background: linear-gradient(90deg, #3b82f6, #2563eb); 
                       height: 100%; border-radius: 10px; transition: width 0.8s ease;"></div>
        </div>
    </div>
    """
    
    # KEY INSIGHTS - Compact Boxes
    html += '<h4 style="margin-top: 40px;">Key Strategic Insights</h4>'
    
    insights = []
    
    # Growth Insight
    if avg_growth > 8 and sustainable_growers >= total_companies * 0.5:
        insights.append({
            'title': '✅ Strong Growth Trajectory',
            'text': f'Portfolio demonstrates {avg_growth:.1f}% average growth with {sustainable_growers} companies showing sustainable expansion',
            'type': 'success'
        })
    elif avg_growth > 0:
        insights.append({
            'title': '📈 Moderate Growth Profile',
            'text': f'Portfolio growing at {avg_growth:.1f}% with opportunities to accelerate through strategic initiatives',
            'type': 'info'
        })
    else:
        insights.append({
            'title': '⚠️ Growth Challenges',
            'text': f'Portfolio requires immediate attention to reverse declining revenue trends',
            'type': 'warning'
        })
    
    # Profitability Insight
    if avg_roic > 15 and value_creators >= total_companies * 0.6:
        insights.append({
            'title': '✅ Excellent Capital Efficiency',
            'text': f'{avg_roic:.1f}% ROIC with {value_creators} companies creating economic value above cost of capital',
            'type': 'success'
        })
    elif avg_roic > 10:
        insights.append({
            'title': '💡 Solid Returns',
            'text': f'{avg_roic:.1f}% ROIC indicates adequate returns with room for optimization',
            'type': 'info'
        })
    else:
        insights.append({
            'title': '⚠️ Capital Efficiency Concerns',
            'text': f'Below-market returns at {avg_roic:.1f}% ROIC require strategic restructuring',
            'type': 'warning'
        })
    
    # Quality Insight
    if avg_quality >= 7:
        insights.append({
            'title': '✅ High Financial Quality',
            'text': f'{high_quality_count} companies demonstrate strong earnings quality and cash generation',
            'type': 'success'
        })
    elif avg_quality >= 5:
        insights.append({
            'title': '📊 Adequate Quality Standards',
            'text': f'Financial quality meets minimum standards with opportunities for enhancement',
            'type': 'info'
        })
    else:
        insights.append({
            'title': '⚠️ Quality Enhancement Required',
            'text': f'Enhanced scrutiny needed for earnings quality and cash flow alignment',
            'type': 'warning'
        })
    
    for insight in insights:
        html += build_info_box(
            f"<p style='margin: 0;'>{insight['text']}</p>",
            box_type=insight['type'],
            title=insight['title']
        )
    
    # RECOMMENDATIONS - Accordion Style
    html += '<h4 style="margin-top: 40px;">Strategic Recommendations</h4>'
    
    # Immediate Actions
    html += f"""
    <div style="background: var(--card-bg); border-radius: 12px; padding: 20px; margin: 15px 0; border-left: 4px solid #ef4444; box-shadow: var(--shadow-sm);">
        <h5 style="margin: 0 0 15px 0; color: #ef4444;">🎯 Immediate Actions (0-6 Months)</h5>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li><strong>Portfolio Optimization:</strong> {'Maintain current allocation' if high_quality_count >= total_companies * 0.6 else 'Increase allocation to high-quality companies'}</li>
            <li><strong>Monitoring:</strong> Implement {'standard' if avg_quality >= 6 else 'enhanced'} financial quality tracking</li>
            <li><strong>Capital Deployment:</strong> {'Accelerate growth investments' if avg_roic > 15 else 'Optimize balance' if avg_roic > 10 else 'Focus on profitability'}</li>
        </ul>
    </div>
    """
    
    # Medium-Term Strategy
    html += f"""
    <div style="background: var(--card-bg); border-radius: 12px; padding: 20px; margin: 15px 0; border-left: 4px solid #f59e0b; box-shadow: var(--shadow-sm);">
        <h5 style="margin: 0 0 15px 0; color: #f59e0b;">📅 Medium-Term Strategy (6-18 Months)</h5>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li><strong>Quality Enhancement:</strong> {'Maintain excellence' if high_quality_count >= total_companies * 0.7 else 'Targeted improvements'}</li>
            <li><strong>Growth Initiatives:</strong> Develop {'advanced' if sustainable_growers >= total_companies * 0.6 else 'standard'} growth frameworks</li>
            <li><strong>Operational Efficiency:</strong> {'Maintain leadership' if avg_wc_efficiency >= 7 else 'Improve working capital'}</li>
        </ul>
    </div>
    """
    
    # Long-Term Vision
    html += f"""
    <div style="background: var(--card-bg); border-radius: 12px; padding: 20px; margin: 15px 0; border-left: 4px solid #10b981; box-shadow: var(--shadow-sm);">
        <h5 style="margin: 0 0 15px 0; color: #10b981;">🎯 Long-Term Vision (18+ Months)</h5>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li><strong>Market Position:</strong> {'Expand leadership' if avg_roic > 15 and avg_quality >= 7 else 'Enhance position' if avg_roic > 10 else 'Defensive strategy'}</li>
            <li><strong>Innovation:</strong> {'Increase R&D' if sustainable_growers >= total_companies * 0.5 and avg_roic > 12 else 'Maintain spending' if avg_roic > 8 else 'Optimize ROI'}</li>
            <li><strong>Shareholder Returns:</strong> {'Aggressive returns' if value_creators >= total_companies * 0.6 and avg_roic > 15 else 'Balanced policy' if value_creators >= total_companies * 0.4 else 'Capital preservation'}</li>
        </ul>
    </div>
    """
    
    # SUCCESS TARGETS
    html += '<h4 style="margin-top: 40px;">Success Metrics & Targets</h4>'
    
    target_cards = [
        {
            "label": "Financial Quality Target",
            "value": f"{min(10, avg_quality + 1.5):.1f}/10",
            "description": "24-month objective",
            "type": "info"
        },
        {
            "label": "ROIC Target",
            "value": f"{min(25, avg_roic + 3):.1f}%",
            "description": "36-month objective",
            "type": "info"
        },
        {
            "label": "Value Creators Target",
            "value": f"{min(total_companies, value_creators + max(1, (total_companies - value_creators) // 2))}/{total_companies}",
            "description": "Portfolio optimization goal",
            "type": "info"
        }
    ]
    
    html += build_stat_grid(target_cards)
    
    html += '</div>'
    
    return html


# =============================================================================
# SECTION 3E HELPER FUNCTIONS: EARNINGS QUALITY ANALYSIS
# =============================================================================

def _analyze_earnings_quality(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze earnings quality and cash flow metrics"""
    
    earnings_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Accruals ratio (Sloan)
        net_income = latest.get('netIncome', 0)
        operating_cash_flow = latest.get('operatingCashFlow', 0)
        total_assets = latest.get('totalAssets', 1)
        
        if total_assets > 0:
            metrics['accruals_ratio'] = (net_income - operating_cash_flow) / total_assets
        else:
            metrics['accruals_ratio'] = 0
        
        # FCF to Net Income ratio
        free_cash_flow = latest.get('freeCashFlow', 0)
        if net_income > 0:
            metrics['fcf_ni_ratio'] = free_cash_flow / net_income
        else:
            metrics['fcf_ni_ratio'] = 0
        
        # OCF to EBITDA ratio
        ebitda = latest.get('ebitda', 1)
        if ebitda > 0:
            metrics['ocf_ebitda_ratio'] = operating_cash_flow / ebitda
        else:
            metrics['ocf_ebitda_ratio'] = 0
        
        # Revenue quality (stability of revenue recognition)
        if len(company_data) >= 4:
            recent_revenues = company_data['revenue'].tail(4).dropna()
            if len(recent_revenues) >= 3:
                revenue_cv = np.std(recent_revenues) / np.mean(recent_revenues)
                metrics['revenue_quality'] = max(0, min(10, 10 - revenue_cv * 10))
            else:
                metrics['revenue_quality'] = 5
        else:
            metrics['revenue_quality'] = 5
        
        # Earnings stability
        if len(company_data) >= 4:
            recent_earnings = company_data['netIncome'].tail(4).dropna()
            if len(recent_earnings) >= 3 and np.mean(recent_earnings) != 0:
                earnings_cv = np.std(recent_earnings) / abs(np.mean(recent_earnings))
                metrics['earnings_stability'] = max(0, min(10, 10 - earnings_cv * 5))
            else:
                metrics['earnings_stability'] = 5
        else:
            metrics['earnings_stability'] = 5
        
        # Cash conversion quality
        if metrics['fcf_ni_ratio'] > 1.2:
            metrics['cash_conversion'] = 10
        elif metrics['fcf_ni_ratio'] > 1.0:
            metrics['cash_conversion'] = 8
        elif metrics['fcf_ni_ratio'] > 0.8:
            metrics['cash_conversion'] = 6
        elif metrics['fcf_ni_ratio'] > 0.5:
            metrics['cash_conversion'] = 4
        else:
            metrics['cash_conversion'] = 2
        
        # Overall quality score
        metrics['quality_score'] = (
            (10 - abs(metrics['accruals_ratio']) * 20) * 0.2 +
            min(10, metrics['fcf_ni_ratio'] * 5) * 0.25 +
            min(10, metrics['ocf_ebitda_ratio'] * 10) * 0.15 +
            metrics['revenue_quality'] * 0.2 +
            metrics['earnings_stability'] * 0.2
        )
        metrics['quality_score'] = max(0, min(10, metrics['quality_score']))
        
        # Quality grade
        if metrics['quality_score'] >= 8:
            metrics['quality_grade'] = 'A (Excellent)'
        elif metrics['quality_score'] >= 6:
            metrics['quality_grade'] = 'B (Good)'
        elif metrics['quality_score'] >= 4:
            metrics['quality_grade'] = 'C (Fair)'
        else:
            metrics['quality_grade'] = 'D (Poor)'
        
        earnings_analysis[company_name] = metrics
    
    return earnings_analysis


def _prepare_earnings_quality_display(earnings_quality: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare earnings quality DataFrame for display"""
    
    rows = []
    
    for company_name, metrics in earnings_quality.items():
        rows.append({
            'Company': company_name,
            'Accruals Ratio': f"{metrics['accruals_ratio']:.2f}",
            'FCF/Net Income': f"{metrics['fcf_ni_ratio']:.2f}",
            'OCF/EBITDA': f"{metrics['ocf_ebitda_ratio']:.2f}",
            'Revenue Quality': f"{metrics['revenue_quality']:.1f}/10",
            'Earnings Stability': f"{metrics['earnings_stability']:.1f}/10",
            'Cash Conversion': f"{metrics['cash_conversion']:.1f}/10",
            'Quality Score': f"{metrics['quality_score']:.1f}/10",
            'Quality Grade': metrics['quality_grade']
        })
    
    return pd.DataFrame(rows)


def _generate_financial_quality_summary(earnings_quality: Dict[str, Dict]) -> str:
    """Generate financial quality analysis summary"""
    
    if not earnings_quality:
        return "Insufficient data for earnings quality analysis."
    
    # Portfolio quality metrics
    avg_quality_score = np.mean([m['quality_score'] for m in earnings_quality.values()])
    high_quality_companies = sum(1 for m in earnings_quality.values() if m['quality_score'] >= 7)
    total_companies = len(earnings_quality)
    
    # Cash conversion analysis
    strong_cash_conversion = sum(1 for m in earnings_quality.values() if m['cash_conversion'] >= 8)
    
    return f"""<strong>Financial Quality & Earnings Assessment:</strong><br>
• Portfolio Quality Score: {avg_quality_score:.1f}/10 indicating {'excellent' if avg_quality_score >= 8 else 'good' if avg_quality_score >= 6 else 'fair' if avg_quality_score >= 4 else 'poor'} earnings quality<br>
• High-Quality Distribution: {high_quality_companies}/{total_companies} companies ({(high_quality_companies/total_companies)*100:.0f}%) rated as high quality (7+ score)<br>
• Cash Conversion Strength: {strong_cash_conversion}/{total_companies} companies with strong cash conversion characteristics<br><br>

<strong>Quality Indicators:</strong><br>
• Accruals Management: {'Conservative' if avg_quality_score >= 7 else 'Moderate' if avg_quality_score >= 5 else 'Aggressive'} accounting practices across portfolio<br>
• Earnings Sustainability: {'High confidence' if high_quality_companies >= total_companies * 0.6 else 'Moderate confidence' if high_quality_companies >= total_companies * 0.4 else 'Low confidence'} in earnings persistence<br>
• Cash Flow Quality: {'Strong' if strong_cash_conversion >= total_companies * 0.6 else 'Adequate' if strong_cash_conversion >= total_companies * 0.4 else 'Weak'} cash generation relative to reported earnings<br><br>

<strong>Risk Assessment:</strong><br>
• Earnings Quality Risk: {'Low' if avg_quality_score >= 7 and high_quality_companies >= total_companies * 0.6 else 'Moderate' if avg_quality_score >= 5 else 'High'} requiring {'minimal' if avg_quality_score >= 7 else 'standard' if avg_quality_score >= 5 else 'enhanced'} due diligence and monitoring<br>
• Financial Reporting Reliability: {'High confidence' if high_quality_companies >= total_companies * 0.7 else 'Moderate confidence' if high_quality_companies >= total_companies * 0.4 else 'Heightened scrutiny recommended'} in reported financial results<br>
• Cash Flow Alignment: {'Strong alignment' if strong_cash_conversion >= total_companies * 0.6 else 'Moderate alignment' if strong_cash_conversion >= total_companies * 0.3 else 'Significant gaps'} between earnings and cash generation"""


# =============================================================================
# SECTION 3F HELPER FUNCTIONS: COMPREHENSIVE INSIGHTS
# =============================================================================

def _generate_comprehensive_financial_insights(
    financial_history: Dict[str, pd.DataFrame],
    growth_metrics: Dict[str, Dict],
    working_capital_analysis: Dict[str, Dict],
    capital_efficiency: Dict[str, Dict],
    earnings_quality: Dict[str, Dict],
    companies: Dict[str, str]
) -> Dict[str, str]:
    """Generate comprehensive financial insights and recommendations"""
    
    # Calculate key portfolio metrics
    total_companies = len(companies)
    
    # Financial strength assessment
    if earnings_quality:
        avg_quality = np.mean([m['quality_score'] for m in earnings_quality.values()])
        high_quality_count = sum(1 for m in earnings_quality.values() if m['quality_score'] >= 7)
    else:
        avg_quality = 5
        high_quality_count = 0
    
    if capital_efficiency:
        avg_roic = np.mean([m['roic'] for m in capital_efficiency.values()])
        value_creators = sum(1 for m in capital_efficiency.values() if m['value_creation'] == 'Creating Value')
    else:
        avg_roic = 10
        value_creators = 0
    
    if growth_metrics:
        avg_growth = np.mean([m['revenue_growth_1y'] for m in growth_metrics.values()])
        sustainable_growers = sum(1 for m in growth_metrics.values() if m['sustainability_rating'] in ['Excellent', 'Good'])
    else:
        avg_growth = 5
        sustainable_growers = 0
    
    # Generate insights
    strength_assessment = f"""<strong>Portfolio Financial Foundation Assessment:</strong><br>
• Overall Financial Health: {avg_quality:.1f}/10 average quality score with {high_quality_count}/{total_companies} companies rated as high quality<br>
• Capital Efficiency: {avg_roic:.1f}% average ROIC with {value_creators}/{total_companies} companies creating economic value<br>
• Growth Sustainability: {sustainable_growers}/{total_companies} companies demonstrating sustainable growth characteristics<br>
• Financial Stability: {'Strong' if high_quality_count >= total_companies * 0.6 and value_creators >= total_companies * 0.5 else 'Moderate' if high_quality_count >= total_companies * 0.4 else 'Weak'} foundation for long-term value creation<br><br>

<strong>Portfolio Strength Analysis:</strong><br>
• Risk Concentration: {'Low' if high_quality_count >= total_companies * 0.7 else 'Moderate' if high_quality_count >= total_companies * 0.4 else 'High'} financial risk concentration requiring {'minimal' if high_quality_count >= total_companies * 0.7 else 'standard' if high_quality_count >= total_companies * 0.4 else 'enhanced'} monitoring<br>
• Competitive Positioning: {'Strong' if avg_roic > 15 and avg_quality >= 7 else 'Solid' if avg_roic > 10 and avg_quality >= 5 else 'Challenged'} relative to industry standards<br>
• Value Creation Trajectory: {'Accelerating' if value_creators >= total_companies * 0.6 and avg_growth > 5 else 'Steady' if value_creators >= total_companies * 0.4 else 'Declining'} based on current metrics"""
    
    growth_profitability = f"""<strong>Growth & Profitability Dynamics Analysis:</strong><br>
• Revenue Growth Trajectory: {avg_growth:.1f}% average growth indicating {'strong' if avg_growth > 10 else 'moderate' if avg_growth > 5 else 'weak' if avg_growth > 0 else 'declining'} top-line momentum<br>
• Growth Quality Distribution: {sustainable_growers}/{total_companies} companies with sustainable growth models<br>
• Profitability Sustainability: Return on invested capital averaging {avg_roic:.1f}% {'above' if avg_roic > 15 else 'near' if avg_roic > 10 else 'below'} long-term expectations<br><br>

<strong>Growth-Profitability Balance:</strong><br>
• High-Quality Growers: {sum(1 for c in companies.keys() if c in growth_metrics and c in earnings_quality and growth_metrics[c]['sustainability_rating'] in ['Excellent', 'Good'] and earnings_quality[c]['quality_score'] >= 7)} companies combining growth with quality<br>
• Value Creation Consistency: {'Strong' if value_creators >= total_companies * 0.6 else 'Moderate' if value_creators >= total_companies * 0.4 else 'Weak'} track record of generating returns above cost of capital<br>
• Margin Sustainability: {'Stable to improving' if high_quality_count >= total_companies * 0.5 else 'Mixed performance' if high_quality_count >= total_companies * 0.3 else 'Under pressure'} based on historical evolution<br><br>

<strong>Strategic Growth Positioning:</strong><br>
• Investment Priority: {'Accelerate growth investments' if avg_roic > 15 and sustainable_growers >= total_companies * 0.5 else 'Optimize growth-profitability balance' if avg_roic > 10 else 'Focus on profitability improvement'} given current performance<br>
• Market Opportunity: {'Expand market presence' if avg_growth > 8 and avg_roic > 12 else 'Selective expansion' if avg_growth > 3 else 'Defend market position'} based on growth trajectory"""
    
    if working_capital_analysis:
        avg_wc_efficiency = np.mean([m['efficiency_score'] for m in working_capital_analysis.values()])
        efficient_wc_companies = sum(1 for m in working_capital_analysis.values() if m['efficiency_score'] >= 7)
    else:
        avg_wc_efficiency = 5
        efficient_wc_companies = 0
    
    capital_efficiency_text = f"""<strong>Capital Allocation & Efficiency Optimization:</strong><br>
• Working Capital Management: {avg_wc_efficiency:.1f}/10 efficiency score with {efficient_wc_companies}/{total_companies} companies demonstrating excellent working capital management<br>
• Return on Invested Capital: {avg_roic:.1f}% portfolio average {'exceeding' if avg_roic > 15 else 'meeting' if avg_roic > 12 else 'trailing'} long-term value creation thresholds<br>
• Capital Deployment Effectiveness: {value_creators}/{total_companies} companies generating positive economic value added<br><br>

<strong>Operational Efficiency Metrics:</strong><br>
• Cash Conversion Excellence: {efficient_wc_companies}/{total_companies} companies optimizing cash conversion cycles<br>
• Asset Utilization: {'Strong' if avg_roic > 15 else 'Moderate' if avg_roic > 10 else 'Weak'} asset turnover trends indicating operational leverage effectiveness<br>
• Investment Discipline: {'Strong' if value_creators >= total_companies * 0.6 else 'Moderate' if value_creators >= total_companies * 0.4 else 'Requires Improvement'} capital allocation discipline<br><br>

<strong>Capital Allocation Priorities:</strong><br>
• High-Return Investments: {'Expand' if avg_roic > 15 else 'Maintain' if avg_roic > 10 else 'Restructure'} capital deployment in highest-return opportunities<br>
• Working Capital Optimization: {'Maintain efficiency' if avg_wc_efficiency >= 7 else 'Improve conversion cycles' if avg_wc_efficiency >= 5 else 'Comprehensive restructuring'} focus areas<br>
• Shareholder Returns: {'Increase' if value_creators >= total_companies * 0.6 and avg_roic > 15 else 'Maintain' if value_creators >= total_companies * 0.4 else 'Preserve capital'} return policies"""
    
    quality_risk = f"""<strong>Financial Quality & Risk Assessment Framework:</strong><br>
• Earnings Quality Portfolio Score: {avg_quality:.1f}/10 indicating {'excellent' if avg_quality >= 8 else 'good' if avg_quality >= 6 else 'fair' if avg_quality >= 4 else 'poor'} overall earnings sustainability<br>
• High-Quality Concentration: {high_quality_count}/{total_companies} companies with superior earnings quality characteristics<br>
• Financial Risk Distribution: {'Conservative' if high_quality_count >= total_companies * 0.7 else 'Moderate' if high_quality_count >= total_companies * 0.4 else 'Aggressive'} portfolio risk profile<br><br>

<strong>Quality Risk Indicators:</strong><br>
• Accruals Management: {'Conservative' if avg_quality >= 7 else 'Moderate' if avg_quality >= 5 else 'Aggressive'} accounting conservatism across portfolio companies<br>
• Cash Flow Conversion: {'Strong' if sum(1 for m in earnings_quality.values() if m['cash_conversion'] >= 8) >= total_companies * 0.6 else 'Adequate' if sum(1 for m in earnings_quality.values() if m['cash_conversion'] >= 8) >= total_companies * 0.3 else 'Weak'} cash generation relative to reported earnings<br>
• Earnings Volatility: {'Low' if avg_quality >= 7 else 'Moderate' if avg_quality >= 5 else 'High'} earnings predictability and sustainability<br><br>

<strong>Risk Management Framework:</strong><br>
• Enhanced Due Diligence: {'Low priority' if high_quality_count >= total_companies * 0.7 else 'Standard protocols' if high_quality_count >= total_companies * 0.4 else 'Enhanced scrutiny required'} for earnings quality monitoring<br>
• Position Sizing: Weight allocation toward higher-quality earnings companies for risk-adjusted returns<br>
• Monitoring Priorities: {'Maintain quality standards' if avg_quality >= 7 else 'Improve quality metrics' if avg_quality >= 5 else 'Comprehensive quality enhancement program'} focus areas"""
    
    recommendations = f"""<strong>Strategic Financial Management Recommendations:</strong><br><br>

<strong>Immediate Priorities (0-6 months):</strong><br>
• Portfolio Rebalancing: {'Maintain current allocation' if high_quality_count >= total_companies * 0.6 and value_creators >= total_companies * 0.5 else 'Increase allocation to high-quality companies' if high_quality_count < total_companies * 0.5 else 'Enhanced capital efficiency focus'}<br>
• Performance Monitoring: Implement {'standard' if avg_quality >= 6 else 'enhanced'} financial quality tracking and early warning systems<br>
• Capital Allocation: {'Accelerate growth investments' if avg_roic > 15 and sustainable_growers >= total_companies * 0.5 else 'Optimize growth-profitability balance' if avg_roic > 10 else 'Focus on profitability improvement'}<br><br>

<strong>Medium-Term Strategic Focus (6-18 months):</strong><br>
• Quality Enhancement: {'Maintain excellence' if high_quality_count >= total_companies * 0.7 else 'Targeted improvements' if high_quality_count >= total_companies * 0.4 else 'Comprehensive quality program'} across portfolio companies<br>
• Growth Sustainability: Develop {'advanced' if sustainable_growers >= total_companies * 0.6 else 'standard' if sustainable_growers >= total_companies * 0.4 else 'fundamental'} growth quality assessment frameworks<br>
• Operational Efficiency: {'Maintain leadership' if avg_wc_efficiency >= 7 else 'Improve working capital management' if avg_wc_efficiency >= 5 else 'Restructure operational processes'} initiatives<br><br>

<strong>Long-Term Value Creation (18+ months):</strong><br>
• Competitive Positioning: Leverage financial strength for {'market leadership expansion' if avg_roic > 15 and avg_quality >= 7 else 'competitive position enhancement' if avg_roic > 10 else 'defensive positioning improvement'}<br>
• Innovation Investment: {'Increase R&D allocation' if sustainable_growers >= total_companies * 0.5 and avg_roic > 12 else 'Maintain innovation spending' if avg_roic > 8 else 'Optimize innovation ROI'} based on capital efficiency<br>
• Shareholder Value: {'Aggressive capital returns' if value_creators >= total_companies * 0.6 and avg_roic > 15 else 'Balanced return policy' if value_creators >= total_companies * 0.4 else 'Capital preservation focus'} strategy<br><br>

<strong>Success Metrics & KPIs:</strong><br>
• Target Financial Quality Score: {min(10, avg_quality + 1.5):.1f}/10 within 24 months<br>
• Target ROIC Improvement: {min(25, avg_roic + 3):.1f}% portfolio average within 36 months<br>
• Target Value Creation: {min(total_companies, value_creators + max(1, (total_companies - value_creators) // 2))} companies generating positive economic value added"""
    
    return {
        'strength_assessment': strength_assessment,
        'growth_profitability': growth_profitability,
        'capital_efficiency': capital_efficiency_text,
        'quality_risk': quality_risk,
        'recommendations': recommendations
    }


# =============================================================================
# HELPER FUNCTIONS: FINANCIAL HISTORY GENERATION
# =============================================================================

def _generate_comprehensive_financial_history(
    df: pd.DataFrame, 
    companies: Dict[str, str], 
    years: int
) -> Dict[str, pd.DataFrame]:
    """Generate comprehensive financial history with growth calculations"""
    
    financial_history = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year').copy()
        
        if company_data.empty:
            continue
        
        # Core financial metrics
        core_metrics = [
            'Year', 'revenue', 'grossProfit', 'operatingIncome', 'netIncome', 'ebitda', 'ebit',
            'operatingCashFlow', 'freeCashFlow', 'capitalExpenditure', 'cashAndCashEquivalents',
            'totalAssets', 'totalLiabilities', 'totalStockholdersEquity', 'totalDebt',
            'grossProfitMargin', 'operatingProfitMargin', 'netProfitMargin', 'ebitdaMargin'
        ]
        
        # Select available metrics
        available_metrics = [col for col in core_metrics if col in company_data.columns]
        history_df = company_data[available_metrics].copy()
        
        # Calculate growth rates for key metrics
        growth_metrics = ['revenue', 'netIncome', 'ebitda', 'operatingCashFlow', 'freeCashFlow', 
                         'totalAssets', 'totalStockholdersEquity']
        
        for metric in growth_metrics:
            if metric in history_df.columns:
                # Year-over-year growth
                history_df[f'{metric}_growth'] = history_df[metric].pct_change() * 100
                
                # 3-year CAGR (if enough data)
                if len(history_df) >= 4:
                    for i in range(3, len(history_df)):
                        current_val = history_df.iloc[i][metric]
                        three_year_ago = history_df.iloc[i-3][metric]
                        if (pd.notna(current_val) and pd.notna(three_year_ago) and current_val > 0 and three_year_ago > 0):
                            cagr_3y = ((current_val / three_year_ago) ** (1/3) - 1) * 100
                            history_df.loc[history_df.index[i], f'{metric}_cagr_3y'] = cagr_3y
        
        # Calculate additional derived metrics
        if 'revenue' in history_df.columns and 'totalAssets' in history_df.columns:
            history_df['asset_turnover'] = history_df['revenue'] / history_df['totalAssets']
        
        if 'netIncome' in history_df.columns and 'totalStockholdersEquity' in history_df.columns:
            history_df['roe'] = (history_df['netIncome'] / history_df['totalStockholdersEquity']) * 100
        
        if 'netIncome' in history_df.columns and 'totalAssets' in history_df.columns:
            history_df['roa'] = (history_df['netIncome'] / history_df['totalAssets']) * 100
        
        if 'totalDebt' in history_df.columns and 'totalStockholdersEquity' in history_df.columns:
            history_df['debt_to_equity'] = history_df['totalDebt'] / history_df['totalStockholdersEquity']
        
        financial_history[company_name] = history_df
    
    return financial_history


def _prepare_financial_history_display(history_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare financial history DataFrame for display"""
    
    # Limit to last 7 years
    recent_history = history_df.tail(7).copy()
    
    # Select key columns for display
    display_columns = {
        'Year': 'Year',
        'revenue': 'Revenue ($K)',
        'revenue_growth': 'Rev Growth %',
        'grossProfitMargin': 'Gross Margin %',
        'operatingProfitMargin': 'Op Margin %',
        'netProfitMargin': 'Net Margin %',
        'netIncome': 'Net Income ($K)',
        'operatingCashFlow': 'OCF ($K)',
        'freeCashFlow': 'FCF ($K)',
        'totalAssets': 'Total Assets ($K)',
        'roe': 'ROE %',
        'debt_to_equity': 'D/E Ratio'
    }
    
    # Build display DataFrame
    display_df = pd.DataFrame()
    
    for col, display_name in display_columns.items():
        if col in recent_history.columns:
            if col == 'Year':
                display_df[display_name] = recent_history[col].astype(int)
            elif col in ['revenue', 'netIncome', 'operatingCashFlow', 'freeCashFlow', 'totalAssets']:
                display_df[display_name] = recent_history[col].apply(
                    lambda x: f"${x/1000:,.0f}K" if pd.notna(x) else "—"
                )
            elif 'margin' in col.lower() or col == 'roe':
                if col.endswith('Margin'):
                    display_df[display_name] = recent_history[col].apply(
                        lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
                    )
                else:
                    display_df[display_name] = recent_history[col].apply(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "—"
                    )
            elif col == 'revenue_growth':
                display_df[display_name] = recent_history[col].apply(
                    lambda x: f"{x:+.1f}%" if pd.notna(x) else "—"
                )
            elif col == 'debt_to_equity':
                display_df[display_name] = recent_history[col].apply(
                    lambda x: f"{x:.2f}x" if pd.notna(x) else "—"
                )
            else:
                display_df[display_name] = recent_history[col].apply(
                    lambda x: f"{x:.1f}" if pd.notna(x) else "—"
                )
    
    return display_df


# =============================================================================
# HELPER FUNCTIONS: GROWTH METRICS
# =============================================================================

def _calculate_advanced_growth_metrics(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Calculate advanced growth quality metrics"""
    
    growth_metrics = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        metrics = {}
        
        # Basic growth rates
        latest = company_data.iloc[-1]
        previous = company_data.iloc[-2]
        
        # Revenue growth
        if pd.notna(latest.get('revenue')) and pd.notna(previous.get('revenue')) and previous['revenue'] > 0:
            metrics['revenue_growth_1y'] = ((latest['revenue'] - previous['revenue']) / previous['revenue']) * 100
        else:
            metrics['revenue_growth_1y'] = 0
        
        # Multi-year CAGR calculations
        if len(company_data) >= 4:
            # 3-year CAGR
            three_years_ago = company_data.iloc[-4]
            if pd.notna(latest.get('revenue')) and pd.notna(three_years_ago.get('revenue')) and three_years_ago['revenue'] > 0:
                metrics['revenue_cagr_3y'] = ((latest['revenue'] / three_years_ago['revenue']) ** (1/3) - 1) * 100
            else:
                metrics['revenue_cagr_3y'] = 0
        else:
            metrics['revenue_cagr_3y'] = 0
        
        if len(company_data) >= 6:
            # 5-year CAGR
            five_years_ago = company_data.iloc[-6]
            if pd.notna(latest.get('revenue')) and pd.notna(five_years_ago.get('revenue')) and five_years_ago['revenue'] > 0:
                metrics['revenue_cagr_5y'] = ((latest['revenue'] / five_years_ago['revenue']) ** (1/5) - 1) * 100
            else:
                metrics['revenue_cagr_5y'] = 0
        else:
            metrics['revenue_cagr_5y'] = 0
        
        # Growth stability (coefficient of variation of revenue growth)
        if len(company_data) >= 4:
            revenue_growth_rates = []
            for i in range(1, len(company_data)):
                current_rev = company_data.iloc[i]['revenue']
                prev_rev = company_data.iloc[i-1]['revenue']
                if pd.notna(current_rev) and pd.notna(prev_rev) and prev_rev > 0:
                    growth_rate = ((current_rev - prev_rev) / prev_rev) * 100
                    revenue_growth_rates.append(growth_rate)
            
            if len(revenue_growth_rates) >= 3:
                cv = np.std(revenue_growth_rates) / (abs(np.mean(revenue_growth_rates)) + 1)
                metrics['growth_stability'] = max(0, min(10, 10 - cv * 2))
            else:
                metrics['growth_stability'] = 5
        else:
            metrics['growth_stability'] = 5
        
        # EBITDA growth
        if pd.notna(latest.get('ebitda')) and pd.notna(previous.get('ebitda')) and previous['ebitda'] > 0:
            metrics['ebitda_growth'] = ((latest['ebitda'] - previous['ebitda']) / previous['ebitda']) * 100
        else:
            metrics['ebitda_growth'] = 0
        
        # FCF growth
        if pd.notna(latest.get('freeCashFlow')) and pd.notna(previous.get('freeCashFlow')) and previous['freeCashFlow'] > 0:
            metrics['fcf_growth'] = ((latest['freeCashFlow'] - previous['freeCashFlow']) / previous['freeCashFlow']) * 100
        else:
            metrics['fcf_growth'] = 0
        
        # Growth quality score (composite)
        revenue_score = min(10, max(0, 5 + metrics['revenue_growth_1y'] / 5))
        consistency_score = metrics['growth_stability']
        profitability_score = min(10, max(0, 5 + metrics['ebitda_growth'] / 10))
        
        metrics['growth_quality_score'] = (revenue_score * 0.4 + consistency_score * 0.3 + profitability_score * 0.3)
        
        # Sustainability rating
        if metrics['growth_quality_score'] >= 8:
            metrics['sustainability_rating'] = 'Excellent'
        elif metrics['growth_quality_score'] >= 6:
            metrics['sustainability_rating'] = 'Good'
        elif metrics['growth_quality_score'] >= 4:
            metrics['sustainability_rating'] = 'Fair'
        else:
            metrics['sustainability_rating'] = 'Poor'
        
        growth_metrics[company_name] = metrics
    
    return growth_metrics


def _prepare_growth_metrics_display(growth_metrics: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare growth metrics DataFrame for display"""
    
    rows = []
    
    for company_name, metrics in growth_metrics.items():
        rows.append({
            'Company': company_name,
            '1Y Rev Growth': f"{metrics['revenue_growth_1y']:.1f}%",
            '3Y CAGR': f"{metrics['revenue_cagr_3y']:.1f}%",
            '5Y CAGR': f"{metrics['revenue_cagr_5y']:.1f}%",
            'Growth Stability': f"{metrics['growth_stability']:.1f}/10",
            'EBITDA Growth': f"{metrics['ebitda_growth']:.1f}%",
            'FCF Growth': f"{metrics['fcf_growth']:.1f}%",
            'Quality Score': f"{metrics['growth_quality_score']:.1f}/10",
            'Sustainability': metrics['sustainability_rating']
        })
    
    return pd.DataFrame(rows)


# =============================================================================
# HELPER FUNCTIONS: ANALYSIS SUMMARIES
# =============================================================================

def _analyze_financial_trends(financial_history: Dict[str, pd.DataFrame], companies: Dict[str, str]) -> str:
    """Analyze financial trends across companies"""
    
    total_companies = len([h for h in financial_history.values() if not h.empty])
    
    if total_companies == 0:
        return "No financial data available for trend analysis."
    
    # Revenue growth trends
    positive_revenue_growth = 0
    avg_revenue_growth = []
    stable_margins = 0
    improving_margins = 0
    
    for company_name, history_df in financial_history.items():
        if history_df.empty or len(history_df) < 2:
            continue
            
        latest_data = history_df.iloc[-1]
        
        # Revenue growth
        if 'revenue_growth' in latest_data and pd.notna(latest_data['revenue_growth']):
            if latest_data['revenue_growth'] > 0:
                positive_revenue_growth += 1
            avg_revenue_growth.append(latest_data['revenue_growth'])
        
        # Margin trends (last 3 years)
        if len(history_df) >= 3 and 'netProfitMargin' in history_df.columns:
            recent_margins = history_df['netProfitMargin'].tail(3).dropna()
            if len(recent_margins) >= 2:
                margin_trend = recent_margins.iloc[-1] - recent_margins.iloc[0]
                if abs(margin_trend) < 0.01:
                    stable_margins += 1
                elif margin_trend > 0.01:
                    improving_margins += 1
    
    avg_growth = np.mean(avg_revenue_growth) if avg_revenue_growth else 0
    
    return f"""<strong>Financial Trend Analysis Summary:</strong><br>
• Revenue Growth Momentum: {positive_revenue_growth}/{total_companies} companies showing positive revenue growth<br>
• Average Revenue Growth: {avg_growth:.1f}% indicating {'strong' if avg_growth > 8 else 'moderate' if avg_growth > 3 else 'weak'} top-line expansion<br>
• Margin Stability: {stable_margins} companies with stable margins, {improving_margins} with improving profitability trends<br>
• Financial Health Trajectory: {'Positive' if positive_revenue_growth >= total_companies * 0.6 and avg_growth > 0 else 'Mixed' if positive_revenue_growth >= total_companies * 0.4 else 'Concerning'} based on growth and margin trends<br><br>
<strong>Portfolio Outlook:</strong> {'Growth acceleration expected' if avg_growth > 5 and improving_margins >= total_companies * 0.4 else 'Steady growth trajectory' if avg_growth > 0 and stable_margins >= total_companies * 0.5 else 'Growth challenges require attention'} based on historical performance trends"""


def _generate_growth_analysis_summary(growth_metrics: Dict[str, Dict]) -> str:
    """Generate growth analysis summary"""
    
    if not growth_metrics:
        return "Insufficient data for growth analysis."
    
    # Calculate portfolio statistics
    avg_1y_growth = np.mean([m['revenue_growth_1y'] for m in growth_metrics.values()])
    avg_3y_cagr = np.mean([m['revenue_cagr_3y'] for m in growth_metrics.values()])
    avg_stability = np.mean([m['growth_stability'] for m in growth_metrics.values()])
    
    high_quality_companies = sum(1 for m in growth_metrics.values() if m['growth_quality_score'] >= 7)
    total_companies = len(growth_metrics)
    
    return f"""<strong>Growth Quality Assessment Summary:</strong><br>
• Portfolio Growth Profile: {avg_1y_growth:.1f}% average 1-year revenue growth, {avg_3y_cagr:.1f}% 3-year CAGR<br>
• Growth Consistency: Average stability score of {avg_stability:.1f}/10 indicating {'highly consistent' if avg_stability >= 7 else 'moderately consistent' if avg_stability >= 5 else 'volatile'} growth patterns<br>
• Quality Distribution: {high_quality_companies}/{total_companies} companies rated as high-quality growth ({(high_quality_companies/total_companies)*100:.0f}%)<br><br>
<strong>Sustainability Outlook:</strong> {'Strong' if avg_stability >= 6 and high_quality_companies >= total_companies * 0.5 else 'Moderate' if avg_stability >= 4 else 'Concerning'} based on growth quality metrics<br><br>
<strong>Strategic Implications:</strong> {'Focus on sustaining high-quality growth momentum' if avg_stability >= 6 else 'Improve growth consistency and quality metrics' if avg_1y_growth > 0 else 'Address fundamental growth challenges'} for optimal portfolio performance"""