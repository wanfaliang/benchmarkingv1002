"""Section 5: Liquidity, Solvency & Capital Structure Analysis"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_stat_card,
    build_info_box,
    build_data_table,
    build_section_divider,
    build_plotly_chart,
    format_currency,
    format_percentage,
    format_number,
    build_enhanced_table,
    build_badge,
    build_score_badge,
    build_completeness_bar
)

def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 5 with Top 3 Priority Enhancements:
    1. Key Takeaways Box
    2. Section Navigation
    3. Trend Indicators
    
    This replaces the original generate() function
    """
    
    # Extract data from collector
    companies = collector.companies
    df = collector.get_all_financial_data()
    
    # Get additional datasets
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
    
    # Sector analysis placeholder
    sector_analysis = {'dominant_sector': 'Mixed'}
    
    # Generate all analyses (needed for key takeaways)
    liquidity_analysis = _analyze_enhanced_liquidity(df, companies, institutional_df, sector_analysis)
    solvency_analysis = _analyze_advanced_solvency(df, companies, economic_df, sector_analysis)
    capital_structure = _analyze_capital_structure_optimization(df, companies, economic_df, sector_analysis, institutional_df)
    balance_sheet_quality = _analyze_balance_sheet_quality(df, companies, sector_analysis)
    cash_flow_adequacy = _analyze_cash_flow_adequacy(df, companies, sector_analysis)
    
    # BUILD KEY TAKEAWAYS BOX (Enhancement #1)
    key_takeaways_html = _build_key_takeaways(
        liquidity_analysis, 
        solvency_analysis, 
        capital_structure, 
        balance_sheet_quality, 
        cash_flow_adequacy, 
        df, 
        len(companies)
    )
    
    # BUILD SECTION NAVIGATION (Enhancement #2)
    navigation_html = _build_section_navigation()
    
    # Build all subsections (reuse existing functions)
    section_5a_html = _build_section_5a_liquidity_analysis(
        df, companies, institutional_df, insider_df, sector_analysis
    )
    
    section_5b_html = _build_section_5b_solvency_analysis(
        df, companies, economic_df, sector_analysis
    )
    
    section_5c_html = _build_section_5c_capital_structure(
        df, companies, economic_df, sector_analysis, institutional_df
    )
    
    section_5d_html = _build_section_5d_balance_sheet_quality(
        df, companies, sector_analysis
    )
    
    section_5e_html = _build_section_5e_cash_flow_adequacy(
        df, companies, sector_analysis
    )
    
    section_5g_html = _build_section_5g_strategic_insights(
        df, companies, sector_analysis, institutional_df, economic_df
    )
    
    # Add anchor IDs to each section for navigation
    section_5a_html = f'<div id="section-5a">{section_5a_html}</div>'
    section_5b_html = f'<div id="section-5b">{section_5b_html}</div>'
    section_5c_html = f'<div id="section-5c">{section_5c_html}</div>'
    section_5d_html = f'<div id="section-5d">{section_5d_html}</div>'
    section_5e_html = f'<div id="section-5e">{section_5e_html}</div>'
    section_5g_html = f'<div id="section-5g">{section_5g_html}</div>'
    
    # Combine all content with enhancements
    content = f"""
    <div id="top"></div>
    <div class="section-content-wrapper">
        {key_takeaways_html}
        
        {navigation_html}
        
        {section_5a_html}
        {build_section_divider() if section_5b_html else ""}
        {section_5b_html}
        {build_section_divider() if section_5c_html else ""}
        {section_5c_html}
        {build_section_divider() if section_5d_html else ""}
        {section_5d_html}
        {build_section_divider() if section_5e_html else ""}
        {section_5e_html}
        {build_section_divider() if section_5g_html else ""}
        {section_5g_html}
    </div>
    """
    
    return generate_section_wrapper(5, "Liquidity, Solvency & Capital Structure", content)




# =============================================================================
# SUBSECTION 5A: ENHANCED LIQUIDITY ANALYSIS (COMPLETE)
# =============================================================================

def _build_section_5a_liquidity_analysis(
    df: pd.DataFrame,
    companies: Dict[str, str],
    institutional_df: pd.DataFrame,
    insider_df: pd.DataFrame,
    sector_analysis: Dict
) -> str:
    """Build complete Section 5A: Enhanced Liquidity Analysis & Stress Testing"""
    
    # Generate liquidity analysis
    liquidity_analysis = _analyze_enhanced_liquidity(df, companies, institutional_df, sector_analysis)
    
    # Generate stress testing analysis
    liquidity_stress = _analyze_liquidity_stress(df, companies, sector_analysis)
    
    # Build HTML content
    html = f"""
    <div class="info-section">
        <h3>5A. Enhanced Liquidity Analysis & Market Flow Intelligence</h3>
        
        <!-- Collapsible subsection 5A.1 -->
        <div style="margin: 30px 0;">
            <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: var(--card-bg); 
                       border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 15px;"
                 onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                         document.getElementById('section-5a1-content').style.display = document.getElementById('section-5a1-content').style.display === 'none' ? 'block' : 'none';">
                <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: var(--primary-gradient-start);">▼</span>
                <h4 style="margin: 0; color: var(--text-primary);">5A.1 Comprehensive Liquidity Assessment with Institutional Impact Analysis</h4>
            </div>
            
            <div id="section-5a1-content" style="display: block;">
                {_build_liquidity_analysis_content(liquidity_analysis, companies)}
            </div>
        </div>
        
        <!-- Collapsible subsection 5A.2 -->
        <div style="margin: 30px 0;">
            <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: var(--card-bg); 
                       border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 15px;"
                 onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                         document.getElementById('section-5a2-content').style.display = document.getElementById('section-5a2-content').style.display === 'none' ? 'block' : 'none';">
                <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: var(--primary-gradient-start);">▼</span>
                <h4 style="margin: 0; color: var(--text-primary);">5A.2 Liquidity Stress Testing & Scenario Resilience</h4>
            </div>
            
            <div id="section-5a2-content" style="display: block;">
                {_build_liquidity_stress_content(liquidity_stress, companies)}
            </div>
        </div>
    </div>
    """
    
    return html


def _build_liquidity_analysis_content(liquidity_analysis: Dict, companies: Dict) -> str:
    """Build liquidity analysis content with table and charts"""
    
    if not liquidity_analysis:
        return '<div class="info-box warning"><p>Insufficient data for liquidity analysis.</p></div>'
    
    # Create summary stat cards
    avg_current = np.mean([m['current_ratio'] for m in liquidity_analysis.values()])
    avg_quick = np.mean([m['quick_ratio'] for m in liquidity_analysis.values()])
    avg_liquidity_score = np.mean([m['adjusted_liquidity_score'] for m in liquidity_analysis.values()])
    excellent_count = sum(1 for m in liquidity_analysis.values() if m['liquidity_rating'] == 'Excellent')
    
    stat_cards = build_stat_grid([
        {
            "label": "Average Current Ratio",
            "value": f"{avg_current:.2f}x",
            "description": "Portfolio liquidity strength",
            "type": "success" if avg_current >= 1.5 else "warning" if avg_current >= 1.2 else "danger"
        },
        {
            "label": "Average Quick Ratio",
            "value": f"{avg_quick:.2f}x",
            "description": "Liquid assets coverage",
            "type": "success" if avg_quick >= 1.0 else "warning" if avg_quick >= 0.8 else "danger"
        },
        {
            "label": "Portfolio Liquidity Score",
            "value": f"{avg_liquidity_score:.1f}/10",
            "description": "Institutional-adjusted score",
            "type": "success" if avg_liquidity_score >= 7 else "info" if avg_liquidity_score >= 5 else "warning"
        },
        {
            "label": "Excellent Liquidity",
            "value": f"{excellent_count}/{len(liquidity_analysis)}",
            "description": "Companies with top ratings",
            "type": "success" if excellent_count >= len(liquidity_analysis) * 0.5 else "info"
        }
    ])
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in liquidity_analysis.items():
        inst_impact = metrics['institutional_liquidity_support'] - metrics['institutional_liquidity_pressure']
        table_data.append({
            'Company': company_name,
            'Current Ratio': f"{metrics['current_ratio']:.2f}",
            'Quick Ratio': f"{metrics['quick_ratio']:.2f}",
            'Cash Ratio': f"{metrics['cash_ratio']:.2f}",
            'Working Capital ($M)': f"${metrics['working_capital']/1_000_000:.0f}",
            'CCC (Days)': f"{metrics['cash_conversion_cycle']:.0f}",
            'Inst. Flow Impact': f"{inst_impact:+.2f}",
            'Liquidity Score': f"{metrics['adjusted_liquidity_score']:.1f}/10",
            'Risk Level': metrics['liquidity_risk'],
            'Rating': metrics['liquidity_rating'],
            'Trend': metrics['liquidity_trend']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Define color coding for specific columns
    def color_risk(val):
        if val == 'Low': return 'excellent'
        elif val == 'Medium': return 'good'
        else: return 'poor'
    
    def color_rating(val):
        if val == 'Excellent': return 'excellent'
        elif val == 'Good': return 'good'
        elif val == 'Fair': return 'fair'
        else: return 'poor'
    
    def color_trend(val):
        if val == 'Improving': return 'excellent'
        elif val == 'Stable': return 'good'
        else: return 'poor'
    
    table_html = build_enhanced_table(
        df_table,
        table_id="liquidity-analysis-table",
        color_columns={
            'Risk Level': color_risk,
            'Rating': color_rating,
            'Trend': color_trend
        },
        badge_columns=['Risk Level', 'Rating', 'Trend']
    )
    
    # Generate charts
    charts_html = _create_liquidity_analysis_charts(liquidity_analysis, companies)
    
    # Generate summary
    summary = _generate_liquidity_summary(liquidity_analysis, len(companies))
    summary_html = build_info_box(summary, "info", "Liquidity Analysis Summary")
    
    return f"""
    {stat_cards}
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">Comprehensive Liquidity Metrics</h5>
        {table_html}
    </div>
    {charts_html}
    {summary_html}
    """


def _build_liquidity_stress_content(liquidity_stress: Dict, companies: Dict) -> str:
    """Build liquidity stress testing content with table and charts"""
    
    if not liquidity_stress:
        return '<div class="info-box warning"><p>Insufficient data for liquidity stress testing.</p></div>'
    
    # Create summary stat cards
    avg_resilience = np.mean([m['resilience_score'] for m in liquidity_stress.values()])
    excellent_stress = sum(1 for m in liquidity_stress.values() if m['stress_rating'] == 'Excellent')
    quick_recovery = sum(1 for m in liquidity_stress.values() if m['recovery_time'] <= 6)
    avg_stress_2 = np.mean([m['stress_scenario_2'] for m in liquidity_stress.values()])
    
    stat_cards = build_stat_grid([
        {
            "label": "Portfolio Resilience Score",
            "value": f"{avg_resilience:.1f}/10",
            "description": "Comprehensive stress resilience",
            "type": "success" if avg_resilience >= 7 else "info" if avg_resilience >= 5 else "warning"
        },
        {
            "label": "Severe Stress Performance",
            "value": f"{avg_stress_2:.2f}x",
            "description": "40% asset stress scenario",
            "type": "success" if avg_stress_2 >= 1.0 else "warning" if avg_stress_2 >= 0.8 else "danger"
        },
        {
            "label": "Excellent Under Stress",
            "value": f"{excellent_stress}/{len(liquidity_stress)}",
            "description": "Companies maintaining excellence",
            "type": "success" if excellent_stress >= len(liquidity_stress) * 0.4 else "info"
        },
        {
            "label": "Quick Recovery Capability",
            "value": f"{quick_recovery}/{len(liquidity_stress)}",
            "description": "Recovery ≤6 months",
            "type": "success" if quick_recovery >= len(liquidity_stress) * 0.5 else "warning"
        }
    ])
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in liquidity_stress.items():
        table_data.append({
            'Company': company_name,
            'Current Liquidity': f"{metrics['current_liquidity']:.2f}",
            'Stress Scenario 1': f"{metrics['stress_scenario_1']:.2f}",
            'Stress Scenario 2': f"{metrics['stress_scenario_2']:.2f}",
            'Critical Threshold': f"{metrics['critical_threshold']:.2f}",
            'Liquidity Buffer': f"{metrics['liquidity_buffer']:.1f}%",
            'Recovery Time': f"{metrics['recovery_time']:.0f} mo",
            'Stress Rating': metrics['stress_rating'],
            'Resilience Score': f"{metrics['resilience_score']:.1f}/10"
        })
    
    df_table = pd.DataFrame(table_data)
    
    def color_stress_rating(val):
        if val == 'Excellent': return 'excellent'
        elif val == 'Good': return 'good'
        elif val == 'Fair': return 'fair'
        else: return 'poor'
    
    table_html = build_enhanced_table(
        df_table,
        table_id="liquidity-stress-table",
        color_columns={'Stress Rating': color_stress_rating},
        badge_columns=['Stress Rating']
    )
    
    # Generate charts
    charts_html = _create_liquidity_stress_charts(liquidity_stress, companies)
    
    # Generate summary
    summary = _generate_stress_summary(liquidity_stress, len(companies))
    summary_html = build_info_box(summary, "warning", "Stress Testing Summary")
    
    return f"""
    {stat_cards}
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">Liquidity Stress Testing Results</h5>
        {table_html}
    </div>
    {charts_html}
    {summary_html}
    """


# =============================================================================
# LIQUIDITY ANALYSIS HELPERS
# =============================================================================

def _analyze_enhanced_liquidity(
    df: pd.DataFrame,
    companies: Dict[str, str],
    institutional_df: pd.DataFrame,
    sector_analysis: Dict
) -> Dict[str, Dict]:
    """Analyze enhanced liquidity metrics with institutional impact"""
    
    liquidity_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core liquidity ratios
        metrics['current_ratio'] = latest.get('currentRatio', 0)
        metrics['quick_ratio'] = latest.get('quickRatio', 0)
        metrics['cash_ratio'] = latest.get('cashRatio', 0)
        
        # Working capital metrics
        cash = latest.get('cashAndCashEquivalents', 0)
        current_assets = latest.get('totalCurrentAssets', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        
        working_capital = current_assets - current_liabilities
        metrics['working_capital'] = working_capital
        metrics['working_capital_ratio'] = working_capital / current_assets if current_assets > 0 else 0
        
        # Cash conversion cycle
        dso = 365 / latest.get('receivablesTurnover', 1) if latest.get('receivablesTurnover', 0) > 0 else 0
        dio = 365 / latest.get('inventoryTurnover', 1) if latest.get('inventoryTurnover', 0) > 0 else 0
        dpo = 365 / latest.get('payablesTurnover', 1) if latest.get('payablesTurnover', 0) > 0 else 0
        
        metrics['cash_conversion_cycle'] = dso + dio - dpo
        
        # Initialize institutional metrics
        metrics['institutional_liquidity_support'] = 0
        metrics['institutional_liquidity_pressure'] = 0
        metrics['institutional_ownership_change'] = 0
        
        # Institutional flow impact
        if not institutional_df.empty:
            inst_data = institutional_df[institutional_df['Company'] == company_name]
            if not inst_data.empty:
                latest_inst = inst_data.iloc[-1]
                ownership_change = latest_inst.get('ownershipPercentChange', 0)
                
                metrics['institutional_ownership_change'] = ownership_change
                
                # Liquidity impact from institutional flows
                if abs(ownership_change) > 2:
                    flow_impact = min(abs(ownership_change) / 10, 0.5)
                    if ownership_change > 0:
                        metrics['institutional_liquidity_support'] = flow_impact
                    else:
                        metrics['institutional_liquidity_pressure'] = flow_impact
        
        # Liquidity quality score
        quality_components = [
            min(10, metrics['current_ratio'] * 3),
            min(10, metrics['quick_ratio'] * 5),
            min(10, metrics['cash_ratio'] * 10),
            min(10, max(0, 10 - abs(metrics['cash_conversion_cycle']) / 10))
        ]
        
        institutional_adjustment = metrics['institutional_liquidity_support'] - metrics['institutional_liquidity_pressure']
        
        metrics['base_liquidity_score'] = np.mean(quality_components)
        metrics['adjusted_liquidity_score'] = max(0, min(10, metrics['base_liquidity_score'] + institutional_adjustment))
        
        # Liquidity trend
        if len(company_data) >= 3:
            recent_current = company_data['currentRatio'].tail(3).mean()
            historical_current = company_data['currentRatio'].head(3).mean()
            
            if recent_current > historical_current * 1.1:
                metrics['liquidity_trend'] = 'Improving'
            elif recent_current < historical_current * 0.9:
                metrics['liquidity_trend'] = 'Declining'
            else:
                metrics['liquidity_trend'] = 'Stable'
        else:
            metrics['liquidity_trend'] = 'Limited Data'
        
        # Risk assessment
        if metrics['adjusted_liquidity_score'] >= 7 and metrics['current_ratio'] >= 1.5:
            metrics['liquidity_risk'] = 'Low'
        elif metrics['adjusted_liquidity_score'] >= 5 and metrics['current_ratio'] >= 1.2:
            metrics['liquidity_risk'] = 'Medium'
        else:
            metrics['liquidity_risk'] = 'High'
        
        # Rating
        if metrics['adjusted_liquidity_score'] >= 8:
            metrics['liquidity_rating'] = 'Excellent'
        elif metrics['adjusted_liquidity_score'] >= 6:
            metrics['liquidity_rating'] = 'Good'
        elif metrics['adjusted_liquidity_score'] >= 4:
            metrics['liquidity_rating'] = 'Fair'
        else:
            metrics['liquidity_rating'] = 'Poor'
        
        liquidity_analysis[company_name] = metrics
    
    return liquidity_analysis


def _analyze_liquidity_stress(
    df: pd.DataFrame,
    companies: Dict[str, str],
    sector_analysis: Dict
) -> Dict[str, Dict]:
    """Analyze liquidity under stress scenarios"""
    
    liquidity_stress = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Current liquidity baseline
        current_liquidity = latest.get('currentRatio', 0)
        cash = latest.get('cashAndCashEquivalents', 0)
        current_assets = latest.get('totalCurrentAssets', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        
        metrics['current_liquidity'] = current_liquidity
        
        # Stress Scenario 1: Mild (20% asset reduction, 10% liability increase)
        stressed_assets_1 = current_assets * 0.8
        stressed_liabilities_1 = current_liabilities * 1.1
        metrics['stress_scenario_1'] = stressed_assets_1 / stressed_liabilities_1 if stressed_liabilities_1 > 0 else 0
        
        # Stress Scenario 2: Severe (40% asset reduction, 20% liability increase)
        stressed_assets_2 = current_assets * 0.6
        stressed_liabilities_2 = current_liabilities * 1.2
        metrics['stress_scenario_2'] = stressed_assets_2 / stressed_liabilities_2 if stressed_liabilities_2 > 0 else 0
        
        # Critical threshold
        sector = sector_analysis.get('dominant_sector', 'Mixed')
        if sector in ['Utilities', 'Consumer Staples']:
            critical_threshold = 1.0
        elif sector in ['Technology', 'Healthcare']:
            critical_threshold = 1.2
        else:
            critical_threshold = 1.1
        
        metrics['critical_threshold'] = critical_threshold
        
        # Liquidity buffer
        buffer_ratio = (current_liquidity - critical_threshold) / critical_threshold if critical_threshold > 0 else 0
        metrics['liquidity_buffer'] = buffer_ratio * 100
        
        # Recovery time
        if metrics['stress_scenario_1'] < critical_threshold:
            ocf = latest.get('operatingCashFlow', 0)
            monthly_ocf = ocf / 12 if ocf > 0 else 0
            
            liquidity_deficit = (critical_threshold * stressed_liabilities_1) - stressed_assets_1
            recovery_months = liquidity_deficit / monthly_ocf if monthly_ocf > 0 else 36
            metrics['recovery_time'] = min(36, max(1, recovery_months))
        else:
            metrics['recovery_time'] = 0
        
        # Stress rating
        if metrics['stress_scenario_2'] >= critical_threshold:
            metrics['stress_rating'] = 'Excellent'
        elif metrics['stress_scenario_1'] >= critical_threshold:
            metrics['stress_rating'] = 'Good'
        elif metrics['stress_scenario_1'] >= critical_threshold * 0.9:
            metrics['stress_rating'] = 'Fair'
        else:
            metrics['stress_rating'] = 'Poor'
        
        # Resilience score
        resilience_components = [
            min(10, current_liquidity * 3),
            min(10, max(0, metrics['stress_scenario_1'] * 5)),
            min(10, max(0, metrics['stress_scenario_2'] * 7)),
            min(10, max(0, 10 - metrics['recovery_time'] / 3))
        ]
        
        metrics['resilience_score'] = np.mean(resilience_components)
        
        liquidity_stress[company_name] = metrics
    
    return liquidity_stress


def _create_liquidity_analysis_charts(liquidity_analysis: Dict, companies: Dict) -> str:
    """Create liquidity analysis charts using Plotly"""
    
    companies_list = list(liquidity_analysis.keys())
    
    # Chart 1: Core Liquidity Ratios
    fig1 = go.Figure()
    
    current_ratios = [liquidity_analysis[c]['current_ratio'] for c in companies_list]
    quick_ratios = [liquidity_analysis[c]['quick_ratio'] for c in companies_list]
    cash_ratios = [liquidity_analysis[c]['cash_ratio'] for c in companies_list]
    
    fig1.add_trace(go.Bar(name='Current Ratio', x=companies_list, y=current_ratios, marker_color='lightblue'))
    fig1.add_trace(go.Bar(name='Quick Ratio', x=companies_list, y=quick_ratios, marker_color='lightgreen'))
    fig1.add_trace(go.Bar(name='Cash Ratio', x=companies_list, y=cash_ratios, marker_color='lightcoral'))
    
    fig1.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Minimum Threshold")
    
    fig1.update_layout(
        title='Core Liquidity Ratios Comparison',
        xaxis_title='Companies',
        yaxis_title='Ratio',
        barmode='group',
        hovermode='x unified',
        height=400
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'liquidity-ratios-chart')
    
    # Chart 2: Base vs Adjusted Scores
    fig2 = go.Figure()
    
    base_scores = [liquidity_analysis[c]['base_liquidity_score'] for c in companies_list]
    adjusted_scores = [liquidity_analysis[c]['adjusted_liquidity_score'] for c in companies_list]
    
    fig2.add_trace(go.Bar(name='Base Score', x=companies_list, y=base_scores, marker_color='lightsteelblue'))
    fig2.add_trace(go.Bar(name='Adjusted Score', x=companies_list, y=adjusted_scores, marker_color='gold'))
    
    fig2.update_layout(
        title='Liquidity Scores: Base vs Institutional-Adjusted',
        xaxis_title='Companies',
        yaxis_title='Score (0-10)',
        barmode='group',
        hovermode='x unified',
        height=400
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'liquidity-scores-chart')
    
    # Chart 3: Cash Conversion Cycle
    fig3 = go.Figure()
    
    ccc_values = [liquidity_analysis[c]['cash_conversion_cycle'] for c in companies_list]
    colors = ['green' if ccc < 30 else 'orange' if ccc < 60 else 'red' for ccc in ccc_values]
    
    fig3.add_trace(go.Bar(x=companies_list, y=ccc_values, marker_color=colors))
    
    fig3.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Excellent (<30 days)")
    fig3.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="Good (<60 days)")
    
    fig3.update_layout(
        title='Cash Conversion Cycle Efficiency',
        xaxis_title='Companies',
        yaxis_title='Days',
        hovermode='x unified',
        height=400
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'ccc-chart')
    
    # Chart 4: Working Capital vs Liquidity Quality
    fig4 = go.Figure()
    
    working_capital = [liquidity_analysis[c]['working_capital']/1_000_000 for c in companies_list]
    liquidity_scores = [liquidity_analysis[c]['adjusted_liquidity_score'] for c in companies_list]
    
    fig4.add_trace(go.Scatter(
        x=working_capital,
        y=liquidity_scores,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=liquidity_scores, colorscale='Viridis', showscale=True),
        hovertemplate='<b>%{text}</b><br>Working Capital: $%{x:.0f}M<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    fig4.update_layout(
        title='Working Capital vs Liquidity Quality Matrix',
        xaxis_title='Working Capital ($M)',
        yaxis_title='Liquidity Score (0-10)',
        height=400
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'wc-quality-chart')
    
    return f"""
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 20px;">Liquidity Analysis Visualizations</h5>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
    </div>
    """


def _create_liquidity_stress_charts(liquidity_stress: Dict, companies: Dict) -> str:
    """Create liquidity stress testing charts using Plotly"""
    
    companies_list = list(liquidity_stress.keys())
    
    # Chart 1: Stress Scenario Performance
    fig1 = go.Figure()
    
    current = [liquidity_stress[c]['current_liquidity'] for c in companies_list]
    stress1 = [liquidity_stress[c]['stress_scenario_1'] for c in companies_list]
    stress2 = [liquidity_stress[c]['stress_scenario_2'] for c in companies_list]
    
    fig1.add_trace(go.Bar(name='Current', x=companies_list, y=current, marker_color='lightblue'))
    fig1.add_trace(go.Bar(name='Mild Stress', x=companies_list, y=stress1, marker_color='orange'))
    fig1.add_trace(go.Bar(name='Severe Stress', x=companies_list, y=stress2, marker_color='red'))
    
    fig1.add_hline(y=1.0, line_dash="dash", line_color="darkred", annotation_text="Critical Threshold")
    
    fig1.update_layout(
        title='Liquidity Under Stress Scenarios',
        xaxis_title='Companies',
        yaxis_title='Current Ratio',
        barmode='group',
        hovermode='x unified',
        height=400
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'stress-scenarios-chart')
    
    # Chart 2: Resilience Scores
    fig2 = go.Figure()
    
    resilience = [liquidity_stress[c]['resilience_score'] for c in companies_list]
    
    fig2.add_trace(go.Bar(x=companies_list, y=resilience, marker_color='steelblue', text=resilience,
                          texttemplate='%{text:.1f}', textposition='outside'))
    
    fig2.update_layout(
        title='Stress Resilience Assessment',
        xaxis_title='Companies',
        yaxis_title='Resilience Score (0-10)',
        hovermode='x unified',
        height=400
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'resilience-chart')
    
    # Chart 3: Recovery Time Analysis
    fig3 = go.Figure()
    
    recovery = [liquidity_stress[c]['recovery_time'] for c in companies_list]
    colors = ['green' if rt <= 6 else 'orange' if rt <= 12 else 'red' for rt in recovery]
    
    fig3.add_trace(go.Bar(x=companies_list, y=recovery, marker_color=colors))
    
    fig3.update_layout(
        title='Liquidity Recovery Time Estimation',
        xaxis_title='Companies',
        yaxis_title='Months',
        hovermode='x unified',
        height=400
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'recovery-chart')
    
    # Chart 4: Stress Rating Distribution
    fig4 = go.Figure()
    
    ratings = {}
    for metrics in liquidity_stress.values():
        rating = metrics['stress_rating']
        ratings[rating] = ratings.get(rating, 0) + 1
    
    colors_map = {'Excellent': 'darkgreen', 'Good': 'green', 'Fair': 'orange', 'Poor': 'red'}
    pie_colors = [colors_map.get(r, 'gray') for r in ratings.keys()]
    
    fig4.add_trace(go.Pie(labels=list(ratings.keys()), values=list(ratings.values()),
                          marker=dict(colors=pie_colors)))
    
    fig4.update_layout(
        title='Stress Rating Distribution',
        height=400
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'stress-distribution-chart')
    
    return f"""
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 20px;">Stress Testing Visualizations</h5>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
    </div>
    """


def _generate_liquidity_summary(liquidity_analysis: Dict, total_companies: int) -> str:
    """Generate liquidity analysis summary"""
    
    avg_current = np.mean([m['current_ratio'] for m in liquidity_analysis.values()])
    avg_quick = np.mean([m['quick_ratio'] for m in liquidity_analysis.values()])
    avg_score = np.mean([m['adjusted_liquidity_score'] for m in liquidity_analysis.values()])
    
    low_risk = sum(1 for m in liquidity_analysis.values() if m['liquidity_risk'] == 'Low')
    excellent = sum(1 for m in liquidity_analysis.values() if m['liquidity_rating'] == 'Excellent')
    improving = sum(1 for m in liquidity_analysis.values() if m['liquidity_trend'] == 'Improving')
    
    net_inst_support = np.mean([
        m['institutional_liquidity_support'] - m['institutional_liquidity_pressure']
        for m in liquidity_analysis.values()
    ])
    
    return f"""
    <strong>Enhanced Liquidity Analysis with Institutional Intelligence Summary:</strong>
    <ul>
        <li><strong>Portfolio Liquidity Profile:</strong> {avg_current:.2f}x average current ratio, {avg_quick:.2f}x quick ratio with {avg_score:.1f}/10 adjusted liquidity score</li>
        <li><strong>Risk Distribution:</strong> {low_risk}/{total_companies} companies classified as low liquidity risk</li>
        <li><strong>Excellence Achievement:</strong> {excellent}/{total_companies} companies with excellent liquidity ratings</li>
        <li><strong>Momentum Assessment:</strong> {improving}/{total_companies} companies showing improving liquidity trends</li>
    </ul>
    
    <strong>Institutional Flow Intelligence Integration:</strong>
    <ul>
        <li><strong>Net Institutional Impact:</strong> {net_inst_support:+.2f} average flow impact on liquidity assessment</li>
        <li><strong>Flow Dynamics:</strong> {'Supportive' if net_inst_support > 0.1 else 'Neutral' if abs(net_inst_support) <= 0.1 else 'Pressure'} institutional flow environment for portfolio liquidity</li>
        <li><strong>Market Confidence:</strong> {'High' if avg_score >= 7 and net_inst_support > 0 else 'Moderate' if avg_score >= 5 else 'Cautious'} institutional confidence in liquidity stability</li>
    </ul>
    """


def _generate_stress_summary(liquidity_stress: Dict, total_companies: int) -> str:
    """Generate stress testing summary"""
    
    avg_stress1 = np.mean([m['stress_scenario_1'] for m in liquidity_stress.values()])
    avg_stress2 = np.mean([m['stress_scenario_2'] for m in liquidity_stress.values()])
    avg_resilience = np.mean([m['resilience_score'] for m in liquidity_stress.values()])
    
    excellent = sum(1 for m in liquidity_stress.values() if m['stress_rating'] == 'Excellent')
    quick_recovery = sum(1 for m in liquidity_stress.values() if m['recovery_time'] <= 6)
    
    return f"""
    <strong>Liquidity Stress Testing & Scenario Resilience Assessment:</strong>
    <ul>
        <li><strong>Mild Stress Resilience:</strong> {avg_stress1:.2f}x average current ratio under 20% asset stress scenario</li>
        <li><strong>Severe Stress Performance:</strong> {avg_stress2:.2f}x average current ratio under 40% asset stress scenario</li>
        <li><strong>Portfolio Resilience Score:</strong> {avg_resilience:.1f}/10 comprehensive stress resilience rating</li>
        <li><strong>Stress Excellence:</strong> {excellent}/{total_companies} companies maintaining excellent ratings under severe stress</li>
    </ul>
    
    <strong>Recovery & Adaptation Capability:</strong>
    <ul>
        <li><strong>Rapid Recovery Capability:</strong> {quick_recovery}/{total_companies} companies with recovery times ≤6 months</li>
        <li><strong>Stress Preparedness:</strong> {'Well-positioned' if excellent >= total_companies * 0.5 and avg_stress2 >= 1.0 else 'Adequately prepared' if avg_stress1 >= 1.0 else 'Stress vulnerability requires attention'} for economic downturns</li>
    </ul>
    """


# =============================================================================
# PHASE 2: SECTION 5B - ADVANCED SOLVENCY ASSESSMENT
# =============================================================================

def _build_section_5b_solvency_analysis(
    df: pd.DataFrame,
    companies: Dict[str, str],
    economic_df: pd.DataFrame,
    sector_analysis: Dict
) -> str:
    """Build Section 5B: Advanced Solvency Assessment & Debt Sustainability Analysis"""
    
    # Generate solvency analysis
    solvency_analysis = _analyze_advanced_solvency(df, companies, economic_df, sector_analysis)
    
    if not solvency_analysis:
        return '<div class="info-box warning"><p>Insufficient data for solvency analysis.</p></div>'
    
    # Build HTML content
    html = f"""
    <div class="info-section">
        <h3>5B. Advanced Solvency Assessment & Debt Sustainability Analysis</h3>
        
        <!-- Collapsible subsection 5B -->
        <div style="margin: 30px 0;">
            <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: var(--card-bg); 
                       border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 15px;"
                 onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                         document.getElementById('section-5b-content').style.display = document.getElementById('section-5b-content').style.display === 'none' ? 'block' : 'none';">
                <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: var(--primary-gradient-start);">▼</span>
                <h4 style="margin: 0; color: var(--text-primary);">Comprehensive Solvency Evaluation with Forward-Looking Debt Capacity</h4>
            </div>
            
            <div id="section-5b-content" style="display: block;">
                {_build_solvency_analysis_content(solvency_analysis, companies)}
            </div>
        </div>
    </div>
    """
    
    return html


def _build_solvency_analysis_content(solvency_analysis: Dict, companies: Dict) -> str:
    """Build solvency analysis content with table and charts"""
    
    # Create summary stat cards
    avg_interest_coverage = np.mean([m['interest_coverage'] for m in solvency_analysis.values()])
    avg_sustainability = np.mean([m['sustainability_score'] for m in solvency_analysis.values()])
    investment_grade = sum(1 for m in solvency_analysis.values() 
                          if m['estimated_credit_rating'] in ['A or higher', 'BBB'])
    low_risk = sum(1 for m in solvency_analysis.values() if m['risk_level'] == 'Low')
    
    stat_cards = build_stat_grid([
        {
            "label": "Average Interest Coverage",
            "value": f"{avg_interest_coverage:.1f}x",
            "description": "Portfolio debt service capability",
            "type": "success" if avg_interest_coverage >= 5 else "warning" if avg_interest_coverage >= 3 else "danger"
        },
        {
            "label": "Portfolio Sustainability Score",
            "value": f"{avg_sustainability:.1f}/10",
            "description": "Comprehensive debt sustainability",
            "type": "success" if avg_sustainability >= 7 else "info" if avg_sustainability >= 5 else "warning"
        },
        {
            "label": "Investment Grade Companies",
            "value": f"{investment_grade}/{len(solvency_analysis)}",
            "description": "BBB rating or higher",
            "type": "success" if investment_grade >= len(solvency_analysis) * 0.5 else "info"
        },
        {
            "label": "Low Solvency Risk",
            "value": f"{low_risk}/{len(solvency_analysis)}",
            "description": "Strong debt management",
            "type": "success" if low_risk >= len(solvency_analysis) * 0.5 else "warning"
        }
    ])
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in solvency_analysis.items():
        table_data.append({
            'Company': company_name,
            'Debt/Equity': f"{metrics['debt_to_equity']:.2f}x",
            'Interest Coverage': f"{metrics['interest_coverage']:.1f}x",
            'Debt Service Coverage': f"{metrics['debt_service_coverage']:.2f}x",
            'EBITDA/Interest': f"{metrics['ebitda_interest_coverage']:.1f}x",
            'Net Debt/EBITDA': f"{metrics['net_debt_to_ebitda']:.1f}x",
            'Debt Capacity': f"{metrics['debt_capacity']:.1f}%",
            'Sustainability Score': f"{metrics['sustainability_score']:.1f}/10",
            'Credit Rating Est.': metrics['estimated_credit_rating'],
            'Risk Level': metrics['risk_level'],
            'Outlook': metrics['solvency_outlook']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Define color coding
    def color_risk(val):
        if val == 'Low': return 'excellent'
        elif val == 'Medium': return 'good'
        elif val == 'High': return 'fair'
        else: return 'poor'
    
    def color_outlook(val):
        if val == 'Improving': return 'excellent'
        elif val == 'Stable': return 'good'
        elif val == 'Deteriorating': return 'poor'
        else: return 'fair'
    
    def color_rating(val):
        if 'A' in val: return 'excellent'
        elif 'BBB' in val: return 'good'
        elif 'BB' in val: return 'fair'
        else: return 'poor'
    
    table_html = build_enhanced_table(
        df_table,
        table_id="solvency-analysis-table",
        color_columns={
            'Risk Level': color_risk,
            'Outlook': color_outlook,
            'Credit Rating Est.': color_rating
        },
        badge_columns=['Risk Level', 'Outlook', 'Credit Rating Est.']
    )
    
    # Generate charts
    charts_html = _create_solvency_analysis_charts(solvency_analysis, companies)
    
    # Generate summary
    summary = _generate_solvency_summary(solvency_analysis, len(companies))
    summary_html = build_info_box(summary, "info", "Solvency Analysis Summary")
    
    return f"""
    {stat_cards}
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">Comprehensive Solvency Metrics</h5>
        {table_html}
    </div>
    {charts_html}
    {summary_html}
    """


# =============================================================================
# SOLVENCY ANALYSIS HELPERS
# =============================================================================

def _analyze_advanced_solvency(
    df: pd.DataFrame,
    companies: Dict[str, str],
    economic_df: pd.DataFrame,
    sector_analysis: Dict
) -> Dict[str, Dict]:
    """Analyze advanced solvency and debt sustainability metrics"""
    
    solvency_analysis = {}
    
    # Risk-free rate for calculations
    risk_free_rate = 4.0
    if not economic_df.empty and 'Treasury_10Y' in economic_df.columns:
        treasury_data = economic_df['Treasury_10Y'].dropna()
        if len(treasury_data) > 0:
            risk_free_rate = treasury_data.iloc[-1]
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core solvency ratios
        metrics['debt_to_equity'] = latest.get('debtToEquityRatio', 0)
        metrics['interest_coverage'] = latest.get('interestCoverageRatio', 0)
        
        # Advanced coverage ratios
        ebitda = latest.get('ebitda', 0)
        interest_expense = latest.get('interestExpense', 1)
        metrics['ebitda_interest_coverage'] = ebitda / interest_expense if interest_expense > 0 else 0
        
        # Debt service coverage
        ocf = latest.get('operatingCashFlow', 0)
        total_debt_service = interest_expense + abs(latest.get('netDebtIssuance', 0))
        metrics['debt_service_coverage'] = ocf / total_debt_service if total_debt_service > 0 else 0
        
        # Net debt to EBITDA
        total_debt = latest.get('totalDebt', 0)
        cash = latest.get('cashAndCashEquivalents', 0)
        net_debt = max(0, total_debt - cash)
        metrics['net_debt_to_ebitda'] = net_debt / ebitda if ebitda > 0 else 0
        
        # Debt capacity analysis
        total_assets = latest.get('totalAssets', 0)
        debt_to_assets = total_debt / total_assets if total_assets > 0 else 0
        
        # Industry-specific optimal debt levels
        sector = sector_analysis.get('dominant_sector', 'Mixed')
        if sector in ['Utilities', 'Real Estate']:
            optimal_debt_ratio = 0.6
        elif sector in ['Technology', 'Healthcare']:
            optimal_debt_ratio = 0.3
        elif sector == 'Financials':
            optimal_debt_ratio = 0.8
        else:
            optimal_debt_ratio = 0.4
        
        debt_capacity_used = debt_to_assets / optimal_debt_ratio if optimal_debt_ratio > 0 else 0
        metrics['debt_capacity'] = min(100, debt_capacity_used * 100)
        
        # Sustainability score
        sustainability_components = [
            min(10, metrics['interest_coverage'] / 2),
            min(10, max(0, 10 - metrics['net_debt_to_ebitda'])),
            min(10, max(0, metrics['debt_service_coverage'] * 3)),
            min(10, max(0, 10 - debt_capacity_used * 5))
        ]
        
        metrics['sustainability_score'] = np.mean(sustainability_components)
        
        # Estimated credit rating
        if (metrics['interest_coverage'] >= 8 and metrics['net_debt_to_ebitda'] <= 1.5 and 
            metrics['debt_service_coverage'] >= 2.0):
            metrics['estimated_credit_rating'] = 'A or higher'
        elif (metrics['interest_coverage'] >= 4 and metrics['net_debt_to_ebitda'] <= 3.0 and 
              metrics['debt_service_coverage'] >= 1.5):
            metrics['estimated_credit_rating'] = 'BBB'
        elif (metrics['interest_coverage'] >= 2 and metrics['net_debt_to_ebitda'] <= 5.0 and 
              metrics['debt_service_coverage'] >= 1.2):
            metrics['estimated_credit_rating'] = 'BB'
        elif metrics['interest_coverage'] >= 1.5 and metrics['debt_service_coverage'] >= 1.0:
            metrics['estimated_credit_rating'] = 'B'
        else:
            metrics['estimated_credit_rating'] = 'CCC or lower'
        
        # Risk level assessment
        if metrics['sustainability_score'] >= 8 and metrics['interest_coverage'] >= 5:
            metrics['risk_level'] = 'Low'
        elif metrics['sustainability_score'] >= 6 and metrics['interest_coverage'] >= 3:
            metrics['risk_level'] = 'Medium'
        elif metrics['sustainability_score'] >= 4 and metrics['interest_coverage'] >= 2:
            metrics['risk_level'] = 'High'
        else:
            metrics['risk_level'] = 'Very High'
        
        # Solvency outlook
        if len(company_data) >= 3:
            recent_coverage = company_data['interestCoverageRatio'].tail(3).mean()
            historical_coverage = company_data['interestCoverageRatio'].head(3).mean()
            
            if recent_coverage > historical_coverage * 1.2:
                metrics['solvency_outlook'] = 'Improving'
            elif recent_coverage < historical_coverage * 0.8:
                metrics['solvency_outlook'] = 'Deteriorating'
            else:
                metrics['solvency_outlook'] = 'Stable'
        else:
            metrics['solvency_outlook'] = 'Unknown'
        
        solvency_analysis[company_name] = metrics
    
    return solvency_analysis


def _create_solvency_analysis_charts(solvency_analysis: Dict, companies: Dict) -> str:
    """Create solvency analysis charts using Plotly"""
    
    companies_list = list(solvency_analysis.keys())
    
    # Chart 1: Coverage Ratios
    fig1 = go.Figure()
    
    interest_coverage = [solvency_analysis[c]['interest_coverage'] for c in companies_list]
    debt_service_coverage = [solvency_analysis[c]['debt_service_coverage'] for c in companies_list]
    ebitda_coverage = [solvency_analysis[c]['ebitda_interest_coverage'] for c in companies_list]
    
    fig1.add_trace(go.Bar(name='Interest Coverage', x=companies_list, y=interest_coverage, marker_color='lightblue'))
    fig1.add_trace(go.Bar(name='Debt Service Coverage', x=companies_list, y=debt_service_coverage, marker_color='lightgreen'))
    fig1.add_trace(go.Bar(name='EBITDA Coverage', x=companies_list, y=ebitda_coverage, marker_color='lightcoral'))
    
    fig1.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="Minimum Threshold")
    
    fig1.update_layout(
        title='Debt Coverage Ratios Analysis',
        xaxis_title='Companies',
        yaxis_title='Coverage Ratio (x)',
        barmode='group',
        hovermode='x unified',
        height=400
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'coverage-ratios-chart')
    
    # Chart 2: Net Debt/EBITDA vs Sustainability Score
    fig2 = go.Figure()
    
    net_debt_ebitda = [solvency_analysis[c]['net_debt_to_ebitda'] for c in companies_list]
    sustainability_scores = [solvency_analysis[c]['sustainability_score'] for c in companies_list]
    
    fig2.add_trace(go.Scatter(
        x=net_debt_ebitda,
        y=sustainability_scores,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=sustainability_scores, colorscale='RdYlGn', showscale=True),
        hovertemplate='<b>%{text}</b><br>Net Debt/EBITDA: %{x:.1f}x<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    fig2.add_vline(x=3.0, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
    
    fig2.update_layout(
        title='Debt Sustainability Matrix',
        xaxis_title='Net Debt/EBITDA (x)',
        yaxis_title='Sustainability Score (0-10)',
        height=400
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'sustainability-matrix-chart')
    
    # Chart 3: Credit Rating Distribution
    fig3 = go.Figure()
    
    ratings = {}
    for metrics in solvency_analysis.values():
        rating = metrics['estimated_credit_rating']
        ratings[rating] = ratings.get(rating, 0) + 1
    
    # Sort ratings by quality
    rating_order = ['A or higher', 'BBB', 'BB', 'B', 'CCC or lower']
    sorted_ratings = {r: ratings.get(r, 0) for r in rating_order if r in ratings}
    
    colors_map = {
        'A or higher': 'darkgreen',
        'BBB': 'green',
        'BB': 'orange',
        'B': 'darkorange',
        'CCC or lower': 'red'
    }
    bar_colors = [colors_map.get(r, 'gray') for r in sorted_ratings.keys()]
    
    fig3.add_trace(go.Bar(
        x=list(sorted_ratings.keys()),
        y=list(sorted_ratings.values()),
        marker_color=bar_colors,
        text=list(sorted_ratings.values()),
        textposition='outside'
    ))
    
    fig3.update_layout(
        title='Estimated Credit Rating Distribution',
        xaxis_title='Credit Rating',
        yaxis_title='Number of Companies',
        hovermode='x unified',
        height=400
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'credit-rating-chart')
    
    # Chart 4: Debt Capacity vs Sustainability Risk Matrix
    fig4 = go.Figure()
    
    debt_capacity = [solvency_analysis[c]['debt_capacity'] for c in companies_list]
    risk_levels = [solvency_analysis[c]['risk_level'] for c in companies_list]
    
    # Map risk levels to colors
    risk_color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red', 'Very High': 'darkred'}
    scatter_colors = [risk_color_map.get(risk, 'gray') for risk in risk_levels]
    
    fig4.add_trace(go.Scatter(
        x=debt_capacity,
        y=sustainability_scores,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=scatter_colors),
        hovertemplate='<b>%{text}</b><br>Debt Capacity: %{x:.1f}%<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    fig4.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="High Utilization")
    
    fig4.update_layout(
        title='Debt Capacity vs Sustainability Risk Matrix',
        xaxis_title='Debt Capacity Utilization (%)',
        yaxis_title='Sustainability Score (0-10)',
        height=400
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'debt-capacity-chart')
    
    return f"""
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 20px;">Solvency Analysis Visualizations</h5>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
    </div>
    """


def _generate_solvency_summary(solvency_analysis: Dict, total_companies: int) -> str:
    """Generate solvency analysis summary"""
    
    avg_interest_coverage = np.mean([m['interest_coverage'] for m in solvency_analysis.values()])
    avg_debt_service = np.mean([m['debt_service_coverage'] for m in solvency_analysis.values()])
    avg_sustainability = np.mean([m['sustainability_score'] for m in solvency_analysis.values()])
    
    low_risk = sum(1 for m in solvency_analysis.values() if m['risk_level'] == 'Low')
    investment_grade = sum(1 for m in solvency_analysis.values() 
                          if m['estimated_credit_rating'] in ['A or higher', 'BBB'])
    improving = sum(1 for m in solvency_analysis.values() if m['solvency_outlook'] == 'Improving')
    
    return f"""
    <strong>Advanced Solvency Assessment & Debt Sustainability Analysis:</strong>
    <ul>
        <li><strong>Portfolio Solvency Profile:</strong> {avg_interest_coverage:.1f}x average interest coverage, {avg_debt_service:.1f}x debt service coverage</li>
        <li><strong>Sustainability Score:</strong> {avg_sustainability:.1f}/10 comprehensive debt sustainability rating</li>
        <li><strong>Risk Distribution:</strong> {low_risk}/{total_companies} companies classified as low solvency risk</li>
        <li><strong>Credit Quality:</strong> {investment_grade}/{total_companies} companies estimated at investment grade ratings</li>
    </ul>
    
    <strong>Debt Sustainability Framework:</strong>
    <ul>
        <li><strong>Coverage Adequacy:</strong> {'Strong' if avg_interest_coverage >= 5 and avg_debt_service >= 2 else 'Adequate' if avg_interest_coverage >= 3 and avg_debt_service >= 1.5 else 'Concerning'} debt service coverage capabilities</li>
        <li><strong>Forward-Looking Sustainability:</strong> {'Excellent' if avg_sustainability >= 8 else 'Good' if avg_sustainability >= 6 else 'Requires Enhancement'} long-term debt sustainability profile</li>
        <li><strong>Outlook Momentum:</strong> {improving}/{total_companies} companies with improving solvency outlook trajectories</li>
    </ul>
    
    <strong>Strategic Solvency Management:</strong>
    <ul>
        <li><strong>Capital Structure Health:</strong> {'Optimal' if low_risk >= total_companies * 0.6 and investment_grade >= total_companies * 0.5 else 'Adequate' if low_risk >= total_companies * 0.4 else 'Requires Optimization'} debt management framework</li>
        <li><strong>Risk Management Priorities:</strong> {'Maintain excellence while optimizing capital efficiency' if avg_sustainability >= 7 and investment_grade >= total_companies * 0.5 else 'Enhance debt sustainability and coverage ratios' if avg_sustainability >= 5 else 'Comprehensive solvency improvement strategy required'} based on current assessment</li>
    </ul>
    """


# =============================================================================
# PHASE 3: SECTION 5C - CAPITAL STRUCTURE OPTIMIZATION & COST OF CAPITAL
# =============================================================================

def _build_section_5c_capital_structure(
    df: pd.DataFrame,
    companies: Dict[str, str],
    economic_df: pd.DataFrame,
    sector_analysis: Dict,
    institutional_df: pd.DataFrame
) -> str:
    """Build Section 5C: Capital Structure Optimization & Cost of Capital Analysis"""
    
    # Generate capital structure analysis
    capital_structure = _analyze_capital_structure_optimization(
        df, companies, economic_df, sector_analysis, institutional_df
    )
    
    if not capital_structure:
        return '<div class="info-box warning"><p>Insufficient data for capital structure analysis.</p></div>'
    
    # Build HTML content
    html = f"""
    <div class="info-section">
        <h3>5C. Capital Structure Optimization & Cost of Capital Analysis</h3>
        
        <!-- Collapsible subsection 5C -->
        <div style="margin: 30px 0;">
            <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: var(--card-bg); 
                       border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 15px;"
                 onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                         document.getElementById('section-5c-content').style.display = document.getElementById('section-5c-content').style.display === 'none' ? 'block' : 'none';">
                <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: var(--primary-gradient-start);">▼</span>
                <h4 style="margin: 0; color: var(--text-primary);">Advanced Capital Structure Evaluation with WACC Optimization</h4>
            </div>
            
            <div id="section-5c-content" style="display: block;">
                {_build_capital_structure_content(capital_structure, companies)}
            </div>
        </div>
    </div>
    """
    
    return html


def _build_capital_structure_content(capital_structure: Dict, companies: Dict) -> str:
    """Build capital structure analysis content with table and charts"""
    
    # Create summary stat cards
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()])
    avg_structure_score = np.mean([m['structure_score'] for m in capital_structure.values()])
    optimal_leverage = sum(1 for m in capital_structure.values() if abs(m['leverage_gap']) <= 5)
    high_efficiency = sum(1 for m in capital_structure.values() if m['capital_efficiency'] >= 7)
    
    stat_cards = build_stat_grid([
        {
            "label": "Average WACC",
            "value": f"{avg_wacc:.2f}%",
            "description": "Weighted average cost of capital",
            "type": "success" if avg_wacc <= 8 else "info" if avg_wacc <= 10 else "warning"
        },
        {
            "label": "Portfolio Structure Score",
            "value": f"{avg_structure_score:.1f}/10",
            "description": "Capital structure efficiency",
            "type": "success" if avg_structure_score >= 7 else "info" if avg_structure_score >= 5 else "warning"
        },
        {
            "label": "Optimal Leverage",
            "value": f"{optimal_leverage}/{len(capital_structure)}",
            "description": "Within ±5pp of target",
            "type": "success" if optimal_leverage >= len(capital_structure) * 0.6 else "info"
        },
        {
            "label": "High Capital Efficiency",
            "value": f"{high_efficiency}/{len(capital_structure)}",
            "description": "Efficiency score ≥7",
            "type": "success" if high_efficiency >= len(capital_structure) * 0.5 else "warning"
        }
    ])
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in capital_structure.items():
        table_data.append({
            'Company': company_name,
            'Debt/Capital': f"{metrics['debt_to_capital']:.1f}%",
            'Equity/Capital': f"{metrics['equity_to_capital']:.1f}%",
            'Cost of Debt': f"{metrics['cost_of_debt']:.2f}%",
            'Cost of Equity': f"{metrics['cost_of_equity']:.2f}%",
            'WACC': f"{metrics['wacc']:.2f}%",
            'Optimal Leverage': f"{metrics['optimal_leverage']:.1f}%",
            'Leverage Gap': f"{metrics['leverage_gap']:+.1f}pp",
            'Capital Efficiency': f"{metrics['capital_efficiency']:.1f}/10",
            'Structure Score': f"{metrics['structure_score']:.1f}/10",
            'Optimization': metrics['optimization_direction'],
            'Priority': metrics['optimization_priority']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Define color coding
    def color_priority(val):
        if val == 'Low': return 'excellent'
        elif val == 'Medium': return 'good'
        else: return 'poor'
    
    def color_optimization(val):
        if val == 'Maintain': return 'excellent'
        elif val == 'Reduce Leverage': return 'fair'
        else: return 'good'
    
    table_html = build_enhanced_table(
        df_table,
        table_id="capital-structure-table",
        color_columns={
            'Priority': color_priority,
            'Optimization': color_optimization
        },
        badge_columns=['Priority', 'Optimization']
    )
    
    # Generate charts
    charts_html = _create_capital_structure_charts(capital_structure, companies)
    
    # Generate summary
    summary = _generate_capital_structure_summary(capital_structure, len(companies))
    summary_html = build_info_box(summary, "info", "Capital Structure Analysis Summary")
    
    return f"""
    {stat_cards}
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">Comprehensive Capital Structure Metrics</h5>
        {table_html}
    </div>
    {charts_html}
    {summary_html}
    """


# =============================================================================
# CAPITAL STRUCTURE ANALYSIS HELPERS
# =============================================================================

def _analyze_capital_structure_optimization(
    df: pd.DataFrame,
    companies: Dict[str, str],
    economic_df: pd.DataFrame,
    sector_analysis: Dict,
    institutional_df: pd.DataFrame
) -> Dict[str, Dict]:
    """Analyze capital structure optimization and cost of capital"""
    
    capital_structure = {}
    
    # Market rates for calculations
    risk_free_rate = 4.0
    market_risk_premium = 6.0
    
    if not economic_df.empty and 'Treasury_10Y' in economic_df.columns:
        treasury_data = economic_df['Treasury_10Y'].dropna()
        if len(treasury_data) > 0:
            risk_free_rate = treasury_data.iloc[-1]
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Capital structure components
        total_debt = latest.get('totalDebt', 0)
        total_equity = latest.get('totalStockholdersEquity', 0)
        total_capital = total_debt + total_equity
        
        if total_capital > 0:
            metrics['debt_to_capital'] = (total_debt / total_capital) * 100
            metrics['equity_to_capital'] = (total_equity / total_capital) * 100
        else:
            metrics['debt_to_capital'] = 0
            metrics['equity_to_capital'] = 100
        
        # Cost of debt calculation
        interest_expense = latest.get('interestExpense', 0)
        if total_debt > 0 and interest_expense > 0:
            metrics['cost_of_debt'] = (interest_expense / total_debt) * 100
        else:
            metrics['cost_of_debt'] = risk_free_rate + 2  # Estimate
        
        # Cost of equity calculation (CAPM approximation)
        beta = 1.2  # Default assumption
        
        # Adjust beta based on sector
        sector = sector_analysis.get('dominant_sector', 'Mixed')
        if sector == 'Utilities':
            beta = 0.8
        elif sector == 'Technology':
            beta = 1.4
        elif sector == 'Healthcare':
            beta = 1.1
        elif sector == 'Financials':
            beta = 1.3
        
        # Adjust for institutional ownership
        if not institutional_df.empty:
            inst_data = institutional_df[institutional_df['Company'] == company_name]
            if not inst_data.empty:
                latest_inst = inst_data.iloc[-1]
                ownership_pct = latest_inst.get('ownershipPercent', 0)
                # Higher institutional ownership typically reduces beta
                beta_adjustment = -0.1 * (ownership_pct / 100) if ownership_pct > 0 else 0
                beta = max(0.5, beta + beta_adjustment)
        
        metrics['cost_of_equity'] = risk_free_rate + beta * market_risk_premium
        
        # WACC calculation
        tax_rate = 0.25  # Assumption
        if total_capital > 0:
            weight_debt = total_debt / total_capital
            weight_equity = total_equity / total_capital
            
            wacc = (weight_equity * metrics['cost_of_equity'] + 
                   weight_debt * metrics['cost_of_debt'] * (1 - tax_rate))
            metrics['wacc'] = wacc
        else:
            metrics['wacc'] = metrics['cost_of_equity']
        
        # Optimal leverage estimation
        sector = sector_analysis.get('dominant_sector', 'Mixed')
        if sector in ['Utilities', 'Real Estate']:
            optimal_debt_ratio = 60
        elif sector in ['Technology', 'Healthcare']:
            optimal_debt_ratio = 20
        elif sector == 'Financials':
            optimal_debt_ratio = 80
        else:
            optimal_debt_ratio = 40
        
        metrics['optimal_leverage'] = optimal_debt_ratio
        metrics['leverage_gap'] = metrics['debt_to_capital'] - optimal_debt_ratio
        
        # Capital efficiency score
        roe = latest.get('returnOnEquity', 0)
        roic = latest.get('returnOnInvestedCapital', 0)
        
        efficiency_components = [
            min(10, max(0, 10 - abs(metrics['leverage_gap']) / 5)),
            min(10, max(0, (roic - metrics['wacc']) / 2)),
            min(10, max(0, roe / 2)),
            min(10, max(0, 15 - metrics['wacc']))
        ]
        
        metrics['capital_efficiency'] = np.mean([comp for comp in efficiency_components if comp >= 0])
        
        # Overall structure score
        structure_components = [
            metrics['capital_efficiency'],
            min(10, max(0, 10 - abs(metrics['leverage_gap']) / 3)),
            min(10, max(0, (20 - metrics['wacc']) / 2))
        ]
        
        metrics['structure_score'] = np.mean(structure_components)
        
        # Optimization direction
        if abs(metrics['leverage_gap']) <= 5:
            metrics['optimization_direction'] = 'Maintain'
        elif metrics['leverage_gap'] > 5:
            metrics['optimization_direction'] = 'Reduce Leverage'
        else:
            metrics['optimization_direction'] = 'Increase Leverage'
        
        # Optimization priority
        if metrics['structure_score'] >= 8:
            metrics['optimization_priority'] = 'Low'
        elif metrics['structure_score'] >= 6:
            metrics['optimization_priority'] = 'Medium'
        else:
            metrics['optimization_priority'] = 'High'
        
        capital_structure[company_name] = metrics
    
    return capital_structure


def _create_capital_structure_charts(capital_structure: Dict, companies: Dict) -> str:
    """Create capital structure optimization charts using Plotly"""
    
    companies_list = list(capital_structure.keys())
    
    # Chart 1: Debt vs Equity Composition (Stacked Bar)
    fig1 = go.Figure()
    
    debt_to_capital = [capital_structure[c]['debt_to_capital'] for c in companies_list]
    equity_to_capital = [capital_structure[c]['equity_to_capital'] for c in companies_list]
    
    fig1.add_trace(go.Bar(
        name='Debt %',
        x=companies_list,
        y=debt_to_capital,
        marker_color='lightcoral'
    ))
    
    fig1.add_trace(go.Bar(
        name='Equity %',
        x=companies_list,
        y=equity_to_capital,
        marker_color='lightblue'
    ))
    
    fig1.update_layout(
        title='Capital Structure Composition',
        xaxis_title='Companies',
        yaxis_title='Capital Structure (%)',
        barmode='stack',
        hovermode='x unified',
        height=400
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'capital-composition-chart')
    
    # Chart 2: Cost of Capital Components
    fig2 = go.Figure()
    
    cost_of_debt = [capital_structure[c]['cost_of_debt'] for c in companies_list]
    cost_of_equity = [capital_structure[c]['cost_of_equity'] for c in companies_list]
    wacc = [capital_structure[c]['wacc'] for c in companies_list]
    
    fig2.add_trace(go.Bar(name='Cost of Debt', x=companies_list, y=cost_of_debt, marker_color='lightgreen'))
    fig2.add_trace(go.Bar(name='Cost of Equity', x=companies_list, y=cost_of_equity, marker_color='orange'))
    fig2.add_trace(go.Bar(name='WACC', x=companies_list, y=wacc, marker_color='purple'))
    
    fig2.update_layout(
        title='Cost of Capital Analysis',
        xaxis_title='Companies',
        yaxis_title='Cost (%)',
        barmode='group',
        hovermode='x unified',
        height=400
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'cost-capital-chart')
    
    # Chart 3: Leverage Gap Analysis
    fig3 = go.Figure()
    
    leverage_gaps = [capital_structure[c]['leverage_gap'] for c in companies_list]
    
    # Color bars based on gap direction
    colors = ['red' if gap > 5 else 'green' if gap < -5 else 'yellow' for gap in leverage_gaps]
    
    fig3.add_trace(go.Bar(
        x=companies_list,
        y=leverage_gaps,
        marker_color=colors,
        text=[f"{gap:+.1f}pp" for gap in leverage_gaps],
        textposition='outside'
    ))
    
    fig3.add_hline(y=0, line_color="black", line_width=2)
    fig3.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Over-leveraged")
    fig3.add_hline(y=-5, line_dash="dash", line_color="green", annotation_text="Under-leveraged")
    
    fig3.update_layout(
        title='Leverage Optimization Gap Analysis',
        xaxis_title='Companies',
        yaxis_title='Leverage Gap (pp)',
        hovermode='x unified',
        height=400
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'leverage-gap-chart')
    
    # Chart 4: Capital Efficiency vs Structure Score
    fig4 = go.Figure()
    
    capital_efficiency = [capital_structure[c]['capital_efficiency'] for c in companies_list]
    structure_scores = [capital_structure[c]['structure_score'] for c in companies_list]
    
    fig4.add_trace(go.Scatter(
        x=capital_efficiency,
        y=structure_scores,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=structure_scores, colorscale='Viridis', showscale=True),
        hovertemplate='<b>%{text}</b><br>Efficiency: %{x:.1f}<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    # Add benchmark lines
    fig4.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Excellence Threshold")
    fig4.add_vline(x=7, line_dash="dash", line_color="green")
    
    fig4.update_layout(
        title='Capital Efficiency vs Structure Quality Matrix',
        xaxis_title='Capital Efficiency (0-10)',
        yaxis_title='Structure Score (0-10)',
        height=400
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'efficiency-structure-chart')
    
    return f"""
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 20px;">Capital Structure Visualizations</h5>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
    </div>
    """


def _generate_capital_structure_summary(capital_structure: Dict, total_companies: int) -> str:
    """Generate capital structure optimization summary"""
    
    avg_debt_to_capital = np.mean([m['debt_to_capital'] for m in capital_structure.values()])
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()])
    avg_structure_score = np.mean([m['structure_score'] for m in capital_structure.values()])
    
    optimal_leverage = sum(1 for m in capital_structure.values() if abs(m['leverage_gap']) <= 5)
    high_efficiency = sum(1 for m in capital_structure.values() if m['capital_efficiency'] >= 7)
    low_priority = sum(1 for m in capital_structure.values() if m['optimization_priority'] == 'Low')
    
    avg_capital_efficiency = np.mean([m['capital_efficiency'] for m in capital_structure.values()])
    avg_debt_capacity = np.mean([m.get('debt_capacity', 50) for m in capital_structure.values()])
    avg_cost_of_debt = np.mean([m['cost_of_debt'] for m in capital_structure.values()])
    maintain_count = sum(1 for m in capital_structure.values() if m['optimization_direction'] == 'Maintain')
    
    return f"""
    <strong>Capital Structure Optimization & Cost of Capital Framework:</strong>
    <ul>
        <li><strong>WACC Optimization Profile:</strong> {avg_wacc:.2f}% portfolio-weighted average cost of capital with {avg_structure_score:.1f}/10 structure optimization score</li>
        <li><strong>Leverage Optimization:</strong> {optimal_leverage}/{total_companies} companies within optimal leverage ranges (±5pp) indicating {'excellent' if optimal_leverage >= total_companies * 0.6 else 'good' if optimal_leverage >= total_companies * 0.4 else 'suboptimal'} capital structure positioning</li>
        <li><strong>Cost of Capital Competitiveness:</strong> {'Industry-leading' if avg_wacc <= 7 else 'Competitive' if avg_wacc <= 9 else 'Standard' if avg_wacc <= 11 else 'Elevated requiring optimization'} positioning for value creation</li>
        <li><strong>Capital Efficiency:</strong> {'High efficiency' if avg_capital_efficiency >= 7 else 'Moderate efficiency' if avg_capital_efficiency >= 5 else 'Efficiency enhancement opportunities'} in capital deployment and utilization</li>
    </ul>
    
    <strong>Advanced Capital Structure Analysis:</strong>
    <ul>
        <li><strong>Debt Capacity Utilization:</strong> {'Conservative positioning' if avg_debt_to_capital <= 40 else 'Moderate utilization' if avg_debt_to_capital <= 60 else 'High utilization requiring monitoring'} providing flexibility for growth investments</li>
        <li><strong>Optimization Direction Clarity:</strong> {maintain_count}/{total_companies} companies at optimal structure requiring maintenance vs optimization</li>
        <li><strong>Cost Component Management:</strong> {'Balanced cost optimization' if avg_wacc <= 9 and avg_cost_of_debt <= 6 else 'Debt cost focus needed' if avg_cost_of_debt > 6 else 'Comprehensive cost reduction required'} across debt and equity components</li>
    </ul>
    
    <strong>Strategic Capital Allocation Framework:</strong>
    <ul>
        <li><strong>Portfolio Optimization:</strong> {'Leverage existing optimal structures for growth acceleration' if optimal_leverage >= total_companies * 0.5 and avg_wacc <= 9 else 'Implement systematic capital structure optimization initiatives' if avg_structure_score >= 5 else 'Comprehensive capital structure transformation and WACC reduction program required'} for enhanced value creation</li>
        <li><strong>Efficiency Excellence:</strong> {high_efficiency}/{total_companies} companies achieving high capital efficiency ratings (≥7 score) demonstrating {'industry-leading' if high_efficiency >= total_companies * 0.6 else 'competitive' if high_efficiency >= total_companies * 0.4 else 'developing'} capital allocation capabilities</li>
        <li><strong>Priority Management:</strong> {low_priority}/{total_companies} companies with low optimization priority indicating {'strong' if low_priority >= total_companies * 0.5 else 'adequate' if low_priority >= total_companies * 0.3 else 'significant'} need for capital structure attention</li>
    </ul>
    """


# =============================================================================
# PHASE 4: SECTION 5D - BALANCE SHEET QUALITY ASSESSMENT
# =============================================================================

def _build_section_5d_balance_sheet_quality(
    df: pd.DataFrame,
    companies: Dict[str, str],
    sector_analysis: Dict
) -> str:
    """Build Section 5D: Balance Sheet Quality Assessment & Hidden Risk Analysis"""
    
    # Generate balance sheet quality analysis
    balance_sheet_quality = _analyze_balance_sheet_quality(df, companies, sector_analysis)
    
    if not balance_sheet_quality:
        return '<div class="info-box warning"><p>Insufficient data for balance sheet quality analysis.</p></div>'
    
    # Build HTML content
    html = f"""
    <div class="info-section">
        <h3>5D. Balance Sheet Quality Assessment & Hidden Risk Analysis</h3>
        
        <!-- Collapsible subsection 5D -->
        <div style="margin: 30px 0;">
            <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: var(--card-bg); 
                       border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 15px;"
                 onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                         document.getElementById('section-5d-content').style.display = document.getElementById('section-5d-content').style.display === 'none' ? 'block' : 'none';">
                <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: var(--primary-gradient-start);">▼</span>
                <h4 style="margin: 0; color: var(--text-primary);">Comprehensive Balance Sheet Quality with Off-Balance Sheet Risk Evaluation</h4>
            </div>
            
            <div id="section-5d-content" style="display: block;">
                {_build_balance_sheet_quality_content(balance_sheet_quality, companies)}
            </div>
        </div>
    </div>
    """
    
    return html


def _build_balance_sheet_quality_content(balance_sheet_quality: Dict, companies: Dict) -> str:
    """Build balance sheet quality content with table and charts"""
    
    # Create summary stat cards
    avg_quality = np.mean([m['overall_quality_score'] for m in balance_sheet_quality.values()])
    avg_tangible = np.mean([m['tangible_asset_ratio'] for m in balance_sheet_quality.values()])
    low_risk = sum(1 for m in balance_sheet_quality.values() if m['risk_rating'] == 'Low Risk')
    low_contingent = sum(1 for m in balance_sheet_quality.values() if m['contingent_risk_level'] == 'Low')
    
    stat_cards = build_stat_grid([
        {
            "label": "Average Quality Score",
            "value": f"{avg_quality:.1f}/10",
            "description": "Comprehensive balance sheet quality",
            "type": "success" if avg_quality >= 7 else "info" if avg_quality >= 5 else "warning"
        },
        {
            "label": "Average Tangible Asset Ratio",
            "value": f"{avg_tangible:.1f}%",
            "description": "Asset base quality",
            "type": "success" if avg_tangible >= 70 else "info" if avg_tangible >= 60 else "warning"
        },
        {
            "label": "Low Risk Companies",
            "value": f"{low_risk}/{len(balance_sheet_quality)}",
            "description": "Strong balance sheet health",
            "type": "success" if low_risk >= len(balance_sheet_quality) * 0.5 else "warning"
        },
        {
            "label": "Low Contingent Risk",
            "value": f"{low_contingent}/{len(balance_sheet_quality)}",
            "description": "Hidden risk management",
            "type": "success" if low_contingent >= len(balance_sheet_quality) * 0.6 else "warning"
        }
    ])
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in balance_sheet_quality.items():
        table_data.append({
            'Company': company_name,
            'Asset Quality': f"{metrics['asset_quality_score']:.1f}/10",
            'Liability Structure': f"{metrics['liability_structure_score']:.1f}/10",
            'Working Capital': f"{metrics['working_capital_score']:.1f}/10",
            'Tangible Assets': f"{metrics['tangible_asset_ratio']:.1f}%",
            'Cash Quality': f"{metrics['cash_quality_score']:.1f}/10",
            'Contingent Risk': metrics['contingent_risk_level'],
            'Quality Score': f"{metrics['overall_quality_score']:.1f}/10",
            'Risk Rating': metrics['risk_rating'],
            'Stability Trend': metrics['stability_trend']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Define color coding
    def color_risk_rating(val):
        if 'Low' in val: return 'excellent'
        elif 'Medium' in val: return 'good'
        elif 'High' in val and 'Very' not in val: return 'fair'
        else: return 'poor'
    
    def color_contingent(val):
        if val == 'Low': return 'excellent'
        elif val == 'Medium': return 'fair'
        else: return 'poor'
    
    def color_trend(val):
        if val == 'Improving': return 'excellent'
        elif val == 'Stable': return 'good'
        elif val == 'Deteriorating': return 'poor'
        else: return 'fair'
    
    table_html = build_enhanced_table(
        df_table,
        table_id="balance-sheet-quality-table",
        color_columns={
            'Risk Rating': color_risk_rating,
            'Contingent Risk': color_contingent,
            'Stability Trend': color_trend
        },
        badge_columns=['Risk Rating', 'Contingent Risk', 'Stability Trend']
    )
    
    # Generate charts
    charts_html = _create_balance_sheet_quality_charts(balance_sheet_quality, companies)
    
    # Generate summary
    summary = _generate_balance_sheet_quality_summary(balance_sheet_quality, len(companies))
    summary_html = build_info_box(summary, "info", "Balance Sheet Quality Summary")
    
    return f"""
    {stat_cards}
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">Balance Sheet Quality Metrics</h5>
        {table_html}
    </div>
    {charts_html}
    {summary_html}
    """


# =============================================================================
# BALANCE SHEET QUALITY HELPERS
# =============================================================================

def _analyze_balance_sheet_quality(
    df: pd.DataFrame,
    companies: Dict[str, str],
    sector_analysis: Dict
) -> Dict[str, Dict]:
    """Analyze balance sheet quality and hidden risks"""
    
    balance_sheet_quality = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Asset quality assessment
        total_assets = latest.get('totalAssets', 0)
        goodwill = latest.get('goodwill', 0)
        intangible_assets = latest.get('intangibleAssets', 0)
        ppe_net = latest.get('propertyPlantEquipmentNet', 0)
        cash = latest.get('cashAndCashEquivalents', 0)
        
        # Tangible asset ratio
        tangible_assets = total_assets - goodwill - intangible_assets
        metrics['tangible_asset_ratio'] = (tangible_assets / total_assets * 100) if total_assets > 0 else 0
        
        # Asset quality score
        asset_quality_components = [
            min(10, metrics['tangible_asset_ratio'] / 10),
            min(10, (cash / total_assets) * 20) if total_assets > 0 else 0,
            min(10, (ppe_net / total_assets) * 15) if total_assets > 0 and ppe_net > 0 else 5,
            min(10, max(0, 10 - (goodwill / total_assets) * 20)) if total_assets > 0 else 10
        ]
        
        metrics['asset_quality_score'] = np.mean(asset_quality_components)
        
        # Liability structure assessment
        total_liabilities = latest.get('totalLiabilities', 0)
        current_liabilities = latest.get('totalCurrentLiabilities', 0)
        long_term_debt = latest.get('longTermDebt', 0)
        deferred_revenue = latest.get('deferredRevenue', 0)
        
        liability_structure_components = [
            min(10, (current_liabilities / total_liabilities) * 15) if total_liabilities > 0 else 5,
            min(10, max(0, 10 - (long_term_debt / total_liabilities) * 10)) if total_liabilities > 0 else 8,
            min(10, (deferred_revenue / total_liabilities) * 20) if total_liabilities > 0 and deferred_revenue > 0 else 5,
            min(10, max(0, 10 - (total_liabilities / total_assets) * 15)) if total_assets > 0 else 5
        ]
        
        metrics['liability_structure_score'] = np.mean(liability_structure_components)
        
        # Working capital quality
        current_assets = latest.get('totalCurrentAssets', 0)
        working_capital = current_assets - current_liabilities
        revenue = latest.get('revenue', 1)
        
        wc_to_revenue = working_capital / revenue if revenue > 0 else 0
        metrics['working_capital_score'] = min(10, max(0, 5 + wc_to_revenue * 10))
        
        # Cash quality assessment
        short_term_investments = latest.get('shortTermInvestments', 0)
        total_investments = latest.get('totalInvestments', 0)
        
        cash_quality_components = [
            min(10, (cash / total_assets) * 30) if total_assets > 0 else 0,
            min(10, ((cash + short_term_investments) / current_liabilities) * 3) if current_liabilities > 0 else 5,
            min(10, max(0, 10 - (total_investments / total_assets) * 20)) if total_assets > 0 else 8
        ]
        
        metrics['cash_quality_score'] = np.mean(cash_quality_components)
        
        # Contingent risk assessment
        off_balance_sheet_risk = 0
        
        if total_assets > 0:
            if (goodwill / total_assets) > 0.3:
                off_balance_sheet_risk += 1
            
            if latest.get('capitalLeaseObligations', 0) > total_assets * 0.1:
                off_balance_sheet_risk += 1
            
            if latest.get('otherNonCurrentLiabilities', 0) > total_liabilities * 0.1:
                off_balance_sheet_risk += 1
            
            if revenue > 0 and latest.get('deferredRevenue', 0) > revenue * 0.2:
                off_balance_sheet_risk += 1
        
        if off_balance_sheet_risk == 0:
            metrics['contingent_risk_level'] = 'Low'
        elif off_balance_sheet_risk <= 2:
            metrics['contingent_risk_level'] = 'Medium'
        else:
            metrics['contingent_risk_level'] = 'High'
        
        # Overall quality score
        quality_components = [
            metrics['asset_quality_score'],
            metrics['liability_structure_score'],
            metrics['working_capital_score'],
            metrics['cash_quality_score']
        ]
        
        risk_adjustment = {'Low': 0, 'Medium': -1, 'High': -2}[metrics['contingent_risk_level']]
        
        metrics['overall_quality_score'] = max(0, np.mean(quality_components) + risk_adjustment)
        
        # Risk rating
        if metrics['overall_quality_score'] >= 8:
            metrics['risk_rating'] = 'Low Risk'
        elif metrics['overall_quality_score'] >= 6:
            metrics['risk_rating'] = 'Medium Risk'
        elif metrics['overall_quality_score'] >= 4:
            metrics['risk_rating'] = 'High Risk'
        else:
            metrics['risk_rating'] = 'Very High Risk'
        
        # Stability trend
        if len(company_data) >= 3:
            recent_leverage = (company_data['totalLiabilities'] / company_data['totalAssets']).tail(3).mean()
            historical_leverage = (company_data['totalLiabilities'] / company_data['totalAssets']).head(3).mean()
            
            if recent_leverage < historical_leverage * 0.95:
                metrics['stability_trend'] = 'Improving'
            elif recent_leverage > historical_leverage * 1.05:
                metrics['stability_trend'] = 'Deteriorating'
            else:
                metrics['stability_trend'] = 'Stable'
        else:
            metrics['stability_trend'] = 'Limited Data'
        
        balance_sheet_quality[company_name] = metrics
    
    return balance_sheet_quality


def _create_balance_sheet_quality_charts(balance_sheet_quality: Dict, companies: Dict) -> str:
    """Create balance sheet quality charts using Plotly"""
    
    companies_list = list(balance_sheet_quality.keys())
    
    # Chart 1: Quality Component Scores (Stacked Bar)
    fig1 = go.Figure()
    
    asset_quality = [balance_sheet_quality[c]['asset_quality_score'] for c in companies_list]
    liability_structure = [balance_sheet_quality[c]['liability_structure_score'] for c in companies_list]
    working_capital = [balance_sheet_quality[c]['working_capital_score'] for c in companies_list]
    cash_quality = [balance_sheet_quality[c]['cash_quality_score'] for c in companies_list]
    
    fig1.add_trace(go.Bar(name='Asset Quality', x=companies_list, y=asset_quality, marker_color='lightblue'))
    fig1.add_trace(go.Bar(name='Liability Structure', x=companies_list, y=liability_structure, marker_color='lightgreen'))
    fig1.add_trace(go.Bar(name='Working Capital', x=companies_list, y=working_capital, marker_color='orange'))
    fig1.add_trace(go.Bar(name='Cash Quality', x=companies_list, y=cash_quality, marker_color='lightcoral'))
    
    fig1.update_layout(
        title='Balance Sheet Quality Components',
        xaxis_title='Companies',
        yaxis_title='Component Scores (0-10)',
        barmode='stack',
        hovermode='x unified',
        height=400
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'quality-components-chart')
    
    # Chart 2: Tangible Asset Ratio vs Overall Quality
    fig2 = go.Figure()
    
    tangible_ratios = [balance_sheet_quality[c]['tangible_asset_ratio'] for c in companies_list]
    overall_quality = [balance_sheet_quality[c]['overall_quality_score'] for c in companies_list]
    
    fig2.add_trace(go.Scatter(
        x=tangible_ratios,
        y=overall_quality,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=overall_quality, colorscale='RdYlGn', showscale=True),
        hovertemplate='<b>%{text}</b><br>Tangible: %{x:.1f}%<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    fig2.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="High Quality")
    fig2.add_vline(x=70, line_dash="dash", line_color="green", annotation_text="High Tangibility")
    
    fig2.update_layout(
        title='Asset Tangibility vs Quality Matrix',
        xaxis_title='Tangible Asset Ratio (%)',
        yaxis_title='Overall Quality Score (0-10)',
        height=400
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'tangibility-quality-chart')
    
    # Chart 3: Risk Rating Distribution
    fig3 = go.Figure()
    
    risk_ratings = {}
    for metrics in balance_sheet_quality.values():
        rating = metrics['risk_rating']
        risk_ratings[rating] = risk_ratings.get(rating, 0) + 1
    
    risk_colors = {
        'Low Risk': 'green',
        'Medium Risk': 'orange',
        'High Risk': 'red',
        'Very High Risk': 'darkred'
    }
    pie_colors = [risk_colors.get(r, 'gray') for r in risk_ratings.keys()]
    
    fig3.add_trace(go.Pie(
        labels=list(risk_ratings.keys()),
        values=list(risk_ratings.values()),
        marker=dict(colors=pie_colors)
    ))
    
    fig3.update_layout(
        title='Balance Sheet Risk Rating Distribution',
        height=400
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'risk-distribution-chart')
    
    # Chart 4: Contingent Risk vs Quality Assessment
    fig4 = go.Figure()
    
    contingent_risk_map = {'Low': 1, 'Medium': 2, 'High': 3}
    contingent_risk_numeric = [contingent_risk_map.get(balance_sheet_quality[c]['contingent_risk_level'], 2) 
                              for c in companies_list]
    
    risk_colors_scatter = ['green' if risk == 1 else 'orange' if risk == 2 else 'red' 
                          for risk in contingent_risk_numeric]
    
    fig4.add_trace(go.Scatter(
        x=contingent_risk_numeric,
        y=overall_quality,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=risk_colors_scatter),
        hovertemplate='<b>%{text}</b><br>Contingent Risk: %{x}<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    fig4.update_layout(
        title='Hidden Risk vs Quality Assessment',
        xaxis=dict(
            title='Contingent Risk Level',
            tickmode='array',
            tickvals=[1, 2, 3],
            ticktext=['Low', 'Medium', 'High']
        ),
        yaxis_title='Overall Quality Score (0-10)',
        height=400
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'contingent-risk-chart')
    
    return f"""
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 20px;">Balance Sheet Quality Visualizations</h5>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
    </div>
    """


def _generate_balance_sheet_quality_summary(balance_sheet_quality: Dict, total_companies: int) -> str:
    """Generate balance sheet quality summary"""
    
    avg_quality = np.mean([m['overall_quality_score'] for m in balance_sheet_quality.values()])
    avg_asset_quality = np.mean([m['asset_quality_score'] for m in balance_sheet_quality.values()])
    avg_tangible = np.mean([m['tangible_asset_ratio'] for m in balance_sheet_quality.values()])
    
    low_risk = sum(1 for m in balance_sheet_quality.values() if m['risk_rating'] == 'Low Risk')
    low_contingent = sum(1 for m in balance_sheet_quality.values() if m['contingent_risk_level'] == 'Low')
    improving = sum(1 for m in balance_sheet_quality.values() if m['stability_trend'] == 'Improving')
    
    avg_liability = np.mean([m['liability_structure_score'] for m in balance_sheet_quality.values()])
    avg_wc = np.mean([m['working_capital_score'] for m in balance_sheet_quality.values()])
    avg_cash = np.mean([m['cash_quality_score'] for m in balance_sheet_quality.values()])
    
    return f"""
    <strong>Balance Sheet Quality Assessment & Hidden Risk Analysis:</strong>
    <ul>
        <li><strong>Portfolio Quality Profile:</strong> {avg_quality:.1f}/10 comprehensive balance sheet quality score</li>
        <li><strong>Asset Quality Excellence:</strong> {avg_asset_quality:.1f}/10 asset quality with {avg_tangible:.1f}% average tangible asset ratio</li>
        <li><strong>Risk Distribution:</strong> {low_risk}/{total_companies} companies classified as low balance sheet risk</li>
        <li><strong>Hidden Risk Management:</strong> {low_contingent}/{total_companies} companies with low contingent risk exposure</li>
    </ul>
    
    <strong>Balance Sheet Strength Indicators:</strong>
    <ul>
        <li><strong>Asset Base Quality:</strong> {'Excellent' if avg_asset_quality >= 8 and avg_tangible >= 70 else 'Good' if avg_asset_quality >= 6 and avg_tangible >= 60 else 'Requires Enhancement'} tangible asset foundation</li>
        <li><strong>Liability Structure Optimization:</strong> {'Well-structured' if avg_liability >= 7 else 'Standard' if avg_liability >= 5 else 'Improvement Needed'} liability management</li>
        <li><strong>Working Capital Quality:</strong> {'Optimized' if avg_wc >= 7 else 'Standard' if avg_wc >= 5 else 'Enhancement Needed'} working capital efficiency</li>
        <li><strong>Cash Position Quality:</strong> {'High-quality' if avg_cash >= 7 else 'Adequate' if avg_cash >= 5 else 'Improvement Needed'} cash management</li>
        <li><strong>Stability Momentum:</strong> {improving}/{total_companies} companies showing improving balance sheet stability trends</li>
    </ul>
    
    <strong>Strategic Quality Management:</strong>
    <ul>
        <li><strong>Hidden Risk Mitigation:</strong> {'Comprehensive' if low_contingent >= total_companies * 0.7 else 'Adequate' if low_contingent >= total_companies * 0.5 else 'Requires Attention'} off-balance sheet risk management</li>
        <li><strong>Quality Enhancement Priorities:</strong> {'Maintain excellence while optimizing efficiency' if avg_quality >= 7 and low_risk >= total_companies * 0.6 else 'Implement quality improvement initiatives' if avg_quality >= 5 else 'Comprehensive balance sheet quality enhancement required'} based on current assessment</li>
    </ul>
    """


# =============================================================================
# PHASE 4: SECTION 5E - CASH FLOW ADEQUACY ANALYSIS
# =============================================================================

def _build_section_5e_cash_flow_adequacy(
    df: pd.DataFrame,
    companies: Dict[str, str],
    sector_analysis: Dict
) -> str:
    """Build Section 5E: Cash Flow Adequacy Analysis & Financial Flexibility Assessment"""
    
    # Generate cash flow adequacy analysis
    cash_flow_adequacy = _analyze_cash_flow_adequacy(df, companies, sector_analysis)
    
    if not cash_flow_adequacy:
        return '<div class="info-box warning"><p>Insufficient data for cash flow adequacy analysis.</p></div>'
    
    # Build HTML content
    html = f"""
    <div class="info-section">
        <h3>5E. Cash Flow Adequacy Analysis & Financial Flexibility Assessment</h3>
        
        <!-- Collapsible subsection 5E -->
        <div style="margin: 30px 0;">
            <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: var(--card-bg); 
                       border-radius: 12px; border: 1px solid var(--card-border); margin-bottom: 15px;"
                 onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                         document.getElementById('section-5e-content').style.display = document.getElementById('section-5e-content').style.display === 'none' ? 'block' : 'none';">
                <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: var(--primary-gradient-start);">▼</span>
                <h4 style="margin: 0; color: var(--text-primary);">Comprehensive Cash Flow Coverage with Financial Flexibility Evaluation</h4>
            </div>
            
            <div id="section-5e-content" style="display: block;">
                {_build_cash_flow_adequacy_content(cash_flow_adequacy, companies)}
            </div>
        </div>
    </div>
    """
    
    return html


def _build_cash_flow_adequacy_content(cash_flow_adequacy: Dict, companies: Dict) -> str:
    """Build cash flow adequacy content with table and charts"""
    
    # Create summary stat cards
    avg_adequacy = np.mean([m['adequacy_score'] for m in cash_flow_adequacy.values()])
    avg_flexibility = np.mean([m['financial_flexibility_score'] for m in cash_flow_adequacy.values()])
    high_flexibility = sum(1 for m in cash_flow_adequacy.values() if m['flexibility_rating'] == 'High Flexibility')
    strong_coverage = sum(1 for m in cash_flow_adequacy.values() if m['overall_coverage_ratio'] >= 2.0)
    
    stat_cards = build_stat_grid([
        {
            "label": "Average Adequacy Score",
            "value": f"{avg_adequacy:.1f}/10",
            "description": "Comprehensive cash flow adequacy",
            "type": "success" if avg_adequacy >= 7 else "info" if avg_adequacy >= 5 else "warning"
        },
        {
            "label": "Average Flexibility Score",
            "value": f"{avg_flexibility:.1f}/10",
            "description": "Financial flexibility rating",
            "type": "success" if avg_flexibility >= 7 else "info" if avg_flexibility >= 5 else "warning"
        },
        {
            "label": "High Flexibility Companies",
            "value": f"{high_flexibility}/{len(cash_flow_adequacy)}",
            "description": "Strong operational adaptability",
            "type": "success" if high_flexibility >= len(cash_flow_adequacy) * 0.5 else "warning"
        },
        {
            "label": "Strong Coverage",
            "value": f"{strong_coverage}/{len(cash_flow_adequacy)}",
            "description": "Coverage ratio ≥2.0x",
            "type": "success" if strong_coverage >= len(cash_flow_adequacy) * 0.5 else "warning"
        }
    ])
    
    # Create DataFrame for table
    table_data = []
    for company_name, metrics in cash_flow_adequacy.items():
        table_data.append({
            'Company': company_name,
            'OCF/Debt Service': f"{metrics['ocf_debt_service_coverage']:.2f}x",
            'FCF/Capital Needs': f"{metrics['fcf_capital_coverage']:.2f}x",
            'Cash Conversion': f"{metrics['cash_conversion_efficiency']:.1f}%",
            'Coverage Ratio': f"{metrics['overall_coverage_ratio']:.2f}x",
            'Financial Flexibility': f"{metrics['financial_flexibility_score']:.1f}/10",
            'Cash Generation': f"{metrics['cash_generation_quality']:.1f}/10",
            'Sustainability': f"{metrics['sustainability_score']:.1f}/10",
            'Adequacy Score': f"{metrics['adequacy_score']:.1f}/10",
            'Flexibility Rating': metrics['flexibility_rating'],
            'Outlook': metrics['cash_flow_outlook']
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Define color coding
    def color_flexibility(val):
        if 'High' in val: return 'excellent'
        elif 'Moderate' in val: return 'good'
        elif 'Limited' in val: return 'fair'
        else: return 'poor'
    
    def color_outlook(val):
        if val == 'Strengthening': return 'excellent'
        elif val == 'Stable': return 'good'
        elif val == 'Weakening': return 'poor'
        else: return 'fair'
    
    table_html = build_enhanced_table(
        df_table,
        table_id="cash-flow-adequacy-table",
        color_columns={
            'Flexibility Rating': color_flexibility,
            'Outlook': color_outlook
        },
        badge_columns=['Flexibility Rating', 'Outlook']
    )
    
    # Generate charts
    charts_html = _create_cash_flow_adequacy_charts(cash_flow_adequacy, companies)
    
    # Generate summary
    summary = _generate_cash_flow_adequacy_summary(cash_flow_adequacy, len(companies))
    summary_html = build_info_box(summary, "info", "Cash Flow Adequacy Summary")
    
    return f"""
    {stat_cards}
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">Cash Flow Adequacy Metrics</h5>
        {table_html}
    </div>
    {charts_html}
    {summary_html}
    """


# =============================================================================
# CASH FLOW ADEQUACY HELPERS
# =============================================================================

def _analyze_cash_flow_adequacy(
    df: pd.DataFrame,
    companies: Dict[str, str],
    sector_analysis: Dict
) -> Dict[str, Dict]:
    """Analyze cash flow adequacy and financial flexibility"""
    
    cash_flow_adequacy = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core cash flow metrics
        ocf = latest.get('operatingCashFlow', 0)
        fcf = latest.get('freeCashFlow', 0)
        capex = abs(latest.get('capitalExpenditure', 0))
        interest_expense = latest.get('interestExpense', 0)
        dividends_paid = abs(latest.get('netDividendsPaid', 0))
        
        # Debt service requirements
        principal_payments = abs(latest.get('netDebtIssuance', 0))
        debt_service = interest_expense + principal_payments
        
        # OCF to debt service coverage
        metrics['ocf_debt_service_coverage'] = ocf / debt_service if debt_service > 0 else 0
        
        # FCF to capital needs coverage
        total_capital_needs = capex + dividends_paid + principal_payments
        metrics['fcf_capital_coverage'] = fcf / total_capital_needs if total_capital_needs > 0 else 0
        
        # Cash conversion efficiency
        net_income = latest.get('netIncome', 0)
        metrics['cash_conversion_efficiency'] = (ocf / net_income * 100) if net_income > 0 else 0
        
        # Overall coverage ratio
        total_cash_needs = debt_service + capex + dividends_paid
        metrics['overall_coverage_ratio'] = ocf / total_cash_needs if total_cash_needs > 0 else 0
        
        # Financial flexibility score
        cash = latest.get('cashAndCashEquivalents', 0)
        total_assets = latest.get('totalAssets', 0)
        revenue = latest.get('revenue', 1)
        
        flexibility_components = [
            min(10, metrics['ocf_debt_service_coverage'] * 2),
            min(10, (cash / revenue) * 20) if revenue > 0 else 0,
            min(10, max(0, fcf / revenue * 20)) if revenue > 0 else 0,
            min(10, max(0, 10 - abs(capex / ocf - 0.3) * 10)) if ocf > 0 else 5
        ]
        
        metrics['financial_flexibility_score'] = np.mean([comp for comp in flexibility_components if comp >= 0])
        
        # Cash generation quality
        ebitda = latest.get('ebitda', 0)
        
        generation_quality_components = [
            min(10, metrics['cash_conversion_efficiency'] / 10),
            min(10, (ocf / ebitda) * 10) if ebitda > 0 else 0,
            min(10, max(0, (fcf / ocf) * 10)) if ocf > 0 else 0,
            min(10, max(0, 10 - (capex / revenue) * 25)) if revenue > 0 else 5
        ]
        
        metrics['cash_generation_quality'] = np.mean([comp for comp in generation_quality_components if comp >= 0])
        
        # Sustainability score
        base_sustainability = np.mean([
            metrics['financial_flexibility_score'],
            metrics['cash_generation_quality']
        ])
        
        metrics['sustainability_score'] = max(0, min(10, base_sustainability))
        
        # Overall adequacy score
        adequacy_components = [
            metrics['financial_flexibility_score'],
            metrics['cash_generation_quality'],
            metrics['sustainability_score'],
            min(10, metrics['overall_coverage_ratio'] * 3)
        ]
        
        metrics['adequacy_score'] = np.mean(adequacy_components)
        
        # Flexibility rating
        if metrics['financial_flexibility_score'] >= 8:
            metrics['flexibility_rating'] = 'High Flexibility'
        elif metrics['financial_flexibility_score'] >= 6:
            metrics['flexibility_rating'] = 'Moderate Flexibility'
        elif metrics['financial_flexibility_score'] >= 4:
            metrics['flexibility_rating'] = 'Limited Flexibility'
        else:
            metrics['flexibility_rating'] = 'Constrained'
        
        # Cash flow outlook
        if len(company_data) >= 3:
            recent_ocf = company_data['operatingCashFlow'].tail(3).mean()
            historical_ocf = company_data['operatingCashFlow'].head(3).mean()
            
            if recent_ocf > historical_ocf * 1.2:
                metrics['cash_flow_outlook'] = 'Strengthening'
            elif recent_ocf < historical_ocf * 0.8:
                metrics['cash_flow_outlook'] = 'Weakening'
            else:
                metrics['cash_flow_outlook'] = 'Stable'
        else:
            metrics['cash_flow_outlook'] = 'Limited Data'
        
        cash_flow_adequacy[company_name] = metrics
    
    return cash_flow_adequacy


def _create_cash_flow_adequacy_charts(cash_flow_adequacy: Dict, companies: Dict) -> str:
    """Create cash flow adequacy charts using Plotly"""
    
    companies_list = list(cash_flow_adequacy.keys())
    
    # Chart 1: Coverage Ratios
    fig1 = go.Figure()
    
    ocf_coverage = [cash_flow_adequacy[c]['ocf_debt_service_coverage'] for c in companies_list]
    fcf_coverage = [cash_flow_adequacy[c]['fcf_capital_coverage'] for c in companies_list]
    overall_coverage = [cash_flow_adequacy[c]['overall_coverage_ratio'] for c in companies_list]
    
    fig1.add_trace(go.Bar(name='OCF/Debt Service', x=companies_list, y=ocf_coverage, marker_color='lightblue'))
    fig1.add_trace(go.Bar(name='FCF/Capital Needs', x=companies_list, y=fcf_coverage, marker_color='lightgreen'))
    fig1.add_trace(go.Bar(name='Overall Coverage', x=companies_list, y=overall_coverage, marker_color='lightcoral'))
    
    fig1.add_hline(y=1.5, line_dash="dash", line_color="red", annotation_text="Adequate Threshold")
    
    fig1.update_layout(
        title='Cash Flow Coverage Analysis',
        xaxis_title='Companies',
        yaxis_title='Coverage Ratio (x)',
        barmode='group',
        hovermode='x unified',
        height=400
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'coverage-analysis-chart')
    
    # Chart 2: Flexibility vs Generation Quality
    fig2 = go.Figure()
    
    flexibility_scores = [cash_flow_adequacy[c]['financial_flexibility_score'] for c in companies_list]
    generation_quality = [cash_flow_adequacy[c]['cash_generation_quality'] for c in companies_list]
    
    fig2.add_trace(go.Scatter(
        x=flexibility_scores,
        y=generation_quality,
        mode='markers+text',
        text=[c[:8] for c in companies_list],
        textposition='top center',
        marker=dict(size=12, color=generation_quality, colorscale='Viridis', showscale=True),
        hovertemplate='<b>%{text}</b><br>Flexibility: %{x:.1f}<br>Quality: %{y:.1f}<extra></extra>'
    ))
    
    fig2.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Excellence")
    fig2.add_vline(x=7, line_dash="dash", line_color="green")
    
    fig2.update_layout(
        title='Flexibility vs Generation Quality Matrix',
        xaxis_title='Financial Flexibility (0-10)',
        yaxis_title='Cash Generation Quality (0-10)',
        height=400
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'flexibility-quality-chart')
    
    # Chart 3: Cash Conversion Efficiency
    fig3 = go.Figure()
    
    conversion_efficiency = [cash_flow_adequacy[c]['cash_conversion_efficiency'] for c in companies_list]
    
    fig3.add_trace(go.Bar(
        x=companies_list,
        y=conversion_efficiency,
        marker_color='steelblue',
        text=[f"{val:.0f}%" for val in conversion_efficiency],
        textposition='outside'
    ))
    
    fig3.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="100% Conversion")
    
    fig3.update_layout(
        title='Earnings to Cash Conversion Analysis',
        xaxis_title='Companies',
        yaxis_title='Cash Conversion Efficiency (%)',
        hovermode='x unified',
        height=400
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'conversion-efficiency-chart')
    
    # Chart 4: Adequacy Score Rankings
    fig4 = go.Figure()
    
    adequacy_scores = [cash_flow_adequacy[c]['adequacy_score'] for c in companies_list]
    
    # Sort by adequacy score
    sorted_data = sorted(zip(companies_list, adequacy_scores), key=lambda x: x[1], reverse=True)
    sorted_companies, sorted_scores = zip(*sorted_data) if sorted_data else ([], [])
    
    fig4.add_trace(go.Bar(
        y=list(sorted_companies),
        x=list(sorted_scores),
        orientation='h',
        marker_color='steelblue',
        text=[f"{score:.1f}" for score in sorted_scores],
        textposition='outside'
    ))
    
    fig4.update_layout(
        title='Cash Flow Adequacy Score Rankings',
        yaxis_title='Companies',
        xaxis_title='Adequacy Score (0-10)',
        height=max(400, len(companies_list) * 30)
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'adequacy-rankings-chart')
    
    return f"""
    <div style="margin: 30px 0;">
        <h5 style="color: var(--text-primary); margin-bottom: 20px;">Cash Flow Adequacy Visualizations</h5>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
    </div>
    """


def _generate_cash_flow_adequacy_summary(cash_flow_adequacy: Dict, total_companies: int) -> str:
    """Generate cash flow adequacy summary"""
    
    avg_adequacy = np.mean([m['adequacy_score'] for m in cash_flow_adequacy.values()])
    avg_flexibility = np.mean([m['financial_flexibility_score'] for m in cash_flow_adequacy.values()])
    avg_coverage = np.mean([m['overall_coverage_ratio'] for m in cash_flow_adequacy.values()])
    
    high_flexibility = sum(1 for m in cash_flow_adequacy.values() if m['flexibility_rating'] == 'High Flexibility')
    strong_coverage = sum(1 for m in cash_flow_adequacy.values() if m['overall_coverage_ratio'] >= 2.0)
    strengthening = sum(1 for m in cash_flow_adequacy.values() if m['cash_flow_outlook'] == 'Strengthening')
    
    avg_generation = np.mean([m['cash_generation_quality'] for m in cash_flow_adequacy.values()])
    avg_conversion = np.mean([m['cash_conversion_efficiency'] for m in cash_flow_adequacy.values()])
    avg_sustainability = np.mean([m['sustainability_score'] for m in cash_flow_adequacy.values()])
    
    return f"""
    <strong>Cash Flow Adequacy Analysis & Financial Flexibility Assessment:</strong>
    <ul>
        <li><strong>Portfolio Adequacy Profile:</strong> {avg_adequacy:.1f}/10 comprehensive cash flow adequacy score</li>
        <li><strong>Financial Flexibility:</strong> {avg_flexibility:.1f}/10 average flexibility with {high_flexibility}/{total_companies} companies achieving high flexibility ratings</li>
        <li><strong>Coverage Strength:</strong> {avg_coverage:.1f}x average overall coverage ratio with {strong_coverage}/{total_companies} companies exceeding 2.0x coverage</li>
        <li><strong>Cash Flow Evolution:</strong> {strengthening}/{total_companies} companies with strengthening cash flow outlook</li>
    </ul>
    
    <strong>Cash Flow Quality Framework:</strong>
    <ul>
        <li><strong>Generation Quality:</strong> {'Excellent' if avg_generation >= 8 else 'Good' if avg_generation >= 6 else 'Requires Enhancement'} cash generation characteristics</li>
        <li><strong>Conversion Efficiency:</strong> {'Optimized' if avg_conversion >= 90 else 'Standard' if avg_conversion >= 70 else 'Improvement Needed'} earnings-to-cash conversion at {avg_conversion:.1f}% average</li>
        <li><strong>Sustainability Profile:</strong> {'Highly Sustainable' if avg_sustainability >= 8 else 'Sustainable' if avg_sustainability >= 6 else 'Sustainability Concerns'} long-term cash generation capability</li>
    </ul>
    
    <strong>Strategic Cash Flow Management:</strong>
    <ul>
        <li><strong>Flexibility Optimization:</strong> {'Maintain high flexibility while optimizing efficiency' if high_flexibility >= total_companies * 0.5 and avg_flexibility >= 7 else 'Enhance financial flexibility and coverage ratios' if avg_adequacy >= 6 else 'Comprehensive cash flow improvement strategy required'} for portfolio resilience</li>
        <li><strong>Coverage Enhancement:</strong> {'Strong defensive cash flow characteristics' if strong_coverage >= total_companies * 0.6 and avg_coverage >= 2.0 else 'Adequate coverage with optimization opportunities' if avg_coverage >= 1.5 else 'Coverage ratio improvement priority'} across all obligations</li>
        <li><strong>Long-term Sustainability:</strong> {'Excellent cash flow sustainability foundation' if strengthening >= total_companies * 0.4 and avg_adequacy >= 7 else 'Develop sustainable cash flow enhancement programs' if avg_adequacy >= 5 else 'Fundamental cash flow capability strengthening needed'} for continued operations and growth</li>
    </ul>
    """


# =============================================================================
# PHASE 5: SECTION 5G - STRATEGIC INSIGHTS & RECOMMENDATIONS
# =============================================================================

def _build_section_5g_strategic_insights(
    df: pd.DataFrame,
    companies: Dict[str, str],
    sector_analysis: Dict,
    institutional_df: pd.DataFrame,
    economic_df: pd.DataFrame
) -> str:
    """Build Section 5G: Comprehensive Financial Stability Summary & Strategic Recommendations"""
    
    # Gather all previous analysis results (in production, these would come from artifacts)
    # For now, we'll recalculate key metrics
    liquidity_analysis = _analyze_enhanced_liquidity(df, companies, institutional_df, sector_analysis)
    solvency_analysis = _analyze_advanced_solvency(df, companies, economic_df, sector_analysis)
    capital_structure = _analyze_capital_structure_optimization(df, companies, economic_df, sector_analysis, institutional_df)
    balance_sheet_quality = _analyze_balance_sheet_quality(df, companies, sector_analysis)
    cash_flow_adequacy = _analyze_cash_flow_adequacy(df, companies, sector_analysis)
    
    # Build HTML content with enhanced visual design
    html = f"""
    <div class="info-section">
        <h3>5G. Comprehensive Financial Stability Summary & Strategic Recommendations</h3>
        
        <div style="margin: 30px 0;">
            {_build_portfolio_overview_cards(liquidity_analysis, solvency_analysis, capital_structure, balance_sheet_quality, cash_flow_adequacy, len(companies))}
        </div>
        
        <div style="margin: 40px 0;">
            {_build_stability_assessment_tabs(liquidity_analysis, solvency_analysis, capital_structure, balance_sheet_quality, cash_flow_adequacy, sector_analysis, institutional_df, len(companies))}
        </div>
        
        <div style="margin: 40px 0;">
            {_build_strategic_recommendations_timeline(liquidity_analysis, solvency_analysis, capital_structure, balance_sheet_quality, cash_flow_adequacy, len(companies))}
        </div>
        
        <div style="margin: 40px 0;">
            {_build_success_metrics_targets(liquidity_analysis, solvency_analysis, capital_structure, balance_sheet_quality, len(companies))}
        </div>
    </div>
    """
    
    return html


def _build_portfolio_overview_cards(
    liquidity_analysis: Dict,
    solvency_analysis: Dict,
    capital_structure: Dict,
    balance_sheet_quality: Dict,
    cash_flow_adequacy: Dict,
    total_companies: int
) -> str:
    """Build portfolio overview with key metric cards"""
    
    # Calculate portfolio-level metrics
    avg_liquidity_score = np.mean([m['adjusted_liquidity_score'] for m in liquidity_analysis.values()]) if liquidity_analysis else 5
    avg_solvency_score = np.mean([m['sustainability_score'] for m in solvency_analysis.values()]) if solvency_analysis else 5
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()]) if capital_structure else 10
    avg_bs_quality = np.mean([m['overall_quality_score'] for m in balance_sheet_quality.values()]) if balance_sheet_quality else 5
    avg_cf_adequacy = np.mean([m['adequacy_score'] for m in cash_flow_adequacy.values()]) if cash_flow_adequacy else 5
    
    # Count excellence metrics
    excellent_liquidity = sum(1 for m in liquidity_analysis.values() if m['liquidity_rating'] == 'Excellent') if liquidity_analysis else 0
    investment_grade = sum(1 for m in solvency_analysis.values() if m['estimated_credit_rating'] in ['A or higher', 'BBB']) if solvency_analysis else 0
    optimal_leverage = sum(1 for m in capital_structure.values() if abs(m['leverage_gap']) <= 5) if capital_structure else 0
    low_bs_risk = sum(1 for m in balance_sheet_quality.values() if m['risk_rating'] == 'Low Risk') if balance_sheet_quality else 0
    high_cf_flexibility = sum(1 for m in cash_flow_adequacy.values() if m['flexibility_rating'] == 'High Flexibility') if cash_flow_adequacy else 0
    
    # Overall portfolio health score
    portfolio_health = np.mean([avg_liquidity_score, avg_solvency_score, avg_bs_quality, avg_cf_adequacy])
    
    # Determine portfolio health rating
    if portfolio_health >= 8:
        health_rating = "Excellent"
        health_color = "success"
        health_icon = "🟢"
    elif portfolio_health >= 6:
        health_rating = "Good"
        health_color = "info"
        health_icon = "🔵"
    elif portfolio_health >= 4:
        health_rating = "Fair"
        health_color = "warning"
        health_icon = "🟡"
    else:
        health_rating = "Needs Improvement"
        health_color = "danger"
        health_icon = "🔴"
    
    return f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h4 style="color: var(--text-primary); margin-bottom: 10px;">Portfolio Financial Stability Overview</h4>
        <div style="font-size: 3rem; margin: 20px 0;">{health_icon}</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-gradient-start); margin-bottom: 5px;">
            {health_rating}
        </div>
        <div style="font-size: 1.1rem; color: var(--text-secondary);">
            Overall Portfolio Health Score: {portfolio_health:.1f}/10
        </div>
    </div>
    
    {build_stat_grid([
        {
            "label": "Liquidity Excellence",
            "value": f"{excellent_liquidity}/{total_companies}",
            "description": f"Avg Score: {avg_liquidity_score:.1f}/10",
            "type": "success" if excellent_liquidity >= total_companies * 0.4 else "info"
        },
        {
            "label": "Investment Grade",
            "value": f"{investment_grade}/{total_companies}",
            "description": f"Sustainability: {avg_solvency_score:.1f}/10",
            "type": "success" if investment_grade >= total_companies * 0.5 else "info"
        },
        {
            "label": "Optimal Capital Structure",
            "value": f"{optimal_leverage}/{total_companies}",
            "description": f"Avg WACC: {avg_wacc:.2f}%",
            "type": "success" if avg_wacc <= 9 else "warning"
        },
        {
            "label": "Low Balance Sheet Risk",
            "value": f"{low_bs_risk}/{total_companies}",
            "description": f"Quality: {avg_bs_quality:.1f}/10",
            "type": "success" if low_bs_risk >= total_companies * 0.5 else "info"
        },
        {
            "label": "High Cash Flow Flexibility",
            "value": f"{high_cf_flexibility}/{total_companies}",
            "description": f"Adequacy: {avg_cf_adequacy:.1f}/10",
            "type": "success" if high_cf_flexibility >= total_companies * 0.4 else "info"
        },
        {
            "label": "Portfolio Resilience",
            "value": f"{portfolio_health:.1f}/10",
            "description": "Comprehensive Stability",
            "type": health_color
        }
    ])}
    """


def _build_stability_assessment_tabs(
    liquidity_analysis: Dict,
    solvency_analysis: Dict,
    capital_structure: Dict,
    balance_sheet_quality: Dict,
    cash_flow_adequacy: Dict,
    sector_analysis: Dict,
    institutional_df: pd.DataFrame,
    total_companies: int
) -> str:
    """Build tabbed stability assessment with visual insights"""
    
    # Calculate key metrics for each area
    avg_liquidity = np.mean([m['adjusted_liquidity_score'] for m in liquidity_analysis.values()]) if liquidity_analysis else 5
    avg_solvency = np.mean([m['sustainability_score'] for m in solvency_analysis.values()]) if solvency_analysis else 5
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()]) if capital_structure else 10
    avg_structure = np.mean([m['structure_score'] for m in capital_structure.values()]) if capital_structure else 5
    avg_bs_quality = np.mean([m['overall_quality_score'] for m in balance_sheet_quality.values()]) if balance_sheet_quality else 5
    avg_cf_adequacy = np.mean([m['adequacy_score'] for m in cash_flow_adequacy.values()]) if cash_flow_adequacy else 5
    
    low_liquidity_risk = sum(1 for m in liquidity_analysis.values() if m['liquidity_risk'] == 'Low') if liquidity_analysis else 0
    low_solvency_risk = sum(1 for m in solvency_analysis.values() if m['risk_level'] == 'Low') if solvency_analysis else 0
    investment_grade = sum(1 for m in solvency_analysis.values() if m['estimated_credit_rating'] in ['A or higher', 'BBB']) if solvency_analysis else 0
    optimal_leverage = sum(1 for m in capital_structure.values() if abs(m['leverage_gap']) <= 5) if capital_structure else 0
    low_bs_risk = sum(1 for m in balance_sheet_quality.values() if m['risk_rating'] == 'Low Risk') if balance_sheet_quality else 0
    high_flexibility = sum(1 for m in cash_flow_adequacy.values() if m['flexibility_rating'] == 'High Flexibility') if cash_flow_adequacy else 0
    
    # Net institutional support
    net_inst_support = np.mean([
        m.get('institutional_liquidity_support', 0) - m.get('institutional_liquidity_pressure', 0)
        for m in liquidity_analysis.values()
    ]) if liquidity_analysis else 0
    
    return f"""
    <h4 style="color: var(--text-primary); margin-bottom: 20px;">📊 Multi-Dimensional Stability Assessment</h4>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
        
        <!-- Liquidity & Risk Card -->
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)); 
                    padding: 25px; border-radius: 16px; border-left: 4px solid #10b981;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2rem; margin-right: 10px;">💧</span>
                <h5 style="margin: 0; color: var(--text-primary);">Liquidity & Short-Term Risk</h5>
            </div>
            <div style="margin: 15px 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #10b981;">{avg_liquidity:.1f}/10</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">Portfolio Liquidity Score</div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 15px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Low Risk Companies:</span>
                    <strong style="color: var(--text-primary);">{low_liquidity_risk}/{total_companies}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Institutional Support:</span>
                    <strong style="color: {'#10b981' if net_inst_support > 0 else '#ef4444'};">{net_inst_support:+.2f}</strong>
                </div>
                <div style="margin-top: 12px; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong>Assessment:</strong> {'Excellent liquidity foundation with strong institutional backing' if avg_liquidity >= 7 and net_inst_support > 0 else 'Solid liquidity position' if avg_liquidity >= 5 else 'Liquidity enhancement needed'}
                </div>
            </div>
        </div>
        
        <!-- Solvency & Credit Card -->
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)); 
                    padding: 25px; border-radius: 16px; border-left: 4px solid #3b82f6;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2rem; margin-right: 10px;">🏦</span>
                <h5 style="margin: 0; color: var(--text-primary);">Solvency & Credit Quality</h5>
            </div>
            <div style="margin: 15px 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #3b82f6;">{avg_solvency:.1f}/10</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">Debt Sustainability Score</div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 15px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Low Risk Companies:</span>
                    <strong style="color: var(--text-primary);">{low_solvency_risk}/{total_companies}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Investment Grade:</span>
                    <strong style="color: var(--text-primary);">{investment_grade}/{total_companies}</strong>
                </div>
                <div style="margin-top: 12px; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong>Assessment:</strong> {'Strong debt management with investment-grade characteristics' if investment_grade >= total_companies * 0.5 else 'Adequate solvency position' if avg_solvency >= 5 else 'Debt sustainability improvement needed'}
                </div>
            </div>
        </div>
        
        <!-- Capital Structure Card -->
        <div style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(168, 85, 247, 0.05)); 
                    padding: 25px; border-radius: 16px; border-left: 4px solid #a855f7;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2rem; margin-right: 10px;">⚖️</span>
                <h5 style="margin: 0; color: var(--text-primary);">Capital Structure & WACC</h5>
            </div>
            <div style="margin: 15px 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #a855f7;">{avg_wacc:.2f}%</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">Average WACC</div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 15px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Optimal Leverage:</span>
                    <strong style="color: var(--text-primary);">{optimal_leverage}/{total_companies}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Structure Score:</span>
                    <strong style="color: var(--text-primary);">{avg_structure:.1f}/10</strong>
                </div>
                <div style="margin-top: 12px; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong>Assessment:</strong> {'Industry-leading capital efficiency' if avg_wacc <= 8 and optimal_leverage >= total_companies * 0.5 else 'Competitive capital structure' if avg_wacc <= 10 else 'Capital structure optimization opportunities'}
                </div>
            </div>
        </div>
        
        <!-- Balance Sheet Quality Card -->
        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05)); 
                    padding: 25px; border-radius: 16px; border-left: 4px solid #f59e0b;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2rem; margin-right: 10px;">📋</span>
                <h5 style="margin: 0; color: var(--text-primary);">Balance Sheet Quality</h5>
            </div>
            <div style="margin: 15px 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #f59e0b;">{avg_bs_quality:.1f}/10</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">Overall Quality Score</div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 15px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Low Risk Companies:</span>
                    <strong style="color: var(--text-primary);">{low_bs_risk}/{total_companies}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Hidden Risk:</span>
                    <strong style="color: var(--text-primary);">{'Low' if low_bs_risk >= total_companies * 0.6 else 'Medium'}</strong>
                </div>
                <div style="margin-top: 12px; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong>Assessment:</strong> {'High-quality balance sheets with minimal hidden risks' if avg_bs_quality >= 7 else 'Adequate balance sheet quality' if avg_bs_quality >= 5 else 'Quality enhancement opportunities'}
                </div>
            </div>
        </div>
        
        <!-- Cash Flow Adequacy Card -->
        <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(236, 72, 153, 0.05)); 
                    padding: 25px; border-radius: 16px; border-left: 4px solid #ec4899;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2rem; margin-right: 10px;">💰</span>
                <h5 style="margin: 0; color: var(--text-primary);">Cash Flow & Flexibility</h5>
            </div>
            <div style="margin: 15px 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #ec4899;">{avg_cf_adequacy:.1f}/10</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">Adequacy Score</div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 15px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">High Flexibility:</span>
                    <strong style="color: var(--text-primary);">{high_flexibility}/{total_companies}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Coverage:</span>
                    <strong style="color: var(--text-primary);">{'Strong' if avg_cf_adequacy >= 7 else 'Adequate'}</strong>
                </div>
                <div style="margin-top: 12px; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong>Assessment:</strong> {'Excellent cash generation with high operational flexibility' if avg_cf_adequacy >= 7 and high_flexibility >= total_companies * 0.4 else 'Adequate cash flow coverage' if avg_cf_adequacy >= 5 else 'Cash flow enhancement opportunities'}
                </div>
            </div>
        </div>
        
        <!-- Overall Risk Profile Card -->
        <div style="background: linear-gradient(135deg, rgba(100, 116, 139, 0.1), rgba(100, 116, 139, 0.05)); 
                    padding: 25px; border-radius: 16px; border-left: 4px solid #64748b;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2rem; margin-right: 10px;">🎯</span>
                <h5 style="margin: 0; color: var(--text-primary);">Composite Risk Profile</h5>
            </div>
            <div style="margin: 15px 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #64748b;">
                    {((low_liquidity_risk + low_solvency_risk + low_bs_risk) / (total_companies * 3) * 100):.0f}%
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">Low Risk Coverage</div>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 15px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Risk Dimensions:</span>
                    <strong style="color: var(--text-primary);">5/5</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="color: var(--text-secondary);">Overall Rating:</span>
                    <strong style="color: var(--text-primary);">
                        {
                            'Excellent' if (low_liquidity_risk + low_solvency_risk + low_bs_risk) >= total_companies * 1.8 
                            else 'Good' if (low_liquidity_risk + low_solvency_risk + low_bs_risk) >= total_companies * 1.2 
                            else 'Moderate'
                        }
                    </strong>
                </div>
                <div style="margin-top: 12px; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong>Assessment:</strong> {'Comprehensive low-risk profile across all dimensions' if (low_liquidity_risk + low_solvency_risk + low_bs_risk) >= total_companies * 1.5 else 'Balanced risk profile with optimization opportunities' if (low_liquidity_risk + low_solvency_risk + low_bs_risk) >= total_companies * 0.9 else 'Elevated risk profile requiring systematic improvement'}
                </div>
            </div>
        </div>
        
    </div>
    """


def _build_strategic_recommendations_timeline(
    liquidity_analysis: Dict,
    solvency_analysis: Dict,
    capital_structure: Dict,
    balance_sheet_quality: Dict,
    cash_flow_adequacy: Dict,
    total_companies: int
) -> str:
    """Build strategic recommendations with timeline approach"""
    
    # Calculate key metrics for recommendations
    avg_liquidity = np.mean([m['adjusted_liquidity_score'] for m in liquidity_analysis.values()]) if liquidity_analysis else 5
    avg_solvency = np.mean([m['sustainability_score'] for m in solvency_analysis.values()]) if solvency_analysis else 5
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()]) if capital_structure else 10
    avg_bs_quality = np.mean([m['overall_quality_score'] for m in balance_sheet_quality.values()]) if balance_sheet_quality else 5
    avg_cf_adequacy = np.mean([m['adequacy_score'] for m in cash_flow_adequacy.values()]) if cash_flow_adequacy else 5
    
    excellent_liquidity = sum(1 for m in liquidity_analysis.values() if m['liquidity_rating'] == 'Excellent') if liquidity_analysis else 0
    investment_grade = sum(1 for m in solvency_analysis.values() if m['estimated_credit_rating'] in ['A or higher', 'BBB']) if solvency_analysis else 0
    optimal_leverage = sum(1 for m in capital_structure.values() if abs(m['leverage_gap']) <= 5) if capital_structure else 0
    
    return f"""
    <h4 style="color: var(--text-primary); margin-bottom: 20px;">🎯 Strategic Enhancement Roadmap</h4>
    
    <!-- Immediate Priorities (0-6 months) -->
    <div style="margin-bottom: 30px;">
        <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)); 
                   border-radius: 12px; border-left: 4px solid #ef4444; margin-bottom: 15px;"
             onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                     document.getElementById('immediate-priorities').style.display = document.getElementById('immediate-priorities').style.display === 'none' ? 'block' : 'none';">
            <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: #ef4444;">▼</span>
            <h5 style="margin: 0; color: var(--text-primary); flex-grow: 1;">⚡ Immediate Priorities (0-6 months)</h5>
            <span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">HIGH PRIORITY</span>
        </div>
        
        <div id="immediate-priorities" style="display: block; padding: 0 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 20px 0;">
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">💧</span>
                        <strong style="color: var(--text-primary);">Liquidity Management</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        {'Optimize working capital efficiency while maintaining excellent liquidity' if excellent_liquidity >= total_companies * 0.4 
                         else 'Enhance liquidity positions and implement stress testing protocols' if avg_liquidity >= 5 
                         else 'Comprehensive liquidity improvement and risk management program'}
                    </p>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1);">
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            <strong>Action Items:</strong><br>
                            • Review cash conversion cycles<br>
                            • Optimize working capital ratios<br>
                            • Strengthen short-term liquidity buffers
                        </div>
                    </div>
                </div>
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">🏦</span>
                        <strong style="color: var(--text-primary);">Solvency Strengthening</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        {'Maintain investment-grade characteristics and optimize coverage ratios' if investment_grade >= total_companies * 0.5 
                         else 'Develop solvency enhancement initiatives and debt sustainability programs' if avg_solvency >= 5 
                         else 'Comprehensive debt management and solvency improvement strategy'}
                    </p>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1);">
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            <strong>Action Items:</strong><br>
                            • Review debt service coverage<br>
                            • Optimize interest coverage ratios<br>
                            • Enhance credit quality metrics
                        </div>
                    </div>
                </div>
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">⚖️</span>
                        <strong style="color: var(--text-primary);">Capital Structure Optimization</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        {'Fine-tune existing optimal structures for efficiency gains' if optimal_leverage >= total_companies * 0.5 
                         else 'Implement systematic capital structure optimization initiatives' if avg_wacc <= 12 
                         else 'Comprehensive capital structure restructuring and WACC reduction program'}
                    </p>
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1);">
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            <strong>Action Items:</strong><br>
                            • Assess current leverage positions<br>
                            • Optimize debt-equity mix<br>
                            • Reduce weighted average cost of capital
                        </div>
                    </div>
                </div>
                
            </div>
        </div>
    </div>
    
    <!-- Medium-Term Framework (6-18 months) -->
    <div style="margin-bottom: 30px;">
        <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05)); 
                   border-radius: 12px; border-left: 4px solid #f59e0b; margin-bottom: 15px;"
             onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                     document.getElementById('medium-term').style.display = document.getElementById('medium-term').style.display === 'none' ? 'block' : 'none';">
            <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: #f59e0b;">▼</span>
            <h5 style="margin: 0; color: var(--text-primary); flex-grow: 1;">📈 Medium-Term Enhancement (6-18 months)</h5>
            <span style="background: #f59e0b; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">MEDIUM PRIORITY</span>
        </div>
        
        <div id="medium-term" style="display: block; padding: 0 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 20px 0;">
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">🛡️</span>
                        <strong style="color: var(--text-primary);">Risk Management Excellence</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        Scale risk management best practices and maintain defensive positioning across all financial stability dimensions.
                    </p>
                </div>
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">📋</span>
                        <strong style="color: var(--text-primary);">Balance Sheet Quality Enhancement</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        {'Maintain excellence while optimizing asset efficiency and transparency' if avg_bs_quality >= 7 
                         else 'Implement balance sheet quality improvement and hidden risk mitigation programs' if avg_bs_quality >= 5 
                         else 'Comprehensive balance sheet transformation and quality enhancement initiative'}
                    </p>
                </div>
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">💰</span>
                        <strong style="color: var(--text-primary);">Cash Flow Optimization</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        {'Leverage strong cash generation for growth while maintaining flexibility' if avg_cf_adequacy >= 7 
                         else 'Enhance cash flow adequacy and develop financial flexibility capabilities' if avg_cf_adequacy >= 5 
                         else 'Comprehensive cash flow improvement and flexibility development program'}
                    </p>
                </div>
                
            </div>
        </div>
    </div>
    
    <!-- Long-Term Leadership (18+ months) -->
    <div style="margin-bottom: 30px;">
        <div style="display: flex; align-items: center; cursor: pointer; padding: 15px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)); 
                   border-radius: 12px; border-left: 4px solid #10b981; margin-bottom: 15px;"
             onclick="this.querySelector('.collapse-icon').textContent = this.querySelector('.collapse-icon').textContent === '▼' ? '▶' : '▼'; 
                     document.getElementById('long-term').style.display = document.getElementById('long-term').style.display === 'none' ? 'block' : 'none';">
            <span class="collapse-icon" style="font-size: 1.2rem; margin-right: 10px; color: #10b981;">▼</span>
            <h5 style="margin: 0; color: var(--text-primary); flex-grow: 1;">🚀 Long-Term Stability Leadership (18+ months)</h5>
            <span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">STRATEGIC</span>
        </div>
        
        <div id="long-term" style="display: block; padding: 0 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 20px 0;">
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">🏰</span>
                        <strong style="color: var(--text-primary);">Financial Fortress Development</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        Establish industry-leading financial stability standards and defensive characteristics for economic cycle resilience.
                    </p>
                </div>
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">💎</span>
                        <strong style="color: var(--text-primary);">Capital Allocation Mastery</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        Advanced capital optimization and value creation scaling through efficient structures for superior returns.
                    </p>
                </div>
                
                <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem; margin-right: 10px;">⭐</span>
                        <strong style="color: var(--text-primary);">Institutional Excellence Recognition</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 10px 0;">
                        Maintain institutional confidence through transparency and stability leadership for market leadership position.
                    </p>
                </div>
                
            </div>
        </div>
    </div>
    """


def _build_success_metrics_targets(
    liquidity_analysis: Dict,
    solvency_analysis: Dict,
    capital_structure: Dict,
    balance_sheet_quality: Dict,
    total_companies: int
) -> str:
    """Build success metrics and performance targets"""
    
    # Current metrics
    excellent_liquidity = sum(1 for m in liquidity_analysis.values() if m['liquidity_rating'] == 'Excellent') if liquidity_analysis else 0
    investment_grade = sum(1 for m in solvency_analysis.values() if m['estimated_credit_rating'] in ['A or higher', 'BBB']) if solvency_analysis else 0
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()]) if capital_structure else 10
    low_risk_total = (
        sum(1 for m in liquidity_analysis.values() if m['liquidity_risk'] == 'Low') +
        sum(1 for m in solvency_analysis.values() if m['risk_level'] == 'Low') +
        sum(1 for m in balance_sheet_quality.values() if m['risk_rating'] == 'Low Risk')
    ) if liquidity_analysis and solvency_analysis and balance_sheet_quality else 0
    
    # Target calculations
    target_excellent_liquidity = min(total_companies, excellent_liquidity + max(1, (total_companies - excellent_liquidity) // 2))
    target_investment_grade = min(total_companies, investment_grade + max(1, (total_companies - investment_grade) // 2))
    target_wacc = max(6.0, avg_wacc - 1.0)
    target_low_risk = min(total_companies * 3, low_risk_total + max(1, (total_companies * 3 - low_risk_total) // 3))
    
    return f"""
    <h4 style="color: var(--text-primary); margin-bottom: 20px;">🎯 Success Metrics & Performance Targets</h4>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        
        <!-- Target 1: Liquidity Excellence -->
        <div style="background: var(--card-bg); padding: 25px; border-radius: 16px; border: 1px solid var(--card-border);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <span style="font-size: 1.5rem;">💧</span>
                <span style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600;">18 MONTHS</span>
            </div>
            <h5 style="color: var(--text-primary); margin: 10px 0;">Liquidity Excellence</h5>
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Current:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary);">{excellent_liquidity}/{total_companies}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Target:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #10b981;">{target_excellent_liquidity}/{total_companies}</span>
                </div>
            </div>
            {build_completeness_bar((excellent_liquidity / total_companies * 100) if total_companies > 0 else 0, "")}
        </div>
        
        <!-- Target 2: Investment Grade -->
        <div style="background: var(--card-bg); padding: 25px; border-radius: 16px; border: 1px solid var(--card-border);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <span style="font-size: 1.5rem;">🏦</span>
                <span style="background: rgba(59, 130, 246, 0.1); color: #3b82f6; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600;">24 MONTHS</span>
            </div>
            <h5 style="color: var(--text-primary); margin: 10px 0;">Investment Grade</h5>
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Current:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary);">{investment_grade}/{total_companies}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Target:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #3b82f6;">{target_investment_grade}/{total_companies}</span>
                </div>
            </div>
            {build_completeness_bar((investment_grade / total_companies * 100) if total_companies > 0 else 0, "")}
        </div>
        
        <!-- Target 3: WACC Optimization -->
        <div style="background: var(--card-bg); padding: 25px; border-radius: 16px; border: 1px solid var(--card-border);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <span style="font-size: 1.5rem;">⚖️</span>
                <span style="background: rgba(168, 85, 247, 0.1); color: #a855f7; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600;">30 MONTHS</span>
            </div>
            <h5 style="color: var(--text-primary); margin: 10px 0;">WACC Optimization</h5>
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Current:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary);">{avg_wacc:.2f}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Target:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #a855f7;">{target_wacc:.2f}%</span>
                </div>
            </div>
            {build_completeness_bar(max(0, 100 - (avg_wacc / 15 * 100)), "")}
        </div>
        
        <!-- Target 4: Risk Management -->
        <div style="background: var(--card-bg); padding: 25px; border-radius: 16px; border: 1px solid var(--card-border);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <span style="font-size: 1.5rem;">🎯</span>
                <span style="background: rgba(245, 158, 11, 0.1); color: #f59e0b; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600;">36 MONTHS</span>
            </div>
            <h5 style="color: var(--text-primary); margin: 10px 0;">Low Risk Classifications</h5>
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Current:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary);">{low_risk_total}/{total_companies * 3}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">Target:</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #f59e0b;">{target_low_risk}/{total_companies * 3}</span>
                </div>
            </div>
            {build_completeness_bar((low_risk_total / (total_companies * 3) * 100) if total_companies > 0 else 0, "")}
        </div>
        
    </div>
    
    <div style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, rgba(100, 116, 139, 0.05), rgba(100, 116, 139, 0.02)); 
               border-radius: 16px; border: 1px solid var(--card-border);">
        <h5 style="color: var(--text-primary); margin-bottom: 15px;">📊 Performance Tracking Framework</h5>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Quarterly Reviews</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-gradient-start);">✓</div>
            </div>
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Progress Dashboards</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-gradient-start);">✓</div>
            </div>
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Adjustment Protocols</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-gradient-start);">✓</div>
            </div>
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Stakeholder Reporting</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-gradient-start);">✓</div>
            </div>
        </div>
    </div>
    """
# =============================================================================
# ENHANCEMENTS: TOP 3 PRIORITY FEATURES
# =============================================================================

# Add these functions to section_05.py

def _get_trend_indicator(current_value: float, historical_values: List[float], 
                        higher_is_better: bool = True) -> str:
    """
    Generate trend indicator with emoji and direction arrow
    
    Args:
        current_value: Most recent value
        historical_values: List of historical values (3-5 periods)
        higher_is_better: True if higher values indicate improvement
    
    Returns:
        HTML string with emoji and arrow (e.g., "🟢 ↑")
    """
    
    if not historical_values or len(historical_values) < 2:
        return '<span style="color: #94a3b8;">⚪ →</span>'  # Neutral - insufficient data
    
    historical_avg = np.mean(historical_values)
    
    # Calculate percentage change
    if historical_avg != 0:
        pct_change = ((current_value - historical_avg) / historical_avg) * 100
    else:
        pct_change = 0
    
    # Determine if improving or declining
    is_improving = (pct_change > 10) if higher_is_better else (pct_change < -10)
    is_declining = (pct_change < -10) if higher_is_better else (pct_change > 10)
    
    # Return appropriate indicator
    if is_improving:
        return '<span style="color: #10b981; font-weight: 600;">🟢 ↑</span>'
    elif is_declining:
        return '<span style="color: #ef4444; font-weight: 600;">🔴 ↓</span>'
    else:
        return '<span style="color: #3b82f6; font-weight: 600;">🔵 →</span>'


def _build_section_navigation() -> str:
    """Build sticky navigation menu for Section 5"""
    
    return """
    <div id="section-nav" style="position: sticky; top: 20px; z-index: 100; 
                background: var(--card-bg); backdrop-filter: blur(20px) saturate(180%);
                padding: 15px 20px; border-radius: 16px; margin-bottom: 30px; 
                box-shadow: var(--shadow-lg); border: 1px solid var(--card-border);
                animation: slideIn 0.6s ease;">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 1.2rem; margin-right: 10px;">🧭</span>
            <strong style="color: var(--text-primary); font-size: 1rem;">Section 5 Navigation</strong>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <a href="#section-5a" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                💧 5A: Liquidity
            </a>
            <a href="#section-5b" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(59, 130, 246, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                🏦 5B: Solvency
            </a>
            <a href="#section-5c" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(168, 85, 247, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(168, 85, 247, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(168, 85, 247, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                ⚖️ 5C: Capital
            </a>
            <a href="#section-5d" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(245, 158, 11, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(245, 158, 11, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                📋 5D: Balance Sheet
            </a>
            <a href="#section-5e" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(236, 72, 153, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(236, 72, 153, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(236, 72, 153, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                💰 5E: Cash Flow
            </a>
            <a href="#section-5g" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(100, 116, 139, 0.1), rgba(100, 116, 139, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(100, 116, 139, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(100, 116, 139, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                🎯 5G: Insights
            </a>
            <a href="#top" style="padding: 8px 16px; border-radius: 8px; 
                      background: linear-gradient(135deg, rgba(148, 163, 184, 0.1), rgba(148, 163, 184, 0.05));
                      color: var(--text-primary); text-decoration: none; font-size: 0.9rem; 
                      font-weight: 600; border: 1px solid rgba(148, 163, 184, 0.2);
                      transition: all 0.3s ease; display: inline-block;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(148, 163, 184, 0.3)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                ⬆️ Top
            </a>
        </div>
    </div>
    """


def _build_key_takeaways(
    liquidity_analysis: Dict,
    solvency_analysis: Dict,
    capital_structure: Dict,
    balance_sheet_quality: Dict,
    cash_flow_adequacy: Dict,
    df: pd.DataFrame,
    total_companies: int
) -> str:
    """Build key takeaways summary box at the top of Section 5"""
    
    # Calculate overall portfolio health
    avg_liquidity = np.mean([m['adjusted_liquidity_score'] for m in liquidity_analysis.values()]) if liquidity_analysis else 5
    avg_solvency = np.mean([m['sustainability_score'] for m in solvency_analysis.values()]) if solvency_analysis else 5
    avg_wacc = np.mean([m['wacc'] for m in capital_structure.values()]) if capital_structure else 10
    avg_bs_quality = np.mean([m['overall_quality_score'] for m in balance_sheet_quality.values()]) if balance_sheet_quality else 5
    avg_cf_adequacy = np.mean([m['adequacy_score'] for m in cash_flow_adequacy.values()]) if cash_flow_adequacy else 5
    
    portfolio_health = np.mean([avg_liquidity, avg_solvency, avg_bs_quality, avg_cf_adequacy])
    
    # Determine health rating
    if portfolio_health >= 8:
        health_rating = "Excellent"
        health_icon = "🟢"
    elif portfolio_health >= 6:
        health_rating = "Good"
        health_icon = "🔵"
    elif portfolio_health >= 4:
        health_rating = "Fair"
        health_icon = "🟡"
    else:
        health_rating = "Needs Improvement"
        health_icon = "🔴"
    
    # Identify best area (highest score)
    areas = {
        'Liquidity': avg_liquidity,
        'Solvency': avg_solvency,
        'Balance Sheet Quality': avg_bs_quality,
        'Cash Flow Adequacy': avg_cf_adequacy,
        'Capital Efficiency': 10 - (avg_wacc / 1.5) if avg_wacc > 0 else 5
    }
    best_area = max(areas.items(), key=lambda x: x[1])
    
    # Identify area needing attention (lowest score, excluding WACC which is inverted)
    needs_attention_areas = {
        'Liquidity': avg_liquidity,
        'Solvency': avg_solvency,
        'Balance Sheet Quality': avg_bs_quality,
        'Cash Flow Adequacy': avg_cf_adequacy
    }
    needs_attention = min(needs_attention_areas.items(), key=lambda x: x[1])
    
    # Count investment grade
    investment_grade = sum(1 for m in solvency_analysis.values() 
                          if m['estimated_credit_rating'] in ['A or higher', 'BBB']) if solvency_analysis else 0
    
    # Calculate trend indicators for key metrics
    liquidity_trend = ""
    solvency_trend = ""
    wacc_trend = ""
    
    if not df.empty:
        # Get historical data for trend analysis
        recent_years = df.groupby('Year').agg({
            'currentRatio': 'mean',
            'interestCoverageRatio': 'mean'
        }).tail(5)
        
        if len(recent_years) >= 3:
            liquidity_historical = recent_years['currentRatio'].head(3).tolist()
            current_liquidity = recent_years['currentRatio'].iloc[-1]
            liquidity_trend = _get_trend_indicator(current_liquidity, liquidity_historical, higher_is_better=True)
            
            solvency_historical = recent_years['interestCoverageRatio'].head(3).tolist()
            current_solvency = recent_years['interestCoverageRatio'].iloc[-1]
            solvency_trend = _get_trend_indicator(current_solvency, solvency_historical, higher_is_better=True)
    
    return f"""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.1)); 
               padding: 30px; border-radius: 20px; margin-bottom: 30px; 
               border: 2px solid var(--primary-gradient-start);
               box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
               animation: slideIn 0.6s ease;">
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <span style="font-size: 2rem; margin-right: 15px;">🔑</span>
            <h3 style="margin: 0; color: var(--text-primary); font-size: 1.5rem;">Key Takeaways - Section 5</h3>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            
            <!-- Portfolio Health -->
            <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; 
                       border-left: 4px solid var(--primary-gradient-start);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <strong style="color: var(--text-secondary); font-size: 0.9rem;">PORTFOLIO HEALTH</strong>
                    <span style="font-size: 1.5rem;">{health_icon}</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin: 10px 0;">
                    {health_rating}
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Overall Score: {portfolio_health:.1f}/10
                </div>
            </div>
            
            <!-- Top Strength -->
            <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; 
                       border-left: 4px solid #10b981;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <strong style="color: var(--text-secondary); font-size: 0.9rem;">TOP STRENGTH</strong>
                    <span style="font-size: 1.5rem;">💪</span>
                </div>
                <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-primary); margin: 10px 0;">
                    {best_area[0]}
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Score: {best_area[1]:.1f}/10
                </div>
            </div>
            
            <!-- Priority Area -->
            <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; 
                       border-left: 4px solid #f59e0b;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <strong style="color: var(--text-secondary); font-size: 0.9rem;">PRIORITY AREA</strong>
                    <span style="font-size: 1.5rem;">🎯</span>
                </div>
                <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-primary); margin: 10px 0;">
                    {needs_attention[0]}
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    Score: {needs_attention[1]:.1f}/10
                </div>
            </div>
            
            <!-- Investment Grade -->
            <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; 
                       border-left: 4px solid #3b82f6;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <strong style="color: var(--text-secondary); font-size: 0.9rem;">INVESTMENT GRADE</strong>
                    <span style="font-size: 1.5rem;">⭐</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin: 10px 0;">
                    {investment_grade}/{total_companies}
                </div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">
                    BBB or Higher
                </div>
            </div>
            
        </div>
        
        <!-- Trend Summary -->
        <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.5); 
                   border-radius: 12px; display: flex; flex-wrap: wrap; gap: 20px; align-items: center;">
            <div style="flex: 1; min-width: 200px;">
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">
                    <strong>Recent Trends:</strong>
                </div>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    {f'<div style="display: flex; align-items: center; gap: 8px;"><span>Liquidity:</span>{liquidity_trend}</div>' if liquidity_trend else ''}
                    {f'<div style="display: flex; align-items: center; gap: 8px;"><span>Solvency:</span>{solvency_trend}</div>' if solvency_trend else ''}
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span>WACC:</span>
                        <span style="color: {'#10b981' if avg_wacc <= 9 else '#f59e0b' if avg_wacc <= 11 else '#ef4444'}; font-weight: 600;">
                            {avg_wacc:.2f}%
                        </span>
                    </div>
                </div>
            </div>
            <div style="flex: 0 0 auto;">
                <a href="#section-5g" style="padding: 10px 20px; background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)); 
                          color: white; text-decoration: none; border-radius: 8px; font-weight: 600;
                          display: inline-block; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);"
                   onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.4)';"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.3)';">
                    View Strategic Insights →
                </a>
            </div>
        </div>
    </div>
    """
