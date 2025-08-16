"""PDF styling utilities for report generation.

Provides PDF style configuration, color management, and layout settings
for consistent document formatting using ReportLab with JSON-based configuration.
"""

import os
import json
import shutil
from typing import Dict, Any, Optional, Tuple, Union, List
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel
from pathlib import Path
from functools import lru_cache

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle

from ePy_docs.files.data import _load_cached_json


# =============================================================================
# Configuration Constants
# =============================================================================

# Default general settings (previously in core/settings.json)
DEFAULT_GENERAL_SETTINGS = {
    "general_settings": {
        "default_dpi": 300,
        "default_encoding": "utf-8",
        "temp_cleanup": True
    }
}

# =============================================================================
# Configuration Management
# =============================================================================

class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class _ConfigManager:
    """Singleton configuration manager for files module.
    
    Handles loading, caching, and synchronizing configuration files between
    source templates and project configuration directory.
    
    Assumptions:
        Configuration files follow a specific directory structure.
        JSON files in project configuration take precedence over source templates.
    """
    
    _instance = None
    _cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._cache = {}
            self._discover_and_sync_configs()
            self._initialized = True
    
    def _discover_and_sync_configs(self):
        """Discover all JSON files and set up configuration paths.
        
        Strict configuration discovery without fallbacks.
        """
        from ePy_docs.project.setup import DirectoryConfig, sync_all_json_configs
        
        project_config = DirectoryConfig()
        config_root = Path(project_config.folders.config)
        src_root = Path(__file__).parent.parent.parent
        
        if not config_root.exists() or len(list(config_root.rglob("*.json"))) < 10:
            sync_all_json_configs(str(config_root.parent))
        
        if not config_root.exists():
            raise ConfigurationError(f"Configuration directory not found: {config_root}")
        
        self._config_paths = {}
        self._src_paths = {}
        
        for json_file in config_root.rglob("*.json"):
            relative_path = json_file.relative_to(config_root)
            config_name = self._create_config_name(relative_path)
            config_path = str(json_file)
            src_path = str(src_root / relative_path)
            
            self._config_paths[config_name] = config_path
            self._src_paths[config_name] = src_path if os.path.exists(src_path) else config_path
    
    def _create_config_name(self, relative_path: Path) -> str:
        """Create configuration name from relative path."""
        parts = list(relative_path.parts[:-1])
        parts.append(relative_path.stem)
        return "_".join(parts)
    
    def _sync_config_file(self, config_name: str) -> None:
        """Synchronize config file from src to configuration."""
        if config_name not in self._src_paths or config_name not in self._config_paths:
            raise ConfigurationError(f"Configuration {config_name} not found in mapping")
            
        src_path = self._src_paths[config_name]
        config_path = self._config_paths[config_name]
        
        if not os.path.exists(src_path):
            raise ConfigurationError(f"Source configuration file not found: {src_path}")
        
        if not os.path.exists(config_path) or os.path.getmtime(src_path) > os.path.getmtime(config_path):
            shutil.copy2(src_path, config_path)
    
    def _load_config(self, config_name: str, sync_json: bool = True) -> Dict[str, Any]:
        """Load configuration from JSON file with caching and synchronization."""
        if config_name not in self._config_paths:
            raise ConfigurationError(f"Unknown configuration: {config_name}")
        
        cache_key = f"{config_name}_{sync_json}"
        
        if not sync_json and cache_key in self._cache:
            return self._cache[cache_key]
        
        if sync_json:
            self._sync_config_file(config_name)
        
        config_path = self._config_paths[config_name]
        
        if not os.path.exists(config_path):
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        config_data = _load_cached_json(config_path)
        if config_data is None:
            raise ConfigurationError(f"Failed to load configuration from: {config_path}")
        
        self._cache[cache_key] = config_data
        return config_data
    
    def get_config_by_path(self, relative_path: str, sync_json: bool = True) -> Dict[str, Any]:
        """Get configuration by relative path."""
        path_obj = Path(relative_path)
        config_name = self._create_config_name(path_obj)
        return self._load_config(config_name, sync_json)
    
    def get_colors_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get colors configuration."""
        return self._load_config('components_colors', sync_json)
    
    def get_styles_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get styles configuration - now deprecated, use specific config functions."""
        # Return a combined config for backward compatibility
        general_settings = DEFAULT_GENERAL_SETTINGS.get('general_settings')
        if general_settings is None:
            raise ConfigurationError("general_settings not found in DEFAULT_GENERAL_SETTINGS")
        
        # Load configurations without fallbacks - will raise exceptions if not found
        page_config = self.get_config_by_path('components/page.json', sync_json)
        text_config = self.get_config_by_path('components/text.json', sync_json)
        tables_config = self.get_config_by_path('components/tables.json', sync_json)
        notes_config = self.get_config_by_path('components/notes.json', sync_json)
        references_config = self.get_config_by_path('references/references.json', sync_json)
        
        # Extract required sections - raise error if not found
        pdf_settings = page_config.get('pdf_settings')
        pdf_styles = text_config.get('pdf_styles')
        table_style = tables_config.get('table_style')
        note_settings = notes_config.get('note_settings')
        reference_settings = references_config.get('reference_settings')
        
        if any(x is None for x in [pdf_settings, pdf_styles, table_style, note_settings, reference_settings]):
            raise ConfigurationError("One or more required configuration sections not found")
        
        return {
            'general_settings': general_settings,
            'pdf_settings': {
                'margins': pdf_settings,
                'styles': pdf_styles,
                'table_style': table_style,
                'note_settings': note_settings,
                'reference_settings': reference_settings
            }
        }
    
    def get_project_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get project configuration."""
        return self.get_config_by_path('project/project.json', sync_json)
    
    def get_conversion_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get conversion configuration."""
        return self.get_config_by_path('units/conversion.json', sync_json)
    
    def get_aliases_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get aliases configuration."""
        return self.get_config_by_path('units/aliases.json', sync_json)
    
    def get_nested_value(self, config_name: str, path: str, default: Any = None, sync_json: bool = True) -> Any:
        """Get nested value from configuration using dot notation."""
        if '/' in config_name:
            config = self.get_config_by_path(config_name, sync_json)
        else:
            config = self._load_config(config_name, sync_json)
        
        keys = path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            if default is None:
                raise ConfigurationError(f"Required configuration path '{path}' not found in {config_name}")
            return default
    
    def invalidate_cache(self, config_name: Optional[str] = None):
        """Invalidate configuration cache."""
        if config_name:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{config_name}_")]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()


# Singleton instance
_config_manager = _ConfigManager()


# =============================================================================
# Public API functions
# =============================================================================

def get_colors_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get colors configuration from colors.json."""
    return _config_manager.get_colors_config(sync_json)


def get_styles_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get styles configuration - now deprecated, use specific config functions."""
    return _config_manager.get_styles_config(sync_json)


def get_project_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get project configuration."""
    return _config_manager.get_project_config(sync_json)


def get_references_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get references configuration from references.json."""
    return _config_manager.get_config_by_path('references/references.json', sync_json)


def get_notes_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get notes configuration from notes.json."""
    return _config_manager.get_config_by_path('components/notes.json', sync_json)


def get_tables_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get tables configuration from tables.json."""
    return _config_manager.get_config_by_path('components/tables.json', sync_json)


def get_text_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get text configuration from text.json."""
    return _config_manager.get_config_by_path('components/text.json', sync_json)


def get_page_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get page configuration from page.json."""
    return _config_manager.get_config_by_path('components/page.json', sync_json)


def get_general_settings(sync_json: bool = True) -> Dict[str, Any]:
    """Get general settings with built-in defaults.
    
    Returns default general settings including DPI, encoding, and cleanup options.
    The sync_json parameter is kept for API compatibility but not used.
    
    Returns:
        Dictionary with general settings configuration.
    """
    return DEFAULT_GENERAL_SETTINGS


def get_full_project_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get complete project configuration including styling components."""
    project_data = _config_manager.get_project_config(sync_json)
    
    tables_config = _config_manager.get_config_by_path('components/tables.json', sync_json)
    colors_config = _config_manager.get_config_by_path('components/colors.json', sync_json)
    styles_config = _config_manager.get_config_by_path('components/page.json', sync_json)
    images_config = _config_manager.get_config_by_path('components/images.json', sync_json)
    
    styling_config = {
        'tables': tables_config,
        'colors': colors_config,
        'styles': styles_config,
        'figures': images_config,  # Use images.json for figures configuration
        'citations': {'default_style': 'apa'}
    }
    
    full_config = project_data.copy()
    full_config['styling'] = styling_config
    
    return full_config


def sync_ref(citation_style: Optional[str] = None) -> None:
    """Synchronize reference files from source to configuration directory."""
    from ePy_docs.project.setup import DirectoryConfig
    config = DirectoryConfig()
    
    src_ref_dir = Path(__file__).parent.parent / "references"
    config_ref_dir = Path(config.folders.config) / "references"
    
    config_ref_dir.mkdir(parents=True, exist_ok=True)
    
    # Always sync references.bib
    bib_file = "references.bib"
    src_bib = src_ref_dir / bib_file
    config_bib = config_ref_dir / bib_file
    
    if not src_bib.exists():
        raise ConfigurationError(f"Source bibliography file not found: {src_bib}")
    
    if not config_bib.exists() or src_bib.stat().st_mtime > config_bib.stat().st_mtime:
        shutil.copy2(str(src_bib), str(config_bib))
    
    if citation_style:
        csl_file = f"{citation_style}.csl"
        src_csl = src_ref_dir / csl_file
        config_csl = config_ref_dir / csl_file
        
        if not src_csl.exists():
            raise ConfigurationError(f"Citation style file not found: {src_csl}")
        
        if not config_csl.exists() or src_csl.stat().st_mtime > config_csl.stat().st_mtime:
            shutil.copy2(str(src_csl), str(config_csl))
    else:
        if not src_ref_dir.exists():
            raise ConfigurationError(f"Source references directory not found: {src_ref_dir}")
        
        for src_file in src_ref_dir.iterdir():
            if src_file.is_file() and src_file.suffix == '.csl':
                config_file = config_ref_dir / src_file.name
                
                if not config_file.exists() or src_file.stat().st_mtime > config_file.stat().st_mtime:
                    shutil.copy2(str(src_file), str(config_file))


def get_color(path: str, format_type: str = "rgb", sync_json: bool = True) -> Union[List[int], str]:
    """Get color value from colors configuration using dot notation."""
    color_value = _config_manager.get_nested_value('components_colors', path, None, sync_json)
    
    if color_value is None:
        raise ConfigurationError(f"Color path '{path}' not found in configuration")
    
    if isinstance(color_value, list) and len(color_value) >= 3:
        r, g, b = color_value[:3]
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
            raise ConfigurationError(f"Invalid RGB values for {path}: {color_value}")
        
        if format_type.lower() == "hex":
            return f"#{r:02x}{g:02x}{b:02x}"
        return [r, g, b]
        
    elif isinstance(color_value, str):
        if color_value.startswith('#'):
            hex_color = color_value.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c+c for c in hex_color)
            
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                
                if format_type.lower() == "rgb":
                    return [r, g, b]
                return color_value
            except ValueError:
                raise ConfigurationError(f"Invalid hex color format for {path}: {color_value}")
        else:
            return get_color(color_value, format_type, sync_json)
    
    raise ConfigurationError(f"Invalid color format for {path}: {color_value}")


def get_style_value(path: str, default: Any = None, sync_json: bool = True) -> Any:
    """Get style value from styles configuration using dot notation."""
    return _config_manager.get_nested_value('components_page', path, default, sync_json)


def get_config_value(config_name: str, path: str, default: Any = None, sync_json: bool = True) -> Any:
    """Get value from any configuration using dot notation."""
    return _config_manager.get_nested_value(config_name, path, default, sync_json)


def invalidate_cache(config_name: Optional[str] = None):
    """Invalidate configuration cache."""
    _config_manager.invalidate_cache(config_name)


def get_units_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get units configuration."""
    return _config_manager.get_config_by_path('units/units.json', sync_json)


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


# =============================================================================
# Citation Style and Layout Management
# =============================================================================

def get_available_csl_styles() -> Dict[str, str]:
    """Get available CSL citation styles from the references directory.
    
    Returns:
        Dict[str, str]: Dictionary mapping style names to CSL file names
        
    Example:
        {
            'ieee': 'ieee.csl',
            'apa': 'apa.csl', 
            'chicago': 'chicago.csl'
        }
    """
    references_dir = Path(__file__).parent.parent / "references"
    available_styles = {}
    
    if references_dir.exists():
        for csl_file in references_dir.glob("*.csl"):
            style_name = csl_file.stem.lower()
            available_styles[style_name] = csl_file.name
    
    return available_styles


def validate_csl_style(style_name: str) -> str:
    """Validate and get the CSL file name for a given style.
    
    Args:
        style_name: Name of the citation style (e.g., 'ieee', 'apa', 'chicago')
        
    Returns:
        str: CSL file name (e.g., 'ieee.csl')
        
    Raises:
        ValueError: If the style is not available in references directory
    """
    if not style_name:
        raise ValueError("Citation style name is required")
    
    available_styles = get_available_csl_styles()
    
    if not available_styles:
        raise ValueError("No CSL files found in references directory")
    
    # Normalize style name
    style_name = style_name.lower().strip()
    
    if style_name in available_styles:
        return available_styles[style_name]
    
    # If not found, check if it's already a .csl filename
    if style_name.endswith('.csl'):
        base_name = style_name[:-4]
        if base_name in available_styles:
            return style_name
    
    # If style not found, raise error
    available_list = ', '.join(available_styles.keys())
    raise ValueError(f"Citation style '{style_name}' not found. Available styles: {available_list}")


def get_layout_config(layout_name: str = None) -> Dict[str, Any]:
    """Get layout configuration from page.json.
    
    Args:
        layout_name: Name of the layout (if None, uses default_layout from page.json)
        
    Returns:
        Dict[str, Any]: Layout configuration
        
    Raises:
        ValueError: If layout is not found in page.json
    """
    import json
    from pathlib import Path
    
    # Use package page.json directly - no fallbacks
    page_file = Path(__file__).parent / "page.json"
    
    if not page_file.exists():
        raise ValueError(f"Page configuration file not found: {page_file}")
    
    with open(page_file, 'r', encoding='utf-8') as f:
        page_config = json.load(f)
    
    # If no layout_name provided, use default_layout
    if layout_name is None:
        if 'default_layout' not in page_config:
            raise ValueError("No default_layout specified in page.json")
        layout_name = page_config['default_layout']
    
    if 'layouts' not in page_config:
        raise ValueError("No layouts found in page.json")
    
    layouts_config = page_config['layouts']
    
    if layout_name not in layouts_config:
        available_layouts = ', '.join(layouts_config.keys())
        raise ValueError(f"Layout '{layout_name}' not found. Available layouts: {available_layouts}")
    
    return layouts_config[layout_name]
    
    return layouts_config[layout_name]


def get_default_citation_style(layout_name: str = None) -> str:
    """Get default citation style from layout configuration.
    
    Args:
        layout_name: Name of the layout (if None, uses default_layout from styler.json)
        
    Returns:
        str: Citation style name from layout configuration
        
    Raises:
        ValueError: If layout is not found in styler.json
    """
    # If no layout_name provided, get the default layout from styler.json
    if layout_name is None:
        import json
        from pathlib import Path
        
        # Use package page.json directly - no fallbacks
        page_file = Path(__file__).parent / "page.json"
        
        if not page_file.exists():
            raise ValueError(f"Page configuration file not found: {page_file}")
        
        with open(page_file, 'r', encoding='utf-8') as f:
            page_config = json.load(f)
        
        if 'default_layout' not in page_config:
            raise ValueError("No default_layout specified in page.json")
        layout_name = page_config['default_layout']
    
    layout_config = get_layout_config(layout_name)
    
    if 'citation_style' not in layout_config:
        raise ValueError(f"Layout '{layout_name}' does not specify citation_style")
    
    return layout_config['citation_style']


# =============================================================================
# PDF Configuration and Utilities
# =============================================================================

class PDFConfigBuilder:
    """Builder pattern for PDF configuration from various JSON sources."""
    
    def __init__(self, sync_json: bool = True):
        self.sync_json = sync_json
        self._config = {
            'format': {},
            'margins': {},
            'fonts': {},
            'colors': {},
            'layout': {}
        }
    
    def with_layout(self, layout_name: str) -> 'PDFConfigBuilder':
        """Set layout configuration."""
        layout_config = get_layout_config(layout_name)
        self._config['layout'] = layout_config
        return self
    
    def with_margins(self, top: float = 1.0, bottom: float = 1.0, 
                    left: float = 1.0, right: float = 1.0) -> 'PDFConfigBuilder':
        """Set page margins in inches."""
        self._config['margins'] = {
            'top': f"{top}in",
            'bottom': f"{bottom}in", 
            'left': f"{left}in",
            'right': f"{right}in"
        }
        return self
    
    def with_format_options(self, documentclass: str = 'article',
                           colorlinks: bool = True, 
                           keep_tex: bool = False) -> 'PDFConfigBuilder':
        """Set PDF format options."""
        self._config['format'] = {
            'documentclass': documentclass,
            'colorlinks': colorlinks,
            'keep-tex': keep_tex
        }
        return self
    
    def with_toc(self, enabled: bool = True, depth: int = 3) -> 'PDFConfigBuilder':
        """Set table of contents options."""
        self._config.update({
            'toc': enabled,
            'toc-depth': depth
        })
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the complete PDF configuration."""
        return self._config


class QuartoConfigManager:
    """Manager for Quarto-specific configuration operations."""
    
    @staticmethod
    def merge_crossref_config() -> Dict[str, Any]:
        """Merge crossref configuration from multiple component files."""
        crossref_config = {}
        
        # Load from images.json
        try:
            images_config = get_config_value('components/images.json', 'crossref', {})
            if images_config:
                crossref_config.update(images_config)
        except ConfigurationError:
            pass
        
        # Load from tables.json  
        try:
            tables_config = get_config_value('components/tables.json', 'crossref', {})
            if tables_config:
                crossref_config.update(tables_config)
        except ConfigurationError:
            pass
        
        # Load from equations.json
        try:
            equations_config = get_config_value('components/equations.json', 'crossref', {})
            if equations_config:
                crossref_config.update(equations_config)
        except ConfigurationError:
            pass
        
        return crossref_config
    
    @staticmethod
    def get_bibliography_config() -> Dict[str, Any]:
        """Get bibliography configuration."""
        try:
            # Try to get from project references
            from ePy_docs.project.setup import DirectoryConfig
            config = DirectoryConfig()
            ref_dir = Path(config.folders.config) / "references"
            
            bib_file = ref_dir / "references.bib"
            if bib_file.exists():
                return {
                    'bibliography': str(bib_file.relative_to(Path.cwd())),
                    'csl': str((ref_dir / f"{get_default_citation_style()}.csl").relative_to(Path.cwd()))
                }
        except Exception:
            pass
        
        # Fallback to package references
        ref_dir = Path(__file__).parent.parent / "references"
        return {
            'bibliography': str(ref_dir / "references.bib"),
            'csl': str(ref_dir / f"{get_default_citation_style()}.csl")
        }


class DocumentStyler:
    """Handles document styling operations for PDF generation."""
    
    def __init__(self, layout_name: str = None):
        self.page_config = self._load_page_config()
        self.text_config = self._load_text_config()
        self.layout_name = layout_name or self.page_config['default_layout']
        self.layout_config = self._get_layout_config()
    
    def _load_page_config(self) -> Dict[str, Any]:
        """Load page configuration from JSON file."""
        config_path = Path(__file__).parent / "page.json"
        
        if not config_path.exists():
            raise ConfigurationError(f"Page configuration not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_text_config(self) -> Dict[str, Any]:
        """Load text configuration from JSON file."""
        config_path = Path(__file__).parent / "text.json"
        
        if not config_path.exists():
            raise ConfigurationError(f"Text configuration not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_layout_config(self) -> Dict[str, Any]:
        """Get layout configuration for the specified layout."""
        if 'layouts' not in self.page_config:
            raise ConfigurationError("No layouts configuration found in page.json")
        
        layouts = self.page_config['layouts']
        if self.layout_name not in layouts:
            raise ConfigurationError(f"Layout '{self.layout_name}' not found in configuration")
        
        return layouts[self.layout_name]
    
    def get_font_config(self) -> Dict[str, Any]:
        """Get font configuration from text.json."""
        if 'text' not in self.text_config:
            raise ConfigurationError("text section not found in text.json")
        
        text_settings = self.text_config['text']
        
        # Check for required configuration in normal text settings
        if 'normal' not in text_settings:
            raise ConfigurationError("normal text settings not found in text.json")
        
        normal_settings = text_settings['normal']
        required_keys = ['fontSize', 'lineSpacing']
        
        for key in required_keys:
            if key not in normal_settings:
                raise KeyError(f"Required font configuration '{key}' not found in text.json normal settings")
        
        font_config = {
            'fontsize': f"{normal_settings['fontSize']}pt",
            'linestretch': normal_settings['lineSpacing']
        }
        
        if 'font_family' in text_settings:
            font_config['mainfont'] = text_settings['font_family']
        
        return font_config
    
    def get_margin_config(self) -> Dict[str, str]:
        """Get margin configuration based on layout."""
        if 'margins' not in self.layout_config:
            raise KeyError("margins configuration not found in layout")
        
        margins = self.layout_config['margins']
        required_margins = ['top', 'bottom', 'left', 'right']
        
        for margin in required_margins:
            if margin not in margins:
                raise KeyError(f"Required margin '{margin}' not found in layout configuration")
        
        return {
            'margin-top': f"{margins['top']}in",
            'margin-bottom': f"{margins['bottom']}in", 
            'margin-left': f"{margins['left']}in",
            'margin-right': f"{margins['right']}in"
        }
    
    def get_header_config(self) -> Dict[str, Any]:
        """Get header styling configuration directly from layout config."""
        if 'header_style' not in self.layout_config:
            raise KeyError("header_style not found in layout configuration")
        
        header_style = self.layout_config['header_style']
        
        # Get global page configuration
        if 'toc' not in self.page_config:
            raise KeyError("toc configuration not found in page.json")
        if 'number-sections' not in self.page_config:
            raise KeyError("number-sections configuration not found in page.json")
        
        config = {
            'toc': self.page_config['toc'],
            'number-sections': self.page_config['number-sections']
        }
        
        # Apply header style specific configuration
        if header_style == 'formal':
            config['header-includes'] = [
                r'\usepackage{titlesec}',
                r'\usepackage{fancyhdr}',
                r'\pagestyle{fancy}',
                r'\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}',
                r'\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}',
                r'\fancyhead[L]{\leftmark}',
                r'\fancyhead[R]{\thepage}',
                r'\fancyfoot[C]{}'
            ]
        elif header_style == 'modern':
            config['header-includes'] = [
                r'\usepackage{titlesec}',
                r'\usepackage{fancyhdr}',
                r'\usepackage{xcolor}',
                r'\pagestyle{fancy}',
                r'\titleformat{\section}{\Large\sffamily\bfseries\color{blue!70!black}}{\thesection}{1em}{}',
                r'\titleformat{\subsection}{\large\sffamily\bfseries\color{blue!50!black}}{\thesubsection}{1em}{}',
                r'\fancyhead[L]{\sffamily\leftmark}',
                r'\fancyhead[R]{\sffamily\thepage}',
                r'\fancyfoot[C]{}'
            ]
        elif header_style == 'branded':
            config['header-includes'] = [
                r'\usepackage{titlesec}',
                r'\usepackage{fancyhdr}',
                r'\usepackage{xcolor}',
                r'\pagestyle{fancy}',
                r'\definecolor{corporateblue}{RGB}{0,102,153}',
                r'\titleformat{\section}{\Large\bfseries\color{corporateblue}}{\thesection}{1em}{}',
                r'\titleformat{\subsection}{\large\bfseries\color{corporateblue!70}}{\thesubsection}{1em}{}',
                r'\fancyhead[L]{\color{corporateblue}\leftmark}',
                r'\fancyhead[R]{\color{corporateblue}\thepage}',
                r'\fancyfoot[C]{\color{corporateblue}\hrule}'
            ]
        elif header_style == 'clean':
            config['header-includes'] = [
                r'\usepackage{titlesec}',
                r'\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}',
                r'\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}',
                r'\pagestyle{plain}'
            ]
        else:
            raise ValueError(f"Unknown header_style: {header_style}")
        
        return config
    
    def build_complete_config(self) -> Dict[str, Any]:
        """Build complete styling configuration for document."""
        config = {}
        
        # Add all style components
        config.update(self.get_font_config())
        config.update(self.get_margin_config()) 
        config.update(self.get_header_config())
        
        # Add crossref configuration
        config['crossref'] = QuartoConfigManager.merge_crossref_config()
        
        # Add bibliography configuration
        config.update(QuartoConfigManager.get_bibliography_config())
        
        return config


# =============================================================================
# Color and Theme Management
# =============================================================================

class ColorThemeManager:
    """Manages color themes for different document layouts."""
    
    def __init__(self):
        self.themes = {
            'academic': {
                'primary': [0, 51, 102],      # Dark blue
                'secondary': [102, 153, 204], # Light blue  
                'accent': [204, 102, 0],      # Orange
                'text': [51, 51, 51],         # Dark gray
                'background': [255, 255, 255] # White
            },
            'technical': {
                'primary': [51, 102, 153],    # Steel blue
                'secondary': [153, 204, 255], # Light steel blue
                'accent': [255, 102, 51],     # Orange red
                'text': [34, 34, 34],         # Very dark gray
                'background': [248, 249, 250] # Light gray
            },
            'corporate': {
                'primary': [34, 34, 34],      # Very dark gray
                'secondary': [102, 102, 102], # Medium gray
                'accent': [0, 123, 191],      # Corporate blue
                'text': [51, 51, 51],         # Dark gray
                'background': [255, 255, 255] # White
            },
            'minimal': {
                'primary': [68, 68, 68],      # Dark gray
                'secondary': [136, 136, 136], # Medium gray
                'accent': [17, 17, 17],       # Almost black
                'text': [51, 51, 51],         # Dark gray  
                'background': [255, 255, 255] # White
            }
        }
    
    def get_theme_colors(self, theme_name: str) -> Dict[str, List[int]]:
        """Get color palette for specified theme."""
        if theme_name not in self.themes:
            theme_name = 'technical'  # Default fallback
        
        return self.themes[theme_name]
    
    def get_latex_colors(self, theme_name: str) -> Dict[str, str]:
        """Get LaTeX color definitions for theme."""
        colors = self.get_theme_colors(theme_name)
        latex_colors = {}
        
        for color_name, rgb_values in colors.items():
            r, g, b = rgb_values
            latex_colors[color_name] = f"rgb({r/255:.3f},{g/255:.3f},{b/255:.3f})"
        
        return latex_colors
    
    def generate_css_variables(self, theme_name: str) -> str:
        """Generate CSS custom properties for theme."""
        colors = self.get_theme_colors(theme_name)
        css_vars = [":root {"]
        
        for color_name, rgb_values in colors.items():
            r, g, b = rgb_values
            css_vars.append(f"  --color-{color_name}: rgb({r}, {g}, {b});")
        
        css_vars.append("}")
        return "\n".join(css_vars)


def create_css_styles(sync_json: bool = True) -> str:
    """Create CSS styles for HTML output.
    
    Generates CSS styling for HTML output based on the project's color scheme
    from JSON configuration files. The styles include heading colors, figure and
    table captions, equation styling, and cross-reference link colors.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        str: Complete CSS styles as a string, ready to be written to a styles.css file.
        
    Assumes:
        The required JSON configuration files exist with valid color definitions.
    """
    # Get colors for styling from JSON configuration
    try:
        primary_blue = get_color('brand.brand_secondary', format_type="hex", sync_json=sync_json)
        accent_red = get_color('brand.brand_primary', format_type="hex", sync_json=sync_json)
        secondary_gray = get_color('brand.brand_tertiary', format_type="hex", sync_json=sync_json)
    except ConfigurationError:
        # Fallback colors
        primary_blue = "#0066cc"
        accent_red = "#cc0000" 
        secondary_gray = "#666666"
    
    css = f"""
    /* Custom ePy_suite heading styles with high specificity */
    .quarto-title-block h1,
    h1.title,
    h1 {{ 
        color: {primary_blue} !important; 
    }}
    
    .quarto-title-block h2,
    h2.subtitle,
    h2 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h3,
    h3 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h4,
    h4 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h5,
    h5 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h6,
    h6 {{ 
        color: {secondary_gray} !important; 
    }}
    
    /* Figure and table caption styling */
    .figure-caption,
    .table-caption {{
        color: {secondary_gray} !important;
        font-style: italic;
        margin-top: 0.5em;
    }}
    
    /* Equation styling */
    .equation {{
        color: {primary_blue};
    }}
    
    /* Cross-reference link colors */
    .quarto-xref {{
        color: {accent_red} !important;
        text-decoration: underline;
    }}
    
    .quarto-xref:hover {{
        color: {primary_blue} !important;
    }}
    
    /* Table styling */
    .table-striped > tbody > tr:nth-of-type(odd) {{
        background-color: rgba(0, 102, 204, 0.05);
    }}
    
    /* Code block styling */
    pre {{
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.375rem;
    }}
    
    /* Callout styling */
    .callout-note .callout-icon {{
        color: {primary_blue};
    }}
    
    .callout-warning .callout-icon {{
        color: #ffc107;
    }}
    
    .callout-tip .callout-icon {{
        color: #28a745;
    }}
    
    .callout-caution .callout-icon {{
        color: #fd7e14;
    }}
    
    .callout-important .callout-icon {{
        color: {accent_red};
    }}
    """
    
    return css