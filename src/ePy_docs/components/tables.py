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

from ePy_docs.styler.colors import (
    get_color, _load_cached_colors, TableColorConfig,
    TableColorPalette, get_custom_colormap
)
from ePy_docs.core.content import ContentProcessor
from .dataframes import (
    apply_table_preprocessing, prepare_dataframe_for_display,
    validate_dataframe_for_table, split_large_table
)
from ePy_docs.files.data import (
    convert_dataframe_to_table_with_units, filter_dataframe_rows, 
    sort_dataframe_rows, hide_dataframe_columns
)


def _load_table_config() -> Dict[str, Any]:
    """Load table configuration from tables.json - no fallbacks."""
    config_path = os.path.join(os.path.dirname(__file__), 'tables.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"tables.json not found at {config_path}. Table configuration is required.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in tables.json: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load tables.json: {e}")


def _load_category_rules() -> Dict[str, Any]:
    """Load category rules configuration from categories.json - no fallbacks."""
    config_path = os.path.join(os.path.dirname(__file__), 'categories.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"categories.json not found at {config_path}. Please ensure configuration file exists.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in categories.json: {e}")


class TableFormatter:
    """Handles table data formatting and text processing."""

    @staticmethod
    def format_cell_text(text, max_words_per_line, is_header=False):
        """Format cell text by limiting words per line."""
        text = ContentProcessor.smart_content_formatter(str(text))
        
        # Check if text contains bullet points, numbered lists, or newlines that should be preserved
        if '•' in text or '\n' in text or re.search(r'\d+\.\s+', text):
            # Preserve existing line structure for bullet points, numbered lists, and formatted text
            lines = text.split('\n')
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
        words = str(text).split()
        lines = []
        current_line = []
        
        # Use more aggressive wrapping for headers with special characters
        if is_header and '(' in text:
            parts = text.split('(')
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
    def format_dataframe(df: pd.DataFrame, max_words_per_line: int) -> Tuple[pd.DataFrame, List[str]]:
        """Format DataFrame for table output."""
        formatted_df = df.copy()
        formatted_columns = []

        # Importar format_unit_display para aplicar a los nombres de columnas y valores
        from ePy_docs.units.converter import format_unit_display
        
        # Format column headers with unit formatting
        renamed_columns = {}
        for col in df.columns:
            # Apply unit formatting to column names
            formatted_col = format_unit_display(str(col))
            if formatted_col != col:
                renamed_columns[col] = formatted_col
            
            processed_col = ContentProcessor.smart_content_formatter(str(formatted_col))
            formatted_columns.append(TableFormatter.format_cell_text(processed_col, 2, is_header=True))
        
        # Rename columns if any were formatted
        if renamed_columns:
            formatted_df = formatted_df.rename(columns=renamed_columns)
        
        # Format cell contents with unit formatting applied to string values
        for col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(
                lambda x: TableFormatter.format_cell_text(
                    format_unit_display(str(x)) if isinstance(x, str) else x, 
                    max_words_per_line
                )
            )

        return formatted_df, formatted_columns


class TableDimensionCalculator:
    """Calculates table dimensions for optimal display."""
    
    @staticmethod
    def calculate_dimensions(formatted_df: pd.DataFrame, formatted_columns: List[str]) -> Tuple[List[float], List[int], int]:
        """Calculate column widths, row heights, and header height."""
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
            # Asegurar una altura mínima y añadir margen para texto multilínea
            return max_lines
        
        col_widths = [get_column_width([col] + formatted_df[col].values.tolist()) for col in formatted_df.columns]
        total_width = sum(col_widths)
        col_widths = [w/total_width for w in col_widths]
        
        row_heights = [get_row_height(row) for _, row in formatted_df.iterrows()]
        
        # Calculate header height con más precisión y espacio garantizado
        header_lines = [len(str(col).split('\n')) for col in formatted_columns]
        header_row_height = max(header_lines)
        
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
            
            # Fallback to old system if new system doesn't have colors
            colors_data = _load_cached_colors()
            
            # Search paths for category colors
            search_paths = [
                ["visualization", category],
                ["reports", "tables", category],
                ["visualization", "nodes"] if "node" in category else None,
                ["visualization", "elements"] if "element" in category else None
            ]
            
            # Remove None entries
            search_paths = [path for path in search_paths if path is not None]
            
            for path in search_paths:
                current = colors_data
                for key in path:
                    if key in current:
                        current = current[key]
                    else:
                        current = None
                        break
                
                if current and isinstance(current, dict):
                    # Normalize colors
                    normalized_colors = {}
                    for k, v in current.items():
                        if not isinstance(k, str) or k.startswith('_'):
                            continue
                        
                        key_lower = k.lower().strip()
                        resolved_color = None
                        
                        if isinstance(v, str):
                            try:
                                # Try to resolve color reference (e.g., "brand.accent_green")
                                # Get the color in hex format for table use
                                resolved_color = get_color(v, format_type="hex", sync_json=True)
                            except Exception as e:
                                resolved_color = None
                        elif isinstance(v, list) and len(v) >= 3:
                            try:
                                r, g, b = v[:3]
                                resolved_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
                            except (ValueError, TypeError):
                                continue
                        
                        if resolved_color:
                            normalized_colors[key_lower] = resolved_color
                    
                    if normalized_colors:
                        return normalized_colors
            
            return {}
            
        except Exception as e:
            print(f"Warning: Could not get colors for category '{category}': {e}")
            return {}

    @staticmethod
    def apply_intelligent_coloring(df: pd.DataFrame, formatted_df: pd.DataFrame, 
                                 highlight_columns: Optional[List[str]] = None,
                                 color_config: Optional[TableColorConfig] = None
                                 ) -> List[List[Tuple[float, float, float, float]]]:
        """Apply intelligent coloring based on column analysis."""
        cell_colors = [[(1, 1, 1, 0)] * len(formatted_df.columns) for _ in range(len(formatted_df))]
        
        # If highlight_columns is None, use all columns for coloring
        # If highlight_columns is an empty list, don't apply any coloring (simple table)
        if highlight_columns is None:
            highlight_columns = list(df.columns)
        elif highlight_columns == []:
            # Empty list means no coloring desired - return default white colors
            return cell_colors
            
        # Analyze columns to determine coloring strategy
        column_strategies = IntelligentColorManager.analyze_columns(df, highlight_columns)
        orig_to_formatted_col_map = {col: i for i, col in enumerate(formatted_df.columns)}
        
        for col, strategy in column_strategies.items():
            if col not in df.columns:
                continue
                
            col_idx_orig = list(df.columns).index(col)
            col_idx = orig_to_formatted_col_map.get(col, col_idx_orig)
            
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
                palette_name = color_config.palette.value if isinstance(color_config.palette, TableColorPalette) else color_config.palette
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
                     n_rows: Optional[int] = None,
                     print_title_in_image: bool = False) -> str:
    """Create a table image with configuration from tables.json.
    
    Args:
        df: DataFrame to display
        output_dir: Directory to save the image
        table_number: Table number for file naming
        title: Optional title for the table
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
        print_title_in_image: Whether to print the title directly in the image
        
    Returns:
        Path to the generated image file
    """
    # Load configuration from tables.json - no fallbacks
    config = _load_table_config()
    
    # Use config values when parameters are None
    if palette_name is None:
        palette_name = config['palette_name']
    if dpi is None:
        dpi = config['dpi'] 
    if header_color is None:
        header_color = config['header_color']
    if font_size is None:
        font_size = config['font_size']
    if header_font_size is None:
        header_font_size = config['header_font_size']
    if title_font_size is None:
        title_font_size = config['title_font_size']
    if padding is None:
        padding = config['padding']
    
    # Validate required parameters are now loaded
    if palette_name is None:
        raise ValueError("palette_name is required. Use one of: 'Blues', 'Greens', 'Reds', 'Oranges', 'Purples', 'YlOrRd', 'viridis', 'plasma' or custom palette from colors.json")
    if dpi is None:
        raise ValueError("dpi is required in styles.json table_style configuration")
    
    # Apply unit conversion and processing pipeline
    df_processed, conversion_log = prepare_dataframe_for_display(df)

    # Apply comprehensive preprocessing (filtering, sorting, row limiting, column management)
    df_display = apply_table_preprocessing(
        df_processed, 
        hide_columns=hide_columns,
        filter_by=filter_by,
        sort_by=sort_by,
        n_rows=n_rows
    )

    # Formatear DataFrame
    max_words_per_line = max(1, 8 - len(df_display.columns))
    formatted_df, formatted_columns = TableFormatter.format_dataframe(df_display, max_words_per_line)
    
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
    
    # Apply intelligent coloring
    cell_colors = IntelligentColorManager.apply_intelligent_coloring(
        df_display, formatted_df, highlight_columns, color_config
    )
    
    # Load configuration for table dimensions
    from ePy_docs.styler.setup import get_styles_config
    styles_config = get_styles_config()
    table_settings = styles_config.get('pdf_settings', {}).get('table_settings', {})
    
    # Use configured width instead of hardcoded values
    PAGE_WIDTH_INCHES = table_settings.get('max_width_inches', 7.5)
    PAGE_MARGINS = 0.75       # Keep margins reasonable
    USABLE_WIDTH = PAGE_WIDTH_INCHES - (PAGE_MARGINS * 2)
    
    # Always use the configured page width for all tables
    fig_width = USABLE_WIDTH
    base_cell_height = 0.2
    # Reduce excessive padding for header - adjust to text height
    total_height = header_row_height * base_cell_height  # More precise header height
    for row_height in row_heights:
        total_height += row_height * base_cell_height
    fig_height = total_height
    
    # Create figure with carefully calculated space for title
    # Use configurable title font size
    title_space = 0 
    if title and print_title_in_image:
        # Calculate an estimate of how much space the title will need (in inches)
        # We add extra space depending on title length to account for wrapping
        title_text = f"{table_number}: {title}"
        # Use the wrap function to get accurate line count
        wrapped_title = ContentProcessor.wrap_title_text(title_text, max_width_chars=85)
        title_lines = len(wrapped_title.split('\n'))
        title_space = 0.15 + (title_lines * 0.15)  # More compact spacing
    
    fig_height_with_title = fig_height + title_space
    
    # Create figure with the calculated dimensions
    fig, ax = plt.subplots(figsize=(fig_width, fig_height_with_title))
    ax.axis('off')
    
    # Coordinates to properly position elements within the figure
    # We use figure coordinates (0,0 at bottom left, 1,1 at top right)
    title_bottom = 0.95  # Position title at the top with fixed margin
    
    # Add title directly to the figure if provided - left-justified with configurable size
    if title and print_title_in_image:
        title_text = f"{table_number}: {title}"
        # Wrap title text for better display
        wrapped_title = ContentProcessor.wrap_title_text(title_text, max_width_chars=85)
        
        # Calculate title height as a fraction of figure height
        title_height_frac = title_space / fig_height_with_title
        
        # Create a separate axes just for the title to avoid overlap
        title_ax = fig.add_axes([0.01, 1.0 - title_height_frac, 0.98, title_height_frac])
        title_ax.axis('off')
        title_ax.text(0.0, 0.5, wrapped_title, fontsize=title_font_size, 
                     fontweight='bold', va='center', ha='left')
    
    # Calculate the exact position for the table
    # When there's a title, position the table precisely below the title area
    table_top_position = title_space / fig_height_with_title if title else 0.01
    
    header_colors = [header_color] * len(formatted_df.columns)
    
    # Create a dedicated axis for the table with precise positioning 
    # This ensures complete separation from the title
    table_height = 1.0 - table_top_position
    table_ax = fig.add_axes([0.01, 0.0, 0.98, table_height])
    table_ax.axis('off')
    
    # Create the table in the dedicated table axis
    table = table_ax.table(
        cellText=formatted_df.values,
        colLabels=formatted_columns,
        cellLoc=alignment.lower(),
        # Use the full area of the table axis
        bbox=[0, 0, 1, 1],
        colColours=header_colors,
        cellColours=cell_colors,
        colWidths=col_widths
    )
    
    # Apply styling to table cells
    _apply_table_styling(table, row_heights, header_row_height, base_cell_height, 
                        fig_height, font_size, header_font_size, header_colors, 
                        padding, formatted_df, alignment)
    
    # CRUCIAL: Configure multiline text rendering for cells with bullets
    _configure_multiline_text(table, formatted_df, formatted_columns)
    
    # Rather than using tight_layout which can cause issues with axes,
    # we've already precisely positioned our title and table axes
    
    # Save image with properly spaced title and table
    # Handle both integer and string table numbers for file naming
    if isinstance(table_number, str):
        # Para números decimales como "1.1", "1.2", etc.
        if '.' in table_number:
            # Mantener formato decimal: table_1.1.png, table_1.2.png
            img_path = os.path.join(output_dir, f"table_{table_number}.png")
        else:
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
    plt.savefig(img_path, bbox_inches='tight', dpi=dpi, facecolor='white', 
               pad_inches=0.2, transparent=False)
    plt.close(fig)
    
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
    # Convertir padding a un valor fraccional apropiado para matplotlib
    padding_fraction =  padding / 100.0 / 20
    
    for pos, cell in table._cells.items():
        # CORREGIR: Usar padding_fraction en lugar de base_cell_height para PAD
        cell.PAD = padding_fraction
        row = pos[0]
        
        # Fix vertical alignment - set to center/middle for all cells
        cell.get_text().set_verticalalignment('center')
        
        # Apply horizontal alignment based on parameter, but ensure proper alignment
        horizontal_align = alignment.lower() if alignment.lower() in ['left', 'center', 'right'] else 'center'
        cell.get_text().set_horizontalalignment(horizontal_align)
        
        if row == 0:
            # Header row: adjust height more precisely to text content
            cell_height_value = (header_row_height) * base_cell_height / fig_height
        else:
            lines_needed = row_heights[row - 1]
            cell_height_value = lines_needed * base_cell_height / fig_height
        
        cell.set_height(cell_height_value)


def _configure_multiline_text(table, formatted_df, formatted_columns):
    """Configure multiline text rendering for table cells with proper bullet display."""
    
    # Process header cells
    for col_idx, col_text in enumerate(formatted_columns):
        if '\n' in str(col_text):
            cell = table._cells[(0, col_idx)]
            # Configure multiline text for header
            text_obj = cell.get_text()
            text_obj.set_text(str(col_text))
            # Keep center alignment for headers
            text_obj.set_horizontalalignment('center')
            text_obj.set_verticalalignment('center')
    
    # Process data cells
    for row_idx in range(len(formatted_df)):
        for col_idx, col_name in enumerate(formatted_df.columns):
            cell_value = formatted_df.iloc[row_idx, col_idx]
            
            # Check if cell contains multiline text, bullets, or numbered lists
            if isinstance(cell_value, str) and ('\n' in cell_value or '•' in cell_value or re.search(r'\d+\.\s+', cell_value)):
                cell = table._cells[(row_idx + 1, col_idx)]  # +1 because row 0 is header
                
                # Configure text properties for better bullet rendering
                text_obj = cell.get_text()
                text_obj.set_text(str(cell_value))
                
                # Ensure proper font that supports Unicode bullets
                text_obj.set_fontfamily('Arial')  # Arial has good Unicode support and is widely available
                
                # For cells with bullets or numbered lists, use left alignment but keep vertical center
                # This provides better readability for bullet lists while maintaining overall table consistency
                if '•' in cell_value or re.search(r'\d+\.\s+', cell_value):
                    text_obj.set_horizontalalignment('left')   # Left align for bullets/numbers readability
                    text_obj.set_verticalalignment('center')   # Center vertically to match other cells
                else:
                    # For multiline text without bullets, maintain center alignment
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
                            n_rows: Optional[int] = None, max_rows_per_table: Optional[Union[int, float, List[Union[int, float]]]] = None,
                            print_title_in_image: bool = False) -> List[str]:
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
        print_title_in_image: Whether to print the title directly in the image (False = clean images)
        
    Returns:
        List of paths to the generated image files
    """
    # Load configuration from PDFStyleManager only if max_rows_per_table is not specified
    if max_rows_per_table is None:
        try:
            from ePy_docs.styler.styler import PDFStyleManager
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
            n_rows=None,     # Already applied
            print_title_in_image=print_title_in_image
        )
        return [img_path]
    
    # Split large table into chunks
    df_chunks = split_large_table(df_processed, max_rows_per_table)
    
    img_paths = []
    for i, chunk in enumerate(df_chunks):
        # For table images, use the original title without "(Parte n/m)"
        # The "(Parte n/m)" will be added to the Quarto caption separately
        chunk_title = title  # Keep original title for the image
        
        # Use decimal numbering for the table number in format "base.part"
        table_number_decimal = f"{base_table_number}.{i+1}"
        
        img_path = create_table_image(
            df=chunk,
            output_dir=output_dir,
            table_number=table_number_decimal,  # Pass as string for decimal numbering
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
            n_rows=None,     # Already applied
            print_title_in_image=print_title_in_image
        )
        img_paths.append(img_path)
    
    return img_paths

def categorize_column(column_name: str, sample_values: List[Any] = None) -> str:
    """
    Categorize a column based on its name and sample values using rules from categories.json.
    
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
            name_keywords = rules.get('name_keywords', [])
            for keyword in name_keywords:
                if keyword.lower() in column_name_lower:
                    # Exact match gets higher score
                    if keyword.lower() == column_name_lower:
                        score += 10
                    # Partial match gets lower score
                    else:
                        score += 5
            
            # Check coordinate patterns for specific categories (high weight for exact matches)
            coordinate_patterns = rules.get('coordinate_patterns', [])
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
                value_keywords = rules.get('value_keywords', [])
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
        print(f"Warning: Could not categorize column '{column_name}': {e}")
        return 'general'


def get_column_coloring_scheme(category: str) -> Dict[str, str]:
    """
    Get the appropriate coloring scheme for a category.
    
    Args:
        category: Category name from categorize_column()
        
    Returns:
        Dictionary mapping values to colors
    """
    try:
        config = _load_category_rules()
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
        
        scheme_name = scheme_mapping.get(category, 'intensity_based')
        return coloring_schemes.get(scheme_name, {})
        
    except Exception as e:
        print(f"Warning: Could not get coloring scheme for category '{category}': {e}")
        return {}


def get_column_format_rules(category: str) -> Dict[str, Any]:
    """
    Get formatting rules for a specific category.
    
    Args:
        category: Category name from categorize_column()
        
    Returns:
        Dictionary with formatting rules (precision, units, format type)
    """
    try:
        config = _load_category_rules()
        format_rules = config.get('format_rules', {})
        
        # Map categories to format rules
        rule_mapping = {
            'nodes': 'coordinates',
            'dimensions': 'coordinates', 
            'forces': 'forces',
            'properties': 'stresses',
            'design': 'ratios',
            'analysis': 'ratios'
        }
        
        rule_name = rule_mapping.get(category, 'coordinates')
        return format_rules.get(rule_name, {
            'precision': 2,
            'units': '',
            'format': 'decimal'
        })
        
    except Exception as e:
        print(f"Warning: Could not get format rules for category '{category}': {e}")
        return {'precision': 2, 'units': '', 'format': 'decimal'}
