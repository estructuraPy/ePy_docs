"""
Test auto-adjustment of plot and image widths based on layout column configuration.
"""

import pytest
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from ePy_docs.writers import DocumentWriter


class TestAutoWidthAdjustment:
    """Test automatic width adjustment for plots and images."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def test_plot_auto_width_creative_layout(self):
        """Test that plots use default width when not specified."""
        # Create writer with creative layout
        writer = DocumentWriter("paper", "creative", language="es")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot without specifying columns (should use default width)
        writer.add_plot(fig, title="Auto-width Plot", caption="Should span full width")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain default width (100%)
        assert "width=100%" in content, "Plot should use default width (100%)"
        
    def test_plot_auto_width_handwritten_layout(self):
        """Test that plots use default width when not specified."""
        # Create writer with handwritten layout
        writer = DocumentWriter("paper", "handwritten")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.cos(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot without specifying columns (should use default width)
        writer.add_plot(fig, title="Auto-width Plot", caption="Should span full width")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain default width (100%)
        assert "width=100%" in content, "Plot should use default width (100%)"
        
    def test_plot_auto_width_report_document_type(self):
        """Test that plots use default width for report document type."""
        # Create writer with report document type
        writer = DocumentWriter("report", "creative")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x) * np.cos(x)
        ax.plot(x, y)
        ax.set_title("Test Plot Report")
        
        # Add plot without specifying columns (should use default width)
        writer.add_plot(fig, title="Auto-width Plot Report", caption="Should span full width")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain default width (100%)
        assert "width=100%" in content, "Plot should use default width (100%)"
        
    def test_image_auto_width_adjustment(self):
        """Test that images use default width when not specified."""
        # Create a temporary test image
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Image")
        
        temp_img_path = Path(self.temp_dir) / "test_image.png"
        fig.savefig(temp_img_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Create writer
        writer = DocumentWriter("paper", "creative")
        
        # Add image without specifying width (should use default)
        writer.add_image(str(temp_img_path), caption="Auto-width image")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain default width (100%)
        assert "width=100%" in content, "Image should use default width (100%)"
        
    def test_image_manual_width_override_auto(self):
        """Test that manual width parameter overrides default for images."""
        # Create a temporary test image
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Image")
        
        temp_img_path = Path(self.temp_dir) / "test_image.png"
        fig.savefig(temp_img_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Create writer
        writer = DocumentWriter("paper", "creative")
        
        # Add image WITH width specified (should override default)
        writer.add_image(str(temp_img_path), caption="Manual width image", width="80%")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain manual width, not default
        assert "width=80%" in content, "Manual width should override default"
        assert "width=100%" not in content, "Should not use default when width specified"


class TestAutoWidthIntegration:
    """Test integration of auto-width with other features."""
    
    def test_auto_width_with_language_parameter(self):
        """Test that default width works correctly with language parameter."""
        # Create writer with language override
        writer = DocumentWriter("paper", "creative", language="en")
        
        # Verify language was set
        # Test that writer can be created successfully
        assert writer is not None
        
        # Create a plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot (should use default width regardless of language)
        writer.add_plot(fig, title="Auto-width with Language", caption="Should span full width")
        
        # Generate QMD
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain correct language AND default width
        assert "lang: en" in content, "Should have correct language"
        assert "width=100%" in content, "Should use default width regardless of language"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])