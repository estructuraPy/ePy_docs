"""Enhanced plotter for reports with advanced formatting and Quarto integration.

Provides report-specific plotting capabilities with professional styling,
automatic figure numbering, and integration with report generation workflows.
"""

import os
from typing import Dict, Any, Optional, Tuple

import matplotlib.pyplot as plt
from .plotter import PlotterBase


class ReportPlotter(PlotterBase):
    """Enhanced plotter specifically designed for report generation."""
    
    def __init__(self, output_dir: str, figsize: Tuple[int, int] = (10, 6), 
                 style: str = 'default', dpi: int = 300):
        super().__init__(figsize, style)
        self.output_dir = output_dir
        self.dpi = dpi
        self.figure_counter = 0
    
    def add_plot_to_report(self, fig: plt.Figure, title: str = None, 
                          caption: str = None, filename: str = None,
                          label: str = None) -> str:
        """Add plot to report with automatic formatting and labeling.
        
        Args:
            fig: Matplotlib figure to add
            title: Optional title for the plot
            caption: Caption for the figure
            filename: Custom filename (if None, auto-generated)
            label: Custom label for cross-referencing
            
        Returns:
            Path to the saved figure
        """
        self.figure_counter += 1
        
        # Generate filename if not provided
        if filename is None:
            filename = f"figure_{self.figure_counter}.png"
        
        # Ensure proper extension
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            filename += '.png'
        
        # Create figures directory
        figures_dir = os.path.join(self.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        # Save figure
        img_path = os.path.join(figures_dir, filename)
        
        # Add title to figure if provided
        if title:
            fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        
        # Save with high quality
        img_path = self.save_matplotlib_figure(
            fig, filename, format='png', dpi=self.dpi,
            directory=figures_dir, create_dir=False
        )
        
        return img_path
    
    def create_report_ready_plot(self, data, plot_type: str = "line", 
                                title: str = None, xlabel: str = None, 
                                ylabel: str = None, **kwargs) -> plt.Figure:
        """Create a plot optimized for report inclusion.
        
        Args:
            data: Data to plot
            plot_type: Type of plot ('line', 'bar', 'scatter', etc.)
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            **kwargs: Additional plotting arguments
            
        Returns:
            Matplotlib figure ready for report inclusion
        """
        # Create figure with report-appropriate size
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Apply report styling
        self._apply_report_styling(ax)
        
        # Create plot based on type
        if plot_type == "line":
            ax.plot(data, **kwargs)
        elif plot_type == "bar":
            ax.bar(range(len(data)), data, **kwargs)
        elif plot_type == "scatter":
            if isinstance(data, tuple) and len(data) == 2:
                ax.scatter(data[0], data[1], **kwargs)
            else:
                ax.scatter(range(len(data)), data, **kwargs)
        
        # Set labels
        if title:
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10)
        
        # Improve layout
        fig.tight_layout()
        
        return fig
    
    def _apply_report_styling(self, ax):
        """Apply consistent styling for report plots."""
        # Set colors from theme
        primary_color = self._get_color("plot.primary", "#2E86AB")
        grid_color = self._get_color("plot.grid", "#E5E7EB")
        
        # Style the axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(grid_color)
        ax.spines['bottom'].set_color(grid_color)
        
        # Style the grid
        ax.grid(True, linestyle='-', alpha=0.3, color=grid_color)
        ax.set_axisbelow(True)
        
        # Style ticks
        ax.tick_params(colors='#374151', which='both')
        
        # Set default line color
        ax.set_prop_cycle(color=[primary_color, '#A23B72', '#059669', '#DC2626'])
    
    def create_comparison_plot(self, datasets: Dict[str, Any], 
                             title: str = "Comparison", **kwargs) -> plt.Figure:
        """Create a comparison plot for multiple datasets.
        
        Args:
            datasets: Dictionary with dataset names as keys and data as values
            title: Plot title
            **kwargs: Additional plotting arguments
            
        Returns:
            Comparison plot figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        self._apply_report_styling(ax)
        
        # Plot each dataset
        for i, (label, data) in enumerate(datasets.items()):
            ax.plot(data, label=label, linewidth=2, **kwargs)
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        ax.legend(frameon=False, loc='best')
        
        fig.tight_layout()
        return fig
    
    def create_distribution_plot(self, data, bins: int = 30, 
                               title: str = "Distribution", **kwargs) -> plt.Figure:
        """Create a distribution/histogram plot.
        
        Args:
            data: Data for histogram
            bins: Number of bins
            title: Plot title
            **kwargs: Additional plotting arguments
            
        Returns:
            Distribution plot figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        self._apply_report_styling(ax)
        
        # Create histogram
        n, bins, patches = ax.hist(data, bins=bins, alpha=0.7, 
                                  color=self._get_color("plot.primary", "#2E86AB"),
                                  **kwargs)
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        ax.set_xlabel('Value', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        
        fig.tight_layout()
        return fig
