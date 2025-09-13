"""Reusable components for reports and presentations.

Pure kingdoms established: COLORS, TEXT, IMAGES, TABLES, NOTES
Provides shared components following the kingdom sovereignty pattern.
"""

# PURE KINGDOMS - Safe to import
from .images import get_images_config
from .colors import get_colors_config, load_colors
from .text import get_text_config
from .notes import get_notes_config, NoteRenderer
from .tables import get_tables_config
from ePy_docs.files import _load_cached_files

__all__ = [
    'get_images_config',
    'get_colors_config', 
    'load_colors',
    'get_text_config',
    'get_notes_config',
    'get_tables_config',
    'NoteRenderer',
    '_load_cached_files'
]
