# RESUMEN CRÍTICO: Estado del Sistema y Problemas

## Fecha: 2025-11-12

## Problemas Identificados

### 1. ❌ CRÍTICO: Document Type "Report" mal configurado
**Problema**: Report usa `documentclass: "article"` en lugar de `documentclass: "report"`
**Impacto**: Report parece paper, no tiene estructura de reporte técnico
**Solución**: ✅ CORREGIDO - Cambiado a `documentclass: "report"`, márgenes ajustados (1in laterales, 1.5in arriba/abajo)

### 2. ❌ CRÍTICO: 20 tests fallando (15%)
**Categorías de fallos**:

#### A. Tests de Columnas (2 fallos)
- `test_calculate_width_single_column`: Test esperaba 3.1 pero matemática correcta da 3.25
- `test_invalid_column_span`: Test pedía 3 columnas en layout de 2 columnas
- **Solución**: ✅ CORREGIDO - Tests actualizados con valores matemáticamente correctos

#### B. Tests de Fuentes Handwritten (4 fallos)
- `test_handwritten_specific_flow`: No encuentra `anm_ingenieria_2025` en font_list
- `test_handwritten_layout_has_font_config`: Retorna cadena vacía
- `test_handwritten_layout_has_fallback`: Sin configuración de fallback
- `test_fonts_dir_passed_to_latex_config`: No pasa fonts_dir correctamente
- **Causa**: Layout usa `font_family_ref` pero código busca `font_family`
- **Estado**: ⚠️ PENDIENTE - Necesita mapeo correcto de referencias

#### C. Tests de Tablas con show_figure (10 fallos)
- `test_table_show_figure_uses_markdown_format`: Esperan `#tbl-1` pero generan `![Tabla 1...]`
- `test_add_table_increments_counter`: Contador incrementa 2 veces en vez de 1
- `test_add_table_with_max_rows_*`: Errores en `_process_split_table()` - múltiples valores para argumento
- **Causa Principal**: TableOrchestrator tiene duplicación de parámetros en llamadas
- **Estado**: ⚠️ PENDIENTE - Necesita refactorización de TableOrchestrator

#### D. Tests de Contadores (3 fallos)
- Contadores se incrementan 2 veces: una en procesamiento, otra en generación
- **Estado**: ⚠️ PENDIENTE - Relacionado con problema C

## Estado Actual

### ✅ Completado
1. Fix colores PDF - Secciones ahora visibles (brandQuinary en vez de brandPrimary)
2. Report documentclass corregido (report en vez de article)
3. Tests de columnas corregidos

### ⚠️ Pendiente Crítico
1. **Mapeo font_family_ref → font_family** en configuración
2. **TableOrchestrator refactorización** - eliminar duplicación de parámetros
3. **Contadores de tablas** - incrementar solo una vez
4. **Formato show_figure** - generar `#tbl-X` en vez de `![Tabla X...]`

## Análisis de Impacto

**Tests pasando**: 113/133 (85%)
**Tests fallando**: 20/133 (15%)

**Prioridad de fixes**:
1. 🔴 **ALTA**: Tablas (10 fallos) - Funcionalidad core rota
2. 🟡 **MEDIA**: Fuentes handwritten (4 fallos) - Un layout específico
3. 🟢 **BAJA**: Contadores (3 fallos) - Cosmético, no bloquea funcionalidad

## Recomendación

El usuario tiene razón - la configuración de document_types y layouts tiene problemas de integración.
Necesitamos:

1. **Mapeo consistente** entre layouts/*.epyson (que usan `*_ref`) y código (que busca campos directos)
2. **Tests actualizados** que reflejen comportamiento esperado real
3. **Refactorización de TableOrchestrator** para eliminar duplicación de parámetros

## Próximos Pasos

1. Corregir TableOrchestrator (mayor impacto - 10 tests)
2. Implementar mapeo correcto de font_family_ref
3. Validar contadores de tablas
4. Ejecutar suite completa nuevamente
