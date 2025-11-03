#!/usr/bin/env python3
"""
Test simple para diagnosticar el problema de layouts
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ePy_docs.core._images import ImageProcessor
from ePy_docs.core._config import get_layout, get_config_section

def test_handwritten_flow():
    """Test específico del flujo handwritten"""
    print("=== DIAGNOSTICO HANDWRITTEN FLOW ===")
    
    processor = ImageProcessor()
    
    # 1. Cargar layout handwritten
    print("\n1. CARGANDO LAYOUT HANDWRITTEN:")
    layout_data = get_layout('handwritten')
    print(f"Layout data keys: {list(layout_data.keys())}")
    
    # 2. Verificar font_family en nivel raíz
    print("\n2. VERIFICANDO FONT_FAMILY:")
    font_family = layout_data.get('font_family')
    print(f"font_family en nivel raíz: {font_family}")
    
    # 3. Test extracción actual
    print("\n3. TEST EXTRACCIÓN ACTUAL:")
    extracted_family = processor._extract_font_family_from_layout(layout_data)
    print(f"Extraído por método: {extracted_family}")
    print(f"¿Coincide? {'✅' if extracted_family == font_family else '❌'}")
    
    # 4. Verificar configuración de font families
    print("\n4. VERIFICANDO CONFIGURACIÓN FONT FAMILIES:")
    format_config = get_config_section('format')
    font_families = format_config.get('font_families', {})
    
    if font_family in font_families:
        family_config = font_families[font_family]
        primary_font = family_config.get('primary')
        font_file_template = family_config.get('font_file_template')
        
        print(f"Configuración encontrada para {font_family}:")
        print(f"  - primary: {primary_font}")
        print(f"  - font_file_template: {font_file_template}")
        
        # 5. Verificar archivo
        if font_file_template:
            package_root = Path(__file__).parent.parent / 'src' / 'ePy_docs'
            font_filename = font_file_template.format(font_name=primary_font)
            font_file = package_root / 'config' / 'assets' / 'fonts' / font_filename
            
            print(f"\n5. VERIFICANDO ARCHIVO:")
            print(f"package_root: {package_root}")
            print(f"Archivo esperado: {font_file}")
            print(f"Existe: {'✅' if font_file.exists() else '❌'}")
            
            # Verificar también la ruta que usa el código real
            actual_package_root = Path(__file__).parent.parent / 'src' / 'ePy_docs' / 'core' / '_images.py'
            actual_package_root = actual_package_root.parent.parent
            actual_font_file = actual_package_root / 'config' / 'assets' / 'fonts' / font_filename
            print(f"Ruta del código real: {actual_font_file}")
            print(f"Código real existe: {'✅' if actual_font_file.exists() else '❌'}")
        
        # 6. Test setup completo
        print("\n6. TEST SETUP COMPLETO:")
        font_list = processor.setup_matplotlib_fonts('handwritten')
        print(f"Font list resultante: {font_list}")
        
        if primary_font in font_list:
            print(f"✅ {primary_font} está en la lista")
        else:
            print(f"❌ {primary_font} NO está en la lista")
    
    else:
        print(f"❌ Font family {font_family} NO encontrada en configuración")

def test_all_layouts_basic():
    """Test básico de todos los layouts"""
    print("\n=== TEST BÁSICO TODOS LOS LAYOUTS ===")
    
    layouts_dir = Path(__file__).parent.parent / 'src' / 'ePy_docs' / 'config' / 'layouts'
    layout_files = list(layouts_dir.glob('*.epyson'))
    layout_names = [f.stem for f in layout_files]
    
    print(f"Layouts encontrados: {layout_names}")
    
    processor = ImageProcessor()
    
    for layout_name in layout_names:
        print(f"\n--- Testing {layout_name} ---")
        
        try:
            # Cargar layout
            layout_data = get_layout(layout_name)
            font_family = layout_data.get('font_family')
            
            # Test extracción
            extracted_family = processor._extract_font_family_from_layout(layout_data)
            
            # Test setup
            font_list = processor.setup_matplotlib_fonts(layout_name)
            
            print(f"  font_family: {font_family}")
            print(f"  extracted: {extracted_family}")
            print(f"  match: {'✅' if extracted_family == font_family else '❌'}")
            print(f"  font_list length: {len(font_list)}")
            print(f"  first font: {font_list[0] if font_list else 'None'}")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

if __name__ == "__main__":
    test_handwritten_flow()
    test_all_layouts_basic()