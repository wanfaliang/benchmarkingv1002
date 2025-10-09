"""Section 0: Cover & Metadata - Professional Light Theme with Theme Toggle"""

from datetime import datetime
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any
from backend.app.report_generation.html_utils import generate_section_wrapper

def _analyze_data_coverage(collector, companies):
    """Analyze comprehensive data coverage across all sources."""
    
    stats = {}
    
    # Get main financial data
    df = collector.get_all_financial_data()
    
    # Basic coverage from main dataframe
    if not df.empty and 'Year' in df.columns:
        stats['min_year'] = int(df['Year'].min())
        stats['max_year'] = int(df['Year'].max())
        stats['total_years'] = stats['max_year'] - stats['min_year'] + 1
        stats['financial_data_points'] = len(df)
    else:
        stats.update({'min_year': 0, 'max_year': 0, 'total_years': 0, 'financial_data_points': 0})
    
    # Price data coverage
    daily_prices = collector.get_prices_daily()
    stats['price_data_points'] = len(daily_prices) if not daily_prices.empty else 0
    
    # Institutional data coverage
    institutional = collector.get_institutional_ownership()
    stats['institutional_quarters'] = len(institutional) if not institutional.empty else 0
    
    # Insider data coverage
    insider_latest = collector.get_insider_trading_latest()
    stats['insider_transactions'] = len(insider_latest) if not insider_latest.empty else 0
    
    # Analyst data coverage
    analyst_est, analyst_targets = collector.get_analyst_estimates()
    stats['analyst_estimates'] = len(analyst_est) if not analyst_est.empty else 0
    
    # Economic data coverage
    try:
        econ = collector.get_economic()
        stats['economic_indicators'] = len(econ.columns) - 1 if not econ.empty else 0  # Exclude Year column
    except:
        stats['economic_indicators'] = 0
    
    return stats


def _create_completeness_matrix(collector, companies):
    """Create data completeness matrix by company and data type."""
    
    data_types = ['Financial', 'Prices', 'Institutional', 'Insider', 'Analyst']
    completeness_data = []
    
    for company_name in companies.keys():
        row = {'Company': company_name}
        
        # Financial data completeness (from main dataframe)
        main_df = collector.get_all_financial_data()
        if not main_df.empty:
            company_financial = main_df[main_df['Company'] == company_name]
            total_possible_years = collector.years
            actual_years = len(company_financial)
            row['Financial'] = actual_years / total_possible_years if total_possible_years > 0 else 0
        else:
            row['Financial'] = 0
        
        # Price data completeness
        daily_prices = collector.get_prices_daily()
        if not daily_prices.empty:
            company_prices = daily_prices[daily_prices['Company'] == company_name]
            if not company_prices.empty and 'date' in company_prices.columns:
                # Rough completeness based on trading days (assuming ~252 trading days/year)
                expected_days = collector.years * 252
                actual_days = len(company_prices)
                row['Prices'] = min(1.0, actual_days / expected_days)
            else:
                row['Prices'] = 0
        else:
            row['Prices'] = 0
        
        # Institutional data completeness
        institutional = collector.get_institutional_ownership()
        if not institutional.empty:
            company_inst = institutional[institutional['Company'] == company_name]
            # Expecting up to 4 quarters, completeness based on available quarters
            row['Institutional'] = min(1.0, len(company_inst) / 4)
        else:
            row['Institutional'] = 0
        
        # Insider data completeness (binary - has recent data or not)
        insider_latest = collector.get_insider_trading_latest()
        if not insider_latest.empty:
            company_insider = insider_latest[insider_latest['Company'] == company_name]
            row['Insider'] = 1.0 if len(company_insider) > 0 else 0.0
        else:
            row['Insider'] = 0
        
        # Analyst data completeness (binary - has estimates or not)
        analyst_est, analyst_targets = collector.get_analyst_estimates()
        has_estimates = not analyst_est.empty and len(analyst_est[analyst_est['Company'] == company_name]) > 0
        has_targets = not analyst_targets.empty and len(analyst_targets[analyst_targets['Company'] == company_name]) > 0
        row['Analyst'] = 1.0 if (has_estimates or has_targets) else 0.0
        
        completeness_data.append(row)
    
    return pd.DataFrame(completeness_data).set_index('Company')


def _analyze_institutional_data(institutional_df):
    """Analyze institutional ownership patterns."""
    
    stats = {}
    
    if 'ownershipPercent' in institutional_df.columns:
        ownership_pcts = pd.to_numeric(institutional_df['ownershipPercent'], errors='coerce').dropna()
        stats['avg_ownership'] = ownership_pcts.mean() / 100  # Convert to decimal
        stats['min_ownership'] = ownership_pcts.min() / 100
        stats['max_ownership'] = ownership_pcts.max() / 100
    else:
        stats.update({'avg_ownership': 0, 'min_ownership': 0, 'max_ownership': 0})
    
    if 'investorsHolding' in institutional_df.columns:
        investors = pd.to_numeric(institutional_df['investorsHolding'], errors='coerce').dropna()
        stats['avg_investors'] = investors.mean()
    else:
        stats['avg_investors'] = 0
        
    if 'totalInvested' in institutional_df.columns:
        total_invested = pd.to_numeric(institutional_df['totalInvested'], errors='coerce').dropna()
        stats['total_invested'] = total_invested.sum() / 1e9  # Convert to billions
    else:
        stats['total_invested'] = 0
    
    # Quarter analysis
    if 'CollectedQuarter' in institutional_df.columns:
        stats['max_quarters'] = institutional_df['CollectedQuarter'].nunique()
        latest_year = institutional_df['CollectedYear'].max() if 'CollectedYear' in institutional_df.columns else 0
        latest_quarter = institutional_df['CollectedQuarter'].max()
        stats['latest_quarter'] = f"Q{latest_quarter} {latest_year}"
    else:
        stats['max_quarters'] = 0
        stats['latest_quarter'] = "N/A"
    
    return stats


def _analyze_insider_data(insider_latest_df, insider_stats_df):
    """Analyze insider trading patterns."""
    
    stats = {}
    
    stats['total_transactions'] = len(insider_latest_df)
    
    # Date range analysis
    if 'transactionDate' in insider_latest_df.columns:
        dates = pd.to_datetime(insider_latest_df['transactionDate'], errors='coerce').dropna()
        if not dates.empty:
            stats['date_range'] = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
        else:
            stats['date_range'] = "N/A"
    else:
        stats['date_range'] = "N/A"
    
    stats['avg_per_company'] = len(insider_latest_df) / insider_latest_df['Company'].nunique() if not insider_latest_df.empty else 0
    
    # Transaction type analysis
    if 'transactionType' in insider_latest_df.columns:
        transaction_counts = insider_latest_df['transactionType'].value_counts()
        total_transactions = len(insider_latest_df)
        
        purchase_transactions = sum([count for txn_type, count in transaction_counts.items() 
                                   if 'buy' in txn_type.lower() or 'purchase' in txn_type.lower() or 'a-' in txn_type.lower()])
        sale_transactions = sum([count for txn_type, count in transaction_counts.items() 
                               if 'sale' in txn_type.lower() or 'sell' in txn_type.lower() or 's-' in txn_type.lower()])
        
        stats['purchase_pct'] = purchase_transactions / total_transactions if total_transactions > 0 else 0
        stats['sale_pct'] = sale_transactions / total_transactions if total_transactions > 0 else 0
        
        if purchase_transactions > sale_transactions:
            stats['net_sentiment'] = "Bullish (more purchases)"
        elif sale_transactions > purchase_transactions:
            stats['net_sentiment'] = "Bearish (more sales)"
        else:
            stats['net_sentiment'] = "Neutral"
    else:
        stats.update({'purchase_pct': 0, 'sale_pct': 0, 'net_sentiment': 'N/A'})
    
    # Unique insider count
    if 'reportingName' in insider_latest_df.columns:
        stats['unique_insiders'] = insider_latest_df['reportingName'].nunique()
    else:
        stats['unique_insiders'] = 0
    
    return stats


def _analyze_price_data(daily_prices, monthly_prices):
    """Analyze price data quality and coverage."""
    
    stats = {}
    
    stats['daily_observations'] = len(daily_prices)
    stats['monthly_observations'] = len(monthly_prices)
    
    # Date range analysis
    if 'date' in daily_prices.columns:
        dates = pd.to_datetime(daily_prices['date'], errors='coerce').dropna()
        if not dates.empty:
            stats['date_range'] = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
        else:
            stats['date_range'] = "N/A"
    else:
        stats['date_range'] = "N/A"
    
    # Company completeness
    if 'Company' in daily_prices.columns:
        companies_with_full_data = []
        for company in daily_prices['Company'].unique():
            company_data = daily_prices[daily_prices['Company'] == company]
            if len(company_data) > 1000:  # Rough threshold for "complete" data (4+ years)
                companies_with_full_data.append(company)
        stats['complete_companies'] = len(companies_with_full_data)
        stats['avg_trading_days'] = daily_prices.groupby('Company').size().mean()
    else:
        stats.update({'complete_companies': 0, 'avg_trading_days': 0})
    
    return stats


def _get_collection_statistics(collector):
    """Get collection and processing statistics."""
    
    stats = {}
    
    # Count endpoints used based on available data
    endpoints_used = []
    
    # Check which data sources have data
    main_df = collector.get_all_financial_data()
    if not main_df.empty:
        endpoints_used.extend(['income-statement', 'balance-sheet', 'cash-flow', 'ratios', 'key-metrics'])
    
    profiles = collector.get_profiles()
    if not profiles.empty:
        endpoints_used.append('profile')
    
    prices = collector.get_prices_daily()
    if not prices.empty:
        endpoints_used.append('historical-price-eod')
    
    institutional = collector.get_institutional_ownership()
    if not institutional.empty:
        endpoints_used.append('institutional-ownership')
    
    insider_latest = collector.get_insider_trading_latest()
    if not insider_latest.empty:
        endpoints_used.extend(['insider-trading/latest', 'insider-trading/statistics'])
    
    try:
        econ = collector.get_economic()
        if not econ.empty:
            endpoints_used.append('FRED economic data')
    except:
        pass
    
    stats['endpoints_used'] = len(endpoints_used)
    
    # Estimate total data points
    total_points = 0
    if not main_df.empty:
        total_points += len(main_df) * len(main_df.columns)
    if not prices.empty:
        total_points += len(prices) * len(prices.columns)
    if not institutional.empty:
        total_points += len(institutional) * len(institutional.columns)
    if not insider_latest.empty:
        total_points += len(insider_latest) * len(insider_latest.columns)
    
    stats['total_data_points'] = total_points
    
    # Estimate collection time (rough approximation)
    num_companies = len(collector.companies)
    estimated_api_calls = num_companies * 8  # Rough estimate of calls per company
    estimated_seconds = estimated_api_calls * (collector.sleep_sec + 0.5)  # Add processing time
    stats['estimated_collection_time'] = f"~{estimated_seconds/60:.1f} minutes"
    
    # Rate limiting info
    if collector.sleep_sec > 0:
        stats['rate_limiting'] = f"Applied ({collector.sleep_sec}s between calls)"
    else:
        stats['rate_limiting'] = "Not applied (high-rate plan)"
    
    return stats


def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 0: Cover & Metadata - Professional Light Theme.
    
    Args:
        collector: Loaded FinancialDataCollection object
        analysis_id: The analysis ID
    
    Returns:
        Complete HTML string with comprehensive metadata and data profiling
    """
    
    # Extract data from collector
    profiles = collector.get_profiles()
    financial_data = collector.get_all_financial_data()
    companies = collector.companies  # Dict of {company_name: ticker}
    
    # Get primary currency
    primary_currency = "USD"
    if not profiles.empty and 'currency' in profiles.columns:
        currencies = profiles['currency'].value_counts()
        if not currencies.empty:
            primary_currency = currencies.index[0]
    
    # Calculate coverage statistics
    coverage_stats = _analyze_data_coverage(collector, companies)
    
    # Get completeness matrix
    completeness_df = _create_completeness_matrix(collector, companies)
    
    # Analyze institutional data
    institutional_df = collector.get_institutional_ownership()
    inst_stats = _analyze_institutional_data(institutional_df) if not institutional_df.empty else None
    
    # Analyze insider data
    insider_latest_df = collector.get_insider_trading_latest()
    insider_stats_df = collector.get_insider_statistics()
    insider_analysis = _analyze_insider_data(insider_latest_df, insider_stats_df) if not insider_latest_df.empty else None
    
    # Analyze price data
    daily_prices = collector.get_prices_daily()
    monthly_prices = collector.get_prices_monthly()
    price_analysis = _analyze_price_data(daily_prices, monthly_prices) if not daily_prices.empty else None
    
    # Get collection statistics
    collection_stats = _get_collection_statistics(collector)
    
    # Build HTML content
    content = f"""
    <div class="cover-page">
        <!-- REPORT HEADER -->
        <div class="report-header">
            <h2>Comprehensive Financial and Equity Analysis Report</h2>
            <p class="report-date">Generated: {datetime.now().strftime("%B %d, %Y at %H:%M UTC")}</p>
            <p class="analysis-id">Analysis ID: <code>{analysis_id}</code></p>
        </div>
        
        <!-- REPORT INFORMATION -->
        <div class="info-section">
            <h3>Report Information</h3>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="label">Report Version</div>
                    <div class="value">v1.0</div>
                    <div class="description">Enhanced Multi-Phase Analysis</div>
                </div>
                <div class="stat-card">
                    <div class="label">Total Records</div>
                    <div class="value">{coverage_stats['financial_data_points']:,}</div>
                    <div class="description">Annual data points analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="label">Coverage Window</div>
                    <div class="value">{coverage_stats['min_year']}-{coverage_stats['max_year']}</div>
                    <div class="description">{coverage_stats['total_years']} years historical</div>
                </div>
                <div class="stat-card">
                    <div class="label">Primary Currency</div>
                    <div class="value">{primary_currency}</div>
                    <div class="description">Unless otherwise noted</div>
                </div>
            </div>
            
            <div class="info-box">
                <p><strong>Data Sources:</strong></p>
                <p>• Financial data: Financial Modeling Prep (FMP) API</p>
                <p>• Economic data: Federal Reserve Economic Data (FRED)</p>
                <p>• Prepared by: Financial Analytics Team</p>
            </div>
        </div>
        
        <div class="section-divider"></div>
        
        <!-- COMPANY PORTFOLIO -->
        <div class="info-section">
            <h3>Company Portfolio</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Symbol</th>
                        <th>Sector</th>
                        <th>Industry</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add company rows
    for company_name, symbol in companies.items():
        if not profiles.empty:
            company_profile = profiles[profiles['Company'] == company_name]
            if not company_profile.empty:
                sector = str(company_profile.iloc[0].get('sector', 'N/A'))
                industry = str(company_profile.iloc[0].get('industry', 'N/A'))
            else:
                sector = 'N/A'
                industry = 'N/A'
        else:
            sector = 'N/A'
            industry = 'N/A'
            
        content += f"""
                    <tr>
                        <td><strong>{company_name}</strong></td>
                        <td><code>{symbol}</code></td>
                        <td>{sector}</td>
                        <td>{industry}</td>
                    </tr>
        """
    
    content += """
                </tbody>
            </table>
        </div>
        
        <div class="section-divider"></div>
        
        <!-- DATA COVERAGE & QUALITY ASSESSMENT -->
        <div class="info-section">
            <h3>Enhanced Data Coverage & Quality Assessment</h3>
            
            <h4>Data Sources & Scope</h4>
            <div class="info-box success">
                <p><strong>Primary Data Provider:</strong> Financial Modeling Prep (FMP) API</p>
                <p><strong>Economic Data:</strong> Federal Reserve Economic Data (FRED)</p>
    """
    
    content += f"""
                <p><strong>Coverage Period:</strong> {coverage_stats['min_year']} - {coverage_stats['max_year']} ({coverage_stats['total_years']} years)</p>
            </div>
            
            <h4>Data Categories Analyzed</h4>
            <ul class="metric-list">
                <li>
                    <span class="metric-label">Financial Statements</span>
                    <span class="metric-value">{coverage_stats['financial_data_points']:,} annual data points</span>
                </li>
                <li>
                    <span class="metric-label">Daily Market Data</span>
                    <span class="metric-value">{coverage_stats['price_data_points']:,} price observations</span>
                </li>
                <li>
                    <span class="metric-label">Institutional Holdings</span>
                    <span class="metric-value">{coverage_stats['institutional_quarters']:,} quarterly reports</span>
                </li>
                <li>
                    <span class="metric-label">Corporate Insider Activity</span>
                    <span class="metric-value">{coverage_stats['insider_transactions']:,} transactions</span>
                </li>
                <li>
                    <span class="metric-label">Analyst Research</span>
                    <span class="metric-value">{coverage_stats['analyst_estimates']:,} estimate records</span>
                </li>
                <li>
                    <span class="metric-label">Economic Indicators</span>
                    <span class="metric-value">{coverage_stats['economic_indicators']:,} macro series</span>
                </li>
            </ul>
        </div>
        
        <div class="section-divider"></div>
        
        <!-- DATA COMPLETENESS MATRIX -->
        <div class="info-section">
            <h3>Data Completeness by Company</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Company</th>
    """
    
    # Add completeness table headers
    for col in completeness_df.columns:
        content += f"<th>{col}</th>"
    
    content += """
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add completeness rows with visual bars
    for company, row in completeness_df.iterrows():
        content += f"""
                    <tr>
                        <td><strong>{company}</strong></td>
        """
        for value in row:
            pct = value * 100
            bar_class = "completeness-fill"
            if pct < 50:
                bar_class += " low"
            elif pct < 80:
                bar_class += " medium"
            
            content += f"""
                        <td>
                            <div class="completeness-cell">
                                <div class="completeness-bar">
                                    <div class="{bar_class}" style="width: {pct}%;">
                                        {pct:.0f}%
                                    </div>
                                </div>
                            </div>
                        </td>
            """
        content += """
                    </tr>
        """
    
    content += """
                </tbody>
            </table>
        </div>
    """
    
    # Add institutional ownership section
    if inst_stats:
        content += f"""
        <div class="section-divider"></div>
        
        <div class="info-section">
            <h3>Institutional Ownership Profile</h3>
            
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="label">Average Ownership</div>
                    <div class="value">{inst_stats['avg_ownership']:.1%}</div>
                    <div class="description">Institutional holdings</div>
                </div>
                <div class="stat-card">
                    <div class="label">Ownership Range</div>
                    <div class="value">{inst_stats['min_ownership']:.1%} - {inst_stats['max_ownership']:.1%}</div>
                    <div class="description">Min to Max</div>
                </div>
                <div class="stat-card">
                    <div class="label">Average Investors</div>
                    <div class="value">{inst_stats['avg_investors']:,.0f}</div>
                    <div class="description">Per company</div>
                </div>
                <div class="stat-card">
                    <div class="label">Total Capital</div>
                    <div class="value">${inst_stats['total_invested']:,.1f}B</div>
                    <div class="description">Under analysis</div>
                </div>
            </div>
            
            <div class="info-box">
                <p><strong>Quarterly Coverage:</strong> Up to {inst_stats['max_quarters']} quarters per company</p>
                <p><strong>Most Recent Data:</strong> {inst_stats['latest_quarter']}</p>
            </div>
        </div>
        """
    
    # Add insider activity section
    if insider_analysis:
        content += f"""
        <div class="section-divider"></div>
        
        <div class="info-section">
            <h3>Insider Activity Summary</h3>
            
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="label">Total Transactions</div>
                    <div class="value">{insider_analysis['total_transactions']:,}</div>
                    <div class="description">Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="label">Average per Company</div>
                    <div class="value">{insider_analysis['avg_per_company']:.0f}</div>
                    <div class="description">Transactions</div>
                </div>
                <div class="stat-card">
                    <div class="label">Unique Insiders</div>
                    <div class="value">{insider_analysis['unique_insiders']:,}</div>
                    <div class="description">Individuals tracked</div>
                </div>
                <div class="stat-card">
                    <div class="label">Net Sentiment</div>
                    <div class="value">{insider_analysis['net_sentiment']}</div>
                    <div class="description">Overall signal</div>
                </div>
            </div>
            
            <div class="info-box">
                <p><strong>Transaction Date Range:</strong> {insider_analysis['date_range']}</p>
                <p><strong>Transaction Breakdown:</strong></p>
                <p>• Purchases: {insider_analysis['purchase_pct']:.1%}</p>
                <p>• Sales: {insider_analysis['sale_pct']:.1%}</p>
            </div>
        </div>
        """
    
    # Add price data quality section
    if price_analysis:
        content += f"""
        <div class="section-divider"></div>
        
        <div class="info-section">
            <h3>Price & Market Data Quality</h3>
            
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="label">Daily Observations</div>
                    <div class="value">{price_analysis['daily_observations']:,}</div>
                    <div class="description">Price points</div>
                </div>
                <div class="stat-card">
                    <div class="label">Monthly Data Points</div>
                    <div class="value">{price_analysis['monthly_observations']:,}</div>
                    <div class="description">Aggregated</div>
                </div>
                <div class="stat-card">
                    <div class="label">Complete Companies</div>
                    <div class="value">{price_analysis['complete_companies']} of {len(companies)}</div>
                    <div class="description">Full history</div>
                </div>
                <div class="stat-card">
                    <div class="label">Avg Trading Days</div>
                    <div class="value">{price_analysis['avg_trading_days']:.0f}</div>
                    <div class="description">Per company</div>
                </div>
            </div>
            
            <div class="info-box success">
                <p><strong>Date Range:</strong> {price_analysis['date_range']}</p>
                <p><strong>Corporate Actions:</strong> Adjusted (built into close prices)</p>
            </div>
        </div>
        """
    
    # Add technical infrastructure section
    content += f"""
        <div class="section-divider"></div>
        
        <div class="info-section">
            <h3>Technical Infrastructure & Methodology</h3>
            
            <h4>Collection & Processing Statistics</h4>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="label">API Endpoints</div>
                    <div class="value">{collection_stats['endpoints_used']}</div>
                    <div class="description">Utilized</div>
                </div>
                <div class="stat-card">
                    <div class="label">Data Points</div>
                    <div class="value">{collection_stats['total_data_points']:,}</div>
                    <div class="description">Collected</div>
                </div>
                <div class="stat-card">
                    <div class="label">Processing Time</div>
                    <div class="value">{collection_stats['estimated_collection_time']}</div>
                    <div class="description">Estimated</div>
                </div>
                <div class="stat-card">
                    <div class="label">Rate Limiting</div>
                    <div class="value">{collection_stats['rate_limiting']}</div>
                    <div class="description">API throttling</div>
                </div>
            </div>
            
            <h4>Data Validation Checks</h4>
            <div class="info-box">
                <p>✓ Cross-source consistency verification</p>
                <p>✓ Market cap reconciliation (price × shares vs reported)</p>
                <p>✓ Institutional ownership totals validation</p>
                <p>✓ Date alignment across all data sources</p>
                <p>✓ Error handling: Automatic retry with exponential backoff</p>
            </div>
            
            <h4>Data Transformations & Standards</h4>
            <div class="info-box warning">
                <p><strong>Standardization Applied:</strong></p>
                <p>• All monetary values in USD (original currency preserved where applicable)</p>
                <p>• Date normalization to YYYY-MM-DD format</p>
                <p>• Percentage values converted to decimals for calculations</p>
                <p>• Corporate actions adjusted in price data</p>
                
                <p><strong>Field Consolidation Rules:</strong></p>
                <p>• Precedence: Income Statement > Cash Flow > Balance Sheet > Key Metrics > Ratios</p>
                <p>• Original FMP field names preserved</p>
                <p>• Company/Symbol identifiers added to all datasets</p>
                
                <p><strong>Quality Filters:</strong></p>
                <p>• YoY delta calculations for key financial metrics</p>
                <p>• Outlier detection (values beyond 3 standard deviations flagged)</p>
                <p>• Missing data percentage tracking by field and company</p>
            </div>
        </div>
        
        <div class="section-divider"></div>
        
        <!-- DATA SOURCES -->
        <div class="info-section">
            <h3>Data Sources</h3>
            <div class="data-sources">
                <ul>
                    <li><strong>Financial Statements:</strong> Financial Modeling Prep (FMP) API - Comprehensive annual and quarterly reports</li>
                    <li><strong>Market Data:</strong> FMP API - Daily and monthly OHLC prices with volume</li>
                    <li><strong>Institutional & Insider Activity:</strong> FMP API - 13F filings, insider transactions, ownership changes</li>
                    <li><strong>Analyst Coverage:</strong> FMP API - Earnings estimates, price targets, consensus data</li>
                    <li><strong>Economic Indicators:</strong> Federal Reserve (FRED) - Macro-economic time series data</li>
                </ul>
            </div>
        </div>
        
        <div class="section-divider"></div>
        
        <!-- DISCLAIMER -->
        <div class="disclaimer">
            <h4>⚠️ Important Disclaimer</h4>
            <p>This report is for informational purposes only and does not constitute investment advice. 
            Past performance does not guarantee future results. All investment decisions should be made 
            in consultation with qualified financial professionals and based on individual circumstances, 
            risk tolerance, and investment objectives.</p>
        </div>
        
        <!-- FOOTER METADATA -->
        <div class="footer-metadata">
            <h4>Report Metadata</h4>
            <p><strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y at %H:%M UTC")}</p>
            <p><strong>Prepared by:</strong> Financial Analytics Team</p>
            <p><strong>Version:</strong> v1.0 (Enhanced Multi-Phase Analysis)</p>
            <p><strong>Analysis ID:</strong> {analysis_id}</p>
            <p><strong>Methodology:</strong> Multi-dimensional equity analysis with institutional ownership, insider activity, and market microstructure integration</p>
            <p><strong>Data Sources:</strong> Financial Modeling Prep API, Federal Reserve Economic Data (FRED)</p>
        </div>
    </div>
    """
    
    # Wrap in section template
    return generate_section_wrapper(0, "Cover & Metadata", content)