#!/usr/bin/env python3
"""
Verificar que las tablas SÍ usan correctamente handwritten
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ePy_docs.core._tables import create_table_image_and_markdown

def test_tabla_handwritten():
    """Crear una tabla con handwritten para comparar"""
    
    print("=== TEST TABLA HANDWRITTEN ===")
    
    # Datos de ejemplo
    data = {
        'Deformación': [0.0000, 0.0005, 0.0010, 0.0015, 0.0020],
        'Esfuerzo (ksi)': [0.0, 1.4, 2.5, 3.4, 4.1],
        'Estado': ['Elástico', 'Elástico', 'Plástico', 'Plástico', 'Plástico']
    }
    
    df = pd.DataFrame(data)
    
    # Crear tabla con handwritten
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    result = create_table_image_and_markdown(
        data=df,
        title="Datos Esfuerzo-Deformación",
        output_dir=str(output_dir),
        layout_style='handwritten',
        document_type='report',
        table_counter=1,
        filename='tabla_handwritten_test.png'
    )
    
    print(f"✅ Tabla generada")
    print(f"Archivo: {output_dir / 'tabla_handwritten_test.png'}")
    print(f"Resultado: {type(result)}")
    
    return output_dir / 'tabla_handwritten_test.png'

if __name__ == "__main__":
    tabla = test_tabla_handwritten()
    
    print("\n" + "="*60)
    print(f"TABLA GENERADA: {tabla}")
    print("Revisa si los NÚMEROS se ven diferentes en la tabla")
    print("Si en la tabla SÍ funciona, entonces el problema es")
    print("que en gráficos no estoy aplicando igual")