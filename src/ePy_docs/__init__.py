"""
ePy Suite package initialization

This module initializes the ePy Suite package, ensuring all submodules
are properly imported and available to users.
"""

# Version information
__version__ = "0.1.0"

# Files management
from ePy_docs.files.reader import ReadFiles

# Import WriteFiles before WriteReportMD to avoid circular imports
from ePy_docs.core.base import WriteFiles
from ePy_docs.reports.formatter import ReportFormatter as WriteReportMD
from ePy_docs.presentations.formatter import PresentationFormatter

from ePy_docs.project.setup import DirectoryManager

# Plotting tools
from ePy_docs.plotter import PlotterBase
from ePy_docs.plotter.for_construction import EngineeringPlots

# Styler tools
from ePy_docs.styler.colors import (
    get_color, 
    get_report_color, 
    get_custom_colormap, 
    get_category_colors,
    normalize_color_value,
    load_colors,
    TableColorPalette,
    TableColorConfig
)

# Data utilities
from ePy_docs.files.data import _load_cached_json, _safe_get_nested
from ePy_analysis.robot.nodes import RobotNodes, RobotSupports
from ePy_analysis.structure.rebar import RebarSelector, RebarCalculator

__all__ = [
    'ReadFiles',
    'WriteFiles', 
    'WriteReportMD',
    'PresentationFormatter',
    'DirectoryManager',
    'PlotterBase',
    'EngineeringPlots',
    'get_color',
    'get_report_color',
    'get_custom_colormap',
    'get_category_colors',
    'normalize_color_value',
    'load_colors',
    'TableColorPalette',
    'TableColorConfig',
    '_load_cached_json',
    '_safe_get_nested',
    'RobotNodes',
    'RobotSupports',
    'RebarSelector',
    'RebarCalculator',
]