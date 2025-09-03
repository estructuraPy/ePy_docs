
"""Color management utilities for styling and visualization.

CENTRALIZED COLOR CONFIGURATION ACCESS.
ALL color-related functionality must go through this module.
NO direct access to colors.json from any other file.
Uses _load_cached_files for centralized caching.
"""

from typing import Dict, Any, Union, List, Optional, Tuple
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

class ConfigurationError(Exception):
    """Configuration not found or invalid."""
    pass

class TableColorConfig(BaseModel):
    """Configuration for table coloring."""
    palette: str = Field(default="viridis")
    header_color: str = Field(...)
    alpha: float = Field(default=0.7, ge=0.0, le=1.0)
    reverse: bool = Field(default=False)
    
    class Config:
        use_enum_values = True

# ============================================================================
# CENTRALIZED COLOR CONFIGURATION LOADING
# All access to colors.json MUST go through these functions
# ============================================================================

def load_colors_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load colors configuration from colors.json using centralized cache.
    
    This is the ONLY function that should access colors.json.
    All other functions must use this function.
    
    Args:
        sync_files: Whether to use synchronized configuration files
        
    Returns:
        Complete colors configuration dictionary
        
    Raises:
        ConfigurationError: If colors configuration cannot be loaded
    """
    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
    try:
        config_path = _resolve_config_path('colors', sync_files)
        return _load_cached_files(config_path, sync_files)
    except Exception as e:
        raise ConfigurationError(f"Failed to load colors configuration: {e}")

# ============================================================================
# BASIC COLOR ACCESS FUNCTIONS
# ============================================================================

def get_color_value(path: str, format_type: str = "rgb", sync_files: bool = False) -> Union[List[int], str]:
    """Get color value using dot notation.
    
    Args:
        path: Dot notation path to color (e.g., 'brand.brand_primary')
        format_type: Output format 'rgb' or 'hex'
        sync_files: Whether to use synchronized configuration files
        
    Returns:
        Color value in specified format
        
    Raises:
        ConfigurationError: If color path not found
    """
    colors_config = load_colors_config(sync_files)
    
    keys = path.split('.')
    color_value = colors_config
    try:
        for key in keys:
            color_value = color_value[key]
    except KeyError:
        raise ConfigurationError(f"Color path '{path}' not found in colors configuration")
    
    return _convert_color_format(color_value, format_type)

def get_color(path: str, format_type: str = "rgb", sync_files: bool = False) -> Union[List[int], str]:
    """Alias for get_color_value for backward compatibility."""
    return get_color_value(path, format_type, sync_files)

def _convert_color_format(color_value: Any, format_type: str) -> Union[List[int], str]:
    """Convert color value to specified format."""
    if isinstance(color_value, list) and len(color_value) >= 3:
        r, g, b = color_value[:3]
        return f"#{r:02x}{g:02x}{b:02x}" if format_type.lower() == "hex" else [r, g, b]
        
    elif isinstance(color_value, str):
        if color_value.startswith('#'):
            if format_type.lower() == "hex":
                return color_value
            # Convert hex to RGB
            hex_color = color_value.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c+c for c in hex_color)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)  
            b = int(hex_color[4:6], 16)
            return [r, g, b]
        else:
            return color_value
    
    return color_value

# ============================================================================
# BRAND AND GENERAL COLORS
# ============================================================================

def get_brand_color(color_name: str, format_type: str = "rgb", sync_files: bool = False) -> Union[List[int], str]:
    """Get brand color by name."""
    return get_color_value(f"brand.{color_name}", format_type, sync_files)

def get_general_color(color_name: str, format_type: str = "rgb", sync_files: bool = False) -> Union[List[int], str]:
    """Get general color by name."""
    return get_color_value(f"general.{color_name}", format_type, sync_files)

def get_all_brand_colors(format_type: str = "rgb", sync_files: bool = False) -> Dict[str, Union[List[int], str]]:
    """Get all brand colors."""
    colors_config = load_colors_config(sync_files)
    brand_colors = {}
    
    if 'brand' in colors_config:
        for color_name, color_value in colors_config['brand'].items():
            brand_colors[color_name] = _convert_color_format(color_value, format_type)
    
    return brand_colors

def get_all_general_colors(format_type: str = "rgb", sync_files: bool = False) -> Dict[str, Union[List[int], str]]:
    """Get all general colors."""
    colors_config = load_colors_config(sync_files)
    general_colors = {}
    
    if 'general' in colors_config:
        for color_name, color_value in colors_config['general'].items():
            general_colors[color_name] = _convert_color_format(color_value, format_type)
    
    return general_colors

# ============================================================================
# LAYOUT STYLE COLORS
# ============================================================================

def get_layout_color(layout_name: str, category: str, element: str, format_type: str = "rgb", sync_files: bool = False) -> Union[List[int], str]:
    """Get layout-specific color."""
    return get_color_value(f"layout_styles.{layout_name}.{category}.{element}", format_type, sync_files)

def get_layout_typography_colors(layout_name: str, format_type: str = "rgb", sync_files: bool = False) -> Dict[str, Union[List[int], str]]:
    """Get all typography colors for a layout."""
    colors_config = load_colors_config(sync_files)
    
    try:
        typography_colors = colors_config['layout_styles'][layout_name]['typography']
        result = {}
        for element, color_value in typography_colors.items():
            result[element] = _convert_color_format(color_value, format_type)
        return result
    except KeyError:
        raise ConfigurationError(f"Typography colors not found for layout '{layout_name}'")

def get_layout_callout_colors(layout_name: str, callout_type: str, format_type: str = "rgb", sync_files: bool = False) -> Dict[str, Union[List[int], str]]:
    """Get callout colors for a layout."""
    colors_config = load_colors_config(sync_files)
    
    try:
        callout_colors = colors_config['layout_styles'][layout_name]['callouts'][callout_type]
        result = {}
        for element, color_value in callout_colors.items():
            result[element] = _convert_color_format(color_value, format_type)
        return result
    except KeyError:
        raise ConfigurationError(f"Callout '{callout_type}' colors not found for layout '{layout_name}'")

def get_all_layout_callout_colors(layout_name: str, format_type: str = "rgb", sync_files: bool = False) -> Dict[str, Dict[str, Union[List[int], str]]]:
    """Get all callout colors for a layout."""
    colors_config = load_colors_config(sync_files)
    
    try:
        callouts_config = colors_config['layout_styles'][layout_name]['callouts']
        result = {}
        for callout_type, callout_colors in callouts_config.items():
            result[callout_type] = {}
            for element, color_value in callout_colors.items():
                result[callout_type][element] = _convert_color_format(color_value, format_type)
        return result
    except KeyError:
        raise ConfigurationError(f"Callout colors not found for layout '{layout_name}'")

# ============================================================================
# VISUALIZATION COLORS
# ============================================================================

def get_visualization_colors(category: str, sync_files: bool = False) -> Dict[str, str]:
    """Get visualization colors for a category."""
    colors_config = load_colors_config(sync_files)
    
    if 'visualization' not in colors_config or category not in colors_config['visualization']:
        raise ConfigurationError(f"Visualization category '{category}' not found")
    
    category_data = colors_config['visualization'][category]
    colors_dict = {}
    
    if isinstance(category_data, list):
        # Handle list of RGB values (like categorical_colors)
        for i, color_value in enumerate(category_data):
            if isinstance(color_value, list) and len(color_value) >= 3:
                r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
                colors_dict[f"color_{i+1}"] = f"#{r:02x}{g:02x}{b:02x}"
            else:
                colors_dict[f"color_{i+1}"] = str(color_value)
                
    elif isinstance(category_data, dict):
        # Handle dictionary structure
        for key, value in category_data.items():
            if isinstance(value, str):
                if value.startswith('#'):
                    colors_dict[key] = value
                elif '.' in value:
                    # Resolve color reference
                    colors_dict[key] = get_color_value(value, "hex", sync_files)
                else:
                    colors_dict[key] = value
            elif isinstance(value, list) and len(value) >= 3:
                r, g, b = int(value[0]), int(value[1]), int(value[2])
                colors_dict[key] = f"#{r:02x}{g:02x}{b:02x}"
            elif isinstance(value, dict):
                # Handle nested dictionaries (like palettes)
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list) and len(subvalue) >= 3:
                        r, g, b = int(subvalue[0]), int(subvalue[1]), int(subvalue[2])
                        colors_dict[f"{key}_{subkey}"] = f"#{r:02x}{g:02x}{b:02x}"
                    else:
                        colors_dict[f"{key}_{subkey}"] = str(subvalue)
            else:
                colors_dict[key] = str(value)
    else:
        raise ConfigurationError(f"Invalid category structure for {category}: {type(category_data)}")
    
    return colors_dict

def get_categorical_colors(n_colors: Optional[int] = None, sync_files: bool = False) -> List[str]:
    """Get categorical colors as hex strings."""
    colors_config = load_colors_config(sync_files)
    
    try:
        categorical_colors = colors_config['visualization']['categorical_colors']
        hex_colors = []
        for color_value in categorical_colors:
            if isinstance(color_value, list) and len(color_value) >= 3:
                r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
                hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
            else:
                hex_colors.append(str(color_value))
        
        if n_colors is not None:
            # Cycle colors if we need more than available
            while len(hex_colors) < n_colors:
                hex_colors.extend(hex_colors)
            return hex_colors[:n_colors]
        
        return hex_colors
    except KeyError:
        raise ConfigurationError("Categorical colors not found in visualization configuration")

# ============================================================================
# TABLE COLORS AND PALETTES
# ============================================================================

def get_table_palette_colors(palette_name: str, sync_files: bool = False) -> Dict[str, List[int]]:
    """Get table palette colors."""
    colors_config = load_colors_config(sync_files)
    
    try:
        palette = colors_config['visualization']['table_palettes'][palette_name]
        return palette
    except KeyError:
        raise ConfigurationError(f"Table palette '{palette_name}' not found")

def get_available_table_palettes(sync_files: bool = False) -> List[str]:
    """Get list of available table palettes."""
    colors_config = load_colors_config(sync_files)
    
    try:
        return list(colors_config['visualization']['table_palettes'].keys())
    except KeyError:
        raise ConfigurationError("Table palettes not found in configuration")

# ============================================================================
# COLORMAP FUNCTIONS
# ============================================================================

def get_custom_colormap(palette_name: str, n_colors: int = 256, reverse: bool = False):
    """Get matplotlib or custom colormap function."""
    # Try matplotlib first
    if hasattr(plt.cm, palette_name):
        cmap = getattr(plt.cm, palette_name)
        if reverse:
            cmap = cmap.reversed()
        
        def matplotlib_colormap_func(value: float) -> tuple:
            if not 0 <= value <= 1:
                raise ValueError(f"Value must be between 0 and 1: {value}")
            return cmap(value)
        
        return matplotlib_colormap_func
    
    # Use custom palette
    try:
        palette_colors = get_table_palette_colors(palette_name, sync_files=False)
        
        if not isinstance(palette_colors, dict):
            raise ConfigurationError(f"Palette '{palette_name}' is not valid")
        
        # Convert to RGB tuples
        sorted_keys = sorted(palette_colors.keys())
        if reverse:
            sorted_keys = sorted_keys[::-1]
            
        colors = []
        for key in sorted_keys:
            color_value = palette_colors[key]
            if isinstance(color_value, list) and len(color_value) >= 3:
                r, g, b = color_value[0]/255.0, color_value[1]/255.0, color_value[2]/255.0
                colors.append((r, g, b, 1.0))
            else:
                raise ConfigurationError(f"Invalid color format in palette '{palette_name}': {color_value}")
        
        if not colors:
            raise ConfigurationError(f"No colors found in palette '{palette_name}'")
        
        def custom_colormap_func(value: float) -> tuple:
            if not 0 <= value <= 1:
                raise ValueError(f"Value must be between 0 and 1: {value}")
            
            if value == 1.0:
                return colors[-1]
            elif value == 0.0:
                return colors[0]
            else:
                # Linear interpolation
                scaled_value = value * (len(colors) - 1)
                lower_idx = int(scaled_value)
                upper_idx = min(lower_idx + 1, len(colors) - 1)
                weight = scaled_value - lower_idx
                
                lower_color = colors[lower_idx]
                upper_color = colors[upper_idx]
                
                return tuple(
                    lower_color[i] * (1 - weight) + upper_color[i] * weight
                    for i in range(4)
                )
        
        return custom_colormap_func
        
    except ConfigurationError:
        raise ConfigurationError(f"Invalid colormap/palette: '{palette_name}'")

# ============================================================================
# COLOR UTILITY FUNCTIONS
# ============================================================================

def rgb_to_latex_str(rgb_list: List[int]) -> str:
    """Convert RGB list to LaTeX color format."""
    return f"{rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]}"

def rgb_to_hex(rgb_list: List[int]) -> str:
    """Convert RGB list to hex string."""
    r, g, b = rgb_list[:3]
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgb(hex_color: str) -> List[int]:
    """Convert hex string to RGB list."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c+c for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)  
    b = int(hex_color[4:6], 16)
    return [r, g, b]

def is_dark_color(rgb_color: List[int]) -> bool:
    """Determine if a color is dark based on luminance."""
    luminance = (0.299 * rgb_color[0] + 0.587 * rgb_color[1] + 0.114 * rgb_color[2]) / 255
    return luminance < 0.5

def get_contrasting_text_color(background_rgb: List[int], format_type: str = "rgb") -> Union[List[int], str]:
    """Get contrasting text color (white/black) for given background."""
    text_rgb = [240, 240, 240] if is_dark_color(background_rgb) else [40, 40, 40]
    
    if format_type.lower() == "hex":
        return rgb_to_hex(text_rgb)
    return text_rgb

def normalize_color_value(color_value: Any) -> str:
    """Normalize any color value to hex string."""
    if isinstance(color_value, str):
        if color_value.startswith('#'):
            return color_value
        elif '.' in color_value:
            return get_color_value(color_value, "hex", sync_files=False)
        else:
            return color_value
    elif isinstance(color_value, list) and len(color_value) >= 3:
        try:
            r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
            if not all(0 <= c <= 255 for c in [r, g, b]):
                raise ConfigurationError(f"RGB values must be 0-255: {color_value}")
            return rgb_to_hex([r, g, b])
        except (TypeError, ValueError, IndexError):
            raise ConfigurationError(f"Invalid RGB color format: {color_value}")
    else:
        raise ConfigurationError(f"Invalid color format: {color_value}")

# ============================================================================
# LEGACY/DEPRECATED FUNCTIONS (for backward compatibility)
# ============================================================================

def load_colors() -> Dict[str, Any]:
    """⚠️ DEPRECATED: Use load_colors_config() instead."""
    return load_colors_config(sync_files=False)

def get_report_color(category: str, variant: str, format_type: str = "rgb", sync_files: bool = False) -> Union[List[int], str]:
    """⚠️ DEPRECATED: Use get_color_value() with proper path instead."""
    return get_color_value(f"reports.{category}.{variant}", format_type, sync_files)

def get_category_colors(category: str, sync_files: bool = False) -> Dict[str, str]:
    """⚠️ DEPRECATED: Use get_visualization_colors() instead."""
    return get_visualization_colors(category, sync_files)

# ============================================================================
# ALL COLOR ACCESS MUST GO THROUGH THIS MODULE
# NO DIRECT ACCESS TO colors.json FROM OTHER FILES
# ============================================================================

