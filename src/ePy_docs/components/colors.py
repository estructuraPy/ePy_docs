
"""Color management utilities for styling and visualization.

Centralized color configuration access and management.
Direct access to colors.json configuration through core setup functions.
"""

from typing import Dict, Any, Union, List, Optional
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt

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

# Direct access configuration loading
def load_colors_config(sync_files: bool = True) -> Dict[str, Any]:
    """Load colors configuration from colors.json.
    
    Direct access to colors configuration through centralized loading system.
    
    Args:
        sync_files: Whether to use synchronized configuration files
        
    Returns:
        Complete colors configuration dictionary
        
    Raises:
        ConfigurationError: If colors configuration cannot be loaded
    """
    from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
    try:
        config_path = _resolve_config_path('colors', sync_files)
        return _load_cached_files(config_path, sync_files)
    except Exception as e:
        raise ConfigurationError(f"Failed to load colors configuration: {e}")

def get_color_value(path: str, format_type: str = "rgb", sync_files: bool = True) -> Union[List[int], str]:
    """Get color value using dot notation.
    
    Args:
        path: Dot notation path to color (e.g., 'brand.brand_primary')
        format_type: Output format 'rgb' or 'hex'
        sync_files: Whether to use synchronized configuration files
        
    Returns:
        Color value in specified format
    """
    colors_config = load_colors_config(sync_files)
    
    keys = path.split('.')
    color_value = colors_config
    for key in keys:
        color_value = color_value[key]
    
    if isinstance(color_value, list) and len(color_value) >= 3:
        r, g, b = color_value[:3]
        return f"#{r:02x}{g:02x}{b:02x}" if format_type.lower() == "hex" else [r, g, b]
        
    elif isinstance(color_value, str):
        if color_value.startswith('#'):
            if format_type.lower() == "hex":
                return color_value
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

# Backward compatibility - mantener función original pero deprecada
def load_colors() -> Dict[str, Any]:
    """⚠️ DEPRECATED: Use load_colors_config() instead."""
    return load_colors_config(sync_files=False)

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

# Estas funciones son alias directos - sin intermediarios
get_color = get_color_value

def get_report_color(category: str, variant: str, format_type: str = "rgb", sync_files: bool = True) -> Union[List[int], str]:
    """Direct access to report colors."""
    colors_config = load_colors_config(sync_files)
    keys = f"reports.{category}.{variant}".split('.')
    color_value = colors_config
    for key in keys:
        color_value = color_value[key]
    
    if isinstance(color_value, list) and len(color_value) >= 3:
        r, g, b = color_value[:3]
        return f"#{r:02x}{g:02x}{b:02x}" if format_type.lower() == "hex" else [r, g, b]
    elif isinstance(color_value, str):
        if color_value.startswith('#'):
            if format_type.lower() == "hex":
                return color_value
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
    """Direct access to visualization category colors."""
    colors_config = load_colors_config(sync_files)
    
    # Direct navigation to visualization category
    if 'visualization' not in colors_config or category not in colors_config['visualization']:
        raise ConfigurationError(f"Category '{category}' not found in visualization")
    
    category_data = colors_config['visualization'][category]
    
    # Handle different data structures
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
        # Handle dictionary structure (like general_colors, background_colors, etc.)
        for key, value in category_data.items():
            if isinstance(value, str):
                if value.startswith('#'):
                    colors_dict[key] = value
                elif '.' in value:
                    # Direct resolution of color reference
                    ref_keys = value.split('.')
                    ref_value = colors_config
                    for ref_key in ref_keys:
                        ref_value = ref_value[ref_key]
                    if isinstance(ref_value, list) and len(ref_value) >= 3:
                        r, g, b = int(ref_value[0]), int(ref_value[1]), int(ref_value[2])
                        colors_dict[key] = f"#{r:02x}{g:02x}{b:02x}"
                    else:
                        colors_dict[key] = ref_value
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
    
    # Direct access to custom palette
    try:
        colors_config = load_colors_config(sync_files=False)
        
        # Check for palette in the correct location: visualization.table_palettes
        if ('visualization' not in colors_config or 
            'table_palettes' not in colors_config['visualization'] or
            palette_name not in colors_config['visualization']['table_palettes']):
            raise KeyError(f"Palette '{palette_name}' not found")
            
        palette_colors = colors_config['visualization']['table_palettes'][palette_name]
        
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
        
    except (KeyError, TypeError):
        raise ConfigurationError(f"Invalid colormap/palette: '{palette_name}'")

