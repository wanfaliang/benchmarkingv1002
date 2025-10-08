"""Section 0: Cover & Metadata"""

from datetime import datetime

def generate_section_wrapper(section_number: int, section_name: str, content: str) -> str:
    """Wrap section content in HTML document structure."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section {section_number}: {section_name}</title>
    <link rel="stylesheet" href="/static/css/sections.css">
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
</head>
<body>
    <div class="section" id="section-{section_number}">
        <header class="section-header">
            <h1>Section {section_number}: {section_name}</h1>
        </header>
        <div class="section-content">
{content}
        </div>
    </div>
</body>
</html>
"""

def generate(collector, analysis_id: str) -> str:
    """
    Generate Section 0: Cover & Metadata.
    This section builds all its HTML inline.
    """
    # Get data from collector
    profiles = collector.get_profiles()
    financial_data = collector.get_all_financial_data()
    
    # Extract what we need
    companies = profiles[["Company", "Symbol", "sector", "industry"]].to_dict('records')
    years = sorted(financial_data["Year"].unique())
    coverage_start = min(years) if years else "N/A"
    coverage_end = max(years) if years else "N/A"
    
    # Build HTML content (each section does this its own way)
    content = f"""
    <div class="cover-page">
        <div class="report-header">
            <h2>Financial Analysis Report</h2>
            <p class="report-date">Generated: {datetime.now().strftime("%B %d, %Y")}</p>
            <p class="analysis-id">Analysis ID: <code>{analysis_id}</code></p>
        </div>
        
        <div class="companies-section">
            <h3>Companies Analyzed</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Ticker</th>
                        <th>Sector</th>
                        <th>Industry</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for company in companies:
        content += f"""
                    <tr>
                        <td>{company['Company']}</td>
                        <td><strong>{company['Symbol']}</strong></td>
                        <td>{company.get('sector', 'N/A')}</td>
                        <td>{company.get('industry', 'N/A')}</td>
                    </tr>
        """
    
    content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="coverage-info">
            <h3>Coverage Period</h3>
            <p>Analysis covers fiscal years: <strong>{coverage_start} - {coverage_end}</strong></p>
            <p>Total of {len(years)} years of historical data</p>
        </div>
        
        <div class="data-sources">
            <h3>Data Sources</h3>
            <ul>
                <li><strong>Financial Statements:</strong> Financial Modeling Prep (FMP) API</li>
                <li><strong>Market Data:</strong> FMP API (prices, volumes)</li>
                <li><strong>Institutional & Insider Activity:</strong> FMP API</li>
                <li><strong>Economic Indicators:</strong> Federal Reserve (FRED)</li>
            </ul>
        </div>
        
        <div class="disclaimer">
            <h4>Disclaimer</h4>
            <p>This report is for informational purposes only and does not constitute investment advice.</p>
        </div>
    </div>
    """
    
    # Wrap in section template
    return generate_section_wrapper(0, "Cover & Metadata", content)