"""Enhanced table creation utilities with configuration from tables.json."""
import os
import re
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from pandas.api.types import is_numeric_dtype

from ePy_docs.components.colors import (
    TableColorConfig, get_custom_colormap
)
from ePy_docs.core.setup import _load_cached_files, get_filepath
from .dataframes import (
    apply_table_preprocessing, prepare_dataframe_for_display,
    validate_dataframe_for_table, split_large_table
)
from ePy_docs.files.data import (
    convert_dataframe_to_table_with_units, filter_dataframe_rows, 
    sort_dataframe_rows, hide_dataframe_columns
)

def _load_table_config(sync_files: bool = True) -> Dict[str, Any]:
    """Load comprehensive table configuration from tables.json, colors.json, and text.json.
    
    Args:
        sync_files: Whether to sync configuration files from source
        
    Returns:
        Unified table configuration dictionary with layout-specific settings
    """
    from ePy_docs.components.pages import get_layout_name
    
    try:
        # Load all configuration files with centralized pattern - NO GUARDIANS
        tables_config = _load_cached_files(get_filepath('files.configuration.writer.tables_json', sync_files), sync_files)
        colors_config = _load_cached_files(get_filepath('files.configuration.styling.colors_json', sync_files), sync_files)  # Direct access, no guardian
        format_config = _load_cached_files(get_filepath('files.configuration.units.format_json', sync_files), sync_files)
        
        # Get current layout
        layout_name = get_layout_name()
        
        # Build unified configuration for current layout
        unified_config = {}
            
        # 1. Base table styling configuration from tables.json
        if 'layout_styles' in tables_config and layout_name in tables_config['layout_styles']:
            layout_table_config = tables_config['layout_styles'][layout_name]
            unified_config['layout_styles'] = {layout_name: layout_table_config}
            # Also add styling directly for backwards compatibility
            if 'styling' in layout_table_config:
                unified_config.update(layout_table_config['styling'])
        
        # 2. Colors from colors.json for current layout
        # Get table colors from the specific layout_styles section
        if 'layout_styles' in colors_config and layout_name in colors_config['layout_styles']:
            layout_colors = colors_config['layout_styles'][layout_name]
            
            # Extract table-specific colors from the layout
            if 'tables' in layout_colors:
                unified_config['layout_table_colors'] = layout_colors['tables']
                
            # Also add general layout colors for compatibility
            unified_config['layout_colors'] = layout_colors
        
        # Fallback: Use global tables section if layout-specific tables are not found
        if 'tables' in colors_config:
            # Use global table configuration as fallback
            global_table_config = colors_config['tables']
            if 'layout_table_colors' not in unified_config:
                unified_config['global_table_colors'] = global_table_config
        
        # 3. Typography from format.json for current layout (use centralized caption config)
        if 'layout_styles' in format_config and layout_name in format_config['layout_styles']:
            layout_text = format_config['layout_styles'][layout_name]
            if 'text' in layout_text:
                unified_config['text_config'] = layout_text['text']
                
                # Use centralized caption configuration for table typography
                text_section = layout_text['text']
                caption_config = text_section.get('caption', {})
                normal_config = text_section.get('normal', {})
                
                # Build typography from centralized text configurations
                unified_config['typography'] = {
                    # For table captions (titles/descriptions)
                    'caption_font_size': caption_config.get('fontSize', 9),
                    'title_font_size': caption_config.get('fontSize', 9),  # Same as caption
                    
                    # For table content (cell text)
                    'font_size': text_section.get('table_content', {}).get('fontSize', 9),
                    
                    # For table headers
                    'header_font_size': text_section.get('table_header', {}).get('fontSize', 10),
                    
                    # Font family and weight from main text config
                    'font_family': text_section.get('font_family', 'Times New Roman'),
                    'font_weight': text_section.get('font_weight', 'normal')
                }
        
        # 4. Add display configuration from tables.json
        unified_config['display'] = tables_config['display']
            
        # 5. Add pagination configuration from tables.json
        unified_config['pagination'] = tables_config['pagination']
            
        # 7. Add other sections from tables.json
        for section in ['category_rules', 'format_rules', 'cross_referencing', 'source', 'default_header_color']:
            if section in tables_config:
                unified_config[section] = tables_config[section]
            
        # 8. Add mathematical notation support from centralized format.json
        from ePy_docs.core.quarto import load_math_config
        format_config = load_math_config()
        unified_config['math_support'] = format_config.get('math_formatting', {
            'enable_superscript': True,
            'enable_subscript': True,
            'superscript_pattern': r'\^(\{[^}]+\}|\w)',
            'subscript_pattern': r'_(\{[^}]+\}|\w)',
            'unicode_conversion': True
        })
        
        return unified_config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load table configurations: {e}")

def _load_column_categories_config() -> Dict[str, Any]:
    """Load column categorization rules from tables.json.
    
    Respects sync_files setting - loads from library if sync_files=False.
    """
    try:
        from ePy_docs.core.setup import _load_cached_files, get_filepath
        config_path = get_filepath('files.configuration.writer.tables_json', False)
        return _load_cached_files(config_path, sync_files=False)
    except Exception as e:
        raise RuntimeError(f"Failed to load tables configuration: {e}")

def _load_format_rules_config() -> Dict[str, Any]:
    """Load format rules from tables.json using unified configuration system."""
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    
    config_path = get_filepath('files.configuration.writer.tables_json', False)
    tables_config = _load_cached_files(config_path, sync_files=False)
    
    if 'format_rules' not in tables_config:
        raise ValueError("Missing 'format_rules' in tables configuration")
    return tables_config['format_rules']

def _load_category_rules() -> Dict[str, Any]:
    """Load category rules configuration from tables.json."""
    return _load_column_categories_config()

def apply_text_formatting(text: str, output_format: str = 'matplotlib') -> str:
    """Apply text formatting including superscripts and subscripts based on format.json.
    
    This is a wrapper that delegates to the advanced text formatting function in text.py.
    
    Args:
        text: Text to format
        output_format: Output format ('matplotlib', 'unicode', 'html', 'latex', etc.)
        
    Returns:
        Formatted text with proper superscripts, subscripts, and symbols
    """
    from ePy_docs.components.text import apply_advanced_text_formatting
    return apply_advanced_text_formatting(text, output_format)

def get_quarto_relative_path(img_path: str, output_dir: str) -> str:
    """Get relative path compatible with Quarto rendering for table images.
    
    For Quarto, image paths should be relative from where the QMD file is located.
    Since we now place QMD files in the user's configured report directory,
    image paths should be relative to that directory.
    
    Args:
        img_path: Full table image path (e.g., 'results/report/tables/table_1.png')
        output_dir: Directory where the QMD file is located (report directory)
        
    Returns:
        Relative path from QMD location with forward slashes for Quarto compatibility
    """
    # Get path relative to where the QMD file is located (report directory)
    # Since QMD is now placed in the report directory, images should be relative to that
    try:
        rel_path = os.path.relpath(img_path, output_dir).replace('\\', '/')
        return rel_path
    except ValueError:
        # If paths are on different drives or can't be made relative, use absolute
        return img_path.replace('\\', '/')

def get_layout_table_style(sync_files: bool = True) -> Dict[str, Any]:
    """Get layout-specific table styling configuration.
    
    Args:
        sync_files: Whether to sync configuration files from source
    
    Returns:
        Dictionary containing table styling configuration for current layout
    """
    config = _load_table_config(sync_files=sync_files)
    
    # Return styling configuration
    styling_config = {}
    
    if 'styling' in config:
        styling_config.update(config['styling'])
        
    if 'colors' in config:
        styling_config.update(config['colors'])
        
    if 'layout_colors' in config:
        styling_config['layout_colors'] = config['layout_colors']
        
    if 'table_colors' in config:
        styling_config['table_colors'] = config['table_colors']
        
    return styling_config

def get_layout_table_typography(sync_files: bool = True) -> Dict[str, Any]:
    """Get layout-specific table typography configuration.
    
    Args:
        sync_files: Whether to sync configuration files from source
        
    Returns:
        Dictionary containing table typography configuration for current layout
    """
    # Get current layout
    from ePy_docs.components.pages import get_current_layout
    from ePy_docs.core.setup import _load_cached_files, get_filepath
    
    current_layout_name = get_current_layout()
    
    # Load text configuration for layout-specific typography
    config_path = get_filepath('files.configuration.components.text_json', sync_files)
    format_config = _load_cached_files(config_path, sync_files=sync_files)
    
    # Get layout-specific typography from format.json following Lord's decrees
    if 'layout_styles' not in format_config:
        raise KeyError("TABLE TYPOGRAPHY FAILURE: 'layout_styles' missing from format configuration")
    
    if current_layout_name not in format_config['layout_styles']:
        available_layouts = list(format_config['layout_styles'].keys())
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: Layout '{current_layout_name}' not found. Available: {available_layouts}")
    
    layout_config = format_config['layout_styles'][current_layout_name]
    
    if 'typography' not in layout_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'typography' not found in layout '{current_layout_name}'")
    
    if 'table_text' not in layout_config['typography']:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'table_text' not found in typography for layout '{current_layout_name}'")
    
    table_text_config = layout_config['typography']['table_text']
    
    # Extract typography configuration following hierarchical structure
    typography_config = {}
    
    # Content (table body) configuration
    if 'content' not in table_text_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'content' not found in table_text for layout '{current_layout_name}'")
    content_config = table_text_config['content']
    
    if 'font_size' not in content_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'font_size' not found in table_text.content for layout '{current_layout_name}'")
    typography_config['font_size'] = content_config['font_size']
    
    if 'font_family' not in content_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'font_family' not found in table_text.content for layout '{current_layout_name}'")
    typography_config['font_family'] = content_config['font_family']
    
    # Header configuration
    if 'header' not in table_text_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'header' not found in table_text for layout '{current_layout_name}'")
    header_config = table_text_config['header']
    
    if 'font_size' not in header_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'font_size' not found in table_text.header for layout '{current_layout_name}'")
    typography_config['header_font_size'] = header_config['font_size']
    
    # Caption/title configuration
    if 'caption' not in table_text_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'caption' not found in table_text for layout '{current_layout_name}'")
    caption_config = table_text_config['caption']
    
    if 'font_size' not in caption_config:
        raise KeyError(f"TABLE TYPOGRAPHY FAILURE: 'font_size' not found in table_text.caption for layout '{current_layout_name}'")
    typography_config['title_font_size'] = caption_config['font_size']
        
    return typography_config

def format_cell_text_with_math(text: str, config: Dict[str, Any] = None) -> str:
    """Format cell text to handle superscripts and subscripts using format.json configuration.
    
    Args:
        text: Original text that may contain mathematical notation
        config: Table configuration (optional, will load if not provided)
        
    Returns:
        Formatted text with proper mathematical notation
    """
    if config is None:
        config = _load_table_config()
    
    text_str = str(text)
    
    # Load formatting rules from format.json using centralized cache system as lord supremo commands
    try:
        from ePy_docs.core.setup import _load_cached_files, get_filepath
        format_config = _load_cached_files(get_filepath('files.configuration.units.format_json'), sync_files=False)
        
        # Get matplotlib formatting (for table images)
        matplotlib_superscripts = format_config.get('matplotlib', {}).get('superscripts', {})
        unicode_superscripts = format_config.get('unicode', {}).get('superscripts', {})
        
        # Combine both sources (matplotlib has priority for table images)
        unit_map = {**unicode_superscripts, **matplotlib_superscripts}
        
    except Exception as e:
        # Fallback to quarto processing if format.json fails
        try:
            from ePy_docs.core.quarto import process_mathematical_text
            return process_mathematical_text(text_str, 'academic', False, 'html')
        except Exception:
            return text_str
    
    processed_text = text_str
    
    # Apply formatting rules from format.json
    import re
    for old_pattern, new_pattern in unit_map.items():
        processed_text = re.sub(re.escape(old_pattern), new_pattern, processed_text, flags=re.IGNORECASE)
    
    # Use quarto processing for any remaining mathematical notation
    try:
        from ePy_docs.core.quarto import process_mathematical_text
        final_text = process_mathematical_text(processed_text, 'academic', False, 'html')
        return final_text
    except Exception:
        return processed_text

def _rgb_to_hex(color_value: Any) -> str:
    """Convert RGB color to hex format.
    
    Args:
        color_value: Color in various formats (hex, RGB tuple, RGB string)
        
    Returns:
        Color in hex format
    """
    if isinstance(color_value, str):
        if color_value.startswith('#'):
            return color_value
        elif color_value.startswith('rgb(') and color_value.endswith(')'):
            # Parse RGB string like "rgb(255, 0, 0)"
            rgb_str = color_value[4:-1]  # Remove "rgb(" and ")"
            rgb_values = [int(x.strip()) for x in rgb_str.split(',')]
            return f"#{rgb_values[0]:02x}{rgb_values[1]:02x}{rgb_values[2]:02x}"
    elif isinstance(color_value, (list, tuple)) and len(color_value) >= 3:
        # Convert RGB tuple/list to hex
        return f"#{int(color_value[0]):02x}{int(color_value[1]):02x}{int(color_value[2]):02x}"
    
    # Return as-is if already in correct format or can't parse
    return str(color_value)

def create_formatted_table(df: pd.DataFrame, title: str = "", sync_files: bool = True, 
                          custom_config: Dict[str, Any] = None) -> str:
    """Create a formatted table respecting all configuration files.
    
    Args:
        df: DataFrame to format
        title: Table title
        sync_files: Whether to sync configuration files from source  
        custom_config: Optional custom configuration to override defaults
        
    Returns:
        Formatted table as string (HTML or Markdown depending on configuration)
    """
    # Load unified configuration
    config = _load_table_config(sync_files=sync_files)
    
    if custom_config:
        # Deep merge custom configuration
        import copy
        config = copy.deepcopy(config)
        for key, value in custom_config.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
    
    # Get styling and typography
    styling = get_layout_table_style(sync_files=False)  # Already loaded
    typography = get_layout_table_typography(sync_files=False)  # Already loaded
    
    # Apply mathematical notation formatting to all text cells
    formatted_df = df.copy()
    for col in formatted_df.columns:
        if formatted_df[col].dtype == 'object':  # Text columns
            formatted_df[col] = formatted_df[col].apply(
                lambda x: format_cell_text_with_math(x, config) if pd.notna(x) else x
            )
    
    # Also format column names for mathematical notation
    formatted_columns = {}
    for col in formatted_df.columns:
        formatted_col = format_cell_text_with_math(str(col), config)
        formatted_columns[col] = formatted_col
    formatted_df = formatted_df.rename(columns=formatted_columns)
    
    # Format title with mathematical notation
    if title:
        title = format_cell_text_with_math(title, config)
    
    # Get display configuration
    display_config = config.get('display', {})
    output_format = display_config.get('format', 'html')
    
    if output_format.lower() == 'html':
        return _create_html_table(formatted_df, title, styling, typography, display_config)
    else:
        return _create_markdown_table(formatted_df, title, styling, typography, display_config)

def _create_html_table(df: pd.DataFrame, title: str, styling: Dict[str, Any], 
                      typography: Dict[str, Any], display_config: Dict[str, Any]) -> str:
    """Create HTML formatted table with full styling."""
    
    # Get colors from styling config
    table_colors = styling.get('table_colors', {})
    header_bg = table_colors.get('header_background', '#f0f0f0')
    header_text = table_colors.get('header_text', '#000000')
    row_bg = table_colors.get('row_background', '#ffffff')
    row_text = table_colors.get('row_text', '#000000')
    alt_row_bg = table_colors.get('alt_row_background', '#f9f9f9')
    border_color = table_colors.get('border', '#cccccc')
    
    # Convert RGB to hex if needed
    header_bg = _rgb_to_hex(header_bg)
    header_text = _rgb_to_hex(header_text)
    row_bg = _rgb_to_hex(row_bg)
    row_text = _rgb_to_hex(row_text)
    alt_row_bg = _rgb_to_hex(alt_row_bg)
    border_color = _rgb_to_hex(border_color)
    
    # Get typography settings
    font_size = typography.get('font_size', 9)
    header_font_size = typography.get('header_font_size', 10)
    title_font_size = typography.get('title_font_size', 9)
    font_family = typography.get('font_family', 'Arial')
    
    # Build HTML
    html_parts = []
    
    # Table title
    if title:
        html_parts.append(f'''
    <div style="text-align: center; font-size: {title_font_size}pt; font-family: {font_family}; 
                font-weight: bold; margin-bottom: 10px;">
        {title}
    </div>''')
    
    # Table opening with styling
    table_style = f'''
    border-collapse: collapse;
    width: 100%;
    font-family: {font_family};
    font-size: {font_size}pt;
    border: 1px solid {border_color};
    '''
    
    html_parts.append(f'<table style="{table_style}">')
    
    # Table header
    html_parts.append('<thead>')
    html_parts.append('<tr>')
    for col in df.columns:
        header_style = f'''
        background-color: {header_bg};
        color: {header_text};
        font-size: {header_font_size}pt;
        font-weight: bold;
        padding: 8px;
        border: 1px solid {border_color};
        text-align: center;
        '''
        html_parts.append(f'<th style="{header_style}">{col}</th>')
    html_parts.append('</tr>')
    html_parts.append('</thead>')
    
    # Table body
    html_parts.append('<tbody>')
    for idx, row in df.iterrows():
        # Alternate row colors
        bg_color = alt_row_bg if idx % 2 == 1 else row_bg
        html_parts.append('<tr>')
        
        for col in df.columns:
            cell_style = f'''
            background-color: {bg_color};
            color: {row_text};
            padding: 6px 8px;
            border: 1px solid {border_color};
            text-align: left;
            '''
            cell_value = row[col] if pd.notna(row[col]) else ''
            html_parts.append(f'<td style="{cell_style}">{cell_value}</td>')
        
        html_parts.append('</tr>')
    html_parts.append('</tbody>')
    html_parts.append('</table>')
    
    return ''.join(html_parts)

def _create_markdown_table(df: pd.DataFrame, title: str, styling: Dict[str, Any],
                          typography: Dict[str, Any], display_config: Dict[str, Any]) -> str:
    """Create Markdown formatted table."""
    
    md_parts = []
    
    # Table title
    if title:
        md_parts.append(f"\n**{title}**\n")
    
    # Create markdown table
    if len(df.columns) > 0:
        # Header row
        headers = [str(col) for col in df.columns]
        md_parts.append('| ' + ' | '.join(headers) + ' |')
        
        # Separator row
        md_parts.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
        
        # Data rows
        for _, row in df.iterrows():
            row_data = []
            for col in df.columns:
                cell_value = row[col] if pd.notna(row[col]) else ''
                row_data.append(str(cell_value))
            md_parts.append('| ' + ' | '.join(row_data) + ' |')
    
    return '\n'.join(md_parts) + '\n'

class TableFormatter:
    """Handles table data formatting and text processing."""

    @staticmethod
    def format_cell_text(text, max_words_per_line, is_header=False):
        """Format cell text by limiting words per line and applying text formatting."""
        text = str(text)
        
        # Apply advanced text formatting (superscripts/subscripts) before word wrapping
        formatted_text = apply_text_formatting(text)
        
        # Check if text contains bullet points, numbered lists, or newlines that should be preserved
        if '•' in formatted_text or '\n' in formatted_text or re.search(r'\d+\.\s+', formatted_text):
            # Preserve existing line structure for bullet points, numbered lists, and formatted text
            lines = formatted_text.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # If line has bullet point or is numbered, preserve it
                if line.startswith('•') or re.match(r'^\d+\.\s+', line):
                    formatted_lines.append(line)
                else:
                    # Apply word wrapping to non-bullet/non-numbered lines
                    words = line.split()
                    if len(words) <= max_words_per_line:
                        formatted_lines.append(line)
                    else:
                        # Break long lines into chunks
                        current_line = []
                        for word in words:
                            if len(current_line) < max_words_per_line:
                                current_line.append(word)
                            else:
                                formatted_lines.append(' '.join(current_line))
                                current_line = [word]
                        if current_line:
                            formatted_lines.append(' '.join(current_line))
            
            return '\n'.join(formatted_lines)
        
        # Original logic for simple text
        words = formatted_text.split()
        lines = []
        current_line = []
        
        # Use more aggressive wrapping for headers with special characters
        if is_header and '(' in formatted_text:
            parts = formatted_text.split('(')
            if len(parts) >= 2:
                lines.append(parts[0].strip())
                lines.append(f"({parts[1].strip()}")
                return '\n'.join(lines)
        
        # Normal word wrapping
        for word in words:
            if len(current_line) < (max_words_per_line if not is_header else 2):
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        return '\n'.join(lines)
    
    @staticmethod
    def format_dataframe(df: pd.DataFrame, max_words_per_line: int, unit_format: str = "unicode") -> Tuple[pd.DataFrame, List[str]]:
        """Format DataFrame for table output.
        
        Args:
            df: DataFrame to format
            max_words_per_line: Maximum words per line for text wrapping
            unit_format: Format to use for unit display ("unicode", "matplotlib", etc.)
        """
        formatted_df = df.copy()
        formatted_columns = []

        # Importar format_unit_display para aplicar a los nombres de columnas y valores
        from ePy_docs.units.converter import format_unit_display
        
        # Load format mappings for table-compatible formatting
        import os
        from ePy_docs.core.setup import _load_cached_files, get_filepath
        
        # No longer need format_mappings - use quarto's autonomous system
        format_mappings = {}  # Empty dict for compatibility
        
        # Format column headers with unit formatting - use specified format
        renamed_columns = {}
        for col in df.columns:
            # Apply unit formatting to column names using specified format
            formatted_col = format_unit_display(str(col), unit_format, format_mappings)
            
            # Apply superscript/subscript formatting from format.json
            formatted_col_with_math = format_cell_text_with_math(str(formatted_col), format_mappings)
            
            if formatted_col_with_math != col:
                renamed_columns[col] = formatted_col_with_math
            
            processed_col = str(formatted_col_with_math)  # Text with math formatting
            formatted_columns.append(TableFormatter.format_cell_text(processed_col, 2, is_header=True))
        
        # Rename columns if any were formatted
        if renamed_columns:
            formatted_df = formatted_df.rename(columns=renamed_columns)
        
        # Format cell contents with unit formatting applied to string values - use specified format
        for col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(
                lambda x: TableFormatter.format_cell_text(
                    format_cell_text_with_math(
                        format_unit_display(str(x), unit_format, format_mappings), 
                        format_mappings
                    ) if isinstance(x, str) else x, 
                    max_words_per_line
                )
            )

        return formatted_df, formatted_columns

class TableDimensionCalculator:
    """Calculates table dimensions for optimal display."""
    
    @staticmethod
    def calculate_dimensions(formatted_df: pd.DataFrame, formatted_columns: List[str]) -> Tuple[List[float], List[int], int]:
        """Calculate column widths, row heights, and header height."""
        # Load configuration for row height calculation
        config = _load_table_config()
        
        # Get display configuration for layout and alignment settings
        display_config = config['display']
        auto_row_height = display_config['auto_row_height']
        min_row_height_factor = display_config['min_row_height_factor']
        line_spacing = display_config['line_spacing']
        min_column_width_inches = display_config['min_column_width_inches']
        max_width_inches = display_config['max_width_inches']
        
        # Get typography configuration from unified system
        typography = get_layout_table_typography()
        font_size = typography['font_size']
        
        def get_column_width(col_content):
            # Calcular el ancho basado en la línea más larga del contenido
            max_chars = max(len(str(x).split('\n')[0]) for x in col_content)
            # Ser más generoso con el ancho para evitar texto comprimido
            return max_chars / 5
        
        def get_row_height(row):
            max_lines = 1
            for cell in row:
                # Contar líneas reales en el contenido de la celda
                lines = len(str(cell).split('\n'))
                max_lines = max(max_lines, lines)
            
            if auto_row_height:
                # La altura base por línea debe ser fija, no proporcional al padding
                # El padding se aplica separadamente como espacio adicional
                base_height_per_line = min_row_height_factor
                # Ajustar por tamaño de fuente
                font_factor = max(1.0, font_size / 8.0)  # Base size is 8pt
                # La altura total es: (número de líneas * altura base) + padding fijo
                content_height = max_lines * base_height_per_line * font_factor
                # line_spacing controla el espacio entre líneas dentro de la celda, no el padding total
                adjusted_height = content_height * line_spacing
                return max(max_lines, adjusted_height)
            else:
                # Usar solo el número de líneas como antes
                return max_lines
        
        # Calculate initial column widths based on content
        col_widths = [get_column_width([col] + formatted_df[col].values.tolist()) for col in formatted_df.columns]
        
        # Convert to inches and apply minimum width constraint
        col_widths_inches = []
        for width in col_widths:
            # Convert relative width to approximate inches (rough estimation)
            approx_inches = (width / sum(col_widths)) * max_width_inches
            # Apply minimum width constraint
            final_width = max(approx_inches, min_column_width_inches)
            col_widths_inches.append(final_width)
        
        # Normalize to relative proportions while respecting the total width constraint
        total_width_inches = sum(col_widths_inches)
        if total_width_inches > max_width_inches:
            # Scale down proportionally if total exceeds maximum
            scale_factor = max_width_inches / total_width_inches
            col_widths_inches = [w * scale_factor for w in col_widths_inches]
            total_width_inches = max_width_inches
        
        # Convert back to relative proportions for matplotlib
        col_widths = [w / total_width_inches for w in col_widths_inches]
        
        row_heights = [get_row_height(row) for _, row in formatted_df.iterrows()]
        
        # Calculate header height with the same auto-adjustment logic
        header_lines = [len(str(col).split('\n')) for col in formatted_columns]
        max_header_lines = max(header_lines)
        
        if auto_row_height:
            # Apply the same logic to header height
            base_height = max_header_lines * min_row_height_factor
            font_factor = max(1.0, font_size / 8.0)
            header_row_height = max(max_header_lines, int(base_height * font_factor * line_spacing))
        else:
            header_row_height = max_header_lines
        
        return col_widths, row_heights, header_row_height

class IntelligentColorManager:
    """Manages intelligent color application for table cells based on column analysis."""
    
    @staticmethod
    def analyze_columns(df: pd.DataFrame, highlight_columns: Optional[List[str]] = None) -> Dict[str, str]:
        """Analyze columns to determine appropriate coloring strategy using category rules.
        
        Returns:
            Dict mapping column names to coloring strategy ('categorical', 'numeric', 'none')
        """
        columns_to_analyze = highlight_columns if highlight_columns else df.columns
        column_strategies = {}
        
        for col in columns_to_analyze:
            if col not in df.columns:
                continue
                
            # Use the new categorization system
            sample_values = df[col].dropna().head(10).tolist() if len(df[col]) > 0 else []
            category = categorize_column(col, sample_values)
            
            # Determine coloring strategy based on category and data type
            strategy = 'none'
            
            if category in ['nodes', 'dimensions']:
                # Coordinate/dimension columns should use numeric gradient
                strategy = 'numeric' if is_numeric_dtype(df[col]) else 'none'
                
            elif category in ['status', 'support', 'elements', 'material', 'design']:
                # These categories work well with categorical coloring
                strategy = 'categorical'
                
            elif category in ['forces', 'properties', 'analysis']:
                # Force/property columns prefer numeric gradients for intensity
                strategy = 'numeric' if is_numeric_dtype(df[col]) else 'categorical'
                
            else:
                # General category - decide based on data characteristics
                if is_numeric_dtype(df[col]):
                    unique_count = df[col].nunique()
                    total_count = len(df[col])
                    
                    # For numeric columns, prefer gradient unless very low cardinality
                    if unique_count >= 4 or unique_count > total_count * 0.5:
                        strategy = 'numeric'
                    else:
                        strategy = 'categorical'
                elif df[col].dtype == 'object' and df[col].nunique() <= 10:
                    strategy = 'categorical'
            
            column_strategies[col] = strategy
        
        return column_strategies

    @staticmethod
    def get_category_colors(category: str) -> Dict[str, str]:
        """Get colors for a specific category using the new categorization system."""
        try:
            # Use the new coloring scheme system
            color_scheme = get_column_coloring_scheme(category)
            
            if color_scheme:
                return color_scheme
            
            # No fallback - require explicit categorization
            raise ValueError(f"Color scheme not found for category '{category}' in the categorization system")
            
        except Exception as e:
            # No fallback warnings - let errors propagate
            raise e

    @staticmethod
    def apply_intelligent_coloring(df: pd.DataFrame, formatted_df: pd.DataFrame, 
                                 highlight_columns: Optional[List[str]] = None,
                                 color_config: Optional[TableColorConfig] = None
                                 ) -> List[List[Tuple[float, float, float, float]]]:
        """Apply intelligent coloring based on column analysis."""
        cell_colors = [[(1, 1, 1, 0)] * len(formatted_df.columns) for _ in range(len(formatted_df))]
        
        # Use all columns for coloring if not specified
        if highlight_columns is None:
            highlight_columns = list(df.columns)
        elif highlight_columns == []:
            # Empty list means no coloring - return white colors
            return cell_colors
            
        # Analyze columns to determine coloring strategy
        column_strategies = IntelligentColorManager.analyze_columns(df, highlight_columns)
        orig_to_formatted_col_map = {col: i for i, col in enumerate(formatted_df.columns)}
        
        for col, strategy in column_strategies.items():
            if col not in df.columns:
                continue
                
            col_idx_orig = list(df.columns).index(col)
            if col not in orig_to_formatted_col_map:
                raise ValueError(f"Column '{col}' not found in formatted column mapping")
            col_idx = orig_to_formatted_col_map[col]
            
            if strategy == 'categorical':
                # Apply categorical coloring using new categorization system
                sample_values = df[col].dropna().head(10).tolist() if len(df[col]) > 0 else []
                category = categorize_column(col, sample_values)
                
                # Get coloring scheme for this category
                category_colors = get_column_coloring_scheme(category)
                if category_colors:
                        match_count = 0
                        for row_idx in range(len(df)):
                            cell_value = str(df.iloc[row_idx, col_idx_orig]).strip().lower()
                            
                            # Try exact match first
                            color_hex = category_colors.get(cell_value)
                            if not color_hex:
                                # Try partial match
                                for key, hex_color in category_colors.items():
                                    if key in cell_value or cell_value in key:
                                        color_hex = hex_color
                                        break
                            
                            if color_hex:
                                try:
                                    color_rgb = mcolors.hex2color(color_hex)
                                    cell_colors[row_idx][col_idx] = (*color_rgb, 0.7)
                                    match_count += 1
                                except Exception:
                                    continue
            
            elif strategy == 'numeric' and color_config and color_config.palette:
                # Apply gradient coloring
                palette_name = color_config.palette
                cmap_func = get_custom_colormap(palette_name)
                col_values = df[col]
                
                if len(col_values) > 0 and col_values.max() != col_values.min():
                    for row_idx in range(len(df)):
                        if pd.notna(col_values.iloc[row_idx]):
                            norm_value = (float(col_values.iloc[row_idx]) - col_values.min()) / \
                                      (col_values.max() - col_values.min())
                            color = (*cmap_func(norm_value)[:-1], color_config.alpha)
                            cell_colors[row_idx][col_idx] = color
        
        return cell_colors

def create_table_image(df: pd.DataFrame, output_dir: str, table_number: Union[int, str], 
                     title: Optional[str] = None, highlight_columns: Optional[List[str]] = None,
                     palette_name: str = None, dpi: int = 300,
                     font_size: Optional[int] = None, header_font_size: Optional[int] = None,
                     title_font_size: Optional[int] = None,
                     header_color: str = None, padding: Optional[int] = None, alignment: str = 'center',
                     hide_columns: Union[str, List[str]] = None,
                     filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]] = None,
                     sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                     n_rows: Optional[int] = None) -> str:
    """Create a table image with configuration from tables.json.
    
    Args:
        df: DataFrame to display
        output_dir: Directory to save the image
        table_number: Table number for file naming
        title: Optional title for the table (used for file naming only, not displayed in image)
        highlight_columns: Columns to apply intelligent coloring to
        palette_name: Color palette for numeric columns (required)
        dpi: Image resolution (required)
        font_size: Font size for table cells (required)
        header_font_size: Font size for table header (required)
        title_font_size: Font size for title (required)
        header_color: Background color for table header (required)
        padding: Cell padding (required)
        alignment: Text alignment in cells
        hide_columns: Column name(s) to hide from the table
        filter_by: Filter rows by column content
        sort_by: Sort rows by column(s)
        n_rows: Limit number of rows to show
        
    Returns:
        Path to the generated image file
    """
    # Load configuration from tables.json and typography from text.json
    config = _load_table_config()
    typography = get_layout_table_typography()
    
    # Get current layout and header color from colors.json
    from ePy_docs.components.pages import get_current_layout, _get_color_direct
    current_layout_name = get_current_layout()
    
    # Get header color specific to current layout from colors.json
    try:
        layout_header_color = _get_color_direct(f"layout_styles.{current_layout_name}.typography.header_color", format_type="hex")
    except Exception:
        # Fallback to default color from tables.json if layout color not found
        layout_header_color = config.get('default_header_color', '#002184')
    
    # Get current layout configuration to determine default palette
    from ePy_docs.core.setup import _load_cached_files, get_filepath, get_current_project_config
    
    # Use project sync_files setting instead of hardcoding
    current_config = get_current_project_config()
    sync_files = current_config.settings.sync_files if current_config else False
    
    config_path = get_filepath('files.configuration.units.format_json', sync_files)
    report_config = _load_cached_files(config_path, sync_files=sync_files)
    
    # The layouts are in the tables config under 'layout_styles'
    table_layouts = config['layout_styles']
    current_layout_config = table_layouts[current_layout_name]
    
    # Use config values when parameters are None
    palette_name = palette_name or current_layout_config.get('palette_name', 'engineering')
    dpi = dpi or config['display'].get('dpi', 300)
    header_color = header_color or layout_header_color
    font_size = font_size or typography['font_size']
    header_font_size = header_font_size or typography['header_font_size']
    title_font_size = title_font_size or typography['title_font_size']
    padding = padding or config['display'].get('padding', 4)
    
    # Apply unit conversion and processing pipeline with configurable decimal places
    df_processed, conversion_log = prepare_dataframe_for_display(df, value_type="general_numeric")

    # Apply comprehensive preprocessing (filtering, sorting, row limiting, column management)
    df_display = apply_table_preprocessing(
        df_processed, 
        hide_columns=hide_columns,
        filter_by=filter_by,
        sort_by=sort_by,
        n_rows=n_rows
    )

    # Formatear DataFrame con formato específico para matplotlib
    max_words_per_line = max(1, 8 - len(df_display.columns))
    formatted_df, formatted_columns = TableFormatter.format_dataframe(df_display, max_words_per_line, "matplotlib")
    
    # Calculate dimensions
    col_widths, row_heights, header_row_height = TableDimensionCalculator.calculate_dimensions(
        formatted_df, formatted_columns
    )
    
    # Set up color configuration
    color_config = TableColorConfig(
        palette=palette_name,
        header_color=header_color,
        alpha=0.7
    )
    
    # Apply intelligent coloring ONLY if highlight_columns is provided (colored tables)
    if highlight_columns is not None:
        cell_colors = IntelligentColorManager.apply_intelligent_coloring(
            df_display, formatted_df, highlight_columns, color_config
        )
    else:
        # No coloring for regular tables - use white/transparent cells
        cell_colors = [[(1, 1, 1, 0)] * len(formatted_df.columns) for _ in range(len(formatted_df))]
    
    # Load table configuration - use direct config, no hardcoded values
    table_config_direct = _load_table_config()
    
    # Load table configuration for base cell height
    display_config = table_config_direct['display']
    base_cell_height = display_config['base_cell_height_inches']
    
    # Always use PDF width for image generation (images are created at full resolution)
    # HTML width control happens at the markdown level with fig-width parameter
    fig_width = display_config['max_width_inches']
    
    # Reduce excessive padding for header - adjust to text height
    total_height = header_row_height * base_cell_height  # More precise header height
    for row_height in row_heights:
        total_height += row_height * base_cell_height
    fig_height = total_height
    
    # Create figure with clean layout (no titles in images)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')
    
    header_colors = [header_color] * len(formatted_df.columns)
    
    # Create the table using the full figure area
    table = ax.table(
        cellText=formatted_df.values,
        colLabels=formatted_columns,
        cellLoc=alignment.lower(),
        bbox=[0, 0, 1, 1],
        colColours=header_colors,
        cellColours=cell_colors,
        colWidths=col_widths
    )
    
    # Apply styling to table cells
    _apply_table_styling(table, row_heights, header_row_height, base_cell_height, 
                        fig_height, font_size, header_font_size, header_colors, 
                        padding, formatted_df, alignment)
    
    # Apply layout-specific custom styles
    _apply_custom_table_styles(table, current_layout_name, config)
    
    # CRUCIAL: Configure multiline text rendering for cells with bullets
    _configure_multiline_text(table, formatted_df, formatted_columns, typography)
    
    # Rather than using tight_layout which can cause issues with axes,
    # we've already precisely positioned our title and table axes
    
    # Save image with properly spaced title and table
    # Handle both integer and string table numbers for file naming
    if isinstance(table_number, str):
        # Para strings que representan enteros
        try:
            num = int(table_number)
            img_path = os.path.join(output_dir, f"table_{num}.png")
        except ValueError:
            # Para strings arbitrarios
            img_path = os.path.join(output_dir, f"table_{table_number}.png")
    else:
        # Para enteros normales - usar formato simple sin ceros
        img_path = os.path.join(output_dir, f"table_{table_number}.png")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save with a small border around the entire figure
    try:
        plt.savefig(img_path, bbox_inches='tight', dpi=dpi, facecolor='white', 
                   pad_inches=0.2, transparent=False)
        plt.close(fig)
        
        # Verify the file was actually created
        if not os.path.exists(img_path):
            raise RuntimeError(f"Failed to create table image at {img_path}")
            
    except Exception as e:
        plt.close(fig)  # Ensure figure is closed even on error
        raise RuntimeError(f"Error creating table image {img_path}: {str(e)}")
    
    # Display image in notebook if running in Jupyter environment
    try:
        from IPython.display import Image, display
        display(Image(img_path))
    except (ImportError, Exception):
        # Silently skip display if not in Jupyter or any other error
        pass
    
    return img_path

def _apply_table_styling(table, row_heights, header_row_height, base_cell_height, 
                        fig_height, font_size, header_font_size, header_colors, 
                        padding, formatted_df, alignment):
    """Apply styling to table cells."""
    # Set font sizes
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    
    if header_font_size != font_size:
        for idx in range(len(formatted_df.columns)):
            cell = table._cells[(0, idx)]
            cell.get_text().set_fontsize(header_font_size)
    
    # Create header text colors for contrast
    header_text_colors = []
    for bg_color in header_colors:
        if isinstance(bg_color, str) and bg_color.startswith('#'):
            # Convert hex to RGB for brightness calculation
            try:
                rgb = mcolors.hex2color(bg_color)
                brightness = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                header_text_colors.append('white' if brightness < 0.5 else 'black')
            except:
                header_text_colors.append('white')
        else:
            header_text_colors.append('white')
    
    # Apply header text colors
    for idx, color in enumerate(header_text_colors):
        cell = table._cells[(0, idx)]
        cell.get_text().set_color(color)
    
    # Apply cell padding and heights - USAR EL PARAMETRO PADDING CORRECTAMENTE
    # El padding debe ser constante independientemente del número de líneas
    padding_fraction = padding / 100.0 / 20  # Convertir a fracción para matplotlib
    
    for pos, cell in table._cells.items():
        # Aplicar padding constante a todas las celdas
        cell.PAD = padding_fraction
        row = pos[0]
        
        # Fix vertical alignment - set to center/middle for all cells
        cell.get_text().set_verticalalignment('center')
        
        # Apply horizontal alignment based on parameter, but ensure proper alignment
        horizontal_align = alignment.lower() if alignment.lower() in ['left', 'center', 'right'] else 'center'
        cell.get_text().set_horizontalalignment(horizontal_align)
        
        # La altura de la celda debe ser proporcional al contenido + padding constante
        if row == 0:
            # Header row: usar la altura calculada
            cell_height_value = (header_row_height * base_cell_height) / fig_height
        else:
            # Content rows: usar la altura calculada (que ya incluye el contenido apropiado)
            lines_needed = row_heights[row - 1]
            cell_height_value = (lines_needed * base_cell_height) / fig_height
        
        cell.set_height(cell_height_value)

def _get_best_font_for_text(text: str) -> str:
    """
    Wrapper for get_best_font_for_text from text.py module.
    """
    from ePy_docs.components.text import get_best_font_for_text
    return get_best_font_for_text(text)

def _apply_font_fallback(text_obj, formatted_text: str):
    """
    Wrapper for apply_font_fallback from text.py module.
    """
    from ePy_docs.components.text import apply_font_fallback
    apply_font_fallback(text_obj, formatted_text)

def _configure_multiline_text(table, formatted_df, formatted_columns, typography):
    """Configure multiline text rendering for table cells with proper bullet display and text formatting."""
    
    # Get font family from typography configuration
    font_family = typography.get('font_family', 'Arial')
    
    # Process header cells
    for col_idx, col_text in enumerate(formatted_columns):
        cell = table._cells[(0, col_idx)]
        # Apply text formatting to header
        formatted_text = apply_text_formatting(str(col_text))
        text_obj = cell.get_text()
        _apply_font_fallback(text_obj, formatted_text)
        # Keep center alignment for headers
        text_obj.set_horizontalalignment('center')
        text_obj.set_verticalalignment('center')
    
    # Process data cells
    for row_idx in range(len(formatted_df)):
        for col_idx, col_name in enumerate(formatted_df.columns):
            cell_value = formatted_df.iloc[row_idx, col_idx]
            cell = table._cells[(row_idx + 1, col_idx)]  # +1 because row 0 is header
            
            # Apply text formatting to all text cells
            if isinstance(cell_value, str):
                formatted_text = apply_text_formatting(cell_value)
                text_obj = cell.get_text()
                _apply_font_fallback(text_obj, formatted_text)
                
                # Check if cell contains multiline text, bullets, or numbered lists
                if '\n' in cell_value or '•' in cell_value or re.search(r'\d+\.\s+', cell_value):
                    # For cells with bullets or numbered lists, use left alignment but keep vertical center
                    # This provides better readability for bullet lists while maintaining overall table consistency
                    if '•' in cell_value or re.search(r'\d+\.\s+', cell_value):
                        text_obj.set_horizontalalignment('left')   # Left align for bullets/numbers readability
                        text_obj.set_verticalalignment('center')   # Center vertically to match other cells
                    else:
                        # For multiline text without bullets, maintain center alignment
                        text_obj.set_verticalalignment('center')
                else:
                    # For single-line text cells, maintain default alignment
                    text_obj.set_verticalalignment('center')
            else:
                # For non-string cells, still apply basic formatting
                text_obj = cell.get_text()
                text_obj.set_fontfamily(font_family)
                text_obj.set_verticalalignment('center')

def create_split_table_images(df: pd.DataFrame, output_dir: str, base_table_number: int,
                            title: Optional[str] = None, highlight_columns: Optional[List[str]] = None,
                            palette_name: str = None, dpi: int = 300,
                            font_size: Optional[int] = None, header_font_size: Optional[int] = None,
                            title_font_size: Optional[int] = None,
                            header_color: str = None, padding: Optional[int] = None, alignment: str = 'center',
                            hide_columns: Union[str, List[str]] = None,
                            filter_by: Union[Tuple[str, Union[str, int, float, List]], List[Tuple[str, Union[str, int, float, List]]]] = None,
                            sort_by: Union[str, Tuple[str, str], List[Union[str, Tuple[str, str]]]] = None,
                            n_rows: Optional[int] = None, max_rows_per_table: Optional[Union[int, float, List[Union[int, float]]]] = None) -> List[str]:
    """Create multiple table images for large DataFrames with automatic splitting.
    
    Args:
        df: DataFrame to display
        output_dir: Directory to save the images
        base_table_number: Base table number for file naming
        title: Optional title for the table
        highlight_columns: Columns to apply intelligent coloring to
        palette_name: Color palette for numeric columns
        dpi: Image resolution
        font_size: Font size for table cells (if None, loads from style manager)
        header_font_size: Font size for table header (if None, loads from style manager)
        header_color: Background color for table header
        padding: Cell padding (if None, loads from style manager)
        alignment: Text alignment in cells
        hide_columns: Column name(s) to hide from the table (string or list of strings)
        filter_by: Filter rows by column content
        sort_by: Sort rows by column(s)
        n_rows: Limit number of rows after filtering and sorting
        max_rows_per_table: Maximum rows per table before splitting. Can be:
                           - int/float: Fixed size for all chunks
                           - List[int/float]: Custom sizes for each subtable. Creates additional table for remainder.
                           - None: loads default from style manager
        
    Returns:
        List of paths to the generated image files
    """
    # Load configuration from PDFStyleManager only if max_rows_per_table is not specified
    if max_rows_per_table is None:
        try:
            from ePy_docs.components.pages import PDFStyleManager
            style_manager = PDFStyleManager()
            table_style_config = style_manager.get_table_style_config()
            max_rows_per_table = table_style_config.max_rows_per_table
            
            # If still None after loading from config, raise an error
            if max_rows_per_table is None:
                raise ValueError(
                    "max_rows_per_table must be specified either as a parameter or in the style configuration. "
                    "Please provide either:\n"
                    "1. max_rows_per_table parameter (int, float, or list)\n"
                    "2. Configure 'max_rows_per_table' in your styles.json file"
                )
        except Exception as e:
            raise ValueError(
                f"Could not load max_rows_per_table from configuration: {e}\n"
                "Please provide max_rows_per_table as a parameter (int, float, or list)"
            )

    # Apply filtering and sorting first using the new preprocessing function
    df_processed = apply_table_preprocessing(
        df, 
        hide_columns=None,  # Don't hide columns yet - we need them for splitting
        filter_by=filter_by,
        sort_by=sort_by,
        n_rows=n_rows
    )
    
    # Check if we need to split the table
    needs_splitting = False
    
    if isinstance(max_rows_per_table, (list, tuple)):
        # Always split when using a list of sizes
        needs_splitting = True
    elif isinstance(max_rows_per_table, (int, float)):
        # Traditional logic: split if rows exceed max_rows_per_table
        needs_splitting = len(df_processed) > max_rows_per_table
    if not needs_splitting:
        # Single table - use the original base table number (no decimal)
        img_path = create_table_image(
            df=df_processed,
            output_dir=output_dir,
            table_number=base_table_number,  # Use original base number for single tables
            title=title,
            highlight_columns=highlight_columns,
            palette_name=palette_name,
            dpi=dpi,
            font_size=font_size,
            header_font_size=header_font_size,
            title_font_size=title_font_size,
            header_color=header_color,
            padding=padding,
            alignment=alignment,
            hide_columns=hide_columns,
            filter_by=None,  # Already applied
            sort_by=None,    # Already applied
            n_rows=None     # Already applied
        )
        return [img_path]
    
    # Split large table into chunks
    df_chunks = split_large_table(df_processed, max_rows_per_table)
    
    img_paths = []
    for i, chunk in enumerate(df_chunks):
        # For table images, use the original title without "(Parte n/m)"
        # The "(Parte n/m)" will be added to the Quarto caption separately
        chunk_title = title  # Keep original title for the image
        
        # Use continuous Arabic numbering for split tables
        # Each split part gets its own sequential number
        table_number_arabic = base_table_number + i
        
        img_path = create_table_image(
            df=chunk,
            output_dir=output_dir,
            table_number=table_number_arabic,  # Use sequential Arabic numbering
            title=chunk_title,
            highlight_columns=highlight_columns,
            palette_name=palette_name,
            dpi=dpi,
            font_size=font_size,
            header_font_size=header_font_size,
            title_font_size=title_font_size,
            header_color=header_color,
            padding=padding,
            alignment=alignment,
            hide_columns=hide_columns,
            filter_by=None,  # Already applied
            sort_by=None,    # Already applied
            n_rows=None     # Already applied
        )
        img_paths.append(img_path)
    
    return img_paths

def categorize_column(column_name: str, sample_values: List[Any] = None) -> str:
    """
    Categorize a column based on its name and sample values using rules from tables.json.
    
    Args:
        column_name: Name of the column to categorize
        sample_values: Optional sample values from the column for additional context
        
    Returns:
        Category name (e.g., 'nodes', 'support', 'status', etc.)
    """
    try:
        config = _load_category_rules()
        category_rules = config['category_rules']
        
        column_name_lower = column_name.lower()
        best_category = 'general'
        best_score = 0
        
        # Check each category for matches with scoring
        for category, rules in category_rules.items():
            score = 0
            
            # Check name keywords (higher weight)
            if 'name_keywords' not in rules:
                continue
            name_keywords = rules['name_keywords']
            for keyword in name_keywords:
                if keyword.lower() in column_name_lower:
                    # Exact match gets higher score
                    if keyword.lower() == column_name_lower:
                        score += 10
                    # Partial match gets lower score
                    else:
                        score += 5
            
            # Check coordinate patterns for specific categories (high weight for exact matches)
            if 'coordinate_patterns' in rules:
                coordinate_patterns = rules['coordinate_patterns']
            if coordinate_patterns:
                # Extract base name (e.g., "x" from "X (mm)")
                col_base = column_name_lower.split('(')[0].strip()
                for pattern in coordinate_patterns:
                    # Only match if it's an exact word match to avoid false positives
                    if pattern.lower() == col_base:
                        score += 15  # Very high score for exact coordinate match
                    # For coordinate patterns, be more strict about partial matches
                    elif col_base.startswith(pattern.lower()) or col_base.endswith(pattern.lower()):
                        score += 8
            
            # Check value keywords if sample values are provided (medium weight)
            if sample_values:
                if 'value_keywords' not in rules:
                    continue
                value_keywords = rules['value_keywords']
                if value_keywords:
                    sample_str = ' '.join(str(val).lower() for val in sample_values[:10] if pd.notna(val))
                    for keyword in value_keywords:
                        if keyword.lower() in sample_str:
                            score += 3
            
            # Update best category if this score is higher
            if score > best_score:
                best_score = score
                best_category = category
        
        # Return best category, or 'general' if no good matches found
        return best_category if best_score > 0 else 'general'
        
    except Exception as e:
        raise ValueError(f"Could not categorize column '{column_name}': {e}")
        return 'general'

def get_column_coloring_scheme(category: str) -> Dict[str, str]:
    """
    Get the appropriate coloring scheme for a category.
    
    Args:
        category: Category name from categorize_column()
        
    Returns:
        Dictionary mapping values to colors
    """
    from ePy_docs.core.setup import _load_cached_files, get_filepath, get_current_project_config
    
    # Use project sync_files setting with direct access
    current_config = get_current_project_config()
    sync_files = current_config.settings.sync_files if current_config else False
    
    config_path = get_filepath('files.configuration.styling.colors_json', sync_files)
    config = _load_cached_files(config_path, sync_files)  # Direct access, no guardian
    
    # Access coloring schemes from new unified structure
    if 'visualization' in config and 'coloring_schemes' in config['visualization']:
        coloring_schemes = config['visualization']['coloring_schemes']
    else:
        # Fallback for old structure
        coloring_schemes = config.get('coloring_schemes', {})
    
    # Map categories to coloring schemes
    scheme_mapping = {
        'status': 'status_based',
        'design': 'status_based',
        'analysis': 'status_based',
        'elements': 'element_based',
        'forces': 'intensity_based',
        'properties': 'intensity_based',
        'general': 'intensity_based'
    }
    
    scheme_name = scheme_mapping[category] if category in scheme_mapping else 'intensity_based'
    
    # Check if the expected scheme exists, otherwise return a fallback
    if scheme_name in coloring_schemes:
        return coloring_schemes[scheme_name]
    else:
        # Fallback to 'default' style if available, otherwise return empty dict
        if 'default' in coloring_schemes:
            return coloring_schemes['default']
        else:
            # Return a minimal working configuration as ultimate fallback
            return {
                'style': 'alternating_rows',
                'alternating_colors': [[255, 255, 255], [248, 250, 252]],
                'header_color': [198, 18, 60]
            }

def get_column_format_rules(category: str) -> Dict[str, Any]:
    """
    Get formatting rules for a specific category.
    
    Args:
        category: Category name from categorize_column()
        
    Returns:
        Dictionary with formatting rules (precision, units, format type)
    """
    format_rules = _load_format_rules_config()
    
    # Map categories to format rules
    rule_mapping = {
        'nodes': 'coordinates',
        'dimensions': 'coordinates', 
        'forces': 'forces',
        'properties': 'stresses',
        'design': 'ratios',
        'analysis': 'ratios'
    }
    
    rule_name = rule_mapping[category] if category in rule_mapping else 'coordinates'
    return format_rules[rule_name]

def add_table_to_content(df: pd.DataFrame, output_dir: Optional[str], table_counter: int,
                        title: str = None, hide_columns: Union[str, List[str]] = None,
                        filter_by: Union[Tuple, List[Tuple]] = None,
                        sort_by: Union[str, Tuple, List] = None,
                        max_rows_per_table: Optional[Union[int, List[int]]] = None,
                        n_rows: Optional[Union[int, List[int]]] = None,
                        source: Optional[str] = None) -> Tuple[List[str], int]:
    """Add simple table to content and return markdown and updated counter.
    
    Args:
        df: DataFrame to create table from
        output_dir: Output directory for table images
        table_counter: Current table counter
        title: Optional table title
        hide_columns: Columns to hide
        filter_by: Filter criteria
        sort_by: Sort criteria
        max_rows_per_table: Maximum rows per table (for splitting)
        n_rows: Take only first N rows (subset)
        source: Optional source information for the table
        
    Returns:
        Tuple of (list of markdown strings, updated table counter)
    """
    from ePy_docs.components.images import ImageProcessor
    from ePy_docs.core.setup import get_absolute_output_directories
    
    # Load table configuration
    tables_config = _load_table_config()
    
    # Get tables directory from setup.json - use full path for dynamic config
    output_dirs = get_absolute_output_directories()
    tables_dir = output_dirs['tables']  # Use full dynamic path
    os.makedirs(tables_dir, exist_ok=True)

    # Handle n_rows as subset (take first N rows) vs max_rows_per_table (split into multiple tables)
    if n_rows is not None:
        df = df.head(n_rows)
    
    effective_max_rows = max_rows_per_table

    # Handle max_rows_per_table as list or int 
    if effective_max_rows is not None:
        if isinstance(effective_max_rows, list):
            needs_splitting = len(df) > min(effective_max_rows) or len(effective_max_rows) > 1
            max_rows_for_check = effective_max_rows
        else:
            needs_splitting = len(df) > effective_max_rows
            max_rows_for_check = effective_max_rows
    else:
        needs_splitting = False
        max_rows_for_check = None

    if needs_splitting:
        img_paths = create_split_table_images(
            df=df, output_dir=tables_dir, base_table_number=table_counter + 1,
            title=title, dpi=tables_config['display']['dpi'], hide_columns=hide_columns,
            filter_by=filter_by, sort_by=sort_by,
            max_rows_per_table=max_rows_for_check
        )
        table_counter += len(img_paths)
    else:
        img_path = create_table_image(
            df=df, output_dir=tables_dir, table_number=table_counter + 1,
            title=title, dpi=tables_config['display']['dpi'], hide_columns=hide_columns,
            filter_by=filter_by, sort_by=sort_by
        )
        img_paths = [img_path]
        table_counter += 1

    # Generate markdown for each table
    markdown_list = []
    table_config = _load_table_config()
    display_config = table_config['display']
    
    # Use HTML-specific width for better sizing in HTML output when html_responsive is enabled
    if display_config['html_responsive']:
        fig_width = display_config['max_width_inches_html']
    else:
        fig_width = display_config['max_width_inches']

    for i, img_path in enumerate(img_paths):
        # Use dynamic configuration for consistent path calculation
        output_dirs = get_absolute_output_directories()
        rel_path = get_quarto_relative_path(img_path, output_dirs['report'])
        
        # Each split table gets its own sequential number
        table_number = table_counter - len(img_paths) + i + 1
        table_id = f"tbl-{table_number}"
        
        # Apply proper title formatting for split tables
        if len(img_paths) > 1:
            # Multiple tables - use multi_table_title_format
            if title:
                multi_format = table_config['pagination']['multi_table_title_format']
                table_caption = multi_format.format(
                    title=title, 
                    part=i + 1, 
                    total=len(img_paths)
                )
            else:
                no_title_format = table_config['pagination']['multi_table_no_title_format']
                table_caption = no_title_format.format(
                    part=i + 1, 
                    total=len(img_paths)
                )
        else:
            # Single table - use single_table_title_format
            if title:
                single_format = table_config['pagination']['single_table_title_format']
                table_caption = single_format.format(title=title)
            else:
                table_caption = f"Table {table_number}"
                
        # Integrate source into caption if provided
        if source:
            if 'source' not in table_config:
                raise ValueError("Missing 'source' configuration in tables.json")
            source_config = table_config['source']
            
            if 'enable_source' not in source_config:
                raise ValueError("Missing 'enable_source' in source configuration")
            if source_config['enable_source']:
                if 'source_format' not in source_config:
                    raise ValueError("Missing 'source_format' in source configuration")
                source_text = source_config['source_format'].format(source=source)
                if table_caption:
                    table_caption = f"{table_caption} {source_text}"
                else:
                    table_caption = source_text

        # Create table markdown
        table_markdown = f"\n\n![{table_caption}]({rel_path}){{#{table_id} fig-width={fig_width}}}\n\n"
        markdown_list.append((table_markdown, img_path))

    return markdown_list, table_counter

def add_colored_table_to_content(df: pd.DataFrame, output_dir: Optional[str], table_counter: int,
                                title: str = None, highlight_columns: Optional[List[str]] = None,
                                hide_columns: Union[str, List[str]] = None,
                                filter_by: Union[Tuple, List[Tuple]] = None,
                                sort_by: Union[str, Tuple, List] = None,
                                max_rows_per_table: Optional[Union[int, List[int]]] = None,
                                palette_name: Optional[str] = None,
                                n_rows: Optional[Union[int, List[int]]] = None,
                                source: Optional[str] = None) -> Tuple[List[str], int]:
    """Add colored table to content and return markdown and updated counter.
    
    Args:
        df: DataFrame to create table from
        output_dir: Output directory for table images
        table_counter: Current table counter
        title: Optional table title
        highlight_columns: Columns to highlight
        hide_columns: Columns to hide
        filter_by: Filter criteria
        sort_by: Sort criteria
        max_rows_per_table: Maximum rows per table (for splitting)
        palette_name: Color palette name
        n_rows: Take only first N rows (subset)
        source: Optional source information for the table
        
    Returns:
        Tuple of (list of markdown strings, updated table counter)
    """
    from ePy_docs.components.images import ImageProcessor
    from ePy_docs.core.setup import get_absolute_output_directories
    
    # Load table configuration
    tables_config = _load_table_config()
    
    # Get current layout configuration to determine palette
    from ePy_docs.core.setup import get_current_project_config, _load_cached_files, get_filepath
    from ePy_docs.components.pages import get_current_layout
    
    # Use project sync_files setting instead of hardcoding
    current_config = get_current_project_config()
    sync_files = current_config.settings.sync_files if current_config else False
    
    # Load report config using centralized system
    try:
        config_path = get_filepath('files.configuration.units.format_json', sync_files)
        report_config = _load_cached_files(config_path, sync_files=sync_files)
    except Exception:
        report_config = {}
    current_layout_name = get_current_layout()
    
    # The layouts are in the tables config under 'layout_styles'
    table_layouts = tables_config['layout_styles']
    current_layout_config = table_layouts[current_layout_name]
    
    # Get tables directory from setup.json - use full path for dynamic config
    output_dirs = get_absolute_output_directories()
    tables_dir = output_dirs['tables']  # Use full dynamic path
    os.makedirs(tables_dir, exist_ok=True)

    # Use provided palette_name or fall back to layout configuration
    table_palette = palette_name if palette_name is not None else current_layout_config.get('palette_name', 'engineering')

    # Handle n_rows as subset (take first N rows) vs max_rows_per_table (split into multiple tables)
    if n_rows is not None:
        df = df.head(n_rows)
    
    effective_max_rows = max_rows_per_table

    # Handle max_rows_per_table as list or int
    if effective_max_rows is not None:
        if isinstance(effective_max_rows, list):
            needs_splitting = len(df) > min(effective_max_rows) or len(effective_max_rows) > 1
            max_rows_for_check = effective_max_rows
        else:
            needs_splitting = len(df) > effective_max_rows
            max_rows_for_check = effective_max_rows
    else:
        needs_splitting = False
        max_rows_for_check = None

    if needs_splitting:
        img_paths = create_split_table_images(
            df=df, output_dir=tables_dir, base_table_number=table_counter + 1,
            title=title, highlight_columns=highlight_columns,
            palette_name=table_palette, dpi=tables_config['display']['dpi'],
            hide_columns=hide_columns, filter_by=filter_by, sort_by=sort_by,
            max_rows_per_table=max_rows_for_check
        )
        table_counter += len(img_paths)
    else:
        img_path = create_table_image(
            df=df, output_dir=tables_dir, table_number=table_counter + 1,
            title=title, highlight_columns=highlight_columns,
            palette_name=table_palette, dpi=tables_config['display']['dpi'],
            hide_columns=hide_columns, filter_by=filter_by, sort_by=sort_by
        )
        img_paths = [img_path]
        table_counter += 1

    # Generate markdown for each table
    markdown_list = []
    table_config = _load_table_config()
    display_config = table_config['display']
    
    # Use HTML-specific width for better sizing in HTML output when html_responsive is enabled
    if display_config['html_responsive']:
        fig_width = display_config['max_width_inches_html']
    else:
        fig_width = display_config['max_width_inches']

    for i, img_path in enumerate(img_paths):
        # Use dynamic configuration for consistent path calculation
        output_dirs = get_absolute_output_directories()
        rel_path = get_quarto_relative_path(img_path, output_dirs['report'])
        
        # Each split table gets its own sequential number
        table_number = table_counter - len(img_paths) + i + 1
        table_id = f"tbl-{table_number}"
        
        # Apply proper title formatting for split tables
        if len(img_paths) > 1:
            # Multiple tables - use multi_table_title_format
            if title:
                multi_format = table_config['pagination']['multi_table_title_format']
                table_caption = multi_format.format(
                    title=title, 
                    part=i + 1, 
                    total=len(img_paths)
                )
            else:
                no_title_format = table_config['pagination']['multi_table_no_title_format']
                table_caption = no_title_format.format(
                    part=i + 1, 
                    total=len(img_paths)
                )
        else:
            # Single table - use single_table_title_format
            if title:
                single_format = table_config['pagination']['single_table_title_format']
                table_caption = single_format.format(title=title)
            else:
                table_caption = f"Table {table_number}"
                
        # Integrate source into caption if provided
        if source:
            if 'source' not in table_config:
                raise ValueError("Missing 'source' configuration in tables.json")
            source_config = table_config['source']
            
            if 'enable_source' not in source_config:
                raise ValueError("Missing 'enable_source' in source configuration")
            if source_config['enable_source']:
                if 'source_format' not in source_config:
                    raise ValueError("Missing 'source_format' in source configuration")
                source_text = source_config['source_format'].format(source=source)
                if table_caption:
                    table_caption = f"{table_caption} {source_text}"
                else:
                    table_caption = source_text

        # Create table markdown
        table_markdown = f"\n\n![{table_caption}]({rel_path}){{#{table_id} fig-width={fig_width}}}\n\n"
        markdown_list.append((table_markdown, img_path))

    return markdown_list, table_counter

def _apply_custom_table_styles(table, layout_name: str, config: dict) -> None:
    """Apply layout-specific custom table styles."""
    from ePy_docs.core.setup import get_current_project_config
    
    current_config = get_current_project_config()
    sync_files = current_config.settings.sync_files if current_config else False
    
    colors_config = _load_cached_files(get_filepath('files.configuration.styling.colors_json', sync_files), sync_files)
    
    if ('layout_styles' not in colors_config or 
        layout_name not in colors_config['layout_styles'] or
        'tables' not in colors_config['layout_styles'][layout_name] or
        'styles' not in colors_config['layout_styles'][layout_name]['tables']):
        return
    
    layout_styles = colors_config['layout_styles'][layout_name]['tables']['styles']
    
    for style_name, style_config in layout_styles.items():
        style_type = style_config.get('style')
        
        if style_type == 'vibrant_gradient':
            _apply_vibrant_gradient_style(table, style_config)
        elif style_type == 'creative_borders':
            _apply_creative_borders_style(table, style_config)
        elif style_type == 'colorful_alternating':
            _apply_colorful_alternating_style(table, style_config)

def _apply_vibrant_gradient_style(table, style_config: dict) -> None:
    """Apply vibrant gradient style - creative layout."""
    gradient_colors = style_config.get('gradient_colors', [[156, 39, 176], [233, 30, 99]])
    background_color = style_config.get('background_color', [35, 35, 45])
    
    def rgb_to_mpl(rgb):
        return [c/255.0 for c in rgb]
    
    bg_color = rgb_to_mpl(background_color)
    grad_start = rgb_to_mpl(gradient_colors[0])
    grad_end = rgb_to_mpl(gradient_colors[1])
    
    num_cols = len([cell for pos, cell in table._cells.items() if pos[0] == 0])
    for col in range(num_cols):
        if (0, col) in table._cells:
            gradient_factor = col / max(1, num_cols - 1)
            interpolated_color = [
                grad_start[i] + gradient_factor * (grad_end[i] - grad_start[i])
                for i in range(3)
            ]
            table._cells[(0, col)].set_facecolor(interpolated_color + [1.0])
    
    for pos, cell in table._cells.items():
        if pos[0] > 0:
            cell.set_facecolor(bg_color + [1.0])
            cell.get_text().set_color('white')

def _apply_creative_borders_style(table, style_config: dict) -> None:
    """Apply creative borders style."""
    border_color = style_config.get('border_color', [255, 193, 7])
    background_color = style_config.get('background_color', [35, 35, 45])
    
    border_mpl = [c/255.0 for c in border_color]
    bg_mpl = [c/255.0 for c in background_color]
    
    for pos, cell in table._cells.items():
        cell.set_facecolor(bg_mpl + [1.0])
        cell.get_text().set_color('white')
        cell.set_edgecolor(border_mpl)
        cell.set_linewidth(2.5)
        
        if pos[0] == 0:
            cell.set_linewidth(3.0)

def _apply_colorful_alternating_style(table, style_config: dict) -> None:
    """Apply colorful alternating rows style."""
    alternating_colors = style_config.get('alternating_colors', [[35, 35, 45], [40, 40, 50]])
    header_color = style_config.get('header_color', [233, 30, 99])
    
    alt_color1 = [c/255.0 for c in alternating_colors[0]]
    alt_color2 = [c/255.0 for c in alternating_colors[1]]
    header_mpl = [c/255.0 for c in header_color]
    
    for pos, cell in table._cells.items():
        row = pos[0]
        
        if row == 0:
            cell.set_facecolor(header_mpl + [1.0])
            cell.get_text().set_color('white')
        else:
            if row % 2 == 1:
                cell.set_facecolor(alt_color1 + [1.0])
            else:
                cell.set_facecolor(alt_color2 + [1.0])
            cell.get_text().set_color('white')
