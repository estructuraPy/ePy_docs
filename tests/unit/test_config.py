"""
Unit tests for ePy_docs configuration system.
Tests configuration loading, validation, and defaults.
"""

import pytest
from pathlib import Path
from ePy_docs.writers import DocumentWriter


class TestBasicConfiguration:
    """Test basic configuration functionality."""
    
    def test_writer_initialization(self):
        """Test that writers can be initialized with different configurations."""
        # Test different document types
        report_writer = DocumentWriter("report")
        paper_writer = DocumentWriter("paper")
        
        # Test different layout styles
        professional_writer = DocumentWriter("report", layout_style="professional")
        minimal_writer = DocumentWriter("report", layout_style="minimal")
        
        # Test that they're all different instances
        assert report_writer is not paper_writer
        assert professional_writer is not minimal_writer
    
    def test_basic_content_operations(self):
        """Test that basic content operations work correctly."""
        writer = DocumentWriter("report")
        
        # Test adding content
        writer.add_text("Test content")
        content = writer.get_content()
        
        # Verify content was added
        assert "Test content" in content
        assert len(content) > 0


class TestLayoutStyles:
    """Test layout style functionality."""
    
    def test_different_layout_styles(self):
        """Test that different layout styles can be initialized."""
        styles = ['professional', 'creative', 'minimal', 'handwritten']
        
        for style in styles:
            writer = DocumentWriter("report", layout_style=style)
            # Test that basic operations work
            writer.add_text(f"Test content for {style}")
            content = writer.get_content()
            assert f"Test content for {style}" in content


class TestDocumentTypes:
    """Test document type functionality."""
    
    def test_different_document_types(self):
        """Test that different document types can be initialized."""
        types = ['report', 'paper']
        
        for doc_type in types:
            writer = DocumentWriter(doc_type)
            # Test that basic operations work
            writer.add_text(f"Test content for {doc_type}")
            content = writer.get_content()
            assert f"Test content for {doc_type}" in content
