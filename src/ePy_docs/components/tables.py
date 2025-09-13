"""Tables configuration and image generation.

Table processing with centralized configuration through _load_cached_files.
All styling organized by layout_styles with comprehensive font system.
Pure implementation with no backward compatibility or fallbacks.
All configuration centralized in tables.json.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Rectangle
from typing import Dict, Any, Union, List, Optional
from ePy_docs.files import _load_cached_files
from ePy_docs.files.data import _safe_get_nested
from ePy_docs.components.setup import _resolve_config_path

def get_tables_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load centralized table configuration.
    
    Args:
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Complete tables configuration dictionary.
    """
    config_path = _resolve_config_path('components/tables', sync_files)
    return _load_cached_files(config_path, sync_files)

def detect_table_category(df: pd.DataFrame, sync_files: bool = False) -> tuple[str, Optional[List[str]]]:
    """Detect table category based on column names and content using category_rules.
    
    Args:
        df: DataFrame to analyze.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Tuple of (category_name, highlight_columns).
    """
    config = get_tables_config(sync_files)
    category_rules = config.get('category_rules', {})
    
    # Analyze column names for category detection
    column_names_lower = [col.lower() for col in df.columns]
    column_text = ' '.join(column_names_lower)
    
    category_scores = {}
    potential_highlight_columns = {}
    
    for category, rules in category_rules.items():
        if category == 'general':
            continue  # Skip general category in scoring
            
        score = 0
        highlight_cols = []
        
        # Score based on name keywords
        for keyword in rules.get('name_keywords', []):
            keyword_lower = keyword.lower()
            if keyword_lower in column_text:
                score += 2  # Higher weight for exact matches
                # Find columns containing this keyword
                for col in df.columns:
                    if keyword_lower in col.lower():
                        highlight_cols.append(col)
            elif any(keyword_lower in col_name for col_name in column_names_lower):
                score += 1  # Lower weight for partial matches
        
        # Score based on coordinate patterns (for nodes category)
        if 'coordinate_patterns' in rules:
            for pattern in rules['coordinate_patterns']:
                if pattern.lower() in column_text:
                    score += 3  # High weight for coordinate patterns
                    for col in df.columns:
                        if pattern.lower() in col.lower():
                            highlight_cols.append(col)
        
        if score > 0:
            category_scores[category] = score
            potential_highlight_columns[category] = list(set(highlight_cols))  # Remove duplicates
    
    # Return highest scoring category or general if no match
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        return best_category, potential_highlight_columns.get(best_category, [])
    else:
        return 'general', []

def create_table_image(data: Union[pd.DataFrame, List[List]], 
                      title: str = None, output_dir: str = None, 
                      filename: str = None, layout_style: str = "corporate", 
                      sync_files: bool = False, 
                      highlight_columns: Optional[List[str]] = None,
                      palette_name: Optional[str] = None,
                      auto_detect_categories: bool = False,
                      document_type: str = "report") -> str:
    """Create table as image using centralized configuration.
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Optional table title.
        output_dir: Output directory path.
        filename: Output filename.
        layout_style: One of 8 universal layout styles.
        sync_files: Control cache synchronization behavior.
        highlight_columns: List of column names to highlight with colors.
        palette_name: Color palette name for highlights.
        auto_detect_categories: Enable automatic category detection for highlighting.
        
    Returns:
        Path to generated image file.
        
    Raises:
        ValueError: If layout_style not found in configuration.
    """
    config = get_tables_config(sync_files)
    
    if layout_style not in config['layout_styles']:
        raise ValueError(f"Layout style '{layout_style}' not found")
    
    style_config = config['layout_styles'][layout_style]
    
    # Get all necessary configurations
    size_config = config['font_sizes']
    format_config = config['formatting']
    display_config = config['display']  # Add display configuration for table dimensions
    
    # Get output directory using document-type-aware function
    from ePy_docs.components.setup import get_absolute_output_directories
    output_dirs = get_absolute_output_directories(document_type=document_type, sync_files=sync_files)
    output_directory = output_dirs['tables']
    
    df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
    
    # Automatic category detection and highlight for add_colored_table
    if auto_detect_categories and (highlight_columns is None or len(highlight_columns) == 0):
        detected_category, auto_highlight_columns = detect_table_category(df, sync_files)
        if auto_highlight_columns:
            highlight_columns = auto_highlight_columns
            # Get category-specific palette if not specified
            if palette_name is None:
                category_rules = config.get('category_rules', {})
                if detected_category in category_rules:
                    # Use different palettes based on category
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
    from ePy_docs.components.format import format_superscripts
    
    for col in df.columns:
        df[col] = df[col].apply(lambda x: format_superscripts(str(x), 'matplotlib', sync_files))
    
    # Code content detection and formatting from Code Kingdom
    from ePy_docs.components.code import get_code_config, get_available_languages
    code_config = get_code_config()
    available_languages = get_available_languages(sync_files)
    
    # Apply code formatting if any cells contain code-like content
    def detect_and_format_code_content(cell_value):
        """Detect and format code content in table cells."""
        cell_str = str(cell_value)
        
        # Check for code patterns using Code Kingdom validation
        code_patterns = [
            '(', ')', '{', '}', '[', ']',  # Code brackets
            'def ', 'function', 'class ',  # Programming keywords
            '=', '==', '!=', '>=', '<=',   # Programming operators
            '\n',  # Multi-line code
        ]
        
        # Simple heuristic: if cell contains multiple code patterns, format as code
        pattern_count = sum(1 for pattern in code_patterns if pattern in cell_str)
        
        if pattern_count >= 3 or any(lang in cell_str.lower() for lang in available_languages[:5]):
            # Use code formatting from Code Kingdom
            formatting_config = code_config.get('formatting', {})
            # Apply monospace styling hint for matplotlib (this could be enhanced)
            return cell_str  # For now, return as-is but flagged as code content
        
        return cell_str
    
    # Apply code detection to all cells
    for col in df.columns:
        df[col] = df[col].apply(detect_and_format_code_content)
    
    # Official access to Text Kingdom for alignment configuration by layout_styles
    from ePy_docs.components.text import get_text_config
    text_config = get_text_config(sync_files)
    
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
                                output_directory, sync_files)

def _generate_table_image(df: pd.DataFrame, title: str, output_dir: str, 
                         filename: str, style_config: Dict,
                         size_config: Dict, format_config: Dict, display_config: Dict,
                         highlight_columns: Optional[List[str]] = None,
                         palette_name: Optional[str] = None, layout_style: str = 'corporate',
                         alignment_config: Optional[Dict[str, str]] = None,
                         output_directory: str = None, sync_files: bool = False) -> str:
    """Generate table image using centralized configuration.
    
    Args:
        df: DataFrame containing table data.
        title: Table title.
        output_dir: Output directory.
        filename: Output filename.
        style_config: Style configuration for layout.
        size_config: Size configuration.
        format_config: Formatting configuration.
        output_directory: Default output directory from Reino SETUP.
        
    Returns:
        Path to generated image file.
    """
    if not output_dir:
        output_dir = output_directory
    os.makedirs(output_dir, exist_ok=True)
    
    if not filename:
        counter = len([f for f in os.listdir(output_dir) if f.startswith('table_')]) + 1
        filename = format_config['filename_format'].format(counter=counter, ext='png')
    
    filepath = os.path.join(output_dir, filename)
    
    # CONFIGURE PRIMARY FONT WITH AUTOMATIC FALLBACK using Text Kingdom
    from ePy_docs.components.text import get_text_config
    text_config = get_text_config(sync_files)
    
    # Get layout configuration
    layout_config = text_config['layout_styles'][layout_style]
    
    # Get font family for tables (prioritize tables, fallback to typography)
    if 'tables' in layout_config and 'content_font' in layout_config['tables']:
        font_family = layout_config['tables']['content_font']['family']
    elif 'typography' in layout_config and 'normal' in layout_config['typography']:
        font_family = layout_config['typography']['normal']['family']
    else:
        font_family = 'sans_technical'  # Emergency fallback
    
    # Build font list from font family configuration
    font_config = text_config['font_families'][font_family]
    font_list = [font_config['primary']]
    if font_config.get('fallback'):
        fallback_fonts = [f.strip() for f in font_config['fallback'].split(',')]
        font_list.extend(fallback_fonts)
    
    # Configure matplotlib to use font list BEFORE any font operations
    plt.rcParams['font.family'] = font_list
    
    # Clear matplotlib font cache after configuration if needed
    import matplotlib.font_manager as fm
    if font_config['primary'] not in [f.name for f in fm.fontManager.ttflist]:
        fm._load_fontmanager(try_read_cache=False)  # Only reload if font not found
    
    # Load Code Kingdom configuration for programming content detection
    from ePy_docs.components.code import get_code_config
    try:
        code_config = get_code_config()
    except:
        code_config = {}  # Fallback if code config unavailable
    
    # HELPER FUNCTION: Detect missing values that need italic styling
    def is_missing_value(text_value):
        """Detect if a value should be displayed in italic for being missing."""
        if pd.isna(text_value):
            return True
        
        text_str = str(text_value).strip().lower()
        missing_indicators = ['', 'nan', 'none', 'null', '-', '--', '---', 'n/a', 'na']
        return text_str in missing_indicators
    
    # HELPER FUNCTION: Configure font based on content type
    def configure_cell_font(cell, text_value, is_header=False):
        """Configure specific font for each cell based on its content."""
        
        # Check if content appears to be code using Code Kingdom patterns
        is_code_content = False
        if not is_header and text_value is not None:
            cell_str = str(text_value)
            code_indicators = ['def ', 'function', 'class ', '()', '{}', '[]', 'import ', 'from ', '=', '==']
            code_count = sum(1 for indicator in code_indicators if indicator in cell_str)
            is_code_content = code_count >= 2
        
        if is_header:
            # Headers always use handwritten font with automatic fallback
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
        elif is_missing_value(text_value):
            # Missing values (including "---") use handwritten font to maintain consistent style
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('italic')
        elif is_code_content:
            # Code content should use monospace font from Code Kingdom
            try:
                # Get monospace font from code configuration
                if layout_style in code_config.get('layout_styles', {}):
                    code_layout = code_config['layout_styles'][layout_style]
                    if 'mono_font' in code_layout:
                        mono_font = code_layout['mono_font']['family']
                        # Use monospace font for code content
                        cell.get_text().set_fontfamily([mono_font] + font_list)
                    else:
                        # Fallback to system monospace
                        cell.get_text().set_fontfamily(['monospace'] + font_list)
                else:
                    # Fallback to system monospace
                    cell.get_text().set_fontfamily(['monospace'] + font_list)
                cell.get_text().set_style('normal')
            except:
                # If code config fails, use regular font
                cell.get_text().set_fontfamily(font_list)
                cell.get_text().set_style('normal')
        else:
            # Normal values use handwritten font with automatic fallback
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
    
    # AUTOMATIC WRAPPING PRE-TABLE
    # OBJECTIVE: Resolve horizontal overflow by wrapping text before matplotlib
    from ePy_docs.components.format import prepare_dataframe_with_wrapping
    df = prepare_dataframe_with_wrapping(df, layout_style, sync_files)
    
    # Alignment configuration by layout_styles via Text Kingdom
    # No fallbacks - valid configuration must exist
    if alignment_config is None:
        raise RuntimeError(f"No alignment configuration provided for layout_style '{layout_style}'")
    
    font_size_content = size_config['content'][style_config['font_sizes']['content']]
    font_size_header = size_config['header'][style_config['font_sizes']['header']]
    
    # Get cell padding from style configuration and convert to matplotlib PAD format
    base_cell_padding = style_config['styling']['cell_padding'] / 1000.0  # Convert pixels to fraction
    
    # Recalculate dimensions after wrapping
    num_rows, num_cols = df.shape
    
    # Width from layout-specific configuration
    table_width = style_config['styling']['width_inches']
    
    # Height settings from display configuration
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
    
    # LATERAL PADDING CORRECTION AND AUTOMATIC FONT ADJUSTMENT
    def apply_header_multiline(header_text, max_length=12):
        """Apply intelligent line breaks to headers to avoid font reduction.
        
        Priority order for line breaks:
        1. Forward slash (/) - natural separator
        2. Parentheses - units usually in parentheses
        3. Space - word boundaries
        4. Hyphen/dash - compound words
        5. Camel case - for compound words without separators
        
        Args:
            header_text (str): Original header text
            max_length (int): Maximum characters per line before considering break
            
        Returns:
            str: Header with strategic line breaks
        """
        # For very short headers, no need to break
        if len(header_text) <= 8:
            return header_text
            
        # Priority 1: Forward slash (/) - excellent natural break point
        # Apply more aggressively for natural separators
        if '/' in header_text:
            parts = header_text.split('/')
            if len(parts) == 2 and max(len(parts[0]), len(parts[1])) <= max_length:
                return f"{parts[0]}/\n{parts[1]}"
            elif len(parts) > 2:
                # Multiple slashes - group intelligently
                first_part = parts[0]
                remaining = '/'.join(parts[1:])
                if len(first_part) <= max_length and len(remaining) <= max_length:
                    return f"{first_part}/\n{remaining}"
        
        # Priority 2: Parentheses - units or additional info (higher priority than spaces)
        # Apply more aggressively for units
        if '(' in header_text and ')' in header_text:
            paren_start = header_text.find('(')
            if paren_start > 0:  # Removed length constraint for more aggressive splitting
                main_part = header_text[:paren_start].strip()
                unit_part = header_text[paren_start:].strip()
                if len(main_part) <= max_length and len(unit_part) <= max_length:
                    return f"{main_part}\n{unit_part}"
        
        # Only apply length check for other patterns
        if len(header_text) <= max_length:
            return header_text
        
        # Priority 3: Space - natural word boundaries (only if no parentheses handled above)
        if ' ' in header_text:
            words = header_text.split(' ')
            if len(words) == 2 and max(len(words[0]), len(words[1])) <= max_length:
                return f"{words[0]}\n{words[1]}"
            elif len(words) > 2:
                # Multiple words - find best split point
                for i in range(1, len(words)):
                    first_part = ' '.join(words[:i])
                    second_part = ' '.join(words[i:])
                    if len(first_part) <= max_length and len(second_part) <= max_length:
                        return f"{first_part}\n{second_part}"
        
        # Priority 4: Hyphen/dash - compound words
        for separator in ['-', '–', '—']:
            if separator in header_text:
                parts = header_text.split(separator, 1)  # Split only at first occurrence
                if len(parts) == 2 and max(len(parts[0]), len(parts[1])) <= max_length:
                    return f"{parts[0]}{separator}\n{parts[1]}"
        
        # Priority 5: Camel case detection (CapitalLetters)
        import re
        camel_pattern = r'([a-z])([A-Z])'
        if re.search(camel_pattern, header_text):
            # Find best camel case split point
            matches = list(re.finditer(camel_pattern, header_text))
            for match in matches:
                split_pos = match.end() - 1  # Position of the capital letter
                first_part = header_text[:split_pos]
                second_part = header_text[split_pos:]
                if len(first_part) <= max_length and len(second_part) <= max_length:
                    return f"{first_part}\n{second_part}"
        
        # Fallback: No good break point found, return original
        return header_text

    def auto_adjust_font_size(cell, original_font_size, num_columns=None, table_width=None, is_header=False):
        """Intelligently adjust font size based on content, table density, and layout constraints.
        
        The original_font_size from text.json is treated as the MAXIMUM size.
        Font is reduced dynamically based on:
        - Content length and complexity
        - Number of columns (table density)
        - Table width constraints
        - Special characters and formatting
        
        Args:
            is_header (bool): If True, applies more conservative reduction for header cells
        """
        cell_text = cell.get_text().get_text()
        current_font_size = original_font_size
        
        # Calculate effective content length
        if '\n' in cell_text:
            # For multiline text, use the longest line
            lines = cell_text.split('\n')
            max_line_length = max(len(line) for line in lines)
            line_count = len(lines)
        else:
            max_line_length = len(cell_text)
            line_count = 1
        
        # FACTOR 1: Content length reduction (menos agresiva para texto más grande)
        length_reduction = 1.0
        if is_header:
            # Headers get more conservative reduction (más texto visible)
            if max_line_length > 25:  # Very long content
                length_reduction = min(0.85, max(0.75, 25 / max_line_length))
            elif max_line_length > 15:  # Long content
                length_reduction = min(0.90, max(0.85, 15 / max_line_length))
            elif max_line_length > 10:  # Medium content
                length_reduction = 0.95
            elif max_line_length > 5:  # Short content
                length_reduction = 1.0
        else:
            # Content cells (lógica original mejorada)
            if max_line_length > 25:  # Very long content
                length_reduction = min(0.78, max(0.65, 25 / max_line_length))
            elif max_line_length > 15:  # Long content
                length_reduction = min(0.85, max(0.78, 15 / max_line_length))
            elif max_line_length > 10:  # Medium content
                length_reduction = 0.90
            elif max_line_length > 5:  # Short content
                length_reduction = 0.95
        
        # FACTOR 2: Table density reduction (menos agresiva para texto más grande)
        density_reduction = 1.0
        if num_columns:
            if num_columns > 12:  # Very dense table
                density_reduction = 0.78
            elif num_columns > 8:  # Dense table
                density_reduction = 0.85
            elif num_columns > 5:  # Medium density
                density_reduction = 0.90
            elif num_columns > 3:  # Light density
                density_reduction = 0.95
        
        # FACTOR 3: Multiline content reduction (menos agresiva para texto más grande)
        multiline_reduction = 1.0
        if line_count > 1:
            multiline_reduction = max(0.82, 1.0 - (line_count - 1) * 0.12)
        
        # FACTOR 4: Special characters that need more space (menos agresiva para texto más grande)
        special_chars_reduction = 1.0
        special_chars = ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '·', '×', '÷', '±', '≤', '≥', 'SRSS']
        if any(char in cell_text for char in special_chars):
            special_chars_reduction = 0.93  # Aumentado de 0.90 a 0.93
        
        # FACTOR 5: Complex formatting (menos agresiva para texto más grande)
        formatting_reduction = 1.0
        complex_chars = ['(', ')', '[', ']', '{', '}', '@', '#', '$', '%']
        complex_count = sum(1 for char in complex_chars if char in cell_text)
        if complex_count > 2:
            formatting_reduction = max(0.85, 1.0 - complex_count * 0.03)  # Aumentado de 0.80-0.04 a 0.85-0.03
        elif complex_count > 0:
            formatting_reduction = 0.93  # Aumentado de 0.90 a 0.93
        
        # Apply all reduction factors
        final_reduction = (length_reduction * density_reduction * multiline_reduction * 
                          special_chars_reduction * formatting_reduction)
        
        # Ensure minimum readable size (aumentado de 50% a 60% para texto más grande)
        final_reduction = max(0.60, final_reduction)  # Aumentado de 0.5 a 0.60
        
        current_font_size = original_font_size * final_reduction
        
        # Apply adjusted size
        cell.set_fontsize(current_font_size)
        return current_font_size

    # APPLY FONT ADJUSTMENT TO HEADERS AND CONTENT
    # Headers (row 0) - automatic adjustment if doesn't fit + font configuration
    for j in range(num_cols):
        cell = table[(0, j)]
        header_text = df.columns[j]
        
        # STEP 1: Apply intelligent multiline breaks BEFORE font reduction
        multiline_header = apply_header_multiline(str(header_text), max_length=12)
        
        # STEP 2: Apply superscript formatting to the multiline header text
        from ePy_docs.components.format import format_superscripts
        formatted_header = format_superscripts(multiline_header, 'matplotlib', sync_files)
        cell.get_text().set_text(formatted_header)
        
        # STEP 3: Configure specific font for header
        configure_cell_font(cell, header_text, is_header=True)
        
        # STEP 4: Apply base font size
        cell.set_fontsize(font_size_header)
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
            
        # STEP 5: Apply intelligent font size adjustment (after multiline optimization)
        auto_adjust_font_size(cell, font_size_header, num_columns=num_cols, table_width=table_width, is_header=True)

    # Content (rows 1+) - automatic adjustment if doesn't fit + font configuration
    for i in range(1, num_rows + 1):
        for j in range(num_cols):
            cell = table[(i, j)]
            
            # Get original value from DataFrame for missing value detection
            df_row_idx = i - 1  # Convert table index to DataFrame
            if df_row_idx < len(df) and j < len(df.columns):
                original_value = df.iloc[df_row_idx, j]
            else:
                original_value = None
            
            # Configure specific font based on content
            configure_cell_font(cell, original_value, is_header=False)
            
            cell.set_fontsize(font_size_content)
            # Automatically adjust font if content is too long
            auto_adjust_font_size(cell, font_size_content, num_columns=num_cols, table_width=table_width)

    # AUTOMATIC WIDTH ADJUSTMENT PER COLUMN
    def calculate_column_width_factor(col_index, column_name):
        """Calculate specific width factor for each column."""
        base_width_factor = 1.0
        max_content_length = len(str(column_name))  # Start with header
        
        # Analyze content of entire column to find the longest
        for row_idx in range(len(df)):
            cell_value = df.iloc[row_idx, col_index]
            cell_str = str(cell_value)
            
            # Consider multiline text
            if '\n' in cell_str:
                # For multiline text, use the longest line
                lines = cell_str.split('\n')
                max_line_length = max(len(line) for line in lines)
                max_content_length = max(max_content_length, max_line_length)
            else:
                max_content_length = max(max_content_length, len(cell_str))
        
        # Calculate width factor based on content - OPTIMIZED FOR EFFICIENCY
        if max_content_length <= 3:
            width_factor = 0.7  # Very short columns - more compact
        elif max_content_length <= 8:
            width_factor = 0.9  # Reduced width
        elif max_content_length <= 15:
            width_factor = 1.0  # Normal width
        elif max_content_length <= 25:
            width_factor = 1.2  # Moderate expanded width
        elif max_content_length <= 35:
            width_factor = 1.4  # Moderate long width
        else:
            width_factor = 1.6  # Controlled very long width
        
        # Additional factor for equations and special symbols - REDUCED
        for row_idx in range(len(df)):
            cell_value = df.iloc[row_idx, col_index]
            cell_str = str(cell_value)
            if any(char in cell_str for char in ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']) or \
               any(pattern in cell_str for pattern in ['·', '×', '÷', '±', '≤', '≥']):
                width_factor *= 1.05  # Reduced additional space for symbols (5% instead of 10%)
                break
        
        return width_factor

    # APPLY AUTOMATIC WIDTH TO EACH COLUMN
    for j in range(num_cols):
        column_name = df.columns[j]
        width_factor = calculate_column_width_factor(j, column_name)
        
        # Apply width to all cells in this column
        for i in range(num_rows + 1):  # +1 to include header
            cell = table[(i, j)]
            current_width = cell.get_width()
            cell.set_width(current_width * width_factor)

    # CORRECT MULTILINE TEXT FORMATTING AND ADJUSTMENT PER COMPLETE ROW
    def calculate_row_height_for_multiline(row_index, is_header=False):
        """Calculate necessary height based on actual letter height + proportional spacing."""
        max_lines_in_row = 1
        base_font_size = float(font_size_header if is_header else font_size_content)
        
        if is_header:
            # Analyze headers to find the one requiring most lines
            for col in df.columns:
                col_str = str(col)
                line_count = col_str.count('\n') + 1
                max_lines_in_row = max(max_lines_in_row, line_count)
                
                # Specific improvement for headers: more conservative estimation
                if len(col_str) > 20:  # Lower threshold for headers
                    # Headers need more space due to larger characters
                    estimated_lines = len(col_str) // 20 + 1  # Fewer characters per line
                    max_lines_in_row = max(max_lines_in_row, estimated_lines)
                
                # Consider special cases in headers (very long words)
                if any(len(word) > 15 for word in col_str.split('\n')):
                    max_lines_in_row = max(max_lines_in_row, line_count + 1)
        else:
            # Analyze all cells in this row
            if row_index < len(df):
                for col in df.columns:
                    cell_value = df.iloc[row_index, df.columns.get_loc(col)]
                    cell_str = str(cell_value)
                    
                    # Count explicit lines
                    line_count = cell_str.count('\n') + 1
                    max_lines_in_row = max(max_lines_in_row, line_count)
                    
                    # Estimate lines by length (automatic wrap) - more conservative
                    if len(cell_str) > 25:  # Lower threshold
                        estimated_lines = len(cell_str) // 25 + 1  # More conservative characters per line
                        max_lines_in_row = max(max_lines_in_row, estimated_lines)
        
        # CALCULATION BASED ON ACTUAL LETTER HEIGHT + PROPORTIONAL SPACING
        # Base height of a text line (in typographic points)
        line_height_points = base_font_size * 1.2  # 1.2 = standard line spacing
        
        # CORRECTION BY FONT TYPE: serif vs sans vs mono vs handwritten
        # Get font type information from layout configuration
        font_type_factor = 1.0
        uses_handwritten = (layout_style == 'minimal' or font_family == 'handwritten_personal')
        if uses_handwritten:
            # Handwritten fonts need 25% more height for irregularity and style
            font_type_factor = 1.25
        else:
            # Use default factor for other font types
            # Could be enhanced later to detect serif/mono from font family names
            font_type_factor = 1.0
        
        # Additional proportional spacing for number of lines - OPTIMIZED
        # More lines = more spacing to avoid visual crowding, but more compact
        if max_lines_in_row == 1:
            # One line: minimal spacing (15% extra - reduced from 20%)
            spacing_factor = 1.15
        elif max_lines_in_row <= 3:
            # 2-3 lines: moderate spacing (25% extra - reduced from 30%)
            spacing_factor = 1.25
        elif max_lines_in_row <= 5:
            # 4-5 lines: generous spacing (30% extra - reduced from 40%)
            spacing_factor = 1.30
        else:
            # 6+ lines: maximum spacing (35% extra - reduced from 50%)
            spacing_factor = 1.35
        
        # Headers need additional spacing for bold - OPTIMIZED
        if is_header:
            spacing_factor *= 1.10  # 10% extra for bold text (reduced from 15%)
        
        # Final factor: actual height × lines × spacing × font correction
        height_factor = (line_height_points * max_lines_in_row * spacing_factor * font_type_factor) / (base_font_size * 1.2)
        
        # Ensure minimum factor for readability
        height_factor = max(height_factor, 1.0)
        
        return height_factor

    # APPLY UNIFORM HEIGHT PER COMPLETE ROW
    # Header (row 0) - alignment from Text Kingdom
    header_height_factor = calculate_row_height_for_multiline(0, is_header=True)
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
        row_height_factor = calculate_row_height_for_multiline(i - 1, is_header=False)
        
        # Apply the SAME height to ALL cells in this row
        for j in range(num_cols):
            cell = table[(i, j)]
            current_height = cell.get_height()
            cell.set_height(current_height * row_height_factor)
            
            # Content alignment from Text Kingdom by layout_styles
            cell_text = cell.get_text().get_text()
            is_multiline = '\n' in cell_text or len(cell_text) > 30
            
            # Determine if it's numeric content for special alignment
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
    from ePy_docs.components.colors import get_colors_config
    colors_config = get_colors_config()
    
    # Get layout-specific color configuration from Reino Colors
    if layout_style in colors_config['layout_styles']:
        layout_colors = colors_config['layout_styles'][layout_style]
        default_palette_name = layout_colors.get('default_palette', 'grays_warm')
        table_config = layout_colors.get('tables', {})
    else:
        # Fallback to grays_warm if layout not found
        default_palette_name = 'grays_warm'
        table_config = {}
    
    def _rgb_to_matplotlib(rgb_list):
        """Convert RGB list [0-255] to matplotlib format [0-1]."""
        # Handle various input formats
        if isinstance(rgb_list, str):
            # If it's a hex color string, return as is
            if rgb_list.startswith('#'):
                return rgb_list
            # If it's a comma-separated string, parse it
            if ',' in rgb_list:
                rgb_list = [x.strip() for x in rgb_list.split(',')]
        
        # Ensure all values are numeric
        numeric_rgb = []
        for x in rgb_list:
            if isinstance(x, str):
                try:
                    numeric_rgb.append(float(x))
                except ValueError:
                    numeric_rgb.append(0.0)  # Fallback for invalid strings
            else:
                numeric_rgb.append(float(x))
        
        return [x/255.0 for x in numeric_rgb]
    
    # Get palette and tone resolver helper
    def get_color_by_palette_tone(palette_name, tone):
        """Get RGB color from palette and tone according to Reino Colors"""
        if palette_name in colors_config['palettes']:
            palette = colors_config['palettes'][palette_name]
            if tone in palette:
                return _rgb_to_matplotlib(palette[tone])
        # Fallback to grays_warm medium_light
        return _rgb_to_matplotlib(colors_config['palettes']['grays_warm']['medium_light'])
    
    # HEADER styling according to layout_style
    header_config = _safe_get_nested(table_config, 'header.default', {
        'palette': default_palette_name, 
        'tone': 'medium_light'
    })
    header_color = get_color_by_palette_tone(
        header_config['palette'], 
        header_config['tone']
    )
    
    for i in range(num_cols):
        cell = table[(0, i)]
        # Fuente y estilo configurados en sección de ajuste automático
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
        cell.set_facecolor(header_color)
    
    if style_config['styling']['alternating_rows']:
        # Use layout-specific alternating row color
        alt_row_color = get_color_by_palette_tone(default_palette_name, 'light')
        for i in range(1, num_rows + 1):
            if i % 2 == 0:
                for j in range(num_cols):
                    table[(i, j)].set_facecolor(alt_row_color)
    
    # HIGHLIGHT COLUMNS: Apply gradient highlighting per column if specified
    if highlight_columns:
        # Default palette if none specified - FIXED: usar 'blues' que sí existe
        if not palette_name:
            palette_name = 'blues'
        
        # Get highlight colors from configuration
        if palette_name in colors_config['palettes']:
            palette = colors_config['palettes'][palette_name]
            
            # Extract gradient colors (from light to dark)
            gradient_colors = []
            for intensity in ['light', 'medium_light', 'medium', 'medium_dark', 'dark']:
                if intensity in palette:
                    gradient_colors.append(_rgb_to_matplotlib(palette[intensity]))
            
            # Fallback if no gradient found
            if not gradient_colors:
                gradient_colors = [_rgb_to_matplotlib(palette.get('light', '#E3F2FD'))]
            
            # Apply gradient per column independently
            for col_name in highlight_columns:
                if col_name in df.columns:
                    col_index = df.columns.get_loc(col_name)
                    
                    # Get column values (excluding header) for gradient calculation
                    col_values = []
                    for row_index in range(1, num_rows + 1):
                        try:
                            # Get the actual DataFrame value for this cell
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
                    
                    # Calculate gradient mapping for this column
                    if col_values and len(gradient_colors) > 1:
                        # Filter out any remaining NaN values and ensure we have valid numbers
                        valid_values = [v for v in col_values if not pd.isna(v) and isinstance(v, (int, float))]
                        
                        if valid_values:
                            min_val = min(valid_values)
                            max_val = max(valid_values)
                        else:
                            # No valid values, use neutral color for all
                            min_val = max_val = 0.0
                        
                        # Apply gradient colors to each cell in this column
                        for i, row_index in enumerate(range(1, num_rows + 1)):
                            if i < len(col_values):
                                current_value = col_values[i]
                                
                                # Calculate color intensity based on value position in range
                                if max_val != min_val and not pd.isna(current_value):
                                    # Normalize value to 0-1 range
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
                        single_color = gradient_colors[0] if gradient_colors else _rgb_to_matplotlib('#E3F2FD')
                        for row_index in range(1, num_rows + 1):
                            table[(row_index, col_index)].set_facecolor(single_color)
    
    # Use layout-specific border color
    border_color = get_color_by_palette_tone(default_palette_name, 'medium')
    for key, cell in table.get_celld().items():
        cell.set_linewidth(style_config['styling']['grid_width'])
        cell.set_edgecolor(border_color)
    
    # Get padding from display configuration in tables.json
    base_padding = display_config.get('padding_inches', 0.04)
    
    # Calculate exact bounding box for precise padding control
    # This eliminates matplotlib's automatic vertical padding
    fig.canvas.draw()  # Force draw to calculate actual dimensions
    
    # Get table bounding box in figure coordinates
    from matplotlib.transforms import Bbox
    table_bbox = table.get_window_extent(fig.canvas.get_renderer())
    table_bbox_inches = table_bbox.transformed(fig.dpi_scale_trans.inverted())
    
    # Create custom bbox with our exact padding using matplotlib Bbox
    custom_bbox = Bbox.from_bounds(
        table_bbox_inches.x0 - base_padding,  # left
        table_bbox_inches.y0 - base_padding,  # bottom  
        table_bbox_inches.width + (2 * base_padding),  # width
        table_bbox_inches.height + (2 * base_padding)  # height
    )
    
    plt.savefig(filepath, 
               dpi=300, 
               bbox_inches=custom_bbox,  # Use custom bbox instead of 'tight'
               transparent=False,
               facecolor='white',  # Ensure white background for consistency
               edgecolor='none')   # Remove edge color artifacts
    plt.close()
    
    return filepath

def process_table_for_report(data: Union[pd.DataFrame, List[List]], 
                           title: str = None, output_dir: str = None, 
                           figure_counter: int = 1, layout_style: str = "corporate", 
                           sync_files: bool = False, 
                           highlight_columns: Optional[List[str]] = None,
                           palette_name: Optional[str] = None,
                           auto_detect_categories: bool = False,
                           document_type: str = "report") -> tuple[str, str]:
    """Process table for report with automatic counter and ID.
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Table title.
        output_dir: Output directory (if None, uses Reino SETUP configuration).
        figure_counter: Counter for figure numbering.
        layout_style: One of 8 universal layout styles.
        sync_files: Control cache synchronization behavior.
        highlight_columns: List of column names to highlight with colors.
        palette_name: Color palette name for highlights.
        auto_detect_categories: Enable automatic category detection for highlighting.
        
    Returns:
        Tuple of (image_path, figure_id).
    """
    config = get_tables_config(sync_files)
    format_config = config['formatting']
    display_config = config['display']
    
    # Get correct output directory from Reino SETUP if not specified
    if output_dir is None:
        # Get output directory using document-type-aware function
        from ePy_docs.components.setup import get_absolute_output_directories
        output_dirs = get_absolute_output_directories(document_type=document_type, sync_files=sync_files)
        output_dir = output_dirs['tables']
    
    figure_id = format_config['figure_id_format'].format(counter=figure_counter)
    filename = format_config['filename_format'].format(
        counter=figure_counter, 
        ext=display_config['image_format']
    )
    
    image_path = create_table_image(
        data=data,
        title=title,
        output_dir=output_dir,
        filename=filename,
        layout_style=layout_style,
        sync_files=sync_files,
        highlight_columns=highlight_columns,
        palette_name=palette_name,
        auto_detect_categories=auto_detect_categories
    )
    
    return image_path, figure_id

def format_cell_text(text: str, sync_files: bool = False) -> str:
    """Format cell text with centralized superscripts.
    
    Args:
        text: Input text to process.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Text with superscripts formatted.
    """
    from ePy_docs.components.format import format_superscripts
    return format_superscripts(str(text), 'matplotlib', sync_files)

def copy_and_process_image(source_path: str, dest_dir: str, 
                          new_filename: str = None, sync_files: bool = False) -> str:
    """Image processing integration through official commerce office.
    
    Args:
        source_path: Source image file path.
        dest_dir: Destination directory.
        new_filename: Optional new filename.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Path to processed image.
    """
    from ePy_docs.components.images import copy_and_process_image as images_copy
    return images_copy(source_path, dest_dir, new_filename, sync_files)

def get_color_from_path(color_path: str, sync_files: bool = False) -> str:
    """Color system integration through official commerce office.
    
    Args:
        color_path: Color path specification.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Color value.
    """
    from ePy_docs.components.colors import get_color_from_path as colors_get
    return colors_get(color_path, sync_files)

def detect_code_content_in_dataframe(df: pd.DataFrame, sync_files: bool = False) -> pd.DataFrame:
    """Detect and mark code content in DataFrame for special formatting.
    
    Uses Code Kingdom configuration to identify programming content in table cells
    and apply appropriate formatting hints.
    
    Args:
        df: DataFrame to analyze
        sync_files: Control cache synchronization behavior
        
    Returns:
        DataFrame with code content detection metadata
    """
    from ePy_docs.components.code import get_code_config, get_available_languages
    
    try:
        code_config = get_code_config()
        available_languages = get_available_languages(sync_files)
        validation_config = code_config.get('validation', {})
        allowed_languages = validation_config.get('allowed_languages', [])
        
        # Create a copy to avoid modifying original
        result_df = df.copy()
        
        # Add metadata about code content detection
        result_df._code_detection_applied = True
        result_df._detected_languages = []
        
        for col in result_df.columns:
            for idx in result_df.index:
                cell_value = result_df.loc[idx, col]
                if pd.notna(cell_value):
                    cell_str = str(cell_value)
                    
                    # Use Code Kingdom patterns for detection
                    code_patterns = {
                        'brackets': sum(1 for char in '(){}[]' if char in cell_str),
                        'operators': sum(1 for op in ['=', '==', '!=', '>=', '<=', '+=', '-='] if op in cell_str),
                        'keywords': sum(1 for keyword in ['def ', 'function', 'class ', 'import ', 'from '] if keyword in cell_str.lower()),
                        'languages': sum(1 for lang in allowed_languages[:10] if lang in cell_str.lower())
                    }
                    
                    # Calculate code confidence score
                    code_score = (
                        min(code_patterns['brackets'], 3) * 0.2 +
                        min(code_patterns['operators'], 3) * 0.3 +
                        code_patterns['keywords'] * 0.4 +
                        code_patterns['languages'] * 0.1
                    )
                    
                    # Mark as code if score exceeds threshold
                    if code_score >= 0.5:
                        if not hasattr(result_df, '_detected_languages'):
                            result_df._detected_languages = []
                        result_df._detected_languages.append((idx, col, 'code'))
        
        return result_df
        
    except Exception:
        # If Code Kingdom unavailable, return original DataFrame
        return df

def get_programming_language_for_content(content: str, sync_files: bool = False) -> str:
    """Identify programming language for given content using Code Kingdom.
    
    Args:
        content: Text content to analyze
        sync_files: Control cache synchronization behavior
        
    Returns:
        Detected programming language or 'text' if none detected
    """
    from ePy_docs.components.code import get_available_languages
    
    try:
        available_languages = get_available_languages(sync_files)
        content_lower = content.lower()
        
        # Language-specific patterns
        language_patterns = {
            'python': ['def ', 'import ', 'from ', 'print(', 'if __name__'],
            'javascript': ['function', 'var ', 'let ', 'const ', 'console.log'],
            'r': ['<-', 'library(', 'data.frame', 'ggplot'],
            'sql': ['select ', 'from ', 'where ', 'join ', 'group by'],
            'bash': ['#!/bin/bash', 'echo ', 'grep ', 'awk ', '$1', '$2'],
            'julia': ['function ', 'end', 'using ', 'println('],
        }
        
        # Score each language
        language_scores = {}
        for lang in available_languages:
            if lang in language_patterns:
                score = sum(1 for pattern in language_patterns[lang] if pattern in content_lower)
                if score > 0:
                    language_scores[lang] = score
        
        # Return language with highest score
        if language_scores:
            return max(language_scores, key=language_scores.get)
        else:
            return 'text'
            
    except Exception:
        return 'text'
