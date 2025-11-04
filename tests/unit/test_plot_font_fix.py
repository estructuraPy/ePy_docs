"""
Test para verificar que writer.add_plot() aplica fuentes automáticamente.
Este test verifica el fix del issue: fonts no se aplicaban a gráficos.
"""

import pytest
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from ePy_docs.writers import DocumentWriter


class TestPlotFontApplication:
    """Test que writer.add_plot() aplica fuentes correctamente."""
    
    @pytest.mark.skip(reason="Test outdated - covered by test_font_system.py::TestPlotFontIntegration")
    def test_add_plot_applies_fonts_automatically(self):
        """Verificar que add_plot() aplica fuentes sin intervención del usuario."""
        # Crear writer con handwritten layout
        writer = DocumentWriter("report", "handwritten")
        
        # Crear un gráfico simple SIN aplicar fuentes manualmente
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        ax.plot(x, y, 'o-')
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_title('Test Title')
        
        # El usuario NO debe llamar apply_fonts - writer.add_plot lo hace automáticamente
        writer.add_plot(fig)
        
        # Verificar que se generó el contenido
        assert len(writer._core.content_buffer) > 0
        
        # El gráfico debería haberse guardado con las fuentes aplicadas
        # Verificar que existe el archivo guardado
        output_dir = Path('results/report/figures')
        saved_plots = list(output_dir.glob('fig_*.png'))
        assert len(saved_plots) > 0, "El gráfico debería haberse guardado"
        
        plt.close('all')
    
    def test_add_plot_works_with_different_layouts(self):
        """Verificar que funciona con diferentes layouts."""
        layouts = ['handwritten', 'academic', 'modern']
        
        for layout in layouts:
            writer = DocumentWriter("report", layout)
            
            # Crear gráfico
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            ax.set_title(f'Test {layout}')
            
            # Agregar sin aplicar fuentes manualmente
            writer.add_plot(fig)
            
            # Debería funcionar sin errores
            assert len(writer._core.content_buffer) > 0
            
            plt.close('all')
    
    @pytest.mark.skip(reason="Test outdated - covered by test_font_system.py::TestPlotFontIntegration")
    def test_fonts_applied_before_save(self):
        """Verificar que las fuentes se aplican ANTES de guardar."""
        writer = DocumentWriter("report", "handwritten")
        
        # Crear figura con texto que requiere fallbacks
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_xlabel('Numbers: 123 (test)')  # Números + paréntesis requieren fallback
        ax.set_ylabel('Letters ABC')  # Solo letras, usa handwriting
        ax.set_title('Mixed: ABC123 (test)')  # Mezcla
        
        # Agregar el plot - debería aplicar fuentes automáticamente
        writer.add_plot(fig)
        
        # Verificar que el gráfico se guardó
        output_dir = Path('results/report/figures')
        assert output_dir.exists()
        saved_plots = list(output_dir.glob('fig_*.png'))
        assert len(saved_plots) > 0
        
        plt.close('all')
    
    def test_example_3_workflow(self):
        """Test que replica el workflow exacto de example_3.ipynb."""
        # Setup igual que example_3
        writer = DocumentWriter("report", "handwritten")
        writer.add_h1("Test Title")
        
        # Datos igual que example_3
        strain = np.array([0, 0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035])
        stress = np.array([0, 10, 18, 24, 28, 30, 30.5, 30])
        
        df_stress_strain = pd.DataFrame({
            'Deformación (ε)': strain,
            'Esfuerzo (σ) [MPa]': stress
        })
        
        # Tabla (ya funcionaba)
        writer.add_table(df_stress_strain, title="Test Table", show_figure=False)
        
        # Gráfico (esto es lo que se arregló)
        fig = plt.figure(figsize=(10, 6))
        plt.plot(df_stress_strain['Deformación (ε)'], 
                df_stress_strain['Esfuerzo (σ) [MPa]'], 
                marker='o', linewidth=2, markersize=6, color='blue')
        plt.xlabel('Deformación (ε)', fontsize=12)
        plt.ylabel('Esfuerzo (σ) [MPa]', fontsize=12)
        plt.title('Diagrama Esfuerzo-Deformación del Concreto', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # El usuario NO llama apply_fonts - writer lo hace automáticamente
        writer.add_plot(fig)
        
        # Verificar que todo se agregó correctamente
        assert len(writer._core.content_buffer) >= 3  # H1 + tabla + gráfico
        
        plt.close('all')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
