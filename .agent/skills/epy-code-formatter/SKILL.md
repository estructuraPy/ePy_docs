---
name: epy-code-formatter
description: Aplica los estándares de arquitectura, diseño y documentación de ePy Suite v0.1.0 (Zero Legacy) al código y documentación de las librerías del ecosistema, y desarrolla las funcionalidades que queden pendientes.
---

# Instrucciones

Utiliza este skill para formatear y estandarizar código y documentación de ePy Suite según los lineamientos de la arquitectura v0.1.0.

## 1. Activación y Contexto
**Mandatorio**: Al iniciar, pregunta al usuario si desea proporcionar una **Librería de Ejemplo** (ej. `ePy_timber`) que ya cumpla con los estándares para usarla como referencia de estilo.

## 2. Estándares de Documentación (Manuales)
Para cada manual de referencia (`ePy_*_guidelines.md`):
- **Encabezado**: `# ePy_{nombre} — Manual de Referencia (Arquitectura v0.1.0)`.
- **Metadatos**: Versión 0.1.0, Estado "ESTÁNDAR DE ORO", Filosofía, Rol y Responsabilidades.
- **Secciones**: Orden exacto (Misión, Directorios, Configuración, Núcleo/API, Técnicos, Visualización, Reporteo, Interoperabilidad, QA, Normas, Checklist).

## 3. Estándares de Validación y Notebooks
Asegura que cada librería implemente los 3 sets obligatorios de cuadernos:
1. **Educativo**: Uso básico de la API.
2. **Pedagógico**: Mecánica interactiva (Plotly) y modelos constitutivos.
3. **Uso Profesional**: Casos reales y optimización.

**Regla Crítica de Verificación**:
- Cada cuaderno DEBE tener una celda de comparación **Librería vs Cálculo a Mano**.
- Debe existir un archivo `.validation` en formato Quarto para cada elemento diseñado.
- La tolerancia numérica permitida es `< 0.1%`.

## 4. Estándares Técnicos de Código
- **Unidades**: Sufijos obligatorios (`_m`, `_kN`, `_MPa`).
- **Precisión**: Mínimo 5 cifras significativas en todos los reportes.
- **Ubicación de Datos**: Los resultados y el registro del proyecto deben ir a `.epy_suite/` en el CWD.
- **Reporteo**: Soporte para `results_path` configurable y generación de LaTeX paso a paso.

## 5. Auditoría de Calidad
Una vez aplicado el formato, recomienda al usuario ejecutar el skill `code-review` para auditar la calidad final y asegurar el cumplimiento de los principios SOLID y la política Zero Legacy.

## 6. Recursos de Referencia (Mandatorios)
Utiliza obligatoriamente los manuales maestros ubicados en el directorio `recursos/` de este skill para asegurar la precisión técnica según el componente:
- `development_prompt_epysuite.md`: Directivas primarias y Definition of Done.
- `ePy_suite_guidelines.md`: Arquitectura maestra y estándares globales.
- `ePy_analysis_guidelines.md`: Orquestación y mecánica de fibras.
- `ePy_timber_guidelines.md`, `ePy_concrete_guidelines.md`, `ePy_steel_guidelines.md`, `ePy_masonry_guidelines.md`, `ePy_geotechnical_guidelines.md`, `ePy_composite_guidelines.md`: Manuales por material.
- `ePy_connections_guidelines.md`, `ePy_loads_guidelines.md`, `ePy_plotter_guidelines.md`, `ePy_blender_guidelines.md`: Manuales especializados.

## 7. Desarrollo de Código Pendiente
**Rol de Arquitecto Proactivo**: Este skill no solo debe "limpiar" el código, sino que debe **completar el desarrollo**.
- **Detección**: Identifica `TODO`, `FIXME`, celdas vacías en notebooks, o lógica marcada como "placeholder".
- **Implementación**: Desarrolla la lógica faltante siguiendo estrictamente los manuales de referencia en `recursos/`.
- **Coherencia**: Asegura que las nuevas funciones mantengan el estilo de sufijos de unidades (`_m`, `_kN`) y precisión de 5 cifras.
- **Validación Inmediata**: Al implementar algo nuevo, crea o actualiza la celda de comparación **Librería vs Manual** para verificarlo.

## 8. Limpieza de Archivos Temporales
**Higiene del Proyecto**: Mantén el entorno de trabajo limpio de archivos residuales.
- **Eliminación**: Al finalizar una tarea de desarrollo o formateo, elimina scripts de generación temporales (ej. `_gen_*.py`), archivos de respaldo, y basura de Jupyter (`.ipynb_checkpoints`).
- **Directorios**: Limpia carpetas `__pycache__` y `.pytest_cache` si no son necesarias en el contexto actual.
- **Proactividad**: No esperes a que el usuario lo pida; si un archivo fue creado solo para una validación intermedia, elimínalo al terminar.

