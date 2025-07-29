"""
ePy Suite package initialization

This module initializes the ePy Suite package, ensuring all submodules
are properly imported and available to users.
"""

# Version information
__version__ = "0.1.0"

# Files management
from ePy_docs.files.reader import ReadFiles

# Import WriteFiles before ReportWriter to avoid circular imports
# from ePy_docs.core.base import WriteFiles
from ePy_docs.reports.reporter import ReportWriter

from ePy_docs.project.setup import DirectoryManager

# Styler tools
from ePy_docs.styler.colors import (
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

__all__ = [
    'ReadFiles',
    'WriteFiles', 
    'ReportWriter',
    'DirectoryManager',
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

]