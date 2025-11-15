#!/usr/bin/env python3
"""
Test para verificar que los documentos tipo 'paper' no tienen TOC
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs import DocumentWriter

def test_paper_no_toc():
    """Crear un documento paper y verificar que no tiene TOC"""
    
    # Crear el writer especificando explícitamente document_type="paper"
    doc = DocumentWriter(
        document_type="paper",  # Tipo específico para paper
        layout_style="academic"  # Estilo académico
    )
    
    # Agregar contenido
    doc.add_h1("Documento Paper Sin TOC")
    doc.add_text("Este es un documento de tipo paper que NO debe tener tabla de contenidos.")
    
    doc.add_h2("Introducción")
    doc.add_text("Contenido de la introducción.")
    
    doc.add_h2("Metodología")
    doc.add_text("Descripción de la metodología utilizada.")
    
    doc.add_h3("Subsección")
    doc.add_text("Contenido de una subsección.")
    
    doc.add_h2("Conclusiones")
    doc.add_text("Principales conclusiones del estudio.")
    
    # Generar el documento
    generated_files = doc.generate()
    
    print("✅ Documento paper generado sin TOC")
    print(f"📄 Archivos generados: {generated_files}")
    
    # Verificar que se generó correctamente
    html_file = generated_files.get('html')
    if html_file and os.path.exists(html_file):
        print(f"✅ Archivo HTML generado: {html_file}")
        
        # Leer el contenido del archivo HTML para verificar
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar que NO contiene TOC
        toc_indicators = [
            'id="TOC"',  # El elemento específico del TOC
            'Table of contents'  # El título visible
        ]
        
        toc_found = any(indicator in content for indicator in toc_indicators)
        
        if toc_found:
            print("❌ ADVERTENCIA: El documento paper todavía contiene TOC visible")
            return False
        else:
            print("✅ CONFIRMADO: El documento paper NO contiene TOC visible")
            return True
    else:
        print("❌ ERROR: No se pudo generar el archivo HTML")
        return False

if __name__ == "__main__":
    test_paper_no_toc()