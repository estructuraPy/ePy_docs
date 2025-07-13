"""Plotting utilities for engineering visualization and general data plotting.

Provides base plotting functionality with color configuration and specialized engineering plots.
"""

import os
from typing import Dict, List, Any, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from tqdm import tqdm

from .plotter import PlotterBase


class GeneralPlots(PlotterBase):
    """General plotting class for creating basic visualizations.
    
    Assumptions:
        Base plotting functionality is properly initialized
        Standard color schemes are available in configuration
        Input data follows expected formats for each plot type
    """

    def scatter(self, x_data: List[float], y_data: List[float],
                title: str, xlabel: str, ylabel: str, marker: str,
                colors: Optional[List] = None, sizes: Optional[List[float]] = None,
                labels: Optional[List[str]] = None, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a scatter plot with customizable markers.

        Args:
            x_data: X-axis data
            y_data: Y-axis data
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            marker: Marker style
            colors: Optional colors for points
            sizes: Optional sizes for points
            labels: Optional labels for annotation
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            x_data and y_data have the same length
            Color configuration contains scatter plot colors
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Update scatter_kwargs with colors from config
        scatter_kwargs = {
            'alpha': 0.7,
            's': 100,
            'marker': marker,
            'edgecolors': self._get_color('visualization.axis.border'),
            'linewidth': 1,
            'c': [self._get_color('visualization.nodes.default')] if colors is None else colors
        }
        scatter_kwargs.update(kwargs)

        if sizes is not None:
            scatter_kwargs['s'] = sizes

        scatter = ax.scatter(x_data, y_data, **scatter_kwargs)

        # Add labels if provided
        if labels is not None:
            for i, label in enumerate(labels):
                if i < len(x_data) and i < len(y_data):
                    ax.annotate(label, (x_data[i], y_data[i]),
                                xytext=(5, 5), textcoords='offset points',
                                fontsize=9, alpha=0.8)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        return fig, ax

    def bar_chart(self, data: Dict[str, float], title: str, xlabel: str, ylabel: str,
                  horizontal: bool = False, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a bar chart.

        Args:
            data: Dictionary with categories as keys and values as values
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            horizontal: Whether to create horizontal bars
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            The data dictionary contains string keys and numeric values
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        categories = list(data.keys())
        values = list(data.values())

        # Update bar style with colors from config
        bar_kwargs = {
            'alpha': 0.8,
            'edgecolor': self._get_color('visualization.axis.border'),
            'color': self._get_color('visualization.plots.bar')
        }
        bar_kwargs.update(kwargs)

        if horizontal:
            bars = ax.barh(categories, values, **bar_kwargs)
            ax.set_xlabel(ylabel, fontsize=12)
            ax.set_ylabel(xlabel, fontsize=12)
        else:
            bars = ax.bar(categories, values, **bar_kwargs)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)

        # Add value labels on bars
        for bar in bars:
            if horizontal:
                width = bar.get_width()
                ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{width:.1f}', ha='left', va='center', fontweight='bold')
            else:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + max(values) * 0.01,
                       f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color=self._get_color('visualization.axis.grid'))

        plt.tight_layout()
        return fig, ax

    def pie_chart(self, data: Dict[str, float], title: str,
                  **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a pie chart.

        Args:
            data: Dictionary with categories as keys and values as values
            title: Plot title
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            The data dictionary contains string keys and numeric values
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        labels = list(data.keys())
        values = list(data.values())

        pie_kwargs = {'autopct': '%1.1f%%', 'startangle': 90}
        pie_kwargs.update(kwargs)

        ax.pie(values, labels=labels, **pie_kwargs)
        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        return fig, ax

    def line_plot(self, x_data: List[float], y_data: List[float],
                  title: str, xlabel: str, ylabel: str,
                  **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a line plot.

        Args:
            x_data: X-axis data
            y_data: Y-axis data
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            x_data and y_data have the same length
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        line_kwargs = {'linewidth': 2, 'marker': 'o', 'markersize': 6}
        line_kwargs.update(kwargs)

        ax.plot(x_data, y_data, **line_kwargs)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def timeline(self, x_data: List[float], y_data: List[float],
                 title: str, xlabel: str, ylabel: str,
                 marker_style: str, line_style: str, annotate_events: bool,
                 event_labels: Optional[List[str]] = None,
                 **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a timeline-style plot.

        Args:
            x_data: Time-axis data (e.g., years)
            y_data: Value-axis data (e.g., magnitude of event, or constant for event markers)
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            marker_style: Marker style for events on the line
            line_style: Line style for the timeline
            annotate_events: If True, and event_labels are provided, annotate points
            event_labels: Optional labels for events, used if annotate_events is True
            **kwargs: Additional matplotlib arguments for the plot line

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            x_data and y_data have the same length
            If annotate_events is True, event_labels must have the same length as x_data and y_data
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        timeline_kwargs = {'linewidth': 2, 'marker': marker_style, 'linestyle': line_style, 'markersize': 8}
        timeline_kwargs.update(kwargs)

        ax.plot(x_data, y_data, **timeline_kwargs)

        if annotate_events and event_labels:
            if len(event_labels) == len(x_data) == len(y_data):
                for i, label in enumerate(event_labels):
                    ax.annotate(label, (x_data[i], y_data[i]),
                                xytext=(5, 10), textcoords='offset points',
                                fontsize=9, ha='left', va='bottom',
                                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.5))
            else:
                print("Warning: Length of event_labels must match x_data and y_data for annotation.")

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')

        # Optional: Improve timeline appearance, e.g., by removing top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        return fig, ax

    def box_plot(self, data: Dict[str, List[float]], title: str, xlabel: str, ylabel: str,
                 **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a box plot.

        Args:
            data: Dictionary with categories as keys and lists of values
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            The data dictionary contains string keys and lists of numeric values
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        labels = list(data.keys())
        values = list(data.values())

        box_kwargs = {'patch_artist': True}
        box_kwargs.update(kwargs)

        box_plot = ax.boxplot(values, labels=labels, **box_kwargs)

        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def histogram(self, data: List[float], title: str, xlabel: str, ylabel: str,
                  bins: int, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a histogram.

        Args:
            data: Data to plot
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            bins: Number of bins
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            The data is a list of numeric values
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        hist_kwargs = {'alpha': 0.7, 'edgecolor': 'black'}
        hist_kwargs.update(kwargs)

        ax.hist(data, bins=bins, **hist_kwargs)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def dual_axis_plot(self, x_data: List[float], y1_data: List[float], y2_data: List[float],
                       title: str, xlabel: str, ylabel1: str, ylabel2: str,
                       **kwargs) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
        """Create a plot with dual y-axes.

        Args:
            x_data: X-axis data
            y1_data: Left y-axis data
            y2_data: Right y-axis data
            title: Plot title
            xlabel: X-axis label
            ylabel1: Left y-axis label
            ylabel2: Right y-axis label
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and tuple of axes objects (left, right)

        Assumptions:
            x_data, y1_data, and y2_data have the same length
        """
        fig, ax1 = plt.subplots(figsize=self.figsize)

        color1 = kwargs.get('color1', self._get_color('visualization.plots.dual_axis.primary'))
        color2 = kwargs.get('color2', self._get_color('visualization.plots.dual_axis.secondary'))

        ax1.set_xlabel(xlabel, fontsize=12)
        ax1.set_ylabel(ylabel1, color=color1, fontsize=12)
        line1 = ax1.plot(x_data, y1_data, color=color1, linewidth=2, marker='o')
        ax1.tick_params(axis='y', labelcolor=color1)

        ax2 = ax1.twinx()
        ax2.set_ylabel(ylabel2, color=color2, fontsize=12)
        line2 = ax2.plot(x_data, y2_data, color=color2, linewidth=2, marker='s')
        ax2.tick_params(axis='y', labelcolor=color2)

        plt.title(title, fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, color=self._get_color('visualization.axis.grid'))

        fig.tight_layout()
        return fig, (ax1, ax2)

    def grouped_bar_chart(self, data1: List[float], data2: List[float], categories: List[str],
                          title: str, xlabel: str, ylabel: str, label1: str, label2: str,
                          **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a grouped bar chart.

        Args:
            data1: First data series
            data2: Second data series
            categories: Category labels
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            label1: Label for first series
            label2: Label for second series
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            data1 and data2 have the same length as categories
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        x = np.arange(len(categories))
        width = kwargs.get('width', 0.35)

        bars1 = ax.bar(x - width/2, data1, width, label=label1, alpha=0.8)
        bars2 = ax.bar(x + width/2, data2, width, label=label2, alpha=0.8)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def heatmap(self, data: np.ndarray, title: str,
                x_labels: Optional[List[str]] = None,
                y_labels: Optional[List[str]] = None, 
                **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a heatmap.

        Args:
            data: 2D array of data
            title: Plot title
            x_labels: Optional x-axis labels
            y_labels: Optional y-axis labels
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            data is a 2D numpy array
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Update heatmap style with colors from config
        heatmap_kwargs = {
            'cmap': kwargs.pop('cmap', 'viridis'),
            'aspect': 'auto',
            'edgecolors': self._get_color('visualization.axis.border')
        }
        heatmap_kwargs.update(kwargs)

        im = ax.imshow(data, **heatmap_kwargs)

        if x_labels is not None:
            ax.set_xticks(np.arange(len(x_labels)))
            ax.set_xticklabels(x_labels)

        if y_labels is not None:
            ax.set_yticks(np.arange(len(y_labels)))
            ax.set_yticklabels(y_labels)

        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)  # noqa: F841

        plt.tight_layout()
        return fig, ax

    def subplots_grid(self, nrows: int, ncols: int, figsize: Optional[Tuple[int, int]] = None,
                      **kwargs) -> Tuple[plt.Figure, np.ndarray]:
        """Create a grid of subplots.

        Args:
            nrows: Number of rows
            ncols: Number of columns
            figsize: Optional figure size, uses default if None
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and array of axes objects
        """
        if figsize is None:
            figsize = (self.figsize[0] * ncols, self.figsize[1] * nrows)

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)

        return fig, axes

    def scatter_with_highlights(self, data_dict: Dict[str, List], x_key: str, y_key: str,
                                group_key: str, title: str, xlabel: str, ylabel: str,
                                highlight_labels: bool, highlight_key: str = None,
                                **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a scatter plot with points grouped by a category and with certain points highlighted.

        Args:
            data_dict: Dictionary containing lists for x values, y values, grouping variable, and highlight flag
            x_key: Key for x-axis values in data_dict
            y_key: Key for y-axis values in data_dict
            group_key: Key for grouping variable in data_dict
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            highlight_labels: Whether to add labels to highlighted points
            highlight_key: Key for boolean flag indicating which points to highlight
            **kwargs: Additional matplotlib arguments

        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            The keys x_key, y_key, and group_key exist in data_dict
            If highlight_key is provided, it exists in data_dict
            All lists in data_dict have the same length
        """
        fig, ax = plt.subplots(figsize=kwargs.pop('figsize', self.figsize))

        # Identify unique groups
        groups = set(data_dict[group_key])
        colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))
        group_to_color = {group: color for group, color in zip(groups, colors)}  # noqa: F841

        # Plot each group separately
        for group in groups:
            indices = [i for i, g in enumerate(data_dict[group_key]) if g == group]

            ax.scatter(
                [data_dict[x_key][i] for i in indices],
                [data_dict[y_key][i] for i in indices],
                label=str(group),
                alpha=0.7,
                s=kwargs.pop('size', 50),
                edgecolors=self._get_color('visualization.axis.border')
            )

        # Highlight specific points if requested
        if highlight_key in data_dict:
            highlight_indices = [i for i, flag in enumerate(data_dict[highlight_key]) if flag]

            # Add circles around highlighted points
            ax.scatter(
                [data_dict[x_key][i] for i in highlight_indices],
                [data_dict[y_key][i] for i in highlight_indices],
                s=kwargs.pop('highlight_size', 100),
                facecolors='none',
                edgecolors=self._get_color('visualization.highlight'),
                linewidth=2,
                zorder=10
            )

            # Add labels to highlighted points if requested
            if highlight_labels:
                for i in highlight_indices:
                    x_val = data_dict[x_key][i]
                    y_val = data_dict[y_key][i]
                    group_val = data_dict[group_key][i]

                    ax.annotate(
                        f"{group_val}: {y_val:.0f}",
                        xy=(x_val, y_val),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center',
                        va='bottom',
                        fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor=self._get_color('visualization.annotation.background'), 
                                alpha=0.7)
                    )

        # Configure plot
        ax.set_title(title, fontsize=14)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3, color=self._get_color('visualization.axis.grid'))
        ax.legend(title=kwargs.pop('legend_title', 'Group'), loc='upper left',
                  bbox_to_anchor=(1, 1), fontsize=10)

        plt.tight_layout()
        return fig, ax