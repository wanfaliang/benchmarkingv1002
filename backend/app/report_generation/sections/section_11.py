"""Section 11: Risk & Alert Panel Analysis"""

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
    format_number,
    format_percentage,
    build_enhanced_table,
    build_badge,
    build_colored_cell
)

def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 11: Risk & Alert Panel Analysis.
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string
    """
    
    # Extract data from collector
    companies = collector.companies
    df = collector.get_all_financial_data()
    
    if df.empty:
        return generate_section_wrapper(
            11,
            "Risk & Alert Panel Analysis",
            '<div class="info-box warning"><p>Insufficient data available for risk and alert panel analysis.</p></div>'
        )
    
    # Build all subsections
    section_11a_html = _build_section_11a_risk_detection(df, companies)
    section_11b_html = _build_section_11b_alert_generation(df, companies)
    section_11c_html = _build_section_11c_risk_scoring(df, companies)
    section_11d_html = _build_section_11d_predictive_modeling(df, companies, collector)
    section_11e_html = _build_section_11e_visualizations(df, companies, analysis_id)
    section_11f_html = _build_section_11f_strategic_framework(df, companies,analysis_id)
    
    # Combine all subsections
    content = f"""
    <div class="section-content-wrapper">
        {section_11a_html}
        {build_section_divider() if section_11b_html else ""}
        {section_11b_html}
        {build_section_divider() if section_11c_html else ""}
        {section_11c_html}
        {build_section_divider() if section_11d_html else ""}
        {section_11d_html}
        {build_section_divider() if section_11e_html else ""}
        {section_11e_html}
        {build_section_divider() if section_11f_html else ""}
        {section_11f_html}
    </div>
    """
    
    return generate_section_wrapper(11, "Risk & Alert Panel Analysis", content)


# =============================================================================
# SUBSECTION 11A: COMPREHENSIVE RISK DETECTION & MONITORING SYSTEM
# =============================================================================

def _build_section_11a_risk_detection(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 11A: Comprehensive Risk Detection & Monitoring System"""
    
    # Generate risk analysis
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    
    if not risk_analysis:
        return _build_collapsible_subsection(
            "11A",
            "Comprehensive Risk Detection & Monitoring System",
            '<div class="info-box warning"><p>Insufficient data for risk detection analysis.</p></div>'
        )
    
    # Build KPI summary cards
    total_companies = len(risk_analysis)
    avg_risk_score = np.mean([analysis['overall_risk_score'] for analysis in risk_analysis.values()])
    total_alerts = sum(len(analysis['alert_triggers']) for analysis in risk_analysis.values())
    high_risk_count = sum(1 for analysis in risk_analysis.values() if analysis['overall_risk_score'] > 6)
    
    kpi_cards = build_stat_grid([
        {
            "label": "Portfolio Companies",
            "value": str(total_companies),
            "description": "Under Risk Monitoring",
            "type": "info"
        },
        {
            "label": "Avg Risk Score",
            "value": f"{avg_risk_score:.1f}/10",
            "description": "Portfolio Composite",
            "type": "warning" if avg_risk_score > 6 else "success" if avg_risk_score < 4 else "default"
        },
        {
            "label": "Total Alerts",
            "value": str(total_alerts),
            "description": "Risk Triggers Detected",
            "type": "danger" if total_alerts > total_companies * 2 else "warning" if total_alerts > total_companies else "success"
        },
        {
            "label": "High Risk Companies",
            "value": str(high_risk_count),
            "description": f"{high_risk_count/total_companies*100:.0f}% of Portfolio",
            "type": "danger" if high_risk_count > total_companies * 0.3 else "warning"
        }
    ])
    
    # Build risk metrics table
    risk_table_df = _prepare_risk_metrics_table(risk_analysis)
    
    # Color coding function for risk ratings
    def color_risk_rating(value):
        value_str = str(value).lower()
        if 'critical' in value_str or 'extreme' in value_str:
            return 'poor'
        elif 'high' in value_str:
            return 'fair'
        elif 'moderate' in value_str:
            return 'good'
        else:
            return 'excellent'
    
    color_columns = {
        'Risk Rating': color_risk_rating
    }
    
    risk_table_html = build_enhanced_table(
        risk_table_df,
        table_id="risk-metrics-table",
        color_columns=color_columns,
        badge_columns=['Financial Risk', 'Operational Risk', 'Liquidity Risk'],
        sortable=True,
        searchable=True
    )
    
    # Build summary narrative
    summary_text = _generate_risk_analysis_summary(risk_analysis, total_companies, avg_risk_score, total_alerts, high_risk_count)
    
    subsection_content = f"""
    <h3>Multi-Dimensional Risk Assessment Framework</h3>
    
    {kpi_cards}
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Portfolio Risk Metrics Overview</h4>
        {risk_table_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Risk Analysis Summary</h4>
        {summary_text}
    </div>
    """
    
    return _build_collapsible_subsection(
        "11A",
        "Comprehensive Risk Detection & Monitoring System",
        subsection_content
    )


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


def _prepare_risk_metrics_table(risk_analysis: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare risk metrics table DataFrame"""
    
    table_data = []
    
    for company_name, analysis in risk_analysis.items():
        overall_score = analysis['overall_risk_score']
        alert_count = len(analysis['alert_triggers'])
        high_severity = sum(1 for alert in analysis['alert_triggers'] if alert['severity'] == 'High')
        
        # Risk rating
        if overall_score <= 3:
            risk_rating = "Low Risk"
        elif overall_score <= 6:
            risk_rating = "Moderate Risk"
        elif overall_score <= 8:
            risk_rating = "High Risk"
        else:
            risk_rating = "Critical Risk"
        
        table_data.append({
            'Company': company_name,
            'Overall Risk Score': f"{overall_score:.1f}/10",
            'Financial Risk': _get_risk_level(analysis['financial_risks']),
            'Operational Risk': _get_risk_level(analysis['operational_risks']),
            'Liquidity Risk': _get_risk_level(analysis['liquidity_risks']),
            'Alert Count': alert_count,
            'High Severity': high_severity,
            'Risk Rating': risk_rating
        })
    
    return pd.DataFrame(table_data)


def _get_risk_level(risk_dict: Dict) -> str:
    """Convert risk metrics to risk level"""
    risk_values = [v for v in risk_dict.values() if isinstance(v, (int, float))]
    if not risk_values:
        return "Unknown"
    
    avg_risk = np.mean(risk_values)
    if avg_risk <= 0.3:
        return "Low"
    elif avg_risk <= 0.6:
        return "Moderate"
    else:
        return "High"


def _generate_risk_analysis_summary(risk_analysis: Dict, total_companies: int, 
                                   avg_risk_score: float, total_alerts: int, 
                                   high_risk_count: int) -> str:
    """Generate risk analysis summary"""
    
    high_severity_alerts = sum(
        sum(1 for alert in analysis['alert_triggers'] if alert['severity'] == 'High') 
        for analysis in risk_analysis.values()
    )
    
    summary_parts = []
    
    # Portfolio risk profile
    if avg_risk_score <= 4 and high_risk_count <= total_companies * 0.2:
        risk_profile = "demonstrates strong risk management with well-controlled exposures"
    elif avg_risk_score <= 6 and high_risk_count <= total_companies * 0.4:
        risk_profile = "shows moderate risk levels requiring standard monitoring"
    else:
        risk_profile = "requires enhanced risk management attention with elevated exposures"
    
    summary_parts.append(
        f"The portfolio of {total_companies} companies {risk_profile}, "
        f"with an average risk score of {avg_risk_score:.1f}/10. "
        f"{high_risk_count} companies ({high_risk_count/total_companies*100:.0f}%) are classified as high-risk, "
        f"triggering {total_alerts} total alerts including {high_severity_alerts} high-severity warnings."
    )
    
    # Multi-dimensional assessment
    summary_parts.append(
        "<br><br><strong>Multi-Dimensional Risk Assessment:</strong><br>"
        f"• <strong>Financial Risk Detection:</strong> "
        f"{'Elevated concerns' if avg_risk_score > 6 else 'Moderate monitoring' if avg_risk_score > 4 else 'Low risk profile'} "
        f"in revenue, profitability, and leverage metrics<br>"
        f"• <strong>Operational Risk Monitoring:</strong> "
        f"{'Active surveillance' if high_severity_alerts > total_companies * 0.5 else 'Standard monitoring'} "
        f"of cash flow, efficiency, and capital allocation<br>"
        f"• <strong>Liquidity Risk Management:</strong> "
        f"{'Enhanced oversight' if high_risk_count > 0 else 'Regular monitoring'} "
        f"of working capital and cash position adequacy"
    )
    
    # Strategic intelligence
    if high_risk_count > 0 and avg_risk_score > 7:
        strategic_rec = "Immediate strategic intervention required with targeted risk mitigation across multiple dimensions"
    elif high_risk_count > total_companies * 0.3:
        strategic_rec = "Enhanced monitoring and selective intervention recommended for high-risk positions"
    else:
        strategic_rec = "Proactive monitoring with standard risk management protocols is appropriate"
    
    summary_parts.append(
        f"<br><br><strong>Strategic Risk Intelligence:</strong> {strategic_rec}."
    )
    
    return build_info_box(
        "".join(summary_parts),
        box_type="info",
        title="Comprehensive Risk Detection Summary"
    )


# =============================================================================
# SUBSECTION 11B: AUTOMATED ALERT GENERATION & CLASSIFICATION SYSTEM
# =============================================================================

def _build_section_11b_alert_generation(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 11B: Automated Alert Generation & Classification System"""
    
    # Get risk analysis from 11A (we'll need to pass this properly in real implementation)
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    
    if not risk_analysis:
        return _build_collapsible_subsection(
            "11B",
            "Automated Alert Generation & Classification System",
            '<div class="info-box warning"><p>Insufficient data for alert generation.</p></div>'
        )
    
    # Generate alert system
    alert_system = _generate_automated_alerts(df, companies, risk_analysis)
    
    if not alert_system:
        return _build_collapsible_subsection(
            "11B",
            "Automated Alert Generation & Classification System",
            '<div class="info-box warning"><p>No alerts generated.</p></div>'
        )
    
    # Build KPI summary cards
    total_alerts = sum(alerts['alert_summary']['total_alerts'] for alerts in alert_system.values())
    total_critical = sum(alerts['alert_summary']['critical_count'] for alerts in alert_system.values())
    total_warning = sum(alerts['alert_summary']['warning_count'] for alerts in alert_system.values())
    companies_with_critical = sum(1 for alerts in alert_system.values() if alerts['alert_summary']['critical_count'] > 0)
    avg_priority = np.mean([alerts['alert_summary']['priority_score'] for alerts in alert_system.values()])
    
    kpi_cards = build_stat_grid([
        {
            "label": "Total Alerts",
            "value": str(total_alerts),
            "description": "Across All Companies",
            "type": "info"
        },
        {
            "label": "Critical Alerts",
            "value": str(total_critical),
            "description": f"{companies_with_critical} Companies Affected",
            "type": "danger" if total_critical > 0 else "success"
        },
        {
            "label": "Warning Alerts",
            "value": str(total_warning),
            "description": "Requiring Attention",
            "type": "warning" if total_warning > len(companies) * 0.5 else "info"
        },
        {
            "label": "Avg Priority Score",
            "value": f"{avg_priority:.0f}/100",
            "description": "Portfolio Priority",
            "type": "danger" if avg_priority > 70 else "warning" if avg_priority > 40 else "success"
        }
    ])
    
    # Build alerts table
    alerts_table_df = _prepare_alerts_table(alert_system)
    
    # Color coding for action priority
    def color_action_priority(value):
        value_str = str(value).lower()
        if 'immediate' in value_str:
            return 'poor'
        elif 'high' in value_str:
            return 'fair'
        elif 'medium' in value_str:
            return 'good'
        else:
            return 'excellent'
    
    color_columns = {
        'Action Priority': color_action_priority
    }
    
    alerts_table_html = build_enhanced_table(
        alerts_table_df,
        table_id="alerts-table",
        color_columns=color_columns,
        badge_columns=['Alert Frequency', 'Risk Direction'],
        sortable=True,
        searchable=True
    )
    
    # Build alert details section
    alert_details_html = _build_alert_details_section(alert_system)
    
    # Build summary narrative
    summary_text = _generate_alerts_summary(alert_system, total_alerts, total_critical, 
                                           total_warning, companies_with_critical, avg_priority)
    
    subsection_content = f"""
    <h3>Real-Time Alert Detection & Severity Assessment</h3>
    
    {kpi_cards}
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Portfolio Alert Overview</h4>
        {alerts_table_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Detailed Alert Analysis</h4>
        {alert_details_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Alert System Summary</h4>
        {summary_text}
    </div>
    """
    
    return _build_collapsible_subsection(
        "11B",
        "Automated Alert Generation & Classification System",
        subsection_content
    )


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


def _prepare_alerts_table(alert_system: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare alerts table DataFrame"""
    
    table_data = []
    
    for company_name, alerts in alert_system.items():
        summary = alerts['alert_summary']
        trends = alerts['alert_trends']
        
        # Action priority
        if summary['critical_count'] > 0:
            action_priority = "Immediate"
        elif summary['warning_count'] > 2:
            action_priority = "High"
        elif summary['total_alerts'] > 3:
            action_priority = "Medium"
        else:
            action_priority = "Standard"
        
        table_data.append({
            'Company': company_name,
            'Total Alerts': summary['total_alerts'],
            'Critical': summary['critical_count'],
            'Warning': summary['warning_count'],
            'Alert Frequency': summary['alert_frequency'],
            'Priority Score': f"{summary['priority_score']:.0f}/100",
            'Risk Direction': trends.get('risk_direction', 'Unknown'),
            'Action Priority': action_priority
        })
    
    return pd.DataFrame(table_data)


def _build_alert_details_section(alert_system: Dict[str, Dict]) -> str:
    """Build detailed alert analysis section"""
    
    details_html = ""
    
    for company_name, alerts in alert_system.items():
        critical = alerts['critical_alerts']
        warning = alerts['warning_alerts']
        
        if not critical and not warning:
            continue
        
        company_details = f"<h5>{company_name}</h5>"
        
        if critical:
            company_details += "<strong>🔴 Critical Alerts:</strong><ul>"
            for alert in critical:
                company_details += f"<li><strong>{alert['trigger']}</strong>: {alert['description']} → <em>{alert['action_required']}</em></li>"
            company_details += "</ul>"
        
        if warning:
            company_details += "<strong>🟠 Warning Alerts:</strong><ul>"
            for alert in warning:
                company_details += f"<li><strong>{alert['trigger']}</strong>: {alert['description']} → <em>{alert['action_required']}</em></li>"
            company_details += "</ul>"
        
        details_html += build_info_box(
            company_details,
            box_type="danger" if critical else "warning",
            title=None
        )
    
    return details_html if details_html else "<p>No critical or warning alerts detected.</p>"


def _generate_alerts_summary(alert_system: Dict, total_alerts: int, total_critical: int,
                            total_warning: int, companies_with_critical: int, avg_priority: float) -> str:
    """Generate automated alerts summary"""
    
    total_companies = len(alert_system)
    companies_with_warnings = sum(1 for alerts in alert_system.values() if alerts['alert_summary']['warning_count'] > 0)
    
    summary_parts = []
    
    # Alert system performance
    if total_critical == 0 and companies_with_critical == 0:
        alert_performance = "demonstrates excellent alert system performance with no critical issues"
    elif total_critical <= total_companies * 0.5:
        alert_performance = "shows effective early warning system with manageable alert volume"
    else:
        alert_performance = "indicates elevated risk levels requiring alert system optimization"
    
    summary_parts.append(
        f"The automated alert system {alert_performance}, "
        f"detecting {total_alerts} total alerts across {total_companies} companies. "
        f"{total_critical} critical alerts affect {companies_with_critical} companies, "
        f"while {total_warning} warning-level issues span {companies_with_warnings} companies, "
        f"resulting in an average priority score of {avg_priority:.0f}/100."
    )
    
    # Real-time intelligence
    summary_parts.append(
        "<br><br><strong>Real-Time Alert Intelligence:</strong><br>"
        f"• <strong>Critical Alert Response:</strong> "
        f"{'No critical interventions required' if total_critical == 0 else f'Immediate attention needed for {total_critical} critical alerts'}<br>"
        f"• <strong>Warning Alert Management:</strong> "
        f"{'Enhanced monitoring protocols' if companies_with_warnings > total_companies * 0.3 else 'Standard monitoring'} "
        f"for early intervention<br>"
        f"• <strong>Alert System Coverage:</strong> "
        f"{'Comprehensive' if total_alerts >= total_companies * 3 else 'Moderate' if total_alerts >= total_companies else 'Limited'} "
        f"risk detection across portfolio"
    )
    
    # Strategic framework
    if total_alerts >= total_companies * 2 and total_critical <= total_companies * 0.2:
        strategic_assessment = "Sophisticated multi-tiered alert system providing comprehensive early warning capabilities"
    elif total_alerts >= total_companies:
        strategic_assessment = "Developing alert optimization with balanced detection and intervention protocols"
    else:
        strategic_assessment = "Enhanced alert system development needed for comprehensive risk coverage"
    
    summary_parts.append(
        f"<br><br><strong>Strategic Alert Framework:</strong> {strategic_assessment}."
    )
    
    return build_info_box(
        "".join(summary_parts),
        box_type="info",
        title="Automated Alert Generation Summary"
    )


# =============================================================================
# SUBSECTION 11C: RISK SCORING & PORTFOLIO-LEVEL RISK AGGREGATION
# =============================================================================

def _build_section_11c_risk_scoring(df: pd.DataFrame, companies: Dict[str, str]) -> str:
    """Build subsection 11C: Risk Scoring & Portfolio-Level Risk Aggregation"""
    
    # Generate risk analysis and alert system
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    alert_system = _generate_automated_alerts(df, companies, risk_analysis)
    
    if not risk_analysis:
        return _build_collapsible_subsection(
            "11C",
            "Risk Scoring & Portfolio-Level Risk Aggregation",
            '<div class="info-box warning"><p>Insufficient data for risk scoring analysis.</p></div>'
        )
    
    # Generate risk scoring system
    risk_scoring = _generate_risk_scoring_system(risk_analysis, alert_system, companies)
    
    if not risk_scoring:
        return _build_collapsible_subsection(
            "11C",
            "Risk Scoring & Portfolio-Level Risk Aggregation",
            '<div class="info-box warning"><p>Risk scoring unavailable.</p></div>'
        )
    
    # Build KPI summary cards
    avg_composite = np.mean([scoring['composite_risk_score'] for scoring in risk_scoring.values()])
    avg_financial = np.mean([scoring['financial_risk_score'] for scoring in risk_scoring.values()])
    avg_operational = np.mean([scoring['operational_risk_score'] for scoring in risk_scoring.values()])
    avg_liquidity = np.mean([scoring['liquidity_risk_score'] for scoring in risk_scoring.values()])
    
    high_risk_count = sum(1 for scoring in risk_scoring.values() 
                         if scoring['risk_rating'] in ['High Risk', 'Critical Risk', 'Extreme Risk'])
    
    kpi_cards = build_stat_grid([
        {
            "label": "Composite Risk",
            "value": f"{avg_composite:.1f}/10",
            "description": "Portfolio Average",
            "type": "danger" if avg_composite > 7 else "warning" if avg_composite > 5 else "success"
        },
        {
            "label": "Financial Risk",
            "value": f"{avg_financial:.1f}/10",
            "description": "Average Score",
            "type": "warning" if avg_financial > 6 else "success"
        },
        {
            "label": "Operational Risk",
            "value": f"{avg_operational:.1f}/10",
            "description": "Average Score",
            "type": "warning" if avg_operational > 6 else "success"
        },
        {
            "label": "Liquidity Risk",
            "value": f"{avg_liquidity:.1f}/10",
            "description": "Average Score",
            "type": "warning" if avg_liquidity > 6 else "success"
        }
    ])
    
    # Build risk scoring table
    scoring_table_df = _prepare_risk_scoring_table(risk_scoring)
    
    # Color coding functions
    def color_risk_rating(value):
        value_str = str(value).lower()
        if 'extreme' in value_str or 'critical' in value_str:
            return 'poor'
        elif 'high' in value_str:
            return 'fair'
        elif 'moderate' in value_str:
            return 'good'
        else:
            return 'excellent'
    
    def color_risk_trend(value):
        value_str = str(value).lower()
        if 'deteriorating' in value_str:
            return 'poor'
        elif 'improving' in value_str:
            return 'excellent'
        else:
            return 'good'
    
    color_columns = {
        'Risk Rating': color_risk_rating,
        'Risk Trend': color_risk_trend
    }
    
    scoring_table_html = build_enhanced_table(
        scoring_table_df,
        table_id="risk-scoring-table",
        color_columns=color_columns,
        badge_columns=['Risk Rating'],
        sortable=True,
        searchable=True
    )
    
    # Build risk rating distribution
    rating_distribution_html = _build_risk_rating_distribution(risk_scoring)
    
    # Build summary narrative
    summary_text = _generate_risk_scoring_summary(risk_scoring, avg_composite, high_risk_count)
    
    subsection_content = f"""
    <h3>Composite Risk Scores & Portfolio Risk Assessment</h3>
    
    {kpi_cards}
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Portfolio Risk Scoring Matrix</h4>
        {scoring_table_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Risk Rating Distribution</h4>
        {rating_distribution_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Risk Scoring Summary</h4>
        {summary_text}
    </div>
    """
    
    return _build_collapsible_subsection(
        "11C",
        "Risk Scoring & Portfolio-Level Risk Aggregation",
        subsection_content
    )


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


def _prepare_risk_scoring_table(risk_scoring: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare risk scoring table DataFrame"""
    
    table_data = []
    
    for company_name, scoring in risk_scoring.items():
        table_data.append({
            'Company': company_name,
            'Financial': f"{scoring['financial_risk_score']:.1f}/10",
            'Operational': f"{scoring['operational_risk_score']:.1f}/10",
            'Market': f"{scoring['market_risk_score']:.1f}/10",
            'Liquidity': f"{scoring['liquidity_risk_score']:.1f}/10",
            'Alert Severity': f"{scoring['alert_severity_score']:.1f}/10",
            'Composite Score': f"{scoring['composite_risk_score']:.1f}/10",
            'Risk Rating': scoring['risk_rating'],
            'Risk Trend': scoring['risk_trend']
        })
    
    return pd.DataFrame(table_data)


def _build_risk_rating_distribution(risk_scoring: Dict[str, Dict]) -> str:
    """Build risk rating distribution visualization"""
    
    # Count ratings
    rating_counts = {}
    for scoring in risk_scoring.values():
        rating = scoring['risk_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    # Build visual bars
    total = len(risk_scoring)
    bars_html = ""
    
    rating_order = ['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk', 'Extreme Risk']
    rating_colors = {
        'Low Risk': '#10b981',
        'Moderate Risk': '#3b82f6',
        'High Risk': '#f59e0b',
        'Critical Risk': '#ef4444',
        'Extreme Risk': '#dc2626'
    }
    
    for rating in rating_order:
        count = rating_counts.get(rating, 0)
        percentage = (count / total * 100) if total > 0 else 0
        color = rating_colors.get(rating, '#667eea')
        
        bars_html += f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600;">{rating}</span>
                <span style="font-weight: 700; color: {color};">{count} companies ({percentage:.0f}%)</span>
            </div>
            <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 8px; height: 24px;">
                <div style="width: {percentage}%; background: {color}; border-radius: 8px; height: 100%; 
                           transition: width 0.6s ease;"></div>
            </div>
        </div>
        """
    
    return bars_html


def _generate_risk_scoring_summary(risk_scoring: Dict, avg_composite: float, 
                                  high_risk_count: int) -> str:
    """Generate risk scoring summary"""
    
    total_companies = len(risk_scoring)
    
    # Rating distribution
    rating_counts = {}
    for scoring in risk_scoring.values():
        rating = scoring['risk_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    # Trend analysis
    deteriorating_count = sum(1 for scoring in risk_scoring.values() 
                             if 'Deteriorating' in scoring['risk_trend'])
    
    summary_parts = []
    
    # Portfolio assessment
    if avg_composite <= 4 and high_risk_count <= total_companies * 0.2:
        assessment = "demonstrates strong risk management with well-controlled exposures"
    elif avg_composite <= 6 and high_risk_count <= total_companies * 0.4:
        assessment = "shows moderate risk levels requiring standard monitoring"
    else:
        assessment = "requires enhanced risk management attention"
    
    summary_parts.append(
        f"The portfolio {assessment}, with an average composite risk score of {avg_composite:.1f}/10. "
        f"{high_risk_count} companies are rated as high-risk or above, while {deteriorating_count} companies "
        f"exhibit deteriorating risk trends requiring proactive intervention."
    )
    
    # Component analysis
    avg_financial = np.mean([s['financial_risk_score'] for s in risk_scoring.values()])
    avg_operational = np.mean([s['operational_risk_score'] for s in risk_scoring.values()])
    avg_liquidity = np.mean([s['liquidity_risk_score'] for s in risk_scoring.values()])
    
    summary_parts.append(
        "<br><br><strong>Risk Component Analysis:</strong><br>"
        f"• <strong>Financial Risk:</strong> {avg_financial:.1f}/10 average across revenue, profitability, and leverage dimensions<br>"
        f"• <strong>Operational Risk:</strong> {avg_operational:.1f}/10 average in cash flow, efficiency, and capital allocation<br>"
        f"• <strong>Liquidity Risk:</strong> {avg_liquidity:.1f}/10 average for working capital and cash position management"
    )
    
    # Distribution summary
    summary_parts.append(
        "<br><br><strong>Portfolio Risk Distribution:</strong><br>"
        f"• {rating_counts.get('Low Risk', 0)} companies with strong fundamentals and minimal risk exposure<br>"
        f"• {rating_counts.get('Moderate Risk', 0)} companies requiring standard monitoring protocols<br>"
        f"• {rating_counts.get('High Risk', 0)} companies needing enhanced oversight and risk mitigation<br>"
        f"• {rating_counts.get('Critical Risk', 0)} companies requiring immediate intervention"
    )
    
    # Strategic assessment
    if avg_composite <= 6 and high_risk_count <= total_companies * 0.3:
        strategic = "Sophisticated risk quantification framework providing comprehensive portfolio risk assessment"
    elif avg_composite <= 7:
        strategic = "Enhanced risk management required to optimize portfolio risk exposure"
    else:
        strategic = "Portfolio risk intervention needed to address elevated risk concentrations"
    
    summary_parts.append(f"<br><br><strong>Strategic Risk Intelligence:</strong> {strategic}.")
    
    return build_info_box(
        "".join(summary_parts),
        box_type="info",
        title="Risk Scoring & Portfolio Aggregation Summary"
    )


# =============================================================================
# SUBSECTION 11D: PREDICTIVE RISK MODELING & EARLY WARNING SYSTEM
# =============================================================================

def _build_section_11d_predictive_modeling(df: pd.DataFrame, companies: Dict[str, str], collector) -> str:
    """Build subsection 11D: Predictive Risk Modeling & Early Warning System"""
    
    # Generate risk analysis
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    
    if not risk_analysis:
        return _build_collapsible_subsection(
            "11D",
            "Predictive Risk Modeling & Early Warning System",
            '<div class="info-box warning"><p>Insufficient data for predictive modeling.</p></div>'
        )
    
    # Get economic data if available
    try:
        economic_df = collector.get_economic()
    except:
        economic_df = pd.DataFrame()
    
    # Generate predictive risk models
    predictive_risk = _generate_predictive_risk_models(df, companies, risk_analysis, economic_df)
    
    if not predictive_risk:
        return _build_collapsible_subsection(
            "11D",
            "Predictive Risk Modeling & Early Warning System",
            '<div class="info-box warning"><p>Predictive modeling unavailable.</p></div>'
        )
    
    # Build KPI summary cards
    avg_early_warning = np.mean([pred['early_warning_score'] for pred in predictive_risk.values()])
    avg_confidence = np.mean([pred['confidence_level'] for pred in predictive_risk.values()])
    
    deteriorating_count = sum(1 for pred in predictive_risk.values() if pred['risk_trajectory'] == 'Deteriorating')
    immediate_action = sum(1 for pred in predictive_risk.values() if pred['recommended_action'] == 'Immediate Risk Mitigation')
    
    kpi_cards = build_stat_grid([
        {
            "label": "Early Warning Score",
            "value": f"{avg_early_warning:.1f}/10",
            "description": "Portfolio Average",
            "type": "danger" if avg_early_warning > 7 else "warning" if avg_early_warning > 5 else "success"
        },
        {
            "label": "Prediction Confidence",
            "value": f"{avg_confidence:.0f}%",
            "description": "Model Reliability",
            "type": "success" if avg_confidence >= 75 else "info" if avg_confidence >= 65 else "warning"
        },
        {
            "label": "Deteriorating Trends",
            "value": str(deteriorating_count),
            "description": f"{deteriorating_count/len(companies)*100:.0f}% of Portfolio",
            "type": "danger" if deteriorating_count > len(companies) * 0.3 else "warning"
        },
        {
            "label": "Immediate Actions",
            "value": str(immediate_action),
            "description": "Requiring Intervention",
            "type": "danger" if immediate_action > 0 else "success"
        }
    ])
    
    # Build predictive risk table
    predictive_table_df = _prepare_predictive_risk_table(predictive_risk)
    
    # Color coding
    def color_risk_trajectory(value):
        value_str = str(value).lower()
        if 'deteriorating' in value_str:
            return 'poor'
        elif 'improving' in value_str:
            return 'excellent'
        else:
            return 'good'
    
    def color_predicted_level(value):
        value_str = str(value).lower()
        if 'critical' in value_str:
            return 'poor'
        elif 'high' in value_str:
            return 'fair'
        elif 'moderate' in value_str:
            return 'good'
        else:
            return 'excellent'
    
    color_columns = {
        'Risk Trajectory': color_risk_trajectory,
        'Predicted Level': color_predicted_level
    }
    
    predictive_table_html = build_enhanced_table(
        predictive_table_df,
        table_id="predictive-risk-table",
        color_columns=color_columns,
        badge_columns=['Risk Trajectory', 'Predicted Level'],
        sortable=True,
        searchable=True
    )
    
    # Build trajectory distribution
    trajectory_distribution_html = _build_trajectory_distribution(predictive_risk)
    
    # Build summary narrative
    summary_text = _generate_predictive_risk_summary(predictive_risk, avg_early_warning, 
                                                     avg_confidence, deteriorating_count, 
                                                     immediate_action)
    
    subsection_content = f"""
    <h3>Forward-Looking Risk Assessment & Trend Analysis</h3>
    
    {kpi_cards}
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Predictive Risk Assessment Matrix</h4>
        {predictive_table_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Risk Trajectory Distribution</h4>
        {trajectory_distribution_html}
    </div>
    
    <div class="info-section" style="margin-top: 30px;">
        <h4>Predictive Risk Summary</h4>
        {summary_text}
    </div>
    """
    
    return _build_collapsible_subsection(
        "11D",
        "Predictive Risk Modeling & Early Warning System",
        subsection_content
    )


def _generate_predictive_risk_models(df: pd.DataFrame, companies: Dict[str, str], 
                                    risk_analysis: Dict, economic_df: pd.DataFrame) -> Dict[str, Dict]:
    """Generate predictive risk modeling framework"""
    
    if not risk_analysis:
        return {}
    
    predictive_risk = {}
    
    for company_name in companies.keys():
        if company_name not in risk_analysis:
            continue
        
        company_data = df[df['Company'] == company_name].sort_values('Year')
        risk_data = risk_analysis[company_name]
        
        # Generate predictive risk assessment
        risk_trajectory = _predict_risk_trajectory(company_data, risk_data)
        leading_indicators = _identify_leading_indicators(company_data, economic_df)
        early_warning_score = _calculate_early_warning_score(risk_data, risk_trajectory, leading_indicators)
        predicted_risk_level = _predict_future_risk_level(early_warning_score, risk_trajectory)
        
        # Time horizon and confidence assessment
        time_horizon = _assess_prediction_time_horizon(company_data)
        confidence_level = _calculate_prediction_confidence(len(company_data))
        
        # Recommended actions
        recommended_action = _determine_recommended_action(predicted_risk_level, early_warning_score, risk_trajectory)
        
        predictive_risk[company_name] = {
            'risk_trajectory': risk_trajectory,
            'leading_indicators': leading_indicators,
            'early_warning_score': early_warning_score,
            'predicted_risk_level': predicted_risk_level,
            'time_horizon': time_horizon,
            'confidence_level': confidence_level,
            'recommended_action': recommended_action
        }
    
    return predictive_risk


def _predict_risk_trajectory(company_data: pd.DataFrame, risk_data: Dict) -> str:
    """Predict risk trajectory direction"""
    
    overall_score = risk_data.get('overall_risk_score', 5)
    
    # Analyze trend components
    financial_risks = risk_data.get('financial_risks', {})
    operational_risks = risk_data.get('operational_risks', {})
    trend_risks = risk_data.get('trend_risks', {})
    
    # Calculate trajectory indicators
    leverage_trend = financial_risks.get('leverage_trend', 0)
    revenue_trend_risk = trend_risks.get('revenue_trend_risk', 0)
    profitability_trend_risk = trend_risks.get('profitability_trend_risk', 0)
    efficiency_deterioration = operational_risks.get('efficiency_deterioration', 0)
    
    trajectory_score = (
        leverage_trend * 5 +
        revenue_trend_risk * 3 +
        profitability_trend_risk * 3 +
        efficiency_deterioration * 4
    )
    
    if trajectory_score > 3 or overall_score > 7:
        return "Deteriorating"
    elif trajectory_score < -2 and overall_score < 4:
        return "Improving"
    else:
        return "Stable"


def _identify_leading_indicators(company_data: pd.DataFrame, economic_df: pd.DataFrame) -> str:
    """Identify key leading risk indicators"""
    
    indicators = []
    
    # Revenue growth leading indicator
    if 'revenue_YoY' in company_data.columns:
        recent_growth = company_data['revenue_YoY'].tail(2).mean()
        if recent_growth < 0:
            indicators.append("Revenue Decline")
        elif recent_growth < 5:
            indicators.append("Slow Growth")
    
    # Margin pressure indicators
    if 'grossProfitMargin' in company_data.columns:
        gross_margin = company_data['grossProfitMargin'].fillna(0)
        if len(gross_margin) > 1 and gross_margin.iloc[-1] < gross_margin.iloc[-2]:
            indicators.append("Margin Pressure")
    
    # Cash flow indicators
    if 'freeCashFlow' in company_data.columns:
        fcf = company_data['freeCashFlow'].fillna(0)
        if len(fcf) > 0 and fcf.iloc[-1] < 0:
            indicators.append("Negative FCF")
    
    # Leverage indicators
    if 'debtToEquityRatio' in company_data.columns:
        debt_equity = company_data['debtToEquityRatio'].fillna(0)
        if len(debt_equity) > 1 and debt_equity.iloc[-1] > debt_equity.iloc[-2]:
            indicators.append("Rising Leverage")
    
    return ", ".join(indicators[:4]) if indicators else "Standard Metrics"


def _calculate_early_warning_score(risk_data: Dict, risk_trajectory: str, leading_indicators: str) -> float:
    """Calculate early warning composite score"""
    
    overall_score = risk_data.get('overall_risk_score', 5)
    
    # Trajectory adjustment
    trajectory_adjustment = 0
    if risk_trajectory == "Deteriorating":
        trajectory_adjustment = 2
    elif risk_trajectory == "Improving":
        trajectory_adjustment = -1.5
    
    # Leading indicators adjustment
    indicator_adjustment = 0
    critical_indicators = ["Revenue Decline", "Negative FCF", "Margin Pressure", "Rising Leverage"]
    for indicator in critical_indicators:
        if indicator in leading_indicators:
            indicator_adjustment += 1
    
    early_warning_score = overall_score + trajectory_adjustment + indicator_adjustment
    
    return min(10, max(0, early_warning_score))


def _predict_future_risk_level(early_warning_score: float, risk_trajectory: str) -> str:
    """Predict future risk level classification"""
    
    if early_warning_score >= 8.5:
        return "Critical Risk"
    elif early_warning_score >= 7:
        return "High Risk"
    elif early_warning_score >= 5:
        return "Moderate Risk"
    elif early_warning_score >= 3:
        return "Low-Moderate Risk"
    else:
        return "Low Risk"


def _assess_prediction_time_horizon(company_data: pd.DataFrame) -> str:
    """Assess prediction time horizon reliability"""
    
    data_years = len(company_data)
    
    if data_years >= 8:
        return "12-18 months"
    elif data_years >= 5:
        return "6-12 months"
    else:
        return "3-6 months"


def _calculate_prediction_confidence(data_points: int) -> float:
    """Calculate prediction confidence level"""
    
    base_confidence = min(80, 40 + data_points * 4)
    return min(95, max(50, base_confidence))


def _determine_recommended_action(predicted_risk_level: str, early_warning_score: float, 
                                 risk_trajectory: str) -> str:
    """Determine recommended risk management action"""
    
    if predicted_risk_level == "Critical Risk" or early_warning_score >= 8:
        return "Immediate Risk Mitigation"
    elif predicted_risk_level == "High Risk" or risk_trajectory == "Deteriorating":
        return "Enhanced Monitoring & Controls"
    elif predicted_risk_level == "Moderate Risk":
        return "Proactive Risk Management"
    else:
        return "Standard Risk Monitoring"


def _prepare_predictive_risk_table(predictive_risk: Dict[str, Dict]) -> pd.DataFrame:
    """Prepare predictive risk table DataFrame"""
    
    table_data = []
    
    for company_name, pred in predictive_risk.items():
        table_data.append({
            'Company': company_name,
            'Risk Trajectory': pred['risk_trajectory'],
            'Leading Indicators': pred['leading_indicators'][:30] + '...' if len(pred['leading_indicators']) > 30 else pred['leading_indicators'],
            'Early Warning': f"{pred['early_warning_score']:.1f}/10",
            'Predicted Level': pred['predicted_risk_level'],
            'Time Horizon': pred['time_horizon'],
            'Confidence': f"{pred['confidence_level']:.0f}%",
            'Action': pred['recommended_action'][:25] + '...' if len(pred['recommended_action']) > 25 else pred['recommended_action']
        })
    
    return pd.DataFrame(table_data)


def _build_trajectory_distribution(predictive_risk: Dict[str, Dict]) -> str:
    """Build trajectory distribution visualization"""
    
    # Count trajectories
    trajectory_counts = {}
    for pred in predictive_risk.values():
        trajectory = pred['risk_trajectory']
        trajectory_counts[trajectory] = trajectory_counts.get(trajectory, 0) + 1
    
    # Build visual bars
    total = len(predictive_risk)
    bars_html = ""
    
    trajectory_order = ['Improving', 'Stable', 'Deteriorating']
    trajectory_colors = {
        'Improving': '#10b981',
        'Stable': '#3b82f6',
        'Deteriorating': '#ef4444'
    }
    
    for trajectory in trajectory_order:
        count = trajectory_counts.get(trajectory, 0)
        percentage = (count / total * 100) if total > 0 else 0
        color = trajectory_colors.get(trajectory, '#667eea')
        
        bars_html += f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600;">{trajectory}</span>
                <span style="font-weight: 700; color: {color};">{count} companies ({percentage:.0f}%)</span>
            </div>
            <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 8px; height: 24px;">
                <div style="width: {percentage}%; background: {color}; border-radius: 8px; height: 100%; 
                           transition: width 0.6s ease;"></div>
            </div>
        </div>
        """
    
    return bars_html


def _generate_predictive_risk_summary(predictive_risk: Dict, avg_early_warning: float,
                                     avg_confidence: float, deteriorating_count: int,
                                     immediate_action: int) -> str:
    """Generate predictive risk summary"""
    
    total_companies = len(predictive_risk)
    improving_count = sum(1 for pred in predictive_risk.values() if pred['risk_trajectory'] == 'Improving')
    
    # Risk level predictions
    risk_predictions = {}
    for pred in predictive_risk.values():
        level = pred['predicted_risk_level']
        risk_predictions[level] = risk_predictions.get(level, 0) + 1
    
    summary_parts = []
    
    # Predictive performance
    if avg_confidence >= 75 and total_companies >= 3:
        predictive_capability = "demonstrates high-confidence forecasting capability"
    elif avg_confidence >= 65:
        predictive_capability = "shows moderate predictive reliability"
    else:
        predictive_capability = "is developing predictive framework capability"
    
    summary_parts.append(
        f"The predictive risk modeling framework {predictive_capability}, with an average early warning "
        f"score of {avg_early_warning:.1f}/10 and {avg_confidence:.0f}% prediction confidence. "
        f"{deteriorating_count} companies exhibit deteriorating risk trajectories, while {improving_count} show "
        f"improving trends. {immediate_action} companies require immediate risk mitigation based on predictive analysis."
    )
    
    # Forward-looking intelligence
    summary_parts.append(
        "<br><br><strong>Forward-Looking Risk Intelligence:</strong><br>"
        f"• <strong>Risk Trajectory Analysis:</strong> "
        f"{'Stable risk trajectories' if deteriorating_count <= total_companies * 0.3 else 'Mixed patterns requiring attention'} "
        f"across portfolio companies<br>"
        f"• <strong>Leading Indicator Detection:</strong> Comprehensive identification of risk drivers including revenue trends, "
        f"margin pressure, cash flow patterns, and leverage dynamics<br>"
        f"• <strong>Early Warning System:</strong> "
        f"{'Sophisticated preventive capability' if avg_early_warning <= 6 and immediate_action <= total_companies * 0.2 else 'Enhanced intervention framework needed'} "
        f"for proactive risk prevention"
    )
    
    # Predicted risk distribution
    summary_parts.append(
        "<br><br><strong>Predicted Risk Distribution:</strong><br>"
        f"• {risk_predictions.get('Low Risk', 0)} companies projected to maintain low-risk profiles<br>"
        f"• {risk_predictions.get('Moderate Risk', 0)} companies expected to require standard monitoring<br>"
        f"• {risk_predictions.get('High Risk', 0)} companies predicted to need enhanced oversight<br>"
        f"• {risk_predictions.get('Critical Risk', 0)} companies forecasted to require critical intervention"
    )
    
    # Strategic predictive intelligence
    if avg_confidence >= 70 and deteriorating_count <= total_companies * 0.3:
        strategic = "Advanced risk forecasting capability enabling proactive portfolio risk management"
    elif avg_confidence >= 60:
        strategic = "Developing predictive risk management with improving forecasting reliability"
    else:
        strategic = "Enhanced predictive modeling needed for comprehensive forward-looking risk assessment"
    
    summary_parts.append(f"<br><br><strong>Strategic Predictive Framework:</strong> {strategic}.")
    
    return build_info_box(
        "".join(summary_parts),
        box_type="info",
        title="Predictive Risk Modeling Summary"
    )


def _build_section_11e_visualizations(df: pd.DataFrame, companies: Dict[str, str], analysis_id) -> str:
    """Build subsection 11E: Risk & Alert Visualization Dashboard"""
    
    # Generate all required data
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    alert_system = _generate_automated_alerts(df, companies, risk_analysis)
    risk_scoring = _generate_risk_scoring_system(risk_analysis, alert_system, companies)
    
    # Get economic data if available
    try:
        from backend.app.report_generation.section_runner import get_collector_for_analysis
        collector = get_collector_for_analysis(analysis_id)
        economic_df = collector.get_economic()
    except:
        economic_df = pd.DataFrame()
    
    predictive_risk = _generate_predictive_risk_models(df, companies, risk_analysis, economic_df)
    
    if not risk_analysis or not alert_system or not risk_scoring or not predictive_risk:
        return _build_collapsible_subsection(
            "11E",
            "Risk & Alert Visualization Dashboard",
            '<div class="info-box warning"><p>Insufficient data for visualization dashboard.</p></div>'
        )
    
    # Build all 6 charts
    chart1_html = _create_risk_metrics_heatmap(risk_analysis, companies)
    chart2_html = _create_alert_system_dashboard(alert_system, companies)
    chart3_html = _create_risk_scoring_distribution(risk_scoring)
    chart4_html = _create_predictive_risk_models_chart(predictive_risk)
    chart5_html = _create_risk_correlation_matrix(risk_analysis, companies)
    chart6_html = _create_comprehensive_risk_dashboard(risk_analysis, alert_system, risk_scoring, predictive_risk)
    
    subsection_content = f"""
    <h3>Comprehensive Risk & Alert Visualization Suite</h3>
    
    <p style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 30px;">
        Interactive dashboards providing multi-dimensional risk assessment, alert classification, 
        predictive modeling insights, and portfolio-wide risk intelligence through advanced visualizations.
    </p>
    
    <div class="info-section">
        <h4>Chart 1: Risk Metrics Heat Map</h4>
        <p style="color: var(--text-secondary);">Multi-dimensional risk assessment across all monitored financial and operational metrics</p>
        {chart1_html}
    </div>
    
    <div class="info-section">
        <h4>Chart 2: Alert System Dashboard</h4>
        <p style="color: var(--text-secondary);">Real-time alert classification by severity with frequency patterns and priority distribution</p>
        {chart2_html}
    </div>
    
    <div class="info-section">
        <h4>Chart 3: Risk Scoring Distribution</h4>
        <p style="color: var(--text-secondary);">Portfolio-wide risk score distribution with composite ratings and component analysis</p>
        {chart3_html}
    </div>
    
    <div class="info-section">
        <h4>Chart 4: Predictive Risk Models</h4>
        <p style="color: var(--text-secondary);">Forward-looking risk trajectory analysis with early warning indicators and confidence metrics</p>
        {chart4_html}
    </div>
    
    <div class="info-section">
        <h4>Chart 5: Risk Correlation Matrix</h4>
        <p style="color: var(--text-secondary);">Inter-metric risk correlation analysis for comprehensive portfolio risk understanding</p>
        {chart5_html}
    </div>
    
    <div class="info-section">
        <h4>Chart 6: Comprehensive Risk Management Dashboard</h4>
        <p style="color: var(--text-secondary);">Executive-level risk overview integrating all risk dimensions with strategic insights</p>
        {chart6_html}
    </div>
    """
    
    return _build_collapsible_subsection(
        "11E",
        "Risk & Alert Visualization Dashboard",
        subsection_content
    )


def _create_risk_metrics_heatmap(risk_analysis: Dict, companies: Dict[str, str]) -> str:
    """Create risk metrics heatmap chart"""
    
    company_names = list(risk_analysis.keys())
    risk_categories = ['Financial Risk', 'Operational Risk', 'Liquidity Risk', 'Market Risk', 'Overall Risk']
    
    # Prepare data
    heatmap_data = []
    for company in company_names:
        risk_data = risk_analysis[company]
        row = [
            _calculate_financial_risk_score(risk_data.get('financial_risks', {})),
            _calculate_operational_risk_score(risk_data.get('operational_risks', {})),
            _calculate_liquidity_risk_score(risk_data.get('liquidity_risks', {})),
            _calculate_market_risk_score(risk_data.get('market_risks', {})),
            risk_data.get('overall_risk_score', 5)
        ]
        heatmap_data.append(row)
    
    # Transpose for proper orientation
    heatmap_array = np.array(heatmap_data).T.tolist()
    
    # Create heatmap
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': heatmap_array,
            'x': [comp[:15] for comp in company_names],
            'y': risk_categories,
            'colorscale': [
                [0, '#10b981'],      # Green (low risk)
                [0.3, '#3b82f6'],    # Blue
                [0.5, '#f59e0b'],    # Orange
                [0.7, '#ef4444'],    # Red
                [1, '#dc2626']       # Dark red (high risk)
            ],
            'zmin': 0,
            'zmax': 10,
            'colorbar': {
                'title': 'Risk Score',
                'titleside': 'right'
            },
            'hovertemplate': '<b>%{y}</b><br>%{x}<br>Score: %{z:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Risk Metrics Heat Map',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Risk Dimensions'},
            'height': 500
        }
    }
    
    return build_plotly_chart(fig_data, div_id="risk-heatmap", height=500)


def _create_alert_system_dashboard(alert_system: Dict, companies: Dict[str, str]) -> str:
    """Create alert system dashboard with multiple charts"""
    
    company_names = list(alert_system.keys())
    
    # Prepare alert data
    critical_alerts = [alert_system[comp]['alert_summary']['critical_count'] for comp in company_names]
    warning_alerts = [alert_system[comp]['alert_summary']['warning_count'] for comp in company_names]
    monitoring_alerts = [alert_system[comp]['alert_summary']['monitoring_count'] for comp in company_names]
    priority_scores = [alert_system[comp]['alert_summary']['priority_score'] for comp in company_names]
    
    # Chart 1: Stacked bar chart of alerts by company
    fig_data = {
        'data': [
            {
                'type': 'bar',
                'name': 'Critical',
                'x': [comp[:12] for comp in company_names],
                'y': critical_alerts,
                'marker': {'color': '#ef4444'},
                'hovertemplate': '<b>%{x}</b><br>Critical: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Warning',
                'x': [comp[:12] for comp in company_names],
                'y': warning_alerts,
                'marker': {'color': '#f59e0b'},
                'hovertemplate': '<b>%{x}</b><br>Warning: %{y}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Monitoring',
                'x': [comp[:12] for comp in company_names],
                'y': monitoring_alerts,
                'marker': {'color': '#3b82f6'},
                'hovertemplate': '<b>%{x}</b><br>Monitoring: %{y}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Alert Distribution by Company & Severity',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Alert Count'},
            'barmode': 'stack',
            'height': 500,
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        }
    }
    
    alert_chart_html = build_plotly_chart(fig_data, div_id="alert-distribution", height=500)
    
    # Chart 2: Priority scores
    priority_fig = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in company_names],
            'y': priority_scores,
            'marker': {
                'color': priority_scores,
                'colorscale': [
                    [0, '#10b981'],
                    [0.5, '#f59e0b'],
                    [1, '#ef4444']
                ],
                'cmin': 0,
                'cmax': 100,
                'colorbar': {'title': 'Priority'}
            },
            'hovertemplate': '<b>%{x}</b><br>Priority: %{y:.0f}/100<extra></extra>'
        }],
        'layout': {
            'title': 'Alert Priority Score by Company',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Priority Score (0-100)'},
            'height': 400
        }
    }
    
    priority_chart_html = build_plotly_chart(priority_fig, div_id="alert-priority", height=400)
    
    return f"""
    {alert_chart_html}
    <div style="margin-top: 20px;"></div>
    {priority_chart_html}
    """


def _create_risk_scoring_distribution(risk_scoring: Dict) -> str:
    """Create risk scoring distribution charts"""
    
    company_names = list(risk_scoring.keys())
    
    # Composite scores
    composite_scores = [risk_scoring[comp]['composite_risk_score'] for comp in company_names]
    
    # Chart 1: Composite risk scores with thresholds
    composite_fig = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in company_names],
            'y': composite_scores,
            'marker': {
                'color': ['#10b981' if s <= 3 else '#3b82f6' if s <= 5 else '#f59e0b' if s <= 7 else '#ef4444' 
                         for s in composite_scores]
            },
            'hovertemplate': '<b>%{x}</b><br>Risk Score: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': 'Composite Risk Score Distribution',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Composite Risk Score (0-10)'},
            'height': 500,
            'shapes': [
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(company_names) - 0.5,
                    'y0': 3,
                    'y1': 3,
                    'line': {'color': '#10b981', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(company_names) - 0.5,
                    'y0': 5,
                    'y1': 5,
                    'line': {'color': '#f59e0b', 'width': 2, 'dash': 'dash'}
                },
                {
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(company_names) - 0.5,
                    'y0': 7,
                    'y1': 7,
                    'line': {'color': '#ef4444', 'width': 2, 'dash': 'dash'}
                }
            ],
            'annotations': [
                {'x': len(company_names) - 0.7, 'y': 3.2, 'text': 'Low Risk', 'showarrow': False, 'font': {'size': 10, 'color': '#10b981'}},
                {'x': len(company_names) - 0.7, 'y': 5.2, 'text': 'Moderate Risk', 'showarrow': False, 'font': {'size': 10, 'color': '#f59e0b'}},
                {'x': len(company_names) - 0.7, 'y': 7.2, 'text': 'High Risk', 'showarrow': False, 'font': {'size': 10, 'color': '#ef4444'}}
            ]
        }
    }
    
    composite_chart_html = build_plotly_chart(composite_fig, div_id="composite-scores", height=500)
    
    # Chart 2: Component breakdown (grouped bars)
    financial_scores = [risk_scoring[comp]['financial_risk_score'] for comp in company_names]
    operational_scores = [risk_scoring[comp]['operational_risk_score'] for comp in company_names]
    liquidity_scores = [risk_scoring[comp]['liquidity_risk_score'] for comp in company_names]
    market_scores = [risk_scoring[comp]['market_risk_score'] for comp in company_names]
    
    component_fig = {
        'data': [
            {
                'type': 'bar',
                'name': 'Financial',
                'x': [comp[:12] for comp in company_names],
                'y': financial_scores,
                'marker': {'color': '#667eea'},
                'hovertemplate': '<b>%{x}</b><br>Financial: %{y:.1f}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Operational',
                'x': [comp[:12] for comp in company_names],
                'y': operational_scores,
                'marker': {'color': '#764ba2'},
                'hovertemplate': '<b>%{x}</b><br>Operational: %{y:.1f}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Liquidity',
                'x': [comp[:12] for comp in company_names],
                'y': liquidity_scores,
                'marker': {'color': '#f093fb'},
                'hovertemplate': '<b>%{x}</b><br>Liquidity: %{y:.1f}<extra></extra>'
            },
            {
                'type': 'bar',
                'name': 'Market',
                'x': [comp[:12] for comp in company_names],
                'y': market_scores,
                'marker': {'color': '#10b981'},
                'hovertemplate': '<b>%{x}</b><br>Market: %{y:.1f}<extra></extra>'
            }
        ],
        'layout': {
            'title': 'Risk Component Score Breakdown',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Risk Score (0-10)'},
            'barmode': 'group',
            'height': 450,
            'showlegend': True,
            'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
        }
    }
    
    component_chart_html = build_plotly_chart(component_fig, div_id="component-scores", height=450)
    
    return f"""
    {composite_chart_html}
    <div style="margin-top: 20px;"></div>
    {component_chart_html}
    """


def _create_predictive_risk_models_chart(predictive_risk: Dict) -> str:
    """Create predictive risk models visualization"""
    
    company_names = list(predictive_risk.keys())
    
    # Early warning scores
    early_warning_scores = [predictive_risk[comp]['early_warning_score'] for comp in company_names]
    confidence_levels = [predictive_risk[comp]['confidence_level'] for comp in company_names]
    
    # Color by trajectory
    trajectory_colors = []
    for comp in company_names:
        trajectory = predictive_risk[comp]['risk_trajectory']
        if trajectory == 'Deteriorating':
            trajectory_colors.append('#ef4444')
        elif trajectory == 'Improving':
            trajectory_colors.append('#10b981')
        else:
            trajectory_colors.append('#3b82f6')
    
    # Chart 1: Early warning scores
    warning_fig = {
        'data': [{
            'type': 'bar',
            'x': [comp[:12] for comp in company_names],
            'y': early_warning_scores,
            'marker': {'color': trajectory_colors},
            'text': [f"{conf:.0f}%" for conf in confidence_levels],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Early Warning: %{y:.1f}/10<br>Confidence: %{text}<extra></extra>'
        }],
        'layout': {
            'title': 'Predictive Early Warning Scores (Colored by Trajectory)',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Early Warning Score (0-10)'},
            'height': 500,
            'annotations': [
                {'x': 0.02, 'y': 0.98, 'xref': 'paper', 'yref': 'paper', 
                 'text': '🔴 Deteriorating  🔵 Stable  🟢 Improving', 
                 'showarrow': False, 'font': {'size': 11}, 'align': 'left'}
            ]
        }
    }
    
    warning_chart_html = build_plotly_chart(warning_fig, div_id="early-warning", height=500)
    
    # Chart 2: Confidence vs Early Warning scatter
    scatter_fig = {
        'data': [{
            'type': 'scatter',
            'mode': 'markers+text',
            'x': confidence_levels,
            'y': early_warning_scores,
            'marker': {
                'size': 15,
                'color': trajectory_colors,
                'line': {'width': 2, 'color': 'white'}
            },
            'text': [comp[:8] for comp in company_names],
            'textposition': 'top center',
            'textfont': {'size': 9},
            'hovertemplate': '<b>%{text}</b><br>Confidence: %{x:.0f}%<br>Warning Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': 'Prediction Confidence vs Early Warning Score',
            'xaxis': {'title': 'Prediction Confidence (%)', 'range': [45, 100]},
            'yaxis': {'title': 'Early Warning Score (0-10)', 'range': [-0.5, 10.5]},
            'height': 450
        }
    }
    
    scatter_chart_html = build_plotly_chart(scatter_fig, div_id="confidence-scatter", height=450)
    
    return f"""
    {warning_chart_html}
    <div style="margin-top: 20px;"></div>
    {scatter_chart_html}
    """


def _create_risk_correlation_matrix(risk_analysis: Dict, companies: Dict[str, str]) -> str:
    """Create risk correlation matrix heatmap"""
    
    if len(risk_analysis) < 2:
        return '<div class="info-box warning"><p>Insufficient companies for correlation analysis.</p></div>'
    
    company_names = list(risk_analysis.keys())
    
    # Prepare risk scores data
    risk_scores = []
    for company in company_names:
        scores = [
            risk_analysis[company].get('overall_risk_score', 5),
            _calculate_financial_risk_score(risk_analysis[company].get('financial_risks', {})),
            _calculate_operational_risk_score(risk_analysis[company].get('operational_risks', {})),
            _calculate_liquidity_risk_score(risk_analysis[company].get('liquidity_risks', {})),
            _calculate_market_risk_score(risk_analysis[company].get('market_risks', {}))
        ]
        risk_scores.append(scores)
    
    # Calculate correlation matrix
    risk_array = np.array(risk_scores)
    correlation_matrix = np.corrcoef(risk_array.T)
    
    labels = ['Overall', 'Financial', 'Operational', 'Liquidity', 'Market']
    
    # Create correlation heatmap
    fig_data = {
        'data': [{
            'type': 'heatmap',
            'z': correlation_matrix.tolist(),
            'x': labels,
            'y': labels,
            'colorscale': 'RdBu',
            'zmid': 0,
            'zmin': -1,
            'zmax': 1,
            'colorbar': {
                'title': 'Correlation',
                'titleside': 'right'
            },
            'text': [[f'{val:.2f}' for val in row] for row in correlation_matrix],
            'texttemplate': '%{text}',
            'textfont': {'size': 12},
            'hovertemplate': '<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
        }],
        'layout': {
            'title': 'Risk Metrics Correlation Matrix',
            'xaxis': {'title': ''},
            'yaxis': {'title': ''},
            'height': 500,
            'width': 550
        }
    }
    
    return build_plotly_chart(fig_data, div_id="correlation-matrix", height=500)


def _create_comprehensive_risk_dashboard(risk_analysis: Dict, alert_system: Dict,
                                        risk_scoring: Dict, predictive_risk: Dict) -> str:
    """Create comprehensive executive risk dashboard"""
    
    company_names = list(risk_scoring.keys())
    
    # Calculate portfolio-level metrics
    avg_composite = np.mean([risk_scoring[comp]['composite_risk_score'] for comp in company_names])
    avg_financial = np.mean([risk_scoring[comp]['financial_risk_score'] for comp in company_names])
    avg_operational = np.mean([risk_scoring[comp]['operational_risk_score'] for comp in company_names])
    avg_liquidity = np.mean([risk_scoring[comp]['liquidity_risk_score'] for comp in company_names])
    avg_alert = np.mean([alert_system[comp]['alert_summary']['total_alerts'] for comp in company_names])
    
    # Chart 1: Portfolio risk summary (bar chart)
    summary_fig = {
        'data': [{
            'type': 'bar',
            'x': ['Composite<br>Risk', 'Financial<br>Risk', 'Operational<br>Risk', 'Liquidity<br>Risk', 'Alert<br>Activity'],
            'y': [avg_composite, avg_financial, avg_operational, avg_liquidity, avg_alert],
            'marker': {
                'color': ['#ef4444', '#667eea', '#764ba2', '#f093fb', '#f59e0b']
            },
            'text': [f'{val:.1f}' for val in [avg_composite, avg_financial, avg_operational, avg_liquidity, avg_alert]],
            'textposition': 'outside',
            'hovertemplate': '<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Risk Management Dashboard - Key Metrics',
            'yaxis': {'title': 'Risk Score / Alert Count'},
            'height': 400,
            'showlegend': False
        }
    }
    
    summary_chart_html = build_plotly_chart(summary_fig, div_id="portfolio-summary", height=400)
    
    # Chart 2: Company risk profile radar/spider chart
    composite_scores = [risk_scoring[comp]['composite_risk_score'] for comp in company_names]
    
    # Create multi-line chart showing risk trends
    trend_fig = {
        'data': [{
            'type': 'bar',
            'x': [comp[:10] for comp in company_names],
            'y': composite_scores,
            'marker': {
                'color': ['#10b981' if s <= 3 else '#3b82f6' if s <= 5 else '#f59e0b' if s <= 7 else '#ef4444' 
                         for s in composite_scores]
            },
            'hovertemplate': '<b>%{x}</b><br>Risk: %{y:.1f}/10<extra></extra>'
        }],
        'layout': {
            'title': 'Portfolio Composite Risk Distribution with Threshold Zones',
            'xaxis': {'title': 'Companies', 'tickangle': -45},
            'yaxis': {'title': 'Composite Risk Score (0-10)'},
            'height': 400,
            'shapes': [
                {'type': 'rect', 'x0': -0.5, 'x1': len(company_names)-0.5, 'y0': 0, 'y1': 3,
                 'fillcolor': '#10b981', 'opacity': 0.1, 'line': {'width': 0}},
                {'type': 'rect', 'x0': -0.5, 'x1': len(company_names)-0.5, 'y0': 3, 'y1': 5,
                 'fillcolor': '#3b82f6', 'opacity': 0.1, 'line': {'width': 0}},
                {'type': 'rect', 'x0': -0.5, 'x1': len(company_names)-0.5, 'y0': 5, 'y1': 7,
                 'fillcolor': '#f59e0b', 'opacity': 0.1, 'line': {'width': 0}},
                {'type': 'rect', 'x0': -0.5, 'x1': len(company_names)-0.5, 'y0': 7, 'y1': 10,
                 'fillcolor': '#ef4444', 'opacity': 0.1, 'line': {'width': 0}}
            ]
        }
    }
    
    trend_chart_html = build_plotly_chart(trend_fig, div_id="risk-distribution", height=400)
    
    # Chart 3: Alert severity distribution (pie chart)
    total_critical = sum(alert_system[comp]['alert_summary']['critical_count'] for comp in company_names)
    total_warning = sum(alert_system[comp]['alert_summary']['warning_count'] for comp in company_names)
    total_monitoring = sum(alert_system[comp]['alert_summary']['monitoring_count'] for comp in company_names)
    
    if total_critical + total_warning + total_monitoring > 0:
        alert_pie_fig = {
            'data': [{
                'type': 'pie',
                'labels': ['Critical', 'Warning', 'Monitoring'],
                'values': [total_critical, total_warning, total_monitoring],
                'marker': {
                    'colors': ['#ef4444', '#f59e0b', '#3b82f6']
                },
                'hovertemplate': '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
            }],
            'layout': {
                'title': 'Portfolio Alert Severity Distribution',
                'height': 350,
                'showlegend': True
            }
        }
        
        alert_pie_html = build_plotly_chart(alert_pie_fig, div_id="alert-severity-pie", height=350)
    else:
        alert_pie_html = '<div class="info-box success"><p>No alerts detected across portfolio.</p></div>'
    
    return f"""
    {summary_chart_html}
    <div style="margin-top: 20px;"></div>
    {trend_chart_html}
    <div style="margin-top: 20px;"></div>
    {alert_pie_html}
    """


"""
Section 11 - Step 4: Strategic Risk Management Framework (Subsection 11F)
This file contains ONLY the 11F subsection implementation.
Replace the stub function _build_section_11f_strategic_framework in your main file.
"""

from typing import Dict
import pandas as pd
import numpy as np
from backend.app.report_generation.html_utils import (
    build_info_box,
    build_stat_grid,
    build_badge,
    build_summary_card,
    build_progress_indicator
)


def _build_section_11f_strategic_framework(df: pd.DataFrame, companies: Dict[str, str], 
                                          analysis_id: str) -> str:
    """Build subsection 11F: Strategic Risk Management Framework & Action Plan"""
    
    # Generate all required data
    risk_analysis = _generate_comprehensive_risk_analysis(df, companies)
    alert_system = _generate_automated_alerts(df, companies, risk_analysis)
    risk_scoring = _generate_risk_scoring_system(risk_analysis, alert_system, companies)
    
    # Get economic data if available
    try:
        from backend.app.report_generation.section_runner import get_collector_for_analysis
        collector = get_collector_for_analysis(analysis_id)
        economic_df = collector.get_economic()
    except:
        economic_df = pd.DataFrame()
    
    predictive_risk = _generate_predictive_risk_models(df, companies, risk_analysis, economic_df)
    
    if not risk_analysis or not alert_system or not risk_scoring or not predictive_risk:
        return _build_collapsible_subsection(
            "11F",
            "Strategic Risk Management Framework & Action Plan",
            '<div class="info-box warning"><p>Insufficient data for strategic framework.</p></div>'
        )
    
    # Generate comprehensive strategic insights
    strategic_insights = _generate_comprehensive_risk_management_insights(
        risk_analysis, alert_system, risk_scoring, predictive_risk, 
        companies, economic_df
    )
    
    # Build enhanced presentation with multiple formats
    subsection_content = f"""
    <h3>Comprehensive Risk Strategy & Portfolio Optimization</h3>
    
    <p style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 30px;">
        Strategic risk intelligence framework integrating multi-dimensional risk assessment, 
        alert optimization, predictive modeling, and portfolio-level recommendations for 
        comprehensive risk management and value protection.
    </p>
    
    {_build_risk_intelligence_section(strategic_insights['risk_intelligence'], risk_analysis, risk_scoring)}
    
    {_build_alert_optimization_section(strategic_insights['alert_optimization'], alert_system)}
    
    {_build_predictive_management_section(strategic_insights['predictive_management'], predictive_risk)}
    
    {_build_portfolio_optimization_section(strategic_insights['portfolio_optimization'], risk_scoring)}
    
    {_build_implementation_roadmap_section(strategic_insights['implementation_strategy'], 
                                          risk_analysis, alert_system, risk_scoring, predictive_risk)}
    """
    
    return _build_collapsible_subsection(
        "11F",
        "Strategic Risk Management Framework & Action Plan",
        subsection_content
    )


def _generate_comprehensive_risk_management_insights(risk_analysis: Dict, alert_system: Dict,
                                                    risk_scoring: Dict, predictive_risk: Dict,
                                                    companies: Dict, economic_df: pd.DataFrame) -> Dict[str, str]:
    """Generate comprehensive risk management strategic insights"""
    
    total_companies = len(companies)
    
    # Calculate key metrics
    if risk_scoring:
        avg_composite_score = np.mean([scoring['composite_risk_score'] for scoring in risk_scoring.values()])
        high_risk_companies = sum(1 for scoring in risk_scoring.values() 
                                 if scoring['risk_rating'] in ['High Risk', 'Critical Risk', 'Extreme Risk'])
        deteriorating_companies = sum(1 for scoring in risk_scoring.values() 
                                     if 'Deteriorating' in scoring['risk_trend'])
    else:
        avg_composite_score = 5
        high_risk_companies = 0
        deteriorating_companies = 0
    
    if alert_system:
        total_critical_alerts = sum(alerts['alert_summary']['critical_count'] for alerts in alert_system.values())
        total_alerts = sum(alerts['alert_summary']['total_alerts'] for alerts in alert_system.values())
        companies_with_critical = sum(1 for alerts in alert_system.values() if alerts['alert_summary']['critical_count'] > 0)
    else:
        total_critical_alerts = 0
        total_alerts = 0
        companies_with_critical = 0
    
    if predictive_risk:
        avg_early_warning = np.mean([pred['early_warning_score'] for pred in predictive_risk.values()])
        immediate_action_needed = sum(1 for pred in predictive_risk.values() 
                                     if pred['recommended_action'] == 'Immediate Risk Mitigation')
        avg_prediction_confidence = np.mean([pred['confidence_level'] for pred in predictive_risk.values()])
    else:
        avg_early_warning = 5
        immediate_action_needed = 0
        avg_prediction_confidence = 60
    
    # Risk Intelligence
    risk_intelligence = f"""Portfolio demonstrates {'strong risk management' if avg_composite_score <= 4 and high_risk_companies <= total_companies * 0.2 else 'moderate risk exposure' if avg_composite_score <= 6 else 'elevated risk levels requiring attention'} with average composite risk score of {avg_composite_score:.1f}/10 across {total_companies} companies. {high_risk_companies} companies require enhanced oversight, while {deteriorating_companies} show deteriorating trends. Detection coverage spans {total_alerts} alerts with {total_critical_alerts} critical-severity warnings across financial, operational, and liquidity dimensions."""
    
    # Alert Optimization
    alert_optimization = f"""Alert system performance {'excellent with comprehensive early warning' if total_critical_alerts == 0 else 'effective with managed alert volume' if total_critical_alerts <= total_companies * 0.5 else 'requires optimization'} across {total_companies} companies. {companies_with_critical} companies trigger critical alerts requiring immediate intervention protocols. Multi-tiered severity classification enables {'sophisticated' if total_alerts >= total_companies * 2 and total_critical_alerts <= total_companies * 0.3 else 'developing'} early warning capabilities."""
    
    # Predictive Management
    predictive_management = f"""Predictive framework achieves {avg_early_warning:.1f}/10 average early warning score with {avg_prediction_confidence:.0f}% confidence. {immediate_action_needed} companies require immediate risk mitigation based on forward-looking analysis. {'High-confidence forecasting' if avg_prediction_confidence >= 75 else 'Moderate predictive reliability' if avg_prediction_confidence >= 65 else 'Developing predictive capability'} enables proactive portfolio risk management."""
    
    # Portfolio Optimization
    portfolio_optimization = f"""Portfolio risk exposure averaging {avg_composite_score:.1f}/10 requires {'minimal adjustment' if avg_composite_score <= 5 else 'moderate optimization' if avg_composite_score <= 6.5 else 'significant rebalancing'}. Risk-adjusted allocation based on quantified multi-dimensional assessment. {'Well-diversified' if high_risk_companies <= total_companies * 0.3 else 'Concentration requiring diversification'} risk distribution across companies."""
    
    # Implementation Strategy
    target_composite = max(3, avg_composite_score - 1.5)
    target_confidence = min(90, avg_prediction_confidence + 15)
    
    implementation_strategy = f"""**Immediate Risk Management (0-3 months):** {'Address {total_critical_alerts} critical alerts through targeted mitigation' if total_critical_alerts > 0 else 'Maintain proactive monitoring protocols'}. Deploy enhanced monitoring for {companies_with_critical if companies_with_critical > 0 else 'all'} companies. Implement quantified risk assessment integration.

**Medium-Term Framework (3-12 months):** Advanced early warning development targeting {target_confidence:.0f}% confidence. Strategic rebalancing toward {target_composite:.1f}/10 composite score. Sophisticated alert automation with reduced manual intervention.

**Long-Term Excellence (12+ months):** Industry-leading risk management with comprehensive intelligence framework. Advanced risk-adjusted allocation with superior optimization. Strategic risk advantage as competitive differentiator.

**Success Metrics:** Target composite {target_composite:.1f}/10 within 18 months, zero critical alerts within 12 months, {target_confidence:.0f}% prediction accuracy within 24 months, enhanced risk-adjusted returns within 36 months."""
    
    return {
        'risk_intelligence': risk_intelligence,
        'alert_optimization': alert_optimization,
        'predictive_management': predictive_management,
        'portfolio_optimization': portfolio_optimization,
        'implementation_strategy': implementation_strategy
    }


def _build_risk_intelligence_section(intelligence_text: str, risk_analysis: Dict, 
                                     risk_scoring: Dict) -> str:
    """Build risk management intelligence section with enhanced presentation"""
    
    # Calculate metrics for cards
    total_companies = len(risk_analysis)
    avg_risk = np.mean([analysis['overall_risk_score'] for analysis in risk_analysis.values()])
    total_alerts = sum(len(analysis['alert_triggers']) for analysis in risk_analysis.values())
    
    high_risk_count = sum(1 for scoring in risk_scoring.values() 
                         if scoring['risk_rating'] in ['High Risk', 'Critical Risk', 'Extreme Risk'])
    
    # Create summary cards
    summary_cards = [
        {
            "label": "Portfolio Health Score",
            "value": f"{(10-avg_risk)*10:.0f}/100",
            "description": "Overall Risk Management"
        },
        {
            "label": "Risk Coverage",
            "value": f"{total_alerts}",
            "description": f"Alerts Across {total_companies} Companies"
        },
        {
            "label": "High-Risk Exposure",
            "value": f"{high_risk_count}",
            "description": f"{high_risk_count/total_companies*100:.0f}% of Portfolio"
        }
    ]
    
    cards_html = ""
    for card in summary_cards:
        cards_html += f"""
        <div style="background: linear-gradient(135deg, var(--card-bg), var(--card-bg)); 
                    padding: 20px; border-radius: 12px; border-left: 4px solid var(--primary-gradient-start);
                    box-shadow: var(--shadow-sm); flex: 1; min-width: 200px;">
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px; font-weight: 600;">
                {card['label']}
            </div>
            <div style="font-size: 2rem; font-weight: 900; background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
                {card['value']}
            </div>
            <div style="font-size: 0.85rem; color: var(--text-tertiary);">
                {card['description']}
            </div>
        </div>
        """
    
    cards_grid = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
        {cards_html}
    </div>
    """
    
    return f"""
    <div class="info-section">
        <h4>🎯 Risk Management Intelligence & Portfolio Assessment</h4>
        
        {cards_grid}
        
        {build_info_box(intelligence_text, box_type="info")}
        
        <div style="margin-top: 20px; padding: 15px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                    border-radius: 12px; border-left: 4px solid var(--primary-gradient-start);">
            <strong>💡 Strategic Insight:</strong> Portfolio risk management framework provides comprehensive multi-dimensional 
            assessment enabling proactive intervention and value protection across all risk categories.
        </div>
    </div>
    """


def _build_alert_optimization_section(optimization_text: str, alert_system: Dict) -> str:
    """Build alert system optimization section"""
    
    total_companies = len(alert_system)
    total_critical = sum(alerts['alert_summary']['critical_count'] for alerts in alert_system.values())
    total_warning = sum(alerts['alert_summary']['warning_count'] for alerts in alert_system.values())
    avg_priority = np.mean([alerts['alert_summary']['priority_score'] for alerts in alert_system.values()])
    
    # Create action priority cards
    action_cards = []
    
    if total_critical > 0:
        action_cards.append({
            "title": "🔴 Critical Intervention Required",
            "items": [
                f"{total_critical} critical alerts across portfolio",
                "Immediate risk mitigation protocols active",
                "Enhanced monitoring and control implementation"
            ],
            "color": "#ef4444"
        })
    
    if total_warning > 0:
        action_cards.append({
            "title": "🟠 Warning-Level Monitoring",
            "items": [
                f"{total_warning} warning alerts requiring attention",
                "Proactive early intervention protocols",
                "Standard monitoring enhancement recommended"
            ],
            "color": "#f59e0b"
        })
    
    action_cards.append({
        "title": "📊 Alert System Performance",
        "items": [
            f"Average priority score: {avg_priority:.0f}/100",
            f"Alert coverage: {total_companies} companies monitored",
            "Multi-tiered severity classification active"
        ],
        "color": "#3b82f6"
    })
    
    cards_html = ""
    for card in action_cards:
        items_html = "".join([f"<li style='margin: 8px 0;'>{item}</li>" for item in card['items']])
        cards_html += f"""
        <div style="background: var(--card-bg); padding: 20px; border-radius: 12px; 
                    border-left: 4px solid {card['color']}; box-shadow: var(--shadow-sm);">
            <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">{card['title']}</h5>
            <ul style="margin: 0; padding-left: 20px; color: var(--text-secondary);">
                {items_html}
            </ul>
        </div>
        """
    
    return f"""
    <div class="info-section">
        <h4>⚡ Alert System Optimization & Response Framework</h4>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
            {cards_html}
        </div>
        
        {build_info_box(optimization_text, box_type="warning" if total_critical > 0 else "info")}
    </div>
    """


def _build_predictive_management_section(predictive_text: str, predictive_risk: Dict) -> str:
    """Build predictive risk management section"""
    
    total_companies = len(predictive_risk)
    avg_warning = np.mean([pred['early_warning_score'] for pred in predictive_risk.values()])
    avg_confidence = np.mean([pred['confidence_level'] for pred in predictive_risk.values()])
    
    deteriorating = sum(1 for pred in predictive_risk.values() if pred['risk_trajectory'] == 'Deteriorating')
    improving = sum(1 for pred in predictive_risk.values() if pred['risk_trajectory'] == 'Improving')
    stable = total_companies - deteriorating - improving
    
    # Progress indicators for trajectories
    progress_html = f"""
    <div style="margin: 20px 0;">
        {build_progress_indicator(improving, total_companies, "🟢 Improving Trajectories", show_percentage=True)}
        {build_progress_indicator(stable, total_companies, "🔵 Stable Trajectories", show_percentage=True)}
        {build_progress_indicator(deteriorating, total_companies, "🔴 Deteriorating Trajectories", show_percentage=True)}
    </div>
    """
    
    # Metrics grid
    metrics_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
        <div style="background: var(--card-bg); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid var(--card-border);">
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 5px;">Early Warning Score</div>
            <div style="font-size: 2rem; font-weight: 700; color: {'#ef4444' if avg_warning > 7 else '#f59e0b' if avg_warning > 5 else '#10b981'};">
                {avg_warning:.1f}/10
            </div>
        </div>
        <div style="background: var(--card-bg); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid var(--card-border);">
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 5px;">Prediction Confidence</div>
            <div style="font-size: 2rem; font-weight: 700; color: {'#10b981' if avg_confidence >= 75 else '#3b82f6' if avg_confidence >= 65 else '#f59e0b'};">
                {avg_confidence:.0f}%
            </div>
        </div>
        <div style="background: var(--card-bg); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid var(--card-border);">
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 5px;">Forecast Horizon</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">
                6-18 months
            </div>
        </div>
    </div>
    """
    
    return f"""
    <div class="info-section">
        <h4>🔮 Predictive Risk Management & Early Warning Systems</h4>
        
        {metrics_html}
        
        {progress_html}
        
        {build_info_box(predictive_text, box_type="info")}
    </div>
    """


def _build_portfolio_optimization_section(optimization_text: str, risk_scoring: Dict) -> str:
    """Build portfolio risk optimization section"""
    
    total_companies = len(risk_scoring)
    avg_composite = np.mean([scoring['composite_risk_score'] for scoring in risk_scoring.values()])
    
    # Rating distribution
    rating_counts = {}
    for scoring in risk_scoring.values():
        rating = scoring['risk_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    # Build distribution bars
    rating_order = ['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk', 'Extreme Risk']
    rating_colors = {
        'Low Risk': '#10b981',
        'Moderate Risk': '#3b82f6', 
        'High Risk': '#f59e0b',
        'Critical Risk': '#ef4444',
        'Extreme Risk': '#dc2626'
    }
    
    distribution_html = ""
    for rating in rating_order:
        count = rating_counts.get(rating, 0)
        if count > 0:
            percentage = (count / total_companies * 100)
            color = rating_colors.get(rating, '#667eea')
            
            distribution_html += f"""
            <div style="margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 600; color: var(--text-primary);">{rating}</span>
                    <span style="font-weight: 700; color: {color};">{count} companies ({percentage:.0f}%)</span>
                </div>
                <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 8px; height: 20px; overflow: hidden;">
                    <div style="width: {percentage}%; background: {color}; height: 100%; border-radius: 8px; transition: width 0.6s ease;"></div>
                </div>
            </div>
            """
    
    # Target metrics
    target_composite = max(3, avg_composite - 1.5)
    improvement_needed = avg_composite - target_composite
    
    target_html = f"""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
                padding: 20px; border-radius: 12px; border-left: 4px solid #10b981; margin: 20px 0;">
        <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">🎯 Portfolio Optimization Targets</h5>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Current Composite Score</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">{avg_composite:.1f}/10</div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Target Score (18 months)</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #10b981;">{target_composite:.1f}/10</div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px;">Required Improvement</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #3b82f6;">{improvement_needed:.1f} points</div>
            </div>
        </div>
    </div>
    """
    
    return f"""
    <div class="info-section">
        <h4>📈 Portfolio Risk Optimization & Strategic Risk Allocation</h4>
        
        {target_html}
        
        <h5 style="margin: 20px 0 10px 0;">Portfolio Risk Distribution</h5>
        {distribution_html}
        
        {build_info_box(optimization_text, box_type="success" if avg_composite <= 5 else "info")}
    </div>
    """


def _build_implementation_roadmap_section(strategy_text: str, risk_analysis: Dict,
                                         alert_system: Dict, risk_scoring: Dict,
                                         predictive_risk: Dict) -> str:
    """Build implementation roadmap section with tabbed timeline"""
    
    # Calculate metrics
    total_critical = sum(alerts['alert_summary']['critical_count'] for alerts in alert_system.values())
    avg_composite = np.mean([scoring['composite_risk_score'] for scoring in risk_scoring.values()])
    avg_confidence = np.mean([pred['confidence_level'] for pred in predictive_risk.values()])
    
    target_composite = max(3, avg_composite - 1.5)
    target_confidence = min(90, avg_confidence + 15)
    
    # Create tabbed timeline sections
    timeline_html = f"""
    <div style="margin: 30px 0;">
        <style>
            .timeline-tabs {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid var(--card-border);
            }}
            .timeline-tab {{
                padding: 12px 24px;
                background: none;
                border: none;
                border-bottom: 3px solid transparent;
                cursor: pointer;
                font-weight: 600;
                color: var(--text-secondary);
                transition: all 0.3s ease;
            }}
            .timeline-tab:hover {{
                color: var(--text-primary);
                background: rgba(102, 126, 234, 0.1);
            }}
            .timeline-tab.active {{
                color: var(--primary-gradient-start);
                border-bottom-color: var(--primary-gradient-start);
            }}
            .timeline-content {{
                display: none;
                padding: 20px;
                background: var(--card-bg);
                border-radius: 12px;
                border: 1px solid var(--card-border);
            }}
            .timeline-content.active {{
                display: block;
                animation: fadeIn 0.3s ease;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
        
        <div class="timeline-tabs">
            <button class="timeline-tab active" onclick="showTimeline('immediate')">⚡ Immediate (0-3M)</button>
            <button class="timeline-tab" onclick="showTimeline('medium')">🔧 Medium-Term (3-12M)</button>
            <button class="timeline-tab" onclick="showTimeline('long')">🏆 Long-Term (12M+)</button>
            <button class="timeline-tab" onclick="showTimeline('metrics')">📊 Success Metrics</button>
        </div>
        
        <div id="immediate" class="timeline-content active">
            <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">⚡ Immediate Risk Management Implementation (0-3 months)</h5>
            <ul style="line-height: 1.8; color: var(--text-secondary);">
                <li><strong>Critical Alert Response:</strong> {'Address ' + str(total_critical) + ' critical alerts through targeted risk mitigation' if total_critical > 0 else 'Maintain proactive monitoring protocols across all companies'}</li>
                <li><strong>Enhanced Monitoring Deployment:</strong> Implement enhanced oversight protocols and daily risk tracking</li>
                <li><strong>Risk Scoring Integration:</strong> Deploy quantified risk assessment framework for strategic decision-making</li>
                <li><strong>Immediate Intervention:</strong> Execute targeted risk mitigation plans for high-risk companies</li>
            </ul>
        </div>
        
        <div id="medium" class="timeline-content">
            <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">🔧 Medium-Term Risk Framework Development (3-12 months)</h5>
            <ul style="line-height: 1.8; color: var(--text-secondary);">
                <li><strong>Predictive Model Enhancement:</strong> Advanced early warning system development targeting {target_confidence:.0f}% confidence</li>
                <li><strong>Portfolio Risk Optimization:</strong> Strategic rebalancing toward {target_composite:.1f}/10 average composite score</li>
                <li><strong>Risk Management Automation:</strong> Sophisticated alert system with reduced manual intervention and automated responses</li>
                <li><strong>Correlation Analysis:</strong> Enhanced economic correlation tracking and leading indicator identification</li>
            </ul>
        </div>
        
        <div id="long" class="timeline-content">
            <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">🏆 Long-Term Risk Excellence Achievement (12+ months)</h5>
            <ul style="line-height: 1.8; color: var(--text-secondary);">
                <li><strong>Industry-Leading Framework:</strong> Comprehensive risk intelligence with best-in-class predictive capabilities</li>
                <li><strong>Portfolio Risk Mastery:</strong> Advanced risk-adjusted allocation with superior risk-return optimization</li>
                <li><strong>Strategic Risk Advantage:</strong> Risk management as competitive differentiator and alpha generation source</li>
                <li><strong>Continuous Innovation:</strong> Ongoing enhancement of risk models and analytical frameworks</li>
            </ul>
        </div>
        
        <div id="metrics" class="timeline-content">
            <h5 style="margin: 0 0 15px 0; color: var(--text-primary);">📊 Success Metrics & Strategic Targets</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px;">
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                            padding: 20px; border-radius: 12px; border-left: 4px solid var(--primary-gradient-start);">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">Composite Risk Score</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px;">
                        {target_composite:.1f}/10
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-tertiary);">Target within 18 months</div>
                </div>
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
                            padding: 20px; border-radius: 12px; border-left: 4px solid #10b981;">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">Critical Alerts</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px;">
                        Zero
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-tertiary);">Target within 12 months</div>
                </div>
                <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
                            padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">Prediction Accuracy</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px;">
                        {target_confidence:.0f}%
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-tertiary);">Target within 24 months</div>
                </div>
                <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
                            padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b;">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">Risk-Adjusted Returns</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px;">
                        Enhanced
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-tertiary);">Target within 36 months</div>
                </div>
            </div>
        </div>
        
        <script>
            function showTimeline(timelineId) {{
                // Hide all timelines
                document.querySelectorAll('.timeline-content').forEach(content => {{
                    content.classList.remove('active');
                }});
                document.querySelectorAll('.timeline-tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                
                // Show selected timeline
                document.getElementById(timelineId).classList.add('active');
                event.target.classList.add('active');
            }}
        </script>
    </div>
    """
    
    return f"""
    <div class="info-section">
        <h4>🚀 Comprehensive Risk Strategy & Implementation Roadmap</h4>
        
        {timeline_html}
        
        <div style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
                    border-radius: 12px; border-left: 4px solid var(--primary-gradient-start);">
            <h5 style="margin: 0 0 10px 0; color: var(--text-primary);">🎯 Strategic Implementation Focus</h5>
            <p style="color: var(--text-secondary); line-height: 1.8; margin: 0;">
                Comprehensive risk management transformation requires coordinated execution across immediate tactical 
                interventions, medium-term strategic framework development, and long-term excellence achievement. 
                Success metrics provide clear benchmarks for progress tracking and continuous optimization of portfolio 
                risk exposure while maintaining alignment with strategic objectives and value creation goals.
            </p>
        </div>
    </div>
    """


# Note: The following helper functions should already exist in your main file from previous steps.
# These are just references - DO NOT duplicate them:
# - _generate_comprehensive_risk_analysis()
# - _generate_automated_alerts()
# - _generate_risk_scoring_system()
# - _generate_predictive_risk_models()
# - _build_collapsible_subsection()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _build_collapsible_subsection(subsection_id: str, title: str, content: str) -> str:
    """Build a collapsible/expandable subsection"""
    
    collapse_id = f"collapse-{subsection_id.replace('.', '-')}"
    
    # We need to add the collapse/expand functionality via CSS and JavaScript
    # Since we can't modify the wrapper, we'll use inline styles and script
    
    html = f"""
    <div class="collapsible-subsection" style="margin: 30px 0; border: 1px solid var(--card-border); border-radius: 12px; overflow: hidden;">
        <div class="subsection-header" style="background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)); padding: 15px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;" onclick="toggleCollapse('{collapse_id}')">
            <h2 style="color: white; margin: 0; font-size: 1.5rem;">{subsection_id}. {title}</h2>
            <span id="{collapse_id}-icon" style="color: white; font-size: 1.5rem; font-weight: bold;">−</span>
        </div>
        <div id="{collapse_id}" class="subsection-content" style="padding: 30px; display: block;">
            {content}
        </div>
    </div>
    
    <script>
        function toggleCollapse(id) {{
            const content = document.getElementById(id);
            const icon = document.getElementById(id + '-icon');
            
            if (content.style.display === 'none') {{
                content.style.display = 'block';
                icon.textContent = '−';
            }} else {{
                content.style.display = 'none';
                icon.textContent = '+';
            }}
        }}
    </script>
    """
    
    return html