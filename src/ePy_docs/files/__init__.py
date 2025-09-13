"""
ePy Files World - Core file handling universe

This world contains the fundamental laws for file operations:
- data: Data manipulation and transformation
- importer: File import operations  
- reader: File reading operations
- saver: File saving operations with pure functions

TRANSPARENCY DIMENSION: Pure functions only, no class contamination.
"""

# Version information
__version__ = "0.1.0"

# Core files world components
from .reader import (
    load_csv_file, load_json_file, load_text_file, load_project_config,
    load_all_project_configs, find_csv_file, list_csv_files,
    clean_dataframe_bom, detect_csv_separator, detect_csv_header_row,
    ReadFiles  # ReadFiles for legacy compatibility only
)
from .saver import (
    ensure_directory, save_json, save_csv, save_txt, 
    save_excel, save_matplotlib_figure, SaveFiles  # SaveFiles for legacy compatibility only
)
from .data import (
    _safe_get_nested, _load_cached_files, safe_parse_numeric,
    hide_dataframe_columns, process_numeric_columns, convert_dataframe_to_table_with_units,
    sort_dataframe_rows, split_large_table
)
from .importer import process_quarto_file, process_markdown_file

# Public API of the files world - PURE FUNCTIONS PREFERRED
__all__ = [
    # Pure reading functions (PREFERRED)
    'load_csv_file',
    'load_json_file', 
    'load_text_file',
    'load_project_config',
    'load_all_project_configs',
    'find_csv_file',
    'list_csv_files',
    'clean_dataframe_bom',
    'detect_csv_separator',
    'detect_csv_header_row',
    # Legacy reading class (DEPRECATED)
    'ReadFiles',
    # Pure saving functions (PREFERRED)
    'ensure_directory',
    'save_json',
    'save_csv', 
    'save_txt',
    'save_excel',
    'save_matplotlib_figure',
    # Legacy saving class (DEPRECATED)
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
