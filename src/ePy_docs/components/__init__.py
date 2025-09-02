"""Reusable components for reports and presentations.

Provides shared components like tables, math, images, and notes
that can be used across different output formats for document creation.
"""

from .tables import *
# Mathematical processing functions are now annexed to ePy_docs.core.quarto
# from .math import *  # REMOVED - math kingdom annexed to quarto empire
from .images import *
from .notes import *

__all__ = [
    'create_table_image', 'create_split_table_images',
    'MathProcessor',
    'ImageProcessor',
    'NoteRenderer'
]
