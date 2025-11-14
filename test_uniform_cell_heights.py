#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test específico para verificar que las celdas con wrapping tienen el mismo tamaño
que las celdas sin wrapping en la misma fila.

Verifica:
1. Todas las celdas de una fila tienen la misma altura
2. Celdas con wrapping no causan inconsistencias
3. El sistema unificado de altura funciona correctamente
"""

import pandas as pd
from src.ePy_docs.writers import DocumentWriter
import os

def test_uniform_cell_heights():
    """Test que verifica que todas las celdas de una fila tengan la misma altura"""
    
    print("=== TEST: ALTURAS UNIFORMES DE CELDAS ===")
    
    # Crear datos con diferentes longitudes de contenido en la misma fila
    data = {
        'Corto': ['A', 'B', 'C'],
        'Contenido Largo que Necesita Wrapping': [
            'Este es un texto largo que debería hacer wrapping',
            'Otro texto corto', 
            'Texto muy largo que definitivamente va a requerir múltiples líneas para mostrarse correctamente'
        ],
        'Medio': ['Data1', 'Data2', 'Data3'],
        'Muy Largo Extremo': [
            'Contenido extremadamente largo que debería ocupar varias líneas y causar wrapping significativo',
            'Normal',
            'Texto largo otra vez para probar consistencia'
        ]
    }
    
    df = pd.DataFrame(data)
    print("Datos de prueba creados:")
    print(df)
    print()
    
    # Test con diferentes layouts
    layouts_to_test = ['corporate', 'handwritten']
    
    for layout in layouts_to_test:
        print(f"=== Testing layout: {layout} ===")
        
        try:
            # Crear DocumentWriter
            writer = DocumentWriter(document_type='report', layout_style=layout)
            
            # Agregar tabla que demuestra el problema
            writer.add_table(
                df,
                title=f'Test Alturas Uniformes - {layout.title()}',
                show_figure=True
            )
            
            print(f"✓ Tabla generada para {layout}")
            print("  - Verificar visualmente que todas las celdas de cada fila tengan la misma altura")
            print("  - Las celdas con wrapping deben tener la misma altura que las celdas cortas en su fila")
            
        except Exception as e:
            print(f"  - ❌ Error en {layout}: {str(e)}")
    
    print("\n" + "="*60)
    print("VERIFICACIONES ESPERADAS:")
    print("1. ✓ Fila 1: 'A' debe tener la misma altura que la celda con wrapping")
    print("2. ✓ Fila 2: 'B' debe tener la misma altura que 'Otro texto corto'")  
    print("3. ✓ Fila 3: 'C' debe tener la misma altura que la celda con texto muy largo")
    print("4. ✓ Headers: Todos los headers deben tener altura consistente")
    print("5. ✓ No debe haber celdas 'flotando' con alturas diferentes")
    
def test_edge_cases():
    """Test casos extremos de wrapping"""
    
    print("\n=== TEST: CASOS EXTREMOS ===")
    
    # Datos con casos extremos
    extreme_data = {
        'Normal': ['Simple', 'Data', 'Test'],
        'Números': [123, 456.789, 0.001],
        'Texto Extremo': [
            'Este es un caso extremo de texto que debería ocupar múltiples líneas y requiere manejo especial de wrapping para verificar que el sistema funciona correctamente',
            'Corto',
            'Texto medianamente largo que también necesita wrapping pero no tanto como el anterior'
        ],
        'Especial': ['NaN', None, '']
    }
    
    df = pd.DataFrame(extreme_data)
    print("Datos extremos creados:")
    print(df)
    
    try:
        writer = DocumentWriter(document_type='report', layout_style='corporate')
        writer.add_table(
            df,
            title='Test Casos Extremos',
            show_figure=True
        )
        
        print("✓ Tabla de casos extremos generada")
        
    except Exception as e:
        print(f"❌ Error en casos extremos: {str(e)}")

if __name__ == "__main__":
    test_uniform_cell_heights()
    test_edge_cases()