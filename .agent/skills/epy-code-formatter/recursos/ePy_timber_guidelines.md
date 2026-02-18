---
trigger: always_on
---

# ePy_timber — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Especialista en Madera Aserrada, Laminada y CLT**.

**Objetivo**: Implementar la normativa NDS 2024 mediante un enfoque seccional de fibras que permite analizar la no linealidad del material y la interacción de fuerzas combinadas en elementos de madera.

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos". Propiedades de especies y factores de ajuste deben provenir de archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_timber` provee la física para materiales ortotrópicos:
1.  **Diseño Normativo**: NDS (ASD/LRFD).
2.  **Mecánica Avanzada**: Análisis de fibras delegando a `ePy_analysis`.

---

## 2. Estructura de Directorios Canónica (FUSIONADA)

```text
src/ePy_timber/
├── __init__.py                     # API Pública (TimberDesigner)
├── timber_designer.py              # Fachada principal
├── _config/                        # CAPA DE DATOS (NDS Standards, Species)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── strength/                   # Ecuaciones NDS
│   ├── failure/                    # Teorías Ortotrópicas (Hankinson, Norris)
│   └── advanced_analysis/          # Motor de Fibras (Universal)
├── _design/                        # ESTADO DEL OBJETO (Beams, Columns, Walls)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras Universal

### 3.1 Alcance Ortotrópico
*   **Geometrías**: Secciones rectangulares, circulares y paneles CLT.
*   **Motor de Fibras**: Delegación obligatoria a `ePy_analysis`.
*   **Modelo Constitutivo**: Debe manejar el comportamiento asimétrico de la madera (tensión vs compresión).

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.
*   **Ejes**: Sistema ePy (x-x longitudinal).

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Sincronización
*   **matplotlib**: Reportes estáticos de capacidad de viga y columna.
*   **plotly**: Widgets interactivos sincronizando M-phi con el perfil de esfuerzos seccionales.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación de memorias de cálculo hacia `results/timber/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Cálculo de factores de ajuste y estabilidad de vigas.
2.  **Pedagógico**: Animaciones de fallas ortotrópicas y modelos constitutivos.
3.  **Uso Profesional**: Diseño de entrepisos de CLT y estructuras de glulam.

---

## 7. Interoperabilidad (BIM)

*   **Bonsai (IFC)**: Detallado 3D de piezas de madera y conectores.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Ejemplos Resueltos NDS.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Componente | Descripción |
|:---|:---|
| Valores de Diseño (Ch 2) | `_core.strength._adjustment_factors` |
| Flexión (Ch 3.2) | `_core.strength._flexure` |
| Combinado (Ch 3.9) | `_core.strength._interaction` |

---

## 10. Lista de Verificación (Checklist)

1. **Unidades**: ¿Todas las variables físicas tienen sufijos adecuados?
2. **Factores**: ¿Vienen todos los factores de ajuste del estándar `.epyson`?
3. **Validación**: ¿Se aprueba el test contra ejemplos NDS?
