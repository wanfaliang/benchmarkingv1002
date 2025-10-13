"""
Section 15: Market Microstructure Analysis
Phase 1: Scaffolding + Section 15A (Liquidity & Float Analysis)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging

from backend.app.report_generation.html_utils import (
    generate_section_wrapper,
    build_stat_card,
    build_stat_grid,
    build_info_box,
    build_section_divider,
    build_data_table,
    build_plotly_chart,
    format_currency,
    format_percentage,
    format_number
)

logger = logging.getLogger(__name__)


"""
REPLACE THE MAIN generate() FUNCTION WITH THIS
This integrates all phases properly
"""

def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 15: Market Microstructure Analysis
    
    Advanced market microstructure analysis with:
    - Liquidity proxy analysis using ownership concentration and float turnover
    - Comprehensive technical indicator suite from OHLC data
    - Price discovery efficiency analysis with analyst target convergence
    - Trading pattern analysis and market impact assessment
    - Microstructure quality scoring and liquidity intelligence
    """
    
    try:
        
        
        # Get data
        companies = collector.companies
        df = collector.get_all_financial_data()
        
        # Get enhanced datasets with error handling
        try:
            prices_df = collector.get_prices_daily()
            institutional_df = collector.get_institutional_ownership()
            profiles_df = collector.get_profiles()
            analyst_estimates, analyst_targets = collector.get_analyst_estimates()
        except Exception as e:
            logger.warning(f"Error loading enhanced datasets: {e}")
            prices_df = pd.DataFrame()
            institutional_df = pd.DataFrame()
            profiles_df = pd.DataFrame()
            analyst_estimates = pd.DataFrame()
            analyst_targets = pd.DataFrame()
        
        # Generate ALL analyses (all phases)
        
        liquidity_analysis = _generate_liquidity_analysis(df, prices_df, institutional_df, profiles_df, companies)
        
        
        float_analysis = _analyze_float_dynamics(df, prices_df, institutional_df, profiles_df, companies)
        
        
        technical_analysis = _generate_technical_analysis(prices_df, companies, df)
        
        
        volatility_analysis = _analyze_volatility_patterns(prices_df, companies, technical_analysis)
        
        
        price_discovery_analysis = _analyze_price_discovery(prices_df, analyst_targets, profiles_df, companies)
        
        # Build HTML content (all sections)
        content_parts = []
        
        
        content_parts.append(_build_section_15a(liquidity_analysis, float_analysis, companies))
        
        
        content_parts.append(_build_section_15b(technical_analysis, volatility_analysis, companies))
        
        
        content_parts.append(_build_section_15c(price_discovery_analysis, companies))
        
        
        content_parts.append(_build_section_15d(liquidity_analysis, technical_analysis, 
                                                volatility_analysis, price_discovery_analysis, companies))
        
        
        content_parts.append(_build_section_15e(liquidity_analysis, float_analysis, technical_analysis, 
                                                volatility_analysis, price_discovery_analysis, companies))
        
        content = "\n".join(content_parts)
        
        
        return generate_section_wrapper(15, "Market Microstructure Analysis", content)
        
    except Exception as e:
        logger.error(f"Error generating Section 15: {str(e)}", exc_info=True)
        error_content = f'<div class="info-box danger"><p>Error generating Section 15: {str(e)}</p></div>'
        return generate_section_wrapper(15, "Market Microstructure Analysis", error_content)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is 0"""
    try:
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        return numerator / denominator
    except:
        return default


# =============================================================================
# SECTION 15A: LIQUIDITY PROXIES & MARKET STRUCTURE
# =============================================================================

def _build_section_15a(liquidity_analysis: Dict, float_analysis: Dict, companies: Dict) -> str:
    """Build Section 15A: Liquidity Proxies & Market Structure Intelligence"""
    
    html_parts = []
    
    html_parts.append('<div class="info-section">')
    html_parts.append('<h3>15A. Liquidity Proxies & Market Structure Intelligence</h3>')
    
    # 15A.1: Ownership Concentration Impact
    html_parts.append(_build_liquidity_concentration_section(liquidity_analysis, companies))
    
    html_parts.append(build_section_divider())
    
    # 15A.2: Float Analysis & Trading Dynamics
    html_parts.append(_build_float_dynamics_section(float_analysis, companies))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_liquidity_concentration_section(liquidity_analysis: Dict, companies: Dict) -> str:
    """Build 15A.1: Ownership Concentration Impact on Trading Liquidity"""
    
    if not liquidity_analysis:
        return build_info_box("Liquidity analysis unavailable due to insufficient market data.", "warning")
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15A.1 Ownership Concentration Impact on Trading Liquidity</h4>')
    
    # Summary cards
    liquidity_summary = _generate_liquidity_summary(liquidity_analysis)
    html_parts.append(liquidity_summary)
    
    # Liquidity table
    html_parts.append('<h4>Liquidity Analysis by Company</h4>')
    liquidity_table = _create_liquidity_table(liquidity_analysis)
    html_parts.append(liquidity_table)
    
    # Liquidity charts (4 standalone charts)
    liquidity_charts = _create_liquidity_charts(liquidity_analysis)
    for chart in liquidity_charts:
        if chart:
            html_parts.append(chart)
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_float_dynamics_section(float_analysis: Dict, companies: Dict) -> str:
    """Build 15A.2: Float Analysis & Trading Dynamics Assessment"""
    
    if not float_analysis:
        return build_info_box("Float analysis unavailable due to insufficient ownership data.", "warning")
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15A.2 Float Analysis & Trading Dynamics Assessment</h4>')
    
    # Summary cards
    float_summary = _generate_float_summary(float_analysis)
    html_parts.append(float_summary)
    
    # Float table
    html_parts.append('<h4>Float Analysis by Company</h4>')
    float_table = _create_float_table(float_analysis)
    html_parts.append(float_table)
    
    # Float charts (4 standalone charts)
    float_charts = _create_float_charts(float_analysis)
    for chart in float_charts:
        if chart:
            html_parts.append(chart)
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


# =============================================================================
# LIQUIDITY ANALYSIS FUNCTIONS
# =============================================================================

def _generate_liquidity_analysis(df: pd.DataFrame, prices_df: pd.DataFrame, 
                                institutional_df: pd.DataFrame, profiles_df: pd.DataFrame,
                                companies: Dict[str, str]) -> Dict[str, Dict]:
    """Generate comprehensive liquidity proxy analysis"""
    
    liquidity_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get company data
            company_prices = prices_df[prices_df['Company'] == company_name] if not prices_df.empty else pd.DataFrame()
            company_institutional = institutional_df[institutional_df['Company'] == company_name] if not institutional_df.empty else pd.DataFrame()
            
            # Safe profile extraction
            if not profiles_df.empty:
                profile_matches = profiles_df[profiles_df['Company'] == company_name]
                company_profile = profile_matches.iloc[0] if len(profile_matches) > 0 else None
            else:
                company_profile = None
            
            # Basic liquidity metrics
            if not company_prices.empty:
                recent_prices = company_prices.tail(252)  # Last year of data
                avg_daily_volume = recent_prices['volume'].mean() if 'volume' in recent_prices.columns else 0
                avg_daily_value = (recent_prices['close'] * recent_prices['volume']).mean() if 'volume' in recent_prices.columns else 0
                volume_volatility = recent_prices['volume'].std() if 'volume' in recent_prices.columns else 0
                
                # Price impact proxy (using high-low spread)
                if 'high' in recent_prices.columns and 'low' in recent_prices.columns:
                    daily_spreads = (recent_prices['high'] - recent_prices['low']) / recent_prices['close']
                    avg_spread = daily_spreads.mean() * 100
                else:
                    avg_spread = 2.0
            else:
                avg_daily_volume = 0
                avg_daily_value = 0
                volume_volatility = 0
                avg_spread = 2.0
            
            # Ownership concentration impact
            if not company_institutional.empty and len(company_institutional) > 0:
                latest_institutional = company_institutional.iloc[-1]
                ownership_concentration = latest_institutional.get('ownershipPercent', 0)
                investor_count = latest_institutional.get('investorsHolding', 0)
                
                # Calculate concentration index
                concentration_index = _safe_divide(ownership_concentration, investor_count)
            else:
                ownership_concentration = 0
                investor_count = 0
                concentration_index = 0
            
            # Market cap and float estimation
            if company_profile is not None:
                market_cap = company_profile.get('marketCap', 0)
                current_price = company_profile.get('price', 0)
                shares_outstanding = _safe_divide(market_cap, current_price)
                
                # Estimate free float
                institutional_shares = shares_outstanding * (ownership_concentration / 100) if shares_outstanding > 0 else 0
                estimated_float = max(0, shares_outstanding - institutional_shares)
                float_percentage = _safe_divide(estimated_float, shares_outstanding) * 100
            else:
                market_cap = 0
                shares_outstanding = 0
                estimated_float = 0
                float_percentage = 100
            
            # Liquidity quality score
            liquidity_components = [
                min(10, avg_daily_value / 1000000),
                max(0, 10 - avg_spread * 2),
                min(10, float_percentage / 10),
                max(0, 10 - concentration_index * 5)
            ]
            
            liquidity_score = np.mean([comp for comp in liquidity_components if comp >= 0])
            
            # Liquidity classification
            if liquidity_score >= 7:
                liquidity_class = "High Liquidity"
            elif liquidity_score >= 5:
                liquidity_class = "Moderate Liquidity"
            else:
                liquidity_class = "Low Liquidity"
            
            liquidity_analysis[company_name] = {
                'avg_daily_volume': avg_daily_volume,
                'avg_daily_value': avg_daily_value,
                'volume_volatility': volume_volatility,
                'avg_spread': avg_spread,
                'ownership_concentration': ownership_concentration,
                'investor_count': investor_count,
                'concentration_index': concentration_index,
                'market_cap': market_cap,
                'estimated_float': estimated_float,
                'float_percentage': float_percentage,
                'liquidity_score': liquidity_score,
                'liquidity_class': liquidity_class
            }
            
        except Exception as e:
            logger.warning(f"Liquidity analysis failed for {company_name}: {e}")
            continue
    
    return liquidity_analysis


def _create_liquidity_table(liquidity_analysis: Dict[str, Dict]) -> str:
    """Create liquidity analysis table"""
    
    if not liquidity_analysis:
        return build_info_box("No liquidity data available.", "warning")
    
    # Prepare DataFrame
    rows = []
    for company_name, analysis in liquidity_analysis.items():
        rows.append({
            'Company': company_name,
            'Avg Daily Volume': format_number(analysis['avg_daily_volume'], decimals=0),
            'Daily Value ($M)': format_number(analysis['avg_daily_value']/1000000, decimals=1),
            'Bid-Ask Spread (%)': f"{analysis['avg_spread']:.2f}",
            'Ownership Conc. (%)': f"{analysis['ownership_concentration']:.1f}",
            'Float (%)': f"{analysis['float_percentage']:.1f}",
            'Liquidity Score': f"{analysis['liquidity_score']:.1f}/10",
            'Liquidity Class': analysis['liquidity_class'],
            'Trading Rank': ''  # Will be filled after sorting
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by liquidity score (need to extract numeric value)
    liquidity_scores = [analysis['liquidity_score'] for analysis in liquidity_analysis.values()]
    sorted_indices = sorted(range(len(liquidity_scores)), key=lambda i: liquidity_scores[i], reverse=True)
    
    df_sorted = df.iloc[sorted_indices].reset_index(drop=True)
    df_sorted['Trading Rank'] = [f"{i+1}/{len(df)}" for i in range(len(df))]
    
    return build_data_table(df_sorted, table_id="liquidity-table")


def _generate_liquidity_summary(liquidity_analysis: Dict[str, Dict]) -> str:
    """Generate liquidity analysis summary cards"""
    
    total_companies = len(liquidity_analysis)
    
    if total_companies == 0:
        return build_info_box("No liquidity analysis available.", "warning")
    
    # Portfolio liquidity statistics
    avg_liquidity_score = np.mean([analysis['liquidity_score'] for analysis in liquidity_analysis.values()])
    high_liquidity = sum(1 for analysis in liquidity_analysis.values() if analysis['liquidity_class'] == 'High Liquidity')
    avg_daily_value = np.mean([analysis['avg_daily_value'] for analysis in liquidity_analysis.values()])
    avg_spread = np.mean([analysis['avg_spread'] for analysis in liquidity_analysis.values()])
    avg_float = np.mean([analysis['float_percentage'] for analysis in liquidity_analysis.values()])
    
    cards = [
        {
            "label": "Portfolio Liquidity Score",
            "value": f"{avg_liquidity_score:.1f}/10",
            "description": f"{high_liquidity}/{total_companies} high-liquidity companies ({(high_liquidity/total_companies)*100:.0f}%)",
            "type": "success" if avg_liquidity_score >= 7 else "info" if avg_liquidity_score >= 5 else "warning"
        },
        {
            "label": "Average Daily Trading Value",
            "value": format_currency(avg_daily_value/1000000, decimals=1, millions=False) + "M",
            "description": f"{avg_spread:.2f}% average bid-ask spreads",
            "type": "success" if avg_daily_value > 10000000 else "info"
        },
        {
            "label": "Average Free Float",
            "value": f"{avg_float:.1f}%",
            "description": "Supporting liquid trading",
            "type": "success" if avg_float >= 60 else "info" if avg_float >= 40 else "warning"
        },
        {
            "label": "Market Access Quality",
            "value": 'Excellent' if avg_liquidity_score >= 7 and high_liquidity >= total_companies * 0.6 else 'Good' if avg_liquidity_score >= 6 else 'Mixed',
            "description": "For portfolio execution",
            "type": "success" if avg_liquidity_score >= 7 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_liquidity_charts(liquidity_analysis: Dict) -> List[str]:
    """Create 4 standalone liquidity analysis charts"""
    
    if not liquidity_analysis:
        return []
    
    import plotly.graph_objects as go
    
    companies_list = list(liquidity_analysis.keys())
    charts = []
    
    # Chart 1: Liquidity Score vs Daily Value
    daily_values = [analysis['avg_daily_value']/1000000 for analysis in liquidity_analysis.values()]
    liquidity_scores = [analysis['liquidity_score'] for analysis in liquidity_analysis.values()]
    
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=daily_values,
            y=liquidity_scores,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color=liquidity_scores, colorscale='RdYlGn', 
                       showscale=True, colorbar=dict(title="Score")),
            hovertemplate='<b>%{text}</b><br>Daily Value: $%{x:.1f}M<br>Liquidity Score: %{y:.1f}/10<extra></extra>'
        )
    )
    fig1.update_layout(
        title="Liquidity Score vs Daily Trading Value",
        xaxis_title="Average Daily Value ($M)",
        yaxis_title="Liquidity Score (0-10)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig1.to_dict(), div_id="liquidity-chart-1", height=500))
    
    # Chart 2: Ownership Concentration Impact on Spreads
    ownership_conc = [analysis['ownership_concentration'] for analysis in liquidity_analysis.values()]
    avg_spreads = [analysis['avg_spread'] for analysis in liquidity_analysis.values()]
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=ownership_conc,
            y=avg_spreads,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color='#3b82f6'),
            hovertemplate='<b>%{text}</b><br>Ownership Conc: %{x:.1f}%<br>Spread: %{y:.2f}%<extra></extra>'
        )
    )
    fig2.update_layout(
        title="Ownership Concentration Impact on Bid-Ask Spreads",
        xaxis_title="Ownership Concentration (%)",
        yaxis_title="Bid-Ask Spread (%)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig2.to_dict(), div_id="liquidity-chart-2", height=500))
    
    # Chart 3: Float vs Liquidity Score
    float_pcts = [analysis['float_percentage'] for analysis in liquidity_analysis.values()]
    
    fig3 = go.Figure()
    fig3.add_trace(
        go.Scatter(
            x=float_pcts,
            y=liquidity_scores,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color='#10b981'),
            hovertemplate='<b>%{text}</b><br>Float: %{x:.1f}%<br>Liquidity Score: %{y:.1f}/10<extra></extra>'
        )
    )
    fig3.update_layout(
        title="Free Float vs Liquidity Quality",
        xaxis_title="Free Float (%)",
        yaxis_title="Liquidity Score (0-10)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig3.to_dict(), div_id="liquidity-chart-3", height=500))
    
    # Chart 4: Liquidity Classification Distribution
    liquidity_classes = [analysis['liquidity_class'] for analysis in liquidity_analysis.values()]
    class_counts = {'High Liquidity': 0, 'Moderate Liquidity': 0, 'Low Liquidity': 0}
    
    for liq_class in liquidity_classes:
        class_counts[liq_class] += 1
    
    fig4 = go.Figure()
    fig4.add_trace(
        go.Pie(
            labels=list(class_counts.keys()),
            values=list(class_counts.values()),
            marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    )
    fig4.update_layout(
        title="Portfolio Liquidity Classification Distribution",
        height=500,
        showlegend=True
    )
    charts.append(build_plotly_chart(fig4.to_dict(), div_id="liquidity-chart-4", height=500))
    
    return charts


# =============================================================================
# FLOAT ANALYSIS FUNCTIONS
# =============================================================================

def _analyze_float_dynamics(df: pd.DataFrame, prices_df: pd.DataFrame, 
                           institutional_df: pd.DataFrame, profiles_df: pd.DataFrame,
                           companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze float dynamics and turnover patterns"""
    
    float_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get basic data
            if not prices_df.empty:
                price_matches = prices_df[prices_df['Company'] == company_name]
                company_prices = price_matches
            else:
                company_prices = pd.DataFrame()
            
            if not institutional_df.empty:
                institutional_matches = institutional_df[institutional_df['Company'] == company_name]
                company_institutional = institutional_matches
            else:
                company_institutional = pd.DataFrame()
            
            if not profiles_df.empty:
                profile_matches = profiles_df[profiles_df['Company'] == company_name]
                company_profile = profile_matches.iloc[0] if len(profile_matches) > 0 else None
            else:
                company_profile = None
            
            if company_profile is None:
                continue
            
            # Basic metrics
            market_cap = company_profile.get('marketCap', 0)
            current_price = company_profile.get('price', 0)
            shares_outstanding = _safe_divide(market_cap, current_price)
            
            # Institutional ownership analysis
            if not company_institutional.empty and len(company_institutional) > 0:
                institutional_data = company_institutional.sort_values('date')
                latest = institutional_data.iloc[-1]
                institutional_ownership = latest.get('ownershipPercent', 0)
                investor_count = latest.get('investorsHolding', 0)
                
                if len(institutional_data) > 1:
                    ownership_change = latest.get('ownershipPercentChange', 0)
                else:
                    ownership_change = 0
            else:
                institutional_ownership = 0
                investor_count = 0
                ownership_change = 0
            
            # Float calculations
            institutional_shares = shares_outstanding * (institutional_ownership / 100)
            insider_shares = shares_outstanding * 0.15  # Rough estimate
            restricted_shares = institutional_shares + insider_shares
            free_float_shares = max(0, shares_outstanding - restricted_shares)
            free_float_percentage = _safe_divide(free_float_shares, shares_outstanding) * 100
            
            # Trading turnover analysis
            if not company_prices.empty and 'volume' in company_prices.columns:
                recent_data = company_prices.tail(63)  # Last quarter
                avg_daily_volume = recent_data['volume'].mean()
                
                daily_turnover_float = _safe_divide(avg_daily_volume, free_float_shares) * 100
                daily_turnover_total = _safe_divide(avg_daily_volume, shares_outstanding) * 100
                
                quarterly_volume = recent_data['volume'].sum()
                float_velocity = _safe_divide(quarterly_volume, free_float_shares)
                
                volume_volatility = _safe_divide(recent_data['volume'].std(), avg_daily_volume) if avg_daily_volume > 0 else 0
            else:
                avg_daily_volume = 0
                daily_turnover_float = 0
                daily_turnover_total = 0
                float_velocity = 0
                volume_volatility = 0
            
            # Float quality score
            float_quality_components = [
                min(10, free_float_percentage / 10),
                min(10, daily_turnover_float * 2) if daily_turnover_float > 0 else 0,
                max(0, 10 - volume_volatility * 5),
                min(10, investor_count / 10) if investor_count > 0 else 5
            ]
            
            float_quality_score = np.mean([comp for comp in float_quality_components if comp >= 0])
            
            # Classification
            if float_quality_score >= 7 and free_float_percentage >= 60:
                float_classification = "Highly Tradeable"
            elif float_quality_score >= 5 and free_float_percentage >= 40:
                float_classification = "Moderately Tradeable"
            else:
                float_classification = "Constrained Trading"
            
            float_analysis[company_name] = {
                'shares_outstanding': shares_outstanding,
                'institutional_ownership': institutional_ownership,
                'free_float_shares': free_float_shares,
                'free_float_percentage': free_float_percentage,
                'avg_daily_volume': avg_daily_volume,
                'daily_turnover_float': daily_turnover_float,
                'daily_turnover_total': daily_turnover_total,
                'float_velocity': float_velocity,
                'volume_volatility': volume_volatility,
                'investor_count': investor_count,
                'ownership_change': ownership_change,
                'float_quality_score': float_quality_score,
                'float_classification': float_classification
            }
            
        except Exception as e:
            logger.warning(f"Float analysis failed for {company_name}: {e}")
            continue
    
    return float_analysis


def _create_float_table(float_analysis: Dict[str, Dict]) -> str:
    """Create float analysis table"""
    
    if not float_analysis:
        return build_info_box("No float data available.", "warning")
    
    # Prepare DataFrame
    rows = []
    for company_name, analysis in float_analysis.items():
        rows.append({
            'Company': company_name,
            'Free Float (%)': f"{analysis['free_float_percentage']:.1f}",
            'Daily Turnover (%)': f"{analysis['daily_turnover_float']:.2f}",
            'Float Velocity': f"{analysis['float_velocity']:.1f}",
            'Volume Volatility': f"{analysis['volume_volatility']:.2f}",
            'Investor Count': format_number(analysis['investor_count'], decimals=0),
            'Float Quality': f"{analysis['float_quality_score']:.1f}/10",
            'Classification': analysis['float_classification'],
            'Rank': ''
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by float quality score
    float_scores = [analysis['float_quality_score'] for analysis in float_analysis.values()]
    sorted_indices = sorted(range(len(float_scores)), key=lambda i: float_scores[i], reverse=True)
    
    df_sorted = df.iloc[sorted_indices].reset_index(drop=True)
    df_sorted['Rank'] = [f"{i+1}/{len(df)}" for i in range(len(df))]
    
    return build_data_table(df_sorted, table_id="float-table")


def _generate_float_summary(float_analysis: Dict[str, Dict]) -> str:
    """Generate float analysis summary cards"""
    
    total_companies = len(float_analysis)
    
    if total_companies == 0:
        return build_info_box("No float analysis available.", "warning")
    
    # Portfolio float statistics
    avg_free_float = np.mean([analysis['free_float_percentage'] for analysis in float_analysis.values()])
    avg_turnover = np.mean([analysis['daily_turnover_float'] for analysis in float_analysis.values()])
    avg_quality_score = np.mean([analysis['float_quality_score'] for analysis in float_analysis.values()])
    highly_tradeable = sum(1 for analysis in float_analysis.values() if analysis['float_classification'] == 'Highly Tradeable')
    
    cards = [
        {
            "label": "Portfolio Float Profile",
            "value": f"{avg_free_float:.1f}%",
            "description": f"{avg_quality_score:.1f}/10 average quality score",
            "type": "success" if avg_free_float >= 60 else "info" if avg_free_float >= 40 else "warning"
        },
        {
            "label": "Trading Accessibility",
            "value": f"{highly_tradeable}/{total_companies}",
            "description": f"Highly tradeable companies ({(highly_tradeable/total_companies)*100:.0f}%)",
            "type": "success" if highly_tradeable >= total_companies * 0.6 else "info"
        },
        {
            "label": "Turnover Activity",
            "value": f"{avg_turnover:.2f}%",
            "description": f"Daily float turnover ({'active' if avg_turnover > 1 else 'moderate' if avg_turnover > 0.5 else 'limited'} trading)",
            "type": "success" if avg_turnover > 0.8 else "info"
        },
        {
            "label": "Float Utilization",
            "value": 'Efficient' if avg_turnover > 0.8 and avg_free_float > 50 else 'Standard' if avg_turnover > 0.4 else 'Constrained',
            "description": "Trading capacity assessment",
            "type": "success" if avg_turnover > 0.8 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_float_charts(float_analysis: Dict) -> List[str]:
    """Create 4 standalone float dynamics charts"""
    
    if not float_analysis:
        return []
    
    import plotly.graph_objects as go
    
    companies_list = list(float_analysis.keys())
    charts = []
    
    # Chart 1: Float Quality Components (Bubble chart with investor count)
    float_pcts = [analysis['free_float_percentage'] for analysis in float_analysis.values()]
    quality_scores = [analysis['float_quality_score'] for analysis in float_analysis.values()]
    investor_counts = [analysis['investor_count'] for analysis in float_analysis.values()]
    
    # Scale bubble sizes
    max_count = max(investor_counts) if investor_counts else 1
    sizes = [max(10, min(40, (count / max_count) * 40)) for count in investor_counts]
    
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=float_pcts,
            y=quality_scores,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=sizes, color=quality_scores, colorscale='Viridis', 
                       showscale=True, colorbar=dict(title="Quality")),
            hovertemplate='<b>%{text}</b><br>Float: %{x:.1f}%<br>Quality: %{y:.1f}/10<br>Investors: %{marker.size}<extra></extra>'
        )
    )
    fig1.update_layout(
        title="Float Quality Components (Bubble Size = Investor Count)",
        xaxis_title="Free Float (%)",
        yaxis_title="Quality Score (0-10)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig1.to_dict(), div_id="float-chart-1", height=500))
    
    # Chart 2: Turnover vs Volume Volatility
    turnover_rates = [analysis['daily_turnover_float'] for analysis in float_analysis.values()]
    volume_vols = [analysis['volume_volatility'] for analysis in float_analysis.values()]
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=turnover_rates,
            y=volume_vols,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color='#f59e0b'),
            hovertemplate='<b>%{text}</b><br>Turnover: %{x:.2f}%<br>Vol Volatility: %{y:.2f}<extra></extra>'
        )
    )
    fig2.update_layout(
        title="Turnover vs Volume Volatility (Trading Consistency)",
        xaxis_title="Daily Float Turnover (%)",
        yaxis_title="Volume Volatility",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig2.to_dict(), div_id="float-chart-2", height=500))
    
    # Chart 3: Float Velocity Analysis (Bar chart)
    float_velocities = [analysis['float_velocity'] for analysis in float_analysis.values()]
    
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=[comp[:10] for comp in companies_list],
            y=float_velocities,
            marker=dict(color=float_velocities, colorscale='Blues', showscale=True,
                       colorbar=dict(title="Velocity")),
            hovertemplate='<b>%{x}</b><br>Velocity: %{y:.1f}<extra></extra>'
        )
    )
    fig3.update_layout(
        title="Float Turnover Velocity (Quarterly)",
        xaxis_title="Companies",
        yaxis_title="Float Velocity",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig3.to_dict(), div_id="float-chart-3", height=500))
    
    # Chart 4: Float Classification Distribution
    float_classes = [analysis['float_classification'] for analysis in float_analysis.values()]
    class_counts = {'Highly Tradeable': 0, 'Moderately Tradeable': 0, 'Constrained Trading': 0}
    
    for float_class in float_classes:
        class_counts[float_class] += 1
    
    fig4 = go.Figure()
    fig4.add_trace(
        go.Pie(
            labels=list(class_counts.keys()),
            values=list(class_counts.values()),
            marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    )
    fig4.update_layout(
        title="Float Tradeability Distribution",
        height=500,
        showlegend=True
    )
    charts.append(build_plotly_chart(fig4.to_dict(), div_id="float-chart-4", height=500))
    
    return charts



"""
Section 15: Market Microstructure Analysis
Phase 2: Technical Indicators & Volatility Analysis

This artifact contains ONLY the new Phase 2 functions to be added to the Phase 1 code.
Replace the stub functions and add these new functions to section_15.py.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# REPLACE _build_section_15b_stub() WITH THIS
# =============================================================================

def _build_section_15b(technical_analysis: Dict, volatility_analysis: Dict, companies: Dict) -> str:
    """Build Section 15B: Technical Indicators & Momentum Intelligence"""
    
    html_parts = []
    
    html_parts.append('<div class="info-section">')
    html_parts.append('<h3>15B. Technical Indicators & Momentum Intelligence</h3>')
    
    # 15B.1: Comprehensive Technical Analysis Suite
    html_parts.append(_build_technical_analysis_section(technical_analysis, companies))
    
    html_parts.append(build_section_divider())
    
    # 15B.2: Volatility Patterns & Mean Reversion Analysis
    html_parts.append(_build_volatility_analysis_section(volatility_analysis, companies))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_technical_analysis_section(technical_analysis: Dict, companies: Dict) -> str:
    """Build 15B.1: Comprehensive Technical Analysis Suite"""
    
    if not technical_analysis:
        return build_info_box("Technical analysis unavailable due to insufficient price data.", "warning")
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15B.1 Comprehensive Technical Analysis Suite</h4>')
    
    # Summary cards
    technical_summary = _generate_technical_summary(technical_analysis)
    html_parts.append(technical_summary)
    
    # Technical table
    html_parts.append('<h4>Technical Analysis by Company</h4>')
    technical_table = _create_technical_table(technical_analysis)
    html_parts.append(technical_table)
    
    # Technical charts (4 standalone charts)
    technical_charts = _create_technical_charts(technical_analysis)
    for chart in technical_charts:
        if chart:
            html_parts.append(chart)
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_volatility_analysis_section(volatility_analysis: Dict, companies: Dict) -> str:
    """Build 15B.2: Volatility Patterns & Mean Reversion Analysis"""
    
    if not volatility_analysis:
        return build_info_box("Volatility analysis unavailable due to insufficient price data.", "warning")
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15B.2 Volatility Patterns & Mean Reversion Analysis</h4>')
    
    # Summary cards
    volatility_summary = _generate_volatility_summary(volatility_analysis)
    html_parts.append(volatility_summary)
    
    # Volatility table
    html_parts.append('<h4>Volatility Analysis by Company</h4>')
    volatility_table = _create_volatility_table(volatility_analysis)
    html_parts.append(volatility_table)
    
    # Volatility charts (4 standalone charts)
    volatility_charts = _create_volatility_charts(volatility_analysis)
    for chart in volatility_charts:
        if chart:
            html_parts.append(chart)
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


# =============================================================================
# TECHNICAL ANALYSIS FUNCTIONS
# =============================================================================

def _generate_technical_analysis(prices_df: pd.DataFrame, companies: Dict[str, str], 
                                df: pd.DataFrame) -> Dict[str, Dict]:
    """Generate comprehensive technical analysis suite"""
    
    first_company = list(companies.keys())[0]
    matches = prices_df[prices_df['Company'] == first_company]
    print(f"  {first_company}: {len(matches)} rows")
    print(f"================================")
    if prices_df.empty:
        return {}
    
    technical_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get company prices
            if not prices_df.empty:
                price_matches = prices_df[prices_df['Company'] == company_name]
                company_prices = price_matches.copy()
            else:
                continue
            
            if len(company_prices) < 50:  # Minimum data for technical analysis
                continue
            
            company_prices = company_prices.sort_values('date').reset_index(drop=True)
            
            # Basic price metrics
            close_prices = company_prices['close']
            high_prices = company_prices['high'] if 'high' in company_prices.columns else close_prices
            low_prices = company_prices['low'] if 'low' in company_prices.columns else close_prices
            volume = company_prices['volume'] if 'volume' in company_prices.columns else pd.Series([1000000] * len(close_prices))
            
            # Momentum indicators
            # RSI (14-day)
            rsi = _calculate_rsi(close_prices, 14)
            current_rsi = rsi.iloc[-1]
            
            # MACD
            macd_line, macd_signal, macd_histogram = _calculate_macd(close_prices)
            current_macd = macd_line.iloc[-1] if not macd_line.empty else 0
            current_macd_signal = macd_signal.iloc[-1] if not macd_signal.empty else 0
            
            # Moving averages
            sma_20 = close_prices.rolling(window=20).mean()
            sma_50 = close_prices.rolling(window=50).mean()
            
            # Price relative to moving averages
            current_price = close_prices.iloc[-1]
            price_vs_sma20 = _safe_divide(current_price - sma_20.iloc[-1], sma_20.iloc[-1]) * 100 if not sma_20.empty else 0
            price_vs_sma50 = _safe_divide(current_price - sma_50.iloc[-1], sma_50.iloc[-1]) * 100 if not sma_50.empty else 0
            
            # Volatility indicators
            # Bollinger Bands
            bb_middle = sma_20
            bb_std = close_prices.rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            bb_position = _safe_divide(current_price - bb_lower.iloc[-1], bb_upper.iloc[-1] - bb_lower.iloc[-1]) if not bb_upper.empty else 0.5
            
            # Average True Range (ATR)
            atr = _calculate_atr(high_prices, low_prices, close_prices, 14)
            current_atr = atr.iloc[-1] if not atr.empty else 0
            atr_percentage = _safe_divide(current_atr, current_price) * 100 if current_price > 0 else 0
            
            # Volume indicators
            volume_sma = volume.rolling(window=20).mean()
            current_volume_ratio = _safe_divide(volume.iloc[-1], volume_sma.iloc[-1]) if not volume_sma.empty and volume_sma.iloc[-1] > 0 else 1
            
            # Trend strength
            adx = _calculate_adx(high_prices, low_prices, close_prices, 14)
            current_adx = adx.iloc[-1] if not adx.empty else 25
            
            # Support and resistance levels
            recent_data = company_prices.tail(60)  # Last 3 months
            support_level = recent_data['low'].min() if 'low' in recent_data.columns else recent_data['close'].min()
            resistance_level = recent_data['high'].max() if 'high' in recent_data.columns else recent_data['close'].max()
            
            # Technical signals
            momentum_signal = _classify_momentum_signal(current_rsi, current_macd, current_macd_signal)
            trend_signal = _classify_trend_signal(price_vs_sma20, price_vs_sma50, current_adx)
            volatility_signal = _classify_volatility_signal(bb_position, atr_percentage)
            
            # Overall technical score
            technical_components = [
                _score_momentum(current_rsi, current_macd > current_macd_signal),
                _score_trend(price_vs_sma20, price_vs_sma50),
                _score_volatility(atr_percentage, bb_position),
                min(10, current_adx / 5)  # Trend strength component
            ]
            
            technical_score = np.mean([comp for comp in technical_components if comp >= 0])
            
            technical_analysis[company_name] = {
                'current_price': current_price,
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'price_vs_sma20': price_vs_sma20,
                'price_vs_sma50': price_vs_sma50,
                'bollinger_position': bb_position,
                'atr_percentage': atr_percentage,
                'volume_ratio': current_volume_ratio,
                'adx': current_adx,
                'support_level': support_level,
                'resistance_level': resistance_level,
                'momentum_signal': momentum_signal,
                'trend_signal': trend_signal,
                'volatility_signal': volatility_signal,
                'technical_score': technical_score
            }
            
        except Exception as e:
            logger.warning(f"Technical analysis failed for {company_name}: {e}")
            continue
    
    return technical_analysis


# Technical indicator calculation helpers
def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI indicator"""
    delta = prices.diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD indicator"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal).mean()
    macd_histogram = macd_line - macd_signal
    
    return macd_line, macd_signal, macd_histogram


def _calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def _calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average Directional Index"""
    tr = _calculate_atr(high, low, close, period)
    
    dm_plus = high.diff()
    dm_minus = low.diff() * -1
    
    dm_plus = dm_plus.where((dm_plus > dm_minus) & (dm_plus > 0), 0)
    dm_minus = dm_minus.where((dm_minus > dm_plus) & (dm_minus > 0), 0)
    
    di_plus = (dm_plus.rolling(window=period).mean() / tr) * 100
    di_minus = (dm_minus.rolling(window=period).mean() / tr) * 100
    
    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100
    adx = dx.rolling(window=period).mean()
    
    return adx.fillna(25)


# Signal classification helpers
def _classify_momentum_signal(rsi: float, macd: float, macd_signal: float) -> str:
    """Classify momentum signal"""
    if rsi > 70 and macd < macd_signal:
        return "Overbought"
    elif rsi < 30 and macd > macd_signal:
        return "Oversold"
    elif macd > macd_signal and rsi > 50:
        return "Bullish Momentum"
    elif macd < macd_signal and rsi < 50:
        return "Bearish Momentum"
    else:
        return "Neutral"


def _classify_trend_signal(price_vs_sma20: float, price_vs_sma50: float, adx: float) -> str:
    """Classify trend signal"""
    if price_vs_sma20 > 2 and price_vs_sma50 > 2 and adx > 25:
        return "Strong Uptrend"
    elif price_vs_sma20 < -2 and price_vs_sma50 < -2 and adx > 25:
        return "Strong Downtrend"
    elif price_vs_sma20 > 0 and price_vs_sma50 > 0:
        return "Uptrend"
    elif price_vs_sma20 < 0 and price_vs_sma50 < 0:
        return "Downtrend"
    else:
        return "Sideways"


def _classify_volatility_signal(bb_position: float, atr_percentage: float) -> str:
    """Classify volatility signal"""
    if bb_position > 0.8 and atr_percentage > 3:
        return "High Vol Breakout"
    elif bb_position < 0.2 and atr_percentage > 3:
        return "High Vol Breakdown"
    elif atr_percentage > 4:
        return "High Volatility"
    elif atr_percentage < 1.5:
        return "Low Volatility"
    else:
        return "Normal Volatility"


# Scoring helpers
def _score_momentum(rsi: float, macd_bullish: bool) -> float:
    """Score momentum component"""
    rsi_score = 10 - abs(rsi - 50) / 5
    macd_score = 7 if macd_bullish else 3
    return (rsi_score + macd_score) / 2


def _score_trend(price_vs_sma20: float, price_vs_sma50: float) -> float:
    """Score trend component"""
    sma20_score = min(10, max(0, 5 + price_vs_sma20))
    sma50_score = min(10, max(0, 5 + price_vs_sma50))
    return (sma20_score + sma50_score) / 2


def _score_volatility(atr_percentage: float, bb_position: float) -> float:
    """Score volatility component"""
    atr_score = max(0, 10 - atr_percentage * 2)
    bb_score = max(0, 10 - abs(bb_position - 0.5) * 20)
    return (atr_score + bb_score) / 2


def _create_technical_table(technical_analysis: Dict[str, Dict]) -> str:
    """Create technical analysis table"""
    
    if not technical_analysis:
        return build_info_box("No technical data available.", "warning")
    
    # Prepare DataFrame
    rows = []
    for company_name, analysis in technical_analysis.items():
        # Determine overall signal
        if analysis['technical_score'] >= 7:
            overall_signal = "Strong Buy"
        elif analysis['technical_score'] >= 5.5:
            overall_signal = "Buy"
        elif analysis['technical_score'] >= 4.5:
            overall_signal = "Hold"
        elif analysis['technical_score'] >= 3:
            overall_signal = "Sell"
        else:
            overall_signal = "Strong Sell"
        
        rows.append({
            'Company': company_name,
            'Current Price': f"${analysis['current_price']:.2f}",
            'RSI': f"{analysis['rsi']:.1f}",
            'MACD Signal': analysis['momentum_signal'][:12],
            'Trend Signal': analysis['trend_signal'][:12],
            'Price vs SMA20': f"{analysis['price_vs_sma20']:.1f}%",
            'Volatility': analysis['volatility_signal'][:12],
            'ADX': f"{analysis['adx']:.1f}",
            'Technical Score': f"{analysis['technical_score']:.1f}/10",
            'Overall Signal': overall_signal
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by technical score
    tech_scores = [analysis['technical_score'] for analysis in technical_analysis.values()]
    sorted_indices = sorted(range(len(tech_scores)), key=lambda i: tech_scores[i], reverse=True)
    
    df_sorted = df.iloc[sorted_indices].reset_index(drop=True)
    
    return build_data_table(df_sorted, table_id="technical-table")


def _generate_technical_summary(technical_analysis: Dict[str, Dict]) -> str:
    """Generate technical analysis summary cards"""
    
    total_companies = len(technical_analysis)
    
    if total_companies == 0:
        return build_info_box("No technical analysis available.", "warning")
    
    # Portfolio technical statistics
    avg_technical_score = np.mean([analysis['technical_score'] for analysis in technical_analysis.values()])
    strong_signals = sum(1 for analysis in technical_analysis.values() if analysis['technical_score'] >= 7)
    avg_rsi = np.mean([analysis['rsi'] for analysis in technical_analysis.values()])
    avg_adx = np.mean([analysis['adx'] for analysis in technical_analysis.values()])
    
    # Signal distribution
    bullish_momentum = sum(1 for analysis in technical_analysis.values() if 'Bullish' in analysis['momentum_signal'])
    
    cards = [
        {
            "label": "Portfolio Technical Score",
            "value": f"{avg_technical_score:.1f}/10",
            "description": f"{strong_signals}/{total_companies} companies with strong signals ({(strong_signals/total_companies)*100:.0f}%)",
            "type": "success" if avg_technical_score >= 7 else "info" if avg_technical_score >= 5 else "warning"
        },
        {
            "label": "Momentum Assessment",
            "value": f"{avg_rsi:.1f} RSI",
            "description": f"{bullish_momentum}/{total_companies} showing bullish momentum",
            "type": "success" if bullish_momentum >= total_companies * 0.5 else "info"
        },
        {
            "label": "Trend Strength",
            "value": f"{avg_adx:.1f} ADX",
            "description": "Average directional movement",
            "type": "success" if avg_adx > 25 else "info"
        },
        {
            "label": "Portfolio Momentum",
            "value": 'Strong Bullish' if bullish_momentum >= total_companies * 0.6 and avg_rsi > 55 else 'Moderate' if bullish_momentum >= total_companies * 0.4 else 'Mixed',
            "description": "Across portfolio holdings",
            "type": "success" if bullish_momentum >= total_companies * 0.6 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_technical_charts(technical_analysis: Dict) -> List[str]:
    """Create 4 standalone technical analysis charts"""
    
    if not technical_analysis:
        return []
    
    import plotly.graph_objects as go
    
    companies_list = list(technical_analysis.keys())
    charts = []
    
    # Chart 1: RSI vs MACD Signal Analysis (colored by momentum signal)
    rsi_values = [analysis['rsi'] for analysis in technical_analysis.values()]
    macd_values = [analysis['macd'] for analysis in technical_analysis.values()]
    
    # Color by momentum signal
    signal_colors = []
    for analysis in technical_analysis.values():
        if 'Bullish' in analysis['momentum_signal']:
            signal_colors.append('green')
        elif 'Bearish' in analysis['momentum_signal']:
            signal_colors.append('red')
        else:
            signal_colors.append('gray')
    
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=rsi_values,
            y=macd_values,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color=signal_colors),
            hovertemplate='<b>%{text}</b><br>RSI: %{x:.1f}<br>MACD: %{y:.2f}<extra></extra>'
        )
    )
    # Add reference lines
    fig1.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3)
    fig1.add_vline(x=30, line_dash="dash", line_color="red", opacity=0.5)
    fig1.add_vline(x=70, line_dash="dash", line_color="red", opacity=0.5)
    
    fig1.update_layout(
        title="RSI vs MACD Signal Analysis (Green=Bullish, Red=Bearish)",
        xaxis_title="RSI",
        yaxis_title="MACD",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig1.to_dict(), div_id="technical-chart-1", height=500))
    
    # Chart 2: Technical Score vs Price Performance
    technical_scores = [analysis['technical_score'] for analysis in technical_analysis.values()]
    price_vs_sma20 = [analysis['price_vs_sma20'] for analysis in technical_analysis.values()]
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=technical_scores,
            y=price_vs_sma20,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color=technical_scores, colorscale='RdYlGn',
                       showscale=True, colorbar=dict(title="Score")),
            hovertemplate='<b>%{text}</b><br>Technical Score: %{x:.1f}/10<br>Price vs SMA20: %{y:.1f}%<extra></extra>'
        )
    )
    fig2.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3)
    
    fig2.update_layout(
        title="Technical Quality vs Price Performance",
        xaxis_title="Technical Score (0-10)",
        yaxis_title="Price vs SMA20 (%)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig2.to_dict(), div_id="technical-chart-2", height=500))
    
    # Chart 3: ADX Trend Strength (Bar chart)
    adx_values = [analysis['adx'] for analysis in technical_analysis.values()]
    
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=[comp[:10] for comp in companies_list],
            y=adx_values,
            marker=dict(color=adx_values, colorscale='Viridis', showscale=True,
                       colorbar=dict(title="ADX")),
            hovertemplate='<b>%{x}</b><br>ADX: %{y:.1f}<extra></extra>'
        )
    )
    fig3.add_hline(y=25, line_dash="dash", line_color="red", opacity=0.7,
                   annotation_text="Strong Trend Threshold")
    
    fig3.update_layout(
        title="Directional Trend Strength Analysis (ADX)",
        xaxis_title="Companies",
        yaxis_title="ADX (Trend Strength)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig3.to_dict(), div_id="technical-chart-3", height=500))
    
    # Chart 4: Technical Signal Distribution
    momentum_signals = [analysis['momentum_signal'] for analysis in technical_analysis.values()]
    signal_counts = {}
    
    for signal in momentum_signals:
        signal_counts[signal] = signal_counts.get(signal, 0) + 1
    
    fig4 = go.Figure()
    fig4.add_trace(
        go.Pie(
            labels=list(signal_counts.keys()),
            values=list(signal_counts.values()),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    )
    fig4.update_layout(
        title="Technical Signal Distribution",
        height=500,
        showlegend=True
    )
    charts.append(build_plotly_chart(fig4.to_dict(), div_id="technical-chart-4", height=500))
    
    return charts


# =============================================================================
# VOLATILITY ANALYSIS FUNCTIONS
# =============================================================================

def _analyze_volatility_patterns(prices_df: pd.DataFrame, companies: Dict[str, str], 
                                technical_analysis: Dict) -> Dict[str, Dict]:
    """Analyze volatility patterns and clustering"""
    
    if prices_df.empty:
        return {}
    
    volatility_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get company prices
            if not prices_df.empty:
                price_matches = prices_df[prices_df['Company'] == company_name]
                company_prices = price_matches.copy()
            else:
                continue
            
            if len(company_prices) < 100:  # Need sufficient data
                continue
            
            company_prices = company_prices.sort_values('date').reset_index(drop=True)
            close_prices = company_prices['close']
            
            # Calculate returns
            returns = close_prices.pct_change().dropna()
            
            # Realized volatility metrics
            daily_vol = returns.std()
            annualized_vol = daily_vol * np.sqrt(252) * 100
            
            # Rolling volatility analysis
            vol_20d = returns.rolling(window=20).std() * np.sqrt(252) * 100
            vol_60d = returns.rolling(window=60).std() * np.sqrt(252) * 100
            
            current_vol_20d = vol_20d.iloc[-1] if not vol_20d.empty else annualized_vol
            current_vol_60d = vol_60d.iloc[-1] if not vol_60d.empty else annualized_vol
            
            # Volatility regime analysis
            vol_percentile_20d = (vol_20d.rank(pct=True).iloc[-1] * 100) if not vol_20d.empty else 50
            vol_regime = _classify_volatility_regime(vol_percentile_20d)
            
            # Volatility clustering
            vol_clustering_score = _calculate_volatility_clustering(returns)
            
            # Skewness and kurtosis
            returns_skewness = returns.skew()
            returns_kurtosis = returns.kurtosis()
            
            # Downside deviation
            negative_returns = returns[returns < 0]
            downside_deviation = negative_returns.std() * np.sqrt(252) * 100 if len(negative_returns) > 0 else 0
            
            # Volatility stability metrics
            vol_of_vol = vol_20d.std() if not vol_20d.empty else 0
            vol_stability_score = max(0, 10 - vol_of_vol * 2)
            
            # VaR estimates (parametric)
            var_95 = returns.quantile(0.05) * 100
            var_99 = returns.quantile(0.01) * 100
            
            # Volatility score components
            volatility_score_components = [
                max(0, 10 - (current_vol_20d - 15) / 5) if current_vol_20d > 15 else 10,
                vol_stability_score,
                max(0, 10 - abs(returns_skewness) * 3),
                max(0, 10 - max(0, returns_kurtosis - 3))
            ]
            
            volatility_quality_score = np.mean([comp for comp in volatility_score_components if comp >= 0])
            
            volatility_analysis[company_name] = {
                'annualized_volatility': annualized_vol,
                'current_vol_20d': current_vol_20d,
                'current_vol_60d': current_vol_60d,
                'vol_percentile': vol_percentile_20d,
                'vol_regime': vol_regime,
                'vol_clustering_score': vol_clustering_score,
                'returns_skewness': returns_skewness,
                'returns_kurtosis': returns_kurtosis,
                'downside_deviation': downside_deviation,
                'vol_stability_score': vol_stability_score,
                'var_95': var_95,
                'var_99': var_99,
                'volatility_quality_score': volatility_quality_score
            }
            
        except Exception as e:
            logger.warning(f"Volatility analysis failed for {company_name}: {e}")
            continue
    
    return volatility_analysis


def _classify_volatility_regime(vol_percentile: float) -> str:
    """Classify current volatility regime"""
    if vol_percentile >= 80:
        return "High Vol Regime"
    elif vol_percentile >= 60:
        return "Elevated Vol"
    elif vol_percentile >= 40:
        return "Normal Vol"
    elif vol_percentile >= 20:
        return "Low Vol"
    else:
        return "Very Low Vol"


def _calculate_volatility_clustering(returns: pd.Series) -> float:
    """Calculate volatility clustering score"""
    try:
        abs_returns = returns.abs()
        clustering_score = abs_returns.autocorr(lag=1)
        return max(0, min(10, clustering_score * 10)) if not pd.isna(clustering_score) else 5
    except:
        return 5


def _create_volatility_table(volatility_analysis: Dict[str, Dict]) -> str:
    """Create volatility analysis table"""
    
    if not volatility_analysis:
        return build_info_box("No volatility data available.", "warning")
    
    # Prepare DataFrame
    rows = []
    for company_name, analysis in volatility_analysis.items():
        rows.append({
            'Company': company_name,
            'Annualized Vol (%)': f"{analysis['annualized_volatility']:.1f}",
            '20D Vol (%)': f"{analysis['current_vol_20d']:.1f}",
            'Vol Regime': analysis['vol_regime'],
            'Skewness': f"{analysis['returns_skewness']:.2f}",
            'Downside Dev (%)': f"{analysis['downside_deviation']:.1f}",
            'VaR 95%': f"{analysis['var_95']:.2f}%",
            'Vol Quality': f"{analysis['volatility_quality_score']:.1f}/10",
            'Vol Rank': ''
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by volatility quality score
    vol_scores = [analysis['volatility_quality_score'] for analysis in volatility_analysis.values()]
    sorted_indices = sorted(range(len(vol_scores)), key=lambda i: vol_scores[i], reverse=True)
    
    df_sorted = df.iloc[sorted_indices].reset_index(drop=True)
    df_sorted['Vol Rank'] = [f"{i+1}/{len(df)}" for i in range(len(df))]
    
    return build_data_table(df_sorted, table_id="volatility-table")


def _generate_volatility_summary(volatility_analysis: Dict[str, Dict]) -> str:
    """Generate volatility analysis summary cards"""
    
    total_companies = len(volatility_analysis)
    
    if total_companies == 0:
        return build_info_box("No volatility analysis available.", "warning")
    
    # Portfolio volatility statistics
    avg_volatility = np.mean([analysis['annualized_volatility'] for analysis in volatility_analysis.values()])
    avg_vol_quality = np.mean([analysis['volatility_quality_score'] for analysis in volatility_analysis.values()])
    high_vol_regime = sum(1 for analysis in volatility_analysis.values() if 'High' in analysis['vol_regime'])
    avg_downside_dev = np.mean([analysis['downside_deviation'] for analysis in volatility_analysis.values()])
    
    cards = [
        {
            "label": "Portfolio Volatility",
            "value": f"{avg_volatility:.1f}%",
            "description": f"Annualized with {avg_vol_quality:.1f}/10 quality score",
            "type": "success" if avg_volatility < 20 else "info" if avg_volatility < 30 else "warning"
        },
        {
            "label": "Volatility Regime",
            "value": f"{high_vol_regime}/{total_companies}",
            "description": "Companies in elevated/high volatility regimes",
            "type": "success" if high_vol_regime <= total_companies * 0.3 else "warning"
        },
        {
            "label": "Downside Risk",
            "value": f"{avg_downside_dev:.1f}%",
            "description": "Average downside deviation indicating tail risk",
            "type": "success" if avg_downside_dev < avg_volatility * 0.8 else "info"
        },
        {
            "label": "Risk Environment",
            "value": 'Favorable' if avg_volatility < 20 and high_vol_regime <= total_companies * 0.3 else 'Moderate' if avg_volatility < 30 else 'Elevated',
            "description": "For risk management",
            "type": "success" if avg_volatility < 20 else "info"
        }
    ]
    
    return build_stat_grid(cards)


def _create_volatility_charts(volatility_analysis: Dict) -> List[str]:
    """Create 4 standalone volatility analysis charts"""
    
    if not volatility_analysis:
        return []
    
    import plotly.graph_objects as go
    
    companies_list = list(volatility_analysis.keys())
    charts = []
    
    # Chart 1: Volatility vs Quality Score
    vol_20d = [analysis['current_vol_20d'] for analysis in volatility_analysis.values()]
    vol_quality = [analysis['volatility_quality_score'] for analysis in volatility_analysis.values()]
    
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=vol_20d,
            y=vol_quality,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color=vol_quality, colorscale='RdYlGn',
                       showscale=True, colorbar=dict(title="Quality")),
            hovertemplate='<b>%{text}</b><br>20D Vol: %{x:.1f}%<br>Quality: %{y:.1f}/10<extra></extra>'
        )
    )
    fig1.update_layout(
        title="Volatility Profile Analysis",
        xaxis_title="20-Day Volatility (%)",
        yaxis_title="Volatility Quality Score (0-10)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig1.to_dict(), div_id="volatility-chart-1", height=500))
    
    # Chart 2: Risk Asymmetry Analysis
    annualized_vol = [analysis['annualized_volatility'] for analysis in volatility_analysis.values()]
    downside_dev = [analysis['downside_deviation'] for analysis in volatility_analysis.values()]
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=annualized_vol,
            y=downside_dev,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color='#ef4444'),
            hovertemplate='<b>%{text}</b><br>Annualized Vol: %{x:.1f}%<br>Downside Dev: %{y:.1f}%<extra></extra>'
        )
    )
    # Add diagonal reference line
    max_vol = max(max(annualized_vol) if annualized_vol else 50, max(downside_dev) if downside_dev else 50)
    fig2.add_trace(
        go.Scatter(
            x=[0, max_vol],
            y=[0, max_vol],
            mode='lines',
            line=dict(color='red', dash='dash', width=1),
            name='Equal Up/Down Vol',
            showlegend=True
        )
    )
    
    fig2.update_layout(
        title="Risk Asymmetry Analysis (Annualized vs Downside)",
        xaxis_title="Annualized Volatility (%)",
        yaxis_title="Downside Deviation (%)",
        height=500
    )
    charts.append(build_plotly_chart(fig2.to_dict(), div_id="volatility-chart-2", height=500))
    
    # Chart 3: VaR Analysis (Bar chart)
    var_95_values = [analysis['var_95'] for analysis in volatility_analysis.values()]
    
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=[comp[:10] for comp in companies_list],
            y=var_95_values,
            marker=dict(color=var_95_values, colorscale='Reds_r', showscale=True,
                       colorbar=dict(title="VaR")),
            hovertemplate='<b>%{x}</b><br>VaR 95%%: %{y:.2f}%%<extra></extra>'
        )
    )
    fig3.update_layout(
        title="Value at Risk Assessment (95% Daily)",
        xaxis_title="Companies",
        yaxis_title="VaR 95% (Daily %)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig3.to_dict(), div_id="volatility-chart-3", height=500))
    
    # Chart 4: Volatility Regime Distribution
    vol_regimes = [analysis['vol_regime'] for analysis in volatility_analysis.values()]
    regime_counts = {}
    
    for regime in vol_regimes:
        regime_counts[regime] = regime_counts.get(regime, 0) + 1
    
    fig4 = go.Figure()
    fig4.add_trace(
        go.Pie(
            labels=list(regime_counts.keys()),
            values=list(regime_counts.values()),
            marker=dict(colors=['#ef4444', '#f59e0b', '#fbbf24', '#84cc16', '#10b981'][:len(regime_counts)]),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    )
    fig4.update_layout(
        title="Volatility Regime Distribution",
        height=500,
        showlegend=True
    )
    charts.append(build_plotly_chart(fig4.to_dict(), div_id="volatility-chart-4", height=500))
    
    return charts


"""
Section 15: Market Microstructure Analysis
Phase 3: Price Discovery Efficiency & Comprehensive Dashboard

This artifact contains ONLY the new Phase 3 functions to be added to the existing code.
Replace the stub functions and add these new functions to section_15.py.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# REPLACE _build_section_15c_stub() WITH THIS
# =============================================================================

def _build_section_15c(price_discovery_analysis: Dict, companies: Dict) -> str:
    """Build Section 15C: Price Discovery Efficiency & Analyst Target Convergence"""
    
    html_parts = []
    
    html_parts.append('<div class="info-section">')
    html_parts.append('<h3>15C. Price Discovery Efficiency & Analyst Target Convergence</h3>')
    
    # 15C.1: Market Efficiency & Price Discovery Analysis
    html_parts.append(_build_price_discovery_section(price_discovery_analysis, companies))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_price_discovery_section(price_discovery_analysis: Dict, companies: Dict) -> str:
    """Build 15C.1: Market Efficiency & Price Discovery Analysis"""
    
    if not price_discovery_analysis:
        return build_info_box("Price discovery analysis unavailable due to insufficient analyst data.", "warning")
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15C.1 Market Efficiency & Price Discovery Analysis</h4>')
    
    # Summary cards
    discovery_summary = _generate_price_discovery_summary(price_discovery_analysis)
    html_parts.append(discovery_summary)
    
    # Price discovery table
    html_parts.append('<h4>Price Discovery Analysis by Company</h4>')
    discovery_table = _create_price_discovery_table(price_discovery_analysis)
    html_parts.append(discovery_table)
    
    # Price discovery charts (4 standalone charts)
    discovery_charts = _create_price_discovery_charts(price_discovery_analysis)
    for chart in discovery_charts:
        if chart:
            html_parts.append(chart)
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


# =============================================================================
# REPLACE _build_section_15d_stub() WITH THIS
# =============================================================================

def _build_section_15d(liquidity_analysis: Dict, technical_analysis: Dict, 
                      volatility_analysis: Dict, price_discovery_analysis: Dict,
                      companies: Dict) -> str:
    """Build Section 15D: Market Microstructure Visualization Analysis"""
    
    html_parts = []
    
    html_parts.append('<div class="info-section">')
    html_parts.append('<h3>15D. Market Microstructure Visualization Analysis</h3>')
    html_parts.append('<p>Comprehensive visualization dashboard integrating liquidity, technical, volatility, and price discovery intelligence.</p>')
    
    # Create comprehensive dashboard chart
    dashboard_chart = _create_microstructure_dashboard(
        liquidity_analysis, technical_analysis, volatility_analysis, 
        price_discovery_analysis, companies
    )
    
    if dashboard_chart:
        html_parts.append(dashboard_chart)
    else:
        html_parts.append(build_info_box("Dashboard unavailable due to insufficient data.", "warning"))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


# =============================================================================
# PRICE DISCOVERY ANALYSIS FUNCTIONS
# =============================================================================

def _analyze_price_discovery(prices_df: pd.DataFrame, analyst_targets: pd.DataFrame, 
                           profiles_df: pd.DataFrame, companies: Dict[str, str]) -> Dict[str, Dict]:
    """Analyze price discovery efficiency and analyst target convergence"""
    
    if prices_df.empty or analyst_targets.empty:
        return {}
    
    price_discovery_analysis = {}
    
    for company_name, ticker in companies.items():
        try:
            # Get current price
            if not profiles_df.empty:
                profile_matches = profiles_df[profiles_df['Company'] == company_name]
                company_profile = profile_matches.iloc[0] if len(profile_matches) > 0 else None
            else:
                company_profile = None
            
            current_price = company_profile.get('price', 0) if company_profile is not None else 0
            
            if current_price <= 0:
                continue
            
            # Get analyst targets
            if not analyst_targets.empty:
                target_matches = analyst_targets[analyst_targets['Company'] == company_name]
                company_targets = target_matches
            else:
                continue
            
            if company_targets.empty:
                continue
            
            latest_targets = company_targets.iloc[-1]
            
            # Analyst target metrics
            target_high = latest_targets.get('targetHigh', current_price)
            target_low = latest_targets.get('targetLow', current_price)
            target_consensus = latest_targets.get('targetConsensus', current_price)
            target_median = latest_targets.get('targetMedian', current_price)
            
            # Price discovery metrics
            upside_to_consensus = _safe_divide(target_consensus - current_price, current_price) * 100
            upside_to_high = _safe_divide(target_high - current_price, current_price) * 100
            downside_to_low = _safe_divide(current_price - target_low, current_price) * 100
            
            # Analyst dispersion
            if target_high > target_low and target_low > 0:
                target_range = _safe_divide(target_high - target_low, target_consensus) * 100
            else:
                target_range = 0
            
            # Price efficiency metrics
            if target_high > target_low and target_low > 0:
                price_position_in_range = _safe_divide(current_price - target_low, target_high - target_low)
            else:
                price_position_in_range = 0.5
            
            # Consensus accuracy proxy
            consensus_deviation = abs(upside_to_consensus)
            
            # Get price momentum for context
            company_prices = prices_df[prices_df['Company'] == company_name].tail(60)
            if not company_prices.empty and len(company_prices) > 0:
                price_momentum_60d = _safe_divide(current_price - company_prices['close'].iloc[0], company_prices['close'].iloc[0]) * 100
                price_volatility_60d = company_prices['close'].pct_change().std() * np.sqrt(252) * 100
            else:
                price_momentum_60d = 0
                price_volatility_60d = 20
            
            # Price discovery efficiency score
            efficiency_components = [
                max(0, 10 - target_range / 10),
                max(0, 10 - consensus_deviation / 5),
                min(10, abs(price_momentum_60d) / 5) if abs(price_momentum_60d) < 50 else 5,
                max(0, 10 - price_volatility_60d / 5)
            ]
            
            discovery_efficiency_score = np.mean([comp for comp in efficiency_components if comp >= 0])
            
            # Classification
            if discovery_efficiency_score >= 7 and consensus_deviation < 10:
                efficiency_class = "Highly Efficient"
            elif discovery_efficiency_score >= 5 and consensus_deviation < 20:
                efficiency_class = "Moderately Efficient"
            else:
                efficiency_class = "Less Efficient"
            
            price_discovery_analysis[company_name] = {
                'current_price': current_price,
                'target_consensus': target_consensus,
                'target_high': target_high,
                'target_low': target_low,
                'upside_to_consensus': upside_to_consensus,
                'upside_to_high': upside_to_high,
                'downside_to_low': downside_to_low,
                'target_range': target_range,
                'price_position_in_range': price_position_in_range,
                'consensus_deviation': consensus_deviation,
                'price_momentum_60d': price_momentum_60d,
                'discovery_efficiency_score': discovery_efficiency_score,
                'efficiency_class': efficiency_class
            }
            
        except Exception as e:
            logger.warning(f"Price discovery analysis failed for {company_name}: {e}")
            continue
    
    return price_discovery_analysis


def _create_price_discovery_table(price_discovery_analysis: Dict[str, Dict]) -> str:
    """Create price discovery analysis table"""
    
    if not price_discovery_analysis:
        return build_info_box("No price discovery data available.", "warning")
    
    # Prepare DataFrame
    rows = []
    for company_name, analysis in price_discovery_analysis.items():
        rows.append({
            'Company': company_name,
            'Current Price': f"${analysis['current_price']:.2f}",
            'Consensus Target': f"${analysis['target_consensus']:.2f}",
            'Upside to Consensus (%)': f"{analysis['upside_to_consensus']:.1f}",
            'Target Range (%)': f"{analysis['target_range']:.1f}",
            'Price Position': f"{analysis['price_position_in_range']:.2f}",
            'Efficiency Score': f"{analysis['discovery_efficiency_score']:.1f}/10",
            'Classification': analysis['efficiency_class'],
            'Efficiency Rank': ''
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by efficiency score
    efficiency_scores = [analysis['discovery_efficiency_score'] for analysis in price_discovery_analysis.values()]
    sorted_indices = sorted(range(len(efficiency_scores)), key=lambda i: efficiency_scores[i], reverse=True)
    
    df_sorted = df.iloc[sorted_indices].reset_index(drop=True)
    df_sorted['Efficiency Rank'] = [f"{i+1}/{len(df)}" for i in range(len(df))]
    
    return build_data_table(df_sorted, table_id="price-discovery-table")


def _generate_price_discovery_summary(price_discovery_analysis: Dict[str, Dict]) -> str:
    """Generate price discovery analysis summary cards"""
    
    total_companies = len(price_discovery_analysis)
    
    if total_companies == 0:
        return build_info_box("No price discovery analysis available.", "warning")
    
    # Portfolio price discovery statistics
    avg_efficiency_score = np.mean([analysis['discovery_efficiency_score'] for analysis in price_discovery_analysis.values()])
    highly_efficient = sum(1 for analysis in price_discovery_analysis.values() if analysis['efficiency_class'] == 'Highly Efficient')
    avg_upside = np.mean([analysis['upside_to_consensus'] for analysis in price_discovery_analysis.values()])
    avg_target_range = np.mean([analysis['target_range'] for analysis in price_discovery_analysis.values()])
    
    cards = [
        {
            "label": "Portfolio Discovery Profile",
            "value": f"{avg_efficiency_score:.1f}/10",
            "description": f"Efficiency score across {total_companies} companies with analyst coverage",
            "type": "success" if avg_efficiency_score >= 7 else "info" if avg_efficiency_score >= 5 else "warning"
        },
        {
            "label": "High Efficiency Distribution",
            "value": f"{highly_efficient}/{total_companies}",
            "description": f"Highly efficient price discovery ({(highly_efficient/total_companies)*100:.0f}%)",
            "type": "success" if highly_efficient >= total_companies * 0.6 else "info"
        },
        {
            "label": "Consensus Positioning",
            "value": f"{avg_upside:.1f}%",
            "description": "Average upside to analyst consensus targets",
            "type": "success" if abs(avg_upside) < 10 else "info"
        },
        {
            "label": "Analyst Uncertainty",
            "value": f"{avg_target_range:.1f}%",
            "description": "Average target range reflecting conviction levels",
            "type": "success" if avg_target_range < 30 else "info" if avg_target_range < 50 else "warning"
        }
    ]
    
    return build_stat_grid(cards)


def _create_price_discovery_charts(price_discovery_analysis: Dict) -> List[str]:
    """Create 4 standalone price discovery charts"""
    
    if not price_discovery_analysis:
        return []
    
    import plotly.graph_objects as go
    
    companies_list = list(price_discovery_analysis.keys())
    charts = []
    
    # Chart 1: Current vs Target Analysis
    current_prices = [analysis['current_price'] for analysis in price_discovery_analysis.values()]
    target_prices = [analysis['target_consensus'] for analysis in price_discovery_analysis.values()]
    
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=current_prices,
            y=target_prices,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color='#3b82f6'),
            hovertemplate='<b>%{text}</b><br>Current: $%{x:.2f}<br>Target: $%{y:.2f}<extra></extra>'
        )
    )
    # Add diagonal reference line
    max_price = max(max(current_prices) if current_prices else 100, max(target_prices) if target_prices else 100)
    fig1.add_trace(
        go.Scatter(
            x=[0, max_price],
            y=[0, max_price],
            mode='lines',
            line=dict(color='red', dash='dash', width=1),
            name='Current = Target',
            showlegend=True
        )
    )
    
    fig1.update_layout(
        title="Current Price vs Analyst Targets",
        xaxis_title="Current Price ($)",
        yaxis_title="Analyst Target ($)",
        height=500
    )
    charts.append(build_plotly_chart(fig1.to_dict(), div_id="discovery-chart-1", height=500))
    
    # Chart 2: Upside Potential vs Market Efficiency
    upside_values = [analysis['upside_to_consensus'] for analysis in price_discovery_analysis.values()]
    efficiency_scores = [analysis['discovery_efficiency_score'] for analysis in price_discovery_analysis.values()]
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=upside_values,
            y=efficiency_scores,
            mode='markers+text',
            text=[comp[:8] for comp in companies_list],
            textposition='top center',
            marker=dict(size=12, color=efficiency_scores, colorscale='RdYlGn',
                       showscale=True, colorbar=dict(title="Efficiency")),
            hovertemplate='<b>%{text}</b><br>Upside: %{x:.1f}%%<br>Efficiency: %{y:.1f}/10<extra></extra>'
        )
    )
    fig2.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.3)
    
    fig2.update_layout(
        title="Upside Potential vs Market Efficiency",
        xaxis_title="Upside to Consensus (%)",
        yaxis_title="Discovery Efficiency Score (0-10)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig2.to_dict(), div_id="discovery-chart-2", height=500))
    
    # Chart 3: Target Range Analysis (Bar chart)
    target_ranges = [analysis['target_range'] for analysis in price_discovery_analysis.values()]
    
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=[comp[:10] for comp in companies_list],
            y=target_ranges,
            marker=dict(color=target_ranges, colorscale='Reds', showscale=True,
                       colorbar=dict(title="Range %")),
            hovertemplate='<b>%{x}</b><br>Target Range: %{y:.1f}%%<extra></extra>'
        )
    )
    fig3.update_layout(
        title="Analyst Conviction Analysis (Target Range)",
        xaxis_title="Companies",
        yaxis_title="Analyst Target Range (%)",
        height=500,
        showlegend=False
    )
    charts.append(build_plotly_chart(fig3.to_dict(), div_id="discovery-chart-3", height=500))
    
    # Chart 4: Efficiency Classification Distribution
    efficiency_classes = [analysis['efficiency_class'] for analysis in price_discovery_analysis.values()]
    class_counts = {}
    
    for eff_class in efficiency_classes:
        class_counts[eff_class] = class_counts.get(eff_class, 0) + 1
    
    fig4 = go.Figure()
    fig4.add_trace(
        go.Pie(
            labels=list(class_counts.keys()),
            values=list(class_counts.values()),
            marker=dict(colors=['#10b981', '#f59e0b', '#ef4444'][:len(class_counts)]),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    )
    fig4.update_layout(
        title="Price Discovery Efficiency Distribution",
        height=500,
        showlegend=True
    )
    charts.append(build_plotly_chart(fig4.to_dict(), div_id="discovery-chart-4", height=500))
    
    return charts


# =============================================================================
# COMPREHENSIVE MICROSTRUCTURE DASHBOARD
# =============================================================================

def _create_microstructure_dashboard(liquidity_analysis: Dict, technical_analysis: Dict,
                                    volatility_analysis: Dict, price_discovery_analysis: Dict,
                                    companies: Dict) -> str:
    """Create comprehensive market microstructure intelligence dashboard"""
    
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Calculate portfolio-level metrics
    if liquidity_analysis:
        avg_liquidity_score = np.mean([a['liquidity_score'] for a in liquidity_analysis.values()])
    else:
        avg_liquidity_score = 5
    
    if technical_analysis:
        avg_technical_score = np.mean([a['technical_score'] for a in technical_analysis.values()])
    else:
        avg_technical_score = 5
    
    if volatility_analysis:
        avg_volatility_quality = np.mean([a['volatility_quality_score'] for a in volatility_analysis.values()])
    else:
        avg_volatility_quality = 5
    
    if price_discovery_analysis:
        avg_discovery_efficiency = np.mean([a['discovery_efficiency_score'] for a in price_discovery_analysis.values()])
    else:
        avg_discovery_efficiency = 5
    
    # Create subplots for dashboard (this is the ONE exception where we use subplots for a comprehensive view)
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            'Portfolio Microstructure Scores',
            'Liquidity vs Technical Quality',
            'Portfolio Intelligence Score',
            'Quality Distribution',
            'Volatility vs Discovery Efficiency',
            'Risk-Return Profile'
        ),
        specs=[
            [{"type": "bar", "colspan": 2}, None, {"type": "indicator"}],
            [{"type": "pie", "colspan": 1}, {"type": "scatter", "colspan": 2}, None],
            [{"type": "scatter", "colspan": 3}, None, None]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Chart 1: Portfolio Summary Metrics (Bar chart)
    metrics = ['Liquidity\nQuality', 'Technical\nSignals', 'Volatility\nManagement', 'Price\nDiscovery']
    values = [avg_liquidity_score, avg_technical_score, avg_volatility_quality, avg_discovery_efficiency]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    fig.add_trace(
        go.Bar(
            x=metrics,
            y=values,
            marker=dict(color=colors),
            text=[f'{v:.1f}' for v in values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}/10<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Chart 2: Portfolio Intelligence Score (Gauge)
    portfolio_intelligence_score = np.mean([avg_liquidity_score, avg_technical_score, 
                                           avg_volatility_quality, avg_discovery_efficiency])
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=portfolio_intelligence_score,
            title={'text': "Portfolio<br>Score", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': '#667eea'},
                'steps': [
                    {'range': [0, 5], 'color': '#fecaca'},
                    {'range': [5, 7], 'color': '#fde68a'},
                    {'range': [7, 10], 'color': '#bbf7d0'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 7
                }
            }
        ),
        row=1, col=3
    )
    
    # Chart 3: Quality Distribution (Pie)
    if liquidity_analysis and technical_analysis:
        quality_scores = []
        quality_scores.extend([a['liquidity_score'] for a in liquidity_analysis.values()])
        quality_scores.extend([a['technical_score'] for a in technical_analysis.values()])
        
        high_quality = sum(1 for score in quality_scores if score >= 7)
        moderate_quality = sum(1 for score in quality_scores if 5 <= score < 7)
        low_quality = len(quality_scores) - high_quality - moderate_quality
        
        fig.add_trace(
            go.Pie(
                labels=['High Quality', 'Moderate Quality', 'Low Quality'],
                values=[high_quality, moderate_quality, low_quality],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>',
                showlegend=True
            ),
            row=2, col=1
        )
    
    # Chart 4: Liquidity vs Technical Quality (Scatter)
    if liquidity_analysis and technical_analysis:
        common_companies = [comp for comp in liquidity_analysis.keys() if comp in technical_analysis]
        
        if common_companies:
            liq_scores = [liquidity_analysis[comp]['liquidity_score'] for comp in common_companies]
            tech_scores = [technical_analysis[comp]['technical_score'] for comp in common_companies]
            
            fig.add_trace(
                go.Scatter(
                    x=liq_scores,
                    y=tech_scores,
                    mode='markers+text',
                    text=[comp[:8] for comp in common_companies],
                    textposition='top center',
                    marker=dict(size=10, color='#3b82f6'),
                    hovertemplate='<b>%{text}</b><br>Liquidity: %{x:.1f}<br>Technical: %{y:.1f}<extra></extra>',
                    showlegend=False
                ),
                row=2, col=2
            )
    
    # Chart 5: Volatility vs Discovery Efficiency (Scatter)
    if volatility_analysis and price_discovery_analysis:
        common_vol_disc = [comp for comp in volatility_analysis.keys() if comp in price_discovery_analysis]
        
        if common_vol_disc:
            vol_scores = [volatility_analysis[comp]['volatility_quality_score'] for comp in common_vol_disc]
            disc_scores = [price_discovery_analysis[comp]['discovery_efficiency_score'] for comp in common_vol_disc]
            
            # Color by volatility regime
            vol_regimes = [volatility_analysis[comp]['vol_regime'] for comp in common_vol_disc]
            regime_colors = {'Very Low Vol': '#10b981', 'Low Vol': '#84cc16', 'Normal Vol': '#fbbf24', 
                           'Elevated Vol': '#f59e0b', 'High Vol Regime': '#ef4444'}
            scatter_colors = [regime_colors.get(regime, 'gray') for regime in vol_regimes]
            
            fig.add_trace(
                go.Scatter(
                    x=vol_scores,
                    y=disc_scores,
                    mode='markers+text',
                    text=[comp[:8] for comp in common_vol_disc],
                    textposition='top center',
                    marker=dict(size=10, color=scatter_colors),
                    hovertemplate='<b>%{text}</b><br>Vol Quality: %{x:.1f}<br>Discovery: %{y:.1f}<extra></extra>',
                    showlegend=False
                ),
                row=3, col=1
            )
    
    # Update layout
    fig.update_xaxes(title_text="Score (0-10)", row=1, col=1)
    fig.update_yaxes(title_text="Score (0-10)", row=1, col=1)
    
    fig.update_xaxes(title_text="Liquidity Score", row=2, col=2)
    fig.update_yaxes(title_text="Technical Score", row=2, col=2)
    
    fig.update_xaxes(title_text="Volatility Quality Score", row=3, col=1)
    fig.update_yaxes(title_text="Price Discovery Efficiency", row=3, col=1)
    
    fig.update_layout(
        height=1200,
        title_text="Section 15D: Comprehensive Market Microstructure Intelligence Dashboard",
        title_x=0.5,
        title_font_size=18,
        showlegend=True
    )
    
    return build_plotly_chart(fig.to_dict(), div_id="microstructure-dashboard", height=1200)


"""
Section 15: Market Microstructure Analysis
Phase 4: Strategic Market Microstructure Intelligence Framework

This artifact contains ONLY the new Phase 4 functions to be added to the existing code.
Replace the stub function and add these new functions to section_15.py.
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# REPLACE _build_section_15e_stub() WITH THIS
# =============================================================================

def _build_section_15e(liquidity_analysis: Dict, float_analysis: Dict,
                      technical_analysis: Dict, volatility_analysis: Dict,
                      price_discovery_analysis: Dict, companies: Dict) -> str:
    """Build Section 15E: Strategic Market Microstructure Intelligence Framework"""
    
    # Generate comprehensive insights
    strategic_insights = _generate_comprehensive_microstructure_insights(
        liquidity_analysis, float_analysis, technical_analysis, 
        volatility_analysis, price_discovery_analysis, companies
    )
    
    html_parts = []
    
    html_parts.append('<div class="info-section">')
    html_parts.append('<h3>15E. Strategic Market Microstructure Intelligence Framework</h3>')
    html_parts.append('<p class="section-intro">Comprehensive strategic insights integrating liquidity, technical, volatility, and price discovery intelligence for portfolio optimization.</p>')
    
    # Build each strategic insight subsection with enhanced visual presentation
    html_parts.append(_build_liquidity_intelligence_section(strategic_insights))
    html_parts.append(build_section_divider())
    
    html_parts.append(_build_technical_strategy_section(strategic_insights))
    html_parts.append(build_section_divider())
    
    html_parts.append(_build_volatility_management_section(strategic_insights))
    html_parts.append(build_section_divider())
    
    html_parts.append(_build_price_discovery_optimization_section(strategic_insights))
    html_parts.append(build_section_divider())
    
    html_parts.append(_build_integrated_strategy_section(strategic_insights))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


# =============================================================================
# STRATEGIC INSIGHTS GENERATION
# =============================================================================

def _generate_comprehensive_microstructure_insights(
    liquidity_analysis: Dict, float_analysis: Dict, technical_analysis: Dict, 
    volatility_analysis: Dict, price_discovery_analysis: Dict, companies: Dict) -> Dict[str, any]:
    """Generate comprehensive market microstructure strategic insights"""
    
    total_companies = len(companies)
    
    # Calculate key metrics for each dimension
    if liquidity_analysis:
        avg_liquidity_score = np.mean([a['liquidity_score'] for a in liquidity_analysis.values()])
        high_liquidity = sum(1 for a in liquidity_analysis.values() if a['liquidity_class'] == 'High Liquidity')
        liquidity_count = len(liquidity_analysis)
    else:
        avg_liquidity_score = 5
        high_liquidity = 0
        liquidity_count = total_companies
    
    if technical_analysis:
        avg_technical_score = np.mean([a['technical_score'] for a in technical_analysis.values()])
        strong_signals = sum(1 for a in technical_analysis.values() if a['technical_score'] >= 7)
        technical_count = len(technical_analysis)
    else:
        avg_technical_score = 5
        strong_signals = 0
        technical_count = total_companies
    
    if volatility_analysis:
        avg_vol_quality = np.mean([a['volatility_quality_score'] for a in volatility_analysis.values()])
        low_vol_regime = sum(1 for a in volatility_analysis.values() if 'Low' in a['vol_regime'])
        volatility_count = len(volatility_analysis)
    else:
        avg_vol_quality = 5
        low_vol_regime = 0
        volatility_count = total_companies
    
    if price_discovery_analysis:
        avg_discovery_score = np.mean([a['discovery_efficiency_score'] for a in price_discovery_analysis.values()])
        efficient_discovery = sum(1 for a in price_discovery_analysis.values() if a['efficiency_class'] == 'Highly Efficient')
        discovery_count = len(price_discovery_analysis)
    else:
        avg_discovery_score = 5
        efficient_discovery = 0
        discovery_count = total_companies
    
    # Calculate overall portfolio intelligence score
    portfolio_intelligence_score = np.mean([avg_liquidity_score, avg_technical_score, 
                                           avg_vol_quality, avg_discovery_score])
    
    return {
        'avg_liquidity_score': avg_liquidity_score,
        'high_liquidity': high_liquidity,
        'liquidity_count': liquidity_count,
        'avg_technical_score': avg_technical_score,
        'strong_signals': strong_signals,
        'technical_count': technical_count,
        'avg_vol_quality': avg_vol_quality,
        'low_vol_regime': low_vol_regime,
        'volatility_count': volatility_count,
        'avg_discovery_score': avg_discovery_score,
        'efficient_discovery': efficient_discovery,
        'discovery_count': discovery_count,
        'portfolio_intelligence_score': portfolio_intelligence_score
    }


# =============================================================================
# ENHANCED VISUAL PRESENTATION SECTIONS
# =============================================================================

def _build_liquidity_intelligence_section(insights: Dict) -> str:
    """Build 15E.1: Liquidity Intelligence & Trading Optimization"""
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15E.1 Liquidity Intelligence & Trading Optimization</h4>')
    
    # Summary stat cards
    liquidity_quality = (
        'Excellent' if insights['avg_liquidity_score'] >= 7 and insights['high_liquidity'] >= insights['liquidity_count'] * 0.6
        else 'Good' if insights['avg_liquidity_score'] >= 6
        else 'Mixed'
    )
    
    execution_capability = (
        'Superior' if insights['high_liquidity'] >= insights['liquidity_count'] * 0.6
        else 'Good' if insights['high_liquidity'] >= insights['liquidity_count'] * 0.4
        else 'Selective'
    )
    
    cards = [
        {
            "label": "📊 Liquidity Infrastructure",
            "value": f"{insights['avg_liquidity_score']:.1f}/10",
            "description": f"{liquidity_quality} liquidity profile",
            "type": "success" if insights['avg_liquidity_score'] >= 7 else "info"
        },
        {
            "label": "⚡ Execution Capability",
            "value": execution_capability,
            "description": f"{insights['high_liquidity']}/{insights['liquidity_count']} high-liquidity names",
            "type": "success" if insights['high_liquidity'] >= insights['liquidity_count'] * 0.6 else "info"
        },
        {
            "label": "🎯 Market Impact",
            "value": "Low" if insights['avg_liquidity_score'] >= 7 else "Standard" if insights['avg_liquidity_score'] >= 5.5 else "Enhanced",
            "description": "Expected execution impact",
            "type": "success" if insights['avg_liquidity_score'] >= 7 else "info"
        }
    ]
    
    html_parts.append(build_stat_grid(cards))
    
    # Strategic recommendations with priority indicators
    recommendations = [
        {
            "priority": "HIGH" if insights['avg_liquidity_score'] >= 7 else "MEDIUM",
            "title": "Execution Strategy Optimization",
            "insight": f"Deploy liquidity-aware allocation models with {'superior' if insights['avg_liquidity_score'] >= 7 else 'standard'} execution capabilities across {insights['high_liquidity']}/{insights['liquidity_count']} high-liquidity holdings.",
            "action": "Implement real-time execution optimization for enhanced portfolio performance."
        },
        {
            "priority": "MEDIUM",
            "title": "Market Impact Management",
            "insight": f"Portfolio exhibits {liquidity_quality.lower()} liquidity characteristics with {(insights['high_liquidity']/insights['liquidity_count']*100):.0f}% high-liquidity concentration.",
            "action": "Optimize position sizing and timing strategies to minimize market impact."
        },
        {
            "priority": "HIGH" if insights['high_liquidity'] >= insights['liquidity_count'] * 0.6 else "MEDIUM",
            "title": "Liquidity-Based Alpha Generation",
            "insight": "Leverage liquidity intelligence for tactical rebalancing and enhanced execution timing.",
            "action": "Deploy sophisticated liquidity-aware strategies for risk-adjusted outperformance."
        }
    ]
    
    html_parts.append(_build_action_priority_cards(recommendations))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_technical_strategy_section(insights: Dict) -> str:
    """Build 15E.2: Technical Analysis & Momentum Strategy Framework"""
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15E.2 Technical Analysis & Momentum Strategy Framework</h4>')
    
    # Summary stat cards
    momentum_quality = (
        'Strong Bullish' if insights['strong_signals'] >= insights['technical_count'] * 0.5 and insights['avg_technical_score'] >= 7
        else 'Moderate Positive' if insights['strong_signals'] >= insights['technical_count'] * 0.3
        else 'Mixed'
    )
    
    cards = [
        {
            "label": "📈 Technical Profile",
            "value": f"{insights['avg_technical_score']:.1f}/10",
            "description": f"{momentum_quality} momentum signals",
            "type": "success" if insights['avg_technical_score'] >= 7 else "info"
        },
        {
            "label": "🚀 Strong Signals",
            "value": f"{insights['strong_signals']}/{insights['technical_count']}",
            "description": f"Companies with conviction signals ({(insights['strong_signals']/insights['technical_count']*100):.0f}%)",
            "type": "success" if insights['strong_signals'] >= insights['technical_count'] * 0.5 else "info"
        },
        {
            "label": "🎪 Momentum Capture",
            "value": "High" if insights['avg_technical_score'] >= 7 else "Moderate" if insights['avg_technical_score'] >= 6 else "Limited",
            "description": "Tactical allocation opportunities",
            "type": "success" if insights['avg_technical_score'] >= 7 else "info"
        }
    ]
    
    html_parts.append(build_stat_grid(cards))
    
    # Strategic recommendations
    recommendations = [
        {
            "priority": "HIGH" if insights['strong_signals'] >= insights['technical_count'] * 0.5 else "MEDIUM",
            "title": "Signal-Based Allocation",
            "insight": f"Portfolio exhibits {momentum_quality.lower()} technical characteristics with {insights['strong_signals']}/{insights['technical_count']} high-conviction signals.",
            "action": "Implement systematic technical-driven strategies with quantitative signal validation."
        },
        {
            "priority": "HIGH" if insights['avg_technical_score'] >= 7 else "MEDIUM",
            "title": "Momentum Strategy Deployment",
            "insight": f"{'Strong' if insights['avg_technical_score'] >= 7 else 'Moderate'} momentum opportunities identified for tactical positioning.",
            "action": "Deploy momentum capture strategies with integrated risk management protocols."
        },
        {
            "priority": "MEDIUM",
            "title": "Technical Intelligence Integration",
            "insight": "Advanced technical framework combining momentum, trend, and volatility indicators.",
            "action": "Leverage systematic technical analysis for enhanced risk-adjusted returns."
        }
    ]
    
    html_parts.append(_build_action_priority_cards(recommendations))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_volatility_management_section(insights: Dict) -> str:
    """Build 15E.3: Volatility Management & Risk Assessment"""
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15E.3 Volatility Management & Risk Assessment</h4>')
    
    # Summary stat cards with progress indicators
    risk_environment = (
        'Favorable' if insights['avg_vol_quality'] >= 7 and insights['low_vol_regime'] >= insights['volatility_count'] * 0.4
        else 'Moderate' if insights['avg_vol_quality'] >= 6
        else 'Elevated'
    )
    
    cards = [
        {
            "label": "📊 Volatility Quality",
            "value": f"{insights['avg_vol_quality']:.1f}/10",
            "description": f"{risk_environment} risk environment",
            "type": "success" if insights['avg_vol_quality'] >= 7 else "info" if insights['avg_vol_quality'] >= 5 else "warning"
        },
        {
            "label": "🛡️ Risk Regime",
            "value": f"{insights['low_vol_regime']}/{insights['volatility_count']}",
            "description": "Companies in favorable volatility regimes",
            "type": "success" if insights['low_vol_regime'] >= insights['volatility_count'] * 0.4 else "info"
        },
        {
            "label": "⚖️ Risk Budget Optimization",
            "value": "Optimal" if insights['avg_vol_quality'] >= 7 else "Standard" if insights['avg_vol_quality'] >= 6 else "Enhanced",
            "description": "Risk allocation framework",
            "type": "success" if insights['avg_vol_quality'] >= 7 else "info"
        }
    ]
    
    html_parts.append(build_stat_grid(cards))
    
    # Strategic recommendations with risk focus
    recommendations = [
        {
            "priority": "HIGH",
            "title": "Risk Budgeting Framework",
            "insight": f"Portfolio operates in {risk_environment.lower()} volatility environment with {insights['avg_vol_quality']:.1f}/10 quality score.",
            "action": "Deploy volatility-intelligent allocation models with dynamic risk adjustment."
        },
        {
            "priority": "MEDIUM" if insights['avg_vol_quality'] >= 6 else "HIGH",
            "title": "Volatility Timing Strategy",
            "insight": f"{'Stable' if insights['avg_vol_quality'] >= 6.5 else 'Variable'} volatility patterns enable {'optimal' if insights['avg_vol_quality'] >= 6.5 else 'tactical'} risk positioning.",
            "action": "Implement sophisticated volatility regime analysis for risk-adjusted allocation."
        },
        {
            "priority": "HIGH",
            "title": "Downside Protection Integration",
            "insight": "Advanced tail risk assessment with integrated hedging strategies.",
            "action": "Enhance portfolio resilience through volatility-aware risk management."
        }
    ]
    
    html_parts.append(_build_action_priority_cards(recommendations))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_price_discovery_optimization_section(insights: Dict) -> str:
    """Build 15E.4: Price Discovery & Market Efficiency Optimization"""
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15E.4 Price Discovery & Market Efficiency Optimization</h4>')
    
    # Summary stat cards
    discovery_quality = (
        'Excellent' if insights['avg_discovery_score'] >= 7 and insights['efficient_discovery'] >= insights['discovery_count'] * 0.6
        else 'Good' if insights['avg_discovery_score'] >= 6
        else 'Standard'
    )
    
    cards = [
        {
            "label": "🎯 Discovery Efficiency",
            "value": f"{insights['avg_discovery_score']:.1f}/10",
            "description": f"{discovery_quality} price discovery",
            "type": "success" if insights['avg_discovery_score'] >= 7 else "info"
        },
        {
            "label": "✨ High Efficiency Names",
            "value": f"{insights['efficient_discovery']}/{insights['discovery_count']}",
            "description": f"Efficient price discovery ({(insights['efficient_discovery']/insights['discovery_count']*100):.0f}%)",
            "type": "success" if insights['efficient_discovery'] >= insights['discovery_count'] * 0.5 else "info"
        },
        {
            "label": "💡 Alpha Opportunity",
            "value": "High" if insights['efficient_discovery'] >= insights['discovery_count'] * 0.5 else "Selective" if insights['efficient_discovery'] >= insights['discovery_count'] * 0.3 else "Conservative",
            "description": "Information advantage potential",
            "type": "success" if insights['efficient_discovery'] >= insights['discovery_count'] * 0.5 else "info"
        }
    ]
    
    html_parts.append(build_stat_grid(cards))
    
    # Strategic recommendations
    recommendations = [
        {
            "priority": "HIGH" if insights['efficient_discovery'] >= insights['discovery_count'] * 0.5 else "MEDIUM",
            "title": "Efficiency-Based Selection",
            "insight": f"{discovery_quality} price discovery efficiency across {insights['efficient_discovery']}/{insights['discovery_count']} highly efficient holdings.",
            "action": "Leverage efficiency-aware strategies for systematic alpha generation."
        },
        {
            "priority": "MEDIUM",
            "title": "Information Integration",
            "insight": f"{'Rapid' if insights['avg_discovery_score'] >= 7 else 'Standard'} information processing enables informed decision-making.",
            "action": "Deploy advanced efficiency intelligence for optimal entry/exit timing."
        },
        {
            "priority": "HIGH" if insights['avg_discovery_score'] >= 6.5 else "MEDIUM",
            "title": "Alpha Generation Framework",
            "insight": "Superior price discovery analysis enabling competitive positioning advantages.",
            "action": "Implement efficiency-aware strategies with systematic information advantage."
        }
    ]
    
    html_parts.append(_build_action_priority_cards(recommendations))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


def _build_integrated_strategy_section(insights: Dict) -> str:
    """Build 15E.5: Integrated Microstructure Strategy & Portfolio Enhancement"""
    
    html_parts = []
    
    html_parts.append('<div class="subsection">')
    html_parts.append('<h4>15E.5 Integrated Microstructure Strategy & Portfolio Enhancement</h4>')
    
    # Overall portfolio intelligence card
    portfolio_status = (
        'Outstanding' if insights['portfolio_intelligence_score'] >= 7
        else 'Strong' if insights['portfolio_intelligence_score'] >= 6
        else 'Developing'
    )
    
    html_parts.append(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 16px; color: white; margin: 20px 0;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
            <div style="text-align: center;">
                <div style="font-size: 3rem; font-weight: 900; margin-bottom: 10px;">
                    {insights['portfolio_intelligence_score']:.1f}/10
                </div>
                <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 5px;">
                    Portfolio Microstructure Intelligence Score
                </div>
                <div style="font-size: 1.1rem; opacity: 0.9;">
                    {portfolio_status} microstructure capabilities
                </div>
            </div>
        </div>
    """)
    
    # Multi-column insight cards with icons
    html_parts.append(_build_multi_column_insights(insights))
    
    # Tabbed strategic timeframes
    html_parts.append(_build_tabbed_strategic_timeframes(insights))
    
    # Success metrics with progress bars
    html_parts.append(_build_success_metrics(insights))
    
    html_parts.append('</div>')
    
    return "\n".join(html_parts)


# =============================================================================
# ENHANCED VISUAL COMPONENTS
# =============================================================================

def _build_action_priority_cards(recommendations: list) -> str:
    """Build action priority cards with color coding"""
    
    priority_colors = {
        "HIGH": "#ef4444",
        "MEDIUM": "#f59e0b",
        "LOW": "#10b981"
    }
    
    cards_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 25px 0;">'
    
    for rec in recommendations:
        priority = rec['priority']
        color = priority_colors.get(priority, "#6b7280")
        
        cards_html += f"""
        <div style="background: var(--card-bg); border-left: 5px solid {color}; 
                    padding: 20px; border-radius: 12px; box-shadow: var(--shadow-sm);
                    transition: transform 0.3s ease;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="background: {color}; color: white; padding: 4px 12px; 
                             border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                    {priority} PRIORITY
                </span>
            </div>
            <h5 style="margin: 12px 0; color: var(--text-primary); font-size: 1.1rem;">
                {rec['title']}
            </h5>
            <p style="color: var(--text-secondary); margin: 10px 0; line-height: 1.6;">
                {rec['insight']}
            </p>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(0,0,0,0.1);">
                <strong style="color: var(--text-primary);">Action:</strong>
                <span style="color: var(--text-secondary);"> {rec['action']}</span>
            </div>
        </div>
        """
    
    cards_html += '</div>'
    
    return cards_html


def _build_multi_column_insights(insights: Dict) -> str:
    """Build multi-column insight cards with icons/emojis"""
    
    comprehensive_integration = (
        "Excellent foundation for superior decision making"
        if insights['portfolio_intelligence_score'] >= 7
        else "Good foundation supporting strategic positioning"
        if insights['portfolio_intelligence_score'] >= 6
        else "Developing foundation with enhancement opportunities"
    )
    
    html = f"""
    <div style="margin: 30px 0;">
        <h4 style="margin-bottom: 20px; color: var(--text-primary);">Strategic Integration Framework</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            
            <div style="background: linear-gradient(135deg, #667eea20, #764ba220); 
                        padding: 25px; border-radius: 12px; border: 1px solid #667eea40;">
                <div style="font-size: 2rem; margin-bottom: 10px;">🎯</div>
                <h5 style="color: var(--text-primary); margin-bottom: 10px;">Comprehensive Integration</h5>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Multi-dimensional analysis framework: {comprehensive_integration}
                </p>
            </div>
            
            <div style="background: linear-gradient(135deg, #10b98120, #05966920); 
                        padding: 25px; border-radius: 12px; border: 1px solid #10b98140;">
                <div style="font-size: 2rem; margin-bottom: 10px;">⚡</div>
                <h5 style="color: var(--text-primary); margin-bottom: 10px;">Execution Excellence</h5>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Microstructure-aware execution with real-time optimization across all dimensions
                </p>
            </div>
            
            <div style="background: linear-gradient(135deg, #f59e0b20, #d9770620); 
                        padding: 25px; border-radius: 12px; border: 1px solid #f59e0b40;">
                <div style="font-size: 2rem; margin-bottom: 10px;">📊</div>
                <h5 style="color: var(--text-primary); margin-bottom: 10px;">Risk-Return Optimization</h5>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Advanced portfolio construction using comprehensive microstructure intelligence
                </p>
            </div>
            
            <div style="background: linear-gradient(135deg, #3b82f620, #2563eb20); 
                        padding: 25px; border-radius: 12px; border: 1px solid #3b82f640;">
                <div style="font-size: 2rem; margin-bottom: 10px;">🚀</div>
                <h5 style="color: var(--text-primary); margin-bottom: 10px;">Competitive Advantage</h5>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Industry-leading microstructure intelligence for sustained outperformance
                </p>
            </div>
            
        </div>
    </div>
    """
    
    return html


def _build_tabbed_strategic_timeframes(insights: Dict) -> str:
    """Build tabbed sections for different strategic timeframes"""
    
    html = """
    <div style="margin: 30px 0;">
        <h4 style="margin-bottom: 20px; color: var(--text-primary);">Strategic Implementation Roadmap</h4>
        
        <div style="background: var(--card-bg); border-radius: 12px; padding: 25px; box-shadow: var(--shadow-sm);">
            
            <div style="border-left: 4px solid #667eea; padding-left: 20px; margin-bottom: 25px;">
                <h5 style="color: #667eea; margin-bottom: 10px;">🎯 Near-Term (0-6 months)</h5>
                <ul style="color: var(--text-secondary); line-height: 1.8; margin-left: 20px;">
                    <li><strong>Comprehensive Integration:</strong> Deploy integrated liquidity-technical-volatility-discovery framework</li>
                    <li><strong>Execution Enhancement:</strong> Implement microstructure-aware execution with real-time optimization</li>
                    <li><strong>Foundation Building:</strong> Establish systematic microstructure intelligence infrastructure</li>
                </ul>
            </div>
            
            <div style="border-left: 4px solid #10b981; padding-left: 20px; margin-bottom: 25px;">
                <h5 style="color: #10b981; margin-bottom: 10px;">📈 Medium-Term (6-18 months)</h5>
                <ul style="color: var(--text-secondary); line-height: 1.8; margin-left: 20px;">
                    <li><strong>Alpha Generation:</strong> Systematic alpha strategies leveraging superior market structure analysis</li>
                    <li><strong>Dynamic Management:</strong> Adaptive allocation models with real-time microstructure adjustment</li>
                    <li><strong>Competitive Positioning:</strong> Industry-leading microstructure intelligence capabilities</li>
                </ul>
            </div>
            
            <div style="border-left: 4px solid #f59e0b; padding-left: 20px;">
                <h5 style="color: #f59e0b; margin-bottom: 10px;">🏆 Long-Term (18+ months)</h5>
                <ul style="color: var(--text-secondary); line-height: 1.8; margin-left: 20px;">
                    <li><strong>Market Structure Mastery:</strong> Comprehensive microstructure expertise with significant competitive advantages</li>
                    <li><strong>Innovation Leadership:</strong> Advanced strategies setting new industry standards</li>
                    <li><strong>Performance Excellence:</strong> Superior risk-adjusted returns through microstructure intelligence</li>
                </ul>
            </div>
            
        </div>
    </div>
    """
    
    return html


def _build_success_metrics(insights: Dict) -> str:
    """Build success metrics with progress indicators and visual metrics"""
    
    # Calculate target improvements
    liquidity_target = min(10, insights['avg_liquidity_score'] + 1)
    technical_target = min(10, insights['avg_technical_score'] + 1.5)
    volatility_target = min(10, insights['avg_vol_quality'] + 1.5)
    discovery_target = min(10, insights['avg_discovery_score'] + 2)
    
    # Calculate target percentages for strong signals/high performers
    liquidity_target_pct = min(95, (insights['high_liquidity']/insights['liquidity_count'])*100 + 15)
    technical_target_pct = min(95, (insights['strong_signals']/insights['technical_count'])*100 + 15)
    
    html = f"""
    <div style="margin: 30px 0;">
        <h4 style="margin-bottom: 20px; color: var(--text-primary);">Success Metrics & Strategic Targets</h4>
        
        <div style="background: var(--card-bg); border-radius: 12px; padding: 25px; box-shadow: var(--shadow-sm);">
            
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-primary);">💧 Liquidity Enhancement Target</span>
                    <span style="font-weight: 700; color: #667eea;">{insights['avg_liquidity_score']:.1f}/10 → {liquidity_target:.1f}/10</span>
                </div>
                <div style="background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); 
                               width: {(insights['avg_liquidity_score']/10)*100}%; height: 100%; 
                               transition: width 0.8s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                        <span style="color: white; font-size: 0.75rem; font-weight: 700;">Current</span>
                    </div>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">
                    Target: {liquidity_target_pct:.0f}% high-liquidity companies within 18 months
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-primary);">📊 Technical Optimization Target</span>
                    <span style="font-weight: 700; color: #10b981;">{insights['avg_technical_score']:.1f}/10 → {technical_target:.1f}/10</span>
                </div>
                <div style="background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #10b981, #059669); 
                               width: {(insights['avg_technical_score']/10)*100}%; height: 100%; 
                               transition: width 0.8s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                        <span style="color: white; font-size: 0.75rem; font-weight: 700;">Current</span>
                    </div>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">
                    Target: {technical_target_pct:.0f}% companies with strong signals within 24 months
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-primary);">⚖️ Volatility Management Target</span>
                    <span style="font-weight: 700; color: #f59e0b;">{insights['avg_vol_quality']:.1f}/10 → {volatility_target:.1f}/10</span>
                </div>
                <div style="background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #f59e0b, #d97706); 
                               width: {(insights['avg_vol_quality']/10)*100}%; height: 100%; 
                               transition: width 0.8s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                        <span style="color: white; font-size: 0.75rem; font-weight: 700;">Current</span>
                    </div>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">
                    Target: {volatility_target:.1f}/10 volatility quality within 30 months
                </div>
            </div>
            
            <div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-primary);">🎯 Discovery Efficiency Target</span>
                    <span style="font-weight: 700; color: #3b82f6;">{insights['avg_discovery_score']:.1f}/10 → {discovery_target:.1f}/10</span>
                </div>
                <div style="background: rgba(0,0,0,0.1); border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #3b82f6, #2563eb); 
                               width: {(insights['avg_discovery_score']/10)*100}%; height: 100%; 
                               transition: width 0.8s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                        <span style="color: white; font-size: 0.75rem; font-weight: 700;">Current</span>
                    </div>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">
                    Target: {discovery_target:.1f}/10 price discovery score within 36 months
                </div>
            </div>
            
        </div>
        
        <div style="background: linear-gradient(135deg, #667eea20, #764ba220); 
                    border-radius: 12px; padding: 20px; margin-top: 20px; border: 1px solid #667eea40;">
            <div style="text-align: center;">
                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 10px;">
                    🏆 Strategic Excellence Achievement
                </div>
                <p style="color: var(--text-secondary); line-height: 1.6; max-width: 800px; margin: 0 auto;">
                    {'Outstanding microstructure capabilities' if insights['portfolio_intelligence_score'] >= 7 
                     else 'Strong microstructure foundation' if insights['portfolio_intelligence_score'] >= 6 
                     else 'Developing microstructure intelligence'} enabling superior portfolio performance 
                    through advanced market structure analysis and systematic execution excellence.
                </p>
            </div>
        </div>
    </div>
    """
    
    return html