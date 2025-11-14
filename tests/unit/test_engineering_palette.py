"""
Test unitario para verificar la paleta 'engineering'
"""

import pytest
import pandas as pd
from ePy_docs.core._config import get_config_section
from ePy_docs import DocumentWriter


class TestEngineeringPalette:
    """Tests para verificar que la paleta 'engineering' funciona correctamente."""
    
    def test_engineering_palette_exists(self):
        """Verificar que la paleta 'engineering' existe en la configuración."""
        colors_config = get_config_section('colors')
        assert 'palettes' in colors_config
        assert 'engineering' in colors_config['palettes']
    
    def test_engineering_palette_has_correct_structure(self):
        """Verificar que la paleta 'engineering' tiene todos los colores requeridos."""
        colors_config = get_config_section('colors')
        eng_palette = colors_config['palettes']['engineering']
        
        # Verificar que todos los colores requeridos están presentes
        required_keys = ['page_background', 'primary', 'secondary', 'tertiary', 
                        'quaternary', 'quinary', 'senary', 'description']
        for key in required_keys:
            assert key in eng_palette, f"Missing key: {key}"
    
    def test_engineering_palette_colors_are_valid_rgb(self):
        """Verificar que todos los colores de la paleta son RGB válidos."""
        colors_config = get_config_section('colors')
        eng_palette = colors_config['palettes']['engineering']
        
        color_keys = ['page_background', 'primary', 'secondary', 'tertiary', 
                     'quaternary', 'quinary', 'senary']
        
        for key in color_keys:
            color = eng_palette[key]
            assert isinstance(color, list), f"{key} should be a list"
            assert len(color) == 3, f"{key} should have 3 values (RGB)"
            for val in color:
                assert 0 <= val <= 255, f"{key} has invalid RGB value: {val}"
    
    def test_engineering_palette_has_proper_gradient(self):
        """Verificar que la paleta tiene un gradiente apropiado (claro a oscuro)."""
        colors_config = get_config_section('colors')
        eng_palette = colors_config['palettes']['engineering']
        
        # Los valores RGB de primary deberían ser mayores que senary (más claro a más oscuro)
        primary_brightness = sum(eng_palette['primary'])
        senary_brightness = sum(eng_palette['senary'])
        
        assert primary_brightness > senary_brightness, \
            "Primary should be brighter than senary"
    
    def test_engineering_palette_with_colored_table(self):
        """Verificar que add_colored_table funciona con la paleta 'engineering'."""
        # Crear datos de ejemplo
        data = {
            'Node': ['N1', 'N2', 'N3'],
            'Force_kN': [100.0, 150.0, 200.0],
            'Displacement_mm': [2.5, 3.8, 5.1]
        }
        df = pd.DataFrame(data)
        
        # Crear writer
        writer = DocumentWriter(
            document_type='report',
            layout_style='professional'
        )
        
        # Intentar crear tabla coloreada con paleta engineering
        try:
            writer.add_colored_table(
                df,
                title="Test Engineering Palette",
                palette_name='engineering',
                highlight_columns=['Force_kN']
            )
            # Si llegamos aquí sin excepción, el test pasa
            assert writer._counters['table'] == 1
        except ValueError as e:
            pytest.fail(f"add_colored_table failed with engineering palette: {e}")
    
    def test_engineering_palette_description(self):
        """Verificar que la paleta tiene una descripción apropiada."""
        colors_config = get_config_section('colors')
        eng_palette = colors_config['palettes']['engineering']
        
        description = eng_palette['description']
        assert isinstance(description, str)
        assert len(description) > 0
        assert 'ingeniería' in description.lower() or 'engineering' in description.lower() or 'técnica' in description.lower()
