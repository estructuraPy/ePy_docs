"""
Demostración de la API Unificada de ePy_docs
============================================

Este script muestra cómo usar la nueva API simplificada con DocumentWriter.
"""

from src.ePy_docs.writers import DocumentWriter
import pandas as pd

print("="*70)
print("DEMO: API UNIFICADA - DocumentWriter")
print("="*70)

# =============================================================================
# 1. API Unificada - Forma Explícita
# =============================================================================
print("\n1️⃣  API UNIFICADA - Forma Explícita")
print("-" * 70)

# Para reportes técnicos
report_writer = DocumentWriter(document_type='report')
print("✅ DocumentWriter('report') creado")

# Para artículos académicos
paper_writer = DocumentWriter(document_type='paper')
print("✅ DocumentWriter('paper') creado")

# Con estilo de layout explícito
custom_writer = DocumentWriter(document_type='report', layout_style='technical')
print("✅ DocumentWriter('report', layout_style='technical') creado")

# =============================================================================
# 2. Ejemplo Completo con Contenido
# =============================================================================
print("\n2️⃣  EJEMPLO COMPLETO")
print("-" * 70)

# Crear writer para reporte técnico
writer = DocumentWriter('report', layout_style='technical')

# Agregar contenido
writer.add_h1("Análisis Estructural")
writer.add_text("Este es un reporte generado con la API unificada.")

# Agregar tabla
df = pd.DataFrame({
    'Elemento': ['Columna C1', 'Viga V1', 'Losa L1'],
    'Material': ['Concreto f\'c=280', 'Concreto f\'c=280', 'Concreto f\'c=210'],
    'Dimensiones': ['30x40 cm', '35x45 cm', 'e=15 cm']
})
writer.add_table(df, title="Especificaciones de Elementos")

print(f"Buffer size: {len(writer.content_buffer)} items")
print(f"Tablas: {writer.table_counter}")

# =============================================================================
# 3. Comparación: Antes vs Ahora
# =============================================================================
print("\n3️⃣  COMPARACIÓN DE SINTAXIS")
print("-" * 70)

comparison = pd.DataFrame({
    'Aspecto': [
        'Clase base',
        'Reporte técnico',
        'Artículo académico',
        'Explícito',
        'Validación'
    ],
    'Antes (3 clases)': [
        'BaseDocumentWriter',
        'ReportWriter()',
        'PaperWriter()',
        'No',
        'No'
    ],
    'Ahora (1 clase)': [
        'DocumentWriter',
        "DocumentWriter('report')",
        "DocumentWriter('paper')",
        'Sí - tipo explícito',
        'Sí - ValueError'
    ]
})

for _, row in comparison.iterrows():
    print(f"{row['Aspecto']:20} | {row['Ahora (1 clase)']}")

# =============================================================================
# 4. Validación de Tipos
# =============================================================================
print("\n4️⃣  VALIDACIÓN DE TIPOS")
print("-" * 70)

try:
    invalid_writer = DocumentWriter('invalid_type')
    print("❌ La validación no funcionó")
except ValueError as e:
    print(f"✅ Validación correcta: {e}")

# =============================================================================
# RESUMEN
# =============================================================================
print("\n" + "="*70)
print("RESUMEN DE BENEFICIOS")
print("="*70)
print("✅ API más simple y directa")
print("✅ Tipos de documento explícitos")
print("✅ Defaults inteligentes (classic/academic)")
print("✅ Validación de parámetros")
print("✅ Código más limpio y mantenible")
print("="*70)
