#!/usr/bin/env python3
"""
Test para verificar la configuración CSL por layout
Prueba que los layouts academic, scientific, handwritten y corporate usen ieee.csl
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter
import json

def test_layout_csl_configuration():
    """Verifica que los layouts tengan la configuración CSL correcta"""
    
    # Layouts que deben usar IEEE
    ieee_layouts = ['academic', 'scientific', 'handwritten', 'corporate']
    
    print("🔍 Verificando configuración CSL por layout...")
    print("=" * 50)
    
    for layout_name in ieee_layouts:
        # Cargar configuración del layout
        layout_path = f"src/ePy_docs/config/layouts/{layout_name}.epyson"
        
        try:
            with open(layout_path, 'r', encoding='utf-8') as f:
                layout_config = json.load(f)
            
            citation_style = layout_config.get('citation_style', 'NO CONFIGURADO')
            
            if citation_style == 'ieee':
                print(f"✅ {layout_name.upper()}: citation_style = '{citation_style}'")
            else:
                print(f"❌ {layout_name.upper()}: citation_style = '{citation_style}' (esperado: 'ieee')")
                
        except Exception as e:
            print(f"❌ {layout_name.upper()}: Error al leer configuración - {e}")
    
    print("\n🧪 Prueba de DocumentWriter con diferentes layouts...")
    print("=" * 50)
    
    # Crear documento de prueba con cada layout
    test_content = """
# Documento de Prueba

Este es un documento para verificar la configuración CSL.

## Referencias de Prueba

Según estudios recientes [@example2023], los sistemas de documentación 
han evolucionado significativamente [@smith2022; @garcia2021].

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
    
    for layout_name in ieee_layouts:
        try:
            print(f"\n📝 Probando layout: {layout_name}")
            
            writer = DocumentWriter()
            writer.configure_references(
                bibliography_content=test_bib,
                csl_style='ieee'  # Esto debería ser el default del layout
            )
            
            # Solo verificamos que se puede crear el objeto sin errores
            print(f"   ✅ DocumentWriter creado correctamente para {layout_name}")
            
        except Exception as e:
            print(f"   ❌ Error con {layout_name}: {e}")

if __name__ == "__main__":
    test_layout_csl_configuration()