#!/usr/bin/env python3
"""
Test de diferenciación visual de callouts en PDF
"""

import os
import sys

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

def test_callouts():
    """Test de callouts en PDF."""
    
    print("📝 Generando test de diferenciación de callouts...")
    
    writer = DocumentWriter(
        document_type="report",
        layout_style="minimal",
        language="es"
    )
    
    writer.add_h1("Test de Diferenciación Visual")
    
    writer.add_h2("1. Display Chunk (Fondo Claro)")
    writer.add_content("Debería verse con fondo claro/gris y borde izquierdo gris.")
    writer.add_code_chunk(
        code='''# Código de ejemplo - Display
def ejemplo_display():
    print("Este chunk tiene fondo claro")
    return "Display"''',
        language="python",
        chunk_type="display",
        caption="Chunk de Display - Fondo Claro"
    )
    
    writer.add_h2("2. Executable Chunk (Fondo Oscuro/Naranja)")
    writer.add_content("Debería verse con fondo naranja/café y borde izquierdo naranja.")
    writer.add_code_chunk(
        code='''# Código ejecutable - Executable
import datetime
print("Este chunk tiene fondo naranja")
print(f"Ejecutado: {datetime.datetime.now()}")
resultado = "Executable"
print(f"Resultado: {resultado}")''',
        language="python",
        chunk_type="executable",
        caption="Chunk Ejecutable - Fondo Naranja/Café"
    )
    
    writer.add_h2("3. Comparación Lado a Lado")
    writer.add_h3("Display #2")
    writer.add_code_chunk(
        code='print("Display - claro")',
        language="python",
        chunk_type="display"
    )
    
    writer.add_h3("Executable #2")
    writer.add_code_chunk(
        code='print("Executable - oscuro")',
        language="python",
        chunk_type="executable"
    )
    
    # Generar PDF y HTML
    results = writer.generate(
        pdf=True,
        html=True,
        markdown=False,
        qmd=False,
        output_filename="test_callouts_final"
    )
    
    print("\n✅ Generación completada!")
    
    html_path = results.get('html')
    pdf_path = results.get('pdf')
    
    if html_path and os.path.exists(html_path):
        print(f"🌐 HTML: {html_path}")
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"📄 PDF: {pdf_path}")
        print("\n🔍 VERIFICAR EN EL PDF:")
        print("  ✓ Display chunks: Fondo claro/gris con borde izquierdo gris")
        print("  ✓ Executable chunks: Fondo naranja/café con borde izquierdo naranja")
        return True
    else:
        print("❌ Error: PDF no generado")
        return False

if __name__ == "__main__":
    try:
        success = test_callouts()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
