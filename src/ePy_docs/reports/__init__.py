"""Report generation module for ePy_suite.

Provides specialized functionality for creating technical and academic reports
with advanced formatting, tables, figures, and professional layouts.
"""

from .formatter import ReportFormatter
from .covers import add_project_cover, add_responsability_page
from .layouts import ReportLayout

__all__ = ['ReportFormatter', 'add_project_cover', 'add_responsibility_cover', 'ReportLayout']
