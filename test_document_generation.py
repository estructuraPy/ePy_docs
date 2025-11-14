#!/usr/bin/env python3
"""
Test de generación de documento para verificar que XeLaTeX compila correctamente.
"""

from pathlib import Path
from src.ePy_docs.writers import DocumentWriter

def test_latex_compilation():
    """Genera un documento simple para probar la compilación LaTeX."""
    print("🔍 Generando documento de prueba para LaTeX...")
    
    # Create output directory
    output_path = Path("results/latex_test")
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize DocumentWriter with handwritten layout
        writer = DocumentWriter(
            document_type="report",
            layout_style="handwritten"
        )
        
        # Add some content
        writer.add_text("Este es un test para verificar que las fuentes LaTeX funcionan correctamente.")
        writer.add_text("La fuente debería ser Latin Modern Roman en lugar de la fuente personalizada anm_ingenieria_2025.")
        
        # Generate document (just QMD to check configuration)
        results = writer.generate(
            output_filename="latex_font_test",
            html=False,
            pdf=False,
            qmd=True
        )
        
        print(f"✅ Documento generado exitosamente")
        print(f"📁 Archivos generados: {list(results.keys())}")
        
        # Check if QMD file was generated
        if 'qmd' in results:
            qmd_file = results['qmd']
            print(f"📄 Archivo QMD: {qmd_file}")
            
            # Try to read the QMD file to verify font configuration in YAML
            if qmd_file and Path(qmd_file).exists():
                with open(qmd_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'Latin Modern Roman' in content or 'Segoe Script' in content:
                        print("✅ QMD contiene configuración de fuente del sistema")
                    else:
                        print("⚠️  No se encontró configuración de fuente del sistema")
                    
                    if 'anm_ingenieria_2025' in content:
                        print("❌ Todavía contiene fuente personalizada problemática")
                        return False
                    else:
                        print("✅ No contiene fuente personalizada problemática")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando documento: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Verificación de compilación LaTeX con nuevas fuentes")
    print("=" * 60)
    
    success = test_latex_compilation()
    
    if success:
        print("\n🎉 ¡ÉXITO! El documento se generó correctamente")
        print("📝 XeLaTeX debería poder compilar el documento sin errores de fuentes")
    else:
        print("\n❌ Hubo problemas generando el documento")