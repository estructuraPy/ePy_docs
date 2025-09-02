"""Page configuration utilities for report generation."""

from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from reportlab.lib import colors
from ePy_docs.core.setup import _load_cached_files, _resolve_config_path, get_color

def _load_component_config(config_name: str, sync_files: bool = False) -> Dict[str, Any]:
    """Helper function to load component configuration using the correct pattern."""
    config_path = _resolve_config_path(f'components/{config_name}', sync_files)
    return _load_cached_files(config_path, sync_files)

# Global layout configuration - moved from layouts.py
_CURRENT_LAYOUT = None

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


def get_colors_config(sync_files: bool = True) -> Dict[str, Any]:
    """Get colors configuration from colors.json."""
    return _load_component_config('colors', sync_files=sync_files)


def get_page_config(sync_files: bool = True) -> Dict[str, Any]:
    """Get page configuration from page.json."""
    return _load_component_config('page', sync_files=sync_files)


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


def get_layout_name(layout_name: str = None, sync_files: bool = True) -> str:
    """Get layout name for a specific layout or default layout."""
    if layout_name is None:
        layout_name = get_current_layout()
    
    report_config = _load_component_config('report', sync_files=sync_files)
    
    if layout_name not in report_config['layouts']:
        available_layouts = ', '.join(report_config['layouts'].keys())
        raise ValueError(f"Layout '{layout_name}' not found. Available: {available_layouts}")
    
    return layout_name


def get_project_config(sync_files: bool = True) -> Dict[str, Any]:
    """Get project configuration."""
    return _load_component_config('project_info', sync_files=sync_files)


def get_references_config(sync_files: bool = True) -> Dict[str, Any]:
    """Get references configuration from references.json."""
    return _load_component_config('references', sync_files=sync_files)


def _get_available_configs(sync_files: bool = True) -> Dict[str, str]:
    """Automatically detect available configuration files."""
    from ePy_docs.core.setup import get_output_directories
    from pathlib import Path
    
    config_map = {}
    
    try:
        output_dirs = get_output_directories()
        
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
        
        # Check core directory
        core_dir = Path(output_dirs['configuration']) / 'core'  
        if core_dir.exists():
            for json_file in core_dir.glob('*.json'):
                config_name = json_file.stem
                config_map[f'core_{config_name}'] = config_name
                
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


def get_config_value(config_name: str, path: str, sync_files: bool = True) -> Any:
    """Get value from any configuration using dot notation."""
    # Handle full path formats like 'components/images.json'
    if '/' in config_name:
        parts = config_name.split('/')
        if len(parts) == 2 and parts[0] == 'components':
            # Extract just the filename without .json extension
            config_name = parts[1].replace('.json', '')
    
    # Get available configurations automatically
    config_type_map = _get_available_configs(sync_files)
    config_type = config_type_map.get(config_name, config_name)
    config = _load_component_config(config_type, sync_files=sync_files)
    
    keys = path.split('.')
    result = config
    for key in keys:
        if key in result:
            result = result[key]
        else:
            return None  # Return None if key path doesn't exist
    return result


def get_full_project_config(sync_files: bool = True) -> Dict[str, Any]:
    """Get complete project configuration including styling components."""
    project_data = _load_component_config('project_info', sync_files=sync_files)
    
    tables_config = _load_component_config('tables', sync_files=sync_files)
    colors_config = _load_component_config('colors', sync_files=sync_files)
    styles_config = _load_component_config('page', sync_files=sync_files)
    images_config = _load_component_config('images', sync_files=sync_files)
    
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


def get_header_style(layout_name: str = None, sync_files: bool = True) -> str:
    """Get header style for a layout."""
    page_config = _load_component_config('page', sync_files=sync_files)
    
    if layout_name is None:
        layout_name = get_current_layout()
    
    return page_config['layouts'][layout_name]['header_style']


def get_text_style(layout_name: str = None, sync_files: bool = True) -> str:
    """Get text style for a layout."""
    return get_layout_name(layout_name, sync_files)


def validate_csl_style(style_name: str, sync_files: bool = True) -> str:
    """Validate and get the CSL file name for a given style."""
    if not style_name:
        raise ValueError("Citation style name is required")
    
    available_styles = get_available_csl_styles(sync_files=sync_files)
    
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


def get_available_csl_styles(sync_files: bool = True) -> Dict[str, str]:
    """Get available CSL citation styles respecting sync_files parameter."""
    from ePy_docs.core.setup import get_output_directories
    
    available_styles = {}
    
    if sync_files:
        # Use configuration directory when sync_files=True
        try:
            output_dirs = get_output_directories()
            references_dir = Path(output_dirs['configuration']) / 'components'
        except Exception:
            references_dir = Path(__file__).parent
    else:
        # Use source directory when sync_files=False
        references_dir = Path(__file__).parent
    
    if references_dir.exists():
        for csl_file in references_dir.glob("*.csl"):
            style_name = csl_file.stem.lower()
            available_styles[style_name] = csl_file.name
    
    return available_styles


def sync_ref(citation_style: Optional[str] = None, sync_files: bool = True) -> None:
    """Synchronize reference files from source to configuration directory."""
    from ePy_docs.core.setup import get_output_directories
    from shutil import copy2
    
    output_dirs = get_output_directories()
    config_dir = output_dirs['configuration']
    
    src_ref_dir = Path(__file__).parent
    config_ref_dir = Path(config_dir) / "components"
    
    config_ref_dir.mkdir(parents=True, exist_ok=True)
    
    bib_file = "references.bib"
    src_bib = src_ref_dir / bib_file
    config_bib = config_ref_dir / bib_file
    
    if src_bib.exists():
        if not config_bib.exists() or src_bib.stat().st_mtime > config_bib.stat().st_mtime:
            copy2(str(src_bib), str(config_bib))
    
    if citation_style:
        csl_file = f"{citation_style}.csl"
        src_csl = src_ref_dir / csl_file
        config_csl = config_ref_dir / csl_file
        
        if src_csl.exists():
            if not config_csl.exists() or src_csl.stat().st_mtime > config_csl.stat().st_mtime:
                copy2(str(src_csl), str(config_csl))
    else:
        for src_file in src_ref_dir.glob("*.csl"):
            config_file = config_ref_dir / src_file.name
            
            if not config_file.exists() or src_file.stat().st_mtime > config_file.stat().st_mtime:
                copy2(str(src_file), str(config_file))


# Legacy compatibility - minimal ConfigManager for existing imports
class _ConfigManager:
    """Minimal legacy ConfigManager for compatibility."""
    
    def __init__(self):
        pass
    
    def get_colors_config(self, sync_files: bool = True):
        return get_colors_config(sync_files)
    
    def get_nested_value(self, config_name: str, path: str, default: Any = None, sync_files: bool = True):
        return get_config_value(config_name, path, sync_files)


def get_layout_config(layout_name: str = None, sync_files: bool = True) -> Dict[str, Any]:
    """Get layout configuration from report.json."""
    report_config = _load_component_config('report', sync_files=sync_files)
    
    if layout_name is None:
        layout_name = get_current_layout()
    
    return report_config['layouts'][layout_name]


def get_page_layout_config(layout_name: str = None, sync_files: bool = True) -> Dict[str, Any]:
    """Get page layout configuration by resolving page_layout_key."""
    layout_config = get_layout_config(layout_name, sync_files)
    page_layout_key = layout_config.get('page_layout_key')
    
    if not page_layout_key:
        # If no page_layout_key, return the layout config itself
        return layout_config
    
    page_config = _load_component_config('page', sync_files=sync_files)
    
    # Check if page_layouts exists in page.json
    if 'page_layouts' not in page_config:
        # If page_layouts section doesn't exist, return layout config
        return layout_config
    
    page_layouts = page_config['page_layouts']
    if page_layout_key not in page_layouts:
        available_layouts = ', '.join(page_layouts.keys())
        raise ValueError(f"Page layout '{page_layout_key}' not found in page.json. Available: {available_layouts}")
    
    return page_layouts[page_layout_key]


def get_background_config(layout_name: str = None, sync_files: bool = True) -> Dict[str, Any]:
    """Get background configuration by resolving background_key."""
    layout_config = get_layout_config(layout_name, sync_files)
    background_key = layout_config.get('background_key')
    
    if not background_key:
        # If no background_key, return a default background config
        return {'color': '#ffffff', 'type': 'solid'}
    
    page_config = _load_component_config('page', sync_files=sync_files)
    
    # Check if backgrounds exists in page.json
    if 'backgrounds' not in page_config:
        # If backgrounds section doesn't exist, return default config
        return {'color': '#ffffff', 'type': 'solid'}
    
    backgrounds = page_config['backgrounds']
    if background_key not in backgrounds:
        available_backgrounds = ', '.join(backgrounds.keys())
        raise ValueError(f"Background '{background_key}' not found in page.json. Available: {available_backgrounds}")
    
    background_config = backgrounds[background_key].copy()
    
    if 'color_key' in background_config:
        color_key = background_config['color_key']
        colors_config = _load_component_config('colors', sync_files=sync_files)
        
        parts = color_key.split('.')
        if len(parts) >= 2:
            category, color_name = parts[0], parts[1]
            if category in colors_config and color_name in colors_config[category]:
                background_config['color'] = colors_config[category][color_name]
                del background_config['color_key']
    
    return background_config


def update_default_layout(new_layout: str, sync_files: bool = True) -> str:
    """Update the global current layout."""
    report_config = _load_component_config('report', sync_files=sync_files)
    
    if new_layout not in report_config['layouts']:
        available_layouts = list(report_config['layouts'].keys())
        raise ValueError(f"Layout '{new_layout}' not found. Available: {available_layouts}")
    
    old_layout = get_current_layout()
    set_current_layout(new_layout)
    return old_layout


class DocumentStyler:
    """Document styling operations for PDF generation."""
    
    def __init__(self, layout_name: str = None, sync_files: bool = True):
        self.layout_name = layout_name or get_current_layout()
        self.sync_files = sync_files
        self.report_config = _load_component_config('report', sync_files=sync_files)
        self.layout_config = self.report_config['layouts'][self.layout_name]
    
    def get_font_config(self) -> Dict[str, Any]:
        """Get font configuration from text.json."""
        text_config = _load_component_config('text', sync_files=self.sync_files)
        
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
        page_config = _load_component_config('page', sync_files=self.sync_files)
        
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
        from ePy_docs.core.quarto import QuartoConfigManager
        from ePy_docs.components.references import get_bibliography_config
        
        config = {}
        config.update(self.get_margin_config()) 
        config.update(self.get_header_config())
        config['crossref'] = QuartoConfigManager.merge_crossref_config()
        config.update(get_bibliography_config(sync_files=self.sync_files))
        
        return config


def create_css_styles(layout_name: Optional[str] = None, sync_files: bool = True) -> str:
    """Create CSS styles for HTML output."""
    if layout_name is None:
        layout_name = get_current_layout()
    
    # Get all colors from JSON
    h1_color = get_color(f'reports.layout_styles.{layout_name}.h1', format_type="hex", sync_files=sync_files)
    h2_color = get_color(f'reports.layout_styles.{layout_name}.h2', format_type="hex", sync_files=sync_files)
    h3_color = get_color(f'reports.layout_styles.{layout_name}.h3', format_type="hex", sync_files=sync_files)
    h4_color = get_color(f'reports.layout_styles.{layout_name}.h4', format_type="hex", sync_files=sync_files)
    h5_color = get_color(f'reports.layout_styles.{layout_name}.h5', format_type="hex", sync_files=sync_files)
    h6_color = get_color(f'reports.layout_styles.{layout_name}.h6', format_type="hex", sync_files=sync_files)
    caption_color = get_color(f'reports.layout_styles.{layout_name}.caption', format_type="hex", sync_files=sync_files)
    normal_color = get_color(f'reports.layout_styles.{layout_name}.normal', format_type="hex", sync_files=sync_files)
    table_header_color = get_color(f'reports.layout_styles.{layout_name}.header_color', format_type="hex", sync_files=sync_files)
    
    primary_color = get_color('brand.brand_primary', format_type="hex", sync_files=sync_files)
    secondary_color = get_color('brand.brand_secondary', format_type="hex", sync_files=sync_files)
    light_gray = get_color('general.light_gray', format_type="hex", sync_files=sync_files)
    white = get_color('general.white', format_type="hex", sync_files=sync_files)
    
    background_color = get_color(f'reports.layout_styles.{layout_name}.background_color', format_type="hex", sync_files=sync_files)
    
    # Get accent colors for creative styling  
    accent1_color = get_color('brand.brand_senary', format_type="hex", sync_files=sync_files)  # purple
    accent2_color = get_color('brand.brand_secondary', format_type="hex", sync_files=sync_files)  # pink/red
    
    # Get font family from text.json
    text_config = _load_component_config('text', sync_files=sync_files)
    layout_text = text_config['layout_styles'][layout_name]
    font_family = layout_text['text']['font_family']
    
    # Get CSS font stack from text.json configuration if available
    if 'css_font_stack' in layout_text['text']:
        css_font_family = layout_text['text']['css_font_stack']
    elif 'font_stack' in layout_text['text']:
        css_font_family = layout_text['text']['font_stack']
    else:
        # Fallback: try to get from font_mapping in text.json
        if 'font_mapping' in text_config and font_family in text_config['font_mapping']:
            css_font_family = text_config['font_mapping'][font_family]
        else:
            # Final fallback: construct basic CSS font stack
            css_font_family = f'"{font_family}", serif' if 'serif' in font_family.lower() else f'"{font_family}", sans-serif'
    
    # Get callout colors from notes configuration - for global CSS integration
    note_bg = get_color('reports.notes.note.background', format_type="hex", sync_files=sync_files)
    note_border = get_color('reports.notes.note.border', format_type="hex", sync_files=sync_files)
    
    warning_bg = get_color('reports.notes.warning.background', format_type="hex", sync_files=sync_files)
    warning_border = get_color('reports.notes.warning.border', format_type="hex", sync_files=sync_files)
    
    tip_bg = get_color('reports.notes.tip.background', format_type="hex", sync_files=sync_files)
    tip_border = get_color('reports.notes.tip.border', format_type="hex", sync_files=sync_files)
    
    caution_bg = get_color('reports.notes.caution.background', format_type="hex", sync_files=sync_files)
    caution_border = get_color('reports.notes.caution.border', format_type="hex", sync_files=sync_files)
    
    important_bg = get_color('reports.notes.important.background', format_type="hex", sync_files=sync_files)
    important_border = get_color('reports.notes.important.border', format_type="hex", sync_files=sync_files)
    
    error_bg = get_color('reports.notes.error.background', format_type="hex", sync_files=sync_files)
    error_border = get_color('reports.notes.error.border', format_type="hex", sync_files=sync_files)
    
    success_bg = get_color('reports.notes.success.background', format_type="hex", sync_files=sync_files)
    success_border = get_color('reports.notes.success.border', format_type="hex", sync_files=sync_files)
    
    return f"""body {{
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
