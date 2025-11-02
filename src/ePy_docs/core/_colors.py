"""Colors configuration and utilities.

Provides color palette management and format conversion utilities.
"""
from typing import Dict, Any
import re


def get_colors_config() -> Dict[str, Any]:
    """Get colors configuration."""
    from ePy_docs.core._config import get_config_section
    return get_config_section('colors')


def validate_color_path(color_path: str) -> None:
    """Validate color path format."""
    if not re.match(r'^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*$', color_path):
        raise ValueError(f"Invalid color path format: {color_path}")


def get_color_from_path(color_path: str, format_type: str = "hex") -> Any:
    """Get color value from dot notation path."""
    validate_color_path(color_path)
    config = get_colors_config()
    
    # Navigate through path
    current = config
    for key in color_path.split('.'):
        try:
            current = current[key]
        except (KeyError, TypeError):
            raise KeyError(f"Color path not found: {color_path}")
    
    # Handle different color formats
    if isinstance(current, dict):
        # Try exact format match first
        if format_type in current:
            return current[format_type]
        # Try conversion from available formats
        for source_format in ['hex', 'rgb', 'hsl']:
            if source_format in current:
                return _convert_color_format(current[source_format], source_format, format_type)
    
    # Handle direct color values
    if isinstance(current, str):
        return _convert_color_format(current, 'hex', format_type)
    elif isinstance(current, list):
        return _convert_color_format(current, 'rgb', format_type)
    
    raise ValueError(f"Cannot extract {format_type} format from color at path: {color_path}")


def _convert_color_format(color_value: Any, from_format: str, to_format: str) -> Any:
    """Convert color between formats."""
    if from_format == to_format:
        return color_value
    
    if from_format == 'hex' and to_format == 'rgb' and isinstance(color_value, str):
        hex_color = color_value.lstrip('#')
        if len(hex_color) == 6:
            return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    
    elif from_format == 'rgb' and to_format == 'hex' and isinstance(color_value, list) and len(color_value) == 3:
        return f"#{color_value[0]:02x}{color_value[1]:02x}{color_value[2]:02x}"
    
    return color_value
