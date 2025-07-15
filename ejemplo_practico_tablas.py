#!/usr/bin/env python3
"""
Ejemplo práctico: Uso de división de tablas en ePy_docs

Este ejemplo muestra cómo usar la funcionalidad de división de tablas
en un escenario real de generación de reportes.
"""

import pandas as pd
import os
from pathlib import Path

def create_sample_data():
    """Crear datos de ejemplo para un reporte estructural."""
    
    # Datos de nodos
    nodes_data = {
        'Nodo': range(1, 151),  # 150 nodos
        'X (m)': [i * 0.5 for i in range(150)],
        'Y (m)': [(i % 10) * 2.0 for i in range(150)],
        'Z (m)': [((i // 10) % 5) * 3.0 for i in range(150)],
        'Soporte': ['Libre'] * 140 + ['Empotrado'] * 8 + ['Articulado'] * 2,
        'Masa (kg)': [1500 + (i % 500) for i in range(150)]
    }
    
    # Datos de elementos
    elements_data = {
        'Elemento': range(1, 201),  # 200 elementos
        'Nodo_i': [i % 150 + 1 for i in range(200)],
        'Nodo_j': [(i + 1) % 150 + 1 for i in range(200)],
        'Material': ['Acero'] * 150 + ['Concreto'] * 50,
        'Sección': [f'IPE{200 + (i % 8) * 50}' if i < 150 else f'C{30 + (i % 5) * 10}x{40 + (i % 3) * 10}' for i in range(200)],
        'Longitud (m)': [2.0 + (i % 10) * 0.5 for i in range(200)]
    }
    
    # Datos de resultados
    results_data = {
        'Elemento': range(1, 101),  # 100 elementos con resultados
        'Caso': ['D+L'] * 50 + ['D+L+W'] * 50,
        'Axial (kN)': [100 + (i % 200) * 10 for i in range(100)],
        'Cortante (kN)': [50 + (i % 100) * 5 for i in range(100)],
        'Momento (kN⋅m)': [200 + (i % 300) * 15 for i in range(100)],
        'Ratio': [0.3 + (i % 50) * 0.01 for i in range(100)],
        'Status': ['OK'] * 85 + ['WARNING'] * 12 + ['CRITICAL'] * 3
    }
    
    return pd.DataFrame(nodes_data), pd.DataFrame(elements_data), pd.DataFrame(results_data)

def demonstrate_table_division_scenarios():
    """Demostrar diferentes escenarios de división de tablas."""
    
    nodes_df, elements_df, results_df = create_sample_data()
    
    print("=== ESCENARIOS DE DIVISIÓN DE TABLAS ===\n")
    
    # Escenario 1: Usar configuración por defecto
    print("1. CONFIGURACIÓN POR DEFECTO (25 filas por tabla)")
    print(f"   Tabla de Nodos ({len(nodes_df)} filas):")
    from ePy_docs.files.data import split_large_table
    
    # Simular división con configuración por defecto
    chunks_default = split_large_table(nodes_df, 25)
    print(f"   → Se crearían {len(chunks_default)} tablas:")
    for i, chunk in enumerate(chunks_default):
        print(f"     tabla_001.{i+1}.png: {len(chunk)} filas")
    
    print(f"\n   Tabla de Elementos ({len(elements_df)} filas):")
    chunks_elements = split_large_table(elements_df, 25)
    print(f"   → Se crearían {len(chunks_elements)} tablas:")
    for i, chunk in enumerate(chunks_elements):
        print(f"     tabla_002.{i+1}.png: {len(chunk)} filas")
    
    # Escenario 2: División personalizada por tipo de contenido
    print("\n\n2. DIVISIÓN PERSONALIZADA POR TIPO DE CONTENIDO")
    
    # Para nodos: mostrar primeros 30, luego grupos de 20
    print(f"   Tabla de Nodos con división [30, 20, 20, ...]:")
    custom_sizes_nodes = [30] + [20] * ((len(nodes_df) - 30) // 20 + 1)
    chunks_custom_nodes = split_large_table(nodes_df, custom_sizes_nodes[:6])  # Limitar a 6 partes
    print(f"   → Se crearían {len(chunks_custom_nodes)} tablas:")
    for i, chunk in enumerate(chunks_custom_nodes):
        print(f"     tabla_nodos.{i+1}.png: {len(chunk)} filas")
    
    # Para resultados: grupos más pequeños para mejor legibilidad
    print(f"\n   Tabla de Resultados con división [15, 15, 15, ...]:")
    chunks_results = split_large_table(results_df, 15)
    print(f"   → Se crearían {len(chunks_results)} tablas:")
    for i, chunk in enumerate(chunks_results):
        print(f"     tabla_resultados.{i+1}.png: {len(chunk)} filas")
    
    # Escenario 3: División por criticidad (ejemplo avanzado)
    print("\n\n3. DIVISIÓN POR CRITERIOS ESPECÍFICOS")
    
    # Separar resultados críticos, warnings, y OK
    critical_df = results_df[results_df['Status'] == 'CRITICAL']
    warning_df = results_df[results_df['Status'] == 'WARNING']
    ok_df = results_df[results_df['Status'] == 'OK']
    
    print(f"   Elementos críticos ({len(critical_df)} filas): tabla única")
    print(f"   Elementos con advertencias ({len(warning_df)} filas): tabla única")
    print(f"   Elementos OK ({len(ok_df)} filas): dividir en grupos de 30")
    
    if len(ok_df) > 30:
        chunks_ok = split_large_table(ok_df, 30)
        print(f"   → Elementos OK se dividirían en {len(chunks_ok)} tablas:")
        for i, chunk in enumerate(chunks_ok):
            print(f"     tabla_ok.{i+1}.png: {len(chunk)} filas")

def show_configuration_examples():
    """Mostrar ejemplos de configuración en archivos."""
    
    print("\n\n=== CONFIGURACIÓN EN ARCHIVOS JSON ===\n")
    
    print("1. CONFIGURACIÓN BÁSICA EN styles.json:")
    print("""
{
  "pdf_settings": {
    "table_style": {
      "max_rows_per_table": 30,
      "header_color": "#f0f0f0", 
      "font_size": 10,
      "multi_table_title_format": "{title} (Parte {part}/{total})"
    }
  }
}
    """)
    
    print("\n2. CONFIGURACIÓN AVANZADA EN tables.json:")
    print("""
{
  "max_rows_per_table": 25,
  "single_table_title_format": "{title}",
  "multi_table_title_format": "{title} (Parte {part}/{total})",
  "multi_table_no_title_format": "Parte {part}/{total}"
}
    """)

def show_code_examples():
    """Mostrar ejemplos de uso en código."""
    
    print("\n\n=== EJEMPLOS DE USO EN CÓDIGO ===\n")
    
    print("1. USO BÁSICO CON CONFIGURACIÓN POR DEFECTO:")
    print("""
from ePy_docs.components.tables import create_split_table_images

# Crear tabla con configuración por defecto del JSON
img_paths = create_split_table_images(
    df=nodes_df,
    output_dir="./images",
    base_table_number=1,
    title="Coordenadas de Nodos"
)
    """)
    
    print("\n2. USO CON DIVISIÓN PERSONALIZADA:")
    print("""
# División con tamaño fijo personalizado
img_paths = create_split_table_images(
    df=elements_df,
    output_dir="./images", 
    base_table_number=2,
    title="Propiedades de Elementos",
    max_rows_per_table=35  # Sobrescribir configuración por defecto
)

# División con tamaños específicos por tabla
img_paths = create_split_table_images(
    df=results_df,
    output_dir="./images",
    base_table_number=3, 
    title="Resultados del Análisis",
    max_rows_per_table=[20, 15, 25, 30]  # Tamaños específicos
)
    """)
    
    print("\n3. USO EN MARKDOWN GENERATOR:")
    print("""
from ePy_docs.formats.markdown import MarkdownGenerator

generator = MarkdownGenerator()

# Método con división automática
markdown_lines = generator.add_dataframe_table(
    df=large_df,
    title="Tabla Grande",
    split_large_tables=True,  # Activar división
    max_rows_per_table=25     # Límite personalizado
)
    """)

if __name__ == "__main__":
    print("EJEMPLO PRÁCTICO: División de Tablas en ePy_docs")
    print("=" * 50)
    
    try:
        demonstrate_table_division_scenarios()
        show_configuration_examples()
        show_code_examples()
        
        print("\n\n=== VENTAJAS DE ESTA IMPLEMENTACIÓN ===")
        print("✅ Flexible: Soporta tanto límites fijos como personalizados")
        print("✅ Configurable: Valores por defecto en JSON, sobrescribibles en código")
        print("✅ Automático: Numeración y títulos manejados automáticamente")
        print("✅ Inteligente: Maneja restos y casos especiales")
        print("✅ Integrado: Funciona con todo el pipeline de ePy_docs")
        
        print("\n=== CASOS DE USO RECOMENDADOS ===")
        print("📋 Tablas de coordenadas de nodos: 25-30 filas por tabla")
        print("🔧 Propiedades de elementos: 20-25 filas por tabla")
        print("📊 Resultados de análisis: 15-20 filas por tabla (mejor legibilidad)")
        print("⚠️  Elementos críticos: Tabla separada, sin división")
        print("📈 Datos históricos: División personalizada por período")
        
    except Exception as e:
        print(f"\n❌ Error durante el ejemplo: {e}")
        print("Nota: Este es un ejemplo de demostración.")
