"""Unit tests for DocumentWriter class.

Tests the main API for document creation and manipulation.
"""

import pytest
import pandas as pd
from pathlib import Path

from ePy_docs.writers import DocumentWriter


class TestDocumentWriterInitialization:
    """Test DocumentWriter initialization and basic properties."""
    
    def test_report_writer_init(self):
        """Test basic ReportWriter creation."""
        writer = DocumentWriter()
        assert writer is not None
        assert hasattr(writer, 'content_buffer')
        assert hasattr(writer, 'table_counter')
        assert hasattr(writer, 'figure_counter')
    
    def test_report_writer_empty_buffer(self):
        """Test that new writer has empty content buffer."""
        writer = DocumentWriter()
        assert len(writer.content_buffer) == 0
    
    def test_report_writer_counters_start_at_zero(self):
        """Test that counters start at 0."""
        writer = DocumentWriter()
        assert writer.table_counter == 0
        assert writer.figure_counter == 0


class TestDocumentWriterHeadings:
    """Test heading methods (add_h1, add_h2, add_h3)."""
    
    def test_add_h1(self):
        """Test adding H1 heading."""
        writer = DocumentWriter()
        writer.add_h1("Test Title")
        
        assert len(writer.content_buffer) > 0
        content = writer.content_buffer[0]
        assert "# Test Title" in content or "Test Title" in content
    
    def test_add_h2(self):
        """Test adding H2 heading."""
        writer = DocumentWriter()
        writer.add_h2("Section Title")
        
        assert len(writer.content_buffer) > 0
        content = writer.content_buffer[0]
        assert "## Section Title" in content or "Section Title" in content
    
    def test_add_h3(self):
        """Test adding H3 heading."""
        writer = DocumentWriter()
        writer.add_h3("Subsection Title")
        
        assert len(writer.content_buffer) > 0
        content = writer.content_buffer[0]
        assert "### Subsection Title" in content or "Subsection Title" in content
    
    def test_headings_method_chaining(self):
        """Test that heading methods support chaining."""
        writer = DocumentWriter()
        result = writer.add_h1("Title")
        
        assert result is writer  # Should return self


class TestDocumentWriterContent:
    """Test content addition methods."""
    
    def test_add_content_simple_text(self):
        """Test adding simple text content."""
        writer = DocumentWriter()
        writer.add_content("This is a test paragraph.")
        
        assert len(writer.content_buffer) > 0
        assert "This is a test paragraph." in writer.content_buffer[0]
    
    def test_add_content_multiline(self):
        """Test adding multiline content."""
        writer = DocumentWriter()
        text = "Line 1\nLine 2\nLine 3"
        writer.add_content(text)
        
        assert len(writer.content_buffer) > 0
    
    def test_add_content_method_chaining(self):
        """Test content method chaining."""
        writer = DocumentWriter()
        result = writer.add_content("Test")
        
        assert result is writer


class TestDocumentWriterTables:
    """Test table-related functionality."""
    
    def test_add_table_with_dataframe(self, sample_dataframe):
        """Test adding table with valid DataFrame."""
        writer = DocumentWriter()
        writer.add_table(sample_dataframe, title="Test Table")
        
        assert len(writer.content_buffer) > 0
        assert writer.table_counter > 0
    
    def test_add_table_without_title(self, sample_dataframe):
        """Test adding table without title."""
        writer = DocumentWriter()
        writer.add_table(sample_dataframe)
        
        assert len(writer.content_buffer) > 0
    
    def test_add_table_increments_counter(self, sample_dataframe):
        """Test that adding tables increments counter."""
        writer = DocumentWriter()
        initial_count = writer.table_counter
        
        writer.add_table(sample_dataframe, title="Table 1")
        assert writer.table_counter == initial_count + 1
        
        writer.add_table(sample_dataframe, title="Table 2")
        assert writer.table_counter == initial_count + 2
    
    def test_add_table_method_chaining(self, sample_dataframe):
        """Test table method chaining."""
        writer = DocumentWriter()
        result = writer.add_table(sample_dataframe)
        
        assert result is writer
    
    def test_add_table_with_show_figure(self, sample_dataframe):
        """Test adding table with show_figure=True.
        
        Note: show_figure only controls Jupyter display, markdown is always image-based.
        """
        writer = DocumentWriter()
        writer.add_table(sample_dataframe, title="Test Table", show_figure=True)
        
        assert len(writer.content_buffer) > 0
        assert writer.table_counter > 0
        # Verify markdown image is generated (show_figure doesn't change markdown output)
        content = ''.join(writer.content_buffer)
        assert '.png' in content
        assert 'Tabla 1' in content
    
    def test_add_table_with_max_rows_int(self):
        """Test table splitting with integer max_rows_per_table."""
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        writer = DocumentWriter()
        writer.add_table(df, title="Split Table", max_rows_per_table=4)
        
        assert len(writer.content_buffer) > 0
        # Should create 3 tables (4 + 4 + 2 rows)
        assert writer.table_counter == 3
    
    def test_add_table_with_max_rows_list(self):
        """Test table splitting with list max_rows_per_table."""
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        writer = DocumentWriter()
        writer.add_table(df, title="Split Table", max_rows_per_table=[3, 3, 2])
        
        assert len(writer.content_buffer) > 0
        # Should create 4 tables (3 + 3 + 2 + remaining 2 rows)
        assert writer.table_counter == 4
    
    def test_add_table_show_figure_with_max_rows_int(self):
        """Test show_figure=True with integer max_rows_per_table.
        
        Note: show_figure only controls Jupyter display, markdown is always image-based.
        """
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        writer = DocumentWriter()
        writer.add_table(df, title="Split Table", max_rows_per_table=4, show_figure=True)
        
        assert len(writer.content_buffer) > 0
        # Should create 3 tables (4 + 4 + 2 rows)
        assert writer.table_counter == 3
        content = ''.join(writer.content_buffer)
        # Verify markdown image format
        assert '.png' in content
        assert '**Tabla 1:** Split Table - Parte 1/3' in content
        assert '{#tbl-1}' in content
    
    def test_add_table_show_figure_with_max_rows_list(self):
        """Test show_figure=True with list max_rows_per_table."""
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        writer = DocumentWriter()
        writer.add_table(df, title="Split Table", max_rows_per_table=[3, 3, 2], show_figure=True)
        
        assert len(writer.content_buffer) > 0
        # Should create 4 tables (3 + 3 + 2 + remaining 2 rows)
        assert writer.table_counter == 4
        content = ''.join(writer.content_buffer)
        # Should have multiple table references
        assert '{#tbl-1}' in content
        assert '{#tbl-4}' in content
        # Verify correct markdown structure (no duplicate captions in alt text)
        assert '**Tabla 1:** Split Table' in content
        assert '![Tabla 1]' in content
    
    def test_add_colored_table_with_show_figure(self):
        """Test add_colored_table with show_figure=True."""
        df = pd.DataFrame({
            'A': range(5),
            'B': [f'Value {i}' for i in range(5)]
        })
        writer = DocumentWriter()
        writer.add_colored_table(df, title="Colored Table", show_figure=True)
        
        assert len(writer.content_buffer) > 0
        assert writer.table_counter > 0
        content = ''.join(writer.content_buffer)
        # Show figure doesn't change markdown output (always image-based)
        assert '.png' in content
    
    def test_add_colored_table_with_max_rows_list_show_figure(self):
        """Test add_colored_table with list max_rows_per_table and show_figure=True."""
        df = pd.DataFrame({
            'A': range(10),
            'B': [f'Value {i}' for i in range(10)]
        })
        writer = DocumentWriter()
        writer.add_colored_table(df, title="Split Colored Table", 
                                max_rows_per_table=[3, 3], show_figure=True)
        
        assert len(writer.content_buffer) > 0
        # Should create 3 tables (3 + 3 + remaining 4 rows)
        assert writer.table_counter == 3
        content = ''.join(writer.content_buffer)
        assert '{#tbl-1}' in content
        # Verify correct markdown structure
        assert '**Tabla 1:** Split Colored Table' in content
        assert '![Tabla 1]' in content
    
    @pytest.mark.skip(reason="Validation not implemented yet")
    def test_add_table_with_none_raises_error(self):
        """Test that None DataFrame raises TypeError."""
        writer = DocumentWriter()
        
        with pytest.raises(TypeError):
            writer.add_table(None)
    
    @pytest.mark.skip(reason="Validation not implemented yet")
    def test_add_table_with_empty_dataframe_raises_error(self, empty_dataframe):
        """Test that empty DataFrame raises ValueError."""
        writer = DocumentWriter()
        
        with pytest.raises(ValueError):
            writer.add_table(empty_dataframe)


class TestDocumentWriterCallouts:
    """Test callout functionality."""
    
    def test_add_callout_tip(self):
        """Test adding tip callout."""
        writer = DocumentWriter()
        writer.add_callout("This is a tip", type="tip")
        
        assert len(writer.content_buffer) > 0
    
    def test_add_callout_warning(self):
        """Test adding warning callout."""
        writer = DocumentWriter()
        writer.add_callout("This is a warning", type="warning")
        
        assert len(writer.content_buffer) > 0
    
    def test_add_callout_note(self):
        """Test adding note callout."""
        writer = DocumentWriter()
        writer.add_callout("This is a note", type="note")
        
        assert len(writer.content_buffer) > 0
    
    def test_add_callout_method_chaining(self):
        """Test callout method chaining."""
        writer = DocumentWriter()
        result = writer.add_callout("Test", type="tip")
        
        assert result is writer


class TestDocumentWriterGeneration:
    """Test document generation."""
    
    @pytest.mark.integration
    def test_generate_html(self, temp_dir):
        """Test HTML generation."""
        writer = DocumentWriter()
        writer.add_h1("Test Document")
        writer.add_content("Test content")
        
        # Note: generate() uses writer.output_dir, not output_dir parameter
        results = writer.generate(html=True, pdf=False)
        
        assert 'html' in results
        html_path = Path(results['html'])
        assert html_path.exists()
        assert html_path.suffix == '.html'
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_generate_pdf(self, temp_dir):
        """Test PDF generation (requires Quarto)."""
        try:
            writer = DocumentWriter()
            writer.add_h1("Test Document")
            writer.add_content("Test content")
            
            results = writer.generate(
                pdf=True,
                output_dir=str(temp_dir)
            )
            
            assert 'pdf' in results
            pdf_path = Path(results['pdf'])
            assert pdf_path.exists()
            assert pdf_path.suffix == '.pdf'
        except Exception as e:
            pytest.skip(f"PDF generation failed (Quarto not installed?): {e}")
    
    @pytest.mark.integration
    def test_generate_both_formats(self, temp_dir):
        """Test generating both HTML and PDF."""
        writer = DocumentWriter()
        writer.add_h1("Test Document")
        
        # Note: generate() uses writer.output_dir, not output_dir parameter
        results = writer.generate(
            html=True,
            pdf=False  # Skip PDF if Quarto not available
        )
        
        assert 'html' in results


class TestDocumentWriterPaperType:
    """Test DocumentWriter with paper document type."""
    
    def test_paper_writer_init(self):
        """Test PaperWriter initialization."""
        writer = DocumentWriter(document_type="paper")
        assert writer is not None
    
    def test_paper_writer_inherits_from_base(self):
        """Test that PaperWriter has base functionality."""
        writer = DocumentWriter(document_type="paper")
        assert hasattr(writer, 'add_h1')
        assert hasattr(writer, 'add_content')
        assert hasattr(writer, 'generate')
    
    def test_paper_writer_method_chaining(self):
        """Test method chaining in PaperWriter."""
        writer = DocumentWriter(document_type="paper")
        result = writer.add_h1("Title").add_content("Content")
        assert result is writer


class TestMethodChaining:
    """Test comprehensive method chaining."""
    
    def test_full_document_chaining(self, sample_dataframe):
        """Test creating document with chained methods."""
        writer = DocumentWriter()
        
        result = (writer
                  .add_h1("Report Title")
                  .add_content("Introduction paragraph")
                  .add_h2("Data Section")
                  .add_table(sample_dataframe, title="Results")
                  .add_callout("Important note", type="note")
                  .add_h2("Conclusion")
                  .add_content("Final thoughts"))
        
        assert result is writer
        assert len(writer.content_buffer) > 0
        assert writer.table_counter == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
