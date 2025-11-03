"""
Test para verificar qué glifos tiene realmente C2024_anm_font.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ft2font import FT2Font

# Buscar el archivo de la fuente C2024_anm_font
font_path = None
for font in fm.fontManager.ttflist:
    if font.name == 'C2024_anm_font':
        font_path = font.fname
        break

if not font_path:
    print("❌ No se encontró C2024_anm_font")
    exit(1)

print(f"Fuente encontrada en: {font_path}")

# Cargar la fuente y ver qué glifos tiene
ft_font = FT2Font(font_path)
char_map = ft_font.get_charmap()

print(f"\nTotal de glifos en la fuente: {len(char_map)}")

# Verificar caracteres específicos
test_chars = {
    'Letras mayúsculas': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'Letras minúsculas': 'abcdefghijklmnopqrstuvwxyz',
    'Números': '0123456789',
    'Puntuación común': '.,;:!?',
    'Símbolos': '+-*/=()[]{}',
    'Espacios': ' '
}

print("\n" + "="*70)
print("ANÁLISIS DE GLIFOS DISPONIBLES:")
print("="*70)

missing_by_category = {}

for category, chars in test_chars.items():
    print(f"\n{category}:")
    missing = []
    present = []
    
    for char in chars:
        code = ord(char)
        if code in char_map:
            present.append(char)
        else:
            missing.append(char)
    
    if present:
        print(f"  ✅ Presentes ({len(present)}): {' '.join(present)}")
    if missing:
        print(f"  ❌ Faltantes ({len(missing)}): {' '.join(missing)}")
        missing_by_category[category] = missing

# Crear visualización de qué caracteres faltan
print("\n" + "="*70)
print("RESUMEN:")
print("="*70)

if missing_by_category:
    print("\n⚠️ CARACTERES FALTANTES QUE NECESITAN FALLBACK:")
    for category, chars in missing_by_category.items():
        print(f"  {category}: {' '.join(chars)}")
else:
    print("\n✅ Todos los caracteres comunes están presentes")

# Crear imagen de prueba con SOLO los caracteres que sabemos que faltan
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Subplot 1: Caracteres presentes
ax1.text(0.1, 0.5, 'PRESENT CHARS: ABC xyz', fontsize=20, 
         fontfamily=['C2024_anm_font', 'DejaVu Sans'])
ax1.set_title('Characters that should use C2024_anm_font')
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.axis('off')

# Subplot 2: Caracteres faltantes (que deberían usar fallback)
missing_text = "MISSING CHARS: "
if '0' not in char_map:
    missing_text += "0123456789 "
if '.' not in char_map:
    missing_text += "... "
if '(' not in char_map:
    missing_text += "()"

ax2.text(0.1, 0.5, missing_text, fontsize=20,
         fontfamily=['C2024_anm_font', 'DejaVu Sans'])
ax2.set_title('Characters that should fallback to DejaVu Sans')
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
ax2.axis('off')

plt.tight_layout()
output = 'results/report/glyph_analysis.png'
plt.savefig(output, dpi=150, bbox_inches='tight')
print(f"\n✅ Análisis visual guardado en: {output}")
print("\nRevisa el archivo para ver:")
print("  - Arriba: Caracteres que SÍ tiene C2024_anm_font (handwriting)")
print("  - Abajo: Caracteres que NO tiene (deberían verse sans-serif)")
