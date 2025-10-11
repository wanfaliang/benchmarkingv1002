"""
Section 6: Workforce & Productivity Analysis
Phase 1: Scaffolding + Subsections 6A & 6B
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    build_badge,
    build_colored_cell,
    build_completeness_bar,
    build_progress_indicator
)



def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 6: Workforce & Productivity Analysis
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    df = collector.get_all_financial_data()
    
    # Get additional data sources
    try:
        economic_df = collector.get_economic()
    except:
        economic_df = pd.DataFrame()
    
    # Build all subsections
    section_6a_html = _build_section_6a_workforce_trends(df, companies, economic_df)
    section_6b_html = _build_section_6b_productivity_analysis(df, companies)
    section_6c_html = _build_section_6c_optimization(df, companies)
    section_6d_html = _build_section_6d_human_capital_roi(df, companies)
    section_6e_html = _build_section_6e_comparative_analysis(df, companies)
    section_6f_html = _build_section_6f_visualizations(df, companies)
    section_6g_html = _build_section_6g_insights(df, companies)
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        {section_6a_html}
        {build_section_divider() if section_6b_html else ""}
        {section_6b_html}
        {build_section_divider() if section_6c_html else ""}
        {section_6c_html}
        {build_section_divider() if section_6d_html else ""}
        {section_6d_html}
        {build_section_divider() if section_6e_html else ""}
        {section_6e_html}
        {build_section_divider() if section_6f_html else ""}
        {section_6f_html}
        {build_section_divider() if section_6g_html else ""}
        {section_6g_html}
    </div>
    """
    
    return generate_section_wrapper(6, "Workforce & Productivity Analysis", content)


# =============================================================================
# SUBSECTION 6A: EMPLOYEE COUNT TRENDS & WORKFORCE EVOLUTION
# =============================================================================

def _build_section_6a_workforce_trends(df: pd.DataFrame, companies: Dict[str, str], 
                                       economic_df: pd.DataFrame) -> str:
    """Build subsection 6A: Employee Count Trends & Workforce Evolution"""
    
    # Analyze workforce trends
    workforce_trends = _analyze_workforce_trends(df, companies, economic_df)
    
    if not workforce_trends:
        return build_info_box("Insufficient data for workforce trends analysis.", "warning")
    
    # Create KPI cards
    total_employees = sum(m['current_employees'] for m in workforce_trends.values())
    avg_growth_1y = np.mean([m['employee_growth_1y'] for m in workforce_trends.values()])
    avg_cagr = np.mean([m['employee_cagr'] for m in workforce_trends.values()])
    rapid_growers = sum(1 for m in workforce_trends.values() if m['growth_phase'] == 'Rapid Expansion')
    
    kpi_cards = [
        {
            "label": "Total Portfolio Employees",
            "value": f"{int(total_employees):,}",
            "description": "Across all companies",
            "type": "info"
        },
        {
            "label": "Average 1Y Growth",
            "value": f"{avg_growth_1y:+.1f}%",
            "description": "Year-over-year change",
            "type": "success" if avg_growth_1y > 5 else "warning" if avg_growth_1y > 0 else "danger"
        },
        {
            "label": "Portfolio CAGR",
            "value": f"{avg_cagr:+.1f}%",
            "description": "Compound annual growth",
            "type": "success" if avg_cagr > 5 else "info"
        },
        {
            "label": "Rapid Growth Companies",
            "value": f"{rapid_growers}/{len(companies)}",
            "description": "In expansion phase",
            "type": "success" if rapid_growers >= len(companies) * 0.3 else "info"
        }
    ]
    
    kpi_html = build_stat_grid(kpi_cards)
    
    # Create workforce trends table
    table_data = []
    for company_name, metrics in workforce_trends.items():
        table_data.append({
            "Company": company_name,
            "Current Employees": f"{int(metrics['current_employees']):,}",
            "1Y Growth (%)": f"{metrics['employee_growth_1y']:.1f}",
            "CAGR (%)": f"{metrics['employee_cagr']:.1f}",
            "Workforce Scale": metrics['workforce_scale'],
            "Scaling Strategy": metrics['scaling_strategy'],
            "Growth Phase": metrics['growth_phase'],
            "Scaling Efficiency": f"{metrics['scaling_efficiency']:.2f}",
            "Volatility": f"{metrics['workforce_volatility']:.1f}",
            "Consistency": f"{metrics['workforce_consistency']:.1f}/10",
            "Scale Advantages": metrics['scale_advantages']
        })
    
    table_df = pd.DataFrame(table_data)
    
    # Color coding for growth phase
    def growth_phase_color(val):
        if val == 'Rapid Expansion':
            return 'excellent'
        elif val == 'Steady Growth':
            return 'good'
        elif val == 'Stable':
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'Growth Phase': growth_phase_color
    }
    
    badge_columns = ['Scaling Strategy', 'Workforce Scale']
    
    table_html = build_enhanced_table(table_df, "workforce-trends-table", 
                                     color_columns=color_columns,
                                     badge_columns=badge_columns)
    
    # Create charts
    charts_html = _create_workforce_evolution_charts(df, companies, workforce_trends)
    
    # Generate summary
    summary = _generate_workforce_trends_summary(workforce_trends, len(companies))
    summary_html = build_info_box(summary, "info", "Workforce Evolution Summary")
    
    # Build collapsible subsection
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6a')">
            <span>6A. Employee Count Trends & Workforce Evolution</span>
            <span id="subsection-6a-toggle" style="font-size: 1.2rem;">â–¼</span>
        </h3>
        <div id="subsection-6a" style="display: block;">
            <h4>Workforce Growth & Strategic Scaling Analysis</h4>
            {kpi_html}
            {table_html}
            {summary_html}
            {charts_html}
        </div>
    </div>
    
    <script>
    function toggleSubsection(id) {{
        const content = document.getElementById(id);
        const toggle = document.getElementById(id + '-toggle');
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            toggle.textContent = 'â–¼';
        }} else {{
            content.style.display = 'none';
            toggle.textContent = 'â–¶';
        }}
    }}
    </script>
    """
    
    return subsection_html


def _analyze_workforce_trends(df: pd.DataFrame, companies: Dict[str, str], 
                              economic_df: pd.DataFrame) -> Dict[str, Dict]:
    """Analyze workforce trends and evolution patterns"""
    
    workforce_trends = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        metrics = {}
        
        # Employee count analysis
        employee_series = company_data['employeeCount'].dropna()
        
        if len(employee_series) >= 2:
            current_employees = employee_series.iloc[-1]
            previous_employees = employee_series.iloc[-2]
            
            metrics['current_employees'] = current_employees
            metrics['previous_employees'] = previous_employees
            
            # Growth calculations
            if previous_employees > 0:
                metrics['employee_growth_1y'] = ((current_employees - previous_employees) / previous_employees) * 100
            else:
                metrics['employee_growth_1y'] = 0
            
            # Multi-year growth if available
            if len(employee_series) >= 3:
                earliest_employees = employee_series.iloc[0]
                years_span = len(employee_series) - 1
                if earliest_employees > 0 and years_span > 0:
                    cagr = ((current_employees / earliest_employees) ** (1/years_span) - 1) * 100
                    metrics['employee_cagr'] = cagr
                else:
                    metrics['employee_cagr'] = 0
            else:
                metrics['employee_cagr'] = metrics['employee_growth_1y']
            
            # Workforce volatility
            if len(employee_series) >= 3:
                growth_rates = []
                for i in range(1, len(employee_series)):
                    if employee_series.iloc[i-1] > 0:
                        growth_rate = ((employee_series.iloc[i] - employee_series.iloc[i-1]) / employee_series.iloc[i-1]) * 100
                        growth_rates.append(growth_rate)
                
                if growth_rates:
                    metrics['workforce_volatility'] = np.std(growth_rates)
                    metrics['workforce_consistency'] = max(0, min(10, 10 - metrics['workforce_volatility'] / 2))
                else:
                    metrics['workforce_volatility'] = 0
                    metrics['workforce_consistency'] = 5
            else:
                metrics['workforce_volatility'] = abs(metrics['employee_growth_1y'])
                metrics['workforce_consistency'] = 5
        else:
            metrics['current_employees'] = 0
            metrics['previous_employees'] = 0
            metrics['employee_growth_1y'] = 0
            metrics['employee_cagr'] = 0
            metrics['workforce_volatility'] = 0
            metrics['workforce_consistency'] = 5
        
        # Workforce scaling assessment
        revenue_series = company_data['revenue'].dropna()
        if len(revenue_series) >= 2 and len(employee_series) >= 2:
            min_length = min(len(revenue_series), len(employee_series))
            rev_growth_rates = []
            emp_growth_rates = []
            
            for i in range(1, min_length):
                if revenue_series.iloc[i-1] > 0:
                    rev_growth = ((revenue_series.iloc[i] - revenue_series.iloc[i-1]) / revenue_series.iloc[i-1]) * 100
                    rev_growth_rates.append(rev_growth)
                
                if employee_series.iloc[i-1] > 0:
                    emp_growth = ((employee_series.iloc[i] - employee_series.iloc[i-1]) / employee_series.iloc[i-1]) * 100
                    emp_growth_rates.append(emp_growth)
            
            if rev_growth_rates and emp_growth_rates and len(rev_growth_rates) == len(emp_growth_rates):
                avg_rev_growth = np.mean(rev_growth_rates)
                avg_emp_growth = np.mean(emp_growth_rates)
                
                if avg_emp_growth != 0:
                    metrics['scaling_efficiency'] = avg_rev_growth / avg_emp_growth
                else:
                    metrics['scaling_efficiency'] = 1.0
                
                # Classify scaling strategy
                if avg_rev_growth > avg_emp_growth * 1.5:
                    metrics['scaling_strategy'] = 'Productivity-Driven'
                elif avg_emp_growth > avg_rev_growth * 1.5:
                    metrics['scaling_strategy'] = 'Expansion-Focused'
                else:
                    metrics['scaling_strategy'] = 'Balanced Growth'
            else:
                metrics['scaling_efficiency'] = 1.0
                metrics['scaling_strategy'] = 'Unknown'
        else:
            metrics['scaling_efficiency'] = 1.0
            metrics['scaling_strategy'] = 'Limited Data'
        
        # Workforce maturity assessment
        if metrics['current_employees'] > 10000:
            metrics['workforce_scale'] = 'Large Enterprise'
            metrics['scale_advantages'] = 'Economies of Scale'
        elif metrics['current_employees'] > 1000:
            metrics['workforce_scale'] = 'Mid-Size'
            metrics['scale_advantages'] = 'Operational Flexibility'
        else:
            metrics['workforce_scale'] = 'Small/Growth'
            metrics['scale_advantages'] = 'Agility Focus'
        
        # Growth phase classification
        if metrics['employee_cagr'] > 15:
            metrics['growth_phase'] = 'Rapid Expansion'
        elif metrics['employee_cagr'] > 5:
            metrics['growth_phase'] = 'Steady Growth'
        elif metrics['employee_cagr'] > -5:
            metrics['growth_phase'] = 'Stable'
        else:
            metrics['growth_phase'] = 'Contracting'
        
        workforce_trends[company_name] = metrics
    
    return workforce_trends


def _create_workforce_evolution_charts(df: pd.DataFrame, companies: Dict[str, str], 
                                      workforce_trends: Dict) -> str:
    """Create workforce evolution charts"""
    
    charts_html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    # Chart 1: Employee count evolution over time
    fig1 = go.Figure()
    
    for i, company_name in enumerate(companies.keys()):
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) >= 2:
            # Keep years and employees aligned - filter together
            valid_data = company_data[['Year', 'employeeCount']].dropna()
            
            if len(valid_data) > 0:
                years = valid_data['Year'].tolist()
                employees = valid_data['employeeCount'].tolist()
                
                fig1.add_trace(go.Scatter(
                    x=years,
                    y=employees,
                    mode='lines+markers',
                    name=company_name,
                    line=dict(width=3, color=colors[i % len(colors)]),
                    marker=dict(size=8),
                    hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Employees: %{y:,.0f}<extra></extra>'
                ))
    
    fig1.update_layout(
        title="Employee Count Evolution Over Time",
        xaxis_title="Year",
        yaxis_title="Employee Count",
        hovermode='x unified',
        height=500
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'workforce-evolution-chart', 500)
    
    # Chart 2: Employee growth rates comparison
    companies_list = list(workforce_trends.keys())
    growth_1y = [workforce_trends[c]['employee_growth_1y'] for c in companies_list]
    cagr = [workforce_trends[c]['employee_cagr'] for c in companies_list]
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=companies_list,
        y=growth_1y,
        name='1-Year Growth (%)',
        marker_color='lightblue',
        hovertemplate='<b>%{x}</b><br>1Y Growth: %{y:.1f}%<extra></extra>'
    ))
    
    fig2.add_trace(go.Bar(
        x=companies_list,
        y=cagr,
        name='CAGR (%)',
        marker_color='lightcoral',
        hovertemplate='<b>%{x}</b><br>CAGR: %{y:.1f}%<extra></extra>'
    ))
    
    fig2.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig2.update_layout(
        title="Employee Growth Rates Comparison",
        xaxis_title="Companies",
        yaxis_title="Growth Rate (%)",
        barmode='group',
        height=500
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'growth-rates-chart', 500)
    
    # Chart 3: Workforce scale distribution
    scale_counts = {}
    for trends in workforce_trends.values():
        scale = trends['workforce_scale']
        scale_counts[scale] = scale_counts.get(scale, 0) + 1
    
    fig3 = go.Figure(data=[go.Pie(
        labels=list(scale_counts.keys()),
        values=list(scale_counts.values()),
        marker=dict(colors=colors[:len(scale_counts)]),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig3.update_layout(
        title="Workforce Scale Distribution",
        height=450
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'scale-distribution-chart', 450)
    
    # Chart 4: Scaling efficiency vs growth phase
    scaling_efficiency = [workforce_trends[c]['scaling_efficiency'] for c in companies_list]
    employee_cagr = [workforce_trends[c]['employee_cagr'] for c in companies_list]
    growth_phases = [workforce_trends[c]['growth_phase'] for c in companies_list]
    
    # Color by growth phase
    phase_color_map = {
        'Rapid Expansion': '#ef4444',
        'Steady Growth': '#f59e0b', 
        'Stable': '#10b981',
        'Contracting': '#3b82f6'
    }
    
    point_colors = [phase_color_map.get(phase, '#94a3b8') for phase in growth_phases]
    
    fig4 = go.Figure()
    
    for phase in set(growth_phases):
        phase_indices = [i for i, p in enumerate(growth_phases) if p == phase]
        fig4.add_trace(go.Scatter(
            x=[scaling_efficiency[i] for i in phase_indices],
            y=[employee_cagr[i] for i in phase_indices],
            mode='markers+text',
            name=phase,
            marker=dict(size=15, color=phase_color_map.get(phase, '#94a3b8')),
            text=[companies_list[i] for i in phase_indices],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Scaling Efficiency: %{x:.2f}<br>CAGR: %{y:.1f}%<extra></extra>'
        ))
    
    fig4.update_layout(
        title="Scaling Efficiency vs Growth Profile",
        xaxis_title="Scaling Efficiency",
        yaxis_title="Employee CAGR (%)",
        height=500
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'scaling-efficiency-chart', 500)
    
    charts_html = f"""
    <div style="margin: 30px 0;">
        <h4>Workforce Evolution Visualizations</h4>
        {chart1_html}
        {chart2_html}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            {chart3_html}
            {chart4_html}
        </div>
    </div>
    """
    
    return charts_html


def _generate_workforce_trends_summary(workforce_trends: Dict, total_companies: int) -> str:
    """Generate workforce trends summary text"""
    
    total_employees = sum(m['current_employees'] for m in workforce_trends.values())
    avg_growth_1y = np.mean([m['employee_growth_1y'] for m in workforce_trends.values()])
    avg_cagr = np.mean([m['employee_cagr'] for m in workforce_trends.values()])
    rapid_growers = sum(1 for m in workforce_trends.values() if m['growth_phase'] == 'Rapid Expansion')
    productivity_driven = sum(1 for m in workforce_trends.values() if m['scaling_strategy'] == 'Productivity-Driven')
    
    summary = f"""
    <p><strong>Portfolio Workforce Scale:</strong> {total_employees:,} total employees across {total_companies} companies with {avg_growth_1y:.1f}% average 1-year growth.</p>
    
    <p><strong>Growth Trajectory:</strong> {avg_cagr:.1f}% portfolio CAGR with {rapid_growers}/{total_companies} companies in rapid expansion phase.</p>
    
    <p><strong>Scaling Strategy Distribution:</strong> {productivity_driven}/{total_companies} companies pursuing productivity-driven scaling approaches.</p>
    
    <p><strong>Workforce Maturity:</strong> {'Large enterprise focus' if sum(1 for m in workforce_trends.values() if m['workforce_scale'] == 'Large Enterprise') >= total_companies * 0.5 else 'Mid-size operational flexibility' if sum(1 for m in workforce_trends.values() if m['workforce_scale'] == 'Mid-Size') >= total_companies * 0.5 else 'Growth-stage agility'} characterizes portfolio.</p>
    
    <p><strong>Strategic Insight:</strong> {'Optimize scaling efficiency while maintaining growth momentum' if avg_cagr > 5 and productivity_driven >= total_companies * 0.4 else 'Focus on productivity-driven growth strategies' if avg_growth_1y > 0 else 'Implement workforce optimization and efficiency programs'} based on current scaling patterns.</p>
    """
    
    return summary


# =============================================================================
# SUBSECTION 6B: REVENUE PER EMPLOYEE & PRODUCTIVITY ANALYSIS
# =============================================================================

def _build_section_6b_productivity_analysis(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 6B: Revenue Per Employee & Labor Productivity Analysis"""
    
    # Analyze labor productivity
    productivity_analysis = _analyze_labor_productivity(df, companies)
    
    if not productivity_analysis:
        return build_info_box("Insufficient data for productivity analysis.", "warning")
    
    # Create KPI cards
    avg_rpe = np.mean([m['revenue_per_employee'] for m in productivity_analysis.values()])
    avg_productivity_score = np.mean([m['productivity_score'] for m in productivity_analysis.values()])
    excellent_performers = sum(1 for m in productivity_analysis.values() if m['productivity_rating'] == 'Excellent')
    high_tech = sum(1 for m in productivity_analysis.values() if m['technology_intensity'] == 'High')
    
    kpi_cards = [
        {
            "label": "Avg Revenue/Employee",
            "value": f"${avg_rpe/1000:.0f}K",
            "description": "Portfolio average",
            "type": "success" if avg_rpe > 300000 else "info"
        },
        {
            "label": "Avg Productivity Score",
            "value": f"{avg_productivity_score:.1f}/10",
            "description": "Composite metric",
            "type": "success" if avg_productivity_score >= 7 else "warning" if avg_productivity_score >= 5 else "danger"
        },
        {
            "label": "Excellent Performers",
            "value": f"{excellent_performers}/{len(companies)}",
            "description": "Top-rated companies",
            "type": "success" if excellent_performers >= len(companies) * 0.3 else "info"
        },
        {
            "label": "High-Tech Intensity",
            "value": f"{high_tech}/{len(companies)}",
            "description": "Technology-driven",
            "type": "info"
        }
    ]
    
    kpi_html = build_stat_grid(kpi_cards)
    
    # Create productivity table
    table_data = []
    for company_name, metrics in productivity_analysis.items():
        table_data.append({
            "Company": company_name,
            "Revenue/Employee": f"${metrics['revenue_per_employee']/1000:.0f}K",
            "Profit/Employee": f"${metrics['profit_per_employee']/1000:.0f}K",
            "Labor Efficiency": f"{metrics['labor_efficiency_ratio']:.2f}",
            "Productivity Score": f"{metrics['productivity_score']:.1f}/10",
            "Rank": f"{metrics['productivity_rank']}/{len(productivity_analysis)}",
            "Growth Rate": f"{metrics['productivity_growth_rate']:.1f}%",
            "Consistency": f"{metrics['productivity_consistency']:.1f}/10",
            "Tech Intensity": metrics['technology_intensity'],
            "Assets/Employee": f"${metrics['assets_per_employee']/1000:.0f}K",
            "Labor Cost %": f"{metrics['labor_cost_ratio']:.1f}",
            "Rating": metrics['productivity_rating']
        })
    
    table_df = pd.DataFrame(table_data)
    
    # Color coding for rating
    def rating_color(val):
        if val == 'Excellent':
            return 'excellent'
        elif val == 'Good':
            return 'good'
        elif val == 'Average':
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {'Rating': rating_color}
    badge_columns = ['Tech Intensity', 'Rating']
    
    table_html = build_enhanced_table(table_df, "productivity-analysis-table",
                                     color_columns=color_columns,
                                     badge_columns=badge_columns)
    
    # Create charts
    charts_html = _create_productivity_charts(productivity_analysis)
    
    # Generate summary
    summary = _generate_productivity_summary(productivity_analysis, len(companies))
    summary_html = build_info_box(summary, "info", "Labor Productivity Summary")
    
    # Build collapsible subsection
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6b')">
            <span>6B. Revenue Per Employee & Labor Productivity Analysis</span>
            <span id="subsection-6b-toggle" style="font-size: 1.2rem;">â–¼</span>
        </h3>
        <div id="subsection-6b" style="display: block;">
            <h4>Comprehensive Productivity Metrics & Efficiency Assessment</h4>
            {kpi_html}
            {table_html}
            {summary_html}
            {charts_html}
        </div>
    </div>
    """
    
    return subsection_html


def _analyze_labor_productivity(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze labor productivity and efficiency metrics"""
    
    productivity_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Core productivity metrics
        revenue = latest.get('revenue', 0)
        employees = latest.get('employeeCount', 1)
        
        metrics['revenue_per_employee'] = revenue / employees if employees > 0 else 0
        
        # Profitability per employee
        net_income = latest.get('netIncome', 0)
        operating_income = latest.get('operatingIncome', 0)
        ebitda = latest.get('ebitda', 0)
        
        metrics['profit_per_employee'] = net_income / employees if employees > 0 else 0
        metrics['operating_income_per_employee'] = operating_income / employees if employees > 0 else 0
        metrics['ebitda_per_employee'] = ebitda / employees if employees > 0 else 0
        
        # Asset productivity
        total_assets = latest.get('totalAssets', 0)
        metrics['assets_per_employee'] = total_assets / employees if employees > 0 else 0
        
        # Labor cost analysis (estimated - sector-based)
        labor_cost_ratio = 0.30  # Default 30%
        estimated_labor_costs = revenue * labor_cost_ratio
        metrics['estimated_labor_cost_per_employee'] = estimated_labor_costs / employees if employees > 0 else 0
        metrics['labor_cost_ratio'] = labor_cost_ratio * 100
        
        # Labor efficiency ratio
        if metrics['estimated_labor_cost_per_employee'] > 0:
            metrics['labor_efficiency_ratio'] = metrics['revenue_per_employee'] / metrics['estimated_labor_cost_per_employee']
        else:
            metrics['labor_efficiency_ratio'] = 0
        
        # Productivity trends
        if len(company_data) >= 3:
            revenue_series = company_data['revenue'].dropna()
            employee_series = company_data['employeeCount'].dropna()
            
            if len(revenue_series) >= 3 and len(employee_series) >= 3:
                rpe_series = []
                for i in range(min(len(revenue_series), len(employee_series))):
                    if employee_series.iloc[i] > 0:
                        rpe = revenue_series.iloc[i] / employee_series.iloc[i]
                        rpe_series.append(rpe)
                
                if len(rpe_series) >= 3:
                    recent_rpe = np.mean(rpe_series[-2:])
                    earlier_rpe = np.mean(rpe_series[:2])
                    
                    if earlier_rpe > 0:
                        productivity_growth = ((recent_rpe - earlier_rpe) / earlier_rpe) * 100
                        metrics['productivity_growth_rate'] = productivity_growth
                    else:
                        metrics['productivity_growth_rate'] = 0
                    
                    rpe_volatility = np.std(rpe_series) / np.mean(rpe_series) if np.mean(rpe_series) > 0 else 0
                    metrics['productivity_consistency'] = max(0, min(10, 10 - rpe_volatility * 10))
                else:
                    metrics['productivity_growth_rate'] = 0
                    metrics['productivity_consistency'] = 5
            else:
                metrics['productivity_growth_rate'] = 0
                metrics['productivity_consistency'] = 5
        else:
            metrics['productivity_growth_rate'] = 0
            metrics['productivity_consistency'] = 5
        
        # Productivity score (composite)
        log_rpe = np.log1p(metrics['revenue_per_employee'])
        rpe_score = min(10, max(0, log_rpe / 15 * 10))
        
        efficiency_score = min(10, max(0, metrics['labor_efficiency_ratio'] / 5 * 10))
        growth_score = min(10, max(0, (metrics['productivity_growth_rate'] + 10) / 2))
        
        metrics['productivity_score'] = (rpe_score * 0.4 + efficiency_score * 0.3 + 
                                        growth_score * 0.2 + metrics['productivity_consistency'] * 0.1)
        
        # Productivity rating
        if metrics['productivity_score'] >= 8:
            metrics['productivity_rating'] = 'Excellent'
        elif metrics['productivity_score'] >= 6:
            metrics['productivity_rating'] = 'Good'
        elif metrics['productivity_score'] >= 4:
            metrics['productivity_rating'] = 'Average'
        else:
            metrics['productivity_rating'] = 'Below Average'
        
        # Technology intensity
        if metrics['revenue_per_employee'] > 500000:
            metrics['technology_intensity'] = 'High'
        elif metrics['revenue_per_employee'] > 200000:
            metrics['technology_intensity'] = 'Medium'
        else:
            metrics['technology_intensity'] = 'Low'
        
        productivity_analysis[company_name] = metrics
    
    # Calculate rankings
    productivity_scores = [(name, metrics['productivity_score']) for name, metrics in productivity_analysis.items()]
    productivity_scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (company_name, _) in enumerate(productivity_scores):
        productivity_analysis[company_name]['productivity_rank'] = rank + 1
    
    return productivity_analysis


def _create_productivity_charts(productivity_analysis: Dict) -> str:
    """Create productivity analysis charts"""
    
    charts_html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    companies_list = list(productivity_analysis.keys())
    
    # Chart 1: Revenue per employee comparison
    rpe_values = [productivity_analysis[c]['revenue_per_employee']/1000 for c in companies_list]
    
    fig1 = go.Figure(data=[go.Bar(
        x=companies_list,
        y=rpe_values,
        marker_color=colors[:len(companies_list)],
        text=[f'${v:.0f}K' for v in rpe_values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Revenue/Employee: $%{y:.0f}K<extra></extra>'
    )])
    
    fig1.update_layout(
        title="Revenue per Employee Analysis",
        xaxis_title="Companies",
        yaxis_title="Revenue per Employee ($K)",
        height=500
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'rpe-comparison-chart', 500)
    
    # Chart 2: Productivity score vs efficiency scatter
    productivity_scores = [productivity_analysis[c]['productivity_score'] for c in companies_list]
    efficiency_ratios = [productivity_analysis[c]['labor_efficiency_ratio'] for c in companies_list]
    
    fig2 = go.Figure(data=[go.Scatter(
        x=efficiency_ratios,
        y=productivity_scores,
        mode='markers+text',
        marker=dict(size=15, color=colors[:len(companies_list)]),
        text=companies_list,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Efficiency: %{x:.2f}<br>Score: %{y:.1f}/10<extra></extra>'
    )])
    
    fig2.update_layout(
        title="Productivity vs Efficiency Matrix",
        xaxis_title="Labor Efficiency Ratio",
        yaxis_title="Productivity Score (0-10)",
        height=500
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'productivity-efficiency-chart', 500)
    
    # Chart 3: Technology intensity distribution
    tech_counts = {}
    for metrics in productivity_analysis.values():
        tech = metrics['technology_intensity']
        tech_counts[tech] = tech_counts.get(tech, 0) + 1
    
    tech_colors_map = {'High': '#10b981', 'Medium': '#f59e0b', 'Low': '#ef4444'}
    pie_colors = [tech_colors_map.get(level, '#94a3b8') for level in tech_counts.keys()]
    
    fig3 = go.Figure(data=[go.Pie(
        labels=list(tech_counts.keys()),
        values=list(tech_counts.values()),
        marker=dict(colors=pie_colors),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig3.update_layout(
        title="Technology Intensity Distribution",
        height=450
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'tech-intensity-chart', 450)
    
    # Chart 4: Performance vs growth trajectory
    growth_rates = [productivity_analysis[c]['productivity_growth_rate'] for c in companies_list]
    current_scores = [productivity_analysis[c]['productivity_score'] for c in companies_list]
    
    rating_color_map = {
        'Excellent': '#10b981',
        'Good': '#3b82f6',
        'Average': '#f59e0b',
        'Below Average': '#ef4444'
    }
    
    ratings = [productivity_analysis[c]['productivity_rating'] for c in companies_list]
    
    fig4 = go.Figure()
    
    for rating in set(ratings):
        rating_indices = [i for i, r in enumerate(ratings) if r == rating]
        fig4.add_trace(go.Scatter(
            x=[current_scores[i] for i in rating_indices],
            y=[growth_rates[i] for i in rating_indices],
            mode='markers+text',
            name=rating,
            marker=dict(size=15, color=rating_color_map.get(rating, '#94a3b8')),
            text=[companies_list[i] for i in rating_indices],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Score: %{x:.1f}/10<br>Growth: %{y:.1f}%<extra></extra>'
        ))
    
    fig4.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig4.update_layout(
        title="Performance vs Growth Trajectory",
        xaxis_title="Current Productivity Score (0-10)",
        yaxis_title="Productivity Growth Rate (%)",
        height=500
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'performance-growth-chart', 500)
    
    charts_html = f"""
    <div style="margin: 30px 0;">
        <h4>Labor Productivity Visualizations</h4>
        {chart1_html}
        {chart2_html}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            {chart3_html}
            {chart4_html}
        </div>
    </div>
    """
    
    return charts_html


def _generate_productivity_summary(productivity_analysis: Dict, total_companies: int) -> str:
    """Generate productivity analysis summary"""
    
    avg_rpe = np.mean([m['revenue_per_employee'] for m in productivity_analysis.values()])
    avg_productivity_score = np.mean([m['productivity_score'] for m in productivity_analysis.values()])
    excellent_performers = sum(1 for m in productivity_analysis.values() if m['productivity_rating'] == 'Excellent')
    high_tech = sum(1 for m in productivity_analysis.values() if m['technology_intensity'] == 'High')
    positive_growth = sum(1 for m in productivity_analysis.values() if m['productivity_growth_rate'] > 0)
    
    summary = f"""
    <p><strong>Portfolio Productivity Profile:</strong> ${avg_rpe/1000:.0f}K average revenue per employee with {avg_productivity_score:.1f}/10 productivity score.</p>
    
    <p><strong>Excellence Distribution:</strong> {excellent_performers}/{total_companies} companies ({(excellent_performers/total_companies)*100:.0f}%) achieving excellent productivity ratings.</p>
    
    <p><strong>Technology Integration:</strong> {high_tech}/{total_companies} companies with high technology intensity driving productivity gains.</p>
    
    <p><strong>Productivity Growth:</strong> {positive_growth}/{total_companies} companies demonstrating positive productivity growth trends.</p>
    
    <p><strong>Strategic Insight:</strong> {'Scale high-productivity models while enhancing technology integration' if excellent_performers >= total_companies * 0.4 and high_tech >= total_companies * 0.4 else 'Focus on productivity enhancement through technology and process optimization' if avg_productivity_score >= 5 else 'Comprehensive productivity transformation initiative required'} for workforce excellence.</p>
    """
    
    return summary


# =============================================================================
# SUBSECTION STUBS (6C-6G) - To be implemented in later phases
# =============================================================================

"""
Section 6: Workforce & Productivity Analysis
Phase 2: Subsections 6C & 6D

This file contains ONLY the new functions for Phase 2.
Replace the stub functions in the Phase 1 file with these implementations.
"""



# =============================================================================
# SUBSECTION 6C: WORKFORCE OPTIMIZATION & STRATEGIC PLANNING
# =============================================================================

def _build_section_6c_optimization(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 6C: Workforce Optimization & Strategic Planning"""
    
    # Get workforce trends and productivity analysis for optimization
    workforce_trends = _analyze_workforce_trends(df, companies, pd.DataFrame())
    productivity_analysis = _analyze_labor_productivity(df, companies)
    
    # Analyze workforce optimization
    optimization_analysis = _analyze_workforce_optimization(df, companies, workforce_trends, 
                                                           productivity_analysis)
    
    if not optimization_analysis:
        return build_info_box("Insufficient data for workforce optimization analysis.", "warning")
    
    # Create KPI cards
    avg_efficiency = np.mean([m['workforce_efficiency'] for m in optimization_analysis.values()])
    high_efficiency = sum(1 for m in optimization_analysis.values() if m['workforce_efficiency'] >= 7)
    automation_ready = sum(1 for m in optimization_analysis.values() if m['automation_score'] >= 7)
    optimal_sizing = sum(1 for m in optimization_analysis.values() if m['current_vs_optimal'] == 'Optimal Range')
    
    kpi_cards = [
        {
            "label": "Avg Workforce Efficiency",
            "value": f"{avg_efficiency:.1f}/10",
            "description": "Portfolio average",
            "type": "success" if avg_efficiency >= 7 else "warning" if avg_efficiency >= 5 else "danger"
        },
        {
            "label": "High Efficiency Companies",
            "value": f"{high_efficiency}/{len(companies)}",
            "description": "Efficiency ≥7",
            "type": "success" if high_efficiency >= len(companies) * 0.5 else "info"
        },
        {
            "label": "Automation Ready",
            "value": f"{automation_ready}/{len(companies)}",
            "description": "High automation potential",
            "type": "info"
        },
        {
            "label": "Optimal Sizing",
            "value": f"{optimal_sizing}/{len(companies)}",
            "description": "Within optimal range",
            "type": "success" if optimal_sizing >= len(companies) * 0.5 else "warning"
        }
    ]
    
    kpi_html = build_stat_grid(kpi_cards)
    
    # Create optimization table
    table_data = []
    for company_name, metrics in optimization_analysis.items():
        table_data.append({
            "Company": company_name,
            "Workforce Efficiency": f"{metrics['workforce_efficiency']:.1f}/10",
            "Scaling Factor": f"{metrics['scaling_factor']:.2f}",
            "Optimal Size Range": metrics['optimal_size_range'],
            "Current vs Optimal": metrics['current_vs_optimal'],
            "Growth Strategy": metrics['growth_strategy'],
            "Automation Score": f"{metrics['automation_score']:.1f}/10",
            "Skill Intensity": metrics['skill_intensity'],
            "Labor Cost %": f"{metrics['labor_cost_ratio']:.1f}",
            "Efficiency Rank": f"{metrics['efficiency_rank']}/{len(optimization_analysis)}",
            "Strategic Focus": metrics['strategic_focus']
        })
    
    table_df = pd.DataFrame(table_data)
    
    # Color coding
    def sizing_color(val):
        if val == 'Optimal Range':
            return 'excellent'
        elif val == 'Understaffed':
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {'Current vs Optimal': sizing_color}
    badge_columns = ['Growth Strategy', 'Skill Intensity', 'Strategic Focus']
    
    table_html = build_enhanced_table(table_df, "optimization-table",
                                     color_columns=color_columns,
                                     badge_columns=badge_columns)
    
    # Create charts
    charts_html = _create_optimization_charts(optimization_analysis)
    
    # Generate summary
    summary = _generate_optimization_summary(optimization_analysis, len(companies))
    summary_html = build_info_box(summary, "info", "Workforce Optimization Summary")
    
    # Build collapsible subsection
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6c')">
            <span>6C. Workforce Optimization & Strategic Planning</span>
            <span id="subsection-6c-toggle" style="font-size: 1.2rem;">▼</span>
        </h3>
        <div id="subsection-6c" style="display: block;">
            <h4>Strategic Workforce Planning & Optimization Framework</h4>
            {kpi_html}
            {table_html}
            {summary_html}
            {charts_html}
        </div>
    </div>
    """
    
    return subsection_html


def _analyze_workforce_optimization(df: pd.DataFrame, companies: Dict[str, str],
                                   workforce_trends: Dict, productivity_analysis: Dict) -> Dict[str, Dict]:
    """Analyze workforce optimization and strategic planning"""
    
    optimization_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Current workforce metrics
        current_employees = latest.get('employeeCount', 0)
        revenue = latest.get('revenue', 0)
        
        workforce_metrics = workforce_trends.get(company_name, {})
        productivity_metrics = productivity_analysis.get(company_name, {})
        
        # Workforce efficiency calculation
        productivity_score = productivity_metrics.get('productivity_score', 5)
        scaling_efficiency = workforce_metrics.get('scaling_efficiency', 1.0)
        consistency = workforce_metrics.get('workforce_consistency', 5)
        
        metrics['workforce_efficiency'] = (productivity_score * 0.5 + 
                                          min(10, scaling_efficiency * 2) * 0.3 + 
                                          consistency * 0.2)
        
        # Scaling factor analysis
        metrics['scaling_factor'] = scaling_efficiency
        
        # Optimal workforce size estimation
        rpe = productivity_metrics.get('revenue_per_employee', 200000)
        industry_avg_rpe = 250000  # Default industry average
        
        # Calculate optimal employee count based on industry benchmarks
        optimal_employees_low = int(revenue / (industry_avg_rpe * 1.2))
        optimal_employees_high = int(revenue / (industry_avg_rpe * 0.8))
        
        metrics['optimal_size_range'] = f"{optimal_employees_low:,}-{optimal_employees_high:,}"
        
        # Current vs optimal assessment
        if current_employees < optimal_employees_low:
            metrics['current_vs_optimal'] = 'Understaffed'
        elif current_employees > optimal_employees_high:
            metrics['current_vs_optimal'] = 'Overstaffed'
        else:
            metrics['current_vs_optimal'] = 'Optimal Range'
        
        # Growth strategy recommendation
        growth_rate = workforce_metrics.get('employee_cagr', 0)
        productivity_growth = productivity_metrics.get('productivity_growth_rate', 0)
        
        if productivity_growth > growth_rate and productivity_growth > 5:
            metrics['growth_strategy'] = 'Productivity Focus'
        elif growth_rate > 10 and productivity_growth > 0:
            metrics['growth_strategy'] = 'Balanced Expansion'
        elif growth_rate > 15:
            metrics['growth_strategy'] = 'Rapid Scaling'
        else:
            metrics['growth_strategy'] = 'Optimization Focus'
        
        # Automation potential score
        tech_intensity = productivity_metrics.get('technology_intensity', 'Low')
        base_automation_score = {'High': 8, 'Medium': 5, 'Low': 3}.get(tech_intensity, 3)
        metrics['automation_score'] = min(10, base_automation_score + 1)
        
        # Skill intensity assessment
        if rpe > 400000:
            metrics['skill_intensity'] = 'High-Skilled'
        elif rpe > 200000:
            metrics['skill_intensity'] = 'Mid-Skilled'
        else:
            metrics['skill_intensity'] = 'Mixed-Skills'
        
        # Labor cost ratio
        metrics['labor_cost_ratio'] = productivity_metrics.get('labor_cost_ratio', 25)
        
        # Strategic focus recommendation
        if metrics['automation_score'] >= 7 and metrics['current_vs_optimal'] == 'Overstaffed':
            metrics['strategic_focus'] = 'Automation & Efficiency'
        elif productivity_growth < 0 and growth_rate > 5:
            metrics['strategic_focus'] = 'Productivity Enhancement'
        elif metrics['current_vs_optimal'] == 'Understaffed' and growth_rate < 5:
            metrics['strategic_focus'] = 'Strategic Hiring'
        else:
            metrics['strategic_focus'] = 'Optimization & Growth'
        
        optimization_analysis[company_name] = metrics
    
    # Calculate efficiency rankings
    efficiency_scores = [(name, metrics['workforce_efficiency']) for name, metrics in optimization_analysis.items()]
    efficiency_scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (company_name, _) in enumerate(efficiency_scores):
        optimization_analysis[company_name]['efficiency_rank'] = rank + 1
    
    return optimization_analysis


def _create_optimization_charts(optimization_analysis: Dict) -> str:
    """Create workforce optimization charts"""
    
    charts_html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    companies_list = list(optimization_analysis.keys())
    
    # Chart 1: Workforce efficiency scores
    efficiency_scores = [optimization_analysis[c]['workforce_efficiency'] for c in companies_list]
    
    fig1 = go.Figure(data=[go.Bar(
        x=companies_list,
        y=efficiency_scores,
        marker_color=colors[:len(companies_list)],
        text=[f'{v:.1f}' for v in efficiency_scores],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Efficiency: %{y:.1f}/10<extra></extra>'
    )])
    
    fig1.add_hline(y=5, line_dash="dash", line_color="red", opacity=0.7,
                   annotation_text="Benchmark")
    
    fig1.update_layout(
        title="Workforce Efficiency Assessment",
        xaxis_title="Companies",
        yaxis_title="Workforce Efficiency Score (0-10)",
        height=500
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'efficiency-scores-chart', 500)
    
    # Chart 2: Automation potential vs current efficiency
    automation_scores = [optimization_analysis[c]['automation_score'] for c in companies_list]
    
    fig2 = go.Figure(data=[go.Scatter(
        x=efficiency_scores,
        y=automation_scores,
        mode='markers+text',
        marker=dict(size=15, color=colors[:len(companies_list)]),
        text=companies_list,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Efficiency: %{x:.1f}<br>Automation: %{y:.1f}<extra></extra>'
    )])
    
    fig2.update_layout(
        title="Efficiency vs Automation Opportunity Matrix",
        xaxis_title="Current Workforce Efficiency (0-10)",
        yaxis_title="Automation Potential (0-10)",
        height=500
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'automation-matrix-chart', 500)
    
    # Chart 3: Strategic focus distribution
    focus_counts = {}
    for metrics in optimization_analysis.values():
        focus = metrics['strategic_focus']
        focus_counts[focus] = focus_counts.get(focus, 0) + 1
    
    fig3 = go.Figure(data=[go.Pie(
        labels=list(focus_counts.keys()),
        values=list(focus_counts.values()),
        marker=dict(colors=colors[:len(focus_counts)]),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig3.update_layout(
        title="Strategic Focus Distribution",
        height=450
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'strategic-focus-chart', 450)
    
    # Chart 4: Workforce sizing analysis
    sizing_counts = {}
    for metrics in optimization_analysis.values():
        sizing = metrics['current_vs_optimal']
        sizing_counts[sizing] = sizing_counts.get(sizing, 0) + 1
    
    sizing_colors_map = {
        'Optimal Range': '#10b981',
        'Understaffed': '#f59e0b',
        'Overstaffed': '#ef4444'
    }
    
    fig4 = go.Figure(data=[go.Bar(
        y=list(sizing_counts.keys()),
        x=list(sizing_counts.values()),
        orientation='h',
        marker_color=[sizing_colors_map.get(k, '#94a3b8') for k in sizing_counts.keys()],
        text=list(sizing_counts.values()),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Companies: %{x}<extra></extra>'
    )])
    
    fig4.update_layout(
        title="Workforce Sizing Optimization",
        xaxis_title="Number of Companies",
        yaxis_title="Workforce Sizing Assessment",
        height=450
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'sizing-optimization-chart', 450)
    
    charts_html = f"""
    <div style="margin: 30px 0;">
        <h4>Workforce Optimization Visualizations</h4>
        {chart1_html}
        {chart2_html}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            {chart3_html}
            {chart4_html}
        </div>
    </div>
    """
    
    return charts_html


def _generate_optimization_summary(optimization_analysis: Dict, total_companies: int) -> str:
    """Generate workforce optimization summary"""
    
    avg_efficiency = np.mean([m['workforce_efficiency'] for m in optimization_analysis.values()])
    high_efficiency = sum(1 for m in optimization_analysis.values() if m['workforce_efficiency'] >= 7)
    automation_ready = sum(1 for m in optimization_analysis.values() if m['automation_score'] >= 7)
    optimization_needed = sum(1 for m in optimization_analysis.values() 
                             if m['current_vs_optimal'] in ['Overstaffed', 'Understaffed'])
    
    summary = f"""
    <p><strong>Portfolio Efficiency Profile:</strong> {avg_efficiency:.1f}/10 workforce efficiency with {high_efficiency}/{total_companies} companies achieving high efficiency ratings.</p>
    
    <p><strong>Sizing Optimization:</strong> {optimization_needed}/{total_companies} companies with workforce sizing optimization opportunities.</p>
    
    <p><strong>Automation Readiness:</strong> {automation_ready}/{total_companies} companies well-positioned for automation initiatives.</p>
    
    <p><strong>Scaling Efficiency:</strong> {'Highly efficient' if np.mean([m['scaling_factor'] for m in optimization_analysis.values()]) > 1.5 else 'Moderately efficient' if np.mean([m['scaling_factor'] for m in optimization_analysis.values()]) > 1.0 else 'Efficiency enhancement needed'} revenue-to-workforce scaling.</p>
    
    <p><strong>Strategic Priority:</strong> {'Accelerate automation while maintaining strategic growth' if automation_ready >= total_companies * 0.4 and avg_efficiency >= 7 else 'Focus on workforce efficiency and optimization initiatives' if avg_efficiency >= 5 else 'Comprehensive workforce transformation and optimization program required'} for enhanced productivity.</p>
    """
    
    return summary


# =============================================================================
# SUBSECTION 6D: HUMAN CAPITAL ROI & TALENT INVESTMENT
# =============================================================================

def _build_section_6d_human_capital_roi(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 6D: Human Capital ROI & Talent Investment Analysis"""
    
    # Get prerequisites
    workforce_trends = _analyze_workforce_trends(df, companies, pd.DataFrame())
    productivity_analysis = _analyze_labor_productivity(df, companies)
    
    # Analyze human capital ROI
    human_capital_analysis = _analyze_human_capital_roi(df, companies, workforce_trends, 
                                                       productivity_analysis)
    
    if not human_capital_analysis:
        return build_info_box("Insufficient data for human capital ROI analysis.", "warning")
    
    # Create KPI cards
    total_hc_investment = sum(m['hc_investment'] for m in human_capital_analysis.values())
    avg_hc_roi = np.mean([m['hc_roi'] for m in human_capital_analysis.values()])
    avg_talent_quality = np.mean([m['talent_quality_score'] for m in human_capital_analysis.values()])
    excellent_hc = sum(1 for m in human_capital_analysis.values() if m['hc_rating'] == 'Excellent')
    
    kpi_cards = [
        {
            "label": "Total HC Investment",
            "value": f"${total_hc_investment/1000000:.0f}M",
            "description": "Portfolio investment",
            "type": "info"
        },
        {
            "label": "Average HC ROI",
            "value": f"{avg_hc_roi:.1f}%",
            "description": "Return on investment",
            "type": "success" if avg_hc_roi > 150 else "warning" if avg_hc_roi > 100 else "danger"
        },
        {
            "label": "Avg Talent Quality",
            "value": f"{avg_talent_quality:.1f}/10",
            "description": "Portfolio score",
            "type": "success" if avg_talent_quality >= 7 else "info"
        },
        {
            "label": "Excellent HC Management",
            "value": f"{excellent_hc}/{len(companies)}",
            "description": "Top-rated companies",
            "type": "success" if excellent_hc >= len(companies) * 0.3 else "info"
        }
    ]
    
    kpi_html = build_stat_grid(kpi_cards)
    
    # Create human capital table
    table_data = []
    for company_name, metrics in human_capital_analysis.items():
        table_data.append({
            "Company": company_name,
            "HC Investment": f"${metrics['hc_investment']/1000000:.0f}M",
            "HC ROI": f"{metrics['hc_roi']:.1f}%",
            "Talent Quality": f"{metrics['talent_quality_score']:.1f}/10",
            "Investment Efficiency": f"{metrics['investment_efficiency']:.1f}/10",
            "Productivity Growth": f"{metrics['productivity_growth']:.1f}%",
            "Skill Premium": f"{metrics['skill_premium']:.1f}%",
            "Retention Quality": f"{metrics['retention_quality']:.1f}/10",
            "Development ROI": f"{metrics['development_roi']:.1f}%",
            "HC Rating": metrics['hc_rating']
        })
    
    table_df = pd.DataFrame(table_data)
    
    # Color coding
    def rating_color(val):
        if val == 'Excellent':
            return 'excellent'
        elif val == 'Good':
            return 'good'
        elif val == 'Average':
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {'HC Rating': rating_color}
    badge_columns = ['HC Rating']
    
    table_html = build_enhanced_table(table_df, "human-capital-table",
                                     color_columns=color_columns,
                                     badge_columns=badge_columns)
    
    # Create charts
    charts_html = _create_human_capital_charts(human_capital_analysis)
    
    # Generate summary
    summary = _generate_human_capital_summary(human_capital_analysis, len(companies))
    summary_html = build_info_box(summary, "info", "Human Capital ROI Summary")
    
    # Build collapsible subsection
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6d')">
            <span>6D. Human Capital ROI & Talent Investment Analysis</span>
            <span id="subsection-6d-toggle" style="font-size: 1.2rem;">▼</span>
        </h3>
        <div id="subsection-6d" style="display: block;">
            <h4>Human Capital Return on Investment Assessment</h4>
            {kpi_html}
            {table_html}
            {summary_html}
            {charts_html}
        </div>
    </div>
    """
    
    return subsection_html


def _analyze_human_capital_roi(df: pd.DataFrame, companies: Dict[str, str],
                              workforce_trends: Dict, productivity_analysis: Dict) -> Dict[str, Dict]:
    """Analyze human capital ROI and talent investment effectiveness"""
    
    human_capital_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if company_data.empty:
            continue
        
        latest = company_data.iloc[-1]
        metrics = {}
        
        # Human capital investment estimation
        revenue = latest.get('revenue', 0)
        employees = latest.get('employeeCount', 1)
        
        productivity_metrics = productivity_analysis.get(company_name, {})
        workforce_metrics = workforce_trends.get(company_name, {})
        
        # Estimate human capital investment
        labor_cost_ratio = productivity_metrics.get('labor_cost_ratio', 25) / 100
        base_labor_costs = revenue * labor_cost_ratio
        
        # Additional HC investments (training, development, benefits - 20%)
        additional_hc_ratio = 0.20
        total_hc_investment = base_labor_costs * (1 + additional_hc_ratio)
        
        metrics['hc_investment'] = total_hc_investment
        metrics['hc_investment_per_employee'] = total_hc_investment / employees if employees > 0 else 0
        
        # Human capital ROI calculation
        if total_hc_investment > 0:
            hc_roi = ((revenue - total_hc_investment) / total_hc_investment) * 100
            metrics['hc_roi'] = hc_roi
        else:
            metrics['hc_roi'] = 0
        
        # Talent quality assessment
        rpe = productivity_metrics.get('revenue_per_employee', 200000)
        industry_avg_rpe = 250000
        
        if rpe > industry_avg_rpe * 1.5:
            talent_quality = 9
        elif rpe > industry_avg_rpe * 1.2:
            talent_quality = 7
        elif rpe > industry_avg_rpe:
            talent_quality = 6
        elif rpe > industry_avg_rpe * 0.8:
            talent_quality = 4
        else:
            talent_quality = 2
        
        metrics['talent_quality_score'] = talent_quality
        
        # Investment efficiency
        cost_per_employee = metrics['hc_investment_per_employee']
        
        if cost_per_employee > 0:
            efficiency_ratio = rpe / cost_per_employee
            if efficiency_ratio > 3:
                investment_efficiency = 9
            elif efficiency_ratio > 2.5:
                investment_efficiency = 7
            elif efficiency_ratio > 2:
                investment_efficiency = 6
            elif efficiency_ratio > 1.5:
                investment_efficiency = 4
            else:
                investment_efficiency = 2
        else:
            investment_efficiency = 5
        
        metrics['investment_efficiency'] = investment_efficiency
        
        # Productivity growth impact
        productivity_growth = productivity_metrics.get('productivity_growth_rate', 0)
        metrics['productivity_growth'] = productivity_growth
        
        # Skill premium calculation
        if industry_avg_rpe > 0:
            skill_premium = ((rpe - industry_avg_rpe) / industry_avg_rpe) * 100
            metrics['skill_premium'] = max(-50, min(200, skill_premium))
        else:
            metrics['skill_premium'] = 0
        
        # Retention quality (estimated)
        workforce_consistency = workforce_metrics.get('workforce_consistency', 5)
        scaling_strategy = workforce_metrics.get('scaling_strategy', 'Unknown')
        
        if scaling_strategy == 'Productivity-Driven' and workforce_consistency >= 7:
            retention_quality = 8
        elif workforce_consistency >= 6:
            retention_quality = 6
        elif workforce_consistency >= 4:
            retention_quality = 4
        else:
            retention_quality = 2
        
        metrics['retention_quality'] = retention_quality
        
        # Development ROI (estimated)
        development_investment = total_hc_investment * 0.10
        
        if development_investment > 0 and productivity_growth > 0:
            productivity_revenue_impact = revenue * (productivity_growth / 100)
            development_roi = (productivity_revenue_impact / development_investment) * 100
            metrics['development_roi'] = min(500, max(-100, development_roi))
        else:
            metrics['development_roi'] = 0
        
        # Overall HC rating
        hc_score_components = [
            metrics['talent_quality_score'],
            metrics['investment_efficiency'],
            metrics['retention_quality'],
            min(10, max(0, (metrics['hc_roi'] + 100) / 20))
        ]
        
        overall_hc_score = np.mean(hc_score_components)
        
        if overall_hc_score >= 8:
            metrics['hc_rating'] = 'Excellent'
        elif overall_hc_score >= 6:
            metrics['hc_rating'] = 'Good'
        elif overall_hc_score >= 4:
            metrics['hc_rating'] = 'Average'
        else:
            metrics['hc_rating'] = 'Below Average'
        
        human_capital_analysis[company_name] = metrics
    
    return human_capital_analysis


def _create_human_capital_charts(human_capital_analysis: Dict) -> str:
    """Create human capital ROI charts"""
    
    charts_html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    companies_list = list(human_capital_analysis.keys())
    
    # Chart 1: Human Capital ROI comparison
    hc_roi_values = [human_capital_analysis[c]['hc_roi'] for c in companies_list]
    
    # Color bars based on ROI performance
    bar_colors = ['#10b981' if roi > 150 else '#3b82f6' if roi > 100 else '#f59e0b' if roi > 50 else '#ef4444' 
                  for roi in hc_roi_values]
    
    fig1 = go.Figure(data=[go.Bar(
        x=companies_list,
        y=hc_roi_values,
        marker_color=bar_colors,
        text=[f'{v:.0f}%' for v in hc_roi_values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>HC ROI: %{y:.1f}%<extra></extra>'
    )])
    
    fig1.add_hline(y=100, line_dash="dash", line_color="black", opacity=0.7,
                   annotation_text="100% ROI Benchmark")
    
    fig1.update_layout(
        title="Human Capital Return on Investment",
        xaxis_title="Companies",
        yaxis_title="Human Capital ROI (%)",
        height=500
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'hc-roi-chart', 500)
    
    # Chart 2: Investment vs Quality scatter
    hc_investment = [human_capital_analysis[c]['hc_investment']/1000000 for c in companies_list]
    talent_quality = [human_capital_analysis[c]['talent_quality_score'] for c in companies_list]
    
    fig2 = go.Figure(data=[go.Scatter(
        x=hc_investment,
        y=talent_quality,
        mode='markers+text',
        marker=dict(size=15, color=colors[:len(companies_list)]),
        text=companies_list,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Investment: $%{x:.0f}M<br>Quality: %{y:.1f}/10<extra></extra>'
    )])
    
    fig2.update_layout(
        title="Investment vs Talent Quality",
        xaxis_title="HC Investment ($M)",
        yaxis_title="Talent Quality Score (0-10)",
        height=500
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'investment-quality-chart', 500)
    
    # Chart 3: Investment efficiency vs Development ROI
    investment_efficiency = [human_capital_analysis[c]['investment_efficiency'] for c in companies_list]
    development_roi = [human_capital_analysis[c]['development_roi'] for c in companies_list]
    
    fig3 = go.Figure(data=[go.Scatter(
        x=investment_efficiency,
        y=development_roi,
        mode='markers+text',
        marker=dict(size=15, color=colors[:len(companies_list)]),
        text=companies_list,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Efficiency: %{x:.1f}/10<br>Dev ROI: %{y:.1f}%<extra></extra>'
    )])
    
    fig3.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig3.update_layout(
        title="Investment Efficiency vs Development Returns",
        xaxis_title="Investment Efficiency (0-10)",
        yaxis_title="Development ROI (%)",
        height=450
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'efficiency-dev-roi-chart', 450)
    
    # Chart 4: HC Rating distribution
    rating_counts = {}
    for metrics in human_capital_analysis.values():
        rating = metrics['hc_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    rating_colors_map = {
        'Excellent': '#10b981',
        'Good': '#3b82f6',
        'Average': '#f59e0b',
        'Below Average': '#ef4444'
    }
    
    pie_colors = [rating_colors_map.get(rating, '#94a3b8') for rating in rating_counts.keys()]
    
    fig4 = go.Figure(data=[go.Pie(
        labels=list(rating_counts.keys()),
        values=list(rating_counts.values()),
        marker=dict(colors=pie_colors),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig4.update_layout(
        title="Human Capital Rating Distribution",
        height=450
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'hc-rating-chart', 450)
    
    charts_html = f"""
    <div style="margin: 30px 0;">
        <h4>Human Capital ROI Visualizations</h4>
        {chart1_html}
        {chart2_html}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            {chart3_html}
            {chart4_html}
        </div>
    </div>
    """
    
    return charts_html


def _generate_human_capital_summary(human_capital_analysis: Dict, total_companies: int) -> str:
    """Generate human capital ROI summary"""
    
    total_hc_investment = sum(m['hc_investment'] for m in human_capital_analysis.values())
    avg_hc_roi = np.mean([m['hc_roi'] for m in human_capital_analysis.values()])
    avg_talent_quality = np.mean([m['talent_quality_score'] for m in human_capital_analysis.values()])
    excellent_hc = sum(1 for m in human_capital_analysis.values() if m['hc_rating'] == 'Excellent')
    high_efficiency = sum(1 for m in human_capital_analysis.values() if m['investment_efficiency'] >= 7)
    
    summary = f"""
    <p><strong>Portfolio HC Investment:</strong> ${total_hc_investment/1000000:.0f}M total human capital investment with {avg_hc_roi:.1f}% average ROI.</p>
    
    <p><strong>Talent Quality Excellence:</strong> {avg_talent_quality:.1f}/10 portfolio talent quality score with {excellent_hc}/{total_companies} companies rated as excellent.</p>
    
    <p><strong>Investment Efficiency:</strong> {high_efficiency}/{total_companies} companies achieving high HC investment efficiency (7+ score).</p>
    
    <p><strong>ROI Performance:</strong> {'Exceptional value creation' if avg_hc_roi > 200 else 'Strong ROI generation' if avg_hc_roi > 100 else 'Moderate returns' if avg_hc_roi > 50 else 'ROI enhancement needed'} from human capital investments.</p>
    
    <p><strong>Strategic Insight:</strong> {'Scale successful talent models while optimizing investment efficiency' if excellent_hc >= total_companies * 0.4 and avg_hc_roi > 100 else 'Enhance talent quality and development ROI' if avg_talent_quality >= 6 else 'Comprehensive human capital transformation and investment optimization required'} for sustained competitive advantage.</p>
    """
    
    return summary

"""
Section 6: Workforce & Productivity Analysis
Phase 3: Subsections 6E & 6F

This file contains ONLY the new functions for Phase 3.
Replace the stub functions in the previous phases with these implementations.
"""

# =============================================================================
# SUBSECTION 6E: COMPARATIVE WORKFORCE ANALYSIS & INDUSTRY BENCHMARKING
# =============================================================================

def _build_section_6e_comparative_analysis(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 6E: Comparative Workforce Analysis & Industry Benchmarking"""
    
    # Get all prerequisite analyses
    workforce_trends = _analyze_workforce_trends(df, companies, pd.DataFrame())
    productivity_analysis = _analyze_labor_productivity(df, companies)
    optimization_analysis = _analyze_workforce_optimization(df, companies, workforce_trends, 
                                                           productivity_analysis)
    human_capital_analysis = _analyze_human_capital_roi(df, companies, workforce_trends, 
                                                       productivity_analysis)
    
    # Analyze comparative workforce
    comparative_analysis = _analyze_comparative_workforce(df, companies, workforce_trends,
                                                         productivity_analysis, optimization_analysis,
                                                         human_capital_analysis)
    
    if not comparative_analysis:
        return build_info_box("Insufficient data for comparative workforce analysis.", "warning")
    
    # Create KPI cards
    avg_workforce_score = np.mean([m['workforce_score'] for m in comparative_analysis.values()])
    industry_leaders = sum(1 for m in comparative_analysis.values() if m['competitive_position'] == 'Industry Leader')
    best_in_class = sum(1 for m in comparative_analysis.values() if m['benchmark_status'] == 'Best-in-Class')
    avg_percentile = np.mean([m['industry_percentile'] for m in comparative_analysis.values()])
    
    kpi_cards = [
        {
            "label": "Avg Workforce Score",
            "value": f"{avg_workforce_score:.1f}/10",
            "description": "Portfolio average",
            "type": "success" if avg_workforce_score >= 7 else "warning" if avg_workforce_score >= 5 else "danger"
        },
        {
            "label": "Industry Leaders",
            "value": f"{industry_leaders}/{len(companies)}",
            "description": "Leading position",
            "type": "success" if industry_leaders >= len(companies) * 0.3 else "info"
        },
        {
            "label": "Best-in-Class",
            "value": f"{best_in_class}/{len(companies)}",
            "description": "Top performers",
            "type": "success" if best_in_class >= len(companies) * 0.3 else "info"
        },
        {
            "label": "Avg Industry Percentile",
            "value": f"{avg_percentile:.0f}th",
            "description": "Portfolio positioning",
            "type": "success" if avg_percentile >= 75 else "info" if avg_percentile >= 50 else "warning"
        }
    ]
    
    kpi_html = build_stat_grid(kpi_cards)
    
    # Create comparative analysis table
    table_data = []
    for company_name, metrics in comparative_analysis.items():
        table_data.append({
            "Company": company_name,
            "Workforce Score": f"{metrics['workforce_score']:.1f}/10",
            "Industry Percentile": f"{metrics['industry_percentile']:.0f}th",
            "Productivity Rank": f"{metrics['productivity_rank']}/{len(comparative_analysis)}",
            "Efficiency Rank": f"{metrics['efficiency_rank']}/{len(comparative_analysis)}",
            "ROI Rank": f"{metrics['roi_rank']}/{len(comparative_analysis)}",
            "Best Practice": metrics['best_practice_area'],
            "Improvement Area": metrics['improvement_area'],
            "Competitive Position": metrics['competitive_position'],
            "Benchmark Status": metrics['benchmark_status'],
            "Strategic Priority": metrics['strategic_priority'],
            "Overall Rating": metrics['overall_rating']
        })
    
    table_df = pd.DataFrame(table_data)
    
    # Color coding
    def position_color(val):
        if val == 'Industry Leader':
            return 'excellent'
        elif val == 'Above Average':
            return 'good'
        elif val == 'Industry Average':
            return 'fair'
        else:
            return 'poor'
    
    def rating_color(val):
        if val == 'Excellent':
            return 'excellent'
        elif val == 'Good':
            return 'good'
        elif val == 'Average':
            return 'fair'
        else:
            return 'poor'
    
    color_columns = {
        'Competitive Position': position_color,
        'Overall Rating': rating_color
    }
    badge_columns = ['Best Practice', 'Benchmark Status', 'Strategic Priority']
    
    table_html = build_enhanced_table(table_df, "comparative-analysis-table",
                                     color_columns=color_columns,
                                     badge_columns=badge_columns)
    
    # Create charts
    charts_html = _create_comparative_charts(comparative_analysis)
    
    # Generate summary
    summary = _generate_comparative_summary(comparative_analysis, len(companies))
    summary_html = build_info_box(summary, "info", "Comparative Analysis Summary")
    
    # Build collapsible subsection
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6e')">
            <span>6E. Comparative Workforce Analysis & Industry Benchmarking</span>
            <span id="subsection-6e-toggle" style="font-size: 1.2rem;">▼</span>
        </h3>
        <div id="subsection-6e" style="display: block;">
            <h4>Cross-Company Workforce Performance & Industry Comparison</h4>
            {kpi_html}
            {table_html}
            {summary_html}
            {charts_html}
        </div>
    </div>
    """
    
    return subsection_html


def _analyze_comparative_workforce(df: pd.DataFrame, companies: Dict[str, str],
                                  workforce_trends: Dict, productivity_analysis: Dict,
                                  optimization_analysis: Dict, human_capital_analysis: Dict) -> Dict[str, Dict]:
    """Analyze comparative workforce performance and industry benchmarking"""
    
    comparative_analysis = {}
    
    # Calculate portfolio benchmarks
    all_productivity_scores = [m['productivity_score'] for m in productivity_analysis.values()]
    all_efficiency_scores = [m['workforce_efficiency'] for m in optimization_analysis.values()]
    all_hc_roi = [m['hc_roi'] for m in human_capital_analysis.values()]
    
    for company_name in companies.keys():
        metrics = {}
        
        workforce_metrics = workforce_trends.get(company_name, {})
        productivity_metrics = productivity_analysis.get(company_name, {})
        optimization_metrics = optimization_analysis.get(company_name, {})
        hc_metrics = human_capital_analysis.get(company_name, {})
        
        # Comprehensive workforce score
        score_components = [
            productivity_metrics.get('productivity_score', 5),
            optimization_metrics.get('workforce_efficiency', 5),
            hc_metrics.get('talent_quality_score', 5),
            hc_metrics.get('investment_efficiency', 5)
        ]
        
        metrics['workforce_score'] = np.mean(score_components)
        
        # Industry percentile calculation
        company_rpe = productivity_metrics.get('revenue_per_employee', 200000)
        industry_rpe = 250000  # Default industry average
        
        if company_rpe >= industry_rpe * 1.5:
            metrics['industry_percentile'] = 90
        elif company_rpe >= industry_rpe * 1.25:
            metrics['industry_percentile'] = 75
        elif company_rpe >= industry_rpe * 1.1:
            metrics['industry_percentile'] = 60
        elif company_rpe >= industry_rpe * 0.9:
            metrics['industry_percentile'] = 40
        elif company_rpe >= industry_rpe * 0.75:
            metrics['industry_percentile'] = 25
        else:
            metrics['industry_percentile'] = 10
        
        # Rankings within portfolio
        metrics['productivity_rank'] = productivity_metrics.get('productivity_rank', len(companies))
        metrics['efficiency_rank'] = optimization_metrics.get('efficiency_rank', len(companies))
        
        # HC ROI ranking
        hc_roi_rank = sorted(all_hc_roi, reverse=True).index(hc_metrics.get('hc_roi', 0)) + 1
        metrics['roi_rank'] = hc_roi_rank
        
        # Best practice identification
        top_quartile_productivity = metrics['productivity_rank'] <= len(companies) * 0.25
        top_quartile_efficiency = metrics['efficiency_rank'] <= len(companies) * 0.25
        top_quartile_hc = metrics['roi_rank'] <= len(companies) * 0.25
        
        if top_quartile_productivity and top_quartile_efficiency:
            metrics['best_practice_area'] = 'Productivity & Efficiency'
        elif top_quartile_productivity:
            metrics['best_practice_area'] = 'Labor Productivity'
        elif top_quartile_efficiency:
            metrics['best_practice_area'] = 'Workforce Efficiency'
        elif top_quartile_hc:
            metrics['best_practice_area'] = 'Human Capital ROI'
        else:
            metrics['best_practice_area'] = 'Operational Foundation'
        
        # Improvement area identification
        bottom_quartile_productivity = metrics['productivity_rank'] > len(companies) * 0.75
        bottom_quartile_efficiency = metrics['efficiency_rank'] > len(companies) * 0.75
        bottom_quartile_hc = metrics['roi_rank'] > len(companies) * 0.75
        
        if bottom_quartile_productivity and bottom_quartile_efficiency:
            metrics['improvement_area'] = 'Comprehensive Optimization'
        elif bottom_quartile_productivity:
            metrics['improvement_area'] = 'Productivity Enhancement'
        elif bottom_quartile_efficiency:
            metrics['improvement_area'] = 'Efficiency Improvement'
        elif bottom_quartile_hc:
            metrics['improvement_area'] = 'HC Investment Optimization'
        else:
            metrics['improvement_area'] = 'Fine-tuning Excellence'
        
        # Competitive position
        if metrics['industry_percentile'] >= 75:
            metrics['competitive_position'] = 'Industry Leader'
        elif metrics['industry_percentile'] >= 50:
            metrics['competitive_position'] = 'Above Average'
        elif metrics['industry_percentile'] >= 25:
            metrics['competitive_position'] = 'Industry Average'
        else:
            metrics['competitive_position'] = 'Below Average'
        
        # Benchmark status
        if metrics['workforce_score'] >= 8:
            metrics['benchmark_status'] = 'Best-in-Class'
        elif metrics['workforce_score'] >= 6:
            metrics['benchmark_status'] = 'Strong Performer'
        elif metrics['workforce_score'] >= 4:
            metrics['benchmark_status'] = 'Average Performer'
        else:
            metrics['benchmark_status'] = 'Improvement Needed'
        
        # Strategic priority
        if metrics['competitive_position'] == 'Industry Leader' and metrics['benchmark_status'] == 'Best-in-Class':
            metrics['strategic_priority'] = 'Maintain Excellence'
        elif metrics['industry_percentile'] >= 50 and metrics['workforce_score'] >= 6:
            metrics['strategic_priority'] = 'Enhance Leadership'
        elif metrics['workforce_score'] >= 4:
            metrics['strategic_priority'] = 'Accelerate Improvement'
        else:
            metrics['strategic_priority'] = 'Transformation Required'
        
        # Overall rating
        if metrics['workforce_score'] >= 8 and metrics['industry_percentile'] >= 75:
            metrics['overall_rating'] = 'Excellent'
        elif metrics['workforce_score'] >= 6 and metrics['industry_percentile'] >= 50:
            metrics['overall_rating'] = 'Good'
        elif metrics['workforce_score'] >= 4:
            metrics['overall_rating'] = 'Average'
        else:
            metrics['overall_rating'] = 'Below Average'
        
        comparative_analysis[company_name] = metrics
    
    return comparative_analysis


def _create_comparative_charts(comparative_analysis: Dict) -> str:
    """Create comparative workforce analysis charts"""
    
    charts_html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    companies_list = list(comparative_analysis.keys())
    
    # Chart 1: Industry position vs workforce excellence
    percentiles = [comparative_analysis[c]['industry_percentile'] for c in companies_list]
    workforce_scores = [comparative_analysis[c]['workforce_score'] for c in companies_list]
    
    fig1 = go.Figure(data=[go.Scatter(
        x=percentiles,
        y=workforce_scores,
        mode='markers+text',
        marker=dict(size=15, color=colors[:len(companies_list)]),
        text=companies_list,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Percentile: %{x:.0f}th<br>Score: %{y:.1f}/10<extra></extra>'
    )])
    
    fig1.add_hline(y=6, line_dash="dash", line_color="green", opacity=0.7,
                   annotation_text="Excellence Threshold")
    fig1.add_vline(x=50, line_dash="dash", line_color="blue", opacity=0.7,
                   annotation_text="Industry Median")
    
    fig1.update_layout(
        title="Industry Position vs Workforce Excellence",
        xaxis_title="Industry Percentile",
        yaxis_title="Workforce Score (0-10)",
        height=500
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'industry-position-chart', 500)
    
    # Chart 2: Competitive position distribution
    position_counts = {}
    for metrics in comparative_analysis.values():
        position = metrics['competitive_position']
        position_counts[position] = position_counts.get(position, 0) + 1
    
    position_colors_map = {
        'Industry Leader': '#10b981',
        'Above Average': '#3b82f6',
        'Industry Average': '#f59e0b',
        'Below Average': '#ef4444'
    }
    
    bar_colors = [position_colors_map.get(pos, '#94a3b8') for pos in position_counts.keys()]
    
    fig2 = go.Figure(data=[go.Bar(
        x=list(position_counts.keys()),
        y=list(position_counts.values()),
        marker_color=bar_colors,
        text=list(position_counts.values()),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Companies: %{y}<extra></extra>'
    )])
    
    fig2.update_layout(
        title="Competitive Position Distribution",
        xaxis_title="Competitive Position",
        yaxis_title="Number of Companies",
        height=500
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'competitive-position-chart', 500)
    
    # Chart 3: Best practice area distribution
    best_practices = [comparative_analysis[c]['best_practice_area'] for c in companies_list]
    
    bp_counts = {}
    for bp in best_practices:
        bp_counts[bp] = bp_counts.get(bp, 0) + 1
    
    fig3 = go.Figure(data=[go.Pie(
        labels=list(bp_counts.keys()),
        values=list(bp_counts.values()),
        marker=dict(colors=colors[:len(bp_counts)]),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig3.update_layout(
        title="Best Practice Area Distribution",
        height=450
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'best-practice-chart', 450)
    
    # Chart 4: Strategic priority distribution
    priority_counts = {}
    for metrics in comparative_analysis.values():
        priority = metrics['strategic_priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    fig4 = go.Figure(data=[go.Bar(
        y=list(priority_counts.keys()),
        x=list(priority_counts.values()),
        orientation='h',
        marker_color=colors[:len(priority_counts)],
        text=list(priority_counts.values()),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Companies: %{x}<extra></extra>'
    )])
    
    fig4.update_layout(
        title="Strategic Priority Distribution",
        xaxis_title="Number of Companies",
        yaxis_title="Strategic Priority",
        height=450
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'strategic-priority-chart', 450)
    
    charts_html = f"""
    <div style="margin: 30px 0;">
        <h4>Comparative Workforce Analysis Visualizations</h4>
        {chart1_html}
        {chart2_html}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            {chart3_html}
            {chart4_html}
        </div>
    </div>
    """
    
    return charts_html


def _generate_comparative_summary(comparative_analysis: Dict, total_companies: int) -> str:
    """Generate comparative workforce analysis summary"""
    
    avg_workforce_score = np.mean([m['workforce_score'] for m in comparative_analysis.values()])
    industry_leaders = sum(1 for m in comparative_analysis.values() if m['competitive_position'] == 'Industry Leader')
    best_in_class = sum(1 for m in comparative_analysis.values() if m['benchmark_status'] == 'Best-in-Class')
    avg_percentile = np.mean([m['industry_percentile'] for m in comparative_analysis.values()])
    
    summary = f"""
    <p><strong>Portfolio Benchmark Performance:</strong> {avg_workforce_score:.1f}/10 workforce score with {avg_percentile:.0f}th percentile industry positioning.</p>
    
    <p><strong>Industry Leadership:</strong> {industry_leaders}/{total_companies} companies positioned as industry leaders in workforce excellence.</p>
    
    <p><strong>Best-in-Class Achievement:</strong> {best_in_class}/{total_companies} companies achieving best-in-class workforce performance.</p>
    
    <p><strong>Competitive Advantage:</strong> {'Strong competitive positioning' if industry_leaders >= total_companies * 0.4 else 'Developing competitive advantage' if avg_percentile >= 60 else 'Building competitive foundation'} across portfolio.</p>
    
    <p><strong>Strategic Insight:</strong> {'Leverage best practices while scaling excellence across portfolio' if best_in_class >= total_companies * 0.3 and industry_leaders >= total_companies * 0.3 else 'Implement targeted improvement programs with best practice sharing' if avg_workforce_score >= 6 else 'Comprehensive benchmarking and capability development program required'} for sustained workforce leadership.</p>
    """
    
    return summary


# =============================================================================
# SUBSECTION 6F: COMPREHENSIVE VISUALIZATION SUITE
# =============================================================================

def _build_section_6f_visualizations(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 6F: Comprehensive Visualization Suite"""
    
    # Get all analyses
    workforce_trends = _analyze_workforce_trends(df, companies, pd.DataFrame())
    productivity_analysis = _analyze_labor_productivity(df, companies)
    optimization_analysis = _analyze_workforce_optimization(df, companies, workforce_trends, 
                                                           productivity_analysis)
    human_capital_analysis = _analyze_human_capital_roi(df, companies, workforce_trends, 
                                                       productivity_analysis)
    comparative_analysis = _analyze_comparative_workforce(df, companies, workforce_trends,
                                                         productivity_analysis, optimization_analysis,
                                                         human_capital_analysis)
    
    if not all([workforce_trends, productivity_analysis, optimization_analysis, 
                human_capital_analysis, comparative_analysis]):
        return build_info_box("Insufficient data for comprehensive visualizations.", "warning")
    
    # Create comprehensive dashboard
    dashboard_html = _create_comprehensive_workforce_dashboard(
        workforce_trends, productivity_analysis, optimization_analysis,
        human_capital_analysis, comparative_analysis, companies
    )
    
    # Build subsection
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6f')">
            <span>6F. Comprehensive Workforce & Productivity Dashboard</span>
            <span id="subsection-6f-toggle" style="font-size: 1.2rem;">▼</span>
        </h3>
        <div id="subsection-6f" style="display: block;">
            <h4>Portfolio-Level Workforce Excellence Overview</h4>
            {dashboard_html}
        </div>
    </div>
    """
    
    return subsection_html


def _create_comprehensive_workforce_dashboard(workforce_trends: Dict, productivity_analysis: Dict,
                                             optimization_analysis: Dict, human_capital_analysis: Dict,
                                             comparative_analysis: Dict, companies: Dict) -> str:
    """Create comprehensive workforce dashboard with multiple integrated charts"""
    
    dashboard_html = ""
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
    
    companies_list = list(workforce_trends.keys())
    
    # Portfolio Summary Stats
    total_employees = sum(m['current_employees'] for m in workforce_trends.values())
    avg_workforce_score = np.mean([m['workforce_score'] for m in comparative_analysis.values()])
    avg_productivity = np.mean([m['productivity_score'] for m in productivity_analysis.values()])
    avg_efficiency = np.mean([m['workforce_efficiency'] for m in optimization_analysis.values()])
    avg_hc_roi = np.mean([m['hc_roi'] for m in human_capital_analysis.values()])
    industry_leaders = sum(1 for m in comparative_analysis.values() if m['competitive_position'] == 'Industry Leader')
    best_in_class = sum(1 for m in comparative_analysis.values() if m['benchmark_status'] == 'Best-in-Class')
    
    summary_cards = [
        {
            "label": "Total Workforce",
            "value": f"{int(total_employees):,}",
            "description": "Portfolio employees",
            "type": "info"
        },
        {
            "label": "Workforce Excellence",
            "value": f"{avg_workforce_score:.1f}/10",
            "description": "Portfolio score",
            "type": "success" if avg_workforce_score >= 7 else "warning"
        },
        {
            "label": "Productivity Score",
            "value": f"{avg_productivity:.1f}/10",
            "description": "Labor efficiency",
            "type": "success" if avg_productivity >= 7 else "info"
        },
        {
            "label": "HC ROI",
            "value": f"{avg_hc_roi:.0f}%",
            "description": "Investment return",
            "type": "success" if avg_hc_roi > 150 else "warning"
        },
        {
            "label": "Industry Leaders",
            "value": f"{industry_leaders}/{len(companies)}",
            "description": "Market position",
            "type": "success"
        },
        {
            "label": "Best-in-Class",
            "value": f"{best_in_class}/{len(companies)}",
            "description": "Top performers",
            "type": "success"
        }
    ]
    
    summary_html = build_stat_grid(summary_cards)
    
    # Chart 1: Multi-metric performance radar
    fig1 = go.Figure()
    
    metrics = ['Workforce Score', 'Productivity', 'Efficiency', 'HC Quality']
    
    for i, company in enumerate(companies_list[:6]):  # Limit to 6 for readability
        values = [
            comparative_analysis[company]['workforce_score'],
            productivity_analysis[company]['productivity_score'],
            optimization_analysis[company]['workforce_efficiency'],
            human_capital_analysis[company]['talent_quality_score']
        ]
        
        fig1.add_trace(go.Scatter(
            x=metrics,
            y=values,
            mode='lines+markers',
            name=company,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=10)
        ))
    
    fig1.update_layout(
        title="Portfolio Workforce Performance Profile",
        xaxis_title="Performance Metrics",
        yaxis_title="Score (0-10)",
        yaxis_range=[0, 10],
        hovermode='x unified',
        height=500
    )
    
    chart1_html = build_plotly_chart(fig1.to_dict(), 'performance-profile-chart', 500)
    
    # Chart 2: Productivity vs Efficiency Bubble Chart
    productivity_scores = [productivity_analysis[c]['productivity_score'] for c in companies_list]
    efficiency_scores = [optimization_analysis[c]['workforce_efficiency'] for c in companies_list]
    hc_scores = [human_capital_analysis[c]['talent_quality_score'] for c in companies_list]
    
    # Size bubbles by HC quality score
    bubble_sizes = [score * 5 for score in hc_scores]
    
    fig2 = go.Figure(data=[go.Scatter(
        x=productivity_scores,
        y=efficiency_scores,
        mode='markers+text',
        marker=dict(
            size=bubble_sizes,
            color=colors[:len(companies_list)],
            opacity=0.6,
            line=dict(width=2, color='white')
        ),
        text=companies_list,
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Productivity: %{x:.1f}<br>Efficiency: %{y:.1f}<br>HC Quality: ' + 
                     '<br>'.join([f'{hc_scores[i]:.1f}' for i in range(len(companies_list))]) + 
                     '<extra></extra>'
    )])
    
    fig2.add_hline(y=5, line_dash="dash", line_color="red", opacity=0.5)
    fig2.add_vline(x=5, line_dash="dash", line_color="red", opacity=0.5)
    
    fig2.update_layout(
        title="Productivity vs Efficiency Matrix<br><sub>Bubble size = Talent Quality</sub>",
        xaxis_title="Productivity Score (0-10)",
        yaxis_title="Workforce Efficiency (0-10)",
        xaxis_range=[0, 10],
        yaxis_range=[0, 10],
        height=500
    )
    
    chart2_html = build_plotly_chart(fig2.to_dict(), 'productivity-efficiency-matrix', 500)
    
    # Chart 3: Industry benchmarking scatter
    percentiles = [comparative_analysis[c]['industry_percentile'] for c in companies_list]
    workforce_scores = [comparative_analysis[c]['workforce_score'] for c in companies_list]
    
    position_color_map = {
        'Industry Leader': '#10b981',
        'Above Average': '#3b82f6',
        'Industry Average': '#f59e0b',
        'Below Average': '#ef4444'
    }
    
    point_colors = [position_color_map.get(comparative_analysis[c]['competitive_position'], '#94a3b8') 
                   for c in companies_list]
    
    fig3 = go.Figure()
    
    for position in set([comparative_analysis[c]['competitive_position'] for c in companies_list]):
        position_indices = [i for i, c in enumerate(companies_list) 
                          if comparative_analysis[c]['competitive_position'] == position]
        
        fig3.add_trace(go.Scatter(
            x=[percentiles[i] for i in position_indices],
            y=[workforce_scores[i] for i in position_indices],
            mode='markers+text',
            name=position,
            marker=dict(size=15, color=position_color_map.get(position, '#94a3b8')),
            text=[companies_list[i] for i in position_indices],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Percentile: %{x:.0f}th<br>Score: %{y:.1f}/10<extra></extra>'
        ))
    
    fig3.update_layout(
        title="Industry Benchmarking Matrix",
        xaxis_title="Industry Percentile",
        yaxis_title="Workforce Score (0-10)",
        height=500
    )
    
    chart3_html = build_plotly_chart(fig3.to_dict(), 'benchmarking-matrix', 500)
    
    # Chart 4: ROI Performance with dual axis
    hc_roi_values = [human_capital_analysis[c]['hc_roi'] for c in companies_list]
    investment_efficiency = [human_capital_analysis[c]['investment_efficiency'] for c in companies_list]
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=companies_list,
        y=hc_roi_values,
        name='HC ROI (%)',
        marker_color='lightblue',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>HC ROI: %{y:.1f}%<extra></extra>'
    ))
    
    fig4.add_trace(go.Scatter(
        x=companies_list,
        y=investment_efficiency,
        name='Investment Efficiency',
        mode='lines+markers',
        marker=dict(size=10, color='red'),
        line=dict(width=3, color='red'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Efficiency: %{y:.1f}/10<extra></extra>'
    ))
    
    fig4.update_layout(
        title="Human Capital ROI & Investment Efficiency",
        xaxis_title="Companies",
        yaxis=dict(title=dict(text="HC ROI (%)", font=dict(color="blue"))),
        yaxis2=dict(title=dict(text="Investment Efficiency (0-10)", font=dict(color="red")),
                   overlaying='y', side='right'),
        height=500,
        hovermode='x unified'
    )
    
    chart4_html = build_plotly_chart(fig4.to_dict(), 'roi-efficiency-chart', 500)
    
    # Chart 5: Overall performance rating distribution
    rating_counts = {}
    for c in companies_list:
        rating = comparative_analysis[c]['overall_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    rating_colors_map = {
        'Excellent': '#10b981',
        'Good': '#3b82f6',
        'Average': '#f59e0b',
        'Below Average': '#ef4444'
    }
    
    pie_colors = [rating_colors_map.get(rating, '#94a3b8') for rating in rating_counts.keys()]
    
    fig5 = go.Figure(data=[go.Pie(
        labels=list(rating_counts.keys()),
        values=list(rating_counts.values()),
        marker=dict(colors=pie_colors),
        hole=0.4,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig5.update_layout(
        title="Overall Performance Rating Distribution",
        height=450
    )
    
    chart5_html = build_plotly_chart(fig5.to_dict(), 'rating-distribution-chart', 450)
    
    # Chart 6: Strategic focus and priorities
    focus_counts = {}
    for metrics in optimization_analysis.values():
        focus = metrics['strategic_focus']
        focus_counts[focus] = focus_counts.get(focus, 0) + 1
    
    fig6 = go.Figure(data=[go.Bar(
        y=list(focus_counts.keys()),
        x=list(focus_counts.values()),
        orientation='h',
        marker_color=colors[:len(focus_counts)],
        text=list(focus_counts.values()),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Companies: %{x}<extra></extra>'
    )])
    
    fig6.update_layout(
        title="Strategic Focus Distribution",
        xaxis_title="Number of Companies",
        yaxis_title="Strategic Focus Area",
        height=450
    )
    
    chart6_html = build_plotly_chart(fig6.to_dict(), 'focus-distribution-chart', 450)
    
    # Assemble dashboard
    dashboard_html = f"""
    <div style="margin: 30px 0;">
        <h4>Portfolio Performance Overview</h4>
        {summary_html}
        
        <h4 style="margin-top: 40px;">Integrated Performance Analysis</h4>
        {chart1_html}
        {chart2_html}
        {chart3_html}
        {chart4_html}
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            {chart5_html}
            {chart6_html}
        </div>
    </div>
    """
    
    return dashboard_html

"""
Section 6: Workforce & Productivity Analysis
Phase 4: Subsection 6G - Comprehensive Insights & Strategic Dashboard

This file contains ONLY the new function for Phase 4.
Replace the stub function in the previous phases with this implementation.
"""


# =============================================================================
# SUBSECTION 6G: COMPREHENSIVE INSIGHTS & STRATEGIC DASHBOARD
# =============================================================================

def _build_section_6g_insights(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 6G: Comprehensive Workforce Summary & Strategic Insights Dashboard"""
    
    # Get all analyses
    workforce_trends = _analyze_workforce_trends(df, companies, pd.DataFrame())
    productivity_analysis = _analyze_labor_productivity(df, companies)
    optimization_analysis = _analyze_workforce_optimization(df, companies, workforce_trends, 
                                                           productivity_analysis)
    human_capital_analysis = _analyze_human_capital_roi(df, companies, workforce_trends, 
                                                       productivity_analysis)
    comparative_analysis = _analyze_comparative_workforce(df, companies, workforce_trends,
                                                         productivity_analysis, optimization_analysis,
                                                         human_capital_analysis)
    
    if not all([workforce_trends, productivity_analysis, optimization_analysis, 
                human_capital_analysis, comparative_analysis]):
        return build_info_box("Insufficient data for comprehensive insights.", "warning")
    
    # Generate insights
    insights = _generate_comprehensive_workforce_insights(
        workforce_trends, productivity_analysis, optimization_analysis,
        human_capital_analysis, comparative_analysis, companies
    )
    
    total_companies = len(companies)
    
    # Build the dashboard-style insights section
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleSubsection('subsection-6g')">
            <span>6G. Workforce Analysis Summary & Strategic Insights</span>
            <span id="subsection-6g-toggle" style="font-size: 1.2rem;">▼</span>
        </h3>
        <div id="subsection-6g" style="display: block;">
            
            {_build_portfolio_excellence_dashboard(workforce_trends, productivity_analysis, 
                                                   optimization_analysis, human_capital_analysis, 
                                                   comparative_analysis, total_companies)}
            
            {build_section_divider()}
            
            {_build_strategic_insights_cards(insights, total_companies)}
            
            {build_section_divider()}
            
            {_build_recommendations_roadmap(insights, workforce_trends, productivity_analysis,
                                          optimization_analysis, human_capital_analysis,
                                          comparative_analysis, total_companies)}
        </div>
    </div>
    """
    
    return subsection_html


def _build_portfolio_excellence_dashboard(workforce_trends: Dict, productivity_analysis: Dict,
                                         optimization_analysis: Dict, human_capital_analysis: Dict,
                                         comparative_analysis: Dict, total_companies: int) -> str:
    """Build portfolio excellence assessment dashboard with visual metrics"""
    
    # Calculate key metrics
    total_employees = sum(m['current_employees'] for m in workforce_trends.values())
    avg_growth = np.mean([m['employee_cagr'] for m in workforce_trends.values()])
    avg_productivity = np.mean([m['productivity_score'] for m in productivity_analysis.values()])
    avg_efficiency = np.mean([m['workforce_efficiency'] for m in optimization_analysis.values()])
    avg_hc_roi = np.mean([m['hc_roi'] for m in human_capital_analysis.values()])
    avg_workforce_score = np.mean([m['workforce_score'] for m in comparative_analysis.values()])
    
    excellence_count = sum(1 for m in productivity_analysis.values() if m['productivity_rating'] == 'Excellent')
    industry_leaders = sum(1 for m in comparative_analysis.values() if m['competitive_position'] == 'Industry Leader')
    
    # Portfolio excellence score (composite)
    portfolio_score = (avg_productivity * 0.3 + avg_efficiency * 0.3 + 
                      avg_workforce_score * 0.4)
    
    # Determine portfolio rating
    if portfolio_score >= 8:
        portfolio_rating = "Exceptional"
        rating_color = "success"
        rating_emoji = "🌟"
    elif portfolio_score >= 7:
        portfolio_rating = "Excellent"
        rating_color = "success"
        rating_emoji = "⭐"
    elif portfolio_score >= 6:
        portfolio_rating = "Strong"
        rating_color = "info"
        rating_emoji = "✓"
    elif portfolio_score >= 5:
        portfolio_rating = "Good"
        rating_color = "warning"
        rating_emoji = "↗"
    else:
        portfolio_rating = "Developing"
        rating_color = "warning"
        rating_emoji = "🔄"
    
    # Main KPI cards
    kpi_cards = [
        {
            "label": "Portfolio Excellence Score",
            "value": f"{portfolio_score:.1f}/10",
            "description": f"{rating_emoji} {portfolio_rating}",
            "type": rating_color
        },
        {
            "label": "Total Workforce",
            "value": f"{int(total_employees):,}",
            "description": f"{avg_growth:+.1f}% CAGR",
            "type": "info"
        },
        {
            "label": "Productivity Score",
            "value": f"{avg_productivity:.1f}/10",
            "description": f"{excellence_count} excellent performers",
            "type": "success" if avg_productivity >= 7 else "info"
        },
        {
            "label": "Workforce Efficiency",
            "value": f"{avg_efficiency:.1f}/10",
            "description": "Optimization score",
            "type": "success" if avg_efficiency >= 7 else "info"
        },
        {
            "label": "HC ROI",
            "value": f"{avg_hc_roi:.0f}%",
            "description": "Investment returns",
            "type": "success" if avg_hc_roi > 150 else "warning"
        },
        {
            "label": "Industry Leaders",
            "value": f"{industry_leaders}/{total_companies}",
            "description": f"{(industry_leaders/total_companies)*100:.0f}% of portfolio",
            "type": "success" if industry_leaders >= total_companies * 0.3 else "info"
        }
    ]
    
    kpi_html = build_stat_grid(kpi_cards)
    
    # Progress bars for key dimensions
    productivity_pct = (avg_productivity / 10) * 100
    efficiency_pct = (avg_efficiency / 10) * 100
    hc_quality_pct = (np.mean([m['talent_quality_score'] for m in human_capital_analysis.values()]) / 10) * 100
    competitive_pct = (np.mean([m['industry_percentile'] for m in comparative_analysis.values()]))
    
    progress_html = f"""
    <div style="margin: 30px 0;">
        <h4>📊 Portfolio Performance Dimensions</h4>
        {build_completeness_bar(productivity_pct, "Labor Productivity Excellence")}
        {build_completeness_bar(efficiency_pct, "Workforce Optimization Efficiency")}
        {build_completeness_bar(hc_quality_pct, "Human Capital Quality")}
        {build_completeness_bar(competitive_pct, "Industry Competitive Position")}
    </div>
    """
    
    dashboard_html = f"""
    <div style="margin: 30px 0;">
        <h4>🎯 Portfolio Workforce Excellence Assessment</h4>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">
            Comprehensive evaluation of workforce management across {total_companies} companies
        </p>
        {kpi_html}
        {progress_html}
    </div>
    """
    
    return dashboard_html


def _build_strategic_insights_cards(insights: Dict, total_companies: int) -> str:
    """Build strategic insights as interactive cards with icons"""
    
    # Create tabbed insights interface
    tabs_html = """
    <div style="margin: 30px 0;">
        <h4>🔍 Strategic Workforce Insights</h4>
        
        <!-- Tab Navigation -->
        <div style="display: flex; gap: 10px; margin: 20px 0; border-bottom: 2px solid var(--card-border); flex-wrap: wrap;">
            <button class="insight-tab active" onclick="showInsightTab('workforce-evolution')" 
                    style="padding: 12px 24px; background: var(--primary-gradient-start); color: white; 
                           border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;
                           transition: var(--transition-fast);">
                👥 Workforce Evolution
            </button>
            <button class="insight-tab" onclick="showInsightTab('productivity')" 
                    style="padding: 12px 24px; background: var(--card-bg); color: var(--text-primary); 
                           border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;
                           transition: var(--transition-fast);">
                📈 Productivity
            </button>
            <button class="insight-tab" onclick="showInsightTab('optimization')" 
                    style="padding: 12px 24px; background: var(--card-bg); color: var(--text-primary); 
                           border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;
                           transition: var(--transition-fast);">
                ⚙️ Optimization
            </button>
            <button class="insight-tab" onclick="showInsightTab('human-capital')" 
                    style="padding: 12px 24px; background: var(--card-bg); color: var(--text-primary); 
                           border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;
                           transition: var(--transition-fast);">
                💎 Human Capital
            </button>
            <button class="insight-tab" onclick="showInsightTab('competitive')" 
                    style="padding: 12px 24px; background: var(--card-bg); color: var(--text-primary); 
                           border: none; border-radius: 8px 8px 0 0; cursor: pointer; font-weight: 600;
                           transition: var(--transition-fast);">
                🏆 Competitive Position
            </button>
        </div>
    """
    
    # Tab content containers
    tabs_html += f"""
        <!-- Tab Contents -->
        <div class="insight-tab-content" id="workforce-evolution" style="display: block;">
            {_build_insight_card("👥 Workforce Evolution & Strategic Scaling", 
                                insights['workforce_excellence'], "info")}
        </div>
        
        <div class="insight-tab-content" id="productivity" style="display: none;">
            {_build_insight_card("📈 Labor Productivity & Efficiency Excellence", 
                                insights['productivity_efficiency'], "success")}
        </div>
        
        <div class="insight-tab-content" id="optimization" style="display: none;">
            {_build_insight_card("⚙️ Strategic Workforce Optimization", 
                                insights['workforce_optimization'], "warning")}
        </div>
        
        <div class="insight-tab-content" id="human-capital" style="display: none;">
            {_build_insight_card("💎 Human Capital Investment & ROI Excellence", 
                                insights['human_capital_roi'], "success")}
        </div>
        
        <div class="insight-tab-content" id="competitive" style="display: none;">
            {_build_insight_card("🏆 Competitive Advantage & Benchmarking", 
                                insights['competitive_benchmarking'], "info")}
        </div>
    </div>
    
    <script>
    function showInsightTab(tabId) {{
        // Hide all tab contents
        document.querySelectorAll('.insight-tab-content').forEach(content => {{
            content.style.display = 'none';
        }});
        
        // Remove active class from all tabs
        document.querySelectorAll('.insight-tab').forEach(tab => {{
            tab.style.background = 'var(--card-bg)';
            tab.style.color = 'var(--text-primary)';
        }});
        
        // Show selected tab content
        document.getElementById(tabId).style.display = 'block';
        
        // Activate clicked tab
        event.target.style.background = 'var(--primary-gradient-start)';
        event.target.style.color = 'white';
    }}
    </script>
    """
    
    return tabs_html


def _build_insight_card(title: str, content: str, card_type: str = "default") -> str:
    """Build an individual insight card with formatted content"""
    
    # Parse the content and format it as bullet points
    lines = content.strip().split('\n')
    formatted_content = ""
    
    for line in lines:
        line = line.strip()
        if line:
            # Remove existing bullet points
            line = line.lstrip('• ').lstrip('- ')
            if line:
                # Add icon based on keywords
                if any(word in line.lower() for word in ['excellent', 'strong', 'high', 'leadership']):
                    icon = "✓"
                    color = "#10b981"
                elif any(word in line.lower() for word in ['good', 'moderate', 'developing']):
                    icon = "→"
                    color = "#3b82f6"
                elif any(word in line.lower() for word in ['opportunity', 'enhance', 'improve']):
                    icon = "↗"
                    color = "#f59e0b"
                else:
                    icon = "•"
                    color = "var(--text-primary)"
                
                formatted_content += f"""
                <div style="display: flex; gap: 12px; margin: 12px 0; padding: 12px; 
                           background: rgba(255, 255, 255, 0.03); border-radius: 8px;
                           border-left: 3px solid {color};">
                    <span style="color: {color}; font-weight: bold; font-size: 1.2rem;">{icon}</span>
                    <span style="flex: 1; line-height: 1.6;">{line}</span>
                </div>
                """
    
    return f"""
    <div style="background: var(--card-bg); border-radius: 16px; padding: 30px; 
               border: 1px solid var(--card-border); box-shadow: var(--shadow-sm);">
        <h4 style="margin: 0 0 20px 0; color: var(--text-primary);">{title}</h4>
        {formatted_content}
    </div>
    """


def _build_recommendations_roadmap(insights: Dict, workforce_trends: Dict, 
                                  productivity_analysis: Dict, optimization_analysis: Dict,
                                  human_capital_analysis: Dict, comparative_analysis: Dict,
                                  total_companies: int) -> str:
    """Build strategic recommendations as an action roadmap with priorities"""
    
    # Calculate priority metrics
    avg_productivity = np.mean([m['productivity_score'] for m in productivity_analysis.values()])
    avg_efficiency = np.mean([m['workforce_efficiency'] for m in optimization_analysis.values()])
    avg_hc_roi = np.mean([m['hc_roi'] for m in human_capital_analysis.values()])
    industry_leaders = sum(1 for m in comparative_analysis.values() if m['competitive_position'] == 'Industry Leader')
    excellence_count = sum(1 for m in productivity_analysis.values() if m['productivity_rating'] == 'Excellent')
    automation_ready = sum(1 for m in optimization_analysis.values() if m['automation_score'] >= 7)
    
    # Generate prioritized actions
    immediate_actions = []
    medium_term_actions = []
    long_term_actions = []
    
    # Immediate priorities (0-6 months)
    if avg_productivity < 7:
        immediate_actions.append({
            "priority": "HIGH",
            "action": "Launch comprehensive productivity enhancement programs",
            "target": f"Increase avg productivity from {avg_productivity:.1f} to 7.5",
            "impact": "High",
            "companies": f"{total_companies - excellence_count} companies need enhancement"
        })
    
    if avg_efficiency < 6:
        immediate_actions.append({
            "priority": "HIGH",
            "action": "Implement workforce efficiency optimization initiatives",
            "target": f"Improve efficiency from {avg_efficiency:.1f} to 7.0",
            "impact": "High",
            "companies": "Portfolio-wide efficiency program"
        })
    else:
        immediate_actions.append({
            "priority": "MEDIUM",
            "action": "Scale productivity excellence across all companies",
            "target": "Achieve 70%+ companies at excellent rating",
            "impact": "Medium",
            "companies": f"Focus on {total_companies - excellence_count} companies"
        })
    
    if avg_hc_roi < 150:
        immediate_actions.append({
            "priority": "MEDIUM",
            "action": "Enhance HC investment effectiveness and development ROI",
            "target": f"Increase ROI from {avg_hc_roi:.0f}% to 175%",
            "impact": "Medium",
            "companies": "Optimize talent development programs"
        })
    
    # Medium-term priorities (6-18 months)
    if excellence_count < total_companies * 0.5:
        medium_term_actions.append({
            "priority": "HIGH",
            "action": "Achieve above-market productivity performance",
            "target": "50%+ companies rated excellent",
            "impact": "High",
            "companies": "Strategic productivity transformation"
        })
    
    if automation_ready < total_companies * 0.5:
        medium_term_actions.append({
            "priority": "MEDIUM",
            "action": "Strategic workforce sizing and efficiency optimization",
            "target": f"Increase automation-ready from {automation_ready} to {int(total_companies*0.6)}",
            "impact": "Medium",
            "companies": "Technology integration programs"
        })
    
    medium_term_actions.append({
        "priority": "MEDIUM",
        "action": "Implement advanced talent development and HC ROI enhancement",
        "target": "Achieve 200%+ average HC ROI",
        "impact": "Medium",
        "companies": "Scale best practices across portfolio"
    })
    
    # Long-term priorities (18+ months)
    if industry_leaders < total_companies * 0.4:
        long_term_actions.append({
            "priority": "HIGH",
            "action": "Achieve industry leadership in workforce management",
            "target": f"Increase leaders from {industry_leaders} to {int(total_companies*0.5)}",
            "impact": "Strategic",
            "companies": "Comprehensive excellence framework"
        })
    
    long_term_actions.append({
        "priority": "MEDIUM",
        "action": "Strategic technology integration and automation optimization",
        "target": "75%+ companies with high automation readiness",
        "impact": "Strategic",
        "companies": "Workforce modernization program"
    })
    
    long_term_actions.append({
        "priority": "HIGH",
        "action": "Achieve industry recognition for human capital excellence",
        "target": "Best-in-class talent management across portfolio",
        "impact": "Strategic",
        "companies": "Build sustainable competitive advantage"
    })
    
    # Build roadmap HTML
    roadmap_html = f"""
    <div style="margin: 30px 0;">
        <h4>🎯 Strategic Workforce Excellence Roadmap</h4>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">
            Prioritized action plan for sustained workforce competitive advantage
        </p>
        
        <div style="display: grid; gap: 30px;">
            {_build_action_phase_card("🚀 Immediate Priorities (0-6 Months)", immediate_actions, "danger")}
            {_build_action_phase_card("📊 Medium-Term Strategic Enhancement (6-18 Months)", medium_term_actions, "warning")}
            {_build_action_phase_card("🏆 Long-Term Competitive Excellence (18+ Months)", long_term_actions, "success")}
        </div>
        
        {_build_success_metrics(avg_productivity, avg_efficiency, avg_hc_roi, industry_leaders, total_companies)}
    </div>
    """
    
    return roadmap_html


def _build_action_phase_card(phase_title: str, actions: List[Dict], phase_color: str) -> str:
    """Build an action phase card with prioritized actions"""
    
    if not actions:
        return ""
    
    color_map = {
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "success": "#10b981",
        "info": "#3b82f6"
    }
    
    border_color = color_map.get(phase_color, "#667eea")
    
    actions_html = ""
    for action in actions:
        priority_color = "#ef4444" if action['priority'] == "HIGH" else "#f59e0b" if action['priority'] == "MEDIUM" else "#3b82f6"
        
        actions_html += f"""
        <div style="background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px; 
                   margin: 15px 0; border-left: 4px solid {priority_color};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div style="flex: 1;">
                    <div style="display: inline-block; padding: 4px 12px; background: {priority_color}; 
                               color: white; border-radius: 6px; font-size: 0.75rem; font-weight: 700; 
                               margin-bottom: 8px;">
                        {action['priority']} PRIORITY
                    </div>
                    <h5 style="margin: 8px 0; color: var(--text-primary);">{action['action']}</h5>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 12px;">
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;">🎯 Target</div>
                    <div style="font-weight: 600; color: var(--text-primary);">{action['target']}</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;">📊 Impact</div>
                    <div style="font-weight: 600; color: var(--text-primary);">{action['impact']}</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;">🏢 Scope</div>
                    <div style="font-weight: 600; color: var(--text-primary);">{action['companies']}</div>
                </div>
            </div>
        </div>
        """
    
    return f"""
    <div style="background: var(--card-bg); border-radius: 16px; padding: 30px; 
               border: 2px solid {border_color}; box-shadow: var(--shadow-md);">
        <h4 style="margin: 0 0 20px 0; color: var(--text-primary); display: flex; align-items: center; gap: 10px;">
            {phase_title}
        </h4>
        {actions_html}
    </div>
    """


def _build_success_metrics(avg_productivity: float, avg_efficiency: float, 
                          avg_hc_roi: float, industry_leaders: int, 
                          total_companies: int) -> str:
    """Build success metrics and targets"""
    
    # Calculate targets (improvements)
    productivity_target = min(10, avg_productivity + 1.5)
    efficiency_target = min(10, avg_efficiency + 1.5)
    hc_roi_target = max(150, avg_hc_roi * 1.3)
    leaders_target = min(total_companies, industry_leaders + max(1, (total_companies - industry_leaders) // 2))
    
    metrics_html = f"""
    <div style="margin-top: 40px; background: var(--card-bg); border-radius: 16px; 
               padding: 30px; border: 1px solid var(--card-border);">
        <h4 style="margin: 0 0 20px 0;">📈 Success Metrics & Performance Targets (24-36 Months)</h4>
        
        <div style="display: grid; gap: 20px;">
            {build_progress_indicator(avg_productivity, productivity_target, 
                                     f"Workforce Excellence Score: {avg_productivity:.1f} → {productivity_target:.1f}/10", True)}
            
            {build_progress_indicator(avg_efficiency, efficiency_target, 
                                     f"Operational Efficiency: {avg_efficiency:.1f} → {efficiency_target:.1f}/10", True)}
            
            {build_progress_indicator(avg_hc_roi / 2, hc_roi_target / 2, 
                                     f"Human Capital ROI: {avg_hc_roi:.0f}% → {hc_roi_target:.0f}%", True)}
            
            {build_progress_indicator(industry_leaders, leaders_target, 
                                     f"Industry Leadership: {industry_leaders} → {leaders_target} companies", False)}
        </div>
        
        <div style="margin-top: 25px; padding: 20px; background: rgba(102, 126, 234, 0.1); 
                   border-radius: 12px; border-left: 4px solid var(--primary-gradient-start);">
            <p style="margin: 0; color: var(--text-primary); font-weight: 600;">
                💡 <strong>Success Framework:</strong> Achieve portfolio-wide workforce excellence through systematic 
                productivity enhancement, operational optimization, and strategic human capital development initiatives 
                over the next 24-36 months.
            </p>
        </div>
    </div>
    """
    
    return metrics_html


def _generate_comprehensive_workforce_insights(workforce_trends: Dict, productivity_analysis: Dict,
                                              optimization_analysis: Dict, human_capital_analysis: Dict,
                                              comparative_analysis: Dict, companies: Dict) -> Dict[str, str]:
    """Generate comprehensive workforce insights (compact bullet-point format)"""
    
    total_companies = len(companies)
    
    # Calculate key metrics
    total_employees = sum(m['current_employees'] for m in workforce_trends.values())
    avg_growth = np.mean([m['employee_cagr'] for m in workforce_trends.values()])
    avg_productivity = np.mean([m['productivity_score'] for m in productivity_analysis.values()])
    avg_efficiency = np.mean([m['workforce_efficiency'] for m in optimization_analysis.values()])
    avg_hc_roi = np.mean([m['hc_roi'] for m in human_capital_analysis.values()])
    
    excellence_count = sum(1 for m in productivity_analysis.values() if m['productivity_rating'] == 'Excellent')
    industry_leaders = sum(1 for m in comparative_analysis.values() if m['competitive_position'] == 'Industry Leader')
    automation_ready = sum(1 for m in optimization_analysis.values() if m['automation_score'] >= 7)
    
    # Workforce Excellence insight
    workforce_excellence = f"""
Portfolio encompasses {total_employees:,} employees with {avg_growth:+.1f}% annual growth trajectory
{excellence_count}/{total_companies} companies demonstrate excellent productivity performance
{'Large-scale operations' if total_employees > 50000 else 'Mid-scale flexibility' if total_employees > 10000 else 'Growth-stage agility'} with balanced scaling strategies
Workforce consistency averaging {np.mean([m['workforce_consistency'] for m in workforce_trends.values()]):.1f}/10 across portfolio
Strategic scaling efficiency {'exceeds benchmarks' if np.mean([m['scaling_efficiency'] for m in workforce_trends.values()]) > 1.5 else 'meets expectations' if np.mean([m['scaling_efficiency'] for m in workforce_trends.values()]) > 1.0 else 'requires enhancement'}
    """.strip()
    
    # Productivity insight
    avg_rpe = np.mean([m['revenue_per_employee'] for m in productivity_analysis.values()])
    productivity_efficiency = f"""
Portfolio generates ${avg_rpe/1000:.0f}K revenue per employee with {avg_productivity:.1f}/10 productivity score
{excellence_count}/{total_companies} companies ({(excellence_count/total_companies)*100:.0f}%) achieve excellent ratings
Technology intensity {'high' if sum(1 for m in productivity_analysis.values() if m['technology_intensity'] == 'High') >= total_companies*0.4 else 'moderate' if sum(1 for m in productivity_analysis.values() if m['technology_intensity'] == 'High') >= total_companies*0.2 else 'developing'} across portfolio driving efficiency gains
Labor efficiency ratios {'exceed' if np.mean([m['labor_efficiency_ratio'] for m in productivity_analysis.values()]) > 3 else 'meet' if np.mean([m['labor_efficiency_ratio'] for m in productivity_analysis.values()]) > 2 else 'below'} industry standards
Productivity growth positive in {sum(1 for m in productivity_analysis.values() if m['productivity_growth_rate'] > 0)}/{total_companies} companies
    """.strip()
    
    # Optimization insight
    optimal_sizing = sum(1 for m in optimization_analysis.values() if m['current_vs_optimal'] == 'Optimal Range')
    workforce_optimization = f"""
Average workforce efficiency {avg_efficiency:.1f}/10 with {sum(1 for m in optimization_analysis.values() if m['workforce_efficiency'] >= 7)}/{total_companies} companies achieving high efficiency
{optimal_sizing}/{total_companies} companies operating within optimal workforce size ranges
Automation readiness strong with {automation_ready}/{total_companies} companies well-positioned for technology integration
Scaling efficiency {'exceptional' if np.mean([m['scaling_factor'] for m in optimization_analysis.values()]) > 1.5 else 'strong' if np.mean([m['scaling_factor'] for m in optimization_analysis.values()]) > 1.2 else 'developing'} across revenue-to-workforce dynamics
Strategic focus balanced between {'productivity enhancement' if sum(1 for m in optimization_analysis.values() if 'Productivity' in m['strategic_focus']) >= total_companies*0.4 else 'efficiency optimization' if sum(1 for m in optimization_analysis.values() if 'Efficiency' in m['strategic_focus']) >= total_companies*0.4 else 'growth scaling'}
    """.strip()
    
    # Human Capital insight
    total_hc_investment = sum(m['hc_investment'] for m in human_capital_analysis.values())
    human_capital_roi = f"""
Portfolio invests ${total_hc_investment/1000000:.0f}M in human capital generating {avg_hc_roi:.0f}% average ROI
Talent quality scores averaging {np.mean([m['talent_quality_score'] for m in human_capital_analysis.values()]):.1f}/10 across portfolio
Investment efficiency {'excellent' if sum(1 for m in human_capital_analysis.values() if m['investment_efficiency'] >= 7) >= total_companies*0.5 else 'good' if sum(1 for m in human_capital_analysis.values() if m['investment_efficiency'] >= 7) >= total_companies*0.3 else 'developing'} with {sum(1 for m in human_capital_analysis.values() if m['investment_efficiency'] >= 7)}/{total_companies} high-efficiency companies
Development ROI {'strong' if np.mean([m['development_roi'] for m in human_capital_analysis.values()]) > 50 else 'moderate' if np.mean([m['development_roi'] for m in human_capital_analysis.values()]) > 0 else 'enhancement needed'} with average {np.mean([m['development_roi'] for m in human_capital_analysis.values()]):.0f}% returns
Skill premium {'high' if np.mean([m['skill_premium'] for m in human_capital_analysis.values()]) > 25 else 'competitive' if np.mean([m['skill_premium'] for m in human_capital_analysis.values()]) > 0 else 'developing'} indicating workforce quality advantage
    """.strip()
    
    # Competitive insight
    avg_percentile = np.mean([m['industry_percentile'] for m in comparative_analysis.values()])
    competitive_benchmarking = f"""
Portfolio positioned at {avg_percentile:.0f}th industry percentile with {industry_leaders}/{total_companies} industry leaders
Best-in-class recognition achieved by {sum(1 for m in comparative_analysis.values() if m['benchmark_status'] == 'Best-in-Class')}/{total_companies} companies
Competitive positioning {'market leadership' if industry_leaders >= total_companies*0.4 else 'above-average' if avg_percentile >= 60 else 'developing'} across workforce metrics
Best practices concentrated in {'productivity & efficiency' if sum(1 for m in comparative_analysis.values() if 'Productivity' in m['best_practice_area']) >= total_companies*0.4 else 'workforce efficiency' if sum(1 for m in comparative_analysis.values() if 'Efficiency' in m['best_practice_area']) >= total_companies*0.4 else 'operational foundation'} domains
Strategic priorities {'excellence maintenance' if sum(1 for m in comparative_analysis.values() if m['strategic_priority'] in ['Maintain Excellence', 'Enhance Leadership']) >= total_companies*0.5 else 'improvement acceleration' if sum(1 for m in comparative_analysis.values() if m['strategic_priority'] == 'Accelerate Improvement') >= total_companies*0.4 else 'transformation required'}
    """.strip()
    
    return {
        'workforce_excellence': workforce_excellence,
        'productivity_efficiency': productivity_efficiency,
        'workforce_optimization': workforce_optimization,
        'human_capital_roi': human_capital_roi,
        'competitive_benchmarking': competitive_benchmarking
    }