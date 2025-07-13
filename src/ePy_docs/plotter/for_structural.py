from typing import Dict, List, Any, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from .plotter import PlotterBase, get_color, load_colors


class StructuralPlotter(PlotterBase):
    """Structural plotting class for beam diagrams and structural analysis visualizations."""
    
    def beam_moment_diagram(self, x_positions: List[float], moments: List[float],
                           title: str, xlabel: str, ylabel: str,
                           fill_positive: bool = True, fill_negative: bool = True,
                           **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a beam moment diagram.
        
        Args:
            x_positions: Positions along the beam
            moments: Moment values at each position
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            fill_positive: Whether to fill positive moment areas
            fill_negative: Whether to fill negative moment areas
            **kwargs: Additional matplotlib arguments
            
        Returns:
            Tuple containing Figure and axes objects

        Assumptions:
            x_positions and moments have the same length
            Color configuration contains moment visualization colors
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot the moment diagram
        ax.plot(x_positions, moments, color=self._get_color('visualization.plots.moment.line'), 
                linewidth=2, label='Moment')
        
        # Fill areas
        if fill_positive:
            positive_mask = np.array(moments) >= 0
            ax.fill_between(x_positions, moments, 0, where=positive_mask, 
                           color=self._get_color('visualization.plots.moment.positive'), 
                           alpha=0.3, label='Positive Moment')
        
        if fill_negative:
            negative_mask = np.array(moments) < 0
            ax.fill_between(x_positions, moments, 0, where=negative_mask, 
                           color=self._get_color('visualization.plots.moment.negative'), 
                           alpha=0.3, label='Negative Moment')
        
        # Add zero line
        ax.axhline(y=0, color=self._get_color('visualization.axis.zero'), 
                   linestyle='-', linewidth=0.8)
        
        # Configure plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3, color=self._get_color('visualization.axis.grid'))
        ax.legend()
        
        plt.tight_layout()
        return fig, ax

    def beam_shear_diagram(self, x_positions: List[float], shears: List[float],
                          title: str = "Shear Diagram", 
                          xlabel: str = "Position", ylabel: str = "Shear",
                          **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a beam shear diagram."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot the shear diagram as stepped line
        ax.step(x_positions, shears, color=self._get_color('visualization.plots.shear.line'), 
                linewidth=2, where='mid', label='Shear')
        
        # Fill areas
        positive_mask = np.array(shears) >= 0
        negative_mask = np.array(shears) < 0
        
        ax.fill_between(x_positions, shears, 0, where=positive_mask, 
                       step='mid', color=self._get_color('visualization.plots.shear.positive'), 
                       alpha=0.3, label='Positive Shear')
        ax.fill_between(x_positions, shears, 0, where=negative_mask, 
                       step='mid', color=self._get_color('visualization.plots.shear.negative'), 
                       alpha=0.3, label='Negative Shear')
        
        # Add zero line
        ax.axhline(y=0, color=self._get_color('visualization.axis.zero'), 
                   linestyle='-', linewidth=0.8)
        
        # Configure plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3, color=self._get_color('visualization.axis.grid'))
        ax.legend()
        
        plt.tight_layout()
        return fig, ax

    def deflection_diagram(self, x_positions: List[float], deflections: List[float],
                          title: str = "Deflection Diagram", 
                          xlabel: str = "Position", ylabel: str = "Deflection",
                          **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a beam deflection diagram."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot the deflection curve
        deflection_color = self._get_color('visualization.plots.deflection')
        ax.plot(x_positions, deflections, color=deflection_color, linewidth=2, label='Deflection')
        ax.fill_between(x_positions, deflections, 0, alpha=0.2, color=deflection_color)
        
        # Add zero line
        ax.axhline(y=0, color=self._get_color('visualization.axis.zero'), 
                   linestyle='-', linewidth=0.8)
        
        # Mark maximum deflection
        max_deflection_idx = np.argmax(np.abs(deflections))
        max_deflection = deflections[max_deflection_idx]
        max_position = x_positions[max_deflection_idx]
        
        ax.plot(max_position, max_deflection, 'ro', markersize=8, 
                color=self._get_color('visualization.highlight'))
        ax.annotate(f'Max: {max_deflection:.2f}',
                   xy=(max_position, max_deflection),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', 
                            facecolor=self._get_color('visualization.annotation.background'), 
                            alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # Configure plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3, color=self._get_color('visualization.axis.grid'))
        ax.legend()
        
        plt.tight_layout()
        return fig, ax

class ForceMomentPlotter(PlotterBase):
    """Specialized plotter for force and moment bubble plots and analysis visualizations."""
    
    def force_moment_bubble_plot(self, forces: List[float], moments: List[float],
                               title: str, force_label: str, moment_label: str,
                               size_scale: float, min_size: float, max_size: float,
                               groups: Optional[List[str]] = None,
                               highlight_indices: Optional[List[int]] = None,
                               node_labels: Optional[List[str]] = None,
                               **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Create a bubble plot for forces vs moments analysis."""
        # Validate inputs
        if len(forces) != len(moments):
            raise ValueError("Forces and moments lists must have the same length.")
        if not forces:
            raise ValueError("Input data cannot be empty.")

        fig, ax = plt.subplots(figsize=kwargs.pop('figsize', self.figsize))

        # Identify indices of maximum values for highlighting
        max_force_idx = forces.index(max(forces))
        max_moment_idx = moments.index(max(moments, key=abs))

        # Add these to highlight indices if not already present
        if highlight_indices is None:
            highlight_indices = []

        for idx in [max_force_idx, max_moment_idx]:
            if idx not in highlight_indices:
                highlight_indices.append(idx)

        # Calculate magnitudes for scaling bubble sizes
        magnitudes = [np.sqrt(f**2 + m**2) for f, m in zip(forces, moments)]
        max_mag = max(magnitudes) if magnitudes else 1

        # Scale bubble sizes
        sizes = [min(max_size, max(min_size, m * size_scale * 500 / max_mag)) for m in magnitudes]

        # Use groups for colors if provided
        if groups:
            unique_groups = sorted(set(groups))
            colors = plt.cm.tab10(np.linspace(0, 1, len(unique_groups)))

            for group in unique_groups:
                indices = [i for i, g in enumerate(groups) if g == group]
                if not indices:
                    continue

                ax.scatter(
                    [moments[i] for i in indices],
                    [forces[i] for i in indices],
                    s=[sizes[i] for i in indices],
                    alpha=0.6,
                    label=str(group),
                    edgecolors=self._get_color('visualization.axis.border'),
                    linewidths=0.5,
                    zorder=5
                )
        else:
            ax.scatter(
                moments, forces, s=sizes,
                alpha=0.6,
                edgecolors=self._get_color('visualization.axis.border'),
                linewidths=0.5,
                zorder=5
            )

        # Highlight specific points if requested
        if highlight_indices:
            highlight_x = [moments[i] for i in highlight_indices if i < len(moments)]
            highlight_y = [forces[i] for i in highlight_indices if i < len(forces)]
            highlight_sizes = [sizes[i] * 1.5 for i in highlight_indices if i < len(sizes)]

            ax.scatter(
                highlight_x, highlight_y,
                s=highlight_sizes,
                facecolors='none',
                edgecolors=self._get_color('visualization.highlight'),
                linewidths=2,
                zorder=15
            )

            # Add labels to highlighted points if node_labels provided
            if node_labels:
                for i in highlight_indices:
                    if i < len(moments) and i < len(forces) and i < len(node_labels):
                        if i == max_force_idx:
                            label_text = f"{node_labels[i]} (F:{forces[i]:.0f}, M:{moments[i]:.0f})"
                        elif i == max_moment_idx:
                            label_text = f"{node_labels[i]} (F:{forces[i]:.0f}, M:{moments[i]:.0f})"
                        else:
                            label_text = node_labels[i]

                        ax.annotate(
                            label_text,
                            (moments[i], forces[i]),
                            xytext=(0, 10),
                            textcoords='offset points',
                            ha='center',
                            va='bottom',
                            fontweight='bold',
                            fontsize=9,
                            bbox=dict(boxstyle="round,pad=0.3", 
                                    facecolor=self._get_color('visualization.annotation.background'), 
                                    alpha=0.7),
                            zorder=20
                        )

        # Create reference bubbles based on actual data range
        max_force = max(forces)
        max_moment = max(abs(m) for m in moments)

        reference_values = [
            (max_force * 0.25, 0),
            (max_force, 0),
            (0, max_moment * 0.25),
            (0, max_moment)
        ]

        ref_magnitudes = [np.sqrt(f**2 + m**2) for f, m in reference_values]
        ref_sizes = [min(max_size, max(min_size, m * size_scale * 500 / max_mag)) for m in ref_magnitudes]

        # Add reference legend entries
        ax.scatter([], [], s=ref_sizes[0], alpha=0.6, color='gray', edgecolors='black',
                  label=f"F ≈ {reference_values[0][0]:.0f}")
        ax.scatter([], [], s=ref_sizes[1], alpha=0.6, color='gray', edgecolors='black',
                  label=f"F ≈ {reference_values[1][0]:.0f}")
        ax.scatter([], [], s=ref_sizes[2], alpha=0.6, color='gray', edgecolors='black',
                  label=f"M ≈ {reference_values[2][1]:.0f}")
        ax.scatter([], [], s=ref_sizes[3], alpha=0.6, color='gray', edgecolors='black',
                  label=f"M ≈ {reference_values[3][1]:.0f}")

        # Configure plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(moment_label, fontsize=12)
        ax.set_ylabel(force_label, fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add zero lines
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

        # Place legend outside the plot
        ax.legend(title="Cases and Reference Values", loc='upper left',
                 bbox_to_anchor=(1, 1), fontsize=9)

        plt.tight_layout()
        return fig, ax
