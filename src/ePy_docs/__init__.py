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
    load_setup_config,
    get_output_directories,
    _load_cached_config
)

# Styler tools
from ePy_docs.components.colors import (
    get_color, 
    get_report_color, 
    get_custom_colormap, 
    get_category_colors,
    normalize_color_value,
    load_colors,
    TableColorPalette,
    TableColorConfig
)

# Data utilities
from ePy_docs.files.data import _load_cached_json, _safe_get_nested

# Project setup and configuration
from ePy_docs.core.setup import (
    load_setup_config,
    get_output_directories
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
    'TableColorPalette',
    'TableColorConfig',
    '_load_cached_json',
    '_safe_get_nested',
    'create_quarto_yml',
    'create_quarto_project',
    'generate_quarto_config',
    'get_layout_config',
    'get_default_citation_style',
    'PDFRenderer',
    'load_setup_config',
    'get_output_directories',
    '_load_cached_config',
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
    
    os.chdir(base_dir)
    config = load_setup_config()
    return config