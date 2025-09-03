"""API module for ePy_docs.

Provides modular API for library initialization and specialized functionality:
- quick_setup: components library initialization  
- units: Unit conversion and management
- report: Report writing and document generation
- file_management: Simple file reading/writing operations
"""

# components initialization
from .quick_setup import quick_setup, setup_library

# Specialized modules
from . import units
from .file_management import FileManager, read_csv, read_json, read_text, write_csv, write_json, write_text

# components report writer
from .report import ReportWriter

__all__ = [
    'quick_setup', 
    'setup_library',
    'units',
    'reports', 
    'ReportWriter',
    'FileManager',
    'read_csv',
    'read_json', 
    'read_text',
    'write_csv',
    'write_json',
    'write_text'
]
