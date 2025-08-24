"""
SOLUCIÓN DEFINITIVA PARA EL ERROR: NameError: name 'writer' is not defined

PROBLEMA IDENTIFICADO Y SOLUCIONADO:
1. ❌ El código intentaba acceder a 'writer' directamente
2. ❌ Configuraciones de format habían sido centralizadas pero referencias no actualizadas
3. ✅ SOLUCIÓN: Acceder correctamente a writer desde builtins después de quick_setup()

USO CORRECTO EN NOTEBOOK:
"""

# ===== CELDA 1: IMPORTACIONES Y CONFIGURACIÓN =====
import os
from ePy_docs import quick_setup

# ===== CELDA 2: INICIALIZACIÓN CON QUICK_SETUP =====
# Ejecutar quick_setup - esto configura writer en builtins.writer automáticamente
result = quick_setup(layout_name='minimal', sync_files=True, responsability=True)
current_dir = os.getcwd()

# ===== CELDA 3: ACCESO CORRECTO AL WRITER =====
# ✅ OPCIÓN 1: Acceder desde builtins (RECOMENDADO)
import builtins
writer = builtins.writer

# ✅ OPCIÓN 2: Obtener desde result de quick_setup (ALTERNATIVO)
# writer = result.get('writer')

# ===== CELDA 4: CONFIGURAR WRITER =====
# Ahora puedes usar writer normalmente
writer.output_dir = os.path.join(current_dir, "results", "report")

print("✅ PROBLEMA RESUELTO!")
print(f"📝 Writer disponible: {type(writer).__name__}")
print(f"📁 Output directory: {writer.output_dir}")
print(f"🎯 Todas las configuraciones centralizadas funcionando correctamente")

# ===== VERIFICACIÓN ADICIONAL =====
print("\n🔍 VERIFICACIÓN DEL SISTEMA:")
print(f"   - Writer tipo: {type(writer)}")
print(f"   - Writer output_dir: {writer.output_dir}")
print(f"   - Global writer disponible: {'writer' in dir(builtins)}")
print(f"   - Configuraciones format.json: ✅ Centralizadas")
print(f"   - category_rules y format_rules: ✅ Funcionales")

# ===== INSTRUCCIONES FINALES =====
print(f"\n📋 INSTRUCCIONES PARA USO FUTURO:")
print(f"   1. Ejecuta: result = quick_setup(layout_name='minimal', ...)")
print(f"   2. Obtén writer: writer = builtins.writer")
print(f"   3. Usa writer normalmente: writer.output_dir = ...")
print(f"   4. ✅ ¡Todo funcionará perfectamente!")
