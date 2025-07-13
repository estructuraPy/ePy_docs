"""Geotechnical and foundation plotting utilities.

Provides specialized plotting functionality for foundation layouts, soil conditions,
and geotechnical visualization with color configuration support.
"""

import os
from typing import Dict, List, Any, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from .plotter import get_color, load_colors

class GeoPlotter:
    """Geotechnical plotting class for foundation and soil visualization."""

    def __init__(self, figsize: Tuple[int, int] = (10, 8)):
        """Initialize the geotechnical plotter.
        
        Args:
            figsize: Default figure size as (width, height)
        """
        self.figsize = figsize
        self.colors = self._load_colors()

    def _load_colors(self) -> Dict[str, Any]:
        """Load color configuration from colors.json file."""
        return load_colors()

    def _get_color(self, color_key: str) -> Tuple[float, float, float]:
        """Get RGB color values from colors.json by key path.
        
        Args:
            color_key: Dot-separated path to color in colors configuration.
            
        Returns:
            Tuple of RGB values normalized to 0-1 range.
        """
        color_str = get_color(color_key, '#000000')
        
        if isinstance(color_str, str):
            if color_str.startswith('#'):
                return tuple(int(color_str.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
        
        return (0, 0, 0)

    def foundation_layout_plot(self,
                            nodes: Dict[str, Any],
                            objects: Dict[str, Any],
                            level: float,
                            length_unit: str = 'm',
                            title: Optional[str] = None,
                            show_dimensions: bool = True,
                            show_node_labels: bool = True,
                            node_color: Optional[str] = None,
                            foundation_color: Optional[str] = None,
                            foundation_label_color: Optional[str] = 'black',
                            foundation_colors: Optional[Dict[str, Any]] = None,
                            figsize: Optional[Tuple[int, int]] = None,
                            **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a foundation layout plot showing nodes and foundation blocks."""
        if figsize is None:
            figsize = self.figsize
            
        fig, ax = plt.subplots(figsize=figsize)
        
        edge_color = self._get_color('visualization.axis.border')
        label_color = self._get_color('visualization.nodes.label')
        grid_color = self._get_color('visualization.axis.grid')
        
        node_positions_x = [node.x for node in nodes.values()]
        node_positions_y = [node.y for node in nodes.values()]
        
        if not objects:
            class MockFoundation:
                def __init__(self, width, length):
                    self.width = width
                    self.length = length
            
            if node_positions_x and node_positions_y:
                x_span = max(node_positions_x) - min(node_positions_x)
                y_span = max(node_positions_y) - min(node_positions_y)
                max_span = max(x_span, y_span) if max(x_span, y_span) > 0 else 10.0
                uniform_block_size = max(0.5, min(3.0, max_span * 0.10))
            else:
                uniform_block_size = 1.5
            
            objects = {}
            
            for node_id in nodes.keys():
                objects[node_id] = MockFoundation(uniform_block_size, uniform_block_size)
            
            is_mock = True
        else:
            is_mock = False
        
        foundation_extents_x = []
        foundation_extents_y = []
        for node_id, foundation in objects.items():
            if node_id in nodes:
                node = nodes[node_id]
                width = foundation.width
                length = foundation.length
                foundation_extents_x.extend([node.x - width/2, node.x + width/2])
                foundation_extents_y.extend([node.y - length/2, node.y + length/2])
        
        for node_id, foundation in objects.items():
            if node_id in nodes:
                node = nodes[node_id]
                
                block_color = None
                if foundation_colors and node_id in foundation_colors:
                    block_color = foundation_colors[node_id]
                else:
                    block_color = foundation_color or get_color('visualization.elements.default', '#cccccc')
                
                width = foundation.width
                length = foundation.length
                x = node.x - width/2
                y = node.y - length/2
                
                rect = patches.Rectangle(
                    (x, y), width, length,
                    linewidth=1,
                    edgecolor='black',
                    facecolor=block_color,
                    alpha=0.7,
                    zorder=5
                )
                ax.add_patch(rect)
                
                if show_dimensions:
                    dimension_text = f"{width:.1f}×{length:.1f}{length_unit}"
                    
                    min_dimension = min(width, length)
                    dynamic_fontsize = max(7, min(12, int(min_dimension * 4)))
                    
                    text_length_factor = len(dimension_text)
                    if text_length_factor > 8:
                        dynamic_fontsize = max(6, dynamic_fontsize - 1)
                    
                    ax.text(
                        node.x, node.y - length/3,
                        dimension_text,
                        ha='center',
                        va='center',
                        color=foundation_label_color,
                        fontsize=dynamic_fontsize,
                        fontweight='bold',
                        zorder=15
                    )
        
        node_x = [node.x for node in nodes.values()]
        node_y = [node.y for node in nodes.values()]
        node_ids = list(nodes.keys())
        
        ax.scatter(node_x, node_y, 
                   s=kwargs.get('node_size', 120),
                   c=node_color or get_color('visualization.nodes.default', '#4472C4'),
                   marker='o', 
                   edgecolors=edge_color,
                   linewidth=0.5,
                   zorder=10, 
                   alpha=0.8)

        if show_node_labels:
            for i, node_id in enumerate(node_ids):
                dynamic_label_fontsize = 9
                
                label_offset_x = 0
                label_offset_y = 15
                
                if node_id in objects:
                    foundation = objects[node_id]
                    min_dimension = min(foundation.width, foundation.length)
                    dynamic_label_fontsize = max(8, min(14, int(min_dimension * 5)))
                    
                    label_length = len(f"N{node_id}")
                    if label_length > 3:
                        dynamic_label_fontsize = max(8, dynamic_label_fontsize - 1)
                    
                    label_offset_x = -foundation.width * 0.10 * 40
                    label_offset_y = foundation.length * 0.18 * 40
                
                ax.annotate(f"N{node_id}", 
                          (node_x[i], node_y[i]),
                          xytext=(label_offset_x, label_offset_y), 
                          textcoords='offset points',
                          fontsize=dynamic_label_fontsize, 
                          color=label_color,
                          alpha=0.8, 
                          zorder=15,
                          ha='center',
                          va='center')

        ax.set_xlabel(f"({length_unit})", fontsize=12)
        ax.set_ylabel(f"({length_unit})", fontsize=12)
        
        all_x = node_positions_x + foundation_extents_x
        all_y = node_positions_y + foundation_extents_y
        
        if all_x and all_y:
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            
            x_padding = 0.1 * (x_max - x_min) if x_max != x_min else 1.0
            y_padding = 0.1 * (y_max - y_min) if y_max != y_min else 1.0
            
            ax.set_xlim(x_min - x_padding, x_max + x_padding)
            ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        if kwargs.get('show_grid', True):
            self._add_grid(
                ax,
                nodes=nodes,
                x_min=x_min - x_padding if all_x else -10,
                x_max=x_max + x_padding if all_x else 10,
                y_min=y_min - y_padding if all_y else -10,
                y_max=y_max + y_padding if all_y else 10,
                use_node_positions=kwargs.get('use_node_grid', True),
                x_spacing=kwargs.get('grid_spacing_x', 5.0),
                y_spacing=kwargs.get('grid_spacing_y', 5.0),
                grid_color=kwargs.get('grid_color', grid_color),
                label_color=kwargs.get('grid_label_color', get_color('visualization.axis.grid', '#cccccc')),
                grid_style=kwargs.get('grid_style', '--'),
                grid_alpha=kwargs.get('grid_alpha', 0.5),
                label_offset=kwargs.get('grid_label_offset', 0.3),
                fontsize=kwargs.get('grid_fontsize', 10),
            )
        
        if kwargs.get('grid_step', 1.0) is not None:
            ax.grid(True, 
                    alpha=0.3, 
                    color=grid_color,
                    linestyle='--')
        
        ax.set_aspect('equal')

        from matplotlib.lines import Line2D
        
        foundation_label = 'Foundation block'
        if is_mock:
            foundation_label += ' (presize)'
        
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', 
               markerfacecolor=node_color or get_color('visualization.nodes.default', '#4472C4'),
               markersize=10, alpha=0.8, label='Support node'),
            patches.Patch(facecolor=foundation_color or get_color('visualization.elements.default', '#cccccc'), 
                     edgecolor='black', alpha=0.7, label=foundation_label)
        ]

        ax.legend(handles=legend_elements, loc='upper right',
                 bbox_to_anchor=(0.98, 0.98), fontsize=10)

        plt.tight_layout()
        return fig, ax

    def _add_grid(self, ax, x_min, x_max, y_min, y_max,
                  nodes=None, use_node_positions=True,
                  x_spacing=5.0, y_spacing=5.0,
                  grid_color='gray', label_color='blue',
                  grid_style='--', grid_alpha=0.5,
                  label_offset=0.3, fontsize=10,
                  threshold=0.05):
        """Add structural reference grid lines and labels to a plot."""
        if grid_color == 'gray':
            grid_color = get_color('visualization.axis.grid', '#cccccc')
        if label_color == 'blue':
            label_color = get_color('brand.blue', '#0066cc')
    
        if use_node_positions and nodes:
            x_positions = []
            y_positions = []
            
            all_x_positions = [node.x for node in nodes.values()]
            all_y_positions = [node.y for node in nodes.values()]
            
            all_x_positions.sort()
            for x in all_x_positions:
                if not x_positions or all(abs(x - existing_x) > threshold for existing_x in x_positions):
                    x_positions.append(x)
            
            all_y_positions.sort()
            for y in all_y_positions:
                if not y_positions or all(abs(y - existing_y) > threshold for existing_y in y_positions):
                    y_positions.append(y)
        else:
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
    
        x_positions = [x for x in x_positions if x_min <= x <= x_max]
        y_positions = [y for y in y_positions if y_min <= y <= y_max]
        
        x_positions.sort()
        y_positions.sort()
        
        for i, x in enumerate(x_positions):
            ax.axvline(x, color=grid_color, linestyle=grid_style, alpha=grid_alpha, zorder=1)
            
            grid_label = str(i + 1)
            
            ax.text(x, y_min - label_offset, grid_label, 
                   ha='center', va='top', color=label_color, 
                   fontsize=fontsize, fontweight='bold', 
                   bbox=dict(facecolor=get_color('visualization.annotation.background', '#ffffff'), alpha=0.8))
               
            ax.text(x, y_max + label_offset, grid_label, 
                   ha='center', va='bottom', color=label_color, 
                   fontsize=fontsize, fontweight='bold', 
                   bbox=dict(facecolor=get_color('visualization.annotation.background', '#ffffff'), alpha=0.8))
        
        grid_labels = {}
        for i, y in enumerate(y_positions):
            grid_labels[y] = chr(65 + i) if i < 26 else f"A{chr(65 + i - 26)}"
        
        for y in reversed(y_positions):
            ax.axhline(y, color=grid_color, linestyle=grid_style, alpha=grid_alpha, zorder=1)
            
            grid_label = grid_labels[y]
            
            bbox_props = dict(
                facecolor=get_color('visualization.annotation.background', '#ffffff'), 
                edgecolor=grid_color,
                alpha=0.9,
                boxstyle='round,pad=0.3'
            )
            
            ax.text(x_min - label_offset, y, grid_label, 
                   ha='right', va='center', color=label_color, 
                   fontsize=fontsize, fontweight='bold', bbox=bbox_props,
                   zorder=10)
               
            ax.text(x_max + label_offset, y, grid_label, 
                   ha='left', va='center', color=label_color, 
                   fontsize=fontsize, fontweight='bold', bbox=bbox_props,
                   zorder=10)

        return {'x_positions': x_positions, 'y_positions': y_positions, 'grid_labels': grid_labels}
