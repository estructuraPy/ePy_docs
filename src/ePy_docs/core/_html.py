"""
HTML Configuration Module

Handles HTML-specific settings including:
- CSS generation and styling
- Font embedding (@font-face)
- Responsive design settings
- HTML themes
"""

from typing import Dict, Any
from pathlib import Path


# =============================================================================
# HTML CONFIGURATION
# =============================================================================

def get_html_config(
    layout_name: str = 'classic',
    **kwargs
) -> Dict[str, Any]:
    """
    Generate complete HTML configuration for Quarto.
    
    Args:
        layout_name: Name of the layout
        **kwargs: Additional HTML options
        
    Returns:
        Dictionary with HTML configuration for Quarto YAML
    """
    from ePy_docs.core._layouts import get_layout
    
    layout = get_layout(layout_name)
    
    config = {
        'theme': kwargs.get('theme', 'default'),
        'css': kwargs.get('css', 'styles.css'),
        'toc': kwargs.get('toc', True),
        'toc-depth': kwargs.get('toc_depth', 3),
        'number-sections': kwargs.get('number_sections', True),
        'code-fold': kwargs.get('code_fold', False),
        'code-tools': kwargs.get('code_tools', False),
        'html-math-method': kwargs.get('html_math_method', 'mathjax'),
        'self-contained': kwargs.get('self_contained', True),
        'embed-resources': kwargs.get('embed_resources', True),
        'fig-align': 'center',
        'fig-cap-location': 'bottom',
        'tbl-cap-location': 'top',
        'fig-responsive': True,
        'fig-dpi': 150,
        'fig-width': 7,
        'fig-height': 4.2
    }
    
    return config


# =============================================================================
# CSS GENERATION
# =============================================================================

def generate_css(layout_name: str = 'classic') -> str:
    """
    Generate CSS stylesheet for layout.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        CSS stylesheet as string
    """
    from ePy_docs.core._layouts import get_layout_colors, get_font_css_config, get_layout
    from ePy_docs.core._config import get_config_section
    
    # Get font configuration (includes @font-face for custom fonts)
    font_css = get_font_css_config(layout_name)
    
    # Get layout configuration
    layout = get_layout(layout_name)
    
    # Get format configuration for font families
    format_config = get_config_section('format')
    font_families = format_config.get('font_families', {})
    
    # Get font family from layout
    font_family_key = layout.get('font_family', 'sans_technical')
    
    # Build font-family CSS value
    if font_family_key in font_families:
        font_config = font_families[font_family_key]
        primary_font = font_config['primary']
        fallback = font_config.get('fallback', 'sans-serif')
        body_font_family = f"'{primary_font}', {fallback}"
    else:
        # Fallback to generic font family
        body_font_family = font_family_key if font_family_key in ['serif', 'sans-serif', 'monospace'] else 'sans-serif'
    
    # Get colors
    colors = get_layout_colors(layout_name)
    
    css = f'''
/* ePy_docs Generated Stylesheet - {layout_name} Layout */

{font_css}

/* Color Scheme */
:root {{
    --color-primary: {colors['primary']};
    --color-secondary: {colors['secondary']};
    --color-background: {colors['background']};
}}

/* Body Styling */
body {{
    font-family: {body_font_family};
    background-color: var(--color-background);
    color: #333;
    line-height: 1.6;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    color: var(--color-primary);
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}}

h1 {{
    font-size: 2.5em;
    border-bottom: 2px solid var(--color-primary);
    padding-bottom: 0.3em;
}}

h2 {{
    font-size: 2em;
    border-bottom: 1px solid var(--color-secondary);
    padding-bottom: 0.2em;
}}

/* Links */
a {{
    color: var(--color-primary);
    text-decoration: none;
}}

a:hover {{
    color: var(--color-secondary);
    text-decoration: underline;
}}

/* Tables */
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}

th {{
    background-color: var(--color-primary);
    color: white;
    padding: 12px;
    text-align: left;
}}

td {{
    padding: 10px;
    border: 1px solid #ddd;
}}

tr:nth-child(even) {{
    background-color: #f9f9f9;
}}

/* Code Blocks */
pre {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    overflow-x: auto;
}}

code {{
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Courier New', Courier, monospace;
}}

/* Figures */
figure {{
    margin: 1.5em 0;
    text-align: center;
}}

figcaption {{
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
}}

/* Callouts/Admonitions */
.callout {{
    padding: 1em;
    margin: 1em 0;
    border-left: 4px solid var(--color-primary);
    background-color: #f0f0f0;
    border-radius: 4px;
}}

.callout-note {{
    border-left-color: #3498db;
    background-color: #ebf5fb;
}}

.callout-warning {{
    border-left-color: #f39c12;
    background-color: #fef5e7;
}}

.callout-important {{
    border-left-color: #e74c3c;
    background-color: #fadbd8;
}}

.callout-tip {{
    border-left-color: #2ecc71;
    background-color: #eafaf1;
}}
'''
    
    return css.strip()


# =============================================================================
# HTML UTILITIES
# =============================================================================

def save_css_file(css_content: str, output_path: Path) -> Path:
    """
    Save CSS content to file.
    
    Args:
        css_content: CSS stylesheet content
        output_path: Path to save CSS file
        
    Returns:
        Path to saved CSS file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return output_path


def get_html_theme(layout_name: str = 'classic') -> str:
    """
    Get recommended Quarto HTML theme for layout.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        Quarto theme name
    """
    theme_map = {
        'classic': 'cosmo',
        'modern': 'flatly',
        'handwritten': 'default',  # Custom CSS handles styling
        'academic': 'journal',
        'minimal': 'minty'
    }
    
    return theme_map.get(layout_name, 'default')
