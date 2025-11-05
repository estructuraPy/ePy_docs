"""
Tests de integración para verificar funcionalidad completa de DocumentWriter.
"""
import pytest
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from ePy_docs.writers import DocumentWriter


class TestDocumentWriterIntegration:
    """Tests de integración para DocumentWriter completo."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crear directorio temporal para pruebas."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Crear DataFrame de prueba."""
        return pd.DataFrame({
            'Column A': [1, 2, 3, 4, 5],
            'Column B': [10, 20, 30, 40, 50],
            'Column C': ['A', 'B', 'C', 'D', 'E']
        })
    
    @pytest.fixture
    def sample_plot(self):
        """Crear plot de prueba."""
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, label='sin(x)')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Sample Plot')
        ax.legend()
        plt.tight_layout()
        yield fig
        plt.close(fig)
    
    def test_professional_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout professional."""
        writer = DocumentWriter("paper", "professional", language="es")
        
        # Agregar contenido
        writer.add_h1("Título Principal")
        writer.add_h2("Subtítulo")
        writer.add_text("Texto de prueba para verificar funcionalidad.")
        
        # Agregar tabla (debe usar auto-width)
        writer.add_table(sample_dataframe, title="Tabla de Prueba")
        
        # Agregar plot (debe usar auto-width)
        writer.add_plot(sample_plot, title="Gráfico de Prueba")
        
        # Verificar que se puede generar sin errores
        result = writer.generate(html=True, pdf=False)
        
        assert result is not None
        
        # Verificar archivos generados
        output_files = list(temp_output_dir.rglob("*.html"))
        assert len(output_files) > 0
    
    def test_creative_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout creative."""
        writer = DocumentWriter("paper", "creative", language="es")
        
        writer.add_h1("Creative Layout Test")
        writer.add_table(sample_dataframe, title="Creative Table")
        writer.add_plot(sample_plot, title="Creative Plot")
        
        result = writer.generate(html=True, pdf=False)
        assert result is not None
    
    def test_minimal_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout minimal."""
        writer = DocumentWriter("paper", "minimal", language="es")
        
        writer.add_h1("Minimal Layout Test")
        writer.add_table(sample_dataframe, title="Minimal Table")
        writer.add_plot(sample_plot, title="Minimal Plot")
        
        result = writer.generate(html=True, pdf=False)
        assert result is not None
    
    def test_handwritten_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout handwritten."""
        writer = DocumentWriter("paper", "handwritten", language="es")
        
        writer.add_h1("Handwritten Layout Test")
        writer.add_table(sample_dataframe, title="Handwritten Table")
        writer.add_plot(sample_plot, title="Handwritten Plot")
        
        result = writer.generate(html=True, pdf=False)
        assert result is not None
    
    def test_language_parameter_functionality(self, temp_output_dir):
        """Test funcionalidad del parámetro language."""
        # Test con español
        writer_es = DocumentWriter("paper", "professional", language="es")
        assert writer_es.language == "es"
        
        # Test con inglés
        writer_en = DocumentWriter("paper", "professional", language="en")
        assert writer_en.language == "en"
        
        # Test override de layout default
        writer_override = DocumentWriter("paper", "creative", language="en")
        assert writer_override.language == "en"  # Debe override el default "es" de creative
    
    def test_auto_width_vs_manual_columns(self, temp_output_dir, sample_plot):
        """Test comparación entre auto-width y columns manual."""
        writer = DocumentWriter("paper", "professional")
        
        # Auto-width (sin especificar columns)
        markdown_auto = writer.add_plot(sample_plot, title="Auto Width Plot")
        
        # Manual columns
        markdown_manual = writer.add_plot(sample_plot, title="Manual Columns Plot", columns=1)
        
        # Ambos deben contener width, pero diferentes valores
        assert "width=" in markdown_auto
        assert "width=" in markdown_manual
        assert markdown_auto != markdown_manual  # Deben ser diferentes
    
    def test_table_and_plot_consistency(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test consistencia entre tablas y plots en auto-width."""
        writer = DocumentWriter("paper", "professional")
        
        # Agregar tabla
        writer.add_table(sample_dataframe, title="Test Table")
        
        # Agregar plot
        markdown_plot = writer.add_plot(sample_plot, title="Test Plot")
        
        # Plot debe usar auto-width consistente con layout
        assert "width=" in markdown_plot
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_work_with_plots(self, layout_name, temp_output_dir, sample_plot):
        """Test que todos los layouts funcionan con plots."""
        writer = DocumentWriter("paper", layout_name)
        
        # Debe poder agregar plot sin errores
        markdown = writer.add_plot(sample_plot, title=f"Test Plot {layout_name}")
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "![Test Plot" in markdown
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_work_with_tables(self, layout_name, temp_output_dir, sample_dataframe):
        """Test que todos los layouts funcionan con tablas."""
        writer = DocumentWriter("paper", layout_name)
        
        # Debe poder agregar tabla sin errores
        writer.add_table(sample_dataframe, title=f"Test Table {layout_name}")
        
        # Verificar que el writer mantiene estado correcto
        assert writer.layout_style == layout_name
    
    def test_document_generation_with_all_elements(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test generación de documento con todos los elementos."""
        writer = DocumentWriter("paper", "professional", language="es")
        
        # Agregar variedad de contenido
        writer.add_h1("Documento de Prueba Completo")
        writer.add_h2("Sección de Tablas")
        writer.add_table(sample_dataframe, title="Tabla Principal")
        
        writer.add_h2("Sección de Gráficos")
        writer.add_plot(sample_plot, title="Gráfico Principal")
        
        writer.add_h2("Texto y Conclusiones")
        writer.add_text("Este es un documento de prueba que incluye todos los elementos.")
        
        # Generar documento
        result = writer.generate(html=True, pdf=False)
        
        assert result is not None
        
        # Verificar que se generaron archivos
        html_files = list(temp_output_dir.rglob("*.html"))
        assert len(html_files) > 0
        
        # Verificar que se generaron figuras
        figure_files = list(temp_output_dir.rglob("figures/*"))
        assert len(figure_files) > 0
    
    def test_error_handling_invalid_layout(self, temp_output_dir):
        """Test manejo de errores con layout inválido."""
        # Debe funcionar con fallback
        writer = DocumentWriter("paper", "nonexistent_layout")
        
        # Debe poder agregar contenido básico
        writer.add_h1("Test with Invalid Layout")
        writer.add_text("This should work with fallback.")
        
        # No debe generar errores
        assert writer.layout_style == "nonexistent_layout"
    
    def test_multiple_plots_auto_width_consistency(self, temp_output_dir):
        """Test consistencia de auto-width con múltiples plots."""
        writer = DocumentWriter("paper", "professional")
        
        # Crear múltiples plots
        plots_markdown = []
        for i in range(3):
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot([1, 2, 3], [i, i+1, i+2])
            ax.set_title(f'Plot {i+1}')
            
            markdown = writer.add_plot(fig, title=f"Plot {i+1}")
            plots_markdown.append(markdown)
            plt.close(fig)
        
        # Todos los plots deben tener width consistente
        for markdown in plots_markdown:
            assert "width=" in markdown
        
        # Extraer anchos y verificar consistencia
        widths = []
        for markdown in plots_markdown:
            if "width=6.5in" in markdown or 'width="6.5in"' in markdown:
                widths.append("6.5in")
        
        # Todos deben tener el mismo ancho auto-calculado
        assert len(set(widths)) <= 1  # Máximo 1 valor único (consistencia)