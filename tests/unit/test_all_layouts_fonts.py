#!/usr/bin/env python3
"""
Test comprehensivo de todos los layouts para verificar el flujo de fuentes
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from ePy_docs.core._images import ImageProcessor
from ePy_docs.core._config import get_layout, get_config_section


class TestLayoutFonts:
    """Test del flujo de fuentes para todos los layouts"""
    
    def get_available_layouts(self):
        """Lista de todos los layouts disponibles"""
        layouts_dir = Path(__file__).parent.parent.parent / 'src' / 'ePy_docs' / 'config' / 'layouts'
        layout_files = list(layouts_dir.glob('*.epyson'))
        return [f.stem for f in layout_files]
    
    def test_all_layouts_have_font_family(self):
        """Verificar que todos los layouts tienen font_family definido"""
        available_layouts = self.get_available_layouts()
        
        for layout_name in available_layouts:
            print(f"\n=== Testing layout: {layout_name} ===")
            
            # Cargar configuración del layout
            layout_data = get_layout(layout_name)
            
            # Verificar que tiene font_family
            assert 'font_family' in layout_data, f"Layout {layout_name} missing font_family"
            
            font_family = layout_data['font_family']
            print(f"✅ {layout_name} -> font_family: {font_family}")
            
            # Verificar que font_family existe en text.epyson
            text_config = get_config_section('text')
            font_families = text_config.get('shared_defaults', {}).get('font_families', {})
            
            assert font_family in font_families, f"Font family {font_family} not found in text.epyson"
            
            family_config = font_families[font_family]
            primary_font = family_config.get('primary')
            
            assert primary_font, f"Font family {font_family} missing primary font"
            print(f"✅ {font_family} -> primary: {primary_font}")
    
    def test_font_family_extraction(self):
        """Test del método _extract_font_family_from_layout"""
        processor = ImageProcessor()
        available_layouts = self.get_available_layouts()
        
        for layout_name in available_layouts:
            print(f"\n=== Testing font extraction: {layout_name} ===")
            
            layout_data = get_layout(layout_name)
            extracted_family = processor._extract_font_family_from_layout(layout_data)
            expected_family = layout_data.get('font_family', 'sans_technical')
            
            assert extracted_family == expected_family, \
                f"Layout {layout_name}: extracted {extracted_family} != expected {expected_family}"
            
            print(f"✅ {layout_name} extraction correct: {extracted_family}")
    
    def test_matplotlib_fonts_setup(self):
        """Test completo del setup de fuentes matplotlib para todos los layouts"""
        import matplotlib.pyplot as plt
        
        processor = ImageProcessor()
        available_layouts = self.get_available_layouts()
        
        for layout_name in available_layouts:
            print(f"\n=== Testing matplotlib setup: {layout_name} ===")
            
            # Ejecutar setup
            font_list = processor.setup_matplotlib_fonts(layout_name)
            
            # Verificar que retorna una lista válida
            assert isinstance(font_list, list), f"Layout {layout_name} did not return list"
            assert len(font_list) > 0, f"Layout {layout_name} returned empty font list"
            
            # Verificar que contiene fallbacks del sistema
            system_fallbacks = ['DejaVu Sans', 'Arial', 'sans-serif']
            for fallback in system_fallbacks:
                assert fallback in font_list, f"Layout {layout_name} missing system fallback {fallback}"
            
            # NUEVO: Verificar que rcParams se configuran
            assert 'sans-serif' in plt.rcParams['font.family'], \
                f"Layout {layout_name} did not configure font.family"
            assert plt.rcParams['font.sans-serif'] == font_list, \
                f"Layout {layout_name} rcParams mismatch"
            
            print(f"✅ {layout_name} font list: {font_list[:3]}... ({len(font_list)} total)")
            print(f"✅ {layout_name} rcParams configured correctly")
    
    def test_handwritten_specific_flow(self):
        """Test específico para el flujo handwritten"""
        print("\n=== SPECIFIC HANDWRITTEN TEST ===")
        
        processor = ImageProcessor()
        
        # 1. Verificar configuración
        layout_data = get_layout('handwritten')
        font_family = layout_data.get('font_family')
        print(f"1. handwritten layout -> font_family: {font_family}")
        
        # 2. Verificar que es handwritten_personal
        assert font_family == 'handwritten_personal', f"Expected handwritten_personal, got {font_family}"
        
        # 3. Verificar configuración de handwritten_personal
        text_config = get_config_section('text')
        font_families = text_config.get('shared_defaults', {}).get('font_families', {})
        family_config = font_families.get('handwritten_personal', {})
        
        primary_font = family_config.get('primary')
        font_file_template = family_config.get('font_file_template')
        
        print(f"2. handwritten_personal -> primary: {primary_font}")
        print(f"3. template: {font_file_template}")
        
        assert primary_font == 'C2024_anm_font', f"Expected C2024_anm_font, got {primary_font}"
        assert font_file_template == '{font_name}.otf', f"Unexpected template: {font_file_template}"
        
        # 4. Verificar archivo
        package_root = Path(__file__).parent.parent.parent / 'src' / 'ePy_docs'
        font_filename = font_file_template.format(font_name=primary_font)
        font_file = package_root / 'config' / 'assets' / 'fonts' / font_filename
        
        print(f"4. Expected file: {font_file}")
        assert font_file.exists(), f"Font file not found: {font_file}"
        
        # 5. Test extracción
        extracted_family = processor._extract_font_family_from_layout(layout_data)
        print(f"5. Extracted font_family: {extracted_family}")
        assert extracted_family == 'handwritten_personal', f"Extraction failed: {extracted_family}"
        
        # 6. Test setup completo
        font_list = processor.setup_matplotlib_fonts('handwritten')
        print(f"6. Final font list: {font_list}")
        
        # Debe contener handwritten_personal como familia (el sistema ahora usa alias)
        assert 'handwritten_personal' in font_list, f"handwritten_personal not in font list: {font_list}"
        
        print("✅ HANDWRITTEN TEST PASSED")
    
    def test_font_registration_for_all_layouts(self):
        """Test registro de fuentes para todos los layouts que tienen archivos"""
        processor = ImageProcessor()
        available_layouts = self.get_available_layouts()
        format_config = get_config_section('format')
        font_families = format_config.get('font_families', {})
        
        for layout_name in available_layouts:
            print(f"\n=== Testing font registration: {layout_name} ===")
            
            layout_data = get_layout(layout_name)
            font_family = layout_data.get('font_family')
            
            if font_family in font_families:
                family_config = font_families[font_family]
                primary_font = family_config.get('primary')
                font_file_template = family_config.get('font_file_template')
                
                print(f"  Layout: {layout_name}")
                print(f"  Font family: {font_family}")
                print(f"  Primary font: {primary_font}")
                print(f"  Template: {font_file_template}")
                
                if font_file_template:
                    # Test registro
                    result = processor._register_font_if_exists(primary_font)
                    print(f"  Registration result: {'✅' if result else '⚠️ (system font)'}")
                    
                    # Test setup completo
                    font_list = processor.setup_matplotlib_fonts(layout_name)
                    assert primary_font in font_list, f"Primary font {primary_font} not in final list for {layout_name}"
                    print(f"  ✅ {primary_font} present in final font list")
                else:
                    print(f"  ⚠️ No template - system font: {primary_font}")


if __name__ == "__main__":
    # Para usar con pytest: python -m pytest tests/unit/test_all_layouts_fonts.py -v
    # Para debug manual: python tests/unit/test_all_layouts_fonts.py
    
    test_instance = TestLayoutFonts()
    
    print("=== MANUAL LAYOUT FONT TESTING ===")
    
    try:
        print("\n1. Testing all layouts have font_family...")
        test_instance.test_all_layouts_have_font_family()
        
        print("\n2. Testing font family extraction...")
        test_instance.test_font_family_extraction()
        
        print("\n3. Testing matplotlib fonts setup...")
        test_instance.test_matplotlib_fonts_setup()
        
        print("\n4. Testing handwritten specific flow...")
        test_instance.test_handwritten_specific_flow()
        
        print("\n5. Testing font registration for all layouts...")
        test_instance.test_font_registration_for_all_layouts()
        
        print("\n🎉 ALL LAYOUT FONT TESTS PASSED!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()