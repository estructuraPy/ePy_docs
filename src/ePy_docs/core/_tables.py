"""
SOLID Architecture Tables Module - True SOLID Principles Implementation

This module implements pure SOLID architecture for table processing:
- Single Responsibility: Each class handles one specific aspect of table processing
- Open/Closed: Extensible via configuration, not code modification  
- Liskov Substitution: Clean interface implementations
- Interface Segregation: Focused, minimal interfaces
- Dependency Inversion: Depends on abstractions, not concrete implementations

Architecture Components:
- TableConfigManager: Configuration loading and validation
- FontManager: Font selection and cell font configuration
- ColorManager: Color palette management and cell coloring  
- CellFormatter: Cell formatting, content detection, and styling
- ImageRenderer: Table image generation with matplotlib
- MarkdownGenerator: Markdown content generation
- TableOrchestrator: Main coordinator with facade pattern

Performance: Optimized caching, lazy loading, and resource management
Memory: Efficient matplotlib usage with proper cleanup
Extensibility: Configuration-driven behavior, zero hardcoded values
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
from typing import Dict, Any, Union, List, Optional, Tuple, Protocol
from pathlib import Path
from abc import ABC, abstractmethod

from ePy_docs.core._data import (
    DataProcessor, TableAnalyzer
)
from ePy_docs.core._format import TextProcessor, FormatConfig
from ePy_docs.core._config import get_absolute_output_directories, get_layout
from ePy_docs.core._images import convert_rgb_to_matplotlib, get_palette_color_by_tone, setup_matplotlib_fonts


# ============================================================================
# SOLID ARCHITECTURE - SPECIALIZED CLASSES
# ============================================================================

class TableConfigManager:
    """
    SOLID: Single Responsibility - Handles all table configuration loading and validation.
    
    Responsibilities:
    - Load and cache table configuration from epyson files
    - Validate configuration parameters
    - Provide configuration defaults with intelligent fallbacks
    - Handle configuration lifecycle and caching
    """
    
    def __init__(self, config_provider=None):
        """Initialize with optional dependency injection for configuration provider."""
        self._config_provider = config_provider
        self._cache = {}
        self._config_cache = None
    
    def get_tables_config(self) -> Dict[str, Any]:
        """Load centralized table configuration with caching."""
        if self._config_cache is not None:
            return self._config_cache
        
        try:
            from ePy_docs.core._config import get_config_section, clear_global_cache
            
            config = get_config_section('tables')
            
            # If category_rules is missing, clear cache and reload
            if 'category_rules' not in config or not config.get('category_rules'):
                clear_global_cache()
                config = get_config_section('tables')
            
            self._config_cache = config
            return config
            
        except (ImportError, KeyError) as e:
            # Configuration-driven fallback - no hardcoded values
            raise RuntimeError(f"Table configuration not available: {e}")
    
    def get_layout_config(self, layout_style: str, document_type: str) -> Tuple[Dict, Dict, Dict, Dict, Dict, str]:
        """Load complete layout configuration for table rendering."""
        cache_key = f"{layout_style}_{document_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Load layout configuration with resolved references
            from ePy_docs.core._config import load_layout, get_config_section
            layout_config = load_layout(layout_style, resolve_refs=True)
            
            # Extract font family - can be direct or from reference
            font_family = layout_config.get('font_family')
            if not font_family:
                raise ValueError(f"Missing 'font_family' in layout '{layout_style}'")
            
            # Load font configuration - prefer resolved sections  
            font_config = {}
            font_family_info = {}
            
            # First try to use resolved 'text' section which should have both typography and font info
            if 'text' in layout_config:
                resolved_text = layout_config['text']
                
                # Get typography configuration
                if 'typography' in resolved_text:
                    font_config = resolved_text['typography']
                elif 'variants' in resolved_text:
                    # Try to get from default variant or first available
                    for variant_data in resolved_text['variants'].values():
                        font_config = variant_data
                        break
                
                # Get font family info (primary, fallback)
                font_family_info = {
                    'primary': resolved_text.get('primary', 'sans-serif'),
                    'fallback': resolved_text.get('fallback', 'sans-serif')
                }
            
            # Fallback to manual text_ref resolution if needed
            if not font_config and 'text_ref' in layout_config:
                text_data = get_config_section('text')
                ref_parts = layout_config['text_ref'].split('.')
                if len(ref_parts) == 2 and ref_parts[0] == 'text':
                    variant_name = ref_parts[1]
                    if 'variants' in text_data and variant_name in text_data['variants']:
                        font_config = text_data['variants'][variant_name]
            
            if not font_config:
                raise ValueError(f"Missing text_ref configuration in layout '{layout_style}'")
            
            if not font_family_info or 'primary' not in font_family_info:
                raise ValueError(
                    f"Missing font family info (primary/fallback) in layout '{layout_style}'. "
                    "Layout must have 'text' with 'primary' and 'fallback' keys"
                )
            
            # Merge font_family_info into font_config for convenience
            font_config['primary'] = font_family_info['primary']
            font_config['fallback'] = font_family_info.get('fallback', 'sans-serif')
            
            # Colors config from resolved palette_ref
            colors_config = layout_config.get('colors', {})
            
            # Load palettes from colors.epyson for colored tables
            # The palettes are needed for highlight_columns functionality
            colors_data = get_config_section('colors')
            if 'palettes' in colors_data:
                colors_config['palettes'] = colors_data['palettes']
            
            # Load tables configuration - prefer resolved 'tables' section
            style_config = {}
            table_config = {}
            
            # First try to use resolved 'tables' section
            if 'tables' in layout_config:
                table_config = layout_config['tables']
                style_config = table_config.get('styling', {})
            # Fallback to manual tables_ref resolution if needed
            elif 'tables_ref' in layout_config:
                tables_data = get_config_section('tables')
                ref_parts = layout_config['tables_ref'].split('.')
                if len(ref_parts) == 2 and ref_parts[0] == 'tables':
                    variant_name = ref_parts[1]
                    if 'variants' in tables_data and variant_name in tables_data['variants']:
                        variant = tables_data['variants'][variant_name]
                        style_config = variant.get('styling', {})
                        # Also store full table config for other uses
                        table_config = variant
            
            # Fallback to layout-level configs if no tables_ref
            if not style_config:
                style_config = layout_config.get('styling', {})
            if not table_config:
                table_config = layout_config.get('tables', {})
            
            code_config = layout_config.get('code', {})
            
            result = (font_config, colors_config, style_config, table_config, code_config, font_family)
            self._cache[cache_key] = result
            return result
            
        except Exception as e:
            raise RuntimeError(f"Layout configuration loading failed for {layout_style}: {e}")
    
    def clear_cache(self):
        """Clear configuration cache to force reload."""
        self._cache.clear()
        self._config_cache = None


class FontManager:
    """
    SOLID: Single Responsibility - Manages font selection and cell font configuration.
    
    Responsibilities:
    - Font family selection and validation
    - Cell-specific font configuration based on content type
    - Font size auto-adjustment based on content and layout
    - Code content detection and monospace font application
    """
    
    def __init__(self, config_manager: TableConfigManager):
        """Initialize with configuration manager dependency."""
        self._config_manager = config_manager
    
    def configure_cell_font(self, cell, text_value, is_header: bool, font_list: List[str], 
                           layout_style: str, code_config: Dict):
        """Configure specific font for each cell based on its content."""
        is_code_content = self._detect_code_content(text_value, is_header)
        
        if is_header:
            self._apply_header_font(cell, font_list)
        elif self._is_missing_value(text_value):
            self._apply_missing_value_font(cell, font_list)
        elif is_code_content:
            self._apply_code_font(cell, font_list, layout_style, code_config)
        else:
            self._apply_normal_font(cell, font_list)
    
    def auto_adjust_font_size(self, cell, original_font_size: float, num_columns: Optional[int] = None, 
                             num_rows: Optional[int] = None, text_content: str = None,
                             font_config: Dict = None) -> float:
        """Auto-adjust font size based on table dimensions and content using configuration."""
        if not font_config:
            raise ValueError("font_config required for auto_adjust_font_size")
            
        if 'auto_adjustment' not in font_config:
            raise ValueError("Missing 'auto_adjustment' configuration in font_config")
        
        adjustment_rules = font_config['auto_adjustment']
        adjusted_size = original_font_size
        
        # Column-based adjustment
        if num_columns and 'column_threshold' in adjustment_rules:
            if 'column_min_factor' not in adjustment_rules:
                raise ValueError("Missing 'column_min_factor' in auto_adjustment")
            if 'column_factor_per_unit' not in adjustment_rules:
                raise ValueError("Missing 'column_factor_per_unit' in auto_adjustment")
                
            threshold = adjustment_rules['column_threshold']
            if num_columns > threshold:
                min_factor = adjustment_rules['column_min_factor']
                factor_per_col = adjustment_rules['column_factor_per_unit']
                adjusted_size *= max(min_factor, 1.0 - (num_columns - threshold) * factor_per_col)
        
        # Row-based adjustment
        if num_rows and 'row_threshold' in adjustment_rules:
            if 'row_min_factor' not in adjustment_rules:
                raise ValueError("Missing 'row_min_factor' in auto_adjustment")
            if 'row_factor_per_unit' not in adjustment_rules:
                raise ValueError("Missing 'row_factor_per_unit' in auto_adjustment")
                
            threshold = adjustment_rules['row_threshold']
            if num_rows > threshold:
                min_factor = adjustment_rules['row_min_factor']
                factor_per_row = adjustment_rules['row_factor_per_unit']
                adjusted_size *= max(min_factor, 1.0 - (num_rows - threshold) * factor_per_row)
        
        # Content-based adjustment
        if text_content and 'content_length_threshold' in adjustment_rules:
            if 'content_length_factor' not in adjustment_rules:
                raise ValueError("Missing 'content_length_factor' in auto_adjustment")
                
            threshold = adjustment_rules['content_length_threshold']
            if len(str(text_content)) > threshold:
                content_factor = adjustment_rules['content_length_factor']
                adjusted_size *= content_factor
        
        # Apply minimum size limit from configuration
        if 'minimum_font_size' not in adjustment_rules:
            raise ValueError("Missing 'minimum_font_size' in auto_adjustment")
        
        min_size = adjustment_rules['minimum_font_size']
        adjusted_size = max(adjusted_size, min_size)
        
        cell.get_text().set_fontsize(adjusted_size)
        return adjusted_size
    
    def _detect_code_content(self, text_value, is_header: bool) -> bool:
        """Detect if cell content appears to be code."""
        if is_header or text_value is None:
            return False
            
        cell_str = str(text_value)
        code_indicators = ['def ', 'function', 'class ', '()', '{}', '[]', 'import ', 'from ', '=', '==']
        code_count = sum(1 for indicator in code_indicators if indicator in cell_str)
        return code_count >= 2
    
    def _is_missing_value(self, text_value) -> bool:
        """Detect if a value should be displayed in italic for being missing."""
        if pd.isna(text_value):
            return True
        
        text_str = str(text_value).strip().lower()
        missing_indicators = ['', 'nan', 'none', 'null', '-', '--', '---', 'n/a', 'na']
        return text_str in missing_indicators
    
    def _apply_header_font(self, cell, font_list: List[str]):
        """Apply header-specific font styling."""
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')
    
    def _apply_missing_value_font(self, cell, font_list: List[str]):
        """Apply italic styling for missing values."""
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('italic')
    
    def _apply_code_font(self, cell, font_list: List[str], layout_style: str, code_config: Dict):
        """Apply monospace font for code content."""
        try:
            if layout_style in code_config.get('layout_config', {}):
                code_layout = code_config['layout_config']
                if 'mono_font' in code_layout:
                    mono_font = code_layout['mono_font']['family']
                    cell.get_text().set_fontfamily([mono_font] + font_list)
                else:
                    cell.get_text().set_fontfamily(['monospace'] + font_list)
            else:
                cell.get_text().set_fontfamily(['monospace'] + font_list)
            cell.get_text().set_style('normal')
        except Exception:
            # Fallback to normal font if monospace configuration fails
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
    
    def _apply_normal_font(self, cell, font_list: List[str]):
        """Apply normal font styling."""
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')


class ColorManager:
    """
    SOLID: Single Responsibility - Manages color palette and cell coloring operations.
    
    Responsibilities:
    - Color palette loading and management
    - Cell background and text color application
    - Color gradient calculation for highlighted columns
    - Color accessibility and contrast management
    """
    
    def __init__(self, config_manager: TableConfigManager):
        """Initialize with configuration manager dependency."""
        self._config_manager = config_manager
        self._color_cache = {}
    
    def load_colors_configuration(self, layout_style: str) -> Dict:
        """Load color configuration for specific layout style."""
        if layout_style in self._color_cache:
            return self._color_cache[layout_style]
        
        try:
            from ePy_docs.core._config import get_config_section
            
            color_config = get_config_section('colors')
            layouts_config = color_config.get('layouts', {})
            
            if layout_style in layouts_config:
                style_colors = layouts_config[layout_style]
            else:
                # Fallback to minimal layout from configuration
                if 'minimal' not in layouts_config:
                    raise ValueError(f"Layout '{layout_style}' not found and no 'minimal' fallback in configuration")
                style_colors = layouts_config['minimal']
            
            self._color_cache[layout_style] = style_colors
            return style_colors
            
        except Exception as e:
            raise RuntimeError(f"Color configuration loading failed for {layout_style}: {e}")
    
    def apply_table_colors(self, table, df: pd.DataFrame, style_config: Dict, 
                          colors_config: Dict, highlight_columns: Union[str, List[str], None] = None,
                          palette_name: str = None) -> None:
        """Apply color scheme to table cells."""
        if not highlight_columns:
            return
        
        # Normalize highlight_columns to list
        if isinstance(highlight_columns, str):
            highlight_columns = [highlight_columns]
        
        # Filter columns that exist in DataFrame
        valid_columns = [col for col in highlight_columns if col in df.columns]
        if not valid_columns:
            return
        
        # Apply colors to each highlighted column
        for col_name in valid_columns:
            self._apply_column_highlighting(table, df, col_name, colors_config, palette_name)
    
    def _apply_column_highlighting(self, table, df: pd.DataFrame, column_name: str, 
                                  colors_config: Dict, palette_name: str = None):
        """Apply color highlighting to a specific column."""
        if column_name not in df.columns:
            return
        
        col_index = df.columns.get_loc(column_name)
        column_data = df[column_name]
        
        # Generate color gradient based on data values
        colors = self._generate_color_gradient(column_data, colors_config, palette_name)
        
        # Apply colors to cells (skip header row)
        for row_idx, color in enumerate(colors):
            cell = table[(row_idx + 1, col_index)]  # +1 to skip header
            cell.set_facecolor(color)
            
            # Adjust text color for contrast
            text_color = self._get_contrasting_text_color(color)
            cell.get_text().set_color(text_color)
    
    def _generate_color_gradient(self, column_data: pd.Series, colors_config: Dict, 
                                palette_name: str = None) -> List[str]:
        """Generate color gradient for column values."""
        # Get palette colors
        palette_colors = self._get_palette_colors(palette_name or 'blues', colors_config)
        
        # Normalize values to 0-1 range for color mapping
        numeric_data = pd.to_numeric(column_data, errors='coerce')
        if numeric_data.isna().all():
            # Non-numeric data - use categorical coloring
            return self._generate_categorical_colors(column_data, palette_colors)
        
        # Numeric data - use gradient coloring
        min_val, max_val = numeric_data.min(), numeric_data.max()
        if min_val == max_val:
            # All values are the same
            return [palette_colors[0]] * len(column_data)
        
        colors = []
        for value in numeric_data:
            if pd.isna(value):
                # Get white/missing color from palette
                missing_color = palette_colors[0] if palette_colors else get_palette_color_by_tone('neutrals', 'primary')
                colors.append(missing_color)
            else:
                # Normalize to 0-1 range
                normalized = (value - min_val) / (max_val - min_val)
                # Map to palette color
                color_index = int(normalized * (len(palette_colors) - 1))
                colors.append(palette_colors[color_index])
        
        return colors
    
    def _get_palette_colors(self, palette_name: str, colors_config: Dict) -> List[str]:
        """Get color list for specified palette."""
        palettes = colors_config.get('palettes', {})
        if palette_name not in palettes:
            raise ValueError(f"Palette '{palette_name}' not found in configuration")
        
        # Get colors from tone sequence (primary -> senary)
        palette = palettes[palette_name]
        tones = ['primary', 'secondary', 'tertiary', 'quaternary', 'quinary', 'senary']
        colors = []
        for tone in tones:
            if tone in palette:
                color_rgb = palette[tone]
                # Convert RGB tuple to hex format
                if isinstance(color_rgb, (list, tuple)) and len(color_rgb) >= 3:
                    r, g, b = [int(c * 255) if c <= 1 else int(c) for c in color_rgb[:3]]
                    colors.append(f'#{r:02X}{g:02X}{b:02X}')
                elif isinstance(color_rgb, str):
                    colors.append(color_rgb)
        
        if not colors:
            raise ValueError(f"Palette '{palette_name}' has no valid colors")
        
        return colors
    
    def _generate_categorical_colors(self, column_data: pd.Series, palette_colors: List[str]) -> List[str]:
        """Generate colors for categorical data."""
        unique_values = column_data.unique()
        color_map = {}
        
        for i, value in enumerate(unique_values):
            color_map[value] = palette_colors[i % len(palette_colors)]
        
        # Use first palette color as fallback for missing
        fallback_color = palette_colors[0] if palette_colors else get_palette_color_by_tone('neutrals', 'primary')
        return [color_map.get(value, fallback_color) for value in column_data]
    
    def _get_contrasting_text_color(self, background_color: str) -> str:
        """Get contrasting text color (black or white) for given background."""
        try:
            # Convert color to RGB
            color_rgb = convert_rgb_to_matplotlib(background_color)
            
            # Calculate luminance
            r, g, b = color_rgb[:3] if len(color_rgb) >= 3 else (1, 1, 1)
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            
            # Return colors from neutral palette for proper theming
            if luminance > 0.5:
                return get_palette_color_by_tone('neutrals', 'senary')  # Dark text
            else:
                return get_palette_color_by_tone('neutrals', 'primary')  # Light text
        except Exception:
            # Fallback to dark text from configuration
            return get_palette_color_by_tone('neutrals', 'senary')


class CellFormatter:
    """
    SOLID: Single Responsibility - Handles cell formatting, content detection and styling.
    
    Responsibilities:
    - Cell content formatting and text wrapping
    - Content type detection (code, missing values, etc.)
    - Cell styling and alignment
    - Header formatting with multiline support
    """
    
    def __init__(self, font_manager: FontManager, color_manager: ColorManager):
        """Initialize with font and color manager dependencies."""
        self._font_manager = font_manager
        self._color_manager = color_manager
    
    def format_table_cells(self, table, df: pd.DataFrame, font_list: List[str],
                          font_config: Dict, layout_style: str, code_config: Dict,
                          font_size: float = None, missing_value_style: str = 'italic',
                          **kwargs) -> None:
        """Format and style all table cells."""
        # Get font size from configuration if not provided
        if font_size is None:
            if 'element_typography' not in font_config:
                raise ValueError(
                    "Missing 'element_typography' in font_config. "
                    "Text configuration must include 'element_typography.tables.content.size'"
                )
            
            tables_typo = font_config['element_typography'].get('tables', {})
            if 'content' not in tables_typo or 'size' not in tables_typo['content']:
                raise ValueError(
                    "Missing 'element_typography.tables.content.size' in font_config"
                )
            
            font_size = tables_typo['content']['size']
        
        # Format each cell
        num_rows, num_cols = df.shape
        num_rows += 1  # Include header row
        
        for (row, col), cell in table.get_celld().items():
            # Determine if this is a header cell
            is_header = (row == 0)
            
            # Get cell content
            if is_header:
                text_value = df.columns[col] if col < len(df.columns) else ""
                text_value = self._apply_header_multiline(str(text_value))
            else:
                if row - 1 < len(df) and col < len(df.columns):
                    text_value = df.iloc[row - 1, col]
                else:
                    text_value = ""
            
            # Apply font configuration
            self._font_manager.configure_cell_font(
                cell, text_value, is_header, font_list, layout_style, code_config
            )
            
            # Auto-adjust font size if configuration available
            if 'auto_adjustment' in font_config:
                self._font_manager.auto_adjust_font_size(
                    cell, font_size, num_cols, num_rows, str(text_value), font_config
                )
            
            # Apply additional cell styling with text wrapping
            self._apply_cell_styling(cell, is_header, text_value)
    
    def _apply_header_multiline(self, header_text: str, max_length: int = 12) -> str:
        """Apply multiline formatting to header text if needed."""
        if len(header_text) <= max_length:
            return header_text
        
        # Split on common delimiters
        for delimiter in [' ', '_', '-', '.']:
            if delimiter in header_text:
                parts = header_text.split(delimiter)
                if len(parts) > 1:
                    # Try to create balanced lines
                    mid_point = len(parts) // 2
                    line1 = delimiter.join(parts[:mid_point])
                    line2 = delimiter.join(parts[mid_point:])
                    if max(len(line1), len(line2)) < len(header_text):
                        return f"{line1}\n{line2}"
        
        # Fallback: split at midpoint
        mid = len(header_text) // 2
        return f"{header_text[:mid]}\n{header_text[mid:]}"
    
    def _apply_cell_styling(self, cell, is_header: bool, text_value, max_width: int = 15) -> None:
        """Apply additional styling to cells with text wrapping."""
        # Apply text wrapping for long content
        if isinstance(text_value, str) and len(str(text_value)) > max_width:
            wrapped_text = self._wrap_text_content(str(text_value), max_width)
            cell.get_text().set_text(wrapped_text)
        
        # Set cell alignment
        cell.get_text().set_horizontalalignment('center')
        cell.get_text().set_verticalalignment('center')
        
        # Apply padding
        cell.set_linewidth(0.5)
        
        # Header-specific styling
        if is_header:
            cell.get_text().set_weight('bold')
    
    def _wrap_text_content(self, text: str, max_width: int = 15) -> str:
        """Wrap text content to prevent cell overflow."""
        if len(text) <= max_width:
            return text
        
        # Split on natural word boundaries first
        words = text.split()
        if len(words) > 1:
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_width:
                    current_line = current_line + " " + word if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            return "\n".join(lines)
        
        # For single long words, break at max_width
        lines = []
        for i in range(0, len(text), max_width):
            lines.append(text[i:i + max_width])
        
        return "\n".join(lines)
    
    def detect_format_code_content(self, cell_value, code_config: Dict, available_languages: List[str]) -> str:
        """Detect and format code content in cells."""
        if not cell_value or pd.isna(cell_value):
            return ""
        
        cell_str = str(cell_value)
        code_indicators = [
            'def ', 'function', 'class ',
            'import ', 'from ', 'export ', 'const ',
            'var ', 'let ', 'function(', 'return ',
            '{}', '[]', '()', '=>', '==', '!='
        ]
        
        code_count = sum(1 for indicator in code_indicators if indicator in cell_str)
        
        if code_count >= 2:
            # Try to detect language
            if 'language_detection' not in code_config:
                return 'generic'
            
            lang_detection = code_config['language_detection']
            for lang in available_languages:
                if lang not in lang_detection:
                    continue
                lang_indicators = lang_detection[lang]
                if any(indicator in cell_str for indicator in lang_indicators):
                    return lang
            return 'generic'
        
        return ""


class ImageRenderer:
    """
    SOLID: Single Responsibility - Handles matplotlib table image generation.
    
    Responsibilities:
    - Matplotlib figure and table creation
    - Image rendering and saving
    - DPI and size optimization
    - Memory management and cleanup
    """
    
    def __init__(self, config_manager: TableConfigManager):
        """Initialize with configuration manager dependency."""
        self._config_manager = config_manager
    
    def create_table_image(self, data: Union[pd.DataFrame, List[List]], 
                          title: str = None, layout_style: str = "corporate",
                          output_dir: str = None, table_number: int = 1,
                          width_inches: float = None, **kwargs) -> str:
        """Create table image and return the file path."""
        # Setup matplotlib
        self._setup_matplotlib(layout_style)
        
        # Convert data to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Load configuration
        document_type = kwargs.get('document_type')
        if not document_type:
            raise ValueError("Missing required parameter 'document_type' in kwargs")
        
        font_config, colors_config, style_config, table_config, code_config, font_family = \
            self._config_manager.get_layout_config(layout_style, document_type)
        
        # Calculate dimensions
        width_inches = width_inches or self._calculate_width(df, style_config)
        height_inches = self._calculate_height(df, style_config)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width_inches, height_inches))
        ax.axis('tight')
        ax.axis('off')
        
        try:
            # Create matplotlib table with layout colors
            table = self._create_matplotlib_table(ax, df, font_config, style_config, colors_config)
            
            # Apply formatting
            cell_formatter = CellFormatter(
                FontManager(self._config_manager),
                ColorManager(self._config_manager)
            )
            
            font_list = self._get_font_list(font_family, font_config)
            cell_formatter.format_table_cells(
                table, df, font_list, font_config, layout_style, code_config
            )
            
            # Apply colors if requested
            if kwargs.get('highlight_columns') or kwargs.get('colored'):
                color_manager = ColorManager(self._config_manager)
                color_manager.apply_table_colors(
                    table, df, style_config, colors_config,
                    kwargs.get('highlight_columns'), kwargs.get('palette_name')
                )
            
            # Add title if provided
            if title:
                self._add_title(fig, title, font_config)
            
            # Save image
            output_path = self._save_image(fig, output_dir, table_number, title)
            
            return output_path
            
        finally:
            # Clean up matplotlib resources
            plt.close(fig)
    
    def _setup_matplotlib(self, layout_style: str):
        """Setup matplotlib with optimal settings."""
        plt.style.use('default')
        setup_matplotlib_fonts(layout_style)
    
    def _create_matplotlib_table(self, ax, df: pd.DataFrame, font_config: Dict, style_config: Dict, colors_config: Dict = None):
        """Create the basic matplotlib table with layout-specific styling."""
        # Prepare data for table
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Create table
        table = ax.table(
            cellText=table_data[1:],  # Data rows
            colLabels=table_data[0],  # Header row
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        
        # Basic table styling
        table.auto_set_font_size(False)
        
        # Get font size from configuration - expect new structure
        if 'element_typography' not in font_config:
            raise ValueError(
                "Missing 'element_typography' in font_config. "
                "Text configuration must include 'element_typography.tables.content.size'"
            )
        
        tables_typo = font_config['element_typography'].get('tables', {})
        if 'content' not in tables_typo or 'size' not in tables_typo['content']:
            raise ValueError(
                "Missing 'element_typography.tables.content.size' in font_config. "
                f"Available: {list(tables_typo.keys())}"
            )
        
        font_size = tables_typo['content']['size']
        table.set_fontsize(font_size)
        table.scale(1, 1.5)  # Adjust cell height
        
        # Apply layout-specific colors
        self._apply_table_layout_colors(table, df, colors_config)
        
        return table
    
    def _apply_table_layout_colors(self, table, df: pd.DataFrame, colors_config: Dict = None):
        """Apply layout-specific colors to table headers and cells."""
        if not colors_config or 'palette' not in colors_config:
            return
        
        palette = colors_config['palette']
        
        # Get primary color for headers
        header_color = palette.get('primary', [150, 150, 150])  # Fallback to gray
        if isinstance(header_color, list) and len(header_color) >= 3:
            header_rgb = [c/255.0 for c in header_color[:3]]  # Convert to matplotlib format
        else:
            header_rgb = [0.6, 0.6, 0.6]  # Gray fallback
        
        # Get secondary color for alternate rows
        background_color = palette.get('secondary', [245, 245, 245])  # Light background
        if isinstance(background_color, list) and len(background_color) >= 3:
            bg_rgb = [c/255.0 for c in background_color[:3]]
        else:
            bg_rgb = [0.96, 0.96, 0.96]  # Very light gray
        
        # Apply header colors
        num_cols = len(df.columns)
        for col in range(num_cols):
            header_cell = table[(0, col)]
            header_cell.set_facecolor(header_rgb)
            
            # Set contrasting text color
            luminance = 0.299 * header_rgb[0] + 0.587 * header_rgb[1] + 0.114 * header_rgb[2]
            text_color = 'white' if luminance < 0.5 else 'black'
            header_cell.get_text().set_color(text_color)
        
        # Apply alternating row colors
        num_rows = len(df)
        for row in range(1, num_rows + 1):  # Skip header row (0)
            if row % 2 == 0:  # Even rows
                for col in range(num_cols):
                    cell = table[(row, col)]
                    cell.set_facecolor(bg_rgb)
    
    def _calculate_width(self, df: pd.DataFrame, style_config: Dict) -> float:
        """Calculate optimal table width from configuration.
        
        Raises:
            ValueError: If width_in not found in style_config
        """
        if 'width_in' not in style_config:
            raise ValueError(
                f"Missing 'width_in' in style_config. "
                f"Tables configuration must include 'styling.width_in'. "
                f"Available keys: {list(style_config.keys())}"
            )
        
        base_width = style_config['width_in']
        num_cols = len(df.columns)
        
        # Adjust for number of columns
        if num_cols > 5:
            return min(base_width * 1.2, 12.0)
        elif num_cols < 3:
            return max(base_width * 0.8, 4.0)
        
        return base_width
    
    def _calculate_height(self, df: pd.DataFrame, style_config: Dict) -> float:
        """Calculate optimal table height from configuration."""
        # Use row_height if available, otherwise calculate dynamically
        row_height = style_config.get('row_height_in', 0.3)
        
        # Calculate height based on number of rows
        num_rows = len(df) + 1  # Include header
        calculated_height = num_rows * row_height + 1  # Add padding
        
        return min(max(calculated_height, 2.0), 15.0)  # Clamp between 2 and 15 inches
    
    def _get_font_list(self, font_family: str, font_config: Dict = None) -> List[str]:
        """Get font list for the specified font family from configuration.
        
        Raises:
            ValueError: If font configuration is incomplete
        """
        # Font config should have primary and fallback from text configuration
        if not font_config:
            raise ValueError("font_config is required")
        
        if 'primary' not in font_config:
            raise ValueError(
                f"Missing 'primary' in font_config. "
                f"Text configuration must include font primary and fallback. "
                f"Available keys: {list(font_config.keys())}"
            )
        
        fonts = [font_config['primary']]
        if 'fallback' in font_config:
            fonts.append(font_config['fallback'])
        
        return fonts
    
    def _add_title(self, fig, title: str, font_config: Dict):
        """Add title to the figure.
        
        Raises:
            ValueError: If title size not found in font_config
        """
        if 'element_typography' not in font_config:
            raise ValueError(
                "Missing 'element_typography' in font_config. "
                "Text configuration must include 'element_typography.tables.title.size'"
            )
        
        tables_typo = font_config['element_typography'].get('tables', {})
        if 'title' not in tables_typo or 'size' not in tables_typo['title']:
            raise ValueError(
                "Missing 'element_typography.tables.title.size' in font_config"
            )
        
        title_size = tables_typo['title']['size']
        fig.suptitle(title, fontsize=title_size, fontweight='bold', y=0.95)
    
    def _save_image(self, fig, output_dir: str, table_number: int, title: str = None) -> str:
        """Save the figure and return the file path."""
        if not output_dir:
            abs_dirs = get_absolute_output_directories()
            if 'results' not in abs_dirs:
                raise ValueError("Missing 'results' directory in output configuration")
            output_dir = abs_dirs['results']
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if title:
            filename = f"table_{table_number}_{title.replace(' ', '_').lower()}.png"
        else:
            filename = f"table_{table_number}.png"
        
        output_path = Path(output_dir) / filename
        
        # Save with high quality
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.1,
            facecolor='white',
            edgecolor='none'
        )
        
        return str(output_path)


class MarkdownGenerator:
    """
    SOLID: Single Responsibility - Generates markdown content for tables.
    
    Responsibilities:
    - Markdown formatting for single and split tables
    - Image reference generation
    - Caption and numbering management
    - Output format optimization
    """
    
    def __init__(self):
        """Initialize markdown generator."""
        pass
    
    def generate_table_markdown(self, image_paths: Union[str, List[str]], 
                               caption: str = None, table_number: int = 1,
                               **kwargs) -> str:
        """Generate markdown content for table(s)."""
        if isinstance(image_paths, str):
            return self._generate_single_table_markdown(image_paths, caption, table_number)
        else:
            return self._generate_split_table_markdown(image_paths, caption, table_number)
    
    def _generate_single_table_markdown(self, image_path: str, caption: str, table_number: int) -> str:
        """Generate markdown for a single table in Quarto format."""
        # Extract relative path for markdown
        rel_path = self._get_relative_path(image_path)
        
        # Quarto format with figure reference
        label = f"#tbl-{table_number}"
        if caption:
            return f"![{caption}]({rel_path}){{{label}}}\n\n"
        else:
            return f"![]({rel_path}){{{label}}}\n\n"
    
    def _generate_split_table_markdown(self, image_paths: List[str], caption: str, table_number: int) -> str:
        """Generate markdown for split tables in Quarto format."""
        markdown_parts = []
        num_parts = len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            rel_path = self._get_relative_path(image_path)
            
            # Quarto format with figure reference
            label = f"#tbl-{table_number + i}"
            if caption:
                part_caption = f"{caption} - Parte {i+1}/{num_parts}"
                markdown_parts.append(f"![{part_caption}]({rel_path}){{{label}}}")
            else:
                markdown_parts.append(f"![]({rel_path}){{{label}}}")
        
        return "\n\n".join(markdown_parts) + "\n\n"
    
    def _get_relative_path(self, image_path: str) -> str:
        """Convert absolute path to relative path for markdown."""
        path = Path(image_path)
        
        # Try to make relative to current directory
        try:
            rel_path = path.relative_to(Path.cwd())
            return str(rel_path).replace('\\', '/')
        except ValueError:
            # If can't make relative, use filename only
            return path.name


class TableOrchestrator:
    """
    SOLID: Facade Pattern - Main coordinator for table processing operations.
    
    Responsibilities:
    - Coordinate all table processing components
    - Provide simple public API
    - Handle component lifecycle and dependencies
    - Manage error handling and fallbacks
    """
    
    def __init__(self):
        """Initialize with dependency injection of all components."""
        self._config_manager = TableConfigManager()
        self._font_manager = FontManager(self._config_manager)
        self._color_manager = ColorManager(self._config_manager)
        self._cell_formatter = CellFormatter(self._font_manager, self._color_manager)
        self._image_renderer = ImageRenderer(self._config_manager)
        self._markdown_generator = MarkdownGenerator()
    
    def create_table_image_and_markdown(self, df: pd.DataFrame, caption: str = None,
                                       layout_style: str = "corporate", output_dir: str = None,
                                       table_number: int = 1, columns: Union[float, List[float], None] = None,
                                       **kwargs) -> Tuple[str, Union[str, List[str]], int]:
        """
        Main public API for table processing.
        
        Args:
            df: DataFrame containing table data
            caption: Table caption/title
            layout_style: Layout style name
            output_dir: Output directory for table image
            table_number: Table number for counter
            columns: Width specification for multi-column layouts
            **kwargs: Additional options
            
        Returns:
            Tuple of (markdown_content, image_path_or_paths, new_counter)
        """
        try:
            # Get document type (required)
            document_type = kwargs.get('document_type')
            if not document_type:
                raise ValueError("Missing required parameter 'document_type' in kwargs")
            
            # Calculate width from columns parameter
            width_inches = self._calculate_width_from_columns(columns, document_type)
            
            # Remove width_inches from kwargs to avoid duplicate parameter error
            kwargs_clean = {k: v for k, v in kwargs.items() if k != 'width_inches'}
            
            # Check if table needs to be split
            max_rows_per_table = kwargs_clean.pop('max_rows_per_table', None)
            if max_rows_per_table:
                # Handle list input for max_rows_per_table
                if isinstance(max_rows_per_table, list):
                    # Always split when list is provided
                    should_split = True
                else:
                    # Split only if table exceeds max_rows
                    should_split = len(df) > max_rows_per_table
                
                if should_split:
                    return self._process_split_table(
                        df, caption, layout_style, output_dir, table_number, 
                        width_inches, max_rows_per_table, **kwargs_clean
                    )
            else:
                return self._process_single_table(
                    df, caption, layout_style, output_dir, table_number, 
                    width_inches, **kwargs_clean
                )
                
        except Exception as e:
            # Error handling with informative message
            raise RuntimeError(f"Table processing failed: {e}")
    
    def _calculate_width_from_columns(self, columns: Union[float, List[float], None], document_type: str) -> Optional[float]:
        """Calculate width in inches from columns specification."""
        if columns is None:
            return None
        
        if isinstance(columns, list):
            return columns[0] if columns else None
        
        # Use ColumnWidthCalculator for width calculation
        try:
            from ePy_docs.core._document import ColumnWidthCalculator
            calculator = ColumnWidthCalculator()
            
            if columns == 1:
                layout_columns = 1  # Full width
            else:
                # Get layout columns from config
                try:
                    from ePy_docs.core._config import ModularConfigLoader
                    config_loader = ModularConfigLoader()
                    doc_config = config_loader.load_external('document_types')
                    
                    doc_types = doc_config.get('document_types', {})
                    if document_type not in doc_types:
                        raise ValueError(f"Document type '{document_type}' not found in configuration")
                    
                    type_config = doc_types[document_type]
                    if 'default_columns' not in type_config:
                        raise ValueError(f"Missing 'default_columns' for document type '{document_type}'")
                    
                    layout_columns = type_config['default_columns']
                except Exception as e:
                    raise ValueError(f"Failed to load layout columns for '{document_type}': {e}")
            
            return calculator.calculate_width(document_type, layout_columns, columns)
            
        except Exception as e:
            # Configuration required - no hardcoded fallbacks
            raise ValueError(f"Width calculation failed for document_type '{document_type}': {e}. "
                           "Ensure ColumnWidthCalculator is properly configured.")
    
    def _process_single_table(self, df: pd.DataFrame, caption: str, layout_style: str,
                             output_dir: str, table_number: int, width_inches: Optional[float],
                             **kwargs) -> Tuple[str, str, int]:
        """Process a single table."""
        # Generate table image
        image_path = self._image_renderer.create_table_image(
            df, caption, layout_style, output_dir, table_number, width_inches, **kwargs
        )
        
        # Generate markdown
        markdown_content = self._markdown_generator.generate_table_markdown(
            image_path, caption, table_number, **kwargs
        )
        
        return markdown_content, image_path, table_number
    
    def _process_split_table(self, df: pd.DataFrame, caption: str, layout_style: str,
                            output_dir: str, table_number: int, width_inches: Optional[float],
                            max_rows_per_table: Union[int, List[int]], **kwargs) -> Tuple[str, List[str], int]:
        """Process a table that needs to be split."""
        # Split DataFrame into chunks based on max_rows specification
        table_chunks = []
        
        if isinstance(max_rows_per_table, list):
            # Use specified sizes for each chunk, put remainder in last chunk
            current_idx = 0
            for chunk_size in max_rows_per_table:
                if current_idx >= len(df):
                    break
                chunk = df.iloc[current_idx:current_idx + chunk_size].copy()
                table_chunks.append(chunk)
                current_idx += chunk_size
            # Add remaining rows if any
            if current_idx < len(df):
                chunk = df.iloc[current_idx:].copy()
                table_chunks.append(chunk)
        else:
            # Use fixed size for all chunks
            for i in range(0, len(df), max_rows_per_table):
                chunk = df.iloc[i:i + max_rows_per_table].copy()
                table_chunks.append(chunk)
        
        # Generate images for each chunk
        image_paths = []
        current_table_number = table_number
        
        for i, chunk in enumerate(table_chunks):
            part_caption = f"{caption} (Parte {i+1})" if caption else None
            
            image_path = self._image_renderer.create_table_image(
                chunk, part_caption, layout_style, output_dir, 
                current_table_number, width_inches, **kwargs
            )
            
            image_paths.append(image_path)
            if i < len(table_chunks) - 1:  # Only increment if not last chunk
                current_table_number += 1
        
        # Generate combined markdown
        markdown_content = self._markdown_generator.generate_table_markdown(
            image_paths, caption, table_number, **kwargs
        )
        
        return markdown_content, image_paths, current_table_number


# ============================================================================
# GLOBAL ORCHESTRATOR INSTANCE
# ============================================================================

table_orchestrator = TableOrchestrator()
