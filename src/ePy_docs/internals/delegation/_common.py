"""
Common Imports for Delegation Modules
=====================================

This module centralizes all shared imports used across delegation modules.
Import this module to access commonly used utilities, validators, and helpers.
"""

# Validators
from ePy_docs.utils.validators import (
    validate_dataframe,
    validate_string,
    validate_list,
    validate_image_path,
    validate_image_width,
    validate_callout_type,
    validate_reference_key,
    validate_format
)

# Helpers
from ePy_docs.utils.markdown_parser import (
    extract_markdown_tables,
    remove_tables_from_content
)

from ePy_docs.utils.logging_config import get_logger

# Config utilities
from ePy_docs.config.setup import (
    get_absolute_output_directories,
    _resolve_config_path
)

# Data processing utilities
from ePy_docs.internals.data_processing._data_utils import (
    process_file,
    process_markdown_file,
    process_quarto_file
)

from ePy_docs.internals.data_processing._data import (
    load_cached_files
)

# Standard library imports commonly used
import os
import tempfile
from typing import Dict, List, Tuple, Any, Callable, Optional