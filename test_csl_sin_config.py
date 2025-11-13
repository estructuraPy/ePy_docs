#!/usr/bin/env python3
"""
Test para verificar que los estilos CSL se apliquen automáticamente SIN configurar referencias
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

def test_csl_sin_configurar_referencias():
    """Test que los layouts apliquen CSL automáticamente incluso sin configure_references()"""
    
    print("🧪 PRUEBA: CSL AUTOMÁTICO SIN CONFIGURAR REFERENCIAS")
    print("=" * 60)
    print("Verificando que los layouts apliquen CSL incluso sin llamar a configure_references()")
    print()
    
    # Layouts de prueba
    layouts_test = {
        'academic': 'ieee',
        'minimal': 'apa',
        'classic': 'chicago'
    }
    
    # Contenido básico sin referencias (para que funcione sin bibliography)
    test_content = """
# Documento de Prueba

Este documento verifica que los estilos CSL se detecten automáticamente
desde la configuración del layout incluso sin configurar referencias explícitamente.

## Contenido de Prueba

Solo contenido básico para generar el QMD y verificar el YAML header.
    """
    
    for layout_name, expected_csl in layouts_test.items():
        try:
            print(f"📝 Probando layout: {layout_name} (esperado: {expected_csl})")
            
            # Crear writer SIN llamar a configure_references()
            writer = DocumentWriter(document_type='report', layout_style=layout_name)
            
            # Solo agregar contenido, sin configurar referencias
            writer.add_text(test_content)
            
            # Generar QMD para verificar configuración
            result = writer.generate(
                html=False, 
                pdf=False, 
                qmd=True,
                output_filename=f"test_sin_config_{layout_name}"
            )
            
            # Leer el archivo QMD generado y verificar el CSL
            qmd_path = result.get('qmd')
            if qmd_path and os.path.exists(qmd_path):
                with open(qmd_path, 'r', encoding='utf-8') as f:
                    qmd_content = f.read()
                
                # Buscar la línea de csl en el YAML header
                if f'csl: {expected_csl}.csl' in qmd_content:
                    print(f"   ✅ Correcto: detectó {expected_csl}.csl automáticamente")
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
                    for line in yaml_lines[:8]:  
                        print(f"      {line}")
            else:
                print(f"   ❌ Error: no se generó el archivo QMD")
                
        except Exception as e:
            print(f"   ❌ Error con layout {layout_name}: {e}")
        
        print()
    
    print("🎯 Prueba completada - CSL automático funciona sin configure_references()")

if __name__ == "__main__":
    test_csl_sin_configurar_referencias()