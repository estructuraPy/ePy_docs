---
trigger: always_on
---

# ePy_masonry — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Especialista en Mampostería Reforzada y Confinada**.

**Objetivo**: Implementar la normativa TMS 402 y los requerimientos de mampostería confinada latinoamericana mediante un enfoque seccional de fibras y diseño por resistencia.

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos". Resistencias de grout y f'm deben provenir de archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_masonry` provee la física para elementos compuestos de unidades, mortero y refuerzo:
1.  **Diseño Normativo**: TMS 402 (ASD/SD).
2.  **Mampostería Confinada**: Lógica de marcos de confinamiento (CSCR).

---

## 2. Estructura de Directorios Canónica (FUSIONADA)

```text
src/ePy_masonry/
├── __init__.py                     # API Pública
├── masonry_designer.py             # Fachada principal
├── _config/                        # CAPA DE DATOS (Bloques, Grout)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── strength/                   # Ecuaciones TMS
│   ├── failure/                    # Teorías de Falla Anisotrópicas
│   └── advanced_analysis/          # Motor de Fibras (Universal)
├── _design/                        # ESTADO DEL OBJETO (Muros, Vigas)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras Universal

### 3.1 Alcance Multimaterial y Multiforma
*   **Geometrías**: Muros con celdas inyectadas parcial o totalmente.
*   **Materiales**: Bloque de concreto, ladrillo de arcilla, grout, refuerzo de acero.
*   **Motor de Fibras**: Delegación obligatoria a `ePy_analysis` para la mecánica biaxial de muros.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.
*   **Ejes**: Sistema ePy (x-x vertical para muros).

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Detallado
*   **matplotlib**: Elevaciones de muros con aparejos de soga/apilado.
*   **plotly**: Diagramas de interacción P-M biaxiales y superficies de falla seccional.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación de memorias de cálculo hacia `results/masonry/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Flexo-compresión en muros de mampostería.
2.  **Pedagógico**: Visualización de celdas inyectadas y distribución de esfuerzos.
3.  **Uso Profesional**: Diseño de edificios de mampostería reforzada y muros de retención.

---

## 7. Interoperabilidad (BIM)

*   **Bonsai (IFC)**: Detallado 3D de celdas y refuerzos.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Ejemplos de Diseño TMS.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Componente | Descripción |
|:---|:---|
| Flexión y Axiales | `_core.strength._flexure` |
| Cortante (TMS 9.3) | `_core.strength._shear` |
| Mampostería Confinada | `_design._confined` |

---

## 10. Lista de Verificación (Checklist)

1. **Grout**: ¿Se verifica la inyectabilidad de las celdas?
2. **Fibras**: ¿Representa la malla la geometría real de las paredes del bloque?
3. **Validación**: ¿Se aprueba el test contra ejemplos de la NCMA?
