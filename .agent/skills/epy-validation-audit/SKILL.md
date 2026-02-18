---
name: epy-validation-audit
description: Valida el formato y la coherencia técnica de los archivos de validación (.qmd/Quarto) de ePy Suite, asegurando el cumplimiento de normas internacionales y de Costa Rica (CSCR).
---

# Instrucciones

Utiliza este skill para auditar archivos de validación generados por las librerías de ePy Suite. La auditoría se divide en **Formato** y **Contenido Técnico**.

## 1. Auditoría de Formato (Quarto)
Delega la validación estética y estructural al skill **`epy-qmd-formatter`**. Verifica que el archivo `.qmd` o `.validation` cumpla con sus estándares maestros:
- **Tablas y Figuras**: IDs en kebab-case y wrappers correctos.
- **Ecuaciones**: Sintaxis LaTeX y espaciado.
- **Callouts**: Uso correcto de bloques para ejemplos y notas técnicas.
- **Header YAML**: Título descriptivo, autor y formato compatible.

## 2. Auditoría de Contenido Técnico (Coherencia Normativa)
Verifica que los cálculos sigan estas reglas críticas:
- **LRFD por Defecto**: Si la normativa permite ASD y LRFD, el cálculo DEBE usar LRFD por defecto, a menos que se especifique lo contrario.
- **Códigos Base**:
    - **Concreto**: ACI 318.
    - **Acero**: AISC 360 / AISI S100.
    - **Madera**: NDS.
    - **Costa Rica**: Debe ser coherente con el **Código Sísmico de Costa Rica (CSCR)** y el **Código de Cimentaciones** cuando aplique.
- **Variables**: Validación de que se usen sufijos de unidades (`_m`, `_kN`, `_MPa`) y precisión constante de **5 cifras significativas**.

## 3. Verificación de Tolerancia
- Compara el resultado de la librería vs el cálculo manual.
- **Tolerancia Máxima**: El error debe ser **menor al 1%**.
- Si el error es mayor, marca el archivo como "RECHAZADO" y especifica la discrepancia técnica.

## 4. Auditoría de Ejecución y Precisión
El skill DEBE validar que los cuadernos sean funcionales y precisos:
- **Ejecución Automatizada**: Ejecuta cada cuaderno (.ipynb) para asegurar que no hay errores de tiempo de ejecución (Runtime Errors).
- **Validación de Precisión**: Verifica que todos los valores reportados en los outputs y tablas tengan un **mínimo de 5 cifras significativas**.
- **Celdas de Validación**: Confirma que la celda de comparación "Librería vs Manual" se ejecute y arroje un resultado exitoso.

## 5. Corrección Automática (MANDSATORIA)
Si un cuaderno falla en ejecución o precisión:
- Analiza el error o la falta de precisión.
- **Aplica correcciones automáticas** al código de la librería o al cuaderno.
- Re-ejecuta la validación hasta que el cuaderno funcione correctamente y cumpla con los estándares.

## 6. Ejecución del Skill
1. Solicita la ruta de la librería o del archivo `.qmd` a validar.
2. Ejecuta el ciclo de **Auditoría -> Fallo -> Corrección -> Re-auditoría**.
3. Lee los recursos normativos en `recursos/` si es necesario profundizar en una fórmula específica.
4. Genera un reporte de auditoría indicando:
    - Estado de Ejecución de Notebooks.
    - Estado de Precisión (5 cifras).
    - Estado de Formato y Coherencia Técnica.
    - Historial de correcciones automáticas realizadas.

## 7. Recursos
Consulta las guías en `.agent/skills/epy-code-formatter/recursos/` para los estándares de arquitectura de ePy Suite.
