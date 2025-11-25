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
    DataProcessor, TableAnalyzer, TablePreparation, 
    TableDimensionCalculator, TableContentAnalyzer
)
from ePy_docs.core._format import TextProcessor, FormatConfig, TableTextWrapper
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
        """Load centralized table configuration with caching.
        
        Note: tables configuration is now embedded in layouts.
        This method is deprecated and should use layout-specific config instead.
        """
        if self._config_cache is not None:
            return self._config_cache
        
        # Tables config is now part of layouts, return empty dict
        # Individual layouts will have their own 'tables' section
        self._config_cache = {}
        return self._config_cache
    
    def get_layout_config(self, layout_style: str, document_type: str) -> Tuple[Dict, Dict, Dict, Dict, Dict, str]:
        """Load complete layout configuration for table rendering."""
        cache_key = f"{layout_style}_{document_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Load layout configuration with resolved references
            from ePy_docs.core._config import load_layout, get_config_section
            layout_config = load_layout(layout_style, resolve_refs=True)
            
            # Extract font family information - NO FALLBACKS
            font_family = layout_config.get('font_family')
            font_family_ref = layout_config.get('font_family_ref')
            
            if not font_family and not font_family_ref:
                raise ValueError(
                    f"Layout '{layout_style}' must have either 'font_family' or 'font_family_ref'. "
                    f"Available keys: {list(layout_config.keys())}"
                )
            
            # Load font configuration
            font_config = {}
            font_family_info = {}
            
            # Get font info from resolved font_family
            if font_family and isinstance(font_family, dict):
                if 'primary' not in font_family:
                    raise ValueError(
                        f"Layout '{layout_style}': 'font_family' must have 'primary' key. "
                        f"Found: {list(font_family.keys())}"
                    )
                if 'fallback' not in font_family:
                    raise ValueError(
                        f"Layout '{layout_style}': 'font_family' must have 'fallback' key. "
                        f"Found: {list(font_family.keys())}"
                    )
                font_family_info = {
                    'primary': font_family['primary'],
                    'fallback': font_family['fallback']
                }
            
            # If font_family_ref exists, resolve it from layout's font_families
            elif font_family_ref:
                if 'font_families' not in layout_config:
                    raise ValueError(
                        f"Layout '{layout_style}' references font_family_ref '{font_family_ref}' "
                        f"but layout has no 'font_families' section"
                    )
                
                font_families = layout_config['font_families']
                
                if font_family_ref not in font_families:
                    raise ValueError(
                        f"Layout '{layout_style}' references font_family_ref '{font_family_ref}' "
                        f"but it's not in layout font_families. Available: {list(font_families.keys())}"
                    )
                
                font_info = font_families[font_family_ref]
                if 'primary' not in font_info:
                    raise ValueError(
                        f"Font family '{font_family_ref}' must have 'primary' key"
                    )
                if 'fallback' not in font_info:
                    raise ValueError(
                        f"Font family '{font_family_ref}' must have 'fallback' key"
                    )
                
                font_family_info = {
                    'primary': font_info['primary'],
                    'fallback': font_info['fallback']
                }
            
            # Get typography configuration from layout
            typography = layout_config.get('typography', {})
            if not typography:
                raise ValueError(
                    f"Layout '{layout_style}' has no 'typography' section"
                )
            
            if font_family_ref or font_family_info:
                # Build complete font_config from typography
                if typography:
                    font_config = {
                        'primary': font_family_info['primary'],
                        'fallback': font_family_info['fallback'],
                        'role_assignments': typography.get('role_assignments', {}),
                        'scales': typography.get('scales', {}),
                        'line_spacing': typography.get('line_spacing', {}),
                        'element_typography': typography.get('element_typography', {})
                    }
                else:
                    # Fallback: create basic font_config with minimal element_typography
                    font_config = {
                        'primary': font_family_info['primary'],
                        'fallback': font_family_info['fallback'],
                        'element_typography': {
                            'tables': {
                                'content': {'size': 10},
                                'header': {'size': 11}
                            }
                        }
                    }
            else:
                raise ValueError(
                    f"Layout '{layout_style}' has neither 'font_family' nor 'font_family_ref'. "
                    f"Available keys: {list(layout_config.keys())}"
                )
            
            # Colors configuration - use palette directly from layout (RGB arrays, not converted to hex)
            colors_config = layout_config.get('colors', {})
            
            # Get palette directly from layout (keeps RGB arrays intact)
            if 'palette' in layout_config:
                embedded_palette = layout_config['palette']
                
                # Flatten palette structure: colors, page, code, table sections
                flattened_palette = {}
                
                # Add main colors (primary, secondary, etc.)
                if 'colors' in embedded_palette:
                    flattened_palette.update(embedded_palette['colors'])
                
                # Add page colors with prefix
                if 'page' in embedded_palette:
                    for key, value in embedded_palette['page'].items():
                        flattened_palette[f'page_{key}'] = value
                
                # Add code colors with prefix
                if 'code' in embedded_palette:
                    for key, value in embedded_palette['code'].items():
                        flattened_palette[f'code_{key}'] = value
                
                # Add table colors with prefix
                if 'table' in embedded_palette:
                    for key, value in embedded_palette['table'].items():
                        flattened_palette[f'table_{key}'] = value
                
                # Add border and caption colors
                if 'border_color' in embedded_palette:
                    flattened_palette['border_color'] = embedded_palette['border_color']
                if 'caption_color' in embedded_palette:
                    flattened_palette['caption_color'] = embedded_palette['caption_color']
                
                colors_config['palette'] = flattened_palette
                colors_config['palettes'] = {
                    layout_style: flattened_palette
                }
            
            # Also load color_palettes from colors.epyson for highlighting (blues, grays, etc.)
            colors_data = get_config_section('colors')
            if 'color_palettes' in colors_data:
                if 'palettes' not in colors_config:
                    colors_config['palettes'] = {}
                colors_config['palettes'].update(colors_data['color_palettes'])
                colors_config['color_palettes'] = colors_data['color_palettes']
            
            # Tables configuration - now embedded in layouts
            style_config = {}
            table_config = {}
            
            # Tables configuration is now directly in layout (no external file)
            if 'tables' in layout_config:
                table_config = layout_config['tables']
                style_config = table_config.get('styling', {})
            else:
                raise ValueError(
                    f"Layout '{layout_style}' has no 'tables' configuration. "
                    f"All layouts must have an embedded 'tables' section."
                )
            
            # Code configuration (optional - only needed for code blocks)
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
        
        # CRITICAL: Always apply font family first, regardless of content type
        cell.get_text().set_fontfamily(font_list)
        
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
        # Ensure font family is applied
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')
        cell.get_text().set_weight('bold')
    
    def _apply_missing_value_font(self, cell, font_list: List[str]):
        """Apply italic styling for missing values."""
        # Ensure font family is applied
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('italic')
    
    def _apply_code_font(self, cell, font_list: List[str], layout_style: str, code_config: Dict):
        """Apply monospace font for code content."""
        try:
            mono_fonts = ['Courier New', 'Consolas', 'Monaco', 'monospace']
            if layout_style in code_config.get('layout_config', {}):
                code_layout = code_config['layout_config']
                if 'mono_font' in code_layout:
                    mono_font = code_layout['mono_font']['family']
                    mono_fonts = [mono_font] + mono_fonts
            
            # Apply monospace font list with fallbacks
            cell.get_text().set_fontfamily(mono_fonts + font_list)
            cell.get_text().set_style('normal')
        except Exception:
            # Fallback to normal font if monospace configuration fails
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
    
    def _apply_normal_font(self, cell, font_list: List[str]):
        """Apply normal font styling."""
        # Ensure font family is applied
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
            raise ValueError(f"Palette '{palette_name}' not found. Available: {list(palettes.keys())}")
        
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
                          font_size: float = None, missing_value_style: str = 'italic') -> None:
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
        
        # Format each cell with unified row heights
        num_rows, num_cols = df.shape
        num_rows += 1  # Include header row
        
        # First pass: calculate maximum lines needed per row
        row_heights = {}
        for (row, col), cell in table.get_celld().items():
            if row not in row_heights:
                row_heights[row] = 1
            
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
            
            # Calculate lines needed for this cell
            line_count = self._calculate_cell_lines(text_value, is_header)
            row_heights[row] = max(row_heights[row], line_count)
        
        # Second pass: apply formatting with consistent row heights
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
            
            # Apply unified cell styling with consistent row height
            max_lines_in_row = row_heights[row]
            self._apply_unified_cell_styling(cell, is_header, text_value, max_lines_in_row)
    
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
    
    def _calculate_cell_lines(self, text_value, is_header: bool, max_width: int = 12) -> int:
        """Calculate number of lines needed for cell content without applying styling.
        
        Delegates to TableContentAnalyzer for consistent logic.
        """
        return TableContentAnalyzer.calculate_cell_lines(
            text_value, is_header, max_width, self._wrap_text_content
        )
    
    def _apply_unified_cell_styling(self, cell, is_header: bool, text_value, max_lines_in_row: int, max_width: int = 12) -> None:
        """Apply unified styling to cells with consistent row height."""
        text_str = str(text_value) if text_value is not None else ""
        
        # Process superscripts before wrapping
        processed_text = self._process_superscripts(text_str)
        
        wrap_width = 10 if is_header else max_width
        
        # Apply text wrapping
        if len(processed_text) > wrap_width:
            wrapped_text = self._wrap_text_content(processed_text, wrap_width)
            cell.get_text().set_text(wrapped_text)
        else:
            cell.get_text().set_text(processed_text)
        
        # Set cell alignment
        cell.get_text().set_horizontalalignment('center')
        cell.get_text().set_verticalalignment('center')
        
        # Apply padding
        cell.set_linewidth(0.5)
        
        # Unified height calculation based on maximum lines in the row
        if is_header:
            cell.get_text().set_weight('bold')
            base_height = 0.08
            height = base_height + (max_lines_in_row - 1) * 0.04
            cell.set_height(max(height, 0.08))
        else:
            base_height = 0.06
            height = base_height + (max_lines_in_row - 1) * 0.03
            cell.set_height(max(height, 0.06))
        
        # Adjust text size if many lines (but consistently for the row)
        if max_lines_in_row > 3:
            current_size = cell.get_text().get_fontsize()
            cell.get_text().set_fontsize(current_size * 0.9)
    
    def _apply_cell_styling(self, cell, is_header: bool, text_value, max_width: int = 12) -> None:
        """Apply additional styling to cells with proper height adjustment for wrapped text."""
        # Apply text wrapping with more reasonable limits
        text_str = str(text_value) if text_value is not None else ""
        
        # Process superscripts before wrapping
        processed_text = self._process_superscripts(text_str)
        
        # More reasonable wrapping - less aggressive for headers
        wrap_width = 10 if is_header else max_width
        wrapped_text = processed_text  # Initialize wrapped_text
        line_count = 1  # Track number of lines
        
        if len(processed_text) > wrap_width:
            wrapped_text = self._wrap_text_content(processed_text, wrap_width)
            cell.get_text().set_text(wrapped_text)
            # Count actual lines in wrapped text
            line_count = len(wrapped_text.split('\n')) if isinstance(wrapped_text, str) else 1
        else:
            cell.get_text().set_text(processed_text)
        
        # Set cell alignment
        cell.get_text().set_horizontalalignment('center')
        cell.get_text().set_verticalalignment('center')
        
        # Apply padding
        cell.set_linewidth(0.5)
        
        # Dynamic cell height based on actual content
        if is_header:
            cell.get_text().set_weight('bold')
            # Calculate height based on line count for headers
            base_height = 0.08
            height = base_height + (line_count - 1) * 0.04  # Add 0.04 per extra line
            cell.set_height(max(height, 0.08))  # Minimum height
        else:
            # Regular cells with dynamic height based on content
            base_height = 0.06
            height = base_height + (line_count - 1) * 0.03  # Smaller increment for regular cells
            cell.set_height(max(height, 0.06))  # Minimum height
            
        # Adjust text size if too many lines
        if line_count > 3:
            current_size = cell.get_text().get_fontsize()
            cell.get_text().set_fontsize(current_size * 0.9)  # Slightly smaller for very long text
    
    def _wrap_text_content(self, text: str, max_width: int = 12) -> str:
        """Wrap text content with reasonable line breaks to prevent cell overflow.
        
        Delegates to TableTextWrapper for consistent logic.
        """
        return TableTextWrapper.wrap_cell_content(text, max_width)
    
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
    
    def _process_superscripts(self, text: str) -> str:
        """Process superscripts in text using the format configuration.
        
        Args:
            text: Original text that may contain superscript markers (^)
            
        Returns:
            Text with superscript markers converted to Unicode superscripts
        """
        return self._process_superscripts_static(text)
    
    @staticmethod
    def _process_superscripts_static(text: str) -> str:
        """Static method to process superscripts in text.
        
        Args:
            text: Original text that may contain superscript markers (^)
            
        Returns:
            Text with superscript markers converted to Unicode superscripts
        """
        # Handle None, NaN, and empty cases
        if text is None:
            return ""
        
        # Convert to string and handle pandas NaN
        try:
            import pandas as pd
            if pd.isna(text):
                return ""
        except (ImportError, TypeError):
            pass
        
        text_str = str(text)
        
        if not text_str or '^' not in text_str:
            return text_str
            
        try:
            # First try with the format configuration system
            from ePy_docs.core._format import SuperscriptFormatter, FormatConfig
            
            # Initialize formatter with configuration
            config = FormatConfig()
            formatter = SuperscriptFormatter(config)
            
            # Process superscripts for matplotlib output (uses Unicode superscripts)
            processed_text = formatter.format_superscripts(text_str, output_format='matplotlib')
            
            return processed_text
            
        except Exception:
            # If formatting fails, use fallback direct mapping
            return CellFormatter._fallback_superscript_processing(text_str)
    
    @staticmethod
    def _fallback_superscript_processing(text: str) -> str:
        """Fallback superscript processing with direct Unicode mapping."""
        if not text or '^' not in text:
            return text
            
        # Direct Unicode superscript mapping
        superscript_map = {
            '^0': '⁰', '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴', 
            '^5': '⁵', '^6': '⁶', '^7': '⁷', '^8': '⁸', '^9': '⁹',
            '^10': '¹⁰', '^11': '¹¹', '^12': '¹²',
            '^n': 'ⁿ', '^x': 'ˣ', '^y': 'ʸ', '^i': 'ⁱ', '^j': 'ʲ', '^k': 'ᵏ',
            '^+': '⁺', '^-': '⁻', '^=': '⁼'
        }
        
        # Apply replacements (longer patterns first to avoid conflicts)
        result = text
        for pattern in sorted(superscript_map.keys(), key=len, reverse=True):
            result = result.replace(pattern, superscript_map[pattern])
            
        return result


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
    
    def _process_superscripts_static(self, text: str) -> str:
        """Process superscripts in text - delegate to CellFormatter static method."""
        return CellFormatter._process_superscripts_static(text)
    
    def create_table_image(self, data: Union[pd.DataFrame, List[List]], 
                          title: str = None, layout_style: str = "corporate",
                          output_dir: str = None, table_number: int = 1,
                          width_inches: float = None,
                          document_type: str = None,
                          highlight_columns: Optional[Union[str, List[str]]] = None,
                          colored: bool = False,
                          palette_name: Optional[str] = None) -> str:
        """Create table image and return the file path."""
        # Setup matplotlib and get configured font list
        configured_font_list = self._setup_matplotlib(layout_style)
        
        # Convert data to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Validate required parameter
        if not document_type:
            raise ValueError("Missing required parameter 'document_type'")
        
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
            
            # Apply formatting - use the configured font list from matplotlib setup
            cell_formatter = CellFormatter(
                FontManager(self._config_manager),
                ColorManager(self._config_manager)
            )
            
            # Use the font list that was configured in matplotlib setup
            font_list = configured_font_list if configured_font_list else self._get_font_list(font_family, font_config)
            cell_formatter.format_table_cells(
                table, df, font_list, font_config, layout_style, code_config
            )
            
            # CRITICAL: Apply fonts to the entire figure (including title and all text elements)
            from ePy_docs.core._images import apply_fonts_to_figure
            apply_fonts_to_figure(fig, font_list)
            
            # Apply colors if requested
            if highlight_columns or colored:
                color_manager = ColorManager(self._config_manager)
                color_manager.apply_table_colors(
                    table, df, style_config, colors_config,
                    highlight_columns, palette_name
                )
            
            # Skip adding title to figure - use caption in markdown instead
            # This avoids duplicate titles (one in image, one in caption)
            
            # Save image
            output_path = self._save_image(fig, output_dir, table_number, title, document_type, colors_config)
            
            return output_path
            
        finally:
            # Clean up matplotlib resources thoroughly
            try:
                plt.close(fig)
                # Force garbage collection to free memory
                import gc
                gc.collect()
            except Exception:
                pass  # Ignore cleanup errors
    
    def _setup_matplotlib(self, layout_style: str):
        """Setup matplotlib with optimal settings and error handling."""
        try:
            # Ensure matplotlib uses non-interactive backend
            import matplotlib
            matplotlib.use('Agg', force=True)
            
            # Configure fonts from layout configuration
            font_list = setup_matplotlib_fonts(layout_style)
            
            # Explicitly enable font fallback settings
            from matplotlib import rcParams
            
            # Set the font family list from configuration - NO hardcoded fallbacks
            if font_list and isinstance(font_list, list):
                rcParams['font.sans-serif'] = font_list
            else:
                raise ValueError("No font configuration available from layout")
                
            rcParams['font.family'] = 'sans-serif'
            
            # CRITICAL: Enable font fallback to avoid errors
            rcParams['svg.fonttype'] = 'none'  # Use fonts as text, not paths
            rcParams['pdf.fonttype'] = 42  # Use TrueType fonts in PDF
            rcParams['ps.fonttype'] = 42   # PostScript fonts
            
            # Memory and performance settings
            rcParams['figure.max_open_warning'] = 0  # Disable warnings about too many figures
            rcParams['axes.unicode_minus'] = False   # Prevent Unicode minus issues
            
            # Ensure matplotlib uses proper font fallback policy
            import matplotlib.font_manager as fm
            if hasattr(fm, 'fontManager'):
                # Refresh font manager to apply changes - but safely
                try:
                    fm.fontManager._rebuild()
                except (AttributeError, OSError, RuntimeError):
                    pass  # Ignore font manager errors
            
            return font_list if font_list else ['Arial', 'sans-serif']
            
        except Exception as e:
            # No hardcoded fallbacks - raise error to force proper configuration
            raise ValueError(f"Font setup failed for layout '{layout_style}': {e}")
    
    def _create_matplotlib_table(self, ax, df: pd.DataFrame, font_config: Dict, style_config: Dict, colors_config: Dict = None):
        """Create the basic matplotlib table with layout-specific styling."""
        # Prepare data for table with superscript processing
        processed_headers = [self._process_superscripts_static(str(col)) for col in df.columns.tolist()]
        processed_data = []
        
        for row_idx in range(len(df)):
            processed_row = []
            for col_idx in range(len(df.columns)):
                cell_value = df.iloc[row_idx, col_idx]
                original_cell = str(cell_value) if cell_value is not None else ""
                processed_cell = self._process_superscripts_static(original_cell)
                processed_row.append(processed_cell)
            processed_data.append(processed_row)
        
        # Ensure matplotlib can handle Unicode superscripts
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        
        # Set font that supports Unicode superscripts
        unicode_fonts = ['DejaVu Sans', 'Arial Unicode MS', 'Lucida Grande', 'Liberation Sans']
        
        for font in unicode_fonts:
            try:
                rcParams['font.family'] = font
                break
            except:
                continue
        
        rcParams['axes.unicode_minus'] = False
        
        # Create table with processed data
        table = ax.table(
            cellText=processed_data,  # Processed data rows
            colLabels=processed_headers,  # Processed header row
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        
        # Ensure Unicode fonts are applied to all cells with superscripts
        for (row, col), cell in table.get_celld().items():
            cell_text = cell.get_text().get_text()
            if any(ord(c) > 127 for c in cell_text):
                # Force Unicode font on cells with superscript characters
                cell.get_text().set_fontname('DejaVu Sans')
        
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
        
        # CRITICAL: Apply font family to each cell individually
        # Get font list from configuration
        if 'primary' not in font_config:
            raise ValueError(
                f"font_config must have 'primary' key. Found: {list(font_config.keys())}"
            )
        
        font_list = [font_config['primary']]
        if 'fallback' in font_config:
            font_list.append(font_config['fallback'])
        
        # Apply font family to all cells
        for (row, col), cell in table.get_celld().items():
            cell.get_text().set_fontfamily(font_list)
        
        # Unified scaling for all tables - let individual cell heights handle wrapping
        table.scale(1.0, 1.2)  # Standard scaling for all content
        
        # Apply layout-specific colors
        self._apply_table_layout_colors(table, df, colors_config)
        
        return table
    
    def _apply_table_layout_colors(self, table, df: pd.DataFrame, colors_config: Dict = None):
        """Apply layout-specific colors to table headers and cells."""
        if not colors_config:
            return
        
        if 'palette' not in colors_config:
            return
        
        palette = colors_config['palette']
        
        # Get primary color for headers
        # Validate required colors exist in palette
        required_colors = ['table_header', 'table_header_text', 'table_stripe', 'table_background']
        missing_colors = [c for c in required_colors if c not in palette]
        if missing_colors:
            raise ValueError(
                f"Palette must have {required_colors}. Missing: {missing_colors}"
            )
        
        # Get table header colors
        header_color = palette['table_header']
        header_text_color = palette['table_header_text']
        
        if not isinstance(header_color, list) or len(header_color) < 3:
            raise ValueError(
                f"table_header color must be list with at least 3 RGB values. Got: {header_color}"
            )
        
        if not isinstance(header_text_color, list) or len(header_text_color) < 3:
            raise ValueError(
                f"table_header_text color must be list with at least 3 RGB values. Got: {header_text_color}"
            )
        
        header_rgb = [c/255.0 for c in header_color[:3]]  # Convert to matplotlib format
        header_text_rgb = [c/255.0 for c in header_text_color[:3]]
        
        # Get stripe color for alternate rows
        stripe_color = palette['table_stripe']
        stripe_text_color = palette.get('table_stripe_text', palette.get('page_text', [0, 0, 0]))
        
        if not isinstance(stripe_color, list) or len(stripe_color) < 3:
            raise ValueError(
                f"table_stripe color must be list with at least 3 RGB values. Got: {stripe_color}"
            )
        
        if not isinstance(stripe_text_color, list) or len(stripe_text_color) < 3:
            raise ValueError(
                f"table_stripe_text color must be list with at least 3 RGB values. Got: {stripe_text_color}"
            )
        
        stripe_rgb = [c/255.0 for c in stripe_color[:3]]
        stripe_text_rgb = [c/255.0 for c in stripe_text_color[:3]]
        
        # Get background color for regular rows
        background_color = palette['table_background']
        background_text_color = palette.get('table_background_text', palette.get('page_text', [0, 0, 0]))
        
        if not isinstance(background_color, list) or len(background_color) < 3:
            raise ValueError(
                f"table_background color must be list with at least 3 RGB values. Got: {background_color}"
            )
        
        if not isinstance(background_text_color, list) or len(background_text_color) < 3:
            raise ValueError(
                f"table_background_text color must be list with at least 3 RGB values. Got: {background_text_color}"
            )
        
        background_rgb = [c/255.0 for c in background_color[:3]]
        background_text_rgb = [c/255.0 for c in background_text_color[:3]]
        
        # Apply header colors
        num_cols = len(df.columns)
        for col in range(num_cols):
            header_cell = table[(0, col)]
            header_cell.set_facecolor(header_rgb)
            header_cell.get_text().set_color(header_text_rgb)
        
        # Apply alternating row colors with text colors
        num_rows = len(df)
        for row in range(1, num_rows + 1):  # Skip header row (0)
            if row % 2 == 0:  # Even rows - apply stripe
                for col in range(num_cols):
                    cell = table[(row, col)]
                    cell.set_facecolor(stripe_rgb)
                    cell.get_text().set_color(stripe_text_rgb)
            else:  # Odd rows - apply background
                for col in range(num_cols):
                    cell = table[(row, col)]
                    cell.set_facecolor(background_rgb)
                    cell.get_text().set_color(background_text_rgb)
    
    def _calculate_width(self, df: pd.DataFrame, style_config: Dict) -> float:
        """Calculate optimal table width based on content and configuration.
        
        Delegates to TableContentAnalyzer for consistent logic.
        
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
        return TableContentAnalyzer.calculate_optimal_width(df, base_width, style_config)
    
    def _calculate_height(self, df: pd.DataFrame, style_config: Dict) -> float:
        """Calculate optimal table height based on content and wrapping.
        
        Delegates to TableContentAnalyzer for consistent logic.
        """
        base_row_height = style_config.get('row_height_in', 0.3)
        return TableContentAnalyzer.calculate_optimal_height(df, base_row_height)
    
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
    
    def _save_image(self, fig, output_dir: str, table_number: int, title: str = None, document_type: str = 'report', colors_config: Dict = None) -> str:
        """Save the figure and return the file path."""
        if not output_dir:
            abs_dirs = get_absolute_output_directories(document_type)
            if 'tables' not in abs_dirs:
                raise ValueError("Missing 'tables' directory in output configuration")
            output_dir = abs_dirs['tables']
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename - simplified to just table_number
        # Title information is preserved in the caption/markdown
        filename = f"table_{table_number}.png"
        
        output_path = Path(output_dir) / filename
        
        # Get background color from palette (default to white if not available)
        bg_color = 'white'
        if colors_config and 'palette' in colors_config:
            palette = colors_config['palette']
            if 'page_background' in palette:
                bg_rgb = palette['page_background']
                if isinstance(bg_rgb, list) and len(bg_rgb) >= 3:
                    # Convert RGB [0-255] to matplotlib format [0-1]
                    bg_color = [c/255.0 for c in bg_rgb[:3]]
        
        # Save with high quality
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.1,
            facecolor=bg_color,
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
    
    def _escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Text with LaTeX special characters escaped
        """
        if not text:
            return text
            
        # Escape special LaTeX characters
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '_': '\\_',
            '^': '\\textasciicircum{}',
            '~': '\\textasciitilde{}',
        }
        
        result = text
        # Handle backslash first to avoid escaping our escape sequences
        if '\\' in result:
            result = result.replace('\\', replacements['\\'])
        
        # Then handle other characters
        for char, replacement in replacements.items():
            if char != '\\' and char in result:
                result = result.replace(char, replacement)
        
        return result
    
    def generate_table_markdown(self, image_paths: Union[str, List[str]], 
                               caption: str = None, table_number: int = 1,
                               document_columns: int = 1, label: str = None) -> str:
        """Generate markdown content for table(s).
        
        Args:
            image_paths: Path or list of paths to table images
            caption: Table caption
            table_number: Table number for referencing
            document_columns: Total number of columns in the document layout
            label: Custom label for cross-referencing. If None, uses table_number.
        """
        
        if isinstance(image_paths, str):
            return self._generate_single_table_markdown(image_paths, caption, table_number, 
                                                       document_columns, label=label)
        else:
            return self._generate_split_table_markdown(image_paths, caption, table_number,
                                                       document_columns, label=label)
    
    def _generate_single_table_markdown(self, image_path: str, caption: str, table_number: int,
                                       document_columns: int = 1, label: str = None) -> str:
        """Generate markdown for a single table in Quarto format.
        
        Args:
            image_path: Path to table image
            caption: Table caption
            table_number: Table number
            document_columns: Total columns in document
            label: Custom label for cross-referencing. If None, uses table_number.
        """
        # Extract relative path for markdown
        rel_path = self._get_relative_path(image_path)
        
        # Standard Quarto markdown
        width_str = "100%"  # Full width for single-column documents
        
        # Quarto format with figure reference and width
        label_str = f"#tbl-{label}" if label else f"#tbl-{table_number}"
        if caption:
            return f"\n\n![{caption}]({rel_path}){{width={width_str} {label_str}}}\n\n"
        else:
            return f"\n\n![]({rel_path}){{width={width_str} {label_str}}}\n\n"
    
    def _generate_split_table_markdown(self, image_paths: List[str], caption: str, table_number: int,
                                      document_columns: int = 1, label: str = None) -> str:
        """Generate markdown for split tables in Quarto format.
        
        Args:
            image_paths: List of paths to table images
            caption: Table caption
            table_number: Starting table number
            document_columns: Total columns in document
            label: Custom label for cross-referencing. If None, uses table_number.
                  For split tables, appends part number (e.g., 'results-1', 'results-2')
        """
        markdown_parts = []
        num_parts = len(image_paths)
        
        # Full width for single-column documents
        width_str = "100%"
        
        for i, image_path in enumerate(image_paths):
            rel_path = self._get_relative_path(image_path)
            
            # Quarto format with figure reference and width
            # Use custom label with part number if provided, otherwise use table_number
            if label:
                label_str = f"#tbl-{label}-{i+1}" if num_parts > 1 else f"#tbl-{label}"
            else:
                label_str = f"#tbl-{table_number + i}"
            
            if caption:
                part_caption = f"{caption} - Parte {i+1}/{num_parts}"
                markdown_parts.append(f"![{part_caption}]({rel_path}){{width={width_str} {label_str}}}")
            else:
                markdown_parts.append(f"![]({rel_path}){{width={width_str} {label_str}}}")
        
        # Add TWO line breaks before first table for proper PDF spacing
        return "\n\n" + "\n\n".join(markdown_parts) + "\n\n"
    
    def _get_relative_path(self, image_path: str) -> str:
        """Convert absolute path to relative path for markdown, optimized for new structure."""
        path = Path(image_path)
        
        try:
            # Get the filename
            filename = path.name
            
            # Try to make relative to current directory
            rel_path = path.relative_to(Path.cwd())
            rel_str = str(rel_path).replace('\\', '/')
            
            # New structure handling: results/document_type/tables/filename
            # QMD is in results/document_type/, so table path should be tables/filename
            if 'results/' in rel_str and '/tables/' in rel_str:
                # Extract the part after /tables/
                tables_index = rel_str.find('/tables/')
                return f"tables/{filename}"
            elif 'results/' in rel_str and '/figures/' in rel_str:
                # Extract the part after /figures/
                figures_index = rel_str.find('/figures/')
                return f"figures/{filename}"
            elif rel_str.startswith('results/'):
                # Legacy handling - if old structure, try to maintain compatibility
                if rel_str.count('/') == 1:  # results/filename
                    return f"tables/{filename}"
                else:
                    # Extract document type and assume it's a table
                    parts = rel_str.split('/')
                    if len(parts) >= 3:
                        return f"tables/{filename}"
            
            return rel_str
            
        except ValueError:
            # If can't make relative, assume it's a table
            return f"tables/{path.name}"


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
                                       document_type: str = None,
                                       document_columns: int = 1,
                                       max_rows_per_table: Union[int, List[int], None] = None,
                                       highlight_columns: Optional[Union[str, List[str]]] = None,
                                       colored: bool = False,
                                       palette_name: Optional[str] = None,
                                       label: str = None) -> Tuple[str, Union[str, List[str]], int]:
        """
        Main public API for table processing.
        
        Args:
            df: DataFrame containing table data
            caption: Table caption/title
            layout_style: Layout style name
            output_dir: Output directory for table image
            table_number: Table number for counter
            columns: Width specification for multi-column layouts
            document_type: Required - Type of document (paper, report, book, notebook)
            document_columns: Total number of columns in the document layout
            max_rows_per_table: Maximum rows per table before splitting (int or list)
            highlight_columns: Columns to highlight with color gradient
            colored: Whether to apply coloring to table
            palette_name: Color palette name for highlighting
            label: Custom label for cross-referencing (e.g., 'results'). Will be formatted as 'tbl-{label}'.
                   If None, uses table_number (e.g., 'tbl-1')
            
        Returns:
            Tuple of (markdown_content, image_path_or_paths, new_counter)
        """
        try:
            # Validate required parameter
            if not document_type:
                raise ValueError("Missing required parameter 'document_type'")
            
            # Calculate width from columns parameter
            width_inches = TableContentAnalyzer.calculate_width_from_columns(columns, document_type)
            
            # Check if table needs to be split
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
                        width_inches, max_rows_per_table, document_type,
                        document_columns, highlight_columns, colored, palette_name, label=label
                    )
            
            return self._process_single_table(
                df, caption, layout_style, output_dir, table_number, 
                width_inches, document_type, document_columns,
                highlight_columns, colored, palette_name, label=label
            )
                
        except Exception as e:
            # Error handling with informative message
            raise RuntimeError(f"Table processing failed: {e}")
    
    def _process_single_table(self, df: pd.DataFrame, caption: str, layout_style: str,
                             output_dir: str, table_number: int, width_inches: Optional[float],
                             document_type: str,
                             document_columns: int, highlight_columns: Optional[Union[str, List[str]]],
                             colored: bool, palette_name: Optional[str], label: str = None) -> Tuple[str, str, int]:
        """Process a single table."""
        # Generate table image
        image_path = self._image_renderer.create_table_image(
            df, caption, layout_style, output_dir, table_number, width_inches,
            document_type, highlight_columns, colored, palette_name
        )
        
        # Generate markdown
        markdown_content = self._markdown_generator.generate_table_markdown(
            image_path, caption, table_number, document_columns, label=label
        )
        
        return markdown_content, image_path, table_number
    
    def _process_split_table(self, df: pd.DataFrame, caption: str, layout_style: str,
                            output_dir: str, table_number: int, width_inches: Optional[float],
                            max_rows_per_table: Union[int, List[int]],
                            document_type: str,
                            document_columns: int, highlight_columns: Optional[Union[str, List[str]]],
                            colored: bool, palette_name: Optional[str], label: str = None) -> Tuple[str, List[str], int]:
        """Process a table that needs to be split."""
        # Split DataFrame into chunks using centralized logic from _data.py
        from ePy_docs.core._data import TablePreparation
        table_chunks = TablePreparation.split_for_rendering(df, max_rows_per_table)
        
        # Generate images for each chunk
        image_paths = []
        current_table_number = table_number
        
        for i, chunk in enumerate(table_chunks):
            part_caption = f"{caption} (Parte {i+1})" if caption else None
            
            image_path = self._image_renderer.create_table_image(
                chunk, part_caption, layout_style, output_dir, 
                current_table_number, width_inches,
                document_type, highlight_columns, colored, palette_name
            )
            
            image_paths.append(image_path)
            if i < len(table_chunks) - 1:  # Only increment if not last chunk
                current_table_number += 1
        
        # Generate combined markdown
        markdown_content = self._markdown_generator.generate_table_markdown(
            image_paths, caption, table_number, document_columns, label=label
        )
        
        return markdown_content, image_paths, current_table_number


# ============================================================================
# GLOBAL ORCHESTRATOR INSTANCE
# ============================================================================

table_orchestrator = TableOrchestrator()
