"""
Layout Configuration Module

Manages document layouts including:
- Layout definitions (classic, modern, handwritten, academic, etc.)
- Layout-specific settings (margins, fonts, colors, spacing)
- Font configuration (including C2024_anm_font for handwritten layout)
"""

from typing import Dict, Any, List
from pathlib import Path
import os


# =============================================================================
# LAYOUT DEFINITIONS
# =============================================================================

AVAILABLE_LAYOUTS = {
    'classic': {
        'name': 'Classic',
        'description': 'Traditional professional report layout',
        'font_family': 'serif',
        'margins': {'top': 2.5, 'bottom': 2.5, 'left': 2.5, 'right': 2.5},
        'line_spacing': 1.5,
        'colors': {
            'primary': '#00217E',
            'secondary': '#C6123C',
            'background': '#FFFFFF'
        }
    },
    'modern': {
        'name': 'Modern',
        'description': 'Clean modern layout with sans-serif fonts',
        'font_family': 'sans-serif',
        'margins': {'top': 2.0, 'bottom': 2.0, 'left': 2.0, 'right': 2.0},
        'line_spacing': 1.3,
        'colors': {
            'primary': '#2563EB',
            'secondary': '#7C3AED',
            'background': '#FFFFFF'
        }
    },
    'handwritten': {
        'name': 'Handwritten',
        'description': 'Personal handwritten-style layout with C2024_anm_font',
        'font_family': 'handwritten_personal',
        'custom_font': 'C2024_anm_font_regular.otf',
        'margins': {'top': 2.5, 'bottom': 2.5, 'left': 2.5, 'right': 2.5},
        'line_spacing': 1.5,
        'colors': {
            'primary': '#00217E',
            'secondary': '#C6123C',
            'background': '#FFFEF7'  # Cream background for handwritten feel
        },
        'requires_lualatex': True  # Required for custom OpenType fonts
    },
    'academic': {
        'name': 'Academic',
        'description': 'Academic paper layout (IEEE/ACM style)',
        'font_family': 'serif',
        'margins': {'top': 2.54, 'bottom': 2.54, 'left': 2.54, 'right': 2.54},
        'line_spacing': 2.0,  # Double spacing for academic papers
        'colors': {
            'primary': '#000000',
            'secondary': '#333333',
            'background': '#FFFFFF'
        }
    },
    'minimal': {
        'name': 'Minimal',
        'description': 'Minimalist layout with maximum whitespace',
        'font_family': 'sans-serif',
        'margins': {'top': 3.0, 'bottom': 3.0, 'left': 3.0, 'right': 3.0},
        'line_spacing': 1.8,
        'colors': {
            'primary': '#1F2937',
            'secondary': '#6B7280',
            'background': '#FFFFFF'
        }
    }
}


# =============================================================================
# LAYOUT RETRIEVAL FUNCTIONS
# =============================================================================

def _load_layout_from_file(layout_name: str) -> Dict[str, Any]:
    """
    Load layout configuration from .epyson file.
    
    Args:
        layout_name: Name of the layout file (without .epyson extension)
        
    Returns:
        Dictionary with layout configuration
        
    Raises:
        FileNotFoundError: If layout file not found
    """
    from ePy_docs.core._config import get_config_section
    
    # Get package root
    package_root = Path(__file__).parent.parent
    layout_file = package_root / 'config' / 'layouts' / f'{layout_name}.epyson'
    
    if not layout_file.exists():
        raise FileNotFoundError(f"Layout file not found: {layout_file}")
    
    # Load the full layout configuration
    import json
    with open(layout_file, 'r', encoding='utf-8') as f:
        layout_config = json.load(f)
    
    # Extract basic layout info
    layout_info = {
        'name': layout_config.get('layout_name', layout_name).title(),
        'description': layout_config.get('description', ''),
        'font_family': layout_config.get('font_family', 'sans-serif'),
        'margins': layout_config.get('layout_config', {}).get('margins', {
            'top': 2.5, 'bottom': 2.5, 'left': 2.5, 'right': 2.5
        }),
        'line_spacing': 1.5,
        'colors': {},
        'requires_lualatex': layout_name == 'handwritten'
    }
    
    # Get colors from layout
    colors_section = layout_config.get('colors', {}).get('layout_config', {})
    if colors_section:
        layout_info['colors'] = {
            'primary': '#2563EB',
            'secondary': '#7C3AED', 
            'background': '#FFFFFF'
        }
    
    return layout_info


def get_layout(layout_name: str = 'classic') -> Dict[str, Any]:
    """
    Get layout configuration by name.
    
    Args:
        layout_name: Name of the layout ('classic', 'corporate', 'handwritten', etc.)
        
    Returns:
        Dictionary with layout configuration
        
    Raises:
        ValueError: If layout_name not found
    """
    # Try to load from file first
    try:
        return _load_layout_from_file(layout_name)
    except FileNotFoundError:
        pass
    
    # Fallback to hardcoded layouts if file not found
    if layout_name not in AVAILABLE_LAYOUTS:
        # List available layout files
        package_root = Path(__file__).parent.parent
        layouts_dir = package_root / 'config' / 'layouts'
        available_files = []
        if layouts_dir.exists():
            available_files = [f.stem for f in layouts_dir.glob('*.epyson')]
        
        available = ', '.join(available_files if available_files else AVAILABLE_LAYOUTS.keys())
        raise ValueError(
            f"Layout '{layout_name}' not found. "
            f"Available layouts: {available}"
        )
    
    return AVAILABLE_LAYOUTS[layout_name].copy()


def list_layouts() -> List[str]:
    """Return list of available layout names."""
    # Get layouts from files
    package_root = Path(__file__).parent.parent
    layouts_dir = package_root / 'config' / 'layouts'
    
    if layouts_dir.exists():
        return [f.stem for f in layouts_dir.glob('*.epyson')]
    
    # Fallback to hardcoded
    return list(AVAILABLE_LAYOUTS.keys())


def get_layout_margins(layout_name: str = 'classic') -> Dict[str, float]:
    """Get margins (in cm) for specified layout."""
    layout = get_layout(layout_name)
    return layout['margins']


def get_layout_font_family(layout_name: str = 'classic') -> str:
    """Get font family for specified layout."""
    layout = get_layout(layout_name)
    return layout['font_family']


def get_layout_colors(layout_name: str = 'classic') -> Dict[str, str]:
    """Get color scheme for specified layout."""
    layout = get_layout(layout_name)
    return layout['colors']


def requires_lualatex(layout_name: str = 'classic') -> bool:
    """Check if layout requires LuaLaTeX (for custom fonts)."""
    layout = get_layout(layout_name)
    return layout.get('requires_lualatex', False)


# =============================================================================
# FONT PATH RESOLUTION
# =============================================================================

def get_font_path(font_filename: str) -> Path:
    """
    Get absolute path to font file in package assets.
    
    Args:
        font_filename: Name of font file (e.g., 'C2024_anm_font_regular.otf')
        
    Returns:
        Absolute path to font file
        
    Raises:
        FileNotFoundError: If font file not found
    """
    # Get package root directory
    package_root = Path(__file__).parent.parent  # ePy_docs/
    font_path = package_root / 'config' / 'assets' / 'fonts' / font_filename
    
    if not font_path.exists():
        raise FileNotFoundError(
            f"Font file not found: {font_path}\n"
            f"Expected location: {package_root / 'config' / 'assets' / 'fonts' / font_filename}"
        )
    
    return font_path.resolve()


def get_custom_font_path(layout_name: str = 'classic') -> Path:
    """
    Get path to custom font for layout (if any).
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        Path to custom font file, or None if layout uses system fonts
    """
    layout = get_layout(layout_name)
    
    if 'custom_font' not in layout:
        return None
    
    font_filename = layout['custom_font']
    return get_font_path(font_filename)


# =============================================================================
# FONT CONFIGURATION FOR LATEX/HTML
# =============================================================================

def get_font_latex_config(layout_name: str = 'classic') -> str:
    """
    Generate LaTeX fontspec configuration for layout.
    
    For layouts with custom fonts, generates fontspec with fallback fonts.
    Uses centralized format.epyson configuration.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        LaTeX fontspec commands or empty string
    """
    layout = get_layout(layout_name)
    font_family = layout.get('font_family')
    
    if not font_family:
        return ""
    
    # Load font families configuration from format.epyson
    import json
    from pathlib import Path
    config_dir = Path(__file__).parent.parent / 'config'
    format_path = config_dir / 'format.epyson'
    
    with open(format_path, 'r', encoding='utf-8') as f:
        format_config = json.load(f)
    
    font_config = format_config['font_families'].get(font_family)
    if not font_config:
        return ""
    
    # Check if layout has custom font file
    custom_font = layout.get('custom_font')
    
    if custom_font:
        # Custom font (e.g., handwritten)
        try:
            font_path = get_custom_font_path(layout_name)
        except (FileNotFoundError, TypeError):
            return ""
        
        if font_path is None:
            return ""
        
        font_extension = font_path.suffix
        font_basename = font_path.stem
        font_dir = str(font_path.parent).replace('\\', '/')
        
        # Parse fallback string from format.epyson into list
        fallback_str = font_config.get('fallback', '')
        fallbacks = [f.strip() for f in fallback_str.split(',') if f.strip()]
        
        # Generate fontspec with explicit glyph substitution for missing characters
        # More reliable than FallbackFonts which doesn't always work
        fallback_definitions = ""
        for i, fallback_font in enumerate(fallbacks):
            fallback_definitions += f"\\newfontfamily\\fallbackfont{i}{{{fallback_font}}}[Scale=MatchLowercase]\n"
        
        # Define commands for common missing characters
        char_fallbacks = r'''
% Character fallback commands (use first available fallback font)
\newcommand{\fbchar}[1]{{\fallbackfont0#1}}
\DeclareRobustCommand{\:}{{\fallbackfont0:}}
\DeclareRobustCommand{\;}{{\fallbackfont0;}}
\catcode`\@=11
\DeclareRobustCommand{\@}{{\fallbackfont0@}}
\catcode`\@=12
'''
        
        return r'''
% Custom font configuration for XeLaTeX
\usepackage{fontspec}

''' + fallback_definitions + r'''
% Set main custom font
\setmainfont{''' + font_basename + r'''}[
    Path = ''' + font_dir + r'''/,
    Extension = ''' + font_extension + r''',
    UprightFont = *,
    BoldFont = *,
    ItalicFont = *,
    BoldItalicFont = *
]

''' + char_fallbacks + r'''
'''
    else:
        # System font - use simple approach since system fonts are more complete
        primary_font = font_config.get('primary', 'Latin Modern Roman')
        fallback_str = font_config.get('fallback', '')
        fallbacks = [f.strip() for f in fallback_str.split(',') if f.strip()]
        
        # Generate fallback font definitions
        fallback_definitions = ""
        for i, fallback_font in enumerate(fallbacks):
            fallback_definitions += f"\\newfontfamily\\fallbackfont{i}{{{fallback_font}}}\n"
        
        return r'''
% System font configuration for XeLaTeX
\usepackage{fontspec}

''' + fallback_definitions + r'''
% Set main system font
\setmainfont{''' + primary_font + r'''}

'''


def get_font_css_config(layout_name: str = 'classic') -> str:
    """
    Generate CSS @font-face configuration for layout.
    
    For handwritten layout, generates @font-face rule to load C2024_anm_font.
    For other layouts, returns empty string (uses system fonts).
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        CSS @font-face rule or empty string
    """
    layout = get_layout(layout_name)
    
    # Only handwritten layout uses custom font
    if layout.get('font_family') != 'handwritten_personal':
        return ""
    
    # Get font path
    try:
        font_path = get_custom_font_path(layout_name)
    except FileNotFoundError:
        return ""
    
    if font_path is None:
        return ""
    
    # For HTML, we need to embed font as base64 or provide URL
    # For now, assume font is copied to output directory
    font_filename = font_path.name
    
    return f'''
@font-face {{
    font-family: 'C2024_anm_font';
    src: url('{font_filename}') format('opentype');
    font-weight: normal;
    font-style: normal;
}}

body {{
    font-family: 'C2024_anm_font', cursive, 'Comic Sans MS', 'Bradley Hand', 'Brush Script MT', fantasy;
}}
'''


# =============================================================================
# LAYOUT VALIDATION
# =============================================================================

def validate_layout(layout_name: str) -> bool:
    """
    Validate that layout exists and has all required fields.
    
    Args:
        layout_name: Name of the layout to validate
        
    Returns:
        True if layout is valid
        
    Raises:
        ValueError: If layout is invalid
    """
    if layout_name not in AVAILABLE_LAYOUTS:
        available = ', '.join(AVAILABLE_LAYOUTS.keys())
        raise ValueError(
            f"Invalid layout '{layout_name}'. "
            f"Available: {available}"
        )
    
    layout = AVAILABLE_LAYOUTS[layout_name]
    
    # Check required fields
    required_fields = ['name', 'description', 'font_family', 'margins', 'line_spacing', 'colors']
    for field in required_fields:
        if field not in layout:
            raise ValueError(
                f"Layout '{layout_name}' missing required field: {field}"
            )
    
    # Validate margins
    margin_keys = ['top', 'bottom', 'left', 'right']
    for key in margin_keys:
        if key not in layout['margins']:
            raise ValueError(
                f"Layout '{layout_name}' margins missing: {key}"
            )
    
    # Validate colors
    color_keys = ['primary', 'secondary', 'background']
    for key in color_keys:
        if key not in layout['colors']:
            raise ValueError(
                f"Layout '{layout_name}' colors missing: {key}"
            )
    
    return True
