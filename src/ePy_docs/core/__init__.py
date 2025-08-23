"""Core functionality for file writing and content management.

Provides base classes and utilities shared across all file writing modules.
"""

from .base import WriteFiles, load_colors
from .setup import _load_cached_config

__all__ = ['WriteFiles', 'load_colors', '_load_cached_config']
