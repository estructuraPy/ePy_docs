"""
Test para verificar que los espaciadores funcionan correctamente al importar archivos MD/QMD
"""
import sys
sys.path.append('src')

from ePy_docs import DocumentWriter
import os

print("=== Test: Espaciadores en importación de archivos MD/QMD ===\n")

# Crear archivos de prueba
test_md_content = """## Sección Importada desde MD

Este contenido viene de un archivo Markdown externo.

- Item 1
- Item 2
- Item 3

Este es un párrafo final del archivo MD."""

test_qmd_content = """---
title: "Test QMD"
---

## Sección Importada desde QMD

Este contenido viene de un archivo Quarto externo.

**Nota importante**: Este texto está en negrita.

```python
# Código de ejemplo
x = 10
print(x)
```
"""

# Crear archivos temporales
os.makedirs("temp_test", exist_ok=True)

with open("temp_test/test_section.md", "w", encoding="utf-8") as f:
    f.write(test_md_content)

with open("temp_test/test_section.qmd", "w", encoding="utf-8") as f:
    f.write(test_qmd_content)

# Crear documento y probar importación
doc = DocumentWriter('report', layout_style='minimal')

# Agregar contenido previo
doc.add_h1("Documento Principal")
doc.add_text("Este es el contenido inicial del documento.")

# Importar archivo MD
print("1. Importando archivo MD...")
doc.add_markdown_file("temp_test/test_section.md")

# Agregar más contenido
doc.add_text("Contenido intermedio después del MD importado.")

# Importar archivo QMD (sin YAML)
print("2. Importando archivo QMD (sin YAML)...")
doc.add_quarto_file("temp_test/test_section.qmd", include_yaml=False)

# Agregar contenido final
doc.add_h2("Sección Final")
doc.add_text("Este es el contenido final del documento.")

# Generar
print("3. Generando documento...")
result = doc.generate(output_filename="Test_Spacers_MD_QMD", html=True, pdf=False)

# Verificar contenido generado
qmd_path = result['qmd']
with open(qmd_path, 'r', encoding='utf-8') as f:
    generated_content = f.read()

print(f"\n✓ Documento generado: {result['html']}")
print(f"✓ Archivo QMD: {qmd_path}")

# Verificar espaciadores
spacer_count = generated_content.count('\n\n\n')  # Triple newline indica espaciado correcto
print(f"\n✓ Espaciadores encontrados: {spacer_count}")

if spacer_count >= 2:
    print("✓ Los espaciadores se agregaron correctamente")
else:
    print("⚠ Advertencia: Pocos espaciadores detectados")

# Limpiar archivos temporales
import shutil
shutil.rmtree("temp_test")
print("\n✓ Archivos temporales eliminados")

print("\nVerificar que:")
print("  - El contenido importado está separado correctamente")
print("  - No hay problemas de renderizado markdown")
print("  - Las secciones están claramente diferenciadas")
