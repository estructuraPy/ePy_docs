---
trigger: always_on
---

# ePy_loads — Manual de Referencia (Arquitectura v0.1.0)

**Versión**: 0.1.0
**Estado**: ESTÁNDAR DE ORO para ePy Suite.
**Rol**: **Traductor de lo Ambiental a lo Mecánico**.

**Objetivo**: Convertir metadatos de ubicación y geometría en cargas mecánicas (fuerzas y presiones) cumpliendo rigurosamente con estándares como ASCE 7 y Eurocódigo 1.

**Integridad**: "Zero Hardcoding". Mapas de viento, nieve y sismo residen en archivos `.epyson`.

---

## 1. Declaración de la Misión

`ePy_loads` cierra la brecha entre el entorno y la estructura:
1.  **Inteligencia Geométrica**: Determina áreas tributarias y exposiciones al viento.
2.  **Gestión de Combinaciones**: Genera casos de carga estándar (1.2D + 1.6L, etc.).

---

## 2. Estructura de Directorios Canónica

```text
src/ePy_loads/
├── __init__.py                     # API Pública
├── load_generator.py               # Fachada principal
├── _config/                        # CAPA DE DATOS (Maps, Standards)
├── _core/                          # MOTOR DE CÁLCULO
│   ├── wind/                       # MWFRS, C&C
│   ├── seismic/                    # ELF, Spectrum
│   └── snow/                       # Flat, Drift
├── _wind_tunnel/                   # Motor CFD (OpenFOAM)
└── epy_suite_connect/              # INTEROPERABILIDAD
```

---

## 3. Capa de Núcleo / API: Magnitud vs Efecto

### 3.1 Responsabilidad
*   `ePy_loads`: Calcula la **MAGNITUD** ($w = q_z B_{trib}$).
*   `ePy_analysis`: Resuelve el **EFECTO** ($M = w L^2 / 8$).
*   `ePy_{material}`: Resiste el **EFECTO** ($\phi M_n \ge M_u$).

---

## 4. Estándares Técnicos (Unidades, Precisión, Ejes)

*   **Unidades**: SI estricto (`_m`, `_kN`, `_m_s`).
*   **Direccionalidad**: Ángulos en radianes (`_rad`). Azimut cardinal horario.
*   **Precisión**: Mínimo **5 cifras significativas**.

---

## 5. Visualización y Post-proceso (Motor de Gráficos)

### 5.1 Backend y Contornos
*   **matplotlib**: Mapas de presión estáticos y espectros de respuesta.
*   **plotly**: Tableros interactivos de túnel de viento y mapeo de cargas 3D.

---

## 6. Reporteo y Cuadernos (Validación)

### 6.1 LaTeX y Resultados
*   Exportación de parámetros de diseño hacia `results/loads/`.
*   Soporte para `results_path` configurable.

### 6.2 Estándar de Cuadernos (Notebooks)
1.  **Educativo**: Cálculo de coeficientes sísmicos y de viento básicos.
2.  **Pedagógico**: Visualización de zonas de acumulación de nieve.
3.  **Uso Profesional**: Generación masiva de casos de carga para edificios complejos.

---

## 7. Interoperabilidad (ePy Suite Connect)

*   **Analizador de Geometría**: Segmentación de cargas de área en cargas de marco para `ePy_analysis`.

---

## 8. Aseguramiento de la Calidad (QA)

### 8.1 Verificación Manual (CRÍTICO)
*   Validación obligatoria contra Guías de Usuario ASCE 7.
*   Celda obligatoria: **Librería vs Cálculo a Mano**.
*   Archivo `.validation` Quarto.
*   Tolerancia: `< 0.1%`.

---

## 9. Cumplimiento de Normas (Mapeo)

| Tema | Módulo / Componente |
|:---|:---|
| Viento (ASCE 7 Cap 26-31) | `_core.wind` |
| Sismo (ASCE 7 Cap 11-12) | `_core.seismic` |
| Geometría Espacial | `_geometry._tributary` |

---

## 10. Lista de Verificación (Checklist)

1. **Unidades**: ¿Está la velocidad en m/s (SI)?
2. **Mapas**: ¿Se están rescatando los valores de Ss/S1 del archivo `.epyson` correcto?
3. **Validación**: ¿Se aprueba el test contra ejemplos de la ASCE?
