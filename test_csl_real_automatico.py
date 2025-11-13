#!/usr/bin/env python3
"""
Test CORRECTO para verificar aplicación automática de estilos CSL desde layouts
Este test NO especifica csl_style, para probar la detección automática real
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Necesito crear una función especial que permita configurar solo bibliografía sin CSL
def crear_writer_con_bibliografia_solamente(layout_style, bib_file):
    """Crear writer y configurar bibliografia SIN especificar CSL style"""
    from ePy_docs.writers import DocumentWriter
    
    writer = DocumentWriter(document_type='report', layout_style=layout_style)
    
    # Configurar directamente el _reference_config sin pasar por configure_references
    # para evitar el csl_style='ieee' por defecto
    if not hasattr(writer, '_reference_config'):
        writer._reference_config = {}
    writer._reference_config['bibliography'] = bib_file
    # Nota: NO se configura 'csl' aquí, para que use el del layout
    
    return writer

def test_csl_aplicacion_automatica_real():
    """Test real de aplicación automática de estilos CSL desde layouts"""
    
    print("🧪 PRUEBA REAL: APLICACIÓN AUTOMÁTICA DE ESTILOS CSL")
    print("=" * 65)
    print("Verificando detección automática sin especificar csl_style manualmente")
    print()
    
    # Layouts de prueba con su estilo CSL esperado
    layouts_test = {
        'academic': 'ieee',
        'scientific': 'ieee', 
        'handwritten': 'ieee',
        'corporate': 'ieee',
        'minimal': 'apa',
        'classic': 'chicago'
    }
    
    # Bibliografia de prueba
    test_bib = """
@article{example2023,
  title={Advanced Documentation Systems},
  author={Example, John},
  journal={Tech Journal},
  year={2023}
}

@book{smith2022,
  title={Modern Writing Tools},
  author={Smith, Jane},
  publisher={Academic Press},
  year={2022}
}
    """
    
    # Crear archivo temporal de bibliografía
    with open('test_real_auto.bib', 'w', encoding='utf-8') as f:
        f.write(test_bib)
    
    # Probar cada layout
    for layout_name, expected_csl in layouts_test.items():
        try:
            print(f"📝 Layout: {layout_name} (esperado: {expected_csl})")
            
            # Crear writer SIN especificar CSL, solo bibliografía
            writer = crear_writer_con_bibliografia_solamente(layout_name, 'test_real_auto.bib')
            
            # Agregar contenido con citas
            writer.add_h1("Test Automático")
            writer.add_text("Cita de prueba ")
            writer.add_citation("example2023")
            writer.add_text(" y ")
            writer.add_citation("smith2022")
            writer.add_text(".")
            writer.add_text("::: {#refs}\n:::")
            
            # Generar QMD
            result = writer.generate(
                html=False, 
                pdf=False, 
                qmd=True,
                output_filename=f"test_real_auto_{layout_name}"
            )
            
            # Verificar CSL en el QMD
            qmd_path = result.get('qmd')
            if qmd_path and os.path.exists(qmd_path):
                with open(qmd_path, 'r', encoding='utf-8') as f:
                    qmd_content = f.read()
                
                if f'csl: {expected_csl}.csl' in qmd_content:
                    print(f"   ✅ Correcto: detectó automáticamente {expected_csl}.csl")
                else:
                    print(f"   ❌ Error: no detectó {expected_csl}.csl")
                    # Mostrar YAML para debug
                    lines = qmd_content.split('\n')
                    in_yaml = False
                    for line in lines[:15]:
                        if line.strip() == '---':
                            if not in_yaml:
                                in_yaml = True
                                continue
                            else:
                                break
                        elif in_yaml and line.startswith('csl:'):
                            print(f"      Encontrado: {line}")
            else:
                print(f"   ❌ Error: no se generó QMD")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Limpiar archivo temporal
    try:
        os.remove('test_real_auto.bib')
    except:
        pass
    
    print("🎯 Prueba real completada")

if __name__ == "__main__":
    test_csl_aplicacion_automatica_real()