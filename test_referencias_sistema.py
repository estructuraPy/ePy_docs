#!/usr/bin/env python3
"""
Test script para verificar el sistema de referencias bibliográficas.
Prueba la configuración automática de CSL y archivos de bibliografía.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ePy_docs import DocumentWriter


def test_references_system():
    """Test the references system with automatic file copying."""
    
    print("=== TEST SISTEMA DE REFERENCIAS ===")
    
    # Create writer
    writer = DocumentWriter(
        document_type='report',
        layout_style='classic'
    )
    
    # Configure references - this should copy files automatically
    print("Configurando referencias IEEE...")
    writer.configure_references(
        csl_style='ieee',
        bibliography_file=None  # Use default bibliography
    )
    
    # Add content with citations
    writer.add_h1("Documento con Referencias")
    
    writer.add_text("Este documento demuestra el uso de referencias bibliográficas.")
    
    writer.add_h2("Introducción")
    writer.add_text("Según múltiples estudios ")
    writer.add_citation("Einstein1905")
    writer.add_text(" y ")
    writer.add_citation("Newton1687")
    writer.add_text(", las leyes de la física son fundamentales.")
    
    writer.add_text("Otros autores como ")
    writer.add_citation("Maxwell1865")
    writer.add_text(" han contribuido significativamente al campo.")
    
    writer.add_h2("Metodología")
    writer.add_text("Se utilizó el método propuesto por ")
    writer.add_citation("Gauss1809", page="42")
    writer.add_text(" para el análisis de datos.")
    
    # Generate documents
    print("\nGenerando documentos...")
    try:
        result = writer.generate(
            html=True,
            pdf=False,  # Skip PDF to avoid LaTeX issues
            qmd=True,
            output_filename="test_referencias"
        )
        
        print("✅ Documentos generados exitosamente!")
        
        for format_name, file_path in result.items():
            if file_path:
                print(f"   {format_name.upper()}: {file_path}")
                
        # Check if reference files were copied
        output_dir = Path(result['qmd']).parent
        
        print(f"\nVerificando archivos en: {output_dir}")
        
        # Check for CSL file
        csl_files = list(output_dir.glob("*.csl"))
        if csl_files:
            print(f"✅ Archivo CSL encontrado: {csl_files[0].name}")
        else:
            print("❌ Archivo CSL no encontrado")
            
        # Check for bibliography file  
        bib_files = list(output_dir.glob("*.bib"))
        if bib_files:
            print(f"✅ Archivo bibliografía encontrado: {bib_files[0].name}")
        else:
            print("❌ Archivo bibliografía no encontrado")
            
        # Check QMD content for references
        qmd_path = Path(result['qmd'])
        if qmd_path.exists():
            content = qmd_path.read_text(encoding='utf-8')
            
            if 'bibliography:' in content:
                print("✅ Configuración bibliography encontrada en QMD")
            else:
                print("❌ Configuración bibliography no encontrada en QMD")
                
            if 'csl:' in content:
                print("✅ Configuración CSL encontrada en QMD")
            else:
                print("❌ Configuración CSL no encontrada en QMD")
                
            # Count citations
            citation_count = content.count('[@')
            print(f"✅ Encontradas {citation_count} citas en el contenido")
            
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


def test_different_csl_styles():
    """Test different CSL styles."""
    
    print("\n=== TEST DIFERENTES ESTILOS CSL ===")
    
    styles = ['ieee', 'apa', 'chicago']
    
    for style in styles:
        print(f"\nProbando estilo: {style}")
        
        try:
            writer = DocumentWriter(document_type='report')
            writer.configure_references(csl_style=style)
            
            writer.add_h1(f"Test {style.upper()}")
            writer.add_text("Citation test ")
            writer.add_citation("Einstein1905")
            writer.add_text(".")
            
            result = writer.generate(
                html=False,
                pdf=False,
                qmd=True,
                output_filename=f"test_{style}"
            )
            
            # Check if correct CSL file was copied
            output_dir = Path(result['qmd']).parent
            csl_files = list(output_dir.glob(f"*{style}*.csl"))
            
            if csl_files:
                print(f"✅ {style.upper()}: Archivo CSL correcto copiado")
            else:
                print(f"❌ {style.upper()}: Archivo CSL no encontrado")
                
        except Exception as e:
            print(f"❌ {style.upper()}: Error - {e}")


if __name__ == "__main__":
    success = test_references_system()
    test_different_csl_styles()
    
    if success:
        print("\n🎉 ¡Test completado! Verificar archivos generados.")
    else:
        print("\n❌ Test falló. Revisar errores.")