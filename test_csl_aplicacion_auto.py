#!/usr/bin/env python3
"""
Test de aplicación automática de estilos CSL desde layouts
Verifica que los layouts apliquen su configuración citation_style automáticamente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter
import json

def test_csl_aplicacion_automatica():
    """Test de aplicación automática de estilos CSL desde layouts"""
    
    print("🧪 PRUEBA: APLICACIÓN AUTOMÁTICA DE ESTILOS CSL")
    print("=" * 60)
    print("Verificando que los layouts apliquen automáticamente su citation_style")
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
    
    # Contenido de prueba con referencias
    test_content = """
# Documento de Prueba con Referencias

Este documento verifica que los estilos CSL se apliquen automáticamente
desde la configuración del layout.

## Citas de Prueba

Según estudios recientes [@example2023], la documentación técnica ha 
evolucionado significativamente [@smith2022]. Otros autores como
[@garcia2021] han contribuido al tema.

## Bibliografía

::: {#refs}
:::
    """
    
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

@article{garcia2021,
  title={Digital Publishing Revolution},
  author={García, María},
  journal={Digital Studies},
  year={2021}
}
    """
    
    # Crear archivo temporal de bibliografía
    with open('test_referencias_auto.bib', 'w', encoding='utf-8') as f:
        f.write(test_bib)
    
    # Probar cada layout
    for layout_name, expected_csl in layouts_test.items():
        try:
            print(f"📝 Probando layout: {layout_name} (esperado: {expected_csl})")
            
            # Crear writer con el layout específico
            writer = DocumentWriter(document_type='report', layout_style=layout_name)
            
            # Solo configurar bibliografía, NO el estilo CSL (debería usar el del layout)
            writer.configure_references(bibliography_file='test_referencias_auto.bib')
            
            # Agregar contenido
            writer.add_text(test_content)
            
            # Generar QMD para verificar configuración
            result = writer.generate(
                html=False, 
                pdf=False, 
                qmd=True,
                output_filename=f"test_auto_{layout_name}"
            )
            
            # Leer el archivo QMD generado y verificar el CSL
            qmd_path = result.get('qmd')
            if qmd_path and os.path.exists(qmd_path):
                with open(qmd_path, 'r', encoding='utf-8') as f:
                    qmd_content = f.read()
                
                # Buscar la línea de csl en el YAML header
                if f'csl: {expected_csl}.csl' in qmd_content:
                    print(f"   ✅ Correcto: usa {expected_csl}.csl como esperado")
                else:
                    print(f"   ❌ Error: no encontró csl: {expected_csl}.csl en el QMD")
                    # Mostrar extracto del YAML para debug
                    lines = qmd_content.split('\n')
                    yaml_lines = []
                    in_yaml = False
                    for line in lines:
                        if line.strip() == '---':
                            if not in_yaml:
                                in_yaml = True
                            else:
                                break
                        elif in_yaml:
                            yaml_lines.append(line)
                    
                    print(f"   🔍 YAML encontrado:")
                    for line in yaml_lines[:10]:  # Mostrar primeras 10 líneas
                        print(f"      {line}")
            else:
                print(f"   ❌ Error: no se generó el archivo QMD")
                
        except Exception as e:
            print(f"   ❌ Error con layout {layout_name}: {e}")
        
        print()
    
    # Limpiar archivo temporal
    try:
        os.remove('test_referencias_auto.bib')
    except:
        pass
    
    print("🎯 Prueba completada. Si hay errores, revisar la integración layout → CSL")

if __name__ == "__main__":
    test_csl_aplicacion_automatica()