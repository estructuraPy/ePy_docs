#!/usr/bin/env python3
"""
Test para verificar qué fuentes se están usando actualmente en tablas y documentos.
"""

import pandas as pd
from pathlib import Path
from src.ePy_docs.writers import DocumentWriter

def test_current_font_usage():
    """Test para ver qué fuentes se están usando actualmente."""
    print("🔍 Verificando uso actual de fuentes...")
    
    # Create test data
    df = pd.DataFrame({
        'Columna A': ['Texto 1', 'Texto 2', 'Texto 3'],
        'Columna B': ['Valor 1', 'Valor 2', 'Valor 3']
    })
    
    # Test with handwritten layout
    print("\n--- Testing Handwritten Layout ---")
    try:
        writer = DocumentWriter(
            document_type="report",
            layout_style="handwritten"
        )
        
        writer.add_text("Este texto debería usar fuente personalizada (anm_ingenieria_2025 o similar)")
        writer.add_table(df, "Tabla de prueba - debería usar fuente personalizada")
        
        # Generate only HTML and QMD to check
        results = writer.generate(
            output_filename="font_test_handwritten",
            html=True,
            pdf=False,
            qmd=True
        )
        
        print(f"✅ Archivos generados: {list(results.keys())}")
        
        # Check QMD content
        if 'qmd' in results:
            qmd_file = Path(results['qmd'])
            if qmd_file.exists():
                content = qmd_file.read_text(encoding='utf-8')
                print(f"📄 QMD file: {qmd_file}")
                
                # Look for font configuration
                if 'Segoe Script' in content:
                    print("🔍 Encontrada: Segoe Script")
                if 'anm_ingenieria_2025' in content:
                    print("🔍 Encontrada: anm_ingenieria_2025")
                if 'Latin Modern Roman' in content:
                    print("🔍 Encontrada: Latin Modern Roman")
                if 'helvetica' in content.lower():
                    print("🔍 Encontrada: helvetica (alguna variante)")
        
        # Check HTML content if generated
        if 'html' in results:
            html_file = Path(results['html'])
            if html_file.exists():
                content = html_file.read_text(encoding='utf-8')
                print(f"📄 HTML file: {html_file}")
                
                # Look for CSS font declarations
                if 'font-family' in content:
                    import re
                    font_families = re.findall(r'font-family:\s*([^;]+)', content)
                    print(f"🎨 Font families found in CSS: {font_families[:5]}")  # First 5
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Verificación de fuentes actuales")
    print("=" * 60)
    
    test_current_font_usage()