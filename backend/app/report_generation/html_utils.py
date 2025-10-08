"""Minimal HTML utilities for report generation."""

def generate_section_wrapper(
    section_number: int,
    section_name: str,
    content: str
) -> str:
    """
    Wrap section content in standard HTML document structure.
    Each section builds its own HTML content.
    """
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