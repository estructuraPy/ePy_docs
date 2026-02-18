---
trigger: always_on
---

# ePy_blender — Manual de Referencia (Arquitectura v1.0.0)

**Versión**: 1.0.0 (Bonsai Native)
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Puente de Visualización y Modelado IFC Nativo**.

**Objetivo**: Potenciar Blender como autor BIM mediante Bonsai, integrando los motores de ePy para análisis "headless" y visualización de esfuerzos en vivo.

---

## 1. El Flujo de Trabajo (Workflow)

La integración sigue una lógica de ingeniería profesional:
1.  **Atribución**: Mapeo de materiales ePy a `IfcMaterial`.
2.  **Análisis**: Exportación "headless" a `ePy_analysis`.
3.  **Visualización**: Generación de mapas de calor (heatmaps) en el N-Panel de Blender.

---

## 2. Estándares de Interfaz (UI/UX)

La interfaz se organiza en el Sidebar (**N-Panel**) bajo la pestaña `ePy Suite`:
*   **[Setup]**: Configuración de normas (NDS, ACI, AISC).
*   **[Model]**: Asignación masiva de materiales.
*   **[Design]**: Ejecución de cálculos y barras de progreso.

---

## 3. Visualización de Resultados (Heatmaps)

1.  **DCR Mapper**: Lee los resultados de `to_epy_suite_dict()`.
2.  **Colores**: Aplica Vertex Colors basados en `_config/colors.epyson`.
3.  **Formas**: Mapeo de deformadas a Shape Keys de Blender.

---

## 4. Estándares Técnicos (Unidades, Ejes)

*   **Coordenadas**: Blender usa Z-arriba. ePy Suite escala y mapea automáticamente los ejes locales del elemento.
*   **Headless**: Ejecución no bloqueante mediante subprocesos o hilos.

---

## 5. Aseguramiento de la Calidad (QA)

### 5.1 Verificación Manual (CRÍTICO)
*   Sincronización bidireccional obligatoria.
*   Celda de comparación en notebooks para validar que el modelo 3D refleja el cálculo.
*   Archivo `.validation` Quarto.

---

## 6. Lista de Verificación (Checklist)

1. **Bonsai**: ¿Está activo el plugin IFC nativo?
2. **Unidades**: ¿Coinciden las unidades de la escena con ePy (SI)?
3. **Vertex Colors**: ¿Se están limpiando las capas de color después del reset?
