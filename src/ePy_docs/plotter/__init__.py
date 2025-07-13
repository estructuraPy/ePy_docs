"""
ePy Plotter package initialization

This module initializes the ePy Plotter package, providing specialized
plotting utilities for engineering visualization and data analysis.
"""

# Version information
__version__ = "0.1.0"

# Core plotting tools
from .plotter import PlotterBase
from .for_construction import EngineeringPlots
from .for_data import GeneralPlots
from .for_geotech import GeoPlotter
from .for_presentations import PresentationPlotter
from .for_reports import ReportPlotter
from .for_structural import StructuralPlotter, ForceMomentPlotter

# Define public API - plotting classes only
__all__ = [
    'PlotterBase',
    'EngineeringPlots',
    'GeneralPlots',
    'GeoPlotter',
    'PresentationPlotter',
    'ReportPlotter',
    'StructuralPlotter',
    'ForceMomentPlotter',
]