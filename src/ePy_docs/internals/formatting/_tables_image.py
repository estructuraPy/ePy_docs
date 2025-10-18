"""Auxiliary module for table image generation with ReportLab and matplotlib.

This module handles all image generation logic for tables, including:
- matplotlib figure creation and rendering
- ReportLab canvas operations
- Font configuration and fallback handling
- Color gradients and styling
- Multi-line text adjustment
- Cell padding and alignment

This is an AUXILIARY module (prefixed with _) and should only be imported
by tables.py. Do not use directly from external code.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Rectangle
from typing import Dict, Any, Union, List, Optional, Tuple

# Import from internal data module
from ePy_docs.internals.data_processing._data import load_cached_files, _safe_get_nested
from ePy_docs.config.setup import _resolve_config_path, get_absolute_output_directories

def _get_tables_config() -> Dict[str, Any]:
    """Load centralized table configuration (internal helper).
    
    Returns:
        Complete tables configuration dictionary.
    """
    config_path = _resolve_config_path('components/tables')
    return load_cached_files(config_path)

def _is_missing_table_value(text_value) -> bool:
    """Detect if a value should be displayed in italic for being missing."""
    if pd.isna(text_value):
        return True
    
    text_str = str(text_value).strip().lower()
    missing_indicators = ['', 'nan', 'none', 'null', '-', '--', '---', 'n/a', 'na']
    return text_str in missing_indicators

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
            if layout_style in code_config.get('layout_styles', {}):
                code_layout = code_config['layout_styles'][layout_style]
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

def _calculate_table_column_width(col_index: int, column_name: str, df: pd.DataFrame) -> float:
    """Calculate specific width factor for each column."""
    max_content_length = len(str(column_name))
    
    for row_idx in range(len(df)):
        cell_value = df.iloc[row_idx, col_index]
        cell_str = str(cell_value)
        
        if '\n' in cell_str:
            lines = cell_str.split('\n')
            max_line_length = max(len(line) for line in lines)
            max_content_length = max(max_content_length, max_line_length)
        else:
            max_content_length = max(max_content_length, len(cell_str))
    
    if max_content_length <= 3:
        width_factor = 0.7
    elif max_content_length <= 8:
        width_factor = 0.9
    elif max_content_length <= 15:
        width_factor = 1.0
    elif max_content_length <= 25:
        width_factor = 1.2
    elif max_content_length <= 35:
        width_factor = 1.4
    else:
        width_factor = 1.6
    
    for row_idx in range(len(df)):
        cell_value = df.iloc[row_idx, col_index]
        cell_str = str(cell_value)
        if any(char in cell_str for char in ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']) or \
           any(pattern in cell_str for pattern in ['·', '×', '÷', '±', '≤', '≥']):
            width_factor *= 1.05
            break
    
    return width_factor

def _calculate_table_row_height(row_index: int, df: pd.DataFrame, is_header: bool, 
                                 font_size_header: float, font_size_content: float,
                                 layout_style: str, font_family: str) -> float:
    """Calculate necessary height based on actual letter height + proportional spacing."""
    max_lines_in_row = 1
    base_font_size = float(font_size_header if is_header else font_size_content)
    
    if is_header:
        for col in df.columns:
            col_str = str(col)
            line_count = col_str.count('\n') + 1
            max_lines_in_row = max(max_lines_in_row, line_count)
            
            if len(col_str) > 20:
                estimated_lines = len(col_str) // 20 + 1
                max_lines_in_row = max(max_lines_in_row, estimated_lines)
            
            if any(len(word) > 15 for word in col_str.split('\n')):
                max_lines_in_row = max(max_lines_in_row, line_count + 1)
    else:
        if row_index < len(df):
            for col in df.columns:
                cell_value = df.iloc[row_index, df.columns.get_loc(col)]
                cell_str = str(cell_value)
                
                line_count = cell_str.count('\n') + 1
                max_lines_in_row = max(max_lines_in_row, line_count)
                
                if len(cell_str) > 25:
                    estimated_lines = len(cell_str) // 25 + 1
                    max_lines_in_row = max(max_lines_in_row, estimated_lines)
    
    line_height_points = base_font_size * 1.2
    
    font_type_factor = 1.0
    uses_handwritten = (layout_style == 'minimal' or font_family == 'handwritten_personal')
    if uses_handwritten:
        font_type_factor = 1.25
    else:
        font_type_factor = 1.0
    
    if max_lines_in_row == 1:
        spacing_factor = 1.15
    elif max_lines_in_row <= 3:
        spacing_factor = 1.25
    elif max_lines_in_row <= 5:
        spacing_factor = 1.30
    else:
        spacing_factor = 1.35
    
    if is_header:
        spacing_factor *= 1.10
    
    height_factor = (line_height_points * max_lines_in_row * spacing_factor * font_type_factor) / (base_font_size * 1.2)
    height_factor = max(height_factor, 1.0)
    return height_factor

def _convert_rgb_to_matplotlib(rgb_list) -> Union[str, List[float]]:
    """Convert RGB list [0-255] to matplotlib format [0-1]."""
    if isinstance(rgb_list, str):
        if rgb_list.startswith('#'):
            return rgb_list
        if ',' in rgb_list:
            rgb_list = [x.strip() for x in rgb_list.split(',')]
    
    numeric_rgb = []
    for x in rgb_list:
        if isinstance(x, str):
            try:
                numeric_rgb.append(float(x))
            except ValueError:
                numeric_rgb.append(0.0)
        else:
            numeric_rgb.append(float(x))
    
    return [x/255.0 for x in numeric_rgb]

def _get_palette_color_by_tone(palette_name: str, tone: str, colors_config: Dict) -> List[float]:
    """Get RGB color from palette and tone according to Reino Colors."""
    if palette_name in colors_config['palettes']:
        palette = colors_config['palettes'][palette_name]
        if tone in palette:
            return _convert_rgb_to_matplotlib(palette[tone])
    return _convert_rgb_to_matplotlib(colors_config['palettes']['grays_warm']['medium_light'])

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

def _create_table_image(data: Union[pd.DataFrame, List[List]], 
                        title: str = None, output_dir: str = None, 
                        filename: str = None, layout_style: str = "corporate", 
                        highlight_columns: Optional[List[str]] = None,
                        palette_name: Optional[str] = None,
                        auto_detect_categories: bool = False,
                        document_type: str = "report") -> str:
    """Create table as image using centralized configuration (internal).
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Optional table title.
        output_dir: Output directory path.
        filename: Output filename.
        layout_style: One of 8 universal layout styles.
        highlight_columns: List of column names to highlight with colors.
        palette_name: Color palette name for highlights.
        auto_detect_categories: Enable automatic category detection for highlighting.
        document_type: Document type for output directory resolution.
        
    Returns:
        Path to generated image file.
        
    Raises:
        ValueError: If layout_style not found in configuration.
    """
    config = _get_tables_config()
    
    if layout_style not in config['layout_styles']:
        raise ValueError(f"Layout style '{layout_style}' not found")
    
    style_config = config['layout_styles'][layout_style]
    
    size_config = config['font_sizes']
    format_config = config['formatting']
    display_config = config['display']
    
    output_dirs = get_absolute_output_directories(document_type=document_type)
    output_directory = output_dirs['tables']
    
    df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
    
    # Automatic category detection and highlight for add_colored_table
    if auto_detect_categories and (highlight_columns is None or len(highlight_columns) == 0):
        # Import detect_table_category from parent module
        from ePy_docs.internals.formatting._tables import detect_table_category
        detected_category, auto_highlight_columns = detect_table_category(df)
        if auto_highlight_columns:
            highlight_columns = auto_highlight_columns
            if palette_name is None:
                category_rules = config.get('category_rules', {})
                if detected_category in category_rules:
                    category_palettes = {
                        'nodes': 'blues',
                        'dimensions': 'grays_warm',
                        'forces': 'reds',
                        'properties': 'greens',
                        'design': 'oranges',
                        'analysis': 'purples',
                        'general': 'grays_cool'
                    }
                    palette_name = category_palettes.get(detected_category, 'blues')
    
    # Superscript formatting from Format module
    from ePy_docs.internals.formatting._format import format_superscripts
    
    for col in df.columns:
        df[col] = df[col].apply(lambda x: format_superscripts(str(x), 'matplotlib'))
    
    # Code content detection and formatting from Code Kingdom
    from ePy_docs.internals.formatting._code import get_code_config, get_available_languages
    code_config = get_code_config()
    available_languages = get_available_languages()
    
    for col in df.columns:
        df[col] = df[col].apply(lambda x: _detect_format_code_content(x, code_config, available_languages))
    
    # Official access to Text Kingdom for alignment configuration by layout_styles
    from ePy_docs.internals.formatting._text import get_text_config
    text_config = get_text_config()
    
    if layout_style not in text_config['layout_styles']:
        raise RuntimeError(f"Layout style '{layout_style}' not found in Text Kingdom")
    
    text_style_config = text_config['layout_styles'][layout_style]
    if 'tables' not in text_style_config or 'alignment' not in text_style_config['tables']:
        raise RuntimeError(f"Alignment configuration missing for layout_style '{layout_style}' in Text Kingdom")
    
    alignment_config = text_style_config['tables']['alignment']
    
    return _generate_table_image(df, title, output_dir, filename, 
                                style_config, size_config, 
                                format_config, display_config, highlight_columns, 
                                palette_name, layout_style, alignment_config, 
                                output_directory)

def _generate_table_image(df: pd.DataFrame, title: str, output_dir: str, 
                          filename: str, style_config: Dict,
                          size_config: Dict, format_config: Dict, display_config: Dict,
                          highlight_columns: Optional[List[str]] = None,
                          palette_name: Optional[str] = None, layout_style: str = 'corporate',
                          alignment_config: Optional[Dict[str, str]] = None,
                          output_directory: str = None) -> str:
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
        output_directory: Default output directory from Reino SETUP.
        
    Returns:
        Path to generated image file.
    """
    # CONSTITUTIONAL MANDATE: Suppress matplotlib font warnings globally
    import logging
    matplotlib_logger = logging.getLogger('matplotlib.font_manager')
    matplotlib_logger.setLevel(logging.ERROR)
    
    if not output_dir:
        output_dir = output_directory
    os.makedirs(output_dir, exist_ok=True)
    
    if not filename:
        counter = len([f for f in os.listdir(output_dir) if f.startswith('table_')]) + 1
        filename = format_config['filename_format'].format(counter=counter, ext='png')
    
    filepath = os.path.join(output_dir, filename)
    
    # CONFIGURE PRIMARY FONT WITH AUTOMATIC FALLBACK using Text Kingdom
    from ePy_docs.internals.formatting._text import get_text_config
    text_config = get_text_config()
    
    layout_config = text_config['layout_styles'][layout_style]
    
    if 'tables' in layout_config and 'content_font' in layout_config['tables']:
        font_family = layout_config['tables']['content_font']['family']
    elif 'typography' in layout_config and 'normal' in layout_config['typography']:
        font_family = layout_config['typography']['normal']['family']
    else:
        font_family = 'sans_technical'  # Emergency fallback
    
    font_config = text_config['font_families'][font_family]
    font_list = [font_config['primary']]
    if font_config.get('fallback'):
        fallback_fonts = [f.strip() for f in font_config['fallback'].split(',')]
        font_list.extend(fallback_fonts)
    
    # Configure matplotlib to use font list BEFORE any font operations - WARNINGS SUPPRESSED
    plt.rcParams['font.family'] = font_list
    
    import matplotlib.font_manager as fm
    if font_config['primary'] not in [f.name for f in fm.fontManager.ttflist]:
        fm._load_fontmanager(try_read_cache=False)  # Only reload if font not found
    
    from ePy_docs.internals.formatting._code import get_code_config
    try:
        code_config = get_code_config()
    except:
        code_config = {}  # Fallback if code config unavailable
    
    # AUTOMATIC WRAPPING PRE-TABLE
    # OBJECTIVE: Resolve horizontal overflow by wrapping text before matplotlib
    from ePy_docs.internals.formatting._format import prepare_dataframe_with_wrapping
    df = prepare_dataframe_with_wrapping(df, layout_style)
    
    # Alignment configuration by layout_styles via Text Kingdom
    # No fallbacks - valid configuration must exist
    if alignment_config is None:
        raise RuntimeError(f"No alignment configuration provided for layout_style '{layout_style}'")
    
    font_size_content = size_config['content'][style_config['font_sizes']['content']]
    font_size_header = size_config['header'][style_config['font_sizes']['header']]
    
    base_cell_padding = style_config['styling']['cell_padding'] / 1000.0  # Convert pixels to fraction
    
    # Recalculate dimensions after wrapping
    num_rows, num_cols = df.shape
    
    table_width = style_config['styling']['width_inches']
    
    base_cell_height = display_config.get('base_cell_height_inches', 0.45)
    row_height_factor = display_config.get('min_row_height_factor', 1.25)
    
    # Minimum height calculated by content using display configuration
    total_height_minima = (num_rows + 1) * base_cell_height * row_height_factor
    
    # FIGURE WITH SPECIFIC WIDTH PER LAYOUT_STYLE
    fig, ax = plt.subplots(figsize=(table_width, total_height_minima))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=df.values, colLabels=df.columns,
                    cellLoc='left', loc='center')  # Default left, overridden individually
    
    # FORCE FULL WIDTH: Table must occupy all available width
    table.auto_set_font_size(False)
    table.scale(1.0, 1.0)  # Base scale, will be adjusted individually per cell
    
    # APPLY FONT ADJUSTMENT TO HEADERS AND CONTENT
    # Headers (row 0) - automatic adjustment if doesn't fit + font configuration
    for j in range(num_cols):
        cell = table[(0, j)]
        header_text = df.columns[j]
        
        # STEP 1: Apply intelligent multiline breaks BEFORE font reduction
        multiline_header = _apply_table_header_multiline(str(header_text), max_length=12)
        
        # STEP 2: Apply superscript formatting to the multiline header text
        from ePy_docs.internals.formatting._format import format_superscripts
        formatted_header = format_superscripts(multiline_header, 'matplotlib')
        cell.get_text().set_text(formatted_header)
        
        # STEP 3: Configure specific font for header
        _configure_table_cell_font(cell, header_text, True, font_list, layout_style, code_config)
        
        # STEP 4: Apply base font size
        cell.set_fontsize(font_size_header)
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
            
        # STEP 5: Apply intelligent font size adjustment (after multiline optimization)
        _auto_adjust_table_font_size(cell, font_size_header, num_cols, table_width, True)

    # Content (rows 1+) - automatic adjustment if doesn't fit + font configuration
    for i in range(1, num_rows + 1):
        for j in range(num_cols):
            cell = table[(i, j)]
            
            df_row_idx = i - 1  # Convert table index to DataFrame
            if df_row_idx < len(df) and j < len(df.columns):
                original_value = df.iloc[df_row_idx, j]
            else:
                original_value = None
            
            _configure_table_cell_font(cell, original_value, False, font_list, layout_style, code_config)
            
            cell.set_fontsize(font_size_content)
            _auto_adjust_table_font_size(cell, font_size_content, num_cols, table_width, False)

    # AUTOMATIC WIDTH ADJUSTMENT PER COLUMN
    for j in range(num_cols):
        column_name = df.columns[j]
        width_factor = _calculate_table_column_width(j, column_name, df)
        
        for i in range(num_rows + 1):  # +1 to include header
            cell = table[(i, j)]
            current_width = cell.get_width()
            cell.set_width(current_width * width_factor)

    # CORRECT MULTILINE TEXT FORMATTING AND ADJUSTMENT PER COMPLETE ROW
    # APPLY UNIFORM HEIGHT PER COMPLETE ROW
    header_height_factor = _calculate_table_row_height(0, df, True, font_size_header, font_size_content, layout_style, font_family)
    for j in range(num_cols):
        cell = table[(0, j)]
        current_height = cell.get_height()
        cell.set_height(current_height * header_height_factor)
        
        # Header alignment from Text Kingdom by layout_styles
        cell_text = cell.get_text().get_text()
        is_multiline = '\n' in cell_text or len(cell_text) > 25
        
        va = alignment_config['header_vertical']
        ha = alignment_config['header_horizontal']
        
        cell.set_text_props(
            verticalalignment=va, 
            horizontalalignment=ha
        )
        
        # Internal padding from configuration (convert from pixels to fraction)
        # cell_padding is in pixels, convert to matplotlib PAD format (fraction of cell)
        base_cell_padding = style_config['styling']['cell_padding'] / 1000.0  # Convert to fraction
        
        if is_multiline:
            # Proportional padding to number of lines
            max_lines = cell_text.count('\n') + 1
            proportional_factor = 1.0 + (max_lines * 0.3)  # 30% increase per extra line
            cell.PAD = base_cell_padding * proportional_factor
        else:
            # Single-line headers use base padding
            cell.PAD = base_cell_padding

    # Data rows (1 to num_rows) - alignment from Text Kingdom
    for i in range(1, num_rows + 1):
        row_height_factor = _calculate_table_row_height(i - 1, df, False, font_size_header, font_size_content, layout_style, font_family)
        
        for j in range(num_cols):
            cell = table[(i, j)]
            current_height = cell.get_height()
            cell.set_height(current_height * row_height_factor)
            
            # Content alignment from Text Kingdom by layout_styles
            cell_text = cell.get_text().get_text()
            is_multiline = '\n' in cell_text or len(cell_text) > 30
            
            is_numeric = False
            try:
                float(cell_text.replace(',', '.').replace(' ', ''))
                is_numeric = True
            except ValueError:
                pass
            
            va = alignment_config['content_vertical']
            ha = alignment_config['numeric_horizontal'] if is_numeric else alignment_config['content_horizontal']
            
            cell.set_text_props(
                verticalalignment=va,
                horizontalalignment=ha
            )
            
            # Internal padding from configuration for content
            if is_multiline:
                # Proportional padding to number of content lines
                max_lines = cell_text.count('\n') + 1
                proportional_factor = 1.0 + (max_lines * 0.2)  # 20% increase per extra line for content
                current_cell = table[(i, j)]
                current_cell.PAD = base_cell_padding * proportional_factor
            else:
                # Single-line content uses base padding
                current_cell = table[(i, j)]
                current_cell.PAD = base_cell_padding

    # Official access to Colors Kingdom for layout_styles
    from ePy_docs.internals.styling._colors import get_colors_config
    colors_config = get_colors_config()
    
    if layout_style in colors_config['layout_styles']:
        layout_colors = colors_config['layout_styles'][layout_style]
        default_palette_name = layout_colors.get('default_palette', 'grays_warm')
        table_config = layout_colors.get('tables', {})
    else:
        # Fallback to grays_warm if layout not found
        default_palette_name = 'grays_warm'
        table_config = {}
    
    # HEADER styling according to layout_style
    header_config = _safe_get_nested(table_config, 'header.default', {
        'palette': default_palette_name, 
        'tone': 'medium_light'
    })
    header_color = _get_palette_color_by_tone(
        header_config['palette'], 
        header_config['tone'],
        colors_config
    )
    
    for i in range(num_cols):
        cell = table[(0, i)]
        # Fuente y estilo configurados en sección de ajuste automático
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
        cell.set_facecolor(header_color)
    
    if style_config['styling']['alternating_rows']:
        alt_row_color = _get_palette_color_by_tone(default_palette_name, 'light', colors_config)
        for i in range(1, num_rows + 1):
            if i % 2 == 0:
                for j in range(num_cols):
                    table[(i, j)].set_facecolor(alt_row_color)
    
    # HIGHLIGHT COLUMNS: Apply gradient highlighting per column if specified
    if highlight_columns:
        # Default palette if none specified - FIXED: usar 'blues' que sí existe
        if not palette_name:
            palette_name = 'blues'
        
        if palette_name in colors_config['palettes']:
            palette = colors_config['palettes'][palette_name]
            
            gradient_colors = []
            for intensity in ['light', 'medium_light', 'medium', 'medium_dark', 'dark']:
                if intensity in palette:
                    gradient_colors.append(_convert_rgb_to_matplotlib(palette[intensity]))
            
            # Fallback if no gradient found
            if not gradient_colors:
                gradient_colors = [_convert_rgb_to_matplotlib(palette.get('light', '#E3F2FD'))]
            
            for col_name in highlight_columns:
                if col_name in df.columns:
                    col_index = df.columns.get_loc(col_name)
                    
                    col_values = []
                    for row_index in range(1, num_rows + 1):
                        try:
                            df_row_index = row_index - 1  # Convert table index to DataFrame index
                            if df_row_index < len(df):
                                cell_value = df.iloc[df_row_index, col_index]
                                # Try to convert to float for numerical gradient
                                if pd.notna(cell_value):
                                    try:
                                        col_values.append(float(cell_value))
                                    except (ValueError, TypeError):
                                        col_values.append(0.0)  # Non-numeric values get neutral color
                                else:
                                    col_values.append(0.0)
                        except (IndexError, ValueError):
                            col_values.append(0.0)
                    
                    if col_values and len(gradient_colors) > 1:
                        # Filter out any remaining NaN values and ensure we have valid numbers
                        valid_values = [v for v in col_values if not pd.isna(v) and isinstance(v, (int, float))]
                        
                        if valid_values:
                            min_val = min(valid_values)
                            max_val = max(valid_values)
                        else:
                            # No valid values, use neutral color for all
                            min_val = max_val = 0.0
                        
                        for i, row_index in enumerate(range(1, num_rows + 1)):
                            if i < len(col_values):
                                current_value = col_values[i]
                                
                                if max_val != min_val and not pd.isna(current_value):
                                    normalized_value = (current_value - min_val) / (max_val - min_val)
                                    # Additional safety check for NaN
                                    if pd.isna(normalized_value):
                                        normalized_value = 0.5  # Use middle color as fallback
                                    # Map to gradient color index
                                    color_index = int(normalized_value * (len(gradient_colors) - 1))
                                    color_index = max(0, min(color_index, len(gradient_colors) - 1))
                                    cell_color = gradient_colors[color_index]
                                else:
                                    # All values are the same or current value is NaN, use middle color
                                    cell_color = gradient_colors[len(gradient_colors) // 2]
                                
                                table[(row_index, col_index)].set_facecolor(cell_color)
                    else:
                        # Fallback to single color if gradient not available
                        single_color = gradient_colors[0] if gradient_colors else _convert_rgb_to_matplotlib('#E3F2FD')
                        for row_index in range(1, num_rows + 1):
                            table[(row_index, col_index)].set_facecolor(single_color)
    
    border_color = _get_palette_color_by_tone(default_palette_name, 'medium', colors_config)
    for key, cell in table.get_celld().items():
        cell.set_linewidth(style_config['styling']['grid_width'])
        cell.set_edgecolor(border_color)
    
    base_padding = display_config.get('padding_inches', 0.04)
    
    # This eliminates matplotlib's automatic vertical padding
    fig.canvas.draw()  # Force draw to calculate actual dimensions
    
    from matplotlib.transforms import Bbox
    table_bbox = table.get_window_extent(fig.canvas.get_renderer())
    table_bbox_inches = table_bbox.transformed(fig.dpi_scale_trans.inverted())
    
    custom_bbox = Bbox.from_bounds(
        table_bbox_inches.x0 - base_padding,  # left
        table_bbox_inches.y0 - base_padding,  # bottom  
        table_bbox_inches.width + (2 * base_padding),  # width
        table_bbox_inches.height + (2 * base_padding)  # height
    )
    
    # Suppress matplotlib font warnings during savefig - CONSTITUTIONAL MANDATE
    matplotlib_logger.setLevel(logging.ERROR)
    
    plt.savefig(filepath, 
               dpi=300, 
               bbox_inches=custom_bbox,  # Use custom bbox instead of 'tight'
               transparent=False,
               facecolor='white',  # Ensure white background for consistency
               edgecolor='none',   # Remove edge color artifacts
               format='png',       # Explicitly specify PNG format
               pil_kwargs={'optimize': True})   # Optimize PNG for better compatibility
    plt.close()
    
    return filepath

def _process_table_for_report(data: Union[pd.DataFrame, List[List]], 
                              title: str = None, output_dir: str = None, 
                              figure_counter: int = 1, layout_style: str = "corporate", 
                              highlight_columns: Optional[List[str]] = None,
                              palette_name: Optional[str] = None,
                              auto_detect_categories: bool = False,
                              document_type: str = "report") -> tuple[str, str]:
    """Process table for report with automatic counter and ID (internal).
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Table title.
        output_dir: Output directory (if None, uses Reino SETUP configuration).
        figure_counter: Counter for figure numbering.
        layout_style: One of 8 universal layout styles.
        highlight_columns: List of column names to highlight with colors.
        palette_name: Color palette name for highlights.
        auto_detect_categories: Enable automatic category detection for highlighting.
        document_type: Document type for output directory resolution.
        
    Returns:
        Tuple of (image_path, figure_id).
    """
    config = _get_tables_config()
    format_config = config['formatting']
    display_config = config['display']
    
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
        auto_detect_categories=auto_detect_categories,
        document_type=document_type
    )
    
    return image_path, figure_id

def _create_split_table_images(df: pd.DataFrame, output_dir: str, base_table_number: int, 
                               title: str = None, highlight_columns: List[str] = None,
                               palette_name: str = None, dpi: int = 300,
                               hide_columns: List[str] = None, filter_by: Dict = None,
                               sort_by: str = None, max_rows_per_table: int = 25,
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
        highlight_columns: Columns to highlight with colors.
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
    
    if max_rows_per_table is None:
        max_rows_per_table = 25
        
    # Split DataFrame into chunks
    total_rows = len(working_df)
    num_parts = (total_rows + max_rows_per_table - 1) // max_rows_per_table
    
    image_paths = []
    
    for part_num in range(num_parts):
        start_idx = part_num * max_rows_per_table
        end_idx = min(start_idx + max_rows_per_table, total_rows)
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
            auto_detect_categories=False,  # Already processed in main call
            document_type=document_type
        )
        
        image_paths.append(part_image_path)
    
    return image_paths
