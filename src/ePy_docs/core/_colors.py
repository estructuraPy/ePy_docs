"""Colors configuration and utilities.

Centralized color palette management with format conversion.
Provides unified access to all color palettes and conversion utilities.
"""
from typing import Dict, Any, Union, List, Tuple
import re


def get_colors_config() -> Dict[str, Any]:
    """Get complete colors configuration from epyson files.
    
    Returns:
        Complete colors configuration dictionary
    """
    from ePy_docs.core._config import get_config_section
    return get_config_section('colors')


def validate_color_path(color_path: str) -> None:
    """Validate dot notation color path format.
    
    Args:
        color_path: Dot notation path like 'palettes.academic.primary'
        
    Raises:
        ValueError: If path format is invalid
    """
    if not re.match(r'^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*$', color_path):
        raise ValueError(f"Invalid color path format: {color_path}")


def _validate_rgb(rgb_values: List[int]) -> None:
    """Validate RGB color values are in valid range.
    
    Args:
        rgb_values: List of RGB values [R, G, B]
        
    Raises:
        ValueError: If RGB values are out of range
    """
    if not all(0 <= val <= 255 for val in rgb_values):
        raise ValueError(f"RGB values must be 0-255, got: {rgb_values}")


def _convert_color_format(color_value: Any, from_format: str, to_format: str) -> Any:
    """Convert color between different formats.
    
    Supports conversions between hex, rgb, and matplotlib formats.
    
    Args:
        color_value: Color value in source format
        from_format: Source format ('hex', 'rgb', 'matplotlib')
        to_format: Target format ('hex', 'rgb', 'matplotlib')
        
    Returns:
        Color value in target format
        
    Raises:
        ValueError: If conversion is not supported or value is invalid
    """
    if from_format == to_format:
        return color_value
    
    # Convert hex to RGB
    if from_format == 'hex' and to_format == 'rgb' and isinstance(color_value, str):
        hex_color = color_value.lstrip('#')
        if len(hex_color) == 6:
            rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            _validate_rgb(rgb)
            return rgb
    
    # Convert RGB to hex
    elif from_format == 'rgb' and to_format == 'hex' and isinstance(color_value, list):
        if len(color_value) == 3:
            _validate_rgb(color_value)
            return f"#{color_value[0]:02x}{color_value[1]:02x}{color_value[2]:02x}"
    
    # Convert RGB to matplotlib
    elif from_format == 'rgb' and to_format == 'matplotlib' and isinstance(color_value, list):
        if len(color_value) == 3:
            _validate_rgb(color_value)
            return tuple(c / 255.0 for c in color_value)
    
    # If no conversion available, return original
    return color_value


def get_color_from_path(color_path: str, format_type: str = "hex") -> Any:
    """Get color value from dot notation path with format conversion.
    
    Args:
        color_path: Dot notation path to color (e.g., 'palettes.academic.primary')
        format_type: Output format ('hex', 'rgb', 'matplotlib')
        
    Returns:
        Color value in requested format
        
    Raises:
        KeyError: If color path not found
        ValueError: If format conversion fails
    """
    validate_color_path(color_path)
    config = get_colors_config()
    
    # Navigate through configuration path
    current = config
    for key in color_path.split('.'):
        try:
            current = current[key]
        except (KeyError, TypeError):
            raise KeyError(f"Color path not found: {color_path}")
    
    # Try different color format sources
    if isinstance(current, dict):
        # Direct format match
        if format_type in current:
            return current[format_type]
        # Convert from available formats
        for source_format in ['hex', 'rgb', 'hsl']:
            if source_format in current:
                return _convert_color_format(current[source_format], source_format, format_type)
    
    # Handle direct color values
    if isinstance(current, str):
        return _convert_color_format(current, 'hex', format_type)
    elif isinstance(current, list):
        return _convert_color_format(current, 'rgb', format_type)
    
    raise ValueError(f"Cannot extract {format_type} format from color at path: {color_path}")


def _flatten_palette(palette: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten hierarchical palette structure to flat structure for backward compatibility.
    
    Converts new structure:
        {
            "colors": {"primary": [r,g,b], ...},
            "page": {"background": [r,g,b], ...},
            "table": {"header": [r,g,b], ...}
        }
    
    To old structure:
        {
            "primary": [r,g,b],
            "page_background": [r,g,b],
            "table_header": [r,g,b],
            ...
        }
    
    Args:
        palette: Hierarchical palette dictionary
        
    Returns:
        Flattened palette dictionary
    """
    flat = {}
    
    for key, value in palette.items():
        if key == 'description':
            flat[key] = value
        elif isinstance(value, dict):
            # Hierarchical section (colors, page, code, table)
            for subkey, subvalue in value.items():
                if key == 'colors':
                    # colors.primary -> primary
                    flat[subkey] = subvalue
                else:
                    # page.background -> page_background
                    # table.header -> table_header
                    flat[f"{key}_{subkey}"] = subvalue
        else:
            # Direct color (border_color, caption_color)
            flat[key] = value
    
    return flat


def get_palette_color(palette_name: str, color_name: str, format_type: str = "rgb") -> Union[List[int], str, Tuple[float, ...]]:
    """Get specific color from palette with automatic format conversion.
    
    Primary function for accessing colors from predefined palettes.
    Supports all major color formats with validation.
    Searches in layout_palettes first (complete palettes with all colors),
    then in color_palettes (simple 6-color palettes for highlighting).
    
    Handles both hierarchical and flat color names:
    - Hierarchical: 'page.background', 'table.header'
    - Flat (legacy): 'page_background', 'table_header'
    
    Args:
        palette_name: Palette identifier (e.g., 'creative', 'academic', 'blues')
        color_name: Color key within palette (e.g., 'page_background', 'primary')
        format_type: Output format ('rgb', 'hex', 'matplotlib')
        
    Returns:
        Color in requested format:
        - 'rgb': List[int] with values 0-255
        - 'hex': str like '#FF0000'
        - 'matplotlib': Tuple[float] with values 0.0-1.0
        
    Raises:
        ValueError: If palette or color not found, or conversion fails
    """
    config = get_colors_config()
    
    # Try layout_palettes first (complete palettes for layouts)
    if 'layout_palettes' in config and palette_name in config['layout_palettes']:
        palette = config['layout_palettes'][palette_name]
        # Flatten hierarchical structure for backward compatibility
        flat_palette = _flatten_palette(palette)
        if color_name in flat_palette:
            color_value = flat_palette[color_name]
            return _convert_color_format(color_value, 'rgb', format_type)
    
    # Try color_palettes second (simple 6-color palettes for highlighting)
    if 'color_palettes' in config and palette_name in config['color_palettes']:
        palette = config['color_palettes'][palette_name]
        if color_name in palette:
            color_value = palette[color_name]
            return _convert_color_format(color_value, 'rgb', format_type)
    
    # If not found in either, raise error
    available_layouts = list(config.get('layout_palettes', {}).keys())
    available_colors = list(config.get('color_palettes', {}).keys())
    raise ValueError(
        f"Color '{color_name}' not found in palette '{palette_name}'. "
        f"Available layout palettes: {available_layouts}. "
        f"Available color palettes: {available_colors}."
    )

