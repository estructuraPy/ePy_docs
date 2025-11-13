"""Test real del notebook - reproducir el caso de uso del usuario"""
from ePy_docs.writers import DocumentWriter
import pandas as pd

# Crear writer como en el notebook
writer = DocumentWriter("report", "handwritten", language="es")

# Verificar configuraciones disponibles
print("="*70)
print("DOCUMENT TYPES DISPONIBLES:")
print("="*70)
for doc_type, desc in writer.get_available_document_types().items():
    print(f"  {doc_type:15s}: {desc}")

print("\n" + "="*70)
print("LAYOUTS DISPONIBLES:")
print("="*70)
for layout, desc in writer.get_available_layouts().items():
    print(f"  {layout:15s}: {desc}")

print("\n" + "="*70)
print("CONFIGURACIÓN ACTUAL:")
print("="*70)
print(f"  Document type: {writer.document_type}")
print(f"  Layout: {writer.layout_style}")
print(f"  Language: {writer.language}")

# Agregar contenido simple
writer.add_heading("Informe de Prueba", level=1)
writer.add_text("Este es un informe de prueba para verificar la configuración.")

# Crear una tabla simple
df = pd.DataFrame({
    'Columna A': [1, 2, 3],
    'Columna B': [4, 5, 6]
})
writer.add_table(df, title="Tabla de Prueba")

print("\n" + "="*70)
print("CONTENIDO GENERADO:")
print("="*70)
print(f"  Buffer length: {len(writer.content_buffer)} items")
print(f"  Table counter: {writer.table_counter}")

# Intentar generar
print("\n" + "="*70)
print("GENERANDO DOCUMENTO...")
print("="*70)

try:
    result = writer.generate(
        markdown=False,
        html=False, 
        pdf=False,
        qmd=True,
        output_filename="test_report_handwritten"
    )
    print("✓ Documento generado exitosamente")
    print(f"  QMD: {result.get('qmd', 'N/A')}")
    
    # Verificar el QMD generado
    if result.get('qmd'):
        with open(result['qmd'], 'r', encoding='utf-8') as f:
            qmd_content = f.read()
        
        print("\n" + "="*70)
        print("VERIFICACIÓN DEL QMD GENERADO:")
        print("="*70)
        
        checks = [
            ('documentclass: report', 'Document class correcto'),
            ('fontspec', 'Configuración de fuentes custom'),
            ('handwritten', 'Referencias a layout handwritten'),
            ('definecolor', 'Definiciones de color'),
        ]
        
        for search_str, desc in checks:
            found = search_str in qmd_content
            status = "✓" if found else "✗"
            print(f"  {status} {desc}")
        
        # Mostrar primeras líneas del YAML
        print("\n" + "="*70)
        print("PRIMERAS 50 LÍNEAS DEL QMD:")
        print("="*70)
        lines = qmd_content.split('\n')[:50]
        for i, line in enumerate(lines, 1):
            print(f"{i:3d}: {line}")
            
except Exception as e:
    print(f"✗ ERROR al generar documento: {e}")
    import traceback
    traceback.print_exc()
