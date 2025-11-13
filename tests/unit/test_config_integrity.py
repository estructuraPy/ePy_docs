"""
Test suite for configuration integrity.

Ensures that critical configuration paths and functions work correctly
to prevent regressions like missing assets.epyson or broken imports.
"""

import pytest
from pathlib import Path

from ePy_docs.writers import DocumentWriter
from ePy_docs.core._config import get_config_section, load_layout, get_loader
from ePy_docs.core._html import get_html_config, generate_css
from ePy_docs.core._pdf import get_pdf_config


class TestConfigurationIntegrity:
    """Test that all configuration loading paths work correctly."""
    
    def test_get_available_palettes_works(self):
        """Test that get_available_palettes() loads from colors.epyson correctly."""
        palettes = DocumentWriter.get_available_palettes()
        
        assert isinstance(palettes, dict), "Should return dictionary"
        assert len(palettes) > 0, "Should have at least one palette"
        
        # Check that common palettes exist
        expected_palettes = ['professional', 'creative', 'minimal', 'neutrals']
        for palette in expected_palettes:
            assert palette in palettes, f"Palette '{palette}' should exist"
    
    def test_colors_configuration_has_palettes(self):
        """Test that colors.epyson contains palettes section."""
        colors_config = get_config_section('colors')
        
        assert 'palettes' in colors_config, "colors.epyson must have 'palettes' section"
        assert isinstance(colors_config['palettes'], dict), "Palettes must be a dictionary"
        assert len(colors_config['palettes']) > 0, "Must have at least one palette defined"
    
    def test_all_critical_config_sections_load(self):
        """Test that all critical configuration sections can be loaded."""
        # These sections are layout-independent and load from external files
        critical_sections = [
            'colors',
            'tables',
            'text',
            'images',
            'reader',
            'callouts',
            'notes',
            'code'
        ]
        
        for section in critical_sections:
            config = get_config_section(section)
            assert isinstance(config, dict), f"Section '{section}' should return dict"
            assert len(config) > 0, f"Section '{section}' should not be empty"
    
    def test_documents_configuration_loads(self):
        """Test that documents.epyson can be loaded directly."""
        loader = get_loader()
        documents_config = loader.load_external('documents')
        
        assert isinstance(documents_config, dict), "documents should return dict"
        assert 'document_types' in documents_config, "Should have document_types section"
        assert len(documents_config['document_types']) > 0, "Should have at least one document type"
        
        # Verify common document types exist
        expected_types = ['paper', 'report', 'book']
        for doc_type in expected_types:
            assert doc_type in documents_config['document_types'], f"Document type '{doc_type}' should exist"
    
    def test_all_layouts_load_successfully(self):
        """Test that all layout files can be loaded without errors."""
        layouts = [
            'professional', 'creative', 'minimal', 'handwritten',
            'classic', 'scientific', 'technical', 'academic', 'corporate'
        ]
        
        for layout_name in layouts:
            layout = load_layout(layout_name)
            assert isinstance(layout, dict), f"Layout '{layout_name}' should return dict"
            assert 'layout_name' in layout, f"Layout '{layout_name}' should have layout_name key"
            assert layout['layout_name'] == layout_name, f"Layout name should match"
    
    def test_html_config_generation_works(self):
        """Test that get_html_config() generates valid configuration."""
        html_config = get_html_config('professional', 'report')
        
        assert isinstance(html_config, dict), "Should return dictionary"
        assert 'theme' in html_config, "Should have theme"
        assert 'css' in html_config, "Should have css reference"
    
    def test_css_generation_works(self):
        """Test that generate_css() produces valid CSS content."""
        css_content = generate_css('professional')
        
        assert isinstance(css_content, str), "Should return string"
        assert len(css_content) > 0, "Should not be empty"
        assert ':root' in css_content, "Should contain CSS root variables"
        assert '--primary-color' in css_content, "Should contain color variables"
    
    def test_document_types_accessible_from_documents(self):
        """Test that document_types can be loaded from documents.epyson."""
        loader = get_loader()
        
        # This should work without error (loads from documents.epyson)
        doc_types_data = loader.load_external('document_types')
        
        assert isinstance(doc_types_data, dict), "Should return dictionary"
        assert 'document_types' in doc_types_data, "Should have document_types key"


class TestConfigurationFiles:
    """Test that all required configuration files exist."""
    
    def test_all_config_files_exist(self):
        """Test that all configuration .epyson files exist."""
        config_dir = Path(__file__).parent.parent.parent / 'src' / 'ePy_docs' / 'config'
        
        required_files = [
            'colors.epyson',
            'tables.epyson',
            'text.epyson',
            'images.epyson',
            'documents/_index.epyson',
            'reader.epyson',
            'core.epyson',
            'project.epyson',
            'callouts.epyson',
            'notes.epyson',
            'code.epyson'
        ]
        
        for filename in required_files:
            file_path = config_dir / filename
            assert file_path.exists(), f"Configuration file '{filename}' must exist"
            assert file_path.is_file(), f"'{filename}' must be a file"
    
    def test_all_layout_files_exist(self):
        """Test that all layout .epyson files exist."""
        layouts_dir = Path(__file__).parent.parent.parent / 'src' / 'ePy_docs' / 'config' / 'layouts'
        
        required_layouts = [
            'professional.epyson',
            'creative.epyson',
            'minimal.epyson',
            'handwritten.epyson',
            'classic.epyson',
            'scientific.epyson',
            'technical.epyson',
            'academic.epyson',
            'corporate.epyson'
        ]
        
        for filename in required_layouts:
            file_path = layouts_dir / filename
            assert file_path.exists(), f"Layout file '{filename}' must exist"
            assert file_path.is_file(), f"'{filename}' must be a file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
