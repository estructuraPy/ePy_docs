#!/usr/bin/env python3
"""
Test DEFINITIVO: verificar que los fallbacks funcionan correctamente
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ePy_docs.core._images import setup_matplotlib_fonts

def test_fallbacks_funcionando():
    """Test que los fallbacks realmente funcionan"""
    
    print("=== TEST DE FALLBACKS ===")
    
    # Setup handwritten
    font_list = setup_matplotlib_fonts('handwritten')
    print(f"Font list configurada: {font_list}")
    
    # Verificar rcParams
    print(f"matplotlib rcParams['font.sans-serif']: {plt.rcParams['font.sans-serif']}")
    print(f"matplotlib rcParams['font.family']: {plt.rcParams['font.family']}")
    
    # Crear gráfico
    x = np.array([0.0000, 0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0035])
    y = np.array([0, 1.4, 2.5, 3.4, 4.1, 4.4, 4.5, 4.4])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, 'b-o', linewidth=2, markersize=4)
    ax.set_title('Diagrama Esfuerzo-Deformación del Concreto', fontsize=14)
    ax.set_xlabel('Deformación (ε)', fontsize=12)
    ax.set_ylabel('Esfuerzo (σ) [ksi]', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xlim(0, 0.0035)
    ax.set_ylim(0, 5)
    
    # Verificar qué fuentes están usando los elementos
    title_font = ax.title.get_fontfamily()
    xlabel_font = ax.xaxis.label.get_fontfamily()
    
    print(f"\nFuentes usadas:")
    print(f"  Título: {title_font}")
    print(f"  Xlabel: {xlabel_font}")
    print(f"  Tick X[0]: {ax.get_xticklabels()[0].get_fontfamily() if ax.get_xticklabels() else 'N/A'}")
    
    # Guardar
    output = Path(__file__).parent / 'results' / 'test_fallbacks_working.png'
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"\n✅ Guardado: {output}")
    plt.show()

def test_comparacion_con_sin_fallbacks():
    """Comparar gráfico con y sin sistema de fallbacks"""
    
    print("\n=== COMPARACIÓN CON/SIN FALLBACKS ===")
    
    x = np.array([0.0, 0.001, 0.002, 0.003])
    y = np.array([0, 2, 4, 4.5])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # IZQUIERDA: Sin configurar (por defecto)
    ax1.plot(x, y, 'b-o', linewidth=2)
    ax1.set_title('SIN setup_matplotlib_fonts', fontsize=12)
    ax1.set_xlabel('Deformación (0.000)')
    ax1.set_ylabel('Esfuerzo (0.00)')
    ax1.grid(True, alpha=0.3)
    
    # DERECHA: Con setup
    font_list = setup_matplotlib_fonts('handwritten')
    
    ax2.plot(x, y, 'r-s', linewidth=2)
    ax2.set_title('CON setup_matplotlib_fonts(handwritten)', fontsize=12)
    ax2.set_xlabel('Deformación (0.000)')
    ax2.set_ylabel('Esfuerzo (0.00)')
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('Los números deberían verse DIFERENTES si los fallbacks funcionan', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    output = Path(__file__).parent / 'results' / 'comparacion_fallbacks.png'
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"✅ Guardado: {output}")
    plt.show()
    
    # Reset
    plt.rcParams.update(plt.rcParamsDefault)

if __name__ == "__main__":
    test_fallbacks_funcionando()
    test_comparacion_con_sin_fallbacks()
    
    print("\n" + "="*60)
    print("AHORA LOS FALLBACKS DEBERÍAN FUNCIONAR")
    print("Los números usarán las fuentes de fallback automáticamente")