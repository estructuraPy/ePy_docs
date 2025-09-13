"""ePy_docs universe initialization.

Constitutional portal providing clean access to all realms without legacy contamination.
"""

__version__ = "0.1.0"

# Constitutional configuration portal
from ePy_docs.components.configurator import (
    initialize_report_config, 
    initialize_paper_config,
    get_units_config,
    get_project_config
)

# FILES world authorized services
from ePy_docs.files.reader import ReadFiles

# Official API portals
from ePy_docs.api.file_manager import (
    read_csv, read_json, read_text,
    write_csv, write_json, write_text
)
from ePy_docs.api.report import ReportWriter
from ePy_docs.api.paper import PaperWriter

# Authorized commercial offices to realms (only existing ones)
from ePy_docs.components.colors import get_colors_config
from ePy_docs.components.text import get_text_config
from ePy_docs.components.tables import get_tables_config
from ePy_docs.components.pages import get_pages_config
from ePy_docs.components.project_info import get_project_config_data
from ePy_docs.components.setup import get_setup_config

# FILES world infrastructure
from ePy_docs.files.data import _load_cached_files, _safe_get_nested

__all__ = [
    # Constitutional configuration
    'initialize_report_config',
    'initialize_paper_config', 
    'get_units_config',
    'get_project_config',
    
    # Official APIs
    'ReadFiles',
    'ReportWriter',
    'PaperWriter',
    
    # File management portal
    'read_csv', 'read_json', 'read_text',
    'write_csv', 'write_json', 'write_text',
    
    # Commercial offices to realms (existing only)
    'get_colors_config',
    'get_text_config', 
    'get_tables_config',
    'get_pages_config',
    'get_project_config_data',
    'get_setup_config',
    
    # FILES world infrastructure
    '_load_cached_files',
    '_safe_get_nested'
]
