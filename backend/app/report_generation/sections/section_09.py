"""Section 9: Data-Driven Signal Discovery & Macro-Financial Analysis
Complete integrated version with all subsections and data caching fix
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import json

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_grid,
    build_data_table,
    build_plotly_chart,
    build_info_box,
    build_section_divider,
    build_enhanced_table,
    build_badge,
    build_score_badge,
    build_summary_card,
    build_progress_indicator,
    format_percentage,
    format_number
)


# =============================================================================
# MODULE-LEVEL DATA CACHE FOR SHARING BETWEEN SUBSECTIONS
# =============================================================================

_section_9_cache = {
    'correlation_analysis': None,
    'univariate_models': None,
    'multifactor_models': None,
    'model_diagnostics': None,
    'cache_key': None
}


def _get_cache_key(df: pd.DataFrame, economic_df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Generate a unique cache key for this analysis run"""
    return f"{len(df)}_{len(economic_df)}_{len(companies)}_{hash(tuple(companies.keys()))}"


def _get_or_generate_correlation_analysis(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                          companies: Dict[str, str]) -> Dict:
    """Get cached correlation analysis or generate if needed"""
    cache_key = _get_cache_key(df, economic_df, companies)
    
    if _section_9_cache['cache_key'] != cache_key or _section_9_cache['correlation_analysis'] is None:
        print("Section 9: Generating correlation analysis...")
        _section_9_cache['correlation_analysis'] = _analyze_comprehensive_correlations(df, economic_df, companies)
        _section_9_cache['cache_key'] = cache_key
    else:
        print("Section 9: Using cached correlation analysis")
    
    return _section_9_cache['correlation_analysis']


def _get_or_generate_univariate_models(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                       companies: Dict[str, str]) -> Dict:
    """Get cached univariate models or generate if needed"""
    cache_key = _get_cache_key(df, economic_df, companies)
    
    if _section_9_cache['cache_key'] != cache_key or _section_9_cache['univariate_models'] is None:
        print("Section 9: Generating univariate models...")
        correlation_analysis = _get_or_generate_correlation_analysis(df, economic_df, companies)
        _section_9_cache['univariate_models'] = _generate_univariate_models(df, economic_df, companies, correlation_analysis)
        _section_9_cache['cache_key'] = cache_key
    else:
        print("Section 9: Using cached univariate models")
    
    return _section_9_cache['univariate_models']


def _get_or_generate_multifactor_models(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                        companies: Dict[str, str]) -> Dict:
    """Get cached multifactor models or generate if needed"""
    cache_key = _get_cache_key(df, economic_df, companies)
    
    if _section_9_cache['cache_key'] != cache_key or _section_9_cache['multifactor_models'] is None:
        print("Section 9: Generating multifactor models...")
        correlation_analysis = _get_or_generate_correlation_analysis(df, economic_df, companies)
        univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
        _section_9_cache['multifactor_models'] = _generate_multifactor_models(df, economic_df, companies, 
                                                                              correlation_analysis, univariate_models)
        _section_9_cache['cache_key'] = cache_key
    else:
        print("Section 9: Using cached multifactor models")
    
    return _section_9_cache['multifactor_models']


def _get_or_generate_model_diagnostics(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                       companies: Dict[str, str]) -> Dict:
    """Get cached model diagnostics or generate if needed"""
    cache_key = _get_cache_key(df, economic_df, companies)
    
    if _section_9_cache['cache_key'] != cache_key or _section_9_cache['model_diagnostics'] is None:
        print("Section 9: Generating model diagnostics...")
        univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
        _section_9_cache['model_diagnostics'] = _generate_model_diagnostics(univariate_models)
        _section_9_cache['cache_key'] = cache_key
    else:
        print("Section 9: Using cached model diagnostics")
    
    return _section_9_cache['model_diagnostics']


# =============================================================================
# MAIN GENERATE FUNCTION
# =============================================================================

def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 9: Data-Driven Signal Discovery & Macro-Financial Analysis
    
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
        economic_df = collector.get_economic()
        
        # Build all subsections (data will be cached and reused)
        section_9a1_html = _build_section_9a1_comprehensive_correlation(df, economic_df, companies)
        section_9a2_html = _build_section_9a2_extended_correlation(df, economic_df, companies)
        section_9b1_html = _build_section_9b1_univariate_regression(df, economic_df, companies)
        section_9b2_html = _build_section_9b2_model_diagnostics(df, economic_df, companies)
        section_9c1_html = _build_section_9c1_multifactor_models(df, economic_df, companies)
        section_9c2_html = _build_section_9c2_model_comparison(df, economic_df, companies)
        section_9d_html = _build_section_9d_visualizations(df, economic_df, companies)
        section_9e_html = _build_section_9e_strategic_insights(df, economic_df, companies)
        
        # Combine all subsections
        content = f"""
        <div class="section-content-wrapper">
            {section_9a1_html}
            {build_section_divider() if section_9a2_html else ""}
            {section_9a2_html}
            {build_section_divider() if section_9b1_html else ""}
            {section_9b1_html}
            {build_section_divider() if section_9b2_html else ""}
            {section_9b2_html}
            {build_section_divider() if section_9c1_html else ""}
            {section_9c1_html}
            {build_section_divider() if section_9c2_html else ""}
            {section_9c2_html}
            {build_section_divider() if section_9d_html else ""}
            {section_9d_html}
            {build_section_divider() if section_9e_html else ""}
            {section_9e_html}
        </div>
        """
        
        return generate_section_wrapper(9, "Signal Discovery & Macro-Financial Analysis", content)
        
    except Exception as e:
        error_content = f"""
        <div class="section-content-wrapper">
            {build_info_box(f"<p>Error generating Section 9: {str(e)}</p>", "danger", "Section Generation Error")}
        </div>
        """
        return generate_section_wrapper(9, "Signal Discovery & Macro-Financial Analysis", error_content)


# =============================================================================
# SUBSECTION 9A.1: COMPREHENSIVE CORRELATION ANALYSIS
# =============================================================================

def _build_section_9a1_comprehensive_correlation(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                                 companies: Dict[str, str]) -> str:
    """Build subsection 9A.1: Comprehensive Correlation Analysis"""
    
    if economic_df.empty or df.empty:
        return build_info_box("<p>Insufficient data for correlation analysis.</p>", "warning", "Data Unavailable")
    
    # Use cached data
    correlation_analysis = _get_or_generate_correlation_analysis(df, economic_df, companies)
    
    if not correlation_analysis:
        return build_info_box("<p>No significant correlations found.</p>", "warning", "Analysis Results")
    
    # Build collapsible subsection
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9a1')">
            <h3>9A.1 Revenue Growth vs Macro Indicators - Comprehensive Correlation Scan</h3>
            <span class="toggle-icon" id="icon-section-9a1">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9a1">
    """
    
    # Summary statistics cards
    total_companies = len(correlation_analysis)
    total_significant = sum(len(analysis['significant_correlations']) for analysis in correlation_analysis.values())
    avg_significant = total_significant / total_companies if total_companies > 0 else 0
    
    strongest_correlations = []
    for company_data in correlation_analysis.values():
        if company_data['all_correlations']:
            strongest = max(company_data['all_correlations'].values(), key=lambda x: x['abs_correlation'])
            strongest_correlations.append(strongest['abs_correlation'])
    
    avg_strongest = np.mean(strongest_correlations) if strongest_correlations else 0
    
    summary_cards = [
        {
            "label": "Companies Analyzed",
            "value": str(total_companies),
            "description": "Portfolio coverage",
            "type": "info"
        },
        {
            "label": "Significant Correlations",
            "value": str(total_significant),
            "description": f"{avg_significant:.1f} per company",
            "type": "success" if avg_significant >= 3 else "warning"
        },
        {
            "label": "Average Strongest Correlation",
            "value": f"{avg_strongest:.3f}",
            "description": "Highest correlation strength",
            "type": "success" if avg_strongest >= 0.4 else "info"
        },
        {
            "label": "Signal Quality",
            "value": "Strong" if avg_significant >= 4 else "Moderate" if avg_significant >= 2 else "Developing",
            "description": "Overall assessment",
            "type": "success" if avg_significant >= 4 else "info" if avg_significant >= 2 else "warning"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    # Create correlation analysis table
    html += "<h4 style='margin-top: 30px;'>Correlation Analysis by Company</h4>"
    
    table_data = []
    for company_name, analysis in correlation_analysis.items():
        if analysis['top_positive']:
            top_pos = list(analysis['top_positive'].items())[0]
            top_pos_name = top_pos[0][:25]
            top_pos_corr = top_pos[1]['correlation']
            top_pos_sig = top_pos[1]['significance']
        else:
            top_pos_name = "None"
            top_pos_corr = np.nan
            top_pos_sig = ""
        
        if analysis['top_negative']:
            top_neg = list(analysis['top_negative'].items())[0]
            top_neg_name = top_neg[0][:25]
            top_neg_corr = top_neg[1]['correlation']
            top_neg_sig = top_neg[1]['significance']
        else:
            top_neg_name = "None"
            top_neg_corr = np.nan
            top_neg_sig = ""
        
        table_data.append({
            'Company': company_name,
            'Top Positive Indicator': f"{top_pos_name} ({top_pos[1]['lag_description']})" if analysis['top_positive'] else "None",
            'Positive Corr': f"{top_pos_corr:.3f}{top_pos_sig}" if not pd.isna(top_pos_corr) else "N/A",
            'Top Negative Indicator': f"{top_neg_name} ({top_neg[1]['lag_description']})" if analysis['top_negative'] else "None",
            'Negative Corr': f"{top_neg_corr:.3f}{top_neg_sig}" if not pd.isna(top_neg_corr) else "N/A",
            'Significant': len(analysis['significant_correlations']),
            'Total Tested': analysis['total_indicators_tested'],
            'Lag 0/1/2': f"{analysis['lag_distribution'][0]}/{analysis['lag_distribution'][1]}/{analysis['lag_distribution'][2]}"
        })
    
    correlation_table_df = pd.DataFrame(table_data)
    html += build_data_table(correlation_table_df, "correlation-analysis-table", sortable=True, searchable=True)
    
    # Generate summary insights
    indicator_frequency = {}
    for analysis in correlation_analysis.values():
        for indicator in analysis['significant_correlations'].keys():
            indicator_frequency[indicator] = indicator_frequency.get(indicator, 0) + 1
    
    most_common = sorted(indicator_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    all_strong = []
    for company, analysis in correlation_analysis.items():
        for indicator, stats in analysis['significant_correlations'].items():
            all_strong.append((company, indicator, stats['correlation'], stats['p_value']))
    
    all_strong.sort(key=lambda x: abs(x[2]), reverse=True)
    
    insight_text = f"""
    <p><strong>Portfolio Signal Coverage:</strong> {total_significant} significant correlations identified across {total_companies} companies ({avg_significant:.1f} per company)</p>
    <p><strong>Signal Consistency:</strong> {len(most_common)} indicators show recurring significance across multiple companies</p>
    <p><strong>Statistical Validation:</strong> {'Strong' if avg_significant >= 3 else 'Moderate' if avg_significant >= 1.5 else 'Weak'} correlation signal discovery rate</p>
    """
    
    if most_common:
        common_list = ", ".join([f"{ind} ({freq} companies)" for ind, freq in most_common[:3]])
        insight_text += f"<p><strong>Most Frequent Significant Indicators:</strong> {common_list}</p>"
    
    if all_strong:
        strongest_text = f"<p><strong>Strongest Portfolio Correlations:</strong></p><ul>"
        for i in range(min(2, len(all_strong))):
            company, indicator, corr, pval = all_strong[i]
            strongest_text += f"<li>{indicator} vs {company}: {corr:.3f} (p={pval:.3f})</li>"
        strongest_text += "</ul>"
        insight_text += strongest_text
    
    html += build_info_box(insight_text, "info", "Correlation Discovery Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 9A.2: EXTENDED CORRELATION ANALYSIS
# =============================================================================

def _build_section_9a2_extended_correlation(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                           companies: Dict[str, str]) -> str:
    """Build subsection 9A.2: Extended Financial Metrics Correlation Matrix"""
    
    if economic_df.empty or df.empty:
        return ""
    
    extended_correlation = _analyze_extended_correlations(df, economic_df, companies)
    
    if not extended_correlation:
        return build_info_box("<p>Insufficient data for extended correlation analysis.</p>", "warning", "Analysis Results")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9a2')">
            <h3>9A.2 Extended Financial Metrics Correlation Matrix</h3>
            <span class="toggle-icon" id="icon-section-9a2">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9a2">
    """
    
    all_metrics = set()
    for company_data in extended_correlation.values():
        all_metrics.update(company_data.keys())
    
    if not all_metrics:
        html += build_info_box("<p>No extended correlation data available.</p>", "warning")
        html += "</div></div>"
        return html
    
    html += "<h4>Strongest Macro Correlations by Financial Metric</h4>"
    html += "<p style='color: var(--text-secondary); margin-bottom: 20px;'>Each cell shows the strongest correlation coefficient for that metric. Significance: *** p<0.01, ** p<0.05, * p<0.10</p>"
    
    table_data = []
    sorted_metrics = sorted(all_metrics)
    
    for company_name, metrics_data in extended_correlation.items():
        row_data = {'Company': company_name}
        
        for metric in sorted_metrics:
            if metric in metrics_data:
                strongest = metrics_data[metric]['strongest_correlation']
                corr_val = strongest[1]['correlation']
                p_val = strongest[1]['p_value']
                
                if p_val < 0.01:
                    sig = "***"
                elif p_val < 0.05:
                    sig = "**"
                elif p_val < 0.10:
                    sig = "*"
                else:
                    sig = ""
                
                row_data[metric] = f"{corr_val:.3f}{sig}"
            else:
                row_data[metric] = "N/A"
        
        table_data.append(row_data)
    
    extended_table_df = pd.DataFrame(table_data)
    html += build_data_table(extended_table_df, "extended-correlation-table", sortable=True, searchable=True)
    
    metric_strength = {}
    for company_data in extended_correlation.values():
        for metric, data in company_data.items():
            if metric not in metric_strength:
                metric_strength[metric] = []
            metric_strength[metric].append(data['average_abs_correlation'])
    
    avg_metric_strength = {metric: np.mean(values) for metric, values in metric_strength.items()}
    strongest_metrics = sorted(avg_metric_strength.items(), key=lambda x: x[1], reverse=True)[:5]
    
    insight_text = f"""
    <p><strong>Metric Sensitivity Ranking:</strong> {strongest_metrics[0][0]} shows strongest average macro-correlation ({strongest_metrics[0][1]:.3f})</p>
    <p><strong>Cross-Metric Analysis:</strong> {len(strongest_metrics)} financial metrics demonstrate meaningful macro-economic sensitivity</p>
    <p><strong>Portfolio Correlation Breadth:</strong> {'Comprehensive' if len(strongest_metrics) >= 8 else 'Moderate' if len(strongest_metrics) >= 5 else 'Limited'} macro-financial relationship coverage</p>
    """
    
    if len(strongest_metrics) >= 3:
        top_metrics_list = ", ".join([f"{metric} ({strength:.3f})" for metric, strength in strongest_metrics[:3]])
        insight_text += f"<p><strong>Top Macro-Sensitive Financial Metrics:</strong> {top_metrics_list}</p>"
    
    html += build_info_box(insight_text, "info", "Extended Correlation Analysis Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 9B.1: UNIVARIATE REGRESSION
# =============================================================================

def _build_section_9b1_univariate_regression(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                            companies: Dict[str, str]) -> str:
    """Build subsection 9B.1: Univariate OLS Regression Analysis"""
    
    if economic_df.empty or df.empty:
        return ""
    
    univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
    
    if not univariate_models:
        return build_info_box("<p>Insufficient data for univariate regression analysis.</p>", "warning", "Analysis Results")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9b1')">
            <h3>9B.1 Univariate OLS Regression - Single-Factor Macro-Financial Relationships</h3>
            <span class="toggle-icon" id="icon-section-9b1">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9b1">
    """
    
    total_companies = len(univariate_models)
    r2_values = []
    excellent_count = 0
    good_count = 0
    
    for model_data in univariate_models.values():
        if model_data['best_model']:
            r2 = model_data['best_model'][1]['adj_r_squared']
            p_val = model_data['best_model'][1]['slope_pvalue']
            r2_values.append(r2)
            
            if r2 > 0.5 and p_val < 0.05:
                excellent_count += 1
            elif r2 > 0.3 and p_val < 0.10:
                good_count += 1
    
    avg_r2 = np.mean(r2_values) if r2_values else 0
    
    summary_cards = [
        {
            "label": "Models Generated",
            "value": str(total_companies),
            "description": "Companies with models",
            "type": "info"
        },
        {
            "label": "Average Adj R²",
            "value": f"{avg_r2:.3f}",
            "description": "Mean predictive power",
            "type": "success" if avg_r2 > 0.3 else "info" if avg_r2 > 0.15 else "warning"
        },
        {
            "label": "Excellent Models",
            "value": str(excellent_count),
            "description": f"R² > 0.5, p < 0.05",
            "type": "success"
        },
        {
            "label": "Model Quality",
            "value": "Strong" if avg_r2 > 0.3 else "Moderate" if avg_r2 > 0.15 else "Developing",
            "description": f"{excellent_count + good_count}/{total_companies} high quality",
            "type": "success" if avg_r2 > 0.3 else "info"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    html += "<h4 style='margin-top: 30px;'>Best Univariate Regression Models by Company</h4>"
    html += "<p style='color: var(--text-secondary); margin-bottom: 20px;'>Single-factor predictive models showing strongest macro-financial relationships</p>"
    
    table_data = []
    for company_name, model_data in univariate_models.items():
        if model_data['best_model']:
            indicator, stats = model_data['best_model']
            
            if stats['adj_r_squared'] > 0.5 and stats['slope_pvalue'] < 0.05:
                quality = "Excellent"
            elif stats['adj_r_squared'] > 0.3 and stats['slope_pvalue'] < 0.10:
                quality = "Good"
            elif stats['adj_r_squared'] > 0.1:
                quality = "Fair"
            else:
                quality = "Weak"
            
            table_data.append({
                'Company': company_name,
                'Best Predictor': indicator[:30],
                'Slope': f"{stats['slope']:.4f}",
                'T-Stat': f"{stats['slope_tstat']:.2f}",
                'P-Value': f"{stats['slope_pvalue']:.4f}",
                'Adj R²': f"{stats['adj_r_squared']:.4f}",
                'F-Stat': f"{stats['f_statistic']:.2f}",
                'N': stats['n_observations'],
                'Quality': quality
            })
    
    models_df = pd.DataFrame(table_data)
    
    color_columns = {
        'Quality': lambda x: 'excellent' if x == 'Excellent' else 'good' if x == 'Good' else 'fair' if x == 'Fair' else 'poor'
    }
    
    html += build_enhanced_table(models_df, "univariate-models-table", 
                                 color_columns=color_columns, 
                                 badge_columns=['Quality'],
                                 sortable=True, searchable=True)
    
    predictor_frequency = {}
    for model_data in univariate_models.values():
        if model_data['best_model']:
            predictor = model_data['best_model'][0]
            predictor_frequency[predictor] = predictor_frequency.get(predictor, 0) + 1
    
    top_predictors = sorted(predictor_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
    
    insight_text = f"""
    <p><strong>Model Performance Portfolio:</strong> {avg_r2:.3f} average adjusted R² across {total_companies} companies</p>
    <p><strong>Model Quality Distribution:</strong> {excellent_count} excellent, {good_count} good models from {total_companies} total companies</p>
    <p><strong>Predictive Power Assessment:</strong> {'Strong' if avg_r2 > 0.4 else 'Moderate' if avg_r2 > 0.2 else 'Weak'} single-factor predictive capability</p>
    """
    
    if top_predictors:
        top_list = ", ".join([f"{pred} ({freq} companies)" for pred, freq in top_predictors])
        insight_text += f"<p><strong>Top Performing Macro Predictors:</strong> {top_list}</p>"
    
    insight_text += f"""
    <p><strong>Statistical Validation:</strong> {excellent_count + good_count}/{total_companies} companies with statistically significant predictive relationships</p>
    <p><strong>Economic Interpretation:</strong> {'High confidence' if excellent_count >= total_companies * 0.4 else 'Moderate confidence' if good_count >= total_companies * 0.5 else 'Limited confidence'} in macro-financial predictive models</p>
    """
    
    html += build_info_box(insight_text, "info", "Univariate Regression Analysis Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 9B.2: MODEL DIAGNOSTICS
# =============================================================================

def _build_section_9b2_model_diagnostics(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                        companies: Dict[str, str]) -> str:
    """Build subsection 9B.2: Statistical Model Diagnostics & Validation"""
    
    if economic_df.empty or df.empty:
        return ""
    
    model_diagnostics = _get_or_generate_model_diagnostics(df, economic_df, companies)
    
    if not model_diagnostics:
        return build_info_box("<p>Model diagnostics unavailable.</p>", "warning", "Diagnostics Status")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9b2')">
            <h3>9B.2 Statistical Model Diagnostics & Validation</h3>
            <span class="toggle-icon" id="icon-section-9b2">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9b2">
    """
    
    avg_diag_score = np.mean([diag['diagnostic_score'] for diag in model_diagnostics.values()])
    normal_count = sum(1 for diag in model_diagnostics.values() if diag['normality_status'] == 'Normal')
    good_autocorr = sum(1 for diag in model_diagnostics.values() if 1.5 <= diag['durbin_watson'] <= 2.5)
    homoscedastic = sum(1 for diag in model_diagnostics.values() if diag['breusch_pagan_pvalue'] > 0.05)
    total_models = len(model_diagnostics)
    
    summary_cards = [
        {
            "label": "Average Diagnostic Score",
            "value": f"{avg_diag_score:.1f}/10",
            "description": "Overall quality",
            "type": "success" if avg_diag_score >= 7 else "info" if avg_diag_score >= 5 else "warning"
        },
        {
            "label": "Normal Residuals",
            "value": f"{normal_count}/{total_models}",
            "description": "Jarque-Bera test",
            "type": "success" if normal_count >= total_models * 0.6 else "info"
        },
        {
            "label": "Good Autocorrelation",
            "value": f"{good_autocorr}/{total_models}",
            "description": "DW ∈ [1.5, 2.5]",
            "type": "success" if good_autocorr >= total_models * 0.7 else "info"
        },
        {
            "label": "Homoscedastic",
            "value": f"{homoscedastic}/{total_models}",
            "description": "Breusch-Pagan test",
            "type": "success" if homoscedastic >= total_models * 0.6 else "info"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    html += "<h4 style='margin-top: 30px;'>Model Diagnostic Test Results</h4>"
    html += "<p style='color: var(--text-secondary); margin-bottom: 20px;'>Statistical validation of regression model assumptions</p>"
    
    table_data = []
    for model_name, diagnostics in model_diagnostics.items():
        table_data.append({
            'Model': model_name[:25],
            'Durbin-Watson': f"{diagnostics['durbin_watson']:.3f}",
            'JB P-Value': f"{diagnostics['jarque_bera_pvalue']:.3f}",
            'BP P-Value': f"{diagnostics['breusch_pagan_pvalue']:.3f}",
            'VIF': f"{diagnostics['vif']:.2f}",
            'Residual SD': f"{diagnostics['residual_std']:.4f}",
            'Normality': diagnostics['normality_status'],
            'Diagnostic Score': f"{diagnostics['diagnostic_score']:.1f}/10"
        })
    
    diag_df = pd.DataFrame(table_data)
    
    color_columns = {
        'Normality': lambda x: 'excellent' if x == 'Normal' else 'fair' if x == 'Questionable' else 'poor'
    }
    
    html += build_enhanced_table(diag_df, "diagnostics-table",
                                 color_columns=color_columns,
                                 badge_columns=['Normality'],
                                 sortable=True, searchable=True)
    
    guide_text = """
    <h4>Diagnostic Test Interpretation:</h4>
    <ul>
        <li><strong>Durbin-Watson (1.5-2.5 ideal):</strong> Tests for autocorrelation in residuals. Values near 2 indicate no autocorrelation.</li>
        <li><strong>Jarque-Bera (p > 0.05):</strong> Tests residual normality. Higher p-values indicate normal distribution.</li>
        <li><strong>Breusch-Pagan (p > 0.05):</strong> Tests for heteroscedasticity. Higher p-values indicate constant variance.</li>
        <li><strong>VIF (< 5 ideal):</strong> Variance Inflation Factor. For univariate models, always ≈1 (no multicollinearity).</li>
        <li><strong>Diagnostic Score:</strong> Composite quality measure (0-10) based on all tests.</li>
    </ul>
    """
    
    html += build_info_box(guide_text, "info", "Understanding Diagnostic Tests")
    
    insight_text = f"""
    <p><strong>Overall Diagnostic Quality:</strong> {avg_diag_score:.1f}/10 average diagnostic score across {total_models} models</p>
    <p><strong>Residual Normality:</strong> {normal_count}/{total_models} models pass normality tests (Jarque-Bera p>0.05)</p>
    <p><strong>Autocorrelation Assessment:</strong> {good_autocorr}/{total_models} models show appropriate Durbin-Watson statistics (1.5-2.5)</p>
    <p><strong>Homoscedasticity Validation:</strong> {homoscedastic}/{total_models} models pass heteroscedasticity tests (Breusch-Pagan p>0.05)</p>
    <p><strong>Model Validity:</strong> {'High confidence' if avg_diag_score >= 7 and normal_count >= total_models * 0.6 else 'Moderate confidence' if avg_diag_score >= 5 else 'Caution advised'} in statistical assumptions</p>
    <p><strong>Regression Robustness:</strong> {'Strong' if good_autocorr >= total_models * 0.7 and homoscedastic >= total_models * 0.6 else 'Adequate' if good_autocorr >= total_models * 0.5 else 'Weak'} statistical foundation</p>
    """
    
    html += build_info_box(insight_text, "success" if avg_diag_score >= 7 else "info", 
                          "Model Diagnostics Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 9C.1: MULTIFACTOR MODELS
# =============================================================================

def _build_section_9c1_multifactor_models(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                         companies: Dict[str, str]) -> str:
    """Build subsection 9C.1: Multifactor OLS Regression Models"""
    
    if economic_df.empty or df.empty:
        return ""
    
    univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
    multifactor_models = _get_or_generate_multifactor_models(df, economic_df, companies)
    
    if not multifactor_models:
        return build_info_box("<p>Insufficient data for multifactor regression analysis.</p>", 
                            "warning", "Analysis Results")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9c1')">
            <h3>9C.1 Multifactor OLS Regression - Complex Macro-Financial Interaction Models</h3>
            <span class="toggle-icon" id="icon-section-9c1">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9c1">
    """
    
    total_companies = len(multifactor_models)
    
    improvements = []
    for company, mf_data in multifactor_models.items():
        if mf_data['best_model'] and company in univariate_models and univariate_models[company]['best_model']:
            mf_r2 = mf_data['best_model'][1]['adj_r_squared']
            uni_r2 = univariate_models[company]['best_model'][1]['adj_r_squared']
            improvements.append(mf_r2 - uni_r2)
    
    avg_improvement = np.mean(improvements) if improvements else 0
    
    mf_r2_values = []
    excellent_count = 0
    good_count = 0
    
    for model_data in multifactor_models.values():
        if model_data['best_model']:
            stats = model_data['best_model'][1]
            mf_r2_values.append(stats['adj_r_squared'])
            
            if stats['adj_r_squared'] > 0.6 and stats['f_pvalue'] < 0.05 and stats['max_vif'] < 5:
                excellent_count += 1
            elif stats['adj_r_squared'] > 0.4 and stats['f_pvalue'] < 0.10 and stats['max_vif'] < 10:
                good_count += 1
    
    avg_mf_r2 = np.mean(mf_r2_values) if mf_r2_values else 0
    
    summary_cards = [
        {
            "label": "Multifactor Models",
            "value": str(total_companies),
            "description": "Complex models generated",
            "type": "info"
        },
        {
            "label": "Average Adj R²",
            "value": f"{avg_mf_r2:.3f}",
            "description": "Multifactor performance",
            "type": "success" if avg_mf_r2 > 0.4 else "info"
        },
        {
            "label": "R² Improvement",
            "value": f"+{avg_improvement:.3f}" if avg_improvement > 0 else f"{avg_improvement:.3f}",
            "description": "vs Univariate models",
            "type": "success" if avg_improvement > 0.1 else "info" if avg_improvement > 0 else "warning"
        },
        {
            "label": "Model Quality",
            "value": f"{excellent_count + good_count}/{total_companies}",
            "description": "High-quality models",
            "type": "success" if (excellent_count + good_count) >= total_companies * 0.5 else "info"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    html += "<h4 style='margin-top: 30px;'>Best Multifactor Regression Models by Company</h4>"
    html += "<p style='color: var(--text-secondary); margin-bottom: 20px;'>Complex models incorporating multiple macro-economic predictors</p>"
    
    table_data = []
    for company_name, model_data in multifactor_models.items():
        if model_data['best_model']:
            model_name, stats = model_data['best_model']
            
            predictors_text = ", ".join([pred[:12] for pred in stats['predictors']])
            if len(predictors_text) > 35:
                predictors_text = predictors_text[:32] + "..."
            
            if stats['adj_r_squared'] > 0.6 and stats['f_pvalue'] < 0.05 and stats['max_vif'] < 5:
                quality = "Excellent"
            elif stats['adj_r_squared'] > 0.4 and stats['f_pvalue'] < 0.10 and stats['max_vif'] < 10:
                quality = "Good"
            elif stats['adj_r_squared'] > 0.2:
                quality = "Fair"
            else:
                quality = "Weak"
            
            table_data.append({
                'Company': company_name,
                'Model Type': model_name.replace('_', ' '),
                'Predictors': predictors_text,
                'Adj R²': f"{stats['adj_r_squared']:.4f}",
                'F-Stat': f"{stats['f_statistic']:.2f}",
                'F P-Val': f"{stats['f_pvalue']:.4f}",
                'AIC': f"{stats['aic']:.1f}",
                'Max VIF': f"{stats['max_vif']:.2f}",
                'Quality': quality
            })
    
    mf_df = pd.DataFrame(table_data)
    
    color_columns = {
        'Quality': lambda x: 'excellent' if x == 'Excellent' else 'good' if x == 'Good' else 'fair' if x == 'Fair' else 'poor'
    }
    
    html += build_enhanced_table(mf_df, "multifactor-models-table",
                                 color_columns=color_columns,
                                 badge_columns=['Quality'],
                                 sortable=True, searchable=True)
    
    insight_text = f"""
    <p><strong>Model Enhancement Performance:</strong> {avg_improvement:.3f} average adjusted R² improvement over univariate models</p>
    <p><strong>Multifactor Model Quality:</strong> {avg_mf_r2:.3f} average adjusted R² across {total_companies} companies</p>
    <p><strong>Model Complexity Validation:</strong> {excellent_count} excellent, {good_count} good multifactor models from {total_companies} companies</p>
    <p><strong>Complexity Benefit:</strong> {'Significant' if avg_improvement > 0.1 else 'Moderate' if avg_improvement > 0.05 else 'Marginal'} improvement from multifactor modeling</p>
    <p><strong>Statistical Robustness:</strong> {excellent_count + good_count}/{total_companies} models meet multicollinearity and significance standards</p>
    <p><strong>Predictive Power:</strong> {'High' if avg_mf_r2 > 0.5 else 'Moderate' if avg_mf_r2 > 0.3 else 'Limited'} explanatory capability from multifactor framework</p>
    """
    
    html += build_info_box(insight_text, "info", "Multifactor Regression Analysis Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# SUBSECTION 9C.2: MODEL COMPARISON
# =============================================================================

def _build_section_9c2_model_comparison(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                       companies: Dict[str, str]) -> str:
    """Build subsection 9C.2: Model Performance Comparison & Selection Framework"""
    
    if economic_df.empty or df.empty:
        return ""
    
    univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
    multifactor_models = _get_or_generate_multifactor_models(df, economic_df, companies)
    
    if not univariate_models and not multifactor_models:
        return ""
    
    model_comparison = _generate_model_comparison(univariate_models, multifactor_models)
    
    if not model_comparison:
        return build_info_box("<p>Model comparison analysis unavailable.</p>", "warning")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9c2')">
            <h3>9C.2 Model Performance Comparison & Selection Framework</h3>
            <span class="toggle-icon" id="icon-section-9c2">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9c2">
    """
    
    uni_models = [m for m in model_comparison.values() if m['model_type'] == 'Univariate']
    mf_models = [m for m in model_comparison.values() if m['model_type'] == 'Multifactor']
    
    uni_avg_r2 = np.mean([m['adj_r_squared'] for m in uni_models]) if uni_models else 0
    mf_avg_r2 = np.mean([m['adj_r_squared'] for m in mf_models]) if mf_models else 0
    
    best_model = max(model_comparison.values(), key=lambda x: x['selection_score'])
    high_quality_count = sum(1 for m in model_comparison.values() if m['selection_score'] >= 7)
    
    summary_cards = [
        {
            "label": "Total Models Compared",
            "value": str(len(model_comparison)),
            "description": f"{len(uni_models)} Uni + {len(mf_models)} Multi",
            "type": "info"
        },
        {
            "label": "Best Model Type",
            "value": best_model['model_type'],
            "description": f"Score: {best_model['selection_score']:.1f}/10",
            "type": "success"
        },
        {
            "label": "Univariate Avg R²",
            "value": f"{uni_avg_r2:.3f}",
            "description": "Single-factor models",
            "type": "info"
        },
        {
            "label": "Multifactor Avg R²",
            "value": f"{mf_avg_r2:.3f}",
            "description": "Complex models",
            "type": "success" if mf_avg_r2 > uni_avg_r2 else "info"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    html += "<h4 style='margin-top: 30px;'>Comprehensive Model Performance Comparison</h4>"
    html += "<p style='color: var(--text-secondary); margin-bottom: 20px;'>Ranked by selection score (combines R², significance, and parsimony)</p>"
    
    table_data = []
    for model_id, comparison in model_comparison.items():
        table_data.append({
            'Rank': comparison['model_rank'],
            'Model Type': comparison['model_type'],
            'Model Name': comparison['model_name'][:30],
            'Company': comparison['company'][:15],
            'Adj R²': f"{comparison['adj_r_squared']:.4f}",
            'AIC': f"{comparison['aic']:.1f}",
            'BIC': f"{comparison['bic']:.1f}",
            'F-Stat': f"{comparison['f_statistic']:.2f}",
            'F P-Val': f"{comparison['f_pvalue']:.4f}",
            'Selection Score': f"{comparison['selection_score']:.1f}/10"
        })
    
    comparison_df = pd.DataFrame(table_data)
    comparison_df = comparison_df.sort_values('Rank')
    
    html += build_data_table(comparison_df, "model-comparison-table", sortable=True, searchable=True)
    
    top_5_models = sorted(model_comparison.items(), key=lambda x: x[1]['selection_score'], reverse=True)[:5]
    
    top_models_text = "<h4>Top 5 Models by Selection Score:</h4><ol>"
    for model_id, model_info in top_5_models:
        top_models_text += f"<li><strong>{model_info['model_name']}</strong> ({model_info['model_type']}) - "
        top_models_text += f"Score: {model_info['selection_score']:.1f}, R²: {model_info['adj_r_squared']:.3f}, "
        top_models_text += f"p={model_info['f_pvalue']:.4f}</li>"
    top_models_text += "</ol>"
    
    html += build_info_box(top_models_text, "success", "Best Performing Models")
    
    insight_text = f"""
    <p><strong>Model Type Performance:</strong> Univariate avg R² = {uni_avg_r2:.3f}, Multifactor avg R² = {mf_avg_r2:.3f}</p>
    <p><strong>Best Overall Model:</strong> {best_model['model_name']} ({best_model['model_type']}) with {best_model['selection_score']:.1f}/10 selection score</p>
    <p><strong>High-Quality Models:</strong> {high_quality_count}/{len(model_comparison)} models achieve selection scores ≥7.0</p>
    <p><strong>Complexity vs Performance:</strong> {'Multifactor models justify complexity' if mf_avg_r2 > uni_avg_r2 + 0.1 else 'Mixed evidence for complexity benefit' if mf_avg_r2 > uni_avg_r2 else 'Univariate models perform competitively'}</p>
    <p><strong>Statistical Robustness:</strong> {sum(1 for m in model_comparison.values() if m['f_pvalue'] < 0.05)}/{len(model_comparison)} models statistically significant at 5% level</p>
    <p><strong>Information Criteria Validation:</strong> AIC and BIC rankings {'align with' if abs(uni_avg_r2 - mf_avg_r2) < 0.05 else 'support'} R² performance assessment</p>
    """
    
    html += build_info_box(insight_text, "info", "Model Selection Framework Summary")
    
    html += """
        </div>
    </div>
    """
    
    return html

"""
Drop-in Replacement for _build_section_9d_visualizations()
Complete subsection 9D with all 25 standalone Plotly charts

INSTRUCTIONS:
1. Copy all chart functions from the two artifacts (section_09_charts_pt1 and section_09_charts_pt2)
   and paste them at the END of your section_09_v1.py file (after all helper functions)

2. Replace your existing _build_section_9d_visualizations() function with this one

3. Done! You now have all 25 charts integrated.
"""

from typing import Dict, Optional


def _build_section_9d_visualizations(df, economic_df, companies):
    """
    Build subsection 9D: Signal Discovery Visualization Analysis
    Complete with all 25 standalone Plotly charts
    """
    
    if economic_df.empty or df.empty:
        return build_info_box("<p>Insufficient data for visualization analysis.</p>", 
                            "warning", "Analysis Results")
    
    # Get all cached data (reuses existing cache)
    correlation_analysis = _get_or_generate_correlation_analysis(df, economic_df, companies)
    univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
    multifactor_models = _get_or_generate_multifactor_models(df, economic_df, companies)
    model_diagnostics = _get_or_generate_model_diagnostics(df, economic_df, companies)
    
    # Get extended correlation data for chart 23
    extended_correlation = _analyze_extended_correlations(df, economic_df, companies)
    
    # Get model comparison data for chart 24
    model_comparison = _generate_model_comparison(univariate_models, multifactor_models)
    
    if not correlation_analysis:
        return build_info_box("<p>Insufficient data for visualization analysis.</p>", 
                            "warning", "Analysis Results")
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9d')">
            <h3>9D. Signal Discovery Visualization Analysis</h3>
            <span class="toggle-icon" id="icon-section-9d">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9d">
    """
    
    html += '<p style="color: var(--text-secondary); margin-bottom: 30px; font-size: 1.05rem;">Comprehensive visual analysis of macro-financial relationships, model performance, and signal quality across 25 interactive charts</p>'
    
    # ==========================================================================
    # GROUP 1: CORRELATION ANALYSIS (Charts 1-5)
    # ==========================================================================
    
    html += '<div style="margin: 40px 0;"><h3 style="color: var(--primary-gradient-start); border-bottom: 2px solid var(--primary-gradient-start); padding-bottom: 10px;">Group 1: Correlation Analysis</h3></div>'
    
    # Chart 1: Correlation Heatmap
    chart1 = create_chart_01_correlation_heatmap(correlation_analysis)
    if chart1:
        html += '<h4 style="margin-top: 30px;">📊 Chart 1: Correlation Heatmap Matrix</h4>'
        html += build_plotly_chart(chart1, "chart-9d-01", height=600)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Companies vs Top 20 macro indicators showing correlation strength with color intensity</p>'
    
    # Chart 2: Top Correlations Bar
    chart2 = create_chart_02_top_correlations_bar(correlation_analysis)
    if chart2:
        html += '<h4 style="margin-top: 30px;">🎯 Chart 2: Top 15 Strongest Correlations</h4>'
        html += build_plotly_chart(chart2, "chart-9d-02", height=600)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Strongest positive and negative correlations with statistical significance indicators (*** p<0.01, ** p<0.05, * p<0.10)</p>'
    
    # Chart 3: Correlation Distribution
    chart3 = create_chart_03_correlation_distribution(correlation_analysis)
    if chart3:
        html += '<h4 style="margin-top: 30px;">📈 Chart 3: Correlation Strength Distribution</h4>'
        html += build_plotly_chart(chart3, "chart-9d-03", height=500)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Histogram showing distribution of correlation strengths with mean and median indicators</p>'
    
    # Chart 4: P-value vs Correlation Scatter
    chart4 = create_chart_04_pvalue_vs_correlation_scatter(correlation_analysis)
    if chart4:
        html += '<h4 style="margin-top: 30px;">🔬 Chart 4: Statistical Significance Analysis</h4>'
        html += build_plotly_chart(chart4, "chart-9d-04", height=600)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">P-value vs correlation scatter plot showing significance zones (log scale)</p>'
    
    # Chart 5: Company Sensitivity Rankings
    chart5 = create_chart_05_company_sensitivity_rankings(correlation_analysis)
    if chart5:
        html += '<h4 style="margin-top: 30px;">🏆 Chart 5: Company Macro-Sensitivity Rankings</h4>'
        html += build_plotly_chart(chart5, "chart-9d-05", height=600)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Composite sensitivity score combining correlation strength and significant indicator count</p>'
    
    html += build_section_divider()
    
    # ==========================================================================
    # GROUP 2: UNIVARIATE REGRESSION ANALYSIS (Charts 6-9)
    # ==========================================================================
    
    html += '<div style="margin: 40px 0;"><h3 style="color: var(--primary-gradient-start); border-bottom: 2px solid var(--primary-gradient-start); padding-bottom: 10px;">Group 2: Univariate Regression Analysis</h3></div>'
    
    if univariate_models:
        # Chart 6: Univariate R² Comparison
        chart6 = create_chart_06_univariate_r2_comparison(univariate_models)
        if chart6:
            html += '<h4 style="margin-top: 30px;">📊 Chart 6: Univariate Model R² Performance</h4>'
            html += build_plotly_chart(chart6, "chart-9d-06", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Single-factor predictive power by company with quality color coding</p>'
        
        # Chart 7: Slope Coefficients
        chart7 = create_chart_07_slope_coefficients(univariate_models)
        if chart7:
            html += '<h4 style="margin-top: 30px;">📐 Chart 7: Regression Slope Coefficients</h4>'
            html += build_plotly_chart(chart7, "chart-9d-07", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Revenue growth sensitivity to macro variables (% change per unit)</p>'
        
        # Chart 8: Statistical Significance Scatter
        chart8 = create_chart_08_statistical_significance_scatter(univariate_models)
        if chart8:
            html += '<h4 style="margin-top: 30px;">🔬 Chart 8: Statistical Significance Volcano Plot</h4>'
            html += build_plotly_chart(chart8, "chart-9d-08", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">T-statistic vs -log10(p-value) with bubble size indicating R²</p>'
        
        # Chart 9: Model Quality Pie
        chart9 = create_chart_09_model_quality_pie(univariate_models)
        if chart9:
            html += '<h4 style="margin-top: 30px;">📊 Chart 9: Model Quality Distribution</h4>'
            html += build_plotly_chart(chart9, "chart-9d-09", height=550)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Portfolio breakdown by model quality (Excellent/Good/Fair/Weak)</p>'
    
    html += build_section_divider()
    
    # ==========================================================================
    # GROUP 3: MULTIFACTOR MODEL ANALYSIS (Charts 10-13)
    # ==========================================================================
    
    html += '<div style="margin: 40px 0;"><h3 style="color: var(--primary-gradient-start); border-bottom: 2px solid var(--primary-gradient-start); padding-bottom: 10px;">Group 3: Multifactor Model Analysis</h3></div>'
    
    if univariate_models and multifactor_models:
        # Chart 10: Univariate vs Multifactor Comparison
        chart10 = create_chart_10_uni_vs_multi_comparison(univariate_models, multifactor_models)
        if chart10:
            html += '<h4 style="margin-top: 30px;">📊 Chart 10: Univariate vs Multifactor R² Comparison</h4>'
            html += build_plotly_chart(chart10, "chart-9d-10", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Grouped bar chart comparing single-factor vs multi-factor model performance</p>'
        
        # Chart 11: R² Improvement
        chart11 = create_chart_11_r2_improvement(univariate_models, multifactor_models)
        if chart11:
            html += '<h4 style="margin-top: 30px;">📈 Chart 11: Multifactor R² Improvement</h4>'
            html += build_plotly_chart(chart11, "chart-9d-11", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Incremental R² gain from adding additional predictors (sorted by improvement)</p>'
        
        # Chart 12: AIC Comparison
        chart12 = create_chart_12_aic_comparison(univariate_models, multifactor_models)
        if chart12:
            html += '<h4 style="margin-top: 30px;">📉 Chart 12: AIC Model Comparison</h4>'
            html += build_plotly_chart(chart12, "chart-9d-12", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Information criteria comparison (positive = multifactor preferred)</p>'
    
    if multifactor_models:
        # Chart 13: Complexity vs Performance
        chart13 = create_chart_13_complexity_vs_performance(multifactor_models)
        if chart13:
            html += '<h4 style="margin-top: 30px;">🎯 Chart 13: Model Complexity vs Performance</h4>'
            html += build_plotly_chart(chart13, "chart-9d-13", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Scatter plot with bubble size = R², color = VIF (multicollinearity)</p>'
    
    html += build_section_divider()
    
    # ==========================================================================
    # GROUP 4: MODEL DIAGNOSTICS (Charts 14-17)
    # ==========================================================================
    
    html += '<div style="margin: 40px 0;"><h3 style="color: var(--primary-gradient-start); border-bottom: 2px solid var(--primary-gradient-start); padding-bottom: 10px;">Group 4: Model Diagnostics & Validation</h3></div>'
    
    if model_diagnostics:
        # Chart 14: Diagnostic Scores
        chart14 = create_chart_14_diagnostic_scores(model_diagnostics)
        if chart14:
            html += '<h4 style="margin-top: 30px;">✅ Chart 14: Model Diagnostic Quality Scores</h4>'
            html += build_plotly_chart(chart14, "chart-9d-14", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Composite diagnostic score (0-10) based on all statistical tests</p>'
        
        # Chart 15: Durbin-Watson Test
        chart15 = create_chart_15_durbin_watson_test(model_diagnostics)
        if chart15:
            html += '<h4 style="margin-top: 30px;">🔄 Chart 15: Durbin-Watson Autocorrelation Test</h4>'
            html += build_plotly_chart(chart15, "chart-9d-15", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Tests for residual autocorrelation (ideal range: 1.5-2.5)</p>'
        
        # Chart 16: Normality Test
        chart16 = create_chart_16_normality_test(model_diagnostics)
        if chart16:
            html += '<h4 style="margin-top: 30px;">📊 Chart 16: Jarque-Bera Normality Test</h4>'
            html += build_plotly_chart(chart16, "chart-9d-16", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Tests for normal distribution of residuals (higher is better on log scale)</p>'
        
        # Chart 17: Heteroscedasticity Test
        chart17 = create_chart_17_heteroscedasticity_test(model_diagnostics)
        if chart17:
            html += '<h4 style="margin-top: 30px;">📈 Chart 17: Breusch-Pagan Heteroscedasticity Test</h4>'
            html += build_plotly_chart(chart17, "chart-9d-17", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Tests for constant variance (homoscedasticity, higher is better)</p>'
    
    html += build_section_divider()
    
    # ==========================================================================
    # GROUP 5: SIGNAL DISCOVERY SUMMARY (Charts 18-22)
    # ==========================================================================
    
    html += '<div style="margin: 40px 0;"><h3 style="color: var(--primary-gradient-start); border-bottom: 2px solid var(--primary-gradient-start); padding-bottom: 10px;">Group 5: Signal Discovery Summary Dashboard</h3></div>'
    
    # Chart 18: Portfolio Metrics Summary
    chart18 = create_chart_18_portfolio_metrics_summary(correlation_analysis, univariate_models, multifactor_models)
    if chart18:
        html += '<h4 style="margin-top: 30px;">📊 Chart 18: Portfolio Signal Discovery Performance</h4>'
        html += build_plotly_chart(chart18, "chart-9d-18", height=550)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Key portfolio-level metrics on normalized 0-10 scale</p>'
    
    # Chart 19: Signal Quality Pie
    chart19 = create_chart_19_signal_quality_pie(correlation_analysis)
    if chart19:
        html += '<h4 style="margin-top: 30px;">🎯 Chart 19: Signal Quality Distribution</h4>'
        html += build_plotly_chart(chart19, "chart-9d-19", height=550)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Portfolio breakdown by signal strength (Strong/Moderate/Weak)</p>'
    
    # Chart 20: Model Performance Evolution
    chart20 = create_chart_20_model_performance_evolution(univariate_models, multifactor_models)
    if chart20:
        html += '<h4 style="margin-top: 30px;">📈 Chart 20: Model Performance Evolution</h4>'
        html += build_plotly_chart(chart20, "chart-9d-20", height=600)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Line chart showing progression from baseline to univariate to multifactor models</p>'
    
    # Chart 21: Top Predictive Indicators
    chart21 = create_chart_21_top_predictive_indicators(correlation_analysis)
    if chart21:
        html += '<h4 style="margin-top: 30px;">🏆 Chart 21: Most Predictive Economic Indicators</h4>'
        html += build_plotly_chart(chart21, "chart-9d-21", height=600)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Top 12 macro indicators by frequency of significant correlations across portfolio</p>'
    
    # Chart 22: Intelligence Score Gauge
    chart22 = create_chart_22_intelligence_score_gauge(correlation_analysis, univariate_models, multifactor_models)
    if chart22:
        html += '<h4 style="margin-top: 30px;">🎯 Chart 22: Portfolio Intelligence Score</h4>'
        html += build_plotly_chart(chart22, "chart-9d-22", height=450)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Composite gauge showing overall macro-financial intelligence capability (0-10)</p>'
    
    html += build_section_divider()
    
    # ==========================================================================
    # GROUP 6: SPECIALTY CHARTS (Charts 23-25)
    # ==========================================================================
    
    html += '<div style="margin: 40px 0;"><h3 style="color: var(--primary-gradient-start); border-bottom: 2px solid var(--primary-gradient-start); padding-bottom: 10px;">Group 6: Advanced Analysis</h3></div>'
    
    # Chart 23: Extended Correlation Heatmap
    if extended_correlation:
        chart23 = create_chart_23_extended_correlation_heatmap(extended_correlation)
        if chart23:
            html += '<h4 style="margin-top: 30px;">📊 Chart 23: Extended Financial Metrics Correlation Heatmap</h4>'
            html += build_plotly_chart(chart23, "chart-9d-23", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Strongest macro correlations across multiple financial metrics (beyond revenue growth)</p>'
    
    # Chart 24: Model Comparison Scatter
    if model_comparison:
        chart24 = create_chart_24_model_comparison_scatter(univariate_models, multifactor_models, model_comparison)
        if chart24:
            html += '<h4 style="margin-top: 30px;">🎯 Chart 24: Model Comparison - Performance vs Parsimony</h4>'
            html += build_plotly_chart(chart24, "chart-9d-24", height=600)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Scatter plot: R² vs AIC showing optimal model selection (top-left quadrant best)</p>'
    
    # Chart 25: Lag Distribution Analysis (NEW!)
    chart25 = create_chart_25_lag_distribution_dashboard(correlation_analysis)
    if chart25:
        html += '<h4 style="margin-top: 30px;">⏱️ Chart 25: Lag Distribution Analysis - Leading vs Coincident Indicators</h4>'
        html += build_plotly_chart(chart25, "chart-9d-25", height=800)
        html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Comprehensive 4-panel dashboard showing lag structure: Lag 0 = contemporaneous, Lag 1-2 = leading indicators predicting future revenue</p>'
    else:
        # Fallback to simple version
        chart25_simple = create_chart_25_simple_lag_bars(correlation_analysis)
        if chart25_simple:
            html += '<h4 style="margin-top: 30px;">⏱️ Chart 25: Lag Distribution Analysis</h4>'
            html += build_plotly_chart(chart25_simple, "chart-9d-25", height=550)
            html += '<p style="color: var(--text-secondary); font-style: italic; margin-bottom: 30px;">Distribution showing leading indicators (Lag 1-2) vs coincident indicators (Lag 0)</p>'
    
    # Summary insight box - count charts that were actually generated
    total_charts_shown = 0
    
    # Initialize all chart variables to track which ones were created
    charts_created = {
        'chart1': 'chart1' in locals() and chart1 is not None,
        'chart2': 'chart2' in locals() and chart2 is not None,
        'chart3': 'chart3' in locals() and chart3 is not None,
        'chart4': 'chart4' in locals() and chart4 is not None,
        'chart5': 'chart5' in locals() and chart5 is not None,
        'chart6': 'chart6' in locals() and chart6 is not None,
        'chart7': 'chart7' in locals() and chart7 is not None,
        'chart8': 'chart8' in locals() and chart8 is not None,
        'chart9': 'chart9' in locals() and chart9 is not None,
        'chart10': 'chart10' in locals() and chart10 is not None,
        'chart11': 'chart11' in locals() and chart11 is not None,
        'chart12': 'chart12' in locals() and chart12 is not None,
        'chart13': 'chart13' in locals() and chart13 is not None,
        'chart14': 'chart14' in locals() and chart14 is not None,
        'chart15': 'chart15' in locals() and chart15 is not None,
        'chart16': 'chart16' in locals() and chart16 is not None,
        'chart17': 'chart17' in locals() and chart17 is not None,
        'chart18': 'chart18' in locals() and chart18 is not None,
        'chart19': 'chart19' in locals() and chart19 is not None,
        'chart20': 'chart20' in locals() and chart20 is not None,
        'chart21': 'chart21' in locals() and chart21 is not None,
        'chart22': 'chart22' in locals() and chart22 is not None,
        'chart23': 'chart23' in locals() and chart23 is not None,
        'chart24': 'chart24' in locals() and chart24 is not None,
        'chart25': ('chart25' in locals() and chart25 is not None) or ('chart25_simple' in locals() and chart25_simple is not None)
    }
    
    total_charts_shown = sum(charts_created.values())
    
    summary_text = f"""
    <p><strong>Visualization Summary:</strong> {total_charts_shown} interactive charts generated across 6 analytical groups</p>
    <ul>
        <li><strong>Group 1 (5 charts):</strong> Correlation analysis - heatmap, top correlations, distributions, significance testing</li>
        <li><strong>Group 2 (4 charts):</strong> Univariate regression - R² performance, slopes, significance, quality distribution</li>
        <li><strong>Group 3 (4 charts):</strong> Multifactor models - comparison, improvement, AIC, complexity vs performance</li>
        <li><strong>Group 4 (4 charts):</strong> Model diagnostics - overall scores, Durbin-Watson, normality, heteroscedasticity</li>
        <li><strong>Group 5 (5 charts):</strong> Signal discovery summary - portfolio metrics, quality, evolution, top indicators, intelligence gauge</li>
        <li><strong>Group 6 (3 charts):</strong> Advanced analysis - extended correlations, model comparison, lag distribution</li>
    </ul>
    <p><strong>Interactive Features:</strong> All charts support hover details, zooming, panning, and screenshot download</p>
    """
    
    html += build_info_box(summary_text, "success", "📊 Complete Visualization Suite")
    
    html += """
        </div>
    </div>
    """
    
    return html


# =============================================================================
# NOTE: Copy all chart functions from the two artifacts here
# Paste them below this line (create_chart_01 through create_chart_25)
# =============================================================================

# ... paste all chart functions here ...





# =============================================================================
# NOTE: Copy all chart functions from the two artifacts here
# Paste them below this line (create_chart_01 through create_chart_25)
# =============================================================================

# ... paste all chart functions here ...


# =============================================================================
# SUBSECTION 9E: STRATEGIC INSIGHTS (Condensed version with key sections)
# =============================================================================

def _build_section_9e_strategic_insights(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                        companies: Dict[str, str]) -> str:
    """Build subsection 9E: Economic Interpretation & Strategic Signal Framework"""
    
    if economic_df.empty or df.empty:
        return ""
    
    correlation_analysis = _get_or_generate_correlation_analysis(df, economic_df, companies)
    univariate_models = _get_or_generate_univariate_models(df, economic_df, companies)
    multifactor_models = _get_or_generate_multifactor_models(df, economic_df, companies)
    model_diagnostics = _get_or_generate_model_diagnostics(df, economic_df, companies)
    
    if not correlation_analysis:
        return build_info_box("<p>Insufficient data for strategic insights analysis.</p>", 
                            "warning", "Analysis Results")
    
    insights = _generate_comprehensive_insights(correlation_analysis, univariate_models, 
                                               multifactor_models, model_diagnostics, companies)
    
    html = """
    <div class="subsection-container">
        <div class="subsection-header" onclick="toggleSubsection('section-9e')">
            <h3>9E. Economic Interpretation & Strategic Signal Framework</h3>
            <span class="toggle-icon" id="icon-section-9e">▼</span>
        </div>
        <div class="subsection-content" id="content-section-9e">
    """
    
    html += "<p style='color: var(--text-secondary); margin-bottom: 30px; font-size: 1.05rem;'>Comprehensive macro-financial intelligence framework with strategic recommendations and actionable insights</p>"
    
    # Build all 5 subsections
    html += _build_relationship_strength_section(insights)
    html += _build_signal_quality_section(insights)
    html += _build_cycle_sensitivity_section(insights)
    html += _build_intelligence_framework_section(insights)
    html += _build_strategy_recommendations_section(insights)
    
    html += """
        </div>
    </div>
    """
    
    return html

def _analyze_comprehensive_correlations(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                       companies: Dict[str, str]) -> Dict[str, Dict]:
    """Generate comprehensive correlation analysis with lag support (0, 1, 2 years)"""
    
    if economic_df.empty or df.empty:
        return {}
    
    correlation_results = {}
    
    # Prepare economic data
    econ_data = economic_df.set_index('Year') if 'Year' in economic_df.columns else economic_df
    numeric_econ_cols = econ_data.select_dtypes(include=[np.number]).columns
    econ_numeric = econ_data[numeric_econ_cols]
    
    print(f"Testing correlations with lags [0, 1, 2] years across {len(numeric_econ_cols)} macro indicators...")
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 3:
            continue
        
        # Calculate revenue growth (use existing if available)
        company_data = company_data.copy()
        if 'revenue_YoY' in company_data.columns:
            company_data['revenue_growth'] = company_data['revenue_YoY']
        else:
            company_data['revenue_growth'] = company_data['revenue'].pct_change() * 100
        
        # Merge with economic data
        merged_data = company_data.set_index('Year').merge(econ_numeric, left_index=True, right_index=True, how='inner')
        
        if len(merged_data) < 3:
            continue
        
        correlations = {}
        
        for macro_indicator in econ_numeric.columns:
            if macro_indicator not in merged_data.columns or 'revenue_growth' not in merged_data.columns:
                continue
            
            # Get base data
            revenue_growth = merged_data['revenue_growth'].dropna()
            macro_values = merged_data[macro_indicator].dropna()
            
            # Find common indices
            common_index = revenue_growth.index.intersection(macro_values.index)
            
            if len(common_index) < 3:
                continue
            
            # Test multiple lags (0, 1, 2 years)
            best_corr = None
            best_lag = 0
            best_p_value = 1.0
            best_n = 0
            
            for lag in [0, 1, 2]:
                try:
                    # For lag > 0: Revenue Growth(t) correlates with Macro(t-lag)
                    # Shift macro indicator forward by 'lag' periods (so it aligns with future revenue)
                    if lag > 0:
                        # Create lagged macro: shift index forward
                        macro_lagged = macro_values.copy()
                        macro_lagged.index = macro_lagged.index + lag
                    else:
                        macro_lagged = macro_values
                    
                    # Find common indices after lag adjustment
                    common_lagged = revenue_growth.index.intersection(macro_lagged.index)
                    
                    if len(common_lagged) < 3:
                        continue
                    
                    rev_common = revenue_growth[common_lagged]
                    macro_common = macro_lagged[common_lagged]
                    
                    # Calculate correlation
                    corr_coef, p_value = stats.pearsonr(rev_common, macro_common)
                    
                    # Keep the best correlation (by absolute value)
                    if best_corr is None or abs(corr_coef) > abs(best_corr):
                        best_corr = corr_coef
                        best_lag = lag
                        best_p_value = p_value
                        best_n = len(common_lagged)
                
                except Exception as e:
                    continue
            
            # Store best correlation found across all lags
            if best_corr is not None:
                # Determine significance level
                if best_p_value < 0.01:
                    significance = "***"
                elif best_p_value < 0.05:
                    significance = "**"
                elif best_p_value < 0.10:
                    significance = "*"
                else:
                    significance = ""
                
                correlations[macro_indicator] = {
                    'correlation': best_corr,
                    'p_value': best_p_value,
                    'n_observations': best_n,
                    'significance': significance,
                    'abs_correlation': abs(best_corr),
                    'best_lag': best_lag,  # NEW: which lag worked best
                    'lag_description': f"Lag {best_lag}Y" if best_lag > 0 else "Contemporaneous"
                }
        
        if correlations:
            # Sort by absolute correlation strength
            sorted_correlations = dict(sorted(correlations.items(), 
                                            key=lambda x: x[1]['abs_correlation'], 
                                            reverse=True))
            
            # Get top positive and negative correlations
            positive_corrs = {k: v for k, v in sorted_correlations.items() if v['correlation'] > 0}
            negative_corrs = {k: v for k, v in sorted_correlations.items() if v['correlation'] < 0}
            
            # Count by lag
            lag_counts = {0: 0, 1: 0, 2: 0}
            for corr_data in sorted_correlations.values():
                lag_counts[corr_data['best_lag']] += 1
            
            print(f"  {company_name}: Found {len(sorted_correlations)} correlations " + 
                  f"(Lag 0: {lag_counts[0]}, Lag 1: {lag_counts[1]}, Lag 2: {lag_counts[2]})")
            
            correlation_results[company_name] = {
                'all_correlations': sorted_correlations,
                'top_positive': dict(list(positive_corrs.items())[:5]),
                'top_negative': dict(list(negative_corrs.items())[:5]),
                'strongest_overall': max(sorted_correlations.items(), key=lambda x: x[1]['abs_correlation']),
                'significant_correlations': {k: v for k, v in sorted_correlations.items() if v['p_value'] < 0.05},
                'total_indicators_tested': len(correlations),
                'lag_distribution': lag_counts  # NEW: how many correlations at each lag
            }
    
    return correlation_results


def _analyze_extended_correlations(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                   companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze correlations for multiple financial metrics beyond revenue growth"""
    
    if economic_df.empty or df.empty:
        return {}
    
    # Key financial metrics to analyze
    financial_metrics = [
        'revenue_YoY', 'netIncome_YoY', 'operatingIncome_YoY', 'ebitda_YoY',
        'grossProfitMargin', 'operatingProfitMargin', 'netProfitMargin',
        'returnOnEquity', 'returnOnAssets', 'currentRatio', 'debtToEquityRatio'
    ]
    
    extended_results = {}
    
    # Prepare economic data
    econ_data = economic_df.set_index('Year') if 'Year' in economic_df.columns else economic_df
    numeric_econ_cols = econ_data.select_dtypes(include=[np.number]).columns
    econ_numeric = econ_data[numeric_econ_cols]
    
    for company_name in companies.keys():
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        if len(company_data) < 3:
            continue
        
        # Calculate growth rates if not present
        company_data = company_data.copy()
        for metric in ['revenue', 'netIncome', 'operatingIncome', 'ebitda']:
            if metric in company_data.columns and f"{metric}_YoY" not in company_data.columns:
                company_data[f"{metric}_YoY"] = company_data[metric].pct_change() * 100
        
        # Merge with economic data
        merged_data = company_data.set_index('Year').merge(econ_numeric, left_index=True, right_index=True, how='inner')
        
        if len(merged_data) < 3:
            continue
        
        metric_correlations = {}
        
        for financial_metric in financial_metrics:
            if financial_metric not in merged_data.columns:
                continue
            
            correlations = {}
            
            for macro_indicator in econ_numeric.columns:
                if macro_indicator in merged_data.columns:
                    # Calculate correlation
                    financial_values = merged_data[financial_metric].dropna()
                    macro_values = merged_data[macro_indicator].dropna()
                    
                    # Find common indices
                    common_index = financial_values.index.intersection(macro_values.index)
                    
                    if len(common_index) >= 3:
                        fin_common = financial_values[common_index]
                        macro_common = macro_values[common_index]
                        
                        try:
                            # Calculate correlation and p-value
                            corr_coef, p_value = stats.pearsonr(fin_common, macro_common)
                            
                            if not np.isnan(corr_coef):
                                correlations[macro_indicator] = {
                                    'correlation': corr_coef,
                                    'p_value': p_value,
                                    'abs_correlation': abs(corr_coef)
                                }
                        except:
                            continue
            
            if correlations:
                # Find strongest correlation for this metric
                strongest = max(correlations.items(), key=lambda x: x[1]['abs_correlation'])
                significant = {k: v for k, v in correlations.items() if v['p_value'] < 0.05}
                
                metric_correlations[financial_metric] = {
                    'strongest_correlation': strongest,
                    'significant_count': len(significant),
                    'average_abs_correlation': np.mean([v['abs_correlation'] for v in correlations.values()])
                }
        
        if metric_correlations:
            extended_results[company_name] = metric_correlations
    
    return extended_results

def _generate_univariate_models(df: pd.DataFrame, economic_df: pd.DataFrame, 
                               companies: Dict[str, str], 
                               correlation_analysis: Dict) -> Dict[str, Dict]:
    """Generate univariate OLS regression models"""
    
    if economic_df.empty or df.empty or not correlation_analysis:
        return {}
    
    univariate_models = {}
    
    # Prepare economic data
    econ_data = economic_df.set_index('Year') if 'Year' in economic_df.columns else economic_df
    numeric_econ_cols = econ_data.select_dtypes(include=[np.number]).columns
    econ_numeric = econ_data[numeric_econ_cols]
    
    for company_name in companies.keys():
        if company_name not in correlation_analysis:
            continue
        
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        # Calculate revenue growth
        company_data = company_data.copy()
        company_data['revenue_growth'] = company_data['revenue'].pct_change() * 100
        
        # Merge with economic data
        merged_data = company_data.set_index('Year').merge(econ_numeric, left_index=True, right_index=True, how='inner')
        
        if len(merged_data) < 4:
            continue
        
        # Get top 5 strongest correlations
        top_correlations = dict(list(correlation_analysis[company_name]['all_correlations'].items())[:5])
        
        company_models = {}
        
        for indicator, corr_stats in top_correlations.items():
            if indicator not in merged_data.columns or abs(corr_stats['correlation']) < 0.3:
                continue
            
            y = merged_data['revenue_growth'].dropna()
            x = merged_data[indicator].dropna()
            
            common_index = y.index.intersection(x.index)
            
            if len(common_index) >= 4:
                y_reg = y[common_index]
                x_reg = x[common_index]
                
                X_reg = sm.add_constant(x_reg)
                
                try:
                    model = sm.OLS(y_reg, X_reg).fit()
                    
                    company_models[indicator] = {
                        'slope': model.params.iloc[1] if len(model.params) > 1 else 0,
                        'intercept': model.params.iloc[0],
                        'slope_tstat': model.tvalues.iloc[1] if len(model.tvalues) > 1 else 0,
                        'slope_pvalue': model.pvalues.iloc[1] if len(model.pvalues) > 1 else 1,
                        'r_squared': model.rsquared,
                        'adj_r_squared': model.rsquared_adj,
                        'f_statistic': model.fvalue,
                        'f_pvalue': model.f_pvalue,
                        'aic': model.aic,
                        'bic': model.bic,
                        'n_observations': len(common_index),
                        'residual_std_error': np.sqrt(model.mse_resid),
                        'model_object': model,
                        'x_data': x_reg,
                        'y_data': y_reg
                    }
                except Exception as e:
                    continue
        
        if company_models:
            ranked_models = dict(sorted(company_models.items(), 
                                      key=lambda x: x[1]['adj_r_squared'], 
                                      reverse=True))
            
            univariate_models[company_name] = {
                'models': ranked_models,
                'best_model': list(ranked_models.items())[0] if ranked_models else None,
                'model_count': len(ranked_models)
            }
    
    return univariate_models


def _generate_model_diagnostics(univariate_models: Dict[str, Dict]) -> Dict[str, Dict]:
    """Generate comprehensive model diagnostics"""
    
    model_diagnostics = {}
    print(f"DEBUG DIAG: Got {len(univariate_models)} univariate models")
    
    for company_name, model_data in univariate_models.items():
        if not model_data['best_model']:
            continue
        
        best_indicator, best_stats = model_data['best_model']
        
        if 'model_object' not in best_stats:
            print(f"DEBUG DIAG: {company_name} missing model_object")
            continue
        
        model = best_stats['model_object']
        
        try:
            from statsmodels.stats.diagnostic import durbin_watson, jarque_bera, het_breuschpagan
            
            # Durbin-Watson test
            dw_stat = durbin_watson(model.resid)
            
            # Jarque-Bera test
            jb_stat, jb_pvalue, _, _ = jarque_bera(model.resid)
            
            # Breusch-Pagan test
            bp_stat, bp_pvalue, _, _ = het_breuschpagan(model.resid, model.model.exog)
            
            # VIF (always 1 for univariate)
            vif = 1.0
            
            # Residual std
            residual_std = np.std(model.resid)
            
            # Normality status
            if jb_pvalue > 0.05:
                normality_status = "Normal"
            elif jb_pvalue > 0.01:
                normality_status = "Questionable"
            else:
                normality_status = "Non-normal"
            
            # Diagnostic score
            score_components = [
                10 if 1.5 <= dw_stat <= 2.5 else 5 if 1.0 <= dw_stat <= 3.0 else 2,
                10 if jb_pvalue > 0.05 else 6 if jb_pvalue > 0.01 else 2,
                10 if bp_pvalue > 0.05 else 6 if bp_pvalue > 0.01 else 2,
                10 if best_stats['adj_r_squared'] > 0.5 else 6 if best_stats['adj_r_squared'] > 0.3 else 2
            ]
            
            diagnostic_score = np.mean(score_components)
            
            model_diagnostics[f"{company_name}_{best_indicator[:15]}"] = {
                'durbin_watson': dw_stat,
                'jarque_bera_stat': jb_stat,
                'jarque_bera_pvalue': jb_pvalue,
                'breusch_pagan_stat': bp_stat,
                'breusch_pagan_pvalue': bp_pvalue,
                'vif': vif,
                'residual_std': residual_std,
                'normality_status': normality_status,
                'diagnostic_score': diagnostic_score
            }
            
        except Exception as e:
            continue
    
    return model_diagnostics


def _generate_multifactor_models(df: pd.DataFrame, economic_df: pd.DataFrame, 
                                companies: Dict[str, str], correlation_analysis: Dict,
                                univariate_models: Dict) -> Dict[str, Dict]:
    """Generate multifactor OLS regression models"""
    print(f"DEBUG MF: Got {len(companies)} companies")
    print(f"DEBUG MF: correlation_analysis has {len(correlation_analysis)} entries")

    if economic_df.empty or df.empty or not correlation_analysis:
        return {}
    
    multifactor_models = {}
    
    # Prepare economic data
    econ_data = economic_df.set_index('Year') if 'Year' in economic_df.columns else economic_df
    numeric_econ_cols = econ_data.select_dtypes(include=[np.number]).columns
    econ_numeric = econ_data[numeric_econ_cols]
    
    for company_name in companies.keys():
        if company_name not in correlation_analysis:
            continue
        
        company_data = df[df['Company'] == company_name].sort_values('Year')
        
        company_data = company_data.copy()
        company_data['revenue_growth'] = company_data['revenue'].pct_change() * 100
        
        merged_data = company_data.set_index('Year').merge(econ_numeric, left_index=True, right_index=True, how='inner')
        
        if len(merged_data) < 6:
            continue
        
        significant_correlations = correlation_analysis[company_name]['significant_correlations']
        print(f"DEBUG MF: {company_name} has {len(significant_correlations)} significant correlations")
        
        if len(significant_correlations) < 2:
            continue
        
        sorted_predictors = sorted(significant_correlations.items(), 
                                 key=lambda x: x[1]['abs_correlation'], reverse=True)
        
        company_models = {}
        
        # Model 1: Top 2 predictors
        if len(sorted_predictors) >= 2:
            predictors = [sorted_predictors[0][0], sorted_predictors[1][0]]
            model_result = _fit_multifactor_model(merged_data, predictors, 'revenue_growth')
            if model_result:
                company_models['Top_2_Predictors'] = model_result
        
        # Model 2: Top 3 predictors
        if len(sorted_predictors) >= 3 and len(merged_data) >= 8:
            predictors = [sorted_predictors[0][0], sorted_predictors[1][0], sorted_predictors[2][0]]
            model_result = _fit_multifactor_model(merged_data, predictors, 'revenue_growth')
            if model_result:
                company_models['Top_3_Predictors'] = model_result
        
        # Model 3: Thematic model (growth + inflation)
        growth_indicators = ['Real_GDP', 'GDP', 'Industrial_Production', 'Nonfarm_Payrolls']
        inflation_indicators = ['CPI_All_Items', 'Core_CPI', 'PCE_Price_Index']
        
        available_growth = [ind for ind in growth_indicators if ind in merged_data.columns and ind in significant_correlations]
        available_inflation = [ind for ind in inflation_indicators if ind in merged_data.columns and ind in significant_correlations]
        
        if available_growth and available_inflation:
            thematic_predictors = [available_growth[0], available_inflation[0]]
            model_result = _fit_multifactor_model(merged_data, thematic_predictors, 'revenue_growth')
            if model_result:
                company_models['Growth_Inflation_Model'] = model_result
        
        if company_models:
            ranked_models = dict(sorted(company_models.items(), key=lambda x: x[1]['aic']))
            
            multifactor_models[company_name] = {
                'models': ranked_models,
                'best_model': list(ranked_models.items())[0] if ranked_models else None,
                'model_count': len(ranked_models)
            }
    
    return multifactor_models


def _fit_multifactor_model(merged_data: pd.DataFrame, predictors: List[str], 
                          target: str) -> Optional[Dict]:
    """Fit a multifactor regression model"""
    
    try:
        y = merged_data[target].dropna()
        x_data = merged_data[predictors].dropna()
        
        common_index = y.index.intersection(x_data.index)
        
        if len(common_index) < len(predictors) + 2:
            return None
        
        y_reg = y[common_index]
        X_reg = x_data.loc[common_index]
        
        # Check multicollinearity
        correlation_matrix = X_reg.corr()
        max_corr = 0
        for i in range(len(correlation_matrix)):
            for j in range(i+1, len(correlation_matrix)):
                max_corr = max(max_corr, abs(correlation_matrix.iloc[i, j]))
        
        if max_corr > 0.8:
            return None
        
        X_reg_const = sm.add_constant(X_reg)
        
        model = sm.OLS(y_reg, X_reg_const).fit()
        
        # Calculate VIFs
        vifs = []
        for i in range(1, X_reg_const.shape[1]):
            vif = variance_inflation_factor(X_reg_const.values, i)
            vifs.append(vif)
        
        max_vif = max(vifs) if vifs else 0
        
        # Extract coefficients
        coefficients = {}
        for i, predictor in enumerate(predictors):
            if i + 1 < len(model.params):
                coefficients[predictor] = {
                    'coefficient': model.params.iloc[i + 1],
                    'tstat': model.tvalues.iloc[i + 1],
                    'pvalue': model.pvalues.iloc[i + 1]
                }
        
        return {
            'predictors': predictors,
            'coefficients': coefficients,
            'intercept': model.params.iloc[0],
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'f_statistic': model.fvalue,
            'f_pvalue': model.f_pvalue,
            'aic': model.aic,
            'bic': model.bic,
            'n_observations': len(common_index),
            'max_vif': max_vif,
            'residual_std_error': np.sqrt(model.mse_resid),
            'model_object': model
        }
        
    except Exception as e:
        return None


def _generate_model_comparison(univariate_models: Dict[str, Dict], 
                               multifactor_models: Dict[str, Dict]) -> Dict[str, Dict]:
    """Generate comprehensive model comparison analysis"""
    
    model_comparison = {}
    comparison_id = 0
    
    # Add univariate models
    for company_name, model_data in univariate_models.items():
        if model_data['best_model']:
            indicator, stats = model_data['best_model']
            
            model_comparison[f"UNI_{comparison_id}"] = {
                'model_type': 'Univariate',
                'model_name': f"{company_name}_{indicator[:15]}",
                'company': company_name,
                'adj_r_squared': stats['adj_r_squared'],
                'aic': stats['aic'],
                'bic': stats['bic'],
                'f_statistic': stats['f_statistic'],
                'f_pvalue': stats['f_pvalue'],
                'n_observations': stats['n_observations']
            }
            comparison_id += 1
    
    # Add multifactor models
    for company_name, model_data in multifactor_models.items():
        if model_data['best_model']:
            model_name, stats = model_data['best_model']
            
            model_comparison[f"MF_{comparison_id}"] = {
                'model_type': 'Multifactor',
                'model_name': f"{company_name}_{model_name}",
                'company': company_name,
                'adj_r_squared': stats['adj_r_squared'],
                'aic': stats['aic'],
                'bic': stats['bic'],
                'f_statistic': stats['f_statistic'],
                'f_pvalue': stats['f_pvalue'],
                'n_observations': stats['n_observations']
            }
            comparison_id += 1
    
    # Rank models
    all_models = list(model_comparison.items())
    
    # Rank by R²
    r2_ranking = sorted(all_models, key=lambda x: x[1]['adj_r_squared'], reverse=True)
    for rank, (model_id, _) in enumerate(r2_ranking):
        model_comparison[model_id]['r2_rank'] = rank + 1
    
    # Rank by AIC
    aic_ranking = sorted(all_models, key=lambda x: x[1]['aic'])
    for rank, (model_id, _) in enumerate(aic_ranking):
        model_comparison[model_id]['aic_rank'] = rank + 1
    
    # Calculate selection scores
    for model_id, model_data in model_comparison.items():
        combined_rank = (model_data['r2_rank'] * 0.6 + model_data['aic_rank'] * 0.4)
        model_data['model_rank'] = int(combined_rank)
        
        r2_score = min(10, model_data['adj_r_squared'] * 10)
        significance_score = 10 if model_data['f_pvalue'] < 0.05 else 6 if model_data['f_pvalue'] < 0.10 else 2
        complexity_penalty = 1 if model_data['model_type'] == 'Multifactor' else 0
        
        selection_score = (r2_score * 0.5 + significance_score * 0.4 + (10 - complexity_penalty) * 0.1)
        model_data['selection_score'] = selection_score
    
    return model_comparison

def _create_correlation_heatmap(correlation_analysis: Dict) -> Optional[Dict]:
    """Create correlation heatmap matrix"""
    
    if not correlation_analysis:
        return None
    
    try:
        companies_list = list(correlation_analysis.keys())
        
        # Get all unique indicators
        all_indicators = set()
        for company_data in correlation_analysis.values():
            all_indicators.update(company_data['all_correlations'].keys())
        
        all_indicators = sorted(list(all_indicators))[:20]  # Limit to top 20
        
        # Create correlation matrix
        correlation_matrix = []
        for company in companies_list:
            company_row = []
            for indicator in all_indicators:
                if indicator in correlation_analysis[company]['all_correlations']:
                    corr_val = correlation_analysis[company]['all_correlations'][indicator]['correlation']
                    company_row.append(corr_val)
                else:
                    company_row.append(0)
            correlation_matrix.append(company_row)
        
        # Create heatmap
        fig_data = {
            'data': [{
                'type': 'heatmap',
                'z': correlation_matrix,
                'x': [ind[:25] for ind in all_indicators],
                'y': [comp[:20] for comp in companies_list],
                'colorscale': 'RdBu',
                'zmid': 0,
                'colorbar': {'title': 'Correlation'},
                'hoverongaps': False,
                'hovertemplate': 'Company: %{y}<br>Indicator: %{x}<br>Correlation: %{z:.3f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Revenue Growth vs Macro Indicators - Correlation Heatmap',
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'xaxis': {
                    'title': 'Macro-Economic Indicators',
                    'tickangle': -45,
                    'side': 'bottom'
                },
                'yaxis': {
                    'title': 'Companies',
                    'autorange': 'reversed'
                },
                'height': 600,
                'margin': {'l': 150, 'r': 50, 't': 80, 'b': 150}
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating correlation heatmap: {e}")
        return None


def _create_top_correlations_chart(correlation_analysis: Dict) -> Optional[Dict]:
    """Create top correlations chart with multiple views"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Collect all significant correlations
        all_correlations = []
        for company, data in correlation_analysis.items():
            for indicator, stats in data['significant_correlations'].items():
                all_correlations.append({
                    'company': company,
                    'indicator': indicator,
                    'correlation': stats['correlation'],
                    'p_value': stats['p_value'],
                    'abs_correlation': stats['abs_correlation']
                })
        
        if not all_correlations:
            return None
        
        # Sort by absolute correlation
        all_correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        # Top 15 strongest correlations
        top_15 = all_correlations[:15]
        
        labels = [f"{item['company'][:12]}<br>{item['indicator'][:20]}" for item in top_15]
        values = [item['correlation'] for item in top_15]
        colors = ['#10b981' if v > 0 else '#ef4444' for v in values]
        
        # Create horizontal bar chart
        fig_data = {
            'data': [{
                'type': 'bar',
                'y': labels,
                'x': values,
                'orientation': 'h',
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'hovertemplate': '%{y}<br>Correlation: %{x:.3f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Top 15 Strongest Revenue Growth Correlations',
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'xaxis': {
                    'title': 'Correlation Coefficient',
                    'zeroline': True,
                    'zerolinecolor': '#64748b',
                    'zerolinewidth': 2
                },
                'yaxis': {
                    'title': '',
                    'autorange': 'reversed'
                },
                'height': 600,
                'margin': {'l': 250, 'r': 50, 't': 80, 'b': 50}
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating top correlations chart: {e}")
        return None


def _create_univariate_regression_chart(univariate_models: Dict) -> Optional[Dict]:
    """Create univariate regression analysis chart"""
    
    if not univariate_models:
        return None
    
    try:
        companies_list = []
        r2_values = []
        colors_list = []
        
        for company, model_data in univariate_models.items():
            if model_data['best_model']:
                indicator, stats = model_data['best_model']
                companies_list.append(company[:15])
                r2_values.append(stats['adj_r_squared'])
                
                # Color based on quality
                if stats['adj_r_squared'] > 0.5 and stats['slope_pvalue'] < 0.05:
                    colors_list.append('#10b981')  # Excellent - green
                elif stats['adj_r_squared'] > 0.3 and stats['slope_pvalue'] < 0.10:
                    colors_list.append('#3b82f6')  # Good - blue
                elif stats['adj_r_squared'] > 0.1:
                    colors_list.append('#f59e0b')  # Fair - orange
                else:
                    colors_list.append('#ef4444')  # Weak - red
        
        if not companies_list:
            return None
        
        # Create bar chart
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': companies_list,
                'y': r2_values,
                'marker': {
                    'color': colors_list,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{val:.3f}' for val in r2_values],
                'textposition': 'outside',
                'hovertemplate': '%{x}<br>Adj R²: %{y:.3f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Univariate Model Performance (Adjusted R²)',
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Adjusted R²',
                    'range': [0, max(r2_values) * 1.1] if r2_values else [0, 1]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'showlegend': False
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating univariate regression chart: {e}")
        return None


def _create_multifactor_performance_chart(univariate_models: Dict, 
                                         multifactor_models: Dict) -> Optional[Dict]:
    """Create multifactor vs univariate comparison chart"""
    
    if not univariate_models or not multifactor_models:
        return None
    
    try:
        companies = []
        uni_r2 = []
        mf_r2 = []
        
        for company in univariate_models.keys():
            if (company in multifactor_models and 
                univariate_models[company]['best_model'] and 
                multifactor_models[company]['best_model']):
                
                companies.append(company[:15])
                uni_r2.append(univariate_models[company]['best_model'][1]['adj_r_squared'])
                mf_r2.append(multifactor_models[company]['best_model'][1]['adj_r_squared'])
        
        if not companies:
            return None
        
        # Create grouped bar chart
        fig_data = {
            'data': [
                {
                    'type': 'bar',
                    'name': 'Univariate Models',
                    'x': companies,
                    'y': uni_r2,
                    'marker': {'color': '#3b82f6'},
                    'hovertemplate': '%{x}<br>Univariate R²: %{y:.3f}<extra></extra>'
                },
                {
                    'type': 'bar',
                    'name': 'Multifactor Models',
                    'x': companies,
                    'y': mf_r2,
                    'marker': {'color': '#10b981'},
                    'hovertemplate': '%{x}<br>Multifactor R²: %{y:.3f}<extra></extra>'
                }
            ],
            'layout': {
                'title': {
                    'text': 'Univariate vs Multifactor Model Performance',
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Adjusted R²'
                },
                'barmode': 'group',
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'legend': {
                    'x': 0.02,
                    'y': 0.98,
                    'bgcolor': 'rgba(255,255,255,0.8)',
                    'bordercolor': '#64748b',
                    'borderwidth': 1
                }
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating multifactor performance chart: {e}")
        return None


def _create_model_diagnostics_chart(model_diagnostics: Dict) -> Optional[Dict]:
    """Create model diagnostics dashboard"""
    
    if not model_diagnostics:
        return None
    
    try:
        model_names = [name[:20] for name in model_diagnostics.keys()]
        diagnostic_scores = [diag['diagnostic_score'] for diag in model_diagnostics.values()]
        dw_stats = [diag['durbin_watson'] for diag in model_diagnostics.values()]
        
        # Color based on diagnostic score
        colors = ['#10b981' if score >= 7 else '#f59e0b' if score >= 5 else '#ef4444' 
                 for score in diagnostic_scores]
        
        # Create bar chart for diagnostic scores
        fig_data = {
            'data': [
                {
                    'type': 'bar',
                    'name': 'Diagnostic Score',
                    'x': model_names,
                    'y': diagnostic_scores,
                    'marker': {'color': colors},
                    'text': [f'{score:.1f}' for score in diagnostic_scores],
                    'textposition': 'outside',
                    'hovertemplate': '%{x}<br>Score: %{y:.1f}/10<extra></extra>',
                    'yaxis': 'y'
                },
                {
                    'type': 'scatter',
                    'name': 'Durbin-Watson',
                    'x': model_names,
                    'y': dw_stats,
                    'mode': 'markers',
                    'marker': {
                        'size': 10,
                        'color': '#667eea',
                        'symbol': 'diamond'
                    },
                    'hovertemplate': '%{x}<br>DW: %{y:.3f}<extra></extra>',
                    'yaxis': 'y2'
                }
            ],
            'layout': {
                'title': {
                    'text': 'Model Diagnostic Quality Assessment',
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'xaxis': {
                    'title': 'Models',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Diagnostic Score (0-10)',
                    'side': 'left',
                    'range': [0, 11]
                },
                'yaxis2': {
                    'title': 'Durbin-Watson Statistic',
                    'overlaying': 'y',
                    'side': 'right',
                    'range': [0, 4]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 80, 't': 80, 'b': 150},
                'legend': {
                    'x': 0.02,
                    'y': 0.98,
                    'bgcolor': 'rgba(255,255,255,0.8)',
                    'bordercolor': '#64748b',
                    'borderwidth': 1
                },
                'shapes': [
                    # DW ideal range shading
                    {
                        'type': 'rect',
                        'xref': 'paper',
                        'yref': 'y2',
                        'x0': 0,
                        'x1': 1,
                        'y0': 1.5,
                        'y1': 2.5,
                        'fillcolor': '#10b981',
                        'opacity': 0.1,
                        'layer': 'below',
                        'line': {'width': 0}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating model diagnostics chart: {e}")
        return None


def _create_signal_discovery_summary(correlation_analysis: Dict, 
                                    univariate_models: Dict, 
                                    multifactor_models: Dict) -> Optional[Dict]:
    """Create comprehensive signal discovery summary dashboard"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Calculate portfolio metrics
        total_companies = len(correlation_analysis)
        total_significant = sum(len(analysis['significant_correlations']) 
                              for analysis in correlation_analysis.values())
        avg_significant = total_significant / total_companies if total_companies > 0 else 0
        
        # Model success rates
        uni_success = len(univariate_models) / total_companies if total_companies > 0 else 0
        mf_success = len(multifactor_models) / total_companies if total_companies > 0 else 0
        
        # Average R² values
        uni_r2_values = []
        mf_r2_values = []
        
        for model_data in univariate_models.values():
            if model_data['best_model']:
                uni_r2_values.append(model_data['best_model'][1]['adj_r_squared'])
        
        for model_data in multifactor_models.values():
            if model_data['best_model']:
                mf_r2_values.append(model_data['best_model'][1]['adj_r_squared'])
        
        avg_uni_r2 = np.mean(uni_r2_values) if uni_r2_values else 0
        avg_mf_r2 = np.mean(mf_r2_values) if mf_r2_values else 0
        
        # Most frequent indicators
        indicator_frequency = {}
        for company_data in correlation_analysis.values():
            for indicator in company_data['significant_correlations'].keys():
                indicator_frequency[indicator] = indicator_frequency.get(indicator, 0) + 1
        
        top_indicators = sorted(indicator_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Create multi-panel dashboard
        fig_data = {
            'data': [
                # Panel 1: Portfolio metrics
                {
                    'type': 'bar',
                    'name': 'Portfolio Metrics',
                    'x': ['Avg Correlations<br>per Company', 'Univariate<br>Success Rate', 
                          'Multifactor<br>Success Rate', 'Avg Univariate<br>R²', 'Avg Multifactor<br>R²'],
                    'y': [avg_significant, uni_success * 10, mf_success * 10, avg_uni_r2 * 10, avg_mf_r2 * 10],
                    'marker': {
                        'color': ['#667eea', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
                    },
                    'text': [f'{avg_significant:.1f}', f'{uni_success*100:.0f}%', f'{mf_success*100:.0f}%',
                            f'{avg_uni_r2:.3f}', f'{avg_mf_r2:.3f}'],
                    'textposition': 'outside',
                    'hovertemplate': '%{x}<br>Value: %{text}<extra></extra>',
                    'xaxis': 'x',
                    'yaxis': 'y'
                },
                # Panel 2: Top indicators frequency
                {
                    'type': 'bar',
                    'name': 'Top Indicators',
                    'x': [ind[:20] for ind, _ in top_indicators],
                    'y': [freq for _, freq in top_indicators],
                    'marker': {'color': '#764ba2'},
                    'hovertemplate': '%{x}<br>Companies: %{y}<extra></extra>',
                    'xaxis': 'x2',
                    'yaxis': 'y2'
                }
            ],
            'layout': {
                'title': {
                    'text': 'Portfolio Signal Discovery Intelligence Dashboard',
                    'font': {'size': 18, 'weight': 'bold'}
                },
                'xaxis': {
                    'domain': [0, 0.48],
                    'anchor': 'y',
                    'title': 'Portfolio Metrics (Normalized)',
                    'tickangle': -45
                },
                'yaxis': {
                    'domain': [0.55, 1],
                    'anchor': 'x',
                    'title': 'Normalized Score'
                },
                'xaxis2': {
                    'domain': [0.52, 1],
                    'anchor': 'y2',
                    'title': 'Macro Indicators',
                    'tickangle': -45
                },
                'yaxis2': {
                    'domain': [0.55, 1],
                    'anchor': 'x2',
                    'title': 'Number of Companies'
                },
                'height': 700,
                'margin': {'l': 80, 'r': 50, 't': 100, 'b': 150},
                'showlegend': False,
                'annotations': [
                    {
                        'text': 'Portfolio Performance Metrics',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.24,
                        'y': 1.05,
                        'showarrow': False,
                        'font': {'size': 14, 'weight': 'bold'}
                    },
                    {
                        'text': 'Most Predictive Indicators',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.76,
                        'y': 1.05,
                        'showarrow': False,
                        'font': {'size': 14, 'weight': 'bold'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating signal discovery summary: {e}")
        return None

def _build_relationship_strength_section(insights: Dict) -> str:
    """Build relationship strength assessment section"""
    
    html = """
    <div style="margin: 40px 0;">
        <h3 style="color: var(--primary-gradient-start); font-size: 1.5rem; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 2px solid var(--primary-gradient-start);">
            📊 9E.1 Macro-Financial Relationship Strength Assessment
        </h3>
    """
    
    # Key metrics cards
    metrics = insights['relationship_metrics']
    
    summary_cards = [
        {
            "label": "Signal Discovery Coverage",
            "value": f"{metrics['total_significant']} correlations",
            "description": f"{metrics['avg_per_company']:.1f} per company",
            "type": "success" if metrics['avg_per_company'] >= 3 else "info"
        },
        {
            "label": "Average Correlation Strength",
            "value": f"{metrics['avg_strongest']:.3f}",
            "description": metrics['strength_label'],
            "type": "success" if metrics['avg_strongest'] >= 0.4 else "info"
        },
        {
            "label": "Cross-Company Consistency",
            "value": f"{metrics['consistent_indicators']} indicators",
            "description": "Recurring significance",
            "type": "success" if metrics['consistent_indicators'] >= 3 else "info"
        },
        {
            "label": "Statistical Confidence",
            "value": metrics['confidence_level'],
            "description": "Signal discovery rate",
            "type": "success" if metrics['confidence_level'] == "High" else "warning"
        }
    ]
    
    html += build_stat_grid(summary_cards)
    
    # Most predictive indicators
    if metrics['top_indicators']:
        html += """
        <div style="margin-top: 30px;">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">🎯 Most Predictive Economic Indicators</h4>
        """
        
        for i, (indicator, freq) in enumerate(metrics['top_indicators'][:5], 1):
            progress_pct = (freq / metrics['total_companies']) * 100
            color = '#10b981' if progress_pct >= 60 else '#3b82f6' if progress_pct >= 40 else '#f59e0b'
            
            html += f"""
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 600; color: var(--text-primary);">{i}. {indicator[:40]}</span>
                    <span style="font-weight: 700; color: {color};">{freq}/{metrics['total_companies']} companies</span>
                </div>
                <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 8px; height: 18px; overflow: hidden;">
                    <div style="width: {progress_pct}%; background: {color}; height: 100%; transition: width 0.8s ease;"></div>
                </div>
            </div>
            """
        
        html += "</div>"
    
    # Strongest correlations highlight
    if metrics['strongest_correlations']:
        html += """
        <div style="margin-top: 25px;">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">⭐ Strongest Portfolio Correlations</h4>
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid var(--primary-gradient-start);">
                <ul style="list-style: none; padding: 0; margin: 0;">
        """
        
        for company, indicator, corr, pval in metrics['strongest_correlations'][:3]:
            corr_color = '#10b981' if corr > 0 else '#ef4444'
            html += f"""
                <li style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                    <strong style="color: var(--primary-gradient-start);">{indicator[:35]}</strong> 
                    vs <strong>{company}</strong>: 
                    <span style="font-size: 1.2rem; font-weight: 700; color: {corr_color};">{corr:.3f}</span>
                    <span style="font-size: 0.9rem; color: var(--text-secondary);">(p={pval:.3f})</span>
                </li>
            """
        
        html += """
                </ul>
            </div>
        </div>
        """
    
    # Portfolio assessment
    html += f"""
    <div style="margin-top: 25px;">
        {build_info_box(insights['relationship_summary'], "success" if metrics['avg_per_company'] >= 3 else "info", 
                       "Portfolio Macro-Sensitivity Assessment")}
    </div>
    """
    
    html += "</div>"
    return html


def _build_signal_quality_section(insights: Dict) -> str:
    """Build signal quality and validation section"""
    
    html = """
    <div style="margin: 40px 0;">
        <h3 style="color: var(--primary-gradient-start); font-size: 1.5rem; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 2px solid var(--primary-gradient-start);">
            🔬 9E.2 Predictive Signal Quality & Statistical Validation
        </h3>
    """
    
    metrics = insights['signal_quality_metrics']
    
    # Model performance cards
    performance_cards = [
        {
            "label": "Univariate Models",
            "value": f"{metrics['uni_success_rate']*100:.0f}%",
            "description": f"Avg R²: {metrics['avg_uni_r2']:.3f}",
            "type": "success" if metrics['avg_uni_r2'] > 0.3 else "info"
        },
        {
            "label": "Multifactor Models",
            "value": f"{metrics['mf_success_rate']*100:.0f}%",
            "description": f"Avg R²: {metrics['avg_mf_r2']:.3f}",
            "type": "success" if metrics['avg_mf_r2'] > 0.4 else "info"
        },
        {
            "label": "Model Improvement",
            "value": f"+{metrics['improvement']:.3f}" if metrics['improvement'] > 0 else f"{metrics['improvement']:.3f}",
            "description": "R² enhancement",
            "type": "success" if metrics['improvement'] > 0.1 else "info"
        },
        {
            "label": "Diagnostic Quality",
            "value": f"{metrics['avg_diagnostic']:.1f}/10",
            "description": metrics['diagnostic_label'],
            "type": "success" if metrics['avg_diagnostic'] >= 7 else "info"
        }
    ]
    
    html += build_stat_grid(performance_cards)
    
    # Model quality distribution
    html += """
    <div style="margin-top: 30px;">
        <h4 style="color: var(--text-primary); margin-bottom: 15px;">📈 Model Quality Distribution</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
    """
    
    quality_items = [
        ("Excellent Models", metrics['excellent_count'], metrics['total_models'], "#10b981"),
        ("Good Models", metrics['good_count'], metrics['total_models'], "#3b82f6"),
        ("Developing Models", metrics['developing_count'], metrics['total_models'], "#f59e0b")
    ]
    
    for label, count, total, color in quality_items:
        pct = (count / total * 100) if total > 0 else 0
        html += f"""
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; 
                    border-left: 4px solid {color}; box-shadow: var(--shadow-sm);">
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">{label}</div>
            <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 5px;">{count}/{total}</div>
            <div style="font-size: 0.85rem; color: var(--text-tertiary);">{pct:.1f}% of portfolio</div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    # Statistical validation summary
    html += f"""
    <div style="margin-top: 25px;">
        {build_info_box(insights['signal_quality_summary'], "info", "Econometric Validation Framework")}
    </div>
    """
    
    html += "</div>"
    return html


def _build_cycle_sensitivity_section(insights: Dict) -> str:
    """Build economic cycle sensitivity section"""
    
    html = """
    <div style="margin: 40px 0;">
        <h3 style="color: var(--primary-gradient-start); font-size: 1.5rem; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 2px solid var(--primary-gradient-start);">
            🌊 9E.3 Economic Cycle Sensitivity Analysis
        </h3>
    """
    
    metrics = insights['cycle_metrics']
    
    # Sensitivity overview cards
    sensitivity_cards = [
        {
            "label": "Revenue Growth Sensitivity",
            "value": metrics['sensitivity_level'],
            "description": f"Avg correlation: {metrics['avg_correlation']:.3f}",
            "type": "success" if metrics['sensitivity_level'] == "High" else "info"
        },
        {
            "label": "Leading Indicators",
            "value": str(metrics['leading_count']),
            "description": "Consistently predictive",
            "type": "success" if metrics['leading_count'] >= 3 else "info"
        },
        {
            "label": "Economic Intelligence",
            "value": metrics['coverage_level'],
            "description": "Indicator mapping",
            "type": "success" if metrics['coverage_level'] == "Comprehensive" else "info"
        },
        {
            "label": "Cycle Awareness",
            "value": metrics['cycle_awareness'],
            "description": "Portfolio-wide",
            "type": "success" if metrics['cycle_awareness'] == "Strong" else "info"
        }
    ]
    
    html += build_stat_grid(sensitivity_cards)
    
    # Cycle responsiveness indicators
    html += """
    <div style="margin-top: 30px;">
        <h4 style="color: var(--text-primary); margin-bottom: 20px;">🎯 Cycle-Responsive Performance Indicators</h4>
    """
    
    responsiveness_items = [
        ("Growth Sensitivity", metrics['growth_sensitivity'], 
         "Correlation with GDP, Industrial Production, Employment", 
         "#10b981" if "Strong" in metrics['growth_sensitivity'] else "#3b82f6"),
        ("Inflation Responsiveness", metrics['inflation_sensitivity'], 
         "Correlation with CPI, PCE, Producer Prices", 
         "#10b981" if "Clear" in metrics['inflation_sensitivity'] else "#f59e0b"),
        ("Interest Rate Dynamics", metrics['rate_sensitivity'], 
         "Correlation with Fed Funds, Treasury Yields", 
         "#10b981" if "confirmed" in metrics['rate_sensitivity'] else "#f59e0b")
    ]
    
    for title, status, description, color in responsiveness_items:
        html += f"""
        <div style="background: var(--card-bg); padding: 20px; margin: 15px 0; border-radius: 12px; 
                    border-left: 5px solid {color}; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h5 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">{title}</h5>
                <span style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">{status}</span>
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.95rem;">{description}</p>
        </div>
        """
    
    html += """
    </div>
    """
    
    # Strategic cycle intelligence
    html += f"""
    <div style="margin-top: 25px;">
        {build_info_box(insights['cycle_summary'], "success" if metrics['cycle_awareness'] == "Strong" else "info", 
                       "Strategic Cycle Intelligence Assessment")}
    </div>
    """
    
    html += "</div>"
    return html


def _build_intelligence_framework_section(insights: Dict) -> str:
    """Build strategic intelligence framework section"""
    
    html = """
    <div style="margin: 40px 0;">
        <h3 style="color: var(--primary-gradient-start); font-size: 1.5rem; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 2px solid var(--primary-gradient-start);">
            🧠 9E.4 Strategic Macro-Financial Intelligence Framework
        </h3>
    """
    
    metrics = insights['intelligence_metrics']
    
    # Framework capability cards
    capability_cards = [
        {
            "label": "Signal Integration",
            "value": metrics['integration_level'],
            "description": "Macro-financial capability",
            "type": "success" if metrics['integration_level'] == "Advanced" else "info"
        },
        {
            "label": "Predictive Architecture",
            "value": metrics['architecture_quality'],
            "description": "Forecasting framework",
            "type": "success" if "Robust" in metrics['architecture_quality'] else "info"
        },
        {
            "label": "Cross-Company Intelligence",
            "value": metrics['cross_company_pattern'],
            "description": "Portfolio consistency",
            "type": "success" if "Strong" in metrics['cross_company_pattern'] else "info"
        },
        {
            "label": "Framework Maturity",
            "value": metrics['overall_assessment'],
            "description": "Intelligence platform",
            "type": "success" if "Sophisticated" in metrics['overall_assessment'] else "info"
        }
    ]
    
    html += build_stat_grid(capability_cards)
    
    # Framework components
    html += """
    <div style="margin-top: 30px;">
        <h4 style="color: var(--text-primary); margin-bottom: 20px;">🏗️ Intelligence Framework Components</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
    """
    
    components = [
        {
            "icon": "🔍",
            "title": "Correlation Discovery Engine",
            "value": f"{metrics['total_correlations']} relationships",
            "description": "Validated macro-financial signals",
            "color": "#667eea"
        },
        {
            "icon": "🎯",
            "title": "Predictive Modeling Suite",
            "value": f"{metrics['model_count']} models",
            "description": "Uni + Multifactor forecasting",
            "color": "#764ba2"
        },
        {
            "icon": "✅",
            "title": "Statistical Validation",
            "value": metrics['validation_status'],
            "description": "Diagnostic framework",
            "color": "#10b981"
        },
        {
            "icon": "📊",
            "title": "Indicator Prioritization",
            "value": f"{metrics['priority_indicators']} indicators",
            "description": "High-frequency predictors",
            "color": "#3b82f6"
        }
    ]
    
    for comp in components:
        html += f"""
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                    padding: 25px; border-radius: 12px; border: 1px solid var(--card-border); 
                    box-shadow: var(--shadow-sm); text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">{comp['icon']}</div>
            <h5 style="margin: 10px 0; color: var(--text-primary); font-size: 1rem;">{comp['title']}</h5>
            <div style="font-size: 1.8rem; font-weight: 700; color: {comp['color']}; margin: 10px 0;">
                {comp['value']}
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">{comp['description']}</p>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    # Framework assessment
    html += f"""
    <div style="margin-top: 25px;">
        {build_info_box(insights['intelligence_summary'], "success" if "Sophisticated" in metrics['overall_assessment'] else "info", 
                       "Integrated Intelligence Assessment")}
    </div>
    """
    
    html += "</div>"
    return html


def _build_strategy_recommendations_section(insights: Dict) -> str:
    """Build strategy recommendations section with action priorities"""
    
    html = """
    <div style="margin: 40px 0;">
        <h3 style="color: var(--primary-gradient-start); font-size: 1.5rem; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 2px solid var(--primary-gradient-start);">
            🚀 9E.5 Signal-Based Investment & Risk Management Strategy
        </h3>
    """
    
    # Strategic roadmap with tabbed interface
    html += """
    <div style="margin-top: 25px;">
        <div class="strategy-tabs" style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
            <button class="tab-button active" onclick="switchTab('immediate')" style="flex: 1; min-width: 150px; padding: 15px 20px; background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">
                ⚡ Immediate (0-6M)
            </button>
            <button class="tab-button" onclick="switchTab('medium')" style="flex: 1; min-width: 150px; padding: 15px 20px; background: var(--card-bg); color: var(--text-primary); border: 2px solid var(--card-border); border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">
                📈 Medium-Term (6-18M)
            </button>
            <button class="tab-button" onclick="switchTab('long')" style="flex: 1; min-width: 150px; padding: 15px 20px; background: var(--card-bg); color: var(--text-primary); border: 2px solid var(--card-border); border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">
                🎯 Long-Term (18M+)
            </button>
        </div>
    """
    
    # Immediate actions tab
    html += """
    <div id="tab-immediate" class="tab-content" style="display: block;">
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05)); 
                    padding: 30px; border-radius: 12px; border-left: 5px solid #10b981;">
            <h4 style="color: #059669; margin-bottom: 20px; font-size: 1.3rem;">⚡ Immediate Signal Implementation (0-6 months)</h4>
    """
    
    immediate_actions = insights['strategy_immediate']
    for i, action in enumerate(immediate_actions, 1):
        html += f"""
        <div style="background: rgba(255,255,255,0.7); padding: 20px; margin: 15px 0; border-radius: 10px; 
                    border-left: 4px solid #10b981;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="background: #10b981; color: white; width: 30px; height: 30px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 15px;">
                    {i}
                </div>
                <h5 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">{action['title']}</h5>
            </div>
            <p style="margin: 10px 0 10px 45px; color: var(--text-secondary); line-height: 1.6;">{action['description']}</p>
            <div style="margin-left: 45px; display: flex; gap: 10px; flex-wrap: wrap;">
                <span style="background: #dcfce7; color: #059669; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">Priority: {action['priority']}</span>
                <span style="background: #dbeafe; color: #2563eb; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">Impact: {action['impact']}</span>
            </div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    # Medium-term tab
    html += """
    <div id="tab-medium" class="tab-content" style="display: none;">
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05)); 
                    padding: 30px; border-radius: 12px; border-left: 5px solid #3b82f6;">
            <h4 style="color: #2563eb; margin-bottom: 20px; font-size: 1.3rem;">📈 Medium-Term Intelligence Development (6-18 months)</h4>
    """
    
    medium_actions = insights['strategy_medium']
    for i, action in enumerate(medium_actions, 1):
        html += f"""
        <div style="background: rgba(255,255,255,0.7); padding: 20px; margin: 15px 0; border-radius: 10px; 
                    border-left: 4px solid #3b82f6;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="background: #3b82f6; color: white; width: 30px; height: 30px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 15px;">
                    {i}
                </div>
                <h5 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">{action['title']}</h5>
            </div>
            <p style="margin: 10px 0 10px 45px; color: var(--text-secondary); line-height: 1.6;">{action['description']}</p>
            <div style="margin-left: 45px; display: flex; gap: 10px; flex-wrap: wrap;">
                <span style="background: #dbeafe; color: #2563eb; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">Priority: {action['priority']}</span>
                <span style="background: #dcfce7; color: #059669; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">Impact: {action['impact']}</span>
            </div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    # Long-term tab
    html += """
    <div id="tab-long" class="tab-content" style="display: none;">
        <div style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(126, 34, 206, 0.05)); 
                    padding: 30px; border-radius: 12px; border-left: 5px solid #a855f7;">
            <h4 style="color: #7e22ce; margin-bottom: 20px; font-size: 1.3rem;">🎯 Long-Term Strategic Intelligence (18+ months)</h4>
    """
    
    long_actions = insights['strategy_long']
    for i, action in enumerate(long_actions, 1):
        html += f"""
        <div style="background: rgba(255,255,255,0.7); padding: 20px; margin: 15px 0; border-radius: 10px; 
                    border-left: 4px solid #a855f7;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="background: #a855f7; color: white; width: 30px; height: 30px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 15px;">
                    {i}
                </div>
                <h5 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">{action['title']}</h5>
            </div>
            <p style="margin: 10px 0 10px 45px; color: var(--text-secondary); line-height: 1.6;">{action['description']}</p>
            <div style="margin-left: 45px; display: flex; gap: 10px; flex-wrap: wrap;">
                <span style="background: #f3e8ff; color: #7e22ce; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">Priority: {action['priority']}</span>
                <span style="background: #dcfce7; color: #059669; padding: 4px 12px; border-radius: 12px; 
                            font-size: 0.85rem; font-weight: 600;">Impact: {action['impact']}</span>
            </div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    html += "</div>"  # Close strategy tabs container
    
    # Success metrics and targets
    html += """
    <div style="margin-top: 40px;">
        <h4 style="color: var(--text-primary); margin-bottom: 20px; font-size: 1.2rem;">🎯 Success Metrics & Performance Targets</h4>
        <div style="background: var(--card-bg); padding: 30px; border-radius: 12px; box-shadow: var(--shadow-sm);">
    """
    
    targets = insights['success_targets']
    for target in targets:
        html += build_progress_indicator(target['current'], target['target'], target['label'], show_percentage=True)
    
    html += """
        </div>
    </div>
    """
    
    # Tab switching JavaScript
    html += """
    <script>
    function switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        
        // Remove active class from all buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.style.background = 'var(--card-bg)';
            btn.style.color = 'var(--text-primary)';
            btn.style.border = '2px solid var(--card-border)';
            btn.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById('tab-' + tabName).style.display = 'block';
        
        // Highlight active button
        event.target.style.background = 'linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end))';
        event.target.style.color = 'white';
        event.target.style.border = 'none';
        event.target.classList.add('active');
    }
    </script>
    """
    
    html += "</div>"
    return html


# =============================================================================
# HELPER FUNCTION: GENERATE COMPREHENSIVE INSIGHTS
# =============================================================================

def _generate_comprehensive_insights(correlation_analysis: Dict, univariate_models: Dict,
                                    multifactor_models: Dict, model_diagnostics: Dict,
                                    companies: Dict) -> Dict:
    """Generate comprehensive strategic insights from all analyses"""
    
    total_companies = len(companies)
    
    # Calculate relationship metrics
    total_significant = sum(len(analysis['significant_correlations']) 
                           for analysis in correlation_analysis.values())
    avg_per_company = total_significant / total_companies if total_companies > 0 else 0
    
    strongest_correlations = []
    for company_data in correlation_analysis.values():
        if company_data['all_correlations']:
            strongest = max(company_data['all_correlations'].values(), key=lambda x: x['abs_correlation'])
            strongest_correlations.append(strongest['abs_correlation'])
    
    avg_strongest = np.mean(strongest_correlations) if strongest_correlations else 0
    
    # Most common indicators
    indicator_frequency = {}
    for company_data in correlation_analysis.values():
        for indicator in company_data['significant_correlations'].keys():
            indicator_frequency[indicator] = indicator_frequency.get(indicator, 0) + 1
    
    top_indicators = sorted(indicator_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Strongest correlations
    all_strong = []
    for company, analysis in correlation_analysis.items():
        for indicator, stats in analysis['significant_correlations'].items():
            all_strong.append((company, indicator, stats['correlation'], stats['p_value']))
    all_strong.sort(key=lambda x: abs(x[2]), reverse=True)
    
    # Signal quality metrics
    uni_success_rate = len(univariate_models) / total_companies if total_companies > 0 else 0
    mf_success_rate = len(multifactor_models) / total_companies if total_companies > 0 else 0
    
    uni_r2_values = [model_data['best_model'][1]['adj_r_squared'] 
                     for model_data in univariate_models.values() if model_data['best_model']]
    mf_r2_values = [model_data['best_model'][1]['adj_r_squared'] 
                    for model_data in multifactor_models.values() if model_data['best_model']]
    
    avg_uni_r2 = np.mean(uni_r2_values) if uni_r2_values else 0
    avg_mf_r2 = np.mean(mf_r2_values) if mf_r2_values else 0
    improvement = avg_mf_r2 - avg_uni_r2
    
    # Model quality counts
    excellent_count = sum(1 for model_data in univariate_models.values() 
                         if model_data['best_model'] and 
                         model_data['best_model'][1]['adj_r_squared'] > 0.5 and 
                         model_data['best_model'][1]['slope_pvalue'] < 0.05)
    
    good_count = sum(1 for model_data in univariate_models.values() 
                    if model_data['best_model'] and 
                    model_data['best_model'][1]['adj_r_squared'] > 0.3 and 
                    model_data['best_model'][1]['slope_pvalue'] < 0.10) - excellent_count
    
    developing_count = len(univariate_models) - excellent_count - good_count
    
    # Diagnostics
    avg_diagnostic = np.mean([diag['diagnostic_score'] for diag in model_diagnostics.values()]) if model_diagnostics else 0
    
    # Cycle sensitivity detection
    growth_indicators = ['Real_GDP', 'GDP', 'Industrial_Production', 'Nonfarm_Payrolls']
    inflation_indicators = ['CPI_All_Items', 'Core_CPI', 'PCE_Price_Index']
    rate_indicators = ['Fed_Funds_Rate', 'Treasury_10Y', 'Treasury_2Y']
    
    has_growth = any(any(ind in sig_ind for sig_ind in analysis['significant_correlations'].keys()) 
                    for ind in growth_indicators for analysis in correlation_analysis.values())
    has_inflation = any(any(ind in sig_ind for sig_ind in analysis['significant_correlations'].keys()) 
                       for ind in inflation_indicators for analysis in correlation_analysis.values())
    has_rates = any(any(ind in sig_ind for sig_ind in analysis['significant_correlations'].keys()) 
                   for ind in rate_indicators for analysis in correlation_analysis.values())
    
    # Strategy actions
    immediate_actions = [
        {
            "title": "Deploy Economic Monitoring Protocol",
            "description": f"Implement systematic tracking of {', '.join([ind for ind, _ in top_indicators[:3]])} across portfolio companies for real-time signal intelligence.",
            "priority": "Critical",
            "impact": "High"
        },
        {
            "title": "Integrate Predictive Models",
            "description": f"{'Deploy multifactor forecasting models' if avg_mf_r2 > 0.3 else 'Implement univariate prediction framework'} for revenue growth anticipation with {avg_uni_r2:.1%} baseline accuracy.",
            "priority": "High",
            "impact": "High"
        },
        {
            "title": "Enhance Risk Management",
            "description": f"{'Advanced economic sensitivity-based position sizing' if avg_strongest > 0.4 else 'Moderate macro-factor risk adjustment'} protocols in portfolio management.",
            "priority": "High",
            "impact": "Medium"
        }
    ]
    
    medium_actions = [
        {
            "title": "Signal Quality Enhancement",
            "description": f"{'Refine multifactor models and expand predictor sets' if mf_success_rate > 0.5 else 'Improve univariate model coverage and accuracy'} to achieve 15-20% improvement in R².",
            "priority": "Medium",
            "impact": "High"
        },
        {
            "title": "Economic Cycle Strategy",
            "description": f"{'Implement cycle-responsive portfolio allocation' if len(top_indicators) >= 3 else 'Develop moderate cycle adjustment protocols'} based on signal intelligence framework.",
            "priority": "Medium",
            "impact": "Medium"
        },
        {
            "title": "Cross-Company Intelligence",
            "description": "Scale best-practice signal identification methodologies across entire portfolio for consistency.",
            "priority": "Medium",
            "impact": "Medium"
        }
    ]
    
    long_actions = [
        {
            "title": "Advanced Forecasting Platform",
            "description": f"{'Develop sophisticated multi-horizon economic forecasting' if avg_mf_r2 > 0.4 else 'Build robust single-factor prediction infrastructure'} for strategic planning.",
            "priority": "Strategic",
            "impact": "Very High"
        },
        {
            "title": "Economic Alpha Generation",
            "description": f"{'Implement systematic signal-based alpha strategies' if avg_per_company >= 4 else 'Develop moderate signal-driven performance enhancement'} targeting 200-300 bps outperformance.",
            "priority": "Strategic",
            "impact": "Very High"
        },
        {
            "title": "Portfolio Intelligence Leadership",
            "description": f"{'Achieve industry-leading macro-financial intelligence' if total_significant >= total_companies * 4 else 'Establish above-market economic intelligence standards'} for competitive advantage.",
            "priority": "Strategic",
            "impact": "Very High"
        }
    ]
    
    # Success targets
    success_targets = [
        {
            "label": "Signal Coverage (Total Significant Correlations)",
            "current": total_significant,
            "target": min(total_companies * 5, total_significant + total_companies * 2)
        },
        {
            "label": "Model Performance (Average Multifactor R²)",
            "current": avg_mf_r2 * 100,
            "target": min(60, (avg_mf_r2 + 0.2) * 100)
        },
        {
            "label": "Diagnostic Quality (Average Score)",
            "current": avg_diagnostic * 10,
            "target": min(100, (avg_diagnostic + 2) * 10)
        }
    ]
    
    return {
        'relationship_metrics': {
            'total_significant': total_significant,
            'avg_per_company': avg_per_company,
            'avg_strongest': avg_strongest,
            'strength_label': 'Strong' if avg_strongest > 0.4 else 'Moderate' if avg_strongest > 0.25 else 'Developing',
            'consistent_indicators': len(top_indicators),
            'confidence_level': 'High' if avg_per_company >= 3 else 'Moderate' if avg_per_company >= 1.5 else 'Developing',
            'top_indicators': top_indicators,
            'strongest_correlations': all_strong[:3],
            'total_companies': total_companies
        },
        'relationship_summary': f"Portfolio demonstrates {'excellent' if avg_per_company >= 4 else 'good' if avg_per_company >= 2 else 'moderate'} macro-economic signal discovery with {total_significant} validated relationships across {total_companies} companies.",
        
        'signal_quality_metrics': {
            'uni_success_rate': uni_success_rate,
            'mf_success_rate': mf_success_rate,
            'avg_uni_r2': avg_uni_r2,
            'avg_mf_r2': avg_mf_r2,
            'improvement': improvement,
            'avg_diagnostic': avg_diagnostic,
            'diagnostic_label': 'High confidence' if avg_diagnostic >= 7 else 'Moderate confidence' if avg_diagnostic >= 5 else 'Developing',
            'excellent_count': excellent_count,
            'good_count': good_count,
            'developing_count': developing_count,
            'total_models': len(univariate_models)
        },
        'signal_quality_summary': f"Econometric framework demonstrates {'robust' if avg_mf_r2 > 0.3 or avg_uni_r2 > 0.25 else 'moderate' if avg_uni_r2 > 0.15 else 'developing'} predictive capability with {excellent_count + good_count} high-quality models and {avg_diagnostic:.1f}/10 diagnostic validation.",
        
        'cycle_metrics': {
            'sensitivity_level': 'High' if avg_strongest > 0.4 else 'Moderate' if avg_strongest > 0.25 else 'Developing',
            'avg_correlation': avg_strongest,
            'leading_count': len(top_indicators),
            'coverage_level': 'Comprehensive' if len(set([ind for ind, _ in top_indicators])) >= 10 else 'Broad' if len(set([ind for ind, _ in top_indicators])) >= 5 else 'Focused',
            'cycle_awareness': 'Strong' if avg_per_company >= 3 and len(top_indicators) >= 3 else 'Moderate' if avg_per_company >= 2 else 'Developing',
            'growth_sensitivity': 'Strong correlation with economic growth indicators' if has_growth else 'Moderate growth sensitivity detected',
            'inflation_sensitivity': 'Clear inflation sensitivity patterns' if has_inflation else 'Mixed inflation relationship signals',
            'rate_sensitivity': 'Interest rate sensitivity confirmed' if has_rates else 'Limited interest rate correlation detected'
        },
        'cycle_summary': f"Portfolio demonstrates {'strong' if avg_per_company >= 3 else 'moderate'} economic cycle awareness with validated sensitivity to {'growth, inflation, and interest rate dynamics' if has_growth and has_inflation and has_rates else 'key economic indicators'}.",
        
        'intelligence_metrics': {
            'integration_level': 'Advanced' if avg_per_company >= 4 and avg_mf_r2 > 0.3 else 'Intermediate' if avg_per_company >= 2 and avg_uni_r2 > 0.2 else 'Basic',
            'architecture_quality': 'Robust multifactor framework' if mf_success_rate > 0.6 and avg_mf_r2 > 0.4 else 'Solid univariate foundation' if uni_success_rate > 0.6 and avg_uni_r2 > 0.25 else 'Developing predictive infrastructure',
            'cross_company_pattern': 'Strong portfolio-wide patterns' if len(top_indicators) >= 3 else 'Moderate cross-company consistency' if len(top_indicators) >= 2 else 'Company-specific patterns',
            'overall_assessment': 'Sophisticated macro-financial intelligence platform' if avg_per_company >= 3 and (avg_mf_r2 > 0.3 or avg_uni_r2 > 0.25) else 'Functional economic intelligence capability' if avg_per_company >= 2 and uni_success_rate > 0.5 else 'Foundational intelligence framework',
            'total_correlations': total_significant,
            'model_count': f"{len(univariate_models)} + {len(multifactor_models)}",
            'validation_status': 'Rigorous framework' if model_diagnostics and len(model_diagnostics) >= total_companies * 0.5 else 'Basic protocols' if model_diagnostics else 'Development required',
            'priority_indicators': len(top_indicators)
        },
        'intelligence_summary': f"{'Sophisticated' if avg_per_company >= 3 and (avg_mf_r2 > 0.3 or avg_uni_r2 > 0.25) else 'Functional' if avg_per_company >= 2 else 'Foundational'} macro-financial intelligence platform established with {total_significant} signals, {len(univariate_models) + len(multifactor_models)} models, and {len(top_indicators)} priority indicators for strategic decision support.",
        
        'strategy_immediate': immediate_actions,
        'strategy_medium': medium_actions,
        'strategy_long': long_actions,
        'success_targets': success_targets
    }

"""
Section 9 Complete Chart Library - 24 Standalone Plotly Charts
All charts return Dict format compatible with build_plotly_chart()
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any


# =============================================================================
# CHART GROUP 1: CORRELATION ANALYSIS (4 CHARTS)
# =============================================================================

def create_chart_01_correlation_heatmap(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 1: Correlation Heatmap Matrix - Companies vs Top Macro Indicators"""
    
    if not correlation_analysis:
        return None
    
    try:
        companies_list = list(correlation_analysis.keys())
        
        # Get all unique indicators, sorted by frequency
        indicator_freq = {}
        for company_data in correlation_analysis.values():
            for indicator in company_data['all_correlations'].keys():
                indicator_freq[indicator] = indicator_freq.get(indicator, 0) + 1
        
        # Top 20 most frequent indicators
        top_indicators = sorted(indicator_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        all_indicators = [ind for ind, _ in top_indicators]
        
        # Create correlation matrix
        correlation_matrix = []
        for company in companies_list:
            company_row = []
            for indicator in all_indicators:
                if indicator in correlation_analysis[company]['all_correlations']:
                    corr_val = correlation_analysis[company]['all_correlations'][indicator]['correlation']
                    company_row.append(corr_val)
                else:
                    company_row.append(np.nan)
            correlation_matrix.append(company_row)
        
        fig_data = {
            'data': [{
                'type': 'heatmap',
                'z': correlation_matrix,
                'x': [ind[:30] for ind in all_indicators],
                'y': [comp[:20] for comp in companies_list],
                'colorscale': 'RdBu',
                'zmid': 0,
                'colorbar': {
                    'title': 'Correlation<br>Coefficient',
                    'titleside': 'right'
                },
                'hoverongaps': False,
                'hovertemplate': '<b>%{y}</b><br>%{x}<br>Correlation: <b>%{z:.3f}</b><extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Revenue Growth vs Macro Indicators - Correlation Heatmap',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Macro-Economic Indicators',
                    'tickangle': -45,
                    'side': 'bottom',
                    'tickfont': {'size': 10}
                },
                'yaxis': {
                    'title': 'Companies',
                    'autorange': 'reversed',
                    'tickfont': {'size': 10}
                },
                'height': 600,
                'margin': {'l': 150, 'r': 100, 't': 80, 'b': 180}
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating correlation heatmap: {e}")
        return None


def create_chart_02_top_correlations_bar(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 2: Top 15 Strongest Correlations - Horizontal Bar Chart"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Collect all significant correlations
        all_correlations = []
        for company, data in correlation_analysis.items():
            for indicator, stats in data['significant_correlations'].items():
                all_correlations.append({
                    'company': company,
                    'indicator': indicator,
                    'correlation': stats['correlation'],
                    'p_value': stats['p_value'],
                    'abs_correlation': stats['abs_correlation']
                })
        
        if not all_correlations:
            return None
        
        # Sort by absolute correlation
        all_correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        top_15 = all_correlations[:15]
        
        # Create labels and values
        labels = [f"{item['company'][:12]} - {item['indicator'][:25]}" for item in top_15]
        values = [item['correlation'] for item in top_15]
        colors = ['#10b981' if v > 0 else '#ef4444' for v in values]
        
        # Add significance stars
        stars = ['***' if item['p_value'] < 0.01 else '**' if item['p_value'] < 0.05 else '*' 
                for item in top_15]
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'y': list(range(len(labels)))[::-1],  # Reverse for top-to-bottom
                'x': values,
                'orientation': 'h',
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{v:.3f}{s}' for v, s in zip(values, stars)],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'hovertemplate': '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Correlation: <b>%{x:.3f}</b><br>P-value: %{customdata[2]:.4f}<extra></extra>',
                'customdata': [[item['company'], item['indicator'], item['p_value']] for item in top_15]
            }],
            'layout': {
                'title': {
                    'text': 'Top 15 Strongest Revenue Growth Correlations',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Correlation Coefficient',
                    'zeroline': True,
                    'zerolinecolor': '#64748b',
                    'zerolinewidth': 2
                },
                'yaxis': {
                    'tickmode': 'array',
                    'tickvals': list(range(len(labels)))[::-1],
                    'ticktext': labels,
                    'tickfont': {'size': 9}
                },
                'height': 600,
                'margin': {'l': 280, 'r': 80, 't': 80, 'b': 60},
                'annotations': [
                    {
                        'text': 'Significance: *** p<0.01, ** p<0.05, * p<0.10',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.08,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating top correlations bar: {e}")
        return None


def create_chart_03_correlation_distribution(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 3: Correlation Strength Distribution Histogram"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Collect all correlation strengths
        all_abs_correlations = []
        for company_data in correlation_analysis.values():
            for stats in company_data['all_correlations'].values():
                all_abs_correlations.append(stats['abs_correlation'])
        
        if not all_abs_correlations:
            return None
        
        mean_corr = np.mean(all_abs_correlations)
        median_corr = np.median(all_abs_correlations)
        
        fig_data = {
            'data': [{
                'type': 'histogram',
                'x': all_abs_correlations,
                'nbinsx': 20,
                'marker': {
                    'color': '#667eea',
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'opacity': 0.8,
                'hovertemplate': 'Correlation Range: %{x}<br>Count: <b>%{y}</b><extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Distribution of Correlation Strengths',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Absolute Correlation Coefficient',
                    'range': [0, 1]
                },
                'yaxis': {
                    'title': 'Frequency'
                },
                'height': 500,
                'shapes': [
                    # Mean line
                    {
                        'type': 'line',
                        'x0': mean_corr,
                        'x1': mean_corr,
                        'y0': 0,
                        'y1': 1,
                        'yref': 'paper',
                        'line': {
                            'color': '#ef4444',
                            'width': 2,
                            'dash': 'dash'
                        }
                    },
                    # Median line
                    {
                        'type': 'line',
                        'x0': median_corr,
                        'x1': median_corr,
                        'y0': 0,
                        'y1': 1,
                        'yref': 'paper',
                        'line': {
                            'color': '#10b981',
                            'width': 2,
                            'dash': 'dot'
                        }
                    }
                ],
                'annotations': [
                    {
                        'x': mean_corr,
                        'y': 0.95,
                        'yref': 'paper',
                        'text': f'Mean: {mean_corr:.3f}',
                        'showarrow': True,
                        'arrowhead': 2,
                        'ax': 40,
                        'ay': -30,
                        'font': {'color': '#ef4444', 'weight': 'bold'}
                    },
                    {
                        'x': median_corr,
                        'y': 0.85,
                        'yref': 'paper',
                        'text': f'Median: {median_corr:.3f}',
                        'showarrow': True,
                        'arrowhead': 2,
                        'ax': -40,
                        'ay': -30,
                        'font': {'color': '#10b981', 'weight': 'bold'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating correlation distribution: {e}")
        return None


def create_chart_04_pvalue_vs_correlation_scatter(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 4: P-Value vs Correlation Scatter Plot with Significance Zones"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Collect all correlations with p-values
        correlations = []
        p_values = []
        companies = []
        indicators = []
        
        for company, data in correlation_analysis.items():
            for indicator, stats in data['all_correlations'].items():
                correlations.append(stats['correlation'])
                p_values.append(stats['p_value'])
                companies.append(company)
                indicators.append(indicator)
        
        if not correlations:
            return None
        
        # Color by significance
        colors = []
        for p in p_values:
            if p < 0.01:
                colors.append('#10b981')  # Highly significant - green
            elif p < 0.05:
                colors.append('#3b82f6')  # Significant - blue
            elif p < 0.10:
                colors.append('#f59e0b')  # Marginally significant - orange
            else:
                colors.append('#ef4444')  # Not significant - red
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'x': correlations,
                'y': p_values,
                'mode': 'markers',
                'marker': {
                    'size': 8,
                    'color': colors,
                    'opacity': 0.6,
                    'line': {'color': '#1e293b', 'width': 0.5}
                },
                'text': [f'{comp}: {ind[:30]}' for comp, ind in zip(companies, indicators)],
                'hovertemplate': '<b>%{text}</b><br>Correlation: %{x:.3f}<br>P-value: <b>%{y:.4f}</b><extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Statistical Significance vs Correlation Strength',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Correlation Coefficient',
                    'zeroline': True,
                    'zerolinecolor': '#64748b',
                    'zerolinewidth': 2
                },
                'yaxis': {
                    'title': 'P-Value',
                    'type': 'log',
                    'range': [-3, 0]  # Log scale from 0.001 to 1
                },
                'height': 600,
                'shapes': [
                    # 1% significance line
                    {
                        'type': 'line',
                        'x0': -1,
                        'x1': 1,
                        'y0': 0.01,
                        'y1': 0.01,
                        'line': {
                            'color': '#10b981',
                            'width': 2,
                            'dash': 'dash'
                        }
                    },
                    # 5% significance line
                    {
                        'type': 'line',
                        'x0': -1,
                        'x1': 1,
                        'y0': 0.05,
                        'y1': 0.05,
                        'line': {
                            'color': '#3b82f6',
                            'width': 2,
                            'dash': 'dash'
                        }
                    },
                    # 10% significance line
                    {
                        'type': 'line',
                        'x0': -1,
                        'x1': 1,
                        'y0': 0.10,
                        'y1': 0.10,
                        'line': {
                            'color': '#f59e0b',
                            'width': 2,
                            'dash': 'dot'
                        }
                    }
                ],
                'annotations': [
                    {
                        'x': 0.9,
                        'y': 0.01,
                        'text': '1% significance',
                        'showarrow': False,
                        'font': {'color': '#10b981', 'size': 10}
                    },
                    {
                        'x': 0.9,
                        'y': 0.05,
                        'text': '5% significance',
                        'showarrow': False,
                        'font': {'color': '#3b82f6', 'size': 10}
                    },
                    {
                        'x': 0.9,
                        'y': 0.10,
                        'text': '10% significance',
                        'showarrow': False,
                        'font': {'color': '#f59e0b', 'size': 10}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating p-value scatter: {e}")
        return None


def create_chart_05_company_sensitivity_rankings(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 5: Company Macro-Sensitivity Rankings"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Calculate average absolute correlation per company
        company_sensitivities = {}
        for company, data in correlation_analysis.items():
            if data['all_correlations']:
                avg_abs_corr = np.mean([stats['abs_correlation'] 
                                       for stats in data['all_correlations'].values()])
                sig_count = len(data['significant_correlations'])
                company_sensitivities[company] = {
                    'avg_correlation': avg_abs_corr,
                    'significant_count': sig_count,
                    'score': avg_abs_corr * 100 + sig_count * 5  # Composite score
                }
        
        # Sort by composite score
        sorted_companies = sorted(company_sensitivities.items(), 
                                 key=lambda x: x[1]['score'], reverse=True)
        
        companies = [comp[:15] for comp, _ in sorted_companies]
        scores = [data['score'] for _, data in sorted_companies]
        avg_corrs = [data['avg_correlation'] for _, data in sorted_companies]
        sig_counts = [data['significant_count'] for _, data in sorted_companies]
        
        # Color gradient based on score
        max_score = max(scores) if scores else 1
        colors = [f'rgba(102, 126, 234, {0.4 + 0.6 * (score/max_score)})' for score in scores]
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': companies,
                'y': scores,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{score:.1f}' for score in scores],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'customdata': [[avg, sig] for avg, sig in zip(avg_corrs, sig_counts)],
                'hovertemplate': '<b>%{x}</b><br>Sensitivity Score: <b>%{y:.1f}</b><br>Avg Correlation: %{customdata[0]:.3f}<br>Significant Indicators: %{customdata[1]}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Company Macro-Sensitivity Rankings',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Macro-Sensitivity Score'
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'annotations': [
                    {
                        'text': 'Score = (Avg Correlation × 100) + (Significant Indicators × 5)',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.2,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating company sensitivity rankings: {e}")
        return None


# =============================================================================
# CHART GROUP 2: UNIVARIATE REGRESSION (4 CHARTS)
# =============================================================================

def create_chart_06_univariate_r2_comparison(univariate_models: Dict) -> Optional[Dict]:
    """Chart 6: Univariate Model R² Comparison by Company"""
    
    if not univariate_models:
        return None
    
    try:
        companies = []
        r2_values = []
        p_values = []
        indicators = []
        
        for company, model_data in univariate_models.items():
            if model_data['best_model']:
                indicator, stats = model_data['best_model']
                companies.append(company[:15])
                r2_values.append(stats['adj_r_squared'])
                p_values.append(stats['slope_pvalue'])
                indicators.append(indicator[:20])
        
        if not companies:
            return None
        
        # Color by quality
        colors = []
        for r2, p in zip(r2_values, p_values):
            if r2 > 0.5 and p < 0.05:
                colors.append('#10b981')  # Excellent
            elif r2 > 0.3 and p < 0.10:
                colors.append('#3b82f6')  # Good
            elif r2 > 0.1:
                colors.append('#f59e0b')  # Fair
            else:
                colors.append('#ef4444')  # Weak
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': companies,
                'y': r2_values,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{val:.3f}' for val in r2_values],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'customdata': [[ind, p] for ind, p in zip(indicators, p_values)],
                'hovertemplate': '<b>%{x}</b><br>Best Predictor: %{customdata[0]}<br>Adj R²: <b>%{y:.3f}</b><br>P-value: %{customdata[1]:.4f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Univariate Model Performance (Adjusted R²)',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Adjusted R²',
                    'range': [0, max(r2_values) * 1.15] if r2_values else [0, 1]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'annotations': [
                    {
                        'text': 'Colors: Green=Excellent (R²>0.5, p<0.05) | Blue=Good (R²>0.3, p<0.10) | Orange=Fair | Red=Weak',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.22,
                        'showarrow': False,
                        'font': {'size': 9, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating univariate R² comparison: {e}")
        return None


def create_chart_07_slope_coefficients(univariate_models: Dict) -> Optional[Dict]:
    """Chart 7: Regression Slope Coefficients - Horizontal Bar"""
    
    if not univariate_models:
        return None
    
    try:
        companies = []
        slopes = []
        t_stats = []
        indicators = []
        
        for company, model_data in univariate_models.items():
            if model_data['best_model']:
                indicator, stats = model_data['best_model']
                companies.append(company[:15])
                slopes.append(stats['slope'])
                t_stats.append(stats['slope_tstat'])
                indicators.append(indicator[:25])
        
        if not companies:
            return None
        
        # Sort by absolute slope
        sorted_indices = sorted(range(len(slopes)), key=lambda i: abs(slopes[i]), reverse=True)
        companies = [companies[i] for i in sorted_indices]
        slopes = [slopes[i] for i in sorted_indices]
        t_stats = [t_stats[i] for i in sorted_indices]
        indicators = [indicators[i] for i in sorted_indices]
        
        colors = ['#10b981' if s > 0 else '#ef4444' for s in slopes]
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'y': list(range(len(companies)))[::-1],
                'x': slopes,
                'orientation': 'h',
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{s:.4f}' for s in slopes],
                'textposition': 'outside',
                'textfont': {'size': 9},
                'customdata': [[comp, ind, t] for comp, ind, t in zip(companies, indicators, t_stats)],
                'hovertemplate': '<b>%{customdata[0]}</b><br>Predictor: %{customdata[1]}<br>Slope: <b>%{x:.4f}</b><br>T-stat: %{customdata[2]:.2f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Regression Slope Coefficients (Revenue Growth Sensitivity)',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Slope Coefficient (% Revenue Growth per Unit Macro Change)',
                    'zeroline': True,
                    'zerolinecolor': '#64748b',
                    'zerolinewidth': 2
                },
                'yaxis': {
                    'tickmode': 'array',
                    'tickvals': list(range(len(companies)))[::-1],
                    'ticktext': companies,
                    'tickfont': {'size': 10}
                },
                'height': 600,
                'margin': {'l': 150, 'r': 100, 't': 80, 'b': 80}
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating slope coefficients chart: {e}")
        return None


def create_chart_08_statistical_significance_scatter(univariate_models: Dict) -> Optional[Dict]:
    """Chart 8: Statistical Significance Analysis - T-stat vs -Log10(P-value)"""
    
    if not univariate_models:
        return None
    
    try:
        t_stats = []
        p_values = []
        companies = []
        r2_values = []
        
        for company, model_data in univariate_models.items():
            if model_data['best_model']:
                stats = model_data['best_model'][1]
                t_stats.append(abs(stats['slope_tstat']))
                p_values.append(stats['slope_pvalue'])
                companies.append(company[:15])
                r2_values.append(stats['adj_r_squared'])
        
        if not t_stats:
            return None
        
        # Convert p-values to -log10 scale
        neg_log_p = [-np.log10(p) if p > 0 else 10 for p in p_values]
        
        # Size by R²
        sizes = [10 + r2 * 40 for r2 in r2_values]
        
        # Color by significance
        colors = []
        for p in p_values:
            if p < 0.01:
                colors.append('#10b981')
            elif p < 0.05:
                colors.append('#3b82f6')
            elif p < 0.10:
                colors.append('#f59e0b')
            else:
                colors.append('#ef4444')
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'x': t_stats,
                'y': neg_log_p,
                'mode': 'markers',
                'marker': {
                    'size': sizes,
                    'color': colors,
                    'opacity': 0.7,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': companies,
                'customdata': [[comp, p, r2] for comp, p, r2 in zip(companies, p_values, r2_values)],
                'hovertemplate': '<b>%{customdata[0]}</b><br>|T-stat|: %{x:.2f}<br>P-value: <b>%{customdata[1]:.4f}</b><br>Adj R²: %{customdata[2]:.3f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Statistical Significance Analysis (Volcano Plot)',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Absolute T-Statistic',
                    'range': [0, max(t_stats) * 1.1] if t_stats else [0, 5]
                },
                'yaxis': {
                    'title': '-Log₁₀(P-value)',
                    'range': [0, max(neg_log_p) * 1.1] if neg_log_p else [0, 5]
                },
                'height': 600,
                'shapes': [
                    # 5% significance line
                    {
                        'type': 'line',
                        'x0': 0,
                        'x1': max(t_stats) if t_stats else 5,
                        'y0': -np.log10(0.05),
                        'y1': -np.log10(0.05),
                        'line': {
                            'color': '#3b82f6',
                            'width': 2,
                            'dash': 'dash'
                        }
                    },
                    # 1% significance line
                    {
                        'type': 'line',
                        'x0': 0,
                        'x1': max(t_stats) if t_stats else 5,
                        'y0': -np.log10(0.01),
                        'y1': -np.log10(0.01),
                        'line': {
                            'color': '#10b981',
                            'width': 2,
                            'dash': 'dash'
                        }
                    }
                ],
                'annotations': [
                    {
                        'text': 'Bubble size = R² | Color = Significance level',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.12,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating statistical significance scatter: {e}")
        return None


def create_chart_09_model_quality_pie(univariate_models: Dict) -> Optional[Dict]:
    """Chart 9: Model Quality Distribution - Pie Chart"""
    
    if not univariate_models:
        return None
    
    try:
        quality_counts = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Weak': 0}
        
        for model_data in univariate_models.values():
            if model_data['best_model']:
                stats = model_data['best_model'][1]
                r2 = stats['adj_r_squared']
                p = stats['slope_pvalue']
                
                if r2 > 0.5 and p < 0.05:
                    quality_counts['Excellent'] += 1
                elif r2 > 0.3 and p < 0.10:
                    quality_counts['Good'] += 1
                elif r2 > 0.1:
                    quality_counts['Fair'] += 1
                else:
                    quality_counts['Weak'] += 1
        
        labels = list(quality_counts.keys())
        values = list(quality_counts.values())
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
        
        total = sum(values)
        percentages = [v/total*100 if total > 0 else 0 for v in values]
        
        fig_data = {
            'data': [{
                'type': 'pie',
                'labels': labels,
                'values': values,
                'marker': {
                    'colors': colors,
                    'line': {'color': '#ffffff', 'width': 2}
                },
                'textinfo': 'label+percent',
                'textposition': 'outside',
                'textfont': {'size': 12, 'weight': 'bold'},
                'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
                'hole': 0.4,
                'pull': [0.1 if v == max(values) else 0 for v in values]
            }],
            'layout': {
                'title': {
                    'text': 'Univariate Model Quality Distribution',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'height': 550,
                'annotations': [
                    {
                        'text': f'<b>{total}</b><br>Models',
                        'x': 0.5,
                        'y': 0.5,
                        'font': {'size': 20, 'weight': 'bold'},
                        'showarrow': False
                    },
                    {
                        'text': 'Excellent: R²>0.5 & p<0.05 | Good: R²>0.3 & p<0.10 | Fair: R²>0.1 | Weak: R²≤0.1',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.1,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating model quality pie: {e}")
        return None


# =============================================================================
# CHART GROUP 3: MULTIFACTOR MODELS (4 CHARTS)
# =============================================================================

def create_chart_10_uni_vs_multi_comparison(univariate_models: Dict, 
                                           multifactor_models: Dict) -> Optional[Dict]:
    """Chart 10: Univariate vs Multifactor R² Comparison - Grouped Bar"""
    
    if not univariate_models or not multifactor_models:
        return None
    
    try:
        companies = []
        uni_r2 = []
        mf_r2 = []
        
        for company in univariate_models.keys():
            if (company in multifactor_models and 
                univariate_models[company]['best_model'] and 
                multifactor_models[company]['best_model']):
                
                companies.append(company[:15])
                uni_r2.append(univariate_models[company]['best_model'][1]['adj_r_squared'])
                mf_r2.append(multifactor_models[company]['best_model'][1]['adj_r_squared'])
        
        if not companies:
            return None
        
        fig_data = {
            'data': [
                {
                    'type': 'bar',
                    'name': 'Univariate Models',
                    'x': companies,
                    'y': uni_r2,
                    'marker': {'color': '#3b82f6'},
                    'text': [f'{val:.3f}' for val in uni_r2],
                    'textposition': 'outside',
                    'textfont': {'size': 9},
                    'hovertemplate': '<b>%{x}</b><br>Univariate R²: <b>%{y:.3f}</b><extra></extra>'
                },
                {
                    'type': 'bar',
                    'name': 'Multifactor Models',
                    'x': companies,
                    'y': mf_r2,
                    'marker': {'color': '#10b981'},
                    'text': [f'{val:.3f}' for val in mf_r2],
                    'textposition': 'outside',
                    'textfont': {'size': 9},
                    'hovertemplate': '<b>%{x}</b><br>Multifactor R²: <b>%{y:.3f}</b><extra></extra>'
                }
            ],
            'layout': {
                'title': {
                    'text': 'Univariate vs Multifactor Model Performance',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Adjusted R²',
                    'range': [0, max(max(uni_r2), max(mf_r2)) * 1.15]
                },
                'barmode': 'group',
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'legend': {
                    'x': 0.02,
                    'y': 0.98,
                    'bgcolor': 'rgba(255,255,255,0.8)',
                    'bordercolor': '#64748b',
                    'borderwidth': 1
                }
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating uni vs multi comparison: {e}")
        return None


def create_chart_11_r2_improvement(univariate_models: Dict, 
                                   multifactor_models: Dict) -> Optional[Dict]:
    """Chart 11: Multifactor R² Improvement - Bar Chart"""
    
    if not univariate_models or not multifactor_models:
        return None
    
    try:
        companies = []
        improvements = []
        uni_r2_vals = []
        mf_r2_vals = []
        
        for company in univariate_models.keys():
            if (company in multifactor_models and 
                univariate_models[company]['best_model'] and 
                multifactor_models[company]['best_model']):
                
                uni_r2 = univariate_models[company]['best_model'][1]['adj_r_squared']
                mf_r2 = multifactor_models[company]['best_model'][1]['adj_r_squared']
                improvement = mf_r2 - uni_r2
                
                companies.append(company[:15])
                improvements.append(improvement)
                uni_r2_vals.append(uni_r2)
                mf_r2_vals.append(mf_r2)
        
        if not companies:
            return None
        
        # Sort by improvement
        sorted_indices = sorted(range(len(improvements)), key=lambda i: improvements[i], reverse=True)
        companies = [companies[i] for i in sorted_indices]
        improvements = [improvements[i] for i in sorted_indices]
        uni_r2_vals = [uni_r2_vals[i] for i in sorted_indices]
        mf_r2_vals = [mf_r2_vals[i] for i in sorted_indices]
        
        colors = ['#10b981' if imp > 0.1 else '#3b82f6' if imp > 0 else '#ef4444' 
                 for imp in improvements]
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': companies,
                'y': improvements,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{imp:+.3f}' for imp in improvements],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'customdata': [[uni, mf] for uni, mf in zip(uni_r2_vals, mf_r2_vals)],
                'hovertemplate': '<b>%{x}</b><br>Improvement: <b>%{y:+.3f}</b><br>Uni R²: %{customdata[0]:.3f}<br>Multi R²: %{customdata[1]:.3f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Multifactor Model R² Improvement over Univariate',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'R² Improvement (Multifactor - Univariate)',
                    'zeroline': True,
                    'zerolinecolor': '#64748b',
                    'zerolinewidth': 2
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'annotations': [
                    {
                        'text': 'Green: Significant improvement (>0.1) | Blue: Positive | Red: Negative',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.2,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating R² improvement chart: {e}")
        return None


def create_chart_12_aic_comparison(univariate_models: Dict, 
                                   multifactor_models: Dict) -> Optional[Dict]:
    """Chart 12: AIC Comparison - Lower is Better"""
    
    if not univariate_models or not multifactor_models:
        return None
    
    try:
        companies = []
        aic_improvements = []
        uni_aic = []
        mf_aic = []
        
        for company in univariate_models.keys():
            if (company in multifactor_models and 
                univariate_models[company]['best_model'] and 
                multifactor_models[company]['best_model']):
                
                uni_aic_val = univariate_models[company]['best_model'][1]['aic']
                mf_aic_val = multifactor_models[company]['best_model'][1]['aic']
                aic_improvement = uni_aic_val - mf_aic_val  # Positive = multifactor is better
                
                companies.append(company[:15])
                aic_improvements.append(aic_improvement)
                uni_aic.append(uni_aic_val)
                mf_aic.append(mf_aic_val)
        
        if not companies:
            return None
        
        colors = ['#10b981' if imp > 0 else '#ef4444' for imp in aic_improvements]
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': companies,
                'y': aic_improvements,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{imp:+.1f}' for imp in aic_improvements],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'customdata': [[uni, mf] for uni, mf in zip(uni_aic, mf_aic)],
                'hovertemplate': '<b>%{x}</b><br>AIC Improvement: <b>%{y:+.1f}</b><br>Uni AIC: %{customdata[0]:.1f}<br>Multi AIC: %{customdata[1]:.1f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Information Criteria Model Comparison (AIC)',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'AIC Improvement (Uni - Multi, positive = better)',
                    'zeroline': True,
                    'zerolinecolor': '#64748b',
                    'zerolinewidth': 2
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'annotations': [
                    {
                        'text': 'Positive values = Multifactor model preferred by AIC (lower is better)',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.2,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating AIC comparison: {e}")
        return None


def create_chart_13_complexity_vs_performance(multifactor_models: Dict) -> Optional[Dict]:
    """Chart 13: Model Complexity vs Performance Scatter"""
    
    if not multifactor_models:
        return None
    
    try:
        complexities = []
        performances = []
        companies = []
        model_names = []
        vifs = []
        
        for company, model_data in multifactor_models.items():
            if model_data['best_model']:
                model_name, stats = model_data['best_model']
                complexity = len(stats['predictors'])
                performance = stats['adj_r_squared']
                vif = stats['max_vif']
                
                complexities.append(complexity)
                performances.append(performance)
                companies.append(company[:15])
                model_names.append(model_name)
                vifs.append(vif)
        
        if not complexities:
            return None
        
        # Color by VIF (multicollinearity)
        colors = []
        for vif in vifs:
            if vif < 5:
                colors.append('#10b981')  # Good
            elif vif < 10:
                colors.append('#f59e0b')  # Warning
            else:
                colors.append('#ef4444')  # Bad
        
        # Size by performance
        sizes = [20 + perf * 40 for perf in performances]
        
        fig_data = {
            'data': [{
                'type': 'scatter',
                'x': complexities,
                'y': performances,
                'mode': 'markers+text',
                'marker': {
                    'size': sizes,
                    'color': colors,
                    'opacity': 0.7,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': companies,
                'textposition': 'top center',
                'textfont': {'size': 9},
                'customdata': [[comp, model, vif] for comp, model, vif in zip(companies, model_names, vifs)],
                'hovertemplate': '<b>%{customdata[0]}</b><br>Model: %{customdata[1]}<br>Predictors: %{x}<br>Adj R²: <b>%{y:.3f}</b><br>Max VIF: %{customdata[2]:.2f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Model Complexity vs Performance',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Model Complexity (Number of Predictors)',
                    'range': [1.5, max(complexities) + 0.5] if complexities else [1.5, 4],
                    'dtick': 1
                },
                'yaxis': {
                    'title': 'Adjusted R² (Performance)',
                    'range': [0, 1]
                },
                'height': 600,
                'annotations': [
                    {
                        'text': 'Bubble size = R² | Color: Green=Low VIF(<5), Orange=Medium VIF(5-10), Red=High VIF(>10)',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.12,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating complexity vs performance chart: {e}")
        return None


# Continue in next message with Charts 14-24...
"""
Section 9 Chart Library Part 2 - Charts 14-24
Model Diagnostics, Signal Discovery Summary, and Additional Charts
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any


# =============================================================================
# CHART GROUP 4: MODEL DIAGNOSTICS (4 CHARTS)
# =============================================================================

def create_chart_14_diagnostic_scores(model_diagnostics: Dict) -> Optional[Dict]:
    """Chart 14: Model Diagnostic Quality Scores - Bar Chart"""
    
    if not model_diagnostics:
        return None
    
    try:
        model_names = [name[:25] for name in model_diagnostics.keys()]
        diagnostic_scores = [diag['diagnostic_score'] for diag in model_diagnostics.values()]
        
        # Color by quality
        colors = []
        for score in diagnostic_scores:
            if score >= 8:
                colors.append('#10b981')  # Excellent
            elif score >= 6:
                colors.append('#3b82f6')  # Good
            elif score >= 4:
                colors.append('#f59e0b')  # Fair
            else:
                colors.append('#ef4444')  # Poor
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': model_names,
                'y': diagnostic_scores,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{score:.1f}' for score in diagnostic_scores],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'hovertemplate': '<b>%{x}</b><br>Diagnostic Score: <b>%{y:.1f}/10</b><extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Model Diagnostic Quality Scores',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Models',
                    'tickangle': -45,
                    'tickfont': {'size': 9}
                },
                'yaxis': {
                    'title': 'Diagnostic Score (0-10)',
                    'range': [0, 11]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'shapes': [
                    # Threshold lines
                    {
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(model_names) - 0.5,
                        'y0': 7,
                        'y1': 7,
                        'line': {'color': '#10b981', 'width': 2, 'dash': 'dash'}
                    },
                    {
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(model_names) - 0.5,
                        'y0': 5,
                        'y1': 5,
                        'line': {'color': '#f59e0b', 'width': 2, 'dash': 'dot'}
                    }
                ],
                'annotations': [
                    {
                        'text': 'Excellent: ≥8 | Good: 6-8 | Fair: 4-6 | Poor: <4',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.22,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating diagnostic scores chart: {e}")
        return None


def create_chart_15_durbin_watson_test(model_diagnostics: Dict) -> Optional[Dict]:
    """Chart 15: Durbin-Watson Test Results - Autocorrelation Check"""
    
    if not model_diagnostics:
        return None
    
    try:
        model_names = [name[:25] for name in model_diagnostics.keys()]
        dw_stats = [diag['durbin_watson'] for diag in model_diagnostics.values()]
        
        # Color by quality (ideal range 1.5-2.5)
        colors = []
        for dw in dw_stats:
            if 1.5 <= dw <= 2.5:
                colors.append('#10b981')  # Good
            elif 1.0 <= dw <= 3.0:
                colors.append('#f59e0b')  # Acceptable
            else:
                colors.append('#ef4444')  # Poor
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': model_names,
                'y': dw_stats,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{dw:.3f}' for dw in dw_stats],
                'textposition': 'outside',
                'textfont': {'size': 9, 'weight': 'bold'},
                'hovertemplate': '<b>%{x}</b><br>Durbin-Watson: <b>%{y:.3f}</b><extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Durbin-Watson Test (Autocorrelation Detection)',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Models',
                    'tickangle': -45,
                    'tickfont': {'size': 9}
                },
                'yaxis': {
                    'title': 'Durbin-Watson Statistic',
                    'range': [0, 4]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'shapes': [
                    # Ideal range shading
                    {
                        'type': 'rect',
                        'x0': -0.5,
                        'x1': len(model_names) - 0.5,
                        'y0': 1.5,
                        'y1': 2.5,
                        'fillcolor': '#10b981',
                        'opacity': 0.15,
                        'layer': 'below',
                        'line': {'width': 0}
                    },
                    # Reference line at 2
                    {
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(model_names) - 0.5,
                        'y0': 2,
                        'y1': 2,
                        'line': {'color': '#10b981', 'width': 2, 'dash': 'dash'}
                    }
                ],
                'annotations': [
                    {
                        'text': 'Ideal range: 1.5-2.5 (no autocorrelation) | ~2 is perfect',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.22,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating Durbin-Watson chart: {e}")
        return None


def create_chart_16_normality_test(model_diagnostics: Dict) -> Optional[Dict]:
    """Chart 16: Jarque-Bera Normality Test - Bar Chart of -Log10(P-values)"""
    
    if not model_diagnostics:
        return None
    
    try:
        model_names = [name[:25] for name in model_diagnostics.keys()]
        jb_pvalues = [diag['jarque_bera_pvalue'] for diag in model_diagnostics.values()]
        
        # Convert to -log10 scale
        neg_log_p = [-np.log10(p) if p > 0 else 10 for p in jb_pvalues]
        
        # Color by significance
        colors = []
        for p in jb_pvalues:
            if p > 0.10:
                colors.append('#10b981')  # Normal
            elif p > 0.05:
                colors.append('#3b82f6')  # Questionable
            else:
                colors.append('#ef4444')  # Non-normal
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': model_names,
                'y': neg_log_p,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{p:.3f}' for p in jb_pvalues],
                'textposition': 'outside',
                'textfont': {'size': 9},
                'customdata': jb_pvalues,
                'hovertemplate': '<b>%{x}</b><br>P-value: <b>%{customdata:.4f}</b><br>-Log₁₀(p): %{y:.2f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Jarque-Bera Residual Normality Test',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Models',
                    'tickangle': -45,
                    'tickfont': {'size': 9}
                },
                'yaxis': {
                    'title': '-Log₁₀(P-value) - Higher is Better',
                    'range': [0, max(neg_log_p) * 1.15] if neg_log_p else [0, 5]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'shapes': [
                    # 5% significance line
                    {
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(model_names) - 0.5,
                        'y0': -np.log10(0.05),
                        'y1': -np.log10(0.05),
                        'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}
                    }
                ],
                'annotations': [
                    {
                        'text': 'Above red line = Normal residuals (p>0.05) | Green bars pass normality test',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.22,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating normality test chart: {e}")
        return None


def create_chart_17_heteroscedasticity_test(model_diagnostics: Dict) -> Optional[Dict]:
    """Chart 17: Breusch-Pagan Heteroscedasticity Test"""
    
    if not model_diagnostics:
        return None
    
    try:
        model_names = [name[:25] for name in model_diagnostics.keys()]
        bp_pvalues = [diag['breusch_pagan_pvalue'] for diag in model_diagnostics.values()]
        
        # Convert to -log10 scale
        neg_log_p = [-np.log10(p) if p > 0 else 10 for p in bp_pvalues]
        
        # Color by test result
        colors = []
        for p in bp_pvalues:
            if p > 0.10:
                colors.append('#10b981')  # Homoscedastic
            elif p > 0.05:
                colors.append('#3b82f6')  # Borderline
            else:
                colors.append('#ef4444')  # Heteroscedastic
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': model_names,
                'y': neg_log_p,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{p:.3f}' for p in bp_pvalues],
                'textposition': 'outside',
                'textfont': {'size': 9},
                'customdata': bp_pvalues,
                'hovertemplate': '<b>%{x}</b><br>P-value: <b>%{customdata:.4f}</b><br>-Log₁₀(p): %{y:.2f}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Breusch-Pagan Heteroscedasticity Test',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Models',
                    'tickangle': -45,
                    'tickfont': {'size': 9}
                },
                'yaxis': {
                    'title': '-Log₁₀(P-value) - Higher is Better',
                    'range': [0, max(neg_log_p) * 1.15] if neg_log_p else [0, 5]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'shapes': [
                    # 5% significance line
                    {
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(model_names) - 0.5,
                        'y0': -np.log10(0.05),
                        'y1': -np.log10(0.05),
                        'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}
                    }
                ],
                'annotations': [
                    {
                        'text': 'Above red line = Homoscedastic (constant variance, p>0.05) | Green bars pass test',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.22,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating heteroscedasticity test chart: {e}")
        return None


# =============================================================================
# CHART GROUP 5: SIGNAL DISCOVERY SUMMARY (5 CHARTS)
# =============================================================================

def create_chart_18_portfolio_metrics_summary(correlation_analysis: Dict, 
                                              univariate_models: Dict,
                                              multifactor_models: Dict) -> Optional[Dict]:
    """Chart 18: Portfolio Signal Discovery Performance Metrics"""
    
    if not correlation_analysis:
        return None
    
    try:
        total_companies = len(correlation_analysis)
        total_significant = sum(len(analysis['significant_correlations']) 
                              for analysis in correlation_analysis.values())
        avg_significant = total_significant / total_companies if total_companies > 0 else 0
        
        # Model success rates
        uni_success = len(univariate_models) / total_companies if total_companies > 0 else 0
        mf_success = len(multifactor_models) / total_companies if total_companies > 0 else 0
        
        # Average R² values
        uni_r2_values = [model_data['best_model'][1]['adj_r_squared'] 
                        for model_data in univariate_models.values() if model_data.get('best_model')]
        mf_r2_values = [model_data['best_model'][1]['adj_r_squared'] 
                       for model_data in multifactor_models.values() if model_data.get('best_model')]
        
        avg_uni_r2 = np.mean(uni_r2_values) if uni_r2_values else 0
        avg_mf_r2 = np.mean(mf_r2_values) if mf_r2_values else 0
        
        # Create normalized metrics for visualization
        metrics = [
            'Avg Correlations<br>per Company',
            'Univariate<br>Success Rate',
            'Multifactor<br>Success Rate',
            'Avg Univariate<br>R²',
            'Avg Multifactor<br>R²'
        ]
        
        values = [
            avg_significant,
            uni_success * 10,  # Scale to 0-10
            mf_success * 10,
            avg_uni_r2 * 10,
            avg_mf_r2 * 10
        ]
        
        actual_values = [
            f'{avg_significant:.1f}',
            f'{uni_success*100:.0f}%',
            f'{mf_success*100:.0f}%',
            f'{avg_uni_r2:.3f}',
            f'{avg_mf_r2:.3f}'
        ]
        
        colors = ['#667eea', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': metrics,
                'y': values,
                'marker': {'color': colors},
                'text': actual_values,
                'textposition': 'outside',
                'textfont': {'size': 12, 'weight': 'bold'},
                'hovertemplate': '<b>%{x}</b><br>Value: %{text}<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Portfolio Signal Discovery Performance Summary',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': '',
                    'tickfont': {'size': 11}
                },
                'yaxis': {
                    'title': 'Normalized Score (0-10)',
                    'range': [0, max(values) * 1.2] if values else [0, 10]
                },
                'height': 550,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 80}
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating portfolio metrics summary: {e}")
        return None


def create_chart_19_signal_quality_pie(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 19: Signal Quality Distribution - Pie Chart"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Classify companies by signal quality
        quality_distribution = {'Strong': 0, 'Moderate': 0, 'Weak': 0}
        
        for company_data in correlation_analysis.values():
            significant_count = len(company_data['significant_correlations'])
            if significant_count >= 4:
                quality_distribution['Strong'] += 1
            elif significant_count >= 2:
                quality_distribution['Moderate'] += 1
            else:
                quality_distribution['Weak'] += 1
        
        labels = list(quality_distribution.keys())
        values = list(quality_distribution.values())
        colors = ['#10b981', '#3b82f6', '#f59e0b']
        
        total = sum(values)
        
        fig_data = {
            'data': [{
                'type': 'pie',
                'labels': labels,
                'values': values,
                'marker': {
                    'colors': colors,
                    'line': {'color': '#ffffff', 'width': 2}
                },
                'textinfo': 'label+percent+value',
                'textposition': 'outside',
                'textfont': {'size': 12},
                'hovertemplate': '<b>%{label}</b><br>Companies: %{value}<br>Percentage: %{percent}<extra></extra>',
                'hole': 0.4,
                'pull': [0.1, 0, 0]
            }],
            'layout': {
                'title': {
                    'text': 'Signal Quality Distribution Across Portfolio',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'height': 550,
                'annotations': [
                    {
                        'text': f'<b>{total}</b><br>Companies',
                        'x': 0.5,
                        'y': 0.5,
                        'font': {'size': 22, 'weight': 'bold'},
                        'showarrow': False
                    },
                    {
                        'text': 'Strong: ≥4 significant correlations | Moderate: 2-3 | Weak: <2',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.1,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating signal quality pie: {e}")
        return None


def create_chart_20_model_performance_evolution(univariate_models: Dict,
                                               multifactor_models: Dict) -> Optional[Dict]:
    """Chart 20: Model Performance Evolution Line Chart"""
    
    if not univariate_models:
        return None
    
    try:
        companies = list(univariate_models.keys())
        
        # Baseline (no model)
        baseline = [0] * len(companies)
        
        # Univariate performance
        uni_performance = []
        for company in companies:
            if univariate_models[company].get('best_model'):
                uni_performance.append(univariate_models[company]['best_model'][1]['adj_r_squared'])
            else:
                uni_performance.append(0)
        
        # Multifactor performance
        mf_performance = []
        for company in companies:
            if company in multifactor_models and multifactor_models[company].get('best_model'):
                mf_performance.append(multifactor_models[company]['best_model'][1]['adj_r_squared'])
            else:
                mf_performance.append(uni_performance[companies.index(company)])
        
        company_labels = [comp[:12] for comp in companies]
        
        fig_data = {
            'data': [
                {
                    'type': 'scatter',
                    'name': 'Baseline (No Model)',
                    'x': company_labels,
                    'y': baseline,
                    'mode': 'lines+markers',
                    'line': {'color': '#94a3b8', 'width': 2, 'dash': 'dash'},
                    'marker': {'size': 8, 'symbol': 'circle'},
                    'hovertemplate': '<b>%{x}</b><br>Baseline R²: %{y:.3f}<extra></extra>'
                },
                {
                    'type': 'scatter',
                    'name': 'Univariate Models',
                    'x': company_labels,
                    'y': uni_performance,
                    'mode': 'lines+markers',
                    'line': {'color': '#3b82f6', 'width': 3},
                    'marker': {'size': 10, 'symbol': 'square'},
                    'hovertemplate': '<b>%{x}</b><br>Univariate R²: <b>%{y:.3f}</b><extra></extra>'
                },
                {
                    'type': 'scatter',
                    'name': 'Multifactor Models',
                    'x': company_labels,
                    'y': mf_performance,
                    'mode': 'lines+markers',
                    'line': {'color': '#10b981', 'width': 3},
                    'marker': {'size': 10, 'symbol': 'triangle-up'},
                    'hovertemplate': '<b>%{x}</b><br>Multifactor R²: <b>%{y:.3f}</b><extra></extra>'
                }
            ],
            'layout': {
                'title': {
                    'text': 'Model Performance Evolution Across Portfolio',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Companies',
                    'tickangle': -45,
                    'tickfont': {'size': 10}
                },
                'yaxis': {
                    'title': 'Adjusted R² (Predictive Power)',
                    'range': [0, max(max(uni_performance), max(mf_performance)) * 1.15] 
                            if uni_performance and mf_performance else [0, 1]
                },
                'height': 600,
                'margin': {'l': 80, 'r': 50, 't': 80, 'b': 150},
                'legend': {
                    'x': 0.02,
                    'y': 0.98,
                    'bgcolor': 'rgba(255,255,255,0.9)',
                    'bordercolor': '#64748b',
                    'borderwidth': 1
                },
                'hovermode': 'x unified'
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating model performance evolution: {e}")
        return None


def create_chart_21_top_predictive_indicators(correlation_analysis: Dict) -> Optional[Dict]:
    """Chart 21: Most Predictive Economic Indicators - Horizontal Bar"""
    
    if not correlation_analysis:
        return None
    
    try:
        # Count frequency of significant indicators
        indicator_frequency = {}
        for company_data in correlation_analysis.values():
            for indicator in company_data['significant_correlations'].keys():
                indicator_frequency[indicator] = indicator_frequency.get(indicator, 0) + 1
        
        if not indicator_frequency:
            return None
        
        # Get top 12 most frequent indicators
        top_indicators = sorted(indicator_frequency.items(), key=lambda x: x[1], reverse=True)[:12]
        
        indicators = [ind[:35] for ind, _ in top_indicators]
        frequencies = [freq for _, freq in top_indicators]
        
        total_companies = len(correlation_analysis)
        percentages = [(freq / total_companies * 100) for freq in frequencies]
        
        # Color gradient
        max_freq = max(frequencies)
        colors = [f'rgba(102, 126, 234, {0.4 + 0.6 * (freq/max_freq)})' for freq in frequencies]
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'y': list(range(len(indicators)))[::-1],
                'x': frequencies,
                'orientation': 'h',
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{freq} ({pct:.0f}%)' for freq, pct in zip(frequencies, percentages)],
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'hovertemplate': '<b>%{customdata}</b><br>Companies: <b>%{x}</b> (%{y:.0f}%)<extra></extra>',
                'customdata': indicators
            }],
            'layout': {
                'title': {
                    'text': 'Most Predictive Economic Indicators',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Number of Companies with Significant Correlation',
                    'range': [0, max(frequencies) * 1.15]
                },
                'yaxis': {
                    'tickmode': 'array',
                    'tickvals': list(range(len(indicators)))[::-1],
                    'ticktext': indicators,
                    'tickfont': {'size': 10}
                },
                'height': 600,
                'margin': {'l': 280, 'r': 100, 't': 80, 'b': 80},
                'annotations': [
                    {
                        'text': f'Based on {total_companies} companies analyzed',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.08,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating top predictive indicators: {e}")
        return None


def create_chart_22_intelligence_score_gauge(correlation_analysis: Dict,
                                             univariate_models: Dict,
                                             multifactor_models: Dict) -> Optional[Dict]:
    """Chart 22: Portfolio Intelligence Score - Gauge Chart"""
    
    if not correlation_analysis:
        return None
    
    try:
        total_companies = len(correlation_analysis)
        total_significant = sum(len(analysis['significant_correlations']) 
                              for analysis in correlation_analysis.values())
        avg_per_company = total_significant / total_companies if total_companies > 0 else 0
        
        # Calculate component scores
        correlation_score = min(10, avg_per_company * 2.5)  # Max 10 at 4 correlations
        
        uni_success_rate = len(univariate_models) / total_companies if total_companies > 0 else 0
        mf_success_rate = len(multifactor_models) / total_companies if total_companies > 0 else 0
        modeling_score = (uni_success_rate + mf_success_rate) * 5  # Max 10
        
        strongest_correlations = []
        for company_data in correlation_analysis.values():
            if company_data['all_correlations']:
                strongest = max(company_data['all_correlations'].values(), key=lambda x: x['abs_correlation'])
                strongest_correlations.append(strongest['abs_correlation'])
        
        avg_strongest = np.mean(strongest_correlations) if strongest_correlations else 0
        quality_score = avg_strongest * 20  # Max 10 at correlation of 0.5
        
        # Overall intelligence score (0-10)
        portfolio_intelligence_score = (correlation_score + modeling_score + quality_score) / 3
        
        # Determine color
        if portfolio_intelligence_score >= 7:
            color = '#10b981'
            assessment = 'Excellent'
        elif portfolio_intelligence_score >= 5:
            color = '#3b82f6'
            assessment = 'Good'
        elif portfolio_intelligence_score >= 3:
            color = '#f59e0b'
            assessment = 'Fair'
        else:
            color = '#ef4444'
            assessment = 'Developing'
        
        fig_data = {
            'data': [{
                'type': 'indicator',
                'mode': 'gauge+number+delta',
                'value': portfolio_intelligence_score,
                'number': {'suffix': '/10', 'font': {'size': 50, 'weight': 'bold'}},
                'delta': {'reference': 5, 'increasing': {'color': '#10b981'}},
                'gauge': {
                    'axis': {'range': [0, 10], 'tickwidth': 2, 'tickcolor': '#64748b'},
                    'bar': {'color': color, 'thickness': 0.8},
                    'bgcolor': 'rgba(0,0,0,0.05)',
                    'borderwidth': 2,
                    'bordercolor': '#64748b',
                    'steps': [
                        {'range': [0, 3], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [3, 5], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [5, 7], 'color': 'rgba(59, 130, 246, 0.2)'},
                        {'range': [7, 10], 'color': 'rgba(16, 185, 129, 0.2)'}
                    ],
                    'threshold': {
                        'line': {'color': '#1e293b', 'width': 4},
                        'thickness': 0.8,
                        'value': portfolio_intelligence_score
                    }
                },
                'domain': {'x': [0, 1], 'y': [0, 1]}
            }],
            'layout': {
                'title': {
                    'text': f'Portfolio Signal Intelligence Score<br><sub>Assessment: {assessment}</sub>',
                    'font': {'size': 20, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'height': 450,
                'margin': {'l': 50, 'r': 50, 't': 100, 'b': 50},
                'annotations': [
                    {
                        'text': f'Correlation: {correlation_score:.1f} | Modeling: {modeling_score:.1f} | Quality: {quality_score:.1f}',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.05,
                        'showarrow': False,
                        'font': {'size': 11, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating intelligence score gauge: {e}")
        return None


# =============================================================================
# CHART GROUP 6: ADDITIONAL SPECIALTY CHARTS (3 CHARTS)
# =============================================================================

def create_chart_23_extended_correlation_heatmap(extended_correlation: Dict) -> Optional[Dict]:
    """Chart 23: Extended Financial Metrics Correlation Heatmap"""
    
    if not extended_correlation:
        return None
    
    try:
        # Get all unique financial metrics
        all_metrics = set()
        for company_data in extended_correlation.values():
            all_metrics.update(company_data.keys())
        
        if not all_metrics:
            return None
        
        sorted_metrics = sorted(all_metrics)
        companies_list = list(extended_correlation.keys())
        
        # Create correlation matrix (strongest correlation per metric)
        correlation_matrix = []
        for company in companies_list:
            company_row = []
            for metric in sorted_metrics:
                if metric in extended_correlation[company]:
                    strongest = extended_correlation[company][metric]['strongest_correlation']
                    corr_val = strongest[1]['correlation']
                    company_row.append(corr_val)
                else:
                    company_row.append(np.nan)
            correlation_matrix.append(company_row)
        
        fig_data = {
            'data': [{
                'type': 'heatmap',
                'z': correlation_matrix,
                'x': [metric[:25] for metric in sorted_metrics],
                'y': [comp[:18] for comp in companies_list],
                'colorscale': 'RdBu',
                'zmid': 0,
                'colorbar': {
                    'title': 'Strongest<br>Correlation',
                    'titleside': 'right'
                },
                'hoverongaps': False,
                'hovertemplate': '<b>%{y}</b><br>Metric: %{x}<br>Strongest Correlation: <b>%{z:.3f}</b><extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': 'Extended Financial Metrics - Strongest Macro Correlations',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Financial Metrics',
                    'tickangle': -45,
                    'side': 'bottom',
                    'tickfont': {'size': 9}
                },
                'yaxis': {
                    'title': 'Companies',
                    'autorange': 'reversed',
                    'tickfont': {'size': 10}
                },
                'height': 600,
                'margin': {'l': 150, 'r': 100, 't': 80, 'b': 180}
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating extended correlation heatmap: {e}")
        return None


def create_chart_24_model_comparison_scatter(univariate_models: Dict,
                                            multifactor_models: Dict,
                                            model_comparison: Dict) -> Optional[Dict]:
    """Chart 24: Comprehensive Model Comparison Scatter - R² vs AIC"""
    
    if not model_comparison:
        return None
    
    try:
        # Separate univariate and multifactor models
        uni_r2 = []
        uni_aic = []
        uni_names = []
        
        mf_r2 = []
        mf_aic = []
        mf_names = []
        
        for model_id, model_data in model_comparison.items():
            if model_data['model_type'] == 'Univariate':
                uni_r2.append(model_data['adj_r_squared'])
                uni_aic.append(model_data['aic'])
                uni_names.append(model_data['company'][:12])
            else:
                mf_r2.append(model_data['adj_r_squared'])
                mf_aic.append(model_data['aic'])
                mf_names.append(model_data['company'][:12])
        
        fig_data = {
            'data': [
                {
                    'type': 'scatter',
                    'name': 'Univariate Models',
                    'x': uni_r2,
                    'y': uni_aic,
                    'mode': 'markers',
                    'marker': {
                        'size': 12,
                        'color': '#3b82f6',
                        'opacity': 0.7,
                        'symbol': 'circle',
                        'line': {'color': '#1e293b', 'width': 1}
                    },
                    'text': uni_names,
                    'hovertemplate': '<b>%{text}</b><br>Adj R²: %{x:.3f}<br>AIC: <b>%{y:.1f}</b><extra></extra>'
                },
                {
                    'type': 'scatter',
                    'name': 'Multifactor Models',
                    'x': mf_r2,
                    'y': mf_aic,
                    'mode': 'markers',
                    'marker': {
                        'size': 14,
                        'color': '#10b981',
                        'opacity': 0.7,
                        'symbol': 'diamond',
                        'line': {'color': '#1e293b', 'width': 1}
                    },
                    'text': mf_names,
                    'hovertemplate': '<b>%{text}</b><br>Adj R²: %{x:.3f}<br>AIC: <b>%{y:.1f}</b><extra></extra>'
                }
            ],
            'layout': {
                'title': {
                    'text': 'Model Comparison: Performance vs Parsimony',
                    'font': {'size': 18, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Adjusted R² (Higher is Better)',
                    'range': [0, 1]
                },
                'yaxis': {
                    'title': 'AIC (Lower is Better)',
                    'autorange': 'reversed'
                },
                'height': 600,
                'legend': {
                    'x': 0.02,
                    'y': 0.02,
                    'bgcolor': 'rgba(255,255,255,0.9)',
                    'bordercolor': '#64748b',
                    'borderwidth': 1
                },
                'annotations': [
                    {
                        'text': 'Top-left quadrant: Best models (high R², low AIC)',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.12,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating model comparison scatter: {e}")
        return None


# =============================================================================
# HELPER: GET ALL CHART FUNCTIONS
# =============================================================================

def get_all_chart_functions():
    """Return dictionary of all chart creation functions"""
    return {
        'chart_01': create_chart_01_correlation_heatmap,
        'chart_02': create_chart_02_top_correlations_bar,
        'chart_03': create_chart_03_correlation_distribution,
        'chart_04': create_chart_04_pvalue_vs_correlation_scatter,
        'chart_05': create_chart_05_company_sensitivity_rankings,
        'chart_06': create_chart_06_univariate_r2_comparison,
        'chart_07': create_chart_07_slope_coefficients,
        'chart_08': create_chart_08_statistical_significance_scatter,
        'chart_09': create_chart_09_model_quality_pie,
        'chart_10': create_chart_10_uni_vs_multi_comparison,
        'chart_11': create_chart_11_r2_improvement,
        'chart_12': create_chart_12_aic_comparison,
        'chart_13': create_chart_13_complexity_vs_performance,
        'chart_14': create_chart_14_diagnostic_scores,
        'chart_15': create_chart_15_durbin_watson_test,
        'chart_16': create_chart_16_normality_test,
        'chart_17': create_chart_17_heteroscedasticity_test,
        'chart_18': create_chart_18_portfolio_metrics_summary,
        'chart_19': create_chart_19_signal_quality_pie,
        'chart_20': create_chart_20_model_performance_evolution,
        'chart_21': create_chart_21_top_predictive_indicators,
        'chart_22': create_chart_22_intelligence_score_gauge,
        'chart_23': create_chart_23_extended_correlation_heatmap,
        'chart_24': create_chart_24_model_comparison_scatter
    }

"""
Chart 25: Lag Distribution Analysis - Multi-Panel Dashboard
Showcases the sophisticated lag analysis feature (0, 1, 2 year lags)
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional


def create_chart_25_lag_distribution_dashboard(correlation_analysis: Dict) -> Optional[Dict]:
    """
    Chart 25: Comprehensive Lag Distribution Analysis Dashboard
    
    Shows:
    - Overall lag distribution across all correlations
    - Top indicators by lag type (leading vs coincident)
    - Company-level lag preferences
    - Timing insights for macro-financial relationships
    """
    
    if not correlation_analysis:
        return None
    
    try:
        # Collect all lag information
        total_lag_0 = 0
        total_lag_1 = 0
        total_lag_2 = 0
        
        company_lag_prefs = {}
        indicator_by_lag = {0: {}, 1: {}, 2: {}}
        
        for company, data in correlation_analysis.items():
            # Get company lag distribution
            lag_dist = data.get('lag_distribution', {0: 0, 1: 0, 2: 0})
            total_lag_0 += lag_dist.get(0, 0)
            total_lag_1 += lag_dist.get(1, 0)
            total_lag_2 += lag_dist.get(2, 0)
            
            # Store company preference
            company_lag_prefs[company] = lag_dist
            
            # Track indicators by lag
            for indicator, stats in data['all_correlations'].items():
                best_lag = stats.get('best_lag', 0)
                if indicator not in indicator_by_lag[best_lag]:
                    indicator_by_lag[best_lag][indicator] = 0
                indicator_by_lag[best_lag][indicator] += 1
        
        total_correlations = total_lag_0 + total_lag_1 + total_lag_2
        
        if total_correlations == 0:
            return None
        
        # Find top indicators for each lag type
        top_lag_0 = sorted(indicator_by_lag[0].items(), key=lambda x: x[1], reverse=True)[:5]
        top_lag_1 = sorted(indicator_by_lag[1].items(), key=lambda x: x[1], reverse=True)[:5]
        top_lag_2 = sorted(indicator_by_lag[2].items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Create multi-trace figure with subplots
        fig_data = {
            'data': [],
            'layout': {
                'title': {
                    'text': 'Lag Distribution Analysis: Leading vs Coincident Indicators',
                    'font': {'size': 20, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'height': 800,
                'showlegend': True,
                'grid': {
                    'rows': 2,
                    'columns': 2,
                    'pattern': 'independent',
                    'roworder': 'top to bottom'
                },
                'annotations': []
            }
        }
        
        # =====================================================================
        # SUBPLOT 1 (Top-Left): Overall Lag Distribution - Pie Chart
        # =====================================================================
        fig_data['data'].append({
            'type': 'pie',
            'labels': ['Contemporaneous<br>(Lag 0)', 'Leading 1Y<br>(Lag 1)', 'Leading 2Y<br>(Lag 2)'],
            'values': [total_lag_0, total_lag_1, total_lag_2],
            'marker': {
                'colors': ['#3b82f6', '#10b981', '#f59e0b'],
                'line': {'color': '#ffffff', 'width': 2}
            },
            'textinfo': 'label+percent+value',
            'textposition': 'outside',
            'textfont': {'size': 11},
            'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            'hole': 0.4,
            'domain': {'x': [0, 0.48], 'y': [0.52, 1]},
            'name': 'Lag Distribution'
        })
        
        # Center annotation for pie chart
        fig_data['layout']['annotations'].append({
            'text': f'<b>{total_correlations}</b><br>Total<br>Correlations',
            'x': 0.24,
            'y': 0.76,
            'font': {'size': 16, 'weight': 'bold'},
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper'
        })
        
        # Subplot title
        fig_data['layout']['annotations'].append({
            'text': '<b>Overall Lag Distribution</b>',
            'x': 0.24,
            'y': 1.02,
            'font': {'size': 14},
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper'
        })
        
        # =====================================================================
        # SUBPLOT 2 (Top-Right): Company Lag Preferences - Stacked Bar
        # =====================================================================
        companies = list(company_lag_prefs.keys())[:10]  # Top 10 companies
        lag_0_counts = [company_lag_prefs[c].get(0, 0) for c in companies]
        lag_1_counts = [company_lag_prefs[c].get(1, 0) for c in companies]
        lag_2_counts = [company_lag_prefs[c].get(2, 0) for c in companies]
        
        company_labels = [comp[:12] for comp in companies]
        
        fig_data['data'].extend([
            {
                'type': 'bar',
                'name': 'Lag 0 (Coincident)',
                'x': company_labels,
                'y': lag_0_counts,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Lag 0: %{y}<extra></extra>',
                'xaxis': 'x2',
                'yaxis': 'y2',
                'showlegend': True
            },
            {
                'type': 'bar',
                'name': 'Lag 1Y (Leading)',
                'x': company_labels,
                'y': lag_1_counts,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Lag 1Y: %{y}<extra></extra>',
                'xaxis': 'x2',
                'yaxis': 'y2',
                'showlegend': True
            },
            {
                'type': 'bar',
                'name': 'Lag 2Y (Leading)',
                'x': company_labels,
                'y': lag_2_counts,
                'marker': {'color': '#f59e0b'},
                'hovertemplate': '<b>%{x}</b><br>Lag 2Y: %{y}<extra></extra>',
                'xaxis': 'x2',
                'yaxis': 'y2',
                'showlegend': True
            }
        ])
        
        fig_data['layout']['xaxis2'] = {
            'domain': [0.52, 1],
            'anchor': 'y2',
            'title': 'Companies',
            'tickangle': -45,
            'tickfont': {'size': 9}
        }
        fig_data['layout']['yaxis2'] = {
            'domain': [0.52, 1],
            'anchor': 'x2',
            'title': 'Number of Correlations'
        }
        fig_data['layout']['barmode'] = 'stack'
        
        # Subplot title
        fig_data['layout']['annotations'].append({
            'text': '<b>Company Lag Preferences</b>',
            'x': 0.76,
            'y': 1.02,
            'font': {'size': 14},
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper'
        })
        
        # =====================================================================
        # SUBPLOT 3 (Bottom-Left): Top Coincident Indicators (Lag 0)
        # =====================================================================
        if top_lag_0:
            lag_0_indicators = [ind[:30] for ind, _ in top_lag_0]
            lag_0_counts = [count for _, count in top_lag_0]
            
            fig_data['data'].append({
                'type': 'bar',
                'y': list(range(len(lag_0_indicators)))[::-1],
                'x': lag_0_counts,
                'orientation': 'h',
                'marker': {'color': '#3b82f6'},
                'text': lag_0_counts,
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'hovertemplate': '<b>%{customdata}</b><br>Companies: %{x}<extra></extra>',
                'customdata': lag_0_indicators,
                'xaxis': 'x3',
                'yaxis': 'y3',
                'showlegend': False
            })
            
            fig_data['layout']['xaxis3'] = {
                'domain': [0, 0.48],
                'anchor': 'y3',
                'title': 'Number of Companies'
            }
            fig_data['layout']['yaxis3'] = {
                'domain': [0, 0.45],
                'anchor': 'x3',
                'tickmode': 'array',
                'tickvals': list(range(len(lag_0_indicators)))[::-1],
                'ticktext': lag_0_indicators,
                'tickfont': {'size': 9}
            }
            
            # Subplot title
            fig_data['layout']['annotations'].append({
                'text': '<b>Top Coincident Indicators (Lag 0)</b>',
                'x': 0.24,
                'y': 0.48,
                'font': {'size': 14, 'color': '#3b82f6'},
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper'
            })
        
        # =====================================================================
        # SUBPLOT 4 (Bottom-Right): Top Leading Indicators (Lag 1-2)
        # =====================================================================
        # Combine lag 1 and lag 2 indicators
        combined_leading = {}
        for ind, count in top_lag_1:
            combined_leading[ind] = combined_leading.get(ind, 0) + count
        for ind, count in top_lag_2:
            combined_leading[ind] = combined_leading.get(ind, 0) + count
        
        top_leading = sorted(combined_leading.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_leading:
            leading_indicators = [ind[:30] for ind, _ in top_leading]
            leading_counts = [count for _, count in top_leading]
            
            # Determine which lag is dominant for each
            colors_leading = []
            for ind, _ in top_leading:
                lag_1_count = indicator_by_lag[1].get(ind, 0)
                lag_2_count = indicator_by_lag[2].get(ind, 0)
                if lag_1_count > lag_2_count:
                    colors_leading.append('#10b981')  # Lag 1 dominant
                else:
                    colors_leading.append('#f59e0b')  # Lag 2 dominant
            
            fig_data['data'].append({
                'type': 'bar',
                'y': list(range(len(leading_indicators)))[::-1],
                'x': leading_counts,
                'orientation': 'h',
                'marker': {'color': colors_leading},
                'text': leading_counts,
                'textposition': 'outside',
                'textfont': {'size': 10, 'weight': 'bold'},
                'hovertemplate': '<b>%{customdata}</b><br>Companies: %{x}<extra></extra>',
                'customdata': leading_indicators,
                'xaxis': 'x4',
                'yaxis': 'y4',
                'showlegend': False
            })
            
            fig_data['layout']['xaxis4'] = {
                'domain': [0.52, 1],
                'anchor': 'y4',
                'title': 'Number of Companies'
            }
            fig_data['layout']['yaxis4'] = {
                'domain': [0, 0.45],
                'anchor': 'x4',
                'tickmode': 'array',
                'tickvals': list(range(len(leading_indicators)))[::-1],
                'ticktext': leading_indicators,
                'tickfont': {'size': 9}
            }
            
            # Subplot title
            fig_data['layout']['annotations'].append({
                'text': '<b>Top Leading Indicators (Lag 1-2Y)</b>',
                'x': 0.76,
                'y': 0.48,
                'font': {'size': 14, 'color': '#10b981'},
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper'
            })
        
        # =====================================================================
        # Overall insights annotation at bottom
        # =====================================================================
        lag_0_pct = (total_lag_0 / total_correlations * 100) if total_correlations > 0 else 0
        lag_1_pct = (total_lag_1 / total_correlations * 100) if total_correlations > 0 else 0
        lag_2_pct = (total_lag_2 / total_correlations * 100) if total_correlations > 0 else 0
        
        leading_pct = lag_1_pct + lag_2_pct
        
        if leading_pct > 50:
            insight = f"<b>Strong Leading Signal Capability:</b> {leading_pct:.0f}% of correlations use lagged indicators (predictive)"
        elif leading_pct > 30:
            insight = f"<b>Moderate Leading Indicators:</b> {leading_pct:.0f}% predictive correlations with 1-2 year lags"
        else:
            insight = f"<b>Coincident Focus:</b> {lag_0_pct:.0f}% contemporaneous relationships dominate"
        
        fig_data['layout']['annotations'].append({
            'text': insight,
            'x': 0.5,
            'y': -0.05,
            'font': {'size': 12, 'color': '#667eea'},
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper'
        })
        
        # Legend positioning
        fig_data['layout']['legend'] = {
            'x': 0.52,
            'y': 0.95,
            'bgcolor': 'rgba(255,255,255,0.9)',
            'bordercolor': '#64748b',
            'borderwidth': 1,
            'orientation': 'v'
        }
        
        fig_data['layout']['margin'] = {'l': 180, 'r': 50, 't': 100, 'b': 80}
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating lag distribution dashboard: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_chart_25_simple_lag_bars(correlation_analysis: Dict) -> Optional[Dict]:
    """
    Chart 25 Alternative: Simple Lag Distribution Bar Chart
    Fallback if the dashboard is too complex
    """
    
    if not correlation_analysis:
        return None
    
    try:
        # Aggregate lag counts
        lag_counts = {0: 0, 1: 0, 2: 0}
        
        for company_data in correlation_analysis.values():
            lag_dist = company_data.get('lag_distribution', {0: 0, 1: 0, 2: 0})
            for lag, count in lag_dist.items():
                lag_counts[lag] = lag_counts.get(lag, 0) + count
        
        total = sum(lag_counts.values())
        
        if total == 0:
            return None
        
        labels = ['Contemporaneous\n(Lag 0 Years)', 'Leading 1 Year\n(Lag 1)', 'Leading 2 Years\n(Lag 2)']
        values = [lag_counts[0], lag_counts[1], lag_counts[2]]
        percentages = [(v/total*100) for v in values]
        colors = ['#3b82f6', '#10b981', '#f59e0b']
        
        fig_data = {
            'data': [{
                'type': 'bar',
                'x': labels,
                'y': values,
                'marker': {
                    'color': colors,
                    'line': {'color': '#1e293b', 'width': 1}
                },
                'text': [f'{v}<br>({p:.1f}%)' for v, p in zip(values, percentages)],
                'textposition': 'outside',
                'textfont': {'size': 14, 'weight': 'bold'},
                'hovertemplate': '<b>%{x}</b><br>Count: %{y}<br>Percentage: %{customdata:.1f}%<extra></extra>',
                'customdata': percentages
            }],
            'layout': {
                'title': {
                    'text': 'Lag Distribution: Leading vs Coincident Indicators',
                    'font': {'size': 20, 'weight': 'bold'},
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Lag Type',
                    'tickfont': {'size': 12}
                },
                'yaxis': {
                    'title': 'Number of Correlations',
                    'range': [0, max(values) * 1.2]
                },
                'height': 550,
                'margin': {'l': 80, 'r': 50, 't': 100, 'b': 100},
                'annotations': [
                    {
                        'text': f'<b>Total Correlations: {total}</b> | Leading Indicators: {percentages[1]+percentages[2]:.0f}% (predictive power)',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.15,
                        'showarrow': False,
                        'font': {'size': 12, 'color': '#667eea'}
                    },
                    {
                        'text': 'Lag 0 = Contemporaneous correlation | Lag 1-2 = Leading indicators (macro predicts future revenue)',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': -0.2,
                        'showarrow': False,
                        'font': {'size': 10, 'color': '#64748b'}
                    }
                ]
            }
        }
        
        return fig_data
        
    except Exception as e:
        print(f"Error creating simple lag bars: {e}")
        return None


# Export both functions
__all__ = [
    'create_chart_25_lag_distribution_dashboard',
    'create_chart_25_simple_lag_bars'
]