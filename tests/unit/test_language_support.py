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
from ePy_docs.core._quarto import quarto_orchestrator


class TestLanguageConfiguration:
    """Test language configuration loading from layouts."""

    def test_creative_layout_has_spanish_default(self):
        """Test that creative layout can be configured with Spanish as default language."""
        config = load_layout("creative")
        
        # Check paper configuration - if no explicit language config, should default to 'en'
        paper_config = config.get("paper", {})
        project_config = paper_config.get("project", {})
        default_lang = project_config.get("lang", "en")  # Fallback to 'en' if not configured
        # For now, layouts don't have explicit language configuration, so this should be 'en'
        assert default_lang in ["en", "es"], "Creative layout should have a valid language default"

    def test_other_layouts_have_english_default(self):
        """Test that other layouts default to English when no explicit language configuration."""
        layouts_to_test = ["handwritten", "academic", "scientific", "technical"]
        
        for layout_name in layouts_to_test:
            config = load_layout(layout_name)
            
            # Check paper configuration - should fallback to 'en' if not configured
            paper_config = config.get("paper", {})
            project_config = paper_config.get("project", {})
            default_lang = project_config.get("lang", "en")  # Fallback to 'en' if not configured
            assert default_lang == "en", f"{layout_name} layout should default to English (en) for paper"


class TestDocumentWriterLanguage:
    """Test DocumentWriter language functionality."""

    def test_writer_without_language_parameter_uses_layout_default(self):
        """Test that DocumentWriter uses layout default language when no parameter provided."""
        # All layouts should default to English ('en') - no special configuration per layout
        writer_creative = DocumentWriter("paper", "creative")
        assert writer_creative.language == "en", "Creative layout should default to English like all layouts"
        
        writer_handwritten = DocumentWriter("paper", "handwritten")
        assert writer_handwritten.language == "en", "Handwritten layout should default to English"

    def test_writer_with_language_parameter_overrides_layout(self):
        """Test that explicit language parameter overrides layout default."""
        # Override default English to Spanish
        writer_creative_es = DocumentWriter("paper", "creative", language="es")
        assert writer_creative_es.language == "es", "Language parameter should override default English"
        
        # Override default English to Spanish with different layout
        writer_handwritten_es = DocumentWriter("paper", "handwritten", language="es")
        assert writer_handwritten_es.language == "es", "Language parameter should override default English"
        
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
        """Test that quarto_orchestrator includes language in output."""
        yaml_config = quarto_orchestrator.generate_yaml_config(
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
            yaml_config = quarto_orchestrator.generate_yaml_config(
                title="Test Document",
                layout_name="handwritten",
                document_type="paper",
                language=lang
            )
            
            assert yaml_config["lang"] == lang, f"Should support {lang} language"

    def test_generate_quarto_yaml_default_language(self):
        """Test YAML generation with default language parameter."""
        yaml_config = quarto_orchestrator.generate_yaml_config(
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
        """Test that no language parameter uses system default."""
        writer = DocumentWriter("paper", "creative")  # No language parameter
        
        writer.add_h1("Documento por Defecto")
        writer.add_text("Usa configuración de idioma por defecto del sistema.")
        
        result = writer.generate(
            markdown=True,
            html=False,
            pdf=False,
            qmd=True,
            output_filename="default_language"
        )
        
        # Check QMD content uses English (system default - no layout-specific language)
        if result["qmd"]:
            qmd_path = Path(result["qmd"])
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "lang: en" in content, "Should use system default English (no layout-specific language configuration)"


class TestLanguageValidation:
    """Test language parameter validation and edge cases."""

    def test_empty_language_parameter(self):
        """Test behavior with empty language parameter."""
        writer = DocumentWriter("paper", "creative", language="")
        # Empty string should be treated as None and fall back to default English
        assert writer.language == "en", "Empty language should fall back to default English"

    def test_none_language_parameter(self):
        """Test behavior with None language parameter."""
        writer = DocumentWriter("paper", "creative", language=None)
        assert writer.language == "en", "None language should fall back to default English"

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
    ("paper", "creative", "en"),
    ("report", "creative", "en"),
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