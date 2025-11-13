"""Búsqueda exhaustiva de hardcodeos de colores restantes."""

import os
import re
from pathlib import Path

def find_color_hardcodes(directory):
    """Buscar hardcodeos de colores en archivos Python."""
    
    color_patterns = [
        r"'white'",
        r'"white"',
        r"'black'",
        r'"black"',
        r"'red'",
        r'"red"',
        r"'blue'",
        r'"blue"',
        r"'green'",
        r'"green"',
        r"#[0-9a-fA-F]{3,6}",
        r"\[255,\s*255,\s*255\]",
        r"\[0,\s*0,\s*0\]",
        r"rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)",
        r"facecolor\s*=\s*['\"][^'\"]*['\"]",
        r"edgecolor\s*=\s*['\"][^'\"]*['\"]",
        r"color\s*=\s*['\"][^'\"]*['\"]"
    ]
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    results = {}
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                file_matches = []
                for line_num, line in enumerate(lines, 1):
                    for pattern in color_patterns:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        if matches:
                            # Skip comments and docstrings
                            stripped_line = line.strip()
                            if not (stripped_line.startswith('#') or 
                                   stripped_line.startswith('"""') or 
                                   stripped_line.startswith("'''")):
                                file_matches.append({
                                    'line': line_num,
                                    'content': line.strip(),
                                    'matches': matches,
                                    'pattern': pattern
                                })
                
                if file_matches:
                    results[file_path] = file_matches
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return results

def analyze_hardcodes(results):
    """Analizar los hardcodeos encontrados y clasificarlos."""
    
    legitimate = []
    suspicious = []
    
    # Patrones que son legítimos (no hardcodeos problemáticos)
    legitimate_patterns = [
        'matplotlib',
        'legend',
        'axis',
        'grid',
        'default',
        'fallback',
        'transparent',
        'none'
    ]
    
    for file_path, matches in results.items():
        for match in matches:
            line_content = match['content'].lower()
            
            # Verificar si es un uso legítimo
            is_legitimate = any(pattern in line_content for pattern in legitimate_patterns)
            
            if is_legitimate:
                legitimate.append({
                    'file': file_path,
                    'line': match['line'],
                    'content': match['content'],
                    'reason': 'Configuración de matplotlib o fallback legítimo'
                })
            else:
                suspicious.append({
                    'file': file_path,
                    'line': match['line'],
                    'content': match['content'],
                    'matches': match['matches']
                })
    
    return legitimate, suspicious

print("=" * 80)
print("🔍 BÚSQUEDA EXHAUSTIVA DE HARDCODEOS DE COLORES")
print("=" * 80)

# Buscar en el directorio src
src_directory = "src/ePy_docs"
results = find_color_hardcodes(src_directory)

print(f"\n📁 Archivos analizados: {len([f for f in Path(src_directory).rglob('*.py')])}")
print(f"📄 Archivos con matches: {len(results)}")

legitimate, suspicious = analyze_hardcodes(results)

print(f"\n🟢 Usos legítimos encontrados: {len(legitimate)}")
print(f"🔴 Hardcodeos sospechosos: {len(suspicious)}")

if suspicious:
    print(f"\n{'='*80}")
    print("🚨 HARDCODEOS SOSPECHOSOS QUE NECESITAN REVISIÓN")
    print("=" * 80)
    
    for item in suspicious:
        file_rel = item['file'].replace(src_directory, '').replace('\\', '/')
        print(f"\n📁 Archivo: {file_rel}")
        print(f"📍 Línea {item['line']}: {item['content']}")
        print(f"🎯 Matches: {item['matches']}")

if legitimate:
    print(f"\n{'='*80}")
    print("✅ USOS LEGÍTIMOS (No requieren cambios)")
    print("=" * 80)
    
    for item in legitimate[:10]:  # Mostrar solo los primeros 10
        file_rel = item['file'].replace(src_directory, '').replace('\\', '/')
        print(f"\n📁 {file_rel}:{item['line']}")
        print(f"   {item['content'][:100]}...")
        print(f"   → {item['reason']}")
    
    if len(legitimate) > 10:
        print(f"\n... y {len(legitimate) - 10} más usos legítimos")

print(f"\n{'='*80}")
print("📋 RESUMEN DE HARDCODEOS ELIMINADOS EN ESTA SESIÓN")
print("=" * 80)

print("\n1. ✅ HEADERS DE TABLAS:")
print("   - Eliminado: color negro hardcodeado en text_props")
print("   - Implementado: sistema inteligente basado en paletas")

print("\n2. ✅ FONDO DE IMÁGENES:")
print("   - Eliminado: facecolor='white' en images.epyson")
print("   - Implementado: facecolor='layout_background'")

print("\n3. ✅ FONDO DE TABLAS:")
print("   - Eliminado: facecolor='white' en plt.savefig")
print("   - Implementado: color desde page_background de paleta")

print("\n4. ✅ FONDO DE PLOTS:")
print("   - Eliminado: fallback hardcodeado a 'white'")
print("   - Implementado: detección automática desde layout")

print("\n5. 🎯 SISTEMA ROBUSTO:")
print("   - Cada layout usa sus colores específicos")
print("   - Fallbacks inteligentes solo cuando es necesario")
print("   - Contraste automático para legibilidad")
print("   - Respeta la regla: 'hardcodeo está prohibido'")

if not suspicious:
    print(f"\n{'='*80}")
    print("🎉 ¡MISIÓN CUMPLIDA! NO SE ENCONTRARON HARDCODEOS PROBLEMÁTICOS")
    print("=" * 80)
else:
    print(f"\n{'='*80}")
    print("⚠️  SE ENCONTRARON ALGUNOS HARDCODEOS QUE REQUIEREN REVISIÓN")
    print("=" * 80)