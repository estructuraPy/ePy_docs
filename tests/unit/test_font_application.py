"""
Unit tests for font application functions.
Tests that fonts are applied directly to matplotlib elements.
"""

import pytest
import matplotlib.pyplot as plt
import numpy as np
from src.ePy_docs.core._images import (
    setup_matplotlib_fonts,
    apply_fonts_to_plot,
    apply_fonts_to_figure
)


class TestFontApplication:
    """Test font application to matplotlib elements."""
    
    def test_setup_matplotlib_fonts_returns_list(self):
        """Test that setup returns a font list."""
        font_list = setup_matplotlib_fonts('handwritten')
        
        assert isinstance(font_list, list)
        assert len(font_list) > 0
        assert 'C2024_anm_font' in font_list
    
    def test_apply_fonts_to_plot(self):
        """Test applying fonts to a single axis."""
        # Setup
        font_list = setup_matplotlib_fonts('handwritten')
        fig, ax = plt.subplots()
        
        # Create plot with labels
        x = np.linspace(0, 10, 10)
        ax.plot(x, np.sin(x), label='sine')
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_title('Title')
        ax.legend()
        
        # Apply fonts
        apply_fonts_to_plot(ax, font_list)
        
        # Verify fonts were set
        title = ax.get_title()
        xlabel = ax.get_xlabel()
        ylabel = ax.get_ylabel()
        
        # Check that text exists
        assert title == 'Title'
        assert xlabel == 'X Label'
        assert ylabel == 'Y Label'
        
        # Check that font family was set on text objects
        title_obj = ax.title
        assert title_obj.get_fontfamily() == font_list
        
        xlabel_obj = ax.xaxis.label
        assert xlabel_obj.get_fontfamily() == font_list
        
        ylabel_obj = ax.yaxis.label
        assert ylabel_obj.get_fontfamily() == font_list
        
        plt.close(fig)
    
    def test_apply_fonts_to_figure(self):
        """Test applying fonts to entire figure with multiple axes."""
        # Setup
        font_list = setup_matplotlib_fonts('academic')
        fig, (ax1, ax2) = plt.subplots(1, 2)
        
        # Create plots
        x = np.linspace(0, 10, 10)
        ax1.plot(x, np.sin(x))
        ax1.set_title('Plot 1')
        ax1.set_xlabel('X1')
        
        ax2.plot(x, np.cos(x))
        ax2.set_title('Plot 2')
        ax2.set_xlabel('X2')
        
        fig.suptitle('Figure Title')
        
        # Apply fonts to entire figure
        apply_fonts_to_figure(fig, font_list)
        
        # Verify suptitle
        assert fig._suptitle.get_fontfamily() == font_list
        
        # Verify both axes received fonts
        assert ax1.title.get_fontfamily() == font_list
        assert ax2.title.get_fontfamily() == font_list
        assert ax1.xaxis.label.get_fontfamily() == font_list
        assert ax2.xaxis.label.get_fontfamily() == font_list
        
        plt.close(fig)
    
    def test_apply_fonts_to_tick_labels(self):
        """Test that tick labels receive font application."""
        # Setup
        font_list = setup_matplotlib_fonts('modern')
        fig, ax = plt.subplots()
        
        # Create plot with specific ticks
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(['A', 'B', 'C'])
        
        # Apply fonts
        apply_fonts_to_plot(ax, font_list)
        
        # Check tick labels
        for label in ax.get_xticklabels():
            assert label.get_fontfamily() == font_list
        
        plt.close(fig)
    
    def test_apply_fonts_to_legend(self):
        """Test that legend text receives font application."""
        # Setup
        font_list = setup_matplotlib_fonts('handwritten')
        fig, ax = plt.subplots()
        
        # Create plot with legend
        ax.plot([1, 2, 3], [1, 2, 3], label='Series 1')
        ax.plot([1, 2, 3], [3, 2, 1], label='Series 2')
        ax.legend()
        
        # Apply fonts
        apply_fonts_to_plot(ax, font_list)
        
        # Check legend texts
        legend = ax.get_legend()
        for text in legend.get_texts():
            assert text.get_fontfamily() == font_list
        
        plt.close(fig)
    
    def test_font_application_matches_table_approach(self):
        """
        Verify that our approach matches what tables do.
        Tables use: cell.get_text().set_fontfamily(font_list)
        We use: element.set_fontfamily(font_list)
        """
        font_list = setup_matplotlib_fonts('handwritten')
        fig, ax = plt.subplots()
        
        # Create text element
        text = ax.text(0.5, 0.5, 'Test Text')
        
        # Apply font the way tables do it
        text.set_fontfamily(font_list)
        
        # Verify it was set correctly
        assert text.get_fontfamily() == font_list
        
        plt.close(fig)
