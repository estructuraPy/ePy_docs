---
trigger: always_on
---

# ePy_connections — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Centro Universal de Diseño de Uniones (Joint Design Hub)**.

**Objetivo**: Centralizar la mecánica de conexiones multimaterial gestionando interfaces híbridas y delegando la física del material a los núcleos respectivos.

**Integridad**: "Zero Hardcoding". Pernos, soldaduras y anclajes comerciales deben provenir de archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_connections` unifica el diseño de uniones tratando al **Nodo** como primera clase:
1.  **Conexiones Híbridas**: Acero-Madera, Concreto-Acero (anclajes).
2.  **Delegación de Física**: Sabe *cómo* conectar, pero consulta a `ePy_concrete` o `ePy_steel` para capacidades detalladas.

---

## 2. Estructura de Directorios Canónica

```text
src/ePy_connections/
├── __init__.py                     # API Pública
├── connection_designer.py          # Fachada principal
├── _config/                        # CAPA DE DATOS (Bolts, Welds, Anchors)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── steel/                      # Acero-Acero
│   ├── timber/                     # Madera-Madera (Dowel Bearing)
│   ├── concrete/                   # Interface (Pullout, Breakout)
│   └── hybrid/                     # Lógica Multi-material
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras y Componentes

### 3.1 Alcance Multi-material
*   **Motor de Fibras**: Utiliza `ePy_analysis` para el análisis de distribución de esfuerzos en placas de extremo y bases de columna.
*   **Teoría de Líneas de Fluencia**: Localizada en `_analysis/` para verificación de deformación en placas.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`, `_rad`).
*   **Precisión**: Mínimo **5 cifras significativas**.

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Detallado
*   **matplotlib**: Esquemas de pernos y soldaduras para reportes.
*   **plotly**: Visualización interactiva de resortes equivalentes y líneas de fluencia.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación de memorias de cálculo hacia `results/connections/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Cómo añadir pernos y soldaduras a una placa.
2.  **Pedagógico**: Mecánica de la unión y resortes equivalentes.
3.  **Uso Profesional**: Diseño de bases de columna biaxiales con cortante y momento.

---

## 7. Interoperabilidad (BIM)

*   **Bonsai (IFC)**: Exportación de pernos (`IfcMechanicalFastener`) y soldaduras (`IfcFastener`).

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Ejemplos Resueltos de AISC y ACI 318 Cap 17.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Componente | Descripción |
|:---|:---|
| Acero-Acero | `_core.steel._shear` / `_moment` |
| Anclaje al Concreto | `_core.concrete._anchorage` |
| Madera | `_core.timber._dowel_bearing` |

---

## 10. Lista de Verificación (Checklist)

1. **Unidades**: ¿Es el ángulo de soldadura en radianes?
2. **Componentes**: ¿Viene la tornillería de la librería `_config/parts/`?
3. **Validación**: ¿Se aprueba el test contra ejemplos de la AISC 360?
