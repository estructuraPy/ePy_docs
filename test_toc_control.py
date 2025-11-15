#!/usr/bin/env python3
"""
Test para verificar que toc: true/false funciona correctamente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs import DocumentWriter

def test_toc_true():
    """Verificar que book tiene TOC (toc: true en book.epyson)"""
    doc = DocumentWriter(document_type="book", layout_style="classic")
    
    doc.add_h1("Capítulo 1")
    doc.add_text("Contenido del capítulo 1.")
    
    doc.add_h2("Sección 1.1")
    doc.add_text("Contenido de la sección.")
    
    generated_files = doc.generate()
    html_file = generated_files.get('html')
    
    if html_file and os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_toc = 'id="TOC"' in content
        print(f"Book (toc: true): {'✅ TOC PRESENTE' if has_toc else '❌ TOC AUSENTE (ERROR)'}")
        return has_toc
    return False

def test_toc_false():
    """Verificar que paper NO tiene TOC (toc: false en paper.epyson)"""
    doc = DocumentWriter(document_type="paper", layout_style="academic")
    
    doc.add_h1("Documento Paper")
    doc.add_text("Este documento NO debe tener tabla de contenidos.")
    
    doc.add_h2("Sección 1")
    doc.add_text("Contenido de la sección.")
    
    generated_files = doc.generate()
    html_file = generated_files.get('html')
    
    if html_file and os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_toc = 'id="TOC"' in content
        print(f"Paper (toc: false): {'❌ TOC PRESENTE (ERROR)' if has_toc else '✅ TOC AUSENTE'}")
        return not has_toc
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Control de TOC mediante configuración document_type")
    print("=" * 60)
    
    result1 = test_toc_true()
    print()
    result2 = test_toc_false()
    
    print()
    print("=" * 60)
    if result1 and result2:
        print("✅ TODOS LOS TESTS PASARON")
        print("✅ toc: true/false funciona correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("=" * 60)
