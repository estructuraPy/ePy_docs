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
    
    # Load palettes for color resolution
    palettes_file = package_root / 'config' / 'palettes.epyson'
    palettes = {}
    if palettes_file.exists():
        with open(palettes_file, 'r', encoding='utf-8') as f:
            palettes_data = json.load(f)
            palettes = palettes_data.get('palettes', {})
    
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
    
    # Helper function to convert RGB list to hex
    def rgb_to_hex(rgb_list):
        if isinstance(rgb_list, list) and len(rgb_list) == 3:
            return '#{:02X}{:02X}{:02X}'.format(int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2]))
        return '#FFFFFF'  # Default fallback
    
    # Get colors from layout - extract from default_palette
    colors_config = layout_config.get('colors', {}).get('layout_config', {})
    default_palette = colors_config.get('default_palette', 'academic')
    
    # Get colors from the palette
    if default_palette in palettes:
        palette = palettes[default_palette]
        layout_info['colors'] = {
            'primary': rgb_to_hex(palette.get('primary', [37, 99, 235])),      # Blue
            'secondary': rgb_to_hex(palette.get('secondary', [124, 58, 237])),  # Purple  
            'background': rgb_to_hex(palette.get('background', [255, 255, 255])) if 'background' in palette else '#FFFFFF'
        }
    else:
        # Default colors if palette not found
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
    # Load from .epyson file
    try:
        return _load_layout_from_file(layout_name)
    except FileNotFoundError:
        # List available layout files
        package_root = Path(__file__).parent.parent
        layouts_dir = package_root / 'config' / 'layouts'
        available_files = []
        if layouts_dir.exists():
            available_files = [f.stem for f in layouts_dir.glob('*.epyson')]
        
        available = ', '.join(available_files) if available_files else 'none'
        raise ValueError(
            f"Layout '{layout_name}' not found. "
            f"Available layouts: {available}"
        )


def list_layouts() -> List[str]:
    """Return list of available layout names."""
    # Get layouts from files
    package_root = Path(__file__).parent.parent
    layouts_dir = package_root / 'config' / 'layouts'
    
    if layouts_dir.exists():
        return [f.stem for f in layouts_dir.glob('*.epyson')]
    
    # Return empty list if no layouts directory
    return []


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
    Uses centralized assets.epyson configuration.
    
    Args:
        layout_name: Name of the layout
        
    Returns:
        LaTeX fontspec commands or empty string
    """
    layout = get_layout(layout_name)
    font_family = layout.get('font_family')
    
    if not font_family:
        return ""
    
    # Load font families configuration from assets.epyson
    import json
    from pathlib import Path
    config_dir = Path(__file__).parent.parent / 'config'
    assets_path = config_dir / 'assets.epyson'
    
    with open(assets_path, 'r', encoding='utf-8') as f:
        assets_config = json.load(f)
    
    font_config = assets_config['font_families'].get(font_family)
    if not font_config:
        return ""
    
    # Check if layout has custom font file or uses handwritten_personal font family
    custom_font = layout.get('custom_font')
    is_handwritten = font_family == 'handwritten_personal'
    
    if custom_font or is_handwritten:
        # Custom font (e.g., handwritten)
        if custom_font:
            try:
                font_path = get_custom_font_path(layout_name)
            except (FileNotFoundError, TypeError):
                return ""
        else:
            # For handwritten_personal without custom_font field, use the default font file
            try:
                font_path = get_font_path('C2024_anm_font_regular.otf')
            except FileNotFoundError:
                return ""
        
        if font_path is None:
            return ""
        
        font_extension = font_path.suffix
        font_basename = font_path.stem
        font_dir = str(font_path.parent).replace('\\', '/')
        
        # Parse fallback string from assets.epyson into list
        fallback_str = font_config.get('fallback', '')
        fallbacks = [f.strip() for f in fallback_str.split(',') if f.strip()]
        
        return r'''
% Custom font configuration for XeLaTeX
\usepackage{fontspec}

% Set main custom font with comprehensive fallback system
\setmainfont{''' + font_basename + r'''}[
    Path = ''' + font_dir + r'''/,
    Extension = ''' + font_extension + r''',
    UprightFont = *,
    BoldFont = *,
    ItalicFont = *,
    BoldItalicFont = *,
    FallbackFonts = {''' + ', '.join(f'"{f.strip()}"' for f in fallbacks if f.strip()) + r'''}
]

'''
    else:
        # System font - use simple approach with fallbacks for any missing characters
        primary_font = font_config.get('primary', 'Latin Modern Roman')
        fallback_str = font_config.get('fallback', '')
        fallbacks = [f.strip() for f in fallback_str.split(',') if f.strip()]
        
        return r'''
% System font configuration for XeLaTeX
\usepackage{fontspec}

% Set main system font with comprehensive fallback system
\setmainfont{''' + primary_font + r'''}[
    FallbackFonts = {''' + ', '.join(f'"{f.strip()}"' for f in fallbacks if f.strip()) + r'''}
]

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
    
    # Load font families configuration from assets.epyson to get fallbacks
    import json
    from pathlib import Path
    config_dir = Path(__file__).parent.parent / 'config'
    assets_path = config_dir / 'assets.epyson'
    
    with open(assets_path, 'r', encoding='utf-8') as f:
        assets_config = json.load(f)
    
    font_config = assets_config['font_families'].get('handwritten_personal', {})
    fallback_str = font_config.get('fallback', 'cursive, sans-serif')
    
    # Get font path
    try:
        font_path = get_custom_font_path(layout_name)
        if font_path is None:
            font_path = get_font_path('C2024_anm_font_regular.otf')
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
    font-family: 'C2024_anm_font', {fallback_str};
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
    # Check if layout file exists
    package_root = Path(__file__).parent.parent
    layout_file = package_root / 'config' / 'layouts' / f'{layout_name}.epyson'
    
    if not layout_file.exists():
        available = ', '.join(list_layouts())
        raise ValueError(
            f"Invalid layout '{layout_name}'. "
            f"Available: {available}"
        )
    
    # Load and validate layout
    try:
        layout = get_layout(layout_name)
    except Exception as e:
        raise ValueError(f"Layout '{layout_name}' is invalid: {str(e)}")
    
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
