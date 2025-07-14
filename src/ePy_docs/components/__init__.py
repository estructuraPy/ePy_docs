"""Reusable components for reports and presentations.

Provides shared components like tables, equations, images, and notes
that can be used across different output formats.
"""

from .tables import *
from .equations import *
from .images import *
from .notes import *

__all__ = [
    # Tables
    'create_table_image', 'create_split_table_images',
    # Equations  
    'EquationRenderer',
    # Images
    'ImageProcessor',
    # Notes
    'NoteRenderer'
]
