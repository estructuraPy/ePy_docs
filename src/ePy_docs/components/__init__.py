"""Reusable components for reports and presentations.

Provides shared components like tables, math/equations, images, notes, and formatting
that can be used across different output formats for document creation.
"""

from .tables import *
from .math import *
from .images import *
from .notes import *

__all__ = [
    'create_table_image', 'create_split_table_images',
    'EquationRenderer',
    'ImageProcessor', 
    'NoteRenderer',
    'MathProcessor',
    'format_superscript',
    'format_subscript', 
    'format_equation',
    'format_math_text',
    'get_mathematical_symbol',
    'get_special_character'
]
