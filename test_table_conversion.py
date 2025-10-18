"""Script de prueba para verificar la conversión de tablas Markdown."""

from src.ePy_docs.writers import DocumentWriter
from pathlib import Path

# Crear un documento de prueba - Nueva API simplificada
writer = DocumentWriter("report", layout_style="technical")

# Configurar el directorio de salida
output_dir = Path("results/report")
output_dir.mkdir(parents=True, exist_ok=True)

# Agregar el archivo Markdown con tablas
print("📄 Procesando archivo Markdown con tablas...")
writer.add_markdown_file(
    file_path="test_markdown_tables.md",
    convert_tables=True
)

# Generar el documento
print("🔄 Generando documento...")
result = writer.generate(
    html=True,
    pdf=False,
    markdown=True,
    output_filename="test_table_conversion"
)

print("\n✅ Documento generado:")
for format_type, path in result.items():
    print(f"   {format_type}: {path}")

print("\n📊 Verificar que las tablas Markdown se convirtieron correctamente en el .qmd generado")
