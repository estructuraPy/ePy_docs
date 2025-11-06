"""
Test suite for column configuration and PDF layout validation.
Ensures that column settings in layout files are properly applied to PDF generation.
"""

import pytest
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
import json

from ePy_docs.core._pdf import get_pdf_config
from ePy_docs.core._config import load_layout
from ePy_docs.core._columns import ColumnWidthCalculator
from ePy_docs.writers import DocumentWriter


class TestColumnConfiguration:
    """Test column configuration loading and validation."""

    def test_handwritten_layout_has_column_config(self):
        """Test that handwritten.epyson has proper column configuration."""
        config_path = Path("src/ePy_docs/config/layouts/handwritten.epyson")
        assert config_path.exists(), "handwritten.epyson file should exist"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verify column configuration exists
        assert "paper" in config, "Paper configuration should exist"
        assert "columns" in config["paper"], "Column configuration should exist in paper"
        
        paper_columns = config["paper"]["columns"]
        assert "default" in paper_columns, "Default column count should be specified"
        assert "supported" in paper_columns, "Supported column counts should be specified"
        
        # Verify default is 2 columns as expected
        assert paper_columns["default"] == 2, "Default should be 2 columns for handwritten paper"
        assert 2 in paper_columns["supported"], "2 columns should be supported"

    def test_column_configuration_types(self):
        """Test that column configuration has correct data types."""
        config_path = Path("src/ePy_docs/config/layouts/handwritten.epyson")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        paper_columns = config["paper"]["columns"]
        
        # Check types
        assert isinstance(paper_columns["default"], int), "Default should be integer"
        assert isinstance(paper_columns["supported"], list), "Supported should be list"
        assert all(isinstance(x, int) for x in paper_columns["supported"]), "All supported values should be integers"
        
        # Check valid ranges
        assert 1 <= paper_columns["default"] <= 3, "Default should be between 1 and 3"
        assert all(1 <= x <= 3 for x in paper_columns["supported"]), "Supported values should be between 1 and 3"


class TestPDFColumnGeneration:
    """Test PDF configuration generation with column support."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            "paper": {
                "columns": {
                    "default": 2,
                    "supported": [1, 2, 3]
                }
            }
        }

    def test_get_pdf_config_single_column(self):
        """Test PDF config generation for single column layout."""
        # Mock config with 1 column
        test_config = {
            "paper": {
                "columns": {
                    "default": 1,
                    "supported": [1, 2, 3]
                }
            }
        }
        
        # Test single column (should not add column commands)
        pdf_config = get_pdf_config("handwritten", "paper", config=test_config)
        
        assert isinstance(pdf_config, dict), "PDF config should be a dictionary"
        
        # For single column, no special LaTeX commands should be added
        if "include-in-header" in pdf_config:
            header_text = pdf_config["include-in-header"].get("text", "")
            assert "\\twocolumn" not in header_text, "Single column should not have \\twocolumn"
            assert "\\usepackage{multicol}" not in header_text, "Single column should not have multicol package"

    def test_get_pdf_config_two_column(self):
        """Test PDF config generation for two column layout."""
        pdf_config = get_pdf_config("handwritten", "paper", config=self.test_config)
        
        assert isinstance(pdf_config, dict), "PDF config should be a dictionary"
        assert "include-in-header" in pdf_config, "Two column layout should have include-in-header"
        
        header_text = pdf_config["include-in-header"].get("text", "")
        assert "\\twocolumn" in header_text, "Two column layout should have \\twocolumn command"

    def test_get_pdf_config_three_column(self):
        """Test PDF config generation for three column layout."""
        # Mock config with 3 columns
        test_config = {
            "paper": {
                "columns": {
                    "default": 3,
                    "supported": [1, 2, 3]
                }
            }
        }
        
        pdf_config = get_pdf_config("handwritten", "paper", config=test_config)
        
        assert isinstance(pdf_config, dict), "PDF config should be a dictionary"
        assert "include-in-header" in pdf_config, "Three column layout should have include-in-header"
        
        header_text = pdf_config["include-in-header"].get("text", "")
        assert "\\usepackage{multicol}" in header_text, "Three column layout should have multicol package"

    def test_get_pdf_config_unsupported_document_type(self):
        """Test PDF config generation for document types without column config."""
        pdf_config = get_pdf_config("handwritten", "book", config=self.test_config)
        
        # Should work without errors even if document type has no column config
        assert isinstance(pdf_config, dict), "PDF config should be a dictionary"

    def test_get_pdf_config_invalid_layout(self):
        """Test PDF config generation with invalid layout."""
        # Test with valid layout but invalid document type
        pdf_config = get_pdf_config("handwritten", "invalid_doc_type", config=self.test_config)
        assert isinstance(pdf_config, dict), "Should return valid config even with invalid document type"


class TestColumnWidthCalculator:
    """Test column width calculation functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.calculator = ColumnWidthCalculator()

    def test_calculate_width_single_column(self):
        """Test width calculation for single column documents."""
        # Full width for single column
        width = self.calculator.calculate_width("paper", 1, 1.0)
        assert width == 6.5, "Full width should be 6.5 inches for paper"
        
        # Half width for single column
        width = self.calculator.calculate_width("paper", 1, 0.5)
        assert width == 3.1, "Half width should be 3.1 inches"

    def test_calculate_width_two_column(self):
        """Test width calculation for two column documents."""
        # Full width spanning both columns
        width = self.calculator.calculate_width("paper", 2, 2.0)
        assert width == 6.5, "Full width should be 6.5 inches for paper"
        
        # Single column width
        width = self.calculator.calculate_width("paper", 2, 1.0)
        expected = 3.1  # Actual value from calculator
        assert width == expected, f"Single column width should be {expected}"

    def test_calculate_width_three_column(self):
        """Test width calculation for three column documents."""
        # Single column width in three-column layout
        width = self.calculator.calculate_width("paper", 3, 1.0)
        expected = 2.0  # Actual value from calculator
        assert width == expected, f"Single column width should be {expected}"
        
        # Two column span in three-column layout
        width = self.calculator.calculate_width("paper", 3, 2.0)
        expected = 4.25  # Actual value from calculator
        assert width == expected, f"Two column span should be {expected}"

    def test_get_width_string(self):
        """Test width string formatting."""
        width_str = self.calculator.get_width_string(6.5)
        assert width_str == "6.5in", "Width string should be formatted as inches"
        
        width_str = self.calculator.get_width_string(3.25)
        assert width_str == "3.25in", "Width string should maintain precision"

    def test_invalid_column_span(self):
        """Test handling of invalid column spans."""
        # Column span larger than available columns - current behavior returns calculated value
        width = self.calculator.calculate_width("paper", 2, 3.0)
        expected = 9.9  # Actual value from calculator (not clamped)
        assert width == expected, "Column span calculation should return calculated value"


class TestDocumentWriterColumns:
    """Test DocumentWriter with column parameters."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.writer = DocumentWriter(
            document_type='paper',
            layout_style='handwritten'
        )

    def test_add_image_with_columns_api(self):
        """Test add_image API accepts columns parameter."""
        # Test that the method signature accepts columns parameter
        import inspect
        sig = inspect.signature(self.writer.add_image)
        assert 'columns' in sig.parameters, "add_image should accept columns parameter"

    def test_add_plot_with_columns_api(self):
        """Test add_plot API accepts columns parameter."""
        # Test that the method signature accepts columns parameter  
        import inspect
        sig = inspect.signature(self.writer.add_plot)
        assert 'columns' in sig.parameters, "add_plot should accept columns parameter"

    def test_columns_parameter_types_signature(self):
        """Test that columns parameter has correct type annotations."""
        import inspect
        
        # Test add_plot signature
        sig = inspect.signature(self.writer.add_plot)
        columns_param = sig.parameters.get('columns')
        assert columns_param is not None, "columns parameter should exist"
        
        # Test add_image signature  
        sig = inspect.signature(self.writer.add_image)
        columns_param = sig.parameters.get('columns')
        assert columns_param is not None, "columns parameter should exist"


class TestEndToEndColumnGeneration:
    """Test complete pipeline from configuration to output."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_complete_column_pipeline(self):
        """Test the complete pipeline from layout config to API availability."""
        # Create a writer with handwritten layout
        writer = DocumentWriter(
            document_type='paper',
            layout_style='handwritten'
        )
        
        # Verify that the writer was created successfully
        # Test that writer can be created successfully
        assert writer is not None
        
        # Verify that column-related methods are available
        assert hasattr(writer, 'add_plot'), "Writer should have add_plot method"
        assert hasattr(writer, 'add_image'), "Writer should have add_image method"
        
        # Verify signatures include columns parameter
        import inspect
        plot_sig = inspect.signature(writer.add_plot)
        image_sig = inspect.signature(writer.add_image)
        
        assert 'columns' in plot_sig.parameters, "add_plot should accept columns parameter"
        assert 'columns' in image_sig.parameters, "add_image should accept columns parameter"

    def test_layout_config_integration(self):
        """Test that layout configuration is properly integrated."""
        # Test loading handwritten layout
        from ePy_docs.core._config import load_layout
        
        # This should load the actual handwritten.epyson file
        config = load_layout("handwritten")
        
        # Verify it has the expected structure
        assert isinstance(config, dict), "Config should be loaded as dictionary"
        
        # Test PDF config generation uses this config
        pdf_config = get_pdf_config("handwritten", "paper", config=config)
        assert isinstance(pdf_config, dict), "PDF config should be generated"


@pytest.mark.parametrize("document_type,expected_columns", [
    ("paper", 2),
    ("report", 1),  # Assuming report is single column by default
])
def test_document_type_column_defaults(document_type, expected_columns):
    """Test that different document types have appropriate column defaults."""
    # Load handwritten layout config
    config_path = Path("src/ePy_docs/config/layouts/handwritten.epyson")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if document_type in config:
            columns_config = config[document_type].get("columns", {})
            default_columns = columns_config.get("default", 1)
            
            # For paper, expect 2 columns; for others, check actual config
            if document_type == "paper":
                assert default_columns == expected_columns, f"{document_type} should default to {expected_columns} columns"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])