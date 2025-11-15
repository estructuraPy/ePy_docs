"""
Test para verificar carga automática de bibliografía y CSL
"""

from ePy_docs import DocumentWriter
from pathlib import Path

# Crear documento con layout technical (debe usar IEEE)
writer = DocumentWriter("paper", layout_style="technical")

writer.add_h1("Test de Carga Automática de Bibliografía")

writer.add_h2("Citas de Prueba")
writer.add_text("Primera cita: [@CSCR2010_14]")
writer.add_text("Segunda cita: [@ACI318_19]")
writer.add_text("Tercera cita: [@AISC360_22]")

writer.add_list([
    "Código Sísmico [@CSCR2010_14]",
    "ACI 318 [@ACI318_19]",
    "AISC 360 [@AISC360_22]"
], ordered=True)

# Generar SIN pasar bibliography_path ni csl_path
print("Generando documento...")
print("Layout: technical")
print("Citation style esperado: ieee")
print()

result = writer.generate(
    html=True,
    pdf=False,
    qmd=True,
    output_filename="test_auto_bib"
)

print("\n=== Resultado ===")
for fmt, path in result.items():
    if path:
        print(f"{fmt.upper()}: {path}")

# Verificar el contenido del .qmd
qmd_path = result.get('qmd')
if qmd_path:
    print(f"\n=== Revisando {qmd_path} ===")
    with open(qmd_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Buscar configuración de bibliografía en YAML
        if 'bibliography:' in content:
            print("✓ bibliography configurado en YAML")
            # Extraer la línea
            for line in content.split('\n'):
                if 'bibliography:' in line:
                    print(f"  {line}")
        else:
            print("✗ bibliography NO configurado en YAML")
            
        if 'csl:' in content:
            print("✓ csl configurado en YAML")
            # Extraer la línea
            for line in content.split('\n'):
                if 'csl:' in line:
                    print(f"  {line}")
        else:
            print("✗ csl NO configurado en YAML")

# Verificar archivos copiados
output_dir = Path(qmd_path).parent
print(f"\n=== Archivos en {output_dir} ===")
bib_files = list(output_dir.glob('*.bib'))
csl_files = list(output_dir.glob('*.csl'))

if bib_files:
    print(f"✓ Archivos .bib encontrados: {[f.name for f in bib_files]}")
else:
    print("✗ NO se encontraron archivos .bib")

if csl_files:
    print(f"✓ Archivos .csl encontrados: {[f.name for f in csl_files]}")
else:
    print("✗ NO se encontraron archivos .csl")
