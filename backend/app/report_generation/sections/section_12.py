"""Section 12: Peer Context & Multi-Company Analysis"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter

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
    build_badge,
    build_colored_cell,
    build_enhanced_table
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 12: Peer Context & Multi-Company Analysis
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    df = collector.get_all_financial_data()
    
    try:
        profiles_df = collector.get_profiles()
    except:
        profiles_df = pd.DataFrame()
    
    # Generate comprehensive peer analysis
    peer_analysis = _generate_comprehensive_peer_analysis(df, companies, profiles_df)
    
    # Generate peer ranking analysis
    ranking_analysis = _generate_peer_ranking_analysis(df, companies, peer_analysis)

    sector_analysis = _generate_sector_analysis(df, companies, profiles_df, peer_analysis)
    valuation_ladder = _generate_valuation_ladder_analysis(df, companies, {})
    
    # Calculate risk scoring
    risk_scoring = calculate_risk_scoring(collector, analysis_id)
    
    # Build all subsections
    section_12a_html = _build_section_12a_cross_company_benchmarking(peer_analysis, companies)
    section_12b_html = _build_section_12b_peer_ranking(ranking_analysis, companies)
    section_12c_html = _build_section_12c_sector_analysis(sector_analysis,companies)  
    section_12d_html = _build_section_12d_valuation_ladder(valuation_ladder,companies)  
    section_12e_html = _build_section_12e_visualization_dashboard(
            peer_analysis, ranking_analysis, sector_analysis, valuation_ladder, risk_scoring
        )
    section_12f_html = _build_section_12f_strategic_intelligence(
            peer_analysis, ranking_analysis, sector_analysis, valuation_ladder, companies, risk_scoring
        )
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        {section_12a_html}
        {build_section_divider() if section_12b_html else ""}
        {section_12b_html}
        {build_section_divider() if section_12c_html else ""}
        {section_12c_html}
        {build_section_divider() if section_12d_html else ""}
        {section_12d_html}
        {build_section_divider() if section_12e_html else ""}
        {section_12e_html}
        {build_section_divider() if section_12f_html else ""}
        {section_12f_html}
    </div>
    """
    
    return generate_section_wrapper(12, "Peer Context & Multi-Company Analysis", content)


# =============================================================================
# SUBSECTION 12A: CROSS-COMPANY FINANCIAL PERFORMANCE BENCHMARKING
# =============================================================================

def _build_section_12a_cross_company_benchmarking(peer_analysis: Dict, companies: Dict) -> str:
    """Build subsection 12A: Cross-Company Financial Performance Benchmarking"""
    
    if not peer_analysis:
        return build_info_box("Peer analysis unavailable due to insufficient financial data.", "warning")
    
    # Create collapsible header
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-12a')">
            <h2>12A. Cross-Company Financial Performance Benchmarking</h2>
            <span class="toggle-icon" id="icon-section-12a">▼</span>
        </div>
        <div class="subsection-content" id="content-section-12a">
    """
    
    # Summary statistics cards
    total_companies = len(peer_analysis)
    revenue_growth_values = [a['financial_metrics']['revenue_growth'] for a in peer_analysis.values()]
    operating_margin_values = [a['profitability_metrics']['operating_margin'] for a in peer_analysis.values()]
    roe_values = [a['profitability_metrics']['roe'] for a in peer_analysis.values()]
    performance_scores = [a['relative_performance']['overall_performance_score'] * 100 for a in peer_analysis.values()]
    
    avg_revenue_growth = np.mean(revenue_growth_values)
    avg_operating_margin = np.mean(operating_margin_values)
    avg_roe = np.mean(roe_values)
    avg_performance_score = np.mean(performance_scores)
    
    # Stat cards
    stat_cards = [
        {
            "label": "Companies Analyzed",
            "value": str(total_companies),
            "description": "Portfolio peer comparison",
            "type": "info"
        },
        {
            "label": "Avg Revenue Growth",
            "value": f"{avg_revenue_growth:.1f}%",
            "description": "Portfolio-wide growth rate",
            "type": "success" if avg_revenue_growth > 10 else "warning" if avg_revenue_growth > 5 else "danger"
        },
        {
            "label": "Avg Operating Margin",
            "value": f"{avg_operating_margin:.1f}%",
            "description": "Portfolio profitability",
            "type": "success" if avg_operating_margin > 15 else "warning" if avg_operating_margin > 10 else "danger"
        },
        {
            "label": "Avg ROE",
            "value": f"{avg_roe:.1f}%",
            "description": "Return on equity",
            "type": "success" if avg_roe > 15 else "warning" if avg_roe > 10 else "danger"
        },
        {
            "label": "Avg Performance Score",
            "value": f"{avg_performance_score:.1f}",
            "description": "Composite peer score",
            "type": "success" if avg_performance_score > 70 else "warning" if avg_performance_score > 50 else "danger"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Cross-company comparison table
    html += "<h3>Latest Fiscal Year Comparative Analysis</h3>"
    html += _create_cross_company_table(peer_analysis, companies)
    
    # Peer analysis summary
    html += _generate_peer_analysis_summary(peer_analysis)
    
    # Charts (4 standalone charts from Performance Matrix)
    html += "<h3>Performance Analysis Charts</h3>"
    
    # Chart 1: Revenue Growth vs Operating Margin
    chart1_html = _create_revenue_growth_vs_operating_margin_chart(peer_analysis)
    if chart1_html:
        html += chart1_html
    
    # Chart 2: ROE vs P/E Ratio
    chart2_html = _create_roe_vs_pe_chart(peer_analysis)
    if chart2_html:
        html += chart2_html
    
    # Chart 3: Leverage vs Liquidity
    chart3_html = _create_leverage_vs_liquidity_chart(peer_analysis)
    if chart3_html:
        html += chart3_html
    
    # Chart 4: Performance Score Rankings
    chart4_html = _create_performance_score_rankings_chart(peer_analysis)
    if chart4_html:
        html += chart4_html
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_cross_company_table(peer_analysis: Dict, companies: Dict) -> str:
    """Create cross-company comparison table"""
    
    # Sort companies by performance score
    sorted_companies = sorted(peer_analysis.items(), 
                             key=lambda x: x[1]['relative_performance']['overall_performance_score'], 
                             reverse=True)
    
    # Build DataFrame
    table_data = []
    for company_name, analysis in sorted_companies:
        financial = analysis['financial_metrics']
        profitability = analysis['profitability_metrics']
        valuation = analysis['valuation_metrics']
        efficiency = analysis['efficiency_metrics']
        relative = analysis['relative_performance']
        
        row = {
            'Company': company_name,
            'FY': analysis['fiscal_year'],
            'Revenue Growth (%)': f"{financial['revenue_growth']:.1f}",
            'Operating Margin (%)': f"{profitability['operating_margin']:.1f}",
            'Net Margin (%)': f"{profitability['net_margin']:.1f}",
            'ROE (%)': f"{profitability['roe']:.1f}",
            'P/E Ratio': f"{valuation['pe_ratio']:.1f}x" if valuation['pe_ratio'] > 0 else "N/A",
            'P/B Ratio': f"{valuation['pb_ratio']:.1f}x" if valuation['pb_ratio'] > 0 else "N/A",
            'Debt/Equity': f"{efficiency['debt_equity_ratio']:.2f}",
            'Current Ratio': f"{efficiency['current_ratio']:.2f}",
            'Performance Score': f"{relative['overall_performance_score']:.2f}"
        }
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="cross-company-table", sortable=True, searchable=True)


def _generate_peer_analysis_summary(peer_analysis: Dict) -> str:
    """Generate peer analysis summary"""
    
    total_companies = len(peer_analysis)
    
    if total_companies == 0:
        return build_info_box("No peer analysis data available.", "warning")
    
    revenue_growth_values = [a['financial_metrics']['revenue_growth'] for a in peer_analysis.values()]
    operating_margin_values = [a['profitability_metrics']['operating_margin'] for a in peer_analysis.values()]
    roe_values = [a['profitability_metrics']['roe'] for a in peer_analysis.values()]
    performance_scores = [a['relative_performance']['overall_performance_score'] for a in peer_analysis.values()]
    
    avg_revenue_growth = np.mean(revenue_growth_values)
    avg_operating_margin = np.mean(operating_margin_values)
    avg_roe = np.mean(roe_values)
    avg_performance_score = np.mean(performance_scores)
    
    sorted_by_performance = sorted(peer_analysis.items(), 
                                  key=lambda x: x[1]['relative_performance']['overall_performance_score'], 
                                  reverse=True)
    top_performer = sorted_by_performance[0][0] if sorted_by_performance else "N/A"
    bottom_performer = sorted_by_performance[-1][0] if sorted_by_performance else "N/A"
    
    high_performers = sum(1 for score in performance_scores if score > 0.7)
    low_performers = sum(1 for score in performance_scores if score < 0.3)
    
    summary_text = f"""
    <h4>Cross-Company Performance Summary</h4>
    <p><strong>Portfolio Performance Profile:</strong> {total_companies} companies with {avg_revenue_growth:.1f}% average revenue growth and {avg_operating_margin:.1f}% operating margin</p>
    <p><strong>Profitability Assessment:</strong> {avg_roe:.1f}% average ROE with {avg_performance_score:.2f} composite performance score</p>
    <p><strong>Performance Distribution:</strong> {high_performers} high-performers (>70th percentile), {low_performers} underperformers (<30th percentile)</p>
    <p><strong>Peer Leadership:</strong> {top_performer} leads portfolio performance, {bottom_performer} requires performance enhancement</p>
    
    <h4>Multi-Dimensional Peer Intelligence</h4>
    <p><strong>Revenue Growth Leadership:</strong> {'Strong portfolio growth momentum' if avg_revenue_growth > 10 else 'Moderate growth profile' if avg_revenue_growth > 5 else 'Growth acceleration needed'} across portfolio companies</p>
    <p><strong>Operational Excellence:</strong> {'Superior operating efficiency' if avg_operating_margin > 15 else 'Competitive operating performance' if avg_operating_margin > 10 else 'Operational improvement opportunity'} in margin generation</p>
    <p><strong>Profitability Leadership:</strong> {'Excellent return profile' if avg_roe > 15 else 'Solid profitability metrics' if avg_roe > 10 else 'Profitability enhancement needed'} across peer group</p>
    """
    
    return build_info_box(summary_text, "info")


# Chart creation functions for 12A

def _create_revenue_growth_vs_operating_margin_chart(peer_analysis: Dict) -> str:
    """Create Revenue Growth vs Operating Margin scatter chart"""
    
    companies = list(peer_analysis.keys())
    revenue_growth = [peer_analysis[comp]['financial_metrics']['revenue_growth'] for comp in companies]
    operating_margin = [peer_analysis[comp]['profitability_metrics']['operating_margin'] for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': revenue_growth,
            'y': operating_margin,
            'text': [comp[:10] for comp in companies],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': revenue_growth,
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Revenue Growth (%)'},
                'line': {'width': 1, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Revenue Growth: %{x:.1f}%<br>Operating Margin: %{y:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Revenue Growth vs Operating Margin',
            'xaxis': {'title': 'Revenue Growth (%)', 'zeroline': True},
            'yaxis': {'title': 'Operating Margin (%)', 'zeroline': True},
            'hovermode': 'closest',
            'shapes': [
                {
                    'type': 'line',
                    'x0': np.median(revenue_growth),
                    'x1': np.median(revenue_growth),
                    'y0': min(operating_margin) - 2,
                    'y1': max(operating_margin) + 2,
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': min(revenue_growth) - 2,
                    'x1': max(revenue_growth) + 2,
                    'y0': np.median(operating_margin),
                    'y1': np.median(operating_margin),
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12a-1", height=500)


def _create_roe_vs_pe_chart(peer_analysis: Dict) -> str:
    """Create ROE vs P/E Ratio scatter chart"""
    
    companies = list(peer_analysis.keys())
    roe_values = [peer_analysis[comp]['profitability_metrics']['roe'] for comp in companies]
    pe_values = [peer_analysis[comp]['valuation_metrics']['pe_ratio'] if peer_analysis[comp]['valuation_metrics']['pe_ratio'] > 0 else 15 for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': roe_values,
            'y': pe_values,
            'text': [comp[:10] for comp in companies],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': roe_values,
                'colorscale': 'RdYlGn',
                'showscale': True,
                'colorbar': {'title': 'ROE (%)'},
                'line': {'width': 1, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>ROE: %{x:.1f}%<br>P/E Ratio: %{y:.1f}x<extra></extra>'
        }],
        'layout': {
            'title': 'Profitability vs Valuation (ROE vs P/E)',
            'xaxis': {'title': 'Return on Equity (%)', 'zeroline': True},
            'yaxis': {'title': 'P/E Ratio', 'zeroline': False},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12a-2", height=500)


def _create_leverage_vs_liquidity_chart(peer_analysis: Dict) -> str:
    """Create Debt/Equity vs Current Ratio scatter chart"""
    
    companies = list(peer_analysis.keys())
    debt_equity = [peer_analysis[comp]['efficiency_metrics']['debt_equity_ratio'] for comp in companies]
    current_ratio = [peer_analysis[comp]['efficiency_metrics']['current_ratio'] for comp in companies]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': debt_equity,
            'y': current_ratio,
            'text': [comp[:10] for comp in companies],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': ['green' if de < 1 else 'orange' if de < 2 else 'red' for de in debt_equity],
                'line': {'width': 1, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Debt/Equity: %{x:.2f}<br>Current Ratio: %{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Financial Strength: Leverage vs Liquidity',
            'xaxis': {'title': 'Debt/Equity Ratio', 'zeroline': True},
            'yaxis': {'title': 'Current Ratio', 'zeroline': True},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12a-3", height=500)


def _create_performance_score_rankings_chart(peer_analysis: Dict) -> str:
    """Create Performance Score Rankings bar chart"""
    
    sorted_companies = sorted(peer_analysis.items(), 
                             key=lambda x: x[1]['relative_performance']['overall_performance_score'], 
                             reverse=True)
    
    companies = [comp[:15] for comp, _ in sorted_companies]
    scores = [analysis['relative_performance']['overall_performance_score'] * 100 for _, analysis in sorted_companies]
    
    colors = ['#10b981' if score > 70 else '#f59e0b' if score > 50 else '#ef4444' for score in scores]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': scores,
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': [f'{score:.1f}' for score in scores],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': 'Overall Performance Score Rankings',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Performance Score (0-100)', 'range': [0, max(scores) * 1.1]},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12a-4", height=500)


# =============================================================================
# SUBSECTION 12B: PEER RANKING & RELATIVE PERFORMANCE ASSESSMENT
# =============================================================================

def _build_section_12b_peer_ranking(ranking_analysis: Dict, companies: Dict) -> str:
    """Build subsection 12B: Peer Ranking & Relative Performance Assessment"""
    
    if not ranking_analysis:
        return build_info_box("Peer ranking analysis unavailable.", "warning")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-12b')">
            <h2>12B. Peer Ranking & Relative Performance Assessment</h2>
            <span class="toggle-icon" id="icon-section-12b">▼</span>
        </div>
        <div class="subsection-content" id="content-section-12b">
    """
    
    # Summary statistics
    total_companies = len(ranking_analysis)
    market_leaders = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Market Leader')
    strong_competitors = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Strong Competitor')
    underperformers = sum(1 for a in ranking_analysis.values() if a['competitive_position'] in ['Below Average', 'Underperformer'])
    
    stat_cards = [
        {
            "label": "Market Leaders",
            "value": str(market_leaders),
            "description": f"{(market_leaders/total_companies)*100:.0f}% of portfolio",
            "type": "success"
        },
        {
            "label": "Strong Competitors",
            "value": str(strong_competitors),
            "description": f"{(strong_competitors/total_companies)*100:.0f}% of portfolio",
            "type": "info"
        },
        {
            "label": "Underperformers",
            "value": str(underperformers),
            "description": f"{(underperformers/total_companies)*100:.0f}% of portfolio",
            "type": "warning" if underperformers > 0 else "success"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Ranking table
    html += "<h3>Multi-Dimensional Ranking Analysis vs Portfolio Median</h3>"
    html += _create_peer_ranking_table(ranking_analysis, companies)
    
    # Ranking summary
    html += _generate_ranking_analysis_summary(ranking_analysis)
    
    # Charts (4 standalone charts from Peer Ranking Dashboard)
    html += "<h3>Ranking Analysis Charts</h3>"
    
    # Chart 1: Overall Rankings
    chart1_html = _create_overall_rankings_chart(ranking_analysis)
    if chart1_html:
        html += chart1_html
    
    # Chart 2: Category Rankings Heatmap
    chart2_html = _create_category_rankings_heatmap(ranking_analysis)
    if chart2_html:
        html += chart2_html
    
    # Chart 3: Competitive Position Distribution
    chart3_html = _create_competitive_position_distribution_chart(ranking_analysis)
    if chart3_html:
        html += chart3_html
    
    # Chart 4: Strengths vs Weaknesses
    chart4_html = _create_strengths_vs_weaknesses_chart(ranking_analysis)
    if chart4_html:
        html += chart4_html
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_peer_ranking_table(ranking_analysis: Dict, companies: Dict) -> str:
    """Create peer ranking analysis table"""
    
    sorted_companies = sorted(ranking_analysis.items(), key=lambda x: x[1]['overall_rank'])
    
    table_data = []
    for company_name, rankings in sorted_companies:
        category_rankings = rankings['category_rankings']
        total_companies = rankings['total_companies']
        
        row = {
            'Company': company_name,
            'Overall Rank': f"{rankings['overall_rank']}/{total_companies}",
            'Growth Rank': f"{category_rankings.get('growth', {}).get('average_rank', 0):.0f}",
            'Profitability Rank': f"{category_rankings.get('profitability', {}).get('average_rank', 0):.0f}",
            'Efficiency Rank': f"{category_rankings.get('efficiency', {}).get('average_rank', 0):.0f}",
            'Valuation Rank': f"{category_rankings.get('valuation', {}).get('average_rank', 0):.0f}",
            'Key Strengths': ", ".join(rankings['strengths'][:2]) if rankings['strengths'] else "None",
            'Key Weaknesses': ", ".join(rankings['weaknesses'][:2]) if rankings['weaknesses'] else "None",
            'Competitive Position': rankings['competitive_position']
        }
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    return build_data_table(df_table, table_id="peer-ranking-table", sortable=True, searchable=True)


def _generate_ranking_analysis_summary(ranking_analysis: Dict) -> str:
    """Generate ranking analysis summary"""
    
    total_companies = len(ranking_analysis)
    
    if total_companies == 0:
        return build_info_box("No ranking analysis data available.", "warning")
    
    market_leaders = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Market Leader')
    strong_competitors = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Strong Competitor')
    underperformers = sum(1 for a in ranking_analysis.values() if a['competitive_position'] in ['Below Average', 'Underperformer'])
    
    top_performer = min(ranking_analysis.items(), key=lambda x: x[1]['overall_rank'])[0]
    bottom_performer = max(ranking_analysis.items(), key=lambda x: x[1]['overall_rank'])[0]
    
    all_strengths = []
    all_weaknesses = []
    for analysis in ranking_analysis.values():
        all_strengths.extend(analysis['strengths'])
        all_weaknesses.extend(analysis['weaknesses'])
    
    strength_counts = Counter(all_strengths)
    weakness_counts = Counter(all_weaknesses)
    
    top_strength = strength_counts.most_common(1)[0][0] if strength_counts else "None"
    top_weakness = weakness_counts.most_common(1)[0][0] if weakness_counts else "None"
    
    summary_text = f"""
    <h4>Peer Ranking Summary</h4>
    <p><strong>Portfolio Ranking Distribution:</strong> {market_leaders} market leaders, {strong_competitors} strong competitors, {underperformers} underperformers across {total_companies} companies</p>
    <p><strong>Performance Leadership:</strong> {top_performer} leads overall rankings, {bottom_performer} ranks lowest requiring strategic focus</p>
    <p><strong>Competitive Position:</strong> {'Strong portfolio positioning' if market_leaders + strong_competitors >= total_companies * 0.6 else 'Mixed competitive positioning' if market_leaders + strong_competitors >= total_companies * 0.4 else 'Portfolio positioning enhancement needed'} across peer group</p>
    
    <h4>Multi-Dimensional Ranking Intelligence</h4>
    <p><strong>Portfolio Strengths:</strong> {top_strength} emerges as common competitive advantage across portfolio companies</p>
    <p><strong>Portfolio Weaknesses:</strong> {top_weakness} represents primary improvement opportunity requiring strategic attention</p>
    <p><strong>Ranking Consistency:</strong> {'Consistent high performance' if market_leaders >= total_companies * 0.4 else 'Moderate performance variation' if strong_competitors >= total_companies * 0.3 else 'Significant performance dispersion'} across ranking categories</p>
    """
    
    return build_info_box(summary_text, "info")


# Chart creation functions for 12B

def _create_overall_rankings_chart(ranking_analysis: Dict) -> str:
    """Create overall rankings bar chart"""
    
    sorted_companies = sorted(ranking_analysis.items(), key=lambda x: x[1]['overall_rank'])
    
    companies = [comp[:15] for comp, _ in sorted_companies]
    ranks = [analysis['overall_rank'] for _, analysis in sorted_companies]
    total_companies = sorted_companies[0][1]['total_companies'] if sorted_companies else 1
    
    colors = ['#10b981' if rank <= total_companies * 0.25 else '#3b82f6' if rank <= total_companies * 0.5 
              else '#f59e0b' if rank <= total_companies * 0.75 else '#ef4444' for rank in ranks]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': companies,
            'y': ranks,
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': [f'#{rank}' for rank in ranks],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Rank: #%{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Overall Peer Rankings (Lower is Better)',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Rank', 'autorange': 'reversed'},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12b-1", height=500)


def _create_category_rankings_heatmap(ranking_analysis: Dict) -> str:
    """Create category rankings heatmap"""
    
    companies = list(ranking_analysis.keys())
    categories = ['Growth', 'Profitability', 'Efficiency', 'Valuation', 'Financial Strength']
    category_keys = ['growth', 'profitability', 'efficiency', 'valuation', 'financial_strength']
    
    total_companies = ranking_analysis[companies[0]]['total_companies'] if companies else 1
    
    z_data = []
    hover_text = []
    
    for company in companies:
        row = []
        hover_row = []
        for cat_key in category_keys:
            rank = ranking_analysis[company]['category_rankings'].get(cat_key, {}).get('average_rank', total_companies/2)
            row.append(rank)
            hover_row.append(f"{company}<br>{cat_key.title()}<br>Rank: {rank:.0f}")
        z_data.append(row)
        hover_text.append(hover_row)
    
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': z_data,
            'x': categories,
            'y': [comp[:15] for comp in companies],
            'colorscale': 'RdYlGn_r',
            'reversescale': False,
            'text': [[f'{val:.0f}' for val in row] for row in z_data],
            'texttemplate': '%{text}',
            'textfont': {'size': 10},
            'hovertext': hover_text,
            'hoverinfo': 'text',
            'colorbar': {'title': 'Rank'}
        }],
        'layout': {
            'title': 'Category Rankings Heatmap (Lower Rank = Better)',
            'xaxis': {'title': 'Performance Categories', 'side': 'bottom'},
            'yaxis': {'title': 'Companies'},
            'height': 400 + len(companies) * 20
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12b-2", height=max(500, 400 + len(companies) * 20))


def _create_competitive_position_distribution_chart(ranking_analysis: Dict) -> str:
    """Create competitive position distribution pie chart"""
    
    position_counts = {}
    for analysis in ranking_analysis.values():
        position = analysis['competitive_position']
        position_counts[position] = position_counts.get(position, 0) + 1
    
    if sum(position_counts.values()) == 0:
        return ""
    
    labels = list(position_counts.keys())
    values = list(position_counts.values())
    
    color_map = {
        'Market Leader': '#059669',
        'Strong Competitor': '#10b981',
        'Average Performer': '#f59e0b',
        'Below Average': '#fb923c',
        'Underperformer': '#ef4444'
    }
    colors = [color_map.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors, 'line': {'color': 'white', 'width': 2}},
            'textposition': 'inside',
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Competitive Position Distribution',
            'showlegend': True
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12b-3", height=500)


def _create_strengths_vs_weaknesses_chart(ranking_analysis: Dict) -> str:
    """Create strengths vs weaknesses comparison chart"""
    
    all_strengths = []
    all_weaknesses = []
    for analysis in ranking_analysis.values():
        all_strengths.extend(analysis['strengths'])
        all_weaknesses.extend(analysis['weaknesses'])
    
    strength_counts = Counter(all_strengths)
    weakness_counts = Counter(all_weaknesses)
    
    all_categories = set(list(strength_counts.keys()) + list(weakness_counts.keys()))
    categories = list(all_categories)[:8]  # Limit to top 8
    
    if not categories:
        return ""
    
    strength_values = [strength_counts.get(cat, 0) for cat in categories]
    weakness_values = [-weakness_counts.get(cat, 0) for cat in categories]  # Negative for diverging chart
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Strengths',
                'x': strength_values,
                'y': categories,
                'orientation': 'h',
                'marker': {'color': '#10b981', 'line': {'width': 1, 'color': 'white'}},
                'hovertemplate': '<b>%{y}</b><br>Strengths: %{x}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Weaknesses',
                'x': weakness_values,
                'y': categories,
                'orientation': 'h',
                'marker': {'color': '#ef4444', 'line': {'width': 1, 'color': 'white'}},
                'hovertemplate': '<b>%{y}</b><br>Weaknesses: %{x}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Portfolio Strengths vs Weaknesses by Category',
            'xaxis': {'title': 'Count (Negative = Weaknesses, Positive = Strengths)'},
            'yaxis': {'title': 'Categories'},
            'barmode': 'relative',
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12b-4", height=500)


# =============================================================================
# SUBSECTION STUBS (12C-12F)
# =============================================================================

# =============================================================================
# SUBSECTION 12C: SECTOR & CATEGORY BREAKOUT ANALYSIS
# =============================================================================

def _build_section_12c_sector_analysis(sector_analysis: Dict, companies: Dict) -> str:
    """Build subsection 12C: Sector & Category Breakout Analysis"""
    
    if not sector_analysis:
        return build_info_box("Sector analysis unavailable due to insufficient profile data.", "warning")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-12c')">
            <h2>12C. Sector & Category Breakout Analysis</h2>
            <span class="toggle-icon" id="icon-section-12c">▼</span>
        </div>
        <div class="subsection-content" id="content-section-12c">
    """
    
    # Summary statistics
    total_sectors = len(sector_analysis)
    excellent_sectors = sum(1 for a in sector_analysis.values() if a['performance_rating'] == 'Excellent')
    good_sectors = sum(1 for a in sector_analysis.values() if a['performance_rating'] == 'Good')
    attractive_sectors = sum(1 for a in sector_analysis.values() 
                           if a['investment_appeal'] in ['Attractive Value', 'Deep Value'])
    
    stat_cards = [
        {
            "label": "Total Sectors",
            "value": str(total_sectors),
            "description": "Distinct industry sectors",
            "type": "info"
        },
        {
            "label": "Excellent Sectors",
            "value": str(excellent_sectors),
            "description": f"{(excellent_sectors/total_sectors)*100:.0f}% of sectors" if total_sectors > 0 else "0%",
            "type": "success"
        },
        {
            "label": "Good Sectors",
            "value": str(good_sectors),
            "description": f"{(good_sectors/total_sectors)*100:.0f}% of sectors" if total_sectors > 0 else "0%",
            "type": "info"
        },
        {
            "label": "Value Opportunities",
            "value": str(attractive_sectors),
            "description": "Sectors with attractive value",
            "type": "success" if attractive_sectors > 0 else "warning"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Sector breakdown table
    html += "<h3>Industry Classification & Sector-Based Comparative Assessment</h3>"
    html += _create_sector_breakdown_table(sector_analysis)
    
    # Sector analysis summary
    html += _generate_sector_analysis_summary(sector_analysis)
    
    # Charts (4 standalone charts)
    html += "<h3>Sector Analysis Charts</h3>"
    
    # Chart 1: Sector Performance Metrics
    chart1_html = _create_sector_performance_metrics_chart(sector_analysis)
    if chart1_html:
        html += chart1_html
    
    # Chart 2: Portfolio Sector Distribution
    chart2_html = _create_portfolio_sector_distribution_chart(sector_analysis)
    if chart2_html:
        html += chart2_html
    
    # Chart 3: Performance Rating Distribution
    chart3_html = _create_sector_performance_rating_chart(sector_analysis)
    if chart3_html:
        html += chart3_html
    
    # Chart 4: Investment Appeal Distribution
    chart4_html = _create_sector_investment_appeal_chart(sector_analysis)
    if chart4_html:
        html += chart4_html
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_sector_breakdown_table(sector_analysis: Dict) -> str:
    """Create sector breakdown table"""
    
    table_data = []
    for sector_name, sector_data in sector_analysis.items():
        row = {
            'Sector/Industry': sector_name,
            'Companies': ", ".join(sector_data['companies'][:3]) + ("..." if len(sector_data['companies']) > 3 else ""),
            'Count': len(sector_data['companies']),
            'Avg Revenue Growth (%)': f"{sector_data['avg_revenue_growth']:.1f}",
            'Avg Operating Margin (%)': f"{sector_data['avg_operating_margin']:.1f}",
            'Avg ROE (%)': f"{sector_data['avg_roe']:.1f}",
            'Avg P/E Ratio': f"{sector_data['avg_pe_ratio']:.1f}" if sector_data['avg_pe_ratio'] > 0 else "N/A",
            'Performance Rating': sector_data['performance_rating'],
            'Investment Appeal': sector_data['investment_appeal']
        }
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding for performance rating and investment appeal
    color_columns = {
        'Performance Rating': lambda x: 'excellent' if x == 'Excellent' else 'good' if x == 'Good' else 'fair' if x == 'Average' else 'poor',
        'Investment Appeal': lambda x: 'excellent' if x in ['Attractive Value', 'Deep Value'] else 'good' if x == 'Fairly Valued' else 'fair' if x == 'Value Opportunity' else 'poor'
    }
    
    return build_enhanced_table(df_table, table_id="sector-breakdown-table", 
                               color_columns=color_columns, sortable=True, searchable=True)


def _generate_sector_analysis_summary(sector_analysis: Dict) -> str:
    """Generate sector analysis summary"""
    
    total_sectors = len(sector_analysis)
    
    if total_sectors == 0:
        return build_info_box("No sector analysis data available.", "warning")
    
    excellent_sectors = sum(1 for a in sector_analysis.values() if a['performance_rating'] == 'Excellent')
    good_sectors = sum(1 for a in sector_analysis.values() if a['performance_rating'] == 'Good')
    attractive_sectors = sum(1 for a in sector_analysis.values() 
                           if a['investment_appeal'] in ['Attractive Value', 'Deep Value'])
    
    # Best performing sector
    best_sector = max(sector_analysis.items(), key=lambda x: x[1]['avg_roe'])[0] if sector_analysis else "None"
    
    # Largest sector by company count
    largest_sector = max(sector_analysis.items(), key=lambda x: x[1]['company_count'])[0] if sector_analysis else "None"
    
    summary_text = f"""
    <h4>Sector Analysis Summary</h4>
    <p><strong>Portfolio Sector Diversity:</strong> {total_sectors} distinct sectors with {largest_sector} as largest sector representation</p>
    <p><strong>Sector Performance Distribution:</strong> {excellent_sectors} excellent-performing sectors, {good_sectors} good-performing sectors</p>
    <p><strong>Investment Appeal Assessment:</strong> {attractive_sectors} sectors offering attractive value opportunities</p>
    <p><strong>Sector Leadership:</strong> {best_sector} leads in profitability metrics across sector analysis</p>
    
    <h4>Industry Positioning Intelligence</h4>
    <p><strong>Sector Quality Profile:</strong> {'High-quality sector exposure' if excellent_sectors >= total_sectors * 0.4 else 'Mixed sector quality' if good_sectors >= total_sectors * 0.3 else 'Sector improvement opportunities'} across portfolio</p>
    <p><strong>Value Opportunity Distribution:</strong> {'Strong value identification' if attractive_sectors >= total_sectors * 0.4 else 'Moderate value opportunities' if attractive_sectors >= total_sectors * 0.2 else 'Limited value sectors'} for strategic allocation</p>
    <p><strong>Sector Diversification:</strong> {'Well-diversified sector exposure' if total_sectors >= 4 else 'Moderate sector diversity' if total_sectors >= 2 else 'Concentrated sector exposure'} providing risk management</p>
    """
    
    return build_info_box(summary_text, "info")


# Chart creation functions for 12C

def _create_sector_performance_metrics_chart(sector_analysis: Dict) -> str:
    """Create sector performance metrics grouped bar chart"""
    
    sectors = list(sector_analysis.keys())
    revenue_growth = [sector_analysis[sector]['avg_revenue_growth'] for sector in sectors]
    operating_margin = [sector_analysis[sector]['avg_operating_margin'] for sector in sectors]
    roe_values = [sector_analysis[sector]['avg_roe'] for sector in sectors]
    
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Revenue Growth (%)',
                'x': [s[:15] for s in sectors],
                'y': revenue_growth,
                'marker': {'color': '#3b82f6', 'line': {'width': 1, 'color': 'white'}},
                'hovertemplate': '<b>%{x}</b><br>Revenue Growth: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Operating Margin (%)',
                'x': [s[:15] for s in sectors],
                'y': operating_margin,
                'marker': {'color': '#10b981', 'line': {'width': 1, 'color': 'white'}},
                'hovertemplate': '<b>%{x}</b><br>Operating Margin: %{y:.1f}%<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'ROE (%)',
                'x': [s[:15] for s in sectors],
                'y': roe_values,
                'marker': {'color': '#f59e0b', 'line': {'width': 1, 'color': 'white'}},
                'hovertemplate': '<b>%{x}</b><br>ROE: %{y:.1f}%<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Sector Performance Comparison',
            'xaxis': {'title': 'Sectors', 'tickangle': -45},
            'yaxis': {'title': 'Performance Metrics (%)'},
            'barmode': 'group',
            'hovermode': 'closest',
            'legend': {'orientation': 'h', 'y': -0.2}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12c-1", height=500)


def _create_portfolio_sector_distribution_chart(sector_analysis: Dict) -> str:
    """Create portfolio sector distribution bar chart"""
    
    sectors = list(sector_analysis.keys())
    company_counts = [sector_analysis[sector]['company_count'] for sector in sectors]
    
    # Sort by company count
    sorted_data = sorted(zip(sectors, company_counts), key=lambda x: x[1], reverse=True)
    sectors_sorted, counts_sorted = zip(*sorted_data) if sorted_data else ([], [])
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#fa709a']
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [s[:15] for s in sectors_sorted],
            'y': counts_sorted,
            'marker': {'color': colors[:len(sectors_sorted)], 'line': {'width': 1, 'color': 'white'}},
            'text': counts_sorted,
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Companies: %{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Sector Distribution by Company Count',
            'xaxis': {'title': 'Sectors', 'tickangle': -45},
            'yaxis': {'title': 'Number of Companies'},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12c-2", height=500)


def _create_sector_performance_rating_chart(sector_analysis: Dict) -> str:
    """Create sector performance rating pie chart"""
    
    rating_counts = {}
    for analysis in sector_analysis.values():
        rating = analysis['performance_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    if sum(rating_counts.values()) == 0:
        return ""
    
    labels = list(rating_counts.keys())
    values = list(rating_counts.values())
    
    color_map = {
        'Excellent': '#059669',
        'Good': '#10b981',
        'Average': '#f59e0b',
        'Below Average': '#ef4444'
    }
    colors = [color_map.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors, 'line': {'color': 'white', 'width': 2}},
            'textposition': 'inside',
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Sector Performance Rating Distribution',
            'showlegend': True
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12c-3", height=500)


def _create_sector_investment_appeal_chart(sector_analysis: Dict) -> str:
    """Create sector investment appeal pie chart"""
    
    appeal_counts = {}
    for analysis in sector_analysis.values():
        appeal = analysis['investment_appeal']
        appeal_counts[appeal] = appeal_counts.get(appeal, 0) + 1
    
    if sum(appeal_counts.values()) == 0:
        return ""
    
    labels = list(appeal_counts.keys())
    values = list(appeal_counts.values())
    
    color_map = {
        'Attractive Value': '#059669',
        'Deep Value': '#10b981',
        'Fairly Valued': '#3b82f6',
        'Value Opportunity': '#f59e0b',
        'Expensive': '#fb923c',
        'Avoid': '#ef4444'
    }
    colors = [color_map.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors, 'line': {'color': 'white', 'width': 2}},
            'textposition': 'inside',
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Sector Investment Appeal Distribution',
            'showlegend': True
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12c-4", height=500)


# =============================================================================
# SUBSECTION 12D: VALUATION LADDER & RELATIVE VALUATION ANALYSIS
# =============================================================================

def _build_section_12d_valuation_ladder(valuation_ladder: Dict, companies: Dict) -> str:
    """Build subsection 12D: Valuation Ladder & Relative Valuation Analysis"""
    
    if not valuation_ladder:
        return build_info_box("Valuation ladder analysis unavailable.", "warning")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-12d')">
            <h2>12D. Valuation Ladder & Relative Valuation Analysis</h2>
            <span class="toggle-icon" id="icon-section-12d">▼</span>
        </div>
        <div class="subsection-content" id="content-section-12d">
    """
    
    # Summary statistics
    total_companies = len(valuation_ladder)
    value_opportunities = sum(1 for a in valuation_ladder.values() 
                             if a['value_rating'] in ['Strong Buy', 'Buy'])
    overvalued = sum(1 for a in valuation_ladder.values() if a['value_rating'] == 'Sell')
    fairly_valued = sum(1 for a in valuation_ladder.values() if a['value_rating'] == 'Hold')
    
    # Valuation bucket counts
    deep_value = sum(1 for a in valuation_ladder.values() if a['valuation_bucket'] == 'Deep Value')
    discount = sum(1 for a in valuation_ladder.values() if a['valuation_bucket'] == 'Discount Valuation')
    
    stat_cards = [
        {
            "label": "Value Opportunities",
            "value": str(value_opportunities),
            "description": f"{(value_opportunities/total_companies)*100:.0f}% rated Buy/Strong Buy" if total_companies > 0 else "0%",
            "type": "success" if value_opportunities > 0 else "warning"
        },
        {
            "label": "Fairly Valued",
            "value": str(fairly_valued),
            "description": f"{(fairly_valued/total_companies)*100:.0f}% rated Hold" if total_companies > 0 else "0%",
            "type": "info"
        },
        {
            "label": "Overvalued",
            "value": str(overvalued),
            "description": f"{(overvalued/total_companies)*100:.0f}% rated Sell" if total_companies > 0 else "0%",
            "type": "danger" if overvalued > 0 else "success"
        },
        {
            "label": "Deep Value + Discount",
            "value": str(deep_value + discount),
            "description": "Companies trading at discount",
            "type": "success" if deep_value + discount > 0 else "info"
        }
    ]
    
    html += build_stat_grid(stat_cards)
    
    # Valuation comparison table
    html += "<h3>Cross-Company Valuation Comparison & Valuation Buckets</h3>"
    html += _create_valuation_comparison_table(valuation_ladder)
    
    # Valuation ladder summary
    html += _generate_valuation_ladder_summary(valuation_ladder)
    
    # Charts (4 standalone charts)
    html += "<h3>Valuation Analysis Charts</h3>"
    
    # Chart 1: P/E Ratio Ladder
    chart1_html = _create_pe_ratio_ladder_chart(valuation_ladder)
    if chart1_html:
        html += chart1_html
    
    # Chart 2: EV/EBITDA Comparison
    chart2_html = _create_ev_ebitda_comparison_chart(valuation_ladder)
    if chart2_html:
        html += chart2_html
    
    # Chart 3: Valuation Bucket Distribution
    chart3_html = _create_valuation_bucket_distribution_chart(valuation_ladder)
    if chart3_html:
        html += chart3_html
    
    # Chart 4: Value Rating Distribution
    chart4_html = _create_value_rating_distribution_chart(valuation_ladder)
    if chart4_html:
        html += chart4_html
    
    html += """
        </div>
    </div>
    """
    
    return html


def _create_valuation_comparison_table(valuation_ladder: Dict) -> str:
    """Create valuation comparison table"""
    
    table_data = []
    for company_name, val_data in valuation_ladder.items():
        row = {
            'Company': company_name,
            'P/E Ratio': f"{val_data['pe_ratio']:.1f}x" if val_data['pe_ratio'] > 0 else "N/A",
            'P/B Ratio': f"{val_data['pb_ratio']:.1f}x" if val_data['pb_ratio'] > 0 else "N/A",
            'EV/EBITDA': f"{val_data['ev_ebitda']:.1f}x" if val_data['ev_ebitda'] > 0 else "N/A",
            'EV/Sales': f"{val_data['ev_sales']:.1f}x" if val_data['ev_sales'] > 0 else "N/A",
            'Valuation Bucket': val_data['valuation_bucket'],
            'Relative Position': val_data['relative_position'],
            'Value Rating': val_data['value_rating'],
            'Investment Thesis': val_data['investment_thesis']
        }
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding for ratings
    color_columns = {
        'Valuation Bucket': lambda x: 'excellent' if x == 'Deep Value' else 'good' if x == 'Discount Valuation' else 'fair' if x == 'Fair Valuation' else 'poor',
        'Value Rating': lambda x: 'excellent' if x == 'Strong Buy' else 'good' if x == 'Buy' else 'fair' if x == 'Hold' else 'poor'
    }
    
    badge_columns = ['Valuation Bucket', 'Value Rating', 'Relative Position']
    
    return build_enhanced_table(df_table, table_id="valuation-ladder-table", 
                               color_columns=color_columns, badge_columns=badge_columns,
                               sortable=True, searchable=True)


def _generate_valuation_ladder_summary(valuation_ladder: Dict) -> str:
    """Generate valuation ladder summary"""
    
    total_companies = len(valuation_ladder)
    
    if total_companies == 0:
        return build_info_box("No valuation ladder data available.", "warning")
    
    # Valuation bucket distribution
    bucket_counts = {}
    rating_counts = {}
    
    for analysis in valuation_ladder.values():
        bucket = analysis['valuation_bucket']
        rating = analysis['value_rating']
        
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    value_opportunities = rating_counts.get('Strong Buy', 0) + rating_counts.get('Buy', 0)
    overvalued_companies = rating_counts.get('Sell', 0)
    
    # Best value opportunity
    strong_buy_companies = [name for name, analysis in valuation_ladder.items() 
                           if analysis['value_rating'] == 'Strong Buy']
    best_value = strong_buy_companies[0] if strong_buy_companies else "None identified"
    
    summary_text = f"""
    <h4>Valuation Ladder Summary</h4>
    <p><strong>Portfolio Valuation Profile:</strong> {total_companies} companies with {bucket_counts.get('Deep Value', 0) + bucket_counts.get('Discount Valuation', 0)} value opportunities identified</p>
    <p><strong>Value Rating Distribution:</strong> {value_opportunities} buy-rated companies, {rating_counts.get('Hold', 0)} hold-rated companies, {overvalued_companies} overvalued companies</p>
    <p><strong>Value Opportunity Leader:</strong> {best_value} represents strongest value opportunity in portfolio</p>
    <p><strong>Valuation Diversification:</strong> {'Well-distributed valuation exposure' if len(bucket_counts) >= 3 else 'Moderate valuation diversity' if len(bucket_counts) >= 2 else 'Concentrated valuation profile'} across companies</p>
    
    <h4>Relative Valuation Intelligence</h4>
    <p><strong>Value Identification:</strong> {'Excellent value opportunity portfolio' if value_opportunities >= total_companies * 0.5 else 'Moderate value opportunities' if value_opportunities >= total_companies * 0.3 else 'Limited value identification'} for strategic allocation</p>
    <p><strong>Overvaluation Risk:</strong> {'Minimal overvaluation exposure' if overvalued_companies <= total_companies * 0.2 else 'Moderate overvaluation risk' if overvalued_companies <= total_companies * 0.4 else 'Significant overvaluation concern'} requiring portfolio review</p>
    <p><strong>Valuation-Based Strategy:</strong> Clear valuation differentiation enabling value-focused investment approach</p>
    """
    
    return build_info_box(summary_text, "info")


# Chart creation functions for 12D

def _create_pe_ratio_ladder_chart(valuation_ladder: Dict) -> str:
    """Create P/E ratio ladder sorted bar chart"""
    
    # Filter companies with valid P/E ratios
    pe_companies = [(name, data['pe_ratio']) for name, data in valuation_ladder.items() 
                    if data['pe_ratio'] > 0 and data['pe_ratio'] < 100]
    
    if not pe_companies:
        return ""
    
    # Sort by P/E ratio
    pe_companies.sort(key=lambda x: x[1])
    companies, pe_values = zip(*pe_companies)
    
    median_pe = np.median(pe_values)
    
    # Color code based on relative to median
    colors = ['#10b981' if pe < median_pe * 0.8 else '#3b82f6' if pe < median_pe * 1.2 
              else '#f59e0b' if pe < median_pe * 1.5 else '#ef4444' for pe in pe_values]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [c[:15] for c in companies],
            'y': pe_values,
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': [f'{pe:.1f}x' for pe in pe_values],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>P/E Ratio: %{y:.1f}x<extra></extra>'
        }],
        'layout': {
            'title': 'P/E Ratio Valuation Ladder (Sorted Low to High)',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'P/E Ratio'},
            'showlegend': False,
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies) - 0.5,
                'y0': median_pe,
                'y1': median_pe,
                'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
            }],
            'annotations': [{
                'x': len(companies) - 1,
                'y': median_pe,
                'text': f'Median: {median_pe:.1f}x',
                'showarrow': False,
                'yshift': 10,
                'bgcolor': 'rgba(255, 0, 0, 0.1)',
                'bordercolor': 'red'
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12d-1", height=500)


def _create_ev_ebitda_comparison_chart(valuation_ladder: Dict) -> str:
    """Create EV/EBITDA comparison bar chart"""
    
    companies = list(valuation_ladder.keys())
    ev_ebitda = [valuation_ladder[comp]['ev_ebitda'] if valuation_ladder[comp]['ev_ebitda'] > 0 
                 else 0 for comp in companies]
    
    # Filter out zero values
    valid_data = [(comp, ev) for comp, ev in zip(companies, ev_ebitda) if ev > 0]
    
    if not valid_data:
        return ""
    
    companies_valid, ev_values = zip(*valid_data)
    
    median_ev = np.median(ev_values)
    
    colors = ['#10b981' if ev < median_ev else '#f59e0b' for ev in ev_values]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': [c[:15] for c in companies_valid],
            'y': ev_values,
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': [f'{ev:.1f}x' for ev in ev_values],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>EV/EBITDA: %{y:.1f}x<extra></extra>'
        }],
        'layout': {
            'title': 'EV/EBITDA Valuation Comparison',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'EV/EBITDA Multiple'},
            'showlegend': False,
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies_valid) - 0.5,
                'y0': median_ev,
                'y1': median_ev,
                'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
            }],
            'annotations': [{
                'x': len(companies_valid) - 1,
                'y': median_ev,
                'text': f'Median: {median_ev:.1f}x',
                'showarrow': False,
                'yshift': 10,
                'bgcolor': 'rgba(255, 0, 0, 0.1)',
                'bordercolor': 'red'
            }]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12d-2", height=500)


def _create_valuation_bucket_distribution_chart(valuation_ladder: Dict) -> str:
    """Create valuation bucket distribution pie chart"""
    
    bucket_counts = {}
    for analysis in valuation_ladder.values():
        bucket = analysis['valuation_bucket']
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    
    if sum(bucket_counts.values()) == 0:
        return ""
    
    labels = list(bucket_counts.keys())
    values = list(bucket_counts.values())
    
    color_map = {
        'Deep Value': '#059669',
        'Discount Valuation': '#10b981',
        'Fair Valuation': '#3b82f6',
        'Premium Valuation': '#ef4444'
    }
    colors = [color_map.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors, 'line': {'color': 'white', 'width': 2}},
            'textposition': 'inside',
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Valuation Bucket Distribution',
            'showlegend': True
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12d-3", height=500)


def _create_value_rating_distribution_chart(valuation_ladder: Dict) -> str:
    """Create value rating distribution pie chart"""
    
    rating_counts = {}
    for analysis in valuation_ladder.values():
        rating = analysis['value_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    if sum(rating_counts.values()) == 0:
        return ""
    
    labels = list(rating_counts.keys())
    values = list(rating_counts.values())
    
    color_map = {
        'Strong Buy': '#059669',
        'Buy': '#10b981',
        'Hold': '#f59e0b',
        'Sell': '#ef4444'
    }
    colors = [color_map.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'pie',
            'labels': labels,
            'values': values,
            'marker': {'colors': colors, 'line': {'color': 'white', 'width': 2}},
            'textposition': 'inside',
            'textinfo': 'label+percent',
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Value Rating Distribution',
            'showlegend': True
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12d-4", height=500)


# =============================================================================
# HELPER FUNCTIONS - SECTOR ANALYSIS
# =============================================================================

def _generate_sector_analysis(df: pd.DataFrame, companies: Dict[str, str], 
                             profiles_df: pd.DataFrame, peer_analysis: Dict) -> Dict[str, Dict]:
    """Generate sector-based analysis"""
    
    if profiles_df.empty or not peer_analysis:
        return {}
    
    sector_analysis = {}
    
    # Group companies by sector/industry
    sector_groups = {}
    for company_name in companies.keys():
        if company_name in peer_analysis:
            company_profile = profiles_df[profiles_df['Company'] == company_name]
            
            if not company_profile.empty:
                sector = company_profile.iloc[0].get('sector', 'Unknown')
                industry = company_profile.iloc[0].get('industry', 'Unknown')
                
                if sector == 'Unknown' and industry != 'Unknown':
                    sector = industry
                elif sector == 'Unknown':
                    sector = 'Diversified'
            else:
                sector = 'Unknown'
            
            if sector not in sector_groups:
                sector_groups[sector] = []
            sector_groups[sector].append(company_name)
    
    # Analyze each sector
    for sector_name, companies_in_sector in sector_groups.items():
        if len(companies_in_sector) == 0:
            continue
        
        sector_metrics = _calculate_sector_metrics(companies_in_sector, peer_analysis)
        performance_rating = _assess_sector_performance(sector_metrics)
        investment_appeal = _assess_investment_appeal(sector_metrics, performance_rating)
        
        sector_analysis[sector_name] = {
            'companies': companies_in_sector,
            'company_count': len(companies_in_sector),
            'avg_revenue_growth': sector_metrics['avg_revenue_growth'],
            'avg_operating_margin': sector_metrics['avg_operating_margin'],
            'avg_roe': sector_metrics['avg_roe'],
            'avg_pe_ratio': sector_metrics['avg_pe_ratio'],
            'avg_debt_equity': sector_metrics['avg_debt_equity'],
            'performance_rating': performance_rating,
            'investment_appeal': investment_appeal,
            'sector_leader': _identify_sector_leader(companies_in_sector, peer_analysis)
        }
    
    return sector_analysis


def _calculate_sector_metrics(companies_in_sector: List[str], peer_analysis: Dict) -> Dict[str, float]:
    """Calculate average metrics for a sector"""
    
    revenue_growth_values = []
    operating_margin_values = []
    roe_values = []
    pe_ratio_values = []
    debt_equity_values = []
    
    for company in companies_in_sector:
        if company in peer_analysis:
            analysis = peer_analysis[company]
            
            revenue_growth_values.append(analysis['financial_metrics']['revenue_growth'])
            operating_margin_values.append(analysis['profitability_metrics']['operating_margin'])
            roe_values.append(analysis['profitability_metrics']['roe'])
            
            pe_ratio = analysis['valuation_metrics']['pe_ratio']
            if pe_ratio > 0 and pe_ratio < 100:
                pe_ratio_values.append(pe_ratio)
            
            debt_equity_values.append(analysis['efficiency_metrics']['debt_equity_ratio'])
    
    return {
        'avg_revenue_growth': np.mean(revenue_growth_values) if revenue_growth_values else 0,
        'avg_operating_margin': np.mean(operating_margin_values) if operating_margin_values else 0,
        'avg_roe': np.mean(roe_values) if roe_values else 0,
        'avg_pe_ratio': np.mean(pe_ratio_values) if pe_ratio_values else 0,
        'avg_debt_equity': np.mean(debt_equity_values) if debt_equity_values else 0
    }


def _assess_sector_performance(sector_metrics: Dict[str, float]) -> str:
    """Assess sector performance rating"""
    
    growth_score = min(10, max(0, sector_metrics['avg_revenue_growth'] / 2))
    margin_score = min(10, max(0, sector_metrics['avg_operating_margin'] / 2))
    roe_score = min(10, max(0, sector_metrics['avg_roe'] / 2))
    debt_score = max(0, 10 - sector_metrics['avg_debt_equity'] * 2)
    
    overall_score = (growth_score + margin_score + roe_score + debt_score) / 4
    
    if overall_score >= 7:
        return "Excellent"
    elif overall_score >= 5:
        return "Good"
    elif overall_score >= 3:
        return "Average"
    else:
        return "Below Average"


def _assess_investment_appeal(sector_metrics: Dict[str, float], performance_rating: str) -> str:
    """Assess investment appeal of sector"""
    
    pe_ratio = sector_metrics['avg_pe_ratio']
    
    if performance_rating in ['Excellent', 'Good']:
        if pe_ratio < 15:
            return "Attractive Value"
        elif pe_ratio < 25:
            return "Fairly Valued"
        else:
            return "Expensive"
    else:
        if pe_ratio < 12:
            return "Deep Value"
        elif pe_ratio < 18:
            return "Value Opportunity"
        else:
            return "Avoid"


def _identify_sector_leader(companies_in_sector: List[str], peer_analysis: Dict) -> str:
    """Identify the leading company in the sector"""
    
    best_company = None
    best_score = -1
    
    for company in companies_in_sector:
        if company in peer_analysis:
            score = peer_analysis[company]['relative_performance']['overall_performance_score']
            if score > best_score:
                best_score = score
                best_company = company
    
    return best_company or companies_in_sector[0] if companies_in_sector else "None"


# =============================================================================
# HELPER FUNCTIONS - VALUATION LADDER ANALYSIS
# =============================================================================

def _generate_valuation_ladder_analysis(df: pd.DataFrame, companies: Dict[str, str], 
                                       valuation_analysis: Dict) -> Dict[str, Dict]:
    """Generate valuation ladder comparative analysis"""
    
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year].copy()
    
    if latest_data.empty:
        return {}
    
    valuation_ladder = {}
    
    all_pe_ratios = []
    all_pb_ratios = []
    all_ev_ebitda = []
    all_ev_sales = []
    
    for company_name in companies.keys():
        company_data = latest_data[latest_data['Company'] == company_name]
        
        if company_data.empty:
            continue
        
        row = company_data.iloc[0]
        
        pe_ratio = row.get('priceToEarningsRatio', 0)
        pb_ratio = row.get('priceToBookRatio', 0)
        ev_ebitda = row.get('enterpriseValueMultiple', 0)
        ev_sales = row.get('evToSales', 0)
        
        if 0 < pe_ratio < 100:
            all_pe_ratios.append(pe_ratio)
        if 0 < pb_ratio < 20:
            all_pb_ratios.append(pb_ratio)
        if 0 < ev_ebitda < 50:
            all_ev_ebitda.append(ev_ebitda)
        if 0 < ev_sales < 20:
            all_ev_sales.append(ev_sales)
        
        valuation_ladder[company_name] = {
            'pe_ratio': pe_ratio if 0 < pe_ratio < 100 else 0,
            'pb_ratio': pb_ratio if 0 < pb_ratio < 20 else 0,
            'ev_ebitda': ev_ebitda if 0 < ev_ebitda < 50 else 0,
            'ev_sales': ev_sales if 0 < ev_sales < 20 else 0
        }
    
    val_stats = {
        'pe_median': np.median(all_pe_ratios) if all_pe_ratios else 15,
        'pb_median': np.median(all_pb_ratios) if all_pb_ratios else 2,
        'ev_ebitda_median': np.median(all_ev_ebitda) if all_ev_ebitda else 12,
        'ev_sales_median': np.median(all_ev_sales) if all_ev_sales else 3
    }
    
    for company_name in valuation_ladder.keys():
        val_data = valuation_ladder[company_name]
        
        valuation_bucket = _classify_valuation_bucket(val_data, val_stats)
        relative_position = _assess_relative_position(val_data, val_stats)
        value_rating = _assess_value_rating(valuation_bucket, relative_position)
        investment_thesis = _generate_investment_thesis(val_data, val_stats, value_rating)
        
        valuation_ladder[company_name].update({
            'valuation_bucket': valuation_bucket,
            'relative_position': relative_position,
            'value_rating': value_rating,
            'investment_thesis': investment_thesis
        })
    
    return valuation_ladder


def _classify_valuation_bucket(val_data: Dict, val_stats: Dict) -> str:
    """Classify company into valuation bucket"""
    
    pe_ratio = val_data['pe_ratio']
    pb_ratio = val_data['pb_ratio']
    ev_ebitda = val_data['ev_ebitda']
    
    pe_median = val_stats['pe_median']
    pb_median = val_stats['pb_median']
    ev_ebitda_median = val_stats['ev_ebitda_median']
    
    above_median_count = 0
    total_valid_metrics = 0
    
    if pe_ratio > 0:
        total_valid_metrics += 1
        if pe_ratio > pe_median:
            above_median_count += 1
    
    if pb_ratio > 0:
        total_valid_metrics += 1
        if pb_ratio > pb_median:
            above_median_count += 1
    
    if ev_ebitda > 0:
        total_valid_metrics += 1
        if ev_ebitda > ev_ebitda_median:
            above_median_count += 1
    
    if total_valid_metrics == 0:
        return "Unknown"
    
    above_median_ratio = above_median_count / total_valid_metrics
    
    if above_median_ratio >= 0.75:
        return "Premium Valuation"
    elif above_median_ratio >= 0.5:
        return "Fair Valuation"
    elif above_median_ratio >= 0.25:
        return "Discount Valuation"
    else:
        return "Deep Value"


def _assess_relative_position(val_data: Dict, val_stats: Dict) -> str:
    """Assess relative valuation position"""
    
    pe_ratio = val_data['pe_ratio']
    pe_median = val_stats['pe_median']
    
    if pe_ratio <= 0:
        return "Not Available"
    
    if pe_ratio < pe_median * 0.7:
        return "Significant Discount"
    elif pe_ratio < pe_median * 0.9:
        return "Moderate Discount"
    elif pe_ratio <= pe_median * 1.1:
        return "At Median"
    elif pe_ratio <= pe_median * 1.3:
        return "Moderate Premium"
    else:
        return "Significant Premium"


def _assess_value_rating(valuation_bucket: str, relative_position: str) -> str:
    """Assess overall value rating"""
    
    if valuation_bucket == "Deep Value" or relative_position == "Significant Discount":
        return "Strong Buy"
    elif valuation_bucket == "Discount Valuation" or relative_position == "Moderate Discount":
        return "Buy"
    elif valuation_bucket == "Fair Valuation" or relative_position == "At Median":
        return "Hold"
    elif valuation_bucket == "Premium Valuation" and relative_position in ["Moderate Premium", "Significant Premium"]:
        return "Sell"
    else:
        return "Hold"


def _generate_investment_thesis(val_data: Dict, val_stats: Dict, value_rating: str) -> str:
    """Generate investment thesis based on valuation"""
    
    if value_rating == "Strong Buy":
        return "Compelling Value"
    elif value_rating == "Buy":
        return "Attractive Entry"
    elif value_rating == "Hold":
        return "Fair Value"
    elif value_rating == "Sell":
        return "Overvalued"
    else:
        return "Neutral"


# =============================================================================
# SUBSECTION 12E: PEER CONTEXT VISUALIZATION DASHBOARD
# =============================================================================

def _build_section_12e_visualization_dashboard(peer_analysis: Dict, ranking_analysis: Dict,
                                               sector_analysis: Dict, valuation_ladder: Dict,
                                               risk_scoring: Dict) -> str:
    """Build subsection 12E: Peer Context Visualization Dashboard"""
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-12e')">
            <h2>12E. Peer Context Visualization Dashboard</h2>
            <span class="toggle-icon" id="icon-section-12e">▼</span>
        </div>
        <div class="subsection-content" id="content-section-12e">
    """
    
    html += "<h3>Comprehensive Visual Analysis</h3>"
    html += build_info_box(
        "Interactive visualization suite providing multi-dimensional peer analysis across performance, "
        "risk, sector positioning, and portfolio intelligence metrics.",
        "info"
    )
    
    # Chart 1: Risk-Return Matrix
    html += "<h4>Risk-Return Portfolio Matrix</h4>"
    chart1_html = _create_risk_return_matrix_chart(peer_analysis, risk_scoring)
    if chart1_html:
        html += chart1_html
    else:
        html += build_info_box("Risk-return matrix unavailable due to insufficient data.", "warning")
    
    # Chart 2: Portfolio Performance Summary Dashboard
    html += "<h4>Portfolio Performance Summary</h4>"
    chart2_html = _create_portfolio_performance_summary_chart(peer_analysis)
    if chart2_html:
        html += chart2_html
    
    # Chart 3: Competitive Positioning Overview
    html += "<h4>Competitive Positioning Overview</h4>"
    chart3_html = _create_competitive_positioning_overview_chart(ranking_analysis)
    if chart3_html:
        html += chart3_html
    
    # Chart 4: Performance vs Growth Bubble Chart
    html += "<h4>Performance vs Growth Analysis</h4>"
    chart4_html = _create_performance_vs_growth_bubble_chart(peer_analysis)
    if chart4_html:
        html += chart4_html
    
    # Chart 5: Sector Performance Comparison
    html += "<h4>Sector Performance Comparison</h4>"
    chart5_html = _create_sector_performance_comparison_chart(sector_analysis)
    if chart5_html:
        html += chart5_html
    
    # Chart 6: Portfolio Intelligence Score Gauge
    html += "<h4>Portfolio Peer Intelligence Score</h4>"
    chart6_html = _create_portfolio_intelligence_gauge_chart(peer_analysis, ranking_analysis, valuation_ladder)
    if chart6_html:
        html += chart6_html
    
    # Chart 7: Multi-Metric Radar Chart
    html += "<h4>Multi-Dimensional Company Comparison</h4>"
    chart7_html = _create_multi_metric_radar_chart(peer_analysis)
    if chart7_html:
        html += chart7_html
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# CHART CREATION FUNCTIONS FOR 12E
# =============================================================================

def _create_risk_return_matrix_chart(peer_analysis: Dict, risk_scoring: Dict) -> str:
    """Create risk-return matrix scatter chart"""
    
    if not peer_analysis:
        return ""
    
    # Find common companies in both analyses
    common_companies = []
    performance_scores = []
    risk_scores = []
    
    for company in peer_analysis.keys():
        if risk_scoring and company in risk_scoring:
            common_companies.append(company)
            performance_scores.append(peer_analysis[company]['relative_performance']['overall_performance_score'] * 100)
            risk_scores.append(risk_scoring[company]['composite_risk_score'])
        else:
            # If no risk scoring, use a default moderate risk
            common_companies.append(company)
            performance_scores.append(peer_analysis[company]['relative_performance']['overall_performance_score'] * 100)
            risk_scores.append(5.0)  # Default middle risk
    
    if not common_companies:
        return ""
    
    median_risk = np.median(risk_scores)
    median_performance = np.median(performance_scores)
    
    # Determine quadrant colors
    colors = []
    for perf, risk in zip(performance_scores, risk_scores):
        if perf >= median_performance and risk < median_risk:
            colors.append('#10b981')  # Green - High return, low risk
        elif perf >= median_performance and risk >= median_risk:
            colors.append('#f59e0b')  # Orange - High return, high risk
        elif perf < median_performance and risk < median_risk:
            colors.append('#3b82f6')  # Blue - Low return, low risk
        else:
            colors.append('#ef4444')  # Red - Low return, high risk
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': risk_scores,
            'y': performance_scores,
            'text': [comp[:10] for comp in common_companies],
            'textposition': 'top center',
            'marker': {
                'size': 15,
                'color': colors,
                'line': {'width': 2, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Risk Score: %{x:.1f}<br>Performance Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Risk-Return Matrix',
            'xaxis': {'title': 'Risk Score (0-10, Lower is Better)', 'range': [0, max(risk_scores) * 1.1]},
            'yaxis': {'title': 'Performance Score (0-100, Higher is Better)', 'range': [0, max(performance_scores) * 1.1]},
            'shapes': [
                {
                    'type': 'line',
                    'x0': median_risk,
                    'x1': median_risk,
                    'y0': 0,
                    'y1': max(performance_scores) * 1.1,
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': max(risk_scores) * 1.1,
                    'y0': median_performance,
                    'y1': median_performance,
                    'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {
                    'x': median_risk * 0.5,
                    'y': median_performance * 1.5,
                    'text': 'Low Risk<br>High Return<br>(Ideal)',
                    'showarrow': False,
                    'bgcolor': 'rgba(16, 185, 129, 0.1)',
                    'bordercolor': '#10b981',
                    'borderwidth': 2
                },
                {
                    'x': median_risk * 1.5,
                    'y': median_performance * 1.5,
                    'text': 'High Risk<br>High Return',
                    'showarrow': False,
                    'bgcolor': 'rgba(245, 158, 11, 0.1)',
                    'bordercolor': '#f59e0b',
                    'borderwidth': 2
                },
                {
                    'x': median_risk * 0.5,
                    'y': median_performance * 0.5,
                    'text': 'Low Risk<br>Low Return',
                    'showarrow': False,
                    'bgcolor': 'rgba(59, 130, 246, 0.1)',
                    'bordercolor': '#3b82f6',
                    'borderwidth': 2
                },
                {
                    'x': median_risk * 1.5,
                    'y': median_performance * 0.5,
                    'text': 'High Risk<br>Low Return<br>(Avoid)',
                    'showarrow': False,
                    'bgcolor': 'rgba(239, 68, 68, 0.1)',
                    'bordercolor': '#ef4444',
                    'borderwidth': 2
                }
            ]
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-1", height=600)


def _create_portfolio_performance_summary_chart(peer_analysis: Dict) -> str:
    """Create portfolio performance summary bar chart"""
    
    if not peer_analysis:
        return ""
    
    companies = list(peer_analysis.keys())
    revenue_growth = [peer_analysis[comp]['financial_metrics']['revenue_growth'] for comp in companies]
    operating_margin = [peer_analysis[comp]['profitability_metrics']['operating_margin'] for comp in companies]
    roe_values = [peer_analysis[comp]['profitability_metrics']['roe'] for comp in companies]
    performance_scores = [peer_analysis[comp]['relative_performance']['overall_performance_score'] * 100 for comp in companies]
    
    metrics = ['Avg Revenue\nGrowth (%)', 'Avg Operating\nMargin (%)', 'Avg ROE (%)', 'Avg Performance\nScore']
    values = [np.mean(revenue_growth), np.mean(operating_margin), np.mean(roe_values), np.mean(performance_scores)]
    
    colors = ['#667eea', '#10b981', '#f59e0b', '#3b82f6']
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': metrics,
            'y': values,
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': [f'{v:.1f}' for v in values],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Value: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Performance Summary - Key Metrics',
            'xaxis': {'title': ''},
            'yaxis': {'title': 'Metric Value'},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-2", height=500)


def _create_competitive_positioning_overview_chart(ranking_analysis: Dict) -> str:
    """Create competitive positioning stacked bar chart"""
    
    if not ranking_analysis:
        return ""
    
    position_counts = {}
    for analysis in ranking_analysis.values():
        position = analysis['competitive_position']
        position_counts[position] = position_counts.get(position, 0) + 1
    
    if sum(position_counts.values()) == 0:
        return ""
    
    # Order positions from best to worst
    position_order = ['Market Leader', 'Strong Competitor', 'Average Performer', 'Below Average', 'Underperformer']
    labels = [pos for pos in position_order if pos in position_counts]
    values = [position_counts[pos] for pos in labels]
    
    color_map = {
        'Market Leader': '#059669',
        'Strong Competitor': '#10b981',
        'Average Performer': '#f59e0b',
        'Below Average': '#fb923c',
        'Underperformer': '#ef4444'
    }
    colors = [color_map.get(label, '#94a3b8') for label in labels]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': labels,
            'y': values,
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': values,
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Companies: %{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Competitive Position Distribution',
            'xaxis': {'title': 'Competitive Position', 'tickangle': -30},
            'yaxis': {'title': 'Number of Companies'},
            'showlegend': False
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-3", height=500)


def _create_performance_vs_growth_bubble_chart(peer_analysis: Dict) -> str:
    """Create performance vs growth bubble chart with operating margin as bubble size"""
    
    if not peer_analysis:
        return ""
    
    companies = list(peer_analysis.keys())
    revenue_growth = [peer_analysis[comp]['financial_metrics']['revenue_growth'] for comp in companies]
    performance_scores = [peer_analysis[comp]['relative_performance']['overall_performance_score'] * 100 for comp in companies]
    operating_margin = [peer_analysis[comp]['profitability_metrics']['operating_margin'] for comp in companies]
    
    # Bubble size based on operating margin
    bubble_sizes = [max(10, margin * 3) for margin in operating_margin]
    
    fig_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': revenue_growth,
            'y': performance_scores,
            'text': [comp[:10] for comp in companies],
            'textposition': 'top center',
            'marker': {
                'size': bubble_sizes,
                'color': operating_margin,
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Operating<br>Margin (%)'},
                'line': {'width': 2, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Revenue Growth: %{x:.1f}%<br>Performance Score: %{y:.1f}<br>Operating Margin: %{marker.color:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Performance vs Growth Analysis (Bubble Size = Operating Margin)',
            'xaxis': {'title': 'Revenue Growth (%)', 'zeroline': True},
            'yaxis': {'title': 'Overall Performance Score (0-100)', 'zeroline': False},
            'hovermode': 'closest'
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-4", height=600)


def _create_sector_performance_comparison_chart(sector_analysis: Dict) -> str:
    """Create sector performance horizontal bar chart"""
    
    if not sector_analysis:
        return ""
    
    sectors = list(sector_analysis.keys())
    sector_roe = [sector_analysis[sector]['avg_roe'] for sector in sectors]
    
    # Sort by ROE
    sorted_data = sorted(zip(sectors, sector_roe), key=lambda x: x[1], reverse=True)
    sectors_sorted, roe_sorted = zip(*sorted_data) if sorted_data else ([], [])
    
    # Color code based on performance
    colors = ['#10b981' if roe > 15 else '#3b82f6' if roe > 10 else '#f59e0b' if roe > 5 else '#ef4444' for roe in roe_sorted]
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': roe_sorted,
            'y': [s[:20] for s in sectors_sorted],
            'orientation': 'h',
            'marker': {'color': colors, 'line': {'width': 1, 'color': 'white'}},
            'text': [f'{roe:.1f}%' for roe in roe_sorted],
            'textposition': 'outside',
            'hovertemplate': '<b>%{y}</b><br>Avg ROE: %{x:.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Sector Performance Analysis by Average ROE',
            'xaxis': {'title': 'Average ROE (%)'},
            'yaxis': {'title': 'Sector'},
            'showlegend': False,
            'height': 400 + len(sectors) * 30
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-5", height=max(500, 400 + len(sectors) * 30))


def _create_portfolio_intelligence_gauge_chart(peer_analysis: Dict, ranking_analysis: Dict, 
                                               valuation_ladder: Dict) -> str:
    """Create portfolio intelligence score indicator"""
    
    # Calculate overall portfolio intelligence score
    intelligence_components = []
    
    if peer_analysis:
        avg_performance = np.mean([analysis['relative_performance']['overall_performance_score'] 
                                 for analysis in peer_analysis.values()])
        intelligence_components.append(avg_performance)
    
    if ranking_analysis:
        market_leaders = sum(1 for analysis in ranking_analysis.values() 
                           if analysis['competitive_position'] == 'Market Leader')
        leadership_ratio = market_leaders / len(ranking_analysis) if ranking_analysis else 0
        intelligence_components.append(leadership_ratio)
    
    if valuation_ladder:
        value_opportunities = sum(1 for analysis in valuation_ladder.values() 
                                if analysis['value_rating'] in ['Strong Buy', 'Buy'])
        value_ratio = value_opportunities / len(valuation_ladder) if valuation_ladder else 0
        intelligence_components.append(value_ratio)
    
    if intelligence_components:
        portfolio_intelligence_score = np.mean(intelligence_components) * 10
    else:
        portfolio_intelligence_score = 5
    
    # Create gauge chart
    fig_data = {
        'data': [{
            'type': 'indicator',
            'mode': 'gauge+number+delta',
            'value': portfolio_intelligence_score,
            'title': {'text': 'Portfolio Peer Intelligence Score', 'font': {'size': 24}},
            'delta': {'reference': 7.0, 'increasing': {'color': '#10b981'}},
            'gauge': {
                'axis': {'range': [0, 10], 'tickwidth': 2, 'tickcolor': 'darkgray'},
                'bar': {'color': '#667eea', 'thickness': 0.75},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 3], 'color': '#fecaca'},
                    {'range': [3, 5], 'color': '#fed7aa'},
                    {'range': [5, 7], 'color': '#fef08a'},
                    {'range': [7, 8.5], 'color': '#bbf7d0'},
                    {'range': [8.5, 10], 'color': '#86efac'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 7.0
                }
            }
        }],
        'layout': {
            'height': 400,
            'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 50}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-6", height=400)


def _create_multi_metric_radar_chart(peer_analysis: Dict) -> str:
    """Create multi-metric radar chart for top 5 companies"""
    
    if not peer_analysis:
        return ""
    
    # Get top 5 companies by performance score
    sorted_companies = sorted(peer_analysis.items(), 
                             key=lambda x: x[1]['relative_performance']['overall_performance_score'], 
                             reverse=True)
    top_companies = sorted_companies[:min(5, len(sorted_companies))]
    
    if not top_companies:
        return ""
    
    categories = ['Revenue Growth', 'Operating Margin', 'ROE', 'Current Ratio', 'Asset Turnover']
    
    traces = []
    colors = ['#667eea', '#10b981', '#f59e0b', '#ef4444', '#3b82f6']
    
    for i, (company_name, analysis) in enumerate(top_companies):
        # Normalize metrics to 0-100 scale for radar chart
        revenue_growth_norm = min(100, max(0, analysis['financial_metrics']['revenue_growth'] * 5))
        operating_margin_norm = min(100, max(0, analysis['profitability_metrics']['operating_margin'] * 4))
        roe_norm = min(100, max(0, analysis['profitability_metrics']['roe'] * 4))
        current_ratio_norm = min(100, max(0, analysis['efficiency_metrics']['current_ratio'] * 40))
        asset_turnover_norm = min(100, max(0, analysis['efficiency_metrics']['asset_turnover'] * 50))
        
        values = [revenue_growth_norm, operating_margin_norm, roe_norm, current_ratio_norm, asset_turnover_norm]
        
        trace = {
            'type': 'scatterpolar',
            'r': values + [values[0]],  # Close the polygon
            'theta': categories + [categories[0]],
            'fill': 'toself',
            'name': company_name[:15],
            'line': {'color': colors[i % len(colors)]},
            'fillcolor': colors[i % len(colors)],
            'opacity': 0.5
        }
        traces.append(trace)
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': 'Top 5 Companies - Multi-Dimensional Performance Comparison',
            'polar': {
                'radialaxis': {
                    'visible': True,
                    'range': [0, 100]
                }
            },
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.15}
        }
    }
    
    return build_plotly_chart(fig_data, div_id="chart-12e-7", height=600)


# =============================================================================
# UPDATE MAIN GENERATE FUNCTION TO PASS PARAMETERS TO 12E
# =============================================================================
# NOTE: This shows what needs to be updated in the main generate() function

"""
In the main generate() function, change this line:

FROM:
    section_12e_html = _build_section_12e_visualization_dashboard()  # Stub

TO:
    # Get risk scoring from context if available
    risk_scoring = {}  # Or retrieve from artifacts if Section 11 has been run
    
    section_12e_html = _build_section_12e_visualization_dashboard(
        peer_analysis, ranking_analysis, sector_analysis, valuation_ladder, risk_scoring
    )
"""


# =============================================================================
# SUBSECTION 12F: STRATEGIC PEER INTELLIGENCE & COMPETITIVE POSITIONING FRAMEWORK
# =============================================================================

def _build_section_12f_strategic_intelligence(peer_analysis: Dict, ranking_analysis: Dict,
                                             sector_analysis: Dict, valuation_ladder: Dict,
                                             companies: Dict, risk_scoring: Dict) -> str:
    """Build subsection 12F: Strategic Peer Intelligence & Competitive Positioning Framework"""
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-12f')">
            <h2>12F. Strategic Peer Intelligence & Competitive Positioning Framework</h2>
            <span class="toggle-icon" id="icon-section-12f">▼</span>
        </div>
        <div class="subsection-content" id="content-section-12f">
    """
    
    # Generate comprehensive peer intelligence insights
    strategic_insights = _generate_comprehensive_peer_intelligence(
        peer_analysis, ranking_analysis, sector_analysis, valuation_ladder, 
        companies, risk_scoring
    )
    
    # Create tabbed interface for strategic sections
    html += """
    <div class="strategic-tabs">
        <div class="tab-buttons">
            <button class="tab-button active" onclick="openTab(event, 'tab-performance')">Performance Intelligence</button>
            <button class="tab-button" onclick="openTab(event, 'tab-positioning')">Positioning & Ranking</button>
            <button class="tab-button" onclick="openTab(event, 'tab-sector')">Sector Leadership</button>
            <button class="tab-button" onclick="openTab(event, 'tab-valuation')">Valuation Intelligence</button>
            <button class="tab-button" onclick="openTab(event, 'tab-framework')">Investment Framework</button>
        </div>
    """
    
    # Tab 1: Performance Intelligence
    html += """
        <div id="tab-performance" class="tab-content active">
            <h3>🎯 Peer Performance Intelligence & Competitive Assessment</h3>
    """
    html += _build_performance_intelligence_cards(strategic_insights, peer_analysis)
    html += "</div>"
    
    # Tab 2: Positioning Intelligence
    html += """
        <div id="tab-positioning" class="tab-content">
            <h3>📊 Relative Positioning & Ranking Intelligence</h3>
    """
    html += _build_positioning_intelligence_cards(strategic_insights, ranking_analysis)
    html += "</div>"
    
    # Tab 3: Sector Intelligence
    html += """
        <div id="tab-sector" class="tab-content">
            <h3>🏭 Sector Leadership & Industry Dynamics</h3>
    """
    html += _build_sector_intelligence_cards(strategic_insights, sector_analysis)
    html += "</div>"
    
    # Tab 4: Valuation Intelligence
    html += """
        <div id="tab-valuation" class="tab-content">
            <h3>💎 Valuation Intelligence & Investment Opportunities</h3>
    """
    html += _build_valuation_intelligence_cards(strategic_insights, valuation_ladder)
    html += "</div>"
    
    # Tab 5: Investment Framework
    html += """
        <div id="tab-framework" class="tab-content">
            <h3>🚀 Strategic Peer-Based Investment Framework</h3>
    """
    html += _build_investment_framework_cards(strategic_insights, peer_analysis, ranking_analysis, valuation_ladder)
    html += "</div>"
    
    html += """
    </div>
    """
    
    # Add CSS and JavaScript for tabs
    html += _get_tab_styling_and_scripts()
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# STRATEGIC INTELLIGENCE CARD BUILDERS
# =============================================================================

def _build_performance_intelligence_cards(strategic_insights: Dict, peer_analysis: Dict) -> str:
    """Build performance intelligence cards"""
    
    if not peer_analysis:
        return build_info_box("Performance intelligence unavailable.", "warning")
    
    # Calculate key metrics
    total_companies = len(peer_analysis)
    revenue_growth_values = [a['financial_metrics']['revenue_growth'] for a in peer_analysis.values()]
    operating_margin_values = [a['profitability_metrics']['operating_margin'] for a in peer_analysis.values()]
    roe_values = [a['profitability_metrics']['roe'] for a in peer_analysis.values()]
    performance_scores = [a['relative_performance']['overall_performance_score'] for a in peer_analysis.values()]
    
    avg_revenue_growth = np.mean(revenue_growth_values)
    avg_operating_margin = np.mean(operating_margin_values)
    avg_roe = np.mean(roe_values)
    avg_performance_score = np.mean(performance_scores)
    
    high_performers = sum(1 for score in performance_scores if score > 0.7)
    low_performers = sum(1 for score in performance_scores if score < 0.3)
    
    # Top performer
    sorted_by_performance = sorted(peer_analysis.items(), 
                                  key=lambda x: x[1]['relative_performance']['overall_performance_score'], 
                                  reverse=True)
    top_performer = sorted_by_performance[0][0] if sorted_by_performance else "N/A"
    bottom_performer = sorted_by_performance[-1][0] if sorted_by_performance else "N/A"
    
    html = '<div class="insight-cards-grid">'
    
    # Card 1: Portfolio Performance Profile
    html += f"""
    <div class="insight-card">
        <div class="card-icon">📈</div>
        <h4>Portfolio Performance Profile</h4>
        <div class="card-metrics">
            <div class="metric-item">
                <span class="metric-label">Companies Analyzed</span>
                <span class="metric-value">{total_companies}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Avg Revenue Growth</span>
                <span class="metric-value" style="color: {'#10b981' if avg_revenue_growth > 10 else '#f59e0b' if avg_revenue_growth > 5 else '#ef4444'}">{avg_revenue_growth:.1f}%</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Avg Operating Margin</span>
                <span class="metric-value" style="color: {'#10b981' if avg_operating_margin > 15 else '#f59e0b' if avg_operating_margin > 10 else '#ef4444'}">{avg_operating_margin:.1f}%</span>
            </div>
        </div>
        <p class="card-insight">
            {'Strong portfolio growth momentum' if avg_revenue_growth > 10 else 'Moderate growth profile' if avg_revenue_growth > 5 else 'Growth acceleration needed'} 
            with {'superior operating efficiency' if avg_operating_margin > 15 else 'competitive operating performance' if avg_operating_margin > 10 else 'operational improvement opportunity'}.
        </p>
    </div>
    """
    
    # Card 2: Profitability Assessment
    html += f"""
    <div class="insight-card">
        <div class="card-icon">💰</div>
        <h4>Profitability Assessment</h4>
        <div class="card-metrics">
            <div class="metric-item">
                <span class="metric-label">Average ROE</span>
                <span class="metric-value" style="color: {'#10b981' if avg_roe > 15 else '#f59e0b' if avg_roe > 10 else '#ef4444'}">{avg_roe:.1f}%</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Avg Performance Score</span>
                <span class="metric-value" style="color: {'#10b981' if avg_performance_score > 0.7 else '#f59e0b' if avg_performance_score > 0.5 else '#ef4444'}">{avg_performance_score:.2f}</span>
            </div>
        </div>
        <p class="card-insight">
            {'Excellent return profile' if avg_roe > 15 else 'Solid profitability metrics' if avg_roe > 10 else 'Profitability enhancement needed'} 
            across peer group with composite performance score of {avg_performance_score:.2f}.
        </p>
    </div>
    """
    
    # Card 3: Performance Distribution
    html += f"""
    <div class="insight-card">
        <div class="card-icon">📊</div>
        <h4>Performance Distribution</h4>
        <div class="progress-metric">
            <div class="progress-label">
                <span>High Performers (>70%)</span>
                <span class="progress-value">{high_performers}/{total_companies}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {(high_performers/total_companies)*100:.0f}%; background: #10b981;"></div>
            </div>
        </div>
        <div class="progress-metric">
            <div class="progress-label">
                <span>Underperformers (<30%)</span>
                <span class="progress-value">{low_performers}/{total_companies}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {(low_performers/total_companies)*100:.0f}%; background: #ef4444;"></div>
            </div>
        </div>
        <p class="card-insight">
            {'Exceptional portfolio quality' if high_performers >= total_companies * 0.6 and avg_performance_score > 0.6 
             else 'Solid peer group performance' if avg_performance_score > 0.5 
             else 'Portfolio optimization opportunity'} with clear performance differentiation.
        </p>
    </div>
    """
    
    # Card 4: Leadership Insight
    html += f"""
    <div class="insight-card highlight-card">
        <div class="card-icon">🏆</div>
        <h4>Performance Leadership</h4>
        <div class="leadership-badges">
            <div class="leader-badge success">
                <div class="badge-label">Top Performer</div>
                <div class="badge-value">{top_performer}</div>
            </div>
            <div class="leader-badge warning">
                <div class="badge-label">Needs Focus</div>
                <div class="badge-value">{bottom_performer}</div>
            </div>
        </div>
        <p class="card-insight">
            {top_performer} leads portfolio performance, while {bottom_performer} requires strategic focus and performance enhancement initiatives.
        </p>
    </div>
    """
    
    html += '</div>'
    
    return html


def _build_positioning_intelligence_cards(strategic_insights: Dict, ranking_analysis: Dict) -> str:
    """Build positioning intelligence cards"""
    
    if not ranking_analysis:
        return build_info_box("Positioning intelligence unavailable.", "warning")
    
    total_companies = len(ranking_analysis)
    market_leaders = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Market Leader')
    strong_competitors = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Strong Competitor')
    underperformers = sum(1 for a in ranking_analysis.values() if a['competitive_position'] in ['Below Average', 'Underperformer'])
    
    top_performer = min(ranking_analysis.items(), key=lambda x: x[1]['overall_rank'])[0]
    bottom_performer = max(ranking_analysis.items(), key=lambda x: x[1]['overall_rank'])[0]
    
    # Most common strengths and weaknesses
    all_strengths = []
    all_weaknesses = []
    for analysis in ranking_analysis.values():
        all_strengths.extend(analysis['strengths'])
        all_weaknesses.extend(analysis['weaknesses'])
    
    strength_counts = Counter(all_strengths)
    weakness_counts = Counter(all_weaknesses)
    
    top_strength = strength_counts.most_common(1)[0][0] if strength_counts else "None"
    top_weakness = weakness_counts.most_common(1)[0][0] if weakness_counts else "None"
    
    html = '<div class="insight-cards-grid">'
    
    # Card 1: Competitive Position Distribution
    html += f"""
    <div class="insight-card">
        <div class="card-icon">🎯</div>
        <h4>Competitive Position Distribution</h4>
        <div class="position-grid">
            <div class="position-item" style="background: rgba(16, 185, 129, 0.1);">
                <div class="position-count">{market_leaders}</div>
                <div class="position-label">Market Leaders</div>
                <div class="position-percent">{(market_leaders/total_companies)*100:.0f}%</div>
            </div>
            <div class="position-item" style="background: rgba(59, 130, 246, 0.1);">
                <div class="position-count">{strong_competitors}</div>
                <div class="position-label">Strong Competitors</div>
                <div class="position-percent">{(strong_competitors/total_companies)*100:.0f}%</div>
            </div>
            <div class="position-item" style="background: rgba(239, 68, 68, 0.1);">
                <div class="position-count">{underperformers}</div>
                <div class="position-label">Underperformers</div>
                <div class="position-percent">{(underperformers/total_companies)*100:.0f}%</div>
            </div>
        </div>
    </div>
    """
    
    # Card 2: Ranking Performance
    html += f"""
    <div class="insight-card">
        <div class="card-icon">📍</div>
        <h4>Ranking Performance Analysis</h4>
        <div class="ranking-stats">
            <div class="stat-badge">
                <span class="stat-label">Overall Assessment</span>
                <span class="stat-value" style="color: {'#10b981' if market_leaders + strong_competitors >= total_companies * 0.6 else '#f59e0b' if market_leaders + strong_competitors >= total_companies * 0.4 else '#ef4444'}">
                    {'Strong Portfolio Positioning' if market_leaders + strong_competitors >= total_companies * 0.6 
                     else 'Mixed Competitive Positioning' if market_leaders + strong_competitors >= total_companies * 0.4 
                     else 'Positioning Enhancement Needed'}
                </span>
            </div>
        </div>
        <p class="card-insight">
            Clear performance differentiation enabling targeted competitive strategies across {total_companies} companies.
        </p>
    </div>
    """
    
    # Card 3: Portfolio Strengths & Weaknesses
    html += f"""
    <div class="insight-card">
        <div class="card-icon">⚖️</div>
        <h4>Portfolio Strengths & Weaknesses</h4>
        <div class="strength-weakness-grid">
            <div class="sw-item strength">
                <div class="sw-icon">✓</div>
                <div class="sw-content">
                    <div class="sw-label">Key Strength</div>
                    <div class="sw-value">{top_strength}</div>
                </div>
            </div>
            <div class="sw-item weakness">
                <div class="sw-icon">⚠</div>
                <div class="sw-content">
                    <div class="sw-label">Key Weakness</div>
                    <div class="sw-value">{top_weakness}</div>
                </div>
            </div>
        </div>
        <p class="card-insight">
            {top_strength} emerges as common competitive advantage, while {top_weakness} represents primary improvement opportunity.
        </p>
    </div>
    """
    
    # Card 4: Ranking Leadership
    html += f"""
    <div class="insight-card highlight-card">
        <div class="card-icon">👑</div>
        <h4>Ranking Leadership</h4>
        <div class="leadership-comparison">
            <div class="leader-item success">
                <div class="leader-rank">#1</div>
                <div class="leader-name">{top_performer}</div>
                <div class="leader-status">Overall Leader</div>
            </div>
            <div class="leader-item danger">
                <div class="leader-rank">#{len(ranking_analysis)}</div>
                <div class="leader-name">{bottom_performer}</div>
                <div class="leader-status">Requires Strategic Focus</div>
            </div>
        </div>
    </div>
    """
    
    html += '</div>'
    
    return html


def _build_sector_intelligence_cards(strategic_insights: Dict, sector_analysis: Dict) -> str:
    """Build sector intelligence cards"""
    
    if not sector_analysis:
        return build_info_box("Sector intelligence unavailable.", "warning")
    
    total_sectors = len(sector_analysis)
    excellent_sectors = sum(1 for a in sector_analysis.values() if a['performance_rating'] == 'Excellent')
    good_sectors = sum(1 for a in sector_analysis.values() if a['performance_rating'] == 'Good')
    attractive_sectors = sum(1 for a in sector_analysis.values() 
                           if a['investment_appeal'] in ['Attractive Value', 'Deep Value'])
    
    best_sector = max(sector_analysis.items(), key=lambda x: x[1]['avg_roe'])[0] if sector_analysis else "None"
    largest_sector = max(sector_analysis.items(), key=lambda x: x[1]['company_count'])[0] if sector_analysis else "None"
    
    html = '<div class="insight-cards-grid">'
    
    # Card 1: Sector Diversity
    html += f"""
    <div class="insight-card">
        <div class="card-icon">🏭</div>
        <h4>Portfolio Sector Diversity</h4>
        <div class="sector-stats">
            <div class="sector-metric">
                <span class="metric-number">{total_sectors}</span>
                <span class="metric-text">Distinct Sectors</span>
            </div>
            <div class="sector-metric">
                <span class="metric-number">{excellent_sectors}</span>
                <span class="metric-text">Excellent-Performing</span>
            </div>
        </div>
        <p class="card-insight">
            {largest_sector} represents largest sector exposure, providing 
            {'well-diversified' if total_sectors >= 4 else 'moderate' if total_sectors >= 2 else 'concentrated'} 
            sector positioning.
        </p>
    </div>
    """
    
    # Card 2: Sector Performance Excellence
    html += f"""
    <div class="insight-card">
        <div class="card-icon">⭐</div>
        <h4>Sector Performance Excellence</h4>
        <div class="progress-metric">
            <div class="progress-label">
                <span>Excellent Sectors</span>
                <span class="progress-value">{excellent_sectors}/{total_sectors}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {(excellent_sectors/total_sectors)*100:.0f}%; background: #10b981;"></div>
            </div>
        </div>
        <div class="progress-metric">
            <div class="progress-label">
                <span>Good Sectors</span>
                <span class="progress-value">{good_sectors}/{total_sectors}</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {(good_sectors/total_sectors)*100:.0f}%; background: #3b82f6;"></div>
            </div>
        </div>
        <p class="card-insight">
            {'Outstanding sector positioning' if excellent_sectors >= total_sectors * 0.5 
             else 'Strong sector performance' if excellent_sectors >= total_sectors * 0.3 
             else 'Mixed sector performance'} across industry exposures.
        </p>
    </div>
    """
    
    # Card 3: Investment Appeal
    html += f"""
    <div class="insight-card">
        <div class="card-icon">💎</div>
        <h4>Sector Investment Appeal</h4>
        <div class="appeal-metrics">
            <div class="appeal-item">
                <div class="appeal-count">{attractive_sectors}</div>
                <div class="appeal-label">Attractive Value Sectors</div>
                <div class="appeal-percent">{(attractive_sectors/total_sectors)*100:.0f}% of Portfolio</div>
            </div>
        </div>
        <p class="card-insight">
            {'Strong value identification' if attractive_sectors >= total_sectors * 0.4 
             else 'Moderate value opportunities' if attractive_sectors >= total_sectors * 0.2 
             else 'Limited value sectors'} for strategic sector-based allocation.
        </p>
    </div>
    """
    
    # Card 4: Sector Leadership
    html += f"""
    <div class="insight-card highlight-card">
        <div class="card-icon">🎖️</div>
        <h4>Sector Leadership Position</h4>
        <div class="sector-leader-badge">
            <div class="leader-sector">{best_sector}</div>
            <div class="leader-metric">Top Sector by ROE</div>
        </div>
        <p class="card-insight">
            {best_sector} demonstrates {'multi-sector leadership' if excellent_sectors >= 3 
             else 'focused sector strength' if excellent_sectors >= 1 
             else 'sector performance development needed'} providing competitive moats.
        </p>
    </div>
    """
    
    html += '</div>'
    
    return html


def _build_valuation_intelligence_cards(strategic_insights: Dict, valuation_ladder: Dict) -> str:
    """Build valuation intelligence cards"""
    
    if not valuation_ladder:
        return build_info_box("Valuation intelligence unavailable.", "warning")
    
    total_companies = len(valuation_ladder)
    
    rating_counts = {}
    bucket_counts = {}
    
    for analysis in valuation_ladder.values():
        rating = analysis['value_rating']
        bucket = analysis['valuation_bucket']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    
    value_opportunities = rating_counts.get('Strong Buy', 0) + rating_counts.get('Buy', 0)
    overvalued_companies = rating_counts.get('Sell', 0)
    
    strong_buy_companies = [name for name, analysis in valuation_ladder.items() 
                           if analysis['value_rating'] == 'Strong Buy']
    best_value = strong_buy_companies[0] if strong_buy_companies else "None identified"
    
    html = '<div class="insight-cards-grid">'
    
    # Card 1: Value Opportunity Portfolio
    html += f"""
    <div class="insight-card">
        <div class="card-icon">💰</div>
        <h4>Value Opportunity Portfolio</h4>
        <div class="value-metrics">
            <div class="value-item success">
                <div class="value-count">{value_opportunities}</div>
                <div class="value-label">Buy Opportunities</div>
                <div class="value-percent">{(value_opportunities/total_companies)*100:.0f}%</div>
            </div>
            <div class="value-item neutral">
                <div class="value-count">{rating_counts.get('Hold', 0)}</div>
                <div class="value-label">Hold Positions</div>
                <div class="value-percent">{(rating_counts.get('Hold', 0)/total_companies)*100:.0f}%</div>
            </div>
            <div class="value-item danger">
                <div class="value-count">{overvalued_companies}</div>
                <div class="value-label">Overvalued</div>
                <div class="value-percent">{(overvalued_companies/total_companies)*100:.0f}%</div>
            </div>
        </div>
    </div>
    """
    
    # Card 2: Valuation Profile
    html += f"""
    <div class="insight-card">
        <div class="card-icon">📊</div>
        <h4>Portfolio Valuation Profile</h4>
        <div class="valuation-distribution">
            <div class="val-bucket" style="background: linear-gradient(135deg, #10b981, #059669);">
                <div class="bucket-count">{bucket_counts.get('Deep Value', 0) + bucket_counts.get('Discount Valuation', 0)}</div>
                <div class="bucket-label">Value Opportunities</div>
            </div>
            <div class="val-bucket" style="background: linear-gradient(135deg, #3b82f6, #2563eb);">
                <div class="bucket-count">{bucket_counts.get('Fair Valuation', 0)}</div>
                <div class="bucket-label">Fair Valuation</div>
            </div>
            <div class="val-bucket" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                <div class="bucket-count">{bucket_counts.get('Premium Valuation', 0)}</div>
                <div class="bucket-label">Premium</div>
            </div>
        </div>
        <p class="card-insight">
            {'Well-distributed valuation exposure' if len(bucket_counts) >= 3 
             else 'Moderate valuation diversity' if len(bucket_counts) >= 2 
             else 'Concentrated valuation profile'} across portfolio companies.
        </p>
    </div>
    """
    
    # Card 3: Risk Assessment
    html += f"""
    <div class="insight-card">
        <div class="card-icon">⚠️</div>
        <h4>Overvaluation Risk Management</h4>
        <div class="risk-assessment">
            <div class="risk-level" style="color: {'#10b981' if overvalued_companies == 0 else '#f59e0b' if overvalued_companies <= total_companies * 0.2 else '#ef4444'}">
                <div class="risk-indicator">
                    {'✓ Minimal Risk' if overvalued_companies <= total_companies * 0.2 
                     else '⚠ Moderate Risk' if overvalued_companies <= total_companies * 0.4 
                     else '✗ Significant Risk'}
                </div>
                <div class="risk-detail">{overvalued_companies} overvalued positions requiring {'minimal' if overvalued_companies == 0 else 'moderate' if overvalued_companies <= total_companies * 0.2 else 'significant'} portfolio rebalancing</div>
            </div>
        </div>
    </div>
    """
    
    # Card 4: Best Value Opportunity
    html += f"""
    <div class="insight-card highlight-card">
        <div class="card-icon">🏅</div>
        <h4>Best Value Opportunity</h4>
        <div class="best-value-showcase">
            <div class="value-company">{best_value}</div>
            <div class="value-rating">
                {build_badge('Strong Buy', 'success') if best_value != 'None identified' else 'No Strong Buy Ratings'}
            </div>
        </div>
        <p class="card-insight">
            {'Compelling value-driven allocation opportunities' if value_opportunities >= total_companies * 0.4 and overvalued_companies <= total_companies * 0.2 
             else 'Moderate value-based positioning' if value_opportunities >= total_companies * 0.3 
             else 'Limited value identification'} for strategic allocation.
        </p>
    </div>
    """
    
    html += '</div>'
    
    return html


def _build_investment_framework_cards(strategic_insights: Dict, peer_analysis: Dict,
                                     ranking_analysis: Dict, valuation_ladder: Dict) -> str:
    """Build investment framework action cards"""
    
    total_companies = len(peer_analysis) if peer_analysis else 0
    market_leaders = sum(1 for a in ranking_analysis.values() if a['competitive_position'] == 'Market Leader') if ranking_analysis else 0
    value_opportunities = sum(1 for a in valuation_ladder.values() if a['value_rating'] in ['Strong Buy', 'Buy']) if valuation_ladder else 0
    underperformers = sum(1 for a in ranking_analysis.values() if a['competitive_position'] in ['Below Average', 'Underperformer']) if ranking_analysis else 0
    
    html = '<div class="framework-container">'
    
    # Immediate Actions (0-6 months)
    html += """
    <div class="framework-phase">
        <div class="phase-header immediate">
            <div class="phase-icon">⚡</div>
            <div class="phase-info">
                <h4>Immediate Implementation</h4>
                <p>0-6 Months • High Priority Actions</p>
            </div>
        </div>
        <div class="action-cards">
    """
    
    html += f"""
            <div class="action-card priority-high">
                <div class="action-header">
                    <span class="action-icon">🎯</span>
                    <span class="action-title">Market Leader Concentration</span>
                    <span class="priority-badge high">High Priority</span>
                </div>
                <div class="action-content">
                    <p class="action-description">
                        {'Increase allocation to ' + str(market_leaders) + ' market leaders' if market_leaders > 0 else 'Develop market leadership pipeline'} 
                        for sustained outperformance
                    </p>
                    <div class="action-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Current Leaders</span>
                            <span class="metric-value">{market_leaders}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Target Allocation</span>
                            <span class="metric-value">+15%</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="action-card priority-high">
                <div class="action-header">
                    <span class="action-icon">💎</span>
                    <span class="action-title">Value Opportunity Execution</span>
                    <span class="priority-badge high">High Priority</span>
                </div>
                <div class="action-content">
                    <p class="action-description">
                        {'Deploy capital to ' + str(value_opportunities) + ' identified value opportunities' if value_opportunities > 0 else 'Enhance value identification capabilities'} 
                        for alpha generation
                    </p>
                    <div class="action-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Value Opportunities</span>
                            <span class="metric-value">{value_opportunities}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Expected Alpha</span>
                            <span class="metric-value">+8-12%</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="action-card priority-medium">
                <div class="action-header">
                    <span class="action-icon">🔧</span>
                    <span class="action-title">Underperformer Optimization</span>
                    <span class="priority-badge medium">Medium Priority</span>
                </div>
                <div class="action-content">
                    <p class="action-description">
                        {'Address ' + str(underperformers) + ' underperforming positions' if underperformers > 0 else 'Maintain performance excellence'} 
                        through strategic intervention
                    </p>
                    <div class="action-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Underperformers</span>
                            <span class="metric-value">{underperformers}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Timeline</span>
                            <span class="metric-value">6 months</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Medium-Term Development (6-18 months)
    html += """
    <div class="framework-phase">
        <div class="phase-header medium-term">
            <div class="phase-icon">📈</div>
            <div class="phase-info">
                <h4>Medium-Term Development</h4>
                <p>6-18 Months • Strategic Growth Initiatives</p>
            </div>
        </div>
        <div class="action-cards">
    """
    
    excellent_sectors = sum(1 for a in strategic_insights.get('sector_analysis', {}).values() if a.get('performance_rating') == 'Excellent') if 'sector_analysis' in strategic_insights else 0
    
    html += f"""
            <div class="action-card priority-medium">
                <div class="action-header">
                    <span class="action-icon">💪</span>
                    <span class="action-title">Competitive Advantage Expansion</span>
                    <span class="priority-badge medium">Strategic</span>
                </div>
                <div class="action-content">
                    <p class="action-description">
                        Systematic development of market leadership across portfolio companies through operational excellence
                    </p>
                    <div class="action-target">
                        <span class="target-label">Target:</span>
                        <span class="target-value">+{min(3, total_companies - market_leaders)} new market leaders</span>
                    </div>
                </div>
            </div>
            
            <div class="action-card priority-medium">
                <div class="action-header">
                    <span class="action-icon">🏭</span>
                    <span class="action-title">Sector Leadership Enhancement</span>
                    <span class="priority-badge medium">Strategic</span>
                </div>
                <div class="action-content">
                    <p class="action-description">
                        Strengthen sector excellence positions for industry dominance and competitive moats
                    </p>
                    <div class="action-target">
                        <span class="target-label">Current Excellence:</span>
                        <span class="target-value">{excellent_sectors} sectors</span>
                    </div>
                </div>
            </div>
            
            <div class="action-card priority-low">
                <div class="action-header">
                    <span class="action-icon">📊</span>
                    <span class="action-title">Valuation Optimization</span>
                    <span class="priority-badge low">Ongoing</span>
                </div>
                <div class="action-content">
                    <p class="action-description">
                        Advanced value-based allocation leveraging peer-relative valuation insights for optimal entry/exit timing
                    </p>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Long-Term Excellence (18+ months)
    html += f"""
    <div class="framework-phase">
        <div class="phase-header long-term">
            <div class="phase-icon">🚀</div>
            <div class="phase-info">
                <h4>Long-Term Excellence</h4>
                <p>18+ Months • Portfolio Transformation</p>
            </div>
        </div>
        <div class="success-metrics">
            <h5>Success Metrics & Strategic Targets</h5>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">👑</div>
                    <div class="metric-content">
                        <div class="metric-title">Market Leadership Target</div>
                        <div class="metric-value">{min(total_companies, market_leaders + 2)}</div>
                        <div class="metric-subtitle">market leaders within 24 months</div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">💎</div>
                    <div class="metric-content">
                        <div class="metric-title">Value Realization Target</div>
                        <div class="metric-value">{max(int(total_companies * 0.6), value_opportunities + 1)}</div>
                        <div class="metric-subtitle">value opportunities within 18 months</div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-content">
                        <div class="metric-title">Portfolio Optimization Target</div>
                        <div class="metric-value">{'Zero' if underperformers > 0 else 'Maintain Zero'}</div>
                        <div class="metric-subtitle">underperformers within 36 months</div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">⭐</div>
                    <div class="metric-content">
                        <div class="metric-title">Portfolio Excellence Target</div>
                        <div class="metric-value">Industry-Leading</div>
                        <div class="metric-subtitle">peer performance within 48 months</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    html += '</div>'
    
    return html


# =============================================================================
# TAB STYLING AND SCRIPTS
# =============================================================================

def _get_tab_styling_and_scripts() -> str:
    """Get CSS styling and JavaScript for tabs"""
    
    return """
    <style>
        /* Tab Interface Styling */
        .strategic-tabs {
            margin: 20px 0;
        }
        
        .tab-buttons {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid var(--card-border);
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .tab-button {
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 600;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            font-size: 0.95rem;
        }
        
        .tab-button:hover {
            color: var(--text-primary);
            background: rgba(102, 126, 234, 0.05);
        }
        
        .tab-button.active {
            color: var(--primary-gradient-start);
            border-bottom-color: var(--primary-gradient-start);
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.4s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Insight Cards Grid */
        .insight-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .insight-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 25px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
        }
        
        .insight-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-md);
        }
        
        .insight-card.highlight-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
            border: 2px solid var(--primary-gradient-start);
        }
        
        .card-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .insight-card h4 {
            color: var(--text-primary);
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        
        .card-metrics {
            margin: 15px 0;
        }
        
        .metric-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .metric-value {
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .card-insight {
            margin-top: 15px;
            padding: 12px;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 8px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        /* Progress Metrics */
        .progress-metric {
            margin: 15px 0;
        }
        
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9rem;
        }
        
        .progress-value {
            font-weight: 700;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 20px;
            background: rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 10px;
            transition: width 0.6s ease;
        }
        
        /* Leadership Badges */
        .leadership-badges {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        
        .leader-badge {
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        
        .leader-badge.success {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
            border: 2px solid #10b981;
        }
        
        .leader-badge.warning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
            border: 2px solid #f59e0b;
        }
        
        .badge-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 5px;
        }
        
        .badge-value {
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--text-primary);
        }
        
        /* Position Grid */
        .position-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .position-item {
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        
        .position-count {
            font-size: 2rem;
            font-weight: 900;
            color: var(--text-primary);
        }
        
        .position-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin: 5px 0;
        }
        
        .position-percent {
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        /* Framework Container */
        .framework-container {
            margin: 20px 0;
        }
        
        .framework-phase {
            margin: 30px 0;
            background: var(--card-bg);
            border-radius: 16px;
            padding: 25px;
            box-shadow: var(--shadow-sm);
        }
        
        .phase-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--card-border);
        }
        
        .phase-header.immediate {
            border-left: 5px solid #ef4444;
            padding-left: 15px;
        }
        
        .phase-header.medium-term {
            border-left: 5px solid #f59e0b;
            padding-left: 15px;
        }
        
        .phase-header.long-term {
            border-left: 5px solid #10b981;
            padding-left: 15px;
        }
        
        .phase-icon {
            font-size: 2rem;
        }
        
        .phase-info h4 {
            margin: 0;
            color: var(--text-primary);
        }
        
        .phase-info p {
            margin: 5px 0 0 0;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .action-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .action-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            border: 2px solid var(--card-border);
            transition: all 0.3s ease;
        }
        
        .action-card.priority-high {
            border-left: 5px solid #ef4444;
        }
        
        .action-card.priority-medium {
            border-left: 5px solid #f59e0b;
        }
        
        .action-card.priority-low {
            border-left: 5px solid #3b82f6;
        }
        
        .action-card:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
        }
        
        .action-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .action-icon {
            font-size: 1.5rem;
        }
        
        .action-title {
            flex: 1;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        .priority-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        
        .priority-badge.high {
            background: #ef4444;
            color: white;
        }
        
        .priority-badge.medium {
            background: #f59e0b;
            color: white;
        }
        
        .priority-badge.low {
            background: #3b82f6;
            color: white;
        }
        
        .action-description {
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .action-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .action-target {
            display: flex;
            gap: 10px;
            padding: 10px;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 8px;
            font-size: 0.9rem;
        }
        
        .target-label {
            color: var(--text-secondary);
        }
        
        .target-value {
            font-weight: 700;
            color: var(--primary-gradient-start);
        }
        
        /* Success Metrics */
        .success-metrics {
            margin: 20px 0;
        }
        
        .success-metrics h5 {
            color: var(--text-primary);
            margin-bottom: 20px;
            font-size: 1.2rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 2px solid var(--primary-gradient-start);
        }
        
        .metric-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .metric-title {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        .metric-card .metric-value {
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .metric-subtitle {
            font-size: 0.8rem;
            color: var(--text-tertiary);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .insight-cards-grid {
                grid-template-columns: 1fr;
            }
            
            .action-cards {
                grid-template-columns: 1fr;
            }
            
            .tab-buttons {
                flex-direction: column;
            }
            
            .tab-button {
                width: 100%;
                text-align: left;
            }
        }
    </style>
    
    <script>
        function openTab(evt, tabName) {
            // Hide all tab contents
            var tabContents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            // Remove active class from all buttons
            var tabButtons = document.getElementsByClassName('tab-button');
            for (var i = 0; i < tabButtons.length; i++) {
                tabButtons[i].classList.remove('active');
            }
            
            // Show the selected tab and mark button as active
            document.getElementById(tabName).classList.add('active');
            evt.currentTarget.classList.add('active');
        }
    </script>
    """


# =============================================================================
# HELPER FUNCTION - GENERATE COMPREHENSIVE PEER INTELLIGENCE
# =============================================================================

def _generate_comprehensive_peer_intelligence(peer_analysis: Dict, ranking_analysis: Dict, 
                                            sector_analysis: Dict, valuation_ladder: Dict,
                                            companies: Dict, risk_scoring: Dict) -> Dict[str, Any]:
    """Generate comprehensive peer intelligence insights"""
    
    return {
        'peer_analysis': peer_analysis,
        'ranking_analysis': ranking_analysis,
        'sector_analysis': sector_analysis,
        'valuation_ladder': valuation_ladder,
        'companies': companies,
        'risk_scoring': risk_scoring
    }


# =============================================================================
# UPDATE MAIN GENERATE FUNCTION TO PASS PARAMETERS TO 12F
# =============================================================================
# NOTE: This shows what needs to be updated in the main generate() function

"""
In the main generate() function, change this line:

FROM:
    section_12f_html = _build_section_12f_strategic_intelligence()  # Stub

TO:
    section_12f_html = _build_section_12f_strategic_intelligence(
        peer_analysis, ranking_analysis, sector_analysis, valuation_ladder, companies, risk_scoring
    )
"""


# =============================================================================
# HELPER FUNCTIONS - COMPREHENSIVE PEER ANALYSIS
# =============================================================================

def _generate_comprehensive_peer_analysis(df: pd.DataFrame, companies: Dict[str, str], 
                                         profiles_df: pd.DataFrame) -> Dict[str, Dict]:
    """Generate comprehensive cross-company peer analysis"""
    
    peer_analysis = {}
    
    print(f"\n=== Peer Analysis: Using Most Recent Year Per Company ===")
    
    for company_name in companies.keys():
        company_all_data = df[df['Company'] == company_name]
        
        if company_all_data.empty:
            print(f"WARNING: {company_name} has no data - EXCLUDED")
            continue
        
        latest_year_for_company = company_all_data['Year'].max()
        company_data = company_all_data[company_all_data['Year'] == latest_year_for_company]
        
        print(f"  {company_name}: Using FY {latest_year_for_company}")
        
        financial_metrics = _extract_financial_metrics(company_data)
        operational_metrics = _extract_operational_metrics(company_data)
        valuation_metrics = _extract_valuation_metrics(company_data)
        profitability_metrics = _extract_profitability_metrics(company_data)
        efficiency_metrics = _extract_efficiency_metrics(company_data)
        
        peer_analysis[company_name] = {
            'financial_metrics': financial_metrics,
            'operational_metrics': operational_metrics,
            'valuation_metrics': valuation_metrics,
            'profitability_metrics': profitability_metrics,
            'efficiency_metrics': efficiency_metrics,
            'fiscal_year': latest_year_for_company
        }
    
    print(f"Successfully processed: {len(peer_analysis)}/{len(companies)} companies")
    print(f"=== End Peer Analysis ===\n")
    
    portfolio_stats = _calculate_portfolio_statistics(peer_analysis)
    
    for company_name in peer_analysis.keys():
        peer_analysis[company_name]['relative_performance'] = _calculate_relative_performance(
            peer_analysis[company_name], portfolio_stats
        )
    
    return peer_analysis


def _extract_financial_metrics(company_data: pd.DataFrame) -> Dict[str, float]:
    """Extract key financial metrics"""
    row = company_data.iloc[0]
    return {
        'revenue': row.get('revenue', 0),
        'revenue_growth': row.get('revenue_YoY', 0),
        'net_income': row.get('netIncome', 0),
        'gross_profit': row.get('grossProfit', 0),
        'operating_income': row.get('operatingIncome', 0),
        'ebitda': row.get('ebitda', 0),
        'total_assets': row.get('totalAssets', 0),
        'total_equity': row.get('totalStockholdersEquity', 0),
        'total_debt': row.get('totalDebt', 0),
        'cash': row.get('cashAndCashEquivalents', 0),
        'market_cap': row.get('marketCap', 0)
    }


def _extract_operational_metrics(company_data: pd.DataFrame) -> Dict[str, float]:
    """Extract operational performance metrics"""
    row = company_data.iloc[0]
    return {
        'operating_cash_flow': row.get('operatingCashFlow', 0),
        'free_cash_flow': row.get('freeCashFlow', 0),
        'capex': row.get('capitalExpenditure', 0),
        'working_capital': row.get('workingCapital', 0),
        'employee_count': row.get('employeeCount', 0),
        'revenue_per_employee': row.get('revenuePerShare', 0) * row.get('weightedAverageShsOut', 1) / max(1, row.get('employeeCount', 1)) if row.get('employeeCount', 0) > 0 else 0
    }


def _extract_valuation_metrics(company_data: pd.DataFrame) -> Dict[str, float]:
    """Extract valuation metrics"""
    row = company_data.iloc[0]
    return {
        'pe_ratio': row.get('priceToEarningsRatio', 0),
        'pb_ratio': row.get('priceToBookRatio', 0),
        'ps_ratio': row.get('priceToSalesRatio', 0),
        'ev_ebitda': row.get('enterpriseValueMultiple', 0),
        'ev_sales': row.get('evToSales', 0),
        'dividend_yield': row.get('dividendYield', 0),
        'enterprise_value': row.get('enterpriseValue', 0)
    }


def _extract_profitability_metrics(company_data: pd.DataFrame) -> Dict[str, float]:
    """Extract profitability metrics"""
    row = company_data.iloc[0]
    return {
        'gross_margin': row.get('grossProfitMargin', 0),
        'operating_margin': row.get('operatingProfitMargin', 0),
        'net_margin': row.get('netProfitMargin', 0),
        'ebitda_margin': row.get('ebitdaMargin', 0),
        'roe': row.get('returnOnEquity', 0),
        'roa': row.get('returnOnAssets', 0),
        'roic': row.get('returnOnInvestedCapital', 0)
    }


def _extract_efficiency_metrics(company_data: pd.DataFrame) -> Dict[str, float]:
    """Extract efficiency metrics"""
    row = company_data.iloc[0]
    return {
        'asset_turnover': row.get('assetTurnover', 0),
        'inventory_turnover': row.get('inventoryTurnover', 0),
        'receivables_turnover': row.get('receivablesTurnover', 0),
        'current_ratio': row.get('currentRatio', 0),
        'quick_ratio': row.get('quickRatio', 0),
        'debt_equity_ratio': row.get('debtToEquityRatio', 0),
        'interest_coverage': row.get('interestCoverageRatio', 0)
    }


def _calculate_portfolio_statistics(peer_analysis: Dict) -> Dict[str, Dict]:
    """Calculate portfolio-wide statistics for benchmarking"""
    portfolio_stats = {}
    all_metrics = {}
    metric_categories = ['financial_metrics', 'operational_metrics', 'valuation_metrics', 
                        'profitability_metrics', 'efficiency_metrics']
    
    for category in metric_categories:
        all_metrics[category] = {}
        for company_data in peer_analysis.values():
            for metric_name, value in company_data[category].items():
                if metric_name not in all_metrics[category]:
                    all_metrics[category][metric_name] = []
                if value is not None and not np.isnan(value) and np.isfinite(value):
                    all_metrics[category][metric_name].append(value)
    
    for category in metric_categories:
        portfolio_stats[category] = {}
        for metric_name, values in all_metrics[category].items():
            if values:
                portfolio_stats[category][metric_name] = {
                    'median': np.median(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'q1': np.percentile(values, 25),
                    'q3': np.percentile(values, 75)
                }
            else:
                portfolio_stats[category][metric_name] = {
                    'median': 0, 'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'q1': 0, 'q3': 0
                }
    
    return portfolio_stats


def _calculate_relative_performance(company_metrics: Dict, portfolio_stats: Dict) -> Dict[str, Any]:
    """Calculate relative performance indicators"""
    relative_performance = {}
    
    key_metrics = {
        'revenue_growth': ('financial_metrics', 'revenue_growth'),
        'operating_margin': ('profitability_metrics', 'operating_margin'),
        'roe': ('profitability_metrics', 'roe'),
        'pe_ratio': ('valuation_metrics', 'pe_ratio'),
        'debt_equity_ratio': ('efficiency_metrics', 'debt_equity_ratio')
    }
    
    for metric_name, (category, field) in key_metrics.items():
        company_value = company_metrics[category].get(field, 0)
        portfolio_median = portfolio_stats[category][field]['median']
        
        if portfolio_median != 0:
            relative_performance[f'{metric_name}_vs_median'] = (company_value - portfolio_median) / portfolio_median
        else:
            relative_performance[f'{metric_name}_vs_median'] = 0
        
        q1 = portfolio_stats[category][field]['q1']
        q3 = portfolio_stats[category][field]['q3']
        median = portfolio_stats[category][field]['median']
        
        if company_value <= q1:
            percentile = 0.25
        elif company_value <= median:
            percentile = 0.5
        elif company_value <= q3:
            percentile = 0.75
        else:
            percentile = 0.9
        
        relative_performance[f'{metric_name}_percentile'] = percentile
    
    performance_score = np.mean([
        relative_performance.get('revenue_growth_percentile', 0.5),
        relative_performance.get('operating_margin_percentile', 0.5),
        relative_performance.get('roe_percentile', 0.5),
        1 - relative_performance.get('debt_equity_ratio_percentile', 0.5)
    ])
    
    relative_performance['overall_performance_score'] = performance_score
    
    return relative_performance


# =============================================================================
# HELPER FUNCTIONS - PEER RANKING ANALYSIS
# =============================================================================

def _generate_peer_ranking_analysis(df: pd.DataFrame, companies: Dict[str, str], 
                                   peer_analysis: Dict) -> Dict[str, Dict]:
    """Generate comprehensive peer ranking analysis"""
    
    if not peer_analysis:
        return {}
    
    ranking_analysis = {}
    
    ranking_categories = {
        'growth': ['revenue_growth'],
        'profitability': ['operating_margin', 'net_margin', 'roe'],
        'efficiency': ['asset_turnover', 'current_ratio'],
        'valuation': ['pe_ratio', 'pb_ratio'],
        'financial_strength': ['debt_equity_ratio', 'interest_coverage']
    }
    
    for company_name, analysis in peer_analysis.items():
        company_rankings = {}
        
        for category, metrics in ranking_categories.items():
            category_scores = []
            category_ranks = []
            
            for metric in metrics:
                metric_value = None
                for metric_category in ['financial_metrics', 'operational_metrics', 'valuation_metrics', 
                                      'profitability_metrics', 'efficiency_metrics']:
                    if metric in analysis[metric_category]:
                        metric_value = analysis[metric_category][metric]
                        break
                
                if metric_value is not None:
                    peer_values = []
                    for peer_name, peer_analysis_data in peer_analysis.items():
                        for peer_metric_category in ['financial_metrics', 'operational_metrics', 'valuation_metrics', 
                                                   'profitability_metrics', 'efficiency_metrics']:
                            if metric in peer_analysis_data[peer_metric_category]:
                                peer_values.append(peer_analysis_data[peer_metric_category][metric])
                                break
                    
                    if peer_values:
                        if metric == 'debt_equity_ratio':
                            rank = sum(1 for v in peer_values if v > metric_value) + 1
                        else:
                            rank = sum(1 for v in peer_values if v > metric_value) + 1
                        
                        percentile = (len(peer_values) - rank + 1) / len(peer_values)
                        category_scores.append(percentile)
                        category_ranks.append(rank)
            
            if category_scores:
                company_rankings[category] = {
                    'average_percentile': np.mean(category_scores),
                    'average_rank': np.mean(category_ranks),
                    'category_score': np.mean(category_scores) * 100,
                    'rank_detail': category_ranks
                }
            else:
                company_rankings[category] = {
                    'average_percentile': 0.5,
                    'average_rank': len(peer_analysis) / 2,
                    'category_score': 50,
                    'rank_detail': []
                }
        
        category_scores = [rankings['category_score'] for rankings in company_rankings.values()]
        overall_score = np.mean(category_scores) if category_scores else 50
        
        peer_overall_scores = []
        for peer_name, peer_data in peer_analysis.items():
            peer_score = peer_data['relative_performance']['overall_performance_score'] * 100
            peer_overall_scores.append(peer_score)
        
        overall_rank = sum(1 for score in peer_overall_scores if score > overall_score) + 1
        
        ranking_analysis[company_name] = {
            'category_rankings': company_rankings,
            'overall_score': overall_score,
            'overall_rank': overall_rank,
            'total_companies': len(peer_analysis),
            'strengths': _identify_ranking_strengths(company_rankings),
            'weaknesses': _identify_ranking_weaknesses(company_rankings),
            'competitive_position': _assess_competitive_position(overall_rank, len(peer_analysis))
        }
    
    return ranking_analysis


def _identify_ranking_strengths(category_rankings: Dict) -> List[str]:
    """Identify ranking strengths (top quartile performance)"""
    strengths = []
    for category, rankings in category_rankings.items():
        if rankings['average_percentile'] >= 0.75:
            strengths.append(category.replace('_', ' ').title())
    return strengths


def _identify_ranking_weaknesses(category_rankings: Dict) -> List[str]:
    """Identify ranking weaknesses (bottom quartile performance)"""
    weaknesses = []
    for category, rankings in category_rankings.items():
        if rankings['average_percentile'] <= 0.25:
            weaknesses.append(category.replace('_', ' ').title())
    return weaknesses


def _assess_competitive_position(overall_rank: int, total_companies: int) -> str:
    """Assess competitive position based on overall rank"""
    percentile = (total_companies - overall_rank + 1) / total_companies
    
    if percentile >= 0.8:
        return "Market Leader"
    elif percentile >= 0.6:
        return "Strong Competitor"
    elif percentile >= 0.4:
        return "Average Performer"
    elif percentile >= 0.2:
        return "Below Average"
    else:
        return "Underperformer"
    

# =============================================================================
# The following would be in section_11.py to provide risk scoring data
# =============================================================================

def calculate_risk_scoring(collector, analysis_id):
    """
    Calculate risk_scoring from collector and analysis_id
    
    Args:
        collector: FinancialDataCollection object
        analysis_id: str
    
    Returns:
        risk_scoring: Dict containing risk scoring data for each company
    """
    
    # Extract required data
    companies = collector.companies
    df = collector.get_all_financial_data()
    
    # Check if we have sufficient data
    if df.empty:
        print("Warning: No financial data available")
        return {}
    
    # Step 1: Generate comprehensive risk analysis
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    
    if not risk_analysis:
        print("Warning: Risk analysis generation failed")
        return {}
    
    # Step 2: Generate automated alert system
    alert_system = _generate_automated_alerts(df, companies, risk_analysis)
    
    if not alert_system:
        print("Warning: Alert system generation failed")
        return {}
    
    # Step 3: Generate risk scoring system
    risk_scoring = _generate_risk_scoring_system(risk_analysis, alert_system, companies)
    
    return risk_scoring

def _generate_comprehensive_risk_analysis(df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Generate comprehensive multi-dimensional risk analysis"""
    
    risk_analysis = {}
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 3:
            continue
        
        # Initialize risk metrics
        risk_metrics = {
            'financial_risks': {},
            'operational_risks': {},
            'liquidity_risks': {},
            'market_risks': {},
            'trend_risks': {},
            'alert_triggers': []
        }
        
        # Financial Risk Analysis
        financial_risks = _analyze_financial_risks(company_data)
        risk_metrics['financial_risks'] = financial_risks
        
        # Operational Risk Analysis
        operational_risks = _analyze_operational_risks(company_data)
        risk_metrics['operational_risks'] = operational_risks
        
        # Liquidity Risk Analysis
        liquidity_risks = _analyze_liquidity_risks(company_data)
        risk_metrics['liquidity_risks'] = liquidity_risks
        
        # Market Risk Analysis
        market_risks = _analyze_market_risks(company_data)
        risk_metrics['market_risks'] = market_risks
        
        # Trend Risk Analysis
        trend_risks = _analyze_trend_risks(company_data)
        risk_metrics['trend_risks'] = trend_risks
        
        # Alert Trigger Detection
        alert_triggers = _detect_alert_triggers(company_data, financial_risks, operational_risks, liquidity_risks)
        risk_metrics['alert_triggers'] = alert_triggers
        
        # Overall risk assessment
        risk_metrics['overall_risk_score'] = _calculate_overall_risk_score(
            financial_risks, operational_risks, liquidity_risks, market_risks, trend_risks
        )
        
        risk_analysis[company_name] = risk_metrics
    
    return risk_analysis

def _generate_automated_alerts(df: pd.DataFrame, companies: Dict[str, str], 
                              risk_analysis: Dict) -> Dict[str, Dict]:
    """Generate comprehensive automated alert system"""
    
    alert_system = {}
    
    for company_name in companies.keys():
        if company_name not in risk_analysis:
            continue
        
        company_data = df[df['Company'] == company_name].sort_values('Year')
        risk_data = risk_analysis[company_name]
        
        # Initialize alert categories
        alerts = {
            'critical_alerts': [],
            'warning_alerts': [],
            'monitoring_alerts': [],
            'alert_summary': {},
            'alert_trends': {},
            'severity_distribution': {}
        }
        
        # Generate critical alerts
        critical_alerts = _generate_critical_alerts(company_data, risk_data)
        alerts['critical_alerts'] = critical_alerts
        
        # Generate warning alerts
        warning_alerts = _generate_warning_alerts(company_data, risk_data)
        alerts['warning_alerts'] = warning_alerts
        
        # Generate monitoring alerts
        monitoring_alerts = _generate_monitoring_alerts(company_data)
        alerts['monitoring_alerts'] = monitoring_alerts
        
        # Alert summary statistics
        alerts['alert_summary'] = {
            'total_alerts': len(critical_alerts) + len(warning_alerts) + len(monitoring_alerts),
            'critical_count': len(critical_alerts),
            'warning_count': len(warning_alerts),
            'monitoring_count': len(monitoring_alerts),
            'alert_frequency': _calculate_alert_frequency(critical_alerts, warning_alerts, monitoring_alerts),
            'priority_score': _calculate_priority_score(critical_alerts, warning_alerts)
        }
        
        # Alert trends analysis
        alerts['alert_trends'] = _analyze_alert_trends(company_data, risk_data)
        
        # Severity distribution
        alerts['severity_distribution'] = _calculate_severity_distribution(critical_alerts, warning_alerts, monitoring_alerts)
        
        alert_system[company_name] = alerts
    
    return alert_system

def _generate_risk_scoring_system(risk_analysis: Dict, alert_system: Dict, 
                                 companies: Dict) -> Dict[str, Dict]:
    """Generate comprehensive risk scoring system"""
    
    if not risk_analysis:
        return {}
    
    risk_scoring = {}
    
    for company_name in companies.keys():
        if company_name not in risk_analysis:
            continue
        
        risk_data = risk_analysis[company_name]
        alerts = alert_system.get(company_name, {})
        
        # Calculate component risk scores
        financial_risk_score = _calculate_financial_risk_score(risk_data.get('financial_risks', {}))
        operational_risk_score = _calculate_operational_risk_score(risk_data.get('operational_risks', {}))
        market_risk_score = _calculate_market_risk_score(risk_data.get('market_risks', {}))
        liquidity_risk_score = _calculate_liquidity_risk_score(risk_data.get('liquidity_risks', {}))
        alert_severity_score = _calculate_alert_severity_score(alerts.get('alert_summary', {}))
        
        # Composite risk score
        composite_score = (
            financial_risk_score * 0.30 +
            operational_risk_score * 0.25 +
            liquidity_risk_score * 0.25 +
            market_risk_score * 0.10 +
            alert_severity_score * 0.10
        )
        
        # Risk rating classification
        if composite_score <= 3:
            risk_rating = "Low Risk"
        elif composite_score <= 5:
            risk_rating = "Moderate Risk"
        elif composite_score <= 7:
            risk_rating = "High Risk"
        elif composite_score <= 8.5:
            risk_rating = "Critical Risk"
        else:
            risk_rating = "Extreme Risk"
        
        # Risk trend analysis
        risk_trend = _analyze_risk_trend(risk_data, alerts.get('alert_trends', {}))
        
        risk_scoring[company_name] = {
            'financial_risk_score': financial_risk_score,
            'operational_risk_score': operational_risk_score,
            'market_risk_score': market_risk_score,
            'liquidity_risk_score': liquidity_risk_score,
            'alert_severity_score': alert_severity_score,
            'composite_risk_score': composite_score,
            'risk_rating': risk_rating,
            'risk_trend': risk_trend
        }
    
    return risk_scoring

def _analyze_financial_risks(company_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze financial-specific risks"""
    
    financial_risks = {}
    
    # Revenue volatility risk
    if 'revenue_YoY' in company_data.columns:
        revenue_growth = company_data['revenue_YoY'].fillna(0)
        financial_risks['revenue_volatility'] = revenue_growth.std()
        financial_risks['revenue_decline_risk'] = (revenue_growth < -10).sum() / len(revenue_growth)
    else:
        financial_risks['revenue_volatility'] = 0
        financial_risks['revenue_decline_risk'] = 0
    
    # Profitability deterioration risk
    if 'netProfitMargin' in company_data.columns:
        profit_margin = company_data['netProfitMargin'].fillna(0)
        financial_risks['margin_compression'] = max(0, profit_margin.iloc[0] - profit_margin.iloc[-1]) if len(profit_margin) > 1 else 0
        financial_risks['negative_margin_risk'] = (profit_margin < 0).sum() / len(profit_margin)
    else:
        financial_risks['margin_compression'] = 0
        financial_risks['negative_margin_risk'] = 0
    
    # Leverage risk
    if 'debtToEquityRatio' in company_data.columns:
        debt_equity = company_data['debtToEquityRatio'].fillna(0)
        financial_risks['leverage_risk'] = debt_equity.iloc[-1] if len(debt_equity) > 0 else 0
        financial_risks['leverage_trend'] = debt_equity.iloc[-1] - debt_equity.iloc[0] if len(debt_equity) > 1 else 0
    else:
        financial_risks['leverage_risk'] = 0
        financial_risks['leverage_trend'] = 0
    
    # Interest coverage risk
    if 'interestCoverageRatio' in company_data.columns:
        interest_coverage = company_data['interestCoverageRatio'].fillna(0)
        financial_risks['interest_coverage_risk'] = 10 - min(10, interest_coverage.iloc[-1]) if len(interest_coverage) > 0 else 5
    else:
        financial_risks['interest_coverage_risk'] = 5
    
    return financial_risks


def _analyze_operational_risks(company_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze operational-specific risks"""
    
    operational_risks = {}
    
    # Cash flow volatility
    if 'operatingCashFlow_YoY' in company_data.columns:
        ocf_growth = company_data['operatingCashFlow_YoY'].fillna(0)
        operational_risks['cash_flow_volatility'] = ocf_growth.std()
        operational_risks['negative_ocf_risk'] = (company_data['operatingCashFlow'] < 0).sum() / len(company_data) if 'operatingCashFlow' in company_data.columns else 0
    else:
        operational_risks['cash_flow_volatility'] = 0
        operational_risks['negative_ocf_risk'] = 0
    
    # Working capital efficiency
    if 'workingCapital' in company_data.columns and 'revenue' in company_data.columns:
        wc_revenue_ratio = (company_data['workingCapital'] / company_data['revenue']).fillna(0)
        operational_risks['working_capital_risk'] = wc_revenue_ratio.std()
    else:
        operational_risks['working_capital_risk'] = 0
    
    # Asset turnover efficiency
    if 'assetTurnover' in company_data.columns:
        asset_turnover = company_data['assetTurnover'].fillna(0)
        operational_risks['efficiency_deterioration'] = max(0, asset_turnover.iloc[0] - asset_turnover.iloc[-1]) if len(asset_turnover) > 1 else 0
    else:
        operational_risks['efficiency_deterioration'] = 0
    
    # Capital expenditure sustainability
    if 'capitalExpenditure' in company_data.columns and 'operatingCashFlow' in company_data.columns:
        capex_ocf_ratio = (abs(company_data['capitalExpenditure']) / company_data['operatingCashFlow'].abs()).fillna(0)
        operational_risks['capex_sustainability_risk'] = (capex_ocf_ratio > 1).sum() / len(capex_ocf_ratio)
    else:
        operational_risks['capex_sustainability_risk'] = 0
    
    return operational_risks


def _analyze_liquidity_risks(company_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze liquidity-specific risks"""
    
    liquidity_risks = {}
    
    # Current ratio risk
    if 'currentRatio' in company_data.columns:
        current_ratio = company_data['currentRatio'].fillna(0)
        liquidity_risks['current_ratio_risk'] = max(0, 2.0 - current_ratio.iloc[-1]) if len(current_ratio) > 0 else 1
        liquidity_risks['liquidity_deterioration'] = max(0, current_ratio.iloc[0] - current_ratio.iloc[-1]) if len(current_ratio) > 1 else 0
    else:
        liquidity_risks['current_ratio_risk'] = 1
        liquidity_risks['liquidity_deterioration'] = 0
    
    # Quick ratio risk
    if 'quickRatio' in company_data.columns:
        quick_ratio = company_data['quickRatio'].fillna(0)
        liquidity_risks['quick_ratio_risk'] = max(0, 1.0 - quick_ratio.iloc[-1]) if len(quick_ratio) > 0 else 0.5
    else:
        liquidity_risks['quick_ratio_risk'] = 0.5
    
    # Cash position risk
    if 'cashAndCashEquivalents' in company_data.columns and 'totalCurrentLiabilities' in company_data.columns:
        cash_coverage = (company_data['cashAndCashEquivalents'] / company_data['totalCurrentLiabilities']).fillna(0)
        liquidity_risks['cash_coverage_risk'] = max(0, 0.3 - cash_coverage.iloc[-1]) if len(cash_coverage) > 0 else 0.3
    else:
        liquidity_risks['cash_coverage_risk'] = 0.3
    
    # Working capital trend
    if 'workingCapital' in company_data.columns:
        working_capital = company_data['workingCapital'].fillna(0)
        liquidity_risks['working_capital_trend'] = min(0, working_capital.iloc[-1] - working_capital.iloc[0]) if len(working_capital) > 1 else 0
    else:
        liquidity_risks['working_capital_trend'] = 0
    
    return liquidity_risks


def _analyze_market_risks(company_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze market-specific risks"""
    
    market_risks = {}
    
    # Valuation risk
    if 'priceToEarningsRatio' in company_data.columns:
        pe_ratio = company_data['priceToEarningsRatio'].fillna(0)
        market_risks['valuation_risk'] = max(0, pe_ratio.iloc[-1] - 25) / 25 if len(pe_ratio) > 0 and pe_ratio.iloc[-1] > 0 else 0
    else:
        market_risks['valuation_risk'] = 0
    
    # Price-to-book risk
    if 'priceToBookRatio' in company_data.columns:
        pb_ratio = company_data['priceToBookRatio'].fillna(0)
        market_risks['price_book_risk'] = max(0, pb_ratio.iloc[-1] - 3) / 3 if len(pb_ratio) > 0 and pb_ratio.iloc[-1] > 0 else 0
    else:
        market_risks['price_book_risk'] = 0
    
    # Enterprise value risk
    if 'enterpriseValueMultiple' in company_data.columns:
        ev_multiple = company_data['enterpriseValueMultiple'].fillna(0)
        market_risks['ev_multiple_risk'] = max(0, ev_multiple.iloc[-1] - 15) / 15 if len(ev_multiple) > 0 and ev_multiple.iloc[-1] > 0 else 0
    else:
        market_risks['ev_multiple_risk'] = 0
    
    # Market cap sustainability
    if 'marketCap' in company_data.columns:
        market_cap = company_data['marketCap'].fillna(0)
        market_risks['market_cap_volatility'] = market_cap.pct_change().std() if len(market_cap) > 1 else 0
    else:
        market_risks['market_cap_volatility'] = 0
    
    return market_risks


def _analyze_trend_risks(company_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze trend-based risks"""
    
    trend_risks = {}
    
    # Revenue trend risk
    if 'revenue' in company_data.columns:
        revenue = company_data['revenue'].fillna(0)
        if len(revenue) >= 3:
            revenue_trend = np.polyfit(range(len(revenue)), revenue, 1)[0]
            trend_risks['revenue_trend_risk'] = max(0, -revenue_trend / revenue.mean()) if revenue.mean() > 0 else 0
        else:
            trend_risks['revenue_trend_risk'] = 0
    else:
        trend_risks['revenue_trend_risk'] = 0
    
    # Profitability trend risk
    if 'netProfitMargin' in company_data.columns:
        profit_margin = company_data['netProfitMargin'].fillna(0)
        if len(profit_margin) >= 3:
            margin_trend = np.polyfit(range(len(profit_margin)), profit_margin, 1)[0]
            trend_risks['profitability_trend_risk'] = max(0, -margin_trend * 10)
        else:
            trend_risks['profitability_trend_risk'] = 0
    else:
        trend_risks['profitability_trend_risk'] = 0
    
    # ROE trend risk
    if 'returnOnEquity' in company_data.columns:
        roe = company_data['returnOnEquity'].fillna(0)
        if len(roe) >= 3:
            roe_trend = np.polyfit(range(len(roe)), roe, 1)[0]
            trend_risks['roe_trend_risk'] = max(0, -roe_trend * 10)
        else:
            trend_risks['roe_trend_risk'] = 0
    else:
        trend_risks['roe_trend_risk'] = 0
    
    # Leverage trend risk
    if 'debtToEquityRatio' in company_data.columns:
        debt_equity = company_data['debtToEquityRatio'].fillna(0)
        if len(debt_equity) >= 3:
            leverage_trend = np.polyfit(range(len(debt_equity)), debt_equity, 1)[0]
            trend_risks['leverage_trend_risk'] = max(0, leverage_trend * 5)
        else:
            trend_risks['leverage_trend_risk'] = 0
    else:
        trend_risks['leverage_trend_risk'] = 0
    
    return trend_risks


def _detect_alert_triggers(company_data: pd.DataFrame, financial_risks: Dict, 
                          operational_risks: Dict, liquidity_risks: Dict) -> List[Dict]:
    """Detect specific alert triggers"""
    
    alerts = []
    
    # Financial alert triggers
    if financial_risks.get('revenue_decline_risk', 0) > 0.3:
        alerts.append({
            'type': 'Financial',
            'severity': 'High',
            'trigger': 'Revenue Decline Pattern',
            'description': f"Revenue decline in {financial_risks['revenue_decline_risk']*100:.0f}% of periods"
        })
    
    if financial_risks.get('leverage_risk', 0) > 1.5:
        alerts.append({
            'type': 'Financial', 
            'severity': 'Medium',
            'trigger': 'High Leverage',
            'description': f"Debt-to-equity ratio of {financial_risks['leverage_risk']:.2f}"
        })
    
    if financial_risks.get('interest_coverage_risk', 0) > 7:
        alerts.append({
            'type': 'Financial',
            'severity': 'High',
            'trigger': 'Interest Coverage Risk',
            'description': "Interest coverage below safe thresholds"
        })
    
    # Operational alert triggers
    if operational_risks.get('negative_ocf_risk', 0) > 0.2:
        alerts.append({
            'type': 'Operational',
            'severity': 'High',
            'trigger': 'Cash Flow Issues',
            'description': f"Negative operating cash flow in {operational_risks['negative_ocf_risk']*100:.0f}% of periods"
        })
    
    if operational_risks.get('capex_sustainability_risk', 0) > 0.5:
        alerts.append({
            'type': 'Operational',
            'severity': 'Medium',
            'trigger': 'CapEx Sustainability',
            'description': "Capital expenditure exceeding operating cash flow"
        })
    
    # Liquidity alert triggers
    if liquidity_risks.get('current_ratio_risk', 0) > 1.0:
        alerts.append({
            'type': 'Liquidity',
            'severity': 'High',
            'trigger': 'Liquidity Constraint',
            'description': "Current ratio below 1.0"
        })
    
    if liquidity_risks.get('cash_coverage_risk', 0) > 0.2:
        alerts.append({
            'type': 'Liquidity',
            'severity': 'Medium',
            'trigger': 'Cash Coverage',
            'description': "Low cash coverage of current liabilities"
        })
    
    return alerts


def _calculate_overall_risk_score(financial_risks: Dict, operational_risks: Dict, 
                                 liquidity_risks: Dict, market_risks: Dict, trend_risks: Dict) -> float:
    """Calculate composite risk score"""
    
    # Normalize and weight risk components
    financial_score = min(10, (
        financial_risks.get('revenue_volatility', 0) / 10 +
        financial_risks.get('revenue_decline_risk', 0) * 10 +
        financial_risks.get('margin_compression', 0) +
        financial_risks.get('leverage_risk', 0) / 2 +
        financial_risks.get('interest_coverage_risk', 0)
    ))
    
    operational_score = min(10, (
        operational_risks.get('cash_flow_volatility', 0) / 10 +
        operational_risks.get('negative_ocf_risk', 0) * 10 +
        operational_risks.get('working_capital_risk', 0) * 5 +
        operational_risks.get('efficiency_deterioration', 0) * 5 +
        operational_risks.get('capex_sustainability_risk', 0) * 5
    ))
    
    liquidity_score = min(10, (
        liquidity_risks.get('current_ratio_risk', 0) * 3 +
        liquidity_risks.get('quick_ratio_risk', 0) * 5 +
        liquidity_risks.get('cash_coverage_risk', 0) * 10 +
        abs(liquidity_risks.get('working_capital_trend', 0)) / 1000000000
    ))
    
    market_score = min(10, (
        market_risks.get('valuation_risk', 0) * 5 +
        market_risks.get('price_book_risk', 0) * 3 +
        market_risks.get('ev_multiple_risk', 0) * 2 +
        market_risks.get('market_cap_volatility', 0) * 20
    ))
    
    trend_score = min(10, (
        trend_risks.get('revenue_trend_risk', 0) * 5 +
        trend_risks.get('profitability_trend_risk', 0) +
        trend_risks.get('roe_trend_risk', 0) +
        trend_risks.get('leverage_trend_risk', 0)
    ))
    
    # Weighted composite score
    composite_score = (
        financial_score * 0.3 +
        operational_score * 0.25 +
        liquidity_score * 0.25 +
        market_score * 0.1 +
        trend_score * 0.1
    )
    
    return min(10, composite_score)

def _generate_critical_alerts(company_data: pd.DataFrame, risk_data: Dict) -> List[Dict]:
    """Generate critical severity alerts"""
    
    critical_alerts = []
    
    # Negative FCF streak >= 2 years
    if 'freeCashFlow' in company_data.columns:
        fcf = company_data['freeCashFlow'].fillna(0)
        negative_streak = 0
        max_negative_streak = 0
        
        for value in fcf:
            if value < 0:
                negative_streak += 1
                max_negative_streak = max(max_negative_streak, negative_streak)
            else:
                negative_streak = 0
        
        if max_negative_streak >= 2:
            critical_alerts.append({
                'type': 'Cash Flow',
                'severity': 'Critical',
                'trigger': f'Negative FCF Streak: {max_negative_streak} years',
                'description': 'Extended period of negative free cash flow generation',
                'action_required': 'Immediate cash flow optimization and capital allocation review'
            })
    
    # Interest Coverage < 2x
    if 'interestCoverageRatio' in company_data.columns:
        interest_coverage = company_data['interestCoverageRatio'].fillna(0)
        if len(interest_coverage) > 0 and interest_coverage.iloc[-1] < 2:
            critical_alerts.append({
                'type': 'Solvency',
                'severity': 'Critical',
                'trigger': f'Interest Coverage: {interest_coverage.iloc[-1]:.2f}x',
                'description': 'Interest coverage below critical threshold',
                'action_required': 'Debt restructuring and earnings improvement required'
            })
    
    # Current Ratio < 1.0
    if 'currentRatio' in company_data.columns:
        current_ratio = company_data['currentRatio'].fillna(0)
        if len(current_ratio) > 0 and current_ratio.iloc[-1] < 1.0:
            critical_alerts.append({
                'type': 'Liquidity',
                'severity': 'Critical',
                'trigger': f'Current Ratio: {current_ratio.iloc[-1]:.2f}',
                'description': 'Current assets insufficient to cover current liabilities',
                'action_required': 'Immediate liquidity enhancement measures required'
            })
    
    # Major leverage increase
    if 'debtToEquityRatio' in company_data.columns:
        debt_equity = company_data['debtToEquityRatio'].fillna(0)
        if len(debt_equity) > 1:
            leverage_change = debt_equity.iloc[-1] - debt_equity.iloc[-2]
            if leverage_change > 0.5:
                critical_alerts.append({
                    'type': 'Leverage',
                    'severity': 'Critical',
                    'trigger': f'Leverage Spike: +{leverage_change:.2f}',
                    'description': 'Significant year-over-year leverage increase',
                    'action_required': 'Debt management and deleveraging strategy required'
                })
    
    return critical_alerts


def _generate_warning_alerts(company_data: pd.DataFrame, risk_data: Dict) -> List[Dict]:
    """Generate warning severity alerts"""
    
    warning_alerts = []
    
    # Margin compression > 150 bps
    if 'netProfitMargin' in company_data.columns:
        net_margin = company_data['netProfitMargin'].fillna(0)
        if len(net_margin) > 1:
            margin_change = net_margin.iloc[-1] - net_margin.iloc[-2]
            if margin_change < -1.5:
                warning_alerts.append({
                    'type': 'Profitability',
                    'severity': 'Warning',
                    'trigger': f'Margin Compression: {margin_change:.1f}pp',
                    'description': 'Significant profit margin deterioration',
                    'action_required': 'Cost management and pricing strategy review'
                })
    
    # Revenue volatility
    revenue_volatility = risk_data.get('financial_risks', {}).get('revenue_volatility', 0)
    if revenue_volatility > 15:
        warning_alerts.append({
            'type': 'Revenue',
            'severity': 'Warning',
            'trigger': f'Revenue Volatility: {revenue_volatility:.1f}%',
            'description': 'High revenue growth volatility indicating business instability',
            'action_required': 'Revenue diversification and stability improvement'
        })
    
    # Cash position deterioration
    if 'cashAndCashEquivalents' in company_data.columns:
        cash = company_data['cashAndCashEquivalents'].fillna(0)
        if len(cash) > 1:
            cash_change_pct = (cash.iloc[-1] - cash.iloc[-2]) / cash.iloc[-2] if cash.iloc[-2] != 0 else 0
            if cash_change_pct < -0.3:
                warning_alerts.append({
                    'type': 'Liquidity',
                    'severity': 'Warning',
                    'trigger': f'Cash Drawdown: {cash_change_pct*100:.0f}%',
                    'description': 'Significant cash position deterioration',
                    'action_required': 'Cash preservation and generation strategies'
                })
    
    return warning_alerts


def _generate_monitoring_alerts(company_data: pd.DataFrame) -> List[Dict]:
    """Generate monitoring severity alerts"""
    
    monitoring_alerts = []
    
    # ROE deterioration
    if 'returnOnEquity' in company_data.columns:
        roe = company_data['returnOnEquity'].fillna(0)
        if len(roe) > 2:
            roe_trend = np.polyfit(range(len(roe)), roe, 1)[0]
            if roe_trend < -1:
                monitoring_alerts.append({
                    'type': 'Profitability',
                    'severity': 'Monitoring',
                    'trigger': f'ROE Trend: {roe_trend:.1f}pp/year',
                    'description': 'Declining return on equity trend',
                    'action_required': 'Monitor profitability drivers and capital efficiency'
                })
    
    # Asset turnover decline
    if 'assetTurnover' in company_data.columns:
        asset_turnover = company_data['assetTurnover'].fillna(0)
        if len(asset_turnover) > 1:
            turnover_change = asset_turnover.iloc[-1] - asset_turnover.iloc[-2]
            if turnover_change < -0.1:
                monitoring_alerts.append({
                    'type': 'Efficiency',
                    'severity': 'Monitoring',
                    'trigger': f'Asset Turnover Decline: {turnover_change:.2f}',
                    'description': 'Declining asset utilization efficiency',
                    'action_required': 'Review asset utilization and operational efficiency'
                })
    
    # Market valuation monitoring
    if 'priceToEarningsRatio' in company_data.columns:
        pe_ratio = company_data['priceToEarningsRatio'].fillna(0)
        if len(pe_ratio) > 0 and pe_ratio.iloc[-1] > 30:
            monitoring_alerts.append({
                'type': 'Valuation',
                'severity': 'Monitoring',
                'trigger': f'P/E Ratio: {pe_ratio.iloc[-1]:.1f}x',
                'description': 'High market valuation multiple',
                'action_required': 'Monitor valuation sustainability and growth delivery'
            })
    
    return monitoring_alerts


def _calculate_alert_frequency(critical_alerts: List, warning_alerts: List, monitoring_alerts: List) -> str:
    """Calculate alert frequency classification"""
    
    total_alerts = len(critical_alerts) + len(warning_alerts) + len(monitoring_alerts)
    
    if total_alerts >= 8:
        return "High Frequency"
    elif total_alerts >= 4:
        return "Moderate Frequency"
    else:
        return "Low Frequency"


def _calculate_priority_score(critical_alerts: List, warning_alerts: List) -> float:
    """Calculate alert priority score"""
    
    critical_weight = 10
    warning_weight = 5
    
    priority_score = len(critical_alerts) * critical_weight + len(warning_alerts) * warning_weight
    return min(100, priority_score)


def _analyze_alert_trends(company_data: pd.DataFrame, risk_data: Dict) -> Dict:
    """Analyze alert trend patterns"""
    
    trends = {}
    
    # Overall risk trend
    overall_score = risk_data.get('overall_risk_score', 5)
    if overall_score > 6:
        trends['risk_direction'] = 'Increasing'
    elif overall_score < 4:
        trends['risk_direction'] = 'Decreasing'
    else:
        trends['risk_direction'] = 'Stable'
    
    # Financial health trend
    financial_risks = risk_data.get('financial_risks', {})
    leverage_trend = financial_risks.get('leverage_trend', 0)
    margin_compression = financial_risks.get('margin_compression', 0)
    
    if leverage_trend > 0.2 or margin_compression > 2:
        trends['financial_health'] = 'Deteriorating'
    elif leverage_trend < -0.1 and margin_compression < 1:
        trends['financial_health'] = 'Improving'
    else:
        trends['financial_health'] = 'Stable'
    
    # Liquidity trend
    liquidity_risks = risk_data.get('liquidity_risks', {})
    liquidity_deterioration = liquidity_risks.get('liquidity_deterioration', 0)
    
    if liquidity_deterioration > 0.2:
        trends['liquidity_trend'] = 'Worsening'
    elif liquidity_deterioration < -0.1:
        trends['liquidity_trend'] = 'Improving'
    else:
        trends['liquidity_trend'] = 'Stable'
    
    return trends


def _calculate_severity_distribution(critical_alerts: List, warning_alerts: List, monitoring_alerts: List) -> Dict:
    """Calculate alert severity distribution"""
    
    total_alerts = len(critical_alerts) + len(warning_alerts) + len(monitoring_alerts)
    
    if total_alerts == 0:
        return {'critical': 0, 'warning': 0, 'monitoring': 0}
    
    return {
        'critical': len(critical_alerts) / total_alerts,
        'warning': len(warning_alerts) / total_alerts,
        'monitoring': len(monitoring_alerts) / total_alerts
    }

def _calculate_financial_risk_score(financial_risks: Dict) -> float:
    """Calculate financial risk component score"""
    
    score = (
        min(10, financial_risks.get('revenue_volatility', 0) / 5) +
        financial_risks.get('revenue_decline_risk', 0) * 10 +
        min(10, financial_risks.get('margin_compression', 0)) +
        min(10, financial_risks.get('leverage_risk', 0) * 2) +
        financial_risks.get('interest_coverage_risk', 0)
    ) / 5
    
    return min(10, score)


def _calculate_operational_risk_score(operational_risks: Dict) -> float:
    """Calculate operational risk component score"""
    
    score = (
        min(10, operational_risks.get('cash_flow_volatility', 0) / 3) +
        operational_risks.get('negative_ocf_risk', 0) * 10 +
        min(10, operational_risks.get('working_capital_risk', 0) * 10) +
        min(10, operational_risks.get('efficiency_deterioration', 0) * 10) +
        operational_risks.get('capex_sustainability_risk', 0) * 10
    ) / 5
    
    return min(10, score)


def _calculate_market_risk_score(market_risks: Dict) -> float:
    """Calculate market risk component score"""
    
    score = (
        market_risks.get('valuation_risk', 0) * 10 +
        market_risks.get('price_book_risk', 0) * 5 +
        market_risks.get('ev_multiple_risk', 0) * 3 +
        min(10, market_risks.get('market_cap_volatility', 0) * 50)
    ) / 4
    
    return min(10, score)


def _calculate_liquidity_risk_score(liquidity_risks: Dict) -> float:
    """Calculate liquidity risk component score"""
    
    score = (
        liquidity_risks.get('current_ratio_risk', 0) * 5 +
        liquidity_risks.get('quick_ratio_risk', 0) * 8 +
        liquidity_risks.get('cash_coverage_risk', 0) * 20 +
        min(10, liquidity_risks.get('liquidity_deterioration', 0) * 10) +
        min(10, abs(liquidity_risks.get('working_capital_trend', 0)) / 100000000)
    ) / 5
    
    return min(10, score)


def _calculate_alert_severity_score(alert_summary: Dict) -> float:
    """Calculate alert severity component score"""
    
    if not alert_summary:
        return 0
    
    critical_count = alert_summary.get('critical_count', 0)
    warning_count = alert_summary.get('warning_count', 0)
    priority_score = alert_summary.get('priority_score', 0)
    
    score = (critical_count * 3 + warning_count * 1.5 + priority_score / 20)
    
    return min(10, score)


def _analyze_risk_trend(risk_data: Dict, alert_trends: Dict) -> str:
    """Analyze overall risk trend direction"""
    
    risk_direction = alert_trends.get('risk_direction', 'Stable')
    financial_health = alert_trends.get('financial_health', 'Stable')
    liquidity_trend = alert_trends.get('liquidity_trend', 'Stable')
    
    # Weight different trend components
    trend_score = 0
    
    if risk_direction == 'Increasing':
        trend_score += 2
    elif risk_direction == 'Decreasing':
        trend_score -= 2
    
    if financial_health == 'Deteriorating':
        trend_score += 2
    elif financial_health == 'Improving':
        trend_score -= 2
    
    if liquidity_trend == 'Worsening':
        trend_score += 1
    elif liquidity_trend == 'Improving':
        trend_score -= 1
    
    if trend_score >= 3:
        return "Rapidly Deteriorating"
    elif trend_score >= 1:
        return "Deteriorating"
    elif trend_score <= -3:
        return "Rapidly Improving"
    elif trend_score <= -1:
        return "Improving"
    else:
        return "Stable"