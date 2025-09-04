"""
Colors configuration management module.
Provides centralized color management and resolution across all components.

Dimensión Transparencia: Solo get_colors_config() como función principal.
Todas las demás funciones eliminadas para evitar repetición.
"""

from typing import Dict, Any
from pathlib import Path

# Global configuration cache
_CONFIG_CACHE = None

def _load_colors_config(sync_files: bool) -> Dict[str, Any]:
    """Internal color configuration loader.
    
    Args:
        sync_files: Whether to use synchronized files or package files
        
    Returns:
        Complete color configuration dictionary
        
    Raises:
        RuntimeError: If configuration loading fails
    """
    global _CONFIG_CACHE
    
    try:
        from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
        
        # Use cached version if available
        cache_key = f"colors_{sync_files}"
        if _CONFIG_CACHE is not None and cache_key in _CONFIG_CACHE:
            return _CONFIG_CACHE[cache_key]
        
        # Load fresh configuration
        config_path = _resolve_config_path('components/colors', sync_files)
        config = _load_cached_files(config_path, sync_files)
        
        # Validate required sections
        required_keys = ['palettes', 'layout_styles']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
        
        # Cache the configuration
        if _CONFIG_CACHE is None:
            _CONFIG_CACHE = {}
        _CONFIG_CACHE[cache_key] = config
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load colors configuration: {e}") from e

def get_colors_config(sync_files: bool = False) -> Dict[str, Any]:
    """Public API for color configuration access.
    
    This is the ONLY function for accessing color resources.
    All other functionality is accessed through this configuration.
    
    Args:
        sync_files: Whether to use synchronized files or package files
        
    Returns:
        Complete color configuration
        
    Raises:
        RuntimeError: If loading fails
    """
    return _load_colors_config(sync_files)
