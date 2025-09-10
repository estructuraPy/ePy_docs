"""
ePy Files World - Core file handling universe

This world contains the fundamental laws for file operations:
- data: Data manipulation and transformation
- importer: File import operations  
- reader: File reading operations
- saver: File saving operations
"""

# Version information
__version__ = "0.1.0"

# Core files world components
from .reader import ReadFiles
from .saver import SaveFiles
from .data import (
    _safe_get_nested, _load_cached_files, safe_parse_numeric,
    hide_dataframe_columns, process_numeric_columns, convert_dataframe_to_table_with_units,
    sort_dataframe_rows, split_large_table
)
from .importer import process_quarto_file, process_markdown_file

# Public API of the files world
__all__ = [
    # Core classes
    'ReadFiles',
    'SaveFiles',
    # Data utilities
    '_safe_get_nested',
    '_load_cached_files',
    'safe_parse_numeric', 
    'hide_dataframe_columns',
    'process_numeric_columns',
    'convert_dataframe_to_table_with_units',
    'sort_dataframe_rows',
    'split_large_table',
    # Import utilities
    'process_quarto_file',
    'process_markdown_file'
]
