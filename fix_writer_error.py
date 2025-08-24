"""
SOLUCIÓN PARA EL ERROR: NameError: name 'writer' is not defined

PROBLEMA:
El código intenta acceder a 'writer' directamente, pero quick_setup() 
lo configura como una variable global en builtins.writer

SOLUCIÓN - USO CORRECTO:
"""

# 1. OPCIÓN RECOMENDADA: Acceder a writer desde builtins
import os
from ePy_docs import quick_setup

# Ejecutar quick_setup (esto configura writer en builtins.writer)  
result = quick_setup(layout_name='minimal', sync_files=True, responsability=True)
current_dir = os.getcwd()

# ✅ CORRECTO: Acceder a writer desde builtins
import builtins
writer = builtins.writer
writer.output_dir = os.path.join(current_dir, "results", "report")

print("✅ Writer configurado correctamente!")
print(f"📁 Output directory: {writer.output_dir}")

# 2. OPCIÓN ALTERNATIVA: Obtener writer desde el resultado de quick_setup
# result = quick_setup(layout_name='minimal', sync_files=True, responsability=True)
# writer = result.get('writer')  # Obtener writer del resultado
# if writer:
#     writer.output_dir = os.path.join(current_dir, "results", "report")

# 3. OPCIÓN DIRECTA: Crear writer manualmente si quick_setup falla
# from ePy_docs.api.report import ReportWriter
# if 'writer' not in result or result['writer'] is None:
#     writer = ReportWriter(
#         file_path=os.path.join(current_dir, "results", "report.pdf"),
#         output_dir=os.path.join(current_dir, "results", "report"),
#         auto_print=True
#     )

print("🎯 TODAS LAS OPCIONES DISPONIBLES PARA ACCEDER AL WRITER:")
print("   1. ✅ builtins.writer (recomendado)")  
print("   2. ✅ result.get('writer') (desde quick_setup)")
print("   3. ✅ ReportWriter(...) (crear manualmente)")
