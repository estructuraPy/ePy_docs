"""
REINO TEXT - Soberanía Absoluta de Tipografía

Dimensión Setup: Caché centralizado por medio de _load_cached_files
Dimensión Apariencia: Organización por layout_styles
Dimensión Transparencia: Sin backward compatibility, sin fallbacks
"""

from typing import Dict, Any
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def _get_text_config(sync_files: bool = False) -> Dict[str, Any]:
    """Sucursal de la secretaría de comercio para recursos de texto.
    
    Args:
        sync_files: Control de sincronización de archivos
        
    Returns:
        Configuración completa de texto
        
    Raises:
        RuntimeError: Si la carga falla
        
    Assumptions:
        El archivo text.json existe en la ubicación resuelta
    """
    try:
        config_path = _resolve_config_path('components/text', sync_files)
        config = _load_cached_files(config_path, sync_files)
        
        required_keys = ['font_families', 'layout_styles']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load text configuration: {e}") from e

def get_text_config(sync_files: bool = False) -> Dict[str, Any]:
    """Única función pública para acceso a recursos de texto.
    
    Comercio oficial del Reino TEXT.
    
    Args:
        sync_files: Control de sincronización de archivos
        
    Returns:
        Configuración completa de texto
        
    Raises:
        RuntimeError: Si la carga falla
        
    Assumptions:
        El sistema de layout_styles está correctamente configurado
        Brand siempre va con corporate
    """
    return _get_text_config(sync_files)
