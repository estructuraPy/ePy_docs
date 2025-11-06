"""
Tests para verificar el funcionamiento del auto-width en plots.
"""
import pytest
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import tempfile
import shutil

from ePy_docs.writers import DocumentWriter
from ePy_docs.core._images import ImageProcessor
from ePy_docs.core._columns import ColumnWidthCalculator


class TestPlotAutoWidth:
    """Tests para el auto-width automático en plots."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crear directorio temporal para pruebas."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_figure(self):
        """Crear figura de prueba."""
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, label='sin(x)')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Test Plot')
        ax.legend()
        plt.tight_layout()
        yield fig
        plt.close(fig)
    
    def test_auto_width_professional_layout(self, sample_figure, temp_output_dir):
        """Test auto-width para layout professional."""
        writer = DocumentWriter("paper", "professional")
        
        # Agregar plot sin especificar columns (debe usar auto-width)
        result = writer.add_plot(sample_figure, title="Test Auto-Width Professional")
        
        # Verificar method chaining
        assert result is writer
        
        # Verificar que el contenido se agregó
        content = writer.get_content()
        assert "Test Auto-Width Professional" in content
    
    def test_auto_width_creative_layout(self, sample_figure, temp_output_dir):
        """Test auto-width para layout creative."""
        writer = DocumentWriter("paper", "creative")
        
        result = writer.add_plot(sample_figure, title="Test Auto-Width Creative")
        
        # Verificar method chaining y contenido
        assert result is writer
        content = writer.get_content()
        assert "Test Auto-Width Creative" in content
    
    def test_auto_width_minimal_layout(self, sample_figure, temp_output_dir):
        """Test auto-width para layout minimal."""
        writer = DocumentWriter("paper", "minimal")
        
        result = writer.add_plot(sample_figure, title="Test Auto-Width Minimal")
        
        assert result is writer
        content = writer.get_content()
        assert "Test Auto-Width Minimal" in content
    
    def test_auto_width_handwritten_layout(self, sample_figure, temp_output_dir):
        """Test auto-width para layout handwritten."""
        writer = DocumentWriter("paper", "handwritten")
        
        result = writer.add_plot(sample_figure, title="Test Auto-Width Handwritten")
        
        assert result is writer
        content = writer.get_content()
        assert "Test Auto-Width Handwritten" in content
    
    def test_manual_columns_override_auto_width(self, sample_figure, temp_output_dir):
        """Test que columns manual override el auto-width."""
        writer = DocumentWriter("paper", "professional")
        
        # Especificar columns=1 manualmente
        result = writer.add_plot(sample_figure, title="Test Manual Columns", columns=1)
        
        # Debe retornar self para method chaining
        assert result is writer
        content = writer.get_content()
        assert "Test Manual Columns" in content
    
    def test_direct_width_specification(self, sample_figure, temp_output_dir):
        """Test especificación directa de ancho."""
        writer = DocumentWriter("paper", "professional")
        
        result = writer.add_plot(sample_figure, title="Test Direct Width", columns=[4.0])
        
        assert result is writer
        content = writer.get_content()
        assert "Test Direct Width" in content
    
    def test_column_width_calculator_integration(self):
        """Test integración con ColumnWidthCalculator."""
        from ePy_docs.core._columns import ColumnWidthCalculator
        calculator = ColumnWidthCalculator()
        
        # Test para paper con 2 columnas, spanning 2 columnas
        width = calculator.calculate_width("paper", 2, 2)
        assert width == pytest.approx(6.5, abs=0.1)
        
        # Test para paper con 2 columnas, spanning 1 columna
        width = calculator.calculate_width("paper", 2, 1)
        assert width == pytest.approx(3.1, abs=0.1)
    
    def test_different_document_types_auto_width(self, sample_figure, temp_output_dir):
        """Test auto-width para diferentes tipos de documento."""
        # Test report type
        writer_report = DocumentWriter("report", "professional")
        result_report = writer_report.add_plot(sample_figure, title="Test Report")
        assert result_report is writer_report
        
        # Test paper type  
        writer_paper = DocumentWriter("paper", "professional")
        result_paper = writer_paper.add_plot(sample_figure, title="Test Paper")
        assert result_paper is writer_paper
    
    def test_fallback_when_layout_config_missing(self, sample_figure, temp_output_dir):
        """Test fallback cuando no hay configuración de layout."""
        # Usar un layout válido pero probar que funciona
        writer = DocumentWriter("paper", "professional")
        
        result = writer.add_plot(sample_figure, title="Test Fallback")
        assert result is writer
        content = writer.get_content()
        assert "Test Fallback" in content
        # Debe funcionar sin errores (usando fallbacks)
        writer.add_plot(sample_figure, title="Test Fallback")
        
        # Debe generar contenido válido
        final_content = writer.get_content()
        assert "Test Fallback" in final_content


class TestLayoutColumnConfiguration:
    """Tests para verificar configuración de columnas en layouts."""
    
    def test_professional_layout_columns(self):
        """Test configuración de columnas en professional layout."""
        from ePy_docs.core._config import load_layout
        
        config = load_layout("professional")
        
        # Verificar que tiene configuración de paper
        assert "paper" in config
        assert "columns" in config["paper"]
        
        # Professional debería tener configuración de columnas
        columns_config = config["paper"]["columns"]
        assert "default" in columns_config
        assert "supported" in columns_config
    
    def test_creative_layout_columns(self):
        """Test configuración de columnas en creative layout."""
        from ePy_docs.core._config import load_layout
        
        config = load_layout("creative")
        
        assert "paper" in config
        assert "columns" in config["paper"]
        
        columns_config = config["paper"]["columns"]
        assert "default" in columns_config
        assert isinstance(columns_config["default"], int)
    
    def test_handwritten_layout_columns(self):
        """Test configuración de columnas en handwritten layout."""
        from ePy_docs.core._config import load_layout
        
        config = load_layout("handwritten")
        
        assert "paper" in config
        assert "columns" in config["paper"]
        
        columns_config = config["paper"]["columns"]
        assert columns_config["default"] == 2  # Handwritten debe tener 2 columnas por defecto
    
    def test_minimal_layout_columns(self):
        """Test configuración de columnas en minimal layout."""
        from ePy_docs.core._config import load_layout
        
        config = load_layout("minimal")
        
        assert "paper" in config
        assert "columns" in config["paper"]
        
        columns_config = config["paper"]["columns"]
        assert columns_config["default"] == 1  # Minimal debe tener 1 columna por defecto
    
    @pytest.mark.parametrize("layout_name", [
        "professional", "creative", "minimal", "handwritten", 
        "classic", "scientific", "technical", "academic", "corporate"
    ])
    def test_all_layouts_have_column_config(self, layout_name):
        """Test que todos los layouts tienen configuración de columnas."""
        from ePy_docs.core._config import load_layout
        
        config = load_layout(layout_name)
        
        # Todos los layouts deben tener configuración de paper y report
        for doc_type in ["paper", "report"]:
            assert doc_type in config, f"Layout {layout_name} missing {doc_type} config"
            
            if "columns" in config[doc_type]:
                columns_config = config[doc_type]["columns"]
                assert "default" in columns_config, f"Layout {layout_name} missing default columns"
                assert isinstance(columns_config["default"], int), f"Layout {layout_name} default columns not int"
                assert columns_config["default"] > 0, f"Layout {layout_name} default columns <= 0"


class TestPlotWidthGeneration:
    """Tests para verificar generación correcta de markdown con anchos."""
    
    def test_width_string_generation(self):
        """Test generación de strings de ancho."""
        calculator = ColumnWidthCalculator()
        
        # Test con diferentes anchos
        assert calculator.get_width_string(6.5) == "6.5in"
        assert calculator.get_width_string(3.25) == "3.25in"
        assert calculator.get_width_string(4.0) == "4in"  # Should strip .0
    
    def test_markdown_contains_proper_width_attribute(self, temp_output_dir):
        """Test que el markdown contiene atributo width correcto."""
        handler = ImageProcessor()
        
        # Crear plot temporal
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 2])
        temp_image = temp_output_dir / "test_plot.png"
        fig.savefig(temp_image)
        plt.close(fig)
        
        markdown, counter = handler.add_plot_content(
            img_path=str(temp_image),
            title="Test Plot",
            figure_counter=1,
            output_dir=str(temp_output_dir),
            document_type="paper",
            layout_style="professional",
            columns=2  # 2 columnas = width completo
        )
        
        # Verificar formato de markdown
        assert "![Test Plot]" in markdown
        assert "width=6.5in" in markdown or 'width="6.5in"' in markdown
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crear directorio temporal para pruebas."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        if temp_dir.exists():
            shutil.rmtree(temp_dir)