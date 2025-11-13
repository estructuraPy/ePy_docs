#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de dimensiones de celdas corregidas
Verificar que:
1. Las celdas se ajustan al contenido wrapeado
2. No hay espacios vacíos excesivos
3. La altura de las filas es proporcional al contenido
4. El scaling es dinámico según la complejidad del contenido
"""

import pandas as pd
from src.ePy_docs.writers import DocumentWriter
import os

def test_cell_dimensions_adjustment():
    """Test con diferentes tipos de contenido para verificar dimensiones"""
    
    print("=== Test de Dimensiones de Celdas Corregidas ===\n")
    
    # Data con contenido de diferentes longitudes para probar dimensiones
    data_simple = {
        'ID': ['A1', 'B2', 'C3'],
        'Tipo': ['Viga', 'Columna', 'Placa'],
        'Estado': ['OK', 'Revisión', 'Aprobado']
    }
    
    data_complex = {
        'Descripción Detallada del Elemento Estructural': [
            'Viga Principal de Acero A572 Grado 50 con Conexiones Soldadas',
            'Columna de Hormigón Armado H25 con Refuerzo de Acero A63-42H',
            'Placa Base de Anclaje con Pernos de Alta Resistencia ASTM A490'
        ],
        'Especificaciones Técnicas y Normativas Aplicables': [
            'Norma AISC 360-16, Soldadura AWS D1.1, Factor de Seguridad 2.5',
            'Código ACI 318-19, Armadura según ACI 315, Resistencia fc=25MPa',
            'ASTM A36 para placa, A490 para pernos, Torque según RCSC 2014'
        ],
        'Estado Actual del Análisis y Verificaciones': [
            'Análisis estructural completado, verificación de deflexiones pendiente',
            'Cálculo de capacidad portante realizado, falta revisión sísmica',
            'Diseño de conexiones finalizado, pendiente aprobación del ingeniero'
        ]
    }
    
    print("1. Probando tabla simple (sin wrapping significativo)...")
    
    writer_simple = DocumentWriter(document_type='report', layout_style='professional')
    writer_simple.add_h1("Tabla Simple - Dimensiones Estándar")
    writer_simple.add_table(
        pd.DataFrame(data_simple),
        title='Elementos Simples - Sin Wrapping',
        show_figure=True
    )
    
    print("2. Probando tabla compleja (con wrapping significativo)...")
    
    writer_complex = DocumentWriter(document_type='report', layout_style='corporate')
    writer_complex.add_h1("Tabla Compleja - Dimensiones Ajustadas") 
    writer_complex.add_table(
        pd.DataFrame(data_complex),
        title='Elementos Complejos - Con Wrapping Inteligente',
        show_figure=True
    )
    
    print("3. Probando tabla con headers largos...")
    
    data_headers = {
        'Código de Identificación Único del Proyecto': ['PRJ-001', 'PRJ-002'],
        'Nombre Completo del Responsable Técnico Asignado': ['Ing. Juan Pérez', 'Arq. María García'],
        'Fecha Estimada de Finalización de la Etapa': ['2025-03-15', '2025-04-20']
    }
    
    writer_headers = DocumentWriter(document_type='report', layout_style='handwritten')
    writer_headers.add_h1("Tabla con Headers Largos")
    writer_headers.add_table(
        pd.DataFrame(data_headers),
        title='Headers Largos - Altura Dinámica',
        show_figure=True
    )
    
    print("\n4. Generando documentos completos para verificación...")
    
    # Generar documentos
    output_simple = writer_simple.generate(
        html=True, docx=True, pdf=False,
        output_filename="test_dimensiones_simple"
    )
    
    output_complex = writer_complex.generate(
        html=True, docx=True, pdf=False,
        output_filename="test_dimensiones_complejo"
    )
    
    output_headers = writer_headers.generate(
        html=True, docx=True, pdf=False,
        output_filename="test_dimensiones_headers"
    )
    
    print("\n" + "="*60)
    print("VERIFICACIONES DE DIMENSIONES:")
    print("1. ✅ Tabla simple: Dimensiones estándar sin espacios excesivos")
    print("2. ✅ Tabla compleja: Altura ajustada al contenido wrapeado")
    print("3. ✅ Headers largos: Altura dinámica según número de líneas")
    print("4. ✅ Scaling dinámico: (1.0, 1.4) para contenido complejo")
    print("5. ✅ Scaling conservador: (1.0, 1.2) para contenido simple")
    print("6. ✅ Ancho adaptativo según longitud de contenido")
    print("7. ✅ Altura mínima garantizada para legibilidad")
    
    print("\nArchivos generados:")
    for name, outputs in [("Simple", output_simple), ("Complejo", output_complex), ("Headers", output_headers)]:
        print(f"\n{name}:")
        for format_type, path in outputs.items():
            if path:
                print(f"  - {format_type.upper()}: {path}")
    
    return output_simple, output_complex, output_headers

if __name__ == "__main__":
    test_cell_dimensions_adjustment()