#!/usr/bin/env python3
"""
Test final: Configuración CSL por layout completada
Verificación que academic, scientific, handwritten y corporate usan ieee.csl
"""

import json

def verificar_configuracion_csl():
    """Verificación final de la configuración CSL"""
    
    # Layouts que deben usar IEEE según la solicitud del usuario
    ieee_layouts = ['academic', 'scientific', 'handwritten', 'corporate']
    
    print("🎯 CONFIGURACIÓN CSL POR LAYOUT - VERIFICACIÓN FINAL")
    print("=" * 60)
    print("Layouts que deben usar ieee.csl:")
    print("• academic, scientific, handwritten, corporate")
    print()
    
    all_correct = True
    
    for layout_name in ieee_layouts:
        layout_path = f"src/ePy_docs/config/layouts/{layout_name}.epyson"
        
        try:
            with open(layout_path, 'r', encoding='utf-8') as f:
                layout_config = json.load(f)
            
            citation_style = layout_config.get('citation_style', 'NO CONFIGURADO')
            
            if citation_style == 'ieee':
                print(f"✅ {layout_name.upper():<12} → citation_style: '{citation_style}'")
            else:
                print(f"❌ {layout_name.upper():<12} → citation_style: '{citation_style}' (esperado: 'ieee')")
                all_correct = False
                
        except Exception as e:
            print(f"❌ {layout_name.upper():<12} → Error: {e}")
            all_correct = False
    
    print("\n" + "=" * 60)
    
    if all_correct:
        print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("   Todos los layouts solicitados ahora usan ieee.csl por defecto")
        print("\n📋 RESUMEN DE CAMBIOS REALIZADOS:")
        print("   • handwritten: harvard → ieee")
        print("   • corporate: apa → ieee")
        print("   • academic: ieee (ya configurado)")
        print("   • scientific: ieee (ya configurado)")
        print("\n✨ El sistema de referencias está listo para usar con")
        print("   configuración automática por layout")
    else:
        print("⚠️  Algunos layouts necesitan corrección")
    
    return all_correct

if __name__ == "__main__":
    verificar_configuracion_csl()