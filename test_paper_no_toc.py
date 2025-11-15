#!/usr/bin/env python3
"""
Test simple para verificar que el paper no tiene TOC
"""

from src.ePy_docs.writers import DocumentWriter

# Crear un documento tipo paper
doc = DocumentWriter(document_type="paper")

# Agregar contenido básico
doc.add_h1("Documento Paper Sin TOC")
doc.add_h2("Introducción")
doc.add_text("Este es un documento de prueba para verificar que los documentos tipo 'paper' no muestran tabla de contenidos.")

doc.add_h2("Contenido")
doc.add_text("Este documento debería renderizarse sin tabla de contenidos.")

doc.add_h3("Subsección de ejemplo")
doc.add_text("Esta subsección está aquí para tener más elementos en el documento.")

# Renderizar el documento
result = doc.generate(output_filename="test_paper_no_toc")

print("✅ Documento paper creado sin TOC")
print(f"📄 Archivos generados: {result}")