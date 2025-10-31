"""
PDF Configuration Module

Handles PDF-specific settings including:
- PDF engine selection (pdflatex, lualatex, xelatex)
- Page geometry and margins
- Headers and footers
- LaTeX packages and styling
"""

from typing import Dict, Any, List
from pathlib import Path


# =============================================================================
# PDF ENGINE SELECTION
# =============================================================================

def get_pdf_engine(layout_name: str = 'classic') -> str:
    """
    Determine appropriate PDF engine for layout.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        PDF engine name ('pdflatex' or 'lualatex')
    """
    from ePy_docs.core._layouts import requires_lualatex
    
    # Handwritten layout requires LuaLaTeX for OpenType fonts
    if requires_lualatex(layout_name):
        return 'lualatex'
    
    # Default to pdflatex for other layouts
    return 'pdflatex'


# =============================================================================
# PDF GEOMETRY CONFIGURATION
# =============================================================================

def get_pdf_geometry(layout_name: str = 'classic') -> List[str]:
    """
    Get PDF page geometry settings for layout.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        List of geometry strings for Quarto (e.g., ['top=2.5cm', 'bottom=2.5cm'])
    """
    from ePy_docs.core._layouts import get_layout_margins
    
    margins = get_layout_margins(layout_name)
    
    return [
        f"top={margins['top']}cm",
        f"bottom={margins['bottom']}cm",
        f"left={margins['left']}cm",
        f"right={margins['right']}cm"
    ]


# =============================================================================
# PDF HEADER CONFIGURATION
# =============================================================================

def get_pdf_header_config(layout_name: str = 'classic') -> str:
    """
    Generate LaTeX include-in-header configuration.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        LaTeX commands for document header
    """
    from ePy_docs.core._layouts import get_font_latex_config, get_layout_colors
    
    # Get font configuration (empty for non-custom fonts)
    font_config = get_font_latex_config(layout_name)
    
    # Get colors
    colors = get_layout_colors(layout_name)
    primary_rgb = _hex_to_rgb(colors['primary'])
    secondary_rgb = _hex_to_rgb(colors['secondary'])
    background_rgb = _hex_to_rgb(colors['background'])
    
    # Generate LaTeX header
    header = rf'''
\usepackage[utf8]{{inputenc}}
\usepackage{{fontenc}}
\usepackage{{lmodern}}
{font_config}

\usepackage{{xcolor}}
\definecolor{{pagebackground}}{{RGB}}{{{primary_rgb}}}
\definecolor{{brandPrimary}}{{RGB}}{{{primary_rgb}}}
\definecolor{{brandSecondary}}{{RGB}}{{{secondary_rgb}}}

\usepackage{{fancyhdr}}
\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0.4pt}}

\usepackage{{graphicx}}
\usepackage{{float}}
\usepackage{{caption}}

\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{amsfonts}}
'''
    
    return header.strip()


# =============================================================================
# PDF CONFIGURATION DICT
# =============================================================================

def get_pdf_config(
    layout_name: str = 'classic',
    document_type: str = 'article',
    **kwargs
) -> Dict[str, Any]:
    """
    Generate complete PDF configuration for Quarto.
    
    Args:
        layout_name: Name of the layout
        document_type: LaTeX document class ('article', 'report', 'book')
        **kwargs: Additional PDF options
        
    Returns:
        Dictionary with PDF configuration for Quarto YAML
    """
    from ePy_docs.core._layouts import get_layout
    
    layout = get_layout(layout_name)
    
    config = {
        'pdf-engine': get_pdf_engine(layout_name),
        'documentclass': document_type,
        'geometry': get_pdf_geometry(layout_name),
        'linestretch': layout['line_spacing'],
        'fontsize': kwargs.get('fontsize', '12pt'),
        'papersize': kwargs.get('papersize', 'letter'),
        'number-sections': kwargs.get('number_sections', True),
        'colorlinks': kwargs.get('colorlinks', True),
        'toc': kwargs.get('toc', True),
        'toc-depth': kwargs.get('toc_depth', 3),
        'lof': kwargs.get('lof', False),  # List of figures
        'lot': kwargs.get('lot', False),  # List of tables
        'fig-pos': 'H',  # Figure position
        'fig-cap-location': 'bottom',
        'tbl-cap-location': 'top',
        'include-in-header': {
            'text': get_pdf_header_config(layout_name)
        }
    }
    
    return config


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _hex_to_rgb(hex_color: str) -> str:
    """
    Convert hex color to RGB string for LaTeX.
    
    Args:
        hex_color: Hex color string (e.g., '#FF0000')
        
    Returns:
        RGB string for LaTeX (e.g., '255,0,0')
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return f"{r},{g},{b}"


def validate_document_class(document_class: str) -> bool:
    """
    Validate LaTeX document class.
    
    Args:
        document_class: Document class name
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If document class is invalid
    """
    valid_classes = ['article', 'report', 'book', 'memoir', 'scrartcl', 'scrreprt', 'scrbook']
    
    if document_class not in valid_classes:
        raise ValueError(
            f"Invalid document class '{document_class}'. "
            f"Valid classes: {', '.join(valid_classes)}"
        )
    
    return True
