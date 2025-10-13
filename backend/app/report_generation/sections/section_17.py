"""Section 17: Cross-Asset Signal Discovery - Step 1"""

from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_card,
    build_stat_grid,
    build_data_table,
    build_enhanced_table,
    build_plotly_chart,
    build_info_box,
    build_section_divider,
    format_currency,
    format_percentage,
    format_number,
    build_summary_card,
    build_comparison_bars
)


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 17: Cross-Asset Signal Discovery
    
    Analyzes relationships between:
    - Price-Fundamental dynamics (technical signals predicting fundamental changes)
    - Ownership-Price relationships (institutional flow impact on prices)
    - Multi-timeframe integration (daily price vs quarterly fundamental/ownership)
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    df_financial = collector.get_all_financial_data()
    df_prices = collector.get_prices_daily()
    
    try:
        df_institutional = collector.get_institutional_ownership()
    except:
        df_institutional = pd.DataFrame()
    
    try:
        df_insider = collector.get_insider_trading_latest()
    except:
        df_insider = pd.DataFrame()
    
    # Perform all analyses
    price_fundamental_signals = _analyze_price_fundamental_relationships(
        df_prices, df_financial, companies
    )
    
    momentum_fundamental_analysis = _analyze_momentum_fundamental_correlation(
        df_prices, df_financial, companies, price_fundamental_signals
    )
    
    ownership_price_signals = _analyze_ownership_price_dynamics(
        df_prices, df_institutional, df_insider, companies
    )
    
    insider_price_analysis = _analyze_insider_price_response(
        df_prices, df_insider, companies, ownership_price_signals
    )
    
    multi_timeframe_signals = _analyze_multi_timeframe_integration(df_prices, df_financial, df_institutional, companies, price_fundamental_signals, ownership_price_signals)

    lead_lag_analysis = _analyze_lead_lag_relationships(df_prices, df_financial, df_institutional, companies, multi_timeframe_signals)
    
    # Build subsections
    section_17a1_html = _build_section_17a1_price_fundamental(
        price_fundamental_signals, companies
    )
    
    section_17a2_html = _build_section_17a2_momentum_fundamental(
        momentum_fundamental_analysis, companies
    )
    
    section_17b1_html = _build_section_17b1_institutional_flow(
        ownership_price_signals, companies
    )
    
    section_17b2_html = _build_section_17b2_insider_response(
        insider_price_analysis, companies
    )
    
    # Stubs for Step 2
    section_17c1_html = _build_section_17c1_multi_timeframe(multi_timeframe_signals,companies)
    section_17c2_html = _build_section_17c2_lead_lag(lead_lag_analysis,companies)
    
    # Stub for Step 4
    section_17e_html = _build_section_17e_strategic_insights()
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        <!-- Section Introduction -->
        <div class="info-box info">
            <h3>Cross-Asset Signal Discovery Overview</h3>
            <p>This section analyzes predictive relationships between price movements, fundamental performance, 
            and ownership activity across multiple timeframes. We examine:</p>
            <ul>
                <li><strong>Price-Fundamental Dynamics:</strong> How technical indicators predict fundamental changes</li>
                <li><strong>Ownership-Price Relationships:</strong> Impact of institutional and insider activity on prices</li>
                <li><strong>Multi-Timeframe Integration:</strong> Signal consistency across daily and quarterly data</li>
                <li><strong>Lead-Lag Patterns:</strong> Which signals lead others for predictive advantage</li>
            </ul>
            <p><em>Analysis focuses on statistical relationships, correlation strengths, and actual returns rather than composite scores.</em></p>
        </div>
        
        {section_17a1_html}
        {build_section_divider() if section_17a1_html else ""}
        
        {section_17a2_html}
        {build_section_divider() if section_17a2_html else ""}
        
        {section_17b1_html}
        {build_section_divider() if section_17b1_html else ""}
        
        {section_17b2_html}
        {build_section_divider() if section_17b2_html else ""}
        
        {section_17c1_html}
        {build_section_divider() if section_17c1_html else ""}
        
        {section_17c2_html}
        {build_section_divider() if section_17c2_html else ""}
        
        {section_17e_html}
    </div>
    """
    
    return generate_section_wrapper(17, "Cross-Asset Signal Discovery", content)


# =============================================================================
# 17A.1: PRICE-FUNDAMENTAL RELATIONSHIPS
# =============================================================================

def _build_section_17a1_price_fundamental(
    price_fundamental_signals: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17A.1: Price-Fundamental Relationships subsection"""
    
    if not price_fundamental_signals:
        return """
        <div class="info-box warning">
            <h3>17A.1: Price-Fundamental Relationships</h3>
            <p>Insufficient data available for price-fundamental relationship analysis.</p>
        </div>
        """
    
    # Create summary statistics
    total_companies = len(price_fundamental_signals)
    
    # Calculate aggregate metrics
    all_correlations = []
    significant_count = 0
    total_tests = 0
    
    for signals in price_fundamental_signals.values():
        correlations = signals.get('correlations', {})
        for corr_data in correlations.values():
            all_correlations.append(abs(corr_data['correlation']))
            total_tests += 1
            if corr_data.get('significant', False):
                significant_count += 1
    
    avg_abs_corr = np.mean(all_correlations) if all_correlations else 0
    median_abs_corr = np.median(all_correlations) if all_correlations else 0
    significance_rate = (significant_count / total_tests * 100) if total_tests > 0 else 0
    
    # Summary cards
    summary_cards = [
        {
            "label": "Companies Analyzed",
            "value": str(total_companies),
            "description": f"With {total_tests} correlation tests",
            "type": "info"
        },
        {
            "label": "Significant Relationships",
            "value": f"{significant_count}/{total_tests}",
            "description": f"{significance_rate:.0f}% significance rate",
            "type": "success" if significance_rate >= 40 else "warning" if significance_rate >= 25 else "default"
        },
        {
            "label": "Avg |Correlation|",
            "value": f"{avg_abs_corr:.3f}",
            "description": f"Median: {median_abs_corr:.3f}",
            "type": "success" if avg_abs_corr >= 0.4 else "info"
        },
        {
            "label": "Median Data Points",
            "value": str(int(np.median([s['data_points'] for s in price_fundamental_signals.values()]))),
            "description": "Annual observations per company",
            "type": "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create detailed table
    table_data = []
    for company_name, signals in price_fundamental_signals.items():
        correlations = signals.get('correlations', {})
        
        row = {'Company': company_name}
        
        # Momentum → Revenue
        if 'momentum_revenue' in correlations:
            mr = correlations['momentum_revenue']
            row['Mom→Rev (r)'] = f"{mr['correlation']:.3f}"
            row['Mom→Rev (p)'] = f"{mr['p_value']:.3f}"
            row['Mom→Rev Sig'] = "Yes" if mr['significant'] else "No"
        else:
            row['Mom→Rev (r)'] = "—"
            row['Mom→Rev (p)'] = "—"
            row['Mom→Rev Sig'] = "—"
        
        # RSI → Margins
        if 'rsi_margins' in correlations:
            rm = correlations['rsi_margins']
            row['RSI→Margin (r)'] = f"{rm['correlation']:.3f}"
            row['RSI→Margin (p)'] = f"{rm['p_value']:.3f}"
            row['RSI→Margin Sig'] = "Yes" if rm['significant'] else "No"
        else:
            row['RSI→Margin (r)'] = "—"
            row['RSI→Margin (p)'] = "—"
            row['RSI→Margin Sig'] = "—"
        
        # Volatility → ROE
        if 'volatility_roe' in correlations:
            vr = correlations['volatility_roe']
            row['Vol→ROE (r)'] = f"{vr['correlation']:.3f}"
            row['Vol→ROE (p)'] = f"{vr['p_value']:.3f}"
            row['Vol→ROE Sig'] = "Yes" if vr['significant'] else "No"
        else:
            row['Vol→ROE (r)'] = "—"
            row['Vol→ROE (p)'] = "—"
            row['Vol→ROE Sig'] = "—"
        
        row['Sig Count'] = f"{signals['significant_signals']}/{signals['total_signals']}"
        row['N (years)'] = signals['data_points']
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding for significance columns
    def sig_color(val):
        if val == "Yes":
            return "excellent"
        elif val == "No":
            return "poor"
        return "neutral"
    
    color_columns = {
        'Mom→Rev Sig': sig_color,
        'RSI→Margin Sig': sig_color,
        'Vol→ROE Sig': sig_color
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="table_17a1_price_fundamental",
        color_columns=color_columns,
        sortable=True,
        searchable=True
    )
    
    # Create charts
    chart1 = _create_chart_17a1_correlation_distribution(price_fundamental_signals)
    chart2 = _create_chart_17a1_significance_by_company(price_fundamental_signals)
    chart3 = _create_chart_17a1_correlation_heatmap(price_fundamental_signals)
    chart4 = _create_chart_17a1_pvalue_scatter(price_fundamental_signals)
    
    # Build collapsible section
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17a1')">
            <span>17A.1: Price-Fundamental Relationships - Technical Indicators as Leading Signals</span>
            <span id="icon_17a1" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17a1" style="display: block;">
            <p><strong>Analysis:</strong> Examines whether technical price indicators (momentum, RSI, volatility) 
            predict fundamental changes in revenue, margins, and profitability using annual data with 1-year lag.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Correlation Analysis by Company</h4>
            <p><em>Note: Uses lagged correlations (t-1 → t) to test predictive power. 
            Significance threshold: p < 0.15 (relaxed for annual data with limited observations).</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            {chart4}
            
            <div class="info-box info">
                <h4>Interpretation Guidelines</h4>
                <ul>
                    <li><strong>Correlation (r):</strong> Values closer to ±1.0 indicate stronger relationships</li>
                    <li><strong>P-value:</strong> Values < 0.15 considered significant (relaxed threshold for annual data)</li>
                    <li><strong>Sample Size (N):</strong> More years = more reliable correlations</li>
                    <li><strong>Momentum→Revenue:</strong> 60-day price momentum predicting next year's revenue growth</li>
                    <li><strong>RSI→Margins:</strong> RSI levels predicting next year's margin changes</li>
                    <li><strong>Volatility→ROE:</strong> Price volatility predicting next year's ROE changes</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
    function toggleCollapse(sectionId) {{
        const content = document.getElementById(sectionId);
        const icon = document.getElementById('icon_' + sectionId.split('_')[1]);
        
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            icon.style.transform = 'rotate(0deg)';
            icon.textContent = '▼';
        }} else {{
            content.style.display = 'none';
            icon.style.transform = 'rotate(-90deg)';
            icon.textContent = '▶';
        }}
    }}
    </script>
    """
    
    return subsection_html


def _create_chart_17a1_correlation_distribution(signals: Dict) -> str:
    """Create correlation distribution chart"""
    
    all_correlations = []
    relationship_labels = []
    
    for company, data in signals.items():
        correlations = data.get('correlations', {})
        
        if 'momentum_revenue' in correlations:
            all_correlations.append(correlations['momentum_revenue']['correlation'])
            relationship_labels.append(f"{company[:10]} - Mom→Rev")
        
        if 'rsi_margins' in correlations:
            all_correlations.append(correlations['rsi_margins']['correlation'])
            relationship_labels.append(f"{company[:10]} - RSI→Mgn")
        
        if 'volatility_roe' in correlations:
            all_correlations.append(correlations['volatility_roe']['correlation'])
            relationship_labels.append(f"{company[:10]} - Vol→ROE")
    
    if not all_correlations:
        return ""
    
    # Create histogram
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=all_correlations,
        nbinsx=15,
        marker=dict(
            color='rgba(102, 126, 234, 0.7)',
            line=dict(color='rgba(102, 126, 234, 1)', width=1)
        ),
        name='Correlations'
    ))
    
    fig.update_layout(
        title='Distribution of Price-Fundamental Correlations',
        xaxis_title='Correlation Coefficient',
        yaxis_title='Frequency',
        showlegend=False,
        height=400
    )
    
    # Add vertical lines at key thresholds
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0.3, line_dash="dot", line_color="green", opacity=0.3, 
                  annotation_text="Moderate (+)")
    fig.add_vline(x=-0.3, line_dash="dot", line_color="green", opacity=0.3,
                  annotation_text="Moderate (-)")
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_corr_dist")


def _create_chart_17a1_significance_by_company(signals: Dict) -> str:
    """Create significance count by company chart"""
    
    companies = []
    sig_counts = []
    total_counts = []
    
    for company, data in signals.items():
        companies.append(company[:15])
        sig_counts.append(data['significant_signals'])
        total_counts.append(data['total_signals'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Tests',
        x=companies,
        y=total_counts,
        marker_color='lightblue',
        opacity=0.6
    ))
    
    fig.add_trace(go.Bar(
        name='Significant',
        x=companies,
        y=sig_counts,
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title='Significant Relationships by Company',
        xaxis_title='Company',
        yaxis_title='Number of Relationships',
        barmode='overlay',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_sig_count")


def _create_chart_17a1_correlation_heatmap(signals: Dict) -> str:
    """Create correlation heatmap"""
    
    companies = list(signals.keys())[:10]  # Limit for readability
    relationship_types = ['Momentum→Revenue', 'RSI→Margins', 'Volatility→ROE']
    
    # Build correlation matrix
    corr_matrix = []
    for company in companies:
        row = []
        correlations = signals[company].get('correlations', {})
        
        for rel_key in ['momentum_revenue', 'rsi_margins', 'volatility_roe']:
            if rel_key in correlations:
                row.append(correlations[rel_key]['correlation'])
            else:
                row.append(0)
        
        corr_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=relationship_types,
        y=[c[:12] for c in companies],
        colorscale='RdYlGn',
        zmid=0,
        text=[[f"{val:.2f}" for val in row] for row in corr_matrix],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title='Price-Fundamental Correlation Heatmap (Top 10 Companies)',
        height=500
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_heatmap")


def _create_chart_17a1_pvalue_scatter(signals: Dict) -> str:
    """Create correlation vs p-value scatter plot"""
    
    correlations = []
    pvalues = []
    labels = []
    colors = []
    
    for company, data in signals.items():
        corrs = data.get('correlations', {})
        
        for rel_name, rel_key in [('Mom→Rev', 'momentum_revenue'), 
                                   ('RSI→Mgn', 'rsi_margins'), 
                                   ('Vol→ROE', 'volatility_roe')]:
            if rel_key in corrs:
                correlations.append(corrs[rel_key]['correlation'])
                pvalues.append(corrs[rel_key]['p_value'])
                labels.append(f"{company[:10]} - {rel_name}")
                colors.append('green' if corrs[rel_key]['significant'] else 'gray')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=correlations,
        y=pvalues,
        mode='markers',
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=labels,
        hovertemplate='%{text}<br>r=%{x:.3f}<br>p=%{y:.3f}<extra></extra>'
    ))
    
    # Add significance threshold line
    fig.add_hline(y=0.15, line_dash="dash", line_color="red", 
                  annotation_text="p=0.15 threshold")
    
    fig.update_layout(
        title='Correlation Strength vs Statistical Significance',
        xaxis_title='Correlation Coefficient',
        yaxis_title='P-value',
        height=400,
        yaxis_type='log'
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_scatter")


# =============================================================================
# 17A.2: MOMENTUM-FUNDAMENTAL CORRELATION
# =============================================================================

def _build_section_17a2_momentum_fundamental(
    momentum_analysis: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17A.2: Momentum-Fundamental Correlation subsection"""
    
    if not momentum_analysis:
        return """
        <div class="info-box warning">
            <h3>17A.2: Momentum-Fundamental Correlation Analysis</h3>
            <p>Momentum-fundamental correlation analysis unavailable.</p>
        </div>
        """
    
    # Summary statistics
    total_companies = len(momentum_analysis)
    revenue_pred_count = sum(1 for m in momentum_analysis.values() if m.get('revenue_predictive', False))
    margin_pred_count = sum(1 for m in momentum_analysis.values() if m.get('margin_predictive', False))
    profit_pred_count = sum(1 for m in momentum_analysis.values() if m.get('profitability_predictive', False))
    
    avg_momentum_strength = np.mean([m.get('momentum_strength', 0) for m in momentum_analysis.values()])
    
    # Summary cards
    summary_cards = [
        {
            "label": "Revenue Predictors",
            "value": f"{revenue_pred_count}/{total_companies}",
            "description": f"{revenue_pred_count/total_companies*100:.0f}% coverage",
            "type": "success" if revenue_pred_count >= total_companies * 0.5 else "info"
        },
        {
            "label": "Margin Predictors",
            "value": f"{margin_pred_count}/{total_companies}",
            "description": f"{margin_pred_count/total_companies*100:.0f}% coverage",
            "type": "success" if margin_pred_count >= total_companies * 0.5 else "info"
        },
        {
            "label": "Profitability Predictors",
            "value": f"{profit_pred_count}/{total_companies}",
            "description": f"{profit_pred_count/total_companies*100:.0f}% coverage",
            "type": "success" if profit_pred_count >= total_companies * 0.5 else "info"
        },
        {
            "label": "Avg Momentum Strength",
            "value": f"{avg_momentum_strength:.3f}",
            "description": "Sum of significant |correlations|",
            "type": "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table
    table_data = []
    for company, metrics in momentum_analysis.items():
        table_data.append({
            'Company': company,
            'Revenue Predictive': "Yes" if metrics.get('revenue_predictive', False) else "No",
            'Margin Predictive': "Yes" if metrics.get('margin_predictive', False) else "No",
            'Profitability Predictive': "Yes" if metrics.get('profitability_predictive', False) else "No",
            'Momentum Strength': f"{metrics.get('momentum_strength', 0):.3f}",
            'Predictive Count': f"{sum([metrics.get('revenue_predictive', False), metrics.get('margin_predictive', False), metrics.get('profitability_predictive', False)])}/3"
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding
    def pred_color(val):
        return "excellent" if val == "Yes" else "poor"
    
    color_columns = {
        'Revenue Predictive': pred_color,
        'Margin Predictive': pred_color,
        'Profitability Predictive': pred_color
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="table_17a2_momentum",
        color_columns=color_columns,
        sortable=True,
        searchable=True
    )
    
    # Charts
    chart1 = _create_chart_17a2_predictive_coverage(momentum_analysis)
    chart2 = _create_chart_17a2_momentum_strength(momentum_analysis)
    
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17a2')">
            <span>17A.2: Momentum-Fundamental Correlation - Price Momentum Predicting Performance</span>
            <span id="icon_17a2" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17a2" style="display: block;">
            <p><strong>Analysis:</strong> Examines which companies show momentum signals that successfully 
            predict fundamental performance across revenue, margins, and profitability metrics.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Predictive Coverage by Company</h4>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            
            <div class="info-box info">
                <h4>Interpretation</h4>
                <ul>
                    <li><strong>Predictive (Yes/No):</strong> Whether the correlation is statistically significant (p < 0.15)</li>
                    <li><strong>Momentum Strength:</strong> Sum of absolute correlations for significant relationships</li>
                    <li><strong>Predictive Count:</strong> Number of fundamental metrics predicted by momentum signals</li>
                </ul>
            </div>
        </div>
    </div>
    """
    
    return subsection_html


def _create_chart_17a2_predictive_coverage(momentum_analysis: Dict) -> str:
    """Create predictive coverage matrix chart"""
    
    companies = list(momentum_analysis.keys())
    revenue_pred = [1 if m.get('revenue_predictive', False) else 0 for m in momentum_analysis.values()]
    margin_pred = [1 if m.get('margin_predictive', False) else 0 for m in momentum_analysis.values()]
    profit_pred = [1 if m.get('profitability_predictive', False) else 0 for m in momentum_analysis.values()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Revenue',
        x=[c[:12] for c in companies],
        y=revenue_pred,
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='Margin',
        x=[c[:12] for c in companies],
        y=margin_pred,
        marker_color='#9b59b6'
    ))
    
    fig.add_trace(go.Bar(
        name='Profitability',
        x=[c[:12] for c in companies],
        y=profit_pred,
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title='Momentum Predictive Coverage Matrix',
        xaxis_title='Company',
        yaxis_title='Predictive (1=Yes, 0=No)',
        barmode='group',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a2_coverage")


def _create_chart_17a2_momentum_strength(momentum_analysis: Dict) -> str:
    """Create momentum strength scatter chart"""
    
    companies = list(momentum_analysis.keys())
    strengths = [m.get('momentum_strength', 0) for m in momentum_analysis.values()]
    pred_counts = [sum([m.get('revenue_predictive', False), 
                       m.get('margin_predictive', False), 
                       m.get('profitability_predictive', False)]) 
                   for m in momentum_analysis.values()]
    
    colors = ['green' if pc == 3 else 'orange' if pc == 2 else 'blue' if pc == 1 else 'gray' 
              for pc in pred_counts]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(companies))),
        y=strengths,
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=[f"{c[:15]}<br>Predictive: {pc}/3" for c, pc in zip(companies, pred_counts)],
        hovertemplate='%{text}<br>Strength: %{y:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Momentum Strength by Company (Color = Predictive Count)',
        xaxis_title='Company Index',
        yaxis_title='Momentum Strength',
        height=400,
        showlegend=False
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a2_strength")


# =============================================================================
# 17B.1: INSTITUTIONAL FLOW IMPACT
# =============================================================================

def _build_section_17b1_institutional_flow(
    ownership_signals: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17B.1: Institutional Flow Impact subsection"""
    
    if not ownership_signals:
        return """
        <div class="info-box warning">
            <h3>17B.1: Institutional Flow Impact on Price</h3>
            <p>Insufficient ownership data for institutional flow analysis.</p>
        </div>
        """
    
    # Summary statistics
    total_companies = len(ownership_signals)
    inst_available = sum(1 for s in ownership_signals.values() if s.get('institutional_impact'))
    insider_available = sum(1 for s in ownership_signals.values() if s.get('insider_impact'))
    
    # Calculate average impact scores
    inst_scores = [s.get('institutional_impact', {}).get('impact_score', 0) 
                   for s in ownership_signals.values() if s.get('institutional_impact')]
    insider_scores = [s.get('insider_impact', {}).get('impact_score', 0) 
                      for s in ownership_signals.values() if s.get('insider_impact')]
    
    avg_inst_score = np.mean(inst_scores) if inst_scores else 0
    avg_insider_score = np.mean(insider_scores) if insider_scores else 0
    
    # Summary cards
    summary_cards = [
        {
            "label": "Institutional Coverage",
            "value": f"{inst_available}/{total_companies}",
            "description": f"{inst_available/total_companies*100:.0f}% with data",
            "type": "info"
        },
        {
            "label": "Insider Coverage",
            "value": f"{insider_available}/{total_companies}",
            "description": f"{insider_available/total_companies*100:.0f}% with data",
            "type": "info"
        },
        {
            "label": "Avg Inst Impact",
            "value": f"{avg_inst_score:.1%}",
            "description": "Significant correlations / total",
            "type": "success" if avg_inst_score >= 0.5 else "default"
        },
        {
            "label": "Avg Insider Impact",
            "value": f"{avg_insider_score:.1%}",
            "description": "Significant correlations / total",
            "type": "success" if avg_insider_score >= 0.5 else "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table
    table_data = []
    for company, signals in ownership_signals.items():
        inst_impact = signals.get('institutional_impact', {})
        insider_impact = signals.get('insider_impact', {})
        combined = signals.get('combined_signal', {})
        
        # Institutional metrics
        inst_corrs = inst_impact.get('correlations', {})
        inst_sig_count = inst_impact.get('significant_relationships', 0)
        inst_total = inst_impact.get('total_tested', 0)
        
        # Insider metrics
        insider_corrs = insider_impact.get('correlations', {})
        insider_sig_count = insider_impact.get('significant_relationships', 0)
        insider_total = insider_impact.get('total_tested', 0)
        
        row = {
            'Company': company,
            'Inst Impact': f"{inst_impact.get('impact_score', 0):.1%}" if inst_impact else "N/A",
            'Inst Sig': f"{inst_sig_count}/{inst_total}" if inst_total > 0 else "N/A",
            'Insider Impact': f"{insider_impact.get('impact_score', 0):.1%}" if insider_impact else "N/A",
            'Insider Sig': f"{insider_sig_count}/{insider_total}" if insider_total > 0 else "N/A",
            'Combined Score': f"{combined.get('combined_score', 0):.1%}" if combined else "N/A",
            'Data Points': max(inst_impact.get('data_points', 0), insider_impact.get('data_points', 0))
        }
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    table_html = build_data_table(
        df_table,
        table_id="table_17b1_ownership",
        sortable=True,
        searchable=True
    )
    
    # Charts
    chart1 = _create_chart_17b1_inst_vs_insider(ownership_signals)
    chart2 = _create_chart_17b1_combined_scores(ownership_signals)
    chart3 = _create_chart_17b1_correlation_details(ownership_signals)
    
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17b1')">
            <span>17B.1: Institutional Flow Impact - Ownership Changes Predicting Price Movements</span>
            <span id="icon_17b1" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17b1" style="display: block;">
            <p><strong>Analysis:</strong> Analyzes how institutional ownership changes and insider transactions 
            correlate with price movements. Uses annual aggregation for institutional data.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Ownership-Price Impact by Company</h4>
            <p><em>Note: Impact score = proportion of significant correlations. 
            Institutional analysis uses annual data; insider uses monthly aggregation.</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            
            <div class="info-box info">
                <h4>Interpretation</h4>
                <ul>
                    <li><strong>Impact Score:</strong> Percentage of ownership-price correlations that are statistically significant</li>
                    <li><strong>Sig Count:</strong> Number of significant relationships out of total tested</li>
                    <li><strong>Combined Score:</strong> Average of institutional and insider impact scores (or max if only one available)</li>
                    <li><strong>Institutional Metrics:</strong> Based on annual ownership changes vs annual returns</li>
                    <li><strong>Insider Metrics:</strong> Based on monthly transaction activity vs monthly returns</li>
                </ul>
            </div>
        </div>
    </div>
    """
    
    return subsection_html


def _create_chart_17b1_inst_vs_insider(ownership_signals: Dict) -> str:
    """Create institutional vs insider impact comparison"""
    
    companies = list(ownership_signals.keys())
    inst_scores = [s.get('institutional_impact', {}).get('impact_score', 0) * 100 
                   for s in ownership_signals.values()]
    insider_scores = [s.get('insider_impact', {}).get('impact_score', 0) * 100 
                      for s in ownership_signals.values()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Institutional',
        x=[c[:12] for c in companies],
        y=inst_scores,
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='Insider',
        x=[c[:12] for c in companies],
        y=insider_scores,
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title='Institutional vs Insider Price Impact',
        xaxis_title='Company',
        yaxis_title='Impact Score (%)',
        barmode='group',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_inst_insider")


def _create_chart_17b1_combined_scores(ownership_signals: Dict) -> str:
    """Create combined ownership scores chart"""
    
    companies = list(ownership_signals.keys())
    combined_scores = [s.get('combined_signal', {}).get('combined_score', 0) * 100 
                       for s in ownership_signals.values()]
    
    colors = ['green' if score >= 60 else 'orange' if score >= 30 else 'gray' 
              for score in combined_scores]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[c[:15] for c in companies],
        y=combined_scores,
        marker_color=colors,
        text=[f"{score:.0f}%" for score in combined_scores],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Combined Ownership-Price Signal Strength',
        xaxis_title='Company',
        yaxis_title='Combined Score (%)',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_combined")


def _create_chart_17b1_correlation_details(ownership_signals: Dict) -> str:
    """Create scatter plot of institutional vs insider impact"""
    
    companies = list(ownership_signals.keys())
    inst_scores = [s.get('institutional_impact', {}).get('impact_score', 0) * 100 
                   for s in ownership_signals.values()]
    insider_scores = [s.get('insider_impact', {}).get('impact_score', 0) * 100 
                      for s in ownership_signals.values()]
    combined_scores = [s.get('combined_signal', {}).get('combined_score', 0) * 100 
                       for s in ownership_signals.values()]
    
    colors = ['green' if score >= 60 else 'orange' if score >= 30 else 'gray' 
              for score in combined_scores]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=inst_scores,
        y=insider_scores,
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=[f"{c[:15]}<br>Combined: {cs:.0f}%" 
              for c, cs in zip(companies, combined_scores)],
        hovertemplate='%{text}<br>Inst: %{x:.0f}%<br>Insider: %{y:.0f}%<extra></extra>'
    ))
    
    # Add diagonal line
    max_val = max(max(inst_scores) if inst_scores else 0, 
                  max(insider_scores) if insider_scores else 0)
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode='lines',
        line=dict(dash='dash', color='red'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title='Institutional vs Insider Impact Comparison (Color = Combined Score)',
        xaxis_title='Institutional Impact Score (%)',
        yaxis_title='Insider Impact Score (%)',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_scatter")


# =============================================================================
# 17B.2: INSIDER TRANSACTION RESPONSE
# =============================================================================

def _build_section_17b2_insider_response(
    insider_analysis: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17B.2: Insider Transaction Response subsection"""
    
    if not insider_analysis:
        return """
        <div class="info-box warning">
            <h3>17B.2: Insider Activity & Price Response</h3>
            <p>Insufficient insider transaction data for price response analysis.</p>
        </div>
        """
    
    # Summary statistics
    total_companies = len(insider_analysis)
    
    # Calculate metrics
    companies_with_buys = sum(1 for m in insider_analysis.values() 
                             if m.get('buy_transactions', 0) > 0)
    
    avg_return_30d = np.mean([m.get('avg_return_30d_after_buy', 0) 
                              for m in insider_analysis.values() 
                              if 'avg_return_30d_after_buy' in m])
    
    avg_return_60d = np.mean([m.get('avg_return_60d_after_buy', 0) 
                              for m in insider_analysis.values() 
                              if 'avg_return_60d_after_buy' in m])
    
    avg_success_rate = np.mean([m.get('buy_success_rate', 0) 
                               for m in insider_analysis.values() 
                               if 'buy_success_rate' in m])
    
    total_buy_transactions = sum(m.get('buy_transactions', 0) 
                                for m in insider_analysis.values())
    
    # Summary cards
    summary_cards = [
        {
            "label": "Companies with Buys",
            "value": f"{companies_with_buys}/{total_companies}",
            "description": f"{total_buy_transactions} total buy transactions",
            "type": "info"
        },
        {
            "label": "Avg 30-Day Return",
            "value": f"{avg_return_30d:+.1f}%",
            "description": "After insider purchases",
            "type": "success" if avg_return_30d > 0 else "danger"
        },
        {
            "label": "Avg 60-Day Return",
            "value": f"{avg_return_60d:+.1f}%",
            "description": "After insider purchases",
            "type": "success" if avg_return_60d > 0 else "danger"
        },
        {
            "label": "Success Rate",
            "value": f"{avg_success_rate:.0%}",
            "description": "% positive returns after buys",
            "type": "success" if avg_success_rate >= 0.55 else "warning" if avg_success_rate >= 0.5 else "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table
    table_data = []
    for company, metrics in insider_analysis.items():
        row = {
            'Company': company,
            'Buy Transactions': metrics.get('buy_transactions', 0),
            '30d Return': f"{metrics.get('avg_return_30d_after_buy', 0):+.1f}%" 
                         if 'avg_return_30d_after_buy' in metrics else "N/A",
            '60d Return': f"{metrics.get('avg_return_60d_after_buy', 0):+.1f}%" 
                         if 'avg_return_60d_after_buy' in metrics else "N/A",
            'Success Rate': f"{metrics.get('buy_success_rate', 0):.0%}" 
                           if 'buy_success_rate' in metrics else "N/A",
            'Signal Strength': f"{metrics.get('signal_quality', 0):.0%}"
        }
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    table_html = build_data_table(
        df_table,
        table_id="table_17b2_insider",
        sortable=True,
        searchable=True
    )
    
    # Charts
    chart1 = _create_chart_17b2_returns_after_buys(insider_analysis)
    chart2 = _create_chart_17b2_success_rates(insider_analysis)
    chart3 = _create_chart_17b2_signal_vs_success(insider_analysis)
    
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17b2')">
            <span>17B.2: Insider Activity & Price Response - Market Reaction to Insider Trades</span>
            <span id="icon_17b2" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17b2" style="display: block;">
            <p><strong>Analysis:</strong> Examines price performance following significant insider purchase transactions 
            (top 50% by transaction value). Tracks 30-day and 60-day forward returns.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Insider Buy Signal Performance by Company</h4>
            <p><em>Note: Analyzes substantial transactions only (≥50th percentile by value). 
            Success rate = % of transactions followed by positive 30-day returns.</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            
            <div class="info-box info">
                <h4>Interpretation</h4>
                <ul>
                    <li><strong>30d/60d Return:</strong> Average return following insider purchases at 30 and 60 day horizons</li>
                    <li><strong>Success Rate:</strong> Percentage of insider buys followed by positive 30-day returns</li>
                    <li><strong>Signal Strength:</strong> 100% if avg 30d return > 0 AND success rate > 50%, else 50%</li>
                    <li><strong>Positive Returns:</strong> Suggest insider buys may be informative signals</li>
                    <li><strong>High Success Rates (>60%):</strong> Indicate consistent predictive value</li>
                </ul>
            </div>
        </div>
    </div>
    """
    
    return subsection_html


def _create_chart_17b2_returns_after_buys(insider_analysis: Dict) -> str:
    """Create returns following insider buys chart"""
    
    companies = list(insider_analysis.keys())
    returns_30d = [m.get('avg_return_30d_after_buy', 0) for m in insider_analysis.values()]
    returns_60d = [m.get('avg_return_60d_after_buy', 0) for m in insider_analysis.values()]
    
    colors_30d = ['green' if r > 0 else 'red' for r in returns_30d]
    colors_60d = ['darkgreen' if r > 0 else 'darkred' for r in returns_60d]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='30-Day Return',
        x=[c[:12] for c in companies],
        y=returns_30d,
        marker_color=colors_30d,
        opacity=0.8
    ))
    
    fig.add_trace(go.Bar(
        name='60-Day Return',
        x=[c[:12] for c in companies],
        y=returns_60d,
        marker_color=colors_60d,
        opacity=0.8
    ))
    
    fig.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.3)
    
    fig.update_layout(
        title='Average Returns Following Insider Purchases',
        xaxis_title='Company',
        yaxis_title='Average Return (%)',
        barmode='group',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_returns")


def _create_chart_17b2_success_rates(insider_analysis: Dict) -> str:
    """Create success rates horizontal bar chart"""
    
    companies = list(insider_analysis.keys())
    success_rates = [m.get('buy_success_rate', 0) * 100 for m in insider_analysis.values()]
    
    colors = ['green' if sr >= 60 else 'orange' if sr >= 50 else 'gray' 
              for sr in success_rates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[c[:15] for c in companies],
        x=success_rates,
        orientation='h',
        marker_color=colors,
        text=[f"{sr:.0f}%" for sr in success_rates],
        textposition='outside'
    ))
    
    fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5,
                  annotation_text="50% threshold")
    
    fig.update_layout(
        title='Insider Buy Signal Success Rates',
        xaxis_title='Success Rate (%)',
        yaxis_title='Company',
        height=max(400, len(companies) * 25)
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_success")


def _create_chart_17b2_signal_vs_success(insider_analysis: Dict) -> str:
    """Create signal strength vs success rate scatter"""
    
    companies = list(insider_analysis.keys())
    signal_strength = [m.get('signal_quality', 0) * 100 for m in insider_analysis.values()]
    success_rates = [m.get('buy_success_rate', 0) * 100 for m in insider_analysis.values()]
    
    colors = ['green' if sr >= 60 else 'orange' if sr >= 50 else 'gray' 
              for sr in success_rates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=signal_strength,
        y=success_rates,
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=[f"{c[:15]}<br>Buys: {insider_analysis[c].get('buy_transactions', 0)}" 
              for c in companies],
        hovertemplate='%{text}<br>Signal: %{x:.0f}%<br>Success: %{y:.0f}%<extra></extra>'
    ))
    
    # Add threshold lines
    fig.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.3)
    fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.3)
    
    fig.update_layout(
        title='Insider Signal Strength vs Success Rate',
        xaxis_title='Signal Strength (%)',
        yaxis_title='Success Rate (%)',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_scatter")


# =============================================================================
# STUBS FOR STEP 2
# =============================================================================

"""
Section 17 Step 2: Multi-Timeframe Integration & Lead-Lag Analysis
This file contains the code to ADD to section_17.py from Step 1
Replace the stub functions with these implementations
"""

# =============================================================================
# 17C.1: MULTI-TIMEFRAME INTEGRATION
# =============================================================================

"""
Section 17 Step 2: Multi-Timeframe Integration & Lead-Lag Analysis
This file contains the code to ADD to section_17.py from Step 1
Replace the stub functions with these implementations
NO SCORING SYSTEMS - Only raw statistical measures
"""

# =============================================================================
# 17C.1: MULTI-TIMEFRAME INTEGRATION
# =============================================================================

def _build_section_17c1_multi_timeframe(
    multi_timeframe_signals: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17C.1: Multi-Timeframe Integration subsection"""
    
    if not multi_timeframe_signals:
        return """
        <div class="info-box warning">
            <h3>17C.1: Multi-Timeframe Integration</h3>
            <p>Insufficient data for multi-timeframe integration analysis.</p>
        </div>
        """
    
    # Summary statistics - RAW METRICS ONLY
    total_companies = len(multi_timeframe_signals)
    
    # Daily signal metrics
    daily_sig_counts = [s['daily_significant'] for s in multi_timeframe_signals.values()]
    daily_total_counts = [s['daily_total'] for s in multi_timeframe_signals.values()]
    total_daily_sig = sum(daily_sig_counts)
    total_daily_tests = sum(daily_total_counts)
    
    # Quarterly signal metrics
    quarterly_sig_counts = [s['quarterly_significant'] for s in multi_timeframe_signals.values()]
    quarterly_total_counts = [s['quarterly_total'] for s in multi_timeframe_signals.values()]
    total_quarterly_sig = sum(quarterly_sig_counts)
    total_quarterly_tests = sum(quarterly_total_counts)
    
    # Companies with both signals
    both_signals = sum(1 for s in multi_timeframe_signals.values() 
                      if s['daily_significant'] > 0 and s['quarterly_significant'] > 0)
    
    # Summary cards
    summary_cards = [
        {
            "label": "Daily Signal Coverage",
            "value": f"{total_daily_sig}/{total_daily_tests}",
            "description": f"{total_daily_sig/total_daily_tests*100:.0f}% significant (price-fundamental)",
            "type": "info"
        },
        {
            "label": "Quarterly Signal Coverage",
            "value": f"{total_quarterly_sig}/{total_quarterly_tests}",
            "description": f"{total_quarterly_sig/total_quarterly_tests*100:.0f}% significant (ownership-price)",
            "type": "info"
        },
        {
            "label": "Dual-Timeframe Coverage",
            "value": f"{both_signals}/{total_companies}",
            "description": "Companies with both daily and quarterly signals",
            "type": "success" if both_signals >= total_companies * 0.5 else "warning"
        },
        {
            "label": "Total Tests",
            "value": str(total_daily_tests + total_quarterly_tests),
            "description": "Cross-frequency correlation tests",
            "type": "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table - RAW NUMBERS ONLY
    table_data = []
    for company, signals in multi_timeframe_signals.items():
        table_data.append({
            'Company': company,
            'Daily Sig/Total': f"{signals['daily_significant']}/{signals['daily_total']}",
            'Daily %': f"{signals['daily_significant']/signals['daily_total']*100:.0f}%" if signals['daily_total'] > 0 else "—",
            'Daily N': signals['daily_data_points'],
            'Quarterly Sig/Total': f"{signals['quarterly_significant']}/{signals['quarterly_total']}",
            'Quarterly %': f"{signals['quarterly_significant']/signals['quarterly_total']*100:.0f}%" if signals['quarterly_total'] > 0 else "—",
            'Quarterly N': signals['quarterly_data_points'],
            'Both Signals': "Yes" if signals['daily_significant'] > 0 and signals['quarterly_significant'] > 0 else "No"
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding
    def both_color(val):
        return "excellent" if val == "Yes" else "neutral"
    
    color_columns = {'Both Signals': both_color}
    
    table_html = build_enhanced_table(
        df_table,
        table_id="table_17c1_multitimeframe",
        color_columns=color_columns,
        sortable=True,
        searchable=True
    )
    
    # Charts
    chart1 = _create_chart_17c1_signal_comparison(multi_timeframe_signals)
    chart2 = _create_chart_17c1_coverage_scatter(multi_timeframe_signals)
    chart3 = _create_chart_17c1_datapoint_distribution(multi_timeframe_signals)
    chart4 = _create_chart_17c1_signal_heatmap(multi_timeframe_signals)
    
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17c1')">
            <span>17C.1: Multi-Timeframe Integration - Daily Price vs Quarterly Fundamental/Ownership Signals</span>
            <span id="icon_17c1" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17c1" style="display: block;">
            <p><strong>Analysis:</strong> Compares signal coverage across different timeframes - daily price-fundamental 
            relationships vs quarterly ownership-price relationships. Shows actual significant correlations, not composite scores.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Multi-Timeframe Signal Coverage by Company</h4>
            <p><em>Note: "Sig/Total" = number of significant correlations / total correlations tested. 
            "N" = number of data points (years for daily analysis, annual for quarterly). 
            "Both Signals" indicates companies with predictive relationships in both timeframes.</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            {chart4}
            
            <div class="info-box info">
                <h4>Interpretation Guidelines</h4>
                <ul>
                    <li><strong>Daily Signals:</strong> From price-fundamental analysis (momentum, RSI, volatility predicting revenue/margins/ROE)</li>
                    <li><strong>Quarterly Signals:</strong> From ownership-price analysis (institutional/insider activity predicting returns)</li>
                    <li><strong>Significance Rate:</strong> Proportion of correlations with p < 0.15 (daily) or p < 0.10 (quarterly)</li>
                    <li><strong>Data Points (N):</strong> Sample size for correlation tests - more points = more reliable</li>
                    <li><strong>Both Signals = Yes:</strong> Company has predictive relationships in BOTH timeframes (strongest evidence)</li>
                    <li><strong>High Daily % + Low Quarterly %:</strong> Price technicals work better than ownership signals</li>
                    <li><strong>Low Daily % + High Quarterly %:</strong> Ownership activity more predictive than price patterns</li>
                </ul>
            </div>
        </div>
    </div>
    """
    
    return subsection_html


def _create_chart_17c1_signal_comparison(signals: Dict) -> str:
    """Create daily vs quarterly signal comparison - actual counts"""
    
    companies = list(signals.keys())
    daily_sig = [s['daily_significant'] for s in signals.values()]
    daily_total = [s['daily_total'] for s in signals.values()]
    quarterly_sig = [s['quarterly_significant'] for s in signals.values()]
    quarterly_total = [s['quarterly_total'] for s in signals.values()]
    
    fig = go.Figure()
    
    # Daily signals
    fig.add_trace(go.Bar(
        name='Daily Sig',
        x=[c[:12] for c in companies],
        y=daily_sig,
        marker_color='#3498db',
        legendgroup='daily'
    ))
    
    fig.add_trace(go.Bar(
        name='Daily Total',
        x=[c[:12] for c in companies],
        y=daily_total,
        marker_color='lightblue',
        opacity=0.5,
        legendgroup='daily'
    ))
    
    # Quarterly signals
    fig.add_trace(go.Bar(
        name='Quarterly Sig',
        x=[c[:12] for c in companies],
        y=quarterly_sig,
        marker_color='#9b59b6',
        legendgroup='quarterly'
    ))
    
    fig.add_trace(go.Bar(
        name='Quarterly Total',
        x=[c[:12] for c in companies],
        y=quarterly_total,
        marker_color='plum',
        opacity=0.5,
        legendgroup='quarterly'
    ))
    
    fig.update_layout(
        title='Multi-Timeframe Signal Coverage: Significant vs Total Tests',
        xaxis_title='Company',
        yaxis_title='Number of Correlations',
        barmode='group',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_comparison")


def _create_chart_17c1_coverage_scatter(signals: Dict) -> str:
    """Create scatter plot of daily vs quarterly coverage"""
    
    companies = list(signals.keys())
    daily_pct = [s['daily_significant']/s['daily_total']*100 if s['daily_total'] > 0 else 0 
                 for s in signals.values()]
    quarterly_pct = [s['quarterly_significant']/s['quarterly_total']*100 if s['quarterly_total'] > 0 else 0 
                     for s in signals.values()]
    both_signals = [s['daily_significant'] > 0 and s['quarterly_significant'] > 0 
                    for s in signals.values()]
    
    colors = ['green' if both else 'gray' for both in both_signals]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_pct,
        y=quarterly_pct,
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=[f"{c[:15]}<br>Daily: {d:.0f}%<br>Quarterly: {q:.0f}%" 
              for c, d, q in zip(companies, daily_pct, quarterly_pct)],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    # Add diagonal line
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        line=dict(dash='dash', color='red', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title='Daily vs Quarterly Signal Coverage % (Green = Both Timeframes Have Signals)',
        xaxis_title='Daily Signal Coverage (%)',
        yaxis_title='Quarterly Signal Coverage (%)',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_scatter")


def _create_chart_17c1_datapoint_distribution(signals: Dict) -> str:
    """Create data point distribution comparison"""
    
    companies = list(signals.keys())
    daily_n = [s['daily_data_points'] for s in signals.values()]
    quarterly_n = [s['quarterly_data_points'] for s in signals.values()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Daily Data Points',
        x=[c[:12] for c in companies],
        y=daily_n,
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='Quarterly Data Points',
        x=[c[:12] for c in companies],
        y=quarterly_n,
        marker_color='#9b59b6'
    ))
    
    fig.update_layout(
        title='Sample Sizes: Data Points Available for Each Timeframe',
        xaxis_title='Company',
        yaxis_title='Number of Data Points',
        barmode='group',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_datapoints")


def _create_chart_17c1_signal_heatmap(signals: Dict) -> str:
    """Create heatmap showing signal counts"""
    
    companies = list(signals.keys())[:12]  # Limit for readability
    
    # Build matrix: [daily_sig, daily_total, quarterly_sig, quarterly_total]
    metrics = ['Daily\nSignificant', 'Daily\nTotal', 'Quarterly\nSignificant', 'Quarterly\nTotal']
    
    matrix = []
    for company in companies:
        s = signals[company]
        matrix.append([
            s['daily_significant'],
            s['daily_total'],
            s['quarterly_significant'],
            s['quarterly_total']
        ])
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=metrics,
        y=[c[:12] for c in companies],
        colorscale='Blues',
        text=[[f"{int(val)}" for val in row] for row in matrix],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Count")
    ))
    
    fig.update_layout(
        title='Multi-Timeframe Signal Count Heatmap (Top 12 Companies)',
        height=500
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_heatmap")


# =============================================================================
# 17C.2: LEAD-LAG RELATIONSHIPS
# =============================================================================

def _build_section_17c2_lead_lag(
    lead_lag_analysis: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17C.2: Lead-Lag Relationships subsection"""
    
    if not lead_lag_analysis:
        return """
        <div class="info-box warning">
            <h3>17C.2: Lead-Lag Relationships & Predictive Signals</h3>
            <p>Insufficient data for lead-lag relationship analysis.</p>
        </div>
        """
    
    # Summary statistics - RAW METRICS ONLY
    total_companies = len(lead_lag_analysis)
    
    # Count significant patterns
    total_significant = sum(a['significant_patterns'] for a in lead_lag_analysis.values())
    total_tested = sum(a['total_tested'] for a in lead_lag_analysis.values())
    
    # Average correlation strengths
    all_mom_vol_corrs = []
    all_short_long_corrs = []
    
    for analysis in lead_lag_analysis.values():
        metrics = analysis.get('lead_lag_metrics', {})
        if 'momentum_leads_volatility' in metrics:
            all_mom_vol_corrs.append(abs(metrics['momentum_leads_volatility']['correlation']))
        if 'short_term_leads_long_term' in metrics:
            all_short_long_corrs.append(metrics['short_term_leads_long_term']['correlation'])
    
    avg_mom_vol = np.mean(all_mom_vol_corrs) if all_mom_vol_corrs else 0
    avg_short_long = np.mean(all_short_long_corrs) if all_short_long_corrs else 0
    
    # Summary cards
    summary_cards = [
        {
            "label": "Companies Analyzed",
            "value": str(total_companies),
            "description": f"{total_tested} lead-lag correlation tests",
            "type": "info"
        },
        {
            "label": "Significant Patterns",
            "value": f"{total_significant}/{total_tested}",
            "description": f"{total_significant/total_tested*100:.0f}% with p < 0.10",
            "type": "success" if total_significant/total_tested >= 0.4 else "warning"
        },
        {
            "label": "Avg |Mom→Vol| Corr",
            "value": f"{avg_mom_vol:.3f}",
            "description": "Mean absolute correlation strength",
            "type": "info"
        },
        {
            "label": "Avg Short→Long Corr",
            "value": f"{avg_short_long:+.3f}",
            "description": "Mean momentum persistence",
            "type": "success" if avg_short_long > 0 else "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table - RAW CORRELATIONS AND P-VALUES
    table_data = []
    for company, analysis in lead_lag_analysis.items():
        metrics = analysis.get('lead_lag_metrics', {})
        
        row = {
            'Company': company,
            'Mom→Vol r': "—",
            'Mom→Vol p': "—",
            'Mom→Vol Sig': "—",
            'Short→Long r': "—",
            'Short→Long p': "—",
            'Short→Long Sig': "—",
            'Sig/Total': f"{analysis['significant_patterns']}/{analysis['total_tested']}",
            'N (days)': "—"
        }
        
        # Momentum leads volatility
        if 'momentum_leads_volatility' in metrics:
            mlv = metrics['momentum_leads_volatility']
            row['Mom→Vol r'] = f"{mlv['correlation']:.3f}"
            row['Mom→Vol p'] = f"{mlv['p_value']:.3f}"
            row['Mom→Vol Sig'] = "Yes" if mlv['significant'] else "No"
            row['N (days)'] = analysis.get('sample_size', '—')
        
        # Short-term leads long-term
        if 'short_term_leads_long_term' in metrics:
            stlt = metrics['short_term_leads_long_term']
            row['Short→Long r'] = f"{stlt['correlation']:.3f}"
            row['Short→Long p'] = f"{stlt['p_value']:.3f}"
            row['Short→Long Sig'] = "Yes" if stlt['significant'] else "No"
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding for significance
    def sig_color(val):
        if val == "Yes":
            return "excellent"
        elif val == "No":
            return "poor"
        return "neutral"
    
    color_columns = {
        'Mom→Vol Sig': sig_color,
        'Short→Long Sig': sig_color
    }
    
    table_html = build_enhanced_table(
        df_table,
        table_id="table_17c2_leadlag",
        color_columns=color_columns,
        sortable=True,
        searchable=True
    )
    
    # Charts
    chart1 = _create_chart_17c2_correlation_comparison(lead_lag_analysis)
    chart2 = _create_chart_17c2_pvalue_scatter(lead_lag_analysis)
    chart3 = _create_chart_17c2_significance_distribution(lead_lag_analysis)
    chart4 = _create_chart_17c2_correlation_heatmap(lead_lag_analysis)
    
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17c2')">
            <span>17C.2: Lead-Lag Relationships - Predictive Signal Correlations & Lead Times</span>
            <span id="icon_17c2" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17c2" style="display: block;">
            <p><strong>Analysis:</strong> Tests whether short-term signals predict longer-term outcomes using 20-day lead periods. 
            Shows actual correlation coefficients and p-values, not composite scores.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Lead-Lag Correlation Analysis by Company</h4>
            <p><em>Note: All tests use 20-day lead period. "r" = correlation coefficient, "p" = p-value. 
            Sig = significant at p < 0.10. Mom→Vol tests if momentum predicts volatility. 
            Short→Long tests momentum persistence (20d returns → 60d returns).</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            {chart4}
            
            <div class="info-box info">
                <h4>Interpretation Guidelines</h4>
                <ul>
                    <li><strong>Momentum → Volatility (Mom→Vol):</strong> Whether 20-day price momentum (lagged 20 days) predicts 60-day volatility changes</li>
                    <li><strong>Short-term → Long-term:</strong> Momentum persistence - whether 20-day returns (lagged 20 days) predict 60-day returns</li>
                    <li><strong>Correlation (r):</strong> Strength and direction of relationship (-1 to +1). Values closer to ±1 indicate stronger relationships</li>
                    <li><strong>P-value (p):</strong> Statistical significance. Values < 0.10 considered significant (higher threshold for lead-lag tests)</li>
                    <li><strong>Lead Period:</strong> All tests use 20 trading days (~1 month) lead time for practical trading utility</li>
                    <li><strong>Sample Size (N):</strong> Number of observations used in correlation test - more = more reliable</li>
                    <li><strong>Positive Short→Long:</strong> Momentum persistence (winners keep winning)</li>
                    <li><strong>Negative Short→Long:</strong> Mean reversion (winners reverse)</li>
                </ul>
            </div>
        </div>
    </div>
    """
    
    return subsection_html


def _create_chart_17c2_correlation_comparison(lead_lag_analysis: Dict) -> str:
    """Create correlation comparison chart"""
    
    companies = list(lead_lag_analysis.keys())
    
    mom_vol_corrs = []
    short_long_corrs = []
    
    for company in companies:
        metrics = lead_lag_analysis[company].get('lead_lag_metrics', {})
        
        if 'momentum_leads_volatility' in metrics:
            mom_vol_corrs.append(abs(metrics['momentum_leads_volatility']['correlation']))
        else:
            mom_vol_corrs.append(0)
        
        if 'short_term_leads_long_term' in metrics:
            short_long_corrs.append(metrics['short_term_leads_long_term']['correlation'])
        else:
            short_long_corrs.append(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='|Mom→Vol| Correlation',
        x=[c[:12] for c in companies],
        y=mom_vol_corrs,
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        name='Short→Long Correlation',
        x=[c[:12] for c in companies],
        y=short_long_corrs,
        marker_color='#3498db'
    ))
    
    fig.add_hline(y=0, line_color='black', line_width=1, opacity=0.3)
    
    fig.update_layout(
        title='Lead-Lag Correlation Strengths by Company',
        xaxis_title='Company',
        yaxis_title='Correlation Coefficient',
        barmode='group',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_correlations")


def _create_chart_17c2_pvalue_scatter(lead_lag_analysis: Dict) -> str:
    """Create correlation vs p-value scatter for both relationships"""
    
    correlations = []
    pvalues = []
    labels = []
    colors = []
    
    for company, analysis in lead_lag_analysis.items():
        metrics = analysis.get('lead_lag_metrics', {})
        
        if 'momentum_leads_volatility' in metrics:
            mlv = metrics['momentum_leads_volatility']
            correlations.append(mlv['correlation'])
            pvalues.append(mlv['p_value'])
            labels.append(f"{company[:10]} - Mom→Vol")
            colors.append('green' if mlv['significant'] else 'gray')
        
        if 'short_term_leads_long_term' in metrics:
            stlt = metrics['short_term_leads_long_term']
            correlations.append(stlt['correlation'])
            pvalues.append(stlt['p_value'])
            labels.append(f"{company[:10]} - Short→Long")
            colors.append('blue' if stlt['significant'] else 'lightgray')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=correlations,
        y=pvalues,
        mode='markers',
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=labels,
        hovertemplate='%{text}<br>r=%{x:.3f}<br>p=%{y:.3f}<extra></extra>'
    ))
    
    fig.add_hline(y=0.10, line_dash="dash", line_color="red", opacity=0.5,
                  annotation_text="p=0.10 threshold")
    
    fig.update_layout(
        title='Lead-Lag Correlation Strength vs Statistical Significance',
        xaxis_title='Correlation Coefficient',
        yaxis_title='P-value',
        height=400,
        yaxis_type='log'
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_pvalue")


def _create_chart_17c2_significance_distribution(lead_lag_analysis: Dict) -> str:
    """Create significance distribution chart"""
    
    companies = list(lead_lag_analysis.keys())
    sig_counts = [a['significant_patterns'] for a in lead_lag_analysis.values()]
    total_counts = [a['total_tested'] for a in lead_lag_analysis.values()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Tests',
        x=[c[:12] for c in companies],
        y=total_counts,
        marker_color='lightblue',
        opacity=0.6
    ))
    
    fig.add_trace(go.Bar(
        name='Significant (p<0.10)',
        x=[c[:12] for c in companies],
        y=sig_counts,
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title='Significant Lead-Lag Patterns: Total vs Significant Tests',
        xaxis_title='Company',
        yaxis_title='Number of Tests',
        barmode='overlay',
        height=400
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_significance")


def _create_chart_17c2_correlation_heatmap(lead_lag_analysis: Dict) -> str:
    """Create heatmap of correlation values"""
    
    companies = list(lead_lag_analysis.keys())[:10]  # Limit for readability
    
    # Build matrix
    metrics = ['Mom→Vol\n(|r|)', 'Short→Long\n(r)']
    
    matrix = []
    for company in companies:
        analysis = lead_lag_analysis[company]
        lead_lag_metrics = analysis.get('lead_lag_metrics', {})
        
        row = []
        
        if 'momentum_leads_volatility' in lead_lag_metrics:
            row.append(abs(lead_lag_metrics['momentum_leads_volatility']['correlation']))
        else:
            row.append(0)
        
        if 'short_term_leads_long_term' in lead_lag_metrics:
            row.append(lead_lag_metrics['short_term_leads_long_term']['correlation'])
        else:
            row.append(0)
        
        matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=metrics,
        y=[c[:12] for c in companies],
        colorscale='RdYlGn',
        zmid=0,
        text=[[f"{val:.3f}" for val in row] for row in matrix],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title='Lead-Lag Correlation Heatmap (Top 10 Companies)',
        height=450
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_heatmap")


# =============================================================================
# ANALYSIS HELPER FUNCTIONS FOR STEP 2
# =============================================================================

def _analyze_multi_timeframe_integration(
    df_prices: pd.DataFrame,
    df_financial: pd.DataFrame,
    df_institutional: pd.DataFrame,
    companies: Dict[str, str],
    price_fundamental_signals: Dict,
    ownership_price_signals: Dict
) -> Dict[str, Dict]:
    """Integrate signals across timeframes - RAW METRICS ONLY"""
    
    multi_timeframe_signals = {}
    
    for company_name in companies.keys():
        try:
            analysis = {
                'daily_significant': 0,
                'daily_total': 0,
                'daily_data_points': 0,
                'quarterly_significant': 0,
                'quarterly_total': 0,
                'quarterly_data_points': 0
            }
            
            # Daily signal metrics (from price-fundamental)
            if company_name in price_fundamental_signals:
                pf_signals = price_fundamental_signals[company_name]
                analysis['daily_significant'] = pf_signals.get('significant_signals', 0)
                analysis['daily_total'] = pf_signals.get('total_signals', 0)
                analysis['daily_data_points'] = pf_signals.get('data_points', 0)
            
            # Quarterly signal metrics (from ownership-price)
            if company_name in ownership_price_signals:
                op_signals = ownership_price_signals[company_name]
                inst_impact = op_signals.get('institutional_impact', {})
                insider_impact = op_signals.get('insider_impact', {})
                
                analysis['quarterly_significant'] = (
                    inst_impact.get('significant_relationships', 0) + 
                    insider_impact.get('significant_relationships', 0)
                )
                analysis['quarterly_total'] = (
                    inst_impact.get('total_tested', 0) + 
                    insider_impact.get('total_tested', 0)
                )
                analysis['quarterly_data_points'] = max(
                    inst_impact.get('data_points', 0),
                    insider_impact.get('data_points', 0)
                )
            
            # Only include if we have data from at least one timeframe
            if analysis['daily_total'] > 0 or analysis['quarterly_total'] > 0:
                multi_timeframe_signals[company_name] = analysis
        
        except Exception as e:
            print(f"Multi-timeframe analysis error for {company_name}: {e}")
            continue
    
    return multi_timeframe_signals


def _analyze_lead_lag_relationships(
    df_prices: pd.DataFrame,
    df_financial: pd.DataFrame,
    df_institutional: pd.DataFrame,
    companies: Dict[str, str],
    multi_timeframe_signals: Dict
) -> Dict[str, Dict]:
    """Analyze lead-lag relationships - RAW CORRELATIONS ONLY"""
    
    lead_lag_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get price data
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            company_prices = company_prices.sort_values('date')
            
            # Calculate returns at different horizons
            company_prices['return_1d'] = company_prices['close'].pct_change() * 100
            company_prices['return_20d'] = company_prices['close'].pct_change(20) * 100
            company_prices['return_60d'] = company_prices['close'].pct_change(60) * 100
            
            # Calculate volatility
            company_prices['vol_60d'] = company_prices['return_1d'].rolling(60).std()
            
            # Analyze lead-lag patterns
            lead_lag_metrics = {}
            sample_size = 0
            
            # Price momentum leading volatility (20-day lead)
            valid_data = company_prices[['return_20d', 'vol_60d']].dropna()
            if len(valid_data) >= 30:
                valid_data = valid_data.copy()
                valid_data['return_20d_lead'] = valid_data['return_20d'].shift(20)
                lead_data = valid_data[['return_20d_lead', 'vol_60d']].dropna()
                
                if len(lead_data) >= 20:
                    corr, pval = stats.pearsonr(lead_data['return_20d_lead'], lead_data['vol_60d'])
                    lead_lag_metrics['momentum_leads_volatility'] = {
                        'correlation': abs(corr),  # Absolute value since direction doesn't matter
                        'p_value': pval,
                        'significant': pval < 0.10,
                        'lead_days': 20,
                        'n': len(lead_data)
                    }
                    sample_size = len(lead_data)
            
            # Short-term returns leading long-term returns (20-day lead)
            valid_data = company_prices[['return_20d', 'return_60d']].dropna()
            if len(valid_data) >= 30:
                valid_data = valid_data.copy()
                valid_data['return_20d_lead'] = valid_data['return_20d'].shift(20)
                lead_data = valid_data[['return_20d_lead', 'return_60d']].dropna()
                
                if len(lead_data) >= 20:
                    corr, pval = stats.pearsonr(lead_data['return_20d_lead'], lead_data['return_60d'])
                    lead_lag_metrics['short_term_leads_long_term'] = {
                        'correlation': corr,
                        'p_value': pval,
                        'significant': pval < 0.10,
                        'lead_days': 20,
                        'n': len(lead_data)
                    }
                    sample_size = max(sample_size, len(lead_data))
            
            # Store results if we have any metrics
            if lead_lag_metrics:
                significant_count = sum(1 for m in lead_lag_metrics.values() if m.get('significant', False))
                
                lead_lag_analysis[company_name] = {
                    'lead_lag_metrics': lead_lag_metrics,
                    'significant_patterns': significant_count,
                    'total_tested': len(lead_lag_metrics),
                    'sample_size': sample_size
                }
        
        except Exception as e:
            print(f"Lead-lag analysis error for {company_name}: {e}")
            continue
    
    return lead_lag_analysis


def _build_section_17e_strategic_insights() -> str:
    """Stub for 17E: Strategic Insights"""
    return """
    <div class="info-box warning">
        <h3>17E: Strategic Cross-Asset Intelligence</h3>
        <p>Coming in Step 4...</p>
    </div>
    """


# =============================================================================
# ANALYSIS HELPER FUNCTIONS
# =============================================================================

def _analyze_price_fundamental_relationships(
    df_prices: pd.DataFrame, 
    df_financial: pd.DataFrame,
    companies: Dict[str, str]
) -> Dict[str, Dict]:
    """Analyze how technical price indicators predict fundamental changes"""
    
    if df_prices.empty or df_financial.empty:
        return {}
    
    price_fundamental_signals = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get company price data
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            company_prices = company_prices.sort_values('date')
            
            # Calculate technical indicators
            company_prices = _calculate_technical_indicators(company_prices)
            
            # Get company financial data
            company_financials = df_financial[df_financial['Company'] == company_name].copy()
            if company_financials.empty:
                continue
            
            if len(company_financials) < 3:
                continue
            
            company_financials = company_financials.sort_values('Year')
            
            # Analyze relationships using ANNUAL data
            relationships = _compute_price_fundamental_correlations_annual(
                company_prices, company_financials
            )
            
            if relationships:
                price_fundamental_signals[company_name] = relationships
        
        except Exception as e:
            print(f"Warning: Price-fundamental analysis failed for {company_name}: {e}")
            continue
    
    return price_fundamental_signals


def _analyze_momentum_fundamental_correlation(
    df_prices: pd.DataFrame, 
    df_financial: pd.DataFrame,
    companies: Dict[str, str],
    price_fundamental_signals: Dict
) -> Dict[str, Dict]:
    """Analyze momentum signals correlation with fundamental performance"""
    
    if not price_fundamental_signals:
        return {}
    
    momentum_analysis = {}
    
    for company_name in price_fundamental_signals.keys():
        try:
            signals = price_fundamental_signals[company_name]
            correlations = signals.get('correlations', {})
            
            # Extract momentum metrics
            momentum_metrics = {
                'momentum_strength': 0,
                'revenue_predictive': False,
                'margin_predictive': False,
                'profitability_predictive': False
            }
            
            # Check momentum-revenue relationship
            if 'momentum_revenue' in correlations:
                mr = correlations['momentum_revenue']
                momentum_metrics['revenue_predictive'] = mr['significant']
                momentum_metrics['momentum_strength'] += abs(mr['correlation']) if mr['significant'] else 0
            
            # Check RSI-margins relationship
            if 'rsi_margins' in correlations:
                rm = correlations['rsi_margins']
                momentum_metrics['margin_predictive'] = rm['significant']
                momentum_metrics['momentum_strength'] += abs(rm['correlation']) if rm['significant'] else 0
            
            # Check volatility-ROE relationship
            if 'volatility_roe' in correlations:
                vr = correlations['volatility_roe']
                momentum_metrics['profitability_predictive'] = vr['significant']
                momentum_metrics['momentum_strength'] += abs(vr['correlation']) if vr['significant'] else 0
            
            momentum_analysis[company_name] = momentum_metrics
        
        except Exception as e:
            print(f"Momentum analysis error for {company_name}: {e}")
            continue
    
    return momentum_analysis


def _analyze_ownership_price_dynamics(
    df_prices: pd.DataFrame, 
    df_institutional: pd.DataFrame,
    df_insider: pd.DataFrame, 
    companies: Dict[str, str]
) -> Dict[str, Dict]:
    """Analyze how institutional and insider activity impacts price movements"""
    
    if df_prices.empty or (df_institutional.empty and df_insider.empty):
        return {}
    
    ownership_price_signals = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get price data
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            company_prices = company_prices.sort_values('date')
            
            analysis = {
                'institutional_impact': {},
                'insider_impact': {},
                'combined_signal': {}
            }
            
            # Analyze institutional flow impact
            if not df_institutional.empty:
                company_inst = df_institutional[df_institutional['Company'] == company_name].copy()
                if not company_inst.empty:
                    inst_impact = _compute_institutional_price_impact(company_prices, company_inst)
                    analysis['institutional_impact'] = inst_impact
            
            # Analyze insider activity impact
            if not df_insider.empty:
                company_insider = df_insider[df_insider['Company'] == company_name].copy()
                if not company_insider.empty:
                    insider_impact = _compute_insider_price_impact(company_prices, company_insider)
                    analysis['insider_impact'] = insider_impact
            
            # Calculate combined signal
            if analysis['institutional_impact'] or analysis['insider_impact']:
                analysis['combined_signal'] = _compute_combined_ownership_signal(analysis)
                ownership_price_signals[company_name] = analysis
        
        except Exception as e:
            print(f"Ownership-price analysis error for {company_name}: {e}")
            continue
    
    return ownership_price_signals


def _analyze_insider_price_response(
    df_prices: pd.DataFrame, 
    df_insider: pd.DataFrame,
    companies: Dict[str, str], 
    ownership_price_signals: Dict
) -> Dict[str, Dict]:
    """Analyze market price response to insider activity"""
    
    if df_insider.empty or df_prices.empty:
        return {}
    
    insider_price_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get insider transactions
            company_insider = df_insider[df_insider['Company'] == company_name].copy()
            if company_insider.empty:
                continue
            
            # Get price data
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_insider['transactionDate'] = pd.to_datetime(company_insider['transactionDate'])
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            
            # Analyze price response to insider transactions
            response_metrics = _compute_insider_transaction_response(company_prices, company_insider)
            
            if response_metrics:
                insider_price_analysis[company_name] = response_metrics
        
        except Exception as e:
            print(f"Insider-price response error for {company_name}: {e}")
            continue
    
    return insider_price_analysis


def _compute_institutional_price_impact(price_df: pd.DataFrame, inst_df: pd.DataFrame) -> Dict:
    """Compute institutional flow impact on price movements using annual aggregation"""
    
    try:
        inst_df = inst_df.copy()
        inst_df['date'] = pd.to_datetime(inst_df['date'])
        inst_df = inst_df.sort_values('date')
        
        # Calculate institutional changes
        inst_df['totalInvested_change'] = inst_df['totalInvested'].diff()
        inst_df['ownershipPercent_change'] = inst_df['ownershipPercent'].diff()
        
        # Extract year from institutional data
        inst_df['year'] = inst_df['date'].dt.year
        
        # Aggregate institutional data by year (use latest quarter per year)
        annual_inst = inst_df.sort_values('date').groupby('year').last().reset_index()
        
        # Calculate annual returns from price data
        price_df = price_df.copy()
        price_df['year'] = pd.to_datetime(price_df['date']).dt.year
        annual_returns = price_df.groupby('year').agg({'close': 'last'}).reset_index()
        annual_returns['annual_return'] = annual_returns['close'].pct_change() * 100
        
        # Merge institutional changes with returns
        merged = pd.merge(annual_inst, annual_returns, on='year', how='inner')
        
        if len(merged) < 3:
            return {}
        
        # Compute correlations
        correlations = {}
        
        # Total invested vs returns
        valid = merged[['totalInvested_change', 'annual_return']].dropna()
        if len(valid) >= 3:
            corr, pval = stats.pearsonr(valid['totalInvested_change'], valid['annual_return'])
            correlations['flow_return'] = {
                'correlation': corr,
                'p_value': pval,
                'significant': pval < 0.15
            }
        
        # Ownership change vs returns
        valid = merged[['ownershipPercent_change', 'annual_return']].dropna()
        if len(valid) >= 3:
            corr, pval = stats.pearsonr(valid['ownershipPercent_change'], valid['annual_return'])
            correlations['ownership_return'] = {
                'correlation': corr,
                'p_value': pval,
                'significant': pval < 0.15
            }
        
        # Calculate impact score
        significant_count = sum(1 for c in correlations.values() if c.get('significant', False))
        impact_score = (significant_count / len(correlations)) if correlations else 0
        
        return {
            'correlations': correlations,
            'impact_score': impact_score,
            'significant_relationships': significant_count,
            'total_tested': len(correlations),
            'data_points': len(merged)
        }
    
    except Exception as e:
        return {}


def _compute_insider_price_impact(price_df: pd.DataFrame, insider_df: pd.DataFrame) -> Dict:
    """Compute insider activity impact on price movements"""
    
    try:
        insider_df = insider_df.copy()
        insider_df['transactionDate'] = pd.to_datetime(insider_df['transactionDate'])
        insider_df = insider_df.sort_values('transactionDate')
        
        # Classify transactions
        insider_df['is_buy'] = insider_df['acquisitionOrDisposition'] == 'A'
        insider_df['is_sell'] = insider_df['acquisitionOrDisposition'] == 'D'
        
        # Aggregate by month
        insider_df['month'] = insider_df['transactionDate'].dt.to_period('M')
        
        monthly_insider = insider_df.groupby('month').agg({
            'is_buy': 'sum',
            'is_sell': 'sum',
            'securitiesTransacted': 'sum'
        }).reset_index()
        
        monthly_insider['net_activity'] = monthly_insider['is_buy'] - monthly_insider['is_sell']
        
        # Calculate monthly returns
        price_df['month'] = price_df['date'].dt.to_period('M')
        monthly_returns = price_df.groupby('month').agg({
            'close': 'last'
        }).reset_index()
        monthly_returns['monthly_return'] = monthly_returns['close'].pct_change() * 100
        
        # Merge
        merged = pd.merge(monthly_insider, monthly_returns, on='month', how='inner')
        
        if len(merged) < 6:
            return {}
        
        # Compute correlations with lag (insider activity leading price)
        correlations = {}
        
        # Net activity vs future returns
        merged['net_activity_lag'] = merged['net_activity'].shift(1)
        valid = merged[['net_activity_lag', 'monthly_return']].dropna()
        
        if len(valid) >= 4:
            corr, pval = stats.pearsonr(valid['net_activity_lag'], valid['monthly_return'])
            correlations['insider_activity_lead'] = {
                'correlation': corr,
                'p_value': pval,
                'significant': pval < 0.10
            }
        
        # Calculate impact score
        significant_count = sum(1 for c in correlations.values() if c.get('significant', False))
        impact_score = (significant_count / len(correlations)) if correlations else 0
        
        return {
            'correlations': correlations,
            'impact_score': impact_score,
            'significant_relationships': significant_count,
            'total_tested': len(correlations),
            'data_points': len(merged)
        }
    
    except Exception as e:
        print(f"Insider impact computation error: {e}")
        return {}


def _compute_combined_ownership_signal(analysis: Dict) -> Dict:
    """Compute combined ownership signal"""
    
    inst_impact = analysis.get('institutional_impact', {})
    insider_impact = analysis.get('insider_impact', {})
    
    # Calculate combined score
    inst_score = inst_impact.get('impact_score', 0) if inst_impact else 0
    insider_score = insider_impact.get('impact_score', 0) if insider_impact else 0
    
    combined_score = (inst_score + insider_score) / 2 if (inst_impact and insider_impact) else max(inst_score, insider_score)
    
    return {
        'combined_score': combined_score,
        'institutional_score': inst_score,
        'insider_score': insider_score
    }


def _compute_insider_transaction_response(price_df: pd.DataFrame, insider_df: pd.DataFrame) -> Dict:
    """Compute price response to insider transactions"""
    
    try:
        # Focus on significant transactions
        insider_df = insider_df.copy()
        insider_df['transaction_value'] = insider_df['securitiesTransacted'] * insider_df['price']
        
        # Filter for substantial transactions (top 50% by value)
        value_threshold = insider_df['transaction_value'].quantile(0.5)
        significant_transactions = insider_df[insider_df['transaction_value'] >= value_threshold].copy()
        
        if len(significant_transactions) < 5:
            return {}
        
        # Calculate returns following insider activity
        buy_returns = []
        sell_returns = []
        
        for idx, transaction in significant_transactions.iterrows():
            trans_date = transaction['transactionDate']
            is_buy = transaction['acquisitionOrDisposition'] == 'A'
            
            # Get price at transaction and 30/60 days after
            future_prices = price_df[price_df['date'] > trans_date].head(60)
            if len(future_prices) >= 30:
                price_at_trans = price_df[price_df['date'] <= trans_date]['close'].iloc[-1] if len(price_df[price_df['date'] <= trans_date]) > 0 else np.nan
                price_30d = future_prices.iloc[29]['close'] if len(future_prices) > 29 else np.nan
                price_60d = future_prices.iloc[-1]['close']
                
                if not np.isnan(price_at_trans) and not np.isnan(price_30d):
                    return_30d = ((price_30d - price_at_trans) / price_at_trans) * 100
                    return_60d = ((price_60d - price_at_trans) / price_at_trans) * 100
                    
                    if is_buy:
                        buy_returns.append({'return_30d': return_30d, 'return_60d': return_60d})
                    else:
                        sell_returns.append({'return_30d': return_30d, 'return_60d': return_60d})
        
        # Calculate average returns
        metrics = {}
        
        if buy_returns:
            buy_df = pd.DataFrame(buy_returns)
            metrics['buy_transactions'] = len(buy_returns)
            metrics['avg_return_30d_after_buy'] = buy_df['return_30d'].mean()
            metrics['avg_return_60d_after_buy'] = buy_df['return_60d'].mean()
            metrics['buy_success_rate'] = (buy_df['return_30d'] > 0).sum() / len(buy_df)
        
        if sell_returns:
            sell_df = pd.DataFrame(sell_returns)
            metrics['sell_transactions'] = len(sell_returns)
            metrics['avg_return_30d_after_sell'] = sell_df['return_30d'].mean()
            metrics['avg_return_60d_after_sell'] = sell_df['return_60d'].mean()
        
        # Calculate signal quality
        if buy_returns:
            buy_signal_quality = 1.0 if metrics['avg_return_30d_after_buy'] > 0 and metrics['buy_success_rate'] > 0.5 else 0.5
        else:
            buy_signal_quality = 0
        
        metrics['signal_quality'] = buy_signal_quality
        
        return metrics
    
    except Exception as e:
        print(f"Insider transaction response error: {e}")
        return {}


def _calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for price data"""
    
    df = df.copy()
    
    # Moving averages
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['SMA_200'] = df['close'].rolling(window=200).mean()
    
    # Momentum indicators
    df['ROC_20'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20)) * 100
    df['ROC_60'] = ((df['close'] - df['close'].shift(60)) / df['close'].shift(60)) * 100
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Volatility
    df['volatility_20'] = df['close'].pct_change().rolling(window=20).std() * np.sqrt(252) * 100
    
    # Volume indicators
    if 'volume' in df.columns:
        df['volume_SMA_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_SMA_20']
    
    return df


def _compute_price_fundamental_correlations_annual(
    price_df: pd.DataFrame, 
    financial_df: pd.DataFrame
) -> Dict:
    """Compute correlations between technical indicators and fundamental changes using ANNUAL data"""
    
    try:
        # Create annual price metrics by aggregating daily data by year
        price_df = price_df.copy()
        price_df['year'] = price_df['date'].dt.year
        
        # Aggregate price metrics by year (using year-end values and averages)
        annual_price = price_df.groupby('year').agg({
            'close': 'last',  # Year-end closing price
            'ROC_20': 'mean',
            'ROC_60': 'mean',
            'RSI': 'mean',
            'MACD': 'mean',
            'volatility_20': 'mean',
            'volume_ratio': 'mean'
        }).reset_index()
        
        # Calculate annual returns
        annual_price['annual_return'] = annual_price['close'].pct_change() * 100
        
        # Merge with annual financials
        financial_df = financial_df.copy()
        financial_df['year'] = financial_df['Year']
        
        merged = pd.merge(annual_price, financial_df, on='year', how='inner')
        
        if len(merged) < 4:
            return {}
        
        # Calculate fundamental changes (year-over-year)
        merged['revenue_growth_yoy'] = merged['revenue'].pct_change() * 100
        merged['margin_change'] = merged['netProfitMargin'].diff()
        merged['roe_change'] = merged['returnOnEquity'].diff()
        
        # Shift technical indicators to test predictive power (lag by 1 year)
        for col in ['ROC_20', 'ROC_60', 'RSI', 'MACD', 'volatility_20', 'annual_return']:
            if col in merged.columns:
                merged[f'{col}_lag1'] = merged[col].shift(1)
        
        # Calculate correlations
        correlations = {}
        
        # Price momentum predicting revenue growth
        valid_data = merged[['ROC_60_lag1', 'revenue_growth_yoy']].dropna()
        if len(valid_data) >= 3:
            corr, pval = stats.pearsonr(valid_data['ROC_60_lag1'], valid_data['revenue_growth_yoy'])
            correlations['momentum_revenue'] = {
                'correlation': corr,
                'p_value': pval,
                'n': len(valid_data),
                'significant': pval < 0.15  # Relaxed threshold for annual data
            }
        
        # RSI predicting margin changes
        valid_data = merged[['RSI_lag1', 'margin_change']].dropna()
        if len(valid_data) >= 3:
            corr, pval = stats.pearsonr(valid_data['RSI_lag1'], valid_data['margin_change'])
            correlations['rsi_margins'] = {
                'correlation': corr,
                'p_value': pval,
                'n': len(valid_data),
                'significant': pval < 0.15
            }
        
        # Volatility predicting ROE changes
        valid_data = merged[['volatility_20_lag1', 'roe_change']].dropna()
        if len(valid_data) >= 3:
            corr, pval = stats.pearsonr(valid_data['volatility_20_lag1'], valid_data['roe_change'])
            correlations['volatility_roe'] = {
                'correlation': corr,
                'p_value': pval,
                'n': len(valid_data),
                'significant': pval < 0.15
            }
        
        if not correlations:
            return {}
        
        # Calculate metrics
        significant_signals = sum(1 for sig in correlations.values() if sig.get('significant', False))
        
        return {
            'correlations': correlations,
            'significant_signals': significant_signals,
            'total_signals': len(correlations),
            'data_points': len(merged)
        }
    
    except Exception as e:
        return {}