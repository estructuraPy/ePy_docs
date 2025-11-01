"""Tests for show_figure parameter in tables."""
import pytest
import pandas as pd
from ePy_docs.writers import DocumentWriter


class TestShowFigureParameter:
    """Test show_figure parameter for tables."""
    
    def test_table_show_figure_uses_quarto_directives(self):
        """Test that show_figure=True uses same format as figures."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        writer = DocumentWriter()
        writer.add_table(df, title="Test Table", show_figure=True)
        
        content = ''.join(writer.content_buffer)
        
        # Should have markdown caption (same format as figures)
        assert '**Tabla 1:** Test Table' in content
        # Should have reference ID
        assert '{#tbl-1}' in content
        # Should have Python code block
        assert '```{python}' in content
        # Should hide code by default
        assert '#| echo: false' in content
        # Should NOT use Quarto tbl-cap directive
        assert '#| tbl-cap:' not in content
        
    def test_table_without_show_figure_has_markdown_caption(self):
        """Test that show_figure=False uses markdown caption with image."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        writer = DocumentWriter()
        writer.add_table(df, title="Test Table", show_figure=False)
        
        content = ''.join(writer.content_buffer)
        
        # Should have markdown caption with image reference
        assert '**Tabla 1:**' in content
        assert 'Test Table' in content
        assert '.png' in content
        assert '{#tbl-1}' in content
        # Should NOT have Python code
        assert '```{python}' not in content
        
    def test_split_table_show_figure_no_duplicate_captions(self):
        """Test split tables don't have duplicate captions."""
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        
        writer = DocumentWriter()
        writer.add_table(df, title="Split Table", max_rows_per_table=4, show_figure=True)
        
        content = ''.join(writer.content_buffer)
        
        # Count caption occurrences for first part
        caption_count = content.count('Split Table - Parte 1/3')
        # Should appear only once (in markdown caption, not in Quarto directive)
        assert caption_count == 1, f"Caption appears {caption_count} times, expected 1"
        
        # Verify format matches figures
        assert '**Tabla 1:** Split Table - Parte 1/3' in content
        assert '{#tbl-1}' in content
        
    def test_colored_table_show_figure_format(self):
        """Test colored table with show_figure has correct format."""
        df = pd.DataFrame({
            'Metric': ['A', 'B', 'C'],
            'Value': [10, 20, 30]
        })
        
        writer = DocumentWriter()
        writer.add_colored_table(df, title="Colored Test", show_figure=True)
        
        content = ''.join(writer.content_buffer)
        
        # Should have Python code block
        assert '```{python}' in content
        # Should have Image display code (not raw DataFrame)
        assert 'from IPython.display import Image, display' in content
        assert 'display(Image(filename=' in content
        # Should have markdown caption (not Quarto directive)
        assert '**Tabla 1:** Colored Test' in content
        assert '{#tbl-1}' in content
        # Should NOT have Quarto tbl-cap directive
        assert '#| tbl-cap:' not in content
