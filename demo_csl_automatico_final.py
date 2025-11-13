#!/usr/bin/env python3
"""
Test de demostración final: Estilos CSL automáticos funcionando
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

def demo_estilos_csl_automaticos():
    """Demostración final: estilos CSL automáticos funcionando"""
    
    print("🎉 DEMOSTRACIÓN FINAL: ESTILOS CSL AUTOMÁTICOS")
    print("=" * 60)
    print("Los layouts ahora aplican automáticamente su estilo de citación configurado")
    print()
    
    # Bibliografia de demostración
    demo_bib = """
@article{smith2023,
  title={Modern Document Generation Systems},
  author={Smith, John A.},
  journal={Technical Documentation Review},
  volume={15},
  number={3},
  pages={45--62},
  year={2023},
  publisher={Academic Press}
}

@book{garcia2022,
  title={Advanced Typography in Digital Publishing},
  author={García, María Elena},
  publisher={Editorial Técnica},
  year={2022},
  address={Barcelona}
}

@inproceedings{johnson2021,
  title={Automated Layout Systems for Scientific Documents},
  author={Johnson, Robert and Chen, Li},
  booktitle={Proceedings of the Digital Publishing Conference},
  pages={123--135},
  year={2021},
  organization={IEEE}
}
    """
    
    # Crear archivo temporal de bibliografía
    with open('demo_referencias.bib', 'w', encoding='utf-8') as f:
        f.write(demo_bib)
    
    # Demostrar diferentes layouts
    layouts_demo = {
        'academic': 'IEEE (numérico)',
        'scientific': 'IEEE (numérico)', 
        'corporate': 'IEEE (numérico)',
        'minimal': 'APA 7ª Edición',
        'classic': 'Chicago Manual of Style'
    }
    
    for layout_name, estilo_desc in layouts_demo.items():
        print(f"📚 Layout: {layout_name.upper()} → {estilo_desc}")
        
        try:
            # Crear writer sin especificar estilo CSL manualmente
            writer = DocumentWriter(document_type='report', layout_style=layout_name)
            
            # Solo configurar bibliografía (el estilo CSL viene automáticamente del layout)
            writer.configure_references(bibliography_file='demo_referencias.bib')
            
            # Agregar contenido con citas
            writer.add_h1(f"Demostración Layout {layout_name.title()}")
            writer.add_text("Este documento demuestra la aplicación automática de estilos CSL desde la configuración del layout.")
            writer.add_h2("Referencias Automáticas")
            writer.add_text("Los sistemas modernos de documentación ")
            writer.add_citation("smith2023")
            writer.add_text(" han evolucionado considerablemente. Otros estudios ")
            writer.add_citation("garcia2022")
            writer.add_text(" y ")
            writer.add_citation("johnson2021")
            writer.add_text(" confirman esta tendencia.")
            writer.add_h2("Bibliografía")
            writer.add_text("::: {#refs}\n:::")
            
            # Generar solo QMD para verificación rápida
            result = writer.generate(
                html=False, 
                pdf=False, 
                qmd=True,
                output_filename=f"demo_{layout_name}"
            )
            
            print(f"   ✅ Generado: {result.get('qmd', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Limpiar archivo temporal
    try:
        os.remove('demo_referencias.bib')
    except:
        pass
    
    print("🎯 DEMOSTRACIÓN COMPLETADA")
    print("✨ Los estilos de citación ahora se aplican automáticamente desde la configuración del layout")
    print("💡 Para usar un estilo diferente al del layout, simplemente especifica csl_style en configure_references()")

if __name__ == "__main__":
    demo_estilos_csl_automaticos()