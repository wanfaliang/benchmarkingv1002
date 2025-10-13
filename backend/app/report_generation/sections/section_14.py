"""Section 14: Insider Activity & Corporate Sentiment Analysis"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_data_table,
    build_plotly_chart,
    build_section_divider,
    build_info_box,
    format_currency,
    format_percentage,
    format_number
)

def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 14: Insider Activity & Corporate Sentiment Analysis.
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    
    try:
        insider_latest_df = collector.get_insider_trading_latest()
        insider_stats_df = collector.get_insider_statistics()
    except Exception as e:
        print(f"Warning: Could not retrieve insider data: {e}")
        insider_latest_df = pd.DataFrame()
        insider_stats_df = pd.DataFrame()
    
    # Build all subsections
    section_14a1_html = _build_transaction_patterns_overview(insider_latest_df, companies)
    section_14a2_html = _build_timing_clusters_analysis(insider_latest_df, companies)
    section_14b1_html = _build_insider_statistics_trends(insider_stats_df, companies)
    section_14b2_html = _build_participation_rates_analysis(insider_stats_df, insider_latest_df, companies)
    section_14c1_html = _build_role_based_activity_analysis(insider_latest_df, companies)
    section_14c2_html = _build_governance_patterns_analysis(insider_latest_df, companies)
    section_14d_html = _build_insider_sentiment_scoring(insider_latest_df, insider_stats_df, companies)
    section_14e_html = _build_visualization_dashboard(insider_latest_df, insider_stats_df, companies)
    section_14f_html = _build_strategic_insights(insider_latest_df, insider_stats_df, companies)
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        {section_14a1_html}
        {build_section_divider() if section_14a2_html else ""}
        {section_14a2_html}
        {build_section_divider() if section_14b1_html else ""}
        {section_14b1_html}
        {build_section_divider() if section_14b2_html else ""}
        {section_14b2_html}
        {build_section_divider() if section_14c1_html else ""}
        {section_14c1_html}
        {build_section_divider() if section_14c2_html else ""}
        {section_14c2_html}
        {build_section_divider() if section_14d_html else ""}
        {section_14d_html}
        {build_section_divider() if section_14e_html else ""}
        {section_14e_html}
        {build_section_divider() if section_14f_html else ""}
        {section_14f_html}
    </div>
    """
    
    return generate_section_wrapper(14, "Insider Activity & Corporate Sentiment", content)


# =============================================================================
# SUBSECTION 14A.1: TRANSACTION PATTERNS OVERVIEW
# =============================================================================

def _build_transaction_patterns_overview(insider_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14A.1: Transaction Patterns Overview"""
    
    if insider_df.empty:
        return build_info_box(
            "<p>No insider trading data available for transaction pattern analysis.</p>",
            "warning",
            "14A.1 Transaction Patterns Overview"
        )
    
    # Analyze transaction patterns
    transaction_patterns = _analyze_transaction_patterns(insider_df, companies)
    
    if not transaction_patterns:
        return build_info_box(
            "<p>Insufficient data for transaction pattern analysis.</p>",
            "warning",
            "14A.1 Transaction Patterns Overview"
        )
    
    # Create summary statistics
    total_companies = len(transaction_patterns)
    total_transactions = sum(p['total_transactions'] for p in transaction_patterns.values())
    total_buys = sum(p['buy_transactions'] for p in transaction_patterns.values())
    total_sells = sum(p['sell_transactions'] for p in transaction_patterns.values())
    avg_buy_sell_ratio = np.mean([p['buy_sell_ratio'] for p in transaction_patterns.values()])
    bullish_count = sum(1 for p in transaction_patterns.values() if p['transaction_sentiment'] == 'Bullish')
    
    stat_cards = [
        {
            "label": "Total Transactions",
            "value": f"{total_transactions:,}",
            "description": f"Across {total_companies} companies",
            "type": "info"
        },
        {
            "label": "Buy Transactions",
            "value": f"{total_buys:,}",
            "description": f"{(total_buys/max(total_transactions,1)*100):.1f}% of total",
            "type": "success"
        },
        {
            "label": "Sell Transactions",
            "value": f"{total_sells:,}",
            "description": f"{(total_sells/max(total_transactions,1)*100):.1f}% of total",
            "type": "danger"
        },
        {
            "label": "Avg Buy/Sell Ratio",
            "value": f"{avg_buy_sell_ratio:.2f}",
            "description": "Portfolio average",
            "type": "success" if avg_buy_sell_ratio >= 1.2 else "warning" if avg_buy_sell_ratio >= 0.8 else "danger"
        },
        {
            "label": "Bullish Sentiment",
            "value": f"{bullish_count}/{total_companies}",
            "description": f"{(bullish_count/total_companies*100):.0f}% of companies",
            "type": "success" if bullish_count >= total_companies * 0.5 else "info"
        }
    ]
    
    # Create transaction patterns table
    table_data = []
    for company_name, patterns in transaction_patterns.items():
        table_data.append({
            'Company': company_name,
            'Total Transactions': patterns['total_transactions'],
            'Buy Count': patterns['buy_transactions'],
            'Sell Count': patterns['sell_transactions'],
            'Buy/Sell Ratio': f"{patterns['buy_sell_ratio']:.2f}",
            'Buy Value ($M)': f"${patterns['total_buy_value']/1e6:.1f}",
            'Sell Value ($M)': f"${patterns['total_sell_value']/1e6:.1f}",
            'Recent (90d)': patterns['recent_transactions_90d'],
            'Sentiment': patterns['transaction_sentiment']
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "transaction-patterns-table")
    
    # Create charts
    companies_list = list(transaction_patterns.keys())
    
    # Chart 1: Buy vs Sell Transactions
    buy_counts = [transaction_patterns[comp]['buy_transactions'] for comp in companies_list]
    sell_counts = [transaction_patterns[comp]['sell_transactions'] for comp in companies_list]
    
    chart1_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Buy Transactions',
                'x': companies_list,
                'y': buy_counts,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Buys: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Sell Transactions',
                'x': companies_list,
                'y': sell_counts,
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{x}</b><br>Sells: %{y}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Buy vs Sell Transaction Counts',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Transaction Count'},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    chart1_html = build_plotly_chart(chart1_data, "chart-14a1-buy-sell-counts")
    
    # Chart 2: Buy/Sell Ratios
    buy_sell_ratios = [transaction_patterns[comp]['buy_sell_ratio'] for comp in companies_list]
    ratio_colors = ['#10b981' if r >= 1.5 else '#f59e0b' if r >= 0.8 else '#ef4444' for r in buy_sell_ratios]
    
    chart2_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': buy_sell_ratios,
            'marker': {'color': ratio_colors},
            'hovertemplate': '<b>%{x}</b><br>Ratio: %{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Buy/Sell Ratio Analysis',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Buy/Sell Ratio'},
            'shapes': [{
                'type': 'line',
                'x0': -0.5,
                'x1': len(companies_list) - 0.5,
                'y0': 1.0,
                'y1': 1.0,
                'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
            }],
            'annotations': [{
                'x': len(companies_list) - 1,
                'y': 1.0,
                'text': 'Neutral (1.0)',
                'showarrow': False,
                'yshift': 10
            }]
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14a1-buy-sell-ratios")
    
    # Chart 3: Transaction Values
    buy_values = [transaction_patterns[comp]['total_buy_value']/1e6 for comp in companies_list]
    sell_values = [transaction_patterns[comp]['total_sell_value']/1e6 for comp in companies_list]
    
    chart3_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Buy Value',
                'x': companies_list,
                'y': buy_values,
                'marker': {'color': '#059669'},
                'hovertemplate': '<b>%{x}</b><br>Buy: $%{y:.1f}M<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Sell Value',
                'x': companies_list,
                'y': sell_values,
                'marker': {'color': '#dc2626'},
                'hovertemplate': '<b>%{x}</b><br>Sell: $%{y:.1f}M<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Transaction Value Analysis',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Value ($M)'},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14a1-transaction-values")
    
    # Chart 4: Sentiment Distribution
    sentiment_counts = {'Bullish': 0, 'Positive': 0, 'Neutral': 0, 'Bearish': 0}
    for patterns in transaction_patterns.values():
        sentiment = patterns['transaction_sentiment']
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
    
    chart4_data = {
        'data': [{
            'type': 'pie',
            'labels': list(sentiment_counts.keys()),
            'values': list(sentiment_counts.values()),
            'marker': {'colors': ['#059669', '#10b981', '#f59e0b', '#ef4444']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Insider Sentiment Distribution'
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14a1-sentiment-distribution")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Portfolio Transaction Activity:</strong> {total_transactions:,} total transactions across {total_companies} companies 
    with insider activity, comprising {total_buys:,} buy transactions and {total_sells:,} sell transactions 
    (average buy/sell ratio: {avg_buy_sell_ratio:.2f}).</p>
    
    <p><strong>Activity Intensity:</strong> {bullish_count}/{total_companies} companies showing bullish insider sentiment, 
    indicating {'strong positive insider confidence' if bullish_count >= total_companies * 0.5 else 'moderate insider engagement' if bullish_count >= total_companies * 0.3 else 'mixed insider signals'}.</p>
    
    <p><strong>Transaction Intelligence:</strong> The portfolio exhibits 
    {'high-conviction insider activity' if avg_buy_sell_ratio >= 1.3 and bullish_count >= total_companies * 0.4 else 'moderate insider engagement' if avg_buy_sell_ratio >= 1.0 else 'cautious insider positioning'}, 
    providing valuable sentiment indicators for investment decision-making.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14a1"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14A.1 Insider Trading Activity Overview & Buy/Sell Patterns</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Transaction Patterns Analysis</h4>
            {table_html}
            
            <h4>Transaction Pattern Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    
    <script>
        function toggleSubsection(id) {{
            var element = document.getElementById(id);
            if (element.style.display === 'none') {{
                element.style.display = 'block';
            }} else {{
                element.style.display = 'none';
            }}
        }}
    </script>
    """
    
    return html


# =============================================================================
# SUBSECTION 14A.2: TIMING CLUSTERS ANALYSIS
# =============================================================================

def _build_timing_clusters_analysis(insider_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14A.2: Timing Clusters Analysis"""
    
    if insider_df.empty:
        return ""
    
    # Analyze timing clusters
    timing_analysis = _analyze_timing_clusters(insider_df, companies)
    
    if not timing_analysis:
        return build_info_box(
            "<p>Insufficient data for timing cluster analysis.</p>",
            "warning",
            "14A.2 Timing Clusters Analysis"
        )
    
    # Create summary statistics
    total_companies = len(timing_analysis)
    avg_timing_score = np.mean([t['timing_score'] for t in timing_analysis.values()])
    distributed_count = sum(1 for t in timing_analysis.values() if t['timing_distribution'] == 'Distributed')
    clustered_count = sum(1 for t in timing_analysis.values() if t['timing_distribution'] == 'Clustered')
    unusual_activity_count = sum(1 for t in timing_analysis.values() if t['unusual_activity'] != 'None Detected')
    total_large_txns = sum(t['large_transactions'] for t in timing_analysis.values())
    
    stat_cards = [
        {
            "label": "Avg Timing Score",
            "value": f"{avg_timing_score:.1f}/10",
            "description": "Portfolio timing quality",
            "type": "success" if avg_timing_score >= 7 else "info" if avg_timing_score >= 5 else "warning"
        },
        {
            "label": "Distributed Timing",
            "value": f"{distributed_count}/{total_companies}",
            "description": "Well-distributed patterns",
            "type": "success"
        },
        {
            "label": "Clustered Timing",
            "value": f"{clustered_count}/{total_companies}",
            "description": "Concentrated patterns",
            "type": "warning"
        },
        {
            "label": "Large Transactions",
            "value": f"{total_large_txns:,}",
            "description": "Significant transactions",
            "type": "info"
        },
        {
            "label": "Unusual Activity",
            "value": f"{unusual_activity_count}/{total_companies}",
            "description": "Companies flagged",
            "type": "danger" if unusual_activity_count >= total_companies * 0.3 else "warning" if unusual_activity_count > 0 else "success"
        }
    ]
    
    # Create timing analysis table
    table_data = []
    for company_name, analysis in timing_analysis.items():
        table_data.append({
            'Company': company_name,
            'Total Transactions': analysis['total_transactions'],
            'Timing Distribution': analysis['timing_distribution'],
            'Peak Quarter': analysis['peak_quarter'],
            'Large Transactions': analysis['large_transactions'],
            'Recent (6M)': analysis['recent_activity_6m'],
            'Unusual Activity': analysis['unusual_activity'],
            'Timing Score': f"{analysis['timing_score']:.1f}/10"
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "timing-analysis-table")
    
    # Create charts
    companies_list = list(timing_analysis.keys())
    
    # Chart 1: Timing Scores
    timing_scores = [timing_analysis[comp]['timing_score'] for comp in companies_list]
    score_colors = ['#10b981' if s >= 7 else '#f59e0b' if s >= 5 else '#ef4444' for s in timing_scores]
    
    chart1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': timing_scores,
            'marker': {'color': score_colors},
            'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': 'Transaction Timing Quality Scores',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Timing Score (0-10)', 'range': [0, 10]}
        }
    }
    chart1_html = build_plotly_chart(chart1_data, "chart-14a2-timing-scores")
    
    # Chart 2: Recent vs Total Activity
    total_transactions = [timing_analysis[comp]['total_transactions'] for comp in companies_list]
    recent_activity = [timing_analysis[comp]['recent_activity_6m'] for comp in companies_list]
    
    chart2_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Total Transactions',
                'x': companies_list,
                'y': total_transactions,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Total: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Recent (6M)',
                'x': companies_list,
                'y': recent_activity,
                'marker': {'color': '#f59e0b'},
                'hovertemplate': '<b>%{x}</b><br>Recent: %{y}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Recent vs Total Transaction Activity',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Transaction Count'},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14a2-recent-activity")
    
    # Chart 3: Large Transactions
    large_transactions = [timing_analysis[comp]['large_transactions'] for comp in companies_list]
    
    chart3_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': large_transactions,
            'marker': {'color': '#8b5cf6'},
            'hovertemplate': '<b>%{x}</b><br>Large Txns: %{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Large Transaction Activity',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Large Transaction Count'}
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14a2-large-transactions")
    
    # Chart 4: Timing Distribution Types
    timing_types = {'Distributed': 0, 'Clustered': 0, 'Moderate': 0}
    for analysis in timing_analysis.values():
        timing_dist = analysis['timing_distribution']
        if timing_dist in timing_types:
            timing_types[timing_dist] += 1
    
    chart4_data = {
        'data': [{
            'type': 'pie',
            'labels': list(timing_types.keys()),
            'values': list(timing_types.values()),
            'marker': {'colors': ['#10b981', '#ef4444', '#f59e0b']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Timing Distribution Patterns'
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14a2-timing-distribution")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Portfolio Timing Quality:</strong> {avg_timing_score:.1f}/10 average timing score across {total_companies} companies, 
    with {distributed_count} companies showing distributed transaction patterns and {clustered_count} showing clustered patterns.</p>
    
    <p><strong>Large Transaction Activity:</strong> {total_large_txns} significant transactions identified requiring enhanced monitoring 
    and analysis for potential unusual activity patterns.</p>
    
    <p><strong>Unusual Activity Detection:</strong> {unusual_activity_count}/{total_companies} companies flagged with unusual activity patterns, 
    requiring {'enhanced surveillance' if unusual_activity_count >= total_companies * 0.3 else 'standard monitoring' if unusual_activity_count > 0 else 'no special attention'}.</p>
    
    <p><strong>Strategic Timing Intelligence:</strong> The portfolio exhibits 
    {'high-quality timing intelligence' if avg_timing_score >= 7 and unusual_activity_count <= total_companies * 0.2 else 'moderate timing analysis' if avg_timing_score >= 5 else 'complex timing patterns'} 
    for insider activity assessment and investment decision support.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14a2"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14A.2 Transaction Timing Analysis & Unusual Activity Detection</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Timing Analysis Results</h4>
            {table_html}
            
            <h4>Timing Pattern Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION STUBS (TO BE IMPLEMENTED IN NEXT PHASES)
# =============================================================================

# =============================================================================
# SUBSECTION 14B.1: INSIDER STATISTICS TRENDS
# =============================================================================

def _build_insider_statistics_trends(insider_stats_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14B.1: Insider Statistics Trends"""
    
    if insider_stats_df.empty:
        return build_info_box(
            "<p>No insider statistics data available for trend analysis.</p>",
            "warning",
            "14B.1 Insider Statistics Trends"
        )
    
    # Analyze insider trends
    insider_trends = _analyze_insider_statistics_trends(insider_stats_df, companies)
    
    if not insider_trends:
        return build_info_box(
            "<p>Insufficient data for insider statistics trend analysis.</p>",
            "warning",
            "14B.1 Insider Statistics Trends"
        )
    
    # Create summary statistics
    total_companies = len(insider_trends)
    positive_trends = sum(1 for t in insider_trends.values() if t['trend_quality'] == 'Positive')
    increasing_ratios = sum(1 for t in insider_trends.values() if t['acquired_disposed_ratio_trend'] == 'Increasing')
    high_intensity = sum(1 for t in insider_trends.values() if t['transaction_intensity'] == 'High')
    avg_ratio_change = np.mean([t['ratio_change_pct'] for t in insider_trends.values()])
    
    stat_cards = [
        {
            "label": "Positive Trends",
            "value": f"{positive_trends}/{total_companies}",
            "description": f"{(positive_trends/total_companies*100):.0f}% of companies",
            "type": "success" if positive_trends >= total_companies * 0.5 else "info"
        },
        {
            "label": "Increasing Ratios",
            "value": f"{increasing_ratios}/{total_companies}",
            "description": "Buy/sell ratio trend",
            "type": "success" if increasing_ratios >= total_companies * 0.5 else "warning"
        },
        {
            "label": "High Intensity",
            "value": f"{high_intensity}/{total_companies}",
            "description": "Current transaction intensity",
            "type": "info"
        },
        {
            "label": "Avg Ratio Change",
            "value": f"{avg_ratio_change:+.1f}%",
            "description": "Recent vs historical",
            "type": "success" if avg_ratio_change > 10 else "info" if avg_ratio_change > -10 else "danger"
        }
    ]
    
    # Create insider trends table
    table_data = []
    for company_name, trends in insider_trends.items():
        table_data.append({
            'Company': company_name,
            'Periods': trends['periods_analyzed'],
            'Buy/Sell Ratio Trend': trends['acquired_disposed_ratio_trend'],
            'Total Acquired Trend': trends['total_acquired_trend'],
            'Purchases Trend': trends['total_purchases_trend'],
            'Ratio Change (%)': f"{trends['ratio_change_pct']:+.1f}",
            'Latest Intensity': trends['transaction_intensity'],
            'Trend Quality': trends['trend_quality']
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "insider-trends-table")
    
    # Create charts
    companies_list = list(insider_trends.keys())
    
    # Chart 1: Buy/Sell Ratio Changes
    ratio_changes = [insider_trends[comp]['ratio_change_pct'] for comp in companies_list]
    change_colors = ['#10b981' if c > 0 else '#ef4444' if c < 0 else '#94a3b8' for c in ratio_changes]
    
    chart1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': ratio_changes,
            'marker': {'color': change_colors},
            'hovertemplate': '<b>%{x}</b><br>Change: %{y:+.1f}%<extra></extra>'
        }],
        'layout': {
            'title': 'Buy/Sell Ratio Change Analysis (Recent vs Historical)',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Change (%)', 'zeroline': True},
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
    chart1_html = build_plotly_chart(chart1_data, "chart-14b1-ratio-changes")
    
    # Chart 2: Trend Quality Distribution
    trend_qualities = {'Positive': 0, 'Mixed': 0, 'Negative': 0}
    for trends in insider_trends.values():
        quality = trends['trend_quality']
        if quality in trend_qualities:
            trend_qualities[quality] += 1
    
    chart2_data = {
        'data': [{
            'type': 'pie',
            'labels': list(trend_qualities.keys()),
            'values': list(trend_qualities.values()),
            'marker': {'colors': ['#059669', '#f59e0b', '#ef4444']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Insider Trend Quality Distribution'
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14b1-trend-quality")
    
    # Chart 3: Transaction Intensity Distribution
    intensity_counts = {'High': 0, 'Moderate': 0, 'Low': 0}
    for trends in insider_trends.values():
        intensity = trends['transaction_intensity']
        if intensity in intensity_counts:
            intensity_counts[intensity] += 1
    
    chart3_data = {
        'data': [{
            'type': 'pie',
            'labels': list(intensity_counts.keys()),
            'values': list(intensity_counts.values()),
            'marker': {'colors': ['#ef4444', '#f59e0b', '#3b82f6']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Current Transaction Intensity Distribution'
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14b1-intensity")
    
    # Chart 4: Data Coverage (Periods Analyzed)
    periods_analyzed = [insider_trends[comp]['periods_analyzed'] for comp in companies_list]
    
    chart4_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': periods_analyzed,
            'marker': {'color': '#667eea'},
            'hovertemplate': '<b>%{x}</b><br>Periods: %{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Historical Data Coverage Analysis',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Periods Analyzed'}
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14b1-coverage")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Portfolio Trend Assessment:</strong> {positive_trends}/{total_companies} companies exhibit positive insider trends, 
    with {increasing_ratios}/{total_companies} showing increasing buy/sell ratio patterns, indicating 
    {'strong insider acquisition momentum' if increasing_ratios >= total_companies * 0.5 else 'moderate acquisition activity' if increasing_ratios >= total_companies * 0.3 else 'mixed acquisition patterns'}.</p>
    
    <p><strong>Activity Momentum:</strong> Average ratio change of {avg_ratio_change:+.1f}% (recent vs historical) suggests 
    {'positive sentiment shift' if avg_ratio_change > 20 else 'stable sentiment' if avg_ratio_change > -10 else 'declining acquisition activity'}. 
    {high_intensity} companies currently show high transaction intensity.</p>
    
    <p><strong>Strategic Intelligence:</strong> The portfolio demonstrates 
    {'strong positive insider momentum' if positive_trends >= total_companies * 0.5 and avg_ratio_change > 10 else 'moderate insider activity' if positive_trends >= total_companies * 0.3 else 'mixed insider signals'}, 
    providing valuable investment confidence indicators for portfolio optimization.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14b1"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14B.1 Net Shares & Transaction Value Trend Analysis</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Insider Statistics Trends Analysis</h4>
            {table_html}
            
            <h4>Trend Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 14B.2: PARTICIPATION RATES ANALYSIS
# =============================================================================

def _build_participation_rates_analysis(insider_stats_df: pd.DataFrame, insider_latest_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14B.2: Participation Rates Analysis"""
    
    if insider_stats_df.empty and insider_latest_df.empty:
        return ""
    
    # Analyze participation
    participation_analysis = _analyze_insider_participation(insider_stats_df, insider_latest_df, companies)
    
    if not participation_analysis:
        return build_info_box(
            "<p>Insufficient data for participation rate analysis.</p>",
            "warning",
            "14B.2 Participation Rates Analysis"
        )
    
    # Create summary statistics
    total_companies = len(participation_analysis)
    total_active_insiders = sum(p['active_insiders'] for p in participation_analysis.values())
    avg_activity_score = np.mean([p['activity_score'] for p in participation_analysis.values()])
    high_engagement = sum(1 for p in participation_analysis.values() if p['engagement_level'] in ['High', 'Very High'])
    high_intensity = sum(1 for p in participation_analysis.values() if p['activity_intensity'] == 'High')
    avg_frequency = np.mean([p['transaction_frequency'] for p in participation_analysis.values()])
    
    stat_cards = [
        {
            "label": "Avg Active Insiders",
            "value": f"{(total_active_insiders/total_companies):.1f}",
            "description": "Per company average",
            "type": "info"
        },
        {
            "label": "High Engagement",
            "value": f"{high_engagement}/{total_companies}",
            "description": "Companies with high engagement",
            "type": "success" if high_engagement >= total_companies * 0.5 else "info"
        },
        {
            "label": "Active Insiders",
            "value": f"{total_active_insiders}",
            "description": "Across portfolio",
            "type": "info"
        },
        {
            "label": "Avg Activity Score",
            "value": f"{avg_activity_score:.1f}/10",
            "description": "Portfolio activity level",
            "type": "success" if avg_activity_score >= 7 else "info" if avg_activity_score >= 5 else "warning"
        },
        {
            "label": "Avg Frequency",
            "value": f"{avg_frequency:.1f}/month",
            "description": "Transaction frequency",
            "type": "info"
        }
    ]
    
    # Create participation analysis table
    table_data = []
    for company_name, analysis in participation_analysis.items():
        table_data.append({
            'Company': company_name,
            'Active Insiders': analysis['active_insiders'],
            'Avg Txn Size': f"${analysis['avg_transaction_size']:,.0f}",
            'Frequency (/mo)': f"{analysis['transaction_frequency']:.1f}",
            'Activity Intensity': analysis['activity_intensity'],
            'Engagement Level': analysis['engagement_level'],
            'Activity Score': f"{analysis['activity_score']:.1f}/10"
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "participation-analysis-table")
    
    # Create charts
    companies_list = list(participation_analysis.keys())
    
    # Chart 1: Active Insider Counts
    active_insider_counts = [participation_analysis[comp]['active_insiders'] for comp in companies_list]
    count_colors = ['#10b981' if c >= 15 else '#f59e0b' if c >= 8 else '#ef4444' for c in active_insider_counts]
    
    chart1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': active_insider_counts,
            'marker': {'color': count_colors},
            'hovertemplate': '<b>%{x}</b><br>Active Insiders: %{y}<extra></extra>'
        }],
        'layout': {
            'title': 'Active Insider Count Analysis',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Number of Active Insiders'}
        }
    }
    chart1_html = build_plotly_chart(chart1_data, "chart-14b2-active-insiders")
    
    # Chart 2: Activity Scores
    activity_scores = [participation_analysis[comp]['activity_score'] for comp in companies_list]
    score_colors = ['#10b981' if s >= 7 else '#f59e0b' if s >= 5 else '#ef4444' for s in activity_scores]
    
    chart2_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': activity_scores,
            'marker': {'color': score_colors},
            'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': 'Insider Activity Score Analysis',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Activity Score (0-10)', 'range': [0, 10]}
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14b2-activity-scores")
    
    # Chart 3: Engagement Level Distribution
    engagement_counts = {'Very High': 0, 'High': 0, 'Moderate': 0, 'Low': 0}
    for analysis in participation_analysis.values():
        level = analysis['engagement_level']
        if level in engagement_counts:
            engagement_counts[level] += 1
    
    # Filter out zero counts
    engagement_counts = {k: v for k, v in engagement_counts.items() if v > 0}
    
    chart3_data = {
        'data': [{
            'type': 'pie',
            'labels': list(engagement_counts.keys()),
            'values': list(engagement_counts.values()),
            'marker': {'colors': ['#059669', '#10b981', '#f59e0b', '#ef4444'][:len(engagement_counts)]},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Engagement Level Distribution'
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14b2-engagement")
    
    # Chart 4: Transaction Frequency Analysis
    frequencies = [participation_analysis[comp]['transaction_frequency'] for comp in companies_list]
    
    chart4_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': frequencies,
            'marker': {'color': '#8b5cf6'},
            'hovertemplate': '<b>%{x}</b><br>Frequency: %{y:.1f}/month<extra></extra>'
        }],
        'layout': {
            'title': 'Transaction Frequency Analysis',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Transactions per Month'}
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14b2-frequency")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Portfolio Activity Assessment:</strong> Average of {(total_active_insiders/total_companies):.1f} active insiders per company across 
    {total_companies} companies, with {total_active_insiders} total active insiders portfolio-wide. {high_engagement}/{total_companies} companies 
    demonstrate high or very high engagement levels.</p>
    
    <p><strong>Activity Intelligence:</strong> Average activity score of {avg_activity_score:.1f}/10 indicates 
    {'strong insider engagement' if avg_activity_score >= 7 else 'moderate engagement' if avg_activity_score >= 5 else 'limited engagement'}. 
    Transaction frequency averages {avg_frequency:.1f} transactions per month across the portfolio.</p>
    
    <p><strong>Strategic Activity Insights:</strong> The portfolio exhibits 
    {'excellent insider engagement' if high_engagement >= total_companies * 0.5 and avg_activity_score >= 6 else 'good insider activity' if high_engagement >= total_companies * 0.3 else 'developing insider participation'}, 
    providing strong corporate confidence indicators for investment decision-making.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14b2"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14B.2 Insider Participation Rates & Activity Intensity Analysis</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Participation Analysis Results</h4>
            {table_html}
            
            <h4>Participation & Activity Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    """
    
    return html


# =============================================================================
# ANALYSIS HELPER FUNCTIONS FOR PHASE 2
# =============================================================================

def _analyze_insider_statistics_trends(insider_stats_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze insider statistics trends over time"""
    
    if insider_stats_df.empty:
        return {}
    
    insider_trends = {}
    
    for company_name in companies.keys():
        company_data = insider_stats_df[insider_stats_df['Company'] == company_name].copy()
        
        if company_data.empty:
            continue
        
        # Sort by year and quarter
        if 'year' in company_data.columns and 'quarter' in company_data.columns:
            company_data = company_data.sort_values(['year', 'quarter'])
        
        if len(company_data) < 2:
            continue
        
        # Analyze trends using correct column names
        ratio_trend = _calculate_trend(company_data, 'acquiredDisposedRatio')
        total_acquired_trend = _calculate_trend(company_data, 'totalAcquired')
        total_purchases_trend = _calculate_trend(company_data, 'totalPurchases')
        
        # Recent vs historical comparison
        if len(company_data) >= 4:
            recent_data = company_data.tail(2)
            historical_data = company_data.head(-2)
            
            recent_ratio = recent_data['acquiredDisposedRatio'].mean() if 'acquiredDisposedRatio' in recent_data.columns else 0
            historical_ratio = historical_data['acquiredDisposedRatio'].mean() if 'acquiredDisposedRatio' in historical_data.columns else 0
            
            ratio_change = ((recent_ratio - historical_ratio) / abs(historical_ratio)) * 100 if historical_ratio != 0 else 0
        else:
            ratio_change = 0
        
        # Activity intensity assessment
        latest_period = company_data.iloc[-1] if not company_data.empty else {}
        
        if 'totalPurchases' in latest_period:
            transaction_intensity = 'High' if latest_period['totalPurchases'] >= 15 else 'Moderate' if latest_period['totalPurchases'] >= 8 else 'Low'
        else:
            transaction_intensity = 'Unknown'
        
        insider_trends[company_name] = {
            'periods_analyzed': len(company_data),
            'acquired_disposed_ratio_trend': ratio_trend,
            'total_acquired_trend': total_acquired_trend,
            'total_purchases_trend': total_purchases_trend,
            'ratio_change_pct': ratio_change,
            'latest_ratio': latest_period.get('acquiredDisposedRatio', 0),
            'latest_total_acquired': latest_period.get('totalAcquired', 0),
            'latest_total_purchases': latest_period.get('totalPurchases', 0),
            'transaction_intensity': transaction_intensity,
            'trend_quality': _assess_trend_quality(ratio_trend, total_acquired_trend, total_purchases_trend)
        }
    
    return insider_trends


def _calculate_trend(data: pd.DataFrame, column: str) -> str:
    """Calculate trend direction for a column"""
    
    if column not in data.columns or len(data) < 2:
        return 'Insufficient Data'
    
    values = pd.to_numeric(data[column], errors='coerce').dropna()
    
    if len(values) < 2:
        return 'No Data'
    
    # Simple trend calculation
    first_half = values[:len(values)//2].mean()
    second_half = values[len(values)//2:].mean()
    
    if second_half > first_half * 1.1:
        return 'Increasing'
    elif second_half < first_half * 0.9:
        return 'Decreasing'
    else:
        return 'Stable'


def _assess_trend_quality(ratio_trend: str, acquired_trend: str, purchases_trend: str) -> str:
    """Assess overall trend quality"""
    
    positive_trends = [ratio_trend, acquired_trend, purchases_trend].count('Increasing')
    
    if positive_trends >= 2:
        return 'Positive'
    elif positive_trends == 1:
        return 'Mixed'
    else:
        return 'Negative'


def _analyze_insider_participation(insider_stats_df: pd.DataFrame, insider_latest_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze insider participation rates and activity intensity"""
    
    if insider_stats_df.empty and insider_latest_df.empty:
        return {}
    
    participation_analysis = {}
    
    for company_name in companies.keys():
        # Get data from both sources
        stats_data = insider_stats_df[insider_stats_df['Company'] == company_name] if not insider_stats_df.empty else pd.DataFrame()
        latest_data = insider_latest_df[insider_latest_df['Company'] == company_name] if not insider_latest_df.empty else pd.DataFrame()
        
        if stats_data.empty and latest_data.empty:
            continue
        
        # Calculate participation metrics
        if not latest_data.empty and 'reportingName' in latest_data.columns:
            active_insiders = latest_data['reportingName'].nunique()
            
            # Calculate transaction frequency (per month)
            if 'transactionDate' in latest_data.columns:
                latest_data['transactionDate'] = pd.to_datetime(latest_data['transactionDate'], errors='coerce')
                date_range = (latest_data['transactionDate'].max() - latest_data['transactionDate'].min()).days
                transaction_frequency = len(latest_data) / max(date_range / 30, 1) if date_range > 0 else 0
            else:
                transaction_frequency = 0
            
            # Average transaction size
            if 'securitiesTransacted' in latest_data.columns and 'price' in latest_data.columns:
                latest_data['transaction_value'] = (
                    pd.to_numeric(latest_data['securitiesTransacted'], errors='coerce') * 
                    pd.to_numeric(latest_data['price'], errors='coerce')
                )
                avg_transaction_size = latest_data['transaction_value'].mean()
            else:
                avg_transaction_size = 0
        else:
            active_insiders = 0
            transaction_frequency = 0
            avg_transaction_size = 0
        
        # Activity intensity assessment
        if transaction_frequency >= 2.0:
            activity_intensity = 'High'
        elif transaction_frequency >= 1.0:
            activity_intensity = 'Moderate'
        else:
            activity_intensity = 'Low'
        
        # Engagement level (based on active insider count and frequency)
        if active_insiders >= 15 and activity_intensity == 'High':
            engagement_level = 'Very High'
        elif active_insiders >= 10 or activity_intensity == 'High':
            engagement_level = 'High'
        elif active_insiders >= 5 or activity_intensity == 'Moderate':
            engagement_level = 'Moderate'
        else:
            engagement_level = 'Low'
        
        # Activity score calculation
        activity_score = min(10, (active_insiders * 0.4) + (transaction_frequency * 2) + (2 if activity_intensity == 'High' else 1 if activity_intensity == 'Moderate' else 0))
        
        participation_analysis[company_name] = {
            'active_insiders': active_insiders,
            'transaction_frequency': transaction_frequency,
            'avg_transaction_size': avg_transaction_size,
            'activity_intensity': activity_intensity,
            'engagement_level': engagement_level,
            'activity_score': activity_score
        }
    
    return participation_analysis

# =============================================================================
# SUBSECTION 14C.1: ROLE-BASED ACTIVITY ANALYSIS
# =============================================================================

def _build_role_based_activity_analysis(insider_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14C.1: Role-Based Activity Analysis"""
    
    if insider_df.empty:
        return build_info_box(
            "<p>No insider data available for role-based activity analysis.</p>",
            "warning",
            "14C.1 Role-Based Activity Analysis"
        )
    
    # Analyze role-based activity
    role_analysis = _analyze_role_based_activity(insider_df, companies)
    
    if not role_analysis:
        return build_info_box(
            "<p>Insufficient data for role-based activity analysis.</p>",
            "warning",
            "14C.1 Role-Based Activity Analysis"
        )
    
    # Create summary statistics
    total_companies = len(role_analysis)
    exec_dominance = sum(1 for r in role_analysis.values() if r['role_dominance'] == 'Executive')
    director_dominance = sum(1 for r in role_analysis.values() if r['role_dominance'] == 'Director')
    balanced_activity = sum(1 for r in role_analysis.values() if r['role_dominance'] == 'Balanced')
    aligned_leadership = sum(1 for r in role_analysis.values() if r['leadership_coordination'] == 'Aligned')
    bullish_executives = sum(1 for r in role_analysis.values() if r['executive_sentiment'] == 'Bullish')
    bullish_directors = sum(1 for r in role_analysis.values() if r['director_sentiment'] == 'Bullish')
    
    stat_cards = [
        {
            "label": "Aligned Leadership",
            "value": f"{aligned_leadership}/{total_companies}",
            "description": "Coordinated sentiment",
            "type": "success" if aligned_leadership >= total_companies * 0.6 else "info"
        },
        {
            "label": "Bullish Executives",
            "value": f"{bullish_executives}/{total_companies}",
            "description": "Executive optimism",
            "type": "success" if bullish_executives >= total_companies * 0.5 else "warning"
        },
        {
            "label": "Bullish Directors",
            "value": f"{bullish_directors}/{total_companies}",
            "description": "Board confidence",
            "type": "success" if bullish_directors >= total_companies * 0.5 else "warning"
        },
        {
            "label": "Balanced Activity",
            "value": f"{balanced_activity}/{total_companies}",
            "description": "Exec-Director balance",
            "type": "info"
        }
    ]
    
    # Create role analysis table
    table_data = []
    for company_name, analysis in role_analysis.items():
        total_transactions = analysis['executive_transactions'] + analysis['director_transactions']
        balance_score = 'Balanced' if abs(analysis['executive_transactions'] - analysis['director_transactions']) <= total_transactions * 0.3 else 'Imbalanced'
        
        table_data.append({
            'Company': company_name,
            'Exec Transactions': analysis['executive_transactions'],
            'Director Transactions': analysis['director_transactions'],
            'Exec Sentiment': analysis['executive_sentiment'],
            'Director Sentiment': analysis['director_sentiment'],
            'Leadership Coord.': analysis['leadership_coordination'],
            'Role Dominance': analysis['role_dominance'],
            'Activity Balance': balance_score
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "role-analysis-table")
    
    # Create charts
    companies_list = list(role_analysis.keys())
    
    # Chart 1: Executive vs Director Transactions
    exec_transactions = [role_analysis[comp]['executive_transactions'] for comp in companies_list]
    director_transactions = [role_analysis[comp]['director_transactions'] for comp in companies_list]
    
    chart1_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Executive',
                'x': companies_list,
                'y': exec_transactions,
                'marker': {'color': '#1e3a8a'},
                'hovertemplate': '<b>%{x}</b><br>Executive: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Director',
                'x': companies_list,
                'y': director_transactions,
                'marker': {'color': '#059669'},
                'hovertemplate': '<b>%{x}</b><br>Director: %{y}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Executive vs Director Transaction Activity',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Transaction Count'},
            'barmode': 'group',
            'hovermode': 'x unified'
        }
    }
    chart1_html = build_plotly_chart(chart1_data, "chart-14c1-exec-director-transactions")
    
    # Chart 2: Leadership Coordination Distribution
    coordination_counts = {'Aligned': 0, 'Divergent': 0, 'Mixed': 0}
    for analysis in role_analysis.values():
        coord = analysis['leadership_coordination']
        if coord in coordination_counts:
            coordination_counts[coord] += 1
    
    chart2_data = {
        'data': [{
            'type': 'pie',
            'labels': list(coordination_counts.keys()),
            'values': list(coordination_counts.values()),
            'marker': {'colors': ['#10b981', '#ef4444', '#f59e0b']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Leadership Coordination Analysis'
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14c1-coordination")
    
    # Chart 3: Executive vs Director Sentiment
    exec_sentiment_counts = {'Bullish': 0, 'Neutral': 0, 'Bearish': 0}
    director_sentiment_counts = {'Bullish': 0, 'Neutral': 0, 'Bearish': 0}
    
    for analysis in role_analysis.values():
        exec_sent = analysis['executive_sentiment']
        director_sent = analysis['director_sentiment']
        
        if exec_sent in exec_sentiment_counts:
            exec_sentiment_counts[exec_sent] += 1
        if director_sent in director_sentiment_counts:
            director_sentiment_counts[director_sent] += 1
    
    sentiment_labels = list(exec_sentiment_counts.keys())
    exec_values = list(exec_sentiment_counts.values())
    director_values = list(director_sentiment_counts.values())
    
    chart3_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Executive',
                'x': sentiment_labels,
                'y': exec_values,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Executive: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Director',
                'x': sentiment_labels,
                'y': director_values,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Director: %{y}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Executive vs Director Sentiment Distribution',
            'xaxis': {'title': 'Sentiment'},
            'yaxis': {'title': 'Company Count'},
            'barmode': 'group'
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14c1-sentiment-comparison")
    
    # Chart 4: Role Dominance Distribution
    dominance_counts = {'Executive': 0, 'Director': 0, 'Balanced': 0}
    for analysis in role_analysis.values():
        dominance = analysis['role_dominance']
        if dominance in dominance_counts:
            dominance_counts[dominance] += 1
    
    chart4_data = {
        'data': [{
            'type': 'pie',
            'labels': list(dominance_counts.keys()),
            'values': list(dominance_counts.values()),
            'marker': {'colors': ['#1e3a8a', '#059669', '#8b5cf6']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Role Dominance Distribution'
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14c1-dominance")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Role Activity Distribution:</strong> {exec_dominance} executive-dominated, {director_dominance} director-dominated, 
    and {balanced_activity} balanced activity patterns across {total_companies} companies.</p>
    
    <p><strong>Leadership Coordination:</strong> {aligned_leadership}/{total_companies} companies show aligned executive-director sentiment, 
    indicating {'strong leadership consensus' if aligned_leadership >= total_companies * 0.6 else 'moderate coordination' if aligned_leadership >= total_companies * 0.4 else 'mixed leadership signals'}.</p>
    
    <p><strong>Sentiment Analysis:</strong> {bullish_executives}/{total_companies} companies have bullish executive sentiment, 
    while {bullish_directors}/{total_companies} show bullish director sentiment, suggesting 
    {'high confidence across leadership' if (bullish_executives + bullish_directors) >= total_companies else 'moderate leadership confidence' if (bullish_executives + bullish_directors) >= total_companies * 0.6 else 'cautious leadership positioning'}.</p>
    
    <p><strong>Strategic Role Intelligence:</strong> The portfolio exhibits 
    {'excellent leadership consensus' if aligned_leadership >= total_companies * 0.5 and (bullish_executives + bullish_directors) >= total_companies else 'good leadership coordination' if aligned_leadership >= total_companies * 0.3 else 'mixed leadership sentiment'}, 
    providing valuable governance and confidence indicators for investment analysis.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14c1"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14C.1 Executive vs Director Activity & Role-Based Analysis</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Role-Based Activity Analysis</h4>
            {table_html}
            
            <h4>Role Activity Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 14C.2: GOVERNANCE PATTERNS ANALYSIS
# =============================================================================

def _build_governance_patterns_analysis(insider_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14C.2: Governance Patterns Analysis"""
    
    if insider_df.empty:
        return ""
    
    # First get role analysis
    role_analysis = _analyze_role_based_activity(insider_df, companies)
    
    if not role_analysis:
        return ""
    
    # Analyze governance patterns
    governance_insights = _analyze_governance_patterns(insider_df, role_analysis, companies)
    
    if not governance_insights:
        return build_info_box(
            "<p>Insufficient data for governance pattern analysis.</p>",
            "warning",
            "14C.2 Governance Patterns Analysis"
        )
    
    # Create summary statistics
    total_companies = len(governance_insights)
    excellent_governance = sum(1 for g in governance_insights.values() if g['governance_quality'] == 'Excellent')
    strong_alignment = sum(1 for g in governance_insights.values() if g['leadership_alignment'] == 'Strong Positive')
    well_balanced = sum(1 for g in governance_insights.values() if g['transaction_coordination'] == 'Well Balanced')
    avg_leadership_score = np.mean([g['leadership_score'] for g in governance_insights.values()])
    
    stat_cards = [
        {
            "label": "Excellent Governance",
            "value": f"{excellent_governance}/{total_companies}",
            "description": f"{(excellent_governance/total_companies*100):.0f}% of companies",
            "type": "success" if excellent_governance >= total_companies * 0.5 else "info"
        },
        {
            "label": "Strong Alignment",
            "value": f"{strong_alignment}/{total_companies}",
            "description": "Leadership alignment",
            "type": "success" if strong_alignment >= total_companies * 0.4 else "warning"
        },
        {
            "label": "Well Balanced",
            "value": f"{well_balanced}/{total_companies}",
            "description": "Transaction coordination",
            "type": "success" if well_balanced >= total_companies * 0.5 else "info"
        },
        {
            "label": "Avg Leadership Score",
            "value": f"{avg_leadership_score:.1f}/10",
            "description": "Portfolio average",
            "type": "success" if avg_leadership_score >= 7 else "info" if avg_leadership_score >= 5 else "warning"
        }
    ]
    
    # Create governance analysis table
    table_data = []
    for company_name, analysis in governance_insights.items():
        table_data.append({
            'Company': company_name,
            'Exec Activity': analysis['executive_activity_level'],
            'Director Activity': analysis['director_activity_level'],
            'Leadership Alignment': analysis['leadership_alignment'],
            'Governance Quality': analysis['governance_quality'],
            'Transaction Coord.': analysis['transaction_coordination'],
            'Leadership Score': f"{analysis['leadership_score']:.1f}/10"
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "governance-analysis-table")
    
    # Create charts
    companies_list = list(governance_insights.keys())
    
    # Chart 1: Leadership Scores
    leadership_scores = [governance_insights[comp]['leadership_score'] for comp in companies_list]
    score_colors = ['#10b981' if s >= 7 else '#f59e0b' if s >= 5 else '#ef4444' for s in leadership_scores]
    
    chart1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': leadership_scores,
            'marker': {'color': score_colors},
            'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': 'Leadership Quality Scores',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Leadership Score (0-10)', 'range': [0, 10]}
        }
    }
    chart1_html = build_plotly_chart(chart1_data, "chart-14c2-leadership-scores")
    
    # Chart 2: Governance Quality Distribution
    quality_counts = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Weak': 0}
    for analysis in governance_insights.values():
        quality = analysis['governance_quality']
        if quality in quality_counts:
            quality_counts[quality] += 1
    
    # Filter out zeros
    quality_counts = {k: v for k, v in quality_counts.items() if v > 0}
    
    chart2_data = {
        'data': [{
            'type': 'pie',
            'labels': list(quality_counts.keys()),
            'values': list(quality_counts.values()),
            'marker': {'colors': ['#059669', '#10b981', '#f59e0b', '#ef4444'][:len(quality_counts)]},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Governance Quality Distribution'
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14c2-governance-quality")
    
    # Chart 3: Leadership Alignment Distribution
    alignment_counts = {'Strong Positive': 0, 'Coordinated': 0, 'Conflicted': 0, 'Unclear': 0}
    for analysis in governance_insights.values():
        alignment = analysis['leadership_alignment']
        if alignment in alignment_counts:
            alignment_counts[alignment] += 1
    
    # Filter out zeros
    alignment_counts = {k: v for k, v in alignment_counts.items() if v > 0}
    
    chart3_data = {
        'data': [{
            'type': 'pie',
            'labels': list(alignment_counts.keys()),
            'values': list(alignment_counts.values()),
            'marker': {'colors': ['#059669', '#10b981', '#ef4444', '#94a3b8'][:len(alignment_counts)]},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Leadership Alignment Distribution'
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14c2-alignment")
    
    # Chart 4: Transaction Coordination Distribution
    coordination_counts = {'Well Balanced': 0, 'Moderately Balanced': 0, 'Imbalanced': 0}
    for analysis in governance_insights.values():
        coord = analysis['transaction_coordination']
        if coord in coordination_counts:
            coordination_counts[coord] += 1
    
    chart4_data = {
        'data': [{
            'type': 'pie',
            'labels': list(coordination_counts.keys()),
            'values': list(coordination_counts.values()),
            'marker': {'colors': ['#10b981', '#f59e0b', '#ef4444']},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Transaction Coordination Distribution'
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14c2-coordination")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Corporate Governance Quality:</strong> {excellent_governance}/{total_companies} companies demonstrate excellent governance 
    indicators from insider activity analysis, with an average leadership score of {avg_leadership_score:.1f}/10.</p>
    
    <p><strong>Leadership Alignment:</strong> {strong_alignment}/{total_companies} companies show strong positive leadership coordination, 
    indicating {'excellent governance standards' if strong_alignment >= total_companies * 0.4 else 'good governance indicators' if strong_alignment >= total_companies * 0.2 else 'developing governance patterns'}.</p>
    
    <p><strong>Transaction Coordination:</strong> {well_balanced}/{total_companies} companies exhibit well-balanced executive-director activity, 
    suggesting {'superior transaction coordination' if well_balanced >= total_companies * 0.5 else 'moderate coordination' if well_balanced >= total_companies * 0.3 else 'variable coordination patterns'}.</p>
    
    <p><strong>Strategic Governance Intelligence:</strong> The portfolio demonstrates 
    {'excellent governance and coordination' if avg_leadership_score >= 7 and excellent_governance >= total_companies * 0.4 else 'strong governance foundation' if avg_leadership_score >= 5 else 'developing governance excellence'}, 
    enhancing overall portfolio quality assessment and investment confidence.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14c2"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14C.2 Leadership Transaction Patterns & Corporate Governance Analysis</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Governance Pattern Analysis</h4>
            {table_html}
            
            <h4>Governance Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 14D: INSIDER SENTIMENT SCORING
# =============================================================================

def _build_insider_sentiment_scoring(insider_latest_df: pd.DataFrame, insider_stats_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14D: Insider Sentiment Scoring"""
    
    if insider_latest_df.empty:
        return build_info_box(
            "<p>No insider data available for sentiment scoring.</p>",
            "warning",
            "14D Insider Sentiment Scoring"
        )
    
    # Get prerequisite analyses
    transaction_patterns = _analyze_transaction_patterns(insider_latest_df, companies)
    timing_analysis = _analyze_timing_clusters(insider_latest_df, companies)
    role_analysis = _analyze_role_based_activity(insider_latest_df, companies)
    
    # Generate sentiment scoring
    sentiment_scoring = _generate_insider_sentiment_scoring(
        insider_latest_df, insider_stats_df, transaction_patterns,
        timing_analysis, role_analysis, companies
    )
    
    if not sentiment_scoring:
        return build_info_box(
            "<p>Insufficient data for insider sentiment scoring.</p>",
            "warning",
            "14D Insider Sentiment Scoring"
        )
    
    # Create summary statistics
    total_companies = len(sentiment_scoring)
    avg_sentiment_score = np.mean([s['overall_sentiment_score'] for s in sentiment_scoring.values()])
    avg_confidence = np.mean([s['confidence_level'] for s in sentiment_scoring.values()])
    avg_leadership_confidence = np.mean([s['leadership_confidence'] for s in sentiment_scoring.values()])
    
    strong_buy_signals = sum(1 for s in sentiment_scoring.values() if s['investment_signal'] == 'Strong Buy')
    buy_signals = sum(1 for s in sentiment_scoring.values() if s['investment_signal'] == 'Buy')
    bullish_sentiment = sum(1 for s in sentiment_scoring.values() if s['market_sentiment'] in ['Bullish', 'Very Bullish'])
    
    avg_buy_sell_ratio = np.mean([s['buy_sell_ratio'] for s in sentiment_scoring.values()])
    
    stat_cards = [
        {
            "label": "Avg Sentiment Score",
            "value": f"{avg_sentiment_score:.1f}/10",
            "description": "Portfolio sentiment",
            "type": "success" if avg_sentiment_score >= 7 else "info" if avg_sentiment_score >= 5 else "warning"
        },
        {
            "label": "Signal Confidence",
            "value": f"{avg_confidence:.0f}%",
            "description": "Average confidence",
            "type": "success" if avg_confidence >= 80 else "info" if avg_confidence >= 70 else "warning"
        },
        {
            "label": "Investment Signals",
            "value": f"{strong_buy_signals + buy_signals}/{total_companies}",
            "description": f"{strong_buy_signals} Strong Buy, {buy_signals} Buy",
            "type": "success" if (strong_buy_signals + buy_signals) >= total_companies * 0.4 else "info"
        },
        {
            "label": "Bullish Sentiment",
            "value": f"{bullish_sentiment}/{total_companies}",
            "description": f"{(bullish_sentiment/total_companies*100):.0f}% of companies",
            "type": "success" if bullish_sentiment >= total_companies * 0.5 else "warning"
        },
        {
            "label": "Avg Buy/Sell Ratio",
            "value": f"{avg_buy_sell_ratio:.2f}",
            "description": "Portfolio average",
            "type": "success" if avg_buy_sell_ratio >= 1.5 else "info" if avg_buy_sell_ratio >= 1.0 else "danger"
        }
    ]
    
    # Create sentiment scoring table
    table_data = []
    for company_name, scoring in sentiment_scoring.items():
        table_data.append({
            'Company': company_name,
            'Buy/Sell Ratio': f"{scoring['buy_sell_ratio']:.2f}",
            'Transaction Sentiment': scoring['transaction_sentiment'],
            'Timing Score': f"{scoring['timing_score']:.1f}/10",
            'Leadership Conf.': f"{scoring['leadership_confidence']:.1f}/10",
            'Market Sentiment': scoring['market_sentiment'],
            'Overall Score': f"{scoring['overall_sentiment_score']:.1f}/10",
            'Confidence': f"{scoring['confidence_level']:.0f}%",
            'Investment Signal': scoring['investment_signal']
        })
    
    table_df = pd.DataFrame(table_data)
    table_html = build_data_table(table_df, "sentiment-scoring-table")
    
    # Create charts
    companies_list = list(sentiment_scoring.keys())
    
    # Chart 1: Overall Sentiment Scores with Confidence Annotations
    sentiment_scores = [sentiment_scoring[comp]['overall_sentiment_score'] for comp in companies_list]
    confidence_levels = [sentiment_scoring[comp]['confidence_level'] for comp in companies_list]
    score_colors = ['#10b981' if s >= 7 else '#f59e0b' if s >= 5 else '#ef4444' for s in sentiment_scores]
    
    chart1_data = {
        'data': [{
            'type': 'bar',
            'x': companies_list,
            'y': sentiment_scores,
            'marker': {'color': score_colors},
            'text': [f"{conf:.0f}%" for conf in confidence_levels],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}/10<br>Confidence: %{text}<extra></extra>'
        }],
        'layout': {
            'title': 'Insider Sentiment Scores (with Confidence %)',
            'xaxis': {'title': 'Company'},
            'yaxis': {'title': 'Sentiment Score (0-10)', 'range': [0, 11]}
        }
    }
    chart1_html = build_plotly_chart(chart1_data, "chart-14d-sentiment-scores")
    
    # Chart 2: Investment Signals Distribution
    signal_counts = {'Strong Buy': 0, 'Buy': 0, 'Hold': 0, 'Watch': 0, 'Caution': 0}
    for scoring in sentiment_scoring.values():
        signal = scoring['investment_signal']
        if signal in signal_counts:
            signal_counts[signal] += 1
    
    # Filter out zeros
    signal_counts = {k: v for k, v in signal_counts.items() if v > 0}
    
    chart2_data = {
        'data': [{
            'type': 'pie',
            'labels': list(signal_counts.keys()),
            'values': list(signal_counts.values()),
            'marker': {'colors': ['#059669', '#10b981', '#f59e0b', '#f97316', '#ef4444'][:len(signal_counts)]},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Investment Signal Distribution'
        }
    }
    chart2_html = build_plotly_chart(chart2_data, "chart-14d-signals")
    
    # Chart 3: Leadership Confidence vs Buy/Sell Ratio (Scatter)
    leadership_confidence = [sentiment_scoring[comp]['leadership_confidence'] for comp in companies_list]
    buy_sell_ratios = [sentiment_scoring[comp]['buy_sell_ratio'] for comp in companies_list]
    
    chart3_data = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': leadership_confidence,
            'y': buy_sell_ratios,
            'text': [comp[:8] for comp in companies_list],
            'textposition': 'top center',
            'marker': {
                'size': 12,
                'color': score_colors,
                'line': {'width': 2, 'color': 'white'}
            },
            'hovertemplate': '<b>%{text}</b><br>Leadership: %{x:.1f}/10<br>Buy/Sell: %{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': 'Leadership Confidence vs Buy/Sell Activity',
            'xaxis': {'title': 'Leadership Confidence (0-10)', 'range': [0, 10]},
            'yaxis': {'title': 'Buy/Sell Ratio'},
            'shapes': [{
                'type': 'line',
                'x0': 0,
                'x1': 10,
                'y0': 1.0,
                'y1': 1.0,
                'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
            }],
            'annotations': [{
                'x': 9,
                'y': 1.0,
                'text': 'Neutral (1.0)',
                'showarrow': False,
                'yshift': 10
            }]
        }
    }
    chart3_html = build_plotly_chart(chart3_data, "chart-14d-confidence-scatter", height=600)
    
    # Chart 4: Market Sentiment Distribution
    market_sentiment_counts = {'Very Bullish': 0, 'Bullish': 0, 'Positive': 0, 'Neutral': 0, 'Cautious': 0, 'Bearish': 0}
    for scoring in sentiment_scoring.values():
        sentiment = scoring['market_sentiment']
        if sentiment in market_sentiment_counts:
            market_sentiment_counts[sentiment] += 1
    
    # Filter out zeros
    market_sentiment_counts = {k: v for k, v in market_sentiment_counts.items() if v > 0}
    
    chart4_data = {
        'data': [{
            'type': 'pie',
            'labels': list(market_sentiment_counts.keys()),
            'values': list(market_sentiment_counts.values()),
            'marker': {'colors': ['#059669', '#10b981', '#86efac', '#fbbf24', '#f97316', '#ef4444'][:len(market_sentiment_counts)]},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        }],
        'layout': {
            'title': 'Market Sentiment Distribution'
        }
    }
    chart4_html = build_plotly_chart(chart4_data, "chart-14d-market-sentiment")
    
    # Generate summary narrative
    summary = f"""
    <p><strong>Portfolio Sentiment Assessment:</strong> Average sentiment score of {avg_sentiment_score:.1f}/10 across {total_companies} companies, 
    with {avg_confidence:.0f}% average confidence level. {bullish_sentiment}/{total_companies} companies exhibit bullish or very bullish market sentiment.</p>
    
    <p><strong>Investment Signal Intelligence:</strong> {strong_buy_signals} Strong Buy and {buy_signals} Buy signals generated from insider sentiment analysis, 
    representing {((strong_buy_signals + buy_signals)/total_companies*100):.0f}% of the portfolio with positive investment signals.</p>
    
    <p><strong>Buy/Sell Activity Analysis:</strong> Average buy/sell ratio of {avg_buy_sell_ratio:.2f} indicates 
    {'strong buying pressure' if avg_buy_sell_ratio >= 1.5 else 'moderate buying activity' if avg_buy_sell_ratio >= 1.0 else 'selling pressure'}. 
    Leadership confidence averages {avg_leadership_confidence:.1f}/10 across companies.</p>
    
    <p><strong>Strategic Sentiment Intelligence:</strong> The portfolio demonstrates 
    {'strong positive insider sentiment' if (strong_buy_signals + buy_signals) >= total_companies * 0.4 and avg_sentiment_score >= 6.5 else 'moderate positive signals' if avg_sentiment_score >= 5.5 else 'mixed insider sentiment'}, 
    providing valuable market confidence indicators for portfolio optimization and investment decision-making.</p>
    """
    
    # Build collapsible subsection
    subsection_id = "subsection-14d"
    html = f"""
    <div class="info-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">14D. Insider Sentiment Scoring & Confidence Indicators</h3>
            <button onclick="toggleSubsection('{subsection_id}')" 
                    style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; 
                           padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                ▼ Collapse/Expand
            </button>
        </div>
        
        <div id="{subsection_id}" class="subsection-content">
            {build_stat_grid(stat_cards)}
            
            <h4>Insider Sentiment Scoring Analysis</h4>
            {table_html}
            
            <h4>Sentiment Scoring Visualizations</h4>
            {chart1_html}
            {chart2_html}
            {chart3_html}
            {chart4_html}
            
            <h4>Summary Analysis</h4>
            {summary}
        </div>
    </div>
    """
    
    return html


# =============================================================================
# ANALYSIS HELPER FUNCTIONS FOR PHASE 3
# =============================================================================

def _analyze_role_based_activity(insider_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze executive vs director activity patterns"""
    
    if insider_df.empty:
        return {}
    
    role_analysis = {}
    
    for company_name in companies.keys():
        company_data = insider_df[insider_df['Company'] == company_name].copy()
        
        if company_data.empty:
            continue
        
        # Calculate transaction values first
        if 'securitiesTransacted' in company_data.columns and 'price' in company_data.columns:
            company_data['transaction_value'] = (
                pd.to_numeric(company_data['securitiesTransacted'], errors='coerce') * 
                pd.to_numeric(company_data['price'], errors='coerce')
            )
        else:
            company_data['transaction_value'] = 0
        
        # Categorize by role using typeOfOwner column
        if 'typeOfOwner' in company_data.columns:
            executives = company_data[company_data['typeOfOwner'].str.contains('Officer|CEO|CFO|COO|CTO|Executive|President', case=False, na=False)]
            directors = company_data[company_data['typeOfOwner'].str.contains('Director|Board', case=False, na=False)]
            other_insiders = company_data[~company_data.index.isin(executives.index.union(directors.index))]
        else:
            # Fallback: split roughly equally
            mid_point = len(company_data) // 2
            executives = company_data.iloc[:mid_point]
            directors = company_data.iloc[mid_point:]
            other_insiders = pd.DataFrame()
        
        # Analyze transactions by role
        exec_transactions = len(executives)
        director_transactions = len(directors)
        other_transactions = len(other_insiders)
        
        # Buy/sell analysis by role
        if 'acquisitionOrDisposition' in company_data.columns:
            exec_buys = len(executives[executives['acquisitionOrDisposition'] == 'A'])
            exec_sells = len(executives[executives['acquisitionOrDisposition'] == 'D'])
            
            director_buys = len(directors[directors['acquisitionOrDisposition'] == 'A'])
            director_sells = len(directors[directors['acquisitionOrDisposition'] == 'D'])
        else:
            exec_buys = exec_transactions // 2
            exec_sells = exec_transactions - exec_buys
            director_buys = director_transactions // 2
            director_sells = director_transactions - director_buys
        
        # Value analysis
        exec_value = executives['transaction_value'].sum() if not executives.empty and 'transaction_value' in executives.columns else 0
        director_value = directors['transaction_value'].sum() if not directors.empty and 'transaction_value' in directors.columns else 0
        
        # Role-based sentiment
        exec_sentiment = 'Bullish' if exec_buys > exec_sells * 1.5 else 'Bearish' if exec_sells > exec_buys * 1.5 else 'Neutral'
        director_sentiment = 'Bullish' if director_buys > director_sells * 1.5 else 'Bearish' if director_sells > director_buys * 1.5 else 'Neutral'
        
        # Leadership coordination
        if exec_sentiment == director_sentiment and exec_sentiment != 'Neutral':
            coordination = 'Aligned'
        elif exec_sentiment != 'Neutral' and director_sentiment != 'Neutral':
            coordination = 'Divergent'
        else:
            coordination = 'Mixed'
        
        role_analysis[company_name] = {
            'executive_transactions': exec_transactions,
            'director_transactions': director_transactions,
            'other_transactions': other_transactions,
            'executive_buys': exec_buys,
            'executive_sells': exec_sells,
            'director_buys': director_buys,
            'director_sells': director_sells,
            'executive_value': exec_value,
            'director_value': director_value,
            'executive_sentiment': exec_sentiment,
            'director_sentiment': director_sentiment,
            'leadership_coordination': coordination,
            'role_dominance': 'Executive' if exec_transactions > director_transactions else 'Director' if director_transactions > exec_transactions else 'Balanced'
        }
    
    return role_analysis


def _analyze_governance_patterns(insider_df: pd.DataFrame, role_analysis: Dict[str, Dict], companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze corporate governance patterns from insider activity"""
    
    if not role_analysis:
        return {}
    
    governance_insights = {}
    
    for company_name in companies.keys():
        if company_name not in role_analysis:
            continue
        
        role_data = role_analysis[company_name]
        
        # Assess executive activity level
        exec_transactions = role_data['executive_transactions']
        exec_activity_level = 'High' if exec_transactions >= 15 else 'Moderate' if exec_transactions >= 8 else 'Low'
        
        # Assess director activity level
        director_transactions = role_data['director_transactions']
        director_activity_level = 'High' if director_transactions >= 10 else 'Moderate' if director_transactions >= 5 else 'Low'
        
        # Leadership alignment assessment
        coordination = role_data['leadership_coordination']
        exec_sentiment = role_data['executive_sentiment']
        director_sentiment = role_data['director_sentiment']
        
        if coordination == 'Aligned' and exec_sentiment == 'Bullish':
            leadership_alignment = 'Strong Positive'
        elif coordination == 'Aligned':
            leadership_alignment = 'Coordinated'
        elif coordination == 'Divergent':
            leadership_alignment = 'Conflicted'
        else:
            leadership_alignment = 'Unclear'
        
        # Governance quality assessment
        quality_factors = []
        if coordination == 'Aligned':
            quality_factors.append(2)
        if exec_activity_level != 'Low' and director_activity_level != 'Low':
            quality_factors.append(2)
        if exec_sentiment == 'Bullish' or director_sentiment == 'Bullish':
            quality_factors.append(1)
        
        governance_score = sum(quality_factors)
        
        if governance_score >= 4:
            governance_quality = 'Excellent'
        elif governance_score >= 3:
            governance_quality = 'Good'
        elif governance_score >= 2:
            governance_quality = 'Fair'
        else:
            governance_quality = 'Weak'
        
        # Transaction coordination assessment
        total_exec = exec_transactions
        total_director = director_transactions
        total_transactions = total_exec + total_director
        
        if total_transactions > 0:
            balance_ratio = min(total_exec, total_director) / max(total_exec, total_director) if max(total_exec, total_director) > 0 else 0
            
            if balance_ratio >= 0.7:
                transaction_coordination = 'Well Balanced'
            elif balance_ratio >= 0.4:
                transaction_coordination = 'Moderately Balanced'
            else:
                transaction_coordination = 'Imbalanced'
        else:
            transaction_coordination = 'No Activity'
            balance_ratio = 0
        
        # Leadership score calculation
        leadership_score = min(10, governance_score * 2 + (1 if balance_ratio >= 0.5 else 0) + (1 if total_transactions >= 10 else 0))
        
        governance_insights[company_name] = {
            'executive_activity_level': exec_activity_level,
            'director_activity_level': director_activity_level,
            'leadership_alignment': leadership_alignment,
            'governance_quality': governance_quality,
            'transaction_coordination': transaction_coordination,
            'governance_score': governance_score,
            'leadership_score': leadership_score
        }
    
    return governance_insights


def _generate_insider_sentiment_scoring(insider_latest_df: pd.DataFrame, insider_stats_df: pd.DataFrame,
                                       transaction_patterns: Dict, timing_analysis: Dict, role_analysis: Dict,
                                       companies: Dict[str, str]) -> Dict[str, Dict]:
    """Generate comprehensive insider sentiment scoring"""
    
    sentiment_scoring = {}
    
    for company_name in companies.keys():
        # Initialize scoring components
        buy_sell_ratio = 1.0
        transaction_sentiment = 'Neutral'
        timing_score = 5.0
        leadership_confidence = 5.0
        market_sentiment = 'Neutral'
        
        # Get transaction patterns data
        if company_name in transaction_patterns:
            trans_data = transaction_patterns[company_name]
            buy_sell_ratio = trans_data['buy_sell_ratio']
            transaction_sentiment = trans_data['transaction_sentiment']
        
        # Get timing analysis data
        if company_name in timing_analysis:
            timing_data = timing_analysis[company_name]
            timing_score = timing_data['timing_score']
        
        # Get role analysis data
        if company_name in role_analysis:
            role_data = role_analysis[company_name]
            
            # Calculate leadership confidence
            exec_sentiment = role_data['executive_sentiment']
            director_sentiment = role_data['director_sentiment']
            coordination = role_data['leadership_coordination']
            
            confidence_components = []
            
            # Executive sentiment component
            if exec_sentiment == 'Bullish':
                confidence_components.append(8)
            elif exec_sentiment == 'Neutral':
                confidence_components.append(5)
            else:
                confidence_components.append(2)
            
            # Director sentiment component
            if director_sentiment == 'Bullish':
                confidence_components.append(8)
            elif director_sentiment == 'Neutral':
                confidence_components.append(5)
            else:
                confidence_components.append(2)
            
            # Coordination bonus
            if coordination == 'Aligned':
                confidence_components.append(7)
            elif coordination == 'Mixed':
                confidence_components.append(5)
            else:
                confidence_components.append(3)
            
            leadership_confidence = np.mean(confidence_components)
        
        # Calculate overall sentiment score
        sentiment_components = [
            min(10, buy_sell_ratio * 3),  # Buy/sell ratio component (0-10)
            timing_score,  # Timing quality component (0-10)
            leadership_confidence,  # Leadership confidence component (0-10)
            8 if transaction_sentiment == 'Bullish' else 5 if transaction_sentiment == 'Positive' else 3 if transaction_sentiment == 'Neutral' else 1
        ]
        
        overall_sentiment_score = np.mean(sentiment_components)
        
        # Market sentiment assessment
        if overall_sentiment_score >= 7.5:
            market_sentiment = 'Very Bullish'
        elif overall_sentiment_score >= 6.5:
            market_sentiment = 'Bullish'
        elif overall_sentiment_score >= 5.5:
            market_sentiment = 'Positive'
        elif overall_sentiment_score >= 4.5:
            market_sentiment = 'Neutral'
        elif overall_sentiment_score >= 3.5:
            market_sentiment = 'Cautious'
        else:
            market_sentiment = 'Bearish'
        
        # Confidence level calculation
        data_quality_factors = []
        
        if company_name in transaction_patterns and transaction_patterns[company_name]['total_transactions'] >= 10:
            data_quality_factors.append(20)
        elif company_name in transaction_patterns and transaction_patterns[company_name]['total_transactions'] >= 5:
            data_quality_factors.append(15)
        else:
            data_quality_factors.append(10)
        
        if company_name in timing_analysis and timing_analysis[company_name]['timing_score'] >= 6:
            data_quality_factors.append(15)
        else:
            data_quality_factors.append(10)
        
        if company_name in role_analysis:
            total_role_transactions = role_analysis[company_name]['executive_transactions'] + role_analysis[company_name]['director_transactions']
            if total_role_transactions >= 15:
                data_quality_factors.append(20)
            elif total_role_transactions >= 8:
                data_quality_factors.append(15)
            else:
                data_quality_factors.append(10)
        else:
            data_quality_factors.append(5)
        
        confidence_level = min(95, sum(data_quality_factors) + 25)
        
        # Investment signal generation
        if overall_sentiment_score >= 7.5 and confidence_level >= 80:
            investment_signal = 'Strong Buy'
        elif overall_sentiment_score >= 6.5 and confidence_level >= 70:
            investment_signal = 'Buy'
        elif overall_sentiment_score >= 5.5:
            investment_signal = 'Hold'
        elif overall_sentiment_score >= 4.0:
            investment_signal = 'Watch'
        else:
            investment_signal = 'Caution'
        
        sentiment_scoring[company_name] = {
            'buy_sell_ratio': buy_sell_ratio,
            'transaction_sentiment': transaction_sentiment,
            'timing_score': timing_score,
            'leadership_confidence': leadership_confidence,
            'market_sentiment': market_sentiment,
            'overall_sentiment_score': overall_sentiment_score,
            'confidence_level': confidence_level,
            'investment_signal': investment_signal
        }
    
    return sentiment_scoring

def _build_visualization_dashboard(insider_latest_df: pd.DataFrame, insider_stats_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14E: Visualization Dashboard (STUB)"""
    return ""

def _build_strategic_insights(insider_latest_df: pd.DataFrame, insider_stats_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 14F: Strategic Insights (STUB)"""
    return ""


# =============================================================================
# ANALYSIS HELPER FUNCTIONS
# =============================================================================

def _analyze_transaction_patterns(insider_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze recent insider transaction patterns"""
    
    if insider_df.empty:
        return {}
    
    transaction_patterns = {}
    
    for company_name in companies.keys():
        company_data = insider_df[insider_df['Company'] == company_name].copy()
        
        if company_data.empty:
            continue
        
        # Convert transaction dates
        if 'transactionDate' in company_data.columns:
            company_data['transactionDate'] = pd.to_datetime(company_data['transactionDate'], errors='coerce')
            company_data = company_data.dropna(subset=['transactionDate'])
        
        if company_data.empty:
            continue
        
        # Calculate transaction values
        if 'securitiesTransacted' in company_data.columns and 'price' in company_data.columns:
            company_data['transaction_value'] = (
                pd.to_numeric(company_data['securitiesTransacted'], errors='coerce') * 
                pd.to_numeric(company_data['price'], errors='coerce')
            )
        else:
            company_data['transaction_value'] = 0
        
        # Analyze buy/sell patterns
        if 'acquisitionOrDisposition' in company_data.columns:
            buy_transactions = company_data[company_data['acquisitionOrDisposition'] == 'A']
            sell_transactions = company_data[company_data['acquisitionOrDisposition'] == 'D']
        else:
            buy_transactions = pd.DataFrame()
            sell_transactions = pd.DataFrame()
        
        # Calculate metrics
        total_transactions = len(company_data)
        buy_count = len(buy_transactions)
        sell_count = len(sell_transactions)
        
        total_buy_value = buy_transactions['transaction_value'].sum() if not buy_transactions.empty else 0
        total_sell_value = sell_transactions['transaction_value'].sum() if not sell_transactions.empty else 0
        
        # Recent activity (last 90 days)
        recent_date = datetime.now() - timedelta(days=90)
        recent_transactions = company_data[company_data['transactionDate'] >= recent_date]
        
        # Calculate ratios and sentiment
        if total_transactions > 0:
            buy_sell_ratio = buy_count / max(sell_count, 1)
            activity_intensity = 'High' if total_transactions >= 20 else 'Moderate' if total_transactions >= 10 else 'Low'
            
            if buy_sell_ratio >= 2.0:
                transaction_sentiment = 'Bullish'
            elif buy_sell_ratio >= 1.0:
                transaction_sentiment = 'Positive'
            elif buy_sell_ratio >= 0.5:
                transaction_sentiment = 'Neutral'
            else:
                transaction_sentiment = 'Bearish'
        else:
            buy_sell_ratio = 0
            activity_intensity = 'None'
            transaction_sentiment = 'No Activity'
        
        transaction_patterns[company_name] = {
            'total_transactions': total_transactions,
            'buy_transactions': buy_count,
            'sell_transactions': sell_count,
            'buy_sell_ratio': buy_sell_ratio,
            'total_buy_value': total_buy_value,
            'total_sell_value': total_sell_value,
            'recent_transactions_90d': len(recent_transactions),
            'activity_intensity': activity_intensity,
            'transaction_sentiment': transaction_sentiment,
            'avg_transaction_size': company_data['transaction_value'].mean() if 'transaction_value' in company_data.columns else 0
        }
    
    return transaction_patterns


def _analyze_timing_clusters(insider_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze transaction timing clusters and unusual activity"""
    
    if insider_df.empty:
        return {}
    
    timing_analysis = {}
    
    for company_name in companies.keys():
        company_data = insider_df[insider_df['Company'] == company_name].copy()
        
        if company_data.empty:
            continue
        
        # Convert transaction dates
        if 'transactionDate' in company_data.columns:
            company_data['transactionDate'] = pd.to_datetime(company_data['transactionDate'], errors='coerce')
            company_data = company_data.dropna(subset=['transactionDate'])
        
        if len(company_data) < 3:
            continue
        
        # Analyze timing patterns
        company_data['month'] = company_data['transactionDate'].dt.month
        company_data['quarter'] = company_data['transactionDate'].dt.quarter
        
        # Transaction clustering
        monthly_counts = company_data['month'].value_counts()
        quarterly_counts = company_data['quarter'].value_counts()
        
        # Unusual activity detection
        if 'securitiesTransacted' in company_data.columns:
            company_data['shares'] = pd.to_numeric(company_data['securitiesTransacted'], errors='coerce')
            large_transactions = company_data[company_data['shares'] > company_data['shares'].quantile(0.75)]
        else:
            large_transactions = pd.DataFrame()
        
        # Recent clustering (last 6 months)
        recent_date = datetime.now() - timedelta(days=180)
        recent_data = company_data[company_data['transactionDate'] >= recent_date]
        
        # Timing quality assessment
        if len(company_data) >= 5:
            monthly_concentration = monthly_counts.max() / len(company_data)
            
            timing_quality = 'Clustered' if monthly_concentration > 0.4 else 'Distributed' if monthly_concentration < 0.25 else 'Moderate'
            
            # Unusual activity flags
            unusual_flags = []
            if len(large_transactions) >= len(company_data) * 0.3:
                unusual_flags.append('Large Transaction Cluster')
            if len(recent_data) >= len(company_data) * 0.5:
                unusual_flags.append('Recent Activity Surge')
            
            unusual_activity = '; '.join(unusual_flags) if unusual_flags else 'None Detected'
        else:
            timing_quality = 'Limited Data'
            unusual_activity = 'Insufficient Data'
            monthly_concentration = 0
        
        timing_analysis[company_name] = {
            'total_transactions': len(company_data),
            'timing_distribution': timing_quality,
            'peak_month': monthly_counts.index[0] if not monthly_counts.empty else 'N/A',
            'peak_quarter': f"Q{quarterly_counts.index[0]}" if not quarterly_counts.empty else 'N/A',
            'large_transactions': len(large_transactions),
            'recent_activity_6m': len(recent_data),
            'monthly_concentration': monthly_concentration,
            'unusual_activity': unusual_activity,
            'timing_score': _calculate_timing_score(company_data, large_transactions, recent_data)
        }
    
    return timing_analysis


def _calculate_timing_score(company_data: pd.DataFrame, large_transactions: pd.DataFrame, recent_data: pd.DataFrame) -> float:
    """Calculate timing quality score"""
    
    score_components = []
    
    # Distribution score
    if len(company_data) > 0:
        months_active = company_data['month'].nunique()
        distribution_score = min(10, months_active * 1.2)
        score_components.append(distribution_score)
    
    # Large transaction timing
    if len(large_transactions) > 0:
        large_timing_score = 8 if len(large_transactions) <= len(company_data) * 0.2 else 5
        score_components.append(large_timing_score)
    
    # Recent activity balance
    if len(company_data) > 0:
        recent_ratio = len(recent_data) / len(company_data)
        recent_score = 7 if 0.2 <= recent_ratio <= 0.4 else 5 if recent_ratio <= 0.6 else 3
        score_components.append(recent_score)
    
    return np.mean(score_components) if score_components else 5.0