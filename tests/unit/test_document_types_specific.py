"""
Test exhaustivo de document_types: paper vs report
Verifica que cada tipo de documento tenga su configuración específica
"""

import pytest
from ePy_docs.core._config import get_document_type_config
from ePy_docs.core._pdf import get_pdf_config
from ePy_docs.core._quarto import generate_quarto_yaml


class TestDocumentTypesConfiguration:
    """Tests para verificar configuraciones específicas por document_type."""
    
    def test_report_has_correct_documentclass(self):
        """Report debe usar documentclass 'report'."""
        config = get_document_type_config('report')
        assert config['documentclass'] == 'report'
    
    def test_paper_has_correct_documentclass(self):
        """Paper debe usar documentclass 'article'."""
        config = get_document_type_config('paper')
        assert config['documentclass'] == 'article'
    
    def test_report_single_column_default(self):
        """Report debe tener 1 columna por defecto."""
        config = get_document_type_config('report')
        assert config['default_columns'] == 1
    
    def test_paper_two_column_default(self):
        """Paper debe tener 2 columnas por defecto."""
        config = get_document_type_config('paper')
        assert config['default_columns'] == 2
    
    def test_report_fontsize(self):
        """Report debe usar fontsize 11pt."""
        config = get_document_type_config('report')
        assert config['quarto_pdf']['fontsize'] == '11pt'
    
    def test_paper_fontsize(self):
        """Paper debe usar fontsize 10pt."""
        config = get_document_type_config('paper')
        assert config['quarto_pdf']['fontsize'] == '10pt'
    
    def test_report_toc_depth(self):
        """Report debe tener toc-depth: 3."""
        config = get_document_type_config('report')
        assert config['quarto_common']['toc-depth'] == 3
    
    def test_paper_toc_depth(self):
        """Paper debe tener toc-depth: 4."""
        config = get_document_type_config('paper')
        assert config['quarto_common']['toc-depth'] == 4
    
    def test_report_crossref_chapters_disabled(self):
        """Report debe tener chapters: false para evitar 'Chapter' prefix."""
        config = get_document_type_config('report')
        assert config['crossref']['chapters'] == False
    
    def test_paper_crossref_chapters_enabled(self):
        """Paper debe tener chapters: true."""
        config = get_document_type_config('paper')
        assert config['crossref']['chapters'] == True


class TestPDFConfigIntegration:
    """Tests para verificar que get_pdf_config usa las configuraciones correctas."""
    
    def test_report_pdf_config_uses_report_class(self):
        """PDF config para report debe usar documentclass 'report'."""
        pdf_config = get_pdf_config(layout_name='professional', document_type='report')
        assert pdf_config['documentclass'] == 'report'
    
    def test_paper_pdf_config_uses_article_class(self):
        """PDF config para paper debe usar documentclass 'article'."""
        pdf_config = get_pdf_config(layout_name='academic', document_type='paper')
        assert pdf_config['documentclass'] == 'article'
    
    def test_report_pdf_config_fontsize(self):
        """PDF config para report debe usar fontsize del archivo report.epyson."""
        pdf_config = get_pdf_config(layout_name='professional', document_type='report')
        assert pdf_config['fontsize'] == '11pt'
    
    def test_paper_pdf_config_fontsize(self):
        """PDF config para paper debe usar fontsize del archivo paper.epyson."""
        pdf_config = get_pdf_config(layout_name='academic', document_type='paper')
        assert pdf_config['fontsize'] == '10pt'


class TestQuartoYAMLIntegration:
    """Tests para verificar que generate_quarto_yaml integra las configs correctamente."""
    
    def test_report_quarto_yaml_toc_depth(self):
        """Quarto YAML para report debe tener toc-depth: 3."""
        yaml_config = generate_quarto_yaml(
            title="Test Report",
            layout_name='professional',
            document_type='report'
        )
        assert yaml_config['toc-depth'] == 3
    
    def test_paper_quarto_yaml_toc_depth(self):
        """Quarto YAML para paper debe tener toc-depth: 4."""
        yaml_config = generate_quarto_yaml(
            title="Test Paper",
            layout_name='academic',
            document_type='paper'
        )
        assert yaml_config['toc-depth'] == 4
    
    def test_report_quarto_yaml_crossref_chapters(self):
        """Quarto YAML para report debe tener crossref.chapters: False."""
        yaml_config = generate_quarto_yaml(
            title="Test Report",
            layout_name='professional',
            document_type='report'
        )
        assert yaml_config['crossref']['chapters'] == False
    
    def test_paper_quarto_yaml_crossref_chapters(self):
        """Quarto YAML para paper debe tener crossref.chapters: True."""
        yaml_config = generate_quarto_yaml(
            title="Test Paper",
            layout_name='academic',
            document_type='paper'
        )
        assert yaml_config['crossref']['chapters'] == True
    
    def test_report_quarto_yaml_pdf_fontsize(self):
        """Quarto YAML para report debe incluir fontsize 11pt en format.pdf."""
        yaml_config = generate_quarto_yaml(
            title="Test Report",
            layout_name='professional',
            document_type='report',
            output_formats=['pdf']
        )
        assert yaml_config['format']['pdf']['fontsize'] == '11pt'
    
    def test_paper_quarto_yaml_pdf_fontsize(self):
        """Quarto YAML para paper debe incluir fontsize 10pt en format.pdf."""
        yaml_config = generate_quarto_yaml(
            title="Test Paper",
            layout_name='academic',
            document_type='paper',
            output_formats=['pdf']
        )
        assert yaml_config['format']['pdf']['fontsize'] == '10pt'
    
    def test_report_applies_quarto_common_settings(self):
        """Report debe aplicar todas las configuraciones de quarto_common."""
        yaml_config = generate_quarto_yaml(
            title="Test Report",
            layout_name='professional',
            document_type='report'
        )
        # Verificar que las configuraciones de quarto_common se aplicaron
        assert yaml_config['toc'] == True
        assert yaml_config['toc-depth'] == 3
        assert yaml_config['number-sections'] == True
        assert yaml_config['fig-align'] == 'center'
        assert yaml_config['fig-cap-location'] == 'bottom'
        assert yaml_config['tbl-cap-location'] == 'top'
    
    def test_paper_applies_quarto_common_settings(self):
        """Paper debe aplicar todas las configuraciones de quarto_common."""
        yaml_config = generate_quarto_yaml(
            title="Test Paper",
            layout_name='academic',
            document_type='paper'
        )
        # Verificar que las configuraciones de quarto_common se aplicaron
        assert yaml_config['toc'] == True
        assert yaml_config['toc-depth'] == 4
        assert yaml_config['number-sections'] == True
        assert yaml_config['fig-align'] == 'center'
        assert yaml_config['fig-cap-location'] == 'bottom'
        assert yaml_config['tbl-cap-location'] == 'top'


class TestDocumentTypeDifferences:
    """Tests para verificar que report y paper son realmente diferentes."""
    
    def test_report_and_paper_have_different_documentclass(self):
        """Report y paper deben tener documentclass diferentes."""
        report_config = get_document_type_config('report')
        paper_config = get_document_type_config('paper')
        assert report_config['documentclass'] != paper_config['documentclass']
    
    def test_report_and_paper_have_different_columns(self):
        """Report y paper deben tener default_columns diferentes."""
        report_config = get_document_type_config('report')
        paper_config = get_document_type_config('paper')
        assert report_config['default_columns'] != paper_config['default_columns']
    
    def test_report_and_paper_have_different_fontsize(self):
        """Report y paper deben tener fontsize diferentes."""
        report_config = get_document_type_config('report')
        paper_config = get_document_type_config('paper')
        assert report_config['quarto_pdf']['fontsize'] != paper_config['quarto_pdf']['fontsize']
    
    def test_report_and_paper_have_different_toc_depth(self):
        """Report y paper deben tener toc-depth diferentes."""
        report_config = get_document_type_config('report')
        paper_config = get_document_type_config('paper')
        assert report_config['quarto_common']['toc-depth'] != paper_config['quarto_common']['toc-depth']
    
    def test_report_and_paper_have_different_crossref_chapters(self):
        """Report y paper deben tener crossref.chapters diferentes."""
        report_config = get_document_type_config('report')
        paper_config = get_document_type_config('paper')
        assert report_config['crossref']['chapters'] != paper_config['crossref']['chapters']
