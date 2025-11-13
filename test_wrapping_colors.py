#!/usr/bin/env python3
"""
Test específico para verificar wrapping agresivo y colores correctos
"""
from ePy_docs.writers import DocumentWriter
import pandas as pd

def test_aggressive_fixes():
    print("=== TEST CORRECCIONES AGRESIVAS ===\n")
    
    # Crear datos con texto extremadamente largo para probar wrapping
    data = {
        'Columna_Con_Nombre_Extremadamente_Largo_Que_Debe_Hacer_Wrap': [
            'Texto_muy_largo_que_debería_hacer_wrapping_automático_en_múltiples_líneas', 
            'Otro_texto_largo_con_múltiples_palabras_separadas_por_guiones', 
            'TextoMuyLargoSinEspaciosQueDebeRomperse'
        ],
        'Otra_Columna_Igualmente_Larga_Para_Probar_Headers': [
            'Valor con espacios muy largos que también debe hacer wrap',
            'AnotherVeryLongValueWithoutSpacesThatShouldBreak',
            'Normal'
        ],
        'ID': [1, 2, 3]
    }
    
    df = pd.DataFrame(data)
    
    # Test específico para handwritten
    print("--- Test Handwritten (debe usar gris [99,100,102], NO azul) ---")
    writer = DocumentWriter(layout_style='handwritten')
    writer.add_h1("Test Handwritten Colors")
    writer.add_text("Esta tabla DEBE usar gris oscuro [99,100,102], NO azul corporate")
    writer.add_table(df, title="Verificación_Handwritten_Colors_Wrapping")
    
    result = writer.generate(output_filename="test_handwritten_fix", html=True, qmd=False, pdf=False)
    print(f"Generado: {result.get('html', 'No HTML')}")
    
    # Test corporate para comparar
    print("\n--- Test Corporate (debe usar azul [219,234,254]) ---")
    writer2 = DocumentWriter(layout_style='corporate')
    writer2.add_h1("Test Corporate Colors")
    writer2.add_text("Esta tabla debe usar azul corporate [219,234,254]")
    writer2.add_table(df, title="Verificación_Corporate_Colors_Wrapping")
    
    result2 = writer2.generate(output_filename="test_corporate_fix", html=True, qmd=False, pdf=False)
    print(f"Generado: {result2.get('html', 'No HTML')}")
    
    print("\n=== VERIFICACIÓN MANUAL REQUERIDA ===")
    print("Abrir las imágenes generadas y verificar:")
    print("1. WRAPPING: Headers largos deben estar en múltiples líneas")
    print("2. COLORES:")
    print("   - Handwritten: Headers GRIS OSCURO [99,100,102]")
    print("   - Corporate: Headers AZUL CLARO [219,234,254]")
    print("3. NO DESBORDAMIENTO: Todo el texto debe caber en las celdas")
    print("\nSi handwritten muestra azul en lugar de gris, hay problema de mapeo de colores.")

if __name__ == "__main__":
    test_aggressive_fixes()