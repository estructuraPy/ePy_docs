"""
Test column_span direction for images and plots - ensures right overflow only.
"""

import pytest
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from ePy_docs.writers import DocumentWriter


class TestColumnSpanDirection:
    """Test that column_span expands to the right, not left."""
    
    def test_plot_column_span_uses_right_direction(self):
        """Test that plots with partial column_span use column-body-outset-right class."""
        # Create writer with 3-column layout so we can test partial span
        writer = DocumentWriter("paper", "professional", columns=3)
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Test Plot")
        
        # Add plot with column_span=2 (should span 2 of 3 columns)
        writer.add_plot(fig, title="Multi-column Plot", caption="Should use right overflow", column_span=2)
        
        # Generate QMD to check the class
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should use column-body-outset-right, NOT column-body-outset
        assert ".column-body-outset-right" in content, "Plot should use column-body-outset-right class"
        assert ".column-body-outset}" not in content, "Plot should NOT use plain column-body-outset class"
        
    def test_image_column_span_uses_right_direction(self):
        """Test that images with partial column_span use column-body-outset-right class."""
        # Create writer with 3-column layout so we can test partial span
        writer = DocumentWriter("paper", "scientific", columns=3)
        
        # Create a temporary test image
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([1, 2, 3], [1, 2, 3])
            fig.savefig(tmp_path)
            plt.close(fig)
            
        try:
            # Add image with column_span=2 (2 of 3 columns)
            writer.add_image(tmp_path, caption="Multi-column Image", column_span=2)
            
            # Generate QMD to check the class
            result = writer.generate(html=False, pdf=False, qmd=True)
            qmd_path = result['qmd']
            
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should use column-body-outset-right, NOT column-body-outset
            assert ".column-body-outset-right" in content, "Image should use column-body-outset-right class"
            assert ".column-body-outset}" not in content, "Image should NOT use plain column-body-outset class"
        finally:
            # Cleanup - wait a bit for file handles to be released
            try:
                os.remove(tmp_path)
            except (PermissionError, FileNotFoundError):
                pass  # Ignore cleanup errors on Windows
    
    def test_single_column_span_uses_body_class(self):
        """Test that single column elements use column-body class."""
        writer = DocumentWriter("paper", "professional")  # Use layout that exists
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Add plot with column_span=1 (single column)
        writer.add_plot(fig, title="Single Column Plot", column_span=1)
        
        # Generate QMD to check the class
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should use column-body
        assert ".column-body" in content, "Single column plot should use column-body class"
        assert ".column-body-outset" not in content, "Single column should NOT use outset classes"
        
    def test_full_width_uses_page_class(self):
        """Test that full width elements use column-page class."""
        writer = DocumentWriter("paper", "academic")  # 2 columns
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Add plot with column_span=2 (full width in 2-column layout)
        writer.add_plot(fig, title="Full Width Plot", column_span=2)
        
        # Generate QMD to check the class
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should use column-page for full width
        assert ".column-page" in content, "Full width plot should use column-page class"
        
    def test_plot_without_column_span_defaults_to_body(self):
        """Test that plots without column_span use default column-body class."""
        writer = DocumentWriter("paper", "classic")
        
        # Create a simple plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Add plot without column_span parameter
        writer.add_plot(fig, title="Default Width Plot", caption="No column_span specified")
        
        # Generate QMD to check the class
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should use column-body by default
        assert ".column-body" in content, "Plot without column_span should use column-body class"


class TestColumnSpanIntegration:
    """Integration tests for column_span with different document types."""
    
    def test_column_span_in_report(self):
        """Test column_span works in report document type."""
        writer = DocumentWriter("report", "corporate")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 9])
        
        writer.add_plot(fig, title="Report Plot", column_span=2)
        
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that column class is present
        assert ".column-" in content, "Report should have column class in plot"
    
    def test_column_span_in_book(self):
        """Test column_span works in book document type."""
        writer = DocumentWriter("book", "academic")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 9])
        
        writer.add_plot(fig, title="Book Plot", column_span=1)
        
        result = writer.generate(html=False, pdf=False, qmd=True)
        qmd_path = result['qmd']
        
        with open(qmd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that column class is present
        assert ".column-body" in content, "Book should have column-body class for single column plot"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
