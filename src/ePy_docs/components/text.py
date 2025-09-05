"""
REINO TEXT - Soberanía Absoluta de Tipografía

Dimensión Setup: Caché centralizado por medio de _load_cached_files
Dimensión Apariencia: Organización por layout_styles
Dimensión Transparencia: Sin backward compatibility, sin fallbacks
"""

from typing import Dict, Any
from ePy_docs.components.setup import _load_cached_files, _resolve_config_path

def get_text_config(sync_files: bool = False) -> Dict[str, Any]:
    """Comercio oficial del Reino TEXT."""
    config_path = _resolve_config_path('components/text', sync_files)
    return _load_cached_files(config_path, sync_files)
