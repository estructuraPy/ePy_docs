"""
Test suite for language configuration and override functionality.
Tests that language settings from layouts can be overridden by constructor parameter.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

from ePy_docs.writers import DocumentWriter
from ePy_docs.core._config import load_layout
from ePy_docs.core._quarto import generate_quarto_yaml


class TestLanguageConfiguration:
    """Test language configuration loading from layouts."""

    def test_creative_layout_has_spanish_default(self):
        """Test that creative layout has Spanish as default language."""
        config = load_layout("creative")
        
        # Check paper configuration
        paper_config = config.get("paper", {})
        project_config = paper_config.get("project", {})
        assert project_config.get("lang") == "es", "Creative layout should have Spanish (es) as default for paper"
        
        # Check report configuration
        report_config = config.get("report", {})
        report_project_config = report_config.get("project", {})
        assert report_project_config.get("lang") == "es", "Creative layout should have Spanish (es) as default for report"

    def test_other_layouts_have_english_default(self):
        """Test that other layouts default to English."""
        layouts_to_test = ["handwritten", "academic", "scientific", "technical"]
        
        for layout_name in layouts_to_test:
            config = load_layout(layout_name)
            
            # Check paper configuration
            paper_config = config.get("paper", {})
            project_config = paper_config.get("project", {})
            assert project_config.get("lang") == "en", f"{layout_name} layout should have English (en) as default for paper"
            
            # Check report configuration
            report_config = config.get("report", {})
            report_project_config = report_config.get("project", {})
            assert report_project_config.get("lang") == "en", f"{layout_name} layout should have English (en) as default for report"


class TestDocumentWriterLanguage:
    """Test DocumentWriter language functionality."""

    def test_writer_without_language_parameter_uses_layout_default(self):
        """Test that DocumentWriter uses layout default language when no parameter provided."""
        # Test with creative layout (Spanish default)
        writer_creative = DocumentWriter("paper", "creative")
        assert writer_creative.language == "es", "Creative layout should default to Spanish"
        
        # Test with handwritten layout (English default)
        writer_handwritten = DocumentWriter("paper", "handwritten")
        assert writer_handwritten.language == "en", "Handwritten layout should default to English"

    def test_writer_with_language_parameter_overrides_layout(self):
        """Test that explicit language parameter overrides layout default."""
        # Override creative (Spanish default) to English
        writer_creative_en = DocumentWriter("paper", "creative", language="en")
        assert writer_creative_en.language == "en", "Language parameter should override layout default"
        
        # Override handwritten (English default) to Spanish
        writer_handwritten_es = DocumentWriter("paper", "handwritten", language="es")
        assert writer_handwritten_es.language == "es", "Language parameter should override layout default"
        
        # Test with French
        writer_french = DocumentWriter("paper", "creative", language="fr")
        assert writer_french.language == "fr", "Should support other languages like French"

    def test_writer_with_language_parameter_different_document_types(self):
        """Test language parameter works with different document types."""
        # Test with paper
        writer_paper = DocumentWriter("paper", "creative", language="en")
        assert writer_paper.language == "en", "Language override should work with paper document type"
        
        # Test with report
        writer_report = DocumentWriter("report", "creative", language="en")
        assert writer_report.language == "en", "Language override should work with report document type"

    def test_writer_properties_access(self):
        """Test that language is accessible as a property."""
        writer = DocumentWriter("paper", "creative", language="fr")
        
        # Test all properties work
        assert writer.document_type == "paper"
        assert writer.layout_style == "creative"
        assert writer.language == "fr"
        assert isinstance(writer.config, dict)
        assert isinstance(writer.output_dir, str)


class TestQuartoYAMLLanguageIntegration:
    """Test language integration in Quarto YAML generation."""

    def test_generate_quarto_yaml_includes_language(self):
        """Test that generate_quarto_yaml includes language in output."""
        yaml_config = generate_quarto_yaml(
            title="Test Document",
            layout_name="creative",
            document_type="paper",
            language="es"
        )
        
        assert "lang" in yaml_config, "YAML config should include language"
        assert yaml_config["lang"] == "es", "YAML config should have correct language"

    def test_generate_quarto_yaml_different_languages(self):
        """Test YAML generation with different languages."""
        languages = ["en", "es", "fr", "de", "it", "pt"]
        
        for lang in languages:
            yaml_config = generate_quarto_yaml(
                title="Test Document",
                layout_name="handwritten",
                document_type="paper",
                language=lang
            )
            
            assert yaml_config["lang"] == lang, f"Should support {lang} language"

    def test_generate_quarto_yaml_default_language(self):
        """Test YAML generation with default language parameter."""
        yaml_config = generate_quarto_yaml(
            title="Test Document",
            layout_name="handwritten",
            document_type="paper"
            # No language parameter - should default to 'en'
        )
        
        assert yaml_config["lang"] == "en", "Should default to English when no language specified"


class TestEndToEndLanguageWorkflow:
    """Test complete language workflow from constructor to document generation."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_spanish_document_generation(self):
        """Test complete workflow with Spanish language."""
        writer = DocumentWriter("paper", "creative", language="es")
        
        # Add some content
        writer.add_h1("Título del Documento")
        writer.add_text("Este es un documento en español.")
        
        # Generate document
        result = writer.generate(
            markdown=True,
            html=False,
            pdf=False,
            qmd=True,
            output_filename="documento_español"
        )
        
        # Verify generation succeeded
        assert isinstance(result, dict), "Should return result dictionary"
        assert "qmd" in result, "Should generate QMD file"
        
        # Check QMD content contains language
        if result["qmd"]:
            qmd_path = Path(result["qmd"])
            assert qmd_path.exists(), "QMD file should exist"
            
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "lang: es" in content, "QMD should contain Spanish language setting"

    def test_english_override_on_spanish_layout(self):
        """Test overriding Spanish layout to English."""
        writer = DocumentWriter("paper", "creative", language="en")
        
        # Add content
        writer.add_h1("English Document Title")
        writer.add_text("This is an English document using creative layout.")
        
        # Generate document
        result = writer.generate(
            markdown=True,
            html=False,
            pdf=False,
            qmd=True,
            output_filename="english_creative"
        )
        
        # Check QMD content
        if result["qmd"]:
            qmd_path = Path(result["qmd"])
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "lang: en" in content, "QMD should contain English language setting despite Spanish layout default"

    def test_no_language_parameter_uses_layout_default(self):
        """Test that no language parameter uses layout default."""
        writer = DocumentWriter("paper", "creative")  # No language parameter
        
        writer.add_h1("Documento por Defecto")
        writer.add_text("Usa configuración de idioma del layout.")
        
        result = writer.generate(
            markdown=True,
            html=False,
            pdf=False,
            qmd=True,
            output_filename="default_language"
        )
        
        # Check QMD content uses Spanish (creative layout default)
        if result["qmd"]:
            qmd_path = Path(result["qmd"])
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "lang: es" in content, "Should use creative layout's default Spanish language"


class TestLanguageValidation:
    """Test language parameter validation and edge cases."""

    def test_empty_language_parameter(self):
        """Test behavior with empty language parameter."""
        writer = DocumentWriter("paper", "creative", language="")
        # Empty string should be treated as None and fall back to layout default
        assert writer.language == "es", "Empty language should fall back to layout default"

    def test_none_language_parameter(self):
        """Test behavior with None language parameter."""
        writer = DocumentWriter("paper", "creative", language=None)
        assert writer.language == "es", "None language should fall back to layout default"

    def test_unsupported_layout_language_fallback(self):
        """Test fallback when layout doesn't have language config."""
        # Create a mock scenario - this is more for robustness
        writer = DocumentWriter("paper", "handwritten", language="zh")
        assert writer.language == "zh", "Should accept any language code provided by user"

    def test_case_sensitivity_language_codes(self):
        """Test that language codes are case-sensitive."""
        writer_lower = DocumentWriter("paper", "creative", language="es")
        writer_upper = DocumentWriter("paper", "creative", language="ES")
        
        assert writer_lower.language == "es", "Lowercase language code should be preserved"
        assert writer_upper.language == "ES", "Uppercase language code should be preserved"


@pytest.mark.parametrize("document_type,layout,expected_default", [
    ("paper", "creative", "es"),
    ("report", "creative", "es"),
    ("paper", "handwritten", "en"),
    ("report", "handwritten", "en"),
    ("paper", "academic", "en"),
    ("report", "academic", "en"),
])
def test_document_type_layout_language_combinations(document_type, layout, expected_default):
    """Test various combinations of document types and layouts."""
    writer = DocumentWriter(document_type, layout)
    assert writer.language == expected_default, f"{document_type}/{layout} should default to {expected_default}"


@pytest.mark.parametrize("override_language", ["en", "es", "fr", "de", "it", "pt", "ja", "zh"])
def test_language_override_support(override_language):
    """Test that various language codes can be used as overrides."""
    writer = DocumentWriter("paper", "creative", language=override_language)
    assert writer.language == override_language, f"Should support {override_language} language override"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])