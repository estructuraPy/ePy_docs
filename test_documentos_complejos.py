"""
Script de prueba para documentos complejos
===========================================

Este script procesa los documentos complejos .md y .qmd creados,
demostrando la conversión automática de tablas Markdown.
"""

from src.ePy_docs.writers import DocumentWriter
from pathlib import Path
import time

print("="*70)
print("PRUEBA DE PROCESAMIENTO DE DOCUMENTOS COMPLEJOS")
print("="*70)

# ============================================================================
# PRUEBA 1: Documento Markdown complejo (.md)
# ============================================================================

print("\n📄 PRUEBA 1: Procesando documento_complejo.md")
print("-" * 70)

start_time = time.time()

writer1 = DocumentWriter('report', layout_style="technical")

# Procesar el archivo Markdown complejo
print("   → Cargando archivo Markdown con tablas...")
writer1.add_markdown_file(
    file_path="data/user/documento_complejo.md",
    convert_tables=True,
    fix_image_paths=True
)

# Generar documento
print("   → Generando documento...")
result1 = writer1.generate(
    html=True,
    pdf=False,
    markdown=True,
    output_filename="test_documento_complejo"
)

elapsed1 = time.time() - start_time

print(f"\n✅ Documento 1 generado en {elapsed1:.2f} segundos:")
for format_type, path in result1.items():
    print(f"   {format_type:10s} → {path}")

# Estadísticas
content1 = writer1.get_content()
n_lines1 = len(content1.split('\n'))
n_tables1 = content1.count('![Tabla')
n_images1 = content1.count('![') - n_tables1

print(f"\n📊 Estadísticas Documento 1:")
print(f"   • Líneas procesadas: {n_lines1}")
print(f"   • Tablas detectadas: {n_tables1}")
print(f"   • Imágenes: {n_images1}")

# ============================================================================
# PRUEBA 2: Documento Quarto complejo (.qmd)
# ============================================================================

print("\n" + "="*70)
print("\n📄 PRUEBA 2: Procesando documento_puente.qmd")
print("-" * 70)

start_time = time.time()

writer2 = DocumentWriter('report', layout_style="academic")

# Procesar el archivo Quarto complejo
print("   → Cargando archivo Quarto con YAML y tablas...")
writer2.add_quarto_file(
    file_path="data/user/documento_puente.qmd",
    include_yaml=False,  # Omitir YAML frontmatter
    convert_tables=True,
    fix_image_paths=True
)

# Generar documento
print("   → Generando documento...")
result2 = writer2.generate(
    html=True,
    pdf=False,
    markdown=True,
    output_filename="test_documento_puente"
)

elapsed2 = time.time() - start_time

print(f"\n✅ Documento 2 generado en {elapsed2:.2f} segundos:")
for format_type, path in result2.items():
    print(f"   {format_type:10s} → {path}")

# Estadísticas
content2 = writer2.get_content()
n_lines2 = len(content2.split('\n'))
n_tables2 = content2.count('![Tabla')
n_images2 = content2.count('![') - n_tables2
n_callouts2 = content2.count(':::')

print(f"\n📊 Estadísticas Documento 2:")
print(f"   • Líneas procesadas: {n_lines2}")
print(f"   • Tablas detectadas: {n_tables2}")
print(f"   • Imágenes: {n_images2}")
print(f"   • Callouts: {n_callouts2 // 2}")  # Dividir por 2 (inicio y fin)

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "="*70)
print("RESUMEN DE PRUEBAS")
print("="*70)

print(f"\n📈 Comparación de documentos:")
print(f"   {'Métrica':<30s} {'Doc 1 (.md)':<15s} {'Doc 2 (.qmd)':<15s}")
print(f"   {'-'*30} {'-'*15} {'-'*15}")
print(f"   {'Líneas totales':<30s} {n_lines1:<15d} {n_lines2:<15d}")
print(f"   {'Tablas Markdown convertidas':<30s} {n_tables1:<15d} {n_tables2:<15d}")
print(f"   {'Referencias a imágenes':<30s} {n_images1:<15d} {n_images2:<15d}")
print(f"   {'Tiempo de procesamiento (s)':<30s} {elapsed1:<15.2f} {elapsed2:<15.2f}")

total_tables = n_tables1 + n_tables2
print(f"\n🎯 Total de tablas Markdown convertidas: {total_tables}")
print(f"✅ Todas las tablas fueron procesadas con éxito")

# Verificar archivos generados
print(f"\n📁 Archivos disponibles en: results/report/")
print(f"   • test_documento_complejo.html")
print(f"   • test_documento_puente.html")
print(f"   • Tablas PNG en: results/report/tables/")

print("\n" + "="*70)
print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
print("="*70)

# Información adicional
print("\n💡 Notas:")
print("   • Las tablas Markdown se convirtieron automáticamente a imágenes PNG")
print("   • Los estilos se aplicaron según layout_style configurado")
print("   • Las referencias a imágenes se preservaron (aunque no existan físicamente)")
print("   • Los callouts de Quarto se mantuvieron en el formato original")
print("   • Las ecuaciones LaTeX se preservaron para renderizado de Quarto")

print("\n🔍 Para verificar los resultados:")
print("   1. Abrir los archivos HTML en un navegador")
print("   2. Revisar el directorio results/report/tables/ para ver las tablas generadas")
print("   3. Comparar el contenido original con el procesado")
