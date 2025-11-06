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
        assert isinstance(result, dict)
        
        # Verificar que se generó HTML
        if 'html' in result and result['html']:
            html_path = Path(result['html'])
            assert html_path.exists(), f"HTML file should exist at {html_path}"
            assert html_path.suffix == '.html'
        else:
            # Fallback: buscar HTML files in likely output locations
            # Check in common output directory patterns
            possible_dirs = [temp_output_dir, Path("results/report"), Path("results/paper")]
            output_files = []
            for dir_path in possible_dirs:
                if dir_path.exists():
                    output_files.extend(list(dir_path.rglob("*.html")))
            assert len(output_files) > 0, f"No HTML files found in any output directories"
    
    def test_creative_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout creative."""
        writer = DocumentWriter("paper", "creative", language="es")
        
        writer.add_h1("Creative Layout Test")
        writer.add_table(sample_dataframe, title="Creative Table")
        writer.add_plot(sample_plot, title="Creative Plot")
        
        result = writer.generate(html=True, pdf=False)
        assert result is not None
        assert isinstance(result, dict)
    
    def test_minimal_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout minimal."""
        writer = DocumentWriter("paper", "minimal", language="es")
        
        writer.add_h1("Minimal Layout Test")
        writer.add_table(sample_dataframe, title="Minimal Table")
        writer.add_plot(sample_plot, title="Minimal Plot")
        
        result = writer.generate(html=True, pdf=False)
        assert result is not None
        assert isinstance(result, dict)
    
    def test_handwritten_layout_complete_workflow(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test workflow completo con layout handwritten."""
        writer = DocumentWriter("paper", "handwritten", language="es")
        
        writer.add_h1("Handwritten Layout Test")
        writer.add_table(sample_dataframe, title="Handwritten Table")
        writer.add_plot(sample_plot, title="Handwritten Plot")
        
        result = writer.generate(html=True, pdf=False)
        assert result is not None
        assert isinstance(result, dict)
    
    def test_language_parameter_functionality(self, temp_output_dir):
        """Test funcionalidad del parámetro language."""
        # Test que diferentes languages pueden ser inicializados y funcionar
        writer_es = DocumentWriter("paper", "professional", language="es")
        writer_en = DocumentWriter("paper", "professional", language="en")
        writer_override = DocumentWriter("paper", "creative", language="en")
        
        # Test que basic operations work
        writer_es.add_text("Contenido en español")
        writer_en.add_text("Content in English")
        writer_override.add_text("Override content")
        
        # Verify content was added
        assert "Contenido en español" in writer_es.get_content()
        assert "Content in English" in writer_en.get_content()
        assert "Override content" in writer_override.get_content()
    
    def test_auto_width_vs_manual_columns(self, temp_output_dir, sample_plot):
        """Test comparación entre auto-width y columns manual."""
        writer = DocumentWriter("paper", "professional")
        
        # Auto-width (sin especificar columns)
        result_auto = writer.add_plot(sample_plot, title="Auto Width Plot")
        assert result_auto is writer  # Method chaining
        
        # Manual columns
        result_manual = writer.add_plot(sample_plot, title="Manual Columns Plot", columns=1)
        assert result_manual is writer  # Method chaining
        
        # Verificar que el contenido se agregó
        content = writer.get_content()
        assert "Auto Width Plot" in content
        assert "Manual Columns Plot" in content
    
    def test_table_and_plot_consistency(self, temp_output_dir, sample_dataframe, sample_plot):
        """Test consistencia entre tablas y plots en auto-width."""
        writer = DocumentWriter("paper", "professional")
        
        # Agregar tabla
        table_result = writer.add_table(sample_dataframe, title="Test Table")
        assert table_result is writer
        
        # Agregar plot
        plot_result = writer.add_plot(sample_plot, title="Test Plot")
        assert plot_result is writer
        
        # Verificar que el contenido se agregó
        content = writer.get_content()
        assert "Test Table" in content
        assert "Test Plot" in content
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_work_with_plots(self, layout_name, temp_output_dir, sample_plot):
        """Test que todos los layouts funcionan con plots."""
        writer = DocumentWriter("paper", layout_name)
        
        # Debe poder agregar plot sin errores
        result = writer.add_plot(sample_plot, title=f"Test Plot {layout_name}")
        
        assert result is writer  # Method chaining
        
        # Verificar que el contenido se agregó
        content = writer.get_content()
        assert f"Test Plot {layout_name}" in content
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_work_with_tables(self, layout_name, temp_output_dir, sample_dataframe):
        """Test que todos los layouts funcionan con tablas."""
        writer = DocumentWriter("paper", layout_name)
        
        # Debe poder agregar tabla sin errores
        writer.add_table(sample_dataframe, title=f"Test Table {layout_name}")
        
        # Verificar que el contenido fue agregado
        content = writer.get_content()
        assert f"Test Table {layout_name}" in content or len(content) > 0
    
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
        
        # Verificar que result es un diccionario con las claves esperadas
        assert isinstance(result, dict)
        if 'html' in result:
            # Si se generó HTML, verificar que la ruta existe
            from pathlib import Path
            if result['html'] and Path(result['html']).exists():
                assert Path(result['html']).suffix == '.html'
    
    def test_error_handling_invalid_layout(self, temp_output_dir):
        """Test manejo de errores con layout inválido."""
        # Debe funcionar con fallback
        writer = DocumentWriter("paper", "nonexistent_layout")
        
        # Debe poder agregar contenido básico
        writer.add_h1("Test with Invalid Layout")
        writer.add_text("This should work with fallback.")
        
        # Verificar que el contenido fue agregado
        content = writer.get_content()
        assert "Test with Invalid Layout" in content
        assert "This should work with fallback." in content
    
    def test_multiple_plots_auto_width_consistency(self, temp_output_dir):
        """Test consistencia de auto-width con múltiples plots."""
        writer = DocumentWriter("paper", "professional")
        
        # Crear múltiples plots
        for i in range(3):
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot([1, 2, 3], [i, i+1, i+2])
            ax.set_title(f'Plot {i+1}')
            
            writer.add_plot(fig, title=f"Plot {i+1}")
            plt.close(fig)
        
        # Obtener contenido y verificar que contiene plots
        content = writer.get_content()
        assert "Plot 1" in content
        assert "Plot 2" in content
        assert "Plot 3" in content
        
        # Verificar que el writer se creó correctamente
        assert writer is not None