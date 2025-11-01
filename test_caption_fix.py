"""
Test para verificar que no hay duplicación de captions en las tablas.
"""

from ePy_docs.writers import DocumentWriter
import pandas as pd

# Crear datos de prueba
data = {
    'Columna A': [1, 2, 3],
    'Columna B': [4, 5, 6],
    'Columna C': [7, 8, 9]
}
df = pd.DataFrame(data)

# Inicializar writer con layout handwritten
writer = DocumentWriter(document_type='report', layout_style='handwritten')

# Agregar una tabla con título
writer.add_h1("Test de Captions de Tabla")
writer.add_colored_table(df, title='Mi Tabla de Prueba')

# Generar solo el QMD para revisar el markdown
try:
    result = writer.generate(html=False, pdf=False, qmd=True, output_filename="test_caption_fix")
    print(f"✓ QMD generado: {result['qmd']}")
    
    # Leer y mostrar el contenido del QMD
    with open(result['qmd'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n=== CONTENIDO DEL QMD ===")
    print(content)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()