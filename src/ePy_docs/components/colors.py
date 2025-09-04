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

def get_color(color_path: str, format_type: str = "rgb", sync_files: bool = False):
    """Get specific color using color path notation.
    
    Supports two formats:
    - Simple: "palette.tone" (e.g., "brand.primary")
    - Layout: "layout_styles.layout.element.property" (e.g., "layout_styles.creative.typography.header_color")
    
    Args:
        color_path: Color path in supported formats
        format_type: Output format ("rgb", "hex", etc.)
        sync_files: Whether to use synchronized files
        
    Returns:
        Color value in requested format
        
    Raises:
        KeyError: If color path not found
        ValueError: If invalid format requested
    """
    config = get_colors_config(sync_files)
    
    if color_path.startswith("layout_styles."):
        # Handle layout style color references
        path_parts = color_path.split(".")
        if len(path_parts) < 4:  # layout_styles.layout_name.section.property
            raise ValueError(f"Invalid layout color path: {color_path}")
        
        layout_name = path_parts[1]
        element_path = ".".join(path_parts[2:])  # Everything after layout_name
        
        # Navigate to the color reference
        if layout_name not in config['layout_styles']:
            raise KeyError(f"Layout '{layout_name}' not found")
        
        current = config['layout_styles'][layout_name]
        for part in element_path.split('.'):
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Path '{element_path}' not found in layout '{layout_name}'")
            current = current[part]
        
        # Current should be a palette reference {"palette": "...", "tone": "..."}
        if not isinstance(current, dict) or 'palette' not in current or 'tone' not in current:
            raise ValueError(f"Invalid palette reference at {color_path}")
        
        # Get the actual color from the palette
        palette_name = current['palette']
        tone = current['tone']
        
        if palette_name not in config['palettes']:
            raise KeyError(f"Palette '{palette_name}' not found")
        
        palette = config['palettes'][palette_name]
        if tone not in palette:
            raise KeyError(f"Tone '{tone}' not found in palette '{palette_name}'")
        
        rgb_value = palette[tone]
        
    else:
        # Handle simple palette.tone references
        path_parts = color_path.split('.')
        if len(path_parts) != 2:
            raise ValueError(f"Invalid color path format: {color_path}. Expected 'palette.tone' or 'layout_styles.layout.element.property'")
        
        palette_name, tone = path_parts
        
        # Look in palettes
        if palette_name not in config['palettes']:
            raise KeyError(f"Palette '{palette_name}' not found")
        
        palette = config['palettes'][palette_name]
        if tone not in palette:
            raise KeyError(f"Tone '{tone}' not found in palette '{palette_name}'")
        
        rgb_value = palette[tone]
    
    # Convert to requested format
    if format_type == "rgb":
        return rgb_value
    elif format_type == "hex":
        return f"#{rgb_value[0]:02x}{rgb_value[1]:02x}{rgb_value[2]:02x}"
    else:
        raise ValueError(f"Unsupported format: {format_type}")
