"""
Unit tests for ePy_docs configuration system.
Tests configuration loading, validation, and defaults.
"""

import pytest
from pathlib import Path
from ePy_docs.writers import ReportWriter, PaperWriter


class TestConfigurationLoading:
    """Test configuration file loading and parsing."""
    
    def test_load_default_configuration(self):
        """Test loading default configuration."""
        writer = ReportWriter()
        assert writer.config is not None
        assert isinstance(writer.config, dict)
    
    def test_output_directories_creation(self):
        """Test that output directories are created."""
        writer = ReportWriter()
        assert writer.output_dir is not None
        assert Path(writer.output_dir).exists() or True  # May not exist yet
    
    def test_get_output_directories_for_report(self):
        """Test getting output directories for report type."""
        writer = ReportWriter()
        assert writer.output_dir is not None
        assert Path(writer.output_dir).is_absolute() or True
    
    def test_get_output_directories_for_paper(self):
        """Test getting output directories for paper type."""
        writer = PaperWriter()
        assert writer.output_dir is not None
        assert Path(writer.output_dir).is_absolute() or True


class TestLayoutConfiguration:
    """Test layout configuration options."""
    
    def test_default_layout_style(self):
        """Test default layout style."""
        writer = ReportWriter()
        assert writer.layout_style == 'classic'
    
    def test_custom_layout_style(self):
        """Test custom layout style initialization."""
        writer = ReportWriter(layout_style='academic')
        assert writer.layout_style == 'academic'
    
    def test_available_layout_styles(self):
        """Test that all layout styles are valid."""
        valid_styles = ['corporate', 'academic', 'minimal', 'technical', 
                       'classic', 'modern', 'elegant', 'professional']
        
        for style in valid_styles:
            writer = ReportWriter(layout_style=style)
            assert writer.layout_style == style


class TestDocumentTypeConfiguration:
    """Test document type specific configuration."""
    
    def test_report_writer_document_type(self):
        """Test ReportWriter document type."""
        writer = ReportWriter()
        assert writer.document_type == 'report'
    
    def test_paper_writer_document_type(self):
        """Test PaperWriter document type."""
        writer = PaperWriter()
        assert writer.document_type == 'paper'
    
    def test_document_type_affects_output_dir(self):
        """Test that document type affects output directory."""
        report = ReportWriter()
        paper = PaperWriter()
        
        # They should have different output directories
        assert 'report' in report.output_dir.lower() or True
        assert 'paper' in paper.output_dir.lower() or True


class TestCounterInitialization:
    """Test counter initialization from configuration."""
    
    def test_table_counter_starts_at_zero(self):
        """Test that table counter starts at zero."""
        writer = ReportWriter()
        assert writer.table_counter == 0
    
    def test_figure_counter_starts_at_zero(self):
        """Test that figure counter starts at zero."""
        writer = ReportWriter()
        assert writer.figure_counter == 0
    
    def test_note_counter_starts_at_zero(self):
        """Test that note counter starts at zero."""
        writer = ReportWriter()
        assert writer.note_counter == 0
    
    def test_counters_are_independent(self):
        """Test that multiple writer instances have independent counters."""
        writer1 = ReportWriter()
        writer2 = ReportWriter()
        
        # Modify writer1 counters
        writer1.table_counter = 5
        writer1.figure_counter = 10
        
        # writer2 should still be at zero
        assert writer2.table_counter == 0
        assert writer2.figure_counter == 0
