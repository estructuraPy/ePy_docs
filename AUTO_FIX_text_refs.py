"""
AUTO-CORRECTOR: Elimina referencias obsoletas a text.epyson
Ejecuta este script para corregir automáticamente los archivos.
"""

import json
from pathlib import Path

# 1. Corregir core.epyson
print("Corrigiendo core.epyson...")
core_path = Path("src/ePy_docs/config/core.epyson")
with open(core_path, 'r', encoding='utf-8') as f:
    core = json.load(f)

if 'text' in core.get('config_modules', {}):
    del core['config_modules']['text']
    
with open(core_path, 'w', encoding='utf-8') as f:
    json.dump(core, f, indent=2, ensure_ascii=False)
print("✅ core.epyson corregido")

# 2. Corregir corporate.epyson
print("\nCorrigiendo corporate.epyson...")
corporate_path = Path("src/ePy_docs/config/layouts/corporate.epyson")
with open(corporate_path, 'r', encoding='utf-8') as f:
    corporate = json.load(f)

if 'text_ref' in corporate:
    del corporate['text_ref']
    
with open(corporate_path, 'w', encoding='utf-8') as f:
    json.dump(corporate, f, indent=2, ensure_ascii=False)
print("✅ corporate.epyson corregido")

print("\n" + "="*60)
print("✅ CORRECCIÓN COMPLETADA")
print("="*60)
print("\nCambios aplicados:")
print("  • core.epyson: Eliminada referencia 'text' de config_modules")
print("  • corporate.epyson: Eliminada propiedad 'text_ref'")
print("\nAhora el sistema debería funcionar sin errores.")
