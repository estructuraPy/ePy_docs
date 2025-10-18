"""Page configuration utilities for report generation."""

from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from reportlab.lib import colors
# Import from internal data module
from ePy_docs.internals.data_processing._data import load_cached_files, _safe_get_nested
from ePy_docs.config.setup import _resolve_config_path
from ._colors import get_colors_config

# Global layout configuration - moved from layouts.py
_CURRENT_LAYOUT = None

def _get_color_hex(palette_name: str, tone_name: str) -> str:
    """Helper para extraer color en formato hex usando get_colors_config exclusivamente"""
    colors_config = get_colors_config()
    
    try:
        # Acceso directo a paletas usando get_colors_config
        if palette_name in colors_config.get('palettes', {}):
            palette = colors_config['palettes'][palette_name]
            if tone_name in palette:
                rgb_color = palette[tone_name]
                # Convert RGB list to hex
                if isinstance(rgb_color, list) and len(rgb_color) == 3:
                    return f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
        
        return "#CCCCCC"  # Fallback color
    except (KeyError, TypeError):
        return "#CCCCCC"  # Fallback color

def _load_pages_config() -> Dict[str, Any]:
    """🏪 SUCURSAL DE LA SECRETARÍA DE COMERCIO - Reino PAGES
    
    Sucursal interna del reino PAGES que proporciona acceso
    validado y seguro a la configuración usando el Guardián Supremo.
    
    Returns:
        Configuración validada del Reino PAGES
        
    Raises:
        KeyError: Si falta configuración requerida
        RuntimeError: Si falla la carga de configuración
    """
    # Import from internal data module
    from ePy_docs.internals.data_processing._data import load_cached_files
    from ePy_docs.config.setup import _resolve_config_path
    
    try:
        config_path = _resolve_config_path('components/pages')
        config = load_cached_files(config_path)
        
        # Validación específica del reino PAGES usando estructura real
        required_keys = ['layouts', 'format', 'crossref']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
                
        return config
    except Exception as e:
        raise RuntimeError(f"Failed to load pages configuration: {e}")

def get_pages_config() -> Dict[str, Any]:
    """🤝 TRATADO COMERCIAL OFICIAL - Reino PAGES
    
    Esta es la ÚNICA función autorizada para que otros reinos
    obtengan recursos del Reino PAGES. Respeta la soberanía del
    gobernante y protege al pueblo (pages.json).
        
    Returns:
        Configuración completa del Reino PAGES
    """
    return _load_pages_config()


def _load_component_config(config_name: str) -> Dict[str, Any]:
    """Helper function to load component configuration using the correct pattern.
    
    DEPRECATED: Use get_pages_config() for pages, or appropriate treaty functions for other components.
    """
    config_path = _resolve_config_path(f'components/{config_name}')
    return load_cached_files(config_path)

def set_current_layout(layout_name: str) -> None:
    """Set the current layout globally."""
    global _CURRENT_LAYOUT
    _CURRENT_LAYOUT = layout_name

def get_current_layout() -> str:
    """Get the current layout. Required - no fallbacks."""
    global _CURRENT_LAYOUT
    if _CURRENT_LAYOUT is None:
        raise RuntimeError("No layout set. Call quick_setup() first with layout_name parameter.")
    return _CURRENT_LAYOUT

class ConfigurationError(Exception):
    """Configuration not found or invalid."""
    pass


def is_dark_color(hex_color: str) -> bool:
    """Determine if a hex color is dark based on luminance."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0  
    b = int(hex_color[4:6], 16) / 255.0
    
    def to_linear(c):
        return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)
    
    luminance = 0.2126 * to_linear(r) + 0.7152 * to_linear(g) + 0.0722 * to_linear(b)
    return luminance < 0.5


def get_page_config() -> Dict[str, Any]:
    """Get page configuration from pages.json."""
    return _load_pages_config()


def convert_to_reportlab_color(color_input) -> colors.Color:
    """Convert color input to ReportLab color format."""
    if isinstance(color_input, list) and len(color_input) >= 3:
        r, g, b = color_input[:3]
        return colors.Color(r/255.0, g/255.0, b/255.0)
    elif isinstance(color_input, str):
        if color_input.startswith('#'):
            hex_color = color_input.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c+c for c in hex_color)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return colors.Color(r/255.0, g/255.0, b/255.0)
        else:
            return getattr(colors, color_input)
    else:
        raise ConfigurationError(f"Invalid color format: {color_input}")


def get_layout_name(layout_name: str = None) -> str:
    """Get layout name for a specific layout or default layout."""
    if layout_name is None:
        layout_name = get_current_layout()
    
    report_config = _load_component_config('report')
    
    if layout_name not in report_config['layouts']:
        available_layouts = ', '.join(report_config['layouts'].keys())
        raise ValueError(f"Layout '{layout_name}' not found. Available: {available_layouts}")
    
    return layout_name


def get_project_config() -> Dict[str, Any]:
    """Get project configuration."""
    return _load_component_config('project_info')


def get_references_config() -> Dict[str, Any]:
    """Get references configuration from references.json."""
    return _load_component_config('references')


def _get_available_configs() -> Dict[str, str]:
    """Automatically detect available configuration files."""
    from ePy_docs.config.setup import get_absolute_output_directories
    from pathlib import Path
    
    config_map = {}
    
    try:
        output_dirs = get_absolute_output_directories(document_type="report")
        
        # Check components directory
        components_dir = Path(output_dirs['configuration']) / 'components'
        if components_dir.exists():
            for json_file in components_dir.glob('*.json'):
                config_name = json_file.stem
                config_map[config_name] = config_name
                config_map[f'components_{config_name}'] = config_name
                config_map[f'components/{config_name}.json'] = config_name
        
        # Check units directory  
        units_dir = Path(output_dirs['configuration']) / 'units'
        if units_dir.exists():
            for json_file in units_dir.glob('*.json'):
                config_name = json_file.stem
                config_map[f'units_{config_name}'] = config_name
        
        # Check components directory
        components_dir = Path(output_dirs['configuration']) / 'components'  
        if components_dir.exists():
            for json_file in components_dir.glob('*.json'):
                config_name = json_file.stem
                config_map[f'components_{config_name}'] = config_name
                
        # Also check src components as fallback
        src_components_dir = Path(__file__).parent
        if src_components_dir.exists():
            for json_file in src_components_dir.glob('*.json'):
                config_name = json_file.stem
                if config_name not in config_map:
                    config_map[config_name] = config_name
                    config_map[f'components_{config_name}'] = config_name
                    config_map[f'components/{config_name}.json'] = config_name
        
    except Exception:
        # Fallback to essential configs if auto-detection fails
        essential_configs = ['colors', 'page', 'text', 'tables', 'images', 'report', 'references', 'project_info', 'setup']
        for config in essential_configs:
            config_map[config] = config
            config_map[f'components_{config}'] = config
            config_map[f'components/{config}.json'] = config
    
    return config_map


def get_config_value(config_name: str, path: str) -> Any:
    """Get value from any configuration using dot notation."""
    # Handle full path formats like 'components/images.json'
    if '/' in config_name:
        parts = config_name.split('/')
        if len(parts) == 2 and parts[0] == 'components':
            # Extract just the filename without .json extension
            config_name = parts[1].replace('.json', '')
    else:
        # Handle direct .json filenames like 'pages.json'
        config_name = config_name.replace('.json', '')
    
    # Get available configurations automatically
    config_type_map = _get_available_configs()
    config_type = config_type_map.get(config_name, config_name)
    config = _load_component_config(config_type)
    
    keys = path.split('.')
    result = config
    for key in keys:
        if key in result:
            result = result[key]
        else:
            return None  # Return None if key path doesn't exist
    return result


def get_full_project_config() -> Dict[str, Any]:
    """Get complete project configuration including styling components."""
    project_data = _load_component_config('project_info')
    
    tables_config = _load_component_config('tables')
    colors_config = _load_component_config('colors')
    styles_config = _load_pages_config()
    images_config = _load_component_config('images')
    
    styling_config = {
        'tables': tables_config,
        'colors': colors_config,
        'styles': styles_config,
        'figures': images_config,
        'citations': {'default_style': 'apa'}
    }
    
    full_config = project_data.copy()
    full_config['styling'] = styling_config
    
    return full_config


def get_header_style(layout_name: str = None) -> str:
    """Get header style for a layout."""
    page_config = _load_pages_config()
    
    if layout_name is None:
        layout_name = get_current_layout()
    
    return page_config['layouts'][layout_name]['header_style']


def get_text_style(layout_name: str = None) -> str:
    """Get text style for a layout."""
    return get_layout_name(layout_name)


def validate_csl_style(style_name: str) -> str:
    """Validate and get the CSL file name for a given style."""
    if not style_name:
        raise ValueError("Citation style name is required")
    
    available_styles = get_available_csl_styles()
    
    if not available_styles:
        raise ValueError("No CSL files found in references directory")
    
    style_name = style_name.lower().strip()
    
    if style_name in available_styles:
        return available_styles[style_name]
    
    if style_name.endswith('.csl'):
        base_name = style_name[:-4]
        if base_name in available_styles:
            return style_name
    
    available_list = ', '.join(available_styles.keys())
    raise ValueError(f"Citation style '{style_name}' not found. Available: {available_list}")


def get_available_csl_styles() -> Dict[str, Any]:
    """Get available CSL citation styles."""
    from ePy_docs.config.setup import get_absolute_output_directories
    
    available_styles = {}
    
    # Use source directory - Los archivos CSL están en resources/styles/
    references_dir = Path(__file__).parent.parent.parent / "resources" / "styles"
    
    if references_dir.exists():
        for csl_file in references_dir.glob("*.csl"):
            style_name = csl_file.stem.lower()
            available_styles[style_name] = csl_file.name
    
    return available_styles


def sync_ref(citation_style: Optional[str] = None) -> None:
    """Synchronize reference files from source to output directory."""
    from ePy_docs.config.setup import get_absolute_output_directories
    from shutil import copy2
    
    output_dirs = get_absolute_output_directories(document_type="report")
    
    # Copy to output directory where Quarto can find them
    target_dir = Path(output_dirs['output'])
    
    src_ref_dir = Path(__file__).parent
    # Los archivos CSL están en resources/styles/
    src_styles_dir = Path(__file__).parent.parent.parent / "resources" / "styles"
    # El archivo references.bib también está en resources/styles/
    src_components_dir = src_styles_dir  # Cambiar para usar la misma ubicación que los CSL
    target_dir.mkdir(parents=True, exist_ok=True)

    bib_file = "references.bib"
    src_bib = src_components_dir / bib_file  # Buscar en resources/styles/
    target_bib = target_dir / bib_file

    if src_bib.exists():
        if not target_bib.exists() or src_bib.stat().st_mtime > target_bib.stat().st_mtime:
            copy2(str(src_bib), str(target_bib))

    if citation_style:
        csl_file = f"{citation_style}.csl"
        src_csl = src_styles_dir / csl_file  # Buscar en styles/ en lugar de styling/
        target_csl = target_dir / csl_file
        
        if src_csl.exists():
            if not target_csl.exists() or src_csl.stat().st_mtime > target_csl.stat().st_mtime:
                copy2(str(src_csl), str(target_csl))
    else:
        for src_file in src_styles_dir.glob("*.csl"):  # Buscar en styles/ en lugar de styling/
            target_file = target_dir / src_file.name
            
            if not target_file.exists() or src_file.stat().st_mtime > target_file.stat().st_mtime:
                copy2(str(src_file), str(target_file))


# Legacy compatibility - minimal ConfigManager for existing imports
class _ConfigManager:
    """Minimal legacy ConfigManager for compatibility."""
    
    def __init__(self):
        pass
    
    def get_colors_config(self):
        from ._colors import get_colors_config
        return get_colors_config()
    
    def get_nested_value(self, config_name: str, path: str, default: Any = None):
        return get_config_value(config_name, path)


def get_layout_config(layout_name: str = None) -> Dict[str, Any]:
    """Get layout configuration from report.json."""
    report_config = _load_component_config('report')
    
    if layout_name is None:
        layout_name = get_current_layout()
    
    return report_config['layouts'][layout_name]


def get_page_layout_config(layout_name: str = None) -> Dict[str, Any]:
    """Get page layout configuration by resolving page_layout_key."""
    layout_config = get_layout_config(layout_name)
    page_layout_key = layout_config.get('page_layout_key')
    
    if not page_layout_key:
        # If no page_layout_key, return the layout config itself
        return layout_config
    
    page_config = _load_pages_config()
    
    # Check if page_layouts exists in pages.json
    if 'page_layouts' not in page_config:
        # If page_layouts section doesn't exist, return layout config
        return layout_config
    
    page_layouts = page_config['page_layouts']
    if page_layout_key not in page_layouts:
        available_layouts = ', '.join(page_layouts.keys())
        raise ValueError(f"Page layout '{page_layout_key}' not found in page.json. Available: {available_layouts}")
    
    return page_layouts[page_layout_key]


def get_background_config(layout_name: str = None) -> Dict[str, Any]:
    """Get background configuration by resolving background_key."""
    layout_config = get_layout_config(layout_name)
    background_key = layout_config.get('background_key')
    
    if not background_key:
        # If no background_key, get default from colors kingdom

        return {
            'color': _get_color_hex('neutrals', 'white'),
            'type': 'solid'
        }
    
    page_config = _load_pages_config()
    
    # Check if backgrounds exists in pages.json
    if 'backgrounds' not in page_config:
        # If backgrounds section doesn't exist, get default from colors kingdom

        return {
            'color': _get_color_hex('neutrals', 'white'),
            'type': 'solid'
        }
    
    backgrounds = page_config['backgrounds']
    if background_key not in backgrounds:
        available_backgrounds = ', '.join(backgrounds.keys())
        raise ValueError(f"Background '{background_key}' not found in pages.json. Available: {available_backgrounds}")
    
    background_config = backgrounds[background_key].copy()
    
    if 'color_key' in background_config:
        color_key = background_config['color_key']
        colors_config = _load_component_config('colors')
        
        parts = color_key.split('.')
        if len(parts) >= 2:
            category, color_name = parts[0], parts[1]
            if category in colors_config and color_name in colors_config[category]:
                background_config['color'] = colors_config[category][color_name]
                del background_config['color_key']
    
    return background_config


def update_default_layout(new_layout: str) -> str:
    """Update the global current layout."""
    report_config = _load_component_config('report')
    
    if new_layout not in report_config['layouts']:
        available_layouts = list(report_config['layouts'].keys())
        raise ValueError(f"Layout '{new_layout}' not found. Available: {available_layouts}")
    
    old_layout = get_current_layout()
    set_current_layout(new_layout)
    return old_layout


class DocumentStyler:
    """Document styling operations for PDF generation."""
    
    def __init__(self, layout_name: str = None):
        self.layout_name = layout_name or get_current_layout()
        self.report_config = _load_component_config('report')
        self.layout_config = self.report_config['layouts'][self.layout_name]
    
    def get_font_config(self) -> Dict[str, Any]:
        """Get font configuration from text.json."""
        text_config = _load_component_config('text')
        
        # Try to get layout-specific text configuration
        if 'layout_styles' in text_config and self.layout_name in text_config['layout_styles']:
            layout_text = text_config['layout_styles'][self.layout_name]
            if 'text' in layout_text:
                text_section = layout_text['text']
                config = {}
                if 'fontSize' in text_section:
                    config['fontsize'] = f"{text_section['fontSize']}pt"
                if 'lineSpacing' in text_section:
                    config['linestretch'] = text_section['lineSpacing']
                return config
        
        # Fallback: use first available configuration with fontSize and lineSpacing
        def find_font_config(obj):
            if isinstance(obj, dict):
                if 'fontSize' in obj and 'lineSpacing' in obj:
                    return {
                        'fontsize': f"{obj['fontSize']}pt",
                        'linestretch': obj['lineSpacing']
                    }
                for value in obj.values():
                    result = find_font_config(value)
                    if result:
                        return result
            return None
        
        result = find_font_config(text_config)
        if result:
            return result
            
        raise ConfigurationError(f"No font configuration found in text.json for layout '{self.layout_name}'")
    
    def get_margin_config(self) -> Dict[str, str]:
        """Get margin configuration based on layout."""
        margins = self.layout_config['margins']
        return {
            'margin-top': f"{margins['top']}in",
            'margin-bottom': f"{margins['bottom']}in", 
            'margin-left': f"{margins['left']}in",
            'margin-right': f"{margins['right']}in"
        }
    
    def get_header_config(self) -> Dict[str, Any]:
        """Get header styling configuration."""
        page_config = _load_pages_config()
        
        config = {}
        if 'format' in page_config and 'common' in page_config['format']:
            common_format = page_config['format']['common']
            if 'toc' in common_format:
                config['toc'] = common_format['toc']
            if 'number-sections' in common_format:
                config['number-sections'] = common_format['number-sections']
        
        # Add available header configuration from layout
        if 'header_position' in self.layout_config:
            config['position'] = self.layout_config['header_position']
        if 'header_content' in self.layout_config:
            config['content'] = self.layout_config['header_content']
            
        return config
    
    def build_complete_config(self) -> Dict[str, Any]:
        """Build complete styling configuration."""
        from ePy_docs.internals.generation._quarto import QuartoConfigManager
        from ePy_docs.internals.generation._references import get_bibliography_config
        
        config = {}
        config.update(self.get_margin_config()) 
        config.update(self.get_header_config())
        config['crossref'] = QuartoConfigManager.merge_crossref_config()
        config.update(get_bibliography_config())
        
        return config


def create_css_styles(layout_name: Optional[str] = None) -> str:
    """Create CSS styles for HTML output."""
    if layout_name is None:
        layout_name = get_current_layout()
    
    # Get layout-specific color configuration
    from ePy_docs.internals.styling._layout import get_layout_coordinator
    coordinator = get_layout_coordinator()
    layout_config = coordinator.coordinate_layout_style(layout_name)
    
    # Get color configuration for this layout
    color_layout_config = layout_config.colors
    typography_colors = color_layout_config.get('typography', {})
    
    # Helper function to resolve color from layout config using get_colors_config
    def get_layout_color(element_name: str, default_palette: str = 'neutrals', default_tone: str = 'black') -> str:
        """Get color from layout configuration using get_colors_config."""
        colors_config = get_colors_config()
        element_config = typography_colors.get(element_name, {})
        
        if isinstance(element_config, dict) and 'palette' in element_config and 'tone' in element_config:
            palette = element_config['palette']
            tone = element_config['tone']
        else:
            palette = default_palette
            tone = default_tone
        
        # Get color from colors_config
        if palette in colors_config.get('palettes', {}):
            palette_colors = colors_config['palettes'][palette]
            if tone in palette_colors:
                rgb_color = palette_colors[tone]
                # Convert RGB list to hex
                if isinstance(rgb_color, list) and len(rgb_color) == 3:
                    return f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
        
        return "#000000"  # Fallback to black
    
    # Get all colors from layout configuration
    h1_color = get_layout_color('h1', 'purples', 'medium')
    h2_color = get_layout_color('h2', 'pinks', 'medium')
    h3_color = get_layout_color('h3', 'neutrals', 'black')
    h4_color = get_layout_color('h4', 'oranges', 'dark')
    h5_color = get_layout_color('h5', 'golds', 'medium')
    h6_color = get_layout_color('h6', 'greens', 'medium')
    caption_color = get_layout_color('caption', 'grays_warm', 'medium_dark')
    normal_color = get_layout_color('normal', 'grays_warm', 'darker')
    table_header_color = get_layout_color('header_color', 'purples', 'medium')
    background_color = get_layout_color('background_color', 'neutrals', 'white')
    
    primary_color = _get_color_hex('brand', 'secondary')
    secondary_color = _get_color_hex('brand', 'secondary')
    light_gray = _get_color_hex('grays_cool', 'light')
    white = _get_color_hex('neutrals', 'white')
    
    # Get accent colors for creative styling  
    accent1_color = _get_color_hex('purples', 'medium')  # purple
    accent2_color = _get_color_hex('pinks', 'medium')  # pink/red
    
    # Get font family from text.json
    text_config = _load_component_config('text')
    layout_text = text_config['layout_styles'][layout_name]
    
    # Get primary font family from normal text or h1 as fallback
    typography_config = _safe_get_nested(layout_text, 'typography', {})
    normal_font_config = _safe_get_nested(typography_config, 'normal', {})
    h1_font_config = _safe_get_nested(typography_config, 'h1', {})
    
    font_family = _safe_get_nested(normal_font_config, 'family', 
                                  _safe_get_nested(h1_font_config, 'family', 'sans_modern'))
    
    # Get CSS font stack from font_families configuration
    font_families = text_config.get('font_families', {})
    if font_family in font_families:
        font_config = font_families[font_family]
        primary = font_config.get('primary', font_family)
        fallback = font_config.get('fallback', 'sans-serif')
        css_font_family = f'"{primary}", {fallback}'
    else:
        # Final fallback: construct basic CSS font stack
        css_font_family = f'"{font_family}", serif' if 'serif' in font_family.lower() else f'"{font_family}", sans-serif'
    
    # Helper function to get callout colors from layout configuration using get_colors_config
    def get_callout_color(callout_name: str, color_type: str, default_palette: str = 'neutrals', default_tone: str = 'light') -> str:
        """Get callout color from layout configuration using get_colors_config."""
        colors_config = get_colors_config()
        callouts_colors = color_layout_config.get('callouts', {})
        callout_config = callouts_colors.get(callout_name, {})
        color_config = callout_config.get(color_type, {})
        
        if isinstance(color_config, dict) and 'palette' in color_config and 'tone' in color_config:
            palette = color_config['palette']
            tone = color_config['tone']
        else:
            palette = default_palette
            tone = default_tone
        
        # Get color from colors_config
        if palette in colors_config.get('palettes', {}):
            palette_colors = colors_config['palettes'][palette]
            if tone in palette_colors:
                rgb_color = palette_colors[tone]
                # Convert RGB list to hex
                if isinstance(rgb_color, list) and len(rgb_color) == 3:
                    return f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
        
        return "#E3F2FD"  # Fallback to light blue
    
    # Get callout colors from layout configuration
    note_bg = get_callout_color('note', 'background', 'purples', 'light')
    note_border = get_callout_color('note', 'border', 'purples', 'medium')
    
    warning_bg = get_callout_color('warning', 'background', 'status_warning', 'light')
    warning_border = get_callout_color('warning', 'border', 'oranges', 'dark')
    
    tip_bg = get_callout_color('tip', 'background', 'golds', 'light')
    tip_border = get_callout_color('tip', 'border', 'golds', 'medium')
    
    caution_bg = get_callout_color('caution', 'background', 'greens', 'light')
    caution_border = get_callout_color('caution', 'border', 'greens', 'medium')
    
    important_bg = get_callout_color('important', 'background', 'pinks', 'light')
    important_border = get_callout_color('important', 'border', 'pinks', 'medium')
    
    # For error and success, use appropriate status colors as fallback
    error_bg = get_callout_color('error', 'background', 'status_negative', 'light')
    error_border = get_callout_color('error', 'border', 'status_negative', 'medium')
    
    success_bg = get_callout_color('success', 'background', 'status_positive', 'light')
    success_border = get_callout_color('success', 'border', 'status_positive', 'medium')
    
    # Check if we need to include @font-face for C2024_anm_font
    font_face_css = ""
    if 'C2024_anm_font' in css_font_family:
        import os
        font_path = os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/C2024_anm_font_regular.ttf")
        if os.path.exists(font_path):
            # Convert Windows path to file URL for CSS
            font_url = font_path.replace("\\", "/").replace("C:", "file:///C:")
            font_face_css = f"""@font-face {{
    font-family: 'C2024_anm_font';
    src: url('{font_url}') format('truetype');
    font-weight: normal;
    font-style: normal;
}}

"""
    
    return f"""{font_face_css}body {{
    background-color: {background_color} !important;
    font-family: {css_font_family} !important;
    color: {normal_color} !important;
}}

h1 {{ color: {h1_color} !important; font-family: {css_font_family} !important; }}
h2 {{ color: {h2_color} !important; font-family: {css_font_family} !important; }}
h3 {{ color: {h3_color} !important; font-family: {css_font_family} !important; }}
h4 {{ color: {h4_color} !important; font-family: {css_font_family} !important; }}
h5 {{ color: {h5_color} !important; font-family: {css_font_family} !important; }}
h6 {{ color: {h6_color} !important; font-family: {css_font_family} !important; }}

.figure-caption, .table-caption {{ 
    color: {caption_color} !important; 
    font-family: {css_font_family} !important; 
}}

.table th {{ 
    background-color: {table_header_color}; 
    color: {white}; 
    font-family: {css_font_family} !important; 
}}

.quarto-xref {{ color: {primary_color} !important; }}
.quarto-xref:hover {{ color: {secondary_color} !important; }}

.table-striped > tbody > tr:nth-of-type(odd) {{ background-color: {light_gray}; }}

.creative-layout {{
    background: linear-gradient(135deg, {background_color}, {accent1_color}22, {accent2_color}22);
    min-height: 100vh;
}}

.creative-layout h1 {{
    text-shadow: 3px 3px 6px {accent1_color}55;
    transform: rotate(-2deg);
    margin: 2rem 0;
}}

.creative-layout h2 {{
    text-shadow: 2px 2px 4px {accent2_color}55;
    transform: rotate(1deg);
    border-left: 4px solid {h2_color};
    padding-left: 1rem;
}}

/* CALLOUT STYLES - INTEGRADOS EN CSS GLOBAL */
/* Usa color normal del layout para asegurar consistencia */
.callout-note-custom {{
    background-color: {note_bg} !important;
    border-left: 4px solid {note_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-note-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}

.callout-warning-custom {{
    background-color: {warning_bg} !important;
    border-left: 4px solid {warning_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-warning-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}

.callout-tip-custom {{
    background-color: {tip_bg} !important;
    border-left: 4px solid {tip_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-tip-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}

.callout-caution-custom {{
    background-color: {caution_bg} !important;
    border-left: 4px solid {caution_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-caution-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}

.callout-important-custom {{
    background-color: {important_bg} !important;
    border-left: 4px solid {important_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-important-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}

.callout-error-custom {{
    background-color: {error_bg} !important;
    border-left: 4px solid {error_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-error-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}

.callout-success-custom {{
    background-color: {success_bg} !important;
    border-left: 4px solid {success_border} !important;
    color: {normal_color} !important;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    font-family: {css_font_family} !important;
}}

.callout-success-custom *:not(.callout-title):not(.callout-icon) {{
    color: {normal_color} !important;
    font-family: {css_font_family} !important;
}}"""


