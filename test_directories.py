#!/usr/bin/env python3
"""
Script de prueba para verificar que la configuración de directorios funcione correctamente.
"""
import os
import sys

# Añadir el directorio src al path para poder importar ePy_docs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_directory_configuration():
    """Prueba la configuración de directorios."""
    try:
        from ePy_docs.core.setup import get_output_directories, get_absolute_output_directories
        
        print("=== Prueba de configuración de directorios ===")
        print(f"Directorio actual de trabajo: {os.getcwd()}")
        
        print("\n1. Configuración relativa desde setup.json:")
        relative_dirs = get_output_directories()
        for key, path in relative_dirs.items():
            print(f"   {key}: {path}")
        
        print("\n2. Configuración absoluta:")
        absolute_dirs = get_absolute_output_directories()
        for key, path in absolute_dirs.items():
            print(f"   {key}: {path}")
            print(f"      Existe: {os.path.exists(path)}")
        
        print("\n3. Verificando que las rutas absolutas son correctas:")
        for key, abs_path in absolute_dirs.items():
            rel_path = relative_dirs[key]
            expected_abs = os.path.join(os.getcwd(), rel_path)
            matches = os.path.normpath(abs_path) == os.path.normpath(expected_abs)
            print(f"   {key}: {'✓' if matches else '✗'} {abs_path}")
            if not matches:
                print(f"      Esperado: {expected_abs}")
        
        print("\n4. Creando directorios de prueba:")
        for key, path in absolute_dirs.items():
            try:
                os.makedirs(path, exist_ok=True)
                print(f"   {key}: ✓ Creado/existe en {path}")
            except Exception as e:
                print(f"   {key}: ✗ Error creando {path}: {e}")
        
        print("\n=== Prueba completada ===")
        return True
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_report_writer():
    """Prueba la inicialización de ReportWriter."""
    try:
        print("\n=== Prueba de ReportWriter ===")
        
        # Crear un proyecto mínimo de prueba si no existe
        from ePy_docs.core.setup import get_absolute_output_directories
        
        dirs = get_absolute_output_directories()
        config_dir = dirs['configuration']
        os.makedirs(os.path.join(config_dir, 'project'), exist_ok=True)
        
        # Crear un archivo project.json mínimo si no existe
        project_json_path = os.path.join(config_dir, 'project', 'project.json')
        if not os.path.exists(project_json_path):
            import json
            project_data = {
                "project": {
                    "report": "test_report",
                    "name": "Proyecto de Prueba",
                    "description": "Proyecto para probar configuración de directorios"
                }
            }
            with open(project_json_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            print(f"   Creado project.json en: {project_json_path}")
        
        from ePy_docs.api.report import ReportWriter
        
        # Probar inicialización
        writer = ReportWriter(sync_files=True)
        
        print(f"   ReportWriter inicializado correctamente")
        print(f"   output_dir: {writer.output_dir}")
        print(f"   file_path: {writer.file_path}")
        print(f"   Directorio existe: {os.path.exists(writer.output_dir)}")
        
        return True
        
    except Exception as e:
        print(f"Error en la prueba de ReportWriter: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_directory_configuration()
    success2 = test_api_report_writer()
    
    if success1 and success2:
        print("\n🎉 Todas las pruebas pasaron correctamente!")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron.")
        sys.exit(1)
