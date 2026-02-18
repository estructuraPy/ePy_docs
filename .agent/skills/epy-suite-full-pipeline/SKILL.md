---
name: epy-suite-full-pipeline
description: Orquestador maestro que ejecuta la triada de calidad de ePy Suite: epy-code-formatter, code-review y epy-validation-audit en secuencia obligatoria.
---

# Instrucciones

Utiliza este skill para realizar una revisión integral y automática de una librería de ePy Suite. Este skill orquesta la ejecución sucesiva de tres herramientas críticas para garantizar la excelencia física, arquitectónica y técnica.

## 1. Entrada de Usuario
Al iniciar, solicita al usuario:
1.  **Ruta de la Librería**: El directorio raíz del componente a procesar (ej. `src/ePy_timber/`).
2.  **Librería de Referencia (Opcional)**: Una librería que ya cumpla los estándares para guiar al formatter.

## 2. Flujo de Ejecución (Secuencia Obligatoria)

### PASO 1: epy-code-formatter
- **Objetivo**: Estandarizar la "forma" y el "estilo".
- **Acción**: Aplica sufijos de unidades, precisión de 5 cifras, estructura de directorios v0.1.0 y genera los 3 sets de notebooks con celdas de validación.
- **Salida**: Código y documentación formateados según el Estándar de Oro.

### PASO 2: code-review
- **Objetivo**: Auditar la "arquitectura" y el "diseño".
- **Acción**: Verifica principios SOLID, ausencia de Legacy, limpieza de docstrings y arquitectura de módulos (Zero Hardcoding).
- **Salida**: Reporte de cumplimiento arquitectónico. Requiere aprobación para pasar al Paso 3.

### PASO 3: epy-validation-audit
- **Objetivo**: Garantizar la "verdad técnica" y "precisión".
- **Acción**: Ejecuta los notebooks, valida contra el Código Sísmico de Costa Rica y normativas internacionales (ACI, AISC, NDS), verifica la precisión de 5 cifras y aplica correcciones automáticas si el error supera el 1%.
- **Salida**: Reporte final de validación funcional y técnica con archivos `.validation` renderizados.

## 3. Reglas de Transición
- No se debe pasar al siguiente paso si existen errores críticos bloqueantes en el paso anterior.
- En el Paso 3, el skill tiene permiso de **autocorrección iterativa** hasta alcanzar el éxito.

## 4. Persistencia y Gestión de Recursos (CRÍTICO)
- **Ejecución Sin Paro**: El skill TIENE la instrucción de no detenerse hasta que la validación final del Paso 3 sea exitosa. Si encuentra errores, debe corregirlos y reintentar automáticamente.
- **Gestión de Tokens/Modelo**: 
    - Si el contexto del LLM se acerca a su límite o se agotan los tokens mid-proceso, el agente debe cambiar a un modelo con mayor ventana de contexto (o solicitar el cambio al usuario si no tiene permisos directos) sin perder el progreso del estado de la librería.
    - Debe guardar checkpoints internos del progreso para reanudar exactamente donde se quedó tras un cambio de modelo o reinicio.

## 5. Reporte Final Unificado
Al finalizar la triada, genera un breve resumen ejecutivo:
- ✅ **Formateo**: [Estado]
- ✅ **Arquitectura**: [Estado]
- ✅ **Validación**: [Estado/Precisión Final]
- **Ubicación de Resultados**: Indica la ruta de la carpeta `results/` generada.
