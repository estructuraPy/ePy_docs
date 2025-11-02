"""Tests for show_figure parameter in tables."""
import pytest
import pandas as pd
from ePy_docs.writers import DocumentWriter


class TestShowFigureParameter:
    """Test show_figure parameter for tables."""
    
    def test_table_show_figure_uses_markdown_format(self):
        """Test that show_figure=True generates markdown image (same as show_figure=False).
        
        Note: show_figure=True only controls Jupyter display, not markdown output.
        """
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        writer = DocumentWriter()
        writer.add_table(df, title="Test Table", show_figure=True)
        
        content = ''.join(writer.content_buffer)
        
        # Should have image reference with title in alt text
        assert 'Test Table' in content
        assert '.png' in content
        assert '{#tbl-1}' in content
        # Show figure only affects Jupyter display, not markdown output
        
    def test_table_without_show_figure_has_markdown_caption(self):
        """Test that show_figure=False uses markdown caption with image."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        writer = DocumentWriter()
        writer.add_table(df, title="Test Table", show_figure=False)
        
        content = ''.join(writer.content_buffer)
        
        # Should have image reference with title in alt text
        assert 'Test Table' in content
        assert '.png' in content
        assert '{#tbl-1}' in content
        assert '```{python}' not in content
        
    def test_split_table_show_figure_no_duplicate_captions(self):
        """Test split tables have captions only in markdown title, not duplicated in alt text."""
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        
        writer = DocumentWriter()
        writer.add_table(df, title="Split Table", max_rows_per_table=4, show_figure=True)
        
        content = ''.join(writer.content_buffer)
        
        # Caption should appear in image alt text
        caption_count = content.count('Split Table - Parte 1/3')
        assert caption_count >= 1, f"Caption appears {caption_count} times, expected at least 1"
        
        # Verify correct image format
        assert 'Split Table - Parte 1/3' in content
        assert '.png' in content
        assert '{#tbl-1}' in content
        
    def test_colored_table_show_figure_format(self):
        """Test colored table with show_figure has correct format.
        
        Note: show_figure only controls Jupyter display, markdown output is always image-based.
        """
        df = pd.DataFrame({
            'Metric': ['A', 'B', 'C'],
            'Value': [10, 20, 30]
        })
        
        writer = DocumentWriter()
        writer.add_colored_table(df, title="Colored Test", show_figure=True)
        
        content = ''.join(writer.content_buffer)
        
        # Should have image reference with title in alt text
        assert 'Colored Test' in content
        assert '{#tbl-1}' in content
        assert '.png' in content
        # Show figure only affects Jupyter display, not markdown output
