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
    
    Uses xelatex for all layouts - better Unicode and font support.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        PDF engine name (always 'xelatex')
    """
    # Use xelatex for all layouts
    # Better Unicode support and custom font handling
    return 'xelatex'


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
    from ePy_docs.core._config import get_layout_margins
    
    margins = get_layout_margins(layout_name)
    
    # Margins in layouts are in inches (see _units annotation)
    return [
        f"top={margins['top']}in",
        f"bottom={margins['bottom']}in",
        f"left={margins['left']}in",
        f"right={margins['right']}in"
    ]


# =============================================================================
# PDF HEADER CONFIGURATION
# =============================================================================

def get_pdf_header_config(layout_name: str = 'classic', fonts_dir: Path = None) -> str:
    """
    Generate LaTeX include-in-header configuration.
    
    Args:
        layout_name: Name of the layout
        fonts_dir: Absolute path to fonts directory (for font loading)
        
    Returns:
        LaTeX commands for document header
    """
    from ePy_docs.core._config import get_font_latex_config, get_layout_colors, get_layout
    
    # Get font configuration from layout with absolute path
    font_config = get_font_latex_config(layout_name, fonts_dir=fonts_dir)
    
    # Get colors from layout
    colors = get_layout_colors(layout_name)
    primary_rgb = _hex_to_rgb(colors['primary'])
    secondary_rgb = _hex_to_rgb(colors['secondary'])
    background_rgb = _hex_to_rgb(colors['background'])
    
    # Get text color from layout typography normal style
    layout = get_layout(layout_name)
    text_color_rgb = None
    
    # For layouts with dark backgrounds, use white text by default
    # This matches the HTML behavior
    if layout_name in ['creative', 'corporate', 'handwritten']:
        text_color_rgb = "255,255,255"  # White text for dark backgrounds
    else:
        # Try to get color from layout configuration
        try:
            # Navigate to colors.layout_config.typography.normal
            colors_config = layout.get('colors', {}).get('layout_config', {})
            typography = colors_config.get('typography', {})
            normal_config = typography.get('normal', {})
            
            if 'palette' in normal_config and 'tone' in normal_config:
                # Get the palette and tone
                palette_name = normal_config['palette']
                tone_name = normal_config['tone']
                
                # Load complete config to access palettes
                from ePy_docs.core._config import get_loader
                loader = get_loader()
                complete_config = loader.load_complete_config(layout_name)
                palettes = complete_config.get('colors', {}).get('palettes', {})
                
                if palette_name in palettes:
                    palette = palettes[palette_name]
                    if tone_name in palette:
                        tone_rgb = palette[tone_name]
                        if isinstance(tone_rgb, list) and len(tone_rgb) == 3:
                            text_color_rgb = f"{int(tone_rgb[0])},{int(tone_rgb[1])},{int(tone_rgb[2])}"
        except (KeyError, AttributeError, TypeError):
            pass  # Use default if color resolution fails
    
    # Build text color command
    text_color_cmd = ""
    if text_color_rgb:
        text_color_cmd = f"\\color[RGB]{{{text_color_rgb}}}"
    
    # Generate LaTeX header (no hardcoded fonts - layouts define them)
    header = rf'''
\usepackage[utf8]{{inputenc}}
\usepackage{{fontenc}}
{font_config}

\usepackage{{xcolor}}
\definecolor{{pagebackground}}{{RGB}}{{{background_rgb}}}
\definecolor{{brandPrimary}}{{RGB}}{{{primary_rgb}}}
\definecolor{{brandSecondary}}{{RGB}}{{{secondary_rgb}}}

\pagecolor{{pagebackground}}
{text_color_cmd}

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

% Configure section colors - section numbers inherit section color
\usepackage{{sectsty}}
\sectionfont{{\color{{brandPrimary}}}}
\subsectionfont{{\color{{brandPrimary}}}}
\subsubsectionfont{{\color{{brandPrimary}}}}
'''
    
    return header.strip()


# =============================================================================
# PDF CONFIGURATION DICT
# =============================================================================

def get_pdf_config(
    layout_name: str = 'classic',
    document_type: str = 'article',
    fonts_dir: Path = None,
    config: Dict[str, Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate complete PDF configuration for Quarto.
    
    Args:
        layout_name: Name of the layout
        document_type: LaTeX document class ('article', 'report', 'book')
        fonts_dir: Absolute path to fonts directory (for font loading)
        config: Optional layout configuration (for testing)
        **kwargs: Additional PDF options
        
    Returns:
        Dictionary with PDF configuration for Quarto YAML
    """
    from ePy_docs.core._config import get_layout
    
    # Use provided config or load from layout
    if config is not None:
        layout = config
    else:
        layout = get_layout(layout_name)
    
    # Get column configuration from layout
    columns_config = None
    if document_type in layout:
        columns_config = layout[document_type].get('columns', {})
    
    # Map document types to Quarto document classes
    def map_document_type_to_quarto_class(doc_type: str) -> str:
        """Map ePy_docs document types to Quarto document classes."""
        mapping = {
            'paper': 'article',     # Academic paper -> article class
            'book': 'book',         # Book format -> book class (has chapters)
            'report': 'article',    # Technical report -> article class (sections, no chapters)
            'presentations': 'beamer'  # Presentations (LaTeX Beamer)
        }
        return mapping.get(doc_type, doc_type)
    
    quarto_documentclass = map_document_type_to_quarto_class(document_type)
    
    # Determine section numbering based on document type
    # Reports should not have numbered sections, books should
    default_number_sections = document_type != 'report'
    
    config = {
        'pdf-engine': get_pdf_engine(layout_name),
        'documentclass': quarto_documentclass,
        'linestretch': layout.get('tables', {}).get('layout_config', {}).get('styling', {}).get('line_spacing', 1.2),
        'fontsize': kwargs.get('fontsize', '12pt'),
        'papersize': kwargs.get('papersize', 'letter'),
        'number-sections': kwargs.get('number_sections', default_number_sections),
        'colorlinks': kwargs.get('colorlinks', True),
        'toc': kwargs.get('toc', True),
        'toc-depth': kwargs.get('toc_depth', 3),
        'lof': kwargs.get('lof', False),  # List of figures
        'lot': kwargs.get('lot', False),  # List of tables
        'fig-pos': 'H',  # Figure position
        'fig-cap-location': 'bottom',
        'tbl-cap-location': 'top',
        'include-in-header': {
            'text': get_pdf_header_config(layout_name, fonts_dir=fonts_dir)
        }
    }
    
    # Only add geometry for non-beamer documents
    # Beamer handles its own geometry and conflicts with manual geometry settings
    if quarto_documentclass != 'beamer':
        config['geometry'] = get_pdf_geometry(layout_name)
    
    # Add column configuration if specified
    if columns_config:
        default_columns = columns_config.get('default', 1)
        if default_columns == 2:
            # For two-column layout, we need to add special LaTeX commands
            header_text = config['include-in-header']['text']
            # Add twocolumn command to header
            if '\\usepackage{multicol}' not in header_text:
                header_text += '\n\\usepackage{multicol}'
            # Set document to start in two-column mode
            config['include-in-header']['text'] = header_text + '\n\\twocolumn'
        elif default_columns == 3:
            # For three-column layout, use multicols environment
            header_text = config['include-in-header']['text']
            if '\\usepackage{multicol}' not in header_text:
                header_text += '\n\\usepackage{multicol}'
            # We'll need to wrap content in \begin{multicols}{3}...\end{multicols}
            # This is more complex and may need document-level changes
            config['include-in-header']['text'] = header_text
    
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
