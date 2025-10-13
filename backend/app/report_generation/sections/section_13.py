"""Section 13: Institutional Ownership Dynamics"""

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
    build_completeness_bar,
    format_currency,
    format_percentage,
    format_number
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 13: Institutional Ownership Dynamics
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    
    try:
        institutional_df = collector.get_institutional_ownership()
    except Exception as e:
        institutional_df = pd.DataFrame()
    
    try:
        df = collector.get_all_financial_data()
    except Exception as e:
        df = pd.DataFrame()
    
    try:
        prices_df = collector.get_prices_daily()
    except Exception as e:
        prices_df = pd.DataFrame()
    
    # Generate analyses
    ownership_flow = _generate_ownership_flow_analysis(institutional_df, companies)
    quality_metrics = _analyze_institutional_quality(institutional_df, companies)
    momentum_analysis = _generate_ownership_momentum_analysis(institutional_df, companies)
    float_analysis = _generate_float_analysis(institutional_df, companies, df, prices_df)
    
    # Build all subsections
    section_13a_html = _build_section_13a(ownership_flow, companies)
    section_13b_html = _build_section_13b(quality_metrics, companies)
    section_13c_html = _build_section_13c(momentum_analysis)
    section_13d_html = _build_section_13d(float_analysis)
    section_13e_html = _build_section_13e(institutional_df, companies, ownership_flow, quality_metrics, momentum_analysis, float_analysis)
    section_13f_html = _build_section_13f(ownership_flow, quality_metrics, momentum_analysis, float_analysis, companies)
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        {section_13a_html}
        {build_section_divider() if section_13b_html else ""}
        {section_13b_html}
        {build_section_divider() if section_13c_html else ""}
        {section_13c_html}
        {build_section_divider() if section_13d_html else ""}
        {section_13d_html}
        {build_section_divider() if section_13e_html else ""}
        {section_13e_html}
        {build_section_divider() if section_13f_html else ""}
        {section_13f_html}
    </div>
    """
    
    return generate_section_wrapper(13, "Institutional Ownership Dynamics", content)


# =============================================================================
# SUBSECTION 13A: OWNERSHIP FLOW ANALYSIS
# =============================================================================

def _build_section_13a(ownership_flow: Dict[str, Dict], companies: Dict[str, str]) -> str:
    """Build subsection 13A: Ownership Flow Analysis & Position Change Tracking"""
    
    if not ownership_flow:
        return build_info_box(
            "Ownership flow analysis unavailable due to insufficient institutional data.",
            "warning",
            "13A. Ownership Flow Analysis"
        )
    
    # Create collapsible section header
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-13a')">
            <h2>13A. Ownership Flow Analysis & Position Change Tracking</h2>
            <span class="toggle-icon" id="icon-section-13a">▼</span>
        </div>
        <div class="subsection-content" id="section-13a">
    """
    
    # Summary stats
    total_companies = len(ownership_flow)
    strong_inflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Strong Inflow')
    moderate_inflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Moderate Inflow')
    strong_outflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Strong Outflow')
    avg_flow_quality = np.mean([flow['flow_quality_score'] for flow in ownership_flow.values()])
    total_new_positions = sum(flow['new_positions'] for flow in ownership_flow.values())
    total_exits = sum(flow['sold_out_positions'] for flow in ownership_flow.values())
    
    stat_cards = [
        {
            "label": "Strong Inflow Companies",
            "value": str(strong_inflow),
            "description": f"Out of {total_companies} companies",
            "type": "success"
        },
        {
            "label": "New Positions (Total)",
            "value": str(total_new_positions),
            "description": "Across all companies",
            "type": "info"
        },
        {
            "label": "Exits (Total)",
            "value": str(total_exits),
            "description": "Position closures",
            "type": "danger"
        },
        {
            "label": "Average Flow Quality",
            "value": f"{avg_flow_quality:.1f}/10",
            "description": "Portfolio flow quality score",
            "type": "default"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Flow table
    html += "<h3>Quarterly Institutional Position Changes</h3>"
    flow_df = _create_ownership_flow_dataframe(ownership_flow)
    html += build_data_table(flow_df, table_id="ownership-flow-table")
    
    # Chart 1: New Positions vs Exits
    html += _create_flow_new_vs_exits_chart(ownership_flow)
    
    # Chart 2: Flow Direction Distribution
    html += _create_flow_direction_pie_chart(ownership_flow)
    
    # Chart 3: Flow Activity vs Quality
    html += _create_flow_activity_quality_chart(ownership_flow)
    
    # Chart 4: Net Flow Scores
    html += _create_net_flow_scores_chart(ownership_flow)
    
    # Summary narrative
    summary_text = _generate_ownership_flow_summary(ownership_flow)
    html += build_info_box(summary_text, "info", "Ownership Flow Analysis Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_ownership_flow_dataframe(ownership_flow: Dict[str, Dict]) -> pd.DataFrame:
    """Create DataFrame for ownership flow table"""
    
    rows = []
    for company_name, flow_data in ownership_flow.items():
        rows.append({
            'Company': company_name,
            'Latest Quarter': str(flow_data['latest_quarter'])[:10] if flow_data['latest_quarter'] else "N/A",
            'New Positions': flow_data['new_positions'],
            'Exits': flow_data['sold_out_positions'],
            'Increases': flow_data['increased_positions'],
            'Decreases': flow_data['decreased_positions'],
            'Net Flow Score': f"{flow_data['net_flow_score']:+.1f}",
            'Flow Direction': flow_data['flow_direction'],
            'Activity Level': flow_data['activity_level'],
            'Flow Quality': f"{flow_data['flow_quality_score']:.1f}"
        })
    
    df = pd.DataFrame(rows)
    # Sort by flow quality score
    df['_sort_key'] = [ownership_flow[name]['flow_quality_score'] for name in df['Company']]
    df = df.sort_values('_sort_key', ascending=False).drop('_sort_key', axis=1)
    
    return df


def _create_flow_new_vs_exits_chart(ownership_flow: Dict[str, Dict]) -> str:
    """Create chart: New Positions vs Exits"""
    
    companies = list(ownership_flow.keys())
    new_positions = [int(ownership_flow[comp]['new_positions']) for comp in companies]
    exits = [int(ownership_flow[comp]['sold_out_positions']) for comp in companies]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'x': [comp[:12] for comp in companies],
                'y': new_positions,
                'name': 'New Positions',
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>New Positions: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'x': [comp[:12] for comp in companies],
                'y': exits,
                'name': 'Exits',
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{x}</b><br>Exits: %{y}<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Institutional Position Changes: New vs Exits', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Number of Positions'},
            'barmode': 'group',
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="flow-new-vs-exits", height=500)


def _create_flow_direction_pie_chart(ownership_flow: Dict[str, Dict]) -> str:
    """Create chart: Flow Direction Distribution"""
    
    flow_directions = [ownership_flow[comp]['flow_direction'] for comp in ownership_flow.keys()]
    direction_counts = {}
    for direction in flow_directions:
        direction_counts[direction] = direction_counts.get(direction, 0) + 1
    
    if not direction_counts:
        return ""
    
    labels = list(direction_counts.keys())
    values = list(direction_counts.values())
    
    flow_colors = {
        'Strong Inflow': '#059669',
        'Moderate Inflow': '#10b981',
        'Balanced': '#f59e0b',
        'Moderate Outflow': '#fb923c',
        'Strong Outflow': '#ef4444'
    }
    colors = [flow_colors.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            'textinfo': 'label+percent',
            'textposition': 'auto'
        }],
        'layout': {
            'title': {'text': 'Portfolio Flow Direction Distribution', 'font': {'size': 16, 'weight': 'bold'}},
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': -0.2, 'xanchor': 'center', 'x': 0.5}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="flow-direction-pie", height=500)


def _create_flow_activity_quality_chart(ownership_flow: Dict[str, Dict]) -> str:
    """Create chart: Flow Activity vs Quality"""
    
    companies = list(ownership_flow.keys())
    flow_activity = [int(ownership_flow[comp]['total_flow_activity']) for comp in companies]
    flow_quality = [float(ownership_flow[comp]['flow_quality_score']) for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'x': flow_activity,
            'y': flow_quality,
            'mode': 'markers+text',
            'marker': {
                'size': 12,
                'color': flow_quality,  # Already converted to float list
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Quality Score'}
            },
            'text': [comp[:8] for comp in companies],
            'textposition': 'top center',
            'hovertemplate': '<b>%{text}</b><br>Activity: %{x}<br>Quality: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Flow Activity vs Quality Analysis', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Total Flow Activity'},
            'yaxis': {'title': 'Flow Quality Score'},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="flow-activity-quality", height=500)


def _create_net_flow_scores_chart(ownership_flow: Dict[str, Dict]) -> str:
    """Create chart: Net Flow Scores"""
    
    companies = list(ownership_flow.keys())
    net_flow_scores = [float(ownership_flow[comp]['net_flow_score']) for comp in companies]
    
    # Color bars based on score
    bar_colors = []
    for score in net_flow_scores:
        if score > 3:
            bar_colors.append('#059669')  # Strong positive
        elif score > 1:
            bar_colors.append('#10b981')  # Moderate positive
        elif score > -1:
            bar_colors.append('#94a3b8')  # Neutral
        elif score > -3:
            bar_colors.append('#fb923c')  # Moderate negative
        else:
            bar_colors.append('#ef4444')  # Strong negative
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in companies],
            'y': net_flow_scores,
            'marker': {'color': bar_colors},
            'hovertemplate': '<b>%{x}</b><br>Net Flow Score: %{y:+.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Net Institutional Flow Scores', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Net Flow Score'},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2, 'dash': 'dash'}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="net-flow-scores", height=500)


# =============================================================================
# SUBSECTION 13B: INSTITUTIONAL QUALITY METRICS
# =============================================================================

def _build_section_13b(quality_metrics: Dict[str, Dict], companies: Dict[str, str]) -> str:
    """Build subsection 13B: Institutional Quality Metrics & Holder Concentration Analysis"""
    
    if not quality_metrics:
        return build_info_box(
            "Institutional quality metrics unavailable due to insufficient data.",
            "warning",
            "13B. Institutional Quality Metrics"
        )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-13b')">
            <h2>13B. Institutional Quality Metrics & Holder Concentration Analysis</h2>
            <span class="toggle-icon" id="icon-section-13b">▼</span>
        </div>
        <div class="subsection-content" id="section-13b">
    """
    
    # Summary stats
    total_companies = len(quality_metrics)
    excellent_quality = sum(1 for m in quality_metrics.values() if m['quality_rating'] == 'Excellent')
    high_quality = sum(1 for m in quality_metrics.values() if m['quality_rating'] == 'High Quality')
    avg_quality_score = np.mean([m['quality_score'] for m in quality_metrics.values()])
    avg_investors = np.mean([m['investors_holding'] for m in quality_metrics.values()])
    high_concentration = sum(1 for m in quality_metrics.values() if m['concentration_risk'] in ['High', 'Very High'])
    
    stat_cards = [
        {
            "label": "Excellent Quality Companies",
            "value": str(excellent_quality),
            "description": f"Out of {total_companies} companies",
            "type": "success"
        },
        {
            "label": "Average Quality Score",
            "value": f"{avg_quality_score:.1f}/10",
            "description": "Portfolio quality assessment",
            "type": "info"
        },
        {
            "label": "Average Investors",
            "value": f"{avg_investors:.0f}",
            "description": "Per company",
            "type": "default"
        },
        {
            "label": "High Concentration Risk",
            "value": str(high_concentration),
            "description": "Companies requiring monitoring",
            "type": "warning" if high_concentration > 0 else "success"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Quality table
    html += "<h3>Institutional Quality Metrics & Holder Concentration</h3>"
    quality_df = _create_quality_metrics_dataframe(quality_metrics)
    html += build_data_table(quality_df, table_id="quality-metrics-table")
    
    # Chart 1: Quality Score vs Investor Count
    html += _create_quality_vs_investors_chart(quality_metrics)
    
    # Chart 2: HHI Distribution
    html += _create_hhi_distribution_chart(quality_metrics)
    
    # Chart 3: Quality Rating Distribution
    html += _create_quality_rating_pie_chart(quality_metrics)
    
    # Chart 4: Stability vs Ownership
    html += _create_stability_ownership_chart(quality_metrics)
    
    # Summary narrative
    summary_text = _generate_quality_metrics_summary(quality_metrics)
    html += build_info_box(summary_text, "info", "Quality Metrics Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_quality_metrics_dataframe(quality_metrics: Dict[str, Dict]) -> pd.DataFrame:
    """Create DataFrame for quality metrics table"""
    
    rows = []
    for company_name, metrics in quality_metrics.items():
        rows.append({
            'Company': company_name,
            'Investors': metrics['investors_holding'],
            'Ownership %': f"{metrics['ownership_percentage']:.1f}",
            'Avg Position ($M)': f"{metrics['avg_position_size_millions']:.1f}",
            'Est. HHI': f"{metrics['estimated_hhi']:.0f}",
            'Stability': f"{metrics['stability_score']:.1f}/10",
            'Quality Score': f"{metrics['quality_score']:.1f}/10",
            'Concentration': metrics['concentration_risk'],
            'Rating': metrics['quality_rating']
        })
    
    df = pd.DataFrame(rows)
    # Sort by quality score
    df['_sort_key'] = [quality_metrics[name]['quality_score'] for name in df['Company']]
    df = df.sort_values('_sort_key', ascending=False).drop('_sort_key', axis=1)
    
    return df


def _create_quality_vs_investors_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create chart: Quality Score vs Investor Count"""
    
    companies = list(quality_metrics.keys())
    investor_counts = [int(quality_metrics[comp]['investors_holding']) for comp in companies]
    quality_scores = [float(quality_metrics[comp]['quality_score']) for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'x': investor_counts,
            'y': quality_scores,
            'mode': 'markers+text',
            'marker': {
                'size': 12,
                'color': quality_scores,  # Already converted to float list
                'colorscale': 'RdYlGn',
                'showscale': True,
                'colorbar': {'title': 'Quality'}
            },
            'text': [comp[:8] for comp in companies],
            'textposition': 'top center',
            'hovertemplate': '<b>%{text}</b><br>Investors: %{x}<br>Quality: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Institutional Quality vs Investor Count', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Number of Institutional Investors'},
            'yaxis': {'title': 'Quality Score (0-10)'},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="quality-vs-investors", height=500)


def _create_hhi_distribution_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create chart: HHI Distribution"""
    
    companies = list(quality_metrics.keys())
    hhi_values = [float(quality_metrics[comp]['estimated_hhi']) for comp in companies]
    concentration_risks = [quality_metrics[comp]['concentration_risk'] for comp in companies]
    
    # Color by concentration risk
    risk_colors_map = {
        'Low': '#10b981',
        'Moderate': '#f59e0b',
        'High': '#fb923c',
        'Very High': '#ef4444'
    }
    bar_colors = [risk_colors_map.get(risk, '#94a3b8') for risk in concentration_risks]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in companies],
            'y': hhi_values,
            'marker': {'color': bar_colors},
            'hovertemplate': '<b>%{x}</b><br>HHI: %{y:.0f}<br>Risk: ' + 
                           '<br>'.join([f'{comp[:12]}: {risk}' for comp, risk in zip(companies, concentration_risks)]) +
                           '<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Holder Concentration Index (HHI)', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Estimated HHI'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 1500,
                    'y1': 1500,
                    'line': {'color': '#f59e0b', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 2500,
                    'y1': 2500,
                    'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {
                    'x': len(companies) - 1,
                    'y': 1500,
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'text': 'Moderate Threshold',
                    'showarrow': False,
                    'font': {'color': '#f59e0b'}
                },
                {
                    'x': len(companies) - 1,
                    'y': 2500,
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'text': 'High Threshold',
                    'showarrow': False,
                    'font': {'color': '#ef4444'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="hhi-distribution", height=500)


def _create_quality_rating_pie_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create chart: Quality Rating Distribution"""
    
    quality_ratings = [quality_metrics[comp]['quality_rating'] for comp in quality_metrics.keys()]
    rating_counts = {}
    for rating in quality_ratings:
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    if not rating_counts:
        return ""
    
    labels = list(rating_counts.keys())
    values = list(rating_counts.values())
    
    rating_colors = {
        'Excellent': '#059669',
        'High Quality': '#10b981',
        'Standard Quality': '#f59e0b',
        'Developing Quality': '#fb923c',
        'Below Average': '#ef4444'
    }
    colors = [rating_colors.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            'textinfo': 'label+percent',
            'textposition': 'auto'
        }],
        'layout': {
            'title': {'text': 'Portfolio Quality Rating Distribution', 'font': {'size': 16, 'weight': 'bold'}},
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': -0.2, 'xanchor': 'center', 'x': 0.5}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="quality-rating-pie", height=500)


def _create_stability_ownership_chart(quality_metrics: Dict[str, Dict]) -> str:
    """Create chart: Stability vs Ownership Percentage"""
    
    companies = list(quality_metrics.keys())
    ownership_pcts = [float(quality_metrics[comp]['ownership_percentage']) for comp in companies]
    stability_scores = [float(quality_metrics[comp]['stability_score']) for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'x': ownership_pcts,
            'y': stability_scores,
            'mode': 'markers+text',
            'marker': {
                'size': 12,
                'color': stability_scores,  # Already converted to float list
                'colorscale': 'Blues',
                'showscale': True,
                'colorbar': {'title': 'Stability'}
            },
            'text': [comp[:8] for comp in companies],
            'textposition': 'top center',
            'hovertemplate': '<b>%{text}</b><br>Ownership: %{x:.1f}%<br>Stability: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Ownership Stability vs Institutional Percentage', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Institutional Ownership (%)'},
            'yaxis': {'title': 'Stability Score (0-10)'},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="stability-ownership", height=500)


# =============================================================================
# SUBSECTION 13C: OWNERSHIP MOMENTUM & INVESTMENT FLOW ANALYSIS
# =============================================================================

def _build_section_13c(momentum_analysis: Dict[str, Dict]) -> str:
    """Build subsection 13C: Ownership Momentum & Investment Flow Analysis"""
    
    if not momentum_analysis:
        return build_info_box(
            "Ownership momentum analysis unavailable due to insufficient data.",
            "warning",
            "13C. Ownership Momentum Analysis"
        )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-13c')">
            <h2>13C. Ownership Momentum & Investment Flow Analysis</h2>
            <span class="toggle-icon" id="icon-section-13c">▼</span>
        </div>
        <div class="subsection-content" id="section-13c">
    """
    
    # Summary stats
    total_companies = len(momentum_analysis)
    very_strong = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] == 'Very Strong')
    strong = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] == 'Strong')
    weak = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] in ['Weak', 'Very Weak'])
    inflow_companies = sum(1 for m in momentum_analysis.values() if m['flow_direction'] == 'Inflow')
    avg_momentum_score = np.mean([m['momentum_score'] for m in momentum_analysis.values()])
    
    stat_cards = [
        {
            "label": "Strong Momentum Companies",
            "value": str(very_strong + strong),
            "description": f"Out of {total_companies} companies",
            "type": "success"
        },
        {
            "label": "Inflow Direction",
            "value": str(inflow_companies),
            "description": "Companies with capital inflows",
            "type": "info"
        },
        {
            "label": "Average Momentum Score",
            "value": f"{avg_momentum_score:.1f}/10",
            "description": "Portfolio momentum strength",
            "type": "default"
        },
        {
            "label": "Weak Momentum",
            "value": str(weak),
            "description": "Requiring attention",
            "type": "warning" if weak > 0 else "success"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Momentum table
    html += "<h3>Quarterly Ownership Changes & Investment Flow</h3>"
    momentum_df = _create_momentum_analysis_dataframe(momentum_analysis)
    html += build_data_table(momentum_df, table_id="momentum-analysis-table")
    
    # Chart 1: Momentum Score by Company
    html += _create_momentum_scores_chart(momentum_analysis)
    
    # Chart 2: Ownership Change vs Investment Change
    html += _create_ownership_investment_scatter(momentum_analysis)
    
    # Chart 3: Flow Direction Distribution
    html += _create_momentum_flow_pie_chart(momentum_analysis)
    
    # Chart 4: Investor Count Changes
    html += _create_investor_count_changes_chart(momentum_analysis)
    
    # Summary narrative
    summary_text = _generate_momentum_analysis_summary(momentum_analysis)
    html += build_info_box(summary_text, "info", "Momentum Analysis Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_momentum_analysis_dataframe(momentum_analysis: Dict[str, Dict]) -> pd.DataFrame:
    """Create DataFrame for momentum analysis table"""
    
    rows = []
    for company_name, momentum_data in momentum_analysis.items():
        rows.append({
            'Company': company_name,
            'Ownership %': f"{momentum_data['latest_ownership_pct']:.1f}",
            'Ownership Δ (pp)': f"{momentum_data['ownership_change_pp']:+.1f}",
            'Investment Δ (%)': f"{momentum_data['total_invested_change_pct']:+.1f}",
            'Investor Δ': f"{momentum_data['investor_count_change']:+d}",
            'Momentum Score': f"{momentum_data['momentum_score']:.1f}/10",
            'Flow Direction': momentum_data['flow_direction'],
            'Flow Strength': momentum_data['flow_strength'],
            'Rating': momentum_data['momentum_rating']
        })
    
    df = pd.DataFrame(rows)
    # Sort by momentum score
    df['_sort_key'] = [momentum_analysis[name]['momentum_score'] for name in df['Company']]
    df = df.sort_values('_sort_key', ascending=False).drop('_sort_key', axis=1)
    
    return df


def _create_momentum_scores_chart(momentum_analysis: Dict[str, Dict]) -> str:
    """Create chart: Momentum Score by Company"""
    
    companies = list(momentum_analysis.keys())
    momentum_scores = [float(momentum_analysis[comp]['momentum_score']) for comp in companies]
    momentum_ratings = [momentum_analysis[comp]['momentum_rating'] for comp in companies]
    
    # Color by momentum rating
    rating_colors_map = {
        'Very Strong': '#059669',
        'Strong': '#10b981',
        'Moderate': '#f59e0b',
        'Weak': '#fb923c',
        'Very Weak': '#ef4444'
    }
    bar_colors = [rating_colors_map.get(rating, '#94a3b8') for rating in momentum_ratings]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in companies],
            'y': momentum_scores,
            'marker': {'color': bar_colors},
            'hovertemplate': '<b>%{x}</b><br>Momentum Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Institutional Ownership Momentum Scores', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Momentum Score (0-10)'},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="momentum-scores", height=500)


def _create_ownership_investment_scatter(momentum_analysis: Dict[str, Dict]) -> str:
    """Create chart: Ownership Change vs Investment Change"""
    
    companies = list(momentum_analysis.keys())
    ownership_changes = [float(momentum_analysis[comp]['ownership_change_pp']) for comp in companies]
    investment_changes = [float(momentum_analysis[comp]['total_invested_change_pct']) for comp in companies]
    momentum_scores = [float(momentum_analysis[comp]['momentum_score']) for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'x': ownership_changes,
            'y': investment_changes,
            'mode': 'markers+text',
            'marker': {
                'size': 12,
                'color': momentum_scores,
                'colorscale': 'RdYlGn',
                'showscale': True,
                'colorbar': {'title': 'Momentum'}
            },
            'text': [comp[:8] for comp in companies],
            'textposition': 'top center',
            'hovertemplate': '<b>%{text}</b><br>Ownership Δ: %{x:+.1f}pp<br>Investment Δ: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Ownership vs Investment Flow Changes', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Ownership Change (percentage points)', 'zeroline': True},
            'yaxis': {'title': 'Total Investment Change (%)', 'zeroline': True},
            'shapes': [
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': 0,
                    'y0': min(investment_changes) - 5,
                    'y1': max(investment_changes) + 5,
                    'line': {'color': 'black', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': min(ownership_changes) - 1,
                    'x1': max(ownership_changes) + 1,
                    'y0': 0,
                    'y1': 0,
                    'line': {'color': 'black', 'width': 1, 'dash': 'dash'}
                }
            ],
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ownership-investment-scatter", height=500)


def _create_momentum_flow_pie_chart(momentum_analysis: Dict[str, Dict]) -> str:
    """Create chart: Flow Direction Distribution"""
    
    flow_directions = [momentum_analysis[comp]['flow_direction'] for comp in momentum_analysis.keys()]
    direction_counts = {}
    for direction in flow_directions:
        direction_counts[direction] = direction_counts.get(direction, 0) + 1
    
    if not direction_counts:
        return ""
    
    labels = list(direction_counts.keys())
    values = list(direction_counts.values())
    
    flow_colors = {
        'Inflow': '#10b981',
        'Mixed': '#f59e0b',
        'Outflow': '#ef4444'
    }
    colors = [flow_colors.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            'textinfo': 'label+percent',
            'textposition': 'auto'
        }],
        'layout': {
            'title': {'text': 'Portfolio Flow Direction Distribution', 'font': {'size': 16, 'weight': 'bold'}},
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': -0.2, 'xanchor': 'center', 'x': 0.5}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="momentum-flow-pie", height=500)


def _create_investor_count_changes_chart(momentum_analysis: Dict[str, Dict]) -> str:
    """Create chart: Quarterly Investor Count Changes"""
    
    companies = list(momentum_analysis.keys())
    investor_changes = [int(momentum_analysis[comp]['investor_count_change']) for comp in companies]
    
    # Color bars based on positive/negative changes
    bar_colors = []
    for change in investor_changes:
        if change > 0:
            bar_colors.append('#10b981')
        elif change < 0:
            bar_colors.append('#ef4444')
        else:
            bar_colors.append('#94a3b8')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in companies],
            'y': investor_changes,
            'marker': {'color': bar_colors},
            'hovertemplate': '<b>%{x}</b><br>Investor Change: %{y:+d}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Quarterly Investor Count Changes', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Investor Count Change'},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': 0,
                'y1': 0,
                'line': {'color': 'black', 'width': 2, 'dash': 'dash'}
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="investor-count-changes", height=500)


# =============================================================================
# SUBSECTION 13D: FLOAT ANALYSIS & LIQUIDITY ASSESSMENT
# =============================================================================

def _build_section_13d(float_analysis: Dict[str, Dict]) -> str:
    """Build subsection 13D: Float Analysis & Liquidity Assessment"""
    
    if not float_analysis:
        return build_info_box(
            "Float analysis unavailable due to insufficient data.",
            "warning",
            "13D. Float Analysis"
        )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-13d')">
            <h2>13D. Float Analysis & Liquidity Assessment</h2>
            <span class="toggle-icon" id="icon-section-13d">▼</span>
        </div>
        <div class="subsection-content" id="section-13d">
    """
    
    # Summary stats
    total_companies = len(float_analysis)
    excellent_liquidity = sum(1 for f in float_analysis.values() if f['liquidity_rating'] == 'Excellent')
    good_liquidity = sum(1 for f in float_analysis.values() if f['liquidity_rating'] == 'Good')
    poor_liquidity = sum(1 for f in float_analysis.values() if f['liquidity_rating'] in ['Poor', 'Very Poor'])
    avg_liquidity_score = np.mean([f['liquidity_score'] for f in float_analysis.values()])
    avg_float = np.mean([f['estimated_float_pct'] for f in float_analysis.values()])
    
    stat_cards = [
        {
            "label": "Excellent Liquidity",
            "value": str(excellent_liquidity),
            "description": f"Out of {total_companies} companies",
            "type": "success"
        },
        {
            "label": "Average Float %",
            "value": f"{avg_float:.1f}%",
            "description": "Estimated free float",
            "type": "info"
        },
        {
            "label": "Average Liquidity Score",
            "value": f"{avg_liquidity_score:.1f}/10",
            "description": "Portfolio liquidity",
            "type": "default"
        },
        {
            "label": "Poor Liquidity",
            "value": str(poor_liquidity),
            "description": "Requiring attention",
            "type": "warning" if poor_liquidity > 0 else "success"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Float analysis table
    html += "<h3>True Float Calculations & Trading Liquidity</h3>"
    float_df = _create_float_analysis_dataframe(float_analysis)
    html += build_data_table(float_df, table_id="float-analysis-table")
    
    # Chart 1: Float Percentage vs Turnover
    html += _create_float_turnover_scatter(float_analysis)
    
    # Chart 2: Liquidity Score Distribution
    html += _create_liquidity_scores_chart(float_analysis)
    
    # Chart 3: Liquidity Rating Distribution
    html += _create_liquidity_rating_pie_chart(float_analysis)
    
    # Chart 4: Institutional Ownership vs Float
    html += _create_ownership_float_dual_chart(float_analysis)
    
    # Summary narrative
    summary_text = _generate_float_analysis_summary(float_analysis)
    html += build_info_box(summary_text, "info", "Float Analysis Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_float_analysis_dataframe(float_analysis: Dict[str, Dict]) -> pd.DataFrame:
    """Create DataFrame for float analysis table"""
    
    rows = []
    for company_name, float_data in float_analysis.items():
        rows.append({
            'Company': company_name,
            'Inst. Own. %': f"{float_data['institutional_ownership_pct']:.1f}",
            'Est. Float %': f"{float_data['estimated_float_pct']:.1f}",
            'Turnover (Ann.)': f"{float_data['float_turnover_annual']:.2f}x",
            'Liquidity Score': f"{float_data['liquidity_score']:.1f}/10",
            'Concentration': float_data['concentration_risk'],
            'Trading Liq.': float_data['trading_liquidity'],
            'Rating': float_data['liquidity_rating']
        })
    
    df = pd.DataFrame(rows)
    # Sort by liquidity score
    df['_sort_key'] = [float_analysis[name]['liquidity_score'] for name in df['Company']]
    df = df.sort_values('_sort_key', ascending=False).drop('_sort_key', axis=1)
    
    return df


def _create_float_turnover_scatter(float_analysis: Dict[str, Dict]) -> str:
    """Create chart: Float Percentage vs Turnover"""
    
    companies = list(float_analysis.keys())
    float_pcts = [float(float_analysis[comp]['estimated_float_pct']) for comp in companies]
    turnovers = [float(float_analysis[comp]['float_turnover_annual']) for comp in companies]
    liquidity_scores = [float(float_analysis[comp]['liquidity_score']) for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'x': float_pcts,
            'y': turnovers,
            'mode': 'markers+text',
            'marker': {
                'size': 12,
                'color': liquidity_scores,
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Liquidity'}
            },
            'text': [comp[:8] for comp in companies],
            'textposition': 'top center',
            'hovertemplate': '<b>%{text}</b><br>Float: %{x:.1f}%<br>Turnover: %{y:.2f}x<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Float Percentage vs Turnover Analysis', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Estimated Float (%)'},
            'yaxis': {'title': 'Annual Float Turnover'},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="float-turnover-scatter", height=500)


def _create_liquidity_scores_chart(float_analysis: Dict[str, Dict]) -> str:
    """Create chart: Liquidity Score Distribution"""
    
    companies = list(float_analysis.keys())
    liquidity_scores = [float(float_analysis[comp]['liquidity_score']) for comp in companies]
    
    # Color by score range
    bar_colors = []
    for score in liquidity_scores:
        if score >= 8:
            bar_colors.append('#059669')
        elif score >= 6:
            bar_colors.append('#10b981')
        elif score >= 4:
            bar_colors.append('#f59e0b')
        else:
            bar_colors.append('#ef4444')
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in companies],
            'y': liquidity_scores,
            'marker': {'color': bar_colors},
            'hovertemplate': '<b>%{x}</b><br>Liquidity Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Portfolio Liquidity Score Assessment', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Liquidity Score (0-10)'},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="liquidity-scores", height=500)


def _create_liquidity_rating_pie_chart(float_analysis: Dict[str, Dict]) -> str:
    """Create chart: Liquidity Rating Distribution"""
    
    liquidity_ratings = [float_analysis[comp]['liquidity_rating'] for comp in float_analysis.keys()]
    rating_counts = {}
    for rating in liquidity_ratings:
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    if not rating_counts:
        return ""
    
    labels = list(rating_counts.keys())
    values = list(rating_counts.values())
    
    liquidity_colors = {
        'Excellent': '#059669',
        'Good': '#10b981',
        'Fair': '#f59e0b',
        'Poor': '#fb923c',
        'Very Poor': '#ef4444'
    }
    colors = [liquidity_colors.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            'textinfo': 'label+percent',
            'textposition': 'auto'
        }],
        'layout': {
            'title': {'text': 'Portfolio Liquidity Rating Distribution', 'font': {'size': 16, 'weight': 'bold'}},
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': -0.2, 'xanchor': 'center', 'x': 0.5}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="liquidity-rating-pie", height=500)


def _create_ownership_float_dual_chart(float_analysis: Dict[str, Dict]) -> str:
    """Create chart: Institutional Ownership vs Float (Dual Axis)"""
    
    companies = list(float_analysis.keys())
    institutional_pcts = [float(float_analysis[comp]['institutional_ownership_pct']) for comp in companies]
    float_pcts = [float(float_analysis[comp]['estimated_float_pct']) for comp in companies]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'x': [comp[:12] for comp in companies],
                'y': institutional_pcts,
                'name': 'Institutional %',
                'marker': {'color': '#3b82f6'},
                'yaxis': 'y',
                'hovertemplate': '<b>%{x}</b><br>Institutional: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'x': [comp[:12] for comp in companies],
                'y': float_pcts,
                'name': 'Float %',
                'marker': {'color': '#ef4444'},
                'yaxis': 'y2',
                'hovertemplate': '<b>%{x}</b><br>Float: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Institutional Ownership vs Float Analysis', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {
                'title': 'Institutional Ownership (%)',
                'side': 'left',
                'showgrid': False
            },
            'yaxis2': {
                'title': 'Estimated Float (%)',
                'side': 'right',
                'overlaying': 'y',
                'showgrid': False
            },
            'barmode': 'group',
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ownership-float-dual", height=500)


# =============================================================================
# HELPER FUNCTIONS - MOMENTUM ANALYSIS
# =============================================================================

def _generate_ownership_momentum_analysis(institutional_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Generate comprehensive ownership momentum and investment flow analysis"""
    
    if institutional_df.empty:
        return {}
    
    momentum_analysis = {}
    
    for company_name, ticker in companies.items():
        company_data = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if company_data.empty or len(company_data) < 2:
            continue
        
        company_data = company_data.sort_values('date')
        latest = company_data.iloc[-1]
        previous = company_data.iloc[-2]
        
        ownership_change_pp = latest.get('ownershipPercentChange', 0) or 0
        total_invested_change_pct = latest.get('totalInvestedChange', 0) or 0
        investor_count_change = (latest.get('investorsHolding', 0) or 0) - (previous.get('investorsHolding', 0) or 0)
        
        momentum_score = _calculate_momentum_score_enhanced(
            ownership_change_pp, total_invested_change_pct, investor_count_change
        )
        
        flow_direction, flow_strength = _assess_flow_characteristics_enhanced(
            ownership_change_pp, total_invested_change_pct, investor_count_change
        )
        
        if momentum_score >= 8:
            momentum_rating = "Very Strong"
        elif momentum_score >= 6:
            momentum_rating = "Strong"
        elif momentum_score >= 4:
            momentum_rating = "Moderate"
        elif momentum_score >= 2:
            momentum_rating = "Weak"
        else:
            momentum_rating = "Very Weak"
        
        momentum_analysis[company_name] = {
            'ticker': ticker,
            'latest_ownership_pct': latest.get('ownershipPercent', 0) or 0,
            'ownership_change_pp': ownership_change_pp,
            'total_invested_change_pct': total_invested_change_pct,
            'investor_count_change': investor_count_change,
            'momentum_score': momentum_score,
            'flow_direction': flow_direction,
            'flow_strength': flow_strength,
            'momentum_rating': momentum_rating
        }
    
    return momentum_analysis


def _calculate_momentum_score_enhanced(ownership_change_pp: float, total_invested_change_pct: float, 
                                     investor_count_change: int) -> float:
    """Enhanced momentum score calculation with weighted components"""
    
    # Ownership change component (0-3 points)
    if ownership_change_pp > 3:
        ownership_component = 3
    elif ownership_change_pp > 1:
        ownership_component = 2.5
    elif ownership_change_pp > 0:
        ownership_component = 2
    elif ownership_change_pp > -1:
        ownership_component = 1
    elif ownership_change_pp > -3:
        ownership_component = 0.5
    else:
        ownership_component = 0
    
    # Investment change component (0-4 points)
    if total_invested_change_pct > 25:
        investment_component = 4
    elif total_invested_change_pct > 15:
        investment_component = 3.5
    elif total_invested_change_pct > 5:
        investment_component = 3
    elif total_invested_change_pct > 0:
        investment_component = 2
    elif total_invested_change_pct > -5:
        investment_component = 1
    elif total_invested_change_pct > -15:
        investment_component = 0.5
    else:
        investment_component = 0
    
    # Investor count component (0-3 points)
    if investor_count_change > 8:
        investor_component = 3
    elif investor_count_change > 3:
        investor_component = 2.5
    elif investor_count_change > 0:
        investor_component = 2
    elif investor_count_change >= -1:
        investor_component = 1
    elif investor_count_change >= -3:
        investor_component = 0.5
    else:
        investor_component = 0
    
    momentum_score = ownership_component + investment_component + investor_component
    return min(10, momentum_score)


def _assess_flow_characteristics_enhanced(ownership_change_pp: float, total_invested_change_pct: float, 
                                        investor_count_change: int) -> Tuple[str, str]:
    """Enhanced flow direction and strength assessment"""
    
    positive_signals = 0
    signal_strength = 0
    
    if ownership_change_pp > 1:
        positive_signals += 1
        signal_strength += abs(ownership_change_pp)
    elif ownership_change_pp < -1:
        signal_strength += abs(ownership_change_pp)
    
    if total_invested_change_pct > 5:
        positive_signals += 1
        signal_strength += abs(total_invested_change_pct) / 5
    elif total_invested_change_pct < -5:
        signal_strength += abs(total_invested_change_pct) / 5
    
    if investor_count_change > 1:
        positive_signals += 1
        signal_strength += investor_count_change
    elif investor_count_change < -1:
        signal_strength += abs(investor_count_change)
    
    if positive_signals >= 2:
        direction = "Inflow"
    elif positive_signals == 1:
        direction = "Mixed"
    else:
        direction = "Outflow"
    
    if signal_strength > 15:
        strength = "Strong"
    elif signal_strength > 5:
        strength = "Moderate"
    else:
        strength = "Weak"
    
    return direction, strength


def _generate_momentum_analysis_summary(momentum_analysis: Dict[str, Dict]) -> str:
    """Generate ownership momentum analysis summary"""
    
    total_companies = len(momentum_analysis)
    
    if total_companies == 0:
        return "No ownership momentum data available."
    
    very_strong = sum(1 for analysis in momentum_analysis.values() if analysis['momentum_rating'] == 'Very Strong')
    strong = sum(1 for analysis in momentum_analysis.values() if analysis['momentum_rating'] == 'Strong')
    weak = sum(1 for analysis in momentum_analysis.values() if analysis['momentum_rating'] in ['Weak', 'Very Weak'])
    
    inflow_companies = sum(1 for analysis in momentum_analysis.values() if analysis['flow_direction'] == 'Inflow')
    outflow_companies = sum(1 for analysis in momentum_analysis.values() if analysis['flow_direction'] == 'Outflow')
    
    avg_ownership_change = np.mean([analysis['ownership_change_pp'] for analysis in momentum_analysis.values()])
    avg_invested_change = np.mean([analysis['total_invested_change_pct'] for analysis in momentum_analysis.values()])
    avg_momentum_score = np.mean([analysis['momentum_score'] for analysis in momentum_analysis.values()])
    
    return f"""<strong>Ownership Momentum Analysis Summary:</strong><br><br>
• Portfolio Momentum Profile: {very_strong + strong} companies with strong momentum, {weak} with weak momentum across {total_companies} companies<br>
• Flow Direction: {inflow_companies} companies experiencing inflows, {outflow_companies} experiencing outflows<br>
• Investment Changes: {avg_ownership_change:+.1f}pp average ownership change, {avg_invested_change:+.1f}% average investment change<br>
• Momentum Score: {avg_momentum_score:.1f}/10 indicating {'strong' if avg_momentum_score >= 6 else 'moderate' if avg_momentum_score >= 4 else 'weak'} institutional momentum<br><br>
<strong>Smart Money Direction:</strong> {'Strong institutional accumulation' if inflow_companies >= total_companies * 0.6 else 'Selective institutional interest' if inflow_companies > outflow_companies else 'Mixed institutional sentiment'} across portfolio"""


# =============================================================================
# HELPER FUNCTIONS - FLOAT ANALYSIS
# =============================================================================

def _generate_float_analysis(institutional_df: pd.DataFrame, companies: Dict[str, str], 
                           df: pd.DataFrame, prices_df: pd.DataFrame) -> Dict[str, Dict]:
    """Generate comprehensive float analysis and liquidity assessment"""
    
    if institutional_df.empty:
        return {}
    
    float_analysis = {}
    
    for company_name, ticker in companies.items():
        company_institutional = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if company_institutional.empty:
            continue
        
        latest_institutional = company_institutional.sort_values('date').iloc[-1]
        institutional_ownership_pct = latest_institutional.get('ownershipPercent', 0) or 0
        
        company_financial = df[df['Company'] == company_name]
        market_cap = 0
        if not company_financial.empty:
            latest_financial = company_financial.sort_values('Year').iloc[-1]
            market_cap = latest_financial.get('marketCap', 0) or 0
        
        estimated_insider_pct = 12
        estimated_float_pct = max(15, 100 - institutional_ownership_pct - estimated_insider_pct)
        
        float_turnover_annual = 0
        if not prices_df.empty:
            company_prices = prices_df[prices_df['Symbol'] == company_name].copy()
            if not company_prices.empty and 'volume' in company_prices.columns:
                recent_prices = company_prices.tail(252)
                if not recent_prices.empty:
                    avg_daily_volume = recent_prices['volume'].mean()
                    institutional_shares = latest_institutional.get('numberOf13Fshares', 0) or 0
                    if institutional_shares > 0 and institutional_ownership_pct > 0:
                        estimated_shares_outstanding = institutional_shares / (institutional_ownership_pct / 100)
                        estimated_float_shares = estimated_shares_outstanding * (estimated_float_pct / 100)
                        
                        if estimated_float_shares > 0:
                            daily_turnover = avg_daily_volume / estimated_float_shares
                            float_turnover_annual = daily_turnover * 252
        
        liquidity_score = _calculate_liquidity_score_enhanced(
            estimated_float_pct, float_turnover_annual, institutional_ownership_pct, market_cap
        )
        
        concentration_risk = _assess_concentration_risk_float(
            institutional_ownership_pct, estimated_float_pct, latest_institutional.get('investorsHolding', 0) or 0
        )
        
        trading_liquidity = _assess_trading_liquidity(float_turnover_annual, estimated_float_pct, market_cap)
        liquidity_rating = _determine_liquidity_rating(liquidity_score, concentration_risk, trading_liquidity)
        
        float_analysis[company_name] = {
            'ticker': ticker,
            'institutional_ownership_pct': institutional_ownership_pct,
            'estimated_float_pct': estimated_float_pct,
            'float_turnover_annual': float_turnover_annual,
            'liquidity_score': liquidity_score,
            'concentration_risk': concentration_risk,
            'trading_liquidity': trading_liquidity,
            'liquidity_rating': liquidity_rating,
            'market_cap_billions': market_cap / 1_000_000_000 if market_cap > 0 else 0
        }
    
    return float_analysis


def _calculate_liquidity_score_enhanced(estimated_float_pct: float, float_turnover_annual: float, 
                                      institutional_ownership_pct: float, market_cap: float) -> float:
    """Enhanced liquidity score calculation"""
    
    if estimated_float_pct >= 60:
        float_component = 2.5
    elif estimated_float_pct >= 40:
        float_component = 2
    elif estimated_float_pct >= 25:
        float_component = 1.5
    elif estimated_float_pct >= 15:
        float_component = 1
    else:
        float_component = 0.5
    
    if float_turnover_annual >= 4:
        turnover_component = 3
    elif float_turnover_annual >= 2:
        turnover_component = 2.5
    elif float_turnover_annual >= 1:
        turnover_component = 2
    elif float_turnover_annual >= 0.5:
        turnover_component = 1.5
    elif float_turnover_annual >= 0.25:
        turnover_component = 1
    else:
        turnover_component = 0.5
    
    market_cap_billions = market_cap / 1_000_000_000 if market_cap > 0 else 0
    if market_cap_billions >= 50:
        market_cap_component = 2.5
    elif market_cap_billions >= 10:
        market_cap_component = 2
    elif market_cap_billions >= 2:
        market_cap_component = 1.5
    elif market_cap_billions >= 0.5:
        market_cap_component = 1
    else:
        market_cap_component = 0.5
    
    if 30 <= institutional_ownership_pct <= 70:
        ownership_component = 2
    elif 20 <= institutional_ownership_pct <= 80:
        ownership_component = 1.5
    elif 15 <= institutional_ownership_pct <= 85:
        ownership_component = 1
    else:
        ownership_component = 0.5
    
    liquidity_score = float_component + turnover_component + market_cap_component + ownership_component
    return min(10, liquidity_score)


def _assess_concentration_risk_float(institutional_ownership_pct: float, estimated_float_pct: float, 
                                   investor_count: int) -> str:
    """Enhanced concentration risk assessment for float analysis"""
    
    risk_score = 0
    
    if institutional_ownership_pct > 85:
        risk_score += 4
    elif institutional_ownership_pct > 75:
        risk_score += 3
    elif institutional_ownership_pct > 65:
        risk_score += 2
    elif institutional_ownership_pct > 50:
        risk_score += 1
    
    if estimated_float_pct < 20:
        risk_score += 3
    elif estimated_float_pct < 30:
        risk_score += 2
    elif estimated_float_pct < 40:
        risk_score += 1
    
    if investor_count < 10:
        risk_score += 2
    elif investor_count < 20:
        risk_score += 1
    
    if risk_score >= 7:
        return "Very High"
    elif risk_score >= 5:
        return "High"
    elif risk_score >= 3:
        return "Moderate"
    else:
        return "Low"


def _assess_trading_liquidity(float_turnover_annual: float, estimated_float_pct: float, market_cap: float) -> str:
    """Assess trading liquidity based on multiple factors"""
    
    liquidity_factors = 0
    
    if float_turnover_annual >= 3:
        liquidity_factors += 3
    elif float_turnover_annual >= 1.5:
        liquidity_factors += 2
    elif float_turnover_annual >= 0.75:
        liquidity_factors += 1
    
    if estimated_float_pct >= 50:
        liquidity_factors += 2
    elif estimated_float_pct >= 30:
        liquidity_factors += 1
    
    market_cap_billions = market_cap / 1_000_000_000 if market_cap > 0 else 0
    if market_cap_billions >= 10:
        liquidity_factors += 2
    elif market_cap_billions >= 2:
        liquidity_factors += 1
    
    if liquidity_factors >= 6:
        return "High"
    elif liquidity_factors >= 4:
        return "Good"
    elif liquidity_factors >= 2:
        return "Moderate"
    else:
        return "Low"


def _determine_liquidity_rating(liquidity_score: float, concentration_risk: str, trading_liquidity: str) -> str:
    """Determine overall liquidity rating"""
    
    base_rating = 0
    
    if liquidity_score >= 8:
        base_rating = 4
    elif liquidity_score >= 6:
        base_rating = 3
    elif liquidity_score >= 4:
        base_rating = 2
    else:
        base_rating = 1
    
    if concentration_risk == "Very High":
        base_rating -= 2
    elif concentration_risk == "High":
        base_rating -= 1
    elif concentration_risk == "Low":
        base_rating += 1
    
    if trading_liquidity == "High":
        base_rating += 1
    elif trading_liquidity == "Low":
        base_rating -= 1
    
    base_rating = max(1, min(5, base_rating))
    
    if base_rating >= 5:
        return "Excellent"
    elif base_rating >= 4:
        return "Good"
    elif base_rating >= 3:
        return "Fair"
    elif base_rating >= 2:
        return "Poor"
    else:
        return "Very Poor"


def _generate_float_analysis_summary(float_analysis: Dict[str, Dict]) -> str:
    """Generate float analysis summary"""
    
    total_companies = len(float_analysis)
    
    if total_companies == 0:
        return "No float analysis data available."
    
    excellent_liquidity = sum(1 for analysis in float_analysis.values() if analysis['liquidity_rating'] == 'Excellent')
    good_liquidity = sum(1 for analysis in float_analysis.values() if analysis['liquidity_rating'] == 'Good')
    poor_liquidity = sum(1 for analysis in float_analysis.values() if analysis['liquidity_rating'] in ['Poor', 'Very Poor'])
    
    very_high_risk = sum(1 for analysis in float_analysis.values() if analysis['concentration_risk'] == 'Very High')
    low_risk = sum(1 for analysis in float_analysis.values() if analysis['concentration_risk'] == 'Low')
    
    avg_float = np.mean([analysis['estimated_float_pct'] for analysis in float_analysis.values()])
    avg_turnover = np.mean([analysis['float_turnover_annual'] for analysis in float_analysis.values()])
    avg_liquidity_score = np.mean([analysis['liquidity_score'] for analysis in float_analysis.values()])
    
    return f"""<strong>Float Analysis & Liquidity Assessment Summary:</strong><br><br>
• Portfolio Liquidity: {excellent_liquidity} companies with excellent liquidity, {poor_liquidity} with poor liquidity across {total_companies} companies<br>
• Float Characteristics: {avg_float:.1f}% average estimated float with {avg_turnover:.1f}x annual turnover<br>
• Concentration Risk: {very_high_risk} companies with very high risk, {low_risk} with low concentration risk<br>
• Liquidity Score: {avg_liquidity_score:.1f}/10 indicating {'excellent' if avg_liquidity_score >= 8 else 'good' if avg_liquidity_score >= 6 else 'moderate'} portfolio liquidity<br><br>
<strong>Liquidity Intelligence:</strong> {'High portfolio liquidity' if excellent_liquidity >= total_companies * 0.5 else 'Good portfolio liquidity' if good_liquidity >= total_companies * 0.4 else 'Mixed liquidity profile'} for optimal position management"""



# =============================================================================
# SUBSECTION 13E: COMPREHENSIVE INSTITUTIONAL VISUALIZATION SUITE
# =============================================================================

def _build_section_13e(institutional_df: pd.DataFrame, companies: Dict[str, str],
                      ownership_flow: Dict, quality_metrics: Dict,
                      momentum_analysis: Dict, float_analysis: Dict) -> str:
    """Build subsection 13E: Comprehensive Institutional Visualization Suite"""
    
    if institutional_df.empty:
        return build_info_box(
            "Institutional visualization suite unavailable due to insufficient data.",
            "warning",
            "13E. Institutional Visualization Dashboard"
        )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-13e')">
            <h2>13E. Comprehensive Institutional Visualization Dashboard</h2>
            <span class="toggle-icon" id="icon-section-13e">▼</span>
        </div>
        <div class="subsection-content" id="section-13e">
    """
    
    html += "<h3>Ownership Trends Analysis</h3>"
    html += "<p>Time-series analysis of institutional ownership evolution across portfolio companies.</p>"
    
    # Chart 1: Ownership Percentage Trends
    html += _create_ownership_percentage_trends(institutional_df, companies)
    
    # Chart 2: Investor Count Trends
    html += _create_investor_count_trends(institutional_df, companies)
    
    # Chart 3: Total Investment Trends
    html += _create_total_investment_trends(institutional_df, companies)
    
    # Chart 4: Portfolio Average Metrics
    html += _create_portfolio_average_metrics(institutional_df)
    
    html += build_section_divider()
    html += "<h3>Comprehensive Institutional Intelligence Dashboard</h3>"
    html += "<p>Executive-level institutional analysis with strategic insights across all metrics.</p>"
    
    # Chart 5: Portfolio Summary Metrics
    html += _create_portfolio_summary_metrics(ownership_flow, quality_metrics, momentum_analysis, float_analysis, companies)
    
    # Chart 6: Flow Direction Summary
    if ownership_flow:
        html += _create_flow_direction_summary(ownership_flow)
    
    # Chart 7: Quality vs Momentum Matrix
    if quality_metrics and momentum_analysis:
        html += _create_quality_momentum_matrix(quality_metrics, momentum_analysis)
    
    # Chart 8: Concentration Risk Analysis
    if quality_metrics:
        html += _create_concentration_risk_dashboard(quality_metrics)
    
    # Chart 9: Portfolio Intelligence Score
    html += _create_portfolio_intelligence_gauge(ownership_flow, quality_metrics, momentum_analysis, float_analysis)
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# OWNERSHIP TRENDS CHARTS (4 charts)
# =============================================================================

def _create_ownership_percentage_trends(institutional_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Create chart: Ownership Percentage Trends Over Time"""
    
    traces = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#ff6b6b', '#45b7d1', '#96ceb4', '#ffa07a']
    
    for i, (company_name, ticker) in enumerate(list(companies.items())[:6]):  # Limit to 6 for readability
        company_data = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if not company_data.empty:
            company_data = company_data.sort_values('date')
            dates = [str(d)[:10] for d in company_data['date'].tolist()]
            ownership_pcts = [float(x) if pd.notna(x) else 0 for x in company_data['ownershipPercent'].tolist()]
            
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': dates,
                'y': ownership_pcts,
                'name': company_name[:12],
                'line': {'color': colors[i % len(colors)], 'width': 2},
                'marker': {'size': 6},
                'hovertemplate': f'<b>{company_name[:12]}</b><br>Date: %{{x}}<br>Ownership: %{{y:.1f}}%<extra></extra>'
            })
    
    if not traces:
        return ""
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Institutional Ownership Percentage Trends', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Date', 'type': 'date'},
            'yaxis': {'title': 'Institutional Ownership (%)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'v', 'yanchor': 'top', 'y': 1, 'xanchor': 'left', 'x': 1.02}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="ownership-percentage-trends", height=500)


def _create_investor_count_trends(institutional_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Create chart: Investor Count Trends Over Time"""
    
    traces = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#ff6b6b', '#45b7d1', '#96ceb4', '#ffa07a']
    
    for i, (company_name, ticker) in enumerate(list(companies.items())[:6]):
        company_data = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if not company_data.empty:
            company_data = company_data.sort_values('date')
            dates = [str(d)[:10] for d in company_data['date'].tolist()]
            investor_counts = [int(x) if pd.notna(x) else 0 for x in company_data['investorsHolding'].tolist()]
            
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': dates,
                'y': investor_counts,
                'name': company_name[:12],
                'line': {'color': colors[i % len(colors)], 'width': 2},
                'marker': {'size': 6, 'symbol': 'square'},
                'hovertemplate': f'<b>{company_name[:12]}</b><br>Date: %{{x}}<br>Investors: %{{y}}<extra></extra>'
            })
    
    if not traces:
        return ""
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Institutional Investor Count Trends', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Date', 'type': 'date'},
            'yaxis': {'title': 'Number of Institutional Investors'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'v', 'yanchor': 'top', 'y': 1, 'xanchor': 'left', 'x': 1.02}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="investor-count-trends", height=500)


def _create_total_investment_trends(institutional_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Create chart: Total Investment Trends Over Time"""
    
    traces = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#4ecdc4', '#ff6b6b', '#45b7d1', '#96ceb4', '#ffa07a']
    
    for i, (company_name, ticker) in enumerate(list(companies.items())[:6]):
        company_data = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if not company_data.empty:
            company_data = company_data.sort_values('date')
            dates = [str(d)[:10] for d in company_data['date'].tolist()]
            total_invested = [float(x) / 1e9 if pd.notna(x) else 0 for x in company_data['totalInvested'].tolist()]
            
            traces.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': dates,
                'y': total_invested,
                'name': company_name[:12],
                'line': {'color': colors[i % len(colors)], 'width': 2},
                'marker': {'size': 6, 'symbol': 'diamond'},
                'hovertemplate': f'<b>{company_name[:12]}</b><br>Date: %{{x}}<br>Investment: $%{{y:.2f}}B<extra></extra>'
            })
    
    if not traces:
        return ""
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': 'Total Institutional Investment Trends', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Date', 'type': 'date'},
            'yaxis': {'title': 'Total Institutional Investment ($B)'},
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'v', 'yanchor': 'top', 'y': 1, 'xanchor': 'left', 'x': 1.02}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="total-investment-trends", height=500)


def _create_portfolio_average_metrics(institutional_df: pd.DataFrame) -> str:
    """Create chart: Portfolio Average Metrics Over Time"""
    
    if institutional_df.empty:
        return ""
    
    # Calculate portfolio averages by date
    portfolio_by_date = institutional_df.groupby('date').agg({
        'ownershipPercent': 'mean',
        'investorsHolding': 'mean',
        'totalInvested': 'sum'
    }).reset_index()
    
    portfolio_by_date = portfolio_by_date.sort_values('date')
    dates = [str(d)[:10] for d in portfolio_by_date['date'].tolist()]
    avg_ownership = [float(x) if pd.notna(x) else 0 for x in portfolio_by_date['ownershipPercent'].tolist()]
    avg_investors = [float(x) if pd.notna(x) else 0 for x in portfolio_by_date['investorsHolding'].tolist()]
    
    fig_data = {
        'data': [
            {
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': dates,
                'y': avg_ownership,
                'name': 'Avg Ownership %',
                'line': {'color': '#3b82f6', 'width': 3},
                'marker': {'size': 8},
                'yaxis': 'y',
                'hovertemplate': '<b>Avg Ownership</b><br>Date: %{x}<br>Ownership: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'scatter',
                'mode': 'lines+markers',
                'x': dates,
                'y': avg_investors,
                'name': 'Avg Investor Count',
                'line': {'color': '#ef4444', 'width': 3},
                'marker': {'size': 8, 'symbol': 'square'},
                'yaxis': 'y2',
                'hovertemplate': '<b>Avg Investors</b><br>Date: %{x}<br>Count: %{y:.0f}<extra></extra>'
            }
        ],
        'layout': {
            'title': {'text': 'Portfolio Average Institutional Metrics', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Date', 'type': 'date'},
            'yaxis': {
                'title': 'Average Ownership (%)',
                'side': 'left',
                'showgrid': True
            },
            'yaxis2': {
                'title': 'Average Investor Count',
                'side': 'right',
                'overlaying': 'y',
                'showgrid': False
            },
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="portfolio-average-metrics", height=500)


# =============================================================================
# COMPREHENSIVE DASHBOARD CHARTS (5 charts)
# =============================================================================

def _create_portfolio_summary_metrics(ownership_flow: Dict, quality_metrics: Dict,
                                     momentum_analysis: Dict, float_analysis: Dict,
                                     companies: Dict[str, str]) -> str:
    """Create chart: Portfolio Summary Metrics Bar Chart"""
    
    # Calculate portfolio-level metrics
    avg_quality_score = 0
    avg_ownership_pct = 0
    avg_investors = 0
    if quality_metrics:
        avg_quality_score = np.mean([m['quality_score'] for m in quality_metrics.values()])
        avg_ownership_pct = np.mean([m['ownership_percentage'] for m in quality_metrics.values()])
        avg_investors = np.mean([m['investors_holding'] for m in quality_metrics.values()])
    
    avg_momentum_score = 0
    if momentum_analysis:
        avg_momentum_score = np.mean([m['momentum_score'] for m in momentum_analysis.values()])
    
    avg_liquidity_score = 0
    if float_analysis:
        avg_liquidity_score = np.mean([f['liquidity_score'] for f in float_analysis.values()])
    
    # Prepare data
    metrics = ['Quality\nScore', 'Ownership\n(%)', 'Investors\n(scaled)', 'Momentum\nScore', 'Liquidity\nScore']
    values = [
        float(avg_quality_score),
        float(avg_ownership_pct / 10),  # Scale to 0-10 for visualization
        float(avg_investors / 10),  # Scale investors for visualization
        float(avg_momentum_score),
        float(avg_liquidity_score)
    ]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA07A']
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': metrics,
            'y': values,
            'marker': {'color': colors},
            'text': [f'{avg_quality_score:.1f}', f'{avg_ownership_pct:.1f}%', 
                    f'{avg_investors:.0f}', f'{avg_momentum_score:.1f}', f'{avg_liquidity_score:.1f}'],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Value: %{text}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Portfolio Institutional Ownership Dashboard', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Metrics'},
            'yaxis': {'title': 'Score (0-10 scale)', 'range': [0, 12]},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="portfolio-summary-metrics", height=500)


def _create_flow_direction_summary(ownership_flow: Dict) -> str:
    """Create chart: Flow Direction Summary Pie Chart"""
    
    flow_directions = [flow['flow_direction'] for flow in ownership_flow.values()]
    direction_counts = {}
    for direction in flow_directions:
        direction_counts[direction] = direction_counts.get(direction, 0) + 1
    
    if not direction_counts:
        return ""
    
    labels = list(direction_counts.keys())
    values = list(direction_counts.values())
    
    flow_colors = {
        'Strong Inflow': '#059669',
        'Moderate Inflow': '#10b981',
        'Balanced': '#f59e0b',
        'Moderate Outflow': '#fb923c',
        'Strong Outflow': '#ef4444'
    }
    colors = [flow_colors.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            'textinfo': 'label+percent',
            'textposition': 'auto',
            'hole': 0.4
        }],
        'layout': {
            'title': {'text': 'Portfolio Flow Direction Summary', 'font': {'size': 16, 'weight': 'bold'}},
            'showlegend': True,
            'legend': {'orientation': 'v', 'yanchor': 'middle', 'y': 0.5, 'xanchor': 'left', 'x': 1.02},
            'annotations': [{
                'text': f'{len(ownership_flow)}<br>Companies',
                'x': 0.5,
                'y': 0.5,
                'font': {'size': 16, 'weight': 'bold'},
                'showarrow': False
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="flow-direction-summary", height=500)


def _create_quality_momentum_matrix(quality_metrics: Dict, momentum_analysis: Dict) -> str:
    """Create chart: Quality vs Momentum Matrix (Bubble Chart)"""
    
    # Get common companies
    common_companies = [comp for comp in quality_metrics.keys() if comp in momentum_analysis]
    
    if not common_companies:
        return ""
    
    quality_scores = [float(quality_metrics[comp]['quality_score']) for comp in common_companies]
    momentum_scores = [float(momentum_analysis[comp]['momentum_score']) for comp in common_companies]
    ownership_pcts = [float(quality_metrics[comp]['ownership_percentage']) for comp in common_companies]
    
    # Bubble sizes based on ownership percentage
    bubble_sizes = [max(8, pct * 0.5) for pct in ownership_pcts]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'x': quality_scores,
            'y': momentum_scores,
            'mode': 'markers+text',
            'marker': {
                'size': bubble_sizes,
                'color': momentum_scores,
                'colorscale': 'RdYlGn',
                'showscale': True,
                'colorbar': {'title': 'Momentum'},
                'line': {'color': 'white', 'width': 2}
            },
            'text': [comp[:8] for comp in common_companies],
            'textposition': 'top center',
            'textfont': {'size': 9},
            'hovertemplate': '<b>%{text}</b><br>Quality: %{x:.1f}<br>Momentum: %{y:.1f}<br>Ownership: ' + 
                           '<br>'.join([f'{comp[:8]}: {pct:.1f}%' for comp, pct in zip(common_companies, ownership_pcts)]) +
                           '<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Quality vs Momentum Matrix (Bubble Size = Ownership %)', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Institutional Quality Score (0-10)', 'range': [0, 11]},
            'yaxis': {'title': 'Momentum Score (0-10)', 'range': [0, 11]},
            'shapes': [
                {
                    'type': 'line',
                    'x0': 5,
                    'x1': 5,
                    'y0': 0,
                    'y1': 10,
                    'line': {'color': 'gray', 'width': 1, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': 10,
                    'y0': 5,
                    'y1': 5,
                    'line': {'color': 'gray', 'width': 1, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {'x': 7.5, 'y': 7.5, 'text': 'Leaders', 'showarrow': False, 'font': {'size': 12, 'color': 'green'}},
                {'x': 2.5, 'y': 7.5, 'text': 'Momentum', 'showarrow': False, 'font': {'size': 12, 'color': 'blue'}},
                {'x': 7.5, 'y': 2.5, 'text': 'Stable', 'showarrow': False, 'font': {'size': 12, 'color': 'orange'}},
                {'x': 2.5, 'y': 2.5, 'text': 'Watch', 'showarrow': False, 'font': {'size': 12, 'color': 'red'}}
            ],
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="quality-momentum-matrix", height=600)


def _create_concentration_risk_dashboard(quality_metrics: Dict) -> str:
    """Create chart: Concentration Risk Analysis"""
    
    companies = list(quality_metrics.keys())
    hhi_values = [float(quality_metrics[comp]['estimated_hhi']) for comp in companies]
    concentration_risks = [quality_metrics[comp]['concentration_risk'] for comp in companies]
    
    # Color by concentration risk
    risk_colors_map = {
        'Low': '#10b981',
        'Moderate': '#f59e0b',
        'High': '#fb923c',
        'Very High': '#ef4444'
    }
    bar_colors = [risk_colors_map.get(risk, '#94a3b8') for risk in concentration_risks]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in companies],
            'y': hhi_values,
            'marker': {'color': bar_colors},
            'text': concentration_risks,
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>HHI: %{y:.0f}<br>Risk: %{text}<extra></extra>'
        }],
        'layout': {
            'title': {'text': 'Portfolio Concentration Risk Analysis (HHI)', 'font': {'size': 16, 'weight': 'bold'}},
            'xaxis': {'title': 'Companies'},
            'yaxis': {'title': 'Estimated HHI'},
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 1500,
                    'y1': 1500,
                    'line': {'color': '#f59e0b', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(companies) - 0.5,
                    'y0': 2500,
                    'y1': 2500,
                    'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {
                    'x': len(companies) - 1,
                    'y': 1500,
                    'xanchor': 'right',
                    'yanchor': 'bottom',
                    'text': 'Moderate Threshold (1500)',
                    'showarrow': False,
                    'font': {'color': '#f59e0b', 'size': 10}
                },
                {
                    'x': len(companies) - 1,
                    'y': 2500,
                    'xanchor': 'right',
                    'yanchor': 'bottom',
                    'text': 'High Threshold (2500)',
                    'showarrow': False,
                    'font': {'color': '#ef4444', 'size': 10}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="concentration-risk-dashboard", height=500)


def _create_portfolio_intelligence_gauge(ownership_flow: Dict, quality_metrics: Dict,
                                        momentum_analysis: Dict, float_analysis: Dict) -> str:
    """Create chart: Portfolio Institutional Intelligence Score (Gauge)"""
    
    # Calculate overall institutional intelligence score
    intelligence_components = []
    
    if quality_metrics:
        avg_quality = np.mean([m['quality_score'] for m in quality_metrics.values()])
        intelligence_components.append(float(avg_quality / 10))
    
    if momentum_analysis:
        avg_momentum = np.mean([m['momentum_score'] for m in momentum_analysis.values()])
        intelligence_components.append(float(avg_momentum / 10))
    
    if float_analysis:
        avg_liquidity = np.mean([f['liquidity_score'] for f in float_analysis.values()])
        intelligence_components.append(float(avg_liquidity / 10))
    
    if ownership_flow:
        inflow_ratio = sum(1 for flow in ownership_flow.values() 
                         if 'Inflow' in flow['flow_direction']) / len(ownership_flow)
        intelligence_components.append(float(inflow_ratio))
    
    if intelligence_components:
        institutional_intelligence_score = np.mean(intelligence_components) * 10
    else:
        institutional_intelligence_score = 5
    
    # Determine color
    if institutional_intelligence_score >= 7:
        gauge_color = '#059669'
        rating = 'Excellent'
    elif institutional_intelligence_score >= 5:
        gauge_color = '#f59e0b'
        rating = 'Good'
    else:
        gauge_color = '#ef4444'
        rating = 'Fair'
    
    fig_data = {
        'data': [{
            'type': 'indicator',
            'mode': 'gauge+number+delta',
            'value': float(institutional_intelligence_score),
            'title': {'text': 'Portfolio Institutional Intelligence Score', 'font': {'size': 18}},
            'delta': {'reference': 5, 'increasing': {'color': 'green'}},
            'gauge': {
                'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': 'darkblue'},
                'bar': {'color': gauge_color},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 3], 'color': '#fee2e2'},
                    {'range': [3, 5], 'color': '#fef3c7'},
                    {'range': [5, 7], 'color': '#dbeafe'},
                    {'range': [7, 10], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 9
                }
            }
        }],
        'layout': {
            'height': 400,
            'annotations': [{
                'text': f'Rating: {rating}',
                'x': 0.5,
                'y': 0.1,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 16, 'weight': 'bold', 'color': gauge_color},
                'showarrow': False
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="portfolio-intelligence-gauge", height=400)


# =============================================================================
# SUBSECTION 13F: STRATEGIC INSTITUTIONAL INTELLIGENCE & SMART MONEY ANALYSIS
# =============================================================================

def _build_section_13f(ownership_flow: Dict, quality_metrics: Dict,
                      momentum_analysis: Dict, float_analysis: Dict,
                      companies: Dict[str, str]) -> str:
    """Build subsection 13F: Strategic Institutional Intelligence & Smart Money Analysis"""
    
    if not ownership_flow and not quality_metrics and not momentum_analysis and not float_analysis:
        return build_info_box(
            "Strategic institutional intelligence unavailable due to insufficient data.",
            "warning",
            "13F. Strategic Intelligence"
        )
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-13f')">
            <h2>13F. Strategic Institutional Intelligence & Investment Framework</h2>
            <span class="toggle-icon" id="icon-section-13f">▼</span>
        </div>
        <div class="subsection-content" id="section-13f">
    """
    
    # Generate strategic insights
    strategic_insights = _generate_comprehensive_institutional_intelligence(
        ownership_flow, quality_metrics, momentum_analysis, float_analysis, companies
    )
    
    # Executive Summary Cards
    html += _build_executive_summary_cards(ownership_flow, quality_metrics, momentum_analysis, float_analysis)
    
    # Tabbed Strategic Intelligence Sections
    html += _build_tabbed_strategic_sections(strategic_insights)
    
    # Investment Framework Timeline
    html += _build_investment_framework_timeline(strategic_insights, ownership_flow, quality_metrics, momentum_analysis)
    
    # Success Metrics Dashboard
    html += _build_success_metrics_dashboard(ownership_flow, quality_metrics, momentum_analysis, float_analysis, companies)
    
    # Action Priority Cards
    html += _build_action_priority_cards(ownership_flow, quality_metrics, momentum_analysis, float_analysis, companies)
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# EXECUTIVE SUMMARY CARDS
# =============================================================================

def _build_executive_summary_cards(ownership_flow: Dict, quality_metrics: Dict,
                                   momentum_analysis: Dict, float_analysis: Dict) -> str:
    """Build executive summary stat cards"""
    
    html = "<h3>📊 Executive Portfolio Intelligence Summary</h3>"
    
    # Calculate key metrics
    total_companies = len(ownership_flow) if ownership_flow else 0
    
    # Flow metrics
    strong_inflow = sum(1 for f in ownership_flow.values() if f['flow_direction'] == 'Strong Inflow') if ownership_flow else 0
    flow_score = np.mean([f['net_flow_score'] for f in ownership_flow.values()]) if ownership_flow else 0
    
    # Quality metrics
    excellent_quality = sum(1 for q in quality_metrics.values() if q['quality_rating'] == 'Excellent') if quality_metrics else 0
    avg_quality = np.mean([q['quality_score'] for q in quality_metrics.values()]) if quality_metrics else 0
    
    # Momentum metrics
    strong_momentum = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] in ['Very Strong', 'Strong']) if momentum_analysis else 0
    avg_momentum = np.mean([m['momentum_score'] for m in momentum_analysis.values()]) if momentum_analysis else 0
    
    # Liquidity metrics
    excellent_liquidity = sum(1 for l in float_analysis.values() if l['liquidity_rating'] == 'Excellent') if float_analysis else 0
    avg_liquidity = np.mean([l['liquidity_score'] for l in float_analysis.values()]) if float_analysis else 0
    
    # Overall intelligence score
    intelligence_score = _calculate_intelligence_score(flow_score, avg_quality, avg_momentum, avg_liquidity)
    
    cards = [
        {
            "label": "🎯 Portfolio Intelligence Score",
            "value": f"{intelligence_score:.1f}/10",
            "description": _get_intelligence_rating(intelligence_score),
            "type": "success" if intelligence_score >= 7 else "info" if intelligence_score >= 5 else "warning"
        },
        {
            "label": "📈 Smart Money Flow",
            "value": f"{strong_inflow}/{total_companies}",
            "description": f"Strong inflows ({flow_score:+.1f} net score)",
            "type": "success" if flow_score > 2 else "warning" if flow_score > -1 else "danger"
        },
        {
            "label": "⭐ Quality Excellence",
            "value": f"{excellent_quality}/{total_companies}",
            "description": f"Excellent quality ({avg_quality:.1f}/10 avg)",
            "type": "success" if avg_quality >= 7 else "info"
        },
        {
            "label": "🚀 Momentum Leaders",
            "value": f"{strong_momentum}/{total_companies}",
            "description": f"Strong momentum ({avg_momentum:.1f}/10 avg)",
            "type": "success" if avg_momentum >= 6 else "warning"
        },
        {
            "label": "💧 Liquidity Profile",
            "value": f"{excellent_liquidity}/{total_companies}",
            "description": f"Excellent liquidity ({avg_liquidity:.1f}/10 avg)",
            "type": "success" if avg_liquidity >= 7 else "info"
        },
        {
            "label": "🎓 Institutional Validation",
            "value": _get_validation_level(strong_inflow, total_companies, avg_quality),
            "description": "Smart money confidence level",
            "type": "success" if strong_inflow >= total_companies * 0.4 else "info"
        }
    ]
    
    html += build_stat_grid(cards)
    
    return html


def _calculate_intelligence_score(flow_score: float, avg_quality: float, 
                                  avg_momentum: float, avg_liquidity: float) -> float:
    """Calculate overall institutional intelligence score"""
    components = []
    
    # Normalize flow score to 0-10
    normalized_flow = min(10, max(0, (flow_score + 5) * 1.0))
    components.append(normalized_flow * 0.25)
    
    if avg_quality > 0:
        components.append(avg_quality * 0.30)
    
    if avg_momentum > 0:
        components.append(avg_momentum * 0.25)
    
    if avg_liquidity > 0:
        components.append(avg_liquidity * 0.20)
    
    return sum(components) if components else 5.0


def _get_intelligence_rating(score: float) -> str:
    """Get intelligence rating text"""
    if score >= 8:
        return "🌟 Outstanding Institutional Foundation"
    elif score >= 7:
        return "💪 Excellent Institutional Support"
    elif score >= 6:
        return "✅ Strong Institutional Base"
    elif score >= 5:
        return "📊 Good Institutional Quality"
    else:
        return "⚠️ Developing Institutional Profile"


def _get_validation_level(strong_inflow: int, total: int, avg_quality: float) -> str:
    """Get institutional validation level"""
    if strong_inflow >= total * 0.5 and avg_quality >= 7:
        return "Very High"
    elif strong_inflow >= total * 0.3 and avg_quality >= 6:
        return "High"
    elif strong_inflow >= total * 0.2:
        return "Moderate"
    else:
        return "Developing"


# =============================================================================
# TABBED STRATEGIC SECTIONS
# =============================================================================

def _build_tabbed_strategic_sections(strategic_insights: Dict[str, str]) -> str:
    """Build tabbed sections for strategic intelligence"""
    
    html = """
    <h3>🎯 Strategic Intelligence Analysis</h3>
    <div class="strategic-tabs">
        <div class="tab-buttons">
            <button class="tab-button active" onclick="openTab(event, 'flow-intel')">💰 Flow Intelligence</button>
            <button class="tab-button" onclick="openTab(event, 'quality-intel')">⭐ Quality Analysis</button>
            <button class="tab-button" onclick="openTab(event, 'momentum-intel')">🚀 Momentum Insights</button>
            <button class="tab-button" onclick="openTab(event, 'liquidity-intel')">💧 Liquidity Framework</button>
        </div>
    """
    
    # Tab 1: Flow Intelligence
    html += f"""
        <div id="flow-intel" class="tab-content active">
            <div class="insight-card">
                <h4>📊 Ownership Flow Intelligence & Smart Money Tracking</h4>
                {_format_insight_text(strategic_insights.get('ownership_intelligence', 'No data available.'))}
            </div>
        </div>
    """
    
    # Tab 2: Quality Analysis
    html += f"""
        <div id="quality-intel" class="tab-content">
            <div class="insight-card">
                <h4>⭐ Institutional Quality Assessment & Holder Analysis</h4>
                {_format_insight_text(strategic_insights.get('quality_intelligence', 'No data available.'))}
            </div>
        </div>
    """
    
    # Tab 3: Momentum Insights
    html += f"""
        <div id="momentum-intel" class="tab-content">
            <div class="insight-card">
                <h4>🚀 Ownership Momentum & Investment Flow Intelligence</h4>
                {_format_insight_text(strategic_insights.get('momentum_intelligence', 'No data available.'))}
            </div>
        </div>
    """
    
    # Tab 4: Liquidity Framework
    html += f"""
        <div id="liquidity-intel" class="tab-content">
            <div class="insight-card">
                <h4>💧 Float Analysis & Liquidity Intelligence</h4>
                {_format_insight_text(strategic_insights.get('liquidity_intelligence', 'No data available.'))}
            </div>
        </div>
    """
    
    html += "</div>"
    
    # Add tab switching script
    html += """
    <script>
    function openTab(evt, tabName) {
        var i, tabcontent, tabbuttons;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].classList.remove("active");
        }
        tabbuttons = document.getElementsByClassName("tab-button");
        for (i = 0; i < tabbuttons.length; i++) {
            tabbuttons[i].classList.remove("active");
        }
        document.getElementById(tabName).classList.add("active");
        evt.currentTarget.classList.add("active");
    }
    </script>
    
    <style>
    .strategic-tabs {
        margin: 30px 0;
    }
    
    .tab-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .tab-button {
        padding: 12px 24px;
        background: var(--card-bg);
        border: 2px solid var(--card-border);
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
        transition: var(--transition-fast);
        color: var(--text-primary);
    }
    
    .tab-button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: var(--primary-gradient-start);
        transform: translateY(-2px);
    }
    
    .tab-button.active {
        background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
        color: white;
        border-color: transparent;
    }
    
    .tab-content {
        display: none;
        animation: fadeIn 0.5s;
    }
    
    .tab-content.active {
        display: block;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .insight-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 30px;
        border-left: 4px solid var(--primary-gradient-start);
        box-shadow: var(--shadow-sm);
    }
    
    .insight-card h4 {
        margin-bottom: 20px;
        color: var(--text-primary);
    }
    </style>
    """
    
    return html


def _format_insight_text(text: str) -> str:
    """Format insight text with proper HTML structure"""
    # Split by bullet points
    lines = text.split('•')
    
    formatted = "<div class='insight-content'>"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if it's a section header (contains : at end or is bold in original)
        if ':' in line and line.count(':') == 1 and len(line.split(':')[0]) < 80:
            parts = line.split(':', 1)
            formatted += f"<div class='insight-section'><strong>{parts[0]}:</strong>{parts[1]}</div>"
        else:
            formatted += f"<div class='insight-item'>• {line}</div>"
    
    formatted += "</div>"
    
    # Add styling
    formatted += """
    <style>
    .insight-content {
        line-height: 1.8;
    }
    
    .insight-section {
        margin: 15px 0;
        padding: 12px;
        background: rgba(102, 126, 234, 0.05);
        border-radius: 8px;
    }
    
    .insight-item {
        margin: 10px 0;
        padding-left: 10px;
    }
    
    .insight-content strong {
        color: var(--primary-gradient-start);
        font-weight: 700;
    }
    </style>
    """
    
    return formatted


# =============================================================================
# INVESTMENT FRAMEWORK TIMELINE
# =============================================================================

def _build_investment_framework_timeline(strategic_insights: Dict, ownership_flow: Dict,
                                        quality_metrics: Dict, momentum_analysis: Dict) -> str:
    """Build investment framework timeline with progress indicators"""
    
    html = """
    <h3>🗓️ Strategic Investment Framework & Implementation Timeline</h3>
    <div class="timeline-container">
    """
    
    total_companies = len(ownership_flow) if ownership_flow else 0
    strong_inflow = sum(1 for f in ownership_flow.values() if f['flow_direction'] == 'Strong Inflow') if ownership_flow else 0
    excellent_quality = sum(1 for q in quality_metrics.values() if q['quality_rating'] == 'Excellent') if quality_metrics else 0
    strong_momentum = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] in ['Very Strong', 'Strong']) if momentum_analysis else 0
    
    # Phase 1: Immediate (0-3 months)
    phase1_progress = _calculate_phase_progress(strong_inflow, total_companies, 0.3)
    html += _build_timeline_phase(
        "Phase 1: Immediate Actions",
        "0-3 Months",
        phase1_progress,
        [
            f"✅ Deploy capital following {strong_inflow} strong institutional inflow signals",
            f"🎯 Concentrate in {excellent_quality} excellent-quality institutional holdings",
            f"🚀 Execute momentum strategies in {strong_momentum} high-momentum positions",
            "📊 Establish institutional flow monitoring dashboard"
        ],
        "success" if phase1_progress >= 75 else "warning"
    )
    
    # Phase 2: Medium-term (3-12 months)
    phase2_progress = _calculate_phase_progress(excellent_quality, total_companies, 0.5)
    html += _build_timeline_phase(
        "Phase 2: Strategic Development",
        "3-12 Months",
        phase2_progress,
        [
            "📈 Advanced institutional flow analysis for enhanced alpha generation",
            f"⭐ Maintain {excellent_quality} high-quality institutional positions",
            "💧 Optimize portfolio liquidity profile for better execution",
            "🔄 Implement dynamic rebalancing based on institutional signals"
        ],
        "info" if phase2_progress >= 50 else "warning"
    )
    
    # Phase 3: Long-term (12+ months)
    target_inflow = min(total_companies, strong_inflow + 2) if total_companies > 0 else 0
    target_quality = min(total_companies, excellent_quality + 2) if total_companies > 0 else 0
    phase3_progress = _calculate_phase_progress(strong_inflow, target_inflow, 1.0)
    html += _build_timeline_phase(
        "Phase 3: Excellence Achievement",
        "12+ Months",
        phase3_progress,
        [
            f"🎯 Achieve institutional validation across {target_inflow} positions",
            f"⭐ Expand to {target_quality} excellent-quality institutional holdings",
            "🏆 Attain industry-leading institutional flow intelligence",
            "💎 Establish sustained competitive advantage through institutional support"
        ],
        "default"
    )
    
    html += "</div>"
    
    # Add timeline styling
    html += """
    <style>
    .timeline-container {
        margin: 30px 0;
    }
    
    .timeline-phase {
        margin: 25px 0;
        padding: 25px;
        background: var(--card-bg);
        border-radius: 12px;
        border-left: 5px solid var(--primary-gradient-start);
        box-shadow: var(--shadow-sm);
        position: relative;
    }
    
    .timeline-phase.success {
        border-left-color: #10b981;
    }
    
    .timeline-phase.warning {
        border-left-color: #f59e0b;
    }
    
    .timeline-phase.info {
        border-left-color: #3b82f6;
    }
    
    .phase-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .phase-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .phase-duration {
        padding: 6px 16px;
        background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .phase-actions {
        list-style: none;
        margin: 15px 0;
    }
    
    .phase-actions li {
        margin: 10px 0;
        padding-left: 10px;
        line-height: 1.6;
    }
    </style>
    """
    
    return html


def _calculate_phase_progress(current: int, target: int, weight: float) -> float:
    """Calculate phase progress percentage"""
    if target == 0:
        return 50.0
    progress = (current / target) * 100 * weight
    return min(100, max(0, progress))


def _build_timeline_phase(title: str, duration: str, progress: float, 
                         actions: List[str], phase_type: str) -> str:
    """Build a single timeline phase"""
    
    actions_html = "".join([f"<li>{action}</li>" for action in actions])
    
    return f"""
    <div class="timeline-phase {phase_type}">
        <div class="phase-header">
            <div class="phase-title">{title}</div>
            <div class="phase-duration">{duration}</div>
        </div>
        {build_completeness_bar(progress, f"Implementation Progress: {progress:.0f}%")}
        <ul class="phase-actions">
            {actions_html}
        </ul>
    </div>
    """


# =============================================================================
# SUCCESS METRICS DASHBOARD
# =============================================================================

def _build_success_metrics_dashboard(ownership_flow: Dict, quality_metrics: Dict,
                                    momentum_analysis: Dict, float_analysis: Dict,
                                    companies: Dict[str, str]) -> str:
    """Build success metrics dashboard with targets"""
    
    html = "<h3>🎯 Success Metrics & Strategic Targets</h3>"
    
    total_companies = len(companies)
    
    # Calculate current metrics
    strong_inflow = sum(1 for f in ownership_flow.values() if f['flow_direction'] == 'Strong Inflow') if ownership_flow else 0
    avg_quality = np.mean([q['quality_score'] for q in quality_metrics.values()]) if quality_metrics else 0
    strong_momentum = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] in ['Very Strong', 'Strong']) if momentum_analysis else 0
    excellent_liquidity = sum(1 for l in float_analysis.values() if l['liquidity_rating'] == 'Excellent') if float_analysis else 0
    
    # Define targets
    target_inflow = min(total_companies, strong_inflow + 2)
    target_quality = min(10, avg_quality + 1.5)
    target_momentum = min(total_companies, strong_momentum + 2)
    target_liquidity = max(excellent_liquidity + 1, int(total_companies * 0.6))
    
    # Build progress indicators
    metrics = [
        {
            'label': '📊 Institutional Flow Target',
            'current': strong_inflow,
            'target': target_inflow,
            'unit': 'companies',
            'timeline': '18 months'
        },
        {
            'label': '⭐ Quality Score Target',
            'current': avg_quality,
            'target': target_quality,
            'unit': '/10',
            'timeline': '24 months'
        },
        {
            'label': '🚀 Momentum Excellence Target',
            'current': strong_momentum,
            'target': target_momentum,
            'unit': 'companies',
            'timeline': '12 months'
        },
        {
            'label': '💧 Liquidity Optimization Target',
            'current': excellent_liquidity,
            'target': target_liquidity,
            'unit': 'companies',
            'timeline': '36 months'
        }
    ]
    
    html += '<div class="metrics-grid">'
    
    for metric in metrics:
        current = metric['current']
        target = metric['target']
        percentage = (current / target * 100) if target > 0 else 0
        percentage = min(100, percentage)
        
        # Format current and target values
        current_display = f"{current:.1f}" if isinstance(current, float) else str(current)
        target_display = f"{target:.1f}" if isinstance(target, float) else str(target)
        
        html += f"""
        <div class="metric-card">
            <div class="metric-header">
                <h4>{metric['label']}</h4>
                <span class="metric-timeline">⏱️ {metric['timeline']}</span>
            </div>
            <div class="metric-values">
                <div class="current-value">
                    <span class="value-label">Current:</span>
                    <span class="value-number">{current_display}</span>
                    <span class="value-unit">{metric['unit']}</span>
                </div>
                <div class="target-value">
                    <span class="value-label">Target:</span>
                    <span class="value-number">{target_display}</span>
                    <span class="value-unit">{metric['unit']}</span>
                </div>
            </div>
            {build_completeness_bar(percentage, f"Progress: {percentage:.0f}%")}
        </div>
        """
    
    html += '</div>'
    
    # Add styling
    html += """
    <style>
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin: 25px 0;
    }
    
    .metric-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 25px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--card-border);
        transition: var(--transition-fast);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-md);
    }
    
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .metric-header h4 {
        font-size: 1.1rem;
        margin: 0;
        color: var(--text-primary);
    }
    
    .metric-timeline {
        padding: 4px 12px;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        font-size: 0.85rem;
        color: var(--primary-gradient-start);
        font-weight: 600;
    }
    
    .metric-values {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .current-value, .target-value {
        text-align: center;
        padding: 15px;
        background: rgba(102, 126, 234, 0.05);
        border-radius: 8px;
    }
    
    .value-label {
        display: block;
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .value-number {
        display: inline-block;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-gradient-start);
    }
    
    .value-unit {
        font-size: 0.9rem;
        color: var(--text-tertiary);
        margin-left: 4px;
    }
    </style>
    """
    
    return html



# =============================================================================
# ACTION PRIORITY CARDS
# =============================================================================

def _build_action_priority_cards(ownership_flow: Dict, quality_metrics: Dict,
                                 momentum_analysis: Dict, float_analysis: Dict,
                                 companies: Dict[str, str]) -> str:
    """Build action priority cards with color coding"""
    
    html = "<h3>🎯 Action Priority Framework</h3>"
    
    # Analyze and generate action items
    actions = []
    
    # Flow-based actions
    if ownership_flow:
        strong_outflow = sum(1 for f in ownership_flow.values() if f['flow_direction'] == 'Strong Outflow')
        if strong_outflow > 0:
            actions.append({
                'priority': 'High',
                'category': '📉 Flow Management',
                'action': f'Address {strong_outflow} companies with strong institutional outflows',
                'impact': 'Portfolio stability and institutional confidence',
                'timeline': 'Immediate (0-1 month)'
            })
    
    # Quality-based actions
    if quality_metrics:
        below_avg = sum(1 for q in quality_metrics.values() if q['quality_rating'] == 'Below Average')
        if below_avg > 0:
            actions.append({
                'priority': 'Medium',
                'category': '⭐ Quality Enhancement',
                'action': f'Improve institutional quality for {below_avg} below-average companies',
                'impact': 'Enhanced institutional appeal and stability',
                'timeline': 'Short-term (1-3 months)'
            })
    
    # Momentum-based actions
    if momentum_analysis:
        weak_momentum = sum(1 for m in momentum_analysis.values() if m['momentum_rating'] in ['Weak', 'Very Weak'])
        if weak_momentum > 0:
            actions.append({
                'priority': 'Medium',
                'category': '🚀 Momentum Building',
                'action': f'Develop momentum strategies for {weak_momentum} weak-momentum companies',
                'impact': 'Improved institutional interest and capital flows',
                'timeline': 'Medium-term (3-6 months)'
            })
    
    # Liquidity-based actions
    if float_analysis:
        poor_liquidity = sum(1 for l in float_analysis.values() if l['liquidity_rating'] in ['Poor', 'Very Poor'])
        if poor_liquidity > 0:
            actions.append({
                'priority': 'Low',
                'category': '💧 Liquidity Optimization',
                'action': f'Enhance liquidity profile for {poor_liquidity} low-liquidity companies',
                'impact': 'Better trading execution and position management',
                'timeline': 'Long-term (6-12 months)'
            })
    
    # Add positive reinforcement actions
    if ownership_flow:
        strong_inflow = sum(1 for f in ownership_flow.values() if f['flow_direction'] == 'Strong Inflow')
        if strong_inflow > 0:
            actions.append({
                'priority': 'Strategic',
                'category': '🌟 Capitalize on Strength',
                'action': f'Maximize positioning in {strong_inflow} companies with strong institutional inflows',
                'impact': 'Alpha generation from institutional momentum',
                'timeline': 'Immediate (0-1 month)'
            })
    
    if not actions:
        actions.append({
            'priority': 'Strategic',
            'category': '✅ Portfolio Monitoring',
            'action': 'Continue monitoring institutional metrics and maintain current positions',
            'impact': 'Sustained institutional support and stability',
            'timeline': 'Ongoing'
        })
    
    # Sort by priority
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2, 'Strategic': 3}
    actions.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    html += '<div class="action-cards-grid">'
    
    for action in actions:
        priority_class = action['priority'].lower()
        priority_color = {
            'high': '#ef4444',
            'medium': '#f59e0b',
            'low': '#3b82f6',
            'strategic': '#10b981'
        }.get(priority_class, '#667eea')
        
        html += f"""
        <div class="action-card {priority_class}">
            <div class="action-priority-badge" style="background: {priority_color};">
                {action['priority']} Priority
            </div>
            <div class="action-category">{action['category']}</div>
            <div class="action-description">{action['action']}</div>
            <div class="action-impact">
                <strong>Expected Impact:</strong> {action['impact']}
            </div>
            <div class="action-timeline">
                <strong>⏱️ Timeline:</strong> {action['timeline']}
            </div>
        </div>
        """
    
    html += '</div>'
    
    # Add styling
    html += """
    <style>
    .action-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 20px;
        margin: 25px 0;
    }
    
    .action-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 25px;
        box-shadow: var(--shadow-sm);
        border: 2px solid var(--card-border);
        transition: var(--transition-smooth);
        position: relative;
        overflow: hidden;
    }
    
    .action-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-gradient-start), var(--primary-gradient-end));
    }
    
    .action-card.high::before {
        background: linear-gradient(90deg, #ef4444, #dc2626);
    }
    
    .action-card.medium::before {
        background: linear-gradient(90deg, #f59e0b, #d97706);
    }
    
    .action-card.low::before {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
    }
    
    .action-card.strategic::before {
        background: linear-gradient(90deg, #10b981, #059669);
    }
    
    .action-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-gradient-start);
    }
    
    .action-priority-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .action-category {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 15px;
    }
    
    .action-description {
        font-size: 1rem;
        color: var(--text-primary);
        line-height: 1.6;
        margin-bottom: 15px;
        padding: 15px;
        background: rgba(102, 126, 234, 0.05);
        border-radius: 8px;
    }
    
    .action-impact, .action-timeline {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 10px 0;
        line-height: 1.5;
    }
    
    .action-impact strong, .action-timeline strong {
        color: var(--text-primary);
    }
    </style>
    """
    
    return html


# =============================================================================
# HELPER FUNCTION - COMPREHENSIVE INTELLIGENCE GENERATION
# =============================================================================

def _generate_comprehensive_institutional_intelligence(ownership_flow: Dict, quality_metrics: Dict,
                                                     momentum_analysis: Dict, float_analysis: Dict, 
                                                     companies: Dict[str, str]) -> Dict[str, str]:
    """Generate comprehensive institutional intelligence insights"""
    
    total_companies = len(companies)
    
    # Calculate key metrics with safe defaults
    if ownership_flow:
        strong_inflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Strong Inflow')
        moderate_inflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Moderate Inflow')
        outflow_companies = sum(1 for flow in ownership_flow.values() if 'Outflow' in flow['flow_direction'])
        avg_flow_quality = np.mean([flow['flow_quality_score'] for flow in ownership_flow.values()])
    else:
        strong_inflow = moderate_inflow = outflow_companies = avg_flow_quality = 0
    
    if quality_metrics:
        excellent_quality = sum(1 for metrics in quality_metrics.values() if metrics['quality_rating'] == 'Excellent')
        high_quality = sum(1 for metrics in quality_metrics.values() if metrics['quality_rating'] == 'High Quality')
        avg_quality_score = np.mean([metrics['quality_score'] for metrics in quality_metrics.values()])
        avg_ownership_pct = np.mean([metrics['ownership_percentage'] for metrics in quality_metrics.values()])
        high_concentration = sum(1 for metrics in quality_metrics.values() if metrics['concentration_risk'] in ['High', 'Very High'])
    else:
        excellent_quality = high_quality = avg_quality_score = avg_ownership_pct = high_concentration = 0
    
    if momentum_analysis:
        strong_momentum = sum(1 for analysis in momentum_analysis.values() if analysis['momentum_rating'] in ['Very Strong', 'Strong'])
        avg_momentum_score = np.mean([analysis['momentum_score'] for analysis in momentum_analysis.values()])
        inflow_companies = sum(1 for analysis in momentum_analysis.values() if analysis['flow_direction'] == 'Inflow')
    else:
        strong_momentum = avg_momentum_score = inflow_companies = 0
    
    if float_analysis:
        excellent_liquidity = sum(1 for analysis in float_analysis.values() if analysis['liquidity_rating'] == 'Excellent')
        avg_liquidity_score = np.mean([analysis['liquidity_score'] for analysis in float_analysis.values()])
    else:
        excellent_liquidity = avg_liquidity_score = 0
    
    # Generate insights (simplified for web presentation)
    ownership_intelligence = f"""Portfolio Flow Analysis: {strong_inflow} companies with strong inflows, {outflow_companies} with outflow patterns across {total_companies} companies
Smart Money Direction: {'Exceptional institutional accumulation' if strong_inflow + moderate_inflow >= total_companies * 0.6 else 'Strong institutional interest' if strong_inflow + moderate_inflow > outflow_companies else 'Mixed institutional sentiment'} with {avg_flow_quality:.1f} average flow quality score
Institutional Validation: {'High institutional confidence' if strong_inflow >= total_companies * 0.4 else 'Moderate institutional support' if strong_inflow + moderate_inflow >= total_companies * 0.4 else 'Mixed institutional signals'} in portfolio quality
Flow Intelligence: {'Broad-based institutional accumulation' if strong_inflow + moderate_inflow >= total_companies * 0.5 else 'Selective institutional interest' if strong_inflow > 0 else 'Limited institutional momentum'} providing investment validation"""
    
    quality_intelligence = f"""Portfolio Quality Profile: {excellent_quality} excellent, {high_quality} high-quality companies with {avg_quality_score:.1f}/10 average institutional quality score
Institutional Coverage: {avg_ownership_pct:.1f}% average institutional ownership providing {'strong' if avg_ownership_pct > 60 else 'moderate' if avg_ownership_pct > 40 else 'developing'} institutional foundation
Holder Quality Distribution: {'Outstanding institutional foundation' if excellent_quality >= total_companies * 0.5 else 'Strong institutional quality' if high_quality >= total_companies * 0.4 else 'Developing institutional quality'} across portfolio companies
Concentration Risk Management: {high_concentration} companies with high concentration risk requiring {'enhanced monitoring' if high_concentration > 0 else 'standard oversight'}"""
    
    momentum_intelligence = f"""Portfolio Momentum Profile: {strong_momentum} companies with strong momentum across {total_companies} portfolio companies
Investment Flow Direction: {inflow_companies} companies experiencing institutional inflows indicating {'broad institutional accumulation' if inflow_companies >= total_companies * 0.6 else 'selective institutional interest' if inflow_companies >= total_companies * 0.4 else 'mixed institutional sentiment'}
Momentum Score Analysis: {avg_momentum_score:.1f}/10 average momentum score reflecting {'strong' if avg_momentum_score >= 6 else 'moderate' if avg_momentum_score >= 4 else 'weak'} institutional conviction
Flow Momentum Assessment: {'Exceptional institutional momentum' if strong_momentum >= total_companies * 0.5 else 'Strong institutional momentum' if strong_momentum >= total_companies * 0.3 else 'Developing momentum patterns'} providing investment timing intelligence"""
    
    liquidity_intelligence = f"""Portfolio Liquidity Profile: {excellent_liquidity} companies with excellent liquidity characteristics across {total_companies} portfolio companies
Trading Liquidity Assessment: {'Excellent liquidity profile' if excellent_liquidity >= total_companies * 0.5 else 'Good liquidity foundation' if avg_liquidity_score >= 6 else 'Mixed liquidity characteristics'} supporting {'optimal position sizing' if excellent_liquidity >= total_companies * 0.5 else 'standard position management' if avg_liquidity_score >= 6 else 'careful position sizing'}
Liquidity Score Analysis: {avg_liquidity_score:.1f}/10 average liquidity score indicating {'superior' if avg_liquidity_score >= 8 else 'strong' if avg_liquidity_score >= 6 else 'moderate' if avg_liquidity_score >= 4 else 'limited'} portfolio liquidity
Float Efficiency: Comprehensive float analysis enabling optimal trading execution and position management"""
    
    return {
        'ownership_intelligence': ownership_intelligence,
        'quality_intelligence': quality_intelligence,
        'momentum_intelligence': momentum_intelligence,
        'liquidity_intelligence': liquidity_intelligence
    }


# =============================================================================
# HELPER FUNCTIONS - OWNERSHIP FLOW ANALYSIS
# =============================================================================

def _generate_ownership_flow_analysis(institutional_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Generate comprehensive ownership flow analysis"""
    
    if institutional_df.empty:
        return {}
    
    ownership_flow_analysis = {}
    
    for company_name, ticker in companies.items():
        company_data = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if company_data.empty:
            continue
        
        company_data = company_data.sort_values('date')
        
        if len(company_data) < 1:
            continue
        
        latest_quarter = company_data.iloc[-1]
        
        new_positions = latest_quarter.get('newPositions', 0) or 0
        sold_out_positions = latest_quarter.get('soldOutPositions', 0) or 0
        increased_positions = latest_quarter.get('increasedPositions', 0) or 0
        decreased_positions = latest_quarter.get('decreasedPositions', 0) or 0
        
        total_position_changes = new_positions + sold_out_positions + increased_positions + decreased_positions
        
        net_new_positions = new_positions - sold_out_positions
        net_position_changes = increased_positions - decreased_positions
        
        total_activity = max(1, total_position_changes)
        inflow_ratio = (new_positions + increased_positions) / total_activity
        outflow_ratio = (sold_out_positions + decreased_positions) / total_activity
        
        net_flow_score = (inflow_ratio - outflow_ratio) * 10
        
        if net_flow_score > 3:
            flow_direction = "Strong Inflow"
        elif net_flow_score > 1:
            flow_direction = "Moderate Inflow"
        elif net_flow_score > -1:
            flow_direction = "Balanced"
        elif net_flow_score > -3:
            flow_direction = "Moderate Outflow"
        else:
            flow_direction = "Strong Outflow"
        
        total_investors = latest_quarter.get('investorsHolding', 1) or 1
        flow_intensity = total_position_changes / max(1, total_investors)
        
        if flow_intensity > 0.5:
            activity_level = "High"
        elif flow_intensity > 0.25:
            activity_level = "Moderate"
        else:
            activity_level = "Low"
        
        flow_quality_score = abs(net_flow_score) + min(5, total_position_changes / 10)
        
        ownership_flow_analysis[company_name] = {
            'ticker': ticker,
            'latest_quarter': latest_quarter.get('date'),
            'new_positions': new_positions,
            'sold_out_positions': sold_out_positions,
            'increased_positions': increased_positions,
            'decreased_positions': decreased_positions,
            'total_flow_activity': total_position_changes,
            'net_new_positions': net_new_positions,
            'net_position_changes': net_position_changes,
            'inflow_ratio': inflow_ratio * 100,
            'outflow_ratio': outflow_ratio * 100,
            'net_flow_score': net_flow_score,
            'flow_direction': flow_direction,
            'activity_level': activity_level,
            'flow_intensity': flow_intensity,
            'total_investors': total_investors,
            'ownership_change': latest_quarter.get('ownershipPercentChange', 0) or 0,
            'total_invested_change': latest_quarter.get('totalInvestedChange', 0) or 0,
            'flow_quality_score': flow_quality_score
        }
    
    return ownership_flow_analysis


def _generate_ownership_flow_summary(ownership_flow: Dict[str, Dict]) -> str:
    """Generate ownership flow analysis summary"""
    
    total_companies = len(ownership_flow)
    
    if total_companies == 0:
        return "No ownership flow data available."
    
    strong_inflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Strong Inflow')
    moderate_inflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Moderate Inflow')
    strong_outflow = sum(1 for flow in ownership_flow.values() if flow['flow_direction'] == 'Strong Outflow')
    
    total_new_positions = sum(flow['new_positions'] for flow in ownership_flow.values())
    total_exits = sum(flow['sold_out_positions'] for flow in ownership_flow.values())
    total_increases = sum(flow['increased_positions'] for flow in ownership_flow.values())
    total_decreases = sum(flow['decreased_positions'] for flow in ownership_flow.values())
    
    avg_flow_quality = np.mean([flow['flow_quality_score'] for flow in ownership_flow.values()])
    avg_net_flow = np.mean([flow['net_flow_score'] for flow in ownership_flow.values()])
    
    return f"""<strong>Ownership Flow Analysis Summary:</strong><br><br>
• Portfolio Flow Direction: {strong_inflow} companies with strong inflows, {strong_outflow} with strong outflows across {total_companies} companies<br>
• Position Activity: {total_new_positions} new positions, {total_exits} exits, {total_increases} increases, {total_decreases} decreases<br>
• Net Portfolio Flow: {avg_net_flow:+.1f} average flow score indicating {'positive institutional sentiment' if avg_net_flow > 1 else 'mixed institutional sentiment' if avg_net_flow > -1 else 'negative institutional sentiment'}<br>
• Flow Quality: {avg_flow_quality:.1f} average flow quality score indicating {'high' if avg_flow_quality > 8 else 'moderate' if avg_flow_quality > 5 else 'low'} institutional engagement<br><br>
<strong>Smart Money Activity:</strong> {'Strong institutional accumulation' if total_new_positions + total_increases > total_exits + total_decreases else 'Institutional distribution pattern' if total_exits + total_decreases > total_new_positions + total_increases else 'Balanced institutional activity'} across portfolio"""


# =============================================================================
# HELPER FUNCTIONS - INSTITUTIONAL QUALITY METRICS
# =============================================================================

def _analyze_institutional_quality(institutional_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze institutional quality metrics"""
    
    if institutional_df.empty:
        return {}
    
    quality_metrics = {}
    
    for company_name, ticker in companies.items():
        company_data = institutional_df[institutional_df['symbol'] == ticker].copy() if 'symbol' in institutional_df.columns else institutional_df[institutional_df['Company'] == company_name].copy()
        
        if company_data.empty:
            continue
        
        company_data = company_data.sort_values('date')
        latest_data = company_data.iloc[-1]
        
        investors_holding = latest_data.get('investorsHolding', 0) or 0
        ownership_pct = latest_data.get('ownershipPercent', 0) or 0
        total_invested = latest_data.get('totalInvested', 0) or 0
        
        avg_position_size = total_invested / max(1, investors_holding) if investors_holding > 0 else 0
        
        estimated_hhi = _estimate_hhi_enhanced(investors_holding, ownership_pct)
        stability_score = _calculate_stability_score_enhanced(company_data)
        quality_score = _assess_institutional_quality_enhanced(
            investors_holding, ownership_pct, avg_position_size, estimated_hhi, stability_score
        )
        concentration_risk = _assess_concentration_risk_enhanced(estimated_hhi, investors_holding, ownership_pct)
        
        if quality_score >= 8:
            quality_rating = "Excellent"
        elif quality_score >= 6.5:
            quality_rating = "High Quality"
        elif quality_score >= 5:
            quality_rating = "Standard Quality"
        elif quality_score >= 3:
            quality_rating = "Developing Quality"
        else:
            quality_rating = "Below Average"
        
        quality_metrics[company_name] = {
            'ticker': ticker,
            'investors_holding': investors_holding,
            'ownership_percentage': ownership_pct,
            'total_invested_millions': total_invested / 1_000_000 if total_invested > 0 else 0,
            'avg_position_size_millions': avg_position_size / 1_000_000 if avg_position_size > 0 else 0,
            'estimated_hhi': estimated_hhi,
            'concentration_risk': concentration_risk,
            'stability_score': stability_score,
            'quality_score': quality_score,
            'quality_rating': quality_rating
        }
    
    return quality_metrics


def _estimate_hhi_enhanced(investors_holding: int, ownership_percent: float) -> float:
    """Enhanced HHI estimation"""
    
    if investors_holding <= 0:
        return 0
    
    if investors_holding == 1:
        return 10000
    elif investors_holding <= 3:
        base_hhi = 4000 - (investors_holding - 1) * 500
    elif investors_holding <= 10:
        base_hhi = 2000 - (investors_holding - 3) * 200
    elif investors_holding <= 25:
        base_hhi = 1000 - (investors_holding - 10) * 40
    elif investors_holding <= 50:
        base_hhi = 600 - (investors_holding - 25) * 15
    else:
        base_hhi = max(100, 400 - (investors_holding - 50) * 5)
    
    ownership_adjustment = 1.0
    if ownership_percent > 80:
        ownership_adjustment = 1.3
    elif ownership_percent > 60:
        ownership_adjustment = 1.1
    elif ownership_percent < 30:
        ownership_adjustment = 0.8
    
    return min(10000, max(100, base_hhi * ownership_adjustment))


def _calculate_stability_score_enhanced(company_data: pd.DataFrame) -> float:
    """Enhanced stability score calculation"""
    
    if len(company_data) < 2:
        return 5.0
    
    company_data = company_data.sort_values('date')
    
    ownership_pct = company_data['ownershipPercent'].fillna(0)
    investor_counts = company_data['investorsHolding'].fillna(0)
    total_invested = company_data['totalInvested'].fillna(0)
    
    stability_components = []
    
    if len(ownership_pct) > 1 and ownership_pct.std() > 0:
        ownership_volatility = ownership_pct.std()
        ownership_stability = max(0, 10 - (ownership_volatility / 3))
        stability_components.append(ownership_stability)
    
    if len(investor_counts) > 1 and investor_counts.std() > 0:
        investor_volatility = investor_counts.std()
        investor_stability = max(0, 10 - (investor_volatility / 5))
        stability_components.append(investor_stability)
    
    if len(total_invested) > 1:
        invested_pct_changes = total_invested.pct_change().fillna(0)
        if invested_pct_changes.std() > 0:
            invested_volatility = invested_pct_changes.std() * 100
            invested_stability = max(0, 10 - (invested_volatility / 10))
            stability_components.append(invested_stability)
    
    return min(10, max(0, np.mean(stability_components))) if stability_components else 5.0


def _assess_institutional_quality_enhanced(investors_holding: int, ownership_percent: float,
                                         avg_position_size: float, estimated_hhi: float,
                                         stability_score: float) -> float:
    """Enhanced institutional quality assessment"""
    
    if investors_holding >= 50:
        investor_score = 10
    elif investors_holding >= 30:
        investor_score = 9
    elif investors_holding >= 20:
        investor_score = 8
    elif investors_holding >= 15:
        investor_score = 7
    elif investors_holding >= 10:
        investor_score = 6
    elif investors_holding >= 5:
        investor_score = 4
    else:
        investor_score = 2
    
    if 40 <= ownership_percent <= 70:
        ownership_score = 10
    elif 30 <= ownership_percent <= 80:
        ownership_score = 8
    elif 25 <= ownership_percent <= 85:
        ownership_score = 6
    elif 15 <= ownership_percent <= 90:
        ownership_score = 4
    else:
        ownership_score = 2
    
    if estimated_hhi < 800:
        concentration_score = 10
    elif estimated_hhi < 1200:
        concentration_score = 8
    elif estimated_hhi < 1800:
        concentration_score = 6
    elif estimated_hhi < 2500:
        concentration_score = 4
    else:
        concentration_score = 2
    
    if avg_position_size > 0:
        position_size_millions = avg_position_size / 1_000_000
        if 10 <= position_size_millions <= 100:
            position_score = 10
        elif 5 <= position_size_millions <= 200:
            position_score = 8
        elif 1 <= position_size_millions <= 500:
            position_score = 6
        else:
            position_score = 4
    else:
        position_score = 5
    
    quality_score = (
        investor_score * 0.25 +
        ownership_score * 0.25 +
        concentration_score * 0.25 +
        stability_score * 0.15 +
        position_score * 0.10
    )
    
    return min(10, max(0, quality_score))


def _assess_concentration_risk_enhanced(estimated_hhi: float, investors_holding: int, ownership_percent: float) -> str:
    """Enhanced concentration risk assessment"""
    
    risk_factors = 0
    
    if estimated_hhi > 2500:
        risk_factors += 3
    elif estimated_hhi > 1500:
        risk_factors += 2
    elif estimated_hhi > 1000:
        risk_factors += 1
    
    if investors_holding < 5:
        risk_factors += 2
    elif investors_holding < 15:
        risk_factors += 1
    
    if ownership_percent > 80:
        risk_factors += 2
    elif ownership_percent > 70:
        risk_factors += 1
    
    if risk_factors >= 5:
        return "Very High"
    elif risk_factors >= 3:
        return "High"
    elif risk_factors >= 2:
        return "Moderate"
    else:
        return "Low"


def _generate_quality_metrics_summary(quality_metrics: Dict[str, Dict]) -> str:
    """Generate institutional quality metrics summary"""
    
    total_companies = len(quality_metrics)
    
    if total_companies == 0:
        return "No institutional quality metrics available."
    
    excellent_quality = sum(1 for metrics in quality_metrics.values() if metrics['quality_rating'] == 'Excellent')
    high_quality = sum(1 for metrics in quality_metrics.values() if metrics['quality_rating'] == 'High Quality')
    below_avg_quality = sum(1 for metrics in quality_metrics.values() if metrics['quality_rating'] == 'Below Average')
    
    high_concentration = sum(1 for metrics in quality_metrics.values() if metrics['concentration_risk'] in ['High', 'Very High'])
    low_concentration = sum(1 for metrics in quality_metrics.values() if metrics['concentration_risk'] == 'Low')
    
    avg_investors = np.mean([metrics['investors_holding'] for metrics in quality_metrics.values()])
    avg_ownership = np.mean([metrics['ownership_percentage'] for metrics in quality_metrics.values()])
    avg_quality_score = np.mean([metrics['quality_score'] for metrics in quality_metrics.values()])
    avg_stability = np.mean([metrics['stability_score'] for metrics in quality_metrics.values()])
    
    return f"""<strong>Institutional Quality Metrics Summary:</strong><br><br>
• Portfolio Quality Profile: {excellent_quality} excellent, {high_quality} high-quality companies with {avg_quality_score:.1f}/10 average quality score<br>
• Institutional Coverage: {avg_investors:.0f} average investors per company with {avg_ownership:.1f}% average institutional ownership<br>
• Concentration Risk: {high_concentration} companies with high concentration risk, {low_concentration} with low concentration risk<br>
• Ownership Stability: {avg_stability:.1f}/10 average stability score indicating {'high' if avg_stability >= 7 else 'moderate' if avg_stability >= 5 else 'variable'} ownership consistency<br><br>
<strong>Quality Assessment:</strong> {'Outstanding institutional foundation' if excellent_quality >= total_companies * 0.5 else 'Strong institutional quality' if high_quality >= total_companies * 0.4 else 'Developing institutional quality'} across portfolio"""


# =============================================================================
# COLLAPSIBLE SUBSECTION JAVASCRIPT (add to section wrapper)
# =============================================================================

# Note: This JavaScript will be added to the final HTML via the section wrapper
# It handles the collapse/expand functionality for subsections