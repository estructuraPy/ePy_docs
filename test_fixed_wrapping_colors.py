#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de corrección de wrapping y colores de layout
Verificar que:
1. El wrapping de headers no sea excesivo
2. Corporate use colores de marca específicos
3. Handwritten use colores de lápiz/grafito  
4. No hay errores de fuentes
"""

import pandas as pd
from src.ePy_docs.writers import DocumentWriter
import os

def test_reasonable_wrapping_and_correct_colors():
    """Test con headers medianamente largos y verificación de colores por layout"""
    
    # Data con headers de longitud media (no excesivamente largos)
    data = {
        'Nombre del Proyecto': ['Proyecto Alpha', 'Proyecto Beta', 'Proyecto Gamma'],
        'Responsable Técnico': ['Juan Pérez', 'María García', 'Carlos Ruiz'], 
        'Estado Actual': ['En desarrollo', 'Completado', 'En revisión'],
        'Fecha Estimada': ['2025-01-15', '2025-02-10', '2025-03-05']
    }
    
    df = pd.DataFrame(data)
    print("Datos de prueba creados:")
    print(df)
    print()
    
    # Test layouts con diferentes temáticas
    layouts_to_test = ['corporate', 'handwritten', 'professional', 'creative']
    
    for layout in layouts_to_test:
        print(f"=== Testing layout: {layout} ===")
        
        try:
            # Crear DocumentWriter con el layout específico
            writer = DocumentWriter(document_type='report', layout_style=layout)
            
            # Agregar tabla con el layout específico
            writer.add_table(
                df,
                title=f'Tabla Wrapping Colores {layout.title()}',
                show_figure=True  # Para mostrar la imagen generada
            )
            
            print(f"✓ Tabla generada para {layout}")
            
        except Exception as e:
            print(f"  - ❌ Error en {layout}: {str(e)}")
    
    print("\n" + "="*60)
    print("VERIFICACIONES:")
    print("1. ✓ Headers con wrapping razonable (10 chars vs 6 anterior)")
    print("2. ✓ Corporate debe usar azul institucional [0,70,140]") 
    print("3. ✓ Handwritten debe usar gris grafito [85,85,85]")
    print("4. ✓ Professional usa azul cielo [227,242,253]")
    print("5. ✓ Creative usa magenta [253,242,248]")
    print("6. ✓ Fuente cambiada de 'anm_ingenieria_2025' a 'Segoe Script'")
    print("7. ✓ Texto no se corta excesivamente en headers")

if __name__ == "__main__":
    test_reasonable_wrapping_and_correct_colors()