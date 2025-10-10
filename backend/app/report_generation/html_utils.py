"""
Enhanced HTML Utilities for Report Generation
Provides sophisticated UI components with glassmorphism, animations, and professional polish.
"""

import pandas as pd
import json
from typing import List, Dict, Optional, Any, Union


# =============================================================================
# MAIN SECTION WRAPPER WITH SOPHISTICATED STYLING
# =============================================================================

def generate_section_wrapper(section_number: int, section_title: str, content: str) -> str:
    """
    Generate complete HTML document with enhanced sophisticated styling.
    
    Features:
    - Glassmorphism effects
    - Gradient backgrounds and text
    - Smooth animations and transitions
    - Dark/Light theme toggle
    - Custom scrollbar
    - Responsive design
    
    Args:
        section_number: Section number (0-19)
        section_title: Title of the section
        content: HTML content for the section body
    
    Returns:
        Complete HTML document string
    """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section {section_number}: {section_title}</title>
    
    <!-- External Libraries -->
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    
    <style>
        /* ============================================================
           ENHANCED SOPHISTICATED STYLING
           Features: Glassmorphism, Gradients, Animations, Dark Mode
        ============================================================ */
        
        /* === BASE RESET === */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        /* === ROOT VARIABLES FOR THEMING === */
        :root {{
            /* Light Theme Colors */
            --bg-gradient-start: #f8fafc;
            --bg-gradient-mid: #e2e8f0;
            --bg-gradient-end: #cbd5e1;
            
            --primary-gradient-start: #667eea;
            --primary-gradient-end: #764ba2;
            
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-border: rgba(255, 255, 255, 0.2);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-tertiary: #94a3b8;
            
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --info-color: #3b82f6;
            
            --shadow-sm: 0 10px 30px rgba(0, 0, 0, 0.1);
            --shadow-md: 0 15px 40px rgba(0, 0, 0, 0.15);
            --shadow-lg: 0 20px 60px rgba(0, 0, 0, 0.3);
            --shadow-colored: 0 25px 60px rgba(102, 126, 234, 0.3);
            
            --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            --transition-fast: all 0.3s ease;
        }}
        
        /* === DARK THEME VARIABLES === */
        body.dark-theme {{
            --bg-gradient-start: #1a1a2e;
            --bg-gradient-mid: #16213e;
            --bg-gradient-end: #0f3460;
            
            --card-bg: rgba(30, 41, 59, 0.9);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #e2e8f0;
            --text-secondary: #cbd5e1;
            --text-tertiary: #94a3b8;
            
            --shadow-sm: 0 10px 30px rgba(0, 0, 0, 0.5);
            --shadow-md: 0 15px 40px rgba(0, 0, 0, 0.6);
            --shadow-lg: 0 20px 60px rgba(0, 0, 0, 0.8);
        }}
        
        /* === BODY BASE STYLES === */
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, 
                var(--bg-gradient-start) 0%, 
                var(--bg-gradient-mid) 50%, 
                var(--bg-gradient-end) 100%);
            background-attachment: fixed;
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
            transition: var(--transition-fast);
            min-height: 100vh;
        }}
        
        /* === CUSTOM SCROLLBAR === */
        ::-webkit-scrollbar {{
            width: 12px;
            height: 12px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(0, 0, 0, 0.1);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, var(--primary-gradient-start), var(--primary-gradient-end));
            border-radius: 6px;
            transition: var(--transition-fast);
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(180deg, var(--primary-gradient-end), var(--bg-gradient-end));
        }}
        
        /* === THEME TOGGLE BUTTON === */
        .theme-toggle {{
            position: fixed;
            top: 30px;
            right: 30px;
            z-index: 1000;
            background: var(--card-bg);
            backdrop-filter: blur(20px) saturate(180%);
            border-radius: 50px;
            padding: 12px 24px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--card-border);
            cursor: pointer;
            transition: var(--transition-smooth);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.05);
            box-shadow: var(--shadow-colored);
        }}
        
        .theme-toggle:active {{
            transform: scale(0.98);
        }}
        
        /* === REPORT CONTAINER === */
        .report-container {{
            max-width: 1400px;
            margin: 40px auto;
            padding: 0 20px 80px 20px;
        }}
        
        /* === SECTION WRAPPER WITH GLASSMORPHISM === */
        .section {{
            background: var(--card-bg);
            backdrop-filter: blur(20px) saturate(180%);
            border-radius: 24px;
            padding: 50px;
            margin: 30px 0;
            box-shadow: var(--shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.1);
            border: 1px solid var(--card-border);
            position: relative;
            overflow: hidden;
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        /* Animated gradient top border */
        .section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, 
                var(--primary-gradient-start), 
                var(--primary-gradient-end), 
                var(--bg-gradient-end), 
                var(--primary-gradient-start));
            background-size: 200% 100%;
            animation: shimmer 3s linear infinite;
        }}
        
        @keyframes shimmer {{
            0% {{ background-position: 0% 0%; }}
            100% {{ background-position: 200% 0%; }}
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* === SECTION HEADER === */
        .section-header {{
            text-align: center;
            margin-bottom: 50px;
            position: relative;
        }}
        
        .section-title {{
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, 
                var(--primary-gradient-start) 0%, 
                var(--primary-gradient-end) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            letter-spacing: -1px;
            line-height: 1.2;
        }}
        
        .section-subtitle {{
            font-size: 1.2rem;
            color: var(--text-secondary);
            font-weight: 500;
            letter-spacing: 0.5px;
        }}
        
        /* === STAT CARDS WITH 3D EFFECTS === */
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin: 35px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, 
                var(--card-bg) 0%, 
                var(--card-bg) 100%);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            border: 1px solid var(--card-border);
            box-shadow: var(--shadow-md), 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: var(--transition-smooth);
            position: relative;
            overflow: hidden;
        }}
        
        /* Gradient overlay on hover */
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, 
                transparent 0%, 
                rgba(102, 126, 234, 0.1) 100%);
            opacity: 0;
            transition: opacity 0.4s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: var(--shadow-colored), 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .stat-card:hover::before {{
            opacity: 1;
        }}
        
        /* Color variants with left border accent */
        .stat-card.success {{
            border-left: 5px solid var(--success-color);
        }}
        
        .stat-card.warning {{
            border-left: 5px solid var(--warning-color);
        }}
        
        .stat-card.danger {{
            border-left: 5px solid var(--danger-color);
        }}
        
        .stat-card.info {{
            border-left: 5px solid var(--info-color);
        }}
        
        .stat-card.default {{
            border-left: 5px solid var(--primary-gradient-start);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, 
                var(--primary-gradient-start) 0%, 
                var(--primary-gradient-end) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            line-height: 1.2;
        }}
        
        .stat-label {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .stat-description {{
            font-size: 0.85rem;
            color: var(--text-tertiary);
            font-weight: 500;
            line-height: 1.4;
        }}
        
        /* === INFO BOXES WITH GRADIENT BORDERS === */
        .info-box {{
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin: 25px 0;
            border: 1px solid var(--card-border);
            box-shadow: var(--shadow-sm);
            position: relative;
            overflow: hidden;
            transition: var(--transition-fast);
        }}
        
        /* Left gradient accent bar */
        .info-box::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            background: linear-gradient(180deg, 
                var(--primary-gradient-start), 
                var(--primary-gradient-end));
        }}
        
        .info-box:hover {{
            transform: translateX(5px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        }}
        
        .info-box.success::before {{
            background: linear-gradient(180deg, #10b981, #059669);
        }}
        
        .info-box.warning::before {{
            background: linear-gradient(180deg, #f59e0b, #d97706);
        }}
        
        .info-box.danger::before {{
            background: linear-gradient(180deg, #ef4444, #dc2626);
        }}
        
        .info-box.info::before {{
            background: linear-gradient(180deg, #3b82f6, #2563eb);
        }}
        
        .info-box h3,
        .info-box h4 {{
            color: var(--text-primary);
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .info-box p,
        .info-box ul,
        .info-box ol {{
            color: var(--text-secondary);
            line-height: 1.8;
        }}
        
        .info-box ul,
        .info-box ol {{
            padding-left: 25px;
            margin: 10px 0;
        }}
        
        .info-box li {{
            margin: 8px 0;
        }}
        
        .info-box strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}
        
        /* === SECTION DIVIDER === */
        .section-divider {{
            height: 2px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--primary-gradient-start), 
                var(--primary-gradient-end), 
                transparent);
            margin: 50px 0;
            border: none;
            opacity: 0.5;
        }}
        
        /* === ENHANCED DATA TABLES === */
        .data-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 25px 0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            background: var(--card-bg);
        }}
        
        .data-table thead {{
            background: linear-gradient(135deg, 
                var(--primary-gradient-start) 0%, 
                var(--primary-gradient-end) 100%);
        }}
        
        .data-table th {{
            padding: 18px 15px;
            text-align: left;
            font-weight: 700;
            color: white;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
        }}
        
        .data-table td {{
            padding: 15px;
            color: var(--text-primary);
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        body.dark-theme .data-table td {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .data-table tbody tr {{
            transition: var(--transition-fast);
        }}
        
        .data-table tbody tr:hover {{
            background: linear-gradient(90deg, 
                rgba(102, 126, 234, 0.1), 
                transparent);
            transform: scale(1.005);
        }}
        
        /* DataTables integration styling */
        .dataTables_wrapper {{
            padding: 20px;
            background: var(--card-bg);
            border-radius: 12px;
            margin: 25px 0;
            box-shadow: var(--shadow-sm);
        }}
        
        .dataTables_filter input,
        .dataTables_length select {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: 8px;
            transition: var(--transition-fast);
        }}
        
        .dataTables_filter input:focus,
        .dataTables_length select:focus {{
            outline: none;
            border-color: var(--primary-gradient-start);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        /* === PLOTLY CHART CONTAINERS === */
        .plotly-chart {{
            margin: 30px 0;
            padding: 25px;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--card-border);
            transition: var(--transition-fast);
        }}
        
        .plotly-chart:hover {{
            box-shadow: var(--shadow-md);
        }}
        
        /* === INFO SECTION === */
        .info-section {{
            margin: 40px 0;
        }}
        
        .info-section h3 {{
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, 
                var(--primary-gradient-start) 0%, 
                var(--primary-gradient-end) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        }}
        
        .info-section h4 {{
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 30px 0 20px 0;
        }}
        
        /* === COMPLETENESS BAR === */
        .completeness-bar {{
            width: 100%;
            height: 30px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            overflow: hidden;
            position: relative;
            margin: 15px 0;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        .completeness-fill {{
            height: 100%;
            background: linear-gradient(90deg, 
                var(--primary-gradient-start), 
                var(--primary-gradient-end));
            border-radius: 15px;
            transition: width 1s ease-out;
            position: relative;
            overflow: hidden;
        }}
        
        .completeness-fill::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.3), 
                transparent);
            animation: shimmer 2s linear infinite;
        }}
        
        .completeness-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: 700;
            font-size: 0.85rem;
            color: white;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }}
        
        /* === RESPONSIVE DESIGN === */
        @media (max-width: 1024px) {{
            .section {{
                padding: 40px 30px;
            }}
            
            .section-title {{
                font-size: 2.5rem;
            }}
        }}
        
        @media (max-width: 768px) {{
            .report-container {{
                padding: 0 15px 60px 15px;
            }}
            
            .section {{
                padding: 30px 20px;
                border-radius: 16px;
                margin: 20px 0;
            }}
            
            .section-title {{
                font-size: 2rem;
            }}
            
            .section-subtitle {{
                font-size: 1rem;
            }}
            
            .stat-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .stat-card {{
                padding: 25px;
            }}
            
            .stat-value {{
                font-size: 2rem;
            }}
            
            .theme-toggle {{
                top: 15px;
                right: 15px;
                padding: 10px 20px;
                font-size: 0.9rem;
            }}
            
            .data-table {{
                font-size: 0.85rem;
            }}
            
            .data-table th,
            .data-table td {{
                padding: 12px 10px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .section {{
                padding: 25px 15px;
            }}
            
            .section-title {{
                font-size: 1.75rem;
            }}
            
            .stat-value {{
                font-size: 1.75rem;
            }}
            
            .info-box {{
                padding: 20px;
            }}
        }}
        
        /* === UTILITY CLASSES === */
        .text-center {{
            text-align: center;
        }}
        
        .text-left {{
            text-align: left;
        }}
        
        .text-right {{
            text-align: right;
        }}
        
        .mb-0 {{ margin-bottom: 0; }}
        .mb-1 {{ margin-bottom: 10px; }}
        .mb-2 {{ margin-bottom: 20px; }}
        .mb-3 {{ margin-bottom: 30px; }}
        .mb-4 {{ margin-bottom: 40px; }}
        
        .mt-0 {{ margin-top: 0; }}
        .mt-1 {{ margin-top: 10px; }}
        .mt-2 {{ margin-top: 20px; }}
        .mt-3 {{ margin-top: 30px; }}
        .mt-4 {{ margin-top: 40px; }}
        
        /* === FADE-IN ANIMATION === */
        .fade-in {{
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }}
        
        .fade-in.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
</head>
<body>
    <!-- Theme Toggle Button -->
    <div class="theme-toggle" onclick="toggleTheme()" role="button" aria-label="Toggle theme">
        <span id="theme-icon">🌙</span>
        <span id="theme-text">Dark Mode</span>
    </div>
    
    <!-- Report Container -->
    <div class="report-container">
        <div class="section">
            <div class="section-header">
                <h1 class="section-title">Section {section_number}: {section_title}</h1>
                <p class="section-subtitle">Comprehensive Financial Analysis & Insights</p>
            </div>
            
            {content}
        </div>
    </div>
    
    <script>
        /* ============================================================
           JAVASCRIPT FUNCTIONALITY
           Theme Toggle, Scroll Animations, Initialization
        ============================================================ */
        
        // Theme Toggle Functionality
        function toggleTheme() {{
            const body = document.body;
            const icon = document.getElementById('theme-icon');
            const text = document.getElementById('theme-text');
            
            body.classList.toggle('dark-theme');
            
            if (body.classList.contains('dark-theme')) {{
                icon.textContent = '☀️';
                text.textContent = 'Light Mode';
                localStorage.setItem('theme', 'dark');
            }} else {{
                icon.textContent = '🌙';
                text.textContent = 'Dark Mode';
                localStorage.setItem('theme', 'light');
            }}
        }}
        
        // Load saved theme preference
        window.addEventListener('DOMContentLoaded', function() {{
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {{
                document.body.classList.add('dark-theme');
                document.getElementById('theme-icon').textContent = '☀️';
                document.getElementById('theme-text').textContent = 'Light Mode';
            }}
            
            // Initialize scroll animations
            initializeScrollAnimations();
            
            // Initialize DataTables if present
            if (typeof $ !== 'undefined' && $.fn.DataTable) {{
                $('.data-table').DataTable({{
                    pageLength: 10,
                    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                    order: [],
                    language: {{
                        search: "Search:",
                        lengthMenu: "Show _MENU_ entries",
                        info: "Showing _START_ to _END_ of _TOTAL_ entries",
                        paginate: {{
                            first: "First",
                            last: "Last",
                            next: "Next",
                            previous: "Previous"
                        }}
                    }}
                }});
            }}
        }});
        
        // Scroll Animations with Intersection Observer
        function initializeScrollAnimations() {{
            const observerOptions = {{
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }};
            
            const observer = new IntersectionObserver(function(entries) {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                        entry.target.classList.add('visible');
                    }}
                }});
            }}, observerOptions);
            
            // Observe all animatable elements
            document.querySelectorAll('.stat-card, .info-box, .plotly-chart, .data-table').forEach(el => {{
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'all 0.6s ease';
                observer.observe(el);
            }});
        }}
        
        // Smooth scroll to top function
        function scrollToTop() {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }}
        
        // Add scroll-to-top button if page is long
        window.addEventListener('scroll', function() {{
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Create scroll-to-top button if it doesn't exist
            let scrollBtn = document.getElementById('scroll-to-top');
            if (!scrollBtn && scrollTop > 300) {{
                scrollBtn = document.createElement('div');
                scrollBtn.id = 'scroll-to-top';
                scrollBtn.innerHTML = '↑';
                scrollBtn.style.cssText = `
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    width: 50px;
                    height: 50px;
                    background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: var(--shadow-md);
                    transition: var(--transition-smooth);
                    z-index: 999;
                `;
                scrollBtn.onclick = scrollToTop;
                document.body.appendChild(scrollBtn);
            }}
            
            // Show/hide scroll button
            if (scrollBtn) {{
                if (scrollTop > 300) {{
                    scrollBtn.style.opacity = '1';
                    scrollBtn.style.transform = 'scale(1)';
                }} else {{
                    scrollBtn.style.opacity = '0';
                    scrollBtn.style.transform = 'scale(0.8)';
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html


# =============================================================================
# STAT CARD COMPONENTS
# =============================================================================

def build_stat_card(
    label: str,
    value: str,
    description: str = "",
    type: str = "default"
) -> str:
    """
    Build a single stat card with enhanced styling.
    
    Args:
        label: Card label/title
        value: Main value to display
        description: Optional description text
        type: Card type ("success", "warning", "danger", "info", "default")
    
    Returns:
        HTML string for stat card
    """
    
    desc_html = f'<div class="stat-description">{description}</div>' if description else ""
    
    return f"""
    <div class="stat-card {type}">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
        {desc_html}
    </div>
    """


def build_stat_grid(cards: List[Dict[str, str]]) -> str:
    """
    Build a grid of stat cards.
    
    Args:
        cards: List of card dictionaries with keys:
               - label: str
               - value: str
               - description: str (optional)
               - type: str (optional, default "default")
    
    Returns:
        HTML string for stat grid
    """
    
    cards_html = ""
    for card in cards:
        cards_html += build_stat_card(
            label=card.get("label", ""),
            value=card.get("value", ""),
            description=card.get("description", ""),
            type=card.get("type", "default")
        )
    
    return f'<div class="stat-grid">{cards_html}</div>'


# =============================================================================
# INFO BOX COMPONENT
# =============================================================================

def build_info_box(
    content: str,
    box_type: str = "default",
    title: Optional[str] = None
) -> str:
    """
    Build an info box with gradient border accent.
    
    Args:
        content: HTML content for the box
        box_type: Box type ("success", "warning", "danger", "info", "default")
        title: Optional title for the box
    
    Returns:
        HTML string for info box
    """
    
    title_html = f"<h4>{title}</h4>" if title else ""
    
    return f"""
    <div class="info-box {box_type}">
        {title_html}
        {content}
    </div>
    """


# =============================================================================
# SECTION DIVIDER
# =============================================================================

def build_section_divider() -> str:
    """
    Build a gradient section divider.
    
    Returns:
        HTML string for divider
    """
    return '<div class="section-divider"></div>'


# =============================================================================
# DATA TABLE COMPONENT
# =============================================================================

def build_data_table(
    df: pd.DataFrame,
    table_id: str = "data-table",
    sortable: bool = True,
    searchable: bool = True,
    page_length: int = 10
) -> str:
    """
    Build an enhanced data table from DataFrame.
    
    Args:
        df: Pandas DataFrame
        table_id: Unique ID for the table
        sortable: Enable DataTables sorting
        searchable: Enable DataTables search
        page_length: Initial page length (-1 for all)
    
    Returns:
        HTML string for data table
    """
    
    if df.empty:
        return '<div class="info-box warning"><p>No data available for this table.</p></div>'
    
    # Generate table HTML
    table_class = "data-table"
    if sortable:
        table_class += " sortable"
    
    table_html = f'<table id="{table_id}" class="{table_class}">'
    
    # Table header
    table_html += "<thead><tr>"
    for col in df.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr></thead>"
    
    # Table body
    table_html += "<tbody>"
    for _, row in df.iterrows():
        table_html += "<tr>"
        for val in row:
            # Handle different data types
            if pd.isna(val):
                display_val = "—"
            elif isinstance(val, (int, float)):
                if isinstance(val, float):
                    display_val = f"{val:.2f}" if abs(val) < 1000 else f"{val:,.2f}"
                else:
                    display_val = f"{val:,}"
            else:
                display_val = str(val)
            
            table_html += f"<td>{display_val}</td>"
        table_html += "</tr>"
    table_html += "</tbody>"
    
    table_html += "</table>"
    
    # Add DataTables initialization if sortable
    if sortable:
        table_html += f"""
        <script>
            (function() {{
                // Wait for DOM and jQuery to be ready
                if (typeof $ === 'undefined' || typeof $.fn.DataTable === 'undefined') {{
                    console.warn('jQuery or DataTables not loaded yet for table {table_id}');
                    return;
                }}
                
                $(document).ready(function() {{
                    // Check if table is already initialized
                    if ($.fn.DataTable.isDataTable('#{table_id}')) {{
                        // Destroy existing instance
                        $('#{table_id}').DataTable().destroy();
                    }}
                    
                    // Initialize DataTable
                    $('#{table_id}').DataTable({{
                        pageLength: {page_length},
                        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                        order: [],
                        searching: {'true' if searchable else 'false'},
                        language: {{
                            search: "Search:",
                            lengthMenu: "Show _MENU_ entries",
                            info: "Showing _START_ to _END_ of _TOTAL_ entries",
                            paginate: {{
                                first: "First",
                                last: "Last",
                                next: "Next",
                                previous: "Previous"
                            }}
                        }},
                        // Prevent reinitialization warnings
                        destroy: true
                    }});
                }});
            }})();
        </script>
        """
    
    return table_html


# =============================================================================
# PLOTLY CHART COMPONENT
# =============================================================================

def build_plotly_chart(
    fig_data: Dict[str, Any],
    div_id: str = "plotly-chart",
    height: int = 500
) -> str:
    """
    Build a Plotly chart with enhanced container.
    
    Args:
        fig_data: Plotly figure data dictionary with 'data' and 'layout' keys
        div_id: Unique ID for the chart div
        height: Chart height in pixels
    
    Returns:
        HTML string for Plotly chart
    """
    
    # Ensure layout has default settings
    if 'layout' not in fig_data:
        fig_data['layout'] = {}
    
    # Merge with default layout settings
    default_layout = {
        'autosize': True,
        'margin': {'l': 50, 'r': 30, 't': 50, 'b': 50},
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Segoe UI, sans-serif', 'color': '#1e293b'},
        'hovermode': 'closest'
    }
    
    for key, value in default_layout.items():
        if key not in fig_data['layout']:
            fig_data['layout'][key] = value
    
    # Convert to JSON
    fig_json = json.dumps(fig_data)
    
    return f"""
    <div class="plotly-chart">
        <div id="{div_id}" style="width:100%; height:{height}px;"></div>
        <script>
            Plotly.newPlot('{div_id}', {fig_json}.data, {fig_json}.layout, {{responsive: true}});
        </script>
    </div>
    """


# =============================================================================
# SIMPLE CHART BUILDERS
# =============================================================================

def build_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    div_id: str = "bar-chart",
    color: str = "#667eea"
) -> str:
    """
    Build a simple bar chart.
    
    Args:
        labels: X-axis labels
        values: Y-axis values
        title: Chart title
        div_id: Unique div ID
        color: Bar color
    
    Returns:
        HTML string for bar chart
    """
    
    fig_data = {
        'data': [{
            'type': 'bar',
            'x': labels,
            'y': values,
            'marker': {'color': color},
            'hovertemplate': '<b>%{x}</b><br>%{y:.2f}<extra></extra>'
        }],
        'layout': {
            'title': {'text': title, 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': ''},
            'yaxis': {'title': 'Value'}
        }
    }
    
    return build_plotly_chart(fig_data, div_id)


def build_multi_line_chart(
    x_data: List,
    y_datasets: List[Dict[str, Any]],
    title: str = "",
    div_id: str = "line-chart"
) -> str:
    """
    Build a multi-line chart.
    
    Args:
        x_data: X-axis data (shared across all lines)
        y_datasets: List of datasets, each with keys:
                   - name: str (line name)
                   - y: List (y values)
                   - color: str (optional)
        title: Chart title
        div_id: Unique div ID
    
    Returns:
        HTML string for line chart
    """
    
    traces = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#10b981', '#f59e0b', '#ef4444']
    
    for i, dataset in enumerate(y_datasets):
        trace = {
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': x_data,
            'y': dataset['y'],
            'name': dataset['name'],
            'line': {'color': dataset.get('color', colors[i % len(colors)]), 'width': 3},
            'marker': {'size': 8}
        }
        traces.append(trace)
    
    fig_data = {
        'data': traces,
        'layout': {
            'title': {'text': title, 'font': {'size': 18, 'weight': 'bold'}},
            'xaxis': {'title': ''},
            'yaxis': {'title': 'Value'},
            'hovermode': 'x unified'
        }
    }
    
    return build_plotly_chart(fig_data, div_id)


# =============================================================================
# COMPLETENESS BAR
# =============================================================================

def build_completeness_bar(
    percentage: float,
    label: str = "Data Completeness"
) -> str:
    """
    Build a completeness/progress bar.
    
    Args:
        percentage: Completion percentage (0-100)
        label: Label for the bar
    
    Returns:
        HTML string for completeness bar
    """
    
    percentage = max(0, min(100, percentage))  # Clamp to 0-100
    
    return f"""
    <div style="margin: 20px 0;">
        <div style="margin-bottom: 8px; font-weight: 600; color: var(--text-secondary);">{label}</div>
        <div class="completeness-bar">
            <div class="completeness-fill" style="width: {percentage}%;">
                <span class="completeness-text">{percentage:.1f}%</span>
            </div>
        </div>
    </div>
    """


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================

def format_currency(
    value: float,
    currency: str = "$",
    decimals: int = 2,
    millions: bool = False
) -> str:
    """
    Format a number as currency.
    
    Args:
        value: Numeric value
        currency: Currency symbol
        decimals: Number of decimal places
        millions: If True, display in millions (e.g., $1.5M)
    
    Returns:
        Formatted currency string
    """
    
    if pd.isna(value):
        return "—"
    
    if millions:
        value = value / 1_000_000
        suffix = "M"
    else:
        suffix = ""
    
    formatted = f"{value:,.{decimals}f}"
    return f"{currency}{formatted}{suffix}"


def format_percentage(
    value: float,
    decimals: int = 1,
    include_sign: bool = False
) -> str:
    """
    Format a decimal as percentage.
    
    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        decimals: Number of decimal places
        include_sign: Include + sign for positive values
    
    Returns:
        Formatted percentage string
    """
    
    if pd.isna(value):
        return "—"
    
    percentage = value * 100
    formatted = f"{percentage:.{decimals}f}%"
    
    if include_sign and percentage > 0:
        formatted = f"+{formatted}"
    
    return formatted


def format_number(
    value: float,
    decimals: int = 2,
    thousands_sep: bool = True
) -> str:
    """
    Format a number with optional thousands separator.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        thousands_sep: Include thousands separator
    
    Returns:
        Formatted number string
    """
    
    if pd.isna(value):
        return "—"
    
    if thousands_sep:
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:.{decimals}f}"
    
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
# =============================================================================
# ENHANCED TABLE STYLING HELPERS (Add to html_utils.py)
# =============================================================================

def build_badge(text: str, badge_type: str = "default") -> str:
    """
    Create a styled badge/pill for categorical values.
    
    Args:
        text: Badge text content
        badge_type: "success", "warning", "danger", "info", "default"
    
    Returns:
        HTML string for styled badge
    """
    
    color_map = {
        "success": "background: linear-gradient(135deg, #10b981, #059669); color: white;",
        "warning": "background: linear-gradient(135deg, #f59e0b, #d97706); color: white;",
        "danger": "background: linear-gradient(135deg, #ef4444, #dc2626); color: white;",
        "info": "background: linear-gradient(135deg, #3b82f6, #2563eb); color: white;",
        "default": "background: linear-gradient(135deg, #667eea, #764ba2); color: white;"
    }
    
    style = color_map.get(badge_type, color_map["default"])
    
    return f"""
    <span style="{style} padding: 4px 12px; border-radius: 12px; 
                  font-size: 0.85rem; font-weight: 600; display: inline-block;
                  box-shadow: 0 2px 4px rgba(0,0,0,0.1); white-space: nowrap;">
        {text}
    </span>
    """


def build_score_badge(score: float, max_score: float = 10.0) -> str:
    """
    Create a colored badge based on score value.
    
    Args:
        score: Numeric score
        max_score: Maximum possible score (default 10.0)
    
    Returns:
        HTML string for score badge with appropriate color
    """
    
    percentage = (score / max_score) * 100
    
    if percentage >= 75:
        badge_type = "success"
        emoji = "🟢"
    elif percentage >= 50:
        badge_type = "info"
        emoji = "🔵"
    elif percentage >= 25:
        badge_type = "warning"
        emoji = "🟡"
    else:
        badge_type = "danger"
        emoji = "🔴"
    
    return f'{emoji} {build_badge(f"{score:.1f}/{max_score}", badge_type)}'


def build_colored_cell(value: str, cell_type: str = "default") -> str:
    """
    Create a table cell with background color based on type.
    
    Args:
        value: Cell content
        cell_type: "excellent", "good", "fair", "poor", "neutral"
    
    Returns:
        HTML string for colored cell
    """
    
    color_map = {
        "excellent": "background-color: rgba(16, 185, 129, 0.15); color: #059669; font-weight: 600;",
        "good": "background-color: rgba(59, 130, 246, 0.15); color: #2563eb; font-weight: 600;",
        "fair": "background-color: rgba(245, 158, 11, 0.15); color: #d97706; font-weight: 600;",
        "poor": "background-color: rgba(239, 68, 68, 0.15); color: #dc2626; font-weight: 600;",
        "neutral": "color: var(--text-primary);"
    }
    
    style = color_map.get(cell_type, color_map["neutral"])
    
    return f'<span style="{style} padding: 4px 8px; border-radius: 6px; display: inline-block;">{value}</span>'


def build_enhanced_table(
    df: pd.DataFrame,
    table_id: str = "enhanced-table",
    color_columns: Dict[str, callable] = None,
    badge_columns: List[str] = None,
    sortable: bool = True,
    searchable: bool = True
) -> str:
    """
    Build an enhanced table with conditional formatting and badges.
    
    Args:
        df: Pandas DataFrame
        table_id: Unique table ID
        color_columns: Dict mapping column names to functions that return color type
                      Example: {'Health': lambda x: 'excellent' if x == 'Excellent' else 'good'}
        badge_columns: List of column names to render as badges
        sortable: Enable DataTables sorting
        searchable: Enable DataTables search
    
    Returns:
        HTML string for enhanced table
    """
    
    if df.empty:
        return '<div class="info-box warning"><p>No data available for this table.</p></div>'
    
    color_columns = color_columns or {}
    badge_columns = badge_columns or []
    
    # Generate table HTML with enhanced styling
    table_class = "data-table"
    if sortable:
        table_class += " sortable"
    
    table_html = f'<table id="{table_id}" class="{table_class}">'
    
    # Table header
    table_html += "<thead><tr>"
    for col in df.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr></thead>"
    
    # Table body with enhanced styling
    table_html += "<tbody>"
    for _, row in df.iterrows():
        table_html += "<tr>"
        for col in df.columns:
            val = row[col]
            
            # Handle different data types
            if pd.isna(val):
                display_val = "—"
            else:
                display_val = str(val)
            
            # Apply color coding if specified
            if col in color_columns:
                color_type = color_columns[col](val)
                display_val = build_colored_cell(display_val, color_type)
            
            # Apply badge styling if specified
            elif col in badge_columns:
                # Infer badge type from value
                if isinstance(val, str):
                    if any(word in val.lower() for word in ['excellent', 'strong', 'wide', 'leader']):
                        badge_type = 'success'
                    elif any(word in val.lower() for word in ['good', 'adequate', 'narrow', 'established']):
                        badge_type = 'info'
                    elif any(word in val.lower() for word in ['fair', 'moderate', 'limited']):
                        badge_type = 'warning'
                    elif any(word in val.lower() for word in ['poor', 'weak', 'no', 'none']):
                        badge_type = 'danger'
                    else:
                        badge_type = 'default'
                    display_val = build_badge(display_val, badge_type)
            
            table_html += f"<td>{display_val}</td>"
        table_html += "</tr>"
    table_html += "</tbody>"
    
    table_html += "</table>"
    
    # Add DataTables initialization if sortable
    if sortable:
        table_html += f"""
        <script>
            (function() {{
                if (typeof $ === 'undefined' || typeof $.fn.DataTable === 'undefined') {{
                    console.warn('jQuery or DataTables not loaded yet for table {table_id}');
                    return;
                }}
                
                $(document).ready(function() {{
                    if ($.fn.DataTable.isDataTable('#{table_id}')) {{
                        $('#{table_id}').DataTable().destroy();
                    }}
                    
                    $('#{table_id}').DataTable({{
                        pageLength: 10,
                        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                        order: [],
                        searching: {'true' if searchable else 'false'},
                        language: {{
                            search: "Search:",
                            lengthMenu: "Show _MENU_ entries",
                            info: "Showing _START_ to _END_ of _TOTAL_ entries",
                            paginate: {{
                                first: "First",
                                last: "Last",
                                next: "Next",
                                previous: "Previous"
                            }}
                        }},
                        destroy: true
                    }});
                }});
            }})();
        </script>
        """
    
    return table_html


def build_heatmap_table(
    df: pd.DataFrame,
    numeric_columns: List[str],
    table_id: str = "heatmap-table"
) -> str:
    """
    Build a table with gradient heatmap coloring for numeric columns.
    
    Args:
        df: Pandas DataFrame
        numeric_columns: List of column names to apply heatmap coloring
        table_id: Unique table ID
    
    Returns:
        HTML string for heatmap table
    """
    
    if df.empty:
        return '<div class="info-box warning"><p>No data available for this table.</p></div>'
    
    # Calculate min/max for each numeric column
    ranges = {}
    for col in numeric_columns:
        if col in df.columns:
            col_data = pd.to_numeric(df[col], errors='coerce')
            ranges[col] = {
                'min': col_data.min(),
                'max': col_data.max()
            }
    
    table_html = f'<table id="{table_id}" class="data-table" style="width: 100%;">'
    
    # Table header
    table_html += "<thead><tr>"
    for col in df.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr></thead>"
    
    # Table body with heatmap
    table_html += "<tbody>"
    for _, row in df.iterrows():
        table_html += "<tr>"
        for col in df.columns:
            val = row[col]
            
            # Handle missing values
            if pd.isna(val):
                table_html += "<td>—</td>"
                continue
            
            # Apply heatmap if numeric column
            if col in numeric_columns and col in ranges:
                numeric_val = pd.to_numeric(val, errors='coerce')
                if not pd.isna(numeric_val):
                    # Normalize to 0-1 range
                    range_min = ranges[col]['min']
                    range_max = ranges[col]['max']
                    if range_max > range_min:
                        normalized = (numeric_val - range_min) / (range_max - range_min)
                    else:
                        normalized = 0.5
                    
                    # Color gradient from red (0) to yellow (0.5) to green (1)
                    if normalized < 0.5:
                        # Red to Yellow
                        r, g, b = 239, int(68 + (187 * normalized * 2)), 68
                    else:
                        # Yellow to Green
                        r, g, b = int(245 - (229 * (normalized - 0.5) * 2)), int(158 + (27 * (normalized - 0.5) * 2)), int(11 + (105 * (normalized - 0.5) * 2))
                    
                    bg_color = f"rgba({r}, {g}, {b}, 0.2)"
                    text_color = f"rgb({int(r*0.7)}, {int(g*0.7)}, {int(b*0.7)})"
                    
                    table_html += f'<td style="background-color: {bg_color}; color: {text_color}; font-weight: 600; text-align: center;">{val}</td>'
                else:
                    table_html += f"<td>{val}</td>"
            else:
                table_html += f"<td>{val}</td>"
        
        table_html += "</tr>"
    table_html += "</tbody>"
    table_html += "</table>"
    
    return table_html
# =============================================================================
# ADVANCED STYLING HELPERS - Phase 3 (Add to html_utils.py)
# =============================================================================

def build_comparison_bars(
    labels: List[str],
    values: List[float],
    benchmark: Optional[float] = None,
    title: str = "",
    color_threshold_good: float = None,
    color_threshold_bad: float = None
) -> str:
    """
    Build horizontal comparison bars with conditional coloring.
    
    Args:
        labels: Bar labels
        values: Bar values
        benchmark: Optional benchmark line to display
        title: Chart title
        color_threshold_good: Values above this are green
        color_threshold_bad: Values below this are red
    
    Returns:
        HTML string for comparison bars
    """
    
    # Determine colors based on thresholds
    colors = []
    for val in values:
        if color_threshold_good and val >= color_threshold_good:
            colors.append('#10b981')  # Green
        elif color_threshold_bad and val <= color_threshold_bad:
            colors.append('#ef4444')  # Red
        else:
            colors.append('#3b82f6')  # Blue
    
    bars_html = f'<div style="margin: 20px 0;"><h4>{title}</h4>'
    
    max_val = max(values) if values else 1
    
    for label, value, color in zip(labels, values, colors):
        bar_width = (value / max_val * 100) if max_val > 0 else 0
        
        bars_html += f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-weight: 600; font-size: 0.9rem;">{label}</span>
                <span style="font-weight: 700; color: {color};">{value:.2f}</span>
            </div>
            <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 8px; height: 24px; position: relative;">
                <div style="width: {bar_width}%; background: {color}; border-radius: 8px; height: 100%; 
                           transition: width 0.6s ease; display: flex; align-items: center; padding: 0 8px;">
                </div>
                {f'<div style="position: absolute; left: {(benchmark/max_val*100):.1f}%; top: -5px; bottom: -5px; width: 2px; background: red; opacity: 0.7;"></div>' if benchmark else ''}
            </div>
        </div>
        """
    
    if benchmark:
        bars_html += f'<div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary);"><span style="color: red;">▬</span> Benchmark: {benchmark:.2f}</div>'
    
    bars_html += '</div>'
    
    return bars_html


def build_metric_comparison_grid(
    companies: List[str],
    metrics: Dict[str, List[float]],
    metric_formats: Dict[str, str] = None
) -> str:
    """
    Build a visual comparison grid with color coding.
    
    Args:
        companies: List of company names
        metrics: Dict mapping metric names to lists of values (one per company)
        metric_formats: Optional dict mapping metric names to format strings
                       ('currency', 'percentage', 'number', 'ratio')
    
    Returns:
        HTML string for comparison grid
    """
    
    metric_formats = metric_formats or {}
    
    grid_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">'
    
    for metric_name, values in metrics.items():
        # Calculate relative performance
        max_val = max(values) if values else 1
        min_val = min(values) if values else 0
        range_val = max_val - min_val if max_val > min_val else 1
        
        format_type = metric_formats.get(metric_name, 'number')
        
        grid_html += f'<div style="background: var(--card-bg); padding: 15px; border-radius: 12px; border: 1px solid var(--card-border); box-shadow: var(--shadow-sm);">'
        grid_html += f'<h5 style="margin: 0 0 10px 0; color: var(--text-primary); font-size: 0.9rem;">{metric_name}</h5>'
        
        for company, value in zip(companies, values):
            # Normalize to 0-1 for color coding
            normalized = (value - min_val) / range_val if range_val > 0 else 0.5
            
            # Color gradient
            if normalized >= 0.7:
                bg_color = 'rgba(16, 185, 129, 0.2)'
                text_color = '#059669'
            elif normalized >= 0.3:
                bg_color = 'rgba(59, 130, 246, 0.2)'
                text_color = '#2563eb'
            else:
                bg_color = 'rgba(239, 68, 68, 0.2)'
                text_color = '#dc2626'
            
            # Format value
            if format_type == 'currency':
                display_val = f"${value:,.0f}"
            elif format_type == 'percentage':
                display_val = f"{value:.1f}%"
            elif format_type == 'ratio':
                display_val = f"{value:.2f}x"
            else:
                display_val = f"{value:.2f}"
            
            grid_html += f"""
            <div style="display: flex; justify-content: space-between; padding: 6px 8px; margin: 4px 0; 
                       background: {bg_color}; border-radius: 6px;">
                <span style="font-size: 0.85rem; color: var(--text-secondary);">{company[:12]}</span>
                <span style="font-weight: 700; color: {text_color}; font-size: 0.9rem;">{display_val}</span>
            </div>
            """
        
        grid_html += '</div>'
    
    grid_html += '</div>'
    
    return grid_html


def build_quadrant_badge(x_score: float, y_score: float, threshold: float = 5.0) -> str:
    """
    Build a badge indicating quadrant position (e.g., Growth/Value matrix).
    
    Args:
        x_score: Horizontal axis score (e.g., Value)
        y_score: Vertical axis score (e.g., Growth)
        threshold: Midpoint threshold (default 5.0)
    
    Returns:
        HTML badge indicating quadrant
    """
    
    if y_score >= threshold and x_score >= threshold:
        quadrant = "Growth Premium"
        badge_type = "success"
        emoji = "🚀"
    elif y_score >= threshold and x_score < threshold:
        quadrant = "Growth (Expensive)"
        badge_type = "warning"
        emoji = "⚠️"
    elif y_score < threshold and x_score >= threshold:
        quadrant = "Deep Value"
        badge_type = "info"
        emoji = "💎"
    else:
        quadrant = "Value Trap Risk"
        badge_type = "danger"
        emoji = "⛔"
    
    return f'{emoji} {build_badge(quadrant, badge_type)}'


def build_progress_indicator(
    current: float,
    target: float,
    label: str = "",
    show_percentage: bool = True
) -> str:
    """
    Build a progress indicator showing current vs target.
    
    Args:
        current: Current value
        target: Target value
        label: Label text
        show_percentage: Show percentage completion
    
    Returns:
        HTML string for progress indicator
    """
    
    percentage = (current / target * 100) if target > 0 else 0
    percentage = min(100, max(0, percentage))
    
    if percentage >= 100:
        color = '#10b981'
        status = "Target Achieved"
    elif percentage >= 75:
        color = '#3b82f6'
        status = "On Track"
    elif percentage >= 50:
        color = '#f59e0b'
        status = "Needs Attention"
    else:
        color = '#ef4444'
        status = "Below Target"
    
    return f"""
    <div style="margin: 15px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-weight: 600;">{label}</span>
            <span style="font-weight: 600; color: {color};">{status}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;">
            <span>Current: {current:.2f}</span>
            <span>Target: {target:.2f}</span>
        </div>
        <div style="width: 100%; background: rgba(0,0,0,0.1); border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="width: {percentage}%; background: {color}; height: 100%; border-radius: 10px; 
                       transition: width 0.8s ease; display: flex; align-items: center; justify-content: center;">
                {f'<span style="color: white; font-size: 0.75rem; font-weight: 700;">{percentage:.0f}%</span>' if show_percentage and percentage > 15 else ''}
            </div>
        </div>
    </div>
    """


def build_summary_card(
    title: str,
    metrics: List[Dict[str, str]],
    card_type: str = "default"
) -> str:
    """
    Build a summary card with multiple metrics.
    
    Args:
        title: Card title
        metrics: List of dicts with 'label' and 'value' keys
        card_type: "success", "warning", "danger", "info", "default"
    
    Returns:
        HTML string for summary card
    """
    
    border_colors = {
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#3b82f6",
        "default": "#667eea"
    }
    
    border_color = border_colors.get(card_type, border_colors["default"])
    
    card_html = f"""
    <div style="background: var(--card-bg); border-left: 4px solid {border_color}; 
               border-radius: 12px; padding: 20px; margin: 15px 0;
               box-shadow: var(--shadow-sm); border: 1px solid var(--card-border);">
        <h4 style="margin: 0 0 15px 0; color: var(--text-primary); font-size: 1.1rem;">{title}</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;">
    """
    
    for metric in metrics:
        card_html += f"""
        <div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px;">
                {metric.get('label', '')}
            </div>
            <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-primary);">
                {metric.get('value', '')}
            </div>
        </div>
        """
    
    card_html += """
        </div>
    </div>
    """
    
    return card_html