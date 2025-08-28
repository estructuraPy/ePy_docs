"""Core functionality for file writing and content management.

Provides base classes and utilities shared across all file writing modules.
"""

from .base import WriteFiles, load_colors
from .setup import _load_cached_config, load_setup_config
from .generator import generate_documents
from .layouts import get_current_layout, set_current_layout

__all__ = [
    'WriteFiles', 
    'load_colors', 
    '_load_cached_config',
    'load_setup_config',
    'generate_documents',
    'get_current_layout',
    'set_current_layout'
]
