#!/usr/bin/env python3
"""
Verificación visual de diferenciación de callouts
"""

import os
import subprocess
import sys

def open_pdfs():
    """Abrir PDFs generados para verificación visual."""
    
    pdf_files = [
        r"C:\Users\ingah\estructuraPy\ePy_docs\results\report\test_callouts_final.pdf",
        r"C:\Users\ingah\estructuraPy\ePy_docs\results\report\test_callouts_final.html"
    ]
    
    print("🔍 Abriendo archivos para verificación visual...")
    print("\n📋 GUÍA DE VERIFICACIÓN:")
    print("=" * 60)
    print("✓ Display chunks (tipo='display'):")
    print("  - Fondo: CLARO/GRIS (gray!5 - muy sutil)")
    print("  - Borde izquierdo: GRIS (2pt)")
    print("  - Contenido: Código Python de ejemplo")
    print()
    print("✓ Executable chunks (tipo='executable'):")
    print("  - Fondo: NARANJA/CAFÉ (orange!10)")
    print("  - Borde izquierdo: NARANJA (2pt)")
    print("  - Contenido: Código Python ejecutable")
    print("=" * 60)
    print()
    
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            ext = os.path.splitext(pdf_path)[1]
            print(f"📄 Abriendo {ext}: {pdf_path}")
            try:
                os.startfile(pdf_path)
            except Exception as e:
                print(f"  ⚠️  No se pudo abrir automáticamente: {e}")
                print(f"  💡 Abre manualmente: {pdf_path}")
        else:
            print(f"❌ No encontrado: {pdf_path}")
    
    print("\n✅ VERIFICACIÓN:")
    print("1. Compara el PDF con el HTML")
    print("2. Los display chunks deben tener fondo MÁS CLARO")
    print("3. Los executable chunks deben tener fondo MÁS OSCURO/NARANJA")
    print("4. Ambos tipos deben tener borde izquierdo visible")

if __name__ == "__main__":
    open_pdfs()
