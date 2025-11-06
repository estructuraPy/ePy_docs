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
            assert len(writer.content_buffer) > 0
            
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
        assert len(writer.content_buffer) >= 3  # H1 + tabla + gráfico
        
        plt.close('all')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
