
"""Color management utilities for styling and visualization.

Provides color configuration, palette management, and matplotlib integration
with centralized configuration loading from JSON files.
"""

from typing import Dict, Any, Union, List
from pydantic import BaseModel, Field
from enum import Enum

import matplotlib.pyplot as plt

from ePy_docs.components.page import get_colors_config, get_color as _get_color, ConfigurationError


# Enums for predefined palettes
class TableColorPalette(Enum):
    """Predefined color palettes for table visualization."""
    VIRIDIS = "viridis"
    PLASMA = "plasma" 
    INFERNO = "inferno"
    MAGMA = "magma"
    COOLWARM = "coolwarm"
    SPECTRAL = "spectral"
    RDYLBU = "RdYlBu"
    RDYLGN = "RdYlGn"
    RDBU = "RdBu"
    BLUES = "Blues"
    REDS = "Reds"
    GREENS = "Greens"
    ORANGES = "Oranges"
    PURPLES = "Purples"
    GREYS = "Greys"
    YLORBR = "YlOrBr"
    YLORRD = "YlOrRd"
    ORRD = "OrRd"
    PUBU = "PuBu"
    BUPU = "BuPu"


class TableColorConfig(BaseModel):
    """Configuration for table coloring."""
    palette: Union[TableColorPalette, str] = Field(default=TableColorPalette.VIRIDIS)
    header_color: str = Field(...)
    alpha: float = Field(default=0.7, ge=0.0, le=1.0)
    reverse: bool = Field(default=False)
    
    class Config:
        use_enum_values = True


def _load_cached_colors() -> Dict[str, Any]:
    """Load colors.json with caching using unified configuration system.
    
    Returns:
        Dict[str, Any]: Complete colors configuration dictionary.
    """
    from ePy_docs.core.setup import _load_cached_config
    return _load_cached_config('colors')

def rgb_to_latex_str(rgb_list: list) -> str:
    """Convert RGB list to string format for LaTeX color definitions.
    Args:
        rgb_list: RGB color as [r, g, b] list where each value is an integer 0-255.
    Returns:
        str: String in the format "r, g, b" for LaTeX color definitions.
    """
    return f"{rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]}"


def is_dark_color(rgb_color: List[int]) -> bool:
    """Determine if a color is dark based on its luminance.
    
    Args:
        rgb_color: RGB color as [r, g, b] list where each value is 0-255
        
    Returns:
        bool: True if the color is dark, False if light
    """
    # Calculate luminance using the formula: 0.299*R + 0.587*G + 0.114*B
    luminance = (0.299 * rgb_color[0] + 0.587 * rgb_color[1] + 0.114 * rgb_color[2]) / 255
    return luminance < 0.5  # Threshold of 0.5 for dark/light


def get_contrasting_text_color(background_rgb: List[int], format_type: str = "rgb") -> Union[List[int], str]:
    """Get appropriate text color (black or white) based on background color.
    
    Args:
        background_rgb: Background color as [r, g, b] list
        format_type: Format type to return - "rgb" for RGB list or "hex" for hex string
        
    Returns:
        Contrasting color - white for dark backgrounds, black for light backgrounds
    """
    if is_dark_color(background_rgb):
        # Dark background - use light text
        text_rgb = [240, 240, 240]  # Light gray
    else:
        # Light background - use dark text
        text_rgb = [40, 40, 40]  # Dark gray (not pure black for better readability)
    
    if format_type.lower() == "hex":
        return f"#{text_rgb[0]:02x}{text_rgb[1]:02x}{text_rgb[2]:02x}"
    return text_rgb


def get_color(path: str, format_type: str = "rgb", sync_files: bool = True) -> Union[List[int], str]:
    """Get a color value from colors configuration using dot notation.
    
    Args:
        path: Dot-separated path to the color value (e.g., 'reports.tables.header.default')
        format_type: Format type to return - "rgb" for RGB list or "hex" for hex string
        sync_files: Whether to reload from disk or use cache
        
    Returns:
        Color value as RGB list [r, g, b] or hex string '#RRGGBB' based on format_type
        
    Raises:
        ConfigurationError: If path not found or if color format is invalid
    """
    return _get_color(path, format_type, sync_files)


def get_report_color(category: str, variant: str, format_type: str = "rgb") -> Union[List[int], str]:
    """Get a report color for specific category and variant.
    
    Args:
        category: Color category
        variant: Color variant within category
        format_type: Format type to return - "rgb" for RGB list or "hex" for hex string
        
    Returns:
        Color value as RGB list [r, g, b] or hex string '#RRGGBB' based on format_type
    """
    path = f"reports.{category}.{variant}"
    return get_color(path, format_type)


# def _resolve_color_reference(color_value: Any, max_depth: int = 5) -> str:
#     """Recursively resolve color references to actual color values.
    
#     Args:
#         color_value: Color reference, hex code, or RGB list.
#         max_depth: Maximum recursion depth for resolving references.
        
#     Returns:
#         str: Resolved hex color code.
        
#     Raises:
#         ConfigurationError: If color cannot be resolved or format is invalid
#     """
#     if max_depth <= 0:
#         raise ConfigurationError("Maximum recursion depth reached resolving color reference")
    
#     if not color_value:
#         raise ConfigurationError("Empty color value provided")
    
#     # If it's already a hex color, return it
#     if isinstance(color_value, str) and color_value.startswith('#'):
#         return color_value
        
#     # If it's an RGB list, convert to hex
#     if isinstance(color_value, list) and len(color_value) >= 3:
#         try:
#             r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
#             if not all(0 <= c <= 255 for c in [r, g, b]):
#                 raise ConfigurationError(f"RGB values must be 0-255: {color_value}")
#             return f"#{r:02x}{g:02x}{b:02x}"
#         except (TypeError, ValueError, IndexError):
#             raise ConfigurationError(f"Invalid RGB color format: {color_value}")

#     # If it's a color reference, resolve it
#     if isinstance(color_value, str) and '.' in color_value:
#         resolved = _get_color(color_value, "hex", sync_files=False)
#         return _resolve_color_reference(resolved, max_depth - 1)
    
#     # If it's a named color string, return as-is
#     if isinstance(color_value, str):
#         return color_value
    
#     raise ConfigurationError(f"Invalid color format: {color_value}")


def get_custom_colormap(palette_name: str, n_colors: int = 256, reverse: bool = False):
    """Get a matplotlib colormap function for the specified palette.
    
    Args:
        palette_name: Name of the color palette from matplotlib or custom palette from config.
        n_colors: Number of colors in the map.
        reverse: Whether to reverse the palette direction.
        
    Returns:
        callable: Function that maps values [0,1] to RGB tuples.
        
    Raises:
        ConfigurationError: If palette name is invalid
    """
    # First, check if it's a matplotlib colormap
    if hasattr(plt.cm, palette_name):
        cmap = getattr(plt.cm, palette_name)
        
        if reverse:
            cmap = cmap.reversed()
        
        def matplotlib_colormap_func(value: float) -> tuple:
            """Map a value [0,1] to RGBA tuple."""
            if not 0 <= value <= 1:
                raise ValueError(f"Value must be between 0 and 1: {value}")
            return cmap(value)
        
        return matplotlib_colormap_func
    
    # If not matplotlib, check if it's a custom palette from configuration
    try:
        from ePy_docs.core.setup import _load_cached_config
        colors_config = _load_cached_config('colors')
        palette_path = f"reports.tables.palettes.{palette_name}"
        
        # Navigate to the palette
        current = colors_config
        for key in palette_path.split('.'):
            if key not in current:
                raise KeyError(f"Key '{key}' not found")
            current = current[key]
        
        # Extract color values and convert to RGB tuples
        if isinstance(current, dict):
            # Sort keys to ensure consistent order (light to dark or vice versa)
            sorted_keys = sorted(current.keys())
            if reverse:
                sorted_keys = sorted_keys[::-1]
                
            colors = []
            for key in sorted_keys:
                color_value = current[key]
                if isinstance(color_value, list) and len(color_value) >= 3:
                    # Normalize RGB values to [0,1]
                    r, g, b = color_value[0]/255.0, color_value[1]/255.0, color_value[2]/255.0
                    colors.append((r, g, b, 1.0))  # Add alpha=1.0
                else:
                    raise ConfigurationError(f"Invalid color format in palette '{palette_name}': {color_value}")
            
            if not colors:
                raise ConfigurationError(f"No colors found in palette '{palette_name}'")
            
            def custom_colormap_func(value: float) -> tuple:
                """Map a value [0,1] to RGBA tuple using custom palette."""
                if not 0 <= value <= 1:
                    raise ValueError(f"Value must be between 0 and 1: {value}")
                
                # Map value to color index
                if value == 1.0:
                    return colors[-1]
                elif value == 0.0:
                    return colors[0]
                else:
                    # Linear interpolation between colors
                    scaled_value = value * (len(colors) - 1)
                    lower_idx = int(scaled_value)
                    upper_idx = min(lower_idx + 1, len(colors) - 1)
                    weight = scaled_value - lower_idx
                    
                    lower_color = colors[lower_idx]
                    upper_color = colors[upper_idx]
                    
                    # Interpolate RGBA values
                    interpolated = tuple(
                        lower_color[i] * (1 - weight) + upper_color[i] * weight
                        for i in range(4)
                    )
                    return interpolated
            
            return custom_colormap_func
        else:
            raise ConfigurationError(f"Palette '{palette_name}' is not a valid palette structure")
            
    except (KeyError, TypeError):
        # Neither matplotlib nor custom palette found
        raise ConfigurationError(f"Invalid colormap/palette: '{palette_name}'. Not found in matplotlib or custom palettes.")


# def convert_to_reportlab_color(color_str: str, alpha: float = 1.0):
#     """Convert color string to ReportLab Color object.
    
#     Args:
#         color_str: Color as hex string.
#         alpha: Alpha transparency value (0.0-1.0).
        
#     Returns:
#         RGB tuple: (r, g, b, alpha) values normalized to 0.0-1.0
        
#     Raises:
#         ConfigurationError: If color format is invalid or alpha out of range
#     """
#     if not 0.0 <= alpha <= 1.0:
#         raise ConfigurationError(f"Alpha must be between 0.0 and 1.0: {alpha}")
        
#     if not color_str.startswith('#'):
#         raise ConfigurationError(f"Color must be hex format starting with #: {color_str}")
    
#     hex_color = color_str.lstrip('#')
#     if len(hex_color) == 3:
#         hex_color = ''.join(c+c for c in hex_color)
#     elif len(hex_color) != 6:
#         raise ConfigurationError(f"Invalid hex color length: {color_str}")
    
#     try:
#         r = int(hex_color[0:2], 16) / 255.0
#         g = int(hex_color[2:4], 16) / 255.0
#         b = int(hex_color[4:6], 16) / 255.0
#         return (r, g, b, alpha)
#     except ValueError:
#         raise ConfigurationError(f"Invalid hex color format: {color_str}")


def get_category_colors(category: str, sync_files: bool = True) -> Dict[str, str]:
    """Get colors for a specific category from configuration.
    
    Args:
        category: Category name (e.g., 'nodes', 'elements') 
        sync_files: Whether to reload from disk or use cache
        
    Returns:
        Dictionary mapping value names to color strings
        
    Raises:
        ConfigurationError: If category not found in configuration
    """
    path = f"visualization.{category}"
    from ePy_docs.core.setup import _load_cached_config
    colors_config = _load_cached_config('colors')
    
    # Navigate to the category
    current = colors_config
    for key in path.split('.'):
        if key not in current:
            raise ConfigurationError(f"Category '{category}' not found in visualization configuration")
        current = current[key]
    
    # Convert to color strings
    colors_dict = {}
    for key, value in current.items():
        if isinstance(value, str):
            # Handle color references
            if '.' in value:
                colors_dict[key] = get_color(value, "hex", sync_files)
            else:
                colors_dict[key] = value
        elif isinstance(value, list) and len(value) >= 3:
            r, g, b = int(value[0]), int(value[1]), int(value[2])
            colors_dict[key] = f"#{r:02x}{g:02x}{b:02x}"
        else:
            raise ConfigurationError(f"Invalid color format for {category}.{key}: {value}")
    
    return colors_dict


def normalize_color_value(color_value: Any) -> str:
    """Normalize color value to hex string.
    
    Args:
        color_value: Color as string, list, or other format
        
    Returns:
        Hex color string
        
    Raises:
        ConfigurationError: If color format is invalid
    """
    if isinstance(color_value, str):
        if color_value.startswith('#'):
            return color_value
        # Handle color references
        elif '.' in color_value:
            return get_color(color_value, "hex", sync_files=False)
        else:
            return color_value
    elif isinstance(color_value, list) and len(color_value) >= 3:
        try:
            r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
            if not all(0 <= c <= 255 for c in [r, g, b]):
                raise ConfigurationError(f"RGB values must be 0-255: {color_value}")
            return f"#{r:02x}{g:02x}{b:02x}"
        except (TypeError, ValueError, IndexError):
            raise ConfigurationError(f"Invalid RGB color format: {color_value}")
    else:
        raise ConfigurationError(f"Invalid color format: {color_value}")


def load_colors() -> Dict[str, Any]:
    """Load colors configuration from colors.json using unified configuration system
    
    Returns:
        Dictionary containing colors configuration
    """
    from ePy_docs.core.setup import _load_cached_config
    return _load_cached_config('colors')


