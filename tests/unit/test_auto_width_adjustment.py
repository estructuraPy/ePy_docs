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
        """Test that plots automatically adjust to creative layout (Spanish, 2 columns for paper)."""
        # Create writer with creative layout (should have 2 columns for paper)
        writer = DocumentWriter("paper", "creative", language="es")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot without specifying columns (should auto-adjust)
        writer.add_plot(fig, title="Auto-width Plot", caption="Should span full width")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain width for 2-column layout (full span = 6.5in)
        assert "width=6.5in" in content, "Plot should auto-adjust to full width for 2-column layout"
        
    def test_plot_auto_width_handwritten_layout(self):
        """Test that plots automatically adjust to handwritten layout (English, 2 columns for paper)."""
        # Create writer with handwritten layout (should have 2 columns for paper)
        writer = DocumentWriter("paper", "handwritten")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.cos(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot without specifying columns (should auto-adjust)
        writer.add_plot(fig, title="Auto-width Plot", caption="Should span full width")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain width for 2-column layout (full span = 6.5in)
        assert "width=6.5in" in content, "Plot should auto-adjust to full width for 2-column layout"
        
    def test_plot_auto_width_report_document_type(self):
        """Test that plots automatically adjust for report document type."""
        # Create writer with report document type (typically 1 column)
        writer = DocumentWriter("report", "creative")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x) * np.cos(x)
        ax.plot(x, y)
        ax.set_title("Test Plot Report")
        
        # Add plot without specifying columns (should auto-adjust)
        writer.add_plot(fig, title="Auto-width Plot Report", caption="Should span full width")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain width appropriate for single column (6.5in)
        assert "width=6.5in" in content, "Plot should auto-adjust to appropriate width for report"
        
    def test_plot_manual_columns_override_auto(self):
        """Test that manual columns parameter overrides auto-adjustment."""
        # Create writer with creative layout
        writer = DocumentWriter("paper", "creative")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot WITH columns specified (should override auto-adjustment)
        writer.add_plot(fig, title="Manual width Plot", caption="Should use manual width", columns=1.0)
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain width for single column (3.1in, not 6.5in)
        assert "width=3.1in" in content, "Manual columns parameter should override auto-adjustment"
        assert "width=6.5in" not in content, "Should not use auto-adjustment width when columns specified"
        
    def test_image_auto_width_adjustment(self):
        """Test that images automatically adjust width when no width specified."""
        # Create a temporary test image
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Image")
        
        temp_img_path = Path(self.temp_dir) / "test_image.png"
        fig.savefig(temp_img_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Create writer
        writer = DocumentWriter("paper", "creative")
        
        # Add image without specifying width (should auto-adjust)
        writer.add_image(str(temp_img_path), caption="Auto-width image")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain auto-calculated width
        assert "width=6.5in" in content, "Image should auto-adjust to layout width"
        
    def test_image_manual_width_override_auto(self):
        """Test that manual width parameter overrides auto-adjustment for images."""
        # Create a temporary test image
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Image")
        
        temp_img_path = Path(self.temp_dir) / "test_image.png"
        fig.savefig(temp_img_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Create writer
        writer = DocumentWriter("paper", "creative")
        
        # Add image WITH width specified (should override auto-adjustment)
        writer.add_image(str(temp_img_path), caption="Manual width image", width="80%")
        
        # Generate QMD to check the width
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain manual width, not auto-calculated
        assert "width=80%" in content, "Manual width should override auto-adjustment"
        assert "width=6.5in" not in content, "Should not use auto-adjustment when width specified"


class TestAutoWidthIntegration:
    """Test integration of auto-width with other features."""
    
    def test_auto_width_with_language_parameter(self):
        """Test that auto-width works correctly with language parameter."""
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
        
        # Add plot (should auto-adjust width regardless of language)
        writer.add_plot(fig, title="Auto-width with Language", caption="Should span full width")
        
        # Generate QMD
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain correct language AND auto-width
        assert "lang: en" in content, "Should have correct language"
        assert "width=6.5in" in content, "Should auto-adjust width regardless of language"
        
    def test_mixed_manual_and_auto_width(self):
        """Test document with both manual and auto-width plots."""
        writer = DocumentWriter("paper", "creative")
        
        # Add auto-width plot
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot([1, 2, 3], [1, 4, 2])
        ax1.set_title("Auto Plot")
        writer.add_plot(fig1, title="Auto-width Plot", caption="Should span full width")
        
        # Add manual-width plot
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot([1, 2, 3], [2, 3, 1])
        ax2.set_title("Manual Plot")
        writer.add_plot(fig2, title="Manual-width Plot", caption="Should use single column", columns=1.0)
        
        # Generate QMD
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain both widths
        assert "width=6.5in" in content, "Should have auto-width plot"
        assert "width=3.1in" in content, "Should have manual-width plot"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])