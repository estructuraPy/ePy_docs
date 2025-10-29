"""
Test suite for image and plot handling functionality.

This module tests the image processing and matplotlib plot integration
capabilities of ePy_docs.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ePy_docs.writers import DocumentWriter


class TestImageOperations:
    """Tests for add_image() method."""
    
    def test_add_image_basic(self, temp_writer):
        """Test adding a basic image to the document."""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img_path = f.name
            f.write(b'fake image data')
        
        try:
            result = temp_writer.add_image(img_path, caption="Test image")
            
            # Verify method chaining
            assert result is temp_writer
            
            # Verify content was added
            content = temp_writer.get_content()
            assert len(content) > 0
            assert 'Test image' in content
            
            # Verify figure counter incremented
            assert temp_writer.figure_counter > 0
        finally:
            os.unlink(img_path)
    
    def test_add_image_with_width(self, temp_writer):
        """Test adding image with custom width."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            img_path = f.name
            f.write(b'fake jpeg data')
        
        try:
            temp_writer.add_image(img_path, caption="Wide image", width="80%")
            
            content = temp_writer.get_content()
            assert 'Wide image' in content
        finally:
            os.unlink(img_path)
    
    def test_add_image_nonexistent_file(self, temp_writer):
        """Test adding image with non-existent file path."""
        # Validation now raises FileNotFoundError for missing files
        fake_path = "nonexistent_image.png"
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            temp_writer.add_image(fake_path, caption="Missing image")
    
    def test_add_image_method_chaining(self, temp_writer):
        """Test that add_image supports method chaining."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img_path = f.name
            f.write(b'data')
        
        try:
            result = temp_writer.add_h2("Images Section") \
                                .add_content("Here are some images:") \
                                .add_image(img_path, caption="First image") \
                                .add_content("Description below image")
            
            assert result is temp_writer
            content = temp_writer.get_content()
            assert "Images Section" in content
            assert "First image" in content
        finally:
            os.unlink(img_path)


class TestPlotOperations:
    """Tests for matplotlib plot integration."""
    
    @pytest.mark.skip(reason="add_plot requires matplotlib figure, needs ePy_files.saver")
    def test_add_plot_basic(self, temp_writer):
        """Test adding matplotlib plot to document."""
        import matplotlib.pyplot as plt
        
        # Create a simple plot
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_title("Test Plot")
        
        result = temp_writer.add_plot(fig, caption="Sample plot")
        plt.close(fig)
        
        assert result is temp_writer
        assert temp_writer.figure_counter > 0
    
    @pytest.mark.skip(reason="add_plot implementation pending")
    def test_add_plot_with_title(self, temp_writer):
        """Test adding plot with custom title."""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [2, 4, 6])
        
        result = temp_writer.add_plot(fig, title="Linear Growth", caption="Growth over time")
        plt.close(fig)
        
        content = temp_writer.get_content()
        assert "Linear Growth" in content or "Growth over time" in content
    
    @pytest.mark.skip(reason="add_plot implementation pending")
    def test_add_plot_method_chaining(self, temp_writer):
        """Test plot addition with method chaining."""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [3, 6, 9])
        
        result = temp_writer.add_h2("Results") \
                            .add_content("Analysis results:") \
                            .add_plot(fig, caption="Data visualization") \
                            .add_content("As shown above...")
        
        plt.close(fig)
        assert result is temp_writer


class TestFigureCounter:
    """Tests for figure counter management."""
    
    def test_figure_counter_initialization(self, temp_writer):
        """Test that figure counter starts at 0."""
        assert temp_writer.figure_counter == 0
    
    def test_figure_counter_increments_with_images(self, temp_writer):
        """Test that figure counter increments when adding images."""
        initial_count = temp_writer.figure_counter
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img_path = f.name
            f.write(b'data')
        
        try:
            temp_writer.add_image(img_path, caption="Image 1")
            assert temp_writer.figure_counter == initial_count + 1
            
            temp_writer.add_image(img_path, caption="Image 2")
            assert temp_writer.figure_counter == initial_count + 2
        finally:
            os.unlink(img_path)
    
    def test_figure_counter_independent_of_tables(self, temp_writer):
        """Test that figure counter is independent of table counter."""
        import pandas as pd
        
        # Add a table
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        temp_writer.add_table(df, title="Table 1")
        
        initial_figure_count = temp_writer.figure_counter
        
        # Add an image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img_path = f.name
            f.write(b'data')
        
        try:
            temp_writer.add_image(img_path, caption="Figure 1")
            
            # Figure counter should increment
            assert temp_writer.figure_counter == initial_figure_count + 1
            # Table counter should be unchanged
            assert temp_writer.table_counter >= 1
        finally:
            os.unlink(img_path)


class TestImagePathHandling:
    """Tests for image path processing."""
    
    def test_absolute_path(self, temp_writer):
        """Test handling of absolute image paths."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            abs_path = os.path.abspath(f.name)
            f.write(b'data')
        
        try:
            temp_writer.add_image(abs_path, caption="Absolute path image")
            content = temp_writer.get_content()
            assert "Absolute path image" in content
        finally:
            os.unlink(abs_path)
    
    def test_relative_path(self, temp_writer):
        """Test handling of relative image paths."""
        # Create temporary image with relative path reference
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir='.') as f:
            rel_path = os.path.basename(f.name)
            f.write(b'data')
        
        try:
            temp_writer.add_image(rel_path, caption="Relative path image")
            content = temp_writer.get_content()
            assert "Relative path image" in content
        finally:
            os.unlink(rel_path)
    
    def test_path_with_spaces(self, temp_writer):
        """Test handling of paths with spaces."""
        with tempfile.NamedTemporaryFile(suffix=' test image.png', delete=False) as f:
            path_with_spaces = f.name
            f.write(b'data')
        
        try:
            temp_writer.add_image(path_with_spaces, caption="Spaced path image")
            content = temp_writer.get_content()
            assert "Spaced path image" in content
        finally:
            os.unlink(path_with_spaces)


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
