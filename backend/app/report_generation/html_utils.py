"""Shared HTML utilities for all sections"""

import pandas as pd
import json
from typing import Dict, List, Optional, Union, Any
import numpy as np


def generate_section_wrapper(section_number: int, section_name: str, content: str) -> str:
    """Wrap section content in HTML document structure with theme support."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section {section_number}: {section_name}</title>
    
    <!-- Chart Libraries -->
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    
    <!-- DataTables for interactive tables -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    
    <style>
        /* ============================================
           CSS VARIABLES - THEME SYSTEM
           ============================================ */
        :root {{
            /* Light Theme (Default) */
            --bg-primary: #f5f7fa;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f8f9fa;
            --bg-card: #ffffff;
            
            --text-primary: #2c3e50;
            --text-secondary: #4a5568;
            --text-tertiary: #718096;
            --text-muted: #a0aec0;
            
            --accent-primary: #667eea;
            --accent-secondary: #5a67d8;
            --accent-tertiary: #764ba2;
            
            --border-color: #e2e8f0;
            --border-light: #edf2f7;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.15);
            
            --success-bg: #f0fdf4;
            --success-border: #86efac;
            --success-text: #166534;
            
            --warning-bg: #fffbeb;
            --warning-border: #fcd34d;
            --warning-text: #92400e;
            
            --info-bg: #eff6ff;
            --info-border: #93c5fd;
            --info-text: #1e40af;
            
            --danger-bg: #fef2f2;
            --danger-border: #fca5a5;
            --danger-text: #991b1b;
            
            --table-header-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --table-row-hover: #f7fafc;
            --table-border: #e2e8f0;
            
            --gradient-header: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-subtle: linear-gradient(135deg, #f0f4f8 0%, #e6ebf1 100%);
        }}
        
        [data-theme="dark"] {{
            /* Dark Theme (Ready for implementation) */
            --bg-primary: #1a202c;
            --bg-secondary: #2d3748;
            --bg-tertiary: #374151;
            --bg-card: #2d3748;
            
            --text-primary: #f7fafc;
            --text-secondary: #e2e8f0;
            --text-tertiary: #cbd5e0;
            --text-muted: #a0aec0;
            
            --accent-primary: #7c3aed;
            --accent-secondary: #8b5cf6;
            --accent-tertiary: #9333ea;
            
            --border-color: #4a5568;
            --border-light: #374151;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.5);
            
            --success-bg: #064e3b;
            --success-border: #10b981;
            --success-text: #d1fae5;
            
            --warning-bg: #78350f;
            --warning-border: #f59e0b;
            --warning-text: #fef3c7;
            
            --info-bg: #1e3a8a;
            --info-border: #3b82f6;
            --info-text: #dbeafe;
            
            --danger-bg: #7f1d1d;
            --danger-border: #ef4444;
            --danger-text: #fee2e2;
            
            --table-header-bg: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
            --table-row-hover: #374151;
            --table-border: #4a5568;
            
            --gradient-header: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
            --gradient-subtle: linear-gradient(135deg, #374151 0%, #4a5568 100%);
        }}
        
        /* ============================================
           BASE STYLES
           ============================================ */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-primary);
            padding: 20px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}
        
        .section {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--bg-card);
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
            transition: background-color 0.3s ease;
        }}
        
        /* ============================================
           SECTION HEADER WITH THEME TOGGLE
           ============================================ */
        .section-header {{
            background: var(--gradient-header);
            color: white;
            padding: 40px;
            text-align: center;
            border-bottom: 4px solid var(--accent-secondary);
            position: relative;
        }}
        
        .section-header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .theme-toggle {{
            position: absolute;
            top: 20px;
            right: 40px;
        }}
        
        .theme-toggle-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .theme-toggle-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.1);
        }}
        
        .theme-toggle-btn:active {{
            transform: scale(0.95);
        }}
        
        .icon-light, .icon-dark {{
            transition: opacity 0.3s ease;
        }}
        
        /* ============================================
           CONTENT AREA
           ============================================ */
        .section-content {{
            padding: 40px;
        }}
        
        .cover-page {{
            animation: fadeIn 0.6s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* ============================================
           REPORT HEADER
           ============================================ */
        .report-header {{
            text-align: center;
            padding: 40px 20px;
            background: var(--gradient-subtle);
            border-radius: 12px;
            margin-bottom: 40px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-light);
        }}
        
        .report-header h2 {{
            font-size: 2.8em;
            color: var(--text-primary);
            margin-bottom: 15px;
            font-weight: 800;
        }}
        
        .report-date {{
            font-size: 1.2em;
            color: var(--accent-primary);
            font-weight: 600;
            margin: 10px 0;
        }}
        
        .analysis-id {{
            font-size: 0.95em;
            color: var(--text-tertiary);
            margin-top: 10px;
        }}
        
        .analysis-id code {{
            background: var(--bg-tertiary);
            padding: 4px 12px;
            border-radius: 6px;
            font-family: 'Monaco', 'Courier New', monospace;
            color: var(--accent-primary);
            border: 1px solid var(--border-color);
        }}
        
        /* ============================================
           INFO SECTIONS
           ============================================ */
        .info-section {{
            margin: 40px 0;
            padding: 30px;
            background: var(--bg-tertiary);
            border-radius: 12px;
            border-left: 6px solid var(--accent-primary);
            transition: background-color 0.3s ease;
        }}
        
        .info-section h3 {{
            font-size: 1.8em;
            color: var(--text-primary);
            margin-bottom: 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
        }}
        
        .info-section h3::before {{
            content: '▸';
            color: var(--accent-primary);
            margin-right: 10px;
            font-size: 1.2em;
        }}
        
        .info-section h4 {{
            font-size: 1.4em;
            color: var(--text-secondary);
            margin: 25px 0 15px 0;
            font-weight: 600;
        }}
        
        /* ============================================
           TABLES
           ============================================ */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: var(--bg-secondary);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--table-border);
        }}
        
        .data-table thead {{
            background: var(--table-header-bg);
            color: white;
        }}
        
        .data-table th {{
            padding: 16px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .data-table td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--table-border);
            color: var(--text-primary);
        }}
        
        .data-table tbody tr {{
            transition: background-color 0.2s ease;
        }}
        
        .data-table tbody tr:hover {{
            background-color: var(--table-row-hover);
        }}
        
        .data-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        .data-table code {{
            background: var(--bg-tertiary);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: var(--accent-primary);
        }}
        
        /* DataTables specific styling */
        .dataTables_wrapper .dataTables_length,
        .dataTables_wrapper .dataTables_filter,
        .dataTables_wrapper .dataTables_info,
        .dataTables_wrapper .dataTables_paginate {{
            color: var(--text-secondary);
            margin: 10px 0;
        }}
        
        .dataTables_wrapper .dataTables_paginate .paginate_button {{
            color: var(--accent-primary) !important;
        }}
        
        .dataTables_wrapper .dataTables_filter input {{
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 6px 12px;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }}
        
        /* Number alignment */
        .data-table td.text-right,
        .data-table th.text-right {{
            text-align: right;
        }}
        
        .data-table td.text-center,
        .data-table th.text-center {{
            text-align: center;
        }}
        
        /* Color coding for positive/negative values */
        .positive {{
            color: #059669;
            font-weight: 600;
        }}
        
        .negative {{
            color: #dc2626;
            font-weight: 600;
        }}
        
        .neutral {{
            color: var(--text-secondary);
        }}
        
        /* ============================================
           COMPLETENESS BARS
           ============================================ */
        .completeness-cell {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .completeness-bar {{
            flex: 1;
            height: 24px;
            background: var(--bg-tertiary);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
            border: 1px solid var(--border-color);
        }}
        
        .completeness-fill {{
            height: 100%;
            background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-size: 0.8em;
            font-weight: 700;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }}
        
        .completeness-fill.medium {{
            background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .completeness-fill.low {{
            background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        }}
        
        .completeness-text {{
            min-width: 45px;
            text-align: right;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.9em;
        }}
        
        /* ============================================
           STAT CARDS
           ============================================ */
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        
        .stat-card {{
            background: var(--bg-secondary);
            padding: 24px;
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
            border-left: 4px solid var(--accent-primary);
            transition: all 0.3s ease;
            border: 1px solid var(--border-light);
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-md);
            border-left-width: 6px;
        }}
        
        .stat-card .label {{
            font-size: 0.85em;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: 700;
            color: var(--accent-primary);
            margin-bottom: 4px;
            line-height: 1.2;
        }}
        
        .stat-card .description {{
            font-size: 0.85em;
            color: var(--text-muted);
        }}
        
        /* Stat card color variants */
        .stat-card.success {{
            border-left-color: #059669;
        }}
        
        .stat-card.success .value {{
            color: #059669;
        }}
        
        .stat-card.warning {{
            border-left-color: #f59e0b;
        }}
        
        .stat-card.warning .value {{
            color: #f59e0b;
        }}
        
        .stat-card.danger {{
            border-left-color: #dc2626;
        }}
        
        .stat-card.danger .value {{
            color: #dc2626;
        }}
        
        /* ============================================
           METRIC LISTS
           ============================================ */
        .metric-list {{
            list-style: none;
            padding: 0;
        }}
        
        .metric-list li {{
            padding: 12px 0;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .metric-list li:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            font-weight: 600;
            color: var(--text-secondary);
        }}
        
        .metric-value {{
            color: var(--accent-primary);
            font-weight: 700;
            font-size: 1.05em;
        }}
        
        /* ============================================
           INFO BOXES
           ============================================ */
        .info-box {{
            background: var(--info-bg);
            border-left: 4px solid var(--info-border);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid var(--info-border);
        }}
        
        .info-box p {{
            margin: 8px 0;
            line-height: 1.8;
            color: var(--text-primary);
        }}
        
        .info-box strong {{
            color: var(--text-primary);
            font-weight: 700;
        }}
        
        .info-box.success {{
            background: var(--success-bg);
            border-left-color: var(--success-border);
            border-color: var(--success-border);
        }}
        
        .info-box.warning {{
            background: var(--warning-bg);
            border-left-color: var(--warning-border);
            border-color: var(--warning-border);
        }}
        
        .info-box.danger {{
            background: var(--danger-bg);
            border-left-color: var(--danger-border);
            border-color: var(--danger-border);
        }}
        
        /* ============================================
           SPECIAL SECTIONS
           ============================================ */
        .coverage-info {{
            background: var(--info-bg);
            padding: 30px;
            border-radius: 12px;
            margin: 30px 0;
            text-align: center;
            border: 2px solid var(--info-border);
        }}
        
        .coverage-info p {{
            font-size: 1.15em;
            margin: 10px 0;
            color: var(--text-primary);
        }}
        
        .coverage-info strong {{
            color: var(--accent-primary);
            font-size: 1.2em;
        }}
        
        .data-sources ul {{
            list-style: none;
            padding: 0;
        }}
        
        .data-sources li {{
            padding: 14px 0;
            padding-left: 30px;
            position: relative;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
        }}
        
        .data-sources li::before {{
            content: '✓';
            position: absolute;
            left: 0;
            color: #48bb78;
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .data-sources li:last-child {{
            border-bottom: none;
        }}
        
        .disclaimer {{
            background: var(--danger-bg);
            border: 2px solid var(--danger-border);
            border-radius: 12px;
            padding: 25px;
            margin: 40px 0;
        }}
        
        .disclaimer h4 {{
            color: var(--danger-text);
            margin-bottom: 12px;
            font-size: 1.3em;
        }}
        
        .disclaimer p {{
            color: var(--danger-text);
            line-height: 1.8;
        }}
        
        /* ============================================
           FOOTER
           ============================================ */
        .footer-metadata {{
            margin-top: 60px;
            padding: 30px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 12px;
            font-size: 0.9em;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
        }}
        
        .footer-metadata h4 {{
            color: var(--text-primary);
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .footer-metadata p {{
            margin: 8px 0;
            line-height: 1.8;
            color: var(--text-secondary);
        }}
        
        .footer-metadata strong {{
            color: var(--text-primary);
        }}
        
        /* ============================================
           SECTION DIVIDER
           ============================================ */
        .section-divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
            margin: 50px 0;
            opacity: 0.3;
        }}
        
        /* ============================================
           CHART CONTAINERS
           ============================================ */
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
        }}
        
        .chart-wrapper {{
            min-height: 400px;
        }}
        
        /* ============================================
           RESPONSIVE DESIGN
           ============================================ */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .section-content {{
                padding: 20px;
            }}
            
            .section-header {{
                padding: 30px 20px;
            }}
            
            .section-header h1 {{
                font-size: 1.8em;
            }}
            
            .theme-toggle {{
                top: 15px;
                right: 20px;
            }}
            
            .theme-toggle-btn {{
                width: 40px;
                height: 40px;
                font-size: 1.2em;
            }}
            
            .report-header h2 {{
                font-size: 2em;
            }}
            
            .stat-grid {{
                grid-template-columns: 1fr;
            }}
            
            .data-table {{
                font-size: 0.85em;
            }}
            
            .data-table th,
            .data-table td {{
                padding: 10px 8px;
            }}
            
            .info-section {{
                padding: 20px;
            }}
            
            .info-section h3 {{
                font-size: 1.5em;
            }}
        }}
        
        /* ============================================
           PRINT STYLES
           ============================================ */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .section {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
            
            .theme-toggle {{
                display: none;
            }}
            
            .section-header {{
                background: white !important;
                color: black !important;
                border-bottom: 2px solid #333;
            }}
            
            .stat-card {{
                break-inside: avoid;
            }}
            
            .info-section {{
                break-inside: avoid;
            }}
            
            .chart-container {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="section" id="section-{section_number}">
        <header class="section-header">
            <div class="theme-toggle">
                <button class="theme-toggle-btn" id="theme-toggle-btn" title="Toggle Light/Dark Mode">
                    <span class="icon-light">☀️</span>
                    <span class="icon-dark" style="display:none;">🌙</span>
                </button>
            </div>
            <h1>Section {section_number}: {section_name}</h1>
        </header>
        <div class="section-content">
{content}
        </div>
    </div>
    
    <script>
        // ============================================
        // THEME TOGGLE FUNCTIONALITY
        // ============================================
        
        // Load saved theme preference or default to light
        const savedTheme = localStorage.getItem('financial-analysis-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        // Theme toggle button event
        document.getElementById('theme-toggle-btn').addEventListener('click', function() {{
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('financial-analysis-theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Optional: Smooth transition effect
            document.body.style.transition = 'background-color 0.3s ease';
        }});
        
        function updateThemeIcon(theme) {{
            const lightIcon = document.querySelector('.icon-light');
            const darkIcon = document.querySelector('.icon-dark');
            
            if (theme === 'light') {{
                lightIcon.style.display = 'inline';
                darkIcon.style.display = 'none';
            }} else {{
                lightIcon.style.display = 'none';
                darkIcon.style.display = 'inline';
            }}
        }}
        
        // Keyboard shortcut: Ctrl/Cmd + Shift + T to toggle theme
        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {{
                e.preventDefault();
                document.getElementById('theme-toggle-btn').click();
            }}
        }});
    </script>
</body>
</html>
"""


# ============================================
# HELPER FUNCTIONS
# ============================================

def build_stat_card(
    label: str,
    value: str,
    description: str = "",
    card_type: str = "default"
) -> str:
    """
    Build a KPI stat card.
    
    Args:
        label: Card label/title (e.g., "Revenue Growth")
        value: Main value to display (e.g., "+12.3%")
        description: Optional description text below value
        card_type: Card style - "default", "success", "warning", "danger"
    
    Returns:
        HTML string for stat card
    """
    type_class = f" {card_type}" if card_type != "default" else ""
    description_html = f'<div class="description">{description}</div>' if description else ""
    
    return f"""
    <div class="stat-card{type_class}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {description_html}
    </div>
    """


def build_stat_grid(cards: List[Dict[str, str]]) -> str:
    """
    Build a responsive grid of stat cards.
    
    Args:
        cards: List of card dictionaries with keys: label, value, description, type
               Example: [{"label": "Revenue", "value": "$100M", "description": "FY2023", "type": "success"}]
    
    Returns:
        HTML string for stat grid
    """
    cards_html = ""
    for card in cards:
        cards_html += build_stat_card(
            label=card.get("label", ""),
            value=card.get("value", ""),
            description=card.get("description", ""),
            card_type=card.get("type", "default")
        )
    
    return f"""
    <div class="stat-grid">
        {cards_html}
    </div>
    """


def build_info_box(
    content: str,
    box_type: str = "info",
    title: Optional[str] = None
) -> str:
    """
    Build an info/alert box.
    
    Args:
        content: HTML content for the box (can include <p>, <ul>, etc.)
        box_type: Box style - "info", "success", "warning", "danger"
        title: Optional title/header for the box
    
    Returns:
        HTML string for info box
    """
    title_html = f"<p><strong>{title}</strong></p>" if title else ""
    
    return f"""
    <div class="info-box {box_type}">
        {title_html}
        {content}
    </div>
    """


def build_metric_list(metrics: List[Dict[str, str]]) -> str:
    """
    Build a key-value metric list.
    
    Args:
        metrics: List of dictionaries with keys: label, value
                Example: [{"label": "Revenue Growth", "value": "+12.3%"}]
    
    Returns:
        HTML string for metric list
    """
    items_html = ""
    for metric in metrics:
        items_html += f"""
        <li>
            <span class="metric-label">{metric.get('label', '')}</span>
            <span class="metric-value">{metric.get('value', '')}</span>
        </li>
        """
    
    return f"""
    <ul class="metric-list">
        {items_html}
    </ul>
    """


def build_section_divider() -> str:
    """Build a visual section divider."""
    return '<div class="section-divider"></div>'


def format_number(
    value: Union[int, float],
    decimals: int = 2,
    prefix: str = "",
    suffix: str = "",
    color_code: bool = False
) -> str:
    """
    Format a number for display.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        prefix: Prefix (e.g., "$")
        suffix: Suffix (e.g., "M", "%")
        color_code: If True, add positive/negative/neutral CSS class
    
    Returns:
        Formatted HTML string
    """
    if pd.isna(value):
        return "N/A"
    
    # Format the number
    if isinstance(value, (int, float)):
        formatted = f"{value:,.{decimals}f}"
    else:
        formatted = str(value)
    
    result = f"{prefix}{formatted}{suffix}"
    
    # Add color coding if requested
    if color_code:
        if value > 0:
            return f'<span class="positive">{result}</span>'
        elif value < 0:
            return f'<span class="negative">{result}</span>'
        else:
            return f'<span class="neutral">{result}</span>'
    
    return result


def format_percentage(
    value: float,
    decimals: int = 1,
    color_code: bool = True
) -> str:
    """
    Format a percentage value.
    
    Args:
        value: Percentage value (e.g., 0.123 for 12.3%)
        decimals: Number of decimal places
        color_code: If True, add positive/negative CSS class
    
    Returns:
        Formatted HTML string
    """
    if pd.isna(value):
        return "N/A"
    
    pct_value = value * 100
    return format_number(pct_value, decimals=decimals, suffix="%", color_code=color_code)


def format_currency(
    value: Union[int, float],
    decimals: int = 2,
    magnitude: str = "",
    color_code: bool = False
) -> str:
    """
    Format a currency value.
    
    Args:
        value: Currency value
        decimals: Number of decimal places
        magnitude: Magnitude indicator ("K", "M", "B", "T")
        color_code: If True, add positive/negative CSS class
    
    Returns:
        Formatted HTML string
    """
    if pd.isna(value):
        return "N/A"
    
    suffix = magnitude if magnitude else ""
    return format_number(value, decimals=decimals, prefix="$", suffix=suffix, color_code=color_code)


def build_data_table(
    df: pd.DataFrame,
    table_id: str = "data-table",
    sortable: bool = True,
    searchable: bool = True,
    page_length: int = 10,
    column_formats: Optional[Dict[str, Dict[str, Any]]] = None
) -> str:
    """
    Build an interactive data table from a pandas DataFrame.
    
    Args:
        df: DataFrame to convert to table
        table_id: Unique ID for the table (needed for DataTables JS)
        sortable: Enable column sorting
        searchable: Enable search box
        page_length: Number of rows per page (set to -1 to disable pagination)
        column_formats: Dictionary mapping column names to format specs
                       Example: {"Revenue": {"decimals": 0, "prefix": "$", "suffix": "M"}}
    
    Returns:
        HTML string with table and initialization script
    """
    if df.empty:
        return '<p class="text-muted">No data available</p>'
    
    # Apply formatting if specified
    df_display = df.copy()
    if column_formats:
        for col, fmt in column_formats.items():
            if col in df_display.columns:
                if fmt.get("type") == "percentage":
                    df_display[col] = df_display[col].apply(
                        lambda x: format_percentage(x, decimals=fmt.get("decimals", 1))
                    )
                elif fmt.get("type") == "currency":
                    df_display[col] = df_display[col].apply(
                        lambda x: format_currency(
                            x,
                            decimals=fmt.get("decimals", 2),
                            magnitude=fmt.get("magnitude", "")
                        )
                    )
                elif fmt.get("type") == "number":
                    df_display[col] = df_display[col].apply(
                        lambda x: format_number(
                            x,
                            decimals=fmt.get("decimals", 2),
                            prefix=fmt.get("prefix", ""),
                            suffix=fmt.get("suffix", ""),
                            color_code=fmt.get("color_code", False)
                        )
                    )
    
    # Build HTML table
    table_html = f'<table id="{table_id}" class="data-table">\n'
    
    # Header
    table_html += '<thead><tr>\n'
    for col in df_display.columns:
        table_html += f'<th>{col}</th>\n'
    table_html += '</tr></thead>\n'
    
    # Body
    table_html += '<tbody>\n'
    for _, row in df_display.iterrows():
        table_html += '<tr>\n'
        for val in row:
            # If value contains HTML tags, use as-is; otherwise escape
            if isinstance(val, str) and ('<' in val or '>' in val):
                table_html += f'<td>{val}</td>\n'
            else:
                table_html += f'<td>{val}</td>\n'
        table_html += '</tr>\n'
    table_html += '</tbody>\n'
    table_html += '</table>\n'
    
    # Add DataTables initialization script if sortable/searchable
    if sortable or searchable:
        options = {
            "paging": page_length != -1,
            "pageLength": page_length if page_length != -1 else 10,
            "searching": searchable,
            "ordering": sortable,
            "info": True,
            "autoWidth": False,
            "responsive": True
        }
        
        table_html += f"""
        <script>
            $(document).ready(function() {{
                $('#{table_id}').DataTable({json.dumps(options)});
            }});
        </script>
        """
    
    return table_html


def build_completeness_bar(
    percentage: float,
    show_text: bool = True
) -> str:
    """
    Build a completeness/progress bar.
    
    Args:
        percentage: Percentage value (0-100)
        show_text: Show percentage text next to bar
    
    Returns:
        HTML string for completeness bar
    """
    pct = min(100, max(0, percentage))  # Clamp between 0-100
    
    # Determine color class based on percentage
    if pct >= 80:
        fill_class = "completeness-fill"
    elif pct >= 50:
        fill_class = "completeness-fill medium"
    else:
        fill_class = "completeness-fill low"
    
    text_html = f'<span class="completeness-text">{pct:.0f}%</span>' if show_text else ""
    
    return f"""
    <div class="completeness-cell">
        <div class="completeness-bar">
            <div class="{fill_class}" style="width: {pct}%;">
                {pct:.0f}%
            </div>
        </div>
        {text_html}
    </div>
    """


def build_plotly_chart(
    fig_data: Dict[str, Any],
    div_id: str = "chart",
    title: Optional[str] = None,
    height: int = 500
) -> str:
    """
    Build a Plotly chart.
    
    Args:
        fig_data: Plotly figure data dictionary (can be from fig.to_dict())
        div_id: Unique ID for chart div
        title: Optional title for chart container
        height: Chart height in pixels
    
    Returns:
        HTML string with chart container and initialization script
    """
    title_html = f'<div class="chart-title">{title}</div>' if title else ""
    
    # Ensure the fig_data has the expected structure
    if 'data' not in fig_data:
        fig_data = {'data': fig_data.get('data', []), 'layout': fig_data.get('layout', {})}
    
    # Set default layout properties if not present
    if 'layout' not in fig_data:
        fig_data['layout'] = {}
    
    fig_data['layout'].setdefault('height', height)
    fig_data['layout'].setdefault('margin', {'l': 60, 'r': 40, 't': 40, 'b': 60})
    fig_data['layout'].setdefault('hovermode', 'closest')
    
    return f"""
    <div class="chart-container">
        {title_html}
        <div id="{div_id}" class="chart-wrapper"></div>
    </div>
    <script>
        Plotly.newPlot('{div_id}', {json.dumps(fig_data['data'])}, {json.dumps(fig_data['layout'])}, {{responsive: true}});
    </script>
    """


def build_simple_line_chart(
    x_data: List,
    y_data: List,
    x_label: str = "X",
    y_label: str = "Y",
    title: str = "Chart",
    div_id: str = "line-chart"
) -> str:
    """
    Build a simple Plotly line chart (convenience function).
    
    Args:
        x_data: X-axis data
        y_data: Y-axis data
        x_label: X-axis label
        y_label: Y-axis label
        title: Chart title
        div_id: Unique div ID
    
    Returns:
        HTML string for line chart
    """
    fig_data = {
        'data': [{
            'x': x_data,
            'y': y_data,
            'type': 'scatter',
            'mode': 'lines+markers',
            'line': {'color': '#667eea', 'width': 3},
            'marker': {'size': 8, 'color': '#667eea'}
        }],
        'layout': {
            'title': title,
            'xaxis': {'title': x_label},
            'yaxis': {'title': y_label}
        }
    }
    
    return build_plotly_chart(fig_data, div_id=div_id)


def build_bar_chart(
    categories: List[str],
    values: List[float],
    x_label: str = "Category",
    y_label: str = "Value",
    title: str = "Chart",
    div_id: str = "bar-chart",
    color: str = "#667eea"
) -> str:
    """
    Build a simple Plotly bar chart (convenience function).
    
    Args:
        categories: Category names
        values: Values for each category
        x_label: X-axis label
        y_label: Y-axis label
        title: Chart title
        div_id: Unique div ID
        color: Bar color
    
    Returns:
        HTML string for bar chart
    """
    fig_data = {
        'data': [{
            'x': categories,
            'y': values,
            'type': 'bar',
            'marker': {'color': color}
        }],
        'layout': {
            'title': title,
            'xaxis': {'title': x_label},
            'yaxis': {'title': y_label}
        }
    }
    
    return build_plotly_chart(fig_data, div_id=div_id)


def build_multi_line_chart(
    x_data: List,
    series_data: Dict[str, List],
    x_label: str = "X",
    y_label: str = "Y",
    title: str = "Chart",
    div_id: str = "multi-line-chart"
) -> str:
    """
    Build a multi-series line chart.
    
    Args:
        x_data: Shared X-axis data
        series_data: Dictionary mapping series names to Y data lists
                    Example: {"Revenue": [100, 120, 150], "Profit": [20, 25, 30]}
        x_label: X-axis label
        y_label: Y-axis label
        title: Chart title
        div_id: Unique div ID
    
    Returns:
        HTML string for multi-line chart
    """
    colors = ['#667eea', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
    
    traces = []
    for idx, (name, y_data) in enumerate(series_data.items()):
        traces.append({
            'x': x_data,
            'y': y_data,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': name,
            'line': {'color': colors[idx % len(colors)], 'width': 3},
            'marker': {'size': 6}
        })
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': title,
            'xaxis': {'title': x_label},
            'yaxis': {'title': y_label},
            'legend': {'x': 0, 'y': 1.1, 'orientation': 'h'}
        }
    }
    
    return build_plotly_chart(fig_data, div_id=div_id)