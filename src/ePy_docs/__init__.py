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

# File management API (clean portal to files world)
from ePy_docs.api.file_management import (
    read_csv, read_json, read_text,
    write_csv, write_json, write_text
)

# Import WriteFiles before ReportWriter to avoid circular imports
from ePy_docs.api.report import ReportWriter

# Import clean setup functions
# (No longer importing _load_cached_files from components.setup - now using files version)

# Styler tools
from ePy_docs.components.colors import (
    get_colors_config
)

# Data utilities
from ePy_docs.files.data import _safe_get_nested
from ePy_docs.files import _load_cached_files



# Quarto book generation - QUARANTINED due to legacy color imports
# from ePy_docs.components.styler import (
#     create_quarto_yml,
#     create_quarto_project,
#     generate_quarto_config,
#     get_layout_config,
#     get_default_citation_style,
#     PDFRenderer
# )

__all__ = [
    'ReadFiles',
    'ReportWriter',
    # File management API (clean portal)
    'read_csv', 'read_json', 'read_text',
    'write_csv', 'write_json', 'write_text',
    'files',  # Convenient namespace for file operations
    # Core functions
    '_load_cached_files',
    '_safe_get_nested',
    # QUARANTINED - styler functions with legacy dependencies
    # 'create_quarto_yml',
    # 'create_quarto_project', 
    # 'generate_quarto_config',
    # 'get_layout_config',
    # 'get_default_citation_style',
    # 'PDFRenderer',
    # Using centralized configuration system
    # 'get_output_directories',  # Temporarily disabled
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
    from ePy_docs.files import _load_cached_files
    from ePy_docs.components.setup import _resolve_config_path
    config_path = _resolve_config_path('core/setup', sync_files=False)
    config = _load_cached_files(config_path, sync_files=False)  #  PURIFICACIÓN ABSOLUTA
    return config

# Create a convenient 'files' namespace for file operations
class FilesNamespace:
    """Convenient namespace for file operations to maintain backward compatibility."""
    
    @staticmethod
    def write_csv(data, filepath, **kwargs):
        """Write CSV file using the file management API."""
        return write_csv(data, filepath, **kwargs)
    
    @staticmethod 
    def write_json(data, filepath, **kwargs):
        """Write JSON file using the file management API."""
        return write_json(data, filepath, **kwargs)
        
    @staticmethod
    def write_text(content, filepath, **kwargs):
        """Write text file using the file management API."""
        return write_text(content, filepath, **kwargs)
    
    @staticmethod
    def read_csv(filepath, **kwargs):
        """Read CSV file using the file management API."""
        return read_csv(filepath, **kwargs)
        
    @staticmethod
    def read_json(filepath, **kwargs):
        """Read JSON file using the file management API.""" 
        return read_json(filepath, **kwargs)
        
    @staticmethod
    def read_text(filepath, **kwargs):
        """Read text file using the file management API."""
        return read_text(filepath, **kwargs)

# Create the files instance
files = FilesNamespace()
