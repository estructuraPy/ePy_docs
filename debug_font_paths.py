"""
Test de debug para ver la ruta de fuentes
"""
from pathlib import Path
from ePy_docs.core._config import get_loader

print("Debug de rutas de fuentes:")
print("-" * 50)

# Ruta actual del archivo de configuración
config_file = Path(__file__)
print(f"Archivo de test: {config_file}")

# Ruta del módulo _config.py
from ePy_docs.core import _config
config_module_path = Path(_config.__file__)
print(f"Módulo _config.py: {config_module_path}")

# Ruta esperada para fuentes
expected_fonts_dir = config_module_path.parent.parent / 'config' / 'assets' / 'fonts'
print(f"Directorio esperado de fuentes: {expected_fonts_dir}")
print(f"¿Existe el directorio?: {expected_fonts_dir.exists()}")

# Test del loader
loader = get_loader()
try:
    font_path = loader.get_font_path("helvetica_lt_std_compressed.OTF")
    print(f"Fuente encontrada en: {font_path}")
    print(f"Directorio padre: {font_path.parent}")
except FileNotFoundError as e:
    print(f"Error: {e}")

# Listar archivos en el directorio de fuentes
if expected_fonts_dir.exists():
    print(f"\nArchivos en {expected_fonts_dir}:")
    for file in expected_fonts_dir.iterdir():
        print(f"  - {file.name}")
else:
    print(f"\nEl directorio {expected_fonts_dir} no existe")