#!/usr/bin/env python3
"""
Ejemplo de uso de la funcionalidad de división de tablas en ePy_docs

Este script demuestra cómo usar la funcionalidad de división automática de tablas
que ya existe en el sistema ePy_docs.
"""

import pandas as pd
from ePy_docs.core.content import ContentProcessor

def demo_table_division():
    """Demostrar la funcionalidad de división de tablas."""
    
    print("=== INFORMACIÓN DE CONFIGURACIÓN DE DIVISIÓN DE TABLAS ===")
    
    # Obtener información de configuración
    info = ContentProcessor.get_table_division_info()
    
    print(f"Límite por defecto: {info['default_max_rows_per_table']} filas por tabla")
    print("\nFuentes de configuración (en orden de prioridad):")
    for source in info['configuration_sources']:
        print(f"  {source}")
    
    print("\n=== TIPOS DE PARÁMETROS SOPORTADOS ===")
    
    for param_type, details in info['parameter_types'].items():
        print(f"\n{param_type.upper()}:")
        print(f"  Descripción: {details['description']}")
        print(f"  Ejemplo: {details['example']}")
        print(f"  Comportamiento: {details['behavior']}")
    
    print("\n=== ESQUEMA DE NUMERACIÓN ===")
    print(f"Tabla única: {info['numbering_scheme']['single_table']}")
    print(f"Múltiples tablas: {info['numbering_scheme']['multiple_tables']}")
    
    print("\n=== COMPORTAMIENTO DE TÍTULOS ===")
    print(f"Título en imagen: {info['title_behavior']['image_title']}")
    print(f"Caption de Quarto: {info['title_behavior']['quarto_caption']}")

def example_usage():
    """Ejemplos de uso con diferentes configuraciones."""
    
    print("\n\n=== EJEMPLOS DE USO ===")
    
    # Crear un DataFrame de ejemplo
    data = {
        'Nodo': range(1, 101),  # 100 filas
        'X (m)': [i * 0.1 for i in range(100)],
        'Y (m)': [i * 0.05 for i in range(100)],
        'Z (m)': [0.0] * 100,
        'Soporte': ['Libre'] * 95 + ['Empotrado'] * 5
    }
    df = pd.DataFrame(data)
    
    print(f"DataFrame de ejemplo creado con {len(df)} filas")
    
    # Simular división con diferentes configuraciones
    from ePy_docs.files.data import split_large_table
    
    print("\n1. DIVISIÓN CON TAMAÑO FIJO (25 filas por tabla):")
    chunks_fixed = split_large_table(df, 25)
    print(f"   Resultado: {len(chunks_fixed)} tablas")
    for i, chunk in enumerate(chunks_fixed):
        print(f"   Tabla {i+1}: {len(chunk)} filas")
    
    print("\n2. DIVISIÓN CON TAMAÑOS PERSONALIZADOS [30, 20, 15]:")
    chunks_custom = split_large_table(df, [30, 20, 15])
    print(f"   Resultado: {len(chunks_custom)} tablas")
    for i, chunk in enumerate(chunks_custom):
        print(f"   Tabla {i+1}: {len(chunk)} filas")
    
    print("\n3. DIVISIÓN CON TAMAÑOS PERSONALIZADOS [40, 35] (con resto):")
    chunks_remainder = split_large_table(df, [40, 35])
    print(f"   Resultado: {len(chunks_remainder)} tablas")
    for i, chunk in enumerate(chunks_remainder):
        print(f"   Tabla {i+1}: {len(chunk)} filas")

def configuration_examples():
    """Ejemplos de configuración en archivos JSON."""
    
    print("\n\n=== EJEMPLOS DE CONFIGURACIÓN ===")
    
    print("\n1. CONFIGURACIÓN EN styles.json:")
    print("""
{
  "pdf_settings": {
    "table_style": {
      "max_rows_per_table": 30,
      "multi_table_title_format": "{title} (Parte {part}/{total})"
    }
  }
}
    """)
    
    print("\n2. USO CON PARÁMETROS EN CÓDIGO:")
    print("""
# Usar configuración por defecto del JSON
create_split_table_images(df, output_dir, table_number=1)

# Sobrescribir con tamaño fijo
create_split_table_images(df, output_dir, table_number=1, max_rows_per_table=25)

# Usar tamaños personalizados por tabla
create_split_table_images(df, output_dir, table_number=1, max_rows_per_table=[20, 15, 30])
    """)
    
    print("\n3. RESULTADO DE ARCHIVOS GENERADOS:")
    print("""
Tabla única (≤ límite):
  - tabla_001.png

Múltiples tablas (> límite):
  - tabla_001.1.png
  - tabla_001.2.png  
  - tabla_001.3.png
    """)

if __name__ == "__main__":
    print("DEMOSTRACIÓN: Funcionalidad de División de Tablas en ePy_docs")
    print("=" * 60)
    
    try:
        demo_table_division()
        example_usage()
        configuration_examples()
        
        print("\n\n=== RESUMEN ===")
        print("✅ La funcionalidad de división de tablas YA ESTÁ IMPLEMENTADA")
        print("✅ Soporta límites por defecto desde archivos JSON")
        print("✅ Permite sobrescribir con parámetros del usuario")
        print("✅ Acepta tanto tamaños fijos como listas personalizadas")
        print("✅ Maneja automáticamente los restos y numeración")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        print("Asegúrate de que el proyecto ePy_docs esté correctamente configurado.")
