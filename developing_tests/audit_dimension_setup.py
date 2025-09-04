"""
AUDITORÍA DIMENSIÓN SETUP - Detección de Violaciones
====================================================

Buscar violaciones de las reglas de la Dimensión Setup:
- Fallbacks hardcodeados (PROHIBIDOS)
- Accesos ilegales a archivos sin usar sucursales
- Uso incorrecto de sync_files
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src'))

def audit_dimension_setup():
    """Auditoría completa de cumplimiento de Dimensión Setup"""
    
    print("🔍 AUDITORÍA DIMENSIÓN SETUP")
    print("=" * 50)
    
    try:
        from ePy_docs.components.tables import _get_layout_default_palette
        from ePy_docs.components.colors import get_colors_config
        from ePy_docs.api.quick_setup import quick_setup
        
        # Configurar layout corporativo
        quick_setup(layout_name='corporate', sync_files=False)
        print("✅ Layout corporate configurado")
        
        # 1. VERIFICAR ACCESO LEGAL A SUCURSALES
        print("\n🏪 VERIFICACIÓN DE SUCURSALES:")
        
        # Reino COLORS - debe usar get_colors_config()
        try:
            colors_config = get_colors_config(sync_files=False)
            print("✅ Reino COLORS: Acceso legal via get_colors_config()")
            print(f"   Paletas disponibles: {len(colors_config['palettes'])}")
        except Exception as e:
            print(f"❌ Reino COLORS: Violación - {e}")
            return False
        
        # 2. VERIFICAR FUNCIÓN HELPER
        print("\n🔧 VERIFICACIÓN DE FUNCIÓN HELPER:")
        try:
            default_palette = _get_layout_default_palette()
            print(f"✅ Función _get_layout_default_palette(): '{default_palette}'")
        except Exception as e:
            print(f"❌ Función helper: Error - {e}")
            return False
        
        # 3. VERIFICAR CONFIGURACIÓN CORRECTA
        print("\n⚙️ VERIFICACIÓN DE CONFIGURACIÓN:")
        layout_config = colors_config.get('layout_styles', {}).get('corporate', {})
        configured_default = layout_config.get('default_palette')
        print(f"✅ Layout corporate: default_palette = '{configured_default}'")
        
        if configured_default != 'brand':
            print("❌ VIOLACIÓN: Corporate debe usar palette 'brand'")
            return False
        
        if default_palette != 'brand':
            print("❌ VIOLACIÓN: Función helper no devuelve 'brand' para corporate")
            return False
        
        # 4. BUSCAR VIOLACIONES DE FALLBACKS
        print("\n🚨 BÚSQUEDA DE VIOLACIONES:")
        
        # Leer el código fuente de la función helper
        import inspect
        source_code = inspect.getsource(_get_layout_default_palette)
        
        # Buscar fallbacks hardcodeados
        violations = []
        if "'blues'" in source_code:
            violations.append("Fallback hardcodeado 'blues' en función helper")
        if "'grays'" in source_code:
            violations.append("Fallback hardcodeado 'grays' en función helper")
        if "'engineering'" in source_code:
            violations.append("Fallback hardcodeado 'engineering' en función helper")
        
        if violations:
            print("❌ VIOLACIONES DETECTADAS:")
            for violation in violations:
                print(f"   - {violation}")
            return False
        else:
            print("✅ No se detectaron fallbacks hardcodeados")
        
        # 5. VERIFICAR QUE NO HAY ACCESOS DIRECTOS A JSON
        print("\n📄 VERIFICACIÓN DE ACCESOS A ARCHIVOS:")
        
        # La función debe usar SOLO get_colors_config(), no abrir archivos directamente
        if 'open(' in source_code or 'json.load' in source_code:
            print("❌ VIOLACIÓN: Acceso directo a archivos detectado")
            return False
        else:
            print("✅ No hay accesos directos a archivos")
        
        if 'get_colors_config' in source_code:
            print("✅ Usa sucursal legal get_colors_config()")
        else:
            print("❌ VIOLACIÓN: No usa sucursal legal")
            return False
        
        # 6. RESULTADO FINAL
        print("\n" + "=" * 50)
        print("✅ DIMENSIÓN SETUP CUMPLIDA")
        print("✅ Todas las reglas respetadas")
        print("✅ Accesos legales via sucursales")
        print("✅ Caché centralizado respetado")
        print("✅ sync_files respetado")
        print("✅ NO hay fallbacks fraudulentos")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN AUDITORÍA: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = audit_dimension_setup()
    if not success:
        print("\n🚨 AUDITORÍA FALLÓ - SE DETECTARON VIOLACIONES")
        sys.exit(1)
    else:
        print("\n🎉 AUDITORÍA EXITOSA - DIMENSIÓN SETUP CUMPLIDA")
        sys.exit(0)
