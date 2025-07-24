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
    """Load table configuration from tables.json, colors from colors.json, and categories from categories.json.
    
    Loads from user's project configuration directory.
    """
    from ePy_docs.project.setup import get_current_project_config
    
    current_config = get_current_project_config()
    config_base_path = current_config.folders.config
    
    # Load tables configuration
    config_path = os.path.join(config_base_path, 'components', 'tables.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        tables_config = json.load(f)
    
    # Load colors configuration
    colors_path = os.path.join(config_base_path, 'styler', 'colors.json')
    with open(colors_path, 'r', encoding='utf-8') as f:
        colors_config = json.load(f)
    
    # Load categories configuration
    categories_path = os.path.join(config_base_path, 'components', 'categories.json')
    with open(categories_path, 'r', encoding='utf-8') as f:
        categories_config = json.load(f)
    
    # Keep structured configuration instead of flattening
    structured_config = tables_config.copy()
    
    # Add category rules from categories.json
    if 'category_rules' in categories_config:
        structured_config['category_rules'] = categories_config['category_rules']
    
    # Add colors from colors.json
    if 'reports' in colors_config and 'tables' in colors_config['reports']:
        table_colors = colors_config['reports']['tables']
        
        # Add default header color (convert RGB array to hex)
        if 'header' in table_colors and 'default' in table_colors['header']:
            rgb = table_colors['header']['default']
            structured_config['header_color'] = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        # Add default palette name
        structured_config['palette_name'] = 'YlOrRd'  # Default matplotlib palette
    
    # Add coloring schemes from colors.json
    if 'coloring_schemes' in colors_config:
        structured_config['coloring_schemes'] = colors_config['coloring_schemes']
    
    return structured_config


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
        import json
        format_file = os.path.join(os.path.dirname(__file__), '..', 'units', 'format.json')
        format_mappings = {}
        if os.path.exists(format_file):
            with open(format_file, 'r', encoding='utf-8') as f:
                format_mappings = json.load(f)
        
        # Format column headers with unit formatting - use specified format
        renamed_columns = {}
        for col in df.columns:
            # Apply unit formatting to column names using specified format
            formatted_col = format_unit_display(str(col), unit_format, format_mappings)
            if formatted_col != col:
                renamed_columns[col] = formatted_col
            
            processed_col = ContentProcessor.smart_content_formatter(str(formatted_col))
            formatted_columns.append(TableFormatter.format_cell_text(processed_col, 2, is_header=True))
        
        # Rename columns if any were formatted
        if renamed_columns:
            formatted_df = formatted_df.rename(columns=renamed_columns)
        
        # Format cell contents with unit formatting applied to string values - use specified format
        for col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(
                lambda x: TableFormatter.format_cell_text(
                    format_unit_display(str(x), unit_format, format_mappings) if isinstance(x, str) else x, 
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
        
        # Get typography configuration for font settings
        typography_config = config['typography']
        font_size = typography_config['font_size']
        
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
    # Load configuration from tables.json
    config = _load_table_config()
    
    # Use config values when parameters are None
    palette_name = palette_name or config['palette_name']
    dpi = dpi or config['display']['dpi'] 
    header_color = header_color or config['header_color']
    font_size = font_size or config['typography']['font_size']
    header_font_size = header_font_size or config['typography']['header_font_size']
    title_font_size = title_font_size or config['typography']['title_font_size']
    padding = padding or config['display']['padding']
    
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
    
    # Apply intelligent coloring
    cell_colors = IntelligentColorManager.apply_intelligent_coloring(
        df_display, formatted_df, highlight_columns, color_config
    )
    
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
    
    # CRUCIAL: Configure multiline text rendering for cells with bullets
    _configure_multiline_text(table, formatted_df, formatted_columns)
    
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
    plt.savefig(img_path, bbox_inches='tight', dpi=dpi, facecolor='white', 
               pad_inches=0.2, transparent=False)
    plt.close(fig)
    
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
    config = _load_table_config()
    coloring_schemes = config['coloring_schemes']
    
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
    return coloring_schemes[scheme_name]


def get_column_format_rules(category: str) -> Dict[str, Any]:
    """
    Get formatting rules for a specific category.
    
    Args:
        category: Category name from categorize_column()
        
    Returns:
        Dictionary with formatting rules (precision, units, format type)
    """
    config = _load_category_rules()
    format_rules = config['format_rules']
    
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
