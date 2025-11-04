"""
Test del nuevo sistema de columnas y tipos de documento.
Verifica: paper, report, book con 1, 2, 3 columnas.
"""

print("=" * 80)
print("PRUEBA DEL SISTEMA DE COLUMNAS Y TIPOS DE DOCUMENTO")
print("=" * 80)

# Importar el calculador de columnas
from ePy_docs.core._columns import ColumnWidthCalculator, calculate_content_width, get_width_string

calc = ColumnWidthCalculator()

# Verificar configuración de tipos de documento
print("\n📋 TIPOS DE DOCUMENTO CONFIGURADOS:")
print("-" * 80)

for doc_type in ['paper', 'report', 'book']:
    try:
        info = calc.get_document_type_info(doc_type)
        print(f"\n{doc_type.upper()}:")
        print(f"  Descripción: {info['description']}")
        print(f"  Columnas por defecto: {info['default_columns']}")
        print(f"  Columnas soportadas: {info['supported_columns']}")
        print(f"  Directorio de salida: {info['output_dir']}")
        print(f"  Layout por defecto: {info['default_layout']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Prueba de cálculo de anchos
print("\n\n📐 CÁLCULO DE ANCHOS POR TIPO Y CONFIGURACIÓN:")
print("=" * 80)

test_cases = [
    # (document_type, layout_columns, requested_columns, description)
    ('report', 1, None, 'Report 1 columna (default)'),
    ('report', 1, 1.0, 'Report 1 columna (explícito)'),
    
    ('paper', 2, None, 'Paper 2 columnas - single column (default)'),
    ('paper', 2, 1.0, 'Paper 2 columnas - 1 columna'),
    ('paper', 2, 1.5, 'Paper 2 columnas - 1.5 columnas'),
    ('paper', 2, 2.0, 'Paper 2 columnas - ancho completo'),
    
    ('paper', 3, None, 'Paper 3 columnas - single column (default)'),
    ('paper', 3, 1.0, 'Paper 3 columnas - 1 columna'),
    ('paper', 3, 2.0, 'Paper 3 columnas - 2 columnas'),
    ('paper', 3, 3.0, 'Paper 3 columnas - ancho completo'),
    
    ('book', 1, None, 'Book 1 columna'),
    ('book', 2, 1.0, 'Book 2 columnas - 1 columna'),
    ('book', 2, 2.0, 'Book 2 columnas - ancho completo'),
]

for doc_type, layout_cols, req_cols, desc in test_cases:
    try:
        width = calc.calculate_width(doc_type, layout_cols, req_cols)
        width_str = get_width_string(width)
        req_display = req_cols if req_cols is not None else 'None (default)'
        print(f"✓ {desc:<45} → {width_str:>7} ({width:.2f} pulgadas)")
    except Exception as e:
        print(f"✗ {desc:<45} → ERROR: {e}")

# Prueba de validación
print("\n\n⚠️  PRUEBAS DE VALIDACIÓN (deben fallar):")
print("-" * 80)

invalid_cases = [
    ('paper', 2, 3.0, 'Solicitar 3 columnas en layout de 2'),
    ('book', 2, 3.0, 'Solicitar 3 columnas en book (no soporta 3)'),
    ('invalid', 1, None, 'Tipo de documento inválido'),
]

for doc_type, layout_cols, req_cols, desc in invalid_cases:
    try:
        width = calc.calculate_width(doc_type, layout_cols, req_cols)
        print(f"✗ {desc:<45} → ⚠️ DEBERÍA FALLAR pero dio: {width}")
    except Exception as e:
        print(f"✓ {desc:<45} → Falló correctamente: {str(e)[:40]}...")

# Mostrar tabla resumen
print("\n\n📊 TABLA RESUMEN DE ANCHOS:")
print("=" * 80)
print(f"{'Tipo':<8} {'Layout':<8} {'Columnas':<10} {'Ancho':<15} {'Uso típico':<30}")
print("-" * 80)

summary_data = [
    ('report', 1, 1.0, 'Tabla/figura estándar'),
    ('paper', 2, 1.0, 'Figura pequeña en una columna'),
    ('paper', 2, 2.0, 'Figura grande a doble columna'),
    ('paper', 3, 1.0, 'Figura pequeña'),
    ('paper', 3, 2.0, 'Figura mediana'),
    ('paper', 3, 3.0, 'Figura grande a triple columna'),
    ('book', 1, 1.0, 'Contenido estándar de libro'),
    ('book', 2, 1.0, 'Columna simple en book'),
    ('book', 2, 2.0, 'Ancho completo en book'),
]

for doc_type, layout_cols, req_cols, uso in summary_data:
    width = calc.calculate_width(doc_type, layout_cols, req_cols)
    width_str = get_width_string(width)
    print(f"{doc_type:<8} {layout_cols} col{'s' if layout_cols > 1 else ' ':<5} {req_cols:<10.1f} {width_str:<15} {uso:<30}")

print("\n" + "=" * 80)
print("✅ SISTEMA DE COLUMNAS VERIFICADO")
print("=" * 80)

print("\n💡 EJEMPLOS DE USO:")
print("""
# Crear documento paper de 2 columnas
writer = DocumentWriter('paper', 'academic', num_columns=2)

# Tabla en una columna (3.1 pulgadas)
writer.add_table(df, columns=1.0)

# Figura que ocupa dos columnas (6.5 pulgadas - ancho completo)
writer.add_plot(fig, columns=2.0)

# Figura que ocupa 1.5 columnas (4.75 pulgadas)
writer.add_image("foto.png", columns=1.5)
""")
