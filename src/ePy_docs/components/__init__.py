"""Reusable components for reports and presentations.

Pure kingdoms established: COLORS, TEXT, IMAGES, TABLES, NOTES
Provides shared components following the kingdom sovereignty pattern.
"""

# PURE KINGDOMS - Safe to import
from .images import get_images_config
from .colors import get_colors_config  
from .text import get_text_config
from .notes import get_notes_config, NoteRenderer
from .tables import get_tables_config
from .base import WriteFiles, load_colors
from .setup import _load_cached_files

__all__ = [
    'get_images_config',
    'get_colors_config', 
    'get_text_config',
    'get_notes_config',
    'get_tables_config',
    'NoteRenderer',
    'WriteFiles',
    'load_colors',
    '_load_cached_files'
]
