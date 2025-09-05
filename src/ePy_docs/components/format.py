"""Format configuration and utilities.

Format processing with centralized configuration through _load_cached_files.
Tribu Format - exists at the boundary of multiple kingdoms.
Handles unicode, superscripts, text wrapping, and cross-kingdom formatting standards.
Also provides universal font management for PDF, HTML, and image rendering.
"""
import textwrap
import pandas as pd
from typing import Dict, Any, Union, List, Tuple
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def get_format_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load centralized format configuration.
    
    DIMENSIÓN SETUP: Oficina comercial oficial para Tribu Format.
    
    Args:
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Complete format configuration dictionary.
    """
    config_path = _resolve_config_path('components/format', sync_files)
    return _load_cached_files(config_path, sync_files)

def wrap_text(text: str, layout_style: str, sync_files: bool = False) -> str:
    """Envolver texto automáticamente según configuración del layout.
    
    DIMENSIÓN TRANSPARENCIA: Wrapping explícito con textwrap estándar.
    OBJETIVO: Resolver overflow horizontal insertando \\n donde corresponde.
    
    Args:
        text: Texto a envolver.
        layout_style: Estilo de layout para determinar ancho de wrapping.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Texto con saltos de línea insertados.
        
    Raises:
        ValueError: Si el layout_style no existe en la configuración.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Obtener configuración de wrapping desde format.json
    config = get_format_config(sync_files)
    
    if 'text_wrapping' not in config or 'layout_styles' not in config['text_wrapping']:
        raise ValueError("Text wrapping configuration missing in format.json")
    
    layout_styles = config['text_wrapping']['layout_styles']
    
    if layout_style not in layout_styles:
        raise ValueError(f"Layout style '{layout_style}' not found in text_wrapping configuration")
    
    max_width = layout_styles[layout_style]['max_chars_per_line']
    
    # Si ya tiene saltos de línea, respetarlos y envolver cada línea individualmente
    if '\n' in text:
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            if len(line) <= max_width:
                wrapped_lines.append(line)
            else:
                wrapped_lines.extend(textwrap.wrap(line, width=max_width))
        return '\n'.join(wrapped_lines)
    
    # Si no tiene saltos de línea, envolver normalmente
    if len(text) <= max_width:
        return text
    
    # Usar textwrap para dividir automáticamente
    wrapped_lines = textwrap.wrap(text, width=max_width)
    return '\n'.join(wrapped_lines)

def prepare_dataframe_with_wrapping(df: pd.DataFrame, layout_style: str, sync_files: bool = False) -> pd.DataFrame:
    """Preparar DataFrame con texto envuelto automáticamente.
    
    DIMENSIÓN TRANSPARENCIA: Pre-procesamiento explícito antes de matplotlib.
    OBJETIVO: Envolver todo el texto antes de crear la tabla.
    
    Args:
        df: DataFrame original.
        layout_style: Estilo de layout para determinar ancho de wrapping.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        DataFrame con texto envuelto.
        
    Raises:
        ValueError: Si el layout_style no existe en la configuración.
    """
    # Crear copia para no modificar el original
    df_wrapped = df.copy()
    
    # Envolver todas las celdas (headers y contenido)
    # Primero envolver el contenido de todas las celdas y limpiar NaN
    for col in df_wrapped.columns:
        df_wrapped[col] = df_wrapped[col].apply(lambda x: _clean_nan_values(x, layout_style, sync_files))
    
    # Luego envolver los nombres de las columnas (headers) si es necesario
    column_mapping = {}
    for col in df_wrapped.columns:
        wrapped_col_name = wrap_text(str(col), layout_style, sync_files)
        if wrapped_col_name != str(col):
            column_mapping[col] = wrapped_col_name
    
    # Aplicar el renaming solo si hay columnas que cambiar
    if column_mapping:
        df_wrapped.rename(columns=column_mapping, inplace=True)
    
    return df_wrapped

def format_superscripts(text: str, output_format: str = 'matplotlib', sync_files: bool = False) -> str:
    """Format superscripts using centralized configuration from format.json.
    
    SUBREINO FORMAT: Autoridad suprema sobre formateo transversal de superíndices.
    
    Args:
        text: Input text to process.
        output_format: Target format ('matplotlib', 'html', 'latex', 'unicode', etc.).
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Text with superscripts formatted for the specified output.
        
    Raises:
        ValueError: Si el formato de salida no está soportado.
    """
    config = get_format_config(sync_files)
    
    # Verificar que el formato existe
    if output_format not in config:
        raise ValueError(f"Output format '{output_format}' not supported")
    
    format_config = config[output_format]
    
    if 'superscripts' not in format_config:
        raise ValueError(f"Superscripts configuration missing for format '{output_format}'")
    
    superscript_config = format_config['superscripts']
    
    # Apply direct mapping from format.json
    result_text = text
    for pattern, replacement in superscript_config.items():
        result_text = result_text.replace(pattern, replacement)
    
    return result_text
    
    wrapping_config = config['text_wrapping']['layout_styles']
    
    if layout_style not in wrapping_config:
        raise ValueError(f"Layout style '{layout_style}' not found in text wrapping configuration")
    
    max_width = wrapping_config[layout_style]['max_chars_per_line']
    
    # Si ya tiene saltos de línea, respetarlos y envolver cada línea individualmente
    if '\n' in text:
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            if len(line) <= max_width:
                wrapped_lines.append(line)
            else:
                wrapped_lines.extend(textwrap.wrap(line, width=max_width))
        return '\n'.join(wrapped_lines)
    
    # Si no tiene saltos de línea, envolver normalmente
    if len(text) <= max_width:
        return text
    
    # Usar textwrap para dividir automáticamente
    wrapped_lines = textwrap.wrap(text, width=max_width)
    return '\n'.join(wrapped_lines)

def _clean_nan_values(value, layout_style: str, sync_files: bool = False) -> str:
    """Clean NaN values and apply text wrapping.
    
    Args:
        value: Cell value to process.
        layout_style: Layout style for wrapping.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Cleaned and wrapped text.
    """
    import pandas as pd
    
    # Detectar valores faltantes y reemplazar con "---"
    if pd.isna(value):
        return "---"
    
    value_str = str(value).strip().lower()
    missing_indicators = ['nan', 'none', 'null', '', 'n/a', 'na']
    
    if value_str in missing_indicators:
        return "---"
    
    # Si no es un valor faltante, aplicar wrapping normal
    return wrap_text(str(value), layout_style, sync_files)

def format_superscripts(text: str, output_format: str = 'unicode', sync_files: bool = False) -> str:
    """Format superscripts using centralized configuration from format.json.
    
    Args:
        text: Input text to process.
        output_format: Output format ('unicode', 'html', 'latex', 'markdown', 'image', 'matplotlib', 'plain').
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Text with superscripts formatted according to output format.
        
    Raises:
        ValueError: Si el output_format no existe en la configuración.
    """
    config = get_format_config(sync_files)
    
    if output_format not in config:
        raise ValueError(f"Output format '{output_format}' not found in format configuration")
    
    if 'superscripts' not in config[output_format]:
        # Return text unchanged if no superscripts config for this format
        return str(text)
    
    superscript_config = config[output_format]['superscripts']
    
    # Apply direct mapping from format.json
    for pattern, replacement in superscript_config.items():
        text = text.replace(pattern, replacement)
    
    return text

def get_wrapping_config(layout_style: str, sync_files: bool = False) -> Dict[str, Any]:
    """Get text wrapping configuration for a specific layout style.
    
    Args:
        layout_style: Layout style name.
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Wrapping configuration dictionary for the layout.
        
    Raises:
        ValueError: Si el layout_style no existe en la configuración.
    """
    config = get_format_config(sync_files)
    
    if 'text_wrapping' not in config or 'layout_styles' not in config['text_wrapping']:
        raise ValueError("Text wrapping configuration missing in format.json")
    
    wrapping_config = config['text_wrapping']['layout_styles']
    
    if layout_style not in wrapping_config:
        raise ValueError(f"Layout style '{layout_style}' not found in text wrapping configuration")
    
    return wrapping_config[layout_style]


# UNIVERSAL FONT MANAGEMENT SYSTEM
# ================================
# Tribu Format authority over cross-kingdom font handling

def get_font_fallback_list(font_family_name: str, sync_files: bool = False) -> List[str]:
    """Get complete font fallback list from Text Kingdom configuration.
    
    TRIBU FORMAT: Universal font fallback system for all kingdoms.
    
    Args:
        font_family_name: Name of font family from text.json (e.g., 'handwritten_personal')
        sync_files: Control cache synchronization behavior.
        
    Returns:
        List of font names including primary and fallbacks, properly cleaned.
        
    Raises:
        ValueError: If font family doesn't exist in configuration.
    """
    from ePy_docs.components.text import get_text_config
    
    text_config = get_text_config(sync_files=sync_files)
    if not text_config or 'font_families' not in text_config:
        raise ValueError("Font families configuration missing from text.json")
    
    font_families = text_config['font_families']
    if font_family_name not in font_families:
        raise ValueError(f"Font family '{font_family_name}' not found in text configuration")
    
    font_config = font_families[font_family_name]
    primary_font = font_config['primary']
    fallback_fonts = font_config['fallback'].split(',')
    
    # Create complete font list with fallbacks, cleaned of quotes and whitespace
    font_list = [primary_font.strip('"')] + [f.strip().strip('"') for f in fallback_fonts]
    
    return font_list

def get_layout_font_requirements(layout_name: str, sync_files: bool = False) -> Dict[str, Any]:
    """Analyze layout typography requirements for font rendering engines.
    
    TRIBU FORMAT: Cross-kingdom layout font analysis.
    
    Args:
        layout_name: Layout name from text.json layout_styles
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Dictionary with font requirements analysis:
        - uses_handwritten_everywhere: bool
        - normal_font_family: str  
        - heading_font_families: Dict[str, str]
        - font_fallback_lists: Dict[str, List[str]]
        
    Raises:
        ValueError: If layout doesn't exist in configuration.
    """
    from ePy_docs.components.text import get_text_config
    
    text_config = get_text_config(sync_files=sync_files)
    if not text_config or 'layout_styles' not in text_config:
        raise ValueError("Layout styles configuration missing from text.json")
    
    layout_styles = text_config['layout_styles']
    if layout_name not in layout_styles:
        raise ValueError(f"Layout '{layout_name}' not found in text configuration")
    
    layout_typography = layout_styles[layout_name]['typography']
    
    # Analyze font requirements
    normal_family = layout_typography.get('normal', {}).get('family', 'brand')
    h1_family = layout_typography.get('h1', {}).get('family', 'brand')
    
    # Check if layout uses handwritten fonts for everything
    uses_handwritten_everywhere = (
        normal_family == 'handwritten_personal' and 
        h1_family == 'handwritten_personal'
    )
    
    # Collect all font families used in layout
    font_families_used = set()
    heading_families = {}
    
    for element in ['normal', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'caption']:
        if element in layout_typography:
            family = layout_typography[element].get('family', 'brand')
            font_families_used.add(family)
            if element.startswith('h'):
                heading_families[element] = family
    
    # Generate fallback lists for all used families
    font_fallback_lists = {}
    for family in font_families_used:
        try:
            font_fallback_lists[family] = get_font_fallback_list(family, sync_files)
        except ValueError:
            # If family doesn't exist, use brand as fallback
            font_fallback_lists[family] = get_font_fallback_list('brand', sync_files)
    
    return {
        'uses_handwritten_everywhere': uses_handwritten_everywhere,
        'normal_font_family': normal_family,
        'heading_font_families': heading_families,
        'font_fallback_lists': font_fallback_lists,
        'all_families_used': list(font_families_used)
    }

def generate_latex_font_commands(layout_name: str, sync_files: bool = False) -> List[str]:
    """Generate LaTeX font commands for PDF rendering.
    
    TRIBU FORMAT: Universal LaTeX font generation for PDF Kingdom.
    
    Args:
        layout_name: Layout name from text.json
        sync_files: Control cache synchronization behavior.
        
    Returns:
        List of LaTeX commands for font configuration.
    """
    requirements = get_layout_font_requirements(layout_name, sync_files)
    latex_commands = []
    
    # Add basic packages
    latex_commands.append("\\usepackage{fontspec}")
    
    # Define font families
    for family_name, font_list in requirements['font_fallback_lists'].items():
        primary_font = font_list[0]
        latex_family_name = f"{family_name}font"
        latex_commands.append(f"\\newfontfamily\\{latex_family_name}{{{primary_font}}}[Scale=0.9]")
    
    # If layout uses handwritten everywhere, set as main font
    if requirements['uses_handwritten_everywhere']:
        handwritten_fonts = requirements['font_fallback_lists']['handwritten_personal']
        main_font = handwritten_fonts[0]
        latex_commands.append(f"\\setmainfont{{{main_font}}}[Scale=0.9]")
    
    # Add convenience commands
    latex_commands.append("\\newcommand{\\handwritten}[1]{{\\handwrittenpersonalfont #1}}")
    
    return latex_commands

def generate_css_font_rules(layout_name: str, sync_files: bool = False) -> Dict[str, str]:
    """Generate CSS font rules for HTML rendering.
    
    TRIBU FORMAT: Universal CSS font generation for HTML Kingdom.
    
    Args:
        layout_name: Layout name from text.json
        sync_files: Control cache synchronization behavior.
        
    Returns:
        Dictionary with CSS selectors and font-family rules.
    """
    requirements = get_layout_font_requirements(layout_name, sync_files)
    css_rules = {}
    
    # Generate font-family CSS values
    font_family_css = {}
    for family_name, font_list in requirements['font_fallback_lists'].items():
        # Create CSS font-family value with proper quoting
        css_fonts = []
        for font in font_list:
            if ' ' in font and not (font.startswith('"') and font.endswith('"')):
                css_fonts.append(f'"{font}"')
            else:
                css_fonts.append(font)
        font_family_css[family_name] = ', '.join(css_fonts)
    
    # Apply to HTML elements based on layout typography
    from ePy_docs.components.text import get_text_config
    text_config = get_text_config(sync_files=sync_files)
    layout_typography = text_config['layout_styles'][layout_name]['typography']
    
    for element, config in layout_typography.items():
        family = config.get('family', 'brand')
        if family in font_family_css:
            if element == 'normal':
                css_rules['body, p'] = f"font-family: {font_family_css[family]}"
            elif element.startswith('h'):
                css_rules[element] = f"font-family: {font_family_css[family]}"
            elif element == 'caption':
                css_rules['.caption'] = f"font-family: {font_family_css[family]}"
    
    return css_rules


# UNIVERSAL TEXT WRAPPING SYSTEM
# ===============================
# Tribu Format authority over cross-kingdom text wrapping

def wrap_html_paragraphs(content: str, layout_name: str, sync_files: bool = False) -> str:
    """Universal HTML paragraph wrapping for all kingdoms.
    
    TRIBU FORMAT: Universal HTML paragraph wrapper using layout typography.
    
    Args:
        content: HTML content to wrap in paragraphs
        layout_name: Layout name from text.json
        sync_files: Control cache synchronization behavior.
        
    Returns:
        HTML content with proper paragraph wrapping and styling.
    """
    from ePy_docs.components.text import get_text_config
    
    text_config = get_text_config(sync_files=sync_files)
    if not text_config or 'layout_styles' not in text_config:
        # Fallback to basic wrapping
        return _basic_html_paragraph_wrap(content)
    
    # Get layout typography
    layout_styles = text_config['layout_styles']
    if layout_name not in layout_styles:
        return _basic_html_paragraph_wrap(content)
    
    layout_typography = layout_styles[layout_name]['typography']
    normal_config = layout_typography.get('normal', {})
    
    # Convert size to fontSize if needed
    if 'size' in normal_config and 'fontSize' not in normal_config:
        size_str = normal_config['size']
        font_size = int(size_str.replace('pt', ''))
    else:
        font_size = normal_config.get('fontSize', 12)
    
    line_height = 1.4  # Standard line height
    
    # Process content line by line
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            processed_lines.append('')
            continue
            
        # Skip HTML tags and existing markup
        if (stripped.startswith('<') and stripped.endswith('>')) or stripped.startswith('</'):
            processed_lines.append(line)
            continue
            
        # Skip lines that already contain HTML tags
        if '<' in stripped and '>' in stripped:
            processed_lines.append(f'<p style="font-size: {font_size}px; line-height: {line_height};">{stripped}</p>')
            continue
            
        # Wrap text that doesn't start with HTML tags
        excluded_tags = ['<h1>', '<h2>', '<h3>', '<h4>', '<ul>', '<ol>', '<li>', '<div']
        if stripped and not any(stripped.startswith(tag) for tag in excluded_tags):
            processed_lines.append(f'<p style="font-size: {font_size}px; line-height: {line_height};">{stripped}</p>')
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def _basic_html_paragraph_wrap(content: str) -> str:
    """Basic HTML paragraph wrapping fallback."""
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            processed_lines.append('')
            continue
            
        if (stripped.startswith('<') and stripped.endswith('>')) or stripped.startswith('</'):
            processed_lines.append(line)
            continue
            
        excluded_tags = ['<h1>', '<h2>', '<h3>', '<h4>', '<ul>', '<ol>', '<li>', '<div']
        if stripped and not any(stripped.startswith(tag) for tag in excluded_tags):
            processed_lines.append(f'<p>{stripped}</p>')
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)
