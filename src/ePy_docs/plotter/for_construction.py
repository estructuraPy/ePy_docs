"""Plotting utilities for engineering visualization and general data plotting.

Provides base plotting functionality with color configuration and specialized engineering plots.
"""
import numpy as np

from .plotter import PlotterBase



class EngineeringPlots(PlotterBase):
    """Engineering plotting class combining civil and structural engineering visualizations.
    
    Assumptions:
        Base plotting functionality is properly initialized
        Engineering-specific color schemes are available in configuration
        Input data follows engineering conventions and units
    """

    
    def add_grid(self, ax, x_min, x_max, y_min, y_max,
                 use_node_positions: bool, x_spacing: float, y_spacing: float,
                 grid_color: str, label_color: str, grid_style: str, 
                 grid_alpha: float, label_offset: float, fontsize: int,
                 threshold: float, nodes=None):
        """Add structural reference grid lines and labels to a plot.

        Args:
            ax: Matplotlib axes object
            x_min: Minimum x value for grid extent
            x_max: Maximum x value for grid extent
            y_min: Minimum y value for grid extent
            y_max: Maximum y value for grid extent
            use_node_positions: Whether to align grid with node positions
            x_spacing: Grid spacing in x direction
            y_spacing: Grid spacing in y direction
            grid_color: Color for grid lines
            label_color: Color for grid labels
            grid_style: Line style for grid
            grid_alpha: Alpha transparency for grid lines
            label_offset: Offset for grid labels
            fontsize: Font size for grid labels
            threshold: Threshold for grouping similar coordinates
            nodes: Optional dictionary of node objects

        Returns:
            Dictionary containing grid positions and labels

        Assumptions:
            Node objects have x and y attributes if provided
            Color configuration is available for visualization elements
        """
        # Use colors from configuration
        if grid_color == 'gray':
            grid_color = self._get_color('visualization.axis.grid')
        if label_color == 'blue':
            label_color = self._get_color('brand.blue')
    
        if use_node_positions and nodes:
            # Extract unique X and Y coordinates from nodes
            x_positions = []
            y_positions = []
            
            # Get all X and Y positions
            all_x_positions = [node.x for node in nodes.values()]
            all_y_positions = [node.y for node in nodes.values()]
            
            # Group similar X coordinates using threshold
            all_x_positions.sort()
            for x in all_x_positions:
                # Only add if not close to an already added position
                if not x_positions or all(abs(x - existing_x) > threshold for existing_x in x_positions):
                    x_positions.append(x)
            
            # Group similar Y coordinates using threshold
            all_y_positions.sort()
            for y in all_y_positions:
                # Only add if not close to an already added position
                if not y_positions or all(abs(y - existing_y) > threshold for existing_y in y_positions):
                    y_positions.append(y)
        else:
            # Generate grid line positions at fixed intervals
            x_positions = np.arange(
                np.floor(x_min / x_spacing) * x_spacing,
                np.ceil(x_max / x_spacing) * x_spacing + x_spacing,
                x_spacing
            )
            
            y_positions = np.arange(
                np.floor(y_min / y_spacing) * y_spacing,
                np.ceil(y_max / y_spacing) * y_spacing + y_spacing,
                y_spacing
            )
    
        # Filter positions to be within plot limits
        x_positions = [x for x in x_positions if x_min <= x <= x_max]
        y_positions = [y for y in y_positions if y_min <= y <= y_max]
        
        # Sort positions ascending
        x_positions.sort()  # Left to right
        y_positions.sort()  # Bottom to top
        
        # Draw vertical grid lines first (numbers)
        for i, x in enumerate(x_positions):
            ax.axvline(x, color=grid_color, linestyle=grid_style, alpha=grid_alpha, zorder=1)
            
            # Number columns starting from 1
            grid_label = str(i + 1)
            
            # Add label at bottom
            ax.text(x, y_min - label_offset, grid_label, 
                   ha='center', va='top', color=label_color, 
                   fontsize=fontsize, fontweight='bold', 
                   bbox=dict(facecolor=self._get_color('visualization.annotation.background'), alpha=0.8))
               
            # Add label at top
            ax.text(x, y_max + label_offset, grid_label, 
                   ha='center', va='bottom', color=label_color, 
                   fontsize=fontsize, fontweight='bold', 
                   bbox=dict(facecolor=self._get_color('visualization.annotation.background'), alpha=0.8))
        
        # Create explicit grid label mapping, with y positions from bottom to top and letters from A upwards
        grid_labels = {}
        for i, y in enumerate(y_positions):
            grid_labels[y] = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
        
        # Draw horizontal grid lines separately to control z-order and label visibility
        # Draw from top to bottom to ensure lower labels (A, B) appear on top of higher ones
        for y in reversed(y_positions):
            ax.axhline(y, color=grid_color, linestyle=grid_style, alpha=grid_alpha, zorder=1)
            
            # Get label for this y position
            grid_label = grid_labels[y]
            
            # Increase visibility with better background
            bbox_props = dict(
                facecolor=self._get_color('visualization.annotation.background'), 
                edgecolor=grid_color,
                alpha=0.9,
                boxstyle='round,pad=0.3'
            )
            
            # Label at left - with higher zorder to ensure visibility
            ax.text(x_min - label_offset, y, grid_label, 
                   ha='right', va='center', color=label_color, 
                   fontsize=fontsize, fontweight='bold', bbox=bbox_props,
                   zorder=10)  # Higher zorder
               
            # Label at right
            ax.text(x_max + label_offset, y, grid_label, 
                   ha='left', va='center', color=label_color, 
                   fontsize=fontsize, fontweight='bold', bbox=bbox_props,
                   zorder=10)  # Higher zorder

        # Return the positions and labels for reference if needed
        return {'x_positions': x_positions, 'y_positions': y_positions, 'grid_labels': grid_labels}
