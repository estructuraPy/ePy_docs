"""
ePy Suite package initialization

This module initializes the ePy Suite package, ensuring all submodules
are properly imported and available to users.
"""

# Version information
__version__ = "0.1.0"

# Quick initialization (recommended for notebooks)
from ePy_docs.api.quick_setup import quick_setup, setup_library

# Files management
from ePy_docs.files.reader import ReadFiles

# Import WriteFiles before ReportWriter to avoid circular imports
from ePy_docs.api.report import ReportWriter

# Import clean setup functions
from ePy_docs.core.setup import (
    # get_output_directories,  # Temporarily disabled
    _load_cached_files
    # Using centralized configuration system _load_cached_files
)

# Styler tools
from ePy_docs.components.colors import (
    get_color, 
    get_report_color, 
    get_custom_colormap, 
    get_category_colors,
    normalize_color_value,
    load_colors,
    TableColorConfig
)

# Data utilities
from ePy_docs.files.data import _safe_get_nested
from ePy_docs.core.setup import _load_cached_files

# Project setup and configuration
from ePy_docs.core.setup import (
    # get_output_directories  # Temporarily disabled
    # Using centralized configuration system _load_cached_files
    _load_cached_files
)

# Quarto book generation
from ePy_docs.core.styler import (
    create_quarto_yml,
    create_quarto_project,
    generate_quarto_config,
    get_layout_config,
    get_default_citation_style,
    PDFRenderer
)

__all__ = [
    'ReadFiles',
    'ReportWriter',
    'get_color',
    'get_report_color',
    'get_custom_colormap',
    'get_category_colors',
    'normalize_color_value',
    'load_colors',
    'TableColorConfig',
    '_load_cached_files',
    '_safe_get_nested',
    'create_quarto_yml',
    'create_quarto_project',
    'generate_quarto_config',
    'get_layout_config',
    'get_default_citation_style',
    'PDFRenderer',
    # Using centralized configuration system
    # 'get_output_directories',  # Temporarily disabled
    '_load_cached_files',
    'setup_project',
]

def setup_project(base_dir=None, sync_json=True):
    """
    Simplified project setup function using setup.json configuration.
    
    This function handles all the necessary initialization for your ePy_docs project:
    - Loads configuration from setup.json
    - Sets up output directories based on configuration
    
    Args:
        base_dir: Base directory path (default: current working directory)
        sync_json: Ignored parameter for backward compatibility
    
    Returns:
        dict: Configuration dictionary from setup.json
    
    Example:
        >>> import ePy_docs as epy
        >>> config = epy.setup_project()
        >>> output_dirs = epy.get_output_directories(config)
    """
    import os
    if base_dir is None:
        base_dir = os.getcwd()
    
    #  System: NO cambiar directorio de trabajo
    # os.chdir(base_dir)  #  REBELDE ELIMINADO
    
    # # Using centralized configuration _load_cached_files
    from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
    config_path = _resolve_config_path('core/setup', sync_files=False)
    config = _load_cached_files(config_path, sync_files=False)  #  PURIFICACIÓN ABSOLUTA
    return config
