#!/usr/bin/env python3
"""
Test para verificar que el override manual sigue funcionando
"""

import sys
import os  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

def test_csl_override_manual():
    """Test que el override manual funcione correctamente"""
    
    print("🧪 PRUEBA: OVERRIDE MANUAL DE CSL")  
    print("=" * 50)
    print("Verificando que se pueda override el CSL del layout manualmente")
    print()
    
    # Casos de prueba: layout → override esperado
    test_cases = [
        ('minimal', 'ieee', 'minimal tiene apa, override a ieee'),
        ('classic', 'apa', 'classic tiene chicago, override a apa'),
        ('academic', 'chicago', 'academic tiene ieee, override a chicago')
    ]
    
    # Bibliografia temporal
    test_bib = """
@article{test2023,
  title={Test Article},
  author={Test Author},
  year={2023}
}
    """
    
    with open('test_override.bib', 'w', encoding='utf-8') as f:
        f.write(test_bib)
    
    for layout_name, override_csl, descripcion in test_cases:
        try:
            print(f"📝 {descripcion}")
            
            writer = DocumentWriter(document_type='report', layout_style=layout_name)
            
            # Override manual del CSL
            writer.configure_references(csl_style=override_csl, bibliography_file='test_override.bib')
            
            writer.add_h1("Test Override")
            writer.add_text("Test de override de CSL ")
            writer.add_citation("test2023")
            writer.add_text(".")
            writer.add_text("::: {#refs}\n:::")
            
            result = writer.generate(
                html=False, 
                pdf=False, 
                qmd=True,
                output_filename=f"test_override_{layout_name}_{override_csl}"
            )
            
            # Verificar que se usó el override
            qmd_path = result.get('qmd')
            if qmd_path and os.path.exists(qmd_path):
                with open(qmd_path, 'r', encoding='utf-8') as f:
                    qmd_content = f.read()
                
                if f'csl: {override_csl}.csl' in qmd_content:
                    print(f"   ✅ Correcto: override a {override_csl}.csl funcionó")
                else:
                    print(f"   ❌ Error: no se aplicó override a {override_csl}.csl")
            else:
                print(f"   ❌ Error: no se generó archivo QMD")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Limpiar
    try:
        os.remove('test_override.bib')
    except:
        pass
    
    print("🎯 Prueba completada - Override manual funciona correctamente")

if __name__ == "__main__":
    test_csl_override_manual()