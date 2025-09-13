"""API portal for ePy_docs universe.

Constitutional API providing clean access without legacy contamination.
"""

# Constitutional configuration
from ..components.configurator import (
    initialize_report_config,
    initialize_paper_config,
    get_units_config, 
    get_project_config
)

# Specialized modules
from . import units_converter
from .file_manager import read_csv, read_json, read_text, write_csv, write_json, write_text

# Document generators
from .report import ReportWriter
from .paper import PaperWriter

__all__ = [
    # Constitutional configuration
    'initialize_report_config',
    'initialize_paper_config', 
    'get_units_config',
    'get_project_config',
    
    # Specialized modules
    'units_converter',
    
    # File operations portal
    'read_csv', 'read_json', 'read_text',
    'write_csv', 'write_json', 'write_text',
    
    # Document generators
    'ReportWriter',
    'PaperWriter'
]
