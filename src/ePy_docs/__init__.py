"""
ePy Suite package initialization

This module initializes the ePy Suite package, ensuring all submodules
are properly imported and available to users.
"""

# Version information
__version__ = "0.1.0"

# Files management
from ePy_files.utils.reader import ReadFiles

# Import WriteFiles before WriteReportMD to avoid circular imports
from ePy_files.core.base import WriteFiles
from ePy_files.reports.formatter import ReportFormatter as WriteReportMD
from ePy_files.presentations.formatter import PresentationFormatter

from ePy_suite.project.setup import DirectoryManager

# Plotting tools
from ePy_plotter.plotter import PlotterBase
from ePy_plotter.for_construction import EngineeringPlots

# Styler tools
from ePy_files.styler.colors import get_color, load_colors, get_custom_colormap, get_report_color

# Data utilities
from ePy_suite.utils.data import _load_cached_json, _safe_get_nested

# Analysis tools
from ePy_suite.analysis.robot.nodes import RobotNodes, RobotSupports

# Reinforcement design
from ePy_suite.analysis.structure.rebar import RebarSelector, RebarCalculator

# Define public API - only using class-based APIs
__all__ = [
    'ReadFiles',
    'WriteFiles', 
    'WriteReportMD',
    'PresentationFormatter',
    'DirectoryManager',
    'PlotterBase',
    'EngineeringPlots',
    'get_color',
    'load_colors', 
    'get_custom_colormap',
    'get_report_color',
    'RobotNodes',
    'RobotSupports',
    'RebarSelector',
    'RebarCalculator',
]