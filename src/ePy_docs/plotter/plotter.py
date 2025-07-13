"""Base plotting functionality for ePy_plotter visualization system.

Provides core plotting capabilities with consistent styling and color management.
"""

import os
from typing import Dict, Any, Optional, Tuple

import matplotlib.pyplot as plt


class PlotterBase:
    """Base class for all plotting classes with shared functionality."""

    def __init__(self, figsize: Tuple[int, int] = (10, 6), style: str = 'default'):
        """Initialize the plotting base class."""
        self.figsize = figsize
        plt.style.use(style)
        self.colors = self._load_colors()

    def _load_colors(self) -> Dict[str, Any]:
        """Load basic color configuration."""
        # Basic color palette for engineering plots
        return {
            'visualization': {
                'elements': {'default': '#cccccc'},
                'nodes': {'default': '#4472C4'},
                'axis': {'grid': '#cccccc'},
                'annotation': {'background': '#ffffff'}
            },
            'brand': {'blue': '#0066cc'},
            'engineering': {
                'concrete': '#c0c0c0',
                'steel': '#4472C4',
                'foundation': '#8B4513'
            }
        }

    def _get_color(self, path: str, default: str = '#333333') -> str:
        """Get color value from configuration using dot notation path."""
        try:
            keys = path.split('.')
            value = self.colors
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def save_matplotlib_figure(self, fig: plt.Figure, filename: str, 
                   format: str = 'png', dpi: int = 300, 
                   bbox_inches: str = 'tight', 
                   directory: Optional[str] = None,
                   create_dir: bool = True) -> str:
        """Save a matplotlib figure to file."""
        if directory is None:
            directory = os.getcwd()
        
        if create_dir and not os.path.exists(directory):
            os.makedirs(directory)
        
        filepath = os.path.join(directory, f"{filename}.{format}")
        fig.savefig(filepath, format=format, dpi=dpi, bbox_inches=bbox_inches)
        return filepath


# Standalone color functions for compatibility
def load_colors() -> Dict[str, Any]:
    """Load basic color configuration."""
    return PlotterBase()._load_colors()


def get_color(path: str, default: str = '#333333', format_type: str = "hex") -> str:
    """Get color value from configuration using dot notation path."""
    return PlotterBase()._get_color(path, default)
