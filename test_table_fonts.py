"""
Test para verificar si las fuentes se están aplicando correctamente en las tablas
"""

import pandas as pd
import matplotlib.pyplot as plt
from ePy_docs import DocumentWriter

# Crear datos de ejemplo
data = {
    'Column_1': ['Row 1', 'Row 2', 'Row 3'],
    'Column_2': [100, 200, 300],
    'Column_3': ['A', 'B', 'C']
}
df = pd.DataFrame(data)

print("=" * 70)
print("TEST: Verificando fuentes en tablas para diferentes layouts")
print("=" * 70)

layouts_to_test = [
    ('professional', 'Source Sans Pro'),
    ('academic', 'Times New Roman'),
    ('handwritten', 'anm_ingenieria_2025'),
    ('classic', 'Georgia')
]

for layout_name, expected_font in layouts_to_test:
    print(f"\n📝 Testing layout: {layout_name}")
    print(f"   Expected font: {expected_font}")
    
    try:
        writer = DocumentWriter(
            document_type='report',
            layout_style=layout_name
        )
        
        writer.add_h2(f"Test Table - {layout_name}") \
              .add_table(df, title=f"Sample Table with {layout_name} layout")
        
        # Verificar que se generó la tabla
        if writer._counters['table'] == 1:
            print(f"   ✅ Table generated successfully")
            
            # Verificar la configuración de fuentes
            from ePy_docs.core._tables import TableConfigManager
            config_mgr = TableConfigManager()
            font_config, _, _, _, _, font_family = config_mgr.get_layout_config(layout_name, 'report')
            
            print(f"   Font family from config: {font_family}")
            print(f"   Primary font: {font_config.get('primary')}")
            print(f"   Fallback font: {font_config.get('fallback')}")
            
            # Verificar que la fuente principal coincide
            if font_config.get('primary') == expected_font:
                print(f"   ✅ Font configuration is correct")
            else:
                print(f"   ❌ Font mismatch! Expected '{expected_font}', got '{font_config.get('primary')}'")
        else:
            print(f"   ❌ Table generation failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)
