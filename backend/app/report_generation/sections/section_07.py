"""Section 7: Valuation Analysis"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_card,
    build_stat_grid,
    build_info_box,
    build_data_table,
    build_section_divider,
    build_plotly_chart,
    format_currency,
    format_percentage,
    format_number,
    build_enhanced_table,
    build_badge,
    build_score_badge
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 7: Valuation Analysis
    
    Comprehensive valuation assessment with:
    - Multi-period valuation analysis
    - Cross-company valuation matrix
    - Smart valuation buckets
    - Enterprise value deep dive
    - Analyst vs market valuation
    - Executive dashboard with actionable insights
    
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
        
        # Get additional data sources
        try:
            prices_df = collector.get_prices_daily()
        except:
            prices_df = pd.DataFrame()
        
        try:
            enterprise_values_df = collector.get_enterprise_values()
        except:
            enterprise_values_df = pd.DataFrame()
        
        try:
            analyst_estimates, analyst_targets = collector.get_analyst_estimates()
        except:
            analyst_estimates = pd.DataFrame()
            analyst_targets = pd.DataFrame()
        
        try:
            economic_df = collector.get_economic()
        except:
            economic_df = pd.DataFrame()
        
        try:
            profiles_df = collector.get_profiles()
        except:
            profiles_df = pd.DataFrame()
        
        # Build all subsections
        section_7a_html = _build_section_7a_multi_period_valuation(
            df, companies, prices_df, economic_df, profiles_df
        )
        
        section_7b_html = _build_section_7b_cross_company_valuation_matrix(
            df, companies, enterprise_values_df, analyst_targets, profiles_df
        )
        
        section_7c_html = _build_section_7c_smart_valuation_buckets(
            df, companies, profiles_df
        )
        
        section_7d_html = _build_section_7d_enterprise_value_deep_dive(
            df, companies, enterprise_values_df
        )
        
        section_7e_html = _build_section_7e_analyst_vs_market_valuation(
            df, companies, analyst_targets, prices_df
        )
        
        section_7f_html = _build_section_7f_executive_dashboard(
            df, companies, analyst_targets, profiles_df
        )
        
        # Combine all subsections
        content = f"""
        <div class="section-content-wrapper">
            {section_7a_html}
            {build_section_divider() if section_7b_html else ""}
            {section_7b_html}
            {build_section_divider() if section_7c_html else ""}
            {section_7c_html}
            {build_section_divider() if section_7d_html else ""}
            {section_7d_html}
            {build_section_divider() if section_7e_html else ""}
            {section_7e_html}
            {build_section_divider() if section_7f_html else ""}
            {section_7f_html}
        </div>
        """
        
        return generate_section_wrapper(7, "Valuation Analysis", content)
        
    except Exception as e:
        error_content = f"""
        <div class="section-content-wrapper">
            {build_info_box(
                f"<p><strong>Error generating Section 7:</strong></p><p>{str(e)}</p>",
                "danger",
                "Section Generation Error"
            )}
        </div>
        """
        return generate_section_wrapper(7, "Valuation Analysis", error_content)


# =============================================================================
# SUBSECTION 7A: MULTI-PERIOD VALUATION ANALYSIS
# =============================================================================

def _build_section_7a_multi_period_valuation(
    df: pd.DataFrame,
    companies: Dict[str, str],
    prices_df: pd.DataFrame,
    economic_df: pd.DataFrame,
    profiles_df: pd.DataFrame
) -> str:
    """Build Section 7A: Multi-Period Valuation Analysis"""
    
    html = """
    <div class="info-section">
        <h3>7A. Multi-Period Valuation Analysis</h3>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">
            Historical valuation trends, current positioning vs multi-year ranges, and market cycle correlation analysis
        </p>
    """
    
    # Calculate time series valuation metrics
    time_series_data = _calculate_time_series_valuation(df, companies, economic_df)
    
    if not time_series_data:
        html += build_info_box(
            "<p>Insufficient historical data for time series valuation analysis.</p>",
            "warning"
        )
        html += "</div>"
        return html
    
    # 7A.1: Current vs Historical Valuation Summary
    html += """
        <div style="margin-top: 30px;">
            <h4>7A.1 Current vs Historical Valuation Positioning</h4>
    """
    
    summary_cards = _create_valuation_summary_cards(time_series_data, companies)
    html += summary_cards
    
    # 7A.2: Detailed Time Series Table
    html += """
        <div style="margin-top: 40px;">
            <h4>7A.2 Historical Valuation Metrics by Company</h4>
    """
    
    time_series_table = _create_time_series_table(time_series_data, companies)
    html += time_series_table
    
    # 7A.3: Valuation Trend Analysis
    html += """
        <div style="margin-top: 40px;">
            <h4>7A.3 Valuation Trend & Consistency Analysis</h4>
    """
    
    trend_analysis_html = _create_trend_analysis(time_series_data, companies)
    html += trend_analysis_html
    
    # 7A.4: Interactive Charts
    html += """
        <div style="margin-top: 40px;">
            <h4>7A.4 Valuation Evolution Visualizations</h4>
    """
    
    charts_html = _create_time_series_charts(df, companies, time_series_data, economic_df)
    html += charts_html
    
    # 7A.5: Key Insights
    html += """
        <div style="margin-top: 40px;">
            <h4>7A.5 Time Series Valuation Insights</h4>
    """
    
    insights_html = _create_time_series_insights(time_series_data, companies, economic_df)
    html += insights_html
    
    html += "</div></div>"
    
    return html


def _calculate_time_series_valuation(
    df: pd.DataFrame,
    companies: Dict[str, str],
    economic_df: pd.DataFrame
) -> Dict[str, Dict]:
    """Calculate time series valuation metrics for each company"""
    
    time_series_data = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 2:
            continue
        
        metrics = {}
        
        # P/E Ratio Analysis
        pe_series = company_data['priceToEarningsRatio'].dropna()
        if len(pe_series) >= 2:
            metrics['current_pe'] = pe_series.iloc[-1]
            metrics['historical_pe_avg'] = pe_series.iloc[:-1].mean()
            metrics['historical_pe_median'] = pe_series.iloc[:-1].median()
            metrics['historical_pe_min'] = pe_series.iloc[:-1].min()
            metrics['historical_pe_max'] = pe_series.iloc[:-1].max()
            metrics['pe_percentile'] = (pe_series < metrics['current_pe']).sum() / len(pe_series) * 100
            metrics['pe_vs_history'] = ((metrics['current_pe'] - metrics['historical_pe_avg']) / 
                                       metrics['historical_pe_avg'] * 100) if metrics['historical_pe_avg'] > 0 else 0
            metrics['pe_volatility'] = pe_series.std()
            metrics['pe_cv'] = metrics['pe_volatility'] / metrics['historical_pe_avg'] if metrics['historical_pe_avg'] > 0 else 0
        else:
            metrics['current_pe'] = 0
            metrics['historical_pe_avg'] = 0
            metrics['pe_percentile'] = 50
            metrics['pe_vs_history'] = 0
            metrics['pe_volatility'] = 0
            metrics['pe_cv'] = 0
        
        # P/B Ratio Analysis
        pb_series = company_data['priceToBookRatio'].dropna()
        if len(pb_series) >= 2:
            metrics['current_pb'] = pb_series.iloc[-1]
            metrics['historical_pb_avg'] = pb_series.iloc[:-1].mean()
            metrics['historical_pb_median'] = pb_series.iloc[:-1].median()
            metrics['pb_percentile'] = (pb_series < metrics['current_pb']).sum() / len(pb_series) * 100
            metrics['pb_vs_history'] = ((metrics['current_pb'] - metrics['historical_pb_avg']) / 
                                       metrics['historical_pb_avg'] * 100) if metrics['historical_pb_avg'] > 0 else 0
        else:
            metrics['current_pb'] = 0
            metrics['historical_pb_avg'] = 0
            metrics['pb_percentile'] = 50
            metrics['pb_vs_history'] = 0
        
        # EV/EBITDA Analysis
        ev_ebitda_series = company_data['evToEBITDA'].dropna()
        if len(ev_ebitda_series) >= 2:
            metrics['current_ev_ebitda'] = ev_ebitda_series.iloc[-1]
            metrics['historical_ev_ebitda_avg'] = ev_ebitda_series.iloc[:-1].mean()
            metrics['ev_ebitda_percentile'] = (ev_ebitda_series < metrics['current_ev_ebitda']).sum() / len(ev_ebitda_series) * 100
            metrics['ev_ebitda_vs_history'] = ((metrics['current_ev_ebitda'] - metrics['historical_ev_ebitda_avg']) / 
                                              metrics['historical_ev_ebitda_avg'] * 100) if metrics['historical_ev_ebitda_avg'] > 0 else 0
        else:
            metrics['current_ev_ebitda'] = 0
            metrics['historical_ev_ebitda_avg'] = 0
            metrics['ev_ebitda_percentile'] = 50
            metrics['ev_ebitda_vs_history'] = 0
        
        # Valuation Trend Assessment
        if len(pe_series) >= 3:
            recent_pe_trend = pe_series.tail(3).mean()
            earlier_pe_trend = pe_series.head(max(1, len(pe_series) - 3)).mean() if len(pe_series) > 3 else pe_series.mean()
            
            if recent_pe_trend > earlier_pe_trend * 1.15:
                metrics['valuation_trend'] = 'Expanding'
                metrics['trend_direction'] = 1
            elif recent_pe_trend < earlier_pe_trend * 0.85:
                metrics['valuation_trend'] = 'Contracting'
                metrics['trend_direction'] = -1
            else:
                metrics['valuation_trend'] = 'Stable'
                metrics['trend_direction'] = 0
        else:
            metrics['valuation_trend'] = 'Limited Data'
            metrics['trend_direction'] = 0
        
        # Valuation Consistency Score
        consistency_components = []
        if metrics['pe_cv'] > 0:
            consistency_score = max(0, 10 - metrics['pe_cv'] * 10)
            consistency_components.append(consistency_score)
        
        if len(pb_series) >= 2:
            pb_cv = pb_series.std() / (pb_series.mean() + 0.1)
            consistency_components.append(max(0, 10 - pb_cv * 10))
        
        metrics['valuation_consistency'] = np.mean(consistency_components) if consistency_components else 5.0
        
        # Market Correlation (if S&P 500 data available)
        if not economic_df.empty and 'S&P_500_Index' in economic_df.columns:
            try:
                company_years = company_data['Year'].values
                market_years = economic_df['Year'].values
                overlap_years = np.intersect1d(company_years, market_years)
                
                if len(overlap_years) >= 3:
                    company_pe_overlap = []
                    market_overlap = []
                    
                    for year in overlap_years:
                        pe_val = company_data[company_data['Year'] == year]['priceToEarningsRatio'].iloc[0]
                        market_val = economic_df[economic_df['Year'] == year]['S&P_500_Index'].iloc[0]
                        
                        if pd.notna(pe_val) and pd.notna(market_val):
                            company_pe_overlap.append(pe_val)
                            market_overlap.append(market_val)
                    
                    if len(company_pe_overlap) >= 3:
                        correlation = np.corrcoef(company_pe_overlap, market_overlap)[0, 1]
                        metrics['market_correlation'] = correlation if not np.isnan(correlation) else 0
                    else:
                        metrics['market_correlation'] = 0
                else:
                    metrics['market_correlation'] = 0
            except:
                metrics['market_correlation'] = 0
        else:
            metrics['market_correlation'] = 0
        
        # Valuation positioning classification
        avg_percentile = (metrics['pe_percentile'] + metrics['pb_percentile'] + 
                         metrics['ev_ebitda_percentile']) / 3
        
        if avg_percentile <= 20:
            metrics['valuation_position'] = 'Deep Discount'
        elif avg_percentile <= 40:
            metrics['valuation_position'] = 'Below Average'
        elif avg_percentile <= 60:
            metrics['valuation_position'] = 'Fair Value'
        elif avg_percentile <= 80:
            metrics['valuation_position'] = 'Above Average'
        else:
            metrics['valuation_position'] = 'Premium'
        
        time_series_data[company_name] = metrics
    
    return time_series_data


def _create_valuation_summary_cards(time_series_data: Dict, companies: Dict) -> str:
    """Create summary stat cards for valuation positioning"""
    
    total_companies = len(time_series_data)
    if total_companies == 0:
        return ""
    
    # Calculate portfolio metrics
    avg_pe_vs_history = np.mean([m['pe_vs_history'] for m in time_series_data.values()])
    
    deep_discount_count = sum(1 for m in time_series_data.values() 
                             if m['valuation_position'] == 'Deep Discount')
    below_avg_count = sum(1 for m in time_series_data.values() 
                         if m['valuation_position'] == 'Below Average')
    
    expanding_count = sum(1 for m in time_series_data.values() 
                         if m['valuation_trend'] == 'Expanding')
    
    high_consistency_count = sum(1 for m in time_series_data.values() 
                                if m['valuation_consistency'] >= 7)
    
    # Create cards
    cards = [
        {
            "label": "Portfolio P/E vs History",
            "value": f"{avg_pe_vs_history:+.1f}%",
            "description": f"{'Premium' if avg_pe_vs_history > 10 else 'Discount' if avg_pe_vs_history < -10 else 'Fair'} valuation vs historical norms",
            "type": "warning" if avg_pe_vs_history > 15 else "success" if avg_pe_vs_history < -15 else "info"
        },
        {
            "label": "Value Opportunities",
            "value": f"{deep_discount_count + below_avg_count}/{total_companies}",
            "description": f"{deep_discount_count} deep discount, {below_avg_count} below average",
            "type": "success" if (deep_discount_count + below_avg_count) >= total_companies * 0.5 else "info"
        },
        {
            "label": "Valuation Trends",
            "value": f"{expanding_count}/{total_companies}",
            "description": f"Companies with expanding valuations",
            "type": "warning" if expanding_count >= total_companies * 0.6 else "info"
        },
        {
            "label": "Consistency Score",
            "value": f"{high_consistency_count}/{total_companies}",
            "description": "Companies with stable valuation patterns (7+ score)",
            "type": "success" if high_consistency_count >= total_companies * 0.6 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_time_series_table(time_series_data: Dict, companies: Dict) -> str:
    """Create detailed time series valuation table"""
    
    if not time_series_data:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, metrics in time_series_data.items():
        table_data.append({
            'Company': company_name,
            'Current P/E': f"{metrics['current_pe']:.1f}x",
            'Historical P/E Avg': f"{metrics['historical_pe_avg']:.1f}x",
            'P/E vs History': f"{metrics['pe_vs_history']:+.1f}%",
            'P/E Percentile': f"{metrics['pe_percentile']:.0f}th",
            'Current P/B': f"{metrics['current_pb']:.1f}x",
            'P/B vs History': f"{metrics['pb_vs_history']:+.1f}%",
            'EV/EBITDA': f"{metrics['current_ev_ebitda']:.1f}x",
            'Valuation Position': metrics['valuation_position'],
            'Consistency': f"{metrics['valuation_consistency']:.1f}/10"
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding for valuation position
    def position_color(val):
        if 'Deep Discount' in val:
            return 'excellent'
        elif 'Below Average' in val:
            return 'good'
        elif 'Fair Value' in val:
            return 'neutral'
        elif 'Above Average' in val:
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'Valuation Position': position_color
    }
    
    return build_enhanced_table(
        df_table,
        table_id="time-series-valuation-table",
        color_columns=color_columns,
        sortable=True,
        searchable=True
    )


def _create_trend_analysis(time_series_data: Dict, companies: Dict) -> str:
    """Create valuation trend analysis section"""
    
    if not time_series_data:
        return ""
    
    # Group by trend
    expanding = [k for k, v in time_series_data.items() if v['valuation_trend'] == 'Expanding']
    contracting = [k for k, v in time_series_data.items() if v['valuation_trend'] == 'Contracting']
    stable = [k for k, v in time_series_data.items() if v['valuation_trend'] == 'Stable']
    
    total = len(time_series_data)
    
    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b;">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">⬆️ Expanding Valuations</h5>
            <div style="font-size: 2rem; font-weight: 700; color: #f59e0b; margin-bottom: 10px;">
                {len(expanding)}/{total}
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                Companies trading at expanding P/E multiples vs historical averages
            </p>
            {f'<div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-tertiary);">{", ".join(expanding[:3])}{"..." if len(expanding) > 3 else ""}</div>' if expanding else ''}
        </div>
        
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid #10b981;">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">⬇️ Contracting Valuations</h5>
            <div style="font-size: 2rem; font-weight: 700; color: #10b981; margin-bottom: 10px;">
                {len(contracting)}/{total}
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                Companies with compressing multiples - potential value opportunities
            </p>
            {f'<div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-tertiary);">{", ".join(contracting[:3])}{"..." if len(contracting) > 3 else ""}</div>' if contracting else ''}
        </div>
        
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">➡️ Stable Valuations</h5>
            <div style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin-bottom: 10px;">
                {len(stable)}/{total}
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                Companies maintaining consistent valuation ranges
            </p>
            {f'<div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-tertiary);">{", ".join(stable[:3])}{"..." if len(stable) > 3 else ""}</div>' if stable else ''}
        </div>
    </div>
    """
    
    return html


def _create_time_series_charts(
    df: pd.DataFrame,
    companies: Dict,
    time_series_data: Dict,
    economic_df: pd.DataFrame
) -> str:
    """Create time series valuation charts"""
    
    charts_html = ""
    
    # Chart 1: P/E Evolution Over Time
    chart1_html = _create_pe_evolution_chart(df, companies)
    if chart1_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">P/E Ratio Evolution Over Time</h5>
            {chart1_html}
        </div>
        """
    
    # Chart 2: Current vs Historical P/E Comparison
    chart2_html = _create_current_vs_historical_chart(time_series_data, companies)
    if chart2_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Current vs Historical P/E Comparison</h5>
            {chart2_html}
        </div>
        """
    
    # Chart 3: Valuation Percentile Distribution
    chart3_html = _create_percentile_distribution_chart(time_series_data, companies)
    if chart3_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Valuation Percentile Distribution</h5>
            {chart3_html}
        </div>
        """
    
    # Chart 4: Market Correlation Analysis
    if not economic_df.empty:
        chart4_html = _create_market_correlation_chart(time_series_data, companies)
        if chart4_html:
            charts_html += f"""
            <div style="margin-bottom: 30px;">
                <h5 style="color: var(--text-primary); margin-bottom: 15px;">Market Correlation vs P/E Percentile</h5>
                {chart4_html}
            </div>
            """
    
    return charts_html


def _create_pe_evolution_chart(df: pd.DataFrame, companies: Dict) -> str:
    """Create P/E evolution time series chart"""
    
    traces = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) >= 2:
            pe_data = company_data[['Year', 'priceToEarningsRatio']].dropna()
            
            if len(pe_data) >= 2:
                trace = {
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'x': pe_data['Year'].tolist(),
                    'y': pe_data['priceToEarningsRatio'].tolist(),
                    'name': company_name,
                    'line': {'color': colors[i % len(colors)], 'width': 3},
                    'marker': {'size': 8},
                    'hovertemplate': '<b>%{fullData.name}</b><br>Year: %{x}<br>P/E: %{y:.1f}x<extra></extra>'
                }
                traces.append(trace)
    
    if not traces:
        return ""
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Year', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'yaxis': {'title': 'P/E Ratio', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'hovermode': 'closest',
            'showlegend': True,
            'legend': {'x': 1.02, 'y': 1, 'xanchor': 'left'},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="pe-evolution-chart", height=500)


def _create_current_vs_historical_chart(time_series_data: Dict, companies: Dict) -> str:
    """Create current vs historical P/E comparison chart"""
    
    if not time_series_data:
        return ""
    
    companies_list = list(time_series_data.keys())
    current_pe = [time_series_data[c]['current_pe'] for c in companies_list]
    historical_pe = [time_series_data[c]['historical_pe_avg'] for c in companies_list]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'x': companies_list,
                'y': current_pe,
                'name': 'Current P/E',
                'marker': {'color': '#667eea'},
                'hovertemplate': '<b>%{x}</b><br>Current P/E: %{y:.1f}x<extra></extra>'
            },
            {
                'type': 'bar',
                'x': companies_list,
                'y': historical_pe,
                'name': 'Historical Avg P/E',
                'marker': {'color': '#43e97b'},
                'hovertemplate': '<b>%{x}</b><br>Historical Avg: %{y:.1f}x<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': '', 'tickangle': -45},
            'yaxis': {'title': 'P/E Ratio', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'barmode': 'group',
            'hovermode': 'closest',
            'showlegend': True,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="current-vs-historical-chart", height=500)


def _create_percentile_distribution_chart(time_series_data: Dict, companies: Dict) -> str:
    """Create valuation percentile distribution chart"""
    
    if not time_series_data:
        return ""
    
    companies_list = list(time_series_data.keys())
    pe_percentiles = [time_series_data[c]['pe_percentile'] for c in companies_list]
    
    # Create histogram bins
    bins = [0, 20, 40, 60, 80, 100]
    hist, _ = np.histogram(pe_percentiles, bins=bins)
    bin_labels = ['0-20th<br>(Deep Discount)', '20-40th<br>(Below Avg)', 
                  '40-60th<br>(Fair Value)', '60-80th<br>(Above Avg)', '80-100th<br>(Premium)']
    bin_colors = ['#10b981', '#43e97b', '#3b82f6', '#f59e0b', '#ef4444']
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': bin_labels,
            'y': hist.tolist(),
            'marker': {'color': bin_colors},
            'text': hist.tolist(),
            'textposition': 'auto',
            'hovertemplate': '<b>%{x}</b><br>Companies: %{y}<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Valuation Percentile Range'},
            'yaxis': {'title': 'Number of Companies', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="percentile-distribution-chart", height=400)


def _create_market_correlation_chart(time_series_data: Dict, companies: Dict) -> str:
    """Create market correlation vs P/E percentile scatter chart"""
    
    if not time_series_data:
        return ""
    
    companies_list = list(time_series_data.keys())
    correlations = [time_series_data[c]['market_correlation'] for c in companies_list]
    percentiles = [time_series_data[c]['pe_percentile'] for c in companies_list]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': correlations,
            'y': percentiles,
            'text': [c[:8] for c in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': percentiles,
                'colorscale': [[0, '#10b981'], [0.5, '#3b82f6'], [1, '#ef4444']],
                'showscale': True,
                'colorbar': {'title': 'P/E<br>Percentile'}
            },
            'hovertemplate': '<b>%{text}</b><br>Correlation: %{x:.2f}<br>Percentile: %{y:.0f}th<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Market Correlation', 'gridcolor': 'rgba(128,128,128,0.2)', 'zeroline': True},
            'yaxis': {'title': 'P/E Historical Percentile', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="market-correlation-chart", height=500)


def _create_time_series_insights(
    time_series_data: Dict,
    companies: Dict,
    economic_df: pd.DataFrame
) -> str:
    """Generate time series valuation insights"""
    
    if not time_series_data:
        return ""
    
    total_companies = len(time_series_data)
    avg_pe_vs_history = np.mean([m['pe_vs_history'] for m in time_series_data.values()])
    
    deep_discount = sum(1 for m in time_series_data.values() 
                       if m['valuation_position'] == 'Deep Discount')
    below_avg = sum(1 for m in time_series_data.values() 
                   if m['valuation_position'] == 'Below Average')
    premium = sum(1 for m in time_series_data.values() 
                 if m['valuation_position'] == 'Premium')
    
    expanding = sum(1 for m in time_series_data.values() 
                   if m['valuation_trend'] == 'Expanding')
    high_consistency = sum(1 for m in time_series_data.values() 
                         if m['valuation_consistency'] >= 7)
    
    # Generate insight text
    insight_text = f"""
    <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #667eea;">
        <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">💡 Key Time Series Insights</h5>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Portfolio Valuation Profile:</strong> 
            Current portfolio valuations are {abs(avg_pe_vs_history):.1f}% {'above' if avg_pe_vs_history > 0 else 'below'} 
            historical P/E averages, indicating a {'premium' if avg_pe_vs_history > 10 else 'discount' if avg_pe_vs_history < -10 else 'fair'} 
            valuation environment.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Value Opportunities:</strong> 
            {deep_discount + below_avg} out of {total_companies} companies ({(deep_discount + below_avg)/total_companies*100:.0f}%) 
            are trading at {'attractive' if (deep_discount + below_avg) >= total_companies * 0.5 else 'moderate'} valuations relative to 
            their own history, with {deep_discount} in deep discount territory.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Valuation Dynamics:</strong> 
            {expanding}/{total_companies} companies show expanding valuations, suggesting 
            {'broad market optimism' if expanding >= total_companies * 0.6 else 'selective market enthusiasm' if expanding >= total_companies * 0.4 else 'market caution'}.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 0;">
            <strong style="color: var(--text-primary);">Consistency Profile:</strong> 
            {high_consistency}/{total_companies} companies demonstrate high valuation consistency (7+ score), 
            indicating {'stable' if high_consistency >= total_companies * 0.6 else 'moderate' if high_consistency >= total_companies * 0.4 else 'volatile'} 
            valuation patterns across the portfolio.
        </p>
    </div>
    """
    
    return insight_text


# =============================================================================
# SUBSECTION 7B: CROSS-COMPANY VALUATION MATRIX
# =============================================================================

def _build_section_7b_cross_company_valuation_matrix(
    df: pd.DataFrame,
    companies: Dict[str, str],
    enterprise_values_df: pd.DataFrame,
    analyst_targets: pd.DataFrame,
    profiles_df: pd.DataFrame
) -> str:
    """Build Section 7B: Cross-Company Valuation Matrix"""
    
    html = """
    <div class="info-section">
        <h3>7B. Cross-Company Valuation Matrix</h3>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">
            Multi-metric valuation rankings, growth-adjusted valuations, and comprehensive peer comparison analysis
        </p>
    """
    
    # Calculate cross-company valuation metrics
    valuation_matrix = _calculate_valuation_matrix(df, companies, analyst_targets, profiles_df)
    
    if not valuation_matrix:
        html += build_info_box(
            "<p>Insufficient data for cross-company valuation analysis.</p>",
            "warning"
        )
        html += "</div>"
        return html
    
    # 7B.1: Valuation Ranking Summary
    html += """
        <div style="margin-top: 30px;">
            <h4>7B.1 Valuation Ranking Summary</h4>
    """
    
    ranking_cards = _create_valuation_ranking_cards(valuation_matrix, companies)
    html += ranking_cards
    
    # 7B.2: Comprehensive Valuation Matrix Table
    html += """
        <div style="margin-top: 40px;">
            <h4>7B.2 Multi-Metric Valuation Matrix</h4>
    """
    
    matrix_table = _create_valuation_matrix_table(valuation_matrix, companies)
    html += matrix_table
    
    # 7B.3: Growth-Adjusted Valuations
    html += """
        <div style="margin-top: 40px;">
            <h4>7B.3 Growth-Adjusted Valuation Metrics</h4>
    """
    
    growth_adjusted_html = _create_growth_adjusted_section(valuation_matrix, companies)
    html += growth_adjusted_html
    
    # 7B.4: Valuation Matrix Visualizations
    html += """
        <div style="margin-top: 40px;">
            <h4>7B.4 Cross-Company Valuation Visualizations</h4>
    """
    
    charts_html = _create_valuation_matrix_charts(valuation_matrix, companies)
    html += charts_html
    
    # 7B.5: Peer Positioning Insights
    html += """
        <div style="margin-top: 40px;">
            <h4>7B.5 Peer Positioning Analysis</h4>
    """
    
    insights_html = _create_valuation_matrix_insights(valuation_matrix, companies)
    html += insights_html
    
    html += "</div></div>"
    
    return html


def _calculate_valuation_matrix(
    df: pd.DataFrame,
    companies: Dict[str, str],
    analyst_targets: pd.DataFrame,
    profiles_df: pd.DataFrame
) -> Dict[str, Dict]:
    """Calculate comprehensive cross-company valuation metrics"""
    
    valuation_matrix = {}
    all_metrics = []
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core valuation ratios
        metrics['pe_ratio'] = latest.get('priceToEarningsRatio', 0)
        metrics['pb_ratio'] = latest.get('priceToBookRatio', 0)
        metrics['ps_ratio'] = latest.get('priceToSalesRatio', 0)
        metrics['ev_ebitda'] = latest.get('evToEBITDA', 0)
        metrics['ev_sales'] = latest.get('evToSales', 0)
        metrics['p_fcf'] = latest.get('priceToFreeCashFlowRatio', 0)
        
        # Growth metrics for PEG calculation
        if len(company_data) >= 2:
            current_revenue = latest.get('revenue', 0)
            previous_revenue = company_data.iloc[-2].get('revenue', 0)
            revenue_growth = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            metrics['revenue_growth'] = revenue_growth
            
            current_earnings = latest.get('netIncome', 0)
            previous_earnings = company_data.iloc[-2].get('netIncome', 0)
            earnings_growth = ((current_earnings - previous_earnings) / previous_earnings * 100) if previous_earnings > 0 else 0
            metrics['earnings_growth'] = earnings_growth
        else:
            metrics['revenue_growth'] = 0
            metrics['earnings_growth'] = 0
        
        # PEG Ratio (P/E to Growth)
        if metrics['pe_ratio'] > 0 and metrics['earnings_growth'] > 0:
            metrics['peg_ratio'] = metrics['pe_ratio'] / metrics['earnings_growth']
        else:
            metrics['peg_ratio'] = 0
        
        # Quality metrics
        metrics['roe'] = latest.get('returnOnEquity', 0)
        metrics['roic'] = latest.get('returnOnInvestedCapital', 0)
        metrics['roa'] = latest.get('returnOnAssets', 0)
        metrics['net_margin'] = latest.get('netProfitMargin', 0)
        metrics['fcf_margin'] = (latest.get('freeCashFlow', 0) / latest.get('revenue', 1) * 100) if latest.get('revenue', 0) > 0 else 0
        
        # Analyst support
        if not analyst_targets.empty:
            analyst_data = analyst_targets[analyst_targets['Company'] == company_name]
            if not analyst_data.empty:
                target_data = analyst_data.iloc[-1]
                current_price = latest.get('price', 0)
                target_consensus = target_data.get('targetConsensus', 0)
                
                if current_price > 0 and target_consensus > 0:
                    upside_potential = ((target_consensus - current_price) / current_price) * 100
                    metrics['analyst_upside'] = upside_potential
                    metrics['target_high'] = target_data.get('targetHigh', 0)
                    metrics['target_low'] = target_data.get('targetLow', 0)
                    
                    if upside_potential > 20:
                        metrics['analyst_signal'] = 'Strong Buy'
                    elif upside_potential > 10:
                        metrics['analyst_signal'] = 'Buy'
                    elif upside_potential > 0:
                        metrics['analyst_signal'] = 'Hold'
                    else:
                        metrics['analyst_signal'] = 'Underperform'
                else:
                    metrics['analyst_upside'] = 0
                    metrics['analyst_signal'] = 'No Target'
            else:
                metrics['analyst_upside'] = 0
                metrics['analyst_signal'] = 'No Coverage'
        else:
            metrics['analyst_upside'] = 0
            metrics['analyst_signal'] = 'No Coverage'
        
        # Sector/Industry info
        if not profiles_df.empty:
            profile = profiles_df[profiles_df['Company'] == company_name]
            if not profile.empty:
                metrics['sector'] = profile.iloc[0].get('sector', 'Unknown')
                metrics['industry'] = profile.iloc[0].get('industry', 'Unknown')
                metrics['market_cap'] = profile.iloc[0].get('marketCap', 0)
            else:
                metrics['sector'] = 'Unknown'
                metrics['industry'] = 'Unknown'
                metrics['market_cap'] = latest.get('marketCap', 0)
        else:
            metrics['sector'] = 'Unknown'
            metrics['industry'] = 'Unknown'
            metrics['market_cap'] = latest.get('marketCap', 0)
        
        all_metrics.append((company_name, metrics))
        valuation_matrix[company_name] = metrics
    
    # Calculate rankings and percentiles
    if all_metrics:
        # P/E rankings (lower is better)
        pe_values = [(name, m['pe_ratio']) for name, m in all_metrics if m['pe_ratio'] > 0]
        pe_values.sort(key=lambda x: x[1])
        
        # P/B rankings
        pb_values = [(name, m['pb_ratio']) for name, m in all_metrics if m['pb_ratio'] > 0]
        pb_values.sort(key=lambda x: x[1])
        
        # EV/EBITDA rankings
        ev_ebitda_values = [(name, m['ev_ebitda']) for name, m in all_metrics if m['ev_ebitda'] > 0]
        ev_ebitda_values.sort(key=lambda x: x[1])
        
        # PEG rankings (lower is better)
        peg_values = [(name, m['peg_ratio']) for name, m in all_metrics if 0 < m['peg_ratio'] < 10]
        peg_values.sort(key=lambda x: x[1])
        
        # Calculate percentile ranks
        for company_name in valuation_matrix.keys():
            metrics = valuation_matrix[company_name]
            
            # PE percentile
            pe_rank = next((i for i, (name, _) in enumerate(pe_values) if name == company_name), len(pe_values))
            metrics['pe_percentile'] = (pe_rank / len(pe_values)) * 100 if pe_values else 50
            metrics['pe_rank'] = pe_rank + 1 if pe_values else 0
            
            # PB percentile
            pb_rank = next((i for i, (name, _) in enumerate(pb_values) if name == company_name), len(pb_values))
            metrics['pb_percentile'] = (pb_rank / len(pb_values)) * 100 if pb_values else 50
            
            # EV/EBITDA percentile
            ev_rank = next((i for i, (name, _) in enumerate(ev_ebitda_values) if name == company_name), len(ev_ebitda_values))
            metrics['ev_percentile'] = (ev_rank / len(ev_ebitda_values)) * 100 if ev_ebitda_values else 50
            
            # PEG percentile
            peg_rank = next((i for i, (name, _) in enumerate(peg_values) if name == company_name), len(peg_values))
            metrics['peg_percentile'] = (peg_rank / len(peg_values)) * 100 if peg_values else 50
            
            # Composite percentile
            avg_percentile = (metrics['pe_percentile'] + metrics['pb_percentile'] + 
                            metrics['ev_percentile']) / 3
            metrics['composite_percentile'] = avg_percentile
            
            # Valuation score (0-10, lower percentile = higher score)
            base_score = 10 - (avg_percentile / 10)
            
            # Quality adjustment
            quality_score = (metrics['roe'] + metrics['roic'] + metrics['roa']) / 3
            quality_bonus = min(2, max(-2, (quality_score - 10) / 10))
            
            # Growth adjustment
            growth_bonus = min(2, max(-2, metrics['revenue_growth'] / 10))
            
            metrics['valuation_score'] = max(0, min(10, base_score + quality_bonus + growth_bonus))
            
            # Value category
            if avg_percentile <= 20:
                metrics['value_category'] = 'Deep Value'
            elif avg_percentile <= 40:
                metrics['value_category'] = 'Value'
            elif avg_percentile <= 60:
                metrics['value_category'] = 'Fair Value'
            elif avg_percentile <= 80:
                metrics['value_category'] = 'Growth Premium'
            else:
                metrics['value_category'] = 'Expensive'
            
            # Investment recommendation
            if metrics['valuation_score'] >= 8 and metrics['analyst_upside'] > 15:
                metrics['recommendation'] = 'Strong Buy'
            elif metrics['valuation_score'] >= 7:
                metrics['recommendation'] = 'Buy'
            elif metrics['valuation_score'] >= 5:
                metrics['recommendation'] = 'Hold'
            elif metrics['valuation_score'] >= 3:
                metrics['recommendation'] = 'Reduce'
            else:
                metrics['recommendation'] = 'Sell'
    
    return valuation_matrix


def _create_valuation_ranking_cards(valuation_matrix: Dict, companies: Dict) -> str:
    """Create valuation ranking summary cards"""
    
    total_companies = len(valuation_matrix)
    if total_companies == 0:
        return ""
    
    # Calculate portfolio metrics
    avg_valuation_score = np.mean([m['valuation_score'] for m in valuation_matrix.values()])
    
    deep_value_count = sum(1 for m in valuation_matrix.values() 
                          if m['value_category'] == 'Deep Value')
    value_count = sum(1 for m in valuation_matrix.values() 
                     if m['value_category'] == 'Value')
    expensive_count = sum(1 for m in valuation_matrix.values() 
                         if m['value_category'] == 'Expensive')
    
    strong_buy_count = sum(1 for m in valuation_matrix.values() 
                          if m['recommendation'] in ['Strong Buy', 'Buy'])
    
    avg_peg = np.mean([m['peg_ratio'] for m in valuation_matrix.values() 
                       if 0 < m['peg_ratio'] < 10])
    
    # Top ranked company
    top_company = max(valuation_matrix.items(), 
                     key=lambda x: x[1]['valuation_score'])[0]
    top_score = valuation_matrix[top_company]['valuation_score']
    
    cards = [
        {
            "label": "Portfolio Valuation Score",
            "value": f"{avg_valuation_score:.1f}/10",
            "description": f"Top: {top_company[:15]} ({top_score:.1f})",
            "type": "success" if avg_valuation_score >= 7 else "info" if avg_valuation_score >= 5 else "warning"
        },
        {
            "label": "Value Opportunities",
            "value": f"{deep_value_count + value_count}/{total_companies}",
            "description": f"{deep_value_count} deep value + {value_count} value",
            "type": "success" if (deep_value_count + value_count) >= total_companies * 0.5 else "info"
        },
        {
            "label": "Buy Recommendations",
            "value": f"{strong_buy_count}/{total_companies}",
            "description": "Strong Buy or Buy rating based on valuation",
            "type": "success" if strong_buy_count >= total_companies * 0.5 else "info"
        },
        {
            "label": "Average PEG Ratio",
            "value": f"{avg_peg:.2f}x",
            "description": f"Growth-adjusted valuation metric",
            "type": "success" if avg_peg < 1.5 else "info" if avg_peg < 2.0 else "warning"
        }
    ]
    
    return build_stat_grid(cards)


def _create_valuation_matrix_table(valuation_matrix: Dict, companies: Dict) -> str:
    """Create comprehensive valuation matrix table"""
    
    if not valuation_matrix:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, metrics in valuation_matrix.items():
        table_data.append({
            'Company': company_name,
            'P/E': f"{metrics['pe_ratio']:.1f}x",
            'P/B': f"{metrics['pb_ratio']:.1f}x",
            'EV/EBITDA': f"{metrics['ev_ebitda']:.1f}x",
            'PEG': f"{metrics['peg_ratio']:.2f}x" if 0 < metrics['peg_ratio'] < 10 else 'N/A',
            'Val Score': f"{metrics['valuation_score']:.1f}/10",
            'Rank': f"#{metrics['pe_rank']}" if metrics['pe_rank'] > 0 else 'N/A',
            'Category': metrics['value_category'],
            'Analyst Upside': f"{metrics['analyst_upside']:+.1f}%",
            'Recommendation': metrics['recommendation']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Sort by valuation score descending
    df_table = df_table.sort_values('Val Score', ascending=False)
    
    # Color coding functions
    def category_color(val):
        if 'Deep Value' in val:
            return 'excellent'
        elif 'Value' in val:
            return 'good'
        elif 'Fair Value' in val:
            return 'neutral'
        elif 'Growth Premium' in val:
            return 'fair'
        else:
            return 'poor'
    
    def recommendation_color(val):
        if 'Strong Buy' in val:
            return 'excellent'
        elif 'Buy' in val:
            return 'good'
        elif 'Hold' in val:
            return 'neutral'
        elif 'Reduce' in val:
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'Category': category_color,
        'Recommendation': recommendation_color
    }
    
    badge_columns = ['Category', 'Recommendation']
    
    return build_enhanced_table(
        df_table,
        table_id="valuation-matrix-table",
        color_columns=color_columns,
        badge_columns=badge_columns,
        sortable=True,
        searchable=True
    )


def _create_growth_adjusted_section(valuation_matrix: Dict, companies: Dict) -> str:
    """Create growth-adjusted valuation section"""
    
    if not valuation_matrix:
        return ""
    
    # Filter companies with valid PEG ratios
    peg_companies = {k: v for k, v in valuation_matrix.items() 
                     if 0 < v['peg_ratio'] < 10}
    
    if not peg_companies:
        return build_info_box(
            "<p>Insufficient data for PEG ratio analysis (requires positive P/E and positive growth).</p>",
            "warning"
        )
    
    # Build PEG analysis table
    table_data = []
    for company_name, metrics in peg_companies.items():
        table_data.append({
            'Company': company_name,
            'P/E Ratio': f"{metrics['pe_ratio']:.1f}x",
            'Earnings Growth': f"{metrics['earnings_growth']:.1f}%",
            'PEG Ratio': f"{metrics['peg_ratio']:.2f}x",
            'Revenue Growth': f"{metrics['revenue_growth']:.1f}%",
            'ROE': f"{metrics['roe']:.1f}%",
            'GARP Score': _calculate_garp_score(metrics)
        })
    
    df_peg = pd.DataFrame(table_data)
    df_peg = df_peg.sort_values('PEG Ratio')
    
    # Analysis text
    avg_peg = np.mean([m['peg_ratio'] for m in peg_companies.values()])
    attractive_peg_count = sum(1 for m in peg_companies.values() if m['peg_ratio'] < 1.5)
    
    html = f"""
    <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
        <p style="color: var(--text-secondary); line-height: 1.8; margin: 0;">
            <strong style="color: var(--text-primary);">Growth-Adjusted Valuation (PEG Analysis):</strong>
            Portfolio average PEG ratio of {avg_peg:.2f}x with {attractive_peg_count}/{len(peg_companies)} companies 
            below 1.5x (indicating {'strong' if attractive_peg_count >= len(peg_companies) * 0.5 else 'moderate'} 
            Growth At Reasonable Price opportunities).
        </p>
    </div>
    
    {build_data_table(df_peg, table_id="peg-analysis-table", sortable=True, searchable=True)}
    """
    
    return html


def _calculate_garp_score(metrics: Dict) -> str:
    """Calculate GARP (Growth At Reasonable Price) score"""
    
    peg = metrics['peg_ratio']
    roe = metrics['roe']
    revenue_growth = metrics['revenue_growth']
    
    score = 0
    
    # PEG component (lower is better)
    if peg < 1.0:
        score += 4
    elif peg < 1.5:
        score += 3
    elif peg < 2.0:
        score += 2
    elif peg < 2.5:
        score += 1
    
    # Quality component (ROE)
    if roe > 20:
        score += 3
    elif roe > 15:
        score += 2
    elif roe > 10:
        score += 1
    
    # Growth component
    if revenue_growth > 15:
        score += 3
    elif revenue_growth > 10:
        score += 2
    elif revenue_growth > 5:
        score += 1
    
    score_out_of_10 = min(10, score)
    
    if score_out_of_10 >= 8:
        return f"⭐⭐⭐ Excellent ({score_out_of_10}/10)"
    elif score_out_of_10 >= 6:
        return f"⭐⭐ Good ({score_out_of_10}/10)"
    elif score_out_of_10 >= 4:
        return f"⭐ Fair ({score_out_of_10}/10)"
    else:
        return f"Poor ({score_out_of_10}/10)"


def _create_valuation_matrix_charts(valuation_matrix: Dict, companies: Dict) -> str:
    """Create valuation matrix visualization charts"""
    
    charts_html = ""
    
    # Chart 1: Valuation Score Rankings
    chart1_html = _create_valuation_score_chart(valuation_matrix)
    if chart1_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Valuation Score Rankings</h5>
            {chart1_html}
        </div>
        """
    
    # Chart 2: P/E vs Growth (PEG Scatter)
    chart2_html = _create_pe_vs_growth_chart(valuation_matrix)
    if chart2_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">P/E Ratio vs Earnings Growth (GARP Analysis)</h5>
            {chart2_html}
        </div>
        """
    
    # Chart 3: Multi-Metric Valuation Heatmap
    chart3_html = _create_valuation_heatmap(valuation_matrix)
    if chart3_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Multi-Metric Valuation Heatmap</h5>
            {chart3_html}
        </div>
        """
    
    # Chart 4: Value Category Distribution
    chart4_html = _create_value_category_distribution(valuation_matrix)
    if chart4_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Portfolio Value Category Distribution</h5>
            {chart4_html}
        </div>
        """
    
    return charts_html


def _create_valuation_score_chart(valuation_matrix: Dict) -> str:
    """Create valuation score ranking chart"""
    
    if not valuation_matrix:
        return ""
    
    # Sort by valuation score
    sorted_companies = sorted(valuation_matrix.items(), 
                             key=lambda x: x[1]['valuation_score'], 
                             reverse=True)
    
    companies_list = [name for name, _ in sorted_companies]
    scores = [metrics['valuation_score'] for _, metrics in sorted_companies]
    categories = [metrics['value_category'] for _, metrics in sorted_companies]
    
    # Color by category
    category_colors = {
        'Deep Value': '#10b981',
        'Value': '#43e97b',
        'Fair Value': '#3b82f6',
        'Growth Premium': '#f59e0b',
        'Expensive': '#ef4444'
    }
    colors = [category_colors.get(cat, '#667eea') for cat in categories]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': companies_list,
            'x': scores,
            'orientation': 'h',
            'marker': {'color': colors},
            'text': [f"{score:.1f}" for score in scores],
            'textposition': 'auto',
            'hovertemplate': '<b>%{y}</b><br>Score: %{x:.1f}/10<br>Category: %{customdata}<extra></extra>',
            'customdata': categories
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Valuation Score (0-10)', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 10]},
            'yaxis': {'title': ''},
            'height': max(400, len(companies_list) * 40),
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="valuation-score-chart", height=max(400, len(companies_list) * 40))


def _create_pe_vs_growth_chart(valuation_matrix: Dict) -> str:
    """Create P/E vs Growth scatter chart for GARP analysis"""
    
    # Filter valid data
    valid_companies = {k: v for k, v in valuation_matrix.items() 
                      if v['pe_ratio'] > 0 and v['earnings_growth'] != 0}
    
    if not valid_companies:
        return ""
    
    companies_list = list(valid_companies.keys())
    pe_ratios = [valid_companies[c]['pe_ratio'] for c in companies_list]
    earnings_growth = [valid_companies[c]['earnings_growth'] for c in companies_list]
    peg_ratios = [valid_companies[c]['peg_ratio'] if 0 < valid_companies[c]['peg_ratio'] < 10 
                  else None for c in companies_list]
    
    # Color by PEG ratio
    colors_list = []
    for peg in peg_ratios:
        if peg is None:
            colors_list.append('#999999')
        elif peg < 1.0:
            colors_list.append('#10b981')
        elif peg < 1.5:
            colors_list.append('#43e97b')
        elif peg < 2.0:
            colors_list.append('#3b82f6')
        elif peg < 2.5:
            colors_list.append('#f59e0b')
        else:
            colors_list.append('#ef4444')
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': earnings_growth,
            'y': pe_ratios,
            'text': [c[:8] for c in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 14,
                'color': colors_list,
                'line': {'width': 1, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Growth: %{x:.1f}%<br>P/E: %{y:.1f}x<br>PEG: %{customdata}<extra></extra>',
            'customdata': [f"{peg:.2f}x" if peg else "N/A" for peg in peg_ratios]
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Earnings Growth (%)', 'gridcolor': 'rgba(128,128,128,0.2)', 'zeroline': True},
            'yaxis': {'title': 'P/E Ratio', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'annotations': [
                {
                    'x': 15,
                    'y': max(pe_ratios) * 0.9 if pe_ratios else 30,
                    'text': 'High Growth<br>Premium',
                    'showarrow': False,
                    'font': {'color': 'rgba(128,128,128,0.5)', 'size': 12}
                },
                {
                    'x': 15,
                    'y': min(pe_ratios) * 1.1 if pe_ratios else 10,
                    'text': 'GARP<br>Sweet Spot',
                    'showarrow': False,
                    'font': {'color': 'rgba(16,185,129,0.7)', 'size': 12, 'weight': 'bold'}
                }
            ],
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="pe-vs-growth-chart", height=500)


def _create_valuation_heatmap(valuation_matrix: Dict) -> str:
    """Create multi-metric valuation heatmap"""
    
    if not valuation_matrix:
        return ""
    
    companies_list = list(valuation_matrix.keys())
    metrics_names = ['P/E Percentile', 'P/B Percentile', 'EV/EBITDA Percentile', 'PEG Percentile']
    
    # Build matrix data
    z_data = []
    for metric_name in metrics_names:
        row = []
        for company in companies_list:
            if metric_name == 'P/E Percentile':
                row.append(valuation_matrix[company]['pe_percentile'])
            elif metric_name == 'P/B Percentile':
                row.append(valuation_matrix[company]['pb_percentile'])
            elif metric_name == 'EV/EBITDA Percentile':
                row.append(valuation_matrix[company]['ev_percentile'])
            elif metric_name == 'PEG Percentile':
                row.append(valuation_matrix[company]['peg_percentile'])
        z_data.append(row)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': z_data,
            'x': [c[:10] for c in companies_list],
            'y': metrics_names,
            'colorscale': [
                [0, '#10b981'],    # Green (low percentile = undervalued)
                [0.5, '#3b82f6'],  # Blue (mid percentile)
                [1, '#ef4444']     # Red (high percentile = overvalued)
            ],
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Percentile: %{z:.0f}th<extra></extra>',
            'colorbar': {'title': 'Percentile<br>Rank'}
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': '', 'tickangle': -45},
            'yaxis': {'title': ''},
            'height': 300,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="valuation-heatmap", height=300)


def _create_value_category_distribution(valuation_matrix: Dict) -> str:
    """Create value category distribution pie chart"""
    
    if not valuation_matrix:
        return ""
    
    # Count categories
    category_counts = {}
    for metrics in valuation_matrix.values():
        cat = metrics['value_category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    categories = ['Deep Value', 'Value', 'Fair Value', 'Growth Premium', 'Expensive']
    counts = [category_counts.get(cat, 0) for cat in categories]
    
    category_colors = ['#10b981', '#43e97b', '#3b82f6', '#f59e0b', '#ef4444']
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': categories,
            'values': counts,
            'marker': {'colors': category_colors},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'showlegend': True,
            'height': 400,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="value-category-pie", height=400)


def _create_valuation_matrix_insights(valuation_matrix: Dict, companies: Dict) -> str:
    """Generate valuation matrix insights"""
    
    if not valuation_matrix:
        return ""
    
    total_companies = len(valuation_matrix)
    
    # Calculate key metrics
    avg_valuation_score = np.mean([m['valuation_score'] for m in valuation_matrix.values()])
    
    deep_value_count = sum(1 for m in valuation_matrix.values() 
                          if m['value_category'] == 'Deep Value')
    value_count = sum(1 for m in valuation_matrix.values() 
                     if m['value_category'] == 'Value')
    expensive_count = sum(1 for m in valuation_matrix.values() 
                         if m['value_category'] == 'Expensive')
    
    strong_buy_count = sum(1 for m in valuation_matrix.values() 
                          if m['recommendation'] == 'Strong Buy')
    buy_count = sum(1 for m in valuation_matrix.values() 
                   if m['recommendation'] == 'Buy')
    
    garp_candidates = sum(1 for m in valuation_matrix.values() 
                         if 0 < m['peg_ratio'] < 1.5 and m['roe'] > 15)
    
    # Find top opportunities
    top_3 = sorted(valuation_matrix.items(), 
                   key=lambda x: x[1]['valuation_score'], 
                   reverse=True)[:3]
    
    insight_text = f"""
    <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #667eea;">
        <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">💡 Cross-Company Valuation Insights</h5>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Portfolio Valuation Profile:</strong> 
            Average valuation score of {avg_valuation_score:.1f}/10 indicates 
            {'excellent' if avg_valuation_score >= 7 else 'good' if avg_valuation_score >= 5 else 'fair'} 
            overall value positioning across the portfolio.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Value Discovery:</strong> 
            {deep_value_count + value_count} out of {total_companies} companies ({(deep_value_count + value_count)/total_companies*100:.0f}%) 
            present attractive value opportunities, with {deep_value_count} in deep value territory and {value_count} in value range.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Investment Recommendations:</strong> 
            {strong_buy_count} Strong Buy and {buy_count} Buy recommendations based on valuation analysis, 
            representing {(strong_buy_count + buy_count)/total_companies*100:.0f}% of the portfolio with 
            {'strong' if (strong_buy_count + buy_count) >= total_companies * 0.6 else 'moderate'} conviction levels.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">GARP Opportunities:</strong> 
            {garp_candidates} companies identified as Growth At Reasonable Price candidates 
            (PEG < 1.5 and ROE > 15%), offering the {'compelling' if garp_candidates >= 2 else 'selective'} 
            combination of growth and value.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 0;">
            <strong style="color: var(--text-primary);">Top Valuation Opportunities:</strong><br>
            {'<br>'.join([f"• {name}: {metrics['valuation_score']:.1f}/10 ({metrics['value_category']}, {metrics['recommendation']})" 
                         for name, metrics in top_3])}
        </p>
    </div>
    """
    
    return insight_text


# =============================================================================
# SUBSECTION 7C: SMART VALUATION BUCKETS (STUB)
# =============================================================================

# =============================================================================
# SUBSECTION 7C: SMART VALUATION BUCKETS
# =============================================================================

def _build_section_7c_smart_valuation_buckets(
    df: pd.DataFrame,
    companies: Dict[str, str],
    profiles_df: pd.DataFrame
) -> str:
    """Build Section 7C: Smart Valuation Buckets"""
    
    html = """
    <div class="info-section">
        <h3>7C. Smart Valuation Buckets</h3>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">
            Dynamic quintile-based classification with quality and growth adjustments, investment style profiling
        </p>
    """
    
    # Calculate valuation buckets
    bucket_data = _calculate_valuation_buckets(df, companies, profiles_df)
    
    if not bucket_data or 'companies' not in bucket_data:
        html += build_info_box(
            "<p>Insufficient data for valuation bucket analysis.</p>",
            "warning"
        )
        html += "</div>"
        return html
    
    # 7C.1: Bucket Distribution Summary
    html += """
        <div style="margin-top: 30px;">
            <h4>7C.1 Valuation Bucket Distribution</h4>
    """
    
    distribution_cards = _create_bucket_distribution_cards(bucket_data)
    html += distribution_cards
    
    # 7C.2: Comprehensive Bucket Classification Table
    html += """
        <div style="margin-top: 40px;">
            <h4>7C.2 Company Bucket Classifications</h4>
    """
    
    bucket_table = _create_bucket_classification_table(bucket_data)
    html += bucket_table
    
    # 7C.3: Investment Style Analysis
    html += """
        <div style="margin-top: 40px;">
            <h4>7C.3 Investment Style Profiling</h4>
    """
    
    style_analysis_html = _create_investment_style_analysis(bucket_data)
    html += style_analysis_html
    
    # 7C.4: Bucket Visualizations
    html += """
        <div style="margin-top: 40px;">
            <h4>7C.4 Valuation Bucket Visualizations</h4>
    """
    
    charts_html = _create_bucket_charts(bucket_data, companies)
    html += charts_html
    
    # 7C.5: Strategic Bucket Insights
    html += """
        <div style="margin-top: 40px;">
            <h4>7C.5 Bucket Strategy Insights</h4>
    """
    
    insights_html = _create_bucket_insights(bucket_data)
    html += insights_html
    
    html += "</div></div>"
    
    return html


def _calculate_valuation_buckets(
    df: pd.DataFrame,
    companies: Dict[str, str],
    profiles_df: pd.DataFrame
) -> Dict[str, Any]:
    """Calculate smart valuation bucket classifications"""
    
    bucket_data = {
        'companies': {},
        'distribution': {},
        'summary': {}
    }
    
    # First pass: collect all valuation metrics
    all_metrics = []
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core valuation metrics
        metrics['pe_ratio'] = latest.get('priceToEarningsRatio', 0)
        metrics['pb_ratio'] = latest.get('priceToBookRatio', 0)
        metrics['ev_ebitda'] = latest.get('evToEBITDA', 0)
        metrics['ev_sales'] = latest.get('evToSales', 0)
        
        # Quality metrics
        metrics['roe'] = latest.get('returnOnEquity', 0)
        metrics['roic'] = latest.get('returnOnInvestedCapital', 0)
        metrics['net_margin'] = latest.get('netProfitMargin', 0)
        
        # Growth metrics
        if len(company_data) >= 2:
            current_revenue = latest.get('revenue', 0)
            previous_revenue = company_data.iloc[-2].get('revenue', 0)
            metrics['revenue_growth'] = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            current_earnings = latest.get('netIncome', 0)
            previous_earnings = company_data.iloc[-2].get('netIncome', 0)
            metrics['earnings_growth'] = ((current_earnings - previous_earnings) / previous_earnings * 100) if previous_earnings > 0 else 0
        else:
            metrics['revenue_growth'] = 0
            metrics['earnings_growth'] = 0
        
        # Leverage
        metrics['debt_to_equity'] = latest.get('debtToEquityRatio', 0)
        
        all_metrics.append((company_name, metrics))
    
    if not all_metrics:
        return bucket_data
    
    # Calculate quintiles for PE and EV/EBITDA
    pe_values = sorted([m['pe_ratio'] for _, m in all_metrics if m['pe_ratio'] > 0])
    ev_ebitda_values = sorted([m['ev_ebitda'] for _, m in all_metrics if m['ev_ebitda'] > 0])
    
    # Calculate quintile thresholds
    def get_quintile(value, sorted_values):
        if not sorted_values or value <= 0:
            return 3  # Default to Q3
        
        n = len(sorted_values)
        position = sum(1 for v in sorted_values if v < value)
        percentile = position / n if n > 0 else 0.5
        
        if percentile <= 0.20:
            return 1
        elif percentile <= 0.40:
            return 2
        elif percentile <= 0.60:
            return 3
        elif percentile <= 0.80:
            return 4
        else:
            return 5
    
    # Second pass: assign buckets and calculate scores
    for company_name, metrics in all_metrics:
        bucket_info = {}
        
        # Quintile assignments
        pe_quintile = get_quintile(metrics['pe_ratio'], pe_values)
        ev_quintile = get_quintile(metrics['ev_ebitda'], ev_ebitda_values)
        
        bucket_info['pe_quintile'] = f"Q{pe_quintile}"
        bucket_info['ev_ebitda_quintile'] = f"Q{ev_quintile}"
        
        # Average quintile for bucket classification
        avg_quintile = (pe_quintile + ev_quintile) / 2
        
        # Primary bucket based on quintiles
        if avg_quintile <= 1.5:
            primary_bucket = 'Deep Value'
        elif avg_quintile <= 2.5:
            primary_bucket = 'Value'
        elif avg_quintile <= 3.5:
            primary_bucket = 'Fair Value'
        elif avg_quintile <= 4.5:
            primary_bucket = 'Growth'
        else:
            primary_bucket = 'Premium'
        
        # Growth adjustment
        revenue_growth = metrics['revenue_growth']
        if revenue_growth > 20:
            growth_adjustment = 2.5
        elif revenue_growth > 15:
            growth_adjustment = 2.0
        elif revenue_growth > 10:
            growth_adjustment = 1.5
        elif revenue_growth > 5:
            growth_adjustment = 1.0
        elif revenue_growth > 0:
            growth_adjustment = 0.5
        elif revenue_growth > -5:
            growth_adjustment = 0.0
        else:
            growth_adjustment = -1.0
        
        bucket_info['growth_adjustment'] = growth_adjustment
        
        # Quality premium
        quality_score = (metrics['roe'] + metrics['roic']) / 2
        if quality_score > 25:
            quality_premium = 2.0
        elif quality_score > 20:
            quality_premium = 1.5
        elif quality_score > 15:
            quality_premium = 1.0
        elif quality_score > 10:
            quality_premium = 0.5
        else:
            quality_premium = 0.0
        
        # Penalty for high leverage
        if metrics['debt_to_equity'] > 2.0:
            quality_premium -= 0.5
        
        bucket_info['quality_premium'] = quality_premium
        
        # Composite bucket score (0-10 scale)
        base_score = (6 - avg_quintile) * 2  # Quintile 1 = 10, Quintile 5 = 2
        bucket_score = base_score + (growth_adjustment * 0.5) + (quality_premium * 0.5)
        bucket_info['bucket_score'] = max(0, min(10, bucket_score))
        
        # Investment style classification
        if primary_bucket in ['Deep Value', 'Value'] and growth_adjustment >= 1.5:
            investment_style = 'GARP'
        elif primary_bucket in ['Deep Value', 'Value'] and quality_premium >= 1.0:
            investment_style = 'Quality Value'
        elif primary_bucket in ['Deep Value', 'Value']:
            investment_style = 'Deep Value'
        elif primary_bucket == 'Fair Value':
            if growth_adjustment >= 1.5:
                investment_style = 'Balanced Growth'
            else:
                investment_style = 'Core Holding'
        elif quality_premium >= 1.5:
            investment_style = 'Quality Growth'
        else:
            investment_style = 'Momentum/Growth'
        
        bucket_info['investment_style'] = investment_style
        
        # Risk level assessment
        if avg_quintile <= 2.0 and quality_premium >= 1.0 and revenue_growth >= 0:
            risk_level = 'Low'
        elif avg_quintile <= 3.0 and quality_premium >= 0.5:
            risk_level = 'Medium'
        elif avg_quintile <= 4.0:
            risk_level = 'Medium-High'
        else:
            risk_level = 'High'
        
        # Additional risk from leverage
        if metrics['debt_to_equity'] > 2.0:
            if risk_level == 'Low':
                risk_level = 'Medium'
            elif risk_level == 'Medium':
                risk_level = 'Medium-High'
        
        bucket_info['risk_level'] = risk_level
        bucket_info['bucket'] = primary_bucket
        
        # Store raw metrics for reference
        bucket_info['pe_ratio'] = metrics['pe_ratio']
        bucket_info['ev_ebitda'] = metrics['ev_ebitda']
        bucket_info['revenue_growth'] = metrics['revenue_growth']
        bucket_info['roe'] = metrics['roe']
        bucket_info['roic'] = metrics['roic']
        
        bucket_data['companies'][company_name] = bucket_info
    
    # Calculate distribution
    bucket_counts = {}
    for info in bucket_data['companies'].values():
        bucket = info['bucket']
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    
    bucket_data['distribution'] = {
        'deep_value': bucket_counts.get('Deep Value', 0),
        'value': bucket_counts.get('Value', 0),
        'fair_value': bucket_counts.get('Fair Value', 0),
        'growth': bucket_counts.get('Growth', 0),
        'premium': bucket_counts.get('Premium', 0)
    }
    
    # Generate summary insights
    total = len(bucket_data['companies'])
    value_oriented = bucket_data['distribution']['deep_value'] + bucket_data['distribution']['value']
    premium_oriented = bucket_data['distribution']['growth'] + bucket_data['distribution']['premium']
    
    if value_oriented >= total * 0.6:
        bucket_data['summary']['orientation'] = 'Strong value orientation with abundant discount opportunities'
    elif premium_oriented >= total * 0.6:
        bucket_data['summary']['orientation'] = 'Growth-focused portfolio with premium valuations'
    else:
        bucket_data['summary']['orientation'] = 'Balanced distribution across value and growth categories'
    
    # Risk profile
    high_risk = sum(1 for info in bucket_data['companies'].values() if info['risk_level'] == 'High')
    low_risk = sum(1 for info in bucket_data['companies'].values() if info['risk_level'] == 'Low')
    
    if low_risk >= total * 0.5:
        bucket_data['summary']['risk_profile'] = 'Conservative - emphasis on capital preservation'
    elif high_risk >= total * 0.4:
        bucket_data['summary']['risk_profile'] = 'Aggressive - seeking high growth returns'
    else:
        bucket_data['summary']['risk_profile'] = 'Moderate - balanced risk-return approach'
    
    return bucket_data


def _create_bucket_distribution_cards(bucket_data: Dict) -> str:
    """Create bucket distribution summary cards"""
    
    distribution = bucket_data.get('distribution', {})
    total = sum(distribution.values())
    
    if total == 0:
        return ""
    
    cards = [
        {
            "label": "Deep Value + Value",
            "value": f"{distribution['deep_value'] + distribution['value']}/{total}",
            "description": f"{distribution['deep_value']} deep value, {distribution['value']} value",
            "type": "success" if (distribution['deep_value'] + distribution['value']) >= total * 0.5 else "info"
        },
        {
            "label": "Fair Value",
            "value": f"{distribution['fair_value']}/{total}",
            "description": "Balanced valuation positioning",
            "type": "info"
        },
        {
            "label": "Growth + Premium",
            "value": f"{distribution['growth'] + distribution['premium']}/{total}",
            "description": f"{distribution['growth']} growth, {distribution['premium']} premium",
            "type": "warning" if (distribution['growth'] + distribution['premium']) >= total * 0.5 else "info"
        },
        {
            "label": "Portfolio Orientation",
            "value": "Value" if (distribution['deep_value'] + distribution['value']) >= total * 0.5 else "Growth" if (distribution['growth'] + distribution['premium']) >= total * 0.5 else "Balanced",
            "description": bucket_data['summary'].get('orientation', 'Mixed positioning')[:50] + "...",
            "type": "success" if (distribution['deep_value'] + distribution['value']) >= total * 0.5 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_bucket_classification_table(bucket_data: Dict) -> str:
    """Create comprehensive bucket classification table"""
    
    companies_data = bucket_data.get('companies', {})
    
    if not companies_data:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, info in companies_data.items():
        table_data.append({
            'Company': company_name,
            'Bucket': info['bucket'],
            'P/E Quintile': info['pe_quintile'],
            'EV/EBITDA Quintile': info['ev_ebitda_quintile'],
            'Growth Adj': f"{info['growth_adjustment']:.1f}",
            'Quality Premium': f"{info['quality_premium']:.1f}",
            'Bucket Score': f"{info['bucket_score']:.1f}/10",
            'Investment Style': info['investment_style'],
            'Risk Level': info['risk_level']
        })
    
    df_table = pd.DataFrame(table_data)
    df_table = df_table.sort_values('Bucket Score', ascending=False)
    
    # Color coding functions
    def bucket_color(val):
        if 'Deep Value' in val:
            return 'excellent'
        elif 'Value' in val:
            return 'good'
        elif 'Fair Value' in val:
            return 'neutral'
        elif 'Growth' in val:
            return 'fair'
        else:
            return 'poor'
    
    def risk_color(val):
        if 'Low' in val:
            return 'excellent'
        elif 'Medium' in val and 'High' not in val:
            return 'good'
        elif 'Medium-High' in val:
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'Bucket': bucket_color,
        'Risk Level': risk_color
    }
    
    badge_columns = ['Bucket', 'Investment Style', 'Risk Level']
    
    return build_enhanced_table(
        df_table,
        table_id="bucket-classification-table",
        color_columns=color_columns,
        badge_columns=badge_columns,
        sortable=True,
        searchable=True
    )


def _create_investment_style_analysis(bucket_data: Dict) -> str:
    """Create investment style analysis section"""
    
    companies_data = bucket_data.get('companies', {})
    
    if not companies_data:
        return ""
    
    # Count by investment style
    style_counts = {}
    for info in companies_data.values():
        style = info['investment_style']
        style_counts[style] = style_counts.get(style, 0) + 1
    
    total = len(companies_data)
    
    # Create style breakdown cards
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">'
    
    style_colors = {
        'Deep Value': '#10b981',
        'Quality Value': '#43e97b',
        'GARP': '#3b82f6',
        'Core Holding': '#667eea',
        'Balanced Growth': '#f59e0b',
        'Quality Growth': '#fa709a',
        'Momentum/Growth': '#ef4444'
    }
    
    for style, count in sorted(style_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        color = style_colors.get(style, '#667eea')
        
        html += f"""
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid {color};">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">{style}</h5>
            <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 10px;">
                {count}/{total}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                {percentage:.0f}% of portfolio
            </div>
        </div>
        """
    
    html += '</div>'
    
    return html


def _create_bucket_charts(bucket_data: Dict, companies: Dict) -> str:
    """Create bucket visualization charts"""
    
    charts_html = ""
    
    # Chart 1: Bucket Score Rankings
    chart1_html = _create_bucket_score_chart(bucket_data)
    if chart1_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Bucket Score Rankings</h5>
            {chart1_html}
        </div>
        """
    
    # Chart 2: Growth vs Quality Matrix
    chart2_html = _create_growth_quality_matrix(bucket_data)
    if chart2_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Growth Adjustment vs Quality Premium Matrix</h5>
            {chart2_html}
        </div>
        """
    
    # Chart 3: Investment Style Distribution
    chart3_html = _create_investment_style_pie(bucket_data)
    if chart3_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Investment Style Distribution</h5>
            {chart3_html}
        </div>
        """
    
    # Chart 4: Risk Level Analysis
    chart4_html = _create_risk_level_chart(bucket_data)
    if chart4_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Risk Level Distribution by Bucket Score</h5>
            {chart4_html}
        </div>
        """
    
    return charts_html


def _create_bucket_score_chart(bucket_data: Dict) -> str:
    """Create bucket score ranking chart"""
    
    companies_data = bucket_data.get('companies', {})
    
    if not companies_data:
        return ""
    
    # Sort by bucket score
    sorted_companies = sorted(companies_data.items(), 
                             key=lambda x: x[1]['bucket_score'], 
                             reverse=True)
    
    companies_list = [name for name, _ in sorted_companies]
    scores = [info['bucket_score'] for _, info in sorted_companies]
    buckets = [info['bucket'] for _, info in sorted_companies]
    
    # Color by bucket
    bucket_colors_map = {
        'Deep Value': '#10b981',
        'Value': '#43e97b',
        'Fair Value': '#3b82f6',
        'Growth': '#f59e0b',
        'Premium': '#ef4444'
    }
    colors = [bucket_colors_map.get(bucket, '#667eea') for bucket in buckets]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': companies_list,
            'x': scores,
            'orientation': 'h',
            'marker': {'color': colors},
            'text': [f"{score:.1f}" for score in scores],
            'textposition': 'auto',
            'hovertemplate': '<b>%{y}</b><br>Score: %{x:.1f}/10<br>Bucket: %{customdata}<extra></extra>',
            'customdata': buckets
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Bucket Score (0-10)', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 10]},
            'yaxis': {'title': ''},
            'height': max(400, len(companies_list) * 40),
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="bucket-score-chart", height=max(400, len(companies_list) * 40))


def _create_growth_quality_matrix(bucket_data: Dict) -> str:
    """Create growth adjustment vs quality premium scatter chart"""
    
    companies_data = bucket_data.get('companies', {})
    
    if not companies_data:
        return ""
    
    companies_list = list(companies_data.keys())
    growth_adj = [companies_data[c]['growth_adjustment'] for c in companies_list]
    quality_prem = [companies_data[c]['quality_premium'] for c in companies_list]
    buckets = [companies_data[c]['bucket'] for c in companies_list]
    
    # Color by bucket
    bucket_colors_map = {
        'Deep Value': '#10b981',
        'Value': '#43e97b',
        'Fair Value': '#3b82f6',
        'Growth': '#f59e0b',
        'Premium': '#ef4444'
    }
    colors = [bucket_colors_map.get(bucket, '#667eea') for bucket in buckets]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': growth_adj,
            'y': quality_prem,
            'text': [c[:8] for c in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': colors,
                'line': {'width': 1, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Growth Adj: %{x:.1f}<br>Quality Premium: %{y:.1f}<br>Bucket: %{customdata}<extra></extra>',
            'customdata': buckets
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Growth Adjustment', 'gridcolor': 'rgba(128,128,128,0.2)', 'zeroline': True},
            'yaxis': {'title': 'Quality Premium', 'gridcolor': 'rgba(128,128,128,0.2)', 'zeroline': True},
            'annotations': [
                {
                    'x': 1.5,
                    'y': 1.5,
                    'text': 'GARP<br>Sweet Spot',
                    'showarrow': False,
                    'font': {'color': 'rgba(59,130,246,0.7)', 'size': 12, 'weight': 'bold'}
                }
            ],
            'shapes': [
                {
                    'type': 'rect',
                    'x0': 1.0, 'y0': 1.0,
                    'x1': 3.0, 'y1': 2.5,
                    'line': {'color': 'rgba(59,130,246,0.3)', 'width': 2, 'dash': 'dash'},
                    'fillcolor': 'rgba(59,130,246,0.1)'
                }
            ],
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="growth-quality-matrix", height=500)


def _create_investment_style_pie(bucket_data: Dict) -> str:
    """Create investment style distribution pie chart"""
    
    companies_data = bucket_data.get('companies', {})
    
    if not companies_data:
        return ""
    
    # Count styles
    style_counts = {}
    for info in companies_data.values():
        style = info['investment_style']
        style_counts[style] = style_counts.get(style, 0) + 1
    
    styles = list(style_counts.keys())
    counts = list(style_counts.values())
    
    style_colors = ['#10b981', '#43e97b', '#3b82f6', '#667eea', '#f59e0b', '#fa709a', '#ef4444']
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': styles,
            'values': counts,
            'marker': {'colors': style_colors[:len(styles)]},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'showlegend': True,
            'height': 400,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="investment-style-pie", height=400)


def _create_risk_level_chart(bucket_data: Dict) -> str:
    """Create risk level distribution chart"""
    
    companies_data = bucket_data.get('companies', {})
    
    if not companies_data:
        return ""
    
    # Group by risk level and calculate average scores
    risk_groups = {}
    for info in companies_data.values():
        risk = info['risk_level']
        if risk not in risk_groups:
            risk_groups[risk] = []
        risk_groups[risk].append(info['bucket_score'])
    
    risk_order = ['Low', 'Medium', 'Medium-High', 'High']
    risk_labels = [r for r in risk_order if r in risk_groups]
    avg_scores = [np.mean(risk_groups[r]) for r in risk_labels]
    counts = [len(risk_groups[r]) for r in risk_labels]
    
    risk_colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
    colors = [risk_colors[risk_order.index(r)] for r in risk_labels]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': risk_labels,
            'y': avg_scores,
            'marker': {'color': colors},
            'text': [f"{score:.1f}<br>({count} cos)" for score, count in zip(avg_scores, counts)],
            'textposition': 'auto',
            'hovertemplate': '<b>%{x}</b><br>Avg Score: %{y:.1f}/10<br>Companies: %{customdata}<extra></extra>',
            'customdata': counts
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Risk Level'},
            'yaxis': {'title': 'Average Bucket Score', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 10]},
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-level-chart", height=400)


def _create_bucket_insights(bucket_data: Dict) -> str:
    """Generate bucket strategy insights"""
    
    companies_data = bucket_data.get('companies', {})
    distribution = bucket_data.get('distribution', {})
    summary = bucket_data.get('summary', {})
    
    if not companies_data:
        return ""
    
    total = len(companies_data)
    value_oriented = distribution['deep_value'] + distribution['value']
    
    # Count GARP candidates
    garp_count = sum(1 for info in companies_data.values() 
                     if info['investment_style'] == 'GARP')
    
    # Count quality value
    quality_value_count = sum(1 for info in companies_data.values() 
                             if info['investment_style'] == 'Quality Value')
    
    # Average scores by bucket
    avg_scores_by_bucket = {}
    for bucket_type in ['Deep Value', 'Value', 'Fair Value', 'Growth', 'Premium']:
        scores = [info['bucket_score'] for info in companies_data.values() 
                 if info['bucket'] == bucket_type]
        if scores:
            avg_scores_by_bucket[bucket_type] = np.mean(scores)
    
    insight_text = f"""
    <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #667eea;">
        <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">💡 Smart Bucket Strategy Insights</h5>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Portfolio Orientation:</strong> 
            {summary.get('orientation', 'Balanced portfolio distribution')} 
            with {value_oriented}/{total} companies ({value_oriented/total*100:.0f}%) in value-oriented buckets.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">GARP Opportunities:</strong> 
            {garp_count} {'exceptional' if garp_count >= 3 else 'strong' if garp_count >= 2 else 'limited'} 
            Growth At Reasonable Price candidates identified, combining quality growth with attractive valuations.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Quality-Value Convergence:</strong> 
            {quality_value_count} companies present the rare combination of deep value pricing with high-quality fundamentals, 
            offering {'compelling' if quality_value_count >= 2 else 'selective'} entry points.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 0;">
            <strong style="color: var(--text-primary);">Risk Profile:</strong> 
            {summary.get('risk_profile', 'Balanced risk-return profile')} across the portfolio with bucket scores 
            ranging from {min(info['bucket_score'] for info in companies_data.values()):.1f} to 
            {max(info['bucket_score'] for info in companies_data.values()):.1f} out of 10.
        </p>
    </div>
    """
    
    return insight_text


# =============================================================================
# SUBSECTION 7D: ENTERPRISE VALUE DEEP DIVE
# =============================================================================

def _build_section_7d_enterprise_value_deep_dive(
    df: pd.DataFrame,
    companies: Dict[str, str],
    enterprise_values_df: pd.DataFrame
) -> str:
    """Build Section 7D: Enterprise Value Deep Dive"""
    
    html = """
    <div class="info-section">
        <h3>7D. Enterprise Value Deep Dive</h3>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">
            EV component analysis, capital structure assessment, and capital efficiency evaluation
        </p>
    """
    
    # Calculate EV metrics
    ev_data = _calculate_enterprise_value_metrics(df, companies, enterprise_values_df)
    
    if not ev_data:
        html += build_info_box(
            "<p>Insufficient data for enterprise value analysis.</p>",
            "warning"
        )
        html += "</div>"
        return html
    
    # 7D.1: EV Components Summary
    html += """
        <div style="margin-top: 30px;">
            <h4>7D.1 Enterprise Value Components</h4>
    """
    
    ev_summary_cards = _create_ev_summary_cards(ev_data)
    html += ev_summary_cards
    
    # 7D.2: Comprehensive EV Analysis Table
    html += """
        <div style="margin-top: 40px;">
            <h4>7D.2 Detailed Enterprise Value Metrics</h4>
    """
    
    ev_table = _create_ev_analysis_table(ev_data)
    html += ev_table
    
    # 7D.3: Capital Structure Analysis
    html += """
        <div style="margin-top: 40px;">
            <h4>7D.3 Capital Structure Assessment</h4>
    """
    
    capital_structure_html = _create_capital_structure_analysis(ev_data)
    html += capital_structure_html
    
    # 7D.4: EV Visualizations
    html += """
        <div style="margin-top: 40px;">
            <h4>7D.4 Enterprise Value Visualizations</h4>
    """
    
    charts_html = _create_ev_charts(ev_data, companies)
    html += charts_html
    
    # 7D.5: EV Strategic Insights
    html += """
        <div style="margin-top: 40px;">
            <h4>7D.5 Capital Efficiency Insights</h4>
    """
    
    insights_html = _create_ev_insights(ev_data)
    html += insights_html
    
    html += "</div></div>"
    
    return html


def _calculate_enterprise_value_metrics(
    df: pd.DataFrame,
    companies: Dict[str, str],
    enterprise_values_df: pd.DataFrame
) -> Dict[str, Dict]:
    """Calculate comprehensive enterprise value metrics"""
    
    ev_data = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core EV components
        market_cap = latest.get('marketCap', 0)
        cash = latest.get('cashAndCashEquivalents', 0)
        total_debt = latest.get('totalDebt', 0)
        
        enterprise_value = market_cap + total_debt - cash
        net_debt = total_debt - cash
        
        metrics['market_cap'] = market_cap
        metrics['cash'] = cash
        metrics['total_debt'] = total_debt
        metrics['net_debt'] = net_debt
        metrics['enterprise_value'] = enterprise_value
        
        # EV ratios
        revenue = latest.get('revenue', 1)
        ebitda = latest.get('ebitda', 1)
        ebit = latest.get('ebit', 1)
        fcf = latest.get('freeCashFlow', 1)
        
        metrics['ev_revenue'] = enterprise_value / revenue if revenue > 0 else 0
        metrics['ev_ebitda'] = enterprise_value / ebitda if ebitda > 0 else 0
        metrics['ev_ebit'] = enterprise_value / ebit if ebit > 0 else 0
        metrics['ev_fcf'] = enterprise_value / fcf if fcf > 0 else 0
        
        # Capital structure metrics
        total_capital = market_cap + total_debt
        metrics['debt_ratio'] = total_debt / total_capital if total_capital > 0 else 0
        metrics['equity_ratio'] = market_cap / total_capital if total_capital > 0 else 0
        metrics['net_debt_to_ebitda'] = net_debt / ebitda if ebitda > 0 else 0
        
        # Capital efficiency score
        asset_turnover = latest.get('assetTurnover', 0)
        roa = latest.get('returnOnAssets', 0)
        roic = latest.get('returnOnInvestedCapital', 0)
        
        efficiency_components = []
        
        # EV/Revenue efficiency (lower is better)
        if metrics['ev_revenue'] > 0:
            ev_rev_score = min(10, max(0, (5 / metrics['ev_revenue']) * 10))
            efficiency_components.append(ev_rev_score)
        
        # Asset turnover (higher is better)
        if asset_turnover > 0:
            efficiency_components.append(min(10, asset_turnover * 5))
        
        # ROA (higher is better)
        if roa > 0:
            efficiency_components.append(min(10, roa * 2))
        
        # ROIC (higher is better)
        if roic > 0:
            efficiency_components.append(min(10, roic * 2))
        
        # Debt burden (lower debt ratio = higher score)
        efficiency_components.append(10 - (metrics['debt_ratio'] * 10))
        
        metrics['capital_efficiency'] = np.mean(efficiency_components) if efficiency_components else 5.0
        
        # EV growth (if historical data available)
        if len(company_data) >= 2:
            prev_revenue = company_data.iloc[-2].get('revenue', 0)
            current_revenue = revenue
            
            if prev_revenue > 0:
                revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
                metrics['ev_growth'] = revenue_growth  # Proxy for EV growth
            else:
                metrics['ev_growth'] = 0
        else:
            metrics['ev_growth'] = 0
        
        # EV quality assessment
        if metrics['capital_efficiency'] >= 7 and metrics['net_debt_to_ebitda'] < 3:
            metrics['ev_quality'] = 'Excellent'
        elif metrics['capital_efficiency'] >= 5 and metrics['net_debt_to_ebitda'] < 4:
            metrics['ev_quality'] = 'Good'
        elif metrics['capital_efficiency'] >= 3:
            metrics['ev_quality'] = 'Fair'
        else:
            metrics['ev_quality'] = 'Poor'
        
        # Cash position assessment
        cash_to_market_cap = cash / market_cap if market_cap > 0 else 0
        if cash_to_market_cap > 0.3:
            metrics['cash_position'] = 'Strong'
        elif cash_to_market_cap > 0.15:
            metrics['cash_position'] = 'Adequate'
        elif cash_to_market_cap > 0.05:
            metrics['cash_position'] = 'Moderate'
        else:
            metrics['cash_position'] = 'Weak'
        
        # Leverage assessment
        if metrics['debt_ratio'] < 0.2:
            metrics['leverage'] = 'Very Low'
        elif metrics['debt_ratio'] < 0.4:
            metrics['leverage'] = 'Low'
        elif metrics['debt_ratio'] < 0.6:
            metrics['leverage'] = 'Moderate'
        elif metrics['debt_ratio'] < 0.75:
            metrics['leverage'] = 'High'
        else:
            metrics['leverage'] = 'Very High'
        
        ev_data[company_name] = metrics
    
    # Calculate rankings
    if ev_data:
        efficiency_scores = [(name, metrics['capital_efficiency']) 
                            for name, metrics in ev_data.items()]
        efficiency_scores.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (company_name, _) in enumerate(efficiency_scores):
            ev_data[company_name]['efficiency_rank'] = rank + 1
    
    return ev_data


def _create_ev_summary_cards(ev_data: Dict) -> str:
    """Create EV summary cards"""
    
    if not ev_data:
        return ""
    
    total_ev = sum(m['enterprise_value'] for m in ev_data.values())
    avg_efficiency = np.mean([m['capital_efficiency'] for m in ev_data.values()])
    
    excellent_quality = sum(1 for m in ev_data.values() if m['ev_quality'] == 'Excellent')
    total_companies = len(ev_data)
    
    avg_net_debt_to_ebitda = np.mean([m['net_debt_to_ebitda'] for m in ev_data.values() 
                                      if 0 < m['net_debt_to_ebitda'] < 20])
    
    cards = [
        {
            "label": "Total Enterprise Value",
            "value": f"${total_ev/1_000_000_000:.1f}B",
            "description": "Aggregate portfolio EV",
            "type": "info"
        },
        {
            "label": "Avg Capital Efficiency",
            "value": f"{avg_efficiency:.1f}/10",
            "description": f"Portfolio efficiency score",
            "type": "success" if avg_efficiency >= 7 else "info" if avg_efficiency >= 5 else "warning"
        },
        {
            "label": "Excellent EV Quality",
            "value": f"{excellent_quality}/{total_companies}",
            "description": "Companies with excellent ratings",
            "type": "success" if excellent_quality >= total_companies * 0.5 else "info"
        },
        {
            "label": "Avg Net Debt/EBITDA",
            "value": f"{avg_net_debt_to_ebitda:.1f}x",
            "description": "Leverage metric",
            "type": "success" if avg_net_debt_to_ebitda < 2 else "info" if avg_net_debt_to_ebitda < 3 else "warning"
        }
    ]
    
    return build_stat_grid(cards)


def _create_ev_analysis_table(ev_data: Dict) -> str:
    """Create comprehensive EV analysis table"""
    
    if not ev_data:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, metrics in ev_data.items():
        table_data.append({
            'Company': company_name,
            'EV ($M)': f"${metrics['enterprise_value']/1_000_000:.0f}",
            'Market Cap ($M)': f"${metrics['market_cap']/1_000_000:.0f}",
            'Net Debt ($M)': f"${metrics['net_debt']/1_000_000:.0f}",
            'EV/Revenue': f"{metrics['ev_revenue']:.1f}x",
            'EV/EBITDA': f"{metrics['ev_ebitda']:.1f}x",
            'EV/FCF': f"{metrics['ev_fcf']:.1f}x" if 0 < metrics['ev_fcf'] < 100 else 'N/A',
            'Capital Efficiency': f"{metrics['capital_efficiency']:.1f}/10",
            'EV Quality': metrics['ev_quality'],
            'Leverage': metrics['leverage']
        })
    
    df_table = pd.DataFrame(table_data)
    df_table = df_table.sort_values('Capital Efficiency', ascending=False)
    
    # Color coding
    def quality_color(val):
        if 'Excellent' in val:
            return 'excellent'
        elif 'Good' in val:
            return 'good'
        elif 'Fair' in val:
            return 'neutral'
        else:
            return 'poor'
    
    def leverage_color(val):
        if 'Very Low' in val or 'Low' in val:
            return 'excellent'
        elif 'Moderate' in val:
            return 'good'
        elif 'High' in val and 'Very' not in val:
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'EV Quality': quality_color,
        'Leverage': leverage_color
    }
    
    badge_columns = ['EV Quality', 'Leverage']
    
    return build_enhanced_table(
        df_table,
        table_id="ev-analysis-table",
        color_columns=color_columns,
        badge_columns=badge_columns,
        sortable=True,
        searchable=True
    )


def _create_capital_structure_analysis(ev_data: Dict) -> str:
    """Create capital structure analysis section"""
    
    if not ev_data:
        return ""
    
    # Group by leverage category
    leverage_groups = {
        'Very Low': [],
        'Low': [],
        'Moderate': [],
        'High': [],
        'Very High': []
    }
    
    for company_name, metrics in ev_data.items():
        leverage = metrics['leverage']
        leverage_groups[leverage].append({
            'name': company_name,
            'debt_ratio': metrics['debt_ratio'],
            'net_debt_to_ebitda': metrics['net_debt_to_ebitda']
        })
    
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">'
    
    leverage_colors = {
        'Very Low': '#10b981',
        'Low': '#43e97b',
        'Moderate': '#3b82f6',
        'High': '#f59e0b',
        'Very High': '#ef4444'
    }
    
    for leverage_type in ['Very Low', 'Low', 'Moderate', 'High', 'Very High']:
        companies_in_group = leverage_groups[leverage_type]
        if not companies_in_group:
            continue
        
        count = len(companies_in_group)
        color = leverage_colors[leverage_type]
        
        html += f"""
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid {color};">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">{leverage_type} Leverage</h5>
            <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 10px;">
                {count}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.85rem;">
                {'<br>'.join([f"• {c['name'][:15]}" for c in companies_in_group[:3]])}
                {' + more...' if count > 3 else ''}
            </div>
        </div>
        """
    
    html += '</div>'
    
    return html


def _create_ev_charts(ev_data: Dict, companies: Dict) -> str:
    """Create enterprise value visualization charts"""
    
    charts_html = ""
    
    # Chart 1: EV Components Breakdown
    chart1_html = _create_ev_components_chart(ev_data)
    if chart1_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Enterprise Value Components</h5>
            {chart1_html}
        </div>
        """
    
    # Chart 2: EV/Revenue vs EV/EBITDA Scatter
    chart2_html = _create_ev_multiples_scatter(ev_data)
    if chart2_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">EV Multiple Correlation</h5>
            {chart2_html}
        </div>
        """
    
    # Chart 3: Capital Efficiency Rankings
    chart3_html = _create_capital_efficiency_chart(ev_data)
    if chart3_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Capital Efficiency Rankings</h5>
            {chart3_html}
        </div>
        """
    
    # Chart 4: Leverage Analysis
    chart4_html = _create_leverage_distribution_chart(ev_data)
    if chart4_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Leverage Distribution</h5>
            {chart4_html}
        </div>
        """
    
    return charts_html


def _create_ev_components_chart(ev_data: Dict) -> str:
    """Create EV components breakdown chart"""
    
    if not ev_data:
        return ""
    
    companies_list = list(ev_data.keys())
    market_caps = [ev_data[c]['market_cap']/1_000_000 for c in companies_list]
    net_debts = [ev_data[c]['net_debt']/1_000_000 for c in companies_list]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'x': companies_list,
                'y': market_caps,
                'name': 'Market Cap ($M)',
                'marker': {'color': '#667eea'},
                'hovertemplate': '<b>%{x}</b><br>Market Cap: $%{y:.0f}M<extra></extra>'
            },
            {
                'type': 'bar',
                'x': companies_list,
                'y': net_debts,
                'name': 'Net Debt ($M)',
                'marker': {'color': '#f59e0b'},
                'hovertemplate': '<b>%{x}</b><br>Net Debt: $%{y:.0f}M<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': '', 'tickangle': -45},
            'yaxis': {'title': 'Value ($M)', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'barmode': 'group',
            'hovermode': 'closest',
            'showlegend': True,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ev-components-chart", height=500)


def _create_ev_multiples_scatter(ev_data: Dict) -> str:
    """Create EV multiples scatter chart"""
    
    # Filter valid data
    valid_companies = {k: v for k, v in ev_data.items() 
                      if 0 < v['ev_revenue'] < 20 and 0 < v['ev_ebitda'] < 30}
    
    if not valid_companies:
        return ""
    
    companies_list = list(valid_companies.keys())
    ev_revenue = [valid_companies[c]['ev_revenue'] for c in companies_list]
    ev_ebitda = [valid_companies[c]['ev_ebitda'] for c in companies_list]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': ev_revenue,
            'y': ev_ebitda,
            'text': [c[:8] for c in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': ev_ebitda,
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'EV/EBITDA'}
            },
            'hovertemplate': '<b>%{text}</b><br>EV/Revenue: %{x:.1f}x<br>EV/EBITDA: %{y:.1f}x<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'EV/Revenue', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'yaxis': {'title': 'EV/EBITDA', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ev-multiples-scatter", height=500)


def _create_capital_efficiency_chart(ev_data: Dict) -> str:
    """Create capital efficiency rankings chart"""
    
    if not ev_data:
        return ""
    
    # Sort by efficiency
    sorted_companies = sorted(ev_data.items(), 
                             key=lambda x: x[1]['capital_efficiency'], 
                             reverse=True)
    
    companies_list = [name for name, _ in sorted_companies]
    efficiency = [metrics['capital_efficiency'] for _, metrics in sorted_companies]
    quality = [metrics['ev_quality'] for _, metrics in sorted_companies]
    
    # Color by quality
    quality_colors_map = {
        'Excellent': '#10b981',
        'Good': '#3b82f6',
        'Fair': '#f59e0b',
        'Poor': '#ef4444'
    }
    colors = [quality_colors_map.get(q, '#667eea') for q in quality]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': companies_list,
            'x': efficiency,
            'orientation': 'h',
            'marker': {'color': colors},
            'text': [f"{eff:.1f}" for eff in efficiency],
            'textposition': 'auto',
            'hovertemplate': '<b>%{y}</b><br>Efficiency: %{x:.1f}/10<br>Quality: %{customdata}<extra></extra>',
            'customdata': quality
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Capital Efficiency Score (0-10)', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 10]},
            'yaxis': {'title': ''},
            'height': max(400, len(companies_list) * 40),
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="capital-efficiency-chart", height=max(400, len(companies_list) * 40))


def _create_leverage_distribution_chart(ev_data: Dict) -> str:
    """Create leverage distribution pie chart"""
    
    if not ev_data:
        return ""
    
    # Count by leverage category
    leverage_counts = {}
    for metrics in ev_data.values():
        leverage = metrics['leverage']
        leverage_counts[leverage] = leverage_counts.get(leverage, 0) + 1
    
    leverage_order = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
    labels = [l for l in leverage_order if l in leverage_counts]
    counts = [leverage_counts[l] for l in labels]
    
    leverage_colors = ['#10b981', '#43e97b', '#3b82f6', '#f59e0b', '#ef4444']
    colors = [leverage_colors[leverage_order.index(l)] for l in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': counts,
            'marker': {'colors': colors},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'showlegend': True,
            'height': 400,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="leverage-distribution-pie", height=400)


def _create_ev_insights(ev_data: Dict) -> str:
    """Generate EV strategic insights"""
    
    if not ev_data:
        return ""
    
    total_companies = len(ev_data)
    total_ev = sum(m['enterprise_value'] for m in ev_data.values())
    avg_efficiency = np.mean([m['capital_efficiency'] for m in ev_data.values()])
    
    excellent_quality = sum(1 for m in ev_data.values() if m['ev_quality'] == 'Excellent')
    high_efficiency = sum(1 for m in ev_data.values() if m['capital_efficiency'] >= 7)
    
    low_leverage = sum(1 for m in ev_data.values() 
                      if m['leverage'] in ['Very Low', 'Low'])
    high_leverage = sum(1 for m in ev_data.values() 
                       if m['leverage'] in ['High', 'Very High'])
    
    avg_net_debt_ebitda = np.mean([m['net_debt_to_ebitda'] for m in ev_data.values() 
                                   if 0 < m['net_debt_to_ebitda'] < 20])
    
    insight_text = f"""
    <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #667eea;">
        <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">💡 Enterprise Value Strategic Insights</h5>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Portfolio Scale:</strong> 
            Total enterprise value of ${total_ev/1_000_000_000:.1f}B with average capital efficiency of {avg_efficiency:.1f}/10, 
            indicating {'excellent' if avg_efficiency >= 7 else 'good' if avg_efficiency >= 5 else 'fair'} 
            capital deployment across the portfolio.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">EV Quality Profile:</strong> 
            {excellent_quality}/{total_companies} companies achieve excellent EV quality ratings with {high_efficiency}/{total_companies} 
            demonstrating high capital efficiency (7+ score), representing 
            {'strong' if excellent_quality >= total_companies * 0.5 else 'moderate'} operational excellence.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Capital Structure:</strong> 
            {low_leverage}/{total_companies} companies maintain conservative leverage (Low/Very Low) while {high_leverage}/{total_companies} 
            carry elevated debt levels. Average Net Debt/EBITDA of {avg_net_debt_ebitda:.1f}x indicates 
            {'healthy' if avg_net_debt_ebitda < 2 else 'moderate' if avg_net_debt_ebitda < 3 else 'elevated'} leverage across the portfolio.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 0;">
            <strong style="color: var(--text-primary);">Strategic Positioning:</strong> 
            {'Strong capital efficiency and conservative leverage provide solid foundation for value creation' if high_efficiency >= total_companies * 0.5 and low_leverage >= total_companies * 0.5 else 'Balanced capital structure with opportunities for efficiency improvements' if avg_efficiency >= 5 else 'Focus required on capital efficiency enhancement and leverage optimization'}.
        </p>
    </div>
    """
    
    return insight_text


# =============================================================================
# SUBSECTION 7E: ANALYST VS MARKET VALUATION
# =============================================================================

def _build_section_7e_analyst_vs_market_valuation(
    df: pd.DataFrame,
    companies: Dict[str, str],
    analyst_targets: pd.DataFrame,
    prices_df: pd.DataFrame
) -> str:
    """Build Section 7E: Analyst vs Market Valuation"""
    
    html = """
    <div class="info-section">
        <h3>7E. Analyst vs Market Valuation</h3>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">
            Price target analysis, upside potential assessment, and analyst conviction scoring
        </p>
    """
    
    # Calculate analyst valuation metrics
    analyst_data = _calculate_analyst_valuation_metrics(df, companies, analyst_targets, prices_df)
    
    if not analyst_data:
        html += build_info_box(
            "<p>Insufficient analyst coverage data for analysis.</p>",
            "warning"
        )
        html += "</div>"
        return html
    
    # 7E.1: Analyst Coverage Summary
    html += """
        <div style="margin-top: 30px;">
            <h4>7E.1 Analyst Coverage Overview</h4>
    """
    
    coverage_cards = _create_analyst_coverage_cards(analyst_data)
    html += coverage_cards
    
    # 7E.2: Price Target Analysis Table
    html += """
        <div style="margin-top: 40px;">
            <h4>7E.2 Price Target vs Current Price Analysis</h4>
    """
    
    target_table = _create_price_target_table(analyst_data)
    html += target_table
    
    # 7E.3: Upside Potential Rankings
    html += """
        <div style="margin-top: 40px;">
            <h4>7E.3 Upside Potential Rankings</h4>
    """
    
    upside_analysis_html = _create_upside_potential_analysis(analyst_data)
    html += upside_analysis_html
    
    # 7E.4: Analyst Valuation Charts
    html += """
        <div style="margin-top: 40px;">
            <h4>7E.4 Analyst Valuation Visualizations</h4>
    """
    
    charts_html = _create_analyst_valuation_charts(analyst_data, companies)
    html += charts_html
    
    # 7E.5: Analyst Insights
    html += """
        <div style="margin-top: 40px;">
            <h4>7E.5 Analyst Conviction & Market Alignment</h4>
    """
    
    insights_html = _create_analyst_insights(analyst_data)
    html += insights_html
    
    html += "</div></div>"
    
    return html


def _calculate_analyst_valuation_metrics(
    df: pd.DataFrame,
    companies: Dict[str, str],
    analyst_targets: pd.DataFrame,
    prices_df: pd.DataFrame
) -> Dict[str, Dict]:
    """Calculate analyst valuation metrics"""
    
    if analyst_targets.empty:
        return {}
    
    analyst_data = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        current_price = latest.get('price', 0)
        
        # Get analyst targets
        analyst_info = analyst_targets[analyst_targets['Company'] == company_name]
        
        if analyst_info.empty or current_price <= 0:
            continue
        
        target_data = analyst_info.iloc[-1]
        metrics = {}
        
        # Price targets
        metrics['current_price'] = current_price
        metrics['target_high'] = target_data.get('targetHigh', 0)
        metrics['target_low'] = target_data.get('targetLow', 0)
        metrics['target_consensus'] = target_data.get('targetConsensus', 0)
        metrics['target_median'] = target_data.get('targetMedian', 0)
        
        # Calculate upside/downside
        if metrics['target_consensus'] > 0:
            metrics['upside_consensus'] = ((metrics['target_consensus'] - current_price) / current_price) * 100
        else:
            metrics['upside_consensus'] = 0
        
        if metrics['target_median'] > 0:
            metrics['upside_median'] = ((metrics['target_median'] - current_price) / current_price) * 100
        else:
            metrics['upside_median'] = 0
        
        if metrics['target_high'] > 0:
            metrics['upside_high'] = ((metrics['target_high'] - current_price) / current_price) * 100
        else:
            metrics['upside_high'] = 0
        
        if metrics['target_low'] > 0:
            metrics['upside_low'] = ((metrics['target_low'] - current_price) / current_price) * 100
        else:
            metrics['upside_low'] = 0
        
        # Target range spread (measures analyst disagreement)
        if metrics['target_high'] > 0 and metrics['target_low'] > 0:
            metrics['target_spread'] = ((metrics['target_high'] - metrics['target_low']) / 
                                       metrics['target_low']) * 100
        else:
            metrics['target_spread'] = 0
        
        # Conviction score (based on spread - lower spread = higher conviction)
        if metrics['target_spread'] > 0:
            if metrics['target_spread'] < 20:
                metrics['conviction'] = 'High'
                metrics['conviction_score'] = 9
            elif metrics['target_spread'] < 40:
                metrics['conviction'] = 'Medium-High'
                metrics['conviction_score'] = 7
            elif metrics['target_spread'] < 60:
                metrics['conviction'] = 'Medium'
                metrics['conviction_score'] = 5
            elif metrics['target_spread'] < 80:
                metrics['conviction'] = 'Medium-Low'
                metrics['conviction_score'] = 3
            else:
                metrics['conviction'] = 'Low'
                metrics['conviction_score'] = 1
        else:
            metrics['conviction'] = 'Unknown'
            metrics['conviction_score'] = 5
        
        # Recommendation based on upside
        upside = metrics['upside_consensus']
        if upside > 25:
            metrics['recommendation'] = 'Strong Buy'
        elif upside > 15:
            metrics['recommendation'] = 'Buy'
        elif upside > 5:
            metrics['recommendation'] = 'Accumulate'
        elif upside > -5:
            metrics['recommendation'] = 'Hold'
        elif upside > -15:
            metrics['recommendation'] = 'Reduce'
        else:
            metrics['recommendation'] = 'Sell'
        
        # Market alignment (is market price close to consensus?)
        price_to_consensus_ratio = current_price / metrics['target_consensus'] if metrics['target_consensus'] > 0 else 1
        if 0.95 <= price_to_consensus_ratio <= 1.05:
            metrics['market_alignment'] = 'Aligned'
        elif price_to_consensus_ratio < 0.95:
            metrics['market_alignment'] = 'Below Target'
        else:
            metrics['market_alignment'] = 'Above Target'
        
        analyst_data[company_name] = metrics
    
    return analyst_data


def _create_analyst_coverage_cards(analyst_data: Dict) -> str:
    """Create analyst coverage summary cards"""
    
    if not analyst_data:
        return ""
    
    total_coverage = len(analyst_data)
    avg_upside = np.mean([m['upside_consensus'] for m in analyst_data.values()])
    
    strong_buy_count = sum(1 for m in analyst_data.values() 
                          if m['recommendation'] in ['Strong Buy', 'Buy'])
    
    high_conviction = sum(1 for m in analyst_data.values() 
                         if m['conviction'] in ['High', 'Medium-High'])
    
    cards = [
        {
            "label": "Companies Covered",
            "value": f"{total_coverage}",
            "description": "With analyst price targets",
            "type": "info"
        },
        {
            "label": "Avg Upside to Target",
            "value": f"{avg_upside:+.1f}%",
            "description": "Consensus target vs current price",
            "type": "success" if avg_upside > 10 else "info" if avg_upside > 0 else "warning"
        },
        {
            "label": "Buy Recommendations",
            "value": f"{strong_buy_count}/{total_coverage}",
            "description": "Strong Buy or Buy ratings",
            "type": "success" if strong_buy_count >= total_coverage * 0.5 else "info"
        },
        {
            "label": "High Conviction",
            "value": f"{high_conviction}/{total_coverage}",
            "description": "Low target spread indicates agreement",
            "type": "success" if high_conviction >= total_coverage * 0.6 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_price_target_table(analyst_data: Dict) -> str:
    """Create price target analysis table"""
    
    if not analyst_data:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, metrics in analyst_data.items():
        table_data.append({
            'Company': company_name,
            'Current Price': f"${metrics['current_price']:.2f}",
            'Target Low': f"${metrics['target_low']:.2f}",
            'Target Consensus': f"${metrics['target_consensus']:.2f}",
            'Target High': f"${metrics['target_high']:.2f}",
            'Upside to Consensus': f"{metrics['upside_consensus']:+.1f}%",
            'Target Spread': f"{metrics['target_spread']:.0f}%",
            'Conviction': metrics['conviction'],
            'Recommendation': metrics['recommendation']
        })
    
    df_table = pd.DataFrame(table_data)
    df_table = df_table.sort_values('Upside to Consensus', ascending=False)
    
    # Color coding
    def conviction_color(val):
        if 'High' in val and 'Low' not in val:
            return 'excellent'
        elif 'Medium-High' in val:
            return 'good'
        elif 'Medium' in val and 'High' not in val and 'Low' not in val:
            return 'neutral'
        elif 'Medium-Low' in val:
            return 'fair'
        else:
            return 'poor'
    
    def recommendation_color(val):
        if 'Strong Buy' in val:
            return 'excellent'
        elif 'Buy' in val or 'Accumulate' in val:
            return 'good'
        elif 'Hold' in val:
            return 'neutral'
        elif 'Reduce' in val:
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'Conviction': conviction_color,
        'Recommendation': recommendation_color
    }
    
    badge_columns = ['Conviction', 'Recommendation']
    
    return build_enhanced_table(
        df_table,
        table_id="price-target-table",
        color_columns=color_columns,
        badge_columns=badge_columns,
        sortable=True,
        searchable=True
    )


def _create_upside_potential_analysis(analyst_data: Dict) -> str:
    """Create upside potential analysis section"""
    
    if not analyst_data:
        return ""
    
    # Group by upside ranges
    upside_groups = {
        'High Upside (>25%)': [],
        'Moderate Upside (15-25%)': [],
        'Low Upside (5-15%)': [],
        'Fairly Valued (±5%)': [],
        'Overvalued (>5% downside)': []
    }
    
    for company_name, metrics in analyst_data.items():
        upside = metrics['upside_consensus']
        if upside > 25:
            upside_groups['High Upside (>25%)'].append(company_name)
        elif upside > 15:
            upside_groups['Moderate Upside (15-25%)'].append(company_name)
        elif upside > 5:
            upside_groups['Low Upside (5-15%)'].append(company_name)
        elif upside >= -5:
            upside_groups['Fairly Valued (±5%)'].append(company_name)
        else:
            upside_groups['Overvalued (>5% downside)'].append(company_name)
    
    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">'
    
    upside_colors = {
        'High Upside (>25%)': '#10b981',
        'Moderate Upside (15-25%)': '#43e97b',
        'Low Upside (5-15%)': '#3b82f6',
        'Fairly Valued (±5%)': '#667eea',
        'Overvalued (>5% downside)': '#ef4444'
    }
    
    for group_name, companies_in_group in upside_groups.items():
        if not companies_in_group:
            continue
        
        count = len(companies_in_group)
        color = upside_colors[group_name]
        
        html += f"""
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border-left: 4px solid {color};">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">{group_name}</h5>
            <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 10px;">
                {count}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.85rem;">
                {'<br>'.join([f"• {c[:15]}" for c in companies_in_group[:3]])}
                {' + more...' if count > 3 else ''}
            </div>
        </div>
        """
    
    html += '</div>'
    
    return html


def _create_analyst_valuation_charts(analyst_data: Dict, companies: Dict) -> str:
    """Create analyst valuation charts"""
    
    charts_html = ""
    
    # Chart 1: Upside Potential Rankings
    chart1_html = _create_upside_potential_chart(analyst_data)
    if chart1_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Upside Potential to Consensus Target</h5>
            {chart1_html}
        </div>
        """
    
    # Chart 2: Price Target Ranges
    chart2_html = _create_price_target_range_chart(analyst_data)
    if chart2_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Analyst Price Target Ranges</h5>
            {chart2_html}
        </div>
        """
    
    # Chart 3: Conviction vs Upside Scatter
    chart3_html = _create_conviction_upside_scatter(analyst_data)
    if chart3_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Analyst Conviction vs Upside Potential</h5>
            {chart3_html}
        </div>
        """
    
    # Chart 4: Recommendation Distribution
    chart4_html = _create_recommendation_distribution(analyst_data)
    if chart4_html:
        charts_html += f"""
        <div style="margin-bottom: 30px;">
            <h5 style="color: var(--text-primary); margin-bottom: 15px;">Analyst Recommendation Distribution</h5>
            {chart4_html}
        </div>
        """
    
    return charts_html


def _create_upside_potential_chart(analyst_data: Dict) -> str:
    """Create upside potential ranking chart"""
    
    if not analyst_data:
        return ""
    
    # Sort by upside
    sorted_companies = sorted(analyst_data.items(), 
                             key=lambda x: x[1]['upside_consensus'], 
                             reverse=True)
    
    companies_list = [name for name, _ in sorted_companies]
    upside = [metrics['upside_consensus'] for _, metrics in sorted_companies]
    
    # Color based on upside magnitude
    colors = []
    for u in upside:
        if u > 25:
            colors.append('#10b981')
        elif u > 15:
            colors.append('#43e97b')
        elif u > 5:
            colors.append('#3b82f6')
        elif u >= -5:
            colors.append('#667eea')
        else:
            colors.append('#ef4444')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'y': companies_list,
            'x': upside,
            'orientation': 'h',
            'marker': {'color': colors},
            'text': [f"{u:+.1f}%" for u in upside],
            'textposition': 'auto',
            'hovertemplate': '<b>%{y}</b><br>Upside: %{x:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Upside to Consensus Target (%)', 'gridcolor': 'rgba(128,128,128,0.2)', 'zeroline': True},
            'yaxis': {'title': ''},
            'height': max(400, len(companies_list) * 40),
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="upside-potential-chart", height=max(400, len(companies_list) * 40))


def _create_price_target_range_chart(analyst_data: Dict) -> str:
    """Create price target range visualization"""
    
    if not analyst_data:
        return ""
    
    companies_list = list(analyst_data.keys())
    
    # Prepare data for box plot style visualization
    traces = []
    
    for company in companies_list:
        metrics = analyst_data[company]
        
        # Create a trace for each company showing range
        traces.append({
            'type': 'scatter',
            'mode': 'markers',
            'x': [metrics['target_low'], metrics['target_consensus'], metrics['target_high']],
            'y': [company, company, company],
            'marker': {
                'size': [8, 12, 8],
                'color': ['#ef4444', '#3b82f6', '#10b981'],
                'symbol': ['diamond', 'circle', 'diamond']
            },
            'name': company,
            'showlegend': False,
            'hovertemplate': '%{y}<br>Price: $%{x:.2f}<extra></extra>'
        })
        
        # Add current price as a different marker
        traces.append({
            'type': 'scatter',
            'mode': 'markers',
            'x': [metrics['current_price']],
            'y': [company],
            'marker': {
                'size': 10,
                'color': '#f59e0b',
                'symbol': 'x',
                'line': {'width': 2}
            },
            'name': company,
            'showlegend': False,
            'hovertemplate': '%{y}<br>Current: $%{x:.2f}<extra></extra>'
        })
        
        # Add line connecting low to high
        traces.append({
            'type': 'scatter',
            'mode': 'lines',
            'x': [metrics['target_low'], metrics['target_high']],
            'y': [company, company],
            'line': {'color': 'rgba(128,128,128,0.3)', 'width': 2},
            'showlegend': False,
            'hoverinfo': 'skip'
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Price ($)', 'gridcolor': 'rgba(128,128,128,0.2)'},
            'yaxis': {'title': ''},
            'height': max(400, len(companies_list) * 50),
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'annotations': [
                {
                    'x': 0.02,
                    'y': 1.05,
                    'xref': 'paper',
                    'yref': 'paper',
                    'text': '🔴 Low | 🔵 Consensus | 🟢 High | ✖️ Current',
                    'showarrow': False,
                    'font': {'size': 10}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="price-target-range-chart", height=max(400, len(companies_list) * 50))


def _create_conviction_upside_scatter(analyst_data: Dict) -> str:
    """Create conviction vs upside scatter chart"""
    
    if not analyst_data:
        return ""
    
    companies_list = list(analyst_data.keys())
    conviction_scores = [analyst_data[c]['conviction_score'] for c in companies_list]
    upside = [analyst_data[c]['upside_consensus'] for c in companies_list]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': conviction_scores,
            'y': upside,
            'text': [c[:8] for c in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': upside,
                'colorscale': [[0, '#ef4444'], [0.5, '#667eea'], [1, '#10b981']],
                'showscale': True,
                'colorbar': {'title': 'Upside<br>(%)'}
            },
            'hovertemplate': '<b>%{text}</b><br>Conviction: %{x}/10<br>Upside: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Analyst Conviction Score (0-10)', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 10]},
            'yaxis': {'title': 'Upside to Consensus (%)', 'gridcolor': 'rgba(128,128,128,0.2)', 'zeroline': True},
            'annotations': [
                {
                    'x': 7.5,
                    'y': max(upside) * 0.8 if upside else 20,
                    'text': 'High Conviction<br>+ High Upside',
                    'showarrow': False,
                    'font': {'color': 'rgba(16,185,129,0.7)', 'size': 12, 'weight': 'bold'}
                }
            ],
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="conviction-upside-scatter", height=500)


def _create_recommendation_distribution(analyst_data: Dict) -> str:
    """Create analyst recommendation distribution pie chart"""
    
    if not analyst_data:
        return ""
    
    # Count recommendations
    rec_counts = {}
    for metrics in analyst_data.values():
        rec = metrics['recommendation']
        rec_counts[rec] = rec_counts.get(rec, 0) + 1
    
    rec_order = ['Strong Buy', 'Buy', 'Accumulate', 'Hold', 'Reduce', 'Sell']
    labels = [r for r in rec_order if r in rec_counts]
    counts = [rec_counts[r] for r in labels]
    
    rec_colors = ['#10b981', '#43e97b', '#3b82f6', '#667eea', '#f59e0b', '#ef4444']
    colors = [rec_colors[rec_order.index(r)] for r in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': counts,
            'marker': {'colors': colors},
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'showlegend': True,
            'height': 400,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="recommendation-distribution-pie", height=400)


def _create_analyst_insights(analyst_data: Dict) -> str:
    """Generate analyst valuation insights"""
    
    if not analyst_data:
        return ""
    
    total_coverage = len(analyst_data)
    avg_upside = np.mean([m['upside_consensus'] for m in analyst_data.values()])
    
    high_upside = sum(1 for m in analyst_data.values() if m['upside_consensus'] > 20)
    strong_buy = sum(1 for m in analyst_data.values() if m['recommendation'] == 'Strong Buy')
    high_conviction = sum(1 for m in analyst_data.values() if m['conviction'] in ['High', 'Medium-High'])
    
    avg_spread = np.mean([m['target_spread'] for m in analyst_data.values()])
    
    insight_text = f"""
    <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #667eea;">
        <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">💡 Analyst Valuation Insights</h5>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Consensus Outlook:</strong> 
            Average {avg_upside:+.1f}% upside to consensus targets across {total_coverage} covered companies indicates 
            {'strong' if avg_upside > 15 else 'moderate' if avg_upside > 5 else 'limited'} price appreciation potential 
            based on analyst expectations.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">High-Conviction Opportunities:</strong> 
            {high_upside}/{total_coverage} companies with >20% upside potential and {strong_buy} Strong Buy ratings, 
            representing {'abundant' if high_upside >= total_coverage * 0.4 else 'selective'} high-conviction opportunities.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;">
            <strong style="color: var(--text-primary);">Analyst Agreement:</strong> 
            Average target spread of {avg_spread:.0f}% with {high_conviction}/{total_coverage} companies showing high conviction 
            (low spread), indicating {'strong' if high_conviction >= total_coverage * 0.6 else 'moderate' if high_conviction >= total_coverage * 0.4 else 'mixed'} 
            analyst alignment on valuations.
        </p>
        
        <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 0;">
            <strong style="color: var(--text-primary);">Strategic Positioning:</strong> 
            {'Strong analyst support with high conviction provides validation for accumulation strategy' if strong_buy >= total_coverage * 0.4 and high_conviction >= total_coverage * 0.5 else 'Selective analyst support suggests careful position sizing and continued monitoring' if avg_upside > 5 else 'Limited analyst upside warrants focus on other valuation metrics and fundamental analysis'}.
        </p>
    </div>
    """
    
    return insight_text


# =============================================================================
# SUBSECTION 7F: EXECUTIVE DASHBOARD & STRATEGIC INSIGHTS
# =============================================================================

def _build_section_7f_executive_dashboard(
    df: pd.DataFrame,
    companies: Dict[str, str],
    analyst_targets: pd.DataFrame,
    profiles_df: pd.DataFrame
) -> str:
    """Build Section 7F: Executive Valuation Dashboard & Strategic Insights"""
    
    # Calculate all metrics needed for dashboard
    dashboard_data = _calculate_dashboard_metrics(df, companies, analyst_targets, profiles_df)
    
    if not dashboard_data:
        return """
        <div class="info-section">
            <h3>7F. Executive Valuation Dashboard & Strategic Insights</h3>
            <p style="color: var(--text-secondary);">
                Insufficient data for executive dashboard generation.
            </p>
        </div>
        """
    
    html = """
    <div class="info-section">
        <h3>7F. Executive Valuation Dashboard & Strategic Insights</h3>
        <p style="color: var(--text-secondary); margin-bottom: 40px;">
            Actionable portfolio overview with prioritized recommendations and visual intelligence
        </p>
    """
    
    # PART 1: EXECUTIVE SUMMARY AT TOP
    html += """
        <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); 
                    padding: 40px; border-radius: 16px; margin-bottom: 40px; border: 2px solid rgba(102,126,234,0.3);">
            <h2 style="text-align: center; color: var(--text-primary); margin-bottom: 35px; font-size: 2rem;">
                📊 Executive Valuation Summary
            </h2>
    """
    
    # 1.1 Portfolio Valuation Snapshot (Hero Cards)
    hero_cards_html = _create_hero_summary_cards(dashboard_data)
    html += hero_cards_html
    
    # 1.2 Key Takeaways (3 Critical Insights)
    key_takeaways_html = _create_key_takeaways(dashboard_data)
    html += key_takeaways_html
    
    # 1.3 Top 3 Action Priorities
    action_priorities_html = _create_action_priorities(dashboard_data)
    html += action_priorities_html
    
    # 1.4 Portfolio Health Metrics
    health_metrics_html = _create_portfolio_health_metrics(dashboard_data)
    html += health_metrics_html
    
    # 1.5 Quick Alerts
    alerts_html = _create_quick_alerts(dashboard_data)
    html += alerts_html
    
    html += "</div>"  # Close executive summary section
    
    # EXPANDABLE DIVIDER
    html += """
        <div style="text-align: center; margin: 50px 0;">
            <div style="height: 2px; background: linear-gradient(90deg, transparent, var(--primary-gradient-start), var(--primary-gradient-end), transparent); 
                       margin-bottom: 20px;"></div>
            <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-secondary);">
                📊 Detailed Analysis & Interactive Tools Below
            </div>
            <div style="font-size: 0.9rem; color: var(--text-tertiary); margin-top: 10px;">
                Comprehensive valuation matrix, opportunity heatmap, and strategic recommendations
            </div>
            <div style="height: 2px; background: linear-gradient(90deg, transparent, var(--primary-gradient-start), var(--primary-gradient-end), transparent); 
                       margin-top: 20px;"></div>
        </div>
    """
    
    # PART 2: DETAILED INTERACTIVE ANALYSIS
    
    # 2.1 Value Opportunity Heatmap
    html += """
        <div style="margin-top: 40px;">
            <h4>📈 Valuation Opportunity Heatmap</h4>
    """
    heatmap_html = _create_opportunity_heatmap(dashboard_data)
    html += heatmap_html
    
    # 2.2 Risk-Return Quadrant
    html += """
        <div style="margin-top: 40px;">
            <h4>🎯 Risk-Return Positioning Matrix</h4>
    """
    quadrant_html = _create_risk_return_quadrant(dashboard_data)
    html += quadrant_html
    
    # 2.3 Comprehensive Recommendations Table
    html += """
        <div style="margin-top: 40px;">
            <h4>📋 Comprehensive Investment Recommendations</h4>
    """
    recommendations_table_html = _create_comprehensive_recommendations_table(dashboard_data)
    html += recommendations_table_html
    
    html += "</div></div>"
    
    return html


def _calculate_dashboard_metrics(
    df: pd.DataFrame,
    companies: Dict[str, str],
    analyst_targets: pd.DataFrame,
    profiles_df: pd.DataFrame
) -> Dict[str, Any]:
    """Calculate all metrics needed for executive dashboard"""
    
    dashboard_data = {
        'companies': {},
        'portfolio_metrics': {},
        'opportunities': [],
        'risks': [],
        'alerts': []
    }
    
    # Recalculate key metrics for each company
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        company_metrics = {}
        
        # Valuation metrics
        company_metrics['pe_ratio'] = latest.get('priceToEarningsRatio', 0)
        company_metrics['pb_ratio'] = latest.get('priceToBookRatio', 0)
        company_metrics['ev_ebitda'] = latest.get('evToEBITDA', 0)
        
        # Quality metrics
        company_metrics['roe'] = latest.get('returnOnEquity', 0)
        company_metrics['roic'] = latest.get('returnOnInvestedCapital', 0)
        
        # Growth metrics
        if len(company_data) >= 2:
            current_revenue = latest.get('revenue', 0)
            previous_revenue = company_data.iloc[-2].get('revenue', 0)
            company_metrics['revenue_growth'] = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        else:
            company_metrics['revenue_growth'] = 0
        
        # Calculate composite valuation score
        pe_score = max(0, min(10, (30 - company_metrics['pe_ratio']) / 3)) if company_metrics['pe_ratio'] > 0 else 5
        quality_score = (company_metrics['roe'] + company_metrics['roic']) / 4
        growth_bonus = min(2, company_metrics['revenue_growth'] / 10)
        
        company_metrics['valuation_score'] = min(10, pe_score + (quality_score / 10) * 2 + growth_bonus)
        
        # Analyst data
        if not analyst_targets.empty:
            analyst_info = analyst_targets[analyst_targets['Company'] == company_name]
            if not analyst_info.empty:
                target_data = analyst_info.iloc[-1]
                current_price = latest.get('price', 0)
                target_consensus = target_data.get('targetConsensus', 0)
                
                if current_price > 0 and target_consensus > 0:
                    company_metrics['analyst_upside'] = ((target_consensus - current_price) / current_price) * 100
                else:
                    company_metrics['analyst_upside'] = 0
            else:
                company_metrics['analyst_upside'] = 0
        else:
            company_metrics['analyst_upside'] = 0
        
        # Risk assessment
        debt_to_equity = latest.get('debtToEquityRatio', 0)
        if company_metrics['pe_ratio'] < 15 and company_metrics['roe'] > 10 and debt_to_equity < 1.0:
            company_metrics['risk_level'] = 'Low'
        elif company_metrics['pe_ratio'] < 25 and company_metrics['roe'] > 5:
            company_metrics['risk_level'] = 'Medium'
        else:
            company_metrics['risk_level'] = 'High'
        
        # Action recommendation
        if company_metrics['valuation_score'] >= 8 and company_metrics['analyst_upside'] > 15:
            company_metrics['action'] = 'Strong Buy'
            company_metrics['priority'] = 'HIGH'
        elif company_metrics['valuation_score'] >= 7:
            company_metrics['action'] = 'Buy'
            company_metrics['priority'] = 'MEDIUM'
        elif company_metrics['valuation_score'] >= 5:
            company_metrics['action'] = 'Hold'
            company_metrics['priority'] = 'LOW'
        elif company_metrics['valuation_score'] >= 3:
            company_metrics['action'] = 'Reduce'
            company_metrics['priority'] = 'MEDIUM'
        else:
            company_metrics['action'] = 'Sell'
            company_metrics['priority'] = 'HIGH'
        
        dashboard_data['companies'][company_name] = company_metrics
    
    if not dashboard_data['companies']:
        return {}
    
    # Calculate portfolio-level metrics
    all_scores = [m['valuation_score'] for m in dashboard_data['companies'].values()]
    all_upsides = [m['analyst_upside'] for m in dashboard_data['companies'].values() if m['analyst_upside'] != 0]
    
    dashboard_data['portfolio_metrics'] = {
        'avg_valuation_score': np.mean(all_scores),
        'avg_analyst_upside': np.mean(all_upsides) if all_upsides else 0,
        'value_opportunities': sum(1 for m in dashboard_data['companies'].values() if m['valuation_score'] >= 7),
        'strong_buy_count': sum(1 for m in dashboard_data['companies'].values() if m['action'] == 'Strong Buy'),
        'high_risk_count': sum(1 for m in dashboard_data['companies'].values() if m['risk_level'] == 'High'),
        'total_companies': len(dashboard_data['companies'])
    }
    
    # Identify top opportunities
    opportunities = []
    for company_name, metrics in sorted(dashboard_data['companies'].items(), 
                                       key=lambda x: x[1]['valuation_score'], 
                                       reverse=True)[:5]:
        opportunities.append({
            'company': company_name,
            'score': metrics['valuation_score'],
            'upside': metrics['analyst_upside'],
            'action': metrics['action'],
            'priority': metrics['priority']
        })
    
    dashboard_data['opportunities'] = opportunities
    
    # Identify risks
    risks = []
    for company_name, metrics in dashboard_data['companies'].items():
        if metrics['valuation_score'] < 4 or (metrics['pe_ratio'] > 40 and metrics['revenue_growth'] < 5):
            risks.append({
                'company': company_name,
                'reason': 'Overvalued' if metrics['pe_ratio'] > 40 else 'Low score',
                'action': metrics['action']
            })
    
    dashboard_data['risks'] = risks[:5]  # Top 5 risks
    
    # Generate alerts
    alerts = []
    for company_name, metrics in dashboard_data['companies'].items():
        if metrics['valuation_score'] >= 8 and metrics['analyst_upside'] > 20:
            alerts.append({
                'type': 'opportunity',
                'company': company_name,
                'message': f"High-conviction opportunity: {metrics['valuation_score']:.1f}/10 score + {metrics['analyst_upside']:.0f}% upside"
            })
        elif metrics['pe_ratio'] > 45:
            alerts.append({
                'type': 'warning',
                'company': company_name,
                'message': f"Extreme valuation: P/E of {metrics['pe_ratio']:.0f}x"
            })
    
    dashboard_data['alerts'] = alerts[:6]  # Top 6 alerts
    
    return dashboard_data


def _create_hero_summary_cards(dashboard_data: Dict) -> str:
    """Create hero summary stat cards"""
    
    pm = dashboard_data['portfolio_metrics']
    
    cards = [
        {
            "label": "Portfolio Valuation Score",
            "value": f"{pm['avg_valuation_score']:.1f}/10",
            "description": f"{'Above Average' if pm['avg_valuation_score'] >= 6 else 'Fair' if pm['avg_valuation_score'] >= 5 else 'Below Average'} Positioning",
            "type": "success" if pm['avg_valuation_score'] >= 6 else "info"
        },
        {
            "label": "Value Opportunities",
            "value": f"{pm['value_opportunities']}/{pm['total_companies']}",
            "description": f"{'Abundant' if pm['value_opportunities'] >= pm['total_companies'] * 0.5 else 'Moderate'} Entry Points",
            "type": "success" if pm['value_opportunities'] >= pm['total_companies'] * 0.5 else "info"
        },
        {
            "label": "Growth Supported",
            "value": f"{pm['strong_buy_count']}/{pm['total_companies']}",
            "description": f"{'Strong' if pm['strong_buy_count'] >= pm['total_companies'] * 0.4 else 'Selective'} Buy Signals",
            "type": "success" if pm['strong_buy_count'] >= pm['total_companies'] * 0.4 else "info"
        },
        {
            "label": "Analyst Confidence",
            "value": f"{pm['avg_analyst_upside']:+.0f}%" if pm['avg_analyst_upside'] != 0 else "N/A",
            "description": f"{'Strong' if pm['avg_analyst_upside'] > 15 else 'Moderate' if pm['avg_analyst_upside'] > 5 else 'Limited'} Upside",
            "type": "success" if pm['avg_analyst_upside'] > 10 else "info" if pm['avg_analyst_upside'] > 0 else "warning"
        }
    ]
    
    return f"""
    <div style="margin-bottom: 40px;">
        {build_stat_grid(cards)}
    </div>
    """


def _create_key_takeaways(dashboard_data: Dict) -> str:
    """Create key takeaway insight cards"""
    
    pm = dashboard_data['portfolio_metrics']
    opportunities = dashboard_data['opportunities']
    
    # Get top 3 opportunities
    top_3 = opportunities[:3] if len(opportunities) >= 3 else opportunities
    
    insight1 = f"{pm['value_opportunities']} companies trading at attractive valuations (7+ scores) with combined upside potential"
    
    insight2 = f"Top opportunities: {', '.join([opp['company'][:15] for opp in top_3])}"
    
    insight3_risk = f"{pm['high_risk_count']} companies require monitoring" if pm['high_risk_count'] > 0 else "Low risk profile across portfolio"
    
    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #10b981;">
            <div style="font-size: 1.5rem; margin-bottom: 10px;">💡</div>
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">CRITICAL INSIGHT #1: Value Opportunities</h5>
            <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                {insight1}
            </p>
            <div style="margin-top: 15px; padding: 10px; background: rgba(16,185,129,0.1); border-radius: 6px;">
                <strong style="color: #10b981;">🎬 ACTION:</strong> 
                <span style="color: var(--text-secondary);">Prioritize accumulation in next 30 days</span>
            </div>
        </div>
        
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <div style="font-size: 1.5rem; margin-bottom: 10px;">💡</div>
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">CRITICAL INSIGHT #2: Top Picks</h5>
            <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                {insight2}
            </p>
            <div style="margin-top: 15px; padding: 10px; background: rgba(59,130,246,0.1); border-radius: 6px;">
                <strong style="color: #3b82f6;">🎬 ACTION:</strong> 
                <span style="color: var(--text-secondary);">High conviction positions</span>
            </div>
        </div>
        
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 4px solid #f59e0b;">
            <div style="font-size: 1.5rem; margin-bottom: 10px;">💡</div>
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">CRITICAL INSIGHT #3: Risk Profile</h5>
            <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                {insight3_risk}
            </p>
            <div style="margin-top: 15px; padding: 10px; background: rgba(245,158,11,0.1); border-radius: 6px;">
                <strong style="color: #f59e0b;">🎬 ACTION:</strong> 
                <span style="color: var(--text-secondary);">{'Monitor and rebalance as needed' if pm['high_risk_count'] > 0 else 'Maintain quality focus'}</span>
            </div>
        </div>
    </div>
    """
    
    return html


def _create_action_priorities(dashboard_data: Dict) -> str:
    """Create top 3 action priority cards"""
    
    opportunities = dashboard_data['opportunities'][:3]
    risks = dashboard_data['risks'][:2]
    
    html = """
    <div style="margin: 40px 0;">
        <h4 style="text-align: center; color: var(--text-primary); margin-bottom: 25px;">
            🎯 Top Priority Actions
        </h4>
        <div style="display: grid; gap: 20px;">
    """
    
    # Top opportunities
    for i, opp in enumerate(opportunities[:2]):
        action_color = '#10b981' if opp['action'] == 'Strong Buy' else '#3b82f6'
        html += f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 5px solid {action_color};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <span style="background: {action_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 700;">
                        #{i+1} {opp['priority']} PRIORITY
                    </span>
                    <h5 style="margin: 10px 0 5px 0; color: var(--text-primary); font-size: 1.3rem;">
                        {opp['company']}
                    </h5>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.85rem; color: var(--text-tertiary);">Risk Level</div>
                    <div style="font-weight: 700; color: var(--text-primary);">
                        {dashboard_data['companies'][opp['company']]['risk_level']}
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px;">
                <div>
                    <div style="font-size: 0.8rem; color: var(--text-tertiary);">Valuation Score</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {action_color};">
                        {opp['score']:.1f}/10
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: var(--text-tertiary);">Analyst Upside</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {action_color};">
                        {opp['upside']:+.0f}%
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: var(--text-tertiary);">P/E Ratio</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-primary);">
                        {dashboard_data['companies'][opp['company']]['pe_ratio']:.1f}x
                    </div>
                </div>
            </div>
            <div style="background: rgba(16,185,129,0.1); padding: 12px; border-radius: 8px;">
                <strong style="color: {action_color};">🎯 {opp['action'].upper()}:</strong>
                <span style="color: var(--text-secondary);">
                    {'Accumulate 15-20% position over next 30 days' if opp['action'] == 'Strong Buy' else 'Initiate or add to position'}
                </span>
            </div>
        </div>
        """
    
    # Top risk if exists
    if risks:
        risk = risks[0]
        html += f"""
        <div style="background: var(--card-bg); padding: 25px; border-radius: 12px; border-left: 5px solid #ef4444;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 700;">
                        #3 IMMEDIATE ACTION
                    </span>
                    <h5 style="margin: 10px 0 5px 0; color: var(--text-primary); font-size: 1.3rem;">
                        {risk['company']}
                    </h5>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.85rem; color: var(--text-tertiary);">Issue</div>
                    <div style="font-weight: 700; color: #ef4444;">
                        {risk['reason']}
                    </div>
                </div>
            </div>
            <div style="background: rgba(239,68,68,0.1); padding: 12px; border-radius: 8px;">
                <strong style="color: #ef4444;">⚠️ {risk['action'].upper()}:</strong>
                <span style="color: var(--text-secondary);">
                    Reduce exposure by 40-50% over next 30 days
                </span>
            </div>
        </div>
        """
    
    html += "</div></div>"
    
    return html


def _create_portfolio_health_metrics(dashboard_data: Dict) -> str:
    """Create portfolio health progress bars"""
    
    pm = dashboard_data['portfolio_metrics']
    
    # Calculate progress metrics
    value_capture_pct = (pm['value_opportunities'] / pm['total_companies']) * 100
    quality_metrics_pct = min(100, pm['avg_valuation_score'] * 10)
    analyst_support_pct = min(100, abs(pm['avg_analyst_upside']) * 5) if pm['avg_analyst_upside'] != 0 else 0
    risk_adjusted_pct = max(0, 100 - (pm['high_risk_count'] / pm['total_companies']) * 100)
    
    html = f"""
    <div style="margin: 40px 0; padding: 30px; background: var(--card-bg); border-radius: 12px;">
        <h4 style="text-align: center; color: var(--text-primary); margin-bottom: 25px;">
            📊 Portfolio Optimization Scorecard
        </h4>
        
        <div style="max-width: 800px; margin: 0 auto;">
            <div style="margin: 20px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-secondary);">Value Capture Efficiency</span>
                    <span style="font-weight: 700; color: var(--text-primary);">{value_capture_pct:.0f}% ➜ Target: 75%</span>
                </div>
                <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="width: {value_capture_pct}%; background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; transition: width 1s ease;"></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-secondary);">Quality Metrics</span>
                    <span style="font-weight: 700; color: var(--text-primary);">{quality_metrics_pct:.0f}% ➜ Target: 85%</span>
                </div>
                <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="width: {quality_metrics_pct}%; background: linear-gradient(90deg, #10b981, #059669); height: 100%; border-radius: 10px; transition: width 1s ease;"></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-secondary);">Analyst Coverage Quality</span>
                    <span style="font-weight: 700; color: var(--text-primary);">{analyst_support_pct:.0f}% ➜ Target: 80%</span>
                </div>
                <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="width: {analyst_support_pct}%; background: linear-gradient(90deg, #3b82f6, #2563eb); height: 100%; border-radius: 10px; transition: width 1s ease;"></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-secondary);">Risk-Adjusted Positioning</span>
                    <span style="font-weight: 700; color: var(--text-primary);">{risk_adjusted_pct:.0f}% ➜ Target: 90%</span>
                </div>
                <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="width: {risk_adjusted_pct}%; background: linear-gradient(90deg, #f59e0b, #d97706); height: 100%; border-radius: 10px; transition: width 1s ease;"></div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return html


def _create_quick_alerts(dashboard_data: Dict) -> str:
    """Create quick alerts panel"""
    
    alerts = dashboard_data['alerts']
    
    if not alerts:
        return ""
    
    html = """
    <div style="margin: 40px 0; padding: 25px; background: var(--card-bg); border-radius: 12px; border: 2px solid rgba(102,126,234,0.3);">
        <h4 style="color: var(--text-primary); margin-bottom: 20px;">
            ⚡ Active Signals & Alerts ({len(alerts)})
        </h4>
        <div style="display: grid; gap: 12px;">
    """
    
    for alert in alerts:
        icon = '🟢' if alert['type'] == 'opportunity' else '🔴' if alert['type'] == 'warning' else '🟡'
        color = '#10b981' if alert['type'] == 'opportunity' else '#ef4444' if alert['type'] == 'warning' else '#f59e0b'
        
        html += f"""
        <div style="display: flex; align-items: center; padding: 12px; background: rgba(0,0,0,0.02); border-radius: 8px; border-left: 3px solid {color};">
            <span style="font-size: 1.2rem; margin-right: 12px;">{icon}</span>
            <div style="flex: 1;">
                <strong style="color: var(--text-primary);">{alert['company']}:</strong>
                <span style="color: var(--text-secondary);"> {alert['message']}</span>
            </div>
        </div>
        """
    
    html += "</div></div>"
    
    return html


def _create_opportunity_heatmap(dashboard_data: Dict) -> str:
    """Create valuation opportunity heatmap table"""
    
    companies_data = dashboard_data['companies']
    
    if not companies_data:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, metrics in companies_data.items():
        table_data.append({
            'Company': company_name,
            'Val Score': f"{metrics['valuation_score']:.1f}",
            'P/E': f"{metrics['pe_ratio']:.1f}",
            'ROE': f"{metrics['roe']:.1f}%",
            'Growth': f"{metrics['revenue_growth']:.1f}%",
            'Analyst Upside': f"{metrics['analyst_upside']:+.0f}%" if metrics['analyst_upside'] != 0 else 'N/A',
            'Risk': metrics['risk_level'],
            'Action': metrics['action'],
            'Priority': metrics['priority']
        })
    
    df_table = pd.DataFrame(table_data)
    df_table = df_table.sort_values('Val Score', ascending=False)
    
    # Color coding
    def action_color(val):
        if 'Strong Buy' in val:
            return 'excellent'
        elif 'Buy' in val:
            return 'good'
        elif 'Hold' in val:
            return 'neutral'
        elif 'Reduce' in val:
            return 'fair'
        else:
            return 'poor'
    
    def risk_color(val):
        if 'Low' in val:
            return 'excellent'
        elif 'Medium' in val:
            return 'good'
        else:
            return 'poor'
    
    color_columns = {
        'Action': action_color,
        'Risk': risk_color
    }
    
    badge_columns = ['Action', 'Risk', 'Priority']
    
    return build_enhanced_table(
        df_table,
        table_id="opportunity-heatmap-table",
        color_columns=color_columns,
        badge_columns=badge_columns,
        sortable=True,
        searchable=True
    )


def _create_risk_return_quadrant(dashboard_data: Dict) -> str:
    """Create risk-return positioning quadrant chart"""
    
    companies_data = dashboard_data['companies']
    
    if not companies_data:
        return ""
    
    companies_list = list(companies_data.keys())
    risk_scores = []
    return_scores = []
    
    for company in companies_list:
        metrics = companies_data[company]
        
        # Risk score (0-10, lower is better)
        if metrics['risk_level'] == 'Low':
            risk_score = 2
        elif metrics['risk_level'] == 'Medium':
            risk_score = 5
        else:
            risk_score = 8
        
        risk_scores.append(risk_score)
        
        # Return score (valuation score + analyst upside bonus)
        return_score = metrics['valuation_score']
        if metrics['analyst_upside'] > 20:
            return_score += 2
        elif metrics['analyst_upside'] > 10:
            return_score += 1
        
        return_scores.append(min(10, return_score))
    
    # Color by action
    action_colors_map = {
        'Strong Buy': '#10b981',
        'Buy': '#43e97b',
        'Hold': '#3b82f6',
        'Reduce': '#f59e0b',
        'Sell': '#ef4444'
    }
    colors = [action_colors_map.get(companies_data[c]['action'], '#667eea') for c in companies_list]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': risk_scores,
            'y': return_scores,
            'text': [c[:8] for c in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 14,
                'color': colors,
                'line': {'width': 1, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Risk: %{x:.0f}/10<br>Return: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': {'text': '', 'font': {'size': 16}},
            'xaxis': {'title': 'Risk Level (Higher = More Risk)', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 10]},
            'yaxis': {'title': 'Return Potential (Higher = Better)', 'gridcolor': 'rgba(128,128,128,0.2)', 'range': [0, 12]},
            'shapes': [
                # Quadrant lines
                {'type': 'line', 'x0': 5, 'y0': 0, 'x1': 5, 'y1': 12, 'line': {'color': 'rgba(128,128,128,0.3)', 'dash': 'dash'}},
                {'type': 'line', 'x0': 0, 'y0': 6, 'x1': 10, 'y1': 6, 'line': {'color': 'rgba(128,128,128,0.3)', 'dash': 'dash'}}
            ],
            'annotations': [
                {'x': 2, 'y': 9, 'text': '🟢 IDEAL<br>Low Risk, High Return', 'showarrow': False, 'font': {'color': 'rgba(16,185,129,0.7)', 'size': 11, 'weight': 'bold'}},
                {'x': 8, 'y': 9, 'text': '⚠️ GROWTH<br>High Risk, High Return', 'showarrow': False, 'font': {'color': 'rgba(245,158,11,0.7)', 'size': 11, 'weight': 'bold'}},
                {'x': 2, 'y': 3, 'text': '🔵 DEFENSIVE<br>Low Risk, Low Return', 'showarrow': False, 'font': {'color': 'rgba(59,130,246,0.7)', 'size': 11, 'weight': 'bold'}},
                {'x': 8, 'y': 3, 'text': '🔴 AVOID<br>High Risk, Low Return', 'showarrow': False, 'font': {'color': 'rgba(239,68,68,0.7)', 'size': 11, 'weight': 'bold'}}
            ],
            'hovermode': 'closest',
            'showlegend': False,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-return-quadrant", height=600)


def _create_comprehensive_recommendations_table(dashboard_data: Dict) -> str:
    """Create comprehensive recommendations table with all details"""
    
    companies_data = dashboard_data['companies']
    
    if not companies_data:
        return ""
    
    # Build DataFrame
    table_data = []
    for company_name, metrics in companies_data.items():
        
        # Determine timeline
        if metrics['priority'] == 'HIGH':
            timeline = '0-30 days'
        elif metrics['priority'] == 'MEDIUM':
            timeline = '30-90 days'
        else:
            timeline = '90+ days'
        
        table_data.append({
            'Company': company_name,
            'Action': metrics['action'],
            'Priority': metrics['priority'],
            'Score': f"{metrics['valuation_score']:.1f}/10",
            'Upside': f"{metrics['analyst_upside']:+.0f}%" if metrics['analyst_upside'] != 0 else 'N/A',
            'Risk': metrics['risk_level'],
            'P/E': f"{metrics['pe_ratio']:.1f}x",
            'ROE': f"{metrics['roe']:.1f}%",
            'Growth': f"{metrics['revenue_growth']:.1f}%",
            'Timeline': timeline
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Sort by priority and score
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    df_table['priority_num'] = df_table['Priority'].map(priority_order)
    df_table = df_table.sort_values(['priority_num', 'Score'], ascending=[True, False])
    df_table = df_table.drop('priority_num', axis=1)
    
    # Color coding
    def action_color(val):
        if 'Strong Buy' in val:
            return 'excellent'
        elif 'Buy' in val:
            return 'good'
        elif 'Hold' in val:
            return 'neutral'
        elif 'Reduce' in val:
            return 'fair'
        else:
            return 'poor'
    
    def priority_color(val):
        if 'HIGH' in val:
            return 'excellent'
        elif 'MEDIUM' in val:
            return 'good'
        else:
            return 'neutral'
    
    def risk_color(val):
        if 'Low' in val:
            return 'excellent'
        elif 'Medium' in val:
            return 'good'
        else:
            return 'poor'
    
    color_columns = {
        'Action': action_color,
        'Priority': priority_color,
        'Risk': risk_color
    }
    
    badge_columns = ['Action', 'Priority', 'Risk']
    
    return build_enhanced_table(
        df_table,
        table_id="comprehensive-recommendations-table",
        color_columns=color_columns,
        badge_columns=badge_columns,
        sortable=True,
        searchable=True
    )