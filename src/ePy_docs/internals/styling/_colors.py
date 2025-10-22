from typing import Dict, Any
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path

def load_colors():
    """ PURIFICADO: Delegate to colors.py guardian - NO DIRECT ACCESS!"""
    try:
        return get_colors_config()
    except Exception as e:
        # No fallbacks - configuration must be complete
        raise ValueError(f"Failed to load colors configuration: {e}. Please ensure colors.json is properly configured.")

def get_colors_config() -> Dict[str, Any]:
    """Get colors configuration.
    
    Returns:
        Complete colors configuration
        
    Raises:
        RuntimeError: Si la carga falla
        
    Assumptions:
        El archivo colors.json existe en la ubicación resuelta
    """
    try:
        from ePy_docs.config.setup import get_config_section
        config = get_config_section('colors')
        
        required_keys = ['palettes', 'layout_styles']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load colors configuration: {e}") from e


def get_color_from_path(color_path: str, format_type: str = "hex") -> Any:
    """Get color value from dot notation path.
    
    Compatibility function for legacy color access patterns.
    
    Args:
        color_path: Dot notation path (e.g., 'brand.primary', 'layout_styles.corporate.typography.h1')
        format_type: Output format ('hex', 'rgb', 'hsl')
        
    Returns:
        Color value in requested format
        
    Raises:
        KeyError: Si la ruta del color no existe
        ValueError: Si el formato no es soportado
        
    Assumptions:
        La configuración de colores contiene las rutas especificadas
    """
    config = get_colors_config()
    
    # Navigate through the path
    keys = color_path.split('.')
    current = config
    
    # Handle legacy paths that don't include 'palettes' prefix
    if len(keys) >= 2 and keys[0] in ['brand', 'neutrals', 'blues', 'reds', 'greens', 'oranges', 'purples', 'grays_cool', 'grays_warm'] and keys[0] not in config:
        # Add 'palettes' prefix for legacy compatibility
        keys = ['palettes'] + keys
    
    try:
        for key in keys:
            current = current[key]
    except (KeyError, TypeError):
        raise KeyError(f"Color path not found: {color_path}")
    
    # If current is a reference object with palette and tone, resolve it
    if isinstance(current, dict) and 'palette' in current and 'tone' in current:
        palette_name = current['palette']
        tone_name = current['tone']
        
        # Look up the actual color value
        try:
            if palette_name in config.get('palettes', {}):
                palette = config['palettes'][palette_name]
                if tone_name in palette:
                    resolved_color = palette[tone_name]
                    return _convert_color_format(resolved_color, 'rgb', format_type)
            
            # If not found in palettes, check if it's a direct reference
            raise KeyError(f"Palette '{palette_name}' or tone '{tone_name}' not found")
            
        except KeyError:
            raise KeyError(f"Cannot resolve color reference: palette='{palette_name}', tone='{tone_name}'")
    
    # If current is a dict with color formats, extract the requested format
    if isinstance(current, dict):
        if format_type in current:
            return current[format_type]
        elif 'hex' in current and format_type == 'hex':
            return current['hex']
        elif 'rgb' in current and format_type == 'rgb':
            return current['rgb']
        elif 'hsl' in current and format_type == 'hsl':
            return current['hsl']
        else:
            # Try to find any color format and convert
            if 'hex' in current:
                return _convert_color_format(current['hex'], 'hex', format_type)
            elif 'rgb' in current:
                return _convert_color_format(current['rgb'], 'rgb', format_type)
    
    # If current is a direct color value, try to convert
    if isinstance(current, (str, list)):
        # Assume it's in hex format if string, rgb if list
        source_format = 'hex' if isinstance(current, str) else 'rgb'
        return _convert_color_format(current, source_format, format_type)
    
    raise ValueError(f"Cannot extract {format_type} format from color at path: {color_path}")


def _convert_color_format(color_value: Any, from_format: str, to_format: str) -> Any:
    """Convert color between formats.
    
    Args:
        color_value: Color value in source format
        from_format: Source format ('hex', 'rgb', 'hsl')
        to_format: Target format ('hex', 'rgb', 'hsl')
        
    Returns:
        Color value in target format
    """
    if from_format == to_format:
        return color_value
    
    # Simple conversions for common cases
    if from_format == 'hex' and to_format == 'rgb':
        # Convert hex to RGB
        if isinstance(color_value, str):
            hex_color = color_value.lstrip('#')
            if len(hex_color) == 6:
                return [
                    int(hex_color[0:2], 16),
                    int(hex_color[2:4], 16),
                    int(hex_color[4:6], 16)
                ]
    
    elif from_format == 'rgb' and to_format == 'hex':
        # Convert RGB to hex
        if isinstance(color_value, list) and len(color_value) == 3:
            return f"#{color_value[0]:02x}{color_value[1]:02x}{color_value[2]:02x}"
    
    # For unsupported conversions, return as-is
    return color_value
