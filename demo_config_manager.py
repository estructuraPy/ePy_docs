"""
Ejemplo de uso del ConfigManager mejorado
==========================================

Este script demuestra cómo el ConfigManager ahora:
1. Lee rutas desde setup.epyson (no hardcodeadas)
2. Carga todas las configuraciones automáticamente
3. Proporciona acceso fácil a todas las configs
"""

from src.ePy_docs.config.config_manager import ConfigManager
from pathlib import Path
import json

# Inicializar ConfigManager
print("🔧 Inicializando ConfigManager...")
cm = ConfigManager()

# Mostrar información del sistema
print(f"\n📦 Package path: {cm.package_path}")
print(f"⚙️  Config path: {cm.config_path}")

# Listar todas las configuraciones cargadas
print(f"\n✅ Configuraciones cargadas: {len(cm._configs)}")
print("\n📋 Archivos de configuración disponibles:")
for i, key in enumerate(sorted(cm._configs.keys()), 1):
    print(f"   {i:2d}. {key}")

# Mostrar la sección config_files del setup
print("\n🗺️  Rutas de archivos de configuración (desde setup.epyson):")
setup = cm.get_config('setup')
config_files = setup.get('config_files', {})
for name, path in sorted(config_files.items()):
    exists = "✅" if (cm.package_path / path).exists() else "❌"
    print(f"   {exists} {name:15s} → {path}")

# Mostrar directorios configurados
print("\n📁 Directorios configurados:")
directories = setup.get('directories', {})
for name, path in list(directories.items())[:8]:
    print(f"   • {name:20s} → {path}")

# Ejemplo: Acceder a configuración específica
print("\n🎨 Ejemplo: Acceso a configuración de colores")
colors_config = cm.get_config('colors')
if colors_config:
    palettes = colors_config.get('palettes', {})
    print(f"   Paletas disponibles: {len(palettes)}")
    if 'brand' in palettes:
        brand = palettes['brand']
        print(f"   Color primario (brand): RGB{brand.get('primary', 'N/A')}")

print("\n🏗️  Ejemplo: Acceso a configuración de tablas")
tables_config = cm.get_config('tables')
if tables_config:
    layout_styles = tables_config.get('layout_styles', {})
    print(f"   Estilos de layout: {len(layout_styles)}")
    print(f"   Disponibles: {', '.join(layout_styles.keys())}")

print("\n" + "="*60)
print("✅ ConfigManager funcionando correctamente")
print("="*60)
