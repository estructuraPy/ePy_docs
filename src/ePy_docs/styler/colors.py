"""Color management utilities for styling and visualization.

Provides color configuration, palette management, and matplotlib integration
with centralized configuration loading from JSON files.
"""

from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field
from enum import Enum

import matplotlib.pyplot as plt
import matplotlib.colors
from reportlab.lib import colors

from ePy_files.styler.setup import get_colors_config, get_color as _get_color, ConfigurationError


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
    """Configuration for table coloring.
    
    Defines color palette, header color, and other styling options
    for table visualization.
    
    Assumptions:
        Palette names correspond to valid matplotlib colormaps.
        Header color is a valid color reference or hex code.
    """
    palette: Union[TableColorPalette, str] = Field(default=TableColorPalette.VIRIDIS)
    header_color: Optional[str] = Field(default=None)
    alpha: float = Field(default=0.7, ge=0.0, le=1.0)
    reverse: bool = Field(default=False)
    
    class Config:
        use_enum_values = True


def _load_cached_colors() -> Dict[str, Any]:
    """Load colors.json with caching.
    
    Returns:
        Dict[str, Any]: Complete colors configuration dictionary.
        
    Assumptions:
        colors.json exists and contains valid configuration.
        Cache is properly initialized.
    """
    return get_colors_config(sync_json=False)


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
    try:
        return _get_color(path, format_type, sync_json)
    except ConfigurationError:
        # Raise the error - no fallbacks for missing colors
        raise ConfigurationError(f"Required color '{path}' not found in configuration")


def get_report_color(category: str, variant: str = 'default', format_type: str = "rgb", sync_json: bool = True) -> Union[List[int], str]:
    """Get a report color for specific category and variant.
    
    Args:
        category: Color category (e.g., 'note', 'warning', 'error')
        variant: Color variant within category
        format_type: Format type to return - "rgb" for RGB list or "hex" for hex string
        sync_json: Whether to reload from disk or use cache
        
    Returns:
        Color value as RGB list [r, g, b] or hex string '#RRGGBB' based on format_type
    """
    path = f"reports.{category}.{variant}"
    return get_color(path, format_type, sync_json)


def _resolve_color_reference(colors_data: Dict[str, Any], color_value: Any, default: str = '#3498db', max_depth: int = 5) -> str:
    """Recursively resolve color references to actual color values.
    
    Args:
        colors_data: Color configuration dictionary.
        color_value: Color reference, hex code, or RGB list.
        default: Default color to return if resolution fails.
        max_depth: Maximum recursion depth for resolving references.
        
    Returns:
        str: Resolved hex color code.
        
    Assumptions:
        Color references use dot notation (e.g., 'brand.primary').
        RGB lists contain three integer values [0-255].
    """
    if not color_value or max_depth <= 0:
        return default
    
    # If it's already a hex color, return it
    if isinstance(color_value, str) and color_value.startswith('#'):
        return color_value
        
    # If it's an RGB list, convert to hex
    if isinstance(color_value, list) and len(color_value) >= 3:
        try:
            r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
            return f"#{r:02x}{g:02x}{b:02x}"
        except (TypeError, ValueError, IndexError):
            return default

    # If it's a color reference, resolve it
    if isinstance(color_value, str) and '.' in color_value:
        try:
            resolved = _get_color(color_value, None, sync_json=False)
            return _resolve_color_reference(colors_data, resolved, default, max_depth - 1)
        except ConfigurationError:
            return default
    
    # Return as-is for named colors
    return color_value if isinstance(color_value, str) else default


def get_custom_colormap(palette_name: str, n_colors: int = 256, reverse: bool = False):
    """Get a matplotlib colormap function for the specified palette.
    
    Args:
        palette_name: Name of the color palette from matplotlib.
        n_colors: Number of colors in the map.
        reverse: Whether to reverse the palette direction.
        
    Returns:
        callable: Function that maps values [0,1] to RGB tuples.
        
    Assumptions:
        palette_name is a valid matplotlib colormap name.
        Fallback to viridis or a simple blue-red gradient if name invalid.
    """
    try:
        # Try to get matplotlib colormap
        if hasattr(plt.cm, palette_name):
            cmap = getattr(plt.cm, palette_name)
        else:
            # Fallback to viridis if palette not found
            cmap = plt.cm.viridis
        
        if reverse:
            cmap = cmap.reversed()
        
        def colormap_func(value: float) -> tuple:
            """Map a value [0,1] to RGBA tuple."""
            if value < 0:
                value = 0
            elif value > 1:
                value = 1
            return cmap(value)
        
        return colormap_func
        
    except Exception:
        # Fallback colormap function
        def fallback_colormap(value: float) -> tuple:
            """Simple fallback colormap from blue to red."""
            if value < 0:
                value = 0
            elif value > 1:
                value = 1
            return (value, 0, 1-value, 0.7)
        
        return fallback_colormap


def convert_to_reportlab_color(color_str: str, alpha: float = 1.0):
    """Convert color string to ReportLab Color object.
    
    Args:
        color_str: Color as hex string or named color.
        alpha: Alpha transparency value (0.0-1.0).
        
    Returns:
        colors.Color: ReportLab Color object for PDF generation.
        
    Assumptions:
        color_str is a valid hex code or a named color in reportlab.lib.colors.
        Alpha value is between 0.0 and 1.0.
    """
    try:
        if color_str.startswith('#'):
            # Convert hex to RGB
            hex_color = color_str.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return colors.Color(r, g, b, alpha)
        
        # Try named color
        return getattr(colors, color_str.lower(), colors.black)
    except Exception:
        return colors.black


def _get_category_colors(category: str, sync_json: bool = True) -> Dict[str, str]:
    """Get colors for a specific category from configuration.
    
    Args:
        category: Category name (e.g., 'nodes', 'elements')
        sync_json: Whether to reload from disk or use cache
        
    Returns:
        Dictionary mapping value names to color strings
    """
    try:
        # Try visualization category first
        path = f"visualization.{category}"
        colors_dict = {}
        colors_config = get_colors_config(sync_json)
        
        # Navigate to the category
        current = colors_config
        for key in path.split('.'):
            if key in current:
                current = current[key]
            else:
                return {}
        
        # Convert to color strings
        for key, value in current.items():
            if isinstance(value, str):
                colors_dict[key] = value
            elif isinstance(value, list) and len(value) >= 3:
                r, g, b = int(value[0]), int(value[1]), int(value[2])
                colors_dict[key] = f"#{r:02x}{g:02x}{b:02x}"
        
        return colors_dict
        
    except Exception:
        return {}


# Convenience functions for common color operations
def _normalize_color_value(color_value: Any) -> str:
    """Normalize color value to hex string."""
    if isinstance(color_value, str):
        return color_value
    elif isinstance(color_value, list) and len(color_value) >= 3:
        try:
            r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
            return f"#{r:02x}{g:02x}{b:02x}"
        except (TypeError, ValueError, IndexError):
            return '#000000'
    else:
        return '#000000'


def load_colors() -> Dict[str, Any]:
    """Load colors configuration from colors.json
    
    Returns:
        Dictionary containing colors configuration
    """
    return get_colors_config(sync_json=True)
