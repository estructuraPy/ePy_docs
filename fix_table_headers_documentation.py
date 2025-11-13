"""
SOLUCIÓN COMPLETA: Headers de Tablas con Colores de Paleta (No Hardcodeados)

PROBLEMA ORIGINAL:
================
Los headers de las tablas se estaban coloreando negros (hardcodeado), ignorando
la paleta configurada en cada layout. Esto violaba la regla de "no hardcodeo"
y causaba problemas de legibilidad cuando el fondo del header también era oscuro.

ANÁLISIS DEL PROBLEMA:
=====================
1. En _tables.py línea 447: cell.set_text_props(weight='bold') solo configuraba
   el peso del texto, pero no el color, dejando que matplotlib use negro por defecto.

2. Las configuraciones de layout tienen `header_color` en typography que especifica
   el color del texto, pero no se estaba utilizando.

3. Los layouts tienen paletas específicas que deberían aplicarse a los headers.

SOLUCIÓN IMPLEMENTADA:
=====================
Modificaciones en src/ePy_docs/core/_tables.py función _apply_table_colors():

1. LECTURA DE CONFIGURACIÓN DE COLOR DE TEXTO:
   - Se lee la configuración `header_color` de typography del layout
   - Se extrae palette y tone para determinar el color del texto

2. SISTEMA INTELIGENTE DE CONTRASTE:
   - Si no hay configuración específica, usa senary del default_palette
   - Calcula la luminancia del fondo y texto del header
   - Si ambos son oscuros: usa texto blanco (neutrals primary)
   - Si ambos son claros: usa texto negro (neutrals senary)

3. APLICACIÓN DEL COLOR:
   - Se aplica el color calculado con set_text_props(color=header_text_color)
   - Mantiene el peso bold si está configurado
   - Funciona para todas las categorías de tabla (engineering, environmental, etc.)

CÓDIGO AÑADIDO:
===============
```python
# Get header text color from layout typography configuration
from ePy_docs.core._config import get_layout
layout = get_layout(layout_style)
header_text_color = None
try:
    typography = layout.get('colors', {}).get('layout_config', {}).get('typography', {})
    header_color_config = typography.get('header_color', {})
    if 'palette' in header_color_config and 'tone' in header_color_config:
        header_text_color = get_palette_color_by_tone(
            header_color_config['palette'], 
            header_color_config['tone']
        )
except:
    pass

# If no header text color config found, use intelligent color selection
if header_text_color is None:
    # Use senary for text color, but with intelligent contrast
    header_text_color = get_palette_color_by_tone(default_palette_name, 'senary')
    
    # Check if header background is dark and text is also dark (low contrast)
    def is_dark_color(color):
        \"\"\"Check if a color is dark based on luminance.\"\"\"
        r, g, b = color
        # Calculate relative luminance (simplified)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return luminance < 0.5  # Dark if luminance < 50%
    
    # If both header background and text are dark, use white text instead
    if is_dark_color(header_color) and is_dark_color(header_text_color):
        header_text_color = get_palette_color_by_tone('neutrals', 'primary')  # White
    # If header background is light and text is also light, use black text instead
    elif not is_dark_color(header_color) and not is_dark_color(header_text_color):
        header_text_color = get_palette_color_by_tone('neutrals', 'senary')  # Black

for i in range(num_cols):
    cell = table[(0, i)]
    if style_config['styling']['header_bold']:
        cell.set_text_props(weight='bold', color=header_text_color)
    else:
        cell.set_text_props(color=header_text_color)
    cell.set_facecolor(header_color)
```

BENEFICIOS DE LA SOLUCIÓN:
=========================
✅ ELIMINACIÓN DE HARDCODEO: No más colores negro hardcodeados
✅ RESPETO A CONFIGURACIÓN: Usa paletas definidas en cada layout
✅ LEGIBILIDAD AUTOMÁTICA: Sistema inteligente de contraste
✅ COMPATIBILIDAD: Funciona con todos los layouts existentes
✅ ROBUSTEZ: Fallbacks automáticos cuando no hay configuración
✅ CATEGORÍAS: Respeta colores específicos por categoría de tabla

LAYOUTS BENEFICIADOS:
====================
- corporate: Usa palette corporate con colores dorados/azul marino
- academic: Usa palette academic con tonos índigo
- handwritten: Usa palette neutrals con contraste inteligente
- minimal: Usa palette minimal (blanco/negro) con contraste
- technical: Usa palette technical con tonos cian
- Y todos los demás layouts del sistema

TESTING REALIZADO:
==================
✅ test_table_colors_fix.py: Verificación básica de funcionamiento
✅ test_complete_table_colors.py: Generación completa de documentos
✅ Verificación de imágenes de tablas generadas
✅ Prueba con múltiples layouts y categorías de tabla
✅ Confirmación de eliminación de hardcodeo

RESULTADO FINAL:
===============
Los headers de las tablas ahora:
- Usan los colores especificados en la configuración del layout
- Tienen contraste automático para máxima legibilidad
- Respetan la regla "hardcodeo está prohibido"
- Funcionan consistentemente en todos los layouts
- Mantienen la estética específica de cada diseño

El problema ha sido completamente resuelto y el sistema es más robusto y configurable.
"""

print("=" * 80)
print("📋 DOCUMENTACIÓN DEL FIX IMPLEMENTADO")
print("=" * 80)
print(__doc__)