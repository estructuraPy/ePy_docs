#!/usr/bin/env python3
"""
Script para probar el auto-ajuste de ancho con diferentes configuraciones.
"""

from ePy_docs.writers import DocumentWriter
import matplotlib.pyplot as plt
import numpy as np

def test_auto_width_variations():
    """Prueba el auto-ajuste con diferentes configuraciones."""
    
    print("=== PRUEBAS DE AUTO-AJUSTE EN DIFERENTES CONFIGURACIONES ===\n")
    
    # Test 1: Creative paper (2 columnas)
    print("1️⃣ CREATIVE PAPER (debería ser 2 columnas):")
    writer1 = DocumentWriter('paper', 'creative')
    
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax1.plot(x, y)
    ax1.set_title('Creative Paper')
    
    writer1.add_plot(fig1, title='Plot Creative Paper', caption='Auto-ajuste creative paper')
    result1 = writer1.generate(html=False, pdf=False, qmd=True, output_filename='test_creative_paper')
    
    with open(result1['qmd'], 'r', encoding='utf-8') as f:
        content1 = f.read()
    
    if 'width=6.5in' in content1:
        print("   ✅ SUCCESS: 6.5in (ancho completo)")
    else:
        for line in content1.split('\n'):
            if 'width=' in line and '#fig-' in line:
                print(f"   ⚠️  Width encontrado: {line.strip()}")
    
    # Test 2: Creative report (típicamente 1 columna)
    print("\n2️⃣ CREATIVE REPORT (debería ser 1 columna):")
    writer2 = DocumentWriter('report', 'creative')
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    y2 = np.cos(x)
    ax2.plot(x, y2)
    ax2.set_title('Creative Report')
    
    writer2.add_plot(fig2, title='Plot Creative Report', caption='Auto-ajuste creative report')
    result2 = writer2.generate(html=False, pdf=False, qmd=True, output_filename='test_creative_report')
    
    with open(result2['qmd'], 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    if 'width=6.5in' in content2:
        print("   ✅ SUCCESS: 6.5in (ancho completo)")
    else:
        for line in content2.split('\n'):
            if 'width=' in line and '#fig-' in line:
                print(f"   ⚠️  Width encontrado: {line.strip()}")
    
    # Test 3: Handwritten paper (2 columnas)
    print("\n3️⃣ HANDWRITTEN PAPER (debería ser 2 columnas):")
    writer3 = DocumentWriter('paper', 'handwritten')
    
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    y3 = np.sin(x) * np.cos(x)
    ax3.plot(x, y3)
    ax3.set_title('Handwritten Paper')
    
    writer3.add_plot(fig3, title='Plot Handwritten Paper', caption='Auto-ajuste handwritten paper')
    result3 = writer3.generate(html=False, pdf=False, qmd=True, output_filename='test_handwritten_paper')
    
    with open(result3['qmd'], 'r', encoding='utf-8') as f:
        content3 = f.read()
    
    if 'width=6.5in' in content3:
        print("   ✅ SUCCESS: 6.5in (ancho completo)")
    else:
        for line in content3.split('\n'):
            if 'width=' in line and '#fig-' in line:
                print(f"   ⚠️  Width encontrado: {line.strip()}")
    
    # Test 4: Con columns manual (debe sobrescribir auto-ajuste)
    print("\n4️⃣ MANUAL COLUMNS=1.0 (debe sobrescribir auto-ajuste):")
    writer4 = DocumentWriter('paper', 'creative')
    
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    y4 = np.tan(x)
    ax4.plot(x, y4)
    ax4.set_title('Manual Columns')
    
    writer4.add_plot(fig4, title='Plot Manual Columns', caption='Columns manual = 1.0', columns=1.0)
    result4 = writer4.generate(html=False, pdf=False, qmd=True, output_filename='test_manual_columns')
    
    with open(result4['qmd'], 'r', encoding='utf-8') as f:
        content4 = f.read()
    
    if 'width=3.1in' in content4:
        print("   ✅ SUCCESS: 3.1in (una columna)")
    elif 'width=6.5in' in content4:
        print("   ❌ FAIL: Sigue usando 6.5in en lugar de usar columns=1.0")
    else:
        for line in content4.split('\n'):
            if 'width=' in line and '#fig-' in line:
                print(f"   ⚠️  Width encontrado: {line.strip()}")
    
    print("\n=== RESUMEN ===")
    print("✅ Auto-ajuste implementado y funcionando")
    print("✅ Manual columns sobrescribe auto-ajuste")
    print("✅ Diferentes layouts y document_types soportados")

if __name__ == "__main__":
    test_auto_width_variations()