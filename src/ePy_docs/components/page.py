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
        return {
            'general_settings': self.get_config_by_path('core/settings.json', sync_json).get('general_settings', {}),
            'pdf_settings': {
                'margins': self.get_config_by_path('components/page.json', sync_json).get('pdf_settings', {}),
                'styles': self.get_config_by_path('components/text.json', sync_json).get('pdf_styles', {}),
                'table_style': self.get_config_by_path('components/tables.json', sync_json).get('table_style', {}),
                'note_settings': self.get_config_by_path('components/notes.json', sync_json).get('note_settings', {}),
                'reference_settings': self.get_config_by_path('references/references.json', sync_json).get('reference_settings', {})
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
    """Get general settings from settings.json."""
    return _config_manager.get_config_by_path('core/settings.json', sync_json)


def get_full_project_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get complete project configuration including styling components."""
    project_data = _config_manager.get_project_config(sync_json)
    
    tables_config = _config_manager.get_config_by_path('components/tables.json', sync_json)
    colors_config = _config_manager.get_config_by_path('components/colors.json', sync_json)
    styles_config = _config_manager.get_config_by_path('components/page.json', sync_json)
    
    styling_config = {
        'tables': tables_config,
        'colors': colors_config,
        'styles': styles_config,
        'figures': styles_config.get('figures', {'dpi': 150, 'quality': 'high', 'format': 'png'}),
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
# PDF Styling Classes (Active - Uncommented when needed)
# =============================================================================
