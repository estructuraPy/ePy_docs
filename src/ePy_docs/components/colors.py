
"""Color management utilities for styling and visualization."""

from typing import Dict, Any, Union, List
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt
from ePy_docs.core.setup import get_color as _get_color


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


def load_colors() -> Dict[str, Any]:
    """Load colors configuration from colors.json."""
    from ePy_docs.core.setup import _load_cached_config
    return _load_cached_config('colors')


def rgb_to_latex_str(rgb_list: List[int]) -> str:
    """Convert RGB list to LaTeX color format."""
    return f"{rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]}"


def is_dark_color(rgb_color: List[int]) -> bool:
    """Determine if a color is dark based on luminance."""
    luminance = (0.299 * rgb_color[0] + 0.587 * rgb_color[1] + 0.114 * rgb_color[2]) / 255
    return luminance < 0.5


def get_contrasting_text_color(background_rgb: List[int], format_type: str = "rgb") -> Union[List[int], str]:
    """Get contrasting text color (white/black) for given background."""
    text_rgb = [240, 240, 240] if is_dark_color(background_rgb) else [40, 40, 40]
    
    if format_type.lower() == "hex":
        return f"#{text_rgb[0]:02x}{text_rgb[1]:02x}{text_rgb[2]:02x}"
    return text_rgb


def get_color(path: str, format_type: str = "rgb", sync_files: bool = True) -> Union[List[int], str]:
    """Get color value using dot notation path."""
    return _get_color(path, format_type, sync_files)


def get_report_color(category: str, variant: str, format_type: str = "rgb") -> Union[List[int], str]:
    """Get report color for specific category and variant."""
    return get_color(f"reports.{category}.{variant}", format_type)


def normalize_color_value(color_value: Any) -> str:
    """Normalize any color value to hex string."""
    if isinstance(color_value, str):
        if color_value.startswith('#'):
            return color_value
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


def get_category_colors(category: str, sync_files: bool = True) -> Dict[str, str]:
    """Get all colors for a visualization category."""
    colors_config = load_colors()
    path = f"visualization.{category}"
    
    # Navigate to category
    current = colors_config
    for key in path.split('.'):
        if key not in current:
            raise ConfigurationError(f"Category '{category}' not found")
        current = current[key]
    
    # Convert to hex strings
    colors_dict = {}
    for key, value in current.items():
        if isinstance(value, str):
            colors_dict[key] = get_color(value, "hex", sync_files) if '.' in value else value
        elif isinstance(value, list) and len(value) >= 3:
            r, g, b = int(value[0]), int(value[1]), int(value[2])
            colors_dict[key] = f"#{r:02x}{g:02x}{b:02x}"
        else:
            raise ConfigurationError(f"Invalid color format for {category}.{key}: {value}")
    
    return colors_dict


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
    
    # Try custom palette
    try:
        colors_config = load_colors()
        palette_path = f"reports.tables.palettes.{palette_name}"
        
        current = colors_config
        for key in palette_path.split('.'):
            if key not in current:
                raise KeyError(f"Key '{key}' not found")
            current = current[key]
        
        if not isinstance(current, dict):
            raise ConfigurationError(f"Palette '{palette_name}' is not valid")
        
        # Convert to RGB tuples
        sorted_keys = sorted(current.keys())
        if reverse:
            sorted_keys = sorted_keys[::-1]
            
        colors = []
        for key in sorted_keys:
            color_value = current[key]
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
        
    except (KeyError, TypeError):
        raise ConfigurationError(f"Invalid colormap/palette: '{palette_name}'")


