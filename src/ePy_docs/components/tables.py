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
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def get_tables_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load centralized table configuration.
    
    Args:
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Complete tables configuration dictionary.
    """
    config_path = _resolve_config_path('components/tables', sync_files)
    return _load_cached_files(config_path, sync_files)

def create_table_image(data: Union[pd.DataFrame, List[List]], 
                      title: str = None, output_dir: str = None, 
                      filename: str = None, layout_style: str = "corporate", 
                      sync_files: bool = False, 
                      highlight_columns: Optional[List[str]] = None,
                      palette_name: Optional[str] = None) -> str:
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
        
    Returns:
        Path to generated image file.
        
    Raises:
        ValueError: If layout_style not found in configuration.
    """
    config = get_tables_config(sync_files)
    
    if layout_style not in config['layout_styles']:
        raise ValueError(f"Layout style '{layout_style}' not found")
    
    style_config = config['layout_styles'][layout_style]
    
    # REINO TABLES COMERCIO: Obtener configuración de fuentes desde Reino Text
    from ePy_docs.components.text import get_text_config
    text_config = get_text_config(sync_files)
    text_style_ref = style_config['text_style_reference']
    
    if text_style_ref not in text_config['layout_styles']:
        raise ValueError(f"Text style reference '{text_style_ref}' not found in Reino Text")
    
    text_layout_config = text_config['layout_styles'][text_style_ref]
    
    # Obtener familia de fuente desde typography.normal (para contenido de tabla)
    if 'typography' not in text_layout_config or 'normal' not in text_layout_config['typography']:
        raise ValueError(f"Typography configuration missing for layout '{text_style_ref}' in Reino Text")
    
    font_family_name = text_layout_config['typography']['normal']['family']
    font_config = text_config['font_families'][font_family_name]
    
    size_config = config['font_sizes']
    display_config = config['display']
    format_config = config['formatting']
    
    df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
    
    # DIMENSIÓN COMERCIO: Formateo de superscripts desde Tribu Format
    from ePy_docs.components.format import format_superscripts
    
    for col in df.columns:
        df[col] = df[col].apply(lambda x: format_superscripts(str(x), 'matplotlib', sync_files))
    
    # DIMENSIÓN SETUP: Acceso oficial a Reino Text para alineación por layout_styles
    from ePy_docs.components.text import get_text_config
    text_config = get_text_config(sync_files)
    
    if layout_style not in text_config['layout_styles']:
        raise RuntimeError(f"Layout style '{layout_style}' not found in Reino Text")
    
    text_style_config = text_config['layout_styles'][layout_style]
    if 'tables' not in text_style_config or 'alignment' not in text_style_config['tables']:
        raise RuntimeError(f"Alignment configuration missing for layout_style '{layout_style}' in Reino Text")
    
    alignment_config = text_style_config['tables']['alignment']
    
    return _generate_table_image(df, title, output_dir, filename, 
                                style_config, font_config, size_config, 
                                display_config, format_config, highlight_columns, 
                                palette_name, layout_style, alignment_config, sync_files)

def _generate_table_image(df: pd.DataFrame, title: str, output_dir: str, 
                         filename: str, style_config: Dict, font_config: Dict,
                         size_config: Dict, display_config: Dict, 
                         format_config: Dict, highlight_columns: Optional[List[str]] = None,
                         palette_name: Optional[str] = None, layout_style: str = 'corporate',
                         alignment_config: Optional[Dict[str, str]] = None,
                         sync_files: bool = False) -> str:
    """Generate table image using centralized configuration.
    
    Args:
        df: DataFrame containing table data.
        title: Table title.
        output_dir: Output directory.
        filename: Output filename.
        style_config: Style configuration for layout.
        font_config: Font configuration.
        size_config: Size configuration.
        display_config: Display configuration.
        format_config: Formatting configuration.
        
    Returns:
        Path to generated image file.
    """
    if not output_dir:
        output_dir = display_config['directory']
    os.makedirs(output_dir, exist_ok=True)
    
    if not filename:
        counter = len([f for f in os.listdir(output_dir) if f.startswith('table_')]) + 1
        filename = format_config['filename_format'].format(counter=counter, ext=display_config['image_format'])
    
    filepath = os.path.join(output_dir, filename)
    
    # CONFIGURE PRIMARY FONT WITH AUTOMATIC FALLBACK
    # For handwritten fonts that may not have all glyphs,
    # configure a fallback list that matplotlib will use automatically
    primary_font = font_config['primary']
    fallback_fonts = font_config['fallback'].split(',')
    
    # Create complete font list with fallbacks
    font_list = [primary_font.strip('"')] + [f.strip().strip('"') for f in fallback_fonts]
    
    # Configure matplotlib to use font list
    plt.rcParams['font.family'] = font_list
    
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
        if is_header:
            # Headers always use handwritten font with automatic fallback
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
        elif is_missing_value(text_value):
            # Missing values (including "---") use handwritten font to maintain consistent style
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('italic')
        else:
            # Normal values use handwritten font with automatic fallback
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
    
    # DIMENSIÓN TRANSPARENCIA: WRAPPING AUTOMÁTICO PRE-TABLA
    # OBJETIVO: Resolver overflow horizontal envolviendo texto antes de matplotlib
    from ePy_docs.components.format import prepare_dataframe_with_wrapping
    df = prepare_dataframe_with_wrapping(df, layout_style, sync_files)
    
    # DIMENSIÓN SETUP: Configuración de alineación por layout_styles vía Reino Text
    # DIMENSIÓN TRANSPARENCIA: Sin fallbacks - debe existir configuración válida
    if alignment_config is None:
        raise RuntimeError(f"No alignment configuration provided for layout_style '{layout_style}'")
    
    font_size_content = size_config['content'][style_config['font_sizes']['content']]
    font_size_header = size_config['header'][style_config['font_sizes']['header']]
    
    # Recalcular dimensiones después del wrapping
    num_rows, num_cols = df.shape
    
    # DIMENSIÓN SETUP: Ancho desde configuración oficial de layout_style
    # DIMENSIÓN TRANSPARENCIA: Sin comercio ilícito - todo desde tables.json
    table_width = style_config.get('table_width_inches', display_config.get('max_width_inches', 8.0))
    
    # Altura mínima calculada según contenido - OPTIMIZADA PARA MENOS PADDING
    cell_height = display_config.get('base_cell_height_inches', 0.35)  # Reducido de 0.45 a 0.35
    total_height_minima = (num_rows + 1) * cell_height * 0.5  # Factor 0.5 = padding más compacto
    
    # FIGURA CON ANCHO ESPECÍFICO POR LAYOUT_STYLE
    fig, ax = plt.subplots(figsize=(table_width, total_height_minima))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=df.values, colLabels=df.columns,
                    cellLoc='left', loc='center')  # Default left, se sobrescribe individualmente
    
    # FORZAR ANCHO COMPLETO: La tabla debe ocupar todo el ancho disponible
    table.auto_set_font_size(False)
    table.scale(1.0, 1.0)  # Escala base, se ajustará individualmente por celda
    
    # CORRECCIÓN DE PADDING LATERAL Y AJUSTE AUTOMÁTICO DE FUENTE
    def auto_adjust_font_size(cell, original_font_size, max_width_chars=None):
        """Ajustar automáticamente el tamaño de fuente si el contenido no cabe."""
        cell_text = cell.get_text().get_text()
        current_font_size = original_font_size
        
        # Calcular longitud efectiva del contenido
        if '\n' in cell_text:
            # Para texto multilínea, usar la línea más larga
            lines = cell_text.split('\n')
            max_line_length = max(len(line) for line in lines)
        else:
            max_line_length = len(cell_text)
        
        # Detectar si necesita reducción de fuente (con moderación)
        if max_line_length > 25:  # Umbral para texto muy largo
            reduction_factor = min(0.85, max(0.7, 25 / max_line_length))  # Reducción moderada
            current_font_size = original_font_size * reduction_factor
        elif max_line_length > 15:  # Umbral para texto largo
            reduction_factor = 0.9  # Reducción ligera
            current_font_size = original_font_size * reduction_factor
        
        # Aplicar el tamaño ajustado
        cell.set_fontsize(current_font_size)
        return current_font_size

    # APLICAR AJUSTE DE FUENTE A HEADERS Y CONTENIDO
    # Headers (fila 0) - ajuste automático si no cabe + configuración de fuente
    for j in range(num_cols):
        cell = table[(0, j)]
        header_text = df.columns[j]
        
        # Apply superscript formatting to header text for proper unit rendering
        from ePy_docs.components.format import format_superscripts
        formatted_header = format_superscripts(str(header_text), 'matplotlib', sync_files)
        cell.get_text().set_text(formatted_header)
        
        # Configurar fuente específica para header
        configure_cell_font(cell, header_text, is_header=True)
        
        cell.set_fontsize(font_size_header)
        if style_config['styling']['header_bold']:
            cell.set_text_props(weight='bold')
        # Ajustar fuente automáticamente si el header es muy largo
        auto_adjust_font_size(cell, font_size_header)

    # Contenido (filas 1+) - ajuste automático si no cabe + configuración de fuente
    for i in range(1, num_rows + 1):
        for j in range(num_cols):
            cell = table[(i, j)]
            
            # Obtener valor original del DataFrame para detección de missing
            df_row_idx = i - 1  # Convertir índice de tabla a DataFrame
            if df_row_idx < len(df) and j < len(df.columns):
                original_value = df.iloc[df_row_idx, j]
            else:
                original_value = None
            
            # Configurar fuente específica según contenido
            configure_cell_font(cell, original_value, is_header=False)
            
            cell.set_fontsize(font_size_content)
            # Ajustar fuente automáticamente si el contenido es muy largo
            auto_adjust_font_size(cell, font_size_content)

    # AJUSTE AUTOMÁTICO DE ANCHO POR COLUMNA
    def calculate_column_width_factor(col_index, column_name):
        """Calcular factor de ancho específico para cada columna."""
        base_width_factor = 1.0
        max_content_length = len(str(column_name))  # Empezar con el header
        
        # Analizar contenido de toda la columna para encontrar el más largo
        for row_idx in range(len(df)):
            cell_value = df.iloc[row_idx, col_index]
            cell_str = str(cell_value)
            
            # Considerar texto multilínea
            if '\n' in cell_str:
                # Para texto multilínea, usar la línea más larga
                lines = cell_str.split('\n')
                max_line_length = max(len(line) for line in lines)
                max_content_length = max(max_content_length, max_line_length)
            else:
                max_content_length = max(max_content_length, len(cell_str))
        
        # Calcular factor de ancho basado en contenido - OPTIMIZADO PARA EFICIENCIA
        if max_content_length <= 3:
            width_factor = 0.7  # Columnas muy cortas - más compactas
        elif max_content_length <= 8:
            width_factor = 0.9  # Ancho reducido
        elif max_content_length <= 15:
            width_factor = 1.0  # Ancho normal
        elif max_content_length <= 25:
            width_factor = 1.2  # Ancho expandido moderado
        elif max_content_length <= 35:
            width_factor = 1.4  # Ancho largo moderado
        else:
            width_factor = 1.6  # Ancho muy largo controlado
        
        # Factor adicional para ecuaciones y símbolos especiales - REDUCIDO
        for row_idx in range(len(df)):
            cell_value = df.iloc[row_idx, col_index]
            cell_str = str(cell_value)
            if any(char in cell_str for char in ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']) or \
               any(pattern in cell_str for pattern in ['·', '×', '÷', '±', '≤', '≥']):
                width_factor *= 1.05  # Espacio adicional reducido para símbolos (5% en lugar de 10%)
                break
        
        return width_factor

    # APLICAR ANCHO AUTOMÁTICO A CADA COLUMNA
    for j in range(num_cols):
        column_name = df.columns[j]
        width_factor = calculate_column_width_factor(j, column_name)
        
        # Aplicar ancho a todas las celdas de esta columna
        for i in range(num_rows + 1):  # +1 para incluir header
            cell = table[(i, j)]
            current_width = cell.get_width()
            cell.set_width(current_width * width_factor)

    # FORMATEO CORRECTO DE TEXTO MULTILÍNEA Y AJUSTE POR FILA COMPLETA
    def calculate_row_height_for_multiline(row_index, is_header=False):
        """Calcular altura necesaria basada en altura real de letras + holgura proporcional."""
        max_lines_in_row = 1
        base_font_size = float(font_size_header if is_header else font_size_content)
        
        if is_header:
            # Analizar headers para encontrar el que requiere más líneas
            for col in df.columns:
                col_str = str(col)
                line_count = col_str.count('\n') + 1
                max_lines_in_row = max(max_lines_in_row, line_count)
                
                # Mejora específica para headers: estimación más conservadora
                if len(col_str) > 20:  # Umbral más bajo para headers
                    # Headers necesitan más espacio por caracteres más grandes
                    estimated_lines = len(col_str) // 20 + 1  # Menos caracteres por línea
                    max_lines_in_row = max(max_lines_in_row, estimated_lines)
                
                # Considerar casos especiales en headers (palabras muy largas)
                if any(len(word) > 15 for word in col_str.split('\n')):
                    max_lines_in_row = max(max_lines_in_row, line_count + 1)
        else:
            # Analizar todas las celdas de esta fila
            if row_index < len(df):
                for col in df.columns:
                    cell_value = df.iloc[row_index, df.columns.get_loc(col)]
                    cell_str = str(cell_value)
                    
                    # Contar líneas explícitas
                    line_count = cell_str.count('\n') + 1
                    max_lines_in_row = max(max_lines_in_row, line_count)
                    
                    # Estimar líneas por longitud (wrap automático) - más conservador
                    if len(cell_str) > 25:  # Umbral más bajo
                        estimated_lines = len(cell_str) // 25 + 1  # Caracteres por línea más conservador
                        max_lines_in_row = max(max_lines_in_row, estimated_lines)
        
        # CÁLCULO BASADO EN ALTURA REAL DE LETRAS + HOLGURA PROPORCIONAL
        # Altura base de una línea de texto (en puntos tipográficos)
        line_height_points = base_font_size * 1.2  # 1.2 = interlineado estándar
        
        # CORRECCIÓN POR TIPO DE FONT: serif vs sans vs mono vs handwritten
        # Las fonts serif necesitan más espacio vertical por sus características
        font_type_factor = 1.0
        if 'type' in font_config:
            font_type = font_config['type']
            if font_type == 'serif':
                # Serif fonts necesitan 15% más altura por descenders y serifs
                font_type_factor = 1.15
            elif font_type == 'monospace':
                # Monospace fonts necesitan 10% más altura por consistencia
                font_type_factor = 1.10
            elif font_type == 'handwritten':
                # Handwritten fonts necesitan 25% más altura por irregularidad y estilo
                font_type_factor = 1.25
            # Sans serif usa factor base 1.0
        
        # Holgura adicional proporcional al número de líneas - OPTIMIZADA
        # Más líneas = más holgura para evitar apretamiento visual, pero más compacta
        if max_lines_in_row == 1:
            # Una línea: holgura mínima (15% extra - reducido de 20%)
            spacing_factor = 1.15
        elif max_lines_in_row <= 3:
            # 2-3 líneas: holgura moderada (25% extra - reducido de 30%)
            spacing_factor = 1.25
        elif max_lines_in_row <= 5:
            # 4-5 líneas: holgura generosa (30% extra - reducido de 40%)
            spacing_factor = 1.30
        else:
            # 6+ líneas: holgura máxima (35% extra - reducido de 50%)
            spacing_factor = 1.35
        
        # Headers necesitan holgura adicional por el bold - OPTIMIZADA
        if is_header:
            spacing_factor *= 1.10  # 10% extra para texto bold (reducido de 15%)
        
        # Factor final: altura real × líneas × holgura × corrección de font
        height_factor = (line_height_points * max_lines_in_row * spacing_factor * font_type_factor) / (base_font_size * 1.2)
        
        # Asegurar factor mínimo para legibilidad
        height_factor = max(height_factor, 1.0)
        
        return height_factor

    # APLICAR ALTURA UNIFORME POR FILA COMPLETA
    # Header (fila 0) - alineación desde Reino Text
    header_height_factor = calculate_row_height_for_multiline(0, is_header=True)
    for j in range(num_cols):
        cell = table[(0, j)]
        current_height = cell.get_height()
        cell.set_height(current_height * header_height_factor)
        
        # DIMENSIÓN SETUP: Alineación de headers desde Reino Text por layout_styles
        cell_text = cell.get_text().get_text()
        is_multiline = '\n' in cell_text or len(cell_text) > 25
        
        va = alignment_config['header_vertical']
        ha = alignment_config['header_horizontal']
        
        cell.set_text_props(
            verticalalignment=va, 
            horizontalalignment=ha
        )
        
        # DIMENSIÓN APARIENCIA: Padding interno optimizado para eficiencia de espacio
        if is_multiline:
            # Padding proporcional al número de líneas - REDUCIDO para mayor eficiencia
            max_lines = cell_text.count('\n') + 1
            proportional_padding = 0.010 + (max_lines * 0.003)  # Base reducido + incremental
            cell.PAD = min(proportional_padding, 0.025)  # Máximo 2.5%
        else:
            # Headers de una línea necesitan padding base por el bold - REDUCIDO
            cell.PAD = 0.015  # Reducido de 0.02

    # Filas de datos (1 a num_rows) - alineación desde Reino Text
    for i in range(1, num_rows + 1):
        row_height_factor = calculate_row_height_for_multiline(i - 1, is_header=False)
        
        # Aplicar la MISMA altura a TODAS las celdas de esta fila
        for j in range(num_cols):
            cell = table[(i, j)]
            current_height = cell.get_height()
            cell.set_height(current_height * row_height_factor)
            
            # DIMENSIÓN SETUP: Alineación de contenido desde Reino Text por layout_styles
            cell_text = cell.get_text().get_text()
            is_multiline = '\n' in cell_text or len(cell_text) > 30
            
            # Determinar si es contenido numérico para alineación especial
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
            
            # DIMENSIÓN APARIENCIA: Padding interno optimizado para contenido
            if is_multiline:
                # Padding proporcional al número de líneas del contenido - REDUCIDO
                max_lines = cell_text.count('\n') + 1
                proportional_padding = 0.008 + (max_lines * 0.002)  # Base menor + incremental reducido
                current_cell = table[(i, j)]
                current_cell.PAD = min(proportional_padding, 0.018)  # Máximo 1.8% para contenido

    # DIMENSIÓN SETUP: Acceso oficial a Reino Colors para layout_styles
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
    header_config = table_config.get('header', {}).get('default', {
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
    
    # CORRECCIÓN DE PADDING LATERAL: Asegurar uniformidad
    # FIDELIDAD ABSOLUTA: Padding exacto y uniforme en todas las direcciones
    # BASADO EN: Configuración JSON + ancho específico por layout_style
    
    # Calcular padding uniforme basado en configuración
    base_padding = display_config['padding_inches']  # 1mm = 0.0394 inches
    
    plt.savefig(filepath, 
               dpi=display_config['dpi'], 
               bbox_inches='tight',
               pad_inches=base_padding,  # Padding uniforme en todas las direcciones
               transparent=display_config.get('transparent', False))
    plt.close()
    
    return filepath

def process_table_for_report(data: Union[pd.DataFrame, List[List]], 
                           title: str = None, output_dir: str = None, 
                           figure_counter: int = 1, layout_style: str = "corporate", 
                           sync_files: bool = False, 
                           highlight_columns: Optional[List[str]] = None,
                           palette_name: Optional[str] = None) -> tuple[str, str]:
    """Process table for report with automatic counter and ID.
    
    Args:
        data: DataFrame or list of lists containing table data.
        title: Table title.
        output_dir: Output directory.
        figure_counter: Counter for figure numbering.
        layout_style: One of 8 universal layout styles.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Tuple of (image_path, figure_id).
    """
    config = get_tables_config(sync_files)
    format_config = config['formatting']
    
    figure_id = format_config['figure_id_format'].format(counter=figure_counter)
    filename = format_config['filename_format'].format(
        counter=figure_counter, 
        ext=config['display']['image_format']
    )
    
    image_path = create_table_image(
        data=data,
        title=title,
        output_dir=output_dir,
        filename=filename,
        layout_style=layout_style,
        sync_files=sync_files,
        highlight_columns=highlight_columns,
        palette_name=palette_name
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
