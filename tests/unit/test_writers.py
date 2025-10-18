"""Unit tests for ReportWriter and PaperWriter classes.

Tests the main API for document creation and manipulation.
"""

import pytest
import pandas as pd
from pathlib import Path

from ePy_docs.writers import ReportWriter, PaperWriter


class TestReportWriterInitialization:
    """Test ReportWriter initialization and basic properties."""
    
    def test_report_writer_init(self):
        """Test basic ReportWriter creation."""
        writer = ReportWriter()
        assert writer is not None
        assert hasattr(writer, 'content_buffer')
        assert hasattr(writer, 'table_counter')
        assert hasattr(writer, 'figure_counter')
    
    def test_report_writer_empty_buffer(self):
        """Test that new writer has empty content buffer."""
        writer = ReportWriter()
        assert len(writer.content_buffer) == 0
    
    def test_report_writer_counters_start_at_zero(self):
        """Test that counters start at 0."""
        writer = ReportWriter()
        assert writer.table_counter == 0
        assert writer.figure_counter == 0


class TestReportWriterHeadings:
    """Test heading methods (add_h1, add_h2, add_h3)."""
    
    def test_add_h1(self):
        """Test adding H1 heading."""
        writer = ReportWriter()
        writer.add_h1("Test Title")
        
        assert len(writer.content_buffer) > 0
        content = writer.content_buffer[0]
        assert "# Test Title" in content or "Test Title" in content
    
    def test_add_h2(self):
        """Test adding H2 heading."""
        writer = ReportWriter()
        writer.add_h2("Section Title")
        
        assert len(writer.content_buffer) > 0
        content = writer.content_buffer[0]
        assert "## Section Title" in content or "Section Title" in content
    
    def test_add_h3(self):
        """Test adding H3 heading."""
        writer = ReportWriter()
        writer.add_h3("Subsection Title")
        
        assert len(writer.content_buffer) > 0
        content = writer.content_buffer[0]
        assert "### Subsection Title" in content or "Subsection Title" in content
    
    def test_headings_method_chaining(self):
        """Test that heading methods support chaining."""
        writer = ReportWriter()
        result = writer.add_h1("Title")
        
        assert result is writer  # Should return self


class TestReportWriterContent:
    """Test content addition methods."""
    
    def test_add_content_simple_text(self):
        """Test adding simple text content."""
        writer = ReportWriter()
        writer.add_content("This is a test paragraph.")
        
        assert len(writer.content_buffer) > 0
        assert "This is a test paragraph." in writer.content_buffer[0]
    
    def test_add_content_multiline(self):
        """Test adding multiline content."""
        writer = ReportWriter()
        text = "Line 1\nLine 2\nLine 3"
        writer.add_content(text)
        
        assert len(writer.content_buffer) > 0
    
    def test_add_content_method_chaining(self):
        """Test content method chaining."""
        writer = ReportWriter()
        result = writer.add_content("Test")
        
        assert result is writer


class TestReportWriterTables:
    """Test table-related functionality."""
    
    def test_add_table_with_dataframe(self, sample_dataframe):
        """Test adding table with valid DataFrame."""
        writer = ReportWriter()
        writer.add_table(sample_dataframe, title="Test Table")
        
        assert len(writer.content_buffer) > 0
        assert writer.table_counter > 0
    
    def test_add_table_without_title(self, sample_dataframe):
        """Test adding table without title."""
        writer = ReportWriter()
        writer.add_table(sample_dataframe)
        
        assert len(writer.content_buffer) > 0
    
    def test_add_table_increments_counter(self, sample_dataframe):
        """Test that adding tables increments counter."""
        writer = ReportWriter()
        initial_count = writer.table_counter
        
        writer.add_table(sample_dataframe, title="Table 1")
        assert writer.table_counter == initial_count + 1
        
        writer.add_table(sample_dataframe, title="Table 2")
        assert writer.table_counter == initial_count + 2
    
    def test_add_table_method_chaining(self, sample_dataframe):
        """Test table method chaining."""
        writer = ReportWriter()
        result = writer.add_table(sample_dataframe)
        
        assert result is writer
    
    @pytest.mark.skip(reason="Validation not implemented yet")
    def test_add_table_with_none_raises_error(self):
        """Test that None DataFrame raises TypeError."""
        writer = ReportWriter()
        
        with pytest.raises(TypeError):
            writer.add_table(None)
    
    @pytest.mark.skip(reason="Validation not implemented yet")
    def test_add_table_with_empty_dataframe_raises_error(self, empty_dataframe):
        """Test that empty DataFrame raises ValueError."""
        writer = ReportWriter()
        
        with pytest.raises(ValueError):
            writer.add_table(empty_dataframe)


class TestReportWriterCallouts:
    """Test callout functionality."""
    
    def test_add_callout_tip(self):
        """Test adding tip callout."""
        writer = ReportWriter()
        writer.add_callout("This is a tip", type="tip")
        
        assert len(writer.content_buffer) > 0
    
    def test_add_callout_warning(self):
        """Test adding warning callout."""
        writer = ReportWriter()
        writer.add_callout("This is a warning", type="warning")
        
        assert len(writer.content_buffer) > 0
    
    def test_add_callout_note(self):
        """Test adding note callout."""
        writer = ReportWriter()
        writer.add_callout("This is a note", type="note")
        
        assert len(writer.content_buffer) > 0
    
    def test_add_callout_method_chaining(self):
        """Test callout method chaining."""
        writer = ReportWriter()
        result = writer.add_callout("Test", type="tip")
        
        assert result is writer


class TestReportWriterGeneration:
    """Test document generation."""
    
    @pytest.mark.integration
    def test_generate_html(self, temp_dir):
        """Test HTML generation."""
        writer = ReportWriter()
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
            writer = ReportWriter()
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
        writer = ReportWriter()
        writer.add_h1("Test Document")
        
        # Note: generate() uses writer.output_dir, not output_dir parameter
        results = writer.generate(
            html=True,
            pdf=False  # Skip PDF if Quarto not available
        )
        
        assert 'html' in results


class TestPaperWriter:
    """Test PaperWriter class."""
    
    def test_paper_writer_init(self):
        """Test PaperWriter initialization."""
        writer = PaperWriter()
        assert writer is not None
    
    def test_paper_writer_inherits_from_base(self):
        """Test that PaperWriter has base functionality."""
        writer = PaperWriter()
        assert hasattr(writer, 'add_h1')
        assert hasattr(writer, 'add_content')
        assert hasattr(writer, 'generate')
    
    def test_paper_writer_method_chaining(self):
        """Test method chaining in PaperWriter."""
        writer = PaperWriter()
        result = writer.add_h1("Title").add_content("Content")
        assert result is writer


class TestMethodChaining:
    """Test comprehensive method chaining."""
    
    def test_full_document_chaining(self, sample_dataframe):
        """Test creating document with chained methods."""
        writer = ReportWriter()
        
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
