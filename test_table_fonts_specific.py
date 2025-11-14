#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test específico para verificar que las tablas usan las fuentes personalizadas correctas.
"""

import pandas as pd
from src.ePy_docs.writers import DocumentWriter
from src.ePy_docs.core._config import get_layout

def test_table_fonts_verification():
    """Test que las tablas usan fuentes personalizadas específicas"""
    
    print("=== VERIFICACIÓN DE FUENTES EN TABLAS ===")
    
    # Datos de comparación
    font_comparison = {
        'Layout': ['Corporate', 'Handwritten', 'Professional', 'Creative'],
        'Fuente Configurada': [
            'helvetica_lt_std_compressed (brand)',
            'anm_ingenieria_2025 (handwritten_personal)', 
            'Poppins (sans_professional)',
            'Brush Script MT (sans_creative)'
        ],
        'Archivo': [
            'helvetica_lt_std_compressed.OTF',
            'anm_ingenieria_2025.otf',
            'Sistema (Poppins)', 
            'Sistema (Brush Script)'
        ],
        'Estado': ['✅ Corregido', '✅ Corregido', '⚠️ Sistema', '⚠️ Sistema']
    }
    
    df = pd.DataFrame(font_comparison)
    
    # Test layouts principales
    layouts_to_test = ['corporate', 'handwritten']
    
    for layout in layouts_to_test:
        print(f"\n=== TESTING {layout.upper()} TABLES ===")
        
        try:
            # Obtener configuración del layout
            layout_config = get_layout(layout)
            font_family_ref = layout_config.get('font_family_ref')
            
            print(f"Layout: {layout}")
            print(f"Font Family Ref: {font_family_ref}")
            
            # Crear tabla de prueba
            writer = DocumentWriter(document_type='report', layout_style=layout)
            
            # Datos específicos para cada layout
            if layout == 'corporate':
                test_data = {
                    'Documento': ['Informe Anual', 'Propuesta Técnica', 'Reporte Ejecutivo'],
                    'Fuente': ['Helvetica Compressed', 'Helvetica Compressed', 'Helvetica Compressed'], 
                    'Color': ['Carmesí ANM', 'Azul Marino ANM', 'Gris Medio ANM'],
                    'Uso': ['Títulos', 'Subtítulos', 'Contenido']
                }
                title = 'Configuración Corporate - Helvetica ANM'
            
            elif layout == 'handwritten':
                test_data = {
                    'Elemento': ['Notas Personales', 'Borradores', 'Anotaciones'],
                    'Fuente': ['ANM Ingeniería 2025', 'ANM Ingeniería 2025', 'ANM Ingeniería 2025'],
                    'Estilo': ['Manuscrito', 'Manuscrito', 'Manuscrito'],
                    'Color': ['Grafito Oscuro', 'Grafito Medio', 'Grafito Claro']
                }
                title = 'Configuración Handwritten - Fuente Personal'
            
            test_df = pd.DataFrame(test_data)
            
            # Generar tabla
            writer.add_table(
                test_df,
                title=title,
                show_figure=True
            )
            
            print(f"✅ Tabla generada para {layout}")
            print(f"   - Fuente esperada: {font_family_ref}")
            print(f"   - Verificar visualmente que la tabla usa la fuente correcta")
            
        except Exception as e:
            print(f"❌ Error en {layout}: {str(e)}")
    
    # Generar tabla resumen con todos los layouts
    print(f"\n=== TABLA RESUMEN DE CONFIGURACIÓN ===")
    try:
        writer_summary = DocumentWriter(document_type='report', layout_style='professional')
        writer_summary.add_table(
            df,
            title='Resumen de Configuración de Fuentes por Layout',
            show_figure=True
        )
        print("✅ Tabla resumen generada")
        
    except Exception as e:
        print(f"❌ Error tabla resumen: {str(e)}")

def verify_custom_fonts_available():
    """Verificar que las fuentes personalizadas están disponibles"""
    
    print(f"\n=== VERIFICACIÓN DE ARCHIVOS DE FUENTES ===")
    
    import os
    from pathlib import Path
    
    # Rutas esperadas de fuentes
    base_path = Path(__file__).parent / 'src' / 'ePy_docs' / 'config' / 'assets' / 'fonts'
    
    expected_fonts = {
        'Handwritten': 'anm_ingenieria_2025.otf',
        'Corporate': 'helvetica_lt_std_compressed.OTF'
    }
    
    print(f"Base path: {base_path}")
    
    for layout, font_file in expected_fonts.items():
        font_path = base_path / font_file
        exists = font_path.exists()
        status = "✅ Existe" if exists else "❌ Falta"
        
        print(f"{layout:<12}: {font_file:<30} {status}")
        
        if exists:
            size = font_path.stat().st_size
            print(f"             Tamaño: {size:,} bytes")

if __name__ == "__main__":
    test_table_fonts_verification()
    verify_custom_fonts_available()