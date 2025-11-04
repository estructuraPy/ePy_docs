"""Tests for font system in images and plots."""

import pytest
import matplotlib.pyplot as plt
from ePy_docs.core._images import ImageProcessor


class TestFontSystem:
    """Test font configuration and application."""
    
    @pytest.fixture
    def processor(self):
        """Create ImageProcessor instance."""
        return ImageProcessor()
    
    def test_setup_matplotlib_fonts_classic(self, processor):
        """Test font setup for classic layout."""
        font_list = processor.setup_matplotlib_fonts('classic')
        
        assert isinstance(font_list, list)
        assert len(font_list) > 0
        assert 'DejaVu Sans' in font_list or 'Arial' in font_list
    
    def test_setup_matplotlib_fonts_handwritten(self, processor):
        """Test font setup for handwritten layout."""
        font_list = processor.setup_matplotlib_fonts('handwritten')
        
        assert isinstance(font_list, list)
        assert len(font_list) > 0
        # Should have handwriting font + fallbacks
        assert 'DejaVu Sans' in font_list
    
    def test_apply_fonts_to_plot(self, processor):
        """Test applying fonts to plot axis."""
        fig, ax = plt.subplots()
        ax.set_title("Test Title")
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")
        
        font_list = ['DejaVu Sans', 'Arial']
        processor.apply_fonts_to_plot(ax, font_list)
        
        # Verify fonts were applied
        assert ax.title.get_fontfamily() == font_list
        assert ax.xaxis.label.get_fontfamily() == font_list
        assert ax.yaxis.label.get_fontfamily() == font_list
        
        plt.close(fig)
    
    def test_apply_fonts_to_figure(self, processor):
        """Test applying fonts to entire figure."""
        fig, axes = plt.subplots(2, 1)
        fig.suptitle("Figure Title")
        
        for ax in axes:
            ax.set_title("Subplot")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
        
        font_list = ['DejaVu Sans', 'Arial']
        processor.apply_fonts_to_figure(fig, font_list)
        
        # Verify all axes have fonts applied
        for ax in axes:
            assert ax.title.get_fontfamily() == font_list
        
        plt.close(fig)
    
    def test_font_fallback_system(self, processor):
        """Test that fallback fonts are included."""
        font_list = processor.setup_matplotlib_fonts('handwritten')
        
        # Should have at least primary + fallback + system fallbacks
        assert len(font_list) >= 3
        
        # Last item should be generic fallback
        assert font_list[-1] == 'sans-serif'
    
    def test_extract_font_family_from_layout(self, processor):
        """Test font family extraction from layout data."""
        # Test with direct font_family
        layout_data = {'font_family': 'sans_handwritten'}
        result = processor._extract_font_family_from_layout(layout_data)
        assert result == 'sans_handwritten'
        
        # Test with tables config
        layout_data = {
            'tables': {
                'content_font': {'family': 'serif_technical'}
            }
        }
        result = processor._extract_font_family_from_layout(layout_data)
        assert result == 'serif_technical'
        
        # Test default fallback
        layout_data = {}
        result = processor._extract_font_family_from_layout(layout_data)
        assert result == 'sans_technical'


class TestPlotFontIntegration:
    """Test font application in plot workflow."""
    
    @pytest.fixture
    def processor(self):
        """Create ImageProcessor instance."""
        return ImageProcessor()
    
    def test_add_plot_content_applies_fonts(self, processor, tmp_path):
        """Test that add_plot_content applies fonts before display."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_xlabel("Test σ (epsilon)")
        ax.set_ylabel("Value")
        
        # Call add_plot_content with layout_style
        markdown, counter = processor.add_plot_content(
            fig=fig,
            title="Test Plot",
            caption="Test caption",
            figure_counter=1,
            output_dir=str(tmp_path),
            document_type='report',
            show_figure=False,
            layout_style='handwritten'
        )
        
        # Verify markdown was generated
        assert 'Test Plot' in markdown
        assert 'fig-1' in markdown
        
        # Verify file was created
        output_files = list(tmp_path.glob('*.png'))
        assert len(output_files) == 1
    
    def test_layout_style_none_skips_fonts(self, processor, tmp_path):
        """Test that None layout_style skips font application."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Should not raise error with layout_style=None
        markdown, counter = processor.add_plot_content(
            fig=fig,
            figure_counter=1,
            output_dir=str(tmp_path),
            document_type='report',
            show_figure=False,
            layout_style=None
        )
        
        assert markdown is not None
        plt.close(fig)
