---
trigger: always_on
---

# ePy_geotechnical — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Especialista en Mecánica de Suelos e Interacción Suelo-Estructura**.

**Objetivo**: Proveer la mecánica pura para capacidad portante, empujes laterales y asentamientos, sirviendo como el proveedor de condiciones de borde para el resto de la suite.

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos". Todos los parámetros geotécnicos deben provenir de archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_geotechnical` cierra la brecha entre la caracterización del sitio y el modelo analítico estructural:
1.  **Condiciones de Borde**: Genera resortes (Winkler) y curvas $p-y$ para análisis.
2.  **Verificación ULS/SLS**: Chequea falla general por corte, deslizamiento y asentamientos.

---

## 2. Estructura de Directorios Canónica (FUSIONADA)

```text
src/ePy_geotechnical/
├── __init__.py                     # API Pública
├── geotech_designer.py             # Fachada principal
├── _config/                        # CAPA DE DATOS (Suelos, Estándares)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── bearing/                    # Capacidad Portante
│   ├── lateral/                    # Empujes Laterales
│   ├── piles/                      # Cimentaciones Profundas
│   ├── seismic/                    # Licuación y Respuesta de Sitio
│   └── advanced_analysis/          # FEA y Motor de Fibras (Pilotes)
├── _design/                        # ESTADO DEL OBJETO (Zapatas, Muros)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Datos / Configuración

### 3.1 Materiales y Suelos
Las propiedades de suelos (phi, cohesión, gamma, módulos) residen en `_config/materials/soils/`. Sin números mágicos en Python.

---

## 4. Capa de Núcleo / API: Interacción y Fibras

### 4.1 Análisis de Fibras en Pilotes
Los pilotes reforzados y pilas utilizan el motor universal de `ePy_analysis` para generar diagramas de interacción P-M-M estructurales.

### 4.2 Interfaces Suelo-Estructura
Soporte para modelos de adherencia y fricción skin-friction dependientes de la profundidad y el material (concreto/acero/madera).

---

## 5. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_kPa`, `_deg`).
*   **Convención de Signos**: Compresión POSITIVA (+) para mecánica de suelos. Profundidad (z) positiva hacia abajo.
*   **Precisión**: Mínimo **5 cifras significativas**.

---

## 6. Visualización y Post-proceso (Motor de Gráficos)

### 6.1 Backend y Alcance
*   **matplotlib**: Bulbos de presión y diagramas de suelo estáticos.
*   **plotly**: Perfiles interactivos de resistencia vs profundidad y superficies de interacción biaxiales.

---

## 7. Reporteo y Cuadernos (Validación)

### 7.1 LaTeX y Resultados
*   Exportación de memorias de cálculo desde `_design` hacia `results/geotechnical/`.
*   Soporte para `results_path` configurable.

### 7.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Cálculo de $q_u$ y empujes activos.
2.  **Pedagógico**: Visualización de bulbos de presión y curvas $p-y$.
3.  **Uso Profesional**: Diseño de cimentaciones complejas de puentes y muros de contención.

---

## 8. Interoperabilidad (ePy Suite Connect)

*   **Exportación de Resortes**: Mapeo directo a `ePy_analysis` para modelos estructurales sobre fundación elástica.

---

## 9. Aseguramiento de la Calidad (QA)

### 9.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra ejemplos de Das (Principles of Foundation Engineering).
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 10. Cumplimiento de Normas (Mapeo)

| Tema | Módulo / Ecuación |
|:---|:---|
| Capacidad Portante | `_core.bearing._vesic` |
| Empujes Laterales | `_core.lateral._coulomb` |
| Pilotes (Axial) | `_core.piles._skin_friction` |

---

## 11. Lista de Verificación (Checklist)

1. **Unidades**: ¿Es la profundidad z positiva hacia abajo?
2. **Agua**: ¿Se consideran presiones hidrostáticas explícitamente?
3. **Validación**: ¿Se aprueba el test contra Bowles/Das?
