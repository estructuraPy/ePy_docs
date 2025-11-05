#!/usr/bin/env python3
"""
Script para probar el auto-ajuste de ancho de plots.
"""

from ePy_docs.writers import DocumentWriter
import matplotlib.pyplot as plt
import numpy as np

def test_auto_width():
    """Prueba el auto-ajuste de ancho de plots."""
    
    print("=== VERIFICACIÓN DE AUTO-AJUSTE DE PLOTS ===")
    
    # Crear writer con layout creative (2 columnas para paper)
    writer = DocumentWriter('paper', 'creative', language='es')
    print(f"Layout: {writer.layout_style}")
    print(f"Document type: {writer.document_type}")
    print(f"Language: {writer.language}")
    
    # Crear plot simple
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)
    ax.set_title('Test Auto-Width')
    
    # Agregar plot SIN especificar columns (debe auto-ajustarse)
    writer.add_plot(fig, title='Plot Auto-Width', caption='Debe ajustarse automáticamente')
    print("✅ Plot agregado SIN especificar columns")
    
    # Generar QMD
    result = writer.generate(html=False, pdf=False, qmd=True, output_filename='test_auto_width')
    print(f"✅ QMD generado: {result['qmd']}")
    
    # Verificar contenido
    with open(result['qmd'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n=== RESULTADOS ===")
    
    if 'width=6.5in' in content:
        print('✅ SUCCESS: Plot se ajustó automáticamente a ancho completo (6.5in)')
    elif 'width=' in content:
        print('⚠️  PARTIAL: Plot tiene ancho especificado, pero no el esperado')
    else:
        print('❌ FAIL: Plot no tiene ancho especificado')
        
    # Mostrar líneas relevantes
    print("\n=== LÍNEAS DE MARKDOWN CON ANCHO ===")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'width=' in line and '#fig-' in line:
            print(f"Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    test_auto_width()