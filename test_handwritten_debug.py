#!/usr/bin/env python3
"""
Diagnóstico: ¿Por qué no funciona handwritten ahora?
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_current_handwritten_behavior():
    """Reproduce exactamente el comportamiento actual de handwritten"""
    
    print("=== DIAGNÓSTICO DEL PROBLEMA HANDWRITTEN ===")
    
    # 1. Verificar archivos de fuente
    print("\n1. VERIFICANDO ARCHIVOS DE FUENTE:")
    package_root = Path(__file__).parent / 'src' / 'ePy_docs'
    font_file = package_root / 'config' / 'assets' / 'fonts' / 'C2024_anm_font_regular.otf'
    
    print(f"Archivo de fuente: {font_file}")
    print(f"Existe: {'✅ SÍ' if font_file.exists() else '❌ NO'}")
    if font_file.exists():
        print(f"Tamaño: {font_file.stat().st_size} bytes")
    
    # 2. Verificar configuración
    print("\n2. VERIFICANDO CONFIGURACIÓN:")
    try:
        from ePy_docs.core._config import get_config_section
        
        # Layout handwritten
        try:
            handwritten_config = get_config_section('handwritten')
            print(f"Configuración handwritten encontrada: {bool(handwritten_config)}")
            font_family = handwritten_config.get('font_family')
            print(f"Font family en handwritten: {font_family}")
        except Exception as e:
            print(f"❌ Error leyendo config handwritten: {e}")
        
        # Familias de fuentes
        format_config = get_config_section('format')
        font_families = format_config.get('font_families', {})
        handwritten_personal = font_families.get('handwritten_personal', {})
        
        print(f"Configuración handwritten_personal:")
        print(f"  - primary: {handwritten_personal.get('primary')}")
        print(f"  - font_file_template: {handwritten_personal.get('font_file_template')}")
        
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
    
    # 3. Test registro manual
    print("\n3. TEST DE REGISTRO MANUAL:")
    
    # Antes del registro
    fonts_before = [f.name for f in fm.fontManager.ttflist if 'C2024' in f.name]
    print(f"Fuentes C2024 antes: {fonts_before}")
    
    # Registro manual directo
    if font_file.exists():
        try:
            fm.fontManager.addfont(str(font_file))
            fonts_after = [f.name for f in fm.fontManager.ttflist if 'C2024' in f.name]
            print(f"Fuentes C2024 después: {fonts_after}")
        except Exception as e:
            print(f"❌ Error registrando fuente: {e}")
    
    # 4. Test ImageProcessor actual
    print("\n4. TEST DEL IMAGEPROCESSOR ACTUAL:")
    try:
        from ePy_docs.core._images import ImageProcessor
        
        processor = ImageProcessor()
        print("ImageProcessor creado ✅")
        
        # Test setup
        result = processor.setup_matplotlib_fonts('handwritten')
        print(f"setup_matplotlib_fonts('handwritten') ejecutado: {result}")
        
        # Verificar fuentes después
        fonts_final = [f.name for f in fm.fontManager.ttflist if 'C2024' in f.name]
        print(f"Fuentes C2024 final: {fonts_final}")
        
    except Exception as e:
        print(f"❌ Error con ImageProcessor: {e}")
        import traceback
        traceback.print_exc()

def create_comparison_plot():
    """Crea un gráfico como los que adjuntaste"""
    
    print("\n5. CREANDO GRÁFICO DE PRUEBA:")
    
    # Datos de ejemplo (como curva esfuerzo-deformación)
    deformation = [0.0000, 0.0005, 0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0035]
    stress_ksi = [0, 1.4, 2.5, 3.4, 4.1, 4.4, 4.5, 4.4]
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Intentar usar handwritten
    try:
        from ePy_docs.core._images import ImageProcessor
        processor = ImageProcessor()
        processor.setup_matplotlib_fonts('handwritten')
        
        print("✅ Setup de handwritten ejecutado")
        
        # Crear gráfico con fuente handwritten
        ax.plot(deformation, stress_ksi, 'b-o', linewidth=2, markersize=6)
        ax.set_title('Diagrama Esfuerzo-Deformación del Concreto', 
                    fontfamily='C2024_anm_font', fontsize=14)
        ax.set_xlabel('Deformación (ε)', fontfamily='C2024_anm_font', fontsize=12)
        ax.set_ylabel('Esfuerzo (σ) [ksi]', fontfamily='C2024_anm_font', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        print("✅ Gráfico creado con fuente C2024_anm_font")
        
    except Exception as e:
        print(f"❌ Error creando gráfico: {e}")
        
        # Fallback con fuente por defecto
        ax.plot(deformation, stress_ksi, 'b-o', linewidth=2, markersize=6)
        ax.set_title('Diagrama Esfuerzo-Deformación del Concreto', fontsize=14)
        ax.set_xlabel('Deformación (ε)', fontsize=12)
        ax.set_ylabel('Esfuerzo (σ) [ksi]', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        print("⚠️ Usando fuente por defecto")
    
    # Guardar
    output_file = Path(__file__).parent / 'test_handwritten_debug.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"📊 Gráfico guardado en: {output_file}")
    
    plt.show()
    
    return output_file

if __name__ == "__main__":
    test_current_handwritten_behavior()
    create_comparison_plot()
    
    print("\n" + "="*50)
    print("DIAGNÓSTICO COMPLETADO")