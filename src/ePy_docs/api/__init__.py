"""API module for ePy_docs.

Provides modular API for library initialization and specialized functionality:
- quick_setup: components library initialization  
- units: Unit conversion and management
- report: Report writing and document generation (QUARANTINED - pandas contamination)
- file_management: Clean portal to files world operations
"""

# components initialization
from .quick_setup import quick_setup, setup_library

# Specialized modules
from . import units
from .file_management import read_csv, read_json, read_text, write_csv, write_json, write_text

# components report writer
from .report import ReportWriter

__all__ = [
    'quick_setup', 
    'setup_library',
    'units',
    'ReportWriter',
    'read_csv',
    'read_json', 
    'read_text',
    'write_csv',
    'write_json',
    'write_text'
]
