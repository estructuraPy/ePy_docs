"""Format configuration and utilities.

Format processing with centralized configuration through _load_cached_files.
Tribu Format - exists at the boundary of multiple kingdoms.
Handles unicode, superscripts, text wrapping, and cross-kingdom formatting standards.
"""
import textwrap
import pandas as pd
from typing import Dict, Any, Union
from ePy_docs.files import _load_cached_files
from ePy_docs.components.setup import _resolve_config_path

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
