#!/usr/bin/env python3
"""
Recrear exactamente el tipo de gráfico que el usuario reportó que no funciona
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ePy_docs.core._images import ImageProcessor

def create_stress_strain_diagram():
    """Crea un diagrama esfuerzo-deformación como el que adjuntaste"""
    
    print("=== RECREANDO DIAGRAMA ESFUERZO-DEFORMACIÓN ===")
    
    # Configurar fuentes
    processor = ImageProcessor()
    font_list = processor.setup_matplotlib_fonts('handwritten')
    print(f"Font list configurada: {font_list}")
    
    # Datos como en tu gráfico
    deformation = np.array([0.0000, 0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0035])
    stress_ksi = np.array([0, 1.4, 2.5, 3.4, 4.1, 4.4, 4.5, 4.4])
    stress_pa = stress_ksi * 1e7  # Para el segundo gráfico
    
    # Crear figura con 2 subplots como tus imágenes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Primer gráfico (ksi)
    ax1.plot(deformation, stress_ksi, 'b-o', linewidth=2.5, markersize=5)
    ax1.set_title('Diagrama Esfuerzo-Deformación del Concreto', 
                 fontfamily='C2024_anm_font', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Deformación (ε)', fontfamily='C2024_anm_font', fontsize=12)
    ax1.set_ylabel('Esfuerzo (σ) [ksi]', fontfamily='C2024_anm_font', fontsize=12)
    ax1.grid(True, alpha=0.4, linestyle='--')
    ax1.set_xlim(0, 0.0035)
    ax1.set_ylim(0, 5)
    
    # Segundo gráfico (Pa) 
    ax2.plot(deformation, stress_pa, 'b-o', linewidth=2.5, markersize=5)
    ax2.set_title('Diagrama Esfuerzo-Deformación del Concreto', 
                 fontfamily='C2024_anm_font', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Deformación (ε)', fontfamily='C2024_anm_font', fontsize=12)
    ax2.set_ylabel('Esfuerzo (σ) [Pa]', fontfamily='C2024_anm_font', fontsize=12)
    ax2.grid(True, alpha=0.4, linestyle='--')
    ax2.set_xlim(0, 0.0035)
    ax2.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    # Configurar todos los labels con la fuente
    for ax in [ax1, ax2]:
        for tick in ax.get_xticklabels():
            tick.set_fontfamily('C2024_anm_font')
        for tick in ax.get_yticklabels():
            tick.set_fontfamily('C2024_anm_font')
    
    plt.tight_layout()
    
    # Guardar
    output_file = Path(__file__).parent / 'results' / 'stress_strain_test.png'
    output_file.parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    
    print(f"✅ Gráfico guardado en: {output_file}")
    
    # Mostrar información de fuentes usadas
    import matplotlib.font_manager as fm
    available_fonts = [f.name for f in fm.fontManager.ttflist if 'C2024' in f.name]
    print(f"Fuentes C2024 disponibles: {len(available_fonts)}")
    
    plt.show()
    
    return output_file

def test_with_epy_docs_add_image():
    """Test usando la función add_image_content de ePy_docs"""
    
    print("\n=== TEST CON add_image_content ===")
    
    from ePy_docs.core._images import add_image_content
    
    # Crear un gráfico temporal
    fig, ax = plt.subplots(figsize=(8, 6))
    
    processor = ImageProcessor()
    processor.setup_matplotlib_fonts('handwritten')
    
    # Datos
    deformation = np.array([0.0000, 0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0035])
    stress_ksi = np.array([0, 1.4, 2.5, 3.4, 4.1, 4.4, 4.5, 4.4])
    
    # Crear gráfico
    ax.plot(deformation, stress_ksi, 'b-o', linewidth=2.5, markersize=5)
    ax.set_title('Diagrama Esfuerzo-Deformación del Concreto', 
                fontfamily='C2024_anm_font', fontsize=14)
    ax.set_xlabel('Deformación (ε)', fontfamily='C2024_anm_font', fontsize=12)
    ax.set_ylabel('Esfuerzo (σ) [ksi]', fontfamily='C2024_anm_font', fontsize=12)
    ax.grid(True, alpha=0.4)
    
    # Guardar temporal
    temp_file = Path(__file__).parent / 'temp_stress_strain.png'
    plt.savefig(temp_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Procesar con ePy_docs
    try:
        result = add_image_content(
            path=str(temp_file),
            caption="Diagrama esfuerzo-deformación del concreto generado con handwritten",
            width="80%",
            layout_style='handwritten',
            document_type='report',
            figure_counter=1
        )
        
        print(f"✅ add_image_content exitoso")
        print(f"Tipo de resultado: {type(result)}")
        print(f"Longitud del resultado: {len(str(result))}")
        
        # Limpiar
        temp_file.unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Error con add_image_content: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_stress_strain_diagram()
    test_with_epy_docs_add_image()
    
    print("\n✅ TESTS COMPLETADOS - Si puedes ver estos gráficos con fuente handwritten, el sistema funciona")