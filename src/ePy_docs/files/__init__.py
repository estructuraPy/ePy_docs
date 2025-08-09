"""
ePy Files package initialization

This module initializes the ePy Files package, providing file reading and writing utilities.
"""

# Version information
__version__ = "0.1.0"

# Files management - import from actual module structure
from ePy_docs.files.reader import ReadFiles
from ePy_docs.files.saver import SaveFiles
from ePy_docs.core.mapper import DataFrameColumnMapper

# Data utilities - import from actual module structure  
from ePy_docs.files.data import _load_cached_json, _safe_get_nested

# Define public API - only include what's actually available
__all__ = [
    'ReadFiles',
    'SaveFiles',
    '_load_cached_json',
    '_safe_get_nested',
    'DataFrameColumnMapper'
]