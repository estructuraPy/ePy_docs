#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comparación visual de las mejoras en dimensiones de tablas
Crear tabla antes/después para mostrar las correcciones
"""

import pandas as pd
from src.ePy_docs.writers import DocumentWriter

def create_comparison_report():
    """Crear reporte de comparación antes/después"""
    
    print("=== Reporte de Comparación de Mejoras ===\n")
    
    # Datos de ejemplo con headers problemáticos
    data_test = {
        'Identificación del Elemento Estructural Completo': [
            'VIG-001', 'COL-002', 'PLA-003'
        ],
        'Descripción Técnica Detallada y Especificaciones': [
            'Viga metálica IPE300 de acero A572',
            'Columna de hormigón armado H25 200x400',
            'Placa base de acero A36 400x400x25'
        ],
        'Estado Actual del Proceso de Verificación': [
            'Cálculo completado, revisión pendiente',
            'En proceso de análisis sísmico',
            'Diseño finalizado, aprobación pendiente'
        ]
    }
    
    df = pd.DataFrame(data_test)
    
    writer = DocumentWriter(document_type='report', layout_style='professional')
    
    writer.add_h1("Mejoras en Dimensiones de Tablas")
    
    writer.add_h2("Problema Anterior")
    writer.add_text("**Antes:** Las tablas con contenido wrapeado tenían:")
    writer.add_dot_list([
        "Headers cortados excesivamente (6 caracteres)",
        "Espacios vacíos en celdas por scaling incorrecto",
        "Altura fija que no se adaptaba al contenido",
        "Dimensiones estáticas sin considerar complejidad"
    ])
    
    writer.add_h2("Solución Implementada")
    writer.add_text("**Ahora:** El sistema ajusta dinámicamente:")
    writer.add_dot_list([
        "Headers con wrapping a 10 caracteres (más legible)",
        "Altura de celdas calculada según número de líneas",
        "Scaling dinámico: (1.0, 1.2) simple vs (1.0, 1.4) complejo",
        "Ancho adaptativo según longitud del contenido",
        "Altura base + incremento por línea adicional"
    ])
    
    writer.add_h2("Tabla de Demostración")
    writer.add_text("Esta tabla utiliza las mejoras implementadas:")
    
    writer.add_table(
        df,
        title='Tabla con Dimensiones Dinámicas Mejoradas',
        show_figure=True
    )
    
    writer.add_h2("Mejoras Técnicas Específicas")
    
    writer.add_h3("1. Cálculo Dinámico de Altura")
    writer.add_text("```python\n# Headers: altura_base + (líneas-1) * 0.04\n# Celdas: altura_base + (líneas-1) * 0.03\nbase_height = 0.08 if is_header else 0.06\nheight = base_height + (line_count - 1) * increment\n```")
    
    writer.add_h3("2. Scaling Inteligente")
    writer.add_text("```python\n# Detección de contenido complejo\nhas_wrapped = any('\\n' in str(cell) for cell in df.values.flatten())\nif has_wrapped:\n    table.scale(1.0, 1.4)  # Para contenido wrapeado\nelse:\n    table.scale(1.0, 1.2)  # Para contenido simple\n```")
    
    writer.add_h3("3. Ancho Adaptativo")
    writer.add_text("El ancho se ajusta según la longitud del contenido:")
    writer.add_dot_list([
        "Contenido >20 chars: multiplier 1.2",
        "Contenido >15 chars: multiplier 1.1", 
        "Contenido estándar: multiplier 1.0"
    ])
    
    # Generar documento
    output = writer.generate(
        html=True, docx=True, pdf=False,
        output_filename="reporte_mejoras_dimensiones"
    )
    
    print("✅ Reporte de comparación generado exitosamente")
    print("\nArchivos generados:")
    for format_type, path in output.items():
        if path:
            print(f"  - {format_type.upper()}: {path}")
    
    return output

if __name__ == "__main__":
    create_comparison_report()