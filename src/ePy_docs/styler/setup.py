"""Central configuration manager for the files module.

This module provides a unified interface to load and cache all configuration
from JSON files, ensuring no hardcoded parameters and proper sync_json behavior.
"""

import os
import json
import shutil
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from functools import lru_cache

from ePy_suite.utils.data import _load_cached_json


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
        """Discover all JSON files in src and set up configuration paths with synchronization.
        
        Searches for JSON files in configuration directory and maps them to their
        corresponding paths in source. Also performs initial synchronization if needed.
        
        Assumptions:
            Project configuration structure follows expected patterns.
            Source files exist and are properly formatted JSON.
        """
        # Use DirectoryConfig to get the correct configuration path
        try:
            from ePy_suite.project.setup import DirectoryConfig, sync_all_json_configs
            
            project_config = DirectoryConfig()
            config_root = Path(project_config.folders.config)
            
            # Get the ePy_suite source directory (where the templates are)
            src_root = Path(__file__).parent.parent.parent  # src/ePy_suite/
            
            # Sync all JSON files first
            if not config_root.exists() or len(list(config_root.rglob("*.json"))) < 10:
                sync_all_json_configs(str(config_root.parent))
            
        except Exception as e:
            # Fallback to old behavior if DirectoryConfig fails
            package_root = Path(__file__).parent.parent.parent.parent
            src_root = package_root / "src" / "ePy_suite"
            config_root = package_root / "configuration"
        
        # Ensure configuration directory exists
        config_root.mkdir(exist_ok=True)
        
        # Discover all JSON files in config directory (not src)
        self._config_paths = {}
        self._src_paths = {}
        
        # Find all JSON files in CONFIGURATION directory
        for json_file in config_root.rglob("*.json"):
            # Get relative path from config root
            relative_path = json_file.relative_to(config_root)
            
            # Create config name from the file path
            config_name = self._create_config_name(relative_path)
            
            # Set up paths - config is primary, src is secondary
            config_path = str(json_file)
            
            # Try to find corresponding source file
            src_path = str(src_root / relative_path)
            
            self._config_paths[config_name] = config_path
            self._src_paths[config_name] = src_path if os.path.exists(src_path) else config_path
    
    def _create_config_name(self, relative_path: Path) -> str:
        """Create a configuration name from relative path.
        
        Args:
            relative_path: Path object representing relative path from config root.
            
        Returns:
            str: Underscore-separated configuration identifier.
            
        Assumptions:
            Path is a valid relative path with at least one component.
        """
        # Convert path like "files/styler/styles.json" to "files_styler_styles"
        parts = list(relative_path.parts[:-1])  # Remove the .json extension
        parts.append(relative_path.stem)  # Add filename without extension
        return "_".join(parts)
    
    def _sync_config_file(self, config_name: str) -> None:
        """Synchronize a single config file from src to configuration.
        
        Args:
            config_name: Unique identifier for the configuration file.
            
        Assumptions:
            Configuration name exists in _src_paths and _config_paths.
            Source file exists and is a valid JSON file.
        """
        if config_name not in self._src_paths or config_name not in self._config_paths:
            return
            
        src_path = self._src_paths[config_name]
        config_path = self._config_paths[config_name]
        
        try:
            # Copy from src to configuration if it doesn't exist or if src is newer
            if not os.path.exists(config_path) or os.path.getmtime(src_path) > os.path.getmtime(config_path):
                shutil.copy2(src_path, config_path)
        except Exception as e:
            pass
    
    def _load_config(self, config_name: str, sync_json: bool = True) -> Dict[str, Any]:
        """Load configuration from JSON file with caching and synchronization.
        
        Args:
            config_name: Unique identifier for the configuration file.
            sync_json: Whether to synchronize the file from source before loading.
            
        Returns:
            Dict[str, Any]: Loaded configuration data.
            
        Raises:
            ConfigurationError: If configuration not found or loading fails.
            
        Assumptions:
            Configuration name exists in _config_paths.
            JSON file is valid and properly formatted.
        """
        if config_name not in self._config_paths:
            raise ConfigurationError(f"Unknown configuration: {config_name}")
        
        cache_key = f"{config_name}_{sync_json}"
        
        # Return cached if available and sync_json is False
        if not sync_json and cache_key in self._cache:
            return self._cache[cache_key]
        
        # If sync_json is True, ensure the config file is synchronized
        if sync_json:
            self._sync_config_file(config_name)
        
        config_path = self._config_paths[config_name]
        
        # If config file doesn't exist in configuration, try to sync it
        if not os.path.exists(config_path):
            if sync_json:
                self._sync_config_file(config_name)
            
            # If still doesn't exist after sync, raise error
            if not os.path.exists(config_path):
                raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            config_data = _load_cached_json(config_path)
            if config_data is None:
                raise ConfigurationError(f"Failed to load configuration from: {config_path}")
            
            self._cache[cache_key] = config_data
            return config_data
            
        except Exception as e:
            raise ConfigurationError(f"Error loading {config_name} configuration: {e}")
    
    def get_config_by_path(self, relative_path: str, sync_json: bool = True) -> Dict[str, Any]:
        """Get configuration by relative path.
        
        Args:
            relative_path: Path relative to config root (e.g., 'files/styler/styles.json').
            sync_json: Whether to synchronize from source before loading.
            
        Returns:
            Dict[str, Any]: Loaded configuration data.
            
        Assumptions:
            Path exists and is a valid JSON file path relative to config root.
        """
        # Convert path to config name
        path_obj = Path(relative_path)
        config_name = self._create_config_name(path_obj)
        return self._load_config(config_name, sync_json)
    
    def get_colors_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get colors configuration."""
        return self.get_config_by_path('files/styler/colors.json', sync_json)
    
    def get_styles_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get styles configuration."""
        return self.get_config_by_path('files/styler/styles.json', sync_json)
    
    def get_section_properties_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get section properties configuration."""
        return self.get_config_by_path('files/writer/section_properties.json', sync_json)
    
    def get_project_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get project configuration."""
        return self.get_config_by_path('project/project.json', sync_json)
    
    def get_units_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get units configuration."""
        return self.get_config_by_path('units/units.json', sync_json)
    
    def get_conversion_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get conversion configuration."""
        return self.get_config_by_path('units/conversion.json', sync_json)
    
    def get_aliases_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get aliases configuration."""
        return self.get_config_by_path('units/aliases.json', sync_json)
    
    def get_prefix_config(self, sync_json: bool = True) -> Dict[str, Any]:
        """Get prefix configuration."""
        return self.get_config_by_path('units/prefix.json', sync_json)
    
    def get_nested_value(self, config_name: str, path: str, default: Any = None, sync_json: bool = True) -> Any:
        """Get a nested value from configuration using dot notation.
        
        Args:
            config_name: Configuration name or relative path.
            path: Dot-separated path to the nested value.
            default: Value to return if path not found.
            sync_json: Whether to synchronize from source before loading.
            
        Returns:
            Any: The nested configuration value or default.
            
        Raises:
            ConfigurationError: If path not found and no default provided.
            
        Assumptions:
            Configuration file exists and is valid JSON.
            Path format follows dot notation for nested values.
        """
        # Handle direct path-based loading for better flexibility
        if '/' in config_name:
            # This is a file path, load directly
            config = self.get_config_by_path(config_name, sync_json)
        else:
            # Legacy config name support
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
        """Invalidate cache for specific config or all configs.
        
        Args:
            config_name: Name of configuration to invalidate, or None to invalidate all.
            
        Assumptions:
            If config_name is provided, it should be a valid configuration name.
        """
        if config_name:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{config_name}_")]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()


# Singleton instance
_config_manager = _ConfigManager()


# Public API functions
def get_colors_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get colors configuration from colors.json.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: Complete colors configuration dictionary.
        
    Assumptions:
        colors.json exists and is valid.
    """
    return _config_manager.get_colors_config(sync_json)


def get_styles_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get styles configuration from styles.json.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: Complete styles configuration dictionary.
        
    Assumptions:
        styles.json exists and is valid.
    """
    return _config_manager.get_styles_config(sync_json)


def get_section_properties_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get section properties configuration.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: Section properties configuration dictionary.
        
    Assumptions:
        section_properties.json exists and is valid.
    """
    return _config_manager.get_section_properties_config(sync_json)


def get_project_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get project configuration.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: Project configuration dictionary.
        
    Assumptions:
        project.json exists and is valid.
    """
    return _config_manager.get_project_config(sync_json)


def get_units_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get units configuration.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: Units configuration dictionary.
        
    Assumptions:
        units.json exists and is valid.
    """
    return _config_manager.get_units_config(sync_json)


def get_color(path: str, format_type: str = "rgb", sync_json: bool = True) -> Union[List[int], str]:
    """Get a color value from colors configuration using dot notation.
    
    Args:
        path: Dot-separated path to the color value (e.g., 'reports.tables.header.default')
        format_type: Format type to return - "rgb" for RGB list or "hex" for hex string
        sync_json: Whether to reload from disk or use cache
        
    Returns:
        Color value as RGB list [r, g, b] or hex string '#RRGGBB' based on format_type
        
    Raises:
        ConfigurationError: If path not found or if color format is invalid
    """
    # Get the color value without fallback
    color_value = _config_manager.get_nested_value('files/styler/colors.json', path, None, sync_json)
    
    if color_value is None:
        raise ConfigurationError(f"Color path '{path}' not found in configuration")
    
    # Handle RGB format [r, g, b]
    if isinstance(color_value, list) and len(color_value) >= 3:
        r, g, b = color_value[:3]
        # Validate RGB values
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
            raise ConfigurationError(f"Invalid RGB values for {path}: {color_value}")
        
        # Return in requested format
        if format_type.lower() == "hex":
            return f"#{r:02x}{g:02x}{b:02x}"
        return [r, g, b]
        
    # Handle string references to other colors (like "brand.primary_blue")
    elif isinstance(color_value, str):
        if color_value.startswith('#'):
            # Convert hex to RGB if needed
            try:
                hex_color = color_value.lstrip('#')
                if len(hex_color) == 3:  # Short form like #ABC
                    hex_color = ''.join(c+c for c in hex_color)
                
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                
                if format_type.lower() == "rgb":
                    return [r, g, b]
                return color_value
            except ValueError:
                raise ConfigurationError(f"Invalid hex color format for {path}: {color_value}")
        else:
            # Resolve reference recursively
            return get_color(color_value, format_type, sync_json)
    
    # Invalid format
    raise ConfigurationError(f"Invalid color format for {path}: {color_value}")


def get_style_value(path: str, default: Any = None, sync_json: bool = True) -> Any:
    """Get a style value from styles configuration using dot notation.
    
    Args:
        path: Dot-separated path to the style value
        default: Default value if path not found
        sync_json: Whether to reload from disk or use cache
        
    Returns:
        Style value
        
    Raises:
        ConfigurationError: If path not found and no default provided
    """
    return _config_manager.get_nested_value('files/styler/styles.json', path, default, sync_json)


def get_config_value(config_name: str, path: str, default: Any = None, sync_json: bool = True) -> Any:
    """Get a value from any configuration using dot notation.
    
    Args:
        config_name: Name of the configuration ('colors', 'styles', etc.)
        path: Dot-separated path to the value
        default: Default value if path not found
        sync_json: Whether to reload from disk or use cache
        
    Returns:
        Configuration value
        
    Raises:
        ConfigurationError: If path not found and no default provided
    """
    return _config_manager.get_nested_value(config_name, path, default, sync_json)


def invalidate_cache(config_name: Optional[str] = None):
    """Invalidate configuration cache.
    
    Args:
        config_name: Specific config to invalidate, or None for all configs
    """
    _config_manager.invalidate_cache(config_name)


# Convenience functions for common operations
def _get_table_style_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get table style configuration.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: Table style configuration dictionary.
        
    Assumptions:
        styles.json exists with pdf_settings.table_style section.
    """
    return get_config_value('files/styler/styles.json', 'pdf_settings.table_style', {}, sync_json)


def _get_pdf_style_config(sync_json: bool = True) -> Dict[str, Any]:
    """Get PDF style configuration.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dict[str, Any]: PDF style configuration dictionary.
        
    Assumptions:
        styles.json exists with pdf_settings section.
    """
    return get_config_value('files/styler/styles.json', 'pdf_settings', {}, sync_json)


def _get_report_color(category: str, variant: str = 'default', sync_json: bool = True) -> List[int]:
    """Get report color for specific category and variant.
    
    Args:
        category: Color category (e.g., 'tables', 'headings').
        variant: Color variant within category (e.g., 'default', 'primary').
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        List[int]: RGB color values [r, g, b].
        
    Assumptions:
        colors.json exists with reports.<category>.<variant> section.
    """
    path = f"reports.{category}.{variant}"
    return get_color(path, "rgb", sync_json)
