#!/usr/bin/env python3
# Test script temporal para verificar setup_library_core

import sys
sys.path.insert(0, 'src')

from ePy_docs.core.setup import setup_library_core

try:
    result = setup_library_core(layout='academic', sync_files=True)
    print("✅ setup_library_core funciona correctamente!")
    print(f"   Layout: {result['layout']}")
    print(f"   Configs cargados: {list(result['configs'].keys())}")
    print(f"   Sync files: {result['sync_files']}")
except Exception as e:
    print(f"❌ Error en setup_library_core: {e}")
    import traceback
    traceback.print_exc()
