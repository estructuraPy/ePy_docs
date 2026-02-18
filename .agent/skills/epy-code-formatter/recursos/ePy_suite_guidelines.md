---
trigger: always_on
---

# ePy Suite — Arquitectura Maestra y Estándares (v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Filosofía**: "Módulos Distribuidos, Ecosistema Unificado".

**Objetivo**: Una suite de librerías de ingeniería estructural especializadas e interoperables (`ePy_timber`, `ePy_concrete`, etc.) orquestadas por un centro geométrico central (`ePy_plotter`) y un motor de análisis (`ePy_analysis`).

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos".

---

## 1. El Ecosistema (Arquitectura Global)

ePy Suite no es un monolito, sino una federación de librerías especializadas que hablan un lenguaje común.

### 1.1 La "Santísima Trinidad" de la Suite
1.  **El Hub (`ePy_plotter`)**: La Fuente de Verdad para la Geometría.
2.  **El Motor de Análisis (`ePy_analysis`)**: La Fuente de Verdad para la Mecánica.
3.  **Las Librerías de Materiales (`ePy_concrete`, `ePy_steel`...)**: Los Especialistas en Diseño.

---

## 2. Estructura de Directorios Canónica (FUSIONADA)

Cada librería de la suite DEBE seguir este diseño estricto.

```text
src/ePy_{material}/
├── __init__.py                  # API Pública
├── {material}_designer.py       # Fachada principal
├── _config/                     # CAPA DE DATOS
├── _core/                       # CAPA DE CÁLCULO (Física Pura)
├── _design/                     # CAPA DE OBJETOS (Estado de Ingeniería)
└── epy_suite_connect/           # INTEROPERABILIDAD
```

---

## 3. Capa de Datos / Configuración

### 3.1 Configuración como Código (`.epyson`)
Sin "números mágicos" en el código Python. Todas las constantes residen en `_config`.
*   **Colores**: `_config/colors.epyson` (Escala DCR Estándar).
*   **Materiales**: `_config/materials/constitutive/`.

---

## 4. Capa de Núcleo / API (Incluyendo Secciones y Fibras)

### 4.1 Motor de Fibras y Modelos Constitutivos
El motor de fibras en `ePy_analysis` es universal y multimaterial.
*   **Protocolo Constitutivo**: Cada librería de material DEBE exponer una clase pública que implemente el `ConstitutiveProtocol`.
*   **Multiformas**: Soporte para muros (C, L, T, rect), perfiles (I, W, IPN), y piezas de madera.
*   **Interfaces**: Definición de adherencia perfecta o modelos de interfaz para secciones compuestas.

---

## 5. Estándares Técnicos (Unidades, Precisión, Ejes)

### 5.1 Unidades y Precisión (SI Estricto)
*   **Longitud**: `_m`, **Fuerza**: `_kN`, **Esfuerzo**: `_MPa`.
*   **Precisión**: Mínimo **5 cifras significativas** en todos los resultados reportados.

### 5.2 Convención de Ejes (Ejes Locales ePy)
*   `x-x`: Longitudinal.
*   `y-y`: Eje Fuerte (AISC x-x).
*   `z-z`: Eje Débil (AISC y-y).

---

## 6. Visualización y Post-proceso (Motor de Gráficos)

### 6.1 Backend Estandarizado
*   **matplotlib**: Reportes estáticos y PDF.
*   **plotly**: Interactividad y Notebooks.
*   **Alcance**: Multimaterial (concreto, acero, madera, FRP, carbono) y multiforma.

---

## 7. Reporteo y Cuadernos (Validación)

### 7.1 LaTeX y Quarto
*   **Módulos strength**: Generación de LaTeX paso a paso.
*   **Módulos _design**: Ensamble de memorias de cálculo integrando LaTeX.

### 7.2 Gestión de Resultados
*   **Directorio**: Carpeta `results/` organizada por material (ej. `results/timber/`).
*   **Configuración**: Soporte para parámetro `results_path`.

### 7.3 Estándar de Cuadernos (Notebooks)
Solo existirán 3 sets oficiales:
1.  **Educativo**: Cálculo por fuerzas internas y elementos.
2.  **Pedagógico**: Mecánica interactiva, modelos constitutivos y optimizadores.
3.  **Uso Profesional**: Comprobación de secciones para múltiples casos de carga y optimización real.

---

## 8. Interoperabilidad (ePy Suite Connect)

### 8.1 Integración BIM
*   `to_epy_suite_dict()`: Exportación a esquema JSON estándar.
*   **Blender/Bonsai**: Ejecución embebida con visualización de esfuerzos en vivo.

---

## 9. Aseguramiento de la Calidad (QA) y Verificación Manual

### 9.1 Verificación Manual (CRÍTICO)
Cada cuaderno DEBE incluir una celda de comparación: **Librería vs Cálculo a Mano**.
*   Los cálculos manuales se registran en un archivo `.validation` renderizable con Quarto.
*   Tolerancia numérica: `< 0.1%`.

---

## 10. Cumplimiento de Normas (Mapeo)

Cada librería debe incluir una tabla de correspondencia entre los capítulos de la norma (ACI, AISC, NDS) y los módulos de código.

---

## 11. Lista de Verificación (Checklist)

1. **Unidades**: ¿Todas las variables físicas tienen sufijos `_m`, `_kN`, `_MPa`?
2. **Precisión**: ¿Los reportes muestran 5 cifras significativas?
3. **Validación**: ¿Existe el archivo `.validation` para este elemento?
4. **Resultados**: ¿Se guardan en la subcarpeta de material correspondiente?

---

## 12. Política de Ubicación de Datos (CRÍTICO)

> [!CAUTION]
> **Regla Inquebrantable**: Los datos del proyecto SIEMPRE viven en el **directorio de ejecución** (`.epy_suite/`), nunca en carpetas de sistema o instalación.
