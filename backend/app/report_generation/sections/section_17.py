"""Section 17: Cross-Asset Signal Discovery - Phase 1"""

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
    
    # Perform analysis for 17A.1
    price_fundamental_signals = _analyze_price_fundamental_relationships(
        df_prices, df_financial, companies
    )
    
    momentum_analysis  = _analyze_momentum_fundamental_correlation(df_prices, df_financial, companies, price_fundamental_signals)
    
    ownership_signals = _analyze_ownership_price_dynamics(df_prices, df_institutional, df_insider,companies)

    insider_price_analysis = _analyze_insider_price_response(
        df_prices, df_insider, companies
    )
    
    multi_timeframe_signals = _analyze_multi_timeframe_integration(
        df_prices, df_financial, df_institutional, companies, 
        price_fundamental_signals, ownership_signals
    )
    
    lead_lag_analysis = _analyze_lead_lag_relationships(
        df_prices, df_financial, df_institutional, companies
    )
    
    # Prepare data for strategic insights
    all_analyses = {
        'price_fundamental': price_fundamental_signals,
        'momentum_fundamental': momentum_analysis,
        'ownership_price': ownership_signals,
        'insider_response': insider_price_analysis,
        'multi_timeframe': multi_timeframe_signals,
        'lead_lag': lead_lag_analysis
    }


    # Build subsections
    section_17a1_html = _build_section_17a1_price_fundamental(
        price_fundamental_signals, companies
    )
    
    # Stubs for remaining subsections
    section_17a2_html = _build_section_17a2_momentum_fundamental(momentum_analysis,companies,price_fundamental_signals)
    section_17b1_html = _build_section_17b1_institutional_flow(ownership_signals, companies)
    section_17b2_html = _build_section_17b2_insider_response(insider_price_analysis, companies)
    section_17c1_html = _build_section_17c1_multi_timeframe(multi_timeframe_signals, companies)
    section_17c2_html = _build_section_17c2_lead_lag(
        lead_lag_analysis, companies
    )
    
    section_17e_html = _build_section_17e_strategic_insights(
        all_analyses, companies
    )
    
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
            <p><em>Analysis focuses on statistical relationships, correlation strengths, percentile rankings, 
            and multi-dimensional visualizations. No arbitrary composite scores are used.</em></p>
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
# 17A.1: PRICE-FUNDAMENTAL RELATIONSHIPS (FULLY IMPLEMENTED)
# =============================================================================

def _build_section_17a1_price_fundamental(
    price_fundamental_signals: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17A.1: Price-Fundamental Relationships subsection - NO ARBITRARY SCORES"""
    
    if not price_fundamental_signals:
        return """
        <div class="info-box warning">
            <h3>17A.1: Price-Fundamental Relationships</h3>
            <p>Insufficient data available for price-fundamental relationship analysis.</p>
        </div>
        """
    
    # Calculate raw metrics
    total_companies = len(price_fundamental_signals)
    
    all_correlations = []
    all_pvalues = []
    significant_count = 0
    total_tests = 0
    
    for signals in price_fundamental_signals.values():
        correlations = signals.get('correlations', {})
        for corr_data in correlations.values():
            all_correlations.append(corr_data['correlation'])
            all_pvalues.append(corr_data['p_value'])
            total_tests += 1
            if corr_data.get('significant', False):
                significant_count += 1
    
    # Calculate distribution statistics
    avg_abs_corr = np.mean([abs(c) for c in all_correlations]) if all_correlations else 0
    median_abs_corr = np.median([abs(c) for c in all_correlations]) if all_correlations else 0
    significance_rate = (significant_count / total_tests * 100) if total_tests > 0 else 0
    
    # Calculate percentiles for context
    if all_correlations:
        corr_25th = np.percentile([abs(c) for c in all_correlations], 25)
        corr_75th = np.percentile([abs(c) for c in all_correlations], 75)
    else:
        corr_25th = corr_75th = 0
    
    # Summary cards - RAW METRICS ONLY
    summary_cards = [
        {
            "label": "Companies Analyzed",
            "value": str(total_companies),
            "description": f"{total_tests} correlation tests performed",
            "type": "info"
        },
        {
            "label": "Significant Relationships",
            "value": f"{significant_count}/{total_tests}",
            "description": f"{significance_rate:.1f}% significance rate (p<0.15)",
            "type": "success" if significance_rate >= 40 else "warning" if significance_rate >= 25 else "default"
        },
        {
            "label": "Median |Correlation|",
            "value": f"{median_abs_corr:.3f}",
            "description": f"IQR: [{corr_25th:.3f}, {corr_75th:.3f}]",
            "type": "success" if median_abs_corr >= 0.4 else "info"
        },
        {
            "label": "Avg Data Points",
            "value": str(int(np.mean([s['data_points'] for s in price_fundamental_signals.values()]))),
            "description": "Annual observations per company",
            "type": "default"
        }
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create detailed correlation table
    table_data = []
    for company_name, signals in price_fundamental_signals.items():
        correlations = signals.get('correlations', {})
        
        row = {'Company': company_name}
        
        # Momentum → Revenue
        if 'momentum_revenue' in correlations:
            mr = correlations['momentum_revenue']
            row['Mom→Rev (r)'] = f"{mr['correlation']:.3f}"
            row['Mom→Rev (p)'] = f"{mr['p_value']:.3f}"
            row['Mom→Rev Sig'] = "✓" if mr['significant'] else "✗"
        else:
            row['Mom→Rev (r)'] = "—"
            row['Mom→Rev (p)'] = "—"
            row['Mom→Rev Sig'] = "—"
        
        # RSI → Margins
        if 'rsi_margins' in correlations:
            rm = correlations['rsi_margins']
            row['RSI→Margin (r)'] = f"{rm['correlation']:.3f}"
            row['RSI→Margin (p)'] = f"{rm['p_value']:.3f}"
            row['RSI→Margin Sig'] = "✓" if rm['significant'] else "✗"
        else:
            row['RSI→Margin (r)'] = "—"
            row['RSI→Margin (p)'] = "—"
            row['RSI→Margin Sig'] = "—"
        
        # Volatility → ROE
        if 'volatility_roe' in correlations:
            vr = correlations['volatility_roe']
            row['Vol→ROE (r)'] = f"{vr['correlation']:.3f}"
            row['Vol→ROE (p)'] = f"{vr['p_value']:.3f}"
            row['Vol→ROE Sig'] = "✓" if vr['significant'] else "✗"
        else:
            row['Vol→ROE (r)'] = "—"
            row['Vol→ROE (p)'] = "—"
            row['Vol→ROE Sig'] = "—"
        
        row['Sig/Total'] = f"{signals['significant_signals']}/{signals['total_signals']}"
        row['N (years)'] = signals['data_points']
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    # Color coding for significance
    def sig_color(val):
        if val == "✓":
            return "excellent"
        elif val == "✗":
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
    
    # Create enhanced visualizations
    chart1 = _create_chart_17a1_correlation_distribution(price_fundamental_signals)
    chart2 = _create_chart_17a1_correlation_heatmap_enhanced(price_fundamental_signals)
    chart3 = _create_chart_17a1_percentile_ranking(price_fundamental_signals, all_correlations)
    chart4 = _create_chart_17a1_pvalue_confidence(price_fundamental_signals)
    chart5 = _create_chart_17a1_correlation_strength_bars(price_fundamental_signals)
    chart6 = _create_chart_17a1_significance_scatter(price_fundamental_signals)
    
    # Build collapsible section with toggle
    subsection_html = f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17a1')">
            <span>17A.1: Price-Fundamental Relationships - Technical Indicators as Leading Signals</span>
            <span id="icon_17a1" style="transition: transform 0.3s;">▼</span>
        </h3>
        
        <div id="section_17a1" style="display: block;">
            <p><strong>Analysis:</strong> Tests whether technical price indicators (momentum, RSI, volatility) 
            predict fundamental changes in revenue, margins, and profitability using lagged annual correlations. 
            Shows raw correlation coefficients, p-values, and percentile rankings—no composite scores.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Detailed Correlation Analysis by Company</h4>
            <p><em>Note: All correlations use 1-year lag (t-1 → t) to test predictive power. 
            Significance threshold: p < 0.15 (relaxed for annual data with limited observations). 
            ✓ = significant, ✗ = not significant.</em></p>
            {table_html}
            
            <h4>Multi-Dimensional Visualizations</h4>
            
            <div style="margin: 20px 0;">
                <h5>Correlation Distribution & Strength Analysis</h5>
                <p><em>Understanding the distribution and strength of predictive relationships</em></p>
                {chart1}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Correlation Heatmap with Gradient Intensity</h5>
                <p><em>Visual comparison of correlation strengths across companies and relationships</em></p>
                {chart2}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Percentile Rankings vs Portfolio</h5>
                <p><em>Where each company ranks in correlation strength relative to peers</em></p>
                {chart3}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Statistical Confidence Analysis</h5>
                <p><em>Relationship between correlation strength and statistical significance</em></p>
                {chart4}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Absolute Correlation Strength Comparison</h5>
                <p><em>Direct comparison of |correlation| magnitudes across all relationships</em></p>
                {chart5}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Multi-Dimensional Scatter: Strength vs Significance</h5>
                <p><em>Combined view showing both correlation magnitude and reliability</em></p>
                {chart6}
            </div>
            
            <div class="info-box info">
                <h4>Interpretation Guidelines</h4>
                <ul>
                    <li><strong>Correlation (r):</strong> Ranges from -1 to +1. Values closer to ±1 indicate stronger linear relationships</li>
                    <li><strong>|Correlation|:</strong> Absolute value indicates strength regardless of direction</li>
                    <li><strong>P-value:</strong> Statistical significance. Values < 0.15 considered significant (relaxed threshold for annual data)</li>
                    <li><strong>Percentile Rank:</strong> Shows relative position within portfolio. 75th percentile = top 25%</li>
                    <li><strong>Sample Size (N):</strong> Years of data used. More observations = more reliable correlations</li>
                    <li><strong>Momentum→Revenue:</strong> 60-day price momentum (year t-1) predicting next year's revenue growth (year t)</li>
                    <li><strong>RSI→Margins:</strong> RSI levels (year t-1) predicting next year's margin changes (year t)</li>
                    <li><strong>Volatility→ROE:</strong> Price volatility (year t-1) predicting next year's ROE changes (year t)</li>
                </ul>
            </div>
            
            <div class="info-box default">
                <h4>Statistical Context</h4>
                <p><strong>Distribution Summary:</strong></p>
                <ul>
                    <li>Median absolute correlation: {median_abs_corr:.3f}</li>
                    <li>Interquartile range: [{corr_25th:.3f}, {corr_75th:.3f}]</li>
                    <li>25th percentile (weak): |r| < {corr_25th:.3f}</li>
                    <li>50th percentile (moderate): |r| ≈ {median_abs_corr:.3f}</li>
                    <li>75th percentile (strong): |r| > {corr_75th:.3f}</li>
                </ul>
                <p><strong>Significance Rate:</strong> {significance_rate:.1f}% of all correlations are statistically significant at p < 0.15</p>
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
    """Create enhanced correlation distribution with multiple views"""
    
    all_correlations = []
    relationship_types = []
    
    for company, data in signals.items():
        correlations = data.get('correlations', {})
        
        if 'momentum_revenue' in correlations:
            all_correlations.append(correlations['momentum_revenue']['correlation'])
            relationship_types.append('Mom→Rev')
        
        if 'rsi_margins' in correlations:
            all_correlations.append(correlations['rsi_margins']['correlation'])
            relationship_types.append('RSI→Margin')
        
        if 'volatility_roe' in correlations:
            all_correlations.append(correlations['volatility_roe']['correlation'])
            relationship_types.append('Vol→ROE')
    
    if not all_correlations:
        return ""
    
    # Create histogram with enhanced features
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=all_correlations,
        nbinsx=20,
        marker=dict(
            color='rgba(102, 126, 234, 0.7)',
            line=dict(color='rgba(102, 126, 234, 1)', width=1)
        ),
        name='All Correlations',
        hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add vertical lines for key statistics
    mean_corr = np.mean(all_correlations)
    median_corr = np.median(all_correlations)
    
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=2, opacity=0.5,
                  annotation_text="Zero", annotation_position="top")
    fig.add_vline(x=median_corr, line_dash="dash", line_color="red", line_width=2,
                  annotation_text=f"Median: {median_corr:.3f}", annotation_position="top")
    fig.add_vline(x=mean_corr, line_dash="dot", line_color="blue", line_width=2,
                  annotation_text=f"Mean: {mean_corr:.3f}", annotation_position="bottom")
    
    # Add shaded regions for strength interpretation
    fig.add_vrect(x0=-0.3, x1=0.3, fillcolor="gray", opacity=0.1, 
                  annotation_text="Weak", annotation_position="top left")
    fig.add_vrect(x0=0.3, x1=1, fillcolor="green", opacity=0.1,
                  annotation_text="Moderate-Strong", annotation_position="top right")
    fig.add_vrect(x0=-1, x1=-0.3, fillcolor="green", opacity=0.1,
                  annotation_text="Moderate-Strong", annotation_position="top left")
    
    fig.update_layout(
        title='Distribution of Price-Fundamental Correlations with Statistical References',
        xaxis_title='Correlation Coefficient (r)',
        yaxis_title='Frequency',
        showlegend=False,
        height=450,
        hovermode='closest'
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_corr_dist")


def _create_chart_17a1_correlation_heatmap_enhanced(signals: Dict) -> str:
    """Create enhanced correlation heatmap with gradient intensity and annotations"""
    
    companies = list(signals.keys())[:15]  # Top 15 for readability
    relationship_types = ['Momentum→Revenue', 'RSI→Margins', 'Volatility→ROE']
    
    # Build correlation matrix
    corr_matrix = []
    annotation_matrix = []
    
    for company in companies:
        row = []
        annot_row = []
        correlations = signals[company].get('correlations', {})
        
        for rel_key in ['momentum_revenue', 'rsi_margins', 'volatility_roe']:
            if rel_key in correlations:
                corr_val = correlations[rel_key]['correlation']
                is_sig = correlations[rel_key]['significant']
                row.append(corr_val)
                annot_row.append(f"{corr_val:.3f}{'*' if is_sig else ''}")
            else:
                row.append(0)
                annot_row.append("—")
        
        corr_matrix.append(row)
        annotation_matrix.append(annot_row)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=relationship_types,
        y=[c[:15] for c in companies],
        colorscale='RdYlGn',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=annotation_matrix,
        texttemplate='%{text}',
        textfont={"size": 9},
        colorbar=dict(title="Correlation<br>Coefficient"),
        hovertemplate='Company: %{y}<br>Relationship: %{x}<br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Price-Fundamental Correlation Heatmap (Top 15 Companies)<br><sub>* indicates p < 0.15 significance</sub>',
        height=600,
        xaxis=dict(side='top')
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_heatmap")


def _create_chart_17a1_percentile_ranking(signals: Dict, all_correlations: List[float]) -> str:
    """Create percentile ranking visualization"""
    
    if not all_correlations:
        return ""
    
    # Calculate percentiles for each company
    companies = []
    percentiles = []
    avg_abs_corrs = []
    
    for company, data in signals.items():
        correlations = data.get('correlations', {})
        company_corrs = [abs(c['correlation']) for c in correlations.values()]
        
        if company_corrs:
            avg_abs_corr = np.mean(company_corrs)
            # Calculate percentile rank
            percentile = stats.percentileofscore([abs(c) for c in all_correlations], avg_abs_corr)
            
            companies.append(company[:15])
            percentiles.append(percentile)
            avg_abs_corrs.append(avg_abs_corr)
    
    # Sort by percentile
    sorted_indices = np.argsort(percentiles)[::-1]
    companies = [companies[i] for i in sorted_indices]
    percentiles = [percentiles[i] for i in sorted_indices]
    avg_abs_corrs = [avg_abs_corrs[i] for i in sorted_indices]
    
    # Color by quartile
    colors = []
    for p in percentiles:
        if p >= 75:
            colors.append('#10b981')  # Green - top quartile
        elif p >= 50:
            colors.append('#3b82f6')  # Blue - upper middle
        elif p >= 25:
            colors.append('#f59e0b')  # Orange - lower middle
        else:
            colors.append('#ef4444')  # Red - bottom quartile
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=companies,
        x=percentiles,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{p:.0f}th %ile<br>|r|={c:.3f}" for p, c in zip(percentiles, avg_abs_corrs)],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Percentile: %{x:.1f}<br>Avg |r|: %{text}<extra></extra>'
    ))
    
    # Add reference lines for quartiles
    fig.add_vline(x=25, line_dash="dot", line_color="gray", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="Median")
    fig.add_vline(x=75, line_dash="dot", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title='Percentile Rankings: Average Absolute Correlation Strength vs Portfolio',
        xaxis_title='Percentile Rank',
        yaxis_title='Company',
        height=max(400, len(companies) * 25),
        showlegend=False
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_percentile")


def _create_chart_17a1_pvalue_confidence(signals: Dict) -> str:
    """Create correlation vs p-value scatter with confidence regions"""
    
    correlations = []
    pvalues = []
    labels = []
    colors = []
    sizes = []
    
    for company, data in signals.items():
        corrs = data.get('correlations', {})
        
        for rel_name, rel_key in [('Mom→Rev', 'momentum_revenue'), 
                                   ('RSI→Mgn', 'rsi_margins'), 
                                   ('Vol→ROE', 'volatility_roe')]:
            if rel_key in corrs:
                r = corrs[rel_key]['correlation']
                p = corrs[rel_key]['p_value']
                n = corrs[rel_key]['n']
                sig = corrs[rel_key]['significant']
                
                correlations.append(r)
                pvalues.append(p)
                labels.append(f"{company[:12]} - {rel_name}")
                colors.append('green' if sig else 'lightgray')
                sizes.append(min(15, max(5, n)))  # Size by sample size
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=correlations,
        y=pvalues,
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=1, color='black'),
            opacity=0.7
        ),
        text=labels,
        hovertemplate='%{text}<br>r = %{x:.3f}<br>p = %{y:.4f}<br>Size ∝ N<extra></extra>'
    ))
    
    # Add significance threshold line
    fig.add_hline(y=0.15, line_dash="dash", line_color="red", line_width=2,
                  annotation_text="p = 0.15 significance threshold", annotation_position="right")
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="solid", line_color="gray", opacity=0.3)
    
    # Add shaded region for high confidence
    fig.add_hrect(y0=0, y1=0.15, fillcolor="green", opacity=0.1,
                  annotation_text="High Confidence", annotation_position="top right")
    
    fig.update_layout(
        title='Statistical Confidence: Correlation Strength vs P-value<br><sub>Marker size proportional to sample size (N). Green = significant (p<0.15)</sub>',
        xaxis_title='Correlation Coefficient (r)',
        yaxis_title='P-value (log scale)',
        yaxis_type='log',
        height=500
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_pvalue")


def _create_chart_17a1_correlation_strength_bars(signals: Dict) -> str:
    """Create absolute correlation strength comparison bars"""
    
    companies = []
    mom_rev = []
    rsi_mgn = []
    vol_roe = []
    
    for company, data in signals.items():
        correlations = data.get('correlations', {})
        companies.append(company[:12])
        
        mom_rev.append(abs(correlations['momentum_revenue']['correlation']) 
                      if 'momentum_revenue' in correlations else 0)
        rsi_mgn.append(abs(correlations['rsi_margins']['correlation']) 
                      if 'rsi_margins' in correlations else 0)
        vol_roe.append(abs(correlations['volatility_roe']['correlation']) 
                      if 'volatility_roe' in correlations else 0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='|Mom→Rev|',
        x=companies,
        y=mom_rev,
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='|RSI→Margin|',
        x=companies,
        y=rsi_mgn,
        marker_color='#9b59b6'
    ))
    
    fig.add_trace(go.Bar(
        name='|Vol→ROE|',
        x=companies,
        y=vol_roe,
        marker_color='#e74c3c'
    ))
    
    # Add reference lines for interpretation
    fig.add_hline(y=0.3, line_dash="dot", line_color="orange", opacity=0.5,
                  annotation_text="Moderate (0.3)", annotation_position="right")
    fig.add_hline(y=0.5, line_dash="dot", line_color="green", opacity=0.5,
                  annotation_text="Strong (0.5)", annotation_position="right")
    
    fig.update_layout(
        title='Absolute Correlation Strength Comparison by Relationship Type',
        xaxis_title='Company',
        yaxis_title='|Correlation Coefficient|',
        barmode='group',
        height=450,
        hovermode='x unified'
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_strength_bars")


def _create_chart_17a1_significance_scatter(signals: Dict) -> str:
    """Create multi-dimensional scatter: correlation strength vs data quality"""
    
    companies = []
    avg_abs_corr = []
    sig_rate = []
    sample_sizes = []
    
    for company, data in signals.items():
        correlations = data.get('correlations', {})
        
        corr_vals = [abs(c['correlation']) for c in correlations.values()]
        sig_count = sum(1 for c in correlations.values() if c['significant'])
        total_tests = len(correlations)
        
        if corr_vals:
            companies.append(company[:15])
            avg_abs_corr.append(np.mean(corr_vals))
            sig_rate.append(sig_count / total_tests * 100)
            sample_sizes.append(data['data_points'])
    
    # Color by significance rate
    colors = []
    for sr in sig_rate:
        if sr >= 66:
            colors.append('#10b981')  # Green
        elif sr >= 33:
            colors.append('#f59e0b')  # Orange
        else:
            colors.append('#ef4444')  # Red
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=avg_abs_corr,
        y=sig_rate,
        mode='markers',
        marker=dict(
            size=[min(20, max(5, n)) for n in sample_sizes],
            color=colors,
            line=dict(width=1, color='black'),
            opacity=0.7
        ),
        text=[f"{c}<br>N={n} years" for c, n in zip(companies, sample_sizes)],
        hovertemplate='%{text}<br>Avg |r|: %{x:.3f}<br>Sig Rate: %{y:.0f}%<extra></extra>'
    ))
    
    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0.3, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=0.15, y=75, text="Weak but<br>Reliable", showarrow=False, opacity=0.5)
    fig.add_annotation(x=0.5, y=75, text="Strong &<br>Reliable", showarrow=False, opacity=0.5)
    fig.add_annotation(x=0.15, y=25, text="Weak &<br>Unreliable", showarrow=False, opacity=0.5)
    fig.add_annotation(x=0.5, y=25, text="Strong but<br>Unreliable", showarrow=False, opacity=0.5)
    
    fig.update_layout(
        title='Multi-Dimensional View: Correlation Strength vs Significance Rate<br><sub>Marker size ∝ sample size. Color: Green=majority significant, Orange=mixed, Red=majority not significant</sub>',
        xaxis_title='Average Absolute Correlation |r|',
        yaxis_title='Significance Rate (%)',
        height=500
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a1_scatter")


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
            'close': 'last',
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
                'significant': pval < 0.15
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


# =============================================================================
# STUB FUNCTIONS FOR PHASE 2-4
# =============================================================================

"""
Section 17 Phase 2 - NEW CODE ONLY
Add these functions to the Phase 1 file and update the generate() function
"""

# =============================================================================
# UPDATE THE generate() FUNCTION - Replace the stub calls with these:
# =============================================================================
"""
In generate() function, replace these lines:

    section_17a2_html = _build_section_17a2_momentum_fundamental()
    section_17b1_html = _build_section_17b1_institutional_flow()

With these lines:

    momentum_fundamental_analysis = _analyze_momentum_fundamental_correlation(
        df_prices, df_financial, companies, price_fundamental_signals
    )
    
    ownership_price_signals = _analyze_ownership_price_dynamics(
        df_prices, df_institutional, df_insider, companies
    )
    
    section_17a2_html = _build_section_17a2_momentum_fundamental(
        momentum_fundamental_analysis, companies, price_fundamental_signals
    )
    
    section_17b1_html = _build_section_17b1_institutional_flow(
        ownership_price_signals, companies
    )
"""


# =============================================================================
# 17A.2: MOMENTUM-FUNDAMENTAL CORRELATION (NEW)
# =============================================================================

def _build_section_17a2_momentum_fundamental(
    momentum_analysis: Dict,
    companies: Dict[str, str],
    price_fundamental_signals: Dict
) -> str:
    """Build 17A.2: Momentum-Fundamental Correlation - NO MOMENTUM STRENGTH SCORE"""
    
    if not momentum_analysis:
        return """
        <div class="info-box warning">
            <h3>17A.2: Momentum-Fundamental Correlation Analysis</h3>
            <p>Momentum-fundamental correlation analysis unavailable.</p>
        </div>
        """
    
    # Summary statistics - RAW COUNTS ONLY
    total_companies = len(momentum_analysis)
    revenue_pred_count = sum(1 for m in momentum_analysis.values() if m.get('revenue_predictive', False))
    margin_pred_count = sum(1 for m in momentum_analysis.values() if m.get('margin_predictive', False))
    profit_pred_count = sum(1 for m in momentum_analysis.values() if m.get('profitability_predictive', False))
    
    # Calculate average correlation strengths (not arbitrary sums)
    all_revenue_corrs = [m.get('revenue_correlation', 0) for m in momentum_analysis.values() if 'revenue_correlation' in m]
    all_margin_corrs = [m.get('margin_correlation', 0) for m in momentum_analysis.values() if 'margin_correlation' in m]
    all_profit_corrs = [m.get('profit_correlation', 0) for m in momentum_analysis.values() if 'profit_correlation' in m]
    
    avg_revenue_corr = np.mean([abs(c) for c in all_revenue_corrs]) if all_revenue_corrs else 0
    avg_margin_corr = np.mean([abs(c) for c in all_margin_corrs]) if all_margin_corrs else 0
    avg_profit_corr = np.mean([abs(c) for c in all_profit_corrs]) if all_profit_corrs else 0
    
    # Summary cards
    summary_cards = [
        {"label": "Revenue Predictive", "value": f"{revenue_pred_count}/{total_companies}", 
         "description": f"Avg |r|: {avg_revenue_corr:.3f}", "type": "success" if revenue_pred_count >= total_companies * 0.5 else "info"},
        {"label": "Margin Predictive", "value": f"{margin_pred_count}/{total_companies}", 
         "description": f"Avg |r|: {avg_margin_corr:.3f}", "type": "success" if margin_pred_count >= total_companies * 0.5 else "info"},
        {"label": "Profitability Predictive", "value": f"{profit_pred_count}/{total_companies}", 
         "description": f"Avg |r|: {avg_profit_corr:.3f}", "type": "success" if profit_pred_count >= total_companies * 0.5 else "info"},
        {"label": "Total Predictive Count", "value": str(revenue_pred_count + margin_pred_count + profit_pred_count), 
         "description": f"Out of {total_companies * 3} possible", "type": "default"}
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table with RAW CORRELATIONS
    table_data = []
    for company, metrics in momentum_analysis.items():
        table_data.append({
            'Company': company,
            'Revenue Pred': "✓" if metrics.get('revenue_predictive', False) else "✗",
            'Revenue |r|': f"{abs(metrics.get('revenue_correlation', 0)):.3f}" if 'revenue_correlation' in metrics else "—",
            'Margin Pred': "✓" if metrics.get('margin_predictive', False) else "✗",
            'Margin |r|': f"{abs(metrics.get('margin_correlation', 0)):.3f}" if 'margin_correlation' in metrics else "—",
            'Profit Pred': "✓" if metrics.get('profitability_predictive', False) else "✗",
            'Profit |r|': f"{abs(metrics.get('profit_correlation', 0)):.3f}" if 'profit_correlation' in metrics else "—",
            'Predictive Count': f"{sum([metrics.get('revenue_predictive', False), metrics.get('margin_predictive', False), metrics.get('profitability_predictive', False)])}/3"
        })
    
    df_table = pd.DataFrame(table_data)
    
    def pred_color(val):
        return "excellent" if val == "✓" else "poor" if val == "✗" else "neutral"
    
    color_columns = {'Revenue Pred': pred_color, 'Margin Pred': pred_color, 'Profit Pred': pred_color}
    
    table_html = build_enhanced_table(df_table, table_id="table_17a2_momentum", 
                                     color_columns=color_columns, sortable=True, searchable=True)
    
    # Charts
    chart1 = _create_chart_17a2_predictive_coverage_heatmap(momentum_analysis)
    chart2 = _create_chart_17a2_correlation_strengths(momentum_analysis)
    chart3 = _create_chart_17a2_percentile_ranking(momentum_analysis)
    chart4 = _create_chart_17a2_multidimensional_profile(momentum_analysis)
    
    return f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17a2')">
            <span>17A.2: Momentum-Fundamental Correlation - Which Fundamentals Are Predictable?</span>
            <span id="icon_17a2" style="transition: transform 0.3s;">▼</span>
        </h3>
        <div id="section_17a2" style="display: block;">
            <p><strong>Analysis:</strong> Shows which companies have momentum signals that predict specific fundamentals. 
            Displays raw correlation strengths—no arbitrary "momentum strength" scores.</p>
            <h4>Summary Statistics</h4>
            {summary_grid}
            <h4>Predictive Pattern Matrix by Company</h4>
            {table_html}
            <h4>Multi-Dimensional Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            {chart4}
        </div>
    </div>
    """


def _create_chart_17a2_predictive_coverage_heatmap(momentum_analysis: Dict) -> str:
    """Create predictive coverage matrix heatmap"""
    companies = list(momentum_analysis.keys())[:12]
    metrics = ['Revenue', 'Margin', 'Profitability']
    matrix = [[1 if momentum_analysis[c].get(f'{m.lower()}_predictive', False) else 0 
               for m in metrics] for c in companies]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=metrics, y=[c[:12] for c in companies],
        colorscale=[[0, '#ef4444'], [1, '#10b981']], showscale=False,
        text=[['✓' if val == 1 else '✗' for val in row] for row in matrix],
        texttemplate='%{text}', textfont={"size": 14, "color": "white"}
    ))
    fig.update_layout(title='Momentum Predictive Coverage Matrix', height=500, xaxis=dict(side='top'))
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a2_heatmap")


def _create_chart_17a2_correlation_strengths(momentum_analysis: Dict) -> str:
    """Create correlation strength comparison bars"""
    companies = [c[:12] for c in momentum_analysis.keys()]
    revenue_corrs = [abs(m.get('revenue_correlation', 0)) for m in momentum_analysis.values()]
    margin_corrs = [abs(m.get('margin_correlation', 0)) for m in momentum_analysis.values()]
    profit_corrs = [abs(m.get('profit_correlation', 0)) for m in momentum_analysis.values()]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Revenue |r|', x=companies, y=revenue_corrs, marker_color='#3498db'))
    fig.add_trace(go.Bar(name='Margin |r|', x=companies, y=margin_corrs, marker_color='#9b59b6'))
    fig.add_trace(go.Bar(name='Profitability |r|', x=companies, y=profit_corrs, marker_color='#e74c3c'))
    fig.add_hline(y=0.3, line_dash="dot", line_color="orange", opacity=0.5)
    fig.add_hline(y=0.5, line_dash="dot", line_color="green", opacity=0.5)
    fig.update_layout(title='Absolute Correlation Strengths', xaxis_title='Company', 
                     yaxis_title='|Correlation|', barmode='group', height=450)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a2_strengths")


def _create_chart_17a2_percentile_ranking(momentum_analysis: Dict) -> str:
    """Create percentile ranking based on predictive count"""
    companies = []
    pred_counts = []
    for company, metrics in momentum_analysis.items():
        count = sum([metrics.get('revenue_predictive', False), 
                    metrics.get('margin_predictive', False), 
                    metrics.get('profitability_predictive', False)])
        companies.append(company[:15])
        pred_counts.append(count)
    
    sorted_indices = np.argsort(pred_counts)[::-1]
    companies = [companies[i] for i in sorted_indices]
    pred_counts = [pred_counts[i] for i in sorted_indices]
    percentiles = [stats.percentileofscore(pred_counts, pc) for pc in pred_counts]
    colors = ['#10b981' if pc==3 else '#3b82f6' if pc==2 else '#f59e0b' if pc==1 else '#ef4444' for pc in pred_counts]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=companies, x=percentiles, orientation='h', marker=dict(color=colors),
                        text=[f"{p:.0f}th %ile<br>{pc}/3" for p, pc in zip(percentiles, pred_counts)],
                        textposition='outside'))
    fig.update_layout(title='Percentile Rankings: Breadth of Coverage', 
                     xaxis_title='Percentile', yaxis_title='Company', 
                     height=max(400, len(companies)*25), showlegend=False)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a2_percentile")


def _create_chart_17a2_multidimensional_profile(momentum_analysis: Dict) -> str:
    """Create radar chart showing correlation profile"""
    companies = list(momentum_analysis.keys())[:6]
    categories = ['Revenue', 'Margin', 'Profitability']
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    fig = go.Figure()
    for idx, company in enumerate(companies):
        m = momentum_analysis[company]
        values = [abs(m.get('revenue_correlation', 0)), abs(m.get('margin_correlation', 0)), 
                 abs(m.get('profit_correlation', 0))]
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', 
                                      name=company[:15], line=dict(color=colors[idx]), opacity=0.6))
    
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                     title='Multi-Dimensional Correlation Profile', showlegend=True, height=550)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17a2_radar")


# =============================================================================
# 17B.1: INSTITUTIONAL FLOW IMPACT (NEW)
# =============================================================================

def _build_section_17b1_institutional_flow(ownership_signals: Dict, companies: Dict[str, str]) -> str:
    """Build 17B.1: Institutional Flow Impact - NO IMPACT/COMBINED SCORES"""
    
    if not ownership_signals:
        return '<div class="info-box warning"><h3>17B.1: Institutional Flow Impact</h3><p>Insufficient data.</p></div>'
    
    # Summary statistics - RAW COUNTS
    total_companies = len(ownership_signals)
    inst_available = sum(1 for s in ownership_signals.values() if s.get('institutional_impact'))
    insider_available = sum(1 for s in ownership_signals.values() if s.get('insider_impact'))
    
    total_inst_sig = sum(s.get('institutional_impact', {}).get('significant_relationships', 0) for s in ownership_signals.values())
    total_inst_tested = sum(s.get('institutional_impact', {}).get('total_tested', 0) for s in ownership_signals.values())
    total_insider_sig = sum(s.get('insider_impact', {}).get('significant_relationships', 0) for s in ownership_signals.values())
    total_insider_tested = sum(s.get('insider_impact', {}).get('total_tested', 0) for s in ownership_signals.values())
    
    all_inst_corrs = []
    all_insider_corrs = []
    for s in ownership_signals.values():
        for corr_data in s.get('institutional_impact', {}).get('correlations', {}).values():
            all_inst_corrs.append(abs(corr_data.get('correlation', 0)))
        for corr_data in s.get('insider_impact', {}).get('correlations', {}).values():
            all_insider_corrs.append(abs(corr_data.get('correlation', 0)))
    
    avg_inst_corr = np.mean(all_inst_corrs) if all_inst_corrs else 0
    avg_insider_corr = np.mean(all_insider_corrs) if all_insider_corrs else 0
    
    summary_cards = [
        {"label": "Institutional Coverage", "value": f"{inst_available}/{total_companies}", 
         "description": f"{total_inst_sig}/{total_inst_tested} significant", "type": "info"},
        {"label": "Insider Coverage", "value": f"{insider_available}/{total_companies}", 
         "description": f"{total_insider_sig}/{total_insider_tested} significant", "type": "info"},
        {"label": "Institutional Avg |r|", "value": f"{avg_inst_corr:.3f}", 
         "description": f"Across {len(all_inst_corrs)} tests", "type": "success" if avg_inst_corr >= 0.3 else "default"},
        {"label": "Insider Avg |r|", "value": f"{avg_insider_corr:.3f}", 
         "description": f"Across {len(all_insider_corrs)} tests", "type": "success" if avg_insider_corr >= 0.3 else "default"}
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Table with RAW CORRELATIONS
    table_data = []
    for company, signals in ownership_signals.items():
        inst = signals.get('institutional_impact', {})
        insider = signals.get('insider_impact', {})
        inst_corrs = [abs(c.get('correlation', 0)) for c in inst.get('correlations', {}).values()]
        insider_corrs = [abs(c.get('correlation', 0)) for c in insider.get('correlations', {}).values()]
        
        table_data.append({
            'Company': company,
            'Inst Sig/Total': f"{inst.get('significant_relationships', 0)}/{inst.get('total_tested', 0)}" if inst else "N/A",
            'Inst Avg |r|': f"{np.mean(inst_corrs):.3f}" if inst_corrs else "—",
            'Insider Sig/Total': f"{insider.get('significant_relationships', 0)}/{insider.get('total_tested', 0)}" if insider else "N/A",
            'Insider Avg |r|': f"{np.mean(insider_corrs):.3f}" if insider_corrs else "—",
            'Total Sig': inst.get('significant_relationships', 0) + insider.get('significant_relationships', 0)
        })
    
    df_table = pd.DataFrame(table_data)
    table_html = build_data_table(df_table, table_id="table_17b1_ownership", sortable=True, searchable=True)
    
    # Charts
    chart1 = _create_chart_17b1_separate_comparison(ownership_signals)
    chart2 = _create_chart_17b1_correlation_scatter(ownership_signals)
    chart3 = _create_chart_17b1_gradient_bars(ownership_signals, avg_inst_corr)
    chart4 = _create_chart_17b1_significance_distribution(ownership_signals)
    
    return f"""
    <div class="info-section">
        <h3 style="cursor: pointer;" onclick="toggleCollapse('section_17b1')">
            <span>17B.1: Institutional Flow Impact</span>
            <span id="icon_17b1">▼</span>
        </h3>
        <div id="section_17b1" style="display: block;">
            <p><strong>Analysis:</strong> Shows raw correlations—no "impact scores". 
            Institutional and insider kept separate.</p>
            <h4>Summary Statistics</h4>
            {summary_grid}
            <h4>Details by Company</h4>
            {table_html}
            <h4>Visualizations</h4>
            {chart1}{chart2}{chart3}{chart4}
        </div>
    </div>
    """


def _create_chart_17b1_separate_comparison(ownership_signals: Dict) -> str:
    """Side-by-side comparison"""
    companies = [c[:12] for c in ownership_signals.keys()]
    inst_sig = [s.get('institutional_impact', {}).get('significant_relationships', 0) for s in ownership_signals.values()]
    inst_total = [s.get('institutional_impact', {}).get('total_tested', 0) for s in ownership_signals.values()]
    insider_sig = [s.get('insider_impact', {}).get('significant_relationships', 0) for s in ownership_signals.values()]
    insider_total = [s.get('insider_impact', {}).get('total_tested', 0) for s in ownership_signals.values()]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Inst Sig', x=companies, y=inst_sig, marker_color='#3498db'))
    fig.add_trace(go.Bar(name='Inst Total', x=companies, y=inst_total, marker_color='lightblue', opacity=0.5))
    fig.add_trace(go.Bar(name='Insider Sig', x=companies, y=insider_sig, marker_color='#e74c3c'))
    fig.add_trace(go.Bar(name='Insider Total', x=companies, y=insider_total, marker_color='#ffcccb', opacity=0.5))
    fig.update_layout(title='Institutional vs Insider (Separate)', barmode='group', height=450)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_separate")


def _create_chart_17b1_correlation_scatter(ownership_signals: Dict) -> str:
    """Scatter WITHOUT combining"""
    companies, inst_avg, insider_avg, total_sigs = [], [], [], []
    for company, signals in ownership_signals.items():
        inst_corrs = [abs(c.get('correlation', 0)) for c in signals.get('institutional_impact', {}).get('correlations', {}).values()]
        insider_corrs = [abs(c.get('correlation', 0)) for c in signals.get('insider_impact', {}).get('correlations', {}).values()]
        if inst_corrs or insider_corrs:
            companies.append(company[:15])
            inst_avg.append(np.mean(inst_corrs) if inst_corrs else 0)
            insider_avg.append(np.mean(insider_corrs) if insider_corrs else 0)
            total_sigs.append(signals.get('institutional_impact', {}).get('significant_relationships', 0) + 
                            signals.get('insider_impact', {}).get('significant_relationships', 0))
    
    colors = ['#10b981' if ts>=3 else '#3b82f6' if ts>=2 else '#f59e0b' if ts>=1 else '#ef4444' for ts in total_sigs]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=inst_avg, y=insider_avg, mode='markers', 
                            marker=dict(size=12, color=colors, line=dict(width=1, color='black')),
                            text=[f"{c}<br>Total Sig: {ts}" for c, ts in zip(companies, total_sigs)]))
    fig.update_layout(title='Independent Comparison: Inst vs Insider', 
                     xaxis_title='Inst Avg |r|', yaxis_title='Insider Avg |r|', height=500)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_scatter")


def _create_chart_17b1_gradient_bars(ownership_signals: Dict, portfolio_avg: float) -> str:
    """Gradient bars with benchmark"""
    companies, inst_corrs = [], []
    for company, signals in ownership_signals.items():
        corrs = [abs(c.get('correlation', 0)) for c in signals.get('institutional_impact', {}).get('correlations', {}).values()]
        if corrs:
            companies.append(company[:15])
            inst_corrs.append(np.mean(corrs))
    
    sorted_idx = np.argsort(inst_corrs)[::-1]
    companies = [companies[i] for i in sorted_idx]
    inst_corrs = [inst_corrs[i] for i in sorted_idx]
    colors = ['#10b981' if ic>portfolio_avg*1.2 else '#3b82f6' if ic>portfolio_avg*0.8 else '#f59e0b' for ic in inst_corrs]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=companies, x=inst_corrs, orientation='h', marker=dict(color=colors),
                        text=[f"{ic:.3f}" for ic in inst_corrs], textposition='outside'))
    fig.add_vline(x=portfolio_avg, line_dash="dash", line_color="red")
    fig.update_layout(title=f'Institutional Strength with Benchmark (Avg={portfolio_avg:.3f})', 
                     height=max(400, len(companies)*25))
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_gradient")


def _create_chart_17b1_significance_distribution(ownership_signals: Dict) -> str:
    """Distribution histogram"""
    sig_counts = [s.get('institutional_impact', {}).get('significant_relationships', 0) + 
                 s.get('insider_impact', {}).get('significant_relationships', 0) 
                 for s in ownership_signals.values()]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=sig_counts, marker=dict(color='rgba(102, 126, 234, 0.7)')))
    if sig_counts:
        fig.add_vline(x=np.mean(sig_counts), line_dash="dash", line_color="red")
    fig.update_layout(title='Distribution of Total Significant Relationships', height=400)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b1_distribution")


# =============================================================================
# ANALYSIS HELPERS (NEW)
# =============================================================================

def _analyze_momentum_fundamental_correlation(df_prices, df_financial, companies, price_fundamental_signals):
    """NO ARBITRARY SUMS"""
    if not price_fundamental_signals:
        return {}
    
    momentum_analysis = {}
    for company_name in price_fundamental_signals.keys():
        try:
            signals = price_fundamental_signals[company_name]
            correlations = signals.get('correlations', {})
            metrics = {'revenue_predictive': False, 'margin_predictive': False, 'profitability_predictive': False}
            
            if 'momentum_revenue' in correlations:
                mr = correlations['momentum_revenue']
                metrics['revenue_predictive'] = mr['significant']
                metrics['revenue_correlation'] = mr['correlation']
            
            if 'rsi_margins' in correlations:
                rm = correlations['rsi_margins']
                metrics['margin_predictive'] = rm['significant']
                metrics['margin_correlation'] = rm['correlation']
            
            if 'volatility_roe' in correlations:
                vr = correlations['volatility_roe']
                metrics['profitability_predictive'] = vr['significant']
                metrics['profit_correlation'] = vr['correlation']
            
            momentum_analysis[company_name] = metrics
        except Exception as e:
            continue
    
    return momentum_analysis


def _analyze_ownership_price_dynamics(df_prices, df_institutional, df_insider, companies):
    """NO ARBITRARY SCORES"""
    if df_prices.empty or (df_institutional.empty and df_insider.empty):
        return {}
    
    ownership_price_signals = {}
    for company_name, ticker in companies.items():
        try:
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            company_prices = company_prices.sort_values('date')
            
            analysis = {'institutional_impact': {}, 'insider_impact': {}}
            
            if not df_institutional.empty:
                company_inst = df_institutional[df_institutional['Company'] == company_name].copy()
                if not company_inst.empty:
                    analysis['institutional_impact'] = _compute_institutional_price_impact(company_prices, company_inst)
            
            if not df_insider.empty:
                company_insider = df_insider[df_insider['Company'] == company_name].copy()
                if not company_insider.empty:
                    analysis['insider_impact'] = _compute_insider_price_impact(company_prices, company_insider)
            
            if analysis['institutional_impact'] or analysis['insider_impact']:
                ownership_price_signals[company_name] = analysis
        except Exception as e:
            continue
    
    return ownership_price_signals


def _compute_institutional_price_impact(price_df, inst_df):
    """RAW CORRELATIONS ONLY"""
    try:
        inst_df = inst_df.copy()
        inst_df['date'] = pd.to_datetime(inst_df['date'])
        inst_df = inst_df.sort_values('date')
        inst_df['totalInvested_change'] = inst_df['totalInvested'].diff()
        inst_df['ownershipPercent_change'] = inst_df['ownershipPercent'].diff()
        inst_df['year'] = inst_df['date'].dt.year
        
        annual_inst = inst_df.sort_values('date').groupby('year').last().reset_index()
        price_df = price_df.copy()
        price_df['year'] = pd.to_datetime(price_df['date']).dt.year
        annual_returns = price_df.groupby('year').agg({'close': 'last'}).reset_index()
        annual_returns['annual_return'] = annual_returns['close'].pct_change() * 100
        
        merged = pd.merge(annual_inst, annual_returns, on='year', how='inner')
        if len(merged) < 3:
            return {}
        
        correlations = {}
        valid = merged[['totalInvested_change', 'annual_return']].dropna()
        if len(valid) >= 3:
            corr, pval = stats.pearsonr(valid['totalInvested_change'], valid['annual_return'])
            correlations['flow_return'] = {'correlation': corr, 'p_value': pval, 'significant': pval < 0.15}
        
        valid = merged[['ownershipPercent_change', 'annual_return']].dropna()
        if len(valid) >= 3:
            corr, pval = stats.pearsonr(valid['ownershipPercent_change'], valid['annual_return'])
            correlations['ownership_return'] = {'correlation': corr, 'p_value': pval, 'significant': pval < 0.15}
        
        significant_count = sum(1 for c in correlations.values() if c.get('significant', False))
        return {'correlations': correlations, 'significant_relationships': significant_count, 
                'total_tested': len(correlations), 'data_points': len(merged)}
    except:
        return {}


def _compute_insider_price_impact(price_df, insider_df):
    """RAW CORRELATIONS ONLY"""
    try:
        insider_df = insider_df.copy()
        insider_df['transactionDate'] = pd.to_datetime(insider_df['transactionDate'])
        insider_df = insider_df.sort_values('transactionDate')
        insider_df['is_buy'] = insider_df['acquisitionOrDisposition'] == 'A'
        insider_df['is_sell'] = insider_df['acquisitionOrDisposition'] == 'D'
        insider_df['month'] = insider_df['transactionDate'].dt.to_period('M')
        
        monthly_insider = insider_df.groupby('month').agg({
            'is_buy': 'sum', 'is_sell': 'sum', 'securitiesTransacted': 'sum'
        }).reset_index()
        monthly_insider['net_activity'] = monthly_insider['is_buy'] - monthly_insider['is_sell']
        
        price_df['month'] = price_df['date'].dt.to_period('M')
        monthly_returns = price_df.groupby('month').agg({'close': 'last'}).reset_index()
        monthly_returns['monthly_return'] = monthly_returns['close'].pct_change() * 100
        
        merged = pd.merge(monthly_insider, monthly_returns, on='month', how='inner')
        if len(merged) < 6:
            return {}
        
        correlations = {}
        merged['net_activity_lag'] = merged['net_activity'].shift(1)
        valid = merged[['net_activity_lag', 'monthly_return']].dropna()
        
        if len(valid) >= 4:
            corr, pval = stats.pearsonr(valid['net_activity_lag'], valid['monthly_return'])
            correlations['insider_activity_lead'] = {'correlation': corr, 'p_value': pval, 'significant': pval < 0.10}
        
        significant_count = sum(1 for c in correlations.values() if c.get('significant', False))
        return {'correlations': correlations, 'significant_relationships': significant_count,
                'total_tested': len(correlations), 'data_points': len(merged)}
    except:
        return {}


# =============================================================================
# 17B.2: INSIDER ACTIVITY & PRICE RESPONSE (NEW - NO SIGNAL QUALITY SCORE)
# =============================================================================

def _build_section_17b2_insider_response(
    insider_analysis: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17B.2: Insider Activity & Price Response - NO ARBITRARY SIGNAL QUALITY"""
    
    if not insider_analysis:
        return """
        <div class="info-box warning">
            <h3>17B.2: Insider Activity & Price Response</h3>
            <p>Insufficient insider transaction data for price response analysis.</p>
        </div>
        """
    
    # Summary statistics - RAW METRICS
    total_companies = len(insider_analysis)
    companies_with_buys = sum(1 for m in insider_analysis.values() if m.get('buy_transactions', 0) > 0)
    
    # Calculate actual returns (not arbitrary quality scores)
    returns_30d = [m.get('avg_return_30d_after_buy', 0) for m in insider_analysis.values() 
                   if 'avg_return_30d_after_buy' in m]
    returns_60d = [m.get('avg_return_60d_after_buy', 0) for m in insider_analysis.values() 
                   if 'avg_return_60d_after_buy' in m]
    success_rates = [m.get('buy_success_rate', 0) for m in insider_analysis.values() 
                     if 'buy_success_rate' in m]
    
    avg_return_30d = np.mean(returns_30d) if returns_30d else 0
    avg_return_60d = np.mean(returns_60d) if returns_60d else 0
    median_success = np.median(success_rates) if success_rates else 0
    positive_30d_count = sum(1 for r in returns_30d if r > 0)
    
    total_buy_transactions = sum(m.get('buy_transactions', 0) for m in insider_analysis.values())
    
    # Summary cards - RAW METRICS ONLY
    summary_cards = [
        {"label": "Companies with Buys", "value": f"{companies_with_buys}/{total_companies}",
         "description": f"{total_buy_transactions} total transactions", "type": "info"},
        {"label": "Avg 30-Day Return", "value": f"{avg_return_30d:+.1f}%",
         "description": f"{positive_30d_count}/{len(returns_30d)} positive", 
         "type": "success" if avg_return_30d > 0 else "danger"},
        {"label": "Avg 60-Day Return", "value": f"{avg_return_60d:+.1f}%",
         "description": "After insider purchases", 
         "type": "success" if avg_return_60d > 0 else "danger"},
        {"label": "Median Success Rate", "value": f"{median_success:.0%}",
         "description": f"Range: {min(success_rates):.0%}-{max(success_rates):.0%}" if success_rates else "N/A",
         "type": "success" if median_success >= 0.55 else "warning" if median_success >= 0.5 else "default"}
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table with RAW RETURNS
    table_data = []
    for company, metrics in insider_analysis.items():
        table_data.append({
            'Company': company,
            'Buy Count': metrics.get('buy_transactions', 0),
            '30d Return': f"{metrics.get('avg_return_30d_after_buy', 0):+.1f}%" if 'avg_return_30d_after_buy' in metrics else "N/A",
            '60d Return': f"{metrics.get('avg_return_60d_after_buy', 0):+.1f}%" if 'avg_return_60d_after_buy' in metrics else "N/A",
            'Success Rate': f"{metrics.get('buy_success_rate', 0):.0%}" if 'buy_success_rate' in metrics else "N/A",
            'Return Stdev': f"{metrics.get('return_stdev', 0):.1f}%" if 'return_stdev' in metrics else "N/A"
        })
    
    df_table = pd.DataFrame(table_data)
    table_html = build_data_table(df_table, table_id="table_17b2_insider", sortable=True, searchable=True)
    
    # Charts - NO QUALITY SCORES
    chart1 = _create_chart_17b2_return_distribution(insider_analysis)
    chart2 = _create_chart_17b2_returns_scatter(insider_analysis)
    chart3 = _create_chart_17b2_success_rate_bars(insider_analysis)
    chart4 = _create_chart_17b2_quadrant_analysis(insider_analysis)
    chart5 = _create_chart_17b2_strip_plot(insider_analysis, returns_30d)
    
    return f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17b2')">
            <span>17B.2: Insider Activity & Price Response - Actual Returns & Success Rates</span>
            <span id="icon_17b2" style="transition: transform 0.3s;">▼</span>
        </h3>
        <div id="section_17b2" style="display: block;">
            <p><strong>Analysis:</strong> Examines actual price performance following insider purchases. 
            Shows real returns, success rates, and distributions—no arbitrary "signal quality" scores.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Insider Buy Performance by Company</h4>
            <p><em>Note: Analyzes substantial transactions (≥50th percentile by value). 
            Success rate = % of purchases followed by positive 30-day returns. Return Stdev = volatility of outcomes.</em></p>
            {table_html}
            
            <h4>Multi-Dimensional Visualizations</h4>
            
            <div style="margin: 20px 0;">
                <h5>Return Distribution Analysis</h5>
                <p><em>Distribution of 30-day returns following insider buys across all companies</em></p>
                {chart1}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>30-Day vs 60-Day Returns Comparison</h5>
                <p><em>How short-term signals persist (or fade) over longer horizons</em></p>
                {chart2}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Success Rate Rankings</h5>
                <p><em>Percentage of insider buys followed by positive returns</em></p>
                {chart3}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Quadrant Analysis: Returns vs Success Rate</h5>
                <p><em>Identifying consistent performers vs high-variance situations</em></p>
                {chart4}
            </div>
            
            <div style="margin: 20px 0;">
                <h5>Distribution Strip Plot: Where Companies Stand</h5>
                <p><em>Visual distribution showing position of each company relative to peers</em></p>
                {chart5}
            </div>
            
            <div class="info-box info">
                <h4>Interpretation Guidelines</h4>
                <ul>
                    <li><strong>30d/60d Return:</strong> Average return following insider buys. Positive = buys preceded gains</li>
                    <li><strong>Success Rate:</strong> % of buys followed by positive 30d returns. >50% = better than random</li>
                    <li><strong>Return Stdev:</strong> Volatility of outcomes. High stdev = inconsistent results</li>
                    <li><strong>Quadrants:</strong> High return + high success = reliable signal; High return + low success = lucky outliers</li>
                    <li><strong>Distribution:</strong> Shows if returns are concentrated or dispersed</li>
                    <li><strong>Buy Count:</strong> More transactions = more reliable statistics</li>
                </ul>
            </div>
        </div>
    </div>
    """


def _create_chart_17b2_return_distribution(insider_analysis: Dict) -> str:
    """Create distribution of returns - not just averages"""
    
    all_30d_returns = []
    for metrics in insider_analysis.values():
        if 'avg_return_30d_after_buy' in metrics:
            all_30d_returns.append(metrics['avg_return_30d_after_buy'])
    
    if not all_30d_returns:
        return ""
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=all_30d_returns,
        nbinsx=15,
        marker=dict(color='rgba(102, 126, 234, 0.7)', line=dict(color='rgba(102, 126, 234, 1)', width=1)),
        hovertemplate='Return Range: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add statistical reference lines
    mean_return = np.mean(all_30d_returns)
    median_return = np.median(all_30d_returns)
    
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=2, 
                  annotation_text="Zero", annotation_position="top")
    fig.add_vline(x=median_return, line_dash="dash", line_color="red", line_width=2,
                  annotation_text=f"Median: {median_return:+.1f}%", annotation_position="top")
    fig.add_vline(x=mean_return, line_dash="dot", line_color="blue", line_width=2,
                  annotation_text=f"Mean: {mean_return:+.1f}%", annotation_position="bottom")
    
    # Shade positive/negative regions
    fig.add_vrect(x0=0, x1=max(all_30d_returns), fillcolor="green", opacity=0.1)
    fig.add_vrect(x0=min(all_30d_returns), x1=0, fillcolor="red", opacity=0.1)
    
    fig.update_layout(
        title='Distribution of 30-Day Returns Following Insider Buys<br><sub>Green = positive returns, Red = negative returns</sub>',
        xaxis_title='30-Day Return (%)',
        yaxis_title='Number of Companies',
        showlegend=False,
        height=450
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_distribution")


def _create_chart_17b2_returns_scatter(insider_analysis: Dict) -> str:
    """Create 30d vs 60d returns scatter"""
    
    companies = []
    returns_30d = []
    returns_60d = []
    success_rates = []
    
    for company, metrics in insider_analysis.items():
        if 'avg_return_30d_after_buy' in metrics and 'avg_return_60d_after_buy' in metrics:
            companies.append(company[:15])
            returns_30d.append(metrics['avg_return_30d_after_buy'])
            returns_60d.append(metrics['avg_return_60d_after_buy'])
            success_rates.append(metrics.get('buy_success_rate', 0) * 100)
    
    # Color by success rate
    colors = ['#10b981' if sr >= 60 else '#3b82f6' if sr >= 50 else '#f59e0b' if sr >= 40 else '#ef4444' 
              for sr in success_rates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=returns_30d,
        y=returns_60d,
        mode='markers',
        marker=dict(size=12, color=colors, line=dict(width=1, color='black'), opacity=0.7),
        text=[f"{c}<br>Success: {sr:.0f}%" for c, sr in zip(companies, success_rates)],
        hovertemplate='%{text}<br>30d: %{x:+.1f}%<br>60d: %{y:+.1f}%<extra></extra>'
    ))
    
    # Add diagonal reference line (30d = 60d)
    all_returns = returns_30d + returns_60d
    if all_returns:
        min_val, max_val = min(all_returns), max(all_returns)
        fig.add_trace(go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode='lines', line=dict(dash='dash', color='gray', width=1),
            showlegend=False, hoverinfo='skip'
        ))
    
    # Add zero lines
    fig.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.3)
    fig.add_vline(x=0, line_dash="solid", line_color="black", opacity=0.3)
    
    fig.update_layout(
        title='Persistence of Returns: 30-Day vs 60-Day<br><sub>Color by success rate. Diagonal = equal persistence</sub>',
        xaxis_title='30-Day Return (%)',
        yaxis_title='60-Day Return (%)',
        height=500
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_scatter")


def _create_chart_17b2_success_rate_bars(insider_analysis: Dict) -> str:
    """Create success rate horizontal bars"""
    
    companies = []
    success_rates = []
    buy_counts = []
    
    for company, metrics in insider_analysis.items():
        if 'buy_success_rate' in metrics:
            companies.append(company[:15])
            success_rates.append(metrics['buy_success_rate'] * 100)
            buy_counts.append(metrics.get('buy_transactions', 0))
    
    # Sort by success rate
    sorted_indices = np.argsort(success_rates)[::-1]
    companies = [companies[i] for i in sorted_indices]
    success_rates = [success_rates[i] for i in sorted_indices]
    buy_counts = [buy_counts[i] for i in sorted_indices]
    
    # Color by threshold
    colors = ['#10b981' if sr >= 60 else '#3b82f6' if sr >= 50 else '#f59e0b' if sr >= 40 else '#ef4444' 
              for sr in success_rates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=companies,
        x=success_rates,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{sr:.0f}% (n={bc})" for sr, bc in zip(success_rates, buy_counts)],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Success Rate: %{x:.1f}%<extra></extra>'
    ))
    
    # Add reference lines
    fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5,
                  annotation_text="50% (random)", annotation_position="top")
    fig.add_vline(x=60, line_dash="dot", line_color="green", opacity=0.5,
                  annotation_text="60% (strong)", annotation_position="top")
    
    fig.update_layout(
        title='Insider Buy Signal Success Rates<br><sub>Green ≥60%, Blue ≥50%, Orange ≥40%, Red <40%. n = number of buys</sub>',
        xaxis_title='Success Rate (%)',
        yaxis_title='Company',
        height=max(400, len(companies) * 25),
        showlegend=False
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_success")


def _create_chart_17b2_quadrant_analysis(insider_analysis: Dict) -> str:
    """Create quadrant analysis: returns vs success rate"""
    
    companies = []
    returns_30d = []
    success_rates = []
    buy_counts = []
    
    for company, metrics in insider_analysis.items():
        if 'avg_return_30d_after_buy' in metrics and 'buy_success_rate' in metrics:
            companies.append(company[:15])
            returns_30d.append(metrics['avg_return_30d_after_buy'])
            success_rates.append(metrics['buy_success_rate'] * 100)
            buy_counts.append(metrics.get('buy_transactions', 0))
    
    # Determine quadrants
    colors = []
    for ret, sr in zip(returns_30d, success_rates):
        if ret > 0 and sr >= 50:
            colors.append('#10b981')  # Green - reliable positive
        elif ret > 0 and sr < 50:
            colors.append('#3b82f6')  # Blue - lucky outliers
        elif ret <= 0 and sr >= 50:
            colors.append('#f59e0b')  # Orange - unlucky
        else:
            colors.append('#ef4444')  # Red - poor performance
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=returns_30d,
        y=success_rates,
        mode='markers',
        marker=dict(
            size=[min(20, max(8, bc/2)) for bc in buy_counts],
            color=colors,
            line=dict(width=1, color='black'),
            opacity=0.7
        ),
        text=[f"{c}<br>Buys: {bc}" for c, bc in zip(companies, buy_counts)],
        hovertemplate='%{text}<br>Return: %{x:+.1f}%<br>Success: %{y:.0f}%<extra></extra>'
    ))
    
    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=5, y=75, text="Reliable<br>Positive", showarrow=False, opacity=0.5, font=dict(size=12))
    fig.add_annotation(x=5, y=25, text="Lucky<br>Outliers", showarrow=False, opacity=0.5, font=dict(size=12))
    fig.add_annotation(x=-5, y=75, text="Unlucky<br>(High Success)", showarrow=False, opacity=0.5, font=dict(size=12))
    fig.add_annotation(x=-5, y=25, text="Poor<br>Performance", showarrow=False, opacity=0.5, font=dict(size=12))
    
    fig.update_layout(
        title='Quadrant Analysis: Return Quality vs Consistency<br><sub>Marker size ∝ number of buys. Green = best, Red = worst</sub>',
        xaxis_title='Average 30-Day Return (%)',
        yaxis_title='Success Rate (%)',
        height=500
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_quadrant")


def _create_chart_17b2_strip_plot(insider_analysis: Dict, all_returns: List[float]) -> str:
    """Create strip plot showing distribution with individual points"""
    
    if not all_returns:
        return ""
    
    companies = []
    returns = []
    
    for company, metrics in insider_analysis.items():
        if 'avg_return_30d_after_buy' in metrics:
            companies.append(company[:12])
            returns.append(metrics['avg_return_30d_after_buy'])
    
    # Sort by return
    sorted_indices = np.argsort(returns)
    returns = [returns[i] for i in sorted_indices]
    companies = [companies[i] for i in sorted_indices]
    
    # Calculate percentiles for context
    p25 = np.percentile(all_returns, 25)
    p50 = np.percentile(all_returns, 50)
    p75 = np.percentile(all_returns, 75)
    
    fig = go.Figure()
    
    # Add strip plot
    fig.add_trace(go.Scatter(
        x=returns,
        y=[0] * len(returns),
        mode='markers',
        marker=dict(
            size=12,
            color=returns,
            colorscale='RdYlGn',
            cmid=0,
            line=dict(width=1, color='black'),
            showscale=True,
            colorbar=dict(title="Return (%)")
        ),
        text=companies,
        hovertemplate='<b>%{text}</b><br>Return: %{x:+.1f}%<extra></extra>'
    ))
    
    # Add box plot overlay
    fig.add_trace(go.Box(
        x=all_returns,
        y=[0] * len(all_returns),
        boxmean='sd',
        marker_color='rgba(0,0,0,0.3)',
        line_color='rgba(0,0,0,0.5)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add percentile lines
    fig.add_vline(x=p25, line_dash="dot", line_color="gray", opacity=0.5, annotation_text="25th %ile")
    fig.add_vline(x=p50, line_dash="dash", line_color="red", opacity=0.7, annotation_text="Median")
    fig.add_vline(x=p75, line_dash="dot", line_color="gray", opacity=0.5, annotation_text="75th %ile")
    fig.add_vline(x=0, line_dash="solid", line_color="black", opacity=0.3)
    
    fig.update_layout(
        title='Distribution Strip Plot: 30-Day Returns with Box Plot Overlay<br><sub>Each point = one company. Box shows quartiles and outliers</sub>',
        xaxis_title='30-Day Return (%)',
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        height=300,
        showlegend=False
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="chart_17b2_strip")


# =============================================================================
# 17C.1: MULTI-TIMEFRAME INTEGRATION (NEW - ENHANCED)
# =============================================================================

def _build_section_17c1_multi_timeframe(
    multi_timeframe_signals: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17C.1: Multi-Timeframe Integration - RAW METRICS ONLY"""
    
    if not multi_timeframe_signals:
        return """
        <div class="info-box warning">
            <h3>17C.1: Multi-Timeframe Integration</h3>
            <p>Insufficient data for multi-timeframe integration analysis.</p>
        </div>
        """
    
    # Summary statistics - RAW METRICS
    total_companies = len(multi_timeframe_signals)
    
    daily_sig_counts = [s['daily_significant'] for s in multi_timeframe_signals.values()]
    daily_total_counts = [s['daily_total'] for s in multi_timeframe_signals.values()]
    quarterly_sig_counts = [s['quarterly_significant'] for s in multi_timeframe_signals.values()]
    quarterly_total_counts = [s['quarterly_total'] for s in multi_timeframe_signals.values()]
    
    total_daily_sig = sum(daily_sig_counts)
    total_daily_tests = sum(daily_total_counts)
    total_quarterly_sig = sum(quarterly_sig_counts)
    total_quarterly_tests = sum(quarterly_total_counts)
    
    both_signals = sum(1 for s in multi_timeframe_signals.values() 
                      if s['daily_significant'] > 0 and s['quarterly_significant'] > 0)
    
    # Summary cards
    summary_cards = [
        {"label": "Daily Signal Coverage", "value": f"{total_daily_sig}/{total_daily_tests}",
         "description": f"{total_daily_sig/total_daily_tests*100:.0f}% significant" if total_daily_tests > 0 else "N/A", 
         "type": "info"},
        {"label": "Quarterly Signal Coverage", "value": f"{total_quarterly_sig}/{total_quarterly_tests}",
         "description": f"{total_quarterly_sig/total_quarterly_tests*100:.0f}% significant" if total_quarterly_tests > 0 else "N/A", 
         "type": "info"},
        {"label": "Dual-Timeframe Coverage", "value": f"{both_signals}/{total_companies}",
         "description": "Both daily and quarterly signals", 
         "type": "success" if both_signals >= total_companies * 0.5 else "warning"},
        {"label": "Total Tests", "value": str(total_daily_tests + total_quarterly_tests),
         "description": "Cross-frequency correlations", "type": "default"}
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table
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
            'Both Signals': "✓" if signals['daily_significant'] > 0 and signals['quarterly_significant'] > 0 else "✗"
        })
    
    df_table = pd.DataFrame(table_data)
    
    def both_color(val):
        return "excellent" if val == "✓" else "neutral"
    
    table_html = build_enhanced_table(df_table, table_id="table_17c1_multitimeframe",
                                     color_columns={'Both Signals': both_color}, sortable=True, searchable=True)
    
    # Charts
    chart1 = _create_chart_17c1_signal_comparison(multi_timeframe_signals)
    chart2 = _create_chart_17c1_coverage_scatter(multi_timeframe_signals)
    chart3 = _create_chart_17c1_heatmap(multi_timeframe_signals)
    
    return f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17c1')">
            <span>17C.1: Multi-Timeframe Integration - Daily vs Quarterly Signal Coverage</span>
            <span id="icon_17c1" style="transition: transform 0.3s;">▼</span>
        </h3>
        <div id="section_17c1" style="display: block;">
            <p><strong>Analysis:</strong> Compares signal coverage across timeframes. 
            Shows actual significant correlations—no composite scores.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Multi-Timeframe Signal Coverage by Company</h4>
            <p><em>Daily = price-fundamental signals. Quarterly = ownership-price signals. 
            Both Signals = predictive in both timeframes.</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
        </div>
    </div>
    """


def _create_chart_17c1_signal_comparison(signals: Dict) -> str:
    """Create comparison chart"""
    companies = list(signals.keys())
    daily_sig = [s['daily_significant'] for s in signals.values()]
    daily_total = [s['daily_total'] for s in signals.values()]
    quarterly_sig = [s['quarterly_significant'] for s in signals.values()]
    quarterly_total = [s['quarterly_total'] for s in signals.values()]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Daily Sig', x=companies, y=daily_sig, marker_color='#3498db'))
    fig.add_trace(go.Bar(name='Daily Total', x=companies, y=daily_total, marker_color='lightblue', opacity=0.5))
    fig.add_trace(go.Bar(name='Quarterly Sig', x=companies, y=quarterly_sig, marker_color='#9b59b6'))
    fig.add_trace(go.Bar(name='Quarterly Total', x=companies, y=quarterly_total, marker_color='plum', opacity=0.5))
    
    fig.update_layout(title='Multi-Timeframe Signal Coverage', xaxis_title='Company',
                     yaxis_title='Count', barmode='group', height=450)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_comparison")


def _create_chart_17c1_coverage_scatter(signals: Dict) -> str:
    """Create coverage scatter"""
    companies = list(signals.keys())
    daily_pct = [s['daily_significant']/s['daily_total']*100 if s['daily_total'] > 0 else 0 for s in signals.values()]
    quarterly_pct = [s['quarterly_significant']/s['quarterly_total']*100 if s['quarterly_total'] > 0 else 0 for s in signals.values()]
    both = [s['daily_significant'] > 0 and s['quarterly_significant'] > 0 for s in signals.values()]
    
    colors = ['#10b981' if b else '#ef4444' for b in both]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_pct, y=quarterly_pct, mode='markers',
                            marker=dict(size=12, color=colors, line=dict(width=1, color='black')),
                            text=[f"{c[:15]}<br>D:{d:.0f}% Q:{q:.0f}%" for c,d,q in zip(companies, daily_pct, quarterly_pct)]))
    fig.add_trace(go.Scatter(x=[0,100], y=[0,100], mode='lines', line=dict(dash='dash', color='gray'), showlegend=False))
    
    fig.update_layout(title='Daily vs Quarterly Coverage % (Green = Both Have Signals)',
                     xaxis_title='Daily %', yaxis_title='Quarterly %', height=500)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_scatter")


def _create_chart_17c1_heatmap(signals: Dict) -> str:
    """Create signal count heatmap"""
    companies = list(signals.keys())[:12]
    metrics = ['Daily Sig', 'Daily Total', 'Quarterly Sig', 'Quarterly Total']
    
    matrix = [[s['daily_significant'], s['daily_total'], s['quarterly_significant'], s['quarterly_total']] 
              for c in companies for s in [signals[c]]]
    
    fig = go.Figure(data=go.Heatmap(z=matrix, x=metrics, y=[c[:12] for c in companies],
                                     colorscale='Blues', text=[[f"{int(v)}" for v in row] for row in matrix],
                                     texttemplate='%{text}', colorbar=dict(title="Count")))
    fig.update_layout(title='Signal Count Heatmap (Top 12 Companies)', height=500)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c1_heatmap")


# =============================================================================
# ANALYSIS HELPERS (NEW)
# =============================================================================

def _analyze_insider_price_response(df_prices, df_insider, companies):
    """Analyze price response to insider transactions - NO QUALITY SCORES"""
    if df_insider.empty or df_prices.empty:
        return {}
    
    insider_price_analysis = {}
    for company_name, ticker in companies.items():
        try:
            company_insider = df_insider[df_insider['Company'] == company_name].copy()
            if company_insider.empty:
                continue
            
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_insider['transactionDate'] = pd.to_datetime(company_insider['transactionDate'])
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            
            response_metrics = _compute_insider_transaction_response(company_prices, company_insider)
            if response_metrics:
                insider_price_analysis[company_name] = response_metrics
        except Exception as e:
            continue
    
    return insider_price_analysis


def _compute_insider_transaction_response(price_df, insider_df):
    """Compute price response - RAW RETURNS & SUCCESS RATES"""
    try:
        insider_df = insider_df.copy()
        insider_df['transaction_value'] = insider_df['securitiesTransacted'] * insider_df['price']
        
        value_threshold = insider_df['transaction_value'].quantile(0.5)
        significant_transactions = insider_df[insider_df['transaction_value'] >= value_threshold].copy()
        
        if len(significant_transactions) < 5:
            return {}
        
        buy_returns = []
        for idx, transaction in significant_transactions.iterrows():
            trans_date = transaction['transactionDate']
            is_buy = transaction['acquisitionOrDisposition'] == 'A'
            
            if not is_buy:
                continue
            
            future_prices = price_df[price_df['date'] > trans_date].head(60)
            if len(future_prices) >= 30:
                price_at_trans = price_df[price_df['date'] <= trans_date]['close'].iloc[-1] if len(price_df[price_df['date'] <= trans_date]) > 0 else np.nan
                price_30d = future_prices.iloc[29]['close'] if len(future_prices) > 29 else np.nan
                price_60d = future_prices.iloc[-1]['close']
                
                if not np.isnan(price_at_trans) and not np.isnan(price_30d):
                    return_30d = ((price_30d - price_at_trans) / price_at_trans) * 100
                    return_60d = ((price_60d - price_at_trans) / price_at_trans) * 100
                    buy_returns.append({'return_30d': return_30d, 'return_60d': return_60d})
        
        if not buy_returns:
            return {}
        
        buy_df = pd.DataFrame(buy_returns)
        metrics = {
            'buy_transactions': len(buy_returns),
            'avg_return_30d_after_buy': buy_df['return_30d'].mean(),
            'avg_return_60d_after_buy': buy_df['return_60d'].mean(),
            'buy_success_rate': (buy_df['return_30d'] > 0).sum() / len(buy_df),
            'return_stdev': buy_df['return_30d'].std()
        }
        
        return metrics
    except:
        return {}


def _analyze_multi_timeframe_integration(df_prices, df_financial, df_institutional, companies, 
                                         price_fundamental_signals, ownership_price_signals):
    """Integrate signals across timeframes - RAW METRICS"""
    multi_timeframe_signals = {}
    
    for company_name in companies.keys():
        try:
            analysis = {
                'daily_significant': 0, 'daily_total': 0, 'daily_data_points': 0,
                'quarterly_significant': 0, 'quarterly_total': 0, 'quarterly_data_points': 0
            }
            
            if company_name in price_fundamental_signals:
                pf = price_fundamental_signals[company_name]
                analysis['daily_significant'] = pf.get('significant_signals', 0)
                analysis['daily_total'] = pf.get('total_signals', 0)
                analysis['daily_data_points'] = pf.get('data_points', 0)
            
            if company_name in ownership_price_signals:
                op = ownership_price_signals[company_name]
                inst = op.get('institutional_impact', {})
                insider = op.get('insider_impact', {})
                analysis['quarterly_significant'] = inst.get('significant_relationships', 0) + insider.get('significant_relationships', 0)
                analysis['quarterly_total'] = inst.get('total_tested', 0) + insider.get('total_tested', 0)
                analysis['quarterly_data_points'] = max(inst.get('data_points', 0), insider.get('data_points', 0))
            
            if analysis['daily_total'] > 0 or analysis['quarterly_total'] > 0:
                multi_timeframe_signals[company_name] = analysis
        except:
            continue
    
    return multi_timeframe_signals


def _build_section_17c2_lead_lag(
    lead_lag_analysis: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17C.2: Lead-Lag Relationships - RAW CORRELATIONS ONLY"""
    
    if not lead_lag_analysis:
        return """
        <div class="info-box warning">
            <h3>17C.2: Lead-Lag Relationships & Predictive Signals</h3>
            <p>Insufficient data for lead-lag relationship analysis.</p>
        </div>
        """
    
    # Summary statistics - RAW METRICS
    total_companies = len(lead_lag_analysis)
    total_significant = sum(a['significant_patterns'] for a in lead_lag_analysis.values())
    total_tested = sum(a['total_tested'] for a in lead_lag_analysis.values())
    
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
        {"label": "Companies Analyzed", "value": str(total_companies),
         "description": f"{total_tested} lead-lag tests", "type": "info"},
        {"label": "Significant Patterns", "value": f"{total_significant}/{total_tested}",
         "description": f"{total_significant/total_tested*100:.0f}% with p < 0.10" if total_tested > 0 else "N/A",
         "type": "success" if total_significant/total_tested >= 0.4 else "warning"},
        {"label": "Avg |Mom→Vol| Corr", "value": f"{avg_mom_vol:.3f}",
         "description": "Momentum predicting volatility", "type": "info"},
        {"label": "Avg Short→Long Corr", "value": f"{avg_short_long:+.3f}",
         "description": "Momentum persistence/reversion", 
         "type": "success" if avg_short_long > 0 else "default"}
    ]
    
    summary_grid = build_stat_grid(summary_cards)
    
    # Create table
    table_data = []
    for company, analysis in lead_lag_analysis.items():
        metrics = analysis.get('lead_lag_metrics', {})
        row = {
            'Company': company,
            'Mom→Vol r': "—", 'Mom→Vol p': "—", 'Mom→Vol Sig': "—",
            'Short→Long r': "—", 'Short→Long p': "—", 'Short→Long Sig': "—",
            'Sig/Total': f"{analysis['significant_patterns']}/{analysis['total_tested']}",
            'N (days)': "—"
        }
        
        if 'momentum_leads_volatility' in metrics:
            mlv = metrics['momentum_leads_volatility']
            row['Mom→Vol r'] = f"{mlv['correlation']:.3f}"
            row['Mom→Vol p'] = f"{mlv['p_value']:.3f}"
            row['Mom→Vol Sig'] = "✓" if mlv['significant'] else "✗"
            row['N (days)'] = analysis.get('sample_size', '—')
        
        if 'short_term_leads_long_term' in metrics:
            stlt = metrics['short_term_leads_long_term']
            row['Short→Long r'] = f"{stlt['correlation']:.3f}"
            row['Short→Long p'] = f"{stlt['p_value']:.3f}"
            row['Short→Long Sig'] = "✓" if stlt['significant'] else "✗"
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    def sig_color(val):
        return "excellent" if val == "✓" else "poor" if val == "✗" else "neutral"
    
    color_columns = {'Mom→Vol Sig': sig_color, 'Short→Long Sig': sig_color}
    
    table_html = build_enhanced_table(df_table, table_id="table_17c2_leadlag",
                                     color_columns=color_columns, sortable=True, searchable=True)
    
    # Charts
    chart1 = _create_chart_17c2_correlation_comparison(lead_lag_analysis)
    chart2 = _create_chart_17c2_pvalue_scatter(lead_lag_analysis)
    chart3 = _create_chart_17c2_heatmap(lead_lag_analysis)
    
    return f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17c2')">
            <span>17C.2: Lead-Lag Relationships - Predictive Signal Timing (20-Day Lead)</span>
            <span id="icon_17c2" style="transition: transform 0.3s;">▼</span>
        </h3>
        <div id="section_17c2" style="display: block;">
            <p><strong>Analysis:</strong> Tests whether short-term signals predict longer-term outcomes using 20-day lead periods. 
            Shows actual correlations and p-values—no composite scores.</p>
            
            <h4>Summary Statistics</h4>
            {summary_grid}
            
            <h4>Lead-Lag Correlation Analysis by Company</h4>
            <p><em>All tests use 20-day lead period. Significance: p < 0.10. 
            Mom→Vol: momentum predicting volatility. Short→Long: momentum persistence.</em></p>
            {table_html}
            
            <h4>Visualizations</h4>
            {chart1}
            {chart2}
            {chart3}
            
            <div class="info-box info">
                <h4>Interpretation Guidelines</h4>
                <ul>
                    <li><strong>Mom→Vol:</strong> 20-day momentum (lagged 20d) predicting 60-day volatility</li>
                    <li><strong>Short→Long:</strong> 20-day returns (lagged 20d) predicting 60-day returns</li>
                    <li><strong>Positive Short→Long:</strong> Momentum persistence (winners continue)</li>
                    <li><strong>Negative Short→Long:</strong> Mean reversion (winners reverse)</li>
                    <li><strong>Lead Period:</strong> 20 trading days (~1 month) for practical utility</li>
                </ul>
            </div>
        </div>
    </div>
    """


def _create_chart_17c2_correlation_comparison(lead_lag_analysis: Dict) -> str:
    """Create correlation comparison"""
    companies = list(lead_lag_analysis.keys())
    mom_vol_corrs = []
    short_long_corrs = []
    
    for company in companies:
        metrics = lead_lag_analysis[company].get('lead_lag_metrics', {})
        mom_vol_corrs.append(abs(metrics.get('momentum_leads_volatility', {}).get('correlation', 0)))
        short_long_corrs.append(metrics.get('short_term_leads_long_term', {}).get('correlation', 0))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='|Mom→Vol|', x=companies, y=mom_vol_corrs, marker_color='#e74c3c'))
    fig.add_trace(go.Bar(name='Short→Long', x=companies, y=short_long_corrs, marker_color='#3498db'))
    fig.add_hline(y=0, line_color='black', line_width=1, opacity=0.3)
    
    fig.update_layout(title='Lead-Lag Correlation Strengths', xaxis_title='Company',
                     yaxis_title='Correlation', barmode='group', height=450)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_correlations")


def _create_chart_17c2_pvalue_scatter(lead_lag_analysis: Dict) -> str:
    """Create correlation vs p-value scatter"""
    correlations, pvalues, labels, colors = [], [], [], []
    
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
    fig.add_trace(go.Scatter(x=correlations, y=pvalues, mode='markers',
                            marker=dict(size=10, color=colors, line=dict(width=1, color='black')),
                            text=labels, hovertemplate='%{text}<br>r=%{x:.3f}<br>p=%{y:.3f}<extra></extra>'))
    
    fig.add_hline(y=0.10, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_vline(x=0, line_dash="solid", line_color="gray", opacity=0.3)
    
    fig.update_layout(title='Correlation Strength vs Statistical Significance',
                     xaxis_title='Correlation', yaxis_title='P-value (log scale)',
                     yaxis_type='log', height=500)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_pvalue")


def _create_chart_17c2_heatmap(lead_lag_analysis: Dict) -> str:
    """Create correlation heatmap"""
    companies = list(lead_lag_analysis.keys())
    metrics_names = ['Mom→Vol (|r|)', 'Short→Long (r)']
    
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
    
    fig = go.Figure(data=go.Heatmap(z=matrix, x=metrics_names, y=[c[:12] for c in companies],
                                     colorscale='RdYlGn', zmid=0,
                                     text=[[f"{val:.3f}" for val in row] for row in matrix],
                                     texttemplate='%{text}', colorbar=dict(title="Correlation")))
    
    fig.update_layout(title='Lead-Lag Correlation Heatmap (Top 10)', height=450)
    return build_plotly_chart(fig.to_dict(), div_id="chart_17c2_heatmap")


# =============================================================================
# 17E: STRATEGIC CROSS-ASSET INTELLIGENCE (NEW - COMPREHENSIVE)
# =============================================================================

def _build_section_17e_strategic_insights(
    all_analyses: Dict,
    companies: Dict[str, str]
) -> str:
    """Build 17E: Strategic Cross-Asset Intelligence - NO ARBITRARY SCORES"""
    
    # Extract key findings
    key_findings = _extract_key_findings(all_analyses, companies)
    
    # Build comparison matrix
    comparison_matrix = _build_comparison_matrix(all_analyses, companies)
    
    # Identify strongest signals
    strongest_signals = _identify_strongest_signals(all_analyses, companies)
    
    # Generate recommendations
    recommendations = _generate_investment_recommendations(all_analyses, companies)
    
    return f"""
    <div class="info-section">
        <h3 style="cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center;" 
            onclick="toggleCollapse('section_17e')">
            <span>17E: Strategic Cross-Asset Intelligence - Integrated Findings & Recommendations</span>
            <span id="icon_17e" style="transition: transform 0.3s;">▼</span>
        </h3>
        <div id="section_17e" style="display: block;">
            <p><strong>Overview:</strong> Synthesizes findings across all cross-asset analyses to identify 
            actionable investment insights based on actual correlations, returns, and statistical significance—no composite scores.</p>
            
            <h4>Executive Summary: Key Findings</h4>
            {key_findings}
            
            <h4>Multi-Company Signal Comparison Matrix</h4>
            {comparison_matrix}
            
            <h4>Strongest Predictive Signals by Company</h4>
            {strongest_signals}
            
            <h4>Strategic Investment Recommendations</h4>
            {recommendations}
            
            <div class="info-box default">
                <h4>Methodology Summary</h4>
                <p><strong>This analysis is based entirely on statistical evidence:</strong></p>
                <ul>
                    <li>All metrics are raw correlations, returns, or significance counts</li>
                    <li>No arbitrary scores, ratings, or composite indices used</li>
                    <li>Thresholds based on statistical significance (p-values) and practical materiality</li>
                    <li>Multiple timeframes analyzed independently (daily, monthly, annual, quarterly)</li>
                    <li>Lead-lag relationships tested with 20-day predictive window</li>
                </ul>
            </div>
        </div>
    </div>
    """


def _extract_key_findings(all_analyses: Dict, companies: Dict[str, str]) -> str:
    """Extract key findings from all analyses"""
    
    findings = []
    
    # Price-Fundamental findings
    if 'price_fundamental' in all_analyses and all_analyses['price_fundamental']:
        pf = all_analyses['price_fundamental']
        total_sig = sum(s['significant_signals'] for s in pf.values())
        total_tests = sum(s['total_signals'] for s in pf.values())
        sig_rate = (total_sig / total_tests * 100) if total_tests > 0 else 0
        
        findings.append({
            "icon": "📈",
            "title": "Price-Fundamental Signals",
            "metric": f"{total_sig}/{total_tests} significant",
            "description": f"{sig_rate:.0f}% of technical indicators successfully predict fundamental changes at 1-year horizon"
        })
    
    # Insider Response findings
    if 'insider_response' in all_analyses and all_analyses['insider_response']:
        insider = all_analyses['insider_response']
        returns_30d = [m.get('avg_return_30d_after_buy', 0) for m in insider.values() if 'avg_return_30d_after_buy' in m]
        avg_return = np.mean(returns_30d) if returns_30d else 0
        positive_count = sum(1 for r in returns_30d if r > 0)
        
        findings.append({
            "icon": "👥",
            "title": "Insider Buy Signals",
            "metric": f"{avg_return:+.1f}% avg return",
            "description": f"{positive_count}/{len(returns_30d)} companies show positive returns 30 days after insider purchases"
        })
    
    # Multi-timeframe findings
    if 'multi_timeframe' in all_analyses and all_analyses['multi_timeframe']:
        mt = all_analyses['multi_timeframe']
        both_signals = sum(1 for s in mt.values() if s['daily_significant'] > 0 and s['quarterly_significant'] > 0)
        total = len(mt)
        
        findings.append({
            "icon": "⏱️",
            "title": "Multi-Timeframe Consistency",
            "metric": f"{both_signals}/{total} companies",
            "description": f"{both_signals/total*100:.0f}% show predictive signals in both daily and quarterly timeframes"
        })
    
    # Lead-lag findings
    if 'lead_lag' in all_analyses and all_analyses['lead_lag']:
        ll = all_analyses['lead_lag']
        total_sig = sum(a['significant_patterns'] for a in ll.values())
        total_tests = sum(a['total_tested'] for a in ll.values())
        
        findings.append({
            "icon": "🔮",
            "title": "Lead-Lag Predictive Patterns",
            "metric": f"{total_sig}/{total_tests} significant",
            "description": f"{total_sig/total_tests*100:.0f}% of lead-lag relationships are statistically significant (20-day lead)"
        })
    
    # Build cards
    cards_html = '<div class="stat-grid">'
    for finding in findings:
        cards_html += f"""
        <div class="stat-card info">
            <div style="font-size: 2rem; margin-bottom: 10px;">{finding['icon']}</div>
            <div class="stat-label">{finding['title']}</div>
            <div class="stat-value" style="font-size: 1.8rem;">{finding['metric']}</div>
            <div class="stat-description">{finding['description']}</div>
        </div>
        """
    cards_html += '</div>'
    
    return cards_html


def _build_comparison_matrix(all_analyses: Dict, companies: Dict[str, str]) -> str:
    """Build multi-dimensional comparison matrix"""
    
    table_data = []
    
    for company_name in companies.keys():
        row = {'Company': company_name}
        
        # Price-Fundamental
        if 'price_fundamental' in all_analyses and company_name in all_analyses['price_fundamental']:
            pf = all_analyses['price_fundamental'][company_name]
            row['PF Sig'] = f"{pf['significant_signals']}/{pf['total_signals']}"
        else:
            row['PF Sig'] = "—"
        
        # Momentum-Fundamental
        if 'momentum_fundamental' in all_analyses and company_name in all_analyses['momentum_fundamental']:
            mf = all_analyses['momentum_fundamental'][company_name]
            pred_count = sum([mf.get('revenue_predictive', False), 
                            mf.get('margin_predictive', False), 
                            mf.get('profitability_predictive', False)])
            row['MF Pred'] = f"{pred_count}/3"
        else:
            row['MF Pred'] = "—"
        
        # Insider Response
        if 'insider_response' in all_analyses and company_name in all_analyses['insider_response']:
            insider = all_analyses['insider_response'][company_name]
            row['Insider 30d'] = f"{insider.get('avg_return_30d_after_buy', 0):+.1f}%"
            row['Success Rate'] = f"{insider.get('buy_success_rate', 0):.0%}"
        else:
            row['Insider 30d'] = "—"
            row['Success Rate'] = "—"
        
        # Multi-timeframe
        if 'multi_timeframe' in all_analyses and company_name in all_analyses['multi_timeframe']:
            mt = all_analyses['multi_timeframe'][company_name]
            has_both = "✓" if mt['daily_significant'] > 0 and mt['quarterly_significant'] > 0 else "✗"
            row['Both TF'] = has_both
        else:
            row['Both TF'] = "—"
        
        # Lead-lag
        if 'lead_lag' in all_analyses and company_name in all_analyses['lead_lag']:
            ll = all_analyses['lead_lag'][company_name]
            row['LL Sig'] = f"{ll['significant_patterns']}/{ll['total_tested']}"
        else:
            row['LL Sig'] = "—"
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    def both_color(val):
        return "excellent" if val == "✓" else "poor" if val == "✗" else "neutral"
    
    color_columns = {'Both TF': both_color}
    
    table_html = build_enhanced_table(df_table, table_id="table_17e_matrix",
                                     color_columns=color_columns, sortable=True, searchable=True)
    
    legend = """
    <div style="margin: 10px 0; padding: 15px; background: var(--card-bg); border-radius: 8px; border: 1px solid var(--card-border);">
        <strong>Legend:</strong> 
        PF Sig = Price-Fundamental significant/total | 
        MF Pred = Momentum-Fundamental predictive count | 
        Insider 30d = Avg return after buys | 
        Success Rate = % positive returns | 
        Both TF = Signals in both timeframes | 
        LL Sig = Lead-lag significant/total
    </div>
    """
    
    return legend + table_html


def _identify_strongest_signals(all_analyses: Dict, companies: Dict[str, str]) -> str:
    """Identify strongest signals per company"""
    
    company_strengths = {}
    
    for company_name in companies.keys():
        strengths = []
        
        # Check each analysis type
        if 'price_fundamental' in all_analyses and company_name in all_analyses['price_fundamental']:
            pf = all_analyses['price_fundamental'][company_name]
            if pf['significant_signals'] >= 2:
                strengths.append(f"Strong price-fundamental ({pf['significant_signals']}/3 sig)")
        
        if 'momentum_fundamental' in all_analyses and company_name in all_analyses['momentum_fundamental']:
            mf = all_analyses['momentum_fundamental'][company_name]
            pred_count = sum([mf.get('revenue_predictive', False), 
                            mf.get('margin_predictive', False), 
                            mf.get('profitability_predictive', False)])
            if pred_count >= 2:
                strengths.append(f"Broad momentum predictive ({pred_count}/3 metrics)")
        
        if 'insider_response' in all_analyses and company_name in all_analyses['insider_response']:
            insider = all_analyses['insider_response'][company_name]
            if insider.get('avg_return_30d_after_buy', 0) > 3 and insider.get('buy_success_rate', 0) > 0.55:
                strengths.append(f"Strong insider signal ({insider['avg_return_30d_after_buy']:+.1f}%, {insider['buy_success_rate']:.0%} success)")
        
        if 'multi_timeframe' in all_analyses and company_name in all_analyses['multi_timeframe']:
            mt = all_analyses['multi_timeframe'][company_name]
            if mt['daily_significant'] > 0 and mt['quarterly_significant'] > 0:
                strengths.append("Multi-timeframe consistency")
        
        if strengths:
            company_strengths[company_name] = strengths
    
    # Build display
    if not company_strengths:
        return '<div class="info-box warning"><p>No companies meet "strong signal" thresholds.</p></div>'
    
    strengths_html = ""
    for company, strength_list in sorted(company_strengths.items(), key=lambda x: len(x[1]), reverse=True):
        badge_type = "success" if len(strength_list) >= 3 else "info" if len(strength_list) >= 2 else "default"
        
        strengths_html += f"""
        <div style="margin: 15px 0; padding: 20px; background: var(--card-bg); border-radius: 12px; 
                   border-left: 4px solid {'#10b981' if badge_type == 'success' else '#3b82f6' if badge_type == 'info' else '#667eea'}; 
                   box-shadow: var(--shadow-sm);">
            <h4 style="margin: 0 0 10px 0; color: var(--text-primary);">
                {company} 
                <span style="background: {'#10b981' if badge_type == 'success' else '#3b82f6' if badge_type == 'info' else '#667eea'}; 
                            color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-left: 10px;">
                    {len(strength_list)} signals
                </span>
            </h4>
            <ul style="margin: 5px 0; padding-left: 20px;">
                {''.join(f'<li style="margin: 5px 0;">{strength}</li>' for strength in strength_list)}
            </ul>
        </div>
        """
    
    return strengths_html


def _generate_investment_recommendations(all_analyses: Dict, companies: Dict[str, str]) -> str:
    """Generate actionable recommendations based on findings"""
    
    recommendations = []
    
    # Recommendation 1: Best technical-fundamental alignment
    if 'price_fundamental' in all_analyses and all_analyses['price_fundamental']:
        pf = all_analyses['price_fundamental']
        best_companies = sorted(
            [(c, s['significant_signals']) for c, s in pf.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if best_companies and best_companies[0][1] >= 2:
            companies_str = ", ".join([c[0] for c in best_companies])
            recommendations.append({
                "title": "🎯 Technical Analysis Priority",
                "type": "success",
                "content": f"<strong>{companies_str}</strong> show the strongest price-fundamental predictive relationships. "
                          f"Technical indicators (momentum, RSI, volatility) successfully predict fundamental changes 1 year ahead. "
                          f"Consider using technical analysis as a timing tool for these stocks."
            })
    
    # Recommendation 2: Insider signal strength
    if 'insider_response' in all_analyses and all_analyses['insider_response']:
        insider = all_analyses['insider_response']
        strong_insider = [(c, m.get('avg_return_30d_after_buy', 0), m.get('buy_success_rate', 0))
                         for c, m in insider.items()
                         if m.get('avg_return_30d_after_buy', 0) > 2 and m.get('buy_success_rate', 0) > 0.55]
        
        if strong_insider:
            companies_str = ", ".join([f"{c} ({r:+.1f}%, {sr:.0%})" for c, r, sr in strong_insider[:3]])
            recommendations.append({
                "title": "👥 Insider Activity Monitoring",
                "type": "info",
                "content": f"Insider purchases at <strong>{companies_str}</strong> have been followed by positive returns. "
                          f"Monitor Form 4 filings for these companies as potential entry signals."
            })
    
    # Recommendation 3: Multi-timeframe consistency
    if 'multi_timeframe' in all_analyses and all_analyses['multi_timeframe']:
        mt = all_analyses['multi_timeframe']
        consistent = [c for c, s in mt.items() 
                     if s['daily_significant'] > 0 and s['quarterly_significant'] > 0]
        
        if len(consistent) >= 2:
            companies_str = ", ".join(consistent[:3])
            recommendations.append({
                "title": "⏱️ Multi-Timeframe Confirmation Strategy",
                "type": "success",
                "content": f"<strong>{companies_str}</strong> show predictive signals across multiple timeframes (daily + quarterly). "
                          f"These offer higher-confidence opportunities when signals align across timeframes."
            })
    
    # Recommendation 4: Momentum characteristics
    if 'lead_lag' in all_analyses and all_analyses['lead_lag']:
        ll = all_analyses['lead_lag']
        persistent = []
        reverting = []
        
        for c, analysis in ll.items():
            metrics = analysis.get('lead_lag_metrics', {})
            if 'short_term_leads_long_term' in metrics:
                stlt = metrics['short_term_leads_long_term']
                if stlt['significant']:
                    if stlt['correlation'] > 0:
                        persistent.append((c, stlt['correlation']))
                    else:
                        reverting.append((c, stlt['correlation']))
        
        if persistent:
            companies_str = ", ".join([c for c, _ in sorted(persistent, key=lambda x: x[1], reverse=True)[:3]])
            recommendations.append({
                "title": "🔮 Momentum Persistence",
                "type": "info",
                "content": f"<strong>{companies_str}</strong> exhibit momentum persistence (winners continue winning). "
                          f"Consider trend-following strategies for these stocks."
            })
        
        if reverting:
            companies_str = ", ".join([c for c, _ in sorted(reverting, key=lambda x: x[1])[:3]])
            recommendations.append({
                "title": "↩️ Mean Reversion Characteristics",
                "type": "warning",
                "content": f"<strong>{companies_str}</strong> show mean reversion tendencies (strong moves reverse). "
                          f"Contrarian strategies or profit-taking after rallies may be more appropriate."
            })
    
    # Build recommendations display
    if not recommendations:
        return '<div class="info-box warning"><p>Insufficient signal strength for specific recommendations.</p></div>'
    
    recs_html = ""
    for rec in recommendations:
        recs_html += f"""
        <div class="info-box {rec['type']}">
            <h4>{rec['title']}</h4>
            <p>{rec['content']}</p>
        </div>
        """
    
    recs_html += """
    <div class="info-box default">
        <h4>⚠️ Important Disclaimers</h4>
        <p><strong>These recommendations are based on historical statistical relationships and should not be considered investment advice.</strong></p>
        <ul>
            <li>Past correlations do not guarantee future relationships</li>
            <li>All investment decisions should consider broader market context, fundamental analysis, and risk tolerance</li>
            <li>Sample sizes vary by company and analysis type - review data quality metrics before acting</li>
            <li>Correlations measure linear relationships only and may miss non-linear dynamics</li>
            <li>Multiple hypothesis testing increases false positive risk - use appropriate skepticism</li>
        </ul>
    </div>
    """
    
    return recs_html


# =============================================================================
# ANALYSIS HELPER (NEW)
# =============================================================================

def _analyze_lead_lag_relationships(df_prices, df_financial, df_institutional, companies):
    """Analyze lead-lag relationships - RAW CORRELATIONS ONLY"""
    lead_lag_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            company_prices = df_prices[df_prices['symbol'] == ticker].copy()
            if company_prices.empty:
                continue
            
            company_prices['date'] = pd.to_datetime(company_prices['date'])
            company_prices = company_prices.sort_values('date')
            
            # Calculate returns
            company_prices['return_1d'] = company_prices['close'].pct_change() * 100
            company_prices['return_20d'] = company_prices['close'].pct_change(20) * 100
            company_prices['return_60d'] = company_prices['close'].pct_change(60) * 100
            company_prices['vol_60d'] = company_prices['return_1d'].rolling(60).std()
            
            lead_lag_metrics = {}
            sample_size = 0
            
            # Momentum leading volatility (20-day lead)
            valid_data = company_prices[['return_20d', 'vol_60d']].dropna()
            if len(valid_data) >= 30:
                valid_data = valid_data.copy()
                valid_data['return_20d_lead'] = valid_data['return_20d'].shift(20)
                lead_data = valid_data[['return_20d_lead', 'vol_60d']].dropna()
                
                if len(lead_data) >= 20:
                    corr, pval = stats.pearsonr(lead_data['return_20d_lead'], lead_data['vol_60d'])
                    lead_lag_metrics['momentum_leads_volatility'] = {
                        'correlation': abs(corr),
                        'p_value': pval,
                        'significant': pval < 0.10,
                        'lead_days': 20,
                        'n': len(lead_data)
                    }
                    sample_size = len(lead_data)
            
            # Short-term leading long-term (20-day lead)
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
            
            if lead_lag_metrics:
                significant_count = sum(1 for m in lead_lag_metrics.values() if m.get('significant', False))
                lead_lag_analysis[company_name] = {
                    'lead_lag_metrics': lead_lag_metrics,
                    'significant_patterns': significant_count,
                    'total_tested': len(lead_lag_metrics),
                    'sample_size': sample_size
                }
        except:
            continue
    
    return lead_lag_analysis