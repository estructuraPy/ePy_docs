---
trigger: always_on
---

# ePy_concrete — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Especialista en Concreto Reforzado y Pre-esforzado**.

**Objetivo**: Implementar ACI 318-19 mediante un motor de análisis de secciones de fibras que integra modelos constitutivos de confinamiento y refuerzo.

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos". Mezclas de concreto y catálogos de barras deben provenir de archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_concrete` provee la física para materiales cuasi-frágiles:
1.  **Diseño Normativo**: ACI 318.
2.  **Mecánica Seccional**: Motor de fibras universal delegando a `ePy_analysis`.

---

## 2. Estructura de Directorios Canónica

```text
src/ePy_concrete/
├── __init__.py                     # API Pública (ConcreteDesigner)
├── concrete_designer.py            # Fachada principal
├── _config/                        # CAPA DE DATOS (Concrete Mixes, Rebar)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── strength/                   # Ecuaciones ACI (Whitney Bloom)
│   ├── failure/                    # Teorías Triaxiales (Willam-Warnke)
│   └── advanced_analysis/          # Motor de Fibras (Universal)
├── _design/                        # ESTADO DEL OBJETO (Beams, Columns, Walls)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras Universal

### 3.1 Alcance Multiforma y Confinamiento
*   **Geometrías**: Secciones rectangulares, circulares, en T, L y muros complejos.
*   **Refuerzo**: Mallas de barras (longitudinal/transversal), FRP y carbono.
*   **Confinamiento**: Modelos de Mander, Hognestad o Popovics integrados en el mapa de fibras.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.
*   **Ejes**: Sistema local ePy (Longitudinal x-x).

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Sincronización
*   **matplotlib**: Planos de detallado y reportes PDF.
*   **plotly**: Tableros interactivos para diagramas de interacción P-M-M biaxiales.
*   **Sincronización**: Visualización de fallas por cortante vs flexión.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación de memorias de cálculo hacia `results/concrete/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Diseño de vigas y longitudes de desarrollo.
2.  **Pedagógico**: Animaciones de agrietamiento y modelos de confinamiento.
3.  **Uso Profesional**: Diseño de marcos especiales de momento (SMF) y muros de cortante.

---

## 7. Interoperabilidad (BIM)

*   **Bonsai (IFC)**: Generación de armaduras 3D (`IfcReinforcingBar`) con LOD 400.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Manual de Diseño ACI.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Capítulo ACI | Módulo / Componente |
|:---|:---|
| Flexión (Ch 22.2) | `_core.strength._flexure` |
| Cortante (Ch 22.5) | `_core.strength._shear` |
| Sismo (Ch 18) | `_core.seismic` |

---

## 10. Lista de Verificación (Checklist)

1. **Unidades**: ¿Se usan sufijos en todas las variables físicas?
2. **Fibras**: ¿Se discretizó correctamente el recubrimiento vs núcleo confinado?
3. **Validación**: ¿Se aprueba el test contra ejemplos de MacGregor/Nawy?
