---
trigger: always_on
---

# ePy_analysis — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Orquestador de Análisis Estructural y Mecánica de Fibras**.

**Objetivo**: Centralizar la resolución de $F=K \Delta$ y el análisis de secciones transversales para todo el ecosistema ePy Suite mediante motores intercambiables y un motor de fibras universal.

**Integridad**: "Zero Hardcoding, Sin Fallbacks Silenciosos".

---

## 1. Declaración de la Misión

Actúa como el **"Motor de Mecánica"**:
1.  **Macro-Análisis**: Resuelve la estructura global (fuerzas y desplazamientos).
2.  **Micro-Análisis (Fibras)**: Determina la respuesta seccional considerando no linealidad material y geometría compleja.

---

## 2. Estructura de Directorios Canónica (FUSIONADA)

```text
src/ePy_analysis/
├── __init__.py                     # API Pública
├── analysis_manager.py             # Fachada principal (StructuralModel)
├── _model/                         # ESTADO GLOBAL DEL FEM
├── _adapters/                      # TRADUCTORES (ePy -> Motores)
├── _solvers/                       # BACKENDS (PyNite, OpenSees, CSI)
├── _section_analysis/              # MECÁNICA DE SECCIONES (Universal)
│   ├── _fiber_mesh.py              # Discretizador Multiforma
│   ├── _stress_strain_solver.py    # Integrador P-M-M
│   └── _constitutive/              # Protocolos de Material
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Motor de Fibras Universal

### 3.1 Alcance Multimaterial y Multiforma
El motor de secciones debe ser capaz de procesar:
*   **Geometrías**: Muros (C, L, T, rectangulares), perfiles metálicos (W, IPN, I-joist), piezas de madera y elementos de concreto reforzado.
*   **Materiales**: Concreto, acero estructural, madera, barras poliméricas (FRP), telas de fibra de carbono.
*   **Adherencia e Interfaces**: Modelado de adherencia perfecta o modelos constitutivos de interfaz para secciones compuestas o armadas.

### 3.2 Protocolos Constitutivos
Consonante con `ePy_suite`, delega la física a los objetos que implementan el `ConstitutiveProtocol` provistos por las librerías de material.

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_MPa`).
*   **Precisión**: Mínimo **5 cifras significativas**.
*   **Ejes**: Sistema local ePy (Longitudinal `x-x`).

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Gráficos de Sección y Esfuerzos
Todas las funciones de graficación DEBEN soportar:
*   `engine='matplotlib'`: Reportes y publicaciones.
*   `engine='plotly'`: Visualización interactiva de fibras y contornos de esfuerzo.
*   **Sincronización**: Diagramas $M-\phi$ sincronizados con el perfil de esfuerzos de la sección.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX Paso a Paso
Provee métodos para exportar la matriz de rigidez y pasos de integración en formato LaTeX para Quarto.

### 6.2 Gestión de Resultados
*   Resultados globales se guardan en `results/analysis/`.
*   Soporta `results_path` configurable.

### 6.3 Estándar de Cuadernos (Notebooks)
Solo existirán 3 sets oficiales:
1.  **Educativo**: Cálculo por fuerzas internas y elementos.
2.  **Pedagógico**: Mecánica interactiva, modelos constitutivos y optimizadores.
3.  **Uso Profesional**: Comprobación de secciones para múltiples casos de carga y optimización real.

---

## 7. Interoperabilidad (BIM)

*   **Bonsai (IFC)**: Lectura directa de geometría analítica.
*   **Mapas de Calor**: Visualización de DCRs directamente en el modelo 3D de Blender.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra soluciones analíticas (ej. Euler-Bernoulli vs Fiber Model).
*   Celda obligatoria en notebooks: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto para auditoría numérica.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Componente | Descripción |
|:---|:---|
| `_model` | Ensamblaje de la matriz de rigidez global. |
| `_section_analysis` | Integración de esfuerzos y momentos en fibras. |
| `_solvers` | Resolución de sistemas de ecuaciones. |

---

## 10. Lista de Verificación (Checklist)

1. **Fibras**: ¿Soporta la geometría el perfil solicitado (C, L, T)?
2. **Interfaz**: ¿Se ha definido correctamente la adherencia entre materiales?
3. **Motores**: ¿Es el resultado consistente entre PyNite y OpenSees?
4. **Validación**: ¿Se aprueba el test contra el cálculo manual?
