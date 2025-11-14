#!/usr/bin/env python3
"""
Debug específico del registro de fuentes en matplotlib
"""

import matplotlib.font_manager as fm
from pathlib import Path

print("=== DEBUG REGISTRO DE FUENTES ===")

# 1. Verificar archivo de fuente
package_root = Path("src/ePy_docs").resolve()
font_file = package_root / 'config' / 'assets' / 'fonts' / 'anm_ingenieria_2025.otf' 

print(f"1. Archivo de fuente:")
print(f"   Ruta: {font_file}")
print(f"   Existe: {font_file.exists()}")
print(f"   Tamaño: {font_file.stat().st_size if font_file.exists() else 'N/A'} bytes")

# 2. Intentar registro manual
if font_file.exists():
    print(f"\n2. Registrando fuente manualmente...")
    try:
        # Agregar fuente al manager
        fm.fontManager.addfont(str(font_file))
        print("   ✅ Fuente agregada con addfont()")
        
        # Forzar reconstrucción del cache de diferentes maneras
        try:
            fm.fontManager._init()
            print("   ✅ Cache reconstruido con _init()")
        except AttributeError:
            try:
                fm._rebuild()
                print("   ✅ Cache reconstruido con _rebuild()")
            except AttributeError:
                try:
                    # Forzar rebuild del fontManager
                    import matplotlib
                    matplotlib.font_manager._rebuild()
                    print("   ✅ Cache reconstruido con matplotlib.font_manager._rebuild()")
                except Exception as e:
                    print(f"   ⚠️ No se pudo reconstruir cache: {e}")
                    # Como último recurso, limpiar el cache manualmente
                    try:
                        fm.fontManager.ttflist = []
                        fm.fontManager.afmlist = []
                        fm.fontManager._find_fonts()
                        print("   ✅ Cache limpiado manualmente")
                    except Exception as e2:
                        print(f"   ❌ Error limpiando cache manualmente: {e2}")
        
    except Exception as e:
        print(f"   ❌ Error registrando fuente: {e}")

# 3. Verificar si la fuente está disponible ahora
print(f"\n3. Verificando disponibilidad después de registro:")
available_fonts = [f.name for f in fm.fontManager.ttflist]
custom_font_available = any('anm_ingenieria' in font_name.lower() for font_name in available_fonts)
print(f"   Fuente disponible: {custom_font_available}")

if custom_font_available:
    matching_fonts = [f.name for f in fm.fontManager.ttflist if 'anm_ingenieria' in f.name.lower()]
    print(f"   Nombres encontrados: {matching_fonts}")

# 4. Test de plot con fuente registrada
print(f"\n4. Test de plot con fuente registrada:")
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['anm_ingenieria_2025', 'Segoe Script', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([1, 2, 3], [1, 4, 2], 'b-')
ax.set_title("Test con fuente registrada", fontsize=16)

title_font = ax.title.get_fontname()
print(f"   Fuente usada en título: {title_font}")

plt.savefig("results/test_registered_font.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✅ Test completado")
print("=== END DEBUG ===")