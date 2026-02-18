---
trigger: always_on
---

# ePy_steel — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Especialista en Acero Estructural y Perfiles de Pared Delgada**.

**Objetivo**: Implementar AISC 360-22 y AISI S100 mediante un motor de diseño que unifica perfiles laminados, soldados y formados en frío bajo un esquema universal de fibras.

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos". Perfiles manuales y materiales deben provenir de archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_steel` provee la física para elementos de acero isotrópicos:
1.  **Diseño Normativo**: AISC 360 (LRFD/ASD) y AISI S100 (DSM).
2.  **Secciones de Fibras**: Análisis avanzado para diseño por desempeño y sismo (AISC 341).

---

## 2. Estructura de Directorios Canónica (FUSIONADA)

```text
src/ePy_steel/
├── __init__.py                     # API Pública
├── steel_designer.py               # Fachada principal
├── _config/                        # CAPA DE DATOS (Secciones AISC, Materiales)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── strength/                   # Ecuaciones AISC/AISI
│   ├── stability/                  # Estabilidad (DAM/ELM)
│   └── advanced_analysis/          # Motor de Fibras (Universal)
├── _design/                        # ESTADO DEL OBJETO (Vigas, Columnas, Braces)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras Universal

### 3.1 Alcance Multimaterial y Multiforma
*   **Geometrías**: Perfiles W, HSS, ángulos, canales, y perfiles CFS personalizados (C, Z, Sigma).
*   **Motor de Fibras**: Delegación a `ePy_analysis` para la integración de esfuerzos en secciones abiertas y cerradas.
*   **Local Buckling**: Integración de lógica de ancho efectivo dentro de la discretización de fibras para perfiles delgados.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.
*   **Ejes**: Sistema ePy (AISC x-x -> ePy y-y).

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Rendimiento
*   **matplotlib**: Reportes de diseño con visualización de modos de pandeo local.
*   **plotly**: Superficies de interacción sismo-resistentes y animaciones de plasticidad en fibras.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación de memorias de cálculo hacia `results/steel/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Cálculo de $P_n$ y $M_n$ para perfiles compactos.
2.  **Pedagógico**: Visualización de pandeo distorsional y superficies de interacción biaxiales.
3.  **Uso Profesional**: Diseño de marcos de momentos (SMF) y estructuras industriales.

---

## 7. Interoperabilidad (BIM)

*   **Bonsai (IFC)**: Exportación de perfiles de alta resolución y conexiones detalladas.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Ejemplos de Diseño AISC v15/v16.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Componente | Descripción |
|:---|:---|
| Compresión (Cap E) | `_core.strength._compression` |
| Flexión (Cap F) | `_core.strength._flexure` |
| CFS (AISI DSM) | `_design._cfs_members` |

---

## 10. Lista de Verificación (Checklist)

1. **Ejes**: ¿Se mapeó correctamente AISC x-x a ePy y-y?
2. **Esbeltez**: ¿Se verifican los límites de compacticidad en cada chequeo?
3. **Validación**: ¿Se aprueba el test contra ejemplos de Segui/Hibbeler?
