"""Tables module - Consolidated table processing and rendering.

This module handles all table operations including:
- Table configuration loading
- Category detection for auto-highlighting  
- Table image generation with matplotlib
- Markdown content generation
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
from typing import Dict, Any, Union, List, Optional, Tuple

from ePy_docs.core._data import (
    load_cached_files, _safe_get_nested,
    calculate_table_column_width, calculate_table_row_height,
    detect_table_category, prepare_dataframe_for_table
)
from ePy_docs.core._config import get_absolute_output_directories
from ePy_docs.core._images import convert_rgb_to_matplotlib, get_palette_color_by_tone, setup_matplotlib_fonts


# ============================================================================
# CONFIGURATION AND UTILITIES
# ============================================================================

def _get_tables_config() -> Dict[str, Any]:
    """Load centralized table configuration (internal helper).
    
    Returns:
        Complete tables configuration dictionary.
    """
    from ePy_docs.core._config import get_config_section, clear_global_cache
    
    config = get_config_section('tables')
    
    # If category_rules is missing, clear cache and reload
    # This handles the case where config files were updated
    if 'category_rules' not in config or not config.get('category_rules'):
        clear_global_cache()
        config = get_config_section('tables')
    
    return config


def _is_missing_table_value(text_value) -> bool:
    """Detect if a value should be displayed in italic for being missing."""
    if pd.isna(text_value):
        return True
    
    text_str = str(text_value).strip().lower()
    missing_indicators = ['', 'nan', 'none', 'null', '-', '--', '---', 'n/a', 'na']
    return text_str in missing_indicators


# ============================================================================
# FONT CONFIGURATION
# ============================================================================

def _configure_table_cell_font(cell, text_value, is_header: bool, font_list: List[str], 
                                layout_style: str, code_config: Dict):
    """Configure specific font for each cell based on its content."""
    is_code_content = False
    if not is_header and text_value is not None:
        cell_str = str(text_value)
        code_indicators = ['def ', 'function', 'class ', '()', '{}', '[]', 'import ', 'from ', '=', '==']
        code_count = sum(1 for indicator in code_indicators if indicator in cell_str)
        is_code_content = code_count >= 2
    
    if is_header:
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')
    elif _is_missing_table_value(text_value):
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('italic')
    elif is_code_content:
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
        except:
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
    else:
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')


def _auto_adjust_table_font_size(cell, original_font_size: float, num_columns: Optional[int] = None, 
                                  table_width: Optional[float] = None, is_header: bool = False) -> float:
    """Intelligently adjust font size based on content and table density."""
    cell_text = cell.get_text().get_text()
    
    if '\n' in cell_text:
        lines = cell_text.split('\n')
        max_line_length = max(len(line) for line in lines)
        line_count = len(lines)
    else:
        max_line_length = len(cell_text)
        line_count = 1
    
    length_reduction = 1.0
    if is_header:
        if max_line_length > 25:
            length_reduction = min(0.85, max(0.75, 25 / max_line_length))
        elif max_line_length > 15:
            length_reduction = min(0.90, max(0.85, 15 / max_line_length))
        elif max_line_length > 10:
            length_reduction = 0.95
        elif max_line_length > 5:
            length_reduction = 1.0
    else:
        if max_line_length > 25:
            length_reduction = min(0.78, max(0.65, 25 / max_line_length))
        elif max_line_length > 15:
            length_reduction = min(0.85, max(0.78, 15 / max_line_length))
        elif max_line_length > 10:
            length_reduction = 0.90
        elif max_line_length > 5:
            length_reduction = 0.95
    
    density_reduction = 1.0
    if num_columns:
        if num_columns > 12:
            density_reduction = 0.78
        elif num_columns > 8:
            density_reduction = 0.85
        elif num_columns > 5:
            density_reduction = 0.90
        elif num_columns > 3:
            density_reduction = 0.95
    
    multiline_reduction = 1.0
    if line_count > 1:
        multiline_reduction = max(0.82, 1.0 - (line_count - 1) * 0.12)
    
    special_chars_reduction = 1.0
    special_chars = ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '·', '×', '÷', '±', '≤', '≥', 'SRSS']
    if any(char in cell_text for char in special_chars):
        special_chars_reduction = 0.93
    
    formatting_reduction = 1.0
    complex_chars = ['(', ')', '[', ']', '{', '}', '@', '#', '$', '%']
    complex_count = sum(1 for char in complex_chars if char in cell_text)
    if complex_count > 2:
        formatting_reduction = max(0.85, 1.0 - complex_count * 0.03)
    elif complex_count > 0:
        formatting_reduction = 0.93
    
    final_reduction = (length_reduction * density_reduction * multiline_reduction * 
                      special_chars_reduction * formatting_reduction)
    final_reduction = max(0.60, final_reduction)
    current_font_size = original_font_size * final_reduction
    cell.set_fontsize(current_font_size)
    return current_font_size


# ============================================================================
# TEXT FORMATTING
# ============================================================================

def _apply_table_header_multiline(header_text: str, max_length: int = 12) -> str:
    """Apply intelligent line breaks to headers to avoid font reduction."""
    if len(header_text) <= 8:
        return header_text
        
    if '/' in header_text:
        parts = header_text.split('/')
        if len(parts) == 2 and max(len(parts[0]), len(parts[1])) <= max_length:
            return f"{parts[0]}/\n{parts[1]}"
        elif len(parts) > 2:
            first_part = parts[0]
            remaining = '/'.join(parts[1:])
            if len(first_part) <= max_length and len(remaining) <= max_length:
                return f"{first_part}/\n{remaining}"
    
    if '(' in header_text and ')' in header_text:
        paren_start = header_text.find('(')
        if paren_start > 0:
            main_part = header_text[:paren_start].strip()
            unit_part = header_text[paren_start:].strip()
            if len(main_part) <= max_length and len(unit_part) <= max_length:
                return f"{main_part}\n{unit_part}"
    
    if len(header_text) <= max_length:
        return header_text
    
    if ' ' in header_text:
        words = header_text.split(' ')
        if len(words) == 2 and max(len(words[0]), len(words[1])) <= max_length:
            return f"{words[0]}\n{words[1]}"
        elif len(words) > 2:
            for i in range(1, len(words)):
                first_part = ' '.join(words[:i])
                second_part = ' '.join(words[i:])
                if len(first_part) <= max_length and len(second_part) <= max_length:
                    return f"{first_part}\n{second_part}"
    
    for separator in ['-', '–', '—']:
        if separator in header_text:
            parts = header_text.split(separator, 1)
            if len(parts) == 2 and max(len(parts[0]), len(parts[1])) <= max_length:
                return f"{parts[0]}{separator}\n{parts[1]}"
    
    import re
    camel_pattern = r'([a-z])([A-Z])'
    if re.search(camel_pattern, header_text):
        matches = list(re.finditer(camel_pattern, header_text))
        for match in matches:
            split_pos = match.end() - 1
            first_part = header_text[:split_pos]
            second_part = header_text[split_pos:]
            if len(first_part) <= max_length and len(second_part) <= max_length:
                return f"{first_part}\n{second_part}"
    
    return header_text


def _detect_format_code_content(cell_value, code_config: Dict, available_languages: List[str]) -> str:
    """Detect and format code content in table cells."""
    cell_str = str(cell_value)
    
    code_patterns = [
        '(', ')', '{', '}', '[', ']',
        'def ', 'function', 'class ',
        '=', '==', '!=', '>=', '<=',
        '\n',
    ]
    
    pattern_count = sum(1 for pattern in code_patterns if pattern in cell_str)
    
    if pattern_count >= 3 or any(lang in cell_str.lower() for lang in available_languages[:5]):
        formatting_config = code_config.get('formatting', {})
        return cell_str
    
    return cell_str


# ============================================================================
# DIMENSION CALCULATION
# ============================================================================

# ============================================================================
# CORE IMAGE GENERATION
# ============================================================================

def _load_table_configuration(layout_style: str, document_type: str) -> Tuple[Dict, Dict, Dict, Dict, Dict, str]:
    """Load all configuration sections for table generation (internal helper).
    
    Args:
        layout_style: Layout style name.
        document_type: Document type for output directory.
        
    Returns:
        Tuple of (style_config, size_config, format_config, display_config, alignment_config, output_directory).
    """
    config = _get_tables_config()
    
    if 'layout_config' not in config:
        raise ValueError(f"Configuration for tables not found (missing layout_config)")
    
    style_config = config['layout_config']
    size_config = config.get('font_sizes', {})
    format_config = config.get('formatting', {})
    display_config = config.get('display', {})
    
    # Provide default filename_format if missing
    if 'filename_format' not in format_config:
        format_config = {**format_config, 'filename_format': 'table_{counter}.{ext}'}
    
    # Get output directory
    output_dirs = get_absolute_output_directories(document_type=document_type)
    output_directory = output_dirs['tables']
    
    # Get alignment configuration
    from ePy_docs.core._config import get_config_section
    tables_config = get_config_section('tables', layout_name=layout_style)
    
    if 'layout_config' not in tables_config:
        raise RuntimeError(f"Layout configuration missing for layout_style '{layout_style}'")
    
    layout_config = tables_config['layout_config']
    if 'alignment' not in layout_config:
        raise RuntimeError(f"Alignment configuration missing for layout_style '{layout_style}'")
    
    alignment_config = layout_config['alignment']
    
    return style_config, size_config, format_config, display_config, alignment_config, output_directory


def _create_table_image(data: Union[pd.DataFrame, List[List]], 
                        title: str = None, output_dir: str = None, 
                        filename: str = None, layout_style: str = "corporate", 
                        highlight_columns: Optional[List[str]] = None,
                        palette_name: Optional[str] = None,
                        document_type: str = "report") -> str:
    """Create table as image using centralized configuration (internal).
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Optional table title.
        output_dir: Output directory path.
        filename: Output filename.
        layout_style: One of 8 universal layout styles.
        highlight_columns: List of column names (or single string) to highlight with colors.
        palette_name: Color palette name for highlights.
        document_type: Document type for output directory resolution.
        
    Returns:
        Path to generated image file.
        
    Raises:
        ValueError: If layout_style not found in configuration.
    """
    # Load all configuration
    style_config, size_config, format_config, display_config, alignment_config, output_directory = \
        _load_table_configuration(layout_style, document_type)
    
    # Get tables configuration for category detection
    tables_config = _get_tables_config()
    
    # Normalize highlight_columns to list
    if highlight_columns is not None and isinstance(highlight_columns, str):
        highlight_columns = [highlight_columns]
    
    # Prepare DataFrame with formatting
    df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
    
    # Handle MultiIndex by converting to columns
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()
    elif df.index.name is not None:
        # Single index with a name - also convert to column
        df = df.reset_index()
    
    # Auto-detect category if no highlight_columns specified
    detected_category = None
    if highlight_columns is None:
        detected_category, auto_highlight_columns = detect_table_category(df, tables_config)
        if auto_highlight_columns:
            highlight_columns = auto_highlight_columns
    
    # Apply superscript formatting
    from ePy_docs.core._format import format_superscripts
    for col in df.columns:
        df[col] = df[col].apply(lambda x: format_superscripts(str(x), 'matplotlib'))
    
    # Generate the actual table image
    return _generate_table_image(df, title, output_dir, filename, 
                                style_config, size_config, 
                                format_config, display_config, highlight_columns, 
                                palette_name, layout_style, alignment_config, 
                                output_directory, detected_category)


def _load_colors_configuration(layout_style: str) -> Dict:
    """Load color configuration for specific layout (internal helper).
    
    Args:
        layout_style: Layout style name.
        
    Returns:
        Complete colors configuration dictionary.
    """
    from ePy_docs.core._colors import get_colors_config
    from ePy_docs.core._config import get_config_section
    
    # Get colors from specific layout file
    layout_colors_section = get_config_section('colors', layout_name=layout_style)
    
    # Get global palettes for color lookups
    global_colors_config = get_colors_config()
    
    # Merge configurations
    colors_config = {
        'palettes': global_colors_config.get('palettes', {}),
        'layout_config': layout_colors_section.get('layout_config', {})
    }
    
    return colors_config


def _apply_table_colors(table, df: pd.DataFrame, style_config: Dict, 
                        colors_config: Dict, layout_style: str,
                        highlight_columns: Optional[List[str]] = None,
                        palette_name: Optional[str] = None,
                        detected_category: Optional[str] = None) -> None:
    """Apply colors to table (headers, rows, borders, highlights) (internal helper).
    
    Args:
        table: Matplotlib table object.
        df: DataFrame with table data.
        style_config: Style configuration.
        colors_config: Colors configuration.
        layout_style: Layout style name.
        highlight_columns: Columns to highlight.
        palette_name: Palette for highlights.
        detected_category: Detected table category for header color selection.
    """
    num_rows, num_cols = df.shape
    
    # Get layout colors
    if 'layout_config' in colors_config and colors_config['layout_config']:
        layout_colors = colors_config['layout_config']
        default_palette_name = layout_colors.get('default_palette', 'neutrals')
        table_config = layout_colors.get('tables', {})
    else:
        default_palette_name = 'neutrals'
        table_config = {}
    
    # Apply header colors - use detected category if available
    header_configs = table_config.get('header', {})
    if detected_category and detected_category in header_configs:
        header_config = header_configs[detected_category]
    else:
        header_config = header_configs.get('default', {
            'palette': default_palette_name, 
            'tone': 'primary'
        })
    
    header_color = get_palette_color_by_tone(
        header_config['palette'], 
        header_config['tone']
    )
    
    for i in range(num_cols):
        cell = table[(0, i)]
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
        cell.set_facecolor(header_color)
    
    # Apply alternating row colors
    if style_config['styling']['alternating_rows']:
        alt_row_config = table_config.get('alt_row', {
            'palette': default_palette_name,
            'tone': 'tertiary'
        })
        alt_row_color = get_palette_color_by_tone(
            alt_row_config['palette'],
            alt_row_config['tone']
        )
        for i in range(1, num_rows + 1):
            if i % 2 == 0:
                for j in range(num_cols):
                    table[(i, j)].set_facecolor(alt_row_color)
    
    # Apply column highlighting
    if highlight_columns:
        if not palette_name:
            palette_name = 'blues'
        
        if palette_name not in colors_config['palettes']:
            pass  # Skip if palette not found
        else:
            palette = colors_config['palettes'][palette_name]
            
            # Build gradient colors
            gradient_colors = []
            for tone in ['primary', 'secondary', 'tertiary', 'quaternary', 'quinary', 'senary']:
                if tone in palette:
                    gradient_colors.append(convert_rgb_to_matplotlib(palette[tone]))
            
            if len(gradient_colors) >= 2:
                for col_name in highlight_columns:
                    # Find matching columns by partial match (case-insensitive)
                    matching_cols = [col for col in df.columns if col_name.lower() in col.lower()]
                    
                    for matched_col in matching_cols:
                        col_index = df.columns.get_loc(matched_col)
                        
                        # Extract numerical values
                        col_values = []
                        for row_index in range(1, num_rows + 1):
                            df_row_index = row_index - 1
                            if df_row_index < len(df):
                                cell_value = df.iloc[df_row_index, col_index]
                                if pd.notna(cell_value):
                                    try:
                                        col_values.append(float(cell_value))
                                    except (ValueError, TypeError):
                                        col_values.append(0.0)
                                else:
                                    col_values.append(0.0)
                            else:
                                col_values.append(0.0)
                        
                        # Apply gradient
                        valid_values = [v for v in col_values if not pd.isna(v)]
                        if valid_values:
                            min_val = min(valid_values)
                            max_val = max(valid_values)
                            
                            for i, row_index in enumerate(range(1, num_rows + 1)):
                                if i < len(col_values):
                                    current_value = col_values[i]
                                    
                                    if max_val != min_val and not pd.isna(current_value):
                                        normalized_value = (current_value - min_val) / (max_val - min_val)
                                        color_index = int(normalized_value * (len(gradient_colors) - 1))
                                        color_index = max(0, min(color_index, len(gradient_colors) - 1))
                                        cell_color = gradient_colors[color_index]
                                    else:
                                        cell_color = gradient_colors[len(gradient_colors) // 2]
                                    
                                    table[(row_index, col_index)].set_facecolor(cell_color)
    
    # Apply border colors
    border_config = table_config.get('border', {
        'palette': default_palette_name,
        'tone': 'secondary'
    })
    border_color = get_palette_color_by_tone(
        border_config['palette'],
        border_config['tone']
    )
    for key, cell in table.get_celld().items():
        cell.set_linewidth(style_config['styling']['grid_width'])
        cell.set_edgecolor(border_color)


def _format_and_style_table_cells(table, df: pd.DataFrame, font_list: List[str],
                                   font_size_header: float, font_size_content: float,
                                   style_config: Dict, alignment_config: Dict,
                                   layout_style: str, code_config: Dict) -> None:
    """Format text and apply styling to all table cells (internal helper).
    
    Args:
        table: Matplotlib table object.
        df: DataFrame with table data.
        font_list: Font priority list.
        font_size_header: Header font size.
        font_size_content: Content font size.
        style_config: Style configuration.
        alignment_config: Alignment configuration.
        layout_style: Layout style name.
        code_config: Code configuration.
    """
    num_rows, num_cols = df.shape
    table_width = style_config['styling']['width_inches']
    base_cell_padding = style_config['styling']['cell_padding']  # Fixed: removed /1000.0 division bug
    
    # Format headers (row 0)
    for j in range(num_cols):
        cell = table[(0, j)]
        header_text = df.columns[j]
        
        # Apply multiline breaks
        multiline_header = _apply_table_header_multiline(str(header_text), max_length=12)
        
        # Apply superscript formatting
        from ePy_docs.core._format import format_superscripts
        formatted_header = format_superscripts(multiline_header, 'matplotlib')
        cell.get_text().set_text(formatted_header)
        
        # Configure font
        _configure_table_cell_font(cell, header_text, True, font_list, layout_style, code_config)
        
        # Apply font size
        cell.set_fontsize(font_size_header)
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
        
        # Auto-adjust font size
        _auto_adjust_table_font_size(cell, font_size_header, num_cols, table_width, True)
    
    # Format content (rows 1+)
    for i in range(1, num_rows + 1):
        for j in range(num_cols):
            cell = table[(i, j)]
            
            df_row_idx = i - 1
            if df_row_idx < len(df) and j < len(df.columns):
                original_value = df.iloc[df_row_idx, j]
            else:
                original_value = None
            
            # Format cell text
            cell_text = cell.get_text().get_text()
            from ePy_docs.core._format import format_table_cell_text
            formatted_text = format_table_cell_text(cell_text, 'matplotlib')
            cell.get_text().set_text(formatted_text)
            
            # Configure font
            _configure_table_cell_font(cell, original_value, False, font_list, layout_style, code_config)
            
            # Apply font size
            cell.set_fontsize(font_size_content)
            
            # Auto-adjust font size
            _auto_adjust_table_font_size(cell, font_size_content, num_cols, table_width, False)
    
    # Adjust column widths
    for j in range(num_cols):
        column_name = df.columns[j]
        width_factor = calculate_table_column_width(j, column_name, df)
        
        for i in range(num_rows + 1):
            cell = table[(i, j)]
            current_width = cell.get_width()
            cell.set_width(current_width * width_factor)
    
    # Apply row heights and alignment
    font_family = font_list[0] if font_list else 'sans-serif'
    
    # Header row
    header_height_factor = calculate_table_row_height(0, df, True, font_size_header, font_size_content, layout_style, font_family)
    for j in range(num_cols):
        cell = table[(0, j)]
        current_height = cell.get_height()
        cell.set_height(current_height * header_height_factor)
        
        cell_text = cell.get_text().get_text()
        is_multiline = '\n' in cell_text or len(cell_text) > 25
        
        va = alignment_config.get('header', {}).get('vertical', 'center')
        ha = alignment_config.get('header', {}).get('horizontal', 'center')
        
        # Add padding spaces if configured
        if 'right_padding_spaces' in alignment_config and alignment_config['right_padding_spaces'] > 0:
            num_spaces = alignment_config['right_padding_spaces']
            padding_text = ' ' * num_spaces
            
            if ha == 'right':
                cell.get_text().set_text(cell_text + padding_text)
            elif ha == 'left':
                cell.get_text().set_text(padding_text + cell_text)
        
        cell.set_text_props(verticalalignment=va, horizontalalignment=ha)
        
        # Apply cell padding
        if is_multiline:
            max_lines = cell_text.count('\n') + 1
            proportional_factor = 1.0 + (max_lines * 0.3)
            cell.PAD = base_cell_padding * proportional_factor
        else:
            cell.PAD = base_cell_padding
    
    # Data rows
    for i in range(1, num_rows + 1):
        row_height_factor = calculate_table_row_height(i - 1, df, False, font_size_header, font_size_content, layout_style, font_family)
        
        for j in range(num_cols):
            cell = table[(i, j)]
            current_height = cell.get_height()
            cell.set_height(current_height * row_height_factor)
            
            cell_text = cell.get_text().get_text()
            is_multiline = '\n' in cell_text or len(cell_text) > 30
            
            is_numeric = False
            try:
                float(cell_text.replace(',', '.').replace(' ', ''))
                is_numeric = True
            except ValueError:
                pass
            
            va = alignment_config.get('content', {}).get('vertical', 'top')
            ha = alignment_config.get('numeric', {}).get('horizontal', 'right') if is_numeric else alignment_config.get('content', {}).get('horizontal', 'right')
            
            # Add padding spaces if configured
            if 'right_padding_spaces' in alignment_config and alignment_config['right_padding_spaces'] > 0:
                num_spaces = alignment_config['right_padding_spaces']
                padding_text = ' ' * num_spaces
                
                if ha == 'right':
                    cell.get_text().set_text(cell_text + padding_text)
                elif ha == 'left':
                    cell.get_text().set_text(padding_text + cell_text)
            
            cell.set_text_props(verticalalignment=va, horizontalalignment=ha)
            
            # Apply cell padding
            if is_multiline:
                max_lines = cell_text.count('\n') + 1
                proportional_factor = 1.0 + (max_lines * 0.2)
                cell.PAD = base_cell_padding * proportional_factor
            else:
                cell.PAD = base_cell_padding


def _generate_table_image(df: pd.DataFrame, title: str, output_dir: str, 
                          filename: str, style_config: Dict,
                          size_config: Dict, format_config: Dict, display_config: Dict,
                          highlight_columns: Optional[List[str]] = None,
                          palette_name: Optional[str] = None, layout_style: str = 'corporate',
                          alignment_config: Optional[Dict[str, str]] = None,
                          output_directory: str = None,
                          detected_category: Optional[str] = None) -> str:
    """Generate table image using centralized configuration (internal).
    
    Args:
        df: DataFrame containing table data.
        title: Table title.
        output_dir: Output directory.
        filename: Output filename.
        style_config: Style configuration for layout.
        size_config: Size configuration.
        format_config: Formatting configuration.
        display_config: Display configuration for table dimensions.
        highlight_columns: Columns to highlight with colors.
        palette_name: Color palette for highlights.
        layout_style: Layout style name.
        alignment_config: Alignment configuration from Text Kingdom.
        output_directory: Default output directory from SETUP configuration.
        
    Returns:
        Path to generated image file.
    """
    import logging
    
    # Setup output directory and filename
    if not output_dir:
        output_dir = output_directory
    os.makedirs(output_dir, exist_ok=True)
    
    if not filename:
        counter = len([f for f in os.listdir(output_dir) if f.startswith('table_')]) + 1
        filename = format_config['filename_format'].format(counter=counter, ext='png')
    
    filepath = os.path.join(output_dir, filename)
    
    # Setup fonts
    font_list = setup_matplotlib_fonts(layout_style)
    
    # Get code config
    from ePy_docs.core._code import get_code_config
    try:
        code_config = get_code_config()
    except:
        code_config = {}
    
    # Apply text wrapping
    from ePy_docs.core._format import prepare_dataframe_with_wrapping
    df = prepare_dataframe_with_wrapping(df, layout_style)
    
    # Validate alignment config
    if alignment_config is None:
        raise RuntimeError(f"No alignment configuration provided for layout_style '{layout_style}'")
    
    # Get font sizes
    fonts_config = style_config.get('fonts', {})
    font_size_content = fonts_config.get('content', {}).get('size', 7.0)
    font_size_header = fonts_config.get('header', {}).get('size', 8.0)
    
    # Calculate dimensions
    num_rows, num_cols = df.shape
    table_width = style_config['styling']['width_inches']
    base_cell_height = display_config.get('base_cell_height_inches', 0.45)
    row_height_factor = display_config.get('min_row_height_factor', 1.25)
    total_height_minima = (num_rows + 1) * base_cell_height * row_height_factor
    
    # Create figure and table
    fig, ax = plt.subplots(figsize=(table_width, total_height_minima))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=df.values, colLabels=df.columns,
                    cellLoc='left', loc='center')
    
    table.auto_set_font_size(False)
    table.scale(1.0, 1.0)
    
    # Format and style cells
    _format_and_style_table_cells(table, df, font_list, font_size_header, font_size_content,
                                   style_config, alignment_config, layout_style, code_config)
    
    # Load and apply colors
    colors_config = _load_colors_configuration(layout_style)
    _apply_table_colors(table, df, style_config, colors_config, layout_style,
                       highlight_columns, palette_name, detected_category)
    
    # Calculate custom bbox
    base_padding = display_config.get('padding_inches', 0.04)
    fig.canvas.draw()
    
    from matplotlib.transforms import Bbox
    table_bbox = table.get_window_extent(fig.canvas.get_renderer())
    table_bbox_inches = table_bbox.transformed(fig.dpi_scale_trans.inverted())
    
    custom_bbox = Bbox.from_bounds(
        table_bbox_inches.x0 - base_padding,
        table_bbox_inches.y0 - base_padding,
        table_bbox_inches.width + (2 * base_padding),
        table_bbox_inches.height + (2 * base_padding)
    )
    
    # Save figure
    matplotlib_logger = logging.getLogger('matplotlib.font_manager')
    matplotlib_logger.setLevel(logging.ERROR)
    
    plt.savefig(filepath, 
               dpi=300, 
               bbox_inches=custom_bbox,
               transparent=False,
               facecolor='white',
               edgecolor='none',
               format='png',
               pil_kwargs={'optimize': True})
    plt.close()
    
    return filepath


def _process_table_for_report(data: Union[pd.DataFrame, List[List]], 
                              title: str = None, output_dir: str = None, 
                              figure_counter: int = 1, layout_style: str = "corporate", 
                              highlight_columns: Optional[List[str]] = None,
                              palette_name: Optional[str] = None,
                              document_type: str = "report") -> tuple[str, str]:
    """Process table for report with automatic counter and ID (internal).
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Table title.
        output_dir: Output directory (if None, uses SETUP configuration).
        figure_counter: Counter for figure numbering.
        layout_style: One of 8 universal layout styles.
        highlight_columns: List of column names (or single string) to highlight with colors.
        palette_name: Color palette name for highlights.
        document_type: Document type for output directory resolution.
        
    Returns:
        Tuple of (image_path, figure_id).
    """
    config = _get_tables_config()
    format_config = config.get('formatting', {})
    display_config = config.get('display', {})
    
    # Provide default values if missing
    if 'filename_format' not in format_config:
        format_config['filename_format'] = 'table_{counter}.{ext}'
    if 'figure_id_format' not in format_config:
        format_config['figure_id_format'] = 'tbl-{counter}'
    if 'image_format' not in display_config:
        display_config['image_format'] = 'png'
    
    if output_dir is None:
        output_dirs = get_absolute_output_directories(document_type=document_type)
        output_dir = output_dirs['tables']
    
    figure_id = format_config['figure_id_format'].format(counter=figure_counter)
    filename = format_config['filename_format'].format(
        counter=figure_counter, 
        ext=display_config['image_format']
    )
    
    image_path = _create_table_image(
        data=data,
        title=title,
        output_dir=output_dir,
        filename=filename,
        layout_style=layout_style,
        highlight_columns=highlight_columns,
        palette_name=palette_name,
        document_type=document_type
    )
    
    return image_path, figure_id


def _create_split_table_images(df: pd.DataFrame, output_dir: str, base_table_number: int, 
                               title: str = None, highlight_columns: List[str] = None,
                               palette_name: str = None, dpi: int = 300,
                               hide_columns: List[str] = None, filter_by: Dict = None,
                               sort_by: str = None, max_rows_per_table = None,
                               layout_style: str = "corporate",
                               document_type: str = "report") -> List[str]:
    """Create multiple table images when table is too large (internal).
    
    Splits table into multiple parts maintaining consecutive numbering
    with part indication as specified by user.
    
    Args:
        df: DataFrame to split and render.
        output_dir: Directory for generated images.
        base_table_number: Base table number for consecutive numbering.
        title: Base title for all parts.
        highlight_columns: Columns to highlight with colors (string or list).
        palette_name: Color palette for highlights.
        dpi: Image resolution.
        hide_columns: Columns to exclude from display.
        filter_by: Dictionary for filtering rows.
        sort_by: Column name for sorting.
        max_rows_per_table: Maximum rows per table part.
        layout_style: Layout style from 8 universal options.
        document_type: Document type for output directory resolution.
        
    Returns:
        List of paths to generated table part images.
    """
    working_df = df.copy()
    
    if hide_columns:
        working_df = working_df.drop(columns=[col for col in hide_columns if col in working_df.columns])
    
    if filter_by:
        # Normalize filter_by to dictionary format for compatibility
        if isinstance(filter_by, (tuple, list)):
            # Handle tuple format: (column, value) or list of tuples
            filter_dict = {}
            if isinstance(filter_by, tuple) and len(filter_by) == 2:
                # Single tuple: (column, value)
                filter_dict[filter_by[0]] = filter_by[1]
            elif isinstance(filter_by, list):
                # List of tuples: [(column, value), ...]
                for item in filter_by:
                    if isinstance(item, tuple) and len(item) == 2:
                        filter_dict[item[0]] = item[1]
            filter_by = filter_dict
        
        for col, value in filter_by.items():
            if col in working_df.columns:
                working_df = working_df[working_df[col] == value]
    
    if sort_by and sort_by in working_df.columns:
        working_df = working_df.sort_values(sort_by)
    
    # Handle max_rows_per_table as int or list
    if max_rows_per_table is None:
        max_rows_per_table = 25
    
    total_rows = len(working_df)
    
    # Calculate splits based on type of max_rows_per_table
    if isinstance(max_rows_per_table, list):
        # List mode: each element specifies rows for that part
        splits = []
        current_idx = 0
        for rows_in_part in max_rows_per_table:
            if current_idx >= total_rows:
                break
            end_idx = min(current_idx + rows_in_part, total_rows)
            splits.append((current_idx, end_idx))
            current_idx = end_idx
        # If there are remaining rows, add one more split
        if current_idx < total_rows:
            splits.append((current_idx, total_rows))
        num_parts = len(splits)
    else:
        # Int mode: uniform split size
        num_parts = (total_rows + max_rows_per_table - 1) // max_rows_per_table
        splits = []
        for part_num in range(num_parts):
            start_idx = part_num * max_rows_per_table
            end_idx = min(start_idx + max_rows_per_table, total_rows)
            splits.append((start_idx, end_idx))
    
    image_paths = []
    
    for part_num, (start_idx, end_idx) in enumerate(splits):
        chunk_df = working_df.iloc[start_idx:end_idx]
        
        if num_parts > 1:
            part_title = f"{title} - Parte {part_num + 1}/{num_parts}" if title else f"Tabla {base_table_number + part_num} - Parte {part_num + 1}/{num_parts}"
        else:
            part_title = title if title else f"Tabla {base_table_number + part_num}"
        
        filename = f"table_{base_table_number + part_num}.png"
        
        part_image_path = _create_table_image(
            data=chunk_df,
            title=part_title,
            output_dir=output_dir,
            filename=filename,
            layout_style=layout_style,
            highlight_columns=highlight_columns,
            palette_name=palette_name,
            document_type=document_type
        )
        
        image_paths.append(part_image_path)
    
    return image_paths


def create_table_image_and_markdown(
    df: pd.DataFrame,
    caption: str = None,
    layout_style: str = "corporate",
    output_dir: str = None,
    table_number: int = 1,
    **kwargs
) -> Tuple[str, Union[str, List[str]], int]:
    """
    Create table image and return markdown with image path(s).
    
    Public API function used by writers.py.
    
    Args:
        df: DataFrame containing table data
        caption: Table caption/title
        layout_style: Layout style name
        output_dir: Output directory for table image
        table_number: Table number for counter
        **kwargs: Additional options (highlight_columns as string or list, palette_name, 
                                      max_rows_per_table, colored, show_figure, etc.)
        
    Returns:
        Tuple of (markdown_content, image_path_or_paths, new_counter)
        - markdown_content: Complete markdown string with all table parts
        - image_path_or_paths: Single string for one table, or list of strings for split tables
        - new_counter: Updated table counter
    """
    # Extract special parameters
    max_rows_per_table = kwargs.pop('max_rows_per_table', None)
    colored = kwargs.pop('colored', False)
    show_figure = kwargs.pop('show_figure', False)
    
    # Filter valid kwargs for _process_table_for_report
    valid_kwargs = {
        'highlight_columns', 'palette_name', 
        'document_type', 'hide_columns', 'filter_by', 'sort_by'
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_kwargs}
    
    # Check if table needs splitting
    if max_rows_per_table:
        # Handle both int and list for max_rows_per_table
        if isinstance(max_rows_per_table, list):
            # List mode: use the list as-is for variable splits
            needs_splitting = len(df) > sum(max_rows_per_table)
        else:
            # Int mode: simple comparison
            needs_splitting = len(df) > max_rows_per_table
        
        if needs_splitting or isinstance(max_rows_per_table, list):
            # Use split table functionality
            if output_dir is None:
                document_type = filtered_kwargs.get('document_type', 'report')
                from ePy_docs.core._config import get_absolute_output_directories
                output_dirs = get_absolute_output_directories(document_type=document_type)
                output_dir = output_dirs['tables']
            
            image_paths = _create_split_table_images(
                df=df,
                output_dir=output_dir,
                base_table_number=table_number,
                title=caption,
                max_rows_per_table=max_rows_per_table,
                layout_style=layout_style,
                **filtered_kwargs
            )
            
            # Build markdown for all parts
            markdown_parts = []
            num_parts = len(image_paths)
            
            for i, img_path in enumerate(image_paths):
                part_number = table_number + i
                figure_id = f"tbl-{part_number}"
                
                if num_parts > 1:
                    part_title = f"{caption} - Parte {i + 1}/{num_parts}" if caption else f"Tabla {part_number} - Parte {i + 1}/{num_parts}"
                else:
                    part_title = caption if caption else f"Tabla {part_number}"
                
                # Use only image caption, not duplicated markdown caption
                markdown_parts.append(f"![{part_title}]({img_path})")
                markdown_parts.append(f"{{#{figure_id}}}\n\n")
            
            markdown = ''.join(markdown_parts)
            # Return ALL image paths for split tables and new counter
            return markdown, image_paths, table_number + num_parts - 1
    
    else:
        # Single table - use normal processing
        image_path, figure_id = _process_table_for_report(
            data=df,
            title=caption,
            output_dir=output_dir,
            figure_counter=table_number,
            layout_style=layout_style,
            **filtered_kwargs
        )
        
        # Build markdown
        markdown_parts = []
        
        # Use only image caption, not duplicated markdown caption
        table_title = caption if caption else f"Tabla {table_number}"
        markdown_parts.append(f"![{table_title}]({image_path})")
        markdown_parts.append(f"{{#{figure_id}}}\n\n")
        
        markdown = ''.join(markdown_parts)
        
        # Return same counter (caller already passed counter + 1)
        return markdown, image_path, table_number
