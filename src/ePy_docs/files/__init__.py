"""
ePy Files package initialization

This module initializes the ePy Files package, providing file reading and writing utilities.
"""

# Version information
__version__ = "0.1.0"

# Files management - import from actual module structure
from .reader import ReadFiles
from .saver import SaveFiles
from ePy_docs.components.setup import _load_cached_files
from .data import _safe_get_nested

# Define public API - only include what's actually available
__all__ = [
    'ReadFiles',
    'SaveFiles',
    '_load_cached_files',
    '_safe_get_nested'
]
