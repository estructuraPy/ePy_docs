"""Enhanced plotter for presentations with slide-optimized formatting.

Provides presentation-specific plotting capabilities with high contrast,
large fonts, and layouts optimized for projection and slide formats.
"""

import os
from typing import Dict, Any, Optional, Tuple, List

import matplotlib.pyplot as plt
from .plotter import PlotterBase


class PresentationPlotter(PlotterBase):
    """Enhanced plotter specifically designed for presentation slides."""
    
    def __init__(self, output_dir: str, figsize: Tuple[int, int] = (12, 8), 
                 style: str = 'default', dpi: int = 150):
        super().__init__(figsize, style)
        self.output_dir = output_dir
        self.dpi = dpi  # Lower DPI for presentations
        self.figure_counter = 0
        
        # Presentation-specific styling
        plt.rcParams.update({
            'font.size': 16,           # Larger base font size
            'axes.titlesize': 20,      # Larger title
            'axes.labelsize': 18,      # Larger axis labels
            'xtick.labelsize': 14,     # Larger tick labels
            'ytick.labelsize': 14,
            'legend.fontsize': 16,     # Larger legend
            'figure.titlesize': 24     # Larger figure title
        })
    
    def add_plot_to_slide(self, fig: plt.Figure, title: str = None, 
                         filename: str = None) -> str:
        """Add plot to presentation slide with optimal formatting.
        
        Args:
            fig: Matplotlib figure to add
            title: Optional title for the plot
            filename: Custom filename (if None, auto-generated)
            
        Returns:
            Path to the saved figure
        """
        self.figure_counter += 1
        
        # Generate filename if not provided
        if filename is None:
            filename = f"slide_figure_{self.figure_counter:03d}.png"
        
        # Ensure proper extension
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename += '.png'
        
        # Create figures directory
        figures_dir = os.path.join(self.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        # Apply presentation styling
        self._apply_presentation_styling(fig)
        
        # Add title if provided
        if title:
            fig.suptitle(title, fontsize=24, fontweight='bold', y=0.95)
        
        # Save with presentation-optimized settings
        img_path = self.save_matplotlib_figure(
            fig, filename, format='png', dpi=self.dpi,
            directory=figures_dir, create_dir=False
        )
        
        return img_path
    
    def create_slide_ready_plot(self, data, plot_type: str = "line", 
                               title: str = None, xlabel: str = None, 
                               ylabel: str = None, high_contrast: bool = True,
                               **kwargs) -> plt.Figure:
        """Create a plot optimized for slide presentation.
        
        Args:
            data: Data to plot
            plot_type: Type of plot ('line', 'bar', 'scatter', etc.)
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            high_contrast: Use high contrast colors for better visibility
            **kwargs: Additional plotting arguments
            
        Returns:
            Matplotlib figure ready for slide inclusion
        """
        # Create figure with presentation-appropriate size
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Apply presentation styling
        self._apply_slide_styling(ax, high_contrast)
        
        # Create plot based on type
        if plot_type == "line":
            line_width = kwargs.pop('linewidth', 3)  # Thicker lines for presentations
            ax.plot(data, linewidth=line_width, **kwargs)
        elif plot_type == "bar":
            ax.bar(range(len(data)), data, **kwargs)
        elif plot_type == "scatter":
            marker_size = kwargs.pop('s', 100)  # Larger markers for presentations
            if isinstance(data, tuple) and len(data) == 2:
                ax.scatter(data[0], data[1], s=marker_size, **kwargs)
            else:
                ax.scatter(range(len(data)), data, s=marker_size, **kwargs)
        
        # Set labels with larger fonts
        if title:
            ax.set_title(title, fontsize=20, fontweight='bold', pad=30)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=18, fontweight='bold')
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=18, fontweight='bold')
        
        # Improve layout for presentations
        fig.tight_layout(pad=2.0)
        
        return fig
    
    def _apply_presentation_styling(self, fig):
        """Apply presentation-specific styling to the entire figure."""
        # Set figure background to white for better contrast
        fig.patch.set_facecolor('white')
        
        # Ensure all text is bold and large enough
        for ax in fig.get_axes():
            self._apply_slide_styling(ax, high_contrast=True)
    
    def _apply_slide_styling(self, ax, high_contrast: bool = True):
        """Apply consistent styling for presentation slides."""
        if high_contrast:
            # High contrast colors for better visibility
            primary_color = "#1E3A8A"  # Dark blue
            secondary_color = "#DC2626"  # Red
            grid_color = "#6B7280"  # Gray
            text_color = "#000000"  # Black
        else:
            # Use theme colors
            primary_color = self._get_color("plot.primary", "#2E86AB")
            secondary_color = self._get_color("plot.secondary", "#A23B72")
            grid_color = self._get_color("plot.grid", "#9CA3AF")
            text_color = self._get_color("plot.text", "#374151")
        
        # Style the axes with thicker lines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(text_color)
        ax.spines['bottom'].set_color(text_color)
        ax.spines['left'].set_linewidth(2)
        ax.spines['bottom'].set_linewidth(2)
        
        # Style the grid for better visibility
        ax.grid(True, linestyle='-', alpha=0.4, color=grid_color, linewidth=1)
        ax.set_axisbelow(True)
        
        # Style ticks with larger, bold text
        ax.tick_params(colors=text_color, which='both', width=2, length=6)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')
        
        # Set high contrast color cycle
        ax.set_prop_cycle(color=[primary_color, secondary_color, '#059669', '#F59E0B', '#8B5CF6'])
    
    def create_key_metrics_slide(self, metrics: Dict[str, float], 
                               title: str = "Key Metrics", 
                               format_func=None) -> plt.Figure:
        """Create a slide showing key metrics in a visually appealing way.
        
        Args:
            metrics: Dictionary with metric names and values
            title: Slide title
            format_func: Optional function to format metric values
            
        Returns:
            Key metrics visualization figure
        """
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Remove axes for clean look
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Add title
        fig.suptitle(title, fontsize=28, fontweight='bold', y=0.9)
        
        # Calculate positions for metrics
        num_metrics = len(metrics)
        cols = min(3, num_metrics)  # Max 3 columns
        rows = (num_metrics + cols - 1) // cols
        
        # Display metrics
        for i, (metric_name, value) in enumerate(metrics.items()):
            row = i // cols
            col = i % cols
            
            x = (col + 0.5) / cols
            y = 0.7 - (row * 0.25)
            
            # Format value
            if format_func:
                formatted_value = format_func(value)
            else:
                formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
            
            # Add metric value (large)
            ax.text(x, y + 0.05, formatted_value, 
                   fontsize=36, fontweight='bold', 
                   ha='center', va='center',
                   color='#1E3A8A')
            
            # Add metric name (smaller)
            ax.text(x, y - 0.05, metric_name, 
                   fontsize=18, fontweight='bold',
                   ha='center', va='center',
                   color='#374151')
        
        return fig
    
    def create_comparison_bars(self, categories: List[str], values: List[float],
                              title: str = "Comparison", colors: List[str] = None) -> plt.Figure:
        """Create a horizontal bar chart optimized for presentations.
        
        Args:
            categories: Category names
            values: Values for each category
            title: Chart title
            colors: Optional custom colors
            
        Returns:
            Horizontal bar chart figure
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Use custom colors or default high-contrast ones
        if colors is None:
            colors = ['#1E3A8A', '#DC2626', '#059669', '#F59E0B', '#8B5CF6'] * (len(categories) // 5 + 1)
        
        # Create horizontal bars
        bars = ax.barh(categories, values, color=colors[:len(categories)], height=0.6)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{value:.1f}', ha='left', va='center', 
                   fontsize=16, fontweight='bold')
        
        # Style the chart
        ax.set_title(title, fontsize=22, fontweight='bold', pad=30)
        ax.set_xlabel('Value', fontsize=18, fontweight='bold')
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(2)
        ax.spines['bottom'].set_linewidth(2)
        
        # Style ticks
        ax.tick_params(axis='both', which='major', labelsize=14, width=2)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')
        
        # Add grid for better readability
        ax.grid(axis='x', alpha=0.3, linewidth=1)
        ax.set_axisbelow(True)
        
        fig.tight_layout()
        return fig
